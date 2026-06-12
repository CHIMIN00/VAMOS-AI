---
tags: [type/guide, version/V0]
aliases: [구현가이드 PART1, 진입전 가이드]
description: "VAMOS 구현가이드 PART1 진입전 — A~E 섹션 구조 (실측 2026-06-12)"
created: 2026-06-12
---

# Implementation Part 1 (구현가이드 PART 1 — 구현단계 진입전)

## 한줄 요약
코드 착수 **전**에 해소해야 할 오류·준비사항·결정사항·방법론·체크리스트를 A~E 5개 섹션으로 정리한 진입전 가이드.

## A~E 섹션 구조 (실측)
| 섹션 | 내용 |
|------|------|
| **A. 산출물 오류 총정리** | BLOCKER 14건(진입 불가) / HIGH 70건(V1 출시 불가) / MEDIUM 87건 / LOW 33건 + 총 요약 |
| **B. 사용자 직접 준비사항** | B.1 V0 즉시(필수) → B.2 V1 MVP 전 → B.3 V2 서버/인프라(비용 발생) → B.4 V3 고급 인프라 → B.5 전체 비용 요약 |
| **C. 미결정사항 + 최종 결정** | V0 전 13건 / V1 중 13건 / V2 이후 5건 + **C.4 LOCK 확정 핵심 57항목(변경 불가)** |
| **D. AI와 함께 코딩하는 방법론** | D.0 CLAUDE.md 수정 필수 → D.1 활용 → D.2 세션 컨텍스트 → D.3 워크플로우 → D.4 지시 팁 → D.5 파일 단위 순서 → D.6 버전 관리 |
| **E. 진입전 최종 체크리스트** | E.1 즉시 액션 / E.2 BLOCKER 14건 문서 수정(+E.2.5 CLAUDE.md 검증, E.2.6 극고위험 2건 해결 완료) / E.3 환경 검증 / E.4 문서 이해도 / E.5 기타 |

## 위치 부여
- [[Implementation-Part2]](구현단계 진입)의 선행 문서 — PART1 체크리스트 통과 후 V0-STEP-1 착수
- LOCK 57항목은 [[LOCK-DECISION-REGISTRY]]·[[Decision-Lock]]과 교차

## 연결
- [[Implementation-Part2]] / [[Beginner-Guide]] / [[Part2-Master-Reference]]
- [[LOCK-DECISION-REGISTRY]] / [[Cost-Limits]] / [[Current-Phase]]

## 원본
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md`
