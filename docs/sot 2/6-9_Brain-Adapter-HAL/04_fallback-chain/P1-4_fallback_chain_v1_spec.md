# P1-4 — Fallback Chain V1 구현 사양서 (2회 전환 + JSON 로깅)

> **도메인**: 6-9_Brain-Adapter-HAL
> **서브폴더**: 04_fallback-chain
> **세션**: P1-4
> **작성일**: 2026-04-14
> **상태**: Phase 1 L2 (설계 완료, 구현 단계 이관용 사양 확정)
> **선행 의존**:
> - P1-1 `01_multi-brain-adapter/P1-1_brain_adapter_v1_spec.md` — 공통 자료구조 `BrainRequest`/`ConnectorResponse`/`BaseBrainAdapter` ABC + §8 `EscalationPayload`
> - P1-2 `02_hal-interface/P1-2_hal_v1_spec.md` — HAL V1 3 Provider + `HalEndpoint` + 설정 우선순위 (LOCK-69-6)
> - P1-3 `03_llm-routing/P1-3_llm_router_v1_spec.md` — Router V1 의 `brain.route.selected` 로깅 스키마·`Decision.gates.result` 기록·"폴백 트리거 시그널" 전달 경계

---

## 0. Purpose & Scope

본 문서는 6-9 도메인의 **Fallback Chain V1** 구현 사양을 정의한다. P1-3 Router 가 선택한 1차 `BaseBrainAdapter` 구현체가 실패(F1~F8) 하는 경우, `04_fallback-chain/_index.md §3` 의 **R-69-3 최대 2회 전환** 정책과 `§4.1` 의 **V-Phase 별 폴백 순서**(LOCK-69-8 기본 Claude→GPT-4o→DeepSeek→Ollama 로컬, 30s 타임아웃) 에 따라 차순위 어댑터를 호출한다. 모든 전환은 `brain.route.fallback` 이벤트로 JSON 구조화 로깅(LOCK-69-10)되며, trace_id 는 전 체인에 걸쳐 단일 값으로 전파된다(LOCK-69-1).

**포함 범위**:
- 폴백 체인 클래스(`FallbackChainV1`) ABC 와 공개 시그니처
- 전환 카운터(`transition_count` 0~2) / 재시도 카운터(`retry_count` F2 전용) 관리
- F1~F8 실패 분류기(`classify_failure`) 및 `failure_code` 매핑
- 30s 타임아웃 기반 전환 결정 (F1, D2.0-04 §5 R2 L721)
- V-Phase 별 폴백 순서 해석 (`§4.1` V0~V3)
- 비용 상한 × 폴백 상호작용 (LOCK-69-7, §5)
- `brain.route.fallback` / `brain.fallback.exhausted` / `brain.qod.low` / `brain.cost.blocked` 4 이벤트 JSON 방출
- `FallbackExhaustedError` + I-20 `EscalationPayload` 전파
- Phase 2 통합 테스트 힌트 12 건

**제외 범위**:
- Router 의 초기 후보 선정 / 가중치 계산 (P1-3 담당)
- 4-4 MLOps 드리프트 기반 가중치 동적 업데이트 (Phase 2 P2-2)
- Batch API 폴백 / Multi-turn 재시도 최적화 (Phase 3 이상)
- CORE 실행·ToolRegistry 위반의 직접 처리 (P1-1 담당)

**정본 경계 원칙**: `04_fallback-chain/_index.md §2~§8` 이 상위 정본이며 본 문서는 구현 사양만 추가한다. `_index.md §9` L3 상태 갱신은 공통 산출물 보호 정책에 따라 도메인 마감 step 5/7/8 에서 일괄 반영하며, 본 세션에서는 본 사양서로 갱신 근거를 확보한다(INDEX.md/_index.md/00_common/ 수정 금지).

---

## 1. 교차 참조 블록 (a)

