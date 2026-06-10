# ethics_framework.md — 감정 AI 윤리 프레임워크

> **P-ID**: P-010, P-010-a, P-010-b
> **V단계**: V1
> **상태**: P-010 EXTEND / P-010-a NEW / P-010-b NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/06_ethics-privacy/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 부록 §A | §A.1~A.8 | 개인정보보호·윤리 프레임워크 상세 |
| 종합계획서 §3.4 | LOCK-HW-02/04/06/09 | LOCK 보호 값 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| STEP7-P | P-010 | 감정 AI 윤리 원칙 원본 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| crisis_protocol.md | 동일 폴더 | 위기 감지 프로토콜 (원칙 4 전문가 연결 구현) |
| cbt_distortion_taxonomy.md | 동일 폴더 | CBT 인지왜곡 분류 (R-09-4 적용) |

---

## 1. 개요

본 문서는 VAMOS 감정 AI 기능에 적용되는 윤리 프레임워크를 L3 구현 즉시 투입 가능 수준으로 정의한다. 감정 AI 7원칙(LOCK-HW-09), 비의료 면책(LOCK-HW-04), 프라이버시 등급(LOCK-HW-02), 암호화 규격(LOCK-HW-06)을 필수 제약으로 적용하며, 모든 Health-Wellness-EmotionAI 서브폴더 산출물에 횡단 적용된다.

---

## 2. LOCK 인용

> LOCK (LOCK-HW-09, STEP7-P P-010): 비진단/프라이버시/투명성/전문가연결/비조작/자율성/기능끄기

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-02, 기존 명세 §1/P-018): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-06, 기존 명세 §4): 건강 데이터 저장 시 AES-256-GCM 필수

---

## 3. 감정 AI 7원칙 구현 가이드라인 (P-010, P-010-a)

### 3.1 원칙 1: 비진단 (Non-Diagnostic)

**정의**: 감정 분석 결과를 의학적/심리학적 진단으로 해석하거나 제시하지 않는다.

**구현 상세**:

```python
class NonDiagnosticFilter:
    """
    비진단 원칙 적용 필터.
    모든 감정 분석 응답 텍스트를 검사하여 금지어를 차단한다.
    
    시간복잡도: O(n * m) — n=응답 텍스트 길이, m=금지어 수(고정 ~50개)
    실질적으로 O(n) (Aho-Corasick 패턴 매칭 사용 시)
    """
    
    PROHIBITED_TERMS = [
        "진단", "장애", "질환", "증상", "병", "치료", "치료법",
        "우울증", "불안장애", "PTSD", "조현병", "양극성",
        "diagnosis", "disorder", "disease", "syndrome",
    ]
    
    REPLACEMENT_MAP = {
        "우울증": "우울한 감정 패턴",
        "불안장애": "불안 경향",
        "스트레스 장애": "스트레스 반응 패턴",
    }
    
    def filter_response(self, response_text: str) -> FilterResult:
        """
        응답 텍스트에서 금지어를 검사하고 대체한다.
        
        Returns:
            FilterResult(
                filtered_text: str,      # 필터링된 텍스트
                violations: list[str],   # 감지된 금지어 목록
                disclaimer_appended: bool # 면책 문구 추가 여부
            )
        """
        violations = []
        filtered = response_text
        
        for term in self.PROHIBITED_TERMS:
            if term in filtered:
                violations.append(term)
                if term in self.REPLACEMENT_MAP:
                    filtered = filtered.replace(term, self.REPLACEMENT_MAP[term])
                else:
                    # 대체어 없는 금지어 → 응답 생성 재시도
                    raise ProhibitedTermError(
                        term=term,
                        error_code="ETH-001",
                        recoverable=True,
                        action="regenerate_response"
                    )
        
        # LOCK-HW-04 면책 문구 항상 추가
        filtered = self._append_disclaimer(filtered)
        
        return FilterResult(
            filtered_text=filtered,
            violations=violations,
            disclaimer_appended=True
        )
```

**위반 감지**: CI/CD 파이프라인에서 응답 텍스트 금지어 자동 스캔. 금지어 포함 응답 = 테스트 실패.

