# COND-088: 예측적 지식서핑 (S7JM) — L2+ 상세 명세

> **모듈 ID**: COND-088
> **카테고리**: CAT-B (Knowledge)
> **이름**: 예측적 지식서핑 (S7JM)
> **우선순위**: LOW
> **Phase**: Phase 0
> **L-Level**: L2+
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ScheduledJob(BaseModel):
    job_id: str = Field(..., description="STEP7 JM 작업 ID")
    job_name: str = Field(..., description="작업 이름")
    scheduled_at: str = Field(..., description="예정 실행 시각 (ISO 8601)")
    job_type: str = Field(..., description="작업 유형 (예: report, analysis, deployment)")
    dependencies: list[str] = Field(default=[], description="선행 작업 ID 목록")
    tags: list[str] = Field(default=[], description="작업 태그 (지식 매핑 키)")
    metadata: dict = Field(default={}, description="작업 메타데이터 (도메인, 도구 등)")

class PrefetchPolicy(BaseModel):
    strategy: Literal["eager", "lazy", "adaptive"] = Field(
        default="adaptive", description="프리페치 전략"
    )
    max_bundles: int = Field(default=10, ge=1, le=50, description="최대 프리페치 번들 수")
    priority_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0, description="프리페치 우선순위 임계값"
    )

class PredictiveSurfingRequest(BaseModel):
    """COND-088 입력 스키마"""
    job_schedule: list[ScheduledJob] = Field(
        ..., min_length=1, description="STEP7 JM 작업 스케줄 목록"
    )
    user_id: str = Field(..., description="사용자 ID")
    lookahead_hours: int = Field(
        default=24, ge=1, le=168, description="미리보기 시간 범위 (시간 단위, 최대 7일)"
    )
    prefetch_policy: PrefetchPolicy = Field(
        default_factory=PrefetchPolicy, description="프리페치 정책"
    )
    include_dependency_chain: bool = Field(
        default=True, description="선행 작업 의존 체인의 지식도 포함"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_schedule": [
                    {
                        "job_id": "job_2026_0401_001",
                        "job_name": "월간 매출 보고서 생성",
                        "scheduled_at": "2026-04-01T09:00:00Z",
                        "job_type": "report",
                        "dependencies": [],
                        "tags": ["매출", "보고서", "월간"],
                        "metadata": {"domain": "finance", "template": "monthly_sales"}
                    },
                    {
                        "job_id": "job_2026_0401_002",
                        "job_name": "고객 이탈 분석",
                        "scheduled_at": "2026-04-01T10:00:00Z",
                        "job_type": "analysis",
                        "dependencies": ["job_2026_0401_001"],
                        "tags": ["고객", "이탈", "분석"],
                        "metadata": {"domain": "crm", "model": "churn_v3"}
                    }
                ],
                "user_id": "user_42",
                "lookahead_hours": 24,
                "prefetch_policy": {
                    "strategy": "adaptive",
                    "max_bundles": 10,
                    "priority_threshold": 0.5
                },
                "include_dependency_chain": True
            }
        }
```

---

## E2. Output Schema

```python
class KnowledgeItem(BaseModel):
    knowledge_id: str = Field(description="지식 항목 ID")
    title: str = Field(description="지식 제목")
    content_preview: str = Field(description="콘텐츠 미리보기 (첫 200자)")
    relevance_score: float = Field(description="작업 관련도 점수 (0.0~1.0)")
    source: str = Field(description="지식 출처 (wiki, document, note 등)")
    memory_layer: Literal["L0", "L1"] = Field(description="프리로드 대상 메모리 레이어")

class KnowledgeBundle(BaseModel):
    bundle_id: str = Field(description="번들 ID")
    job_id: str = Field(description="대상 작업 ID")
    job_name: str = Field(description="대상 작업 이름")
    scheduled_at: str = Field(description="작업 예정 시각")
    items: list[KnowledgeItem] = Field(description="프리로드된 지식 항목 목록")
    prefetch_priority: float = Field(description="프리페치 우선순위 (0.0~1.0)")
    cache_key: Optional[str] = Field(default=None, description="시맨틱 캐시 키")
    cache_ttl_sec: int = Field(description="캐시 TTL (초)")
    status: Literal["prefetched", "cached", "pending"] = Field(description="번들 상태")