| 참조 대상 | 섹션 | 용도 |
|-----------|------|------|
| `04_fallback-chain/_index.md` | §2(F1~F8), §3(R-69-3 카운터), §4(V-Phase), §5(비용 상호작용), §6(로깅 스키마) | 상위 정본 — 변경 금지 |
| `03_llm-routing/P1-3_llm_router_v1_spec.md` | §2 `RoutingInput`/`RoutingCandidate`, §로깅 `brain.route.selected` | 1차 선택 결과 수신, trace_id 연결 |
| `03_llm-routing/_index.md` | §2.1 step 5 (폴백 연결점) | 라우팅 → 폴백 계약 |
| `01_multi-brain-adapter/P1-1_brain_adapter_v1_spec.md` | §2 공통 자료구조, §6 로깅(R-01-7), §7 예외 정책, §8 `EscalationPayload`, §10 Phase 2 시나리오 | 에러 코드, 로깅 중첩 구조 |
| `01_multi-brain-adapter/_index.md` | §4.1 `BaseBrainAdapter` ABC | 폴백 체인 입력 타입 (변경 금지) |
| `02_hal-interface/P1-2_hal_v1_spec.md` | §3 설정 우선순위, `HalEndpoint.enabled`/`health_check` | 차순위 후보 필터 |
| `AUTHORITY_CHAIN.md` | LOCK-69-1/7/8/10, R-69-3, R-69-5 | 규칙 근거 |
| `CONFLICT_LOG.md` | W-4 (Part2 V1 순서 ↔ LOCK-69-8) | §4.1 V-Phase 분기로 해결됨 확인 |
| `D:\VAMOS\docs\sot\D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` | §5 R2, §5.1 step 5, §6 에러 복구, §8.3 로깅 | L1 정본 |
| `D:\VAMOS\docs\sot\RULE 1.3_VAMOS_RULES_v1.3.md` | §5 비용 상한 | LOCK-69-7 근거 |
| `BRAIN_ADAPTER_HAL_구조화_종합계획서.md` | §7 P1-4 절차·검증·산출물 | 작업 절차 |

---

## 2. 공통 자료 구조 선정의 (g, k)

> `BrainRequest`/`ConnectorResponse`/`BaseBrainAdapter` 는 P1-1 §2 및 `01/_index.md §3/§4.1` 정본을 그대로 참조한다(변경 금지). `RoutingInput`/`RoutingCandidate` 는 P1-3 §2 를 그대로 참조한다(변경 금지). 본 세션에서 추가로 필요한 자료구조만 아래에 정의한다.

### 2.1 폴백 체인 입력/출력 (Pydantic, `extra=forbid`)

```python
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

FailureType = Literal["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]
FailureCode = Literal[
    "BRAIN_TIMEOUT", "BRAIN_RATE_LIMIT", "BRAIN_SERVER_ERROR",
    "BRAIN_COST_EXCEEDED", "BRAIN_QOD_LOW", "BRAIN_POLICY_DENIED",
    "BRAIN_NETWORK_ERROR", "BRAIN_NOT_REGISTERED",
]
VPhase = Literal["V0", "V1", "V2", "V3"]

class FallbackInput(BaseModel):
    """FallbackChainV1.execute() 입력."""
    request: "BrainRequest"                  # P1-1 §2.1 정본 (변경 금지)
    primary: "RoutingCandidate"              # P1-3 §2 Router 가 1차 선택한 후보
    v_phase: VPhase                          # §4.1 분기 근거
    cost_budget_remaining_pct: float = Field(..., ge=0.0, le=100.0)
    started_at: datetime                     # 최초 호출 시각 (total_elapsed_ms 산정)
    class Config: extra = "forbid"

class FallbackAttempt(BaseModel):
    """전환/재시도 1회 단위 기록."""
    attempt_index: int = Field(..., ge=0, le=3)  # 0=primary, 1/2=transition
    from_model: Optional[str] = None             # primary 시 None
    to_model: str
    adapter_id: str                              # "llm_anthropic_text" 등
    failure_type: Optional[FailureType] = None   # 성공 시 None
    failure_code: Optional[FailureCode] = None
    retry_count_for_attempt: int = 0             # F2 전용
    elapsed_ms: int = Field(..., ge=0)
    class Config: extra = "forbid"

class FallbackOutput(BaseModel):
    """FallbackChainV1.execute() 결과."""
    response: Optional["ConnectorResponse"] = None   # 최종 성공 시 존재
    exhausted: bool                                  # True 면 response=None
    transition_count: int = Field(..., ge=0, le=2)
    retry_count: int = Field(..., ge=0)
    attempts: List[FallbackAttempt]
    trace_id: str
    total_elapsed_ms: int
    deny_reason: Optional[str] = None                # F6 또는 exhausted 시
    class Config: extra = "forbid"
```

### 2.2 타임아웃·전환 상수 (ENV / config / 코드 기본값 — LOCK-69-6)

| 키 | ENV | config.yaml | 기본값 | 근거 |
|----|-----|-------------|--------|------|
| 단일 호출 타임아웃(ms) | `VAMOS_BRAIN_TIMEOUT_MS` | `brain.global.timeout_ms` | `30000` | LOCK-69-8, §2 F1 |
| 최대 전환 횟수 | `VAMOS_FALLBACK_MAX_TRANSITIONS` | `brain.fallback.max_transitions` | `2` | R-69-3, §3.2 |
| F2 재시도 기본 대기(s) | `VAMOS_FALLBACK_RETRY_AFTER_DEFAULT_S` | `brain.fallback.retry_after_default_s` | `10` | §2 F2 |
| V1 타임아웃 재시도 한도 | — | `brain.fallback.v1_timeout_retries` | `3` | §4.2 Part2 L2123 LOCK |
| Ollama 최종 도달 허용 | — | `brain.fallback.allow_local_tail` | `true` | LOCK-69-8 |

