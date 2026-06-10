# COND-019: 지식 신선도 관리 — L2+ 상세 명세

> **모듈 ID**: COND-019
> **카테고리**: CAT-B (Knowledge)
> **이름**: 지식 신선도 관리
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark/Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class DomainRule(BaseModel):
    """도메인별 신선도 규칙"""
    domain: str = Field(..., description="도메인 식별자 (news, finance, legal, tech, etc.)")
    max_age_hours: int = Field(..., ge=1, description="최대 허용 나이 (시간)")
    refresh_strategy: Literal["auto_recrawl", "manual_review", "deprecate"] = Field(
        default="auto_recrawl",
        description="만료 시 갱신 전략"
    )
    priority_boost: float = Field(
        default=1.0, ge=0.1, le=5.0,
        description="도메인 우선순위 가중치 (높을수록 빠른 갱신)"
    )

class FreshnessPolicy(BaseModel):
    """신선도 정책 정의"""
    max_age_hours: int = Field(
        default=720, ge=1,
        description="기본 최대 허용 나이 (시간, 기본 30일)"
    )
    domain_rules: list[DomainRule] = Field(
        default_factory=list,
        description="도메인별 커스텀 규칙"
    )
    check_source_availability: bool = Field(
        default=True,
        description="원본 소스 가용성 확인 여부"
    )
    qod_recheck: bool = Field(
        default=True,
        description="QoD 재평가 동반 여부"
    )

class KnowledgeFreshnessRequest(BaseModel):
    """COND-019 입력 스키마"""
    knowledge_ids: list[str] = Field(
        default_factory=list,
        description="신선도 검사 대상 지식 항목 ID 목록 (targeted 모드에서 필수)"
    )
    freshness_policy: FreshnessPolicy = Field(
        default_factory=FreshnessPolicy,
        description="신선도 정책"
    )
    scan_mode: Literal["targeted", "full_scan", "domain_scan"] = Field(
        default="targeted",
        description="검사 모드 — targeted: 지정 ID만, full_scan: 전체, domain_scan: 도메인 단위"
    )
    target_domain: Optional[str] = Field(
        default=None,
        description="domain_scan 시 대상 도메인"
    )
    trigger_refresh: bool = Field(
        default=False,
        description="만료 항목에 대해 자동 갱신 트리거 여부"
    )
    namespace: str = Field(
        default="default",
        description="지식 저장소 네임스페이스"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "knowledge_ids": ["kg-node-001", "kg-node-002", "mem-2024-050"],
                "freshness_policy": {
                    "max_age_hours": 168,
                    "domain_rules": [
                        {
                            "domain": "news",
                            "max_age_hours": 24,
                            "refresh_strategy": "auto_recrawl",
                            "priority_boost": 3.0
                        },
                        {
                            "domain": "finance",
                            "max_age_hours": 1,
                            "refresh_strategy": "auto_recrawl",
                            "priority_boost": 5.0
                        },
                        {
                            "domain": "legal",
                            "max_age_hours": 720,
                            "refresh_strategy": "manual_review",
                            "priority_boost": 2.0
                        }
                    ],
                    "check_source_availability": True,
                    "qod_recheck": True
                },
                "scan_mode": "targeted",
                "trigger_refresh": True,
                "namespace": "user-42/knowledge-base"
            }
        }
```

---

## E2. Output Schema

```python
class FreshnessEntry(BaseModel):
    """개별 지식 항목의 신선도 보고서"""
    id: str = Field(description="지식 항목 ID")
    title: Optional[str] = Field(default=None, description="항목 제목/요약")
    domain: str = Field(default="general", description="도메인 분류")
    age_hours: float = Field(description="현재 나이 (시간)")
    max_age_hours: int = Field(description="적용된 최대 허용 나이")
    status: Literal["fresh", "aging", "stale", "expired", "unknown"] = Field(
        description="신선도 상태"
    )
    refresh_priority: Literal["critical", "high", "medium", "low", "none"] = Field(
        description="갱신 우선순위"
    )
    source_available: Optional[bool] = Field(
        default=None, description="원본 소스 가용 여부"
    )
    qod_current: Optional[float] = Field(
        default=None, description="현재 QoD 점수"
    )
    qod_previous: Optional[float] = Field(
        default=None, description="이전 QoD 점수 (변화 추적)"
    )
    refresh_triggered: bool = Field(
        default=False, description="자동 갱신 트리거 여부"
    )
    last_verified: Optional[datetime] = Field(
        default=None, description="마지막 검증 시각"
    )
    next_check_at: Optional[datetime] = Field(
        default=None, description="다음 검사 예정 시각"
    )

