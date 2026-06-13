"""V0 최소 파이프라인 — LangGraph StateGraph 5노드 직선 (PART2 V0-STEP-4 #6).

PHASE4-DEC-001: LangGraph는 오케스트레이션 전용 예외(StateGraph 정의·노드 간 전이 한정) —
Gate/Decision 판정 우회 금지, StateGraph 중첩 금지, START/END 상수 사용.
노드: intake(I-1) → plan(I-2+I-5) → execute(LLM) → verify(SelfCheckGate 스텁, M-14)
→ deliver(ResponseEnvelope 5필드). 토폴로지는 정본 직선 보존 — Gate deny 시 조기 종료는
execute/verify pass-through로 구현(LLM 미호출, deliver에서 거부 응답).
상태: S0_RECEIVED~S8_DONE (D2.0-02 §2.2 LOCK, 9-State).
A21 배선: L1=config LOCK frozen(config_loader) / L2=5-Gate(I-5) / L3=NEVER_AUTO frozenset
(safety.never_auto — plan 노드에서 게이트와 독립 판정, DEC-008).
"""

from __future__ import annotations

from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event, new_trace_id
from vamos_core.orange_core.i1_intent_detector import ChatModel, IntentDetector
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine
from vamos_core.orange_core.i6_self_check import SelfCheckEngine
from vamos_core.orange_core.i9_cost_manager import CostManager, count_tokens
from vamos_core.orange_core.i20_failure_manager import FailureManager
from vamos_core.safety.never_auto import detect_never_auto
from vamos_core.schemas.contracts import (
    DecisionSchema,
    EvidencePack,
    IntentFrame,
    ResponseEnvelope,
)

#: DEC-010 행동 분기 사용자 문구 (PHASE3-DEC-010 표)
_LEVEL_MESSAGES = {
    "MEDIUM": "⚠ 확신도 보통",
    "LOW": "⚠ 불확실한 답변입니다. 직접 확인을 권장합니다",
    "REFUSE": "판단이 어렵습니다. 더 많은 정보가 필요합니다",
}


class VamosState(TypedDict, total=False):
    """파이프라인 상태 (PART2 L1140~1148 — trace_id M-26 / pipeline_state FIX-02 필수)."""

    trace_id: str
    user_input: str
    intent_frame: IntentFrame | None
    evidence_pack: EvidencePack | None
    decision: DecisionSchema | None
    llm_response: str | None
    response_envelope: ResponseEnvelope | None
    pipeline_state: str
    failure_codes: list[str]
    fallback_ids: list[str]
    self_check: dict[str, Any] | None  # I-6 산출 (verify 노드 → deliver 노드)


def _stage(trace_id: str, stage: str, state_code: str) -> None:
    log_event("wf.stage.enter", producer="pipeline",
              payload={"stage": stage, "pipeline_state": state_code}, trace_id=trace_id)


