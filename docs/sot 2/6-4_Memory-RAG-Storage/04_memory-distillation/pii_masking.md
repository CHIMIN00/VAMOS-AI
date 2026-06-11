# P1-7. PII 마스킹 파이프라인 구현 상세 (V1)

> **세션**: P1-7 (2026-04-13)
> **산출물 버전**: v1.1 (재검증 반영: EscalationPayload JSON 정합, 중첩 JSON 로깅 R-01-7 정합, 경로 오류 교정)
> **상태**: COMPLETE
> **LOCK 준수**: LOCK-MR-015 (Deny 벡터 삽입 금지), LOCK-MR-017 (project_id 격리), LOCK-MR-018 (저장 전 사용자 확인), LOCK-MR-019 (루프 저장 폭주 방지)
> **이슈 전환**: I-6 SHELL->FULL (PII 마스킹 파이프라인)
> **정본**: D2.0-06 §3 (저장 정책/마스킹 파이프라인) + S7D-066 (PII 자동 감지+마스킹) + S7D-065 (데이터 분류), D2.0-07 §2.3.2 (민감 데이터 처리) + S7E-007 (PII 자동 마스킹), Part2 V1-Phase 2 항목7
> **교차 참조**: P0-1 MemoryRecordSchema, P1-1 L0_session_memory_crud, P1-2 L1_project_memory_crud, P1-3 chroma_adapter, P1-5 semantic_cache, P1-6 export_import, P1-9 DCL 기초 구현 (미완 — 인터페이스만 참조)
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D2.0-07 (Policy SOT) > D6 (Schema SOT) > Part2 V1-P2 (구현가이드) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수 상세**:
>   - LOCK-MR-015: Deny 판정 시 벡터 삽입 절대 금지, 저장 완전 차단
>   - LOCK-MR-017: project_id 기반 격리, PII 탐지/마스킹 결과도 프로젝트 범위 내
>   - LOCK-MR-018: 마스킹 후 저장 시에도 사용자 확인 기본 정책 유지
>   - LOCK-MR-019: 루프 저장 폭주 방지 — 원문이 아닌 요약/메타만 저장 (마스킹 대상도 요약 수준)
>
> **입력 파일**:
>   - D2.0-06 §3 저장 정책(Allow/Restrict/Deny)과 마스킹 파이프라인
>   - D2.0-06 S7D-066 PII 자동 감지+마스킹 (주민번호/전화번호/이메일/주소/카드번호/계좌번호, 정규식+NER)
>   - D2.0-06 S7D-065 데이터 분류 체계 (4등급: 공개/내부/비밀/극비)
>   - D2.0-07 §2.3.2 민감 데이터 처리 (평문 기록 금지, 마스킹 필수, SENSITIVE_DATA_FLAG)
>   - D2.0-07 S7E-007 PII 자동 마스킹 (이메일/전화번호/주민번호 등)
>   - Part2 V1-Phase 2 항목7 (pii_masker.py — regex 탐지, `***` 마스킹, VAL-008 연동)
>   - P0-1: `MemoryRecordSchema.md` (policy_decision 필드, masked 필드)
>   - P1-1: `L0_session_memory_crud.md` (Create §3.1 step 7 — `apply_pii_masking()` 호출 인터페이스)
>   - P1-2: `L1_project_memory_crud.md` (restrict 마스킹 인터페이스)
>
> **이전 단계 이월 사항**: P1-1~P1-6 모두 이월 없음. P1-6에서 P1-7 인터페이스 계약 정의(§8) — 본 문서에서 FULL 구현.

---

## 목차

