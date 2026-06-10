# Permission Matrix — K-041 / K-045 / K-046 L3

> **정본 소유**: #13 Agent-Protocol-Interoperability / 06_autonomy-safety
> **레벨**: L3 (구현 상세)
> **버전**: v1.0 (2026-04-11, P1-2)
> **담당 K-ID**: K-041 (에이전트 권한 매트릭스), K-045 (롤백/되돌리기), K-046 (설명가능성)
> **LOCK 참조**: LOCK-AP-02 (Permission Level 0~5), LOCK-AP-05 (Lead + max 2 Sub), LOCK-AP-10 (HITL Confidence < 50%)
> **상태**: APPROVED — Phase 1 (V1)

---

## §0. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 이유 |
|-----------|------|----------|
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §3.4 | LOCK-AP-02·AP-05·AP-10 원본 값 |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §B (B.1~B.3) | 자율성 레벨 L0~L4 정의 + 허용 작업 매트릭스 |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §C (C.2~C.4) | SafetyGuardrail/HumanInterventionRequest 스키마 |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §7.3.2 | Agent Teams 방식 C 요약 (RBAC 연결) |
| `06_autonomy-safety/_index.md` | 담당 K-ID 표 | K-041·K-045·K-046 V1 스코프 |
| `06_autonomy-safety/guardrail_rules.md` | §§ (본 세션 동반 산출) | SG-001~SG-010, HITL 실행 흐름 |
| `06_autonomy-safety/agent_mode_autonomy_mapping.md` | §2 | Agent Mode(LOCK-A2A-08) ↔ Autonomy Level 매핑 |
| `01_framework-adapters/langgraph_adapter.md` | §3 EscalationPayload / §5.3 GatePolicy | EscalationPayload / GatePolicy 타입 정합 |
| `01_framework-adapters/autogen_adapter.md` | §10 | EscalationPayload I-19/I-20 target_channel 정합 |
| `01_framework-adapters/crewai_adapter.md` | §4 register_function permission | Permission Level 사용 사례 |
| `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` | K-041, K-045, K-046 | 원본 요구사항 |
| `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | HITL I-19, 자율성 | HITL I-19 채널 원본 |

---

## §1. Purpose & Scope

### 1.1 Purpose

본 문서는 VAMOS 에이전트가 수행 가능한 **작업의 권한 경계 (K-041)**, **작업 결과의 되돌리기 메커니즘 (K-045)**, **결정 과정의 설명가능성 (K-046)** 3 축을 L3 수준에서 정의한다. 세 축은 동일한 런타임 컴포넌트 `PermissionEnforcer` 로 집약되어 평가된다.

### 1.2 Scope

- **포함**: Permission Level 0~5 정의, 레벨×작업 카테고리 매트릭스, 승인 흐름, 롤백 스냅샷/트랜잭션 로그/복원 절차, 설명 생성 파이프라인, I-19/I-20 에스컬레이션 연결, Phase 2 통합 테스트 힌트
- **제외 (Phase 2 이후)**: K-047 자기진화 안전 가드레일 (V2), K-048 에이전트 윤리 프레임워크 (V3), Prod 환경 Rollback 오케스트레이션 세부(Tier 4 배포 도메인 소유)

### 1.3 세션 간 인터페이스 cross-check

| 대상 산출물 | 확인 항목 | 결과 |
|-------------|----------|------|
| `langgraph_adapter.md` §3 `GatePolicy.confidence_min=0.5` | LOCK-AP-10 기준 일치 | PASS |
| `langgraph_adapter.md` §3 `GatePolicy.escalate_to: "I-19"\|"I-20"` | 본 문서 HITL/에스컬레이션 채널 일치 | PASS |
| `autogen_adapter.md` §10 `EscalationPayload.target_channel: Literal["I-19","I-20"]` | 본 문서 EscalationPayload 구조 일치 | PASS |
| `autogen_adapter.md` §11 log nested `error/context/recovery` + `trace_id` | 본 문서 §8 로깅 포맷 일치 | PASS |
| `crewai_adapter.md` register_function permission | Permission Level 사용 시 LOCK-AP-02 참조 | PASS |
| `guardrail_rules.md` SG-009 `result.confidence < 0.5` → HITL | LOCK-AP-10 트리거와 일치 | PASS |

---

## §2. Permission Level 0~5 완전 매트릭스 (K-041)

> **LOCK 참조 (출처: §3.4 LOCK-AP-02)**: Permission Level 0~5 (읽기→금융) — 재정의 금지. 본 절은 LOCK 원본을 **참조 해석**만 한다.

### 2.1 레벨 정의

| Level | 이름 | 핵심 범위 | 기본 자율성 바인딩 | 승인 흐름 |
|-------|------|----------|-------------------|----------|
| **0** | `READ_ONLY` | 정보 조회, 검색, 요약 (부작용 0) | L0~L4 공통 허용 | Pre-check만 |
| **1** | `READ_WRITE_LOCAL` | 에이전트 로컬 작업공간 파일 생성 (STEP7-K Level 1; 수정은 Level 2/§V2.1) | L1 이상 | Pre-check + 최초 1회 사용자 고지 |
| **2** | `EXEC_SANDBOX` | 샌드박스(K-043) 내부 코드 실행, 내부 도구 호출 | L2 이상 | Pre-check + 비용 가드(SG-001) |
| **3** | `EXTERNAL_API` | 외부 API 호출, 이메일/메시지 발송 준비 | L3 이상 (R-13-1 HITL) | HITL 1회 승인 + per-call 로깅 |
| **4** | `IRREVERSIBLE_SIDE_EFFECTS` | 비가역 외부 상태 변경 (이메일 발송, 파일 배포, 메시지 채널 전파) | L3 조건부 / L4 자동 | HITL 승인 + SG-010 post-action 로그 |
| **5** | `FINANCIAL_TX` | 금융/결제/계약 트랜잭션 | L4 only + Ask | HITL **강제** + 이중 승인 + 감사 로그 |

> **주**: Level 표기는 LOCK-AP-02 원문 "0~5 (읽기→금융)" 을 위 6개 범주로 고정한다. 레벨 명칭은 내부 식별자이며 재번호 금지.

### 2.2 작업 카테고리 × Permission Level 매트릭스 (§B.3 cross-map)

> **정본 소유**: §B.3 허용 작업 매트릭스는 자율성 **레벨 L0~L4** 축, 본 §2.2는 **Permission Level 0~5** 축. 두 축은 §2.3 에서 교차 매핑한다.

| 작업 카테고리 (§B.3 정본) | P0 READ | P1 WRITE_LOCAL | P2 EXEC_SANDBOX | P3 EXTERNAL | P4 IRREVERSIBLE | P5 FINANCIAL |
|---------------------------|:-------:|:--------------:|:---------------:|:-----------:|:---------------:|:------------:|
| 정보 조회/검색 | YES | YES | YES | YES | YES | YES |
| 파일 생성 | NO | YES | YES | YES | YES | YES |
| 파일 수정 | NO | YES | YES | YES | YES | YES |
| 코드 실행 | NO | NO | YES | YES | YES | YES |
| 외부 API 호출 | NO | NO | NO | YES | YES | YES |
| 이메일/메시지 발송 | NO | NO | NO | HITL | YES | YES |
| 금융 거래 | NO | NO | NO | NO | HITL | YES (Ask) |
| 비가역 작업 | NO | NO | NO | NO | YES | YES |

> `HITL` = 실행 시점 인간 승인 필수 (R-13-1 경유). `Ask` = §B.3 원문 규칙 그대로 사용자 선행 질의.

### 2.3 Permission Level ↔ Autonomy Level 교차 매핑

> **정본 분리**: Autonomy Level 정의는 §B (레벨/전환), Permission Level 정의는 본 문서 §2.1 (레벨/범위). 본 표는 **조합 가능성** 만 표현한다.

| Autonomy | P0 | P1 | P2 | P3 | P4 | P5 |
|----------|:--:|:--:|:--:|:--:|:--:|:--:|
| **L0 Manual** | YES | Ask | Ask | Ask | Ask | Ask |
| **L1 Assisted** | YES | YES | Ask | Ask | Ask | Ask |
| **L2 Supervised** | YES | YES | YES | Ask | Ask | Ask |
| **L3 Conditional (R-13-1)** | YES | YES | YES | YES (per-scope) | HITL | Ask |
| **L4 Autonomous** | YES | YES | YES | YES | YES (post-log) | Ask (never Auto) |

### 2.4 API 범위 · 자원 접근 구체화

| Level | 허용 API 프리픽스 | 파일시스템 | 네트워크 | CPU·메모리 상한 | 비용 상한 참조 |
|-------|-----------------|-----------|----------|----------------|----------------|
| P0 | `vamos.read.*`, `mcp.list.*` | read-only | egress-allowlist | 500ms, 256MB | N/A |
| P1 | 위 + `vamos.write.local.*` | agent_workspace/** (RW) | egress-allowlist | 2s, 512MB | N/A |
| P2 | 위 + `vamos.exec.sandbox.*` | sandbox/** (RW) | egress-allowlist | 30s, 2GB | SG-001 (budget_remaining) |
| P3 | 위 + `vamos.ext.api.*` | 위 | egress-allowlist + approved-domains | 60s, 4GB | LOCK-AP-09 V1 ₩40K |
| P4 | 위 + `vamos.ext.write.*` | 위 | 위 | 120s, 4GB | LOCK-AP-09 |
| P5 | 위 + `vamos.fin.*` | deny (별도 서명 세션) | financial-gateway only | 120s, 4GB | LOCK-AP-09 + FR-14 |

### 2.5 Agent Teams V1 제약 (LOCK-AP-05 교차)

> **LOCK 참조 (출처: §3.4 LOCK-AP-05 / Part2 §6.7 LOCK-AT-014)**: Lead + max 2 Sub-Agent — 재정의 금지.

- Lead 에이전트는 Sub 에이전트의 **Permission Level 상한을 초과하여 위임 불가**.
- Sub Level = `min(sub.own_level, lead.own_level, delegation_request.level)`.
- Sub count > 2 감지 시 `PermissionEnforcer.enforce()` 에서 `LockViolation(LOCK-AP-05)` raise → I-20 (§4 `PE-003` 경로).

---

## §3. 공통 자료 구조 (Pydantic)

> 본 절의 모든 타입은 `permission_matrix.md` 와 `guardrail_rules.md` 가 공유한다. 인라인 중복 정의 금지.

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

PermissionLevel = Literal[0, 1, 2, 3, 4, 5]          # LOCK-AP-02
AutonomyLevel = Literal[0, 1, 2, 3, 4]                # §B

class ActionRequest(BaseModel):
    request_id: str
    agent_id: str
    task_id: str
    action_name: str                                   # e.g. "send_email"
    required_permission: PermissionLevel
    autonomy_required: AutonomyLevel
    estimated_cost_usd: float = 0.0
    api_calls_count: int = 0
    data_scope: list[str] = Field(default_factory=list)  # e.g. ["PII"]
    target_system: Optional[str] = None
    reversible: bool = True
    side_effects_count: int = 0
    trace_id: str

class PermissionDecision(BaseModel):
    request_id: str
    decision: Literal["allow", "deny", "hitl", "escalate"]
    effective_permission: PermissionLevel
    guardrail_hits: list[str] = Field(default_factory=list)  # e.g. ["SG-005"]
    confidence: float = 1.0                            # LOCK-AP-10 비교 대상
    reason_chain: list[str] = Field(default_factory=list)  # K-046 설명 입력
    trace_id: str
    evaluated_at: datetime

class StateSnapshot(BaseModel):
    """K-045 롤백 기본 단위"""
    snapshot_id: str
    task_id: str
    agent_id: str
    taken_at: datetime
    scope: Literal["workspace", "sandbox", "external_refs"]
    storage_uri: str                                    # s3://... or file://
    checksum_sha256: str
    parent_snapshot_id: Optional[str] = None
    size_bytes: int

class TxLogEntry(BaseModel):
    """K-045 트랜잭션 로그 항목"""
    entry_id: str
    task_id: str
    snapshot_id: str
    action: ActionRequest
    result_hash: str
    reversible: bool
    compensation_handler: Optional[str] = None          # qualified name
    created_at: datetime

class ExplanationTrace(BaseModel):
    """K-046 결정 설명 구조"""
    explanation_id: str
    task_id: str
    agent_id: str
    decision: Literal["allow", "deny", "hitl", "escalate"]
    reason_chain: list[str]                             # 순서 있는 자연어 reason
    evidence: list[dict] = Field(default_factory=list)  # [{"type":"log","ref":"..."}]
    confidence: float
    created_at: datetime
    trace_id: str

class HumanInterventionRequest(BaseModel):
    """§C.4 정본 스키마 참조 — 재정의 금지"""
    request_id: str
    agent_id: str
    task_id: str
    urgency: Literal["low", "medium", "high", "critical"]
    type: Literal["approval", "decision", "review", "error_resolution"]
    context: dict                                       # §C.4 context 필드 세트
    timeout_seconds: int
    default_action: Literal["approve", "deny", "escalate"]
    notification_channels: list[Literal["email", "slack", "ui", "sms"]]

class EscalationPayload(BaseModel):
    """langgraph/autogen adapter §10 EscalationPayload 와 정합"""
    source_engine: Literal["permission_enforcer"] = "permission_enforcer"
    target_channel: Literal["I-19", "I-20"]
    error_code: str
    original_request: ActionRequest
    partial_result: Optional[dict] = None
    retry_count: int = 0
    lock_violations: list[str] = Field(default_factory=list)
    confidence_after_penalty: float
    trace_id: str
    timestamp: datetime
```

