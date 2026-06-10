# COND-055: 감사 로그 운영 — L2 골격 명세

> **모듈 ID**: COND-055
> **E-번호**: E-049 (D2.0-03 Blue Node External 운영 모듈 매핑)
> **카테고리**: CAT-C (Ops/Infra) — E-Series 운영
> **이름**: 감사 로그 운영
> **우선순위**: HIGH
> **Phase**: Phase 1 — §7 작업 1-2 (CAT-C E-series 39개 모듈 골격)
> **L 수준**: L2 골격 — §13.1 8개 항목 중 6개(Input/Output/Algorithm/Error/Dependency/BlueNode) 완성, 2개(Performance/IntegrationTest) 골격
> **LOCK 준수**: LOCK-CD-03 (BaseModule ABC), LOCK-CD-04 (Runnable), LOCK-CD-05 (Result+VamosError, 예외 throw 금지), LOCK-CD-06 (failure_code/message/fallback_id/trace_id 4필드), LOCK-CD-08 (NODE 독립 실행 불가), LOCK-CD-10 (ModuleConfig 5필드)
> **이슈 진척**: I-03 (VamosError 매핑 + FailureCode 등록 — §E4), I-04 (기본 SLA 목표·측정 항목 — §E6)
> **출처**: 종합명세 #55 E-049 감사 로그 운영
> **설명**: 시스템 감사 로그. append-only(변조 방지), 검색/필터링, 규정 준수 보고서, 보관 정책.

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

# 종합명세 #55 기재 I/O (L2 골격 — L3에서 정밀 Pydantic 모델로 확장)
# 원본 입력 시그니처: audit_operation: Literal['write','query','report'], audit_entry: Optional[AuditEntry], query_filter: Optional[AuditFilter]
# 참조 타입(Forward declaration, L3 보강 예정): AuditEntry, AuditFilter

class AuditLogRequest(BaseModel):
    """COND-055 감사 로그 운영 입력 스키마 (L2 골격)

    L3 보강 시: 위의 forward 타입(AuditEntry, AuditFilter)을 Pydantic v2 모델로 정밀화하여
    operation/payload 일반 envelope 대신 typed union 사용 권장.
    """
    operation: Literal["write", "query", "report"] = Field(
        ..., description="요청 연산 (capabilities 중 하나)"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description=f"연산별 파라미터 — L3에서 AuditEntry, AuditFilter 정밀 타입으로 교체"
    )
    trace_id: Optional[str] = Field(default=None, description="분산 추적 ID (I-9 LogEvent 8필드 정합)")

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "write",
                "payload": {},
                "trace_id": "trace-055-001"
            }
        }
```

> **L3 보강 시 확장 항목**: 종합명세 #55 정의 타입(`audit_operation: Literal['write','query','report'], audit_entry: Optional[AuditEntry], query_filter: Optional[AuditFilter]`)을 Pydantic v2 모델로 정밀화. capabilities 3종 각각에 대한 typed payload 모델 정의.

---

## E2. Output Schema

```python
# 종합명세 #55 출력 시그니처: audit_records: list[AuditRecord], compliance_report: Optional[ComplianceReport]
# 참조 타입(Forward declaration, L3 보강 예정): AuditRecord, ComplianceReport

