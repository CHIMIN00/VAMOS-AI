# P6-1b-2 회고 — Phase 6 (V1 구현) [6-3 CORE 활성화 2분할 2/2] — E6+S1+A2+B1+C3+D2 = 15 모듈

> **세션**: P6-1b-2 (2026-06-14) · **모델**: claude-opus-4-8[1m] · **effort**: max + ultracode
> **판정**: ✅ **PASS → 6-3 전건 32 완성 → P6-1c(6-4 RAG) 진입 허용** (표준 구현 — 게이트 아님, A11)
> **범위**: E6(E-1~6) + S1(S-1) + A2(A-1/A-2) + B1(B-3) + C3(C-1/2/3) + D2(D-1/D-2) = **15 모듈**. 6-4 RAG = P6-1c (비대상)

---

## 0. 결과 요약

- **15 모듈 6-3 활성화**: I-Series 17(P6-1b) + 본 15 = **6-3 분모 32 전건 완성** → 로드맵 6-3 ✅.
- **하네스 GREEN**: pytest **182 → 254**(+72: 신규 59 + 적대 수리 13) · mypy strict **35 → 55 files** · ruff clean · vamos_lint **0 / 87 files**.
- **잠긴 분모 무변경**: contracts 25(A-1=BrainAdapterResponse·E=ToolRegistryEntry·B-3=MemoryRecord 전부 **재사용**, C/D 결과=모듈 내부 dataclass) · registries **123/36/23**(등록 식별자 재사용, 설계 이벤트 재매핑) · config 14섹션(B-3 모듈 상수, I-15 선례) · 5-Gate·9-State·confidence·토폴로지 — 전부 불변.
- **신규 의존성 0**(stdlib만 — C-3 ast·C-2 ast·B-3 math). SOT 무수정.
- **적대 검증 17건 수리**(major 5 — 단위테스트 green 코드의 실결함) + **round-2 dry 수렴**.
- 커밋 1건(이 세션), tag 없음(v1-release = 6-9).

---

## 1. STEP 0/1 — 진입·reconcile

- **STEP 0**: SOT 재스캔 **carry**(HEAD=6a1fa95 = P6-1b 커밋·tracked clean → 코퍼스 무변경, active CONFLICT 0 carry). 하네스 baseline 182 재확인.
- **STEP 1 3-원 reconcile**(catalog↔schema↔design): 식별/상태 = **D2.0-01 §(A) L1249 + §5.7~§5.12**(15 = S-1·E-1~6·A-1/2·B-3·C-1/2/3·D-1/2 실측) · 스키마 = **owner_schema_doc(D2/D4/D5/D6) + contracts 25** · 설계 = **SOT2 분산**(C/D-1/D-2=1-1_Verifier-Reasoning-Engines[04=D-1·05=D-2 동거] · A-1=6-9_Brain-Adapter-HAL · B-3=6-4/01_memory-hierarchy/B3_memory_decay.md · A-2=guides PART2 §6 · E=§5.8).
- **owner_schema_doc(스키마) ≠ 설계 도메인**(I-모듈 D2.0-02 §7 집중과 달리 분산) — 혼동 함정 회피, 병렬 Explore 3에이전트로 도메인별 정본 추출.

## 2. STEP 2 — CORE 구현 (3 서브페이즈)

**명명/위치 정본근거**(VL-006 시리즈 taxonomy I≤25/E≤16/S≤8/A≤7/B≤6/C≤7/D≤6 검증):
- `vamos_core/reasoning/`(C-1/2/3 + D-1/2 + `_common` — 설계 도메인 1-1 통합·BaseVerifier/BaseReasoningEngine 공유) · `vamos_core/adapters/`(A-1/A-2 §5.9) · `vamos_core/tools/`(E-1~6 §5.8 "외부 기능") · `vamos_core/storage/b3_memory_decay.py`(memory_store I-3 연계·owner D6) · `vamos_core/orange_core/s1_self_check_surface.py`(I-6/I-15 wrap·§5.7).

