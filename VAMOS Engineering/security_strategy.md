# VAMOS 보안 전략 — security_strategy.md (3-8, X1)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Must · **매트릭스 셀**: X1 (보안 전략 ①②③ + 책임 AI A16 ⑨ + 다층 방어 검증 A21)
> **위상 (로드맵 L293)**: 본 문서는 기존 정본(BASE-1.3·D2.0-07·SDAR·sot2 3-10·STRATEGY_05)의 **결정 요약 + 로드맵 바인딩**이다. 기존 정본을 대체하지 않으며 충돌 시 기존 정본 우선, 변경은 LOCK 절차.

## 1. 7개 불변 구역 (BASE-1.3 — 강제 방법)

| # | 불변 구역 | 강제 계층 (PHASE3-DEC-008 A21) |
|---|-----------|-------------------------------|
| 1 | `safety_rules` | Layer 3 NEVER_AUTO `RA_NEVER_01 modify_safety_rules` (frozenset) |
| 2 | `cost_ceiling` | Layer 1 config LOCK (cost.monthly_limit) + Layer 3 `RA_NEVER_02` |
| 3 | `approval_flow` | Layer 2 ApprovalGate + Layer 3 `RA_NEVER_03` |
| 4 | `non_goals` | Layer 3 `RA_NEVER_04 modify_non_goals` |
| 5 | `audit_format` | Layer 3 `RA_NEVER_05 change_audit_format` |
| 6 | `data_retention` | Layer 1 config(TTL) + Layer 3 `RA_NEVER_06` |
| 7 | `user_consent` | Layer 3 `RA_NEVER_07 modify_user_consent` |

- 정본: BASE-1.3 §6 (L612 "7개 불변 구역 하드코딩") · SDAR §5.1 RA_NEVER_01~10 (L594-603)
- 강제 = 3계층 독립 방어(PHASE3-DEC-008): 어느 한 계층 실패에도 나머지가 차단. NEVER_AUTO 10항목은 코드 frozenset이라 config 수정으로도 우회 불가.

## 2. Permission Matrix (정본 바인딩)

- **정본**: `docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/permission_matrix.md` — **LOCK-AP-02 Permission Level 0~5** (P0 read-only/egress-allowlist ~ P5 금융), `PermissionEnforcer` 단일 컴포넌트로 평가. (본 전략은 정본을 **참조 해석만** — 재정의 0)
- **도구 승인 정책 (DEC-003 LOCK)**: 읽기전용 = 자동 승인 / 외부 API·쓰기·코드 실행 = 사용자 확인 필수
- Lead↔Sub 위임: Sub는 Lead의 Permission Level 상한 초과 위임 불가 (LOCK-AP-05), Sub count > 2 → `LockViolation` → I-20 에스컬레이션
- HITL: Confidence < 50% → 사용자 확인 (LOCK-AP-10) — A25 REFUSE 임계(0.30, PHASE3-DEC-010)와 계층 구분 (Permission HITL은 권한 축, confidence는 판정 신뢰도 축)

## 3. 감사 로그 무결성 전략

- 형식 LOCK: **JSON Structured + trace_id 필수** (평문 금지 — LOCK Registry §5) · 변경 = `RA_NEVER_05`로 봉인
- 승인 이벤트: **해시 체인 audit trail** (변조 방지, STRATEGY_06 §? / BASE-1.3 L590)
- 전 이벤트 trace_id 연결 → S0~S8 전 구간 감사 가능 (PHASE3-DEC-004) · 6-12 Event-Logging 도메인이 EventType/FC/FB 정본

## 4. 책임 AI 체크리스트 (A16 — STRATEGY_05 §2.3 바인딩)

V0~V1 구현·운영 시 강제:
- ☐ 투자/금융 응답 → "과거 성과가 미래를 보장하지 않습니다" 면책 (disclaimer, PHASE3-DEC-009 metadata)
- ☐ 건강/웰니스 응답 → "의료 전문가 상담을 권장합니다" 면책 + 의료 행위 대체 금지(Non-goal)
- ☐ EvidenceGate: 근거 2건 미만 → 답변 거부(추측 금지) → confidence 강제 < 0.30 → REFUSE (PHASE3-DEC-010 §5.3 연계)
- ☐ NEVER_AUTO: 금전 거래·개인정보 전송·외부 API 쓰기 → 항상 사용자 승인 (Layer 3)
- ☐ 편향 탐지: 특정 종목/브랜드 반복 추천 시 경고 (V2+)
- 활용 스킬: /guardrails-validate · /input-guard · /llama-firewall

## 5. A21 다층 방어 검증 방법 (PHASE3-DEC-008 / STRATEGY_05 §3.3)

- **Phase 4 R2a 구현 시**: ① config LOCK 값 로드 → 런타임 상한 적용 테스트 ② 5-Gate 각각 독립 실행(Gate A 비활성 → 나머지 4개 동작 확인) ③ NEVER_AUTO 우회 시도 → 차단 확인
- **Phase 5 검증 시**: ④ config LOCK vs SOT LOCK 대조(D3) ⑤ NEVER_AUTO frozenset vs SDAR §5.1 대조
- ※ 본 "Defense Layer"는 내부 아키텍처 방어 계층 — PART2 "Security Layer"(버전별 보안 성숙도 2→3→4 Layer Guardrails)와 **다른 개념**

## 6. X2 실행 바인딩 (보안)
- OWASP Top 10 코드 스캔 (Critical 0건) + PII 필터링 파이프라인 검증 + consent 관리 로직 검증
- CI 통합: ruff `S`(bandit) 룰 포함(Phase 2 ci.yml 13룰 중 S) + pip-audit/cargo-audit/npm audit (PART2 V1 완료 체크 #11)
- 회귀 정합: Phase 2 ci.yml(quality/test/vamos-lint 3 job)·Hook 18과 모순 0 — 본 전략은 그 위에 보안 스캔 job을 추가 바인딩(신규 충돌 없음)

## 정본 인용
BASE-1.3 §6 L612 · SDAR §5.1 L594-603 · sot2 3-10 permission_matrix.md(LOCK-AP-02/05/10) · LOCK Registry §3(RBAC)·§5(로깅)·DEC-003 · STRATEGY_05 §2.3·§3.3 · PHASE3-DEC-008/009/010
