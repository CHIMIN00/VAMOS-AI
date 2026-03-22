# VAMOS v10 Phase 2: REAL_MISSING 확정 목록

> **파이프라인**: v10 Phase 2 — 대화 27
> **생성일**: 2026-03-09
> **입력**: Phase 1 M-1~M-4 MISSING + Phase 1.5 FP/FN 보정
> **PART2 버전**: v21.0.0 → **v22.0.0** (대화 28 반영) | **Feature Registry**: v10.1.0

---

## 1. 전체 통계

| 구분 | 건수 |
|------|------|
| **총 REAL_MISSING** | **1,068** |
| Phase 1 원본 MISSING | 1,140 |
| Phase 1.5 FN 제거 (MATCHED 복원) | -38 (확정 FN) |
| Phase 1.5 FP 추가 (MISSING 전환) | +3 (확정 FP) |
| Phase 1.5 POSSIBLE_FN (보류) | -37 (추후 확인) |

### 1.4 FN Reconciliation (Phase 1.5 → Phase 2 수량 대사)

| 구분 | 자동 탐지 | 확정 적용 | 차이 | 사유 |
|------|----------|----------|------|------|
| FN (definite) | 51건 | 38건 | 13건 | 13건은 다른 에이전트에서 MISSING으로 존재 (cross-version) |
| POSSIBLE_FN | 42건 | 37건 | 5건 | 5건은 다른 에이전트에서 MISSING으로 존재 (cross-version) |
| FN unique feature_ids | 50개 | - | - | D208-052가 M-2/M-3 양쪽에서 FN (51건→50 IDs) |
| FN IDs in consolidated | 49개 | - | - | 48개 feature_id는 다른 에이전트 경유로 잔존 |
| FN IDs fully excluded | 1개 | - | - | D203-065 (M-2 FN, 타 에이전트 MISSING 없음) |

> **핵심**: FN 보정은 **(feature_id, agent) 쌍** 단위로 적용. 동일 feature_id라도 다른 에이전트에서 MISSING이면 consolidated에 잔존하는 것이 정상.
> 확정 적용 수(38, 37)는 자동 탐지 수(51, 42)보다 보수적이며, 수식 `1140 - 38 - 37 + 3 = 1068`로 검증됨.


### 1.1 심각도별

| 심각도 | 건수 | 비율 | 대응 방침 |
|--------|------|------|----------|
| **BLOCKER** | **3** | 0.3% | PART2 즉시 추가 |
| **HIGH** | **612** | 57.3% | 분류 후 선택적 추가 |
| **MEDIUM** | **272** | 25.5% | PRIMARY만 추가 검토 |
| **LOW** | **181** | 16.9% | 대부분 SKIP |

### 1.2 조치별 분류

| 조치 | 건수 | 설명 |
|------|------|------|
| **PART2_ADD** | **710** | PART2에 구현 항목 추가 대상 |
| **REVIEW** | **266** | STEP7 추정 항목 — 실제 구현 필요 여부 판정 필요 |
| **SKIP** | **60** | LOW CROSSCHECK — 다른 버전에서 이미 커버 |
| **RECLASSIFY_NA** | **32** | STEP7 TITLE_ONLY → NOT_APPLICABLE 재분류 |

### 1.3 Phase 배정 분포

| 배정 | 건수 | 비고 |
|------|------|------|
| §5.2 V3-Phase 2 | 2 | BLOCKER (PARL Agent Swarm) |
| §5.3 V3-Phase 3 | 1 | BLOCKER (Agent Specialization) |
| §3 V1 (Phase TBD) | 218 | V1 PRIMARY 항목 |
| §4 V2 (Phase TBD) | 66 | V2 PRIMARY 항목 |
| §5 V3 (Phase TBD) | 20 | V3 PRIMARY 항목 |
| §2 V0 | 1 | V0 FP 전환 항목 |
| REVIEW_NEEDED (STEP7 추정) | 620 | Phase 1 보고서 §7.3 원인 참조 |
| NOT_APPLICABLE (STEP7 TITLE_ONLY) | 140 | 제목만 존재, 스펙 없음 |

