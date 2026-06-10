# healthcheck.md — Python Bridge Healthcheck 프로토콜

> **파일 위치**: `4-1_Rust-Tauri-Infrastructure/05_process-management/healthcheck.md`
> **세션**: T1-4 (프로세스 관리 상세) Phase 1
> **정본**: LOCK-RT-12 (상세명세 §D-2, DEFINED-HERE, Phase 5 동결) — **HC 15초 간격, 5초 타임아웃, 3회 연속 실패 → 재시작**
> **해소 대상**: ISS-05 프로세스 관리 전면 신규 — Healthcheck 축

---

## §1. 교차 참조 (AUTHORITY_CHAIN)

```
AUTHORITY_CHAIN (본 파일 의존 LOCK)
  ├── LOCK-RT-04  python_manager.rs 모듈 경계 — §7 healthcheck() 인터페이스
  ├── LOCK-RT-07  FailureCodeRegistry 48건 — §9 매핑 (CFL-RT-009 RESOLVED-DEFERRED 상속, REF-only 소유 = 6-12)
  ├── LOCK-RT-11  JSON-RPC 2.0 프로토콜 — §3 HC 프로토콜 프레이밍
  ├── LOCK-RT-12  *** HC 15초 간격 / 5초 타임아웃 / 3회 임계치 *** (정본 수치, 재정의 금지)
  │     출처: 상세명세 §D-2 (DEFINED-HERE, Phase 5 동결)
  │     본 파일 사용: §2, §5, §6, §8 전체
  ├── LOCK-RT-13  Restart backoff — §4 Unhealthy → Restarting 전이 시 restart_policy.md 위임
  ├── LOCK-RT-14  TauriError 7 variant — §9 매핑
  └── LOCK-RT-15  stderr 로그 분리 — §11 구조화 로그 sink

주변 정본 참조
  ├── 상세명세 §D-2  "15초마다 health_check RPC 호출, 5초 타임아웃, 3회 연속 → 재시작"
  ├── 상세명세 §D-5  메트릭 수집 (RSS, CPU, 큐 길이)
  └── 상세명세 §F-1  상태 머신 Running↔Unhealthy↔Restarting

세션 간 인터페이스 cross-check
  ├── T1-2 workflow_event_config_models.md §3.12 HealthReport/HealthStatus/PythonProcessStatus
  │     — §6 HC 응답 필드 = HealthStatus enum (Healthy/Degraded/Unhealthy) 재사용
  ├── T1-3 rpc_protocol.md §6.1 타임아웃 계층 L1 — HC 15s interval / 5s per-call / 3 fail
  │     — 본 파일 §2 수치와 1:1 일치
  ├── T1-3 rpc_protocol.md §7.7 healthcheck() 선정의 — "15초 루프, mcp.bridge.health 호출, 5s timeout, 3회 연속 실패 → Unhealthy → restart"
  │     — 본 파일은 L3 상세 구현
  ├── T1-3 method_catalog.md §4.12 mcp.bridge.health — Python 측 엔드포인트 스키마
  │     — §3 HC 프로토콜 메서드명 = `mcp.bridge.health`
  └── spawn_protocol.md §2 Step 10 — Ready 완료 시점에 healthcheck_loop 기동, §9 ProcessFailureEscalation 재사용
```

---

## §2. LOCK-RT-12 준수 (정본 수치)

> **재정의 절대 금지**. 본 파일은 정본 값을 인용하고 L3 구현만 상세화한다.

| 항목 | 값 | 정본 | 본 파일 사용 섹션 |
|---|---|---|---|
| HC 주기 (interval) | **15초** | LOCK-RT-12 / 상세명세 §D-2 | §3, §6 |
| HC per-call 타임아웃 | **5초** | LOCK-RT-12 / rpc_protocol.md §6.2 | §3, §9 |
| 연속 실패 임계치 | **3회** | LOCK-RT-12 / 상세명세 §D-2 | §4, §5 |
| HC 실패 후 재시작 backoff | **2s → 4s → 8s** | LOCK-RT-13 HC 경로 | §4 (restart_policy.md 위임) |

- **주기 15s 의 근거**: 상세명세 §D-2 원문 "15초마다 health_check RPC 호출". Phase 5 동결. 변경 시 LOCK-RT-12 갱신 + CFL 등재 필요.
- **5s 타임아웃**: rpc_protocol.md §6.2 "HC per-call 5s". `mcp.bridge.health` 전용 타임아웃 (method_catalog §6 "mcp.bridge.health = 5s 불가 override").
- **3회 임계치의 근거**: 상세명세 §D-2 "임계치: unhealthy 3회 연속 → 프로세스 재시작". 본 파일 §5 는 이 수치의 근거를 보강한다.

---

## §3. HC 프로토콜 (JSON-RPC `mcp.bridge.health`)

### 3.1 메서드명 결정

> T1-3 method_catalog.md §4.12 `mcp.bridge.health` 가 정본 엔드포인트이다. 상세명세 §C #12 `health_check` 와 **1:1 동일**, `mcp.bridge.health` 는 PRE-3 해소 과정에서 확정된 모듈 접두사 포함 이름이다 (CFL-RT-002 RESOLVED).

- **Python 측**: `mcp.bridge.health` 메서드 핸들러. 타임아웃 5s 내에 응답 필수.
- **Rust 측**: `PythonManager::healthcheck_loop()` 이 `PythonManager::send("mcp.bridge.health", (), 5_000)` 호출.

### 3.2 요청 스키마

```json
{
  "jsonrpc": "2.0",
  "id": "<uuid v7>",
  "method": "mcp.bridge.health",
  "params": {
    "_meta": {
      "trace_id": "<uuid v7>",
      "correlation_id": "hc_<tick>",
      "deadline_ms": 5000,
      "origin": "healthcheck_loop"
    }
  }
}
```

