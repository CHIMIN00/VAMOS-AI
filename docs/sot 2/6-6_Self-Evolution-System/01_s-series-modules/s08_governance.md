# S-8 Self-evo Governance — 상세 설계 (L3, V3-002)

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-6_Self-Evolution-System / 01_s-series-modules
> **Tier**: 6 (System-wide Components)
> **정본 출처**:
> - D2.0-02 §10.4~§10.6 (LOCK, S-Module 경유 동작 원칙)
> - D2.0-01 §5.7 (명칭 LOCK)
> - Part2 V3-Phase 2 L4099-L4115 (S-Module When/Where·BaseSelfEvo ABC), L4119 (ABC 시그니처)
> - Part2 V3-Phase 3 L4382-L4435 (S-8 거버넌스 완성 — V3-002)
> - SDAR_SPEC §9.3 L1366~L1370 (자동 적용 절대 금지 + S-8 승인 필수)
> - 종합계획서 §11 S-5 (DH-2 timeout=600s 출처) + §14 W5 (DH-2 S-8 timeout 잠정→Phase 2 확정 근거) + 부록 A.3 S-8 (Policy-based 승인 엔진, DH-3)
> **LOCK 매핑**: L1(모듈 목록), L2(I-Module 경유 — I-19 READ/WRITE, I-5 READ, I-8 READ), L3(S-8 승인 필수 — 본 모듈 자체), L4(자동 적용 금지 — 승인 후에도 6-13 Operations 경유), L5(자기개선 5단계 — ④ 검증=S-8 승인 게이트), L8(S-2 회귀 테스트 — 사후 보고 입력), L9(s_module_hints Decision 확장 — 거버넌스 메타 첨부)
> **DH 매핑**: DH-1 (안정화 4메트릭 — S-2~S-7 활성화 전제), **DH-2 (S-8 timeout=600s — Phase 2 정식 확정)**, DH-3 (Policy-based 승인 엔진 — 알고리즘 힌트), DH-4 (SDAR repair_result 5-필드 소비 — 6-5 W-2 RESOLVED), **DH-7 (S-7 pre-exec 재확인 timeout=10s — DH-2 600s와 별개 항목 명시)**
> **Phase**: P2-1 (V3-002 상세화)
> **생성일**: 2026-04-27
> **ISS 해결**: P1 (S-8 Governance 상세 미정의) + ISS-1 (S-8 알고리즘 힌트 소비 — Policy-based 승인 엔진)
> **선행 의존**: s02_pattern_miner.md (P1-M1) / s03_strategy_optimizer.md (P1-M2) / s06_adaptation_engine.md (P1-M5) / s07_evolution_scheduler.md (P1-M6) / 02_self-improvement-loop/loop_pipeline.md (Phase 1 ISS-3) / 6-5 SDAR P2-4 04_self-diagnosis/_index.md §V2.4 (DH-4 정식 등재 baseline, W-2 RESOLVED)

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **D2.0-02 §10.4~§10.6** | S-Module 경유 동작 원칙 정본 (LOCK L2). "S-3~S-7 후보→S-8 승인→반영+I-15 스냅샷+I-9 로그" 흐름 (L3) |
| **D2.0-02 §10.6 L3854~L3856** | S-8 거버넌스 1차 확인(위험·비용·정책) → 승인된 항목만 반영 → 회귀 테스트(S-2) 흐름 정본 |
| **D2.0-01 §5.7** | S-Module 명칭·카테고리 LOCK (S-8 = "Self-evo Governance") |
| **Part2 V3-Phase 2 L4099-L4115** | S-8 When(S-7 스케줄 실행 직전)/Where(`backend/vamos_core/self_evo/s08_governance.py`) 정본 — I/O: `EvolutionPlan` → `GovernanceDecision(approved, risk_level, reason)` |
| **Part2 V3-Phase 2 L4119** | BaseSelfEvo ABC 시그니처 정본 (`async def evolve()`, `async def evaluate() -> float`, `async def rollback(snapshot_id: str) -> bool`) |
| **Part2 V3-Phase 3 (V3-002)** | S-8 Self-evo Governance 완성 (거버넌스 규칙 엔진·승인 워크플로우·감사 로그 정책 상세) — 본 문서가 L3 상세화 |
| **SDAR_SPEC §9.3 L1366~L1370** | "Self-evo 결과 자동 적용 절대 금지" + "S-Module 적용 시 반드시 S-8 거버넌스 승인 필요" 정본 (LOCK L4) |
| **종합계획서 §3.2 5-stage authority chain** | D2.0-02 §10.4~§10.6 > D2.0-01 §5.7 > Part2 V3-Phase 2 > SDAR_SPEC §9.3 > SOT2 6-6 (S-8은 5-stage 전체 의존) |
| **종합계획서 §11 S-5 (OPEN→Phase 2 확정)** | "S-8 승인 timeout/에스컬레이션 미정의" → 본 문서에서 timeout=600초 **정식 확정** + ADMIN+ 에스컬레이션 |
| **종합계획서 §14 W5** | "S-8 승인 timeout 무한 지연 위험" → 본 §4 워크플로우 + §4.4 에스컬레이션으로 대응 |
| **종합계획서 부록 A.3 S-8** | 알고리즘 힌트: "Policy-based 승인 엔진. 리스크 등급별 자동/반자동/수동 분기. timeout=600초(DH-2)" |
| **종합계획서 §7.4 6-5 SDAR 연동** | repair_result 5-필드 → S-2 → 새로운 패턴 발견 시 **S-8 승인** 경로 → SDAR 수리 액션 카탈로그 확장 제안 (인간 최종 승인 필수) |
| **01_s-series-modules/_index.md §1.1** | S-8 역할·Input(`EvolutionPlan`)·Output(`GovernanceDecision`)·트리거(S-7 스케줄 실행 시) 정본 |
| **01_s-series-modules/_index.md §2.3 부록 A.4** | 접근 매트릭스 정본 — **S-8 = I-19 READ/WRITE (승인 결정 기록 단독 권한)**, I-5 READ(결정 모듈), I-8 READ(비용 모듈) |
| **01_s-series-modules/_index.md §3.1/§3.2** | BaseSelfEvo ABC 시그니처, 에러 핸들링 기본 정책(DH-2 S-8 timeout=600초) 정본 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1/L2/L3/L4/L5/L8/L9 레지스트리 |
| **AUTHORITY_CHAIN.md §5** | DEFINED-HERE DH-1/DH-2/DH-3/DH-4/DH-7+a~e 레지스트리 |
| **s02_pattern_miner.md (P1-M1)** | `RegressionRequest` 발행자 — S-8 승인 plan 반영 후 S-2 회귀 테스트(L8). `new_pattern_discovered` → S-8 승인 요청 라우팅(§7.4) |
| **s03_strategy_optimizer.md (P1-M2)** | `EvolutionPlan` 공급자 (source_module="S-3"). UCB1 기반 전략 후보 → S-8 평가 |
| **s06_adaptation_engine.md (P1-M5)** | `EvolutionPlan` 공급자 (source_module="S-6"). RL 기반 적응 후보 → S-8 평가 |
| **s07_evolution_scheduler.md (P1-M6)** | **S-7 실행 직전 pre-exec S-8 재확인 게이트(L3)** — DH-7 S7_PREEXEC_TIMEOUT_SEC=10s + MAX_RETRIES=2 + HOLD→ABORT_S8_REJECT (DH-2 본 모듈 600s와 별개) |
| **02_self-improvement-loop/loop_pipeline.md** | ISS-3 5단계 중 "Plan(③ 제안)" 직후 "Execute(④ 검증=S-8 승인)" 게이트 — 본 모듈이 게이트 주체 |
| **03_model-upgrade-strategy/upgrade_safety.md (P2-2)** | 모델 업그레이드도 EvolutionPlan으로 S-8 평가 대상. `model_upgrade_request.safety_checks` 사전 검증 후 S-8 승인 |
| **03_model-upgrade-strategy/canary_rollback.md (P2-3)** | 자동 롤백 4요소 중 "S-8 사후 보고" — 롤백 결정은 자동, 사후 거버넌스 보고는 본 모듈로 수신 |
| **6-5 SDAR-System P2-4 04_self-diagnosis/_index.md §V2.4** | DH-4 정식 등재 5-필드 verbatim baseline (W-2 RESOLVED). 본 §6 소비측 정합 인용 |
| **6-2 Security-Governance** | STRIDE × MCP/Agent/RAG 84 매트릭스 (참조만, 본 모듈 재정의 ❌). risk_level 평가 시 6-2 STRIDE 컨텍스트 활용 가능 |
| **6-12 Event-Logging** | `oc.self_evo.s08.*` 이벤트 기록 대상 (R-01-7 구조화 로깅) |
| **6-13 Operations** | S-8 승인 후 반영 주체. 본 모듈은 결정만 발행, 실제 적용 경로 보유 ❌ (L4) |
| **1-2 Auxiliary-Modules (S-1)** | S-1 Self-check Engine (DH-5 1-2 배치) → I-6 QoD 신호 → S-Module 진입 → S-3~S-7 후보 → S-8 (본 모듈) |

