# PHASE_B5_TEST_STRATEGY (v1.0.0)

## 0. 문서 메타

| 항목 | 값 |
|------|-----|
| 문서 ID | B5 |
| 문서명 | PHASE_B5_TEST_STRATEGY |
| 버전 | 1.0.0 |
| 역할 | 테스트 전략 (Test Strategy & AC Verification Mapping) |
| 상위 정본 | BASE 1.3 > PLAN 3.0 > DESIGN 2.0 > D2.1 Schema > B4 Config Spec |
| 생성 일자 | 2026-02-22 |
| 연결 참조 | D2~D8 Acceptance Criteria, A1 Tech Stack, B4 Config Spec |

---

## 1. 개요

### 1.1 테스트 피라미드

VAMOS 플랫폼의 테스트는 3-Layer 피라미드 구조를 따른다.

```
        /  E2E  \          ← 핵심 시나리오 100%
       / 통합 테스트 \       ← 60%+ 커버리지
      /  단위 테스트   \     ← 80%+ 커버리지
     ------------------
```

| 계층 | 범위 | 도구 | 커버리지 목표 |
|------|------|------|-------------|
| **단위 (Unit)** | 함수/클래스/모듈 개별 검증 | pytest (Python), cargo test (Rust), vitest (React) | **80%+** |
| **통합 (Integration)** | 모듈 간 인터페이스, Pipeline 흐름 | pytest + subprocess, Docker Compose | **60%+** |
| **E2E** | 사용자 시나리오 전체 흐름 | Tauri WebDriver + Playwright | 핵심 시나리오 **100%** |

### 1.2 테스트 원칙

1. **AC 완전 매핑**: D2~D8의 모든 AC(Acceptance Criteria)는 최소 1개 이상의 테스트 케이스에 매핑.
2. **스키마 우선 검증**: Pydantic v2 모델로 정의된 스키마는 유효/무효 인스턴스 모두 테스트.
3. **비밀 분리**: 테스트 환경에서도 실제 API 키를 사용하지 않으며, mock/fixture로 대체.
4. **재현 가능성**: 모든 테스트는 CI/CD에서 독립 실행 가능. 외부 의존성은 mock 처리.
5. **실패 추적**: 테스트 실패 시 관련 AC ID와 스키마 REF를 로그에 기록.

### 1.3 테스트 ID 규칙

```
T-{계층}-{문서ID}-{순번}
```

- 계층: `U` (Unit), `I` (Integration), `E` (E2E)
- 문서 ID: `D2`~`D8`, `SYS` (시스템 전반)
- 순번: 3자리 (001, 002, ...)

예시: `T-U-D2-001`, `T-I-SYS-003`, `T-E-SYS-001`

---

## 2. 단위 테스트 (Unit Tests)

### 2.1 Python -- pytest

#### 2.1.1 schemas/ (Pydantic 모델 검증 -- D2.1 AC 기반)

모든 D2.1 스키마 문서에서 정의한 Pydantic 모델에 대해 유효/무효 인스턴스 테스트를 수행한다.

```
tests/
  unit/
    schemas/
      test_decision_schema.py       # D2 DecisionSchema
      test_log_event_schema.py      # D2 LogEventSchema
      test_node_schemas.py          # D3 NodeCapabilityProfile, Request/Response Envelope
      test_tool_schemas.py          # D4 ToolRegistryEntry, BrainAdapterResponse
      test_workflow_schemas.py      # D5 WorkflowOutputEnvelope, FailureReport, VerifyChainEntry
      test_agent_schemas.py         # D5 AgentMarketplace, CircuitBreaker, GatePipelineMapping, HITL
      test_memory_schemas.py        # D6 MemoryRecord, SourceQoD, VectorStoreAdapter
      test_graph_cache_schemas.py   # D6 GraphRAGConfig, SemanticCache
      test_safety_schemas.py        # D7 PolicyCheck, Approval, CostBudget, Downshift
      test_guardrails_schema.py     # D7 GuardrailsCheck, RBACRole, AutonomyLevel
      test_config_model.py          # B4 VamosConfig (config.toml 검증)
```

**주요 테스트 패턴**:

```python
# tests/unit/schemas/test_decision_schema.py
import pytest
from vamos_core.schemas.orange_core import DecisionSchema


class TestDecisionSchema:
    """AC-D2-001: _meta 필수 속성 검증"""

    def test_valid_decision(self, valid_decision_fixture):
        """유효한 DecisionSchema 인스턴스가 생성된다."""
        d = DecisionSchema(**valid_decision_fixture)
        assert d.decision_id.startswith("dec_")
        assert d.locked is True

    def test_meta_required_fields(self, valid_decision_fixture):
        """_meta에 schema_name, schema_version, owner_doc,
        sec_id_slug, ref, ref_locked 포함."""
        d = DecisionSchema(**valid_decision_fixture)
        meta = d.meta
        for field in ["schema_name", "schema_version", "owner_doc",
                       "sec_id_slug", "ref", "ref_locked"]:
            assert hasattr(meta, field), f"Missing _meta.{field}"

    def test_invalid_policy_gate_rejected(self, valid_decision_fixture):
        """AC-D2-003: policy_gate에 근거 없는 값 추가 시 거부."""
        data = {**valid_decision_fixture, "policy_gate": "unknown"}
        with pytest.raises(ValueError):
            DecisionSchema(**data)

    def test_enum_conclusion_values(self, valid_decision_fixture):
        """AC-D2-003: conclusion은 ACCEPT|REJECT|HOLD|ESCALATE만 허용."""
        for valid in ["ACCEPT", "REJECT", "HOLD", "ESCALATE"]:
            data = {**valid_decision_fixture, "conclusion": valid}
            d = DecisionSchema(**data)
            assert d.conclusion == valid

        data = {**valid_decision_fixture, "conclusion": "INVALID"}
        with pytest.raises(ValueError):
            DecisionSchema(**data)
```

#### 2.1.2 orange_core/ (Decision Kernel, Intent Parser)

```
tests/
  unit/
    orange_core/
      test_decision_kernel.py       # Decision Kernel 로직
      test_intent_parser.py         # Intent 파싱/분류
      test_evidence_collector.py    # Evidence 수집/QoD 산출
      test_event_registry.py        # EventTypeRegistry 정합
      test_failure_registry.py      # FailureCodeRegistry 정합
      test_fallback_registry.py     # FallbackRegistry 정합
```