---

## §4. PermissionEnforcer 의사코드 (K-041)

```python
def enforce(req: ActionRequest, agent_state) -> PermissionDecision:
    """
    시간복잡도: O(R + G)  — R=레벨 규칙수(상수), G=평가 가드레일수(SG-001~SG-005 pre-action)
    공간복잡도: O(R)
    LOCK 참조: AP-02 (level 범위), AP-05 (Lead+2 Sub), AP-10 (confidence<0.5 → HITL)
    ABC 패턴: Chain of Responsibility (pre-check 체인) + Strategy (level-specific allowlist)
    """
    reasons: list[str] = []

    # 1) 레벨 계층 검증 — §2.1
    if req.required_permission > agent_state.current_permission:
        reasons.append(f"required={req.required_permission} > current={agent_state.current_permission}")
        return _deny(req, reasons, "PE-001", penalty=0.20)

    # 2) Autonomy × Permission 교차 — §2.3 테이블 기반 상수 LOOKUP
    #    LOOKUP = {(L, P): cell for (L, P, cell) in §2.3 표}   # YES|Ask|HITL|NO
    cell = LOOKUP[(agent_state.autonomy_level, req.required_permission)]
    if cell == "NO":
        reasons.append(f"autonomy L{agent_state.autonomy_level} forbids P{req.required_permission}")
        return _deny(req, reasons, "PE-002", penalty=0.20)
    if cell == "Ask":
        reasons.append(f"autonomy L{agent_state.autonomy_level} requires user_query for P{req.required_permission}")
        return _hitl(req, reasons, "PE-006", confidence=agent_state.last_confidence)
    if cell == "HITL":
        reasons.append(f"autonomy L{agent_state.autonomy_level} requires HITL approval for P{req.required_permission}")
        return _hitl(req, reasons, "PE-006", confidence=agent_state.last_confidence)
    if cell == "Ask":
        reasons.append(f"autonomy L{agent_state.autonomy_level} requires user_query for P{req.required_permission}")
        return _hitl(req, reasons, "PE-006", confidence=agent_state.last_confidence)
    if cell == "HITL":
        reasons.append(f"autonomy L{agent_state.autonomy_level} requires HITL approval for P{req.required_permission}")
        return _hitl(req, reasons, "PE-006", confidence=agent_state.last_confidence)

    # 3) LOCK-AP-05 교차 — §2.5
    if is_team_delegation(req) and team_subagent_count(agent_state.team) > 2:
        reasons.append("LOCK-AP-05 violation: team size > Lead + 2 Sub")
        return _escalate(req, reasons, "PE-003", channel="I-20", lock="LOCK-AP-05")

    # 4) Pre-action guardrails (SG-001 ~ SG-005, guardrail_rules.md §3.3 참조)
    hits = evaluate_pre_action_guards(req, agent_state)   # CEL
    reasons.extend(hits.reasons)
    if hits.block:
        return _deny(req, reasons, hits.code, penalty=0.15)
    if hits.escalate:
        return _escalate(req, reasons, hits.code, channel="I-19", lock=None)

    # 5) Confidence (LOCK-AP-10) — HITL 트리거
    if agent_state.last_confidence < 0.5:
        reasons.append("LOCK-AP-10: confidence < 0.5 → HITL")
        return _hitl(req, reasons, "PE-010", confidence=agent_state.last_confidence)

    # 6) 허용
    return PermissionDecision(
        request_id=req.request_id,
        decision="allow",
        effective_permission=req.required_permission,
        guardrail_hits=[],
        confidence=agent_state.last_confidence,
        reason_chain=reasons or ["all checks passed"],
        trace_id=req.trace_id,
        evaluated_at=utc_now(),
    )
```