---

## 1. 개요

S-8 Self-evo Governance는 Self-Evolution 서브시스템의 **거버넌스 게이트**이다. S-3~S-7이 생성한 `EvolutionPlan` 후보를 수신하여 **위험·비용·정책** 3축 평가 후 `GovernanceDecision(approved, risk_level, reason)`을 발행한다. 본 모듈은 LOCK L3(S-8 승인 필수) + L4(자동 적용 절대 금지)를 강제하는 **유일한 승인 주체**이며, 어떤 경우에도 자동 반영 경로를 보유하지 않는다(반영은 6-13 Operations). 알고리즘은 부록 A.3 힌트에 따라 **Policy-based 승인 엔진** + **리스크 등급별 자동/반자동/수동 분기**를 결합하며, **timeout=600초(DH-2 Phase 2 정식 확정)** 초과 시 ADMIN+ 수동 승인으로 에스컬레이션한다. BaseSelfEvo ABC(L7)를 구현하며, S-2~S-7 전체 안정화(DH-1) 후 활성화된다.

### 1.1 책임 요약

- **승인 게이트**: S-3/S-6 후보 → S-7 스케줄 → 실행 직전 S-8 재확인 / S-2 새 패턴 발견 → S-8 승인 요청 (양 경로 통합)
- **3축 평가**: 위험(risk) + 비용(cost) + 정책(policy) — 각 축 점수 산정 후 종합 판정
- **결정 발행**: `GovernanceDecision(approved: bool, risk_level: Literal["low","medium","high"], reason: str)`
- **승인 워크플로우**: `pending → evaluating → {approved | denied | timeout(에스컬레이션)}` 상태 전이 (§4.3)
- **timeout 관리(DH-2)**: 기본 600초 (정식 확정 — Phase 2). 초과 시 보수적 자동 거부(`auto_timeout_reject`, terminal) + ADMIN+ 알림 동시 발행 (§3.3/§3.4 정합, §4.4 에스컬레이션 — L4 자동 승인 절대 금지)
- **감사 로그(§5)**: 모든 결정 30일+ 보존, CRITICAL 삭제 불가 (CONFIDENTIAL 처리)
- **자동 적용 금지(L4)**: 본 모듈은 설정 파일·파라미터 저장소를 직접 수정하지 않는다. 승인된 plan은 6-13 Operations에 반영 요청
- **I-Module 경유(L2)**: I-6 READ(QoD), I-9 READ(로그/메트릭), I-19 READ/WRITE(승인 기록 — 단독 WRITE 권한) — 접근 매트릭스 §2.3 부록 A.4 정본. (A.1 S-8행의 I-5/I-8은 A.4 미정의 상태 = CONFLICT_LOG 후보, 직접 접근 ❌ — 결정·비용 컨텍스트는 I-9 이벤트/S-3 위탁 경유 간접 참조)
- **순차 활성화(L6, DH-1)**: S-2~S-7 전체 안정화 (에러율<1% 7일, 스키마 검증 100%, I-Module 경유 성공률 ≥99%, 리소스 80% 미만) 통과 후에만 활성화
- **6-5 SDAR 연동(DH-4)**: SDAR Layer 5 → repair_result 5-필드 → S-2 Pattern Miner → `new_pattern_discovered` → 본 모듈 승인 요청 (§6)

### 1.2 입출력 요약 (01/_index.md §1.1 정합)

- **Input**: `EvolutionPlan` (s03 §2 정본 스키마, source_module ∈ {"S-3","S-4","S-5","S-6","S-7"}) — S-7 스케줄 실행 직전 또는 S-2 new_pattern_discovered 트리거
- **Output**: `GovernanceDecision(approved, risk_level, reason)` (Part2 V3-P2 정본 필드)
- **트리거**: S-7 pre-exec gate(DH-7 10s) → 본 모듈 600s(DH-2) / S-2 pattern miner → 새 패턴 발견 시 즉시
- **Cron 보조**: `audit_sweep` 일 1회(03:00 UTC) — 30일 경과 감사 로그 보존 검증

