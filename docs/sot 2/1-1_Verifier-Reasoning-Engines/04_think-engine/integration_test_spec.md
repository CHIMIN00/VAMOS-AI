# D-1 Think Engine — Integration Test Spec (L3)

> **Status**: APPROVED
> **버전**: v1.1
> **작성일**: 2026-04-18
> **Last-reviewed**: 2026-06-02 (Phase 4 production promotion RECOVERY Sub-B P4-6 Status 승급 + P4-7 LOCK-VR-06 4조건 + 6-11 cross-ref 양방향 반영 + ReadOnly TRUE 진입)
> **Owner**: 1-1_Verifier-Reasoning-Engines
> **근거**: P2-6, G2-2 기여 — 5개 엔진 통합 테스트 스펙
> **Phase 태그**: V2-Phase 2 (Phase 2 신규 산출물)
> **TEST_MODE**: sandbox (production UNCHANGED)

---

## 1. 교차 참조 블록

| 정본 문서 | 참조 섹션 | 용도 |
|----------|----------|------|
| `04_think-engine/spec.md` (P1-5~6, V1) | I/O Schema, 전략 | 시나리오 기초 |
| `04_think-engine/reasoning_strategies.md` (P1-5/6, V1) | CoT/ToT/GoT/Auto | 전략별 시나리오 |
| `04_think-engine/state_machine.md` (V1) | EngineState 전이 | 상태 검증 |
| `04_think-engine/error_handling.md` (P1-9, V1) | §4.1, §5.4 | 예외 |
| `06_dependency-graph/escalation_flow.md` (P1-11, V1) | §2.5, §3.2, §5.4 | D-1 흐름 (Layer 1/2 교차) |
| `06_dependency-graph/orange_core_integration.md` (P1-12, V1) | §3.1, §5.4, §6 | State + chain_used + Failover |
| `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §10.5.2, §11.1.2 | chain_used + LLM Failover |
| `00_common/failover_policy.md` (P0-8) | Layer 1 LLM Failover | LOCK-VR-07 적용 |
| `AUTHORITY_CHAIN.md` §4 | LOCK-VR-04/05/07/08/11/12 | LOCK 정본 |
| **6-12 Event-Logging** (READ-only) | oc.i1~i5 + BRAIN_FAILOVER | 이벤트 검증 |

---

## 1.R Verify Chain LOCK-VR-06 + 6-11 ORANGE CORE cross-ref (RECOVERY Sub-B P4-7, 2026-06-02)

> **근거**: CONFLICT_LOG CONF-VRE-010 RESOLVED (RECOVERY Sub-A P4-5, 2026-06-02)의 물리 반영. 본 절은 (1) `verify.chain_used` per-engine check-type identifier 정본 명칭 정합, (2) LOCK-VR-06 Verify Chain 4조건 인용, (3) 6-11 ORANGE CORE 양방향 cross-ref를 명시한다.

### 1.R.1 per-engine check-type identifier 정본 (V1 명칭 정합)

| 항목 | 정본 값 | 출처 |
|------|---------|------|
| D-1 Think Engine `verify.chain_used` 추가 식별자 | `"think_reasoning_check"` | 1-1 per-engine check-type identifier 정본 (CONF-VRE-010 RESOLVED, TYPE-D) |
| 6-11 carrier 필드 | `Decision.verify.chain_used` (list[str]) | ORANGE CORE D2.0-02 §10.5.2 정본 carrier |

> **명칭 정합 확정**: 본 통합 테스트 시나리오 IT-D1-F-01 (chain_used 추적)에서 사용하는 `"think_reasoning_check"` 는 D-1 Think Engine의 per-engine check-type identifier 정본이며, 6-11 ORANGE CORE의 `verify.chain_used` carrier 필드가 이를 **값으로 수용**한다 (TYPE-D: ORANGE CORE carrier 정본 우선 + 1-1 per-engine 명칭 정본). CONF-VRE-010은 RECOVERY Sub-A P4-5에서 RESOLVED (OPEN=0) 정식 마킹되었고, 본 P4-7은 그 물리 반영이다.

### 1.R.2 LOCK-VR-06 Verify Chain 4조건 (인용)

> **LOCK (D2.0-02 §10.1/§10.3 + AUTHORITY_CHAIN §3.4 LOCK-VR-06)**: Verify Chain = **Default OFF + timeboxed + cost limit + approval**
> - **Default OFF**: Verify Chain은 기본 비활성 — 자동 ON 금지 (§10.3)
> - **timeboxed**: 체인 실행은 타임박스 내로 제한 (§10.1)
> - **cost limit**: 비용 상한 적용 (§10.1)
> - **approval**: 활성화 시 승인 필요 (§10.3)

본 D-1 Think Engine의 chain_used 기록은 위 4조건을 준수하는 Verify Chain 활성 구간에서만 발생하며, Default OFF 상태에서는 `verify.chain_used`에 `"think_reasoning_check"`가 추가되지 않는다.

### 1.R.3 6-11 ORANGE CORE 양방향 cross-ref

| 방향 | 내용 | 상태 |
|------|------|------|
| 1-1 → 6-11 | D-1 Think Engine `"think_reasoning_check"` per-engine identifier 정본 제공 | DEFINED-HERE (1-1 정본) |
| 6-11 → 1-1 | `Decision.verify.chain_used` carrier가 `"think_reasoning_check"` 수용 + Pipeline S5→S6 기록 | CITE-ONLY (6-11 ORANGE CORE 정본 carrier, D2.0-02 §10.5.2) |

> **6-11 진입 시 양방향 확정 forward-defined**: 6-11 Hologram-Main-LLM은 Wave 3 #28 미진입 상태이므로, 본 cross-ref는 1-1 측 정본을 확립하고 6-11 진입 시 양방향 최종 확정한다. 6-11 plan baseline 0 touch (외부 도메인 자체 진행). CROSS_HANDOFF_DRIFT NOT FIRED.

---

## 2. 범위 (Purpose / Scope)

D-1 Think Engine 통합 테스트 시나리오 (L3). Given-When-Then ≥ 10건.

**범위 포함**: 전략별 (CoT/ToT/GoT/Auto), auto-select 정확도, max_depth boundary, C → D 에스컬레이션 수신, Layer 1 LLM Failover (LOCK-VR-07), chain_used, Event-Logging.

**범위 제외**: 실 LLM 모델 정확도 평가 (Phase 3, 5-1 Benchmark Evaluation 도메인 책임).

---

## 3. LOCK 정본 인용 (AUTHORITY_CHAIN.md §4)

> LOCK-VR-04 (D2.0-02 §2.2): S0~S8 (S3 Decision Lock immutable)
> LOCK-VR-05 (상세명세 C-1 §4): D-1는 자체 품질 판정 사용 (escalation_flow §2.5: confidence < 0.5 트리거)
> LOCK-VR-07 (D2.0-02 §11.1.2): GPT-4o → Claude Sonnet → Ollama (LLM Failover) [scope: 1-1 추론 엔진 전용]
> LOCK-VR-08 (D2.0-02 §2.3-A): tiktoken 표준
> LOCK-VR-11 (상세명세 C-1 §3): ABC 패턴 (D-1는 BaseReasoningEngine ABC)
> LOCK-VR-12 (D2.0-02 §2.3-B): 단일응답 ≤2s / 복합응답 ≤10s / Self-check ≤1s

D-1 직접 적용: **VR-04 / VR-05 / VR-07 (Layer 1 핵심) / VR-08 (token 계측) / VR-11 / VR-12**.

---

## 4. 시나리오 식별 체계

| 카테고리 | 시나리오 ID 범위 | 건수 |
|---------|----------------|------|
| A. 전략별 (CoT/ToT/GoT/Auto) | IT-D1-A-01 ~ IT-D1-A-04 | 4 |
| B. auto-select 정확도 | IT-D1-B-01 | 1 |
| C. max_depth boundary | IT-D1-C-01 ~ IT-D1-C-02 | 2 |
| D. C → D 에스컬레이션 수신 | IT-D1-D-01 | 1 |
| E. Layer 1 LLM Failover (LOCK-VR-07) | IT-D1-E-01 ~ IT-D1-E-02 | 2 |
| F. chain_used 추적 | IT-D1-F-01 | 1 |
| G. Event-Logging | IT-D1-G-01 | 1 |
| **합계** | | **12** |

---

## 5. 시나리오 (Given-When-Then)

### IT-D1-A-01: CoT (Chain of Thought) — shallow

**Given**: `ThinkRequest(question="What is 2+3*4?", strategy="cot", max_depth=3, timeout_ms=2000)`.

**When**: D-1 `reason(req)`, CoT 단일 체인 추론.

**Then**:
- `ThinkResult.confidence ≥ 0.8`
- `result.strategy_used == "cot"`
- `result.reasoning_trace` 에 step ≤ 3 단계 기록
- 응답시간 ≤ 800ms (orange_core_integration §6.3 D-1 shallow budget).

**판정 기준**: confidence + strategy + trace.

---

### IT-D1-A-02: ToT (Tree of Thought) — branching

**Given**: `question="Plan a trip to Paris in 3 days"`, `strategy="tot"`, `max_depth=4`, branching=3.

**When**: ToT 트리 탐색.

**Then**:
- `confidence ≥ 0.8`, `strategy_used == "tot"`
- `reasoning_trace` 에 분기 노드 + 가지치기 흔적
- 응답시간 ≤ 4,000ms (D-1 deep budget).

**판정 기준**: ToT 구조 확인 + 시간.

---

### IT-D1-A-03: GoT (Graph of Thought) — interconnected

**Given**: `question="Compare Python vs Rust for backend"`, `strategy="got"`, `max_depth=5`.

**When**: GoT 그래프 추론 (cross-references).

**Then**:
- `confidence ≥ 0.8`, `strategy_used == "got"`
- `reasoning_trace` 에 graph edges 기록.

**판정 기준**: graph 구조.

---

### IT-D1-A-04: Auto — strategy 자동 선택

**Given**: `question="Solve this math problem: 2x+3=11"`, `strategy="auto"`.

**When**: D-1 가 question 분석 후 strategy 선택 (단순 → CoT 자동).

**Then**:
- `strategy_used == "cot"` 자동 선택
- `confidence ≥ 0.8`.

**판정 기준**: auto 가 적절한 strategy 선택.

---

### IT-D1-B-01: auto-select 정확도 — 복합 질문

**Given**: 10개 다양한 question (단순 산수 / 다단계 plan / 비교 분석 / open-ended).

**When**: 각각 `strategy="auto"` 로 D-1 호출.

**Then**:
- 단순 산수 → CoT
- 다단계 plan → ToT
- 비교 분석 → GoT
- 정확도 ≥ 80% (10건 중 8건 적절한 매핑).

**판정 기준**: auto-select 정확도 ≥ 80%.

---

### IT-D1-C-01: max_depth boundary — 정확히 max_depth 도달

**Given**: `question="Deep philosophical inquiry..."`, `strategy="tot"`, `max_depth=5`.

**When**: 추론이 정확히 5 depth 에서 강제 수렴.

**Then**:
- `current_depth == 5`
- 결과 반환 (조기 종합 또는 PASS).

**판정 기준**: depth 정확.

---

### IT-D1-C-02: max_depth boundary — 초과 → D1_DEPTH_EXCEEDED

**Given**: 매우 깊은 추론 필요 question, `max_depth=2` (의도적 작게).

**When**: 추론 depth 2 초과 시도.

**Then**:
- `error_code="D1_DEPTH_EXCEEDED"` (escalation_flow §5.4)
- 조기 종합 결과 `confidence < 0.5`
- I-20 → Fallback Chain (Layer 1 LLM 교체) (escalation_flow §2.5 T-D1-1).

**판정 기준**: D1_DEPTH_EXCEEDED + I-20 발동.

---

### IT-D1-D-01: C → D 에스컬레이션 수신

**Given**: C-1 (또는 C-2/C-3) 가 FAIL 후 I-20 통해 D-1 재검증 요청.
- `EscalationPayload(source_engine="C-1", error_code="VRE_ENGINE_FAILURE", original_request=LogicVerifyRequest(...), partial_result=..., confidence=0.3, trace_id="trace-X", ...)`

**When**: D-1 가 ReasoningRequest 로 변환 후 `reason()` 실행.

**Then**:
- D-1 `reason()` PASS → `ThinkResult(confidence=0.85, verdict="PASS")`
- I-20 가 결과를 C-1 호출자에게 반환 (escalation_flow §3.1)
- trace_id "trace-X" 유지 (orange_core_integration §3.2 단일결정 원칙)
- D-1 EngineState: IDLE → ANALYZING → REASONING → EVALUATING → COMPLETE.

**판정 기준**: D-1 PASS + trace_id 유지 + state 전이.

---

### IT-D1-E-01: Layer 1 LLM Failover — GPT-4o 3회 timeout → Claude Sonnet

**Given**: D-1 가 GPT-4o 호출, GPT-4o 가 연속 3회 timeout (LOCK-VR-12 ≤10s 초과).

**When**: I-20 가 Brain Adapter 통해 Layer 1 Failover 발동 (LOCK-VR-07).

**Then**:
- Claude Sonnet 으로 전환 (escalation_flow §3.2 / orange_core_integration §6.4)
- `OC_I20_BRAIN_TIMEOUT` 이벤트 발행 (escalation_flow §7)
- `BRAIN_FAILOVER` LogEvent (D2.0-02 §11.1.2 정본)
- trace_id 유지
- Claude Sonnet 응답으로 `ThinkResult` 반환.

**판정 기준**: Failover 발동 + trace_id 유지 + Claude 응답.

---

### IT-D1-E-02: Layer 1 Failover Chain 전부 소진 → HITL

**Given**: GPT-4o → Claude → Ollama 전부 실패.

**When**: Fallback Chain 전부 소진 후 I-20 → HITL.

**Then**:
- `OC_I20_BRAIN_EXHAUSTED` (escalation_flow §7)
- HITL 사용자 판단 결과 반환
- ESC-1 (HIGH) 큐 우선 처리 (escalation_flow §4.1).

**판정 기준**: HITL 호출 + EXHAUSTED 이벤트.

---

### IT-D1-F-01: verify.chain_used 추적

**Given**: IT-D1-A-01 PASS 완료.

**When**: ORANGE CORE Decision 후처리.

**Then**:
- `Decision.verify.chain_used` append `"think_reasoning_check"`
- `Decision.verify.refs.reasoning_trace_id` 기록 (orange_core_integration §5.4)
- D2.0-02 §10.5.2 패턴 준수.

**판정 기준**: chain_used + refs.

> Phase 1 이연: `"think_reasoning_check"` 명칭 ORANGE CORE 컨펌 → [CONFLICT_CANDIDATE: chain_used naming awaiting ORANGE CORE owner confirm].

---

### IT-D1-G-01: Event-Logging oc.i1~i5

**Given**: IT-D1-A-01~04 + IT-D1-D-01 + IT-D1-E-01~02 시나리오.

**When**: reason() 진입/종료 + Failover 시점에 6-12 Event-Logging 호출.

**Then**:
- `oc.i1` (REQUEST_RECEIVED), `oc.i4` (REASONING_COMPLETED) 등 발행
- `BRAIN_FAILOVER` (D2.0-02 §11.1.2 정본 LogEvent) 발행
- payload: `trace_id`, `engine="D-1"`, `strategy_used`, `current_depth`, `tokens_consumed`, `confidence`, `failed_brain?`, `next_brain?`.

**판정 기준**: 이벤트 누적 + BRAIN_FAILOVER 정확 발행.

---

## 6. 엔진 간 연동 매트릭스

| 시나리오 | D-1 | I-20 | Brain Adapter | C-* | HITL | 6-12 |
|---------|-----|------|--------------|-----|------|------|
| IT-D1-A-01~04 | ✅ | — | (LLM 호출) | — | — | ✅ |
| IT-D1-B-01 | ✅ | — | — | — | — | ✅ |
| IT-D1-C-01 | ✅ | — | — | — | — | ✅ |
| IT-D1-C-02 | ✅ | ✅ | (Failover) | — | (조건) | ✅ |
| IT-D1-D-01 | ✅ | ✅ | — | ✅ | — | ✅ |
| IT-D1-E-01 | ✅ | ✅ | ✅ | — | — | ✅ |
| IT-D1-E-02 | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| IT-D1-F-01 | ✅ | — | — | — | — | ✅ |
| IT-D1-G-01 | ✅ | (조건) | (조건) | — | (조건) | ✅ |

---

## 7. 검증 체크리스트 (G2-2 기여)

- [x] 시나리오 ≥ 10건: **12건**
- [x] Given-When-Then + 기대 + 판정
- [x] 엔진 간 연동 (C → D 수신): IT-D1-D-01
- [x] Layer 1 LLM Failover (LOCK-VR-07): IT-D1-E-01, E-02
- [x] verify.chain_used: IT-D1-F-01
- [x] 6-12 Event-Logging oc.i1~i5 + BRAIN_FAILOVER: IT-D1-G-01
- [x] LOCK 정본 인용 (VR-04/05/07/08/11/12)
- [x] LOCK-VR-07 Failover Chain: IT-D1-E-01, E-02
- [x] Phase 1 이연 "통합 테스트 시나리오" 해소
- [x] Phase 1 이연 "verify.chain_used 명칭" 반영
- [N/A] 6-2 OWASP LLM01/LLM02: D-1 직접 미해당
- [N/A] LOCK-VR-15 sandbox: D-1 미해당

---

## 8. Phase 3 이연

| 항목 | 사유 | 후속 |
|------|------|------|
| 실 LLM 모델 정확도 | 실 환경 + 데이터셋 필요 | Phase 3 / 5-1 Benchmark |
| chain_used 명칭 컨펌 | D2.0-02 owner | [CONFLICT_CANDIDATE] |
| Brain Adapter 인터페이스 정합 | 6-9 Brain-Adapter-HAL | 6-9 도메인 cross-handoff |
| oc.i1~i5 정본 ID | 6-12 정본 합의 | 6-12 Phase 2 |

---

## 변경 이력

| 버전 | 날짜 | 변경 | 작성자 |
|------|------|------|--------|
| v1.0 | 2026-04-18 | V2-Phase 2 초안 — P2-6, 12건 시나리오, LOCK-VR-07 Failover Chain 핵심 | P2-6 |
| v1.0.1 | 2026-04-18 | P2-6 step 2 reverify — §2.5.4 LOCK-VR-12 본문 "단순/복합" 약식 표기 → AUTHORITY_CHAIN.md §4 정본 (단일응답 ≤2s / 복합응답 ≤10s / Self-check ≤1s) 1:1 일치 | P2-6 reverify |