---

## 3. 알고리즘 (f, Big-O + LOCK + ABC)

### 3.1 ABC 시그니처 정본 (h, i)

```python
from abc import ABC, abstractmethod

class BaseFallbackChain(ABC):
    """S6 (Fallback Chain) ABC — _index.md §1 본 도메인 역할."""

    @abstractmethod
    def execute(self, fin: "FallbackInput") -> "FallbackOutput":
        """
        Big-O: 최악 O(T) — T = max_transitions + 1 ≤ 3 호출.
        LOCK: 69-1, 69-7, 69-8, 69-10. R-69-3, R-69-5.
        """
        raise NotImplementedError

    @abstractmethod
    def classify_failure(self, exc: BaseException, http_status: Optional[int] = None) -> "FailureType":
        """예외·HTTP 상태 → F1~F8 매핑. Big-O O(1). LOCK: 69-10."""
        raise NotImplementedError

    @abstractmethod
    def next_candidate(
        self, current: "RoutingCandidate", v_phase: "VPhase",
        cost_budget_remaining_pct: float, excluded: List[str],
    ) -> Optional["RoutingCandidate"]:
        """§4.1 분기표 + §5 비용 필터 적용하여 차순위 1개 반환.
           Big-O O(P) — P = V-Phase 별 폴백 후보 수 ≤ 4. LOCK: 69-7, 69-8."""
        raise NotImplementedError
```

### 3.2 S 번호 정본 (i) — 도메인 모듈 S0~S8 중 본 세션 범위

| S 번호 | 모듈 | 담당 세션 | 본 세션 역할 |
|--------|------|-----------|-------------|
| S0 | `_index.md` / AUTHORITY_CHAIN 정본 | 공통 | 참조 |
| S1 | 01 Multi-Brain-Adapter 공통 자료구조 | P1-1 | 참조 (BrainRequest/ConnectorResponse) |
| S2 | 02 HAL Interface | P1-2 | 참조 (HalEndpoint, 설정 우선순위) |
| S3 | 03 LLM Router | P1-3 | 입력 계약 (primary candidate) |
| **S4** | **04 Fallback Chain** | **P1-4 (본 세션)** | **ABC·로직·로깅·테스트 산출** |
| S5 | 05 Integration Test 스위트 | Phase 2 P2-1~P2-4 | 미범위 |
| S6 | 도메인 Adapter Catalog 통합 | 도메인 마감 | 미범위 |
| S7 | 06 MLOps Drift Handler | Phase 2 P2-2 | 미범위 |
| S8 | 07 Observability 통합 | Phase 3 | 미범위 |

### 3.3 execute() 절차 (Phase 별 복구, e)

```
[Phase 0: 입력 검증]
  FallbackInput Pydantic extra=forbid 검증 → 실패 시 raise ValidationError
  trace_id = fin.request.trace_id (LOCK-69-1 전파)

[Phase 1: Primary 호출]
  attempt 0 = invoke(fin.primary.adapter) with timeout=30s
    ├── 성공 → FallbackOutput(exhausted=False, transition_count=0, attempts=[a0 success])
    └── 예외 → classify_failure(exc, http_status) → ft
                 │
                 ├── F6 → 즉시 deny + brain.route.fallback(to=null) + I-20 (severity=high) → Phase 4 (exhausted)
                 ├── F2 & retry_count==0 → Phase 2a (재시도)
                 └── 그 외 → Phase 2b (전환)

[Phase 2a: 동일 모델 재시도 (F2 전용)]
  retry_count += 1 (transition_count 미변경)
  sleep(Retry-After or default 10s)
  invoke(primary) 재호출
    ├── 성공 → FallbackOutput(transition_count=0, retry_count=1)
    └── 실패 → Phase 2b 진입

[Phase 2b: 전환 (최대 2회)]
  while transition_count < MAX_TRANSITIONS:
      nxt = next_candidate(current, v_phase, cost_budget_remaining_pct, excluded)
      if nxt is None:  # §5 비용 필터로 후보 소진
          break
      brain.route.fallback 로그 방출 (transition_count+1 시점 값)
      transition_count += 1
      attempt_k = invoke(nxt) with timeout=30s
        ├── 성공 → FallbackOutput(exhausted=False, transition_count=k, ...)
        └── 실패 → classify_failure → excluded.append(current.model_id) → 루프 계속

[Phase 3: V1 타임아웃 재시도 예외 경로 (§4.2)]
  if v_phase == "V1" and ft == "F1" and same_model_timeouts < 3:
      same_model_timeouts += 1 (transition_count 미소모)
      invoke(current) 재호출
  else:
      정상 Phase 2b 경로

[Phase 4: 소진 처리]
  exhausted=True
  brain.fallback.exhausted ERROR 로그 + I-20 EscalationPayload(severity=high) 동기 전송
  return FallbackOutput(response=None, exhausted=True, deny_reason="...", attempts=[...])
```

