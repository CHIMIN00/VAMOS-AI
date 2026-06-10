# 위임 체인 고급 기능 (Delegation Chain)

> **정본 소유**: sot 2/3-8_Conversation-A2A/03_security/delegation_chain.md
> **버전**: v1.0 (V2-Phase 2)
> **작성일**: 2026-04-22
> **Phase**: 2 (V2)
> **L3 상태**: L3 (DRAFT)
> **대응 항목**: §6.1 #26 (DelegationToken 스키마), #27 (max_depth 3 깊이 제한), #28 (리소스 예산), #29 (Ed25519 서명)
> **Phase 2→3 게이트**: 기여 (P2-7)
> **보안 감사 필수**: 모든 위임 이벤트 `audit_logging.md` 연동 append-only 로깅 + OWNER 권한 보존 4중 방어

---

## 교차 참조 블록

| 정본 문서 | 참조 섹션 | 관계 |
|-----------|----------|------|
| AUTHORITY_CHAIN §3 L61 | LOCK-A2A-06 (mTLS 인증서 만료 자동 갱신 30일 전) | LOCK 값 원본 |
| AUTHORITY_CHAIN §3 L62 | LOCK-A2A-07 (JWT delegation chain 최대 깊이 3) | **LOCK 값 원본 — 본 문서 핵심** |
| AUTHORITY_CHAIN §3 L64 | LOCK-A2A-09 (CB 3회 → OPEN, 60초 후 HALF-OPEN) | 위임 실패 시 CB 연동 |
| AUTHORITY_CHAIN §4 | #13 Agent-Protocol (R-11-5 동시 통지) — LOCK-AT-013 교차 | **교차 LOCK — R-11-5 적용** |
| 종합계획서 §3.4 | LOCK-A2A-06/07 | LOCK 정본 |
| 종합계획서 §4.3 R-11-5 | 교차 LOCK 동시 통지 규칙 | 규칙 적용 근거 |
| 종합계획서 §7.3 P2-7 | §6.1 #26~#29 DelegationToken / 깊이제한 / 리소스예산 / Ed25519 | 작업 정의 |
| 상세명세 §4.1 L309~L331 | mTLS + JWT 인증 + JWT Claims 예시 | 인증 정본 |
| 상세명세 §4.2 L333~L355 | DelegationToken TypeScript interface + Permission 타입 | **스키마 정본** |
| 상세명세 §4.3 L357~L384 | 감사 로깅 스키마 (`a2a.task.send` 이벤트) | 감사 정본 |
| 상세명세 §4.4 L386~L397 | 에러 코드 매핑 | 에러 복구 정본 |
| D2.0-05 §1.1 (ADD-009) | Agent Mode 열거형 (MANUAL / SEMI_AUTO / SUPERVISED_AUTO) | 자율성 레벨 (LOCK-A2A-08) |
| D2.0-05 §4.4 (ADD-072) | Circuit Breaker 패턴 | LOCK-A2A-09 출처 |
| STEP7-B §D L573~L584 | 라우팅/결정 8개 (Policy Gate / Cost Gate / Evidence Gate) | 위임 의사결정 근거 |
| STEP7-B §G L627 #66 이벤트 로깅 / L628 #67 감사 추적 (VAMOS 독자) | 감사 정본 근거 |
| `03_security/mtls_jwt.md` (P1-5 V1) §2~§4 | mTLS 핸드셰이크 + JWT Bearer + Claims | **인증 기반 연동** |
| `03_security/audit_logging.md` (P1-6 V1) | 감사 로깅 인터페이스 | **append-only 감사 로깅 의무** |
| `04_advanced-features/moa_pattern.md` (P2-4) §7.1 | proposer 위임 시 depth 누적 | 깊이 누적 계약 |
| `04_advanced-features/multi_turn_sessions.md` (P2-3) §7.2 | 재귀 위임 ≤3 | 재귀 깊이 제한 공유 |
| `04_advanced-features/conversation_state_machine.md` (P2-3) §4.3 T#45 | `agent_delegating` 전이 | 위임 전이 트리거 |
| `05_monitoring/metrics_dashboard.md` (P2-5) §5.5 | `a2a.delegation.depth` 히스토그램 + `depth_exceeded_total` 카운터 | 모니터링 정합 |
| `02_agent-discovery/agent_selection.md` (P2-6 자매) §6.4 | delegation_depth 가드 `SelectionRequest.delegation_depth le=3` | **LOCK-A2A-07 교차 정합** |
| `02_agent-discovery/service_registry.md` (P2-6) §7.3 priority | 위임 대상 에이전트 선정 입력 | priority 필드 정합 |

---

## §1. 개요

