---
session: 28
sections: [37, 38]
status: complete
---

# §37. 테스트 전략 (~128개 테스트) (Test Strategy)

> **비유**: VAMOS의 테스트는 **건물 검사**와 같습니다. 집을 지을 때 기초 공사(벽돌 하나하나) → 구조 점검(벽과 기둥이 연결되었는지) → 완성 후 입주 테스트(수도/전기가 실제로 작동하는지)를 순서대로 확인하듯, 소프트웨어도 **작은 부품부터 전체 시나리오까지** 단계별로 검사합니다. 이것을 **테스트 피라미드(Test Pyramid)**라고 부릅니다.

---

## §37.1 테스트 피라미드 (Unit / Integration / E2E)

### 테스트 피라미드란?

테스트를 **3개 층**으로 나누어 아래에서 위로 쌓아가는 구조입니다. 아래층일수록 **빠르고 많이**, 위층일수록 **느리지만 실제 사용자 관점**에서 검증합니다. [근거: B5 §1.1]

```
        /    E2E     \         ← 핵심 시나리오 100% (완성 검사)
       /  통합 테스트   \       ← 60%+ 커버리지 (구조 검사)
      /   단위 테스트    \     ← 80%+ 커버리지 (기초 검사)
     ----------------------
```

### 3개 계층 비교표

| 계층 | 비유 | 범위 | 도구 | 커버리지 목표 | 속도 |
|------|------|------|------|-------------|------|
| **단위 테스트 (Unit Test)** | 벽돌 하나하나 검사 | 함수/클래스/모듈 개별 검증 | pytest (Python), cargo test (Rust), vitest (React) | **80%+** | 빠름 (초 단위) |
| **통합 테스트 (Integration Test)** | 벽과 기둥 연결 검사 | 모듈 간 인터페이스, 파이프라인 흐름 | pytest + subprocess, Docker Compose | **60%+** | 보통 (분 단위) |
| **E2E 테스트 (End-to-End Test)** | 입주 후 전체 작동 확인 | 사용자 시나리오 전체 흐름 | Tauri WebDriver + Playwright | 핵심 시나리오 **100%** | 느림 (분~십분) |

[근거: B5 §1.1]

### 테스트 원칙 5가지

| # | 원칙 | 설명 |
|---|------|------|
| 1 | **AC 완전 매핑** | D2~D8의 모든 AC(인수 기준)는 최소 1개 이상의 테스트에 연결 |
| 2 | **스키마 우선 검증** | Pydantic v2 모델은 유효/무효 인스턴스 모두 테스트 |
| 3 | **비밀 분리** | 테스트 환경에서 실제 API 키 사용 금지, mock/fixture로 대체 |
| 4 | **재현 가능성** | 모든 테스트는 CI/CD에서 독립 실행 가능 |
| 5 | **실패 추적** | 테스트 실패 시 관련 AC ID와 스키마 REF를 로그에 기록 |

[근거: B5 §1.2]

### 테스트 ID 규칙

테스트 이름은 **"T-{계층}-{문서ID}-{순번}"** 형식을 따릅니다. [근거: B5 §1.3]

```
T-U-D2-001   →  단위(U) 테스트, D2 문서 관련, 첫 번째
T-I-SYS-003  →  통합(I) 테스트, 시스템 전반(SYS), 세 번째
T-E-SYS-001  →  E2E(E) 테스트, 시스템 전반, 첫 번째
```

**핵심 요약 (3줄)**
1. 테스트 피라미드는 단위(80%+) → 통합(60%+) → E2E(핵심 100%) 3개 층 구조입니다.
2. 모든 테스트는 AC에 매핑되어야 하며, 실제 API 키는 사용하지 않습니다.
3. 테스트 ID는 `T-{계층}-{문서ID}-{순번}` 형식을 따릅니다.

---

## §37.2 V0~V1 기본 테스트 (~85개)

> **비유**: 집의 **기초 공사와 골조**를 검사하는 단계입니다. 가장 핵심적인 CORE 모듈들이 제대로 작동하는지, 모듈끼리 연결이 잘 되는지를 확인합니다. V0(프로토타입)~V1(로컬 MVP)에서 반드시 통과해야 하는 기본 테스트입니다.

### 단위 테스트 — Python (pytest) 모듈별 분류

#### (1) 스키마 검증 테스트 (`schemas/`) — 약 10개 파일

모든 Pydantic v2 모델의 유효/무효 인스턴스를 검증합니다. [근거: B5 §2.1.1]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_decision_schema.py` | DecisionSchema (결정 스키마) | AC-D2-001, AC-D2-003 |
| `test_log_event_schema.py` | LogEventSchema (로그 이벤트 스키마) | AC-D2-001 |
| `test_node_schemas.py` | NodeCapabilityProfile, Request/Response Envelope | AC-D3-002, AC-D3-004, AC-D3-005 |
| `test_tool_schemas.py` | ToolRegistryEntry, BrainAdapterResponse | AC-D4-002, AC-D4-005 |
| `test_workflow_schemas.py` | WorkflowOutputEnvelope, FailureReport, VerifyChainEntry | AC-D5-002, AC-D5-003 |
| `test_agent_schemas.py` | AgentMarketplace, CircuitBreaker, GatePipelineMapping, HITL | AC-D5-008~011 |
| `test_memory_schemas.py` | MemoryRecord, SourceQoD, VectorStoreAdapter | AC-D6-001~003 |
| `test_graph_cache_schemas.py` | GraphRAGConfig, SemanticCache | AC-D6-009, AC-D6-010 |
| `test_safety_schemas.py` | PolicyCheck, Approval, CostBudget, Downshift | AC-D7-001 |
| `test_guardrails_schema.py` | GuardrailsCheck, RBACRole, AutonomyLevel | AC-D7-005~007 |
| `test_config_model.py` | VamosConfig (config.toml 검증) | B4 Config Spec |

#### (2) ORANGE CORE 테스트 (`orange_core/`) — 6개 파일

두뇌(ORANGE CORE)의 핵심 로직을 검증합니다. [근거: B5 §2.1.2]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_decision_kernel.py` | Decision 생성/잠금/단일결정 원칙 | AC-D2-001, AC-D2-003 |
| `test_intent_parser.py` | IntentFrame (의도 프레임) 생성, 필수 필드 | D2 intent_frame_ref |
| `test_evidence_collector.py` | EvidencePack (근거 묶음) 수집, QoD (품질 점수) 산출 | D2 evidence_pack_ref |
| `test_event_registry.py` | EventTypeRegistry (이벤트 유형 등록부) SOT 검증 | AC-D2-002 |
| `test_failure_registry.py` | FailureCodeRegistry (에러코드 등록부) SOT 검증 | AC-D2-002 |
| `test_fallback_registry.py` | FallbackRegistry (비상대처 등록부) SOT 검증 | AC-D2-002 |

