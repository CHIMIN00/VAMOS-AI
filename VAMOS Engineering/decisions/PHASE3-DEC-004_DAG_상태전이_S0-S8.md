# PHASE3-DEC-004 (3-4): DAG 상태 전이 S0~S8 + LangGraph 사용 경계

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must
> ⟦정본 매핑 정정 반영: D2.0-05 + D2.0-02 §2.2 — 구 PHASE_B5 오참조 아님⟧

## 결정

### 9-State 상태 머신 (D2.0-02 §2.2 LOCK 추인)
`S0_RECEIVED → S1_INTENT_PARSED(I-1) → S2_EVIDENCE_READY(I-2,I-19) → S3_DECISION_LOCKED(I-5) → S4_EXECUTING(BLUE NODE/TOOLS via I-11) → S5_OUTPUT_READY(I-4) → S6_SELF_CHECKED(I-6) → S7_MEMORY_COMMITTED(I-3+06/07) → S8_DONE`

### 전이 규칙
1. **S3 이후 결론 불변** (단일결정 원칙 — Decision locked=true)
2. **S6 FAIL 시 자동 Soft loop 1회만 허용** (LOCK §7.53): (A)재검색/재계획 or (B)재생성 or (C)deny/fallback — 2회 연속 FAIL → 게이트 결과 우선 수렴(승인/축소/deny)
3. 각 단계 경계에서 `.model_validate()` 의무 (D2.0-02 L582) + 전이 시점 LogEvent `latency_ms` 기록 (L530)
4. Circuit Breaker: Execute(S3~S4) 작동, OPEN 진입 시 S5로 전이해 실패 처리, HALF-OPEN 재진입은 S3 — P2 이상은 60초 자동 HALF-OPEN 금지·사용자 승인 필수 (D2.0-05 L186-194 LOCK)

### LangGraph 사용 경계
- **V1 기본 = 자체 경량 프레임워크** (D2.0-05 §5.1 L217 LOCK) — CORE→NODE→Sub-agent 위임 + Gate 선행 통과 + trace_id 추적
- LangGraph는 **워크플로우 오케스트레이션 전용 예외 허용** (D2.0-02 L69 DEC-002 LOCK): 노드/스텝 실행·상태 전이·체크포인트/리플레이 한정, **Gate/Decision/정책 판정 우회 금지**, 연결 시 D2.0-05 §7.3 어댑터 규칙 준수
- StateGraph 표현 시 노드 = 9-State 매핑 (D2.0-05 §12.12.2)

## 근거 (정본 라인)
D2.0-02 §2.2 L313-330(상태 머신 확정+전이 규칙) · L69(LangGraph 예외 LOCK) · L582 · D2.0-05 L191-198(9-State 매핑)·L210-217(자체 프레임워크 LOCK)·L186-189(P2 CB LOCK) · CLAUDE.md L567-573(S0~S8 + 단계 타임아웃 5s/30s/120s/10s/15s) — 전건 일치, 재정의 0.

## 이유·대안
9-State는 5-Phase 파이프라인(Perception/Reasoning/Action/Memory/Reflection)의 세분 상태로 정본 기확정. 대안(LangGraph를 V1 기본 엔진으로) — D2.0-05 §5.1 LOCK 위반으로 기각.

## 구현 바인딩
V0: 5-Phase 직렬 파이프라인 + S0~S8 상태코드(PART2 V0-STEP-4) — LangGraph 미사용. V1-Phase 3: StateGraph + Soft/Hard Loop + CB.
