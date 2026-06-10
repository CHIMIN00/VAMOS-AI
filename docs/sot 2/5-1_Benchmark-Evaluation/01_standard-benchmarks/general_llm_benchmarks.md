# General LLM Benchmarks — 표준 벤치마크 채점 규칙 및 실행 파라미터

> **Phase**: 1-A (P1-1)
> **범위**: S7G-001 (MMLU), S7G-002 (HumanEval), S7G-003 (MT-Bench), S7G-004 (IFEval)
> **작성일**: 2026-04-12
> **상태**: V1 정의 완료

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|-----------|----------|
| STEP7-G S7G-001~004 | Part 1 표준 LLM 벤치마크 목표값/평가 방식/우선순위 |
| BENCHMARK_EVALUATION_상세명세.md §A-1 | MMLU 채점: 5-shot exact match, bootstrap 95% CI |
| BENCHMARK_EVALUATION_상세명세.md §A-2 | HumanEval 채점: Docker 샌드박스, 10초/문제 |
| AUTHORITY_CHAIN.md LOCK-BE-01 | MMLU ≥ 85% (macro average) |
| AUTHORITY_CHAIN.md LOCK-BE-02 | HumanEval pass@1 ≥ 85% |
| AUTHORITY_CHAIN.md LOCK-BE-03 | LogicKor ≥ 8.0/10 (참조: MT-Bench 채점 동일 LLM-as-Judge 계열) |
| AUTHORITY_CHAIN.md LOCK-BE-06 | Bootstrap 95% CI 필수 (B=10000 for n<100, B=5000 for n>1000) |
| AUTHORITY_CHAIN.md LOCK-BE-08 | seed=42, 모델 버전/시스템 프롬프트 해시/실행 환경 기록 |
| PHASE_B5 §6.1 | 도구 스택 (pytest ≥ 8.0) |
| PHASE_B5 §6.4 | CI/CD Pipeline 연동 구조 |
| Phase 0 F-01 | benchmark_runner.py — 러너 프레임워크 |
| Phase 0 F-02 | schemas/benchmark_result.schema.json — 결과 스키마 (필수 6필드) |
| Phase 0 F-05 | promptfoo.yaml — 기존 MMLU+HumanEval 2건 설정 |
| CONFLICT_LOG C-01 | HumanEval pass@1: STEP7-G 85% 우선 (상세명세 80%는 MBPP 최소 기준) |

---

## S7G-001: MMLU (Massive Multitask Language Understanding)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-001 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **LOCK** | LOCK-BE-01: ≥ 85% (macro average) |
| **Phase 0 상태** | 정의 완료 + 시뮬레이션 실행 완료 (F-05) |

### 입력 포맷

```
Question: {question}
A. {choice_a}
B. {choice_b}
C. {choice_c}
D. {choice_d}

Few-shot examples (5개):
Subject: {subject}
Example 1: Q → A(정답)
...
Example 5: Q → A(정답)

Answer:
```

- **n-shot**: 5-shot (§A-1 정본)
- **데이터셋**: 14,042 문항 (57개 과목), V1 골든셋 50문항 (층화 추출 seed=42)
- **한국어**: KMMLU 병행 평가, 한국 법/역사/문화 과목 추가 (2,000 문항)

### 채점 방식

1. **정답 추출**: 3단계 cascade regex
   - Stage 1: `^\s*\(?([A-D])\)?[\.\):]?\s*$` (단독 문자)
   - Stage 2: `(?:answer|정답)\s*(?:is|:)\s*\(?([A-D])\)?` (answer is X 패턴)
   - Stage 3: `\(([A-D])\)` (괄호 안 문자)
   - 추출 실패 시: **오답 처리** (penalty for ambiguity, §A-1)
2. **과목별 정답률**: accuracy per subject
3. **전체 점수**: macro average (과목별 균등 가중치 1/57)
4. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06)
   - n < 100: B=10,000 resample
   - n > 1,000: B=5,000 resample

### 실행 파라미터