class KnowledgeFreshnessResponse(BaseModel):
    """COND-019 출력 스키마"""
    freshness_report: list[FreshnessEntry] = Field(
        description="항목별 신선도 보고서"
    )
    stale_count: int = Field(description="만료/스테일 항목 수")
    fresh_count: int = Field(description="신선 항목 수")
    aging_count: int = Field(description="노화 중 항목 수")
    refresh_triggered_count: int = Field(
        default=0, description="갱신 트리거된 항목 수"
    )
    scan_coverage: float = Field(
        description="검사 커버리지 (검사 완료 / 전체 대상)"
    )
    summary: str = Field(description="신선도 검사 요약")
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "freshness_report": [
                    {
                        "id": "kg-node-001",
                        "title": "서울시 AI 스타트업 지원 프로그램",
                        "domain": "news",
                        "age_hours": 48.5,
                        "max_age_hours": 24,
                        "status": "expired",
                        "refresh_priority": "high",
                        "source_available": True,
                        "qod_current": 0.65,
                        "qod_previous": 0.85,
                        "refresh_triggered": True,
                        "last_verified": "2024-03-15T10:00:00Z",
                        "next_check_at": "2024-03-17T10:00:00Z"
                    }
                ],
                "stale_count": 1,
                "fresh_count": 1,
                "aging_count": 1,
                "refresh_triggered_count": 1,
                "scan_coverage": 1.0,
                "summary": "3건 검사 완료: 신선 1건, 노화 1건, 만료 1건. 뉴스 도메인 1건 자동 갱신 트리거.",
                "execution_time_ms": 850
            }
        }