**Big-O**: 최악 `O(3)` 호출 (Phase 1 + Phase 2b 최대 2회) + Phase 3 V1 에서 동일 모델 최대 3회 추가 재시도(v1_timeout_retries=3). 총 호출 수 상한은 `1 + 3 + 2 = 6` (V1 한정). 공간 복잡도 `O(T)` — attempts 리스트.

### 3.4 next_candidate() — V-Phase 분기 + 비용 필터

```python
_BASE_ORDER = {
  "V0": ["ollama_local"],
  "V1": ["openai_gpt4o_mini", "anthropic_sonnet", "ollama_local"],      # §4.1
  "V2": ["anthropic_sonnet", "openai_gpt4o", "deepseek", "ollama_local"],
  "V3": ["anthropic_sonnet", "openai_gpt4o", "deepseek", "vllm_local"],
}

def next_candidate(current, v_phase, cost_budget_remaining_pct, excluded):
    order = _BASE_ORDER[v_phase]
    # 1) LOCK-69-7: CostBudget ≥ 100% → 외부 API 전체 제외, 로컬만 허용
    if cost_budget_remaining_pct <= 0.0:
        allowed = [m for m in order if m.endswith("_local")]
    # 2) 80% ≤ CostBudget < 100% → 고비용 모델 제외
    elif cost_budget_remaining_pct < 20.0:
        allowed = [m for m in order if m not in HIGH_COST_MODELS]
    else:
        allowed = order
    # 3) 이미 시도한 모델 + 현재 모델 제외
    allowed = [m for m in allowed if m not in excluded and m != current.model_id]
    return RoutingCandidate.from_id(allowed[0]) if allowed else None
```

Big-O `O(P)` (P ≤ 4). LOCK-69-7 (비용) + LOCK-69-8 (기본 순서) 동시 준수.

> [V1_LITERAL_EXTENSION_NOTE] P1-3 §2.1 `RoutingCandidate.provider_id` Literal 은 V1 범위 3종(`ollama_local`, `openai`, `anthropic`) 이다. V2 의 `deepseek` 및 V3 의 `vllm_local` 은 V-Phase 확장 시 P1-3 Literal 확장을 요구한다. 본 세션 V1 구현에서는 `next_candidate` 가 V2/V3 `_BASE_ORDER` 순회 중 V1 Literal 밖 값(`deepseek`, `vllm_local`) 을 만나면 **V1 범위 허용 목록으로 사전 필터**하여 건너뛰고, 실제 V2/V3 운영 시점에 P1-3 Literal 확장 + 어댑터 추가가 선행된다는 전제로 `_BASE_ORDER` 원본은 정본 순서로 유지한다. CONFLICT 는 아니며 V-Phase 전환 체크리스트 항목으로 추적한다.

---

## 4. 예외 정책표 (g) — _index.md §2.2 정합

| failure_type | failure_code | 트리거 | recoverable | 처리 | 에스컬레이션 | LOCK |
|:---:|---|---|:---:|---|---|---|
| F1 | `BRAIN_TIMEOUT` | health_check or invoke > 30s | YES | 즉시 차순위 전환 (V1 은 3회 예외) | 소진 시 I-20 (severity=high) | 69-8 |
| F2 | `BRAIN_RATE_LIMIT` | HTTP 429 | YES | Retry-After 대기 후 재시도 1회 → 실패 시 전환 | 소진 시 I-20 (severity=medium) | 69-8 |
| F3 | `BRAIN_SERVER_ERROR` | HTTP 5xx | YES | 즉시 차순위 전환 | 인시던트 로깅 + I-20 (severity=high) | 69-8 |
| F4 | `BRAIN_COST_EXCEEDED` | CostBudget ≥ 100% | NO (상향 불가) | 비용 하향 폴백 전용 → 최종 로컬 | I-20 (severity=medium) | 69-7 |
| F5 | `BRAIN_QOD_LOW` | qod_hint < 0.3 | YES | 상위 모델 에스컬레이션 (LOCK-69-8 역순, 비용 범위 내) | 결과 반환 + `brain.qod.low` 경고 | 69-7, 69-8 |
| F6 | `BRAIN_POLICY_DENIED` | 07 PolicyCheck deny | **NO (폴백 불가)** | 즉시 deny | I-20 (severity=critical) | R-69-5 |
| F7 | `BRAIN_NETWORK_ERROR` | TCP/DNS/TLS 실패 | YES | 로컬 직행 (외부 불가) | I-20 (severity=high) | 69-8 |
| F8 | `BRAIN_NOT_REGISTERED` | HAL 카탈로그 미등록 | NO | HAL 기본 모델 → 로컬 | I-20 (severity=high) — 설정 오류 | 69-6, 69-8 |

