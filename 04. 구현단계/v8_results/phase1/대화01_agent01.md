# [Agent 1] 검증 결과 — 코어 아키텍처 + 파이프라인

> **검증 일시**: 2026-03-04
> **PART2 버전**: v18.0.0 | **v8 프롬프트**: v8.1.0
> **검증 방법**: STEP A (순방향) + STEP B (역방향)

---

## 읽은 파일 (실제 읽은 수 / 할당 수: 6/6)

- [x] VAMOS_구현가이드_PART2_구현단계.md (1821행) — 전수 열독
- [x] D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md (1857행) — 전수 열독
- [x] D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md (4474행) — §7, §8.1, §11.12, C3 템플릿 중심 열독
- [x] D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md (1982행) — 전수 열독
- [x] D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md (2696행) — 전수 열독
- [x] CLAUDE.md (697행) — 전수 열독
- [x] 0-D.json (80 entries) — 전수 활용

---

## 검사 통계

- **Dim B** Forward: 20 / MATCH: 13 / MISMATCH: 3 (B-05, B-07, B-09) / NO_SOURCE: 4 (B-01~B-04) / Reverse MISSING: 3 (총 23 체크)
- **Dim C** Facts checked: 27 / IMP_OK: 16 / IMP_IMPOSSIBLE: 0 / IMP_MISSING: 8 / IMP_CONFLICT: 3

> **주**: v8 §5 Agent 1 Dim B "4-Layer 명칭 (5항목)"의 기대값 "Application/Domain/Infrastructure/External — D2.0-01 §5.3"이 D2.0-01 어디에도 존재하지 않음. D2.0-01 §2의 실제 4-Layer는 "ORANGE CORE/BLUE NODE/OTHER BRAINS/STORAGE". v8의 "(5항목)"과 "§5.3" 참조는 오기재로 판단하여 B-01~B-04 (4건 NO_SOURCE)로 기록. B-05는 EvidencePack 출처 오류(MISMATCH)로 별도 등록.

---

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MATCH (13건)

| # | 항목 | PART2 값 | SRC 값 | 원본 출처 |
|---|------|---------|--------|----------|
| B-06 | 5-Phase LOCK 순서 | Intake→Plan→Execute→Verify→Deliver (L492) | Perception/Intake→Reasoning/Plan→Action/Execute→Reflection/Verify→Memory/Store (LOCK) | CLAUDE.md L70-78 |
| B-08 | 5-Gate 명칭 | Policy/Cost/Approval/Evidence/SelfCheck (L571) | PolicyGate/CostGate/ApprovalGate/EvidenceGate/SelfCheckGate | CLAUDE.md L83-88 |
| B-10 | 5-Gate bypass LOCK | Gate를 필수 파이프라인 노드로 구현 (L493,541) | "우회 불가, LOCK" (L80) | CLAUDE.md L80 |
| B-11 | Circuit Breaker 60s | recovery_time_sec=60 (D2.0-05 §4.4 LOCK) (L495) | OPEN 유지 시간 기본값 60초, 임계값 규칙(LOCK) (L175-177) | D2.0-05 §4.4 |
| B-12 | 모듈 총수 81개 | V3=81 (L44) | I=25+S=8+E=16+A=7+B=6+C=7+D=6+EVX=6=81 | D2.0-01 §5.6~§5.13 |
| B-13 | V0=5 | V0=5 (L39) | I-1,I-2,I-3,I-5,I-19 활성 (나머지 stub) | D2.0-01 §5.6 |
| B-14 | V1=32 | V1=32 (L41) | CORE 17(I) + S/E/A/B/C/D/EVX CORE 합계 = 32 | D2.0-01 §5.6~§5.13 |
| B-15 | V2=42 | V2=42 (L42) | V1(32) + COND 모듈 활성화 (+10) = 42 | D2.0-01 §5.6~§5.13 |
| B-16 | V3=81 | V3=81 (L44) | 전체 모듈 활성 (EXP 포함) = 81 | D2.0-01 §5.6~§5.13 |
| B-17 | V0 스텁 I-8/I-9/I-20 | I-8(Policy),I-9(Cost),I-20(Failure/Fallback) stub (L60,336) | I-8/I-9/I-20 stub 정의 | D2.0-02 §7.57-7.62,7.93 |
| B-18 | COND 기본 OFF | "COND 모듈 기본 OFF" (L647) | "COND(status) 모듈/기능은 기본 OFF" (LOCK) (L766) | D2.0-01 §5.14.4 |
| B-19 | Module Status Enum | enum={CORE\|COND\|EXP\|RE-ADD} (L647) | status:{CORE\|COND\|EXP\|RE-ADD} (LOCK) (L565) | D2.0-01 §5.5 |
| B-20 | EvidencePack 필드 수 | 6필드 (L206) | 6 top-level: evidence_pack_id,trace_id,timestamp,items[],coverage,citations_ready | D2.0-02 C3 §출력 |