```

---

## E3. Algorithm Pseudocode

> LOCK (D2.0-06 §2.1): TTL policy by layer — L0(Session, session-scoped), L1(Project, 90d), L2(Long-term, 무기한)
> LOCK (D2.0-06 §4.7.2): 캐시 무효화 — TTL 만료, 소스 변경, QoD 하락
> LOCK (D2.0-06 §2.5.2): QoD < 0.4 → L2/L3 저장 금지

```
FUNCTION execute(request: KnowledgeFreshnessRequest) -> Result<KnowledgeFreshnessResponse, VamosError>:

    # 0. 입력 검증
    validation = validate_request(request)
    IF validation.is_err:
        RETURN Err(validation.error)

    start_time = now_ms()

    # 1. 대상 지식 항목 수집
    knowledge_items = []

    IF request.scan_mode == "targeted":
        FOR kid IN request.knowledge_ids:
            item = KnowledgeStore.get(kid, namespace=request.namespace)
            IF item IS NOT None:
                knowledge_items.append(item)
            ELSE:
                LOG.warn("Knowledge item not found", id=kid)

    ELIF request.scan_mode == "full_scan":
        knowledge_items = KnowledgeStore.get_all(namespace=request.namespace)

    ELIF request.scan_mode == "domain_scan":
        IF request.target_domain IS None:
            RETURN Err(VamosError(COND_019_NO_TARGET_DOMAIN))
        knowledge_items = KnowledgeStore.get_by_domain(
            domain=request.target_domain,
            namespace=request.namespace
        )

    IF len(knowledge_items) == 0:
        RETURN Err(VamosError(COND_019_NO_ITEMS_FOUND))

    # 2. 도메인 규칙 인덱스 구축
    domain_rules_map = {}
    FOR rule IN request.freshness_policy.domain_rules:
        domain_rules_map[rule.domain] = rule

    # 3. 항목별 신선도 평가
    report_entries = []
    stale_count = 0
    fresh_count = 0
    aging_count = 0
    refresh_triggered = 0

    FOR item IN knowledge_items:
        # 3a. 도메인 분류 (미분류 시 자동 감지)
        domain = item.domain
        IF domain IS None OR domain == "":
            domain = DomainClassifier.classify(item.content)

        # 3b. 적용할 TTL 결정
        IF domain IN domain_rules_map:
            rule = domain_rules_map[domain]
            max_age = rule.max_age_hours
            strategy = rule.refresh_strategy
            priority_boost = rule.priority_boost
        ELSE:
            max_age = request.freshness_policy.max_age_hours
            strategy = "auto_recrawl"
            priority_boost = 1.0

        # 3c. Layer-level TTL 보정
        # LOCK (D2.0-06 §2.1): L0=session, L1=90d, L2=무기한
        IF item.memory_layer == "L0":
            # L0은 세션 종료 시 만료 — 별도 TTL 없음
            max_age = min(max_age, 24)  # 세션 내 최대 24시간
        ELIF item.memory_layer == "L1":
            max_age = min(max_age, 2160)  # 90일 상한
        ELIF item.memory_layer == "L2":
            # L2는 무기한이나 도메인 규칙이 있으면 준수
            pass  # max_age = 도메인 규칙 그대로 적용

        # 3d. 나이 계산
        age_hours = (now() - item.created_at).total_seconds() / 3600.0

        # 3e. 상태 결정
        ratio = age_hours / max_age
        IF ratio < 0.5:
            status = "fresh"
            fresh_count += 1
        ELIF ratio < 0.8:
            status = "aging"
            aging_count += 1
        ELIF ratio < 1.0:
            status = "stale"
            stale_count += 1
        ELSE:
            status = "expired"
            stale_count += 1

        # 3f. 갱신 우선순위 계산
        base_priority = calculate_base_priority(ratio, status)
        adjusted_priority = adjust_priority(base_priority, priority_boost, item.access_frequency)

        # 3g. 소스 가용성 확인 (선택)
        source_available = None
        IF request.freshness_policy.check_source_availability AND item.source_url IS NOT None:
            source_available = await SourceChecker.check_availability(item.source_url)
            IF NOT source_available:
                # 소스 불가 → 만료 처리
                # LOCK (D2.0-06 §4.7.2): 소스 변경 연동 무효화
                prev_status = status
                status = "expired"
                IF prev_status != "expired":
                    stale_count += 1

        # 3h. QoD 재평가 (선택)
        qod_current = item.qod_score
        qod_previous = item.qod_score
        IF request.freshness_policy.qod_recheck:
            qod_current = QoDEvaluator.score(
                item.content,
                source=item.source,
                formula="relevance*0.30 + accuracy*0.25 + freshness*0.25 + completeness*0.20"
            )
            IF qod_current < 0.4 AND item.memory_layer IN ("L2", "L3"):
                # LOCK (D2.0-06 §2.5.2): QoD < 0.4 → L2/L3 저장 금지
                status = "expired"
                adjusted_priority = "critical"
                LOG.warn("QoD dropped below threshold for L2/L3 item",
                         id=item.id, qod=qod_current)

                # 캐시 무효화 트리거
                # LOCK (D2.0-06 §4.7.2): QoD 하락 시 무효화
                SemanticCache.invalidate(item_id=item.id)

        # 3i. 자동 갱신 트리거
        refresh_was_triggered = False
        IF request.trigger_refresh AND status IN ("stale", "expired"):
            IF strategy == "auto_recrawl" AND source_available != False:
                RefreshQueue.enqueue(
                    item_id=item.id,
                    source_url=item.source_url,
                    priority=adjusted_priority,
                    domain=domain
                )
                refresh_was_triggered = True
                refresh_triggered += 1
            ELIF strategy == "manual_review":
                NotificationService.notify_review_needed(item_id=item.id, reason="freshness_expired")
            ELIF strategy == "deprecate":
                KnowledgeStore.mark_deprecated(item.id)

        # 3j. 다음 검사 시각 계산
        IF status == "fresh":
            check_interval = max_age * 0.5
        ELIF status == "aging":
            check_interval = max_age * 0.1
        ELSE:
            check_interval = max_age * 0.05  # 만료 항목은 빈번하게

        next_check = now() + timedelta(hours=check_interval)

        entry = FreshnessEntry(
            id=item.id,
            title=item.title,
            domain=domain,
            age_hours=age_hours,
            max_age_hours=max_age,
            status=status,
            refresh_priority=adjusted_priority,
            source_available=source_available,
            qod_current=qod_current,
            qod_previous=qod_previous,
            refresh_triggered=refresh_was_triggered,
            last_verified=now(),
            next_check_at=next_check
        )
        report_entries.append(entry)

        # 3k. 신선도 메타데이터 업데이트
        KnowledgeStore.update_freshness_meta(
            item_id=item.id,
            status=status,
            last_verified=now(),
            next_check_at=next_check,
            qod_score=qod_current
        )

    # 4. 요약 생성
    total = len(report_entries)
    scan_coverage = total / max(len(knowledge_items), 1)
    summary = generate_freshness_summary(
        total=total,
        fresh=fresh_count,
        aging=aging_count,
        stale=stale_count,
        refreshed=refresh_triggered
    )

    RETURN Ok(KnowledgeFreshnessResponse(
        freshness_report=report_entries,
        stale_count=stale_count,
        fresh_count=fresh_count,
        aging_count=aging_count,
        refresh_triggered_count=refresh_triggered,
        scan_coverage=scan_coverage,
        summary=summary,
        execution_time_ms=elapsed_ms(start_time)
    ))


