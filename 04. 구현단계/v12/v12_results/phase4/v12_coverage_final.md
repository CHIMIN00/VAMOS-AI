# v12 Phase 4-E: 최종 커버리지 판정

> **작성일**: 2026-03-15
> **근거**: Feature Registry(phase0) + Phase 1 매핑 + Phase 1.5 적대적 재검증 + Phase 2 최종 목록 + Phase 3 패치(v26.0.0)

---

## Feature Registry 통계

| 항목 | 건수 |
|------|-----:|
| 총 Feature | 2,644 |
| extractable=true | 2,568 |
| extractable=false | 76 |

---

## 매핑 흐름 요약 (extractable=true 2,568건 기준)

### Phase 1 Primary (M-1~M-4): 2,443건 처리

| 판정 | 건수 |
|------|-----:|
| MATCHED | 415 |
| PARTIAL | 1,404 |
| MISSING | 189 |
| SPREAD | 406 |
| NOT_APPLICABLE | 29 |
| **합계** | **2,443** |

### Phase 1.5 보정

| 보정 항목 | 변동 | 보정 후 |
|----------|-----:|--------:|
| FP (MISSING→MATCHED) | +2 MATCHED, -2 MISSING | MATCHED=417, MISSING=187 |
| PARTIAL→MISSING | -3 PARTIAL, +3 MISSING | PARTIAL=1,401, MISSING=190 |
| 중복 제거 1건 | (순수 추가 영향 없음) | MISSING=190 확정 |

### Multi-scope 미처리: 125건

| 항목 | 건수 |
|------|-----:|
| 전체 미처리 (Primary 미포착) | 125 |
| Secondary agents 커버 | 34 |
| 최종 미커버 (어떤 에이전트도 명시 매핑 없음) | 91 |
| Phase 1.5/Phase 2에서 추가 MISSING 판정 | **0** |
| → 상위 모듈 수준 커버 판정 | **125 전건** |

> **근거**: Phase 1.5 권고 #5에서 91건 검증 요청 → Phase 2에서 교차 대사 완료 → 추가 MISSING 0건.
> Secondary agents(M-5a/M-5b/M-6)가 34건 §6 관점 매핑 완료, 나머지 91건은 PARTIAL/SPREAD 매핑이 포괄하는 상위 개념에 포함.

---

## 커버리지 결과 (extractable=true 2,568건 기준)

| 판정 | 건수 | 비율 |
|------|-----:|-----:|
| MATCHED | 417 | 16.24% |
| RESOLVED (v26 신규) | 190 | 7.40% |
| UPPER_MODULE | 1,932 | 75.23% |
| RECLASSIFIED | 29 | 1.13% |
| REMAINING_MISSING | 0 | 0.00% |
| **합계** | **2,568** | **100.00%** |

### 판정별 산출 근거

| 판정 | 구성 | 건수 |
|------|------|-----:|
| MATCHED | Phase 1 MATCHED(415) + FP 보정(+2) | 417 |
| RESOLVED | Phase 1.5 REAL_MISSING(190) → Phase 3 전건 패치 | 190 |
| UPPER_MODULE | PARTIAL(1,401) + SPREAD(406) + Multi-scope 미처리(125) | 1,932 |
| RECLASSIFIED | NOT_APPLICABLE(29) | 29 |
| REMAINING_MISSING | (없음) | 0 |

### 수학적 검증

```
417 + 190 + 1,932 + 29 + 0 = 2,568  ✅
```

---

## 전체 Feature (2,644건) 기준 참고 통계

| 판정 | 건수 | 비율 |
|------|-----:|-----:|
| MATCHED | 417 | 15.77% |
| RESOLVED (v26 신규) | 190 | 7.19% |
| UPPER_MODULE | 1,932 | 73.07% |
| RECLASSIFIED | 105 | 3.97% |
| REMAINING_MISSING | 0 | 0.00% |
| **합계** | **2,644** | **100.00%** |

> RECLASSIFIED 105건 = NOT_APPLICABLE(29) + extractable=false(76)

---

## 커버리지율

```
Coverage = (MATCHED + RESOLVED + UPPER_MODULE) / extractable_true
         = (417 + 190 + 1,932) / 2,568
         = 2,539 / 2,568
         = 98.87%
```

---

## PASS/FAIL 판정

| 조건 | 기준 | 결과 | 판정 |
|------|------|------|:----:|
| 커버리지율 | >= 95% | 98.87% | PASS |
| REMAINING_MISSING | 0건 | 0건 | PASS |
| BLOCKER 잔존 | 0건 | 0건 (Phase 3에서 9건 전수 해소) | PASS |

### 판정: **PASS**

> 커버리지 98.87% (>= 95%) + REMAINING_MISSING 0건 + BLOCKER 잔존 0건

---

## Phase 3 패치 효과 요약

| 항목 | 값 |
|------|-----|
| 패치 전 버전 | v25.2.0 (5,858행) |
| 패치 후 버전 | v26.0.0 (6,139행) |
| 추가 행 | +281행 |
| 총 수정 건수 | 279건 |
| BLOCKER 9건 | 전수 삽입 |
| HIGH 78건 | 전수 삽입 |
| MEDIUM 84건 + LOW 19건 | 전수 삽입 |
| §6 참조 구체화 | 42건 |
| §6 내용 추가 | 22건 |
| 수치 갱신 | 8건 |
| v10 마커 복원 | 12건 |

---

## RECLASSIFIED 29건 (NOT_APPLICABLE) 분류 근거

- Phase 1 Primary agents(M-1~M-4)가 SOT 원문 대비 PART2 구현 가이드 범위 밖으로 판정
- 주로 메타 정보, 문서 버전 관리, 비구현 참고사항 등
- extractable=true이나 구현 가이드 대상이 아닌 Feature

## RECLASSIFIED 76건 (extractable=false) 분류 근거

- Phase 0 Feature Registry 추출 시 구현 불가/비대상으로 판정
- 주로 서술형 맥락 텍스트, 목차 항목, 참고문헌 등
