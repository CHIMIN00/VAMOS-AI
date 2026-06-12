---
tags: [type/concept, tier/T4, version/V1, lock/FREEZE]
aliases: [MCP Bridge, Streamable HTTP, DEC-017]
created: 2026-06-12
---

# MCP Bridge Layer (Streamable HTTP)

## 정의
외부 도구를 Model Context Protocol로 연결하는 브리지 계층. 전송 방식은 **Streamable HTTP (DEC-017, LOCK)**. 통신 계층 말단에 위치: React UI ↔ Tauri IPC ↔ Rust ↔ JSON-RPC ↔ Python ↔ **MCP Streamable HTTP**. 코드 위치: `backend/vamos_core/mcp/` (bridge/server/client/tool_discovery).

## 이 개념이 등장하는 모든 도메인
- [[T4-MCP]] — 정본(4-3): Streamable HTTP, 마켓플레이스, 외부 서버/클라이언트
- [[T4-Rust-Tauri]] — JSON-RPC `mcp.*` 메서드(Python-Rust 13개 중)
- [[T1-Auxiliary-Modules]] — I-10 Tool Registry/Router가 도구 라우팅
- [[T3-A2A-Protocol]] — 에이전트 간 통신과 외부 도구 통신의 경계

## 값·수치 (LOCK)
- `mcp.transport = streamable_http` — config.v1.toml LOCK (CLAUDE.md §20)
- **MCP max_retries: V1/V2=2, V3=3** (D2.0-03·PHASE_B4 §3.9 정본 — exponential backoff 1s→2s, V3 +4s. PART2 config 예시 '3'은 비정본 표기)
- MCP Tool Protocol 엔드포인트 3개: `tools/call`, `tool_registry.get`, `tool_registry.list`
- DEC-003 (LOCK): 도구 승인 Allowlist — 읽기전용=자동, 외부API/쓰기/코드실행=확인 필요

## 버전별 차이
- V1~V3: 전송 Streamable HTTP 동일 (LOCK) / max_retries만 V3에서 3으로 상향

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.1(DEC-017)·§7.4(max_retries)·§13·§20 / `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` / `D:\VAMOS\docs\sot\PHASE_B4_CONFIG_SPEC` §3.9 / `D:\VAMOS\docs\sot 2\4-3_MCP-Server-Client\`
