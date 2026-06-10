# Reflection & Planning 패턴 — K-026 + K-027 (V2 확장, L3)

> **STEP7-K**: K-026 Reflection 패턴 (L514~L530) + K-027 Planning 패턴 (L533~L552)
> **레벨**: L3 (V2 확장 패턴, 상세 구현)
> **Part2 상태**: ABSENT (K-026, K-027 모두) → 본 문서로 방식 C 신규 편입
> **정본 소유**: #13 Agent-Protocol-Interoperability / 01_framework-adapters
> **V 스코프**: V2-Phase 2 (K-026 V1: 즉시, K-027 V1: ReAct 즉시 / V2: 고급 Planning 3개월)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2a 3-10 도메인 P2-1 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L514~L530 | K-026 Reflection (자기 비평 → 개선 루프, 3-Gate 연동) |
| STEP7-K (Level 2) | L533~L552 | K-027 Planning (ReAct/Plan-and-Solve/Tree of Thoughts/Graph of Thoughts/ADaPT) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-05 | Lead + max 2 Sub-Agent (Reflection 루프 내 Critic sub-agent 배치 시 준수) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | HITL < 50% (Reflection 반복 후에도 confidence 저하 시 에스컬레이션) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP (외부 Planning tool 호출 시) |
| 구조화_종합계획서.md | §7.4 P2-1 L1117~L1149 | Phase 2 V2 K-026/K-027 배치 근거 |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 import |
| 01_framework-adapters/magentic_one.md | §5 Orchestrator | `orchestrator_plan(request)` 함수가 Planning 엔진 출력 재사용 |
| 01_framework-adapters/moa_pattern.md | §4.2 Aggregator | 모순 해결 단계가 Reflection 자기 비평과 유사 메커니즘 |
| 6-3 Agent-Teams-PARL | LOCK-AT-014 (V1=3) | Reflection loop 내 Proposer + Critic + Synthesizer 가 3-agent 상한 |
| 03_data-exchange/message_format.md §2.5 | CFL-AP-007 alias | canonical type=`task/result/event/control` 보존 |

> **R6 준수**: What+How 전용. When/Where 는 Part2 정본, 미기재.

---

## §2. 개요 (Purpose & Scope)

### 2.1 목적
**K-026 Reflection** (자기 비평·개선 루프) 과 **K-027 Planning** (계획 수립 패턴) 을 VAMOS 프레임워크 어댑터 계층에 도입한다. Reflection 은 각 Blue Node 의 출력 품질 향상 루프를, Planning 은 복합 작업의 자동 분해·실행 경로 생성을 담당한다. 두 패턴은 **상보적**으로 동작하며, Planning 결과 → 실행 → Reflection 검증 → 재실행 사이클로 자기 개선 구조를 형성한다.

### 2.2 범위
- **In-scope K-026**: 자기 비평 → 개선 루프, 만족 기준 기반 종료, 3-Gate 시스템 연동(G1~G5), 코드/투자 분석/Self-Evolution 도메인 적용.
- **In-scope K-027**: ReAct (V1), Plan-and-Solve (V1), Tree of Thoughts (V2), Graph of Thoughts (V2), ADaPT 적응적 재계획 (V2). Task Decomposition, 의존성 그래프 생성, 병렬 실행 식별.
- **Out-of-scope (V3 이관)**: Multi-step Reflection chain(5단 이상, V3), Graph of Thoughts 동적 그래프 수정(V3), Constitutional AI 윤리 반영 Reflection(K-048 V3), Reflection 결과 Persistent Learning(K-047 자기진화 V3).

### 2.3 비고
- **Reflection 반복 상한**: V1=3회, V2=5회. 초과 시 LOCK-AP-10 HITL 에스컬레이션.
- **Planning 분해 깊이 상한**: V1=3단계, V2=5단계. 초과 시 원본 요청 재확인 요구.
- **LOCK-AP-05 준수**: Reflection 루프 내부 Critic 은 별도 Sub-Agent 가 아닌 **동일 Lead Agent 의 self-critic prompt** 로 구현(V1). V2 에서 별도 Critic Agent 배치 시 LOCK-AT-014 V1=3 상한 내 유지.