FUNCTION calculate_base_priority(ratio: float, status: str) -> str:
    IF status == "expired":
        RETURN "critical" IF ratio > 2.0 ELSE "high"
    ELIF status == "stale":
        RETURN "high"
    ELIF status == "aging":
        RETURN "medium"
    ELSE:
        RETURN "none"


FUNCTION adjust_priority(base: str, boost: float, access_freq: float) -> str:
    """접근 빈도와 도메인 부스트로 우선순위 조정"""
    priority_map = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}
    reverse_map = {4: "critical", 3: "high", 2: "medium", 1: "low", 0: "none"}
    score = priority_map[base] * boost * (1 + log(1 + access_freq))
    clamped = min(4, max(0, round(score)))
    RETURN reverse_map[clamped]
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_019_NO_ITEMS_FOUND` | 지정된 knowledge_ids에 해당하는 항목 없음 | `F-019-01` | "검사 대상 지식 항목을 찾을 수 없습니다." |
| `COND_019_NO_TARGET_DOMAIN` | domain_scan인데 target_domain 미지정 | `F-019-02` | "도메인 스캔 시 대상 도메인을 지정해 주세요." |
| `COND_019_STORE_UNAVAILABLE` | 지식 저장소 연결 실패 | `F-019-03` | "지식 저장소에 연결할 수 없습니다." |
| `COND_019_SOURCE_CHECK_TIMEOUT` | 원본 소스 가용성 확인 시간 초과 | `F-019-04` | "원본 소스 확인 시간이 초과되었습니다." |
| `COND_019_REFRESH_QUEUE_FULL` | 갱신 큐가 가득 찬 상태 | `F-019-05` | "갱신 대기열이 가득 차 있습니다. 잠시 후 다시 시도해 주세요." |
| `COND_019_QOD_EVALUATOR_FAILURE` | QoD 평가 엔진 오류 | `F-019-06` | "품질 평가에 실패했습니다." |
| `COND_019_SCAN_LIMIT_EXCEEDED` | full_scan 시 항목 수가 최대 제한 초과 | `F-019-07` | "전체 스캔 항목 수가 한도를 초과합니다. 도메인 스캔을 사용해 주세요." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_019_NO_ITEMS_FOUND",
    message="No knowledge items found for IDs: {ids}",
    fallback_id="F-019-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-B 내부 의존 (§A.3.2)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비** (B-1) | COND-019 → COND-018 | KG 노드의 TTL/신선도 메타데이터 관리 | ②③ |

> COND-019는 **Level 2** — COND-018(Level 1)을 소비

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
| `httpx` | ≥0.25 | 원본 소스 가용성 확인 (HTTP HEAD) |
| `apscheduler` | ≥3.10 | 주기적 신선도 스캔 스케줄링 |
| `redis` | ≥4.5 | 갱신 큐 + 스캔 결과 캐시 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| Redis | 갱신 큐 (RefreshQueue), 신선도 캐시 |
| KnowledgeStore (ChromaDB/Neo4j) | 지식 항목 메타데이터 조회/갱신 |
| Cron/Scheduler | 주기적 신선도 스캔 트리거 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **targeted 스캔 (10건)** | ≤ 500ms | ID 직접 조회 + 신선도 평가 |
| **targeted 스캔 (100건)** | ≤ 3,000ms | 배치 처리 |
| **domain_scan (1K 항목)** | ≤ 10,000ms | 도메인 필터 + 일괄 평가 |
| **full_scan (10K 항목)** | ≤ 60,000ms | 전체 스캔 (페이징) |
| **소스 가용성 확인** | ≤ 2,000ms/건 | HTTP HEAD + timeout |
| **QoD 재평가** | ≤ 100ms/건 | QoD 수식 연산 |
| **갱신 큐 enqueue** | ≤ 10ms/건 | Redis LPUSH |

### 병목 요인 및 최적화
- **소스 가용성 확인**: 네트워크 I/O 병목 → 병렬 HTTP 요청 (max 20 concurrent)
- **full_scan**: 대규모 데이터 → 페이징 + 스트리밍 처리
- **QoD 재평가**: 일괄 처리 시 배치 연산 최적화

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 정상 신선도 검사 (도메인 규칙 적용)
```yaml
name: "freshness_check_with_domain_rules"
setup:
  - create_knowledge_item(id="ki-001", domain="news", created_at="48h ago", qod=0.8)
  - create_knowledge_item(id="ki-002", domain="legal", created_at="10d ago", qod=0.9)
  - create_knowledge_item(id="ki-003", domain="general", created_at="2h ago", qod=0.7)