**6-3/6-4 경계**(엄수):
- C-1 결정론 모순/오류 규칙 / C-2 stdlib ast 안전 산술(eval 금지) / C-3 ast.parse 구문+정적 보안(코드 미실행) — 실 SAT·SymPy·Z3·Docker 샌드박스 = 6-4.
- D-1 규칙기반 전략선택+상태기계+골격 / D-2 융합전략+텍스트 패스스루 — 실 LLM·CLIP/Whisper/OCR = 6-4.
- A-1 5-step 결정론 라우팅(classify→filter→score→gate→select)+Fallback Chain+invoke stub — 실 멀티-LLM = 6-4. **BrainAdapterResponse 계약 재사용**.
- B-3 지수 감쇠 `0.5^(days/30)`·임계 0.3/0.1(B3_memory_decay.md §3 verbatim)·자동삭제 금지(LOCK-MR-005) — memory_records SQL 동결.
- E-1~6 ToolRegistryEntry 등록 + invoke stub — 실 외부 API/실행 = 6-4. **잠긴 TOOL_REGISTRY_SEED(2) 무변경**(라우터 entries 합성 → seed 2 + E 6 = 8).
- S-1 = I-6+I-15 wrap surface(재구현 금지). 파이프라인 verify 노드는 I-6 직접 사용(P6-1b 토폴로지 LOCK 보존) — S-1 은 비-파이프라인 통합 표면.

**등록 식별자 재사용**(설계 이벤트 미등록 → registries 정본 재매핑, P6-1b 선례):
- E: `ui.tool.call.{started,finished}`·TL_ERR_*·FB_USE_WEB_SEARCH/RETURN_RAW/REQ_REUPLOAD/RETRY_SOFT.
- B-3: `mem.reference.updated`(설계 memory.decay.* 미등록)·MC_ERR_STALE·FB_SHOW_STALE.
- A-1: `ui.node.selected`(설계 brain.route.* 미등록)·OC_I5_COST_OVER_BUDGET·FB_COST_DOWNSHIFT.
- C/D: 순수 계산(미등록 이벤트 발행 0 — 에스컬레이션은 should_escalate 결정론 노출, 실 I-20 라우팅 호출측).

## 3. STEP 3 — 산출물 검증

- `verify_artifacts.py p6_1b_2_manifest.json` → **PASS 28/0**(17 source + 10 test + tools/__init__).
- 회귀 전수 PASS: p6_1b 22 · p6_1a 16 · p6_0 11 · p5_1 10 · p4_2 34 · p4_3 10.
- ⚠️ **pre-existing 발견·수리**: p6_1a/p6_0 로드맵 anchor 2건 stale(P6-1b 로드맵 편집이 휘발성 status 문자열 깨뜨림, 본 세션 무관) → durable substring 으로 교정(`P6-1b ✅`/`P6-0 게이트 ✅`). pipeline 'SelfCheckEngine' anchor = S-1 rewire 시도가 깨뜨림 → rewire revert(S-1 standalone, C/D/E/A/B 와 동형·토폴로지 무변경)로 해소.
- `trace_matrix.py` → 요구 **41**(+15 6-3 모듈↔테스트) · 미커버 0 · 허위 0. `check_lockfiles.py` → drift 0.

## 4. STEP 4 — 적대 검증 (ultracode wf, loop-until-dry)

**round-1**(7 finders 모듈군별 + 적대 2-vote 반증): **19 후보 → 17 확정**(major 5 + minor 12). tools-e clean.

