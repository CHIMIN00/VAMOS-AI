# COND-035 (E-024): 사용자 세션 관리 운영 — L3 상세 명세

> **모듈 ID**: COND-035
> **E-번호**: E-024
> **카테고리**: CAT-C (Ops/Infra) — E-series 운영
> **이름**: 사용자 세션 관리 운영
> **우선순위**: HIGH
> **Phase**: Phase 3
> **L3 수준**: L3 (구현 즉시 투입 가능)
> **LOCK 준수**: BaseModule ABC (D2.0-02 §7), Runnable 프로토콜 (D2.0-02 §1.2-A), ErrorHandlingStandard (D2.0-02 §0.3)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class SessionConfig(BaseModel):
    """세션 설정"""
    max_idle_seconds: int = Field(default=1800, description="유휴 세션 타임아웃 (초)")
    max_session_seconds: int = Field(default=86400, description="최대 세션 수명 (초)")
    max_concurrent_sessions: int = Field(default=5, description="사용자당 최대 동시 세션")
    session_store: Literal["redis", "memory", "database"] = Field(
        default="redis", description="세션 저장소 유형"
    )

class SessionRequest(BaseModel):
    """COND-035 입력 스키마"""
    operation: Literal[
        "create", "get", "refresh", "invalidate",
        "list_active", "cleanup_expired", "get_stats"
    ] = Field(description="세션 연산 유형")
    session_id: Optional[str] = Field(
        default=None, description="세션 ID (get/refresh/invalidate 시 필수)"
    )
    user_id: Optional[str] = Field(
        default=None, description="사용자 ID (create/list_active 시 필수)"
    )
    session_data: Optional[dict] = Field(
        default=None, description="세션에 저장할 데이터 (create/refresh 시)"
    )
    session_config: SessionConfig = Field(
        default_factory=SessionConfig, description="세션 설정"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "create",
                "user_id": "user-12345",
                "session_data": {
                    "device": "desktop",
                    "ip": "192.168.1.100",
                    "user_agent": "VAMOS/2.0"
                },
                "session_config": {
                    "max_idle_seconds": 1800,
                    "max_concurrent_sessions": 5,
                    "session_store": "redis"
                }
            }
        }
```

---

## E2. Output Schema

```python
class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    is_active: bool
    device: Optional[str] = None
    ip_address: Optional[str] = None
    data: Optional[dict] = None

class SessionStats(BaseModel):
    total_active: int
    total_expired_cleaned: int
    avg_session_duration_seconds: float
    peak_concurrent: int
    store_memory_bytes: int