---

## §3. 공통 자료 구조 참조

> **정본**: `01_framework-adapters/langgraph_adapter.md §3`. 아래는 참조만.

다음 타입을 **langgraph_adapter.md §3에서 그대로 import** 한다:
`VamosMessage`, `VamosPhase`, `A2ATaskState`, `FrameworkTaskRef`, `GatePolicy`, `AdapterResult`.

본 문서 전용 추가 타입:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ReflectionCycle(BaseModel):
    """K-026 자기 성찰 루프의 한 반복"""
    cycle_id: int                                   # 1, 2, 3, ...
    input_answer: str
    critique_text: str                              # 자기 비평 결과
    improved_answer: str
    improvement_delta: float                        # 개선 정도 (0.0 ~ 1.0)
    satisfaction_met: bool                          # 만족 기준 충족 여부
    gate_trigger: Optional[Literal["G1", "G2", "G3", "G4", "G5"]] = None

class PlanStep(BaseModel):
    """K-027 Planning 단위 step"""
    step_id: str
    description: str
    dependencies: list[str] = Field(default_factory=list)  # 선행 step_id 목록
    parallelizable: bool = False
    estimated_duration_s: float = 0.0
    assigned_blue_node: Optional[str] = None        # "research", "dev", "content", ...

class PlanGraph(BaseModel):
    """Planning 결과 DAG"""
    goal: str
    steps: list[PlanStep]
    revision: int = 0
    algorithm: Literal["react", "plan_and_solve", "tree_of_thoughts", "graph_of_thoughts", "adapt"]
    max_depth: int = 3                              # V1=3, V2=5
    total_parallel_branches: int = 0

class ReflectionResult(BaseModel):
    """Reflection 루프 종료 결과"""
    final_answer: str
    cycles: list[ReflectionCycle]
    total_cycles: int
    terminated_reason: Literal["satisfaction", "max_cycles", "hitl_escalation", "cost_gate"]
    hitl_required: bool = False
```

---

## §4. K-026 Reflection 패턴 (L514~L530 원문 매핑)

### 4.1 4단계 루프 (STEP7-K L517~L521)

```
1. 초기 답변 생성        (Phase "execute")
2. 자기 비평             ("이 답변의 문제점은?")
3. 개선 답변 생성        (비평 반영)
4. 만족 기준 충족 시 최종 출력 (아니면 2로 복귀)
```

### 4.2 VAMOS Reflection 통합 (STEP7-K L523~L527)

| 도메인 | Reflection 적용 | 만족 기준 |
|-------|---------------|----------|
| 3-Gate 시스템 | Gate 실패 → 자동 Reflection | Gate 재검증 PASS |
| 코드 생성 | 코드 → 테스트 → 실패 → 수정 루프 | 테스트 PASS + lint clean |
| 투자 분석 | 분석 → 반론 → 재분석 | confidence ≥ 0.70 |
| Self-Evolution (K-047) | 장기 성능 개선 | 이전 세션 대비 개선률 > 5% |

### 4.3 Reflection 의사코드 (Big-O: O(C × M), C=cycle 상한, M=평균 답변 토큰)

```python
def reflection_loop(
    request: VamosMessage,
    satisfaction_fn: callable,          # answer -> bool
    max_cycles: int = 3,                # V1=3, V2=5
) -> ReflectionResult:
    cycles = []
    answer = generate_initial(request)
    for c in range(1, max_cycles + 1):
        critique = self_critique(answer, criteria=satisfaction_fn.__doc__)
        improved = improve(answer, critique)
        delta = quality_delta(answer, improved)
        satisfied = satisfaction_fn(improved)
        cycles.append(ReflectionCycle(
            cycle_id=c, input_answer=answer, critique_text=critique,
            improved_answer=improved, improvement_delta=delta,
            satisfaction_met=satisfied,
        ))
        answer = improved
        if satisfied:
            return ReflectionResult(final_answer=answer, cycles=cycles,
                                    total_cycles=c, terminated_reason="satisfaction")
        if cost_so_far(request.id) > BUDGET_V2_KRW_93000:
            return ReflectionResult(final_answer=answer, cycles=cycles,
                                    total_cycles=c, terminated_reason="cost_gate",
                                    hitl_required=True)
    # max_cycles 도달 시 LOCK-AP-10 HITL 체크
    confidence = compute_final_confidence(cycles)
    if confidence < 0.5:
        return ReflectionResult(final_answer=answer, cycles=cycles,
                                total_cycles=max_cycles,
                                terminated_reason="hitl_escalation",
                                hitl_required=True)
    return ReflectionResult(final_answer=answer, cycles=cycles,
                            total_cycles=max_cycles,
                            terminated_reason="max_cycles")
