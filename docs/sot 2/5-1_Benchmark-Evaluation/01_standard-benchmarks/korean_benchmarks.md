# Korean Benchmarks — 한국어 특화 벤치마크 채점 규칙 및 실행 파라미터

> **Phase**: 1-A (P1-1)
> **범위**: S7G-011 (KoBEST), S7G-012 (KLUE), S7G-013 (LogicKor), S7G-014 (CLIcK)
> **작성일**: 2026-04-12
> **상태**: V1 정의 완료

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|-----------|----------|
| STEP7-G S7G-011~014 | Part 2 한국어 특화 벤치마크 목표값/평가 방식/우선순위 |
| BENCHMARK_EVALUATION_상세명세.md §A-4 | LogicKor 채점: GPT-4 Judge, 1~10 척도 |
| AUTHORITY_CHAIN.md LOCK-BE-03 | LogicKor ≥ 8.0/10 (GPT-4 Judge 기준) |
| AUTHORITY_CHAIN.md LOCK-BE-06 | Bootstrap 95% CI 필수 |
| AUTHORITY_CHAIN.md LOCK-BE-08 | seed=42 고정 |
| CONFLICT_LOG C-02 | LogicKor 척도 불일치 — STEP7-G 85+(백분율) vs 상세명세 8.0/10(judge 절대). 병행 유지 |
| CONFLICT_LOG C-05 | KoBEST 목표값 — STEP7-G 정본 "평균 ≥ 88"으로 통일 |
| CONFLICT_LOG C-06 | KLUE 목표값 — STEP7-G 정본 "평균 ≥ 85"로 통일 |
| Phase 0 F-01 | benchmark_runner.py — 러너 프레임워크 |
| Phase 0 F-02 | schemas/benchmark_result.schema.json — 결과 스키마 (필수 6필드) |
| Phase 0 F-05 | promptfoo.yaml — 기존 2건 설정 (확장 대상) |

---

## S7G-011: KoBEST (Korean Benchmark Evaluation of Semantic Textual similarity)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-011 |
| **우선순위** | CRITICAL |
| **버전** | V1 |
| **목표** | 평균 ≥ 88 (STEP7-G 정본, CONFLICT_LOG C-05 참조) |
| **Phase 0 상태** | 미매핑 (§6 I-05 — Phase 1 신규 작성) |

### 입력 포맷

KoBEST는 5개 서브태스크로 구성:

| 서브태스크 | 설명 | 유형 |
|-----------|------|------|
| BoolQ | 예/아니오 질의 | 이진 분류 |
| COPA | 원인/결과 추론 | 다중 선택 |
| WiC | 단어 의미 구별 | 이진 분류 |
| HellaSwag | 상황 완성 추론 | 다중 선택 |
| SentiNeg | 부정 감성 분석 | 이진 분류 |

```
[BoolQ 예시]
지문: {passage}
질문: {question}
답: 예 / 아니오

[COPA 예시]
전제: {premise}
선택지:
1. {alternative_1}
2. {alternative_2}
질문: 원인/결과는?
답: 1 또는 2
```

- **데이터셋**: 서브태스크별 ~1,000~6,000 문항
- **V1 골든셋**: 100문항 (5 서브태스크 x 20, 층화 추출 seed=42)
- **평가 방식**: exact match (각 서브태스크별 accuracy)

### 채점 방식

1. **서브태스크별 정답률**: accuracy per subtask
2. **전체 점수**: 5개 서브태스크 **macro average** (균등 가중치)
3. **정답 추출**: BoolQ/SentiNeg → "예/아니오" 매칭, COPA/HellaSwag → "1/2" 또는 선택지 텍스트 매칭, WiC → "같다/다르다" 매칭
4. **추출 실패 시**: 오답 처리 (MMLU 동일 정책)
5. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### 실행 파라미터

