# COND-115 언어 학습 (Language Learning)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-115
> **카테고리**: CAT-E Education
> **우선순위**: MEDIUM
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-1
> **Phase 1 대응**: 종합명세 §115
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10

---

## §0 교차 참조 블록

- **종합계획서**: §7.4 (세션 2-1) / §13.1 / §B
- **종합명세**: §#115
- **AUTHORITY_CHAIN**: §4 LOCK-CD-01~11
- **ErrorHandling**: `D2.0-02 §0.3`
- **교차 도메인**: `3-3 PKM` LOCK-PKM-02 (Spaced Repetition) · `3-2 Multimodal-Processing` (TTS/STT) · `6-2 Security-Governance` · `6-12 Event-Logging`
- **연계 모듈**: COND-091 (경로 통합) · COND-093 (어휘/문장 컨텐츠 공급) · COND-094 (발음/문법 채점) · COND-114 (학습 분석)

---

## §1 개요

### 1.1 목적
외국어 학습을 지원한다. 어휘 · 문법 · 발음 · 대화 시뮬레이션 · CEFR 레벨 평가 · Anki 기반 간격 반복 게임형 학습.

### 1.2 핵심 기술
- **Spaced Repetition (Anki SM-2)**: ease factor `[1.3, 2.5]` (COND-091 과 일관성)
- **TTS/STT**: 3-2 Multimodal-Processing 위임 (언어별 음성 모델)
- **Dialogue Simulation**: LLM + 역할 프롬프트 + CEFR 레벨 매칭
- **Grammar Error Correction (GEC)**: encoder-decoder (e.g., T5-small)

### 1.3 LOCK 준수 요약
LOCK-CD-01/03/04/05/06/10 전수.

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
ExerciseType = Literal["vocab", "grammar", "pronunciation", "conversation"]

class LanguageLearningInput(BaseModel):
    target_language: str = Field(..., min_length=2, max_length=10, description="BCP-47 (en, fr, ja-JP)")
    learner_level: CefrLevel
    exercise_type: ExerciseType
    native_language: str = Field(default="ko", min_length=2)
    daily_minutes: int = Field(default=20, ge=5, le=240)
    topic: str | None = Field(default=None, max_length=200)

    @field_validator("target_language", "native_language")
    @classmethod
    def bcp47_basic(cls, v):
        parts = v.split("-")
        if not parts[0].isalpha() or not 2 <= len(parts[0]) <= 3:
            raise ValueError(f"invalid language tag: {v}")
        return v
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal

class VocabCard(BaseModel):
    card_id: str
    term: str
    translation: str
    example_sentence: str
    pronunciation_ipa: str | None = None
    ease_factor: float = Field(..., ge=1.3, le=2.5)
    next_review_days: int = Field(..., ge=0)

class GrammarDrill(BaseModel):
    drill_id: str
    prompt: str
    expected_answer: str
    alternatives: list[str] = Field(default_factory=list)
    cefr_level: CefrLevel

class ConversationTurn(BaseModel):
    role: Literal["learner", "tutor"]
    text: str
    audio_ref: str | None = None

class LanguageExercise(BaseModel):
    exercise_id: str
    exercise_type: ExerciseType
    vocab_cards: list[VocabCard] = Field(default_factory=list)
    grammar_drills: list[GrammarDrill] = Field(default_factory=list)
    dialogue: list[ConversationTurn] = Field(default_factory=list)
    estimated_minutes: int

class ExerciseEvaluation(BaseModel):
    accuracy: float = Field(..., ge=0.0, le=1.0)
    feedback: str
    gec_corrections: list[dict] = Field(default_factory=list, description="{span, suggestion, explanation}")
    pronunciation_score: float | None = None

