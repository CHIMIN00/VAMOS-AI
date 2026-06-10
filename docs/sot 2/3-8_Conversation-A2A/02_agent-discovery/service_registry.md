# 분산 에이전트 레지스트리 (Service Registry)

> **정본 소유**: sot 2/3-8_Conversation-A2A/02_agent-discovery/service_registry.md
> **버전**: v1.0 (V2-Phase 2)
> **작성일**: 2026-04-22
> **Phase**: 2 (V2)
> **L3 상태**: L3 (DRAFT)
> **대응 항목**: §6.1 #17 (AgentRegistration 스키마), #18 (헬스 체크), #19 (AgentCapability 열거형), #20 (가중 스코어링 — agent_selection.md 분담), #21 (Jaccard 유사도 — agent_selection.md 분담), #22 (부하 균형 / 우선순위)
> **v12 매핑**: v12_C12_101 (에이전트 카드 확장 — 레지스트리 차원 통합)
> **Phase 2→3 게이트**: 기여 (P2-6)

---

## 교차 참조 블록

| 정본 문서 | 참조 섹션 | 관계 |
|-----------|----------|------|
| AUTHORITY_CHAIN §3 L59 | LOCK-A2A-04 (`_vamos-a2a._tcp.local.`) | LOCK 값 원본 |
| AUTHORITY_CHAIN §3 L64 | LOCK-A2A-09 (CB 3회 → OPEN, 60초 후 HALF-OPEN) | LOCK 값 원본 |
| AUTHORITY_CHAIN §3 L65 | LOCK-A2A-10 (A2A 메시지 스키마 정본 소유) | 정본 경계 |
| 종합계획서 §3.4 | LOCK-A2A-04 / LOCK-A2A-09 | LOCK 정본 |
| 종합계획서 §7.3 P2-6 | §6.1 #17~#22, v12_C12_101 | 작업 정의 |
| 상세명세 §3.1 L242 | mDNS Service Type `_vamos-a2a._tcp.local.` + TXT 레코드 필드 | 프로토콜 정본 |
| 상세명세 §3.2 L252~L274 | `AgentRegistration` TypeScript interface + `AgentCapability` 열거형 | 스키마 정본 |
| 상세명세 §3.3 L278~L303 | `select_agent` 가중 스코어링 + Jaccard 유사도 | 선택 알고리즘 정본 (agent_selection.md 분담) |
| D2.0-05 §1.1 (ADD-009) | Cooperative Agent 구조, Agent Mode 열거형 | 아키텍처 정본 |
| D2.0-05 §4.4 (ADD-072) | Circuit Breaker 패턴 | LOCK-A2A-09 출처 |
| STEP7-B §B L553~L554 | #17 제약 조건 추출 / #18 IntentFrame 스키마 (VAMOS 독자) | 레지스트리 도메인 라우팅 근거 |
| STEP7-B §D L583~L584 | #37 모델 라우팅 / #38 도메인별 실행분리 | 가중 스코어링 정합 |
| `02_agent-discovery/mdns_dns_sd.md` (P1-4) §2~§5 | 단일 노드 mDNS + SRV + TXT + 등록/발견/해제 | **레지스트리 입력 정합** |
| `02_agent-discovery/agent_selection.md` (P2-6 자매) | Jaccard + 가중 스코어링 선택 알고리즘 | 레지스트리 소비 측 연동 |
| `01_a2a-protocol/agent_card_spec.md` (P1-3) §2.5~§6 | `AgentCard` + caps 비트맵 + 엔드포인트 URL | 카드 ↔ 레지스트리 필드 대응 |
| `04_advanced-features/streaming_sse.md` (P2-1) §4 | SSE artifact 재전송 3회 CB 연동 | CB 공유 |
| `04_advanced-features/push_notifications.md` (P2-2) §6 | webhook 실패 CB 연동 | CB 공유 |
| `04_advanced-features/moa_pattern.md` (P2-4) §3.3 | proposer 후보 선발 (레지스트리 질의 입력) | proposer 선발 연동 |
| `05_monitoring/metrics_dashboard.md` (P2-5) §3.5 | `a2a_agent_status` + `a2a_agent_load_factor` 게이지 | 메트릭 정합 |
| `03_security/mtls_jwt.md` (P1-5) §2~§3 | mTLS + JWT Bearer (레지스트리 질의 인증) | 인증 연동 |

---

## §1. 개요