**로깅**:
```json
{
  "trace_id": "eth-nondx-{uuid}",
  "error": {
    "code": "ETH-001",
    "message": "Prohibited term detected in response",
    "term": "진단",
    "position": 42
  },
  "context": {
    "module": "ethics_framework.non_diagnostic_filter",
    "response_id": "{response_uuid}",
    "timestamp": "2026-04-10T09:00:00Z"
  },
  "recovery": {
    "action": "regenerate_response",
    "attempt": 1,
    "max_retries": 3,
    "fallback": "generic_empathy_response"
  }
}
```

### 3.2 원칙 2: 프라이버시 (Privacy)

**정의**: 감정 데이터는 사용자 본인만 접근 가능하며, 최소 수집·로컬 처리 원칙을 준수한다.

**구현 상세**:

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class PrivacyLevel(Enum):
    """프라이버시 등급 (LOCK-HW-02)"""
    PRIVATE = "PRIVATE"      # 감정 데이터 — 로컬 전용
    PROTECTED = "PROTECTED"  # 건강 데이터 — AES-256 + 별도 PIN
    HIGHEST = "HIGHEST"      # 의료 데이터 — 외부 전송 절대 금지

@dataclass
class DataClassification:
    """데이터 분류 판정 결과"""
    data_type: str
    privacy_level: PrivacyLevel
    storage_location: str          # "local_only" | "local_preferred" | "isolated"
    encryption: str                # "AES-256-GCM" | "AES-256-GCM+PIN" | "AES-256-GCM+MASTER"
    external_transfer: str         # "prohibited" | "summary_with_consent" | "absolutely_prohibited"
    retention_period: str          # TTL 규칙
    purpose_codes: list[str] = field(default_factory=list)  # EMO, HLT, STR, WEL

class PrivacyClassifier:
    """
    데이터 프라이버시 등급 분류기.
    
    분류 규칙 (종합계획서 부록 §A.1):
    1. 불명확 → 상위 등급 (보수적)
    2. 복합 데이터 → 최고 등급
    3. 집계/익명화 → 원본 등급 한 단계 아래까지만 완화
    """
    
    CLASSIFICATION_TABLE = {
        "emotion_analysis": DataClassification(
            data_type="감정 분석 결과",
            privacy_level=PrivacyLevel.PRIVATE,
            storage_location="local_only",
            encryption="AES-256-GCM",
            external_transfer="prohibited",
            retention_period="user_setting_default_180d",
            purpose_codes=["EMO"]
        ),
        "health_activity": DataClassification(
            data_type="건강 데이터 (활동/수면/영양/체중)",
            privacy_level=PrivacyLevel.PROTECTED,
            storage_location="local_preferred",
            encryption="AES-256-GCM+PIN",
            external_transfer="summary_with_consent",
            retention_period="aggregate_90d_raw_24h",
            purpose_codes=["HLT"]
        ),
        "medical_records": DataClassification(
            data_type="의료 기록/약물/진단",
            privacy_level=PrivacyLevel.HIGHEST,
            storage_location="isolated",
            encryption="AES-256-GCM+MASTER",
            external_transfer="absolutely_prohibited",
            retention_period="until_user_explicit_delete",
            purpose_codes=["HLT"]
        ),
    }
    
    def classify(self, data_types: list[str]) -> DataClassification:
        """복합 데이터 시 최고 등급 적용"""
        levels = [self.CLASSIFICATION_TABLE[dt].privacy_level for dt in data_types]
        highest = max(levels, key=lambda l: list(PrivacyLevel).index(l))
        return self.CLASSIFICATION_TABLE[
            next(dt for dt in data_types 
                 if self.CLASSIFICATION_TABLE[dt].privacy_level == highest)
        ]
