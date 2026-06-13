# PHASE4-DEC-011 — Opus 4.8 ↔ Fable 5 역량 갭 폐쇄 수단 및 운영 SOP

> **결정일**: 2026-06-13 · **우선순위**: Must (구현 모델 전략) · **상태**: 확정
> **적용 범위**: Phase 4~8 (V0~V3 구현) — Phase 1·2·3 잠금분 제외
> **근거 SOT**: 최종 로드맵 R16/R15 · test_strategy.md §4 · PHASE_B5/B6 · STRATEGY_09(하네스) · STRATEGY_02(MoSCoW) · 2026-06 SWE-bench/Artificial Analysis 실측(Fable/Mythos > Opus 4.8, 갭=신뢰도)

---

## 1. 결정 (Decision)

주력 구현은 **Opus 4.8 단독**으로 진행한다. Opus↔Fable 갭(=단발 신뢰도·오류율, *추론 천장 아님*)은 **티어드 엔지니어링**으로 폐쇄한다:

- **(A) 지금 구현** — 잠긴 정본을 위반하지 않고 대상 코드가 존재하는 *순수 검증/분석 도구* 3종을 즉시 도입(아래 §A).
- **(B) 프로세스 SOP** — "파일"이 아니라 *운영방식*인 레버(멀티에이전트·컨텍스트 규율·에스컬레이션)는 본 ADR §B를 운영 표준으로 고정.
- **(C) 보류 + 사유** — 대상 코드 미생성 또는 잠긴 phasing 충돌로 *지금 하면 안 되는* 항목은 §C 대장에 사유·부착 Phase와 함께 등재. 각 Phase 진입 시 집행.

## 2. 이유 (Why)

- 2026-06 실측: 접근 가능한 최강 코딩 모델은 Fable 5(=Mythos-class, Opus 4.8보다 한 티어 위; SWE-bench Verified 95.0 vs 88.6). 그러나 **갭의 성격은 신뢰도/오류율**이고, 어려운 *설계 추론*은 Phase 3에서 LOCK으로 종결됨. 남은 작업은 "확정 정본에 맞춘 명세-구동 구현" = 자동 오라클로 정오 판정이 되는 영역.
- 이 조건에서 갭은 **오라클 강화 + 다중시도/적대적 검증 + 착시 방어**로 실효상 폐쇄된다(앙상블 검증은 단발 Fable보다 검증 구조가 두꺼움). Opus는 Fable 절반가라 N회+검증이 비용상 Fable 1회와 동급.
- 잔여 갭(자동 오라클 없음 + 신규 추론)은 Opus 단독으로 닫지 않고 **교차-모델 감사/에스컬레이션으로 라우팅**한다(§B-6, §B-VI).

## 3. 검토한 대안

- **대안 1: Fable 복귀 대기** — 기각. Fable은 이미 출시(2026-06-09); "막힘"은 접근/쿼터 이슈이며 해소 시점 불확실. 대기 = 순수 기회비용(P4-2 즉시 진행 가능).
- **대안 2: 비-Anthropic(GPT-5.5/Gemini/Grok)로 전환** — 기각. 에이전트 코딩에서 Opus보다도 열위(GPT-5.5 Pro 58.6%).
- **대안 3: §4 28개 전부 지금 물리 구현** — 기각. 대상 코드(Rust/TS) 미생성 + 잠긴 test_strategy §4(V0=0테스트 허용·깊이 V1부터·신규도구 없음)와 충돌 → 공회전·정본 위반·R16 착시 유발 위험.
- **채택: 티어드(A/B/C)** — 즉시 가치(R16 직결)는 지금, 프로세스는 SOP로, 충돌/미성숙은 사유와 함께 해당 Phase로.

> **모집단 reconcile (전수 커버리지 증명)**: §4 항목 총 **28개** = I-1~9(9) + II-1~6(6) + III-1~4(4) + IV-1~4(4) + V-1~2(2) + VI-1~3(3). 배치: **§A 5개**(III-1/2/4, IV-3, V-2) + **§B 14개**(II-1~6, III-3, IV-1/2/4, V-1, VI-1~3) + **§C 9개**(I-1~9) = **28 (누락 0)**.

