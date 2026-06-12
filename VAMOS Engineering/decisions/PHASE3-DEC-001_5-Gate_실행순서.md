# PHASE3-DEC-001 (3-1): 5-Gate 실행 순서

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must

## 결정
5-Gate 실행 순서 = **PolicyGate → ApprovalGate → CostGate → EvidenceGate → SelfCheckGate** (LOCK — 우회 불가, 생략 불가).

## 근거 (정본 라인)
- D2.0-07 L969: "5-Gate 파이프라인: PolicyGate → ApprovalGate → CostGate → EvidenceGate → **SelfCheckGate** → 응답 전달"
- D2.0-07 L954-955: SelfCheckGate = 5번째 게이트, 정본 D2.0-02 §2.3 + CLAUDE.md §5
- LOCK Registry §2 "Gate 우회 불가: Policy→Approval→Cost→Evidence→SelfCheck 필수 통과" — 기존 LOCK과 **일치** (신규 등록 불요, 재정의 0)
- CLAUDE.md §5 Gate 표(L84-92)는 게이트별 파이프라인 위치·역할 정의표(S1~S6 중첩 구간) — 순서 주장 아님, 모순 없음

## 이유
ApprovalGate가 CostGate에 선행해야 "승인되지 않을 작업의 비용 계산·다운시프트"가 발생하지 않고, P2 승인 타임아웃(600s/300s) 동안 비용 점유가 없다. SelfCheckGate는 산출물 생성 후(S5→S6)만 의미가 있어 항상 마지막.

## 검토 대안 (기각)
- STRATEGY_05 §3.1 L85 "Policy→Cost→Approval→Evidence→SelfCheck" — 전략 문서 측 표기 오기로 판정(정본 D2.0-07과 불일치) → 본 세션에서 교정 (Engineering 문서, SOT 아님).

## 구현 바인딩
- Phase 4 R2a: V0는 Gate 3종(Policy/Cost/Approval) 우선 구현(로드맵 4-2 — 5-Gate 완성은 V1), 단 **체인 순서 자리는 5-Gate 기준으로 예약**(Evidence/SelfCheck 슬롯 stub).
- 게이트별 결과는 LogEvent + ResponseEnvelope.metadata.reasoning_trace(DEC-009)에 실행 순서대로 기록.