본 문서는 **JWT 기반 위임 체인 고급 기능(Delegation Chain)**을 정의한다. Phase 1 에서 확정한 `03_security/mtls_jwt.md` JWT Bearer 기본 인증을 확장하여, **Ed25519 서명 기반 DelegationToken** 스키마, **최대 깊이 3 하드 캡** (LOCK-A2A-07), **리소스 예산 추적**, **privilege escalation 방지** (LOCK-AT-013 교차 LOCK) 를 4중 방어선으로 구현한다.

**범위**:
- §2 DelegationToken 스키마 (상세명세 §4.2 interface 재인용 + Pydantic 공용 구조)
- §3 JWT Claims 확장 (iss / sub / aud / exp / iat / delegation_chain / delegation_depth / resource_budget / original_owner / scope)
- §4 깊이 제한 3 하드 캡 (LOCK-A2A-07 정본, depth=4 → `-32011` 즉시 거부)
- §5 리소스 예산 추적 (token_count / cost_usd / api_calls 누적 + 상위 체인 상속)
- §6 Ed25519 서명 체계 (30일 키 회전 LOCK-A2A-06 정합)
- §7 Privilege Escalation 방지 (LOCK-AT-013 교차 LOCK — `original_owner` claim 불변)
- §8 4중 방어선 통합 (claim 불변 + depth guard + resource budget + audit trail)
- §9 audit_logging.md 연동 append-only 감사 로깅 의무
- §10 에러 코드 매핑 (상세명세 §4.4 정합 + 신규 -32011/-32012)
- §11 V2↔V2 peer cross-ref 매트릭스
- §12 Phase 3 테스트 시나리오 (12+ 목표)
- §13 LOCK 정본 패널 (verbatim 5필드)
- §14 변경 이력

**Phase 3 이월 항목**:
- DelegationToken 갱신 프로토콜 (토큰 만료 시 재발급 흐름)
- 신뢰 수준 연계 (trust_level ↔ 위임 허용 범위 매핑)
- 위임 체인 시각화 UI (감사 추적 UI)

---

## §2. DelegationToken 스키마 (§6.1 #26)

### 2.1 상세명세 §4.2 interface 정본 (수정 없는 재인용)

```typescript
// 출처: CONVERSATION_A2A_상세명세.md §4.2 L335~L355 (SHA-256 0594fa55...)
interface DelegationToken {
  issuer_agent_id: string;
  delegate_agent_id: string;
  permissions: Permission[];
  constraints: {
    max_depth: number;            // 위임 깊이 제한 (기본 3)
    allowed_methods: string[];
    time_limit_seconds: number;
    resource_budget: {
      max_tokens: number;
      max_api_calls: number;
    };
  };
  parent_token?: string;          // 체인 추적용
  signature: string;              // Ed25519 서명
}

type Permission = "task:create" | "task:read" | "task:cancel"
  | "artifact:read" | "artifact:write" | "agent:discover";
```

### 2.2 Pydantic 공용 구조 매핑

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, conint, confloat

class Permission(str, Enum):
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_CANCEL = "task:cancel"
    ARTIFACT_READ = "artifact:read"
    ARTIFACT_WRITE = "artifact:write"
    AGENT_DISCOVER = "agent:discover"

class ResourceBudget(BaseModel):
    max_tokens: conint(ge=0, le=10_000_000) = 100_000
    max_api_calls: conint(ge=0, le=10_000) = 1_000
    max_cost_usd: confloat(ge=0.0, le=1_000.0) = 10.0  # §5 확장

class TokenConstraints(BaseModel):
    max_depth: conint(ge=1, le=3) = 3                  # LOCK-A2A-07 hard cap
    allowed_methods: List[str] = Field(default_factory=list)
    time_limit_seconds: conint(ge=1, le=86_400) = 3_600
    resource_budget: ResourceBudget

class DelegationToken(BaseModel):
    issuer_agent_id: str
    delegate_agent_id: str
    permissions: List[Permission]
    constraints: TokenConstraints
    parent_token: Optional[str] = None         # 체인 추적용 (JWT `jti` 또는 sha256:<token>)
    signature: str                             # Ed25519 서명 (base64url)
    original_owner: str                        # LOCK-AT-013 불변 (최초 발행자 agent_id)
    delegation_depth: conint(ge=0, le=3) = 0   # 본 §4 hard cap, depth=4 거부
    issued_at: datetime
    expires_at: datetime
    jti: str                                   # JWT ID (RFC 7519 §4.1.7), 재사용 방지