### 4.1 예외 처리 정책 표

| error_code | 원인 | recoverable | 처리 |
|------------|------|:-----------:|------|
| `PE-001` | required > current permission | No | deny, confidence −0.20 |
| `PE-002` | Autonomy×Permission cell = NO | No | deny, confidence −0.20 |
| `PE-003` | LOCK-AP-05 (team size) | No | escalate I-20 (LOCK violation) |
| `PE-004` | SG-005 (autonomy_required > current_level) | No | deny, confidence −0.15 |
| `PE-005` | SG-001 (estimated_cost > budget) | Yes (Gate G5) | deny, suggest budget raise |
| `PE-010` | Confidence < 0.5 (LOCK-AP-10) | Yes (HITL) | hitl I-19, confidence hold |
| `PE-020` | Snapshot 실패 (K-045) | Yes (retry×3) | deny action, escalate I-20 on retry 실패 |
| `PE-030` | Explanation 생성 실패 (K-046) | Yes (warn) | allow action, log warning |
| `PE-099` | 분류 불가 | No | escalate I-20 post-mortem |

---

## §5. 롤백/되돌리기 메커니즘 (K-045)

### 5.1 스냅샷-트랜잭션 모델

1. **Pre-action**: P1+ 작업은 `StateSnapshot` 선행 생성. `scope ∈ {workspace, sandbox, external_refs}`.
2. **Action 실행**: `TxLogEntry` 1건 기록 (append-only, WAL 스타일).
3. **Post-action**: 결과 해시·부작용 수·가역 플래그 갱신.
4. **Rollback**: `restore(snapshot_id)` + `tx_log` 역재생 (보상 핸들러 체인).

### 5.2 스냅샷 정책

| Permission | 스냅샷 주기 | 보관 |
|------------|-----------|------|
| P0 | 생략 (read-only) | - |
| P1 | Task 시작 1회 + 5분마다 | Task 종료 +24h |
| P2 | Action 1회마다 | Task 종료 +72h |
| P3 | Action 1회 + 외부 호출 직전 | Task 종료 +7d |
| P4 | Action 1회 + 외부 호출 직전 + 직후 | Task 종료 +30d |
| P5 | Action 1회 + 서명 직전/직후 + 감사 저장소 동기화 | **영구** (감사) |

### 5.3 복원 절차 (의사코드)

```python
def rollback(task_id: str, target_snapshot_id: str) -> RollbackResult:
    """
    시간복잡도: O(T)  — T=해당 task_id 의 TxLogEntry 수
    LOCK 참조: AP-03 (A2A state 전이는 롤백 후 재검증)
    ABC 패턴: Command + Memento
    """
    snap = snapshot_store.get(target_snapshot_id)                 # O(1)
    entries = list(tx_log.iter_after(snap.snapshot_id, task_id))  # O(T) — materialize 1회
    for e in reversed(entries):                                   # O(T)
        if not e.reversible:
            return _escalate_irreversible(task_id, e, "I-19", "PE-021")
        apply_compensation(e.compensation_handler, e.action)      # O(1)
    restore_state_from(snap)                                      # O(size)
    emit_rollback_log(task_id, target_snapshot_id)                # K-046 기록
    return RollbackResult(ok=True, reverted_entries=len(entries))
```

### 5.4 가역 / 비가역 분류 원칙

- **가역** (기본): 워크스페이스/샌드박스 파일 변경, 캐시 기록, 로컬 DB 트랜잭션.
- **비가역** (SG-010 트리거): 이메일/메시지 발송, 외부 파일 공유, 금융 거래, 물리 디바이스 동작.
- 비가역 작업은 `compensation_handler` 정의 **필수** 또는 `HITL` 선승인 필수.

### 5.5 롤백 × 자율성 전환 연계

- 에러율 급등 (>10%) → §B.2 즉시 1단계 하향 + 최신 snapshot 으로 자동 rollback 제안.
- 보안 위반 → L0 리셋 + **전체 task_id** 의 P3+ 작업 rollback 강제.

---

