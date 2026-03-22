# v12 Phase 2-A: v10 교차 대사

> **작성일**: 2026-03-15
> **목적**: v12 독립 검증 REAL_MISSING 190건 vs v10 consolidated_missing 1,068건 교차 비교
> **입력**: v12 adversarial_report.md, v12 mapping M01~M06, v10 consolidated_missing.json, v10_step2_integrated_result.json, PART2 v25.2.0

---

## 방법론

1. **v12 REAL_MISSING 190건**: Phase 1 MISSING(M-3: 177, M-4: 12 = 189) - FP 2건 + PARTIAL->MISSING 3건 = 190건 (adversarial report 확정)
   - 파일 데이터 기준 191건이나, v12_C09b_557(PagedAttention/vLLM 최적화)은 v12_C09b_451(PagedAttention/vLLM 최신)과 동일 개념 중복으로 보고서 기준 190건 적용
2. **v10 consolidated_missing 1,068건** -> Step2 분류: EXACT_MATCH 11, UPPER_MODULE 514, RECLASSIFIED 276, TRUE_MISSING 200
3. **매칭 방식**: feature_id 체계가 다르므로(v12_CXX_NNN vs DXXX-NNN/S7XX-NNN 등) feature_name 기반 내용 대조
   - 정규화 후 문자열 포함/일치 + 키워드 Jaccard 유사도 사용
   - 매칭 점수 30점 이상을 유효 매칭으로 판정

---

## 교차 비교 요약

| 조합 | 건수 | 비고 |
|------|-----:|------|
| v12 MISSING + v10 TRUE_MISSING (양쪽 확정 MISSING) | **2** | v25.2.0에서도 미해소 |
| v12 MISSING + v10 MATCHED (v12만 누락) | **17** | v10에서는 UPPER_MODULE/RECLASSIFIED로 해소 판정 |
| v10 TRUE_MISSING + v12 MATCHED (v10만 누락, v12 해소) | **37** | v12에서 매핑 확인됨 |
| v12 MISSING + v10 없음 (v12 신규) | **172** | v10 미분석 25개 SOT에서 추출된 신규 Feature |
| v10 TRUE_MISSING only (v12 미대조) | **161** | v10 고유 Feature, v12 SOT에 미포함 |

### 참고: v12 vs v10 SOT 범위 차이

| 항목 | v10 | v12 |
|------|-----|-----|
| SOT 파일 수 | 43개 | 68개 (+25) |
| Feature Registry 총 건수 | 3,940 | 2,644 |
| Feature 추출 방식 | STEP6 산출물 기반 | 68개 SOT 전수 재추출 |

v12는 25개 추가 SOT(IDEA-*.md, PLAN-3.0, MASTER_SPEC 등)에서 신규 Feature를 추출하여 v10에 없는 172건의 MISSING이 발생. 반대로 v10의 3,940건 중 상당수가 v12에서 재구성/통합되어 v10 고유 Feature 161건이 v12에 미대조.

---

## v10 TRUE_MISSING 200건 반영 상태

v10 Phase 2에서 TRUE_MISSING 200건을 PART2 v23.0.0에 `<!-- <feature_id> v23 -->` 마커와 함께 삽입.
현재 PART2 v25.2.0(5,858행)에서 마커 존재 여부 확인:

| 상태 | 건수 |
|------|-----:|
| v25.2.0에 v23 마커 존재 (반영 확인) | **188** |
| v25.2.0에 v23 마커 미존재 (반영 미확인) | **12** |

### 반영 미확인 12건 상세

| # | v10 feature_id | feature_name | severity | 비고 |
|---|---------------|--------------|----------|------|
| 1 | D205-138 | 학습 커뮤니티 (스터디 그룹/공유/토론/멘토-멘티) | MEDIUM | v12_C09b_346에서 MATCHED |
| 2 | D207-084 | 국가별 규제 적응 | MEDIUM | |
| 3 | D207-116 | 웰니스 커뮤니티 (V3 익명 참여) | MEDIUM | v12_C09b_397에서 MATCHED |
| 4 | S7FI-180 | 장기 평가 추적 | MEDIUM | |
| 5 | S7FI-239 | 글로벌 확장 전략 | MEDIUM | |
| 6 | S7FI-247 | 확장 시장 진입 | MEDIUM | |
| 7 | S7FI-248 | M&A 전략 | MEDIUM | |
| 8 | S7FI-262 | 장기 재무 예측 | MEDIUM | |
| 9 | S7NP-055 | 동료 학습 매칭 | MEDIUM | |
| 10 | S7NP-065 | 학습 커뮤니티 | MEDIUM | v12_C09b_346에서 MATCHED |
| 11 | S7NP-121 | 웰니스 커뮤니티 | MEDIUM | v12_C09b_397에서 MATCHED |
| 12 | S7NP-185 | B2B 컨설팅 모델 | MEDIUM | v12_C09b_469에서 MATCHED |