### 1.3 5-stage 매핑 (LOCK L5 대조, Part2 L3078 정합)

| L5 단계 | 본 모듈 행위 | 산출 |
|---------|-------------|------|
| ① 수집 | `receive_plan()` — S-7 pre-exec 또는 S-2 new_pattern 이벤트 큐 pop + I-5/I-8 READ 컨텍스트 | `ApprovalRequest` |
| ② 분석 | `evaluate_3axis()` — risk·cost·policy 3축 점수 산정 + DH-3 Policy-based 규칙 평가 | `EvaluationContext` |
| ③ 제안 | `decide()` — 자동/반자동/수동 분기 → `GovernanceDecision` 초안 | `GovernanceDecision (draft)` |
| ④ 검증 | (본 단계 자체가 거버넌스 게이트 — L3) — timeout 600s 내 ADMIN+ 또는 자동 승인 확정 | `GovernanceDecision (final)` |
| ⑤ 적용 | `publish_decision()` — I-19 WRITE(승인 기록) + 6-13 Operations 반영 요청(L4 준수, 본 모듈은 경로 보유 ❌) | `oc.self_evo.s08.decided` 이벤트 |

> ※ L5 "검증" 단계 자체가 S-8 거버넌스 승인 게이트(L3 정합). ISS-3 "Verify"=S-2 회귀 테스트(Execute 후)와 경계 다름 — loop_pipeline.md 정합.

---

## 2. 공통 자료 구조 정의 (Pydantic, Rule k)

> `EvolutionPlan`은 **s03 §2 정본을 재사용**(S-8은 소비자, 신규 정의 없음). `GovernanceDecision`은 본 §2 정본. `EscalationPayload`는 s02/s03/s04/s05/s06/s07 정합.

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime

# ── 외부 정본 재사용 (import만) ───────────────────────────────
# from .s03_strategy_optimizer import EvolutionPlan, OptimizedStrategy
# from .s07_evolution_scheduler import JobContext, ScheduledEvolution
# from .s02_pattern_miner       import PatternProposal, RegressionRequest

# ── 거버넌스 결정 (S-8 정본 Output) ────────────────────────────
class GovernanceDecision(BaseModel):
    """S-8 정본 Output (Part2 V3-P2 L4115, 01/_index.md §1.1 정합).

    LOCK L4 준수: approved=True 라도 본 모듈은 직접 적용하지 않는다.
    승인된 plan_id는 6-13 Operations에 반영 요청 이벤트로만 전달된다.
    """
    decision_id: str                                  # UUID v4
    plan_id: str                                      # 평가된 EvolutionPlan.plan_id
    approved: bool                                    # True=승인 / False=거부
    risk_level: Literal["low", "medium", "high"]
    reason: str                                       # 결정 사유 (자유 텍스트, 200자 이내 권장)
    decided_by: Literal["auto_policy", "semi_auto", "admin_manual",
                        "auto_timeout_reject"]        # §3.3 분기 결과
    decided_at: datetime
    timeout_used_sec: float                            # 0 ≤ x ≤ 600 (DH-2)
    s_module_hints: Optional[Dict[str, Any]] = None    # LOCK L9 Decision 확장 첨부

    model_config = ConfigDict(extra="forbid")          # LOCK 인터페이스

# ── 승인 요청 (입력 큐 엔트리) ─────────────────────────────────
class ApprovalRequest(BaseModel):
    """S-7 pre-exec gate 또는 S-2 new_pattern_discovered 시 발행.

    eval_deadline = received_at + 600s (DH-2). 초과 시 §4.4 에스컬레이션.
    """
    request_id: str                                    # UUID v4
    plan_id: str
    source_module: Literal["S-2", "S-3", "S-4", "S-5", "S-6", "S-7"]
    routing_reason: Literal["s7_pre_exec",             # S-7 스케줄 실행 직전
                            "s2_new_pattern",          # S-2 신규 패턴 발견
                            "model_upgrade",           # 03/upgrade_safety.md (P2-2)
                            "rollback_post_report"]    # 03/canary_rollback.md (P2-3) 사후 보고
    received_at: datetime
    eval_deadline: datetime                             # received_at + 600s (DH-2)
    pre_snapshot_id: Optional[str] = None               # I-15 스냅샷 ID (S-7 pre-exec 시 plan에 동봉)
    proposed_pattern: Optional[Dict[str, Any]] = None   # S-2 new_pattern 시 PatternProposal
    repair_result: Optional[Dict[str, Any]] = None      # SDAR DH-4 5-필드 (s2_new_pattern 시)
    cost_impact: Optional[float] = None                 # I-8 추정치 (KRW/일)
    trace_id: str

    model_config = ConfigDict(extra="forbid")

# ── 3축 평가 컨텍스트 (내부 계산용) ────────────────────────────
class EvaluationContext(BaseModel):
    """3축(risk/cost/policy) 평가 결과. DH-3 Policy-based 규칙 입력.

    종합 점수 = W_RISK·risk_score + W_COST·cost_score + W_POLICY·policy_score
              (§3.2 가중치)
    """
    request_id: str
    risk_score: float = Field(ge=0.0, le=1.0)          # 0=low, 1=high
    cost_score: float = Field(ge=0.0, le=1.0)
    policy_score: float = Field(ge=0.0, le=1.0)        # 정책 위반도 (0=준수, 1=중대 위반)
    composite_score: float                              # 자동 분기용 (§3.3)
    matched_policies: list[str] = []                    # 적중 정책 ID (DH-3 규칙 ID)
    risk_factors: Dict[str, str] = {}                   # 세부 위험 요인 (예: {"target_param": "llm_temperature", "blast_radius": "global"})
    decision_path: Literal["auto_approve", "auto_reject",
                            "semi_auto", "admin_required"]  # §3.3 분기 결과 (timeout 전 사전 분류)

    model_config = ConfigDict(extra="forbid")

