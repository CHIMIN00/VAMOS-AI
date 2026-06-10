# S-7 Evolution Scheduler — 상세 설계 (L3)

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-6_Self-Evolution-System / 01_s-series-modules
> **Tier**: 6 (System-wide Components)
> **정본 출처**: D2.0-02 §10.4~§10.6 (LOCK), D2.0-01 §5.7 (명칭 LOCK), Part2 V3-Phase 2 L4099-L4115 (S-Module When/Where·ABC)·L4119 (ABC 시그니처)·L4063/L4306 (순차 활성화 L6), 종합계획서 부록 A.3 (S-7: Cron 기반. 우선순위 큐 + 의존성 DAG 검사)
> **LOCK 매핑**: L1(모듈 목록), L2(I-Module 경유 — I-12 READ / I-18 READ), L3(S-8 승인 필수 — 실행 전 gate), L4(자동 적용 금지 — 반영 주체는 6-13 Operations), L6(순차 활성화 — S-6 안정화 후 활성화), L7(BaseSelfEvo ABC)
> **Phase**: P1-M6
> **생성일**: 2026-04-14
> **ISS 해결**: ISS-1 (S-7 알고리즘 힌트 소비 — Cron 기반 + 우선순위 큐 + 의존성 DAG)

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **D2.0-02 §10.4~§10.6** | S-Module 경유 동작 원칙 정본 (LOCK L2). "S-3~S-7 후보→S-8 승인→반영+I-15 스냅샷+I-9 로그" 흐름 (L3) |
| **D2.0-01 §5.7** | S-Module 명칭·카테고리 LOCK (S-7 = "Evolution Scheduler") |
| **Part2 V3-Phase 2 L4099-L4115** | S-7 When(S-3/S-6 출력 수신 시)/Where(backend/vamos_core/self_evo/s07_evolution_scheduler.py) 정본 — I/O: `list[EvolutionPlan]` → `ScheduledEvolution(plan_id, execute_at, dependencies)` |
| **Part2 V3-Phase 2 L4119** | BaseSelfEvo ABC 시그니처 정본 (`async def evolve()`, `async def evaluate() -> float`, `async def rollback(snapshot_id: str) -> bool`) |
| **Part2 V3-Phase 2 L4063 / L4306** | **순차 활성화 규칙(L6)** 정본 — S-2 → S-3 → S-4 → S-5 → S-6 → S-7 → S-8 순서. S-7은 S-6 안정화 후 활성화 |
| **종합계획서 §7 P1-M6** | Cron 기반 스케줄링 힌트, S-2~S-6 오케스트레이션, I-Module 호출 순서(I-18→I-9→I-12→I-6→I-15) 힌트 |
| **종합계획서 부록 A.3** | S-7 알고리즘 힌트: "Cron 기반. 우선순위 큐 + 의존성 DAG 검사" |
| **01_s-series-modules/_index.md §1.1** | S-7 역할·Input(`list[EvolutionPlan]`)·Output(`ScheduledEvolution`)·트리거(S-3/S-6 출력 수신 시) 정본 |
| **01_s-series-modules/_index.md §2.3** | 접근 매트릭스 정본 — **S-7 = I-12 READ, I-18 READ** (I-6/I-9/I-14/I-15/I-19 직접 접근 금지) |
| **01_s-series-modules/_index.md §3.1/§3.2** | BaseSelfEvo ABC 시그니처, 에러 핸들링 기본 정책(DH-2 S-8 timeout=600초) 정본 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1/L2/L3/L4/L6/L7 레지스트리 |
| **s02_pattern_miner.md (P1-M1)** | 스케줄된 반영 후 S-2에 `RegressionRequest(source_module="S-7")` 회귀 의뢰 (L8). `RegressionRequest` 스키마 정본은 s02 §2 |
| **s03_strategy_optimizer.md (P1-M2)** | `EvolutionPlan` 스키마 **정본 재사용** (S-7은 소비자). S-3 출력 수신 시 S-7 트리거 — 01/_index.md §1.1 정본 |
| **s04_performance_monitor.md (P1-M3)** | S-7 단독 트리거 없음. S-4의 `EnvironmentAlert`은 S-6 경유 후 S-6이 생성한 `EvolutionPlan`으로 간접 공급 |
| **s05_feedback_loop.md (P1-M4)** | S-7 단독 트리거 없음. S-5는 S-3/S-6에 후보 힌트만 전달 |
| **s06_adaptation_engine.md (P1-M5)** | `EvolutionPlan(source_module="S-6")` 공급자. S-6 승인된 plan → S-7 스케줄 큐 적재 (s06 §9.2 후속 계약 재확인) |
| **s08_governance (P2 예정)** | **S-7 실행 직전(pre-exec) S-8 승인 gate**(L3): D2.0-02 §10.6 "S-3~S-7 후보→S-8 승인→반영" + 01/_index.md §1.1 "S-8 트리거 = S-7 스케줄 실행 시". 실행 결과 통보 및 rollback 대행 |
| **02_self-improvement-loop/** | ISS-3 5단계 중 "Execute(S-7)" 단계의 주 담당 모듈 — S-8 승인 plan의 `execute_at` 도래 시 반영 트리거 발행 (자동 반영 경로는 6-13 Operations 보유, L4) |
| **03_model-upgrade-strategy/** | 모델 교체성 plan은 canary_rollback.md(ISS-6) 스케줄 슬롯 정책과 의존성 DAG를 공유 |
| **6-12 Event-Logging** | `oc.self_evo.s07.*` 이벤트 기록 대상 (R-01-7 구조화 로깅) |
| **6-13 Operations** | 스케줄 도래 시 실행 주체 — S-7은 큐/알람만 관리, 반영은 Operations |
| **6-4 Memory-RAG-Storage** | I-15 스냅샷 경로(S-7은 WRITE 없음, 스냅샷 ID는 plan에 사전 첨부됨 — S-6/S-3 책임) |
| **6-2 Security-Governance** | EscalationPayload(I-20) ADMIN+ 에스컬레이션 대상 |

---

## 1. 개요

S-7 Evolution Scheduler는 Self-Evolution 서브시스템의 **오케스트레이션 엔진**이다. S-3 Strategy Optimizer 및 S-6 Adaptation Engine이 S-8에 제출하여 승인된 `EvolutionPlan` 목록을 수신·정렬·스케줄링하여, 적절한 시점(`execute_at`)에 **반영 트리거**를 발행한다. 스케줄링 알고리즘은 **Cron 기반 주기 실행**(정기 점검 윈도우) + **우선순위 큐**(risk/비용 가중치) + **의존성 DAG 검사**(plan 간 선후행)를 결합한다. S-2~S-6 오케스트레이션 순서는 LOCK L6 순차 활성화를 기반으로 하며, **실행 직전 S-8 재확인 gate**(L3)를 반드시 경유한다. 자동 적용 금지(L4) 원칙에 따라 본 모듈은 **반영 경로를 보유하지 않고**, 도래 시점에 6-13 Operations에 반영 트리거만 발행한다. BaseSelfEvo ABC(L7)를 구현하며, S-6 안정화(L6) 후 활성화된다.

### 1.1 책임 요약
- **승인 plan 수신**: S-8이 approve한 `EvolutionPlan`을 구독 (`source_module` ∈ {"S-3", "S-6"})
- **스케줄 결정**: Cron 윈도우(정기 점검 슬롯) + 우선순위 큐(risk×비용×age) + 의존성 DAG 검사
- **의존성 DAG**: plan 간 전·후행 의존 탐지(예: 동일 `target_param` 순차화, 스냅샷 체인)·순환 검출
- **실행 트리거 발행**: `execute_at` 도래 시 **S-8 pre-exec 재확인** → 통과 시 6-13 Operations에 반영 요청
- **S-2~S-6 오케스트레이션 순서(L6 기반)**: 스케줄 순서는 원천 모듈 안정화 의존을 반영 — S-2 → S-3 → S-4 → S-5 → S-6 우선 가중치, 동일 우선순위는 risk 오름차순
- **자동 적용 금지(L4)**: 본 모듈은 설정 파일·파라미터 저장소를 직접 수정하지 않는다. 실행 주체는 6-13 Operations
- **I-Module 경유(L2)**: I-12 READ(워크플로우 조회·실행 윈도우 충돌 확인), I-18 READ(스케줄 엔트리 조회) — 접근 매트릭스 §2.3 정본
- **순차 활성화(L6)**: S-6 DH-1 안정화(에러율<1%, 스키마 검증률=100%, 3주기 연속 PASS) 통과 후에만 활성화
- **회귀 검증(L8)**: 반영 완료 후 S-2에 `RegressionRequest(source_module="S-7")` 발행 (원 plan의 source_module은 context로 동봉)

### 1.2 입출력 요약 (01/_index.md §1.1 정합)
- **Input**: `list[EvolutionPlan]` (S-8 approve 이벤트 구독; s03 §2 정본 스키마)
- **Output**: `ScheduledEvolution(plan_id, execute_at, dependencies)` (Part2 V3-P2 정본)
- **트리거**: S-3/S-6 출력 수신 시(S-8 승인 경유). Cron 주기(정기 점검 슬롯)에도 활성화되어 큐 상태 점검

### 1.3 5-stage 매핑 (LOCK L5 대조, Part2 L3078 정합)

| L5 단계 | 본 모듈 행위 | 산출 |
|---------|-------------|------|
| ① 수집 | `collect_plans()` — S-8 approved 이벤트 큐 pop + I-18 READ 현재 스케줄 상태 | `list[EvolutionPlan]` |
| ② 분석 | `analyze_dependencies()` — DAG 구축·순환 검출·우선순위 점수 산정 | `ScheduleGraph` |
| ③ 제안 | `propose_schedule()` — Cron 윈도우 매칭 + 우선순위 선점 → `ScheduledEvolution` 배치 | `list[ScheduledEvolution]` |
| ④ 검증 | `pre_exec_gate()` — `execute_at` 도래 시 S-8 재확인(L3) + 선행 의존 완료 확인 | `PreExecVerdict` |
| ⑤ 적용 | 6-13 Operations에 반영 요청 발행(본 모듈은 경로 보유 금지 — L4) + S-2 회귀 의뢰(L8) | 이벤트만 |

---

## 2. 공통 자료 구조 선정의 (Pydantic, Rule k)

> `EvolutionPlan`은 **s03 §2 정본을 재사용**(S-7은 소비자, 신규 정의 없음). `RegressionRequest`는 **s02 §2 정본을 재사용**. `EscalationPayload`는 s02/s03/s04/s05/s06 정합.

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime, timedelta

# ── 외부 정본 재사용 (import만) ───────────────────────────────
# from .s03_strategy_optimizer import EvolutionPlan, OptimizedStrategy
# from .s02_pattern_miner      import RegressionRequest

# ── 스케줄 엔트리 (I-18 경유 조회 대상) ────────────────────────
class ScheduleEntry(BaseModel):
    """I-18 스케줄 엔트리(캘린더 슬롯). S-7은 READ만 (§3.2, _index.md §2.3).

    Cron 표현식 + 창(window). 정기 점검 슬롯 vs 임시 슬롯 구분.
    """
    entry_id: str
    cron_expr: str                                 # 표준 Cron (5-field) 또는 Quartz-like
    window_start_offset_sec: int = 0
    window_duration_sec: int = 900                 # 기본 15분 창
    slot_type: Literal["routine", "urgent", "canary", "maintenance"]
    max_concurrent: int = 1                        # 동시 실행 상한 (동일 slot_type)
    timezone: str = "UTC"
    active: bool = True

# ── 우선순위 큐 엔트리 ─────────────────────────────────────────
class PriorityQueueItem(BaseModel):
    """우선순위 큐 힙 노드. score 작을수록 먼저 실행(min-heap).

    score = W_ORIGIN*origin_rank + W_RISK*risk_rank
          + W_AGE*(-age_sec)    + W_COST*cost_rank
    (§4.2 상세)
    """
    plan_id: str
    source_module: Literal["S-3", "S-6"]            # 01/_index.md S-7 트리거 정본
    origin_rank: int                                # S-2~S-6 오케스트레이션 순위(L6 파생)
    risk_rank: int                                  # 0=low, 1=medium, 2=high
    cost_rank: int                                  # 0=low .. 2=high (expected_cost 버킷)
    age_sec: float                                  # enqueued_at 이후 경과
    score: float                                    # 계산된 정렬 키 (min-heap)
    enqueued_at: datetime

# ── 의존성 DAG 노드/엣지 ───────────────────────────────────────
class PlanDependency(BaseModel):
    """plan_id 간 선후행 엣지."""
    upstream_plan_id: str
    downstream_plan_id: str
    kind: Literal["same_target_param", "snapshot_chain",
                  "origin_order", "manual"] = "same_target_param"
    rationale: str = ""

class ScheduleGraph(BaseModel):
    """현재 사이클의 DAG 스냅샷 (cycle-local)."""
    graph_id: str
    nodes: list[str]                                # plan_id 목록
    edges: list[PlanDependency]
    has_cycle: bool = False
    topo_order: list[str] = []                      # 순환 없을 때 위상 정렬

# ── 잡 실행 컨텍스트 ───────────────────────────────────────────
class JobContext(BaseModel):
    """스케줄 실행 단위. S-7이 생성 → 6-13 Operations가 소비(L4)."""
    job_id: str
    plan_id: str
    source_module: Literal["S-3", "S-6"]
    scheduled_at: datetime
    execute_at: datetime                             # Cron 윈도우 내 결정치
    dependencies: list[str] = []                     # 선행 plan_id (위상 정렬 전제)
    slot_entry_id: str                               # ScheduleEntry.entry_id
    priority_score: float
    pre_exec_verdict: Optional[Literal["PASS", "HOLD",
                                        "ABORT_S8_REJECT",
                                        "ABORT_DEP_FAIL",
                                        "ABORT_WINDOW_CONFLICT"]] = None
    pre_snapshot_id: Optional[str] = None            # plan.rollback_snapshot_id 복사
    trace_id: str
    attempt: int = 1
    max_retries: int = 2                             # Cron 다음 슬롯 재시도 상한

# ── S-7 정본 출력 (Part2 V3-P2 정본 필드) ─────────────────────
class ScheduledEvolution(BaseModel):
    """S-7 정본 Output (01/_index.md §1.1 / Part2 L4115)."""
    plan_id: str
    execute_at: datetime
    dependencies: list[str]                          # plan_id 목록
    # ── 본 세션에서 추가되는 운영 필드 (정본 필드 하위 확장, 순서 유지) ──
    job_id: str
    source_module: Literal["S-3", "S-6"]
    slot_entry_id: str
    priority_score: float
    risk_rank: int
    age_sec_at_schedule: float
    trace_id: str

# ── pre-exec gate 결과 ────────────────────────────────────────
class PreExecVerdict(BaseModel):
    job_id: str
    plan_id: str
    verdict: Literal["PASS", "HOLD", "ABORT_S8_REJECT",
                     "ABORT_DEP_FAIL", "ABORT_WINDOW_CONFLICT"]
    reason: Optional[str] = None
    s8_reconfirm_at: Optional[datetime] = None
    next_try_at: Optional[datetime] = None            # HOLD 시 다음 시도

# ── BaseSelfEvo 반환 구조 (L7 정본, s02~s06 정합) ─────────────
class EvolutionResult(BaseModel):
    module_id: str = "s07"
    scheduled: list[ScheduledEvolution]               # 이번 주기 결정분
    deferred_plans: list[str] = []                    # 윈도우 미충족/HOLD
    executed_jobs: list[str] = []                     # 도래 후 trigger 발행 완료
    aborted_jobs: list[str] = []                      # S-8 재거부 등
    dag_cycle_detected: bool = False
    duration_ms: int
    status: Literal["SUCCESS", "PARTIAL", "FAILED",
                    "EMPTY", "S6_NOT_STABLE"]

class HealthStatus(BaseModel):
    module_id: str = "s07"
    healthy: bool
    last_run_at: Optional[datetime] = None
    error_count_7d: int
    schema_validation_rate: float
    imodule_call_success_rate: float
    queue_depth: int
    dag_cycle_count_7d: int
    pre_exec_reject_rate_7d: float
    on_time_ratio_7d: float                           # execute_at ± 30s 내 발행 비율
    deferred_ratio_7d: float

# ── 에스컬레이션 페이로드 (I-20, R-01-8, s02~s06 정합) ─────────
class EscalationPayload(BaseModel):
    source_engine: str = "s07_evolution_scheduler"
    error_code: str
    original_request: dict
    partial_result: Optional[dict] = None
    retry_count: int
    timestamp: datetime
    trace_id: str
    severity: Literal["info", "warn", "error", "critical"]
```

---

## 3. BaseSelfEvo ABC 구현 명세 (LOCK L7)

> 정본: 01_s-series-modules/_index.md §3.1. **시그니처 임의 변경 금지(Rule h/i).**
> Part2 V3-P2 정본(L4119): `async def evolve()`, `async def evaluate() -> float`, `async def rollback(snapshot_id: str) -> bool`.

### 3.1 클래스 스켈레톤

```python
class EvolutionScheduler(BaseSelfEvo):
    """S-7 Evolution Scheduler — L7 BaseSelfEvo 구현.

    정본 시그니처 준수(Part2 L4119):
      - evolve() -> EvolutionResult        # plan 수집→DAG→스케줄→pre-exec gate→트리거
      - evaluate() -> float                # on-time 비율·DAG 건전성·pre-exec 통과율
      - rollback(snapshot_id: str) -> bool # 스케줄 자체 복원(큐/DAG/엔트리 선택). 반영 rollback은 S-8 대행

    순차 활성화(L6, Part2 L4063/L4306): S-2→S-3→S-4→S-5→S-6 전 단계 DH-1
    안정화(에러율<1%, 스키마 검증률=100%, 3주기 연속 PASS) 통과 후에만 활성화.
    특히 S-6 안정화가 본 모듈의 직전 gate.

    자동 적용 금지(L4): 본 모듈은 파라미터·설정 파일·저장소를 직접 수정하지
    않는다. execute_at 도래 시 JobContext 기반 반영 트리거만 6-13 Operations
    에 발행하며, 실제 적용 주체는 Operations이다. S-8 pre-exec 재확인(§4.4,
    L3)과 S-2 회귀 의뢰(L8)를 반드시 수반한다.

    I-Module 제한(L2): I-12 READ, I-18 READ만 보유. I-15/I-19/I-6/I-9 직접
    접근 금지 (§3.2). I-15 스냅샷 ID는 plan.rollback_snapshot_id로 간접
    수신, I-19 승인은 S-8 단독 권한이며 본 모듈은 S-8에 재확인을 요청할 뿐
    직접 WRITE 금지.
    """

    MODULE_ID = "s07"
    CRON_TICK_SEC            = 30                 # 주기 점검 간격
    S8_PREEXEC_TIMEOUT_SEC   = 10                 # pre-exec 재확인 타임아웃(DH-7)
    S8_DEFAULT_TIMEOUT_SEC   = 600                # DH-2 준수
    DEFAULT_WINDOW_SEC       = 900                # 15분 슬롯
    MAX_QUEUE_DEPTH          = 500                # 큐 상한
    MAX_JOBS_PER_TICK        = 20                 # tick당 최대 발행 수
    COOLDOWN_SAME_PARAM_SEC  = 300                # 동일 target_param 반복 방지(s06 정합)
    MAX_RETRIES              = 2                  # Cron 다음 슬롯 재시도
    # 우선순위 가중치 (DH-7a)
    W_ORIGIN = 1.0
    W_RISK   = 2.0                                 # high risk일수록 후순위
    W_AGE    = -0.01                               # 오래된 plan 우대(부호 주의)
    W_COST   = 0.5

    async def evolve(self) -> EvolutionResult:
        """plan 수집→DAG 분석→스케줄 결정→pre-exec gate→트리거 발행.

        단계 (LOCK L5):
          ① 수집:
             - IF NOT S6_STABLE(): return EMPTY (L6 gate)
             - approved_plans ← S8_APPROVED_QUEUE.drain(MAX_JOBS_PER_TICK)
             - schedule_entries ← I18.list_entries()        (L2 READ)
          ② 분석 (의존성 DAG):
             - dag ← BUILD_DAG(approved_plans + pending_queue)
             - IF dag.has_cycle: EMIT error, abort cycle, drop 가해자
             - topo ← TOPO_SORT(dag)
          ③ 제안 (Cron 윈도우 + 우선순위 큐):
             - FOR p IN topo: score ← PRIORITY_SCORE(p) ; heap.push((score, p))
             - next_window ← NEXT_CRON_SLOT(schedule_entries, slot_type_of(p))
             - plan에 execute_at 할당 + max_concurrent 검사
          ④ 검증 (pre-exec gate, 도래 시):
             - pre_exec_gate(job): S8.reconfirm(plan_id) + DEP_DONE 확인
             - verdict in {PASS, HOLD, ABORT_*}
          ⑤ 적용 (트리거 발행, 경로 보유 금지 — L4):
             - OPS.trigger_apply(job_context)
             - on-complete: S2.RegressionRequest(source_module="S-7",
                                                 context={origin: plan.source_module})
             - I-12 READ로 워크플로우 상태 확인(실행 충돌 없음)
        """

    async def evaluate(self) -> float:
        """모듈 성능 점수 (0.0~1.0).

        공식:
          score = 0.35 * on_time_ratio_7d
                + 0.20 * (1 - pre_exec_reject_rate_7d)
                + 0.15 * schema_ok_rate
                + 0.15 * (1 - deferred_ratio_7d)
                + 0.10 * (1 - dag_cycle_count_7d/max(1, total_cycles_7d))
                + 0.05 * imodule_call_success_rate
        DH-1 안정화 기준(에러율<1%, 스키마 100%)을 하한으로 강제.
        """

    async def rollback(self, snapshot_id: str) -> bool:
        """스케줄 상태(큐/DAG/선점 엔트리 매핑) 복원.

        - 대상: PriorityQueueItem 집합, ScheduleGraph, job_id↔entry 매핑
        - I-15 스냅샷 WRITE 권한은 S-7에 없음(§3.2) → 스냅샷 생성/복원은
          S-8 대행(s06 동형 패턴).
        - 플랜의 **반영 rollback**(파라미터 되돌림)은 본 모듈 책임이 아님
          → S-8에 `snapshot_id` 복원 요청 전달 (원 plan의
          rollback_snapshot_id 사용).
        - 실패 시 SELF_EVO_ROLLBACK_FAIL → ADMIN+ 에스컬레이션(I-20).
        """

    def get_module_id(self) -> str:
        return self.MODULE_ID

    async def health_check(self) -> HealthStatus:
        ...
```

### 3.2 I-Module 접근 권한 (정본: 01/_index.md §2.3)

| I-Module | 권한 | 용도 |
|----------|------|------|
| I-12 워크플로우 | **READ** | 현재 워크플로우 상태 조회(실행 윈도우 충돌·동시성 한도 확인) |
| I-18 스케줄 | **READ** | `ScheduleEntry`(Cron 슬롯) 목록 조회·다음 슬롯 계산 |
| I-6 QoD | — | 직접 접근 금지 (S-8 pre-exec 결정은 S-8 내부에서 QoD 참조) |
| I-9 로그/메트릭 | — | 직접 접근 금지. 이벤트 emit은 버스 경유(6-12 Event-Logging) |
| I-14 QA | — | 직접 접근 금지 |
| I-15 스냅샷 | — | 직접 접근 금지. plan.rollback_snapshot_id로 **간접 수신**, WRITE/복원은 S-8 대행 |
| I-19 승인 | — | **직접 접근 금지** — S-8 단독 WRITE. pre-exec 재확인도 S-8에 요청만 발행 |

> **주의 (Rule j 정합)**: 종합계획서 §7 P1-M6 절차 5 "I-Module 경유 호출 순서: I-18(스케줄) → I-9(로그) → I-12(워크플로우) → I-6(QoD) → I-15(스냅샷)" 지시 중 **I-9/I-6/I-15는 S-7 직접 권한이 아니다** (01/_index.md §2.3, 부록 A.4). 해석: (a) I-9 로그 기록은 6-12 Event-Logging 버스 경유로 치환, (b) I-6 QoD는 S-8이 pre-exec 재확인 시 내부 참조, (c) I-15는 `plan.rollback_snapshot_id` 간접 수신. 본 파일은 _index.md §2.3(FINAL REVIEW R-6 승인)을 정본으로 채택. 이는 s02/s03/s04/s05/s06 SEVO-C003 확장과 동형. 본 불일치는 §10.2 CONFLICT 후보(**SEVO-C003 확장 S-7**)로 등재.

### 3.3 S-Module 간 연계 (트리거 in-edges / out-edges)

| 방향 | 대상 | 트리거 조건 | 스키마 | 루프 분류 |
|------|------|------------|--------|----------|
| IN  | **S-3 Strategy Optimizer** (간접) | S-8 approve 이벤트 수신 (원천 `source_module="S-3"`) | `EvolutionPlan` (s03 §2) | 전략 루프 |
| IN  | **S-6 Adaptation Engine** (간접) | S-8 approve 이벤트 수신 (원천 `source_module="S-6"`) | `EvolutionPlan` (s03 §2 정본 재사용) | 적응 루프 |
| IN  | **S-8 Governance** | approve 이벤트 발행 / pre-exec 재확인 응답 | `GovernanceDecision` (P2 예정) | L3 gate |
| IN  | I-18 (경유) | 주기적 | `ScheduleEntry` 목록 | 스케줄 |
| IN  | I-12 (경유) | 실행 직전 | 워크플로우 상태 | 충돌 확인 |
| OUT | **S-8 Governance** | pre-exec 재확인 요청 | `{plan_id, job_id, intended_execute_at}` | L3 재확인 |
| OUT | **6-13 Operations** | `execute_at` 도래 + pre-exec PASS | `JobContext` | 반영 트리거 (L4 준수) |
| OUT | **S-2 Pattern Miner** | 반영 완료 시 | `RegressionRequest(source_module="S-7")` (s02 §2 재사용) | 회귀 검증(L8) |
| —   | **S-4 Performance Monitor** | 직접 트리거 없음 (S-4 알림은 S-6 경유) | — | 루프 분리 |
| —   | **S-5 Feedback Loop** | 직접 트리거 없음 | — | 루프 분리 |

---

## 4. 알고리즘 상세 (L3 의사코드, Rule f)

> 시간복잡도(Big-O) + LOCK 참조 + ABC 패턴 매핑.
> 힌트 출처: 종합계획서 부록 A.3 "S-7: Cron 기반. 우선순위 큐 + 의존성 DAG 검사", _index.md §4 힌트 S-7 행.

### 4.1 파이프라인 총괄 (evolve() 본체)

```
ALGORITHM S7_Evolve
INPUT:   s8_approved_queue: Queue[EvolutionPlan],
         pending_queue:     PriorityQueue[PriorityQueueItem],
         dag_state:         ScheduleGraph,
         schedule_entries:  list[ScheduleEntry],         # I-18 READ
         cooldown_tbl:      Dict[target_param, last_applied_at],
         params:            {W_ORIGIN=1.0, W_RISK=2.0, W_AGE=-0.01,
                             W_COST=0.5, MAX_JOBS_PER_TICK=20,
                             DEFAULT_WINDOW_SEC=900,
                             S8_PREEXEC_TIMEOUT=10,
                             MAX_RETRIES=2}
OUTPUT:  EvolutionResult
LOCK:    L1(S-7), L2(I-12/I-18 READ), L3(S-8 승인 + pre-exec 재확인),
         L4(자동 반영 금지 — OPS 경유), L5(①~⑤),
         L6(S-6 선행 안정화), L7(ABC)
ABC-매핑: evolve()

1.  IF NOT S6_STABLE():                                   # L6 gate
2.    RETURN EvolutionResult(status="S6_NOT_STABLE")
3.  # ① 수집
4.  new_plans ← s8_approved_queue.drain(params.MAX_JOBS_PER_TICK)
5.  entries   ← I18.list_entries(active=True)              # L2 READ
6.  wf_state  ← I12.get_workflow_state()                   # L2 READ
7.  IF new_plans == [] AND pending_queue.is_empty() AND not any_job_due():
8.    RETURN EvolutionResult(status="EMPTY")
9.  # ② 분석 — DAG
10. all_plans ← new_plans ∪ pending_queue.snapshot_plans()
11. dag       ← BUILD_DAG(all_plans)                       # O(N^2) — §4.3
12. IF dag.has_cycle:
13.   offenders ← DETECT_CYCLE_EDGES(dag)
14.   EMIT("oc.self_evo.s07.dag_cycle",
           {edges: offenders, trace_id})
15.   all_plans ← DROP(all_plans, offenders.downstream_ids)
16.   dag       ← BUILD_DAG(all_plans)
17. topo ← TOPO_SORT(dag)                                  # O(N+E)
18. # ③ 제안 — 우선순위 큐 + Cron 윈도우 매칭
19. FOR p IN topo:
20.   IF p.plan_id IN pending_queue: CONTINUE              # 재배치 방지
21.   item ← MAKE_QUEUE_ITEM(p, params)                    # §4.2 score
22.   pending_queue.push(item)
23. scheduled ← []
24. deferred  ← []
25. FOR item IN pending_queue.pop_k(params.MAX_JOBS_PER_TICK):
26.   slot ← SELECT_SLOT(entries, item, wf_state)          # §4.4 Cron next
27.   IF slot IS None:
28.     deferred.append(item.plan_id) ; pending_queue.push(item) ; CONTINUE
29.   # cooldown check (동일 target_param 반복 방지)
30.   IF IN_COOLDOWN(item, cooldown_tbl,
                     params.cooldown_default=300):
31.     deferred.append(item.plan_id) ; CONTINUE
32.   job ← BUILD_JOB_CONTEXT(item, slot,
                               plan.rollback_snapshot_id)
33.   dag_state.nodes.append(item.plan_id)
34.   scheduled.append(ScheduledEvolution(plan_id=item.plan_id,
                                           execute_at=job.execute_at,
                                           dependencies=dag.parents(item.plan_id),
                                           job_id=job.job_id,
                                           source_module=item.source_module,
                                           slot_entry_id=slot.entry_id,
                                           priority_score=item.score,
                                           risk_rank=item.risk_rank,
                                           age_sec_at_schedule=item.age_sec,
                                           trace_id=job.trace_id))
35.   EMIT("oc.self_evo.s07.scheduled",
           {plan_id, execute_at, dependencies, score, trace_id})
36. # ④ 검증 (pre-exec gate) — 도래한 job만 처리
37. due_jobs ← DUE_JOBS(scheduled ∪ pending_scheduled, NOW(), tolerance=30s)
38. executed ← [] ; aborted ← []
39. FOR job IN due_jobs:
40.   # 선행 의존 완료 확인 (위상 정렬 준수)
41.   IF NOT ALL_DEPS_DONE(job.dependencies):
42.     job.pre_exec_verdict ← "HOLD"
43.     CONTINUE
44.   # S-8 재확인 (L3) — 승인 당시와 현재 상태 차이 보정
45.   v ← S8.reconfirm(job.plan_id,
                        timeout=params.S8_PREEXEC_TIMEOUT)
46.   IF v.approved == False:
47.     job.pre_exec_verdict ← "ABORT_S8_REJECT"
48.     aborted.append(job.job_id)
49.     EMIT("oc.self_evo.s07.aborted", {job_id, reason: v.reason})
50.     CONTINUE
51.   # 워크플로우 창 충돌 최종 확인
52.   IF I12.has_window_conflict(wf_state, job.slot_entry_id):
53.     job.pre_exec_verdict ← "ABORT_WINDOW_CONFLICT"
54.     IF job.attempt < params.MAX_RETRIES:
55.       RESCHEDULE_NEXT(job) ; CONTINUE
56.     aborted.append(job.job_id) ; CONTINUE
57.   job.pre_exec_verdict ← "PASS"
58.   # ⑤ 반영 트리거 발행 (L4 — 본 모듈 경로 없음)
59.   OPS.trigger_apply(job)                                # 6-13 Operations
60.   cooldown_tbl[target_param_of(job)] ← NOW()
61.   EMIT("oc.self_evo.s07.executed",
         {job_id, plan_id, executed_at: NOW(), trace_id})
62.   # L8 회귀 의뢰 (Operations 완료 통보 수신 후)
63.   ON_OPS_COMPLETE(job): S2.receive(
         RegressionRequest(source_module="S-7",
                           context={origin: job.source_module,
                                    plan_id: job.plan_id}))
64.   executed.append(job.job_id)
65. RETURN EvolutionResult(scheduled=scheduled,
                           deferred_plans=deferred,
                           executed_jobs=executed,
                           aborted_jobs=aborted,
                           dag_cycle_detected=dag.has_cycle,
                           status=RESOLVE_STATUS(scheduled,
                                                  executed, aborted))
```

**총 시간복잡도**: `O(N^2)` DAG 구축 + `O(N log N)` 우선순위 큐 + `O(N+E)` 위상 정렬 + `O(J)` 도래 job 처리. N ≤ MAX_QUEUE_DEPTH=500, 동시 in-flight J ≤ MAX_JOBS_PER_TICK=20 → tick당 경계 상한 `O(500^2)`. 실질 비동기 I/O(I-12/I-18 READ, S-8 reconfirm, OPS trigger)가 지배. SELF_EVO_TIMEOUT(120s) 내부.

### 4.2 PRIORITY_SCORE (우선순위 점수 산정)

```
ALGORITHM PRIORITY_SCORE(plan, params)
# 시간복잡도: O(1)
# ABC-매핑: evolve() ③ 제안
# min-heap 기준 — score 작을수록 먼저 실행
LOCK: 부록 A.3 "우선순위 큐", L6(S-2~S-6 오케스트레이션 순서)

1. origin_rank ← ORIGIN_RANK_MAP[plan.strategy.source_module]
   # L6 파생 순서 (S-2 안정화가 최상류):
   #   S-2 → 1, S-3 → 2, S-4 → 3, S-5 → 4, S-6 → 5
   # S-7 큐에는 S-3/S-6만 들어오므로 실 사용값은 {2, 5}
2. risk_rank   ← {"low":0, "medium":1, "high":2}[plan.risk_hint]
3. cost_rank   ← COST_BUCKET(plan.expected_cost)   # 0..2
4. age_sec     ← NOW() - plan.enqueued_at
5. score ← params.W_ORIGIN * origin_rank
         + params.W_RISK   * risk_rank
         + params.W_AGE    * age_sec                  # 음수 가중 → 오래된 plan 우대
         + params.W_COST   * cost_rank
6. RETURN score
```

> **가중치 근거(DH-7a)**: W_RISK=2.0은 고위험 plan의 후순위화(리드타임 확보) 목적. W_AGE=-0.01은 age가 200s 증가하면 priority가 2.0 감소 → 대기 24분이면 risk 1단계와 동등한 가속 효과. W_ORIGIN=1.0으로 S-6(rank=5) plan이 S-3(rank=2)보다 기본 +3 지연되어 **오케스트레이션 순서(L6)**를 반영한다. W_COST=0.5는 비용 고지연 방지 미세 가중.

### 4.3 BUILD_DAG (의존성 DAG 구축)

```
ALGORITHM BUILD_DAG(plans)
# 시간복잡도: O(N^2) — param/snapshot 매칭
# ABC-매핑: evolve() ② 분석
LOCK: 부록 A.3 "의존성 DAG 검사"

1. nodes  ← [p.plan_id for p in plans]
2. edges  ← []
3. # 엣지 추출 규칙
4. FOR i IN 0..len(plans)-1:
5.   FOR j IN 0..len(plans)-1 WHERE i != j:
6.     a ← plans[i] ; b ← plans[j]
7.     # 규칙 1: 동일 target_param → enqueued_at 빠른 것이 상류
8.     IF TARGET_PARAM(a) == TARGET_PARAM(b)
         AND a.enqueued_at < b.enqueued_at:
9.       edges.append(PlanDependency(a.plan_id, b.plan_id,
                                      kind="same_target_param"))
10.    # 규칙 2: 스냅샷 체인 — b.pre_snapshot_id가 a의 post 상태에 의존
11.    IF b.rollback_snapshot_id == POST_SNAPSHOT_OF(a):
12.      edges.append(PlanDependency(a.plan_id, b.plan_id,
                                      kind="snapshot_chain"))
13.    # 규칙 3: origin order — S-3 전략 변경이 S-6 적응보다 선행
14.    IF a.source_module == "S-3" AND b.source_module == "S-6"
         AND OVERLAP_PARAMS(a, b):
15.      edges.append(PlanDependency(a.plan_id, b.plan_id,
                                      kind="origin_order"))
16. dag.nodes ← nodes ; dag.edges ← edges
17. dag.has_cycle ← DFS_CYCLE_DETECT(dag)              # O(V+E)
18. IF NOT dag.has_cycle:
19.   dag.topo_order ← KAHN_TOPO_SORT(dag)             # O(V+E)
20. RETURN dag
```

**순환 검출**: Kahn 알고리즘으로 indegree=0 노드를 반복 제거 → 잔여 노드 = 순환 참여. 순환 발견 시 `edges[].downstream_id` 중 가장 늦게 enqueued된 plan을 드롭하여 복구. 드롭 plan은 `oc.self_evo.s07.dag_cycle` 이벤트로 기록되며 다음 사이클에 재평가된다.

### 4.4 Cron 슬롯 선택 (SELECT_SLOT + NEXT_CRON_SLOT)

```
ALGORITHM SELECT_SLOT(entries, item, wf_state)
# 시간복잡도: O(|entries|)
# ABC-매핑: evolve() ③ 제안
LOCK: 부록 A.3 "Cron 기반"

1. slot_type ← CHOOSE_SLOT_TYPE(item)
   # risk=high    → "urgent"
   # source=S-6   → "urgent" (적응 루프 실시간성)
   # canary plan  → "canary"
   # else         → "routine"
2. candidates ← [e FOR e IN entries
                 IF e.slot_type == slot_type AND e.active]
3. IF candidates == []: RETURN None
4. best ← None
5. FOR e IN candidates:
6.   next_at ← NEXT_CRON_SLOT(e.cron_expr, e.timezone, NOW())
7.   # 동시성 한도 검사
8.   live ← COUNT_JOBS_IN_WINDOW(e.entry_id,
                                    next_at,
                                    next_at + e.window_duration_sec)
9.   IF live >= e.max_concurrent: CONTINUE
10.  # 워크플로우 창 충돌 검사 (I-12 READ)
11.  IF I12.has_window_conflict(wf_state, e.entry_id,
                                 next_at,
                                 next_at + e.window_duration_sec):
12.    CONTINUE
13.  IF best IS None OR next_at < best.next_at:
14.    best ← (e, next_at)
15. RETURN best

ALGORITHM NEXT_CRON_SLOT(cron_expr, tz, now)
# 표준 5-필드 Cron 파서(분 시 일 월 요일), 확장: "@routine"/"@urgent" 별칭
# 시간복잡도: O(k) where k=365*24*60 상한 (탐색 창 1년)
1. fields ← PARSE_CRON(cron_expr)          # 예: "*/15 * * * *" → 15분마다
2. t ← now.replace(second=0)
3. WHILE t < now + 1_year:
4.   IF MATCH_ALL_FIELDS(t, fields): RETURN t
5.   t ← t + 1min
6. RAISE "no slot within 1y"
```

**슬롯 타입 매핑(DH-7b)**:

| slot_type | 예시 Cron | window | max_concurrent | 용도 |
|-----------|----------|--------|----------------|------|
| routine | `*/15 * * * *` (15분) | 900s | 2 | 정기 점검 — S-3 전략 최적화 반영 |
| urgent  | `*/5 * * * *` (5분) | 300s | 1 | 즉시 대응 — S-6 적응, risk=high |
| canary  | `0 */2 * * *` (2시간) | 1800s | 1 | 모델 교체 — canary_rollback.md 연동 |
| maintenance | `0 3 * * *` (03:00 일일) | 3600s | 1 | 정비 윈도우 — 장기 작업 |

### 4.5 pre_exec_gate (S-8 재확인 + 의존 확인)

```
ALGORITHM PRE_EXEC_GATE(job, params)
# 시간복잡도: O(|dependencies|) + 1 RPC
# ABC-매핑: evolve() ④ 검증
LOCK: L3(S-8 승인 재확인), L4(자동 적용 금지)