class SessionResponse(BaseModel):
    """COND-035 출력 스키마"""
    session: Optional[SessionInfo] = Field(
        default=None, description="세션 정보 (create/get/refresh)"
    )
    active_sessions: Optional[list[SessionInfo]] = Field(
        default=None, description="활성 세션 목록 (list_active)"
    )
    invalidated: Optional[bool] = Field(
        default=None, description="무효화 성공 여부 (invalidate)"
    )
    cleaned_count: Optional[int] = Field(
        default=None, description="정리된 만료 세션 수 (cleanup_expired)"
    )
    stats: Optional[SessionStats] = Field(
        default=None, description="세션 통계 (get_stats)"
    )
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "session": {
                    "session_id": "sess_abc123def456",
                    "user_id": "user-12345",
                    "created_at": "2026-03-22T10:00:00Z",
                    "last_accessed": "2026-03-22T10:15:00Z",
                    "expires_at": "2026-03-22T10:30:00Z",
                    "is_active": True,
                    "device": "desktop"
                },
                "execution_time_ms": 5
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: SessionRequest) -> SessionResponse:
    store = SessionStore.connect(request.session_config.session_store)
    now = datetime.utcnow()

    MATCH request.operation:

        CASE "create":
            # 동시 세션 제한 확인
            active = store.get_active_sessions(request.user_id)
            IF len(active) >= request.session_config.max_concurrent_sessions:
                # 가장 오래된 세션 무효화 (LRU)
                oldest = min(active, key=lambda s: s.last_accessed)
                store.invalidate(oldest.session_id)
                LOG("COND.C.035.SESSION_EVICTED", session_id=oldest.session_id)

            session_id = generate_secure_session_id()  # crypto-random, 256-bit
            now = datetime.utcnow()
            session = SessionInfo(
                session_id=session_id,
                user_id=request.user_id,
                created_at=now,
                last_accessed=now,
                expires_at=now + timedelta(seconds=request.session_config.max_idle_seconds),
                is_active=True,
                data=request.session_data
            )
            store.save(session)
            LOG("COND.C.035.SESSION_CREATED", session_id=session_id, user_id=request.user_id)
            RETURN SessionResponse(session=session)

        CASE "get":
            session = store.get(request.session_id)
            IF session IS None OR NOT session.is_active:
                RETURN Error(COND_035_SESSION_NOT_FOUND)
            IF session.expires_at < now:
                store.invalidate(session.session_id)
                RETURN Error(COND_035_SESSION_EXPIRED)
            RETURN SessionResponse(session=session)

        CASE "refresh":
            session = store.get(request.session_id)
            IF session IS None:
                RETURN Error(COND_035_SESSION_NOT_FOUND)
            session.last_accessed = now
            session.expires_at = now + timedelta(seconds=request.session_config.max_idle_seconds)
            # 최대 수명 초과 체크
            IF session.expires_at > session.created_at + timedelta(seconds=request.session_config.max_session_seconds):
                session.expires_at = session.created_at + timedelta(seconds=request.session_config.max_session_seconds)
            IF request.session_data:
                session.data.update(request.session_data)
            store.save(session)
            RETURN SessionResponse(session=session)

        CASE "invalidate":
            success = store.invalidate(request.session_id)
            LOG("COND.C.035.SESSION_INVALIDATED", session_id=request.session_id)
            RETURN SessionResponse(invalidated=success)

        CASE "list_active":
            sessions = store.get_active_sessions(request.user_id)
            RETURN SessionResponse(active_sessions=sessions)

        CASE "cleanup_expired":
            count = store.cleanup_expired()
            LOG("COND.C.035.CLEANUP", cleaned=count)
            RETURN SessionResponse(cleaned_count=count)

        CASE "get_stats":
            stats = store.compute_stats()
            RETURN SessionResponse(stats=stats)
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_035_SESSION_NOT_FOUND` | 세션 ID에 해당하는 세션이 없음 | `F-035-01` | "세션을 찾을 수 없습니다." |
| `COND_035_SESSION_EXPIRED` | 세션이 만료됨 | `F-035-02` | "세션이 만료되었습니다. 다시 로그인해 주세요." |
| `COND_035_STORE_UNAVAILABLE` | 세션 저장소 연결 실패 (Redis 다운 등) | `F-035-03` | "세션 서비스에 일시적 문제가 있습니다." |
| `COND_035_USER_ID_REQUIRED` | create/list_active에 user_id 누락 | `F-035-04` | "사용자 ID가 필요합니다." |
| `COND_035_SESSION_ID_REQUIRED` | get/refresh/invalidate에 session_id 누락 | `F-035-05` | "세션 ID가 필요합니다." |
| `COND_035_CONCURRENT_LIMIT` | 동시 세션 제한 초과 (eviction 실패 시) | `F-035-06` | "동시 세션 수 제한을 초과했습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_035_SESSION_NOT_FOUND",
    message="Session not found: {session_id}",
    fallback_id="F-035-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

### 내부 의존 모듈
| 의존 모듈 | 의존 내용 | 필수/선택 |
|-----------|----------|----------|
| COND-036 (인증/토큰 관리) | 인증된 사용자 컨텍스트 | 필수 (소비) |
| COND-038 (로그 수집) | 세션 이벤트 로깅 | 필수 (제공) |
| COND-055 (감사 로그) | 세션 생성/무효화 감사 기록 | 선택 (제공) |
| COND-041 (헬스체크) | 세션 저장소 헬스체크 | 선택 (소비) |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `redis` (aioredis) | ≥5.0 | Redis 세션 저장소 |
| `cryptography` | ≥41.0 | 세션 ID 생성 (CSPRNG) |
| `msgpack` | ≥1.0 | 세션 데이터 직렬화 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| Redis (Primary) | 세션 저장소 |
| Redis Sentinel/Cluster | HA 구성 |

---

## E6. Performance Benchmark

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **세션 생성** | ≤ 5ms | Redis SET + EXPIRE |
| **세션 조회** | ≤ 2ms | Redis GET |
| **세션 갱신** | ≤ 3ms | Redis SET |
| **세션 무효화** | ≤ 2ms | Redis DEL |
| **만료 정리 (1000건)** | ≤ 500ms | SCAN + DEL pipeline |
| **동시 세션 조회** | ≤ 10ms | Redis SMEMBERS + MGET |
| **동시 처리 용량** | 10,000 ops/sec | Redis benchmark |
| **메모리 (세션 1개)** | ≤ 2KB | msgpack 직렬화 |

---

## E7. Integration Test Spec

### 시나리오 1: 세션 생성 → 조회 → 갱신 → 무효화
```yaml
name: "session_lifecycle"
setup:
  - ensure_redis_available()
