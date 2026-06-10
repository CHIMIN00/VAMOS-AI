# Magentic-One 패턴 — K-024 (V2 확장, L2)

> **STEP7-K**: K-024 — Magentic-One 패턴 (STEP7-K L459~L476)
> **레벨**: L2 (V2 확장 패턴)
> **Part2 상태**: ABSENT — Part2 미반영, 본 문서로 방식 C 신규 편입
> **정본 소유**: #13 Agent-Protocol-Interoperability / 01_framework-adapters
> **V 스코프**: V2-Phase 2
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2a 3-10 도메인 P2-1 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L459~L476 | K-024 Magentic-One 패턴 원본 정의 (Orchestrator + WebSurfer + FileSurfer + Coder + ComputerTerminal) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-05 | Lead + max 2 Sub-Agent (V1 총 3 agent, 6-3 LOCK-AT-014 교차) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 지원 필수 (외부 에이전트 인터롭) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 V2 ₩93K (복수 Blue Node 병렬 호출 관리) |
| 구조화_종합계획서.md | §7.4 P2-1 L1117~L1149 | Phase 2 V2 K-024 배치 근거 (Magentic-One ABSENT → V2 신규) |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 (VamosMessage, VamosPhase, FrameworkTaskRef, StateMapping, GatePolicy) import |
| 01_framework-adapters/autogen_adapter.md | §§ V2 | AutoGen GroupChat 기반 Orchestrator 매핑 (K-023 V1 기반) |
| 01_framework-adapters/moa_pattern.md | §§ 전체 | K-025 MoA Aggregator 단계에서 Magentic-One Orchestrator와 역할 분리 (Magentic-One=계획, MoA=합의) |
| 6-3 Agent-Teams-PARL | LOCK-AT-014 (V1=3) | V1 Lead+2 Sub-Agent 제약이 Magentic-One Orchestrator+2 Sub 패턴에 그대로 적용 |
| #2-1 Blue Node Architecture | Research/Dev/Content Node | VAMOS Blue Node와 Magentic-One 에이전트 1:N 매핑 |

> **R6 준수**: 본 문서는 What+How 전용. When/Where(Phase/Week)는 Part2 정본, 미기재.

---

## §2. 개요 (Purpose & Scope)

### 2.1 목적
Microsoft Magentic-One 아키텍처(2024)를 VAMOS 3-10 Framework Adapter Layer에 도입하여, **Orchestrator 중심의 멀티 에이전트 협업 패턴**을 Blue Node 생태계에 구현한다. V1의 단순 Lead+Sub-Agent 팀 패턴(LOCK-AT-014, LOCK-AP-05)을 Magentic-One의 **Progress Ledger + Task Ledger** 구조로 확장하며, VAMOS Blue Node(Research/Dev/Content/Quant/Trading)가 Magentic-One 에이전트 역할(WebSurfer/FileSurfer/Coder/ComputerTerminal)을 흡수·확장한다.

### 2.2 범위
- **In-scope**: Orchestrator 계획 수립 로직 VAMOS 적용, Progress Ledger 스키마, Task Ledger 재계획 트리거, Blue Node ↔ Magentic-One 에이전트 역할 매핑, LOCK-AP-05 제약 내 팀 구성, Magentic-One Tool-Use 흡수, Magentic-One 종료 조건 (Task Ledger satisfied).
- **Out-of-scope (V3 이관)**: Magentic-One 다중 Orchestrator(연방 Orchestrator) 패턴, ComputerTerminal sandbox 전용 가상화(gVisor/Firecracker, K-043 V3와 결합), WebSurfer Playwright 병렬 탐색 최적화(K-043 V2와 겹치므로 V3 이관), Magentic-One 자체 평가 loop(K-047 자기진화 V3와 결합).