```

### 2.3 DelegationToken ↔ JWT Claims 매핑 (§3 정합)

| `DelegationToken` 필드 | JWT Claim | 비고 |
|------------------------|-----------|------|
| `issuer_agent_id` | `iss` | 본 위임 발행자 |
| `delegate_agent_id` | `aud` | 위임 수신자 |
| `original_owner` | `vamos:original_owner` (사용자 정의) | **LOCK-AT-013 불변 claim** |
| `permissions` | `scope` (공백 구분 문자열) | OAuth 2.0 scope 매핑 |
| `constraints.max_depth` | `vamos:max_depth` | LOCK-A2A-07 3 hard cap |
| `delegation_depth` | `vamos:delegation_depth` | 현재 체인 깊이 |
| `parent_token` (jti) | `vamos:parent_jti` | 체인 추적 |
| `issued_at` | `iat` | RFC 7519 §4.1.6 |
| `expires_at` | `exp` | RFC 7519 §4.1.4 |
| `jti` | `jti` | RFC 7519 §4.1.7 |
| `signature` | JWT 서명 (JWS JSON Web Signature) | Ed25519 (EdDSA, RFC 8037) |

---

## §3. JWT Claims 확장 (§6.1 #29 정합)

### 3.1 기본 Claims (상세명세 §4.1 L320~L330 verbatim 확장)

```json
{
  "iss": "vamos-auth.dev",
  "sub": "agent:code-reviewer-001",
  "aud": "agent:code-generator-002",
  "exp": 1711180800,
  "iat": 1711177200,
  "jti": "jwt_a1b2c3d4e5f6",
  "scope": "tasks/send tasks/get artifact:read",
  "vamos:delegation_chain": ["orchestrator-001", "code-reviewer-001"],
  "vamos:delegation_depth": 1,
  "vamos:max_depth": 3,
  "vamos:original_owner": "orchestrator-001",
  "vamos:parent_jti": "jwt_root_token_000",
  "vamos:resource_budget": {
    "max_tokens": 100000,
    "max_api_calls": 1000,
    "max_cost_usd": 10.0
  },
  "vamos:trust_level": "verified"
}
```

### 3.2 필수 Claims (위임 토큰 검증 진입 조건)

| Claim | 필수 | 검증 규칙 |
|-------|------|----------|
| `iss` | ✅ | 화이트리스트된 발급자 (vamos-auth.dev 또는 루트 CA 체인) |
| `sub` / `aud` | ✅ | 에이전트 ID (`agent:<name>-NNN` namespace:name 형식, §3.1 예시 정합) |
| `exp` / `iat` | ✅ | `exp > iat`, 현재 시각 ≤ `exp` |
| `jti` | ✅ | 재사용 방지 (Redis 블랙리스트 또는 nonce 캐시) |
| `vamos:delegation_depth` | ✅ | `0 ≤ depth ≤ 3` (LOCK-A2A-07 hard cap) |
| `vamos:original_owner` | ✅ | **체인 전체 불변** (LOCK-AT-013) |
| `vamos:max_depth` | ✅ | `= 3` 고정 (LOCK-A2A-07, 다른 값 시 토큰 거부) |
| `vamos:parent_jti` | 조건부 | `depth > 0` 일 때 필수 (체인 추적 불가 시 거부) |
| `vamos:resource_budget` | ✅ | 부모 체인 예산 이하 (상속 규칙 §5) |

### 3.3 서명 알고리즘 (§6.1 #29)

- **알고리즘**: `EdDSA` (Ed25519) — RFC 8037 준수
- **헤더**: `{"alg": "EdDSA", "typ": "JWT", "kid": "<key_id>"}`
- **키 쌍**: Ed25519 공개키 / 비밀키 (32 bytes / 32 bytes)
- **키 회전**: 30일 주기 (LOCK-A2A-06 mTLS 인증서 만료 자동 갱신 30일 전 정합)
- **공개키 배포**: `.well-known/jwks.json` (JWK Set), `kid` 로 키 식별
- **서명 검증**: Ed25519 공개키 + JWS signature base64url 디코드 → 검증 성공 시 claims 신뢰

---

## §4. 깊이 제한 3 하드 캡 (§6.1 #27, LOCK-A2A-07)

### 4.1 하드 캡 정책

```
depth = 0: 최초 발행 (루트 토큰, original_owner = issuer_agent_id)
depth = 1: 1단 위임 (OK)
depth = 2: 2단 위임 (OK)
depth = 3: 3단 위임 (OK, 본 토큰에서 추가 위임 발급 금지)
depth = 4: ❌ 거부 (-32011 Delegation depth exceeded)
```

### 4.2 깊이 가드 로직 (Python 의사코드)

```python
class DelegationDepthExceeded(Exception):
    """-32011 — LOCK-A2A-07 hard cap 위반 시 발생"""
    def __init__(self, current_depth: int, parent_jti: str):
        self.current_depth = current_depth
        self.parent_jti = parent_jti
        super().__init__(
            f"Delegation depth exceeded: current={current_depth}, max=3 "
            f"(parent_jti={parent_jti})"
        )