class PredictiveSurfingResponse(BaseModel):
    """COND-088 출력 스키마"""
    preloaded_knowledge: list[KnowledgeBundle] = Field(
        description="프리로드된 지식 번들 목록"
    )
    job_knowledge_map: dict[str, list[str]] = Field(
        description="작업 ID → 지식 항목 ID 매핑"
    )
    total_items_prefetched: int = Field(description="프리페치된 총 지식 항목 수")
    cache_hit_count: int = Field(description="시맨틱 캐시 히트 수")
    lookahead_window: str = Field(description="미리보기 윈도우 (예: 'next 24h')")
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "preloaded_knowledge": [
                    {
                        "bundle_id": "bundle_001",
                        "job_id": "job_2026_0401_001",
                        "job_name": "월간 매출 보고서 생성",
                        "scheduled_at": "2026-04-01T09:00:00Z",
                        "items": [
                            {
                                "knowledge_id": "k_fin_001",
                                "title": "월간 매출 보고서 작성 가이드",
                                "content_preview": "월간 매출 보고서는 전월 대비 증감률, 부서별 매출...",
                                "relevance_score": 0.92,
                                "source": "wiki",
                                "memory_layer": "L0"
                            },
                            {
                                "knowledge_id": "k_fin_002",
                                "title": "2026 Q1 매출 데이터 요약",
                                "content_preview": "2026년 1분기 매출 총액: 15.2B, 전년 동기 대비...",
                                "relevance_score": 0.88,
                                "source": "document",
                                "memory_layer": "L1"
                            }
                        ],
                        "prefetch_priority": 0.95,
                        "cache_key": "sem_cache_fin_monthly_202604",
                        "cache_ttl_sec": 86400,
                        "status": "prefetched"
                    }
                ],
                "job_knowledge_map": {
                    "job_2026_0401_001": ["k_fin_001", "k_fin_002"],
                    "job_2026_0401_002": ["k_crm_001"]
                },
                "total_items_prefetched": 3,
                "cache_hit_count": 1,
                "lookahead_window": "next 24h",
                "execution_time_ms": 1200
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: PredictiveSurfingRequest) -> PredictiveSurfingResponse:
    # 1. 입력 검증
    validation = validate_schedule(request.job_schedule, request.lookahead_hours)
    IF NOT validation.valid:
        RETURN Err(COND_088_INVALID_SCHEDULE, details=validation.errors)

    # 2. 미리보기 윈도우 내 작업 필터링 + 정렬
    now = current_time()
    cutoff = now + hours(request.lookahead_hours)
    jobs_in_window = [j for j in request.job_schedule
                      IF parse_iso(j.scheduled_at) >= now AND parse_iso(j.scheduled_at) <= cutoff]
    jobs_in_window.sort(key=lambda j: j.scheduled_at)

    IF len(jobs_in_window) == 0:
        RETURN Ok(PredictiveSurfingResponse(
            preloaded_knowledge=[], job_knowledge_map={},
            total_items_prefetched=0, cache_hit_count=0,
            lookahead_window=f"next {request.lookahead_hours}h",
            execution_time_ms=elapsed_ms()
        ))

    # 3. 의존 체인 확장
    IF request.include_dependency_chain:
        dep_jobs = resolve_dependency_chain(request.job_schedule, jobs_in_window)
        jobs_in_window = merge_unique(jobs_in_window, dep_jobs)

    # 4. 작업별 지식 요구 분석
    bundles = []
    job_knowledge_map = {}
    cache_hit_count = 0
    total_items = 0

    FOR job IN jobs_in_window:
        # 4a. 시맨틱 캐시 확인 (D2.0-06 §4.7, cosine ≥ 0.95, TTL 24h)
        cache_key = build_cache_key(request.user_id, job)
        cached = semantic_cache.get(cache_key, threshold=0.95)
        IF cached is not None:
            bundle = cached.to_bundle(status="cached")
            bundles.append(bundle)
            job_knowledge_map[job.job_id] = [item.knowledge_id for item in bundle.items]
            cache_hit_count += 1
            total_items += len(bundle.items)
            CONTINUE

        # 4b. 작업 태그/메타데이터 기반 지식 검색 쿼리 생성
        search_query = build_knowledge_query(job.tags, job.metadata, job.job_type)

        # 4c. 접근 패턴 라우터 (D2.0-06 §10.4.1) — L0/L1 프리페치 대상 결정
        access_pattern = access_pattern_router.predict(
            user_id=request.user_id, job=job
        )

        # 4d. 시맨틱 검색 (BGE-M3 1024dim, DEC-005)
        query_vec = bge_m3_encode(search_query)
        search_results = vectorstore.search(
            query_vec, limit=20,
            filter={"user_id": request.user_id}
        )

        # 4e. 프리페치 우선순위 계산
        time_urgency = compute_urgency(job.scheduled_at, now)
        dep_weight = min(1.0, len(job.dependencies) * 0.1)
        prefetch_priority = time_urgency * 0.6 + dep_weight * 0.2 + access_pattern.score * 0.2

        IF prefetch_priority < request.prefetch_policy.priority_threshold:
            CONTINUE  # 임계값 미달 → 스킵

        # 4f. 상위 N개 항목 선택 + 메모리 레이어 할당
        top_items = []
        FOR result IN search_results[:request.prefetch_policy.max_bundles]:
            layer = "L0" IF result.score >= 0.85 ELSE "L1"
            item = KnowledgeItem(
                knowledge_id=result.id,
                title=result.metadata["title"],
                content_preview=result.content[:200],
                relevance_score=result.score,
                source=result.metadata.get("source", "unknown"),
                memory_layer=layer
            )
            top_items.append(item)

        # 4g. 번들 생성 + 캐시 저장
        bundle = KnowledgeBundle(
            bundle_id=generate_bundle_id(),
            job_id=job.job_id, job_name=job.job_name,
            scheduled_at=job.scheduled_at,
            items=top_items,
            prefetch_priority=prefetch_priority,
            cache_key=cache_key,
            cache_ttl_sec=86400,  # 24h
            status="prefetched"
        )

        # 시맨틱 캐시 저장 (D2.0-06 §4.7)
        semantic_cache.put(cache_key, bundle, ttl=86400)

        bundles.append(bundle)
        job_knowledge_map[job.job_id] = [item.knowledge_id for item in top_items]
        total_items += len(top_items)

    # 5. 번들 수 제한 (정책 max_bundles)
    bundles = bundles[:request.prefetch_policy.max_bundles]

    RETURN Ok(PredictiveSurfingResponse(
        preloaded_knowledge=bundles,
        job_knowledge_map=job_knowledge_map,
        total_items_prefetched=total_items,
        cache_hit_count=cache_hit_count,
        lookahead_window=f"next {request.lookahead_hours}h",
        execution_time_ms=elapsed_ms()
    ))
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_088_INVALID_SCHEDULE` | job_schedule 형식 오류 (ISO 8601 파싱 실패, 빈 목록 등) | `F-088-01` | "작업 스케줄 형식이 올바르지 않습니다." |
| `COND_088_JM_CONNECTION_FAILED` | STEP7 JM 연동 실패 (연결 타임아웃, 인증 오류) | `F-088-02` | "STEP7 Job Manager 연결에 실패했습니다." |
| `COND_088_KNOWLEDGE_FETCH_FAILED` | 지식 검색/프리페치 실패 (VectorStore 오류) | `F-088-03` | "지식 프리로드 중 오류가 발생했습니다." |
| `COND_088_CACHE_WRITE_FAILED` | 시맨틱 캐시 쓰기 실패 | `F-088-04` | "캐시 저장에 실패했습니다. 프리로드는 정상 수행되었습니다." |
| `COND_088_DEPENDENCY_CYCLE` | 작업 의존 체인에 순환 참조 발견 | `F-088-05` | "작업 스케줄에 순환 의존이 있습니다." |
| `COND_088_PREFETCH_TIMEOUT` | 프리페치 작업이 timeout_ms 초과 | `F-088-06` | "지식 프리로드 시간이 초과되었습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_088_INVALID_SCHEDULE",
    message="Invalid schedule: job_id='job_x' has unparseable scheduled_at='not-a-date'",
    fallback_id="F-088-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-B 내부 의존 (§A.3.2)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| (없음) | — | Level 0: 내부 의존 없음 | — |

> COND-088은 **Level 0** — CAT-B 내부 의존 없음 (독립 모듈)

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
| `pydantic` | ≥2.5 | 스키마 검증 |
| `sentence-transformers` | ≥2.3 | BGE-M3 임베딩 (DEC-005) |
| `croniter` | ≥2.0 | JM 스케줄 파싱 (cron 표현식) |
| `networkx` | ≥3.2 | 작업 의존 그래프 분석 (순환 검출) |
| `cachetools` | ≥5.3 | 로컬 캐시 유틸리티 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| VectorStore (Qdrant/Milvus) | 시맨틱 검색 (D2.0-06) |
| Semantic Cache (Redis) | 시맨틱 캐시 (cosine ≥ 0.95, TTL 24h) |
| STEP7 JM API | 작업 스케줄 조회 |
| 메모리 ≥ 256MB | 프리페치 번들 + 캐시 |

### D2.0-06 LOCK Citations

> LOCK (D2.0-06 §4.7): Semantic Cache — cosine_similarity ≥ 0.95 히트, TTL 24시간, 소스 변경 시 즉시 무효화
> LOCK (D2.0-06 §10.4.1): 쿼리 라우팅 — factual: L2→L1, procedural: L3→L1, creative: L1→L0

---

## E6. Performance Benchmark

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **스케줄 분석 (10 jobs)** | ≤ 200ms | 작업 파싱 + 의존 체인 해석 |
| **지식 검색 (단일 작업)** | ≤ 500ms | VectorStore semantic search |
| **프리페치 (10 bundles)** | ≤ 3,000ms | 전체 번들 생성 + 캐시 저장 |
| **캐시 히트 조회** | ≤ 50ms | 시맨틱 캐시 cosine 비교 |
| **의존 체인 해석 (20 jobs)** | ≤ 100ms | DAG 분석 + 순환 검출 |
| **임베딩 연산 (BGE-M3)** | ≤ 200ms | 단일 쿼리 1024dim 벡터 생성 |

### 병목 요인 및 최적화
- **VectorStore 검색**: 작업 수에 비례 → 배치 검색 + 병렬 쿼리
- **프리페치 번들**: max_bundles로 상한 제한 → adaptive 전략에서 우선순위 기반 절삭
- **캐시 미스 연속**: 초기 콜드 스타트 → eager 전략으로 빠른 워밍업

---

## E7. Integration Test Spec

### 시나리오 1: 기본 프리페치 (2 작업, adaptive)
```yaml
name: "basic_prefetch_adaptive"
setup:
  - seed_knowledge_base(user_id="test_user", items=30)
  - mock_jm_api(jobs=2)