### 2.3 비고
- LOCK-AP-05: Orchestrator는 Lead 역할, 하위 에이전트는 최대 2개. Magentic-One 원본 5-agent 구조를 VAMOS에서는 **Lead + 2 Sub-Agent = 총 3** 으로 축소(6-3 LOCK-AT-014 "V1=3" 정합).
- LOCK-AT-014(6-3 정본 verbatim 값): `V1=3 / V2=10 / V3=50+` (SPEC S7-A-008). V2 Phase 2 본 문서 배치 시점에도 **3-agent 상한** 유지(10-agent 확장은 V2 Team size 확장과 별도 진행).
- Magentic-One 원본의 ComputerTerminal / FileSurfer는 **L3 권한 이상** 필요 → VAMOS Permission Level 0~5(LOCK-AP-02) 에서 L3/L4 필터링 후 실행.

---

## §3. 공통 자료 구조 참조

> **정본**: `01_framework-adapters/langgraph_adapter.md §3`. 아래는 참조만.

다음 타입을 **langgraph_adapter.md §3에서 그대로 import** 한다:
`VamosMessage` (LOCK-AP-01), `A2ATaskState` (LOCK-AP-03), `VamosPhase`, `FrameworkTaskRef`, `StateMapping`, `GatePolicy`, `CircuitBreakerState`, `AdapterResult`, `VamosTask`.

본 문서 전용 추가 타입:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class MagenticAgentRole(BaseModel):
    """Magentic-One 에이전트 역할 ↔ VAMOS Blue Node 매핑"""
    magentic_role: Literal["orchestrator", "web_surfer", "file_surfer", "coder", "computer_terminal"]
    vamos_blue_node: Literal["orange_core", "research", "dev", "content", "quant", "trading"]
    permission_level: Literal[0, 1, 2, 3, 4, 5]  # LOCK-AP-02
    sub_agent_slot: Literal["lead", "sub1", "sub2"]  # LOCK-AP-05, LOCK-AT-014

class ProgressLedger(BaseModel):
    """Orchestrator 가 매 step 갱신하는 진행 기록"""
    task_id: str
    iteration: int
    completed_steps: list[str]
    pending_steps: list[str]
    blockers: list[str] = Field(default_factory=list)
    replan_required: bool = False
    confidence: float  # LOCK-AP-10 HITL 트리거 < 50%

class TaskLedger(BaseModel):
    """Orchestrator 가 계획·재계획 시 사용하는 작업 원장"""
    task_id: str
    facts_known: list[str]
    facts_to_lookup: list[str]
    plan_steps: list[str]                     # 고수준 계획
    assignments: dict[str, str]                # step -> agent_id
    revision: int = 0
    created_at: datetime
