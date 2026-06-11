---
tags: [tier/T2, module/E-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [2-1, 블루 노드, Blue-Node-Architecture]
tier: T2
domain: "2-1 Blue-Node-Architecture"
sot_source: "D:\\VAMOS\\docs\\sot 2\\2-1_Blue-Node-Architecture\\"
design_doc: "[[D2.0-03-Blue-Nodes]]"
quality_gate: "LOCKED (Phase 4 2026-05-31, 18-file LOCKED inventory)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 3 nodes | V2: 10 nodes | V3: 50 nodes"
created: 2026-06-11
---

# 2-1 Blue-Node-Architecture

## 한줄 요약
Permission Matrix, CORE↔NODE 인터페이스, Node Lifecycle, Template Injection, MCP Bridge 등 Blue Node 실행 계층의 정본을 소유하는 Tier 2 도메인.

## 핵심 정의
- 정본 소유 7개념: Permission Matrix / CORE-NODE Interface / Template Injection / Node Lifecycle / Memory Sharing / Policy Overrides / MCP Bridge
- BN 타입 4+1: Dev, Research, Content, Quant, Trading
- Permission Level 6단계 (L0 읽기전용~L5 금융), 모든 통신은 CORE 경유 (Node-to-Node 직접 통신 금지)
- Lifecycle 8 States: CANDIDATE→LAZY→ACTIVATING→ACTIVE→BUSY→DRAINING→SUSPENDED→TERMINATED

## LOCK 항목 (LOCK-BN-01~19 + 05a, 20건)
- BN-01 BN 타입 4+1 / BN-02 Permission Level 6단계 / BN-03/04 Request·ResponseEnvelope 필수 7필드
- BN-05 Lifecycle P0/P1/P2 규칙 / BN-05a Lifecycle 8 States (DEFINED-HERE, Phase 5 동결)
- BN-06 P2 자동 생성 금지 / BN-07 P2 세션 종료 시 자동 OFF / BN-08 Node 활성화 = 승인 필수
- BN-09 CORE↔NODE 계약 불변 / BN-10 07 Gate 경유 의무 / BN-11 MCP = Streamable HTTP
- BN-12 active_node_cap V1=3/V2=10/V3=50 / BN-13 candidate_node_cap V1=5/V2=20/V3=100
- BN-14 직접 Node-to-Node 통신 금지 / BN-15 최대 동시 실행 3 (V1)
- BN-16 VamosMessage 표준 포맷 / BN-17 Policy Override 더 엄격한 방향만
- BN-18 Template 소유 = CORE(02) / BN-19 P2 승인 타임아웃 (일반 10분/P2 5분 → Auto deny)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-COND-Modules]] — COND = BN 실행 도구 (양방향)
- [[T4-Rust-Tauri]] — IPC 계층 (CORE↔NODE) / [[T4-MCP]] — 도구 호출 인프라
- [[T6-Security]] — Node 간 HMAC 통신 / [[T6-Event-Logging]] — BLUE NODE 이벤트 네임스페이스

## 제공 (Provides To)
- [[T3-Multimodal]] [[T3-PKM]] [[T3-Workflow-RPA]] [[T3-Education]] [[T3-Health-EmotionAI]] [[T3-Dev-Tools]] [[T3-A2A-Protocol]] [[T3-Business-Model]] [[T3-Agent-Protocol]] — BN 런타임 실행 환경
- [[AI-Investing-Overview]] — BN 런타임 / [[T2-COND-Modules]] — BN = COND 소비자 (양방향)

## 횡단 개념 연결
- [[Permission-Matrix-System]] — L0~L5 정본 / [[VamosMessage-Schema]] — 표준 메시지 포맷
- [[MCP-Bridge-Layer]] — Streamable HTTP / [[5-Gate-Decision-Framework]] — 07 Gate 경유

## 관련 모듈 시리즈
- [[MODULE-MAP]] — E-Series (Blue Node 외부 기능 모듈) 실행 호스트

## STEP7 매핑
- 출처: D2.0-03 (K-041, K-049) + D2.1-D3 스키마 — SPEC §14 기술스택 범위 내

## 버전별 범위
- V1: 3 nodes (P0~P1) / V2: 10 nodes (P2) / V3: 50 nodes (P3)

## 검증 상태
- Quality Gate: LOCKED (Phase 4 2026-05-31, 구조 변경 불가)
- LOCK 검증: 20/20 일치 (BN-01~19 + BN-05a, AUTHORITY_CHAIN 실측)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\2-1_Blue-Node-Architecture\
- Authority: 2-1_Blue-Node-Architecture\AUTHORITY_CHAIN.md
- Design: [[D2.0-03-Blue-Nodes]], [[D2.1-Schema-Index]] (D3 Envelope)