1. # 의존성 완료 확인 (위상 정렬 준수)
2. FOR d_plan_id IN job.dependencies:
3.   IF JOB_STATE(d_plan_id) != "COMPLETED":
4.     RETURN PreExecVerdict(verdict="HOLD",
                             reason=f"dep {d_plan_id} not done",
                             next_try_at=NOW()+30s)
5. # S-8 재확인 — 승인 당시와 현재 상태 차이 검증
6. v ← S8.reconfirm(job.plan_id,
                     timeout=params.S8_PREEXEC_TIMEOUT)
7. IF v.status == TIMEOUT:
8.   IF job.attempt < params.MAX_RETRIES:
9.     RETURN PreExecVerdict(verdict="HOLD",
                             reason="s8 timeout, retry",
                             next_try_at=NEXT_CRON_SLOT_AFTER(job))
10.  RETURN PreExecVerdict(verdict="ABORT_S8_REJECT",
                           reason="s8 timeout exceeded")
11. IF NOT v.approved:
12.   RETURN PreExecVerdict(verdict="ABORT_S8_REJECT",
                            reason=v.reason)
13. RETURN PreExecVerdict(verdict="PASS",
                          s8_reconfirm_at=NOW())
```

### 4.6 S-2~S-6 오케스트레이션 순서 (L6 기반, Rule l)

> LOCK L6(Part2 L4063/L4306 정본): S-2 → S-3 → S-4 → S-5 → S-6 → S-7 → S-8 **안정화 순차 활성화**. 본 모듈은 S-6 안정화 이후에만 활성화되며, 실행 순서는 L6 파생 `origin_rank`(§4.2)로 반영한다.

```
[S-2 Pattern Miner]      안정화 DH-1(에러율<1%/스키마100%/3주기 PASS)
      ↓                    │
