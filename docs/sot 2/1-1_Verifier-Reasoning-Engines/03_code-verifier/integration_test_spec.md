# C-3 Code Verifier — Integration Test Spec (L3)

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
| `03_code-verifier/spec.md` (P1-3, V1) | I/O Schema, 4-Phase | 시나리오 기초 |
| `03_code-verifier/error_handling.md` (P1-9, V1) | §4.1, §5.3 | 예외 시나리오 |
| `03_code-verifier/security_rules.md` (P1-3 부록, V1) | OWASP 매핑 | 보안 시나리오 |
| `06_dependency-graph/escalation_flow.md` (P1-11, V1) | §2.4, §5.3 | C-3 → I-20 → D-1 |
| `06_dependency-graph/orange_core_integration.md` (P1-12, V1) | §5.4 | code_verify_check, sandbox_run_id |
| `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §10.5.2, §10.2 LOCK | chain_used + sandbox 정본 |
| `AUTHORITY_CHAIN.md` §4 | LOCK-VR-04/05/11/12/15 | LOCK 정본 |
| **6-2 Security-Governance** (READ-only) | OWASP LLM01 (Prompt Injection), LLM02 (Insecure Output Handling) | 보안 시나리오 |
| **6-12 Event-Logging** (READ-only) | oc.i1~i5 | 이벤트 검증 |

---

## 1.R Verify Chain LOCK-VR-06 + 6-11 ORANGE CORE cross-ref (RECOVERY Sub-B P4-7, 2026-06-02)

> **근거**: CONFLICT_LOG CONF-VRE-009 RESOLVED (RECOVERY Sub-A P4-5, 2026-06-02)의 물리 반영. 본 절은 (1) `verify.chain_used` per-engine check-type identifier 정본 명칭 정합, (2) LOCK-VR-06 Verify Chain 4조건 인용, (3) 6-11 ORANGE CORE 양방향 cross-ref를 명시한다.

### 1.R.1 per-engine check-type identifier 정본 (V1 명칭 정합)

| 항목 | 정본 값 | 출처 |
|------|---------|------|
| C-3 Code Verifier `verify.chain_used` 추가 식별자 | `"code_verify_check"` | 1-1 per-engine check-type identifier 정본 (CONF-VRE-009 RESOLVED, TYPE-D) |
| 6-11 carrier 필드 | `Decision.verify.chain_used` (list[str]) | ORANGE CORE D2.0-02 §10.5.2 정본 carrier |

> **명칭 정합 확정**: 본 통합 테스트 시나리오 IT-C3-F-01 (chain_used 추적)에서 사용하는 `"code_verify_check"` 는 C-3 Code Verifier의 per-engine check-type identifier 정본이며, 6-11 ORANGE CORE의 `verify.chain_used` carrier 필드가 이를 **값으로 수용**한다 (TYPE-D: ORANGE CORE carrier 정본 우선 + 1-1 per-engine 명칭 정본). CONF-VRE-009은 RECOVERY Sub-A P4-5에서 RESOLVED (OPEN=0) 정식 마킹되었고, 본 P4-7은 그 물리 반영이다.

### 1.R.2 LOCK-VR-06 Verify Chain 4조건 (인용)

> **LOCK (D2.0-02 §10.1/§10.3 + AUTHORITY_CHAIN §3.4 LOCK-VR-06)**: Verify Chain = **Default OFF + timeboxed + cost limit + approval**
> - **Default OFF**: Verify Chain은 기본 비활성 — 자동 ON 금지 (§10.3)
> - **timeboxed**: 체인 실행은 타임박스 내로 제한 (§10.1)
> - **cost limit**: 비용 상한 적용 (§10.1)
> - **approval**: 활성화 시 승인 필요 (§10.3)

본 C-3 Code Verifier의 chain_used 기록은 위 4조건을 준수하는 Verify Chain 활성 구간에서만 발생하며, Default OFF 상태에서는 `verify.chain_used`에 `"code_verify_check"`가 추가되지 않는다.

### 1.R.3 6-11 ORANGE CORE 양방향 cross-ref

| 방향 | 내용 | 상태 |
|------|------|------|
| 1-1 → 6-11 | C-3 Code Verifier `"code_verify_check"` per-engine identifier 정본 제공 | DEFINED-HERE (1-1 정본) |
| 6-11 → 1-1 | `Decision.verify.chain_used` carrier가 `"code_verify_check"` 수용 + Pipeline S5→S6 기록 | CITE-ONLY (6-11 ORANGE CORE 정본 carrier, D2.0-02 §10.5.2) |

> **6-11 진입 시 양방향 확정 forward-defined**: 6-11 Hologram-Main-LLM은 Wave 3 #28 미진입 상태이므로, 본 cross-ref는 1-1 측 정본을 확립하고 6-11 진입 시 양방향 최종 확정한다. 6-11 plan baseline 0 touch (외부 도메인 자체 진행). CROSS_HANDOFF_DRIFT NOT FIRED.

---

## 2. 범위 (Purpose / Scope)

C-3 Code Verifier 통합 테스트 시나리오 (L3). Given-When-Then ≥ 10건. **6-2 OWASP LLM01/LLM02 보안 시나리오 포함**.

**범위 포함**: 언어별 (Python/JS/TS/Java/Go/Rust), 보안 (injection/overflow/escape), sandbox boundary, LOCK-VR-15 30s timeout, 에스컬레이션, chain_used, Event-Logging.

**범위 제외**: Docker 인프라 자체의 신뢰성 테스트 (Phase 3 인프라 영역).

---

## 3. LOCK 정본 인용 (AUTHORITY_CHAIN.md §4)

> LOCK-VR-04 (D2.0-02 §2.2): S0~S8 (S3 Decision Lock immutable)
> LOCK-VR-05 (상세명세 C-1 §4): ≥0.8 PASS / 0.5~0.8 REVIEW / <0.5 FAIL
> LOCK-VR-11 (상세명세 C-1 §3): ABC 패턴
> LOCK-VR-12 (D2.0-02 §2.3-B): 단일응답 ≤2s / 복합응답 ≤10s / Self-check ≤1s
> LOCK-VR-15 (D2.0-02 §1.3-A C-3): Docker sandbox, timeout 30s, CPU/RAM 상한은 설정 파일

C-3 직접 적용: **VR-04 / VR-05 / VR-11 / VR-12 / VR-15** (sandbox 30s 핵심).

---

## 4. 시나리오 식별 체계

| 카테고리 | 시나리오 ID 범위 | 건수 |
|---------|----------------|------|
| A. 언어별 (Python/JS/TS/Java/Go/Rust) | IT-C3-A-01 ~ IT-C3-A-06 | 6 |
| B. 보안 — 6-2 OWASP LLM01 (Prompt Injection) | IT-C3-B-01 | 1 |
| C. 보안 — 6-2 OWASP LLM02 (Insecure Output) + Injection/overflow/escape | IT-C3-C-01 ~ IT-C3-C-03 | 3 |
| D. sandbox boundary (LOCK-VR-15 30s timeout) | IT-C3-D-01 ~ IT-C3-D-02 | 2 |
| E. 에스컬레이션 수신 | IT-C3-E-01 | 1 |
| F. chain_used 추적 | IT-C3-F-01 | 1 |
| G. Event-Logging | IT-C3-G-01 | 1 |
| **합계** | | **15** |

---

## 5. 시나리오 (Given-When-Then)

### IT-C3-A-01: Python — 단순 함수

**Given**: `CodeVerifyRequest(code="def add(a,b): return a+b\nassert add(2,3)==5", language="python", timeout_ms=5000)`.

**When**: C-3 `verify(req)`, Docker sandbox에서 실행.

**Then**:
- `verdict="PASS"`, `confidence ≥ 0.8`
- `sandbox_status="success"`, `phases_completed=["parse","static","sandbox","synthesis"]`
- 응답시간 ≤ 5,000ms (orange_core_integration §6.3 C-3 budget).

**판정 기준**: PASS + sandbox 성공.

---

### IT-C3-A-02: JavaScript

**Given**: `code="const f = (a,b)=>a+b; if(f(2,3)!==5) throw 'fail';"`, `language="javascript"`.

**When**: Node sandbox 실행.

**Then**: `verdict="PASS"`, JS 런타임 에러 없음.

**판정 기준**: PASS.

---

### IT-C3-A-03: TypeScript

**Given**: TS 코드 + `tsc --noEmit` 타입 체크, language="typescript".

**When**: 타입 체크 + 변환 + 실행.

**Then**: `verdict="PASS"`, type errors=0.

**판정 기준**: PASS.

---

### IT-C3-A-04: Java

**Given**: Java 클래스 + `main()` + JUnit assertion.

**When**: javac + java 실행.

**Then**: `verdict="PASS"`, JUnit 통과.

**판정 기준**: PASS.

---

### IT-C3-A-05: Go

**Given**: Go 함수 + `_test.go` test file.

**When**: `go test`.

**Then**: `verdict="PASS"`, test pass.

**판정 기준**: PASS.

---

### IT-C3-A-06: Rust

**Given**: Rust 함수 + `#[test]` block.