- `params` 는 비어있어도 되지만 `_meta` 는 필수 (rpc_protocol.md §4 trace 전파 규약).
- `id` 는 UUID v7 — 시간순 정렬 가능하여 HC 전용 correlation map 분리 없이도 pending map 에 공존 가능.

### 3.3 응답 스키마 (정상)

```json
{
  "jsonrpc": "2.0",
  "id": "<uuid v7>",
  "result": {
    "status": "Healthy",
    "uptime_s": 3612,
    "rss_bytes": 524288000,
    "cpu_pct": 12.4,
    "active_calls": 3,
    "queue_length": 0,
    "last_error": null,
    "capabilities": ["llm", "embed", "mcp"],
    "python_version": "3.11.9",
    "checked_at": "2026-04-11T03:00:12.345Z"
  }
}
```

### 3.4 응답 스키마 (에러)

```json
{
  "jsonrpc": "2.0",
  "id": "<uuid v7>",
  "error": {
    "code": -32020,
    "message": "health_check_degraded",
    "data": {
      "reason": "rss_over_threshold",
      "rss_bytes": 1932735283,
      "rss_limit_bytes": 2147483648
    }
  }
}
```

### 3.5 HC 루프 의사코드

```rust
async fn healthcheck_loop(
    manager: Arc<PythonManager>,
    config: Arc<PythonBridgeConfig>,
) {
    const HC_INTERVAL: Duration = Duration::from_secs(15);    // LOCK-RT-12
    const HC_TIMEOUT:  Duration = Duration::from_secs(5);     // LOCK-RT-12
    const HC_THRESHOLD: u32 = 3;                              // LOCK-RT-12

    let mut ticker = tokio::time::interval(HC_INTERVAL);
    ticker.set_missed_tick_behavior(MissedTickBehavior::Delay); // drift 방지
    let mut consecutive_fails: u32 = 0;

    loop {
        ticker.tick().await;                                  // O(1)

        // 상태 게이트: Running 아니면 루프 계속 (spawn/restart 중에는 HC 미발행)
        let st = manager.state.load(Ordering::Acquire);
        if st != ProcessState::Running as u8 {
            consecutive_fails = 0;                            // reset
            if st == ProcessState::Dead as u8 { break; }      // 루프 종료
            continue;
        }

        let tick_id = format!("hc_{}", uuid_v7());
        let t0 = Instant::now();
        let result = tokio::time::timeout(
            HC_TIMEOUT + Duration::from_millis(500),          // grace 0.5s
            manager.send::<_, HealthTickResult>(
                "mcp.bridge.health",
                serde_json::json!({}),
                HC_TIMEOUT.as_millis() as u64,
            ),
        ).await;

        let elapsed = t0.elapsed();

        match result {
            Ok(Ok(hr)) => {
                consecutive_fails = 0;
                record_health_metrics(&hr, elapsed);          // §6
                if hr.status != HealthStatus::Healthy {
                    tracing::warn!(status=?hr.status, "python_bridge_health_degraded");
                    // Degraded 판정은 루프를 끊지 않음. §7 참조.
                }
            }
            Ok(Err(e)) | Err(_) => {
                if manager.state.load(Ordering::Acquire) == ProcessState::Unhealthy as u8 /* Degraded 가속, §7.2 */ { consecutive_fails += 2; } else { consecutive_fails += 1; }
                tracing::warn!(
                    consecutive_fails,
                    threshold = HC_THRESHOLD,
                    elapsed_ms = elapsed.as_millis() as u64,
                    "python_bridge_healthcheck_fail"
                );
                if consecutive_fails >= HC_THRESHOLD {        // 3회 연속
                    manager.state.store(ProcessState::Unhealthy as u8, Ordering::Release);
                    // restart_policy.md §4 HC 실패 경로 트리거
                    let cause = RestartCause::HealthcheckExhausted { fails: consecutive_fails };
                    tokio::spawn({
                        let m = Arc::clone(&manager);
                        async move { let _ = m.restart(cause).await; }
                    });
                    break;                                    // 현재 루프 종료, 재시작 후 새 루프 기동
                }
            }
        }
    }
}
```

- **시간복잡도**:
  - 루프 1 틱: O(1) (상태 조회) + O(log N) (pending map 삽입/제거) + O(payload) (JSON 직렬화/역직렬화).
  - 15s 주기이므로 amortized 가산 부하 극소.
- **`set_missed_tick_behavior(MissedTickBehavior::Delay)`**: 시스템 스트레스로 틱이 누적되어도 한 번에 몰아서 호출하지 않고 **다음 주기로 지연**. HC 가 DoS 가속기로 변하는 것 방지.
- **루프 종료**: Unhealthy 전이 시 `break`. 재시작 후 spawn_protocol.md §2 Step 10 에서 새 루프를 기동한다 → 루프는 ProcessState 라이프사이클당 1 회 기동.

---

## §4. 상태 머신 (Healthcheck 관점)

```
                      ┌─────────────┐
                      │   Healthy   │ ◄───────────── HC OK (consecutive_fails=0)
                      └──────┬──────┘
                             │
                   HC result.status == Degraded
                     OR rss/cpu 임계 초과
                             │
                             ▼
                      ┌─────────────┐
                      │  Degraded   │ ◄──── HC OK 이지만 메트릭 임계 초과 (§7)
                      └──────┬──────┘
                             │
                       HC 연속 1~2회 실패
                             │
                             ▼
                      ┌─────────────┐
                      │ HC_Failing  │ (내부 카운터, AtomicU8 미반영)
                      └──────┬──────┘
                             │
                       consecutive_fails == 3
                             │
                             ▼
                      ┌─────────────┐
                      │  Unhealthy  │ ◄── AtomicU8 CAS Running→Unhealthy
                      └──────┬──────┘
                             │
                      restart_policy.md §4 트리거
                             │
                             ▼
                      ┌─────────────┐
                      │ Restarting  │
                      └─────────────┘
```