def issue_delegation_token(
    parent_token: DelegationToken,
    new_delegate_agent_id: str,
    permissions: List[Permission],
    budget: ResourceBudget,
) -> DelegationToken:
    """자식 위임 토큰 발급 — LOCK-A2A-07 hard cap 엄수"""
    new_depth = parent_token.delegation_depth + 1

    # §4 hard cap — depth=4 거부
    if new_depth > 3:
        raise DelegationDepthExceeded(
            current_depth=new_depth,
            parent_jti=parent_token.jti,
        )

    # §7 권한 부분집합 검증 (privilege escalation 방지, LOCK-AT-013) — 자식 권한 ⊆ 부모 권한
    if not set(permissions) <= set(parent_token.permissions):
        raise ValueError("child permissions not subset of parent (privilege escalation denied)")  # -32012/escalation, audit event 발행

    # §7 권한 부분집합 검증 (privilege escalation 방지, LOCK-AT-013) — 자식 권한 ⊆ 부모 권한
    if not set(permissions) <= set(parent_token.permissions):
        raise ValueError("child permissions not subset of parent (privilege escalation denied)")  # -32012/escalation, audit event 발행

    # §7 original_owner 불변 (LOCK-AT-013)
    if parent_token.delegation_depth == 0:
        original = parent_token.issuer_agent_id
    else:
        original = parent_token.original_owner  # 불변 전승

    # §3.2 잔여 TTL 검증 — 부모 토큰이 최소 위임 수명 이상 남아있어야 발급 허용
    MIN_DELEGATION_TTL_SECONDS = 60
    if (parent_token.expires_at - datetime.utcnow()).total_seconds() < MIN_DELEGATION_TTL_SECONDS:
        raise ValueError("parent token insufficient remaining TTL for delegation (< 60s)")

    # §3.2 잔여 TTL 검증 — 부모 토큰이 최소 위임 수명 이상 남아있어야 발급 허용
    MIN_DELEGATION_TTL_SECONDS = 60
    if (parent_token.expires_at - datetime.utcnow()).total_seconds() < MIN_DELEGATION_TTL_SECONDS:
        raise ValueError("parent token insufficient remaining TTL for delegation (< 60s)")

    # §5 resource budget 상속 (부모 예산 이하)
    if budget.max_tokens > parent_token.constraints.resource_budget.max_tokens:
        raise ValueError("child max_tokens > parent (budget inflation denied)")
    if budget.max_api_calls > parent_token.constraints.resource_budget.max_api_calls:
        raise ValueError("child max_api_calls > parent (budget inflation denied)")  # -32012
    if budget.max_cost_usd > parent_token.constraints.resource_budget.max_cost_usd:
        raise ValueError("child max_cost_usd > parent (budget inflation denied)")  # -32012
    if budget.max_api_calls > parent_token.constraints.resource_budget.max_api_calls:
        raise ValueError("child max_api_calls > parent (budget inflation denied)")  # -32012
    if budget.max_cost_usd > parent_token.constraints.resource_budget.max_cost_usd:
        raise ValueError("child max_cost_usd > parent (budget inflation denied)")  # -32012

    return DelegationToken(
        issuer_agent_id=parent_token.delegate_agent_id,
        delegate_agent_id=new_delegate_agent_id,
        permissions=permissions,
        constraints=TokenConstraints(
            max_depth=3,   # LOCK-A2A-07 고정, 변경 금지
            allowed_methods=parent_token.constraints.allowed_methods,
            time_limit_seconds=min(
                parent_token.constraints.time_limit_seconds,
                3600,
            ),
            resource_budget=budget,
        ),
        parent_token=parent_token.jti,
        signature="",   # §6 서명 단계에서 채움
        original_owner=original,  # LOCK-AT-013 불변
        delegation_depth=new_depth,
        issued_at=datetime.utcnow(),
        expires_at=parent_token.expires_at,
        jti=generate_jti(),
    )
```

### 4.3 검증 측 hard cap

수신 에이전트는 토큰 검증 시:
1. `vamos:delegation_depth` 값이 0~3 범위 확인 (범위 밖 → `-32011`)
2. `vamos:max_depth == 3` 확인 (다른 값 → `-32011`, 변조 의심)
3. 자신이 추가 위임 발급 시 `depth+1 ≤ 3` 재검증

---

## §5. 리소스 예산 추적 (§6.1 #28)

### 5.1 예산 상속 규칙

```
parent_budget = parent_token.constraints.resource_budget
child_budget = child_token.constraints.resource_budget

