---
session: 03
sections: [3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7]
status: complete
---

# §3. 처리 파이프라인 — 요청부터 응답까지

> **비유**: 병원에 가면 "접수 → 진료 → 검사 → 처방 → 수납"의 순서를 거치듯, VAMOS도 사용자의 요청을 **정해진 순서**로 처리합니다. 각 단계마다 "관문(Gate)"이 있어서, 통과하지 못하면 다음 단계로 넘어갈 수 없습니다.

이 장에서는 VAMOS가 사용자의 요청을 받아서 응답을 만들기까지의 **전체 흐름**을 설명합니다.

---

## §3.1 9-State 상태 머신 (S0~S8) — 요청의 여정 추적

### 비유

택배를 주문하면 "주문 접수 → 상품 준비 → 배송 중 → 배달 완료"처럼 상태가 변합니다. VAMOS도 마찬가지로, 모든 요청을 **9개의 상태(State)**로 추적합니다. 지금 어디까지 진행되었는지 언제든 알 수 있습니다.

### 정의

**상태 머신(State Machine)**이란, 시스템이 가질 수 있는 상태들과 그 사이의 전환 규칙을 정의한 구조입니다. VAMOS의 상태 머신은 **9개 상태(S0~S8)**로 구성되며, 이 구조는 **LOCK(변경 불가)**입니다. [근거: D2.0-02 §2.2]

### 상태 다이어그램

```
S0_RECEIVED ──→ S1_INTENT_PARSED ──→ S2_EVIDENCE_READY ──→ S3_DECISION_LOCKED
  (접수됨)        (의도 파악 완료)      (근거 수집 완료)       (판단 확정)
                                                                  │
                                                                  ▼
S8_DONE ←── S7_MEMORY_COMMITTED ←── S6_SELF_CHECKED ←── S5_OUTPUT_READY ←── S4_EXECUTING
(완료!)      (기억에 저장)           (자체 검증 완료)     (결과 생성 완료)     (실행 중)
```

[근거: BEGINNER_GUIDE §3.1]

### 각 상태 상세 설명

| 상태 | 이름 | 담당 모듈 | 하는 일 | 비유 |
|------|------|----------|---------|------|
| **S0** | RECEIVED (접수됨) | Front Mini LLM | 사용자 입력을 처음 받음. 안전한 요청인지, 어떤 분야인지 즉시 판단 | 접수처 직원이 서류를 받음 |
| **S1** | INTENT_PARSED (의도 파악 완료) | I-1 Intent Detector | 사용자의 말을 **IntentFrame**(의도 프레임)이라는 구조체로 변환. 목표, 제약, 위험 등을 파악 | 의사가 "어디가 아프세요?" 확인 |
| **S2** | EVIDENCE_READY (근거 수집 완료) | I-2 Context Builder (RAG) | 관련 정보를 수집하고 **QoD**(근거 품질 점수)를 매김 | 검사실에서 혈액검사, X-ray 촬영 |
| **S3** | DECISION_LOCKED (판단 확정) | I-5 Routing & Decision | 5개 Gate(관문)를 통과하여 최종 판단 확정. **locked=true** 이후 결론 변경 불가 (**LOCK**) | 의사가 진단서에 서명 |
| **S4** | EXECUTING (실행 중) | BLUE NODE | 해당 분야 전문 노드가 실제 작업 수행 (코딩, 리서치, 트레이딩 등) | 수술실에서 수술 진행 |
| **S5** | OUTPUT_READY (결과 생성 완료) | I-11 Output Composer | 실행 결과를 **3단 출력 구조**로 정리 (§3.3 참조) | 검사 결과지 작성 |
| **S6** | SELF_CHECKED (자체 검증 완료) | I-6 Self-check | 출력의 정확성·안전성·일관성을 자동 검증. 점수 미달 시 재시도 | 약사가 처방전 다시 확인 |
| **S7** | MEMORY_COMMITTED (기억에 저장) | I-3 Memory Manager | 대화 내용과 결과를 기억에 저장 (저장 정책에 따라) | 진료 기록 차트에 기재 |
| **S8** | DONE (완료) | — | **ResponseEnvelope**(응답 봉투)에 담아 사용자에게 전달 | 수납 후 퇴원 |

[근거: D2.0-02 §2.2, BEGINNER_GUIDE §3.1]

### 전이 규칙 (상태가 바뀌는 조건)

| 전이 | 조건 | 비고 |
|------|------|------|
| S0 → S1 | Front Mini LLM이 안전 필터링 통과 + 의도 파악 완료 | PC_SAFETY_CLASSIFY 훅 실행 |
| S1 → S2 | IntentFrame 생성 완료 + 근거 수집 시작 | 모호하면 FB_ASK_CLARIFICATION 발동 |
| S2 → S3 | QoD(근거 품질)가 임계값 이상 + 5개 Gate 통과 | QoD 미달 시 재검색 루프 |
| S3 → S4 | Decision locked=true + 실행 계획 확정 | **단일결정 원칙**: 이후 결론 변경 불가 (**LOCK**) |
| S4 → S5 | BLUE NODE 실행 완료 + 결과 수집 | — |
| S5 → S6 | 3단 출력 생성 완료 + Self-check 시작 | — |
| S6 → S7 | Self-check PASS + 메모리 저장 시작 | FAIL 시 Soft/Hard Loop (§3.5 참조) |
| S7 → S8 | 메모리 커밋 완료 + ResponseEnvelope 전달 | — |

[근거: D2.0-02 §2.2]

### ⚠️ 핵심 규칙 (LOCK — 변경 불가)

