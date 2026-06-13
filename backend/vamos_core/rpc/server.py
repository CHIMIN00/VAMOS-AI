"""IPC JSON-RPC 2.0 서버 — V0-STEP-3 (PHASE3-DEC-006 / PHASE_B1 §5.2).

규칙 (PART2 V0-STEP-3 L975~982):
  - 통신은 stdin/stdout 파이프만 (TCP/HTTP 아님).
  - stderr = 로그 전용 (structlog → stderr; JSON-RPC stdout과 혼선 금지 — M-5).
  - 시작 시 ready 메시지를 stdout 첫 줄로 출력 → Rust 측 감지.
  - 에러 = JSON-RPC error object (code + message + data). 비즈니스 에러는
    data.failure_code = FailureCodeRegistry 등재값 (registries 검증).

13 메서드는 전부 V0 stub: 파라미터 검증(필수 누락 → -32602) + 기본 응답. 미존재 메서드
→ -32601 (jsonrpcserver 자동). embedding.* = 임베딩 0(stub). mcp.* = 시그니처 예약(DEC-007).

실행: python -m vamos_core.rpc.server
"""

from __future__ import annotations

import sys
from typing import Any

import structlog
from jsonrpcserver import Error, Result, Success, dispatch, method

from vamos_core.schemas import registries

# ── 로깅: structlog → stderr 전용 (stdout 순수성 보장) ───────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger("vamos.rpc")

# JSON-RPC 2.0 사용자 정의 비즈니스 에러 코드 (PHASE_B1 §6 — -32000 대역).
BUSINESS_ERROR_CODE = -32000

#: V0 13 메서드 분모 (PHASE3-DEC-006 / PHASE_B1 §5.2 — LOCK).
RPC_METHODS: tuple[str, ...] = (
    "langgraph.workflow.run",
    "langgraph.stage.execute",
    "langgraph.decision.create",
    "langgraph.node.dispatch",
    "langgraph.verify.run_chain",
    "embedding.encode",
    "embedding.store",
    "llm.generate",
    "llm.record_invoke",
    "llm.rate_limit.get",
    "mcp.bridge.init",
    "mcp.bridge.health",
    "mcp.tools.discover",
)


def _business_error(failure_code: str, trace_id: str, message: str) -> Result:
    """FailureCodeRegistry 연동 에러 (data.failure_code 등재값 검증)."""
    valid = registries.is_valid_failure_code(failure_code)
    data: dict[str, Any] = {
        "failure_code": failure_code if valid else "UNREGISTERED",
        "failure_code_registered": valid,
        "trace_id": trace_id,
    }
    return Error(BUSINESS_ERROR_CODE, message, data)


def _stub(method_name: str, trace_id: str, **extra: Any) -> dict[str, Any]:
    """V0 stub 응답 공통 봉투 (trace_id 에코 + stub 마커)."""
    return {"method": method_name, "trace_id": trace_id, "v0_stub": True, **extra}


# ── langgraph.* (5) ──────────────────────────────────────────────────────────
@method(name="langgraph.workflow.run")
def workflow_run(trace_id: str, user_input: str, **kwargs: Any) -> Result:
    log.info("rpc.workflow.run", trace_id=trace_id)
    return Success(_stub("langgraph.workflow.run", trace_id,
                         user_response="", evidence_summary="", log_report={"trace_id": trace_id}))


@method(name="langgraph.stage.execute")
def stage_execute(trace_id: str, workflow_id: str, stage_id: str, **kwargs: Any) -> Result:
    if stage_id not in ("intake", "plan", "execute", "verify", "deliver"):
        return _business_error("OC_I5_ROUTE_NOT_FOUND", trace_id, f"unknown stage_id: {stage_id}")
    return Success(_stub("langgraph.stage.execute", trace_id,
                         workflow_id=workflow_id, stage_id=stage_id, status="pending"))