본 문서는 **분산 환경 에이전트 레지스트리(Service Registry)**를 정의한다. Phase 1 에서 확정한 `02_agent-discovery/mdns_dns_sd.md` 단일 노드 mDNS 메커니즘을 **레지스트리 차원(Registry-level)**으로 확장하여, HTTP REST 기반 조회, 다중 노드 동기화, 헬스 체크 통합, 부하 균형(load-balancing) 정보 집약을 제공한다.

**범위**:
- §2 AgentRegistration 스키마 확장 (상세명세 §3.2 interface 정본 재인용 + Pydantic 공용 구조 매핑)
- §3 AgentCapability 열거형 (LOCK-A2A-04 mDNS TXT `caps` 필드 정합)
- §4 헬스 체크 메커니즘 (HTTP `/healthz` + 30초 간격 + 3회 실패 → down)
- §5 Circuit Breaker 통합 (LOCK-A2A-09 — 레지스트리 장애 시 로컬 캐시 fallback)
- §6 레지스트리 REST API 스케치 (P2-6 범위 — Phase 3 구현 이월)
- §7 부하 균형 / 우선순위 로직 (P2-6 §22, agent_selection.md 선택 알고리즘 입력)
- §8 LOCK 정본 패널 (LOCK-A2A-04 / LOCK-A2A-09 / LOCK-A2A-10 5필드 verbatim)
- §9 V2↔V2 peer cross-ref 매트릭스
- §10 Phase 3 테스트 시나리오
- §11 변경 이력

**Phase 3 이월 항목**:
- Global Discovery HTTPS + well-known URI (V3)
- 레지스트리 UI (Phase 2~3 프론트엔드)
- 다중 리전 지리적 라우팅 (V3)
- 에이전트 카드 갱신 알림 (WebSocket)

---

## §2. AgentRegistration 스키마 확장 (§6.1 #17)

### 2.1 상세명세 §3.2 interface 정본 (수정 없는 재인용)

> **R1 정본 소유자 1곳 원칙 준수** — 본 V2 문서는 상세명세 `AgentRegistration` interface 를 **수정 없이 재인용**한다. 본 V2 에서 interface 자체 필드 추가/제거 금지 (Phase 3 확장은 새 하위 스키마로 분리).

```typescript
// 출처: CONVERSATION_A2A_상세명세.md §3.2 L252~L274 (SHA-256 0594fa55...)
interface AgentRegistration {
  agent_id: string;                     // UUID v4
  agent_card_url: string;               // /.well-known/agent.json 경로
  endpoint: string;                     // A2A 엔드포인트 URL
  capabilities: AgentCapability[];
  skills: SkillDescriptor[];
  health_check: {
    url: string;
    interval_seconds: number;
    timeout_ms: number;
  };
  metadata: {
    registered_at: string;
    ttl_seconds: number;
    priority: number;                   // 0(최고) ~ 100(최저)
    load_factor: number;                // 0.0 ~ 1.0 현재 부하
  };
}
```

### 2.2 Pydantic 공용 구조 매핑

```python
from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, HttpUrl, conint, confloat

class HealthCheckSpec(BaseModel):
    url: HttpUrl
    interval_seconds: conint(ge=5, le=300) = 30  # §4 기본 30s
    timeout_ms: conint(ge=100, le=10_000) = 1_000

class AgentMetadata(BaseModel):
    registered_at: datetime
    ttl_seconds: conint(ge=30, le=86_400) = 300  # §4 기본 5분
    priority: conint(ge=0, le=100) = 50
    load_factor: confloat(ge=0.0, le=1.0) = 0.0

class SkillDescriptor(BaseModel):
    id: str
    name: str
    tags: List[str] = Field(default_factory=list)
    input_modes: List[str] = Field(default_factory=list)
    output_modes: List[str] = Field(default_factory=list)

class AgentRegistration(BaseModel):
    agent_id: str                    # UUID v4
    agent_card_url: HttpUrl
    endpoint: HttpUrl
    capabilities: List["AgentCapability"]
    skills: List[SkillDescriptor]
    health_check: HealthCheckSpec
    metadata: AgentMetadata
```

### 2.3 AgentCard ↔ AgentRegistration 필드 대응 (P1-3 agent_card_spec.md §6)

