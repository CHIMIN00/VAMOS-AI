"""I-14 Summarizer & Memory Distiller (요약·증류기) — 요약 + 메모리 압축.

정본: D2.0-01 §5.6 (I-14 CORE, V1:ON). ⚠️ D2.0-02 0:1 GAP (설계 부재 — 구현 시 신규, §4.0).
신규 최소 구현 (CompactionConfig §2.1 trigger=0.8/target_ratio=0.5 hint).

책임: ① summarize(content) → 결정론 요약(문장경계 절단 — MemoryRecord.content_summary 후보)
② distill(records, ratio) → 메모리 압축(상위 비율 보존) ③ compaction_needed(used, trigger).
6-3/6-4 경계: LLM 추출/추상 요약 = 6-4. 본 모듈은 결정론 요약(문장경계·길이순)만.
이벤트: ui.frontmini.summary.ready / ui.memory.candidate.found (registries 정본).
"""

from __future__ import annotations

import math
from typing import Any

from vamos_core.infra.logger import log_event

#: CompactionConfig (D2.0-02 §2.1 hint) — 컨텍스트 80% 도달 시 50% 목표로 압축
COMPACTION_TRIGGER = 0.8
COMPACTION_TARGET_RATIO = 0.5
DEFAULT_SUMMARY_CHARS = 200

_SENT_DELIMS = (". ", "! ", "? ", "다. ", "。", "\n")


class SummarizerDistiller:
    """summarize / distill / compaction_needed — 결정론 (LLM 요약 = 6-4)."""

    @staticmethod
    def summarize(content: str, max_chars: int = DEFAULT_SUMMARY_CHARS,
                  trace_id: str | None = None) -> str:
        """문장경계 절단 결정론 요약 (경계 우선; 경계 부재 시 max_chars+말줄임표 1자)."""
        text = (content or "").strip()
        if len(text) <= max_chars:
            summary = text
        else:
            cut = text[:max_chars]
            boundary = max((cut.rfind(d) + len(d) for d in _SENT_DELIMS
                            if cut.rfind(d) > max_chars * 0.5), default=0)
            summary = (cut[:boundary].strip() if boundary else cut.rstrip() + "…")
        if trace_id is not None:
            log_event("ui.frontmini.summary.ready", producer="I-14",
                      payload={"in_chars": len(text), "out_chars": len(summary)},
                      trace_id=trace_id)
        return summary

    def distill(
        self, records: list[dict[str, Any]], target_ratio: float = COMPACTION_TARGET_RATIO,
        trace_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """메모리 증류 — 정보량(content_summary 길이) 상위 target_ratio 보존 (결정론)."""
        if not records:
            return []
        keep = max(1, math.ceil(len(records) * target_ratio))
        ranked = sorted(
            enumerate(records),
            key=lambda ir: (-len(str(ir[1].get("content_summary", ""))), ir[0]),
        )
        kept_idx = sorted(i for i, _ in ranked[:keep])
        result = [records[i] for i in kept_idx]
        if trace_id is not None:
            log_event("ui.memory.candidate.found", producer="I-14",
                      payload={"in": len(records), "kept": len(result),
                               "target_ratio": target_ratio},
                      trace_id=trace_id)
        return result

    @staticmethod
    def compaction_needed(used_ratio: float, trigger: float = COMPACTION_TRIGGER) -> bool:
        """컨텍스트 사용률 ≥ trigger(0.8) → 압축 필요 (§2.1)."""
        return used_ratio >= trigger