## §6. 설명가능성 (K-046)

### 6.1 설명 생성 파이프라인

```
[PermissionDecision.reason_chain]
        │  ← §4 enforce() 결과
        ▼
[ExplanationAssembler] ── 수집: action context + guardrail hits + tx_log refs
        │
        ▼
[ExplanationTrace] ── NLG(optional) → user_text
        │
        ▼
[K-046 Store] (append-only) ←── agent_mode_autonomy_mapping.md 의 audit 요구 충족
```

### 6.2 설명 컨텐츠 3단 구조

| 단계 | 내용 | 대상 |
|------|------|------|
| **What** | 에이전트가 수행하려/수행한 action | 최종 사용자 |
| **Why** | `reason_chain` + 가드레일 hits + 참조 데이터 | 감사자 |
| **How to undo** | rollback 가능 snapshot_id + 예상 영향 | 사용자/운영자 |

### 6.3 불변 감사 체인

- 모든 `ExplanationTrace` 는 append-only 스토어에 기록.
- `trace_id` 는 `ActionRequest` / `PermissionDecision` / `TxLogEntry` / `ExplanationTrace` 전 구간 동일.
- 동일 `trace_id` 로 최소 1건의 reason_chain 이 존재하지 않으면 `PE-030` warning.

### 6.4 의사코드

```python
def build_explanation(req: ActionRequest, dec: PermissionDecision,
                      tx_entry: Optional[TxLogEntry]) -> ExplanationTrace:
    """
    시간복잡도: O(R + E) — R=reason_chain 길이, E=evidence 참조 수
    LOCK 참조: AP-10 (confidence 표기)
    ABC 패턴: Builder
    """
    evidence: list[dict] = []
    for r in dec.reason_chain:
        if ref := parse_rule_ref(r):          # e.g. "SG-005" → rule link
            evidence.append({"type": "rule", "ref": ref})
    if tx_entry:
        evidence.append({"type": "tx", "ref": tx_entry.entry_id})
        evidence.append({"type": "snapshot", "ref": tx_entry.snapshot_id})
    return ExplanationTrace(
        explanation_id=new_uuid(),
        task_id=req.task_id,
        agent_id=req.agent_id,
        decision=dec.decision,
        reason_chain=dec.reason_chain,
        evidence=evidence,
        confidence=dec.confidence,
        created_at=utc_now(),
        trace_id=req.trace_id,
    )
```

---

## §7. Phase별 복구 흐름 + Confidence Penalty

### 7.1 Phase 흐름도

```
Phase 1 Intake → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Deliver
   │               │               │                  │                │
   │               │               │                  │                └── P4·P5 비가역 → SG-010 + HITL(L3)
   │               │               │                  └── SG-009 conf<0.5 → HITL I-19 (LOCK-AP-10)
   │               │               └── K-043 sandbox 이탈 → PE-004 deny → rollback to last snap
   │               └── autonomy_required > current → PE-002 deny → downshift autonomy
   └── required_permission 미충족 → PE-001 deny → reject task at intake
```

### 7.2 다운그레이드 Confidence Penalty 표

| 트리거 | 다운그레이드 | confidence penalty |
|--------|-------------|:------------------:|
| PE-001 레벨 부족 | action reject | −0.20 |
| PE-002 autonomy 부족 | 자율성 L→L-1 제안 | −0.20 |
| PE-003 LOCK-AP-05 위반 | team → single-agent 제안 | −0.25 |
| PE-004 SG-005 autonomy | deny + 사용자 승격 요청 | −0.15 |
| PE-005 SG-001 budget | G5 hold + Budget 요청 | −0.10 |
| PE-010 LOCK-AP-10 conf<0.5 | HITL I-19 대기 | hold (penalty 없음) |
| PE-020 snapshot 실패 | retry×3 → I-20 | −0.10 per retry |
| PE-021 비가역 rollback 불가 | HITL I-19 승인 요청 | −0.30 |
| PE-099 분류불가 | I-20 post-mortem | −0.25 |

> penalty 는 `agent_state.last_confidence` 에 누적 감산. 0.5 미만 도달 시 LOCK-AP-10 에 의해 자동 HITL.

### 7.3 단계별 복구 전략

| Phase | 실패 유형 | 복구 | 다운그레이드 | 에스컬레이션 |
|-------|----------|------|-------------|-------------|
| Intake | required > current | 작업 reject | - | - |
| Plan | autonomy 부족 | 계획 재작성 (보수적) | autonomy L−1 | - |
| Execute (P1~P2) | sandbox 이탈 | last snapshot rollback | - | I-19 (사용자 알림) |
| Execute (P3) | 외부 API 실패 | retry×3 + CB | L3→L2 | I-20 on CB open |
| Verify | conf<0.5 | HITL 판정 | hold | **I-19 (LOCK-AP-10)** |
| Deliver (P4·P5) | 비가역 오류 | compensation → 불가 시 HITL | - | I-19 (승인) + I-20 (post-mortem) |

---

## §8. 에스컬레이션 페이로드 + 로깅 포맷

### 8.1 EscalationPayload 구조

§3 에 정의된 `EscalationPayload` 를 그대로 사용하며, I-19 / I-20 채널 구분은 target_channel 로 표현한다.

- **I-19** 경로: HITL 승인 필요 (LOCK-AP-10 `PE-010` / `PE-006` / `PE-007` / `PE-021` / `PE-050` 등 사용자 승인으로 재개 가능한 사례).
- **I-20** 경로: LOCK 위반 (`PE-003` LOCK-AP-05), 샌드박스 이탈 (`PE-061`), CB open, `PE-099` 분류 불가, `PE-020` 스냅샷 실패 retry 초과 등 자동 복구 불가·감사 필요 사례.
- **deny-only** (에스컬레이션 없음): `PE-001`, `PE-002`, `PE-004`, `PE-005`, `PE-008`, `PE-042` 는 사용자 승인 여지 없이 거부되며 I-19/I-20 에 송신하지 않는다 (단, 감사 로그는 §8.2 포맷으로 기록).

### 8.2 structured JSON 로그 (R-01-7)

```json
{
  "ts": "2026-04-11T10:31:04.118Z",
  "level": "WARN",
  "logger": "permission_enforcer",
  "trace_id": "7a2c...91",
  "event": "hitl_required",
  "error": {
    "code": "PE-010",
    "message": "confidence 0.42 < 0.5 (LOCK-AP-10)",
    "class": "HitlRequired",
    "stack_digest": null
  },
  "context": {
    "agent_id": "agent-42",
    "task_id": "t-00abc",
    "action_name": "send_email",
    "required_permission": 4,
    "autonomy_level": 3,
    "team_size": 2,
    "vamos_phase": "verify"
  },
  "recovery": {
    "strategy": "hitl_i19",
    "lock_violations": [],
    "last_snapshot_id": "snap-00019",
    "hitl_required": true,
    "confidence_after": 0.42
  }
}
```

### 8.3 감사 저장 요건 (K-046 x K-045)

- `trace_id` 1건당 최소: 1 × ActionRequest, 1 × PermissionDecision, (≥1) × TxLogEntry (P1+), 1 × ExplanationTrace.
- 로그·스냅샷·설명 3종은 **동일 trace_id** 로 조인 가능해야 한다.