**주요 테스트**:

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_decision_kernel.py` | Decision 생성/잠금/단일결정 원칙 | AC-D2-001, AC-D2-003 |
| `test_intent_parser.py` | IntentFrame 생성, 필수 필드 | D2 DecisionSchema.intent_frame_ref |
| `test_evidence_collector.py` | EvidencePack 수집, QoD 점수 | D2 DecisionSchema.evidence_pack_ref |
| `test_event_registry.py` | EventTypeRegistry SOT 검증 | AC-D2-002 |
| `test_failure_registry.py` | FailureCodeRegistry SOT 검증 | AC-D2-002 |
| `test_fallback_registry.py` | FallbackRegistry SOT 검증 | AC-D2-002 |

#### 2.1.3 blue_nodes/ (Node 실행 로직)

```
tests/
  unit/
    blue_nodes/
      test_node_registry.py         # NodeRegistry SOT 검증
      test_node_executor.py         # Node 실행/라우팅
      test_request_envelope.py      # NodeRequestEnvelope 7필드
      test_response_envelope.py     # NodeResponseEnvelope 최소필드
      test_tool_call_registry.py    # ToolCallRegistry 정합
      test_mcp_bridge.py            # MCPBridgeLayer 전송 방식
```

**주요 테스트**:

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_node_registry.py` | NodeRegistry D3 SOT 단일 확정 | AC-D3-001 |
| `test_request_envelope.py` | Request 7필드 필수 포함 | AC-D3-004 |
| `test_response_envelope.py` | Response 최소 필드 포함 | AC-D3-005 |
| `test_tool_call_registry.py` | ToolCallRegistry.tool_id와 D4 ToolRegistry 정합 | AC-D3-007 |
| `test_mcp_bridge.py` | transport가 `streamable_http`만 허용 | AC-D3-008 |

#### 2.1.4 safety/ (PolicyCheck, CostBudget, Guardrails)

```
tests/
  unit/
    safety/
      test_policy_check.py          # PolicyCheck deny/restrict/allow
      test_approval.py              # Approval 요청/응답/상태
      test_cost_budget.py           # CostBudget 예산/임계치/다운시프트
      test_downshift.py             # Downshift 80%/100% 동작
      test_guardrails.py            # 3-Layer Guardrails 판정
      test_rbac.py                  # RBAC 4역할 검증
      test_autonomy.py              # Autonomy L0~L3 검증
```

**주요 테스트**:

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_guardrails.py` | 3-Layer 모두 pass 시 allow, 하나라도 fail 시 deny/restrict | AC-D7-005 |
| `test_rbac.py` | OWNER/ADMIN/OPERATOR/VIEWER 4역할만 허용 | AC-D7-006 |
| `test_autonomy.py` | L0~L3만 허용, L2/L3에서만 auto_execute=true | AC-D7-007 |
| `test_policy_check.py` | deny/restrict/allow 판정 정확성 | AC-D7-002 |
| `test_cost_budget.py` | daily/monthly limit, warn/block 임계값 | D7 CostBudgetSchema |
| `test_downshift.py` | 80% warn -> force_mini, 100% -> block | D7 DownshiftSchema |

#### 2.1.5 storage/ (Memory, VectorStore, SemanticCache)

```
tests/
  unit/
    storage/
      test_memory_record.py         # MemoryRecord scope/type 검증
      test_vector_store.py          # VectorStore 어댑터 전환 투명성
      test_semantic_cache.py        # SemanticCache 0.95 LOCK
      test_graph_rag.py             # GraphRAG scope V1=P1/V2+=FULL
      test_source_qod.py            # SourceQoD 점수 산출
```

**주요 테스트**:

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_memory_record.py` | scope L0~L3만, memory_type B-1~B-4만 허용 | AC-D6-002, AC-D6-003 |
| `test_memory_record.py` | policy_decision allow/restrict/deny와 D7 정합 | AC-D6-004 |
| `test_vector_store.py` | backend 전환(chroma->qdrant) 시 인터페이스 무변경 | AC-D6-008 |
| `test_semantic_cache.py` | similarity_threshold >= 0.95 LOCK | AC-D6-010 |
| `test_graph_rag.py` | scope V1=P1, V2+=FULL | AC-D6-009 |

#### 2.1.6 agent/ (LangGraph StateGraph, CircuitBreaker)

```
tests/
  unit/
    agent/
      test_state_graph.py           # LangGraph StateGraph 구성
      test_pipeline_stages.py       # 5단계 Pipeline (Intake~Deliver)
      test_workflow_output.py       # WorkflowOutputEnvelope 3단 출력
      test_verify_chain.py          # VerifyChainEntry EVX-1~6
      test_failure_report.py        # FailureReport 생성
      test_circuit_breaker.py       # CircuitBreaker open 차단
      test_gate_pipeline.py         # GatePipelineMapping 최소1Gate
      test_hitl_request.py          # HITLRequest autonomy_level
      test_agent_marketplace.py     # AgentMarketplace verified+sandbox
      test_loop_control.py          # Soft/Hard loop 제어
```

**주요 테스트**:

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_workflow_output.py` | user_response/evidence_summary/log_report 3필드 필수 산출 | AC-D5-003 |
| `test_verify_chain.py` | evx_id는 EVX-1~EVX-6 또는 self_check/evidence_check만 | AC-D5-004 |
| `test_loop_control.py` | Soft loop 1회 자동, Hard loop 승인 필요 | AC-D5-006 |
| `test_circuit_breaker.py` | state=open 시 recovery_time 전 호출 차단 | AC-D5-009 |
| `test_gate_pipeline.py` | 모든 stage에 최소 1개 필수 Gate | AC-D5-010 |
| `test_hitl_request.py` | autonomy_level L0~L3만 허용 | AC-D5-011 |
| `test_agent_marketplace.py` | verified=true + sandbox_required=true일 때만 실행 | AC-D5-008 |

### 2.2 Rust -- cargo test

#### 2.2.1 IPC command handler 테스트

```
src-tauri/
  src/
    commands/
      mod.rs
      tests.rs                      # IPC 커맨드 핸들러 단위 테스트