```

**빌드 타임 검증**: CI/CD 정적 분석에서 감정 데이터(PRIVATE 등급) 외부 호출 감지 시 빌드 실패.

```python
# CI/CD 정적 분석 규칙 (의사코드)
PROHIBITED_EXTERNAL_CALLS = [
    r"http\.post\(.*(emotion|감정|feeling)",
    r"api\.send\(.*(emotion_data|mood_log)",
    r"cloud\.upload\(.*(private_data|emotion)",
]
# 매칭 시 → 빌드 실패 + P0 버그 등록
```

### 3.3 원칙 3: 투명성 (Transparency)

**정의**: 감정 분석이 언제, 어떻게, 왜 수행되는지 사용자에게 명확히 고지한다.

**구현 상세**:

```python
@dataclass
class EmotionAnalysisIndicator:
    """감정 분석 활성 인디케이터 UI 상태"""
    is_active: bool
    analysis_type: str            # "text" | "voice" | "multimodal"
    confidence_score: float       # 0.0 ~ 1.0
    primary_keywords: list[str]   # 분석 근거 키워드 (최대 5개)
    explanation_available: bool   # 사용자 요청 시 상세 설명 가능 여부
    
    def to_ui_state(self) -> dict:
        return {
            "icon": "emotion_active" if self.is_active else "emotion_inactive",
            "tooltip": f"감정 인식 중 ({self.analysis_type})",
            "detail_button": self.explanation_available,
        }
    
    def explain(self) -> str:
        """사용자 요청 시 분석 근거 공개"""
        return (
            f"감정 분석 방식: {self.analysis_type}\n"
            f"신뢰도: {self.confidence_score:.0%}\n"
            f"주요 근거 키워드: {', '.join(self.primary_keywords)}"
        )
```

**위반 감지**: 감정 분석 활성 상태에서 인디케이터 미표시 = UI 테스트 실패.

### 3.4 원칙 4: 전문가 연결 (Expert Referral)

**정의**: 위기 상황 감지 시 반드시 전문 기관/전문가를 안내하며, 자체 해결을 시도하지 않는다.

**구현 상세**: `crisis_protocol.md` 에 상세 정의. 본 문서에서는 원칙 수준 요약.

- HIGH 위험도 → 즉시 전문기관 정보(LOCK-HW-05: 1393, 1577-0199) 표시
- 자체 해결 시도 = 절대 금지 (P0 버그)
- R-09-2: 위기 키워드 감지 시 즉시 전문기관 안내 (예외 없음)

**위반 감지**: 위기 감지 후 전문기관 미안내 = P0 버그.

### 3.5 원칙 5: 비조작 (Non-Manipulation)

**정의**: 감정 분석 결과를 상업적 목적(구매 유도, 광고 타겟팅, 행동 조작)으로 사용하지 않는다.

**구현 상세**:

```python
class EmotionDataAccessControl:
    """
    감정 데이터 접근 제어.
    마케팅/광고 모듈은 API 레벨에서 접근 자체를 차단한다.
    """
    
    BLOCKED_MODULES = [
        "marketing", "advertising", "ad_targeting",
        "purchase_recommendation", "behavior_nudging",
    ]
    
    def check_access(self, caller_module: str, data_type: str) -> AccessResult:
        if caller_module in self.BLOCKED_MODULES:
            self._log_violation(caller_module, data_type)
            return AccessResult(
                allowed=False,
                reason="R-09-7: 감정 데이터 상업적 사용 금지",
                action="block_and_alert"
            )
        return AccessResult(allowed=True)
    
    def _log_violation(self, module: str, data_type: str):
        """위반 시도 즉시 로깅 + 알림"""
        log_entry = {
            "trace_id": f"eth-manip-{uuid4()}",
            "error": {
                "code": "ETH-005",
                "message": "Blocked commercial access to emotion data",
                "module": module,
                "data_type": data_type
            },
            "context": {
                "rule": "R-09-7",
                "principle": "non_manipulation",
                "timestamp": datetime.utcnow().isoformat()
            },
            "recovery": {
                "action": "block_access",
                "alert_sent": True,
                "escalation": "security_team"
            }
        }
        structured_log(log_entry)
```

**위반 감지**: 감정 데이터 참조 API 호출 로그에서 마케팅 모듈 접근 감지 시 즉시 알림 + 기능 비활성.

### 3.6 원칙 6: 자율성 (Autonomy)

**정의**: 사용자가 감정 분석 결과에 대해 동의하지 않을 권리를 보장한다.

**구현 상세**:

```python
@dataclass
class EmotionFeedback:
    """사용자 감정 분석 피드백"""
    session_id: str
    original_emotion: str        # 시스템 분석 결과
    user_correction: str         # 사용자 수정 값
    confidence_before: float
    timestamp: str
    
