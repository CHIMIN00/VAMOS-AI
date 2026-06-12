# VAMOS 최종 로드맵

> **작성일**: 2026-04-04 | **최종 갱신**: 2026-06-12 (**Phase 2 최종 확정** — 3-AI 독립 교차감사 CONFIRM[Fable 5 max·Opus 4.8 max 디스크 실측 + GPT 5.5 증거팩, CONDITIONAL 12항목 전수 재실측 해소] · decisions/PHASE2-DEC-03; 직전 동일자 Phase 2 완료 반영 — A12 대조 갱신)
> **목적**: VAMOS AI 프로젝트의 전체 진행 순서 — **Phase 0~8 (V0·V1 + V2·V3 차기 사이클 정식 편입 — 전 기능 커버)**
> **근거**: 엔지니어링 매트릭스 + 하네스 계획서 + 보강전략 V1.0 + 검증 체계 + 자산 인벤토리 + 25건 관점 전략 (STRATEGY 01~07)
> **상태**: 최종 확정 (25건 관점 전략 반영) · **진행: Phase 0 ✅ 완료 / Phase 1 ✅ 완료 (D1 PASS, 2026-06-04, 조건부·비차단 이연 1도메인 5-3 — 2026-06-11 결정 D1~D5로 전건 RESOLVED, 3-0 참조) / Phase 2 ✅ 완료·**최종 확정** (2026-06-12, 2-V 전항목 PASS + 3-AI 교차감사 CONFIRM — PHASE2-DEC-03) / Phase 3 ◐ 부분 / Phase 4~8 미착수**

---

## 📍 현재 진행 상황 (2026-06-12 기준)

> **요약**: 프로젝트는 현재까지 **Phase 0 완료 + Phase 1 완료(SOT 2 콘텐츠 + D1 PASS, 2026-06-04) + Phase 2 완료·최종 확정(보강/환경, 2026-06-12 — 2-V 전항목 PASS + 3-AI 교차감사 CONFIRM[PHASE2-DEC-03])** 상태이며, **실제 코드 구현(Phase 4~6)은 아직 착수하지 않았다(Phase 3은 설계가 SOT 2에 흡수된 ◐ 부분 — 3-0 미결정 게이트 선행).** Phase 1의 "SOT 2 완성"은 당초 계획(648 파일 상세화)을 크게 넘어 **30개 도메인 다단계 설계 정본 체계**로 확장되어 전 단계가 종결되었고, **D1 검증은 값 게이트 5/5 PASS(조건부: 비차단 이연 1도메인 5-3 C-04~C-08; 6-5 W-CB는 v1.3 RESOLVED)** 로 종결되었다.

| Phase | 상태 | 근거 / 비고 |
|-------|:----:|------------|
| **0** 자산 인벤토리 + 매트릭스 | ✅ **완료** (2026-04-04) | `VAMOS Engineering/PROGRESS.md` — 0-V 전항목 PASS. ✔ **(2026-06-05 정정)** 엔지니어링 Phase 0 산출물(STRATEGY_01~11+P0-2/P0-4+retro)을 소급 커밋(`1d52614`)하고 `git tag phase0-complete`를 해당 커밋으로 재지정 완료 — 기존 AI-Investing 커밋(0d49b6c) 오지정 해소. (phase0-start는 Phase 0 착수 시점 저장소 상태 마커로 유지) |
| **1** SOT 2 완성 + D1 검증 | ✅ **완료** (D1 PASS, 2026-06-04) | SOT 2 **30/30 도메인** Phase 0~4 전 단계 genuine 완료. `docs/sot 2/SOT2_MASTER_INDEX.md` `[SOT2_ALL_PHASES_ALL_DOMAINS_COMPLETE: 2026-06-03]`. **D1 값 게이트 5/5 PASS**(CONFLICT active 0·MISMATCH 0·LOCK MISMATCH 0·SDV-1 crit 0·snapshot 저장), 조건부 비차단 이연 1도메인(5-3 C-04~C-08; 6-5 RESOLVED). 산출물 `v13_results/phase0/D1_RESULTS_INDEX.md`. `git tag phase1-d1-pass` 생성 (2026-06-05 감사 정정 반영) |
| **2** 보강/환경 (CLAUDE.md·Obsidian·린터/CI) | ✅ **완료** (2026-06-12) | 2-V 전항목 PASS — 외부 의존성 28/28 · **골든셋 v2 실데이터 162문항**(D14, LOCK-BE-01/02 유효화; LogicKor 전수 42 편차 기록) · CLAUDE.md 보강 946줄 §1~§28 **GOLD 판정**(8단계 검증+회귀 12/12) · Obsidian **124노트**(깨진 링크 0·A16 responsible-ai 9) · 린터/CI(backend/pyproject·ci.yml 단일 통합·vamos_lint VL-001~005·Hook 16→18·D17 결정) · 정리작업(D-2 보수·D-3 종결·유산 이동·5-4 SHELL→3-0 이연[PHASE2-DEC-02]). `git tag phase2-complete`. ✔ **(2026-06-12 최종 확정)** 3-AI 독립 교차감사 — Fable 5 max CONFIRM/GO·Opus 4.8 max CONFIRM/GO(디스크 실측)·GPT 5.5 CONDITIONAL(증거팩 한계)→UNVERIFIABLE 12항목 전수 디스크 재실측 해소, CRITICAL/MAJOR 0(실효)·silent drop 0·원격 태그 ls-remote 확인 — `decisions/PHASE2-DEC-03` |
| **3** R1 런타임 설계 + X1 횡단 전략 | ◐ **부분** (SOT 2에 흡수) | 5-Gate·메모리 L0~L3·IPC JSON-RPC·보안 등 런타임 설계가 SOT 2 도메인 정본에 포함됨. 단, 독립 결정문서 7종(`runtime_decisions.md`·`security_strategy.md`·`test_strategy.md`·`release_strategy.md`·`doc_strategy.md`·`runtime_eng_plan.md`·`cross_eng_plan.md`)은 전 산출물 미생성 |
| **4** V0 코드 구현 | ⬜ **미착수** | 구현 코드 미생성 — `src/` · `src-tauri/` 부재 (`backend/`엔 Phase 2-4 환경 파일만: pyproject·tests 골격) — 코드 한 줄도 미생성 |
| **5** V0 검증 + GO/NO-GO | ⬜ **미착수** | Phase 4 선행 필요 |
| **6** V1 구현 | ⬜ **미착수** | V0 완료 선행 필요 |
| **7** V2 구현 사이클 (Pro Server) | ⬜ **미착수** | V1 완료 + 전환 조건 6건 — 구현 정본 PART2 §4 (2026-06-11 정식 편입) |
| **8** V3 구현 사이클 (Enterprise) | ⬜ **미착수** | V2 완료 + 전환 조건 5건+승인 — 구현 정본 PART2 §5 (2026-06-11 정식 편입) |

### Phase 1 (SOT 2) 상세 진행

SOT 2(설계 정본 체계)는 자체 다단계 라이프사이클로 진행되었으며 전부 종결:

- **SOT 2 콘텐츠 완성**: 7 Tier / 36 대분류 / 30 구현 도메인, **36개 전부 APPROVED** + ALL-A VERIFIED (2026-03-27~28) · LOCK 469~484건 · CONFLICT active(차단) 0 · 비차단 이연 OPEN 5건(5-3 C-04~C-08)
- **구현 Phase 추적 (도메인별 §7)**: Phase 0(추출) → 1 → 2 → 3(V3 설계) → **4(V3 정본 승격)** 전 단계 완료
- **Phase 4 정본 승격**: 30/30 도메인 (pre-complete 5 + RECOVERY 25/25 = 116/116 P4 task) **genuine production write 완결** (`[RECOVERY_COMPLETE: 2026-06-03]`)
  - 불변식 전 도메인 유지: **CONFLICT active 0(비차단 이연 OPEN 5: 5-3 C-04~C-08) / LOCK 재정의 0 / abort NOT FIRED / FABRICATION 0**
  - 추적 정합: 종합계획서 §7 ↔ `PHASE4_ORCHESTRATION/PROGRESS.md` ↔ `SOT2_MASTER_INDEX.md` ↔ RECOVERY_PLAN v1.1 상호 일치
  - **RECOVERY 경위**: Phase 4 1차 승격 시 일부 도메인이 promotion report만 생성하고 V3 정본을 디스크에 쓰지 않은 verify-only 착시(보고서 ✅ ≠ 산출물 존재)가 발견되어, Wave1~3 25개 도메인 회수(genuine write)로 116/116 task를 완결했다. 재발 방지는 리스크 R16 참조.

### ▶ 다음 작업 (권장 진입점)

