# 04.connection_pool — MCP Connection Pool 최적화

> **세션**: 2-4 (Phase 2 V2-Phase 2) · **Phase**: 2 V2 · **상태**: L3 DRAFT
> **범위**: Connection Pool 최대 10 (LOCK-MCP-10) + acquire/release + 유휴 재사용 + 워밍업 + health check 30s + max_lifetime 3600s + 고갈 시 fallback + Phase 2 9 서버 + active 5 제약 (LOCK-MCP-05) + LOCK-MCP-06/07 재시도/CB 통합
> **L3 승급 기준**: LOCK-MCP-10 정본 인용 + bridge_layer.md §5 acquire/release 인터페이스 정합 + retry_circuit_breaker.md §7 fallback 연동 + 모니터링 메트릭 (P2→3 exit_gate "모니터링 메트릭" 핵심 충족)
> **편성 근거**: 종합계획서 §7 Phase 2 #6 "Connection Pool 최적화" — `03_connection-management/connection_pool.md` 신규 산출물 (plan §7.3 2-4 산출물 명세 명시)

---

## §1. 교차 참조 블록

| 참조 대상 | 위치 | 용도 |
|----------|------|------|
| 종합계획서 §3.4 LOCK-MCP-01 | `MCP_SERVER_CLIENT_구조화_종합계획서.md` | 페이로드 10MB |
| 종합계획서 §3.4 LOCK-MCP-04 | 동상 | Streamable HTTP MCP 2025-03-26 |
| 종합계획서 §3.4 LOCK-MCP-05 | 동상 | 최대 동시 서버 5 (Pool 운용 시 active 서버 제한) |
| 종합계획서 §3.4 LOCK-MCP-06 | 동상 | RetryPolicy max=3, factor=2.0 |
| 종합계획서 §3.4 LOCK-MCP-07 | 동상 | CircuitBreaker 5/60s/3 |
| 종합계획서 §3.4 LOCK-MCP-08 | 동상 | idle 10분 (Pool eviction 정책) |
| 종합계획서 §3.4 LOCK-MCP-10 | 동상 | **Connection Pool 최대 10 동시 연결 — 본 파일 정본** |
| 상세명세 §B-1 | `MCP_SERVER_CLIENT_상세명세.md` | 연결 관리 (Pool max 10) |
| 상세명세 §B-2 | 동상 | 연결 프로토콜 4단계 |
| 상세명세 §B-3 | 동상 | RetryPolicy + CircuitBreaker |
| 상세명세 §E-1 / §E-2 | 동상 | 글로벌 설정 / 라이프사이클 |
| `bridge_layer.md §5` | `03_connection-management/` | **acquire/release 인터페이스 정본 (본 파일 §3 인용)** |
| `bridge_layer.md §6 ~ §10` | 동상 | Streamable HTTP 클라이언트 + S0~S6 상태 + HTTP→McpError 매핑 |
| `connection_protocol.md §3` | 동상 | Stage 3 ToolList (Pool 진입 직전 단계) |
| `retry_circuit_breaker.md §7` | 동상 | **Pool 고갈 시 fallback 정책 (본 파일 §6.3 연동)** |
| `retry_circuit_breaker.md §13.1` | 동상 | SERVER_RETRY_OVERRIDES 인터페이스 |
| `retry_circuit_breaker.md §14.1 L1~L10` | 동상 | LOCK 지점 10개 (변경 금지) |
| `01_internal-tools/search_tools.md §2` | `01_internal-tools/` | McpError / ToolInvocationLog (재정의 금지) |
| `02_external-servers/development_servers.md §2.5 / §3.5` | 본 도메인 P1-6 | Filesystem / GitHub 라이프사이클 (Pool 슬롯 진입) |
| `02_external-servers/communication_servers.md §2.5 ~ §5.5` | 본 STEP_B 세션 2-3 | Slack/Drive/Notion/Linear 라이프사이클 (4 슬롯) |
| `02_external-servers/automation_servers.md §2.5 / §3.5` | 동상 | Postgres/Puppeteer 라이프사이클 (2 슬롯) |
| `04_payload-schema/tool_discovery.md §4.1` | 본 STEP_B 세션 2-2 | 캐시 키 (`server_id`) ↔ Pool slot 매핑 |
| `blue_node_bridge.md` | 본 STEP_B 세션 2-4 파트너 | Blue Node 연동 시 Pool 사용 |
| 6-12 Event-Logging | `6-12_event-logging/` | Pool 상태 메트릭 송출 |
| 6-13 Operations | `6-13_operations/` | 운영 런북 (Pool 고갈 대응) |

