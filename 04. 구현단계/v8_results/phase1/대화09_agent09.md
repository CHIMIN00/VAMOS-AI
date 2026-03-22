# [Agent 9] 검증 결과 — 의사결정 + 비용 + LLM 모델

> **검증 일시**: 2026-03-05
> **PART2 버전**: v18.0.0 (1933행)
> **Phase 0 참조**: 0-D.json (LOCK/FREEZE 80 entries)

## 읽은 파일 (실제/할당: 9/10)

- [x] VAMOS_구현가이드_PART2_구현단계.md (1933행) — 전수 열독 (§1~§7, config.v1.toml, §3 V1-Phase 1~6, §6.4 CI/CD, §6.8 AI Investing)
- [x] CLAUDE.md (672행) — 전수 열독 (§7 LOCK 결정사항, §20 config.v1.toml LOCK 값)
- [x] D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md (부분, ~2500행 중 주요 섹션) — §4 비용 상한/다운시프트 전수 열독
- [x] D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md (100행) — §0~§1 CostGate UI 참조 확인
- [x] PHASE_B_EXHAUSTIVE_ANALYSIS.md (1800행) — 전수 열독 (Category D: Config, J: LOCK 항목)
- [x] 0-D.json (571행) — 전수 열독 (LOCK/FREEZE 80 entries)
- [x] D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md — DSPy V2 항목 확인 (:717 EXP/V3:ON, :1647 SOT 참조)
- [x] D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md — approval_status(:543), Agent-Level LLM(:4214), Multi-Brain Failover(:3880) 확인
- [x] D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md — QoD 스코어링(:795 qod_min:0.7, :363 evidence_summary, :679 Verify) 확인
- [ ] PHASE_B4 (단독 파일) — 미열독 (PHASE_B_EXHAUSTIVE_ANALYSIS.md의 B4 추출본으로 대체)

