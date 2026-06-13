# VAMOS 진행 상태

> 최종 갱신: 2026-06-13 (**Phase 5 게이트(5-V) — V0 GO (CONDITIONAL→GO·PHASE5-DEC-001 스코프환원+인간 사인오프)·git tag v0-release**)

## 현재 Phase
**Phase 5 ✅ 완료 — P5-1 V0 GO/NO-GO PASS (2026-06-13)** → 다음: **Phase 6 (P6-0 V1 준비 게이트)**

## P5-1 결과 (2026-06-13) — Phase 5 (V0 검증 + GO/NO-GO): Eval + D3 정합 + 배포무결성 + 멱등성 + V0 16건 게이트 → V0 릴리스 판정
- ☑ **판정: V0 GO (CONDITIONAL→GO)**. 게이트 본체 전건 PASS, §2.8 16건 중 6건(2·7·11·13·15·16)이 'V0-스코프상 정당 이연/등가'로 미기록 상태 → **ADR PHASE5-DEC-001** 스코프환원 기록 + **인간 사인오프(VI-2/VI-1 — II-6 교차모델 미가용 정규 폴백)** → GO. tag **v0-release**.
- ☑ **5-V 횡단 7항 전건 PASS** (게이트 wf_0229a151-bb3, 9 에이전트 III-3 독립재도출+II-1 적대 3+VI-3 완전성, loop-until-dry): ① **D3 DRIFT 0**(모듈 25↔8·스키마 25/25 왕복 serde·Registry 123/36/23=D2.1-D2 §5.1·LOCK 23/0) ② confidence_score 3곳(DecisionSchema+config [confidence] 0.85/0.60/0.30+score_to_level) ③ Defense 3계층 독립(L1 config frozen / L2 5-Gate / L3 never_auto RA_NEVER) ④ 배포 A24 3단계(vamos-app.exe+rpc 8테스트 / config LOCK 런타임 / E2E run_pipeline→oc.done) ⑤ 멱등성 A17(seed=42·temp=0 3회 동일 — per-prompt 워밍업으로 KV-cache 잔여 제어) ⑥ V0 16건(아래) ⑦ 자산갱신(STRATEGY_11 §2.16).
- ☑ **V0 GO/NO-GO 16건(READINESS §2.8 — ≠ Must 11 ≠ PART2 완료 13)**: 디스크실측 SATISFIED 10(1·3·4·5·6·8·9·10·12·14) + SATISFIED_BY_DESIGN 2(11 Guardrails=P4-0⑩ 코드등가 / 16 SQLite programmatic·Alembic 이연) + DEFERRED_V1 1(15 Chroma=V1) + 부분/리터럴-이연 3(2 24규칙 안전핵심 부분코드화 / 7 I-4=V1:ON / 13 data 5종중 logs·sqlite 활성) — 6건 환원 ADR 기록.
- ☑ **5-1/5-2 Eval (Should·DEC-007)**: [tool.poetry.group.eval] optional 등재(ragas 0.4.3·deepeval 4.0.6 A4 핀) → `poetry install --with eval` → import PASS. 골든셋 v2 162문항(mmlu 50/humaneval 20/mbpp 50/logickor 42) Ollama llama3.2:3b 실행 → mmlu 56%·humaneval 45%·mbpp 66%·logickor 95.2% · **QoD 5요소 가중합 0.8471**(Accuracy 0.30+Relevance 0.25+Completeness 0.20+Safety 0.15+Efficiency 0.10, CLAUDE.md:300 PLAN정본) → `benchmark_results/eval_results.json`(seed·반복 기록). QoD<0.85=V0 스켈레톤+mini모델 한계, V1 RAG+main모델 30일 목표(A9 비차단).
- ☑ **산출물 게이트(H2)**: `scripts/p5_1_manifest.json` → verify_artifacts PASS/0 + P4-2 회귀 34/0·P4-3 10/0 · trace_matrix 요구15(5-3~5-6 +4)·매핑21·미커버0·허위0 · check_lockfiles drift 0(eval 그룹 등재 후 poetry.lock 정합).
- ⚠️ **비차단 flag(정정 권고)**: ① PART2 L1621 'EventType 134'=stale(정본 D2.1-D2 §5.1=123·코드 123) ② 본 PROGRESS L186/로드맵 L443 'V0 16건=PART2 §7.1' 라벨 부정확 → 디스크 검증원=READINESS §2.8 ③ data/backups 디렉토리 미생성(backup_enabled=true) ④ 하네스 false-skip(check_config_lock=config 파일경로 인자 필수·vamos_lint=backend 경로).
- 🔴 **II-6 교차모델 미가용**: GPT/Gemini/Fable 환경 미접근 → 게이트는 Opus 앙상블(II-1/II-2/III-3/VI-3/II-5)+인간 사인오프로 수행(H9-3 Opus 페르소나 대체 금지 준수). V1 게이트(6-9)서 복구 우선.
- 📌 **P6-0 입력**: ① V0 GO 완료·tag v0-release ② §C I-1~I-9 전건 재확인(I-1 CI배선·I-6 골든·I-7 퍼징=DEC-014+ ADR 선행) ③ V1 활성화: Chroma 벡터/RAG(I-2)·graph_db·Alembic(스키마 진화)·24규칙 잔여·I-4·NeMo/Guardrails-AI ④ II-6 교차모델 복구 ⑤ Eval QoD≥0.85(V1 RAG).

