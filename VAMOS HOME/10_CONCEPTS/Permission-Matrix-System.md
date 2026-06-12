---
tags: [type/concept, tier/all, version/V1, responsible-ai]
aliases: [권한 매트릭스, K-041, Agent Permission Matrix, L0~L5 권한]
requested-by: A16
created: 2026-06-12
---

# Permission Matrix System (L0~L5)

## 정의
에이전트 행위를 6단계 계층적 권한으로 통제하는 체계 (K-041, V1 즉시): **Level 0 읽기 → L1 생성 → L2 수정 → L3 실행 → L4 외부통신 → L5 금융(항상 사용자 확인)**. 권한 매트릭스는 07 Gate의 PolicyCheck와 연결되며, 오버라이드는 "안전한 방향만" 원칙(D2.0-03 §4.1)을 준수한다.

## Blue Node 기본 권한 (K-041 정본)
| Node | 허용 | Ask | 불가 |
|---|---|---|---|
| Dev | L0-L3 | L4 | L5 |
| Research | L0-L1, L3 | — | — |
| Content | L0-L2 | L4 | — |
| Quant | L0-L1, L3 | — | — |
| Trading | L0-L1, L3 | L5 | — |

## 이 개념이 등장하는 모든 도메인
- [[T2-Blue-Node]] — 노드별 기본 권한 적용 대상
- [[T3-Agent-Protocol]] — permission_matrix 운영 정본(3-10)
- [[T6-Security]] — RBAC(역할 축)와 직교 운영
- [[T0-Governance]] — PolicyGate/승인 구조 상위 규칙

## 값·수치 (LOCK / 구분 주의)
- 3개 권한 축 구분: K-041 에이전트 행위 L0~L5 / **RBAC (LOCK §7.3)**: OWNER(L3,P2,₩266K)·ADMIN(L2,P2,₩93K)·OPERATOR(L1,₩40K)·VIEWER(L0,₩0) / **Autonomy Level** 정본 L0~L4(3-10) — [[Autonomy-Level-Framework]] (용어 충돌 §23 #14)
- Autonomy 기본 L1 SUPERVISED — L3에서도 Non-goal/RBAC/CostBudget/안전필터 자동 불가 (LOCK)

## 버전별 차이
- V1: 매트릭스 즉시 구현 / V2+: 세분화 보강(S7E-077 보완)

## 원본 참조
- `D:\VAMOS\docs\sot\VAMOS_STEP7_J-M_상세명세서.md` §K-041 / `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` L745 (STEP7-K 보강) / `D:\VAMOS\CLAUDE.md` §7.3