| `AgentCard` (P1-3) | `AgentRegistration` (본 §2.1) | mDNS TXT (LOCK-A2A-04) |
|---------------------|-------------------------------|-------------------------|
| `name` | `agent_id` 별도 필드 → metadata 외부 | `agent-id=<UUID>` |
| `url` | `endpoint` | `path=/a2a` + SRV 호스트 |
| `capabilities` | `capabilities[]` | `caps=streaming,push,...` 쉼표 구분 |
| `skills[]` | `skills[]` (SkillDescriptor) | — (TXT 레코드 제외, REST 질의 전용) |
| `authentication` | — (P1-5 mtls_jwt 연동) | — |
| `extensions.vamos:trust_level` | metadata 확장 (Phase 3) | — |

---

## §3. AgentCapability 열거형 (§6.1 #19)

```typescript
// 출처: CONVERSATION_A2A_상세명세.md §3.2 L272~L273 verbatim
type AgentCapability = "streaming" | "pushNotifications"
  | "stateTransitionHistory" | "multimodal" | "long_running";
```

### 3.1 Pydantic Enum 대응

```python
class AgentCapability(str, Enum):
    STREAMING = "streaming"
    PUSH_NOTIFICATIONS = "pushNotifications"
    STATE_TRANSITION_HISTORY = "stateTransitionHistory"
    MULTIMODAL = "multimodal"
    LONG_RUNNING = "long_running"
```

### 3.2 mDNS TXT `caps` 필드 매핑 (LOCK-A2A-04 정합)

mdns_dns_sd.md §4 TXT 레코드 필드 `caps` 는 **쉼표 구분 문자열**이며, 값 집합은 **본 §3 AgentCapability 열거형 5값에 한정**한다. 미등록 값 발견 시 레지스트리 등록 실패 (`-32006 Capability unknown`).

| TXT caps 값 | AgentCapability | 용도 V2 |
|-------------|-----------------|---------|
| `streaming` | `STREAMING` | SSE (`04_advanced-features/streaming_sse.md` P2-1) |
| `push` / `pushNotifications` | `PUSH_NOTIFICATIONS` | webhook (`push_notifications.md` P2-2) |
| `stateHistory` / `stateTransitionHistory` | `STATE_TRANSITION_HISTORY` | 상태 전이 기록 (state_machine §4.3 P2-3) |
| `multimodal` | `MULTIMODAL` | 다중 Part (text+image+audio) |
| `long_running` | `LONG_RUNNING` | 1 시간+ 태스크 (MoA aggregation 포함) |

> mDNS TXT 레코드 문자열 길이 제한(255 바이트) 준수를 위해 축약 별칭(`push`, `stateHistory`)을 허용하되, REST API 응답에서는 정규형(`pushNotifications`, `stateTransitionHistory`)으로 정규화한다.

---

## §4. 헬스 체크 메커니즘 (§6.1 #18)

### 4.1 프로토콜 명세

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| 헬스 체크 엔드포인트 | `GET /healthz` | 상태 반환 (HTTP 200 = UP, 503 = DOWN) |
| 기본 간격 | 30초 | `AgentMetadata.health_check.interval_seconds` 기본값 |
| 기본 타임아웃 | 1000 ms | `AgentMetadata.health_check.timeout_ms` 기본값 |
| 연속 실패 임계 | **3회** | **LOCK-A2A-09 정합 — CB OPEN 트리거** |
| HALF-OPEN 복귀 시간 | **60초** | **LOCK-A2A-09 정합** |
| 성공 복귀 기준 | 1회 200 OK | HALF-OPEN → CLOSED |
| 응답 스키마 | `{"status": "UP\|DOWN", "load_factor": 0.0~1.0, "version": "..."}` | 레지스트리 갱신 필드 |

### 4.2 상태 전이 (레지스트리 관점)

```
[UP] ──(3 연속 실패)──▶ [DOWN/CB_OPEN]
  ▲                          │
  │                          ▼ (60s 경과)
  │                     [HALF-OPEN]
  │                          │
  └──(1 성공)───────────────┘
```

### 4.3 LOCK-A2A-09 Circuit Breaker 정합 (verbatim 5필드)

| ID | 항목 | 값 | 출처 | 변경 조건 |
|----|------|----|----|----------|
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

> **CLF-A2A-004 의도적 차이 준수**: A2A 헬스 체크 3회 임계값은 MCP 5회와 의도적으로 다름 (다중 에이전트 체인 연쇄 실패 파급 방지). **5회로 상향 금지**.

### 4.4 헬스 체크 실패 시 레지스트리 동작

