# [Agent 5] 검증 결과 — 스키마 + 타입 시스템

**검증 일시**: 2026-03-04
**PART2 버전**: v13.0.0 (1931행)
**Phase 0 참조**: 0-D.json (LOCK/FREEZE 80건)

---

## 읽은 파일 (실제 읽은 수 / 할당 수: 15 / 12)

- [x] PART2 v13.0.0 (1931행) — 전수 열독 (§2 스키마 구현, §6.2~6.4, V0 체크리스트, 변경 이력)
- [x] D2.1-D1_D1_SCHEMA_GLOSSARY.md (280행) — 전수 열독
- [x] D2.1-D2_D2_SCHEMA_ORANGE_CORE.md (506행) — 전수 열독
- [x] D2.1-D3_D3_SCHEMA_BLUE_NODES.md (418행) — 전수 열독
- [x] D2.1-D4_D4_SCHEMA_INFRA_CORE.md (514행) — 전수 열독
- [x] D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md (493행) — 전수 열독
- [x] D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md (344행) — 전수 열독
- [x] D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md (590행) — 전수 열독
- [x] D2.1-D8_D8_SCHEMA_UI_UX.md (163행) — 전수 열독
- [x] D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md (2829행) — §3.2, §5.1, §7 중심 열독
- [x] CLAUDE.md (§12 스키마 섹션) — 전수 열독
- [x] PHASE_B3_DEPENDENCIES.md — 전수 열독 ※ v8 §5 SRC 할당 외 추가 열독 (타입 파이프라인 교차검증용)
- [x] D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md — serde 관련 검색 열독 ※ v8 §5 SRC 할당 외 추가 열독 (Rust serde 교차검증용)
- [x] VAMOS_검증_프롬프트_v8.md §5 Agent 5 (392-413행) — 전수 열독 ※ v8 §5 SRC 할당 외 추가 열독 (검증 항목 확인용)
- [x] 0-D.json (LOCK/FREEZE 80건) — 전수 열독

---

## 검사 통계

- **Dim B** Forward: **18** / MATCH: **12** / MISMATCH: **2** / NO_SOURCE: **3** / MISSING: **1** / Reverse MISSING: **5** (총 **23** 체크)
- **Dim C** Facts checked: **20** / IMP_OK: **9** / IMP_IMPOSSIBLE: **0** / IMP_MISSING: **3** / IMP_CONFLICT: **8**
- **SOURCE_CONFLICT**: **5건**
- 수정 전: BLOCKER **4**건, HIGH **7**건, MEDIUM **4**건 = 총 **15**건
- 수정 후 (PART2 v14.0.0): BLOCKER **0**건 (BLK-1~4 해소), HIGH **7**건, MEDIUM **4**건 = 총 **11**건

---

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상, FREEZE 위반
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MISMATCH

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|----------|----------|---------|----------|----------|
| 1 | L201,L377 | **24개** Pydantic v2 핵심 모델 | AutonomyLevelSchema 포함 시 **25개**; D2.1-D1 SOT 전체 = 41개 | D2.1-D1 §3.3 (41 schemas), v8 프롬프트 (25개) | **BLOCKER** — PART2 모델 리스트에서 AutonomyLevelSchema 누락. 24→25 정정 필요 |
| 2 | L207 | DecisionSchema **17** (FREEZE) "14 required + 3 optional" | **18**필드 (14 required + **4** optional). 4번째 optional = `s_module_hints` | D2.1-D2 §4.1 L92, CLAUDE.md §12 L508 | **BLOCKER** — FREEZE 위반. s_module_hints 누락으로 17→18 정정 필수. 0-D.json L25도 17로 기록 |

---

## Dim B — NO_SOURCE

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | 판정 |
|---|----------|-----------|----------------|------|
| 1 | L240-241 | 타입 생성 파이프라인: `scripts/generate_types.py` (Pydantic→JSON Schema→TypeScript/Zod) | PHASE_B3_DEPENDENCIES.md 전문 — 해당 내용 없음. B3는 의존성 목록만 포함, zod를 dependency로 나열하나 생성 스크립트 미언급 | NO_SOURCE — PART2 자체 정의만 존재, B3에 미기재. **MEDIUM** |
| 2 | L911 | Rust serde 모델 24개 (D2.1 스키마 매칭 Rust struct) | D2.0-04 전문 — `serde`, `구조체`, `Rust struct` 검색 결과 없음. D2.0-04는 Brain Engine 추상화 문서이며 Rust 구조체 정의 미포함 | NO_SOURCE — PART2가 "D2.1 스키마 매칭"이라 기술하나 D2.0-04에 근거 없음. **MEDIUM** |
| 3 | L206 | EvidencePack 6필드 | D2.1-D1~D8 전체 — EvidencePack/EvidencePackSchema 미존재. D2.1-D1 §3.3 ownership mapping에도 미등재 | NO_SOURCE — D2.0-02 §7.2에만 비형식 정의. D2.1 SOT 미반영. **HIGH** |

