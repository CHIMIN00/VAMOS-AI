# RAGAS 자동 평가 설정 — ragas_config.md

> **소유 도메인**: 5-2_File-Context (목표 정의·평가 기준 설계)
> **상위 문서**: `FILE_CONTEXT_구조화_종합계획서.md` §12.4
> **측정 실행**: 5-1_Benchmark-Evaluation (CF-52-003 경계)
> **작성일**: 2026-04-12
> **Phase**: P1-1 (W12 벤치마크 기반 구축)
> **V1 범위**: 메트릭 정의·기준선·실행 주기·알림 정책. V2 범위(RAGAS 완전 자동화/CI 통합)는 Phase 2 소관(R7 준수).

---

## 1. RAGAS 메트릭 5개 (§12.4 정본)

> 종합계획서 §12.4 기준 5개가 정본. _index.md의 Context Precision은 5-1 도메인(LOCK-BE-11) 소유 추가 항목으로 별도 표기.

### 1.1 정본 메트릭 (5-2 소유 — 5개)

| # | 메트릭 | 기준선 | 하회 시 조치 | 유형 |
|---|--------|--------|------------|------|
| M1 | **Faithfulness** | ≥ 0.85 | 배포 차단 | 핵심 |
| M2 | **Answer Relevancy** | ≥ 0.80 | 배포 차단 | 핵심 |
| M3 | **Context Recall** | ≥ 0.75 | 배포 차단 | 핵심 |
| M4 | **Citation Accuracy** (VAMOS 전용) | ≥ 0.85 | 배포 차단 | VAMOS 확장 |
| M5 | **Cross-Doc Consistency** (VAMOS 전용) | 측정 시작 | 알림 | VAMOS 확장 |

### 1.2 추가 항목 (5-1 소유 — 별도 표기)

| # | 메트릭 | 기준선 | 하회 시 조치 | 비고 |
|---|--------|--------|------------|------|
| M6 | **Context Precision** | ≥ 0.75 | 배포 차단 | 5-1 LOCK-BE-11 소유. _index.md에 "측정 시작"→5-1 정본에서 LOCK-BE-11로 ≥0.75 확정. 5-2에서는 참조만 수행. |

> **참고**: 5-2 §12.4와 5-1 LOCK-BE-11의 차이점:
> - 5-2 §12.4: Faithfulness ≥ 0.85 (5-2 기준선 — 골든셋 V1 초기 목표)
> - 5-1 LOCK-BE-11: Faithfulness ≥ 0.90 (5-1 프로덕션 게이트 — 더 엄격)
> - CF-52-003 경계: 5-2는 "목표 정의·해석"이므로 V1 초기 기준선 0.85를 설정. 5-1은 프로덕션 PASS/FAIL 판정에 0.90 적용.

---

## 2. 메트릭별 측정 방법

### 2.1 M1: Faithfulness (≥ 0.85)

| 항목 | 내용 |
|------|------|
| **정의** | 답변의 모든 주장(claim)이 제공된 컨텍스트에 근거하는지 평가 |
| **수식** | `faithfulness = \|supported_claims\| / \|total_claims\|` |
| **측정 절차** | 1. LLM으로 답변에서 사실 주장(claim) 추출 (NLI 기반) → 2. 각 claim이 contexts 중 하나 이상에 의해 지지되는지 판정 → 3. 지지 비율 계산 |
| **판정 모델** | 로컬 NLI 모델 (V1: Pydantic Strict + SOT 필드 대조 — G5 활용), 고복잡도 시 Cloud 판정 (W1 Cascade) |
| **대상 데이터** | 골든 테스트셋 100 QA (golden_testset.md) |
| **Phase F 연동** | Phase F-L2(G5 환각 검증) + F-L3(W11 Attributed QA) 출력을 입력으로 활용 |

### 2.2 M2: Answer Relevancy (≥ 0.80)

| 항목 | 내용 |
|------|------|
| **정의** | 답변이 질문에 얼마나 관련되는지 평가 |
| **수식** | `relevancy = mean(cosine_similarity(question, generated_questions))` |
| **측정 절차** | 1. 답변에서 역질문(reverse question) N개 생성 → 2. 원본 질문과 역질문 간 코사인 유사도 평균 계산 |
| **임베딩 모델** | BGE-M3 (L2 LOCK Hybrid Search 기반; W3 Ensemble 구성 중 주 모델) |
| **대상 데이터** | 골든 테스트셋 100 QA |
| **판정 기준** | 0.80 이상이면 질문-답변 관련성 충분. 하회 시 답변 초점이 질문에서 벗어난 것으로 판정. |

### 2.3 M3: Context Recall (≥ 0.75)

