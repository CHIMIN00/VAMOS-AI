---
tags: [tier/T3, module/COND, status/COND, version/V1, type/domain, lock/FREEZE, lock/DEFINED-HERE]
aliases: [3-10, 에이전트 프로토콜·상호운용성, Agent-Protocol-Interoperability]
tier: T3
domain: "3-10 Agent-Protocol-Interoperability"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-10_Agent-Protocol-Interoperability\\"
design_doc: "[[D2.0-05-Agent-Workflow]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / Phase 4 PRODUCTION PROMOTION COMPLETE (2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 LangGraph+MCP | V2: P2 보안감사 | V3: P3 K8s+윤리"
created: 2026-06-12
---

# 3-10 Agent-Protocol-Interoperability

## 한줄 요약
에이전트 자율성 레벨(L0~L4)·가드레일·프레임워크 어댑터(CrewAI/AutoGen/LangGraph)·배포/스케일링·자기진화 전략을 정본 소유하는 Tier 3 에이전트 프로토콜 도메인.

## 핵심 정의
- 정본 소유 4영역: 자율성/안전(L0~L4, 가드레일) / 프레임워크 어댑터 / 배포·스케일링(컨테이너, 오토스케일) / 자기진화 전략(Dream Mode)
- 비소유(소비만): MCP 스펙=#16, A2A 스펙=#11, COND-085=#4, Blue Node 인터페이스=#3
- LOCK-AP-10 DEFINED-HERE 정본 소유처: `06_autonomy-safety/guardrail_rules.md §V2.2`
- Phase 4 V3 = 7 NEW(83,350B: multi_persona/multi_user/agent_marketplace/agent_testing/k8s_autoscaling/constitutional_ai/iot_integration) + 2 §V3 EXTEND

## LOCK 항목 (LOCK-AP-01~10, 10건)
- AP-01 VamosMessage 스키마(id, type, source, target, content, metadata) / AP-02 Permission Level 0~5 (읽기→금융)
- AP-03 A2A Task 상태 머신 submitted→working→input-required→completed/failed/canceled / AP-04 MCP 전송 Streamable HTTP(V1, WebSocket 아님)
- AP-05 Agent Teams V1 = Lead + max 2 Sub-Agent (6-3 LOCK-AT-014 일치) / AP-06 Circuit Breaker recovery 60초
- AP-07 A2A+MCP 양방향 지원 필수 / AP-08 LangGraph START/END 상수 (set_entry_point 금지)
- AP-09 비용 상한 V1 ₩40K·V2 ₩93K·V3 ₩266K / AP-10 HITL 트리거 Confidence <50% (DEFINED-HERE)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T1-Verifier-Engines]] — 가드레일 안전성 검증 (#2)
- [[T2-Blue-Node]] — 에이전트 실행 환경 (#5) / [[T2-COND-Modules]] — COND-085 AgentCoordinator (#10)
- [[T4-MCP]] — MCP↔A2A 브리지·Tool Discovery (#26) / [[T6-Security]] — 자율성 게이팅 L0~L4·가드레일 (#36)

## 제공 (Provides To)
- [[T3-Business-Model]] — 에이전트 마켓플레이스 비즈니스 모델 (#18)
- [[T3-Dev-Tools]] — 코드 리뷰 위임 ↔ Plugin SDK·VADD (B8) / [[T3-A2A-Protocol]] — 프레임워크 어댑터 ↔ A2A 프로토콜 (B9)
- [[T6-Agent-Teams]] — L0~L4 정의·어댑터 ↔ Agent Types/자율성 (B23)

## 횡단 개념 연결
- [[Autonomy-Level-Framework]] — L0~L4 정본 소유 / [[Permission-Matrix-System]] — Permission Level 0~5 (AP-02)
- [[LangGraph-DAG-Engine]] — START/END 규약 (AP-08) / [[MCP-Bridge-Layer]] — Streamable HTTP (AP-04) / [[Cost-Limits]] — AP-09

## 관련 모듈 시리즈
- [[MODULE-MAP]] — COND-085 AgentCoordinator 소비, 프레임워크 어댑터·자기진화 전략 정본

## STEP7 매핑
- 출처: STEP7-K (86항목, 10 Parts — Part2 PARTIAL: 24 반영/44 미반영/8 N/A)

## 버전별 범위
- V1: P1 LangGraph+MCP / V2: P2 보안감사 (22 V2: 11 NEW+11 §V2 EXTEND) / V3: P3 K8s+윤리 (K-038/K-048/K-056/K-065~068)

## 검증 상태
- Quality Gate: APPROVED ([DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-10 — 2026-06-03] genuine, AUTHORITY v1.2)
- LOCK 검증: 10/10 일치 (재정의 0, AP-10 DEFINED-HERE §V2.2 byte 무변경, cross-domain cite-only 3건 재정의 0, CFL-AP-001~007 무손상)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\
- Authority: 3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md (v1.2)
- Design: [[D2.0-03-Blue-Nodes]], [[D2.0-05-Agent-Workflow]] (아키텍처 LOCK)
