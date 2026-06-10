# Agent Composition — 에이전트 체이닝/병렬 실행 패턴

> **도메인**: #11 Conversation-A2A (TIER3-DOMAIN-08)
> **서브폴더**: `04_advanced-features/`
> **V3 산출물**: P4-4 (Phase 4 #4, P2) — P3-4 forward-defined 정본 승급
> **작성일**: 2026-06-03
> **Status**: V3-Phase 4 APPROVED (production-ready)
> **상세명세 근거**: §2.1 method enum, §6.1 #40 Agent Composition, 부록 §C MoA 정본 매트릭스
> **종합계획서 근거**: §6.1 구현 항목 #40, §7.3 P3-4 블록, §7.4 P4-4 블록, 부록 §C (MoA L2539~L2590)
> **LOCK 직접 보호**: LOCK-A2A-08 Agent Mode 열거형 / LOCK-A2A-09 Circuit Breaker
> **고유 규칙 직접 참조**: R-11-6 MoA proposer 최소 2 / 최대 5

---

## 교차 참조

- `_index.md` — 04_advanced-features/ 항목 #10 Agent Composition (에이전트 체이닝/병렬 P2, Phase 3→4 APPROVED)
- `moa_pattern.md` — MoA proposer/aggregator 패턴 (R-11-6 2~5), 부록 §C MoA 정본 매트릭스 ↔ 본 문서 양방향 cross-ref
- `02_agent-discovery/agent_selection.md` — 4-factor + historical_success 5단 가중 (0.40/0.25/0.20/0.15/0.05) 에이전트 해소
- `conversation_branching.md` — 조건부 조합(conditional)을 분기 트리로 표현 (P4-1 cross-ref)
- `priority_queuing.md` — 조합 단계별 작업 우선순위 큐잉 (P4-2 cross-ref)
- `03_security/delegation_chain.md` — 조합 시 위임 체인 (LOCK-A2A-07 깊이 3)
- `05_monitoring/vbs12_benchmark.md` — 시나리오 11 (Agent Composition) 측정 (P4-6 cross-ref)
- 상위 아키텍처 정본: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §1.1 Agent Mode (LOCK-A2A-08 정본, ADD-009), §4.4 Circuit Breaker (LOCK-A2A-09 정본)
- 교차 도메인: 3-10★ Agent-Protocol (#13 어댑터 조합 langgraph 양방향), 6-3 PARL Wave 2 #15 (Decision Aggregator + Swarm Red Team Lead direct inheritance)

---

## 1. 개요

### 1.1 목적

복수의 A2A 에이전트를 **그래프(DSL)** 로 조합하여 파이프라인(순차)·병렬·조건부 실행 패턴으로 오케스트레이션한다. MoA 패턴(moa_pattern)을 일반화하여, agent_selection 의 4-factor + historical_success 가중 해소를 통해 적합 에이전트를 동적으로 바인딩한다. Agent Mode (LOCK-A2A-08) 와 Circuit Breaker (LOCK-A2A-09) 를 준수한다.

### 1.2 범위

- 조합 DSL (`graph{nodes[], edges[]}`, `mode{pipeline|parallel|conditional}`)
- 에이전트 동적 해소 (agent_selection 4-factor + historical_success 0.05)
- 실행 엔진 (mode별 스케줄링) + 비용 budget 관리
- fallback (LOCK-A2A-09 CB) + DSL parse 검증
- 조합 권한 RBAC

### 1.3 범위 외 (Phase 5+ 이월)

- 조합 그래프 시각 편집기 — 6-1 UI-UX-System
- 조합 학습/자동 그래프 생성 (ML) — Phase 5
- 분산 조합 실행(멀티 노드 코디네이션) — 단일 노드 안정화 후 검토

---

## 2. CompositionRequest (Input Schema, D1)

### 2.1 조합 DSL

```python
from __future__ import annotations
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CompositionMode(str, Enum):
    PIPELINE = "pipeline"        # 순차 체이닝 (출력 → 다음 입력)
    PARALLEL = "parallel"        # 병렬 실행 후 집계 (MoA 일반화)
    CONDITIONAL = "conditional"  # 조건 분기 (분기 트리 연계)


class GraphNode(BaseModel):
    node_id: str
    role: str = Field(..., description="요구 역할/스킬 (agent_selection 매칭 키)")
    agent_id: Optional[str] = None  # 명시 바인딩 시, 없으면 동적 해소


class GraphEdge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None  # conditional 모드 분기 표현식


class CompositionRequest(BaseModel):
    graph_nodes: list[GraphNode]
    graph_edges: list[GraphEdge]
    mode: CompositionMode
    agents_pool: list[str] = Field(default_factory=list, description="후보 에이전트 풀")
    budget_usd: Optional[float] = Field(default=None, description="조합 실행 비용 상한")
```

---

## 3. CompositionResult (Output Schema, D2)

```python
class NodeResult(BaseModel):
    node_id: str
    agent_id: str
    status: Literal["submitted", "working", "input-required", "completed", "failed", "canceled"]
    output_ref: Optional[str] = None
    latency_ms: int


class CompositionResult(BaseModel):
    execution_graph_id: str
    results: list[NodeResult]
    cost_breakdown: dict[str, float]   # node_id → usd
    total_latency_ms: int
```

- 각 노드 `status` 는 **LOCK-A2A-02 Task 상태 열거형** 을 따른다 (간접 — 노드는 개별 Task).

---

## 4. 조합 실행 알고리즘 (D3)

### 4.1 절차

```
def execute_composition(req):
    graph = parse_dsl(req.graph_nodes, req.graph_edges)   # parse error → 400
    # 동적 에이전트 해소: agent_selection 4-factor + historical_success 0.05
    bindings = {n.node_id: n.agent_id or resolve_agent(n.role, req.agents_pool)
                for n in req.graph_nodes}
    if req.mode == PIPELINE:
        return run_pipeline(graph, bindings, req.budget_usd)
    if req.mode == PARALLEL:
        # MoA 일반화: 2~5 proposer (R-11-6) 병렬 실행 후 aggregator 집계
        return run_parallel(graph, bindings, req.budget_usd)
    if req.mode == CONDITIONAL:
        return run_conditional(graph, bindings, req.budget_usd)  # 분기 트리 연계
```

### 4.2 에이전트 해소 가중 (agent_selection 정합)

| 요소 | 가중치 |
|------|--------|
| 스킬 매칭 (skill_match, Jaccard) | 0.40 |
| 부하 (load_score = 1 - load_factor) | 0.25 |
| 우선순위 (priority_score) | 0.20 |
| 지연 (latency_score) | 0.15 |
| historical_success (Phase 3 도입, 4-factor 정규화에 미포함) | 0.00 (Phase 3) |

- 4-factor 합계 1.00 (skill_match 0.40 + load_score 0.25 + priority_score 0.20 + latency_score 0.15). historical_success 는 agent_selection.md §1 'Phase 3 이월 항목' 으로 본 정규화 합계에 미포함(0.00, Phase 3 도입 시 재정규화)하여 정본과 정합한다.

### 4.3 PARALLEL 모드와 MoA

PARALLEL 모드는 moa_pattern 의 proposer/aggregator 를 일반화한다. proposer 노드 수는 **R-11-6 (최소 2, 최대 5)** 를 준수하며, aggregator 노드가 결과를 합성한다. 부록 §C MoA 정본 매트릭스와 본 문서는 양방향 cross-ref 관계로, 조합 그래프의 PARALLEL 패턴이 MoA 의 상위 추상이다.

---

## 5. 에러 처리 (D4)

| 코드 / HTTP | 상황 | 복구 |
|------|------|------|
| `-32602` | DSL parse error (순환 엣지 / 미해소 노드) | 400, DSL 수정 |
| HTTP 402 | budget_usd 초과 | 실행 중단 + 부분 결과 반환 |
| `-32008` | agent unavailable (overloaded) | LOCK-A2A-09 CB fallback → 대체 에이전트 |
| `-32037` (비표준) | proposer 수 R-11-6 위반 (<2 또는 >5) | 400 |

- **agent unavailable fallback**: 노드 에이전트 연속 3회 실패 시 LOCK-A2A-09 CB OPEN → agent_selection 차순위 에이전트로 재바인딩(rebind) 후 재실행.

```json
{
  "trace_id": "trace-uuid",
  "error": { "code": "-32004", "message": "Agent unavailable", "source": "agent_composition.fallback" },
  "context": { "node_id": "n3", "agent_id": "agent:reviewer-001", "cb_state": "OPEN" },
  "recovery": { "strategy": "rebind_next_candidate", "next_agent": "agent:reviewer-002" }
}
```

---

## 6. 의존성 (D5)

| 대상 | 방향 | 내용 |
|------|------|------|
| `moa_pattern.md` | ← (소비) | PARALLEL = MoA 일반화, R-11-6 |
| `02_agent-discovery/agent_selection.md` | ← (소비) | 4-factor + historical_success 해소 |
| langgraph adapter (#13) | → (참조) | 그래프 실행 어댑터 (3-10 양방향) |
| `conversation_branching.md` | ← (제공) | conditional 모드 분기 |
| `priority_queuing.md` | ← (소비) | 노드 작업 우선순위 |

---

## 7. 성능 SLA (D6)

| 메트릭 | 목표 | 측정 |
|--------|------|------|
| 조합 plan P99 | < 200ms | vbs12_benchmark 시나리오 11 |
| 실행 latency | mode/workload 의존 (집계만) | metrics_dashboard |
| proposer 수 | 2~5 (R-11-6) | DSL 검증 |
| fallback rebind | CB OPEN 후 즉시 차순위 | LOCK-A2A-09 |

- 조합 plan(파싱 + 에이전트 해소 + 그래프 검증) P99 < 200ms. 실제 실행 시간은 노드 작업 특성에 의존하므로 본 SLA 는 plan 단계만 보장한다.

---

## 8. 테스트 시나리오 (D7, AGC-T01~T12)

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|----------|
| AGC-T01 | pipeline 정상 | 3노드 순차 | 출력→입력 체이닝, 전수 completed |
| AGC-T02 | parallel 정상 (MoA) | proposer 3 + aggregator | 병렬 실행 → 집계 |
| AGC-T03 | conditional 정상 | 조건 분기 2경로 | 조건 충족 경로만 실행 |
| AGC-T04 | agent unavailable fallback | 노드 에이전트 다운 | CB OPEN → 차순위 rebind |
| AGC-T05 | budget 한도 | budget_usd 초과 | HTTP 402 + 부분 결과 |
| AGC-T06 | historical_success 가중 | 동률 후보 2 | historical_success 높은 쪽 선택 |
| AGC-T07 | DSL parse error (순환) | 순환 엣지 | `-32602` 400 |
| AGC-T08 | proposer 수 위반 | proposer 6개 | `-32007` (R-11-6 max 5) |
| AGC-T09 | proposer 수 위반 (하한) | proposer 1개 | `-32007` (R-11-6 min 2) |
| AGC-T10 | conditional → 분기 | conversation_branching 연계 | 분기 트리 생성 |
| AGC-T11 | 조합 권한 RBAC | VIEWER 조합 생성 | `-32003` 403 |
| AGC-T12 | 조합 plan SLA | plan 부하 | P99 < 200ms |

---

## 9. 보안 / RBAC (D8)

- **agent 조합 권한 RBAC**: 조합 생성/실행은 EDITOR 이상, 자율 에이전트(AGENT)는 위임받은 OWNER 권한 범위 내에서 SEMI_AUTO/SUPERVISED_AUTO 모드로만 조합을 실행할 수 있다 (LOCK-A2A-08).

| 역할 | 조합 생성 | 조합 실행 | 조합 조회 |
|------|----------|----------|----------|
| OWNER | ✅ | ✅ | ✅ |
| EDITOR | ✅ | ✅ | ✅ |
| VIEWER | ❌ | ❌ | ✅ |
| AGENT (SEMI_AUTO/SUPERVISED_AUTO) | 위임 범위 | 위임 범위 | ✅ |

- 모든 조합 실행은 `03_security/audit_logging.md` 에 기록하며, 위임 깊이는 `delegation_chain.md` 의 LOCK-A2A-07 (깊이 3) 을 따른다.
- 6-3 PARL 의 Decision Aggregator / Swarm Red Team Lead 패턴과 PARALLEL 모드가 정합한다 (direct inheritance).

---

## 10. LOCK 인용 표 (5필드 분리 강제)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-08 | Agent Mode 열거형 | `MANUAL\|SEMI_AUTO\|SUPERVISED_AUTO` | D2.0-05 §1.1 (ADD-009) | D2.0-05 변경 시만 |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

**고유 규칙**: R-11-6 MoA proposer 최소 2 / 최대 5 (종합계획서 §4.3 + 04 _index L42 정본) — §4.3/§8 적용.

- LOCK-A2A-08 적용 위치: §9 AGENT 모드 조합 권한
- LOCK-A2A-09 적용 위치: §5 agent unavailable fallback rebind

> **R2/R9 준수**: LOCK 값은 AUTHORITY_CHAIN.md §3 정본 verbatim. PARALLEL 모드의 MoA 일반화는 R-11-6 proposer 2~5 를 변경하지 않고 준수한다.

---

## 11. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| PARALLEL = MoA | `moa_pattern.md` 부록 §C | proposer/aggregator R-11-6 양방향 |
| 에이전트 해소 | `agent_selection.md` | 4-factor + historical_success 0.05 |
| conditional 분기 | `conversation_branching.md` | 분기 트리 |
| 위임 깊이 | `delegation_chain.md` | LOCK-A2A-07 깊이 3 |
| 조합 측정 | `05_monitoring/vbs12_benchmark.md` | 시나리오 11 |

---

## 12. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-06-03 | Phase 4 RECOVERY (genuine write) | V3-Phase 4 NEW 최초 작성 (P4-4, P3-4 forward-defined 정본 승급). D1~D8 8섹션 + 조합 DSL(pipeline/parallel/conditional) + 4-factor+historical_success 0.05 + fallback rebind + budget + RBAC. moa_pattern 부록 §C 양방향 cross-ref. Status DRAFT→APPROVED. LOCK-A2A-08/09 verbatim + R-11-6. SPEC Stage B verify-only 착시(phase4_v3_p4-4_promotion_report) genuine write 해소. |

---

**[END OF agent_composition.md V3 — Phase 4 APPROVED, 2026-06-03]**
