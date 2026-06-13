"""D-1 Think Engine 검증 — 규칙기반 전략선택 + 골격 (1-1/04_think-engine).

6-3 범위: select_strategy(CoT/ToT/GoT) + reasoning_trace 골격. 실 LLM 추론 = 6-4.
"""

from __future__ import annotations

from vamos_core.reasoning.d1_think_engine import (
    ThinkEngine,
    ThinkRequest,
    select_strategy,
)


def test_strategy_cot_default():
    """분기 키워드 없음 → cot (순차)."""
    assert select_strategy("explain how recursion works") == "cot"


def test_strategy_tot_single_branch():
    """단일 분기 키워드 → tot (트리)."""
    assert select_strategy("design a caching layer") == "tot"


def test_strategy_got_multi_branch():
    """다수 분기 키워드 → got (그래프)."""
    assert select_strategy("compare and design alternative options") == "got"


def test_strategy_hint_overrides():
    """명시 strategy hint 우선."""
    assert select_strategy("anything", "cot") == "cot"


def test_reason_returns_scaffold_deferred():
    """reason → trace 골격 + 6-4 위임 마킹, answer 공백(실 생성 6-4)."""
    e = ThinkEngine()
    r = e.reason(ThinkRequest(problem="설계 비교 분석", context=["근거1"]))
    assert r.strategy_used in ("cot", "tot", "got")
    assert r.reasoning_trace  # R-01-5 최소 1 step
    assert r.answer == ""
    assert r.deferred_to_6_4 is True
    assert "llm_cot_tot_got_generation" in r.details["defer_to_6_4"]


def test_empty_problem_low_confidence():
    """빈 문제 → 낮은 신뢰도 → should_escalate."""
    e = ThinkEngine()
    r = e.reason(ThinkRequest(problem="   "))
    assert e.should_escalate(r) is True


def test_max_depth_caps_trace():
    """max_depth 가 trace 길이 상한."""
    e = ThinkEngine()
    r = e.reason(ThinkRequest(problem="explain", max_depth=2))
    assert len(r.reasoning_trace) <= 2


def test_no_substring_branch_false_positive():
    """'optional'/'comparison' 부분문자열로 인한 허위 분기 탐지 없음 (적대검증 수리)."""
    # 'optional' 은 'option' 부분문자열이지만 전체 단어가 아니므로 분기 키워드 아님 → cot
    assert select_strategy("explain the optional comparison setting") == "cot"