class AuditLogResponse(BaseModel):
    """COND-055 감사 로그 운영 출력 스키마 (L2 골격)

    L3 보강 시: result/metrics dict envelope 대신
    AuditRecord, ComplianceReport 정밀 모델로 교체.
    """
    status: Literal["ok", "degraded", "error"] = Field(description="실행 결과 상태")
    result: dict[str, Any] = Field(
        default_factory=dict,
        description=f"연산 결과 — L3에서 AuditRecord, ComplianceReport 정밀 타입으로 교체"
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict, description="실행 메트릭 (latency_ms, items_processed 등)"
    )
    execution_time_ms: int = Field(ge=0, description="총 실행 시간 (밀리초)")
    trace_id: Optional[str] = Field(default=None, description="분산 추적 ID 에코")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "result": {},
                "metrics": {"items_processed": 1},
                "execution_time_ms": 12,
                "trace_id": "trace-055-001"
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: AuditLogRequest) -> Result[AuditLogResponse, VamosError]:
    # 1. 입력 검증 (LOCK-CD-05: 예외 throw 금지, Result로 반환)
    IF request.operation NOT IN ["write", "query", "report"]:
        RETURN Err(VamosError(
            failure_code="COND_055_INVALID_OPERATION",
            message=f"unsupported operation: {request.operation}",
            fallback_id="FB_COND_REJECT",
            trace_id=request.trace_id,
        ))

    # 2. 백엔드 인프라 헬스 확인 (의존 인프라 미가용 시 fast-fail)
    IF NOT _backend.is_ready():
        RETURN Err(VamosError(
            failure_code="COND_055_BACKEND_UNAVAILABLE",
            message="COND-055 backend not ready",
            fallback_id="FB_COND_SKIP",
            trace_id=request.trace_id,
        ))

    # 3. 동시 처리 한도 검사 (max_concurrent — LOCK-CD-10)
    IF _semaphore.in_flight() >= config.max_concurrent:
        RETURN Err(VamosError(
            failure_code="COND_055_QUOTA_EXCEEDED",
            message="max_concurrent exceeded",
            fallback_id="FB_COND_REJECT",
            trace_id=request.trace_id,
        ))

    # 4. 연산 디스패치 (LOCK-CD-04 Runnable.run에 위임)
    _emit_event("cond.c.055.execute_start", trace_id=request.trace_id)
    SWITCH request.operation:
        CASE "write": result = _handle_write(request.payload)
        CASE "query": result = _handle_query(request.payload)
        CASE "report": result = _handle_report(request.payload)
        DEFAULT: UNREACHABLE  # step 1에서 차단됨

    # 5. 타임아웃 검사 (LOCK-CD-10 timeout_ms)
    IF elapsed_ms() > config.timeout_ms:
        RETURN Err(VamosError(
            failure_code="COND_055_EXECUTE_TIMEOUT",
            message=f"timeout after {config.timeout_ms}ms",
            fallback_id="FB_COND_SKIP",
            trace_id=request.trace_id,
        ))

    # 6. 메트릭 기록 + LogEvent 발행 (lower.dot, §B.4 / §B.4.1 8필드)
    _emit_event("cond.c.055.execute_done", trace_id=request.trace_id)

    # 7. 응답 구성
    RETURN Ok(AuditLogResponse(
        status="ok",
        result=result,
        metrics={"items_processed": 1},
        execution_time_ms=elapsed_ms(),
        trace_id=request.trace_id,
    ))
```

> **L3 보강 시**: 각 capability별 세부 절차(상태 머신, 락, 트랜잭션 경계, 외부 호출 sequence)를 종합명세 #55 기준으로 상세화.

---

## E4. Error Handling

> LOCK-CD-05: `Result<T, VamosError>`, 예외 throw 금지
> LOCK-CD-06: `failure_code`, `message`, `fallback_id`, `trace_id` 4필드 필수
> I-03 해결: 본 표가 39개 E-series 모듈 전수 VamosError 매핑 + FailureCode 등록 프레임의 일부

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|---------------|
| `COND_055_INVALID_OPERATION` | 미지원 operation 요청 | `FB_COND_REJECT` | "지원하지 않는 연산입니다." |
| `COND_055_BACKEND_UNAVAILABLE` | 백엔드 인프라 미가용 (감사 쓰기는 무음 스킵 금지) | `FB_COND_REJECT` | "감사 로그 백엔드가 일시적으로 사용 불가합니다. 요청을 거부합니다." |
| `COND_055_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "처리 시간이 초과되었습니다." |
| `COND_055_QUOTA_EXCEEDED` | max_concurrent 초과 | `FB_COND_REJECT` | "동시 처리 한도를 초과했습니다." |
| `COND_055_DEPENDENCY_FAIL` | 하위 의존 모듈/서비스 실패 | `FB_COND_SKIP` | "의존 서비스 호출에 실패했습니다." |