환경/보강(Phase 2)까지 완비되었으므로, 다음은 **Phase 3 — 3-0 미결정 게이트(선행 Must)** 다.
- **Phase 3-0**: 미결정 게이트 — D1 이연 대장 확인 + PART1 C.1 13건 + 분모 2건·V1 귀속·STEP7 reconcile + ⟦2026-06-12 추가 이관⟧ Phase 2 발견 SOT 내부 이형 9건(claude-md-verification step1 C-001~C-008 + 마스터인덱스↔READINESS 사유 이형)·docs\sot\CLAUDE.md 스냅샷 동기화 여부·5-4 SHELL 87(PHASE2-DEC-02)·LOCK-MCP-06(3회) vs PHASE_B4(V1/V2=2·V3=3) 표기 뉘앙스 — ⟪정본 체크리스트는 PROGRESS.md L21 (교차감사 F-02)⟫. 추가 권고(비차단): OpenAI 구키 revoke 사용자 통보 수신 시 액션대장 등재 + main 병합 정책 확정(현재 phase01-targeted-fixes)
- 이후 R1(3-1~3-7c)/X1(3-8~3-13) 2트랙 → Phase 4 V0 스켈레톤 코드 생산 (하네스: ruff·vamos_lint·pytest·ci.yml 가동 준비 완료)

---

## 전체 구조 요약

| Phase | 작업 | 병렬 가능 | 선행 조건 | 진행 |
|-------|------|----------|----------|:----:|
| **0** | 자산 인벤토리 + 매트릭스 완성 | **SOT 2와 병렬** | 없음 | ✅ |
| **1** | SOT 2 완성 → D1 검증 | Phase 0과 병렬 (SOT 2) | Phase 0 + SOT 2 완료 후 D1 | ✅ |
| **2** | CLAUDE.md 보강 + Obsidian 생성 + 린터/CI | **3트랙 병렬** | D1 PASS | ✅ |
| **3** | R1 런타임 설계 + X1 횡단 전략 | **2트랙 병렬** | Phase 2 완료 | ◐ |
| **4** | V0 코드 구현 (하네스 위에서) | **3트랙 병렬** | Phase 3 완료 | ⬜ |
| **5** | V0 검증 + GO/NO-GO | **3트랙 병렬** | Phase 4 완료 | ⬜ |
| **6** | V1 구현 (Phase 1~5 반복) | 선후만 정의 (병렬 트랙 미정의) | V0 완료 | ⬜ |
| **7** | V2 구현 사이클 (Pro Server) | PART2 §4 위임 (V2-Phase 1~3 직렬) | V1 완료 + 전환 조건 6건 | ⬜ |
| **8** | V3 구현 사이클 (Enterprise) | PART2 §5 위임 (V3-Phase 1~3 직렬) | V2 완료 + 전환 조건 5건+승인 | ⬜ |

> 범례: ✅ 완료 (Phase 1=D1 PASS 2026-06-04 · Phase 2=2-V PASS 2026-06-12) · ◐ 부분(Phase 3=SOT 2 흡수) · ⬜ 미착수

---

## 공통 규칙 — 전 Phase 적용

### 세션 관리 프로토콜 (A5, A13 — STRATEGY_03)

```
작업 중단 전: VAMOS Engineering/PROGRESS.md 갱신 (현재 Phase, 완료/미완료 항목, 다음 작업)
작업 재개 시: PROGRESS.md 읽기 → 즉시 이어서 작업

새 대화 시작 시 AI에게 주는 정보 (A13):
  Phase 0: PROGRESS.md + 자산 인벤토리 + 매트릭스
  Phase 1: PROGRESS.md + 자산 인벤토리 §3.1 + D1 스킬 목록
  Phase 2: PROGRESS.md + 보강전략 or Obsidian전략 or 하네스§7~8 (트랙별)
  Phase 3: PROGRESS.md + D2.0-01~08 + LOCK Registry
  Phase 4: PROGRESS.md + 자산 인벤토리 §3.4 + R1 결정 문서 + PART2
  Phase 5: PROGRESS.md + 자산 인벤토리 §3.5 + 벤치마크 설정
  Phase 6: PROGRESS.md + V0 완료 결과 + PART1 Section B.2
  Phase 7: PROGRESS.md + V1 완료 결과 + PART2 §4 + PHASE_B7(마이그레이션) + READINESS §4 + PART1 B.3
  Phase 8: PROGRESS.md + V2 완료 결과 + PART2 §5 + READINESS §5 + PART1 B.4
```

### 의사결정 기록 (A6 — STRATEGY_03)

```
기록 대상: 아키텍처 결정, 전략 결정, 스코프 축소 결정, 예외 허용
저장 위치: VAMOS Engineering/decisions/PHASE{N}-DEC-{순번}_{제목}.md
포맷: 결정 + 이유 + 검토한 대안 + 근거 SOT
```

> ※ **A6 준수 미충족**: 현재 ADR 미생성(`decisions/`엔 phase0_retro.md만, ADR 0건) — 주요 결정 ADR 소급 기록 필요. 또는 SOT2 종합계획서 §7 / AUTHORITY 문서로 분산 기록됨을 명시.

### Phase 회고 (A11 — STRATEGY_07)

```
Phase 완료 시 (5분):
  잘된 것 3가지 / 안된 것 3가지 / 다음에 바꿀 것 1가지
  저장: VAMOS Engineering/decisions/phase{N}_retro.md
  실패가 있었으면 포스트모템 추가 (근본 원인 + 재발 방지)
```

### 로드맵 갱신 주기 (A12 — STRATEGY_04)

```
Phase N 완료 시 → 로드맵 Phase N+1 내용을 현실과 대조
  불일치 0~2건: 메모만 남기고 계속
  불일치 3건 이상: 로드맵 해당 Phase 이후 갱신
```

### 데이터 백업 (A2 — STRATEGY_01)

```
Phase 완료 시: git tag phase{N}-complete → git push --tags → git push origin main (push 확인)
  Phase 0 완료 → git tag phase0-complete
  Phase 1 완료 → git tag phase1-d1-pass
  Phase 5 완료 → git tag v0-release
  Phase 6 완료 → git tag v1-release
  Phase 7 완료 → git tag v2-release
  Phase 8 완료 → git tag v3-release
```

> ✔ **push 확인 완료 (2026-06-11)**: `git push origin main` 및 태그 push(phase0-complete·phase1-d1-pass 포함 4종) 확인.

### Must/Should/Could 우선순위 (A14 — STRATEGY_02)

```
모든 작업에 우선순위 태그:
  Must:   이것 없으면 다음 Phase 불가
  Should: 없어도 진행 가능, 다음 사이클 보완
  Could:  시간 여유 시 수행

Critical Path (Must만 연결한 최단 루트):
  0-0→0-3 → 1-1→1-2~1-5→1-9 → 2-0→2-1→2-4→2-5 → 3-0→3-1~3-7c → 4-1→4-2→4-4→4-5 → 5-3~5-6→5-7a→5-8
  → 6-1→6-2→6-3→6-4→6-7→6-8→6-8a→6-9 → 7-0→7-1→7-2→7-3→7-4 → 8-0→8-1→8-2→8-3→8-4 (V1~V3 구간 — 2026-06-11 연장)
```

---

## Phase 0: 자산 인벤토리 + 전체 그림 확정 (SOT 2와 병렬) — ✅ 완료 (2026-04-04)

> **목적**: 프로젝트 전체 자산 파악 + D1 검증 범위 확정
> **전제**: SOT 2 내용 불필요 — 구조만 정의
> **적용 전략**: A2(백업 확인), A15(리스크 식별)

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 0-0 | **프로젝트 자산 인벤토리** | 전체 폴더/파일 역할, 매트릭스 셀 매핑, 중복/미사용 식별, 용도별 분류 | **Must** | ✓ | STRATEGY_11 |
| 0-1 | CLAUDE.md 최종 구조 확정 | 보강전략 §1~§27 구조 + §28 엔지니어링 프레임워크 참조 계획 | Should | ✓ | 구조 명세 |
| 0-2 | Obsidian 전략과 매트릭스 연결 | Strategy v3.0 노트가 매트릭스 어느 셀인지 확정 | Should | ✓ | 매핑 문서 |
| 0-3 | 매트릭스 v1.1 갱신 | 미연동 8건 해소 + 설계 자산 전체 맵 반영 | **Must** | ✓ | STRATEGY_08 갱신 |
| 0-4 | 5개 계획서 범위/목차 | ②설계정합 ③런타임 ④다중스택 ⑤횡단 ⑥운영 | Could | ✓ | 5개 목차 |
| 0-5 | 하네스 역참조 추가 | STRATEGY_09 ↔ STRATEGY_08 양방향 연결 | Could | ✓ | STRATEGY_09 갱신 |
| 0-6 | **Git remote 확인 + 리스크 초기 식별** | GitHub remote 연결 확인(A2) + STRATEGY_01 §4 리스크 15건 검토(A15) | **Must** | ✓ | 환경 확인 |

