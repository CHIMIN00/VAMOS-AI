# COND-015: 작업패턴 프로파일링 — L2+ 상세 명세

> **모듈 ID**: COND-015
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: 작업패턴 프로파일링
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark·Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC, LOCK-CD-04 Runnable, LOCK-CD-05 ErrorHandlingStandard, LOCK-CD-06 VamosError 필드, LOCK-CD-10 ModuleConfig

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TimeRange(BaseModel):
    """시간 범위"""
    start: datetime = Field(..., description="시작 시각 (UTC)")
    end: datetime = Field(..., description="종료 시각 (UTC)")

class TaskPatternRequest(BaseModel):
    """COND-015 입력 스키마"""
    user_id: str = Field(
        ..., description="프로파일링 대상 사용자 ID"
    )
    time_range: TimeRange = Field(
        ..., description="분석 대상 시간 범위"
    )
    granularity: Literal["hourly", "daily", "weekly"] = Field(
        default="daily",
        description="분석 세분화 수준 — hourly: 시간 단위, daily: 일 단위, weekly: 주 단위"
    )
    min_support: float = Field(
        default=0.05, ge=0.01, le=0.5,
        description="Sequential Pattern Mining 최소 지지도"
    )
    max_pattern_length: int = Field(
        default=5, ge=2, le=20,
        description="탐색할 최대 패턴 길이"
    )
    prediction_horizon: int = Field(
        default=3, ge=1, le=10,
        description="예측할 미래 작업 수"
    )
    include_tool_usage: bool = Field(
        default=True,
        description="도구 사용 패턴 포함 여부"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-2024-abcdef",
                "time_range": {
                    "start": "2024-02-01T00:00:00Z",
                    "end": "2024-03-01T00:00:00Z"
                },
                "granularity": "daily",
                "min_support": 0.05,
                "max_pattern_length": 5,
                "prediction_horizon": 3,
                "include_tool_usage": True
            }
        }
```

---

## E2. Output Schema

```python
class TaskPattern(BaseModel):
    """발견된 작업 패턴"""
    pattern_id: str = Field(description="패턴 고유 ID")
    sequence: list[str] = Field(description="작업 시퀀스 (예: ['코드작성', '코드리뷰', '배포'])")
    support: float = Field(description="지지도 (전체 시퀀스 중 출현 비율)")
    confidence: float = Field(description="신뢰도 (선행 패턴 발생 시 후행 발생 확률)")
    avg_interval_minutes: float = Field(description="패턴 내 작업 간 평균 간격 (분)")
    occurrence_count: int = Field(description="패턴 출현 횟수")

class TimeslotProfile(BaseModel):
    """시간대별 활동 프로파일"""
    timeslot: str = Field(description="시간대 레이블 (예: 'Mon 09:00-10:00', '14:00-15:00')")
    activity_level: float = Field(description="활동 수준 (0.0~1.0 정규화)")
    dominant_task_type: str = Field(description="해당 시간대 주요 작업 유형")
    avg_task_count: float = Field(description="해당 시간대 평균 작업 수")

class ToolUsageProfile(BaseModel):
    """도구 사용 프로파일"""
    tool_name: str = Field(description="도구/기능 이름")
    usage_count: int = Field(description="사용 횟수")
    usage_ratio: float = Field(description="전체 대비 사용 비율")
    avg_duration_minutes: float = Field(description="평균 사용 시간 (분)")
    common_preceding_task: Optional[str] = Field(default=None, description="직전에 주로 수행하는 작업")
    common_following_task: Optional[str] = Field(default=None, description="직후에 주로 수행하는 작업")

class TaskPrediction(BaseModel):
    """작업 예측"""
    predicted_task: str = Field(description="예측된 작업 유형")
    probability: float = Field(description="예측 확률")
    predicted_time: Optional[datetime] = Field(default=None, description="예상 시각")
    reasoning: str = Field(description="예측 근거 (패턴 ID 참조)")