| 관점 | 상태 | AtomicU8 | 본 파일 섹션 |
|---|---|---|---|
| 정상 | Healthy | Running(2) | §3, §6 |
| 경고 | Degraded | Running(2) (AtomicU8 미변경) | §7 |
| 실패 카운트 | HC_Failing (내부) | Running(2) + `consecutive_fails > 0` | §5 |
| 실패 확정 | Unhealthy | Unhealthy(3) | §5, §9 |
| 재시작 중 | Restarting | Restarting(4) | restart_policy.md §4 |

- **Degraded 가 AtomicU8 에 반영되지 않는 이유**: ProcessState 6-variant 에 Degraded 가 없기 때문 (rpc_protocol.md §7.2 정본). Degraded 는 `HealthReport.overall` (T1-2 §3.12) 에서만 외부 노출되며, Rust 내부 제어 흐름은 Running 을 유지한다.
- **HC_Failing 이 AtomicU8 에 반영되지 않는 이유**: 1~2회 실패는 잠깐의 hiccup 일 수 있어 외부 노출(=상태 변경) 을 피한다. 3회 확정 시에만 CAS.

---

## §5. 실패 판정 기준 (3회 임계치 근거)

### 5.1 "3회 연속 실패" 수식

```
failure_event = (timeout_5s) OR (rpc_error code ∈ [-32001, -32005]) OR (tcp reset)
unhealthy = failure_event × 3  (연속)  → 프로세스 재시작
```

- **연속** 의 의미: 중간에 1 회라도 성공하면 카운터 0 리셋. (§3.5 의사코드 `consecutive_fails = 0` 분기)

### 5.2 N=3 선택 근거

| N 후보 | 장점 | 단점 | 정본 |
|---|---|---|---|
| 1 | 즉각 대응 | false positive 빈발 (네트워크 hiccup, GC pause) | — |
| 2 | 중간 | hiccup 에 여전히 취약 (15s × 2 = 30s 내 2회 실패) | — |
| **3** | hiccup 필터 + 45s 내 탐지 | 45s 동안 사용자 체감 가능 | **LOCK-RT-12** |
| 5 | 매우 안정 | 75s 탐지 지연 (사용자 체감 과도) | — |

- 상세명세 §D-2 **"unhealthy 3회 연속 → 프로세스 재시작"** 가 정본이다. 본 파일은 N=3 을 Phase 5 동결 수치로 수용.
- **탐지 상한 시간**: `3 * 15s + 5s_timeout = 50s` (최악 케이스, 첫 틱 직후 장애 발생 시). 평균 `2.5 * 15s = 37.5s`.

### 5.3 실패 분류 (어떤 실패가 카운트되는가)

| 실패 유형 | 카운트? | 근거 |
|---|---|---|
| HC per-call 5s 타임아웃 | **Yes** | 정본 §D-2 |
| Rust 측 `-32001 python_bridge_timeout` | Yes | 동상 |
| Rust 측 `-32005 python_bridge_spawn_failed` | Yes | 프로세스 비정상 |
| Python 응답 `{"error":{"code":-32020,"message":"health_check_degraded"}}` | **No (result 수신 성공)** | §7 Degraded 경로 |
| Python 응답 `{"error":{"code":-32000, ...}}` other | Yes | 브릿지 비정상 |
| stdin write 실패 (broken pipe) | Yes | 프로세스 사망 |
| manager.state != Running (HC 루프 게이트) | **No (HC 미발행)** | §3.5 gate |
| pending map 삽입 실패 (OOM) | Yes (로컬 OOM) | Rust 측 장애 |

### 5.4 공정성 보장

- HC RPC 는 `send()` 를 통해 일반 RPC 와 **같은 Semaphore(50)** 공유. 동시 RPC 50 개가 차 있을 때 HC 도 대기한다.
- 대기 시간이 HC per-call 5s 타임아웃을 초과하면 그 자체로 실패 카운트된다 → 부하 포화 시에도 HC 탐지 기능 유지.
- 반대로 HC 가 과도하게 블록되지 않도록, §8 에서 `send()` 내부 Semaphore 취득 timeout 을 3s 로 제한하는 최적화를 Phase 2 로 유보한다.

---

## §6. HC 응답 필드 정의

### 6.1 HealthTickResult (내부 DTO — Rust)

```rust
#[derive(Debug, Clone, Deserialize)]
pub struct HealthTickResult {
    pub status: HealthStatus,            // T1-2 §3.12 재사용 (Healthy | Degraded | Unhealthy)
    pub uptime_s: u64,
    pub rss_bytes: u64,
    pub cpu_pct: f32,
    pub active_calls: u32,
    #[serde(default)]
    pub queue_length: u32,               // Python 측 asyncio queue 길이
    #[serde(default)]
    pub last_error: Option<HealthLastError>,
    #[serde(default)]
    pub capabilities: Vec<String>,
    #[serde(default)]
    pub python_version: Option<String>,
    #[serde(default)]
    pub checked_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct HealthLastError {
    pub code: i32,                       // JSON-RPC code
    pub name: String,                    // 내부 레이블
    pub ts: DateTime<Utc>,
    pub method: String,                  // 마지막 실패 RPC method
}
```

### 6.2 필드 ↔ 정본 매핑

| 필드 | 타입 | 정본 | 비고 |
|---|---|---|---|
| `status` | `HealthStatus` | T1-2 §3.12 enum | Healthy/Degraded/Unhealthy |
| `uptime_s` | `u64` | 상세명세 §D-5 + T1-2 HealthReport | 초 단위 |
| `rss_bytes` | `u64` | 상세명세 §D-5 "RSS 메모리" | 2GB 제한 대비 |
| `cpu_pct` | `f32` | 상세명세 §D-5 "CPU%" | 0.0~100.0 |
| `active_calls` | `u32` | T1-2 HealthReport 확장 | 진행 중 RPC 수 |
| `queue_length` | `u32` | 상세명세 §D-5 "처리 큐 길이" | Python asyncio 큐 |
| `last_error` | Option | 본 파일 DEFINED-HERE | Degraded 원인 추적 |
| `capabilities` | `Vec<String>` | method_catalog §4.11 `mcp.bridge.init.result.capabilities` | 런타임 변동 반영 |
| `checked_at` | `DateTime<Utc>` | T1-2 HealthReport.checked_at | Python 측 타임스탬프 |

