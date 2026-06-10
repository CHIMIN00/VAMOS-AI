# 06. Domain-specific Policy Overrides (SS4.1)

> **버전**: v2.1
> **Status**: LOCKED (Phase 4 2026-05-31, was REVIEW — 18-file LOCKED inventory)
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-04-07 (v2.1: 재검증 패스 — 자세한 변경은 §14) / Phase 4 LOCKED 2026-05-31
> **정본 소유 개념**: "Only Stricter Direction" 판정 알고리즘(연산자별), 6개 카테고리 기본값(Global), Policy Resolution 4단계 파이프라인(Global→Domain→Node→Merge), 도메인별 Override 예시(BN-Health/CodeEngine/Trading/Content), 느슨한 override 자동 거부 + 감사 로그 스키마. **권한 매트릭스(Permission Level 0~5) 정본은 01**, **Guardrail 카탈로그/병합 정본은 03**, **본 문서는 K-041/Guardrail이 아닌 정책 룰(파라미터 단위 수치/enum/boolean) 차원에서의 stricter-only 합성 알고리즘을 정본화**.
> **기술스택 의존성**: SPEC §14 범위 내
> **SOT 근거**: D2.0-03 §4.1 (Lines 732~736: 도메인 정책 상속+오버라이드 규칙); D2.0-01 RULE 1.3 §4.2 (NODE는 CORE 정책 상속); D2.0-05 §7.3 고정 1 (LOCK-BN-10 07 Gate 경유 의무); D2.1-D3 (Envelope 정본)
> **GAP 해결**: GAP-BN-06 (HIGH)
> **L3 달성**: E1~E9 전항목 충족

---

## LOCK 인용

> LOCK (D2.0-03 §4.1 — LOCK-BN-17, Lines 734~736): 오버라이드 허용 범위는 **안전한 방향만**이다.
> - 허용: 더 엄격한 제한(Restrict/Deny 강화), 더 낮은 비용/리소스 사용, 더 보수적 승인 요구
> - 금지: Non-goal 완화, P2 자동 실행/자동 생성, 비용 상한 완화, 민감정보 저장 허용 등 (RULE 1.3 절대 변경 불가 항목)

> LOCK (D2.0-01 RULE 1.3 §4.2): NODE는 CORE 정책을 **상속**한다. 상속 체인은 Global(ORANGE CORE) → Domain(도메인 분류) → Node(개별 BN) 3단으로 고정.

> LOCK (D2.0-05 §7.3 고정 1 — LOCK-BN-10): 모든 정책/비용/승인 판정은 07 Gate 경유. 본 문서가 산출한 `ResolvedPolicy`는 Execute 단계 진입 전 07 Gate(PolicyCheck)의 **선행 입력**으로 전달되며, Gate 결과를 에이전트 내부 if문으로 대체할 수 없다.

---

## 1. 개요

Blue Node의 도메인별 정책 재정의 규칙을 정의한다. 핵심 원칙은 **"Only Stricter Direction"** — 자식 노드는 부모 정책을 더 엄격한 방향으로만 재정의 가능하며, 느슨한 override 시도는 자동 거부 + 감사 로그에 기록된다.

본 문서는 다음을 정본으로 보유한다:

1. **Policy 데이터 모델** — `PolicyRule` / `Policy` / `OverrideAttempt` / `ResolvedPolicy` Pydantic 모델 (§2, 선언 순서 = forward ref 회피)
2. **6개 카테고리 Global 기본값** — Safety/Quality/Performance/Resource/Privacy/Content (§3)
3. **연산자별 stricter 판정 알고리즘** — `max`/`min`/`exact`/`range`/`enum`/`boolean` (§4)
4. **Policy Resolution 4단계 파이프라인** — Global→Domain→Node→Merge (§5)
5. **도메인별 Override 예시** — BN-Health(엄격 강화), BN-CodeEngine(혼합), BN-Trading(보수적 승인), BN-Content(필터 강화) (§6)
6. **자동 거부 + 감사 로그 스키마** + 에러 코드 (§7~§8)

> **소유 경계**:
> - **Permission Level 0~5 매트릭스**(K-041)·**resource_type별 기본 Level**·**Dynamic Permission Adjuster**의 정본은 `01_permission-matrix/_index.md`. 본 문서는 Permission Level을 정책 룰의 한 파라미터로 **참조만** 한다(파라미터명: `min_permission_level`).
> - **Guardrail 카탈로그**(GR_NO_PII 등 11종)·**guardrail merge**(action 우선순위 block>rewrite>warn)의 정본은 `03_template-injection/_index.md` §3.3/§4.1. 본 문서는 guardrail 단위가 아닌 **파라미터 단위(수치/enum/boolean)** 정책 룰만 정본화한다.
> - **저장 계층 L0~L3**·**TTL**·**MemoryRecord**의 정본은 D2.0-06.

---

## 2. Pydantic 모델 (E1)

