---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE, responsible-ai]
aliases: [5-Gate, 게이트 시스템, VAMOS-5-Gate]
created: 2026-06-11
---

# 5-Gate Decision Framework

## 정의
모든 요청이 우회 불가(LOCK)로 통과해야 하는 5단계 의사결정 게이트 체계. Policy→Approval→Cost→Evidence→SelfCheck 순서이며, 단독으로 "5-Gate"라 하면 본 VAMOS-5-Gate를 의미한다(용어충돌 #13 — SDAR-Gate(6-5)/CL-Gate(6-8 CL-G0~G4)와 구분).

| Gate | 위치 | 판정 | 실패 시 |
|------|------|------|--------|
| PolicyGate | S1~S3, S6 | block/require_approval/mask/allow | deny + 감사로그 |
| CostGate | S2~S3, S4 | normal/downshift/split/stop | FB_COST_DOWNSHIFT |
| ApprovalGate | S1~S3 | approved/denied/pending/expired | FB_REQUIRE_APPROVAL |
| EvidenceGate | S2 | sufficient/insufficient | HOLD/ESCALATE + 재검색 |
| SelfCheckGate | S5→S6 | PASS/WARN/FAIL | Soft loop 1회 → 승인/deny |

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — 5-Gate 정본 소유(0-0), 단독 사용 시 기준 의미
- [[T2-Blue-Node]] — 실행 전 Gate 통과 후 Blue Node 라우팅
- [[T6-SDAR]] — SDAR-Gate는 별개 체계(접두어 구분)
- [[T6-Cloud-Library]] — CL-G0~CL-G4 접두어로 분리(CC-004)
- [[T6-Security]] — RBAC/Autonomy와 결합된 승인 흐름

## 값·수치 (LOCK)
- Gate 우회 불가(LOCK): Policy→Approval→Cost→Evidence 필수 통과
- Self-check 임계값 P0:70 / P1:75 / P2:80, Soft loop 자동 1회만(LOCK)
- 승인 타임아웃 600s(P2=300s) 미응답 → 자동 거부

## 버전별 차이
- V1~V3 공통 적용 — Gate 구조 자체는 전 버전 불변(ABSOLUTE)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §5 / `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md`
- `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\GLOSSARY_CROSS_DOMAIN.md` (#13)