---

## §9. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|-----------|----------|
| PM-T01 | Level 상한 위반 | P3 action × P1 agent | `PE-001` deny, confidence −0.20, I-20 없이 사용자 알림 |
| PM-T02 | Autonomy×Perm NO 셀 | L1 agent → P3 external API | `PE-002` deny, L1→L0 제안 없이 거절 |
| PM-T03 | LOCK-AP-05 위반 | Lead + 3 Sub 팀 요청 | `PE-003` I-20 escalate, lock_violations=["LOCK-AP-05"] |
| PM-T04 | LOCK-AP-10 HITL | verify phase conf=0.42 | `PE-010` HITL I-19, HumanInterventionRequest 생성 |
| PM-T05 | SG-001 budget 초과 | estimated_cost 초과 | `PE-005` deny, G5 hold, confidence −0.10 |
| PM-T06 | SG-005 autonomy_required > current | autonomy_required=3, current=2 | `PE-004` deny, downshift 제안 |
| PM-T07 | P2 sandbox 이탈 감지 | 샌드박스 경계 밖 write | last snapshot rollback + I-19 사용자 알림 |
| PM-T08 | K-045 비가역 rollback 불가 | 이메일 발송 후 rollback 시도 | `PE-021` HITL I-19, confidence −0.30 |
| PM-T09 | K-046 설명 누락 | reason_chain 비어있는 allow | `PE-030` warn, allow 유지 |
| PM-T10 | P5 금융 트랜잭션 이중 승인 | L4 agent + P5 action | HITL 승인 2회 필수, 감사 로그 영구 저장 |
| PM-T11 | 에러율 >10% 자동 하향 | 10건 중 2건 실패 후 추가 실패 | autonomy L→L−1 자동, 이전 snapshot rollback 제안 |
| PM-T12 | 보안 위반 L0 리셋 | SG-003 PII leak | L0 리셋 + 전체 P3+ task rollback |
| PM-T13 | Trace ID 단절 검출 | tx_log trace_id 불일치 | 감사 실패 warning, 재빌드 요청 |
| PM-T14 | Team 위임 레벨 상한 | Lead P2 → Sub P3 위임 | min(P2, P3)=P2 로 강제 하향 + 로그 |
| PM-T15 | 로그 nested 구조 검증 | 임의 deny 1건 | error/context/recovery 3블록 + trace_id 존재 |

---

## §10. ABC 패턴 매핑 요약

| 알고리즘 / 컴포넌트 | ABC 패턴 | 이유 |
|---------------------|---------|------|
| `PermissionEnforcer.enforce` | Chain of Responsibility | 레벨→교차→LOCK→guardrail→conf 순차 |
| Level-specific allowlist | Strategy | 레벨별 허용 prefix/자원 |
| `rollback()` | Command + Memento | snapshot=Memento, tx_log=Command |
| `build_explanation` | Builder | reason_chain + evidence 조립 |
| EscalationPayload routing | Adapter | I-19/I-20 채널 변환 |

---

## §11. R6 준수 선언

본 문서는 **What+How** 만 기재한다. Phase/Week 일정, 담당자, 배포 순서 등 **When** 정보는 Part2 정본에만 존재한다. 이월·게이트 시점은 `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §7 를 참조한다.

---

## §12. 이슈/후속 작업

- K-045 의 `compensation_handler` 레지스트리 구현은 §11.1 FR-1 에서 구현.
- K-046 NLG 번역기는 Phase 2 이후 선택 사항 (optional).
- `[CONFLICT_CANDIDATE: 없음]` — agent_mode_autonomy_mapping.md 와 정본 범위 충돌 0건 확인 (본 문서는 Permission Level, 참조 문서는 Agent Mode↔Autonomy Level 매핑으로 정본 범위 상호 배타).

---

*정본 소유: #13 Agent-Protocol-Interoperability / 06_autonomy-safety*
*LOCK 참조: AP-02 (Level 0~5), AP-05 (Lead+2 Sub), AP-10 (HITL <50%)*

---

## §V2. V2-Phase 2 확장 (2026-04-22, STAGE 7 STEP_B #2c)

> **V2 태그**: V2-Phase 2 (append-only 확장, V1 §0~§12 + 상기 footer 본문 불변)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`
> **범위**: **K-041 에이전트 권한 매트릭스 × K-047 자기진화 권한 제약** — 자기진화 시 Permission Level L0~L4 자동 상한 + L5 금융 절대 금지 + Dream Mode × Permission × 활성 시간 3차원 매트릭스 + 예측형/앰비언트/Time-Travel 권한 제약 + 확대 요청 HITL 경로.
> **LOCK 재확인**: LOCK-AP-02 (Permission Level 0~5) / LOCK-AP-05 (Lead + max 2 Sub-Agent) / LOCK-AP-09 (V1 ₩40K / V2 ₩93K / V3 ₩266K) / LOCK-AP-10 (HITL < 50%, 정본은 guardrail_rules.md §V2.2).
> **동반 산출물**: `guardrail_rules.md §V2` (자기진화 안전 가드레일 + LOCK-AP-10 정본) — 본 §V2 는 동반 산출물의 Permission 측면 구체화.
> **경계**: K-048 에이전트 윤리 프레임워크 (STEP7-K L957~L975) 는 V3 범위 (본 §V2 외). K-056 / K-065~K-068 V3 이관 명시.

### §V2.1 K-041 원문 verbatim 매핑 + 자기진화 × Permission 제약 표

**K-041 STEP7-K L820~L840 원문 verbatim**

```
# STEP7-K L820~L840 verbatim (본 §V2 정본 입력)

[구현 상세]
- 계층적 권한 시스템:
  Level 0 (읽기 전용): 정보 조회, 검색
  Level 1 (생성): 파일 생성, 코드 생성
  Level 2 (수정): 파일 수정, 설정 변경
  Level 3 (실행): 코드 실행, API 호출
  Level 4 (외부 통신): 이메일 발송, PR 생성
  Level 5 (금융): 주문 실행, 결제 (항상 사용자 확인)

- Blue Node 별 기본 권한:
  | Node | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
  |------|---------|---------|---------|---------|---------|---------|
  | Dev  | ✅ | ✅ | ✅ | ✅ | Ask | ❌ |
  | Research | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
  | Content | ✅ | ✅ | ✅ | ❌ | Ask | ❌ |
  | Quant | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
  | Trading | ✅ | ✅ | ❌ | ✅ | ❌ | Ask |

[구현성] V1: ✅ 즉시
```

**자기진화 시 Permission 제약 표 (6 Blue Node × L0~L5)**

> V1 §2.1 "Permission Level 0~5" × STEP7-K "Blue Node 기본 권한" 의 **자기진화 경로 전용 서브셋**. `is_self_evolution == true` context 에서만 적용. 일반 사용자 호출 경로는 V1 §2.1~§2.2 매트릭스가 유효.

