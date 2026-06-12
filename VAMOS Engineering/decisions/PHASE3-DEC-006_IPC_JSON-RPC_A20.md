# PHASE3-DEC-006 (3-6): IPC JSON-RPC 사양 + A20 인터페이스 계약 규칙

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must
> ⟦정본 매핑 정정 반영: PHASE_B1 §5.2 + D2.1 스키마 — 구 PHASE_B4 오참조 아님⟧

## 결정

### IPC 전송 (PHASE_B1 추인)
- **V1: JSON-RPC 2.0 over subprocess stdin/stdout** — Rust가 Python 프로세스를 spawn, 메시지 교환 (PHASE_B1 L1398-1399). V2+: gRPC 전환 가능 (L21).
- 3채널 구조: React↔Rust = Tauri IPC / Rust↔Python = JSON-RPC subprocess / 도구 = MCP Streamable HTTP (L15)

### JSON-RPC 메서드 13개 (PHASE_B1 §5.2 L2052-2068 — 분모 LOCK 추인)
| # | Method | 소스 스키마 |
|---|--------|------------|
| 1 | `langgraph.workflow.run` | D5 WorkflowOutputEnvelopeSchema |
| 2 | `langgraph.stage.execute` | D5 WorkflowStageSchema |
| 3 | `langgraph.decision.create` | D2 DecisionSchema |
| 4 | `langgraph.node.dispatch` | D3 NodeRequest/ResponseEnvelopeSchema |
| 5 | `langgraph.verify.run_chain` | D5 VerifyChainEntrySchema |
| 6 | `embedding.encode` | D6 KBEmbeddingRecordSchema |
| 7 | `embedding.store` | D6 VectorStoreAdapterSchema |
| 8 | `llm.generate` | D4 BrainAdapterResponseSchema |
| 9 | `llm.record_invoke` | D4 InfraInvokeResultSchema |
| 10 | `llm.rate_limit.get` | D4 RateLimitConfigSchema |
| 11 | `mcp.bridge.init` | D3 MCPBridgeLayerSchema |
| 12 | `mcp.bridge.health` | D3 MCPBridgeLayerSchema |
| 13 | `mcp.tools.discover` | D3 ToolCallRegistrySchema |

### A20 인터페이스 계약 규칙 (STRATEGY_06 §2 — R1 확정)
1. **정본(SSoT) = Python Pydantic v2 모델** — 유일한 수동 편집 지점
2. 파생 자동 생성: Pydantic → JSON Schema → serde(Rust)/TypeScript interface
3. **직접 수정 금지 3종**: serde 구조체 / TS interface / JSON Schema
4. 변경 절차 6 Step: Pydantic 수정 → Schema 재생성 → serde 재생성 → TS 재생성 → **왕복 테스트(Round-trip) PASS** → **4파일 동시 커밋** (부분 커밋 금지)
5. 에러 응답은 D2 FailureCodeRegistry 연동 (PHASE_B1 §6)

## 근거 (정본 라인)
PHASE_B1 §3.0 L1401-1408(공통 규격)·§5.2 L2052-2068(13개 전수)·L1398-1399 · STRATEGY_06 §2.1-2.3 L26-80 · 4-1 도메인 cross-ref(4-3 jsonrpc_4-1_cross_ref EXACT MATCH 100% — Phase 4 검증 기존재) — 재정의 0.

## 이유·대안
13개 분모는 PHASE_B1이 D2.1 소스 스키마와 1:1 매핑으로 기확정. 대안(gRPC V1 도입)은 PHASE_B1 V1 명세 위반 — 기각. Pydantic 단일 정본은 타입 3중화(Py/Rust/TS) 드리프트의 유일 차단책.

## 구현 바인딩
V0-STEP-2(스키마 25+generate_types.py)·STEP-3(IPC 서버+python_manager) — 왕복 테스트는 V0 GO/NO-GO 게이트 항목(로드맵 4-V).
