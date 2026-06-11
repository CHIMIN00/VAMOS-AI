---
tags: [type/audit, tier/T0, version/V0]
aliases: [SOT 정합성 감사, 교차참조 검증, _cross-ref]
created: 2026-06-11
source: "D:\\VAMOS\\docs\\sot 2\\_cross-ref\\"
---

# SOT Consistency Audits — 검증 리포트 목록

> `docs\sot 2\_cross-ref\` 실측 (2026-06-11): **.md 리포트 26개 + JSON 47개** (36개 도메인별 crossref JSON + 베이스라인/매트릭스 JSON 11개).

## Phase 11 검증 리포트 (S11-1 ~ S11-7, 23개)

| 세션 | 리포트 | 역할 |
|------|--------|------|
| S11-1 | INTEGRITY_REPORT / SOT_CONFLICT_REPORT | 무결성 베이스라인 + SOT 충돌 스캔 |
| S11-2 | AUDIT / CROSS_MATCH / SOT_CHECK / VALIDATE | 전수 감사·교차 매칭·SOT 대조·구조 검증 |
| S11-3 | DEEP_VERIFICATION | 심층 검증 통합 |
| S11-3a | HALLUCINATION / MINICHECK | 환각 탐지 + MiniCheck 사실성 |
| S11-3b | CONSENSUS / FACT_AUDIT / PATRONUS | 합의 검증·사실 감사·Patronus 충실성(37/37 FAITHFUL) |
| S11-4 | SOT2_CROSS_REF / SOT2_DEDICATED / SOT2_QUALITY_GATE / SOT2_VALIDATE | SOT 2 교차참조·전담·품질게이트·검증 |
| S11-5 | CONFIDENCE / DRIFT / ECOSYSTEM_QA / EVAL_AUDIT / GISKARD / RAGAS | 신뢰도·드리프트·생태계 QA·평가 감사·Giskard·RAGAS(4메트릭 ALL PASS) |
| S11-6 | CROSS_EXAMINE_FIX_REPORT | 교차 심문 + 수정 집행 |
| S11-7 | FINAL_REVIEW_REPORT | 최종 리뷰 (Mode A~F 3-pass) |

## 보조 리포트 (3개) + 종합 (1개)

- `broken_references.md` — 끊어진 참조 스캔 / `cross_ref_matrix.md` — 36 도메인 교차참조 매트릭스 / `lock_consistency.md` — LOCK 정합성 (469/469 TRUE MISMATCH 0)
- `SOT2_FINAL_COMPREHENSIVE_REPORT.md` — Phase 11 종합 최종 보고 (26개+ 스킬 CRITICAL 0건)

## JSON 베이스라인

- 도메인별 crossref JSON 36개 (0-0 ~ 6-13 + Ai-investing-detail)
- `integrity_baseline.json`(87KB) / `cross_ref_matrix.json` / `lock_consistency.json` / `sot2_conflict_scan.json` / `sot2_crossref_report.json` / `sot2_internal_report.json` / `broken_references.json`

## 연결

- 결과 요약: [[Phase11-Validation-Summary]] / 잔여 이슈: [[Known-Issues-Registry]]
- 구조 참조: [[SOT2-STRUCTURE-MAP]] · [[LOCK-DECISION-REGISTRY]]