```

---

## §5. K-027 Planning 패턴 (L533~L552 원문 매핑)

### 5.1 Planning 알고리즘 카탈로그 (STEP7-K L536~L541)

| 알고리즘 | 분해 전략 | V 스코프 | VAMOS 적용 |
|---------|---------|---------|---------|
| ReAct | Reasoning + Acting 교차 | V1 | 기본 Planning 엔진, 도구 호출 필요 작업 |
| Plan-and-Solve | 계획 → 실행 → 검증 | V1 | 고정 단계 작업 (보고서 작성) |
| Tree of Thoughts | 분기 탐색 | V2 | 복수 해결책 필요 (투자 전략 3안) |
| Graph of Thoughts | 그래프 기반 추론 | V2 | 교차 의존 복합 작업 (다단 분석) |
| ADaPT | 적응적 계획 (실패 시 재계획) | V2 | 불확실한 외부 환경 (웹 탐색) |

### 5.2 VAMOS Planning Engine 파이프라인 (STEP7-K L543~L549)

```
1. 사용자 요청 분석       (intent classification)
2. 작업 분해 (Task Decomposition)  (알고리즘 선택 → PlanGraph 생성)
3. 의존성 그래프 생성     (PlanStep.dependencies 추론)
4. 병렬 실행 가능 작업 식별 (topological sort + parallel branch detection)
5. 실행 + 모니터링        (Blue Node 배정 후 실행)
6. 실패 시 재계획          (ADaPT 트리거 또는 Reflection loop)
```

### 5.3 Planning 의사코드 (Big-O: O(V + E) — V=step, E=dependency)

```python
def plan_and_decompose(
    request: VamosMessage,
    algorithm: Literal["react", "plan_and_solve", "tree_of_thoughts", "graph_of_thoughts", "adapt"] = "react",
    max_depth: int = 3,                 # V1=3, V2=5
) -> PlanGraph:
    intent = classify_intent(request)
    if algorithm == "react":
        steps = react_decompose(request, max_depth)
    elif algorithm == "plan_and_solve":
        steps = plan_and_solve(request, max_depth)
    elif algorithm == "tree_of_thoughts":
        steps = tot_branch_search(request, max_depth, branches=3)
    elif algorithm == "graph_of_thoughts":
        steps = got_graph_reason(request, max_depth)
    elif algorithm == "adapt":
        steps = adapt_adaptive_plan(request, max_depth)
    # 의존성 그래프 생성
    deps = infer_dependencies(steps)
    for s in steps:
        s.dependencies = deps.get(s.step_id, [])
    # 병렬 branch 식별
    parallel_groups = topological_parallel_groups(steps)
    parallel_count = sum(1 for g in parallel_groups if len(g) > 1)
    # Blue Node 배정
    for s in steps:
        s.assigned_blue_node = match_blue_node(s, intent)
    return PlanGraph(
        goal=request.content.get("goal", ""),
        steps=steps, algorithm=algorithm,
        max_depth=max_depth, total_parallel_branches=parallel_count,
    )