class EmotionFeedbackHandler:
    """
    사용자 피드백 처리기.
    사용자가 감정 분석 결과를 수정하면 즉시 해당 세션의 결과를 덮어쓴다.
    """
    
    def apply_correction(self, feedback: EmotionFeedback) -> None:
        # 1. 해당 세션의 분석 결과 즉시 덮어쓰기
        self.session_store.update_emotion(
            session_id=feedback.session_id,
            emotion=feedback.user_correction,
            source="user_correction",
            confidence=1.0  # 사용자 수정은 최대 신뢰도
        )
        
        # 2. 피드백 로그 기록 (익명화, 모델 개선용 아님 — R-09-5)
        self._log_feedback(feedback)
        
        # 3. UI 확인 메시지
        return "감정 분석 결과가 수정되었습니다. 감사합니다."
```

**위반 감지**: 피드백 UI 미제공 = UX 검수 실패.

### 3.7 원칙 7: 기능 끄기 (Opt-Out)

**정의**: 사용자가 언제든 감정 분석/건강 추적 등 모든 기능을 비활성화할 수 있다.

**구현 상세**:

```python
class EmotionAIGlobalToggle:
    """
    감정 AI 전체 끄기 원클릭 토글.
    위치: 설정 > 프라이버시 > 감정AI 전체 끄기
    """
    
    def disable_all(self, user_id: str) -> DisableResult:
        """
        감정 AI 전체 비활성화.
        기존 데이터는 유지 (별도 삭제 선택 제공).
        """
        # 1. 모든 감정 관련 처리 즉시 중단
        self.emotion_recognition.stop()
        self.adaptive_response.stop()
        self.emotion_journal.stop()
        self.wellness_score.stop()
        # R-09-2 (예외 없음): 위기 감지는 전역 감정 AI 토글과 무관하게 항상 활성 유지.
        # crisis_detection.stop() 호출 금지 — 생명 안전 경로 차단 = P0 버그.
        
        # 2. 활성 세션의 감정 분석 즉시 중단
        self.session_manager.clear_emotion_context(user_id)
        
        # 3. 데이터 유지 (삭제는 별도 선택)
        # → 사용자에게 "기존 데이터 삭제 여부" 다이얼로그 표시
        
        # 4. 감사 로그
        self._audit_log(user_id, action="global_disable")
        
        return DisableResult(
            success=True,
            data_retained=True,
            delete_prompt_shown=True,
            message="감정 AI 기능이 비활성화되었습니다."
        )
    
    def enable_all(self, user_id: str) -> EnableResult:
        """재활성화 시 동의 플로우 재실행"""
        return self.consent_manager.show_granular_consent(user_id)
```

**위반 감지**: 끄기 후에도 감정 분석 실행 감지 시 = P0 버그.

---

## 4. 비의료 면책 표준 문구 (P-010-b)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

### 4.1 한국어 표준 문구

```
⚕️ 안내: VAMOS는 의료 서비스가 아닙니다. 제공되는 건강 정보와 감정 분석은
참고용이며, 의학적 진단·치료·처방을 대체하지 않습니다. 건강에 관한 우려가
있으시면 의료 전문가와 상담하시기 바랍니다.
```

### 4.2 영어 표준 문구

```
⚕️ Notice: VAMOS is not a medical service. Health information and emotion
analysis provided are for reference only and do not replace professional
medical diagnosis, treatment, or prescription. If you have health concerns,
please consult a healthcare professional.
```

### 4.3 CBT 도구 추가 면책 문구

```
이 도구는 자가 관리 보조 도구이며, 전문 심리 상담을 대체하지 않습니다.
```

### 4.4 적용 규칙

| 규칙 | 설명 |
|------|------|
| 건강 관련 응답 매회 포함 | 생략 불가 (R-09-1) |
| 감정-건강 연관 언급 시 포함 | 감정 분석 결과를 건강과 연관 지어 언급 시 |
| CBT 도구 사용 시 | 표준 문구 + CBT 추가 문구 함께 포함 |
| 위치 | 응답 말미 (사용자 경험 방해 최소화) |
| 누락 시 | 응답 차단 (R-09-1 위반) |

### 4.5 면책 문구 자동 삽입 구현

```python
class DisclaimerInjector:
    """
    면책 문구 자동 삽입기.
    
    시간복잡도: O(1) — 응답 말미에 문자열 연결
    ABC 패턴: Append (응답 후처리 파이프라인의 마지막 단계)
    """
    
    HEALTH_DISCLAIMER_KO = (
        "⚕️ 안내: VAMOS는 의료 서비스가 아닙니다. "
        "제공되는 건강 정보와 감정 분석은 참고용이며, "
        "의학적 진단·치료·처방을 대체하지 않습니다. "
        "건강에 관한 우려가 있으시면 의료 전문가와 상담하시기 바랍니다."
    )
    
    CBT_DISCLAIMER_KO = (
        "이 도구는 자가 관리 보조 도구이며, "
        "전문 심리 상담을 대체하지 않습니다."
    )
    
    def inject(self, response: str, context: ResponseContext) -> str:
        """
        응답 유형에 따라 면책 문구를 자동 삽입한다.
        
        Args:
            response: 원본 응답 텍스트
            context: 응답 맥락 (health_related, cbt_tool 등)
        
        Returns:
            면책 문구가 추가된 응답
        """
        if context.is_health_related or context.is_emotion_health_linked:
            response += f"\n\n{self.HEALTH_DISCLAIMER_KO}"
        
        if context.is_cbt_tool:
            response += f"\n{self.CBT_DISCLAIMER_KO}"
        
        return response