```

**주요 테스트**:

| 테스트 ID | 검증 대상 | 설명 |
|----------|----------|------|
| `T-U-RUST-001` | `invoke_python_agent` | Tauri IPC -> Python subprocess 호출 정상 동작 |
| `T-U-RUST-002` | `handle_ipc_error` | Python 프로세스 에러 시 Rust 에러 핸들링 |
| `T-U-RUST-003` | `serialize_response` | IPC 응답 JSON 직렬화 정합성 |
| `T-U-RUST-004` | `config_load` | config.toml 로딩 및 Rust 구조체 매핑 |

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_invoke_python_agent_returns_valid_json() {
        // Tauri IPC command가 Python subprocess를 호출하고
        // 유효한 JSON 응답을 반환하는지 검증
        let result = invoke_python_agent_mock("test_input");
        assert!(result.is_ok());
        let json: serde_json::Value = serde_json::from_str(
            &result.unwrap()
        ).unwrap();
        assert!(json.get("trace_id").is_some());
    }

    #[test]
    fn test_handle_python_subprocess_error() {
        // Python 프로세스 비정상 종료 시 에러 핸들링
        let result = invoke_python_agent_mock("__trigger_error__");
        assert!(result.is_err());
    }
}
```

#### 2.2.2 Python subprocess 관리 테스트

| 테스트 ID | 검증 대상 | 설명 |
|----------|----------|------|
| `T-U-RUST-005` | `spawn_python` | Python 프로세스 정상 생성/종료 |
| `T-U-RUST-006` | `python_health_check` | Python 프로세스 상태 확인 (health ping) |
| `T-U-RUST-007` | `python_restart` | Python 프로세스 비정상 종료 시 자동 재시작 |
| `T-U-RUST-008` | `stdin_stdout_pipe` | stdin/stdout 파이프 데이터 전송 검증 |

### 2.3 React -- vitest

#### 2.3.1 컴포넌트 테스트

```
src/
  components/
    __tests__/
      ChatPanel.test.tsx            # 채팅 패널 컴포넌트
      DecisionCard.test.tsx         # Decision 표시 카드
      CostDashboard.test.tsx        # 비용 대시보드
      ApprovalDialog.test.tsx       # 승인 다이얼로그
      NodeStatusBadge.test.tsx      # BLUE NODE 상태 배지
      GuardrailsAlert.test.tsx      # Guardrails 경고 알림
```

**주요 테스트**:

| 테스트 ID | 검증 대상 | 관련 AC |
|----------|----------|---------|
| `T-U-UI-001` | ChatPanel이 메시지를 올바르게 렌더링 | AC-D8-003 |
| `T-U-UI-002` | CostDashboard가 daily/monthly limit 표시 | AC-D8-005 |
| `T-U-UI-003` | ApprovalDialog가 HITL 승인 요청 표시 | AC-D8-005 |
| `T-U-UI-004` | GuardrailsAlert가 deny/restrict 상태 표시 | AC-D8-005 |
| `T-U-UI-005` | Tauri 2.0 IPC invoke 호출 정합성 | AC-D8-004 |

#### 2.3.2 Store/Hook 테스트

```
src/
  stores/
    __tests__/
      useAgentStore.test.ts         # Agent 상태 관리
      useCostStore.test.ts          # 비용 추적 상태
      useConfigStore.test.ts        # 설정 상태
  hooks/
    __tests__/
      useIPC.test.ts                # Tauri IPC 훅
      useStreaming.test.ts          # 스트리밍 응답 훅
```

| 테스트 ID | 검증 대상 | 설명 |
|----------|----------|------|
| `T-U-UI-006` | `useAgentStore` | Agent 상태 전이 (idle -> running -> completed) |
| `T-U-UI-007` | `useCostStore` | 비용 누적/임계값 경고 상태 |
| `T-U-UI-008` | `useIPC` | Tauri invoke 호출/응답 처리 |
| `T-U-UI-009` | `useStreaming` | Streamable HTTP 스트리밍 데이터 처리 |

---

## 3. 통합 테스트 (Integration Tests)

### 3.1 Python <-> Rust IPC 통합

```
tests/
  integration/
    test_ipc_bridge.py              # Python <-> Rust IPC 통합
```

| 테스트 ID | 검증 대상 | 설명 |
|----------|----------|------|
| `T-I-SYS-001` | IPC 요청/응답 라운드트립 | Rust에서 Python subprocess 호출 후 JSON 응답 수신 |
| `T-I-SYS-002` | IPC 에러 전파 | Python에서 발생한 에러가 Rust를 거쳐 React UI까지 전달 |
| `T-I-SYS-003` | IPC 타임아웃 처리 | Python 응답 지연 시 타임아웃 -> fallback 동작 |
| `T-I-SYS-004` | IPC trace_id 전파 | trace_id가 Rust IPC를 거쳐 Python까지 일관 전파 |

### 3.2 LangGraph Pipeline 통합 (Intake -> Deliver)

```
tests/
  integration/
    test_pipeline_e2e.py            # 5단계 Pipeline 전체 흐름
    test_pipeline_gates.py          # Gate 통과 검증
    test_pipeline_loop.py           # Soft/Hard loop 시나리오
```

| 테스트 ID | 검증 대상 | 관련 AC | 설명 |
|----------|----------|---------|------|
| `T-I-PIPE-001` | 정상 흐름 Intake->Deliver | AC-D5-003 | 5단계 전체 통과 후 3단 출력 생성 |
| `T-I-PIPE-002` | Gate 차단 시 흐름 중단 | AC-D5-010, AC-D7-005 | PolicyCheck deny 시 Execute 진입 차단 |
| `T-I-PIPE-003` | Soft loop 1회 자동 재시도 | AC-D5-006 | Verify 실패 -> 1회 자동 재시도 |
| `T-I-PIPE-004` | Hard loop 승인 대기 | AC-D5-006 | 2회 이상 실패 -> HITL 승인 필요 |
| `T-I-PIPE-005` | CircuitBreaker open 차단 | AC-D5-009 | open 상태 -> 호출 차단 -> recovery 후 half_open |
| `T-I-PIPE-006` | 비용 초과 시 다운시프트 | D7 DownshiftSchema | 80% -> force_mini, 100% -> block |
| `T-I-PIPE-007` | Decision -> Node 연결 | AC-D3-006 | decision_id로 Node 실행 추적 가능 |