> **B-06 부연**: CLAUDE.md 5번째 Phase를 "Memory/Store"로 표기하나, CLAUDE.md L355-356에서 "Memory/Reflection은 표준 파이프라인의 Deliver(5) 단계 내부 하위 구간으로 포함"으로 명시. D2.0-05 L514도 "Deliver" 사용. PART2의 "Deliver" 표기는 정합.

---

## Dim B — MISMATCH (3건)

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|---------|---------|--------|----------|----------|
| B-07 | L836-854 | **UI_S0 INIT / UI_S1 IDLE / UI_S2 INPUT_READY / UI_S3 PROCESSING / UI_S4 STREAMING / UI_S5 TOOL_EXECUTING / UI_S6 HITL_PENDING / UI_S7 ERROR / UI_S8 SESSION_END** | **UI_S0_BOOT / UI_S1_IDLE / UI_S2_EDITING / UI_S3_READY / UI_S4_RUNNING / UI_S5_AWAIT_APPROVAL / UI_S6_PRESENTING / UI_S7_RECOVERY / UI_S8_ARCHIVED** | D2.0-08 §4.1 L336-344 | **BLOCKER** |
| B-05 | L206 | EvidencePack 출처: "D2.0-02 **§7.2**" | 실제 위치: D2.0-02 **§7.13**(레거시) 또는 **C3 템플릿** L2692-2703 (정본) | D2.0-02 C3 | **MEDIUM** |
| B-09 | L571 | Gate 나열 순서: Policy/Cost/Approval/Evidence/SelfCheck | Gate 정본 순서: Policy→Approval→Cost→Evidence (CLAUDE.md L232) | CLAUDE.md §7.2 L232 | **LOW** |

### B-07 상세 분석 (BLOCKER)

PART2 §6.1.6 제목에 "D2.0-08 §4 정본"을 명시하면서도, 9개 상태 중 **7개의 이름이 불일치**:

| State | PART2 (§6.1.6) | D2.0-08 §4.1 (정본) | 일치 |
|-------|----------------|---------------------|------|
| S0 | INIT | BOOT | ✗ |
| S1 | IDLE | IDLE | ✓ |
| S2 | INPUT_READY | EDITING | ✗ |
| S3 | PROCESSING | READY | ✗ |
| S4 | STREAMING | RUNNING | ✗ |
| S5 | TOOL_EXECUTING | AWAIT_APPROVAL | ✗ |
| S6 | HITL_PENDING | PRESENTING | ✗ |
| S7 | ERROR | RECOVERY | ✗ |
| S8 | SESSION_END | ARCHIVED | ✗ |

**판정**: PART2가 D2.0-08 §4.1 정본 상태 이름을 따르지 않고 독자적 이름 체계를 사용함. PART2 L856에서 "기존 6-state(UIS1~6) 대비 3개 추가"라 기술하나, D2.0-08 §4.1의 9-state 정본과 명칭이 완전히 다름. **D2.0-08 §4.1이 UI 설계 정본(D2.0-08 L406 확인)이므로, PART2의 상태명을 D2.0-08 §4.1에 맞춰 수정해야 함.**

### B-09 부연 (LOW)

Gate들은 파이프라인의 서로 다른 단계(S1~S6)에서 작동하므로 엄밀한 실행 순서가 아닌 논리적 우선순위 차이. CLAUDE.md L83-88 테이블 순서(Policy→Cost→Approval→Evidence→SelfCheck)와 L232 순서(Policy→Approval→Cost→Evidence)도 상이하여, CLAUDE.md 내부에서도 나열 순서가 일관되지 않음. 실질적 영향 낮음.

---