```

---

## 5. 프라이버시 등급 구현 상세

### 5.1 데이터 분류 체계 (부록 §A.1 L3 변환)

| 등급 | 대상 데이터 | 저장 위치 | 암호화 | 접근 제어 | 외부 전송 | 보존 기간 |
|------|-----------|----------|--------|----------|----------|----------|
| **PRIVATE** | 감정 분석 결과, 감정 로그, 대화 감정 메타데이터 | 로컬 전용 (디바이스) | AES-256-GCM | 사용자 본인만 | **절대 금지** | 사용자 설정 (기본 180일) |
| **PROTECTED** | 건강 데이터 (활동, 수면, 영양, 체중), 웰니스 점수 | 로컬 우선, 동기화 시 E2E 암호화 | AES-256-GCM + 별도 PIN | 사용자 본인 + 명시적 허가 모듈 | 사용자 동의 시 요약만 | 집계 90일, 원시 24시간 TTL |
| **HIGHEST** | 의료 기록, 약물 정보, 진단 이력 | 로컬 전용 (격리 저장소) | AES-256-GCM + 별도 마스터 키 | 사용자 본인만 (PIN + 생체인증) | **절대 금지 (예외 없음)** | 사용자 명시적 삭제까지 |

### 5.2 분류 판정 규칙

1. 데이터 유형 불명확 → **상위 등급** 적용 (보수적 판정)
2. 복합 데이터(감정+건강 결합) → 포함된 데이터 중 **최고 등급**
3. 집계/익명화 데이터 → 원본 등급의 **한 단계 아래**까지만 완화

### 5.3 암호화 규격 (부록 §A.2 L3 변환)

> LOCK (LOCK-HW-06, 기존 명세 §4): 건강 데이터 저장 시 AES-256-GCM 필수

| 항목 | 규격 |
|------|------|
| 알고리즘 | AES-256-GCM (인증 암호화) |
| 키 길이 | 256-bit |
| IV/Nonce | 96-bit 난수 (동일 키 2^32 이상 암호화 금지) |
| 키 파생 | Argon2id (정본 — medical_records §3.5 정합, 단일 KDF). PBKDF2-HMAC-SHA256(>=100,000 iters)는 Argon2id 미지원 레거시 폴백 한정 |
| 키 로테이션 | 90일 주기 자동 |
| At-Rest | SQLCipher 또는 OS Keychain 연동 |
| In-Transit | TLS 1.3 (PROTECTED 동기화) |
| 키 저장 | OS Secure Enclave / Android Keystore / Windows DPAPI |

### 5.4 키 관리 프로세스

```
[사용자 비밀번호] → PBKDF2 → [마스터 키]
  → KDF → [데이터 암호화 키 (DEK)]  ← 실제 데이터 암호화
  → KDF → [키 암호화 키 (KEK)]      ← DEK 래핑

키 로테이션:
  1. 새 DEK 생성
  2. 기존 데이터를 새 DEK로 재암호화 (백그라운드)
  3. 구 DEK 안전 삭제 (메모리 제로화)
  4. 키 로테이션 이벤트 감사 로그 기록
```

---

## 6. 동의 관리 (부록 §A.4 L3 변환)

### 6.1 동의 모델: Granular Opt-in

```python
@dataclass
class ConsentItem:
    """세분화 동의 항목"""
    item_id: str
    label: str
    default: bool = False       # 기본 OFF (opt-in)
    description: str = ""
    data_collected: str = ""
    storage_location: str = ""
    retention_period: str = ""
    revocation_impact: str = ""

