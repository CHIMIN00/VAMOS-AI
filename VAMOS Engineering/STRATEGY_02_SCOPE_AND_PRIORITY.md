# STRATEGY 02: 범위 관리 및 우선순위

> **상위 전략**: Agile/SAFe (MoSCoW, Definition of Done, Critical Path Method)
> **포함 관점**: A9(스코프 축소 ��칙) + A10(SOT 2 완성 정의) + A14(Must/Should/Could + Critical Path)
> **적용 Phase**: Phase 0~6 전체
> **관련 문서**: 로드맵 전 Phase 작업 항목, PART2 V0 체크리스트

---

## 1. 전략 개요

```
핵심 원칙:
  "모든 것을 다 할 수 없을 때, 핵심부터 한다"
  
3가지 기법:
  MoSCoW: 모든 작업에 Must/Should/Could 태그
  Definition of Done: "완성"이 뭔지 명확히 정의
  Critical Path: Must만 연결한 최단 경로 식별
```

---

## 2. A9: Phase 내 스코프 축소 규칙

### 2.1 MoSCoW 분류 기준

```
Must:   이것 없으면 다음 Phase 진입 불가. 제거하면 프로젝트가 멈춤
Should: 있으면 품질 향상. 없어도 다음 Phase 진행 가능. 다음 사이클에 보완
Could:  있으면 좋지만 없어도 제품 동작에 영향 없음. 시간 여유 시 수행
```

### 2.2 Phase별 MoSCoW 분류

**Phase 0:**

| 작업 | 우선순위 | 이유 |
|------|---------|------|
| 0-0 자산 인벤토리 | **Must** | 다른 0-X 작업의 입력 |
| 0-3 매트릭스 갱신 | **Must** | D1 검증 범위 확정 필수 |
| 0-1 CLAUDE.md 구조 | Should | 구조만 확정, 내용은 Phase 2 |
| 0-2 Obsidian 연결 | Should | 연결만 확정, 생성은 Phase 2 |
| 0-4 5개 계획서 목차 | Could | Phase 3 착수 시 작성해도 됨 |
| 0-5 하네스 역참조 | Could | Phase 2 B1 시 작성해도 됨 |

**Phase 1:**

| 작업 | 우선순위 | 이유 |
|------|---------|------|
| 1-1 SOT 2 완성 | **Must** (핵심 5개) | D1 전제 조건 |
| 1-2~1-5 D1 검증 | **Must** | 정합성 확보 필수 |
| 1-9 기준선 저장 | **Must** | D2 감시 기반 |
| 1-6 CLAUDE.md 검증 | Should | GAP 목록 생성 (Phase 2 입력) |
| 1-7 Obsidian 검증 | Should | GAP 목록 생성 |
| 1-8 BLOCKER 재확인 | Should | 2026-03-02 PASS → 변경 가능성 낮음 |

**Phase 2:**

| 작업 | 우선순위 | 이유 |
|------|---------|------|
| 2-1 CLAUDE.md 보강 | **Must** | AI 컨텍스트 없으면 Phase 4 품질 저하 |
| 2-4 린터/CI | **Must** | 하네스 기반 없으면 Phase 4 불가 |
| 2-5 vamos_lint | **Must** | VAMOS 고유 규칙 강제 |
| 2-2 CLAUDE.md 검증 | Should | SILVER+ 목표 (BRONZE도 진행 가능) |
| 2-3 Obsidian 생성 | Should | 없어도 V0 구현 가능 |
| 2-6 CPS 템플릿 | Could | Phase 4에서 필요 시 생성 |
| 2-7 로딩 전략 | Could | 경험적으로 운영 가능 |

**Phase 4 (V0 체크리스트 16항목):**

| 항목 | 우선순위 | 이유 |
|------|---------|------|
| monorepo 구조 | **Must** | 전체 프로젝트 기반 |
| 25개 Pydantic 스키마 | **Must** | 모든 컴포넌트의 타입 계약 |
| JSON-RPC IPC 동작 | **Must** | Python↔Rust 통신 필수 |
| LangGraph 5-Phase 최소 동작 | **Must** | 코어 파이프라인 |
| 입력→IntentFrame→Decision→Response | **Must** | E2E 기본 흐름 |
| config.v1.toml 로드 | **Must** | LOCK 값 런타임 적용 |
| EventType/Failure/Fallback Registry | **Must** | 이벤트 체계 기반 |
| ruff PASS | **Must** | 하네스 기본 |
| vamos_lint PASS | **Must** | VAMOS 규칙 강제 |
| CI 워크플로우 정상 | **Must** | 자동 검증 기반 |
| JSONL 로깅 동작 | Should | 없어도 기본 동작 |
| L0 Session Memory CRUD | Should | V1에서 필수화 |
| Tauri IPC 브릿지 동작 | Should | 프론트엔드 없이도 백엔드 동작 |
| 기본 E2E 테스트 통과 | Should | 수동 확인으로 대체 가능 |
| pytest 실행 | **Must** (0 tests OK) | 테스트 프레임워크 존재 확인 |
| V0 비용 ₩0 확인 | Could | 로컬 전용이므로 자명 |

