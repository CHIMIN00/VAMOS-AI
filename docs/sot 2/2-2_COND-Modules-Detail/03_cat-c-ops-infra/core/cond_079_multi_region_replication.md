# COND-079: 다중 리전 복제 — L3 상세 명세

> **모듈 ID**: COND-079
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: LOW
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Active-Active / Active-Passive Replication, CRDT, Geo-routing, Conflict Resolution, **Saga**(failover orchestration)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class ReplicationConfig(BaseModel):
    mode: Literal["active_active", "active_passive"] = "active_passive"
    regions: list[str] = Field(..., min_length=2, description="ex) ['ap-northeast-2', 'us-west-2']")
    primary_region: Optional[str] = None
    conflict_resolution: Literal["lww", "crdt", "manual"] = "lww"
    sync_interval_ms: int = 1000
    max_lag_ms: int = 5000

class MultiRegionRequest(BaseModel):
    """COND-079 입력 스키마"""
    operation: Literal["sync", "status", "failover", "configure", "resolve_conflict"] = "status"
    replication_config: Optional[ReplicationConfig] = None
    target_dataset: str = Field(..., description="복제 대상 데이터셋/네임스페이스")
    target_region: Optional[str] = None       # failover 대상
    conflict_id: Optional[str] = None         # resolve_conflict 용
    resolution: Optional[dict] = None         # manual 해결값

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "status",
                "target_dataset": "user_profiles"
            }
        }
```

---

## E2. Output Schema

```python
class RegionStatus(BaseModel):
    region: str
    role: Literal["primary", "secondary", "standby"]
    state: Literal["healthy", "degraded", "down", "recovering"]
    lag_ms: int
    last_synced_at: str   # ISO-8601
    pending_ops: int

class ConflictRecord(BaseModel):
    conflict_id: str
    dataset: str
    key: str
    region_a: str
    region_b: str
    detected_at: str
    resolution_strategy: Literal["lww", "crdt", "manual", "pending"]