input_sequence:
  - {operation: "create", user_id: "test-user-1", session_data: {device: "web"}}
  - {operation: "get", session_id: "$prev.session.session_id"}
  - {operation: "refresh", session_id: "$prev.session.session_id"}
  - {operation: "invalidate", session_id: "$prev.session.session_id"}
  - {operation: "get", session_id: "$prev.session.session_id"}
expected:
  - step[0]: session.is_active == true
  - step[1]: session.user_id == "test-user-1"
  - step[2]: session.last_accessed > step[1].session.last_accessed
  - step[3]: invalidated == true
  - step[4]: error.failure_code == "COND_035_SESSION_NOT_FOUND"
```

### 시나리오 2: 동시 세션 제한 (LRU eviction)
```yaml
name: "concurrent_session_limit"
setup:
  - session_config: {max_concurrent_sessions: 2}
input_sequence:
  - {operation: "create", user_id: "user-a", session_data: {device: "desktop"}}
  - {operation: "create", user_id: "user-a", session_data: {device: "mobile"}}
  - {operation: "create", user_id: "user-a", session_data: {device: "tablet"}}
  - {operation: "list_active", user_id: "user-a"}
expected:
  - step[3]: len(active_sessions) == 2
  - step[3]: "desktop" not in [s.data.device for s in active_sessions]  # oldest evicted
```

### 시나리오 3: 만료 세션 정리
```yaml
name: "cleanup_expired_sessions"
setup:
  - create_session(user_id="user-x", expires_in=-60)  # already expired
  - create_session(user_id="user-y", expires_in=-120)
  - create_session(user_id="user-z", expires_in=3600)  # still active
input:
  operation: "cleanup_expired"
expected:
  - cleaned_count == 2
```

---

## E8. Blue Node Integration

### 호출 패턴
```
User 로그인
  → ORANGE CORE (인증 완료 후)
    → COND-035.execute(operation="create", user_id="user-123", ...)
      → 세션 생성 → session_id 발급
        → 이후 모든 Blue Node 요청에 session_id 첨부

Blue Node 요청 시
  → ORANGE CORE
    → COND-035.execute(operation="get", session_id="sess_...")
      → 세션 유효성 확인
        → 유효 → Blue Node 실행 허용
        → 만료 → 재인증 요구
```

### Permission Level
- **P0 (시스템 레벨)**: 인프라 모듈, 모든 Blue Node에서 자동 호출
- **내부 전용**: 사용자가 직접 호출하지 않음 (ORANGE CORE가 내부적으로 사용)

### 이벤트 매핑

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 세션 생성 | `COND.C.035.SESSION_CREATED` | 신규 세션 생성 |
| 세션 갱신 | `COND.C.035.SESSION_REFRESHED` | 세션 만료 시간 연장 |
| 세션 무효화 | `COND.C.035.SESSION_INVALIDATED` | 로그아웃 또는 강제 종료 |
| 세션 만료 | `COND.C.035.SESSION_EXPIRED` | 유휴 타임아웃 초과 |
| 세션 퇴출 | `COND.C.035.SESSION_EVICTED` | 동시 세션 제한 초과 |
| 정리 완료 | `COND.C.035.CLEANUP` | 만료 세션 일괄 정리 |

---

## E9. Configuration

> LOCK (종합명세 §공통): ModuleConfig 표준 필드

```python
class Cond035Config(ModuleConfig):
    """COND-035 모듈 설정"""
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 100
    timeout_ms: int = 5000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=3, backoff_ms=100)

    # COND-035 전용 설정
    session_store: Literal["redis", "memory", "database"] = "redis"
    redis_url: str = "redis://localhost:6379/0"
    redis_key_prefix: str = "vamos:session:"
    default_idle_timeout_seconds: int = 1800
    default_max_session_seconds: int = 86400
    default_max_concurrent_sessions: int = 5
    session_id_length: int = 32
    cleanup_interval_seconds: int = 300
    enable_session_encryption: bool = True
    serializer: Literal["msgpack", "json"] = "msgpack"
```