CONSENT_ITEMS = [
    ConsentItem("text_emotion",    "텍스트 감정 분석", False,
                "대화 텍스트에서 감정 추론", "감정 카테고리+강도",
                "로컬 전용", "사용자 설정(기본 180일)",
                "감정 적응 응답 비활성"),
    ConsentItem("voice_emotion",   "음성 감정 분석", False,
                "음성 톤/피치에서 감정 추론", "음성 감정 벡터",
                "로컬 전용", "세션 종료 시 삭제",
                "음성 감정 인식 비활성"),
    ConsentItem("health_sync",     "건강 데이터 연동", False,
                "Apple Health/Google Fit 읽기", "활동/수면/영양 데이터",
                "로컬 우선(E2E 암호화)", "집계 90일/원시 24h",
                "건강 대시보드 비활성"),
    ConsentItem("emotion_journal", "감정 일지 자동 기록", False,
                "대화 기반 감정 자동 기록", "감정 이벤트",
                "로컬 전용", "사용자 설정",
                "수동 기록만 가능"),
    ConsentItem("edu_emotion",     "Education 감정 공유", False,
                "#8 Education 도메인에 감정 요약 공유",
                "7분류+강도+arousal/valence", "로컬→Education(opt-in)",
                "Education 연동 시까지", "학습 적응 감정 연동 비활성"),
    ConsentItem("wellness_score",  "웰니스 점수 계산", False,
                "VWS 5차원 점수 산출", "VWS 점수(0-100)",
                "로컬 전용", "90일", "대시보드에 점수 미표시"),
]
```

### 6.2 동의 철회 플로우

```
[동의 철회 시]:
  1. 즉시 해당 기능 비활성
  2. 수집 중인 데이터 처리 즉시 중단
  3. 기존 데이터 삭제 여부 묻기 (선택적)
  4. 철회 사실 감사 로그 기록
```

---

## 7. 데이터 삭제 (부록 §A.5 L3 변환)

### 7.1 삭제 유형

| 유형 | 대상 | 처리 | 소요 시간 |
|------|------|------|----------|
| 개별 | 특정 감정 로그, 특정 날짜 건강 데이터 | 레코드 + 인덱스 제거 | 즉시 |
| 카테고리 | 모든 감정/건강 데이터 | 전체 + 집계 재계산 | 5초 이내 |
| 전체 | 모든 H-W-E 데이터 | 전체 DB 파기 + 키 삭제 | 10초 이내 |
| 계정 연동 | VAMOS 계정 삭제 | 전체 삭제 + 백업 파기 + 감사 로그 30일 보존 | 즉시 |

### 7.2 완전 삭제 보장 (Crypto-Shredding)

```python
class SecureDataDeletion:
    """
    완전 삭제 보장.
    Crypto-Shredding: 암호화 키를 삭제하여 데이터를 복호화 불가 상태로 만든다.
    """
    
    def delete_secure(self, target: DeletionTarget) -> DeletionResult:
        # 1. 데이터 레코드 삭제 (DB DELETE)
        self.db.delete(target.records)
        
        # 2. 관련 인덱스 엔트리 제거
        self.index.remove(target.index_entries)
        
        # 3. 관련 캐시 무효화
        self.cache.invalidate(target.cache_keys)
        
        # 4. 암호화 키 안전 삭제 (Crypto-Shredding)
        self.key_store.secure_delete(target.encryption_key_id)
        
        # 5. 저장 공간 제로 필 (민감 등급 시)
        if target.privacy_level in (PrivacyLevel.PROTECTED, PrivacyLevel.HIGHEST):
            self.storage.zero_fill(target.storage_blocks)
        
        # 6. 삭제 확인 감사 로그 (내용 없이 "삭제됨" 사실만)
        self.audit.log_deletion(target.id, verified=True)
        
        # 7. 복구 불가 확인 테스트 (자동)
        assert not self.db.exists(target.records)
        
        return DeletionResult(success=True, verified=True)