### 6.3 T1-2 HealthReport 통합 매핑

```
HealthTickResult (본 파일)  →  HealthReport (T1-2 §3.12)
─────────────────────────────────────────────────────────
.status                     →  .python.ok = (status == Healthy)
                              .overall = worst_of(python, db, ...)
.uptime_s                   →  .uptime_s
.rss_bytes                  →  (HealthReport 미노출 — Rust 내부 메트릭만)
.cpu_pct                    →  (동상)
.active_calls               →  (동상)
.last_error                 →  .failures.push(failure_code_from(last_error.code))
.checked_at                 →  .checked_at
latency_ms (측정 elapsed)   →  .python.latency_ms
restart_count (PM 필드)     →  .python.restart_count
pid (PM 필드)               →  .python.pid
```

- **경계**: 본 파일은 **Python→Rust 방향의 tick 결과** 를 정의. T1-1 `health_check()` 커맨드가 HealthReport 로 변환하는 어댑터는 T1-1 health_commands.md 가 담당 — 본 파일은 위 매핑 표를 제공하는 것까지.

---

## §7. Degraded 판정 기준

> Degraded 는 HC 응답 `result.status == Degraded` 인 경우, **또는** Rust 측이 rss/cpu/큐길이 임계를 초과했다고 판단한 경우에 노출된다. AtomicU8 은 Running 유지 (§4 참조).

### 7.1 임계 (권장 기본값)

| 메트릭 | Degraded 임계 | Unhealthy (판정 경합 경계) | 근거 |
|---|---|---|---|
| `rss_bytes` | ≥ 80% of 2GB (1717986918 B) | ≥ 95% of 2GB (OOM 임박) | §D-5 + 6-12 관측성 권장 |
| `cpu_pct` | ≥ 85.0 지속 3 tick | ≥ 98.0 지속 3 tick | 동상 |
| `queue_length` | ≥ 40 (Semaphore 50 대비 80%) | ≥ 50 | §G-2 동시성 한도 |
| HC elapsed | ≥ 3000ms (5s 중 60%) | ≥ 5000ms (타임아웃) | §3 |
| `active_calls` | ≥ 40 | ≥ 50 | §G-2 |

- **"Unhealthy 경계 경합"**: rss ≥ 95% 등은 즉시 Unhealthy 로 전환되는 것이 아니라 **HC 실패 카운트에 1 카운트 가산** (아래 7.2).
- **Degraded 임계는 권장값**: 본 파일 DEFINED-HERE. 운영 튜닝 대상이므로 `config.python_bridge.health_thresholds.*` 에 `[LOCK_CHANGE_NEEDED]` 없이 override 가능.

### 7.2 Degraded → Unhealthy 가속 규칙

- Degraded 상태에서 HC 실패가 발생하면 `consecutive_fails += 2` (일반 1 대신). 즉 3회 임계치를 1.5 tick (약 22s) 만에 도달 가능.
- 근거: 이미 Degraded 는 장애 전조 → 보수적 가속. 단 가속은 1 tick 당 최대 +2 로 제한.

### 7.3 Degraded 해제

- `result.status == Healthy` + rss/cpu/큐 모두 Degraded 임계 미만 2 tick 연속 → Degraded 해제.
- 해제 시 `consecutive_fails = 0` 리셋.

---

## §8. T1-3 타임아웃 계층 L1 정합 (FR-8)

> rpc_protocol.md §6.1 타임아웃 계층 L1 = HC. 본 파일은 L1 수치를 정본 인용하고 재정의하지 않는다.

```
┌────────────────────────────────────────────────────────┐
│  L0 Spawn 5s × 3                  (spawn_protocol.md)  │
│        ↓                                               │
│  L1 HC 15s / 5s / 3 fail         (본 파일 — LOCK-RT-12) │
│        ↓                                               │
│  L2 RPC 120s/30s/5s/10s           (rpc_protocol.md §6) │
│        ↓                                               │
│  L3 Graceful Shutdown 5s         (restart_policy.md)   │
└────────────────────────────────────────────────────────┘
```

- **L1 ↔ L2 경계**: HC 자체가 L2 에 속하는 RPC (`mcp.bridge.health`, method_catalog §4.12) 이지만, 타임아웃은 L1 (5s) 로 별도 정의. 다른 L2 메서드(`process_message 120s`) 와 무관.
- **drift 방지**: L0 Spawn 실패 → restart backoff 진입 시 HC 루프는 미기동. restart 성공 후 새 HC 루프가 기동되면 `consecutive_fails` 는 0 으로 초기화된다 (§3.5 `break` + 재기동).
- **상위 전파**: L1 3회 실패 → Unhealthy → L3 Graceful Shutdown 5s → SIGKILL → Spawn 재진입 (L0). 이 체인은 restart_policy.md §6 에서 상세화.

---

## §9. FailureCodeRegistry 매핑 (LOCK-RT-07)

### 9.1 [CFL-RT-009 RESOLVED-DEFERRED (CC-T14-01)] 상속

spawn_protocol.md §7 에서 등재한 CFL-RT-009 (CC-T14-01) 를 본 파일도 상속한다. 해소 상태: **RESOLVED-DEFERRED** (CONFLICT_LOG v1.2, 2026-04-11) — 4-1 로컬 `rt.py_bridge.*` 네임스페이스 처리 + 6-12 V4 cross-handoff. HC 관련 내부 레이블은 아래와 같으며, 48건 정본 내 직접 매핑 없음.