> ※ D2.0-01, D2.0-02, D2.0-05는 초회 검증 시 `C:\tmp\output\updated\` 경로에 미존재. OneDrive 경로에서 확인하여 추가 검증 완료.

## 검사 통계

- **수정 전**: Dim B = MATCH 8 / MISMATCH 3 / NO_SOURCE 1 / MISSING 1 / 검증불가 2, SC 미분리
- **수정 후**: Forward **15** / MATCH **10** / MISMATCH **4** / NO_SOURCE **1** / Reverse MISSING **3** (총 **18** 체크) + SC **2건** 별도
- Dim C: **21** / IMP_OK **12** / IMP_IMPOSSIBLE **1** / IMP_MISSING **5** / IMP_CONFLICT **3**

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MISMATCH

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|---------|---------|--------|----------|----------|
| 1 | :157 | `matryoshka_dim = 256` | `matryoshka_dim = 512` | PHASE_B4 (PHASE_B_EXHAUSTIVE_ANALYSIS:966) | **HIGH** |
| 2 | :113~169 | config.v1.toml 내 섹션 수 = **10개** ([general], [llm], [cost], [storage], [mcp], [safety], [self_check], [embedding], [graph_db], [vector_db]) | config 섹션 수 = **13개** ([core], [llm], [embedding], [vector_db], [graph_db], [storage], [cost], [guardrails], [mcp], [rbac], [rate_limit], [logging], [semantic_cache]) | PHASE_B4 (PHASE_B_EXHAUSTIVE_ANALYSIS:937~1095, v8 §1.5 V7-1 확인) | **BLOCKER** |
| 3 | :121~122 | `default_model = "ollama:llama3.2:3b"`, `main_model = "ollama:llama3.1:8b"` | `mini_model = "ollama/gemma-2b"`, `main_model = "gpt-4o-mini"` | PHASE_B4 (PHASE_B_EXHAUSTIVE_ANALYSIS:952~953) | **HIGH** |
| 4 | :1084 | Agent-Level LLM: "Sonnet(Lead)/Haiku(Sub)" | V1 기본: "GPT-4o 한국어 (API) / SOLAR 10.7B (로컬)", classifier/summary: "front_mini" | D2.0-02:4214, D2.0-02:254 | **MEDIUM** |

**상세 분석**:

**#1**: PART2 §2 V0-STEP-1 config.v1.toml에서 `matryoshka_dim = 256`으로 기재하나, PHASE_B4 원본은 `matryoshka_dim = 512`로 기재. 수치가 2배 차이나며, 임베딩 검색 성능에 직접 영향.

**#2**: PART2의 config.v1.toml은 10개 섹션만 포함. PHASE_B4 정본은 13개 섹션. 누락된 3개: [guardrails], [rate_limit], [logging]/[semantic_cache] 등. v8 문서 §1.5 V7-1에서도 "11섹션→13섹션(B4 §3 정본)" 갱신을 명시. PART2는 [general]+[safety]+[self_check] 등 B4와 다른 명명도 사용. 구현 시 config 파일 불일치로 LOCK 값 누락 발생 가능.

**#3**: PART2의 V0 config에서 LLM 모델명이 `ollama:llama3.2:3b` / `ollama:llama3.1:8b`이나, PHASE_B4 정본은 `ollama/gemma-2b` / `gpt-4o-mini`. 모델명 형식도 다름(콜론 vs 슬래시). CLAUDE.md §11에는 "V1: Ollama + GPT-4o mini"로 기재. PART2의 llama3 계열은 V0 로컬용이므로 의도된 차이일 수 있으나, B4 정본과 명시적 불일치.

**#4**: PART2에서 Agent-Level LLM을 Sonnet(Lead)/Haiku(Sub)로 기재하나, D2.0-02:4214에서는 V1 기본 모델로 "GPT-4o 한국어 (API) / 로컬은 SOLAR 10.7B"를 정의하고 :254에서 classifier/summary에 "front_mini"를 할당. 버전별 모델 정책 차이일 수 있으나 D2.0-02(SRC 정본)와 직접 불일치.

---

## Dim B — NO_SOURCE

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | Severity | 판정 |
|---|---------|-----------|---------------|----------|------|
| 1 | :58 | V0 비용 "테스트용 (~₩5,000)" | CLAUDE.md §7.3 (V0 비용 미정의), PHASE_B4 [cost] (V1 daily_limit=1300만 기재) | **MEDIUM** | NO_SOURCE — CLAUDE.md §20에 V0 비용 관련 키 없음. CLAUDE.md §9 미해소이슈 V0-001에서 "V0 비용 상한 미정의 → V1 동일 적용" 명시. ₩5,000이라는 수치의 출처 불명 |

---

## Dim B — MISSING (역방향)

| # | 구분 | 원본 출처 | 누락 내용 | Severity |
|---|------|---------|---------|----------|
| 1 | 역방향 | CLAUDE.md §20:668 | `cost.warn_threshold = 80` / `cost.block_threshold = 100` — PART2 config.v1.toml에는 `warn_threshold_pct`/`block_threshold_pct`로 키명이 다름 (변수명 불일치) | **MEDIUM** |
| 2 | 역방향 | CLAUDE.md §20:670~672 | `semantic_cache.similarity_threshold = 0.95`, `logging.trace_id_required = true`, `mcp.transport = streamable_http` — PART2 config.v1.toml에 [semantic_cache], [logging] 섹션 자체가 부재 | **HIGH** (MISMATCH #2와 동일 근인) |
| 3 | 역방향 | PHASE_B4 (PHASE_B_EXHAUSTIVE_ANALYSIS:1017) | `downshift_model = "ollama/gemma-2b"` — PART2 config.v1.toml에 downshift_model 키 미기재 | **MEDIUM** |

---

## Dim B — SOURCE_CONFLICT

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|-----------------|
| 1 | CLAUDE.md §7.2:213 = "Multi-Brain Failover: GPT-4o→Claude→Ollama (3회 타임아웃 시 전환)" + D2.0-02:3880 = "GPT-4o (주) → Claude Sonnet (1차 대체) → Ollama (2차 대체), 연속 3회 타임아웃" | PART2:497 = "A-1 MultiBrain Adapter: Ollama + GPT-4o-mini 통합 인터페이스" (순서/모델 불일치) | CLAUDE.md + D2.0-02 일치 (Failover LOCK). PART2는 V1 구현 관점 기술이나, 정본 순서(GPT-4o→Claude→Ollama)를 명시해야 함. **Severity: MEDIUM** |
| 2 | D2.0-02:543 = "approval_status: approved \| denied \| pending (07 §6.2 + pending 확장, 3값)" | D2.1-D7 §6.2 / PART2:1758 = "SOT=2개(approved/denied)" | D2.1-D7이 SOT로 채택됨 (PART2 주석 기재). pending은 D2.0-02의 확장 값. PART2 기재가 정본 우선순위에 따라 정합하나, D2.0-02의 pending 미반영 가능성 주의. **Severity: MEDIUM** |

---

## Dim B — MATCH 확인

| # | 항목 | PART2 값 | SRC 값 | 판정 |
|---|------|---------|--------|------|
| 1 | 비용 상한 V1 | ₩40,000/월, ₩1,300/일 | CLAUDE.md §20:666~667, D2.0-07 §4.1:612 동일 | MATCH |
| 2 | 비용 상한 V2 | ₩93,000/월 | CLAUDE.md §7.3:222, D2.0-07 §4.1:613 동일 | MATCH |
| 3 | 비용 상한 V3 | ₩266,000/월 | CLAUDE.md §7.3:223, D2.0-07 §4.1:614 동일 | MATCH |
| 4 | 다운시프트 임계값 | 80% 경고/100% 차단 | D2.0-07 §4.2:643, CLAUDE.md §20:668~669 동일 | MATCH |
| 5 | 임베딩 모델 V1 | BGE-M3, 1024dim | CLAUDE.md §20:662~663, PHASE_B4:964~965 동일 | MATCH |
| 6 | Decision Lock 규칙 | "5-Gate 통합, Decision Lock" (PART2:406) | CLAUDE.md §7.2:206 "한 시점/한 컨텍스트/한 결론 → locked=true" | MATCH |
| 7 | 비용 경고 임계값 | 80%/100% 2단계 (PART2:129~130) | D2.0-07 §4.2:643 "80% 경고/100% 차단" LOCK | MATCH |
| 8 | 토큰 추적 | I-9 Cost Manager "비용 추적, 다운시프트, 토큰 카운팅" (PART2:424) | D2.0-07 §15.6.1:1559 "토큰 사용량 매 호출 수집" | MATCH |
| 9 | QoD 스코어링 | I-15 QoD 평가, 소스 품질 스코어링 (PART2:405) | D2.0-05:795 `qod_min: 0.7`, D2.0-05:363 evidence_summary에 QoD 포함, D2.0-05:679 "교차 검증 + QoD 점수 산출" | MATCH |
| 10 | DSPy V2 | DSPy 등 V3 B-Series (PART2:732) | D2.0-01:717 "DSPy Prompt Optimizer \| EXP \| V1:OFF / V2:OFF / V3:ON", D2.0-01:1647 확인 | MATCH |

---

## Dim C — IMP_IMPOSSIBLE

| # | PART2:행 | 명세 내용 | 불가 사유 | 대안 제안 | Severity |
|---|---------|---------|---------|---------|----------|
| 1 | :157 | `matryoshka_dim = 256` (검색용 축소 차원) | BGE-M3의 Matryoshka 지원 차원은 모델에 의존. PHASE_B4는 512로 기재. 256은 모델이 지원하지 않을 수 있음 (BGE-M3 공식 지원 차원 확인 필요) | Matryoshka 차원을 PHASE_B4 정본(512)으로 통일하거나, BGE-M3 실제 지원 차원 확인 후 결정 | **HIGH** |

---

## Dim C — IMP_MISSING

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|---------|---------|---------|----------|
| 1 | :113~169 | config.v1.toml (10섹션) | [guardrails], [rbac], [rate_limit], [logging], [semantic_cache] 섹션 코드 블록 미제공. V0-STEP-1에서 이 설정 없이 시작하면 V1 진입 시 config 재작성 필요 | **HIGH** |
| 2 | :424 | I-9 Cost Manager "비용 추적, 다운시프트, 토큰 카운팅" | 비용 기록 포맷(JSON 구조체) 미정의. D2.0-07 §15.6에 실시간 모니터링 항목은 있으나 저장 포맷/스키마 명세 부족 | **MEDIUM** |
| 3 | :126~130 | [cost] 섹션 | KRW/USD 환율 명세 부재. D2.0-07 §4.7:778에서 "1 USD ≈ 1,450 KRW 가정"이나 PART2 config에 환율 키 미정의. 환율 변동 시 비용 상한 계산 기준 불명확 | **MEDIUM** |
| 4 | config.v1.toml 전체 | V0→V1 config 마이그레이션 경로 | PART2에 V0 config→V1 config 변환 가이드 부재. PHASE_B7에 V1→V2만 있고, V0→V1 전환 시 섹션명/키명 변경(general→core, safety→guardrails 등) 대응 필요 | **MEDIUM** |
| 5 | PHASE_B4:908 | ENV override 허용/비허용 키 | "ENV > Runtime DB > config.toml > preset defaults" 우선순위 정의되어 있으나, LOCK 키의 ENV override 허용 여부 명시 부재. cost.daily_limit 등 ABSOLUTE LOCK 키를 ENV로 override할 수 있으면 LOCK 위반 | **HIGH** |

---

## Dim C — IMP_CONFLICT

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|---------|------|
| 1 | PART2:115~118 config `[general]` 섹션 (version, log_level, log_format) | PHASE_B4:939~947 config `[core]` 섹션 (autonomy_level, single_decision_lock, pipeline_stages) | 동일 위치(첫 번째 config 섹션)의 섹션명과 키가 완전히 다름. 구현 시 어느 것을 따를지 혼란 유발 | **BLOCKER** — B4가 정본. PART2의 [general]을 [core]로 교체하고 B4 키 채택 필요 |
| 2 | PART2:121~124 `[llm]` 섹션: default_model/main_model/temperature=0.3/max_tokens=2048 | PHASE_B4:950~959 `[llm]` 섹션: mini_model/main_model/fallback_model/temperature=0.3/max_tokens=4096/streaming=true/prompt_cache=true | 키명 불일치(default_model vs mini_model, fallback_model 미기재), max_tokens 2배 차이(2048 vs 4096), streaming/prompt_cache 미기재 | **HIGH** — B4 정본 기준으로 PART2 수정 필요 |
| 3 | PART2 config ttl_L3 = "unlimited" | PHASE_B4:1007 `l3 = "policy_based"` | L3 TTL 표현 불일치. PART2는 "unlimited"로, B4 정본은 "policy_based"로 기재. SQLite에서 무기한은 NULL 또는 매우 큰 값으로 표현 가능하나, 정본 기준 "policy_based" 채택 필요 | **MEDIUM** |

---

## Dim C — IMP_OK (요약)

| # | 항목 | 판정 근거 |
|---|------|---------|
| 1 | 비용 추적 세분성 | D2.0-07 §15.6.1에 일간/월간/토큰/인프라별 수집 주기 정의. 구현 가능 |
| 2 | daily reset 타이밍 | cost.daily_limit=1300 KRW, 일별 리셋은 표준 cron/scheduler로 구현 가능 |
| 3 | force_mini 대상 | D2.0-07 §4.2 "80% 경고 시 Mini 우선 강제, Main/Flagship은 승인 시만". 구현 가능 |
| 4 | 100% 차단 진행 중 요청 | D2.0-07 §4.3 "초과 시 즉시 차단(deny) + 사용자 알림 + 선택지 제시". 구현 가능 |
| 5 | Ollama 제로 비용 토큰 카운팅 | 로컬 Ollama 호출 시 API 비용=0이나 토큰 카운팅은 필요. tiktoken 등으로 로컬 카운팅 가능 |
| 6 | 비용 경고 UI-CostGate | D2.0-08 §0 "비용 상한 접근 시 경고/다운그레이드, 초과 시 차단 UI 피드백 포함" 명시. 구현 가능 |
| 7 | invalidation_policy Literal | PART2:481~483에 3가지 정의(TTL/Drift/수동). Literal 타입으로 구현 가능 |
| 8 | LOCK 불변 메커니즘 | PHASE_B4에 VAL-002 "LOCK 값 변경 불가 검증" 테스트 정의. config 로드 시 검증으로 구현 가능 |
| 9 | Python config 접근 | PHASE_B4 D.4에 Pydantic v2 ConfigModel 정의. 구현 가능 |
| 10 | distance_metric Chroma 기본값 | PHASE_B4:978 `similarity_metric = "cosine"`. Chroma 기본값과 일치. 구현 가능 |
| 11 | config Pydantic ConfigModel | PHASE_B4:1096~1100에 VamosConfig 루트 모델 + 서브모델 정의. 구현 가능 |
| 12 | relation_types NetworkX | PART2:162 `relation_types = ["CALLS","DEPENDS","USES"]`. NetworkX는 임의 엣지 타입 지원하므로 구현 가능 |

---

## Phase 0 교차 참조

| Phase 0 항목 | Agent 9 대응 | 판정 |
|-------------|-------------|------|
| 0-D LOCK: cost.daily_limit = 1300 | MATCH #1 (₩1,300/일) | ✅ MATCH |
| 0-D LOCK: cost.warn_threshold = 80 | MISSING #1 (키명 차이: warn_threshold vs warn_threshold_pct) | ⚠️ MISMATCH (키명) |
| 0-D LOCK: cost.block_threshold = 100 | MISSING #1 (키명 차이: block_threshold vs block_threshold_pct) | ⚠️ MISMATCH (키명) |
| 0-D LOCK: embedding.matryoshka_dim = 512 | MISMATCH #1 (256 vs 512) | ⚠️ MISMATCH |
| 0-D LOCK: config 13섹션 | MISMATCH #2 (10 vs 13) | ⚠️ MISMATCH |
| 0-D LOCK: semantic_cache.similarity_threshold = 0.95 | MISSING #2 (섹션 부재) | ⚠️ MISSING |

---

## 종합 판정

### BLOCKER (1건)

| ID | 관련 항목 | 내용 | 유형 |
|----|---------|------|------|
| BLK-1 | MISMATCH #2 / IMP_CONFLICT #1 / IMP_MISSING #1 / MISSING #2 | Config 섹션 구조 불일치: PART2=10개 vs B4=13개, [general]→[core] 명명, 누락 섹션([guardrails]/[rbac]/[rate_limit]/[logging]/[semantic_cache]) — 동일 근인 통합 | MISMATCH + IMP_CONFLICT + IMP_MISSING + MISSING |

### HIGH (4건)

| ID | 관련 항목 | 내용 | 유형 |
|----|---------|------|------|
| H-1 | MISMATCH #1 / IMP_IMPOSSIBLE #1 | matryoshka_dim 256 vs 512 불일치 + 기술적 타당성 미확인 — 동일 근인 | MISMATCH + IMP_IMPOSSIBLE |
| H-2 | MISMATCH #3 | LLM 모델명 llama3 vs gemma-2b 불일치 | MISMATCH |
| H-3 | IMP_CONFLICT #2 | [llm] 섹션 키명/값 다수 불일치 (max_tokens 2048 vs 4096 등) | IMP_CONFLICT |
| H-4 | IMP_MISSING #5 | ENV override LOCK 키 허용/비허용 명세 부재 — LOCK 위반 가능성 | IMP_MISSING |

### MEDIUM (8건)

| ID | 관련 항목 | 내용 | 유형 |
|----|---------|------|------|
| M-1 | NO_SOURCE #1 | V0 비용 ₩5,000 출처 불명 | NO_SOURCE |
| M-2 | MISSING #1 | cost 키명 표기 차이 (warn_threshold vs warn_threshold_pct) | MISSING |
| M-3 | MISSING #3 | downshift_model 키 누락 | MISSING |
| M-4 | SC #1 | Multi-Brain Failover 순서/모델 불일치 (PART2 vs CLAUDE.md+D2.0-02) | SOURCE_CONFLICT |
| M-5 | SC #2 | approval_status 값 수 (D2.0-02=3값 vs D2.1-D7=2값) | SOURCE_CONFLICT |
| M-6 | MISMATCH #4 | Agent-Level LLM 할당 불일치 (Sonnet/Haiku vs GPT-4o/SOLAR) | MISMATCH |
| M-7 | IMP_MISSING #2 | 비용 기록 포맷(JSON 구조체) 미정의 | IMP_MISSING |
| M-8 | IMP_MISSING #3 | KRW/USD 환율 config 키 미정의 | IMP_MISSING |
| M-9 | IMP_CONFLICT #3 | ttl_L3 "unlimited" vs "policy_based" 값 불일치 (config 값 근인, BLK-1 구조 근인과 별도) | IMP_CONFLICT |

> ※ IMP_MISSING #4 (V0→V1 마이그레이션)는 IMP_MISSING #1 (config 섹션 누락)과 동일 근인 → BLK-1에 포함

**합계**: BLOCKER **1** + HIGH **4** + MEDIUM **9** = **14건**

---

## 검증 완료 선언

- **Forward 검증**: v8 §5 Agent 9 Dim B 15항목 전수 대조 완료
- **Reverse 검증**: SRC→PART2 역방향 3건 확인 (MISSING #1~#3)
- **Dim C 검증**: 21항목 (IMP_OK 12 + IMP_IMPOSSIBLE 1 + IMP_MISSING 5 + IMP_CONFLICT 3)
- **Phase 0 교차**: 0-D.json LOCK 항목 6건 대조 완료
- **미검증 해소**: D2.0-01, D2.0-02, D2.0-05 추가 검증 → 검증불가 4건 전량 해소
- ⚠️ **BLOCKER 1건 미해소** — Config 섹션 구조 불일치 (PART2 수정 필요)
- 검증 범위: PHASE_B4, D2.0-01, D2.0-02, D2.0-05, D2.0-07, D2.0-08, CLAUDE.md, 0-D.json