```

---

## 8. 외부 감사 대응 (부록 §A.8 L3 변환)

| 감사 항목 | 기록 내용 | 보존 기간 | 접근 권한 |
|----------|----------|----------|----------|
| 데이터 접근 로그 | 누가, 언제, 어떤 데이터에 접근 | 1년 | 시스템 관리자 + 감사인 |
| 동의 변경 로그 | 항목, 전/후, 시각 | 3년 | 시스템 관리자 + 감사인 |
| 데이터 삭제 로그 | 카테고리, 시각, 완료 확인 | 3년 | 시스템 관리자 + 감사인 |
| 위기 감지 로그 | 시각, 위험도, 조치 (대화 내용 미포함) | 1년 | 시스템 관리자 |
| 키 로테이션 로그 | 시각, 영향 범위 | 1년 | 시스템 관리자 |
| API 호출 로그 | 외부 모듈 접근 시도 | 1년 | 시스템 관리자 + 감사인 |

---

## 9. 에스컬레이션 페이로드 구조

```python
@dataclass
class EthicsEscalationPayload:
    """
    윤리 위반 에스컬레이션 페이로드.
    I-20 경유 (R-01-8) 에스컬레이션 구조.
    """
    escalation_id: str           # "ESC-ETH-{uuid}"
    severity: str                # "P0" | "P1" | "P2"
    principle_violated: str      # 7원칙 중 위반된 원칙
    rule_violated: str           # R-09-1 ~ R-09-7
    violation_detail: str        # 위반 상세
    evidence: dict               # 증거 (로그 참조)
    timestamp: str
    auto_action_taken: str       # 자동 조치 (차단/비활성 등)
    requires_human_review: bool  # 사람 검토 필요 여부
    
    def to_i20_payload(self) -> dict:
        """I-20 에스컬레이션 인터페이스 형식으로 변환"""
        return {
            "source": "health-wellness-emotionai/ethics",
            "escalation_id": self.escalation_id,
            "severity": self.severity,
            "category": "ethics_violation",
            "detail": {
                "principle": self.principle_violated,
                "rule": self.rule_violated,
                "description": self.violation_detail,
            },
            "evidence_ref": self.evidence,
            "auto_action": self.auto_action_taken,
            "human_review": self.requires_human_review,
            "timestamp": self.timestamp,
        }
```

---

## 10. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|-------------|------|
| ETH-001 | 응답에 금지어(진단/장애/질환) 포함 | YES | 응답 재생성 (최대 3회), 실패 시 generic_empathy_response |
| ETH-002 | PRIVATE 데이터 외부 전송 시도 | NO | 즉시 차단 + P0 버그 등록 + 보안팀 에스컬레이션 |
| ETH-003 | 면책 문구 삽입 실패 | YES | 재삽입 시도, 실패 시 응답 전체 차단 (R-09-1) |
| ETH-004 | 위기 감지 후 전문기관 미안내 | NO | P0 버그 + 즉시 수동 안내 트리거 + 세션 기록 |
| ETH-005 | 마케팅 모듈의 감정 데이터 접근 | NO | 접근 차단 + 보안 알림 + R-09-7 위반 기록 |
| ETH-006 | 끄기 후 감정 분석 실행 감지 | NO | P0 버그 + 강제 중단 + 감사 로그 |
| ETH-007 | 동의 없는 데이터 수집 | NO | 수집 즉시 중단 + 수집 데이터 삭제 + P0 에스컬레이션 |
| ETH-008 | 키 로테이션 실패 | YES | 재시도 (3회), 실패 시 암호화 키 긴급 갱신 + 관리자 알림 |
| ETH-009 | 데이터 삭제 불완전 | YES | 재삭제 시도, 실패 시 Crypto-Shredding 강제 실행 |
| ETH-010 | 투명성 인디케이터 미표시 | YES | UI 강제 갱신, 실패 시 감정 분석 일시 중단 |

---

## 11. Phase별 복구 전략

### Phase 1 (현재): 기본 복구

```
[윤리 위반 감지]
  → 자동 조치 (차단/비활성)
  → 로그 기록
  → 에스컬레이션 (P0/P1)
  → 수동 검토
```

### Phase 2: 자동 복구 강화

```
[위반 감지]
  → 자동 분류 (원칙별)
  → recoverable → 자동 재시도/대체
  → non-recoverable → 즉시 차단 + 에스컬레이션
  → 위반 패턴 분석 → 예방 규칙 갱신
```

### Phase 3: 예측 기반 예방

```
[사전 예측]
  → 응답 생성 전 윤리 검사 (pre-check)
  → 위반 가능성 높은 패턴 사전 차단
  → A/B 테스트 기반 면책 문구 최적화
