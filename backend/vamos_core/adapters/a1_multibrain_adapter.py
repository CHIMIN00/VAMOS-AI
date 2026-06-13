"""A-1 MultiBrain Adapter (멀티-브레인 어댑터) — V1 CORE 6-3 결정론 라우팅 인터페이스.

정본: D2.0-01 §5.9 (A-1 CORE, V1:ON, owner D4, internal, ties 04/02(I-5)) +
docs/sot 2/6-9_Brain-Adapter-HAL/01_multi-brain-adapter (BaseBrainAdapter ABC,
ConnectorResponse=BrainAdapterResponse 7필드) + 03_llm-routing (5-step) + 04_fallback-chain.

6-3 범위(결정론): 5-step 라우팅(classify→filter→score→gate→select) + RoutingDecision +
Fallback Chain 분류(F1~F8) + invoke() stub. 6-4 위임: 실 provider SDK 호출(Ollama/OpenAI/
Anthropic), 실 비용/지연 측정. 응답 계약 = BrainAdapterResponse(D2.1-D4 §4.2, 계약 25 재사용).
이벤트: ui.node.selected(registries 정본 — 설계 brain.route.* 미등록 → 재사용). 비용초과 =
OC_I5_COST_OVER_BUDGET / FB_COST_DOWNSHIFT, 라우팅실패 = OC_I5_ROUTE_NOT_FOUND /
FB_ROUTE_SAFE_NODE (registries 정본).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import BrainAdapterResponse

Complexity = Literal["instant", "low", "medium", "high", "max"]
GateResult = Literal["allow", "downshift", "deny"]

#: complexity → 후보 모델 식별자 (03_llm-routing §4.2 — 6-3 결정론 선택 테이블, 실 연결 6-4)
_COMPLEXITY_CANDIDATES: dict[Complexity, tuple[str, ...]] = {
    "instant": ("ollama_local", "gpt_4o_mini"),
    "low": ("ollama_local", "gpt_4o_mini", "gemini_flash"),
    "medium": ("gpt_4o_mini", "gemini_flash", "claude_haiku"),
    "high": ("claude_sonnet", "gpt_4o", "deepseek_v3"),
    "max": ("claude_opus", "deepseek_r1", "gpt_4o"),
}
#: 도메인 오버라이드 (03_llm-routing §3.2 — 우선 모델)
_DOMAIN_OVERRIDE: dict[str, str] = {
    "code": "claude_sonnet",
    "finance": "claude_sonnet",
    "creative": "gpt_4o",
}
#: 비용 하향 시 안전 모델 (downshift 대상)
_DOWNSHIFT_MODEL = "ollama_local"
#: 토큰 임계 (D2.0-02 §2.1-A 근사 — 결정론 복잡도 분류)
_TOKEN_INSTANT, _TOKEN_LOW, _TOKEN_MEDIUM, _TOKEN_HIGH = 20, 100, 500, 2000


def classify_complexity(token_estimate: int, tier: str | None = None) -> Complexity:
    """토큰 추정·tier 로 복잡도 분류 (결정론) — 03_llm-routing §4.2."""
    if tier == "main" and token_estimate >= _TOKEN_MEDIUM:
        return "max"
    if token_estimate < _TOKEN_INSTANT:
        return "instant"
    if token_estimate < _TOKEN_LOW:
        return "low"
    if token_estimate < _TOKEN_MEDIUM:
        return "medium"
    if token_estimate < _TOKEN_HIGH:
        return "high"
    return "max"


@dataclass
class BrainRequest:
    """A-1 라우팅 입력 — 01_multi-brain-adapter §2.1 (6-3 결정론 필드 서브셋)."""

    task_type: str
    prompt: str
    domain: str = "general"
    tier: str | None = None
    token_estimate: int = 0
    cost_budget_used_pct: float = 0.0  # LOCK-69-7 — 100=초과
    trace_id: str = ""


@dataclass
class RoutingDecision:
    """5-step 라우팅 결과 — 03_llm-routing §2.1 (모듈 내부, 계약 25 무변경)."""

    complexity: Complexity
    domain: str
    selected_model: str
    candidates_evaluated: int
    gate_result: GateResult
    reason: str
    fallback_chain: list[str] = field(default_factory=list)


def gate_check(cost_budget_used_pct: float) -> GateResult:
    """비용 게이트 (LOCK-69-7) — ≥100 deny / 80~100 downshift / <80 allow (결정론)."""
    if cost_budget_used_pct >= 100.0:
        return "deny"
    if cost_budget_used_pct >= 80.0:
        return "downshift"
    return "allow"


class MultiBrainAdapter:
    """A-1 — 5-step 결정론 라우팅 + invoke() stub (실 멀티-LLM 호출 = 6-4)."""

    engine_id = "A-1"

    def route(self, request: BrainRequest) -> RoutingDecision:
        """classify → filter → score → gate → select (결정론). 실 invoke 는 호출측/6-4."""
        complexity = classify_complexity(request.token_estimate, request.tier)
        candidates = list(_COMPLEXITY_CANDIDATES[complexity])
        gate = gate_check(request.cost_budget_used_pct)

        # 도메인 오버라이드 (03_llm-routing §3.2 우선 모델) — 후보집합에 편입 후 선두 정렬.
        # 미편입 모델 무단 선택 금지(selected ∈ candidates 불변, candidates_evaluated 정합).
        override = _DOMAIN_OVERRIDE.get(request.domain)
        if override:
            if override in candidates:
                candidates.remove(override)
            candidates.insert(0, override)  # 후보로 편입(평가 집합 일관)

        if gate == "deny":
            selected, reason = _DOWNSHIFT_MODEL, "cost_deny_safe_node"
        elif gate == "downshift":
            selected, reason = _DOWNSHIFT_MODEL, "cost_downshift"
        else:
            selected = candidates[0]  # 오버라이드 편입 시 선두 = override (selected ∈ candidates)
            reason = f"complexity={complexity}"
            if override:
                reason += f" domain_override={override}"

        # Fallback Chain (04_fallback-chain §4 — V1: 후보 → ollama, MAX_TRANSITIONS=2 결정론)
        fallback_chain = [c for c in candidates if c != selected][:2] + [_DOWNSHIFT_MODEL]
        decision = RoutingDecision(
            complexity=complexity, domain=request.domain, selected_model=selected,
            candidates_evaluated=len(candidates), gate_result=gate, reason=reason,
            fallback_chain=fallback_chain,
        )
        if request.trace_id:
            low = gate == "deny"
            log_event(
                "ui.node.selected", producer="A-1",
                payload={"selected_blue_node_id": selected, "complexity": complexity,
                         "gate_result": gate, "candidates": len(candidates)},
                trace_id=request.trace_id, severity="warn" if low else "info",
                links={"failure_code": ["OC_I5_COST_OVER_BUDGET"],
                       "fallback_id": ["FB_COST_DOWNSHIFT"]} if gate != "allow" else None,
            )
        return decision

    def invoke(self, request: BrainRequest) -> BrainAdapterResponse:
        """실 LLM 호출 = 6-4 — 6-3 은 계약 형태 보존 stub(output_text 공백, 위임 경고)."""
        decision = self.route(request)
        return BrainAdapterResponse.model_validate({
            "output_text": "",  # 실 생성 = 6-4 (provider SDK)
            "evidence_summary": "",
            "cost_used_estimate": {"deferred_to_6_4": True,
                                   "selected_model": decision.selected_model},
            "warnings": ["deferred_to_6_4: real multi-LLM invoke (Ollama/OpenAI/Anthropic)"],
            "trace_id": request.trace_id or "stub",
            "tool_calls": None,
            "qod_hint": None,
        })