class LanguageLearningOutput(BaseModel):
    exercise: LanguageExercise
    evaluation: ExerciseEvaluation
    level_update: CefrLevel | None = Field(default=None, description="레벨 승격 시 새 레벨")
    confidence: float = Field(..., ge=0.0, le=1.0)
    cost_krw: float = Field(..., ge=0.0)
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM LanguageLearning(input) -> Result<Output, VamosError>:
    # 1. Fetch learner's SM-2 state
    sm2_state = pkm.get_spaced_repetition_state(
        learner_id=..., language=input.target_language
    )

    # 2. Branch by exercise_type
    updated_ease = None
    IF type == "vocab":
        due_cards = sm2_select_due(sm2_state, count=ceil(daily_minutes/0.5))
        new_cards = request_new_cards_from_COND093(count=5, cefr=input.learner_level)
        vocab_cards = merge_due_and_new(due_cards, new_cards)
    ELIF type == "grammar":
        drills = request_drills_from_COND093(level=input.learner_level, count=10)
    ELIF type == "pronunciation":
        audio_exercises = build_pron_exercises(learner_level, topic=input.topic)
    ELIF type == "conversation":
        dialogue = simulate_dialogue(level=input.learner_level, topic=input.topic, turns=10)

    # 3. Evaluate learner response (runtime, 예시)
    IF submission_provided:
        IF type == "vocab":
            accuracy = exact_match_ratio(submission, expected)
            updated_ease = sm2_update(sm2_state, quality=compute_quality(accuracy))
        ELIF type == "grammar":
            gec_corrections = gec_model.correct(submission)
            accuracy = 1 - len(gec_corrections) / expected_tokens
        ELIF type == "pronunciation":
            stt_result = multimodal.stt(audio, language=target)
            pronunciation_score = wer_based(stt_result, reference)
        ELIF type == "conversation":
            accuracy = llm_judge(dialogue, cefr_level=input.learner_level)

    # 4. Level update (CEFR promotion logic)
    IF rolling_accuracy(learner) >= 0.85 OVER 20 exercises AT current_level:
        level_update = next_cefr(input.learner_level)
    ELSE:
        level_update = None

    # 5. Persist SM-2 update (PKM) + emit event (6-12)
    pkm.upsert_spaced_repetition(sm2_state, updated_ease)
    emit_event("COND_115_EXERCISE_COMPLETED", ...)

    # 6. Confidence
    confidence = 0.6 + 0.3 * signal_strength + 0.1 * (1 if sm2_state is fresh else 0)

    RETURN Ok(LanguageLearningOutput(...))
```

### 4.2 SM-2 Update (재사용 — COND-091 / PKM LOCK-PKM-02 일관성)
```
quality ∈ {0..5}  # 0=blackout, 5=perfect
IF quality < 3:
    interval = 1
    ease = max(1.3, ease - 0.2)
ELSE:
    IF interval == 1: interval = 6
    ELIF interval == 6: interval = 16
    ELSE: interval = round(interval * ease)
    ease = min(2.5, ease + 0.1 - (5 - quality)*0.08)
```

### 4.3 CEFR 레벨 승격 조건
- 20 exercises rolling window 에서 평균 accuracy ≥ 0.85
- AND 최소 14일 현 레벨 유지
- AND 문법/발음/어휘 3 영역 전수 ≥ 0.75

### 4.4 시간 복잡도
- SM-2 select: `O(|due|)`
- GEC inference: `O(T · d)` (encoder-decoder)
- 전체: LLM/STT 호출 지배 (p99 ≤ 3s)

---

## §5 Error Handling — §13.1 #4

### 5.1 FailureCode
```
COND_115_LANGUAGE_UNSUPPORTED       # target_language 외
COND_115_TTS_STT_UNAVAILABLE        # 3-2 Multimodal 실패
COND_115_SM2_STATE_CORRUPT          # PKM state 역직렬화 실패
COND_115_CEFR_LEVEL_INVALID
COND_115_GEC_MODEL_TIMEOUT
COND_115_CONTENT_FETCH_FAILED       # COND-093 위임 실패
```

### 5.2 Phase별 복구 전략
```
Phase 1 (State Fetch): corrupt → reset + 1 retry (penalty × 0.5)
Phase 2 (Content Gen): COND-093 실패 → 캐시된 예비 카드 사용 (penalty × 0.7)
Phase 3 (Eval): STT 실패 → 텍스트 입력 fallback (pronunciation 점수 null, penalty × 0.6)
Phase 3 (GEC): 모델 timeout → rule-based 기본 검사 fallback (penalty × 0.7)
Phase 4 (Escalation): 반복 실패 → I-20
```

### 5.3 에스컬레이션 Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-115"
    error_code: str
    original_request: LanguageLearningInput
    partial_result: LanguageLearningOutput | None
    retry_count: int
    timestamp: datetime
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-...",
  "error": {"code": "COND_115_TTS_STT_UNAVAILABLE", "severity": "WARN"},
  "context": {"learner_id": "...", "language": "ja-JP", "exercise_type": "pronunciation"},
  "recovery": {"strategy": "text_fallback", "confidence_penalty": 0.6}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 (CAT-E)
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-091 | SHARES | SM-2 ease factor `[1.3, 2.5]` 범위 일관성 |
| COND-093 | CONSUMES | 어휘/문장 컨텐츠 공급 |
| COND-094 | CONSUMES | 발음/문법 채점 위임 |
| COND-114 | NOTIFIES | 연습 완료 이벤트 |

### 6.2 외부
| 대상 | 방향 | 이유 |
|---|---|---|
| `3-2 Multimodal-Processing` | CROSS-DOMAIN | TTS / STT 호출 |
| `3-3 PKM` LOCK-PKM-02 | CROSS-DOMAIN | SM-2 상태 저장소 정본 |
| `3-3 PKM` LOCK-PKM-03 | CROSS-DOMAIN | Memory Store (학습 이력) |
| `6-2 Security-Governance` | CROSS-DOMAIN | 음성 데이터 PII 보호 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_115_* prefix |

### 6.3 의존성 매트릭스 (요약)
```
            091  092  093  094  113  114  115
