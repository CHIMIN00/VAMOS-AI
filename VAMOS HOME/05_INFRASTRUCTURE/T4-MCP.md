---
tags: [tier/T4, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [4-3, MCP 서버/클라이언트, MCP-Server-Client]
tier: T4
domain: "4-3 MCP-Server-Client"
sot_source: "D:\\VAMOS\\docs\\sot 2\\4-3_MCP-Server-Client\\"
design_doc: "[[D2.0-04-Infra]]"
quality_gate: "APPROVED — Phase 4 RECOVERY 도메인 종료 (13 V3 NEW, 외부 11/11 ALL CONNECTED, 2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 31 도구 + 연결/재시도 | V2: 디스커버리·Pool 7 NEW | V3: 마켓플레이스·런타임 13 NEW"
created: 2026-06-12
---

# 4-3 MCP-Server-Client

## 한줄 요약
MCP 도구 31개(내부 20 + 외부 11)·Streamable HTTP 연결·Bridge Layer·디스커버리·Connection Pool을 관장하는 도구 인프라 정본 도메인.

## 핵심 정의
- 전송 프로토콜: **Streamable HTTP** (DEC-017, MCP 2025-03-26 spec) — stdio 예외는 CLF-MCP-005 RESOLVED-DEFERRED 주석 상속
- 재시도: max 3회 + 지수 백오프 factor 2.0 (LOCK-MCP-06 상한, 서버별 오버라이드 ≤3 — V1/V2 일부 서버 1~2회 실측, V3 멀티리전 전환은 connection_protocol §6.3)
- Circuit Breaker 5/60s/3 (LOCK-MCP-07), 최대 동시 서버 5, Connection Pool 10

## LOCK 항목 (LOCK-MCP-01~10, 10건)
- MCP-01 페이로드 10MB / MCP-02 네임스페이스 `{server}.{tool}` / MCP-03 31개 도구(내부20+외부11)
- MCP-04 Streamable HTTP / MCP-05 동시 서버 5 / MCP-06 재시도 max 3·backoff 2.0
- MCP-07 CB 5회→OPEN·60s→HALF-OPEN·3성공→CLOSE / MCP-08 on-demand idle 10분 종료
- MCP-09 스키마 정본 소유(sot 2/4-3 구현, D2.0-04 아키텍처) / MCP-10 Pool 최대 10
- cross-domain cite-only: LOCK-BM-09 70:30(3-9 정본) + 4-1 LOCK-RT (재정의 0)

## 의존성 (Depends On)
- [[T6-Security]] — MCP Tool 화이트리스트·서명 검증 / [[T6-Event-Logging]] — MCP 통신 이벤트
- [[T6-Operations]] — 헬스체크·로그 보존 / [[T0-Governance]] — R1~R11

## 제공 (Provides To)
- [[T2-Blue-Node]] — 도구 호출 인프라(07_mcp-bridge) / [[T3-Dev-Tools]] — 도구 호출 프로토콜
- [[T3-Agent-Protocol]] — MCP↔A2A 브리지·Tool Discovery / [[T6-Brain-Adapter]] — ToolRegistry
- [[T3-A2A-Protocol]] — 양방향(B10, 프로토콜 경계 분리: A2A=3-8, MCP=4-3)
- [[T4-Rust-Tauri]] — JSON-RPC 13 메서드 양방향 cross-ref 완성(jsonrpc_4-1_cross_ref, IPC mcp_* 3개)

## 횡단 개념 연결
- [[MCP-Bridge-Layer]] — 본 도메인이 Bridge 구현 정본 / [[Failover-Chain-Pattern]] — 재시도·CB 정책

## STEP7 매핑
- 출처: Part2 §6.6 (MCP 구성요소 7개 + 외부 서버 카탈로그 11개 이름만 — PARTIAL, tool schemas는 본 도메인 정본)

## 버전별 범위
- V1: 31 도구 스키마 + 연결/재시도/CB / V2: 디스커버리·협상·외부서버·Pool 7 NEW (3,300L) / V3: 마켓플레이스·RBAC·런타임 13 NEW (외부 11/11 closure)

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY Wave 3 #21 (2026-06-03), CONFLICT OPEN 0 (CLF-MCP-001~005)
- LOCK 검증: 10/10 일치 (AUTHORITY_CHAIN v1.3, set accuracy 10 유일 보존)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\4-3_MCP-Server-Client\
- Authority: 4-3_MCP-Server-Client\AUTHORITY_CHAIN.md (v1.3)
- Design: D2.0-04 §7 + D2.0-03 §6.3~§6.5 + PHASE_B1 §4
