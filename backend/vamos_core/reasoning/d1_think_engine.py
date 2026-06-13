"""D-1 Think Engine (사고 엔진) — V1 CORE 6-3 결정론 인터페이스.

정본: D2.0-01 §5.12 (D-1 CORE, V1:ON, owner D2, internal, ties 02(I-5)) +
docs/sot 2/1-1_Verifier-Reasoning-Engines/04_think-engine 상세명세 (CoT/ToT/GoT 전략,
상태기계 IDLE→ANALYZING→REASONING→EVALUATING→COMPLETE, max_depth/budget_tokens).

6-3 범위(결정론): 규칙기반 전략 선택(select_strategy) + 상태기계 전이 + reasoning_trace 골격
템플릿 + 깊이/토큰 예산 통제. 6-4 위임: 실 LLM 추론 생성(CoT/ToT/GoT), 신뢰도 LLM 집계,
Fallback Chain(6-9). C-1/C-2/C-3 에스컬레이션 수신 대상(R-01-8). 결과는 모듈 내부 dataclass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from vamos_core.reasoning._common import BaseReasoningEngine, ReasonResult, clamp01

Strategy = Literal["cot", "tot", "got", "auto"]
#: 상태기계 (04_think-engine — 6-3 = 전이 로직, 실 추론 6-4)
ENGINE_STATES = ("IDLE", "ANALYZING", "REASONING", "EVALUATING", "COMPLETE")
#: 영문 분기 키워드 — **전체 단어 일치**(부분문자열 금지: 'option'≠'optional')
_BRANCH_EN = frozenset({"compare", "design", "alternative", "option", "options",
                       "tradeoff", "trade-off", "versus", "vs"})
#: 한글 분기 키워드 — 부분문자열 매칭(교착어)
_BRANCH_KO = ("비교", "설계", "대안", "선택지", "장단점")
_WORD_RE = re.compile(r"[A-Za-z가-힣-]+")


@dataclass
class ThinkRequest:
    """D-1 입력 — 04_think-engine §2 (6-3 결정론 필드 서브셋)."""

    problem: str
    context: list[str] = field(default_factory=list)
    strategy: Strategy = "auto"
    max_depth: int = 5
    budget_tokens: int = 2048
    request_id: str = ""


def select_strategy(problem: str, hint: Strategy = "auto") -> Strategy:
    """규칙기반 전략 선택 (결정론) — auto면 문제 특성으로 CoT/ToT/GoT 분류."""
    if hint != "auto":
        return hint
    tokens = {t.lower() for t in _WORD_RE.findall(problem)}
    branch = len(tokens & _BRANCH_EN)  # 영문: 전체 단어 일치
    branch += sum(1 for kw in _BRANCH_KO if kw in problem)  # 한글: 부분문자열
    if branch >= 2:
        return "got"  # 다수 분기 비교 = 그래프
    if branch == 1:
        return "tot"  # 단일 분기 탐색 = 트리
    return "cot"      # 순차 추론 = 체인


def _scaffold(strategy: Strategy, problem: str, max_depth: int) -> list[dict[str, object]]:
    """전략별 reasoning_trace 골격 (결정론 템플릿 — 실 내용 채움 = 6-4)."""
    templates = {
        "cot": ["전제 식별", "단계적 추론", "결론 도출"],
        "tot": ["분기 후보 생성", "각 분기 평가", "최적 경로 선택"],
        "got": ["노드/관계 구성", "그래프 탐색", "수렴 결론"],
        "auto": ["분석", "추론", "결론"],
    }
    steps = templates.get(strategy, templates["auto"])[:max_depth]
    return [
        {"step_number": i + 1, "description": desc, "intermediate_conclusion": None,
         "confidence": None, "deferred_to_6_4": True}
        for i, desc in enumerate(steps)
    ]


class ThinkEngine(BaseReasoningEngine):
    """reason(ThinkRequest) → ReasonResult — 전략선택·상태기계·골격 (실 추론 6-4)."""

    engine_id = "D-1"

    def reason(self, request: ThinkRequest) -> ReasonResult:
        strategy = select_strategy(request.problem, request.strategy)
        trace = _scaffold(strategy, request.problem, max(1, request.max_depth))
        # 6-3 결정론 신뢰도: 입력 충실도(문제+컨텍스트 존재) 기반 — 실 추론 신뢰도는 6-4
        confidence = clamp01(0.5 + (0.1 if request.context else 0.0)
                            + (0.1 if request.problem.strip() else -0.5))
        return ReasonResult(
            engine_id=self.engine_id,
            answer="",  # 실 생성 = 6-4 (LLM CoT/ToT/GoT)
            confidence=confidence,
            strategy_used=strategy,
            reasoning_trace=trace,
            details={
                "state_path": list(ENGINE_STATES),
                "max_depth": request.max_depth,
                "budget_tokens": request.budget_tokens,
                "request_id": request.request_id,
                "defer_to_6_4": ["llm_cot_tot_got_generation", "confidence_aggregation",
                                 "fallback_chain_6-9"],
            },
            deferred_to_6_4=True,
        )
