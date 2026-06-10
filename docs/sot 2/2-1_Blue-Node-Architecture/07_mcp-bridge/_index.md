# 07. MCP-Blue Node Bridge (K-010)

> **버전**: v2.1
> **Status**: LOCKED (Phase 4 2026-05-31, was REVIEW — 18-file LOCKED inventory)
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-04-08 (v2.1: 미세 재검증 패스 — 자세한 변경은 §17.4) / Phase 4 LOCKED 2026-05-31
> **정본 소유 개념**: MCPBridgeLayer 스키마(LOCK-BN-11), MCPBlueNodeServer(BN capabilities → MCP tools 변환), MCPToolRegistry(Lifecycle 연계 자동 등록/해제), MCPAuthGateway(API key + Permission Level 매핑), 6개 MCP 프로토콜 지원 범위 + sampling 미지원, P2 Approval Timeout 흐름(LOCK-BN-19). **Permission Level 0~5 정본은 01**, **Lifecycle FSM 정본은 04**, **ApprovalManager 정본은 D2.0-07 §4.3.2/S7E-050**. 본 문서는 외부 MCP 클라이언트 ↔ Blue Node 경계의 **bridge 계층** 만 정본화한다.
> **기술스택 의존성**: SPEC §14 범위 내 (Streamable HTTP, JSON-RPC 2.0)
> **SOT 근거**: D2.0-03 §6.4 (MCP 표준 채택 LOCK), §6.4.2 (서버 카탈로그), §6.5 (Claude Tool Use + Bridge Layer), §6.6 (Realtime/외부 인터페이스), §6.7 (SDK 통합/인증/캐시/에러); D2.1-D3 §5.5 MCPBridgeLayerSchema (DEC-017 LOCK), AC-D3-008; D2.0-07 §4.3.2 + §15.11 S7E-050 (LOCK-BN-19 Approval Timeout)
> **GAP 해결**: GAP-BN-07 (CRITICAL)
> **L3 달성**: E1~E9 전항목 충족

---

## LOCK 인용

> LOCK (D2.1-D3 §5.5 MCPBridgeLayerSchema — DEC-017, AC-D3-008): `transport`는 enum **`"streamable_http"`** 만 허용한다. stdio/SSE 전송은 deprecated 이며 본 도메인에서는 구현 금지.

> LOCK (D2.0-03 §6.4.1 — LOCK-BN-11): VAMOS는 MCP를 외부 도구 연결의 **단일 표준**으로 확정한다. 모든 BN의 외부 노출/소비는 예외 없이 본 Bridge 계층 → 04 ToolRegistry → 07 Gate 경로를 따른다. LangChain Tool/CrewAI Tools/직접 API 연동 금지.

> LOCK (D2.0-07 §4.3.2 / §15.11 S7E-050 — LOCK-BN-19): P2 승인 타임아웃은 **일반 10분 / P2(HITL) 5분** 이며 만료 시 Auto deny + 작업 취소 + 세션 P2 비활성화. MCP `tools/call` 이 P2 권한이 필요한 high-risk 도구를 호출한 경우 본 타임아웃을 그대로 상속한다.

> LOCK (D2.0-05 §7.3 고정 1 — LOCK-BN-10): 모든 외부 MCP 호출은 **07 Gate 경유 의무**. AuthGateway 통과 후에도 `tools/call` 의 실제 실행은 07 Gate(PolicyCheck → CostCheck → Approval) 를 거쳐야 하며 Bridge 가 직접 BN 을 호출할 수 없다.

---

## 1. 개요

Blue Node 의 capabilities/memory/template 를 MCP (Model Context Protocol) 서버로 노출하여 외부 클라이언트(Claude Desktop, Cursor, 3rd-party agent 등)가 Blue Node 를 표준화된 도구로 사용할 수 있게 하는 **Bridge 계층** 을 정의한다.

본 문서는 다음을 정본으로 보유한다:

1. **MCPBridgeLayer 스키마** — DEC-017 / AC-D3-008 LOCK 준수, Pydantic/dataclass 모델 (§3, E1)
2. **MCPBlueNodeServer** — `NodeCapability → MCPTool` / `SharedMemoryKey → MCPResource` / `TemplateSet → MCPPrompt` 변환 규칙 (§4)
3. **MCPToolRegistry** — Lifecycle FSM `ACTIVE/TERMINATED` 이벤트 구독을 통한 자동 등록/해제 (§5, atomic swap)
4. **MCPAuthGateway** — API Key/OAuth2/MCP Token 인증 + 클라이언트 tier → Permission Level 매핑 + Rate Limiting (§6)
5. **6개 MCP 프로토콜 지원 범위** + **sampling 미지원** 정책 (§7)
6. **P2 Approval Timeout 적용 시퀀스** — LOCK-BN-19 통합 (§8)
7. **에러 코드 + 감사 로그 + 단위 테스트 + 성능 기준 + Phase 매핑** (§10~§14)

> **소유 경계**:
> - **Permission Level 0~5 매트릭스 정본**은 `01_permission-matrix/_index.md`. 본 문서는 클라이언트 tier → Level 매핑만 정본화하며 Level 의미·resource_type 별 기본 Level·Dynamic Adjuster 는 01 에 위임한다.
> - **Lifecycle FSM (8-State) 정본**은 `04_node-lifecycle/_index.md`. 본 문서는 04 §9 LogEvent 의 단일 `bn.lifecycle.state_changed` 이벤트 **구독자** 이며 `to` 필드 분기로 등록/해제만 수행 — 상태 전이 자체는 정의하지 않는다.
> - **ApprovalManager / Approval Timeout 정본**은 D2.0-07 §4.3.2/S7E-050. 본 문서는 LOCK-BN-19 값을 인용·전파만 한다.
> - **NodeRequestEnvelope / NodeResponseEnvelope 정본**은 `02_core-node-interface/_index.md`. Bridge 는 변환 규칙(§4.3)만 정의한다. 7 필수 필드 = `request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id` (LOCK-BN-03 / AC-D3-004).
> - **Guardrail 카탈로그**는 `03_template-injection/_index.md` **§4 (Guardrail 체계)** — 11종(GR_NO_PII/GR_NO_SECRETS/GR_NO_BYPASS_GATE/GR_RESPECT_K048/GR_REQUIRE_CITATION/GR_SOURCE_QUALITY_MIN/GR_NO_HALLUCINATED_URL/GR_NO_EXEC_UNTRUSTED/GR_DEPENDENCY_WHITELIST/GR_TEST_REQUIRED/GR_NO_HARDCODED_SECRET). `prompts/get` 노출 시 guardrail 적용은 03 의 정본을 호출한다.

---

## 2. 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│  External MCP Client (Claude Desktop / Cursor / Agent SDK)   │
└────────────────────┬─────────────────────────────────────────┘
                     │ MCP Protocol (JSON-RPC 2.0 over Streamable HTTP)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                MCP-Blue Node Bridge (본 문서)                │
│                                                              │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ AuthGateway  │  │ ToolRegistry    │  │ RateLimiter    │   │
│  │  (§6)        │  │  (§5, atomic)   │  │  (§6.3)        │   │
│  └──────┬───────┘  └────────┬────────┘  └────────────────┘   │
│         │                   │                                │
│  ┌──────▼───────────────────▼────────────────────────────┐   │
│  │ Request Translator                                     │   │
│  │   MCP request → NodeRequestEnvelope (02 §2.1, §4.3)    │   │
│  │   MCP request → VamosMessage (02 §1.1, K-049)          │   │
│  └────────────────────┬───────────────────────────────────┘   │
└───────────────────────┼──────────────────────────────────────┘
                        │ NodeRequestEnvelope (D2.1-D3 AC-D3-004)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                       07 Gate (LOCK-BN-10)                   │