@method(name="langgraph.decision.create")
def decision_create(trace_id: str, intent_frame_ref: str, evidence_pack_ref: str,
                    **kwargs: Any) -> Result:
    return Success(_stub("langgraph.decision.create", trace_id,
                         intent_frame_ref=intent_frame_ref, evidence_pack_ref=evidence_pack_ref,
                         conclusion="HOLD", locked=False))


@method(name="langgraph.node.dispatch")
def node_dispatch(trace_id: str, node_id: str, **kwargs: Any) -> Result:
    return Success(_stub("langgraph.node.dispatch", trace_id, node_id=node_id, status="success"))


@method(name="langgraph.verify.run_chain")
def verify_run_chain(trace_id: str, decision_id: str, **kwargs: Any) -> Result:
    return Success(_stub("langgraph.verify.run_chain", trace_id,
                         decision_id=decision_id, entries=[], overall_passed=True))


# ── embedding.* (2) — V0 임베딩 0 (stub) ─────────────────────────────────────
@method(name="embedding.encode")
def embedding_encode(trace_id: str, texts: list[Any], **kwargs: Any) -> Result:
    return Success(_stub("embedding.encode", trace_id,
                         embeddings=[], count=len(texts), note="V0 임베딩 0 — stub"))


@method(name="embedding.store")
def embedding_store(trace_id: str, record_id: str, **kwargs: Any) -> Result:
    return Success(_stub("embedding.store", trace_id, record_id=record_id, stored=False))


# ── llm.* (3) ────────────────────────────────────────────────────────────────
@method(name="llm.generate")
def llm_generate(trace_id: str, prompt: str, **kwargs: Any) -> Result:
    return Success(_stub("llm.generate", trace_id, output_text="", warnings=["v0_stub"]))


@method(name="llm.record_invoke")
def llm_record_invoke(trace_id: str, model_id: str, **kwargs: Any) -> Result:
    return Success(_stub("llm.record_invoke", trace_id, model_id=model_id, recorded=True))


@method(name="llm.rate_limit.get")
def llm_rate_limit_get(trace_id: str, target_id: str, **kwargs: Any) -> Result:
    return Success(_stub("llm.rate_limit.get", trace_id, target_id=target_id,
                         rpm=0, on_exceed="queue"))


# ── mcp.* (3) — 시그니처 예약 (DEC-007, 실구현 V1-Phase 6) ────────────────────
@method(name="mcp.bridge.init")
def mcp_bridge_init(trace_id: str, bridge_id: str, **kwargs: Any) -> Result:
    return Success(_stub("mcp.bridge.init", trace_id, bridge_id=bridge_id,
                         status="reserved", transport="streamable_http"))


@method(name="mcp.bridge.health")
def mcp_bridge_health(trace_id: str, bridge_id: str, **kwargs: Any) -> Result:
    return Success(_stub("mcp.bridge.health", trace_id, bridge_id=bridge_id, status="reserved"))


@method(name="mcp.tools.discover")
def mcp_tools_discover(trace_id: str, bridge_id: str, **kwargs: Any) -> Result:
    return Success(_stub("mcp.tools.discover", trace_id, bridge_id=bridge_id, tools=[]))


def dispatch_request(raw: str) -> str:
    """단일 JSON-RPC 요청 문자열 → 응답 문자열 (테스트/루프 공통)."""
    return dispatch(raw)


def _emit_ready() -> None:
    """ready 센티넬을 stdout 첫 줄로 출력 (Rust 감지용)."""
    ready = (
        '{"jsonrpc": "2.0", "method": "server.ready", '
        f'"params": {{"methods": {len(RPC_METHODS)}, "protocol": "json-rpc-2.0"}}}}'
    )
    sys.stdout.write(ready + "\n")
    sys.stdout.flush()


def serve() -> int:
    """stdin/stdout JSON-RPC 루프. 한 줄 = 한 요청."""
    sys.stdin.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # type: ignore[union-attr]
    log.info("rpc.server.start", methods=len(RPC_METHODS))
    _emit_ready()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = dispatch_request(line)
        if response:  # 알림(notification)은 빈 문자열 → 미출력
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
    log.info("rpc.server.stop")
    return 0


if __name__ == "__main__":
    sys.exit(serve())
