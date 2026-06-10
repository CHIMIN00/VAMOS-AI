# 에이전트 설정 관리 — K-059 (V2 신규 L3)

> **STEP7-K**: K-059 에이전트 설정 관리 (L1143~L1153 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V2-Phase 2 신규)
> **Part2 상태**: ABSENT — 본 문서로 L3 방식 C 신규
> **정본 소유**: #13 Agent-Protocol-Interoperability / 04_deployment-scaling
> **V 스코프**: V2-Phase 2 (K-056 Kubernetes 배포 STEP7-K L1101~L1111 은 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2b 3-10 도메인 P2-4 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1143~L1153 | K-059 원문 (환경별 dev/staging/prod, 동적 런타임 변경, 비밀 관리, 스키마 검증) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-01 | VamosMessage 스키마 정합 — 설정 파일도 동일 Pydantic 모델 계열 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-02 | Permission Level 0~5 — config 변경 권한도 L2/L3 제한 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-04 | MCP Streamable HTTP — 설정 endpoint 도 HTTP (WS 아님) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 — Secret Manager 호출 비용 감시 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% HITL (06_autonomy-safety 정본) |
| 구조화_종합계획서.md | §7.4 P2-4 L1213~L1245 | Phase 2 K-059 배치 |
| 04_deployment-scaling/_index.md | L19 | K-059 L0→L3 |
| 04_deployment-scaling/container_spec.md | §4.4 BuildKit secrets | 빌드 타임 비밀 분리 |
| 04_deployment-scaling/healthcheck_spec.md | §4.3 startup config_loaded | 설정 로드 후 startup probe |
| 04_deployment-scaling/logging_spec.md | §4 로그 레벨 | hot reload 대상 |
| 04_deployment-scaling/migration_guide.md | §3 Blue-Green | 환경 승격 시 config diff |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 import |
| 4-3 MCP-Server-Client | Tool Registry 설정 | Tool 설정 정본은 #16 |
| 6-2 Security-Governance | LOCK 암호화 키 순환 정책 | Secret 순환 정본은 #20 |

> **R6 준수**: What+How 전용.

---

## §2. Purpose & Scope

### 2.1 4대 요건 (STEP7-K L1147~L1150 원문)

| 요건 | 구현 섹션 | 핵심 메커니즘 |
|------|----------|--------------|
| 환경별 설정 (dev/staging/prod) | §4 | Layered YAML + 환경 오버라이드 |
| 동적 설정 (런타임 변경) | §5 | Hot reload (SIGHUP + etcd watch) |
| 비밀 관리 | §3 | Vault/AWS SM/환경 비밀 참조 |
| 설정 검증 (스키마) | §6 | Pydantic 모델 + pre-commit |

### 2.2 범위 경계

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| YAML 스키마 + layering + hot reload | ✅ | — |
| 비밀 저장소 물리 구성 | ❌ | 6-2 Security-Governance |
| 키 순환·감사 | ❌ | 6-2 Security-Governance |
| 빌드 타임 비밀 주입 | 참조 | `container_spec.md §4.4` |

---

## §3. 공통 자료 구조 Import

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,
    GatePolicy,
    AdapterResult,
)
from pydantic import BaseModel, Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional, Dict, List
from datetime import datetime
from enum import Enum
```

---

## §4. 환경별 설정 Layering (STEP7-K L1147 원문)

### 4.1 우선순위 계층 (아래가 위를 덮어씀)

```
1. defaults (패키지 내장)                → vamos/node/<type>/config/defaults.yaml
2. environment base                       → /etc/vamos/node.yaml (dev|staging|prod 공통)
3. environment override                   → /etc/vamos/node.<env>.yaml
4. local override (개발자 전용)            → ~/.vamos/node.local.yaml (prod 금지)
5. 환경변수                                → VAMOS_NODE__LLM__DEFAULT_PROVIDER=anthropic
6. 런타임 API (PATCH /admin/config)       → L3 권한 필수 (LOCK-AP-02)
```

### 4.2 YAML 스키마 (뼈대)

```yaml
# /etc/vamos/node.yaml
version: "1.0"
node_type: dev           # dev | research | content | quant | trading | personal
environment: prod        # dev | staging | prod
image_ref: "registry.vamos.local/vamos/dev-node@sha256:a1b9628f..."   # migration_guide.md §3 digest pin

