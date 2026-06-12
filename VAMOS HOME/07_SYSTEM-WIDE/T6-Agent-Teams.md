---
tags: [tier/T6, module/COND, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-3, 에이전트 팀, Agent-Teams-PARL]
tier: T6
domain: "6-3 Agent-Teams-PARL"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-3_Agent-Teams-PARL\\"
design_doc: "[[D2.0-05-Agent-Workflow]]"
quality_gate: "APPROVED (AUTHORITY v1.3 truly_converged_v2)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 Lead+2 | V2: V2-P3 6패턴(Redis/HMAC/Lead+9) | V3: V3-P3 PARL/Mesh/Marketplace"
created: 2026-06-12
---

# 6-3 Agent-Teams-PARL

## 한줄 요약
Lead Agent 단일결정 원칙 기반 에이전트 팀 구성·협업 패턴·PARL(병렬 에이전트 강화학습) 구현 정본을 소유하는 Tier 6 도메인.

## 핵심 정의
- 단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정, Lead는 직접 실행 금지(계획/분배/검증만)
- V1 자체 경량 프레임워크 기본, 외부 엔진은 어댑터로만 연결, LangChain import 금지
- 위임 체인 최대 3단계(V1 config=2), 병렬 상한 V1=3/V2=10/V3=50+, V3 PARL 100 서브에이전트
- 대화 턴 상한 P0=5/P1=10/P2=20, TEE 최대 반복 P0=3/P1=5/P2=10

## LOCK 항목 (20건 = LOCK-AT-001~017 + LOCK-63-1~3)
- AT-001 V1 경량 프레임워크 / AT-002 단일결정 원칙 / AT-003 무한 루프 금지 / AT-004 위임 깊이 3
- AT-005 07 Gate 필수 / AT-006 Execute 단계 도구 호출 / AT-007 Checkpoint/Replay/Fork=trace_id 단위
- AT-008 P2 Trading 기본 OFF / AT-009 대화 턴 상한 / AT-010 TEE 반복 상한 / AT-011 비용 자동 차단
- AT-012 HMAC 서명 필수 / AT-013 위임 권한 계승(상승 방지) / AT-014 병렬 상한 3/10/50+
- AT-015 Lead 직접실행 금지 / AT-016 LangChain import 금지 / AT-017 n8n+Flowise 듀얼
- 63-1 PARL 최종 확정=Lead / 63-2 PARL 최대 병렬 100 / 63-3 특화 에이전트 최대 20

## 의존성 (Depends On)
- [[T6-Security]] — HMAC/Gate 보안 정책 (양방향 B16) / [[T6-Memory-RAG]] — Agent 메모리 공유·팀 컨텍스트
- [[T6-Event-Logging]] — agent.* 이벤트 / [[T3-A2A-Protocol]] — A2A JSON-RPC (양방향 B22)
- [[T3-Agent-Protocol]] — 자율성 L0-L4 정의·어댑터 (양방향 B23) / [[T6-SDAR]] — 자기진단 엔진 (양방향 B17)

## 제공 (Provides To)
- [[T1-Verifier-Engines]] — Research/Critic Agent → 추론 엔진 / [[T3-Workflow-RPA]] — no-code builder → RPA
- [[T6-SDAR]] — SDAR Agent 타입 정의 (양방향 B17)

## 횡단 개념 연결
- [[Decision-Lock]] — 단일결정 원칙(S3 이후 변경불가) / [[Autonomy-Level-Framework]] — 자율성 게이팅
- [[5-Gate-Decision-Framework]] — 07 Gate 선행 통과 / [[LangGraph-DAG-Engine]] — 워크플로우 실행 패턴

## 관련 모듈 시리즈
- [[MODULE-MAP]] — COND-085 AgentCoordinator (2-2 COND 제공) 소비

## STEP7 매핑
- 출처: VAMOS_AGENT_TEAMS_SPEC (S7-A-001-FULL) + Part2 §6.7 L5033-5055 (LOCK-AT 17건 선언)

## 버전별 범위
- V1: Lead+2 경량 / V2: V2-P3 6패턴 (Redis, HMAC, Lead+9) / V3: V3-P3 PARL·Mesh·Marketplace

## 검증 상태
- Quality Gate: APPROVED (STEP_C truly_converged_v2, 2026-04-30)
- LOCK 검증: 20/20 일치 (LOCK-AT 17 + LOCK-63 3, AUTHORITY_CHAIN §2/§3 실측)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-3_Agent-Teams-PARL\
- Authority: 6-3_Agent-Teams-PARL\AUTHORITY_CHAIN.md
- Design: [[D2.0-05-Agent-Workflow]], [[D2.0-02-Orange-Core]], [[SPEC-Agent-Teams]]
