# COND-093 교육 컨텐츠 생성 (Educational Content Generation)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-093
> **카테고리**: CAT-E Education
> **우선순위**: HIGH
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-1
> **Phase 1 대응**: 종합명세 §93
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10

---

## §0 교차 참조 블록

- **종합계획서**: §7.4 (세션 2-1) / §13.1 / §B Blue Node 매핑
- **종합명세**: §#93
- **AUTHORITY_CHAIN**: §4 LOCK-CD-01~11
- **ErrorHandling 정본**: `D2.0-02 §0.3`
- **교차 도메인**: `3-3 PKM` · `6-2 Security-Governance` (생성 컨텐츠 유해성 차단) · `6-12 Event-Logging`
- **연계 모듈**: COND-091 (경로의 content_refs 공급) · COND-092 (모의시험 item 공급) · COND-113 (튜토리얼 컨텐츠 공급) · COND-115 (언어 학습 자료)

---

## §1 개요

### 1.1 목적
주제 · 난이도 · 언어 · 컨텐츠 유형에 맞춰 교육 자료(강의 노트, 퀴즈, 플래시카드, 요약)를 자동 생성한다. Bloom 분류 정합 + distractor 품질 + 다국어 지원.

### 1.2 핵심 기술
- **LLM-based Content Generation**: 모델 체인 `generator → critic → refiner` (3-stage)
- **Bloom's Taxonomy Alignment**: `remember → understand → apply → analyze → evaluate → create`
- **Question Generation (QG)**: Stem + Answer + Distractor 3-part 생성
- **Distractor Generation**: 의미적 유사도 임계값 `[0.3, 0.7]`
- **Quality Score**: factual accuracy + bloom alignment + distractor quality 가중 평균

### 1.3 LOCK 준수 요약
| LOCK | 준수 |
|---|---|
| LOCK-CD-01 | COND-093 (CAT-E) |
| LOCK-CD-03 | BaseModule ABC 4 메서드 |
| LOCK-CD-04 | Runnable |
| LOCK-CD-05 | Result<T, VamosError> |
| LOCK-CD-06 | VamosError 4 필드 |
| LOCK-CD-10 | ModuleConfig 5 필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

ContentType = Literal["lecture_note", "quiz", "flashcard", "summary"]
BloomLevel = Literal["remember", "understand", "apply", "analyze", "evaluate", "create"]