> **재정의 금지 항목**: `McpError` / `ToolInvocationLog` 정본 (`search_tools.md §2`). LOCK-MCP-10 Pool max=10 + LOCK-MCP-05 active 5 + LOCK-MCP-08 idle 10분 모두 인용만, 변경 0건.

---

## §2. Pool 정의

### §2.1 핵심 파라미터 (LOCK-MCP-10 정본)

| 파라미터 | 값 | 근거 |
|---------|-----|------|
| **max_connections** | 10 (전역) | LOCK-MCP-10 (상세명세 §B-1) |
| **max_active_servers** | 5 (동시 활성 서버) | LOCK-MCP-05 (상세명세 §E-1) |
| **idle_timeout_ms** | 600000 (10분) | LOCK-MCP-08 (상세명세 §E-2) |
| **max_lifetime_ms** | 3600000 (1시간) | 본 세션 정의 (장기 연결 안정성) |
| **health_check_interval_ms** | 30000 (30초) | 본 세션 정의 (모니터링 메트릭 exit_gate 핵심) |
| **acquire_timeout_ms** | 5000 (5초) | 본 세션 정의 (Pool 고갈 시 대기 한계) |
| **warmup_on_app_start** | true (AutoConnect 서버) | R-16-6 |

### §2.2 Pool 슬롯 매핑 (Phase 2 9 서버 누계)

| Slot # | 서버 ID | AutoConnect | LOCK-MCP-08 idle 적용 | 정의 위치 |
|--------|---------|-------------|----------------------|----------|
| 1 | filesystem | ✅ | ❌ (AutoConnect 제외) | development_servers §2 |
| 2 | github | ❌ On-demand | ✅ | development_servers §3 |
| 3 | brave_search | ❌ On-demand | ✅ | search_servers §3 |
| 4 | slack | ❌ On-demand | ✅ | communication_servers §2 |
| 5 | gdrive | ❌ On-demand | ✅ | communication_servers §3 |
| 6 | notion | ❌ On-demand | ✅ | communication_servers §4 |
| 7 | linear | ❌ On-demand | ✅ | communication_servers §5 |
| 8 | postgres | ❌ On-demand | ✅ | automation_servers §2 |
| 9 | puppeteer | ❌ On-demand | ✅ | automation_servers §3 |
| 10 | (on-demand 회전) | ❌ On-demand | ✅ | Phase 4 Sentry/Exa 등 11 서버가 on-demand 회전 (LOCK-MCP-10 10슬롯, LOCK-MCP-05 동시활성 5 — 배타 아님) |

> 9 서버 + 1 예비 슬롯 = 10 (LOCK-MCP-10 max). active 동시 5 제한 (LOCK-MCP-05) → 활성 5 + 대기/유휴 5 의 시나리오 가능.

---

## §3. acquire / release 인터페이스 (bridge_layer.md §5 정본 인용)

### §3.1 acquire(server_id, timeout_ms=5000)

```python
class McpConnectionPool:
    def acquire(self, server_id: str, timeout_ms: int = 5000) -> McpConnection:
        """
        지정 server_id 의 connection 을 획득. 5초 이내 미획득 시 timeout.

        근거: bridge_layer.md §5 정본 acquire 인터페이스.
        본 파일은 §5 인용만 수행, 인터페이스 시그니처/예외 처리 재정의 0건.
        """
        # Step 1: idle pool 에서 유휴 connection 검색 (server_id 일치)
        # Step 2: 없으면 신규 connection 생성 (active < max_active=5 조건)
        # Step 3: active=5 도달 + 모든 idle 비활성 → 5초 대기
        # Step 4: 대기 timeout → McpError(category="server_error", details.reason="pool_exhausted")  # bridge_layer §7.2 #b 정본
```

| 단계 | 동작 | 실패 시 |
|------|------|---------|
| 1. idle 검색 | 같은 `server_id` 의 idle connection 우선 재사용 | (없으면 step 2) |
| 2. 신규 생성 | active < 5 (LOCK-MCP-05) 조건 시 새 connection 생성 (Stage 1~3) | active=5 시 step 3 |
| 3. 대기 | 다른 connection release 또는 idle timeout (10분) 대기 | (시작 후 5s 초과 시 step 4) |
| 4. timeout | `McpError(category="server_error", details.reason="pool_exhausted")` | retry 0회 (즉시 fallback §6.3) |