### 4.1 P1-1 §7 매핑 (세션 간 인터페이스 cross-check, j)

| P1-1 예외 코드 | 본 세션 매핑 | 비고 |
|---|---|---|
| `cost_cap_exceeded` | F4 `BRAIN_COST_EXCEEDED` | 사전 견적 단계는 P1-1 어댑터에서 raise, 본 세션은 호출 중 CostBudget 갱신 시 재검사 |
| `provider_timeout` | F1 `BRAIN_TIMEOUT` | classify_failure 가 `TimeoutError` / `httpx.ReadTimeout` → F1 |
| `provider_auth_error` | F3 `BRAIN_SERVER_ERROR` (401/403 은 F6 으로 격상 가능) | 401/403 은 정책 차단으로 전환 금지 — 설정 문제 가능성 → I-20 critical |
| `provider_rate_limit` | F2 `BRAIN_RATE_LIMIT` | 동일 모델 1회 재시도 후 전환 |
| `tool_registry_miss` | (폴백 불가) | P1-1 어댑터 단계 raise, 본 체인 미도달 |
| `langchain_import_detected` | (CI 단계 차단) | 본 체인 미도달 |
| `schema_validation_error` | F3 취급 (서버 오류로 간주) | 즉시 전환 |
| `provider_5xx` | F3 `BRAIN_SERVER_ERROR` | 즉시 전환 |

---

## 5. 로깅 포맷 (c, R-01-7 중첩 JSON)

### 5.1 `brain.route.fallback` — WARN, `_index.md §6.2` 스키마 정본 준수

```json
{
  "ts": "2026-04-14T06:00:12.337Z",
  "level": "WARN",
  "event": "brain.route.fallback",
  "module": "brain.adapter.fallback",
  "trace_id": "tr-abc123",
  "error": {
    "code": "BRAIN_TIMEOUT",
    "message": "anthropic.messages call exceeded 30s",
    "recoverable": true,
    "source": "invoke"
  },
  "context": {
    "from_model": "claude-sonnet-4-20250514",
    "to_model": "gpt-4o",
    "failure_type": "F1",
    "v_phase": "V2",
    "transition_count": 1,
    "retry_count": 0,
    "total_elapsed_ms": 30250,
    "cost_budget_remaining_pct": 45.2,
    "adapter_id": "llm_anthropic_text"
  },
  "recovery": {
    "retried": 0,
    "fallback_used": true,
    "downgrade_penalty": 0.10,
    "retry_after_sec": null,
    "qod_hint": null,
    "deny_reason": null
  }
}
```

R-01-7 중첩 4 요소(`error`/`context`/`recovery` + `trace_id`) 전부 충족. P1-1 §6 로그 구조 정합 (최상위 `event`/`trace_id`, 중첩 `error`/`context`/`recovery` 동일).

### 5.2 `brain.fallback.exhausted` — ERROR

```json
{
  "ts": "2026-04-14T06:00:45.811Z",
  "level": "ERROR",
  "event": "brain.fallback.exhausted",
  "module": "brain.adapter.fallback",
  "trace_id": "tr-abc123",
  "error": {
    "code": "BRAIN_FALLBACK_EXHAUSTED",
    "message": "2 transitions + primary all failed",
    "recoverable": false,
    "source": "fallback_chain"
  },
  "context": {
    "v_phase": "V2",
    "attempts_count": 3,
    "last_failure_type": "F1",
    "total_elapsed_ms": 95430,
    "cost_budget_remaining_pct": 45.2
  },
  "recovery": {
    "retried": 0,
    "fallback_used": true,
    "downgrade_penalty": 0.30,
    "deny_reason": "brain.fallback.exhausted"
  }
}
```

### 5.3 `brain.qod.low` — WARN (F5)

| 필드 | 값 |
|---|---|
| event | `brain.qod.low` |
| level | WARN |
| context.qod_hint | < 0.3 실측값 |
| recovery.fallback_used | `true` (에스컬레이션 1회 시) |

### 5.4 `brain.cost.blocked` — WARN (LOCK-69-7)