> **분석**: 12건 모두 MEDIUM 심각도. 5건은 v12에서 별도 Feature로 MATCHED 확인됨. 나머지 7건은 v23->v25 버전 업 과정에서 마커가 제거되었거나 섹션 재구성으로 이동된 것으로 추정. BLOCKER/HIGH 미반영 0건.

---

## 상세 목록

### A. 양쪽 모두 MISSING (확정 MISSING) -- 2건

v12와 v10 모두 PART2에 구현 지침이 부재한 것으로 판정된 항목.

| # | v12 ID | v12 Name | v12 Sev | v10 ID | v10 Name | v10 Sev | Score |
|---|--------|----------|---------|--------|----------|---------|------:|
| 1 | v12_C10_042 | VaR 위험 경고 및 감정적 투자 방지 | MEDIUM | S7NP-110 | 감정적 투자 방지 | LOW | 80 |
| 2 | v12_C11_236 | 커스텀 조건 알림 규칙 엔진 | MEDIUM | S7AE-549 | 알림 규칙 엔진 | HIGH | 65 |

> S7AE-549(알림 규칙 엔진)는 v10에서 TRUE_MISSING으로 분류되었으나, v23 마커(S7FI-056)와 별개 항목. S7FI-056은 "알림 규칙"으로 v23에 반영됨. S7AE-549는 "알림 규칙 **엔진**"으로 엔진 구현 스펙이 별도로 필요.

### B. v12 MISSING + v10 MATCHED (v12만 누락, v10 해소) -- 17건

v12에서 MISSING이나 v10에서는 UPPER_MODULE 또는 RECLASSIFIED로 해소 판정된 항목. v25.2.0에서 재확인 필요.

| # | v12 ID | v12 Name | v12 Sev | v10 ID | v10 Name | v10 분류 | Score |
|---|--------|----------|---------|--------|----------|---------|------:|
| 1 | v12_C08_015 | TradingAnalysisAgent 구현 | MEDIUM | TEAM-021 | TradingAnalysisAgent 구현 (투자 분석, AINV 연동) | UPPER_MODULE | 85 |
| 2 | v12_C09b_200 | 플러그인 개발 도구 (Plugin Development Kit) | HIGH | S7JM-200 | 플러그인 개발 도구 | UPPER_MODULE | 80 |
| 3 | v12_C09b_424 | Yi-Lightning (01.AI) | LOW | D204-031 | Yi-Lightning 01.AI 경량 모델 참조 | UPPER_MODULE | 85 |
| 4 | v12_C09b_460 | MoA 평가 기준 | HIGH | S7NP-176 | MoA 평가 기준 | UPPER_MODULE | 100 |
| 5 | v12_C09b_463 | PolyBench | MEDIUM | S7NP-179 | PolyBench | RECLASSIFIED | 100 |
| 6 | v12_C09b_464 | MMLU-Pro | MEDIUM | S7NP-180 | MMLU-Pro | UPPER_MODULE | 100 |
| 7 | v12_C09b_470 | 오픈소스 듀얼 라이선스 | MEDIUM | S7NP-186 | 오픈소스 듀얼 라이선스 | RECLASSIFIED | 100 |
| 8 | v12_C09b_476 | 크립토 온체인 분석 | LOW | S7NP-192 | 크립토 온체인 분석 | UPPER_MODULE | 100 |
| 9 | v12_C09b_479 | Cross-Device Seamless State Sync | MEDIUM | S7NP-195 | Cross-Device Seamless State Sync | UPPER_MODULE | 100 |
| 10 | v12_C09b_538 | AutoGen 대화 패턴 참조 | HIGH | S7JM-124 | AutoGen 대화 패턴 참조 | UPPER_MODULE | 100 |
| 11 | v12_C09b_547 | IDE 플러그인 (VSCode) | HIGH | S7BG-059 | IDE 플러그인 (VSCode Extension) | UPPER_MODULE | 85 |
| 12 | v12_C09b_192 | API 문서 자동 생성 | HIGH | S7BG-057 | 문서 자동 생성 | UPPER_MODULE | 65 |
| 13 | v12_C09b_128 | VBS-12 에이전트 성능 벤치마크 | HIGH | S7FI-091 | 성능 벤치마크 | RECLASSIFIED | 65 |
| 14 | v12_C12_029 | 오디오 감정 분석 | MEDIUM | S7JM-024 | 오디오 감정 분석 | UPPER_MODULE | 100 |
| 15 | v12_C12_123 | IoT/스마트홈 연동 | LOW | D203-067 | IoT/스마트홈 연동 구현 | UPPER_MODULE | 85 |
| 16 | v12_C12_196 | 자동 온톨로지 구축 | HIGH | S7JM-261 | 자동 온톨로지 구축 | UPPER_MODULE | 100 |
| 17 | v12_C03_045 | IoT Smart Home Integration | LOW | D203-067 | IoT/스마트홈 연동 구현 | UPPER_MODULE | 32 |

