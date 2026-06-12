# PHASE4-DEC-010 (P4-1): A22 reasoning_trace V0 수용처 + confidence V0 산출 스텁

> **결정일**: 2026-06-12 (P4-1) · **포맷**: A6 · **우선순위**: Must(I-5 차단 해소) · **출처**: P4-1 프롬프트 "측정·운영 함정" #1 (A22 수용처 이형)

## 배경 (이형 실측)

- A22 정본 위치(PHASE3-DEC-009): reasoning_trace 등 4종 키는 **ResponseEnvelope.metadata 내부**(D6 틀 — top-level 불변). 스키마 수용처 = D2.1-D5 §4.9 ResponseEnvelopeSchema(9필드, `metadata` object required, L394).
- V0 코드 정본(contracts.py·P4-0 4-1 산출물): ResponseEnvelope = **CLAUDE.md §12 5필드 LOCK**(answer/evidence/self_check/decision_ref/audit) — **metadata 필드 없음, 필드 추가 절대 금지**.
- DEC-009 자체가 두 표기를 "계층 차이(설계 vs 스키마)"로 인정하고 "어느 표기 기준으로도 top-level 불변 + 내부 확장 원칙(D6) 동일 적용"을 명시 — 본 결정은 그 틀 안의 V0 바인딩만 확정한다.

## 결정 1 — A22 V0 수용처: Decision.gates(기존 optional dict) + decision_ref 연계

1. **reasoning_trace의 V0 단일 수용처 = `Decision.gates["reasoning_trace"]`** — DEC-009 GateTraceEntry 스키마(gate/result/detail) 그대로, 실행 순서(DEC-001) append. `gates`는 D2.1-D2 §4.1 기존 optional 필드(dict)라 **DecisionSchema 20필드 FREEZE 무변경·필드 추가 0**.
   - V0 기록 범위(DEC-009 구현 바인딩 그대로): Gate 4종(Policy/Approval/Cost/Evidence) + SelfCheck **SKIP→verify 노드에서 PASS 갱신** — 5엔트리.
2. **ResponseEnvelope 연계**: `decision_ref = {decision_id, gates{}}`(§12 기존 하위 구조)에 게이트 결과 요약을 전달 — 5필드 LOCK 틀 내 dict 내부 활용으로 **top-level 불변 원칙(D6/R1-A22)의 V0 등가**.
3. **confidence 단일 출처 = Decision.confidence_score**(DEC-010·20필드 기확정) — envelope에 복제하지 않고 decision_ref로 연결(DEC-009 "단일 출처: Decision" 그대로).
4. **D2.1-D5 §4.9 ResponseEnvelopeSchema(9필드·metadata)는 V0 contracts와 별개 표현** — IPC/UI 직렬화 계층 표현으로 **P4-2(IPC)·4-3(UI [왜?] 버튼)에서 활성**. V0 contracts 25모델은 무변경.
5. evidence_sources/disclaimer는 **V1**(DEC-009 구현 바인딩 무변경 — RAG·민감 도메인 활성 시점).

## 결정 2 — confidence V0 산출 스텁 (SOT 산출식 미정의 — §1.3.1 #3 처분)

SOT(DEC-010/STRATEGY_05 §5.2)는 임계값·분기·강제 REFUSE 연계만 정의하고 **산출식은 미정의**(V0 EvidencePack 빈 스텁) — 임의 발명 금지 원칙에 따라 아래 **최소 스텁 규칙**을 본 ADR에 명기하고 V1(QoD/모델 신호 기반 실산출)에서 대체한다.

| 우선순위 | 조건 | confidence_score | 파생 level |
|---|---|---|---|
| 1 | EvidenceGate insufficient | **0.0** | REFUSE — DEC-010 강제 연계(LOCK) |
| 2 | PolicyGate block ∨ CostGate stop ∨ Approval denied | **0.0** | REFUSE(답변 거부 — 사유는 게이트 필드가 보존) |
| 3 | I-1 파싱 실패 fallback(intent="unknown") ∨ ambiguity.is_ambiguous | **0.50** | LOW(경고 + 답변 제공) |
| 4 | 그 외(전 게이트 통과·명확 intent) | **0.90** | HIGH |

- **level은 항상 score에서 단일 함수로 파생**(독립 배정 금지): ≥0.85 HIGH / ≥0.60 MEDIUM / ≥0.30 LOW / <0.30 REFUSE — 임계값은 config [confidence] LOCK 3키에서 로드(하드코딩 금지).
- 스텁 상수 0.50/0.90은 분기 경계(LOW/HIGH 구간 대표값) 선택 — 정본 임계값과 충돌 0. V0에서 MEDIUM은 자연 발생하지 않음(스텁 한계 — 단위 테스트는 score 주입으로 4분기 전수 검증).
- EvidenceGate insufficient→REFUSE 경로는 V0 스텁이 항상 sufficient이므로 **단위 테스트로 강제 검증**(P4-1 프롬프트 기확정).

## 근거
PHASE3-DEC-009(D6 틀·계층 차이 명시·V0 reasoning_trace+confidence 바인딩) · PHASE3-DEC-010(임계·REFUSE 연계) · CLAUDE.md §12(5필드 LOCK) · D2.1-D2 §4.1(gates optional 기존재) · D2.1-D5 §4.9 L394(metadata object — P4-2 활성) · PART2 §1.3.1 #3(창작 금지→스텁 명기).

## 기각 대안
- ResponseEnvelope에 metadata 필드 추가 — §12 5필드 LOCK 위반(필드 추가 절대 금지). 기각.
- D5 §4.9 9필드로 contracts ResponseEnvelope 교체 — P4-0 왕복 25/25 기준선 파괴 + §12 LOCK 충돌. 기각(P4-2에서 별개 표현으로 공존).
- confidence V0 미산출(0 고정) — DEC-003 "V0부터 산출 로직 포함"(R2a 스코프) 위반. 기각.

## 구현 바인딩
P4-1 STEP 5: i5_decision_engine(스텁 산출+gates["reasoning_trace"]) · STEP 6: verify 노드 SelfCheck SKIP→PASS 갱신 + deliver 노드 decision_ref 연계 · 테스트: REFUSE 강제 경로 + 4분기 전수.