| 필드 | 값 |
|---|---|
| event | `brain.cost.blocked` |
| level | WARN |
| context.cost_budget_remaining_pct | `0.0` |
| recovery.fallback_used | `true` (로컬 강제 전환 시) or `false` (deny 시) |

---

## 6. EscalationPayload (I-20, b) — P1-1 §8 정본 재사용

본 세션은 P1-1 §8 `EscalationPayload` 를 **그대로 재사용**한다. 신규 필드 추가 없음 (j 세션 간 인터페이스 cross-check 준수).

```python
# P1-1 §8 정본 재사용 - 변경 없음
EscalationPayload(
    source_engine="brain_adapter.fallback",
    error_code="BRAIN_FALLBACK_EXHAUSTED",   # §4 표의 failure_code
    severity="high",                          # F1/F3/F7/F8 high, F4/F5 medium, F6 critical
    original_request=redact(fin.request),     # API 키/PII 제거
    partial_result=last_response_or_none,
    retry_count=fout.retry_count,
    fallback_path=[a.adapter_id for a in fout.attempts],
    timestamp=datetime.utcnow().isoformat() + "Z",
    trace_id=fout.trace_id,
    notes=fout.deny_reason,
)
```

**severity 매핑**:

| failure_type | severity | 근거 |
|:---:|:---:|------|
| F6 (정책 차단) | critical | R-69-5 위반, 즉시 거버넌스 보고 |
| F3, F7, F8 | high | 시스템/네트워크/설정 오류 |
| F1 소진 | high | 전 프로바이더 가용성 장애 가능 |
| F4 | medium | 정상적 비용 보호 |
| F2, F5 | medium | 일시적 저하 |

전송 경로: `FallbackChainV1 → I-20 Escalation Router → 6-2 Security-Governance + 0-0 Governance(F6)`. 동기 호출(R-01-8), fire-and-forget 금지.

---

## 7. 의존성 그래프 산출물 (l)

```
[Upstream 호출자]
  1-1 Verifier-Reasoning-Engines (C-1~C-3, D-1~D-2)
  6-11 Hologram-Main-LLM (2-tier 라우팅)
  4-3 MCP Server/Client (도구 호출)
          │
          ▼
[P1-3 Router V1]  ──brain.route.selected──▶  Decision.gates.result
          │  (RoutingCandidate primary + RoutingInput)
          ▼
[P1-4 Fallback Chain V1] ◀── 본 세션 ──▶
          │  ├─(invoke)─▶ [P1-1 BaseBrainAdapter] ── Ollama / OpenAI / Anthropic
          │  ├─(config)──▶ [P1-2 HAL Endpoints]
          │  └─(log)────▶ brain.route.fallback / brain.fallback.exhausted
          ▼
[I-20 Escalation Router] ── 6-2 Security-Governance
                         ── 0-0 Governance (F6 critical 시)
          │
[Downstream]
  ConnectorResponse → 호출자
  또는 FallbackExhaustedError → 호출자 raise
```

**계약 불변**:
- 상류: `RoutingCandidate` 는 P1-3 §2 정본 사용 (본 세션 확장 금지)
- 하류: `ConnectorResponse` 는 P1-1 §2 / LOCK-69-1 5 필드 정본 사용
- 로깅: `_index.md §6` 스키마 정본 (본 세션 추가 금지, 5.x 는 정본 재구성)

---

## 8. Phase 2 테스트 시나리오 (≥ 12 건, d)

> 단위 테스트(`tests/unit/fallback/test_fallback_chain_v1.py`) 와 통합 테스트(`tests/integration/fallback/`) 로 분할. Phase 2 P2-1~P2-4 에서 확장.

### 8.1 단위 테스트 (U-FB-1 ~ U-FB-12)