```yaml
benchmark_id: S7G-011
name: KoBEST
type: classification_suite
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 16          # 짧은 응답
subtasks: [boolq, copa, wic, hellaswag, sentineg]
dataset_size_per_subtask: ~1000-6000
golden_set_size: 100     # 20 per subtask
scoring: exact_match
aggregation: subtask_macro_average
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| avg ≥ 88 | **PASS** | 목표 충족 (STEP7-G 정본) |
| 85 ≤ avg < 88 | **BORDERLINE** | CI 상한 88+ 시 조건부 PASS |
| avg < 85 | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-kobest-{run_id}",
  "benchmark": "S7G-011",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "subtask_failures": {}
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "subtasks": ["boolq", "copa", "wic", "hellaswag", "sentineg"],
    "dataset_sizes": {"boolq": 20, "copa": 20, "wic": 20, "hellaswag": 20, "sentineg": 20},
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-011",
  "lock_id": null,
  "threshold": 88,
  "actual": "{avg_score}",
  "severity": "CRITICAL",
  "route": "I-20 → QA-GATE → PRIORITY-REVIEW",
  "note": "CRITICAL 우선순위 — V1 배포 차단 대상"
}
```

---

## S7G-012: KLUE (Korean Language Understanding Evaluation)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-012 |
| **우선순위** | CRITICAL |
| **버전** | V1 |
| **목표** | 평균 ≥ 85 (STEP7-G 정본, CONFLICT_LOG C-06 참조) |
| **Phase 0 상태** | 미매핑 (§6 I-05 — Phase 1 신규 작성) |

### 입력 포맷

KLUE는 8개 서브태스크로 구성:

| 서브태스크 | 설명 | 유형 | 메트릭 |
|-----------|------|------|--------|
| TC (Topic Classification) | 뉴스 주제 분류 | 다중 분류 | macro F1 |
| STS (Semantic Textual Similarity) | 문장 유사도 | 회귀 | Pearson's r |
| NLI (Natural Language Inference) | 자연어 추론 | 3-class | accuracy |
| NER (Named Entity Recognition) | 개체명 인식 | 시퀀스 라벨링 | entity-level F1 |
| RE (Relation Extraction) | 관계 추출 | 다중 분류 | micro F1 + AUPRC |
| DP (Dependency Parsing) | 의존 구문 분석 | 구조 예측 | UAS/LAS |
| MRC (Machine Reading Comprehension) | 기계 독해 | 추출형 QA | EM/F1 |
| DST (Dialogue State Tracking) | 대화 상태 추적 | 슬롯 값 예측 | JGA (Joint Goal Accuracy) |

```
[NLI 예시]
전제: {premise}
가설: {hypothesis}
답: entailment / contradiction / neutral

[MRC 예시]
지문: {context}
질문: {question}
답: {answer_span}
```

- **데이터셋**: 서브태스크별 ~3,000~30,000 문항
- **V1 골든셋**: 80문항 (8 서브태스크 x 10, 층화 추출 seed=42)
- **평가 방식**: 서브태스크별 공식 메트릭

### 채점 방식

1. **서브태스크별 공식 메트릭** (위 표 참조):
   - TC: macro F1
   - STS: Pearson's r (0~1 스케일 변환)
   - NLI: accuracy
   - NER: entity-level F1
   - RE: micro F1
   - DP: LAS (Labeled Attachment Score)
   - MRC: EM (Exact Match) + F1 평균
   - DST: JGA
2. **전체 점수**: 8개 서브태스크 메트릭의 **macro average** (0~100 스케일 정규화)
3. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### 실행 파라미터