class UserTaskProfile(BaseModel):
    """사용자 작업 프로파일"""
    user_id: str = Field(description="사용자 ID")
    analysis_period: TimeRange = Field(description="분석 기간")
    total_tasks: int = Field(description="분석 기간 내 총 작업 수")
    unique_task_types: int = Field(description="고유 작업 유형 수")
    patterns: list[TaskPattern] = Field(description="발견된 패턴 리스트 (지지도 내림차순)")
    timeslot_profile: list[TimeslotProfile] = Field(description="시간대별 활동 프로파일")
    peak_hours: list[str] = Field(description="피크 시간대 목록")
    tool_usage: Optional[list[ToolUsageProfile]] = Field(
        default=None, description="도구 사용 프로파일 (include_tool_usage=True 시)"
    )

class TaskPatternResponse(BaseModel):
    """COND-015 출력 스키마"""
    profile: UserTaskProfile = Field(description="사용자 작업 프로파일")
    predictions: list[TaskPrediction] = Field(description="작업 예측 리스트 (확률 내림차순)")
    execution_time_ms: int = Field(description="프로파일링 실행 시간 (ms)")

    class Config:
        json_schema_extra = {
            "example": {
                "profile": {
                    "user_id": "user-2024-abcdef",
                    "analysis_period": {
                        "start": "2024-02-01T00:00:00Z",
                        "end": "2024-03-01T00:00:00Z"
                    },
                    "total_tasks": 1250,
                    "unique_task_types": 8,
                    "patterns": [
                        {
                            "pattern_id": "pat-001",
                            "sequence": ["코드작성", "코드리뷰", "배포"],
                            "support": 0.15,
                            "confidence": 0.72,
                            "avg_interval_minutes": 45.0,
                            "occurrence_count": 188
                        },
                        {
                            "pattern_id": "pat-002",
                            "sequence": ["데이터조회", "분석", "리포트생성"],
                            "support": 0.12,
                            "confidence": 0.68,
                            "avg_interval_minutes": 30.0,
                            "occurrence_count": 150
                        }
                    ],
                    "timeslot_profile": [
                        {
                            "timeslot": "Mon-Fri 09:00-10:00",
                            "activity_level": 0.85,
                            "dominant_task_type": "코드작성",
                            "avg_task_count": 12.5
                        },
                        {
                            "timeslot": "Mon-Fri 14:00-15:00",
                            "activity_level": 0.92,
                            "dominant_task_type": "코드리뷰",
                            "avg_task_count": 15.2
                        }
                    ],
                    "peak_hours": ["09:00-10:00", "14:00-15:00", "16:00-17:00"],
                    "tool_usage": [
                        {
                            "tool_name": "IDE",
                            "usage_count": 580,
                            "usage_ratio": 0.464,
                            "avg_duration_minutes": 35.0,
                            "common_preceding_task": "데이터조회",
                            "common_following_task": "코드리뷰"
                        }
                    ]
                },
                "predictions": [
                    {
                        "predicted_task": "코드리뷰",
                        "probability": 0.72,
                        "predicted_time": "2024-03-01T14:00:00Z",
                        "reasoning": "패턴 pat-001 기반: 코드작성 후 평균 45분 뒤 코드리뷰 수행 (confidence 72%)"
                    },
                    {
                        "predicted_task": "배포",
                        "probability": 0.55,
                        "predicted_time": "2024-03-01T15:30:00Z",
                        "reasoning": "패턴 pat-001 기반: 코드리뷰 후 배포 전환 (confidence 55%)"
                    }
                ],
                "execution_time_ms": 820
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: TaskPatternRequest) -> TaskPatternResponse:
    # 1. 사용자 작업 이력 조회
    user_events = TaskEventStore.query(
        user_id=request.user_id,
        start=request.time_range.start,
        end=request.time_range.end
    )
    IF NOT UserStore.exists(request.user_id):
        RETURN Err(VamosError(COND_015_USER_NOT_FOUND))

    IF len(user_events) < config.min_events_for_profiling:
        RETURN Err(VamosError(COND_015_INSUFFICIENT_DATA))

    # 2. 이벤트 전처리 — 작업 시퀀스 추출
    sequences = extract_task_sequences(user_events, request.granularity)
    # 예: [["코드작성", "코드리뷰", "배포"], ["데이터조회", "분석"], ...]

    # 3. Sequential Pattern Mining (PrefixSpan)
    prefixspan = PrefixSpan(sequences)
    prefixspan.min_support = request.min_support
    prefixspan.max_pattern_length = request.max_pattern_length

    raw_patterns = prefixspan.mine()

    # 3a. 패턴 신뢰도 계산
    patterns = []
    FOR seq, support IN raw_patterns:
        IF len(seq) < 2:
            CONTINUE
        prefix = seq[:-1]
        prefix_count = count_occurrences(sequences, prefix)
        full_count = count_occurrences(sequences, seq)
        confidence = full_count / prefix_count IF prefix_count > 0 ELSE 0

        intervals = compute_intervals(user_events, seq)
        patterns.append(TaskPattern(
            pattern_id=generate_pattern_id(),
            sequence=seq,
            support=support,
            confidence=confidence,
            avg_interval_minutes=mean(intervals),
            occurrence_count=full_count
        ))

    patterns.sort(key=lambda p: p.support, reverse=True)

    # 4. 시간대 프로파일 생성 (Time Series Clustering)
    timeslot_data = aggregate_by_timeslot(user_events, request.granularity)
    timeslot_profile = []
    FOR slot, events IN timeslot_data.items():
        task_counts = Counter(e.task_type for e IN events)
        timeslot_profile.append(TimeslotProfile(
            timeslot=slot,
            activity_level=normalize(len(events), timeslot_data),
            dominant_task_type=task_counts.most_common(1)[0][0],
            avg_task_count=len(events) / num_periods(request.time_range, slot)
        ))

    peak_hours = [ts.timeslot for ts IN timeslot_profile
                  IF ts.activity_level >= 0.75]

    # 5. 도구 사용 프로파일 (옵션)
    tool_usage = None
    IF request.include_tool_usage:
        tool_events = filter_tool_events(user_events)
        tool_usage = build_tool_profile(tool_events, sequences)

    # 6. Markov Chain 예측
    transition_matrix = build_markov_chain(sequences)
    last_tasks = get_recent_tasks(user_events, n=3)

    predictions = []
    current_state = tuple(last_tasks)
    FOR i IN range(request.prediction_horizon):
        next_task, prob = transition_matrix.predict(current_state)
        IF prob < 0.1:
            BREAK  # 신뢰도 너무 낮으면 중단

        # 시간 예측: 패턴 내 평균 간격 활용
        predicted_time = estimate_next_time(
            last_event_time=user_events[-1].timestamp,
            pattern=find_matching_pattern(patterns, current_state, next_task)
        )
        matching_pattern = find_matching_pattern(patterns, current_state, next_task)
        predictions.append(TaskPrediction(
            predicted_task=next_task,
            probability=prob,
            predicted_time=predicted_time,
            reasoning=f"패턴 {matching_pattern.pattern_id} 기반: "
                      f"{'→'.join(current_state)} 후 {next_task} 수행 "
                      f"(confidence {prob*100:.0f}%)"
        ))
        current_state = (*current_state[1:], next_task)

    predictions.sort(key=lambda p: p.probability, reverse=True)

    # 7. 프로파일 조립
    profile = UserTaskProfile(
        user_id=request.user_id,
        analysis_period=request.time_range,
        total_tasks=len(user_events),
        unique_task_types=len(set(e.task_type for e IN user_events)),
        patterns=patterns,
        timeslot_profile=timeslot_profile,
        peak_hours=peak_hours,
        tool_usage=tool_usage
    )

    RETURN TaskPatternResponse(
        profile=profile,
        predictions=predictions,
        execution_time_ms=elapsed_ms()
    )


FUNCTION build_markov_chain(sequences) -> MarkovChain:
    """작업 시퀀스로부터 n-gram Markov Chain 구축"""
    transitions = defaultdict(Counter)
    FOR seq IN sequences:
        FOR i IN range(len(seq) - 1):
            state = tuple(seq[max(0, i-2):i+1])  # 최대 3-gram
            next_state = seq[i+1]
            transitions[state][next_state] += 1

    # 정규화
    FOR state IN transitions:
        total = sum(transitions[state].values())
        FOR next_s IN transitions[state]:
            transitions[state][next_s] /= total

    RETURN MarkovChain(transitions)
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_015_USER_NOT_FOUND` | user_id에 해당하는 사용자가 존재하지 않음 | `F-015-01` | "지정된 사용자를 찾을 수 없습니다." |
| `COND_015_INSUFFICIENT_DATA` | 분석 기간 내 작업 이력이 최소 기준 미달 | `F-015-02` | "프로파일링을 위한 충분한 작업 이력이 없습니다." |
| `COND_015_PATTERN_EXTRACTION_FAILED` | PrefixSpan 패턴 추출 중 연산 오류 | `F-015-03` | "작업 패턴 추출에 실패했습니다." |
| `COND_015_PREDICTION_TIMEOUT` | Markov Chain 예측이 timeout_ms 초과 | `F-015-04` | "작업 예측 시간이 초과되었습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_015_INSUFFICIENT_DATA",
    message="Insufficient task history for user '{user_id}': {actual} events < {minimum} minimum",
    fallback_id="F-015-02",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **제공** (A-4) | COND-104 (AmbientContext) → COND-015 | UserTaskProfile → AmbientContext 보강 | ②③ |

> COND-015는 **제공 전용** — CAT-A 내부에서 소비하는 모듈 없음 (Level 0)

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `prefixspan` | ≥0.5 | Sequential Pattern Mining (PrefixSpan 알고리즘) |
| `numpy` | ≥1.24 | 수치 연산, 전이 행렬 |
| `pandas` | ≥2.0 | 시계열 집계, DataFrame 처리 |
| `scikit-learn` | ≥1.3 | Time Series Clustering (KMeans, DBSCAN) |
| `scipy` | ≥1.11 | 통계 연산, 정규화 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| TaskEventStore (PostgreSQL/ClickHouse) | 사용자 작업 이벤트 로그 저장 |
| UserStore (PostgreSQL) | 사용자 정보 관리 |
| 메모리 ≥ 2GB | PrefixSpan 패턴 마이닝 연산 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **프로파일 생성 (1K events)** | ≤ 2,000ms | PrefixSpan + 시간대 분석 |
| **프로파일 생성 (10K events)** | ≤ 8,000ms | 대규모 작업 이력 |
| **프로파일 생성 (100K events)** | ≤ 30,000ms | 장기간 이력 분석 |
| **Markov 예측** | ≤ 100ms | 3-gram 전이 행렬 조회 |
| **메모리 사용량** | ≤ 1GB (10K events) | peak RSS 측정 |
| **동시 프로파일링** | ≥ 5 users 병렬 | max_concurrent 기준 |

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 기본 프로파일 생성
```yaml
name: "basic_task_profiling"
setup:
  - create_user("user-test-001")
  - generate_task_events(user="user-test-001", count=500, types=["코드작성", "코드리뷰", "배포", "데이터조회", "분석"])
input:
  user_id: "user-test-001"
  time_range: {start: "2024-02-01T00:00:00Z", end: "2024-03-01T00:00:00Z"}
  granularity: "daily"
  min_support: 0.05
  prediction_horizon: 3
expected:
  - profile.user_id == "user-test-001"
  - profile.total_tasks == 500
  - profile.patterns.length > 0
  - all(p.support >= 0.05 for p in profile.patterns)
  - profile.timeslot_profile.length > 0
  - profile.peak_hours.length > 0
  - predictions.length <= 3
  - all(p.probability > 0 for p in predictions)
  - execution_time_ms < 5000
```

### 시나리오 2: 시간 단위 세분화 + 도구 사용 포함
```yaml
name: "hourly_with_tool_usage"
setup:
  - create_user("user-test-002")
  - generate_task_events(user="user-test-002", count=1000, include_tools=true)
input:
  user_id: "user-test-002"
  time_range: {start: "2024-02-15T00:00:00Z", end: "2024-02-22T00:00:00Z"}
  granularity: "hourly"
  include_tool_usage: true
expected:
  - profile.timeslot_profile has hourly entries (e.g., "09:00-10:00")
  - profile.tool_usage is not None
  - profile.tool_usage.length > 0
  - all(t.usage_ratio > 0 for t in profile.tool_usage)
```

### 시나리오 3: 에러 — 사용자 미존재
```yaml
name: "error_user_not_found"
input:
  user_id: "nonexistent-user"
  time_range: {start: "2024-02-01T00:00:00Z", end: "2024-03-01T00:00:00Z"}
  granularity: "daily"
expected:
  - error.failure_code == "COND_015_USER_NOT_FOUND"
  - error.fallback_id == "F-015-01"
```

### 시나리오 4: 에러 — 이력 부족
```yaml
name: "error_insufficient_data"
setup:
  - create_user("user-test-003")
  - generate_task_events(user="user-test-003", count=2)  # 너무 적음
input:
  user_id: "user-test-003"
  time_range: {start: "2024-02-01T00:00:00Z", end: "2024-03-01T00:00:00Z"}
  granularity: "daily"
expected:
  - error.failure_code == "COND_015_INSUFFICIENT_DATA"
  - error.fallback_id == "F-015-02"
```

---

## E8. Blue Node Integration

> §B.6.1 CAT-A 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.1)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Research Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy |
| **우선순위** | MEDIUM |

### 호출 패턴
```
System → "사용자 작업 패턴 분석 및 다음 작업 예측"
  → ORANGE CORE (I-1 Intent 해석: profile_task_pattern)
    → I-5 라우팅 → Research Node
      → Research Node: COND-015.execute(user_id="user-...", time_range={...})
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (사용자 데이터 접근 권한 확인)
          → COND-015 실행 → TaskPatternResponse 반환
            → Research Node → ORANGE CORE
              → (선택) COND-104 AmbientContext에 UserTaskProfile 전달
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.015.initialized` | initialize() 완료 |
| 프로파일링 시작 | `cond.a.015.execute_start` | execute() 진입 |
| 프로파일링 완료 | `cond.a.015.execute_done` | 정상 반환 |
| 프로파일링 실패 | `cond.a.015.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.015.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.015.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-015", "execution_ms": N, "result_type": "task_profile", "patterns_found": K, "predictions_count": P }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond015TaskPatternProfiling(BaseModule):
    """COND-015 작업패턴 프로파일링"""

    async def initialize(self) -> Result[None, VamosError]:
        """TaskEventStore 연결, UserStore 연결, PrefixSpan 엔진 초기화"""
        self._event_store = await TaskEventStore.connect()
        self._user_store = await UserStore.connect()
        self._profile_cache = LRUCache(max_size=self.config.cache_max_profiles)
        self._emit_event("cond.a.015.initialized")
        return Ok(None)

    async def execute(self, request: TaskPatternRequest) -> Result[TaskPatternResponse, VamosError]:
        """Runnable.run() 위임 — 작업 패턴 프로파일링 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """TaskEventStore, UserStore 연결 상태 확인"""
        event_ok = await self._event_store.ping()
        user_ok = await self._user_store.ping()
        return Ok(HealthStatus(
            healthy=event_ok and user_ok,
            latency_ms=elapsed,
            details={"event_store": event_ok, "user_store": user_ok}
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """스토어 연결 해제, 캐시 정리"""
        await self._event_store.disconnect()
        await self._user_store.disconnect()
        self._profile_cache.clear()
        self._emit_event("cond.a.015.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-015", version="1.0.0",
            capabilities=["task_pattern_mining", "timeslot_profiling", "markov_prediction", "tool_usage_analysis"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond015Config(ModuleConfig):
    """COND-015 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 5
    timeout_ms: int = 30000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=1000)

    # COND-015 전용 설정
    default_granularity: Literal["hourly", "daily", "weekly"] = "daily"
    default_min_support: float = 0.05
    default_max_pattern_length: int = 5
    default_prediction_horizon: int = 3
    min_events_for_profiling: int = 50  # 최소 이벤트 수
    markov_ngram_size: int = 3  # Markov Chain n-gram 크기
    peak_hour_threshold: float = 0.75  # 피크 시간대 판정 임계값
    cache_max_profiles: int = 100  # 프로파일 캐시 최대 수
    cache_ttl_seconds: int = 3600  # 캐시 TTL (1시간)
    event_store_dsn: str = "clickhouse://vamos:***@localhost/task_events"
    enable_incremental_update: bool = True  # 증분 업데이트 활성화
```
