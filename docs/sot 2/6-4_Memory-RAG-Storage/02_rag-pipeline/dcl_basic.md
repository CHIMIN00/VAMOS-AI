# P1-9. DCL 기초 구현 (Data Control Layer) 상세 (V1)

> **세션**: P1-9 (2026-04-13)
> **산출물 버전**: v1.1
> **상태**: COMPLETE
> **LOCK 준수**: LOCK-MR-015 (Deny 벡터 삽입 금지), LOCK-MR-016 (L3 활성 게이트), LOCK-MR-017 (project_id 격리), LOCK-MR-018 (저장 전 사용자 확인)
> **정본**: D2.0-06 §3.2 (Allow/Restrict/Deny 정책), D2.0-07 (PolicyCheck Gate, ApprovalGate), Part2 V1-Phase 2 항목9
> **교차 참조**: P0-1 MemoryRecordSchema, P1-1 L0_session_memory_crud, P1-2 L1_project_memory_crud, P1-3 chroma_adapter, P1-4 json_graphrag, P1-5 semantic_cache, P1-6 export_import, P1-7 pii_masking, P1-8 B3_memory_decay
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D2.0-07 (Policy SOT) > Part2 V1-P2 (구현가이드) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수 상세**:
>   - LOCK-MR-015: Deny 판정 시 벡터 삽입 절대 금지, 모든 저장소 장기 저장 불가
>   - LOCK-MR-016: L3 저장/활성은 D7 ApprovalGate 필수
>   - LOCK-MR-017: project_id 기반 격리, 정책 판정도 프로젝트 범위 내
>   - LOCK-MR-018: 저장 전 사용자 확인이 기본 정책
>
> **입력 파일**:
>   - D2.0-06 §3.2 Allow/Restrict/Deny (계층별 최소 원칙)
>   - D2.0-07 §5 PolicyCheck Gate, §3.3 S-Module/E-Module 승인 규칙
>   - D2.0-07 5-Gate 파이프라인: PolicyGate -> ApprovalGate -> CostGate -> EvidenceGate -> SelfCheckGate
>   - Part2 V1-Phase 2 항목9 (DCL 기초 구현 — `storage/kb/dcl_collector.py`)
>   - P0-1: `MemoryRecordSchema.md` (policy_decision 필드: allow/restrict/deny)
>   - P1-1: `L0_session_memory_crud.md` (§5.2 UserConfirmationHook, §6.1 L0_ERR_006 deny 처리)
>   - P1-7: `pii_masking.md` (§6 DCL 연동 — P1-9 인터페이스 수용 준비 완료)
>
> **이전 단계 이월 사항**: P1-1~P1-8 모두 이월 없음. P1-7에서 "P1-9(DCL) 미완 — 인터페이스만 참조" 기록 — 본 문서에서 FULL 구현.

---

## 목차