│        PolicyCheck → CostCheck → Approval (LOCK-BN-19)       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│         Blue Node Pool (Lifecycle FSM, 정본=04)              │
│  BN-WebResearch │ BN-Code │ BN-PKM │ BN-Trading │ ...        │
└──────────────────────────────────────────────────────────────┘
        ▲                            ▲
        │ bn.lifecycle.state_changed  │  (정본 04 §9, payload: from/to/trigger)
        └────────────────────────────┴── ToolRegistry 구독 (§5.1):
              to == ACTIVE → 등록  /  to in {DRAINING, TERMINATED} → 해제
```

---

## 3. 데이터 모델 (E1)

> Pydantic v1 호환. forward ref 회피를 위해 선언 순서 유지.

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Any
from enum import Enum
from uuid import uuid4


# ─── 3.1 Transport / Schema (LOCK-BN-11, AC-D3-008) ───────────────────────

TransportType = Literal["streamable_http"]   # LOCK: 단일 enum (DEC-017)


class AuthConfig(BaseModel):
    """MCPBridgeLayer.auth_config (D2.1-D3 §5.5)."""
    type: Literal["bearer", "api_key", "oauth2", "mcp_token"]
    token_env: Optional[str] = None        # 환경변수명 (예: VAMOS_MCP_KEY_RESEARCH)
    scopes: list[str] = Field(default_factory=list)


class MCPBridgeLayer(BaseModel):
    """MCPBridgeLayerSchema 정본 (D2.1-D3 §5.5, DEC-017 LOCK).

    AC-D3-008: transport 는 'streamable_http' 만 허용된다.
    """
    bridge_id: str                          # 브릿지 고유 ID
    node_id: str                            # 연결된 Blue Node ID
    transport: TransportType                # LOCK: streamable_http only
    base_url: str                           # MCP 서버 기본 URL (HTTPS 권장)
    discovered_tools: Optional[list[str]] = None
    auth_config: Optional[AuthConfig] = None
    health_check_interval_sec: int = 30

    @validator("transport")
    def _enforce_streamable_http(cls, v):
        # AC-D3-008 가드: 다른 값 입력 시 즉시 거부
        if v != "streamable_http":
            raise ValueError(
                f"AC-D3-008 LOCK: transport must be 'streamable_http' (got {v!r})"
            )
        return v

    @validator("base_url")
    def _require_url_scheme(cls, v, values):
        # TLS 1.3 강제 (§12.2): 기본은 https 만 허용.
        # http 는 allow_insecure_http=True AND 비-production 환경에서만 허용 (dev/test 호환).
        if v.startswith("https://"):
            return v
        if v.startswith("http://"):
            import os
            allow_insecure = values.get("allow_insecure_http", False)
            is_prod = os.getenv("VAMOS_ENV", "production") == "production"
            if allow_insecure and not is_prod:
                return v
            raise ValueError("base_url: production 에서는 https:// 필수 (TLS 1.3, §12.2). http 는 allow_insecure_http=True + 비-production 에서만 허용")
        raise ValueError("base_url must include scheme (https:// — 또는 dev/test 한정 http://)")


# ─── 3.2 MCP 요청/응답 (JSON-RPC 2.0) ─────────────────────────────────────

class MCPRequest(BaseModel):
    """JSON-RPC 2.0 형식의 MCP 요청.

    method 는 6개 지원 메서드만 enum 으로 허용 (§7.1). 미지원 메서드(`sampling/*` 등)
    호출 시 Pydantic ValidationError 가 발생하며, Bridge 의 디스패처가 이를
    catch 하여 JSON-RPC 표준 -32601 (Method not found) + `bridge.sampling.blocked`
    감사 이벤트로 변환한다 (§7.2 / §10 / TC-MB-16).
    """
    jsonrpc: Literal["2.0"] = "2.0"
    id: str = Field(default_factory=lambda: str(uuid4()))
    method: Literal[
        "tools/list", "tools/call",
        "resources/list", "resources/read",
        "prompts/list", "prompts/get",
    ]
    params: dict = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)   # Bearer/API key 전달


class MCPResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: Optional[Any] = None
    error: Optional[dict] = None            # {"code": int, "message": str, "data": ...}


# ─── 3.3 도구 / 리소스 / 프롬프트 디스크립터 ─────────────────────────────

class MCPTool(BaseModel):
    name: str                               # "{node_id}__{capability_name}"
    description: str
    input_schema: dict                      # JSON Schema (capability.input_schema)
    risk_class: Literal["low", "med", "high"]
    cost_class: Literal["v0", "v1", "v2", "v3"]
    required_permission_level: int = Field(ge=0, le=5)   # 01 정본 참조


class MCPResource(BaseModel):
    uri: str                                # "memory://{node_id}/{key}"
    name: str
    mime_type: str = "application/json"
    required_permission_level: int = Field(ge=0, le=5)


class MCPPrompt(BaseModel):
    name: str                               # "{node_id}.template_set.{ts_id}"
    description: str
    arguments: list[dict] = Field(default_factory=list)


# ─── 3.4 인증 / Rate Limit ────────────────────────────────────────────────

class ClientTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class MCPClient(BaseModel):
    client_id: str
    api_key_hash: str                       # bcrypt/argon2 hash, 평문 저장 금지
    tier: ClientTier
    enabled: bool = True                    # §6.1 단계 3 가드 (CLIENT_DISABLED)
    allowed_node_ids: Optional[list[str]] = None      # None = 모든 활성 노드
    allowed_tool_patterns: list[str] = Field(default_factory=list)


class AuthResult(BaseModel):
    """외부 MCP 클라이언트 인증 결과.

    LOCK: permission_level 은 0~4 만 허용. Level 5 (`FINANCIAL` — 01 §1
    PermissionLevel enum 값 5, "항상 사용자 확인 필수", LOCK-BN-02) 는 외부
    클라이언트에 절대 매핑 금지 (§6.2 LOCK + TC-MB-06).
    """
    authenticated: bool
    authorized: bool = False
    permission_level: int = Field(0, ge=0, le=4)   # 0 = REJECTED, 4 = ENTERPRISE 상한
    client_id: Optional[str] = None
    reason: Optional[str] = None            # 거부 사유 (구조적 enum 권장)


class RateLimitConfig(BaseModel):
    rpm: int                                # requests per minute
    daily: int                              # daily cap, -1 = unlimited
```

> 모델 선언 순서 = forward ref 자체 회피. v2 migration 시 `Any` → `JsonValue` 고려 가능.

---

## 4. MCPBlueNodeServer — 변환 규칙

### 4.1 자동 변환 매핑

| Blue Node 구성 | MCP 노출 | MCP 메서드 | 정본 |
|---|---|---|---|
| `NodeCapability` (도구) | `MCPTool` | `tools/list`, `tools/call` | 02 NodeCapabilityProfile |
| `SharedMemory` 키 | `MCPResource` | `resources/list`, `resources/read` | 05 SHARED 타입 |
| `TemplateSet` (TS_*) | `MCPPrompt` | `prompts/list`, `prompts/get` (guardrail 적용) | 03 §2 (Template Set 정의) + §4 (Guardrail) |
| LLM `sampling` | **미지원** | — | §7.2 정책 |

### 4.2 capability → MCPTool 변환 예시

```json
// Blue Node 측 NodeCapability (정본 02)
{
  "node_id": "bn_web_research",
  "name": "web_search",
  "description": "Execute web search via Tavily/SerpAPI",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "max_results": {"type": "integer", "default": 10}
    },
    "required": ["query"]
  },
  "risk_class": "med",
  "cost_class": "v1",
  "required_permission_level": 2
}
```

```json
// → Bridge 가 노출하는 MCPTool
{
  "name": "bn_web_research__web_search",
  "description": "Execute web search via Tavily/SerpAPI (BN: bn_web_research)",
  "input_schema": { /* 동일 (per-tool 추가 변형 금지) */ },
  "risk_class": "med",
  "cost_class": "v1",
  "required_permission_level": 2
}
```

규칙:
- `MCPTool.name` = `{node_id}__{capability.name}` (구분자 `__`, 충돌 방지)
- `input_schema` 는 **그대로 전달** (변형 금지 — 02 정본 일관성 유지)
- `required_permission_level` 은 01 의 resource_type 매트릭스 결과를 그대로 인용

### 4.3 MCP `tools/call` → NodeRequestEnvelope 변환

> **정본 위임**: NodeRequestEnvelope / VamosMessage 구조는 02 §1~§2 정본을 따른다. 본 절은 **변환 로직만** 정의한다.
> **LOCK-BN-03 (AC-D3-004) 7 필수 필드**: `request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id` — 02 §2.1 / §2.2 정본 (CF-007 해소). `conversation_turn / task_type / task_params / user_intent / relevant_memory / template_set_id / message` 등 상세명세 L2 필드는 02 에서 **삭제됨** — `intent_summary` 로 통합되거나 `constraints` 내부로 재분류된다.

```python
# 02 정본에서 import (sketch — 실제 모듈 경로는 02 와 정합)
from vamos.bn.interface import (
    NodeRequestEnvelope, VamosMessage,
    VamosMessageSource, VamosMessageTarget,
    VamosMessageContent, VamosMessageMetadata,
)