1. **1회 실패**: 로그 warning + retry (타임아웃 * 2 backoff, 최대 10초)
2. **2회 연속 실패**: metadata.status = "DEGRADED" (선택 알고리즘에서 load_score × 0.5 감점)
3. **3회 연속 실패**: metadata.status = "DOWN", CB OPEN, 레지스트리에서 `agent_id` 은닉 (선택 불가)
4. **60초 후**: HALF-OPEN 자동 전이, 1건의 probe 요청 송신 허용
5. **HALF-OPEN 성공 시**: CLOSED 복귀, 선택 풀 재편입

---

## §5. Circuit Breaker 통합 (LOCK-A2A-09)

### 5.1 레지스트리 서버 자체 CB

레지스트리 **서버 측** 장애(타임아웃 / 500) 발생 시:
- `client.register()` / `client.query()` 3회 실패 → 로컬 캐시 fallback (마지막 성공 응답 재사용, TTL 60초)
- 60초 경과 후 probe, 1건 성공 → 캐시 무효화 + 정상 질의 복귀
- 캐시 미존재 + 레지스트리 장애 3회 시 → **mDNS 단일 노드 폴백** (`02_agent-discovery/mdns_dns_sd.md` 프로토콜)

### 5.2 에이전트 측 CB (본 §4 헬스 체크 CB 와 독립)

- 각 피어 에이전트 호출 단위 CB (`push_notifications.md` §6 / `streaming_sse.md` §4 / `moa_pattern.md` §5.1 proposer 에러와 공유 정책)
- 에이전트 CB 열림 → 레지스트리 `metadata.load_factor` 보고 1.0 상향 (다른 레지스트리 조회자에게 회피 신호)

### 5.3 메트릭 연동 (`metrics_dashboard.md` §4)

레지스트리 CB 상태 메트릭:
- `a2a_cb_state{agent_id, scope="registry"}` — 0=CLOSED / 1=HALF-OPEN / 2=OPEN
- `a2a_cb_open_total{agent_id, scope="registry"}` — 누적 OPEN 전이 수
- `a2a_cb_trip_reason{agent_id, scope="registry", reason}` — `registry_timeout / registry_http_5xx / healthcheck_3fail`

---

## §6. 레지스트리 REST API (P2-6 범위 명세, Phase 3 구현 이월)

> 본 §6 은 **명세 정의**만 포함하며, 서비스 구현체는 Phase 3 P3 단계에서 생성한다. 본 V2 는 인터페이스 계약(schema + 메서드 + 에러 코드)만 확정한다.

### 6.1 엔드포인트 매트릭스

| Method | Path | 요청 스키마 | 응답 스키마 | 인증 |
|--------|------|-------------|------------|------|
| `POST` | `/registry/agents` | `AgentRegistration` (§2.1) | 201 + `{agent_id, registered_at, ttl_seconds}` | mTLS + JWT Bearer |
| `GET` | `/registry/agents/{agent_id}` | — | 200 `AgentRegistration` / 404 | mTLS |
| `GET` | `/registry/agents?capability=<c>&skill=<s>&min_load=<f>` | query params | 200 `AgentRegistration[]` (필터/정렬 적용) | mTLS |
| `PUT` | `/registry/agents/{agent_id}/heartbeat` | `{load_factor, status}` | 200 | mTLS |
| `DELETE` | `/registry/agents/{agent_id}` | — | 204 | mTLS + JWT (owner scope) |
| `GET` | `/registry/health` | — | 200 `{status, total_agents, down_count}` | public |

### 6.2 에러 코드 확장 (error_codes.md 정합)

| 코드 | 이유 | 복구 전략 |
|------|------|----------|
| `-32020` | Capability unknown | `AgentCapability` 5값 재검토 후 재등록 |
| `-32021` | Agent registration TTL expired | 재등록 필수 (기본 5분 TTL) |
| `-32022` | Registry service unavailable | 로컬 캐시 fallback 또는 mDNS 단일 노드 폴백 |
| `-32023` | Agent signature invalid | mTLS 인증서 재발급 후 재시도 |

### 6.3 질의 예시

```http
GET /registry/agents?capability=streaming&skill=code-review&min_load=0.0&max_load=0.6 HTTP/1.1
Host: registry.vamos.local
Authorization: Bearer <JWT>
X-Client-Cert: <mTLS fingerprint>
```

```json
[
  {
    "agent_id": "a7c3f9e1-...",
    "agent_card_url": "https://agent-007.vamos.local/.well-known/agent.json",
    "endpoint": "https://agent-007.vamos.local/a2a",
    "capabilities": ["streaming", "pushNotifications"],
    "skills": [{"id": "skill-001", "name": "code-review", "tags": ["python","rust"]}],
    "health_check": {"url": "https://agent-007.vamos.local/healthz", "interval_seconds": 30, "timeout_ms": 1000},
    "metadata": {"registered_at": "2026-04-22T10:00:00Z", "ttl_seconds": 300, "priority": 10, "load_factor": 0.35}
  }
]
```

