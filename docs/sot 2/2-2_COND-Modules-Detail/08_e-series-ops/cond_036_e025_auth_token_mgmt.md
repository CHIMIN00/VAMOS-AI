# COND-036 (E-025): 인증/토큰 관리 운영 — L3 상세 명세

> **모듈 ID**: COND-036
> **E-번호**: E-025
> **카테고리**: CAT-C (Ops/Infra) — E-series 운영
> **이름**: 인증/토큰 관리 운영
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

class TokenConfig(BaseModel):
    """토큰 설정"""
    access_token_ttl_seconds: int = Field(default=900, description="액세스 토큰 유효시간 (초)")
    refresh_token_ttl_seconds: int = Field(default=604800, description="리프레시 토큰 유효시간 (초, 기본 7일)")
    token_algorithm: Literal["HS256", "RS256", "ES256"] = Field(
        default="RS256", description="JWT 서명 알고리즘"
    )
    max_refresh_count: int = Field(default=30, description="리프레시 토큰 최대 갱신 횟수")
    issuer: str = Field(default="vamos-auth", description="토큰 발행자")

class AuthTokenRequest(BaseModel):
    """COND-036 입력 스키마"""
    operation: Literal[
        "issue", "validate", "refresh", "revoke",
        "revoke_all", "introspect", "list_active"
    ] = Field(description="토큰 연산 유형")
    user_id: Optional[str] = Field(
        default=None, description="사용자 ID (issue/revoke_all/list_active 시 필수)"
    )
    access_token: Optional[str] = Field(
        default=None, description="액세스 토큰 (validate/introspect 시 필수)"
    )
    refresh_token: Optional[str] = Field(
        default=None, description="리프레시 토큰 (refresh/revoke 시 필수)"
    )
    claims: Optional[dict] = Field(
        default=None, description="JWT 커스텀 클레임 (issue 시)"
    )
    token_config: TokenConfig = Field(
        default_factory=TokenConfig, description="토큰 설정"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "issue",
                "user_id": "user-12345",
                "claims": {"role": "investor", "tier": "pro"},
                "token_config": {
                    "access_token_ttl_seconds": 900,
                    "refresh_token_ttl_seconds": 604800,
                    "token_algorithm": "RS256"
                }
            }
        }
```

---

## E2. Output Schema

```python
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    token_type: str = "Bearer"

class TokenIntrospection(BaseModel):
    active: bool
    user_id: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    claims: Optional[dict] = None
    refresh_count: int = 0