class EduContentGenInput(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    content_type: ContentType
    difficulty: int = Field(..., ge=1, le=5, description="1=입문, 5=전문")
    language: str = Field(..., min_length=2, max_length=10, description="BCP-47 (ko, en-US, ja)")
    target_bloom_level: BloomLevel = Field(default="understand")
    target_length_tokens: int = Field(default=500, ge=50, le=5000)
    context_refs: list[str] = Field(default_factory=list, description="참조 KG node_id")
    safety_level: Literal["educational", "family_friendly", "strict"] = Field(default="family_friendly")

    @field_validator("language")
    @classmethod
    def bcp47_basic(cls, v: str) -> str:
        # 기본 BCP-47 검증 (lang[-REGION])
        parts = v.split("-")
        if not parts[0].isalpha() or not 2 <= len(parts[0]) <= 3:
            raise ValueError(f"invalid language tag: {v}")
        return v
```

### 2.1 예시
```json
{
  "topic": "Gradient descent convergence",
  "content_type": "quiz",
  "difficulty": 3,
  "language": "en-US",
  "target_bloom_level": "apply",
  "target_length_tokens": 400,
  "context_refs": ["KG-optim-gd", "KG-calc-partial"],
  "safety_level": "educational"
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal

class QuizItem(BaseModel):
    question_id: str
    stem: str
    options: list[str] = Field(..., min_length=2, max_length=6)
    correct_index: int = Field(..., ge=0)
    distractor_quality: float = Field(..., ge=0.0, le=1.0)
    bloom_level: BloomLevel
    irt_b_estimate: float = Field(..., ge=-3.0, le=3.0)

class Flashcard(BaseModel):
    card_id: str
    front: str
    back: str
    hint: str | None = None

class EducationalContent(BaseModel):
    content_id: str
    content_type: ContentType
    language: str
    body_markdown: str = Field(..., min_length=1)
    quiz_items: list[QuizItem] = Field(default_factory=list)
    flashcards: list[Flashcard] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)

class EduContentGenOutput(BaseModel):
    content: EducationalContent
    quality_score: float = Field(..., ge=0.0, le=1.0)
    bloom_level: BloomLevel
    tokens_used: int = Field(..., gt=0)
    generation_cost_krw: float = Field(..., ge=0.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름 (3-stage chain)
```
ALGORITHM EduContentGen(input) -> Result<Output, VamosError>:
    # 1. Safety pre-check (6-2 Security-Governance 체크리스트)
    safety = content_safety_scan(input.topic, level=input.safety_level)
    IF safety.violation THEN RETURN Err(COND_093_SAFETY_VIOLATION)

    # 2. Context fetch (CAT-B KG)
    context_docs = kg.fetch_context(input.context_refs, max_tokens=2000)
    IF context_docs is None AND input.context_refs THEN
        RETURN Err(COND_093_CONTEXT_FETCH_FAILED)

    # 3. Stage 1: Generator (LLM)
    draft = llm_generator.generate(
        topic=input.topic,
        content_type=input.content_type,
        difficulty=input.difficulty,
        bloom=input.target_bloom_level,
        language=input.language,
        context=context_docs,
    )

    # 4. Stage 2: Critic (LLM with self-critique prompt)
    critique = llm_critic.evaluate(draft, rubric="bloom_accuracy + factual + clarity")
    IF critique.score < 0.6 THEN
        draft = llm_refiner.rewrite(draft, critique.issues)

    # 5. Stage 3: Quiz/Flashcard extraction (content_type 분기)
    IF content_type == "quiz":
        quiz_items = extract_quiz_items(draft)
        FOR each item: item.distractor_quality = compute_distractor_quality(item)
        FOR each item: item.irt_b_estimate = estimate_difficulty_from_bloom(item)
    ELIF content_type == "flashcard":
        flashcards = extract_flashcards(draft)
    ELSE:
        pass

    # 6. Safety post-filter (output scan)
    safety_post = content_safety_scan(draft, level=input.safety_level)
    IF safety_post.violation THEN
        draft = redact_unsafe(draft, safety_post.spans)
        safety_flags = safety_post.flags

    # 7. Quality scoring
    quality = 0.4*factual_score + 0.3*bloom_alignment + 0.3*distractor_quality_avg

    # 8. Cost accounting (LOCK-CD-11 참조)
    cost = tokens_used * LLM_PRICE_PER_TOKEN
    assert cost < BUDGET_PER_REQUEST_KRW  # V2 ₩93K / request count 한도

    RETURN Ok(EduContentGenOutput(...))
```

### 4.2 Bloom's Taxonomy 난이도 매핑
```
remember   → difficulty ∈ [1, 2]
understand → difficulty ∈ [2, 3]
apply      → difficulty ∈ [3, 4]
analyze    → difficulty ∈ [3, 4]
evaluate   → difficulty ∈ [4, 5]
create     → difficulty ∈ [4, 5]
```

### 4.3 Distractor Quality
```
quality = 1 - max(0, sim_to_correct - 0.7) - max(0, 0.3 - sim_to_correct)  # 너무 가까우면 ambiguous, 너무 멀면 too_easy
sim_to_correct = cosine(embed(distractor), embed(correct_answer))
```

### 4.4 시간 복잡도
- **LLM call × 3 stages**: `O(T_out)` (token-bound)
- **Safety scan**: `O(T_in + T_out)`
- **Distractor sim**: `O(|distractors| · d)` d=embedding dim 768
- **전체**: LLM 지배 (generator ~2s, critic ~1s, refiner ~1.5s p99)

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05/06)

### 5.1 FailureCode
```
COND_093_SAFETY_VIOLATION         # 주제/결과물 안전 규정 위반 (6-2 체크리스트)
COND_093_CONTEXT_FETCH_FAILED     # KG context Read 실패
COND_093_LLM_TIMEOUT              # LLM p99 초과
COND_093_LLM_BUDGET_EXCEEDED      # 비용 한도 초과 (LOCK-CD-11)
COND_093_LANGUAGE_UNSUPPORTED     # BCP-47 지원 외
COND_093_CRITIC_DIVERGENCE        # critic 점수 3회 반복 낮음
COND_093_QUIZ_MALFORMED           # correct_index 범위 이탈 등
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Safety pre-check): violation 즉시 거부
Phase 2 (Context fetch): 실패 → context 없는 생성 (penalty × 0.6)
Phase 3 (Generation): LLM timeout → 1 retry → fallback 작은 모델 (penalty × 0.7)
Phase 3 (Critic): 수렴 실패 → draft 그대로 (penalty × 0.5)
Phase 4 (Escalation): safety 위반 반복 → I-20 + 관리자 알림
```

### 5.3 에스컬레이션 Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-093"
    error_code: str
    original_request: EduContentGenInput
    partial_result: EduContentGenOutput | None
    retry_count: int
    timestamp: datetime
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-...",
  "error": {"code": "COND_093_SAFETY_VIOLATION", "severity": "ERROR"},
  "context": {"topic": "redacted", "safety_level": "strict", "violation_type": "medical_advice"},
  "recovery": {"strategy": "reject", "fallback_id": null}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-E)
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-091 | PRODUCES | LearningUnit.content_refs 의 콘텐츠 공급 |
| COND-092 | PRODUCES | 모의시험 item 공급 |
| COND-113 | PRODUCES | 튜토리얼 스크립트/질문 공급 |
| COND-115 | PRODUCES | 언어 학습 어휘/문장 공급 |
| COND-094 | NOTIFIES | 자동 채점 기준 rubric 연계 |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| CAT-A ML (LLM) | CONSUMES | generator/critic/refiner 모델 |
| CAT-B Knowledge Graph | CONSUMES | context_refs 문서 fetch |
| `6-2 Security-Governance` | CROSS-DOMAIN | safety 정책 · 유해 콘텐츠 차단 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_093_* 이벤트 prefix |
| `3-3 PKM` | CROSS-DOMAIN | 생성 컨텐츠 저장 경로 (PKM Memory Store) |