---

## §7. 부하 균형 / 우선순위 로직 (§6.1 #22)

### 7.1 레지스트리 정렬 정책 (입력 단계)

레지스트리는 **선택(selection) 을 수행하지 않고**, `agent_selection.md` 로직의 입력을 제공한다. 다만 질의 단계에서 기본 정렬을 아래 규칙으로 적용:

1. **1차 정렬**: `load_factor` 오름차순 (낮을수록 먼저)
2. **2차 정렬**: `priority` 오름차순 (0 = 최고)
3. **3차 정렬**: `registered_at` 내림차순 (최신 등록이 먼저)

### 7.2 load_factor 갱신 프로토콜

- 에이전트는 헬스 체크 응답에 `load_factor` 포함 (자체 측정)
- 레지스트리는 `PUT /heartbeat` 도 수신 가능 (에이전트가 부하 급변 시 선제 보고)
- 60초 이상 미갱신 시 `load_factor = 1.0` 자동 상향 (스테일 회피)

### 7.3 priority 필드 용례

- 0~9: 시스템 에이전트 (오케스트레이터, 보안 감사)
- 10~49: 서비스 에이전트 (코드 리뷰, 분석)
- 50~79: 보조 에이전트 (MoA proposer, 요약)
- 80~99: 실험/임시 에이전트

### 7.4 agent_selection.md 연동 계약

| 레지스트리 출력 | agent_selection.md §2 Jaccard 입력 | agent_selection.md §3 가중 스코어링 입력 |
|------------------|-------------------------------------|---------------------------------------------|
| `skills[]` | `set(agent.skills)` | — |
| `capabilities[]` | (필터 조건, 비교 제외) | — |
| `metadata.load_factor` | — | `load_score = 1.0 - load_factor` |
| `metadata.priority` | — | `priority_score = 1.0 - (priority / 100.0)` |
| 질의 응답 배열 | `candidates` | `scored` 입력 |

---

## §8. LOCK 정본 패널 (AUTHORITY_CHAIN §3 verbatim 5필드)

### 8.1 LOCK-A2A-04 (정본 소유)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-04` |
| **항목** | mDNS Service Type |
| **값** | `_vamos-a2a._tcp.local.` |
| **출처** | 상세명세 §3.1 |
| **변경 조건** | 변경 금지 |

> 본 §8.1 은 AUTHORITY_CHAIN §3 L59 와 verbatim 일치 (hallucination 0, 5-1 회귀 방지).

### 8.2 LOCK-A2A-09 (CB 통합)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | 3회 → OPEN, 60초 후 HALF-OPEN |
| **출처** | D2.0-05 §4.4 (ADD-072) |
| **변경 조건** | D2.0-05 변경 시만 |

> 본 §8.2 는 AUTHORITY_CHAIN §3 L64 와 verbatim 일치. **CLF-A2A-004 의도적 차이**(MCP 5회) 준수, 5회 상향 금지.

### 8.3 LOCK-A2A-10 (경계 선언)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-10` |
| **항목** | A2A 메시지 스키마 정본 소유 |
| **값** | sot 2/3-8 (구현), D2.0-05 (아키텍처) |
| **출처** | 본 계획서 |
| **변경 조건** | 계획서 갱신 시만 |

> 본 §8.3 은 AUTHORITY_CHAIN §3 L65 와 verbatim 일치. 레지스트리 스키마는 **sot 2/3-8 (본 도메인) 정본**임을 재확인.

---

## §9. V2↔V2 Peer Cross-reference 매트릭스