[S-3 Strategy Optimizer]   ▼ 안정화 → 후보 생성(EvolutionPlan) ───┐
      ↓                                                           │
[S-4 Performance Monitor]  안정화 → 알림(EnvironmentAlert) → S-6  │
      ↓                                                           │
[S-5 Feedback Loop]        안정화 → 힌트(S-3/S-6)                 │
      ↓                                                           │
[S-6 Adaptation Engine]    안정화 → 후보(EvolutionPlan, source=S-6)┤
      ↓                                                           │
[L6 gate] S-6 안정화 3주기 PASS 확인                                │
      ↓                                                           │
[S-7 Evolution Scheduler (본 모듈)]                                │
  1) S-8 승인 이벤트 구독 (from S-3/S-6 plans) ←──────────────────┘
  2) DAG 구축 (same_target / snapshot_chain / origin_order)
     └─ origin_order: S-3 plan이 S-6 plan보다 선행 (param 중첩 시)
  3) 우선순위 큐 (L6 origin_rank 반영)
     └─ S-3 origin_rank=2 vs S-6 origin_rank=5
         ↔ 동 risk일 때 S-3 plan이 **기본 +3 먼저** 실행
         ↔ 단, urgent slot(risk=high·S-6 적응)은 slot_type으로 재분리
  4) Cron 슬롯 매칭 (routine/urgent/canary/maintenance)
  5) pre-exec gate (S-8 재확인, L3)
  6) 6-13 Operations에 반영 트리거 발행 (L4 — 본 모듈은 경로 없음)
  7) L8 회귀 의뢰: S-2.RegressionRequest(source_module="S-7",
                                          context.origin=plan.source_module)
      ↓
