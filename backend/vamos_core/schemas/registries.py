"""VAMOS 레지스트리 5종 (V0) — D2.1-D2 §5 SOT + D2.1-D4 §4.1 + D2.1-D3 §4.1.

자동 생성: scripts/gen_registries_py.py (P4-0, 2026-06-12) — 직접 수정 금지.
값 변경은 SOT(D2.1) 개정 + seed 재추출 + 본 파일 재생성으로만 수행 (A20 준용).
분모: EventType 123 / FailureCode 36 / Fallback 23 / Tool seed 2 / Node seed 1.
네이밍: event=lower.dot / failure=UPPER_SNAKE / fallback=FB_UPPER_SNAKE (VL-005).
"""

from __future__ import annotations

from typing import Any, Final

#: EventTypeRegistry — D2.1-D2 §5.1 (123, lower.dot)
EVENT_TYPES: Final[tuple[str, ...]] = (
    "oc.request.received",
    "oc.i1.parse.started",
    "oc.i1.intent.parsed",
    "oc.i1.intent.ambiguous",
    "oc.i1.parse.failed",
    "oc.i2.query.built",
    "oc.i2.fetch.started",
    "oc.i2.evidence.ready",
    "oc.i2.evidence.insufficient",
    "oc.i2.fetch.blocked",
    "oc.i2.fetch.failed",
    "oc.i3.plan.created",
    "oc.i3.commit.requested",
    "oc.i3.commit.approval_required",
    "oc.i3.commit.completed",
    "oc.i3.commit.denied",
    "oc.i3.commit.failed",
    "oc.i4.structuring.started",
    "oc.i4.output.structured",
    "oc.i4.spec.violated",
    "oc.i4.mask.applied",
    "oc.i4.structuring.failed",
    "oc.i5.gates.evaluated",
    "oc.i5.route.selected",
    "oc.i5.decision.locked",
    "oc.i5.approval.required",
    "oc.i5.cost.downshifted",
    "oc.i5.policy.blocked",
    "oc.i5.decision.failed",
    "oc.loop.retry.reasoning",
    "oc.loop.retry.action",
    "oc.deny.blocked",
    "oc.done",
    "oc.p2.activated",
    "oc.p2.deactivated",
    "wf.stage.enter",
    "wf.stage.exit",
    "wf.approval.requested",
    "wf.report.created",
    "ui.builder.run.started",
    "ui.builder.node.inspected",
    "ui.builder.approval.granted",
    "ui.builder.approval.denied",
    "ui.builder.cost.mode_changed",
    "ui.builder.memory.candidate_excluded",
    "ui.builder.log.filtered",
    "ui.builder.debug.step_over",
    "ui.builder.session.loaded",
    "ui.builder.artifact.exported",
    "ui.builder.policy.edit.attempted",
    "ui.builder.approval.requested",
    "ui.builder.simulate.started",
    "ui.builder.simulate.finished",
    "ui.frontmini.input.received",
    "ui.frontmini.scan.started",
    "ui.frontmini.pii.detected",
    "ui.frontmini.malware.found",
    "ui.frontmini.summary.ready",
    "ui.frontmini.package.ready",
    "ui.frontmini.package.sent",
    "ui.core.received",
    "ui.core.intent.analyzed",
    "ui.core.decision.locked",
    "ui.core.p2.locked",
    "ui.core.p2.modal.shown",
    "ui.core.p2.modal.confirmed",
    "ui.core.p2.modal.cancelled",
    "ui.gate.policy.checked",
    "ui.gate.policy.violated",
    "ui.gate.cost.calculated",
    "ui.gate.cost.warning",
    "ui.gate.cost.warning_80",
    "ui.gate.cost.ceiling_100",
    "ui.gate.approval.required",
    "ui.gate.approval.waiting",
    "ui.policy.blocked",
    "ui.node.selected",
    "ui.node.context.loaded",
    "ui.main.job.queued",
    "ui.main.execution.started",
    "ui.main.step.started",
    "ui.main.stream.chunk",
    "ui.main.artifact.created",
    "ui.main.evidence.linked",
    "ui.main.selfcheck.started",
    "ui.main.selfcheck.passed",
    "ui.main.selfcheck.failed",
    "ui.main.qod.updated",
    "ui.main.alert.shown",
    "ui.tool.call.started",
    "ui.tool.call.finished",
    "ui.tool.error.timeout",
    "ui.tool.error.ratelimit",
    "ui.tool.error.parse",
    "ui.tool.file.converted",
    "ui.memory.candidate.found",
    "ui.memory.masking.applied",
    "ui.memory.commit.success",
    "ui.memory.commit.denied",
    "ui.memory.source.trust_updated",
    "ui.cli.command.received",
    "ui.cli.command.completed",
    "ui.cli.command.failed",
    "ui.cli.auth.prompted",
    "ui.cli.auth.resolved",
    "ui.cli.progress.updated",
    "ui.cli.output.streamed",
    "ui.cli.config.changed",
    "ui.cli.session.started",
    "ui.cli.session.ended",
    "mem.reference.updated",
    "mem.kb.derived",
    "storage.policy.checked",
    "storage.memory.write.requested",
    "storage.memory.write.completed",
    "storage.vector.insert.denied",
    "storage.pii.longterm.denied",
    "agent.task.started",
    "agent.task.completed",
    "agent.task.failed",
    "sdar.risk.assessed",
    "sdar.audit.logged",
    "sdar.safety.checked",
)