```
병렬 구조:
  트랙 A: SOT 2 상세화 계속 ──────────────→ SOT 2 완성
  트랙 B: 0-0(Must) → 0-1,0-2(Should,병렬) → 0-3(Must) → 0-4,0-5(Could,병렬) + 0-6(Must)
```

**Phase 0 검증 체크리스트 (0-V):**
- □ 자산 인벤토리 완성 (STRATEGY_11)
- □ 매트릭스 v1.1 갱신 완료 (미연동 8건 해소)
- □ Git remote 연결 + git tag phase0-complete
- □ 리스크 15건 검토 완료
- □ PROGRESS.md 초기 생성

**Phase 0 실패 시 (A1):** 매트릭스 갱신 불가 → 모순 항목 PENDING 표시 + Phase 1 D1 결과로 해소

**Phase 0 완료 조건**: Must 항목 전부 통과 + 검증 체크리스트 통과 + 회고 기록

---

## Phase 1: SOT 2 완성 + D1 검증 — ✅ 완료 (D1 PASS, 2026-06-04, 30/30 도메인 · 조건부 비차단 이연 1도메인 5-3)

> **목적**: 원본 설계 자산의 정합성 100% 확보
> **전제**: Phase 0 완료 + SOT 2 완성
> **적용 전략**: A10(SOT 2 완성 정의), A17(재현성), A15(리스크 R01~R03)
> **거버넌스 교차**: PART1 Section A.1/E.2 (BLOCKER 14건)

> ※ **D1 PASS (2026-06-04)**: D1 산출물 전종 생성 완료 — `sot_conflict_report.json`·`sot2_conflict_scan.json`·`cross_ref_matrix/lock_consistency/broken_references`·`{도메인}_validation.json×36`·`integrity_snapshot.json`(2,654 파일)·`claude_md_gap_report`·`obsidian_gap_report`·`blocker_log`. 값 게이트 5/5 PASS, 인덱스 `04. 구현단계/v13_results/phase0/D1_RESULTS_INDEX.md`(+`D1_VERDICT.json`). 조건부: 비차단 이연 1도메인(5-3 C-04~C-08 5건)·BROKEN 1(사소 네비)은 이연대장 등록, 자동 정본 변경 0. **6-5 W-CB는 v1.3(2026-05-19)에서 RESOLVED**(1차 D1의 6-5 이연·OPEN 6은 2026-06-05 감사로 5-3 5건+6-5 0으로 정정). ⟦2026-06-11: 5-3 C-04~C-08도 결정 D1~D5로 전건 RESOLVED — 실효 OPEN 0, 3-0 게이트 기록 참조⟧ SOT2 빌드 산출물(S11-x)은 별개.

### SOT 2 완성 기준 (A10 — STRATEGY_02)

```
Must:   T0~T2 핵심 5개 도메인 완성 (14-섹션 + LOCK 등록 + Authority Chain)
Should: T3~T4 13개 도메인 완성
Could:  T5~T6 + AI-Investing 18개 도메인 완성

Must 5개 완성 → D1 부분 실행 가능
전체 36개 완성 → D1 전체 실행
```

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 1-1 | SOT 2 상세화 완료 | 상세화 마무리 (당초 상세화 대상 648→710 → Phase4 확장 후 현행 2,654 실측) | **Must** (핵심5개) | Phase 0과 병렬 | SOT 2 완성본 |
| 1-2 | D1: SOT 내부 정합 | /sot-conflict scan | **Must** | 1-1 후 | sot_conflict_report.json |
| 1-3 | D1: SOT↔SOT 2 교차 | /sot-conflict sot2-vs-sot | **Must** | 순차 | sot2_crossref_report.json |
| 1-4 | D1: SOT 2 내부 교차 | /sot2-cross-ref all | **Must** | 순차 | sot2_internal_report.json |
| 1-5 | D1: 구조+LOCK 검증 | /validate sot2-all (SDV-1~7, SDV-4 LOCK) | **Must** | 순차 | sot2_validate_report.json |
| 1-6 | D1: CLAUDE.md 검증 | /sot-check method-c → GAP 목록 | Should | 순차 | claude_md_gap_report |
| 1-7 | D1: Obsidian 전략 정합 | 도메인 수/모듈 수 수동 대조 | Should | 순차 | obsidian_gap_report |
| 1-8 | D1: BLOCKER 재확인 | PART1 14건 변경 여부 확인 | Should | 순차 | blocker_log |
| 1-8a | D1: BLOCKER 수정 후 재검증 | 수정 시 1-2~1-5 해당 범위 재실행 | 조건부 | 순차 | 재검증 리포트 |
| 1-9 | D1: 기준선 저장 | /integrity snapshot | **Must** | 전부 후 | integrity_snapshot.json |

```
사전 확인 (A17 재현성 + A7 도구 점검):
  D1 실행 전 /sot-conflict, /sot2-cross-ref, /validate golden test 실행
  → 알려진 케이스 탐지 확인 → 도구 신뢰성 확보

재현성 보장 (A17):
  결정론적 검증(1-2~1-5): 동일 입력 = 동일 결과 → 자동 보장
  AI 검증(1-6, 1-7): 3회 실행 → 2회 이상 동일 → PASS
  모든 결과에 timestamp + input_hash + skill_version 기록
```

**Phase 1 검증 체크리스트 (1-V):**
- □ CONFLICT 0건 — /sot-conflict scan
- □ MISMATCH 0건 — /sot-conflict sot2-vs-sot
- □ SOT 2 교차참조 무결 — /sot2-cross-ref all
- □ integrity_snapshot.json 저장 완료
- □ 검증 결과에 재현성 메타데이터(timestamp, hash) 기록 확인

**Phase 1→2 인수인계 확인:**
- □ claude_md_gap_report → Phase 2-1 입력 존재?
- □ obsidian_gap_report → Phase 2-3 입력 존재?
- □ integrity_snapshot.json → D2 감시 기준선 로드 가능?

**Phase 1 실패 시 (A1):**
- CONFLICT 해소 불가 → 정본 우선순위(RULE>PLAN>DESIGN LOCK)로 해소. 그래도 불가 → 해당 도메인 제외 → V1 D1'에서 재검증
- SOT 2 미완성 → 핵심 5개 도메인만으로 D1 부분 실행(A10)

**Phase 1 완료 조건**: Must 전부 통과 + 검증 체크리스트 통과 + 인수인계 확인 + 회고 기록 → **D1 PASS**

---

## Phase 2: 보강/생성 + 환경 세팅 (B1) — ✅ 완료·최종 확정 (2026-06-12, 2-V 전항목 PASS + 3-AI 교차감사 CONFIRM[PHASE2-DEC-03] · 상세: VAMOS Engineering/PROGRESS.md + decisions/phase2_retro.md)

> **목적**: AI 컨텍스트 확보 + 지식 그래프 구축 + 코드 생산 환경 준비
> **전제**: D1 PASS
> **적용 전략**: A16(책임 AI 자산 식별), A15(리스크 R04~R05, R10, R12~R13)
> **거버넌스 교차**: PART1 E.1(9건), E.3(8건), E.5(5건), B.1(11건)

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 2-0 | **외부 의존성 재확인** | PART1 E.1+E.3+B.1 재확인(A4). 2026-03-02 이후 변경 여부 + **골든셋 실데이터 재구축**(D14 선행과업 — benchmarks/ [SYNTHETIC] 해소; 5-1·6-7 Eval과 LOCK-BE-01/02 게이트의 전제) | **Must** | 선행 | 환경 리포트 + 골든셋 v2 |
| 2-1 | CLAUDE.md 보강 | 보강전략 Phase A (5세션) → §21~§27 추가 + §28(엔지니어링 프레임워크 — 본 로드맵 신설분, 보강전략엔 미정의). §28에 매트릭스/PROGRESS.md/Phase별 컨텍스트(A13) 포함. 입력: PART1 §D.0(CLAUDE.md 필수 수정) + claude_md_gap_report 2건(D1 산출) 반영 | **Must** | ⓐ | 보강된 CLAUDE.md |
| 2-2 | CLAUDE.md 검증 | 보강전략 Phase B~D(스킬 8종 생성[B, 2세션]→8단계 검증 실행[C, 4세션]→수정·재검증[D]) → SILVER+ 판정 | Should | 2-1후 | 검증 리포트 |
| 2-3 | Obsidian 노트 생성 | Strategy v3.0 → 120+ 노트 + 매트릭스 노트. 책임 AI 관련 자산 태깅(A16) | Should | ⓑ | VAMOS HOME |
| 2-4 | 린터/CI 환경 세팅 | 하네스 §7 → pyproject.toml + ruff + CI yaml + conftest.py. ✔ (2026-06-11 기집행) 구 .claude-pre-commit 처분 완료 — pre-commit 훅 블록 제거(D17, `repos: []` 보존)·gitlink 언트래킹(D18, 디스크 보존); 훅 재도입 여부는 본 작업에서 결정. **CI yaml 기준**: PHASE_B6 §2 ci.yml 단일 통합이 정본(V0 최소=quality+test job; V1 전체 분리는 PART2 §6.4 11종 — L4844 주석) | **Must** | ⓒ | 린터/CI 파일 + 코드 생산 Hook(STRATEGY_10 §4 4-V4: py 수정 시 ruff·config LOCK 검증) |
| 2-5 | VAMOS 커스텀 린터 | 하네스 §8 → vamos_lint VL-001~005 (commitlint는 §8 vamos_lint 규칙 아님 — STRATEGY_09 §3 린터 목록의 별도 커밋 린터, 2-4 린터/CI 트랙) | **Must** | 2-4후 | vamos_lint.py |
| 2-6 | CPS 템플릿 정의 | Context/Problem/Solution 구조화 | Could | 2-4병렬 | 템플릿 |
| 2-7 | 컨텍스트 로딩 전략 | 자산 인벤토리 §3 기반 로딩 맵 | Could | 2-1후 | 로딩 맵 |
| 2-8 | **자산 인벤토리 갱신** | Phase 2 생성 파일을 STRATEGY_11에 반영. 정리작업 포함: D-2 네비링크 보수 · D-3 INDEX 부재 6도메인 보완(D1 이연 대장) · 유산 폴더 정리 | Should | 전체후 | STRATEGY_11 갱신 |

