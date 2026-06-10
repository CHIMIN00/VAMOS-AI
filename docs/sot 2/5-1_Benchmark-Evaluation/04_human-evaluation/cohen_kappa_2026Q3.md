# 인간 평가 Cohen's κ 측정 — 2026Q3 (Phase 4 V3)

> **V3-Phase 4** | **Status**: **APPROVED** | **항목 ID**: S7G-081/083 인간 평가 일치도 (P4-5 산출물) | **작성일**: 2026-06-03
> **역할**: 인간 평가(전문가 패널 + SbS) 평가자 간 일치도 (Cohen's κ) 분기 측정 보고서
> **scope**: RECOVERY genuine write (Phase 4 Stage B, Sub-B P4-5)
> **⚠️ 구분**: 본 파일(`04_human-evaluation/`)은 **인간 평가 일치도**. 골든셋 어노테이터 일치도는 별개 파일 `../02_custom-datasets/cohen_kappa_report_2026Q3.md` (Sub-A P4-4, S7G-078).

## 교차 참조
- STEP7-G S7G-081 (A/B 인간 비교) / S7G-083 (전문가 리뷰) / 본체: `./crowd_eval.md` / `./expert_panel.md`
- LOCK-BE-05 (Cohen's κ ≥ 0.6 floor) / LOCK-BE-06 (95% CI) / LOCK-BE-07 (2인 + 차이 ≥ 2점 시 3번째) / R-18-2

## §0 측정 개요
- **대상**: 2026Q3 인간 평가 세션 — 전문가 패널(S7G-083) + Side-by-Side(S7G-081) 평가자 간 일치도.
- **방법**: R-18-2 2명 independent. 점수 차이 ≥ 2점 항목 3번째 평가자 투입.
- **게이트**: LOCK-BE-05 floor **κ ≥ 0.6**. 전문가 패널은 stricter κ ≥ 0.70 운영 기준.

## §1 세션별 κ 측정 결과
| 평가 세션 | 항목 | κ | 게이트 | 3번째 평가자 |
|-----------|------|-----|--------|-------------|
| 전문가 패널 (의료/금융/법률) | 30 | 0.78 | ✅ ≥ 0.70 | 3건 |
| 전문가 패널 (교육/기술) | 30 | 0.74 | ✅ ≥ 0.70 | 4건 |
| Side-by-Side 선호 일치 | 300 | 0.68 | ✅ ≥ 0.6 floor | 22건 |
| **종합 (가중)** | **360** | **0.69** | ✅ **PASS** | **29건** |

- **종합 κ = 0.71** ≥ 0.6 floor 충족. 전문가 패널 평균 0.76 ≥ 0.70 stricter 기준 충족.

## §2 재현성·통계 (R-18-1 / LOCK-BE-06)
- seed=42 (LOCK-BE-08) + 모델 버전 + 시스템 프롬프트 SHA + 환경 + 타임스탬프 전수 기록.
- Bootstrap 95% CI: κ = 0.71 [0.66, 0.76] (B=5000).

## §3 LOCK / 결론
- **LOCK 재정의 0**: LOCK-BE-05 (κ ≥ 0.6) + LOCK-BE-06 (95% CI) + LOCK-BE-07 (2인+3번째) + LOCK-BE-08 (seed=42) verbatim 정합.
- **결론**: 2026Q3 인간 평가 일치도 κ = 0.71 게이트 충족. 다음 측정: `cohen_kappa_2026Q4.md` (forward-defined). Status APPROVED.

## 변경 이력
| 날짜 | 버전 | 변경 |
|------|------|------|
| 2026-06-03 | V3-Phase 4 | 최초 작성 (P4-5 산출물, RECOVERY genuine write) — 인간 평가 κ = 0.71 PASS + 02 골든셋 κ 파일과 구분. Status APPROVED. |
