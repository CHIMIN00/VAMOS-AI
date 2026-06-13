"""I-9 Cost Manager (V0 stub) — tiktoken 카운팅 + JSONL 사용 기록 + 게이트/경보 평가.

정본: PART2 V0-STEP-4 #5 + PHASE4-DEC-002(게이트 80/100 LOCK + 경보 70/85/95 통지 전용)
+ PHASE3-DEC-005(80% force_mini / 100% deny — V1 한도 ₩40,000/₩1,300 사전 설정 통제).
V0 정본 지출 ₩0(D10 — 로컬 Ollama) — 기록 스키마는 (날짜, 모델, 토큰수, 추정비용).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import tiktoken

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event

_USAGE_FILENAME = "cost_usage.jsonl"  # config storage.log_path 부모 하위 (경로 config 유래)


def count_tokens(text: str) -> int:
    """tiktoken 토큰 수 카운팅 (로컬 모델 공용 cl100k_base)."""
    return len(tiktoken.get_encoding("cl100k_base").encode(text))


def _usage_file() -> Path:
    d = Path(get_config().storage.log_path).parent
    d.mkdir(parents=True, exist_ok=True)
    return d / _USAGE_FILENAME


class CostManager:
    """사용 기록 + get_daily/monthly_usage + 게이트(80/100)·경보(70/85/95) 평가."""

    async def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        trace_id: str,
        cost_krw: float = 0.0,  # V0 로컬 Ollama = ₩0 (D10)
    ) -> dict[str, Any]:
        entry = {
            "date": datetime.now(UTC).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_krw": cost_krw,
            "trace_id": trace_id,
        }
        with open(_usage_file(), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def _iter_entries(self) -> list[dict[str, Any]]:
        f = _usage_file()
        if not f.is_file():
            return []
        return [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line]

    async def get_daily_usage(self) -> float:
        """오늘 사용량(₩) 합산 — config cost.daily_limit 대조용."""
        today = datetime.now(UTC).date().isoformat()
        return float(sum(e["cost_krw"] for e in self._iter_entries() if e["date"][:10] == today))

    async def get_monthly_usage(self) -> float:
        """이번 달 사용량(₩) 합산 — config cost.monthly_limit 대조용."""
        month = datetime.now(UTC).strftime("%Y-%m")
        return float(sum(e["cost_krw"] for e in self._iter_entries() if e["date"][:7] == month))

    async def evaluate_gate(
        self, trace_id: str, usage_override_krw: float | None = None
    ) -> Literal["normal", "downshift", "stop"]:
        """CostGate(DEC-005 LOCK): ≥100% deny(stop) / ≥80% force_mini(downshift) / 그 외 normal.
        경보 alert_thresholds(70/85/95)는 통지 전용 — 차단 없음 (PHASE4-DEC-002).
        ※ Decision.cost_gate enum의 "split"은 V1+(작업 분할) — V0 미사용.
        """
        cfg = get_config().cost
        used = usage_override_krw if usage_override_krw is not None else max(
            await self.get_daily_usage() / cfg.daily_limit * 100,
            await self.get_monthly_usage() / cfg.monthly_limit * 100,
        )
        # 경보 (비-LOCK, 통지 전용)
        for alert in cfg.alert_thresholds:
            if used >= alert:
                log_event(
                    "ui.gate.cost.warning",
                    producer="I-9",
                    payload={"alert_threshold": alert, "usage_percent": used,
                             "action": "notify_only"},
                    trace_id=trace_id,
                    severity="warn",
                )
        # 게이트 (LOCK 집행)
        if used >= cfg.block_threshold:
            log_event(
                "ui.gate.cost.ceiling_100",
                producer="I-9",
                payload={"usage_percent": used, "action": "deny"},
                trace_id=trace_id,
                severity="error",
                links={"failure_code": ["OC_I5_COST_OVER_BUDGET"],
                       "fallback_id": ["FB_DENY_WITH_REASON"]},
            )
            return "stop"
        if used >= cfg.warn_threshold:
            log_event(
                "ui.gate.cost.warning_80",
                producer="I-9",
                payload={"usage_percent": used, "action": "force_mini",
                         "downshift_model": cfg.downshift_model},
                trace_id=trace_id,
                severity="warn",
                links={"fallback_id": ["FB_COST_DOWNSHIFT"]},
            )
            return "downshift"
        return "normal"