- **단일결정 원칙**: S3(Decision Locked) 이후에는 결론을 바꾸지 않습니다. 축소(downshift)만 허용됩니다. [근거: D2.0-02 §2.2]
- **S6 FAIL 시 자동 Soft Loop 1회만 허용**, 이후에는 사용자 승인이 필요합니다. [근거: D2.0-02 §7.53-1]

### 각 단계별 소요 시간 목표

| 구간 | 시간 목표 |
|------|----------|
| 단순 응답 (mini 모델) | ≤ 2초 |
| 복합 응답 (main + 도구 1회) | ≤ 10초 |
| Self-check 소요 | ≤ 1초 |
| 동시 처리 가능 요청 | 5개 |

[근거: BEGINNER_GUIDE §3.2]

> **핵심 요약 (3줄)**
> 1. VAMOS는 모든 요청을 **9개 상태(S0~S8)**로 추적하며, 이 구조는 LOCK(변경 불가)입니다.
> 2. S3(판단 확정) 이후에는 결론 변경이 불가능한 **단일결정 원칙**이 적용됩니다.
> 3. 각 상태 전이에는 명확한 조건이 있으며, 조건 미달 시 재시도(Loop) 또는 거부(Deny)로 처리됩니다.

---

## §3.2 Standard 5-Phase 파이프라인

### 비유

9-State가 "택배 추적 번호"라면, 5-Phase는 "공장 조립 라인"입니다. 원재료(사용자 요청)가 5개의 작업대를 거쳐 완제품(응답)이 됩니다. 각 작업대에는 **품질 검사원(Gate)**이 서 있어서, 불량품은 다음 단계로 넘어갈 수 없습니다.

### 정의

**5-Phase 파이프라인**은 VAMOS의 표준 처리 단계입니다. 9-State를 작업 관점에서 5단계로 묶은 것이며, **LOCK(변경 불가)**입니다. [근거: D2.0-05 §7.1]

### 구조도

```
[Intake]  →  [Plan]  →  [Execute]  →  [Verify]  →  [Deliver]
 요청 수집     계획       실행          검증          전달
   G0          G1,G2      (선행완료)     G3           G4
```

[근거: D2.0-05 §7.1, §12.16]

### 9-State ↔ 5-Phase 매핑표

| ORANGE CORE 용어 | 5-Phase 용어 | 상태 코드 | UI 표시 |
|-----------------|-------------|----------|---------|
| Perception (인지) | **Intake** (접수) | S0 → S1 | RECEIVED → INTENT |
| Reasoning (추론) | **Plan** (계획) | S2 → S3 | EVIDENCE → DECISION |
| Action (실행) | **Execute** (실행) | S4 → S5 | EXEC |
| Reflection (성찰) | **Verify** (검증) | S6 | SELF-CHECK |
| Memory (기억) | Deliver 하위 구간 | S7 → S8 | MEMORY → DONE |

> ⚠️ **Reflection(S6)과 Memory(S7)는 표준 파이프라인의 Verify(4)~Deliver(5) 단계 내부 하위 구간으로 포함됩니다** (**LOCK**). [근거: D2.0-05 §7.1]

[근거: BEGINNER_GUIDE §4.2]

---

### §3.2.1 Phase 1: Intake (접수)

> **비유**: 병원 접수처에서 "어디가 아프세요?"라고 물어보고, 보험증을 확인하는 단계입니다.

| 항목 | 내용 |
|------|------|
| **목적** | 사용자 요청 수신 + 전처리 + 형식 파악 (텍스트/파일/이미지 등) |
| **입력** | 사용자의 원본 메시지 |
| **출력** | IntentFrame (의도 프레임) |
| **적용 Gate** | **G0** — 입력 검증 (형식/범위/안전). 실패 시 **즉시 거부** |
| **담당 모듈** | Front Mini LLM → I-1 Intent Detector |
| **이벤트** | oc.intent.parsed |
| **에러코드** | OC_I1_PARSE_FAIL → FB_INTENT_HEURISTIC_PARSE (경험적 파싱 시도) |
|  | OC_I1_AMBIGUOUS → FB_ASK_CLARIFICATION (사용자에게 질문 1~3개) |

[근거: D2.0-02 §2.1, D2.0-05 §7.1, §12.16]

---

### §3.2.2 Phase 2: Plan (계획)

> **비유**: 의사가 검사 결과를 보고, "어떤 치료를 할지" 계획을 세우는 단계입니다. 예산(보험 한도)도 확인합니다.

| 항목 | 내용 |
|------|------|
| **목적** | 작업 분해 + 라우팅(어떤 전문 노드가 처리할지) + 비용 계산 + 계획 수립 |
| **입력** | IntentFrame + EvidencePack (근거 모음) |
| **출력** | Decision (판단 객체, locked=true) |
| **적용 Gate** | **G1** — 정책 검사 (PolicyCheck). 실패 시 **deny(거부)** |
|  | **G2** — 비용 검사 (CostBudget). 실패 시 **deny 또는 downshift(저비용 모드 전환)** |
| **담당 모듈** | I-2 Context Builder (RAG) → I-5 Routing & Decision |
| **에러코드** | OC_I2_RAG_NO_SOURCE → FB_RAG_RETRY_EXPAND (검색 범위 확장) |
|  | OC_I2_EVIDENCE_QOD_LOW → FB_RAG_RETRY_EXPAND (재검색) |
|  | OC_I5_COST_OVER_BUDGET → FB_COST_DOWNSHIFT (저비용 모델로 전환) |
|  | OC_I5_POLICY_BLOCK → FB_DENY_WITH_REASON (사유와 함께 거부) |

