# COND-092 시험준비 도우미 (Exam Preparation Assistant)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-092
> **카테고리**: CAT-E Education
> **우선순위**: MEDIUM
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-1
> **Phase 1 대응**: 종합명세 §92 + `05_cat-e-education/_index.md`
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10

---

## §0 교차 참조 블록 (정본)

- **종합계획서**: `COND_MODULES_DETAIL_구조화_종합계획서.md` §7.4 (세션 2-1) / §13.1 / §B Blue Node 매핑
- **종합명세**: `COND_MODULES_종합명세.md` §#92 (I/O 정의)
- **AUTHORITY_CHAIN**: `AUTHORITY_CHAIN.md` §4 LOCK-CD-01~11
- **ErrorHandling 정본**: `D2.0-02 §0.3`
- **Runnable Protocol 정본**: `D2.0-02 §1.2-A`
- **교차 도메인**: `3-3 PKM` (spaced repetition) · `6-2 Security-Governance` (시험 데이터 무결성) · `6-12 Event-Logging`
- **연계 모듈**: COND-091 (학습 경로 / 취약 영역 복습 경로 주입) · COND-094 (자동 채점 / 모의시험 채점 재사용) · COND-114 (학습 분석 / 취약 영역 통계)

---

## §1 개요

### 1.1 목적
사용자가 지정한 시험·자격증 준비를 위해 맞춤 학습 계획, 모의시험 생성, 취약 영역 분석, 오답 관리를 제공한다.

### 1.2 핵심 기술
- **IRT (Item Response Theory) 3-PL**: 문항 난이도(b) · 변별도(a) · 추측도(c) 추정
- **CAT (Computerized Adaptive Testing)**: Maximum Fisher Information 기반 다음 문항 선택
- **Spaced Repetition**: Anki SM-2 기반 오답 복습 스케줄 (ease factor `[1.3, 2.5]`)
- **Question Generation**: COND-093 위임(콘텐츠 생성) + 자체 난이도 보정 레이어

### 1.3 LOCK 준수 요약
| LOCK | 준수 |
|---|---|
| LOCK-CD-01 | COND-092 (CAT-E 3자리) |
| LOCK-CD-03 | BaseModule ABC 4 메서드 |
| LOCK-CD-04 | Runnable 프로토콜 |
| LOCK-CD-05 | Result<T, VamosError> |
| LOCK-CD-06 | VamosError 4 필드 |
| LOCK-CD-10 | ModuleConfig 5 필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import date

class ExamInfo(BaseModel):
    exam_name: str = Field(..., min_length=1, max_length=200)
    target_date: date = Field(..., description="시험 예정일 (UTC)")
    syllabus: list[str] = Field(..., min_length=1, description="주제 영역 IDs (KG node_id)")
    total_score: int = Field(..., gt=0, le=10_000)
    pass_threshold: float = Field(..., ge=0.0, le=1.0, description="합격 정규화 기준 [0~1]")
    time_limit_minutes: int = Field(..., gt=0, le=600)

class AssessmentResult(BaseModel):
    assessment_id: str
    learner_id: str
    theta_estimate: float = Field(..., ge=-4.0, le=4.0, description="IRT 능력모수 θ")
    theta_se: float = Field(..., gt=0.0, description="SE(θ) 표준오차")
    mastery_by_topic: dict[str, float] = Field(default_factory=dict)

    @field_validator("mastery_by_topic")
    @classmethod
    def mastery_range(cls, v):
        for k, m in v.items():
            if not 0.0 <= m <= 1.0:
                raise ValueError(f"mastery out of range for {k}: {m}")
        return v

class ExamPrepInput(BaseModel):
    exam_info: ExamInfo
    current_level: AssessmentResult
    study_hours_per_week: float = Field(..., gt=0.0, le=168.0)
    preferred_mock_count: int = Field(default=3, ge=1, le=20)