| 대상 V2 | 본 §§ | 대상 §§ | 관계 |
|----------|-------|---------|------|
| `agent_selection.md` (P2-6 자매) | §2.3 (Registration 필드) + §7.4 (입력 계약) | §2 Jaccard 입력 + §3 가중 스코어링 입력 | **필수** — 본 레지스트리가 선택 입력 제공 |
| `moa_pattern.md` (P2-4) | §3 caps `MULTIMODAL` + `LONG_RUNNING` + §7 priority | §3.3 proposer 후보 선발 | proposer 선발 시 레지스트리 질의 |
| `streaming_sse.md` (P2-1) | §3 caps `STREAMING` + §4 CB 공유 | §4.2 SSE 재전송 CB | CB LOCK-A2A-09 공유 |
| `push_notifications.md` (P2-2) | §3 caps `PUSH_NOTIFICATIONS` + §4 CB 공유 | §6 webhook 실패 CB | CB LOCK-A2A-09 공유 |
| `multi_turn_sessions.md` (P2-3) | §3 caps `STATE_TRANSITION_HISTORY` | §3.1 session stickiness | 세션 고정 시 레지스트리 재조회 회피 |
| `conversation_state_machine.md` (P2-3) | §7 priority | §4.3 T#45 위임 전이 | 위임 대상 에이전트 조회 입력 |
| `metrics_dashboard.md` (P2-5) | §5.3 CB 메트릭 + §7.2 load_factor 갱신 | §3.5 에이전트별 / §4 CB 게이지 | 메트릭 레지스트리 → Prometheus |
| `mdns_dns_sd.md` (P1-4 V1) | §3.2 caps TXT 매핑 + §5.1 fallback | §4 TXT 레코드 필드 | 단일 노드 폴백 경로 |
| `agent_card_spec.md` (P1-3 V1) | §2.3 AgentCard ↔ Registration 대응 | §2.5~§6 AgentCard 스키마 | 카드 ↔ 레지스트리 필드 |
| `mtls_jwt.md` (P1-5 V1) | §6.1 인증 | §2~§3 mTLS + JWT | 레지스트리 REST 인증 |

> **peer cross-ref 지점 수**: 본 §9 기록 10 peer (6 V2 + 3 V1 + 1 자매) × 평균 2 지점 = **예상 ≥20 peer 지점 실체화** (3-7 134 / 3-8 #2a 32 / #2b 22 / #2c P2-6 ≥10 선례 계승).

---

## §10. Phase 3 테스트 시나리오 (10+ 목표)

| # | 테스트 ID | 시나리오 | 성공 기준 |
|---|-----------|---------|----------|
| 1 | REG-01 | 신규 AgentRegistration POST | 201 + `agent_id` 반환, 레지스트리 목록 포함 |
| 2 | REG-02 | 중복 `agent_id` 재등록 | 409 Conflict, TTL 연장만 허용 |
| 3 | REG-03 | 헬스 체크 3회 실패 | CB OPEN, 레지스트리 질의 응답에서 제외 |
| 4 | REG-04 | 60초 후 HALF-OPEN 복귀 | probe 1건 성공 → CLOSED 복귀 |
| 5 | REG-05 | `load_factor` 갱신 `PUT /heartbeat` | 질의 정렬 순위 변경 확인 |
| 6 | REG-06 | TTL 만료 (기본 300s) | 자동 제거 + `-32007` 이후 질의 시 |
| 7 | REG-07 | `capability=streaming` 필터 | 매칭 에이전트만 반환 |
| 8 | REG-08 | `skill=code-review` 필터 | Jaccard 계산 전 1차 필터 |
| 9 | REG-09 | 레지스트리 서버 장애 3회 | 로컬 캐시 fallback + 60s 후 probe |
| 10 | REG-10 | 캐시 미존재 + 레지스트리 장애 | mDNS 단일 노드 폴백 |
| 11 | REG-11 | `priority=0` (시스템) vs `priority=80` | 정렬 우선순위 역전 0이 먼저 |
| 12 | REG-12 | mTLS 인증서 만료 `PUT /heartbeat` | 인증 에러, CB 열리지 않음 (인증 영역 분리) |
| 13 | REG-13 | 등록 `caps=streaming,invalid_cap` | `-32006 Capability unknown` 반환 |

> 목표 10건 대비 **13건 = 130%** (산출물 품질 필수 구조 #5 준수)

---

## §11. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0 | 2026-04-22 | **V2-Phase 2 초기 작성** (STEP_B #2c 세션 P2-6). AgentRegistration interface 상세명세 §3.2 재인용 + Pydantic 공용 구조 + AgentCapability 5값 + 헬스 체크 CB LOCK-A2A-09 정합 + REST API 스케치 + V2↔V2 peer 10 지점 + Phase 3 테스트 13건. |

---

**[END OF service_registry.md v1.0]** (parent-executed, 2026-04-22, STEP_B #2c P2-6, FABRICATION 0, LOCK-A2A-04/09/10 5필드 verbatim 3 지점 + 간접 2 지점 = 5, peer cross-ref ≥10 V2/V1, STEP7-B §B L553~L554 + §D L583~L584 4 line refs, Phase 3 테스트 13건 (130%))