```python
from pydantic import BaseModel, Field, validator
from typing import Any, Optional, Literal, Union
from datetime import datetime
from enum import Enum
from uuid import uuid4


class PolicyCategory(str, Enum):
    SAFETY = "safety"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    PRIVACY = "privacy"
    CONTENT = "content"


class PolicyOperator(str, Enum):
    MAX = "max"          # value 이하만 허용 (낮을수록 엄격, direction=↓)
    MIN = "min"          # value 이상만 허용 (높을수록 엄격, direction=↑)
    EXACT = "exact"      # value 정확히 일치
    RANGE = "range"      # [lo, hi] 범위 내 (좁을수록 엄격, direction=⊂)
    ENUM = "enum"        # 허용 값 집합 (부분집합일수록 엄격, direction=⊂)
    BOOLEAN = "boolean"  # bool (strict pole 은 direction 으로 결정 — ↑=true / ↓=false)


class PolicyDirection(str, Enum):
    DOWN = "↓"           # 작은 쪽이 엄격 (max numerics, false-pole boolean)
    UP = "↑"             # 큰 쪽이 엄격 (min numerics, true-pole boolean)
    SUBSET = "⊂"         # 부분집합일수록 엄격 (enum / range)


class PolicyRule(BaseModel):
    """단일 정책 룰 — 파라미터 단위"""
    rule_id: str = Field(default_factory=lambda: f"pr_{uuid4().hex[:12]}")
    category: PolicyCategory
    parameter: str                       # 예: "max_risk_score"
    operator: PolicyOperator
    direction: PolicyDirection
    # 주의: bool은 int의 서브클래스이므로 Pydantic Union 평가 순서상 bool을 최우선에 둔다.
    value: Union[bool, int, float, str, list[Any], dict[str, Any]]
    source_scope: Literal["global", "domain", "node"]
    source_id: str                       # 출처 식별 (예: "ORANGE_CORE", "domain:health", "node:bn_dev_01")

    @validator("direction")
    def _direction_consistent(cls, v, values):
        op = values.get("operator")
        consistent = {
            PolicyOperator.MAX: {PolicyDirection.DOWN},
            PolicyOperator.MIN: {PolicyDirection.UP},
            PolicyOperator.EXACT: {PolicyDirection.DOWN, PolicyDirection.UP, PolicyDirection.SUBSET},
            PolicyOperator.RANGE: {PolicyDirection.SUBSET},
            PolicyOperator.ENUM: {PolicyDirection.SUBSET},
            PolicyOperator.BOOLEAN: {PolicyDirection.UP, PolicyDirection.DOWN},  # ↑=true-pole / ↓=false-pole
        }
        if op and v not in consistent[op]:
            raise ValueError(f"operator {op} is incompatible with direction {v}")
        return v

    @validator("value")
    def _value_type_for_operator(cls, v, values):
        op = values.get("operator")
        if op in (PolicyOperator.MAX, PolicyOperator.MIN):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(f"operator {op} requires numeric (int/float, not bool); got {type(v).__name__}")
        elif op == PolicyOperator.RANGE:
            if not (isinstance(v, (list, tuple)) and len(v) == 2
                    and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
                    and v[0] <= v[1]):
                raise ValueError("operator range requires [lo, hi] with lo<=hi, numeric (not bool)")
        elif op == PolicyOperator.ENUM:
            if not (isinstance(v, list) and len(v) > 0):
                raise ValueError("operator enum requires non-empty list")
        elif op == PolicyOperator.BOOLEAN:
            if not isinstance(v, bool):
                raise ValueError(f"operator boolean requires bool; got {type(v).__name__}")
        return v

    def is_stricter_than(self, other: "PolicyRule") -> bool:
        """본 룰이 other보다 엄격한지 — §4 알고리즘 호출"""
        return _is_stricter(self, other)


class Policy(BaseModel):
    """정책 묶음"""
    policy_id: str = Field(default_factory=lambda: f"pol_{uuid4().hex[:12]}")
    scope: Literal["global", "domain", "node"]
    source_id: str
    rules: list[PolicyRule]
    priority: int = Field(0, description="낮을수록 우선 (global=0, domain=10, node=20)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OverrideAttempt(BaseModel):
    """거부된 override 시도 (감사 로그용)"""
    attempt_id: str = Field(default_factory=lambda: f"oa_{uuid4().hex[:12]}")
    parameter: str
    base_rule: Optional[PolicyRule] = None    # 신규 파라미터 등록 거부 시 None
    proposed_rule: PolicyRule                 # 시도된 override 룰
    reason: Literal[
        "LOOSER_DIRECTION",
        "OPERATOR_MISMATCH",
        "DIRECTION_MISMATCH",
        "TYPE_MISMATCH",
        "ABSOLUTE_LOCK_VIOLATION",
    ]
    rejected_at: datetime = Field(default_factory=datetime.utcnow)
    actor_node_id: Optional[str] = None


class ResolvedPolicy(BaseModel):
    """Policy Resolution 결과 — 07 Gate PolicyCheck의 입력"""
    node_id: str
    request_id: str
    rules: dict[str, PolicyRule]              # parameter → 최종 채택 룰
    derivation_trace: list[dict[str, Any]]    # 각 파라미터의 채택 경로 (감사 추적용)
    rejected_overrides: list[OverrideAttempt] # 거부된 override 시도
    resolved_at: datetime = Field(default_factory=datetime.utcnow)
```

> **모델 정의 순서 주의**: `OverrideAttempt`는 `ResolvedPolicy`에서 참조되므로 **반드시 먼저 선언**한다(forward reference 회피, Pydantic v1 호환).

---

## 3. 6개 카테고리 Global 기본값 (E1)

> Global 정책은 ORANGE CORE가 정본 소유. 본 표는 BN 측 기준값으로, V1 출시 시점의 합의된 baseline이다.

| 카테고리 | parameter | 기본값 | operator | direction | 설명 | SOT 근거 |
|---------|-----------|--------|----------|-----------|------|---------|
| **safety** | `max_risk_score` | 0.7 | max | ↓ | 위험 점수 상한 (0~1) | D2.0-07 PolicyCheck (V1 baseline) |
| **safety** | `content_filter_level` | 2 | min | ↑ | 콘텐츠 필터 강도 (1~5) | D2.0-07 (V1 baseline) |
| **safety** | `min_permission_level` | 1 | min | ↑ | 최소 Permission Level (값 정본 = 01 K-041) | LOCK-BN-02 |
| **safety** | `require_human_approval` | false | boolean | ↑ | true=항상 사용자 확인 (true가 strict pole) | D2.0-03 §4.1 K-042 (Line 761) |
| **quality** | `min_confidence` | 0.6 | min | ↑ | 최소 신뢰도 (0~1). `Confidence < 50%` HITL 트리거 baseline은 D2.0-03 Line 766 (MASTER_SPEC §5/§7.9 정본) | D2.0-03 Line 766 |
| **quality** | `max_hallucination_rate` | 0.10 | max | ↓ | 환각률 상한 (V1 baseline — SOT 미정) | 본 문서 V1 baseline |
| **quality** | `min_evidence_count` | 0 | min | ↑ | 응답당 최소 evidence_refs 개수 (CF-002와 정합 — 구조적 필수, 의미적 선택) | D2.1-D3 AC-D3-005 |
| **performance** | `max_response_time_ms` | 30000 | max | ↓ | 도구 호출 기본 응답 시간 상한 (30초) | D2.0-03 Line 358 |
| **performance** | `max_streaming_time_ms` | 120000 | max | ↓ | 스트리밍 응답 상한 (120초) | D2.0-03 Line 358 |
| **resource** | `max_tokens_per_request` | 4096 | max | ↓ | 요청당 토큰 상한 (V1 baseline) | 본 문서 V1 baseline |
| **resource** | `max_cost_usd_per_request` | 0.50 | max | ↓ | 요청당 비용 상한 (USD) | D2.0-03 K-044 (Line 795, V1 baseline) |
| **resource** | `max_concurrent_calls` | 3 | max | ↓ | BN당 동시 호출 상한 (per-node 호출 축 — MODULE-ARCH 결정, LOCK-BN-15 active-node 수 제약과는 직교) | 본 문서 V1 baseline (MODULE-ARCH) |
| **privacy** | `data_retention_days` | 90 | max | ↓ | 데이터 보존 기간 (일) — D2.0-06 §2.1 L1 Project 메모리 90일 baseline 정합 | D2.0-06 §2.1 Line 122 |
| **privacy** | `pii_redaction_required` | true | boolean | ↑ | PII 마스킹 필수 (true가 strict pole, ABSOLUTE_LOCK) | 03 GR_NO_PII 정합 |
| **privacy** | `cross_domain_share_allowed` | false | boolean | ↓ | 도메인 간 데이터 공유 금지 (false가 strict pole, ABSOLUTE_LOCK) | LOCK-BN-14 정합 |
| **content** | `allowed_languages` | ["ko","en"] | enum | ⊂ | 허용 언어 (확장 거부, 축소만 허용) | 본 문서 V1 baseline |
| **content** | `allowed_output_formats` | ["text","json","markdown"] | enum | ⊂ | 허용 출력 포맷 (확장 거부, 축소만 허용) | 본 문서 V1 baseline |