```python
return Err(VamosError(
    failure_code="COND_055_BACKEND_UNAVAILABLE",
    message="COND-055 backend not ready",
    fallback_id="FB_COND_SKIP",
    trace_id=ctx.trace_id,
))
```

> **FB_ID 네이밍 정합성**: §B.7.2 (Phase 0 P0-2 fix) 기준으로 일반 fallback_id 사용 (`FB_COND_REJECT`, `FB_COND_SKIP`) — 모듈명 누출 금지.
> **L3 보강 시**: capability별 세부 FailureCode(예: `COND_055_<CAP>_<REASON>`)와 root-cause-specific fallback_id를 추가.

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출): CAT-C는 인프라 최하위 계층 — 외부 CAT 소비 의존 0건
> **CAT-C 내부 의존**: §A.2 P0-1 매트릭스가 CAT-A/B 범위만 다루어 CAT-C 내부 의존은 미수록 — Phase 2 P2-1에서 P0-1 확장 예정
> **추적**: 본 모듈의 잠재적 CAT-C 내부 의존(예: COND-029 version_control, COND-030 distributed_tracing 등)은 `CONFLICT_LOG.md` 의존성매트릭스누락 항목으로 일괄 추적됨 (1-1 cond_079 사례와 동일 처리)

### COND 내부 의존 (잠정)
| 관계 | 모듈 | 비고 |
|------|------|------|
| 소비 (외부 CAT) | — | 없음 (CAT-C 인프라 계층, P0-1 §A.3 확인) |
| 소비 (CAT-C 내부) | (Phase 2 P2-1 확장 시 정식 등록) | R-04-7 직접 교차 호출 금지 준수 — 패턴 재사용만 허용 |
| 제공 | 모든 CAT (운영 기반) | Blue Node 전 도메인 공통 소비 |

### I-Series 소비 (공통 4종)
| I-Module | 용도 |
|----------|------|
| I-1 (Intent) | 호출 의도 해석 |
| I-5 (Decision) | 라우팅 결정 |
| I-6 (Self-check) | 자기 검증 |
| I-9 (Logging) | LogEvent 발행 (lower.dot, §B.4.1 8필드) |

### 외부 인프라/라이브러리 (L2 골격)
| 항목 | 용도 |
|------|------|
| 백엔드 인프라 (L3 보강 예정) | 시스템 감사 로그. append-only(변조 방지), 검색/필터링, 규정 준수 보고서, 보관 정책. |
| Prometheus | 메트릭 수집 (E6 SLA 측정) |
| OpenTelemetry | 분산 추적 (trace_id 전파) |

---

## E6. Performance Benchmark (I-04 기본 SLA — 골격)

> **상태**: L2 골격 (Phase 2에서 부하시험 데이터 기반 L3 보강)
> I-04 해결 프레임: 39개 E-series 모듈 전수 4종 기본 SLA 메트릭 골격 기재
> 모듈 특성 반영: p99=100ms, throughput=10000req/s

| 메트릭 | SLA 목표 | 임계값 (Alert) | 측정 방법 |
|--------|---------|----------------|-----------|
| **p99 응답시간** | ≤ 100 ms | > 400 ms | Prometheus histogram |
| **처리량** | ≥ 10000 req/s/instance | < 2500 req/s | 부하시험 (k6/wrk) |
| **가용성** | 99.9 % (월) | < 99.5 % | uptime probe |
| **에러율** | ≤ 0.1 % | > 1 % | error_total / request_total |

---

## E7. Integration Test Spec (골격)