COND-115  [  S    .    C    C    .    N    -  ]
```

---

## §7 Performance Benchmark — §13.1 #6

| 지표 | V2 목표 | 측정 |
|---|---|---|
| p50 응답 (vocab) | ≤ 150 ms | SM-2 select + 10 cards |
| p50 (grammar/pron) | ≤ 1.8 s | GEC 또는 STT 호출 |
| p99 | ≤ 5.0 s | conversation 10 turns LLM |
| 처리량 | ≥ 60 req/s | mixed |
| STT WER target | ≤ 0.12 | CEFR ≥ B1 |
| GEC BLEU | ≥ 0.85 | 학습 코퍼스 |

### 7.1 벤치마크 시나리오
```
BENCH-115-01: vocab 100k turns → p50/p99
BENCH-115-02: pronunciation WER by CEFR level
BENCH-115-03: CEFR 승격 로직 검증 (200 learner 시뮬)
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3)

### 8.1 I-05-COND115-01: Vocab 정상 (SM-2 업데이트)
- 주입: `exercise_type="vocab", learner_level="B1"`, 제출=정답
- 기대: `vocab_cards.length >= 10`, `updated_ease in [1.3, 2.5]`, 성공 시 `ease ↑`, PKM upsert 호출 확인

### 8.2 I-05-COND115-02: Pronunciation STT 실패 → 텍스트 fallback
- 주입: `exercise_type="pronunciation"`, STT stub 500
- 기대: `pronunciation_score is None`, `confidence <= 0.6 * max`, header `X-COND115-Fallback: text`

### 8.3 I-05-COND115-03: CEFR 승격
- 주입: 과거 20 exercises rolling accuracy=0.88, 14일 경과
- 기대: `level_update == "B2"` (B1→B2)

### 8.4 I-05-COND115-04: Unsupported language
- 주입: `target_language="xx"` (지원 외)
- 기대: `failure_code == "COND_115_LANGUAGE_UNSUPPORTED"`

### 8.5 Phase 3 확장 (≥ 10)
| ID | 주입 | 기대 |
|---|---|---|
| 115-S5 | SM-2 state corrupt | reset + retry → penalty 0.5 |
| 115-S6 | GEC timeout | rule-based fallback |
| 115-S7 | conversation 10 turns | dialogue simulate OK |
| 115-S8 | concurrent 50 | p99 ≤ 5s |
| 115-S9 | daily_minutes=5 | 카드 ≤ 10 제한 |
| 115-S10 | Pydantic invalid BCP-47 | validator 차단 |
| 115-S11 | trace 전파 | 로그 일치 |

---

## §9 Blue Node Integration (LOCK-CD-04/08)

- Node: Learning Node (P1)
- LOCK-CD-08 준수
- ModuleConfig (LOCK-CD-10): `priority=2, max_concurrent=20, timeout_ms=6000, retry_policy={max_retries=1, backoff="fixed_1s"}`

### 9.1 Runnable
```python
class LanguageLearning(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: LanguageLearningInput) -> Result[LanguageLearningOutput, VamosError]: ...
    def run(self, input: LanguageLearningInput) -> Result[LanguageLearningOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def shutdown(self) -> None: ...
```

### 9.2 이벤트 (6-12)
```
COND_115_EXERCISE_COMPLETED   INFO   exercise_type, accuracy
COND_115_LEVEL_UP             INFO   from, to
COND_115_TTS_STT_FALLBACK     WARN   language
COND_115_SM2_CORRUPT          ERROR  learner_id
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

**[END OF COND-115 V2]** — L3 8 항목 전수. LOCK-CD-01/03/04/05/06/10. I-05 11 시나리오. CAT-E 4 연계 (091/093/094/114). 3-2 Multimodal · 3-3 PKM LOCK-PKM-02/03 · 6-2 · 6-12 연동.