| # | 모듈 | 심각도 | 결함 | 수리 |
|---|---|---|---|---|
| 1 | C-2 | **major** | 0-나눗셈/오버플로(`1/0=5`·`10.0**10000`)가 MathEvalError 밖으로 escape → 호출자 크래시 | `_parse_eval` 가 ZeroDivisionError/OverflowError/ValueError 포착→MathEvalError→_deferred(REVIEW) |
| 2 | C-1 | **major** | 부정 토큰 부분문자열 매칭('no' in 'now')→허위 극성 반전·내용어 누락 | 영문 전체토큰 일치 + 한글 형태소 부분일치 분리 |
| 3 | C-1 | **major** | 불용어만 공유한 무관 문장→허위 모순('cat is black' vs 'dog is not white') | 불용어 필터(_STOPWORDS) — 의미 내용어만 비교 |
| 6 | D-2 | **major** | confidence_per_modality 타입 키 붕괴→중복 모달 순서 의존(0.0↔1.0) | 입력 단위 평균(순서 무관) + 타입별 평균 집계 |
| 12 | B-3 | **major** | naive 타임스탬프(SQLite CURRENT_TIMESTAMP) → tz-aware now 와 빼기 시 TypeError | naive → UTC 정규화 |
| 8 | D-1 | minor | select_strategy 부분문자열('optional'→'option') 허위 분기 | 영문 전체토큰 일치 |
| 9 | A-1 | minor | 도메인 오버라이드 모델이 후보집합 밖 선택(selected ∉ candidates) | 오버라이드 후보 편입 후 선두 선택 |
| 11 | A-2 | minor | update() 버전 증가가 patch("1.0.0")서 크래시 | 마지막 숫자 세그먼트 증가·비정형 append |
| 15 | S-1 | minor | minimal_check None-path dict 이 I-15 evaluate 키셋과 불일치 | l2_eligible/low_qod_count 추가 |
| 4,5,7,10,13,14,16,17 | C-2/C-1/D-2/A-1/B-3/S-1 | minor | test-gap | 13 신규 테스트(버그 경로 전수 커버) |

**round-2**(8 fix 독립 재검증·III-3): **전건 fix_correct·new_defect 0 → 수렴 dry**(commit 단일).

> 교훈(P6-1b 재확인): 단위테스트 green 코드에 **major correctness bug 5건**(0-나눗셈 escape·부분문자열 매칭 2·confidence 붕괴·naive 타임스탬프) 잠복. II-1/II-2 필수.

## 5. 산출물 (자산)

| 자산 | 위치 | 비고 |
|---|---|---|
| reasoning 패키지 6 (C-1/2/3·D-1/2·_common) + 6 테스트 | `backend/vamos_core/reasoning/`·`backend/tests/` | BaseVerifier/BaseReasoningEngine |
| adapters 2 (A-1·A-2) + 2 테스트 | `backend/vamos_core/adapters/` | A-1=BrainAdapterResponse |
| storage b3_memory_decay + 테스트 | `backend/vamos_core/storage/` | 지수 감쇠, memory_store 동결 |
| tools 8 (E-1~6·_base·__init__) + 테스트 | `backend/vamos_core/tools/` | I-10 ToolRegistry 합성 |
| s1_self_check_surface + 테스트 | `backend/vamos_core/orange_core/` | I-6/I-15 wrap |
| scripts/p6_1b_2_manifest.json + trace +15 | `scripts/` | H2/IV-3 |

## 6. 잔여 / 다음

- **다음**: **P6-1c** — 6-4 RAG/임베딩/실 LLM I/O/멀티모달 모델/실 solver(Z3)/Docker 샌드박스. 본 6-3 모듈들의 `defer_to_6_4` 마커가 6-4 진입점.
- **이월(P6-1b-2 비대상)**: item 11 NeMo/Guardrails 실설치 · V1-004 enum·GO/NO-GO 분모·II-6 = P6-3 reconcile · 2-2 nav-ref broken(6-9/2-2 유지보수).
- 잠긴 분모 변경 0 → SOT edits 승인 불요(본 세션 SOT 무수정). B-3 운영 컬럼(decay_score 등) DB 마이그레이션 = 6-4/후속.
