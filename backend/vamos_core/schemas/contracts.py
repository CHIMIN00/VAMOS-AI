"""VAMOS 핵심 Pydantic v2 계약 모델 25종 (V0 서브셋 — A20 단일 정본, 유일한 수동 편집 지점).

생성: P4-0 4-1 타입 동기화 (2026-06-12). 필드 정의는 전건 SOT verbatim 추출 — 창작 0.
  - D2.1-D2 §4.1/§4.2 (Decision 18+DEC-010 2 = 20 FREEZE / LogEvent 7)
  - D2.0-02 I-1/I-2/I-4 상세 출력 (IntentFrame 10 / EvidencePack 6 / StructuredOutput 4)
  - CLAUDE.md §12 (ResponseEnvelope 5 LOCK)
  - D2.1-D3 §5.1~5.5 / D2.1-D4 §4.1~4.2 / D2.1-D5 §4.1~4.4 / D2.1-D6 §4.1~4.2 / D2.1-D7 §4.1~4.7
교차 검증: schemas/seed/*.json (Method B). 불일치 시 SOT 우선 + 즉시 중단 보고 (PART2 §1.3.1 #1).
파생물(JSON Schema/TS)은 scripts/generate_types.py 자동 생성 — 직접 수정 금지 (A20/DEC-006).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class VamosModel(BaseModel):
    """공통 베이스 — extra='forbid' 전 모델 의무 (R2)."""

    model_config = ConfigDict(extra="forbid")


# ── ORANGE CORE 파이프라인 (D2.0-02 / D2.1-D2 / CLAUDE.md §12) ──────────────


class IntentFrame(VamosModel):
    """I-1 출력 — D2.0-02 I-1 상세 (10필드)."""

    intent_id: str
    trace_id: str
    timestamp: str
    user_goal: str
    task_type: Literal["explain", "plan", "code", "research", "summarize", "design", "debug", "etc"]
    domain_hint: dict[str, Any]  # P0/P1/P2 + 후보 리스트
    constraints: dict[str, Any]  # format_constraints + must_include[]/must_not_include[]
    risk_flags: dict[str, Any]  # safety_sensitive/approval_maybe_required/cost_sensitive (bool)
    ambiguity: dict[str, Any]  # is_ambiguous + missing_slots[] + clarification_questions[](0..3)
    required_artifacts: list[str]  # doc|pdf|ppt|sheet|code|diagram|etc


class EvidencePack(VamosModel):
    """I-2 출력 — D2.0-02 I-2 상세 (6필드)."""

    evidence_pack_id: str
    trace_id: str
    timestamp: str
    items: list[dict[str, Any]]  # source_type/source_ref/excerpt_or_summary/qod_score/captured_at
    coverage: dict[str, Any]  # sufficient(bool) + gaps[]
    citations_ready: bool


class DecisionSchema(VamosModel):
    """단일 Decision Kernel 산출물 — D2.1-D2 §4.1 FREEZE 18 + PHASE3-DEC-010 confidence 2 = 20필드.

    16 required + 4 optional. 필드 추가/삭제 절대 불가 (FREEZE — 변경은 A20 6-Step + ADR).
    """

    decision_id: str
    trace_id: str
    timestamp: str
    intent_frame_ref: str
    evidence_pack_ref: str
    policy_gate: Literal["block", "require_approval", "mask", "allow"]
    approval_required: bool
    approval_status: Literal["approved", "denied"]  # D7 정본 2값 (PL-09 FIX, DN-014)
    cost_gate: Literal["normal", "downshift", "split", "stop"]
    routing: dict[str, Any]  # selected_blue_node_id + execution_mode(mini|main|tool)
    memory_plan: dict[str, Any]  # save_candidate + target_layer(L0|L1|L2) + requires_user_approval
    output_spec: dict[str, Any]  # format_constraints 등
    conclusion: Literal["ACCEPT", "REJECT", "HOLD", "ESCALATE"]
    locked: bool
    optional_signals: list[dict[str, Any]] | None = None
    verify: dict[str, Any] | None = None
    gates: dict[str, Any] | None = None
    s_module_hints: dict[str, Any] | None = None
    # PHASE3-DEC-010 확장 2필드 (required — seed/SOT 순서 정렬: 원본 18 뒤 말미 추가)
    confidence_score: float = Field(ge=0.0, le=1.0)  # A25, 0.0~1.0
    confidence_level: Literal["HIGH", "MEDIUM", "LOW", "REFUSE"]  # 임계 0.85/0.60/0.30 LOCK


class LogEventSchema(VamosModel):
    """표준 이벤트 로그 — D2.1-D2 §4.2 (7필드, 5+2)."""

    event_type: str  # D2.1-D2 EventTypeRegistry 값 (registries.EVENT_TYPES 검증)
    producer: str
    when: str
    payload: dict[str, Any]
    severity: Literal["info", "warn", "error", "critical"]
    sinks: list[str] | None = None
    links: dict[str, Any] | None = None


class ResponseEnvelope(VamosModel):
    """최종 응답 봉투 — CLAUDE.md §12 (5필드 LOCK)."""

    answer: dict[str, Any]  # summary + details + next_actions[]
    evidence: dict[str, Any]  # coverage(0~1) + items[] + qod(0~1)
    self_check: dict[str, Any]  # score(0~1) + verdict(PASS|WARN|FAIL) + reasons[] + retry_allowed
    decision_ref: dict[str, Any]  # decision_id + gates{}
    audit: dict[str, Any]  # event_ids[] + failure_codes[] + fallback_ids[]


class StructuredOutput(VamosModel):
    """I-4 출력 — D2.0-02 I-4 상세 (4필드)."""

    artifact_type: Literal["md", "json", "code", "diagram", "etc"]
    content: str
    compliance_report: dict[str, Any]  # output_spec_ok/citations_ok/safety_mask/missing_parts[]
    artifact_meta: dict[str, Any]  # size/hash/parts


# ── STORAGE / MEMORY (D2.1-D6) ──────────────────────────────────────────────


class MemoryRecord(VamosModel):
    """메모리 레코드 — D2.1-D6 §4.1 (20필드, 7+13)."""

    record_id: str
    project_id: str
    scope: Literal["L0", "L1", "L2", "L3"]
    memory_type: Literal["B-1", "B-2", "B-3", "B-4"]
    content_summary: str
    created_at: str
    policy_decision: Literal["allow", "restrict", "deny"]
    ttl: str | None = None
    tags: list[str] | None = None
    source_refs: list[str] | None = None
    masked: bool | None = None
    activation_state: Literal["draft", "approved", "active", "deprecated"] | None = None
    version: str | None = None
    procedure_id: str | None = None
    target_scope: Literal["global", "project"] | None = None
    trigger_conditions: str | None = None
    steps: list[str] | None = None
    required_tools: list[str] | None = None
    safety_notes: str | None = None
    provenance: dict[str, Any] | None = None


class SourceQoD(VamosModel):
    """소스 QoD — D2.1-D6 §4.2 (8필드, 7+1)."""

    source_id: str
    project_id: str
    qod_score: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    computed_at: str
    scope: Literal["L0", "L1", "L2", "L3"] | None = None


# ── SAFETY / COST / APPROVAL (D2.1-D7) ──────────────────────────────────────


class PolicyCheck(VamosModel):
    """정책 체크 결과 — D2.1-D7 §4.1 (7필드, 5+2)."""

    check_id: str
    decision: Literal["deny", "restrict", "allow"]
    reasons: list[str]
    rule_refs: list[str]
    detected_sensitive_types: list[Literal["PII", "AUTH", "MEDICAL", "LEGAL"]]
    fallback_id: str | None = None
    required_approval_id: str | None = None


class ApprovalSchema(VamosModel):
    """승인 객체 — D2.1-D7 §4.2 (12필드, 8+4)."""

    approval_id: str
    approval_stage: Literal["plan", "execute"]
    requester: str
    scope: Literal["domain", "cost", "policy", "external_action", "storage"]
    description: str
    expires_at: str
    status: Literal["approved", "denied"]  # 07 §6.2 확정 (DN-014)
    decided_by: str
    risk_level: Literal["P0", "P1", "P2"] | None = None
    cost_snapshot: dict[str, Any] | None = None
    policy_snapshot: dict[str, Any] | None = None
    audit_trace_id: str | None = None


class CostBudget(VamosModel):
    """비용 예산 — D2.1-D7 §4.3 (9필드, 6+3)."""

    budget_id: str
    mode: Literal["V1", "V2", "V3"]
    daily_limit: int  # V1=1300 (07 §4.1 LOCK)
    monthly_limit: int  # V1=40000 (07 §4.1 LOCK)
    used_today: int
    used_month: int
    forecast: float | None = None
    actual: float | None = None
    block_on_exceed: bool | None = None


class DownshiftSchema(VamosModel):
    """다운시프트 정책 — D2.1-D7 §4.4 (6필드). LOCK: 80% 경고 / 100% 차단."""

    warn_threshold_percent: int  # LOCK: 80 (07 §4.2)
    block_threshold_percent: int  # LOCK: 100 (07 §4.2)
    trigger_type: Literal["daily", "monthly"]
    near_action: Literal["warn", "force_mini"]
    exceed_action: Literal["block"]
    main_requires_approval: bool


class GuardrailsCheck(VamosModel):
    """Guardrails 통합 판정 — D2.1-D7 §4.5 (7필드, 6+1)."""

    check_id: str
    trace_id: str
    layer1_nemo: dict[str, Any]
    layer2_guardrails_ai: dict[str, Any]
    layer3_llamaguard: dict[str, Any]
    overall_decision: Literal["allow", "restrict", "deny"]
    blocked_by: Literal["layer1", "layer2", "layer3"] | None = None


class RBACRole(VamosModel):
    """RBAC 역할 — D2.1-D7 §4.6 (6필드, 5+1)."""

    role: Literal["OWNER", "ADMIN", "OPERATOR", "VIEWER"]
    permissions: list[str]
    description: str
    max_autonomy_level: Literal["L0", "L1", "L2", "L3"]
    p2_access: bool
    cost_approval_limit: int | None = None


class AutonomyLevelSchema(VamosModel):
    """자율 수준 — D2.1-D7 §4.7 (7필드, 6+1)."""

    level: Literal["L0", "L1", "L2", "L3"]
    name: str
    description: str
    auto_execute: bool
    notification_required: bool
    approval_required: bool
    allowed_domains: list[str] | None = None


# ── BLUE NODES (D2.1-D3) ────────────────────────────────────────────────────


class NodeCapabilityProfile(VamosModel):
    """노드 능력 프로파일 — D2.1-D3 §5.1 (6필드, 5+1)."""

    node_id: str
    required_tools: list[str]
    risk_class: Literal["low", "med", "high"]
    cost_class: Literal["v0", "v1", "v2", "v3"]
    required_gates: list[Literal["policy", "cost", "approval", "evidence", "self_check"]]
    optional_tools: list[str] | None = None


class NodeRequestEnvelope(VamosModel):
    """CORE→NODE 요청 봉투 — D2.1-D3 §5.2 (12필드, 7+5)."""

    request_id: str
    project_id: str
    session_id: str
    node_id: str
    intent_summary: str
    constraints: dict[str, Any]
    trace_id: str
    policy_snapshot_id: str | None = None
    budget_snapshot_id: str | None = None
    evidence_refs: list[str] | None = None
    decision_id: str | None = None
    ui_hints: dict[str, Any] | None = None


class NodeResponseEnvelope(VamosModel):
    """NODE→CORE 응답 봉투 — D2.1-D3 §5.3 (6필드)."""

    trace_id: str
    node_id: str
    domain: str
    inputs: dict[str, Any]  # inputs.summary 포함
    outputs: dict[str, Any]  # outputs.result + outputs.evidence_refs
    status: Literal["success", "fail"]


class ToolCallRegistry(VamosModel):
    """노드별 도구 호출 등록 — D2.1-D3 §5.4 (7필드, 5+2)."""

    tool_id: str
    node_id: str
    risk_class: Literal["low", "med", "high"]
    auth_method: Literal["none", "api_key", "oauth2", "mcp_token"]
    enabled: bool
    mcp_endpoint: str | None = None  # MCP Streamable HTTP (DEC-017 LOCK)
    rate_limit: dict[str, Any] | None = None


class MCPBridgeLayer(VamosModel):
    """MCP 브릿지 계층 — D2.1-D3 §5.5 (7필드, 4+3)."""

    bridge_id: str
    node_id: str
    transport: Literal["streamable_http"]  # DEC-017 LOCK — stdio 제거
    base_url: str
    discovered_tools: list[str] | None = None
    auth_config: dict[str, Any] | None = None
    health_check_interval_sec: int | None = None


# ── INFRA CORE (D2.1-D4) ────────────────────────────────────────────────────


class ToolRegistryEntry(VamosModel):
    """도구 레지스트리 항목 — D2.1-D4 §4.1 (8필드, 6+2)."""

    tool_id: str
    category: str  # llm.text|llm.vision|llm.embedding|browser.render|api.http|... (확장 가능)
    adapter_id: str
    risk_class: Literal["low", "med", "high"]
    cost_class: Literal["v0", "v1", "v2", "v3"]
    required_gates: list[Literal["policy", "cost", "approval", "evidence", "self_check"]]
    outputs: list[Literal["signal", "artifact", "memory", "log"]] | None = None
    notes: str | None = None


class BrainAdapterResponse(VamosModel):
    """Brain Adapter 응답 — D2.1-D4 §4.2 (7필드, 5+2)."""

    output_text: str
    evidence_summary: str
    cost_used_estimate: dict[str, Any]
    warnings: list[str]
    trace_id: str
    tool_calls: list[dict[str, Any]] | None = None
    qod_hint: dict[str, Any] | None = None


# ── AGENT WORKFLOW (D2.1-D5) ────────────────────────────────────────────────


class WorkflowStage(VamosModel):
    """워크플로우 스테이지 — D2.1-D5 §4.4 (4필드 LOCK, 3+1)."""

    stage_id: Literal["intake", "plan", "execute", "verify", "deliver"]
    stage_name: str
    description: str
    sub_stages: list[Any] | None = None


class WorkflowOutput(VamosModel):
    """워크플로우 최종 산출 — D2.1-D5 §4.1 (3필드 LOCK)."""

    user_response: str
    evidence_summary: str
    log_report: dict[str, Any]  # trace_id + 저장/승인 이벤트 포함


class FailureReport(VamosModel):
    """실패 보고 — D2.1-D5 §4.2 (4필드)."""

    failure_cause: str
    evidence_gap: str
    risk_detected: dict[str, Any]
    improvement_hint: str


#: V0 25개 모델 전수 (PART2 V0-STEP-2 분모 — generate_types.py 입력)
ALL_MODELS: tuple[type[VamosModel], ...] = (
    IntentFrame,
    EvidencePack,
    DecisionSchema,
    LogEventSchema,
    ResponseEnvelope,
    StructuredOutput,
    MemoryRecord,
    SourceQoD,
    PolicyCheck,
    ApprovalSchema,
    CostBudget,
    DownshiftSchema,
    NodeCapabilityProfile,
    NodeRequestEnvelope,
    NodeResponseEnvelope,
    ToolCallRegistry,
    MCPBridgeLayer,
    ToolRegistryEntry,
    BrainAdapterResponse,
    WorkflowStage,
    WorkflowOutput,
    FailureReport,
    GuardrailsCheck,
    RBACRole,
    AutonomyLevelSchema,
)