#### (3) BLUE NODES 테스트 (`blue_nodes/`) — 6개 파일

실행 노드(BLUE NODE)의 요청/응답/도구 호출을 검증합니다. [근거: B5 §2.1.3]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_node_registry.py` | NodeRegistry D3 SOT 단일 확정 | AC-D3-001 |
| `test_node_executor.py` | Node 실행/라우팅 | D3 |
| `test_request_envelope.py` | NodeRequestEnvelope 7필드 필수 | AC-D3-004 |
| `test_response_envelope.py` | NodeResponseEnvelope 최소 필드 | AC-D3-005 |
| `test_tool_call_registry.py` | ToolCallRegistry.tool_id와 D4 ToolRegistry 정합 | AC-D3-007 |
| `test_mcp_bridge.py` | MCPBridgeLayer transport가 `streamable_http`만 허용 | AC-D3-008 |

#### (4) Safety 테스트 (`safety/`) — 7개 파일

보안/비용/승인 관련 모듈을 검증합니다. [근거: B5 §2.1.4]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_policy_check.py` | deny/restrict/allow 판정 | AC-D7-002 |
| `test_approval.py` | Approval (승인) 요청/응답/상태 | D7 |
| `test_cost_budget.py` | 일일/월간 예산 한도, warn/block 임계값 | D7 CostBudgetSchema |
| `test_downshift.py` | 80% → force_mini(강제 경량 모델), 100% → block(차단) | D7 DownshiftSchema |
| `test_guardrails.py` | 4-Layer Guardrails (L1~L3 실시간) 보호벽 모두 pass 시 allow, 하나라도 fail 시 deny/restrict | AC-D7-005 |
| `test_rbac.py` | OWNER/ADMIN/OPERATOR/VIEWER 4역할만 허용 | AC-D7-006 |
| `test_autonomy.py` | L0~L3만 허용, L2/L3에서만 auto_execute=true | AC-D7-007 |

#### (5) Storage 테스트 (`storage/`) — 5개 파일