> **ABSOLUTE_LOCK 파라미터 (RULE 1.3 절대 변경 불가)**: `pii_redaction_required`(canonical=true), `cross_domain_share_allowed`(canonical=false). 두 파라미터는 **어떤 scope에서도 canonical 값과 다른 값으로 override 불가** — 시도 시 즉시 `ABSOLUTE_LOCK_VIOLATION`(CRITICAL)으로 거부 + 운영자 알림. 신규 등록 경로(global에 미정의 → domain/node에서 추가)에서도 canonical 값 강제 검증된다(§4.3 + §5.2).
>
> **참고**: `min_permission_level`은 **ABSOLUTE_LOCK이 아니다** — 도메인이 더 높은 최소 레벨로 stricter 강화 가능(예: BN-Trading은 5로 상향, §6.3). LOOSER 시도(예: 1→0)는 일반 stricter-only 메커니즘으로 거부된다.

---

## 4. Stricter 판정 알고리즘 (E2)

### 4.1 연산자별 판정 함수

```python
def _is_stricter(new: PolicyRule, base: PolicyRule) -> bool:
    """
    new가 base보다 더 엄격한지 판정.
    parameter, operator, direction이 일치해야 함 (불일치 → False, 거부 사유 OPERATOR_MISMATCH/DIRECTION_MISMATCH).
    """
    if new.parameter != base.parameter:
        return False
    if new.operator != base.operator:
        return False
    if new.direction != base.direction:
        return False

    op = new.operator

    # 1) max: 더 작은 값이 엄격
    if op == PolicyOperator.MAX:
        return _to_num(new.value) <= _to_num(base.value)

    # 2) min: 더 큰 값이 엄격
    if op == PolicyOperator.MIN:
        return _to_num(new.value) >= _to_num(base.value)

    # 3) exact: 동일 값만 허용 (override 무의미하나 명시적 재선언은 허용)
    if op == PolicyOperator.EXACT:
        return new.value == base.value

    # 4) range [lo, hi]: 새 범위가 기존 범위의 부분집합
    if op == PolicyOperator.RANGE:
        n_lo, n_hi = new.value
        b_lo, b_hi = base.value
        return (n_lo >= b_lo) and (n_hi <= b_hi)

    # 5) enum: 새 집합이 기존 집합의 부분집합
    if op == PolicyOperator.ENUM:
        return set(new.value).issubset(set(base.value))

    # 6) boolean: direction이 strict pole을 결정
    #    direction=↑ (UP)   → true 가 strict pole  (예: require_human_approval, pii_redaction_required)
    #    direction=↓ (DOWN) → false 가 strict pole (예: cross_domain_share_allowed)
    if op == PolicyOperator.BOOLEAN:
        strict_pole: bool = (new.direction == PolicyDirection.UP)  # True 면 true가 strict
        nv, bv = bool(new.value), bool(base.value)
        # accept 조건:
        #  (a) new 가 strict pole 에 있다 (이동 방향 = strict화 또는 이미 strict)
        #  (b) base 가 strict pole 에 없다 = 둘 다 loose pole 동일값 (no-op)
        if nv == strict_pole:
            return True
        if bv != strict_pole:
            return True   # 둘 다 loose pole — 동일값 no-op
        return False      # base 가 strict pole, new 가 loose pole → 느슨

    return False


def _to_num(v: Any) -> float:
    # bool 은 int 의 서브클래스이지만 numeric 의미가 다르므로 명시적으로 거부
    if isinstance(v, bool):
        raise TypeError(f"bool value not allowed for numeric operator: {v!r}")
    if isinstance(v, (int, float)):
        return float(v)
    raise TypeError(f"non-numeric value for max/min operator: {v!r}")
```

### 4.2 판정 진리표 요약

| operator | direction | base | new | is_stricter? | 채택? |
|---------|----------|------|-----|--------------|------|
| max | ↓ | 0.7 | 0.3 | ✅ | YES (0.3 채택) |
| max | ↓ | 0.7 | 0.9 | ❌ | NO → REJECT (LOOSER_DIRECTION) |
| max | ↓ | 0.7 | 0.7 | ✅ (동일) | YES (no-op 재선언 허용) |
| min | ↑ | 0.6 | 0.8 | ✅ | YES |
| min | ↑ | 0.6 | 0.4 | ❌ | NO → REJECT |
| range | ⊂ | [10,100] | [20,80] | ✅ | YES |
| range | ⊂ | [10,100] | [5,120] | ❌ | NO → REJECT |
| enum | ⊂ | ["ko","en","ja"] | ["ko","en"] | ✅ | YES |
| enum | ⊂ | ["ko","en"] | ["ko","en","ja"] | ❌ | NO → REJECT |
| boolean | ↑ (true=strict) | false | true | ✅ | YES (require 강화) |
| boolean | ↑ (true=strict) | true | false | ❌ | NO → REJECT (require 해제) |
| boolean | ↑ (true=strict) | true | true | ✅ (동일) | YES (no-op) |
| boolean | ↓ (false=strict) | true | false | ✅ | YES (deny 강화) |
| boolean | ↓ (false=strict) | false | true | ❌ | NO → REJECT (deny 해제) |
| boolean | ↓ (false=strict) | false | false | ✅ (동일) | YES (no-op) |
| max | ↓ | 0.7 | "0.3"(str) | TypeError | NO → REJECT (TYPE_MISMATCH, validator 단계 사전 차단) |
| max | ↓ | 0.7 | True (bool) | TypeError | NO → REJECT (TYPE_MISMATCH, `_to_num` bool 가드) |

### 4.3 절대 불변 파라미터 가드

