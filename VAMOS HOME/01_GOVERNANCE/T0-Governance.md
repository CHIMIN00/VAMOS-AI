---
tags: [tier/T0, status/CORE, version/V0, type/domain, lock/ABSOLUTE]
aliases: [0-0, 거버넌스, Governance-Rules-Meta]
tier: T0
domain: "0-0 Governance-Rules-Meta"
sot_source: "D:\\VAMOS\\docs\\sot 2\\0-0_Governance-Rules-Meta\\"
design_doc: "[[D2.0-01-Overview]]"
quality_gate: "Phase 11 ALL-A VERIFIED"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 항시 | V2: 항시 | V3: 항시"
created: 2026-06-11
---

# 0-0 Governance-Rules-Meta

## 한줄 요약
VAMOS 전체의 거버넌스 메타 정보(R1~R11 규칙, LOCK/FREEZE 레지스트리, K-값, Phase 체크리스트)를 단일 정본으로 관리하는 Tier 0 도메인.

## 핵심 정의
- 모든 도메인(1-1~6-13)은 본 도메인 규칙을 **참조 전용**으로 사용, 변경은 0-0에서만 가능
- 정본 우선순위: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
- 버전 진화 V0(Scaffold)→V1(MVP)→V2(Pro)→V3(Enterprise), 모듈 분류 CORE/COND/EXP
- 비용 절대 상한: V1 ₩40,000 / V2 ₩93,000 / V3 ₩266,000 (월, ABSOLUTE LOCK)

## LOCK 항목 (L1~L15, 15건)
- L1 R1~R11 규칙 텍스트 (Part2 §1.3 원문) / L2 판단 실패 규칙 5건
- L3~L5 비용 상한 V1 ₩40K / V2 ₩93K / V3 ₩266K
- L6 5-Gate 순서: Policy→Approval→Cost→Evidence→SelfCheck / L7 9-State 전이 S0→S8
- L8 config LOCK 값 23건 / L9 K-값 레지스트리 (K-1~K-11) / L10 SLA 목표치
- L11 GO/NO-GO 합계 64건 / L12 Stage Gate 합계 204건
- L13 SOURCE_CONFLICT 해결 15건 (재오픈 금지) / L14 산출물 파일 43개 / L15 정본 우선순위 체계

## 의존성 (Depends On)
- [[T5-Benchmark]] — 벤치마크 실행/측정 결과 소비 (T5→ALL)

## 제공 (Provides To)
- ALL 35개 도메인 — R1~R11 규칙, LOCK/FREEZE 레지스트리 (T0→ALL, DEPENDENCY_GRAPH §2 #1)

## 횡단 개념 연결
- [[VAMOS-Authority-Chain]] — 문서 위계 정본 소유
- [[LOCK-Mechanism]] / [[Decision-Lock]] — LOCK/FREEZE 체계 정의
- [[Cost-Limits]] — 비용 절대 상한 정본
- [[VAMOS-Version-Strategy]] — V0→V3 진화 원칙

## 관련 모듈 시리즈
- [[MODULE-MAP]] — CORE/COND/EXP 3단계 분류 원칙의 정본 출처

## STEP7 매핑
- 출처: Part2 §1 Foundation (L1-191) + §7 Validation (L6143-6450) — STEP7 카테고리 외 메타 도메인

## 버전별 범위
- V1~V3: 항시 적용 (거버넌스는 버전 무관 상시 정본)

## 검증 상태
- Quality Gate: Phase 11 ALL-A VERIFIED
- LOCK 검증: 15/15 일치 (AUTHORITY_CHAIN §2 실측)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\
- Authority: 0-0_Governance-Rules-Meta\AUTHORITY_CHAIN.md (v1.0)
- Design: [[D2.0-01-Overview]], Part2 §1/§7
