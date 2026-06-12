# PHASE4-DEC-001 (P4-0 ⑦): V0 파이프라인 프레임워크 — LangGraph 오케스트레이션 전용 예외 허용 (선택지 b)

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must · **출처**: P4-PRE A-01 (HIGH)

## 결정

**V0에서도 LangGraph StateGraph를 워크플로우 오케스트레이션 전용 예외(D2.0-02 L69 DEC-002 LOCK 범위 내)로 사용한다 — PART2 V0-STEP-4 정본 코드 유지, PHASE3-DEC-004 구현 바인딩 1줄 보정.**

- DEC-004의 **결정 본문(9-State·전이 규칙·LangGraph 사용 경계)은 무변경** — 재정의 아님. 보정 대상은 "구현 바인딩" 1줄("V0 … LangGraph 미사용")뿐이며, 이 줄 자체가 인용처(PART2 V0-STEP-4)의 실태(StateGraph 정본 코드 L1030-1048·L1123-1151)와 어긋난 오기였다.
- V0 사용 조건(= V1과 동일한 경계): StateGraph 정의·노드 간 전이에만 사용, 개별 모듈 내부 로직은 함수 호출/조건문, **Gate/Decision/정책 판정 우회 금지**, StateGraph 중첩 금지 — PART2 L1174가 이미 동일 제약을 명시.
- **Must 11 분모 라벨 연동**: STRATEGY_02 L78 "LangGraph 5-Phase 최소 동작 | Must" **무수정 보존** — GATE-03 분모 11 불변.

## 근거 (정본 라인)

- 2층 구조(로드맵 L355): 구현 상세 충돌 시 **PART2 우선** — PART2 V0-STEP-4는 LangGraph가 정본 코드(L1030-1048·L1123-1151)+규칙(L1174)+Stage Gate #8(L1195)+V0 완료 체크(L1573).
- D2.0-02 L69 LangGraph 예외 LOCK은 "오케스트레이션 한정 허용"이며 버전 한정이 아님 — V0 직선 그래프(intake→plan→execute→verify→deliver)는 예외 범위의 최소 사용.
- PHASE_B1 JSON-RPC 13 메서드 네임스페이스가 `langgraph.*`(LOCK 분모) — (a) 채택 시 명명 일관성 추가 훼손.
- PHASE_B3 의존성·STRATEGY_02 Must 라벨·V1-Phase 3 StateGraph(DEC-004 바인딩 기확정)와 전부 정합 — V0→V1 재작업 0.

## 기각 대안

(a) DEC-004 바인딩 유지 + PART2/STRATEGY_02 수정 — PART2 정본 코드 블록 2곳+규칙+Stage Gate #8+완료 체크+STRATEGY_02 Must 라벨 광범위 수정 유발(수정 면적 최대), 2층 구조의 "구현 상세는 PART2 우선" 원칙 역행, Must 11 분모 라벨 변경 리스크. 기각.

## 집행

PHASE3-DEC-004 "구현 바인딩" 줄 보정(본 세션): "V0: 5-Phase 직렬 파이프라인 + S0~S8 상태코드(PART2 V0-STEP-4) — LangGraph 미사용" → "LangGraph StateGraph를 오케스트레이션 전용 예외로 사용(Gate/Decision 판정 우회 금지)". 보정 주석에 본 ADR 참조 부기. PART2·STRATEGY_02·로드맵 수정 0.
