---
tags: [tier/T3, module/A-series, status/COND, version/V1, type/domain, lock/FREEZE]
aliases: [3-8, 대화·A2A, Conversation-A2A]
tier: T3
domain: "3-8 Conversation-A2A"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-8_Conversation-A2A\\"
design_doc: "[[D2.0-05-Agent-Workflow]]"
quality_gate: "APPROVED — S10-4 등급 A / Phase 4 RECOVERY 6 V3 ALL NEW (2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 기본 프로토콜 | V2: P2 MoA+SSE | V3: P3 분산 디스커버리"
created: 2026-06-12
---

# 3-8 Conversation-A2A

## 한줄 요약
Google A2A 스펙 기반 에이전트 간 통신(JSON-RPC 2.0)·디스커버리·MoA 패턴·mTLS/JWT 보안을 구현 정본으로 관리하는 Tier 3 대화·A2A 프로토콜 도메인.

## 핵심 정의
- A2A 메시지 스키마·디스커버리·보안·MoA 패턴의 구현 정본 (아키텍처는 D2.0-05, 체크리스트는 STEP7-B)
- 정본 소유자 매핑: A2A 스키마=3-8 / 프로토콜 추상·자율성=#13(3-10) / 도구 스키마·MCP Bridge=#16(4-3) / VamosMessage=#3(2-1)
- Phase 2 V2 = 8 NEW(3,984L: SSE/Push/multi-turn/state machine/MoA/metrics/registry/delegation), Phase 4 V3 = 6 ALL NEW(분기트리·WFQ·청킹·composition DSL·테스트 프레임워크·VBS-12)

## LOCK 항목 (LOCK-A2A-01~10, 10건)
- A2A-01 `"jsonrpc": "2.0"` / A2A-02 Task 상태 submitted|working|input-required|completed|failed|canceled
- A2A-03 턴 구조 role: "user"|"agent" + parts: Part[] / A2A-04 mDNS `_vamos-a2a._tcp.local.` 변경 금지
- A2A-05 컨텍스트 윈도우 모델별 max_tokens 준수·초과 시 압축 / A2A-06 mTLS 인증서 만료 30일 전 자동 갱신
- A2A-07 JWT delegation chain 최대 깊이 3 (LOCK-AT-004 교차) / A2A-08 Agent Mode MANUAL|SEMI_AUTO|SUPERVISED_AUTO
- A2A-09 Circuit Breaker 연속 실패 3회→OPEN·60초 후 HALF-OPEN / A2A-10 스키마 정본 소유 sot 2/3-8(구현)+D2.0-05(아키텍처)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-Blue-Node]] — BN 런타임·VamosMessage 연동 (#5)
- [[T6-Memory-RAG]] — 세션 메모리 L0 (#46) / [[T1-Verifier-Engines]] — A2A 태스크 결과 검증

## 제공 (Provides To)
- [[T3-Agent-Protocol]] — A2A 프로토콜 계층 ↔ 프레임워크 어댑터 (B9)
- [[T4-MCP]] — A2A 메시지 스키마 ↔ 도구 호출 스키마 (B10) / [[T6-Agent-Teams]] — A2A JSON-RPC ↔ 팀 커뮤니케이션 (B22)

## 횡단 개념 연결
- [[VamosMessage-Schema]] — 노드 간 표준 포맷과의 경계 (#3 정본) / [[MCP-Bridge-Layer]] — A2A↔MCP 위임 인터페이스
- [[A-Series-Architecture-Extensions]] — Agent Workflow 확장 연계 / [[Failover-Chain-Pattern]] — CB/Fallback·Retry (D2.0-05 §4.4)

## 관련 모듈 시리즈
- [[MODULE-MAP]] — Agent Mode·Cooperative Agent 구조 (D2.0-05 ADD-009/ADD-072)

## STEP7 매핑
- 출처: STEP7-B (대화 프로세스 작업가이드 — 체크리스트/항목 목록 정본)

## 버전별 범위
- V1: P1 기본 프로토콜 / V2: P2 MoA+SSE / V3: P3 분산 디스커버리 (6 V3: branching/priority WFQ 8/4/2/1/chunking 64KB/composition/test/VBS-12)

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v1.3, Phase 4 RECOVERY genuine write 2026-06-03, DRAFT→APPROVED 6/6, #15 CI/CD RESOLVED_PHASE4)
- LOCK 검증: 10/10 일치 (R2/R9 verbatim 보존, 재정의 0, CONFLICT OPEN=0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\
- Authority: 3-8_Conversation-A2A\AUTHORITY_CHAIN.md (v1.3)
- Design: [[D2.0-05-Agent-Workflow]] §1.1/§4.4/§12.13, [[D2.0-03-Blue-Nodes]]