def build_pipeline(llm: ChatModel | None = None) -> Any:
    """StateGraph 컴파일 — llm 주입은 테스트/모킹용 (기본 ChatOllama, config 유래)."""
    detector = IntentDetector(llm=llm)
    builder = ContextBuilder()
    engine = DecisionEngine()
    self_checker = SelfCheckEngine()
    cost = CostManager()
    failures = FailureManager()
    injected_llm = llm

    async def intake_node(state: VamosState) -> VamosState:
        trace_id = state["trace_id"]
        log_event("oc.request.received", producer="ORANGE_CORE",
                  payload={"input_meta": {"text_len": len(state["user_input"])}},
                  trace_id=trace_id)
        _stage(trace_id, "intake", "S0_RECEIVED")
        frame, failure = await detector.parse_intent(state["user_input"], trace_id=trace_id)
        out: VamosState = {"intent_frame": frame, "pipeline_state": "S1_INTENT_PARSED"}
        if failure is not None:
            handled = await failures.handle_failure(failure, "OC_I1_PARSE_FAIL", trace_id)
            out["failure_codes"] = [handled["failure_code"]]
            out["fallback_ids"] = [handled["fallback_id"]]
        return out

    async def plan_node(state: VamosState) -> VamosState:
        trace_id = state["trace_id"]
        _stage(trace_id, "plan", "S2_EVIDENCE_READY")
        intent = state["intent_frame"]
        assert intent is not None  # noqa: S101 — 직선 그래프 불변식
        pack = await builder.build_evidence(intent, trace_id)
        decision = await engine.decide(intent, pack, trace_id)
        out: VamosState = {
            "evidence_pack": pack,
            "decision": decision,
            "pipeline_state": "S3_DECISION_LOCKED",
        }
        # Defense Layer 3 — NEVER_AUTO (게이트/판정과 독립 단독 작동, DEC-008.
        # Decision 결론(locked) 변경 아님 — 실행 차단 플래그로 execute가 거부)
        action = detect_never_auto(state["user_input"])
        if action is not None:
            log_event("oc.deny.blocked", producer="DefenseLayer3",
                      payload={"never_auto_action": action, "layer": "L3"},
                      trace_id=trace_id, severity="error",
                      links={"failure_code": ["POLICY_DENY"],
                             "fallback_id": ["FB_DENY_WITH_REASON"]})
            out["failure_codes"] = [*state.get("failure_codes", []), "POLICY_DENY"]
            out["fallback_ids"] = [*state.get("fallback_ids", []), "FB_DENY_WITH_REASON"]
        return out

    def _executable(state: VamosState) -> bool:
        decision = state["decision"]
        return (
            decision is not None
            and decision.conclusion == "ACCEPT"
            and "POLICY_DENY" not in state.get("failure_codes", [])
        )

    async def execute_node(state: VamosState) -> VamosState:
        trace_id = state["trace_id"]
        _stage(trace_id, "execute", "S4_EXECUTING")
        if not _executable(state):  # Gate deny/hold — 조기 종료 (LLM 미호출)
            return {"llm_response": None, "pipeline_state": "S5_OUTPUT_READY"}
        cfg = get_config().llm
        decision = state["decision"]
        assert decision is not None  # noqa: S101
        # 모델 선택: routing.execution_mode + CostGate downshift(force_mini) — config 유래
        model_id = cfg.mini_model if (
            decision.routing.get("execution_mode") == "mini"
            or decision.cost_gate == "downshift"
        ) else cfg.main_model
        client = injected_llm
        if client is None:
            from langchain_community.chat_models import ChatOllama

            client = cast(ChatModel, ChatOllama(model=model_id.removeprefix("ollama/"),
                                                temperature=cfg.temperature))
        prompt = state["intent_frame"].user_goal if state["intent_frame"] else state["user_input"]
        result = await client.ainvoke(prompt)
        text = str(result.content)
        await cost.record_usage(
            model=model_id,
            input_tokens=count_tokens(prompt),
            output_tokens=count_tokens(text),
            trace_id=trace_id,
            cost_krw=0.0,  # V0 로컬 Ollama = ₩0 (D10)
        )
        return {"llm_response": text, "pipeline_state": "S5_OUTPUT_READY"}

    async def verify_node(state: VamosState) -> VamosState:
        """SelfCheckGate 위치 (M-14) — V1: I-6 Self-check Engine 활성화 (V0 스텁 대체).

        I-6 결정론 4-검증 → self_check 보고서. reasoning_trace SelfCheck SKIP → 실판정 갱신
        (감사 기록 — S3 conclusion 불변, DEC-010). 직선 토폴로지 보존(soft loop = retry_allowed).
        """
        trace_id = state["trace_id"]
        _stage(trace_id, "verify", "S6_SELF_CHECKED")
        decision = state["decision"]
        if decision is None:
            return {"pipeline_state": "S6_SELF_CHECKED"}
        report = self_checker.run_self_check(
            decision,
            llm_response=state.get("llm_response"),
            failure_codes=state.get("failure_codes", []),
            trace_id=trace_id,
        )
        out: VamosState = {"self_check": report, "pipeline_state": "S6_SELF_CHECKED"}
        if decision.gates:  # SelfCheckGate SKIP → 실판정 (PASS/WARN→PASS, FAIL→FAIL)
            gate_result = "PASS" if report["verdict"] != "FAIL" else "FAIL"
            for entry in decision.gates.get("reasoning_trace", []):
                if entry.get("gate") == "SelfCheckGate":
                    entry["result"] = gate_result
                    entry["detail"] = {"verdict": report["verdict"], "score": report["score"],
                                       "risk": report["_risk"], "threshold": report["_threshold"]}
        fb = report.get("_fallback_id")
        if fb is not None:  # 2회 연속 FAIL 수렴 fallback (게이트 결과 우선, 02 §6.3 정본)
            out["fallback_ids"] = [*state.get("fallback_ids", []), fb]
        return out

    async def deliver_node(state: VamosState) -> VamosState:
        trace_id = state["trace_id"]
        _stage(trace_id, "deliver", "S7_MEMORY_COMMITTED")
        decision = state["decision"]
        assert decision is not None  # noqa: S101
        level = decision.confidence_level
        if state.get("llm_response") and level != "REFUSE":
            prefix = _LEVEL_MESSAGES.get(level)
            summary = f"{prefix}\n{state['llm_response']}" if prefix else state["llm_response"]
        elif decision.conclusion == "HOLD":
            summary = "승인 대기(HOLD) — P2 작업은 명시적 승인이 필요합니다."
        else:
            summary = _LEVEL_MESSAGES["REFUSE"] if level == "REFUSE" else (
                "요청이 거부되었습니다."
            )
        envelope = ResponseEnvelope.model_validate(  # 경계 검증 의무 — 5필드 LOCK
            {
                "answer": {"summary": summary, "details": state.get("llm_response") or "",
                           "next_actions": []},
                "evidence": {
                    "coverage": 0.0,  # V0 빈 EvidencePack
                    "items": [],
                    "qod": 0.0,
                },
                "self_check": {  # I-6 산출 (verify 노드) — 미존재 시 보수적 PASS
                    k: v for k, v in (state.get("self_check") or {
                        "score": 1.0, "verdict": "PASS", "reasons": [], "retry_allowed": False,
                    }).items() if not k.startswith("_")  # 내부 힌트(_risk 등) 제외 — 5필드 계약
                },
                "decision_ref": {  # A22 V0 연계 (PHASE4-DEC-010 — confidence 단일 출처 Decision)
                    "decision_id": decision.decision_id,
                    "gates": decision.gates or {},
                },
                "audit": {
                    "event_ids": [],
                    "failure_codes": state.get("failure_codes", []),
                    "fallback_ids": state.get("fallback_ids", []),
                },
            }
        )
        log_event("oc.done", producer="pipeline",
                  payload={"decision_id": decision.decision_id,
                           "conclusion": decision.conclusion,
                           "confidence_level": level},
                  trace_id=trace_id)
        return {"response_envelope": envelope, "pipeline_state": "S8_DONE"}

    # PART2 L1150~1162 정본 그래프 (직선 5노드 — START/END 상수, set_entry_point 금지)
    graph = StateGraph(VamosState)
    graph.add_node("intake", intake_node)      # I-1 Intent Detector
    graph.add_node("plan", plan_node)          # I-2 Context Builder + I-5 Decision
    graph.add_node("execute", execute_node)    # Ollama LLM 직접 호출
    graph.add_node("verify", verify_node)      # SelfCheckGate 위치 (M-14)
    graph.add_node("deliver", deliver_node)    # ResponseEnvelope 생성
    graph.add_edge(START, "intake")            # LangGraph 0.2+: START/END 상수
    graph.add_edge("intake", "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "verify")        # S5(Execute) → SelfCheck(verify) → S6(Deliver)
    graph.add_edge("verify", "deliver")
    graph.add_edge("deliver", END)
    return graph.compile()


async def run_pipeline(user_input: str, llm: ChatModel | None = None) -> VamosState:
    """편의 실행기 — trace_id 서버 생성(R8) 후 E2E 1회 실행."""
    app = build_pipeline(llm=llm)
    initial: VamosState = {
        "trace_id": new_trace_id(),
        "user_input": user_input,
        "pipeline_state": "S0_RECEIVED",
        "failure_codes": [],
        "fallback_ids": [],
    }
    final: VamosState = await app.ainvoke(initial)
    return final