### 6.3 의존성 매트릭스 (요약)
```
            091  092  093  094  113  114  115
COND-093  [  P    P    -    N    P    .    P  ]   P=PRODUCES, N=NOTIFIES
```

### 6.4 Phase 1 deferral 인계
본 모듈 무관 (CF-2026-04-07/08 CAT-C/D 내부 의존).

---

## §7 Performance Benchmark — §13.1 #6

| 지표 | V2 목표 | 측정 |
|---|---|---|
| p50 생성 지연 (lecture_note 500 tokens) | ≤ 2.5 s | warm LLM |
| p99 생성 지연 | ≤ 8.0 s | cold + critic 반복 |
| 처리량 | ≥ 30 req/s | 1 LLM 인스턴스당 |
| 평균 tokens/req | ≤ 1800 | generator+critic+refiner 합 |
| 평균 비용/req | ≤ ₩1.2 | GPT-4o / Claude 기준 |
| 안전 필터 민감도 | ≥ 95% recall | 내부 레드팀 코퍼스 |

### 7.1 비용 상한 (LOCK-CD-11)
V2 ₩93K / day 를 초과하지 않도록 per-request budget 가드; 초과 시 `COND_093_LLM_BUDGET_EXCEEDED`.

### 7.2 벤치마크 시나리오
```
BENCH-093-01: lecture_note 500 tok × 1000 → p50/p99/cost
BENCH-093-02: quiz 20 items × 500 → distractor_quality 평균
BENCH-093-03: safety redteam corpus 1000건 → recall/precision
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3)

### 8.1 I-05-COND093-01: 정상 퀴즈 10 문항 생성
- 주입: `topic="Gradient descent", content_type="quiz", difficulty=3`
- 기대: `quiz_items.length >= 10`, `distractor_quality avg >= 0.65`, `bloom_level == "apply"`

### 8.2 I-05-COND093-02: Safety 위반 주제 거부
- 주입: `topic="의료 처방 자가치료"`, `safety_level="strict"`
- 기대: `failure_code == "COND_093_SAFETY_VIOLATION"`, `error.severity=ERROR`, 관리자 알림 큐 enqueue 확인

### 8.3 I-05-COND093-03: Context Fetch 실패 → 컨텍스트 없이 생성
- 주입: `context_refs=["KG-rare-x"]` KG stub 404
- 기대: `confidence <= 0.6 * max`, `safety_flags` 는 none, `body_markdown` 존재

### 8.4 I-05-COND093-04 (추가): LLM timeout → fallback small model
- 주입: generator LLM 10s sleep 주입
- 기대: retry 1회 → fallback 모델 사용, `confidence <= 0.7 * max`, header `X-COND093-Fallback: small_model`

### 8.5 Phase 3 확장 (≥ 10)
| ID | 주입 | 기대 |
|---|---|---|
| 093-S5 | BCP-47 unsupported `xx-ZZ` | `LANGUAGE_UNSUPPORTED` |
| 093-S6 | critic 3회 낮은 점수 | `CRITIC_DIVERGENCE` after penalty |
| 093-S7 | quiz `correct_index=out_of_range` | `QUIZ_MALFORMED` |
| 093-S8 | 동시 50 req | p99 ≤ 8s |
| 093-S9 | budget 초과 | `LLM_BUDGET_EXCEEDED` |
| 093-S10 | flashcard 30장 | 정상 생성 |
| 093-S11 | trace_id 전파 | 로그 일치 |

---

## §9 Blue Node Integration (LOCK-CD-04/08)

- Node: Learning Node (P1)
- LOCK-CD-08 준수: Blue Node 경유 호출만 허용
- ModuleConfig (LOCK-CD-10): `priority=1, max_concurrent=8, timeout_ms=10_000, retry_policy={max_retries=1, backoff="fixed_2s"}`

### 9.1 Runnable
```python
class EduContentGenerator(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: EduContentGenInput) -> Result[EduContentGenOutput, VamosError]: ...
    def run(self, input: EduContentGenInput) -> Result[EduContentGenOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def shutdown(self) -> None: ...
```

### 9.2 이벤트 (6-12)
```
COND_093_CONTENT_GENERATED   INFO   content_type, tokens, cost_krw
COND_093_SAFETY_BLOCKED      WARN   violation_type, safety_level
COND_093_FALLBACK_MODEL      WARN   original_model, fallback
COND_093_BUDGET_EXCEEDED     ERROR  daily_spend_krw
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

**[END OF COND-093 V2]** — L3 8 항목 전수. LOCK-CD-01/03/04/05/06/10. I-05 11 시나리오. CAT-E 4 소비 모듈 (091/092/113/115) + COND-094 notify. 6-2 safety · 6-12 logging 연동.