```
실행 구조:
  2-0 (Must,선행) → 3트랙 병렬:
    ⓐ 2-1(Must) → 2-2(Should) → 2-7(Could)
    ⓑ 2-3(Should)
    ⓒ 2-4(Must) → 2-5(Must), 2-6(Could)
  → 2-8(Should)
```

**Phase 2 검증 체크리스트 (2-V):**
- □ CLAUDE.md 보강 완료 (§28 엔지니어링 프레임워크에 A13 컨텍스트 프로토콜 포함?)
- □ 린터: ruff 13룰 PART2 일치 + vamos_lint VL-001~005 동작
- □ CI: yaml PART2 일치
- □ 외부 의존성 E.1+E.3 PASS
- □ 회귀 확인: CLAUDE.md 보강이 D1 정합 안 깨뜨렸는지 /sot-check 재실행(A15 R10)
- □ Obsidian 생성 시 책임 AI 자산 태깅 완료?(A16)

**Phase 2→3 인수인계:**
- □ 보강된 CLAUDE.md → Phase 3 AI 컨텍스트 활성화?
- □ 린터/CI → Phase 4 자동 실행 준비?

**Phase 2 실패 시 (A1):**
- CLAUDE.md REJECT → 보강 범위 축소(§21~§24만) → BRONZE 허용 → Phase 3 진입
- 린터 오탐(A15 R05) → 초기 warn 모드 → 안정화 후 error 전환

**Phase 2 완료 조건**: Must 전부 통과 + 검증 체크리스트 통과 + 인수인계 확인 + 회고 기록

---

## Phase 3: 런타임 설계 + 횡단 전략 (R1 + X1) — ◐ 부분 (설계 내용은 SOT 2에 흡수, 독립 결정문서 미생성)

> **목적**: 제품 아키텍처 확정 + 전략 수립
> **전제**: Phase 2 완료
> **적용 전략**: A20(인터페이스 계약), A21(다층 방어), A22(사용자 투명성), A25(예측 신뢰도), A15(리스크 R06~R07)
> **거버넌스 교차**: LOCK Registry DEC-001~017 중 10건

> ※ **산출물 위상·경로**: 3-1~3-13이 신설하는 결정문서 7종은 기존 정본(PHASE_B5/B6/B7·SOT 2 도메인 정본)의 **결정 요약+로드맵 바인딩** 문서이며 기존 정본을 대체하지 않는다(충돌 시 기존 정본 우선, 변경은 LOCK 절차). 저장 위치: `VAMOS Engineering\` 직하(3-0에서 확정 시 변경 가능).

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 3-0 | **미결정 게이트** | R1 착수 전 미결정·이연 항목 일괄 처리 게이트: ①D1 이연 대장(D1_RESULTS_INDEX §3, D-1~D-4) + 전수진단 결정 항목 확인 ②PART1 C.1 V0 시작 전 결정 13건(#1~3 기결정 확인·#4~13 확정 기록) ③분모 확정 2건(V0 모듈 "전 25 파일 선생성 여부"·V1 CORE 26 vs 32 — 4-2/6-3 참조) ④V1 귀속 확정(SDAR §10.1 기반·Cloud Library CB1[E-15/S-5]·RT-BNP V1·4-4 MLOps 본대 — SPEC↔PART2 충돌 해소) ⑤STEP7 V1 라벨↔PART2 V2/V3 배치 reconcile 방침 ⑥READINESS §8 문서수정 잔여 확인. ✔ (2026-06-11) D-1(5-3 C-04~C-08) RESOLVED·결정 D1~D19 기적용(17건 — D8·D12 결번) — 잔여·신규 미결정은 본 게이트에서 확정 후 R1 진행 | **Must** | 선행 | 결정 기록(decisions/ — 기존 17건 정본은 `_targets/DECISION_REGISTER.md`; ADR 소급 여부 본 게이트에서 결정) |
| 3-1 | R1: 5-Gate 실행 순서 | PolicyGate→Approval→Cost→Evidence→SelfCheck | **Must** | ⓐ | runtime_decisions.md |
| 3-2 | R1: 메모리 L0~L3 알고리즘 | 승격/강등 조건, 저장 방식 | **Must** | 순차 | |
| 3-3 | R1: Multi-Brain Failover | GPT→Claude→Ollama 순서/조건 | **Must** | 순차 | |
| 3-4 | R1: LangGraph DAG 상태 전이 | S0→S1→...→S8 | **Must** | 순차 | |
| 3-5 | R1: CostGate 임계값 | 80%/100% LOCK | **Must** | 순차 | |
| 3-6 | R1: IPC JSON-RPC 사양 | Python↔Rust 통신. **인터페이스 계약 규칙 포함(A20)**: Pydantic 정본, Rust/TS 자동 생성, 수동 수정 금지 | **Must** | 순차 | |
| 3-7 | R1: MCP Streamable HTTP | 외부 도구 통신 계약 | **Must** | 순차 | |
| 3-7a | **R1: 다층 방어 설계 (A21)** | Defense Layer 1(config LOCK) + Defense Layer 2(5-Gate) + Defense Layer 3(NEVER_AUTO) 독립 3계층 확정. ※PART2 "Security Layer"와 다른 개념 — 내부 아키텍처 방어 계층 | **Must** | 3-7후 | |
| 3-7b | **R1: 사용자 투명성 설계 (A22)** | ResponseEnvelope에 reasoning_trace + evidence_sources 추가. ※SOT 5필드 LOCK과의 관계 **확정(D6, 2026-06-11): 선택지A 채택** — reasoning_trace/evidence_sources는 metadata(dict) 내부 포함, 5필드 LOCK 보존 (선택지B LOCK 해제 기각, Approval Gate 불요) — STRATEGY_05 §4.2 참조 | **Must** | 3-7a후 | |
| 3-7c | **R1: 예측 신뢰도 설계 (A25)** | Decision에 confidence_score(0.0~1.0) + 임계값(0.85/0.60/0.30 LOCK) + 행동 분기(HIGH/MEDIUM/LOW/REFUSE) | **Must** | 3-7b후 | |
| 3-8 | X1: 보안 전략 | 7개 불변 + Permission Matrix + 감사 로그 + **책임 AI 체크리스트(A16)** + **다층 방어 검증 방법(A21)** | **Must** | ⓑ | security_strategy.md |
| 3-9 | X1: 테스트 전략 | 테스트 피라미드 + 커버리지 80%+ | Should | 순차 | test_strategy.md |
| 3-10 | X1: 버전/릴리스 전략 | Git 브랜치 + SemVer + **Expand/Contract 규칙(A23)** | Should | 순차 | release_strategy.md |
| 3-11 | X1: 문서화 전략 | 코드 문서 vs 설계 문서 주체 + Obsidian 갱신 규칙 | Could | 순차 | doc_strategy.md |
| 3-12 | 런타임 계획서 | R1 기반 R2a/R2b/RF 상세 | Should | 3-7c후 | runtime_eng_plan.md |
| 3-13 | 횡단 계획서 | X1 기반 X2/X3/XF 상세 | Should | 3-11후 | cross_eng_plan.md |

```
2트랙 병렬:
  ⓐ R1: 3-1→3-2→3-3→3-4→3-5→3-6→3-7→3-7a→3-7b→3-7c→3-12
  ⓑ X1: 3-8→3-9→3-10→3-11→3-13