### §3.2 release(connection)

```python
def release(self, conn: McpConnection) -> None:
    """
    connection 사용 종료, idle pool 로 반환.
    근거: bridge_layer.md §5 정본 release.
    """
    # Step 1: connection 상태 검증 (CB OPEN 시 idle pool 진입 거부, close 후 폐기)
    # Step 2: max_lifetime (1시간) 초과 시 close 후 폐기
    # Step 3: 정상 시 idle pool 로 이동, last_used 시각 갱신
```

| 단계 | 동작 |
|------|------|
| 1. 상태 검증 | CB OPEN / connection 오류 시 close 후 폐기 (idle pool 진입 거부) |
| 2. lifetime 검증 | `now - created_at > max_lifetime (1h)` 시 close 후 폐기 |
| 3. idle 진입 | 정상 시 idle pool, `last_used = now` 갱신 |

### §3.3 사용 예 (with-statement 권장)

```python
async with pool.acquire("github", timeout_ms=5000) as conn:
    response = await conn.call_tool("github.search_repositories", {"query": "vamos"})
# release 자동 호출 (with-exit)
```

---

## §4. 유휴 연결 재사용 정책

### §4.1 재사용 조건

idle pool 에서 connection 을 재사용하기 위해 다음 조건 모두 충족해야 한다:

1. `server_id` 일치.
2. `connection.state == Connected` (Stage 4 Ready 유지).
3. `now - last_used < idle_timeout (10분)` (LOCK-MCP-08).
4. `now - created_at < max_lifetime (1시간)`.
5. `circuit_breaker.state != OPEN` (LOCK-MCP-07).
6. 직전 health check 성공 (§5).

조건 1~6 중 하나라도 실패 시 해당 connection 을 close 후 폐기, 신규 생성 시도.

### §4.2 재사용 우선순위

같은 `server_id` 의 idle connection 이 복수 존재할 경우:

1. **LRU (Least Recently Used)**: `last_used` 가 가장 오래된 connection 우선 재사용 (장기 연결의 lifetime 분산).
2. **Health 점수**: 직전 health check 의 응답 시간이 빠른 connection 우선 (성능 최적화).

---

## §5. Health Check (30초 주기)

### §5.1 메커니즘

```python
async def health_check_loop(self):
    """
    30초마다 idle pool 의 모든 connection 에 대해 health check 수행.
    실패 connection 은 close 후 폐기 (재시도 없음, 다음 acquire 시 신규 생성).
    """
    while not self._shutdown:
        await asyncio.sleep(30)
        for conn in list(self.idle_pool):
            ok = await self._ping(conn, timeout_ms=2000)
            if not ok:
                self._evict(conn, reason="health_check_failed")
```

### §5.2 health check 구현 (서버별)

| 전송 | health check 메서드 | 타임아웃 |
|------|-------------------|---------|
| Streamable HTTP (gdrive) | `GET /mcp/health` 또는 `ping` JSON-RPC | 2s |
| stdio (filesystem/github/slack/notion/linear/postgres/puppeteer/brave_search) | `ping` JSON-RPC (서브프로세스 stdin) | 2s |

응답 부재 시 `health_check_failed` 카테고리 → eviction.

### §5.3 메트릭 송출 (모니터링 — exit_gate 핵심)

매 health check 주기 종료 시 6-12 Event-Logging 표준으로 다음 메트릭 송출:

```json
{
  "event": "mcp.pool.health_check",
  "timestamp": "2026-04-26T17:00:00Z",
  "trace_id": "trc_pool_hc_xxx",
  "metrics": {
    "pool_size": 10,
    "active_count": 3,
    "idle_count": 4,
    "evicted_this_cycle": 1,
    "evicted_reasons": {"health_check_failed": 1},
    "per_server": {
      "filesystem": {"active": 1, "idle": 0, "avg_latency_ms": 50},
      "github": {"active": 0, "idle": 1, "avg_latency_ms": 200},
      "gdrive": {"active": 1, "idle": 0, "avg_latency_ms": 800},
      "slack": {"active": 1, "idle": 1, "avg_latency_ms": 350}
    }
  }
}
```