> **상태**: L2 골격 (Phase 2에서 핵심 시나리오 L3 완성)
> I-05 진척: 본 모듈 기본 happy/unhappy path 3종 골격 기재

```yaml
- name: "audit_log_happy_path"
  description: "정상 연산 — write"
  input: { operation: "write", payload: {}, trace_id: "test-001" }
  expected:
    - status == "ok"
    - execution_time_ms < 400
    - trace_id == "test-001"

- name: "audit_log_invalid_operation"
  description: "미지원 operation은 INVALID_OPERATION + FB_COND_REJECT"
  input: { operation: "__unknown__", payload: {} }
  expected:
    - error.failure_code == "COND_055_INVALID_OPERATION"
    - error.fallback_id == "FB_COND_REJECT"

- name: "audit_log_backend_down"
  description: "백엔드 인프라 미가용 시 BACKEND_UNAVAILABLE + FB_COND_SKIP"
  setup: [stop_backend()]
  input: { operation: "write", payload: {} }
  expected:
    - error.failure_code == "COND_055_BACKEND_UNAVAILABLE"
    - error.fallback_id == "FB_COND_SKIP"
```

---

## E8. Blue Node Integration (§B.6.1 골격)

> §B.6.1 CAT-C 패턴 적용 — 운영 인프라는 모든 Blue Node에 공통 적용
> LOCK-CD-08: NODE는 CORE 규칙 상속, 독립 실행 불가
> §B.4 lower.dot event_type 정본 (D2.0-02 §6.1)

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (시스템 공통 운영 인프라) |
| **Permission Level** | P0 (시스템 레벨, 기본 활성) |
| **게이트 요구** | policy (운영 정책 검사), cost (리소스 한도) |
| **호출 패턴** | OpsInfraMixin.audit_log() — Runnable.run 위임 (LOCK-CD-04) |
| **E-번호 매핑** | E-049 (D2.0-03 Blue Node External §5) |
| **독립 실행 가능 여부** | ❌ 불가 (LOCK-CD-08) — Blue Node 컨텍스트에서만 호출 |

### 이벤트 매핑 (§B.4 lower.dot, §B.4.1 LogEvent 8필드)
| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.055.initialized` |
| 실행 시작 | `cond.c.055.execute_start` |
| 실행 완료 | `cond.c.055.execute_done` |
| 실행 실패 | `cond.c.055.execute_fail` |
| 헬스체크 | `cond.c.055.health` |
| 종료 | `cond.c.055.shutdown` |

### Decision 기록 (§B.8)
- `Decision.optional_signals ← {cond_module_id: "COND-055", e_number: "E-049", operation, status, execution_time_ms}`

---

## E9. BaseModule ABC 적합성 (LOCK-CD-03/04 골격)

```python
class Cond055AuditLog(BaseModule):
    """COND-055 BaseModule ABC 골격 (LOCK-CD-03 4-method + LOCK-CD-04 Runnable 위임)"""

    async def initialize(self) -> Result[None, VamosError]:
        self._backend = await self._connect_backend()
        self._emit_event("cond.c.055.initialized")
        return Ok(None)

    async def execute(self, request: AuditLogRequest) -> Result[AuditLogResponse, VamosError]:
        return await self.run(request)  # LOCK-CD-04 Runnable.run() 위임

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(
            healthy=self._backend.is_ready(),
            latency_ms=0,
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._backend.close()
        self._emit_event("cond.c.055.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-055",
            version="0.1.0",
            capabilities=["write", "query", "report"],
        )
```

---

## E10. Configuration (LOCK-CD-10 골격)

```python
class Cond055Config(ModuleConfig):
    """COND-055 모듈 설정 (LOCK-CD-10 5필드 + 모듈 전용)"""
    # LOCK-CD-10 표준 5필드
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 100
    timeout_ms: int = 400
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=200)

    # COND-055 전용 (L3 보강 예정)
    backend_endpoint: str = "internal://audit_log"
```
