# VAMOS 컨텍스트 로딩 맵 (Phase별)

> **생성**: Phase 2-7 (2026-06-11) · **근거**: STRATEGY_11 §3 용도별 분류 + 로드맵 A13 (STRATEGY_03)
> **용도**: 새 대화/세션 시작 시 "무엇을 읽혀야 하는가"의 단일 참조. CLAUDE.md §28.3과 동기.

## 공통 (모든 세션)

```
1. D:\VAMOS\CLAUDE.md                          ← 자동 로딩 (946줄, §1~§28, GOLD 검증 2026-06-11)
2. D:\VAMOS\VAMOS Engineering\PROGRESS.md      ← 현재 상태 + 다음 작업 (A5)
```

## Phase별 추가 로딩 (A13 + STRATEGY_11 §3 실파일)

| Phase | 작업 | 추가 로딩 (우선순) |
|-------|------|------------------|
| 3 (R1/X1) | 런타임 결정 | ① `_targets\DECISION_REGISTER.md`(D1~D19) ② `docs\sot\D2.0-01~08` 해당 섹션 ③ `VAMOS HOME\00_HUB\LOCK-DECISION-REGISTRY.md` ④ 3-0 게이트 결정 기록 |
| 4 (V0 구현) | 코드 생산 | ① `docs\guides\...PART2` V0-STEP 해당부 ② `docs\sot\D2.1-D1~D8`(스키마)·`PHASE_B1~B7` ③ `backend\pyproject.toml`+`scripts\vamos_lint.py`(하네스) ④ STRATEGY_11 §3.4 ⑤ CPS_TEMPLATE.md |
| 5 (V0 검증) | 품질 평가 | ① `benchmarks\golden_set\`(v2 실데이터 162) + `scripts\verify_golden_set.py` ② `.claude\skills\final-review·quality-gate` ③ STRATEGY_11 §3.5 ④ READINESS V0 GO/NO-GO 16건 |
| 6 (V1) | 기능 구현 | ① V0 완료 결과(PROGRESS+retro) ② PART1 B.2 ③ PART2 V1-Phase 해당부 |
| 7 (V2) | Pro Server | ① V1 완료 결과 ② PART2 §4 ③ PHASE_B7(마이그레이션) ④ READINESS §4 + PART1 B.3 |
| 8 (V3) | Enterprise | ① V2 완료 결과 ② PART2 §5 ③ READINESS §5 + PART1 B.4 |

## 주제별 진입 (Phase 무관)

| 주제 | 읽을 것 |
|------|--------|
| 특정 도메인 설계 | CLAUDE.md §21 라우팅 → `docs\sot 2\{도메인}\AUTHORITY_CHAIN.md` → 종합계획서 |
| LOCK 값 확인 | CLAUDE.md §7/§20 → `VAMOS HOME\00_HUB\LOCK-DECISION-REGISTRY.md` → 도메인 AUTHORITY_CHAIN |
| 용어 충돌 | CLAUDE.md §23 → `docs\sot 2\0-0_Governance-Rules-Meta\GLOSSARY_CROSS_DOMAIN.md` |
| 의존성 | CLAUDE.md §25 → `docs\sot 2\0-0_Governance-Rules-Meta\DEPENDENCY_GRAPH.md` |
| 지식 그래프 탐색 | `VAMOS HOME\00_HUB\VAMOS-HOME.md` → Tier 노트 → 도메인 노트 (Obsidian) |
| 과거 결정 | `_targets\DECISION_REGISTER.md` → `VAMOS Engineering\decisions\` |

## 컨텍스트 과부하 방지 (PART1 D.2 준용)

- 1세션 = 1모듈/1기능. 전체 파일 로딩 금지 — 위 표의 해당 행만.
- 2,000줄 초과 정본은 섹션 지정 Read (예: "PART2 V0-STEP-3만").
- 수치 인용 전 실측(RULE-A2) — 본 맵은 "어디를 읽을지"만 정의, 값의 정본은 원본.
