---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE]
aliases: [Autonomy Level, 자율성 레벨, L0~L4]
created: 2026-06-11
---

# Autonomy Level Framework

## 정의
에이전트 자율 행동 허용 수준 체계. 정본은 3-10의 L0~L4 5단계이며, 도메인별 범위 차이가 존재한다(용어충돌 #14): 정본 L0~L4(3-10) / 운영 L0~L3(6-2) / 확장 L0~L4+NEVER(6-5).

| 레벨 | 명칭 (3-10 정본) | 의미 |
|------|------|------|
| L0 | Manual | 모든 액션에 사용자 승인 필요 |
| L1 | Assisted | 실행 전 확인 요청, 일부 자동 |
| L2 | Supervised | 자동 실행 + 이상 시 개입 |
| L3 | Conditional | 조건부 자율 — 진입은 R-13-1 HITL 승인 필수 |
| L4 | Autonomous | 90일 L3 운영 + 에러율 <1% 충족 후 전환 |

## 이 개념이 등장하는 모든 도메인
- [[T3-Agent-Protocol]] — L0~L4 정본 소유(재정의 금지), A2A Agent Mode 매핑
- [[T6-Security]] — 운영 L0~L3, 기본 L1(SUPERVISED), RBAC 결합(OWNER=L3/ADMIN=L2/OPERATOR=L1/VIEWER=L0)
- [[T6-SDAR]] — 확장 L0~L4 + NEVER_AUTO 10항목(AR-Level AR-L0~AR-L4, 기본 AR-L2)
- [[T3-A2A-Protocol]] — Agent Mode(MANUAL/SEMI_AUTO/SUPERVISED_AUTO)↔Autonomy 독립 설정

## 값·수치 (LOCK)
- Autonomy 기본 L1 — L3에서도 Non-goal/RBAC/CostBudget/안전필터는 자동 불가(LOCK)
- SDAR NEVER_AUTO: safety_rules/cost_ceiling/approval_flow/non_goals/audit_format/data_retention/user_consent/escalate_own_privilege/guardrails/gate

## 버전별 차이
- V1: 기본 L1 운영 / V2: SDAR COND(AR-L2→AR-L3 조건) / V3: SDAR ON(AR-L4, 수리성공률≥95%)

## 원본 참조
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\` / `D:\VAMOS\CLAUDE.md` §7.3·§17·§23(#14)