R1 결정 시 SOT 대조 (A15 R06):
  각 결정을 /sot-check로 정본과 직접 라인 대조
  결정마다 decisions/ 폴더에 ADR 기록 (A6)
```

**Phase 3 검증 체크리스트 (3-V):**
- □ R1 7개+3개(A21,A22,A25) = 10개 결정이 SOT 정본과 일치? → /sot-check 대조
- □ R1 결정 전부 LOCK Registry 일치 또는 신규 등록?
- □ A20 인터페이스 규칙: Pydantic 정본 + 자동 생성 + 수동 금지 확정?
- □ A21 다층 방어: 3계층 독립 설계 확정?
- □ A22 투명성: reasoning_trace 스키마 확정?
- □ A25 신뢰도: confidence_score + 임계값 LOCK 확정?
- □ A16 책임 AI: 보안 전략에 체크리스트 포함?
- □ 회귀: R1 결정이 Phase 2 CLAUDE.md §5와 모순 없는가?

**Phase 3→4 인수인계:**
- □ runtime_decisions.md → Phase 4 R2a 참조?
- □ IPC 사양 + A20 규칙 → Phase 4 B2c 입력?
- □ 4개 전략 문서 → Phase 4 X2 참조?

**Phase 3 실패 시 (A1):**
- R1 결정이 SOT와 충돌(A15 R06) → SOT가 정본이므로 R1 수정
- SOT 자체 모순 → DF 역류 → D1 부분 재실행

**Phase 3 완료 조건**: Must 전부 통과 + 검증 체크리스트 통과 + 인수인계 확인 + 회고 기록

---

## Phase 4: V0 구현 (B2 + R2 + X2) — ⬜ 미착수 (코드 디렉토리 부재)

> **목적**: 스켈레톤 코드 생산 — 하네스 위에서
> **전제**: Phase 2 + Phase 3 완료
> **적용 전략**: A7(스킬 점검), A20(계약 거버넌스), A8(스킬 의존), A15(리스크 R07~R09, R14)
> **사용 자산**: STRATEGY_11 §3.4 "V0 코드 짤 때"

> ※ **Phase 4 ↔ PART2 V0 매핑**: V0 구현 상세의 정본은 PART2 §2 V0-STEP-1~6(+§7.1 V0 GO/NO-GO 16항·각 STEP 단계검증 게이트·§1.3 공통 규칙 R1~R11)이다. 본 표 4-1~4-7은 트랙 요약이며 구현 상세 충돌 시 PART2가 우선한다 — Phase 6 표의 V1 매핑 노트와 함께 **"로드맵=마스터 + PART2=V0·V1 실행 상세 정본"의 2층 구조**를 구성한다.

### 스킬/Hook 사전 점검 (A7 — STRATEGY_04)

```
Phase 4 착수 전:
  검증 스킬 11개 실행 가능 확인
  Hook 6개 트리거 정상 확인
  settings.json 경로가 실제 파일과 일치 확인
  결과: PROGRESS.md에 "도구 점검 PASS" 기록
  ※ Hook 분모는 점검 시점 .claude/settings.json 실측 기준 재확정(현행 16 wired —
    STRATEGY_04 "6개"는 작성 시점 값). 코드 생산 Hook 신설(py 수정 시 ruff·config LOCK
    검증, STRATEGY_10 §4 4-V4)은 2-4 산출물에 포함.
```

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 4-1 | B2c: 타입 동기화 | Pydantic→JSON Schema→serde→TS. **A20 규칙 적용**: Pydantic 정본, 자동 생성, 왕복 테스트 PASS | **Must** | 선행 | backend/vamos_core/schemas/ |
| 4-2 | R2a: ORANGE CORE 스켈레톤 | V0 활성 5(I-1/2/3/5/19)+stub 3(I-8/9/20) — **PART2 V0-STEP-4·§7.1 #12 정본**(전 25 파일 선생성 여부는 3-0 확정; 모듈 카탈로그는 I-1~I-25, D9) + 5-Phase Pipeline + Gate 3종(Policy/Cost/Approval — 5-Gate 완성은 V1) + **Defense Layer 3계층(A21)** + **reasoning_trace(A22)** + **confidence_score(A25)** | **Must** | ⓐ | backend/vamos_core/orange_core/ |
| 4-3 | R2c: 프론트엔드 스켈레톤 | Tauri 앱 셸 + React UI + IPC + **"왜?" 버튼(A22)** + **신뢰도 표시(A25)** + **면책 조항(A16)** | Should | ⓑ | src/ + src-tauri/ |
| 4-4 | R2a: Registry 정의 | EventType/Failure/Fallback Registry | **Must** | 순차 | |
| 4-5 | R2a: config.v1.toml | LOCK 값 포함. **confidence 임계값 3개(A25)** + **cost_monthly_limit(A21 Layer1)** | **Must** | 순차 | |
| 4-6 | R2b: BLUE NODE 스켈레톤 | 디렉토리 스캐폴딩만(PHASE_B2 — PART2 V0 스코프 E-Series 0; 노드 구현 E-1~E-6은 V1-Phase 3, 3노드 명칭 Dev/Research/Productivity는 D2.0-03) | Should | 순차 | backend/vamos_core/blue_nodes/ |
| 4-7 | X2: 횡단 실행 | 보안 스캔 + 테스트 작성 + 커밋 린트 | Should | ⓒ | 리포트 |

```
3트랙 병렬:
  4-1(Must,선행) → ⓐ 4-2→4-4→4-5→4-6 | ⓑ 4-3 | ⓒ 4-7

코드 생산 하네스 (매 커밋):
  코드 생성 → ruff → vamos_lint → pytest → PASS → 커밋

D2 상시 감시:
  SOT 수정 → Hook → "/sot-conflict scan 권장"
  DF 역류: SOT 모순 발견 → DESIGN_ISSUE → D1 부분 재실행

인터페이스 변경 시 (A20):
  Pydantic 수정 → JSON Schema 재생성 → Rust/TS 재생성 → 왕복 테스트 → 4파일 동시 커밋
```

**Phase 4 중간 체크포인트 (A9 — MoSCoW):**

| STEP | 내용 | 우선순위 |
|------|------|---------|
| V0-STEP-1 | 디렉토리 구조 PHASE_B2 일치 | **Must** |
| V0-STEP-2 | 25개 Pydantic D2.1 일치 + confidence_score(A25) | **Must** |
| V0-STEP-3 | config.v1.toml 20개 LOCK + confidence 임계값 3개 | **Must** |
| V0-STEP-4 | JSON-RPC 왕복 테스트 PASS | **Must** |
| V0-STEP-5 | 5-Phase 최소 동작 | **Must** |
| JSONL 로깅 | 구조적 로깅 동작 | Should |
| L0 메모리 CRUD | Session Memory 기본 | Should |
| Tauri IPC 브릿지 | 프론트엔드 연결 | Should |
| E2E 테스트 | 입력→응답 전체 | Should |

> ※ 본 표의 V0-STEP-1~5는 A9 MoSCoW 중간체크포인트(자체 번호)로, PART2 정본의 V0-STEP 번호(STEP-3=IPC/JSON-RPC, STEP-4=ORANGE CORE 5-Phase, STEP-5=저장소+로깅)와는 별개 체계다.

```
V0-STEP Must 5개 + Registry·E2E 기본 흐름 2개 + 하네스 게이트(ruff·vamos_lint·pytest·CI) 4개 — 정본 STRATEGY_02 "V0 체크리스트 16항목"(표 L71~96) 中 Must 라벨 실측 11개(舊요약문 "10"은 표 라벨과 불일치 — 분모 11로 확정, STRATEGY_02 요약 동기 정정 완료)
Must 11개 전부 PASS → Phase 5 진입 가능
Should 미통과 → V1에서 보완 (A9)
```

**Phase 4 검증 체크리스트 (4-V):**
- □ Must 11개 전부 통과 (STRATEGY_02 표 기준 — 위 분모 확정 참조)
- □ B2c 타입 동기화: Python↔Rust↔TS 일치 + 왕복 PASS (A20)
- □ 하네스 자동 실행: 매 커밋 ruff+vamos_lint+pytest 확인
- □ 다층 방어 구현: config LOCK(Defense Layer1) + Gate 체인(Defense Layer2 — V0는 Policy/Cost/Approval 3종, 5-Gate 완성은 V1) + NEVER_AUTO(Defense Layer3) (A21)
- □ 사용자 투명성: reasoning_trace 필드 존재 (A22)
- □ 예측 신뢰도: confidence_score + 임계값 + 행동 분기 동작 (A25)

**Phase 4 실패 시 (A1):**
- Must 미통과 → 원인 분석(설계?코드?환경?) → 해당 영역 수정 → 재실행
- 3개 언어 타입 불일치(A15 R07) → A20 규칙: Pydantic에서 재생성

**Phase 4 완료 조건**: Must 전부 통과 + 검증 체크리스트 통과 + 회고 기록

---

## Phase 5: V0 검증 + GO/NO-GO — ⬜ 미착수

> **목적**: 품질 평가 + 설계↔코드 정합 + V0 릴리스 판정
> **전제**: Phase 4 완료
> **적용 전략**: A17(재현성), A24(배포 무결성), A15(리스크 R08)
> **거버넌스 교차**: READINESS_GUIDE V0 GO/NO-GO (16건)
> **사용 자산**: STRATEGY_11 §3.5

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 5-1 | B3: Eval 파이프라인 | ragas+deepeval+promptfoo+minicheck | Should | ⓐ | eval_results.json |
| 5-2 | B3: QoD 측정 | 5요소 가중합 | Should | 순차 | QoD 점수 |
| 5-3 | D3: 모듈 수 대조 | 모듈 카탈로그 25종(D9) 정의 ↔ 코드 구조 정합 — V0 실파일 분모는 PART2 §7.1 #12(활성 5+stub 3; 전 25 파일 선생성 채택 시 3-0 확정값) | **Must** | ⓑ | alignment_report.json |
| 5-4 | D3: 스키마 필드 대조 | D2.1 vs 실제 Pydantic + confidence_score(A25) 포함 확인 | **Must** | 순차 | |
| 5-5 | D3: Registry 대조 | EventType/Failure/Fallback vs 코드 | **Must** | 순차 | |
| 5-6 | D3: LOCK 값 대조 | config.v1.toml vs SOT LOCK + confidence 임계값(A25) | **Must** | 순차 | |
| 5-7 | X3: 횡단 운영 | CI pytest 자동 + commitlint + main 병합 | Should | ⓒ | |
| 5-7a | **배포 무결성 확인 (A24)** | 앱 기동 확인 + config LOCK 런타임 대조 + 기본 E2E 테스트 | **Must** | 5-7후 | |
| 5-8 | **V0 GO/NO-GO 통합** | Phase 5 완료 조건 + READINESS V0 16건 동시 확인 | **Must** | 전부후 | V0 릴리스 판정 |

```
3트랙 병렬:
  ⓐ 5-1→5-2 (Eval)
  ⓑ 5-3→5-4→5-5→5-6 (D3 정합)
  ⓒ 5-7→5-7a (횡단+배포검증)
  전부 → 5-8 (GO/NO-GO)