# ── 감사 로그 엔트리 (§5 정본) ─────────────────────────────────
class AuditLogEntry(BaseModel):
    """모든 S-8 결정의 영구 감사 로그. CRITICAL 삭제 불가, 30일+ 보존.

    저장 경로: I-9 경유 oc.self_evo.s08.audit 토픽 (6-12 Event-Logging WRITE).
    """
    audit_id: str                                       # UUID v4
    decision_id: str                                    # GovernanceDecision.decision_id 1:1
    plan_id: str
    source_module: Literal["S-2", "S-3", "S-4", "S-5", "S-6", "S-7"]
    risk_level: Literal["low", "medium", "high"]
    decided_by: Literal["auto_policy", "semi_auto", "admin_manual",
                        "auto_timeout_reject"]
    sensitivity: Literal["NORMAL", "CONFIDENTIAL", "CRITICAL"]  # CRITICAL=삭제 불가
    retention_days: int = 30                             # 최소 30일 (§5)
    request_payload: Dict[str, Any]                      # ApprovalRequest 직렬화 (감사 추적용)
    evaluation_payload: Dict[str, Any]                   # EvaluationContext 직렬화
    decision_payload: Dict[str, Any]                     # GovernanceDecision 직렬화
    admin_actor: Optional[str] = None                    # admin_manual 시 ADMIN+ 사용자 ID
    created_at: datetime

    model_config = ConfigDict(extra="forbid")

# ── 에스컬레이션 페이로드 (s02~s07 정합) ───────────────────────
class EscalationPayload(BaseModel):
    """timeout 600s 초과 또는 risk=high 강제 ADMIN+ 승인 요청.

    수신처: I-20 EscalationManager → 6-2 Security 알림 채널.
    """
    escalation_id: str
    request_id: str
    plan_id: str
    reason: Literal["timeout_600s", "risk_high_forced",
                    "policy_critical_violation",
                    "cost_exceeds_budget"]
    severity: Literal["WARN", "ERROR", "CRITICAL"]
    target_role: Literal["ADMIN", "SECURITY", "FINANCE"]
    payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(extra="forbid")
```

---

## 3. 거버넌스 규칙 엔진 (DH-3 Policy-based)

### 3.1 알고리즘 힌트 (부록 A.3 정본)

> **DH-3 (AUTHORITY §5)**: "S-8 Self-evo Governance: Policy-based 승인 엔진"

본 §3은 부록 A.3 힌트를 L3 수준으로 상세화한다. 핵심 구성:
1. **정책 카탈로그** (§3.2): 위험·비용·정책 3축 × low/medium/high 9 셀 매트릭스
2. **분기 알고리즘** (§3.3): composite_score 기반 자동/반자동/수동 분기
3. **DH-3 알고리즘 의사코드** (§3.4): pseudo-code

### 3.2 3축 평가 매트릭스

```
╔═══════════════╤═══════════════════╤═══════════════════╤═══════════════════╗
║   축 \ 등급   │    LOW (0.0~0.3)  │   MEDIUM (0.3~0.7)│   HIGH (0.7~1.0)  ║
╠═══════════════╪═══════════════════╪═══════════════════╪═══════════════════╣
║ risk          │ 단일 파라미터·    │ 복수 파라미터·    │ 시스템 전역·      ║
║ (영향 범위)   │ 가역적 변경       │ 부분 가역         │ 비가역·LOCK 영향  ║
╟───────────────┼───────────────────┼───────────────────┼───────────────────╢
║ cost          │ ≤₩1,000/일        │ ₩1,000~₩10,000/일 │ ≥₩10,000/일       ║
║ (비용 추정)   │ (I-8 추정)        │                   │ 또는 ₩266K/월 위반║
╟───────────────┼───────────────────┼───────────────────┼───────────────────╢
║ policy        │ 정책 100% 준수    │ 경미 위반·예외    │ 핵심 정책 위반    ║
║ (정책 위반도) │                   │ 신청 가능         │ (LOCK 위반, GDPR)║
╚═══════════════╧═══════════════════╧═══════════════════╧═══════════════════╝
```

**축별 가중치 (W)** — 종합 점수 산정용:
- `W_RISK = 0.5` (영향 범위가 가장 중요)
- `W_COST = 0.2`
- `W_POLICY = 0.3`
- `composite_score = W_RISK·risk_score + W_COST·cost_score + W_POLICY·policy_score`

### 3.3 자동/반자동/수동 분기 규칙

| 분기 | 조건 | 동작 | 결정자 |
|------|------|------|--------|
| **auto_approve** | composite_score ≤ 0.30 AND policy_score ≤ 0.30 AND risk_level="low" | timeout 60초 내 자동 승인 (DH-2 600s 미사용) | `auto_policy` |
| **auto_reject** | policy_score ≥ 0.85 OR (risk_level="high" AND cost_score ≥ 0.7) | 즉시 거부 (정책/비용 명백 위반) | `auto_policy` |
| **semi_auto** | 0.30 < composite_score < 0.70 AND risk_level ∈ {"low","medium"} | timeout 600s 대기 (DH-2). 600s 내 ADMIN+ 응답 시 ADMIN 결정, 미응답 시 정책 기본값 적용 | `semi_auto` (응답 시) / `auto_timeout_reject` (timeout 시 보수적 거부) |
| **admin_required** | composite_score ≥ 0.70 OR risk_level="high" OR `routing_reason="model_upgrade"` (LOCK L10) | 즉시 ADMIN+ 에스컬레이션 (§4.4) — timeout 600s 내 응답 필수, 미응답 시 자동 거부 | `admin_manual` (응답 시) / `auto_timeout_reject` (timeout 시) |
| **default (catch-all)** | 위 4 분기 미적중 (예: composite_score ≤ 0.30 AND risk_level="medium") | 보수적 기본값 — semi_auto 처리 (ADMIN+ 600s 대기, 미응답 시 `auto_timeout_reject`). 자동 승인 절대 금지 (L4) | `semi_auto` (응답 시) / `auto_timeout_reject` (timeout 시) |
| **default (catch-all)** | 위 4 분기 미적중 (예: composite_score ≤ 0.30 AND risk_level="medium") | 보수적 기본값 — semi_auto 처리 (ADMIN+ 600s 대기, 미응답 시 `auto_timeout_reject`). 자동 승인 절대 금지 (L4) | `semi_auto` (응답 시) / `auto_timeout_reject` (timeout 시) |

> **보수적 기본값(L4 준수)**: timeout 시 자동 승인 절대 금지. 자동 적용 금지(L4)를 강제하기 위해 `auto_timeout_reject`로 거부 확정.

### 3.4 DH-3 Policy-based 승인 엔진 의사코드

```pseudocode
function evaluate_governance(req: ApprovalRequest) -> GovernanceDecision:
    # ① 3축 평가
    ctx = EvaluationContext(
        request_id    = req.request_id,
        risk_score    = score_risk(req),       # §3.2 risk 매트릭스
        cost_score    = score_cost(req),       # I-8 READ
        policy_score  = score_policy(req),     # 정책 카탈로그 매칭 (CSV/JSON)
        matched_policies = match_policies(req),
        risk_factors  = extract_risk_factors(req),
    )
    ctx.composite_score = 0.5*ctx.risk_score + 0.2*ctx.cost_score + 0.3*ctx.policy_score
    ctx.decision_path   = classify_path(ctx)   # §3.3 분기 규칙 적용

    # ② 분기 실행
    match ctx.decision_path:
        case "auto_approve":
            decision = GovernanceDecision(approved=True, decided_by="auto_policy",
                                          risk_level=derive_risk_level(ctx),
                                          reason=f"Auto-approved: composite={ctx.composite_score:.2f}",
                                          timeout_used_sec=elapsed())
        case "auto_reject":
            decision = GovernanceDecision(approved=False, decided_by="auto_policy",
                                          risk_level=derive_risk_level(ctx),
                                          reason=f"Policy violation: {ctx.matched_policies}",
                                          timeout_used_sec=elapsed())
        case "semi_auto":
            verdict = await wait_admin_response(req, timeout_sec=600)  # DH-2
            if verdict is None:
                decision = build_timeout_reject(ctx, elapsed=600.0)    # 보수적 거부
            else:
                decision = build_admin_decision(ctx, verdict, elapsed())
        case "admin_required":
            emit_escalation(req, ctx, severity="ERROR")                # §4.4
            verdict = await wait_admin_response(req, timeout_sec=600)
            if verdict is None:
                decision = build_timeout_reject(ctx, elapsed=600.0)
            else:
                decision = build_admin_decision(ctx, verdict, elapsed())

    # ③ 감사 로그 + 결정 발행
    write_audit_log(req, ctx, decision)        # §5 (CRITICAL/CONFIDENTIAL 분류)
    publish_oc_event("oc.self_evo.s08.decided", decision)
    return decision
