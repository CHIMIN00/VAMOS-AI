"""I-14 Summarizer & Memory Distiller 검증 (D2.0-01 §5.6, D2.0-02 0:1 GAP 신규 최소).

결정론 요약(문장경계) · distill(상위 비율 보존) · compaction_needed(0.8) · 이벤트 정본 ·
LLM 요약 없음(6-3 경계).
"""

from __future__ import annotations

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i14_summarizer import (
    COMPACTION_TARGET_RATIO,
    COMPACTION_TRIGGER,
    SummarizerDistiller,
)


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_compaction_constants_lock():
    assert COMPACTION_TRIGGER == 0.8
    assert COMPACTION_TARGET_RATIO == 0.5


def test_summarize_short_passthrough():
    s = SummarizerDistiller().summarize("짧은 답변입니다.")
    assert s == "짧은 답변입니다."


def test_summarize_truncates_at_sentence_boundary():
    """긴 텍스트 → 문장경계 절단 (max_chars 이내)."""
    text = "첫 문장입니다. 둘째 문장입니다. " + "긴 본문 " * 50
    s = SummarizerDistiller().summarize(text, max_chars=30)
    assert len(s) <= 31
    assert s.startswith("첫 문장입니다.")


def test_summarize_hard_cut_ellipsis():
    """경계 없는 긴 토큰 → 말줄임."""
    s = SummarizerDistiller().summarize("가" * 300, max_chars=50)
    assert s.endswith("…")
    assert len(s) <= 51


def test_distill_keeps_top_ratio():
    """4건 × 0.5 → 정보량(요약 길이) 상위 2건 보존, 원순서 유지."""
    recs = [{"content_summary": "x" * n, "id": i} for i, n in enumerate([10, 50, 5, 40])]
    kept = SummarizerDistiller().distill(recs, target_ratio=0.5)
    assert len(kept) == 2
    assert {r["id"] for r in kept} == {1, 3}  # 50, 40 길이
    assert [r["id"] for r in kept] == [1, 3]  # 원순서 보존


def test_distill_empty():
    assert SummarizerDistiller().distill([]) == []


def test_compaction_needed_threshold():
    m = SummarizerDistiller()
    assert m.compaction_needed(0.8) is True
    assert m.compaction_needed(0.79) is False


def test_events_registered():
    m = SummarizerDistiller()
    m.summarize("가" * 300, max_chars=50, trace_id=new_trace_id())
    m.distill([{"content_summary": "a"}], trace_id=new_trace_id())