```yaml
benchmark_id: S7G-001
name: MMLU
type: multiple_choice
model: ${MODEL_ID}  # S7F-070 정본
temperature: 0       # R-18-1
seed: 42             # LOCK-BE-08
max_tokens: 16       # 단일 문자 응답
n_shot: 5
dataset_size: 14042
golden_set_size: 50
scoring: exact_match
aggregation: macro_average
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000  # n=50 < 100 → B=10000
timeout_seconds: 30     # per question
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| score ≥ 85% | **PASS** | LOCK-BE-01 충족 |
| 82% ≤ score < 85% | **BORDERLINE** | CI 상한이 85% 이상이면 조건부 PASS |
| score < 82% | **FAIL** | LOCK-BE-01 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-mmlu-{run_id}",
  "benchmark": "S7G-001",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "extraction_failures": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "n_shot": 5,
    "dataset_size": 50,
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false,
    "extraction_cascade_stage": 1
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-001",
  "lock_id": "LOCK-BE-01",
  "threshold": 0.85,
  "actual": "{score}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE → LOCK-REVIEW"
}
```

---

## S7G-002: HumanEval (코드 생성)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-002 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **LOCK** | LOCK-BE-02: pass@1 ≥ 85% |
| **Phase 0 상태** | 정의 완료 + 시뮬레이션 실행 완료 (F-05) |

### 입력 포맷

```python
# Function signature + docstring provided
def {function_name}({params}) -> {return_type}:
    """
    {docstring with examples}
    """
    # Model generates function body
```

- **데이터셋**: 164문항 (전체), V1 골든셋 20문항 (난이도 분포)
- **실행 환경**: Docker 샌드박스, Python 3.11, 타임아웃 10초/문제 (§A-2)
  - (참고: 운영 환경 타임아웃은 LOCK-VR-15 30초 — CONFLICT_LOG C-09 RESOLVED)

### 채점 방식

1. **코드 추출**: ` ```python ` 블록 또는 함수 본문 자동 추출
2. **실행**: Docker 샌드박스에서 단위 테스트 실행
3. **판정**: pass (모든 테스트 통과) / fail (하나라도 실패)
4. **부분 점수 없음** (binary)
5. **pass@k 계산**: `1 - C(n-c, k) / C(n, k)` (n=시도횟수, c=통과횟수)
6. **메트릭**: pass@1 (V1 기본), pass@5, pass@10 (참조용)
7. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### 실행 파라미터

```yaml
benchmark_id: S7G-002
name: HumanEval
type: code_generation
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 2048       # 함수 본문 생성
dataset_size: 164
golden_set_size: 20
scoring: pass_at_k
k_values: [1, 5, 10]
primary_metric: pass_at_1
execution_env: docker
docker_image: python:3.11-slim
timeout_seconds: 10    # per problem (§A-2)
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| pass@1 ≥ 85% | **PASS** | LOCK-BE-02 충족 |
| 82% ≤ pass@1 < 85% | **BORDERLINE** | CI 상한이 85% 이상이면 조건부 PASS |
| pass@1 < 82% | **FAIL** | LOCK-BE-02 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-humaneval-{run_id}",
  "benchmark": "S7G-002",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "timeout_count": 0,
    "syntax_error_count": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "dataset_size": 20,
    "docker_image": "python:3.11-slim",
    "timeout_seconds": 10,
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "docker_restart_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-002",
  "lock_id": "LOCK-BE-02",
  "threshold": 0.85,
  "actual": "{pass_at_1}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE → LOCK-REVIEW"
}
```

---

## S7G-003: MT-Bench (다중 턴 벤치마크)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-003 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **목표** | ≥ 8.0/10 (종합계획서 Phase 1-A 정본) |
| **Phase 0 상태** | 미매핑 (§6 I-01 — Phase 1 신규 작성) |
| **의존** | Phase 1-C S7G-071 LLM-as-Judge 파이프라인 |

### 입력 포맷

MT-Bench는 80개 다중 턴(2턴) 질문으로 구성. 8개 카테고리 x 10문항.

```
[Turn 1]
System: You are a helpful assistant.
User: {question_turn1}
→ Model response