---

## 2. BLOCKER 항목 (3건) — PART2 즉시 보강 필수

| # | feature_id | feature_name | version | SOT 근거 | 제안 배정 |
|---|-----------|-------------|---------|----------|----------|
| 1 | D202-130 | Agent Swarm (PARL) 병렬 실행 구현 | V3 | D2.0-02 §11.15.2, D2.0-05 §12.17.1 | §5.2 V3-Phase 2 |
| 2 | D205-067 | PARL Agent Swarm Execute 단계 | V3 | D2.0-05 §12.17.1 (TEE Execute에 PARL 옵션) | §5.2 V3-Phase 2 |
| 3 | D205-076 | Agent Specialization Protocol (자동 fork/특화/retire) | V3 | D2.0-05 §12.19, PLAN-3.0 P6-AGT-04 | §5.3 V3-Phase 3 |

### BLOCKER 분석

**공통 원인**: VAMOS_AGENT_TEAMS_SPEC §9~§10 및 D2.0-05 §12.17~12.19에 정의된 V3 고급 에이전트 기능이 PART2 §5(V3 구현)에 반영되지 않음.

- **D202-130 + D205-067**: PARL(Parallel Agent RL) 패턴은 V3 Agent Swarm의 핵심 실행 방식. 현재 PART2 §5.2 V3-Phase 2 테이블(14행)에 Agent Teams 관련 항목이 없음. D2.0-02 §11.15.2에 따르면 "Execute 단계에 PARL 패턴 통합, 오케스트레이터가 태스크 분해 → 서브에이전트 병렬 실행 (최대 100개)"로 정의됨.

- **D205-076**: Agent Specialization Protocol은 PLAN-3.0 P6-AGT-04에 등재된 V3 자기 복제 기능. 에이전트가 자동으로 fork/특화/retire하는 프로토콜. §5.3 V3-Phase 3의 "50+ Agent Mesh"와 밀접하나, 별도 구현 항목으로 명시 필요.

---

## 3. HIGH 항목 분류 (612건)

### 3.1 실질 PART2 추가 대상 (HIGH + PRIMARY) — ~143건

구현 Phase별 주요 항목:

#### §3 V1 대상 (주요)

| feature_id | feature_name | 비고 |
|-----------|-------------|------|
| CLAUDE-089 | EVX-1 Code-as-Policy 검증 구현 | EVX 시리즈 §5.2에 이미 존재 (V3) |
| CLAUDE-108 | 대화 턴 상한 구현 (P0=5, P1=10, P2=20) | LOCK-AT-009로 §6.7에 존재, §3 미배정 |
| P30-009 | DomainScore 종합 점수화 공식 구현 | PLAN-3.0 §4.4 정본 |
| P30-029 | 비용 기반 뇌 선택 정책 구현 | PLAN-3.0 §INFRA-CORE-8 |
| P30-058 | 비용 3단계 경보 체계 (70%/85%/95%) | PLAN-3.0 §9.3.2 |
| P30-061 | 고비용 모델 사용 제약 구현 | PLAN-3.0 §9.5 |
| S7AE-035 | Citation 시스템 | Phase 1.5 FP → MISSING 전환 |
| AINV-003 | 5-Agent 워크플로우 오케스트레이션 | Phase 1.5 FP → MISSING 전환 |

#### §4 V2 대상 (주요)

| feature_id | feature_name | 비고 |
|-----------|-------------|------|
| CLAUDE-203 | V2 UI: PWA (Next.js) 추가 | §11 기술 스택에 기재, §4 미배정 |
| D203-065 | 캘린더/태스크 관리 | Phase 1.5 FN → MATCHED 복원 대상이었으나 비대상 |

#### §5 V3 대상 (주요)

