---
tags: [type/concept, tier/all, status/CORE, status/COND, status/EXP]
aliases: [모듈 분류, CORE/COND/EXP, 187 모듈]
created: 2026-06-11
---

# Module Classification (CORE / COND / EXP)

## 정의
VAMOS 187개 모듈의 status 분류 체계. **187 = Named 81 + COND 106** (D9 확정: Named 81 = I25+E16+S8+A7+B6+C7+D6+EVX6).
- **CORE**: 항상 활성(버전 게이트 내) — 예: I-1~I-6, I-8~I-11, C-1~C-3, D-1~D-2
- **COND**: 조건부 활성 — 예: I-7/I-12/I-22/I-23/I-25, A-4, E-13~E-16
- **EXP**: 실험적, V3 중심 — 예: I-18/I-21/I-24, B-1~B-2/B-4~B-6, C-4~C-7, D-3~D-6

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — 모듈 카탈로그·분모 187 정본
- [[T2-COND-Modules]] — COND 106개(CAT-A~G) 상세(2-2)
- [[T6-EXP-Modules]] — B/D/EVX 등 EXP 관리(6-10)
- [[T1-Auxiliary-Modules]] — I-Series 25개
- 전수 맵: [[MODULE-MAP]]

## 값·수치 (LOCK)
- 시리즈별 분포: I(CORE 17/COND 5/EXP 3), E(CORE 12/COND 4), S(CORE 1/EXP 7), A(CORE 2/EXP 5), B(CORE 1/EXP 5), C(CORE 3/EXP 4), D(CORE 2/EXP 4), EVX(CORE 5/EXP 1)
- ⚠️ 혼동 금지: COND 106(SOT 2 2-2 분류 체계) ≠ D2.0-01 카탈로그의 status=COND 모듈(I-7/I-12/I-22/I-23/I-25/S-8/A-4)
- 실행 모델: COND는 CORE 소비만 가능 — CORE→COND 역방향 import 금지(R7, vamos_lint VL-003)

## 버전별 차이
- V1: CORE 중심 ON / V2: COND 단계 활성 / V3: EXP 포함 전면 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §6 / `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` / `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\`