**Plan 강화 옵션** (기본 OFF, 조건부 활성): [근거: D2.0-02 §10.1]
- D-4 (HTN Planning): 계획 수립 시 프랙탈 분해 수행 (기본 CORE)
- D-5 (Value Function): 후보 Plan/Tool/Brain 선택을 점수화하여 Decision에 입력 (옵션 필드)
- D-2 (MCTS, EXP): 타임박스+상한 조건에서만 후보 탐색 (기본 OFF)
- D-1 (World Model, EXP): 실행 전 시뮬레이션으로 위험·성공확률 추정 (기본 OFF)

> ⚠️ **규칙 (LOCK)**: D 계열 기능은 "기본 OFF + 타임박스 + 비용 상한 + 승인(필요 시)"을 만족할 때만 Decision의 optional 필드로 사용 가능합니다. [근거: D2.0-02 §10.3]

[근거: D2.0-02 §2.1, §2.3, §10.1, D2.0-05 §7.1, §12.16]

---

### §3.2.3 Phase 3: Execute (실행)

> **비유**: 수술실에서 실제로 수술이 진행되는 단계입니다. 이전 단계에서 모든 준비와 승인이 완료된 상태입니다.

| 항목 | 내용 |
|------|------|
| **목적** | 도구/노드 실행 + 산출물 생성 |
| **입력** | Decision (확정된 판단) + 실행 계획 |
| **출력** | 실행 결과 (도구 결과, 생성 텍스트 등) |
| **적용 Gate** | 선행 Gate(G0, G1, G2)가 이미 통과 완료된 상태 |
| **담당 모듈** | BLUE NODE (분야별 전문 노드) + OTHER BRAINS (실제 도구들) |
| **에러코드** | TOOL_TIMEOUT → FB_RAG_RETRY_EXPAND (재시도) |

[근거: D2.0-02 §2.1, D2.0-05 §7.1, §12.16]

---

### §3.2.4 Phase 4: Verify (검증)

> **비유**: 약사가 의사의 처방전을 다시 한번 확인하는 단계입니다. "이 약 조합이 안전한가?", "용량이 맞는가?"를 체크합니다.

| 항목 | 내용 |
|------|------|
| **목적** | 품질 검사 + Self-check + EVX(검증 확장) 체인 실행 |
| **입력** | 실행 결과 + 3단 출력 초안 |
| **출력** | Self-check 결과 (score, verdict: PASS/WARN/FAIL) |
| **적용 Gate** | **G3** — 품질 검사 (QoD + EVX). 실패 시 **Soft loop 1회 → deny** |
| **담당 모듈** | I-6 Self-check |
| **에러코드** | OC_GATE_SELFCHECK_FORMAT_FAIL — 출력 포맷 불일치 |
|  | OC_GATE_SELFCHECK_SAFETY_FAIL — 안전 가이드라인 위반 |
|  | OC_GATE_SELFCHECK_EVIDENCE_MISMATCH — 근거-결론 불일치 |
| **폴백** | FB_SELFCHECK_RETRY → 재생성 1회 / FB_SELFCHECK_HARD → ApprovalGate 이관 |

**Verify 강화 옵션**: [근거: D2.0-02 §10.2]
- EVX-1 (Code-as-Policy): 정책/규칙을 검증 단계에서 실행 가능한 형태로 체크
- C-1/EVX-6 (Z3 Solver): 제약 문제(모순/충돌)를 Solver로 분기 (조건부)
- D-3 (Self-consistency): 불확실성이 높을 때만 다중 샘플 합의 적용
- C-3 (Code Verifier, CORE): 코드/툴 결과는 샌드박스 검증 통과 후에만 채택

[근거: D2.0-02 §2.1, §8.1, §10.2, D2.0-05 §7.1, §12.16]

---

### §3.2.5 Phase 5: Deliver (전달)

> **비유**: 수납을 마치고 검사 결과지, 처방전, 진료비 영수증을 함께 받는 단계입니다.

| 항목 | 내용 |
|------|------|
| **목적** | 결과 전달 + 로그 기록 + 메모리 저장 |
| **입력** | Self-check 통과된 3단 출력 |
| **출력** | ResponseEnvelope (응답 봉투) — 사용자에게 최종 전달 |
| **적용 Gate** | **G4** — 최종 승인 (P1 이상에서 Approval). 실패 시 **hold(보류) 또는 deny(거부)** |
| **담당 모듈** | I-11 Output Composer + I-3 Memory Manager |
| **하위 구간** | Memory(저장) + Reflection(성찰) 포함 (**LOCK**) |

[근거: D2.0-02 §2.1, D2.0-05 §7.1, §12.16]

---

### Gate-Pipeline 매핑 요약표 (LOCK — 변경 불가)

| Pipeline 단계 | Gate | 역할 | 실패 시 |
|--------------|------|------|--------|
| **1) Intake** | G0 | 입력 검증 (형식/범위/안전) | 즉시 거부 |
| **2) Plan** | G1 | 정책 검사 (PolicyCheck) | deny |
| **2) Plan** | G2 | 비용 검사 (CostBudget) | deny / downshift |
| **3) Execute** | — | 실행 (G0~G2 선행 완료 상태) | — |
| **4) Verify** | G3 | 품질 검사 (QoD + EVX) | Soft loop / deny |
| **5) Deliver** | G4 | 최종 승인 (P1+: Approval) | hold / deny |

[근거: D2.0-05 §12.16]

### Gate 피드백 루프

```
G3 실패 → Soft loop 1회 (§3.5) → Execute 재실행
G3 재실패 → 승인 요청 또는 deny
G2 downshift → 저비용 모델로 자동 전환 후 재실행
G4 hold → 사용자 승인 대기 큐 등록
```

[근거: D2.0-05 §12.16]