```

> **주의**: `wait_admin_response`는 **자동 적용 경로 자체를 보유하지 않는다(L4)** — 승인 결정 전달만 수행. 실제 반영은 6-13 Operations.

---

## 4. 승인 워크플로우

### 4.1 ApprovalRequest 생명주기

```
[수신: S-7 pre-exec or S-2 new_pattern]
        │
        ▼
   pending (received_at 기록)
        │
        ▼
   evaluating (3축 평가 시작, eval_deadline = received_at + 600s)
        │
        ├──▶ auto_approve / auto_reject (즉시 결정, ≤60s)
        │        │
        │        ▼
        │   {approved | denied}
        │
        ├──▶ semi_auto / admin_required (대기 ≤600s)
        │        │
        │        ├── ADMIN+ 응답 도착 ──▶ {approved | denied} (decided_by=admin_manual/semi_auto)
        │        │
        │        └── 600s timeout ──▶ auto_timeout_reject (decided_by=auto_timeout_reject)
        │
        ▼
   decided (GovernanceDecision 발행 + I-19 WRITE + 감사 로그)
        │
        ▼
   [후속] 6-13 Operations 반영 요청 (L4 — 본 모듈 경로 보유 ❌)
```

### 4.2 거버넌스 컨텍스트 평가 (위험·비용·정책 1차 확인)

> **D2.0-02 §10.6 L3854 verbatim**: "S-3~S-7이 만든 후보는 S-8로 전달되고, S-8은 위험·비용·정책을 1차 확인한 뒤, '승인된 항목만' 문서/설정/템플릿/정책 파일 갱신 + 스냅샷(I-15) + 로그(I-9) 기록을 거친다."

3축 평가는 본 §4.2의 1차 확인 절차이며, §3.2 매트릭스에 따라 점수화된다. 평가 결과 `EvaluationContext`는 §3.4 의사코드 ②분기 실행으로 전달된다.

### 4.3 승인/거부/타임아웃 (DH-2 정식 확정)

> **DH-2 (AUTHORITY §5, 종합계획서 §11 S-5/§14 W5)**: "S-8 Governance 승인 timeout = 600초". 종합계획서 §11에서 잠정 600s 명시 후, 본 Phase 2 P2-1 시점 **정식 확정**.

| 결정 종류 | 조건 | timeout_used_sec | decided_by |
|----------|------|-----------------|------------|
| **자동 승인** | composite_score ≤ 0.30 AND policy_score ≤ 0.30 AND risk_level="low" | ≤ 60 | `auto_policy` |
| **자동 거부** | policy_score ≥ 0.85 OR (risk_level="high" AND cost_score ≥ 0.7) | ≤ 5 | `auto_policy` |
| **반자동 승인** | semi_auto 분기 + ADMIN+ 600s 내 응답 | 0 < x ≤ 600 | `semi_auto` |
| **수동 승인** | admin_required 분기 + ADMIN+ 600s 내 응답 | 0 < x ≤ 600 | `admin_manual` |
| **timeout 거부** | semi_auto/admin_required 분기 + 600s timeout | = 600 | `auto_timeout_reject` |

> **L4 준수 명시**: timeout 시 자동 **승인** 절대 금지. 무응답 = 보수적 거부 (`auto_timeout_reject`).

### 4.4 ADMIN+ 에스컬레이션

| 트리거 | 대상 역할 | 알림 채널 |
|--------|----------|----------|
| `admin_required` 분기 즉시 | ADMIN | I-20 EscalationManager → 이메일 + Slack |
| `semi_auto` 600s 절반 경과 (300s) | ADMIN | I-20 알림 갱신 (대기 중 표시) |
| `auto_reject` (policy_critical_violation) 사후 통지 | SECURITY | I-20 + 6-2 Security 채널 |
| `cost_exceeds_budget` (월 ₩266,000 위반 의심) | FINANCE | I-20 + 비용 알림 |

```python
# §4.4 에스컬레이션 발행 의사코드
def emit_escalation(req: ApprovalRequest, ctx: EvaluationContext, severity: str):
    payload = EscalationPayload(
        escalation_id = uuid4(),
        request_id    = req.request_id,
        plan_id       = req.plan_id,
        reason        = derive_reason(ctx),
        severity      = severity,
        target_role   = derive_target(ctx),
        payload       = {"composite_score": ctx.composite_score,
                         "matched_policies": ctx.matched_policies,
                         "risk_factors":  ctx.risk_factors},
        created_at    = utcnow(),
    )
    publish_oc_event("oc.escalation.requested", payload)