| 항목 | 내용 |
|------|------|
| **정의** | 정답에 필요한 정보가 검색된 컨텍스트에 얼마나 포함되었는지 평가 |
| **수식** | `context_recall = \|gt_statements_attributed_to_context\| / \|gt_statements\|` |
| **측정 절차** | 1. Ground truth 답변을 개별 문장으로 분해 → 2. 각 문장이 검색된 컨텍스트 중 하나 이상에 귀속되는지 판정 → 3. 귀속 비율 계산 |
| **대상 데이터** | 골든 테스트셋 100 QA (각 QA에 ground truth + 출처 라인 명시) |
| **검색 파이프라인** | Phase E 4-Index Fusion(L11) 출력 → E-5 리랭킹 후 top-3~5 컨텍스트 |

### 2.4 M4: Citation Accuracy — VAMOS 전용 (≥ 0.85)

| 항목 | 내용 |
|------|------|
| **정의** | 답변에 포함된 출처 참조(파일명, 라인 번호)가 실제 원문과 일치하는지 평가 |
| **수식** | `citation_accuracy = \|correct_citations\| / \|total_citations\|` |
| **측정 절차** | 1. 답변에서 출처 참조 추출 (정규식: 파일명:라인, §섹션 등) → 2. 각 참조의 실제 원문 존재 확인 → 3. BERTScore ≥ 0.8 일치도 검증 (W11 Attributed QA 기준) → 4. 정확 비율 계산 |
| **연동 기술** | W11(Attributed QA: 원문 발췌+BERTScore≥0.8) + H16(Confidence Calibration) |
| **대상 데이터** | 골든 테스트셋 100 QA 중 출처 포함 QA (교차 참조 30 + 추론 20 = ~50건 예상) |
| **VAMOS 독점 이유** | 상용 AI는 출처 라인 단위 참조 불가. VAMOS는 로컬 파일 직접 접근으로 라인 단위 검증 가능. |

### 2.5 M5: Cross-Doc Consistency — VAMOS 전용 (측정 시작)

| 항목 | 내용 |
|------|------|
| **정의** | 복수 문서에서 추출한 정보 간 일관성 평가 |
| **수식** | `cross_doc_consistency = \|consistent_claims\| / \|cross_doc_claims\|` |
| **측정 절차** | 1. 교차 참조 QA에서 다중 문서 기반 주장 추출 → 2. 동일 사실에 대한 문서 간 일치 여부 판정 → 3. 일관성 비율 계산 |
| **대상 데이터** | 골든 테스트셋 교차 참조 30 QA |
| **V1 제한** | "측정 시작" — 기준선 없이 데이터 수집만 수행. V2에서 기준선 확정 예정. |
| **연동 기술** | W7(MDCure: V2→V3) 원자 명제 추출 기반. V1에서는 수동 판정. |

---

## 3. 실행 주기

| 주기 | 실행 내용 | 대상 | 비고 |
|------|----------|------|------|
| **주간** (매주 월요일) | RAGAS 5개 메트릭 전수 실행 | 골든 테스트셋 100 QA | V1 기본 주기. Phase G-6 Continuous Evaluation Loop. |
| **배포 전** (코드 변경 시) | Faithfulness + Citation Accuracy | 골든 테스트셋 100 QA | 배포 차단 게이트. 기준선 하회 시 배포 불가. |
| **월간** (매월 첫 주) | 전체 메트릭 + 추세 분석 | 골든 테스트셋 100 QA + 누적 결과 | H16 Confidence 교정 곡선 갱신. |

---

## 4. 알림 정책

### 4.1 알림 트리거

| 조건 | 알림 수준 | 대상 | 조치 |
|------|----------|------|------|
| M1 Faithfulness < 0.85 | **CRITICAL** | 개발팀 전체 | 즉시 원인 분석 + 배포 차단 |
| M2 Answer Relevancy < 0.80 | **CRITICAL** | 개발팀 전체 | 즉시 원인 분석 + 배포 차단 |
| M3 Context Recall < 0.75 | **CRITICAL** | 개발팀 전체 | 즉시 원인 분석 + 배포 차단 |
| M4 Citation Accuracy < 0.85 | **CRITICAL** | 개발팀 전체 | 즉시 원인 분석 + 배포 차단 |
| M5 Cross-Doc Consistency 급락 (전주 대비 -10%p) | **WARNING** | 컨텍스트 팀 | 원인 분석 (배포 차단 아님) |
| 모든 메트릭 주간 추세 -5%p 이상 하락 | **WARNING** | 컨텍스트 팀 | 회귀 분석 |

### 4.2 알림 채널

| 수준 | 채널 | 응답 SLA |
|------|------|----------|
| CRITICAL | 개발 채널 즉시 알림 + 이메일 | 4시간 이내 원인 분석 착수 |
| WARNING | 개발 채널 일반 알림 | 다음 주간 회의에서 논의 |
| INFO | 대시보드 기록 | 월간 리뷰 시 확인 |

---

## 5. 배포 차단 로직

### 5.1 차단 조건