> **핵심 요약 (3줄)**
> 1. 5-Phase 파이프라인(Intake→Plan→Execute→Verify→Deliver)은 9-State를 작업 관점으로 묶은 **LOCK** 구조입니다.
> 2. 각 Phase마다 **Gate(G0~G4)**가 배치되어 정책·비용·품질·승인을 검사합니다.
> 3. Gate 실패 시 deny(거부), downshift(저비용 전환), Soft loop(1회 재시도) 등 정해진 규칙으로 처리됩니다.

---

## §3.3 3-Part Output (3단 출력)

### 비유

병원에서 진료를 마치면 세 가지를 받습니다: ① **처방전** (치료 결과), ② **검사 결과지** (근거), ③ **진료비 영수증** (기록). VAMOS도 마찬가지로, 모든 응답을 항상 **3가지 부분**으로 나누어 제공합니다.

### 정의

VAMOS의 모든 워크플로우 종료 시 반드시 산출해야 하는 3개 필드입니다. 이 구조는 **LOCK(변경 불가)**입니다. [근거: D2.0-05 §7.2]

### 구조표

| # | 필드명 | 설명 | 비유 |
|---|--------|------|------|
| 1 | **user_response** (최종 결과) | 사용자에게 전달되는 응답. 요약(summary) + 상세(details) + 제안(next_actions) | 처방전 |
| 2 | **evidence_summary** (근거 요약) | 출처, 신뢰도, QoD(근거 품질 점수) 포함 | 검사 결과지 |
| 3 | **log_report** (내부 로그) | trace_id, 소요 시간, 사용 비용, 저장/승인 이벤트 기록 | 진료비 영수증 |

[근거: D2.0-02 §5.1, D2.0-05 §7.2]

### ResponseEnvelope 개요 (LOCK — 변경 불가)

VAMOS는 3단 출력을 **ResponseEnvelope**(응답 봉투)라는 표준 구조에 담습니다. 핵심 구성은 다음과 같습니다: [근거: D2.0-02 §5.1]

| 구성 요소 | 포함 내용 | 비유 |
|-----------|----------|------|
| **answer** | summary(요약) + details(상세) + next_actions(제안) | 처방전 |
| **evidence** | coverage(충족률) + items(출처 목록) + qod(품질 점수) | 검사 결과지 |
| **self_check** | score + verdict(PASS/WARN/FAIL) | 교정쇄 확인 |
| **decision_ref** | decision_id + gates 통과 결과 | 판결문 참조 |
| **audit** | event_ids + failure_codes + fallback_ids | 감사 기록 |

> **ResponseEnvelope와 EvidenceItem의 전체 필드 상세는 §5.6(ResponseEnvelope)에서 다룹니다.**
> [근거: D2.0-02 §5.1~§5.1.3]

### 실제 예시

사용자가 "삼성전자 실적 분석해줘"라고 요청한 경우:

```
[1단] user_response (최종 결과)
  "삼성전자 2025년 실적 분석:
   매출: XX조, 전년 대비 +XX%
   영업이익: XX조, ..."

[2단] evidence_summary (근거 요약)
  "출처1: 삼성전자 IR자료 (QoD: 0.92)
   출처2: DART 공시 (QoD: 0.88)"

[3단] log_report (내부 로그)
  "trace_id: xxx, 소요시간: 4.2초, 사용 비용: ₩15"
```

[근거: BEGINNER_GUIDE §3.1 S5_OUTPUT_READY]

> **핵심 요약 (3줄)**
> 1. VAMOS의 모든 응답은 **user_response(결과) + evidence_summary(근거) + log_report(로그)** 3단 구조입니다 (**LOCK**).
> 2. 이 구조는 **ResponseEnvelope**이라는 표준 형식에 담겨 전달됩니다.
> 3. "근거 없는 단정"을 방지하기 위해, EvidenceGate 미달 시 결론은 HOLD/ESCALATE로 제한됩니다.

---

## §3.4 TEE Loop (Think-Execute-Evaluate)

### 비유

요리를 할 때 "레시피 확인(Think) → 재료 넣기(Execute) → 맛보기(Evaluate)"를 반복하는 것과 같습니다. 맛이 부족하면 다시 레시피를 확인하고 조미료를 추가합니다. 하지만 무한히 반복할 수는 없으니, **최대 반복 횟수**가 정해져 있습니다.

### 정의

**TEE Loop**는 VAMOS 파이프라인 내부에서 작동하는 핵심 실행 루프입니다. 각 Phase 안에서 "생각 → 실행 → 평가"를 반복하며, 이 구조는 **LOCK(변경 불가)**입니다. [근거: D2.0-05 §12.5.1]

### 구조도

```
Think(생각) → Execute(실행) → Evaluate(평가)
     ↑                              │
     └──── 미달 시 다시 생각 ←──────┘
```

[근거: BEGINNER_GUIDE §3.4, D2.0-05 §12.5.1]

### 각 단계 상세

| 단계 | 하는 일 | 연결 모듈 |
|------|---------|----------|
| **Think** (생각) | 현재 상태/컨텍스트 분석 → 다음 액션 결정. Gate 선행 확인(G1 PolicyCheck), 비용 예측(G2 CostBudget) | I-1 (Intent) + I-5 (Router) |
| **Execute** (실행) | 결정된 액션 실행 — 도구 호출, 서브에이전트 위임. Allowlist 자동승인 또는 명시적 확인 | I-5 (Router) → Brain/Node |
| **Evaluate** (평가) | 실행 결과 평가 — Self-check(QoD 점수), 목표 달성 여부 판단. 미달 시 Soft loop 1회 → 재 Think | I-6 (Self-check) |

[근거: D2.0-02 §11.10.2, D2.0-05 §12.5.1]