```

---

## §4. Magentic-One → VAMOS Blue Node 매핑

| Magentic-One 원본 | VAMOS 매핑 | 정본 소유 | Permission Level |
|------|-----------|----------|-------|
| Orchestrator | ORANGE CORE (Lead) | #2-1 Blue Node Architecture | L2 (조정) |
| WebSurfer | Research Node ⊃ WebSurfer | #2-1 Research Node | L0 (읽기 전용) |
| FileSurfer | Dev Node / Research Node (파일 시스템 탐색) | #2-1 Dev Node | L1 (생성) ~ L2 (수정) |
| Coder | Dev Node ⊃ Coder | #2-1 Dev Node | L3 (실행) |
| ComputerTerminal | Dev Node ⊃ Terminal | #2-1 Dev Node + #4-1 Rust-Tauri Infra | L3 (실행) + sandbox |
| (추가) InvestmentSurfer | Quant Node / Trading Node | #2-1 Quant/Trading | L3~L5 |
| (추가) ContentCreator | Content Node | #2-1 Content Node | L1 (생성) |

> **STEP7-K L469~L473 원문 참조** — "ORANGE CORE = Orchestrator / Research Node ⊃ WebSurfer / Dev Node ⊃ Coder + ComputerTerminal / 추가: InvestmentSurfer, ContentCreator".

---

## §5. Orchestrator 루프 (의사코드, Big-O: O(N×K))

N = plan_steps 수, K = 평균 agent 호출 라운드. 시간복잡도 표기는 Orchestrator 자체 loop 기준.

```python
def magentic_one_loop(
    request: VamosMessage,
    team: list[MagenticAgentRole],     # 정확히 3개 (Lead + 2 Sub), LOCK-AP-05
) -> AdapterResult:
    # Step 1: Task Ledger 초기화
    ledger = TaskLedger(
        task_id=request.id,
        facts_known=extract_facts(request),
        facts_to_lookup=[],
        plan_steps=orchestrator_plan(request),
        assignments=assign_agents(request, team),  # LOCK-AT-014 V1=3 제약
        created_at=datetime.utcnow(),
    )
    # Step 2: Progress Ledger 루프
    progress = ProgressLedger(task_id=request.id, iteration=0,
                              completed_steps=[], pending_steps=ledger.plan_steps,
                              confidence=1.0)
    while not is_satisfied(progress, ledger):
        progress.iteration += 1
        # 2.1 각 pending step 을 할당된 agent 가 실행
        for step_id in progress.pending_steps[:]:
            agent_id = ledger.assignments[step_id]
            result = call_agent(agent_id, step_id, progress)
            if result.blocked:
                progress.blockers.append(f"{step_id}:{result.reason}")
            else:
                progress.completed_steps.append(step_id)
                progress.pending_steps.remove(step_id)
            progress.confidence = update_confidence(progress, result)
            # LOCK-AP-10: confidence < 0.5 -> HITL 에스컬레이션
            if progress.confidence < 0.5:
                escalate_hitl(progress, ledger, route="I-19")
                return AdapterResult(status="hitl_required", progress=progress)
        # 2.2 Orchestrator 자가 점검 → 재계획 필요 판단
        if progress.replan_required or len(progress.blockers) >= 3:
            if ledger.revision >= REPLAN_LIMIT:   # =3 (§8/§11.3) — 무한 replan 방지
                escalate_hitl(progress, ledger, route="I-19")
                return AdapterResult(status="hitl_required", progress=progress)
            ledger = replan(ledger, progress)   # Task Ledger revision++
            progress.pending_steps = ledger.plan_steps[:]
            progress.blockers = []
        # 2.3 비용 상한 체크 — LOCK-AP-09 V2 ₩93K
        if cost_so_far(request.id) > BUDGET_V2_KRW_93000:
            return AdapterResult(status="cost_gate_blocked", progress=progress)
    return AdapterResult(status="completed", progress=progress)