```
IF any(
    faithfulness < 0.85,
    answer_relevancy < 0.80,
    context_recall < 0.75,
    citation_accuracy < 0.85
) THEN:
    BLOCK deployment
    TRIGGER CRITICAL alert
    LOG to benchmark_store (5-1 F-07)
    REQUIRE manual review + fix + re-evaluation
```

### 5.2 차단 해제 조건

```
IF all(
    faithfulness >= 0.85,
    answer_relevancy >= 0.80,
    context_recall >= 0.75,
    citation_accuracy >= 0.85
) AND:
    re_evaluation_passed = True
    reviewer_approved = True
THEN:
    UNBLOCK deployment
    LOG resolution to benchmark_store
```

### 5.3 Cross-Doc Consistency (M5) — 차단 미적용

```
# M5는 V1에서 "측정 시작" 단계 — 배포 차단 조건에 포함하지 않음.
# 급락(-10%p) 시 WARNING 알림만 발송.
# V2에서 기준선 확정 후 배포 차단 조건 추가 예정.
```

### 5.4 Phase F 연동

| Phase F Layer | RAGAS 메트릭 연동 | 역할 |
|--------------|-----------------|------|
| L1: QoD ≥ 0.6 | — | 기본 품질 게이트 (LOCK L9) |
| L2: Pydantic Strict (G5) | M1 Faithfulness | 구조적 환각 검증 → Faithfulness 기초 |
| L3: Attributed QA (W11) | M4 Citation Accuracy | 출처 검증 → Citation Accuracy 직접 연동 |
| L6: Confidence (H16) | M1, M2 | 저신뢰 응답 플래그 → Faithfulness/Relevancy 개선 |
| L7: Self-Consistency (W9) | M1 Faithfulness | 3x 합의로 환각 감소 → Faithfulness 향상 |

---

## 6. QoD 점수 체계와 RAGAS 메트릭 관계

### 6.1 LOCK L9 QoD 점수 체계 (글자 그대로 인용 — CLAUDE.md L264-266)

> **Accuracy(0.30) + Relevance(0.25) + Completeness(0.20) + Safety(0.15) + Efficiency(0.10) ≥ 0.6**

### 6.2 QoD vs RAGAS 역할 구분

| 구분 | QoD (L9) | RAGAS (W12) |
|------|----------|-------------|
| **적용 시점** | Phase F-L1 (응답 생성 직후) | Phase G-6 (주간 평가/배포 전) |
| **범위** | 개별 응답의 종합 품질 | 시스템 전체의 RAG 파이프라인 품질 |
| **기준선** | ≥ 0.6 (단일 응답 PASS) | 메트릭별 개별 기준선 (시스템 PASS) |
| **차단 대상** | 개별 응답 차단 (사용자에게 경고 표시) | 배포 차단 (시스템 릴리즈 불가) |
| **목적** | 실시간 품질 보증 | 지속적 품질 모니터링 + 회귀 탐지 |

### 6.3 QoD 5요소와 RAGAS 5메트릭 매핑

| QoD 요소 | 가중치 | RAGAS 메트릭 | 관계 |
|---------|--------|------------|------|
| **Accuracy** | 0.30 | M1 Faithfulness | Accuracy는 사실 정확성, Faithfulness는 컨텍스트 근거. 상호 보완. |
| **Relevance** | 0.25 | M2 Answer Relevancy | 동일 개념의 다른 수준 측정. QoD=개별 응답, RAGAS=시스템 평균. |
| **Completeness** | 0.20 | M3 Context Recall | Completeness는 답변 완전성, Context Recall은 검색 완전성. 인과 관계(Recall↑ → Completeness↑). |
| **Safety** | 0.15 | — | RAGAS에 직접 대응 없음. 환각 탐지(M1)와 간접 연관. |
| **Efficiency** | 0.10 | — | RAGAS에 직접 대응 없음. 실행 시간 측정은 별도. |

---

## 7. V1 실행 환경

| 항목 | V1 설정 |
|------|---------|
| **RAGAS 버전** | ragas 0.2.x (5-1 rag_benchmarks.md S7G-035 정본) |
| **실행 환경** | 로컬 (비용: 로컬 모델 100 QA = 무료) |
| **임베딩 모델** | BGE-M3 (W3 Ensemble 주 모델) |
| **판정 모델** | 로컬 NLI (V1) / Cloud claude-haiku-4-5 fallback (W1 Cascade) |
| **시드** | seed=42 (5-1 LOCK-BE-08 재현성 보장) |
| **CI** | Bootstrap 95% CI, B=5000 (5-1 LOCK-BE-06) |
| **결과 저장** | 5-1 benchmark_store/ (F-07) |

---

*변경 이력*

| 날짜 | 변경 내용 | 사유 |
|------|----------|------|
| 2026-04-12 | 초기 생성 — RAGAS 5메트릭 측정/주기/알림/차단 완비 | P1-1 W12 벤치마크 기반 구축 |