input:
  knowledge_ids: ["ki-001", "ki-002", "ki-003"]
  freshness_policy:
    max_age_hours: 720
    domain_rules:
      - {domain: "news", max_age_hours: 24, refresh_strategy: "auto_recrawl", priority_boost: 3.0}
      - {domain: "legal", max_age_hours: 720, refresh_strategy: "manual_review", priority_boost: 2.0}
  scan_mode: "targeted"
  trigger_refresh: false
expected:
  - freshness_report[0].status == "expired"    # news: 48h > 24h
  - freshness_report[1].status == "fresh"       # legal: 240h < 720h * 0.5
  - freshness_report[2].status == "fresh"       # general: 2h < 720h * 0.5
  - stale_count == 1
  - fresh_count == 2
```

### 시나리오 2: QoD 하락에 의한 만료 처리
```yaml
name: "qod_drop_triggers_expiry"
setup:
  - create_knowledge_item(id="ki-qod-001", memory_layer="L2", qod=0.75)
  - mock_qod_evaluator(return_score=0.35)  # 재평가 시 0.35
input:
  knowledge_ids: ["ki-qod-001"]
  freshness_policy:
    max_age_hours: 720
    qod_recheck: true
  scan_mode: "targeted"
expected:
  - freshness_report[0].status == "expired"
  - freshness_report[0].refresh_priority == "critical"
  - freshness_report[0].qod_current < 0.4
  - stale_count == 1
```

### 시나리오 3: 자동 갱신 트리거
```yaml
name: "auto_refresh_trigger"
setup:
  - create_knowledge_item(id="ki-refresh-001", domain="finance", created_at="3h ago",
                          source_url="https://api.example.com/prices")
input:
  knowledge_ids: ["ki-refresh-001"]
  freshness_policy:
    max_age_hours: 720
    domain_rules:
      - {domain: "finance", max_age_hours: 1, refresh_strategy: "auto_recrawl", priority_boost: 5.0}
    check_source_availability: true
  scan_mode: "targeted"
  trigger_refresh: true
expected:
  - freshness_report[0].status == "expired"   # 3h > 1h
  - freshness_report[0].refresh_triggered == true
  - refresh_triggered_count == 1
```

### 시나리오 4: 에러 — 항목 미존재
```yaml
name: "error_no_items_found"
input:
  knowledge_ids: ["nonexistent-001", "nonexistent-002"]
  scan_mode: "targeted"
expected:
  - error.failure_code == "COND_019_NO_ITEMS_FOUND"
  - error.fallback_id == "F-019-01"