본 메트릭은 **P2→3 exit_gate "모니터링 메트릭" 조건 충족의 핵심 증빙**이다.

---

## §6. Pool 고갈 시 fallback (retry_circuit_breaker.md §7 연동)

### §6.1 시나리오

active=5 (LOCK-MCP-05 상한 도달) + idle 0 + 신규 acquire 요청 5초 대기 만료.

### §6.2 fallback 흐름

```
1. acquire timeout (5s)
2. McpError(category="server_error", details.reason="pool_exhausted") 반환
3. retry_circuit_breaker.md §7 fallback 정책 호출
4. fallback 종류:
   a. 내부 도구 대체 (예: Filesystem 외부 → code_tools.md §4 file_read)
   b. 직접 API 호출 (예: GitHub MCP → REST API)
   c. 큐 적재 (write 작업, 5분 후 재시도)
   d. manual_review 에스컬레이션 (CB OPEN 등 critical)
5. trace_id 전파 + ToolInvocationLog 기록 (recovery.action="fallback")
```

### §6.3 fallback 미지원 도구

일부 도구는 fallback 경로 부재 — `manual_review` 즉시 에스컬레이션:

| 도구 | fallback 부재 사유 |
|------|------------------|
| `puppeteer.evaluate` | 브라우저 sandbox 외 직접 JS 실행 불가 |
| `slack.search_messages` | Slack API 직접 검색은 별도 권한 필요, 사용자 확인 우선 |
| `notion.update_page` | 데이터 무결성 위험, manual_review |

---

## §7. Pool 워밍업 (앱 시작 시)

### §7.1 워밍업 트리거

1. 앱 시작 시 AutoConnect 서버 (현재 Filesystem 1개) 즉시 acquire 시도 → idle pool 진입.
2. tool_discovery.md §8.1 캐시 워밍 트리거와 동시 진행.
3. 사용자 명시 워밍 (관리 UI, Phase 3 v12_C05_098 이관).

### §7.2 워밍업 실패 처리

AutoConnect 서버 워밍업 실패 (Stage 1~3 timeout) 시:
- 로그 기록 (`event="mcp.pool.warmup_failed"`).
- CB +1 (다른 서버 활성에 영향 없음).
- 다음 도구 호출 시 신규 acquire 시도.

---

## §8. Pool eviction 트리거

다음 조건 중 하나 만족 시 connection eviction (close 후 폐기):

| 트리거 | 조건 | 사유 |
|--------|------|------|
| **idle timeout** | `now - last_used > 10분` | LOCK-MCP-08 |
| **max lifetime** | `now - created_at > 1시간` | 장기 연결 안정성 |
| **health check 실패** | §5 ping 실패 | 연결 손상 |
| **CB OPEN** | `circuit_breaker.state == OPEN` | LOCK-MCP-07 |
| **explicit close** | acquire/release 사이클 외 명시적 close | 운영 명령 |

---

## §9. 메트릭 카탈로그 (모니터링 exit_gate 핵심)

본 파일이 6-12 Event-Logging 표준으로 송출하는 Pool 메트릭 카탈로그:

| 메트릭 이름 | 단위 | 의미 |
|-----------|------|------|
| `mcp.pool.size` | gauge | Pool 최대 (10 고정, LOCK-MCP-10) |
| `mcp.pool.active` | gauge | 현재 active connection 수 |
| `mcp.pool.idle` | gauge | 현재 idle connection 수 |
| `mcp.pool.acquire.latency_ms` | histogram | acquire 호출 응답 시간 |
| `mcp.pool.acquire.timeout_total` | counter | acquire timeout (5s 초과) 누적 |
| `mcp.pool.eviction.total` | counter | eviction 누적 (사유별 라벨) |
| `mcp.pool.health_check.success_rate` | gauge | health check 성공률 (최근 100 cycle) |
| `mcp.pool.per_server.active{server_id}` | gauge | 서버별 active count |
| `mcp.pool.per_server.idle{server_id}` | gauge | 서버별 idle count |
| `mcp.pool.per_server.avg_latency_ms{server_id}` | gauge | 서버별 평균 응답 시간 |
| `mcp.pool.warmup.failed_total` | counter | 워밍업 실패 누적 |
| `mcp.pool.fallback.invoked_total` | counter | fallback 발동 누적 (사유별 라벨) |

---

## §10. LOCK / CONFLICT 점검

### §10.1 LOCK 준수 (변경 0건)