[Turn 2]
System: You are a helpful assistant.
User: {question_turn1}
Assistant: {model_response_turn1}
User: {question_turn2}  (follow-up)
→ Model response
```

- **데이터셋**: 80문항 (8 카테고리 x 10: Writing, Roleplay, Extraction, Reasoning, Math, Coding, Knowledge, Common Sense)
- **V1 골든셋**: 80문항 전수 (소규모이므로 전수 포함)
- **평가 방식**: LLM-as-Judge (GPT-4 등급 모델 심판)

### 채점 방식

1. **LLM Judge 평가**: 각 턴별로 judge 모델이 1~10 점수 부여
2. **턴별 평가**: Turn 1 점수 + Turn 2 점수 → 문항별 평균
3. **카테고리별 평균**: 8개 카테고리 각각의 평균 점수
4. **전체 점수**: 8개 카테고리 평균의 macro average
5. **Judge 프롬프트**: fastchat 표준 judge 프롬프트 사용
6. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### Judge 루브릭 (1~10)

| 점수 | 기준 |
|------|------|
| 1~3 | 무관하거나 부정확한 응답, 지시 무시 |
| 4~5 | 부분적으로 관련되나 핵심 누락/오류 |
| 6~7 | 대체로 정확하고 유용, 사소한 개선 여지 |
| 8~9 | 정확하고 완전하며 논리적, 높은 품질 |
| 10 | 예시 수준의 완벽한 응답, 추가 가치 제공 |

### 실행 파라미터

```yaml
benchmark_id: S7G-003
name: MT-Bench
type: multi_turn_judge
model: ${MODEL_ID}
judge_model: gpt-4-turbo  # LLM-as-Judge (S7G-071)
temperature: 0
seed: 42
max_tokens: 4096        # 다중 턴 응답
n_turns: 2
categories: [writing, roleplay, extraction, reasoning, math, coding, knowledge, common_sense]
dataset_size: 80
golden_set_size: 80     # 전수
scoring: llm_judge_1_to_10
aggregation: category_macro_average
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
judge_prompt: fastchat_standard
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| score ≥ 8.5 | **PASS** | 목표 충족 (_index.md, CONFLICT_LOG C-10 RESOLVED) |
| 7.5 ≤ score < 8.0 | **BORDERLINE** | CI 상한이 8.0 이상이면 조건부 PASS |
| score < 7.5 | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-mt-bench-{run_id}",
  "benchmark": "S7G-003",
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
    "n_turns": 2,
    "categories": 8,
    "dataset_size": 80,
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
  "benchmark_id": "S7G-003",
  "lock_id": null,
  "threshold": 8.0,
  "actual": "{score}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE",
  "note": "LOCK 미등록 — 종합계획서 §7.3 Phase 1-A 목표값 기준"
}
```

---

## S7G-004: IFEval (Instruction Following Evaluation)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-004 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **목표** | ≥ 80% strict accuracy (종합계획서 Phase 1-A 정본) |
| **Phase 0 상태** | 미매핑 (§6 I-02 — Phase 1 신규 작성) |

### 입력 포맷

IFEval은 541개 검증 가능한 지시 사항(instruction)으로 구성. 각 프롬프트에 1~3개의 구속 조건 포함.

```
Prompt: {instruction_with_constraints}