---

## Dim B — MISSING

| # | 구분 | 원본 출처 | 누락 내용 | Severity |
|---|------|----------|----------|----------|
| 1 | 순방향 (B#11) | D2.1-D7 §4.7 L221-244 | **AutonomyLevelSchema** (7필드: level, name, description, auto_execute, notification_required, approval_required, allowed_domains) — PART2 24-모델 테이블에 미포함 | **BLOCKER** — v8 Dim B #11에 명시된 검증 항목이 PART2에 누락 |
| 2 | 역방향 (MISMATCH #2 동일 근인) | D2.1-D2 §4.1 L92 | DecisionSchema 4번째 optional 필드 **`s_module_hints`** (Self-evo 모듈 힌트 객체) — PART2 필드 수 17에 미반영 | **BLOCKER** — FREEZE 위반 (MISMATCH #2와 동일 근인) |
| 3 | 역방향 | D2.1-D5 L373-398 | **ResponseEnvelopeSchema** (D5, 9필드) — PART2의 ResponseEnvelope(5필드 LOCK)와 별개 스키마이나 PART2에 미언급 | **HIGH** — D5 SOT에 독립 스키마로 존재하나 PART2가 CLAUDE.md §12의 5필드 LOCK만 반영 |
| 4 | 역방향 | D2.1-D1 §3.3 L216-256 | PART2 24개 외 **추가 17개 스키마** (InfraInvokeResult, PromptCacheManager, RateLimitConfig, BackupConfig, AgentMarketplace, CircuitBreaker, GatePipelineMapping, HITLRequest, VerifyChainEntry, VectorStoreAdapter, GraphRAGConfig, SemanticCache, CloudLibrary* 7종) — V0 서브셋 판단이지만 명시적 제외 사유 미기재 | **MEDIUM** — V0/V1/V2 버전 분류 기준으로 제외 가능하나 "전체 vs 서브셋" 경계 불명확 |
| 5 | 역방향 | D2.1-D2 §5.1 EventTypeRegistry | EventTypeRegistry **123개** 이벤트 타입 — PART2 L233은 "53+ (oc.* 네임스페이스)"로 기재하나 D2.1-D2 SOT는 전체 123개 | **HIGH** — 53+ vs 123 불일치 (oc.* 실제 33개, 전체 123개) |
| 6 | 역방향 | D2.1-D1 §3.3 | **IntentFrame**, **EvidencePack**, **StructuredOutput** — PART2에 포함되나 D2.1-D1 SOT ownership mapping에 미등재. 이 3개는 D2.0-02에만 비형식 정의 존재 | **MEDIUM** — 형식 스키마화 필요 |

---

## Dim B — SOURCE_CONFLICT

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|------------------|
| 1 | D2.1-D2 §4.1 L79: `approval_status` = **approved \| denied** (2값, Q1 DN-014 A 결정) | CLAUDE.md §12 L504: `approval_status` = **approved\|denied\|pending\|expired** (4값) | **D2.1-D2 SOT** 우선 (Schema > CLAUDE.md). 다만 D2.0-02 §3.2 L544는 3값(+pending). CLAUDE.md §12를 D2.1-D2에 정합 필요 |
| 2 | D2.1-D2 §4.1 L77: `policy_gate` = **block \| require_approval \| mask \| allow** (4값) | D2.0-02 §3.2 L540 + D2.1-D7 PolicyCheck.decision = **deny \| restrict \| allow** (3값) | D2.1-D2 SOT가 "D7 PolicyCheck 정본" 참조하면서 다른 값 사용. **D2.1-D2 SOT 수정** 또는 의도적 변환 명시 필요 |
| 3 | CLAUDE.md §12 L521-529: ResponseEnvelope = **5필드 LOCK** (answer, evidence, self_check, decision_ref, audit) | D2.1-D5 §4.9 L373-398: ResponseEnvelopeSchema = **9필드** (response_id, trace_id, decision_id, status, user_response, evidence_summary, metadata, warnings, created_at) | **다른 스키마**: CLAUDE.md는 개념적 출력 구조, D2.1-D5는 API 레벨 형식 스키마. 명칭 충돌 해소 필요 |
| 4 | PART2 L233: EventTypeRegistry = **53+** (oc.* 네임스페이스) | D2.1-D2 §5.1 L137: EventTypeRegistry = **123**개 (oc.*/wf.*/ui.*/mem.*/storage.*/agent.*/sdar.*) | **D2.1-D2 SOT** 우선. PART2는 V0 서브셋 의미로 53+를 기재한 것으로 보이나, oc.* 실제 = 33개로 53+ 자체도 부정확 |
| 5 | PART2 L207: DecisionSchema = **17필드** (FREEZE) | D2.1-D2 SOT + CLAUDE.md §12: DecisionSchema = **18필드** (FREEZE) | **D2.1-D2 SOT** 우선. PART2 v9.0.0 변경 시 "14 req + 3 opt = 17"로 잘못 집계. s_module_hints(4번째 opt) 누락 |

---

## Dim C — IMP_IMPOSSIBLE

| # | PART2:행 | 명세 내용 | 불가 사유 | 대안 제안 | Severity |
|---|----------|----------|----------|----------|----------|
| (해당 없음) | | | | | |

---

## Dim C — IMP_MISSING

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|----------|----------|----------|----------|
| 1 | §2 전반 | IntentFrame optional/required 구분 | D2.0-02 §7.3은 비형식 명세(필드 나열)만 제공. D2.1-D1 SOT에 IntentFrameSchema 미등재. `required/optional` 구분 없어 구현 시 해석 필요 | **HIGH** — Pydantic 코드 생성 시 required 판정 불가 |
| 2 | L207 (MemoryRecord) | MemoryRecord → SQLite 테이블 매핑 DDL | 20필드의 SQLite column type 매핑, NOT NULL/DEFAULT, 인덱스 전략 미정의. PHASE_B4 config에도 DDL 미포함 | **MEDIUM** — 구현 시 개발자 재량에 의존 |
| 3 | L911 | Pydantic → serde (Rust) 변환 파이프라인 | `scripts/generate_types.py`는 Pydantic→JSON Schema→Zod만 커버. Rust serde 구조체 24개 자동 생성 도구/스크립트 미정의 | **HIGH** — 수동 작성 시 동기화 리스크 |

---

## Dim C — IMP_CONFLICT

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|----------|------|
| 1 | PART2 L201: "24개 Pydantic" | v8 프롬프트 + D2.1-D7(AutonomyLevelSchema): 25개 | 모델 카운트 불일치. AutonomyLevelSchema 추가 시 25. | **BLOCKER** — PART2 테이블에 AutonomyLevelSchema 추가 필요 |
| 2 | PART2 L207: "DecisionSchema 17 (FREEZE)" | D2.1-D2 §4.1: 18필드 (14R+4O) | FREEZE 카운트 1 차이. s_module_hints 누락. | **BLOCKER** — 17→18 정정, s_module_hints 항목 추가 |
| 3 | CLAUDE.md §12 L521: "ResponseEnvelope 5필드 LOCK" | D2.1-D5 L373: "ResponseEnvelopeSchema 9필드" | 동일 명칭 다른 구조. CLAUDE.md=개념적 출력봉투, D5=API 형식 스키마 | **HIGH** — 명칭 분리 또는 관계 명시 필요 |
| 4 | D2.1-D2 L77: policy_gate = block\|require_approval\|mask\|allow | D2.0-02 L540 + D2.1-D7: deny\|restrict\|allow | DecisionSchema.policy_gate enum 값이 PolicyCheck.decision enum 값과 불일치 | **HIGH** — D2.1-D2 SOT 내부 참조("D7 PolicyCheck 정본")와 실제 값 상충 |
| 5 | PART2 L233: EventTypeRegistry = "53+" | D2.1-D2 §5.1: EventTypeRegistry = 123개 | PART2의 53+가 V0 서브셋이라 해도 oc.*=33개여서 53+도 부정확 | **HIGH** — 카운트 정정 필요 (V0 범위 명시 또는 123으로 수정) |
| 6 | PART2 L207 + CLAUDE.md §12: s_module_hints 처리 | D2.1-D2 §4.1 L92: s_module_hints = optional | PART2는 3 optional만 집계 (optional_signals, verify, gates). s_module_hints 누락 | **BLOCKER** — FREEZE 스키마 불완전 반영 |
| 7 | PART2: "24개" (V0 서브셋) | D2.1-D1 SOT: 41개 (전체) | V0 서브셋=24, 전체=41. "25개"가 올바른 V0 서브셋이나 PART2는 24로 기재 | **HIGH** — V0 범위 기준 명확화 필요 |
| 8 | D2.1-D2 L79: approval_status = approved\|denied (2값) | CLAUDE.md §12 L504: approved\|denied\|pending\|expired (4값) | DecisionSchema.approval_status enum 값 불일치. DN-014 A에서 pending 제거 결정 vs CLAUDE.md 미반영 | **HIGH** — CLAUDE.md §12를 D2.1-D2 SOT(2값)에 정합하거나, DN-014 A 재검토 |

---

## Phase 0 교차 참조

| # | 0-D.json 항목 | PART2 값 | 0-D.json 값 | 판정 |
|---|--------------|---------|------------|------|
| 1 | DecisionSchema (FREEZE) | 18필드 (v14.0.0 수정 후) | 18 (BLK-3 수정 후) | ✅ MATCH |
| 2 | ResponseEnvelope (LOCK) | 5필드 | 5필드 | ✅ MATCH |
| 3 | WorkflowStage (LOCK) | 4필드 | 4필드 | ✅ MATCH |
| 4 | WorkflowOutput (LOCK) | 3필드 | 3필드 | ✅ MATCH |

---

## v8 §5 Agent 5 Dim B 항목 13~18 문서 갭 보고

v8 프롬프트 §5 Agent 5 Dim B 섹션(L394-406)은 **12개 bullet만 나열**하나 매트릭스(L268)는 18항목으로 기재. 실행 프롬프트(L1193)는 "§5에서 나머지 6항목 확인"을 지시하나 §5에 해당 항목 부재.

본 검증에서는 PART2 테이블의 나머지 스키마 필드 수를 추가 검증하여 18항목을 채움:

| 추론 # | 검증 항목 | PART2 값 | SRC 값 | 결과 |
|--------|----------|---------|--------|------|
| 13 | EvidencePack 6필드 | 6 (L206) | D2.0-02 §7.2 비형식: 6 (D2.1 SOT 없음) | NO_SOURCE |
| 14 | SourceQoD 8필드 | 8 (L212) | D2.1-D6: 8 (6R+2O) | MATCH |
| 15 | PolicyCheck 7필드 | 7 (L213) | D2.1-D7: 7 (5R+2O) | MATCH |
| 16 | ApprovalSchema 12필드 | 12 (L214) | D2.1-D7: 12 (8R+4O) | MATCH |
| 17 | CostBudget 9필드 | 9 (L215) | D2.1-D7: 9 (6R+3O) | MATCH |
| 18 | NodeCapabilityProfile 6필드 | 6 (L217) | D2.1-D3: 6 (5R+1O) | MATCH |

---

## 전체 Dim B 개별 검증 상세

| B# | 검증 항목 | PART2 값 | SRC 정본 값 | 판정 | Severity |
|----|----------|---------|-----------|------|----------|
| 1 | Pydantic 모델 수 | 24개 | 25개 (AutonomyLevelSchema 포함) | **MISMATCH** | BLOCKER |
| 2 | DecisionSchema 필드 수 (FREEZE) | 17 (14R+3O) | 18 (14R+4O) | **MISMATCH** | BLOCKER |
| 3 | ResponseEnvelope 필드 수 (LOCK) | 5 | 5 (CLAUDE.md §12) | MATCH | - |
| 4 | IntentFrame 필드 수 | 10 | 10 (D2.0-02 §7.3) | MATCH | - |
| 5 | MemoryRecord 필드 수 | 20 | 20 (D2.1-D6: 7R+13O) | MATCH | - |
| 6 | StructuredOutput 필드 수 | 4 | 4 (D2.0-02 C3 appendix) | MATCH | - |
| 7 | WorkflowStage/Output (LOCK) | 4/3 | 4(3R+1O)/3(3R) (D2.1-D5) | MATCH | - |
| 8 | 타입 생성 파이프라인 | Pydantic→JSON→Zod | PHASE_B3에 미기재 | **NO_SOURCE** | MEDIUM |
| 9 | Rust serde 구조체 수 | 24 | D2.0-04에 미기재 | **NO_SOURCE** | MEDIUM |
| 10 | 스키마 버전 | v3.0.0 | v3.0.0 (D2.1-D1~D8 전체) | MATCH | - |
| 11 | AutonomyLevelSchema 필드 수 | (PART2 미등재) | 7 (D2.1-D7: 6R+1O) | **MISSING** | BLOCKER |
| 12 | LogEventSchema 필드 수 | 7 | 7 (D2.1-D2: 5R+2O) | MATCH | - |
| 13 | EvidencePack 필드 수 | 6 | D2.1 SOT 없음 | **NO_SOURCE** | HIGH |
| 14 | SourceQoD 필드 수 | 8 | 8 (D2.1-D6: 6R+2O) | MATCH | - |
| 15 | PolicyCheck 필드 수 | 7 | 7 (D2.1-D7: 5R+2O) | MATCH | - |
| 16 | ApprovalSchema 필드 수 | 12 | 12 (D2.1-D7: 8R+4O) | MATCH | - |
| 17 | CostBudget 필드 수 | 9 | 9 (D2.1-D7: 6R+3O) | MATCH | - |
| 18 | NodeCapabilityProfile 필드 수 | 6 | 6 (D2.1-D3: 5R+1O) | MATCH | - |

---

## 전체 Dim C 개별 검증 상세

| C# | 검증 항목 | 판정 | 상세 | Severity |
|----|----------|------|------|----------|
| 1 | 25개 모델 필드 수 일치 | **IMP_CONFLICT** | PART2=24개, v8=25개, D2.1-D1=41개. AutonomyLevelSchema 누락 | BLOCKER |
| 2 | DecisionSchema 18필드 FREEZE 강제 | **IMP_CONFLICT** | PART2=17, SRC=18. s_module_hints 누락 | BLOCKER |
| 3 | IntentFrame optional/required | **IMP_MISSING** | D2.0-02 비형식 정의만 존재. D2.1에 IntentFrameSchema 미등재. required/optional 구분 불가 | HIGH |
| 4 | MemoryRecord SQLite 매핑 | **IMP_MISSING** | 20필드 DDL 미정의. column type, NOT NULL, 인덱스 전략 부재 | MEDIUM |
| 5 | Pydantic→JSON Schema→Zod 파이프라인 | **IMP_OK** | PART2 L240-241: `scripts/generate_types.py` 정의. PHASE_B3에 zod 의존성 확인 | - |
| 6 | Pydantic→serde 변환 | **IMP_MISSING** | Pydantic→Zod만 자동화. Rust serde 24구조체 자동 생성 스크립트 미정의 | HIGH |
| 7 | ResponseEnvelope vs StructuredOutput | **IMP_CONFLICT** | ResponseEnvelope=최종 출력 봉투(5필드 LOCK), StructuredOutput=I-4 아티팩트(4필드). 역할 분리 OK. 단, D2.1-D5 ResponseEnvelopeSchema(9필드)와 CLAUDE.md ResponseEnvelope(5필드)는 동명이체 | HIGH |
| 8 | PolicyCheck 결과 타입 | **IMP_CONFLICT** | D2.1-D7 PolicyCheck.decision=deny\|restrict\|allow (3값) vs D2.1-D2 DecisionSchema.policy_gate=block\|require_approval\|mask\|allow (4값). 값 매핑 미정의 | HIGH |
| 9 | CostBudget daily_limit_krw | **IMP_OK** | D2.1-D7: `daily_limit`=1300, `monthly_limit`=40000. 필드명에 `_krw` 없으나 값(₩)으로 단위 확인 | - |
| 10 | EventTypeRegistry 123개 Enum | **IMP_CONFLICT** | D2.1-D2 SOT=123개 확인. PART2=53+ 불일치. oc.*=33개로 53+도 부정확 | HIGH |
| 11 | FailureCode→Fallback 매핑 비율 | **IMP_OK** | D2.1-D2: 36 FailureCode 중 22개 매핑 (61.1%). 나머지 14개는 범용 핸들러 또는 미매핑 | - |
| 12 | s_module_hints | **IMP_CONFLICT** | D2.1-D2 SOT에 18번째 필드로 정의. PART2는 17필드만 집계하여 누락. CLAUDE.md는 포함 | BLOCKER |
| 13 | WorkflowStage→LangGraph state | **IMP_OK** | 5-Stage(intake/plan/execute/verify/deliver) → LangGraph StateGraph 노드 매핑 가능 | - |
| 14 | RBACRole 권한 매트릭스 | **IMP_OK** | D2.1-D7: OWNER\|ADMIN\|OPERATOR\|VIEWER 4역할, permissions 배열 정의. 매트릭스 구현 가능 | - |
| 15 | 24-모델 import cycle | **IMP_OK** | `backend/schemas/contracts.py` 단일 파일에 24(25)개 정의. 순환 의존 위험 없음 | - |
| 16 | V0 전체 vs 서브셋 | **IMP_CONFLICT** | PART2=24개(V0 서브셋), D2.1-D1=41개(전체). 서브셋 선정 기준 미명시. 25개가 올바른 V0 서브셋(+AutonomyLevelSchema) | HIGH |
| 17 | ApprovalSchema 2값 vs 4값 | **IMP_CONFLICT** | D2.1-D2/D7 SOT=2값(approved\|denied, DN-014 A). CLAUDE.md=4값(+pending\|expired). D2.0-02=3값(+pending). 정합 필요 | HIGH |
| 18 | DownshiftSchema 트리거 | **IMP_OK** | D2.1-D7: trigger_type=daily\|monthly, warn=80% LOCK, block=100% LOCK. 구현 명확 | - |
| 19 | GuardrailsCheck 듀얼 프레임워크 | **IMP_OK** | D2.1-D7: 3-Layer (NeMo + Guardrails AI + LlamaGuard). "듀얼"=2 프레임워크(NeMo+GuardrailsAI) + LlamaGuard 보강 | - |
| 20 | NodeCapabilityProfile vs ToolRegistryEntry | **IMP_OK** | D3:NodeCapabilityProfile(6필드,노드 레벨) vs D4:ToolRegistryEntry(8필드,도구 레벨). 공유 필드: risk_class, cost_class, required_gates. 역할 분리 적절 | - |

---

## 종합 판정

### BLOCKER 목록 (4건 — 즉시 수정 필요)

| # | 항목 | 내용 | 수정 방안 |
|---|------|------|----------|
| **BLK-1** | DecisionSchema FREEZE 위반 | PART2 L207: 17필드 → SRC 정본 18필드. 4번째 optional `s_module_hints` 누락 | PART2 §2 테이블 #3: `17 (FREEZE)` → `18 (FREEZE)` 정정. 변경이력에 "14 required + 4 optional" 명기 |
| **BLK-2** | Pydantic 모델 수 불일치 | PART2: 24개. AutonomyLevelSchema(D2.1-D7 §4.7, 7필드) 누락 | PART2 §2 테이블에 #25 AutonomyLevelSchema 추가. "24개"→"25개" 전수 정정 (L201, L377, L1742 등) |
| **BLK-3** | 0-D.json FREEZE 값 구버전 | 0-D.json L25: "DecisionSchema \| 17 (FREEZE)" | Phase 0 재추출 또는 0-D.json 수동 정정: 17→18 |
| **BLK-4** | v9.0.0 변경이력 오기재 | PART2 L1926: "14 required + 3 optional" | → "14 required + 4 optional" 정정 |

### HIGH 목록 (7건)

| # | 항목 | 내용 |
|---|------|------|
| H-1 | ResponseEnvelopeSchema 명칭 충돌 | CLAUDE.md 5필드 LOCK vs D2.1-D5 9필드 — 다른 스키마인데 동일 명칭 |
| H-2 | policy_gate enum 불일치 | D2.1-D2 SOT(4값) vs D2.0-02/D2.1-D7(3값). 내부 참조 모순 |
| H-3 | approval_status enum 불일치 | D2.1-D2(2값) vs CLAUDE.md(4값) vs D2.0-02(3값) |
| H-4 | EventTypeRegistry 카운트 | PART2=53+, SRC=123, oc.*실제=33. 53+ 근거 불명 |
| H-5 | EvidencePack D2.1 SOT 미등재 | PART2에 포함(6필드)되나 D2.1 정식 스키마 없음 |
| H-6 | IntentFrame required/optional 미정의 | D2.0-02 비형식 명세만 존재. Pydantic 코드 생성 시 해석 필요 |
| H-7 | Pydantic→serde 변환 파이프라인 미정의 | 24 Rust 구조체 수동 작성 시 동기화 리스크 |

### MEDIUM 목록 (4건)

| # | 항목 | 내용 |
|---|------|------|
| M-1 | 타입 생성 파이프라인 PHASE_B3 미기재 | PART2 자체 정의만 존재, B3 교차참조 부재 |
| M-2 | serde 24 구조체 D2.0-04 출처 오류 | D2.0-04에 Rust serde 정의 없음. PART2 자체 기술 |
| M-3 | V0 서브셋 경계 불명확 | 41개 SOT 중 24(또는 25)개 선정 기준 미명시 |
| M-4 | MemoryRecord SQLite DDL 미정의 | 20필드의 column type/index 전략 미기재 |

---

## 수정 권고 우선순위

1. **[즉시]** PART2 §2 DecisionSchema: 17→18, "14R+3O"→"14R+4O", s_module_hints 추가
2. **[즉시]** PART2 §2 모델 테이블: #25 AutonomyLevelSchema(7필드, D2.1-D7) 추가, "24개"→"25개" 전수 정정
3. **[즉시]** 0-D.json / Phase 0 결과: DecisionSchema 17→18 정정
4. **[HIGH]** CLAUDE.md §12 approval_status: 4값→2값 정합 (D2.1-D2 SOT DN-014 A 준수) 또는 DN-014 A 재검토
5. **[HIGH]** D2.1-D2 policy_gate enum: D7 PolicyCheck.decision과 값 매핑 관계 명시
6. **[HIGH]** ResponseEnvelopeSchema(D5, 9필드) vs ResponseEnvelope(CLAUDE.md, 5필드 LOCK) 명칭/관계 정리
7. **[HIGH]** EventTypeRegistry: PART2 53+→V0 범위 명확화 또는 123으로 정정
8. **[HIGH]** IntentFrame/EvidencePack/StructuredOutput: D2.1 SOT 스키마 정의 추가 또는 "D2.0-02 전용" 명시
9. **[HIGH]** Pydantic→serde 변환 자동화 스크립트 정의 추가
10. **[MEDIUM]** 타입 파이프라인/serde 출처: PHASE_B3/D2.0-04 교차참조 보강

---

## 검증 완료 선언

- 수정 전: BLOCKER **4**건, HIGH **7**건, MEDIUM **4**건 = 총 **15**건 (SOURCE_CONFLICT **5**건은 severity에 포함)
- 수정 후 (PART2 v14.0.0): BLOCKER **0**건 (BLK-1~4 해소), HIGH **7**건, MEDIUM **4**건 = 총 **11**건
- Dim B: Forward **18** + Reverse **5** = **23** 체크 — MATCH **12**, MISMATCH **2**, NO_SOURCE **3**, MISSING **6**
- Dim C: **20**항목 — IMP_OK **9**, IMP_MISSING **3**, IMP_CONFLICT **8**, IMP_IMPOSSIBLE **0**
- ✅ **PASS** — BLOCKER 전수 해소 완료. 잔여 HIGH 7건 + MEDIUM 4건은 Phase 2에서 처리.

---

## 수정 이력 (v14.0.0 반영)

> 아래 4건은 PART2 v14.0.0 (2026-03-04)에서 수정 완료됨.

| # | ID | 수정 내용 | PART2 위치 | 상태 |
|---|-----|----------|-----------|------|
| 1 | BLK-1 | DecisionSchema 17필드 → 18필드 (14R+3O → 14R+4O), s_module_hints 추가 | §2 스키마 테이블 | ✅ 완료 |
| 2 | BLK-2 | Pydantic 모델 24개 → 25개, #25 AutonomyLevelSchema(7필드) 추가 | §2 모델 테이블, L201, L377 | ✅ 완료 |
| 3 | BLK-3 | 0-D.json DecisionSchema 17 → 18 정정 | 0-D.json L25 | ✅ 완료 |
| 4 | BLK-4 | 변경이력 "14 required + 3 optional" → "14 required + 4 optional" | PART2 변경이력 | ✅ 완료 |

**수정 파일**: `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (v13.0.0 → v14.0.0)
**변경 이력**: changelog v14.0.0 항목 추가