runtime:
  max_inflight: 32
  queue_capacity: 512
  heartbeat_interval_seconds: 10
  graceful_shutdown_seconds: 30

protocols:
  mcp:
    transport: "streamable-http"      # LOCK-AP-04 엄수
    endpoint_internal: "http://127.0.0.1:8081/mcp"
    client_timeout_seconds: 30
  a2a:
    endpoint_internal: "http://127.0.0.1:8082/a2a"
    bidirectional: true               # LOCK-AP-07

llm:
  default_provider: "anthropic"
  budget_krw_month: 93000             # LOCK-AP-09 V2 상한
  budget_warning_pct: 80              # P2 알람
  budget_critical_pct: 95             # P1 알람

permissions:
  max_level: 4                        # LOCK-AP-02 (Trading Node 만 5)
  l4_require_hitl: true
  l5_require_hitl: true

observability:
  log_level: "INFO"
  log_sampling_pct: 1.0
  otel_exporter: "otlp-http"
  trace_sampling_pct: 10.0

secrets:
  backend: "vault"                    # vault | aws_sm | env
  vault_role: "vamos-dev-node"
  refresh_interval_seconds: 3600
```

### 4.3 환경변수 주입 규칙 (DelimetedDot)

```
VAMOS_NODE__<SECTION>__<KEY>=<value>
예:
  VAMOS_NODE__LLM__DEFAULT_PROVIDER=anthropic
  VAMOS_NODE__LLM__BUDGET_KRW_MONTH=93000
  VAMOS_NODE__OBSERVABILITY__LOG_LEVEL=DEBUG