class AuthTokenResponse(BaseModel):
    """COND-036 출력 스키마"""
    token_pair: Optional[TokenPair] = Field(
        default=None, description="토큰 쌍 (issue/refresh)"
    )
    valid: Optional[bool] = Field(
        default=None, description="토큰 유효 여부 (validate)"
    )
    introspection: Optional[TokenIntrospection] = Field(
        default=None, description="토큰 상세 정보 (introspect)"
    )
    revoked: Optional[bool] = Field(
        default=None, description="폐기 성공 여부 (revoke/revoke_all)"
    )
    active_tokens: Optional[list[TokenIntrospection]] = Field(
        default=None, description="활성 토큰 목록 (list_active)"
    )
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "token_pair": {
                    "access_token": "eyJhbGciOiJSUzI1NiJ9...",
                    "refresh_token": "rt_abc123def456...",
                    "access_expires_at": "2026-03-22T10:15:00Z",
                    "refresh_expires_at": "2026-03-29T10:00:00Z",
                    "token_type": "Bearer"
                },
                "execution_time_ms": 8
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: AuthTokenRequest) -> AuthTokenResponse:
    key_store = KeyStore.load(request.token_config.token_algorithm)
    token_store = TokenStore.connect()  # Redis blacklist/metadata

    MATCH request.operation:

        CASE "issue":
            VALIDATE request.user_id IS NOT None

            # JWT 클레임 구성
            now = datetime.utcnow()
            access_claims = {
                "sub": request.user_id,
                "iss": request.token_config.issuer,
                "iat": now,
                "exp": now + timedelta(seconds=request.token_config.access_token_ttl_seconds),
                "jti": generate_uuid_v7(),
                **(request.claims or {})
            }
            access_token = jwt.encode(access_claims, key_store.private_key, algorithm=request.token_config.token_algorithm)

            # 리프레시 토큰 (opaque, DB 저장)
            refresh_token = generate_secure_token(64)  # crypto-random
            refresh_expires = now + timedelta(seconds=request.token_config.refresh_token_ttl_seconds)
            token_store.save_refresh(refresh_token, request.user_id, refresh_expires, refresh_count=0, access_jti=access_claims["jti"])

            LOG("COND.C.036.TOKEN_ISSUED", user_id=request.user_id)
            RETURN AuthTokenResponse(token_pair=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                access_expires_at=access_claims["exp"],
                refresh_expires_at=refresh_expires
            ))

        CASE "validate":
            TRY:
                claims = jwt.decode(request.access_token, key_store.public_key, algorithms=[request.token_config.token_algorithm])
                # 블랙리스트 체크
                IF token_store.is_blacklisted(claims["jti"]):
                    RETURN AuthTokenResponse(valid=False)
                RETURN AuthTokenResponse(valid=True)
            CATCH ExpiredSignatureError:
                RETURN AuthTokenResponse(valid=False)
            CATCH InvalidTokenError:
                RETURN AuthTokenResponse(valid=False)

        CASE "refresh":
            meta = token_store.get_refresh(request.refresh_token)
            IF meta IS None:
                RETURN Error(COND_036_REFRESH_TOKEN_NOT_FOUND)
            IF meta.expires_at < now:
                token_store.delete_refresh(request.refresh_token)
                RETURN Error(COND_036_REFRESH_TOKEN_EXPIRED)
            IF meta.refresh_count >= request.token_config.max_refresh_count:
                token_store.delete_refresh(request.refresh_token)
                RETURN Error(COND_036_REFRESH_LIMIT_EXCEEDED)

            # 기존 리프레시 토큰 폐기 + 새 토큰 쌍 발행 (rotation)
            token_store.delete_refresh(request.refresh_token)
            new_request = AuthTokenRequest(operation="issue", user_id=meta.user_id, claims=meta.claims, token_config=request.token_config)
            result = execute(new_request)
            # 갱신 횟수 기록
            token_store.update_refresh_count(result.token_pair.refresh_token, meta.refresh_count + 1)
            LOG("COND.C.036.TOKEN_REFRESHED", user_id=meta.user_id, count=meta.refresh_count + 1)
            RETURN result

        CASE "revoke":
            meta = token_store.get_refresh(request.refresh_token)
            IF meta IS NOT None:
                # 연관 액세스 토큰 블랙리스트 등록
                token_store.blacklist_access(meta.access_jti, ttl=request.token_config.access_token_ttl_seconds)
                token_store.delete_refresh(request.refresh_token)
            LOG("COND.C.036.TOKEN_REVOKED", refresh_token_prefix=request.refresh_token[:8])
            RETURN AuthTokenResponse(revoked=True)

        CASE "revoke_all":
            count = token_store.revoke_all_for_user(request.user_id)
            LOG("COND.C.036.ALL_TOKENS_REVOKED", user_id=request.user_id, count=count)
            RETURN AuthTokenResponse(revoked=True)

        CASE "introspect":
            TRY:
                claims = jwt.decode(request.access_token, key_store.public_key, algorithms=[request.token_config.token_algorithm], options={"verify_exp": False})
                is_active = claims["exp"] > now AND NOT token_store.is_blacklisted(claims["jti"])
                RETURN AuthTokenResponse(introspection=TokenIntrospection(
                    active=is_active, user_id=claims["sub"],
                    issued_at=claims["iat"], expires_at=claims["exp"],
                    claims={k:v for k,v in claims.items() if k not in ("sub","iss","iat","exp","jti")}
                ))
            CATCH InvalidTokenError:
                RETURN AuthTokenResponse(introspection=TokenIntrospection(active=False))

        CASE "list_active":
            tokens = token_store.list_active_for_user(request.user_id)
            RETURN AuthTokenResponse(active_tokens=tokens)
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_036_REFRESH_TOKEN_NOT_FOUND` | 리프레시 토큰이 존재하지 않음 | `F-036-01` | "인증이 만료되었습니다. 다시 로그인해 주세요." |
| `COND_036_REFRESH_TOKEN_EXPIRED` | 리프레시 토큰 만료 | `F-036-02` | "인증이 만료되었습니다. 다시 로그인해 주세요." |
| `COND_036_REFRESH_LIMIT_EXCEEDED` | 리프레시 최대 횟수 초과 | `F-036-03` | "보안을 위해 재로그인이 필요합니다." |
| `COND_036_INVALID_TOKEN` | JWT 서명 검증 실패 | `F-036-04` | "유효하지 않은 인증 토큰입니다." |
| `COND_036_KEY_STORE_ERROR` | 서명 키 로드 실패 | `F-036-05` | "인증 서비스에 일시적 문제가 있습니다." |
| `COND_036_USER_ID_REQUIRED` | issue/revoke_all에 user_id 누락 | `F-036-06` | "사용자 ID가 필요합니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_036_REFRESH_TOKEN_EXPIRED",
    message="Refresh token expired: {token_prefix}",
    fallback_id="F-036-02",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

### 내부 의존 모듈
| 의존 모듈 | 의존 내용 | 필수/선택 |
|-----------|----------|----------|
| COND-035 (세션 관리) | 세션 생성 시 토큰 발행 트리거 | 필수 (소비) |
| COND-038 (로그 수집) | 토큰 발행/폐기 이벤트 로깅 | 필수 (제공) |
| COND-055 (감사 로그) | 인증 이벤트 감사 기록 | 필수 (제공) |
| COND-037 (API 게이트웨이) | 토큰 검증 요청 처리 | 필수 (제공) |
| COND-051 (시크릿 관리) | JWT 서명 키 보관 | 필수 (소비) |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `PyJWT` | ≥2.8 | JWT 생성/검증 |
| `cryptography` | ≥41.0 | RSA/ECDSA 키 관리 |
| `redis` (aioredis) | ≥5.0 | 토큰 블랙리스트 + 리프레시 저장소 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| Redis (Primary) | 리프레시 토큰 저장 + 블랙리스트 |
| Key Vault / 시크릿 관리 | JWT 서명 키 보관 |

---

## E6. Performance Benchmark

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **토큰 발행** | ≤ 15ms | JWT 서명 (RS256) + Redis SET |
| **토큰 검증** | ≤ 3ms | JWT 디코드 + 블랙리스트 체크 |
| **토큰 갱신** | ≤ 20ms | 폐기 + 재발행 |
| **토큰 폐기** | ≤ 5ms | Redis DEL + 블랙리스트 SET |
| **전체 폐기** | ≤ 50ms | SCAN + DEL pipeline |
| **토큰 조회 (introspect)** | ≤ 5ms | JWT 디코드 (exp 미검증) |
| **동시 처리 용량** | 5,000 ops/sec | JWT + Redis 병합 |
| **블랙리스트 메모리 (건당)** | ≤ 128B | jti + TTL |

---

## E7. Integration Test Spec

### 시나리오 1: 토큰 발행 → 검증 → 갱신 → 폐기
```yaml
name: "token_lifecycle"
setup:
  - ensure_redis_available()
  - ensure_key_store_loaded()