```

### 2.1 예시
```json
{
  "exam_info": {
    "exam_name": "AWS Solutions Architect - Associate",
    "target_date": "2026-06-15",
    "syllabus": ["KG-AWS-EC2", "KG-AWS-S3", "KG-AWS-VPC"],
    "total_score": 1000,
    "pass_threshold": 0.72,
    "time_limit_minutes": 130
  },
  "current_level": {
    "assessment_id": "ASSESS-2f9",
    "learner_id": "LEARNER-7f3a",
    "theta_estimate": 0.4,
    "theta_se": 0.35,
    "mastery_by_topic": {"KG-AWS-EC2": 0.6, "KG-AWS-S3": 0.75, "KG-AWS-VPC": 0.4}
  },
  "study_hours_per_week": 8.0,
  "preferred_mock_count": 4
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal

class StudyPlanItem(BaseModel):
    topic_id: str
    week_offset: int = Field(..., ge=0)
    hours: float = Field(..., gt=0.0)
    priority: Literal["low", "medium", "high", "critical"]
    content_refs: list[str] = Field(default_factory=list)

class StudyPlan(BaseModel):
    items: list[StudyPlanItem]
    total_hours: float
    weeks_remaining: int
    review_schedule: dict[str, list[int]] = Field(
        default_factory=dict,
        description="topic_id → review week offsets (SM-2 generated)"
    )

class MockExamItem(BaseModel):
    question_id: str
    topic_id: str
    irt_b: float = Field(..., ge=-3.0, le=3.0)
    irt_a: float = Field(..., ge=0.5, le=3.0)
    irt_c: float = Field(..., ge=0.0, le=0.3)
    bloom_level: Literal["remember", "understand", "apply", "analyze", "evaluate", "create"]

class MockExam(BaseModel):
    exam_id: str
    items: list[MockExamItem]
    estimated_duration_minutes: int
    target_theta: float = Field(..., description="이 세트가 타겟하는 능력 수준")
    information_at_target: float = Field(..., ge=0.0, description="Fisher Information(θ)")

class WeaknessReport(BaseModel):
    top_weak_topics: list[str] = Field(..., min_length=0)
    mastery_gaps: dict[str, float]
    recommended_focus_hours: dict[str, float]
    incorrect_pattern_clusters: list[str] = Field(default_factory=list)

class ExamPrepOutput(BaseModel):
    study_plan: StudyPlan
    mock_exam: MockExam
    weakness_analysis: WeaknessReport
    pass_probability: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM ExamPrep(input) -> Result<Output, VamosError>:
    # 1. Validate weeks_remaining
    weeks = (exam_info.target_date - today) / 7
    IF weeks <= 0 THEN RETURN Err(COND_092_EXAM_DATE_PASSED)

    # 2. Topic-wise time allocation (mastery-gap weighted)
    gaps = { topic: max(0, pass_threshold - mastery) for topic in syllabus }
    total_gap = sum(gaps.values())
    time_budget = study_hours_per_week * weeks
    topic_hours = { t: (gaps[t]/total_gap) * time_budget for t in syllabus if gaps[t] > 0 }

    # 3. Study plan generation (priority-based ordering)
    priorities = assign_priority(gaps, pass_threshold)
    study_plan = generate_plan(topic_hours, priorities, weeks)

    # 4. Review schedule via SM-2 (weak topics auto-scheduled)
    review_schedule = sm2_generate_reviews(priorities, weeks, ease=[1.3, 2.5])

    # 5. Mock exam generation (CAT + Maximum Fisher Information)
    target_theta = current_level.theta_estimate + 0.3  # 약간 더 어려운 세트
    item_pool = fetch_item_pool(syllabus)
    mock_items = cat_select_items(
        item_pool, theta=target_theta, count=ceil(duration/per_item_time)
    )
    info_target = sum(fisher_information(it, target_theta) for it in mock_items)

    # 6. Weakness analysis (mastery-gap clustering)
    weak_topics = sorted(syllabus, key=lambda t: mastery_by_topic.get(t, 0))[:3]
    pattern_clusters = detect_incorrect_patterns(current_level)

    # 7. Pass probability estimation
    pass_prob = estimate_pass_probability(theta_estimate, theta_se, pass_threshold)

    # 8. Confidence scoring
    confidence = 1.0 - 0.5 * (theta_se / 1.0)   # theta_se 정규화

    RETURN Ok(ExamPrepOutput(...))
```

### 4.2 IRT 3-PL Fisher Information
```
I(θ; a, b, c) = a² * (1 - c)² * P(θ) * Q(θ) / (c + P(θ))²
  where P(θ) = c + (1-c) / (1 + exp(-a(θ - b)))
       Q(θ) = 1 - P(θ)
CAT: 다음 문항 선택 = argmax_item I(θ_current; item.a, item.b, item.c)
```

### 4.3 Pass Probability (정규근사)
```
Z = (theta_estimate - theta_at_pass) / theta_se
pass_prob = Φ(Z)    # 표준정규 CDF
  theta_at_pass = irt_solve_theta(pass_threshold, item_pool)
```

### 4.4 시간 복잡도
- **CAT selection**: `O(|pool| · k)` k=세트 크기 (≤ 100)
- **Study plan**: `O(|syllabus| · weeks)` (≤ 30 · 52)
- **SM-2 scheduling**: `O(|weak_topics| · weeks)`
- **전체**: `O(|pool| · k)` 지배 (pool ≤ 10_000 → ≤ 1M ops)

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05/06)

### 5.1 FailureCode
```
COND_092_EXAM_DATE_PASSED         # target_date 가 과거
COND_092_ITEM_POOL_INSUFFICIENT   # syllabus 커버 item < threshold
COND_092_THETA_SE_TOO_HIGH        # SE(θ) > 1.0 → CAT 불안정
COND_092_SYLLABUS_UNMAPPED        # syllabus[i] KG 미매핑
COND_092_MOCK_EXAM_UNDERFILLED    # 시간 제한 내 item 수 부족
COND_092_LEARNER_NOT_FOUND
COND_092_IRT_NONCONVERGENT        # IRT 추정 발산
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation): Pydantic 차단 → 즉시 400
Phase 2 (Gap Analysis): mastery 누락 → 0.0 가정 (conservative, penalty × 0.9)
Phase 3 (CAT Generation): item pool 부족 → syllabus 추가 COND-093 위임 생성 (penalty × 0.7)
Phase 4 (Escalation): IRT 비수렴 → I-20 에스컬레이션 (retry 2회 후)
```

### 5.3 에스컬레이션 Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-092"
    error_code: str
    original_request: ExamPrepInput
    partial_result: ExamPrepOutput | None
    retry_count: int
    timestamp: datetime
```