## P4-3 결과 (2026-06-13) — Phase 4 게이트(4-V): Must 11 + A20/A21/A22/A25 + 게이트 적대검증(ultracode) → Phase 5 진입 판정
- ☑ **판정: PASS — Phase 5 진입 허용 (수리 후)**. 서사: **NO-GO(CI 2/3 RED)** → 사용자(VI-1/VI-2) "수리 인가 + 재게이트" → A1 수리(ADR **PHASE4-DEC-012**) → **재게이트 converged GO**. 신규 코드 0 원칙은 게이트 자체에 적용되었고, 발견된 결함 수리는 A1 경로(사용자 인가)로 집행.
- 🔴 **게이트가 잡은 핵심 결함 (독립 적대검증 III-3 — PROGRESS "PASS 단언" 디스크 반증)**: CI 3-job 중 **2개가 배선 그대로 RED** — ① `ci.yml:24` `mypy tests/`=88 errors(quality RED, stale placeholder 전환 미집행) + 소스 `mypy vamos_core`=**12개 실제 strict 타입결함**(Optional LLM `.ainvoke` NPE·`str`→`Literal` 게이트결과 등 — mypy가 tests만 봐서 한 번도 게이트 안 됨) ② `vamos_lint.py backend`=1 violation(test_config.py:75 LOCK-거부 테스트 오탐, vamos-lint RED). 완전성비평가(VI-3) **asymmetric-tolerance 논거**(pytest엔 exit-5 V0 관용 있으나 mypy/lint엔 없음 → "V0이라 봐준다" 불성립)로 NO-GO 정당화.
- ☑ **A1 수리(PHASE4-DEC-012, 사용자 인가 — 잠금 강도 불변·스코프 교정만)**: ① 소스 mypy 12건 수정(`pipeline·i1·i5·i9·config_loader` — cast 7+float 2+or-chain 1, **순수 타입레벨 런타임 무변경**) ② `ci.yml` mypy `tests/`→`vamos_core`(strict=true 유지·제품 소스 게이트) ③ `vamos_lint.py` VL-004 테스트 파일 면제(R5 의도=런타임 덮어쓰기 금지이지 거부테스트 금지 아님). contracts.py/registries.py/SOT **무변경**.
- ☑ **Must 11 전건 실측 PASS**: 1 monorepo 6디렉토리 / 2 contracts ALL_MODELS=25·non-forbid 0 / 3 IPC rpc 13메서드+ping·test 8·ipc_spawn_check 5-7a PASS / 4 pipeline 5노드(intake→plan→execute→verify→deliver) / 5 E2E pipeline·Ollama / 6 config VamosConfig 14섹션 frozen / 7 registries 123/36/23+is_valid / 8 ruff All passed / **9 vamos_lint `backend` 위반 0(수리후)** / **10 CI 3-job 전부 GREEN 실측(수리후) — quality(ruff+mypy vamos_core exit0)·test(pytest 118)·vamos-lint(0)** / 11 pytest **118 passed**.
- ☑ **4-V 추가 4항**: A20 왕복 25/25(serde cargo deny_unknown_fields 포함) · A21 3층(L1 config frozen ValidationError / L2 5-Gate pipeline 배선 / L3 NEVER_AUTO frozenset RA_NEVER_01~10 `is_never_auto` 단독판정) · A22 DecisionSchema `gates` 필드(reasoning_trace 수용처 DEC-010) · A25 confidence 임계(0.85/0.60/0.30)+REFUSE 분기 단위테스트.
- ☑ **갭폐쇄 도구·산출물 게이트**: verify_artifacts P4-2 매니페스트 회귀 **34/0** + P4-3 매니페스트 PASS · trace_matrix 요구11·매핑12·미커버0·허위0 · check_lockfiles drift 0(Python/Node/Rust).
- ☑ **게이트 적대검증 수렴(H3/H5 ultracode)**: R1(5 에이전트 III-3 그룹재도출 A/B/C PASS·D FAIL + VI-3 완전성비평가 NO-GO) → 수리 → R2(CI 재도출 all_green + 적대 회귀비평가 fixes_sound=true·masked_bug 0·pytest118/roundtrip25·25/IPC PASS, GO) → **신규 발견 0 = converged**. **II-6 교차모델**: 워크플로 에이전트=Opus 자기참조(H9-3상 불충족), GPT/Gemini 환경 미접근 → **인간(사용자) VI-1/VI-2 게이트 승인으로 대체**(수리 인가 판정).
- ☑ **마감**: 회고 `decisions/phase4_retro.md`(A11) + STRATEGY_11 §2.15 Phase 4 자산 등재 + 로드맵 추적표 §8 P4-3 ✅ + **git tag `phase4-complete`**.
- 📌 **P5-1 입력**: ① Phase 5 = V0 GO/NO-GO 16건(PART2 §7.1) 분모 — P4-3 비대상이던 릴리스 게이트 ② Eval 스택(ragas·deepeval·minicheck) poetry `eval` optional 그룹 등재(DEC-009 ⑬) ③ D3 정합(모듈수·스키마·Registry·LOCK) ④ 5-7a 배포무결성(GUI 기동 기실측) ⑤ **잔여 V1 hardening 후보**(비차단): 테스트 strict 타입화 88건(6-7) · UI vitest(I-1·6-5) · Rust/Node CI job(DEC-012+ ADR·6-5) ⑥ 백업/회귀 기준선.

- 🔧 **2026-06-13 갭폐쇄**: PHASE4-DEC-011(Opus↔Fable 갭폐쇄 수단·SOP) + scripts 3종(verify_artifacts·check_lockfiles·trace_matrix) + 2시드(artifact_manifest·trace_matrix.map) — 미커밋분 → P4-2 시작 전 독립 커밋(verify 5/0·trace 갭0·lock drift 0 실측·pytest 108 무회귀)