### 최대 반복 횟수 (LOCK — 변경 불가)

무한 루프를 방지하기 위해, 위험도(Priority)에 따라 최대 반복 횟수가 제한됩니다:

| 위험도 | 최대 TEE 반복 | 설명 |
|--------|-------------|------|
| **P0** (기본) | **3회** | 일반적인 요청. 3번 안에 해결 안 되면 종료 |
| **P1** (확장) | **5회** | 복잡한 요청. 더 많은 시도 허용 |
| **P2** (고위험) | **10회** | 고위험 작업. 최대 10회, 승인 시 확장 가능 |

[근거: D2.0-05 §12.5.1]

### TEE Loop와 5-Phase의 관계

ORANGE CORE는 TEE Loop의 **"제어자"** 역할만 수행하고, 실제 실행은 05(Agent Workflow)에 위임합니다. [근거: D2.0-02 §11.10.2]

| 5-Phase 단계 | TEE 단계 |
|-------------|---------|
| Plan | Think |
| Execute | Execute |
| Verify | Evaluate |

### 루프 종료 조건

TEE 루프는 다음 중 하나가 발생하면 종료됩니다: [근거: D2.0-05 §12.12.4]

1. **목표 달성** — Self-check PASS
2. **최대 반복 도달** — P0=3, P1=5, P2=10
3. **Gate deny** — 정책/비용/승인 거부

> **핵심 요약 (3줄)**
> 1. TEE Loop(Think→Execute→Evaluate)는 파이프라인 내부의 핵심 실행 루프입니다 (**LOCK**).
> 2. 무한 루프 방지를 위해 최대 반복 횟수가 P0=3회, P1=5회, P2=10회로 제한됩니다.
> 3. 목표 달성, 최대 반복, Gate deny 중 하나가 발생하면 루프가 종료됩니다.

---

## §3.5 Soft Loop / Hard Loop / Circuit Breaker

### 비유

- **Soft Loop**: 시험에서 답을 틀렸을 때, 같은 자리에서 지우개로 지우고 다시 쓰는 것 (1회만 허용)
- **Hard Loop**: 시험지를 새로 받아서 처음부터 다시 푸는 것 (선생님 허락 필요)
- **Circuit Breaker**: 집에서 전기가 자꾸 끊기면, 차단기가 내려가서 더 이상 전기를 보내지 않는 것 (안전 보호)

### 정의

VAMOS에서 실패가 발생했을 때의 **재시도 전략** 3가지입니다. 각각 자동화 수준과 허용 범위가 다릅니다.

### 비교표

| 구분 | Soft Loop | Hard Loop | Circuit Breaker |
|------|-----------|-----------|-----------------|
| **정의** | 동일 단계 내에서 입력/프롬프트/검색 범위를 조정해 1회 보정 후 재시도 | 워크플로우를 이전 단계로 되감아 재실행 | 연속 실패 시 호출 자체를 자동 차단 |
| **자동 여부** | ✅ 자동 (1회만) | ❌ 사용자 승인 필요 | ✅ 자동 (임계값 초과 시) |
| **횟수** | 1회 (**LOCK**) | 승인 시에만 | N/A (상태 기반) |
| **발동 조건** | Self-check FAIL | Soft loop 후에도 FAIL | 연속 3회 실패 |
| **비유** | 지우개로 지우고 다시 씀 | 시험지를 새로 받음 | 차단기가 내려감 |

[근거: D2.0-05 §4.2, D2.0-02 §7.53-1]

### Soft Loop 상세 (LOCK — 변경 불가)

```
Self-check 실행
    │
    ├── PASS → 출력 확정 → Deliver
    │
    └── FAIL (1차)
         │
         ├── 자동 Soft Loop 1회 실행
         │   (입력/프롬프트/검색 범위 보정 후 재평가)
         │
         └── FAIL (2차, 연속)
              │
              ├── 승인 필요 상황 → fallback_id = FB_REQUIRE_APPROVAL
              ├── 축소 출력 가능 → fallback_id = FB_OUTPUT_MINIMAL
              └── 정책 위반/Non-goal → fallback_id = FB_DENY_WITH_REASON
```

[근거: D2.0-02 §7.53-1]

### Self-check 임계값 (LOCK — 변경 불가)

| 위험도 | PASS 기준 점수 | 설명 |
|--------|--------------|------|
| **P0** (기본) | self_check_score ≥ **70** | 일반 작업 |
| **P1** (확장) | self_check_score ≥ **75** | 확장 작업 |
| **P2** (고위험) | self_check_score ≥ **80** | 고위험 작업 |

> 해석: "관문(Self-check)은 고정" = 반드시 통과해야 다음 단계로 진행 가능. "임계값은 가변" = 위험도에 따라 PASS 기준점만 달라집니다. [근거: D2.0-02 §7.53-1]

### P2 고위험 특례 (LOCK — 변경 불가)

P2에서 FAIL일 경우, Soft loop를 강행하지 않고 **07의 Approval/Policy/Cost Gate 결론을 우선**합니다. 승인 없이는 "확정 결론/대규모 실행/확장 도구 호출"로 넘어가지 않습니다. [근거: D2.0-02 §7.53-1]

### Hard Loop 상세

```
Soft Loop 후에도 FAIL
    │
    ├── 위험/정책 위반 탐지 → 루프/재시도 없이 즉시 deny
    │
    └── 위반 없음
         │
         ├── 사용자에게 승인 요청 (재시도/확장 검색/도구 사용 등)
         │     │
         │     ├── 승인됨 → Hard Loop 실행 (이전 단계로 되감아 재실행)
         │     └── 거부됨 → deny + 사유 기록
         │
         └── 승인 없이는 즉시 종료 (deny/hold)
```