```python
# RULE 1.3 § 절대 변경 불가 항목 — canonical 값과 다른 어떠한 override도 거부
ABSOLUTE_LOCK_CANONICAL: dict[str, Any] = {
    "pii_redaction_required":     True,    # 항상 true 유지
    "cross_domain_share_allowed": False,   # 항상 false 유지
}


def _check_absolute_lock(new: PolicyRule, base: Optional[PolicyRule]) -> Optional[str]:
    """
    base 가 없는(신규 등록) 경로에서도 canonical 값과 비교한다.
    base 가 있다면 base 값이 canonical 과 다를 가능성은 없으나(global baseline 강제), 방어적으로 둘 다 검증.
    """
    canonical = ABSOLUTE_LOCK_CANONICAL.get(new.parameter)
    if canonical is None:
        return None  # 절대 불변 대상이 아님
    if new.value != canonical:
        return "ABSOLUTE_LOCK_VIOLATION"
    if base is not None and base.value != canonical:
        # 이미 base 가 어긋나 있다면 무결성 위반 — 운영 알림
        return "ABSOLUTE_LOCK_VIOLATION"
    return None
```

> **신규 등록 경로 가드**: §5.2 PolicyResolver 는 base 가 없는 경우에도 `_check_absolute_lock(new_rule, base=None)` 을 호출하여 canonical 값을 강제한다. 즉 global 이 해당 파라미터를 정의하지 않았더라도 domain/node 가 임의 값으로 신규 등록할 수 없다.

---

## 5. Policy Resolution 4단계 파이프라인 (E2)

### 5.1 시퀀스 다이어그램

```
[1] Load Global    ─ ORANGE CORE 기본 정책 로드 (priority=0)
[2] Load Domain    ─ node_id → domain 매핑 → 해당 도메인 정책 로드 (priority=10)
[3] Load Node      ─ node_id 직접 정책 로드 (priority=20)
[4] Merge          ─ §4 stricter-only 알고리즘으로 합성
                     │
                     ├─ accept → ResolvedPolicy.rules[parameter] 갱신
                     │            + derivation_trace 기록 (어느 scope에서 어떤 값으로 채택됐는지)
                     └─ reject → OverrideAttempt 생성 + rejected_overrides 추가
                                  + Module #6 Event Log 기록 (bn.policy.override_rejected)
                                  + 07 Gate에 PolicyCheck 입력 시 reject 사실 노출
                     │
                     ▼
[5] Output         ─ ResolvedPolicy → 07 Gate PolicyCheck 선행 입력 (LOCK-BN-10)
```

### 5.2 PolicyResolver 의사 코드

```python
class PolicyResolver:
    def __init__(self, policy_store, audit_logger, gate_client):
        self.store = policy_store
        self.audit = audit_logger
        self.gate = gate_client      # 07 Gate 기록용

    async def resolve(self, node_id: str, request_id: str) -> ResolvedPolicy:
        # [1] Global
        global_pol = await self.store.load(scope="global", source_id="ORANGE_CORE")

        # [2] Domain
        domain = await self.store.get_domain_of(node_id)
        domain_pol = await self.store.load(scope="domain", source_id=f"domain:{domain}")

        # [3] Node
        node_pol = await self.store.load(scope="node", source_id=f"node:{node_id}")

        # [4] Merge
        resolved: dict[str, PolicyRule] = {}
        trace: list[dict] = []
        rejected: list[OverrideAttempt] = []

        # 4-a) global을 baseline으로
        for r in global_pol.rules:
            resolved[r.parameter] = r
            trace.append({"parameter": r.parameter, "scope": "global", "value": r.value})

        # 4-b) domain → node 순으로 stricter-only 적용
        for pol in (domain_pol, node_pol):
            for new_rule in pol.rules:
                base = resolved.get(new_rule.parameter)

                # (가드 1) 절대 불변 — base 유무 무관, canonical 값과 다르면 즉시 거부
                lock_err = _check_absolute_lock(new_rule, base)
                if lock_err:
                    rejected.append(OverrideAttempt(
                        parameter=new_rule.parameter, base_rule=base, proposed_rule=new_rule,
                        reason=lock_err, actor_node_id=node_id,
                    ))
                    await self._emit_audit(node_id, request_id, new_rule, base, lock_err)
                    continue

                # (분기 1) 신규 파라미터 — base 없음, canonical 가드 통과 후 채택
                if base is None:
                    resolved[new_rule.parameter] = new_rule
                    trace.append({
                        "parameter": new_rule.parameter, "scope": pol.scope,
                        "value": new_rule.value, "decision": "added",
                    })
                    await self._emit_info(node_id, request_id, new_rule, "MISSING_GLOBAL_BASELINE")
                    continue

                # 타입/연산자/방향 일치 검증
                if (new_rule.operator != base.operator
                    or new_rule.direction != base.direction):
                    reason = "OPERATOR_MISMATCH" if new_rule.operator != base.operator else "DIRECTION_MISMATCH"
                    rejected.append(OverrideAttempt(
                        parameter=new_rule.parameter, base_rule=base, proposed_rule=new_rule,
                        reason=reason, actor_node_id=node_id,
                    ))
                    await self._emit_audit(node_id, request_id, new_rule, base, reason)
                    continue

                # stricter 판정
                try:
                    stricter = new_rule.is_stricter_than(base)
                except TypeError:
                    rejected.append(OverrideAttempt(
                        parameter=new_rule.parameter, base_rule=base, proposed_rule=new_rule,
                        reason="TYPE_MISMATCH", actor_node_id=node_id,
                    ))
                    await self._emit_audit(node_id, request_id, new_rule, base, "TYPE_MISMATCH")
                    continue

                if stricter:
                    resolved[new_rule.parameter] = new_rule
                    trace.append({
                        "parameter": new_rule.parameter, "scope": pol.scope,
                        "value": new_rule.value, "decision": "accepted_stricter",
                        "previous_value": base.value, "previous_scope": base.source_scope,
                    })
                    await self._emit_info(node_id, request_id, new_rule, "ACCEPTED_STRICTER")
                else:
                    rejected.append(OverrideAttempt(
                        parameter=new_rule.parameter, base_rule=base, proposed_rule=new_rule,
                        reason="LOOSER_DIRECTION", actor_node_id=node_id,
                    ))
                    await self._emit_audit(node_id, request_id, new_rule, base, "LOOSER_DIRECTION")

        result = ResolvedPolicy(
            node_id=node_id, request_id=request_id,
            rules=resolved, derivation_trace=trace, rejected_overrides=rejected,
        )

        # [4-c] Resolution 완료 INFO 이벤트
        await self.audit.emit({
            "event_type": "bn.policy.resolved",
            "node_id": node_id,
            "request_id": request_id,
            "rules_count": len(resolved),
            "rejected_count": len(rejected),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        # [5] 07 Gate 선행 입력 등록 (LOCK-BN-10)
        await self.gate.register_policy_input(request_id, result)

        return result

    async def _emit_audit(self, node_id, request_id, new, base, reason):
        # base 가 None 일 수 있다 — 신규 등록 경로에서 ABSOLUTE_LOCK 위반이 발생한 경우
        event_type = (
            "bn.policy.absolute_lock_violation"
            if reason == "ABSOLUTE_LOCK_VIOLATION"
            else "bn.policy.override_rejected"
        )
        await self.audit.emit({
            "event_type": event_type,
            "node_id": node_id,
            "request_id": request_id,
            "parameter": new.parameter,
            "operator": new.operator.value,
            "base_value": base.value if base is not None else None,
            "base_scope": base.source_scope if base is not None else None,
            "attempted_value": new.value,
            "attempted_scope": new.source_scope,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    async def _emit_info(self, node_id, request_id, rule, info_reason):
        """채택/추가/리졸브 등 INFO-수준 감사 (MISSING_GLOBAL_BASELINE 포함)."""
        event_type_map = {
            "MISSING_GLOBAL_BASELINE": "bn.policy.override_accepted",
            "ACCEPTED_STRICTER":       "bn.policy.override_accepted",
        }
        await self.audit.emit({
            "event_type": event_type_map[info_reason],
            "node_id": node_id,
            "request_id": request_id,
            "parameter": rule.parameter,
            "value": rule.value,
            "scope": rule.source_scope,
            "info_reason": info_reason,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
```