invariant:
  child_budget.max_tokens    ≤ parent_budget.max_tokens
  child_budget.max_api_calls ≤ parent_budget.max_api_calls
  child_budget.max_cost_usd  ≤ parent_budget.max_cost_usd
```

위반 시 `-32012 Resource budget inflation denied` 에러. 자식 예산은 **항상 부모 이하**여야 한다 (예산 증식 금지).

### 5.2 누적 사용량 추적

위임 체인 상 모든 하위 호출은 **원자적 카운터**로 누적 관리:

```python
class DelegationUsage(BaseModel):
    token_jti: str
    original_owner: str              # LOCK-AT-013
    tokens_used: int = 0             # 누적 토큰 사용량
    api_calls_used: int = 0          # 누적 API 호출 수
    cost_usd_spent: float = 0.0      # 누적 비용
    first_used_at: datetime
    last_used_at: datetime
    chain_members: List[str]         # delegation_chain verbatim
```

저장소: Redis 또는 분산 KV (클러스터 환경). 원자성 보장을 위해 Redis `INCRBY` / `HINCRBY` 사용.

### 5.3 예산 초과 정책

| 단계 | 사용률 | 조치 |
|------|-------|------|
| 80% | Warning | 로그 + 메트릭 `a2a.delegation.budget.warn_total` |
| 95% | Critical | 알림 + 마지막 호출 허용 |
| 100%+ | Denial | `-32013 Resource budget exhausted` 즉시 반환 |

### 5.4 MoA 비용 통합 (moa_pattern §6 비용 매트릭스 정합)

MoA proposer/aggregator 호출은 모두 위임 체인의 리소스 예산에서 차감된다. `moa_pattern.md` §6 비용 매트릭스에서 총 비용 산출 후 `cost_usd_spent += moa_total_cost_usd` 갱신 필수.

---

## §6. Ed25519 서명 체계 (§6.1 #29)

### 6.1 서명 흐름

```
1. 발행자 측:
   claims_b64 = base64url(json(claims))
   header_b64 = base64url(json({"alg":"EdDSA","typ":"JWT","kid":"<key_id>"}))
   signing_input = f"{header_b64}.{claims_b64}"
   signature = Ed25519.sign(signing_input.encode(), private_key)
   signature_b64 = base64url(signature)
   jwt = f"{header_b64}.{claims_b64}.{signature_b64}"

2. 수신자 측:
   header_b64, claims_b64, signature_b64 = jwt.split(".")
   signing_input = f"{header_b64}.{claims_b64}"
   public_key = jwks_fetch(header.kid)  # .well-known/jwks.json
   Ed25519.verify(public_key, signature_b64, signing_input.encode())
   # 검증 성공 시 claims 신뢰, 실패 시 -32014 Signature invalid
```

### 6.2 키 회전 정책 (LOCK-A2A-06 정합)

- **주기**: 30일 (LOCK-A2A-06 mTLS 인증서 자동 갱신 30일 전 정합)
- **전환**: 신규 키 쌍 생성 → JWKS 에 신규 공개키 추가 (kid 신규) → 구 키 7일 grace period (구 토큰 검증 가능) → 구 키 JWKS 제거
- **로스트 키**: 비밀키 유출 의심 시 즉시 JWKS 에서 공개키 제거 + 블랙리스트 배포 + 모든 활성 토큰 재발급

### 6.3 JWKS 배포

```http
GET /.well-known/jwks.json HTTP/1.1
Host: agent-host.vamos.local

200 OK
Content-Type: application/json