[근거: D2.0-05 §4.2]

### Circuit Breaker (회로 차단기) 상세

특정 에이전트/도구/외부 API에서 **연속 실패**가 발생할 경우, 자동으로 호출을 차단하여 시스템 전체 장애 전파를 방지합니다. [근거: D2.0-05 §4.4]

#### 3가지 상태

```
CLOSED (정상)          3회 연속 실패         OPEN (차단)
  ● 호출 허용    ──────────────────→    ✗ 호출 차단
                                              │ 60초 경과
                  성공하면 CLOSED로      HALF-OPEN (시험)
                 ←─────────────────    ○ 1건만 시도
```

| 상태 | 의미 | 동작 |
|------|------|------|
| **CLOSED** (닫힘) | 정상 운영 상태 | 호출 허용 |
| **OPEN** (열림) | 연속 3회 실패 → 자동 차단 | 60초간 호출 금지, 호출 시 즉시 deny |
| **HALF-OPEN** (반열림) | 60초 후 복구 탐지 | 1건만 시험적으로 호출. 성공 → CLOSED, 실패 → OPEN |

#### 임계값 규칙 (LOCK — 변경 불가)

- 연속 실패 **3회** 초과 시 OPEN 전환 (기본값)
- OPEN 유지 시간 **60초** 경과 후 HALF-OPEN 시도 (기본값)
- 임계값 변경은 07 Gate 승인 후만 허용

[근거: D2.0-05 §4.4]

#### P2 이상 특례 (LOCK — 변경 불가)

P2 이상 작업에서 OPEN 상태 진입 시, **60초 자동 HALF-OPEN 전환을 적용하지 않습니다.** 반드시 **사용자 승인 후에만** HALF-OPEN 전환이 허용됩니다. [근거: D2.0-05 §4.4]

#### 9-State 파이프라인 매핑

- CB는 주로 **Execute(S3~S4)** 단계에서 외부 API/도구 호출 실패 시 작동
- OPEN 진입 시 현재 파이프라인은 **Verify(S5)** 단계로 전이하여 실패 처리
- HALF-OPEN 복구 시도는 **Execute(S3)** 단계에서 재진입

[근거: D2.0-05 §4.4]

> **핵심 요약 (3줄)**
> 1. **Soft Loop**는 자동 1회 보정 재시도, **Hard Loop**는 사용자 승인 후 이전 단계 재실행, **Circuit Breaker**는 연속 실패 시 자동 차단입니다.
> 2. Self-check 임계값은 P0=70, P1=75, P2=80이며 (**LOCK**), 2회 연속 FAIL 시 fallback으로 수렴합니다.
> 3. Circuit Breaker는 3회 연속 실패 → OPEN(60초 차단) → HALF-OPEN(시험) → CLOSED(복구) 순으로 작동합니다.

---

## §3.6 에러 발생 시 흐름 (Failure → Fallback → Deny)

### 비유

소방서에는 화재 대응 매뉴얼이 있습니다. "물이 안 나오면 → 소화기를 쓰고 → 소화기도 없으면 → 대피 명령". VAMOS도 모든 가능한 오류에 대해 **미리 정해진 대응 매뉴얼(Fallback)**이 있습니다.

### 정의

VAMOS의 에러 처리 원칙: **모든 실패는 deny(거부) 또는 fallback(대안 행동)으로 귀결됩니다.** 예외 없이, 실패가 발생하면 반드시 코드화(FailureCode)하여 레지스트리에 등록하고, 대응책을 실행합니다. [근거: D2.0-02 §0.4]

### 에러 처리 흐름도

```
오류 발생!
    │
    ▼
[1] FailureCode 생성 ── 오류를 코드로 변환 (예: OC_I1_PARSE_FAIL)
    │
    ▼
[2] Fallback 조회 ──── 레지스트리에서 대응책 검색
    │
    ├── Fallback 있음 → 대안 행동 실행
    │     │
    │     ├── 성공 → 처리 계속
    │     └── 실패 → deny (거부 + 사유 기록)
    │
    └── Fallback 없음 → 즉시 deny (거부 + 사유 기록)
```

[근거: D2.0-02 §0.3, §6.2, §6.3]

### 주요 오류 코드와 대응표

| 오류 (FailureCode) | 의미 | 대응 (Fallback) | degrade_level |
|-------------------|------|----------------|---------------|
| `OC_I1_PARSE_FAIL` | 의도 파악 실패 | `FB_INTENT_HEURISTIC_PARSE` (경험적 파싱 시도) | V1 |
| `OC_I1_AMBIGUOUS` | 의도가 모호함 | `FB_ASK_CLARIFICATION` (사용자에게 질문 1~3개) | V1 |
| `OC_I2_RAG_NO_SOURCE` | 검색 결과 없음 | `FB_RAG_RETRY_EXPAND` (검색 범위 확장, 최대 2~3회) | V1 |
| `OC_I2_EVIDENCE_QOD_LOW` | 정보 품질 낮음 | `FB_RAG_RETRY_EXPAND` (재검색) | V1 |
| `OC_I5_COST_OVER_BUDGET` | 예산 초과 | `FB_COST_DOWNSHIFT` (저비용 모델로 전환) | V1 |
| `OC_I5_POLICY_BLOCK` | 정책 위반 | `FB_DENY_WITH_REASON` (사유와 함께 거부) | V0 |
| `TOOL_TIMEOUT` | 도구 실행 시간 초과 | retry 1회 → fallback/deny | V1 |

[근거: BEGINNER_GUIDE §3.5, D2.0-02 §6.2, §6.3]

