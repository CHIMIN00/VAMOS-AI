"""V0-STEP-3 IPC JSON-RPC 서버 테스트 (Stage Gate #1~#3, #8)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from vamos_core.rpc import server

BACKEND_DIR = Path(__file__).resolve().parent.parent

# 13 메서드 × 유효 파라미터 (정상 응답 경로)
VALID_PARAMS: dict[str, dict[str, Any]] = {
    "langgraph.workflow.run": {"trace_id": "t1", "user_input": "hello"},
    "langgraph.stage.execute": {"trace_id": "t1", "workflow_id": "w1", "stage_id": "intake"},
    "langgraph.decision.create": {"trace_id": "t1", "intent_frame_ref": "if1",
                                  "evidence_pack_ref": "ev1"},
    "langgraph.node.dispatch": {"trace_id": "t1", "node_id": "bn_web_research"},
    "langgraph.verify.run_chain": {"trace_id": "t1", "decision_id": "d1"},
    "embedding.encode": {"trace_id": "t1", "texts": ["a", "b"]},
    "embedding.store": {"trace_id": "t1", "record_id": "r1"},
    "llm.generate": {"trace_id": "t1", "prompt": "p"},
    "llm.record_invoke": {"trace_id": "t1", "model_id": "gpt-4o-mini"},
    "llm.rate_limit.get": {"trace_id": "t1", "target_id": "tg1"},
    "mcp.bridge.init": {"trace_id": "t1", "bridge_id": "b1"},
    "mcp.bridge.health": {"trace_id": "t1", "bridge_id": "b1"},
    "mcp.tools.discover": {"trace_id": "t1", "bridge_id": "b1"},
}


def _call(method: str, params: dict[str, Any], req_id: int = 1) -> dict[str, Any]:
    raw = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": req_id})
    result: dict[str, Any] = json.loads(server.dispatch_request(raw))
    return result


def test_method_count_is_13() -> None:
    assert len(server.RPC_METHODS) == 13
    assert len(set(server.RPC_METHODS)) == 13  # 중복 0


def test_all_13_methods_have_valid_param_coverage() -> None:
    assert set(VALID_PARAMS) == set(server.RPC_METHODS)


def test_all_13_methods_return_normal_result() -> None:
    """Stage Gate #2: 각 메서드 → JSON-RPC 정상 응답(에러 아님)."""
    for m in server.RPC_METHODS:
        resp = _call(m, VALID_PARAMS[m])
        assert "result" in resp, f"{m} 정상 result 부재: {resp}"
        assert "error" not in resp, f"{m} 예기치 않은 error: {resp}"
        assert resp["result"]["trace_id"] == "t1"
        assert resp["result"]["v0_stub"] is True


def test_unknown_method_returns_minus_32601() -> None:
    """Stage Gate #3: 미존재 메서드 → -32601."""
    resp = _call("does.not.exist", {"trace_id": "t1"})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_missing_required_param_returns_minus_32602() -> None:
    """필수 파라미터 누락 → -32602 (파라미터 검증)."""
    resp = _call("langgraph.workflow.run", {"trace_id": "t1"})  # user_input 누락
    assert "error" in resp
    assert resp["error"]["code"] == -32602


def test_business_error_links_failure_code_registry() -> None:
    """비즈니스 에러 → -32000 + data.failure_code = FailureCodeRegistry 등재값."""
    resp = _call("langgraph.stage.execute",
                 {"trace_id": "t1", "workflow_id": "w1", "stage_id": "BOGUS"})
    assert "error" in resp
    assert resp["error"]["code"] == server.BUSINESS_ERROR_CODE
    data = resp["error"]["data"]
    assert data["failure_code_registered"] is True
    assert data["failure_code"] == "OC_I5_ROUTE_NOT_FOUND"
    assert data["trace_id"] == "t1"


def test_subprocess_ready_message_and_dispatch() -> None:
    """Stage Gate #1: spawn → stdout ready + 정상 디스패치 + stderr 로그 분리."""
    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", "vamos_core.rpc.server"],
        cwd=str(BACKEND_DIR), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1,
    )
    try:
        ready = proc.stdout.readline()  # type: ignore[union-attr]
        ready_obj = json.loads(ready)
        assert ready_obj["method"] == "server.ready"
        assert ready_obj["params"]["methods"] == 13

        req = json.dumps({"jsonrpc": "2.0", "method": "llm.generate",
                          "params": {"trace_id": "t9", "prompt": "x"}, "id": 7})
        proc.stdin.write(req + "\n")  # type: ignore[union-attr]
        proc.stdin.flush()  # type: ignore[union-attr]
        resp = json.loads(proc.stdout.readline())  # type: ignore[union-attr]
        assert resp["id"] == 7
        assert resp["result"]["trace_id"] == "t9"
    finally:
        proc.stdin.close()  # type: ignore[union-attr]
        out, err = proc.communicate(timeout=5)
    # stderr 분리: 로그(structlog)는 stderr에만, stdout(ready+resp)에 로그 혼입 없음
    assert "rpc.server.start" in err  # structlog → stderr