```yaml
benchmark_id: S7G-012
name: KLUE
type: nlu_suite
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 512         # MRC 등 긴 응답 허용
subtasks: [tc, sts, nli, ner, re, dp, mrc, dst]
golden_set_size: 80      # 10 per subtask
scoring: subtask_specific  # 각 서브태스크 공식 메트릭
aggregation: subtask_macro_average_normalized
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| avg ≥ 85 | **PASS** | 목표 충족 (STEP7-G 정본) |
| 82 ≤ avg < 85 | **BORDERLINE** | CI 상한 85+ 시 조건부 PASS |
| avg < 82 | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-klue-{run_id}",
  "benchmark": "S7G-012",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "subtask_failures": {}
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "subtasks": ["tc", "sts", "nli", "ner", "re", "dp", "mrc", "dst"],
    "dataset_sizes": {"tc": 10, "sts": 10, "nli": 10, "ner": 10, "re": 10, "dp": 10, "mrc": 10, "dst": 10},
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-012",
  "lock_id": null,
  "threshold": 85,
  "actual": "{avg_score}",
  "severity": "CRITICAL",
  "route": "I-20 → QA-GATE → PRIORITY-REVIEW",
  "note": "CRITICAL 우선순위 — V1 배포 차단 대상"
}
```

---

## S7G-013: LogicKor (한국어 논리/추론)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-013 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **LOCK** | LOCK-BE-03: ≥ 8.0/10 (GPT-4 Judge 기준) — 품질 게이트용 |
| **추가 기준** | STEP7-G 85+ (백분율 리더보드 추적용, CONFLICT_LOG C-02) |
| **Phase 0 상태** | 상세명세 §A-4 매핑 완료, 골든셋 50문항 포함 (F-04) |

### 입력 포맷

LogicKor는 50개 한국어 논리/추론 문항으로 구성.

```
질문: {question}
(카테고리: 논리추론 / 독해 / 수학 / 코딩 / 상식)

→ 모델 자유 형식 응답
```

- **데이터셋**: 50문항 (전수, 전체가 골든)
- **V1 골든셋**: 50문항 (전수)
- **평가 방식**: GPT-4 Judge + 인간 평가 (§A-4)

### 채점 방식

1. **GPT-4 Judge 평가**: 각 문항에 1~10 점수 부여
2. **루브릭** (§A-4 정본):
   - 1~3: 오답 또는 무관한 응답, 논리 비약 심각
   - 4~5: 부분 정답, 핵심 누락 또는 논리 오류 존재
   - 6~7: 대체로 정확, 사소한 누락 또는 개선 여지
   - 8~9: 정확하고 논리적, 완성도 높음
   - 10: 완벽한 응답, 추가 가치 제공
3. **가중치**: 정확성(40%) + 논리성(30%) + 완성도(30%)
4. **전체 점수**: 50문항 평균 (1~10 스케일)
5. **리더보드 점수**: 전체 점수 x 10 → 백분율 (STEP7-G 85+ 비교용)
6. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)
7. **인간 평가 병행** (LOCK-BE-05/07):
   - 최소 2명 독립 평가, Cohen's Kappa ≥ 0.6
   - 점수 차이 2점+ 시 3번째 평가자 투입

### 실행 파라미터

```yaml
benchmark_id: S7G-013
name: LogicKor
type: open_ended_judge
model: ${MODEL_ID}
judge_model: gpt-4-turbo  # LLM-as-Judge (S7G-071)
temperature: 0
seed: 42
max_tokens: 4096
dataset_size: 50
golden_set_size: 50      # 전수
scoring: llm_judge_1_to_10
rubric_weights: {accuracy: 0.40, logic: 0.30, completeness: 0.30}
aggregation: mean
human_eval: true          # LOCK-BE-05/07
human_eval_min_raters: 2
human_eval_kappa_threshold: 0.6
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정 (이중 기준 — CONFLICT_LOG C-02)

**기준 1: GPT-4 Judge 절대 평가 (품질 게이트, LOCK-BE-03)**

| 구간 | 판정 | 조건 |
|------|------|------|
| score ≥ 8.0 | **PASS** | LOCK-BE-03 충족 |
| 7.5 ≤ score < 8.0 | **BORDERLINE** | CI 상한 8.0+ 시 조건부 PASS |
| score < 7.5 | **FAIL** | LOCK-BE-03 미충족 |

**기준 2: 백분율 리더보드 (STEP7-G 추적용)**

| 구간 | 판정 |
|------|------|
| score x 10 ≥ 85 | 리더보드 목표 달성 |
| score x 10 < 85 | 리더보드 목표 미달 (게이트 차단 아님) |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-logickor-{run_id}",
  "benchmark": "S7G-013",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "judge_failures": 0
  },
  "context": {
    "model_id": "{model_version}",
    "judge_model": "gpt-4-turbo",
    "seed": 42,
    "dataset_size": 50,
    "rubric_weights": {"accuracy": 0.40, "logic": 0.30, "completeness": 0.30},
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "judge_retry_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-013",
  "lock_id": "LOCK-BE-03",
  "threshold": 8.0,
  "actual": "{judge_mean}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE → LOCK-REVIEW",
  "note": "이중 기준 — 리더보드 85+ 미달 시 추가 보고 (C-02)"
}
```