#: FailureCodeRegistry — D2.1-D2 §5.2 (36, UPPER_SNAKE)
FAILURE_CODES: Final[tuple[str, ...]] = (
    "OC_I1_PARSE_FAIL",
    "OC_I1_AMBIGUOUS_UNRESOLVED",
    "OC_I2_RAG_NO_SOURCE",
    "OC_I2_EVIDENCE_QOD_LOW",
    "OC_I2_SOURCE_POLICY_BLOCK",
    "OC_I2_TIMEOUT",
    "OC_I3_MEMORY_POLICY_DENY",
    "OC_I3_APPROVAL_REQUIRED",
    "OC_I3_COMMIT_FAIL",
    "OC_I4_OUTPUT_SPEC_VIOLATION",
    "OC_I4_CITATION_MISSING",
    "OC_I4_MASK_FAIL",
    "OC_I5_POLICY_BLOCK",
    "OC_I5_APPROVAL_REQUIRED",
    "OC_I5_COST_OVER_BUDGET",
    "OC_I5_EVIDENCE_INSUFFICIENT",
    "OC_I5_ROUTE_NOT_FOUND",
    "PII_LONGTERM_DENIED",
    "POLICY_DENY",
    "GT_ERR_COST_LIMIT",
    "TOOL_TIMEOUT",
    "FM_ERR_FMT",
    "FM_ERR_SIZE",
    "FM_ERR_PII",
    "FM_ERR_ZERO",
    "OC_ERR_NONGOAL",
    "OC_ERR_P2_LOCK",
    "OC_ERR_COST_LV",
    "OC_ERR_COST_OV",
    "OC_ERR_NO_ROUTE",
    "TL_ERR_TIMEOUT",
    "TL_ERR_403",
    "TL_ERR_PARSE",
    "MC_ERR_LOW_QOD",
    "MC_ERR_CONFLICT",
    "MC_ERR_STALE",
)

#: FallbackRegistry — D2.1-D2 §5.3 (23, FB_UPPER_SNAKE)
FALLBACK_IDS: Final[tuple[str, ...]] = (
    "FB_INTENT_HEURISTIC_PARSE",
    "FB_ASK_CLARIFICATION",
    "FB_RAG_RETRY_EXPAND",
    "FB_RAG_SWITCH_SOURCE",
    "FB_MEMORY_META_ONLY",
    "FB_REQUIRE_APPROVAL",
    "FB_OUTPUT_REFORMAT",
    "FB_OUTPUT_MINIMAL",
    "FB_POLICY_MASK",
    "FB_COST_DOWNSHIFT",
    "FB_ROUTE_SAFE_NODE",
    "FB_RESTRICT_GENERAL_INFO",
    "FB_DENY_WITH_REASON",
    "FB_DENY_STORAGE",
    "FB_REJECT_INPUT",
    "FB_MASK_AND_CONFIRM",
    "FB_REQ_REUPLOAD",
    "FB_RETRY_SOFT",
    "FB_USE_WEB_SEARCH",
    "FB_RETURN_RAW",
    "FB_AUTO_REPAIR",
    "FB_SHOW_CONFLICT",
    "FB_SHOW_STALE",
)

#: ToolRegistry seed — D2.1-D4 §4.1 (2 seed entries; 정본 목록 확정은 G2 이후)
TOOL_REGISTRY_SEED: Final[tuple[dict[str, Any], ...]] = (
    {
        "tool_id": "llm_openai_text",
        "category": "llm.text",
        "adapter_id": "llm_openai_text",
        "risk_class": "low",
        "cost_class": "v1",
        "required_gates": [
            "policy",
            "cost"
        ],
        "outputs": [
            "signal",
            "log"
        ],
        "notes": "seed example only (D2.1-D4 §4.1)"
    },
    {
        "tool_id": "tool_playwright",
        "category": "browser.render",
        "adapter_id": "tool_playwright",
        "risk_class": "high",
        "cost_class": "v2",
        "required_gates": [
            "policy",
            "cost",
            "approval"
        ],
        "outputs": [
            "artifact",
            "log"
        ],
        "notes": "seed example only (D2.1-D4 §4.1)"
    },
)

#: NodeRegistry seed — D2.1-D3 §4.1 (1 seed entry; node_id/domain 필수 LOCK)
NODE_REGISTRY_SEED: Final[tuple[dict[str, Any], ...]] = (
    {
        "node_id": "bn_web_research",
        "domain": "research",
        "capabilities": {},
        "constraints": {}
    },
)

EVENT_TYPE_SET: Final[frozenset[str]] = frozenset(EVENT_TYPES)
FAILURE_CODE_SET: Final[frozenset[str]] = frozenset(FAILURE_CODES)
FALLBACK_ID_SET: Final[frozenset[str]] = frozenset(FALLBACK_IDS)


def is_valid_event_type(value: str) -> bool:
    """EventTypeRegistry 등재 여부 (LogEventSchema.event_type 검증용)."""
    return value in EVENT_TYPE_SET


def is_valid_failure_code(value: str) -> bool:
    """FailureCodeRegistry 등재 여부."""
    return value in FAILURE_CODE_SET


def is_valid_fallback_id(value: str) -> bool:
    """FallbackRegistry 등재 여부."""
    return value in FALLBACK_ID_SET