```

---

## §6. Reflection + Planning 결합 워크플로우

```
[사용자 요청]
    ↓
PlanGraph 생성 (K-027 §5.3)
    ↓
각 PlanStep 실행 (Blue Node 배정)
    ↓
각 step 결과 → Reflection loop (K-026 §4.3, V1=3 cycle)
    ↓
전체 Plan 완료 후 최종 Reflection (goal 달성 여부)
    ↓
satisfaction_met=True → 종료 / False → ADaPT 재계획 (V2)
```

**상호작용 예**:
- 투자 분석 요청 → Plan: "데이터 수집 → 분석 → 반론" → 각 step 실행 → Reflection("이 분석의 반론은?") → 최종 통합 답변.
- 코드 생성 요청 → Plan: "테스트 작성 → 코드 작성 → 실행" → 실패 시 Reflection("왜 실패했나?") → 수정 → 재실행.

---

## §7. LOCK 매핑 (5필드 분리 인용)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 |
|---------|------|----------|-----|-------|-------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | Reflection cycle 결과는 VamosMessage.content 에 serialize |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 | Lead + max 2 Sub-Agent | 금지 | V1 self-critique 는 Lead 내 prompt 로 구현, V2 별도 Critic Agent 는 Sub1/Sub2 slot 소비 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 | 금지 | Planning 단계에서 외부 MCP tool 호출 시 Tool Registry 경유 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §4.3 reflection_loop 내 cost_gate 체크 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety/guardrail_rules.md 정본) | HITL 트리거 < 50% | 금지 | §4.3 max_cycles 도달 후 confidence < 0.5 → hitl_required |
| LOCK-AT-014 | Agent Team size | 6-3 AUTHORITY_CHAIN.md L67 (SPEC S7-A-008) | V1=3 / V2=10 / V3=50+ | 금지 (6-3 정본) | Reflection V2 Proposer + Critic + Synthesizer 배치 시 3-agent 상한 준수 |

---

## §8. Phase별 복구/다운그레이드 흐름

```
Phase 1 (Planning 실패) → 단순 알고리즘 폴백 (ToT → ReAct) → confidence -0.10
Phase 2 (step 실행 실패) → Reflection 루프 진입 → max_cycles 내 복구
Phase 3 (Reflection max_cycles 도달) → LOCK-AP-10 HITL → I-19
Phase 4 (비용 초과) → LOCK-AP-09 Cost Gate → [COST_GATE_BLOCKED]
```

confidence penalty:
- cycle 2회차에도 improvement_delta < 0.05 → -0.15
- Plan revision 2회 이상 → -0.10
- 의존성 추론 실패 → -0.20 (Plan 재생성 요구)

---

## §9. 에스컬레이션 페이로드 (I-20 경유)

```python
class ReflectionPlanningEscalation(BaseModel):
    source_engine: Literal["reflection_loop", "planning_engine"]
    error_code: Literal[
        "REFLECTION_MAX_CYCLES", "PLAN_REVISION_LIMIT",
        "HITL_CONFIDENCE_LOW", "COST_GATE_BLOCKED", "DEPENDENCY_CYCLE",
    ]
    original_request: VamosMessage
    partial_result: Optional[dict]          # ReflectionResult or PlanGraph
    retry_count: int
    cycles_or_revisions: list[dict]
    trace_id: str
    timestamp: datetime