## Dim B — NO_SOURCE (4건)

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | 판정 |
|---|---------|-----------|----------------|------|
| B-01 | — | "Application" Layer 미기재 | D2.0-01 전문 (§2, §5.3) / PART2 전문 grep "Application" | v8 기대값 "Application/Domain/Infrastructure/External"이 D2.0-01 어디에도 없음. §5.3=Fallback Registry. §2의 4-Layer는 ORANGE CORE/BLUE NODE/OTHER BRAINS/STORAGE. **v8 프롬프트 기대값 또는 section 참조 오류 의심** |
| B-02 | — | "Domain" Layer 미기재 | 동일 | 동일 |
| B-03 | — | "Infrastructure" Layer 미기재 | 동일 | 동일 |
| B-04 | — | "External" Layer 미기재 | 동일 | 동일 |

> **판정 종합**: D2.0-01 §5.3은 "Fallback Registry (degrade_level 포함)"이며 4-Layer 아키텍처와 무관. D2.0-01 §2에 정의된 실제 4-Layer는: **(1) ORANGE CORE** (판단/제어), **(2) BLUE NODES** (도메인 실행), **(3) OTHER BRAINS / INFRA-CORE** (실행 자원), **(4) STORAGE/MEMORY** (저장). "Application/Domain/Infrastructure/External"은 DDD/Clean Architecture 용어로, PHASE_B2 프로젝트 구조에서 사용될 수 있으나 D2.0-01 정본에는 부재. PART2 역시 이 용어를 사용하지 않음. **v8 프롬프트의 기대값 자체를 재확인 필요**.

---

## Dim B — MISSING (역방향 검증, 3건)

| # | 원본 출처 | 누락 내용 | Severity |
|---|----------|----------|----------|
| B-M1 | D2.0-08 §4.5 L388-406 | **9-state↔6-state 양방향 매핑 테이블** — D2.0-08이 정의한 §4.1(9-state) ↔ §4.4(6-state) 매핑이 PART2에 반영되지 않음. PART2는 독자적 9-state를 사용하여 매핑 자체가 불가 | **HIGH** |
| B-M2 | D2.0-08 §4.6 L407-421 | **Pipeline S0~S8 ↔ UI State 크로스 매핑** — D2.0-08이 정의한 파이프라인 상태(S0~S8)→UI 상태 매핑이 PART2에 부재. 구현 시 파이프라인 상태와 UI 상태 동기화 근거 부족 | **HIGH** |
| B-M3 | D2.0-02 C3 템플릿 L2606 | **VamosState 필드 정의** — PART2 L324에서 `StateGraph(VamosState)` 사용하나 VamosState의 필드 목록이 PART2에 미기재. 구현자가 어떤 필드를 포함해야 하는지 알 수 없음. *(C-16과 동일 이슈 — Dim B 역방향 관점)* | **HIGH** |

---

## Dim B — SOURCE_CONFLICT (2건)

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|-----------------|
| SC-1 | D2.0-05 §4.4 LOCK: recovery_time=**60초** | D2.1-D5/D7 스키마: recovery_time=**300초** | D2.0-05 LOCK > Schema. **60초 채택** (PART2 L495 HTML 주석에 이미 기록됨) |
| SC-2 | CLAUDE.md L83-88: Gate 테이블 순서=Policy→Cost→Approval→Evidence→SelfCheck | CLAUDE.md L232: Gate 정본 순서=Policy→**Approval→Cost**→Evidence | CLAUDE.md 내부 불일치. L232가 §7.2 LOCK 섹션이므로 **Policy→Approval→Cost→Evidence 채택** |

---

## Dim C — IMP_OK (16건 요약)