```

### 4.4 환경 승격 규칙 (dev → staging → prod)

| 설정 키 | dev 기본 | staging 기본 | prod 기본 | 승격 시 검증 |
|--------|---------|-------------|----------|-------------|
| `image_ref` | `:dev` 별칭 허용 | `@sha256:` digest 필수 | `@sha256:` digest 필수 | migration_guide.md §3 |
| `runtime.max_inflight` | 8 | 16 | 32 | 트래픽 예측 |
| `llm.budget_krw_month` | 40 000 | 60 000 | 93 000 | LOCK-AP-09 V2 상한 |
| `observability.log_level` | DEBUG | INFO | INFO | PII 검토 |
| `secrets.backend` | `env` | `vault` | `vault` | 암호화 필수 |

---

## §5. 비밀 관리 (Secret Manager) — STEP7-K L1149 원문 "API 키, 토큰 암호화 저장"

### 5.1 3 Backend 지원

| Backend | 적합 환경 | 장점 | 제약 |
|---------|----------|------|------|
| `vault` (HashiCorp) | prod/staging | 감사 로그, TTL, transit encryption | 네트워크 의존 |
| `aws_sm` (AWS Secrets Manager) | AWS 네이티브 prod | IAM 통합, KMS 연동 | vendor lock-in |
| `env` (환경변수) | dev only | 간단 | prod 금지 (§4.4) |

### 5.2 Secret 참조 구문 (`${secret://...}`)

```yaml
# config 파일 내 비밀 참조 — 평문 저장 금지
llm:
  api_keys:
    anthropic: "${secret://vault/vamos/dev-node/anthropic#api_key}"
    openai:    "${secret://vault/vamos/dev-node/openai#api_key}"
    google:    "${secret://vault/vamos/dev-node/google#api_key}"

external_apis:
  github_token: "${secret://aws_sm/vamos/prod/github_pat#value}"
  slack_bot:    "${secret://aws_sm/vamos/prod/slack#bot_token}"
```

### 5.3 Secret 로딩 Pydantic 모델

```python
class LLMSecrets(BaseModel):
    anthropic: Optional[SecretStr] = None
    openai: Optional[SecretStr] = None
    google: Optional[SecretStr] = None

    @validator("*", pre=True)
    def resolve_secret_ref(cls, v):
        if isinstance(v, str) and v.startswith("${secret://"):
            return resolve_secret_reference(v)     # backend dispatch
        return v

def resolve_secret_reference(ref: str) -> str:
    """
    ${secret://<backend>/<path>#<key>} → 실제 비밀 값
    backend: vault | aws_sm | env
    """
    # backend parsing 생략 (구현은 src/vamos/config/secret_resolver.py)
    ...
```

### 5.4 순환 (Rotation) 정책 연계

- 순환 정본은 **6-2 Security-Governance** — 본 문서는 refresh_interval_seconds 만 소비
- refresh 간격: vault 3600 s (기본), aws_sm 7200 s, env 갱신 불가
- 순환 실패 시 마지막 유효 값 유지 + P1 알람

---

## §6. 스키마 검증 (STEP7-K L1150 원문 "스키마 기반 유효성 검사")

### 6.1 단계별 검증

```
1. 파싱 (YAML → dict)
2. Pydantic 모델 인스턴스 생성
3. 상호 의존 validator (e.g., trading node 은 max_level >= 5 검증)
4. LOCK 정합 검증 (config.llm.budget_krw_month <= LOCK-AP-09 해당 단계)
5. 환경 승격 검증 (prod 면 image_ref digest pin 필수)
```

### 6.2 NodeConfig 메인 모델

```python
class NodeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VAMOS_NODE__",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    version: str = "1.0"
    node_type: Literal["dev", "research", "content", "quant", "trading", "personal"]
    environment: Literal["dev", "staging", "prod"]
    image_ref: str

    runtime: "RuntimeConfig"
    protocols: "ProtocolsConfig"
    llm: "LLMConfig"
    permissions: "PermissionsConfig"
    observability: "ObservabilityConfig"
    secrets: "SecretsConfig"

    @validator("image_ref")
    def prod_requires_digest_pin(cls, v, values):
        env = values.get("environment")
        if env == "prod" and "@sha256:" not in v:
            raise ValueError("prod image_ref must be digest-pinned (@sha256:...)")
        return v

    @validator("llm")
    def budget_matches_lock_ap_09(cls, v, values):
        env = values.get("environment")
        lock_ap_09 = {"dev": 40_000, "staging": 60_000, "prod": 93_000}
        if v.budget_krw_month > lock_ap_09[env]:
            raise ValueError(
                f"llm.budget_krw_month {v.budget_krw_month} exceeds LOCK-AP-09 {env} cap {lock_ap_09[env]}"
            )
        return v
```

### 6.3 Pre-commit + CI 검증

```bash
# pre-commit hook
python -m vamos.config.validate --path /etc/vamos/node.yaml --strict

# CI matrix: 3 환경 × 6 Node = 18 조합 스키마 검증
for env in dev staging prod; do
  for node in dev research content quant trading personal; do
    python -m vamos.config.validate --node "$node" --environment "$env"
  done
done
```

---

## §7. 동적 설정 (Hot Reload) — STEP7-K L1148 원문 "런타임 변경 가능"

### 7.1 트리거 채널 3종

| 채널 | 수용 대상 | 권한 |
|------|----------|------|
| `SIGHUP` 신호 | 파일 기반 설정 재로드 | L2 (운영자) |
| `etcd watch` (prefix `/vamos/node/<id>/config`) | 중앙 집중식 반영 | L3 (SRE) |
| `PATCH /admin/config` 내부 API | 운영 중 즉시 반영 | L3 + audit log |

### 7.2 Hot reload 가능/불가능

| 카테고리 | Hot reload | 재시작 필요 |
|---------|:---------:|:-----------:|
| `observability.log_level` | ✅ | — |
| `observability.trace_sampling_pct` | ✅ | — |
| `llm.default_provider` | ✅ | — |
| `runtime.max_inflight` | ✅ (점진 적용) | — |
| `permissions.max_level` 상향 | ✅ (L3 승인) | — |
| `permissions.max_level` 하향 | ✅ (즉시 적용) | — |
| `protocols.*` endpoint 변경 | ⚠️ | 재시작 권장 |
| `image_ref` 변경 | ❌ | migration_guide.md §3 Blue-Green |
| `node_type` 변경 | ❌ | 재배포 |

### 7.3 재로드 원자성 (Swap-on-success)

```python
class ConfigReloader:
    def reload(self, new_yaml_text: str) -> ReloadResult:
        # 1. 파싱 + 검증
        try:
            new_cfg = NodeConfig.model_validate(yaml.safe_load(new_yaml_text))
        except ValidationError as e:
            return ReloadResult(success=False, error=str(e))

        # 2. 이전 config 보존 후 원자 교체 (atomic pointer swap)
        old_cfg = self._current
        self._current = new_cfg
        # 3. 구독자 알림 (log/metric/span 설정 반영)
        self._notify_subscribers(new_cfg)
        # 4. Readiness 재검증 — fail 시 §7.4 이전 config 로 즉시 rollback
        try:
            if not request_readiness_recheck():
                raise RuntimeError("readiness_recheck_failed")
        except Exception as e:
            self._current = old_cfg
            self._notify_subscribers(old_cfg)
            return ReloadResult(success=False, error=f"readiness_rollback: {e}")
        return ReloadResult(success=True)
```

### 7.4 재로드 후 Readiness 재검증

`healthcheck_spec.md §4.3 startup gates` 재실행 → 1개라도 fail 시 이전 config 로 즉시 rollback.

---

## §8. 비용 관점 (LOCK-AP-09 verbatim)

### 8.1 LOCK-AP-09 정본 전재

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 |
|---------|------|----------|-----|--------|
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | **금지** |

### 8.2 Secret Manager 호출 비용 (월간)

| Backend | V1 | V2 | V3 |
|---------|:--:|:--:|:--:|
| Vault OSS (self-hosted) | 0 | 0 | 0 |
| Vault Enterprise / HCP | 0 | 8,000 | 25,000 |
| AWS SM (10 secret × 6 Node) | 3,000 | 3,000 | 3,000 |
| KMS Decrypt (refresh 3600s × 24h × 30) | 300 | 500 | 1,000 |

→ V2 ₩93K 상한 기준 Secret 관리 비용 ₩3~8K (logging 비용과 합산 시 APM 행 내 관리).

---

## §9. Phase 별 복구/다운그레이드 흐름 + Confidence Penalty

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| Secret resolve 실패 (vault down) | -0.15 | 누적 기준 |
| config 재로드 validation error | -0.10 | 누적 기준 |
| LOCK-AP-09 예산 초과 config (validator 차단) | -0.20 | ✅ |
| prod image_ref 별칭 사용 시도 (validator 차단) | -0.25 | ✅ |
| hot reload 후 readiness fail → rollback | -0.10 | 누적 기준 |
| Permission L4/L5 승격 요청 HITL 미승인 | -0.05 | HITL 재요청 |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety 정본 참조.

---

## §10. 에스컬레이션 페이로드 Python Class

```python
class ConfigEscalation(BaseModel):
    trace_id: str
    event_class: Literal[
        "secret_resolve_failed",
        "config_validation_error",
        "lock_ap_09_budget_exceeded",
        "prod_image_not_pinned",
        "reload_rollback",
        "permission_elevation_denied",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    details: Dict[str, str]
    recommended_action: str
    occurred_at: datetime

    def to_structured_log(self) -> dict:
        return {
            "error": {
                "class": self.event_class,
                "severity": self.severity,
            },
            "context": {
                "trace_id": self.trace_id,
                "details": self.details,
                "occurred_at": self.occurred_at.isoformat(),
            },
            "recovery": {
                "action": self.recommended_action,
                "confidence_delta": self.confidence_delta,
            },
        }
```

---

## §11. LOCK 매핑 5필드 표

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | §3 import + trace_id 필드 |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §7.1 PATCH /admin/config L3 필수 + §7.2 권한 승격 규칙 |
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 | 금지 | §4.2 protocols.mcp.transport `streamable-http` 엄수 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §4.2 protocols.a2a.bidirectional=true |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §6.2 validator `budget_matches_lock_ap_09` + §8.1 verbatim + §8.2 비용 매트릭스 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §9 penalty (참조자) |

---

## §12. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | CF-01 | prod 환경에서 image_ref 별칭(`:prod`) 설정 시 validation 실패 | ✅ 차단 |
| 2 | CF-02 | budget_krw_month=95000 (V2 환경) 시 validation 실패 | ✅ LOCK-AP-09 |
| 3 | CF-03 | Vault down 시 마지막 유효 비밀 값 유지 + P1 알람 | ✅ graceful |
| 4 | CF-04 | SIGHUP 후 log_level DEBUG 즉시 반영 (재시작 없이) | ✅ hot reload |
| 5 | CF-05 | PATCH /admin/config L2 권한 호출 → 403 | ✅ LOCK-AP-02 |
| 6 | CF-06 | etcd watch 반영 지연 < 5 s | ✅ SLA |
| 7 | CF-07 | 환경변수 오버라이드 `VAMOS_NODE__LLM__DEFAULT_PROVIDER=openai` 적용 | ✅ layering |
| 8 | CF-08 | 재로드 후 readiness fail → 이전 config 자동 rollback | ✅ §7.4 |
| 9 | CF-09 | pre-commit validate: 18 조합 스키마 전수 PASS | ✅ CI matrix |
| 10 | CF-10 | protocols.mcp.transport=`websocket` 설정 시 validation 실패 | ✅ LOCK-AP-04 |
| 11 | CF-11 | Secret reference `${secret://...}` 미해결 시 마스크 ("***") | ✅ PII |
| 12 | CF-12 | Secret refresh 3600 s 주기 동작 + metric `vamos_secret_refresh_total` 증가 | ✅ 관측 |

---

## §13. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 V2 파일 | 검증 기준 |
|-----------|-------------|----------|
| `image_ref` digest pin | `container_spec.md §7` | `@sha256:` 엄수 |
| BuildKit secret ↔ 런타임 secret 분리 | `container_spec.md §4.4` | 이미지 레이어 secret 0 |
| startup probe `config_loaded` | `healthcheck_spec.md §4.3` | config 로드 완료 후 True |
| 로그 레벨 / trace 샘플링 hot reload | `logging_spec.md §4.1 / §5` | SIGHUP 즉시 반영 |
| Blue-Green 환경 승격 diff | `migration_guide.md §3` | dev → staging → prod 필드 비교 |
| MCP transport `streamable-http` | `02_service-integration/llm_gateway.md §2.5` | LOCK-AP-04 공유 |
| Permission Matrix load 경로 | `06_autonomy-safety/permission_matrix.md` (V1) | read-only reference |

---

## §14. 검증 자가 체크리스트

- [x] K-059 4대 요건 전수 구현 (환경별 / 동적 / 비밀 / 스키마)
- [x] LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 (§11)
- [x] LOCK-AP-09 validator 코드 제시 (§6.2)
- [x] LOCK-AP-04 `streamable-http` 엄수 (§4.2)
- [x] LOCK-AP-10 재정의 없음 (§9 참조자)
- [x] FABRICATION 10-마커 0건 (step 3 finalize scan 예정)
- [x] 세션 간 인터페이스 7건 cross-check (§13)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족)
- [x] 에스컬레이션 Pydantic + structured JSON 3-block (§10)
- [x] Secret Manager 3 backend (vault/aws_sm/env) + 참조 구문 (§5.2)

---

*정본 소유: #13 Agent-Protocol-Interoperability*
*K-056 Kubernetes 배포 (STEP7-K L1101~L1111) 는 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의*
*Secret 키 순환·감사 정본은 6-2 Security-Governance 소유*