| Blue Node | L0 READ | L1 WRITE_LOCAL | L2 EXEC_SANDBOX | L3 EXTERNAL | L4 IRREVERSIBLE | L5 FINANCIAL |
|-----------|:-------:|:--------------:|:---------------:|:-----------:|:---------------:|:------------:|
| **Dev** | ✅ 자동 | ✅ 자동 | ✅ 자동 | ⚠️ HITL | ❌ 금지 | ❌ 절대 금지 |
| **Research** | ✅ 자동 | ✅ 자동 | ❌ (V1 동일) | ⚠️ HITL | ❌ 금지 | ❌ 절대 금지 |
| **Content** | ✅ 자동 | ✅ 자동 | ✅ 자동 | ❌ 금지 | ❌ 금지 | ❌ 절대 금지 |
| **Quant** | ✅ 자동 | ✅ 자동 | ❌ (V1 동일) | ⚠️ HITL | ❌ 금지 | ❌ 절대 금지 |
| **Trading** | ✅ 자동 | ✅ 자동 | ❌ (V1 동일) | ⚠️ HITL | ❌ 금지 | ❌ **절대 금지 (Trading L5=Ask도 자기진화 경로에서는 금지)** |
| **Integration (#13 본 도메인)** | ✅ 자동 | ✅ 자동 | ✅ 자동 | ⚠️ HITL | ❌ 금지 | ❌ 절대 금지 |

**핵심 변경점 (V1 기본 권한 → V2 자기진화 경로)**

| 변경 | V1 기본 | V2 자기진화 경로 | 근거 |
|------|:-------:|:---------------:|------|
| Dev L4 | `Ask` (HITL 1회) | **금지** | 자기진화 경로에서 비가역 외부 영향 차단 |
| Content L4 | `Ask` | **금지** | 동 |
| Trading L5 | `Ask` | **절대 금지** | 금융 주문은 자기진화 경로에서 이중 방어 (LOCK-AP-02 + guardrail_rules.md §V2.5) |
| 모든 Node L3 | Node별 상이 | **HITL 필수** | R-13-7-6 (guardrail_rules.md §V2.4 Phase 3) |

### §V2.2 Dream Mode × Permission × 활성 시간 3차원 매트릭스

> Dream Mode (05_self-evolution/dream_mode.md) 는 **비활성 시간에만** 실행되며 Permission L2 상한을 자동 적용한다. 본 §V2.2 는 시간 축을 추가한 3차원 매트릭스를 정의한다.

**3차원 매트릭스**: (Permission Level) × (Agent Mode) × (활성 시간)

| Permission | 활성 시간 (사용자 action < 5min 이내) | 비활성 시간 (idle ≥ 5min) | 근거 |
|:----------:|:--------------------------------:|:----------------------:|------|
| **L0 READ** | ✅ 자동 | ✅ 자동 | 부작용 없음 |
| **L1 WRITE_LOCAL** | ⚠️ 경고 로그 (자기진화 보류) | ✅ 자동 (Dream Mode) | 로컬 스코프 |
| **L2 EXEC_SANDBOX** | ❌ 차단 (D-1 fail) | ✅ 자동 (Dream Mode) | 샌드박스 실행 사용자 영향 |
| **L3 EXTERNAL** | ❌ 차단 | ⚠️ HITL 비동기 대기 | 외부 영향 |
| **L4 IRREVERSIBLE** | ❌ 금지 | ❌ 금지 | 항상 금지 |
| **L5 FINANCIAL** | ❌ 절대 금지 | ❌ 절대 금지 | **이중 방어** |

**Dream Mode 진입 3 중 가드** (guardrail_rules.md §V2.4 Phase 6 D-1/D-2/D-3)

| 가드 | 조건 | 본 §V2.2 해석 |
|------|------|---------------|
| D-1 | `active_time == false` | 활성 시간 → Dream Mode 미진입 (위 매트릭스 "활성 시간" 열은 Dream Mode 사용 불가) |
| D-2 | `autonomy_level ∈ {L0, L1, L2}` | L3+ Permission 은 Dream Mode 경로에서 자동 실행 불가 |
| D-3 | `cumulative_drift_{24h} ≤ 0.20` | guardrail §V2.3 drift 초과 시 Dream Mode 일시 중단 |

### §V2.3 예측형 / 앰비언트 / Time-Travel 자기진화 작업 권한 제약

| 에이전트 모드 | 본 문서 Permission 상한 | 자기진화 사용 범위 | 근거 |
|--------------|:----------------------:|--------------------|------|
| **Predictive** (05_self-evolution/predictive_agent.md) | **L1~L2** | 시간/작업/계절/컨텍스트 4 패턴 예측 → dispatch 의사결정 | predictive_agent.md §6 (L1=알림 초안, L2=샌드박스 시뮬레이션) |
| **Ambient** (ambient_agent.md) | **L0~L2** | 환경 모니터링 5 종 → 알림 P0~P3 | ambient_agent.md §7 (L0=모니터링, L1=알림 초안, L2=자동 필터링) |
| **Time-Travel** (time_travel.md) | **shadow L2** (메인 상태 영향 0) | 스냅샷 replay + counter-factual 분석 | time_travel.md §5.2 (L2 shadow scope 격리) |

**Permission 확대 요청 경로**

```
┌─────────────────────────────────────────────────────────────────────┐
│  Predictive/Ambient/Time-Travel 내부 자기진화 제안                  │
│    └─ L3+ Permission 필요 시 → EscalationPayload (I-19)            │
│        ├─ 사용자 승인 → 1회 실행 허용 (per-call 로깅)               │
│        └─ 사용자 거부 → 제안 reject + 거부 사유 학습 (SG-014 P4)    │
└─────────────────────────────────────────────────────────────────────┘
```

### §V2.4 확대 요청 HITL 경로 (I-19 / I-20 구분)

자기진화 경로에서 Permission 확대 (L2→L3) 시 채널 선택 규칙:

| 상황 | 채널 | 응답 시한 | 비고 |
|------|:----:|:---------:|------|
| 사용자 직접 상호작용 중 (active_time=true) | **I-19** (동기 HITL) | ≤ 2 min | UI blocking prompt |
| Dream Mode (비활성 시간) 제안 | **I-19 비동기** | ≤ 24 h | push notification |
| 외부 시스템 긴급 신호 (앰비언트 P0) | **I-20** (긴급 통지) | ≤ 30 s | 다중 채널 broadcast |
| A/B 테스트 결과 승격 제안 | I-19 비동기 | ≤ 72 h | 분석 리포트 첨부 |
| 실패 분석 자동 패치 제안 (SG-014) | I-19 | ≤ 24 h | LOCK 영역 touches 시 자동 reject |

**EscalationPayload 확장** (V1 §3 EscalationPayload 상속)

```python
class SelfEvolutionPermissionEscalation(EscalationPayload):
    """자기진화 경로 Permission 확대 요청 — V2-Phase 2"""
    # V1 EscalationPayload 필드 전수 상속 (target_channel, trace_id, ...)
    requested_level: Literal[3, 4, 5]               # L3~L5 요청 (L0~L2 는 자동)
    current_level: Literal[0, 1, 2]                 # 현재 자기진화 상한
    self_evolution_phase: Literal[1, 2, 3, 4, 5, 6] # guardrail §V2.4 Phase 1~6
    business_justification: str                     # 확대 필요 사유 (LLM 생성)
    risk_assessment: str                            # 위험 분석 (LLM 생성)
    rollback_plan: Optional[str] = None             # L4 이상 필수
    financial_impact_krw: Optional[float] = None    # L5 필수 (자동 거절 대상)

    @validator("requested_level")
    def forbid_l5(cls, v):
        if v == 5:
            raise ValueError("LOCK-AP-02 + §V2.5 이중 차단 — L5 자기진화 절대 금지")
        return v
```

### §V2.5 자기진화 경로 롤백 제약 (K-045 × V2)

> V1 §5 롤백 메커니즘 (스냅샷/트랜잭션 로그/복원) 은 **자기진화 경로에서도 동일 적용** 되며, 아래 V2 추가 제약을 따른다.

| 자기진화 Phase (guardrail §V2.4) | 자동 롤백 트리거 | 체크포인트 보존 |
|----------------------------------|------------------|------------------|
| Phase 1 성능 모니터링 | `success_rate < 0.70 지속 3h` | 24h |
| Phase 2 프롬프트 최적화 | `prompt_drift > 0.30` | 72h (Rollback 가능) |
| Phase 3 도구 패턴 | `tool_chain_drift > 0.30` | 72h |
| Phase 4 실패 분석 | 자동 패치 실패 탐지 | 영구 (감사 로그) |
| Phase 5 A/B 테스트 | 실험군 `success_rate` 대조군 대비 `< 90%` | 30 days |
| Phase 6 Dream Mode | `cumulative_drift > 0.30` (guardrail §V2.3) | 14 days |

**롤백 시 Permission 자동 회귀**: 자기진화 제안이 롤백되면 해당 경로의 Permission 상한이 **1 단계 자동 하향** (예: L3 허용 상태 → L2 로 회귀). 재상향은 I-19 HITL 경유.

### §V2.6 설명가능성 확장 (K-046 × V2)

V1 §6 설명 생성 파이프라인 (`build_explanation`) 은 자기진화 경로에 대해 **메타 설명 (meta-explanation)** 을 추가 생성한다:

```python
class SelfEvolutionExplanation(BaseModel):
    """V1 Explanation 확장 — V2-Phase 2"""
    base_explanation: Explanation                   # V1 §6 원본
    self_evolution_trace: list[str]                 # Phase 1~6 적용 이력
    cumulative_drift: float                         # guardrail §V2.3
    cumulative_confidence: float                    # guardrail §V2.2
    permission_escalations: list[str]               # 세션 내 확대 이력
    ab_test_arm: Optional[Literal["control","experiment"]] = None
    rollback_available: bool                        # Phase 5 체크포인트 유효 여부
```

### §V2.7 로깅 포맷 (V1 §8 nested 확장)

V1 §8 `error/context/recovery` 3-block 에 자기진화 전용 필드 추가:

```json
{
  "error": { "...": "V1 §8 원본 필드" },
  "context": {
    "is_self_evolution": true,
    "self_evolution_phase": 4,
    "cumulative_drift_24h": 0.18,
    "cumulative_confidence": 0.62,
    "permission_requested": 3,
    "permission_granted": 2,
    "ab_test_id": "abt_selfevo_2026_04_...",
    "...": "V1 §8 원본 필드"
  },
  "recovery": {
    "permission_auto_regress": true,
    "regressed_from": 3,
    "regressed_to": 2,
    "...": "V1 §8 원본 필드"
  }
}
```

### §V2.8 Phase 3 통합 테스트 시나리오 (≥ 10건)

| # | ID | 시나리오 | 검증 기준 |
|---|-----|---------|----------|
| 1 | PM-01 | Dev Node 자기진화 경로 L4 요청 → deny (V1 L4=Ask vs V2 금지) | §V2.1 변경점 적용 |
| 2 | PM-02 | Trading Node L5 자기진화 경로 → 절대 금지 (이중 방어) | LOCK-AP-02 + §V2.5 |
| 3 | PM-03 | Dream Mode 활성 시간 L2 시도 → pause | §V2.2 D-1 fail |
| 4 | PM-04 | Dream Mode 비활성 시간 L2 → 자동 진입 | §V2.2 3차원 매트릭스 |
| 5 | PM-05 | Dream Mode cumulative_drift 0.25 → D-3 escalate | guardrail §V2.3 + §V2.4 D-3 |
| 6 | PM-06 | Predictive L2 샌드박스 시뮬레이션 자동 허용 | §V2.3 Predictive L1~L2 |
| 7 | PM-07 | Predictive L3 dispatch 제안 → I-19 HITL | §V2.4 I-19 |
| 8 | PM-08 | Ambient P0 외부 긴급 통지 L3 → I-20 긴급 채널 | §V2.4 I-20 |
| 9 | PM-09 | Time-Travel shadow L2 메인 상태 격리 검증 | §V2.3 shadow L2 |
| 10 | PM-10 | 자기진화 제안 롤백 후 L3→L2 자동 회귀 | §V2.5 |
| 11 | PM-11 | L5 요청 Pydantic validator `forbid_l5` 차단 | §V2.4 validator |
| 12 | PM-12 | A/B 테스트 승격 제안 I-19 비동기 ≤ 72h | §V2.4 |

> **≥10 충족**: 12건 (목표 ≥ 10건 1.2배 초과).

### §V2.9 세션 간 인터페이스 cross-check

| 참조자 | 참조 지점 | 본 §V2.x 정합 | 결과 |
|--------|----------|---------------|------|
| `guardrail_rules.md §V2.2 LOCK-AP-10 cumulative` | HITL < 0.50 트리거 | 본 §V2.4 escalate_to_HITL I-19 | PASS |
| `guardrail_rules.md §V2.4 Phase 3 R-13-7-6` | L4+ 자기진화 금지 | 본 §V2.1 L4 금지 + §V2.3 permission 상한 | PASS |
| `guardrail_rules.md §V2.5 L5 이중 차단` | LOCK-AP-02 + §V2.5 | 본 §V2.4 `forbid_l5` validator | PASS |
| `05_self-evolution/dream_mode.md §4.3` | L2 상한 | 본 §V2.2 Dream Mode × L2 | PASS |
| `05_self-evolution/predictive_agent.md §6` | L1~L2 범위 | 본 §V2.3 Predictive | PASS |
| `05_self-evolution/ambient_agent.md §7` | L5 금지 | 본 §V2.3 Ambient L0~L2 + §V2.4 L5 validator | PASS |
| `05_self-evolution/time_travel.md §5.2` | shadow L2 | 본 §V2.3 Time-Travel shadow | PASS |

### §V2.10 자가 검증 체크리스트

- [x] V1 §0~§12 + footer 본문 불변 (append-only 엄수)
- [x] V2-Phase 2 태그 + STAGE 7 STEP_B #2c 명시
- [x] K-041 원문 verbatim 매핑 (§V2.1, L820~L840)
- [x] 자기진화 × Permission 6 Blue Node 제약 표 (§V2.1)
- [x] Dream Mode × Permission × 활성 시간 3차원 매트릭스 (§V2.2)
- [x] Predictive/Ambient/Time-Travel 자기진화 권한 제약 (§V2.3)
- [x] 확대 요청 HITL I-19 / I-20 구분 (§V2.4)
- [x] L5 이중 차단 `forbid_l5` validator (§V2.4)
- [x] 롤백 시 Permission 자동 회귀 (§V2.5)
- [x] 설명가능성 메타 설명 (§V2.6)
- [x] 로깅 포맷 nested 확장 (§V2.7)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§V2.8, 12건)
- [x] 세션 간 인터페이스 cross-check (§V2.9)
- [x] LOCK-AP-02/AP-05/AP-09/AP-10 verbatim 5필드 (§V2.11)
- [x] FABRICATION 10종 census 0 hits
- [x] guardrail_rules.md §V2 동반 산출물 cross-ref 정합 (7 지점)
- [x] parent-executed (Subagent 0회)
- [x] sandbox-only (production permission_matrix.md SHA UNCHANGED)