input:
  job_schedule:
    - {job_id: "j1", job_name: "보고서 생성", scheduled_at: "+2h", job_type: "report",
       dependencies: [], tags: ["보고서", "매출"], metadata: {domain: "finance"}}
    - {job_id: "j2", job_name: "데이터 분석", scheduled_at: "+4h", job_type: "analysis",
       dependencies: ["j1"], tags: ["분석", "통계"], metadata: {domain: "analytics"}}
  user_id: "test_user"
  lookahead_hours: 6
  prefetch_policy: {strategy: "adaptive", max_bundles: 10, priority_threshold: 0.3}
  include_dependency_chain: true
expected:
  - len(preloaded_knowledge) >= 1
  - len(preloaded_knowledge) <= 10
  - all(b.status in ["prefetched", "cached"] for b in preloaded_knowledge)
  - "j1" in job_knowledge_map
  - total_items_prefetched > 0
  - execution_time_ms < 3000
```

### 시나리오 2: 캐시 히트 확인
```yaml
name: "semantic_cache_hit"
setup:
  - seed_knowledge_base(user_id="test_user", items=20)
  - pre_populate_cache(user_id="test_user", job_id="j1", ttl=86400)
input:
  job_schedule:
    - {job_id: "j1", job_name: "보고서 생성", scheduled_at: "+2h", job_type: "report",
       dependencies: [], tags: ["보고서", "매출"], metadata: {domain: "finance"}}
  user_id: "test_user"
  lookahead_hours: 4