**When**: `cargo test`.

**Then**: `verdict="PASS"`, test pass.

**판정 기준**: PASS.

---

### IT-C3-B-01: 6-2 OWASP LLM01 — Prompt Injection 시도 코드

**Given**: 코드 내부에 LLM API 호출 + 사용자 입력을 prompt에 그대로 합치는 패턴 (예: `prompt = f"Translate: {user_input}"`). 6-2 OWASP LLM01 정의에 부합.

**When**: C-3 정적분석 (security_rules.md OWASP 매핑) + sandbox 실행 분석.

**Then**:
- `verdict="REVIEW"` 또는 `"FAIL"` (보안 위협 탐지 시)
- `result.security_findings` 에 `OWASP_LLM01_PROMPT_INJECTION` 신호
- `should_escalate=True` (REVIEW 또는 FAIL)
- I-19 보안 승인 요청 + I-20 에스컬레이션 병행
- 6-12 Event-Logging 에 `SECURITY_FINDING` 이벤트 발행.

**판정 기준**: OWASP_LLM01 신호 검출 + REVIEW/FAIL.

> 6-2 Security-Governance 정본 (`6-2_Security-Governance`) Read-only 참조. 정확한 신호 ID/탐지 룰은 6-2 도메인 산출물에 따름.

---

