# C-1 Logic Verifier — Integration Test Spec (L3)

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
| `01_logic-verifier/spec.md` (P1-1, V1) | §3 LogicVerifyRequest, §4 LogicVerifyResult, §5 4-Phase | 입출력 / 알고리즘 시나리오 기초 데이터 |
| `01_logic-verifier/error_handling.md` (P1-9, V1) | §4.1 트리거, §5.1 에러 코드 | 예외 시나리오 |
| `06_dependency-graph/escalation_flow.md` (P1-11, V1) | §2.2 C-1 트리거, §3.1 체인, §5.1 매핑 | C → I-20 → D-1 흐름 |
| `06_dependency-graph/orange_core_integration.md` (P1-12, V1) | §5.4 chain_used, §3 State Machine | verify.chain_used 추적 |
| `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §10.5.2 verify.chain_used | 정본 명칭 컨펌 |
| `00_common/confidence_thresholds.md` (P0-7, V1) | LOCK-VR-05 | PASS/REVIEW/FAIL 판정 |
| `AUTHORITY_CHAIN.md` §4 | LOCK-VR-04, LOCK-VR-05, LOCK-VR-07 (간접), LOCK-VR-11, LOCK-VR-12 | LOCK 정본 인용 |
| **6-2 Security-Governance** (READ-only) | OWASP LLM01/LLM02 | C-1 단독에는 직접 적용 미해당 (C-3로 위임), 본 문서는 참조만 |
| **6-12 Event-Logging** (READ-only) | oc.i1~i5 (BRAIN/VERIFY 이벤트) | 전 시나리오 검증 항목으로 포함 |

---

## 1.R Verify Chain LOCK-VR-06 + 6-11 ORANGE CORE cross-ref (RECOVERY Sub-B P4-7, 2026-06-02)

> **근거**: CONFLICT_LOG CONF-VRE-007 RESOLVED (RECOVERY Sub-A P4-5, 2026-06-02)의 물리 반영. 본 절은 (1) `verify.chain_used` per-engine check-type identifier 정본 명칭 정합, (2) LOCK-VR-06 Verify Chain 4조건 인용, (3) 6-11 ORANGE CORE 양방향 cross-ref를 명시한다.

### 1.R.1 per-engine check-type identifier 정본 (V1 명칭 정합)

| 항목 | 정본 값 | 출처 |
|------|---------|------|
| C-1 Logic Verifier `verify.chain_used` 추가 식별자 | `"logic_verify_check"` | 1-1 per-engine check-type identifier 정본 (CONF-VRE-007 RESOLVED, TYPE-D) |
| 6-11 carrier 필드 | `Decision.verify.chain_used` (list[str]) | ORANGE CORE D2.0-02 §10.5.2 정본 carrier |

> **명칭 정합 확정**: 본 통합 테스트 시나리오 IT-C1-D-01 (chain_used 추적)에서 사용하는 `"logic_verify_check"` 는 C-1 Logic Verifier의 per-engine check-type identifier 정본이며, 6-11 ORANGE CORE의 `verify.chain_used` carrier 필드가 이를 **값으로 수용**한다 (TYPE-D: ORANGE CORE carrier 정본 우선 + 1-1 per-engine 명칭 정본). CONF-VRE-007은 RECOVERY Sub-A P4-5에서 RESOLVED (OPEN=0) 정식 마킹되었고, 본 P4-7은 그 물리 반영이다.

### 1.R.2 LOCK-VR-06 Verify Chain 4조건 (인용)

> **LOCK (D2.0-02 §10.1/§10.3 + AUTHORITY_CHAIN §3.4 LOCK-VR-06)**: Verify Chain = **Default OFF + timeboxed + cost limit + approval**
> - **Default OFF**: Verify Chain은 기본 비활성 — 자동 ON 금지 (§10.3)
> - **timeboxed**: 체인 실행은 타임박스 내로 제한 (§10.1)
> - **cost limit**: 비용 상한 적용 (§10.1)
> - **approval**: 활성화 시 승인 필요 (§10.3)

본 C-1 Logic Verifier의 chain_used 기록은 위 4조건을 준수하는 Verify Chain 활성 구간에서만 발생하며, Default OFF 상태에서는 `verify.chain_used`에 `"logic_verify_check"`가 추가되지 않는다.

### 1.R.3 6-11 ORANGE CORE 양방향 cross-ref

| 방향 | 내용 | 상태 |
|------|------|------|
| 1-1 → 6-11 | C-1 Logic Verifier `"logic_verify_check"` per-engine identifier 정본 제공 | DEFINED-HERE (1-1 정본) |
| 6-11 → 1-1 | `Decision.verify.chain_used` carrier가 `"logic_verify_check"` 수용 + Pipeline S5→S6 기록 | CITE-ONLY (6-11 ORANGE CORE 정본 carrier, D2.0-02 §10.5.2) |

> **6-11 진입 시 양방향 확정 forward-defined**: 6-11 Hologram-Main-LLM은 Wave 3 #28 미진입 상태이므로, 본 cross-ref는 1-1 측 정본을 확립하고 6-11 진입 시 양방향 최종 확정한다. 6-11 plan baseline 0 touch (외부 도메인 자체 진행). CROSS_HANDOFF_DRIFT NOT FIRED.

---

## 2. 범위 (Purpose / Scope)

본 문서는 C-1 Logic Verifier의 **Integration Test Spec(L3)** 으로, Phase 3에서 실행할 통합 테스트 시나리오를 Given-When-Then 형식으로 정의한다. **단위 테스트(unit)** 와 **순수 부하 테스트(load)** 는 범위 외 (각각 `unit_test_plan.md`, `performance_benchmark.md`에서 다룸).

**범위 포함**:
- C-1 단독 통합 시나리오 (명제 유형 / 엣지 / 에스컬레이션 수신 / chain_used / Event-Logging) ≥ 10건
- 엔진 간 연동 (C-1 → I-20 → D-1)
- ORANGE CORE 통합 (Pipeline S5→S6, verify.chain_used 기록)

**범위 제외 (Phase 3 이후)**:
- 실제 LLM 호출 부하 측정 (G3-x)
- 실 운영 환경 카오스 테스트
- 사용자 수용 테스트(UAT)

---

## 3. LOCK 정본 인용 (AUTHORITY_CHAIN.md §4)

> LOCK-VR-04 (D2.0-02 §2.2): S0~S8 (S3 Decision Lock immutable)
> LOCK-VR-05 (상세명세 C-1 §4): ≥0.8 PASS / 0.5~0.8 REVIEW / <0.5 FAIL
> LOCK-VR-07 (D2.0-02 §11.1.2): GPT-4o → Claude Sonnet → Ollama [scope: 1-1 추론 엔진 전용 — C-1 직접 미해당, 에스컬레이션 후 D-1 경로에 적용]
> LOCK-VR-11 (상세명세 C-1 §3): ABC 패턴 Ask→Bridge→Confirm
> LOCK-VR-12 (D2.0-02 §2.3-B): 단일응답 ≤2s / 복합응답 ≤10s / Self-check ≤1s

C-1 직접 적용: **VR-04 / VR-05 / VR-11 / VR-12**.
간접 적용 (에스컬레이션 후 D-1): VR-07.
C-1 미해당: VR-08(C-2 token 계측) / VR-15(C-3 sandbox).

---

## 4. 시나리오 식별 체계

| 카테고리 | 시나리오 ID 범위 | 건수 |
|---------|----------------|------|
| A. 명제 유형 (단순/중첩/모순/불완전) | IT-C1-A-01 ~ IT-C1-A-04 | 4 |
| B. 엣지 (빈입력/초과크기) | IT-C1-B-01 ~ IT-C1-B-02 | 2 |
| C. 에스컬레이션 수신 (REVIEW/FAIL → I-20 → D-1) | IT-C1-C-01 ~ IT-C1-C-02 | 2 |
| D. chain_used 추적 | IT-C1-D-01 | 1 |
| E. Event-Logging (oc.i1~i5) | IT-C1-E-01 | 1 |
| F. SLA / LOCK-VR-12 boundary | IT-C1-F-01 | 1 |
| **합계** | | **11** |

---

## 5. 시나리오 (Given-When-Then)

### IT-C1-A-01: 단순 명제 — 직접 entailment

**Given**:
- `LogicVerifyRequest(claim="The sky is blue", context=["Observation: blue sky at noon."], timeout_ms=2000, request_id="t-c1-a01", verification_depth="standard")`
- C-1 ABC `verify()` 진입, EngineState=IDLE.

**When**: ORANGE CORE Pipeline S5→S6에서 `verify(req)` 호출.

**Then**:
- `result.details["judgment"] == "PASS"`
- `result.confidence ≥ 0.8` (LOCK-VR-05 PASS)
- `should_escalate(result) == False`
- 응답 시간 ≤ 1,000ms (orange_core_integration §6.3 단순 검증 budget)

**판정 기준**: 위 4개 조건 모두 충족 → PASS. 1개라도 미달 → FAIL.

---

### IT-C1-A-02: 중첩 명제 — 다단계 함의 체인

**Given**:
- `claim="∴ All Athenians are mortal"`, `context=["All men are mortal", "Socrates is a man", "All Athenians are men"]`, `verification_depth="deep"`, `timeout_ms=5000`
- `reasoning_chain=[ReasoningStep(...) × 3]`

**When**: `verify(req)` 호출, Phase 1~4 전체 실행.

**Then**:
- `result.details["judgment"] == "PASS"`, `confidence ≥ 0.8`
- `result.evidence` 에 3-step 추론 경로 기록
- ORANGE CORE 호출자가 `verify.chain_used` 에 `"logic_verify_check"` 추가 가능 상태 (refs.logic_verify_id 존재)

**판정 기준**: verdict + confidence + evidence 길이 ≥ 3 step.

---

### IT-C1-A-03: 모순 명제 — 직접 충돌

**Given**: `claim="X is mortal"`, `context=["X is immortal", "X is a god"]`.

**When**: `verify(req)`.

**Then**:
- `result.details["judgment"] == "FAIL"`, `confidence < 0.5`
- `error_codes` 에 모순 탐지 신호 (C1 도메인 — `C1_FALLACY_DETECTION_ERR` LOW 또는 정상 FAIL 판정)
- `should_escalate(result) == True` (LOCK-VR-05 FAIL → 자동 에스컬레이션)
- I-20 호출 트리거 발동 (escalation_flow §2.1 T-C-1).

**판정 기준**: FAIL 판정 + should_escalate True.

---

### IT-C1-A-04: 불완전 명제 — 정보 부족

**Given**: `claim="Tomorrow will rain"`, `context=["No weather data available."]`.

**When**: `verify(req)`.

**Then**:
- `0.5 ≤ confidence < 0.8` (REVIEW)
- `result.details["judgment"] == "REVIEW"`
- `should_escalate(result) == True` (REVIEW 구간 — escalation_flow §2.1 T-C-2)
- I-19 승인 요청 + I-20 에스컬레이션 **동시 병행** (판정-에스컬레이션 독립 원칙).

**판정 기준**: REVIEW + 두 병행 호출 모두 발동.

---

### IT-C1-B-01: 엣지 — 빈 context

**Given**: `claim="Anything"`, `context=[]` → Pydantic 검증에서 `min_length=1` 위반.

**When**: `verify(req)` 호출 시도.

**Then**:
- Pydantic `ValidationError` 또는 `VRE_INVALID_INPUT` 에러 반환
- `should_escalate` 미호출 (즉시 에러 반환, error_handling §4.1)
- 호출자 측 에러 핸들러가 사용자에게 "context required" 메시지 노출.

**판정 기준**: ValidationError 발생 + 에스컬레이션 미발동.

---

### IT-C1-B-02: 엣지 — claim 초과 크기 (>10000자)

**Given**: `claim="A" × 10001`, `context=["valid"]`.

**When**: `verify(req)`.

**Then**:
- Pydantic `max_length=10000` 위반 → `ValidationError`
- `C1_PARSE_FAILURE` 변환 가능 (error_handling §5.1)
- recoverable=False → 즉시 에러 반환.

**판정 기준**: ValidationError + 재시도 없음.

---

### IT-C1-C-01: 에스컬레이션 수신 → D-1 재검증 성공

**Given**:
- 모순 명제 (IT-C1-A-03 와 동일) 입력으로 `verdict="FAIL", confidence=0.3` 산출 후 I-20에 EscalationPayload 전달.
- `EscalationPayload(source_engine="C-1", error_code="VRE_ENGINE_FAILURE", original_request=..., partial_result=..., retry_count=0, confidence=0.3, trace_id="trace-001", timestamp=...)`

**When**: I-20 가 D-1 `reason()` 호출.

**Then**:
- D-1 가 새 `ReasoningResult(confidence=0.85, verdict="PASS")` 반환
- I-20 가 결과를 C-1 호출자에게 returnsleeting (escalation_flow §3.1)
- 원래 FAIL 결과 → **D-1 결과로 대체**
- trace_id "trace-001" 유지 (orange_core_integration §3.2).

**판정 기준**: D-1 결과 반환 + trace_id 유지 + 원래 FAIL 대체.

---

### IT-C1-C-02: 에스컬레이션 수신 → D-1 실패 → HITL

**Given**: 위와 동일하나 D-1 `reason()` 도 `confidence=0.4` (FAIL) 반환.

**When**: I-20 가 HITL 경로로 전환.

**Then**:
- `OC_I20_BRAIN_EXHAUSTED` (제안) 또는 `OC_I20_ESCALATION_FAIL` 발동 (escalation_flow §7)
- HITL 사용자 판단 결과 수신 후 호출자에 반환
- ESC-1 (HIGH) 우선순위 큐에 배치 (escalation_flow §4.1).

**판정 기준**: HITL 호출 발동 + ESC-1 큐 진입.

---

### IT-C1-D-01: verify.chain_used 추적

**Given**: IT-C1-A-01 PASS 시나리오 완료 후 ORANGE CORE Decision 객체.

**When**: ORANGE CORE 가 Decision 후처리에서 verify.chain_used 갱신.

**Then**:
- `Decision.verify.chain_used` 에 `"logic_verify_check"` 항목 append 가능 (orange_core_integration §5.4)
- `Decision.verify.refs.logic_verify_id` 에 본 verify 호출 ID 기록
- D2.0-02 §10.5.2 LOCK 패턴 준수: append-only, 기존 항목 변경 금지 (LOCK-VR-10 단일결정 원칙).

**판정 기준**: chain_used append 성공 + refs 기록.

> **Phase 1 이연 (P1-12 §9)**: `verify.chain_used` 항목 명칭 ORANGE CORE 컨펌 — 본 시나리오에서 `"logic_verify_check"` 명칭이 D2.0-02 §10.5.2 패턴(`*_check` suffix)을 따름을 확인. ORANGE CORE 소유자 컨펌은 [CONFLICT_CANDIDATE: chain_used naming awaiting ORANGE CORE owner confirm] 으로 보고.

---

### IT-C1-E-01: Event-Logging oc.i1~i5 퍼블리싱

**Given**: IT-C1-A-01 ~ A-04 4건 시나리오 순차 실행, 6-12 Event-Logging 구독자 활성.

**When**: 각 시나리오에서 verify() 진입/종료 시 Event-Logging 인터페이스 호출.

**Then**:
- 진입 시 `oc.i1` (REQUEST_RECEIVED) 또는 도메인별 정의 이벤트 발행
- 정상 종료 시 `oc.i4` (VERIFY_COMPLETED) 발행 (정확한 이벤트 ID는 6-12 정본 참조)
- 에스컬레이션 시 `oc.i5` (ESCALATION_TRIGGERED) 발행
- 모든 이벤트 페이로드에 `trace_id`, `engine="C-1"`, `confidence`, `verdict`, `timestamp` 포함.

**판정 기준**: 이벤트 4건 (각 시나리오당 진입+종료) + 에스컬레이션 시 추가 이벤트.

> 6-12 Event-Logging 정본 (`6-12_Event-Logging`) Read-only 참조. oc.i1~i5 정확한 ID/페이로드 스키마는 6-12 도메인 산출물에 따름.

---

### IT-C1-F-01: SLA boundary — LOCK-VR-12 단일응답 ≤2s

**Given**: 100개 단순 명제(IT-C1-A-01 패턴) 동시 입력.

**When**: ORANGE CORE Pipeline 가 100건 verify() 병렬 호출.

**Then**:
- 95% 시나리오에서 응답시간 ≤ 1,000ms (orange_core_integration §6.3 budget)
- 99% 시나리오에서 응답시간 ≤ 2,000ms (LOCK-VR-12 단일응답 SLA)
- 초과 시 `VRE_TIMEOUT` (recoverable=True) 발동, error_handling §5.1 의 `verdict="TIMEOUT"` 마킹 후 체인 계속 (orange_core_integration §5.3).

**판정 기준**: P95 ≤ 1,000ms AND P99 ≤ 2,000ms.

---

## 6. 엔진 간 연동 매트릭스

| 시나리오 | C-1 | I-20 | D-1 | HITL | 6-12 Event |
|---------|-----|------|-----|------|-----------|
| IT-C1-A-01~04 | ✅ | — | — | — | ✅ |
| IT-C1-B-01~02 | ✅ | — | — | — | ✅ |
| IT-C1-C-01 | ✅ | ✅ | ✅ | — | ✅ |
| IT-C1-C-02 | ✅ | ✅ | ✅ | ✅ | ✅ |
| IT-C1-D-01 | ✅ | — | — | — | ✅ |
| IT-C1-E-01 | ✅ | — | — | — | ✅ |
| IT-C1-F-01 | ✅ | (조건부) | — | — | ✅ |

---

## 7. 검증 체크리스트 (G2-2 기여)

- [x] 엔진당 시나리오 ≥ 10건: **11건**
- [x] Given-When-Then + 기대 결과 + 판정 기준 형식
- [x] 엔진 간 연동 (C-1 → I-20 → D-1): IT-C1-C-01, C-02
- [x] verify.chain_used 추적: IT-C1-D-01
- [x] 6-12 Event-Logging oc.i1~i5: IT-C1-E-01 (전 시나리오 적용)
- [x] LOCK 정본 인용 §3 (AUTHORITY_CHAIN.md 직접 Read 후 1:1 매칭)
- [x] Phase 1 이연 항목 "통합 테스트 시나리오" 해소
- [x] Phase 1 이연 항목 "verify.chain_used 명칭 ORANGE CORE 컨펌" 반영 (IT-C1-D-01 + CONFLICT_CANDIDATE)
- [N/A] 6-2 OWASP LLM01/LLM02: C-1 직접 미해당 (C-3에 적용)
- [N/A] LOCK-VR-15 sandbox: C-1 미해당
- [N/A] LOCK-VR-08 token 계측: C-1 미해당

---

## 8. Phase 3 이연 / 후속 작업

| 항목 | 이연 사유 | 후속 |
|------|----------|------|
| 실측 응답시간 측정 | 실 LLM 환경 필요 | Phase 3 G3-x performance benchmark |
| chain_used 명칭 ORANGE CORE 컨펌 | D2.0-02 §10.5.2 owner 결정 필요 | [CONFLICT_CANDIDATE] 보고 후 사람 확정 |
| oc.i1~i5 정확한 ID/payload | 6-12 정본 합의 후 확정 | 6-12 Event-Logging Phase 2 산출물 참조 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0 | 2026-04-18 | V2-Phase 2 초안 — P2-6 G2-2 기여, 11건 시나리오, LOCK-VR-04/05/07/11/12 인용, chain_used 추적, oc.i1~i5 검증 | P2-6 |
| v1.0.1 | 2026-04-18 | P2-6 step 2 reverify — §2.5.4 LOCK-VR-12 본문 "단순응답"→"단일응답" 정본 일치 (AUTHORITY_CHAIN.md §4), §1 교차 참조 LOCK 목록에 VR-07 (간접) 추가 | P2-6 reverify |
