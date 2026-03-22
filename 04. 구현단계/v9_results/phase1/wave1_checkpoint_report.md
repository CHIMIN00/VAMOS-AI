# Wave 1 Checkpoint Report

> **Pipeline**: VAMOS v9.0.0
> **단계**: Phase 1 — Wave 1 (v9-B + v9-E)
> **실행일**: 2026-03-07
> **목적**: 파일 경로 정합성 + 수량 일관성 전수 검증

---

## 1. 종합 판정

| 관점 | 검증 수 | REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | INFO | 판정 |
|------|---------|:----------:|:--------------:|:-------------:|:----:|:----:|
| v9-B 파일 경로 | ~80 | **1** | 21 | 8 | 1 | Checkpoint 통과 |
| v9-E 수량 일관성 | 248 | **0** | 0 | 0 | 0 | Checkpoint 통과 |
| **합계** | **~328** | **1** | **21** | **8** | **1** | |

**Wave 1 Checkpoint: PASS — Wave 2 진입 가능**

---

## 2. REAL_ERROR 상세 (1건)

### RE-B-001: config_loader.rs vs config.rs 파일명 불일치

| 항목 | 내용 |
|------|------|
| **관점** | v9-B (파일 경로) |
| **Check Item** | B-4 (§6 파일 경로 ↔ PHASE_B2) |
| **위치** | PART2 §6.2.3 (line ~2840) |
| **PART2 표기** | `config_loader.rs` |
| **PHASE_B2 정본** | `config.rs` |
| **Severity** | **MEDIUM** |
| **영향** | 구현 시 파일명 혼동 가능. 기능 구현에는 지장 없으나 SOT 불일치 |
| **Phase 2 조치** | PART2 수정 또는 PHASE_B2 파일명 확인 후 통일 |

---

## 3. v9-E 전수 PASS 요약

- EXACT_LOCK 89건: 전수 일치 (LOCK/FREEZE 수치 완벽 정합)
- EXACT_COUNT 112건: 전수 일치
- APPROX 41건: ±20% 범위 내 전수 일치
- DERIVED 6건: 산술 정확성 전수 확인
- §6.13 매트릭스: 행 합계(454) = 열 합계(454) 교차 검증 통과
- §7 GO/NO-GO: 16+21+14+11=62 정확 일치
- §7.6 산출물: 43개 정확 일치

---

## 4. FP 분석

| FP 원인 | 건수 | 적용 RULE |
|---------|------|----------|
| V2+/V3 전용 경로 (PHASE_B2 미포함 정상) | 14 | RULE-2 |
| CI yml 구조적 차이 (단일 통합 vs 역할별 분리) | 5 | RULE-5, XREF-V0-19 |
| 명명 차이 (i1_ vs i01_) | 2 | RULE-5, SD-02 |
| **합계** | **21** | |

FP 오판율: 21 / (21+1) = **95.5%** — 이는 GT-1의 unmatched 50건 중 실제 오류가 1건뿐이라는 의미.
프롬프트 정확도: 1/1 REAL_ERROR 정확 식별 (100%)

---

## 5. Wave 2 진입 판정

| 조건 | 결과 | 판정 |
|------|------|:----:|
| REAL_ERROR 전수 식별 | 1건 식별 완료 | PASS |
| FP 판별 완료 | 21건 판별 완료 | PASS |
| Severity 분류 | MEDIUM 1건 (BLOCKER 0건) | PASS |

**Wave 2 진입: 승인**

---

## 6. Wave 2 연계사항

- v9-B RE-B-001 `config_loader.rs` 경로 → v9-A/D에서 해당 파일의 의존성/산출물 체인 재확인 필요
- v9-E 전수 PASS → Wave 2에 영향 없음