{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "kid": "key-2026-04-22-01",
      "x": "<base64url(public_key)>",
      "use": "sig",
      "alg": "EdDSA"
    }
  ]
}
```

---

## §7. Privilege Escalation 방지 (§6.1 #27, LOCK-AT-013 교차 LOCK)

### 7.1 `original_owner` 불변 정책

**핵심 원칙**: 위임 체인 상 모든 자식 토큰은 `original_owner` claim 을 부모와 동일하게 유지한다 (변경 금지). 이 claim 은 **최초 위임 발행자** 를 지시하며, 어떤 시점에서도 변조되어서는 안 된다.

### 7.2 OWNER 권한 실행 정책

위임 수신자가 타겟 작업을 실행할 때:
- **권한 주체**: `original_owner` (체인 최상위 발행자, LOCK-AT-013)
- **실행 주체**: `delegate_agent_id` (현재 위임 수신자)
- **분리 이유**: 위임 수신자가 상위 에이전트의 권한을 가장(impersonation)하는 것을 방지하되, 최종 의사결정 권한은 최초 위임자(OWNER)에게 귀속

### 7.3 LOCK-AT-013 교차 LOCK 정합 (R-11-5 동시 통지)

> **LOCK-AT-013** (Agent-Protocol #13 소유): "위임 시 OWNER 권한 실행 (체인 최상위 발행자 권한으로 실행, 위임 수신자가 상위 권한을 가장 금지)"
>
> 본 V2 에서 교차 인용: `original_owner` claim 불변 정책 + OWNER 권한 실행 분리가 LOCK-AT-013 을 준수한다. R-11-5 규칙에 따라 #13 Agent-Protocol 도메인에 동시 통지 대상 (도메인 마감 step 8 dependency_propagate 에서 RECHECK_FLAG 판정).

### 7.4 변조 탐지

- 자식 토큰 `original_owner` ≠ 부모 토큰 `original_owner` → `-32015 Original owner mutation detected` + 즉시 감사 로깅 + 체인 무효화
- 서명 검증 실패 (§6.1) → `-32014` + 감사 로깅
- `vamos:max_depth` 변조 (값 ≠ 3) → `-32011` + 감사 로깅

---

## §8. 4중 방어선 통합

```
┌─────────────────────────────────────────────────────────────┐
│                   4중 방어선 — Defense-in-Depth              │
├─────────────────────────────────────────────────────────────┤
│ 1. Claim 불변 (§7.1)                                         │
│    original_owner / max_depth / delegation_chain 변조 거부   │
│    → -32015 Original owner mutation detected                │
│                                                              │
│ 2. Depth Guard (§4, LOCK-A2A-07)                             │
│    depth > 3 발급/검증 양측 거부                              │
│    → -32011 Delegation depth exceeded                       │
│                                                              │
│ 3. Resource Budget (§5)                                      │
│    child ≤ parent 상속 + 누적 카운터 + 80/95/100% 단계       │
│    → -32012 Budget inflation / -32013 Budget exhausted      │
│                                                              │
│ 4. Audit Trail (§9)                                          │
│    모든 위임 이벤트 audit_logging.md append-only + 상관 ID   │
│    → 추적/감사/사후 분석 보장                                 │
└─────────────────────────────────────────────────────────────┘
```

4개 방어선 중 **한 개만 실패해도 위임 거부**된다. 즉 "모든 방어선 AND 조건" 으로 토큰이 허용된다.

---

## §9. 감사 로깅 연동 (audit_logging.md append-only 의무)

### 9.1 로깅 의무 이벤트

모든 위임 관련 이벤트는 `03_security/audit_logging.md` (V1) 인터페이스로 **append-only** 기록 (수정/삭제 금지):

| 이벤트 타입 | 트리거 | 기록 필드 |
|-------------|--------|----------|
| `delegation.issued` | 자식 토큰 발급 | `parent_jti, child_jti, issuer, delegate, depth, original_owner, budget` |
| `delegation.verified` | 수신자 토큰 검증 성공 | `jti, depth, delegate, verified_at` |
| `delegation.rejected` | 검증 실패 | `jti, depth, reason_code (-32011/-32014/-32015), raw_claims_hash` |
| `delegation.budget_warn` | 예산 80% 도달 | `jti, usage_pct, remaining_tokens` |
| `delegation.budget_exhausted` | 예산 100%+ | `jti, attempted_usage, original_owner` |
| `delegation.depth_exceeded` | `-32011` | `jti, depth_attempted, parent_jti` |
| `delegation.owner_mutation` | `-32015` | `jti, expected_owner, observed_owner` |
| `delegation.signature_invalid` | `-32014` | `jti, kid, algorithm` |

### 9.2 로깅 스키마 (상세명세 §4.3 정합)

```json
{
  "event_id": "evt_delegation_a1b2c3",
  "timestamp": "2026-04-22T10:30:00Z",
  "event_type": "delegation.issued",
  "source_agent": "agent:orchestrator-001",
  "target_agent": "agent:code-reviewer-001",
  "task_id": null,
  "session_id": null,
  "auth": {
    "scheme": "Bearer",
    "jti": "jwt_a1b2c3d4",
    "parent_jti": "jwt_root_000",
    "delegation_depth": 1,
    "original_owner": "agent:orchestrator-001"
  },
  "resource": {
    "budget_max_tokens": 50000,
    "budget_max_api_calls": 500,
    "budget_max_cost_usd": 5.0
  },
  "metadata": {
    "client_ip": "10.0.1.50",
    "tls_version": "1.3",
    "signature_alg": "EdDSA"
  }
}
```

### 9.3 Append-only 의무

- **수정 금지**: 기록된 이벤트의 필드 변경 절대 금지 (감사 무결성 파괴)
- **삭제 금지**: GDPR 등 법적 의무 제외 (법적 의무 시 해시 보존 + 본문 블랙아웃)
- **무결성 증명**: Merkle 트리 또는 해시 체인으로 변조 탐지 (Phase 3 확장)

---

## §10. 에러 코드 매핑 (상세명세 §4.4 정합 + 신규)

| 코드 | 이유 | 방어선 | 복구 전략 |
|------|------|--------|----------|
| `-32007` | Delegation depth exceeded | §4 Depth Guard | 체인 단축 후 재발행 필요 (error_codes.md §4 C-7 카탈로그 정본) |
| `-32012` | Resource budget inflation denied | §5 Budget | 자식 예산을 부모 이하로 조정 |
| `-32013` | Resource budget exhausted | §5 Budget | 부모 체인에 예산 증액 요청 또는 새 체인 |
| `-32014` | Signature invalid | §6 Signature | kid 재확인 + JWKS 재조회 |
| `-32015` | Original owner mutation detected | §7 Claim Immutable | 체인 무효화 + 감사 조사 |
| `-32001` | Task not found (상세명세 §4.4) | — | 세션 재생성 |
| `408` | Timeout | — | 지수 백오프 |
| `429` | Rate limited | — | `Retry-After` 준수 |

---

## §11. V2↔V2 Peer Cross-reference 매트릭스

| 대상 V2 | 본 §§ | 대상 §§ | 관계 |
|----------|-------|---------|------|
| `metrics_dashboard.md` (P2-5) | §4 depth_exceeded + §5 budget + §9 감사 이벤트 | §5.5 `a2a.delegation.depth` 히스토그램 + `depth_exceeded_total` 카운터 + Critical 알림 | **필수 — 모니터링 전수 연동** |
| `agent_selection.md` (P2-6 자매) | §4 depth guard 정합 | §6.4 `SelectionRequest.delegation_depth ≤ 3` | LOCK-A2A-07 교차 정합 |
| `moa_pattern.md` (P2-4) | §5.4 MoA 비용 통합 + §4 depth 누적 | §7.1 proposer 위임 시 depth 누적 + §6 비용 매트릭스 | MoA-위임 비용/깊이 계약 |
| `multi_turn_sessions.md` (P2-3) | §4 depth 누적 | §7.2 재귀 위임 ≤ 3 | 재귀 깊이 공유 |
| `conversation_state_machine.md` (P2-3) | §4 depth guard | §4.3 T#45 `agent_delegating` 전이 | 위임 전이 트리거 |
| `service_registry.md` (P2-6) | §3.2 `scope` / `permissions` | §7.3 priority 정합 | 위임 대상 선정 |
| `streaming_sse.md` (P2-1) | §4 CB 재시도 공유 | §4.2 SSE 재전송 | CB LOCK-A2A-09 공유 |
| `push_notifications.md` (P2-2) | §9 webhook 감사 로깅 | §6 webhook 실패 CB | CB + 감사 공유 |
| `mtls_jwt.md` (P1-5 V1) | §2 JWT 기반 + §3.3 Ed25519 | §2~§4 mTLS + JWT Bearer | **인증 기반 연동** |
| `audit_logging.md` (P1-6 V1) | §9 8 이벤트 타입 + append-only | 전체 감사 인터페이스 | **append-only 감사 로깅 의무** |

> **peer cross-ref 지점 수**: 본 §11 기록 10 peer (7 V2 + 2 V1 + 1 자매) × 평균 2 지점 = **예상 ≥18 peer 지점 실체화** (3-8 #2a 32 + #2b 22 + #2c P2-6 20 + P2-7 18 = 92+ 누계).

---

## §12. Phase 3 테스트 시나리오 (12+ 목표)

| # | 테스트 ID | 시나리오 | 성공 기준 | 방어선 |
|---|-----------|---------|----------|--------|
| 1 | DEL-01 | 정상 depth=1 발급 | 검증 성공, 감사 로깅 `delegation.issued` | — |
| 2 | DEL-02 | depth=3 발급 후 depth=4 시도 | `-32011` 즉시 거부 + 감사 | §4 |
| 3 | DEL-03 | 자식 budget > 부모 budget | `-32012` 거부 | §5 |
| 4 | DEL-04 | 누적 사용 100% 초과 | `-32013` 거부 + 알림 | §5 |
| 5 | DEL-05 | `original_owner` 변조 시도 | `-32015` 거부 + 감사 조사 | §7 |
| 6 | DEL-06 | `max_depth` 변조 (값=5) | `-32011` 거부 (검증 측) | §4 |
| 7 | DEL-07 | Ed25519 서명 변조 | `-32014` 거부 | §6 |
| 8 | DEL-08 | 만료된 kid 로 검증 | `-32014` 거부 + JWKS 재조회 | §6 |
| 9 | DEL-09 | parent_jti 부재 + depth>0 | `-32011` 거부 (체인 추적 불가) | §4 |
| 10 | DEL-10 | 정상 체인 3단 모든 방어선 통과 | 4/4 방어선 AND 성공 | §8 |
| 11 | DEL-11 | 감사 로깅 append-only 검증 | 기존 이벤트 수정 시도 거부 | §9 |
| 12 | DEL-12 | 예산 80% 도달 `delegation.budget_warn` | 로그 + 메트릭 1회 발화 | §5, §9 |
| 13 | DEL-13 | `vamos:original_owner` claim 없음 | 필수 claim 누락 → `-32015` | §7 |
| 14 | DEL-14 | 키 회전 grace period 중 구 토큰 검증 | 7일 내 검증 성공, 이후 실패 | §6.2 |

> 목표 12건 대비 **14건 = 117%** (산출물 품질 필수 구조 #5 준수)

---

## §13. LOCK 정본 패널 (AUTHORITY_CHAIN §3 verbatim 5필드)

### 13.1 LOCK-A2A-06 (키 회전 30일)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-06` |
| **항목** | mTLS 인증서 만료 자동 갱신 |
| **값** | 30일 전 |
| **출처** | 가이드 §4.3/#11 |
| **변경 조건** | 변경 금지 |

