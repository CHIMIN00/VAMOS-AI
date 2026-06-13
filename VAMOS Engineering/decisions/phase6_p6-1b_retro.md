# P6-1b 회고 — Phase 6 (V1 구현) [6-3 CORE 활성화 2분할 1/2] — I-Series 17 CORE 완성

> **세션**: P6-1b (2026-06-14) · **모델**: claude-opus-4-8[1m] · **effort**: max + ultracode
> **판정**: ✅ **PASS → P6-1b-2 진입 허용** (표준 구현 — 게이트 아님, A11)
> **범위**: I-Series 17 CORE 완성(V1-Phase 1). E6+S1+A2+B1+C3+D2(15) = P6-1b-2 · 6-4 RAG = P6-1c (비대상)

---

## 0. 결과 요약

- **I-Series 17 CORE 전수 활성화**: 기존 8(I-1,2,3,5,8,9,19,20) + **신규 9(I-4,6,10,11,13,14,15,16,17)** 구현·배선·테스트.
- **하네스 GREEN**: pytest **121 → 182**(+61) · mypy strict **26 → 35 files** · ruff clean · vamos_lint **0 / 57 files**.
- **잠긴 분모 무변경**: contracts 25 · registries **123/36/23**(추가 0 — 등록 식별자 재사용) · 5-Gate 순서 · 9-State S0~S8 · confidence 0.85/0.60/0.30 · 직선 5노드 토폴로지 — 전부 불변.
- **2 FLAG 해소**(STEP 0) + **적대 검증 7건 수리**(2 major correctness bug 포함) + **round-2 dry 수렴**.
- 커밋 14건(8ba3fcb → ad576d5), tag 없음(v1-release = 6-9).

---

## 1. STEP 0 — P6-1a 2 비차단 FLAG 해소 (commit dad1602)

| FLAG | 내용 | 해소 |
|---|---|---|
| 1 (SOT2 스캔 stale) | Jun-5 스캔 vs Jun-12 코퍼스 변경(437파일) → active CONFLICT 0 CONDITIONAL | 현 코퍼스 재스캔: **active CONFLICT 0**(36 CONFLICT_LOG OPEN ledger 실측) · real_lock_mismatch 0(advisory 26 hit 전수 삼중분류 FP) · design broken-ref 0(canonical 1=2-2 nav-ref carry-forward, 범위 외) |
| 2 (integrity baseline stale) | Jun-4 485 drift(prior-session) | baseline 재생성 2654→2658, Jun-4 정본 backup 보존 → d1_prime_verify drift=0/regression=0 PASS |

- 신규 도구 `scripts/p6_1b_step0_rescan.py`(재현 가능, `--refresh-baseline`) + 증거 `p6_1b_step0_rescan_report.json` + d1_prime_report 비파괴 RESOLVED 주석.
- ⚠️ carry-forward: `2-2/04_cat-d-media/_index.md → ../_index.md`(2-2 root _index.md 부재) — conflict 아님·P6-1b 범위 외 → 6-9 게이트/2-2 유지보수 이연.

---

## 2. STEP 2 — 핵심 발견: D2.0-02 [LEGACY] 번호 ↔ D2.0-01 정본 reconcile

> **🔑 가장 큰 함정**: D2.0-02 §7 I-모듈 번호는 **PLAN-2.0 [LEGACY] 체계**(L624 배너) — 정본은 **D2.0-01 §5.6** + §4.0 매핑 테이블. 최초 research 에이전트 fact-pack 은 legacy 번호 기반이라 I-10/11/13/14/15/16/17 **오매핑**(예: legacy I-15=State Snapshot ≠ 정본 I-15=Evidence & QoD). 기존 V0 코드(i19_approval/i20_failure)가 D2.0-01 준거임을 tiebreaker 로 확인 → 전건 §4.0 재매핑.

신규 9 모듈 명세 출처 (D2.0-01 정본 ID 기준):

| 모듈 | 명세 출처 | 비고 |
|---|---|---|
| I-4 Multimodal Interpreter | D2.0-02 §7.31~7.40 (A* 해석차이) | 출력 구조화; 멀티모달 입력 = 6-4 stub |
| I-6 Self-check Engine | D2.0-02 §7.51~7.53 (A) | verify 노드 활성화 |
| I-10 Tool Registry/Router | D2.0-02 §7.63~7.68 | i5 라우팅 대체 |
| I-11 Output Composer | **0:1 GAP 신규** | deliver answer 합성 모듈화 |
| I-13 Multimodal Output Renderer | **0:1 GAP 신규** | 멀티모달 렌더 = 6-4 stub |
| I-14 Summarizer & Memory Distiller | **0:1 GAP 신규** | LLM 요약 = 6-4 |
| I-15 Evidence & QoD Manager | D2.0-02 §7.90~7.92 (legacy I-19) | EvidenceGate 활성화 |
| I-16 Knowledge Search | D2.0-02 §7.11~7.20 (I-2 overlap) | RAG = 6-4 |
| I-17 Blue Node Manager | **D2.0-03** | 노드 실행 = 6-4 |

### 핵심 전략: 등록 식별자 재사용 = 잠긴 분모(123/36/23) 변경 0

- `log_event` 가 EVENT_TYPES 강제 검증 → 신규 모듈은 **이미 등록된** 이벤트만 사용(예: I-6=`ui.main.selfcheck.*`, I-15=`ui.main.qod.updated`, I-4=`oc.i4.output.structured`). D2.0-02 §7 의 `oc.i6.*`/`oc.i19.*` 등은 [LEGACY] 미등록 → 미사용.
- 실패코드/폴백도 등록분 재사용(FB_DENY_WITH_REASON/FB_RAG_SWITCH_SOURCE/FB_ROUTE_SAFE_NODE 등). → **SOT-edit 승인 불요**(무단 분모 변경 0).