### 5.4 로깅 포맷 (R-01-7 중첩 JSON)
```json
{
  "trace_id": "trace-...",
  "error": {"code": "COND_092_ITEM_POOL_INSUFFICIENT", "severity": "WARN"},
  "context": {"exam": "AWS-SAA", "syllabus_size": 25, "pool_coverage": 0.4},
  "recovery": {"strategy": "COND093_GEN_ONDEMAND", "confidence_penalty": 0.7}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-E)
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-091 학습 경로 | CONSUMES | 취약 영역 기반 경로 재계산 |
| COND-093 컨텐츠 생성 | CONSUMES | 부족 item 온디맨드 생성 |
| COND-094 교육 평가 | CONSUMES | 모의시험 채점 재사용 |
| COND-114 학습 분석 | NOTIFIES | 모의시험 점수 이벤트 |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| CAT-A ML (IRT / CAT) | CONSUMES | IRT 파라미터 추정기 |
| CAT-B Knowledge Graph | CONSUMES | syllabus → KG node 매핑 |
| `3-3 PKM` LOCK-PKM-02 (Spaced Repetition) | CROSS-DOMAIN | SM-2 파라미터 일관성 |
| `6-2 Security-Governance` | CROSS-DOMAIN | 시험 데이터 무결성 · 부정방지 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_092_* FailureCode prefix |

### 6.3 의존성 매트릭스 (요약, 상세는 _index.md)
```
            091  092  093  094  113  114  115