### 3.3 Storage 통합 (Memory + Vector + Cache)

```
tests/
  integration/
    test_storage_stack.py           # Storage 스택 통합
    test_vector_migration.py        # Vector DB 전환 테스트
```

| 테스트 ID | 검증 대상 | 관련 AC | 설명 |
|----------|----------|---------|------|
| `T-I-STOR-001` | MemoryRecord CRUD | AC-D6-002, AC-D6-003 | L0~L3, B-1~B-4 메모리 생성/조회/삭제 |
| `T-I-STOR-002` | VectorStore 쓰기/검색 | AC-D6-008 | 임베딩 저장 후 유사도 검색 정확성 |
| `T-I-STOR-003` | SemanticCache 히트/미스 | AC-D6-010 | 0.95 이상 = 히트, 미만 = 미스 |
| `T-I-STOR-004` | Chroma->Qdrant 전환 | AC-D6-008 | 어댑터 교체 후 상위 인터페이스 무변경 |
| `T-I-STOR-005` | GraphRAG 쿼리 통합 | AC-D6-009 | JSON 파일(V1) / Neo4j(V2+) 동일 인터페이스 |
| `T-I-STOR-006` | Memory TTL 만료 처리 | D6 MemoryRecordSchema | L0=session_end, L1=90d 등 TTL 적용 |

### 3.4 Safety 통합 (PolicyCheck -> Approval -> CostBudget)

```
tests/
  integration/
    test_safety_chain.py            # Safety 체인 통합
    test_guardrails_pipeline.py     # 3-Layer Guardrails 통합
```

| 테스트 ID | 검증 대상 | 관련 AC | 설명 |
|----------|----------|---------|------|
| `T-I-SAFE-001` | PolicyCheck -> Approval 연결 | AC-D7-002 | restrict 판정 -> 승인 요청 생성 |
| `T-I-SAFE-002` | CostBudget -> Downshift 연결 | D7 DownshiftSchema | 예산 80% -> force_mini 전환 |
| `T-I-SAFE-003` | 3-Layer Guardrails 순차 검사 | AC-D7-005 | L1(NeMo) -> L2(Guardrails AI) -> L3(LlamaGuard) 순차 통과 |
| `T-I-SAFE-004` | RBAC 권한 기반 실행 제어 | AC-D7-006 | VIEWER는 실행 불가, OPERATOR는 실행 가능 |
| `T-I-SAFE-005` | Autonomy 수준별 승인 흐름 | AC-D7-007 | L0/L1은 auto_execute=false, L2/L3은 auto_execute=true |
| `T-I-SAFE-006` | ToolRegistry 경유 필수 | AC-D4-006 | 직접 HTTP 호출 시 차단, ToolRegistry 경유 시 허용 |

---

## 4. E2E 테스트

### 4.1 Tauri WebDriver 기반

E2E 테스트는 Tauri의 WebDriver 지원 + Playwright를 조합하여 실행한다.

```
tests/
  e2e/
    conftest.py                     # Tauri 앱 실행/종료 fixture
    test_user_chat_flow.py          # 채팅 시나리오
    test_cost_limit_flow.py         # 비용 제한 시나리오
    test_approval_flow.py           # 승인 흐름 시나리오
    test_error_recovery_flow.py     # 에러 복구 시나리오
```

**E2E 환경 구성**:

```python
# tests/e2e/conftest.py
import pytest
import subprocess
import time


@pytest.fixture(scope="session")
def tauri_app():
    """Tauri 데스크톱 앱 빌드 및 실행."""
    proc = subprocess.Popen(
        ["cargo", "tauri", "dev"],
        cwd="src-tauri",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(10)  # 앱 기동 대기
    yield proc
    proc.terminate()
    proc.wait()
```

### 4.2 시나리오 기반 (사용자 입력 -> 결과 확인)

| 테스트 ID | 시나리오 | 관련 AC | 검증 방법 |
|----------|---------|---------|----------|
| `T-E-SYS-001` | **기본 채팅 흐름**: 사용자가 질문 입력 -> AI 응답 수신 | AC-D5-003, AC-D8-003 | 5단계 Pipeline 완료, 3단 출력(user_response/evidence_summary/log_report) 확인 |
| `T-E-SYS-002` | **비용 초과 다운시프트**: 반복 요청으로 80% 도달 -> mini 모델 전환 | D7 DownshiftSchema, AC-D8-005 | CostDashboard에 경고 표시, 응답 모델이 mini로 전환 확인 |
| `T-E-SYS-003` | **비용 100% 차단**: 100% 도달 -> 요청 차단 | D7 DownshiftSchema | 차단 메시지 UI 표시, 추가 요청 불가 확인 |
| `T-E-SYS-004` | **HITL 승인 흐름**: P2 도메인 요청 -> 승인 대화상자 -> 승인/거부 | AC-D5-011, AC-D7-007 | ApprovalDialog 표시, 승인 시 실행 재개, 거부 시 중단 |
| `T-E-SYS-005` | **Guardrails 차단**: PII 포함 입력 -> deny 판정 -> 에러 메시지 | AC-D7-005 | GuardrailsAlert 표시, 실행 차단 확인 |
| `T-E-SYS-006` | **Node 에러 복구**: BLUE NODE 에러 -> fallback 동작 | D2 FallbackRegistry | 에러 메시지 후 fallback 실행, 사용자에게 결과 전달 |
| `T-E-SYS-007` | **MCP 브릿지 호출**: 웹 검색 요청 -> MCP 경유 -> 결과 표시 | AC-D3-008 | streamable_http 전송, 결과 정상 렌더링 |
| `T-E-SYS-008` | **설정 변경 반영**: config 변경 -> 앱 재시작 -> 변경 적용 확인 | B4 Config Spec | 설정 값이 UI에 정확히 반영 |

---

## 5. AC(Acceptance Criteria) 검증 매핑