[S-8 Governance]  pre-exec 재확인 / 실행 결과 통보 수신 / rollback 대행
      ↓
[6-13 Operations]  실제 반영 주체 (L4)
      ↓
[S-2 회귀]  성능 비교 → 저하 시 즉시 rollback 요청 (L8)
```

**오케스트레이션 불변식**:
- I1: S-6 DH-1 미충족 시 본 모듈 `evolve()`는 `S6_NOT_STABLE` 조기 반환 (L6)
- I2: S-3·S-6 plan이 동일 `target_param` 중첩 시 위상 정렬 상 S-3 선행 (§4.3 규칙 3)
- I3: urgent slot 점유 중 동일 slot_type max_concurrent=1 → 후속은 다음 슬롯으로 deferred
- I4: pre-exec ABORT_S8_REJECT 발생 plan은 본 모듈이 큐에서 제거(재제출은 S-3/S-6 책임)

### 4.7 I-Module 경유 호출 순서 (정본 해석)

> §3.2 주의에 따라 S-7 **직접 호출**은 I-12 READ·I-18 READ만. I-9는 버스 경유, I-6/I-15/I-19는 간접.

```
STEP  Caller  Module         Action                                    LOCK
1     S-8     (bus)          approved EvolutionPlan emit                L3
2     S-7     I-18 READ       ScheduleEntry list 조회                    L2
3     S-7     I-12 READ       워크플로우 상태 조회(충돌 사전 확인)       L2
4     S-7     (in-process)    BUILD_DAG / TOPO / PRIORITY_SCORE           —
5     S-7     (event bus)    oc.self_evo.s07.scheduled (→ 6-12)         R-01-7
6     (tick) S-7             DUE_JOBS 탐지                               —
7     S-7     S-8 (bus)       pre-exec reconfirm(plan_id)                L3
8     S-8     I-6 (S-8 내부)  QoD 재평가                                  (S-8 권한)
9     S-8     I-19 WRITE      pre-exec 결정 기록                          L3
10    S-8     (bus)           PreExecVerdict 반환                         L3
11    S-7     I-12 READ       최종 창 충돌 재확인                         L2
12    S-7     (bus)           OPS.trigger_apply(JobContext)               L4(OPS 주체)
13    OPS     (6-13)          실제 반영                                    L4
14    OPS     (bus)           반영 완료 통보                                —
15    S-7     S-2 (bus)       RegressionRequest(source="S-7",
                                                context.origin=...)     L8