| # | 항목 | PART2 근거 | 판정 |
|---|------|-----------|------|
| C-01 | 의존성 체인 구조 | §1.2 (L46): V0→V1→V2→V3 필수 순서 | IMP_OK |
| C-02 | 순환 감지 메커니즘 | L931: VAL-003 "모듈 의존성 순환 참조 없음" 검증 항목 | IMP_OK |
| C-03 | V0 의존성 검증 | L293-336: V0 5개 모듈 의존성 없음(I-1→없음) | IMP_OK |
| C-04 | V1 의존성 검증 | L400-424: I-1→I-2→I-15→I-5→I-8/I-19→I-4→I-6→I-3 체인 | IMP_OK |
| C-05 | V2 의존성 검증 | §4: V2 COND 모듈 활성화 순서 기술 | IMP_OK |
| C-07 | LangGraph 노드 매핑 (5-Phase) | L322-334: intake=I-1, plan=I-2+I-5, execute=LLM, verify=stub, deliver=ResponseEnvelope | IMP_OK |
| C-08 | LangGraph 노드 매핑 (Gate 통합) | L493: "LangGraph 노드로 Gate 실행" | IMP_OK |
| C-09 | Lead Agent 구조 | L498,1037,1075: Lead=ORANGE CORE/I-5, Sonnet, 계획/분배/검증만, LOCK-AT-015 직접 실행 금지 | IMP_OK |
| C-10 | Lead Agent LOCK-AT 제약 | L1062,1065,1075: LOCK-AT-002(단일결정), AT-005(Gate 필수), AT-015(직접 실행 금지) | IMP_OK |
| C-17 | 노드 I/O 타입 | L205-206,299,304: IntentFrame(10필드)→EvidencePack(6필드)→Decision→ResponseEnvelope(5필드) 스키마 참조 | IMP_OK |
| C-19 | Circuit Breaker wrapping | L495: CB 3-state + D2.0-05 §4.4 L184-187: Execute(S3~S4)에서 작동, OPEN→Verify(S5) 전이 | IMP_OK |
| C-20 | Gate 상태 전파 | L541: deny/allow/downshift/hold 4경로 정의, L405: I-5 Gate 통합→Decision | IMP_OK |
| C-22 | 병렬 태스크 | L498: V1 max 2 Sub-Agent, L1074: LOCK-AT-014 V1=3/V2=10/V3=50+ | IMP_OK |
| C-23 | Decision.locked 강제 | L405: "Decision Lock", D2.0-08 §4.3: "Decision Lock 이후 결론 변경 UI 제공 금지" | IMP_OK |
| C-24 | ResponseEnvelope 매핑 | L209,329: deliver_node에서 ResponseEnvelope 생성, 5필드 LOCK | IMP_OK |
| C-25 | trace_id 영속성 | L186: trace_id_required=true LOCK, L1067: LOCK-AT-007 trace_id 단위 Checkpoint/Replay/Fork | IMP_OK |

---

## Dim C — IMP_IMPOSSIBLE (0건)

해당 없음.

---

## Dim C — IMP_MISSING (8건)

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|---------|----------|----------|----------|
| C-06 | — | EventType 체인 순환 감지 | PART2 L1528-1541에 EventType 53+개 등록하나, EventType 간 순환 참조 감지 메커니즘(예: DAG 검증)이 미기재 | **MEDIUM** |
| C-13 | — | conditional_edge (Gate 결정 분기) | V1에서 Gate 결과(deny/allow/downshift/hold)에 따른 LangGraph `add_conditional_edges` 구현 방법 미기재. V0 코드(L322-334)는 `add_edge`만 사용 | **HIGH** |
| C-14 | L494 | conditional_edge (Verify 실패 재시도) | "검증 실패 → 1회 자동 재시도 → HITL 승인" 텍스트 기술만 있고, LangGraph conditional_edge 구현 코드/의사코드 부재 | **HIGH** |
| C-15 | — | conditional_edge (SelfCheckGate S5→S6) | CLAUDE.md L88: "SelfCheckGate \| S5→S6" 정의. PART2에 SelfCheck Gate의 파이프라인 위치(S5→SelfCheck→S6) 명시 부재 | **MEDIUM** |
| C-16 | L324 | VamosState 필드 정의 | `StateGraph(VamosState)` 사용하나 VamosState의 필드 목록(intent, evidence_pack, decision, trace_id, phase, gate_results 등) 미기재. 구현자가 상태 구조를 알 수 없음. *(BLOCKER 근거: 주1 참조)* | **BLOCKER** |
| C-18 | — | Verify 실패 conditional_edge 구현 | Soft Loop 1회 후 Hard Loop(승인 필요) 분기를 LangGraph에서 어떻게 구현하는지 구체적 가이드 부재 | **HIGH** |
| C-21 | — | Pipeline timeout 정의 | 전체 파이프라인(S0→S8) 실행 제한 시간이 미정의. 개별 CB timeout(60s)은 있으나 전체 파이프라인 timeout 부재 | **MEDIUM** |
| C-26 | — | Multi-turn Decision 처리 | 대화가 여러 턴에 걸칠 때 Decision 객체의 연속성/갱신/잠금 해제 메커니즘이 미기재 | **MEDIUM** |