재현성 보장 (A17):
  멱등성 테스트: seed=42 고정 3회 실행 → 동일 결과 확인
  Eval 결과에 seed + 반복 횟수 기록
```

**Phase 5 검증 체크리스트 (5-V):**
- □ DRIFT 0건 (모듈 수, 스키마, Registry, LOCK 전부 일치)
- □ confidence_score 필드가 스키마+config+코드에 전부 존재 (A25)
- □ Defense Layer 3계층 독립 동작 확인 (A21)
- □ 배포 무결성: 앱 기동 + config 대조 + E2E (A24)
- □ 멱등성 3회 동일 확인 (A17)
- □ V0 GO/NO-GO 16건 전부 충족
- □ 자산 인벤토리 갱신 (코드 구조 반영)

**Phase 5 실패 시 (A1):**
- DRIFT 발견 → 설계 정본 기준 코드 수정 → Phase 4 해당 STEP 재실행
- GO/NO-GO 미충족 → 미충족 항목 수정 → 5-8 재확인

**Phase 5 완료 조건**: Must 전부 통과 + 검증 체크리스트 + GO/NO-GO + 회고 기록 → **V0 완료 + git tag v0-release**

---

## Phase 6: V1 구현 (Phase 1~5 반복) — ⬜ 미착수

> **목적**: V0 위에서 실제 기능 구현
> **전제**: V0 완료
> **적용 전략**: A23(마이그레이션), A24(배포 검증), A7(스킬 재점검)
> **거버넌스 교차**: PART1 B.2(12건), READINESS V1 GO/NO-GO (21건)

### 스킬/Hook 재점검 (A7)

```
Phase 6 착수 전: V0에서 코드 구조가 변경되었으므로 스킬 11개 + Hook 6개 재점검
```

### V0→V1 마이그레이션 규칙 (A23 — STRATEGY_06)

```
스키마 변경: Expand/Contract 3단계 (새 필드 추가 → 전환 → 구 필드 제거)
config: 기존 키 유지 + 새 키에 기본값 필수
모듈 활성화: OFF→ON은 config 수준 (코드 변경 없이)
데이터 호환: V0 SQLite → V1에서 읽기 가능
```

> ※ Phase 6 작업표는 타 Phase와 달리 **병렬 열이 없다** — 6-1~6-9의 트랙/선후는 위 V0→V1 마이그레이션 규칙과 6-8a→6-9 직렬 외에는 미정의(전체 구조표 Phase 6 행도 "선후만 정의"로 정정함).

| # | 작업 | 상세 | 우선순위 |
|---|------|------|---------|
| 6-1 | D1' 재검증 | V0 D3 결과 + COND 106개 추가 | **Must** |
| 6-2 | B1' 환경 확장 | vamos_lint Layer 2 (187개 네이밍) | **Must** |
| 6-3 | R2a': CORE 활성화 | CORE 실제 구현 — V1 활성 분모 = **PART2 §1.1 기준 32**(I17+E6+S1+A2+B1+C3+D2; V1-Phase 1은 I-모듈 17 우선. STRATEGY_08 표기 26은 구집계 — 충돌 시 PART2 우선, 최종 확정 3-0) | **Must** |
| 6-4 | R2b': 에이전트+RAG | LangGraph 3개 + BGE-M3→Chroma | **Must** |
| 6-5 | R2c': E2E UI | 입력→응답 + reasoning_trace(A22) + confidence(A25) 표시 | Should |
| 6-6 | R3: 운영 시작 | SQLite 모니터링 + 비용 추적(₩40K/월) + Alert | Should |
| 6-7 | B3': Eval | QoD≥0.70 + V1 벤치마크 4개 | **Must** |
| 6-8 | D3': API 정합 | 88개 API 계약 vs 코드 | **Must** |
| 6-8a | **배포 검증 (A24)** | /health + config LOCK 런타임 대조 + 핵심 E2E 1개 | **Must** |
| 6-9 | **V1 GO/NO-GO** | PART2 §7.2 22항목(=READINESS V1 21건 + MCP Bridge/Server/Client 개별 검증 1, FIX-11) + PART1 B.2(12건) | **Must** |

> ※ **Phase 6 ↔ PART2 V1-Phase 매핑**: V1 구현 순서의 정본은 PART2의 V1-Phase 1~6(Week 1~16)이다. 본 표에 직접 행이 없는 **AI Investing MVP·MCP(PART2 §6.6 서버/클라이언트 7개)·Circuit Breaker**는 PART2 **V1-Phase 6**(AI Investing MVP + MCP — Phase 4-5와 병렬, Week 13-16; Circuit Breaker 자체 구현은 V1-Phase 3 Workflow+Agent)에 배정되어 있다 — V1 착수 시 PART2 기준으로 스코프에 포함한다.

```
버전 간 역류:
  V1 D1'에서 V0 결함 발견 시:
    수정 ≤ 50% → V1 B2'에서 흡수 수정
    수정 > 50% → ESCALATE (사람 판단)