class MultiRegionResponse(BaseModel):
    """COND-079 출력 스키마"""
    operation: str
    replication_status: list[RegionStatus]
    lag_ms: dict[str, int] = Field(default_factory=dict, description="region → lag_ms")
    conflict_count: int = 0
    conflicts: list[ConflictRecord] = Field(default_factory=list)
    failover_completed: bool = False
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "status",
                "replication_status": [
                    {"region": "ap-northeast-2", "role": "primary", "state": "healthy",
                     "lag_ms": 0, "last_synced_at": "2026-04-07T10:00:00Z", "pending_ops": 0},
                    {"region": "us-west-2", "role": "secondary", "state": "healthy",
                     "lag_ms": 320, "last_synced_at": "2026-04-07T10:00:00Z", "pending_ops": 5}
                ],
                "lag_ms": {"ap-northeast-2": 0, "us-west-2": 320},
                "conflict_count": 0,
                "execution_time_ms": 12
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request) -> Result[MultiRegionResponse, VamosError]:
    cfg = registry.get(request.target_dataset)
    IF cfg IS NULL AND request.operation != "configure":
        RETURN Err(VamosError("COND_079_DATASET_NOT_REGISTERED", ...))

    SWITCH request.operation:
      CASE "configure":
          IF request.replication_config IS NULL:
              RETURN Err(VamosError("COND_079_CONFIG_REQUIRED", ...))
          IF len(request.replication_config.regions) < 2:
              RETURN Err(VamosError("COND_079_REGIONS_INSUFFICIENT", ...))
          registry.upsert(request.target_dataset, request.replication_config)
          replication_engine.bootstrap(request.target_dataset)
          RETURN Ok(...)

      CASE "status":
          status_list = [probe(region, request.target_dataset) for region in cfg.regions]
          lag_map = {s.region: s.lag_ms for s in status_list}
          conflicts = conflict_store.list(request.target_dataset, state="pending")
          RETURN Ok(MultiRegionResponse(operation="status",
                                        replication_status=status_list,
                                        lag_ms=lag_map,
                                        conflict_count=len(conflicts),
                                        conflicts=conflicts))

      CASE "sync":
          # Pull pending ops from each region and apply via conflict_resolution rule
          ops = sync_engine.gather_pending(request.target_dataset)
          FOR op IN ops:
              conflict = sync_engine.detect_conflict(op)
              IF conflict:
                  resolved = resolve(conflict, cfg.conflict_resolution)
                  IF resolved IS NULL:
                      conflict_store.persist(conflict)
                      CONTINUE
                  sync_engine.apply(resolved)
              ELSE:
                  sync_engine.apply(op)
          RETURN Ok(...)

      CASE "failover":
          IF request.target_region IS NULL:
              RETURN Err(VamosError("COND_079_FAILOVER_TARGET_REQUIRED", ...))
          IF request.target_region NOT IN cfg.regions:
              RETURN Err(VamosError("COND_079_FAILOVER_TARGET_INVALID", ...))
          target_status = probe(request.target_region, request.target_dataset)
          IF target_status.state == "down":
              RETURN Err(VamosError("COND_079_FAILOVER_TARGET_DOWN", ...))
          # Saga: drain primary writes → promote target → reroute clients
          saga = build_failover_saga(cfg, current_primary, request.target_region)
          result = saga_engine.run(saga)
          IF result.status != "completed":
              RETURN Err(VamosError("COND_079_FAILOVER_SAGA_FAILED", ...))
          registry.update_primary(request.target_dataset, request.target_region)
          geo_router.update(request.target_dataset, primary=request.target_region)
          RETURN Ok(... failover_completed=true ...)

      CASE "resolve_conflict":
          c = conflict_store.get(request.conflict_id)
          IF c IS NULL:
              RETURN Err(VamosError("COND_079_CONFLICT_NOT_FOUND", ...))
          IF cfg.conflict_resolution != "manual":
              RETURN Err(VamosError("COND_079_NOT_MANUAL_MODE", ...))
          sync_engine.apply_manual(c, request.resolution)
          conflict_store.mark_resolved(c.conflict_id)
          RETURN Ok(...)
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_079_DATASET_NOT_REGISTERED` | dataset 미등록 | `FB_COND_REJECT` | "복제 대상이 등록되지 않았습니다." |
| `COND_079_CONFIG_REQUIRED` | configure 시 누락 | `FB_COND_REJECT` | "설정이 필요합니다." |
| `COND_079_REGIONS_INSUFFICIENT` | regions < 2 | `FB_COND_REJECT` | "최소 2개 리전이 필요합니다." |
| `COND_079_LAG_EXCEEDED` | 모든 secondary lag 초과 | `FB_COND_079_PRIMARY_ONLY` | "복제 지연 초과. 프라이머리 단독 운영." |
| `COND_079_FAILOVER_TARGET_REQUIRED` | failover 대상 누락 | `FB_COND_REJECT` | "페일오버 대상이 필요합니다." |
| `COND_079_FAILOVER_TARGET_INVALID` | regions에 없음 | `FB_COND_REJECT` | "대상 리전이 유효하지 않습니다." |
| `COND_079_FAILOVER_TARGET_DOWN` | 대상 down | `FB_COND_REJECT` | "대상 리전이 다운 상태입니다." |
| `COND_079_FAILOVER_SAGA_FAILED` | saga 실패 → 자동 보상 | `FB_COND_079_REVERT` | "페일오버 실패. 원상 복구." |
| `COND_079_CONFLICT_NOT_FOUND` | conflict_id 미존재 | `FB_COND_REJECT` | "충돌 레코드를 찾을 수 없습니다." |
| `COND_079_NOT_MANUAL_MODE` | manual이 아닌데 수동 해결 시도 | `FB_COND_REJECT` | "수동 해결 모드가 아닙니다." |
| `COND_079_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "처리 시간 초과." |

