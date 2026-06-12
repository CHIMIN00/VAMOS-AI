---
tags: [tier/T5, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [5-3, v12 추가사항, v12-Additions-Detail]
tier: T5
domain: "5-3 v12-Additions-Detail"
sot_source: "D:\\VAMOS\\docs\\sot 2\\5-3_v12-Additions-Detail\\"
design_doc: "[[Part2-Master-Reference]]"
quality_gate: "APPROVED — Phase 8 QC B+ / Phase 10 QC A-, C-04~C-08 전건 RESOLVED (2026-06-11)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 인덱스 허브 확립 | V2/V3: 타겟 도메인 추적만 (구현 Phase 영구 제외)"
created: 2026-06-12
---

# 5-3 v12-Additions-Detail

## 한줄 요약
v12 추가 항목 51건을 각 도메인 정본 폴더로 연결·추적하는 횡단 인덱스 허브 — 원본은 항상 해당 도메인 sot 2/ 폴더에 유지.

## 핵심 정의
- 인덱스 허브 원칙(R-19-1): "v12 항목은 해당 도메인 sot 2/ 폴더에 원본 유지, 여기는 인덱스만"
- 매핑 테이블: 51건 전체 (24건 확정 + 27건 잠정, 부록 §A)
- 구현 Phase 영구 제외: `permanently_excluded_design_decision` (메타 허브 — Phase 4 비대상, 2026-06-11 명기)
- 충돌 전건 해소: **C-04~C-08 5건 전건 RESOLVED (2026-06-11)** — C-04 CBT 정본=3-6 §4.1 / C-05 Zettelkasten 링크 5종(PKM §A.3) / C-06 현금비중 5%/20% 맥락 구분 / C-07 TS 3종=D2.0-03 §4.2+LOCK-BN-18 / C-08 tau=0.025 단일 정본

## LOCK 항목 (LOCK-V12-01~10, 자체 2 + 상속 8)
- 자체: V12-01 도메인 귀속 원칙(R-19-1) / V12-10 매핑 테이블 51건(R-19-2)
- 상속: V12-02 SM-2(#6 PKM) / V12-03 Black-Litterman tau=0.025(AI Investing) / V12-04 Factor 6종(AI Investing) / V12-05 CBT 15유형(#9 HW) / V12-06 호흡 4-7-8(LOCK-HW-07) / V12-07 TemplateSets 3종(2-1 LOCK-BN-18, C-07 판정으로 출처 정정) / V12-08 Portfolio 비중 10%/30%(AI Investing) / V12-09 Zettelkasten 원자 노트(#6 PKM)

## 의존성 (Depends On)
- 상속 LOCK 원본 도메인 — [[T3-PKM]] / [[T3-Health-EmotionAI]] / [[T2-Blue-Node]] / [[AI-Investing-Overview]] (원본 변경 시 자동 상속)

## 제공 (Provides To)
- 14개 타겟 도메인 — v12 추가 항목 추적 인덱스 (T5→multi): [[T3-PKM]] / [[T3-Workflow-RPA]] / [[T3-Education]] / [[T3-Health-EmotionAI]] / [[T3-Dev-Tools]] / [[T3-A2A-Protocol]] / [[T3-Business-Model]] / [[T4-MLOps]] / [[AI-Investing-Overview]] 등

## 횡단 개념 연결
- [[Module-Classification]] — v12 항목의 CORE/COND/EXP 귀속 / [[LOCK-Mechanism]] — 상속 LOCK 전파 프로토콜

## STEP7 매핑
- 출처: Part2 §6.1/§6.7/§6.8/§6.10 + V2/V3 Phase (1줄 설명만 산재 — PARTIAL)

## 버전별 범위
- V1: 인덱스 허브 + LOCK 상속 체계 확립 / V2/V3: 타겟 도메인별 항목 추적 (자체 구현 없음 — 영구 제외)

## 검증 상태
- Quality Gate: APPROVED — Phase 8 QC B+ (2026-03-26) / Phase 10 QC A- (2026-03-27)
- LOCK 검증: 10/10 일치 (AUTHORITY_CHAIN 2026-06-11 갱신), CONFLICT C-04~C-08 OPEN 0

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\
- Authority: 5-3_v12-Additions-Detail\AUTHORITY_CHAIN.md
- 구현 인덱스 노트: [[v12-Additions]]