```

**Phase 6 완료 조건**: V1 MVP 동작 + QoD≥0.70 + 비용≤₩40K/월 + 배포 검증 PASS + V1 GO/NO-GO + 회고 기록 + git tag v1-release → **Phase 7(V2 사이클) 진입 준비**

---

## Phase 7: V2 구현 사이클 (Pro Server) — ⬜ 미착수 (V1 완료 후, "Phase 1~5 반복" 패턴 준용 — D11)

> **목적**: 로컬 MVP → Pro Server 승급 (서버 배포 + DB 업그레이드 + COND 활성화 + 보안 강화)
> **전제**: Phase 6 완료(v1-release) + **V1→V2 전환 조건 6건 전수**(QoD≥0.85 30일 · RAG 정확도≥60% · 메모리 승격/강등 오류율<1% · P0 테스트 100% · 비용 무초과 30일 · 사용자 승인 — 측정 방법·도구·주기·판정 기준은 PART2 §7.2 하단 "V1→V2 TC 측정 메커니즘" 표가 정본)
> **비용**: ₩93,000/월 LOCK (D10 · BASE-1.3) | **구현 상세 정본 = PART2 §4 V2-Phase 1~3** (Phase 4 노트와 동일한 2층 구조 원칙)
> **거버넌스 교차**: READINESS §4(V2 착수 전 준비) · §9.3(V2 GO/NO-GO 14건) + PART1 B.3(서버/인프라 + API Key 2 + GitHub Secrets 11) + STEP7 R4~R5(V2 항목 ~610건 — 7-0에서 6-1 D1' 패턴의 범위 재검증으로 수용)

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 7-0 | **V2 진입 게이트** | V1→V2 전환 조건 6건 판정 + PART1 B.3 인프라 준비 + **C.3 #1~3 결정 정식화**(D11 배정: #1 Redis 기확정→구현만 잔존, #2 GroupChat 순서 알고리즘, #3 Agent Marketplace 등록 기준) + **한국어 로컬 LLM 도입 결정**(PART1 C.2 #1 DEFER V1.1 — SOLAR/Polyglot-Ko 벤치마크 후 확정) + 3-0에서 V2 귀속 확정된 항목 수용(SDAR §10.1 기반·Cloud Library CB1·RT-BNP V1·4-4 MLOps 본대 — PART2 §4 보강 필요분 확인) + STEP7 R4~R5 범위 재검증 | **Must** | 결정 기록(decisions/) + 진입 판정 |
| 7-1 | V2-Phase 1: 인프라 마이그레이션 | SQLite→PostgreSQL · JSONL→PG · Chroma→Qdrant(재임베딩) · JSON→Neo4j · config v1→v2 · Docker Compose · 배포/롤백 스크립트 — **PHASE_B7 §6 10-Step Migration Orchestration + 사후검증 7항목** 준수 | **Must** | scripts/migration/ + docker-compose.v2.yml |
| 7-2 | V2-Phase 2: COND 모듈 활성화 | 원본 COND 10(I-7·I-12·I-22·I-23·I-25 SDAR AR-L2→L3·A-4·E-13~E-16[E-15 Cloud Collector+RT-BNP V1+DCL-GEO V2]) + **v10 확장 106(CAT-A~G 카테고리 그룹)** — V2 활성 모듈 합계 42(PART2 §1.1) | **Must** | backend/vamos_core/modules/ |
| 7-3 | V2-Phase 3: Agent Teams V2 + 보안 | Redis MessageBus · 협업 패턴 6종 · Lead+9 Sub-Agent · HMAC-SHA256 · LlamaGuard L3 · GDPR · Cloud Library V2 + RT-BNP V2 · SDAR AR-L3 확장 | **Must** | backend/vamos_core/agent_teams/ · security/ |
| 7-4 | **V2 검증 + GO/NO-GO** | D3''(모듈·스키마·Registry·LOCK 재대조 — 5-3~5-6 패턴 V2 분모) + Eval(QoD≥0.85 유지 확인) + 배포 무결성(A24 — Docker/SSH) + **PART2 §7.3 14항목(=READINESS §9.3 동수)** + 비용 모니터링 대시보드(₩93,000 이내) | **Must** | V2 릴리스 판정 |

**Phase 7 완료 조건**: 7-4 전수 PASS + 비용≤₩93,000/월(ABSOLUTE LOCK) + 회고 기록 + **git tag v2-release**

---

## Phase 8: V3 구현 사이클 (Enterprise) — ⬜ 미착수 (V2 완료 후)

> **목적**: Enterprise 완성 — **전 모듈 81개 활성**(I 25 + E 16 + S 8 + A 7 + B 6 + C 7 + D 6 + EVX 6, PART2 §1.1), 자기진화·에이전트 메시·셀프호스팅
> **전제**: Phase 7 완료(v2-release) + **V2→V3 전환 조건 전수**(QoD≥0.90 60일 · 2-tier LLM 최적화 · P1 고급 테스트 · Self-evo 체계 검증 · V3 비용 재검토+사용자 승인 — PART2 §7.3 하단 "V2→V3 TC 측정 메커니즘" 표가 정본)
> **비용**: ₩266,000/월 ABSOLUTE LOCK | **구현 상세 정본 = PART2 §5 V3-Phase 1~3**
> **거버넌스 교차**: READINESS §5 · §9.4(V3 GO/NO-GO 11건) + PART1 B.4(고급 인프라) + STEP7 R6(V3 전 항목 ~248건 — 8-0에서 범위 재검증으로 수용)

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 8-0 | **V3 진입 게이트** | V2→V3 전환 조건 판정 + PART1 B.4 준비 + **C.3 #4~5 결정 정식화**(D11 배정: #4 Federated Agent 승인 정책[OWNER 수동+샌드박스 72h 권장안], #5 A2A 프로토콜[JSON-RPC over Streamable HTTP — DEC-017 통일]) + STEP7 TITLE_ONLY 보강분 확인(PART2 §7.4 #7) | **Must** | 결정 기록(decisions/) + 진입 판정 |
| 8-1 | V3-Phase 1: 인프라 스케일업 | K8s Helm(선택) 또는 **Hetzner Lite + RunPod Serverless(권장 대안 — PART2 §5)** · vLLM 셀프호스팅 · 관리형 DB · Loki + Grafana Observability · config.v3.toml · Blue-Green 배포 | **Must** | deploy/k8s/ + config.v3.toml |
| 8-2 | V3-Phase 2: EXP 모듈 전체 활성화 | 그룹 1~15: I-18/I-21/I-24 · **S-2~S-8(Self-evo 서브시스템 — 거버넌스 게이트 포함)** · E-7~E-12(멀티모달) · A-3~A-7(Meta AI·Lazy·Federated·Remote) · B-1~B-6(학습) · C-4~C-7(추론) · D-3~D-6(생성) · EVX-1~6(실험) · RT-BNP V3 · **PARL Agent Swarm** — 전 81 모듈 도달 | **Must** | backend/vamos_core/ (modules·self_evo·learning·reasoning·generation·experimental) |
| 8-3 | V3-Phase 3: 고급 기능 + 최종 통합 | Agent Marketplace(LOCK-BM-09 70:30 — QoD≥0.7+테스트 10회+OWNER 승인) · 50+ Agent Mesh · S-8 거버넌스 확장 · SDAR AR-L4 · Cloud Library V3 · **A2A 프로토콜 구현** · 멀티모달 고급 · 최종 벤치마크 · Agent Specialization | **Must** | backend/vamos_core/agent_teams/ 외 |
| 8-4 | **V3 검증 + GO/NO-GO** | **PART2 §7.4 12항목(=READINESS §9.4 11 + PARL 1)** + SDAR V3 ON 조건(AR-L4·수리성공률≥95%·스냅샷복원 100%) + 비용 60일 연속 준수 확인 | **Must** | V3 릴리스 판정 |

**Phase 8 완료 조건**: 8-4 전수 PASS + 비용≤₩266,000/월 + 회고 기록 + **git tag v3-release** → **🏁 VAMOS AI 전 기능 완성(V0~V3 전 사이클 종결)**

> ※ **Phase 7~8 운용 원칙**: 세부 트랙·주차(Week)·AI 프롬프트·LOCK 값·검증 체크리스트는 **PART2 §4·§5가 정본**(2층 구조). V2/V3 항목별 결정 정식화 시점은 각 진입 게이트(7-0·8-0)이며 이는 D11 패턴("각 사이클의 Phase 3 상당")의 보존이다. docs\sot 3(LSG)은 D15(DRAFT) 유지 — 채택 시 LOCK_CHANGE_NEEDED 게이트 + DEC 재번호 선행(하단 선언 참조).

---

## 리스크 레지스터 (A15 — STRATEGY_01)

| # | 위험 | 확률 | 영향 | Phase | 대응 |
|---|------|------|------|-------|------|
| R01 | SOT 내부 불일치 다수 | M | H | 1 | 정본 우선순위로 해소 + 범위 축소(A9) |
| R02 | SOT↔SOT 2 불일치 다수 | H | H | 1 | 핵심 5개 도메인 우선(A10) |
| R03 | PART2 참조 구버전 | M | M | 1 | /sot-check method-c 탐지 + 갱신 |
| R04 | CLAUDE.md REJECT 판정 | L | M | 2 | 범위 축소 → BRONZE 허용(A1) |
| R05 | 린터 오탐 | M | L | 2 | warn 모드 → 안정화 후 error |
| R06 | R1 결정 SOT 충돌 | M | H | 3 | /sot-check 대조 → SOT 기준 수정 |
| R07 | 3언어 타입 불일치 | M | H | 4 | A20 Pydantic 정본 + 자동 생성 |
| R08 | V0 일부 미통과 | M | M | 4 | Must/Should 축소(A9) |
| R09 | CI 과엄격 속도 저하 | M | L | 4 | V0 ruff+pytest만 필수 |
| R10 | CLAUDE.md 보강이 D1 깨뜨림 | L | H | 2 | 보강 후 /sot-check 재실행 |
| R11 | SOT 2 중 기존 SOT 변경 필요 | H | M | 1 | D2 감시 + /integrity |
| R12 | Obsidian↔SOT 2 불일치 | M | M | 2 | 샘플 10% 수동 대조 |
| R13 | 외부 의존성 변경 | L | M | 2 | LOCK 버전 고정(A4) |
| R14 | 스킬/Hook 깨짐 | M | M | 4 | Phase 착수 전 점검(A7) |
| R15 | V1이 V0 깨뜨림 | M | H | 6 | 회귀 테스트 + expand/contract(A23) |
| R16 | verify-only 착시(보고서 ✅ ≠ 산출물 존재) | M | H | 4~8 | 산출물 디스크 실존 검증 |
| R17 | V2 마이그레이션 데이터 손실/불일치 | M | H | 7 | PHASE_B7 10-Step + 사후검증 7항목 + 롤백 스크립트(7-1) |
| R18 | V2/V3 인프라 비용 초과 | M | H | 7~8 | ₩93K/₩266K ABSOLUTE LOCK + 비용 대시보드(7-4) + Hetzner Lite 대안(8-1) |

---

## 전체 로드맵 시각화

```
시간 →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→