Constraints (검증 가능):
- format: {format_constraint}     (예: "Write in bullet points")
- length: {length_constraint}     (예: "Use exactly 3 paragraphs")
- keyword: {keyword_constraint}   (예: "Include the word 'however'")
- language: {language_constraint}  (예: "Respond in Korean")
```

- **데이터셋**: 541개 프롬프트, ~1300개 개별 instruction
- **V1 골든셋**: 100문항 (지시 유형 분포 유지 층화 추출 seed=42)
- **평가 방식**: 프로그래매틱 검증 (regex/rule-based)

### 채점 방식

1. **Strict Accuracy**: 모든 instruction이 충족된 프롬프트 비율
   - 프롬프트 내 instruction 중 하나라도 실패 → 해당 프롬프트 FAIL
2. **Loose Accuracy**: 개별 instruction 충족률
   - 각 instruction 독립 평가
3. **Instruction 유형별 분석**:
   - Format constraints (bullet, numbered list, etc.)
   - Length constraints (word count, paragraph count, sentence count)
   - Keyword constraints (inclusion/exclusion)
   - Language constraints
4. **메트릭**: Strict Accuracy (primary), Loose Accuracy (secondary)
5. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000 — 골든셋 n=100, LOCK-BE-06 경계값이므로 보수적 B=10000 적용)

### 실행 파라미터

```yaml
benchmark_id: S7G-004
name: IFEval
type: instruction_following
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 4096        # 다양한 출력 길이 허용
dataset_size: 541
golden_set_size: 100
scoring: programmatic_verification
primary_metric: strict_accuracy
secondary_metric: loose_accuracy
verification_method: rule_based   # regex + counting + keyword check
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000   # LOCK-BE-06: 골든셋 n=100 (경계값), 보수적 B=10000 적용
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| strict ≥ 85% | **PASS** | 목표 충족 (_index.md, CONFLICT_LOG C-11 RESOLVED) |
| 77% ≤ strict < 80% | **BORDERLINE** | CI 상한이 80% 이상이면 조건부 PASS |
| strict < 77% | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-ifeval-{run_id}",
  "benchmark": "S7G-004",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "verification_failures": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "dataset_size": 100,
    "verification_method": "rule_based",
    "constraint_types": ["format", "length", "keyword", "language"],
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
  "benchmark_id": "S7G-004",
  "lock_id": null,
  "threshold": 0.80,
  "actual": "{strict_accuracy}",
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
# S7G-001~004 등록 (Phase 1-A 확장)
runner.register(
    benchmark_id="S7G-001",
    name="MMLU",
    scorer=MMLUScorer(n_shot=5, regex_cascade=True),
    dataset=GoldenSet("mmlu", size=50),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id="LOCK-BE-01", pass_value=0.85, borderline_delta=0.03)
)

runner.register(
    benchmark_id="S7G-002",
    name="HumanEval",
    scorer=CodeExecScorer(docker_image="python:3.11-slim", timeout=10),
    dataset=GoldenSet("humaneval", size=20),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id="LOCK-BE-02", pass_value=0.85, borderline_delta=0.03)
)

runner.register(
    benchmark_id="S7G-003",
    name="MT-Bench",
    scorer=LLMJudgeScorer(judge_model="gpt-4-turbo", prompt="fastchat_standard", scale=(1,10)),
    dataset=GoldenSet("mt_bench", size=80),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=8.0, borderline_delta=0.5)
)