### 5.1 D2 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D2-001 | DecisionSchema/LogEventSchema의 `_meta`는 D1 Schema Meta Template 필수 속성을 모두 포함 | T-U-D2-001 | `test_meta_required_fields` | Pydantic 모델에 _meta 필수 필드(schema_name, schema_version, owner_doc, sec_id_slug, ref, ref_locked) 존재 검증 |
| AC-D2-001 | (LogEventSchema) | T-U-D2-002 | `test_log_event_meta_fields` | LogEventSchema._meta 동일 필드 존재 검증 |
| AC-D2-002 | Registry 값 목록은 D2 SOT에서만 확정, 타 문서 재정의 금지 | T-U-D2-003 | `test_event_type_registry_sot` | EventTypeRegistry 값이 D2 정의와 일치, 외부 추가 시 거부 |
| AC-D2-002 | (FailureCodeRegistry) | T-U-D2-004 | `test_failure_code_registry_sot` | FailureCodeRegistry 값이 D2 정의와 일치 |
| AC-D2-002 | (FallbackRegistry) | T-U-D2-005 | `test_fallback_registry_sot` | FallbackRegistry 값이 D2 정의와 일치 |
| AC-D2-003 | enum 필드(policy_gate, approval_status, cost_gate, conclusion)는 DESIGN 2.0/D7 정본과 정합 | T-U-D2-006 | `test_enum_policy_gate_values` | policy_gate: deny/restrict/allow만 허용, 그 외 거부 |
| AC-D2-003 | (approval_status) | T-U-D2-007 | `test_enum_approval_status_values` | approval_status: approved/denied만 허용 |
| AC-D2-003 | (cost_gate) | T-U-D2-008 | `test_enum_cost_gate_values` | cost_gate: normal/downshift/split/stop만 허용 |
| AC-D2-003 | (conclusion) | T-U-D2-009 | `test_enum_conclusion_values` | conclusion: ACCEPT/REJECT/HOLD/ESCALATE만 허용 |

### 5.2 D3 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D3-001 | NodeRegistry는 D3 SOT로만 확정 | T-U-D3-001 | `test_node_registry_sot_ownership` | NodeRegistry 엔트리 생성은 D3 모듈만 가능, 외부 모듈에서 직접 추가 시 거부 |
| AC-D3-002 | D3 모든 스키마 블록은 D1 Meta Template 준수 | T-U-D3-002 | `test_d3_schemas_meta_template` | NodeCapabilityProfile/RequestEnvelope/ResponseEnvelope의 _meta 필수 필드 존재 |
| AC-D3-003 | event_type/failure_code/fallback_id는 02 정본 REF-only | T-U-D3-003 | `test_d3_ref_only_registries` | D3 모듈 내에 코드값 목록 직접 정의 없음 확인, import 경로가 D2 모듈 |
| AC-D3-004 | NodeRequestEnvelopeSchema 필수 7필드 포함 | T-U-D3-004 | `test_request_envelope_7_fields` | request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id 필수 검증 |
| AC-D3-005 | NodeResponseEnvelopeSchema 최소 필드 포함 | T-U-D3-005 | `test_response_envelope_min_fields` | trace_id, node_id, domain, inputs.summary, outputs.result, outputs.evidence_refs, status 포함 검증 |
| AC-D3-006 | 모든 NODE 실행은 decision_id로 D2 Decision에 연결 | T-U-D3-006 | `test_node_execution_decision_link` | Node 실행 결과에 decision_id 연결 존재, Trace 조회 가능 |
| AC-D3-007 | ToolCallRegistrySchema.tool_id는 D4 ToolRegistry와 정합 | T-U-D3-007 | `test_tool_call_registry_d4_alignment` | tool_id가 D4 ToolRegistry에 존재하지 않으면 거부 |
| AC-D3-008 | MCPBridgeLayerSchema.transport는 streamable_http만 | T-U-D3-008 | `test_mcp_transport_streamable_only` | transport="stdio" 시 ValidationError, transport="streamable_http" 시 성공 |

### 5.3 D4 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D4-001 | ToolRegistry는 D4 SOT로만 확정 | T-U-D4-001 | `test_tool_registry_sot_ownership` | ToolRegistry 값 목록/구조 변경은 D4 모듈에서만 가능 |
| AC-D4-002 | D4 모든 스키마는 D1 Meta Template 준수 | T-U-D4-002 | `test_d4_schemas_meta_template` | ToolRegistryEntry/BrainAdapterResponse/InfraInvokeResult의 _meta 필수 필드 확인 |
| AC-D4-003 | ToolRegistryEntry.required_gates는 D7 Gate와 정합 | T-U-D4-003 | `test_required_gates_d7_alignment` | required_gates 값이 policy/cost/approval/evidence/self_check 범위 내 |
| AC-D4-004 | event_type/failure_code/fallback_id는 02 정본 REF-only | T-U-D4-004 | `test_d4_ref_only_registries` | D4 모듈 내 코드값 직접 정의 없음 확인 |
| AC-D4-005 | BrainAdapterResponseSchema.trace_id 필수 | T-U-D4-005 | `test_brain_adapter_trace_id_required` | trace_id 누락 시 ValidationError |
| AC-D4-006 | 모든 Tool 실행은 ToolRegistry 경유 필수 | T-U-D4-006 | `test_tool_execution_registry_only` | 직접 HTTP/SDK 호출 차단, ToolRegistry.invoke()만 허용 |
| AC-D4-006 | (통합) | T-I-D4-001 | `test_tool_registry_bypass_blocked` | 통합 환경에서 직접 호출 시도 -> 차단 확인 |