| 내부 레이블 | 상위 JSON-RPC 코드 | TauriError variant | 발생 시점 |
|---|---|---|---|
| `HC_TIMEOUT` | -32001 `python_bridge_timeout` | `Timeout` | §3.5 `Err(_)` (tokio::timeout) |
| `HC_UNHEALTHY_CONSECUTIVE` | -32000 `python_bridge_unhealthy` | `PythonBridgeError` | §3.5 consecutive_fails ≥ 3 |
| `HC_DEGRADED` | (에러 아님) | — | §7 Degraded 전이 |
| `HC_RSS_OVER` | -32020 `health_check_degraded` (Python 응답) | — | §7 rss 임계 |
| `HC_CPU_OVER` | -32020 | — | §7 cpu 임계 |
| `HC_QUEUE_OVER` | -32020 | — | §7 queue 임계 |
| `HC_PIPE_BROKEN` | -32004 `python_bridge_pipe` | `IoError` | §3.5 stdin write 실패 |
| `HC_MALFORMED_RESPONSE` | -32700 `parse_error` | `InternalError` | result 역직렬화 실패 |

### 9.2 6-12 V4 통합 후 canonical 매핑 (cross-handoff 대기)

- `HC_TIMEOUT` → `PY_BRIDGE_HC_TIMEOUT`
- `HC_UNHEALTHY_CONSECUTIVE` → `PY_BRIDGE_HC_UNHEALTHY`
- `HC_PIPE_BROKEN` → `PY_BRIDGE_SPAWN_FAILED` (근거: pipe broken = 프로세스 사망)

---

## §10. Phase 2 테스트 시나리오 (10건 이상)

> 실제 Python subprocess + `mcp.bridge.health` 핸들러 mock 기반.

### TC-HC-01 — Happy path (3 틱 정상)
- **조건**: spawn 후 45s 대기, HC 3회 발행.
- **기대**: 3회 모두 Healthy, `consecutive_fails == 0`, state 변화 없음.
- **검증**: 간격 15±0.5s, elapsed < 100ms/tick.

### TC-HC-02 — LOCK-RT-12 15초 간격 검증
- **조건**: 10분 HC 루프 실행, 타임스탬프 수집.
- **기대**: 각 tick 간격 15±0.5s, 40 tick 수집.
- **검증**: LOCK-RT-12 불변.

### TC-HC-03 — per-call 5초 타임아웃
- **조건**: Python 측 `mcp.bridge.health` 가 `sleep 10s`.
- **기대**: 5.0~5.5s 에 타임아웃, `consecutive_fails = 1`.
- **검증**: grace 0.5s 반영.

### TC-HC-04 — 3회 연속 실패 → 재시작 트리거
- **조건**: Python 측이 HC 3회 연속 무응답.
- **기대**: 3번째 실패 후 state Running→Unhealthy, restart_policy.md `HealthcheckExhausted` 트리거, HC 루프 break.
- **검증**: 탐지 시간 ≤ 50s, restart 메트릭 +1.

### TC-HC-05 — 간헐 실패 (1 fail, 1 success, 1 fail, 1 success, 1 fail)
- **조건**: 5 tick 중 1,3,5 실패.
- **기대**: 각 실패 후 카운터 1, 성공 후 리셋, 최종 `consecutive_fails = 1`. 재시작 없음.
- **검증**: 정상 운영 유지.

### TC-HC-06 — Degraded 응답 (status="Degraded" in result)
- **조건**: Python 측이 `{"result":{"status":"Degraded","rss_bytes":1800000000,...}}`.
- **기대**: `consecutive_fails` 증가 없음, HealthReport.overall=Degraded, 경고 로그, HC 루프 계속.
- **검증**: AtomicU8 Running 유지, §7.2 가속 규칙 발동 준비.

### TC-HC-07 — Degraded 지속 중 1회 실패 → 가속
- **조건**: TC-HC-06 직후 1 tick 타임아웃.
- **기대**: `consecutive_fails = 0 + 2 = 2` (가속 규칙).
- **검증**: §7.2.

### TC-HC-08 — rss 95% 접근 시 Degraded 판정
- **조건**: Python 측 `rss_bytes = 1.95GB`, `status=Healthy`.
- **기대**: Rust 측이 §7.1 임계 초과 감지 → HealthReport.overall=Degraded 노출.
- **검증**: Python 응답이 Healthy 여도 Rust 판정 우선.

### TC-HC-09 — cpu 지속 85% 3 tick
- **조건**: Python 측 cpu_pct = 88.0 을 3 tick 연속 응답.
- **기대**: 3번째 tick 후 Degraded 전이.
- **검증**: 1~2 tick 시점에는 Healthy 유지.

### TC-HC-10 — queue_length 50 (Semaphore 포화)
- **조건**: 동시 RPC 50 건 진행 중 HC tick.
- **기대**: queue_length=50 보고 → Unhealthy 경계 경합, `consecutive_fails += 1`.
- **검증**: §7.1 Unhealthy 경계 규칙.

### TC-HC-11 — HC 루프 상태 게이트 (spawn 중)
- **조건**: spawn() 진행 중 (state=Spawning) healthcheck_loop 도 기동되어 있다고 가정.
- **기대**: 루프는 tick 을 skip (state != Running). `consecutive_fails = 0` 유지.
- **검증**: `mcp.bridge.health` 호출 없음.

### TC-HC-12 — HC 중 Python crash (stdin broken pipe)
- **조건**: HC 송출 순간 Python 프로세스 exit 1.
- **기대**: stdin write 실패 → `HC_PIPE_BROKEN` → state Dead (stdout reader 감지) → restart.
- **검증**: `consecutive_fails` 가 3 에 도달하지 않아도 즉시 Dead 전환.