runner.register(
    benchmark_id="S7G-004",
    name="IFEval",
    scorer=InstructionFollowingScorer(verification="rule_based", mode="strict"),
    dataset=GoldenSet("ifeval", size=100),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=0.80, borderline_delta=0.03)
)
```

### schemas/benchmark_result.schema.json (F-02) 매핑

Phase 0 F-02 스키마 필수 6필드 + CI 서브필드 매핑:

| F-02 필드 | S7G-001 | S7G-002 | S7G-003 | S7G-004 |
|-----------|---------|---------|---------|---------|
| benchmark_name | "MMLU" | "HumanEval" | "MT-Bench" | "IFEval" |
| model_id | ${MODEL_ID} | ${MODEL_ID} | ${MODEL_ID} | ${MODEL_ID} |
| run_date | ISO-8601 | ISO-8601 | ISO-8601 | ISO-8601 |
| score | macro_average | pass_at_1 | judge_mean | strict_accuracy |
| confidence_interval | {ci_low, ci_high, level, method, B} | 동일 | 동일 | 동일 |
| metadata | {seed, n_shot, temperature, golden_set_used} | {seed, docker_image, timeout} | {seed, judge_model, n_turns} | {seed, verification_method} |
| status | PASS/BORDERLINE/FAIL | 동일 | 동일 | 동일 |

### promptfoo.yaml assertion 매핑 (F-05 확장)

| 벤치마크 | assertion type | threshold | LOCK |
|---------|---------------|-----------|------|
| S7G-001 MMLU | exact_match (regex cascade) | ≥ 0.85 | LOCK-BE-01 |
| S7G-002 HumanEval | python_exec (pass@1) | ≥ 0.85 | LOCK-BE-02 |
| S7G-003 MT-Bench | llm_judge (1~10) | ≥ 8.0 | (목표값, LOCK 미등록) |
| S7G-004 IFEval | rule_based (strict) | ≥ 0.80 | (목표값, LOCK 미등록) |

---

## 복구/재시도 흐름도

### Phase별 복구 흐름

```
[실행 시작] → [API 호출]
  ├── 성공 → [채점] → [CI 산출] → [결과 저장]
  ├── API 타임아웃 → retry (max 3, backoff 2^n초)
  ├── Rate Limit → retry (max 5, backoff 60초)
  ├── 코드 실행 실패 (S7G-002) → FAIL 판정 (no retry)
  ├── Judge 실패 (S7G-003) → retry judge (max 2)
  └── 전체 실패 → [에스컬레이션 I-20]

Phase 1: 개별 벤치마크 독립 복구
Phase 2: 벤치마크 간 의존성 고려 (MT-Bench → LLM-as-Judge 선행)
Phase 3: 회귀 테스트 자동 복구 (3% 하락 시 LOCK-BE-14 알림)
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 유형 | 점수 penalty | 적용 대상 |
|-----------------|-------------|----------|
| API fallback (GPT-4 → GPT-3.5) | -15% confidence | S7G-003 MT-Bench judge |
| 데이터셋 축소 (전수 → 서브셋) | CI 폭 확대 (√n 비례) | 전체 |
| 타임아웃 연장 (10s → 30s) | 표기만 (성능 비교 불가) | S7G-002 HumanEval |
| seed 변경 | 재현성 LOCK-BE-08 위반 경고 | 전체 |

### 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|------------|------|:-----------:|------|
| E-API-TIMEOUT | API 호출 타임아웃 | Yes | retry (max 3, backoff 2^n초) |
| E-RATE-LIMIT | API Rate Limit 초과 | Yes | retry (max 5, backoff 60초) |
| E-JUDGE-FAIL | LLM Judge 응답 실패 (S7G-003) | Yes | retry judge (max 2), 2회 실패 시 해당 문항 skip + 경고 |
| E-CODE-EXEC | 코드 실행 실패 (S7G-002) | No | FAIL 판정, 다음 문항 진행 |
| E-EXTRACT | 정답 추출 실패 (S7G-001, S7G-004) | No | 오답 처리, extraction_failures 카운트 증가 |
| E-DOCKER | Docker 컨테이너 장애 (S7G-002) | Yes | 컨테이너 재생성 후 retry (max 2) |
| E-VERIFY | IFEval constraint 검증 실패 (S7G-004) | No | 해당 constraint FAIL 판정, 로그 기록 |
| E-NETWORK | 네트워크 장애 | Yes | retry (max 3, backoff 5초) |

---

## Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | MMLU 전수(14,042문항) 실행 시 macro average 산출 정확성 | 전체 데이터셋 투입 | 과목별 accuracy → macro avg 일치, CI 범위 합리적 |
| T-02 | HumanEval Docker 격리 위반 시도 | 악성 코드 (os.system, import subprocess) 포함 문항 삽입 | 샌드박스 차단, 해당 문항 FAIL, 시스템 무결성 유지 |
| T-03 | MT-Bench judge 일관성 (같은 응답 2회 평가) | 동일 응답에 대해 judge 2회 실행 | 점수 차이 ≤ 0.5점, 비일관 시 경고 로그 |
| T-04 | IFEval 복합 constraint 충족 여부 | 3개 constraint 동시 부여 (format + length + keyword) | strict: 3개 모두 충족만 PASS, loose: 개별 카운트 |
| T-05 | seed=42 재현성 검증 | 동일 설정 2회 연속 실행 | 바이트 수준 동일 결과 (LOCK-BE-08) |
| T-06 | LOCK 임계값 경계 테스트 (MMLU 84.9%) | 시뮬레이션으로 84.9% 점수 주입 | status=FAIL, CI 상한 85%+ 시 BORDERLINE |
| T-07 | promptfoo assertion 연동 검증 | promptfoo eval 실행 후 결과 파싱 | 4건 벤치마크 assertion 결과 + F-02 스키마 변환 성공 |
| T-08 | bootstrap CI 수렴 검증 | B=100 vs B=10000 비교 | B=10000 CI 폭이 더 좁고 안정적 |
| T-09 | MMLU regex cascade 단계별 추출 실패 처리 | "The answer might be A or B" 형태 모호 응답 삽입 | Stage 1~3 순차 시도 후 실패 → 오답 처리, 로그 기록 |
| T-10 | HumanEval 타임아웃 10초 초과 코드 | 무한 루프 또는 time.sleep(15) 포함 코드 생성 유도 | 10초 후 강제 종료, FAIL 판정, 다른 문항에 영향 없음 |
| T-11 | MT-Bench Turn 2 의존성 검증 | Turn 1 응답이 부정확한 경우 Turn 2 평가 | Turn 2 평가 시 Turn 1 맥락 반영, judge가 독립 평가 |
| T-12 | IFEval 한국어 language constraint | "한국어로 응답하세요" constraint 포함 프롬프트 | 한국어 응답 여부 자동 검증 (language detection) |

---

## 변경 이력

| 날짜 | 변경 내용 | 근거 |
|------|----------|------|
| 2026-04-12 | Phase 1-A P1-1 초기 작성: S7G-001~004 채점 규칙 + 실행 파라미터 정의 | §7.3 Phase 1-A 절차 1~2 |
| 2026-04-12 | S7G-003 MT-Bench, S7G-004 IFEval 신규 추가 (§6 I-01, I-02 해소) | I-01, I-02 Phase 1 범위 |
| 2026-04-12 | Step 2 재검증: (1) IFEval CI B=5000→B=10000 수정 (LOCK-BE-06 n=541은 100~1000 구간), (2) S7G-002/003/004 로깅+에스컬레이션 블록 추가, (3) 예외 처리 정책 표 추가 | P1-1 Step 2 품질 심화 |

---

## Phase 4 §확장 (V3-Phase 4 production-ready, RECOVERY genuine write 2026-06-03)

> **Status**: **APPROVED** | **scope**: P4-6 그룹 1 (일반 LLM). V1/V2 본문(상기) byte 무변경 prefix EXACT, 본 §은 append-only V3 확장.

### S7G-009 WildBench — 실제 사용 시나리오 벤치마크
- **내용**: 실제 사용자 질문 기반 현실적 벤치마크 (학술 ↔ 실사용 갭 측정).
- **VAMOS 활용**: 분기별 실행. 학술 점수 ↔ 실사용 점수 갭 ≤ 10%p 모니터링.
- **measurement (1차 baseline)**: WildBench score 통산 추적 시작, Bootstrap 95% CI (LOCK-BE-06).

### S7G-010 LiveBench — 지속 갱신 벤치마크
- **내용**: 데이터 오염 방지 위해 매월 새 문제로 갱신 (진짜 실력 측정).
- **VAMOS 활용**: R-T5-2 월 1회 갱신 자동화 메커니즘 연동.
- **measurement (1차 baseline)**: 월별 LiveBench 추세 추적 시작, seed=42 (LOCK-BE-08) + R-18-1 재현성 5요건.

- **LOCK 재정의 0**: LOCK-BE-06 (95% CI) + LOCK-BE-08 (seed=42) verbatim. S7G-009/010 = DONE. 측정 위임: `../05_test-items/measurement_delegation_router.md` (P4-1).