expected:
  - cache_hit_count >= 1
  - any(b.status == "cached" for b in preloaded_knowledge)
  - execution_time_ms < 500  # 캐시 히트로 빠른 응답
```

### 시나리오 3: 스케줄 형식 오류
```yaml
name: "error_invalid_schedule"
setup: []
input:
  job_schedule:
    - {job_id: "j1", job_name: "잘못된 작업", scheduled_at: "not-a-date", job_type: "report",
       dependencies: [], tags: [], metadata: {}}
  user_id: "test_user"
  lookahead_hours: 24
expected:
  - error.failure_code == "COND_088_INVALID_SCHEDULE"
  - error.fallback_id == "F-088-01"
```

### 시나리오 4: 의존 체인 순환 참조
```yaml
name: "error_dependency_cycle"
setup: []
input:
  job_schedule:
    - {job_id: "j1", job_name: "작업A", scheduled_at: "+2h", job_type: "report",
       dependencies: ["j2"], tags: [], metadata: {}}
    - {job_id: "j2", job_name: "작업B", scheduled_at: "+3h", job_type: "report",
       dependencies: ["j1"], tags: [], metadata: {}}
  user_id: "test_user"
  lookahead_hours: 6
  include_dependency_chain: true
expected:
  - error.failure_code == "COND_088_DEPENDENCY_CYCLE"
  - error.fallback_id == "F-088-05"