### 5.4 D5 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D5-001 | D5 SOT 스키마 목록은 본 문서에서만 확정 | T-U-D5-001 | `test_d5_sot_schema_ownership` | WorkflowOutputEnvelope/FailureReport/VerifyChainEntry/WorkflowStage가 D5 모듈에 정의 확인 |
| AC-D5-002 | D5 모든 스키마는 D1 Meta Template 준수 | T-U-D5-002 | `test_d5_schemas_meta_template` | 모든 D5 스키마 _meta 필수 필드 존재 검증 |
| AC-D5-003 | WorkflowOutputEnvelope는 3필드 필수 산출 | T-U-D5-003 | `test_workflow_output_3_fields` | user_response, evidence_summary, log_report 모두 non-null |
| AC-D5-003 | (통합) | T-I-PIPE-001 | `test_pipeline_produces_3_outputs` | 5단계 Pipeline 완료 후 3단 출력 확인 |
| AC-D5-004 | VerifyChainEntry.evx_id는 EVX-1~6 + 표준 토큰만 | T-U-D5-004 | `test_verify_chain_evx_id_values` | EVX-1~EVX-6, self_check, evidence_check만 허용 |
| AC-D5-005 | event_type/failure_code/fallback_id는 02 REF-only | T-U-D5-005 | `test_d5_ref_only_registries` | D5 모듈 내 코드값 직접 정의 없음 확인 |
| AC-D5-006 | Soft loop 1회 자동, Hard loop 승인 필요 | T-U-D5-006 | `test_soft_loop_auto_retry` | Verify 실패 1회 -> 자동 재시도 |
| AC-D5-006 | (Hard loop) | T-U-D5-007 | `test_hard_loop_requires_approval` | Verify 실패 2회 이상 -> 승인 대기, 자동 실행 차단 |
| AC-D5-007 | Registry 표현 형식은 JSON 확정 | T-U-D5-008 | `test_registry_json_format` | VerifyChainRegistry가 JSON 형식으로 저장/로드 |
| AC-D5-008 | AgentMarketplace: verified+sandbox 필수 | T-U-D5-009 | `test_marketplace_verified_sandbox` | verified=false -> 실행 거부, sandbox_required=false -> 실행 거부 |
| AC-D5-009 | CircuitBreaker open 시 호출 차단 | T-U-D5-010 | `test_circuit_breaker_open_blocks` | state=open, recovery_time 미경과 -> 호출 차단 |
| AC-D5-009 | (recovery) | T-U-D5-011 | `test_circuit_breaker_half_open` | recovery_time 경과 -> half_open -> 시험 호출 |
| AC-D5-010 | GatePipelineMapping 모든 stage 최소 1Gate | T-U-D5-012 | `test_gate_pipeline_min_one_gate` | 5단계 각각에 required_gates 최소 1개 존재 |
| AC-D5-011 | HITLRequest.autonomy_level L0~L3만 | T-U-D5-013 | `test_hitl_autonomy_level_enum` | L0/L1/L2/L3만 허용, L4 등 거부 |

### 5.5 D6 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D6-001 | D6 모든 스키마는 D1 Meta Template _meta 포함 | T-U-D6-001 | `test_d6_schemas_meta_template` | MemoryRecord/SourceQoD/VectorStoreAdapter/GraphRAGConfig/SemanticCache의 _meta 검증 |
| AC-D6-002 | MemoryRecordSchema.scope는 L0~L3만 | T-U-D6-002 | `test_memory_scope_enum` | L0/L1/L2/L3 허용, L4/L5 등 거부 |
| AC-D6-003 | MemoryRecordSchema.memory_type은 B-1~B-4만 | T-U-D6-003 | `test_memory_type_enum` | B-1/B-2/B-3/B-4 허용, B-5 등 거부 |
| AC-D6-004 | policy_decision은 allow/restrict/deny, D7 정합 | T-U-D6-004 | `test_policy_decision_d7_alignment` | allow/restrict/deny만 허용, D7 PolicyCheckSchema.decision과 값 집합 일치 |
| AC-D6-005 | Example JSON에 MemoryRecord 2개 + SourceQoD 1개 | T-U-D6-005 | `test_example_json_presence` | D6 문서/fixtures에 최소 3개 Example JSON 존재 확인 |
| AC-D6-006 | L3/B-2 절차 메모리 확장 필드 | T-U-D6-006 | `test_l3_b2_procedural_memory` | L3/B-2 인스턴스에 procedure_id 등 확장 필드 선택 포함 가능 |
| AC-D6-007 | Failure/Fallback 코드값은 02 REF-only | T-U-D6-007 | `test_d6_ref_only_registries` | D6 모듈 내 코드값 직접 정의 없음 확인 |
| AC-D6-008 | VectorStore backend 전환 시 인터페이스 무변경 | T-U-D6-008 | `test_vector_store_adapter_interface` | Chroma/Qdrant 어댑터가 동일 인터페이스(add/search/delete) 구현 |
| AC-D6-008 | (통합) | T-I-STOR-004 | `test_chroma_to_qdrant_migration` | Chroma -> Qdrant 전환 후 동일 쿼리 결과 |
| AC-D6-009 | GraphRAG scope: V1=P1, V2+=FULL | T-U-D6-009 | `test_graph_rag_scope_by_version` | V1 config에서 scope="P1", V2 config에서 scope="FULL" |
| AC-D6-010 | SemanticCache similarity_threshold >= 0.95 LOCK | T-U-D6-010 | `test_semantic_cache_threshold_lock` | threshold=0.94 -> ValidationError, threshold=0.95 -> 성공 |

### 5.6 D7 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D7-001 | D7 모든 스키마는 D1 Meta Template _meta 포함 | T-U-D7-001 | `test_d7_schemas_meta_template` | PolicyCheck/Approval/CostBudget/Downshift/Guardrails/RBAC/Autonomy의 _meta 검증 |
| AC-D7-002 | 스키마 필드는 07 derived view 범위 내에서만 정의 | T-U-D7-002 | `test_d7_fields_design_scope` | 스키마 필드 목록이 07 DESIGN §6.2~6.4, §4.1~4.2와 일치 |
| AC-D7-003 | Example JSON 스키마별 최소 1개 (총 4개+) | T-U-D7-003 | `test_d7_example_json_count` | D7 fixtures에 PolicyCheck/Approval/CostBudget/Downshift Example 최소 4개 |
| AC-D7-004 | 코드값 목록은 02 REF-only | T-U-D7-004 | `test_d7_ref_only_registries` | D7 모듈 내 event_type/failure_code/fallback_id 직접 정의 없음 |
| AC-D7-005 | Guardrails 3-Layer 모두 통과 시만 allow | T-U-D7-005 | `test_guardrails_all_pass_allow` | L1+L2+L3 모두 pass -> overall_decision="allow" |
| AC-D7-005 | (일부 실패) | T-U-D7-006 | `test_guardrails_partial_fail` | L1 pass, L2 fail -> overall_decision="deny" 또는 "restrict" |
| AC-D7-006 | RBAC role은 OWNER/ADMIN/OPERATOR/VIEWER 4개만 | T-U-D7-007 | `test_rbac_role_enum_only_4` | OWNER/ADMIN/OPERATOR/VIEWER 허용, SUPERADMIN 등 거부 |
| AC-D7-007 | Autonomy level은 L0~L3만, L2/L3만 auto_execute | T-U-D7-008 | `test_autonomy_level_enum` | L0~L3 허용, L4 거부 |
| AC-D7-007 | (auto_execute) | T-U-D7-009 | `test_autonomy_auto_execute_restriction` | L0+auto_execute=true -> 거부, L2+auto_execute=true -> 허용 |