| # | 케이스 | 주입 | 기대 결과 | LOCK |
|---|--------|------|-----------|:---:|
| U-FB-1 | Primary 즉시 성공 | mock Anthropic 200 | exhausted=False, transition_count=0, attempts=[1 success] | 69-1 |
| U-FB-2 | F1 타임아웃 → 1회 전환 성공 | Anthropic 31s sleep, GPT-4o 200 | transition_count=1, attempts[0].failure_type=F1, attempts[1].success | 69-8 |
| U-FB-3 | F1 + F3 2회 전환 → Ollama 성공 | Anthropic timeout, GPT-4o 500, Ollama 200 | transition_count=2, Ollama 최종 성공 | 69-8 |
| U-FB-4 | 3회 모두 실패 → exhausted | 3 모델 전부 timeout | FallbackExhaustedError raise, I-20 payload severity=high | R-69-3 |
| U-FB-5 | F2 429 → 동일 모델 재시도 성공 | Anthropic 429 (Retry-After: 5), 2회째 200 | transition_count=0, retry_count=1 | 69-8 |
| U-FB-6 | F2 재시도 실패 → 전환 | Anthropic 429 → 429, GPT-4o 200 | transition_count=1, retry_count=1 | 69-8 |
| U-FB-7 | F4 비용 초과 → 하향 전환 | cost_budget_remaining_pct=0, Claude Opus 제외 확인 | next_candidate 결과 Ollama 로컬만 | 69-7 |
| U-FB-8 | F6 정책 차단 → 즉시 deny | Anthropic 403 Policy | transition_count=0, exhausted=True, I-20 severity=critical | R-69-5 |
| U-FB-9 | F7 네트워크 → 로컬 직행 | DNS ResolutionError | attempts[1].to_model=Ollama (외부 스킵) | 69-8 |
| U-FB-10 | V1 타임아웃 3회 재시도 예외 | v_phase=V1, Anthropic 3회 timeout → GPT-4o 200 | transition_count=1, same_model_timeouts=3 기록 | §4.2 |
| U-FB-11 | JSON 로그 중첩 구조 | 임의 F1 전환 | log.error/context/recovery/trace_id 4 블록 전부 존재 | 69-10, R-01-7 |
| U-FB-12 | trace_id 체인 전파 | request.trace_id="T-X" | 모든 attempts / 모든 로그 / FallbackOutput.trace_id == "T-X" | 69-1 |

### 8.2 통합 테스트 힌트 (IT-FB-1 ~ IT-FB-5, Phase 2 P2-1/P2-3 선행 연계)

| # | 시나리오 | 연계 세션 |
|---|----------|-----------|
| IT-FB-1 | 1-1 C-1 검증기 → Brain Adapter → F1 폴백 → 최종 응답까지 E2E | P2-1 |
| IT-FB-2 | 6-11 2-tier 라우팅 Main LLM 실패 → Ollama 폴백 | P2-3 |
| IT-FB-3 | 4-4 드리프트 가중치 갱신 후 폴백 체인 순서 변경 반영 | P2-2 |
| IT-FB-4 | V-Phase V1 → V2 전환 시 폴백 순서 런타임 교체 | Phase 2 |
| IT-FB-5 | 병렬 3 태스크 모두 F1 발생 → 각각 독립 체인으로 폴백 (LOCK-69-2 상한 준수) | P2-4 |

### 8.3 커버리지 목표

- 단위: 라인 ≥ 90%, 브랜치 ≥ 85%
- F1~F8 실패 타입 전수 1 건 이상 커버
- LOCK-69-1/7/8/10, R-69-3/R-69-5 각 1 건 이상 커버

---

## 9. 예외 케이스 및 구현 노트

1. **V1 3회 재시도 (§4.2 Part2 L2123 LOCK)** — `v_phase == "V1" && failure_type == "F1"` 조건에서만 동일 모델 최대 3회 호출. `same_model_timeouts` 카운터 별도 관리, `transition_count` 와 분리.
2. **F5 에스컬레이션 상한** — qod_hint < 0.3 으로 상위 모델 전환 시 LOCK-69-7 비용 범위 내 모델만 허용. `next_candidate` 에 `escalation=True` 힌트 전달 (역순 탐색).
3. **trace_id 주입 규칙** — `fin.request.trace_id` 가 None 이면 즉시 `FallbackInputError` raise (LOCK-69-1 전파 보장).
4. **Downgrade Penalty** — P1-1 §7.2 표 준수. 1차 전환 -0.10, 2차 -0.20, Ollama 도달 -0.25, 누적 상한 -0.30. `FallbackOutput.response.qod_hint` 적용 시 `max(0.0, qod - Σpenalty)`.
5. **로그 평문 금지 (LOCK-69-10)** — 모든 전환/소진 이벤트는 JSON logger (`structlog` 또는 `logging.Formatter(json)`) 로 단일 라인 출력. `print` / plain `logger.warning("text")` 사용 금지 — pre-commit `ast` 린트로 차단.
6. **CORE 실행 금지 (LOCK-69-5)** — FallbackChain 내부에서 `subprocess.run` / 파일 IO / OS 명령 금지. 로그는 ConnectorResponse 의 `evidence_summary` 경로로 위임.
7. **공통 산출물 미터치** — `_index.md §9 L3 상태` 의 "구현 코드 ⬜ L0" 항목은 도메인 마감 step 에서 일괄 갱신. 본 세션 L0→L2 전환 근거는 본 사양서로 확보.

---

## 10. 검증 체크리스트 (§7 P1-4 게이트 정합)