> **주1 (C-16 BLOCKER 근거)**: v8 심각도 정의상 BLOCKER = "구현 차단". LangGraph `StateGraph(VamosState)`는 V0~V3 전체 파이프라인의 최상위 상태 컨테이너이며, 필드 정의 없이는 어떤 노드도 구현할 수 없음 (모든 노드가 VamosState를 읽고 쓰므로). 단순 누락 스펙(HIGH)이 아닌, 파이프라인 구현 자체를 차단하는 근본 의존성. **B-M3과 동일 이슈의 Dim C 관점 기록** (이중 집계 아님, 차원별 교차 확인).

---

## Dim C — IMP_CONFLICT (3건)

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|----------|------|
| C-11 | PART2 L839-854: 9-state=INIT/IDLE/INPUT_READY/PROCESSING/STREAMING/TOOL_EXECUTING/HITL_PENDING/ERROR/SESSION_END | D2.0-08 §4.1 L336-344: 9-state=BOOT/IDLE/EDITING/READY/RUNNING/AWAIT_APPROVAL/PRESENTING/RECOVERY/ARCHIVED | **5-Phase→9-State 매핑 불가**: PART2의 9-state 이름이 D2.0-08 정본과 불일치하여, D2.0-08 §4.6에 정의된 Pipeline S0~S8 ↔ UI State 매핑을 적용할 수 없음 | **BLOCKER** — D2.0-08 §4.1 정본 이름으로 통일 필요 |
| C-12 | PART2 L856: "기존 6-state 대비 3개 추가" | D2.0-08 §4.5: "§4.1(9-state)이 UI 설계 정본" | PART2가 6-state 확장 방식으로 9-state를 구성했으나, D2.0-08은 §4.1을 독립적 9-state 정본으로 정의. 접근 방식 자체가 상충 | **HIGH** — PART2를 D2.0-08 §4.1 정본에 맞춰 재정의 필요 |
| C-27 | PART2 L853: UI_S7 **ERROR** | D2.0-08 §4.1 L342: UI_S7_**RECOVERY** | S7 상태의 의미 차이: PART2="에러 상태"(문제 발생) vs D2.0-08="실패/폴백/재시도 안내"(복구 프로세스). 구현 관점에서 에러 감지와 복구는 다른 로직 | **HIGH** — D2.0-08 정본에 따라 RECOVERY로 수정하고 에러→복구 흐름 명확화 |

---

## 종합 요약

### BLOCKER (3건 — 즉시 수정 필요)

1. **B-07**: PART2 9-State Machine 이름이 D2.0-08 §4.1 정본과 7/9 불일치
2. **C-11**: 9-State 이름 불일치로 5-Phase→9-State 매핑 및 D2.0-08 §4.6 크로스 매핑 적용 불가
3. **C-16**: VamosState 필드 정의 누락 — LangGraph StateGraph 구현의 핵심 정보 부재

### HIGH (8건)

| # | 유형 | 내용 |
|---|------|------|
| B-M1 | MISSING | D2.0-08 §4.5 양방향 매핑 PART2 미반영 |
| B-M2 | MISSING | D2.0-08 §4.6 Pipeline↔UI 크로스 매핑 PART2 미반영 |
| B-M3 | MISSING | VamosState 필드 정의 PART2 미기재 |
| C-12 | IMP_CONFLICT | PART2 9-state 구성 접근 방식이 D2.0-08 정본과 상충 |
| C-13 | IMP_MISSING | Gate 결정 분기 conditional_edge 미기재 |
| C-14 | IMP_MISSING | Verify 실패 재시도 conditional_edge 미기재 |
| C-18 | IMP_MISSING | Soft/Hard Loop LangGraph 구현 가이드 부재 |
| C-27 | IMP_CONFLICT | UI_S7 ERROR vs RECOVERY 의미 차이 |

### MEDIUM (6건)

| # | 유형 | 내용 |
|---|------|------|
| B-01~04 | NO_SOURCE | 4-Layer "Application/Domain/Infrastructure/External" — v8 기대값/§5.3 참조 오기재. D2.0-01 §2 실제 4-Layer = ORANGE CORE/BLUE NODE/OTHER BRAINS/STORAGE |
| B-05 | MISMATCH | EvidencePack 출처: PART2 "D2.0-02 §7.2" → 실제 "D2.0-02 C3 템플릿" (필드 수 6개는 정확) |
| C-06 | IMP_MISSING | EventType 순환 감지 메커니즘 미기재 |
| C-15 | IMP_MISSING | SelfCheckGate S5→S6 위치 매핑 미명시 |
| C-21 | IMP_MISSING | Pipeline 전체 timeout 미정의 |
| C-26 | IMP_MISSING | Multi-turn Decision 처리 미기재 |