| LOCK | 본 세션 관련 | 변경 여부 |
|------|-------------|-----------|
| LOCK-MCP-01 10MB | acquire/release 페이로드 영향 없음 | 참조만 ✅ |
| LOCK-MCP-04 Streamable HTTP | §5.2 health check (HTTP 서버) | 참조만 ✅ |
| LOCK-MCP-05 동시 서버 5 | §3.1 acquire step 2 active < 5 조건 | 참조만 ✅ |
| LOCK-MCP-06 RetryPolicy | §6 fallback 흐름 retry 정책 (overrides §13.1) | 참조만 ✅ |
| LOCK-MCP-07 CircuitBreaker | §4.1 재사용 조건 5 + §8 eviction CB OPEN | 참조만 ✅ |
| LOCK-MCP-08 idle 10분 | §2.1 idle_timeout_ms / §4.1 재사용 조건 3 / §8 eviction | 참조만 ✅ |
| **LOCK-MCP-10 Pool max 10** | **§2.1 max_connections=10 정본 (본 파일 정의 정점)** | 참조만 ✅ |
| `retry_circuit_breaker.md §14.1 L1~L10` | 변경 0건 | 참조만 ✅ |

### §10.2 CONFLICT 후보

| 후보 | 판정 | 근거 |
|------|------|------|
| Pool max 10 vs active 5 (LOCK-MCP-10 vs LOCK-MCP-05) | 후보 아님 | 의도적 차이. 10 = 총 슬롯 (idle 포함), 5 = 동시 활성 한도. §2.2 슬롯 매핑 명시 |
| max_lifetime 1시간 vs LOCK-MCP-08 idle 10분 | 후보 아님 | 두 정책 동시 적용 (§4.1 재사용 조건 3+4) |
| AutoConnect filesystem idle 미적용 vs LOCK-MCP-08 | 후보 아님 | development_servers §2.5 명시 (AutoConnect 서버는 idle 적용 외) |
| health_check 30s 주기 vs idle 10분 | 후보 아님 | 30s 마다 health check, idle 10분은 마지막 사용 시각 기준 |
| Pool 고갈 시 timeout=5s vs LOCK-MCP-06 max=3 retry | 후보 아님 | acquire timeout 은 Pool 슬롯 대기, retry 는 도구 호출 단위 (다른 layer) |

`[INTERFACE_MISMATCH]` 0건 / `[LOCK_CHANGE_NEEDED]` 0건 / `[CONFLICT_CANDIDATE]` 0건.

---

## §11. Phase 2 통합 테스트 시나리오 (≥10건)

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | T-CP-01 | 앱 시작 → filesystem 워밍업 | idle pool 1 connection (filesystem) |
| 2 | T-CP-02 | github 도구 호출 → acquire | active +1, idle pool 0 |
| 3 | T-CP-03 | 같은 server_id 재호출 (LRU 재사용) | idle 에서 재사용, 신규 생성 0 |
| 4 | T-CP-04 | 5 서버 동시 활성 + 6번째 acquire | 5초 대기 → release 발생 시 진행 또는 timeout |
| 5 | T-CP-05 | 10분 idle 경과 → eviction | LOCK-MCP-08 적용, idle pool 0 |
| 6 | T-CP-06 | 1시간 max_lifetime 초과 connection | release 시점 폐기, 신규 acquire 시 새 connection |
| 7 | T-CP-07 | health check 30s 주기 ping 실패 | eviction, 다음 acquire 시 신규 |
| 8 | T-CP-08 | CB OPEN 상태 connection idle pool 진입 거부 | release 시 close, idle pool 0 |
| 9 | T-CP-09 | acquire timeout 5s 초과 | server_error (`pool_exhausted`), fallback 발동 |
| 10 | T-CP-10 | filesystem 외부 fallback → code_tools file_read | fallback 성공, recovery.action="fallback" |
| 11 | T-CP-11 | puppeteer.evaluate fallback 미지원 | manual_review 에스컬레이션 |
| 12 | T-CP-12 | health check 메트릭 송출 (30s 주기) | mcp.pool.health_check event 6-12 표준 |
| 13 | T-CP-13 | Phase 3 10번째 슬롯 사용 | Sentry 또는 Exa 진입, max=10 도달 |

---

## §12. 검증 체크리스트 (P2 #6 게이트)