16    S-7     (event bus)    oc.self_evo.s07.executed (→ 6-12)          R-01-7
(rollback) S-7 → S-8 (bus)    snapshot_id 복원 요청 (plan.rollback_...) L3
           S-8 → I-15 WRITE   스냅샷 복원(대행)                          L3
```

---

## 5. 예외 처리 정책 표 (Rule g)

> 01/_index.md §3.2 DH 에러 핸들링 정본 확장.

| error_code | 상황 | recoverable | 처리 | 비고 |
|------------|------|-------------|------|------|
| `SELF_EVO_TIMEOUT` | evolve() > 120s | ✅ | 실행 중단 → 다음 tick 재시도, 현재 큐 보존 | DH-2 |
| `SELF_EVO_EVAL_FAIL` | evaluate() 예외 | ✅ | 이전 점수 유지(최대 3주기) → 초과 시 비활성화 | — |
| `SELF_EVO_ROLLBACK_FAIL` | S-8 대행 복원 실패 | ❌ | I-20 경유 ADMIN+ 즉시 에스컬레이션 | 무결성 보호 |
| `SELF_EVO_IMODULE_FAIL` | I-12/I-18 호출 실패 | ✅ | 3회 재시도(backoff 1s→2s→4s) → 실패 시 해당 사이클 드롭 | 표준 재시도 |
| `S7_S6_NOT_STABLE` | S-6 DH-1 미충족 | ✅ | evolve() 조기 반환, 이벤트만 기록 | L6 gate |
| `S7_DAG_CYCLE` | DAG 순환 탐지 | ✅ | 가해자 엣지(downstream 최근 plan) 드롭, 다음 사이클 재평가 | §4.3 Kahn |
| `S7_NO_SLOT` | 적합 Cron 슬롯 없음 | ✅ | deferred 처리, 다음 tick 재탐색. 60분 초과 시 경보 | §4.4 |
| `S7_WINDOW_CONFLICT` | I-12 창 충돌 | ✅ | 다음 슬롯 재시도(attempt++). max_retries=2 초과 시 abort | §4.4 |
| `S7_S8_RECONFIRM_TIMEOUT` | S-8 pre-exec 응답 지연 | ✅ | MAX_RETRIES까지 HOLD → 초과 시 ABORT_S8_REJECT | DH-7 10s |
| `S7_S8_REJECT` | S-8 pre-exec 재거부 | ✅ | plan 큐 제거, 재제출은 S-3/S-6 책임, 이벤트 기록 | L3 |
| `S7_DEP_FAIL` | 선행 의존 영구 실패 | ✅ | HOLD 유지 + 60분 후 cascade abort 권고(이벤트) | §4.5 |
| `S7_COOLDOWN` | 동일 target_param 300s 내 | ✅ | deferred, 다음 사이클 | §4.1 line 30 |
| `S7_QUEUE_FULL` | pending_queue ≥ MAX_QUEUE_DEPTH=500 | ⚠️ | 신규 plan 거부(back-pressure), 경보 | — |
| `S7_SCHEMA_VALIDATION_FAIL` | Pydantic 검증 실패 | ❌ | 해당 plan 드롭 + 경고 | DH-1 감소 |
| `S7_L4_AUTO_APPLY_ATTEMPT` | 본 모듈이 직접 반영 경로 탐지 | ❌ | 즉시 중단 + 감사 로그 + I-20 | **L4 위반** |
| `S7_OPS_NO_ACK` | 6-13 Operations 반영 미완료 | ✅ | 10분 대기 → 재발행(attempt++), 2회 초과 시 ABORT | 트리거 재전송 |
| `S7_CRON_PARSE_FAIL` | ScheduleEntry.cron_expr 불량 | ❌ | 해당 entry 비활성화 + ADMIN 경보 | I-18 데이터 품질 |

---

## 6. Phase별 복구 전략 (Rule e)

### 6.1 Phase 흐름도

```mermaid
flowchart TD
    P1[Phase 1: Detect<br/>승인 plan 수신 이상·DAG 순환·슬롯 미존재 식별] --> P2[Phase 2: Local Retry<br/>3회 재시도 w/ backoff 1s→2s→4s<br/>I-12/I-18 재조회·다음 Cron 슬롯 탐색]
    P2 -- 성공 --> OK[정상 → ScheduledEvolution 발행]
    P2 -- 실패 --> P3[Phase 3: Degrade<br/>- urgent slot 일시 중단<br/>- 신규 plan 수신 back-pressure<br/>- priority_score penalty ×0.6<br/>- routine slot만 운영]
    P3 -- recoverable --> P3b[다음 tick 재시도]
    P3 -- 연속 3회 or S-8 timeout 누적 --> P4[Phase 4: Escalate<br/>I-20 경유 ADMIN+ 알림<br/>+ 모든 urgent/canary 실행 중단<br/>+ pending_queue 스냅샷 요청(S-8 대행)]
    P4 --> DEACT[모듈 비활성화<br/>oc.self_evo.s07.deactivated]