### LOW (1건)

| # | 유형 | 내용 |
|---|------|------|
| B-09 | MISMATCH | Gate 나열 순서 차이 (실질적 영향 없음, Gate는 각각 다른 파이프라인 단계에서 작동) |

---

## 추가 확인 사항

### Phase 0 교차 확인

- **IMP-A (순환 의존성)**: Phase 0에서 **I-10(Tool Registry) ↔ I-11(Output Composer) 순환 의존성** 감지 (BLOCKER). Agent 1 검증에서 C-02(순환 감지 메커니즘)를 IMP_OK로 판정하였으나, 이는 PART2에 VAL-003 검증 항목이 존재함을 확인한 것. Phase 0 IMP-A가 발견한 실제 순환(I-10↔I-11)은 **PART2 의존성 테이블 자체의 오류**이며, Phase 2에서 수정 필요.
- **IMP-B (DecisionSchema)**: Phase 0에서 PART2의 DecisionSchema=17 ≠ SOT 18 감지. Agent 1 범위(아키텍처)에서 DecisionSchema 필드 수는 직접 검증 대상이 아님 (Agent 5 범위). 다만 C-23(Decision.locked 강제)에서 Decision 구조 참조 시 18필드 SOT 인지 필요.

### SelfCheckGate 위치 (v8 주의사항)

- **CLAUDE.md L88**: `SelfCheckGate | S5→S6 | PASS/WARN/FAIL`
- **PART2**: SelfCheck Gate 존재 확인(L571)되나, "S5 → SelfCheck → S6" 파이프라인 위치 매핑은 미명시
- **판정**: C-15 IMP_MISSING으로 기록

### trace_id in VamosState (v8 주의사항)

- **PART2 L186**: `trace_id_required = true  # LOCK`
- **PART2 L1067**: `LOCK-AT-007 | Checkpoint/Replay/Fork는 trace_id 단위로만 허용`
- **VamosState 필드로서의 명시**: 부재 (C-16 VamosState 필드 누락에 포함)
- **판정**: trace_id 자체는 LOCK으로 존재하나, VamosState의 명시적 필드 정의 부재

### EvidencePack section 참조

- **PART2 L206**: `EvidencePack | 6 | D2.0-02 §7.2` — section 참조 "§7.2" 부정확
- **D2.0-02 실제 위치**: §7.13 (레거시) 또는 C3 템플릿 (정본, L2692-2703)
- **판정**: 필드 수(6개)는 정확하나, 출처 section 번호가 §7.2→§7.13/C3로 수정 필요 (MEDIUM)

### 4-Layer 아키텍처 v8 기대값 이슈

- v8 프롬프트가 "Application/Domain/Infrastructure/External — D2.0-01 §5.3"로 명시하나:
  - D2.0-01 §5.3 = "Fallback Registry" (4-Layer 무관)
  - D2.0-01 §2 실제 4-Layer = ORANGE CORE / BLUE NODE / OTHER BRAINS / STORAGE
  - "Application/Domain/Infrastructure/External"은 DDD/Clean Architecture 패턴 용어
- **권고**: v8 프롬프트의 B-01~B-04 항목을 D2.0-01 §2 기준으로 재정의하거나, PHASE_B2 프로젝트 구조의 디렉토리 레이어와 대조하도록 수정

---

## 수정 권고 우선순위

1. **PART2 §6.1.6**: 9-State 이름을 D2.0-08 §4.1 정본에 맞춰 수정 (BOOT/IDLE/EDITING/READY/RUNNING/AWAIT_APPROVAL/PRESENTING/RECOVERY/ARCHIVED)
2. **PART2 신규 추가**: VamosState 필드 정의 (최소: intent_frame, evidence_pack, decision, trace_id, phase, gate_results, error, artifacts)
3. **PART2 신규 추가**: D2.0-08 §4.6 Pipeline↔UI 크로스 매핑 테이블 반영
4. **PART2 V1 구현 가이드**: LangGraph conditional_edge 구현 예시 (Gate 분기, Verify 실패 재시도, SelfCheck 위치)
5. **PART2 L206**: EvidencePack 출처를 "D2.0-02 §7.2" → "D2.0-02 C3 템플릿 §출력" 으로 정정
