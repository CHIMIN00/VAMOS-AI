---
tags: [type/workflow, tier/T0, version/V1, status/CORE]
aliases: [E2E 요청 흐름, S0-S8 전체 흐름, 5-Phase 파이프라인]
description: "사용자 요청 S0 접수부터 S8 완료까지 전체 흐름 — CLAUDE.md §5·§12 기준"
created: 2026-06-11
---

# End-to-End Request Flow (S0→S8)

## 한줄 요약
사용자 요청이 Front Mini LLM → ORANGE CORE → BLUE NODE → OTHER BRAINS → Main/Hologram LLM 4계층을 거쳐 S0~S8 상태 머신으로 처리되는 전체 흐름.

## 상태 머신 (S0~S8, CLAUDE.md §12)
```
S0_RECEIVED → S1_INTENT_PARSED(5s) → S2_EVIDENCE_READY(30s)
→ S3_DECISION_LOCKED(120s) → S4_EXECUTING(10s) → S5_OUTPUT_READY(15s)
→ S6_SELF_CHECKED → S7_MEMORY_COMMITTED → S8_DONE
```

## 5-Phase 파이프라인 (LOCK, CLAUDE.md §5)
| # | 단계 | 담당 | 산출물 | 상태코드 |
|---|------|------|--------|---------|
| 1 | Perception/Intake | Front Mini + I-1 | IntentFrame | S0→S1 |
| 2 | Reasoning/Plan | I-2 + I-5 + Gates | EvidencePack + Decision | S2→S3 |
| 3 | Action/Execute | BLUE NODE + D4 | Artifacts/Results | S4→S5 |
| 4 | Reflection/Verify | I-6 + EVX | Self-check 결과 | S6 |
| 5 | Memory/Store | I-3 + D6 | L0/L1/L2/L3 저장 | S7→S8 |

## 핵심 규칙
- Decision Lock: S3 이후 결론 변경 불가 (locked=true) — [[Decision-Lock]]
- 모든 Gate 우회 불가 — 실패 분기는 [[Gate-Rejection-Paths]] 참조
- S6 Self-check 실패 시 Soft loop 1회 — [[Self-Check-Loop]] 참조
- 최종 출력은 ResponseEnvelope(LOCK) 스키마 — [[VamosMessage-Schema]]

## 연결
- [[5-Gate-Decision-Framework]] / [[Memory-Layers]] / [[T2-Blue-Node]] / [[T6-Hologram]]

## 원본
- `D:\VAMOS\CLAUDE.md` §5(4계층/파이프라인/Gate)·§12(스키마/상태 머신)