### §V2.11 LOCK 5필드 매핑

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | V2 사용 지점 |
|---------|------|----------|-----|--------|--------------|
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 (읽기→금융) | 금지 | **§V2.1 자기진화 × 6 Blue Node × L0~L5 제약 표 (정본)** + §V2.2 3D 매트릭스 |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 | Lead + max 2 Sub-Agent | 금지 | §V2.3 Predictive/Ambient/Time-Travel 모두 `agents.length ≤ 2` 엄수 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1 ₩40K / V2 ₩93K / V3 ₩266K | 금지 | §V2.4 A/B 테스트 + Dream Mode Phase 6 예산 한도 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §V2.4 I-19 escalate (정본은 guardrail_rules.md §V2.2) |

### §V2.12 Phase 3 이월 항목 + FABRICATION 10종 census

**Phase 3 이월 항목**

1. K-048 에이전트 윤리 프레임워크 (STEP7-K L957~L975) — V3 Constitutional AI 연동 (본 §V2 범위 외)
2. K-056 Kubernetes 오토스케일링 Permission 연동 — V3 04_deployment-scaling
3. K-065~K-068 멀티 페르소나/멀티유저/마켓플레이스 Permission 확장 — V3 05_self-evolution
4. A/B 테스트 승격 제안 자동 승인 V3 확장 (현재 V2 는 HITL 필수)
5. Dream Mode 활성 시간 판정 임계 (idle ≥ 5min) V3 튜닝