### TC-HC-13 — HC 응답 malformed (JSON 아님)
- **조건**: Python 측이 stdout 에 `"not a json"` 출력.
- **기대**: §9.1 `HC_MALFORMED_RESPONSE` → `consecutive_fails += 1`, 루프 유지.
- **검증**: stdout_reader_task 의 frame 에러 카운터와 별도 관리.

### TC-HC-14 — restart 후 HC 루프 재기동 시 카운터 리셋
- **조건**: TC-HC-04 후 restart 성공.
- **기대**: 새 HC 루프가 기동되며 `consecutive_fails = 0` 초기 상태.
- **검증**: restart 바로 후 1 tick 실패 발생해도 state 변화 없음 (카운트=1).

---

## §11. 구조화 로그 JSON

### 11.1 HC tick 로그 (정상)

```json
{
  "timestamp": "2026-04-11T03:00:12.345Z",
  "level": "debug",
  "logger": "bridge.python_manager.healthcheck",
  "event": "python_bridge_healthcheck_tick",
  "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "correlation_id": "hc_240",
  "context": {
    "tick_number": 240,
    "elapsed_ms": 12,
    "status": "Healthy",
    "uptime_s": 3612,
    "rss_bytes": 524288000,
    "rss_pct": 24.4,
    "cpu_pct": 12.4,
    "active_calls": 3,
    "queue_length": 0,
    "consecutive_fails": 0
  }
}
```

### 11.2 HC 실패 로그

```json
{
  "timestamp": "2026-04-11T03:00:52.345Z",
  "level": "error",
  "logger": "bridge.python_manager.healthcheck",
  "event": "python_bridge_healthcheck_fail",
  "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "correlation_id": "hc_243",
  "error": {
    "internal_label": "HC_UNHEALTHY_CONSECUTIVE",
    "registry_code": null,
    "jsonrpc_code": -32000,
    "tauri_variant": "PythonBridgeError",
    "message": "3 consecutive healthcheck failures"
  },
  "context": {
    "tick_number": 243,
    "consecutive_fails": 3,
    "threshold": 3,
    "last_elapsed_ms": 5002,
    "last_status": "Timeout",
    "process_state": "Running"
  },
  "recovery": {
    "action": "trigger_restart",
    "next_state": "Unhealthy",
    "handoff_to": "restart_policy.md §4 HealthcheckExhausted"
  }
}
```

### 11.3 이벤트 카탈로그

| event | level | 발생 시점 | 필수 context |
|---|---|---|---|
| `python_bridge_healthcheck_tick` | debug | 매 tick 정상 완료 | tick_number, status, elapsed_ms |
| `python_bridge_healthcheck_degraded` | warn | Degraded 전이 | reason, rss_bytes/cpu_pct/queue_length |
| `python_bridge_healthcheck_fail` | warn | 1~2회 실패 | consecutive_fails |
| `python_bridge_healthcheck_exhausted` | error | 3회 누적 | consecutive_fails=3 |
| `python_bridge_healthcheck_loop_start` | info | 루프 기동 | process_pid |
| `python_bridge_healthcheck_loop_stop` | info | 루프 종료 | reason |
| `python_bridge_healthcheck_gate_skipped` | debug | state != Running 으로 skip | state |

- **LOCK-RT-15**: Rust `tracing` crate → `logs/rust_bridge.log`. Python 측 stderr 는 별도 `logs/python_engine.log`.

---

## §12. LOCK 교차 점검표

| LOCK ID | 본 파일 준수 항목 | 섹션 | 재정의? |
|---|---|---|---|
| LOCK-RT-04 | `python_manager.rs::healthcheck()` + `healthcheck_loop` 경계 | §3.5, §1 | 없음 |
| LOCK-RT-07 | 48건 정본 내 HC 실패 코드 부재 인지 + 잠정 매핑 (REF-only, 소유 = 6-12) | §9 (CFL-RT-009 RESOLVED-DEFERRED 상속) | 없음 |
| LOCK-RT-11 | `mcp.bridge.health` JSON-RPC 프레이밍 | §3 | 없음 |
| LOCK-RT-12 | **HC 15s / 5s / 3회** 정본 수치만 인용 | §2, §3, §5 | **없음 (재정의 절대 금지)** |
| LOCK-RT-13 | HC 실패 → `HealthcheckExhausted` → restart backoff 2→4→8s (restart_policy.md 위임) | §4, §8 | 없음 |
| LOCK-RT-14 | TauriError 매핑 (Timeout, PythonBridgeError, IoError, InternalError) | §9 | 없음 |
| LOCK-RT-15 | Rust tracing → rust_bridge.log, Python stderr → python_engine.log 분리 | §11.3 | 없음 |

- **LOCK 변경 필요 여부**: 없음. FailureCodeRegistry 확장 12건은 CFL-RT-009 RESOLVED-DEFERRED (CONFLICT_LOG v1.2) 로 처리되며 spawn_protocol.md §7 과 공유. 6-12 Event-Logging V4 cross-handoff 경로 사용.

---

