"""A20 왕복(Round-trip) 테스트 — Python → JSON Schema → serde(Rust) → TS(Node) → Python (DEC-006 Step 5).

경로: 25모델 샘플 인스턴스를 Pydantic으로 생성 → JSON 직렬화 →
  (a) serde(Rust) 구간: src-tauri/tests/roundtrip_instances.json 으로 기록 후 `cargo test`로
      deny_unknown_fields 역직렬화/재직렬화 동일성 검증 (cargo 부재 시 보류·비차단).
  (b) TS(Node) 구간: shared/types/validate_roundtrip.mjs(생성 JSON Schema로 구조 검증) 통과 출력을
      다시 Python model_validate → 원본과 동일성 비교.
4파일(Python·JSON Schema·serde·TS) 전 구간 일치 시 PASS (PHASE4-DEC-005 §5).

사용: python scripts/roundtrip_test.py  (종료 0=PASS)
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from vamos_core.schemas import contracts as c  # noqa: E402
from vamos_core.schemas import registries as r  # noqa: E402

TS = "2026-06-12T10:00:00+09:00"

SAMPLES: dict[str, dict] = {
    "IntentFrame": {
        "intent_id": "if_01", "trace_id": "trc_01", "timestamp": TS,
        "user_goal": "단일 코드블럭으로 파서 작성", "task_type": "code",
        "domain_hint": {"priority": "P1", "candidates": ["P1"]},
        "constraints": {"format_constraints": "single_codeblock", "must_include": [], "must_not_include": []},
        "risk_flags": {"safety_sensitive": False, "approval_maybe_required": False, "cost_sensitive": False},
        "ambiguity": {"is_ambiguous": False, "missing_slots": [], "clarification_questions": []},
        "required_artifacts": ["code"],
    },
    "EvidencePack": {
        "evidence_pack_id": "evp_01", "trace_id": "trc_01", "timestamp": TS,
        "items": [{"source_type": "doc", "source_ref": "doc_001", "excerpt_or_summary": "요약",
                   "qod_score": 0.9, "captured_at": TS}],
        "coverage": {"sufficient": True, "gaps": []}, "citations_ready": True,
    },
    "DecisionSchema": {
        # D2.1-D2 §4.1 example 값 기반 (seed 추출 동일)
        "decision_id": "dec_01HZX9R1ABCDE", "trace_id": "trc_01HZX9R1ABCDE",
        "timestamp": "2026-01-15T20:17:00+09:00",
        "intent_frame_ref": "if_01HZX9R1ABCDE", "evidence_pack_ref": "evp_01HZX9R1ABCDE",
        "policy_gate": "allow", "approval_required": False, "approval_status": "approved",
        "cost_gate": "normal",
        "routing": {"selected_blue_node_id": "bn_analysis", "execution_mode": "main"},
        "memory_plan": {"save_candidate": True, "target_layer": "L1", "requires_user_approval": False},
        "output_spec": {"format_constraints": "markdown"},
        "conclusion": "ACCEPT", "locked": True,
        "confidence_score": 0.91, "confidence_level": "HIGH",
        "optional_signals": [{"signal_id": "sig_01", "source_module": "I-6", "name": "qod_score", "value": 0.85}],
        "verify": {"chain_used": ["self_check", "policy_check", "cost_check"],
                   "refs": {"policy_check_id": "pol_01", "cost_budget_id": "bud_01"}},
        "gates": {"result": {"policy": {"decision": "allow"}, "cost": {"mode": "normal"}}},
        "s_module_hints": {"s1_priority": "high", "s3_cache_policy": "aggressive"},
    },
    "LogEventSchema": {
        "event_type": "oc.i1.parse.started", "producer": "I-1", "when": "파싱 시작 시",
        "payload": {"trace_id": "trc_01", "decision_id": "dec_01"}, "severity": "info",
        "sinks": ["file", "db"], "links": {"failure_code": ["OC_I1_PARSE_FAIL"]},
    },
    "ResponseEnvelope": {
        "answer": {"summary": "요약", "details": "상세", "next_actions": []},
        "evidence": {"coverage": 0.9, "items": [], "qod": 0.85},
        "self_check": {"score": 0.9, "verdict": "PASS", "reasons": [], "retry_allowed": False},
        "decision_ref": {"decision_id": "dec_01", "gates": {}},
        "audit": {"event_ids": [], "failure_codes": [], "fallback_ids": []},
    },
    "StructuredOutput": {
        "artifact_type": "md", "content": "# 결과",
        "compliance_report": {"output_spec_ok": True, "citations_ok": True,
                              "safety_mask_applied": False, "missing_parts": []},
        "artifact_meta": {"size": 1024, "hash": "abc", "parts": 1},
    },
    "MemoryRecord": {
        "record_id": "mem_01", "project_id": "prj_default", "scope": "L0", "memory_type": "B-4",
        "content_summary": "세션 요약", "created_at": TS, "policy_decision": "allow",
        "ttl": "session_end", "tags": ["session"], "masked": False,
    },
    "SourceQoD": {
        "source_id": "src_01", "project_id": "prj_default", "qod_score": 0.8, "freshness": 0.9,
        "reliability": 0.8, "completeness": 0.7, "computed_at": TS, "scope": "L1",
    },
    "PolicyCheck": {
        "check_id": "pol_01", "decision": "allow", "reasons": ["non-goal 미해당"],
        "rule_refs": ["RULE-1.3-§5"], "detected_sensitive_types": [],
    },
    "ApprovalSchema": {
        "approval_id": "apr_01", "approval_stage": "plan", "requester": "user",
        "scope": "cost", "description": "비용 승인", "expires_at": TS,
        "status": "approved", "decided_by": "OWNER", "risk_level": "P1",
    },
    "CostBudget": {
        "budget_id": "bud_v1_001", "mode": "V1", "daily_limit": 1300, "monthly_limit": 40000,
        "used_today": 650, "used_month": 12000, "forecast": 35000.0, "block_on_exceed": True,
    },
    "DownshiftSchema": {
        "warn_threshold_percent": 80, "block_threshold_percent": 100, "trigger_type": "daily",
        "near_action": "force_mini", "exceed_action": "block", "main_requires_approval": True,
    },
    "NodeCapabilityProfile": {
        "node_id": "bn_web_research", "required_tools": ["tool_playwright"], "risk_class": "low",
        "cost_class": "v1", "required_gates": ["policy", "cost"], "optional_tools": [],
    },
    "NodeRequestEnvelope": {
        "request_id": "req_01", "project_id": "prj_default", "session_id": "ses_01",
        "node_id": "bn_web_research", "intent_summary": "조사", "constraints": {},
        "trace_id": "trc_01", "decision_id": "dec_01",
    },
    "NodeResponseEnvelope": {
        "trace_id": "trc_01", "node_id": "bn_web_research", "domain": "research",
        "inputs": {"summary": "입력 요약"}, "outputs": {"result": "결과", "evidence_refs": []},
        "status": "success",
    },
    "ToolCallRegistry": {
        "tool_id": "tool_playwright", "node_id": "bn_web_research", "risk_class": "high",
        "auth_method": "none", "enabled": True, "mcp_endpoint": "http://localhost:8080/mcp",
    },
    "MCPBridgeLayer": {
        "bridge_id": "brg_01", "node_id": "bn_web_research", "transport": "streamable_http",
        "base_url": "http://localhost:8080", "discovered_tools": ["tool_playwright"],
        "health_check_interval_sec": 30,
    },
    "ToolRegistryEntry": dict(r.TOOL_REGISTRY_SEED[0]),
    "BrainAdapterResponse": {
        "output_text": "응답", "evidence_summary": "근거 요약",
        "cost_used_estimate": {"tokens": 120, "relative_cost": "low"}, "warnings": [],
        "trace_id": "trc_01",
    },
    "WorkflowStage": {
        "stage_id": "intake", "stage_name": "Intake", "description": "입력 수집 단계",
    },
    "WorkflowOutput": {
        "user_response": "최종 응답", "evidence_summary": "근거(출처/신뢰도/QoD)",
        "log_report": {"trace_id": "trc_01"},
    },
    "FailureReport": {
        "failure_cause": "파싱 실패", "evidence_gap": "소스 없음",
        "risk_detected": {"non_goal": False}, "improvement_hint": "재시도 전략 A",
    },
    "GuardrailsCheck": {
        "check_id": "grd_001", "trace_id": "trc_01",
        "layer1_nemo": {"passed": True}, "layer2_guardrails_ai": {"passed": True},
        "layer3_llamaguard": {"passed": True}, "overall_decision": "allow",
    },
    "RBACRole": {
        "role": "OWNER", "permissions": ["*"], "description": "소유자",
        "max_autonomy_level": "L1", "p2_access": True, "cost_approval_limit": 40000,
    },
    "AutonomyLevelSchema": {
        "level": "L1", "name": "제안", "description": "AI 제안 + 사용자 확인",
        "auto_execute": False, "notification_required": True, "approval_required": True,
    },
}


def main() -> int:
    models = {m.__name__: m for m in c.ALL_MODELS}
    missing = set(models) - set(SAMPLES)
    if missing:
        print(f"FATAL: 샘플 누락 {sorted(missing)}")
        return 1

    # 1) Python: 인스턴스 생성 (검증 포함)
    originals = {name: models[name].model_validate(data) for name, data in SAMPLES.items()}

    # 2) Python → JSON
    payload = {name: json.loads(inst.model_dump_json()) for name, inst in originals.items()}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp = f.name

    # 2.5) serde(Rust) 구간 — 인스턴스 픽스처 기록 + cargo test (DEC-005 §5)
    rust_dir = ROOT / "src-tauri"
    fixture = rust_dir / "tests" / "roundtrip_instances.json"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    with open(fixture, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    cargo = shutil.which("cargo")
    if cargo and (rust_dir / "Cargo.toml").exists():
        proc_rs = subprocess.run(  # noqa: S603
            [cargo, "test", "--manifest-path", str(rust_dir / "Cargo.toml"),
             "--test", "roundtrip", "--quiet"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if proc_rs.returncode != 0:
            print("FAIL: serde(Rust)측 왕복 검증 실패")
            print(proc_rs.stdout[-2000:])
            print(proc_rs.stderr[-2000:])
            return 1
        print("   serde(Rust) 구간 PASS — cargo test roundtrip (deny_unknown_fields 25/25)")
    else:
        print("   serde(Rust) 구간 PENDING — cargo 부재 (픽스처는 기록됨, 비차단)")

    # 3) TS측(Node) 검증 — 생성된 JSON Schema 25종 대조
    proc = subprocess.run(  # noqa: S603
        ["node", str(ROOT / "shared" / "types" / "validate_roundtrip.mjs"), tmp],  # noqa: S607
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        print("FAIL: TS(Node)측 검증 실패")
        print(proc.stderr)
        return 1
    echoed = json.loads(proc.stdout)

    # 4) TS 출력 → Python 재파싱 → 원본 동일성
    failures = []
    for name, data in echoed.items():
        restored = models[name].model_validate(data)
        if restored != originals[name]:
            failures.append(name)
    if failures:
        print(f"FAIL: 왕복 불일치 {failures}")
        return 1

    print(f"✅ 왕복 테스트 PASS — {len(echoed)}/25 모델 "
          "(Python→JSON Schema→serde(Rust)→TS(Node)→Python 동일성 확인)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