def mcp_call_to_envelope(
    req: MCPRequest,
    auth: AuthResult,
    project_id: str,
    session_id: str,
    trace_id: str,
) -> tuple[NodeRequestEnvelope, VamosMessage]:
    """MCP 'tools/call' 요청을 02 정본 NodeRequestEnvelope + VamosMessage 로 변환.

    호출 측 책임:
      - project_id / session_id / trace_id 는 인증 컨텍스트(MCP Bridge 세션)에서
        주입한다. uuid4() 즉석 생성은 trace 단절을 유발하므로 금지.
      - registry 가 capability 메타(`risk_class`/`cost_class`/`required_permission_level`)
        를 조회하여 §6.1 단계 6 검증을 선행한 뒤 본 함수를 호출한다.

    반환:
      (envelope, vmsg) — Bridge → 07 Gate 호출 시 두 객체를 한 쌍으로 전달.
      VamosMessage 는 NodeRequestEnvelope 의 필드가 아님 (02 §1.1 / §2.1 교정 사항):
      에이전트 간 메시지 표준 포맷(K-049)과 NODE 실행 계약(AC-D3-004)은 분리된
      레이어이며 trace_id 로 연결된다 (02 §4.2).
    """
    tool_full = req.params["name"]               # "bn_web_research__web_search"
    node_id, cap_name = tool_full.split("__", 1)
    arguments = req.params.get("arguments", {}) or {}

    # 1) NodeRequestEnvelope (LOCK-BN-03, AC-D3-004 — 7 필수 필드)
    envelope = NodeRequestEnvelope(
        request_id=req.id,                       # MCP request id 재사용 (멱등 키)
        project_id=project_id,                   # Bridge 세션 컨텍스트 주입
        session_id=session_id,                   # 동일
        node_id=node_id,                         # tool name 파싱 결과
        intent_summary=(f"mcp.{cap_name}: {repr(arguments)}")[:120],  # 의도 요약 (≤120자)
        constraints={                            # 내부 구조 미확정 (CF-006), 참고 키만 채움
            "mcp_arguments": arguments,          # 원본 인수 (07 Gate PolicyCheck 입력)
            "mcp_tool_full_name": tool_full,
            "mcp_client_id": auth.client_id or "anonymous",  # tier 는 별도 채널 전달
        },
        trace_id=trace_id,                       # VamosMessage.metadata.trace_id 와 동일
        # 선택 5종은 07 Gate 가 채움 (policy_snapshot_id / budget_snapshot_id /
        # evidence_refs / decision_id / ui_hints) — Bridge 는 채우지 않는다.
    )

    # 2) VamosMessage (LOCK-BN-16, K-049 — 6 top-level 필수)
    vmsg = VamosMessage(
        # id, type 은 K-049 정본 (id=UUID 자동, type=request)
        type="request",
        source=VamosMessageSource(
            agent_id=f"mcp-bridge:{auth.client_id}",
            node_type="mcp_bridge",
        ),
        target=VamosMessageTarget(
            agent_id=node_id,
            node_type="blue_node",
        ),
        content=VamosMessageContent(
            text=None,
            data=arguments,
            artifacts=None,
        ),
        metadata=VamosMessageMetadata(
            priority=3,                          # 1~5 (K-049: int, 3=normal)
            cost=0.0,                            # 07 Gate CostCheck 가 갱신
            confidence=0.0,
            trace_id=trace_id,                   # envelope.trace_id 와 동일 (02 §4.2)
        ),
    )

    return envelope, vmsg
```

> **주의** (02 §1.1 교정 사항): VamosMessage 에는 `auth_token` / `permission_level` / `signature` / `destination` / `payload` / `message_type` 필드가 **없다**. 인증·권한은 본 Bridge 의 AuthGateway(§6) 와 ORANGE CORE Policy Engine 이 처리하며, K-049 정본 6 필드(`id, type, source, target, content, metadata`) 외에는 추가하지 않는다.

### 4.4 응답 변환 (NodeResponseEnvelope → MCPResponse)

`outputs.result` 를 `MCPResponse.result` 로, `outputs.evidence_refs` 는 `result._evidence_refs` 로 보존(평탄화 금지). `failure_code` 가 있으면 `MCPResponse.error` 로 매핑하며, JSON-RPC 표준 코드 외에는 `data.failure_code` 로 확장한다.

| failure_code (02 §6.1~6.3 UPPER_SNAKE) | MCP error.code | 의미 |
|---|---|---|
| `POLICY_DENIED` | -32001 | 07 Gate PolicyCheck 거부 |
| `APPROVAL_TIMEOUT` (LOCK-BN-19) | -32002 | P2 승인 타임아웃 → Auto deny |
| `RATE_LIMIT_EXCEEDED` | -32003 | RateLimiter 차단 |
| `TOOL_NOT_FOUND` | -32601 | JSON-RPC 표준 (Method not found 변형) |
| `INVALID_PARAMS` | -32602 | JSON-RPC 표준 |
| 기타 | -32000 | Server error (`data.failure_code` 보존) |

---

## 5. MCPToolRegistry — Lifecycle 연계 자동 등록/해제

### 5.1 이벤트 구독 모델 (정본 04 §9 LogEvent 의존)

> **정본 위임**: 04 §9 LogEvent 이벤트 기록 명세 정본은 단일 이벤트 `bn.lifecycle.state_changed` (payload: `node_id, from, to, trigger`) 만 발행한다. Bridge 는 별도 `activated`/`terminated` 이벤트를 정의하지 않고 `to` 필드로 분기한다 (04 §9 정본 + 02 §6.1 LogEvent Registry REF 규칙 — D2.1-D3 AC-D3-003).

| 구독 이벤트 (정본 04 §9) | 트리거 조건 | Bridge 동작 | 원자성 |
|---|---|---|---|
| `bn.lifecycle.state_changed` | `to == "ACTIVE"` (T7/T9 등) | 해당 노드의 capabilities/memory/template → MCPTool/Resource/Prompt 등록 | 단일 트랜잭션, 부분 등록 시 전체 롤백 |
| `bn.lifecycle.state_changed` | `to in {"DRAINING", "TERMINATED"}` | 디스크립터 일괄 해제 + 진행 중 호출 graceful drain | 해제 후 `notifications/tools/list_changed` 전송 |
| `bn.lifecycle.state_changed` | 동일 노드 내 capability 메타 변경 (재활성화) | 기존 해제 → 신규 등록 (atomic swap) | 두 단계 사이에 외부 호출 불가 (lock) |

```python
import asyncio