---

## §A. 지금 구현 — 산출물 (잠긴 정본 미위반)

| §4 ID | 산출물 | 역할 | 비고 |
|------|--------|------|------|
| III-1/2/4 | `scripts/verify_artifacts.py` + `scripts/artifact_manifest.json` | 산출물 디스크 실존·비어있지않음·SHA·필수문자열·참조 테스트 파일 *실존* 검증 (내용 참조 정합은 미검사) + 공허 매니페스트 차단 (R16 착시 게이트) | pytest 테스트 아님 → V0=0테스트 정본 미저촉. 신규 *검증 스크립트*(테스트 프레임워크 아님). ※III-4(referencing_test) 검증 메커니즘은 구현됐으나 시드 매니페스트는 미사용 — 대상 테스트 부착은 §C-증분(IV-3와 동일 헤지) |
| V-2 | `scripts/check_lockfiles.py` | 3-스택 락파일 정합(Python 실검사; Node/Rust 미생성 시 보류) | drift발 실패의 모델 오인 방지 |
| IV-3 | `scripts/trace_matrix.py` + `scripts/trace_matrix.map.json` | 명세→테스트 추적 + 미커버/허위매핑 탐지 (test_strategy §2.1 "AC 완전매핑" 원칙의 기계화) | 메커니즘 + 시드 7항; 모집단은 §C-증분 |

**도입 방식**: 위 3종은 `scripts/`의 기존 검증 도구(vamos_lint·check_config_lock·roundtrip_test·validate_schema_registry)와 동급의 *수동/게이트 실행* 도구다. **잠긴 CI 3-job(quality/test/vamos-lint)과 Hook을 수정하지 않는다** — CI 배선은 §D의 ADR-게이트 사안으로 별도 결정.

---

## §B. 프로세스 SOP — 운영 표준 (코드 아닌 레버)

구현가(Opus 세션/오케스트레이터)는 아래를 표준 운영절차로 따른다. **티어드 적용**(§E).

**B-멀티에이전트 (§4 그룹 II — 갭 폐쇄 본체)**
- **II-1 생성→적대적 검증**: 모듈마다 독립 회의론자 에이전트가 *반증 시도* 후에만 커밋.
- **II-2 N회 앙상블+심판**: 난도 높은 모듈은 다회 시도 → 심판 선택/병합.
- **II-3 상시 자동 리뷰어**: 모든 diff에 독립 리뷰(코드리뷰형)를 *커밋 전*에.
- **II-4 역할 분리**: 계획가→구현가→검증가를 별 컨텍스트로.
- **II-5 loop-until-dry**: 각 Phase 게이트 직전, 새 발견 0될 때까지 버그 스윕.
- **II-6 게이트 교차-모델 감사**: V0~V3 GO/NO-GO(5-8·6-9·7-4·8-4)에 Fable(복구 시)/GPT/Gemini 독립 감사역 투입 — 자기참조("Opus가 짜고 Opus가 PASS") 차단. (Phase 2/3 3-AI 감사의 구현게이트 제도화)
- **III-3 독립 검증 에이전트**: 구현가의 *서술을 무시*하고 디스크 상태 + 테스트 결과 + `verify_artifacts.py`(§A)에서 "완료"를 *재도출*하는 독립 검증 워크플로. 본 ADR의 재검증(gap-closure-reverify 워크플로)이 이 레버의 실시 예다.

**B-컨텍스트 규율 (§4 그룹 IV)**
- **IV-1 컨텍스트 팩**: 작업별로 해당 PART2 STEP + SOT 발췌 + 관련 LOCK + 스키마만 로드.
- **IV-2 원자적 분해**: 작업 단위를 오라클이 완전히 경계 짓도록 작게.
- **IV-4 STEP 사전점검 체크리스트**: 단계 진입 전 입력 누락 차단.

