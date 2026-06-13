"""I-15 Evidence & QoD Manager (근거·QoD 관리자) — EvidenceGate 활성화 (V0 스텁 대체).

정본: D2.0-01 §5.6 (I-15 CORE, V1:ON) + D2.0-02 §7.90~7.92 (목적/인터페이스/이벤트, 구 I-19
→ I-15 매핑 §4.0) + §8.1 EvidenceGate(5-Gate 3번째). 계약: SourceQoD(qod_score/freshness/
reliability/completeness) + EvidencePack.items[].qod_score.

핵심 임계값(정본 LOCK): QoD < 0.4 → L2 벡터 삽입 금지(QOD_L2_BAN — sot2 정본 cross-cutting
constant), QoD < 0.7 → 근거 불충분(HOLD, EvidenceGate insufficient — CLAUDE.md L2 저장정책).
6-3/6-4 경계: 실제 RAG 수집·임베딩(items 채움)은 6-4. 본 모듈은 평가 인터페이스 + 결정론 집계
(빈 팩 = 근거 불요 직답 경로 보존, 채워진 팩 = 실QoD 게이트). config에 qod 섹션 부재 →
임계는 모듈 상수(SOT cite). 이벤트: ui.main.qod.updated / 실패: OC_I2_EVIDENCE_QOD_LOW
(registries 정본 재사용 — 구 oc.i19.qod.scored/OC_I19_QOD_FAIL 는 [LEGACY] 미등록).
"""

from __future__ import annotations

from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import EvidencePack

#: 정본 LOCK 임계 — QoD < 0.4 L2 삽입 금지 (sot2_conflict_scan QOD_L2_BAN 정본)
QOD_L2_BAN = 0.4
#: 정본 LOCK 임계 — QoD < 0.7 근거 불충분(HOLD) (CLAUDE.md L2 저장정책)
QOD_HOLD = 0.7
#: qod_score 누락 항목 보수 기본값 (평가 불가 = 중립)
QOD_DEFAULT = 0.5


class EvidenceQoDManager:
    """score_qod / filter_by_qod / evaluate — D2.0-02 §7.91 최소 인터페이스 (근거 QoD 평가)."""

    @staticmethod
    def score_qod(source_item: dict[str, Any]) -> float:
        """근거 항목 단일 QoD 점수 — items[].qod_score 사용(6-4 RAG 산출), 누락 시 중립."""
        raw = source_item.get("qod_score", QOD_DEFAULT)
        try:
            score = float(raw)
        except (TypeError, ValueError):
            score = QOD_DEFAULT
        return min(1.0, max(0.0, score))

    def filter_by_qod(
        self, items: list[dict[str, Any]], threshold: float = QOD_L2_BAN
    ) -> list[dict[str, Any]]:
        """임계 미만 항목 제거 (L2 삽입 후보 필터 — D2.0-02 §7.91)."""
        return [it for it in items if self.score_qod(it) >= threshold]

    def evaluate(self, evidence_pack: EvidencePack, trace_id: str | None = None) -> dict[str, Any]:
        """팩 집계 QoD + EvidenceGate 판정(sufficient) + L2 적격 — 결정론, conclusion 무관.

        빈 팩(RAG 미수집/6-3) → sufficient=True(직답 경로 보존, V0 무회귀), qod=0/coverage=0.
        채워진 팩 → 집계 QoD ≥ 0.7 면 sufficient, 항목 중 ≥0.4 비율 = coverage.
        """
        items = evidence_pack.items
        scores = [self.score_qod(it) for it in items]
        if scores:
            qod = round(sum(scores) / len(scores), 4)
            coverage = round(sum(1 for s in scores if s >= QOD_L2_BAN) / len(scores), 4)
            sufficient = qod >= QOD_HOLD
        else:
            qod, coverage, sufficient = 0.0, 0.0, True  # 빈 팩 = 직답 경로 (무회귀)
        l2_eligible = bool(scores) and qod >= QOD_L2_BAN

        if trace_id is not None:
            low = bool(scores) and not sufficient
            log_event("ui.main.qod.updated", producer="I-15",
                      payload={"evidence_pack_id": evidence_pack.evidence_pack_id,
                               "qod": qod, "coverage": coverage, "sufficient": sufficient,
                               "items": len(items)},
                      trace_id=trace_id, severity="warn" if low else "info",
                      links={"failure_code": ["OC_I2_EVIDENCE_QOD_LOW"],
                             "fallback_id": ["FB_RAG_SWITCH_SOURCE"]} if low else None)
        return {
            "qod": qod,
            "coverage": coverage,
            "sufficient": sufficient,
            "l2_eligible": l2_eligible,
            "items_evaluated": len(items),
            "low_qod_count": sum(1 for s in scores if s < QOD_L2_BAN),
        }
