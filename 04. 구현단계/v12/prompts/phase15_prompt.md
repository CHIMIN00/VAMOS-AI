# Phase 1.5: 적대적 재검증

> **대화**: 대화 8
> **목표**: Phase 1 MATCHED/MISSING 판정의 FP(False Positive)/FN(False Negative) 감사 → REAL_MISSING 확정
> **성격**: 독립적 검증. Phase 1의 결과를 의심하고 반증을 찾는 적대적 관점.
> **선행 조건**: Phase 1 PASS

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase15_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase 1 PASS 확인 (FAIL이면 Phase 1.5 진행 불가)
⑤ Phase 1 핵심 산출물 로드:
   - v12_phase1_report.md (Phase 1 종합 보고서 — MISSING/MATCHED 통계)
   - v12_mapping_M01_v0.json ~ v12_mapping_M06.json (7개 매핑 결과)
⑥ Phase 0 산출물 로드:
   - v12_feature_registry_final.json
   - v12_section_map.json
⑦ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업은 **Agent tool(스킬 에이전트)**을 활용하여 일관된 결과를 도출합니다.

1. **독립 검증**: 각 작업(작업 1~6)은 가능한 Agent tool로 독립 실행하여 교차 오염 방지
2. **동일 템플릿**: 모든 산출물은 본 프롬프트에 정의된 출력 포맷 준수
3. **증거 기반**: 에이전트 결과에 evidence_source + evidence_line + evidence_text 필수
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 판정 기준을 명시적으로 적용

---

## 입력 파일

### Phase 1 산출물 (검증 대상)

| # | 파일 | 경로 |
|---|------|------|
| 1 | M-1 V0 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M01_v0.json` |
| 2 | M-2 V1 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M02_v1.json` |
| 3 | M-3 V2 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M03_v2.json` |
| 4 | M-4 V3 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M04_v3.json` |
| 5 | M-5a §6 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M05a.json` |
| 6 | M-5b §6+§7 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M05b.json` |
| 7 | M-6 §1+§7(변경이력) 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M06.json` |
| 8 | Phase 1 보고서 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_phase1_report.md` |

### Phase 0 산출물 (원본 참조)

| # | 파일 | 경로 |
|---|------|------|
| 9 | Feature Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json` |
| 10 | Section Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json` |

### PART2 (원본 확인)

| 파일 | 경로 |
|------|------|
| PART2 구현단계 v25.2.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### SOT (원본 확인)

```
경로: D:\VAMOS\docs\sot\
(필요 시 개별 파일 직접 확인)
```

---

## 스킬 에이전트 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| 적대적 재검증 | v10 Phase 1.5 + v11 Phase 1.5 | 구조 계승 |
| 심각도 분류 | v6 §4-C | REAL_MISSING 심각도 판정 |
| FP 기준 강화 | v12 신규 | v11 FP율 19.7% → v12 목표 ≤10% |

### 오류 주의사항 (v11 적대적 검증 교훈)

| v11 문제 | v12 대응 |
|---------|---------|
| FP율 19.7% (44/223건) | 샘플 크기 증가 + 검증 엄격화 |
| "Stage Gate missing" 오판 | 내용 기반 검색 (라인 번호 의존 금지) |
| "changelog missing" 오판 | 문서 전체 검색 후 판정 |

---

## 작업 상세

### 작업 1: 층화 샘플링

**방법**:
1. Phase 1 MATCHED 판정 목록에서 **30건** 층화 샘플링
   - version별 비례: V0 N건 + V1 N건 + V2 N건 + V3 N건 (비례 배분)
   - 에이전트별 최소 3건
2. Phase 1 MISSING 판정 목록에서 **30건** 층화 샘플링
   - 심각도별 비례: BLOCKER 전수 + HIGH N건 + MEDIUM N건 + LOW N건
   - 에이전트별 최소 3건
3. Phase 1 PARTIAL 판정 목록에서 **15건** 샘플링
   - "§6 참조" 유형 위주
   ※ PARTIAL 15건은 plan.md 보강 항목: §6 참조 유형의 실제 커버리지 확인을 위해 추가

**총 샘플**: 75건 (MATCHED 30 + MISSING 30 + PARTIAL 15)

---

### 작업 2: FP 감사 (MISSING 중 실제 MATCHED) — FP (False Positive of MISSING = MISSING으로 판정했으나 실제로는 MATCHED)

**각 MISSING 샘플에 대해**:
1. feature_id로 Feature Registry 원본 확인
2. SOT 원본 파일에서 해당 Feature 텍스트 확인
3. PART2 v25.2.0에서 **전체 검색** (§2~§7 전범위)
   - 키워드 검색
   - 유사 표현 검색
   - §6.X 상세에서 검색
4. 발견되면 **FP** (False Positive) 판정 → 실제로는 MATCHED

**FP 판정 기준**: PART2에서 해당 Feature의 구현 지침이 실질적으로 존재하면 FP

---

### 작업 3: FN 감사 (MATCHED 중 실제 MISSING) — FN (False Negative of MISSING = MATCHED로 판정했으나 실제로는 MISSING)

**각 MATCHED 샘플에 대해**:
1. feature_id로 Feature Registry 원본 확인
2. SOT 원본 파일에서 해당 Feature 텍스트 확인
3. Phase 1에서 매핑한 PART2 위치(part2_line, part2_text)로 이동
4. 해당 PART2 텍스트가 실제로 해당 Feature를 충분히 커버하는지 검증
   - 상위 모듈 수준만 언급 → Feature 수준 미달 = **FN**
   - 실제 다른 Feature를 설명하고 있음 = **FN**
   - 충분히 커버 = MATCHED 확인