```

**ABC 패턴 매핑** (base_reasoning_engine_abc.md): `magentic_one_loop` 은 `ReasoningEngineABC.run(...)` 서브클래스 구현. sync 계약 준수.

---

## §6. LOCK 매핑

| LOCK ID | 항목 | 원본 문서 | 값 | 본 문서 적용 |
|---------|------|----------|-----|-------------|
| LOCK-AP-01 | VamosMessage 스키마 | STEP7-K, D2.0-05 | 6필드 (id, type, source, target, content, metadata) | Orchestrator ↔ Sub-Agent 통신은 전수 VamosMessage, 6필드 외 추가 금지 |
| LOCK-AP-02 | Permission Level | STEP7-K K-041 | 0~5 | §4 테이블의 각 Magentic 역할에 L0~L5 배정, Coder/ComputerTerminal = L3 (사용자 확인 필요 시 L4) |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 | Lead + max 2 Sub-Agent | Magentic-One 원본 5-agent → 3-agent 축소 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | WebSurfer 가 외부 A2A Agent Discovery 로 Research Node 와 상호 호출 시 필수 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K / V2: ₩93K / V3: ₩266K | §5 Orchestrator 루프 2.3 단계에서 BUDGET_V2_KRW_93000 체크 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety/guardrail_rules.md 정본) | HITL 트리거 < 50% | §5 progress.confidence < 0.5 시 I-20 에스컬레이션 |
| LOCK-AT-014 (6-3 정본) | Agent Team size | 6-3 AUTHORITY_CHAIN.md L67 (SPEC S7-A-008) | V1=3 / V2=10 / V3=50+ | V2 Phase 2 본 문서 시점 **3-agent 상한 유지** (V2 10-agent 확장은 6-3 본 도메인 정본 변경 선행 조건 후 적용) |

---

## §7. §6 Issues 해소 증거

### FR-9 어댑터 호환성 매트릭스 (K-030과 결합, `tool_memory_benchmark.md §3` 상세)

| 프레임워크 | Magentic-One 도입 가능 | VAMOS 수용 버전 | 비고 |
|-----------|----------------------|--------------|------|
| LangGraph 0.2.x | ✅ (StateGraph 노드 = Magentic agent) | V1 (V1 어댑터 기반, Orchestrator=루트) | LOCK-AP-08 START/END 상수 |
| CrewAI 0.70+ | ⚠ 부분 (Sequential/Hierarchical) | V2 (Hierarchical Process + manager_llm) | `allow_delegation=True` + max 2 sub |
| AutoGen 0.4+ | ✅ GroupChatManager = Orchestrator | V2 | `GroupChat.admin_name` = Orchestrator |

### FR-7 Agent Teams 역할 선정 (6-3 연계)
Magentic-One 역할 계층 → Lead(Orchestrator) + 2 Sub(기능별) 로 평탄화. 역할 선정 알고리즘은 `06_autonomy-safety/agent_mode_autonomy_mapping.md` V1 Permission Matrix와 결합하여 **권한 수준 매칭** + **Blue Node 전문성 매칭** 2단 평가.

---

## §8. Phase별 복구/다운그레이드 흐름

```
Phase 1 (Plan 단계 실패) → Orchestrator 재계획 (Task Ledger revision++) → 3회 실패 시 HITL
Phase 2 (Execute 단계 blocker) → Progress Ledger.blockers 기록 → blockers >= 3 시 재계획
Phase 3 (Verify 단계 confidence 하락) → LOCK-AP-10 < 50% → I-20 에스컬레이션
Phase 4 (Deliver 단계 비용 초과) → LOCK-AP-09 V2 ₩93K → Cost Gate 차단
```

confidence penalty:
- blocker 1개 발생 → -0.1
- agent timeout → -0.15
- LOCK 위반 감지 → -0.3 (즉시 HITL)
- tool 호출 실패 → -0.08

---

## §9. 에스컬레이션 페이로드 (I-20 경유)

```python
class MagenticEscalation(BaseModel):
    source_engine: Literal["magentic_one_orchestrator"] = "magentic_one_orchestrator"
    error_code: Literal["HITL_CONFIDENCE_LOW", "COST_GATE_BLOCKED", "REPLAN_LIMIT", "LOCK_VIOLATION"]
    original_request: VamosMessage
    partial_result: Optional[dict]
    retry_count: int
    progress_ledger: ProgressLedger
    task_ledger: TaskLedger
    trace_id: str
    timestamp: datetime