```
Must 10개 전부 PASS → Phase 5 진입 가능
Should 4개 미통과 → V1 초반에 보완
Could 2개 미통과 → V2에서 보완
```

---

## 3. A10: SOT 2 "완성"의 정의 (Definition of Done)

### 3.1 개별 도메인 완성 기준

```
하나의 SOT 2 도메인이 "완성"이란:
  ① 14-섹션 구조 존재 (sot2-plan-gen 템플릿)
  ② LOCK 항목 전부 등록 (LOCK-{NS}-001~ 형식)
  ③ Authority Chain 문서 존재 (AUTHORITY_CHAIN.md)
  ④ 상위 SOT와 수치 일치 (/sot-conflict sot2-vs-sot CLEAN)
  ⑤ CONFLICT_LOG.md에 미해소 CRITICAL 0건

  ①~⑤ 전부 충족 → 해당 도메인 "완성"
```

### 3.2 전체 SOT 2 완성 기준 (부분 허용)

```
단계 1: 핵심 완성 (D1 부분 실행 가능)
  Must: T0(Governance) + T1(Verifier, Auxiliary) + T2(Blue-Node, COND) = 5개 도메인
  → 이 5개가 완성되면 D1 핵심 검증 실행 가능

단계 2: 확장 완성 (D1 전체 실행)
  Should: T3(9개) + T4(4개) = 13개 도메인 추가
  → 18개 완성 시 D1 대부분 커버

단계 3: 전체 완성 (D1 완전 실행)
  Could: T5(4개) + T6(13개) + AI-Investing(1개) = 18개 도메인 추가
  → 36개 전부 완성 시 D1 100% 실행

현실적 흐름:
  단계 1 완성 → D1 부분 실행 + Phase 2 병행 시작
  단계 2 완성 → D1 전체 실행
  단계 3은 Phase 2와 병행 가능
```

---

## 4. A14: Critical Path (최소 경로)

### 4.1 Must 항목만 연결한 최단 루트

```
Phase 0: 0-0(인벤토리) → 0-3(매트릭스)
  ↓
Phase 1: 1-1(SOT2 핵심5개) → 1-2~1-5(D1 검증) → 1-9(기준선)
  ↓
Phase 2: 2-1(CLAUDE.md 보강) → 2-4(린터) → 2-5(vamos_lint)
  ↓
Phase 3: 3-1~3-7(R1 7개 LOCK)
  ↓
Phase 4: 4-1(타입동기화) → 4-2(ORANGE CORE) → 4-4~4-6(Registry+config+BLUE NODE)
  ↓
Phase 5: 5-3~5-6(D3 정합) → 5-8(GO/NO-GO)
  ↓
V0 완료

이 경로에 없는 것 = Should/Could = 시간 여유 시 수행
```

### 4.2 Critical Path에서 제외된 것 (Should/Could)

```
Phase 0: 0-1(CLAUDE구조), 0-2(Obsidian연결), 0-4(계획서목차), 0-5(하네스역참조)
Phase 1: 1-6(CLAUDE검증), 1-7(Obsidian검증), 1-8(BLOCKER재확인)
Phase 2: 2-2(CLAUDE검증), 2-3(Obsidian생성), 2-6(CPS), 2-7(로딩전략)
Phase 3: 3-8~3-13(X1 전략 전부)
Phase 4: 4-3(프론트엔드), 4-7(횡단실행)
Phase 5: 5-1~5-2(Eval), 5-7(X3)
```

---

## 5. 관점 간 연결

```
A10(완성 정의) → SOT 2 "핵심 5개 완성"이면 → A9(스코프 축소) D1 부분 실행 허용
A14(Critical Path) → Must만 연결 → A9(축소 시 Must 기준)
A9(축소 규칙) → Should 미통과 시 → STRATEGY_01 A1(복구: 다음 사이클 연기)
```

---

> **참조**: STRATEGY_08 (매트릭스 셀별 적용), STRATEGY_10 (검증 체계 체크리스트)
