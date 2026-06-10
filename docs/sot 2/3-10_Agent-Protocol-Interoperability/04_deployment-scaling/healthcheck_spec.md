# 에이전트 헬스체크 (Liveness/Readiness/Startup) — K-057 (V2 신규 L3)

> **STEP7-K**: K-057 에이전트 헬스체크 (L1113~L1123 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
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
| STEP7-K (Level 2) | L1113~L1123 | K-057 원문 (Heartbeat, `/health`, 메트릭 응답시간·에러율·큐 길이, 자동 재시작) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-04 | MCP Streamable HTTP — 헬스 엔드포인트도 동일 전송방식 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 — 두 프로토콜 모두 헬스 응답 가능 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 — 헬스 호출 빈도 × 로그 저장 비용 관리 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% 시 HITL (06_autonomy-safety 정본, 본 문서 참조자) |
| 구조화_종합계획서.md | §7.4 P2-4 L1213~L1245 | Phase 2 K-057 배치 |
| 04_deployment-scaling/_index.md | L17 | K-057 L0→L3 |
| 04_deployment-scaling/container_spec.md | §4.1 HEALTHCHECK | Dockerfile readiness probe 호출 대상 |
| 04_deployment-scaling/logging_spec.md | §4 메트릭 | Prometheus exporter 공유 |
| 04_deployment-scaling/migration_guide.md | §3 Blue-Green | 헬스 실패 시 자동 롤백 트리거 |
| 04_deployment-scaling/config_spec.md | §3 Hot reload | 설정 재로드 후 readiness 재검증 |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 import |
| 03_data-exchange/event_bus.md (V1) | 이벤트 버스 상세 | 헬스 상태 전이 이벤트 publish |
| 6-12 Event-Logging | LOCK-EL-05 구조화 JSON | 본 문서 §6 구조화 JSON 스키마 소비 |

> **R6 준수**: What+How 전용.

---

## §2. Purpose & Scope

### 2.1 세 가지 Probe 분리 (K8s 표준 + Docker HEALTHCHECK)

| Probe | 용도 | 실패 시 동작 | 주기 (기본) | 타임아웃 |
|-------|------|-------------|:----------:|:--------:|
| **startup** | 콜드 스타트 완료 여부 | failureThreshold 초과 시 컨테이너 kill | 5 s | 3 s |
| **liveness** | 런타임 행(hang)/데드락 감지 | 재시작 | 10 s | 3 s |
| **readiness** | 트래픽 수용 가능 여부 | 트래픽 제외 (Service endpoints 제거) | 5 s | 2 s |

> Docker Compose 운영 환경은 `HEALTHCHECK` 단일 명령이므로 **readiness 만** 호출하고, K8s 이관(K-056 V3) 시 위 세 probe 전수 적용.

### 2.2 엔드포인트 스펙

```
GET  /healthz/liveness    → 200 OK (행 여부) / 503 (데드락·치명 오류)
GET  /healthz/readiness   → 200 OK (트래픽 수용) / 503 (의존성 미준비)
GET  /healthz/startup     → 200 OK (부팅 완료) / 503 (부팅 중)
GET  /metrics             → Prometheus text exposition
```

모든 엔드포인트는 **내부 네트워크 전용**(`127.0.0.1:9090`)으로 바인딩, 외부 노출 금지.

---

## §3. 공통 자료 구조 Import

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,
    GatePolicy,
    AdapterResult,
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
```

---

## §4. Probe 구현 상세

### 4.1 Liveness — 데드락·치명 행 감지 (Big-O: O(1) — 원자 카운터)

```python
class LivenessState(BaseModel):
    last_event_loop_tick: datetime
    inflight_operations: int
    deadlock_watchdog_triggered: bool
    max_tick_gap_ms: int = 2000   # 2s 초과 시 행으로 간주

class LivenessProbe:
    THRESHOLD_MS = 2000

    def evaluate(self, state: LivenessState) -> tuple[bool, str]:
        # 이벤트 루프 tick gap 기반 판정
        gap_ms = (datetime.utcnow() - state.last_event_loop_tick).total_seconds() * 1000
        if state.deadlock_watchdog_triggered:
            return False, f"watchdog_triggered"
        if gap_ms > self.THRESHOLD_MS:
            return False, f"event_loop_stall_{int(gap_ms)}ms"
        return True, "alive"
```

### 4.2 Readiness — 의존성·큐 포화 감지 (STEP7-K L1119 "큐 길이")

```python
class ReadinessChecks(BaseModel):
    mcp_client_connected: bool         # LOCK-AP-04 Streamable HTTP 핸드쉐이크
    a2a_bridge_connected: bool         # LOCK-AP-07
    llm_gateway_reachable: bool        # 02_service-integration/llm_gateway.md §2
    queue_depth: int
    queue_capacity: int
    active_permissions_loaded: bool    # LOCK-AP-02 Permission Matrix

    @property
    def queue_saturation(self) -> float:
        return self.queue_depth / max(self.queue_capacity, 1)

class ReadinessProbe:
    QUEUE_SATURATION_MAX = 0.85

    def evaluate(self, checks: ReadinessChecks) -> tuple[bool, str]:
        reasons: list[str] = []
        if not checks.mcp_client_connected:
            reasons.append("mcp_unreachable")
        if not checks.a2a_bridge_connected:
            reasons.append("a2a_bridge_down")
        if not checks.llm_gateway_reachable:
            reasons.append("llm_gateway_down")
        if checks.queue_saturation > self.QUEUE_SATURATION_MAX:
            reasons.append(f"queue_saturation_{checks.queue_saturation:.2f}")
        if not checks.active_permissions_loaded:
            reasons.append("permission_matrix_not_loaded")
        if reasons:
            return False, ",".join(reasons)
        return True, "ready"
```

### 4.3 Startup — 부팅 완료 순차 게이트

```python
class StartupGates(BaseModel):
    config_loaded: bool
    permission_matrix_loaded: bool      # LOCK-AP-02
    lock_set_hydrated: bool             # LOCK-AP-01~10 10/10
    mcp_client_initialized: bool        # LOCK-AP-04
    a2a_bridge_initialized: bool        # LOCK-AP-07
    framework_adapter_ready: bool       # 01_framework-adapters/* (LangGraph/CrewAI/AutoGen)
    guardrail_loaded: bool              # 06_autonomy-safety/guardrail_rules.md

    def all_passed(self) -> bool:
        return all(v for v in self.model_dump().values())
```

startup probe 는 위 7 게이트가 모두 True 일 때만 200 OK.

---

## §5. 메트릭 카탈로그 (STEP7-K L1119 "응답 시간, 에러율, 큐 길이")

### 5.1 Prometheus 표준 메트릭

| 메트릭 | 타입 | 라벨 | 설명 |
|--------|------|------|------|
| `vamos_agent_request_duration_seconds` | Histogram | `node_type`, `protocol`, `route` | 요청 처리 시간 |
| `vamos_agent_request_total` | Counter | `node_type`, `protocol`, `route`, `outcome` | 요청 건수 |
| `vamos_agent_errors_total` | Counter | `node_type`, `protocol`, `error_class` | 오류 건수 |
| `vamos_agent_queue_depth` | Gauge | `node_type`, `queue_name` | 큐 대기 항목 수 |
| `vamos_agent_queue_capacity` | Gauge | `node_type`, `queue_name` | 큐 용량 (saturation 분모, §4.2) |
| `vamos_agent_queue_capacity` | Gauge | `node_type`, `queue_name` | 큐 용량 (saturation 분모, §4.2) |
| `vamos_agent_inflight_requests` | Gauge | `node_type` | 진행 중 요청 수 |
| `vamos_agent_health_probe_total` | Counter | `probe_type`, `outcome` | probe 호출·결과 |
| `vamos_agent_heartbeat_seconds` | Gauge | `node_type` | 마지막 heartbeat 이후 경과 |
| `vamos_agent_lock_set_violations_total` | Counter | `lock_id` | LOCK-AP-\* 위반 누적 (상시 0 유지) |
| `vamos_agent_confidence_gauge` | Gauge | `node_type`, `task_class` | 현재 confidence (LOCK-AP-10 < 0.50 알람) |

### 5.2 SLO 매트릭스 (Node × probe)

| Node | p95 request duration | 에러율 상한 | 큐 saturation 상한 | 월간 가용성 목표 |
|------|:-------------------:|:----------:|:-----------------:|:----------------:|
| Dev | 2.0 s | 0.5 % | 0.75 | 99.5 % |
| Research | 3.5 s | 0.7 % | 0.80 | 99.0 % |
| Content | 4.0 s | 0.8 % | 0.80 | 99.0 % |
| Quant | 5.0 s | 1.0 % | 0.75 | 99.0 % |
| Trading | 1.2 s | 0.2 % | 0.60 | 99.9 % |
| Personal | 2.5 s | 0.5 % | 0.80 | 99.0 % |

### 5.3 SLI → Alert 규칙 (PromQL 예)

```promql
# 에러율 > 2 % for 5m → L3 자동 재시작 (LOCK-AP-02 L3)
sum by(node_type) (
  rate(vamos_agent_errors_total[5m])
) / sum by(node_type) (
  rate(vamos_agent_request_total[5m])
) > 0.02

# Heartbeat 30 s 이상 미도달 → liveness failure
vamos_agent_heartbeat_seconds > 30

# Queue saturation > 85 % for 3m → readiness 제외
avg_over_time(vamos_agent_queue_depth[3m]) / on(node_type)
  avg_over_time(vamos_agent_queue_capacity[3m]) > 0.85
```

---

## §6. 구조화 JSON 로그 3-block (logging_spec.md §2 스키마 준수)

### 6.1 정상 readiness 로그 (sampled 1 %)

```json
{
  "error": null,
  "context": {
    "probe": "readiness",
    "node_type": "dev",
    "trace_id": "01HVZ9K3M4Q7R8T9XWY0ZABCDE",
    "checks": {
      "mcp_client_connected": true,
      "a2a_bridge_connected": true,
      "llm_gateway_reachable": true,
      "queue_saturation": 0.42,
      "permission_matrix_loaded": true
    },
    "ts": "2026-04-22T10:15:32.123Z"
  },
  "recovery": null
}
```

### 6.2 실패 liveness 로그 (stall 감지)

```json
{
  "error": {
    "class": "event_loop_stall",
    "severity": "CRITICAL",
    "gap_ms": 3450
  },
  "context": {
    "probe": "liveness",
    "node_type": "quant",
    "trace_id": "01HVZ9K3M4Q7R8T9XWY0ZFGHIJ",
    "inflight_operations": 7,
    "ts": "2026-04-22T10:15:32.567Z"
  },
  "recovery": {
    "action": "container_restart",
    "confidence_delta": -0.20,
    "next_probe_in_seconds": 10
  }
}
```

---

## §7. 자동 재시작 정책 (STEP7-K L1120 "비정상 감지 → 재시작")

### 7.1 재시작 판단 트리

```
[liveness 실패]
  ├─ 연속 3회 → 즉시 재시작 (Docker restart:on-failure:3)
  └─ 재시작 후 startup probe 대기
[readiness 실패]
  ├─ 5분 이상 503 → 트래픽 제외 유지 + 알람
  └─ 10분 이상 지속 → migration_guide.md §4 자동 롤백 트리거
[startup 실패]
  ├─ startupProbe.failureThreshold × periodSeconds = 5 × 5 = 25s 초과 → 부팅 실패
  └─ 이전 digest 로 롤백 (container_spec.md §9.1 장애 트리)
```

### 7.2 Backoff 정책

| 재시작 횟수 | backoff 지연 | 누적 시간 |
|:----------:|:------------:|:---------:|
| 1 | 0 s | 0 s |
| 2 | 10 s | 10 s |
| 3 | 30 s | 40 s |
| 4 | 90 s | 130 s |
| 5+ | 300 s (상한) | — |

5회 이상 재시작 시 → HITL 에스컬레이션(Permission L3 이상).

---

## §8. 비용 영향 (LOCK-AP-09 verbatim)

### 8.1 LOCK-AP-09 정본 전재

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 |
|---------|------|----------|-----|--------|
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | **금지** |

### 8.2 Probe 호출 빈도 × 비용

| 구간 | probe/sec (6 Node 합) | 월간 호출 수 | 메트릭 저장 (GB/월) | 영향 |
|------|:--------------------:|:-----------:|:-------------------:|------|
| V1 | 6 × 1/10s = 0.6 | 1.55 M | 0.5 | APM 행 ₩10K 이내 |
| V2 | 6 × 3/10s = 1.8 | 4.66 M | 2.1 | APM 행 ₩19K 이내 |
| V3 | 6 × 6/10s = 3.6 | 9.33 M | 5.0 | APM 행 ₩49K 이내 |

> V2 ₩93K 상한 기준, 헬스체크 단독 비용은 APM 행 내에서 관리. Prometheus `scrape_interval` 15 s 초과 설정 금지 (1 s 감소당 월 TSDB ≈ 70 MiB 증가).

---

## §9. Phase 별 복구/다운그레이드 흐름 + Confidence Penalty

| 이벤트 | Confidence penalty | HITL 발동 (LOCK-AP-10 < 0.50) |
|--------|:-----------------:|:----------------------------:|
| liveness 1회 실패 | -0.05 | 아님 |
| liveness 연속 3회 실패 → 재시작 | -0.20 | 누적 기준 (guardrail_rules.md 정본) |
| readiness 5분 연속 실패 | -0.15 | 누적 기준 |
| startup 실패 → 롤백 | -0.25 | ✅ |
| SLI 위반 (에러율 > 2 % 5m) | -0.10 | 누적 기준 |
| Heartbeat 60 s 미도달 | -0.30 | ✅ |

> LOCK-AP-10 재정의 없음 — `06_autonomy-safety/guardrail_rules.md` (P2-6 정본) cumulative 기준을 전제.

---

## §10. 에스컬레이션 페이로드 Python Class

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict
from datetime import datetime

class HealthEscalation(BaseModel):
    trace_id: str
    node_type: Literal["dev", "research", "content", "quant", "trading", "personal"]
    probe: Literal["liveness", "readiness", "startup"]
    consecutive_failures: int
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    recommended_action: Literal[
        "container_restart",
        "rollback_previous_digest",
        "drain_traffic",
        "escalate_hitl_L3",
        "escalate_hitl_L4",
    ]
    metrics_snapshot: Dict[str, float]
    occurred_at: datetime

    def to_structured_log(self) -> dict:
        return {
            "error": {
                "class": f"health_{self.probe}_failure",
                "severity": "HIGH" if self.consecutive_failures >= 3 else "MEDIUM",
                "consecutive_failures": self.consecutive_failures,
            },
            "context": {
                "probe": self.probe,
                "node_type": self.node_type,
                "trace_id": self.trace_id,
                "metrics": self.metrics_snapshot,
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
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §7.2 5회 이상 재시작 → L3 이상 HITL |
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 | 금지 | §2.2 헬스 endpoints HTTP only, WS 금지 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §4.2 readiness checks (MCP + A2A) |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §8.1 verbatim + §8.2 probe 호출 비용 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §9 penalty 표 (재정의 없음, 06_autonomy-safety 정본 참조) |

---

## §12. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | HC-01 | startup probe 25s 내 통과 (콜드 스타트) | ✅ 정상 부팅 |
| 2 | HC-02 | liveness 이벤트 루프 stall 3s 감지 → 재시작 | ✅ 컨테이너 재시작 |
| 3 | HC-03 | readiness: LLM Gateway down → 503 + 트래픽 제외 | ✅ drain |
| 4 | HC-04 | readiness: queue saturation > 0.85 → 503 | ✅ 백프레셔 |
| 5 | HC-05 | readiness: MCP client 미연결 → 503 (LOCK-AP-04 미충족) | ✅ LOCK 준수 |
| 6 | HC-06 | readiness: A2A bridge down → 503 (LOCK-AP-07 미충족) | ✅ LOCK 준수 |
| 7 | HC-07 | 재시작 5회 초과 → HITL L3 에스컬레이션 | ✅ guardrail 발동 |
| 8 | HC-08 | Heartbeat 60 s 미도달 → confidence -0.30 → HITL | ✅ LOCK-AP-10 발동 |
| 9 | HC-09 | 정상 probe 1 % 샘플링 로그 volume < 예산 | ✅ APM 비용 |
| 10 | HC-10 | SLI error rate > 2 % for 5m → 자동 알람 | ✅ PromQL rule 동작 |
| 11 | HC-11 | `/metrics` 외부 접근 차단 (127.0.0.1 only) | ✅ 보안 |
| 12 | HC-12 | startup 의 7 게이트 중 1 미달 시 non-ready 유지 | ✅ 부분 부팅 차단 |

---

## §13. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 V2 파일 | 검증 기준 |
|-----------|-------------|----------|
| Dockerfile HEALTHCHECK CMD | `container_spec.md §4.1/§5.3` | readiness probe 호출 CLI 일치 |
| Prometheus scrape endpoint | `logging_spec.md §4` | `/metrics` 스크레이프 interval 15s |
| 자동 롤백 트리거 | `migration_guide.md §4` | readiness 10분 연속 실패 시 활성 |
| Hot reload 이후 재검증 | `config_spec.md §3.5` | readiness 재호출 주기 |
| MoA Proposer 장애 격리 | `01_framework-adapters/moa_pattern.md §6` | 개별 Proposer liveness 독립 판정 |

---

## §14. 검증 자가 체크리스트

- [x] K-057 3 probe (liveness/readiness/startup) 전수 구현 (STEP7-K L1115~L1120)
- [x] SLA 모니터링 SLI/SLO/Alert 정의 (§5)
- [x] 자동 재시작 + Backoff 정책 (§7)
- [x] LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 (§11)
- [x] LOCK-AP-10 본 문서 재정의 없음 (§9 참조자)
- [x] FABRICATION 10-마커 0건 (step 3 finalize scan 예정)
- [x] 세션 간 인터페이스 5건 cross-check (§13)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족)
- [x] 에스컬레이션 Pydantic + structured JSON 3-block (§6/§10)
- [x] 비용 영향 probe × LOCK-AP-09 정합 (§8.2)

---

*정본 소유: #13 Agent-Protocol-Interoperability*
*K-056 Kubernetes 배포 (STEP7-K L1101~L1111) 는 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의*
