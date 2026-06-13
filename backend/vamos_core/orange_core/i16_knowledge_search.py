"""I-16 Knowledge Search Engine (지식 검색 엔진) — 검색 인터페이스 + 결정론 폴백.

정본: D2.0-01 §5.6 (I-16 CORE, V1:ON). ⚠️ D2.0-02 I-2(RAG)와 기능 중복 가능(§4.0 "구현 시
범위 확인"). 6-3/6-4 경계: 실제 임베딩·벡터·하이브리드 검색(BGE-M3/Chroma/BM25) = 6-4. 본
모듈은 검색 인터페이스 + 결정론 폴백(키워드/부분문자열 매칭)만 — 6-4 가 의미검색으로 대체.

책임: search(query, records, top_k) → 점수순 결과. 결정론 스코어 = 질의 토큰의 record 본문
(content_summary + tags) 매칭 비율. 결과 0 → OC_I2_RAG_NO_SOURCE + FB_RAG_RETRY_EXPAND.
이벤트: oc.i2.query.built / oc.i2.evidence.ready / oc.i2.evidence.insufficient (I-2↔I-16
overlap, registries 정본 재사용 — oc.i16.* 미등록). producer="I-16" 로 구분.
"""

from __future__ import annotations

import re
from typing import Any

from vamos_core.infra.logger import log_event

_TOKEN = re.compile(r"[\w가-힣]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "")]


class KnowledgeSearchEngine:
    """search — 결정론 키워드 검색(6-3). 의미검색·임베딩은 6-4 가 본 인터페이스로 대체."""

    @staticmethod
    def _haystack(record: dict[str, Any]) -> str:
        parts = [str(record.get("content_summary", ""))]
        tags = record.get("tags") or []
        if isinstance(tags, list):
            parts.extend(str(t) for t in tags)
        return " ".join(parts)

    def _score(self, query_tokens: list[str], record: dict[str, Any]) -> float:
        """질의 토큰의 부분문자열 매칭 비율 (한국어 조사/어미 robust — exact token 회피)."""
        if not query_tokens:
            return 0.0
        hay = self._haystack(record).lower()
        hits = sum(1 for q in query_tokens if q in hay)
        return round(hits / len(query_tokens), 4)

    def search(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int = 5,
        trace_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """결정론 키워드 검색 → [{record, score}] 점수 내림차순(score>0), 상위 top_k."""
        if trace_id is not None:
            log_event("oc.i2.query.built", producer="I-16",
                      payload={"query_len": len(query or ""), "corpus": len(records)},
                      trace_id=trace_id)
        qtokens = _tokens(query)
        ranked: list[tuple[float, dict[str, Any]]] = [
            (score, r) for r in records if (score := self._score(qtokens, r)) > 0.0
        ]
        ranked.sort(key=lambda x: x[0], reverse=True)
        results: list[dict[str, Any]] = [
            {"record": r, "score": score} for score, r in ranked[:top_k]
        ]

        if trace_id is not None:
            if results:
                log_event("oc.i2.evidence.ready", producer="I-16",
                          payload={"results": len(results), "top_score": ranked[0][0]},
                          trace_id=trace_id)
            else:  # 결정론 폴백 — 결과 0 (6-4 의미검색이 보완)
                log_event("oc.i2.evidence.insufficient", producer="I-16",
                          payload={"results": 0, "deterministic_fallback": True},
                          trace_id=trace_id, severity="warn",
                          links={"failure_code": ["OC_I2_RAG_NO_SOURCE"],
                                 "fallback_id": ["FB_RAG_RETRY_EXPAND"]})
        return results