```

### 4.5 S-7 pre-exec 재확인 게이트 (DH-7 별개 항목 명시)

> **DH-7 (AUTHORITY §5)**: "S-7 Evolution Scheduler S-8 pre-exec 재확인 timeout — `S7_PREEXEC_TIMEOUT_SEC = 10s`, `MAX_RETRIES = 2`. 초과 시 HOLD → ABORT_S8_REJECT. **DH-2(S-8 기본 600s) 별개 항목**".

S-7이 `execute_at` 도래 시 발행하는 pre-exec 재확인 호출은 **DH-2의 600s가 아닌 DH-7의 10s** 짧은 타임아웃을 사용한다 — 이는 이미 1차 승인된 plan의 **즉시 재확인** 용도이며, 본 §4.3 의 신규 평가 600s와 별개:

```
[S-7 → S-8 pre-exec 재확인 호출]
   ├── S7_PREEXEC_TIMEOUT_SEC = 10s
   ├── MAX_RETRIES = 2 (재시도 시 다음 Cron 슬롯)
   │
   ├──▶ 10s 내 PASS 응답 ──▶ S-7 실행 진행 (JobContext.pre_exec_verdict="PASS")
   │
   ├──▶ 10s 내 HOLD 응답 ──▶ Cron 다음 슬롯 재시도 (max 2회)
   │
   ├──▶ 10s 내 ABORT_S8_REJECT 응답 ──▶ JobContext 폐기 + I-9 로그
   │
   └──▶ 10s 초과 (응답 없음) ──▶ HOLD 처리 후 Cron 다음 슬롯 재시도
```

**DH-7 vs DH-2 구분 표**:

| 항목 | DH-7 (S-7 pre-exec) | DH-2 (S-8 1차 평가) |
|------|---------------------|---------------------|
| 출처 | s07_evolution_scheduler.md §3.1 | 본 문서 §4.3 + 종합계획서 §11/§14/A.3 |
| timeout | 10s (S7_PREEXEC_TIMEOUT_SEC) | 600s (DH-2 정식 확정) |
| 재시도 | MAX_RETRIES=2 (Cron 다음 슬롯) | 없음 (timeout 즉시 거부) |
| 용도 | 이미 1차 승인된 plan의 실행 직전 재확인 | 신규 EvolutionPlan 1차 평가 |
| 결과 종류 | PASS / HOLD / ABORT_S8_REJECT | approved / denied / auto_timeout_reject |
| 별개 사유 | "동일 통지 채널이지만 의도/대기시간/재시도 정책이 다름" — 양 항목은 AUTHORITY §5에 별도 등재 |

> **주의**: DH-7 10s는 본 모듈에서 별도 관리되는 fast-path API (`s8_preexec_verify(plan_id)`). DH-2 600s 큐와 분리된 동기 응답 채널을 사용한다.

---

## 5. 감사 로그 정책

### 5.1 보존 기준

> **CRITICAL 삭제불가 + 30일+ 보존** (종합계획서 §1.3 P1 + §11 S-5 요구사항)

| sensitivity | 보존 기간 | 삭제 가능 여부 | 저장 위치 |
|-------------|----------|----------------|----------|
| **NORMAL** | 30일 | 자동 삭제 (cron 03:00 UTC) | I-9 oc.self_evo.s08.audit |
| **CONFIDENTIAL** | 90일 | 사용자 요청 + ADMIN 승인 시 가능 | I-9 + 암호화 저장 |
| **CRITICAL** | **무기한 (삭제 불가)** | ❌ 절대 불가 | I-9 + WORM (Write Once Read Many) 영구 저장소 |

### 5.2 분류 규칙

```
NORMAL: auto_approve + risk_level="low"
CONFIDENTIAL: semi_auto OR risk_level="medium" OR routing_reason ∈ {"model_upgrade","s2_new_pattern"}
CRITICAL: admin_manual OR risk_level="high" OR auto_reject(policy_critical_violation)
         OR cost_exceeds_budget OR routing_reason="rollback_post_report"
```

### 5.3 감사 로그 필드 (AuditLogEntry §2 정합)

모든 결정에 대해 다음 필드를 기록:
- `audit_id` (UUID v4)
- `decision_id` (1:1 매핑)
- `plan_id` / `source_module` / `risk_level` / `decided_by`
- `sensitivity` (§5.2 분류)
- `retention_days` (NORMAL=30 / CONFIDENTIAL=90 / CRITICAL=∞)
- `request_payload` (ApprovalRequest 직렬화)
- `evaluation_payload` (EvaluationContext 직렬화)
- `decision_payload` (GovernanceDecision 직렬화)
- `admin_actor` (admin_manual 시 ADMIN+ 사용자 ID)
- `created_at`

### 5.4 무결성 보증

- **WORM 저장**: CRITICAL 로그는 6-4 Memory-RAG-Storage WORM 토픽 (append-only)
- **무결성 해시**: SHA-256 체인 (각 엔트리는 직전 엔트리 해시 포함)
- **외부 감사**: 분기별 외부 감사관 read-only 액세스 (6-2 Security 협업)

---

## 6. 6-5 SDAR 연동 (DH-4 5-필드 verbatim 소비)

### 6.1 W-2 RESOLVED entry_gate 정합

> **6-5 W-2 RESOLVED**: 6-5 sandbox `04_self-diagnosis/_index.md §V2.4` 에서 DH-4 정식 등재 — `repair_result = {issue_id, action, success, metrics_before, metrics_after}` (5-필드 verbatim baseline).
>
> **6-6 P2-1 (본 §6) 소비측 정합**: 본 모듈은 DH-4 baseline을 **재정의 ❌, 참조만 ✅** 한다.

### 6.2 Layer 5 → S-2 → S-8 라우팅 (DH-4 verbatim 인용)

종합계획서 §7.4 정본 발췌 (verbatim):

```
[SDAR → Self-evo 방향]
SDAR Layer 5 (Verification 완료)
  → repair_result = {issue_id, action, success, metrics_before, metrics_after}
  → S-2 Pattern Miner: 수리 패턴 학습 (성공/실패 패턴 축적)

[Self-evo → SDAR 방향]
S-3 Strategy Optimizer → 새로운 수리 패턴 제안
  → S-8 Governance 승인
    → SDAR 수리 액션 카탈로그 확장 제안 (인간 최종 승인 필수)
```

### 6.3 DH-4 5-필드 verbatim 소비 스키마

```python
# 6-5 sandbox 04_self-diagnosis/_index.md §V2.4.1 baseline (verbatim 인용)
# 본 §6.3은 소비측 정합 스키마 — DH-4 정본은 6-5 측, 본 모듈은 import만 수행
class RepairResultConsumer(BaseModel):
    """6-5 RepairResult 5-필드 verbatim 소비측 인터페이스.

    LOCK L18(SDAR) 준수: 6-5 측 자동 적용 절대 금지.
    본 §6은 S-2 → 본 모듈 승인 요청 라우팅 시점에서 5-필드를 ApprovalRequest.repair_result에 동봉.
    """
    issue_id: str          # SDARDiagnosis.diagnosis_id 와 1:1 (UUID v4)
    action: str            # 실행한 수리 액션 ID (RA_001 ~ RA_014)
    success: bool          # Layer 5 Verification PASS=True / FAIL/WARN=False
    metrics_before: Dict[str, float]  # 수리 직전 메트릭
    metrics_after:  Dict[str, float]  # Layer 5 검증 시점 동일 키 셋
    # ↑ 5-필드 verbatim — 추가/변경 ❌ (DH-4 LOCK)

    model_config = ConfigDict(extra="forbid")