```

### Phase 4: 완전 자동화

```
[지속 모니터링]
  → 실시간 윤리 준수 대시보드
  → 자동 감사 보고서 생성
  → 규제 변경 자동 반영
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | penalty | 결과 |
|-----------------|---------|------|
| Phase 3 → Phase 2 | -0.1 | 예측 검사 비활성, 사후 검사만 |
| Phase 2 → Phase 1 | -0.2 | 자동 복구 비활성, 수동 검토 필수 |
| Phase 1 → 긴급 모드 | -0.5 | 모든 건강 응답 차단, 면책 문구만 표시 |

---

## 12. Phase 2 테스트 시나리오

| # | 시나리오 | 입력/조건 | 기대 결과 | 관련 원칙 |
|---|---------|----------|----------|----------|
| T-ETH-01 | 응답에 "진단" 포함 | 감정 분석 결과에 "우울증 진단" 텍스트 | 금지어 필터 차단 + 응답 재생성 | 원칙1 비진단 |
| T-ETH-02 | PRIVATE 데이터 외부 전송 | 감정 데이터 HTTP POST 시도 | 빌드 실패 (정적 분석) | 원칙2 프라이버시 |
| T-ETH-03 | 감정 분석 인디케이터 미표시 | 감정 분석 활성 + UI 렌더링 | 인디케이터 필수 표시 | 원칙3 투명성 |
| T-ETH-04 | HIGH 위기 감지 후 전문기관 미안내 | 위기 키워드 "자살" 입력 | 즉시 1393/1577-0199 표시 | 원칙4 전문가연결 |
| T-ETH-05 | 마케팅 모듈 감정 데이터 접근 | marketing 모듈이 emotion API 호출 | 접근 차단 + 보안 알림 | 원칙5 비조작 |
| T-ETH-06 | 사용자 감정 수정 피드백 | 분석: 분노 → 사용자: 피로 | 즉시 "피로"로 덮어쓰기 | 원칙6 자율성 |
| T-ETH-07 | 전체 끄기 후 분석 실행 | 감정AI 끄기 → 텍스트 입력 | 감정 분석 미실행 확인 | 원칙7 기능끄기 |
| T-ETH-08 | 면책 문구 누락 | 건강 관련 응답 생성 | LOCK-HW-04 문구 필수 포함 | R-09-1 |
| T-ETH-09 | 복합 데이터 등급 판정 | 감정+건강 결합 데이터 | PROTECTED (최고 등급) 적용 | §A.1 규칙2 |
| T-ETH-10 | 동의 철회 시 즉시 중단 | 텍스트 감정 분석 동의 OFF | 해당 기능 즉시 비활성 확인 | §A.4 |
| T-ETH-11 | Crypto-Shredding 삭제 | 전체 삭제 요청 | 키 삭제 + 데이터 복구 불가 | §A.5 |
| T-ETH-12 | 키 로테이션 90일 | 90일 경과 시뮬레이션 | 자동 로테이션 + 재암호화 + 로그 | §A.2 |
| T-ETH-13 | Education opt-in 미동의 상태 | edu_emotion OFF + Education 요청 | 데이터 공유 차단 | R-09-6 |
| T-ETH-14 | 건강 데이터 AI 학습 시도 | 학습 파이프라인에서 건강 데이터 접근 | 접근 차단 | R-09-5 |
| T-ETH-15 | CBT 도구 "치료" 단어 사용 | CBT 응답에 "치료" 포함 | 금지어 필터 차단 | R-09-4 |

---

## 13. 공통 자료 구조 선정의

본 문서에서 정의한 공통 자료 구조:

| 클래스/Enum | 용도 | 참조 위치 |
|------------|------|----------|
| `PrivacyLevel` | 프라이버시 등급 3단계 | §3.2, 전 서브폴더 |
| `DataClassification` | 데이터 분류 판정 결과 | §3.2, §5 |
| `ConsentItem` | 동의 항목 구조 | §6.1 |
| `EmotionAnalysisIndicator` | 투명성 UI 상태 | §3.3 |
| `EmotionFeedback` | 사용자 피드백 | §3.6 |
| `EthicsEscalationPayload` | 에스컬레이션 페이로드 | §9 |

---

> **문서 끝** — ethics_framework.md V1 L3 완성 (2026-04-10)