| feature_id | feature_name | 비고 |
|-----------|-------------|------|
| D202-064 | 화면 공유 구현 (S7B-017) | V3 전용 기능 |
| DA1-016 | 섹터/피어 그룹 비교 분석 모듈 | AI Investing V3 |
| DA1-019 | 옵션/파생상품 분석 | AI Investing V3 |

### 3.2 STEP7 추정 항목 (HIGH) — ~469건

STEP7 문서에서 추출된 항목으로, 제목만 존재하거나 다른 SRC에서 상세 스펙이 이미 정의된 항목.

**처리 방침**:
- `TITLE_ONLY` 32건 → **NOT_APPLICABLE** 재분류
- 상세 스펙 있는 항목 → SRC 원본 대조 후 PART2 반영 여부 판단
- `시스템설계`/`데이터설계` 시리즈 (S7AE-448~537) → **PART2 §5에 상위 항목으로 통합 검토**

---

## 4. MEDIUM 항목 분류 (272건)

### 4.1 실질 PART2 추가 대상 (MEDIUM + PRIMARY) — ~116건

| 버전 | 건수 | 주요 항목 예시 |
|------|------|-------------|
| V3 | ~50 | SSO 통합, 국가별 규제, 멀티테넌시, LSTM 예측, 실전거래 등 |
| V2 | ~30 | PWA, IoT 연동, 앰비언트 인텔리전스, RAG 품질 평가 등 |
| V1 | ~36 | Muon 옵티마이저, 학습 커뮤니티, 개인 위키 등 |

### 4.2 CROSSCHECK/SKIP — ~156건

다른 버전에서 이미 커버되거나 STEP7 추정 항목.

---

## 5. LOW 항목 (181건)

대부분 CROSSCHECK 역할로, PRIMARY 버전에서 이미 매핑됨. **전수 SKIP 권고**.

예외: LOCK 값 관련 항목 (비용 상한, Rate Limit, TTL 등)은 §6에서 이미 정의되어 있으므로 Phase 배정 불필요.

---

## 6. PARTIAL 재분류 (Phase 1.5 §4 후속)

Phase 1.5에서 식별된 PARTIAL 699건(§6 only) 중:
- 구현 필수 추정: ~100건 → Phase 2에서 MISSING(HIGH) 격상 검토
- 참조 유지: ~599건 → 현행 PARTIAL 유지

**본 목록에는 PARTIAL 재분류 대상이 미포함**. 대화 28에서 PART2 수정 시 함께 처리.

---

## 7. Phase 2 실행 권고

### 7.1 즉시 실행 (BLOCKER 3건)

PART2 §5.2 및 §5.3에 PARL/Agent Specialization 구현 항목 추가.

### 7.2 선택적 실행 (PART2_ADD 710건 중 실질 대상)

| 우선순위 | 대상 | 추정 건수 | 방법 |
|---------|------|----------|------|
| P1 | BLOCKER | 3 | PART2 §5 직접 추가 |
| P2 | HIGH PRIMARY (비-STEP7) | ~143 | Phase별 구현 항목 테이블에 행 추가 |
| P3 | MEDIUM PRIMARY | ~116 | Phase별 검토 후 선택 추가 |
| P4 | STEP7 HIGH (상세 있음) | ~437 | 상위 항목으로 통합 (1:N 매핑) |
| P5 | STEP7 TITLE_ONLY | ~140 | NOT_APPLICABLE 재분류 |
| P6 | LOW/CROSSCHECK | ~229 | SKIP |

### 7.3 판단 요청 사항

사용자 확인 필요:

1. **STEP7 추정 ~620건 처리**: 전수 PART2 추가 vs 상위 항목 통합 vs NOT_APPLICABLE 재분류?
2. **MEDIUM PRIMARY ~116건**: 전수 추가 vs 선별 추가?
3. **PARTIAL §6 only ~100건**: MISSING 격상 vs 현행 유지?

---

## 8. 산출물