Phase 0                Phase 1        Phase 2           Phase 3
자산+매트릭스+리스크     D1 검증        보강/환경          설계/전략
─────────────────      ──────────    ─────────────     ────────────

트랙A: SOT 2 ━━━━━━━━━━━━━━━━━━┓
                                ┃
트랙B: Phase 0                  ┃
  0-0(인벤토리) ━┓               ┃
  0-1,0-2(병렬)  ┃               ┃
  0-3(매트릭스)  ┃               ┃
  0-6(Git+리스크)┃               ┃
                ┃               ┃
                ┗━━━━━━━━━━━━━━━╋→ D1 (1-2~1-9) ━━━━┓
                                ┃  + 재현성(A17)      ┃
                                ┗━━━━━━━━━━━━━━━━━━━━┛
                                                     ┃ 인수인계
                                                     ┃
                                                     ┣→ 2-0(환경+A4)
                                                     ┣→ 2-1(CLAUDE+A13)→2-2
                                                     ┣→ 2-3(Obsidian+A16) 병렬
                                                     ┣→ 2-4→2-5(린터) 병렬
                                                     ┃
Phase 3                Phase 4·5          Phase 6      ┃
설계/전략(R1+X1)        V0 구현·검증        V1 구현       ┃
──────────────        ──────────        ────────────  ┃
                                                     ┃
  ┣→ R1+A21+A22+A25 ━━━┓                             ┃
  ┣→ X1+A16(책임AI) ━━━━╋→ V0(4-1~4-7) ━━━━━━━━━━━┓  ┃
  ┃  (병렬)             ┃  + A20(계약)              ┃  ┃
  ┃                     ┃  + A7(도구점검)           ┃  ┃
  ┃                     ┃                          ┃  ┃
  ┃                     ┃  → 검증(5-1~5-8) ━━━━━━━╋━━╋→ V1
  ┃                     ┃    + A24(배포검증)        ┃  ┃  + A23(마이그레이션)
  ┃                     ┃    + A17(재현성)          ┃  ┃  + A24(배포검증)
  ┃                     ┃    + GO/NO-GO            ┃  ┃
  ┗━━━━━━━━━━━━━━━━━━━━━┛                          ┗━━┛

공통 (전 Phase): A5(PROGRESS.md) + A6(decisions/) + A11(회고) + A12(로드맵갱신) + A2(git tag)
```

> ※ 하단 블록 좌측 컬럼(R1+X1)은 **Phase 3**(설계/전략)으로, **Phase 2 완료 후 직렬 진입**한다(상단 Phase 2 트랙 → ┃ → R1/X1). 중앙=Phase 4·5(V0 구현·검증), 우측=Phase 6(V1). **Phase 7~8(V2·V3 사이클)은 "Phase 1~5 반복" 준용으로 본 도식엔 미표시 — Phase 7/8 작업표와 PART2 §4·§5 참조.**

---

## 참조 문서 맵

| 문서 | 경로 | 역할 |
|------|------|------|
| 실패/리스크 | `VAMOS Engineering\STRATEGY_01_FAILURE_AND_RISK.md` | A1+A2+A15 상세 |
| 범위/우선순위 | `VAMOS Engineering\STRATEGY_02_SCOPE_AND_PRIORITY.md` | A9+A10+A14 상세 |
| 세션/지식 | `VAMOS Engineering\STRATEGY_03_SESSION_AND_KNOWLEDGE.md` | A5+A6+A13 상세 |
| 도구/유지보수 | `VAMOS Engineering\STRATEGY_04_TOOL_MAINTENANCE.md` | A7+A8+A12 상세 |
| 안전/윤리 | `VAMOS Engineering\STRATEGY_05_SAFETY_AND_ETHICS.md` | A16+A21+A22+A25 상세 |
| 통합/배포 | `VAMOS Engineering\STRATEGY_06_INTEGRATION_AND_DEPLOY.md` | A20+A23+A24 상세 |
| 학습/품질 | `VAMOS Engineering\STRATEGY_07_LEARNING_AND_QUALITY.md` | A11+A17 상세 |
| 매트릭스 | `VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md` | 전체 작업 분류 (20셀) |
| 하네스 | `VAMOS Engineering\STRATEGY_09_HARNESS_ENGINEERING.md` | AI 코드 품질 보장 |
| 검증 체계 | `VAMOS Engineering\STRATEGY_10_VERIFICATION_SYSTEM.md` | 교차 참조 + 24건 갭 |
| 자산 인벤토리 | `VAMOS Engineering\STRATEGY_11_ASSET_INVENTORY.md` | 전체 파일/도구 역할 |
| 보강전략 | `CLAUDE 보강전략 V1.0.md` | CLAUDE.md 보강 계획 |
| Obsidian 전략 | `VAMOS HOME\OBSIDIAN-STRATEGY-v3.md` | 지식 그래프 구축 |
| PART1 | `docs\guides\VAMOS_구현가이드_PART1_진입전.md` | 체크리스트 82건 |
| PART2 | `docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | 구현 순서 + 린터/CI |
| READINESS | `docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` | GO/NO-GO 62건 |
| LOCK Registry | `VAMOS HOME\00_HUB\LOCK-DECISION-REGISTRY.md` | LOCK 469건 |
| 세션 실행 프롬프트 | `VAMOS Engineering\ROADMAP_SESSION_EXECUTION_PROMPTS.md` | Phase별 세션 실행 프롬프트 |
| D1 결과 인덱스 | `04. 구현단계\v13_results\phase0\D1_RESULTS_INDEX.md` | D1 검증 산출물 인덱스 + 이연 대장(D-1~D-4) |
| 결정 대장 | `_targets\DECISION_REGISTER.md` | 확정 결정 17건(D1~D7·D9~D11·D13~D19 — D8·D12 결번), 3-0 게이트 입력 |
| 정본화 검증 보고서 | `_targets\ROADMAP_정본화_검증보고서_2026-06-11.md` | 본 로드맵 전수 검증 + PART2 매핑표 + 수정 적용 근거 |

> ※ **문서 위상 선언 — `docs\sot 3` (Living System Graph) [D15, 2026-06-11]**: `docs\sot 3\LIVING-SYSTEM-GRAPH\00~12`는 **DRAFT 제안 계층**이며 정본(SOT/SOT 2)이 아니다. 본 로드맵 Phase 0~8 및 참조 문서 맵에 미등재이고, 자체 GO 조건인 DEC-018 승인도 미수행 상태다. 알려진 정본 충돌(신규 이벤트 78개 ↔ 6-12 LOCK-EL-02 134항목·LOCK-EL-09 네임스페이스 8종 / DEC-018 ID ↔ 정본 DEC-018 백테스트 엔진 선택[D2.0-05·D2.1-D7])은 **채택 결정 전까지 효력 없음 — 정본은 6-12 AUTHORITY_CHAIN**이다. 채택하려면 LOCK_CHANGE_NEEDED 게이트 + DEC 재번호가 선행되어야 한다.

> ※ **스코프 편입 선언 — V2/V3·한국어 LLM [2026-06-11 사용자 지시로 개정]**: 구 선언(D11 연계 — 오류리스트 §D 원번호 D12, DECISION_REGISTER에는 D11에 병합·D12 결번)은 V2/V3 GO 조건(25건)과 한국어 LLM을 "차기 로드맵 이연"으로 두었으나, **본 로드맵 Phase 7~8(차기 사이클 정식 편입)이 이를 대체**한다 — V2/V3 GO 조건은 7-4·8-4 게이트에, C.3 #1~5 결정 정식화는 7-0·8-0 게이트에, 한국어 LLM 도입 결정은 7-0 게이트에 배정. **D11의 실질(사이클 배정·결정 정식화 시점·V1 이후 선후)은 그대로 보존**되며, 변경된 것은 문서 패키징(별도 차기 로드맵 → 본 파일 내 Phase 7~8)뿐이다. 이로써 본 로드맵은 V0~V3 전 기능의 단일 진입점이 된다.
