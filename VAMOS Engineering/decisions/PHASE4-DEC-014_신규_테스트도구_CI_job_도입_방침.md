# PHASE4-DEC-014 — Phase 6(V1) 신규 테스트 도구·CI job 도입 방침 (계획 ADR)

> **결정일**: 2026-06-13 (P6-0, Phase 6 진입 게이트) · **포맷**: A6 · **우선순위**: Must (잠긴 test_strategy §4 초과 사안) · **상태**: 확정(계획) — 집행은 부착 Phase
> **승인**: 인간 사인오프(VI-2/VI-1) — P6-0 게이트 적대검증 wf_a202edf4-b5c(7 에이전트) PASS-WITH-CONDITIONS 조건 C3 + 사용자 승인(2026-06-13).
> **근거 SOT**: PHASE4-DEC-011 §C 보류대장 + §D 경계 / SESSION_PROMPT_SKELETON.md H4 Phase 6 행 / 잠긴 `test_strategy.md §4`(V0=0테스트·신규도구 없음·깊이 V1부터) / 로드맵 6-2·6-3·6-4·6-5·6-7

---

## 1. 결정 (Decision)

DEC-011 §C 보류대장의 **신규 테스트 프레임워크 도구**(I-2 뮤테이션 · I-4 프로퍼티 기반)와 **신규 CI job**(I-1 Rust/TS·E2E 배선 · I-3 커버리지 래칫)은 잠긴 `test_strategy.md §4`("V0=0테스트 허용·실질 깊이 V1부터·신규 도구 없음")의 **변경**에 해당하므로, 각 부착 Phase에서 **본 ADR을 선행 근거로** 도입한다. 도입 시점·도구·LOCK 절차를 아래 §3에 고정한다.

본 ADR은 **계획(authorization)만** 제공한다 — 실제 도구 설치·CI job 추가·LOCK 등재는 해당 부착 Phase 세션(6-2/6-3/6-4/6-5/6-7)에서 집행한다(코드 0 in P6-0).

## 2. 이유 (Why)

- DEC-011 §D는 신규 테스트 도구·CI job을 "별도 ADR(`PHASE4-DEC-012+`) + LOCK 절차 선행" 사안으로 못박았다. 그러나 **그 placeholder 번호 `DEC-012+`는 stale**다: `PHASE4-DEC-012`는 P4-3에서 CI mypy 소스전환+VL-004 테스트면제에 **이미 소비**되었고, `PHASE4-DEC-013`은 jsonrpcserver 채택에 점유되었다(디스크 실측 2026-06-13). 따라서 본 사안의 정본 ADR 번호 = **`PHASE4-DEC-014`(본 문서)**.
- V0는 스켈레톤(0테스트 허용)이었으나 V1은 실 기능 구현 — test_strategy가 명시한 "실질 깊이 V1부터"의 집행 시점이 도래했다. 보류는 *능력 한계*가 아니라 *순서/성숙도*였다(DEC-011 §C 공통 원칙).
- 적대검증(F3)이 "PHASE4-DEC-014+ 부재 + DEC-012+ 표기 stale"를 MEDIUM으로 확인 → 본 ADR이 그 forward-requirement를 기록·해소.

## 3. 도입 대장 (부착 Phase·도구·LOCK 절차)

| §C ID | 도구/배선 | 부착 Phase (로드맵·H4) | LOCK 절차(집행 시) |
|------|-----------|----------------------|-------------------|
| **I-1** | Rust(clippy/cargo test/cargo-deny)·TS(tsc/eslint/vitest)·E2E(Playwright/tauri-driver) **CI job 배선** | **6-5**(프론트 셸 위) | ci.yml job 추가 + STRATEGY_09 하네스 표 갱신 + LOCK 등재. 대상 코드(src-tauri/프론트) 실재 확인 후. |
| **I-2** | 뮤테이션 테스트(mutmut / cargo-mutants / Stryker) | **6-7**(V1 Eval) | 신규 도구 — pyproject dev/eval 그룹 핀(A4) + test_strategy §4 보강 LOCK + 임계(생존 뮤턴트 상한) 등재. |
| **I-3** | 커버리지 래칫 + 분기 커버리지 + 모듈별 하한 CI 강제 | **6-2 / 6-7** (ci.yml) | ci.yml coverage gate 추가 + 모듈별 하한값 LOCK 등재(테스트 피라미드 80/60/100 정합). |
| **I-4** | 프로퍼티 기반 테스트(Hypothesis / proptest / fast-check) | **6-3 / 6-4** | 신규 도구 핀(A4) + 대상 모듈(CORE 활성·RAG) 프로퍼티 정의 LOCK 등재. (⚠️ §C "I-4 프로퍼티-테스트" ≠ PHASE5-DEC-001 item 7 "모듈 I-4 Multimodal" — 별개) |

> ※ I-5 메타모픽(6-4)·I-7 퍼징(6-8)·I-9 회귀코퍼스(6-1)는 *신규 외부 도구 도입이 아닌 기존 하네스 위 테스트 작성*이므로 별도 ADR 불요(DEC-011 §C 부착열대로 해당 Phase서 직접 집행). **I-6 골든·I-8 런타임 계약은 5-4(Phase 5)서 부착·종결** — Phase 6 신규 대상 아님.
> ※ 잠긴 베이스라인 불변(DEC-011 §D): ruff 13룰·mypy strict·vamos_lint·기존 CI 3-job·테스트 피라미드는 무수정. 본 ADR은 그 *위에 추가*하는 신규 job/도구만 다룬다.

## 4. 검토한 대안 (기각)

- **P6-0서 즉시 도구 도입** — 기각: P6-0=착수 게이트(코드 0). 대상 코드/테스트가 아직 없어 영구 실패·공회전(DEC-011 §C I-1 사유 동일).
- **ADR 없이 부착 Phase서 즉흥 도입** — 기각: 잠긴 test_strategy §4 변경을 무근거 강행 = 정본 위반. 본 ADR이 근거를 선제공.
- **현황·계획만(ADR 미신설)** — 기각(사용자 결정 2026-06-13): forward-requirement가 게이트 노트에만 남으면 부착 Phase서 누락 위험(§C 선례 = 로드맵 cross-ref 등재로 누락 방지).

## 5. 네임스페이스 주의

- 본 엔지니어링 ADR `**PHASE4-DEC-014**`는 설계 결정 네임스페이스 `DEC-014`(= QoD/SourceQoD 가중치 공식 결정, D2.0-06 §7.3·MASTER_SPEC §8.8·§17.4)와 **번호만 같고 별개**다. 접두어(`PHASE4-DEC-` vs `DEC-`)로 구분한다. (P6-0 SOT 정정 시 MASTER_SPEC §8.8에 동 주의 병기.)

## 6. 검증

- 본 ADR은 계획 ADR — 집행 검증은 각 부착 Phase 게이트(6-2/6-3/6-4/6-5/6-7)에서 도구 실재·LOCK 등재·CI GREEN으로 수행.
- 본 ADR은 A6 준수 산출물이며 PROGRESS.md·로드맵 추적표·SESSION_PROMPT_SKELETON H4에서 참조한다(H4/§D "DEC-012+" stale 표기 → "DEC-014+" 정본 정정).