```

---

## E8. Blue Node Integration

> §B.6.2 CAT-B 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.2)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Research Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy |
| **우선순위** | LOW |

### 호출 패턴
```
User → "내일 오전 작업들에 필요한 자료 미리 준비해줘"
  → ORANGE CORE (I-1 Intent 해석: predictive_knowledge_prefetch)
    → I-5 라우팅 → Research Node
      → Research Node: COND-088.execute(job_schedule=..., lookahead_hours=24, ...)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (지식 프리페치 정책 확인)
          → COND-088 실행:
            → STEP7 JM 스케줄 분석
            → 의존 체인 해석
            → VectorStore 시맨틱 검색 (D2.0-06)
            → Semantic Cache 확인/저장 (D2.0-06 §4.7)
            → L0/L1 프리페치 (D2.0-06 §10.4.1)
          → PredictiveSurfingResponse 반환
            → Research Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.b.088.initialized` | initialize() 완료 |
| 실행 시작 | `cond.b.088.execute_start` | execute() 진입 |
| 실행 완료 | `cond.b.088.execute_done` | 정상 반환 |
| 실행 실패 | `cond.b.088.execute_fail` | VamosError 발생 |
| 프리페치 완료 | `cond.b.088.prefetch_done` | 번들 프리로드 완료 |
| 캐시 히트 | `cond.b.088.cache_hit` | 시맨틱 캐시 히트 |
| 헬스체크 | `cond.b.088.health` | health_check() 호출 |
| 모듈 종료 | `cond.b.088.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-088", "execution_ms": N, "bundles_prefetched": M, "cache_hits": K, "lookahead_hours": H }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond088PredictiveSurfingS7JM(BaseModule):
    """COND-088 예측적 지식서핑 (S7JM)"""

    async def initialize(self) -> Result[None, VamosError]:
        """VectorStore 연결, 시맨틱 캐시 초기화, JM API 클라이언트 설정"""
        self._vectorstore = await VectorStoreAdapter.connect(
            collection="knowledge_base", dim=1024  # DEC-005 BGE-M3
        )
        self._semantic_cache = await SemanticCache.connect(
            threshold=0.95, default_ttl=86400  # D2.0-06 §4.7
        )
        self._embedder = BGE_M3_Encoder(dim=1024)
        self._jm_client = STEP7_JM_Client()
        self._access_router = AccessPatternRouter()  # D2.0-06 §10.4.1
        self._emit_event("cond.b.088.initialized")
        return Ok(None)

    async def execute(self, request: PredictiveSurfingRequest) -> Result[PredictiveSurfingResponse, VamosError]:
        """Runnable.run() 위임 — 예측적 지식 프리페치"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """VectorStore + 시맨틱 캐시 + JM API 가용성 확인"""
        vs_ok = await self._vectorstore.ping()
        cache_ok = await self._semantic_cache.ping()
        jm_ok = await self._jm_client.ping()
        return Ok(HealthStatus(
            healthy=vs_ok and cache_ok and jm_ok,
            latency_ms=elapsed
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """VectorStore 연결 해제, 시맨틱 캐시 플러시, JM 연결 종료"""
        await self._semantic_cache.flush()
        await self._vectorstore.disconnect()
        await self._jm_client.close()
        self._emit_event("cond.b.088.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-088", version="1.0.0",
            capabilities=["predictive_prefetch", "job_schedule_analysis",
                          "dependency_chain_resolution", "semantic_cache",
                          "knowledge_bundling", "access_pattern_routing"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond088Config(ModuleConfig):
    """COND-088 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "low"
    max_concurrent: int = 4
    timeout_ms: int = 10000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=1000)

    # COND-088 전용 설정
    default_lookahead_hours: int = 24
    max_lookahead_hours: int = 168  # 7일
    default_prefetch_strategy: Literal["eager", "lazy", "adaptive"] = "adaptive"
    max_bundles_per_request: int = 10
    priority_threshold: float = 0.5
    semantic_cache_threshold: float = 0.95  # D2.0-06 §4.7
    semantic_cache_ttl_sec: int = 86400  # 24h
    embedding_model: str = "bge-m3"
    embedding_dim: int = 1024  # DEC-005
    vectorstore_collection: str = "knowledge_base"
    jm_api_base_url: str = "http://step7-jm:8080/api/v1"
    jm_api_timeout_ms: int = 5000
    max_items_per_bundle: int = 20
    prefetch_l0_score_threshold: float = 0.85
    prefetch_l1_score_threshold: float = 0.60
    enable_dependency_chain: bool = True
    cycle_detection_enabled: bool = True
```