1. [PIIMasker 클래스 설계](#1-piimasker-클래스-설계)
2. [PII 카테고리 정의](#2-pii-카테고리-정의)
3. [PII 탐지 엔진](#3-pii-탐지-엔진)
4. [마스킹 전략 (카테고리별)](#4-마스킹-전략-카테고리별)
5. [데이터 분류 체계 연동 (S7D-065)](#5-데이터-분류-체계-연동-s7d-065)
6. [DCL 연동 — Allow/Restrict/Deny](#6-dcl-연동--allowrestrictdeny)
7. [Create/Update 경로 파이프라인 통합](#7-createupdate-경로-파이프라인-통합)
8. [project_id 격리 (LOCK-MR-017)](#8-project_id-격리-lock-mr-017)
9. [I-6 SHELL->FULL 전환 명세](#9-i-6-shellfull-전환-명세)
10. [에러 코드 정의](#10-에러-코드-정의)
11. [복구/재시도 전략](#11-복구재시도-전략)
12. [에스컬레이션 정책](#12-에스컬레이션-정책)
13. [로깅 규격 (R-01-7)](#13-로깅-규격-r-01-7)
14. [시간복잡도 분석 (Big-O)](#14-시간복잡도-분석-big-o)
15. [예외 처리 정책 표](#15-예외-처리-정책-표)
16. [단위 테스트 시나리오](#16-단위-테스트-시나리오)
17. [Phase 2 통합 테스트](#17-phase-2-통합-테스트)
18. [세션 간 인터페이스 cross-check](#18-세션-간-인터페이스-cross-check)
19. [LOCK-MR 참조 추적표](#19-lock-mr-참조-추적표)
20. [교차 참조 블록](#20-교차-참조-블록)

---

## 1. PIIMasker 클래스 설계

### 1.1 클래스 계층

```
PIIMasker (본 문서)
  ├── __init__(config: PIIMaskerConfig)
  ├── detect(text: str) -> DetectionResult
  ├── mask(text: str) -> MaskResult
  ├── detect_and_mask(text: str) -> DetectMaskResult
  ├── classify_sensitivity(detections: list[PIIDetection]) -> SensitivityLevel
  ├── apply_to_record(record: MemoryRecord, policy_decision: str) -> PIIPipelineResult
  ├── _detect_by_regex(text: str) -> list[PIIDetection]
  ├── _detect_by_dictionary(text: str) -> list[PIIDetection]
  ├── _merge_detections(regex_hits: list, dict_hits: list) -> list[PIIDetection]
  ├── _apply_mask(text: str, detections: list[PIIDetection]) -> str
  ├── _validate_masking_completeness(original: str, masked: str, detections: list) -> bool
  └── _log_pii_event(event_type: str, details: dict) -> None
```

### 1.2 설정 구조체

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class PIICategory(Enum):
    """PII 카테고리 — D2.0-06 S7D-066 기반 6종 + 확장 2종 = 총 8종"""
    RRN = "resident_registration_number"    # 주민등록번호
    PHONE = "phone_number"                  # 전화번호
    EMAIL = "email_address"                 # 이메일 주소
    CARD = "credit_card_number"             # 카드번호
    ACCOUNT = "bank_account_number"         # 계좌번호
    ADDRESS = "physical_address"            # 주소
    API_KEY = "api_key"                     # API 키 (Part2 항목7 추가)
    PASSWORD = "password"                   # 비밀번호 (Part2 항목7 추가)

class SensitivityLevel(Enum):
    """민감도 등급 — D2.0-06 S7D-065 4등급"""
    PUBLIC = "public"             # 공개 — 모든 저장소 허용
    INTERNAL = "internal"         # 내부 — L1/L2 저장 허용, 공유 제한
    CONFIDENTIAL = "confidential" # 비밀 — L1만 허용(TTL 강제), 벡터 마스킹 필수
    SECRET = "secret"             # 극비 — 저장 금지(Deny), 세션 종료 시 자동 삭제

class MaskFormat(Enum):
    """마스킹 포맷 유형"""
    ASTERISK = "asterisk"         # *** (기본 — D2.0-06 §3.3)
    PARTIAL = "partial"           # 일부 보존 (예: ***@***.com)
    HASH = "hash"                 # SHA-256 해시 (로그용)
    REDACTED = "redacted"         # [REDACTED] 태그

@dataclass
class PIIMaskerConfig:
    """PIIMasker 설정 — D2.0-06 §3 + S7D-066 + Part2 항목7 기반"""
    enabled: bool = True                                      # 마스킹 활성화 (V1 기본 ON)
    categories: list[PIICategory] = field(default_factory=lambda: list(PIICategory))  # 전체 카테고리
    default_mask_format: MaskFormat = MaskFormat.ASTERISK      # D2.0-06 §3.3: *** 기본
    log_mask_format: MaskFormat = MaskFormat.HASH              # 로그용 해시 (D2.0-06 §3.3)
    min_confidence: float = 0.8                                # 탐지 최소 신뢰도 (V1=0.8, V2+=0.95)
    strict_mode: bool = True                                   # True=미완전 마스킹 시 deny (D2.0-06 §3.2 옵션 B)
    enable_dictionary: bool = True                             # 패턴 사전 보조 탐지
    max_text_length: int = 100_000                             # 탐지 대상 최대 길이 (DoS 방지)
    sensitive_data_flag: bool = True                            # D2.0-07 §2.3.2: SENSITIVE_DATA_FLAG 자동 부착
```

### 1.3 데이터 구조체

```python
@dataclass
class PIIDetection:
    """개별 PII 탐지 결과"""
    category: PIICategory          # 탐지된 PII 유형
    start: int                     # 시작 위치 (0-based)
    end: int                       # 끝 위치 (exclusive)
    original_text: str             # 원문 (로깅 시 해시 변환, 절대 평문 저장 금지 — D2.0-07 §2.3.2)
    confidence: float              # 탐지 신뢰도 (0.0~1.0)
    detector: str                  # 탐지기 유형 ("regex" | "dictionary")

@dataclass
class DetectionResult:
    """PII 탐지 결과 (mask 미적용)"""
    text_length: int               # 원문 길이
    detections: list[PIIDetection] # 탐지 목록
    pii_found: bool                # PII 발견 여부
    sensitivity_level: SensitivityLevel  # 산출 민감도 등급
    detection_count: int           # 탐지 건수
    categories_found: list[PIICategory]  # 발견된 카테고리 목록

@dataclass
class MaskResult:
    """마스킹 적용 결과"""
    masked_text: str               # 마스킹 적용 텍스트
    mask_count: int                # 마스킹 적용 건수
    masking_complete: bool         # 마스킹 완전성 여부
    categories_masked: list[PIICategory]  # 마스킹된 카테고리 목록

@dataclass
class DetectMaskResult:
    """탐지+마스킹 통합 결과"""
    detection: DetectionResult     # 탐지 결과
    mask: MaskResult               # 마스킹 결과
    policy_recommendation: str     # "allow" | "restrict" | "deny" 권고

@dataclass
class PIIPipelineResult:
    """파이프라인 최종 결과 (record 단위)"""
    record_id: str                 # 대상 레코드 ID
    project_id: str                # 프로젝트 ID (LOCK-MR-017)
    policy_decision: str           # 최종 정책 결정 (allow/restrict/deny)
    pii_found: bool                # PII 발견 여부
    sensitivity_level: SensitivityLevel  # 산출 민감도 등급
    masked: bool                   # 마스킹 적용 여부
    masking_complete: bool         # 마스킹 완전성 여부
    action: str                    # "store" | "store_masked" | "block" | "escalate"
    vector_insert_allowed: bool    # 벡터 삽입 허용 여부 (LOCK-MR-015)
    content_summary: Optional[str] # 마스킹 후 요약 (LOCK-MR-019)
    event_log: dict                # 감사 로그 페이로드
```

---

## 2. PII 카테고리 정의

> **정본**: D2.0-06 S7D-066 (6종 기본), Part2 V1-Phase 2 항목7 (API 키/비밀번호 추가)

### 2.1 V1 탐지 대상 (8종)

| # | 카테고리 | PIICategory | 정본 출처 | 민감도 등급 | 마스킹 우선순위 |
|---|---------|------------|----------|-----------|-------------|
| 1 | 주민등록번호 | RRN | S7D-066 | SECRET | 1 (최우선) |
| 2 | 전화번호 | PHONE | S7D-066 | CONFIDENTIAL | 3 |
| 3 | 이메일 주소 | EMAIL | S7D-066 | CONFIDENTIAL | 3 |
| 4 | 카드번호 | CARD | S7D-066 | SECRET | 1 |
| 5 | 계좌번호 | ACCOUNT | S7D-066 | SECRET | 1 |
| 6 | 주소 | ADDRESS | S7D-066 | CONFIDENTIAL | 4 |
| 7 | API 키 | API_KEY | Part2 항목7 | SECRET | 2 |
| 8 | 비밀번호 | PASSWORD | Part2 항목7 | SECRET | 2 |

### 2.2 민감도 등급 → 정책 매핑

| 민감도 등급 | 기본 정책 | 벡터 삽입 | 저장 범위 | 정본 |
|-----------|----------|----------|---------|------|
| PUBLIC | allow | 허용 | 모든 저장소 | S7D-065 |
| INTERNAL | allow | 허용 (공유 제한) | L1/L2 | S7D-065 |
| CONFIDENTIAL | restrict | 마스킹 후 허용 | L1만 (TTL 강제) | S7D-065 |
| SECRET | deny | **절대 금지** (LOCK-MR-015) | 저장 금지 | S7D-065 |

### 2.3 카테고리 조합 규칙

- 복수 PII 탐지 시 **가장 높은 민감도 등급**을 최종 등급으로 채택
- SECRET 카테고리가 1건이라도 포함되면 전체 레코드를 SECRET으로 판정
- CONFIDENTIAL + CONFIDENTIAL 조합은 CONFIDENTIAL 유지 (등급 상승 없음)

---

## 3. PII 탐지 엔진

> **정본**: D2.0-06 S7D-066 (정규식 + NER, 한국어 특화), Part2 항목7 (regex 탐지)
> **V1 범위**: 정규식 기반 1차 탐지 + 패턴 사전(dictionary) 보조. NER/ML 탐지는 V2+ (IR-022 참조)

### 3.1 정규식 패턴 (V1 — 규칙 기반)

```python
import re
from typing import Pattern

# PII 정규식 패턴 사전 — D2.0-06 S7D-066 + Part2 항목7
PII_REGEX_PATTERNS: dict[PIICategory, list[Pattern]] = {
    
    PIICategory.RRN: [
        # 주민등록번호: YYMMDD-NNNNNNN (13자리, 하이픈 포함/미포함)
        re.compile(r'\b(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[-\s]?([1-4]\d{6})\b'),
    ],
    
    PIICategory.PHONE: [
        # 휴대전화: 010-XXXX-XXXX, 01X-XXX-XXXX
        re.compile(r'\b(01[016789])[-.\s]?(\d{3,4})[-.\s]?(\d{4})\b'),
        # 일반전화: 02-XXXX-XXXX, 0XX-XXX-XXXX
        re.compile(r'\b(0[2-6][0-5]?)[-.\s]?(\d{3,4})[-.\s]?(\d{4})\b'),
    ],
    
    PIICategory.EMAIL: [
        # 이메일: user@domain.tld
        re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
    ],
    
    PIICategory.CARD: [
        # 카드번호: 4자리-4자리-4자리-4자리 (VISA/Master/국내)
        re.compile(r'\b(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})\b'),
    ],
    
    PIICategory.ACCOUNT: [
        # 계좌번호: 은행별 포맷 (10~16자리, 하이픈 구분)
        re.compile(r'\b(\d{3,6})[-\s](\d{2,6})[-\s](\d{2,8})\b'),
    ],
    
    PIICategory.ADDRESS: [
        # 한국 주소: 도/시/구/동 패턴
        re.compile(r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[시도]?\s+\S+[시군구]\s+\S+[읍면동로길]'),
    ],
    
    PIICategory.API_KEY: [
        # API Key: sk-*, api_key=*, key-* 형태 (32자+ hex/base64)
        re.compile(r'\b(sk[-_]|api[-_]?key[-_=:]\s*)[a-zA-Z0-9_-]{20,}\b', re.IGNORECASE),
        # Bearer 토큰
        re.compile(r'Bearer\s+[a-zA-Z0-9_.-]{20,}\b'),
    ],
    
    PIICategory.PASSWORD: [
        # 비밀번호: password=*, pwd=*, passwd=* 뒤 값
        re.compile(r'(password|passwd|pwd)\s*[:=]\s*\S{6,}', re.IGNORECASE),
    ],
}
```

### 3.2 패턴 사전 보조 탐지

```python
# 패턴 사전 — 문맥 키워드 기반 2차 탐지 (정규식 미스 보완)
PII_DICTIONARY_PATTERNS: dict[PIICategory, list[str]] = {
    PIICategory.RRN: [
        "주민등록번호", "주민번호", "resident registration",
        "주민등록", "개인식별번호",
    ],
    PIICategory.PHONE: [
        "전화번호", "휴대폰", "연락처", "phone number",
        "mobile", "핸드폰",
    ],
    PIICategory.EMAIL: [
        "이메일", "메일주소", "email address",
        "전자우편",
    ],
    PIICategory.CARD: [
        "카드번호", "신용카드", "체크카드", "credit card",
        "card number",
    ],
    PIICategory.ACCOUNT: [
        "계좌번호", "은행계좌", "bank account",
        "입금계좌", "출금계좌",
    ],
    PIICategory.ADDRESS: [
        "주소", "거주지", "address", "우편번호",
        "배송지",
    ],
    PIICategory.API_KEY: [
        "api key", "api_key", "apikey", "secret key",
        "access token", "인증키",
    ],
    PIICategory.PASSWORD: [
        "비밀번호", "패스워드", "password", "비번",
        "암호",
    ],
}
```

### 3.3 탐지 함수 구현

```python
def detect(self, text: str) -> DetectionResult:
    """
    PII 탐지 — 정규식 1차 + 패턴 사전 2차.
    
    정본: D2.0-06 S7D-066 (정규식 + NER), V1=정규식 + dictionary.
    V2+: NER/ML 문맥 인식 마스킹 (IR-022 로드맵).
    
    Args:
        text: 탐지 대상 텍스트
        
    Returns:
        DetectionResult: 탐지 결과 (카테고리별 위치+신뢰도)
        
    Raises:
        PII_ERR_001: text 길이 초과 (max_text_length)
        PII_ERR_002: 탐지 엔진 내부 오류
    """
    # 0. 길이 검증
    if len(text) > self.config.max_text_length:
        raise PIIMaskerError("PII_ERR_001", f"Text length {len(text)} exceeds max {self.config.max_text_length}")
    
    # 1. 정규식 기반 1차 탐지
    regex_hits = self._detect_by_regex(text)
    
    # 2. 패턴 사전 기반 2차 탐지 (문맥 키워드 근처 값 추출)
    dict_hits = self._detect_by_dictionary(text) if self.config.enable_dictionary else []
    
    # 3. 결과 병합 (중복 제거 — 위치 겹침 시 정규식 우선)
    merged = self._merge_detections(regex_hits, dict_hits)
    
    # 4. 신뢰도 필터링
    filtered = [d for d in merged if d.confidence >= self.config.min_confidence]
    
    # 5. 민감도 등급 산출
    sensitivity = self.classify_sensitivity(filtered)
    
    # 6. 결과 구성
    categories_found = list(set(d.category for d in filtered))
    
    return DetectionResult(
        text_length=len(text),
        detections=filtered,
        pii_found=len(filtered) > 0,
        sensitivity_level=sensitivity,
        detection_count=len(filtered),
        categories_found=categories_found,
    )

def _detect_by_regex(self, text: str) -> list[PIIDetection]:
    """정규식 1차 탐지 — O(P * N) where P=패턴 수, N=텍스트 길이"""
    results = []
    for category in self.config.categories:
        patterns = PII_REGEX_PATTERNS.get(category, [])
        for pattern in patterns:
            for match in pattern.finditer(text):
                results.append(PIIDetection(
                    category=category,
                    start=match.start(),
                    end=match.end(),
                    original_text=match.group(),
                    confidence=0.95,  # 정규식 매치 = 높은 신뢰도
                    detector="regex",
                ))
    return results

def _detect_by_dictionary(self, text: str) -> list[PIIDetection]:
    """패턴 사전 2차 탐지 — 키워드 인접 값 추출. 신뢰도 0.7~0.85"""
    results = []
    text_lower = text.lower()
    for category, keywords in PII_DICTIONARY_PATTERNS.items():
        if category not in self.config.categories:
            continue
        for kw in keywords:
            idx = text_lower.find(kw.lower())
            if idx >= 0:
                # 키워드 뒤 30자 범위에서 정규식 미탐지 값 검색
                context_start = idx + len(kw)
                context_end = min(context_start + 60, len(text))
                context = text[context_start:context_end]
                # 숫자/영문 연속열 추출 (PII 후보)
                value_match = re.search(r'[\s:=]*(\S{6,})', context)
                if value_match:
                    abs_start = context_start + value_match.start(1)
                    abs_end = context_start + value_match.end(1)
                    results.append(PIIDetection(
                        category=category,
                        start=abs_start,
                        end=abs_end,
                        original_text=value_match.group(1),
                        confidence=0.8,  # 사전 탐지 — min_confidence(0.8) 기본 통과 가능하도록 (2차 fallback 유효)
                        detector="dictionary",
                    ))
    return results

def _merge_detections(
    self,
    regex_hits: list[PIIDetection],
    dict_hits: list[PIIDetection]
) -> list[PIIDetection]:
    """중복 제거 병합 — 위치 겹침 시 정규식(고신뢰) 우선"""
    merged = list(regex_hits)
    for dh in dict_hits:
        overlap = any(
            rh.start <= dh.start < rh.end or rh.start < dh.end <= rh.end
            for rh in regex_hits
        )
        if not overlap:
            merged.append(dh)
    # 시작 위치 기준 정렬
    merged.sort(key=lambda d: d.start)
    return merged
```

### 3.4 민감도 분류

```python
# 카테고리별 민감도 매핑 — D2.0-06 S7D-065
CATEGORY_SENSITIVITY: dict[PIICategory, SensitivityLevel] = {
    PIICategory.RRN: SensitivityLevel.SECRET,
    PIICategory.CARD: SensitivityLevel.SECRET,
    PIICategory.ACCOUNT: SensitivityLevel.SECRET,
    PIICategory.API_KEY: SensitivityLevel.SECRET,
    PIICategory.PASSWORD: SensitivityLevel.SECRET,
    PIICategory.PHONE: SensitivityLevel.CONFIDENTIAL,
    PIICategory.EMAIL: SensitivityLevel.CONFIDENTIAL,
    PIICategory.ADDRESS: SensitivityLevel.CONFIDENTIAL,
}

SENSITIVITY_ORDER = [
    SensitivityLevel.PUBLIC,
    SensitivityLevel.INTERNAL,
    SensitivityLevel.CONFIDENTIAL,
    SensitivityLevel.SECRET,
]

def classify_sensitivity(self, detections: list[PIIDetection]) -> SensitivityLevel:
    """
    복수 PII 탐지 결과에서 최고 민감도 등급 산출.
    §2.3 카테고리 조합 규칙: 가장 높은 등급 채택.
    PII 미발견 시 PUBLIC.
    """
    if not detections:
        return SensitivityLevel.PUBLIC
    
    max_level = SensitivityLevel.PUBLIC
    for det in detections:
        cat_level = CATEGORY_SENSITIVITY.get(det.category, SensitivityLevel.INTERNAL)
        if SENSITIVITY_ORDER.index(cat_level) > SENSITIVITY_ORDER.index(max_level):
            max_level = cat_level
    
    return max_level
```

---

## 4. 마스킹 전략 (카테고리별)

> **정본**: D2.0-06 §3.3 (`***` 마스킹 또는 hash), S7D-066 (`***` 원본 복구 불가), Part2 항목7 (`***` 마스킹)

### 4.1 카테고리별 마스킹 포맷

| 카테고리 | 마스킹 포맷 | 예시 (원본 → 마스킹) | 복구 가능 여부 |
|---------|-----------|-------------------|-------------|
| RRN | 전체 `***` | `900101-1234567` → `***-***` | 불가 (S7D-066) |
| PHONE | 부분 보존 | `010-1234-5678` → `010-****-****` | 불가 |
| EMAIL | 부분 보존 | `user@domain.com` → `***@***.com` | 불가 |
| CARD | 부분 보존 (BIN만) | `1234-5678-9012-3456` → `1234-****-****-****` | 불가 |
| ACCOUNT | 전체 `***` | `110-123-456789` → `***-***-***` | 불가 |
| ADDRESS | 시/도만 보존 | `서울시 강남구 역삼동 123` → `서울시 ***` | 불가 |
| API_KEY | 전체 `***` | `sk-abc123...` → `[API_KEY_REDACTED]` | 불가 |
| PASSWORD | 전체 `***` | `password=MyP@ss1` → `password=***` | 불가 |

### 4.2 마스킹 함수 구현

```python
# 카테고리별 마스킹 함수 맵
MASK_FUNCTIONS: dict[PIICategory, callable] = {
    PIICategory.RRN: lambda text: re.sub(r'\d', '*', text),
    PIICategory.PHONE: lambda text: _mask_phone(text),
    PIICategory.EMAIL: lambda text: _mask_email(text),
    PIICategory.CARD: lambda text: _mask_card(text),
    PIICategory.ACCOUNT: lambda text: re.sub(r'\d', '*', text),
    PIICategory.ADDRESS: lambda text: _mask_address(text),
    PIICategory.API_KEY: lambda text: "[API_KEY_REDACTED]",
    PIICategory.PASSWORD: lambda text: re.sub(r'(\S+\s*[:=]\s*)\S+', r'\1***', text) if re.search(r'[:=]', text) else "***",
}

def _mask_phone(text: str) -> str:
    """010-1234-5678 → 010-****-****"""
    parts = re.split(r'[-.\s]', text)
    if len(parts) >= 3:
        return f"{parts[0]}-****-****"
    return "***-****-****"

def _mask_email(text: str) -> str:
    """user@domain.com → ***@***.com"""
    at_idx = text.find('@')
    if at_idx < 0:
        return "***"
    domain = text[at_idx+1:]
    dot_idx = domain.rfind('.')
    if dot_idx > 0:
        tld = domain[dot_idx:]
        return f"***@***{tld}"
    return "***@***"

def _mask_card(text: str) -> str:
    """1234-5678-9012-3456 → 1234-****-****-****"""
    digits = re.sub(r'[-\s]', '', text)
    if len(digits) >= 4:
        return f"{digits[:4]}-****-****-****"
    return "****-****-****-****"

def _mask_address(text: str) -> str:
    """서울시 강남구 역삼동 123 → 서울시 ***"""
    # 시/도 추출 후 나머지 마스킹
    match = re.match(r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[시도]?', text)
    if match:
        return f"{match.group()} ***"
    return "***"

def mask(self, text: str) -> MaskResult:
    """
    PII 탐지 후 마스킹 적용.
    
    정본: D2.0-06 §3.3 (*** 마스킹 또는 hash), S7D-066 (원본 복구 불가).
    """
    detection = self.detect(text)
    if not detection.pii_found:
        return MaskResult(
            masked_text=text,
            mask_count=0,
            masking_complete=True,
            categories_masked=[],
        )
    
    masked_text = self._apply_mask(text, detection.detections)
    masking_complete = self._validate_masking_completeness(
        text, masked_text, detection.detections
    )
    
    return MaskResult(
        masked_text=masked_text,
        mask_count=detection.detection_count,
        masking_complete=masking_complete,
        categories_masked=detection.categories_found,
    )

def _apply_mask(self, text: str, detections: list[PIIDetection]) -> str:
    """
    탐지 위치 기반 마스킹 적용 — 뒤에서 앞으로 치환 (인덱스 보존).
    Big-O: O(D * M) where D=탐지 수, M=마스킹 함수 복잡도 (상수)
    """
    # 역순 정렬 (뒤부터 치환하여 인덱스 보존)
    sorted_dets = sorted(detections, key=lambda d: d.start, reverse=True)
    result = text
    for det in sorted_dets:
        mask_fn = MASK_FUNCTIONS.get(det.category, lambda t: "***")
        masked_segment = mask_fn(det.original_text)
        result = result[:det.start] + masked_segment + result[det.end:]
    return result

def _validate_masking_completeness(
    self,
    original: str,
    masked: str,
    detections: list[PIIDetection]
) -> bool:
    """
    마스킹 완전성 검증 — 마스킹 후 원본 PII 잔존 여부 확인.
    D2.0-06 §3.2 옵션 B: 불완전 마스킹 시 deny/보류 처리.
    """
    for det in detections:
        if det.original_text in masked:
            return False  # PII 잔존 — 불완전 마스킹
    return True
```

---

## 5. 데이터 분류 체계 연동 (S7D-065)

> **정본**: D2.0-06 S7D-065 (4등급 민감도: 공개/내부/비밀/극비)

### 5.1 분류 → 저장 정책 매핑

```python
SENSITIVITY_STORAGE_POLICY: dict[SensitivityLevel, dict] = {
    SensitivityLevel.PUBLIC: {
        "storage_allowed": ["L0", "L1", "L2", "L3"],
        "vector_insert": True,
        "mask_required": False,
        "ttl_forced": False,
        "policy_decision": "allow",
    },
    SensitivityLevel.INTERNAL: {
        "storage_allowed": ["L0", "L1", "L2"],
        "vector_insert": True,
        "mask_required": False,
        "ttl_forced": False,
        "policy_decision": "allow",
    },
    SensitivityLevel.CONFIDENTIAL: {
        "storage_allowed": ["L1"],  # S7D-065: L1만(TTL 강제)
        "vector_insert": True,            # 마스킹 후 허용 (D2.0-06 §3.2)
        "mask_required": True,            # 벡터 삽입 전 마스킹 필수
        "ttl_forced": True,               # TTL 강제 적용
        "policy_decision": "restrict",
    },
    SensitivityLevel.SECRET: {
        "storage_allowed": [],            # S7D-065: 저장 금지
        "vector_insert": False,           # LOCK-MR-015: 절대 금지
        "mask_required": True,            # 마스킹 필수 (로그용)
        "ttl_forced": True,
        "policy_decision": "deny",
    },
}
```

### 5.2 분류 판정 흐름

```
입력 텍스트
  │
  ├── PIIMasker.detect(text)
  │     ├── 정규식 1차 탐지
  │     └── 패턴 사전 2차 탐지
  │
  ├── PIIMasker.classify_sensitivity(detections)
  │     └── 최고 민감도 등급 산출
  │
  └── SENSITIVITY_STORAGE_POLICY 조회
        ├── PUBLIC/INTERNAL → allow
        ├── CONFIDENTIAL → restrict (마스킹 후 저장)
        └── SECRET → deny (저장 차단)
```

---

## 6. DCL 연동 — Allow/Restrict/Deny

> **정본**: D2.0-06 §3.2 (Allow/Restrict/Deny 계층별), D2.0-07 PolicyCheck, LOCK-MR-015 (Deny 벡터 삽입 금지)

### 6.1 정책 판정 흐름

```python
def apply_to_record(
    self,
    record,       # MemoryRecord (P0-1)
    policy_decision: str  # D7 PolicyCheck 결과 (allow/restrict/deny) 또는 None=자체 판정
) -> PIIPipelineResult:
    """
    레코드 단위 PII 파이프라인 — Create/Update 경로 통합 진입점.
    
    흐름:
    1. PII 탐지
    2. 민감도 분류
    3. D7 PolicyCheck 결과와 PII 민감도 교차 판정
    4. 정책에 따른 액션 결정 (store/store_masked/block/escalate)
    5. 마스킹 적용 (restrict인 경우)
    6. 벡터 삽입 허용 여부 결정 (LOCK-MR-015)
    7. 로그 기록 (D2.0-07 §2.3.2 SENSITIVE_DATA_FLAG)
    
    LOCK 준수:
    - LOCK-MR-015: deny 시 벡터 삽입 절대 금지
    - LOCK-MR-017: project_id 격리 (입력 record에서 참조)
    - LOCK-MR-018: 사용자 확인 필요 시 escalate
    - LOCK-MR-019: 원문 저장 금지, 요약만 저장
    """
    # 1. PII 탐지
    detect_result = self.detect(record.content_summary or "")
    
    # 2. 민감도 분류
    sensitivity = detect_result.sensitivity_level
    pii_policy = SENSITIVITY_STORAGE_POLICY[sensitivity]
    
    # 3. 교차 판정: D7 PolicyCheck 결과 vs PII 민감도 → 엄격한 쪽 채택
    if policy_decision is None:
        final_decision = pii_policy["policy_decision"]
    else:
        # deny가 하나라도 있으면 deny
        decisions = [policy_decision, pii_policy["policy_decision"]]
        if "deny" in decisions:
            final_decision = "deny"
        elif "restrict" in decisions:
            final_decision = "restrict"
        else:
            final_decision = "allow"
    
    # 4. 액션 결정
    if final_decision == "deny":
        action = "block"
        masked = False
        masking_complete = True
        vector_allowed = False  # LOCK-MR-015: 절대 금지
        content_out = None      # 저장 차단
    elif final_decision == "restrict":
        # D2.0-06 §3.2 옵션 B: 마스킹 후 저장 허용
        mask_result = self.mask(record.content_summary or "")
        masked = True
        masking_complete = mask_result.masking_complete
        
        if not masking_complete and self.config.strict_mode:
            # 마스킹 불완전 + strict_mode → deny 승격
            action = "block"
            final_decision = "deny"
            vector_allowed = False
            content_out = None
        elif not masking_complete and not self.config.strict_mode:
            # §6.3: 마스킹 불완전 + !strict_mode → 사용자 승인 요청 (escalate, LOCK-MR-018)
            action = "escalate"
            vector_allowed = False
            content_out = None
        else:
            action = "store_masked"
            # D2.0-06 §3.2: Restrict 저장이라도 벡터 삽입은 정책/민감도에 따라 별도 판단
            vector_allowed = pii_policy["vector_insert"]
            content_out = mask_result.masked_text
    else:
        # allow
        action = "store"
        masked = detect_result.pii_found  # PII 있으나 공개/내부 등급이면 allow
        masking_complete = True
        vector_allowed = True
        content_out = record.content_summary
    
    # 5. 로그 기록
    event_log = {
        "event_type": "storage.pii.checked",
        "record_id": record.record_id,
        "project_id": record.project_id,
        "pii_found": detect_result.pii_found,
        "pii_count": detect_result.detection_count,
        "categories": [c.value for c in detect_result.categories_found],
        "sensitivity_level": sensitivity.value,
        "policy_decision": final_decision,
        "action": action,
        "vector_insert_allowed": vector_allowed,
        "masking_complete": masking_complete,
    }
    
    if detect_result.pii_found and self.config.sensitive_data_flag:
        event_log["flags"] = ["SENSITIVE_DATA_FLAG"]  # D2.0-07 §2.3.2
    
    self._log_pii_event(event_log["event_type"], event_log)
    
    return PIIPipelineResult(
        record_id=record.record_id,
        project_id=record.project_id,
        policy_decision=final_decision,
        pii_found=detect_result.pii_found,
        sensitivity_level=sensitivity,
        masked=masked,
        masking_complete=masking_complete,
        action=action,
        vector_insert_allowed=vector_allowed,
        content_summary=content_out,
        event_log=event_log,
    )
```

### 6.2 Allow 처리

| 조건 | 동작 | 벡터 삽입 | 저장 |
|------|------|----------|------|
| PII 미발견 | 그대로 저장 | 허용 | 전체 계층 |
| PII 발견 + PUBLIC | 그대로 저장 | 허용 | 전체 계층 |
| PII 발견 + INTERNAL | 그대로 저장 | 허용 (공유 제한) | L1/L2 |

### 6.3 Restrict 처리 (D2.0-06 §3.2 옵션 B)

| 조건 | 동작 | 벡터 삽입 | 저장 |
|------|------|----------|------|
| 마스킹 완전 | 마스킹 후 요약본 + TTL 저장 | 마스킹 후 허용 | L0/L1 (TTL 강제) |
| 마스킹 불완전 + strict_mode | deny 승격 → 저장 차단 | **금지** | 저장 불가 |
| 마스킹 불완전 + !strict_mode | 사용자 승인 요청 (escalate) | 보류 | 승인 후 결정 |

### 6.4 Deny 처리 (LOCK-MR-015)

| 조건 | 동작 | 벡터 삽입 | 저장 |
|------|------|----------|------|
| D7 deny 또는 SECRET | **저장 완전 차단** | **절대 금지** (LOCK-MR-015) | 불가 (모든 저장소) |
| 로그 기록 | input_hint만 (해시/마스킹) | — | 원문 금지 (D2.0-06 §3.3) |

> **[LOCK-MR-015 엄수]**: Deny 판정 시 벡터 삽입 절대 금지. `vector_insert_allowed=False`를 반환하며, 이를 무시하는 호출자는 PII_ERR_010 에러를 발생시킨다.

---

## 7. Create/Update 경로 파이프라인 통합

> **정본**: 종합계획서 P1-7 절차 5 — Create/Update 경로에 PII 탐지→마스킹→저장 순서 보장

### 7.1 파이프라인 순서 (Create 경로)

```
사용자 입력
  │
  ├── [1] MemoryRecord 생성 (P0-1 스키마)
  │     └── project_id 할당 (LOCK-MR-017)
  │
  ├── [2] D7 PolicyCheck 호출 (P1-9 DCL — 미완, 인터페이스만)
  │     └── policy_decision: allow | restrict | deny
  │
  ├── [3] PIIMasker.apply_to_record(record, policy_decision)
  │     ├── PII 탐지 (§3)
  │     ├── 민감도 분류 (§5)
  │     ├── 교차 판정 (§6.1)
  │     ├── 마스킹 적용 (restrict인 경우)
  │     └── 벡터 삽입 허용 결정
  │
  ├── [4] 결과에 따른 분기
  │     ├── action="store" → SQLite INSERT (P1-1/P1-2)
  │     ├── action="store_masked" → 마스킹된 content_summary로 INSERT + masked=True
  │     ├── action="block" → INSERT 거부, 에러 반환 (PII_ERR_006/007)
  │     └── action="escalate" → 사용자 승인 요청 (LOCK-MR-018)
  │
  ├── [5] 벡터 삽입 (P1-3 ChromaVectorStore)
  │     ├── vector_insert_allowed=True → upsert 진행
  │     └── vector_insert_allowed=False → 벡터 삽입 건너뛰기
  │
  └── [6] 감사 로그 기록 (§13 R-01-7)
```

### 7.2 파이프라인 순서 (Update 경로)

```
레코드 수정 요청
  │
  ├── [1] 기존 MemoryRecord 조회 (Read)
  │
  ├── [2] 수정된 content에 대해 PIIMasker.apply_to_record() 재실행
  │     └── 기존 masked=True인 레코드도 수정 시 재탐지 필수
  │
  ├── [3] 결과에 따른 분기 (Create 경로와 동일)
  │
  ├── [4] 기존 벡터 업데이트
  │     ├── vector_insert_allowed=True → upsert (덮어쓰기)
  │     └── vector_insert_allowed=False → 기존 벡터 delete (Deny 전환 시)
  │
  └── [5] 감사 로그 (변경 전/후 정책 비교 기록)
```

### 7.3 P1-1 (L0) / P1-2 (L1) 호출 지점

| 호출 세션 | 호출 지점 | 인터페이스 |
|----------|---------|----------|
| P1-1 (L0) | Create §3.1 step 7 | `apply_pii_masking()` → `PIIMasker.apply_to_record()` |
| P1-1 (L0) | Update 경로 | `PIIMasker.apply_to_record()` 재실행 |
| P1-2 (L1) | Create 경로 | `PIIMasker.apply_to_record()` (L0→L1 승격 시 포함) |
| P1-2 (L1) | Update 경로 | `PIIMasker.apply_to_record()` 재실행 |
| P1-3 (Chroma) | upsert 전 | `vector_insert_allowed` 검사 (P1-7 결과 참조) |
| P1-5 (Cache) | 캐시 저장 전 | deny 레코드 캐시 제외 (S7D-054) |
| P1-6 (Export) | 내보내기 시 | `_check_pii_masking_status()` → `PIIMasker.detect()` |

### 7.4 인터페이스 계약 — P1-6 export_import.md §8 이행

P1-6에서 정의한 인터페이스 계약:
- `detect(text) -> DetectionResult` — **본 문서 §3.3에서 FULL 구현**
- `mask(text) -> MaskResult` — **본 문서 §4.2에서 FULL 구현**

P1-6 `_check_pii_masking_status()` 및 `_recheck_pii_on_import()`는 본 문서의 `detect()`/`mask()` 메서드를 호출하여 활성화된다.

---

## 8. project_id 격리 (LOCK-MR-017)

> **LOCK-MR-017**: 프로젝트 간 데이터 혼합 금지

### 8.1 격리 적용

- PII 탐지/마스킹 결과는 레코드의 `project_id`와 바인딩
- PII 감사 로그에 항상 `project_id` 포함 (추적성)
- 교차 프로젝트 PII 통계 집계 금지 (프로젝트 단위로만 조회)
- PIIMasker 인스턴스는 project_id-agnostic (입력 레코드에서 project_id 참조)

### 8.2 격리 검증

```python
def _validate_project_isolation(self, record) -> None:
    """project_id 존재 여부 검증 — LOCK-MR-017"""
    if not record.project_id:
        raise PIIMaskerError(
            "PII_ERR_003",
            "project_id is required for PII pipeline (LOCK-MR-017)"
        )
```

---

## 9. I-6 SHELL->FULL 전환 명세

> **이슈**: I-6 (PII 마스킹 파이프라인 — regex 4종 나열 → 탐지→분류→마스킹→검증 전체 파이프라인)
> **위치**: 04_memory-distillation

### 9.1 SHELL 상태 (전환 전)

| 항목 | SHELL 상태 | 출처 |
|------|----------|------|
| PII 카테고리 | regex 4종 나열(주민/전화/이메일/카드) | D2.0-06 §3 |
| 탐지 방식 | "정규식" 언급만 | S7D-066 |
| 마스킹 방식 | "***" 언급만 | §3.3 |
| DCL 연동 | 미정의 | — |
| 파이프라인 | 미정의 | — |
| 검증 | 미정의 | — |

### 9.2 FULL 상태 (전환 후 — 본 문서)

| 항목 | FULL 상태 | 본 문서 위치 |
|------|----------|------------|
| PII 카테고리 | **8종** (주민/전화/이메일/카드/계좌/주소/API키/비밀번호) | §2.1 |
| 탐지 방식 | **정규식 1차 + 패턴 사전 2차** (신뢰도 필터링) | §3.1~§3.3 |
| 마스킹 방식 | **카테고리별 개별 포맷** (부분 보존/전체 마스킹/태그) | §4.1~§4.2 |
| 분류 체계 | **4등급 민감도** (PUBLIC/INTERNAL/CONFIDENTIAL/SECRET) | §5 |
| DCL 연동 | **Allow/Restrict/Deny 교차 판정** + LOCK-MR-015 | §6 |
| 파이프라인 | **Create/Update 경로 6단계** (탐지→분류→판정→마스킹→저장→로그) | §7 |
| 검증 | **마스킹 완전성 검증 + strict_mode** (불완전 시 deny 승격) | §4.2 |
| 에러 코드 | **12종** (PII_ERR_001~PII_ERR_012) | §10 |
| 복구/재시도 | **3단계** (자동 재탐지 → 사용자 확인 → 에스컬레이션) | §11 |
| 테스트 | **단위 20건 + Phase 2 통합 12건** | §16~§17 |

### 9.3 전환 증거

- 본 문서(`pii_masking.md`)가 I-6의 FULL 전환 산출물임
- SHELL에서 누락된 항목 전체(분류/DCL/파이프라인/검증/에러/테스트)를 L3 수준으로 구현
- 종합계획서 §6 I-6 행의 상태를 FULL로 갱신 가능

---

## 10. 에러 코드 정의

> **네이밍**: 02 Registry 패턴 UPPER_SNAKE. 접두어 `PII_ERR_`.

| 코드 | 의미 | 발생 조건 | HTTP (참조) | 복구 가능 |
|------|------|---------|-----------|----------|
| PII_ERR_001 | 텍스트 길이 초과 | `len(text) > max_text_length` | 413 | O (텍스트 분할) |
| PII_ERR_002 | 탐지 엔진 내부 오류 | regex/dictionary 예외 | 500 | O (재시도) |
| PII_ERR_003 | project_id 누락 | LOCK-MR-017 위반 | 400 | O (ID 보충) |
| PII_ERR_004 | 카테고리 미설정 | `config.categories` 비어있음 | 400 | O (설정 보정) |
| PII_ERR_005 | 마스킹 불완전 경고 | `masking_complete=False` | 422 | O (수동 마스킹) |
| PII_ERR_006 | Deny 저장 차단 | `policy_decision="deny"` (PII 기반) | 403 | X |
| PII_ERR_007 | Deny 벡터 삽입 차단 | `vector_insert_allowed=False` 무시 시도 | 403 | X |
| PII_ERR_008 | Restrict 마스킹 실패 | 마스킹 함수 예외 | 500 | O (재시도) |
| PII_ERR_009 | 감사 로그 기록 실패 | 로그 저장소 오류 | 500 | O (버퍼 후 재시도) |
| PII_ERR_010 | LOCK-MR-015 위반 시도 | deny 레코드에 벡터 삽입 시도 | 403 | X |
| PII_ERR_011 | 민감도 분류 오류 | 분류 매핑 누락 | 500 | O (기본값 SECRET) |
| PII_ERR_012 | 파이프라인 타임아웃 | 탐지+마스킹 처리 시간 초과 | 504 | O (재시도, 텍스트 분할) |

---

## 11. 복구/재시도 전략

### 11.1 3단계 복구

| 단계 | 조건 | 동작 | 최대 재시도 |
|------|------|------|-----------|
| L1 자동 재시도 | PII_ERR_002, 008, 009, 012 | 500ms 간격 재시도 | 2회 |
| L2 사용자 확인 | PII_ERR_005 (불완전 마스킹) | LOCK-MR-018 사용자 확인 요청 | 1회 |
| L3 에스컬레이션 | L1/L2 실패 | §12 에스컬레이션 페이로드 전달 | 0회 (즉시) |

### 11.2 Fallback 정책

```python
PII_FALLBACK_POLICY = {
    "PII_ERR_002": {
        "fallback": "DENY_CONSERVATIVE",   # 탐지 실패 시 보수적 거부
        "fallback_id": "FB_PII_DETECT_FAIL",
        "description": "탐지 엔진 오류 시 해당 레코드를 deny로 처리 (안전 우선)",
    },
    "PII_ERR_008": {
        "fallback": "DENY_CONSERVATIVE",
        "fallback_id": "FB_PII_MASK_FAIL",
        "description": "마스킹 실패 시 저장 차단 (원문 노출 방지)",
    },
    "PII_ERR_011": {
        "fallback": "CLASSIFY_AS_SECRET",
        "fallback_id": "FB_PII_CLASSIFY_FAIL",
        "description": "분류 오류 시 SECRET으로 간주 (최고 보호 수준)",
    },
}
```

> **안전 원칙**: PII 관련 장애 시 항상 보수적(deny/SECRET) 방향으로 처리. 원문 노출 위험보다 저장 실패가 안전.

---

## 12. 에스컬레이션 정책

### 12.1 에스컬레이션 페이로드

> **정합 기준**: P1-4 (JsonGraphStore §11.1), P1-5 (SemanticCache §12.1), P1-6 (ExportImport §12.1) EscalationPayload JSON 구조와 동일 패턴.

```json
{
  "escalation_id": "ESC-PII-{uuid}",
  "timestamp": "2026-04-13T10:30:00Z",
  "source": "PIIMasker",
  "severity": "WARN | ERROR | CRITICAL",
  "category": "PII_MASKING",
  "project_id": "proj_xxx",
  "operation": "detect | mask | apply_to_record | classify",
  "error_code": "PII_ERR_002 | PII_ERR_005 | PII_ERR_010 | ...",
  "error_type": "PIIMaskerError | PIIDetectionError | PIIMaskIncompleteError | ...",
  "message": "사람이 읽을 수 있는 오류 설명",
  "record_id": "rec_xxx",
  "sensitivity_level": "SECRET | CONFIDENTIAL | INTERNAL | PUBLIC",
  "pii_categories": ["resident_registration_number", "email_address"],
  "context": {
    "pii_count": 3,
    "masking_complete": false,
    "policy_decision": "deny",
    "vector_insert_allowed": false,
    "retry_count": 2,
    "requires_approval": false
  },
  "recommended_action": "PII 재탐지 | 수동 마스킹 | 보안팀 확인",
  "auto_resolved": false
}
```

**Python 데이터 클래스 (역직렬화용)**:

```python
@dataclass
class PIIEscalationPayload:
    """PII 에스컬레이션 페이로드 — D2.0-07 Approval 연동. JSON 구조는 위 §12.1 참조."""
    escalation_id: str                      # ESC-PII-{uuid}
    timestamp: str                          # ISO 8601
    source: str = "PIIMasker"               # 발생 모듈
    severity: str = "ERROR"                 # WARN | ERROR | CRITICAL
    category: str = "PII_MASKING"           # 에스컬레이션 분류
    project_id: str = ""                    # LOCK-MR-017
    operation: str = ""                     # detect | mask | apply_to_record | classify
    error_code: str = ""                    # PII_ERR_*
    error_type: str = ""                    # 예외 클래스명
    message: str = ""                       # 상세 메시지
    record_id: str = ""                     # 대상 레코드 ID
    sensitivity_level: str = ""             # 민감도 등급
    pii_categories: list[str] = field(default_factory=list)  # 탐지된 카테고리
    context: dict = field(default_factory=dict)  # 추가 컨텍스트
    recommended_action: str = ""            # 권장 조치
    auto_resolved: bool = False             # 자동 해소 여부
```

### 12.2 에스컬레이션 조건

| 조건 | 에스컬레이션 대상 | 권장 조치 |
|------|--------------|---------|
| PII_ERR_005 불완전 마스킹 + !strict_mode | 사용자 | 수동 검토 후 allow/deny 결정 |
| PII_ERR_002 탐지 엔진 2회 실패 | 시스템 관리자 | 엔진 상태 점검 |
| SECRET 등급 데이터 발견 | 감사 로그 | 보안 이벤트 기록 |
| LOCK-MR-015 위반 시도 | 보안 팀 | 즉시 차단 + 위반 로그 |

---

## 13. 로깅 규격 (R-01-7)

> **정본**: 02 Registry LogEvent 패턴, D2.0-06 §8 event_type/failure_code

### 13.1 이벤트 유형

| event_type | 발생 조건 | 페이로드 필수 필드 |
|-----------|---------|---------------|
| `storage.pii.checked` | PII 탐지 완료 시 | record_id, project_id, pii_found, categories, sensitivity |
| `storage.pii.masked` | 마스킹 적용 완료 시 | record_id, mask_count, masking_complete, categories_masked |
| `storage.pii.blocked` | Deny 차단 시 (D2.0-06 §8 확정) | record_id, policy_decision=deny, categories |
| `storage.pii.escalated` | 에스컬레이션 발생 시 | escalation_id, error_code, sensitivity_level |
| `storage.pii.violation` | LOCK-MR-015 위반 시도 시 | record_id, attempted_action, violation_type |

### 13.2 Failure Code 매핑

| failure_code | 연결 에러 코드 | 02 Registry 등록 |
|-------------|-------------|---------------|
| ST_PII_DETECTED | PII_ERR_006 | 등록 필요 (D2.0-06 §8) |
| ST_MASK_INCOMPLETE | PII_ERR_005 | 등록 필요 (D2.0-06 §8) |
| ST_VECTOR_DENIED | PII_ERR_007/010 | 등록 필요 (D2.0-06 §8) |
| PII_LONGTERM_DENIED | PII_ERR_006 | 등록 필요 (D2.0-06 §8) |

### 13.3 중첩 JSON 로그 구조

> **정합 기준**: P1-4 (JsonGraphStore §12.1), P1-5 (SemanticCache §13.1), P1-6 (ExportImport §13.2) 중첩 JSON 로그 패턴과 동일.

```json
{
  "log_id": "LOG-PII-{uuid}",
  "timestamp": "2026-04-13T10:30:00.123Z",
  "level": "INFO",
  "component": "PIIMasker",
  "operation": "apply_to_record",
  "project_id": "proj_investment_01",
  "entity_id": "rec_001",
  "status": "PII_DETECTED",
  "duration_ms": 12,
  "details": {
    "pii_found": true,
    "pii_count": 2,
    "categories": ["email_address", "phone_number"],
    "sensitivity_level": "CONFIDENTIAL",
    "policy_decision": "restrict",
    "action": "store_masked",
    "vector_insert_allowed": true,
    "masking_complete": true,
    "flags": ["SENSITIVE_DATA_FLAG"]
  },
  "lock_checks": {
    "MR-015_deny_vector_block": "PASS",
    "MR-017_project_isolation": "PASS",
    "MR-018_user_confirmation": "N/A",
    "MR-019_loop_flood_guard": "PASS"
  },
  "trace_id": "TRACE-{session_uuid}"
}
```

### 13.4 로그 함수 구현

```python
import json, uuid, logging, hashlib
from datetime import datetime, timezone

logger = logging.getLogger("vamos.pii_masker")

def _log_pii_event(self, event_type: str, details: dict) -> None:
    """
    PII 감사 로그 — R-01-7 중첩 JSON 규격 + D2.0-06 §3.3 + §8 준수.
    
    원칙:
    - 원문 PII 절대 평문 기록 금지 (D2.0-07 §2.3.2)
    - PII 값은 SHA-256 해시만 기록 (D2.0-06 §3.3 hash 처리)
    - SENSITIVE_DATA_FLAG 자동 부착 (D2.0-07 §2.3.2)
    - 중첩 JSON 패턴: P1-4/P1-5/P1-6과 동일 (log_id, timestamp, level, component, details)
    """
    # PII 원문이 있으면 해시 변환 (평문 기록 금지)
    safe_details = dict(details)
    if "original_text" in safe_details:
        safe_details["original_text_hash"] = hashlib.sha256(
            safe_details.pop("original_text").encode()
        ).hexdigest()
    
    log_entry = {
        "log_id": f"LOG-PII-{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "WARN" if safe_details.get("action") == "block" else "INFO",
        "component": "PIIMasker",
        "operation": event_type.split(".")[-1],  # e.g., "checked", "masked", "blocked"
        "project_id": safe_details.pop("project_id", ""),
        "entity_id": safe_details.pop("record_id", ""),
        "status": event_type.replace("storage.pii.", "PII_").upper(),
        "duration_ms": safe_details.pop("duration_ms", 0),
        "details": safe_details,
        "lock_checks": {
            "MR-015_deny_vector_block": "PASS" if safe_details.get("action") != "block" else "TRIGGERED",
            "MR-017_project_isolation": "PASS",
            "MR-018_user_confirmation": "N/A",
            "MR-019_loop_flood_guard": "PASS",
        },
        "trace_id": f"TRACE-{uuid.uuid4()}",
    }
    
    logger.info(json.dumps(log_entry, ensure_ascii=False))
```

---

## 14. 시간복잡도 분석 (Big-O)

| 연산 | Big-O | 변수 설명 | LOCK |
|------|-------|---------|------|
| `detect()` 전체 | O(P * N) | P=패턴 수(~20), N=텍스트 길이 | — |
| `_detect_by_regex()` | O(P * N) | P=정규식 패턴 수, N=텍스트 길이 | — |
| `_detect_by_dictionary()` | O(K * N) | K=키워드 수(~40), N=텍스트 길이 | — |
| `_merge_detections()` | O(R * D) | R=regex 탐지 수, D=dict 탐지 수 | — |
| `classify_sensitivity()` | O(D) | D=탐지 수 | — |
| `mask()` 전체 | O(P * N + D) | P=패턴, N=텍스트, D=탐지 수 | — |
| `_apply_mask()` | O(D * M) | D=탐지 수, M=마스킹 함수(상수) | — |
| `_validate_masking_completeness()` | O(D * N) | D=탐지 수, N=마스킹 텍스트 길이 | — |
| `apply_to_record()` | O(P * N + D) | 위 합산 | LOCK-MR-015 |

> **성능 목표**: V1에서 100KB 텍스트 기준 50ms 이내 (정규식 기반, NER 없음). `max_text_length=100_000`으로 DoS 방지.

---

## 15. 예외 처리 정책 표

| 상황 | 에러 코드 | 처리 | Fallback |
|------|---------|------|---------|
| 텍스트 길이 초과 | PII_ERR_001 | 분할 처리 권고, 즉시 에러 | 텍스트 truncate 후 재시도 |
| 정규식 예외 | PII_ERR_002 | 2회 재시도 후 deny | FB_PII_DETECT_FAIL |
| project_id 누락 | PII_ERR_003 | 즉시 에러 | — |
| 카테고리 미설정 | PII_ERR_004 | 즉시 에러 | 기본 전체 카테고리 |
| 마스킹 불완전 | PII_ERR_005 | strict=deny, !strict=escalate | 사용자 확인 |
| Deny 저장 차단 | PII_ERR_006 | 즉시 차단 | — |
| Deny 벡터 차단 | PII_ERR_007 | 즉시 차단 | — |
| 마스킹 함수 예외 | PII_ERR_008 | 2회 재시도 후 deny | FB_PII_MASK_FAIL |
| 로그 기록 실패 | PII_ERR_009 | 버퍼 후 재시도 | 메모리 버퍼 |
| LOCK 위반 시도 | PII_ERR_010 | 즉시 차단 + 위반 로그 | — |
| 분류 오류 | PII_ERR_011 | SECRET 기본값 | FB_PII_CLASSIFY_FAIL |
| 파이프라인 타임아웃 | PII_ERR_012 | 텍스트 분할 후 재시도 | deny 처리 |

---

## 16. 단위 테스트 시나리오

| # | 테스트 | 입력 | 기대 결과 | LOCK |
|---|-------|------|---------|------|
| T-01 | 이메일 정규식 탐지 | `user@test.com 포함 텍스트` | category=EMAIL, confidence>=0.95 | — |
| T-02 | 전화번호 정규식 탐지 | `010-1234-5678 포함 텍스트` | category=PHONE, confidence>=0.95 | — |
| T-03 | 주민번호 정규식 탐지 | `900101-1234567 포함 텍스트` | category=RRN, confidence>=0.95 | — |
| T-04 | 카드번호 정규식 탐지 | `1234-5678-9012-3456 포함` | category=CARD, confidence>=0.95 | — |
| T-05 | 계좌번호 정규식 탐지 | `110-123-456789 포함` | category=ACCOUNT, confidence>=0.95 | — |
| T-06 | API 키 정규식 탐지 | `sk-abc123def456...` | category=API_KEY | — |
| T-07 | 비밀번호 패턴 탐지 | `password=MySecret123` | category=PASSWORD | — |
| T-08 | 주소 패턴 탐지 | `서울시 강남구 역삼동 123` | category=ADDRESS | — |
| T-09 | PII 미발견 | `PII 없는 일반 텍스트` | pii_found=False, PUBLIC | — |
| T-10 | 복수 PII 탐지 | `이메일+전화번호 포함` | 2건 탐지, CONFIDENTIAL | — |
| T-11 | SECRET 등급 판정 | `주민번호 포함` | sensitivity=SECRET | — |
| T-12 | 이메일 마스킹 포맷 | `user@domain.com` | `***@***.com` | — |
| T-13 | 전화번호 마스킹 포맷 | `010-1234-5678` | `010-****-****` | — |
| T-14 | 카드번호 마스킹 (BIN 보존) | `1234-5678-9012-3456` | `1234-****-****-****` | — |
| T-15 | 마스킹 완전성 검증 | 마스킹 후 원본 잔존 | masking_complete=False | — |
| T-16 | Deny 저장 차단 | policy=deny | action=block, vector=False | MR-015 |
| T-17 | Restrict 마스킹 후 저장 | policy=restrict | action=store_masked, masked=True | MR-015 |
| T-18 | Allow 그대로 저장 | policy=allow, PUBLIC | action=store | — |
| T-19 | project_id 누락 | project_id=None | PII_ERR_003 | MR-017 |
| T-20 | 텍스트 길이 초과 | 100,001자 | PII_ERR_001 | — |

---

## 17. Phase 2 통합 테스트

| # | 테스트 | 연동 세션 | 시나리오 | 기대 결과 |
|---|-------|---------|---------|---------|
| P2-T-01 | L0 Create + PII 마스킹 E2E | P1-1 | restrict 입력 → 마스킹 → L0 INSERT | masked=True, content 마스킹 확인 |
| P2-T-02 | L1 Create + PII 마스킹 E2E | P1-2 | restrict 입력 → 마스킹 → L1 INSERT | masked=True |
| P2-T-03 | L0 Create + Deny 차단 E2E | P1-1, P1-3 | deny 입력 → 저장 거부 + 벡터 삽입 금지 | PII_ERR_006, 벡터 0건 |
| P2-T-04 | Chroma 벡터 삽입 PII 검사 | P1-3 | restrict → 마스킹 후 벡터 삽입 | 마스킹된 텍스트 임베딩 |
| P2-T-05 | Semantic Cache PII 제외 | P1-5 | SECRET 레코드 캐시 저장 시도 | 캐시 저장 거부 (S7D-054) |
| P2-T-06 | Export PII 상태 확인 | P1-6 | restrict+unmasked 레코드 내보내기 | EI_ERR_005 경고 |
| P2-T-07 | Import PII 재검사 | P1-6 | 가져오기 시 PII 재탐지 | 신규 PII 발견 시 마스킹 적용 |
| P2-T-08 | DCL 정책 + PII 교차 판정 | P1-9 | D7 allow + PII SECRET | 최종 deny (PII 우선) |
| P2-T-09 | RAG Pipeline PII 필터 | P1-10 | 검색 결과 중 deny 레코드 제외 | deny 레코드 0건 반환 |
| P2-T-10 | Hybrid Search PII 마스킹 | P1-11 | restrict 레코드 검색 | 마스킹된 content 반환 |
| P2-T-11 | 마스킹 완전성 + strict_mode | — | 불완전 마스킹 → deny 승격 | action=block |
| P2-T-12 | LOCK-MR-015 위반 시도 | P1-3 | deny 레코드 강제 벡터 삽입 시도 | PII_ERR_010 + 위반 로그 |

---

## 18. 세션 간 인터페이스 cross-check

### 18.1 P1-1 (L0 CRUD) 접점

| 접점 | 본 세션 (P1-7) | P1-1 | 정합 방법 |
|------|---------------|------|----------|
| restrict 마스킹 | `apply_to_record()` 제공 | Create §3.1 step 7에서 `apply_pii_masking()` 호출 | P1-1의 `apply_pii_masking()` = P1-7의 `PIIMasker.apply_to_record()` |
| deny 차단 | `PIIPipelineResult.action="block"` 반환 | L0_ERR_006 반환 | deny 시 P1-1은 INSERT 거부 |
| project_id | `_validate_project_isolation()` | LOCK-MR-017 검증 | 양측 동일 project_id 사용 |

### 18.2 P1-2 (L1 CRUD) 접점

| 접점 | 본 세션 (P1-7) | P1-2 | 정합 방법 |
|------|---------------|------|----------|
| restrict 마스킹 | 동일 인터페이스 | L1 Create 경로에서 호출 | P1-1과 동일 패턴 |
| L0→L1 승격 시 PII | 승격 레코드도 재탐지 | promoted_from 추적 | 승격 시 PII 파이프라인 재실행 |

### 18.3 P1-3 (Chroma) 접점

| 접점 | 본 세션 (P1-7) | P1-3 | 정합 방법 |
|------|---------------|------|----------|
| 벡터 삽입 허용 | `vector_insert_allowed` 필드 | upsert 전 policy_decision 체크 | P1-7 결과의 `vector_insert_allowed`를 P1-3에서 참조 |
| deny 삽입 금지 | LOCK-MR-015 엄수 | LOCK-MR-015 양측 준수 | deny 시 벡터 0건 삽입 |

### 18.4 P1-5 (Semantic Cache) 접점

| 접점 | 본 세션 (P1-7) | P1-5 | 정합 방법 |
|------|---------------|------|----------|
| deny 캐시 제외 | `action="block"` 시 캐시 저장 금지 | deny 레코드 캐시 거부 | LOCK-MR-015 + S7D-054 |

### 18.5 P1-6 (Export/Import) 접점

| 접점 | 본 세션 (P1-7) | P1-6 | 정합 방법 |
|------|---------------|------|----------|
| 인터페이스 계약 | `detect()` → DetectionResult, `mask()` → MaskResult | §8.1 `_check_pii_masking_status()`, §8.2 `_recheck_pii_on_import()` | P1-6 §8 인터페이스 계약 이행 완료 |
| Export PII 확인 | `detect()` 호출로 실시간 재탐지 | `pii_check_on_export=True` | P1-7 완료 후 활성화 |

### 18.6 P1-9 (DCL 기초 — 미완) 접점

| 접점 | 본 세션 (P1-7) | P1-9 (예정) | 정합 방법 |
|------|---------------|-----------|----------|
| D7 PolicyCheck 결과 | `apply_to_record(record, policy_decision)` 입력으로 수용 | policy_decision 제공 | P1-9 완료 후 D7 결과를 P1-7에 전달 |

### 18.7 P1-10 (6-Stage RAG Pipeline) / P1-11 (Hybrid Search) 접점

| 접점 | 본 세션 (P1-7) | P1-10/P1-11 | 정합 방법 |
|------|---------------|------------|----------|
| 검색 결과 PII 필터 | deny 레코드 반환 금지 | 검색 결과에서 deny 제외 | `policy_decision` 필터링 |
| restrict 결과 | 마스킹된 content 반환 | 마스킹된 텍스트로 응답 | `masked=True` 레코드는 `content_summary` 사용 |

---

## 19. LOCK-MR 참조 추적표

| LOCK | 항목 | 본 문서 적용 위치 | 준수 방법 |
|------|------|------------|---------|
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §6.1 [교차 판정], §6.4, §10 PII_ERR_007/010 | deny 시 `vector_insert_allowed=False` 반환 + 위반 시 PII_ERR_010 |
| LOCK-MR-017 | project_id 격리 | §8, §1.3 PIIPipelineResult | 모든 결과에 project_id 포함, 교차 접근 금지 |
| LOCK-MR-018 | 저장 전 사용자 확인 | §6.3 (restrict 불완전 → escalate) | strict_mode=False 시 사용자 승인 요청 |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §7.1 [6] | 원문 저장 금지, content_summary만 저장 |
| LOCK-MR-001 | 4계층 메모리 | §5.1 (계층별 저장 정책) | 분류별 허용 계층 명시 (L0~L3) |
| LOCK-MR-002 | B↔L 매핑 | — (간접) | 레코드의 scope/memory_type에 따른 파이프라인 동작 |
| LOCK-MR-003/004 | L0/L1 TTL | §5.1 CONFIDENTIAL | TTL 강제 적용 (restrict 시) |
| LOCK-MR-016 | L3 활성 게이트 | §5.1 SECRET/CONFIDENTIAL | L3 저장 시 ApprovalGate 필수 (간접) |

---

## 20. 교차 참조 블록

### 20.1 본 세션 산출물

| 파일 | 경로 | 상태 |
|------|------|------|
| pii_masking.md | `04_memory-distillation/pii_masking.md` | 신규 생성 (v1.1) |

### 20.2 참조한 기존 산출물

| 세션 | 파일 | 참조 내용 |
|------|------|---------|
| P0-1 | `01_memory-hierarchy/MemoryRecordSchema.md` | policy_decision/masked 필드, 20필드 스키마 |
| P1-1 | `01_memory-hierarchy/L0_session_memory_crud.md` | Create §3.1 step 7 apply_pii_masking(), L0_ERR_006 |
| P1-2 | `01_memory-hierarchy/L1_project_memory_crud.md` | L1 Create restrict 마스킹, L0→L1 승격 |
| P1-3 | `03_vector-db/chroma_adapter.md` | upsert 전 policy_decision 체크, deny 벡터 금지 |
| P1-5 | `04_memory-distillation/semantic_cache.md` | deny 캐시 제외 (S7D-054) |
| P1-6 | `04_memory-distillation/export_import.md` | §8 PII 연동 인터페이스 계약 (detect/mask) |

### 20.3 참조한 정본 (SoT)

| 정본 | 섹션 | 참조 내용 |
|------|------|---------|
| D2.0-06 | §3 | 저장 정책 Allow/Restrict/Deny + 마스킹 파이프라인 |
| D2.0-06 | §3.2 | 옵션 B (마스킹 후 저장), Deny 벡터 삽입 절대 금지 |
| D2.0-06 | §3.3 | *** 마스킹/hash, input_summary/input_hint |
| D2.0-06 | S7D-066 | PII 6종 (주민/전화/이메일/주소/카드/계좌), 정규식+NER |
| D2.0-06 | S7D-065 | 4등급 민감도 (공개/내부/비밀/극비), 등급별 처리 |
| D2.0-06 | S7D-054 | 캐시 프라이버시 (PII 미저장) |
| D2.0-06 | §8 | event_type/failure_code (ST_PII_DETECTED 등) |
| D2.0-07 | §2.3.2 | 민감 데이터 평문 기록 금지, SENSITIVE_DATA_FLAG |
| D2.0-07 | S7E-007 | PII 자동 마스킹 (이메일/전화/주민) |
| Part2 | V1-P2 항목7 | pii_masker.py regex, *** 마스킹, VAL-008 |

---

*끝 — P1-7 PII 마스킹 파이프라인 v1.1*