### 5.7 D8 AC -> 테스트 케이스

| AC ID | AC 설명 | 테스트 ID | 테스트 설명 | 검증 방법 |
|-------|---------|----------|-----------|----------|
| AC-D8-001 | D8은 SOT 스키마를 소유하지 않음 | T-U-D8-001 | `test_d8_no_sot_schema` | D8 관련 디렉토리에 SOT 스키마 클래스 없음 확인 (코드 검사) |
| AC-D8-002 | D8은 코드값 목록 미정의 (REF-only) | T-U-D8-002 | `test_d8_no_code_value_definition` | D8 모듈에서 event_type/failure_code/fallback_id 정의 없음 |
| AC-D8-003 | UI 메시지 매핑 규칙은 08 DESIGN §7 정합 | T-U-D8-003 | `test_ui_message_mapping_alignment` | UI 컴포넌트의 메시지 매핑이 08 DESIGN §7 규칙과 일치 |
| AC-D8-004 | V1 데스크톱 UI는 Tauri 2.0 + React | T-U-D8-004 | `test_tauri_react_integration` | Tauri 2.0 IPC invoke 호출 성공, React 컴포넌트 렌더링 |
| AC-D8-004 | (빌드 검증) | T-E-D8-001 | `test_tauri_build_success` | `cargo tauri build` 성공 확인 |
| AC-D8-005 | UI 메시지 확장 매핑은 D5/D6/D7 신규 스키마 정합 | T-U-D8-005 | `test_ui_extension_mapping_d5d6d7` | CircuitBreaker/SemanticCache/Guardrails 등의 UI 메시지가 해당 스키마 필드와 매핑 |
| AC-D8-005 | (E2E 검증) | T-E-D8-002 | `test_ui_displays_all_schema_states` | E2E에서 각 스키마 상태(deny/restrict/open/hit 등)의 UI 표시 확인 |

---

## 6. 테스트 도구 / 인프라

### 6.1 도구 스택

| 계층 | 도구 | 버전 | 용도 |
|------|------|------|------|
| Python 단위/통합 | **pytest** | >= 8.0 | 테스트 실행, fixture, parametrize |
| Python 커버리지 | **pytest-cov** | >= 5.0 | 커버리지 측정/리포트 |
| Python 비동기 | **pytest-asyncio** | >= 0.24 | async 테스트 지원 |
| Python Mock | **pytest-mock** / **unittest.mock** | -- | 외부 의존성 모킹 |
| Python Pydantic | **pydantic** | >= 2.0 | 스키마 검증 테스트 |
| Rust | **cargo test** | Rust stable | Rust 단위 테스트 |
| React | **vitest** | >= 2.0 | React 컴포넌트/훅 테스트 |
| React 컴포넌트 | **@testing-library/react** | >= 16.0 | DOM 렌더링 테스트 |
| E2E | **Playwright** | >= 1.45 | 브라우저 자동화 |
| E2E Tauri | **tauri-driver** | >= 2.0 | Tauri WebDriver 통합 |
| CI/CD | **GitHub Actions** | -- | 자동 테스트 실행 |
| Linting | **ruff** | >= 0.5 | Python 린팅/포매팅 |

### 6.2 pytest fixture 전략 (conftest.py 구조)

```
tests/
  conftest.py                       # 최상위: 공통 fixture
  unit/
    conftest.py                     # 단위 테스트 공통 fixture
    schemas/
      conftest.py                   # 스키마 테스트 fixture
    orange_core/
      conftest.py                   # ORANGE CORE fixture
    blue_nodes/
      conftest.py                   # BLUE NODES fixture
    safety/
      conftest.py                   # Safety fixture
    storage/
      conftest.py                   # Storage fixture
    agent/
      conftest.py                   # Agent fixture
  integration/
    conftest.py                     # 통합 테스트 공통 fixture
  e2e/
    conftest.py                     # E2E fixture (Tauri 앱)
```

#### 최상위 conftest.py

```python
# tests/conftest.py
import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """프로젝트 루트 경로."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """테스트 데이터 디렉토리."""
    d = project_root / "tests" / "data"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """테스트 환경 변수 설정 (실제 API 키 사용 금지)."""
    monkeypatch.setenv("VAMOS_VERSION_TIER", "V1")
    monkeypatch.setenv("VAMOS_DATA_DIR", "./test_data")
    monkeypatch.setenv("VAMOS_ENV", "test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-mock-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-mock-key")
```

#### 스키마 테스트 conftest.py

