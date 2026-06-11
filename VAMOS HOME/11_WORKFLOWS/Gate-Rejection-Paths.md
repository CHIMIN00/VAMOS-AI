---
tags: [type/workflow, tier/T0, version/V1, status/CORE, lock/ABSOLUTE]
aliases: [Gate 거부 분기, Gate 실패 경로, 5-Gate 실패]
description: "5-Gate 실패 시 분기 경로 — CLAUDE.md §5 Gate표 기준"
created: 2026-06-11
---

# Gate Rejection Paths (5-Gate 실패 분기)

## 한줄 요약
PolicyGate→CostGate→ApprovalGate→EvidenceGate→SelfCheckGate 5개 Gate는 우회 불가(LOCK)이며, 각 Gate 실패 시 정해진 fallback 경로로 분기한다.

## Gate 시스템 (우회 불가, LOCK — CLAUDE.md §5)
| Gate | 위치 | 역할(판정) | 실패 시 |
|------|------|------|--------|
| PolicyGate | S1~S3, S6 | block/require_approval/mask/allow | deny + 감사로그 |
| CostGate | S2~S3, S4 | normal/downshift/split/stop | FB_COST_DOWNSHIFT |
| ApprovalGate | S1~S3 | approved/denied/pending/expired | FB_REQUIRE_APPROVAL |
| EvidenceGate | S2 | sufficient/insufficient | HOLD/ESCALATE + 재검색 |
| SelfCheckGate | S5→S6 | PASS/WARN/FAIL | Soft loop 1회 → 승인/deny |

## 분기 상세
- **PolicyGate deny**: Non-goal 7개·안전 위반 → 즉시 거부 + 감사로그 (JSON, trace_id 필수)
- **CostGate**: 80% 도달 warn/force_mini(downshift), 100% block — 비용 LOCK은 [[Cost-Limits]]
- **ApprovalGate**: 승인 타임아웃 600s(P2는 300s) 미응답 → expired → 자동 거부
- **EvidenceGate insufficient**: 재검색 후에도 부족 시 결론 HOLD/ESCALATE
- **SelfCheckGate FAIL**: [[Self-Check-Loop]] Soft loop 자동 1회 → 재실패 시 사용자 승인 또는 deny

## 용어 주의
- 단독 "5-Gate"는 VAMOS-5-Gate(0-0 정본) 의미 — SDAR-Gate(6-5)·CL-Gate(6-8)와 구분 ([[Cross-Domain-Terminology]])

## 연결
- [[5-Gate-Decision-Framework]] / [[End-to-End-Request-Flow]] / [[T0-Governance]] / [[Non-Goals]]

## 원본
- `D:\VAMOS\CLAUDE.md` §5 Gate표·§7.3 비용/안전 LOCK·§20 config LOCK 값
