# VAMOS 로드맵 검증 체계 — 선택지 B: 교차 참조 방식

> **작성일**: 2026-04-04
> **목적**: 로드맵 Phase 0~6과 기존 거버넌스 613건의 교차 참조 + 24건 검증 갭 해소
> **방식**: 선택지 B — 로드맵과 기존 체크리스트를 별도 유지하되 교차 참조 테이블로 연결
> **상태**: 최종 확정

---

## 목차

1. [설계 자산 전체 맵](#1-설계-자산-전체-맵)
2. [기존 거버넌스 613건 ↔ 로드맵 Phase 매핑](#2-기존-거버넌스-613건--로드맵-phase-매핑)
3. [GO/NO-GO ↔ Phase Gate 통합 관계](#3-gono-go--phase-gate-통합-관계)
4. [Phase별 검증 체크리스트 (24건 갭 해소)](#4-phase별-검증-체크리스트-24건-갭-해소)
5. [스킬 커버리지 맵 — 현재 vs 필요](#5-스킬-커버리지-맵--현재-vs-필요)
6. [Phase 간 인수인계 프로토콜](#6-phase-간-인수인계-프로토콜)
7. [Phase 간 회귀 감지 규칙](#7-phase-간-회귀-감지-규칙)
8. [24건 해소 추적표](#8-24건-해소-추적표)

---

# 1. 설계 자산 전체 맵

```
VAMOS 설계 자산 — 완전한 그림:

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  [원본 계층]              [요약/접근 계층]        [지식 그래프 계층]      │
│                                                                         │
│  SOT 68개 ──────────→  CLAUDE.md  ←──────────  VAMOS HOME              │
│     │ 89,413줄            697줄→~953줄           120+ 노트              │
│     │                     (AI가 읽는 요약)        (사람이 탐색하는 KG)   │
│     ▼                         ↑                       ↑                 │
│  SOT 2 2,654개 ───────────────┘───────────────────────┘                 │
│     │ 169,628줄                                                         │
│     ▼                                                                   │
│  PART2 구현가이드 ────→ 코드 생성 지시                                   │
│     4,700줄                                                             │
│                                                                         │
│  [거버넌스 계층]                                                         │
│                                                                         │
│  PART1 체크리스트 ──→ 31+38+13건 = 82건 (진입전 검증)                    │
│  GO/NO-GO ──────────→ 62건 (버전별 게이트)                              │
│  LOCK Registry ─────→ 469건 (변경 불가 결정)                             │
│                      합계: 613건                                        │
│                                                                         │
│  [엔지니어링 계층]                                                       │
│                                                                         │
│  매트릭스 v1.0 ────→ 20개 셀 (전체 작업 분류)                            │
│  하네스 계획서 ────→ D1+B행 상세 (AI 코드 생산 품질)                     │
│  로드맵 ───────────→ Phase 0~6 (실행 순서)                              │
│  본 문서 ──────────→ 검증 체계 (교차 참조 + 갭 해소)                     │
│                                                                         │
│  [도구 계층]                                                             │
│                                                                         │
│  검증 스킬 11개 ───→ SOT/SOT2/EA/CM 검증 (D행 + B행 일부)               │
│  Hook 6개 ─────────→ EA/CM/SOT 파일 자동 검증                           │
│  린터 (미생성) ────→ ruff + vamos_lint (B2a)                            │
│  Eval (미연결) ────→ ragas + deepeval + promptfoo (B3)                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 2. 기존 거버넌스 613건 ↔ 로드맵 Phase 매핑

## PART1 Section E: 진입전 체크리스트 31건

| 섹션 | 건수 | 해당 Phase | 확인 시점 | 현재 상태 |
|------|------|-----------|----------|----------|
| E.1 즉시 액션 | 9건 | Phase 2 (B1 환경 세팅) 전 | B1 착수 전 재확인 | 전부 PASS (2026-03-02) |
| E.2 BLOCKER 해소 | 14건 | Phase 1 (D1) 내 1-8 | D1 실행 시 재검증 | 전부 PASS (2026-03-02) |
| E.3 환경 검증 | 8건 | Phase 2 (B1) 전 | B1 착수 전 재확인 | 전부 PASS (2026-03-02) |
| E.4 문서 이해도 | 9건 | Phase 0 (전체 그림 확정) | Phase 0 시 참조 | 전부 PASS (2026-03-02) |
| E.5 기타 준비 | 5건 | Phase 2 (B1) 전 | B1 착수 전 재확인 | 전부 PASS (2026-03-02) |

> **주의**: 전부 PASS이지만 2026-03-02 기준. SOT 2 작업으로 E.2 BLOCKER 상태가 변경되었을 수 있음 → D1에서 재검증 필요

## PART1 Section B: 사용자 준비사항 38건

| 섹션 | 건수 | 해당 Phase | 확인 시점 |
|------|------|-----------|----------|
| B.1 V0 준비 (API+SW+HW+결정) | 9건 | Phase 2 (B1) 전 | B1 착수 전 |
| B.2 V1 추가 (API+SW+GitHub) | 12건 | Phase 6 (V1) 전 | V1 착수 전 |
| B.3 V2 추가 (서버+API+Secrets) | 14건 | V2 착수 전 | V2 착수 전 |
| B.4 V3 추가 (K8s+GPU) | 3건 | V3 착수 전 | V3 착수 전 |

## PART1 Section C: 미결정사항 13건

| 상태 | 건수 | 해당 Phase |
|------|------|-----------|
| 전부 RESOLVED | 13건 | 해당 없음 (이미 결정됨) |

> Phase 0에서 결정값이 매트릭스/로드맵과 일치하는지 확인만 필요

## READINESS_GUIDE: GO/NO-GO 62건

| 게이트 | 건수 | 해당 Phase | 확인 시점 |
|--------|------|-----------|----------|
| V0 GO/NO-GO | ~15건 | Phase 4 완료 시 | Phase 5 진입 전 |
| V1 GO/NO-GO | ~20건 | Phase 6 완료 시 | V1 릴리스 전 |
| V2 GO/NO-GO | ~15건 | V2 완료 시 | V2 릴리스 전 |
| V3 GO/NO-GO | ~12건 | V3 완료 시 | V3 릴리스 전 |

## LOCK Registry: 469건

| 네임스페이스 | 건수 | 해당 Phase | 확인 시점 |
|-------------|------|-----------|----------|
| DEC-001~017 (아키텍처) | 10건 | Phase 3 (R1) | R1 결정 시 대조 |
| LOCK-GOV (거버넌스) | 15건 | Phase 1 (D1) | D1 검증 시 |
| 도메인별 28개 NS | ~444건 | Phase 4~6 | 해당 모듈 구현 시 |

---

# 3. GO/NO-GO ↔ Phase Gate 통합 관계

```
관계 정의: 별도 유지 + 교차 확인

  로드맵 Phase Gate          GO/NO-GO Gate
  (엔지니어링 관점)          (제품 관점)
  ─────────────────         ─────────────────
  Phase 0 완료 조건    ←──→  해당 없음 (GO/NO-GO는 제품 기준)
  Phase 1 완료 (D1 PASS) ←→  해당 없음
  Phase 2 완료 (B1)    ←──→  해당 없음
  Phase 3 완료 (R1+X1) ←──→  해당 없음
  Phase 4 완료 (V0)    ←──→  V0 GO/NO-GO (~15건) ← 동시 확인
  Phase 5 완료 (검증)  ←──→  V0 GO/NO-GO 최종 판정
  Phase 6 완료 (V1)    ←──→  V1 GO/NO-GO (~20건) ← 동시 확인

규칙:
  ① Phase 완료 = 로드맵 완료 조건 충족
  ② GO/NO-GO 통과 = READINESS_GUIDE 게이트 항목 충족
  ③ 버전 릴리스 = ① + ② 둘 다 충족 필수
  ④ Phase는 통과했지만 GO/NO-GO가 FAIL → 릴리스 불가 (GO/NO-GO 항목 수정 후 재확인)
  ⑤ GO/NO-GO는 통과했지만 Phase가 미완료 → 릴리스 불가 (Phase 작업 완료 필요)
```

---

# 4. Phase별 검증 체크리스트 (24건 갭 해소)

## Phase 0 검증 체크리스트

```
0-V1: 매트릭스 완전성 검증 (#1 해소)
  □ 매트릭스 20개 셀이 VAMOS 전체 작업을 빠짐없이 커버하는가?
  □ CLAUDE.md 역할이 매트릭스에 명시되어 있는가?
  □ Obsidian 역할이 매트릭스에 명시되어 있는가?
  □ 하네스 5계층 ↔ 매트릭스 셀 매핑이 양방향 완전한가?
  □ 기존 613건 거버넌스가 Phase에 매핑되어 있는가? (#18 해소)

0-V2: 5개 계획서 목차 완전성 (#15 부분 해소)
  □ ② 설계정합성 계획서 목차: D2, D3, DF 범위 커버?
  □ ③ 런타임 계획서 목차: R1, R2a, R2b, RF 범위 커버?
  □ ④ 다중스택 계획서 목차: B2c, R2c 범위 커버?
  □ ⑤ 횡단 계획서 목차: X1, X2, X3, XF 범위 커버?
  □ ⑥ 운영 계획서 목차: R3 범위 커버?

0-V3: 로드맵 자체 검증 (#17 해소)
  □ Phase 순서가 매트릭스 의존관계와 일치하는가?
  □ 병렬 표시된 작업이 실제로 I/O 의존 없는가?
  □ PART1 Section E 31건이 해당 Phase에 매핑되어 있는가?
  □ GO/NO-GO 62건과 Phase Gate 관계가 정의되어 있는가? (#23 해소)
  □ Section C 13건 결정값이 로드맵과 모순 없는가?

검증 방법: 수동 체크리스트 (매트릭스 대조)
```

## Phase 1 검증 체크리스트

```
1-V1: 검증 도구 사전 확인 (#12 해소)
  □ /sot-conflict scan 실행 → 알려진 7건 감지 여부 확인 (golden test)
  □ /sot2-cross-ref all 실행 → 기존 결과와 일관성 확인
  □ /validate sot2-all 실행 → DV-1~9 정상 동작 확인

1-V2: D1 검증 완전성 (#2, #15 해소)
  □ 1-6 CLAUDE.md 검증: /sot-check method-c 사용 → SOT 대비 GAP 목록 생성
  □ 1-7 Obsidian 검증: Strategy v3.0의 도메인 수/모듈 수가 SOT 2 최신과 일치?
     → 수동 체크 (120+ 노트 구조 vs SOT 2 36개 도메인 대조)
  □ 1-8a BLOCKER 수정 후 재검증: 1-2~1-5 해당 범위 재실행 (#3 해소)

1-V3: D1 완료 판정
  □ CONFLICT 0건 (CRITICAL) — /sot-conflict scan
  □ MISMATCH 0건 (CRITICAL) — /sot-conflict sot2-vs-sot
  □ SOT 2 교차참조 무결 — /sot2-cross-ref all
  □ BLOCKER 14건 재확인 — PART1 E.2 상태 재검증
  □ CLAUDE.md GAP 목록 생성 — Phase 2 입력으로 전달
  □ Obsidian GAP 목록 생성 — Phase 2 입력으로 전달
  □ integrity_snapshot.json 저장 — D2 기준선

검증 방법: 기존 스킬 (/sot-conflict, /sot2-cross-ref, /validate, /sot-check, /integrity)
```

## Phase 1→2 인수인계 검증 (#13 해소)

```
1→2-H: Phase 1 산출물이 Phase 2 입력으로 전달되는가?
  □ sot_conflict_report.json → Phase 2에서 CLAUDE.md 보강 시 참조?
  □ claude_md_gap_report → Phase 2-1 (CLAUDE.md 보강) 입력으로 확인?
  □ obsidian_gap_report → Phase 2-3 (Obsidian 생성) 입력으로 확인?
  □ integrity_snapshot.json → Phase 2 이후 D2 감시 기준선으로 로드?
  □ blocker_resolution_log → Phase 2-4 (린터 설정) 시 참조?

검증 방법: 수동 확인 (파일 존재 + 내용 참조 확인)
```

## Phase 2 검증 체크리스트

```
2-V1: CLAUDE.md 보강 검증 (보강전략 8스킬 사용)
  □ /claude-md-sot-conflict → SOT 간 모순 0건
  □ /claude-md-hallucination → atomic claim 95%+ VERIFIED
  □ /claude-md-fact-audit → 3 Agent 토론 CONFIRMED
  □ /claude-md-cross-examine → 핵심 수치 근거 추적 PASS
  □ /claude-md-symbolic → 수학적 결정론 검증 (AI 0%)
  □ /claude-md-consensus → 50개 수치 3회 다수결 PASS
  □ /claude-md-completeness → SOT 대비 누락 0건
  □ /claude-md-final-review → SILVER+ 판정

2-V2: Obsidian 노트 검증 (#4, #21 해소)
  □ 노트 수: 120+ 개 생성 확인
  □ 도메인 노트: 36개 도메인 전부 노트 존재?
  □ 모듈 매핑: 187개 모듈이 MODULE-MAP과 일치?
  □ LOCK 항목: 각 도메인 노트의 LOCK이 Registry와 일치?
  □ 링크 무결성: [[wikilink]] 전부 유효? (깨진 링크 0건)
  □ 매트릭스 노트: 12_IMPLEMENTATION/Engineering-Matrix.md 존재?
  □ SOT 2 원본 대조: 노트 내용이 SOT 2 원본과 일치? (샘플 10% 확인)

  검증 방법: 수동 체크리스트 + Obsidian 링크 검증 플러그인

2-V3: 린터/CI 검증 (#5 해소)
  □ ruff 13룰이 PART2 line 1523~1536과 일치?
  □ vamos_lint VL-001~005가 CLAUDE.md §7 LOCK와 일치?
  □ CI yaml이 PART2 line 1410~1450과 일치?
  □ 린터 실행 시 기존 코드(없으면 테스트 파일)에서 오탐 0건?

  검증 방법: PART2 원본 대조 (수동) + 실행 테스트

2-V4: 외부 의존성 확인 (#16, #22 해소)
  □ PART1 Section E.1 (9건) 재확인 — 환경 변경 없었는지
  □ PART1 Section E.3 (8건) 재확인 — 버전 변경 없었는지
  □ PART1 Section B.1 (9건) 확인 — V0 준비 완료

  검증 방법: E.1 + E.3 체크리스트 재실행
```

## Phase 2→3 인수인계 검증

```
2→3-H: Phase 2 산출물이 Phase 3 입력으로 전달되는가?
  □ 보강된 CLAUDE.md → Phase 3 작업 시 AI 컨텍스트로 활성화?
  □ Obsidian 노트 → Phase 3 R1 설계 시 참조 가능?
  □ 린터/CI → Phase 4 코드 생산 시 자동 실행 준비?
  □ 컨텍스트 로딩 전략 맵 → Phase 3~4에서 사용 준비?
```

## Phase 3 검증 체크리스트

```
3-V1: R1 결정 vs SOT 정합 검증 (#6 해소 — CRITICAL)
  □ 5-Gate 순서: D2.0-07 정본과 일치?
     → /sot-check로 D2.0-07 해당 라인 직접 대조
  □ 메모리 L0~L3: D2.0-06 정본과 일치?
     → /sot-check로 D2.0-06 해당 라인 직접 대조
  □ Failover: D2.0-02 A-1 MultiBrain Adapter 정본과 일치?
  □ LangGraph DAG: PHASE_B5 정본과 일치?
  □ CostGate 임계값: D2.0-07 §4.2 LOCK (80%/100%)과 일치?
  □ IPC JSON-RPC: PHASE_B4 정본과 일치?
  □ MCP: DEC-017 Streamable HTTP LOCK과 일치?
  □ 7개 결정 전부 LOCK Registry에 등록 또는 기존 LOCK과 일치?

  검증 방법: /sot-check {SOT파일} {항목} 으로 직접 라인 대조
             + LOCK Registry 469건과 교차 확인

3-V2: X1 전략 vs SOT/PART2 정합 검증 (#7 해소)
  □ 보안 전략: D2.0-07 §3 (보안 정본) + BASE-1.3 (7개 불변) 일치?
  □ 테스트 전략: PART2 §3.5 (V1 Phase 5 테스트) 일치?
  □ 릴리스 전략: PLAN-3.0 §2 (V0~V3 로드맵) 일치?
  □ 문서화 전략: Obsidian Strategy v3.0과 일치?

  검증 방법: SOT 원본 수동 대조

3-V3: 계획서 검증
  □ ③ 런타임 계획서가 R1 7개 결정을 전부 반영?
  □ ⑤ 횡단 계획서가 X1 4개 전략을 전부 반영?

3-V4: Phase 3 회귀 검증 (#14 해소)
  □ R1 결정이 Phase 2 CLAUDE.md 내용과 모순 없는가?
     → CLAUDE.md §5 아키텍처 + §7 LOCK과 R1 결정 대조
  □ X1 전략이 Phase 2 린터 설정과 모순 없는가?
     → 테스트 전략의 커버리지 목표 vs CI yaml 설정 대조
```

## Phase 3→4 인수인계 검증

```
3→4-H:
  □ runtime_decisions.md → Phase 4 R2a 구현 시 참조?
  □ 4개 전략 문서 → Phase 4 X2 실행 시 참조?
  □ IPC 사양 → Phase 4 B2c 타입 동기화 입력?
  □ LOCK Registry에 신규 등록된 항목 → Phase 4 코드에 반영?
```

## Phase 4 검증 체크리스트

```
4-V1: 구현 중간 체크포인트 (#8 해소)
  □ V0-STEP-1 (스캐폴딩) 완료 → 디렉토리 구조 PHASE_B2와 일치?
  □ V0-STEP-2 (스키마) 완료 → 25개 Pydantic 모델 D2.1과 일치?
  □ V0-STEP-3 (config) 완료 → config.v1.toml 20개 LOCK 값 일치?
  □ V0-STEP-4 (IPC) 완료 → JSON-RPC 왕복 테스트 PASS?
  □ V0-STEP-5 (파이프라인) 완료 → 5-Phase 최소 동작?
  (각 STEP 완료 시 확인 — Phase 5까지 미루지 않음)

4-V2: B2c 타입 동기화 검증 (#9 해소)
  □ Pydantic → JSON Schema 추출 성공?
  □ JSON Schema → serde(Rust) 변환 일치?
  □ JSON Schema → TypeScript interface 변환 일치?
  □ JSON-RPC 왕복 테스트 (Python→Rust→Python) PASS?

4-V3: 하네스 자동 실행 확인
  □ 매 커밋 시 ruff check 자동 실행?
  □ 매 커밋 시 vamos_lint 자동 실행?
  □ 매 커밋 시 pytest 자동 실행?
  □ FAIL 시 커밋 차단?

4-V4: Hook 커버리지 확인 (#20 해소)
  □ 기존 Hook: EA/CM/SOT 파일 → 동작 확인
  □ 추가 필요: .py 파일 생성/수정 시 ruff 자동 실행
  □ 추가 필요: config.v1.toml 수정 시 LOCK 값 검증
  □ D2 감시: SOT 변경 시 /integrity 실행 권고 메시지

4-V5: D2 상시 감시 구체화 (#24 해소)
  □ SOT 파일 수정 → .claude Hook 트리거 → "/sot-conflict scan 실행 권장" 메시지
  □ SOT 2 파일 수정 → .claude Hook 트리거 → "/sot-conflict sot2-vs-sot 실행 권장" 메시지
  □ 코드가 SOT 참조를 변경하는 경우 → 수동으로 /sot-check 실행
```

## Phase 5 검증 체크리스트

```
5-V1: V0 GO/NO-GO 통합 확인 (#23 해소)
  □ 로드맵 Phase 5 완료 조건 전부 충족?
  □ READINESS_GUIDE V0 GO/NO-GO ~15건 전부 충족?
  □ 둘 다 충족 → V0 릴리스 가능 판정
  □ 하나라도 미충족 → 미충족 항목 수정 → 재확인

5-V2: X3 완료 기준 구체화 (#10 해소)
  □ 테스트 자동화: CI에서 pytest 자동 실행 확인
  □ 커버리지: 80%+ (로드맵 3-9 테스트 전략 기준으로 단일화, 2026-06-11)
  □ 브랜치: main 브랜치에 V0 코드 병합 완료
  □ commitlint: 최근 10개 커밋 전부 규칙 통과
```

## Phase 6 검증 (#11 해소)

```
6-V1: V1 전용 추가 검증
  □ D1' 범위: COND 106개 모듈 검증 추가 (V0에서는 26개만)
  □ B1' 린터: vamos_lint Layer 2 (187개 모듈 네이밍) 추가
  □ B3' 기준: QoD ≥ 0.70 + V1 전용 벤치마크 4개 (MMLU, HumanEval, MBPP, LogicKor)
  □ R3 검증: 모니터링 실제 동작 (SQLite 메트릭 + Alert 트리거 테스트)
  □ 버전 간 역류: V1 D1'에서 V0 결함 발견 시 "V0 회귀 항목"으로 등록 + V1 B2'에서 수정

6-V2: V1 GO/NO-GO
  □ READINESS_GUIDE V1 GO/NO-GO ~20건 확인
  □ PART1 Section B.2 (12건) V1 추가 준비 확인
  □ 비용: ≤ ₩40,000/월 확인
```

---

# 5. 스킬 커버리지 맵 — 현재 vs 필요

## 현재 스킬이 커버하는 매트릭스 셀

| 매트릭스 셀 | 사용 가능한 스킬 | 커버 수준 |
|------------|----------------|----------|
| D1 | /sot-conflict, /sot-check, /sot2-cross-ref, /validate, /integrity | ● 완전 |
| D2 | /integrity (변경 감지), /sot-conflict (재검증) | ● 완전 |
| D3 | /sot-check (대조), /cross-match (일관성) | ◐ 부분 (코드 대조는 스크립트 필요) |
| B1 | 해당 없음 (환경 세팅은 스킬 대상 아님) | — |
| B2a | 해당 없음 (린터/테스트는 별도 도구) | — |
| B2b | /sot-check method-c, /completeness-map sot2 | ● 완전 |
| B2c | 없음 | ✗ 없음 |
| B3 | /final-review, /quality-gate, ragas/deepeval (별도) | ◐ 부분 |
| R1 | /sot-check (SOT 대조 가능하나 R1 전용은 아님) | ◐ 부분 (#6) |
| R2a~R2c | 없음 (코드 검증은 린터/테스트) | ✗ 없음 (#19) |
| R3 | 없음 | ✗ 없음 |
| X1~X3 | 없음 (전략 문서 검증 스킬 없음) | ✗ 없음 (#19) |

## 필요하지만 없는 검증 (#19 해소 방향)

| 필요 검증 | 해소 방법 | 우선순위 |
|----------|----------|---------|
| R1 결정 vs SOT 대조 | /sot-check 확장 사용 (기존 스킬로 커버 가능) | Phase 3 시 |
| X1 전략 vs SOT 대조 | 수동 체크리스트 (전략 문서는 4개뿐) | Phase 3 시 |
| R2 코드 vs 설계 대조 | D3 스크립트 (Phase 5에서 실행) | Phase 5 시 |
| B2c 타입 동기화 | 통합 테스트 (JSON-RPC 왕복) | Phase 4 시 |
| Obsidian 품질 | 수동 체크리스트 + Obsidian 플러그인 | Phase 2 시 |

---

# 6. Phase 간 인수인계 프로토콜 (#13 해소)

```
모든 Phase 경계에서 실행:

  Step 1: 이전 Phase 산출물 목록 확인
    → 해당 Phase의 "출력" 항목 전부 파일로 존재하는가?

  Step 2: 다음 Phase 입력 확인
    → 다음 Phase의 "입력" 항목이 이전 Phase 산출물을 참조하는가?

  Step 3: 산출물 유효성 확인
    → 파일이 비어있지 않은가?
    → JSON 파일은 파싱 가능한가?
    → 판정 결과(PASS/FAIL)가 명시되어 있는가?

  Step 4: 인수인계 확인서 작성
    → Phase N 완료일, 산출물 목록, 판정 결과 기록
    → Phase N+1 입력으로 전달 확인 기록
```

---

# 7. Phase 간 회귀 감지 규칙 (#14 해소)

```
규칙: 현재 Phase가 이전 Phase 산출물에 영향을 줄 수 있는 경우,
      영향받는 산출물을 해당 Phase 완료 검증 시 재확인

Phase 2 회귀 체크:
  CLAUDE.md 보강이 D1 정합성을 깨뜨리지 않았는가?
  → /sot-check로 보강된 CLAUDE.md 재검증

Phase 3 회귀 체크:
  R1 결정이 CLAUDE.md §5 아키텍처와 모순 없는가?
  X1 전략이 B1 린터 설정과 모순 없는가?
  → 수동 대조

Phase 4 회귀 체크:
  코드 구현이 R1 결정을 정확히 반영하는가?
  → D3 (Phase 5)에서 전체 확인, Phase 4 중간에는 STEP별 확인

Phase 6 회귀 체크:
  V1 작업이 V0 코드를 깨뜨리지 않았는가?
  → 회귀 테스트 (pytest) 자동 실행
```

---

# 8. 24건 해소 추적표

| # | 항목 | 심각도 | 해소 위치 | 해소 방법 | 상태 |
|---|------|--------|----------|----------|------|
| 1 | Phase 0 완료 검증 없음 | HIGH | §4 Phase 0 (0-V1~V3) | 수동 체크리스트 15항목 | ● 해소 |
| 2 | 1-6,1-7 도구 미정의 | MEDIUM | §4 Phase 1 (1-V2) | /sot-check + 수동 체크 | ● 해소 |
| 3 | BLOCKER 재검증 루프 | MEDIUM | §4 Phase 1 (1-V2: 1-8a) | 수정 후 1-2~1-5 재실행 | ● 해소 |
| 4 | Obsidian 노트 검증 없음 | HIGH | §4 Phase 2 (2-V2) | 수동 체크리스트 7항목 | ● 해소 |
| 5 | 린터 규칙 정합 검증 | MEDIUM | §4 Phase 2 (2-V3) | PART2 원본 대조 4항목 | ● 해소 |
| 6 | R1 vs SOT 정합 없음 | CRITICAL | §4 Phase 3 (3-V1) | /sot-check 직접 대조 8항목 | ● 해소 |
| 7 | X1 vs SOT 정합 없음 | HIGH | §4 Phase 3 (3-V2) | SOT 원본 수동 대조 4항목 | ● 해소 |
| 8 | 구현 중간 체크포인트 | MEDIUM | §4 Phase 4 (4-V1) | STEP별 5항목 확인 | ● 해소 |
| 9 | B2c 타입 동기화 검증 | MEDIUM | §4 Phase 4 (4-V2) | 왕복 테스트 4항목 | ● 해소 |
| 10 | X3 완료 기준 모호 | LOW | §4 Phase 5 (5-V2) | 수치 기준 4항목 | ● 해소 |
| 11 | V1 상세 미정의 | MEDIUM | §4 Phase 6 (6-V1,V2) | 10항목 구체화 | ● 해소 |
| 12 | 검증 도구 자체 검증 | LOW | §4 Phase 1 (1-V1) | golden test 3항목 | ● 해소 |
| 13 | Phase간 인수인계 없음 | HIGH | §6 인수인계 프로토콜 | 4-step 프로토콜 | ● 해소 |
| 14 | Phase간 회귀 감지 없음 | HIGH | §7 회귀 감지 규칙 | Phase별 회귀 체크 | ● 해소 |
| 15 | 완료 기준 완전성 | MEDIUM | §4 전체 (각 Phase -V 항목) | Phase마다 구체적 수치 기준 | ● 해소 |
| 16 | 외부 의존성 검증 | LOW | §4 Phase 2 (2-V4) | E.1+E.3 재확인 | ● 해소 |
| 17 | 로드맵 자체 검증 | HIGH | §4 Phase 0 (0-V3) | 매트릭스 대조 5항목 | ● 해소 |
| 18 | 613건 미매핑 | CRITICAL | §2 전체 매핑 테이블 | 교차 참조 테이블 | ● 해소 |
| 19 | 스킬 커버리지 갭 | HIGH | §5 커버리지 맵 | 기존 스킬 확장 + 수동 | ● 해소 |
| 20 | Hook 커버리지 한정 | HIGH | §4 Phase 4 (4-V4) | Hook 확장 범위 정의 | ● 해소 |
| 21 | Obsidian 검증 스킬 0개 | HIGH | §4 Phase 2 (2-V2) | 수동 체크리스트 7항목 | ● 해소 |
| 22 | Section E 매핑 불명 | MEDIUM | §2 Section E 매핑 | Phase별 확인 시점 명시 | ● 해소 |
| 23 | GO/NO-GO 관계 미정의 | HIGH | §3 통합 관계 정의 | 5개 규칙 정의 | ● 해소 |
| 24 | D2 감시 구체화 부재 | MEDIUM | §4 Phase 4 (4-V5) | Hook 트리거 3항목 | ● 해소 |

**24건 전부 해소됨**

---

> **참조 문서**:
> - `D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md` — 매트릭스
> - `D:\VAMOS\VAMOS_최종_로드맵.md` — 로드맵
> - `D:\VAMOS\VAMOS Engineering\STRATEGY_09_HARNESS_ENGINEERING.md` — 하네스 계획서
> - `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md` — PART1 (Section B/C/E)
> - `D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` — GO/NO-GO
> - `D:\VAMOS\VAMOS HOME\00_HUB\LOCK-DECISION-REGISTRY.md` — LOCK 469건
> - `D:\VAMOS\CLAUDE 보강전략 V1.0.md` — 보강전략
> - `D:\VAMOS\VAMOS HOME\OBSIDIAN-STRATEGY-v3.md` — Obsidian 전략