```python
# tests/unit/schemas/conftest.py
import pytest


@pytest.fixture
def valid_decision_fixture():
    """유효한 DecisionSchema 인스턴스 데이터."""
    return {
        "decision_id": "dec_01HZX9R1ABCDE",
        "trace_id": "trc_01HZX9R1ABCDE",
        "timestamp": "2026-01-15T20:17:00+09:00",
        "intent_frame_ref": "if_01HZX9R1ABCDE",
        "evidence_pack_ref": "evp_01HZX9R1ABCDE",
        "policy_gate": "allow",
        "approval_required": False,
        "approval_status": "approved",
        "cost_gate": "normal",
        "routing": {
            "selected_blue_node_id": "bn_analysis",
            "execution_mode": "main"
        },
        "memory_plan": {
            "save_candidate": True,
            "target_layer": "L1",
            "requires_user_approval": False
        },
        "output_spec": {"format_constraints": "markdown"},
        "conclusion": "ACCEPT",
        "locked": True,
    }


@pytest.fixture
def valid_memory_record_fixture():
    """유효한 MemoryRecordSchema 인스턴스 데이터."""
    return {
        "record_id": "rec_01",
        "project_id": "proj_01",
        "scope": "L1",
        "memory_type": "B-1",
        "content_summary": "프로젝트 목표 요약",
        "created_at": "2026-01-17T10:30:00Z",
        "policy_decision": "allow",
    }


@pytest.fixture
def valid_policy_check_fixture():
    """유효한 PolicyCheckSchema 인스턴스 데이터."""
    return {
        "check_id": "chk_001",
        "decision": "allow",
        "reasons": ["No sensitive content detected"],
        "rule_refs": ["RULE 1.3 §7.3"],
        "detected_sensitive_types": [],
    }


@pytest.fixture
def valid_node_request_fixture():
    """유효한 NodeRequestEnvelopeSchema 인스턴스 데이터 (7필드)."""
    return {
        "request_id": "req_01",
        "project_id": "proj_01",
        "session_id": "sess_01",
        "node_id": "bn_web_research",
        "intent_summary": "주식 시장 동향 조사",
        "constraints": {"max_sources": 5},
        "trace_id": "trc_01",
    }


@pytest.fixture
def valid_workflow_output_fixture():
    """유효한 WorkflowOutputEnvelopeSchema 인스턴스 데이터 (3단 출력)."""
    return {
        "trace_id": "trc_01",
        "user_response": "분석 결과입니다...",
        "evidence_summary": "근거 요약...",
        "log_report": {"events": [], "total_cost": 150},
    }


@pytest.fixture
def valid_cost_budget_fixture():
    """유효한 CostBudgetSchema 인스턴스 데이터."""
    return {
        "budget_id": "bud_01",
        "daily_limit": 1300,
        "monthly_limit": 40000,
        "daily_used": 500,
        "monthly_used": 12000,
        "currency": "KRW",
    }


@pytest.fixture
def valid_guardrails_check_fixture():
    """유효한 GuardrailsCheckSchema 인스턴스 데이터."""
    return {
        "check_id": "gc_001",
        "layer1_result": {"passed": True, "provider": "nemo"},
        "layer2_result": {"passed": True, "provider": "guardrails_ai"},
        "layer3_result": {"passed": True, "provider": "llamaguard"},
        "overall_decision": "allow",
    }
```

#### Storage 테스트 conftest.py

```python
# tests/unit/storage/conftest.py
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_chroma_dir():
    """임시 Chroma 영속 디렉토리."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def temp_sqlite_db():
    """임시 SQLite DB 파일."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)


@pytest.fixture
def temp_graph_json():
    """임시 JSON Graph 파일."""
    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False, mode="w"
    ) as f:
        f.write('{"nodes":[],"edges":[]}')
        yield Path(f.name)
```

### 6.3 테스트 실행 명령어

```bash
# --- Python 단위 테스트 ---
pytest tests/unit/ -v --cov=vamos --cov-report=html --cov-report=term-missing

# --- Python 통합 테스트 ---
pytest tests/integration/ -v --timeout=60

# --- Python 전체 ---
pytest tests/ -v --cov=vamos --cov-report=html

# --- Rust 단위 테스트 ---
cd src-tauri && cargo test

# --- React 단위 테스트 ---
npx vitest run --coverage

# --- E2E 테스트 ---
pytest tests/e2e/ -v --timeout=120

# --- 린팅 ---
ruff check vamos/ tests/
ruff format --check vamos/ tests/
```

### 6.4 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: VAMOS Test Suite
on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v --cov=vamos --cov-report=xml
      - run: pytest tests/integration/ -v --timeout=60
      - uses: codecov/codecov-action@v4

  rust-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cd src-tauri && cargo test

  react-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx vitest run --coverage

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check vamos/ tests/
      - run: ruff format --check vamos/ tests/
```

---

## 7. 커버리지 목표

### 7.1 목표 요약

| 계층 | 커버리지 목표 | 측정 도구 | 비고 |
|------|-------------|----------|------|
| **단위 테스트 (Python)** | **80%+** (라인 커버리지) | pytest-cov | schemas/, orange_core/, blue_nodes/, safety/, storage/, agent/ |
| **단위 테스트 (Rust)** | **80%+** | cargo-tarpaulin | IPC command handler, subprocess 관리 |
| **단위 테스트 (React)** | **80%+** | vitest + @vitest/coverage-v8 | 컴포넌트, Store/Hook |
| **통합 테스트** | **60%+** (경로 커버리지) | pytest-cov | IPC 통합, Pipeline, Storage, Safety |
| **E2E 테스트** | 핵심 시나리오 **100%** | Playwright report | 8개 핵심 시나리오 전체 통과 |

### 7.2 모듈별 최소 커버리지

| 모듈 | 최소 커버리지 | 근거 |
|------|-------------|------|
| `schemas/` | **95%** | 모든 Pydantic 모델은 유효/무효 케이스 필수 |
| `safety/` | **90%** | 보안/비용/승인은 높은 신뢰도 필수 |
| `orange_core/` | **85%** | Decision Kernel은 핵심 로직 |
| `blue_nodes/` | **80%** | Node 실행 로직 |
| `storage/` | **80%** | 데이터 영속성 |
| `agent/` | **80%** | LangGraph 워크플로우 |
| `ui/` (React) | **75%** | UI 컴포넌트 |
| `src-tauri/` (Rust) | **80%** | IPC 핸들러 |

### 7.3 AC 커버리지 매트릭스 요약

| 문서 | AC 수 | 단위 테스트 수 | 통합 테스트 수 | E2E 테스트 수 | 총 테스트 수 |
|------|------|-------------|-------------|-------------|-------------|
| D2 | 3 | 9 | 0 | 0 | 9 |
| D3 | 8 | 8 | 0 | 1 | 9 |
| D4 | 6 | 6 | 1 | 0 | 7 |
| D5 | 11 | 13 | 5 | 1 | 19 |
| D6 | 10 | 10 | 3 | 0 | 13 |
| D7 | 7 | 9 | 5 | 1 | 15 |
| D8 | 5 | 5 | 0 | 2 | 7 |
| **합계** | **50** | **60** | **14** | **5** | **79** |

> 모든 50개 AC는 최소 1개 이상의 테스트 케이스에 매핑되어 있다.

---

## 8. 문서 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-22 | Phase B5 초판. 테스트 피라미드(단위/통합/E2E), pytest fixture 전략, D2~D8 전체 50개 AC 테스트 매핑(79개 테스트 케이스), 커버리지 목표(단위 80%+, 통합 60%+, E2E 핵심 100%), CI/CD 파이프라인 정의. |

---

---

<\!-- END OF DOCUMENT -->