COND-092  [  C    -    C    C    .    N    .  ]
```

### 6.4 Phase 1 deferral 인계
- CF-2026-04-07 / CF-2026-04-08 deferral: 본 모듈 무관

---

## §7 Performance Benchmark — §13.1 #6

| 지표 | V2 목표 | 측정 |
|---|---|---|
| p50 응답 시간 (mock exam 생성) | ≤ 250 ms | item pool size 2000 |
| p99 응답 시간 | ≤ 800 ms | pool size 10_000 |
| 처리량 | ≥ 80 req/s | 단일 인스턴스 |
| CAT selection iter | ≤ 50 평균 | 100 items/exam |
| IRT 추정 지연 | ≤ 150 ms | theta_se < 0.3 수렴 |
| 메모리 | ≤ 640 MB | 단일 request |

### 7.1 비용 상한 (LOCK-CD-11)
V2 ₩93K 한도; COND-093 위임 호출 발생 시 per-request ≤ ₩0.5 추산.

### 7.2 벤치마크 시나리오
```
BENCH-092-01: 워밍업 후 pool=5000 × 1000 회 → p50/p99
BENCH-092-02: Item pool 부족(40% coverage) 주입 → COND-093 위임 p99 측정
BENCH-092-03: IRT 비수렴 10% 주입 → 에스컬레이션 비율 측정
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3 시나리오)

### 8.1 I-05-COND092-01: 정상 시험 준비 생성
- **주입**: AWS SAA 예제, 4주 남음, `theta_estimate=0.4`
- **기대**: `study_plan.weeks_remaining==4`, `mock_exam.items.length > 10`, `pass_probability in [0.4, 0.9]`
- **목**: `mocks/COND-092/happy_aws.json`

### 8.2 I-05-COND092-02: Item Pool 부족 → COND-093 위임
- **주입**: syllabus=`["KG-rare-topic"]`, pool coverage = 0.3
- **기대**: degradation header 반환, `confidence <= 0.7 * max`, `context.pool_coverage < 0.5` 로깅

### 8.3 I-05-COND092-03: 시험일 경과
- **주입**: `target_date` = 지난 날짜
- **기대**: `failure_code == "COND_092_EXAM_DATE_PASSED"`, HTTP 400

### 8.4 I-05-COND092-04 (추가): θ SE 과다
- **주입**: `theta_se = 1.2`
- **기대**: `COND_092_THETA_SE_TOO_HIGH`, fallback 경로 제안 (diagnostic exam 선권장)

### 8.5 Phase 3 확장 (≥ 10 시나리오)
| ID | 주입 | 기대 |
|---|---|---|
| 092-S5 | IRT 비수렴 주입 | 에스컬레이션 |
| 092-S6 | concurrent 50 | p99 ≤ 800ms |
| 092-S7 | 학습자 미존재 | `LEARNER_NOT_FOUND` |
| 092-S8 | pass_threshold=0.99 | pass_prob 정상 계산 (극단값) |
| 092-S9 | syllabus 100 항목 | 대형 입력 메모리 확인 |
| 092-S10 | SM-2 review 주 간격 검증 | 간격 = interval * ease |
| 092-S11 | trace_id 전파 | 응답/로그 일치 |

---

## §9 Blue Node Integration (LOCK-CD-04/08) — §13.1 #8

- **주요 소비 Node**: Learning Node (P1)
- **LOCK-CD-08**: Blue Node 는 CORE 규칙 상속; 독립 실행 불가
- **ModuleConfig** (LOCK-CD-10): `priority=2, max_concurrent=12, timeout_ms=3000, retry_policy={max_retries=2, backoff=exp}`

### 9.1 Runnable 메서드
```python
class ExamPrepAssistant(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: ExamPrepInput) -> Result[ExamPrepOutput, VamosError]: ...
    def run(self, input: ExamPrepInput) -> Result[ExamPrepOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def shutdown(self) -> None: ...
```

### 9.2 Blue Node 이벤트 (6-12 Event-Logging)
```
COND_092_EXAM_PLAN_CREATED    INFO   exam_name, weeks_remaining
COND_092_MOCK_GENERATED       INFO   item_count, info_at_target
COND_092_POOL_AUGMENTED       WARN   strategy=COND093_ONDEMAND
COND_092_ESCALATED            ERROR  failure_code
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

**[END OF COND-092 V2]** — L3 8 항목 전수. LOCK-CD-01/03/04/05/06/10. I-05 11 시나리오. CAT-E 내부 4 연계 (091/093/094/114). CAT-B KG / CAT-A ML 외부 의존. PKM LOCK-PKM-02 교차.