기억 저장소(Memory, VectorStore, SemanticCache) 검증. [근거: B5 §2.1.5]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_memory_record.py` | scope L0~L3만, memory_type B-1~B-4만 허용 | AC-D6-002, AC-D6-003 |
| `test_vector_store.py` | backend 전환(chroma→qdrant) 시 인터페이스 무변경 | AC-D6-008 |
| `test_semantic_cache.py` | similarity_threshold ≥ 0.95 **LOCK** 🔒 변경 불가 | AC-D6-010 |
| `test_graph_rag.py` | scope: V1=P1 / V2+=FULL | AC-D6-009 |
| `test_source_qod.py` | SourceQoD (출처 품질) 점수 산출 | D6 |

#### (6) Agent/Workflow 테스트 (`agent/`) — 10개 파일

LangGraph 워크플로우 파이프라인 검증. [근거: B5 §2.1.6]

| 테스트 파일 | 검증 대상 | 관련 AC |
|-----------|----------|---------|
| `test_state_graph.py` | LangGraph StateGraph 구성 | D5 |
| `test_pipeline_stages.py` | 5단계 Pipeline (Intake→Deliver) | D5 |
| `test_workflow_output.py` | 3단 출력 (user_response / evidence_summary / log_report) 필수 | AC-D5-003 |
| `test_verify_chain.py` | VerifyChainEntry evx_id는 EVX-1~6 또는 self_check/evidence_check만 | AC-D5-004 |
| `test_failure_report.py` | FailureReport 생성 | D5 |
| `test_circuit_breaker.py` | state=open 시 recovery_time 전 호출 차단 | AC-D5-009 |
| `test_gate_pipeline.py` | 모든 stage에 최소 1개 필수 Gate (관문) | AC-D5-010 |
| `test_hitl_request.py` | HITLRequest autonomy_level L0~L3만 | AC-D5-011 |
| `test_agent_marketplace.py` | verified=true + sandbox_required=true일 때만 실행 | AC-D5-008 |
| `test_loop_control.py` | Soft loop 1회 자동, Hard loop 승인 필요 | AC-D5-006 |

### 단위 테스트 — Rust (cargo test) — 8개

Tauri IPC(프로세스 간 통신) 핸들러를 검증합니다. [근거: B5 §2.2]

| 테스트 ID | 검증 대상 | 설명 |
|----------|----------|------|
| T-U-RUST-001 | `invoke_python_agent` | Tauri IPC → Python 호출 정상 동작 |
| T-U-RUST-002 | `handle_ipc_error` | Python 에러 시 Rust 에러 핸들링 |
| T-U-RUST-003 | `serialize_response` | IPC 응답 JSON 직렬화 정합성 |
| T-U-RUST-004 | `config_load` | config.toml 로딩 및 구조체 매핑 |
| T-U-RUST-005 | `spawn_python` | Python 프로세스 정상 생성/종료 |
| T-U-RUST-006 | `python_health_check` | Python 프로세스 상태 확인 |
| T-U-RUST-007 | `python_restart` | 비정상 종료 시 자동 재시작 |
| T-U-RUST-008 | `stdin_stdout_pipe` | stdin/stdout 파이프 데이터 전송 |

### 단위 테스트 — React (vitest) — 약 9개

UI 컴포넌트와 상태 관리 훅(Hook)을 검증합니다. [근거: B5 §2.3]

| 테스트 ID | 검증 대상 | 관련 AC |
|----------|----------|---------|
| T-U-UI-001 | ChatPanel 메시지 렌더링 | AC-D8-003 |
| T-U-UI-002 | CostDashboard 일일/월간 한도 표시 | AC-D8-005 |
| T-U-UI-003 | ApprovalDialog HITL 승인 요청 표시 | AC-D8-005 |
| T-U-UI-004 | GuardrailsAlert deny/restrict 상태 표시 | AC-D8-005 |
| T-U-UI-005 | Tauri 2.0 IPC invoke 호출 정합성 | AC-D8-004 |
| T-U-UI-006 | useAgentStore 상태 전이 (idle→running→completed) | D8 |
| T-U-UI-007 | useCostStore 비용 누적/경고 상태 | D8 |
| T-U-UI-008 | useIPC Tauri invoke 호출/응답 처리 | D8 |
| T-U-UI-009 | useStreaming 스트리밍 데이터 처리 | D8 |

### 통합 테스트 — 23개

모듈 간 연결을 검증합니다. [근거: B5 §3]

| 카테고리 | 테스트 수 | 주요 검증 내용 |
|---------|----------|--------------|
| **IPC 통합** (Python ↔ Rust) | 4개 | 요청/응답 라운드트립, 에러 전파, 타임아웃, trace_id 전파 |
| **Pipeline 통합** (Intake→Deliver) | 7개 | 정상 흐름 5단계 통과, Gate 차단, Soft/Hard loop, CircuitBreaker, 다운시프트, Decision→Node 연결 |
| **Storage 통합** (Memory+Vector+Cache) | 6개 | MemoryRecord CRUD, VectorStore 검색, SemanticCache 히트/미스, Chroma→Qdrant 전환, GraphRAG 쿼리, TTL 만료 |
| **Safety 통합** (PolicyCheck→Approval→CostBudget) | 6개 | PolicyCheck→Approval 연결, CostBudget→Downshift 연결, L1~L3 Guardrails 순차 검사, RBAC 권한, Autonomy 승인 흐름, ToolRegistry 경유 필수 |

### E2E 테스트 — 8개

실제 사용자 시나리오를 처음부터 끝까지 검증합니다. [근거: B5 §4]

| 테스트 ID | 시나리오 | 관련 AC |
|----------|---------|---------|
| T-E-SYS-001 | **기본 채팅**: 질문 입력 → AI 응답 수신 (3단 출력 확인) | AC-D5-003, AC-D8-003 |
| T-E-SYS-002 | **비용 80% 다운시프트**: 반복 요청 → mini 모델 전환 | D7 DownshiftSchema |
| T-E-SYS-003 | **비용 100% 차단**: 100% 도달 → 요청 차단 | D7 DownshiftSchema |
| T-E-SYS-004 | **HITL 승인 흐름**: 승인 대화상자 → 승인/거부 | AC-D5-011, AC-D7-007 |
| T-E-SYS-005 | **Guardrails 차단**: PII 포함 입력 → deny → 에러 메시지 | AC-D7-005 |
| T-E-SYS-006 | **Node 에러 복구**: BLUE NODE 에러 → fallback 동작 | D2 FallbackRegistry |
| T-E-SYS-007 | **MCP 브릿지 호출**: 웹 검색 → MCP 경유 → 결과 표시 | AC-D3-008 |
| T-E-SYS-008 | **설정 변경 반영**: config 변경 → 앱 재시작 → 적용 확인 | B4 Config Spec |

**핵심 요약 (3줄)**
1. V0~V1 기본 테스트는 Python(~44개 파일) + Rust(8개) + React(9개) + 통합(23개) + E2E(8개)이며, 이 중 Storage 통합(6개)은 V2+에서 활성화됩니다.
2. 스키마/ORANGE CORE/BLUE NODES/Safety/Storage/Agent 6개 영역을 모두 커버합니다.
3. 통합 테스트는 IPC/Pipeline/Storage/Safety 4개 카테고리로 모듈 간 연결을 검증합니다.

---

## §37.3 V2 COND 모듈 테스트 (~30개)

> **비유**: 집에 **에어컨, 난방, 보안 시스템** 같은 조건부 설비를 추가한 뒤, 조건이 맞을 때만 (여름에 에어컨, 겨울에 난방) 정확히 작동하는지 검사하는 단계입니다. V2에서 활성화되는 **조건부(COND) 모듈**들을 테스트합니다.

### V2에서 추가/확장되는 테스트 영역

| 영역 | 추가 테스트 | 설명 |
|------|-----------|------|
| **Docker 배포 통합** | ~5개 | Docker Compose 기반 서비스 간 통합 테스트 |
| **VectorStore 전환** | ~3개 | Chroma → Qdrant 실제 전환 후 정합성 검증 |
| **GraphRAG 확장** | ~3개 | scope P1 → FULL 확장, Neo4j 연동 |
| **API Gateway** | ~5개 | REST API 엔드포인트 검증 |
| **다중 사용자** | ~4개 | RBAC 기반 동시 접근, 권한 분리 검증 |
| **성능 벤치마크** | ~5개 | 응답 시간, 메모리, 토큰 처리량 기준치 검증 |
| **보안 강화** | ~5개 | SAST 결과 반영, 의존성 취약점 자동 차단 |

### 버전별 테스트 활성 여부

| 테스트 카테고리 | V0 | V1 | V2 | V3 |
|---------------|----|----|----|----|
| 스키마 검증 (Unit) | ✅ | ✅ | ✅ | ✅ |
| ORANGE CORE (Unit) | ✅ | ✅ | ✅ | ✅ |
| BLUE NODES (Unit) | ❌ | ✅ | ✅ | ✅ |
| Safety (Unit) | ✅ | ✅ | ✅ | ✅ |
| Storage (Unit) | ❌ | ✅ | ✅ | ✅ |
| Agent/Workflow (Unit) | ❌ | ✅ | ✅ | ✅ |
| Rust IPC (Unit) | ❌ | ✅ | ✅ | ✅ |
| React UI (Unit) | ❌ | ✅ | ✅ | ✅ |
| IPC 통합 | ❌ | ✅ | ✅ | ✅ |
| Pipeline 통합 | ❌ | ✅ | ✅ | ✅ |
| Storage 통합 | ❌ | ❌ | ✅ | ✅ |
| Docker 배포 통합 | ❌ | ❌ | ✅ | ✅ |
| API Gateway 통합 | ❌ | ❌ | ✅ | ✅ |
| E2E 시나리오 | ❌ | ✅ (기본) | ✅ (확장) | ✅ (전체) |
| 성능 벤치마크 | ❌ | ❌ | ✅ | ✅ |
| 나이틀리 전체 스위트 | ❌ | ❌ | ❌ | ✅ |

[근거: B5 §2~§4, B6 §1.1]

**핵심 요약 (3줄)**
1. V2에서는 Docker 배포, VectorStore 전환, GraphRAG 확장, API Gateway 등 ~30개 조건부 테스트가 추가됩니다.
2. Storage 통합, Docker 배포 통합, API Gateway 통합은 V2부터 활성화됩니다.
3. 성능 벤치마크도 V2부터 시작되어 응답 시간/메모리/토큰 처리량을 측정합니다.

---

## §37.4 V3 EXP 모듈 테스트 (~13개)

> **비유**: 건물에 **실험적인 스마트홈 기능**(음성 인식 조명, AI 온도 조절 등)을 시범 도입한 뒤, 안정성과 호환성을 검사하는 단계입니다. V3에서 실험적으로 추가되는 EXP 모듈들을 테스트합니다.

### V3에서 추가되는 실험 테스트

| 영역 | 추가 테스트 수 | 설명 |
|------|-------------|------|
| **K8s 배포 통합** | ~3개 | Helm Chart 배포, Blue-Green 전략, 자동 롤백 검증 |
| **나이틀리 전체 스위트** | ~3개 | 매일 새벽 전체 테스트 실행 (Unit + Integration + E2E + 성능) |
| **ArgoCD 자동 배포** | ~2개 | GitOps 기반 자동 배포 파이프라인 검증 |
| **고급 보안 스캔** | ~3개 | Snyk 통합, 컨테이너 이미지 취약점 스캔 (Trivy) |
| **멀티 리전 테스트** | ~2개 | 여러 지역 배포 시 데이터 정합성 검증 |

### 전체 테스트 수 요약 (버전별 누적)

| 버전 | 단위 | 통합 | E2E | 합계 (누적) |
|------|------|------|-----|------------|
| **V0~V1** | ~60 | ~17 | ~8 | **~85** |
| **V2** (+COND) | +15 | +10 | +5 | **~115** |
| **V3** (+EXP) | +5 | +5 | +3 | **~128** |

[근거: B5 §7.3, B6 §1.1]

**핵심 요약 (3줄)**
1. V3에서는 K8s 배포, 나이틀리 스위트, ArgoCD, 고급 보안 등 ~13개 실험 테스트가 추가됩니다.
2. 최종 누적 테스트 수는 약 128개(단위 ~80 + 통합 ~32 + E2E ~16)입니다.
3. 나이틀리(nightly) 테스트는 V3부터 매일 새벽 3시(UTC)에 전체 스위트를 자동 실행합니다.

---

## §37.5 AC 매핑 (50 AC → 79 테스트)

> **비유**: 건축 허가서에 적힌 **50개 검사 항목**(AC, Acceptance Criteria = 인수 기준)을 충족하는지 확인하기 위해, 각 항목에 맞는 **79개 검사 도구**를 배정하는 과정입니다. 하나의 검사 항목에 여러 도구가 배정될 수도 있습니다.

### AC 매핑 요약표

| 문서 | AC 수 | 단위 테스트 | 통합 테스트 | E2E 테스트 | 총 테스트 |
|------|------|-----------|-----------|-----------|----------|
| **D2** (Decision Kernel) | 3 | 9 | 0 | 0 | **9** |
| **D3** (Blue Nodes) | 8 | 8 | 0 | 1 | **9** |
| **D4** (Tool Registry) | 6 | 6 | 1 | 0 | **7** |
| **D5** (Workflow/Agent) | 11 | 13 | 5 | 1 | **19** |
| **D6** (Memory/Storage) | 10 | 10 | 3 | 0 | **13** |
| **D7** (Safety/Policy) | 7 | 9 | 5 | 1 | **15** |
| **D8** (UI/Frontend) | 5 | 5 | 0 | 2 | **7** |
| **합계** | **50** | **60** | **14** | **5** | **79** |

> 🔒 **LOCK**: 모든 50개 AC는 최소 1개 이상의 테스트 케이스에 매핑되어야 합니다. 매핑 없는 AC는 허용되지 않습니다. — 변경 불가 [근거: B5 §5, §1.2 원칙 1]

### D2 AC 매핑 상세

| AC ID | AC 설명 | 테스트 ID | 검증 방법 |
|-------|---------|----------|----------|
| AC-D2-001 | DecisionSchema의 `_meta` 필수 속성 포함 | T-U-D2-001, T-U-D2-002 | Pydantic 모델의 _meta 필드 존재 검증 |
| AC-D2-002 | Registry 값 목록은 D2 SOT에서만 확정 | T-U-D2-003~005 | EventType/FailureCode/Fallback Registry가 D2 정의와 일치 |
| AC-D2-003 | enum 필드는 DESIGN 정본과 정합 | T-U-D2-006~009 | policy_gate/approval_status/cost_gate/conclusion 값 검증 |

### D5 AC 매핑 상세 (가장 많은 19개 테스트)

| AC ID | AC 설명 | 테스트 수 | 주요 검증 |
|-------|---------|----------|----------|
| AC-D5-003 | WorkflowOutput 3필드 필수 산출 | 2개 (단위+통합) | user_response, evidence_summary, log_report 모두 non-null |
| AC-D5-006 | Soft loop 1회 자동, Hard loop 승인 필요 | 2개 | 재시도 횟수별 자동/승인 동작 검증 |
| AC-D5-008 | AgentMarketplace verified+sandbox 필수 | 1개 | 미검증 에이전트 실행 차단 |
| AC-D5-009 | CircuitBreaker open 시 차단 | 2개 | open→차단, recovery→half_open 검증 |
| AC-D5-010 | 모든 stage 최소 1개 Gate | 1개 | 5단계 각각 required_gates 존재 |
| AC-D5-011 | HITL autonomy L0~L3만 | 1개 | L4 등 비허용 값 거부 |

### D7 AC 매핑 상세 (보안 중심 15개 테스트)

| AC ID | AC 설명 | 테스트 수 | 주요 검증 |
|-------|---------|----------|----------|
| AC-D7-005 | 4-Layer Guardrails (L1~L3 실시간) 모두 통과 시 allow | 2개 (단위) + 1개 (통합) | 전체 pass=allow, 부분 fail=deny/restrict |
| AC-D7-006 | RBAC 4역할만 허용 | 1개 (단위) + 1개 (통합) | OWNER/ADMIN/OPERATOR/VIEWER 외 거부 |
| AC-D7-007 | Autonomy L0~L3, L2/L3만 auto_execute | 2개 (단위) + 1개 (통합) | 수준별 자동 실행 허용/차단 검증 |

[근거: B5 §5.1~§5.7]

**핵심 요약 (3줄)**
1. 50개 AC가 79개 테스트에 매핑되며, AC 매핑 없는 테스트는 존재하지 않습니다.
2. D5(Workflow/Agent)가 19개로 가장 많고, D7(Safety)이 15개로 두 번째입니다.
3. 단위 테스트(60개)가 전체의 76%를 차지하며, 테스트 피라미드 원칙에 부합합니다.

---

## §37.6 상세 테스트 케이스

> **비유**: 건물 검사에서 **구체적으로 무엇을 어떻게 검사하는지** 체크리스트를 작성하는 단계입니다. "벽 두께는 몇 cm인지 자로 재라", "수도꼭지를 3번 돌려서 물이 나오는지 확인하라" 같은 구체적인 지시사항입니다.

### T-VAL: 설정 검증 테스트 (Validation Tests)

> config.toml 설정 파일이 올바르게 로딩되고 검증되는지 확인합니다. [근거: B5 §2.1.1 `test_config_model.py`, B4 Config Spec]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-VAL-001 | VamosConfig 유효 인스턴스 생성 | 모든 필수 필드 정상 로드 |
| T-VAL-002 | 필수 필드 누락 시 거부 | ValidationError 발생 |
| T-VAL-003 | version_tier 값 검증 | V0/V1/V2/V3만 허용, V4 등 거부 |
| T-VAL-004 | Rust 측 config.toml 로딩 | Rust 구조체에 정확히 매핑 |

### T-SDAR: SDAR 자동수리 테스트 (Self-Diagnosis & Auto-Repair)

> 시스템이 스스로 문제를 감지하고 복구하는 기능을 검증합니다. [근거: B5 §2.1.6 `test_circuit_breaker.py`, `test_loop_control.py`]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-SDAR-001 | CircuitBreaker open 시 차단 | state=open → 호출 즉시 거부 |
| T-SDAR-002 | CircuitBreaker recovery → half_open | recovery_time 경과 → 시험 호출 허용 |
| T-SDAR-003 | Soft loop 1회 자동 재시도 | Verify 실패 → 1회 자동 재시도 후 성공 |
| T-SDAR-004 | Hard loop 승인 대기 | 2회 이상 실패 → HITL 승인 필요 |
| T-SDAR-005 | Python 프로세스 비정상 종료 시 재시작 | Rust 측에서 자동 재시작 (T-U-RUST-007) |

### T-HMAC: HMAC 인증 테스트

> 데이터 무결성(변조 방지)을 위한 인증 메커니즘을 검증합니다. [근거: B5 §2.1.4 `test_policy_check.py`]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-HMAC-001 | IPC 요청에 trace_id 포함 | trace_id가 Python까지 일관 전파 |
| T-HMAC-002 | 무결성 검증 실패 시 거부 | 변조된 요청 → PolicyCheck deny |
| T-HMAC-003 | Decision 잠금(locked=true) 후 변경 불가 | 잠긴 Decision 수정 시도 → 에러 |

### T-GUARD: Guardrails 테스트 (보호벽)

> 보호벽(4-Layer Guardrails, L1~L3 실시간 검사)이 올바르게 작동하는지 검증합니다. [근거: B5 §2.1.4 `test_guardrails.py`, §3.4]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-GUARD-001 | L1(NeMo) + L2(Guardrails AI) + L3(LlamaGuard) 전부 pass | overall_decision = "allow" |
| T-GUARD-002 | L1 pass, L2 fail | overall_decision = "deny" 또는 "restrict" |
| T-GUARD-003 | L1 fail (유해 콘텐츠 감지) | 즉시 deny, L2/L3 건너뜀 |
| T-GUARD-004 | 통합: L1→L2→L3 순차 검사 | 순서대로 실행, 결과 종합 |
| T-GUARD-005 | E2E: PII 포함 입력 → deny → UI 경고 표시 | GuardrailsAlert 컴포넌트에 경고 렌더링 |

### T-GDPR: 개인정보보호 테스트

> 개인정보(PII) 마스킹(가림 처리)과 정책 준수를 검증합니다. [근거: B5 §2.1.4 `test_policy_check.py`, §2.1.5 `test_memory_record.py`]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-GDPR-001 | PolicyCheck에서 PII 감지 시 restrict/deny | detected_sensitive_types 목록에 PII 포함 |
| T-GDPR-002 | Memory 저장 시 policy_decision 적용 | allow/restrict/deny가 MemoryRecord에 기록 |
| T-GDPR-003 | 출력 마스킹 적용 | 개인정보가 마스킹되어 사용자에게 전달 |

### T-AC: 접근제어 테스트 (Access Control)

> RBAC(역할 기반 접근 제어)와 Autonomy(자율성 수준) 검증. [근거: B5 §2.1.4 `test_rbac.py`, `test_autonomy.py`, §3.4]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-AC-001 | RBAC 4역할만 허용 | OWNER/ADMIN/OPERATOR/VIEWER만 허용, 기타 거부 |
| T-AC-002 | VIEWER는 실행 불가 | VIEWER 권한으로 Agent 실행 시도 → 차단 |
| T-AC-003 | OPERATOR는 실행 가능 | OPERATOR 권한으로 Agent 실행 → 성공 |
| T-AC-004 | Autonomy L0~L3만 허용 | L4 등 비허용 값 → ValidationError |
| T-AC-005 | L0/L1은 auto_execute=false | L0 + auto_execute=true → 거부 |
| T-AC-006 | L2/L3은 auto_execute=true 허용 | L2 + auto_execute=true → 허용 |
| T-AC-007 | 통합: RBAC + Autonomy 조합 검증 | VIEWER+L3=차단, OPERATOR+L2=허용 |

### T-ARCH: 아키텍처 테스트

> 시스템 구조 규칙(SOT 소유권, REF-only 원칙)이 코드에서 지켜지는지 검증합니다. [근거: B5 §5.1~§5.7 AC 매핑]

| 테스트 ID | 검증 대상 | 기대 결과 |
|----------|----------|----------|
| T-ARCH-001 | D2 Registry SOT 단일 소유 | EventType/FailureCode/Fallback는 D2 모듈에서만 정의 |
| T-ARCH-002 | D3 Registry는 D2 REF-only | D3 모듈에서 코드값 직접 정의 없음, import는 D2 경유 |
| T-ARCH-003 | D4 Registry는 D2 REF-only | D4 모듈에서 코드값 직접 정의 없음 |
| T-ARCH-004 | D5 Registry는 D2 REF-only | D5 모듈에서 코드값 직접 정의 없음 |
| T-ARCH-005 | ToolRegistry 경유 필수 | 직접 HTTP/SDK 호출 시 차단, ToolRegistry.invoke()만 허용 |
| T-ARCH-006 | D8은 SOT 스키마 미소유 | D8 관련 디렉토리에 Pydantic 모델 클래스 없음 |
| T-ARCH-007 | 모든 스키마 _meta 필수 | D2~D7 모든 스키마에 _meta 필드 존재 (D1 Template 준수) |

**핵심 요약 (3줄)**
1. 상세 테스트는 T-VAL(설정) / T-SDAR(자동수리) / T-HMAC(인증) / T-GUARD(보호벽) / T-GDPR(개인정보) / T-AC(접근제어) / T-ARCH(아키텍처) 7개 카테고리로 구성됩니다.
2. T-GUARD와 T-AC가 가장 많은 케이스를 가지며, 보안이 테스트의 핵심입니다.
3. T-ARCH 테스트는 코드 구조 자체를 검증하여 SOT 소유권과 REF-only 원칙을 강제합니다.

---

# §38. CI/CD 파이프라인 (CI/CD Pipeline)

> **비유**: CI/CD는 **자동 공장 라인**과 같습니다. **CI(Continuous Integration, 지속적 통합)**는 여러 사람이 만든 부품을 자동으로 검사하고 조립하는 **품질 검수 라인**, **CD(Continuous Delivery/Deployment, 지속적 전달/배포)**는 완성품을 포장하여 고객에게 배달하는 **출하 라인**입니다. 코드를 올리면(push) 자동으로 검사 → 테스트 → 빌드 → 배포까지 이루어집니다.

---

## §38.1 GitHub Actions 워크플로우 (~14개)

> **비유**: GitHub Actions(깃허브 액션)는 **자동 로봇 직원**입니다. 코드가 올라오면 자동으로 "코드 검사해!", "테스트 돌려!", "빌드해!" 같은 작업을 수행하는 로봇들이 **워크플로우(workflow)**라는 이름의 업무 지시서를 받아 움직입니다.

### 워크플로우 파일 목록

```
.github/
  workflows/
    ci.yml              ← 통합 CI (가장 핵심)
    release.yml          ← 릴리스 파이프라인
    deploy-v2.yml        ← V2 Docker Compose 배포
    deploy-v3.yml        ← V3 K8s 배포
    security.yml         ← 보안 스캔
    nightly.yml          ← 나이틀리 전체 테스트 (V3)