## P4-2 결과 (2026-06-13) — IPC JSON-RPC 13 + A20 serde 왕복 + Tauri 셸 + BLUE NODE + UI (B2c·R2c: 로드맵 4-1 serde·4-3·4-6·4-7 + V0-STEP-3)
- ☑ **판정: PASS — P4-3 진입 허용** (수렴 선언: 독립 적대검증 ultracode 2라운드 — R1 5리뷰어 clean + 완전성비평가 실 findings 5건[major 2·minor 3]·nit 1 → 수정 4 + 잠금-순연 명기 1 → R2 fix-verify·critic 양자 clean·**신규 실 findings 0 = converged**). §E 고위험 Must(serde/IPC/spawn) ultracode 워크플로 적용.
- ☑ **Must 전건 (V0 게이트 직결)**:
  - **① A20 serde 활성화 (4-1 완성, DEC-005 §5)**: `generate_types.py` serde 슬롯 활성 → `src-tauri/src/models/generated.rs`(25 구조체·`#[serde(deny_unknown_fields)]`=extra='forbid'·`roundtrip_validate` 디스패처) + **왕복 4파일 PASS 25/25**(Python→JSON Schema→serde[Rust cargo test 컴파일]→TS[Node]→Python 동일성). deny 미지필드 거부 **25/25 negative**. contracts.py/registries.py **무변경**(git diff 0).
  - **② V0-STEP-3 IPC (PHASE_B1 §5.2 / DEC-006)**: `backend/vamos_core/rpc/server.py` — jsonrpcserver 13 메서드 stub(파라미터 검증 -32602·미존재 -32601 자동) + ready 센티넬(stdout 첫 줄) + structlog→stderr(M-5) + 비즈니스 에러 -32000 `data.failure_code`=FailureCodeRegistry 등재값. `system.ping`(헬스 인프라, 13 분모 별개). test_rpc_server 8건.
  - **③ Rust python_manager + Tauri 셸 (5-7a 서브셋, DEC-008)**: `bridge/python_manager.rs` 스폰(`python -m vamos_core.rpc.server`·env 경유·하드코딩 0)+stdin/stdout 파이프+stderr 별도스레드+ready 대기+health(ping/pong)+자동재시작(max=3)+타임아웃(30s) / `commands/` 5종(#[tauri::command] Result<T,String>) / `state.rs` AppState(브릿지 지연스폰+인메모리 config·LOCK 키 거부 A21 L1) / main·lib·build.rs·tauri.conf.json·capabilities·icon → **cargo build(Tauri) PASS** + **5-7a 스폰 통합 PASS**(spawn+ready+ping/pong+dispatch+자동재시작 / 재시작 budget 경계) + **GUI 창 기동 ✅ 실측 PASS**(2026-06-13 사용자 데스크톱 `pnpm tauri dev` — 창 부팅 + Python 지연스폰[터미널 `rpc.server.start` methods:13] + workflow.run/decision.create 디스패치 렌더 + A22[왜?]/A25[신뢰도 N/A]/A16[면책] + stderr 분리 + 에러 0).
- ☑ **Should**: 4-3 React UI(5 커맨드 invoke 배선 + ConfidenceBadge[A25]/WhyButton[A22 reasoning_trace]/Disclaimer[A16], `pnpm build` tsc+vite PASS) / 4-6 BLUE NODE 디렉토리 스캐폴딩(dev/research/content __init__·구현 0·E-Series V1-Phase 3·seed 충돌없음) / 4-7 X2(보안 7항목 스캔 CRITICAL 0·테스트 보강·commitlint 준수 — `_targets/p4_2_x2_report_2026-06-13.md`).
- ☑ **의존성·하네스**: Python `jsonrpcserver>=5.0,<6.0`(PHASE4-DEC-013·PART2 V0-STEP-3 L410·B3 미핀) / Rust Cargo(tauri 2·serde·serde_json·tokio·tauri-build) / Node package.json(react 18.3·@tauri-apps/api 2.2·zustand 5·vite 6·typescript 5.7·zod 3.24). **3-stack 락 정합 drift 0**. **pytest 108→118**(+10: rpc 8·blue_nodes 2) 무회귀 · ruff(backend) clean · 신규 backend mypy clean · cargo build/test 전건 PASS.
- ☑ **산출물 게이트(§A)**: `scripts/p4_2_manifest.json`(34 산출물) → **verify_artifacts PASS 34/0** · `trace_matrix.map.json` V0-STEP-3 4행 추가 → 요구 11·매핑 12·미커버 0·**허위매핑 0** · Stage Gate 8항+V0-STEP-1 잔여+A20+5-7a 전건 실측(`_targets/p4_2_stage_gate_실측_2026-06-13.md`).
- ☑ **신규 ADR PHASE4-DEC-013**: jsonrpcserver 채택+버전핀(§1.3.1 #3 — B3 미핀 공백 ADR 메움). PHASE4-DEC-012는 CI job 추가 게이트용으로 **예약(본 세션 미생성 — 로컬 하네스로 진행, §D 준수)**.
- ⚠️ **이형/순연 기록(SOT·로드맵 무수정)**: ① 로드맵 L379 BLUE NODE 'Productivity'=오기(정본 content) → edits 명기·승인대기(`_targets/p4_2_roadmap_edits_pending.md`) ② 舊 세션표(§8) "IPC V0-STEP-4 / Pipeline V0-STEP-5 Must / BLUE NODE Must" 오류 → 추적표 교정 주석 집행(IPC=STEP-3·STEP4/5는 P4-1 완료·4-6=Should) ③ UI 런타임 테스트(vitest)=PHASE4-DEC-011 §C I-1 **잠금-순연**(4-3/6-5 ADR-게이트) — V0 게이트=tsc+vite(통과), 적대검증 인지·수용. → **2026-06-13 누락방지 cross-ref 등재**(로드맵 6-5 행[I-1 vitest+CI]·6-0[P6-0 게이트, §C I-1~I-9 우산]·6-7[I-2 뮤테이션] + 세션 P6-2/P6-0 + ADR §C 역참조): §C 전 항목이 P6-0 V1 착수 게이트에서 재확인·게이트화됨.
- 📌 **P4-3 입력**: ① **Must 11 분모**(GATE-03 — 로드맵 4-2/5-3/6-3) + V0 GO/NO-GO 16항 현황 점검 ② serde 왕복·IPC 13·5-7a 전건 PASS(차단 0) ③ **PENDING/보류**: ~~cargo run GUI 창 기동~~ → **✅ 실측 PASS(2026-06-13 데스크톱)** / UI vitest(I-1 순연·4-3/6-5) · CI Rust/Node job(PHASE4-DEC-012 ADR 선행 시·6-5) — 잔여 2건 전부 비차단·잠금순연·게이트 판정 시 사유 명기 ④ contracts.py/registries.py/SOT 무변경 유지 ⑤ 잔여 Should 완료(4-3 UI 스켈레톤 이상·4-6·4-7 전건 집행) ⑥ Ollama 실측 기완료(P4-1) ⑦ 백업 `_targets/_integ/backup_p4_2/`

## P4-1 결과 (2026-06-12) — ORANGE CORE 8파일 + Registry 연동 + config.v1.toml (B2a·R2a: 로드맵 4-2+4-4+4-5)
- ☑ **판정: PASS — P4-2 진입 허용** (수렴 선언: 적대 R1 공격 6종 전건 증거 방어 → R2 신규 발견 0. Stage Gate 23항 전건 실측 — 보류 0, `_targets/p4_1_stage_gate_실측_2026-06-12.md`)
- ☑ **실파일 8/8 (GATE-03 분모)**: `backend/vamos_core/orange_core/{i1_intent_detector, i2_context_builder, i5_decision_engine, i8_policy_engine, i9_cost_manager, i19_approval_manager, i20_failure_manager}.py` 7 + I-3 구현체 `storage/memory_store.py` 1. 분모 외 지원: `orange_core/pipeline.py`·`infra/{config_loader, logger}.py`·`safety/never_auto.py`. 전 모듈 async·경계 model_validate 의무·전이 LogEvent·전 코드 LF(git i/lf·w/lf)
- ☑ **4-5 config**: `config/config.v1.toml` **14섹션**(B4 13+[confidence] — B4 §4.1+PART2 V0 템플릿 정본 추출, 창작 0) · LOCK 물리 21 수록+[core] ipc 2키(3/30, DEC-009)+alert_thresholds=[70,85,95](DEC-002) · `check_config_lock.py` 분모 20→**23** 갱신 → Hook ✅ "LOCK 23키 위반 0건"(미정의 2키=blue_nodes·ui V0 부재 정상 경로) · `config_loader.py` VamosConfig+서브모델 14종·3단계 로딩(TOML→ENV `VAMOS_{SECTION}_{KEY}`→CLI·LOCK 전 단계 변경 불가)·frozen(런타임 변경 시 ValidationError — Defense Layer 1)·get_config() 싱글톤
- ☑ **4-2 코어**: LangGraph StateGraph 직선 5노드(intake→plan→execute→verify→deliver, START/END 상수 — DEC-001 오케스트레이션 한정·중첩 0·Gate 우회 0) + S0_RECEIVED~S8_DONE 전이 기록 + Gate deny/hold 시 조기 종료(토폴로지 정본 보존 — execute pass-through·LLM 미호출) + 4-Gate(Policy→Approval→Cost→Evidence)+SelfCheckGate verify 스텁(SKIP→PASS 갱신) + **A21 3계층**(L1 config frozen / L2 게이트 / L3 `safety/never_auto.py` RA_NEVER_01~10 frozenset verbatim — 게이트 독립 차단 테스트 PASS) + ResponseEnvelope 5필드 LOCK
- ☑ **신규 ADR PHASE4-DEC-010** (A22 수용처 이형 단일 결론): reasoning_trace V0 수용처 = **Decision.gates["reasoning_trace"]**(기존 optional dict — 20필드 FREEZE 무변경)+decision_ref 연계. D2.1-D5 §4.9 9필드(metadata)는 P4-2 IPC/UI 계층 표현으로 별개 활성. **confidence V0 산출 스텁 명기**(SOT 산출식 미정의 — §1.3.1 #3): insufficient→0.0 REFUSE(강제·단위테스트 검증) / block·stop·denied→0.0 / unknown·ambiguous→0.50 LOW / 그 외 0.90 HIGH — level은 config LOCK 임계(0.85/0.60/0.30)에서 단일 함수 파생
- ☑ **4-4 Registry 연동**: LogEvent 발행 시 `registries.is_valid_event_type` 검증 의무(미등록 거부 테스트 PASS) + I-20 FAILURE_TO_FALLBACK 매핑(D2.0-02 모듈 절 기반 V0 서브셋·registries 양방 검증·로그만)
- ☑ **저장·로깅(V0-STEP-5)**: memory_store(PART2 SQL 정본·CRUD 5종·TTL `min(close, created+30d)` M-30·aiosqlite — 실DB `backend/data/sqlite/vamos.db` 생성 실측) + logger(structlog JSONL·정본 7필드 매핑 표·trace_id UUID v4 필수·`vamos_{date}.jsonl`) + schema_registry.toml [sqlite.tables] memory_records 동기 등재(P4-0 주석 예고분 집행)
- ☑ **하네스·테스트**: 의존성 4종(aiosqlite/tiktoken/structlog/aiofiles — B3 정본 버전, poetry venv 일치) · **pytest 108 passed**(기존 61 무회귀 + 신규 47: config 14·storage/logger 10·i1 5·i5 10(REFUSE 강제 경로 포함)·pipeline 8) · ruff/vamos_lint 0건 · 25모델 contracts.py/registries.py **무변경**(git diff 0) · 커밋 6건(d53c1a8→5a6e991) 매 커밋 하네스 PASS
- ☑ **Ollama 실호출 PASS(PENDING 아님)**: ChatOllama llama3.2:3b 실응답 + **실모델 E2E** `S8_DONE | ACCEPT | locked=True | confidence 0.9 HIGH` + 실답변·JSONL trace 일관
- ☑ **CLAUDE.md 갱신(4-5 바인딩·DEC-010 경로)**: §12 Decision 18→**20필드**(confidence 2필드+**approval_status 4값→D7 정본 2값(approved|denied) 동기 — DN-014·contracts.py 정합, 공시**) + §20 표 20→**23키**(confidence 3행) — 946→**950줄**(+4)·CR 0 + docs\sot\CLAUDE.md byte 재복사 **SHA-256 683E959C 일치**(기승인 운영 규칙)
- ⚠️ **이형 발견 2건(기록 — SOT 무수정)**: ① PHASE_B4 §4.1 프리셋 `sinks=["file"]`+`[[logging.sinks]]` 동일 키 충돌(유효 TOML 불가) — V0 config는 PART2 V0 템플릿 표기 채택, B4 정비는 SOT edits 후보 ② CLAUDE.md §16 레지스트리 요약 수치(53+/20/13)는 P4-0 실측(123/36/23) 대비 stale — 본 세션 범위(§12/§20) 외, 차기 CLAUDE.md 정비 후보
- 📌 **P4-2 입력**: ① **pnpm 설치 필요**(실측 부재 — node v23.1.0 실재) ② src-tauri 스캐폴딩+serde 활성화(DEC-005 순연분 — generate_types.py serde 슬롯 NotImplemented 기존재) ③ JSON-RPC 13 메서드(PHASE_B1 §5.2 — [core] ipc_max_restart=3/ipc_timeout_s=30 기수록) ④ BLUE NODE 3 스켈레톤+Tauri 셸 ⑤ Ollama 실측 기완료(차단 0) ⑥ D2.1-D5 §4.9 ResponseEnvelopeSchema(9필드·metadata)는 IPC 직렬화 계층에서 활성(PHASE4-DEC-010 결정 1-4) ⑦ 백업 `_targets/_integ/backup_p4_1/`

## P4-0 결과 (2026-06-12) — Phase 4 진입 게이트: 환경·도구(A7) + 선행 결정 9건 + 4-1 타입 동기화
- ☑ **판정: PASS — P4-1 진입 허용** (수렴 선언: 적대 R1 6건 정정→R2 잔존 0→R3 1건 정정→R4 신규 0)
- ☑ **환경·EOL 게이트**: autocrlf=false 재확인 + `git ls-files --eol` 기준선 저장(`_targets/eol_baseline_p4-0.txt` — 이중 상태 683 실측) + sot CLAUDE.md SHA-256 루트 일치(45120F11, 재이격 0) + DEC-011 §4 재동기화 상시 규칙 release_strategy.md §1 집행 + `.gitattributes` 코드 확장자 EOL 규칙 추가(LFS 규칙 보존·추가만, 기존 추적 126파일 변경 0 — PHASE4-DEC-006)
- ☑ **도구 점검 PASS (A7)**: 검증 스킬 11/11(SKILL.md+엔진 py_compile) + **Hook 18/18**(Pre 6+Post 11+Stop 1 — 분모 실측, 경로 전건 실재) + 하네스(ruff 0.12.1 All passed·vamos_lint 0건·pytest·ci.yml YAML 유효·poetry 2.4.1) — **수리 2건**: check_config_lock.py·vamos_lint.py cp949 UnicodeEncodeError(utf-8 reconfigure)
- ☑ **선행 결정 9건 전건 단일 결론 + ADR(decisions/PHASE4-DEC-001~009) + 즉시 집행**:
  - ⑦ **(b) LangGraph V0 오케스트레이션 전용 예외 허용** — PART2 V0-STEP-4 정본 유지, PHASE3-DEC-004 구현 바인딩 1줄 보정(결정 본문 무변경·재정의 0), Must 11 라벨 무수정(분모 불변)
  - ⑧ **CostGate 병존 확정**: 게이트 [cost] warn_threshold=80/block_threshold=100(LOCK — check_config_lock.py D13 분모 기대값과 일치, DownshiftSchema D7 §4.4 명문) + 경보 alert_thresholds=[70,85,95](P30-058 비-LOCK 통지 전용) — PART2 템플릿 2곳+L1097+§6.12.8 주석+§7.5.1 연쇄 집행
  - ⑨ **DecisionSchema 18→20(16 required+4 optional)** + 신규 [confidence] 섹션 3키(V0 config 13→**14섹션**) — PART2 V0-STEP-2 연쇄 전건 집행(표 2곳·Stage Gate #2 len==20·FREEZE_SNAPSHOT·test 예시·약기 #3/#11/#12 SOT 정정·VamosConfig 14 서브모델·템플릿 [confidence] 2곳), PHASE_B4 §3.17 신설은 SOT 지시 등재
  - ⑩ V0 GO #15 = 코드 수준 L1(입력: extra=forbid+model_validate+non-goal deny)/L2(출력: ResponseEnvelope 검증+verify 노드) 등가 — [guardrails] 섹션 V1 유지
  - ⑪ D:\VAMOS 단일 repo 확정 + Phase 2 자산(backend/pyproject·tests·ci.yml·Hook 18) 승계 + **ci.yml 단일 통합 정본 재확인**(STEP-6 yml 2종 대체) + **src-tauri/serde = P4-2 순연** + PART2 STEP-1/6 reconcile 주석
  - ⑫ EOL: 일괄 정규화 불채택 — **자연 수렴(d5bc6e8 선례) + .gitattributes 코드 확장자 한정 LF 규칙**(집행 완료)
  - ⑬ Eval 스택(ragas·deepeval·minicheck) = **Phase 5 착수 시** poetry `eval` optional 그룹 등재
  - ⑭ 5-7a(Must) 전제 = **4-3 최소 서브셋(Tauri 셸 기동+Python spawn)만 한정 격상** — 로드맵 4-3·5-7a 행 명기, 분모 무변경
  - ⑮ seed=루트 `schemas/seed/` 확정·[core] ipc 2키(3/30) P4-1 포함·**VAMOS_DATA_DIR=.env.example 추가 집행**·config "17섹션" 라벨 정정 + ※ PART2 약기 테이블 SOT 이탈 발견(경고 주석+#3/#11/#12 교체 처분)
- ☑ **4-1 타입 동기화 (B2c·A20)**: `schemas/seed/` 5종(D2.1-D2·CLAUDE.md §12·D2.0-02 I-모듈 상세에서 **기계 추출, 창작 0** — scripts/extract_seeds.py 카운트 assert) + `backend/vamos_core/schemas/contracts.py` **25모델**(extra="forbid" 전건, 필드 수 SOT 실측 전건 일치) + `registries.py`(기계 생성 — EventType **123**/FailureCode **36**/Fallback **23**/Tool 2/Node 1) + `scripts/generate_types.py`(JSON Schema 25종+Zod TS 25종 자동 생성) + `config/schema_registry.toml`+검증 스크립트 → **왕복 테스트 25/25 PASS**(Python→JSON→TS[무의존 Node 검증기]→Python 동일성) + **pytest 61 passed**(필드 수·extra·레지스트리 분모·네이밍 VL-005) + seed↔contracts 교차 7/7 — serde(Rust)는 P4-2 활성화(PHASE4-DEC-005)
- ⚠️ **필드 분기 해소 기록**: IntentFrame/EvidencePack/StructuredOutput은 D2.0-02 초반 §7.3/7.13/7.33 요약(9/5/3 — timestamp·artifact_meta 누락 구판)과 후반 I-모듈 상세(10/6/4)가 병존 — **후반 상세 = 필드 정본 판정**(PART2 분모 10/6/4와 정확 일치, CLAUDE.md §12 IntentFrame 18 = 코어 10 + §11.12.1 V1 확장 8). seed에 판정 근거 기록
- ☑ **SOT 수정 ✅ 사용자 승인·집행 완료 (2026-06-12)**: `_targets/p4_0_sot_edits_pending.md` 집행 기록 — ①GATE-06 #4 MASTER_SPEC L78 "(= IMPLEMENTATION 계층)"(원문 "구현직접가이드" 기준) ②C-001 4곳(D2.0-01 L208·MASTER_SPEC L1512·BEGINNER L1376·**L1813 신규 발견분 포함**) 5-Gate 전체 열거 ③**PHASE_B4 §3.16 [confidence] 신설**(실측 17섹션의 다음 번호 — 초안 §3.17 정정)+§4.1 프리셋 동반. EOL 무회귀(MASTER_SPEC CRLF 1904 보존·잔여 LF) + integrity 신규 체크 `v13_integrity_check_20260612T230000.json` **CHANGED_AS_APPROVED**(승인 4+CLAUDE.md F1 기집행분 한정) = 새 참조 기준. ⚠️ MASTER_SPEC blob LF→CRLF 수렴(이중 상태 자연 수렴 — DEC-006 경로 공시). **추가 확인: B4 §3.7 정본 자체가 warn=80/block=100 — DEC-002 병존 설계와 정확 일치**
- ☑ 구키 revoke: 통보 미수신 유지(등재 트리거 유지·비차단) / CLAUDE.md §12 Decision 20필드·§20 분모 23 갱신은 4-5 바인딩(DEC-010 기확정 경로)
- 📌 **P4-1 입력**: ⑦ LangGraph(오케스트레이션 한정·Gate 우회 금지·StateGraph 중첩 금지) · ⑧ [cost] 80/100 LOCK+alert 3값 · **config 23키**(20+confidence 3, 14섹션) + [core] ipc_max_restart=3/ipc_timeout_s=30 · **DecisionSchema 20** · V0 실파일 8(GATE-03) · 백업 `_targets/_integ/backup_p4_0/`

## P4-PRE 결과 (2026-06-12) — 구현단계(Phase 4~8) 사전 전수 검증: 정확성(축A) + 부재 탐지(축B 5종)
- ☑ **판정: Phase 4 진입 가능(차단 0)** — 보고서 `_targets/구현단계_사전검증보고서_2026-06-12.md` (수렴 R4, 발견 전건 처분·미결 0)
- ☑ 축A: Phase 4~8 행↔PART2 재대조 + 게이트 3-way(16/22/14/12 분모 불일치 0) + Stage Gate 204 실측 일치(58/66/43/37) + Phase 3 산출물 소비 연결 전건 확인(고아 0)
- ⚠️ **HIGH 2건 → P4-0 등재**: ⑦ V0 파이프라인 프레임워크(DEC-004 "V0 LangGraph 미사용" ↔ PART2 V0-STEP-4 StateGraph 정본 코드·STRATEGY_02 Must 라벨 충돌) ⑧ CostGate 임계 2체계(DEC-005 80/100 LOCK vs config 템플릿 70/85/95 — 80/100 키 부재)
- ☑ [수정] 11건 집행(백업 `_targets/_integ/backup_p4pre/`·EOL 무회귀 실측): 로드맵 Phase 3 stale 5곳 현행화 + Phase 5 게이트 비대칭 노트 + **6-0 V1 착수 게이트(P6-0) 행 신설**(B.2 12건 준비+GATE-06/07 배정분 착지)+Critical Path + Phase 7~8 실패 시(A1) 준용 노트 / PART2 `[mcp] max_retries` 3→2 정정(L312·L488, GATE-07d — V3 키 보존, CRLF 6454 보존)
- ☑ P4-0 신규 입력 ⑨~⑮: confidence 3키 PART2 동기(DEC-010) · V0 GO #15 Guardrails 충족 수단 · 저장소/스캐폴딩 방침(D:\VAMOS 단일 repo·Phase 2 자산 승계·ci.yml reconcile) · .gitattributes EOL 규칙(현행 LFS 전용 — 보존 필수) · Eval 스택 의존성(ragas·deepeval·minicheck 정의처 0) · 5-7a(Must)→4-3(Should) 의존 명시 · 미세 4건(seed 경로·ipc_* 키·VAMOS_DATA_DIR·config 라벨)
- ☑ 이연 등재: P6-0(V1→V2 TC 비용 기준 ₩93,000 모순 의심·READINESS enum drift·TC 측정 도구 6종 생산처·/health vs stdio·운영 결정 4건) / P7-0(V2 도메인/TLS 미정의) / P8-0(READINESS 전환조건 표기·PART1 B.4 Hetzner/RunPod 미반영) · 의도적 부재 3건 기록(updater·LICENSE·READINESS 실패절차)
- ℹ️ git blob EOL: PART2 blob이 d5bc6e8에서 디스크 진실(CRLF)로 정합화(디스크 무변경·내용 diff 2줄 실측 — 이중 상태 684→683, 잔여 정규화 결정은 P4-0 유지. 보고서 §6 공시)

## Phase 3 교차감사 최종 확정 (2026-06-12)
- 3-AI 독립 감사: Fable 5 max **CONFIRM/GO**(C0/M0/m1) · Opus 4.8 max CONDITIONAL(C0/M1) · GPT 5.5 CONDITIONAL(C0/m1, 증거팩 한정) — **CRITICAL 0·silent drop 0·fabrication 0 공통**, 디스크 감사관 실측 상호 일치(인용 10/10 verbatim·LOCK 순수 추가만·EOL diff 0)
- 수합(다수결 금지·증거 우선): finding 전수 재실측 — **F1 스냅샷 재이격 1줄 즉시 해소**(루트→sot 재복사 SHA 45120F11 일치) + **F2 헤더 날짜 해소**(946줄·CR 0 무회귀) + F3 □=기존 컨벤션 NO_FIX + F4 STRATEGY_08 "26"=GATE-03 기처분 유지 + F5 GPT UNVERIFIABLE 전건 원문 일치 해소 → **실효 CONFIRM 3/3, PHASE4_ENTRY=GO**
- 권고(P4-0): Phase 종결 커밋 후 sot CLAUDE.md 재동기화 1줄 추가(구조적 재발 방지) — PHASE3-DEC-011 §4

## P3-2 결과 (2026-06-12) — X1 횡단 전략 + 계획서 + Phase 3 Gate
- ☑ **산출물 6종** (전부 `VAMOS Engineering/` 직하, 위상 = 결정 요약+바인딩·정본 무대체):
  - 3-8 `security_strategy.md` — 7불변×3계층 강제 + Permission Matrix(sot2 3-10 LOCK-AP-02) + 감사로그 해시체인 + A16 체크리스트 + A21 검증
  - 3-9 `test_strategy.md` — 피라미드(단위 80%/통합 60%/E2E 100%, PHASE_B5 추인) + R1 10결정 연계 테스트
  - 3-10 `release_strategy.md` — Git 브랜치(GATE-08 ff-only) + SemVer + Expand/Contract(A23, config 분모 20→23 Expand)
  - 3-11 `doc_strategy.md` — 코드/설계/ADR 주체 + VAMOS HOME 124노트 갱신 규칙
  - 3-12 `runtime_eng_plan.md` — R1 10결정 → R2a/R2b/R2c/R3/RF 매핑(V0=8/V1=32 분모 반영)
  - 3-13 `cross_eng_plan.md` — X1 4전략 → X2/X3/XF + Phase 2 하네스 정합
- ☑ **3-V Gate 전항목 PASS**: R1 10결정 SOT 정합 / LOCK Registry 일치+신규 3건(§8) / A20 Pydantic 정본·자동생성·수동금지(DEC-006) / A21 3계층 독립(DEC-008) / A22 reasoning_trace 스키마(DEC-009) / A25 confidence+임계값 LOCK(DEC-010) / A16 체크리스트(security §4) / 회귀 CLAUDE.md §5 모순 0
- ☑ **Phase 3→4 인수인계**: runtime_decisions.md→R2a / IPC+A20→B2c / 4전략→X2 (전건 ☑)
- ☑ 회고 `decisions/phase3_retro.md` (잘된 3/안된 3/바꿀 1 + autocrlf 포스트모템) · git tag **phase3-complete**

## P3-1 결과 (2026-06-12) — R1 런타임 설계 10개 결정 확정
- ☑ **산출물**: `VAMOS Engineering/runtime_decisions.md` 신설(결정 요약+로드맵 바인딩 — 기존 정본 비대체, 위상 L293 준수) + ADR 10건 `decisions/PHASE3-DEC-001~010`(A6)
- ☑ 3-1 5-Gate 순서: **Policy→Approval→Cost→Evidence→SelfCheck** (D2.0-07 L969 — STRATEGY_05 §3.1 순서 오기 교정 동반)
- ☑ 3-2 메모리 L0~L3: 계층·TTL·승격(L0→L1 자동/L1→L2 3회∨QoD≥0.7/L2→L3 크로스)·강등(pinned 제외)·B↔L 매핑 (D2.0-06 추인)
- ☑ 3-3 Failover: GPT-4o→Claude Sonnet→Ollama, 연속 3회 타임아웃∨5xx (D2.0-02 §11.1.2 LOCK 추인)
- ☑ 3-4 DAG: 9-State S0~S8 + S3 결론불변 + Soft loop 1회 + V1 자체 경량 프레임워크 기본·LangGraph 어댑터 한정 (D2.0-02 §2.2+D2.0-05 — 정정된 정본 매핑 사용)
- ☑ 3-5 CostGate: 80% force_mini / 100% deny(LOCK 변경불가) (D2.0-07 §4.2 추인)
- ☑ 3-6 IPC: JSON-RPC 2.0 subprocess + 13 메서드(PHASE_B1 §5.2 전수) + A20(Pydantic 단일 정본·자동 생성·왕복 테스트·4파일 동시 커밋)
- ☑ 3-7 MCP: Streamable HTTP(DEC-017) + max_retries V1/V2=2·V3=3(GATE-07d 준수)
- ☑ 3-7a A21: Defense Layer 3계층 독립(config LOCK/5-Gate/NEVER_AUTO 10 frozenset) — PART2 Security Layer와 별개 명기
- ☑ 3-7b A22: D6 틀 내 metadata 스키마 상세(reasoning_trace/evidence_sources/confidence_score/disclaimer — top-level 불변)
- ☑ 3-7c A25: Decision confidence_score+level 신규 + 임계값 0.85/0.60/0.30 LOCK(config 신규 3키 — 분모 20→23 V0 집행) + REFUSE 분기
- ☑ **LOCK**: 기존 재정의 0 · 신규 3건 등록(LOCK-DECISION-REGISTRY §8: R1-A25/R1-A21/R1-A22) · 회귀 CLAUDE.md §5 모순 0

## Phase 3-0 미결정 게이트 결과 (2026-06-12) — 게이트 통과 선언
- ☑ ① D1 이연 대장 D-1~D-4: 전건 종결/기록-전용 재확인 — 실효 OPEN 0 (GATE-01)
- ☑ ② PART1 C.1 13건: #1~3 기결정 확인(pnpm/Poetry/CUDA) + #4~13 전건 권장안 채택 확정 (GATE-02; #10 일반 API 3회 — MCP 채널은 별도 정본)
- ☑ ③ 분모 3건 확정: **V0 실파일 8개**(전 25 선생성 안 함, 활성5+stub3) · **V1 CORE 32**(PART2 §1.1) · **Phase 4→5 Must 11** (GATE-03 — 로드맵 4-2/5-3/6-3 확정 반영)
- ☑ ④ V1 귀속 4건 **전부 V2 이연**(SDAR §10.1·CB1 E-15/S-5·RT-BNP 본체·4-4 MLOps 본대 — P7-0 수용, F-18 해소; D11 #10/#11은 조건부 해석으로 Phase 7 집행. PART2 L2549 CONFLICT 마커 확정 갱신) (GATE-04)
- ☑ ⑤ STEP7 reconcile 방침: PART2 배치 = 구현 시점 정본, STEP7 V1 라벨 = 카탈로그 라벨 — V1 GO 분모는 PART2 V1 스코프 (GATE-05)
- ☑ ⑥ READINESS §8 38건 분류: 기집행/실효 22 + supersede 3(#5=D10·#16/#17=PL-09) + 잔여 13 — 책임 게이트 배정(P4-0 1건: MASTER_SPEC §0 IMPLEMENTATION 계층 / P6-0 5건 / P7-0 9건), **R1 차단 0** (GATE-06)
- ☑ ⑦ Phase 2 이관 4항목 (GATE-07, **SOT 물리 수정 0건**): a.SOT 이형 9건 — NO_FIX 2(C-003·C-008)+운영확정·DEFER 1(C-004→P8-0)+수정 지시 6(edits 명기, P4-0/P6-0/P7-0 배정) b.docs\sot\CLAUDE.md 스냅샷(709줄 구판) → **루트 946줄 GOLD로 동기화 — ✅ 집행 완료(2026-06-12 사용자 승인, SHA 일치·CR 0·946줄, 백업 backup_phase3, integrity 신규 체크 20260612T175049 = 새 참조 기준)** c.5-4 SHELL 87 = V2+ 확정, P7-0 수용(작성 0 유지) d.LOCK-MCP-06 단일 표기 = **config 정본 PHASE_B4 §3.9 V1/V2=2·V3=3**(LOCK-MCP-06은 Bridge 구현 상한으로 무수정 보존·재정의 0, V3 근거 보강은 P8-0)
- ⚠️ **git EOL 사건·복구 (2026-06-12, GATE-07 집행 기록 참조)**: main ff 체크아웃 왕복 × autocrlf=true가 824파일 작업트리를 CRLF로 재작성 → 역사적 EOL 기계판정(06-04 해시↔blob 양방 대조+backup_session5) 후 LF군 725 복원·CRLF군 27 무손상 확인·교차검증 PASS(1-1 상세명세 3AE9E739)·blob 무변화(diff 0). **재발 방지: repo-local autocrlf=false 설정 + 브랜치 체크아웃 금지(main 동기화는 `git fetch . <branch>:main`)** — CRLF-디스크/LF-blob 이중 상태 ~684파일의 정규화 여부는 P4-0 결정 후보
- ☑ ⑧ 감사 권고 2건 (GATE-08): 구키 revoke — 통보 미수신 유지(등재 트리거 유지) / main 병합 정책 **확정** — Phase 게이트마다 ff-only 동기화+push (실측 main 29 후행·분기 0)
- ☑ ⑨ 문서 동기 3건: 세션 프롬프트 §8 추적표 P2-0~P2-5·P3-0 ✅ 갱신 + §4 P3-0 보정판 반영 + P3-2 파일명 교정 (EOL 무회귀: 로드맵 LF·PART2 CRLF 6454 보존)
- ☑ ⑩ ADR 8건: decisions/PHASE3-GATE-01~08 (PHASE3-DEC-001~010은 P3-1 예약 — 충돌 없음. 기존 17건은 _targets/DECISION_REGISTER.md 정본 유지)

## Phase 2 검증 결과 (2-V) — 전항목 ☑
- ☑ CLAUDE.md 보강 완료 — 946줄 §1~§28, §28에 A13 컨텍스트 프로토콜 포함, **GOLD 판정**
- ☑ 린터: ruff 13룰 PART2 일치 + vamos_lint VL-001~005 동작(위반 샘플 전탐지·오탐 0)
- ☑ CI: ci.yml 단일 통합(PHASE_B6 §2 정본 중재) — quality/test/vamos-lint 3 job, YAML 유효
- ☑ 외부 의존성 E.1(9)+E.3(8) PASS (+B.1 11 — 합 28/28)
- ☑ 회귀: /sot-check method-c 재실행 — **12/12 PRESENT, GAP 0** (D1 baseline 10/12 → 보강으로 해소, D1 산출물·SOT 무수정)
- ☑ Obsidian 124노트 + A16 responsible-ai 태깅 9노트 (깨진 링크 0/1,289 · 샘플 12표본 수치 전수 일치)
- ☑ (추가 게이트) 골든셋 data_status REAL_DATA 전환 + LOCK-BE-01/02 유효화

## Phase 2→3 인수인계 — ☑
- ☑ 보강된 CLAUDE.md(946줄 GOLD) → Phase 3 AI 컨텍스트 활성화 (자동 로딩 + §21 라우팅 + §28 프레임워크)
- ☑ 린터/CI(ruff·vamos_lint·pytest·ci.yml) + Hook 18 → Phase 4 자동 실행 준비 완료
- ☑ Obsidian Vault(124) + CPS_TEMPLATE + CONTEXT_LOADING_MAP → Phase 3~4 설계 참조·세션 골격
- 📌 3-0 게이트 추가 이관: SOT 내부 이형 9건(step1 C-001~C-008 등) + docs\sot\CLAUDE.md 스냅샷 동기화 + 5-4 SHELL 87(PHASE2-DEC-02) + LOCK-MCP-06(3회) vs PHASE_B4(V1/V2=2·V3=3) 표기 뉘앙스 1건 — **✅ 4항목 전건 처분 완료 (2026-06-12, PHASE3-GATE-07 — 상기 Phase 3-0 결과 ⑦ 참조)**

## Phase 2 체크포인트 (2026-06-11)
- [x] **2-0A** 외부 의존성 재확인: E.1(9)+E.3(8)+B.1(11) = **28/28 PASS** — `_targets/PHASE2_환경리포트.md` (변경 2 비차단: pydantic 2.12.5·디스크 / WARN 1: poetry 미설치→2-4 처리)
- [x] **2-0B** 골든셋 실데이터 재구축(D14): v1 합성 170 → **v2 실데이터 162** (MMLU 50/HumanEval 20/MBPP 50/LogicKor 42 전수[편차 기록 — 명세 50은 합성 가정치]). 라이선스 4종 검증(MIT/MIT/CC BY 4.0/CC BY-SA 4.0). verify ALL PASS + 재현성 PASS. data_status=REAL_DATA → **LOCK-BE-01/02 유효화**. v1 백업 `_targets/_integ/backup_phase2/golden_set_v1/`
- [x] **2-0C** OpenAI 구키 revoke: 사용자 통보 미수신 — 기록만(현행 키 HTTP 200 유효). 환경리포트 §5
- [x] **2-1** CLAUDE.md 보강: 705→944줄(LF 무회귀), §21~§28 신설 + §2/§4/§6/§7.4/§17/§18 실측 갱신. GAP 2건 해소(§7.4: Hybrid Search BM25 0.3/Vector 0.7·Top-K 20·threshold 0.75 + MCP max_retries V1/V2=2·V3=3 [PHASE_B4 §3.9 정본]). §28에 A13 컨텍스트 테이블 포함. 백업 `_targets/_integ/backup_phase2/CLAUDE.md.pre-2-1`
- [x] **2-2** CLAUDE.md 검증: 스킬 8종 신설(.claude/skills/claude-md-*) + 8단계 전수 실행 + Phase D 수정 10건(944→946줄, LF 무회귀) → **판정 GOLD** (UNVERIFIED 0·FAIL 0·누락 0; Symbolic 9/9·Cross-examine 91건·Consensus 50값×3라운드 값충돌 0). 회귀(R10): method-c 재실행 **12/12 PRESENT GAP 0**(비파괴 — D1 산출물·SOT 무수정). 리포트 `04. 구현단계/claude-md-verification/step1~8`. ⚠️ SOT 내부 이형 9건(C-001~C-008 등) 발견 — 기록만, **3-0 게이트 이관**
- [x] **2-3 Obsidian 노트 — 완료 (2026-06-12)**: Vault **124 .md** (17폴더 전부 목표 충족 — 도메인 35+AINV 4+설계 12+개념 36+워크플로우 3+구현 13+가이드 4+감사 3+규칙 4+RAW 1+HUB 7). 검증: **깨진 [[wikilink]] 0** (1,289링크/124노트, 코드펜스 제외 기준) · 36 도메인 전부 커버(3-7 gap 도메인 포함) · **A16 responsible-ai 태그 9노트**(요구 7+) · 샘플 10%(12표본) SOT2 대조 — 수치/LOCK **12/12 일치·창작 0·LOCK 레지스트리 모순 0** (형식 태그 3건 보정 완료). 2026-06-11 중단분(43) + 재개분(71+10) 합산
- [x] **2-4** 린터/CI: `backend/pyproject.toml`(Poetry+DEC-002 banned-api+ruff 13룰+line-length 100+mypy strict) + `.github/workflows/ci.yml`(**단일 통합 정본** — quality/test/vamos-lint 3 job) + `backend/tests/{__init__,conftest}.py`. 검증: poetry lock 해석 정상·ruff All checks passed·pytest 0 tests(exit 5 OK)·YAML 유효. **코드 생산 Hook 2종 신설**(.py→ruff 자동, config.v1.toml→LOCK 20키 검증 `scripts/check_config_lock.py`) — 기존 16 Hook 보존(16→18). **D17 결정**: pre-commit 훅 불재도입(ci.yml 대체) — `decisions/PHASE2-DEC-01`. poetry 2.4.1/ruff 0.12.1 설치(2-0A WARN 해소)
- [x] **2-5** vamos_lint: `scripts/vamos_lint.py` VL-001~005 구현 — 위반 샘플 8건 전 규칙 탐지 PASS·정상 파일 오탐 0 (mode=error 기본, warn 폴백 내장). ruff banned-api(§8.1)는 pyproject 포함, ci.yml vamos-lint job 통합(§8.3). `commitlint.config.js` 별도 생성
- [x] **2-6** CPS 템플릿: `VAMOS Engineering/CPS_TEMPLATE.md` / **2-7** 로딩 맵: `VAMOS Engineering/CONTEXT_LOADING_MAP.md`
- [x] **2-8 완료 (2026-06-12)**: **D-2 종결(보수)** — 04_cat-d-media/_index.md 링크 교정(백업·LF 보존) / **D-3 종결(보완 불요)** — AUTHORITY 6/6+MASTER_INDEX+§21 라우팅 충족 / **유산 이동 집행** — back up(git 언트래킹 1)+.claude-pre-commit → `D:\VAMOS_ARCHIVE\legacy_phase2\`(42파일, 삭제 0) / **5-4 SHELL 87 → 3-0 이연 확정**(`decisions/PHASE2-DEC-02`) / **STRATEGY_11 §2.13 신설**(Phase 2 자산 16종 등재)+§5.2 집행 기록+골든셋 v2 반영
- [x] 2-V Gate + 마감(회고·tag phase2-complete·push·A12 대조) — 완료 (2026-06-12, 상기 2-V 전항목 ☑)
- [x] **교차감사 최종 확정 (2026-06-12)**: 3-AI 독립 감사 — Fable 5 max **CONFIRM/GO**·Opus 4.8 max **CONFIRM/GO**(디스크 실측, 실측값 상호 일치)·GPT 5.5 CONDITIONAL(증거팩 미포함 구조 한계, 허위·충돌 0) → UNVERIFIABLE 12항목 **전수 디스크 재실측 해소**(다수결 아닌 증거 우선 규칙). CRITICAL/MAJOR 0(실효)·silent drop 0(3감사 공통)·원격 태그 `ls-remote` 확인. MINOR 정리: CLAUDE.md §28.4 stale 갱신(F-01, 946줄 유지)+로드맵 L40 LOCK-MCP-06 열거 보완(F-02). 기록 `decisions/PHASE2-DEC-03_교차감사_최종확정.md`

## Phase 1 — D1 검증 결과 (2026-06-04)
- **판정: D1 PASS (CONDITIONAL)** — 값 게이트 5/5 통과, 이연 4항목 전수 등록(누락 0), 자동 정본 변경 0
- 인덱스: `04. 구현단계/v13_results/phase0/D1_RESULTS_INDEX.md` + 머신 판정서 `D1_VERDICT.json`
- Must 게이트:
  - 1-2 SOT 내부 정합: CONFLICT active 0 (14건 발견·전부 RESOLVED, v13 verdict) — `sot_conflict_report.json`
  - 1-3 SOT↔SOT2 교차: MISMATCH 0 — `docs/sot 2/_cross-ref/sot2_conflict_scan.json`(+alias `sot2_crossref_report.json`)
  - 1-4 SOT2 내부 교차: LOCK MISMATCH 0 · BROKEN(설계) 1(사소 네비, 이연) — `cross_ref_matrix.md`/`lock_consistency.md`/`broken_references.md`/`sot2_internal_report.json`/`{도메인}.json×36`
  - 1-5 구조+LOCK: SDV-1 critical 0 FAIL(36/36) · SDV-4 LOCK WARN 1(5-3 비차단 이연; 6-5는 RESOLVED) · SDV-7 0 — `_sot2_validate_summary.json`(+alias `sot2_validate_report.json`)/`{도메인}_validation.json×36`
  - 1-9 기준선: `integrity/integrity_snapshot.json` (2,654 파일 SHA-256, D2 기준선) + `integrity/v13_integrity_check_*.json`(SOT68 67 OK/1 CHANGED)
- Should (비차단, 후속 입력):
  - 1-6 CLAUDE.md GAP 2건(HYBRID_RATIO, MAX_RETRIES) → Phase 2-1 입력 — `extraction/sot_check/claude_md_gap_report.json`
  - 1-7 Obsidian 미참조 1 도메인 → Phase 2-3 입력 — `extraction/sot_check/obsidian_gap_report.json`
  - 1-8 PART1 BLOCKER 14건 baseline · 변경 0 — `extraction/sot_check/blocker_log.json`
- 이연 대장(자동 정본 변경 0, **4항목**): D-1 5-3 C-04~C-08(5건) / D-2 2-2 네비링크 / D-3 INDEX 부재 6도메인 / D-4 readiness 문서 변경 — D1_RESULTS_INDEX.md §3
- 진짜 현행 OPEN 충돌 = 5건(전부 5-3). **6-5 W-CB는 RESOLVED**(CONFLICT_LOG v1.3 §8.1 OPEN 0 — 1차 D1의 6-5 이연은 2026-06-05 감사로 정정 제거)
- git tag: `phase1-d1-pass`
- **2026-06-05 감사 정정**(게이트 불변): OPEN 6→5(5-3 C-07 복구+6-5 stale 제거)·SDV-4 WARN 2→1·EXTERNAL 6→4·1-2 RESOLVED 11/NO_FIX 1/DEFERRED 2. 엔진 3종 정정. 상세 D1_VERDICT.json `audit_corrections_2026_06_05`

## 완료 항목
- Phase 0 (2026-04-04): 자산 인벤토리 + 매트릭스 v1.1 + 리스크 15건 + 0-V 전항목 PASS + git tag phase0-complete
  - **2026-06-05 정정**: 미커밋이던 Phase 0 산출물(STRATEGY_01~11+P0-2/P0-4+phase0_retro)을 소급 커밋(`1d52614`)하고 phase0-complete 태그를 AI-Investing 오지정(0d49b6c)→`1d52614`로 재지정 완료(ultracode 재검증 F-D2-01/02 해소)
  - P0-2 CLAUDE.md 구조 명세 / Obsidian-매트릭스 매핑 / 설계 자산 맵
  - P0-4 5개 계획서 목차 / STRATEGY_09 하네스 역참조 / phase0_retro.md
- Phase 1 SOT 2 콘텐츠 (2026-06-03): 30/30 도메인 Phase 0~4 전 단계 genuine 완료 (`SOT2_MASTER_INDEX.md` ALL_PHASES_ALL_DOMAINS_COMPLETE)
- Phase 1 D1 검증 (2026-06-04): 위 결과 — **D1 PASS_CONDITIONAL**

## Phase 1 검증 결과 (1-V)
- ☑ CONFLICT 0건 (active) — /sot-conflict scan (14 RESOLVED)
- ☑ MISMATCH 0건 — /sot-conflict sot2-vs-sot
- ☑ SOT 2 교차참조 무결 (LOCK MISMATCH 0; BROKEN 1 사소·이연)
- ☑ integrity_snapshot.json 저장 완료 (2,654 파일)
- ☑ 재현성 메타데이터(timestamp, input_hash, skill_version) 전 산출물 기록
- ⚠️ SDV-4 LOCK WARN 1 (5-3 C-04~C-08) — 비차단 이연 등록(D1_RESULTS_INDEX §3). 6-5는 RESOLVED

## 다음 작업
**P6-0 — Phase 6 (V1 구현) 진입 게이트** (Phase 5 ✅ 완료·V0 GO, tag v0-release)
→ 입력: **상단 P5-1 결과 "P6-0 입력" ①~⑤** (V0 GO 완료·tag v0-release / §C I-1~I-9 전건 재확인[신규 테스트도구·CI job = DEC-014+ ADR 선행] / V1 활성화: Chroma 벡터·RAG(I-2)·graph_db·Alembic·24규칙 잔여·I-4·NeMo/Guardrails-AI / II-6 교차모델 복구[6-9 게이트] / Eval QoD≥0.85 V1 RAG) + PHASE5-DEC-001(스코프환원 6건) + DEC-011 §B/§E(게이트=ultracode 교차모델, GPT/Gemini 우선·불가시 인간)
→ ⚠️ 분모 라벨 정정: V0 GO/NO-GO 16건 디스크 검증원 = **READINESS §2.8**(상기 L196 'PART2 §7.1'은 부정확 — PART2 §7.1은 IntentFrame/I-모듈 상세). PHASE5-DEC-001 참조.
→ 매 커밋 하네스: 코드 생성 → ruff → vamos_lint → pytest → PASS → 커밋 / A20 왕복은 Rust serde 컴파일 검증 동반(DEC-005)
→ 잔여(비차단): ~~SOT edits 승인 대기~~ → **✅ 집행 완료(2026-06-12)** / 차기 CLAUDE.md 정비 후보(§16 레지스트리 수치 53+/20/13 → 실측 123/36/23) / B4 §4.1 sinks TOML 키 충돌(SOT edits 후보) / P6-0(5건+이형 3건+A-06 등) / P7-0(9건+이형 2건+5-4 SHELL 87) / P8-0(C-004 V3 근거) / 구키 revoke(사용자)

## 참조 파일
- 04. 구현단계/v13_results/phase0/D1_RESULTS_INDEX.md (D1 산출물 인덱스 + 게이트 + 이연대장)
- 04. 구현단계/v13_results/phase0/D1_VERDICT.json (머신 판정서)
- VAMOS_최종_로드맵.md Phase 1~2 섹션
- STRATEGY_11_ASSET_INVENTORY.md / STRATEGY_08_ENGINEERING_MATRIX.md v1.1
- decisions/phase1_retro.md (Phase 1 회고)

## 리스크 메모
- 이연 4항목(D-1~D-4)은 LOCK 값 충돌 아님·비차단. 5-3 C-04~C-08(5건)은 Phase 2/3 협의 시 정본 우선순위로 해소 예정 (자동 변경 금지). 6-5 W-CB는 v1.3에서 이미 RESOLVED.
- SOT 1건(readiness review 문서) 2026-03-27 baseline 대비 변경 — 신규 snapshot이 새 D2 기준선.
- hooks/skills 수 변동 → Phase 4 전 건강 검진 필요 (R14).