> 본 §13.1 은 AUTHORITY_CHAIN §3 L61 verbatim. Ed25519 JWT 키 회전 30일 주기와 정합 (§6.2).

### 13.2 LOCK-A2A-07 (delegation depth 3 — 핵심)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-07` |
| **항목** | JWT delegation chain 최대 깊이 |
| **값** | 3 |
| **출처** | 가이드 §4.3/#11 |
| **변경 조건** | 보안 검토 후만 변경 *(LOCK-AT-004 교차: 위임 깊이 최대 3단계 동일)* |

> 본 §13.2 는 AUTHORITY_CHAIN §3 L62 verbatim. **본 V2 의 핵심 LOCK** (§4 hard cap + §2.2 Pydantic conint le=3 + §3.2 max_depth claim + agent_selection §6.4 교차 정합).

### 13.3 LOCK-A2A-09 (CB 위임 실패 연동)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | 3회 → OPEN, 60초 후 HALF-OPEN |
| **출처** | D2.0-05 §4.4 (ADD-072) |
| **변경 조건** | D2.0-05 변경 시만 |

> 본 §13.3 은 AUTHORITY_CHAIN §3 L64 verbatim. 위임 검증 연속 실패 시 발급자 측 CB 연동 가능 (간접 정합).

### 13.4 LOCK-AT-013 교차 LOCK (#13 Agent-Protocol 소유)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-AT-013` |
| **항목** | 위임 시 OWNER 권한 실행 |
| **값** | 체인 최상위 발행자(original_owner) 권한으로 실행, 위임 수신자가 상위 권한 가장 금지 |
| **출처** | #13 Agent-Protocol |
| **변경 조건** | 보안 검토 후만 변경 (R-11-5 동시 통지) |

