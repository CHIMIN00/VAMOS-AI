"""JSONL 구조화 로깅 — LogEventSchema 기반 (V0-STEP-5 / PART2 L1277~1312, D2.0-04 §9).

정본 필드 7 (D2.1-D2 §4.2): event_type, producer, when, payload, severity + sinks/links(opt).
structlog 출력 매핑 (PART2 L1285~1293 표):
  event_type→event_type / module→producer / timestamp→when / data→payload /
  level→severity / trace_id→links / message→payload.message
- 모든 로그 JSON 형식 (평문 금지 — LOCK) · trace_id(UUID v4) 필수 (LOCK)
- event_type은 registries.is_valid_event_type 검증 의무 (4-4 연동)
- 파일: {log_dir}/vamos_{date}.jsonl 일별 로테이션 — log_dir은 config storage.log_path의
  부모 디렉토리(파일 경로 config 유래 — 하드코딩 금지), 파일명 패턴은 V0-STEP-5 정본.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from vamos_core.infra.config_loader import get_config
from vamos_core.schemas.contracts import LogEventSchema
from vamos_core.schemas.registries import is_valid_event_type

# PART2 L1299~1311 정본 초기화
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

_console = structlog.get_logger("vamos")


def new_trace_id() -> str:
    """trace_id 생성 — 서버 생성 전용 UUID v4 (R8/M-26)."""
    return str(uuid.uuid4())


def _log_dir() -> Path:
    return Path(get_config().storage.log_path).parent


def _log_file(when: str) -> Path:
    d = _log_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d / f"vamos_{when[:10]}.jsonl"


def log_event(
    event_type: str,
    producer: str,
    payload: dict[str, Any],
    trace_id: str,
    severity: str = "info",
    sinks: list[str] | None = None,
    links: dict[str, Any] | None = None,
) -> LogEventSchema:
    """정본 7필드 LogEvent 발행 — 경계 model_validate 의무 + 레지스트리 검증."""
    if not is_valid_event_type(event_type):
        raise ValueError(f"미등록 event_type: {event_type!r} (registries.EVENT_TYPES — 4-4 연동)")
    if not trace_id:
        raise ValueError("trace_id 필수 (LOCK — logging.trace_id_required)")
    uuid.UUID(trace_id)  # UUID v4 형식 검증 — 위조/비정형 거부 (R8)
    when = datetime.now(UTC).isoformat()
    event = LogEventSchema.model_validate(
        {
            "event_type": event_type,
            "producer": producer,
            "when": when,
            "payload": payload,
            "severity": severity,
            "sinks": sinks,
            "links": {"trace_id": trace_id, **(links or {})},
        }
    )
    record = event.model_dump(exclude_none=True)
    with open(_log_file(when), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    # 콘솔도 JSON 형식 (structlog JSONRenderer)
    log_fn = getattr(_console, severity if severity != "critical" else "error", _console.info)
    log_fn(event_type, producer=producer, trace_id=trace_id)
    return event
