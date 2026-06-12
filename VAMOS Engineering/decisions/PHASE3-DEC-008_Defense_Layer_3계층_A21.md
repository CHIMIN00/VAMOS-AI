# PHASE3-DEC-008 (3-7a): 다층 방어 설계 — Defense Layer 3계층 독립 (A21)

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must

## 결정
독립 3계층 방어 체계를 확정한다. **각 계층은 다른 계층의 실패와 무관하게 단독 작동**한다.

| 계층 | 성격 | 내용 | 우회 가능성 |
|------|------|------|------------|
| **Defense Layer 1** | 정적 방어 | config.v1.toml **LOCK 값 상한선** (20키 — D13; 예: cost.monthly_limit=40000) — 코드와 별도 파일, 코드 버그와 무관하게 작동 | 코드로 우회 불가 (config가 차단) |
| **Defense Layer 2** | 동적 방어 | **5-Gate 소프트웨어 체인** (DEC-001 순서) — 각 Gate 독립 판단, Gate 간 의존성 0 | 1개 Gate 버그 시에도 나머지 4개 동작 |
| **Defense Layer 3** | 최후 방어 | **NEVER_AUTO 10항목 코드 내 frozenset 하드코딩** (SDAR §5.1 RA_NEVER_01~10) | config 수정으로도 우회 불가 — 소스 수정+재배포만 가능 |

- NEVER_AUTO 10항목 (SDAR §5.1 L594-603 LOCK 전사): RA_NEVER_01 modify_safety_rules / 02 change_cost_ceiling / 03 alter_approval_flow / 04 modify_non_goals / 05 change_audit_format / 06 alter_data_retention / 07 modify_user_consent / 08 escalate_own_privilege / 09 disable_guardrails / 10 bypass_gate
- Layer 1의 보호 대상 원천 = BASE-1.3 **7개 불변 구역** (safety, cost_ceiling, approval_flow, non_goals, audit_log, data_retention, consent)
- ※ **개념 구분 명기**: 본 "Defense Layer"는 VAMOS 내부 아키텍처 방어 계층 — PART2의 "Security Layer"(버전별 보안 성숙도: 2-Layer Guardrails→3-Layer+HMAC→4-Layer+LlamaGuard)와 **다른 개념**이다 (STRATEGY_05 §3.2 주석 동일).

## 근거 (정본 라인)
STRATEGY_05 §3.2 L90-117(3계층 정의+방어 시나리오) · SDAR §5.1 L590-603(NEVER_AUTO 10 LOCK)·L407(L3 FULL_AUTO에서도 NEVER_AUTO 절대 불가) · BASE-1.3 7개 불변(STRATEGY_05 §2.2 L46-48 인용) · D13(config LOCK 20키). 기존 LOCK 재정의 0 — 3계층 "독립성" 원칙만 신규 (LOCK Registry 신규 등록 R1-A21).

## 이유
단일 장애점 제거: PolicyGate 버그 → Layer 1 config가 비용 초과 차단 / config 파일 손상 → Layer 3 NEVER_AUTO가 위험 행동 차단 / Layer 3 코드 수정 시도 → Git 리뷰+commitlint(X2). 검증 방법은 STRATEGY_05 §3.3 (Phase 4: 계층별 독립 테스트 ①~③, Phase 5: SOT 대조 ④~⑤).

## 검토 대안 (기각)
Gate 체인 강화 단일 계층 — 소프트웨어 단일 장애점 잔존, A21 목적 미달로 기각.

## 구현 바인딩
Phase 4 R2a: 4-2(Defense Layer 3계층)·4-5(config LOCK). V0 Gate 3종 시점에도 Layer 1/3은 완전체로 구현(정적·하드코딩이라 비용 低).