```

[근거: B6 §8 워크플로우 파일 구조]

### 14개 워크플로우(Job) 상세

| # | 워크플로우/Job 이름 | 트리거 | 역할 | 버전 |
|---|------------------|--------|------|------|
| 1 | **python-quality** | PR/Push | Python 린팅(ruff) + 타입체크(mypy) | V1+ |
| 2 | **rust-quality** | PR/Push | Rust 린팅(clippy) + 포맷체크(rustfmt) | V1+ |
| 3 | **react-quality** | PR/Push | React 린팅(eslint) + 타입체크(tsc) + 포맷(prettier) | V1+ |
| 4 | **schema-validation** | PR/Push (python-quality 후) | Pydantic v2 스키마 전체 임포트/인스턴스화 검증 | V1+ |
| 5 | **python-test** | PR/Push (schema 후) | pytest 단위+통합 테스트 + 커버리지 | V1+ |
| 6 | **rust-test** | PR/Push (rust-quality 후) | cargo test + tarpaulin 커버리지 | V1+ |
| 7 | **react-test** | PR/Push (react-quality 후) | vitest + v8 커버리지 | V1+ |
| 8 | **coverage-report** | 테스트 완료 후 | Python+Rust+React 커버리지 합산, PR 코멘트, 임계값 체크 | V1+ |
| 9 | **security** (비밀 키 + 의존성) | PR/Push + 주간 | gitleaks(비밀 키 노출) + pip-audit/cargo-audit/npm-audit | V1+ |
| 10 | **build-check** | 테스트 통과 후 | Tauri 크로스 플랫폼 빌드 (Linux/Windows/macOS) | V1+ |
| 11 | **release** | Tag push (`v*`) | Changelog 생성 + GitHub Release + Tauri 바이너리 업로드 | V1+ |
| 12 | **deploy-v2** | 수동 (workflow_dispatch) | Docker Compose 배포 (staging/production) | V2+ |
| 13 | **deploy-v3** | 수동 (workflow_dispatch) | Helm + K8s 배포 (Blue-Green 전략) | V3 |
| 14 | **nightly** | 매일 03:00 UTC (schedule) | 전체 테스트 스위트 + 성능 벤치마크 | V3 |

### 워크플로우 의존관계 (실행 순서)

```
PR/Push 트리거
  ├─ python-quality ─── schema-validation ─── python-test ──┐
  ├─ rust-quality ──────────────────────────── rust-test ────┤
  ├─ react-quality ─────────────────────────── react-test ──┤
  └─ security (병렬) ──────────────────────────────────────┐│
                                                           ▼▼
                                          coverage-report + build-check
                                                     │
                                                ci-summary