```

---

## §10. 로깅 포맷 (R-01-7 structured JSON)

```json
{
  "trace_id": "...",
  "error": {"code": "REPLAN_LIMIT", "message": "task ledger revision 3 reached"},
  "context": {"orchestrator_agent_id": "...", "iteration": 3, "team_size": 3, "lock_at_014": "V1=3"},
  "recovery": {"action": "hitl_escalation", "route": "I-20", "reason": "replan_limit"}
}
```

---

## §11. Phase 3 테스트 시나리오 (10건)

1. **정상 플로우**: Orchestrator 가 plan_steps=5 생성 → Sub1/Sub2 가 순차 처리 → 5/5 완료 → 상태 `completed`.
2. **재계획 트리거**: Sub1 이 step3 에서 blocker 2회 → replan → revision=1 → 재시도 성공.
3. **재계획 한도 초과**: revision=3 에서도 unresolved blocker → `REPLAN_LIMIT` → HITL.
4. **confidence 하락**: 3 step 연속 실패 → confidence=0.45 < 0.5 → I-20 에스컬레이션.
5. **LOCK-AT-014 위반 시도**: team=4 agent 로 호출 → `[VIOLATION:LOCK-AT-014 exceeded V1=3]` + 거부.
6. **비용 초과**: Orchestrator + 2 sub 누적 ₩95K → BUDGET_V2_KRW_93000 초과 → `cost_gate_blocked`.
7. **Tool 호출 실패 (WebSurfer)**: Brave Search 429 → retry 1회 → 실패 시 confidence -0.08 → Replan 아님.
8. **외부 A2A Agent 합류**: Magentic-One Sub2 가 외부 A2A Agent 대체 → LOCK-AP-07 A2A+MCP 양방향 확인.
9. **권한 초과 시도**: Coder 가 Permission L5 작업(결제) 시도 → LOCK-AP-02 차단 → `[BLOCKED:permission_level_violation]`.
10. **MoA 협업 요청**: Orchestrator 가 Sub2 대신 MoA Aggregator 호출 → `moa_pattern.md §5` Aggregator 단계로 위임.
11. **Magentic-One + LangGraph**: LangGraph StateGraph 노드에서 Magentic Orchestrator 호출 → Phase 2 `execute` 상태에서만 활성.
12. **Magentic-One + CrewAI Hierarchical**: CrewAI `manager_llm` = Orchestrator, `agents` = 2 sub → LOCK-AP-05 정합.

---

## §12. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 일치 여부 |
|------------|-----------|-----------|
| langgraph_adapter.md §3 공통 타입 | VamosMessage, VamosPhase, FrameworkTaskRef | ✅ import 경로 일치 |
| moa_pattern.md §3 | MoA Aggregator 호출 시 VamosMessage type="task" | ✅ K-049 LOCK-AP-01 정합 |
| reflection_planning.md §4 | Planning 단계가 Orchestrator 의 plan_steps 생성에 재사용 | ✅ 인터페이스 `orchestrator_plan(request)` 이 planning.py 의 ReAct 출력 |
| 06_autonomy-safety/permission_matrix.md | Permission Level 0~5 매칭 | ✅ LOCK-AP-02 |
| 06_autonomy-safety/guardrail_rules.md | LOCK-AP-10 confidence < 0.5 | ✅ DEFINED-HERE 경계 준수 |
| 6-3 Agent-Teams-PARL AUTHORITY_CHAIN.md L67 | LOCK-AT-014 V1=3 | ✅ 본 문서 §2.3, §4, §6, §11 전수 verbatim |

---

## §13. 검증 자가 체크리스트

- [x] §1 교차 참조 블록 포함
- [x] §3 공통 자료 구조 langgraph_adapter.md §3 참조 (중복 정의 금지)
- [x] LOCK-AP-01/02/05/07/09/10 + LOCK-AT-014 분리 인용 (5필드: ID × 항목 × 원본 × 값 × 재정의)
- [x] LOCK-AP-05 × LOCK-AT-014 교차 verbatim 인용 (§2.3, §6)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§11: 12건)
- [x] 에스컬레이션 페이로드 Python class (§9)
- [x] 로깅 포맷 structured JSON 중첩 3-block (§10)
- [x] V2-Phase 2 헤더 태그
- [x] R6 준수 (What+How 전용)
- [x] FABRICATION 10종 census — 0 hits (marker 문자열 literal 포함 금지)

---

*정본 소유: #13 Agent-Protocol-Interoperability / 01_framework-adapters*
*V2-Phase 2 최초 작성: 2026-04-22 (STAGE 7 STEP_B #2a)*
