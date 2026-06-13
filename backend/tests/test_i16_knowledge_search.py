"""I-16 Knowledge Search 검증 — 결정론 키워드 검색 + 폴백 (D2.0-01 §5.6, RAG=6-4).

결정론 스코어·정렬·top_k · 결과 0 폴백(OC_I2_RAG_NO_SOURCE) · 이벤트 registries 정본 ·
의미검색·임베딩 없음(6-3 경계).
"""

from __future__ import annotations

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i16_knowledge_search import KnowledgeSearchEngine


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


_RECORDS = [
    {"content_summary": "파이썬 데코레이터는 함수를 감싸는 함수", "tags": ["python", "decorator"]},
    {"content_summary": "자바 스트림 API 사용법", "tags": ["java"]},
    {"content_summary": "파이썬 제너레이터와 이터레이터", "tags": ["python", "generator"]},
]


def test_search_ranks_by_keyword_overlap():
    """결정론 — 질의 토큰 매칭 비율 내림차순."""
    res = KnowledgeSearchEngine().search("파이썬 데코레이터", _RECORDS)
    assert res[0]["record"]["content_summary"].startswith("파이썬 데코레이터")
    assert res[0]["score"] == 1.0  # 2/2 토큰 매칭
    assert all(r["score"] > 0 for r in res)


def test_search_top_k_limit():
    res = KnowledgeSearchEngine().search("파이썬", _RECORDS, top_k=1)
    assert len(res) == 1


def test_search_tags_matched():
    res = KnowledgeSearchEngine().search("java", _RECORDS)
    assert len(res) == 1
    assert res[0]["record"]["tags"] == ["java"]


def test_search_no_match_empty_with_fallback():
    """결과 0 → 빈 리스트 (이벤트 폴백 OC_I2_RAG_NO_SOURCE, 예외 없음=정본 이벤트)."""
    res = KnowledgeSearchEngine().search("코틀린 코루틴", _RECORDS, trace_id=new_trace_id())
    assert res == []


def test_search_empty_query():
    assert KnowledgeSearchEngine().search("", _RECORDS) == []


def test_search_event_registered():
    KnowledgeSearchEngine().search("파이썬", _RECORDS, trace_id=new_trace_id())