### IT-C3-C-01: 6-2 OWASP LLM02 — Insecure Output Handling

**Given**: LLM 응답을 검증 없이 `eval()` 또는 `exec()` 로 실행하는 코드 패턴. OWASP LLM02 부합.

**When**: 정적분석에서 위험 패턴 탐지.

**Then**:
- `verdict="FAIL"`, `confidence < 0.5`
- `security_findings` 에 `OWASP_LLM02_INSECURE_OUTPUT` 신호
- `SANDBOX_POLICY_DENIED` 가능성 (운영 정책에 따름)
- 자동 거부 + 보안 로그.

**판정 기준**: OWASP_LLM02 검출 + FAIL.

---

### IT-C3-C-02: SQL Injection 패턴

**Given**: `cursor.execute(f"SELECT * FROM users WHERE id={user_id}")` 패턴.

**When**: 정적분석 (Bandit + 자체 룰).

**Then**:
- `verdict="FAIL"` 또는 `"REVIEW"`
- `security_findings` 에 SQL injection 경고.

**판정 기준**: 경고 검출.

---

### IT-C3-C-03: Buffer overflow 시도 (C/C++ 입력)

**Given**: `language="c"`, 고정 크기 buffer 에 사용자 입력 strcpy.

**When**: 정적분석 + sandbox 실행 (메모리 검사).

**Then**:
- 정적분석 경고 + sandbox AddressSanitizer 검출 시 `verdict="FAIL"`
- `security_findings` 에 buffer overflow 신호.

**판정 기준**: 경고 또는 sanitizer 검출.

---

### IT-C3-D-01: sandbox boundary — 정상 30s 직전 종료

**Given**: 코드가 29초 sleep 후 종료. `LOCK-VR-15 timeout=30s`.

**When**: sandbox 실행.

**Then**:
- `verdict="PASS"` (timeout 직전 정상 종료)
- 응답시간 ~ 29s + overhead.

**판정 기준**: 30s 이내 PASS.

---

### IT-C3-D-02: sandbox boundary — 30s 초과 → SANDBOX_TIMEOUT

**Given**: 코드가 60초 sleep, LOCK-VR-15 30s timeout.

**When**: sandbox 실행.

**Then**:
- 30s 시점에 sandbox kill, `error_code="SANDBOX_TIMEOUT"`
- 정적분석 only fallback 시도 (escalation_flow §2.4 T-C3-1)
- confidence 미달 시 I-20 → D-1 재검증
- ESC-1 (HIGH) 큐 (escalation_flow §4.1).

**판정 기준**: 30s 정확 timeout + fallback + I-20 발동.

---

### IT-C3-E-01: 에스컬레이션 수신 — Docker OOM

**Given**: 메모리 폭주 코드 → `SANDBOX_OOM`.

**When**: 메모리 상향 재시도 → 정적분석 only fallback (escalation_flow §2.4 T-C3-2).

**Then**:
- 정적분석 confidence 미달 → I-20 → D-1 재검증
- `EscalationPayload(source_engine="C-3", error_code="SANDBOX_OOM", sandbox_status="oom_killed", phases_completed=["parse","static"], ...)`
- D-1 결과로 대체 또는 HITL.

**판정 기준**: I-20 발동 + payload + D-1 결과.

---

### IT-C3-F-01: verify.chain_used 추적

**Given**: IT-C3-A-01 PASS 후.

**When**: ORANGE CORE Decision 후처리.

**Then**:
- `Decision.verify.chain_used` append `"code_verify_check"`
- `Decision.verify.refs.code_verify_id`, `Decision.verify.refs.sandbox_run_id` 둘 다 기록 (orange_core_integration §5.4)
- D2.0-02 §10.5.2 패턴 준수.

