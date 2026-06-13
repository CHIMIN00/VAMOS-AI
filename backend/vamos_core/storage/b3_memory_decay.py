"""B-3 Memory Decay (망각/감쇠) — V1 CORE 6-3 결정론 감쇠 알고리즘.

정본: D2.0-01 §5.10 (B-3 CORE, V1:ON, owner D6, ties 06) +
docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/B3_memory_decay.md §3 (지수 감쇠
`decay_score = 0.5^(days_elapsed / half_life_days)`, half_life=30, review=0.3, demote=0.1).

6-3 범위(결정론): 지수 감쇠 점수 산출 + 3-단계 분류(ACTIVE/REVIEW/DEMOTE_CANDIDATE) +
권고 액션(deprecate/demote/keep — 자동삭제 금지 LOCK-MR-005). memory_store(I-3) 연계 —
L2·B-3·pinned=0 레코드 대상. 임계는 모듈 상수(config [memory.decay] 부재 — I-15 QoD 선례
동형, SOT cite). 메모리 schema(memory_records SQL)는 동결(운영 컬럼 추가 = 후속 마이그레이션).
이벤트: mem.reference.updated(registries 정본 — 설계 memory.decay.* 는 미등록 → 재사용),
저감쇠 stale = MC_ERR_STALE / FB_SHOW_STALE(registries 정본).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from vamos_core.infra.logger import log_event

#: 정본 LOCK — 반감기 30일 (B3_memory_decay.md §3.2). 30일 후 ≈0.50, 60일 ≈0.25, 90일 ≈0.125
HALF_LIFE_DAYS = 30.0
#: 정본 LOCK — 재검증 트리거 임계 (decay_score < 0.3 → REVIEW, 약 52일)
DECAY_THRESHOLD_REVIEW = 0.3
#: 정본 LOCK — 강등 후보 임계 (decay_score < 0.1 → DEMOTE_CANDIDATE, 약 100일)
DECAY_THRESHOLD_DEMOTE = 0.1

DecayStatus = Literal["ACTIVE", "REVIEW", "DEMOTE_CANDIDATE"]
#: 권고 액션 (LOCK-MR-005 — 자동삭제 없음, 사용자 확인 필수 LOCK-MR-018)
DecayAction = Literal["keep", "review", "demote_candidate"]


def compute_decay_score(
    last_accessed_at: datetime, now: datetime, half_life_days: float = HALF_LIFE_DAYS
) -> float:
    """지수 감쇠 점수 (B3_memory_decay.md §3.1 verbatim) — 0.0~1.0, 1.0=방금 접근."""
    days_elapsed = (now - last_accessed_at).total_seconds() / 86400.0
    if days_elapsed < 0:
        return 1.0  # 미래 시각 보정
    decay_score = math.pow(0.5, days_elapsed / half_life_days)
    return round(max(0.0, min(1.0, decay_score)), 4)


def classify(decay_score: float) -> DecayStatus:
    """3-단계 분류 (B3_memory_decay.md §3.2) — ≥0.3 ACTIVE / 0.1~0.3 REVIEW / <0.1 DEMOTE."""
    if decay_score >= DECAY_THRESHOLD_REVIEW:
        return "ACTIVE"
    if decay_score >= DECAY_THRESHOLD_DEMOTE:
        return "REVIEW"
    return "DEMOTE_CANDIDATE"


@dataclass
class DecayEvaluation:
    """단일 레코드 감쇠 평가 — B3_memory_decay.md §3.3 (모듈 내부, 계약 25 무변경)."""

    record_id: str
    decay_score: float
    days_since_last_access: float
    status: DecayStatus
    recommended_action: DecayAction


_STATUS_TO_ACTION: dict[DecayStatus, DecayAction] = {
    "ACTIVE": "keep",
    "REVIEW": "review",
    "DEMOTE_CANDIDATE": "demote_candidate",
}


class MemoryDecay:
    """L2·B-3 레코드 감쇠 평가기 — 결정론(자동삭제 금지, 재평가 트리거만)."""

    def __init__(self, half_life_days: float = HALF_LIFE_DAYS) -> None:
        self._half_life = half_life_days

    def evaluate_record(
        self, record: dict[str, Any], now: datetime, *, trace_id: str | None = None
    ) -> DecayEvaluation:
        """레코드 dict(memory_store row) → DecayEvaluation. last_accessed_at 부재 시 created_at."""
        ref = record.get("last_accessed_at") or record.get("created_at")
        if isinstance(ref, str):
            last = datetime.fromisoformat(ref)
        elif isinstance(ref, datetime):
            last = ref
        else:
            raise ValueError("last_accessed_at/created_at 필수 (ISO str 또는 datetime)")
        # naive 타임스탬프(SQLite CURRENT_TIMESTAMP = 오프셋 없음) → UTC 가정(now 와 정합).
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        score = compute_decay_score(last, now, self._half_life)
        status = classify(score)
        days = round((now - last).total_seconds() / 86400.0, 2)
        rec_id = str(record.get("id") or record.get("record_id") or "")

        if trace_id is not None:
            stale = status == "DEMOTE_CANDIDATE"
            log_event(
                "mem.reference.updated", producer="B-3",
                payload={"record_id": rec_id, "decay_score": score, "status": status,
                         "days_since_last_access": days},
                trace_id=trace_id, severity="warn" if stale else "info",
                links={"failure_code": ["MC_ERR_STALE"], "fallback_id": ["FB_SHOW_STALE"]}
                if stale else None,
            )
        return DecayEvaluation(
            record_id=rec_id, decay_score=score, days_since_last_access=days,
            status=status, recommended_action=_STATUS_TO_ACTION[status],
        )

    def evaluate_batch(
        self, records: list[dict[str, Any]], now: datetime, *, trace_id: str | None = None
    ) -> list[DecayEvaluation]:
        """배치 평가 — L2·B-3·pinned=0 대상만(LOCK-MR-002), pinned 제외(S7D-041 예외)."""
        out: list[DecayEvaluation] = []
        for rec in records:
            if rec.get("pinned"):
                continue  # 고정 레코드 = Decay 제외
            out.append(self.evaluate_record(rec, now, trace_id=trace_id))
        return out