**B-에스컬레이션/결정성 (§4 그룹 VI·V-1)**
- **VI-1 단계적 에스컬레이션**: 모듈이 검증 N회(권장 3) 실패 → Fable(복구 시)/사람으로 라우팅. Opus 무한재시도 금지.
- **VI-2 리스크-티어 인간 체크포인트**: 폭발반경 큰 모듈(5-Gate·Permission Matrix·IPC 계약·V2 마이그레이션 스크립트·A2A)은 인간 승인 필수.
- **VI-3 완전성 비평가**: 각 게이트 직전 "빠진 요구사항/테스트/산출물?" 점검 에이전트.
- **V-1 생성 결정성**: 코드생성 시 모델 id + temperature(저/0) 고정 + 런런 메타 기록(A17의 *생성* 확장).

---

## §C. 보류 대장 — 지금 못 하는 항목 + 정확한 사유 + 부착 Phase

| §4 ID | 항목 | 지금 못 하는 정확한 사유 | 부착(집행 시점) |
|------|------|------------------------|----------------|
| **I-1** | Rust(clippy/cargo test/cargo-deny)·TS(tsc/eslint/vitest)·E2E(Playwright/tauri-driver) CI 배선 | **대상 코드 부재** — `src-tauri/`·프론트가 아직 없음(git 실측). P4-2/4-3가 생성. 없는 코드에 CI job = 영구 실패/공회전. test_strategy가 vitest/Playwright/tauri-driver를 *명명*만 했고 CI 강제는 미정. | **4-3**(셸 생성 직후) / 6-5 |
| **I-2** | 뮤테이션 테스트(mutmut/cargo-mutants/Stryker) | 잠긴 test_strategy §4 = **V0 스캐폴드 단계, 0 tests 허용, 실질 깊이 V1부터** + "신규 도구 없음". V0에 뮤테이션 = 정본 phasing 위반 + 측정 대상(테스트) 부재. *신규 도구 도입은 ADR-게이트 사안*(§D). | **6-7**(V1 Eval) — ADR 선행 |
| **I-3** | 커버리지 래칫 + 분기 커버리지 + 모듈별 하한 CI 강제 | 커버리지는 정본상 "실질 V1부터", V0=0테스트 허용 → V0에 래칫 무의미(0→0). | **6-2/6-7** / ci.yml |
| **I-4** | 프로퍼티 기반 테스트(Hypothesis/proptest/fast-check) | "신규 도구" + V0 테스트 깊이 미적용. ADR-게이트. | **6-3/6-4** |
| **I-5** | 메타모픽/차분 테스트(라우팅·RAG·에이전트) | **대상 컴포넌트 미구현** — 멀티브레인 라우팅/RAG/LangGraph 에이전트는 V1(6-4). | **6-4** / 7-3·8-2 |
| **I-6** | 골든/스냅샷(IPC 페이로드·생성 스키마) | IPC JSON-RPC 페이로드는 **P4-2가 생성**(아직 없음). 스키마 골든은 가능하나 *신규 테스트* → V0 정본 저촉. | **4-2 직후/5-4** — ADR-게이트 |
| **I-7** | 경계 퍼징(IPC/MCP) | IPC/MCP seam 미구현. | **5-7a/6-8** |
| **I-8** | 런타임 계약 강제(Pydantic strict + IPC 경계 런타임 검증) | IPC 경계 미구현. (mypy strict는 이미 잠금) | **4-1/5-4** |
| **I-9** | V0→V1 회귀 코퍼스 | V0 동작이 아직 미완(P4 진행 중) → 잠글 기준선 부재. A23은 *규칙*(잠금), 회귀 *자산*은 V1 구현물. | **6-1** |

> **공통 원칙**: §C 항목은 "능력 한계"가 아니라 **순서/성숙도** 때문에 보류된다. 각 부착 Phase 진입 게이트에서 본 대장을 재확인해 집행한다.

---

## §D. 잠긴 Phase 1·2·3과의 관계 (경계 선언)

