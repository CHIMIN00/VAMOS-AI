---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-C, Ops/Infra COND, OpsInfraMixin, E-Ops]
created: 2026-06-12
---

# COND CAT-C: Ops/Infra (53개)

## 정의
COND 106개 중 운영/인프라 카테고리 53개 — **7개 CAT 중 최대**. `OpsInfraMixin`으로 Blue Node에 운영·모니터링·인프라 능력을 제공한다. 모듈 ID 범위 **#27-#34, #35-#73(E-Ops 하위그룹 39 포함), #74-#79**. 주요 의존성: Prometheus, Redis, PostgreSQL.

## 구성
| 하위 범위 | 수 | 비고 |
|---|---|---|
| #27-#34 | 8 | 운영 기본 |
| #35-#73 | 39 | E-Ops 하위그룹 ("E-0XX 운영" — 구체 시나리오 보강 대상, 계획서 핵심 문제 #2) |
| #74-#79 | 6 | 인프라 보조 |

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T6-Operations]] — 운영/장애대응(6-13) 실행 연계
- [[T4-CICD]] — 배포/파이프라인 인프라 연계
- [[T6-Event-Logging]] — Prometheus/Loki 등 관측 스택 공유

## 값·수치 (LOCK 여부)
- COND 합산 (CLAUDE.md §6 정본): CAT-C **53** (13+13+53+8+7+8+4=106)
- 실행 모델: COND는 CORE 소비만 가능 — CORE→COND 역방향 import 금지 (R7, vamos_lint VL-003)

## 버전별 차이
- 조건부 실행, 버전 게이트 Mixed — 인프라 스택은 V1 SQLite/JSONL → V2 Postgres/Docker → V3 K8s/Loki 전환을 따름

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_종합명세.md` / CAT-C 하위 (E-Ops 하위그룹 포함)
