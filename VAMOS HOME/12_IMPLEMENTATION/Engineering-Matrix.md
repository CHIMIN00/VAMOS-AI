---
tags: [type/implementation, tier/T0, status/CORE, version/V0]
aliases: [엔지니어링 매트릭스, STRATEGY 08, 기준점 매트릭스]
description: "VAMOS 엔지니어링 기준점 매트릭스 v1.1 요약 — STRATEGY_08 (108,821B, 14절 구조 실측 2026-06-12)"
created: 2026-06-12
---

# Engineering Matrix (엔지니어링 기준점 매트릭스 v1.1)

## 한줄 요약
VAMOS의 모든 엔지니어링 활동을 **목적(D/B/R/X) × 시점(Pre/Mid/Post/Feedback)** 2축으로 분류하는 기준 프레임워크 — 하네스 외 8개 영역까지 빠짐없이 수용 (v1.1 최종 확정, 2026-04-04).

## 2축 구조 (실측)
- **목적 축**: D 설계(Define) · B 구축(Build, AI 코드 생산) · R 작동(Run, 제품) · X 횡단(Cross, 3행 이상 관통)
- **시점 축**: 1 구현 전(Pre) · 2 구현 중(Mid) · 3 구현 후(Post) · F 피드백(역류)

## 셀 구성 (§4 — I/O 계약 포함)
| 행 | 셀 |
|----|-----|
| D | D1 설계 정합성 / D2 변경 추적·전파 / D3 설계↔코드 정합 |
| B | B1 환경 세팅 / B2a 하네스(린터·멱등성·CPS) / B2b 컨텍스트 관리 / B2c 다중언어 동기화 / B3 품질 평가 |
| R | R1 런타임 설계 / R2a 코어 / R2b 도메인 / R2c 프론트엔드 / R3 운영·모니터링 |
| X | X1 횡단 전략 / X2 횡단 실행 / X3 횡단 운영 |
| F | DF/BF/RF/XF 역류 프로토콜 (4행 공통) |

## 문서 구조 (14절)
§1 도출 근거(하네스 외 8영역) → §2 2축 정의 → §3 전체 구조도 → §4 셀 상세 → §5 흐름도·동시성 3원칙 → §6 역류 상세 → §7 버전 래퍼(V0~V3 스코프) → §8 X행 경계 판별 → §9 하네스 5계층 통합 맵 → §10 자동화 총괄 → §11 완료 기준 총괄 → §12 V0 E2E 시뮬레이션 → §13 외부 영역 매핑 → §14 스트레스 테스트 이력

## 연결
- [[Current-Phase]] — 현 Phase가 매트릭스 어느 셀인지 / [[VAMOS-Authority-Chain]] / [[VAMOS-HOME]]
- 설계 자산 맵: SOT·SOT2=D행, CLAUDE.md=B행, Obsidian KG=X1+D1

## 원본
- `D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md` (108,821B)
- 관련: 동일 폴더 `STRATEGY_09_HARNESS_ENGINEERING.md`, `P0-2_OBSIDIAN_MATRIX_MAPPING.md`