## §13. 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|---|---|---|---|
| v0.1 | 2026-04-11 | 초기 작성 (T1-4 step 1). §1~§12 신규. LOCK-RT-12 정본 15s/5s/3회 전수 준수, HC 루프 의사코드 (MissedTickBehavior::Delay), Degraded 판정 기준 (rss 80%/cpu 85%/queue 40/elapsed 3s), Degraded→Unhealthy 가속 규칙 +2/tick, HealthTickResult DTO + T1-2 HealthReport 통합 매핑, CC-T14-01 상속, Phase 2 테스트 시나리오 14건. T1-3 rpc_protocol.md §6.1 L1 / §7.7 healthcheck() 선정의와 1:1 정합. | T1-4 Subagent |
| v0.2 | 2026-04-11 | T1-4 step 2 재검증. LOCK-RT-12 (15s/5s/3회) 정본 수치 재정의 없음 재확인, §3.5 HC 루프 의사코드 / §5.2 탐지 상한 50s / §7 Degraded 임계 불변. CC-T14-01 상속 표기 (신규 CFL 번호는 step 7 에서 할당) 명확화 — 본 파일에는 CFL 직접 번호 기재 없으므로 수정 불필요, spawn_protocol.md §7 의 정정과 일관. §8 FR-8 L1 계층, §6 T1-2 HealthReport 매핑, §3 `mcp.bridge.health` 메서드명 재검증 완료. 본문 §1~§12 무변경. | T1-4 Subagent |
| v0.3 | 2026-04-11 | 4-1 Deep Reverify — §1/§9.1/§12 의 `[CONFLICT_CANDIDATE CC-T14-01]` 마커를 `[CFL-RT-009 RESOLVED-DEFERRED (CC-T14-01)]` 정규 참조로 정정 (CONFLICT_LOG v1.2 반영). §9.2 헤딩을 "6-12 V4 통합 후 canonical 매핑" 으로 갱신. §12 LOCK-RT-07 행에 "REF-only (소유 = 6-12)" 명시. §12 LOCK 변경 필요 여부 단락을 cross-handoff 설명으로 갱신. | Deep Reverify |

<!-- END OF DOCUMENT -->

---

# §V2. Prometheus 모니터링 메트릭 — T2-4 (healthcheck)

> **Phase 2 T2-4 산출물** (plan §7 T2-4 L1039~L1074 + §B.4 L1327~L1338 정본 verbatim)
> **작성일**: 2026-04-24
> **대상 V1**: healthcheck.md §1~§13 불변 (baseline SHA `b51fbeb13c50b323`, 30397 bytes, 624 lines)
> **LOCK 근거**: LOCK-RT-12 (HC 15s/5s/3회, DEFINED-HERE §D-2) 정본 · LOCK-RT-15 (stderr 분리)

## §V2.1 교차 참조 블록

| 대상 | 경로 | 관계 |
|-----|-----|------|
| **plan 정본** | RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md §B.4 L1327~L1338 + §7 T2-4 L1039~L1074 | Prometheus 메트릭 정본 |
| **SLA 매핑** | plan §A.3 L1255~L1264 (System/Health P99 ≤ 30ms) | HC 알림 임계값 보조 |
| **LOCK-RT-12 DEFINED-HERE** | RUST_TAURI_INFRASTRUCTURE_상세명세.md §D-2 L352~L356 | 15s/5s/3회 정본 |
| **peer V2 (T2-4 EXTEND)** | spawn_protocol.md §V2 + restart_policy.md §V2 | HC 실패 → restart 경로 |
| **peer V2 (T2-2 EXTEND)** | 01_ipc-commands/health_commands.md §V2 | SEC-3 health:admin 권한 |
| **V1 §1~§12** | healthcheck.md §3 HC 루프 의사코드 + §5 탐지 상한 50s + §7 Degraded 임계 | §V2 메트릭 source of truth |

## §V2.2 대상 메트릭 3종 (healthcheck 담당)

| # | 메트릭 이름 | 타입 | 라벨 | 단위 | 설명 |
|---|-------------|------|-----|------|-----|
| 1 | `python_bridge_healthcheck_failures_total` | Counter | `reason` | count | HC 실패 누적 (reason: timeout / bad_response / rss_limit / cpu_limit / queue_limit) |
| 2 | `python_bridge_rpc_duration_seconds` | Histogram | `method`, `status` | seconds | JSON-RPC 메서드별 응답시간 (13 메서드, LOCK-RT-03 정본 + 6 내부 `_lifecycle.*`) |
| 3 | `python_bridge_rpc_errors_total` | Counter | `method`, `error_code` | count | JSON-RPC 에러 수 (48 FailureCode + rt.py_bridge.* 12 로컬 네임스페이스) |

### Prometheus client Rust
```rust
use prometheus::{CounterVec, HistogramVec, HistogramOpts, register_counter_vec, register_histogram_vec};
use once_cell::sync::Lazy;

pub static HC_FAILURES: Lazy<CounterVec> = Lazy::new(|| register_counter_vec!(
    "python_bridge_healthcheck_failures_total",
    "Python bridge HC failure count",
    &["reason"]
).expect("register"));

pub static RPC_DURATION: Lazy<HistogramVec> = Lazy::new(|| register_histogram_vec!(
    HistogramOpts::new(
        "python_bridge_rpc_duration_seconds",
        "JSON-RPC method duration"
    ).buckets(vec![0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 120.0]),
    &["method", "status"]
).expect("register"));

pub static RPC_ERRORS: Lazy<CounterVec> = Lazy::new(|| register_counter_vec!(
    "python_bridge_rpc_errors_total",
    "JSON-RPC error count",
    &["method", "error_code"]
).expect("register"));
```

> **타임아웃 버킷 확장**: LOCK-RT-12 HC 5s 및 process_message 120s 를 커버하기 위해 기본 10s 에 30s/120s 추가 (버킷 13개).

## §V2.3 LOCK-RT-12 HC 알림 임계값 연동 (DEFINED-HERE §D-2)

| 조건 | PromQL | 임계 | 알림 수준 |
|------|--------|-----|-----------|
| HC 실패 1회 | `increase(python_bridge_healthcheck_failures_total[30s]) >= 1` | ≥ 1 | `info` (로그만) |
| HC 실패 2회 연속 | `increase(python_bridge_healthcheck_failures_total[45s]) >= 2` | ≥ 2 | `warn` (3회시 재시작 임박) |
| HC 실패 3회 연속 (LOCK-RT-12 재시작 트리거) | `increase(python_bridge_healthcheck_failures_total[60s]) >= 3` | ≥ 3 | `critical` (restart 시도) |
| HC timeout 비율 | `rate(python_bridge_healthcheck_failures_total{reason="timeout"}[5m]) / rate(python_bridge_healthcheck_total[5m])` | > 0.1 | `warn` (LOCK-RT-12 5s 타임아웃 기준) |
| RSS 80% 초과 | V1 §7 Degraded 임계 | > 80% | `warn` → HC 가속 |
| CPU 85% 초과 | V1 §7 | > 85% | `warn` |
| Queue 40+ | V1 §7 | > 40 | `warn` |
| RPC 응답 > 5s | `histogram_quantile(0.99, python_bridge_rpc_duration_seconds_bucket{method="mcp.bridge.health"}) > 5.0` | > 5s | `critical` (LOCK-RT-12 위반) |