**판정 기준**: chain_used + 2개 refs.

> Phase 1 이연: `"code_verify_check"` 명칭 ORANGE CORE 컨펌 → [CONFLICT_CANDIDATE: chain_used naming awaiting ORANGE CORE owner confirm].

---

### IT-C3-G-01: Event-Logging oc.i1~i5

**Given**: IT-C3-A-01~06 + IT-C3-B-01 + IT-C3-C-01~03 + IT-C3-D-01~02 + IT-C3-E-01 시나리오.

**When**: 각 시나리오 verify() 진입/종료 + 보안 검출 + sandbox 실행 시 6-12 Event-Logging 호출.

**Then**:
- `oc.i1` (REQUEST_RECEIVED), `oc.i4` (VERIFY_COMPLETED), `oc.i5` (ESCALATION_TRIGGERED) 발행
- 보안 시나리오는 추가로 `SECURITY_FINDING` (6-2/6-12 합의 이벤트)
- payload: `trace_id`, `engine="C-3"`, `language`, `sandbox_status`, `phases_completed`, `security_findings?`.

**판정 기준**: 이벤트 누적 ≥ 30건 (15 시나리오 × 평균 2 + 보안 추가).

---

## 6. 엔진 간 연동 매트릭스

| 시나리오 | C-3 | I-20 | D-1 | I-19 | HITL | 6-2 | 6-12 |
|---------|-----|------|-----|------|------|-----|------|
| IT-C3-A-01~06 | ✅ | — | — | — | — | — | ✅ |
| IT-C3-B-01 | ✅ | ✅ | (조건) | ✅ | (조건) | ✅ | ✅ |
| IT-C3-C-01~03 | ✅ | (조건) | (조건) | (조건) | — | ✅ | ✅ |
| IT-C3-D-01 | ✅ | — | — | — | — | — | ✅ |
| IT-C3-D-02 | ✅ | ✅ | ✅ | — | (조건) | — | ✅ |
| IT-C3-E-01 | ✅ | ✅ | ✅ | — | (조건) | — | ✅ |
| IT-C3-F-01 | ✅ | — | — | — | — | — | ✅ |
| IT-C3-G-01 | ✅ | (조건) | — | — | — | (조건) | ✅ |

---

## 7. 검증 체크리스트 (G2-2 기여)

- [x] 시나리오 ≥ 10건: **15건**
- [x] Given-When-Then + 기대 + 판정
- [x] 엔진 간 연동 (C-3 → I-20 → D-1): IT-C3-D-02, E-01
- [x] verify.chain_used: IT-C3-F-01 (refs 2개)
- [x] 6-2 Security-Governance OWASP LLM01: IT-C3-B-01
- [x] 6-2 Security-Governance OWASP LLM02: IT-C3-C-01
- [x] 6-12 Event-Logging oc.i1~i5: IT-C3-G-01
- [x] LOCK-VR-15 30s sandbox: IT-C3-D-01, D-02
- [x] LOCK 정본 인용 (VR-04/05/11/12/15)
- [x] Phase 1 이연 "통합 테스트 시나리오" 해소
- [x] Phase 1 이연 "verify.chain_used 명칭" 반영
- [N/A] LOCK-VR-08 tiktoken: C-3 직접 미해당

---

## 8. Phase 3 이연

| 항목 | 사유 | 후속 |
|------|------|------|
| 실 Docker 인프라 신뢰성 | 인프라 환경 필요 | Phase 3 / 4-1 Rust-Tauri |
| OWASP 신호 ID 정합 | 6-2 정본 합의 | 6-2 Phase 2 |
| chain_used 명칭 컨펌 | D2.0-02 owner | [CONFLICT_CANDIDATE] |
| oc.i1~i5 정본 ID | 6-12 정본 합의 | 6-12 Phase 2 |
| LOCK-VR-15 CPU/RAM 상한 | "설정 파일로 관리" — 운영 결정 | Phase 3 운영 결정 |

---

## 변경 이력

| 버전 | 날짜 | 변경 | 작성자 |
|------|------|------|--------|
| v1.0 | 2026-04-18 | V2-Phase 2 초안 — P2-6, 15건 시나리오, OWASP LLM01/LLM02 + LOCK-VR-15 sandbox 30s | P2-6 |
| v1.0.1 | 2026-04-18 | P2-6 step 2 reverify — §2.5.4 LOCK-VR-12 본문 "단순/복합" 약식 표기 → AUTHORITY_CHAIN.md §4 정본 (단일응답 ≤2s / 복합응답 ≤10s / Self-check ≤1s) 1:1 일치 | P2-6 reverify |