- [x] 타임아웃 시나리오에서 30s 후 전환 결정 로직 정의 (LOCK-69-8) — §3.3 Phase 1·2b
- [x] 최대 2회 전환 후 FallbackExhaustedError 반환 로직 정의 (R-69-3) — §3.3 Phase 4
- [x] 폴백 순서 Claude → GPT-4o → DeepSeek → Ollama (V2 기본) 준수 (LOCK-69-8) — §3.4 `_BASE_ORDER`
- [x] 각 전환 시 JSON 구조화 로그 정의 (LOCK-69-10) — §5.1
- [x] trace_id 체인 전반 전파 (LOCK-69-1) — §2.1 FallbackOutput.trace_id, §9 주입 규칙
- [x] `_index.md` 미수정 (공통 산출물 보호) — §0 정본 경계 원칙, 도메인 마감 일괄 반영 명시
- [x] 교차 참조 블록(a) — §1
- [x] Phase 별 복구 전략(e) — §3.3
- [x] EscalationPayload(b) I-20 — §6
- [x] R-01-7 중첩 JSON(c) — §5.1
- [x] Phase 2 테스트 10+ (d) — §8 17 건 (단위 12 + 통합 5)
- [x] Big-O + LOCK + ABC (f) — §3.1, §3.3 Big-O
- [x] 공통 자료구조 선정의 (g, k) — §2
- [x] 세션 간 인터페이스 cross-check (j) — §1, §4.1, §6 (P1-1 EscalationPayload 재사용)
- [x] ABC 시그니처 정본 (h) — §3.1
- [x] S0~S8 정본 (i) — §3.2
- [x] 의존성 그래프 산출물 (l) — §7
- [x] 예외 정책표 (g) — §4

---

## 11. 이월 메모 (다음 세션 / 구현 단계)

> **[P1-4 → 도메인 마감 / 구현 단계 핸드오프]** (2026-04-14)
> - (a) `_index.md §9 L3 상태` 의 "구현 코드 ⬜ L0" → 구현 단계에서 파일 생성 시 L2 갱신. 본 세션 사양 근거 확보 완료 (공통 산출물 보호로 미수정).
> - (b) `vamos/fallback/fallback_chain_v1.py` 실 파일 생성 및 U-FB-1 ~ U-FB-12 실행 → 구현 단계 (본 세션 범위 아님).
> - (c) IT-FB-1 ~ IT-FB-5 통합 테스트(1-1/4-4/6-11/P2-4 교차 도메인) → Phase 2 (본 세션 범위 아님).
> - (d) V-Phase V1 ↔ V2 런타임 스위칭 시 `_BASE_ORDER` 핫리로드 전략 → 구현 단계에서 `watchdog` 기반 config reload 검토.
> - (e) F6 critical 시 0-0 Governance 보고 엔드포인트는 I-20 Escalation Router 통일 경로 사용. 0-0 도메인 별도 통합은 Phase 3 거버넌스 통합 시점.
> - 선행 확인(Phase 2 P2-1): 본 세션이 확정한 `FallbackChainV1` ABC 시그니처 (`execute`/`classify_failure`/`next_candidate`) 및 `brain.route.fallback` 로깅 스키마를 1-1 추론 엔진 통합 테스트의 폴백 시나리오 기준으로 참조할 것.

---

## 12. 산출물 파일 경로 (구현 단계 — 경로 고정)

| 경로 | 용도 | 생성 주체 |
|------|------|-----------|
| `D:\VAMOS\04. 구현단계\[버전]\vamos\fallback\fallback_chain_v1.py` | FallbackChainV1 구현체 | 구현 단계 (본 세션 범위 아님) |
| `D:\VAMOS\04. 구현단계\[버전]\vamos\fallback\classify.py` | classify_failure 매핑 헬퍼 | 구현 단계 |
| `D:\VAMOS\04. 구현단계\[버전]\vamos\fallback\config\fallback_v1_config.yaml` | v_phase 별 `_BASE_ORDER`, max_transitions, timeout_ms | 구현 단계 |
| `D:\VAMOS\04. 구현단계\[버전]\tests\unit\fallback\test_fallback_chain_v1.py` | U-FB-1 ~ U-FB-12 단위 테스트 | 구현 단계 |
| `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\04_fallback-chain\P1-4_fallback_chain_v1_spec.md` | **본 문서 (P1-4 산출물)** | 본 세션 |
| `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\04_fallback-chain\_index.md` | §9 구현 상태 업데이트 (L0→L2) | 도메인 마감 step 5/7/8 일괄 반영 |

---

[GUARDS_OK] memory_skipped=YES forbidden_paths=untouched common_artifacts=untouched
[STEP1_COMPLETE] domain=6-9 session=P1-4 files_modified=1
