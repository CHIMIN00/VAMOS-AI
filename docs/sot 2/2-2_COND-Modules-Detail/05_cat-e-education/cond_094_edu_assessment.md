# COND-094 교육 평가 도구 (Educational Assessment Tool)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-094
> **카테고리**: CAT-E Education
> **우선순위**: MEDIUM
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-1
> **Phase 1 대응**: 종합명세 §94
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10

---

## §0 교차 참조 블록

- **종합계획서**: §7.4 (세션 2-1) / §13.1 / §B
- **종합명세**: §#94
- **AUTHORITY_CHAIN**: §4 LOCK-CD-01~11
- **ErrorHandling**: `D2.0-02 §0.3`
- **교차 도메인**: `3-3 PKM` · `6-2 Security-Governance` (평가 무결성·표절 검사) · `6-12 Event-Logging`
- **연계 모듈**: COND-091 (learner_profile 조회) · COND-092 (모의시험 채점 재사용) · COND-093 (rubric 공유) · COND-114 (평가 결과 → 학습 분석 전달)

---

## §1 개요

### 1.1 목적
학습자의 수행을 자동 평가한다. 객관식은 정답 대조, 주관식은 LLM + 루브릭 기반 채점, 피드백 생성, 성취도 분석을 포함한다.

### 1.2 핵심 기술
- **Automated Essay Scoring (AES)**: BERT-like encoder + regression head
- **LLM-based Grading**: rubric-aware few-shot + chain-of-thought 판정 (self-consistency ≥ 3 샘플)
- **Rubric Evaluation**: 6 차원 (Content/Organization/Grammar/Style/Originality/Citation) 가중합
- **Formative Feedback**: error pattern 분류 + 개선 제안 생성

### 1.3 LOCK 준수 요약
LOCK-CD-01/03/04/05/06/10 전수 준수.

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class EvaluationRubric(BaseModel):
    rubric_id: str
    dimensions: dict[str, float] = Field(
        ..., description="dimension_name → weight (합=1.0)"
    )
    max_score: float = Field(default=100.0, gt=0)

    @field_validator("dimensions")
    @classmethod
    def weights_sum_one(cls, v):
        s = sum(v.values())
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"rubric weights must sum to 1.0, got {s}")
        return v

class Submission(BaseModel):
    submission_id: str
    learner_id: str
    question_id: str
    submission_type: Literal["multiple_choice", "short_answer", "essay"]
    answer: str = Field(..., max_length=20_000)
    submitted_at: str       # ISO-8601

class AnswerKey(BaseModel):
    question_id: str
    correct_option: int | None = None      # multiple_choice 일 때
    reference_answer: str | None = None    # short_answer / essay 일 때
    acceptable_patterns: list[str] = Field(default_factory=list)

class EduAssessmentInput(BaseModel):
    submission: Submission
    rubric: EvaluationRubric
    answer_key: AnswerKey | None = None
    feedback_language: str = Field(default="ko")
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field

class RubricScore(BaseModel):
    dimension: str
    score: float = Field(..., ge=0.0, le=1.0)
    rationale: str

class EvaluationResult(BaseModel):
    submission_id: str
    total_score: float = Field(..., ge=0.0)
    normalized_score: float = Field(..., ge=0.0, le=1.0)
    pass_fail: Literal["pass", "fail"]
    rubric_scores: list[RubricScore]
    feedback: str
    grading_method: Literal["exact_match", "pattern_match", "llm_grading", "aes_model"]