input_sequence:
  - {operation: "issue", user_id: "test-user-1", claims: {role: "investor"}}
  - {operation: "validate", access_token: "$prev.token_pair.access_token"}
  - {operation: "refresh", refresh_token: "$prev.token_pair.refresh_token"}
  - {operation: "revoke", refresh_token: "$prev.token_pair.refresh_token"}
  - {operation: "validate", access_token: "$step[0].token_pair.access_token"}
expected:
  - step[0]: token_pair.token_type == "Bearer"
  - step[1]: valid == true
  - step[2]: token_pair.access_token != step[0].token_pair.access_token  # rotated
  - step[3]: revoked == true
  - step[4]: valid == false  # blacklisted after revoke
```

### 시나리오 2: 리프레시 횟수 제한
```yaml
name: "refresh_limit"
setup:
  - token_config: {max_refresh_count: 2}
input_sequence:
  - {operation: "issue", user_id: "user-a"}
  - {operation: "refresh", refresh_token: "$prev.token_pair.refresh_token"}  # count=1
  - {operation: "refresh", refresh_token: "$prev.token_pair.refresh_token"}  # count=2
  - {operation: "refresh", refresh_token: "$prev.token_pair.refresh_token"}  # count=3 → fail
expected:
  - step[1]: token_pair IS NOT None
  - step[2]: token_pair IS NOT None
  - step[3]: error.failure_code == "COND_036_REFRESH_LIMIT_EXCEEDED"
