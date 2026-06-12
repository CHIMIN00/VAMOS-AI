---
tags: [type/implementation, version/V0]
aliases: [v10 결과, v10 검증 산출물]
description: "v10 검증 라운드 산출물 — 04. 구현단계\\v10_results 실측 149파일"
created: 2026-06-12
---

# V10 Results (v10 검증 산출물)

## 한줄 요약
43개 SRC 전수 추출 기반 Feature Registry 3,940건 구축 + PART2 v22.0.0→v23.0.0 반영 라운드 — 9개 완료조건 전부 PASS (checkpoint 2026-03-11), 총 149개 파일 (실측 2026-06-12).

## 폴더 구조 (ls 실측)
경로: `D:\VAMOS\04. 구현단계\v10_results\`

| 하위 폴더/파일 | 파일 수 | 목적 (1줄) |
|---------------|---------|-----------|
| phase0-a ~ phase0-f | 1/2/15/9/3/3 | Phase 0 분할 — 레지스트리·SRC 전수 읽기·V8/V9 재검증 등 |
| phase1 | 40 | M-1(V0)~M-5b 매핑 — extractable 3,390건 100% 매핑 |
| phase15 | 3 | Phase 1.5 적대적 재검증 (FP/FN 감사) |
| phase2 | 69 | PART2 반영 — TRUE_MISSING 200건 삽입·패치·재검증 |
| 루트 4파일 | 4 | D2.0-03/04/05_features.json + v10_checkpoint.md |
| **합계** | **149** | |

## 핵심 결과 (v10_checkpoint.md 실측)
- Feature Registry 3,940건 / MISSING BLOCKER 0건 / 1,001건 전수 커버(EXACT 11 + UPPER 514 + RECLASSIFIED 276 + TRUE_MISSING 200)
- 구조 무결성 PASS (heading·테이블 산술·LOCK 값·ID 참조)

## 연결
- [[V8-Results]] / [[V9-Results]] / [[V11-Results]] / [[V12-Results]] / [[V13-Results]]
- [[Part2-Master-Reference]] / [[Current-Phase]]

## 원본
- `D:\VAMOS\04. 구현단계\v10_results\` (판정 정본: `v10_checkpoint.md`)