```

### 6.4 S-2 → S-8 승인 경로 (verbatim)

6-5 sandbox §V2.4.3 인용 (요약):

```
[S-2 Pattern Miner: 패턴 분석]
    │
    ├──▶ existing_pattern → 카운터 증가만, S-8 보고 X
    │
    └──▶ new_pattern_discovered → S-8 Governance 승인 요청
            │
            ▼
        [S-8 결정 (본 모듈)]
            ├── ApprovalRequest 생성 (UUID v4)
            ├── 거버넌스 컨텍스트 (risk/cost/policy 3축)
            ├── Approval Timeout: 600초 (DH-2 정식 확정)
            │
            ▼
        [결과]
            ├─ approved      → 6-13 Operations 반영 요청 (L4)
            ├─ denied        → audit log 누적, 미적용
            └─ timeout(600s) → auto_timeout_reject + ADMIN 알림
```

### 6.5 LOCK L18(SDAR) ↔ LOCK L4(6-6) 정합

- 6-5 LOCK L18: "Self-evo 자동 적용 절대 금지" (SDAR 측 발화)
- 6-6 LOCK L4: "자동 적용 절대 금지" (Self-evo 측 발화)
- **양측 동일 원칙 — 본 모듈은 6-5 발화를 6-6 LOCK L4로 수신, S-Module 적용 시 본 §3~§4 워크플로우 강제**

> **자동 RESOLVE 금지 원칙**: 6-5 W-2 RESOLVED는 6-5 측 sandbox 정본 변경 금지(read-only). 본 §6은 소비측 인용만, 6-5 정본 자체 수정 ❌.

---

## 7. 6-2 Security cross-handoff (참조만)

### 7.1 STRIDE × MCP/Agent/RAG 84 매트릭스 (참조만, 재정의 ❌)

> **6-2 Security-Governance** STEP_C truly_converged_v2 완료 (2026-04-27). STRIDE × MCP/Agent/RAG 84 매트릭스 정본은 6-2 측 sandbox에 존재.

본 §7은 6-2 정본을 **참조만** 한다. risk_level 평가 시 6-2 STRIDE 컨텍스트(Spoofing/Tampering/Repudiation/Information disclosure/DoS/Elevation of privilege × MCP/Agent/RAG 14 표면) 활용 가능:

| STRIDE 위협 | 본 모듈 risk 평가 시 활용 |
|-------------|------------------------|
| Spoofing | source_module 위변조 검증 (I-19 WRITE 시) |
| Tampering | EvolutionPlan 무결성 해시 검증 |
| Repudiation | §5 감사 로그 (CRITICAL 삭제 불가) |
| Information disclosure | sensitivity 분류 (CONFIDENTIAL 암호화) |
| DoS | timeout 600s 강제 (큐 폭주 방지) |
| Elevation of privilege | I-19 WRITE 단독 권한, 우회 차단 |

### 7.2 LOCK-SE-* 재정의 ❌

6-2 LOCK-SE-* 시리즈는 본 모듈에서 재정의 ❌. 본 모듈 LOCK은 AUTHORITY §4 L1~L10 + DH 15 unique 만 사용.

---

## 8. LOCK 참조 매핑

| LOCK | 항목 | 정본 출처 | 본 문서 반영 위치 |
|------|------|----------|-----------------|
| **L1** | S-2~S-8 모듈 목록 | D2.0-01 §5.7, Part2 V3-P2 L4099-L4115 | §1 (S-8 = 본 모듈) |
| **L2** | I-Module 경유 동작 원칙 | D2.0-02 §10.4~§10.6 | §1.1 (I-19 R/W 단독, I-5/I-8 READ) |
| **L3** | S-8 거버넌스 승인 필수 | D2.0-02 §10.6 L3854~L3855, SDAR_SPEC §9.3 L1370 | **본 모듈 자체 = L3 게이트 주체** |
| **L4** | 자동 적용 절대 금지 | SDAR_SPEC §9.3 L1366~L1368 | §1.1, §3.4, §4.3 timeout 보수적 거부 |
| **L5** | 자기개선 5단계 | D2.0-02 §10.6, Part2 L3078 | §1.3 (④ 검증=본 모듈 게이트) |
| **L8** | S-2 회귀 테스트 | D2.0-02 §10.6 L3856 | §6.4 후속 회귀 의뢰 |
| **L9** | s_module_hints Decision 확장 | D2.0-02 §10.5.4 L3840~L3842 | §2 GovernanceDecision.s_module_hints 첨부 |

### 도메인 규칙 참조

| 규칙 | 설명 | 반영 위치 |
|------|------|----------|
| **R-66-1** | 자동 적용 절대 금지 | §1, §3.3 보수적 기본값, §4.3 |
| **R-66-2** | 순차 활성화 엄수 (L6) | §1.1 (S-2~S-7 안정화 후 활성화) |
| **R-66-3** | 회귀 테스트 필수 (L8) | §6.4 (S-2 회귀 후속) |

---

## 9. DH 매핑

| DH | 항목 | 본 문서 반영 위치 | 비고 |
|----|------|------------------|------|
| **DH-1** | 안정화 4메트릭 | §1.1 순차 활성화 전제 | 변경 없음 |
| **DH-2** | S-8 timeout=600s | §1.1, §4.3 | **잠정→Phase 2 정식 확정** |
| **DH-3** | Policy-based 승인 엔진 | §3 전체 (3.1~3.4) | 부록 A.3 힌트 L3 상세화 |
| **DH-4** | SDAR repair_result 5-필드 | §6.3 verbatim 소비 | 6-5 baseline 재정의 ❌ |
| **DH-7** | S-7 pre-exec timeout=10s | §4.5 별개 항목 명시 | DH-2와 별개 |
| DH-7a | 우선순위 가중치 | §3.2 W_RISK/W_COST/W_POLICY와 별개 (S-7 측) | 변경 없음 |
| DH-7b | Cron 슬롯 타입 매핑 | §1.2 audit_sweep cron만 사용 | 변경 없음 |
| DH-7c | JobContext 스키마 | §4.5 pre_exec_verdict 필드 인용 | 변경 없음 |
| DH-7d | Cooldown 정합 (300s) | (S-6/S-7 영역) — 본 모듈은 미사용 | 변경 없음 |
| DH-7e | 큐/틱 상한 | (S-7 영역, MAX_QUEUE_DEPTH=500 — s07 §3.1/DH-7e 정본) — 본 모듈 자체 승인 채널은 timeout 600s 보호, S-7 pending_queue 상한(500)은 s07 소유 | 변경 없음 |

---

## 10. ISS 해결 매트릭스

| ISS | 본 문서 해결 위치 | 검증 |
|-----|------------------|------|
| **P1 (S-8 Governance 상세 미정의)** | §3 거버넌스 규칙 엔진 + §4 승인 워크플로우 + §5 감사 로그 정책 | V3-002 상세 ✅ |
| ISS-1 (S-8 알고리즘 힌트) | §3 (Policy-based 승인 엔진 + 리스크 등급별 분기) | DH-3 부록 A.3 → L3 ✅ |
| §11 S-5 (S-8 timeout 미정의) | §4.3 DH-2 정식 확정 (600s) + §4.4 ADMIN+ 에스컬레이션 | OPEN→CLOSED ✅ |
| §14 W5 (timeout 무한 지연) | §4.3 (timeout=600s 보수적 거부) + §4.4 (300s 알림 갱신) | 3중 방어 ✅ |
| ISS-7 (DH-4 SDAR 정합) | §6.3 5-필드 verbatim 소비 (6-5 W-2 RESOLVED 정합) | entry_gate 충족 ✅ |

---

## 11. 향후 확장 (Phase 3 이월)

- **C-1** (LOW): Federated Governance — 다중 노드 S-8 합의 프로토콜 (현재 단일 노드 가정)
- **C-2** (MEDIUM): ML 기반 risk_score 학습 — 현재 정책 매칭은 룰 기반, S-2 패턴 학습 결과를 risk 평가에 통합
- **C-3** (LOW): 정책 카탈로그 hot-reload — 현재 재시작 필요, 무중단 정책 갱신 메커니즘 추가
- **C-4** (LOW): 외부 감사관 read-only API 표준화 (현재 6-2 협업 ad-hoc)

> Phase 3 V3-003 단계에서 검토 예정. 본 §11 항목은 OPEN (변경 시 CONFLICT_LOG 등재).

---

## 12. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-04-27 | P2-1 V2 NEW 작성 (V3-002 S-8 거버넌스 상세) | DH-2 잠정→정식 확정 + DH-7 별개 명시 + DH-4 6-5 W-2 정합 소비 |
| 2026-06-02 | **V3-Phase 3 운영 검증 EXTEND** (Phase 4 RECOVERY P4-2 genuine write) | §13 V3-Phase 3 운영 검증 append (자체진화 5종 + DH-2 600s + LOCK L18 + 4-4 reverse-inheritance). 본문 P2-1 638L prefix UNCHANGED 보존. LOCK L1~L10 + DH 15 재정의 0. |

---

## 13. V3-Phase 3 운영 검증 (Phase 4 RECOVERY P4-2, 2026-06-02)

> **EXTEND 정책**: 본 §13 은 Phase 4 RECOVERY 시점 V3-Phase 3 운영 검증 append. 위 §1~§12 (P2-1 V2 NEW 본문) 은 byte-prefix UNCHANGED 보존. SELF_EVO_5_OPERATIONS_REPORT.md (P4-2) §6 동반 작업으로 등재.

### 13.1 자체진화 5종 운영 (S-8 거버넌스 게이트 관점)

| # | 모듈 | S-8 거버넌스 게이트 통과 흐름 |
|---|------|------------------------------|
| 1 | S-2 Pattern Miner | 수리/실패 패턴 → 후보 생성 → §3 Policy 평가 → 승인 시 S-2 회귀 테스트 (L8) |
| 2 | S-3 Strategy Optimizer | UCB1 전략 후보 → §3.2 risk/cost/policy 3축 → §4 승인 워크플로우 |
| 3 | S-7 Evolution Scheduler | Cron 4 slot_type → §4.5 S-8 pre-exec 재확인 (DH-7 10s) → HOLD/ABORT |
| 4 | S-8 Self-evo Governance | 본 모듈 — §3 Policy 엔진 + §4.3 DH-2 600s timeout + §4.4 ADMIN+ 에스컬레이션 |
| 5 | 카나리 배포 5단계 | Shadow→Canary(5%)→Partial(25%)→Majority(75%)→Full(100%) 각 단계 게이트 FAIL 시 자동 롤백 (L4 인용, 사후 S-8 승인 L3) |

### 13.2 DH-2 600s timeout 에스컬레이션 운영 (4 시나리오)

§4.3 `0 ≤ timeout_used_sec ≤ 600` (Pydantic Field) 기반: (1) 정상 timeout 내 승인 / (2) timeout 초과 → `auto_timeout_reject` 보수적 거부 / (3) 에스컬레이션 → ADMIN+ 수동 승인 / (4) LOCK L4 자동 적용 금지 강제. DH-7 (S-7 pre-exec 10s) 는 DH-2 600s 와 별개 항목 — §4.5 명시 유지.

### 13.3 LOCK L18 자동 적용 절대 금지 — 5 시나리오 차단

S-7 Cron(HOLD→ABORT_S8_REJECT) / S-8(auto_timeout_reject) / 카나리(단계 게이트 FAIL 자동 롤백) / DH-2(보수적 거부→ADMIN+ 수동) / model_upgrade_request(S-8 ApprovalRequest 변환 강제 §3.3 admin_required) — 5 시나리오 ALL 차단 강제. SDAR §9.3 정본 출처 재정의 0.

### 13.4 4-4 LOCK-ML read-only 운영 (reverse-inheritance)

3층 QoD 매트릭스 (SEVO-C005 RESOLVED): 1층 배포 진입 L10 0.90 (6-6 자체 LOCK) / 2층 일상 운영 ML-05 0.85 (4-4 read-only) / 3층 긴급 롤백 ML-07 0.60 (4-4 read-only). 카나리 5단계 = LOCK-ML-08 verbatim direct, 자동 롤백 = LOCK-ML-09 정합. 4-4 측 LOCK 인용은 read-only — 재정의 ❌.

<!-- END OF s08_governance.md V3-Phase 3 운영 검증 EXTEND (Phase 4 RECOVERY P4-2, 2026-06-02) -->
