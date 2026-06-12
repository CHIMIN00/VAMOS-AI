---
tags: [tier/T3, status/COND, version/V1, type/domain, lock/ABSOLUTE]
aliases: [3-9, 비즈니스 모델 전략, Business-Model-Strategy]
tier: T3
domain: "3-9 Business-Model-Strategy"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-9_Business-Model-Strategy\\"
design_doc: "[[D2.0-07-Safety-Cost]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / Phase 4 RECOVERY 5 §V3 EXTEND (2026-06-01)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 가격+구독 | V2: P2 시장분석 | V3: P3 글로벌"
created: 2026-06-12
---

# 3-9 Business-Model-Strategy

## 한줄 요약
가격 체계(7티어)·비용 상한·마켓플레이스 수수료율·GTM/재무 모델을 유일 구현 정본으로 관리하는 Tier 3 비즈니스 전략 도메인 (Part2 ABSENT — 적용·성장 전략 도메인).

## 핵심 정의
- 권한 체인 특이점: Part2 ABSENT — STEP7-H(78항목, Part 1~10)가 최상위 정본, sot 2/3-9가 유일 구현 정본
- 최종 티어 7단계 (C-7 해결): Free $0 / Core API실비 / Pro $15 / Power $25 / Team $20/user / Enterprise $35/seat(최소 10석) / API 사용량 기반
- 서브폴더 5개: 01 pricing-revenue / 02 market-analysis / 03 gtm-growth / 04 financial-modeling / 05 kpi-dashboard

## LOCK 항목 (LOCK-BM-01~10, 10건)
- BM-01 V1 월 상한 ₩40,000 / BM-02 V2 월 상한 ₩93,000 / BM-03 V3 월 상한 ₩266,000
- BM-04 과금 단위 토큰 기반(API)+월 구독(SaaS) / BM-05 SLA Enterprise 99.9%
- BM-06 Free Tier 일일 LLM 요청 50회 / BM-07 Pro $15/mo (연간 $144, 20% 할인)
- BM-08 Enterprise $35/seat/mo 최소 10석 / BM-09 마켓플레이스 수수료 70% 개발자/30% VAMOS (S7H-021)
- BM-10 가격 변경 30일 사전 고지 (R-12-2)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-Blue-Node]] — BN 런타임 (#5)
- [[T3-PKM]] — 투자 지식 분석 데이터 (#13) / [[T3-Workflow-RPA]] — 비즈니스 프로세스 자동화 (#14)
- [[T3-Health-EmotionAI]] — 투자 감정 가드 FOMO/fear (#16) / [[T3-Agent-Protocol]] — 마켓플레이스 비즈니스 모델 (#18)
- [[T4-Rust-Tauri]] — 인프라 비용→가격 원가 (#20) / [[T4-MLOps]] — LLM API 비용 최적화 (#28)

## 제공 (Provides To)
- 단방향 제공 간선 0 (의존성 그래프 §2.3 종단 소비 도메인)
- 단, LOCK-BM-09 정본 cite-only 제공: [[T4-MCP]] 마켓 정책 / [[T3-Dev-Tools]] VADD / [[T3-Agent-Protocol]] agent_marketplace

## 횡단 개념 연결
- [[Cost-Limits]] — BM-01~03 비용 절대 한도 정본 연동 / [[VAMOS-Version-Strategy]] — V1/V2/V3 가격 게이트
- [[SLA-Performance-Targets]] — Enterprise 99.9% (BM-05)

## 관련 모듈 시리즈
- [[MODULE-MAP]] — 직접 모듈 없음 (비기술 전략 도메인, KPI 대시보드 횡단)

## STEP7 매핑
- 출처: STEP7-H (78항목, S7H-001~078, Part 1~10) — sha256 UNCHANGED

## 버전별 범위
- V1: P1 가격+구독 / V2: P2 시장분석 (V2 §E 11파일/33항목) / V3: P3 글로벌 (5 §V3 EXTEND +32,582B: revenue/gtm/growth/financial/kpi)

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v1.2, Phase 4 RECOVERY genuine write 2026-06-01, V1+V2 prefix EXACT 5/5, RO 16)
- LOCK 검증: 10/10 일치 (변경 0건 유지, LOCK-BM-09 정본 불변, CONFLICT 13건 전체 RESOLVED)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-9_Business-Model-Strategy\
- Authority: 3-9_Business-Model-Strategy\AUTHORITY_CHAIN.md (v1.2)
- Design: [[D2.0-07-Safety-Cost]] (비용 상한 연동), 상세명세 §2.3 (티어 가격)