| 파일 | 설명 |
|------|------|
| `consolidated_missing.json` | 전체 1,068건 상세 데이터 (심각도/Phase/조치 포함) |
| `v10_missing_items_list.md` | 본 보고서 |
| `v10_part2_patch_plan.md` | PART2 수정 계획 (Patch Plan) + §8 결정사항 |
| `v10_part2_line_mapping.md` | PART2 v21→v22 행번호 매핑 테이블 |

---

## 9. 대화 28 결과 — PART2 v22.0.0 반영 완료

> **기록일**: 2026-03-09

### 9.1 RESOLVED 항목 (10건)

| # | Patch | feature_id | feature_name | 반영 위치 |
|---|-------|-----------|-------------|----------|
| 1 | PATCH-B01 | D202-130 | Agent Swarm (PARL) 병렬 실행 구현 | §5.2 행 15 + §6.7 PARL 상세 |
| 2 | PATCH-B01 | D205-067 | PARL Agent Swarm Execute 단계 | §5.2 행 16 + §6.7 PARL 상세 |
| 3 | PATCH-B02 | D205-076 | Agent Specialization Protocol | §5.3 행 9 + §6.7 Specialization 상세 |
| 4 | PATCH-H02 | P30-009 | DomainScore 종합 점수화 공식 | §3 I-5 하위 체크리스트 |
| 5 | PATCH-H02 | P30-029 | 비용 기반 뇌 선택 정책 | §3 I-8 하위 체크리스트 |
| 6 | PATCH-H02 | P30-058 | 비용 3단계 경보 체계 | §3 I-9 하위 체크리스트 |
| 7 | PATCH-H02 | P30-061 | 고비용 모델 사용 제약 | §3 I-9 하위 체크리스트 |
| 8 | PATCH-H02 | CLAUDE-108 | 대화 턴 상한 (P0=5, P1=10, P2=20) | §3 I-5 하위 체크리스트 |
| 9 | PATCH-H05 | DA1-016 | 섹터/피어 비교 분석 모듈 | §5.3 행 10 |
| 10 | PATCH-H05 | DA1-019 | 옵션/파생상품 분석 | §5.3 행 10 |

### 9.2 NO_CHANGE 확정 (5건)

| Patch | feature_id | 사유 |
|-------|-----------|------|
| PATCH-H01 | CLAUDE-089~093 | §5.2에 이미 존재, M-2 CROSSCHECK 정상 |
| PATCH-H03 | AINV-003 | 기존 5-Agent Pipeline 행(§3 L1703)이 커버 |
| PATCH-H03 | AINV-066 | V2 Docker Compose에서 커버 |
| PATCH-H03 | S7AE-035 | V2 §4 별도 검토 대상 |
| PATCH-H04 | CLAUDE-203 | V2 데스크톱 중심, PWA는 V3 모바일 확장에서 처리 |

### 9.3 STEP7 620건 재분류 (옵션 B 결정)

| 분류 | 건수 | 처리 |
|------|------|------|
| **MISSING_CONFIRMED** | 620 | §6 참조로 PARTIAL 유지 — 실질 구현 항목이므로 MISSING 상태 유지 |
| **NOT_APPLICABLE** | 140 | TITLE_ONLY 확정 — 제목만 존재, 스펙 없음 |

### 9.4 HIGH PRIMARY 비-STEP7 148건 처리

| 분류 | 건수 | 처리 |
|------|------|------|
| **RESOLVED** | 7 | PATCH-H02(5) + PATCH-H05(2)로 PART2 반영 |
| **COVERED_BY_UPPER_MODULE** | 141 | 상위 모듈(§6 상세 구현 가이드)에서 커버. PART2 Phase 테이블 추가 불필요 |

### 9.5 최종 잔여 MISSING 현황

| 구분 | 건수 |
|------|------|
| 총 REAL_MISSING (원본) | 1,068 |
| RESOLVED (PART2 v22.0.0 반영) | -10 |
| **잔여 MISSING** | **1,058** |

잔여 1,058건 세부:

