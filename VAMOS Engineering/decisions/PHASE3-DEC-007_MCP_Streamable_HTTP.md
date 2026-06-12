# PHASE3-DEC-007 (3-7): MCP Streamable HTTP 통신 계약

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must

## 결정
- **MCP 전송 = Streamable HTTP** (DEC-017 LOCK 추인) — MCP 2025-03-26 spec, stdio 제거 (PHASE_B4 L357 config `mcp.transport = "streamable_http"`)
- 타임아웃: `default_timeout_ms` V1/V2=10000·V3=15000 (PHASE_B4 §3.9 L358)
- 재시도: `max_retries` **V1/V2=2 · V3=3** — P3-0 GATE-07d 단일 표기 준수 (config 정본 PHASE_B4 §3.9; sot2 4-3 LOCK-MCP-06 "max 3회"는 Bridge 구현 상한으로 무수정 보존)
- 도구 호출 프로토콜: `tools/call` (JSON-RPC 2.0 over Streamable HTTP, PHASE_B1 §5.3) + 내부 ToolRegistry 조회(`mcp.tool_registry.get/list`)
- 구현 상세 정본 = sot2 4-3 MCP-Server-Client (LOCK-MCP-01~10: 페이로드 10MB·네임스페이스 접두사·31 도구·동시 서버 5·CB 5/60s/3·idle 10분·Pool 10)

## 근거 (정본 라인)
- LOCK Registry §1 "DEC-017 | MCP 전송: Streamable HTTP | D2.0-04" — 일치, 재정의 0
- PHASE_B1 L15·L45("Streamable HTTP (LOCK)")·§5.3 L2070-2076 · PHASE_B4 §3.9 L356-360 · sot2 4-3 AUTHORITY_CHAIN L57-66 (LOCK-MCP-01~10)
- P3-0 PHASE3-GATE-07 §d (max_retries 단일 표기 — 본 결정이 준수 인용)

## 이유
DEC-017 기확정 추인. Streamable HTTP는 단일 엔드포인트로 스트리밍+요청/응답을 통합하며 stdio 대비 다중 서버 관리(동시 5)·원격 도구 확장에 적합 — 정본 결정 사유 승계.

## 검토 대안 (기각)
stdio 병행 지원 — DEC-017이 "stdio 제거"로 명시 확정, 재론 금지. (CFL-005 stdio 관련 예외 이력은 4-3 CONFLICT_LOG 참조 — 본 결정 영향 없음)

## 구현 바인딩
V1-Phase 6 (MCP Bridge/Server/Client — V1 GO/NO-GO #22). V0는 `mcp.bridge.init/health`·`mcp.tools.discover` 메서드 시그니처만 예약(DEC-006의 13개 중 3개).
