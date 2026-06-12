---
tags: [tier/T3, module/I-series, module/COND, status/COND, version/V1, type/domain, lock/FREEZE]
aliases: [3-4, 워크플로우 자동화, Workflow-RPA]
tier: T3
domain: "3-4 Workflow-RPA"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-4_Workflow-RPA\\"
design_doc: "[[D2.0-05-Agent-Workflow]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / PHASE3_READY v2 (2026-04-19)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 DAG+NL+RPA | V2: P2 Desktop+SNS | V3: P3 Mobile+Team"
created: 2026-06-12
---

# 3-4 Workflow-RPA

## 한줄 요약
LangGraph StateGraph 기반 DAG 워크플로우 엔진과 브라우저/데스크톱 RPA를 구현 정본으로 관리하는 Tier 3 자동화 도메인.

## 핵심 정의
- 핵심 모듈: I-12 워크플로우 자동화 (D2.0-01~03 정의, COND CAT-G)
- DAG 12 노드 타입 + 트리거 7유형 + 상태 머신 PENDING→RUNNING→(SUCCESS|FAILED|CANCELLED|TIMEOUT)
- LLMNode failover: GPT-4o → Claude → Ollama (A-1 MultiBrain Adapter 연동)
- LOCK 카운트 다중 정의: distinct 24 / cells 24 / raw 86 (STEP_C 실측)

## LOCK 항목 (LOCK-WF-01~10, 10건)
- WF-01 DAG 노드 12타입(LLMNode~CodeNode, 추가만 허용) / WF-02 워크플로우 최대 노드 50개 (R-07-1)
- WF-03 Human Approval 타임아웃 10분/600초 (R-07-2) / WF-04 DAG 순환 금지(순환 감지 시 등록 거부)
- WF-05 LangGraph StateGraph·최대 동시 실행 10 / WF-06 트리거 7유형(Time/Event/Condition/Webhook/Manual/Conversation/Ambient)
- WF-07 브라우저 액션 10타입(navigate~execute_js, 추가만) / WF-08 데스크톱 액션 12타입(launch_app~clipboard, 추가만)
- WF-09 상태 머신 전이 변경 불가 / WF-10 RPA 보안: 샌드박스 필수·파일시스템 제한·자격증명 AES-256

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-Blue-Node]] — BN 런타임 (#5)
- [[T3-PKM]] — 지식 기반 워크플로우 템플릿 (#12) / [[T6-Agent-Teams]] — no-code builder→RPA (#75)
- [[T3-Dev-Tools]] — 자동화 파이프라인·CI/CD 통합 (B6 양방향)

## 제공 (Provides To)
- [[T3-Business-Model]] — 비즈니스 프로세스 자동화 (#14)
- [[T3-Health-EmotionAI]] — 웰니스 자동화 ↔ 번아웃 방지 자동화 (B5) / [[T3-Education]] — 학습 자동화 (U2 역참조)

## 횡단 개념 연결
- [[LangGraph-DAG-Engine]] — 실행 엔진 정본 (LOCK-WF-05) / [[Failover-Chain-Pattern]] — LLMNode 폴백 체인
- [[COND-CAT-G-Integration]] — I-12 카탈로그 / [[End-to-End-Request-Flow]] — Execute Phase 실행 엔진 역할

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-12 Workflow Builder (COND CAT-G)

## STEP7 매핑
- 출처: STEP7-N (44 N-ID, N-001~N-044)

## 버전별 범위
- V1: P1 DAG+NL+RPA / V2: P2 Desktop+SNS / V3: P3 Mobile+Team

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v1.2, [PHASE3_READY v2] 최종 확정 2026-04-19, STEP_C fully_converged)
- LOCK 검증: 10/10 일치 (LOCK 미재정의 선언 §2, V1 통산 158회+ 인용)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-4_Workflow-RPA\
- Authority: 3-4_Workflow-RPA\AUTHORITY_CHAIN.md (v1.2)
- Design: [[D2.0-05-Agent-Workflow]], D2.0-01~03 (I-12)