```

### 시나리오 3: 전체 폐기
```yaml
name: "revoke_all"
input_sequence:
  - {operation: "issue", user_id: "user-b"}
  - {operation: "issue", user_id: "user-b"}
  - {operation: "revoke_all", user_id: "user-b"}
  - {operation: "list_active", user_id: "user-b"}
expected:
  - step[2]: revoked == true
  - step[3]: len(active_tokens) == 0
```

---

## E8. Blue Node Integration

### 호출 패턴
```
User 로그인 (COND-035 세션 생성 후)
  → ORANGE CORE
    → COND-036.execute(operation="issue", user_id="user-123", claims={role: "investor"})
      → access_token + refresh_token 발급
        → 클라이언트에 전달, 이후 모든 API 요청에 Bearer 토큰 첨부

API 요청 시
  → API Gateway (COND-037)
    → COND-036.execute(operation="validate", access_token="eyJ...")
      → 유효 → Blue Node 실행 허용
      → 만료 → 401 Unauthorized (클라이언트가 refresh 시도)
```

### Permission Level
- **P0 (시스템 레벨)**: 인프라 모듈, 모든 인증이 필요한 Blue Node에서 자동 호출
- **내부 전용**: 사용자가 직접 호출하지 않음 (API Gateway/ORANGE CORE가 내부적으로 사용)

### 이벤트 매핑

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 토큰 발행 | `COND.C.036.TOKEN_ISSUED` | 신규 토큰 쌍 발행 |
| 토큰 갱신 | `COND.C.036.TOKEN_REFRESHED` | 리프레시 토큰으로 갱신 |
| 토큰 폐기 | `COND.C.036.TOKEN_REVOKED` | 개별 토큰 폐기 |
| 전체 폐기 | `COND.C.036.ALL_TOKENS_REVOKED` | 사용자 전체 토큰 폐기 |
| 검증 실패 | `COND.C.036.VALIDATION_FAILED` | 유효하지 않은 토큰 사용 시도 |

---

## E9. Configuration

> LOCK (종합명세 §공통): ModuleConfig 표준 필드

```python
class Cond036Config(ModuleConfig):
    """COND-036 모듈 설정"""
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 200
    timeout_ms: int = 5000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=50)

    # COND-036 전용 설정
    token_algorithm: Literal["HS256", "RS256", "ES256"] = "RS256"
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 604800
    max_refresh_count: int = 30
    issuer: str = "vamos-auth"
    redis_url: str = "redis://localhost:6379/1"
    redis_key_prefix: str = "vamos:auth:"
    blacklist_key_prefix: str = "vamos:auth:blacklist:"
    key_rotation_interval_days: int = 90
    enable_token_encryption: bool = False
```