### 5.3 07 Gate 연동 (LOCK-BN-10)

| 단계 | 본 문서 책임 | 07 Gate 책임 |
|------|------------|------------|
| Resolution | `ResolvedPolicy` 생성 | — |
| 등록 | `gate.register_policy_input(request_id, ResolvedPolicy)` | 입력 수신, request_id 묶음 |
| 판정 | — | PolicyCheck 평가 (resolved.rules 기준 + 07 도메인 정책 결합) |
| Execute 진입 | — | PolicyCheck=allow 일 때만 BN Execute 진입 허용 |
| 거부 시 | rejected_overrides 노출 | PolicyCheck=deny + reason 전파 → 호출자 응답에 포함 |

> **금지**: 본 문서의 PolicyResolver 결과를 BN 내부 if문이 직접 소비하여 Execute 단계로 진입시키는 패턴은 LOCK-BN-10 위반. 반드시 07 Gate에 register 후 Gate 결과를 기다린다.

---

## 6. 도메인별 Override 예시 (E8)

### 6.1 BN-Health (의료 — 엄격 강화)

```yaml
scope: domain
source_id: domain:health
priority: 10
rules:
  - {category: safety,  parameter: max_risk_score,         operator: max,     direction: "↓", value: 0.3}
  - {category: safety,  parameter: content_filter_level,   operator: min,     direction: "↑", value: 4}
  - {category: safety,  parameter: require_human_approval, operator: boolean, direction: "↑", value: true}
  - {category: quality, parameter: min_confidence,         operator: min,     direction: "↑", value: 0.85}
  - {category: quality, parameter: min_evidence_count,     operator: min,     direction: "↑", value: 2}
  - {category: privacy, parameter: data_retention_days,    operator: max,     direction: "↓", value: 30}
```

| 파라미터 | Global | Domain | Effective | 판정 |
|---------|--------|--------|-----------|------|
| max_risk_score | 0.7 | **0.3** | 0.3 | ✅ accepted_stricter |
| content_filter_level | 2 | **4** | 4 | ✅ accepted_stricter |
| require_human_approval | false | **true** | true | ✅ accepted_stricter (true=strict pole, ↑) |
| min_confidence | 0.6 | **0.85** | 0.85 | ✅ accepted_stricter |
| min_evidence_count | 0 | **2** | 2 | ✅ accepted_stricter |
| data_retention_days | 90 | **30** | 30 | ✅ accepted_stricter |

### 6.2 BN-CodeEngine (혼합 — 일부 거부)

```yaml
scope: node
source_id: node:bn_code_engine
priority: 20
rules:
  - {category: quality,  parameter: min_confidence,         operator: min, direction: "↑", value: 0.7}
  - {category: resource, parameter: max_tokens_per_request, operator: max, direction: "↓", value: 8192}   # ❌ 느슨
  - {category: resource, parameter: max_cost_usd_per_request, operator: max, direction: "↓", value: 0.30}
```

| 파라미터 | Base (Global) | Node 시도 | 결과 | 사유 |
|---------|---------------|----------|------|------|
| min_confidence | 0.6 | **0.7** | ✅ 0.7 채택 | accepted_stricter |
| max_tokens_per_request | 4096 | **8192** | ❌ **REJECT** | LOOSER_DIRECTION (max는 작은 값이 엄격) |
| max_cost_usd_per_request | 0.50 | **0.30** | ✅ 0.30 채택 | accepted_stricter |

→ rejected_overrides에 1건 기록, Module #6 Event Log `bn.policy.override_rejected` 1건 발생.

### 6.3 BN-Trading (금융 — 보수적 승인)

```yaml
scope: domain
source_id: domain:trading
priority: 10
rules:
  - {category: safety,   parameter: min_permission_level,    operator: min,     direction: "↑", value: 5}    # 금융 노드 전용
  - {category: safety,   parameter: require_human_approval,  operator: boolean, direction: "↑", value: true}
  - {category: resource, parameter: max_concurrent_calls,    operator: max,     direction: "↓", value: 1}    # 동시 1건만
  - {category: privacy,  parameter: pii_redaction_required,  operator: boolean, direction: "↑", value: true} # 유지 (no-op, canonical=true)
```

→ 모든 룰 accepted. `min_permission_level=5`는 K-041 Level 5(금융) 강제 — 01 Permission Matrix와 정렬.

### 6.4 BN-Content (콘텐츠 — 언어/포맷 축소)

```yaml
scope: node
source_id: node:bn_content_kr
priority: 20
rules:
  - {category: content, parameter: allowed_languages,       operator: enum, direction: "⊂", value: ["ko"]}
  - {category: content, parameter: allowed_output_formats,  operator: enum, direction: "⊂", value: ["markdown"]}
  - {category: content, parameter: allowed_output_formats,  operator: enum, direction: "⊂", value: ["text","json","markdown","html"]}  # ❌ 확장 시도
```

| 파라미터 | Base | Node 시도 | 결과 |
|---------|------|----------|------|
| allowed_languages | ["ko","en"] | **["ko"]** | ✅ accepted (subset) |
| allowed_output_formats | ["text","json","markdown"] | **["markdown"]** | ✅ accepted (subset) |
| allowed_output_formats(2차) | ["markdown"] (방금 채택) | **[..."html"]** | ❌ REJECT — html 추가는 superset (LOOSER_DIRECTION) |

---

## 7. 에러 코드 + 복구 전략 (E5)