```

[근거: B6 §8 통합 CI YAML]

**핵심 요약 (3줄)**
1. GitHub Actions 워크플로우는 총 ~14개이며, ci.yml이 핵심 통합 파이프라인입니다.
2. 코드 품질(3개) → 스키마 검증(1개) → 테스트(3개) → 커버리지+빌드(2개) → 보안(1개) 순서로 실행됩니다.
3. V2+부터 배포 워크플로우(Docker/K8s), V3부터 나이틀리 스위트가 추가됩니다.

---

## §38.2 브랜치 전략 (Branch Strategy)

> **비유**: 브랜치(branch)는 **작업실**과 같습니다. 본관(main)에서 바로 공사하면 위험하니, 별도의 **작업실(feature)**에서 작업하고 검수(PR)를 거쳐 본관에 합칩니다. 급한 수리는 **긴급 수리실(hotfix)**에서 별도로 처리합니다.

### Git Flow 기반 브랜치 전략

| 브랜치 | 용도 | 트리거 | 보호 규칙 |
|--------|------|--------|----------|
| `main` | **프로덕션 릴리스** (실제 배포 버전) | tag push | PR 필수, 리뷰 필수, CI 통과 필수 |
| `develop` | **통합 개발** (다음 릴리스 준비) | merge commit | PR 필수, CI 통과 필수 |
| `feature/*` | **기능 개발** (새로운 기능 작업) | PR open/push | develop으로 PR 생성 |
| `hotfix/*` | **긴급 수정** (프로덕션 버그 수정) | PR open/push | main으로 직접 PR 가능 |
| `release/*` | **릴리스 준비** (최종 테스트/문서 정리) | manual (수동) | main + develop 양쪽 merge |

[근거: B6 §1.3]

### 브랜치 흐름도

```
feature/login ──PR──► develop ──PR──► release/1.0 ──PR──► main
                         ▲                                  │
                         │          hotfix/urgent-fix ──────┘
                         └── merge back ────────────────────┘
```

### 버전별 브랜치 전략 차이

| 항목 | V1 | V2 | V3 |
|------|----|----|-----|
| 주요 브랜치 | main, develop, feature/* | + hotfix/*, release/* | + staging 환경 브랜치 |
| PR 리뷰 | 선택 | 필수 (1명+) | 필수 (2명+) |
| CI 통과 | 필수 | 필수 | 필수 + 보안 스캔 |
| 배포 방식 | 수동 (로컬 설치) | Docker Compose 자동 | K8s (ArgoCD) 자동 |

[근거: B6 §1.1, §1.3]

**핵심 요약 (3줄)**
1. Git Flow 기반으로 main/develop/feature/hotfix/release 5개 브랜치 유형을 사용합니다.
2. main은 프로덕션 전용이며 PR 필수 + CI 통과 필수로 보호됩니다.
3. 기능 개발은 feature/* → develop → release/* → main 순서로 합쳐집니다.

---

## §38.3 8-Stage 파이프라인

> **비유**: 자동 공장에서 제품이 **8개 검수 단계**를 거쳐 출하되는 것과 같습니다. 1단계(코드 품질) → 2단계(스키마 검증) → 3단계(테스트) → ... → 8단계(배포)까지 순서대로 통과해야 최종 출하됩니다. 한 단계라도 실패하면 다음 단계로 넘어가지 않습니다.

### 8-Stage 상세

| Stage | 이름 | 역할 | 실행 조건 | 실패 시 행동 |
|-------|------|------|----------|-------------|
| **1** | 코드 품질 (Code Quality) | Python(ruff+mypy), Rust(clippy+rustfmt), React(eslint+tsc+prettier) 린팅/타입체크 | PR/Push 즉시 (병렬) | ❌ 전체 파이프라인 중단 |
| **2** | 스키마 검증 (Schema Validation) | Pydantic v2 모델 전체 임포트/인스턴스화 | Stage 1 Python 통과 후 | ❌ 테스트 진입 차단 |
| **3** | 테스트 (Test) | Python pytest + Rust cargo test + React vitest (병렬) | Stage 1+2 통과 후 | ❌ 빌드 진입 차단 |
| **4** | 커버리지 리포트 (Coverage Report) | Python+Rust+React 커버리지 합산, PR 코멘트, 임계값 체크 | Stage 3 통과 후 | ⚠️ 경고 (차단하지 않음) |
| **5** | 보안 스캔 (Security Scan) | gitleaks(비밀 키 노출) + pip-audit + cargo-audit + npm-audit + Trivy | Stage 1과 병렬 | ⚠️ 경고 (CRITICAL은 차단) |
| **6** | 빌드 확인 (Build Check) | Tauri 크로스 플랫폼 빌드 (Linux/Windows/macOS) | Stage 3 통과 후 | ❌ 릴리스 진입 차단 |
| **7** | 릴리스 (Release) | Changelog 생성 + GitHub Release + 바이너리 업로드 | Tag push (`v*`) + Stage 6 통과 | ❌ 배포 진입 차단 |
| **8** | 배포 (Deploy) | V2: Docker Compose / V3: Helm + K8s (Blue-Green) | 수동 트리거 + Stage 7 완료 | 🔄 자동 롤백 (V3) |

[근거: B6 §2~§6, §8 통합 CI YAML]

### 파이프라인 흐름도

```
Stage 1          Stage 2      Stage 3        Stage 4
┌──────────┐     ┌──────┐     ┌──────────┐   ┌──────────┐
│Python 품질├──►│스키마  ├──►│Python 테스트├──►│          │
│Rust   품질│     │검증   │     │Rust   테스트│   │커버리지   │
│React  품질│     └──────┘     │React  테스트│   │리포트     │
└──────────┘                   └──────────┘   └──────────┘
     ▼ (병렬)                                       │
Stage 5                                  Stage 6    ▼
┌──────────┐                   ┌──────────┐
│보안 스캔   ├─────────────────►│빌드 확인   │
└──────────┘                   └──────────┘
                                      │
                               Stage 7 ▼
                               ┌──────────┐
                               │릴리스      │
                               └──────────┘
                                      │
                               Stage 8 ▼
                               ┌──────────┐
                               │배포        │
                               └──────────┘
```

### 커버리지 임계값 (Stage 4에서 체크)

| 언어 | 최소 커버리지 | 목표 커버리지 | 측정 도구 |
|------|-------------|-------------|----------|
| **Python** | 75% | 85% | pytest-cov |
| **Rust** | 80% | 80% | cargo-tarpaulin |
| **React** | 80% | 80% | vitest + @vitest/coverage-v8 |

[근거: B6 §3.4 커버리지 임계값, B5 §7.1]

### 모듈별 최소 커버리지

| 모듈 | 최소 커버리지 | 이유 |
|------|-------------|------|
| `schemas/` | **95%** 🔒 | 모든 Pydantic 모델은 유효/무효 케이스 필수 |
| `safety/` | **90%** | 보안/비용/승인은 높은 신뢰도 필수 |
| `orange_core/` | **85%** | Decision Kernel은 핵심 로직 |
| `blue_nodes/` | **80%** | Node 실행 로직 |
| `storage/` | **80%** | 데이터 영속성 |
| `agent/` | **80%** | LangGraph 워크플로우 |
| `ui/` (React) | **75%** | UI 컴포넌트 |
| `src-tauri/` (Rust) | **80%** | IPC 핸들러 |

[근거: B5 §7.2]

**핵심 요약 (3줄)**
1. 8-Stage 파이프라인은 코드 품질 → 스키마 → 테스트 → 커버리지 → 보안 → 빌드 → 릴리스 → 배포 순서입니다.
2. Stage 1~3 중 하나라도 실패하면 전체 파이프라인이 중단됩니다.
3. V3에서는 Stage 8 배포 실패 시 자동 롤백(Helm rollback)이 작동합니다.

---

## §38.4 보안 스캔 (Security Scan)

> **비유**: 건물에 **방범 시스템**을 설치하는 것과 같습니다. **SAST(정적 분석)**는 건물 설계도를 보고 "이 창문은 잠금장치가 없다!"를 찾아내는 **도면 검사관**, **Dependency Audit(의존성 감사)**는 사용한 자재(라이브러리)에 "리콜(취약점) 대상이 있는지" 확인하는 **자재 검수관**입니다.

### SAST: 정적 코드 분석 (Static Application Security Testing)

> 코드를 실행하지 않고(정적으로) 보안 취약점을 찾아내는 도구입니다. [근거: B6 §7]

| 도구 | 대상 언어 | 검사 항목 | 실행 시점 |
|------|----------|----------|----------|
| **ruff** (S 규칙) | Python | 하드코딩된 패스워드, SQL 인젝션 패턴, assert 사용 등 | PR/Push (Stage 1) |
| **clippy** (pedantic) | Rust | 안전하지 않은 코드 패턴, 메모리 누수 가능성 | PR/Push (Stage 1) |
| **eslint** (security plugin) | TypeScript/React | XSS 위험, innerHTML 사용, eval 사용 등 | PR/Push (Stage 1) |
| **gitleaks** | 전체 | Git 히스토리에서 비밀 키(API Key, 비밀번호) 노출 검사 | PR/Push + 주간 (Stage 5) |
| **Trivy** | 전체 (V2+) | 파일시스템/컨테이너 이미지 취약점 스캔 | main 브랜치 push |

### VAMOS 전용 비밀 키 패턴 검사

gitleaks 기본 규칙 외에 VAMOS 프로젝트 전용 패턴도 검사합니다. [근거: B6 §7.2]

| 패턴 | 설명 | 예시 |
|------|------|------|
| `OPENAI_API_KEY=sk-*` | OpenAI API 키 노출 | 코드에 직접 작성 시 경보 |
| `ANTHROPIC_API_KEY=*` | Anthropic API 키 노출 | 코드에 직접 작성 시 경보 |
| `POSTGRES_PASSWORD=*` (비변수) | DB 비밀번호 하드코딩 | 환경변수($) 미사용 시 경보 |
| `NEO4J_AUTH=neo4j/*` | Neo4j 인증 정보 노출 | 기본 패스워드 사용 시 경보 |
| `TAURI_SIGNING_PRIVATE_KEY=*` | Tauri 서명 키 노출 | 코드에 직접 작성 시 경보 |

### Dependency Audit: 의존성 취약점 검사

> 프로젝트에서 사용하는 외부 라이브러리(패키지)에 알려진 보안 취약점이 있는지 자동으로 검사합니다. [근거: B6 §7.1]

| 도구 | 대상 | 검사 대상 파일 | 실행 주기 |
|------|------|-------------|----------|
| **pip-audit** | Python 패키지 | requirements.txt | PR/Push + 매주 월요일 09:00 UTC |
| **cargo-audit** | Rust 크레이트 | Cargo.lock | PR/Push + 매주 월요일 |
| **npm audit** | Node.js 패키지 | package-lock.json | PR/Push + 매주 월요일 |
| **Trivy** (V2+) | Docker 이미지 | Dockerfile | main push 시 |

### 라이선스 검사

오픈소스 라이선스 호환성도 자동으로 검사합니다. [근거: B6 §7.3]

| 허용 라이선스 | 금지 라이선스 |
|-------------|-------------|
| MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, PSF-2.0, LGPL, MPL-2.0 | **GPL-3.0**, **AGPL-3.0**, **SSPL-1.0** |

> 금지 라이선스가 포함된 패키지가 감지되면 경고가 발생합니다.

### 필수 GitHub Secrets (비밀 설정)

CI/CD 파이프라인에서 사용하는 비밀 키 목록입니다. 코드에 직접 작성하면 안 되고, GitHub Settings > Secrets에 등록해야 합니다. [근거: B6 §8]

| Secret 이름 | 용도 | 활성 버전 |
|-------------|------|----------|
| `TAURI_SIGNING_PRIVATE_KEY` | Tauri 앱 서명 | V1+ |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 서명 키 패스워드 | V1+ |
| `STAGING_SSH_KEY` / `PROD_SSH_KEY` | 배포 서버 SSH (staging/prod 분리) | V2+ |
| `STAGING_HOST` / `PROD_HOST_LIST` | 배포 서버 호스트 (staging/prod 분리) | V2+ |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | DB 인증 | V2+ |
| `QDRANT_API_KEY` | Qdrant (벡터DB) API 키 | V2+ |
| `NEO4J_AUTH` | Neo4j (그래프DB) 인증 | V2+ |
| `OPENAI_API_KEY` | OpenAI API 키 | V2+ |
| `KUBECONFIG` | K8s kubeconfig (base64 인코딩) | V3 |
| `SLACK_WEBHOOK_URL` | Slack 알림 Webhook | V2+ |

### 커밋 메시지 컨벤션 (Conventional Commits)

릴리스 버전 번호가 자동으로 올라가도록, 커밋 메시지에 특정 접두사를 사용합니다. [근거: B6 §5.1]

| 접두사 | 의미 | 버전 증가 |
|--------|------|----------|
| `feat:` | 새 기능 추가 | MINOR (1.0.0 → 1.1.0) |
| `fix:` | 버그 수정 | PATCH (1.0.0 → 1.0.1) |
| `feat!:` 또는 `BREAKING CHANGE:` | 하위 호환 깨지는 변경 | MAJOR (1.0.0 → 2.0.0) |
| `chore:` | 빌드/도구 관련 | 릴리스 노트 제외 |
| `docs:` | 문서 변경 | 릴리스 노트 제외 |
| `test:` | 테스트 추가/수정 | 릴리스 노트 제외 |

**핵심 요약 (3줄)**
1. SAST(정적 분석)는 ruff/clippy/eslint/gitleaks로 코드 수준 보안을, Dependency Audit는 pip-audit/cargo-audit/npm-audit으로 라이브러리 취약점을 검사합니다.
2. VAMOS 전용 비밀 키 패턴 5종이 추가로 검사되며, GPL-3.0/AGPL-3.0/SSPL-1.0 라이선스는 금지됩니다.
3. 모든 비밀 키는 GitHub Secrets에 등록하고, 코드에 직접 작성하면 gitleaks가 경보를 발생시킵니다.

---

## 검증 체크리스트

- [x] 테스트 피라미드 (Unit/Integration/E2E)? → §37.1
- [x] 128개 테스트 카테고리별? → §37.2 (~85) + §37.3 (~30) + §37.4 (~13)
- [x] AC 매핑 (50 AC → 79 테스트)? → §37.5
- [x] 상세 케이스 (T-VAL~T-ARCH)? → §37.6
- [x] GitHub Actions ~14개? → §38.1
- [x] 브랜치 전략? → §38.2
- [x] 8-Stage 파이프라인? → §38.3
- [x] 보안 스캔? → §38.4
- [x] 비유 설명 포함? → 모든 섹션 첫 문단
- [x] 근거 SOT 참조 표기? → [근거: B5 §x.x], [근거: B6 §x.x] 형식