class EduAssessmentOutput(BaseModel):
    evaluation: EvaluationResult
    improvement_suggestions: list[str] = Field(default_factory=list)
    similarity_to_reference: float | None = Field(default=None, ge=0.0, le=1.0)
    plagiarism_score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    grading_cost_krw: float = Field(..., ge=0.0)
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM EduAssessment(input) -> Result<Output, VamosError>:
    # 1. Validate rubric
    IF rubric.dimensions 합 ≠ 1.0 THEN Pydantic 자동 차단

    # 2. Dispatch by submission_type
    IF type IN ("multiple_choice", "short_answer", "essay") AND answer_key IS None:
        RETURN Err(COND_094_ANSWER_KEY_MISSING)
    IF type == "multiple_choice":
        result = grade_mc(submission.answer, answer_key.correct_option)
        method = "exact_match"
    ELIF type == "short_answer":
        IF answer_key.acceptable_patterns:
            result = grade_pattern(submission.answer, patterns)
            method = "pattern_match"
        ELSE:
            result = grade_llm_short(submission.answer, answer_key.reference_answer, rubric)
            method = "llm_grading"
    ELIF type == "essay":
        result = grade_essay(submission.answer, rubric, answer_key)
        method = "llm_grading" if use_llm else "aes_model"

    # 3. Plagiarism / similarity (essay + short_answer)
    IF answer_key.reference_answer:
        similarity = cosine_sim(embed(answer), embed(reference))
        plagiarism = similarity_to_corpus(answer, cohort_corpus)

    # 4. Rubric aggregate
    total = sum(dim.score * rubric.dimensions[dim.name] for dim in rubric_scores) * rubric.max_score
    normalized = total / rubric.max_score

    # 5. Feedback generation (rubric 약점 영역 기반)
    weak_dims = [d for d in rubric_scores if d.score < 0.6]
    feedback = generate_feedback(weak_dims, lang=feedback_language)
    suggestions = derive_improvement_suggestions(weak_dims)

    # 6. Confidence (LLM grading 일 때 self-consistency 기반)
    IF method == "llm_grading":
        samples = 3
        confidence = 1 - stdev([sample_scores]) / max_score
    ELSE:
        confidence = 1.0      # exact/pattern 은 결정적

    RETURN Ok(EduAssessmentOutput(...))
```

### 4.2 AES 모델 (essay)
```
score = BERTScore(answer, reference) * 0.3 +
        LLM_rubric_score(answer, rubric) * 0.5 +
        feature_score(length, vocab_diversity, readability) * 0.2
```

### 4.3 Self-Consistency (LLM grading)
```
samples = [llm_grade(answer, rubric) for _ in range(3)]
final_score = median(samples)
confidence = 1 - (max(samples) - min(samples)) / rubric.max_score
```

### 4.4 시간 복잡도
- exact_match: `O(1)`
- pattern_match: `O(|patterns|)`
- LLM grading: `O(T)` (token-bound)
- AES: `O(T + d · d)` (BERT pool + regression)

---

## §5 Error Handling — §13.1 #4

### 5.1 FailureCode
```
COND_094_RUBRIC_WEIGHTS_INVALID   # Pydantic 차단되지만 방어
COND_094_ANSWER_KEY_MISSING       # mc 인데 correct_option 없음
COND_094_LLM_GRADING_TIMEOUT
COND_094_LLM_INCONSISTENT         # self-consistency 분산 초과
COND_094_SUBMISSION_TOO_LONG      # 20k 초과 (Pydantic 차단 확장)
COND_094_PLAGIARISM_DETECTED      # threshold 초과 시 플래그
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation): Pydantic 차단
Phase 2 (Dispatch): answer_key 누락 → LLM-only fallback (confidence × 0.6)
Phase 3 (Grading): LLM timeout → AES 모델 fallback (confidence × 0.7)
Phase 3 (LLM inconsistent): 5 샘플로 재추정 → 여전히 분산 크면 에스컬레이션
Phase 4 (Escalation): 표절 의심 → I-20 + 인간 리뷰 큐
```

### 5.3 에스컬레이션 Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-094"
    error_code: str
    original_request: EduAssessmentInput
    partial_result: EduAssessmentOutput | None
    retry_count: int
    timestamp: datetime
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-...",
  "error": {"code": "COND_094_LLM_INCONSISTENT", "severity": "WARN"},
  "context": {"submission_id": "S-...", "rubric_id": "R-...", "variance": 0.22},
  "recovery": {"strategy": "AES_fallback", "confidence_penalty": 0.7}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-E)
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-091 | CONSUMES | learner_profile 조회 (개인 맞춤 피드백) |
| COND-092 | PRODUCES | 모의시험 채점 결과 공급 |
| COND-093 | SHARES | rubric 템플릿 공유 |
| COND-114 | NOTIFIES | 평가 결과 이벤트 전달 |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| CAT-A ML (AES/BERT/LLM) | CONSUMES | 주관식 채점 모델 |
| CAT-B Knowledge Graph | CONSUMES | question_id → topic 매핑 |
| `6-2 Security-Governance` | CROSS-DOMAIN | 표절 검사 · 평가 무결성 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_094_* prefix |
| `3-3 PKM` | CROSS-DOMAIN | 평가 결과 저장 (Memory Store) |

### 6.3 의존성 매트릭스 (요약)
```
            091  092  093  094  113  114  115
