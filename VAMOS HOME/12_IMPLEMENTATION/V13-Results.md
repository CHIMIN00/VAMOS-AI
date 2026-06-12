---
tags: [type/implementation, version/V0]
aliases: [v13 결과, v13 검증 산출물, D1 검증]
description: "v13 검증 라운드 산출물 — 04. 구현단계\\v13_results 실측 381파일 (D1 검증 포함)"
created: 2026-06-12
---

# V13 Results (v13 검증 산출물 — 현재 라운드)

## 한줄 요약
v8~v12 전 라운드 재검증을 phase별로 통합한 현행 종합 파이프라인 + **D1 검증 산출물(phase0)** — D1 PASS (CONDITIONAL, 판정 2026-06-04 · 감사 정정 2026-06-05), 총 381개 파일 (실측 2026-06-12).

## 폴더 구조 (ls 실측)
경로: `D:\VAMOS\04. 구현단계\v13_results\`

| 하위 폴더/파일 | 파일 수 | 목적 (1줄) |
|---------------|---------|-----------|
| phase0 | 181 | **D1 검증** — 루트 10파일(D1_RESULTS_INDEX.md·D1_VERDICT.json·sot_conflict_report 등) + cross_match 22 / extraction 50 / fixes 20 / integrity 2 / _d1 9(결정론 엔진) / _targets 68 |
| pass2 | 15 | 2차 패스 산출물 |
| phase1_v6 ~ phase7_v12 | 20/26/19/21/26/16/41 | v6~v12 라운드별 재검증분 |
| phase8 | 15 | 마감 phase 산출물 |
| 루트 1파일 | 1 | normalize_ea.py |
| **합계** | **381** | |

## D1 검증 핵심 (D1_RESULTS_INDEX.md 실측)
- 값 게이트 5/5 PASS: active CONFLICT 0 / SOT↔SOT2 MISMATCH 0 / LOCK MISMATCH 0 / SDV-1 critical 0 / snapshot 2,654
- 비차단 이연: SDV-4 WARN 1 (5-3) + BROKEN 1 (네비) — 자동 정본 변경 0 원칙

## 연결
- [[V8-Results]] / [[V9-Results]] / [[V10-Results]] / [[V11-Results]] / [[V12-Results]]
- [[Current-Phase]] / [[SOT-Consistency-Audits]] / [[39-FILE-MASTER-INDEX]]

## 원본
- `D:\VAMOS\04. 구현단계\v13_results\` (D1 판정 정본: `phase0\D1_RESULTS_INDEX.md` + `phase0\D1_VERDICT.json`)