### FailureCode / Fallback 표준 구조

각 FailureCode는 `failure_code`, `origin`, `trigger`, `fallback_id` 등 8개 필드로 구성되고, 각 Fallback은 `fallback_id`, `goal`, `steps`, `degrade_level` 등 7개 필드로 구성됩니다.

> **FailureCode/Fallback의 전체 필드 상세는 §35(이벤트 & 로깅 시스템)에서 다룹니다.**
> [근거: D2.0-02 §6.2, §6.3]

### 충돌 해결 규칙 (확정)

여러 Gate에서 동시에 문제가 발생하면, 다음 우선순위로 처리합니다: [근거: D2.0-02 §3.3]

| 충돌 유형 | 해결 규칙 |
|----------|----------|
| **정책 충돌** | policy_gate가 우선 (deny > restrict > allow) |
| **비용 충돌** | cost_gate가 라우팅/모델/실행 계획을 제한 |
| **근거 충돌** | evidence_gate 미달이면 결론은 HOLD/ESCALATE로 제한 |
| **포맷 충돌** | output_spec 위반은 Self-check FAIL → 재생성 또는 사유와 함께 종료 |

### 조건별 분기 (Gate 사전 차단)

| 조건 | 결과 |
|------|------|
| PolicyCheck = deny | 즉시 중단 (deny) |
| 비용 상한 초과 | 승인 없이 자동 차단 (deny) |
| P2 관련 요청 + 세션별 승인 없음 | 중단 (deny) |

[근거: D2.0-05 §3]

### 사용자에게 보이는 에러 메시지 예시

| 코드 | 메시지 |
|------|--------|
| FM_ERR_PII | "민감 정보 포함. 마스킹 후 진행할까요?" |
| OC_ERR_NONGOAL | "VAMOS 안전 정책상 수행 불가" |
| OC_ERR_COST | "절약 모드 전환" |
| TL_ERR_TIMEOUT | "작업 시간 초과. 잠시 후 재시도" |
| MC_ERR_LOW_QOD | "결과 품질 기준 미달. 보완 수행 중" |

[근거: BEGINNER_GUIDE §9.4]

### Fallback Chain (대체 모델 순서)

모델(Brain)이 실패하면 자동으로 다음 모델로 전환됩니다 (최대 3단계): [근거: BEGINNER_GUIDE §6.2]

```
gpt-4o → claude-sonnet → local-ollama → error_response
```

**Multi-Brain Failover**: 연속 3회 타임아웃 시 다음 모델로 전환 (**LOCK**)

> **핵심 요약 (3줄)**
> 1. VAMOS의 모든 실패는 **FailureCode로 코드화** → **Fallback(대안 행동)** 또는 **deny(거부)**로 귀결됩니다.
> 2. 정책 충돌 시 **policy_gate가 최우선** (deny > restrict > allow)이며, 근거 부족 시 결론은 HOLD로 제한됩니다.
> 3. 모델 실패 시 **Fallback Chain**(gpt-4o → claude-sonnet → local-ollama → error_response)으로 자동 전환됩니다.

---

## §3.7 ★에러 처리 표준 — Result<T, VamosError> 계약 — GAP-1

### 비유

병원에서 모든 의료진이 **같은 양식의 진단서**를 쓰도록 규정하는 것과 같습니다. 의사마다 다른 형식으로 쓰면 약사가 해석할 수 없으니까요. VAMOS도 모든 모듈이 **같은 형식으로 에러를 보고**하도록 표준을 정했습니다.

### 정의

**ErrorHandlingStandard**(에러 처리 표준)는 VAMOS의 모든 모듈이 준수해야 하는 통일된 에러 처리 규약입니다. 핵심은 **예외(Exception)를 던지지 않고**, 대신 `Result<T, VamosError>` 타입으로 에러를 반환하는 것입니다. [근거: D2.0-02 §0.3]

### Result<T, VamosError> 구조

```
모듈 A                          모듈 B
┌──────────┐                  ┌──────────┐
│          │  Result<T, Err>  │          │
│  처리    │ ──────────────→  │  처리    │
│          │                  │          │
└──────────┘                  └──────────┘

성공 시: Result<데이터, _>     ← 정상 데이터 반환
실패 시: Result<_, VamosError> ← 에러 정보 반환
                                (예외 throw 금지!)
```

### VamosError 필드 상세

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| **failure_code** | FailureCode (string) | 고유 실패 코드. 레지스트리에 등록된 코드만 사용 | "OC_I1_PARSE_FAIL" |
| **message** | string | 사람이 읽을 수 있는 에러 설명 | "의도 파악에 실패했습니다" |
| **fallback_id** | string \| null | 연결된 Fallback 전략의 ID. 없으면 null | "FB_INTENT_HEURISTIC_PARSE" |
| **trace_id** | string | 추적용 고유 ID. 디버깅과 감사에 사용 | "trc-20250315-abc123" |

[근거: D2.0-02 §0.3]

### 핵심 원칙

#### 1) 모듈 경계에서 예외(Exception) 금지

```
❌ 금지:
def process(data):
    raise ValueError("잘못된 입력")   ← 예외를 던지면 안 됩니다!

✅ 올바른 방법:
def process(data) -> Result[Output, VamosError]:
    if not valid(data):
        return Err(VamosError(
            failure_code="OC_ERR_SCHEMA_INVALID",
            message="입력 스키마 검증 실패",
            fallback_id="FB_ASK_CLARIFICATION",
            trace_id=generate_trace_id()
        ))
    return Ok(processed_data)
```

> 예외(Exception)가 내부에서 발생하더라도, **모듈 경계에서 반드시 VamosError로 변환** 후 상위에 전달해야 합니다. [근거: D2.0-02 §0.3]