1. [DCL 아키텍처 개요](#1-dcl-아키텍처-개요)
2. [PolicyDecision 열거형 및 데이터 클래스](#2-policydecision-열거형-및-데이터-클래스)
3. [DataControlLayer 클래스 설계](#3-datacontrollayer-클래스-설계)
4. [check_policy() 핵심 구현](#4-check_policy-핵심-구현)
5. [Allow 경로 상세](#5-allow-경로-상세)
6. [Restrict 경로 상세](#6-restrict-경로-상세)
7. [Deny 경로 상세](#7-deny-경로-상세)
8. [LOCK-MR-015 연동 — Deny 시 벡터 삽입 금지](#8-lock-mr-015-연동--deny-시-벡터-삽입-금지)
9. [LOCK-MR-016 연동 — L3 ApprovalGate 필수](#9-lock-mr-016-연동--l3-approvalgate-필수)
10. [LOCK-MR-018 연동 — 저장 전 사용자 확인 훅](#10-lock-mr-018-연동--저장-전-사용자-확인-훅)
11. [project_id 격리 (LOCK-MR-017)](#11-project_id-격리-lock-mr-017)
12. [에러 코드 정의](#12-에러-코드-정의)
13. [복구/재시도 전략](#13-복구재시도-전략)
14. [에스컬레이션 정책](#14-에스컬레이션-정책)
15. [로깅 규격 (R-01-7)](#15-로깅-규격-r-01-7)
16. [시간복잡도 분석 (Big-O)](#16-시간복잡도-분석-big-o)
17. [예외 처리 정책 표](#17-예외-처리-정책-표)
18. [단위 테스트 시나리오](#18-단위-테스트-시나리오)
19. [Phase 2 통합 테스트](#19-phase-2-통합-테스트)
20. [세션 간 인터페이스 cross-check](#20-세션-간-인터페이스-cross-check)
21. [LOCK-MR 참조 추적표](#21-lock-mr-참조-추적표)
22. [교차 참조 블록](#22-교차-참조-블록)

---

## 1. DCL 아키텍처 개요

### 1.1 역할 정의

> **DCL(Data Control Layer)**: 메모리 저장/조회 시 정책 판정을 중재하는 계층.
> 모든 메모리 CRUD 경로에서 저장소 접근 전 DCL을 통과하며, D7 PolicyCheck 결과를 기반으로 Allow/Restrict/Deny 판정을 반환한다.

```
                       ┌─────────────────────┐
                       │   클라이언트 요청     │
                       └─────────┬───────────┘
                                 │
                       ┌─────────▼───────────┐
                       │  MemoryRecord 구성   │
                       │  (P0-1 스키마)       │
                       └─────────┬───────────┘
                                 │
                  ┌──────────────▼──────────────┐
                  │   DCL: check_policy()        │
                  │   ┌───────────────────────┐  │
                  │   │ 1. D7 PolicyCheck 호출 │  │
                  │   │ 2. PII 민감도 교차판정  │  │
                  │   │ 3. L3 ApprovalGate 확인│  │
                  │   │ 4. 사용자 확인 훅      │  │
                  │   └───────────────────────┘  │
                  └──────────┬────────┬────┬─────┘
                    Allow    │ Restrict│    │ Deny
                  ┌──────────▼─┐  ┌───▼──┐ │ ┌────▼──────┐
                  │ 정상 저장   │  │마스킹 │ │ │ 저장 차단  │
                  │ + 벡터 삽입 │  │후 저장│ │ │ 벡터 금지  │
                  └────────────┘  └──────┘ │ │ 로그만 기록│
                                           │ └───────────┘
                                           │
                              (LOCK-MR-015: 벡터 삽입 절대 금지)
```

### 1.2 DCL 위치 (5-Gate 파이프라인 내)

> LOCK (D2.0-07): 5-Gate = PolicyGate -> ApprovalGate -> CostGate -> EvidenceGate -> SelfCheckGate

DCL은 **PolicyGate + ApprovalGate** 결과를 메모리 저장 맥락에 특화하여 적용하는 **어댑터 계층**이다. 5-Gate의 범용 판정을 메모리 도메인(6-4)의 Allow/Restrict/Deny로 변환한다.

| 5-Gate 판정 | DCL 매핑 | 근거 |
|------------|---------|------|
| PASS | Allow | D2.0-06 §3.2 — 정상 저장 |
| NEEDS_APPROVAL | Restrict | D2.0-06 §3.2 — 마스킹/승인 조건부 저장 |
| BLOCK | Deny | D2.0-06 §3.2 — 저장 금지 |
| ERROR | Deny (보수적) | D2.0-06 §3.2 — ERROR는 기본 BLOCK 처리 |

### 1.3 코드 위치

```
backend/vamos_core/storage/kb/dcl_collector.py      # Part2 지정 경로
backend/vamos_core/storage/kb/data_control_layer.py  # DCL 핵심 모듈
```

> **명칭 정합**: Part2 항목9는 "DCL 기초 구현"으로 `dcl_collector.py`를 지정. 본 문서는 DCL의 핵심 정책 판정 로직(`data_control_layer.py`)과 DCL 수집기(`dcl_collector.py` — DCL-FIN/DCL-TECH RSS 연동)를 모두 포함한다.
> - **data_control_layer.py**: Allow/Restrict/Deny 정책 판정 인터페이스 (본 문서의 주요 범위)
> - **dcl_collector.py**: DCL-FIN(RT-BNP RSS)/DCL-TECH(RSS 1시간 폴링) 수집기 (Part2 게이트 11 충족 — §1.4에서 요약)

### 1.4 DCL 수집기 (Part2 게이트 11 충족)

> Part2 V1-Phase 2 검증 체크리스트 #11: "DCL-FIN + DCL-TECH 수집 동작"

| 수집기 | 대상 | 폴링 주기 | RAG 연동 |
|-------|------|----------|---------|
| DCL-FIN | RT-BNP RSS (실시간 속보) | 60초 | I-2 RAG 파이프라인 자동 삽입 |
| DCL-TECH | 기술 RSS 피드 | 1시간 | I-2 RAG 파이프라인 자동 삽입 |

**수집 흐름**:
1. RSS 피드 폴링 -> 신규 항목 감지
2. MemoryRecord 구성 (scope=L1, memory_type=B-1 Episodic)
3. **DCL check_policy() 통과** (본 문서 §4)
4. Allow 시 -> RAG 파이프라인(P1-10) 삽입 -> Chroma 벡터 저장(P1-3)
5. Restrict 시 -> PII 마스킹(P1-7) 적용 후 저장
6. Deny 시 -> 저장 차단, 감사 로그만 기록

> **범위 주의**: DCL 수집기(DCL-FIN/DCL-TECH)의 RSS 파싱/폴링 상세는 Cloud Library Spec(E-15) 및 6-12 Event-Logging 도메인 범위. 본 문서는 수집된 데이터가 DCL 정책 판정을 거치는 경로에 집중한다.

---

## 2. PolicyDecision 열거형 및 데이터 클래스

### 2.1 PolicyDecision 열거형

```python
from enum import Enum

class PolicyDecision(str, Enum):
    """DCL 정책 판정 결과.
    
    정본: D2.0-06 §3.2 (Allow/Restrict/Deny)
    D7 매핑: PASS->allow, NEEDS_APPROVAL->restrict, BLOCK/ERROR->deny
    MemoryRecordSchema(P0-1) policy_decision 필드와 1:1 대응.
    """
    ALLOW = "allow"       # 정상 저장 허용
    RESTRICT = "restrict"  # 조건부 저장 (마스킹/승인/TTL 강제)
    DENY = "deny"          # 저장 완전 차단
```

### 2.2 PolicyCheckResult 데이터 클래스

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PolicyCheckResult:
    """DCL check_policy() 반환 타입."""
    
    # --- 필수 필드 ---
    decision: PolicyDecision           # 최종 판정
    record_id: str                     # 대상 MemoryRecord ID
    project_id: str                    # 프로젝트 ID (LOCK-MR-017)
    scope: str                         # L0|L1|L2|L3 (LOCK-MR-001)
    memory_type: str                   # B-1|B-2|B-3|B-4 (LOCK-MR-002)
    
    # --- 판정 상세 ---
    d7_gate_result: str = ""           # D7 PolicyCheck 원본 (PASS/BLOCK/NEEDS_APPROVAL/ERROR)
    pii_decision: str = ""             # PII 민감도 기반 판정 (P1-7 교차)
    final_reason: str = ""             # 판정 사유 (사람이 읽을 수 있는 설명)
    
    # --- 액션 지시 ---
    vector_insert_allowed: bool = True  # 벡터 삽입 허용 여부 (LOCK-MR-015)
    mask_required: bool = False         # 마스킹 필요 여부 (restrict 경로)
    approval_required: bool = False     # ApprovalGate 필요 여부 (LOCK-MR-016)
    user_confirmation_required: bool = True  # 사용자 확인 필요 여부 (LOCK-MR-018)
    ttl_forced: bool = False           # TTL 강제 적용 여부
    
    # --- 메타데이터 ---
    checked_at: str = ""               # ISO 8601 판정 시각
    trace_id: str = ""                 # 요청 추적 ID
    lock_checks: dict = field(default_factory=dict)  # LOCK 준수 검사 결과
    
    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.utcnow().isoformat() + "Z"
        # LOCK-MR-015 강제: deny 시 벡터 삽입 절대 금지
        if self.decision == PolicyDecision.DENY:
            self.vector_insert_allowed = False
```

### 2.3 DCLConfig 설정 클래스

```python
@dataclass
class DCLConfig:
    """DCL 설정. config.toml [storage.dcl] 섹션에서 로드.
    
    어댑터 교체 시 config 변경만으로 전환 가능 (D2.0-06 L184 제약 준수).
    """
    # D7 PolicyCheck 서비스 연결
    policy_check_enabled: bool = True           # D7 PolicyCheck 호출 활성화
    policy_check_timeout_ms: int = 3000         # D7 호출 타임아웃 (ms)
    policy_check_retry_count: int = 2           # D7 호출 재시도 횟수
    
    # PII 교차 판정
    pii_cross_check_enabled: bool = True        # PII 민감도 교차 판정 활성화
    
    # L3 ApprovalGate
    l3_approval_required: bool = True           # L3 레코드 ApprovalGate 필수 (LOCK-MR-016)
    
    # 사용자 확인
    user_confirmation_default: bool = True      # 저장 전 사용자 확인 기본값 (LOCK-MR-018)
    auto_confirm_ttl_expiry: bool = True        # TTL 만료 삭제는 자동 확인
    auto_confirm_session_summary: bool = True   # 세션 종료 요약은 자동 확인
    
    # ERROR 처리 정책
    error_default_decision: str = "deny"        # D7 호출 실패 시 기본 판정 (보수적)
    
    # DCL-FIN / DCL-TECH 수집기 설정
    dcl_fin_enabled: bool = True                # DCL-FIN(RT-BNP RSS) 활성화
    dcl_fin_poll_interval_sec: int = 60         # DCL-FIN 폴링 주기 (초)
    dcl_tech_enabled: bool = True               # DCL-TECH 활성화
    dcl_tech_poll_interval_sec: int = 3600      # DCL-TECH 폴링 주기 (초)
```

---

## 3. DataControlLayer 클래스 설계

### 3.1 클래스 계층

```
DataControlLayer
  ├── __init__(config: DCLConfig, policy_checker: D7PolicyChecker, pii_masker: PIIMasker)
  ├── check_policy(record: MemoryRecord) -> PolicyCheckResult
  ├── enforce_policy(record: MemoryRecord, result: PolicyCheckResult) -> EnforcementResult
  ├── _call_d7_policy_check(record: MemoryRecord) -> str
  ├── _cross_check_pii(record: MemoryRecord, d7_result: str) -> PolicyDecision
  ├── _check_l3_approval(record: MemoryRecord) -> bool
  ├── _check_user_confirmation(record: MemoryRecord, action: str) -> bool
  ├── _enforce_project_filter(project_id: str) -> None
  ├── _build_lock_checks(record, decision) -> dict
  └── _log_policy_event(event_type: str, payload: dict) -> None
```

### 3.2 의존성 주입 구조

```python
class DataControlLayer:
    """Data Control Layer — 메모리 저장/조회 정책 판정 중재 계층.
    
    정본: D2.0-06 §3 (저장 정책), D2.0-07 (5-Gate PolicyCheck)
    LOCK: MR-015 (Deny 벡터 금지), MR-016 (L3 ApprovalGate), MR-018 (저장 전 확인)
    
    위치: backend/vamos_core/storage/kb/data_control_layer.py
    """
    
    def __init__(
        self,
        config: DCLConfig,
        policy_checker,     # D7PolicyChecker — 5-Gate PolicyCheck 서비스
        pii_masker=None,    # PIIMasker(P1-7) — PII 교차 판정용 (optional)
        confirmation_hook=None,  # UserConfirmationHook(P1-1 §5.2) — 사용자 확인
        logger=None         # 감사 로그 (R-01-7, 6-12 Event-Logging)
    ):
        self._config = config
        self._policy_checker = policy_checker
        self._pii_masker = pii_masker
        self._confirmation_hook = confirmation_hook
        self._logger = logger or self._default_logger()
```

---

## 4. check_policy() 핵심 구현

### 4.1 판정 흐름

```python
def check_policy(self, record) -> PolicyCheckResult:
    """메모리 레코드에 대한 정책 판정 수행.
    
    흐름:
    1. project_id 격리 검증 (LOCK-MR-017)
    2. D7 PolicyCheck 호출 (5-Gate 결과 수신)
    3. PII 민감도 교차 판정 (P1-7 연동)
    4. L3 ApprovalGate 확인 (LOCK-MR-016)
    5. 최종 판정 산출 (엄격한 쪽 채택)
    6. LOCK 준수 검사 (MR-015/016/017/018)
    7. 감사 로그 기록
    
    Returns:
        PolicyCheckResult — 판정 결과 + 액션 지시
    
    Raises:
        DCL_ERR_001: project_id 누락
        DCL_ERR_002: D7 PolicyCheck 호출 실패 (재시도 후)
    """
    # Step 1: project_id 격리 (LOCK-MR-017)
    self._enforce_project_filter(record.project_id)
    
    # Step 2: D7 PolicyCheck 호출
    d7_result = self._call_d7_policy_check(record)
    # d7_result: "PASS" | "NEEDS_APPROVAL" | "BLOCK" | "ERROR"
    
    # Step 3: PII 교차 판정 (P1-7 PIIMasker 연동)
    combined_decision = self._cross_check_pii(record, d7_result)
    # combined_decision: PolicyDecision (allow/restrict/deny)
    
    # Step 4: L3 ApprovalGate 확인 (LOCK-MR-016)
    approval_required = False
    if record.scope == "L3" and self._config.l3_approval_required:
        approval_granted = self._check_l3_approval(record)
        if not approval_granted:
            # L3는 ApprovalGate 미통과 시 restrict 이상으로 승격
            if combined_decision == PolicyDecision.ALLOW:
                combined_decision = PolicyDecision.RESTRICT
            approval_required = True
    
    # Step 5: LOCK 준수 검사
    lock_checks = self._build_lock_checks(record, combined_decision)
    
    # Step 6: 판정 결과 구성
    result = PolicyCheckResult(
        decision=combined_decision,
        record_id=record.record_id,
        project_id=record.project_id,
        scope=record.scope,
        memory_type=record.memory_type,
        d7_gate_result=d7_result,
        pii_decision=self._get_pii_decision_str(record),
        final_reason=self._build_reason(d7_result, combined_decision, record),
        vector_insert_allowed=(combined_decision != PolicyDecision.DENY),
        mask_required=(combined_decision == PolicyDecision.RESTRICT),
        approval_required=approval_required,
        user_confirmation_required=self._needs_user_confirmation(record, combined_decision),
        ttl_forced=(combined_decision == PolicyDecision.RESTRICT),
        lock_checks=lock_checks,
    )
    
    # LOCK-MR-015 강제 (post_init에서도 적용, 이중 안전)
    if result.decision == PolicyDecision.DENY:
        result.vector_insert_allowed = False
    
    # LOCK-MR-015 벡터 가드 이중 검증 (§8.2) — 모든 정책 판정에 강제 통합
    self.enforce_vector_guard(record, result)

    # LOCK-MR-015 벡터 가드 이중 검증 (§8.2) — 모든 정책 판정에 강제 통합
    self.enforce_vector_guard(record, result)

    # Step 7: 감사 로그
    self._log_policy_event("storage.dcl.policy_checked", {
        "record_id": record.record_id,
        "project_id": record.project_id,
        "scope": record.scope,
        "memory_type": record.memory_type,
        "d7_result": d7_result,
        "pii_decision": result.pii_decision,
        "final_decision": result.decision.value,
        "vector_insert_allowed": result.vector_insert_allowed,
        "approval_required": result.approval_required,
        "lock_checks": lock_checks,
    })
    
    return result
```

### 4.2 D7 PolicyCheck 호출

```python
def _call_d7_policy_check(self, record) -> str:
    """D7 PolicyCheck Gate 호출.
    
    5-Gate 파이프라인(D2.0-07): PolicyGate -> ApprovalGate -> CostGate -> ...
    
    Returns:
        "PASS" | "NEEDS_APPROVAL" | "BLOCK" | "ERROR"
    """
    if not self._config.policy_check_enabled:
        # SECURITY: 게이트 비활성 — 운영 환경에서 모든 콘텐츠 무검증 저장 위험. 매 우회마다 CRITICAL 경보.
        self._logger.warning({"event": "storage.dcl.policy_check_bypassed", "severity": "CRITICAL",
                              "detail": "policy_check_enabled=False — D7 PolicyCheck 우회 (개발/테스트 전용, 운영 금지)"})
        return "PASS"  # 비활성 시 기본 허용 (개발/테스트 환경 전용)
    
    retry_count = self._config.policy_check_retry_count
    timeout_ms = self._config.policy_check_timeout_ms
    
    for attempt in range(retry_count + 1):
        try:
            result = self._policy_checker.check(
                record_id=record.record_id,
                project_id=record.project_id,
                scope=record.scope,
                memory_type=record.memory_type,
                content_summary=record.content_summary,
                timeout_ms=timeout_ms,
            )
            return result  # "PASS" | "NEEDS_APPROVAL" | "BLOCK" | "ERROR"
        except TimeoutError:
            self._log_policy_event("storage.dcl.d7_timeout", {
                "record_id": record.record_id,
                "attempt": attempt + 1,
                "timeout_ms": timeout_ms,
            })
            if attempt == retry_count:
                # 재시도 소진: 보수적 처리 (BLOCK)
                return self._config.error_default_decision.upper()
        except Exception as e:
            self._log_policy_event("storage.dcl.d7_error", {
                "record_id": record.record_id,
                "attempt": attempt + 1,
                "error": str(e),
            })
            if attempt == retry_count:
                return self._config.error_default_decision.upper()
    
    return "ERROR"
```

### 4.3 PII 교차 판정

```python
def _cross_check_pii(self, record, d7_result: str) -> PolicyDecision:
    """D7 결과와 PII 민감도를 교차 판정. 엄격한 쪽 채택.
    
    연동: P1-7 pii_masking.md §6 DCL 연동
    
    교차 규칙 (D2.0-06 §3.2):
    - deny가 하나라도 있으면 -> deny
    - restrict가 하나라도 있으면 -> restrict
    - 모두 allow이면 -> allow
    """
    # D7 -> DCL 변환
    d7_to_dcl = {
        "PASS": PolicyDecision.ALLOW,
        "NEEDS_APPROVAL": PolicyDecision.RESTRICT,
        "BLOCK": PolicyDecision.DENY,
        "ERROR": PolicyDecision.DENY,  # 보수적 처리
    }
    d7_decision = d7_to_dcl.get(d7_result, PolicyDecision.DENY)
    
    # PII 교차 판정
    if self._config.pii_cross_check_enabled and self._pii_masker is not None:
        pii_result = self._pii_masker.apply_to_record(record, policy_decision=None)
        pii_decision_str = pii_result.policy_decision
        pii_decision = PolicyDecision(pii_decision_str)
    else:
        pii_decision = PolicyDecision.ALLOW
    
    # 엄격한 쪽 채택
    decisions = [d7_decision, pii_decision]
    if PolicyDecision.DENY in decisions:
        return PolicyDecision.DENY
    elif PolicyDecision.RESTRICT in decisions:
        return PolicyDecision.RESTRICT
    else:
        return PolicyDecision.ALLOW
```

---

## 5. Allow 경로 상세

### 5.1 Allow 판정 조건

| 조건 | 설명 | 근거 |
|------|------|------|
| D7 = PASS | PolicyCheck 통과 | D2.0-07 |
| PII = PUBLIC 또는 INTERNAL | 민감정보 없음/내부용 | D2.0-06 §3.2 |
| scope != L3 또는 L3 + approval_granted | L3는 ApprovalGate 필수 | LOCK-MR-016 |

### 5.2 Allow 시 동작

```python
# Allow 경로
if result.decision == PolicyDecision.ALLOW:
    # 1. 벡터 삽입 허용
    result.vector_insert_allowed = True
    
    # 2. 마스킹 불필요
    result.mask_required = False
    
    # 3. 정상 저장 진행
    # L0/L1/L2: 요약/결과만 저장 (LOCK-MR-019 준수)
    # L3(B-2): allow라도 자동 활성(active) 금지 (D2.0-06 §3.2)
    #   -> activation_state = "draft" 유지
    
    # 4. 사용자 확인 (LOCK-MR-018)
    #   -> 기본 필요. 자동 확인 예외는 §10.3 참조
```

### 5.3 L3 Allow 특수 처리

> LOCK (D2.0-06 §3.2): L3(B-2)는 allow라도 **자동 활성(active) 금지**. 활성은 §2.3.3 게이트(D7 ApprovalGate)를 만족해야 함.

```python
def _enforce_l3_activation_guard(self, record, result):
    """L3 레코드의 Allow 판정이라도 activation_state를 draft으로 강제."""
    if record.scope == "L3" and result.decision == PolicyDecision.ALLOW:
        # L3는 allow여도 자동 active 불가
        # activation_state는 draft -> approved -> active 순서 필수
        # approved/active 전환은 D7 ApprovalGate 경유 (LOCK-MR-016)
        pass  # record.activation_state = "draft" (변경하지 않음)
```

---

## 6. Restrict 경로 상세

### 6.1 Restrict 판정 조건

| 조건 | 설명 | 근거 |
|------|------|------|
| D7 = NEEDS_APPROVAL | 승인 필요 | D2.0-07 |
| PII = CONFIDENTIAL | 비밀 등급 PII 포함 | D2.0-06 §3.2 + P1-7 §5 |
| scope = L3 + approval 미완료 | L3 승인 대기 | LOCK-MR-016 |

### 6.2 Restrict 시 동작

> 정본 (D2.0-06 §3.2): 옵션 B — 마스킹 후 저장 허용 + TTL 기본

```python
# Restrict 경로
if result.decision == PolicyDecision.RESTRICT:
    # 1. 마스킹 필수 -> P1-7 PIIMasker 호출
    result.mask_required = True
    
    # 2. 벡터 삽입: 민감도에 따라 결정
    #    CONFIDENTIAL: 마스킹 후 허용 (D2.0-06 §3.2)
    #    SECRET: 절대 금지 (LOCK-MR-015 — deny 승격 경로)
    
    # 3. TTL 강제 적용
    result.ttl_forced = True
    
    # 4. 사용자 확인 필수 (LOCK-MR-018)
    result.user_confirmation_required = True
    
    # 5. L3(B-2): 저장(write) 또는 활성(active) 중 최소 1개에 D7 ApprovalGate 필수
    #    (D2.0-06 §3.2 Restrict L3 규칙)
```

### 6.3 마스킹 불완전 시 처리

> 정본 (D2.0-06 §3.2): 마스킹이 불완전하거나 민감도가 높으면 "승인 없이는 저장 금지(deny 또는 보류)"

```python
def _handle_incomplete_masking(self, record, pii_result):
    """마스킹 불완전 시 deny 승격 또는 에스컬레이션."""
    if not pii_result.masking_complete:
        if pii_result.sensitivity_level.value >= SensitivityLevel.CONFIDENTIAL.value:
            # 고민감 + 마스킹 불완전 -> deny 승격
            return PolicyDecision.DENY
        else:
            # 저민감 + 마스킹 불완전 -> 에스컬레이션
            self._escalate("DCL_ESC_003", record, "마스킹 불완전 — 수동 검토 필요")
            return PolicyDecision.RESTRICT  # 유지, 에스컬레이션 병행
```

---

## 7. Deny 경로 상세

### 7.1 Deny 판정 조건

| 조건 | 설명 | 근거 |
|------|------|------|
| D7 = BLOCK | PolicyCheck 차단 | D2.0-07 |
| D7 = ERROR | 서비스 오류 (보수적 처리) | D2.0-06 §3.2 |
| PII = SECRET | 극비 등급 | P1-7 §5 |
| 마스킹 불완전 + 고민감 | Restrict에서 승격 | D2.0-06 §3.2 |

### 7.2 Deny 시 동작 (체크리스트)

> LOCK (D2.0-06 §3.2 Deny):
> - 모든 레벨(L0~L3): 정책 위반 시 저장 불가
> - 어떤 저장소에도 "장기 저장" 불가
> - **벡터 삽입 절대 금지** (RAG/임베딩 금지) — LOCK-MR-015
> - 로그/트레이스에도 원문 저장 금지 (필요 시 요약/힌트만)

```python
# Deny 경로
if result.decision == PolicyDecision.DENY:
    # 1. 벡터 삽입 절대 금지 (LOCK-MR-015)
    result.vector_insert_allowed = False
    
    # 2. 모든 저장소 장기 저장 불가
    #    SQLite: INSERT/UPDATE 차단
    #    Chroma: upsert() 차단 (P1-3 §4.1 Step 1)
    #    GraphRAG: add_node()/add_edge() 차단 (P1-4)
    #    Semantic Cache: 캐시 저장 차단 (P1-5)
    
    # 3. 감사 로그에 요약/힌트만 기록 (원문 금지)
    self._log_policy_event("storage.dcl.deny_blocked", {
        "record_id": record.record_id,
        "project_id": record.project_id,
        "scope": record.scope,
        "reason": result.final_reason,
        # content_summary 대신 해시만 기록
        "content_hash": hashlib.sha256(
            (record.content_summary or "").encode()
        ).hexdigest()[:16],
    })
    
    # 4. 사용자 확인 불필요 (차단이므로)
    result.user_confirmation_required = False
```

---

## 8. LOCK-MR-015 연동 -- Deny 시 벡터 삽입 금지

> **LOCK-MR-015** (D2.0-06 §3.2): Deny 판정 시 벡터 삽입 절대 금지

### 8.1 연동 경로

```
DCL check_policy() -> PolicyCheckResult.vector_insert_allowed = False
    │
    ├── P1-3 ChromaVectorStore.upsert()
    │   └── Step 1: policy_decision 검사 -> deny 시 ValueError 발생
    │       (산출물: chroma_adapter.md §4.1)
    │
    ├── P1-4 JsonGraphStore.add_node()/add_edge()
    │   └── policy_decision=deny 시 삽입 거부
    │
    └── P1-5 SemanticCache.cache_response()
        └── policy_decision=deny 시 캐시 저장 거부
```

### 8.2 이중 안전장치

```python
def enforce_vector_guard(self, record, result: PolicyCheckResult):
    """벡터 삽입 전 LOCK-MR-015 이중 검증.
    
    DCL 판정 결과와 MemoryRecord.policy_decision 양쪽 확인.
    """
    # Guard 1: DCL 판정 결과
    if not result.vector_insert_allowed:
        raise PolicyViolationError(
            code="DCL_ERR_006",
            message=f"벡터 삽입 금지 (LOCK-MR-015): record={record.record_id}, "
                    f"decision={result.decision.value}",
        )
    
    # Guard 2: MemoryRecord.policy_decision 필드 직접 확인
    if getattr(record, "policy_decision", None) == "deny":
        raise PolicyViolationError(
            code="DCL_ERR_006",
            message=f"벡터 삽입 금지 (LOCK-MR-015, record-level): "
                    f"record={record.record_id}",
        )
```

---

## 9. LOCK-MR-016 연동 -- L3 ApprovalGate 필수

> **LOCK-MR-016** (D2.0-06 §2.3): L3 저장/활성은 D7 ApprovalGate 필수

### 9.1 L3 ApprovalGate 흐름

```python
def _check_l3_approval(self, record) -> bool:
    """L3 레코드의 ApprovalGate 확인.
    
    D7 ApprovalGate 호출:
    - activation_state=draft -> 저장 허용 (draft 상태)
    - activation_state=approved -> D7 ApprovalGate 통과 필수
    - activation_state=active -> D7 ApprovalGate 통과 + 3회 수동 실행 이력 필수 (V2)
    
    V1 정책 (D2.0-06 §2.3.2):
    - L3 저장은 draft 상태로만 허용
    - approved/active 전환은 D7 ApprovalGate 결과에 따름
    """
    if record.scope != "L3":
        return True  # L3가 아니면 항상 통과
    
    # V1: draft 저장은 허용, 활성 전환은 ApprovalGate 필수
    activation = getattr(record, "activation_state", "draft")
    
    if activation == "draft":
        # draft 상태 저장: ApprovalGate 불필요 (단, 사용자 확인은 필요)
        return True
    
    if activation in ("approved", "active"):
        # approved/active 전환: D7 ApprovalGate 호출
        try:
            approval_result = self._policy_checker.check_approval(
                record_id=record.record_id,
                project_id=record.project_id,
                scope="L3",
                activation_state=activation,
            )
            return approval_result == "APPROVED"
        except Exception as e:
            self._log_policy_event("storage.dcl.l3_approval_error", {
                "record_id": record.record_id,
                "error": str(e),
            })
            return False  # 오류 시 보수적 처리 (미승인)
    
    return False  # 알 수 없는 상태
```

### 9.2 L3 접근 제어

> LOCK (D2.0-06 §2.4): L3 읽기는 L1 이상 접근 권한 필요, L3 쓰기는 D7 ApprovalGate 필수

| 작업 | 권한 요구 | DCL 처리 |
|------|----------|---------|
| L3 읽기 | L1 이상 접근 권한 | RBAC 검증 (6-2 Security 도메인 연동) |
| L3 쓰기 (draft) | 사용자 확인 | LOCK-MR-018 훅 |
| L3 쓰기 (approved) | D7 ApprovalGate | LOCK-MR-016 게이트 |
| L3 쓰기 (active) | D7 ApprovalGate + 3회 수동 실행 (V2) | V1에서는 ApprovalGate만 |

---

## 10. LOCK-MR-018 연동 -- 저장 전 사용자 확인 훅

> **LOCK-MR-018** (RULE 1.3 §7.3): 저장 전 사용자 확인이 기본

### 10.1 확인 훅 통합

```python
def _check_user_confirmation(self, record, action: str) -> bool:
    """저장 전 사용자 확인 훅 호출.
    
    P1-1 §5.2 UserConfirmationHook 인터페이스 재사용.
    
    Args:
        record: MemoryRecord
        action: "CREATE" | "UPDATE" | "DELETE" | "L1_CREATE" 등
    
    Returns:
        True=확인됨, False=취소됨
    
    Note:
        - deny 판정은 확인 불필요 (차단이므로)
        - TTL 만료 삭제는 자동 확인 (config.auto_confirm_ttl_expiry)
        - 세션 종료 요약은 자동 확인 (config.auto_confirm_session_summary)
    """
    if self._confirmation_hook is None:
        # 확인 훅 미등록: LOCK-MR-018 fail-closed — 기본 거부 (자동 확인 예외 §10.3는 호출부에서 별도 처리)
        self._logger.warning({"event": "storage.dcl.confirmation_hook_unregistered", "severity": "WARN",
                              "detail": "_confirmation_hook=None — LOCK-MR-018 fail-closed deny"})
        return False
    
    # 자동 확인 예외 체크
    if self._is_auto_confirmable(record, action):
        return True
    
    # P1-1 §5.2 UserConfirmationHook 호출
    confirmed = self._confirmation_hook.request_confirmation(
        project_id=record.project_id,
        action=action,
        content_preview=self._truncate_preview(record.content_summary, max_len=200),
        metadata={
            "scope": record.scope,
            "memory_type": record.memory_type,
            "record_id": record.record_id,
        },
    )
    
    self._log_policy_event("storage.dcl.user_confirmation", {
        "record_id": record.record_id,
        "project_id": record.project_id,
        "action": action,
        "confirmed": confirmed,
    })
    
    return confirmed
```

### 10.2 DCL-사용자 확인 통합 시퀀스

```
사용자 요청 -> MemoryRecord 구성
    -> DCL.check_policy() [정책 판정]
        -> Allow/Restrict 판정
            -> UserConfirmationHook.request_confirmation()
                -> 6-1 UI: 확인 모달 표시
                    -> 사용자 확인/취소
                        -> confirmed=True: 저장 진행
                        -> confirmed=False: 저장 중단 + 감사 로그
        -> Deny 판정
            -> 확인 불필요, 즉시 차단
```

### 10.3 자동 확인 예외 (V1)

| 시나리오 | 자동 확인 | 근거 |
|----------|----------|------|
| 세션 종료 시 자동 요약 저장 (L0->L1 승격 전처리) | 허용 | 세션 시작 시 일괄 동의 (P1-1 §5.3) |
| TTL 만료 삭제 | 허용 | 시스템 정책 (LOCK-MR-003) |
| API 호출 시 명시적 `user_confirmed=True` | 허용 | 클라이언트 책임 |
| DCL-FIN/DCL-TECH 자동 수집 | 허용 | 초기 설정 시 일괄 동의 전제 |

---

## 11. project_id 격리 (LOCK-MR-017)

> **LOCK-MR-017** (D2.0-06 §1 / RULE 1.3 §7.2): 프로젝트 간 데이터 혼합 금지

```python
def _enforce_project_filter(self, project_id: str) -> None:
    """project_id 필수 검증 가드.
    
    P1-1 §3.1 Step 2, P1-2 §3.1 Step 2, P1-3 §4.1 Step 0 동일 패턴.
    """
    if not project_id or not project_id.strip():
        raise PolicyViolationError(
            code="DCL_ERR_001",
            message="project_id 누락 (LOCK-MR-017): 프로젝트 식별자 필수",
        )
```

---

## 12. 에러 코드 정의

| error_code | 설명 | recoverable | 처리 |
|------------|------|-------------|------|
| `DCL_ERR_001` | project_id 누락 (LOCK-MR-017) | Yes | 클라이언트에 project_id 재요청 |
| `DCL_ERR_002` | D7 PolicyCheck 호출 실패 (재시도 소진) | Yes | 에스컬레이션 + 보수적 deny |
| `DCL_ERR_003` | D7 PolicyCheck 타임아웃 | Yes | 재시도 2회 -> 에스컬레이션 |
| `DCL_ERR_004` | PII 교차 판정 실패 | Yes | PII 교차 판정 비활성화, D7 결과만 사용 |
| `DCL_ERR_005` | L3 ApprovalGate 호출 실패 | Yes | 보수적 미승인 처리 |
| `DCL_ERR_006` | 벡터 삽입 금지 위반 시도 (LOCK-MR-015) | No | 즉시 차단 + 감사 로그 + 에스컬레이션 |
| `DCL_ERR_007` | 사용자 확인 미완료 (LOCK-MR-018) | Yes | 확인 훅 재실행 |
| `DCL_ERR_008` | L3 activation_state 무효 값 | Yes | draft로 초기화 후 재판정 |
| `DCL_ERR_009` | 정책 판정 내부 오류 | Yes | 보수적 deny + 에스컬레이션 |
| `DCL_ERR_010` | UserConfirmationHook 미등록 | Yes | 기본 정책 적용 (config 참조) |
| `DCL_ERR_011` | 마스킹 불완전 + 고민감 (deny 승격) | No | deny 승격 + 감사 로그 |
| `DCL_ERR_012` | DCL-FIN/DCL-TECH 수집 오류 | Yes | 다음 폴링 주기에 재시도 |

---

## 13. 복구/재시도 전략

### 13.1 재시도 정책

| 에러 | 최대 재시도 | 간격 | 실패 시 동작 |
|------|-----------|------|------------|
| D7 PolicyCheck 타임아웃 | 2회 | 500ms 지수 백오프 | deny (보수적) + 에스컬레이션 |
| D7 PolicyCheck 오류 | 2회 | 500ms 지수 백오프 | deny (보수적) + 에스컬레이션 |
| UserConfirmationHook 오류 | 1회 | 즉시 | deny + 에스컬레이션 |
| L3 ApprovalGate 오류 | 1회 | 즉시 | 미승인 (보수적) |

### 13.2 복구 경로

| 시나리오 | 복구 방법 |
|----------|----------|
| D7 서비스 일시 장애 | 자동 재시도 -> 실패 시 deny + 큐에 재판정 요청 적재 |
| PII 탐지 엔진 오류 | PII 교차 판정 비활성화, D7 결과만 사용 |
| 확인 훅 타임아웃 | 기본 정책 적용 (V1: 확인 처리) |
| deny 판정 후 사용자 이의 | 수동 재판정 트리거 (config 변경 또는 관리자 오버라이드) |

---

## 14. 에스컬레이션 정책

### 14.1 에스컬레이션 페이로드

```python
@dataclass
class EscalationPayload:
    """에스컬레이션 페이로드 구조.
    
    P1-1 §6.2 EscalationPayload와 동일 구조.
    P1-4 §11, P1-5 §12, P1-6 §12, P1-7 §12, P1-8 §6.4 정합.
    """
    escalation_id: str          # 고유 ID
    trace_id: str               # 원본 요청 추적 ID
    source_domain: str = "6-4"  # 발생 도메인
    source_module: str = "data_control_layer"
    error_code: str = ""        # DCL_ERR_XXX
    error_message: str = ""
    severity: str = "HIGH"      # LOW | MEDIUM | HIGH | CRITICAL
    context: dict = field(default_factory=dict)
    timestamp: str = ""         # ISO 8601
    recommended_action: str = ""
```

### 14.2 에스컬레이션 트리거

| ID | 조건 | 심각도 | 권고 조치 |
|----|------|--------|---------|
| DCL_ESC_001 | D7 PolicyCheck 재시도 소진 | HIGH | D7 서비스 상태 확인 |
| DCL_ESC_002 | LOCK-MR-015 벡터 삽입 금지 위반 시도 | CRITICAL | 보안 감사 + 위반 경로 차단 |
| DCL_ESC_003 | 마스킹 불완전 + 고민감 | HIGH | 수동 마스킹 검토 |
| DCL_ESC_004 | L3 ApprovalGate 반복 실패 | MEDIUM | ApprovalGate 서비스 확인 |
| DCL_ESC_005 | DCL-FIN/DCL-TECH 수집 반복 실패 (3회+) | MEDIUM | RSS 피드 URL/네트워크 확인 |

### 14.3 에스컬레이션 레벨 매트릭스

| 심각도 | 자동 처리 | 알림 대상 | 응답 SLA |
|--------|----------|---------|---------|
| LOW | deny 후 자동 복구 시도 | 로그만 | 24시간 |
| MEDIUM | deny 후 큐 적재 | 시스템 관리자 | 4시간 |
| HIGH | 즉시 deny + 감사 로그 | OWNER | 1시간 |
| CRITICAL | 즉시 deny + 전체 경로 차단 | OWNER + 보안 | 즉시 |

---

## 15. 로깅 규격 (R-01-7)

### 15.1 이벤트 타입

| event_type | 발생 시점 | 필수 필드 |
|------------|----------|----------|
| `storage.dcl.policy_checked` | check_policy() 완료 | record_id, project_id, scope, decision, lock_checks |
| `storage.dcl.deny_blocked` | deny 판정으로 저장 차단 | record_id, project_id, reason, content_hash |
| `storage.dcl.vector_guard_violated` | 벡터 삽입 금지 위반 시도 | record_id, violation_detail |
| `storage.dcl.d7_timeout` | D7 호출 타임아웃 | record_id, attempt, timeout_ms |
| `storage.dcl.d7_error` | D7 호출 오류 | record_id, attempt, error |
| `storage.dcl.l3_approval_checked` | L3 ApprovalGate 결과 | record_id, activation_state, approved |
| `storage.dcl.l3_approval_error` | L3 ApprovalGate 오류 | record_id, error |
| `storage.dcl.user_confirmation` | 사용자 확인 결과 | record_id, project_id, action, confirmed |
| `storage.dcl.restrict_masked` | Restrict 경로 마스킹 완료 | record_id, masking_complete |
| `storage.dcl.escalation` | 에스컬레이션 발생 | escalation_id, error_code, severity |

### 15.2 로그 구조 (R-01-7 준수)

```json
{
    "timestamp": "2026-04-13T10:30:00.000Z",
    "level": "INFO",
    "event_type": "storage.dcl.policy_checked",
    "source": {
        "domain": "6-4",
        "module": "data_control_layer",
        "method": "check_policy"
    },
    "payload": {
        "record_id": "rec_abc123",
        "project_id": "proj_001",
        "scope": "L1",
        "memory_type": "B-1",
        "d7_result": "PASS",
        "pii_decision": "allow",
        "final_decision": "allow",
        "vector_insert_allowed": true,
        "approval_required": false,
        "lock_checks": {
            "MR-015": "PASS",
            "MR-016": "N/A",
            "MR-017": "PASS",
            "MR-018": "PASS"
        }
    },
    "trace_id": "trace_xyz789"
}
```

---

## 16. 시간복잡도 분석 (Big-O)

| 연산 | 복잡도 | 설명 |
|------|--------|------|
| check_policy() | O(1) + O(D7) + O(PII) | D7 호출(네트워크) + PII 탐지(P1-7: O(n*p), n=텍스트 길이, p=패턴 수) |
| D7 PolicyCheck 호출 | O(1) | 네트워크 호출 (타임아웃 3초) |
| PII 교차 판정 | O(n*p) | P1-7 PIIMasker.apply_to_record() 위임 |
| L3 ApprovalGate 확인 | O(1) | 네트워크 호출 |
| 사용자 확인 훅 | O(1) + 대기 | 비동기 — 사용자 응답 대기 |
| project_id 검증 | O(1) | 문자열 null/empty 체크 |
| LOCK 준수 검사 | O(1) | 4개 LOCK 항목 순차 확인 |

---

## 17. 예외 처리 정책 표

| 예외 | 기본 동작 | 사용자 표시 | 로그 수준 |
|------|----------|-----------|----------|
| project_id 누락 | deny | "프로젝트를 선택해주세요" | WARN |
| D7 서비스 불가 | deny (보수적) | "정책 서비스 일시 불가, 나중에 다시 시도하세요" | ERROR |
| PII 탐지 오류 | D7 결과만 사용 | (투명 — 사용자 미노출) | WARN |
| L3 승인 거부 | restrict | "L3 저장에 승인이 필요합니다" | INFO |
| 사용자 확인 취소 | 저장 중단 | "저장이 취소되었습니다" | INFO |
| 벡터 삽입 금지 위반 | 즉시 차단 | "보안 정책에 의해 저장이 차단되었습니다" | CRITICAL |
| 마스킹 불완전 | deny 승격 또는 에스컬레이션 | "민감 정보 처리 중 오류 — 저장이 보류됩니다" | ERROR |

---

## 18. 단위 테스트 시나리오

### 18.1 3개 경로 기본 테스트

| ID | 테스트 | 입력 | 기대 결과 | LOCK |
|----|--------|------|----------|------|
| T-DCL-01 | Allow 정상 경로 | D7=PASS, PII=PUBLIC, scope=L1 | decision=allow, vector=True | — |
| T-DCL-02 | Restrict 경로 | D7=NEEDS_APPROVAL, scope=L1 | decision=restrict, mask=True | — |
| T-DCL-03 | Deny 경로 (D7 BLOCK) | D7=BLOCK, scope=L0 | decision=deny, vector=False | MR-015 |
| T-DCL-04 | Deny 경로 (PII SECRET) | D7=PASS, PII=SECRET | decision=deny, vector=False | MR-015 |
| T-DCL-05 | Deny 경로 (D7 ERROR) | D7=ERROR | decision=deny, vector=False | MR-015 |

### 18.2 LOCK-MR-015 테스트

| ID | 테스트 | 입력 | 기대 결과 | LOCK |
|----|--------|------|----------|------|
| T-DCL-06 | Deny 시 벡터 삽입 금지 | decision=deny -> upsert 시도 | PolicyViolationError | MR-015 |
| T-DCL-07 | Deny 시 vector_insert_allowed 강제 False | decision=deny | vector_insert_allowed=False | MR-015 |
| T-DCL-08 | Allow 시 벡터 삽입 허용 | decision=allow | vector_insert_allowed=True | MR-015 |
| T-DCL-09 | Restrict + CONFIDENTIAL 벡터 허용 | decision=restrict, PII=CONFIDENTIAL | vector_insert_allowed=True (마스킹 후) | MR-015 |

### 18.3 LOCK-MR-016 테스트

| ID | 테스트 | 입력 | 기대 결과 | LOCK |
|----|--------|------|----------|------|
| T-DCL-10 | L3 draft 저장 허용 | scope=L3, activation=draft | decision=allow (ApprovalGate 불필요) | MR-016 |
| T-DCL-11 | L3 approved + 승인 통과 | scope=L3, activation=approved, approval=APPROVED | decision=allow | MR-016 |
| T-DCL-12 | L3 approved + 승인 미통과 | scope=L3, activation=approved, approval=DENIED | decision=restrict | MR-016 |
| T-DCL-13 | L3 active + 승인 미통과 | scope=L3, activation=active, approval=DENIED | decision=restrict | MR-016 |
| T-DCL-14 | L0/L1/L2 ApprovalGate 불필요 | scope=L1, activation=active | approval_required=False | MR-016 |

### 18.4 LOCK-MR-018 테스트

| ID | 테스트 | 입력 | 기대 결과 | LOCK |
|----|--------|------|----------|------|
| T-DCL-15 | 사용자 확인 성공 | action=CREATE, confirmed=True | 저장 진행 | MR-018 |
| T-DCL-16 | 사용자 확인 취소 | action=CREATE, confirmed=False | 저장 중단 | MR-018 |
| T-DCL-17 | TTL 만료 자동 확인 | action=TTL_EXPIRE | auto_confirm=True | MR-018 |
| T-DCL-18 | 세션 종료 자동 확인 | action=SESSION_SUMMARY | auto_confirm=True | MR-018 |
| T-DCL-19 | Deny 시 확인 불필요 | decision=deny | user_confirmation_required=False | MR-018 |

### 18.5 교차 판정 테스트

| ID | 테스트 | D7 결과 | PII 결과 | 기대 판정 | LOCK |
|----|--------|--------|---------|----------|------|
| T-DCL-20 | D7=PASS + PII=allow | PASS | allow | allow | — |
| T-DCL-21 | D7=PASS + PII=restrict | PASS | restrict | restrict | — |
| T-DCL-22 | D7=PASS + PII=deny | PASS | deny | deny | MR-015 |
| T-DCL-23 | D7=NEEDS_APPROVAL + PII=allow | NEEDS_APPROVAL | allow | restrict | — |
| T-DCL-24 | D7=BLOCK + PII=allow | BLOCK | allow | deny | MR-015 |
| T-DCL-25 | D7=ERROR + PII=allow | ERROR | allow | deny | MR-015 |

### 18.6 project_id 격리 테스트

| ID | 테스트 | 입력 | 기대 결과 | LOCK |
|----|--------|------|----------|------|
| T-DCL-26 | project_id 누락 | project_id=None | DCL_ERR_001 | MR-017 |
| T-DCL-27 | project_id 빈 문자열 | project_id="" | DCL_ERR_001 | MR-017 |
| T-DCL-28 | project_id 공백 | project_id="  " | DCL_ERR_001 | MR-017 |

### 18.7 에러/재시도 테스트

| ID | 테스트 | 입력 | 기대 결과 |
|----|--------|------|----------|
| T-DCL-29 | D7 타임아웃 -> 재시도 -> 성공 | 1회 타임아웃, 2회 PASS | decision=allow |
| T-DCL-30 | D7 타임아웃 -> 재시도 소진 | 3회 타임아웃 | decision=deny + 에스컬레이션 |
| T-DCL-31 | PII 탐지 오류 -> D7만 사용 | PII 예외 발생 | D7 결과만 적용 |
| T-DCL-32 | 확인 훅 미등록 | hook=None | config 기본 정책 적용 |

---

## 19. Phase 2 통합 테스트

| ID | 테스트 | 관련 세션 | 시나리오 |
|----|--------|----------|---------|
| P2-T-01 | DCL + L0 CRUD 통합 | P1-1 | L0 Create 시 DCL check_policy() 경유 + deny 시 L0 저장 차단 |
| P2-T-02 | DCL + L1 CRUD 통합 | P1-2 | L1 Create 시 DCL 경유 + L0->L1 승격 시 DCL deny 시 승격 차단 |
| P2-T-03 | DCL + Chroma 벡터 통합 | P1-3 | deny 시 ChromaVectorStore.upsert() 차단 (LOCK-MR-015) |
| P2-T-04 | DCL + GraphRAG 통합 | P1-4 | deny 시 JsonGraphStore 삽입 차단 |
| P2-T-05 | DCL + Semantic Cache 통합 | P1-5 | deny 시 캐시 저장 차단 |
| P2-T-06 | DCL + Export/Import 통합 | P1-6 | export 시 deny 레코드 포함 여부 정책 확인 |
| P2-T-07 | DCL + PII 마스킹 통합 | P1-7 | restrict 판정 -> PII 마스킹 -> 저장 전체 경로 |
| P2-T-08 | DCL + Memory Decay 통합 | P1-8 | deprecated 소스를 DCL 수집기가 참조 시 경고 |
| P2-T-09 | DCL + 6-Stage RAG Pipeline 통합 | P1-10 | RAG 파이프라인 삽입 전 DCL check_policy() 게이트 |
| P2-T-10 | DCL + Hybrid Search 통합 | P1-11 | 검색 결과에 deny 레코드 포함 방지 |
| P2-T-11 | DCL-FIN + RAG 자동 삽입 | P1-10 | RSS 수집 -> check_policy() -> RAG 삽입 전체 경로 |
| P2-T-12 | DCL-TECH + RAG 자동 삽입 | P1-10 | 1시간 폴링 -> check_policy() -> RAG 삽입 전체 경로 |

---

## 20. 세션 간 인터페이스 cross-check

### 20.1 P1-1 (L0 Session Memory CRUD) 접점

| 인터페이스 | P1-1 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| UserConfirmationHook | §5.2 인터페이스 정의 | §10 확인 훅 통합 | 동일 시그니처 |
| L0_ERR_006 (deny 처리) | §6.1 에러 코드 | §7 Deny 경로에서 L0 저장 차단 | 에러 코드 정합 |
| L0 Create §3.1 Step 5 | policy_decision 검사 | DCL check_policy() 결과 주입 | 판정 결과 전달 |
| P2-T-12 | DCL deny 필터 L0 테스트 | P2-T-01 | 양방향 참조 |

### 20.2 P1-2 (L1 Project Memory CRUD) 접점

| 인터페이스 | P1-2 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| L0->L1 승격 경로 | §9 승격 경로 | §7 deny 시 승격 차단 | P2-T-02 |
| UserConfirmationHook 재사용 | §5.2 P1-1 재사용 | §10 동일 | 동일 |
| P2-T-12 | DCL deny 시 L1 승격 차단 | P2-T-02 | 양방향 참조 |

### 20.3 P1-3 (Chroma Vector DB) 접점

| 인터페이스 | P1-3 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| upsert() policy_decision 검사 | §4.1 Step 1 | §8 벡터 삽입 금지 연동 | LOCK-MR-015 |
| deny 시 에러 | §4.2 deny 시 ValueError 발생 | §8.2 PolicyViolationError (이중 안전장치) | P1-3=ValueError, P1-9=PolicyViolationError — 호출 계층 분리, 양쪽 모두 deny 삽입 차단 |

### 20.4 P1-4 (JSON GraphRAG) 접점

| 인터페이스 | P1-4 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| add_node()/add_edge() deny 차단 | policy_decision=deny 시 삽입 거부 | §7 Deny 경로 (GraphRAG 삽입 차단), §8.1 벡터 가드 경로 | LOCK-MR-015 |
| project_id 3중 격리 | 격리 가드 | §11 project_id 격리 (LOCK-MR-017) | 동일 패턴 |

### 20.5 P1-5 (Semantic Cache) 접점

| 인터페이스 | P1-5 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| cache_response() deny 차단 | 캐시 저장 deny 경로 | §7 Deny 경로 | P2-T-05 |

### 20.6 P1-6 (Export/Import) 접점

| 인터페이스 | P1-6 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| export 시 deny 레코드 포함 정책 | 직렬화 시 policy_decision 보존 | §7 Deny 경로 — deny 레코드 export 포함 여부 정책 | P2-T-06 |

### 20.7 P1-7 (PII 마스킹) 접점

| 인터페이스 | P1-7 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| apply_to_record() | §6 DCL 연동 | §4.3 PII 교차 판정 | 시그니처 정합 |
| PIIPipelineResult.policy_decision | §1.6 데이터 클래스 | §4.3 pii_decision 추출 | 필드 정합 |
| SENSITIVITY_STORAGE_POLICY | §5.1 분류별 정책 맵 | §4.3 민감도 교차 참조 | 값 정합 |

### 20.8 P1-8 (Memory Decay) 접점

| 인터페이스 | P1-8 제공 | P1-9 소비 | 검증 |
|-----------|----------|----------|------|
| deprecated 소스 경고 | P2-T-10 정의 | §1.4 수집기가 deprecated 참조 시 경고 | P2-T-08 |

---

## 21. LOCK-MR 참조 추적표

| LOCK | 설명 | 본 문서 참조 위치 | 준수 상태 |
|------|------|----------------|----------|
| LOCK-MR-001 | 4계층 메모리 L0~L3 | §2.2 scope 필드, §9 L3 특수 처리 | PASS |
| LOCK-MR-002 | B<->L 매핑 | §2.2 memory_type 필드 | PASS |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §7 Deny 경로, §8 벡터 가드 | PASS |
| LOCK-MR-016 | L3 활성 게이트 | §9 L3 ApprovalGate 필수 | PASS |
| LOCK-MR-017 | project_id 격리 | §11 project_id 검증 가드 | PASS |
| LOCK-MR-018 | 저장 전 사용자 확인 | §10 확인 훅 통합 | PASS |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §7.2 원문 대신 해시만 기록 | PASS |

---

## 22. 교차 참조 블록

### 22.1 입력 참조 (본 문서가 참조하는 정본)

| 정본 | 참조 내용 | 본 문서 위치 |
|------|----------|-------------|
| D2.0-06 §3.2 | Allow/Restrict/Deny 계층별 정책 | §1, §5, §6, §7 |
| D2.0-06 §2.3 | L3 Procedural Memory 활성 게이트 | §9 |
| D2.0-07 §5 | PolicyCheck Gate 설계 | §1.2, §4.2 |
| D2.0-07 5-Gate | PolicyGate -> ApprovalGate -> ... | §1.2 |
| RULE 1.3 §7.3 | 저장 전 사용자 확인 | §10 |
| P0-1 MemoryRecordSchema | policy_decision 필드 enum | §2.1 |
| Part2 V1-P2 항목9 | DCL 기초 구현, `storage/kb/dcl_collector.py` | §1.3, §1.4 |

### 22.2 출력 참조 (본 문서를 참조할 후속 세션)

| 후속 세션 | 참조 목적 | 인터페이스 |
|----------|----------|-----------|
| P1-10 (6-Stage RAG) | RAG 파이프라인 삽입 전 DCL 게이트 | check_policy() -> vector_insert_allowed |
| P1-11 (Hybrid Search) | 검색 결과에 deny 레코드 제외 | PolicyDecision.DENY 필터 |
| P2-4 (승격/강등) | 승격 전 DCL 정책 재판정 | check_policy() 재호출 |
| Phase 2 전체 | DCL 통합 테스트 | §19 Phase 2 통합 테스트 12건 |

### 22.3 양방향 포인터

| 도메인 | 6-4 -> 인접 | 인접 -> 6-4 |
|--------|-----------|-----------|
| 6-1 UI-UX | §10 UserConfirmationHook | 확인 모달 구현 |
| 6-2 Security | §9.2 RBAC 검증 | PII 정책 정의 |
| 6-12 Event-Logging | §15 감사 로그 생성 | 로그 저장/보존 정책 |
| 6-5 SDAR | P2-T-08 deprecated 경고 | 이상 탐지 트리거 |
