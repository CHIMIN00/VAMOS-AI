---
tags: [type/implementation, version/V1, version/V2, version/V3]
aliases: [릴리스 트랙 맵, R1-R6 라운드, STEP7 우선순위]
description: "STEP7 처리 라운드 R1~R6 → V1/V2/V3 매핑 — STEP7_STEP6통합_마스터인덱스 우선순위 표 기준"
created: 2026-06-11
---

# Release Track Map (STEP7 R1~R6 → V1/V2/V3)

## 한줄 요약
STEP7 미적용 1,485건을 우선순위(CRITICAL~LOW)×버전(V1~V3)으로 R1~R6 라운드에 배분하는 처리 계획.

## 우선순위 분포 (마스터인덱스 §1 — 정정 전 추정치)
| 우선순위 | V1 | V2 | V3 | 합계 |
|---------|-----|-----|-----|------|
| CRITICAL | ~120 | ~80 | ~38 | ~238 |
| HIGH | ~350 | ~250 | ~86 | ~686 |
| MEDIUM | ~180 | ~220 | ~88 | ~488 |
| LOW | ~20 | ~60 | ~36 | ~116 |
| **합계** | **~670** | **~610** | **~248** | **1,545** |

## 처리 라운드 계획 (R1~R6)
| 라운드 | 대상 | 예상 건수 | 누적 |
|--------|------|----------|------|
| R1 | V1 + CRITICAL | ~120건 | 120 |
| R2 | V1 + HIGH | ~350건 | 470 |
| R3 | V1 + MEDIUM/LOW | ~200건 | 670 |
| R4 | V2 + CRITICAL/HIGH | ~330건 | 1,000 |
| R5 | V2 + MEDIUM/LOW | ~280건 | 1,280 |
| R6 | V3 전체 | ~248건 | 1,528 |
| 미분류 | 범위/참조 항목 | ~17건 | 1,545 |

## ⚠️ 실측 불일치 (2026-06-11)
- K/L/M 유령 ID 60건 정정으로 STEP7 실총계는 **1,485건**. 위 표의 분포·누적치(~표기)는 정정 전 총계(1,545) 기준 추정치이며, 60건의 버전/우선순위 귀속은 실측 불가 — 재배분 미반영.

## 연결
- [[STEP7-Implementation-Bridge]] — 카테고리(A~P)별 건수·설계문서 매핑
- [[STEP6-Completed-Items]] / [[VAMOS-Version-Strategy]] / [[Current-Phase]]

## 원본
- `D:\VAMOS\docs\sot\STEP7_STEP6통합_마스터인덱스.md` §1 (우선순위 분포·처리 라운드 계획)