| error_code | 발생 조건 | severity | 복구 전략 |
|-----------|----------|---------|-----------|
| `LOOSER_DIRECTION` | new가 base보다 느슨 | MEDIUM | reject + audit. 호출자에게 base 값 사용 통지. 도메인 정책 작성자에 알림. |
| `OPERATOR_MISMATCH` | new.operator ≠ base.operator | HIGH | reject + audit. 정책 정의 오류 — 작성자 수정 필요. |
| `DIRECTION_MISMATCH` | new.direction ≠ base.direction | HIGH | reject + audit. 정책 정의 오류. |
| `TYPE_MISMATCH` | 수치 연산자에 비수치 값 | HIGH | reject + audit. Pydantic validator 단계에서 사전 차단 권장. |
| `ABSOLUTE_LOCK_VIOLATION` | RULE 1.3 절대 불변 파라미터 변경 시도 | CRITICAL | 즉시 reject + audit + 운영자 알림 (페이지). 시도자 노드 격리 검토. |
| `MISSING_GLOBAL_BASELINE` | global에 정의 없는 파라미터에 대한 domain/node 룰 | HIGH | reject + audit. global baseline 미등록 키는 비교 base 부재 → LOCK-BN-17 "Only Stricter" 적용 불가이므로 거부. ORANGE CORE Policy Registry에 global 등록 후에만 domain/node 사용 가능. |
| `RESOLVER_TIMEOUT` | PolicyResolver 처리 시간 초과 | HIGH | fallback: global-only ResolvedPolicy 반환 + 07 Gate에 fallback 표시. |

---

## 8. 보안 + 감사 로그 스키마 (E7)

### 8.1 감사 이벤트 네임스페이스 (Module #6 Event Log)

| event_type | 발생 시점 | emitter | 페이로드 |
|-----------|----------|---------|---------|
| `bn.policy.resolved` | resolve() 종료 시 | resolver inline | node_id, request_id, rules_count, rejected_count, timestamp |
| `bn.policy.override_accepted` | stricter 채택 또는 신규 등록 시 | `_emit_info` | node_id, request_id, parameter, value, scope, info_reason ∈ {ACCEPTED_STRICTER, MISSING_GLOBAL_BASELINE}, timestamp |
| `bn.policy.override_rejected` | LOOSER/MISMATCH/TYPE_MISMATCH 거부 | `_emit_audit` | node_id, request_id, parameter, operator, base_value, base_scope, attempted_value, attempted_scope, reason, timestamp |
| `bn.policy.absolute_lock_violation` | ABSOLUTE_LOCK_VIOLATION 거부 | `_emit_audit` | (override_rejected와 동일 페이로드, base_value/base_scope는 신규 등록 경로에서 null 가능) — **운영자 알림 트리거** |

### 8.2 거부 이벤트 JSON 예시

```json
{
  "event_type": "bn.policy.override_rejected",
  "node_id": "bn_code_engine",
  "request_id": "req_01H8...",
  "parameter": "max_tokens_per_request",
  "operator": "max",
  "base_value": 4096,
  "base_scope": "global",
  "attempted_value": 8192,
  "attempted_scope": "node",
  "reason": "LOOSER_DIRECTION",
  "timestamp": "2026-04-07T10:00:00Z"
}
```

### 8.3 보안 정책

1. **PolicyResolver 단독 실행 금지** — BN 프로세스 내부가 아닌 ORANGE CORE 측 PolicyEngine 내부에서 실행. BN은 ResolvedPolicy를 **읽기 전용**으로 수신.
2. **rejected_overrides 무손실 전파** — 07 Gate PolicyCheck 응답에 rejected_count > 0이면 호출자 응답의 `meta.policy_warnings`에 포함.
3. **Resolver 무결성 해시** — PolicyResolver 코드 해시를 정기 verify (V2+). 변조 탐지 시 운영자 알림.
4. **시크릿 차단 정렬** — 본 문서의 `pii_redaction_required`/`cross_domain_share_allowed`는 03 Guardrail의 `GR_NO_PII`/`GR_NO_SECRETS` 규칙과 정렬 (둘 중 하나라도 false/disable 시 양쪽 모두 reject).

---

## 9. 의존성 (E3)

### 9.1 상위 (본 문서 입력)
- **D2.0-03 §4.1** (Lines 732~736) — "안전한 방향만" 원칙 SOT 정본
- **D2.0-01 RULE 1.3 §4.2** — 정책 상속 체인 LOCK
- **ORANGE CORE PolicyEngine** — Global 정책 정본 + PolicyResolver 실행 주체
- **D2.0-07 §4.3.2 / S7E-050 ApprovalManager** — Approval 정책 (LOCK-BN-19)

### 9.2 하위 (본 문서 출력 소비)
- **07 Gate PolicyCheck** — `ResolvedPolicy` 선행 입력 (LOCK-BN-10)
- **모든 BN 실행 경로** — Execute 단계 진입 전 ResolvedPolicy 적용

### 9.3 연관 (정합 대상)
- **`01_permission-matrix/_index.md`** — `min_permission_level` 파라미터의 값 정본은 K-041. Dynamic Adjuster의 런타임 레벨 하향과 본 문서의 stricter-only 합성은 동일 방향(엄격화) 정렬.
- **`03_template-injection/_index.md` §3.3 / §4.1** — Guardrail merge의 stricter-only(`block > rewrite > warn`, severity 상승 우선)와 본 문서의 stricter-only 합성(numeric/enum/boolean strict pole)은 동일 LOCK-BN-17 적용. boolean strict pole은 파라미터별 의미에 따라 ↑(true=strict, 예: `pii_redaction_required`) 또는 ↓(false=strict, 예: `cross_domain_share_allowed`).
- **`05_memory-sharing/_index.md`** — `cross_domain_share_allowed=false` 정렬, `data_retention_days`의 D2.0-06 저장 계층 TTL 정합.
- **`07_mcp-bridge/_index.md`** — MCP 외부 클라이언트의 권한/Rate-limit 결정도 ResolvedPolicy 결과를 참조 (1-4 진행 시 정합 검증).

---

## 10. 단위 테스트 케이스 (E4)