---

## S7G-014: CLIcK (Cultural and Linguistic Intelligence in Korean)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-014 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **목표** | ≥ 70% (종합계획서 Phase 1-A 정본) |
| **Phase 0 상태** | 미매핑 (§6 I-05 — Phase 1 신규 작성) |

### 입력 포맷

CLIcK은 한국 문화, 사회, 역사, 언어 지식을 평가하는 다중 선택 벤치마크.

```
질문: {question_about_korean_culture}
A. {choice_a}
B. {choice_b}
C. {choice_c}
D. {choice_d}

카테고리: 한국사 / 한국 사회 / 한국 문화 / 한국어 / 한국 지리
```

- **데이터셋**: ~1,500 문항 (5 카테고리)
- **V1 골든셋**: 50문항 (5 카테고리 x 10, 층화 추출 seed=42)
- **평가 방식**: exact match (다중 선택)

### 채점 방식

1. **정답 추출**: MMLU 동일 3단계 cascade regex
2. **카테고리별 정답률**: accuracy per category
3. **전체 점수**: 5개 카테고리 **macro average**
4. **추출 실패 시**: 오답 처리
5. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### 실행 파라미터

```yaml
benchmark_id: S7G-014
name: CLIcK
type: multiple_choice
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 16
categories: [history, society, culture, language, geography]
dataset_size: ~1500
golden_set_size: 50      # 10 per category
scoring: exact_match
aggregation: category_macro_average
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| avg ≥ 70% | **PASS** | 목표 충족 |
| 67% ≤ avg < 70% | **BORDERLINE** | CI 상한 70%+ 시 조건부 PASS |
| avg < 67% | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-click-{run_id}",
  "benchmark": "S7G-014",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "extraction_failures": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "categories": ["history", "society", "culture", "language", "geography"],
    "dataset_sizes": {"history": 10, "society": 10, "culture": 10, "language": 10, "geography": 10},
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-014",
  "lock_id": null,
  "threshold": 0.70,
  "actual": "{category_macro_avg}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE",
  "note": "LOCK 미등록 — 종합계획서 §7.3 Phase 1-A 목표값 기준"
}
```

---

## 공통 인터페이스 — Phase 0 산출물 정합성

### benchmark_runner.py (F-01) 등록 인터페이스

```python
# S7G-011~014 등록 (Phase 1-A 확장)
runner.register(
    benchmark_id="S7G-011",
    name="KoBEST",
    scorer=SubtaskSuiteScorer(
        subtasks=["boolq", "copa", "wic", "hellaswag", "sentineg"],
        scoring="exact_match"
    ),
    dataset=GoldenSet("kobest", size=100),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=88, borderline_delta=3, scale=100)
)

runner.register(
    benchmark_id="S7G-012",
    name="KLUE",
    scorer=SubtaskSuiteScorer(
        subtasks=["tc", "sts", "nli", "ner", "re", "dp", "mrc", "dst"],
        scoring="subtask_specific",
        normalize_to_100=True
    ),
    dataset=GoldenSet("klue", size=80),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=85, borderline_delta=3, scale=100)
)

runner.register(
    benchmark_id="S7G-013",
    name="LogicKor",
    scorer=LLMJudgeScorer(
        judge_model="gpt-4-turbo",
        prompt="logickor_rubric",
        scale=(1, 10),
        weights={"accuracy": 0.40, "logic": 0.30, "completeness": 0.30}
    ),
    dataset=GoldenSet("logickor", size=50),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id="LOCK-BE-03", pass_value=8.0, borderline_delta=0.5, scale=10)
)

runner.register(
    benchmark_id="S7G-014",
    name="CLIcK",
    scorer=MultipleChoiceScorer(
        regex_cascade=True,
        categories=["history", "society", "culture", "language", "geography"]
    ),
    dataset=GoldenSet("click", size=50),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=0.70, borderline_delta=0.03)
)
```