#### 2) Pydantic 스키마 전수 검증

모든 내부 데이터 객체는 **BaseModel(Pydantic v2)** 기반 스키마로 정의합니다: [근거: D2.0-02 ADD-036b]

- 파이프라인 각 단계(S0→S8) 경계에서 `.model_validate()` 호출 **의무화**
- 검증 실패 시 ValidationError를 포착하여 즉시 `OC_ERR_SCHEMA_INVALID`로 변환 → Fallback 분기
- 외부 입력(API 요청, Tool 응답)도 진입 시점에 스키마 검증 수행
- **금지**: dict 또는 Any 타입으로 검증 없이 단계 간 전달하는 것

#### 3) Function Call(FC) 에러 처리 표준

| 에러 유형 | FailureCode | 처리 방법 |
|----------|-------------|----------|
| FC 스키마 불일치 | OC_ERR_FC_SCHEMA | 재시도 1회 → deny |
| FC 응답 누락/타임아웃 | OC_ERR_FC_TIMEOUT | Fallback: 다운그레이드 모드 |
| FC 응답 파싱 실패 | OC_ERR_FC_PARSE | 재시도 1회 → deny |
| FC 정책 위반 | OC_ERR_FC_POLICY | 즉시 deny (재시도 없음) |
| FC 비용 한도 초과 | OC_ERR_FC_COST | Cost Gate → downshift or stop |

[근거: D2.0-02 ADD-037b]

**공통 원칙**: [근거: D2.0-02 ADD-037b]
1. 모든 FC 호출은 try/except 블록으로 감싸고, 에러는 반드시 위 분류 코드로 변환
2. 재시도 횟수는 **최대 1회**로 제한, 재시도 후에도 실패 시 Fallback 또는 deny로 귀결
3. 모든 FC 에러는 LogEvent(`OC_FC_ERROR`)로 레지스트리에 기록

### 버전별 에러 처리 차이

| 기능 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 기본 FailureCode/Fallback | — | ✅ MUST | ✅ | ✅ |
| VamosError 계약 | — | ✅ MUST | ✅ | ✅ |
| Pydantic 스키마 검증 | — | ✅ MUST | ✅ | ✅ |
| Self-check (I-6) | — | ✅ NICE (1.0 FREEZE 범위) | ✅ | ✅ |
| SDAR 자동 수리 | — | ❌ | 부분 | ✅ |
| 검증 리포트 생성 | 미생성 | 코드 변경만 | 모든 작업 + QoD | 실시간 + 자동 회귀 |

[근거: D2.0-02 §0.7, D2.0-05 Verification Report 버전별]

### 에러 분류 체계 (5가지 카테고리)

| 카테고리 | 예시 | 자동 수리 가능? | 비유 |
|---------|------|---------------|------|
| **A. 인프라** | DB 연결 끊김, API 429 | 대부분 자동 (AR-L2) | "전선 끊어짐 → 다시 연결" |
| **B. 모델/AI** | AI 환각, 품질 저하 | 중위험 (AR-L3) | "AI가 헛소리 → 다른 모델로 전환" |
| **C. 로직** | 워크플로우 멈춤, Gate 오설정 | AR-L3~L4 | "길이 막힘 → 우회도로 찾기" |
| **D. 코드** | 버그, 회귀, 라이브러리 깨짐 | 고위험 (AR-L4) | "부품 결함 → 교체" |
| **E. 보안** | 해킹 시도, 데이터 유출 | **절대 자동 수리 불가** | "침입자 → 즉시 잠금 + 신고" |

> ⚠️ **E(보안)은 절대 자동 수리하지 않습니다.** 즉시 차단하고 사람에게 알립니다. [근거: BEGINNER_GUIDE §16.6]

### 감사/기록 원칙 (LOCK — 변경 불가)

- PASS/FAIL/Soft loop/수렴(fallback/deny/restrict) 결과는 **LogEvent로 기록**
- 단일결정 원칙 위반을 방지하기 위해, 결론이 lock된 이후에는 **downshift(축소)만 허용**
- 모든 수리에 **사람 알림 필수** (자동이라도 알림은 발송)
- **Emergency Kill Switch**: 어떤 역할이든 즉시 SDAR 비활성화 가능

[근거: D2.0-02 §7.53-1, BEGINNER_GUIDE §16.9]

> **핵심 요약 (3줄)**
> 1. 모든 모듈은 `Result<T, VamosError>` 타입으로 에러를 반환하며, **모듈 경계에서 예외(Exception) throw는 금지**됩니다.
> 2. VamosError는 failure_code, message, fallback_id, trace_id 4개 필드로 구성됩니다.
> 3. 모든 데이터는 Pydantic v2 스키마로 검증되며, dict/Any 타입의 무검증 전달은 금지됩니다.

---

# 검증 체크리스트 결과

- [x] S0~S8 9개 상태 모두 설명 — §3.1에서 모든 상태 상세 기술
- [x] 5 Phase 모두 상세 — §3.2.1~§3.2.5에서 각 Phase별 목적/입출력/Gate/에러코드 기술
- [x] TEE Loop 반복 조건 — §3.4에서 P0=3, P1=5, P2=10 및 종료 조건 기술
- [x] Circuit Breaker 3상태 (CLOSED/OPEN/HALF-OPEN) — §3.5에서 상세 기술
- [x] VamosError 계약 포함 — §3.7에서 Result<T, VamosError> 및 4개 필드 상세 기술
- [x] 9-State LOCK 표시 — §3.1에서 LOCK 명시
- [x] 근거 SOT 참조 표기 — 모든 섹션에 [근거: D2.0-0X §X.X] 형태로 표기