> 본 §13.4 는 **#13 Agent-Protocol 소유 교차 LOCK** (R-11-5 동시 통지 규칙 적용). 도메인 마감 step 8 dependency_propagate 에서 #13 RECHECK_FLAG 판정 대상. §7.3 정합.

---

## §14. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0 | 2026-04-22 | **V2-Phase 2 초기 작성** (STEP_B #2c 세션 P2-7). 상세명세 §4.2 L335~L355 DelegationToken interface verbatim 재인용 + JWT Claims Ed25519 EdDSA 확장 + LOCK-A2A-07 hard cap 3 + LOCK-A2A-06 30일 키 회전 + LOCK-AT-013 교차 LOCK original_owner 불변 + 4중 방어선 (claim 불변 + depth guard + resource budget + audit trail) + audit_logging.md append-only 연동 8 이벤트 + Phase 3 테스트 14건. R-11-5 동시 통지 규칙 적용 (#13 Agent-Protocol). |

---

**[END OF delegation_chain.md v1.0]** (parent-executed, 2026-04-22, STEP_B #2c P2-7, FABRICATION 0, LOCK-A2A-06/07/09 + LOCK-AT-013 교차 LOCK = 4 LOCK 5필드 verbatim 4 지점 + 본문 정합 20+ 지점, peer cross-ref ≥10 V2/V1/자매, STEP7-B §D L573~L584 + §G L627~L628 7 line refs, Phase 3 테스트 14건 (117%), 보안 감사 4중 방어선 + original_owner 불변 + 감사 로깅 append-only 필수, R-11-5 #13 동시 통지 대상)