```

### 6.2 다운그레이드 시 priority / 처리 penalty 표

| 다운그레이드 유형 | 처리 | 누적 한도 |
|-------------------|------|-----------|
| Local retry 후 성공 (Phase 2) | 영향 없음 | — |
| I-18 READ 실패 → 캐시 ScheduleEntry 재사용 | priority_score penalty ×0.8 | 2연속 시 경보 |
| I-12 READ 실패 → 창 충돌 검사 생략 시도 | plan 일시 HOLD, priority ×0.7 | 3연속 시 Phase 3 |
| S-8 reconfirm timeout 1회 | HOLD + MAX_RETRIES까지 재시도 | — |
| S-8 reconfirm timeout 누적(1h 5회↑) | urgent slot 중단, routine만 운영 | Phase 3 |
| DAG 순환 탐지 | 가해자 드롭, priority ×0.9 | 사이클당 독립 |
| Cron 슬롯 포화 (60분 내 후보 0) | deferred 유지 + deferred_ratio_7d 상승 경보 | 90분 초과 시 ADMIN |
| 워크플로우 창 충돌 재발(attempt=max) | plan abort 처리 (재제출 S-3/S-6 책임) | — |
| Timeout → 다음 tick 재시도 | 큐 보존, penalty ×0.6, 매 tick ×0.9 누적 | 연속 5회 시 비활성화 |
| Operations 반영 미완료 | 10분 재발행 × 2회 → ABORT | 2회 초과 Phase 4 |
| Queue Full (back-pressure) | 신규 plan 거부 + 소스 모듈에 S7_QUEUE_FULL 통보 | 15분 이상 지속 시 ADMIN |

---

## 7. 에스컬레이션 & 로깅 (I-20, R-01-7/R-01-8)

### 7.1 EscalationPayload (I-20 경유, Rule c)

```json
{
  "source_engine": "s07_evolution_scheduler",
  "error_code": "SELF_EVO_ROLLBACK_FAIL",
  "original_request": {
    "op": "rollback",
    "snapshot_id": "snap_s07_sched_2026-04-14T02-30",
    "trigger": "operations_apply_failed",
    "target": {
      "job_id": "job_s07_9e21",
      "plan_id": "plan_s06_a19",
      "source_module": "S-6",
      "scheduled_at": "2026-04-14T02:30:00Z",
      "execute_at": "2026-04-14T02:35:00Z",
      "slot_entry_id": "se_urgent_5min",
      "priority_score": 6.87,
      "dependencies": ["plan_s03_s11"]
    }
  },
  "partial_result": {
    "priority_queue_restored": true,
    "dag_state_restored": true,
    "ops_trigger_reverted": false,
    "restored_items": 2,
    "failed_items": 1
  },
  "retry_count": 1,
  "timestamp": "2026-04-14T02:38:11Z",
  "trace_id": "trc_s07_9e21",
  "severity": "critical"
}
```

- **대상 경로**: 6-12 Event-Logging I-20 → 6-2 Security-Governance ADMIN+ notify → 6-13 Operations alertmanager.

### 7.2 구조화 JSON 로깅 (R-01-7, Rule d — 중첩)

```json
{
  "ts": "2026-04-14T02:30:12.431Z",
  "level": "info",
  "logger": "self_evo.s07",
  "event": "oc.self_evo.s07.scheduled",
  "module_id": "s07",
  "trace_id": "trc_s07_9e21",
  "error": null,
  "context": {
    "inbound": {
      "s8_approved_batch": 3,
      "pending_queue_depth_before": 7,
      "pending_queue_depth_after":  10
    },
    "dag": {
      "graph_id": "dag_s07_2026-04-14T02-30",
      "nodes": ["plan_s03_s11", "plan_s06_a19", "plan_s06_a20"],
      "edges": [
        {"upstream":"plan_s03_s11","downstream":"plan_s06_a19",
         "kind":"origin_order","rationale":"S-3 전략 선행, 동일 concurrency_limit 파라미터"},
        {"upstream":"plan_s06_a19","downstream":"plan_s06_a20",
         "kind":"same_target_param","rationale":"timeout_ms 순차화"}
      ],
      "has_cycle": false,
      "topo_order": ["plan_s03_s11","plan_s06_a19","plan_s06_a20"]
    },
    "scheduled": [
      {"plan_id":"plan_s03_s11",
       "job_id":"job_s07_8b01",
       "source_module":"S-3",
       "slot_entry_id":"se_routine_15min",
       "execute_at":"2026-04-14T02:45:00Z",
       "priority_score": 2.12,
       "risk_rank": 1,
       "age_sec_at_schedule": 142.0,
       "dependencies": []},
      {"plan_id":"plan_s06_a19",
       "job_id":"job_s07_9e21",
       "source_module":"S-6",
       "slot_entry_id":"se_urgent_5min",
       "execute_at":"2026-04-14T02:35:00Z",
       "priority_score": 6.87,
       "risk_rank": 1,
       "age_sec_at_schedule": 67.0,
       "dependencies": ["plan_s03_s11"]},
      {"plan_id":"plan_s06_a20",
       "job_id":"job_s07_9e22",
       "source_module":"S-6",
       "slot_entry_id":"se_urgent_5min",
       "execute_at":"2026-04-14T02:40:00Z",
       "priority_score": 7.15,
       "risk_rank": 0,
       "age_sec_at_schedule": 65.0,
       "dependencies": ["plan_s06_a19"]}
    ],
    "deferred_plans": [],
    "entries_considered": 4,
    "wf_conflicts_detected": 0
  },
  "recovery": {
    "action": "await_execute_at",
    "confidence_penalty": 0.0,
    "next_retry_at": null,
    "phase": 1,
    "triggers_emitted": {"s2": false, "s8": false,
                         "ops_trigger": false,
                         "s2_regression": false}
  }
}
```

### 7.3 정상 이벤트 목록 (6-12 ocodes)

| 이벤트 | 의미 | level |
|--------|------|-------|
| `oc.self_evo.s07.started` | evolve() tick 시작 | info |
| `oc.self_evo.s07.plans_ingested` | S-8 approved plan 수신 | info |
| `oc.self_evo.s07.dag_built` | DAG 구축 완료 (nodes/edges) | info |
| `oc.self_evo.s07.dag_cycle` | DAG 순환 탐지 → 가해자 드롭 | warn |
| `oc.self_evo.s07.scheduled` | ScheduledEvolution 발행 | info |
| `oc.self_evo.s07.deferred` | 슬롯 없음/쿨다운으로 deferred | info |
| `oc.self_evo.s07.preexec_passed` | S-8 pre-exec PASS | info |
| `oc.self_evo.s07.preexec_hold` | 의존/재확인 대기 | info |
| `oc.self_evo.s07.aborted` | pre-exec ABORT_* | warn |
| `oc.self_evo.s07.executed` | Operations 반영 트리거 발행 | info |
| `oc.self_evo.s07.ops_complete` | 6-13 반영 완료 수신 | info |
| `oc.self_evo.s07.regression_requested` | S-2 회귀 의뢰 | info |
| `oc.self_evo.s07.queue_full` | pending_queue 포화 | warn |
| `oc.self_evo.s07.rolled_back` | rollback 완료 | warn |
| `oc.self_evo.s07.error` | 예외 (위 7.2 포맷) | error |
| `oc.self_evo.s07.deactivated` | 모듈 비활성화 | critical |

---

## 8. Phase 2 통합 테스트 시나리오 (Rule e, 10건 이상)

| # | 시나리오 | 입력 | 기대 결과 | 검증 LOCK |
|---|---------|------|-----------|-----------|
| T1 | 정상 routine 흐름 | S-3 plan 1건, risk=medium | DAG empty edges, routine slot 15분 내 `ScheduledEvolution` 발행 | L1, L3, 부록 A.3 |
| T2 | S-6 DH-1 미충족 | S-6 에러율 3% | `S7_S6_NOT_STABLE` 조기 반환, 큐 변경 없음 | L6 |
| T3 | 정상 urgent 흐름 | S-6 plan risk=high | urgent slot 5분 내 execute_at, priority_score < routine plan | §4.2, §4.4 |
| T4 | Priority 역전 방지 (S-3 vs S-6 동파라미터) | S-3 + S-6 plan 동일 concurrency_limit | DAG edge (S-3→S-6, origin_order), 위상 순서 준수 | §4.3 I2 |
| T5 | DAG 순환 탐지 | 3건 plan이 snapshot_chain 순환 구성 | `S7_DAG_CYCLE`, 가해자(최신 enqueued) 드롭, 남은 2건만 스케줄 | §4.3 Kahn |
| T6 | Cron 슬롯 미존재 | 모든 urgent entry inactive, S-6 plan 제출 | `S7_NO_SLOT` deferred, 60분 뒤 `deferred_ratio` 경보 | §4.4 |
| T7 | I-18 READ 실패 | I-18 다운 | 3회 재시도 → 캐시 재사용 (priority ×0.8), 실패 시 사이클 드롭 | §5 SELF_EVO_IMODULE_FAIL |
| T8 | I-12 READ 실패 | I-12 다운 | HOLD 처리 (priority ×0.7), 3연속 실패 시 Phase 3 | §6.2 |
| T9 | S-8 pre-exec timeout | S-8 무응답 10s | HOLD + 다음 슬롯 재시도, MAX_RETRIES=2 초과 시 ABORT_S8_REJECT | DH-7, §4.5 |
| T10 | S-8 pre-exec 재거부 | approved 후 조건 변화로 reconfirm=false | `ABORT_S8_REJECT`, 큐 제거, 이벤트 기록, 재제출은 원천 모듈 책임 | L3 |
| T11 | 워크플로우 창 충돌 | I-12가 동시 workflow 실행 보고 | `ABORT_WINDOW_CONFLICT` or 다음 슬롯 retry (attempt<max) | §4.4 |
| T12 | max_concurrent 초과 | urgent slot에 이미 1개 실행 중 | 다음 Cron 슬롯으로 deferred, 동시성 불변 유지 | §4.4 |
| T13 | 정상 실행 도래 → OPS 트리거 | pre-exec PASS + execute_at 도래 | `OPS.trigger_apply(JobContext)` 발행, cooldown_tbl 갱신 | L4 |
| T14 | OPS 반영 완료 → S-2 회귀 | OPS ACK 수신 | `RegressionRequest(source="S-7", context.origin=plan.source_module)` 발행 | L8 |
| T15 | OPS no-ack 10분 | OPS ACK 누락 | 재발행 → 2회 초과 시 ABORT, `S7_OPS_NO_ACK` 경보 | §5 |
| T16 | rollback 성공 | S-8 대행 I-15 복원 | pending_queue/DAG 복원, `rolled_back` 이벤트 | L7, §4.7 |
| T17 | rollback 실패 | 스냅샷 손상 | `SELF_EVO_ROLLBACK_FAIL`, I-20 ADMIN+ 에스컬레이션 | §7.1 |
| T18 | L4 위반 탐지 | rogue 직접 파라미터 write 시도 | `S7_L4_AUTO_APPLY_ATTEMPT`, 즉시 중단, 감사 로그, I-20 | **L4** |
| T19 | 타임아웃 evolve() 125s | 대량 plan·DAG 지연 | `SELF_EVO_TIMEOUT`, Phase 3 degrade, priority ×0.6 | §5, §6 |
| T20 | Queue Full | pending_queue=500 + 신규 1건 | `S7_QUEUE_FULL`, 신규 거부 back-pressure, 원천 모듈 통보 | §5 |
| T21 | 쿨다운 적중 | 290s 전 동일 target_param 반영 | deferred, 다음 사이클 재평가 (s06 정합) | §4.1 line 30 |
| T22 | age-기반 역전 우선 | 오래된(age=1800s) low-risk plan vs 신규(age=10s) medium-risk | age 가중(W_AGE=-0.01)으로 오래된 plan 선행 | §4.2 |
| T23 | Cron 파싱 실패 | ScheduleEntry `cron_expr="* * *"` 불량 | `S7_CRON_PARSE_FAIL`, entry 비활성화, ADMIN 경보 | §5 |
| T24 | canary 슬롯 연동 | canary plan 제출 | canary slot(2h window=1800s) 배정, 03_model-upgrade-strategy 정합 | §4.4 |
| T25 | pre-exec PASS 후 의존 미완 | 선행 plan HOLD 중 후행 job 도래 | `S7_DEP_FAIL` 유예, 60분 후 cascade abort 권고 | §4.5 |
| T26 | 스키마 검증 실패 | EvolutionPlan.strategy 타입 불량 | 해당 plan 드롭, DH-1 감소 경보 | DH-1 |
| T27 | 재현성 확인 | seed=42, 동일 plan 50건 재생 | DAG/topo/priority 결정론적 일치 | §4.1~§4.4 |

---

## 9. 세션 간 인터페이스 cross-check (Rule j)

> 공급·소비 계약 정본화.

| 인터페이스 | 공급자 | 소비자 | 스키마 | 정본 |
|-----------|--------|--------|--------|------|
| `EvolutionPlan` (from S-3) | **S-3 Strategy Optimizer** (S-8 승인 후) | **S-7 (본 세션)** | **s03 §2 정본** (`strategy=OptimizedStrategy`, `rollback_snapshot_id`, `risk_hint`) | s03 §2 / 01/_index.md §1.1 |
| `EvolutionPlan` (from S-6) | **S-6 Adaptation Engine** (S-8 승인 후) | **S-7 (본 세션)** | **s03 §2 정본 재사용** (`strategy=AdaptationAction`, `source_module="S-6"`) | s06 §9.2 / s03 §2 |
| `ScheduleEntry` (READ) | I-18 | **S-7** | §2 ScheduleEntry | 01/_index.md §2.3 |
| 워크플로우 상태 (READ) | I-12 | **S-7** | in-process DTO | 01/_index.md §2.3 |
| pre-exec reconfirm req/resp | **S-7** / S-8 | S-8 / **S-7** | §2 `PreExecVerdict` | L3 |
| `ScheduledEvolution` | **S-7** | 6-13 Operations / 6-12 Event-Logging | §2 ScheduledEvolution (Part2 L4115 필드 + 확장) | 01/_index.md §1.1 / Part2 V3-P2 |
| `JobContext` (반영 트리거) | **S-7** | **6-13 Operations** | §2 JobContext | 본 파일 정본 (DH-7c) |
| `RegressionRequest` | **S-7** | S-2 | **s02 §2 정본 재사용**, `source_module="S-7"`, context에 원천 plan.source_module 동봉 | L8 |
| `GovernanceDecision` | S-8 (P2) | **S-7** | s08 예정 | L3 |
| `EscalationPayload` | **S-7** | I-20 | §2 EscalationPayload (s02~s06 정합) | R-01-8 |

### 9.1 선행 세션(P1-M1~M5) cross-check
- **s02 §2 `RegressionRequest`**: `source_module` Literal 실제 값 = `Literal["S-3","S-4","S-5","S-6","S-7"]` (s02 line 84 확인) — **"S-7" 이미 포함**. 본 파일은 s02 정본을 **재사용**(subset 아님), `source_module="S-7"` 직접 발행 가능, 하위호환 래핑 불필요. SEVO-C004 RESOLVED(CONFLICT_LOG).
- **s03 §2 `EvolutionPlan`**: 본 파일은 s03 정본을 **재사용** (신규 정의 없음). S-3가 생성한 plan과 S-6가 s03 스키마로 생성한 plan 모두 동일하게 소비 (`source_module` 구분만).
- **s04 §3.3 out-edge**: S-4 알림은 S-6 경유 → S-7 직접 연결 없음. 본 파일 §3.3에서 재확인.
- **s05 §3.3 out-edges**: S-5 → S-7 직접 트리거 없음. s05 정본 재확인.
- **s06 §9.2 후속 계약**: "S-7 작성 시 `source_module='S-6'` 분기 처리 반드시 명시" — 본 파일 §4.2 `ORIGIN_RANK_MAP`, §4.3 규칙 3(origin_order edge), §4.4 slot_type 매핑에서 S-6 분기 완비 (§4.6 I2/I3).

### 9.2 후속 세션(P2 s08) 공급 계약
- **S-8 (P2)**: 본 파일 §4.5 pre-exec 재확인, §4.7 STEP 7-10 S-8 단독 I-19 WRITE, rollback 대행(§3.1 rollback() 주석), pre-exec timeout=10s(DH-7)를 s08_governance.md 작성 시 반드시 대조. S-8의 `GovernanceDecision`에 `reconfirm_type` 구분 필드 도입 권고.
- **02_self-improvement-loop/loop_pipeline.md (P1-M7)**: ISS-3 Execute 단계 주 담당이 S-7임을 명시(§4.6 오케스트레이션도). L5 "제안→검증→적용" 중 "적용" 절대 자동 금지(L4) 원칙은 본 모듈에서 `OPS.trigger_apply`로 구현됨을 정합 확인.
- **03_model-upgrade-strategy/canary_rollback.md (P2)**: canary slot(§4.4 DH-7b)과 연동. QoD<0.90 자동 롤백(ISS-6) 트리거 시 본 모듈은 큐·DAG만 복원하고 실제 rollback은 S-8 대행.

---

## 10. LOCK 참조 매핑 & CONFLICT 후보

### 10.1 LOCK 참조

| LOCK | 반영 위치 |
|------|-----------|
| L1 S-2~S-8 모듈 목록 | §1, §2 (MODULE_ID="s07"), §3.1 |
| L2 I-Module 경유 원칙 | §3.2 접근 권한(I-12/I-18 READ), §4.1/§4.7 호출 순서 |
| L3 S-8 거버넌스 승인 필수 | §1.1, §3.1 evolve()/rollback() 주석, §4.1 line 44-50, §4.5 pre-exec gate, §4.7 STEP 7-10, §8 T9/T10 |
| L4 자동 적용 금지 | §1.1, §3.1 클래스 주석, §4.1 line 58-59 주석, §5 `S7_L4_AUTO_APPLY_ATTEMPT`, §8 T18 |
| L5 5-stage 수집→분석→제안→검증→적용 | §1.3 매핑표, §4.1 주석, Part2 L3078 대조 |
| L6 순차 활성화 (S-6 → S-7) | §1.1, §3.1 클래스 주석, §4.1 line 1 gate, §4.2 `ORIGIN_RANK_MAP`(S-2~S-6 파생), §4.6 오케스트레이션 순서, §8 T2 |
| L7 BaseSelfEvo ABC | §3.1 클래스 스켈레톤 (시그니처 정본 준수, L4119) |
| L8 S-2 회귀 테스트 | §4.1 line 62-63, §4.7 STEP 15, §8 T14 (S-7 → S-2 회귀 의뢰, context.origin 동봉) |

### 10.2 CONFLICT 후보 기록

**[CONFLICT_CANDIDATE: 종합계획서 §7 P1-M6 본문 절차 5 "I-Module 경유 호출 순서: I-18(스케줄) → I-9(로그) → I-12(워크플로우) → I-6(QoD) → I-15(스냅샷)" 지시와 01/_index.md §2.3 I-Module 접근 매트릭스(S-7 = I-12/I-18 READ only) 간 불일치 — I-9 직접 WRITE 권한 없음, I-6/I-15 직접 READ 권한 없음]**

- **불일치 상세**:
  - 종합계획서 §7 P1-M6 본문(절차 5): "I-Module 경유 호출 순서: I-18(스케줄) → I-9(로그) → I-12(워크플로우) → I-6(QoD) → I-15(스냅샷)"
  - 01/_index.md §2.3 접근 매트릭스: **S-7 = {I-12 READ, I-18 READ}**. I-6/I-9/I-14/I-15/I-19 권한 없음.
  - 부록 A.4 접근 매트릭스 동일 (S10-3 추가, FINAL REVIEW R-6 승인).
- **본 파일의 채택**: 01/_index.md §2.3 (FINAL REVIEW 승인 정본) 준수. 본문 절차 5의 I-9/I-6/I-15 참조는 (a) I-9 로그 기록은 6-12 Event-Logging 버스 경유로 치환(`oc.self_evo.s07.*` ocodes), (b) I-6 QoD는 S-8 pre-exec 재확인 시 S-8 내부에서 참조(본 모듈 직접 접근 없음), (c) I-15 스냅샷은 `plan.rollback_snapshot_id`로 간접 수신하며 WRITE/복원은 S-8 대행(§4.7 rollback STEP)으로 해석. 본 파일은 이를 §3.2 / §4.7 호출 순서 표에 명시.
- **근거**: Rule (j) "다른 세션 산출물과의 인터페이스 정합" — P0 산출물 _index.md가 정본. _index.md §2.3은 SEVO-C001/002 정합 회로의 최종 형태이며 P1-M1/M2/M3/M4/M5(s02/s03/s04/s05/s06)에서도 동일 해석 적용(SEVO-C003 시리즈).
- **등재 제안 ID**: **SEVO-C003 확장(S-7)**(P1-M1 S-2, P1-M2 S-3, P1-M3 S-4, P1-M4 S-5, P1-M5 S-6에 이어 S-7에도 동일 구조로 적용). 상태: **✅ RESOLVED 2026-04-14** (CONFLICT_LOG.md SEVO-C003 참조 — D2.0-02 §10.6 "S-Module ↔ I-Module 경유 동작" 원칙으로 접근 매트릭스(A.4) 정본 채택. 종합계획서 §7 본문 "I-18→I-9→I-12→I-6→I-15" 표기는 경유 flow 설명으로 해석 고정. 종합계획서 본문 정정은 Phase 2 진입 전 개정 작업으로 이월).

**[SEVO-C004 — s02 §2 `RegressionRequest.source_module` Literal에 "S-7" 포함 여부]**

- **확인 결과 (2026-04-14)**: s02_pattern_miner.md §2 line 84 실제 값 = `source_module: Literal["S-3","S-4","S-5","S-6","S-7"]` — **"S-7" 이미 포함**. s07 Evolution Scheduler는 `source_module="S-7"`를 **직접 발행 가능**하며 하위호환 래핑 불필요.
- **상태**: **✅ RESOLVED 2026-04-14** (CONFLICT_LOG.md SEVO-C004 참조 — s02 정본 이미 S-7 확장 반영 상태, 파일 수정 불필요 / 무변경).

> 파서 마커: 본 항목 2건은 CONFLICT_LOG.md에 SEVO-C003/C004로 RESOLVED 반영 완료. 본 파일은 RESOLVED 상태를 단순 반영하며 _index.md·CONFLICT_LOG 추가 수정 없음(공통 산출물 보호).

### 10.3 DEFINED-HERE 목록 (본 파일)

| DH | 내용 | 정본 위치 |
|----|------|-----------|
| DH-7 | S-8 pre-exec 재확인 타임아웃 10s + MAX_RETRIES=2 | §3.1, §4.5, §5 `S7_S8_RECONFIRM_TIMEOUT`, §8 T9 |
| DH-7a | 우선순위 가중치: W_ORIGIN=1.0, W_RISK=2.0, W_AGE=-0.01, W_COST=0.5 (L6 파생 origin_rank S-2=1..S-6=5) | §3.1, §4.2 |
| DH-7b | Cron 슬롯 타입 매핑: routine(`*/15`, 900s, concur=2) / urgent(`*/5`, 300s, concur=1) / canary(`0 */2`, 1800s, concur=1) / maintenance(`0 3 *`, 3600s, concur=1) | §4.4 |
| DH-7c | `JobContext` 스키마(job_id, execute_at, dependencies, pre_exec_verdict, pre_snapshot_id, attempt, max_retries=2) | §2, §4.1 |
| DH-7d | Cooldown 기본 300s per target_param (s06 DH-6b와 정합) | §3.1, §4.1 line 30, §5 `S7_COOLDOWN` |
| DH-7e | pending_queue 상한 MAX_QUEUE_DEPTH=500, tick당 MAX_JOBS_PER_TICK=20, CRON_TICK_SEC=30 | §3.1, §4.1, §5 `S7_QUEUE_FULL` |

---

## 11. 수정 정책

> **정본 — Phase 변경 시 갱신 (§8.2)**.
> 본 파일은 S-7 Evolution Scheduler의 Cron 기반 스케줄링·우선순위 큐·의존성 DAG·S-8 pre-exec 재확인(L3)·자동 적용 금지(L4)·S-2~S-6 오케스트레이션(L6)·BaseSelfEvo ABC(L7) 구현의 L3 정본이다. 상위 정본(D2.0-02 §10.4~§10.6, Part2 V3-P2 L4099-L4119·L4063/L4306, 01/_index.md §1.1/§2.3/§3.1, 종합계획서 부록 A.3) 변경이 없는 한 임의 수정 금지.

---

## 12. 변경 이력

| 일자 | 변경 | 세션 |
|------|------|------|
| 2026-04-14 | 초기 작성(P1-M6) — BaseSelfEvo ABC 구현, Cron 기반 스케줄링(4 slot_type: routine/urgent/canary/maintenance) + 우선순위 큐(W_ORIGIN/W_RISK/W_AGE/W_COST, L6 origin_rank 반영) + 의존성 DAG(same_target_param/snapshot_chain/origin_order, Kahn 순환 검출) 의사코드, S-8 pre-exec 재확인 gate(DH-7, timeout=10s), JobContext 반영 트리거(6-13 Operations 경유, L4 준수), S-2 회귀 의뢰(L8, context.origin 동봉), 접근 매트릭스 정합(§3.2, I-12/I-18 READ only), CONFLICT 후보 SEVO-C003 확장(S-7) + SEVO-C004 후보(RegressionRequest Literal 확장) 기록, Phase 2 테스트 27건, EvolutionPlan(s03) / RegressionRequest(s02) 정본 재사용 확인, S-2~S-6 오케스트레이션(§4.6 L6 파생 순서) | P1-M6 |

---

## 이월·검증 상태 (step 1 자기 확인)

- 1. 선행 세션(P1-M1 s02, P1-M2 s03, P1-M3 s04, P1-M4 s05, P1-M5 s06) cross-check: PASS
  - s02 §2 `RegressionRequest` 재사용 — `source_module="S-7"` Literal 이미 포함(s02 line 84 확인, SEVO-C004 RESOLVED)
  - s03 §2 `EvolutionPlan` 정본 재사용 (신규 정의 없음)
  - s04 직접 트리거 없음 재확인 (§3.3)
  - s05 직접 트리거 없음 재확인 (§3.3)
  - s06 §9.2 후속 계약 "source_module='S-6' 분기" 완비 — §4.2 `ORIGIN_RANK_MAP`, §4.3 규칙 3, §4.4 slot_type, §4.6 I2
- 2. CONFLICT: 2건 모두 RESOLVED
  - **SEVO-C003 확장(S-7)** — §7 P1-M6 절차 5 "I-18 → I-9 → I-12 → I-6 → I-15" vs 부록 A.4 S-7 = I-12/I-18 READ only. **✅ RESOLVED 2026-04-14** (CONFLICT_LOG.md SEVO-C003 — 접근 매트릭스 A.4 정본, 종합계획서 본문은 경유 flow 설명)
  - **SEVO-C004** — s02 §2 `RegressionRequest.source_module` Literal 확인 결과 이미 "S-7" 포함(s02 line 84). **✅ RESOLVED 2026-04-14** (CONFLICT_LOG.md SEVO-C004 — s02 정본 이미 확장, 하위호환 래핑 불필요)
- 3. LOCK 변경: 없음 (L1/L2/L3/L4/L5/L6/L7/L8 인용만, 본문 수정 0건) — [LOCK_CHANGE_NEEDED] 없음
- 4. 이월: 없음 — Phase 1 S-시리즈 6파일(s02~s07) 완성 → 02_self-improvement-loop/(P1-M7) 순차 진입 가능
- 5. 해결 이슈 ID: ISS-1 S-7 알고리즘 힌트(부록 A.3 Cron + 우선순위 큐 + 의존성 DAG) P1-M6 본 세션에서 소비
- 6. 산출물 품질 체크(12개 항목):
  - 1) 교차 참조 블록: 상단 — ✅
  - 2) Phase 1→4 복구 + penalty 표: §6 — ✅
  - 3) EscalationPayload(I-20): §2 / §7.1 — ✅
  - 4) R-01-7 중첩 JSON(error/context/recovery/trace_id): §7.2 — ✅
  - 5) Phase 2 테스트 시나리오 10건+: §8 (27건) — ✅
  - 6) Cron 스케줄링 Big-O + LOCK + ABC 매핑: §4.1~§4.5 — ✅
  - 7) Pydantic 공통 자료구조(ScheduleEntry / PriorityQueueItem / PlanDependency / ScheduleGraph / JobContext / ScheduledEvolution / PreExecVerdict): §2 — ✅
  - 8) 세션 cross-check (선행 s02~s06, 후속 S-8): §9 — ✅
  - 9) BaseSelfEvo ABC 정본(evolve / evaluate→float / rollback(snapshot_id)→bool): §3.1 — ✅
  - 10) I-Module 경유(I-18 스케줄 / I-9 로그 / I-12 워크플로우 / I-6 QoD / I-15 스냅샷) + §2.3 접근 매트릭스 대조: §3.2 / §4.7 (해석 및 CONFLICT 등재 포함) — ✅
  - 11) S-2~S-6 오케스트레이션 순서 (L6 순차 활성화): §4.6 — ✅
  - 12) LOCK L1/L2/L6/L7 (+ L3/L4/L5/L8) 매핑 + §8.2 수정 정책 헤더: §10.1 / 상단 / §11 — ✅

---

[STEP1_COMPLETE] domain=6-6 session=P1-M6 files_modified=1

[GUARDS_OK] memory_skipped=YES forbidden_paths=untouched common_artifacts=untouched