- **수정하지 않는다**: ruff 13룰+banned-api, **mypy strict=true**(이미 적용), 보안린트(ruff "S"), pytest/cov 도구, **CI 3-job**, vamos_lint VL-001~005, 테스트 피라미드 80/60/100, AC→TC 매핑 원칙, 타입 왕복(4-1), 코드생산 Hook. → §A/§B는 이 위의 *순수 추가*이며 기존 잠금분을 건드리지 않는다.
- **ADR-게이트 사안(베이스라인 초과·잠긴 phasing 변경)**: §C의 신규 *테스트 프레임워크 도구*(I-2/I-4/I-6) 및 *CI job 추가*(I-1/I-3)는 잠긴 test_strategy §4("신규 도구 없음"·"V0=0테스트")의 변경이므로, 도입 시 **별도 ADR(PHASE4-DEC-012+) + LOCK 절차**를 선행한다. 본 ADR은 그 *계획*만 등재하며 자동 도입하지 않는다.
- 본 ADR은 A6(의사결정 기록) 준수 산출물이다.

---

## §E. 실행 모드 정책 (effort vs ultracode — 티어드)

| 작업 유형 | 모드 |
|---|---|
| 사소·기계적(config·보일러플레이트·단일파일) | Opus 평이 effort + 하네스(§A) |
| 표준 구현 모듈 | Opus effort high/max + 자동 하네스 + 상시 리뷰(II-3) |
| 난도·고위험 모듈(5-Gate·IPC·RAG·라우팅·V2 마이그레이션·A2A·self-evo) | **ultracode workflows**(II-1/II-2/III-3 + high) |
| 모든 Phase GO/NO-GO 게이트(5-8·6-9·7-4·8-4) | **ultracode workflows**(II-5/II-6/VI-3 + 교차모델) |

> effort-max는 *기본 깊이*이나 단독으로는 갭을 닫지 못한다(앙상블/적대 구조 부재). 갭 폐쇄는 ultracode 워크플로 층이 담당하며, **고위험 모듈 + 전 게이트에 선택 투입**한다(전면 풀가동 금지 — 비용).

---

## 6. 검증

- §A 3종은 도입 직후 자체 실행 + `verify_artifacts.py`로 상호 실존 검증(dogfood). **실행은 리포 루트에서**(기본 시드 경로는 cwd 비의존으로 `__file__` 기준 resolve):
  ```
  cd D:\VAMOS
  python scripts/verify_artifacts.py        # → PASS 5 / FAIL 0
  python scripts/check_lockfiles.py --root . # → drift 0건 (Node/Rust 보류)
  python scripts/trace_matrix.py --root .    # → 미커버 0 · 허위매핑 0
  ```
  (backend/에서 호출 시: `poetry run python ..\scripts\verify_artifacts.py --root ..`)
- §B/§C는 각 Phase 진입 게이트에서 본 ADR을 인용해 집행 여부 점검.
- **재검증 이력 (2026-06-13, 독립 적대적 워크플로 5라운드 — III-3/VI-3 실시, loop-until-dry까지 반복)**:
  - R1(리뷰어5+비평가1): major 6·minor 5·nit 1 → 공허 매니페스트 차단·항목 타입가드·PEP503 정규화·dev그룹 의존성·디렉터리 오통과 차단·문자열 tests 가드·BOM·문구 정정·모집단 23→28+III-3 §B 등재.
  - R2: 1차 전건 해소 확인·회귀 0; 신규 major 1(must_contain 문자열 글자단위 거짓GREEN) → 가드 추가.
  - R3: major 1(verify path 절대경로/'..' 이탈로 게이트 리포 밖 우회) → _within_root 차단.
  - R4: major 2(referencing_test 동일 우회 잔존 / min_bytes<1로 0바이트 거짓PASS) → 양자 차단.
  - R5: **converged — blocking 0, 양쪽 clean.** (경로우회 클래스 전면 차단 확인)
  - 각 라운드 수정마다 정상 회귀(verify 5/0·trace 갭0·합법 referencing_test PASS) + ruff(T201만) + backend pytest 108 무회귀 실측.
- 본 ADR은 PROGRESS.md / 로드맵 추적표에서 참조한다.