class MCPToolRegistry:
    """Blue Node lifecycle 이벤트 구독 + atomic swap.

    NodeHandle / BridgeRegistrationError 는 02 / 본 모듈에서 import. 본 코드 블록은
    spec sketch 이며 실제 모듈 경로는 구현 단계에서 확정한다.
    """

    def __init__(self):
        self._tools: dict[str, MCPTool] = {}
        self._resources: dict[str, MCPResource] = {}
        self._prompts: dict[str, MCPPrompt] = {}
        self._node_index: dict[str, dict[str, list[str]]] = {}  # node → {tools, resources, prompts}
        self._lock = asyncio.Lock()

    async def on_state_changed(self, payload: dict):
        """04 §9 `bn.lifecycle.state_changed` 단일 진입점.

        payload = {"node_id": ..., "from": ..., "to": ..., "trigger": ...}
        """
        node_id = payload["node_id"]
        to_state = payload["to"]
        if to_state == "ACTIVE":
            await self._on_activated(node_id)
        elif to_state in {"DRAINING", "TERMINATED"}:
            await self._on_terminated(node_id)
        # 그 외 상태 (CANDIDATE/LAZY/ACTIVATING/BUSY/SUSPENDED) 는 무시

    async def _on_activated(self, node_id: str):
        async with self._lock:
            tools, resources, prompts = await self._collect(node_id)
            try:
                self._apply(node_id, tools, resources, prompts)
            except Exception as e:
                self._rollback(node_id)              # 부분 등록 롤백
                raise BridgeRegistrationError(e)
        await self._notify("tools/list_changed")

    async def _on_terminated(self, node_id: str):
        async with self._lock:
            await self._drain_in_flight(node_id)     # graceful, max 30s
            self._rollback(node_id)
        await self._notify("tools/list_changed")
```

### 5.2 디스커버리

- `tools/list` 응답에 `risk_class`, `cost_class`, `required_permission_level` 메타 포함
- 클라이언트가 fuzzy 검색 시 이름·설명 기반 매칭, 단 결과는 `auth.permission_level` 로 사전 필터링
- 구독자(Realtime API §6.6) 에게 `notifications/tools/list_changed` 전송

---

## 6. MCPAuthGateway

### 6.1 인증 단계

| # | 단계 | 실패 시 reason |
|---|---|---|
| 1 | API Key/Bearer 헤더 추출 (`x-api-key` 또는 `Authorization: Bearer ...`) | `AUTH_HEADER_MISSING` |
| 2 | 해시 비교 (bcrypt/argon2, 평문 저장 금지) | `AUTH_KEY_INVALID` |
| 3 | 클라이언트 활성 여부 확인 (`enabled = true`) | `CLIENT_DISABLED` |
| 4 | 클라이언트 tier → Permission Level 매핑 (§6.2) | — |
| 5 | Rate Limit 확인 (§6.3) | `RATE_LIMIT_EXCEEDED` |
| 6 | tool/resource 별 `required_permission_level ≤ auth.permission_level` 검증 | `INSUFFICIENT_LEVEL` |
| 7 | 07 Gate 호출 위임 (LOCK-BN-10) | (Gate 결과 그대로 전파) |

> 인증 통과 ≠ 실행 허가. 모든 `tools/call` 은 §8 의 07 Gate 흐름을 거친다.

### 6.2 클라이언트 tier → Permission Level 매핑

| Client Tier | Permission Level | 01 매트릭스 의미 (정본 위임) |
|---|:---:|---|
| `free` | 1 | CREATE (생성) |
| `basic` | 2 | MODIFY (수정) |
| `premium` | 3 | EXECUTE (실행) |
| `enterprise` | 4 | EXTERNAL (외부통신) |
| **(미지원)** | 5 | FINANCIAL (금융 — 01 §1 PermissionLevel.FINANCIAL = 5) — 외부 클라이언트는 절대 도달 불가 (LOCK) |

> Level 5 (`FINANCIAL` — 01 정본 PermissionLevel enum 값 5, "항상 사용자 확인 필수", LOCK-BN-02)는 **외부 MCP 클라이언트에 매핑 금지**. enterprise 도 4 가 상한이며, Level 5 도구는 `tools/list` 에서 사전 필터링되어 노출되지 않는다. 시도 시 `INSUFFICIENT_LEVEL` 즉시 거부 + `bridge.auth.level5_blocked` 감사 이벤트 emit. (관련: 01 의 `FINANCIAL_CONFIRMATION_TIMEOUT` failure_code 와 LOCK-BN-19 P2 HITL 5분 매핑)

### 6.3 Rate Limiting

```yaml
rate_limits:
  free:       { rpm: 10,   daily: 100 }
  basic:      { rpm: 60,   daily: 1000 }
  premium:    { rpm: 300,  daily: 10000 }
  enterprise: { rpm: 1000, daily: -1 }       # -1 = unlimited
```

- 키: `(client_id, minute_bucket)` / `(client_id, day_bucket)` Redis counter
- 차단 시 `RateLimitInfo` 헤더 반환 (`x-ratelimit-remaining`, `x-ratelimit-reset`)
- 캐시 hit (risk_class=low) 응답은 카운터 차감하지 않음 (정본 D2.0-03 §6.7.3)

---

## 7. 6개 MCP 프로토콜 지원 + sampling 미지원

### 7.1 지원 프로토콜 매트릭스

| MCP 메서드 | 지원 | 매핑 대상 | 권한 검증 |
|---|:---:|---|---|
| `tools/list` | ✅ | 등록된 `MCPTool` (auth.permission_level 사전 필터) | 6.1 단계 4 + 6 사전 필터 |
| `tools/call` | ✅ | `mcp_call_to_envelope()` → 07 Gate → BN execute → MCPResponse 변환 (§4.3) | 6.1 + 07 Gate + LOCK-BN-19 (§8) |
| `resources/list` | ✅ | 등록된 `MCPResource` (SHARED 키만, 05 정본 위임) | required_permission_level 비교 |
| `resources/read` | ✅ | `MemoryReadRequest` (05 **§4.2** CORE-mediated MemoryBroker 경유) | 05 ACL + 01 매트릭스 |
| `prompts/list` | ✅ | 등록된 `MCPPrompt` (TS_*) | 1 이상 |
| `prompts/get` | ✅ | TemplateSet 본문 (03 §4 Guardrail 체계 적용 후 반환) | 1 이상, guardrail 11종 강제 |
| `sampling/createMessage` (외) | ❌ | — (Pydantic enum 차단 → -32601 + `bridge.sampling.blocked`) | (§7.2) |

### 7.2 sampling 미지원 정책 + 향후 확장 조건

- **미지원 사유** (보안):
  1. 외부 MCP 서버가 VAMOS 의 LLM 자원을 임의 호출하면 비용/할당량 정책(D2.0-07 CostCheck)을 우회할 수 있음
  2. sampling 결과의 출처가 외부 서버이므로 evidence/audit 사슬이 끊김 (07 Gate Evidence 계층 위반)
  3. prompt injection 공격면 확대 — 외부 서버가 사용자 LLM context 에 직접 영향
- **확장 조건** (V3+ 검토 대상, 모두 충족 시에만 활성화):
  1. 07 Gate 가 sampling 요청을 별도 PolicyCheck 단계로 검증할 수 있는 schema 정의 완료
  2. CostCheck 가 sampling 토큰을 클라이언트 tier 별 일별 cap 으로 제한 가능
  3. Evidence chain 에 `sampling.requester` / `sampling.intent` 필드 추가 + audit 로그 보존
  4. `sampling/createMessage` 가 P2 권한으로 분류되며 LOCK-BN-19 타임아웃 적용

---

## 8. P2 Approval Timeout 적용 시퀀스 (LOCK-BN-19)

> LOCK (D2.0-07 §4.3.2 / S7E-050 — LOCK-BN-19): General 10 분 / P2(HITL) 5 분 → Auto deny + 작업 취소 + 세션 P2 비활성화.

### 8.1 high-risk `tools/call` 흐름

```
External Client                Bridge                07 Gate         BN
   │                             │                     │              │
   │── tools/call (POST) ───────▶│                     │              │
   │                             │── auth(6.1) ───────▶│              │
   │                             │                     │              │
   │                             │── translate(4.3) ──▶│              │
   │                             │                     │              │
   │                             │  PolicyCheck───────▶│              │
   │                             │  CostCheck────────▶│              │
   │                             │  Approval (P2?)────▶│              │
   │                             │     │               │              │
   │                             │     │  LOCK-BN-19   │              │
   │                             │     │  10min / 5min │              │
   │                             │     │  ApprovalManager              │
   │                             │     │               │              │
   │                             │  ◀──┘ approved      │              │
   │                             │── execute ──────────────────────▶│
   │                             │ ◀── NodeResponseEnvelope ─────────│
   │ ◀── MCPResponse ────────────│                                    │