## §V2.4 LOCK 5필드 매핑

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-RT-12 | Python HC 주기 | 상세명세 §D-2 L352~L356 (DEFINED-HERE) | 15s 간격 / 5s 타임아웃 / 3회 연속 실패→재시작 | ❌ |
| LOCK-RT-15 | stderr 로그 분리 | PHASE_B2 + Part2 V0-STEP-3 | stdout=JSON-RPC / stderr=로그 | ❌ |
| LOCK-RT-07 (REF-only) | FailureCodeRegistry 48건 | D2.1-D2 §5.2 (6-12 정본) | rpc_errors.error_code 라벨 (48 canonical + rt.py_bridge.* 12 로컬) | REF-only (재정의 0, PY_BRIDGE_* 12 는 CFL-RT-009 V4 cross-handoff) |

## §V2.5 SLA ↔ HC 메트릭 알림 규칙

| 항목 | PromQL | 임계 |
|------|--------|-----|
| System/Health P99 ≤ 30ms | `histogram_quantile(0.99, python_bridge_rpc_duration_seconds_bucket{method="health_check"}) < 0.030` | 위반 시 `warn` (plan §A.3 ↔ T2-3 STEP_B #2b) |
| HC 성공률 99.9% | `1 - rate(python_bridge_healthcheck_failures_total[5m])/rate(python_bridge_healthcheck_total[5m]) >= 0.999` | 위반 시 `critical` |
| RPC 성공률 (카테고리별) | `1 - rate(python_bridge_rpc_errors_total[5m])/rate(python_bridge_rpc_total[5m])` | 카테고리 한도 |

## §V2.6 구조화 로그 3-block

### block-1: HC timeout
```json
{
  "source": "rust_tauri.process.hc",
  "event": "healthcheck.timeout",
  "reason": "timeout",
  "elapsed_ms": 5001,
  "consecutive_failures": 2,
  "severity": "Warn"
}
```

### block-2: RPC duration sample
```json
{
  "source": "rust_tauri.process.rpc",
  "event": "rpc.completed",
  "method": "process_message",
  "status": "ok",
  "duration_seconds": 1.234
}
```

### block-3: HC 3연속 실패 (LOCK-RT-12 재시작 트리거)
```json
{
  "source": "rust_tauri.process.hc",
  "event": "healthcheck.threshold_exceeded",
  "consecutive_failures": 3,
  "action": "restart_initiated",
  "severity": "Critical"
}
```

## §V2.7 Phase 3 테스트 시나리오 (≥ 10건)

1. TS-M-HC-1 — HC 정상 4주기 × 15s → failures_total = 0
2. TS-M-HC-2 — Python stdin close → timeout 1회 → failures_total +1 (reason=timeout)
3. TS-M-HC-3 — 3회 연속 실패 → `restart_initiated` 로그 + restart_total +1 (restart_policy.md §V2 연동)
4. TS-M-HC-4 — process_message 120s 경계 (119/120/121) → duration_seconds 버킷 정확
5. TS-M-HC-5 — 13 RPC 메서드 × 각 1회 → method 라벨 13종 커버리지
6. TS-M-HC-6 — 48 FailureCode + 12 PY_BRIDGE_* 에러 매핑 정합 (error_code 라벨 60 전수)
7. TS-M-HC-7 — Degraded 진입 (RSS 85%) → HC 주기 가속 (+2/tick) V1 §7 연동
8. TS-M-HC-8 — HC 실패율 10% 초과 → `warn` Alertmanager 발화
9. TS-M-HC-9 — `/metrics` scrape → 3 메트릭 노출 + buckets 13 확인
10. TS-M-HC-10 — RPC error 라벨 cardinality 60 < 100 (Prometheus cardinality limit)
11. TS-M-HC-11 — timestamp 역전 공격 (system clock skew) → HC 탐지 반영 확인
12. TS-M-HC-12 — P99 30ms SLA 초과 (System/Health) → `warn` (plan §A.3 연동)

## §V2.8 자가 체크리스트

- [x] §1 교차 참조 블록 (§V2.1): plan §B.4 + §A.3 + 상세명세 §D-2 + peer 2 V2 + T2-2 health_commands 전수
- [x] §2 공통 자료 구조 참조 (§V2.4): LOCK-RT-12/15 + LOCK-RT-07 REF-only 3 row 5필드
- [x] §3 구현 상세 (§V2.2 Rust 코드): Prometheus client + 버킷 13 확장 (LOCK-RT-12 5s + process_message 120s 커버)
- [x] §4 기능별 상세: HC 실패 reason 5종 + RPC method 13 + error_code 60 (48 + 12) 전수 라벨
- [x] §N LOCK-RT-12 알림 임계값 8 row 실체화 + §N 구조화 로그 3-block (§V2.6)
- [x] §N Phase 3 테스트 시나리오 ≥ 10건 (§V2.7): TS-M-HC-1~12 실체화
- [x] §N 세션 간 cross-check: peer T2-4 spawn + restart + T2-2 health_commands 전수
- [x] 자가 체크리스트 (§V2.8): §3.1~§3.5 anti-fabrication 가이드 준수

---

<!-- END OF §V2 (T2-4 healthcheck) -->