| substatus | 건수 | 설명 |
|-----------|------|------|
| COVERED_BY_UPPER_MODULE | 141 | HIGH PRIMARY — §6에서 커버 |
| MISSING_CONFIRMED | 620 | STEP7 실질 항목 — §6 참조 유지 |
| NOT_APPLICABLE | 140 | STEP7 TITLE_ONLY — 구현 불필요 |
| (미분류) | 157 | MEDIUM/LOW/CROSSCHECK — SKIP 또는 추후 검토 |
| `v10_part2_patch_plan.md` | Ripple Map + 수정 계획 (별도 파일) |

---

## 10. 대화 28.5 결과 — Step 1/2 분류 (2026-03-10)

> **목적**: 잔여 1,058건(1,068 - 10 RESOLVED)의 정밀 분류
> **방법**: 5차 재검토 (SOT 대조, STEP7 작업가이드 대조, 아키텍처 근거 확보)

### 10.1 Step 1 확정 분류 (67건 제외)

| # | 분류 | 건수 | 핵심 내용 |
|---|------|------|----------|
| 3-1 | NOT_APPLICABLE | 0 | 4차 재검토: STEP7-D 작업가이드 대조 → 24건 전부 구현 상세 존재 → Step 2 이동 |
| 3-2 | SUB_FEATURE_OF_EXISTING | 45 | 5차 재검토: PART2 상위 모듈 종속 확인 (HIGH 27 + MEDIUM 18). 아키텍처 근거+PART2 행번호 포함 |
| 3-3 | SKIP_CONFIRMED | 10 | 2차 재검토: PART2 100% 커버 확인. 원래 60건 중 50건 Step 2 이동, 10건만 SKIP 유지 |
| 3-4 | RESOLVED | 10 | 대화 28 v22.0.0 반영 완료. BLOCKER 3 + HIGH 7 |
| 3-5 | SECTION6_DETAILED | 1 | CLIB-023: §6.10 Cloud Library 평가 점수 체계로 커버 |
| 3-6 | DUPLICATE | 1 | D207-108 ↔ AINV-056: XAI SHAP/LIME 의미적 중복 |

### 10.2 Step 2 잔여 현황

| 구분 | 건수 |
|------|------|
| 원본 REAL_MISSING | 1,068 |
| Step 1 제외 합계 | -67 |
| **Step 2 잔여** | **1,001** |

### 10.3 최종 PART2 적용 판정

**결론: PART2에 대한 추가 수정 불필요**

잔여 1,001건은 모두 아래 사유로 PART2 변경 대상이 아님:

| 대상 | 건수 | 사유 |
|------|------|------|
| STEP7 TITLE_ONLY | ~140 | NOT_APPLICABLE — 제목만 존재, 구현 스펙 없음 |
| STEP7 실질 항목 | ~480 | MISSING_CONFIRMED — §6 상세 구현 가이드에 이미 존재 |
| HIGH PRIMARY 비-STEP7 | ~98 | COVERED_BY_UPPER_MODULE — §6 상위 모듈에서 커버 |
| MEDIUM/LOW/CROSSCHECK | ~283 | SKIP/PARTIAL — 다른 버전/모듈에서 커버 |

### 10.4 전체 흐름 요약

```
1,140 (Phase 1 원본)
  -38 (FN 제거) -37 (POSSIBLE_FN) +3 (FP 추가)
= 1,068 (REAL_MISSING 확정, 대화 27)
  -10 (RESOLVED, 대화 28 PART2 v22.0.0 반영)
  -45 (SUB_FEATURE, 대화 28.5 Step 1)
  -10 (SKIP_CONFIRMED, 대화 28.5 Step 1)
  -1 (SECTION6_DETAILED, 대화 28.5 Step 1)
  -1 (DUPLICATE, 대화 28.5 Step 1)
= 1,001 (Step 2 잔여 — PART2 추가 변경 불필요 확정)
```

산출물: `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` (6개 파일)