```

---

## E8. Blue Node Integration

> §B.6.2 CAT-B 연동 프로토콜 (P0-2 산출물) 반영
> LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.2)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Content Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy |
| **우선순위** | MEDIUM |

### 호출 패턴
```
Scheduler → 주기적 신선도 스캔 트리거 (크론)
  → ORANGE CORE (내부 이벤트: freshness_scan_due)
    → I-5 라우팅 → Content Node
      → Content Node: COND-019.execute(scan_mode="full_scan", trigger_refresh=True)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (자동 스캔 정책 충족)
          → COND-019 실행 → KnowledgeFreshnessResponse 반환
            → Content Node (만료 알림 생성)
              → ORANGE CORE → User (만료 항목 알림)

User → "내 지식베이스에서 오래된 정보가 있어?"
  → ORANGE CORE (I-1 Intent 해석: knowledge_freshness_check)
    → I-5 라우팅 → Content Node
      → Content Node: COND-019.execute(scan_mode="full_scan")
        → COND-019 실행 → KnowledgeFreshnessResponse 반환
          → Content Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.b.019.initialized` | initialize() 완료 |
| 신선도 검사 시작 | `cond.b.019.execute_start` | execute() 진입 |
| 신선도 검사 완료 | `cond.b.019.execute_done` | 정상 반환 |
| 신선도 검사 실패 | `cond.b.019.execute_fail` | VamosError 발생 |
| 갱신 트리거 발행 | `cond.b.019.refresh_triggered` | 만료 항목 갱신 큐 등록 |
| 헬스체크 | `cond.b.019.health` | health_check() 호출 |
| 모듈 종료 | `cond.b.019.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-019", "execution_ms": N, "scanned_count": M, "stale_count": K, "refresh_triggered": J }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond019KnowledgeFreshness(BaseModule):
    """COND-019 지식 신선도 관리"""

    async def initialize(self) -> Result[None, VamosError]:
        """KnowledgeStore 연결, QoD 평가기 초기화, 갱신 큐 연결, 스케줄러 등록"""
        self._knowledge_store = await KnowledgeStore.connect(self.config.store_url)
        self._qod_evaluator = QoDEvaluator()
        self._refresh_queue = await RefreshQueue.connect(self.config.redis_url)
        self._source_checker = SourceChecker(
            timeout_ms=self.config.source_check_timeout_ms,
            max_concurrent=self.config.source_check_concurrency
        )
        self._domain_classifier = DomainClassifier()
        self._emit_event("cond.b.019.initialized")
        return Ok(None)

    async def execute(self, request: KnowledgeFreshnessRequest) -> Result[KnowledgeFreshnessResponse, VamosError]:
        """Runnable.run() 위임 — 지식 신선도 검사 수행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """KnowledgeStore + Redis 갱신 큐 + QoD 평가기 상태 확인"""
        store_ok = await self._knowledge_store.ping()
        queue_ok = await self._refresh_queue.ping()
        qod_ok = self._qod_evaluator.is_ready()
        healthy = store_ok and queue_ok and qod_ok
        return Ok(HealthStatus(
            healthy=healthy,
            latency_ms=elapsed,
            details={
                "knowledge_store": store_ok,
                "refresh_queue": queue_ok,
                "qod_evaluator": qod_ok
            }
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """갱신 큐 연결 해제, 스케줄러 정지, 리소스 정리"""
        await self._refresh_queue.disconnect()
        await self._knowledge_store.disconnect()
        self._emit_event("cond.b.019.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-019", version="1.0.0",
            capabilities=[
                "freshness_check", "domain_rule_evaluation",
                "source_availability_check", "qod_recheck",
                "auto_refresh_trigger", "freshness_scheduling"
            ]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond019Config(ModuleConfig):
    """COND-019 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 5
    timeout_ms: int = 60000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=1000)

    # COND-019 전용 설정
    store_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/2"
    default_max_age_hours: int = 720           # 30일
    source_check_timeout_ms: int = 2000
    source_check_concurrency: int = 20
    full_scan_max_items: int = 50000
    full_scan_page_size: int = 500
    scheduled_scan_cron: str = "0 */6 * * *"   # 6시간마다
    qod_minimum_threshold: float = 0.4         # D2.0-06 §2.5.2
    aging_ratio: float = 0.5                    # age/max_age 비율 기준: < 0.5 = fresh
    stale_ratio: float = 0.8                    # < 0.8 = aging, < 1.0 = stale, >= 1.0 = expired
    refresh_queue_max_size: int = 10000
    enable_source_check: bool = True
    enable_qod_recheck: bool = True
```