> **해석**: 17건 중 14건이 v10에서 UPPER_MODULE(상위 모듈 커버), 3건이 RECLASSIFIED(범위 외). v10 판정이 "상위 모듈에서 커버된다"고 본 항목을 v12에서는 세부 구현 스펙 부재로 MISSING 판정. 이는 v12의 Feature 정의가 v10보다 세분화(granular)되어 발생한 차이.
>
> **조치 권고**: 17건 중 HIGH 이상 7건(#2, 4, 10, 11, 12, 16, v12_C09b_200/460/538/547/192/196 + v12_C09b_128)은 v25.2.0에서 §6 상세 구현 가이드에 커버되는지 재확인 필요.

### C. v10 TRUE_MISSING + v12 MATCHED (v10 해소 확인) -- 37건

v10에서 TRUE_MISSING(PART2 패치 필요)이었으나, v12 독립 검증에서는 MATCHED로 판정된 항목. v23 패치 또는 이후 PART2 업데이트로 해소된 것으로 확인.

| # | v10 ID | v10 Name | v12 ID | v12 Name |
|---|--------|----------|--------|----------|
| 1 | D203-111 | 시간 여행 디버깅 | v12_C11_039 | Time-Travel Debugging 상태 복원 |
| 2 | D206-039 | 작업 중단 복원 (task_checkpoint) | v12_C04_017 | 작업 중단 복원 기능 |
| 3 | D206-115 | 개인 멀티미디어 라이브러리 | v12_C12_068 | 개인 멀티미디어 라이브러리 |
| 4 | D206-117 | MemGPT/Letta 패턴 통합 | v12_C09b_441 | MemGPT/Letta 패턴 |
| 5 | D206-217 | 지식 기반 의사결정 지원 (SWOT) | v12_C12_205 | 지식 기반 의사결정 지원 |
| 6 | D206-218 | 지식 기반 글쓰기 지원 | v12_C12_205 | 지식 기반 의사결정 지원 |
| 7 | D206-220 | 지식 기반 개인 어시스턴트 (V3 심화) | v12_C12_204 | 지식 기반 개인 어시스턴트 |
| 8 | D206-222 | 스크린 캡처 지식화 (Microsoft Recall 로컬 버전) | v12_C12_178 | 스크린 캡처 지식화 |
| 9 | D206-226 | 시간 기반 지식 관리 | v12_C09b_246 | 시간 기반 지식 관리 |
| 10 | D206-232 | 예측적 지식 서핑 | v12_C09b_273 | 예측적 지식 서핑 |
| 11 | D207-114 | 개인 감정 패턴 학습 | v12_C09b_370 | 개인 감정 패턴 학습 |
| 12 | D207-176 | 공감 대화 엔진 (Carl Rogers) | v12_C09b_371 | 공감 대화 엔진 |
| 13 | D203-110 | 앰비언트 인텔리전스 | v12_C03_070 | Ambient Intelligence |
| 14 | S7FI-283 | 소셜 미디어 분석 | v12_C11_208 | 소셜 미디어 투자 감성 분석 |
| 15 | S7JM-123 | CrewAI 역할 패턴 참조 | v12_C09b_537 | CrewAI 역할 기반 에이전트 참조 |
| 16 | S7JM-201 | 데이터베이스 관리 도구 | v12_C09b_201 | 데이터베이스 관리 도구 |
| 17 | S7JM-243 | 폴더/노트북 구조 | v12_C09b_243 | 폴더/노트북 구조 |
| 18 | S7JM-244 | Zettelkasten 방법론 구현 | v12_C12_187 | Zettelkasten 방법론 구현 |
| 19 | S7JM-247 | 지식 성숙도 추적 | v12_C12_190 | 지식 성숙도 추적 |
| 20 | S7JM-267 | 개인 위키 | v12_C12_201 | 개인 위키 |
| 21 | S7JM-273 | 예측적 지식 서핑 | v12_C09b_273 | 예측적 지식 서핑 |
| 22 | S7JM-274 | 지식 기반 개인 어시스턴트 | v12_C12_204 | 지식 기반 개인 어시스턴트 |
| 23 | S7JM-275 | 지식 기반 의사결정 지원 | v12_C12_205 | 지식 기반 의사결정 지원 |
| 24 | S7JM-276 | 지식 기반 글쓰기 지원 | v12_C12_205 | 지식 기반 의사결정 지원 |
| 25 | S7NP-017 | 폼 자동 입력 | v12_C09b_298 | 폼 자동 입력 |
| 26 | S7NP-031 | Notion/Obsidian 통합 | v12_C09b_549 | Obsidian 통합 |
| 27 | S7NP-048 | 간격 반복 (Spaced Repetition) | v12_C09b_330 | 간격 반복 시스템 |
| 28 | S7NP-109 | 번아웃 예방 | v12_C09b_387 | 번아웃 예방 |
| 29 | S7NP-190 | FinGPT 활용 | v12_C09b_474 | FinGPT 활용 |
| 30 | S7NP-198 | Ambient Intelligence | v12_C03_070 | Ambient Intelligence |
| 31 | S7JM-057 | 인포그래픽 자동 생성 | v12_C12_047 | 인포그래픽 자동 생성 |
| 32 | S7NP-065 | 학습 커뮤니티 | v12_C09b_346 | 학습 커뮤니티 |
| 33 | S7NP-121 | 웰니스 커뮤니티 | v12_C09b_397 | 웰니스 커뮤니티 |
| 34 | S7NP-185 | B2B 컨설팅 모델 | v12_C09b_469 | B2B 컨설팅 모델 |
| 35 | S7JM-058 | 마인드맵 자동 생성 | v12_C09b_550 | 마인드맵 자동 생성 |
| 36 | S7NP-051 | 학습 분석 대시보드 | v12_C09b_338 | 학습 분석 대시보드 |
| 37 | S7NP-057 | 투자 교육 특화 | v12_C09b_333 | 투자 교육 특화 |

> **해석**: 37건 중 대다수가 지식관리(D206-xxx), 교육/웰니스(S7NP-xxx), 멀티모달(S7JM-xxx) 관련. v12에서 이 Feature들이 PART2에서 MATCHED/PARTIAL로 판정됨. 이는 v23 패치 반영 또는 v23 이후 PART2 업데이트(v24~v25.2.0)로 커버리지가 확장된 결과.

### D. v12 MISSING + v10 없음 (v12 신규) -- 172건

v10 SOT에 포함되지 않은 v12 고유 Feature 중 MISSING으로 판정된 항목. v12가 25개 추가 SOT에서 추출한 Feature.

심각도별 분포:

| 심각도 | 건수 |
|--------|-----:|
| BLOCKER | 9 |
| HIGH | 68 |
| MEDIUM | 77 |
| LOW | 18 |
| **합계** | **172** |

**BLOCKER 9건** (v12 고유 신규):

| # | v12 ID | Feature Name |
|---|--------|--------------|
| 1 | v12_C09a_037 | Self-RAG 자기 반성 RAG |
| 2 | v12_C09b_451 | PagedAttention / vLLM 최신 |
| 3 | v12_C09b_557 | PagedAttention / vLLM 최적화 (v12_C09b_451 중복) |
| 4 | v12_C11_151 | LLM 비용 최적화 시스템 |
| 5 | v12_C12_170 | 자율 코딩 에이전트 |
| 6 | v12_C13_003 | 에이전트 공유 TaskBoard |
| 7 | v12_C13_008 | 추론 모드 통합 (Reasoning Budget) |
| 8 | v12_C13_013 | Personal Constitution 시스템 |
| 9 | v12_C13_025 | EU AI Act 위험 분류 자동 평가 |
| 10 | v12_C13_034 | 사용자 피드백 수집 시스템 |

> #3(v12_C09b_557)과 #2(v12_C09b_451)는 동일 개념(PagedAttention/vLLM) 중복. 실질 BLOCKER는 9건.

### E. v10 TRUE_MISSING only (v12 미대조) -- 161건

v10에서 TRUE_MISSING(200건)이나 v12 Feature Registry에 대응 Feature가 없어 교차 매칭이 불가한 항목. v10 고유 SOT에서 추출된 Feature.

심각도별 분포:

| 심각도 | 건수 |
|--------|-----:|
| HIGH | 120 |
| MEDIUM | 35 |
| LOW | 6 |
| **합계** | **161** |

주요 도메인별 분류:

| 도메인 | 건수 | 대표 항목 |
|--------|-----:|----------|
| S7AE 운영 항목 (E-024~E-092) | ~60 | 운영/모니터링 세부 항목 |
| S7NP 교육/웰니스 | ~25 | 학습경로, 퀴즈, 수면개선, 운동트래커 |
| S7FI 인프라/재무 | ~20 | 작업큐서버, CDN, 방화벽, 블랙-리터만 |
| S7JM 멀티모달/도구 | ~15 | 스타일트랜스퍼, 화자분리, 코드변환 |
| D2XX 구현 상세 | ~20 | 배치처리, 프롬프트라이브러리, OAuth2 |
| 기타 | ~21 | AINV, CLIB, TEAM 등 |

> **해석**: 161건 중 ~60건이 S7AE 운영 항목(E-024~E-092)으로, STEP7 상세명세서의 운영 체크리스트 수준 항목. v12 SOT 재구성 시 이들은 운영 항목으로 통합되었거나 extractable=false로 분류된 것으로 추정. 나머지 ~100건은 교육, 웰니스, 인프라, 금융 도메인의 세부 Feature로 v12 SOT에 대응 항목 없음.

---

## 종합 분석

### 1. v12 REAL_MISSING 190건의 v10 대비 위치

| 구분 | 건수 | 비율 |
|------|-----:|-----:|
| v10에도 누락 (확정 MISSING) | 2 | 1.1% |
| v10에서 해소 판정 (재확인 필요) | 17 | 8.9% |
| v10에 없음 (v12 신규) | 172 | 90.0% |
| **합계** | **191** | 100% |

> 주: 파일 데이터 기준 191건 (v12_C09b_557 중복 포함). 보고서 기준 190건.

### 2. 교차 검증의 시사점

1. **v12 MISSING의 90%가 v12 고유**: v10에서 분석하지 않은 25개 추가 SOT(IDEA-*.md, PLAN-3.0 등)에서 추출된 Feature. v10의 검증 범위 밖이므로 v12 독립 검증 결과가 유일한 판정 근거.

2. **양쪽 확정 MISSING은 단 2건**: 감정적 투자 방지(v12_C10_042), 알림 규칙 엔진(v12_C11_236). 이 2건은 v10 Phase 2에서도 TRUE_MISSING으로 패치했으나, v12에서도 여전히 MISSING. v23 패치가 불충분했거나 v12의 Feature 정의가 더 엄격한 것으로 판단.

3. **v10 해소 17건의 의미**: v10에서 UPPER_MODULE/RECLASSIFIED로 "상위 모듈 커버" 또는 "범위 외"로 판정한 항목을 v12에서는 세부 구현 스펙 부재로 MISSING 판정. Feature 세분화(granularity) 차이에 기인. Phase 3 패치 시 §6 상세 구현 가이드 존재 여부 우선 확인 필요.

4. **v10 TRUE_MISSING 200건의 v25.2.0 반영률**: 188/200 = **94.0%** 반영 확인. 미확인 12건은 모두 MEDIUM이며 BLOCKER/HIGH 미반영 0건. v23->v25 버전업 과정에서 섹션 재구성 시 일부 마커 소실 추정.

### 3. Phase 3 권고

| 우선순위 | 권고 | 대상 |
|----------|------|------|
| BLOCKER | v12 BLOCKER 9건 패치 | 섹션 D 중 BLOCKER 9건 |
| HIGH | v12 HIGH 68건 + 섹션 B의 HIGH 7건 패치 | 75건 |
| MEDIUM | v10 미반영 12건 PART2 존재 여부 재확인 | 마커 소실 12건 |
| LOW | 섹션 E의 161건 중 v12 SOT 미포함분은 v12 범위 외 처리 | 확인만 |

---

## 산출물

| # | 파일 | 위치 | 비고 |
|---|------|------|------|
| 1 | 본 보고서 | `phase2/v12_v10_crosscheck.md` | v12-v10 교차 대사 결과 |
| 2 | 교차 대사 원본 데이터 | `_crosscheck_results.json` | JSON 원본 (자동 생성) |
| 3 | 교차 대사 스크립트 | `_crosscheck.py` | 재현 가능 스크립트 |