### schemas/benchmark_result.schema.json (F-02) 매핑

| F-02 필드 | S7G-011 | S7G-012 | S7G-013 | S7G-014 |
|-----------|---------|---------|---------|---------|
| benchmark_name | "KoBEST" | "KLUE" | "LogicKor" | "CLIcK" |
| model_id | ${MODEL_ID} | ${MODEL_ID} | ${MODEL_ID} | ${MODEL_ID} |
| run_date | ISO-8601 | ISO-8601 | ISO-8601 | ISO-8601 |
| score | subtask_macro_avg | subtask_macro_avg_norm | judge_mean | category_macro_avg |
| confidence_interval | {ci_low, ci_high, level, method, B} | 동일 | 동일 | 동일 |
| metadata | {seed, subtasks: 5} | {seed, subtasks: 8} | {seed, judge_model, weights} | {seed, categories: 5} |
| status | PASS/BORDERLINE/FAIL | 동일 | 동일 | 동일 |

### promptfoo.yaml assertion 매핑

| 벤치마크 | assertion type | threshold | LOCK |
|---------|---------------|-----------|------|
| S7G-011 KoBEST | exact_match (서브태스크별) | avg ≥ 88 | (목표값) |
| S7G-012 KLUE | subtask_specific | avg ≥ 85 | (목표값) |
| S7G-013 LogicKor | llm_judge (1~10) | ≥ 8.0 | LOCK-BE-03 |
| S7G-014 CLIcK | exact_match (다중선택) | ≥ 70% | (목표값) |

---

## 복구/재시도 흐름도