```python
return Err(VamosError(
    failure_code="COND_079_FAILOVER_SAGA_FAILED",
    message=f"failover saga failed at phase={phase}: {reason}",
    fallback_id="FB_COND_079_REVERT",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | COND-033 (Saga, failover 오케스트레이션) — **CAT-C 내부 동반 사용** (직접 호출이 아닌 패턴 재사용; R-04-7 준수) |
| 제공 | 모든 CAT (DR/지역 분산) |

> **주**: COND-033은 §A.1상 CAT-C 내부 의존이지만 §A.2의 P0-1 매트릭스(CAT-A/B 범위)에는 미수록.
> Phase 2 P2-1 (CAT-C 내부 의존성 추출 P0-1 확장)에서 정식 등록 권장 — `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\CONFLICT_LOG.md`에 추적 항목으로 기록.

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| CockroachDB / YugabyteDB | 다중 리전 SQL |
| Cassandra / DynamoDB Global Tables | NoSQL 옵션 |
| Route 53 / Cloudflare Geo DNS | geo-routing |
| Kafka MirrorMaker 2 | 이벤트 복제 |
| etcd | 글로벌 메타데이터 |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **status p99** | ≤ 80 ms | > 300 ms | histogram |
| **sync 주기 lag p95** | ≤ 1 s | > 10 s | gauge |
| **failover RTO** | ≤ 60 s | > 5 min | incident timer |
| **failover RPO** | ≤ 5 s | > 60 s | data loss probe |
| **충돌 발생률** | ≤ 0.1 % | > 1 % | counter |
| **가용성** | 99.99 % | < 99.95 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "mr_status_two_regions"
  setup: [register("user_profiles", regions=["ap-ne-2", "us-w-2"], mode: "active_passive")]
  input: { operation: "status", target_dataset: "user_profiles" }
  expected: [replication_status.length == 2, conflict_count == 0]

- name: "mr_failover_promotes_secondary"
  setup: [seed_dataset(), primary_down("ap-ne-2")]
  input: { operation: "failover", target_dataset: "user_profiles", target_region: "us-w-2" }
  expected: [failover_completed == true]

- name: "mr_conflict_lww"
  setup: [active_active(), concurrent_writes(key: "k1", region_a: {ts: 100}, region_b: {ts: 110})]
  input: { operation: "sync", target_dataset: "user_profiles" }
  expected: [conflict_count == 0, applied_value.ts == 110]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (DR/글로벌 배포) |
| **Permission Level** | P0 |
| **게이트 요구** | policy, approval (failover 시 필수) |
| **호출 패턴** | 운영 콘솔 / 자동화 스크립트 → OpsInfraMixin.replication() |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.079.initialized` |
| 실행 시작/완료/실패 | `cond.c.079.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.079.health` |
| 종료 | `cond.c.079.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-079", op, dataset, primary_region, conflict_count}`

---

## E9. BaseModule ABC 적합성

```python
class Cond079MultiRegion(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._registry = await ReplicationRegistry.connect(self.config.registry_dsn)
        self._engine = ReplicationEngine.from_config(self.config)
        self._conflicts = await ConflictStore.connect(self.config.conflict_dsn)
        self._saga = SagaClient.from_config(self.config)
        self._geo_router = GeoRouter.from_config(self.config)
        self._emit_event("cond.c.079.initialized")
        return Ok(None)

    async def execute(self, request: MultiRegionRequest) -> Result[MultiRegionResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(
            healthy=await self._registry.ping() and await self._conflicts.ping(),
            latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._conflicts.close(); await self._registry.close()
        self._emit_event("cond.c.079.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-079", version="1.0.0",
                              capabilities=["sync", "status", "failover", "configure", "resolve_conflict"])
```

---

## E10. Configuration

```python
class Cond079Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 50
    timeout_ms: int = 10000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=3, backoff_ms=1000)

    registry_dsn: str
    conflict_dsn: str
    sync_interval_ms: int = 1000
    default_max_lag_ms: int = 5000
    default_conflict_resolution: Literal["lww", "crdt", "manual"] = "lww"
    failover_quorum: int = 2
    enable_geo_routing: bool = True
```