**FN 판정 기준**: PART2 매핑 위치에서 해당 Feature의 구현 지침이 실질적으로 부재하면 FN

---

### 작업 4: PARTIAL 감사

**각 PARTIAL 샘플에 대해**:
1. partial_reason 확인
2. "§6 참조"인 경우: §6.X 실제 내용 확인
   - §6.X에 충분한 구현 상세 있음 → MATCHED로 상향
   - §6.X에도 불충분 → MISSING으로 하향
   - §6.X에 부분적 → PARTIAL 유지

---

### 작업 5: REAL_MISSING 확정

**방법**:
1. FP/FN 감사 결과로 오판율 계산
   - FP율 = FP건수 / MISSING 샘플 건수
   - FN율 = FN건수 / MATCHED 샘플 건수
2. **오판율 ≤ 10%**: Phase 1 결과 신뢰 → REAL_MISSING = Phase 1 MISSING - FP + FN + PARTIAL→MISSING
   ※ FP/FN 패턴을 전체 모집단에 적용: 샘플에서 발견된 FP/FN의 특성(유형, 에이전트, 섹션)을 기준으로 전수 재검토하여 추가 FP/FN 식별
3. **오판율 > 10%**: Phase 1 결과 불신 → Phase 1 재실행 필요 (FAIL)

**REAL_MISSING 목록 확정**:
- Phase 1 MISSING 전체에서 FP 패턴 적용하여 제거
- Phase 1 MATCHED에서 FN 패턴 적용하여 추가
- PARTIAL → MISSING 상향분 추가
- PARTIAL → MATCHED 상향분 제거

---

### 작업 6: 최종 보고서 작성

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase15\v12_adversarial_report.md`

**포맷**:
```markdown
# v12 Phase 1.5 적대적 재검증 보고서

## 1. 샘플링 요약
| 대상 | 모집단 | 샘플 | 비율 |
|------|--------|------|------|
| MATCHED | X | 30 | X% |
| MISSING | X | 30 | X% |
| PARTIAL | X | 15 | X% |
| **합계** | **X** | **75** | |

## 2. FP 감사 결과 (MISSING → 실제 MATCHED)
| # | feature_id | Phase 1 판정 | 실제 | PART2 위치 | 판정 사유 |
|---|-----------|-------------|------|-----------|---------|

FP율: X/30 = X%

## 3. FN 감사 결과 (MATCHED → 실제 MISSING)
| # | feature_id | Phase 1 판정 | 실제 | 판정 사유 |
|---|-----------|-------------|------|---------|

FN율: X/30 = X%

## 4. PARTIAL 감사 결과
| # | feature_id | Phase 1 판정 | 재판정 | 사유 |
|---|-----------|-------------|--------|------|

## 5. 오판율 종합
| 지표 | 수치 | 기준 | 판정 |
|------|------|------|------|
| FP율 | X% | ≤10% | PASS/FAIL |
| FN율 | X% | ≤10% | PASS/FAIL |
| 종합 오판율 | X% | ≤10% | PASS/FAIL |

> **종합 오판율 = max(FP율, FN율)** — 두 비율 중 큰 값을 종합 오판율로 사용

## 6. REAL_MISSING 확정
| 항목 | 건수 |
|------|-----:|
| Phase 1 MISSING 원본 | X |
| - FP 제거 | -X |
| + FN 추가 | +X |
| + PARTIAL→MISSING | +X |
| **REAL_MISSING 확정** | **X** |

> ※ PARTIAL→MATCHED 상향분은 MISSING 기반에 미포함이므로 감산 불필요

## 7. REAL_MISSING 심각도 분류
| 심각도 | 건수 |
|--------|-----:|
| BLOCKER | X |
| HIGH | X |
| MEDIUM | X |
| LOW | X |

## 8. Phase 1.5 판정: PASS/FAIL
(오판율 ≤10%: PASS, 초과: FAIL → Phase 1 재실행)
```

---

## 교차검증 ④

교차검증은 보고서 §5~§7에 포함:
- FP/FN 감사 결과 → 오판율 계산
- REAL_MISSING 수학적 검증 (합산 확인)
- 심각도 분류 타당성

---

## 산출물 전수 목록

| # | 파일 | 경로 |
|---|------|------|
| 1 | 적대적 재검증 보고서 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase15\v12_adversarial_report.md` |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **적대적 관점 유지**: Phase 1을 "맞다"고 가정하지 말 것. 반증을 적극적으로 찾을 것
2. **전범위 검색**: MISSING 판정 FP 검사 시 PART2 전체(§1~§7)에서 검색. 한 섹션만 보고 판정 금지
3. **원본 대조 필수**: 모든 판정에 SOT 원본 + PART2 원본 양쪽 확인
4. **환각 금지**: "발견" 시 반드시 PART2 행 번호 + 텍스트 인용
5. **v11 FP 교훈 적용**: "Stage Gate missing" 같은 구조적 오판 방지 — 전체 구조 파악 후 판정
6. **통계 교차검증**: REAL_MISSING = MISSING - FP + FN + PARTIAL→MISSING 수식 검증
7. **필드 값 enum 준수**: 판정값은 `MATCHED`/`MISSING`/`PARTIAL`/`SPREAD`/`NOT_APPLICABLE`만, 심각도는 `BLOCKER`/`HIGH`/`MEDIUM`/`LOW`만 허용. Phase 0~1에서 사용된 priority/category/source_group 값 변경 금지

---

## 완료 시 수행

1. 산출물 파일 존재 확인
2. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase15": {
       "status": "completed",
       "conversation": "대화 8",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. 오판율 > 10%이면 FAIL → Phase 1 재실행 지시
4. BLOCKER > 0이면 즉시 보고