### 6-3/6-4 경계 엄수

- I-2/I-16 실검색·임베딩(BGE-M3/Chroma/BM25) = 6-4. 6-3 = 인터페이스 + 결정론 폴백.
- I-4/I-13 멀티모달(이미지/음성/다이어그램 렌더) = 6-4. 6-3 = 텍스트/코드/JSON 결정론.
- I-14 LLM 요약 = 6-4. 6-3 = 문장경계 결정론. I-17 노드 실행·MCP = 4-2/6-4. 6-3 = 레지스트리+요청봉투.
- 빈 EvidencePack(RAG 미수집) → EvidenceGate sufficient 직답 경로 보존(V0 무회귀).

### 파이프라인 활성화 (V0 스텁 → V1 모듈)

- verify 노드: 항상-PASS 스텁 → **I-6** 결정론 4-검증(출력/근거-결론/안전/자기모순).
- EvidenceGate: 항상-sufficient 스텁 → **I-15** QoD 실평가(<0.4 L2금지/<0.7 HOLD).
- deliver answer: 인라인 → **I-11** 합성. execute 구조화: **I-4** StructuredOutput. 라우팅: **I-10**.

### 기존 8 — 24규칙 enforcement 감사 PASS

RA_NEVER 10(never_auto verbatim) · Non-goal 7(i8 NON_GOALS verbatim) · cost(I-9) · schema(contracts model_validate) · logging(logger registry 강제) · config-order(config_loader LOCK) — 전수 intact, 하네스 무회귀.

---

## 3. STEP 3 — 산출물 검증 (commit e9660be)

- `verify_artifacts.py p6_1b_manifest.json` → **PASS 22/0** (9모듈+i5/pipeline 배선+9테스트+STEP0 산출물).
- 회귀 매니페스트 전수 PASS: p6_1a 16 · p6_0 11 · p5_1 10 · p4_2 34 · p4_3 10.
- `trace_matrix.py` → 요구 **26**(+9 6-3 I-module↔테스트) · 매핑 32 · 미커버 0 · 허위 0.
- `check_lockfiles.py` → drift 0.

---

## 4. STEP 4 — 적대 검증 (II-1/II-2/III-3, loop-until-dry)

**round-1**(ultracode wf, 17 에이전트 — 모듈별 독립 리뷰 + 발견 적대 검증): **확정 7건 수리** (commit 94d6a70)

| # | 모듈 | 심각도 | 결함 | 수리 |
|---|---|---|---|---|
| 1 | I-4 | **major** | 빈 content + format=code 가 `content.strip()` 가드로 검증 우회 → output_spec_ok 오True | 가드 제거 |
| 2 | I-13 | **major** | json 파싱 실패 시 rendered 무조건 True | try=True/except=False |
| 3 | I-15 | **major** | 저QoD 이벤트 links 에 fallback_id 누락 | FB_RAG_SWITCH_SOURCE 추가(i20 정본 매핑) |
| 4 | I-6 | minor | SelfVerdict 미생성 WARN | 이진 PASS/FAIL 로 narrow |
| 5 | I-14 | minor | summarize docstring max_chars 부정합 | 말줄임 +1 실동작 정합 |
| 6,7 | I-4/I-15 | minor | test-gap | 빈-code 테스트 + 이벤트 links 실측 테스트 |

**round-2**(4 에이전트, 수정 모듈 재검증): **수렴 dry** (commit ad576d5)
- I-4/I-13/I-15 수정 정확·신규결함 0. I-6 수정 정확.
- 단일 지적(contracts.py self_check verdict PASS|WARN|FAIL) = **오탐 판정**: ResponseEnvelope 는 A20 잠긴 계약, 정본 self_check 스키마(D2.0-02 §5.1.2-C)가 WARN 허용 — I-6 가 이진 부분집합만 생성할 뿐 계약 축소는 부정확(잠긴 계약 무단편집 금지). III-3 독립 판단으로 계약 보존 + pipeline 주석만 정합화.

> 교훈: 초기 구현에 **major correctness bug 2건**(I-4 가드·I-13 rendered) 존재 → 적대 검증이 잡음. 단위 테스트 green 만으로 불충분, II-1/II-2 필수.

---

## 5. 산출물 (자산)

| 자산 | 위치 | 비고 |
|---|---|---|
| 신규 9 I-module + 9 테스트 | `backend/vamos_core/orange_core/`·`backend/tests/` | iN_ 무패딩 |
| pipeline.py / i5_decision_engine.py 배선 | `backend/vamos_core/orange_core/` | verify/EvidenceGate/answer/route/structure 활성화 |
| scripts/p6_1b_step0_rescan.py + report | `scripts/`·`04. 구현단계/v13_results/phase0/` | STEP 0 재현 도구 |
| scripts/p6_1b_manifest.json + trace +9 | `scripts/` | H2/IV-3 |
| integrity_snapshot.json(2658) + .jun4 backup | `04. 구현단계/v13_results/phase0/integrity/` | baseline refresh |

---

## 6. 잔여 / 다음

- **다음**: **P6-1b-2** — E6 + S1 + A2 + B1 + C3 + D2 (15 모듈). 그 후 P6-1c(6-4 RAG) → 6-9 GO/NO-GO.
- **이월(P6-1b 비대상)**: item 11 NeMo/Guardrails 실설치(실 LLM 활성 시 6-3/6-4) · V1-004 enum·GO/NO-GO 분모·II-6 = P6-3 reconcile · 2-2 nav-ref broken(6-9/2-2 유지보수).
- 잠긴 분모 변경 0 → SOT edits 승인 불요(본 세션 SOT 무수정).