```
[실행 시작] → [API 호출]
  ├── 성공 → [채점] → [CI 산출] → [결과 저장]
  ├── API 타임아웃 → retry (max 3, backoff 2^n초)
  ├── Rate Limit → retry (max 5, backoff 60초)
  ├── Judge 실패 (S7G-013) → retry judge (max 2)
  │     └── Judge 2회 실패 → 해당 문항 skip + 경고, 나머지로 평균 산출
  └── 전체 실패 → [에스컬레이션 I-20]

서브태스크 부분 실패 (S7G-011/012):
  ├── 개별 서브태스크 실패 → 해당 서브태스크 제외, 나머지로 평균
  ├── 2개 이상 실패 → 전체 FAIL + 에스컬레이션
  └── 전체 성공 → 정상 집계
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 유형 | 점수 penalty | 적용 대상 |
|-----------------|-------------|----------|
| Judge 모델 대체 (GPT-4 → GPT-3.5) | -20% confidence | S7G-013 LogicKor |
| 서브태스크 일부 제외 | CI 폭 확대 + 경고 표기 | S7G-011/012 |
| 데이터셋 축소 | CI 폭 확대 (√n 비례) | 전체 |
| seed 변경 | 재현성 LOCK-BE-08 위반 경고 | 전체 |

### 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|------------|------|:-----------:|------|
| E-API-TIMEOUT | API 호출 타임아웃 | Yes | retry (max 3, backoff 2^n초) |
| E-RATE-LIMIT | API Rate Limit 초과 | Yes | retry (max 5, backoff 60초) |
| E-JUDGE-FAIL | LLM Judge 응답 실패 (S7G-013) | Yes | retry judge (max 2), 2회 실패 시 해당 문항 skip + 경고 |
| E-EXTRACT | 정답 추출 실패 (S7G-011/014) | No | 오답 처리, extraction_failures 카운트 증가 |
| E-SUBTASK | 서브태스크 전체 실패 (S7G-011/012) | No | 1개 실패: 제외 후 나머지 평균, 2개+ 실패: 전체 FAIL + 에스컬레이션 |
| E-HUMAN-EVAL | 인간 평가 불일치 (S7G-013) | Yes | 점수 차이 2점+ 시 3번째 평가자 투입 (LOCK-BE-07) |
| E-NETWORK | 네트워크 장애 | Yes | retry (max 3, backoff 5초) |

---

## Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | KoBEST 서브태스크 1개 전체 오답 시 평균 영향 | BoolQ 전체 0% 주입 | 전체 평균 하락, 해당 서브태스크 상세 보고서 생성 |
| T-02 | KLUE NER 한국어 개체명 복합 케이스 | "삼성전자 이재용 부회장" 등 복합 개체 삽입 | entity-level F1 정밀 산출, 부분 일치 처리 검증 |
| T-03 | LogicKor judge 일관성 (같은 응답 2회 평가) | 동일 응답에 대해 judge 2회 실행 | 점수 차이 ≤ 1.0점, ICC(2,1) ≥ 0.75 (test-retest 신뢰도; Cohen's κ는 단일 평가자 재현성에 부적합) |
| T-04 | CLIcK 한국사 심화 문항 (예: 조선 시대 정치제도) | 난이도 상 문항 집중 배치 | 카테고리별 정답률 분포 확인 |
| T-05 | seed=42 재현성 검증 (한국어 4건 동시) | 동일 설정 2회 연속 실행 | 4건 벤치마크 모두 바이트 수준 동일 결과 |
| T-06 | KoBEST 목표값 경계 테스트 (평균 87.9) | 시뮬레이션으로 87.9 주입 | status=FAIL, CI 상한 88+ 시 BORDERLINE |
| T-07 | KLUE STS Pearson's r 0~1 정규화 정확성 | STS raw correlation 값 주입 | 0~100 스케일 변환 후 다른 서브태스크와 호환 |
| T-08 | LogicKor 인간 평가 불일치 시 3번째 평가자 투입 | 평가자 A=9, 평가자 B=6 (차이 3점) | 3번째 평가자 자동 요청, 중앙값 채택 |
| T-09 | CLIcK 존재하지 않는 카테고리 문항 삽입 | 카테고리="과학" (기존 5개 외) | 오류 처리 + 경고 로그, 나머지 정상 집계 |
| T-10 | KLUE DST 대화 상태 추적 복합 슬롯 | 3개 슬롯 동시 변경 대화 | JGA: 3개 모두 일치해야 정답 |
| T-11 | KoBEST HellaSwag 한국어 문맥 완성 | 문화 특수 상황 (명절/예절 등) | 한국 문화 반영된 completion 선택 정확도 |
| T-12 | 4건 벤치마크 동시 실행 시 자원 경합 | benchmark_runner에서 4건 병렬 실행 | 결과 독립성 보장, 상호 간섭 없음 |

---

## 변경 이력

| 날짜 | 변경 내용 | 근거 |
|------|----------|------|
| 2026-04-12 | Phase 1-A P1-1 초기 작성: S7G-011~014 한국어 벤치마크 채점 규칙 + 실행 파라미터 정의 | §7.3 Phase 1-A 절차 2 |
| 2026-04-12 | S7G-011 KoBEST, S7G-012 KLUE, S7G-014 CLIcK 신규 추가 (§6 I-05 해소) | I-05 Phase 1 범위 |
| 2026-04-12 | S7G-013 LogicKor 정의 보완 — 이중 기준 (judge 절대 + 백분율 리더보드) 명시 | CONFLICT_LOG C-02 반영 |
| 2026-04-12 | Step 2 재검증: (1) S7G-012 KLUE/S7G-014 CLIcK 로깅+에스컬레이션 블록 추가, (2) S7G-013 LogicKor 에스컬레이션 블록 추가, (3) 예외 처리 정책 표 추가 | P1-1 Step 2 품질 심화 |