COND-094  [  C    P    S    -    .    N    .  ]
```

---

## §7 Performance Benchmark — §13.1 #6

| 지표 | V2 목표 | 측정 |
|---|---|---|
| p50 (객관식) | ≤ 5 ms | exact_match |
| p50 (주관식/에세이) | ≤ 3.5 s | LLM + AES |
| p99 | ≤ 12 s | LLM cold + self-consistency |
| 처리량 | ≥ 50 req/s (혼합) | 단일 인스턴스 |
| LLM 비용/req | ≤ ₩0.8 | per essay |
| 표절 검사 지연 | ≤ 400 ms | 코퍼스 10k |

### 7.1 벤치마크 시나리오
```
BENCH-094-01: mc 100k req → p50/throughput
BENCH-094-02: essay 500 req → AES vs LLM 품질 비교 (QWK)
BENCH-094-03: plagiarism 코퍼스 sweep → recall/precision
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3)

### 8.1 I-05-COND094-01: 객관식 정답 채점
- 주입: `submission_type="multiple_choice", answer="2", answer_key.correct_option=2`
- 기대: `pass_fail="pass"`, `normalized_score==1.0`, `grading_method="exact_match"`, `confidence==1.0`

### 8.2 I-05-COND094-02: 에세이 LLM 채점 + 피드백
- 주입: 400단어 에세이 + 6 차원 rubric
- 기대: `rubric_scores.length==6`, `feedback.length > 0`, `grading_method in ["llm_grading","aes_model"]`, `confidence >= 0.7`

### 8.3 I-05-COND094-03: LLM 분산 초과 → AES fallback
- 주입: LLM stub 이 3 샘플에서 점수 분산 0.3 초과 반환
- 기대: `confidence <= 0.7 * max`, header `X-COND094-Fallback: AES`

### 8.4 I-05-COND094-04: 표절 탐지
- 주입: 참조 답안과 cosine_sim 0.95 인 제출
- 기대: `plagiarism_score >= 0.9`, 에스컬레이션 이벤트 발행

### 8.5 Phase 3 확장 (≥ 10)
| ID | 주입 | 기대 |
|---|---|---|
| 094-S5 | answer_key 누락 (mc) | `ANSWER_KEY_MISSING` |
| 094-S6 | 20k 초과 제출 | `SUBMISSION_TOO_LONG` |
| 094-S7 | rubric weights 0.99 | Pydantic 차단 |
| 094-S8 | concurrent 100 | p99 ≤ 12s |
| 094-S9 | LLM 전면 장애 | AES 단독 동작 |
| 094-S10 | 다국어 피드백 (ja) | 피드백 ja 생성 |
| 094-S11 | trace 전파 | 로그 일치 |

---

## §9 Blue Node Integration (LOCK-CD-04/08)

- Node: Learning Node (P1)
- LOCK-CD-08 준수
- ModuleConfig (LOCK-CD-10): `priority=2, max_concurrent=16, timeout_ms=15_000, retry_policy={max_retries=2, backoff="exp"}`

### 9.1 Runnable
```python
class EduAssessmentTool(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: EduAssessmentInput) -> Result[EduAssessmentOutput, VamosError]: ...
    def run(self, input: EduAssessmentInput) -> Result[EduAssessmentOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def shutdown(self) -> None: ...
```

### 9.2 이벤트 (6-12)
```
COND_094_GRADED             INFO   submission_id, score
COND_094_LLM_INCONSISTENT   WARN   variance
COND_094_PLAGIARISM         ERROR  plagiarism_score
COND_094_ESCALATED          ERROR  failure_code
```

---

## §10 V2-Phase 2 변경 이력

| 버전 | 일자 | 변경 | 근거 |
|---|---|---|---|
| V1 | 2026-03-22 | SHELL L1 | Phase 1 |
| V2 | 2026-04-19 | L3 상세 8 항목 | STAGE 7 Phase 7-II 2-2 STEP_B 세션 2-1 |

### 10.1 Pydantic 재사용 출처
- `ModuleConfig` ← `common_types.md §3.4`
- `VamosError` / `Result[T,E]` ← `D2.0-02 §0.3`

---

**[END OF COND-094 V2]** — L3 8 항목 전수. LOCK-CD-01/03/04/05/06/10. I-05 11 시나리오. CAT-E 4 연계 + 6-2 표절 검사 · 6-12 이벤트.