| TC ID | 시나리오 | 입력 | 기대 결과 |
|-------|---------|------|----------|
| TC-PO-01 | max stricter accept | base max=0.7, new max=0.3 | accepted_stricter, resolved=0.3 |
| TC-PO-02 | max looser reject | base max=0.7, new max=0.9 | reject, reason=LOOSER_DIRECTION |
| TC-PO-03 | min stricter accept | base min=0.6, new min=0.8 | accepted_stricter, resolved=0.8 |
| TC-PO-04 | enum subset accept | base ["ko","en","ja"], new ["ko","en"] | accepted_stricter |
| TC-PO-05 | enum superset reject | base ["ko","en"], new ["ko","en","ja"] | reject, reason=LOOSER_DIRECTION |
| TC-PO-06 | range subset accept | base [10,100], new [20,80] | accepted_stricter |
| TC-PO-07 | boolean ↑ true-pole 강화 | base `require_human_approval=false`(↑), new=true | accepted_stricter (true=strict pole, require 강화) |
| TC-PO-07b | boolean ↑ true-pole 해제 거부 | base `require_human_approval=true`(↑), new=false | reject, reason=LOOSER_DIRECTION |
| TC-PO-07c | boolean ↓ false-pole 강화 | base `cross_domain_share_allowed=true`(↓), new=false | accepted_stricter (false=strict pole, deny 강화) |
| TC-PO-07d | boolean ↓ false-pole 해제 거부 | base `cross_domain_share_allowed=false`(↓), new=true | reject, reason=ABSOLUTE_LOCK_VIOLATION (canonical=false 강제) |
| TC-PO-08 | absolute lock 변경 시도 | base `pii_redaction_required=true`(canonical), new=false | reject, reason=ABSOLUTE_LOCK_VIOLATION + `bn.policy.absolute_lock_violation` emit + 운영자 알림 |
| TC-PO-08b | absolute lock 신규 등록 우회 | global 미정의, node가 `pii_redaction_required=false` 신규 등록 시도 | reject, reason=ABSOLUTE_LOCK_VIOLATION (base=None 경로 가드 검증, base_value=null) |
| TC-PO-09 | operator mismatch | base max=0.7, new operator=min value=0.3 | reject, reason=OPERATOR_MISMATCH |
| TC-PO-10 | type mismatch (string) | base max=0.7 (float), new value="0.3" (str) | Pydantic `_value_type_for_operator` validator 단계에서 ValidationError (사전 차단). 우회 시 `_to_num` TypeError → reason=TYPE_MISMATCH |
| TC-PO-10b | type mismatch (bool→numeric) | base max=0.7 (float), new value=True (bool) | Pydantic validator에서 차단 (`bool not allowed for max/min`). 우회 시 `_to_num` 가드에서 TypeError |
| TC-PO-10c | range value 형식 검증 | operator=range, value=42 (단일값) | Pydantic validator ValidationError (`range requires [lo, hi]`) |
| TC-PO-11 | 4단계 파이프라인 정합 | global+domain+node 모두 채택 가능 | derivation_trace 3건+, 최종 가장 엄격한 값, ACCEPTED_STRICTER 정보 emit |
| TC-PO-12 | 07 Gate register 호출 검증 | resolve() 호출 1회 | `gate.register_policy_input` 1회 호출 (mock 검증) |
| TC-PO-13 | rejected_overrides 비손실 | 거부 3건 발생 | ResolvedPolicy.rejected_overrides 길이=3, 각 reason 보존 |
| TC-PO-14 | MISSING_GLOBAL_BASELINE 정보 emit | global 미정의 파라미터(절대 불변 아님)를 domain이 신규 등록 | accept (decision=added) + `bn.policy.override_accepted` info_reason=MISSING_GLOBAL_BASELINE emit |
| TC-PO-15 | direction validator | rule operator=max, direction=↑ 생성 시도 | Pydantic validator ValidationError (`operator max incompatible with direction ↑`) |

---

## 11. 성능 기준 (E6)

| 지표 | 기준값 | 측정 방법 |
|------|--------|----------|
| Resolve latency p50 | < 5 ms | Resolver 단독 (Store 캐시 hit 가정) |
| Resolve latency p99 | < 20 ms | Store cache miss 포함 |
| Audit emit latency | < 2 ms (async) | fire-and-forget, 본문 처리 비차단 |
| Throughput | ≥ 1000 resolve/sec | LOCK-BN-15 (동시 BN 3개) 기준 충분 |
| Memory footprint per ResolvedPolicy | < 8 KB | rules 17개 baseline + trace + rejected |
| Resolver timeout fallback 비율 | < 0.1% | RESOLVER_TIMEOUT → global-only fallback |

---

## 12. V1/V2/V3 Phase 매핑 (E9, R6 준수)

> Phase **일정**은 Part2 정본. 본 절은 **scope 정의**만 기술.

| Phase | scope |
|-------|-------|
| **V1** | 6개 카테고리 17개 baseline 파라미터 + 5종 operator (max/min/exact/enum/boolean — `range`는 모델 정의만, baseline 미사용). 3 BN(Dev/Research/Content) 도메인 정책 정의. PolicyResolver 단일 인스턴스. ABSOLUTE_LOCK 가드 활성. `_emit_audit`·`_emit_info` 4종 event_type 활성. |
| **V2** | `range` operator 활성화, 10 BN 도메인 정책 확장 (Health/Trading/CodeEngine 등). PolicyResolver Store 캐시 도입. Resolver 무결성 해시 verify. rejected_overrides 호출자 응답 자동 첨부. RESOLVER_TIMEOUT fallback 활성. |
| **V3** | 사용자 정의 파라미터 등록 API. 도메인 간 정책 상속 그래프(지금은 1차원, V3는 다중 부모). Policy A/B 시뮬레이션 도구. |

---

## 13. 교차 참조 요약

| 참조 대상 | 위치 | 관계 |
|----------|------|------|
| D2.0-03 §4.1 | SOT | 본 문서 SOT 정본 (Lines 732~736) |
| D2.0-01 RULE 1.3 §4.2 | SOT | 상속 체인 LOCK |
| 01 Permission Matrix | `01_permission-matrix/` | `min_permission_level` 파라미터 값 정본 = K-041, Dynamic Adjuster와 stricter-only 정렬 |
| 03 Template Injection | `03_template-injection/` §3.3/§4.1 | Guardrail merge stricter-only(`block>rewrite>warn`, severity↑) 와 본 문서 numeric/enum/boolean stricter-only 가 동일 LOCK-BN-17 정렬 |
| 05 Memory Sharing | `05_memory-sharing/` | `cross_domain_share_allowed=false`, `data_retention_days` 정합 |
| 07 MCP Bridge | `07_mcp-bridge/` (1-4) | MCP 클라이언트 권한/Rate-limit이 ResolvedPolicy 참조 — 1-4 완료 시 정합 검증 |
| 07 Gate (D2.0-07) | SOT | LOCK-BN-10 — ResolvedPolicy → PolicyCheck 선행 입력 |
| Module #6 Event Log | D2.0-06 | `bn.policy.*` 네임스페이스 영속화 |

---

## 14. 변경 요약

### 14.1 v1.0 → v2.0 (2026-04-07 1차)

