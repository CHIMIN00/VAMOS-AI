"""V0 스키마 검증 테스트 — P4-0 4-1 (PART2 V0-STEP-2 Stage Gate + STEP-6 test_schemas).

분모 정본: D2.1 SOT + PHASE3-DEC-010 (DecisionSchema 20 — PHASE4-DEC-003).
"""

from __future__ import annotations

import pydantic
import pytest

from vamos_core.schemas import contracts as c
from vamos_core.schemas import registries as r

# 모델별 기대 필드 수 (SOT 실측 — P4-0 2026-06-12)
EXPECTED_FIELD_COUNTS = {
    "IntentFrame": 10,
    "EvidencePack": 6,
    "DecisionSchema": 20,  # FREEZE 18 + DEC-010 confidence 2
    "LogEventSchema": 7,
    "ResponseEnvelope": 5,  # LOCK
    "StructuredOutput": 4,
    "MemoryRecord": 20,
    "SourceQoD": 8,
    "PolicyCheck": 7,
    "ApprovalSchema": 12,
    "CostBudget": 9,
    "DownshiftSchema": 6,
    "NodeCapabilityProfile": 6,
    "NodeRequestEnvelope": 12,
    "NodeResponseEnvelope": 6,
    "ToolCallRegistry": 7,
    "MCPBridgeLayer": 7,
    "ToolRegistryEntry": 8,
    "BrainAdapterResponse": 7,
    "WorkflowStage": 4,  # LOCK
    "WorkflowOutput": 3,  # LOCK
    "FailureReport": 4,
    "GuardrailsCheck": 7,
    "RBACRole": 6,
    "AutonomyLevelSchema": 7,
}


def test_model_count_is_25() -> None:
    assert len(c.ALL_MODELS) == 25


@pytest.mark.parametrize("model", c.ALL_MODELS, ids=lambda m: m.__name__)
def test_field_counts(model: type) -> None:
    assert len(model.model_fields) == EXPECTED_FIELD_COUNTS[model.__name__]


def test_decision_schema_field_count() -> None:
    """DecisionSchema는 정확히 20필드 (FREEZE 18 + DEC-010 confidence 2)."""
    fields = c.DecisionSchema.model_fields
    assert len(fields) == 20
    required = [n for n, f in fields.items() if f.is_required()]
    assert len(required) == 16  # 14 + confidence 2 (PHASE4-DEC-003)


def test_response_envelope_field_count() -> None:
    """ResponseEnvelope은 정확히 5필드 (LOCK)."""
    assert len(c.ResponseEnvelope.model_fields) == 5


def test_workflow_lock_field_counts() -> None:
    assert len(c.WorkflowStage.model_fields) == 4
    assert len(c.WorkflowOutput.model_fields) == 3


@pytest.mark.parametrize("model", c.ALL_MODELS, ids=lambda m: m.__name__)
def test_extra_forbid(model: type) -> None:
    """전 모델 extra='forbid' 적용 (R2)."""
    assert model.model_config.get("extra") == "forbid"


def test_extra_field_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        c.WorkflowOutput(
            user_response="r", evidence_summary="e", log_report={}, bogus_field=1,
        )


def test_required_field_missing_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        c.WorkflowOutput(user_response="r")  # evidence_summary/log_report 누락


def test_confidence_score_range() -> None:
    """confidence_score 0.0~1.0 (DEC-010)."""
    base = {
        "decision_id": "d", "trace_id": "t", "timestamp": "2026-06-12T00:00:00+09:00",
        "intent_frame_ref": "i", "evidence_pack_ref": "e", "policy_gate": "allow",
        "approval_required": False, "approval_status": "approved", "cost_gate": "normal",
        "routing": {}, "memory_plan": {}, "output_spec": {}, "conclusion": "ACCEPT",
        "locked": True, "confidence_level": "HIGH",
    }
    with pytest.raises(pydantic.ValidationError):
        c.DecisionSchema(**base, confidence_score=1.5)


def test_registry_counts() -> None:
    """레지스트리 분모 — D2.1-D2 SOT (123/36/23) + Tool 2 + Node 1."""
    assert len(r.EVENT_TYPES) == 123
    assert len(r.FAILURE_CODES) == 36
    assert len(r.FALLBACK_IDS) == 23
    assert len(r.TOOL_REGISTRY_SEED) == 2
    assert len(r.NODE_REGISTRY_SEED) == 1


def test_registry_no_duplicates() -> None:
    assert len(set(r.EVENT_TYPES)) == 123
    assert len(set(r.FAILURE_CODES)) == 36
    assert len(set(r.FALLBACK_IDS)) == 23


def test_registry_naming_conventions() -> None:
    """VL-005: event=lower.dot / failure=UPPER_SNAKE / fallback=FB_UPPER_SNAKE."""
    assert all(e == e.lower() and "." in e for e in r.EVENT_TYPES)
    assert all(f == f.upper() for f in r.FAILURE_CODES)
    assert all(fb.startswith("FB_") and fb == fb.upper() for fb in r.FALLBACK_IDS)


def test_registry_membership_helpers() -> None:
    assert r.is_valid_event_type("oc.i1.parse.started")
    assert not r.is_valid_event_type("oc.fake.event")
    assert r.is_valid_failure_code("OC_I1_PARSE_FAIL")
    assert r.is_valid_fallback_id("FB_INTENT_HEURISTIC_PARSE")