- [x] LOCK-MCP-10 Pool max=10 정본 인용 (§2.1)
- [x] LOCK-MCP-05 active 5 제약 acquire 단계 검증 (§3.1)
- [x] LOCK-MCP-08 idle 10분 eviction (§8)
- [x] max_lifetime 1시간 (§2.1 / §4.1 / §8)
- [x] health check 30s 주기 (§5)
- [x] acquire/release 인터페이스 bridge_layer.md §5 정본 인용 (§3)
- [x] 유휴 재사용 정책 (LRU + Health 우선순위) (§4)
- [x] 워밍업 (AutoConnect filesystem) (§7)
- [x] Pool 고갈 시 fallback retry_circuit_breaker.md §7 연동 (§6)
- [x] 메트릭 카탈로그 12 메트릭 (§9) — **모니터링 exit_gate 핵심 충족**
- [x] 9 서버 슬롯 매핑 + Phase 3 10번째 슬롯 (§2.2)
- [x] 공통 자료 구조 (search_tools §2) 재정의 0건
- [x] Phase 2 통합 테스트 시나리오 13건 (≥10 충족)

---

## §13. 세션 간 인터페이스 cross-check

| 후속 세션/파일 | 본 파일 소비 지점 | 변경 금지 |
|---------------|-----------------|-----------|
| **blue_node_bridge.md (본 STEP_B 파트너)** | §3 acquire/release → Blue Node Bridge 호출 시 사용 | LOCK-MCP-10 max 10 |
| **6-13 Operations 런북** | §9 메트릭 카탈로그 → 알림 임계 정의 | 메트릭 이름 |
| **6-12 Event-Logging** | §5.3 / §9 mcp.pool.* event 송출 | event 이름 (정본) |
| **Phase 3 Sentry/Exa** | §2.2 10번째 예비 슬롯 진입 | LOCK-MCP-10 (10 상한 불변) |

---

## §14. 본 파일 LOCK 지점

| # | LOCK 지점 | 섹션 | 변경 조건 |
|---|-----------|------|----------|
| L-CP-1 | max_connections=10 정본 | §2.1 | LOCK-MCP-10 변경 시만 (AUTHORITY §3.4) |
| L-CP-2 | max_active_servers=5 | §2.1 | LOCK-MCP-05 변경 시만 |
| L-CP-3 | idle_timeout_ms=600000 (10분) | §2.1 | LOCK-MCP-08 변경 시만 |
| L-CP-4 | max_lifetime_ms=3600000 (1시간) | §2.1 | 본 세션 정의, 운영 튜닝 가능 |
| L-CP-5 | health_check_interval_ms=30000 (30초) | §2.1 | 운영 튜닝 가능 |
| L-CP-6 | acquire_timeout_ms=5000 (5초) | §2.1 | 운영 튜닝 가능 |
| L-CP-7 | acquire/release 인터페이스 시그니처 | §3 | bridge_layer.md §5 변경 시만 |
| L-CP-8 | 메트릭 카탈로그 12 메트릭 이름 | §9 | 6-12 Event-Logging 표준 변경 시만 |
| L-CP-9 | 9 서버 슬롯 매핑 | §2.2 | 신규 서버 진입 시 row 추가 (Phase 3 Sentry/Exa) |
| L-CP-10 | fallback 미지원 도구 3건 | §6.3 | 운영 정책 변경 시만 |

---

## §15. 자가 체크리스트 (FABRICATION 방지)

- [x] 모든 LOCK-MCP-XX 인용은 AUTHORITY_CHAIN.md §3.4 정본과 1:1 일치
- [x] acquire/release 인터페이스는 bridge_layer.md §5 정본 인용 (재정의 0건)
- [x] 9 서버 슬롯 매핑은 development_servers / search_servers / communication_servers / automation_servers 정본 매핑
- [x] FABRICATION 마커 census 0 hits (placeholder/TODO/TBD/`...` prose 0건)

---

## §16. 변경 이력

| 날짜 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-26 | 신규 작성 — Connection Pool 최적화 (LOCK-MCP-10 max=10 + LOCK-MCP-05 active 5 + LOCK-MCP-08 idle 10분 + max_lifetime 1h + health_check 30s + acquire/release + 워밍업 + 9 서버 슬롯 매핑 + 12 메트릭 카탈로그 + 13 테스트). **모니터링 메트릭 exit_gate 핵심 충족**. | 2-4 (Phase 2 V2-Phase 2) |