| 항목 | v1.0 (DRAFT) | v2.0 |
|------|--------------|------|
| 카테고리 baseline | 8 항목 | **17 항목** (boolean 3건 + permission/cost/concurrent 등 추가) |
| operator 종류 | max/min/exact/range/enum | + **boolean**, direction validator 추가 |
| Resolution 알고리즘 | 5줄 의사 코드 | **PolicyResolver 클래스 + 4단계 파이프라인 + 07 Gate 등록** |
| 거부 사유 | 1종 (LOOSER_DIRECTION) | **7종** (+ OPERATOR/DIRECTION/TYPE_MISMATCH, ABSOLUTE_LOCK, MISSING_BASELINE, RESOLVER_TIMEOUT) |
| 도메인 예시 | 2건 (Health/CodeEngine) | **4건** (+ Trading/Content) |
| 절대 불변 파라미터 | 미정의 | **ABSOLUTE_LOCK_PARAMETERS** + 가드 함수 |
| 감사 로그 | 1 JSON 예시 | **4 event_type + 운영자 알림 트리거 정의** |
| 테스트 케이스 | 0 | **TC-PO-01~13 (13건)** |
| 성능 기준 | 미정의 | **6 지표** |
| Phase 매핑 | 미정의 | **V1/V2/V3 scope** (R6 준수) |
| 정본 소유 경계 | 모호 | **Permission/Guardrail/Storage 정본 위임 명시** |

### 14.2 v2.0 → v2.1 (2026-04-07 재검증 패스)

> 1-3 산출물 미세 검증 결과 다음 결함 8종을 수정.

| # | 결함 | 위치 | 수정 |
|---|------|------|------|
| F1 | **Boolean direction `⊘` 의미 충돌** — `require_human_approval`(true=strict)와 `cross_domain_share_allowed`(false=strict)는 반대 pole이지만 단일 `⊘` 라벨로는 구분 불가 | §2 enum, §4.1 알고리즘, §3 baseline, §6 예시 | `⊘` 제거. boolean도 `↑`(true=strict) / `↓`(false=strict) 두 방향 사용. validator 갱신, `_is_stricter` boolean 분기 재설계 (strict_pole 변수) |
| F2 | **Pydantic Union 평가 순서 버그** — `Union[float, int, str, bool, ...]`에서 `bool`이 `int` 뒤에 있어 `True` 값이 `1`로 coerce | §2 PolicyRule.value | `Union[bool, int, float, str, list, dict]`로 재정렬 (bool 최우선) |
| F3 | **`_to_num()` bool subclass 누수** — `isinstance(True, int)==True`로 numeric 연산자에 bool이 통과 | §4.1 `_to_num` | bool 명시적 거부 가드 추가 |
| F4 | **ABSOLUTE_LOCK 신규 등록 우회** — global이 절대 불변 파라미터를 정의하지 않으면 domain/node가 임의 값으로 신규 등록 가능했음 | §4.3 + §5.2 resolver | `ABSOLUTE_LOCK_CANONICAL` dict 도입, `_check_absolute_lock(new, base=None)` 에서도 canonical 검증. resolver 4-b 루프에서 절대 불변 가드를 신규/기존 분기 **이전**에 우선 적용 |
| F5 | **잘못된 SOT line/section 참조** — `D2.0-03 §3.5.4`(존재 안 함), `max_hallucination_rate→§4.1`(섹션 무관), `D2.0-06 §2.1 L1`(line 미지정) | §3 baseline 표 SOT 근거 열 | 모두 실제 line으로 교정: response/streaming → Line 358, hallucination → V1 baseline 표기, retention → D2.0-06 §2.1 Line 122, K-042 → Line 761, K-044 → Line 795 |
| F6 | **§3 footnote의 `min_permission_level` 잘못된 ABSOLUTE_LOCK 분류** — Trading 예시는 1→5 stricter override를 허용함에도 footnote는 "어떤 scope에서도 override 불가"로 모순 표기 | §3 footnote | footnote에서 `min_permission_level` 제거 + 별도 참고 박스로 stricter override 허용임을 명시 |
| F7 | **Pydantic v1 forward ref** — `ResolvedPolicy.rejected_overrides: list["OverrideAttempt"]`가 v1에서 `update_forward_refs()` 미호출 시 unresolved | §2 모델 정의 순서 | `OverrideAttempt`를 `ResolvedPolicy` **이전**에 선언하여 forward ref 자체 회피 |
| F8 | **operator-value 타입 검증 부재** — `operator=range`에 단일 값, `operator=boolean`에 문자열 등 잘못된 조합이 Pydantic 단계에서 차단되지 않음 | §2 PolicyRule | `@validator("value")` `_value_type_for_operator` 추가 (max/min/range/enum/boolean 각각 타입·구조 검증) |

**v2.1 부수 변화**:
- §4.2 진리표에 `direction` 컬럼 추가, boolean 6 케이스(↑/↓ × accept/reject/no-op) 전부 명시
- §4.3 ABSOLUTE_LOCK 가드에 base=None 신규 등록 경로 주석 + canonical 무결성 방어 검증 추가
- §5.2 resolver 루프 순서 재구성: `_check_absolute_lock` → `base is None` 분기 → `operator/direction mismatch` → `_is_stricter` (모든 경로에서 absolute lock이 최우선)
- §5.2 `_emit_audit`에 `base=None` 안전 처리 + ABSOLUTE_LOCK_VIOLATION 시 `bn.policy.absolute_lock_violation` event_type 자동 분기
- §5.2 `_emit_info` 신설 — `MISSING_GLOBAL_BASELINE` / `ACCEPTED_STRICTER` INFO 이벤트 emit
- §5.2 resolver 종료 시 `bn.policy.resolved` inline emit (rules_count, rejected_count) — §8.1 표와 정합
- §3 baseline 표의 `data_retention_days` SOT 근거를 D2.0-06 §2.1 Line 122 (L1 90일 baseline)로 정밀화
- `OverrideAttempt.base_rule` 타입을 `Optional[PolicyRule]`로 완화 (신규 등록 거부 시 base 없음 케이스 지원)
- §8.1 emitter 컬럼 추가 — 각 event_type을 어느 함수가 생성하는지 명시
- §10 TC 13건 → **21건** (07b/07c/07d 추가 boolean 케이스, 08b 신규 등록 ABSOLUTE_LOCK, 10b/10c 추가 type validator, 14 MISSING_GLOBAL_BASELINE, 15 direction validator)
- §12 V1 operator 표기 수정 — "4종" → "5종(max/min/exact/enum/boolean)" 으로 정확화 (range는 V2)
- §9.3 / §13 03 Template Injection 교차참조 설명에서 outdated `boolean stricter (false=deny)` 표현을 strict pole 양방향 표기로 갱신

---

*정본 소유: 06_policy-overrides/_index.md → "Only Stricter" 알고리즘 (연산자별 6종) + Policy Resolution 4단계 파이프라인 + 6 카테고리 17 baseline + 4 도메인 Override 예시 + ABSOLUTE_LOCK 가드 + 7종 거부 사유 + 4 이벤트 감사 로그*