```

---

## §10. 로깅 포맷 (R-01-7 structured JSON)

```json
{
  "trace_id": "...",
  "error": {"code": "REFLECTION_MAX_CYCLES", "cycles": 3},
  "context": {
    "algorithm": "react",
    "goal": "투자 분석: 삼성전자 2026 Q2 전망",
    "blue_node": "quant",
    "improvement_deltas": [0.12, 0.08, 0.02],
    "final_confidence": 0.48
  },
  "recovery": {"action": "hitl_escalation", "route": "I-20", "reason": "confidence_below_threshold_after_max_cycles"}
}
```

---

## §11. Phase 3 테스트 시나리오 (10건)

1. **ReAct 기본 Plan**: "오늘 주가 조회" → 2-step plan (search, format) → 병렬 분기 0 → 실행 성공.
2. **Reflection 1-cycle 만족**: 초기 답변 품질 양호 → cycle 1 개선 → satisfaction_met=True → 종료.
3. **Reflection 2-cycle 만족**: cycle 1 improvement_delta=0.20 → cycle 2 improvement_delta=0.08 → 만족 → 종료.
4. **Reflection max_cycles 초과**: 3 cycle 모두 만족 실패 + final_confidence=0.48 → HITL 에스컬레이션.
5. **Plan-and-Solve 3-step**: "보고서 작성" → plan(aggregate, structure, draft) → 순차 실행.
6. **Tree of Thoughts 3-branch**: "투자 전략" → 3개 분기 plan → 병렬 평가 → 최적 선택.
7. **Graph of Thoughts 교차 의존**: 4-step 상호 의존 → DAG topological sort → 병렬 group 2개.
8. **ADaPT 재계획**: step 2 실패 → 재계획 revision=1 → 재실행 성공 → cycle 2회.
9. **비용 초과 차단**: Reflection 3-cycle + MoA 결합 → ₩95K → COST_GATE_BLOCKED.
10. **LOCK-AT-014 위반 방지**: V2 에서 Proposer+Critic+Synthesizer 3-agent 가 Orchestrator 와 함께 4-agent 가 되려 함 → `[VIOLATION:LOCK-AT-014 V1=3]` 사전 차단.
11. **Magentic-One Orchestrator 연계**: `magentic_one.md §5` 의 `orchestrator_plan(request)` 이 본 문서 `plan_and_decompose()` 호출 → PlanGraph 반환 정합.
12. **Gate 실패 → Reflection**: G3 Verify 실패 → 자동 Reflection 진입 → cycle 2회 개선 → Gate 재검증 PASS.

---

## §12. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 일치 여부 |
|------------|-----------|-----------|
| langgraph_adapter.md §3 | 공통 VamosMessage, VamosPhase | ✅ import 일치 |
| magentic_one.md §5 | `orchestrator_plan(request)` → `plan_and_decompose()` | ✅ 반환 타입 PlanGraph 정합 |
| moa_pattern.md §4.2 | 모순 해결 메커니즘 재사용 (Aggregator = 일종의 Reflection) | ✅ 자기 비평 로직 공통화 |
| tool_memory_benchmark.md §3 VBS-12 9 | Reflection 개선률 측정 지표 (VBS-12 9-1) | ✅ improvement_delta 평균값 입력 |
| 03_data-exchange/message_format.md §2 | VamosMessage.metadata.trace_id 필수 | ✅ 본 문서 §10 로그 일치 |
| 06_autonomy-safety/guardrail_rules.md LOCK-AP-10 | confidence < 0.5 HITL | ✅ §4.3 연동 |

---

## §13. 검증 자가 체크리스트

- [x] §1 교차 참조 블록 포함
- [x] §3 공통 자료 구조 langgraph_adapter.md §3 참조
- [x] §4 STEP7-K L514~L530 원문 line refs 명시 (L517~L521, L523~L527)
- [x] §5 STEP7-K L533~L552 원문 line refs 명시 (L536~L541, L543~L549)
- [x] §7 LOCK 매핑 5필드 분리 인용 (AP-01/05/07/09/10 + AT-014)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§11: 12건)
- [x] 에스컬레이션 페이로드 Python class (§9)
- [x] 로깅 포맷 structured JSON 중첩 3-block (§10)
- [x] V2-Phase 2 헤더 태그
- [x] FABRICATION 10종 census 0 hits
- [x] R6 준수 (What+How 전용)

---

*정본 소유: #13 Agent-Protocol-Interoperability / 01_framework-adapters*
*V2-Phase 2 최초 작성: 2026-04-22 (STAGE 7 STEP_B #2a)*