```

### 8.2 타임아웃 분기 매핑

| 시나리오 | 타임아웃 | 결과 | MCP error.code | 후속 |
|---|:---:|---|:---:|---|
| 일반 승인 (P0/P1 경로) | **10 min** | Auto deny | -32002 | `failure_code: APPROVAL_TIMEOUT`, 세션 유지 |
| P2 HITL 승인 | **5 min** | Auto deny + 작업 취소 + **세션 P2 비활성화** | -32002 | `failure_code: APPROVAL_TIMEOUT`, `bridge.session.p2_disabled` 이벤트, 클라이언트 재요청 안내 |

> 타임아웃 시 Bridge 는 직접 타이머를 보유하지 않는다. ApprovalManager(D2.0-07 S7E-050) 가 발생시키는 `approval.timeout` 이벤트를 구독하여 위 매핑을 수행한다 (정본 위임).

### 8.3 클라이언트 안내 페이로드

```json
{
  "error": {
    "code": -32002,
    "message": "Approval timeout (LOCK-BN-19)",
    "data": {
      "failure_code": "APPROVAL_TIMEOUT",
      "timeout_seconds": 300,
      "scope": "p2_hitl",
      "session_p2_disabled": true,
      "retry_hint": "Re-request after explicit user approval (per-session re-confirm required)"
    }
  }
}
```

---

## 9. 의존성 (E3)

### 9.1 상위 (소비)

| 대상 | SOT | 사용 방식 |
|---|---|---|
| 01 Permission Matrix (K-041) | `01_permission-matrix/_index.md` v2.0 | resource_type → required_permission_level 조회, Level 5 차단 LOCK |
| 02 Interface Contract (K-049) | `02_core-node-interface/_index.md` v2.0 | NodeRequest/Response Envelope 변환 (§4.3, §4.4) |
| 03 Template Injection | `03_template-injection/_index.md` v2.0 **§2** (Template Set 정의) + **§4** (Guardrail 체계) | `prompts/list` 노출 = §2 TS_*; `prompts/get` 본문 = §2 + §4 guardrail 11종 적용 |
| 04 Lifecycle FSM | `04_node-lifecycle/_index.md` v2.0 **§9** (LogEvent 명세) | `bn.lifecycle.state_changed` 구독, `to` 분기 |
| 05 Memory Sharing | `05_memory-sharing/_index.md` v2.0 **§4.2** (CORE-mediated 시퀀스) | `resources/read` → MemoryReadRequest → MemoryBroker (LOCK-BN-14 우회 금지) |
| 06 Policy Overrides | `06_policy-overrides/_index.md` v2.1 | RateLimit/permission 파라미터 stricter override 수용 |
| 07 Gate (D2.0-07) | SOT §4.3.2/S7E-050 | LOCK-BN-10 경유 의무, LOCK-BN-19 타임아웃 |
| D2.1-D3 §5.5 | SOT | MCPBridgeLayerSchema 필드 정합 (DEC-017, AC-D3-008) |
| D2.0-03 §6.4~§6.7 | SOT | LOCK-BN-11 + 서버 카탈로그 + Tool Use + SDK 통합 |

### 9.2 하위 (제공)

| 대상 | 사용 방식 |
|---|---|
| 외부 MCP 클라이언트 (Claude Desktop, Cursor, Agent SDK) | Streamable HTTP 엔드포인트 |
| #16 MCP Server/Client (Tier 3) | 본 Bridge 의 LOCK-BN-11 전송 규칙 준수 |
| #14 Rust-Tauri (IPC) | 본 Bridge 가 노출하는 도구 카탈로그 소비 |

---

## 10. 에러 코드 (E5)

| failure_code (UPPER_SNAKE) | 발생 시점 | 복구 전략 | MCP error.code |
|---|---|---|:---:|
| `AUTH_HEADER_MISSING` | §6.1 단계 1 | 401 응답, 클라이언트 헤더 첨부 안내 | -32001 |
| `AUTH_KEY_INVALID` | §6.1 단계 2 | 401, key 재발급 안내 | -32001 |
| `CLIENT_DISABLED` | §6.1 단계 3 | 401, 운영자 문의 | -32001 |
| `RATE_LIMIT_EXCEEDED` | §6.3 | 429, `x-ratelimit-reset` 후 재시도 | -32003 |
| `INSUFFICIENT_LEVEL` | §6.1 단계 6 / §6.2 Level 5 차단 | 403, tier 업그레이드 안내 | -32001 |
| `TOOL_NOT_FOUND` | §5 종료/미등록 도구 호출 | 404, `tools/list` 재조회 안내 | -32601 |
| `INVALID_PARAMS` | §4.3 schema 검증 실패 | 400, input_schema 안내 | -32602 |
| `POLICY_DENIED` | 07 Gate PolicyCheck | Gate 응답 그대로 전파 | -32001 |
| `COST_LIMIT_EXCEEDED` | 07 Gate CostCheck | 일별 cap 안내 | -32001 |
| `APPROVAL_TIMEOUT` | LOCK-BN-19 (§8) | 세션 P2 비활성화 + 재승인 안내 | -32002 |
| `BRIDGE_REGISTRATION_FAILED` | §5 atomic 등록 실패 | 운영자 알림 + 노드 재활성화 | -32000 |
| `SAMPLING_NOT_SUPPORTED` | §7.2 sampling 차단 (Pydantic enum) | 명시적 거부 + `bridge.sampling.blocked` emit | -32601 |
| `TRANSPORT_VIOLATION` | `transport != streamable_http` | 즉시 거부 + 운영자 알림 (LOCK-BN-11/AC-D3-008) | -32000 |

---

## 11. 단위 테스트 케이스 (E4)

| ID | 시나리오 | 입력 | 기대 결과 |
|---|---|---|---|
| TC-MB-01 | LOCK-BN-11 / AC-D3-008 transport 가드 | `transport="stdio"` 로 MCPBridgeLayer 생성 시도 | Pydantic ValidationError + `TRANSPORT_VIOLATION` 감사 |
| TC-MB-02 | LOCK-BN-11 / AC-D3-008 transport 정합 | `transport="streamable_http"` | 정상 생성 |
| TC-MB-03 | 인증 헤더 누락 | `tools/list` (헤더 없음) | `AUTH_HEADER_MISSING`, error.code=-32001 |
| TC-MB-04 | API Key 위조 | 잘못된 Bearer | `AUTH_KEY_INVALID` |
| TC-MB-05 | tier → Level 매핑 | tier=premium | `permission_level=3` |
| TC-MB-06 | Level 5 차단 LOCK | enterprise 가 Level 5 도구 호출 | `INSUFFICIENT_LEVEL` + `bridge.auth.level5_blocked` |
| TC-MB-07 | Rate Limit free tier | 11번째 분당 호출 | `RATE_LIMIT_EXCEEDED` (-32003) + `x-ratelimit-reset` |
| TC-MB-08 | `tools/list` 사전 필터 | client level=2, 등록된 도구 중 level 4 도구 1건 | level 4 제외된 목록만 반환 |
| TC-MB-09 | `tools/call` → Envelope 변환 (§4.3) | name=`bn_web_research__web_search`, arguments={query}, project_id/session_id/trace_id 주입 | NodeRequestEnvelope 7 필수 필드(`request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id`) 전부 충족 + 동일 trace_id 의 VamosMessage 동시 생성, `source.agent_id="mcp-bridge:..."`, `source.node_type="mcp_bridge"` |
| TC-MB-10 | 07 Gate 경유 검증 (LOCK-BN-10) | `tools/call` mock | 07 Gate 호출 1회 (mock 검증), Gate bypass 시도 → 거부 |
| TC-MB-11 | LOCK-BN-19 일반 10분 타임아웃 | P0/P1 경로 승인 미응답 (mock 10:01) | `APPROVAL_TIMEOUT` -32002, 세션 유지 |
| TC-MB-12 | LOCK-BN-19 P2 HITL 5분 타임아웃 | P2 권한 도구 (Trading 등) 승인 미응답 (mock 5:01) | `APPROVAL_TIMEOUT` -32002, **세션 P2 비활성화**, `bridge.session.p2_disabled` emit |
| TC-MB-13 | Lifecycle ACTIVE 진입 자동 등록 | `bn.lifecycle.state_changed` payload `{from:"ACTIVATING", to:"ACTIVE"}` | `MCPToolRegistry._tools` 에 신규 등록 + `notifications/tools/list_changed` 전송 |
| TC-MB-14 | Lifecycle TERMINATED 자동 해제 | `bn.lifecycle.state_changed` payload `{from:"DRAINING", to:"TERMINATED"}` | 디스크립터 0건, in-flight 호출 graceful drain (≤30s) |
| TC-MB-14b | Lifecycle DRAINING 진입 즉시 차단 | `bn.lifecycle.state_changed` payload `{from:"ACTIVE", to:"DRAINING"}` | 신규 호출 거부 + 기존 호출만 drain |
| TC-MB-14c | 무관 상태 무시 | `to in {CANDIDATE, LAZY, ACTIVATING, BUSY, SUSPENDED}` | Registry 무변경, 이벤트 silently ignored |
| TC-MB-15 | atomic swap (capability 변경) | 기존 5도구 → 신규 6도구 로 swap | swap 도중 외부 호출 4건 모두 일관 결과 (구버전 또는 신버전 둘 중 하나, 혼합 0) |
| TC-MB-16 | sampling 미지원 정책 (Pydantic enum) | `sampling/createMessage` 호출 | Pydantic ValidationError → 디스패처 catch → -32601 `Method not found` + `SAMPLING_NOT_SUPPORTED` + `bridge.sampling.blocked` emit |
| TC-MB-17 | `prompts/get` guardrail 적용 | TS_CORE 노출 | 03 **§4** guardrail 11종 적용된 본문 반환, PII 미노출 |
| TC-MB-18 | `resources/read` CORE-mediated | SHARED 키 읽기 | 05 MemoryReadRequest 경로 호출, 직접 read 차단 |
| TC-MB-19 | failure_code → MCP error 매핑 | BN execute 결과 `failure_code=POLICY_DENIED` | error.code=-32001, data.failure_code 보존 |
| TC-MB-20 | atomic 등록 실패 롤백 | 5/6 도구 등록 후 6번째 실패 | 5 도구 모두 롤백 + `BRIDGE_REGISTRATION_FAILED` |

---

## 12. 보안 + 감사 로그 (E7)

### 12.1 감사 이벤트 카탈로그

| event_type | 발생 | 필수 필드 |
|---|---|---|
| `bridge.auth.success` | 인증 성공 | client_id, tier, permission_level |
| `bridge.auth.failed` | 인증 실패 | reason, ip, attempted_key_hash_prefix |
| `bridge.auth.level5_blocked` | Level 5 매핑 시도 | client_id, requested_tool |
| `bridge.tool.registered` | §5 등록 | node_id, tool_count |
| `bridge.tool.deregistered` | §5 해제 | node_id, tool_count |
| `bridge.call.translated` | §4.3 변환 | bridge_id, node_id, tool_name, trace_id |
| `bridge.call.gate_denied` | 07 Gate 거부 | failure_code, gate_step |
| `bridge.call.approval_timeout` | §8 LOCK-BN-19 발화 | scope (general/p2_hitl), session_id |
| `bridge.session.p2_disabled` | P2 세션 비활성화 | session_id, reason=APPROVAL_TIMEOUT |
| `bridge.sampling.blocked` | sampling 시도 차단 | client_id |
| `bridge.transport.violation` | LOCK-BN-11 위반 시도 | bridge_id, attempted_transport |

### 12.2 보안 가드

- API Key 평문 저장 금지 (bcrypt/argon2 해시만)
- 토큰 마스킹 (`***REDACTED***`) — D2.0-03 §6.7.2 정본 준수
- TLS 1.3 필수 (LOCK D2.0-03 §6.4)
- input_schema 미검증 페이로드 BN 직접 전달 금지
- 모든 호출에 trace_id 전파 (분산 추적, D2.0-03 §6.7.5)

---

## 13. 성능 기준 (E6)

| 지표 | 기준값 | 측정 방법 |
|---|---|---|
| `tools/list` 응답 p50 | < 20 ms | 캐시 hit 가정 (Redis) |
| `tools/list` 응답 p99 | < 80 ms | cache miss 포함 |
| `tools/call` 변환 (4.3) p50 | < 5 ms | Bridge 단독 (07 Gate/BN execute 제외) |
| 인증 검증 (6.1 1~3 단계) p50 | < 3 ms | bcrypt 검증 포함, key cache hit |
| 등록 swap (5.1) | < 100 ms | 도구 50개 기준 atomic swap |
| 동시 활성 클라이언트 | ≥ 100 | enterprise 5 + premium 20 + basic/free 75 |
| Throughput per Bridge | ≥ 500 req/s | LOCK-BN-15 (BN 3개) 기준 충분 |
| Health check overhead | < 1% CPU | 30s interval (D2.1-D3 §5.5 기본값) |

---

## 14. V1/V2/V3 Phase 매핑 (E9, R6 준수)

> Phase **일정**은 종합계획서 §7 정본. 본 절은 **scope 정의** 만 기술.

| Phase | scope |
|---|---|
| **V1** | Streamable HTTP 단일 transport (LOCK-BN-11), 6 protocol 전부, **4 tier 매핑(free/basic/premium/enterprise)** + API Key 단일 인증, Lifecycle `state_changed` 구독(ACTIVE/DRAINING/TERMINATED 분기), `prompts/get` guardrail 적용(03 §4), LOCK-BN-19 타임아웃 흐름 (10min/5min), **Level 5 차단 LOCK**, sampling 차단 (Pydantic enum) |
| **V2** | OAuth2 / MCP Token 인증 추가, atomic capability swap, ToolRegistry 캐시 (Redis), `notifications/*` push, Realtime API §6.6 와의 연동, 인증 실패 anomaly detection |
| **V3** | sampling 활성화 검토 (§7.2 4 조건 충족 시), 다중 Bridge 인스턴스 (per-region), MCP 마켓플레이스 (D2.0-03 §6.4 K-008) 연동, 동적 클라이언트 onboarding API |

---

## 15. 교차 참조 요약

| 참조 대상 | 위치 | 관계 |
|---|---|---|
| D2.1-D3 §5.5 MCPBridgeLayerSchema | SOT | 본 문서 정본 (DEC-017, AC-D3-008 LOCK) |
| D2.0-03 §6.4 / §6.5 / §6.6 / §6.7 | SOT | LOCK-BN-11, Tool Use, Realtime, SDK 통합 |
| D2.0-07 §4.3.2 + §15.11 S7E-050 | SOT | LOCK-BN-19 Approval Timeout |
| 01 Permission Matrix | `01_permission-matrix/` | tier→Level 매핑, Level 5 차단 LOCK, resource_type 검증 |
| 02 Interface Contract | `02_core-node-interface/` | NodeRequest/Response Envelope 변환 |
| 03 Template Injection | `03_template-injection/` **§2 + §4** | `prompts/list` (§2 TS_*) + `prompts/get` guardrail 11종 (§4) |
| 04 Lifecycle FSM | `04_node-lifecycle/` **§9** | `bn.lifecycle.state_changed` 구독 (`to` 분기) |
| 05 Memory Sharing | `05_memory-sharing/` **§4.2** | `resources/read` → MemoryBroker (CORE-mediated, LOCK-BN-14) |
| 06 Policy Overrides | `06_policy-overrides/` | RateLimit/permission stricter override 수용 |
| 07 Gate (D2.0-07) | SOT | LOCK-BN-10 경유 의무 |

---

## 16. L3 충족 매트릭스 + GAP 해소

### 16.1 E1~E9 매트릭스

| 항목 | 충족 위치 | 비고 |
|---|---|---|
| **E1** 데이터 모델 (Pydantic) | §3 (**10 BaseModel** + 1 Enum: AuthConfig, MCPBridgeLayer, MCPRequest, MCPResponse, MCPTool, MCPResource, MCPPrompt, MCPClient, AuthResult, RateLimitConfig + ClientTier(Enum)) | Forward ref 자체 회피 선언 순서. AC-D3-008 transport validator + Level 5 차단 validator(`AuthResult.permission_level ≤ 4`) 포함 |
| **E2** 알고리즘/플로우 | §4.3 변환 함수(`mcp_call_to_envelope`), §5.1 `state_changed` 분기 + atomic swap, §6.1 7 단계 인증, §8.1 시퀀스 | 변환 + 디스패치 + 시퀀스 |
| **E3** 의존성 명시 | §9 (상위 9건 / 하위 3건) | 정본 위임 경계 명시 |
| **E4** 단위 테스트 ≥ 5 | §11 TC-MB-01 ~ TC-MB-20 + 14b/14c (**22건**) | LOCK-BN-11/19/10 + Level 5 + Lifecycle 4 분기 + sampling 차단 전부 커버 |
| **E5** 에러 코드 + 복구 | §10 (**13종** failure_code + MCP error.code 매핑) | UPPER_SNAKE, JSON-RPC 호환 |
| **E6** 성능 기준 | §13 (8 지표) | LOCK-BN-15 정렬 |
| **E7** 보안 + 감사 | §12 (11 event_type + 5 가드) | TLS 1.3, 토큰 마스킹, atomic 롤백 |
| **E8** 도메인 예시 | §4.2 BN-WebResearch 변환 예시, §6.2 4 tier 매핑, §8.3 클라이언트 안내 페이로드 | 실제 BN 인스턴스 기반 |
| **E9** Phase 매핑 (R6) | §14 V1/V2/V3 scope | 일정 미포함 (정본 위임) |

### 16.2 GAP-BN-07 해소 판정

| 항목 | 결과 | 근거 |
|---|---|---|
| Part2 수준 상세 → L3 기준 충족 | **PASS** | E1~E9 9/9 |
| LOCK-BN-11 (Streamable HTTP only) | **PASS** | §LOCK 인용, §3.1 validator (TC-MB-01/02), §10 TRANSPORT_VIOLATION |
| LOCK-BN-19 (10min / 5min Auto deny) | **PASS** | §8 시퀀스, §8.2 매핑, TC-MB-11/12 |
| AC-D3-008 (transport enum) | **PASS** | §3.1 `MCPBridgeLayer._enforce_streamable_http` validator |
| LOCK-BN-10 (07 Gate 경유) | **PASS** | §LOCK 인용, §8.1 시퀀스, TC-MB-10 |
| 6 MCP 프로토콜 지원 + sampling 미지원 | **PASS** | §7 |
| GAP-BN-07 CRITICAL 해소 | **PASS** | 위 전부 + Part2 부재 → Part2 정본 작성 |
| V-10 기여 | **PASS** | GAP 7건 중 본 건 resolved → V-10 진행도 **7/7** |

---

## 17. 변경 요약

### 17.1 v1.0 → v2.0 (2026-04-07)

| 항목 | v1.0 (DRAFT, 178줄) | v2.0 (REVIEW, L3) |
|---|---|---|
| Status | DRAFT | REVIEW |
| LOCK 인용 | DEC-017 만 | **LOCK-BN-11 + LOCK-BN-19 + LOCK-BN-10 + AC-D3-008 4건** |
| 데이터 모델 | YAML 6 필드 | **Pydantic 10 BaseModel + 1 Enum + transport/Level5 validator** (§3) |
| MCPBlueNodeServer | 표 1개 | **변환 규칙 + 4.3 변환 함수 + 4.4 응답 매핑** |
| MCPToolRegistry | 표 1개 | **atomic swap + Lifecycle 이벤트 구독 + 롤백** (§5) |
| MCPAuthGateway | 표 + tier 매핑 | **7 단계 인증 + Level 5 차단 LOCK + Rate Limit YAML** (§6) |
| MCP 프로토콜 | 표 1개 (✅/❌) | **§7 매핑 + sampling 4 확장 조건** |
| LOCK-BN-19 통합 | **부재** | **§8 시퀀스 + 매핑 표 + 에러 페이로드** |
| 에러 코드 | 부재 | **13 failure_code + JSON-RPC code 매핑** (§10) |
| 단위 테스트 | 부재 | **TC-MB-01~20 + 14b/14c (22건)** (§11) |
| 감사 로그 | 부재 | **11 event_type + 보안 가드** (§12) |
| 성능 기준 | 부재 | **8 지표** (§13) |
| Phase 매핑 (R6) | 부재 | **V1/V2/V3 scope** (§14) |
| 의존성 명시 | 4행 | **상위 9건 / 하위 3건** (§9) |
| 정본 소유 경계 | 모호 | **5 도메인 위임 명시** (§1 소유 경계 박스) |
| L3 매트릭스 | 부재 | **E1~E9 9/9 + GAP-BN-07 해소 판정** (§16) |

### 17.2 SoT 교차 검증 (HIGH/MED/LOW)

> MEMORY [feedback "SoT 교차 검증 필수"](memory/feedback_sot_crosscheck.md) 패턴 적용.

| 등급 | 건수 | 내용 | 처리 |
|:---:|:---:|---|---|
| HIGH | 0 | — | — |
| MED | 0 | — | — |
| LOW | 1 | 종합계획서 §7 1-4 입력 파일 표기 "D2.0-03 §5 (MCP 연동)" 은 D2.0-03 §5 가 통신 레이어 절이며 실제 MCP 정본은 **§6.4~§6.7** (§6.4 표준 채택, §6.5 Bridge Layer, §6.6 Realtime, §6.7 SDK 통합). 1-1~1-3 LOW 사례와 동일한 SoT 라벨 차이 패턴. | 본 문서 §LOCK + §SOT 근거에서 §6.4~§6.7 로 정정 인용. 종합계획서 §7 1-4 텍스트는 P1-4 검증 결과 박스에 LOW 사례로 기록. |

### 17.3 해결 이슈 ID

- **GAP-BN-07** ✅ (CRITICAL) — Part2 부재 → 17 섹션 L3 정본 작성
- **V-10 진행도** 6/7 → **7/7** (잔여 0)
- **LOCK-BN-11 / LOCK-BN-19 / LOCK-BN-10 / LOCK-BN-03 / LOCK-BN-16 / AC-D3-008** 인용 정합 ✅
- **L3 E1~E9** 9/9 ✅
- 06 (1-3) §13 의 "1-4 완료 시 07_mcp-bridge L2→L3 정합 재확인" 이월 항목 → 본 문서로 충족 (RateLimit/permission 파라미터가 06 의 stricter-only 합성에 정합)

### 17.4 v2.0 → v2.1 (2026-04-08 미세 재검증 패스)

> 1-4 산출물 미세 검증 결과 다음 결함 11종 + 부수 6종을 수정. 06 의 v2.0→v2.1 패스와 동일한 형식.

| # | 결함 | 위치 | 수정 |
|---|------|------|------|
| F1 | **NodeRequestEnvelope 7 필수 필드 명세 오류 (CRITICAL)** — 02 §2.1 / AC-D3-004 정본 7 필드는 `request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id` 인데 v2.0 §4.3 변환 함수가 상세명세 L2 의 **삭제 필드** 7개(`task_type, task_params, template_set_id, conversation_turn, user_intent, relevant_memory, message`)를 사용 | §4.3 변환 함수, §1 소유 경계, TC-MB-09 docstring | 7 정본 필드로 완전 재작성. `intent_summary` 로 의도 요약, `constraints` 에 `mcp_arguments` 를 보존 (내부 구조 미확정 — CF-006). 함수 시그니처에 `project_id/session_id/trace_id` 명시 주입 강제 (uuid4() 즉석 생성 금지 — trace 단절 방지) |
| F2 | **VamosMessage K-049 6 필드 위반 (CRITICAL)** — 02 §1.1 정본은 `id, type, source, target, content, metadata` 6 필드 + Source/Target/Content/Metadata 서브모델인데 v2.0 §4.3 가 K-049 에서 **삭제된 필드**(`source: str, destination, message_type, payload, metadata=MessageMetadata, auth_token, permission_level`)를 사용 | §4.3 VamosMessage 생성 | 02 §1.1 정본 그대로 사용: `VamosMessageSource(agent_id, node_type)`, `VamosMessageTarget(agent_id, node_type)`, `VamosMessageContent(text, data, artifacts)`, `VamosMessageMetadata(priority:int, cost, confidence, trace_id)`. 인증/권한 필드는 K-049 에 부재이므로 제거. `message_type` → `type` 으로 정정. envelope 와 vmsg 를 **동일 trace_id** 로 묶고 tuple 반환 (02 §4.2) |
| F3 | **04 Lifecycle 이벤트 명 부재 (CRITICAL)** — v2.0 §5.1 가 `bn.lifecycle.activated` / `bn.lifecycle.terminated` / `bn.capability.changed` 3 이벤트를 구독한다고 명시했으나 04 §9 LogEvent Registry 에는 **`bn.lifecycle.state_changed`** 단일 이벤트만 존재 (payload: `node_id, from, to, trigger`). 존재하지 않는 이벤트 구독은 구현 시 0 호출로 귀결 | §5.1 표 + 5.1 코드, §9.1, §15, TC-MB-13/14 | 단일 진입점 `on_state_changed(payload)` 로 변경, `to == "ACTIVE"` → 등록 / `to in {"DRAINING", "TERMINATED"}` → 해제 분기. TC-MB-13/14 payload 명시. TC-MB-14b/14c 신규 추가 (DRAINING 즉시 차단 + 무관 상태 무시) |
| F4 | **04 섹션 번호 오류** — `04 §6 LogEvent` 라고 표기했으나 04 의 LogEvent 명세는 **§9** (§6 은 Lazy Generation 전략) | §9.1 + §15 | `§9` 로 정정 |
| F5 | **03 섹션 번호 오류** — `03 §3.3` 이라고 표기했으나 03 의 Guardrail 카탈로그는 **§4** (§3 은 주입 파이프라인). 추가로 §4.1 row TemplateSet 정본 = `03 §3` (실제는 **§2 Template Set 정의**) 도 동일 클래스 오류 | §1 소유 경계, §4.1 TemplateSet 행, §7.1 prompts/get, §9.1, §15, TC-MB-17 | `§4` 로 정정 (5 곳) + §4.1 / §9.1 / §15 row 03 항목에 §2 (Template Set) + §4 (Guardrail) 두 섹션 모두 명시 |
| F6 | **§7.1 함수명 typo** — `tools_call_to_envelope()` ← v2.0 의 §4.3 정의는 `mcp_call_to_envelope()` | §7.1 tools/call 행 | `mcp_call_to_envelope()` 로 정정 |
| F7 | **MCPClient `enabled` 필드 누락** — §6.1 단계 3 가 `enabled = true` 를 검증한다고 명시했으나 §3.4 `MCPClient` 모델에 `enabled` 필드 부재 → `CLIENT_DISABLED` 거부 사유 발화 불가 | §3.4 `MCPClient` | `enabled: bool = True` 추가 |
| F8 | **AuthResult Level 5 코드 가드 부재** — §6.2 가 "Level 5 외부 클라이언트 매핑 금지 LOCK" 을 선언했으나 `AuthResult.permission_level: int = 0` 는 `le=4` 미설정 → 코드 레벨 강제 부재. 추가로 v2.0 docstring 이 Level 5 를 "FINANCIAL_CONFIRMATION" 으로 명명했으나 01 §1 PermissionLevel enum 정본은 **`FINANCIAL = 5`** ("FINANCIAL_CONFIRMATION_TIMEOUT" 은 failure_code 명) | §3.4 `AuthResult`, §6.2 footnote | `Field(0, ge=0, le=4)` + docstring LOCK 명시 + Level 5 명칭을 01 정본 `FINANCIAL` 로 정정 (TC-MB-06 와 정합) |
| F9 | **MCPRequest sampling 차단 메커니즘 미명시** — §3.2 method Literal 에 sampling 부재로 Pydantic ValidationError 발생하나 디스패처가 이를 -32601 로 변환하는 흐름이 명시되지 않음 → TC-MB-16 와 §10 표 사이 의미 단절 | §3.2 docstring, §10 신규 코드, §11 TC-MB-16, §7.1 sampling 행 | MCPRequest docstring 에 ValidationError → -32601 변환 흐름 명시. §10 에 `SAMPLING_NOT_SUPPORTED` 신규 추가 (-32601). TC-MB-16 결과에 ValidationError catch 단계 명시 |
| F10 | **`_https_in_prod` validator 명 ↔ 동작 불일치** — 함수명은 "https in prod" 인데 `http://` 도 허용 → 의도/이름 misleading | §3.1 validator | `_require_url_scheme` 으로 개명 + 주석 "프로덕션은 https 권장 (TLS 1.3, §12.2)" |
| F11 | **`from datetime import datetime` 사용처 0** — §3 import 블록에 dead import (datetime 필드 없음. timestamp 는 02 정본 VamosMessageMetadata 가 보유) | §3 imports | 삭제 |

**v2.1 부수 변화**:
- §3 §5 코드 블록에 `import asyncio` 명시 (`MCPToolRegistry._lock = asyncio.Lock()` 과 정합)
- §4.3 변환 함수 반환형을 `tuple[NodeRequestEnvelope, VamosMessage]` 로 명시 — 두 객체는 분리 레이어이며 trace_id 로 연결됨을 02 §4.2 에 따라 명시
- §4.3 함수에 `registry` 의 capability 메타 사전 조회 책임 주석 추가 (§6.1 단계 6 선행)
- §14 V1 scope 에 `enterprise tier` 추가 (§6.2 / §6.3 와 정합 — v2.0 은 V2 로 분류했으나 매핑 표는 V1 에 이미 존재 → V1 에 통합)
- §16.1 E1 행 "10 클래스" → "**10 BaseModel** + 1 Enum" 로 정확화. ClientTier 가 Enum 임을 명시
- §16.1 E4 행 "20 건" → **22건** (TC-MB-14b/14c 신규)
- §16.1 E5 행 "12종" → **13종** (`SAMPLING_NOT_SUPPORTED` 신규)
- §11 TC-MB-09 의 expected 결과에 **7 정본 필드명 전부** 나열 + VamosMessage source/node_type 검증 명시
- §17.3 LOCK 정합 목록에 LOCK-BN-03 / LOCK-BN-16 추가 (02 정본 사용에 따른 자연 인용)

### 17.5 v2.1 SoT 교차 검증 후속 (2026-04-08)

| 등급 | 건수 | 내용 | 처리 |
|:---:|:---:|---|---|
| HIGH | 0 | — | — |
| MED | 0 | — | — |
| LOW | 0 | (v2.1 패스에서 신규 발견 0건) | — |

> v2.1 패스에서 발견된 결함 11종(F1~F11) 은 모두 **본 문서 내부의 교차 일관성 결함**(02/03/04 정본과의 부정합 또는 자체 코드/이름 일관성 위반) 이며, SoT 자체에 대한 신규 LOW 사례는 발견되지 않았다.

---

*정본 소유: 07_mcp-bridge/_index.md → MCPBridgeLayer (LOCK-BN-11/AC-D3-008) + MCPBlueNodeServer 변환(02 §2.1 7 필드 정합) + MCPToolRegistry atomic swap (04 §9 `state_changed` 분기) + MCPAuthGateway 7단계 + Level 5 차단 코드 가드 + 6 protocol + sampling 차단(Pydantic enum + -32601) + LOCK-BN-19 시퀀스*