**FABRICATION 10종 census**

| Marker | hits |
|--------|:----:|
| `[FICTION]` | 0 |
| `[PLACEHOLDER]` | 0 |
| `[TBD]` | 0 |
| `[UNVERIFIED]` | 0 |
| `[GUESS]` | 0 |
| `[ASSUMED]` | 0 |
| `[HYPOTHETICAL]` | 0 |
| `[FAKE]` | 0 |
| `[STUB]` | 0 |
| `[MOCK_VALUE]` | 0 |

**TOTAL: 0/10 CLEAN** — parent-executed 100%, Subagent 0회 유지.

---

*V2-Phase 2 확장 작성: 2026-04-22 (STAGE 7 STEP_B #2c, 3-10 P2-6 세션, 도메인 마감 직전)*
*동반 산출물: `guardrail_rules.md §V2` (LOCK-AP-10 DEFINED-HERE 정본 소유)*
*K-041 Permission Level 0~5 × 자기진화 6 Blue Node 제약 표 본 §V2.1 정본 확정*

---

## §V3. Phase 4 추가 이월 통합 정밀화 (PM-12) — append-only, V2 영역 byte 무변경

> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-5)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03)
> **append-only 원칙**: 본 §V3 는 §V2 이하 영역을 일절 변경하지 않는다 (prefix EXACT). LOCK-AP-02 verbatim, §V2.1 정본 무변경, LOCK-AP-10 정본은 guardrail_rules.md §V2.2.

### §V3.1 Dream Mode 활성 시간 판정 임계 (idle ≥ 5min) V3 자동 튜닝 (이월 #3)

Phase 2 §V2.2 3차원 매트릭스의 Dream Mode 활성 판정 임계 `idle ≥ 5min` 은 고정 기본값이었다. V3 에서 **사용자별 활동 패턴 학습 기반 개인화 임계**로 정밀화한다.

| 항목 | Phase 2 (§V2.2) | V3 개인화 | 제약 |
|------|:---------------:|:--------:|------|
| idle 임계 | 5min 고정 | 사용자별 3 ~ 15min 학습 | R-13-1 HITL 학습 단계 필수 |
| 학습 입력 | — | 사용자 세션 패턴 (Dream Mode 진입/이탈 빈도) | dream_mode.md §6 |

> 개인화 임계는 §V2.2 3차원 매트릭스 구조(Permission × 활성/비활성)는 불변, idle 판정 값만 사용자별 학습. Dream Mode 비활성 시간 L2 상한(LOCK-AP-02)은 영구 불변.

### §V3.2 A/B 테스트 승격 제안 자동 승인 조건 (이월 #4, PM-12)

Phase 2 §V2.8 PM-12 의 A/B 테스트 승격 제안은 I-19 비동기 HITL 필수(≤72h)였다. V3 에서 **조건부 자동 승인**을 정밀 검토한다.

```python
# §V3.2 A/B 승격 자동 승인 (PM-12 V3 정밀화)
def ab_promotion_auto_approve(sample_size: int, error_rate: float,
                              confidence: float, user_optin: bool) -> str:
    # R-13-7: 첫 자동 승인은 사용자 명시 opt-in
    if not user_optin:
        return "hitl_required"                # opt-in 전까지 HITL (Phase 2 정본 유지)
    if sample_size > N0 and error_rate < 0.01 and confidence > 0.95:
        return "auto_approve"                 # 3조건 모두 충족
    return "hitl_required"                     # 미충족 시 HITL (PM-12 fallback)
```

| 조건 | 임계 | 미충족 시 |
|------|:----:|----------|
| sample size | > N0 | HITL |
| 에러율 | < 1% | HITL |
| 측정 신뢰도 | > 95% | HITL |
| 첫 자동 승인 opt-in (R-13-7) | 사용자 명시 | HITL (opt-in 전) |

### §V3.3 LOCK 재확인 + CFL 무손상

> **LOCK 재확인 (재정의 0)**: LOCK-AP-02 (Permission Level 0~5, §V2.1 정본 불변) / LOCK-AP-10 (HITL < 50%, 정본 guardrail_rules.md §V2.2 — §V3 참조자) / R-13-7 (외부/자동 승인 첫 연동 사용자 명시 opt-in).
> **CFL-AP-001~007 무손상**: Phase 4 신규 충돌 발화 0건 strict.

> 완전 무인 자동화(opt-in 없는 무인 자동 승인)는 안전성 추가 입증 후 **Phase 4+ 이월**.

---

*V3-Phase 4 추가 이월 통합 정밀화: 2026-06-03 (RECOVERY genuine write, P4-5, append-only)*
*§V2 이하 영역 byte 무변경 (prefix EXACT) — §V2.1 LOCK-AP-02 정본 무손상, LOCK-AP-10 정본은 guardrail_rules.md §V2.2*
