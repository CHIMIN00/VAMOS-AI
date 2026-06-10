# restart_policy.md — Python Bridge Restart 정책 + FR-8 타임아웃 캐스케이드

> **파일 위치**: `4-1_Rust-Tauri-Infrastructure/05_process-management/restart_policy.md`
> **세션**: T1-4 (프로세스 관리 상세) Phase 1
> **정본**: LOCK-RT-13 (상세명세 §D-3, DEFINED-HERE, Phase 5 동결) — **비정상 종료 1s→2s→4s→8s→16s / OOM 5s 고정 / HC 실패 2s→4s→8s**
> **해소 대상**: ISS-05 프로세스 관리 전면 신규 — Restart/Graceful Shutdown/Circuit Breaker 축 + FR-8 타임아웃 캐스케이드 계층 구조

---

## §1. 교차 참조 (AUTHORITY_CHAIN)

```
AUTHORITY_CHAIN (본 파일 의존 LOCK)
  ├── LOCK-RT-04  python_manager.rs::restart()/shutdown() 인터페이스
  ├── LOCK-RT-07  FailureCodeRegistry 48건 (CFL-RT-009 RESOLVED-DEFERRED 상속, REF-only 소유 = 6-12)
  ├── LOCK-RT-11  JSON-RPC 2.0 (shutdown RPC 프레이밍)
  ├── LOCK-RT-12  HC 15초 — 재시작 후 HC 루프 재기동 정책
  ├── LOCK-RT-13  *** Restart backoff 1→2→4→8→16s / OOM 5s / HC 2→4→8s *** (정본, 재정의 금지)
  │     출처: 상세명세 §D-3 (DEFINED-HERE, Phase 5 동결)
  │     본 파일 사용: §2, §4, §5, §6, §7, §8 전체
  ├── LOCK-RT-14  TauriError 7 variant
  └── LOCK-RT-15  stderr 분리

주변 정본 참조
  ├── 상세명세 §D-3  Restart Policy 원문 (3 조건 × backoff)
  ├── 상세명세 §F-1  상태 전이도 (Running→Unhealthy→Restarting→Spawning)
  ├── 상세명세 §F-2  동시성 가드 (drain 패턴, 좀비 스캔 30s)
  └── 상세명세 §D-1  Spawn 프로토콜 (재진입 대상)

세션 간 인터페이스 cross-check
  ├── T1-2 HealthReport / HealthStatus / PythonProcessStatus.restart_count
  │     — §6 재시작 성공 시 restart_count += 1
  ├── T1-3 rpc_protocol.md §6.1 타임아웃 계층 L0~L3
  │     — 본 파일 §6 는 L0~L3 간 전파 규칙의 유일한 정본
  ├── T1-3 rpc_protocol.md §7.7 restart()/shutdown() 선정의
  │     — "drain pending → SIGTERM 5s → SIGKILL → backoff → spawn() 재진입" 1:1 정합
  ├── spawn_protocol.md §2 Step 1 spawn_mutex + §6 FR-5 동시성 가드
  │     — 본 파일 §4 restart 는 동일 mutex 를 공유
  ├── spawn_protocol.md §9.3 ProcessFailureEscalation
  │     — 본 파일 §9 재사용
  └── healthcheck.md §3.5 HealthcheckExhausted 트리거
        — 본 파일 §3 restart 트리거 소스
```

---

## §2. LOCK-RT-13 준수 (정본 backoff 표)

> **재정의 절대 금지**. 본 파일은 정본 값을 인용하고 L3 구현만 상세화한다.

### 2.1 상세명세 §D-3 원문 표 (정본)

| 조건 | 동작 | 최대 재시도 | 백오프 |
|---|---|---|---|
| 비정상 종료 (exit code ≠ 0) | 즉시 재시작 | **5회** | **1s → 2s → 4s → 8s → 16s** |
| OOM (exit code 137) | 메모리 제한 상향 후 재시작 | **3회** | **5s 고정** |
| Healthcheck 실패 | SIGTERM → 5s 대기 → SIGKILL → 재시작 | **3회** | **2s → 4s → 8s** |
| 사용자 명시적 중지 | 재시작 안 함 | — | — |

### 2.2 본 파일 수치 인용 규약

- 위 표의 모든 수치는 **정본 수치만 인용**한다. 본 파일 §2 이외 섹션에서 값이 재등장할 때는 반드시 "LOCK-RT-13" 참조 주석을 동반한다.
- `[LOCK_CHANGE_NEEDED]` 마커는 본 파일에서 사용하지 않음.
- **OOM 이후 backoff 정상 진입 여부** (§7) 도 본 §2 표의 "3회 최대" 를 넘지 않는다.

---

## §3. 재시작 트리거

| # | 트리거 | 원천 | RestartCause | backoff 경로 |
|---|---|---|---|---|
| T-01 | Unhealthy 판정 (HC 3회 연속 실패) | healthcheck.md §3.5 | `HealthcheckExhausted { fails: 3 }` | §2.1 HC 경로 2→4→8s |
| T-02 | 프로세스 크래시 (stdout EOF + exit ≠ 0, ≠ 137) | rpc_protocol.md §7.5 reader task | `CrashExit { code: i32 }` | §2.1 비정상 종료 1→2→4→8→16s |
| T-03 | OOM kill (exit code 137) | reader task + 9.3 로그 감지 | `OutOfMemory { pid }` | §2.1 OOM 5s 고정 |
| T-04 | spawn() 3 attempt 실패 (spawn_protocol.md E-10/E-11) | spawn_protocol.md §5 | `SpawnExhausted { attempts: 3 }` | §2.1 비정상 종료 경로 (attempt 4~5) |
| T-05 | stdin 파이프 깨짐 | send() / healthcheck_loop | `PipeBroken { io_err }` | §2.1 비정상 종료 경로 |
| T-06 | 명시적 shutdown → graceful 실패 fallback | §4.2 | `GracefulShutdownFailed` | §2.1 비정상 종료 경로 (1회만) |
| T-07 | operator 수동 `restart_bridge` IPC 커맨드 | Tauri 커맨드 | `OperatorRequested` | backoff 0s (즉시) |
| T-08 | 사용자 명시적 중지 (`shutdown()` 정상 완료) | §4 | — | **재시작 안 함** (§2.1 마지막 행) |

### 3.1 RestartCause enum (DEFINED-HERE)

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RestartCause {
    HealthcheckExhausted { fails: u32 },
    CrashExit { code: i32 },
    OutOfMemory { pid: u32 },
    SpawnExhausted { attempts: u32 },
    PipeBroken { io_err: String },
    GracefulShutdownFailed,
    OperatorRequested,
}

impl RestartCause {
    /// LOCK-RT-13 경로 분류
    pub fn backoff_schedule(&self) -> BackoffSchedule {
        match self {
            Self::OutOfMemory { .. }        => BackoffSchedule::OomFixed5s,
            Self::HealthcheckExhausted {..} => BackoffSchedule::Hc2_4_8s,
            Self::OperatorRequested         => BackoffSchedule::Immediate,
            _                               => BackoffSchedule::Normal1_2_4_8_16s,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum BackoffSchedule {
    Normal1_2_4_8_16s,   // 비정상 종료 (5회)
    OomFixed5s,          // OOM (3회)
    Hc2_4_8s,            // HC 실패 (3회)
    Immediate,           // operator (0s, 5회)
}

impl BackoffSchedule {
    pub fn delay_ms(&self, attempt: u32) -> u64 {
        match self {
            Self::Normal1_2_4_8_16s => match attempt {
                1 => 1_000, 2 => 2_000, 3 => 4_000, 4 => 8_000, 5 => 16_000,
                _ => 16_000,
            },
            Self::OomFixed5s        => 5_000,
            Self::Hc2_4_8s          => match attempt {
                1 => 2_000, 2 => 4_000, 3 => 8_000,
                _ => 8_000,
            },
            Self::Immediate         => 0,
        }
    }
    pub fn max_attempts(&self) -> u32 {
        match self {
            Self::Normal1_2_4_8_16s => 5,
            Self::OomFixed5s        => 3,
            Self::Hc2_4_8s          => 3,
            Self::Immediate         => 5,
        }
    }
}
```

---

## §4. 재시작 절차 (L3 상세도)

### 4.1 단계 시퀀스

```
┌────────────────────────────────────────────────────────────────────────┐
│  restart(cause: RestartCause)                                          │
│                                                                        │
│  Step 1.  acquire spawn_mutex (FR-5, spawn_protocol §6.1 L1)            │
│  Step 2.  state CAS Running/Unhealthy/Dead → Restarting                 │
│  Step 3.  drain_pending() — 모든 PendingEntry 에 -32000 응답             │
│  Step 4.  graceful shutdown 시도:                                       │
│             4.1  shutdown RPC 송출 (mcp.bridge.shutdown, 10s timeout)   │
│             4.2  진행 중 RPC drain (5s grace)                           │
│             4.3  SIGTERM 전송                                           │
│             4.4  5s 내 프로세스 종료 대기                                │
│             4.5  5s 초과 시 SIGKILL                                     │
│  Step 5.  pid_history 기록 + 좀비 스캔 등록                              │
│  Step 6.  pidfile 삭제                                                  │
│  Step 7.  RestartCause → BackoffSchedule 결정                            │
│  Step 8.  attempt 루프 (max_attempts 까지):                              │
│             8.1  tokio::time::sleep(backoff.delay_ms(attempt))           │
│             8.2  circuit breaker 확인 (§5)                              │
│             8.3  spawn() 재진입 (spawn_protocol.md §2 Step 1~10)        │
│             8.4  spawn 성공 → Running, restart_count += 1, break         │
│             8.5  spawn 실패 → attempt += 1 → 8.1                         │
│  Step 9.  attempt 루프 종료:                                             │
│             9.1  성공: healthcheck_loop 재기동 (새 카운터 0)             │
│             9.2  실패: state → Suspended, circuit breaker OPEN          │
│  Step 10. release spawn_mutex                                           │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Graceful Shutdown Fallback (Step 4)

```rust
async fn graceful_shutdown_then_kill(
    child: &mut Child,
    stdin: &Arc<Mutex<Option<ChildStdin>>>,
    pending: &Arc<Mutex<BTreeMap<String, PendingEntry>>>,
) -> GracefulResult {
    const SHUTDOWN_RPC_TIMEOUT: Duration = Duration::from_secs(10);  // rpc_protocol.md §6.2 L2 shutdown 10s
    const DRAIN_TIMEOUT: Duration         = Duration::from_secs(5);  // L3 상세명세 §D-3 "SIGTERM → 5s 대기 → SIGKILL"

    // 4.1 shutdown RPC (best-effort)
    let rpc_sent = {
        let mut stdin_g = stdin.lock().await;
        if let Some(s) = stdin_g.as_mut() {
            let req = build_shutdown_request();
            let line = serde_json::to_string(&req).unwrap();
            tokio::time::timeout(Duration::from_millis(500),
                async {
                    s.write_all(line.as_bytes()).await?;
                    s.write_all(b"\n").await?;
                    s.flush().await
                }
            ).await.is_ok()
        } else { false }
    };

    // 4.2 drain pending 5s grace (RPC 응답 수신 기회)
    if rpc_sent {
        let _ = tokio::time::timeout(DRAIN_TIMEOUT, wait_pending_drain(pending)).await;
    }

    // 4.3 SIGTERM
    #[cfg(unix)] {
        if let Some(pid) = child.id() {
            unsafe { libc::kill(pid as i32, libc::SIGTERM); }
        }
    }
    #[cfg(windows)] {
        // Job Object KILL_ON_JOB_CLOSE 가 Rust 측 drop 에서 자동 종료.
        // 여기서는 TerminateProcess 또는 Job Object close 로 대체.
        let _ = child.start_kill();  // tokio::process::Child::start_kill → TerminateProcess
    }

    // 4.4 5s wait for exit
    match tokio::time::timeout(DRAIN_TIMEOUT, child.wait()).await {
        Ok(Ok(status)) => GracefulResult::Graceful { exit_status: status },
        Ok(Err(e))     => GracefulResult::IoError(e.to_string()),
        Err(_) => {
            // 4.5 SIGKILL fallback
            let _ = child.start_kill();  // 이미 보낸 경우 idempotent
            let _ = child.kill().await;
            GracefulResult::HardKilled
        }
    }
}

enum GracefulResult {
    Graceful { exit_status: std::process::ExitStatus },
    HardKilled,
    IoError(String),
}
```

- **FR-8 L3 수치**: Graceful Shutdown timeout **5s** (상세명세 §D-3 + rpc_protocol.md §6.2).
- **shutdown RPC 타임아웃 10s 는 L2 값**이지만, Step 4.1 송출 자체는 best-effort 500ms 로 제한한다 (상대가 이미 Unhealthy 라 write 자체가 블록될 수 있음).
- **drain 5s 는 Step 4.2 진행 중 RPC 완료 대기** 이며, Step 4.4 의 "프로세스 종료 대기 5s" 와 **순차 수행** (총 최대 10s).

### 4.3 pending drain 의 2 단계

1. **Step 3 (restart 진입 즉시)**: 모든 pending 에 `-32000 python_bridge_unhealthy` 응답. 신규 요청 거부 목적.
2. **Step 4.2 (graceful 5s)**: Step 3 직후 들어온 RPC 또는 Step 3 직전에 이미 stdin 에 write 된 RPC 의 응답을 Python 측이 반환하도록 유예. 이 시점은 rpc_protocol.md §7.7 restart() 선정의의 "drain pending" 과 동일.

실제 구현은 Step 3 만 수행하고 Step 4.2 는 무시할 수도 있으나, 상세명세 §F-2 "drain 패턴" 은 **우아한 종료 지원**을 명시한다 → 본 파일은 Step 3 + Step 4.2 **둘 다** 수행을 기본으로 한다.

### 4.4 spawn() 재진입 시 spawn_mutex

- spawn_protocol.md §2 Step 1 도 `spawn_mutex.lock()` 이다. 본 파일 §4 Step 1 이 이미 mutex 를 보유하고 있으므로 **재진입 가능한(re-entrant) mutex 가 아니면 데드락**이 발생한다.
- Tokio `Mutex` 는 기본적으로 **재진입 불가** → 두 가지 옵션:
  1. (권장) `restart()` 내부에서 `spawn()` 대신 **`spawn_inner()`** 이라는 lockless 함수를 호출. `spawn()` 공개 API 는 mutex 를 잠그고 `spawn_inner()` 를 호출하는 thin wrapper.
  2. `spawn_mutex` 를 `parking_lot::ReentrantMutex` 로 변경 (Tokio 호환 불가 → 채택 곤란).
- **결정**: 옵션 1 채택. spawn_protocol.md §2 Step 1 주석 "이후 모든 Step 은 본 guard 보호 구간" 을 훼손하지 않으며, 본 파일 §4 Step 8.3 은 `spawn_inner()` 를 호출하도록 명세. rpc_protocol.md §7.7 의 공개 인터페이스는 변경 없음.

---

## §5. 최대 재시작 횟수 & Circuit Breaker

### 5.1 경로별 최대 재시도 (LOCK-RT-13)

| 경로 | 최대 재시도 | 이후 동작 |
|---|---|---|
| 비정상 종료 | 5 | Suspended + operator 알림 |
| OOM | 3 | Suspended + 메모리 한도 상향 제안 |
| HC 실패 | 3 | Suspended + 최근 HC 로그 operator 전달 |
| Immediate (operator) | 5 | Suspended |

### 5.2 Circuit Breaker (시간 윈도우 기반)

단일 restart 세션의 최대 재시도 수는 LOCK-RT-13 으로 결정된다. 그러나 **여러 번의 restart 세션이 짧은 시간에 반복**되면 더 강한 가드가 필요하다 → **sliding window circuit breaker**.

#### 5.2.1 정의

```
WINDOW        = 600s (10분)
MAX_RESTARTS  = 10   (본 파일 DEFINED-HERE 권장값)
```

- 최근 10분 내 restart 횟수가 10 을 초과하면 **circuit OPEN**, 이후 모든 restart 요청은 즉시 거부 + operator 개입 요구.
- **10분/10회 의 근거**: 평균 1회/분 = 매우 높은 장애율. 이 빈도를 넘으면 자동 복구가 아니라 인적 조치가 필요. 본 값은 config 로 override 가능 (LOCK 아님).

#### 5.2.2 의사코드 (O(1) sliding window counter)

```rust
use std::collections::VecDeque;
use std::time::{Duration, Instant};

pub struct RestartCircuitBreaker {
    window:           Duration,          // 600s
    max_restarts:     u32,               // 10
    timestamps:       Mutex<VecDeque<Instant>>,
    state:            AtomicU8,          // 0=Closed, 1=HalfOpen, 2=Open
    opened_at:        Mutex<Option<Instant>>,
    cooldown:         Duration,          // Open 진입 후 재진입 허용 시각 (600s)
}

impl RestartCircuitBreaker {
    /// 재시작 시도 가능 여부 — 시간복잡도 O(1) amortized
    /// (내부 VecDeque pop_front 는 amortized O(1))
    pub async fn allow_restart(&self) -> bool {
        let now = Instant::now();
        // Open 상태 체크
        if self.state.load(Ordering::Acquire) == 2 {
            let opened_at = *self.opened_at.lock().await;
            if let Some(t) = opened_at {
                if now.duration_since(t) < self.cooldown {
                    return false;                        // 여전히 OPEN
                }
                // cooldown 지남 → HalfOpen
                self.state.store(1, Ordering::Release);
                self.timestamps.lock().await.clear();
            }
        }
        // 윈도우 초과 타임스탬프 제거 (amortized O(1))
        let mut ts = self.timestamps.lock().await;
        while let Some(&front) = ts.front() {
            if now.duration_since(front) > self.window {
                ts.pop_front();
            } else { break; }
        }
        if ts.len() as u32 >= self.max_restarts {
            // OPEN 전이
            self.state.store(2, Ordering::Release);
            *self.opened_at.lock().await = Some(now);
            return false;
        }
        ts.push_back(now);
        true
    }

    pub async fn record_success(&self) {
        // HalfOpen 에서 성공 → Closed
        if self.state.load(Ordering::Acquire) == 1 {
            self.state.store(0, Ordering::Release);
            *self.opened_at.lock().await = None;
        }
    }
}
```

- **시간복잡도**:
  - `allow_restart`: `VecDeque::pop_front` 는 amortized O(1). while 루프는 totally amortized O(1) (각 요소는 한 번만 pop 됨).
  - `record_success`: O(1).
- **공간복잡도**: O(max_restarts) — 최대 10 개 Instant 저장.

#### 5.2.3 3 상태 머신

```
          allow_restart(n < max)
   ┌──────────────────────────────────┐
   ▼                                  │
[Closed] ─ allow_restart(n == max) ─→ [Open]
   ▲                                  │
   │                                  │ cooldown 600s 경과
   │                                  ▼
   │                              [HalfOpen]
   │                                  │
   └──── record_success ──────────────┤
                                      │
                                      └── allow_restart 실패 → Open 재전이
```

### 5.3 Suspended 상태에서의 복구

- operator 가 Tauri IPC `vamos:bridge:unsuspend` 또는 UI 버튼으로 수동 해제.
- 해제 시 circuit breaker 강제 Reset + state → Idle + 새 `spawn()` 호출.
- 해제 커맨드 권한: `bridge:admin` scope 필수 (T1-1 secure_commands 참조 — 경계).

---

## §6. FR-8 타임아웃 캐스케이드 계층 구조 (정본)

> 본 절은 FR-8 타임아웃 캐스케이드의 **유일한 정본 구조**이다. rpc_protocol.md §6.1 는 본 절을 요약 인용한다 (상호 참조).

### 6.1 4 층 계층도

```
┌──────────────────────────────────────────────────────────────────────────┐
│ L0: Spawn                                                                │
│     - Spawn attempt: 5s × 3 retry                                        │
│     - 정본: spawn_protocol.md §2 Step 9 (_ready 5s + init 30s)           │
│     - 단일 attempt budget: 35s. 총 attempt budget: 105s + backoff.       │
│     ─ 실패 시 상위 전파: L0 exhausted → restart_policy (본 파일) §3 T-04 │
├──────────────────────────────────────────────────────────────────────────┤
│ L1: Healthcheck                                                          │
│     - Interval: 15s (LOCK-RT-12)                                         │
│     - Per-call: 5s (LOCK-RT-12)                                          │
│     - Threshold: 3 consecutive fails (LOCK-RT-12)                        │
│     - 최악 탐지 시간: 3 × 15 + 5 = 50s                                   │
│     ─ 실패 시 상위 전파: L1 exhausted → restart_policy §3 T-01           │
├──────────────────────────────────────────────────────────────────────────┤
│ L2: RPC                                                                  │
│     - process_message: 120s                                              │
│     - 기타 11 메서드: 30s (default)                                      │
│     - health_check (mcp.bridge.health): 5s  ← L1 재사용                  │
│     - shutdown: 10s                                                      │
│     - deadline 전파: Python 측 deadline_ms - 500ms grace (§6.3 rpc_proto)│
│     ─ 실패 시 상위 전파: -32001 timeout → 호출자 반환. restart 불발행     │
│       (단, RPC 실패가 HC 실패의 원인이 되면 L1 카운트 기여)              │
├──────────────────────────────────────────────────────────────────────────┤
│ L3: Graceful Shutdown                                                    │
│     - Shutdown RPC: 10s (L2 상한)                                        │
│     - Pending drain: 5s                                                  │
│     - SIGTERM → wait: 5s                                                 │
│     - SIGKILL fallback (즉시)                                            │
│     - 총 최악 경과: 10 + 5 + 5 = 20s (단, §4.2 Step 4.1 best-effort 500ms │
│       적용 시 5 + 5 = 10s)                                               │
│     ─ 실패 시 상위 전파: GracefulShutdownFailed → T-06 backoff 비정상 경로│
└──────────────────────────────────────────────────────────────────────────┘
```

### 6.2 상위 전파 규칙 (L → L+1)

| 발원 계층 | 실패 조건 | 상위 전파 결과 | restart backoff |
|---|---|---|---|
| **L0** Spawn | attempt 3회 실패 | restart_policy T-04 (SpawnExhausted) | 비정상 경로 1→2→4→8→16s (attempt 4,5) |
| **L1** HC | 연속 3회 실패 | restart_policy T-01 (HealthcheckExhausted) | HC 경로 2→4→8s |
| **L1** HC | elapsed ≥ 5s | L1 실패 카운트 +1 (restart 아직 없음) | — |
| **L2** RPC | tokio::timeout Err | `-32001 python_bridge_timeout` 호출자 반환 | **restart 아님** (RPC 층 복구) |
| **L2** RPC | Python 측 -32020 workflow_cancelled | 호출자 반환 | restart 아님 |
| **L2** RPC | stdin broken pipe | restart_policy T-05 (PipeBroken) | 비정상 경로 |
| **L3** Graceful | 5s 초과 | SIGKILL + T-06 (GracefulShutdownFailed) | 비정상 경로 1회 |
| **L3** Graceful | shutdown RPC -32000 | SIGKILL 즉시 + T-06 (GracefulShutdownFailed) | 비정상 경로 |

### 6.3 하위 재시도와 상위 계층의 관계

- **L0 내부 재시도 3회** (_ready 타임아웃 등) 는 상위 L1 HC 와 **무관**. Spawn 중에는 HC 루프가 게이트로 skip 됨 (healthcheck.md §3.5).
- **L1 내부 재시도 3회** 는 상위 L3 shutdown 과 독립. L1 exhausted 시점에 L3 를 경유하여 재시작.
- **L2 내부 재시도는 없음**. RPC 타임아웃은 호출자 반환만 수행 (rpc_protocol.md §6.3). 재시도는 IPC 호출자(T1-1 commands) 레벨에서 결정.
- **L3 는 상위가 없음** (최상위). 실패 시 바로 Suspended 전환 또는 operator 알림.

### 6.4 cascade 실패 최악 경과 (worst case)

```
시나리오: "사용자 shutdown 요청 중 Python 측 stall"
  T+0s     : user triggers shutdown()
  T+0s     : Step 3 drain pending (즉시)
  T+0.5s   : Step 4.1 shutdown RPC best-effort write (500ms cap)
  T+5.5s   : Step 4.2 drain 5s grace 초과
  T+5.5s   : Step 4.3 SIGTERM
  T+10.5s  : Step 4.4 5s wait 초과
  T+10.5s  : Step 4.5 SIGKILL
  T+10.5s  : T-06 (GracefulShutdownFailed) → backoff 1s
  T+11.5s  : spawn() 재진입
  T+16.5s  : spawn _ready 5s timeout (최악)
  T+16.5s  : attempt 2 backoff 2s
  T+18.5s  : spawn attempt 2
  ...
  최악 상한: L3(10.5s) + 5 × (spawn 35s + backoff) = 약 200s 내 Suspended 전환
```

- **즉시 복구 목표 SLA**: 10s (T-07 operator requested, backoff 0) + spawn 35s = 45s.
- **평균 복구**: T-01 HC 2s + spawn 8s = 10s.

---

## §7. OOM 처리 (Exit 137)

### 7.1 감지 경로

| 경로 | 소스 | 조건 |
|---|---|---|
| Unix | `Child::wait()` 결과 `ExitStatus::code() == Some(137)` | OOM killer 또는 Job Object |
| Unix (signal) | `ExitStatus::signal() == Some(9)` (SIGKILL) + RSS ≥ 95% 직전 기록 | OOM killer 추정 |
| Windows | Job Object 가 `JOB_OBJECT_LIMIT_JOB_MEMORY` 초과로 종료 → exit code 를 137 로 정규화 | §7.3 |
| stderr | `OOMKilled` / `MemoryError` 마지막 라인 감지 | 보조 지표 |

### 7.2 OOM 처리 절차

```
T+0      : reader task EOF + exit 137 감지
T+0      : state = Dead
T+0      : restart_policy §3 T-03 OutOfMemory 트리거
T+0      : RestartCause::OutOfMemory { pid: last_pid }
T+0      : BackoffSchedule::OomFixed5s (정본 §2.1)
T+0      : memory_limit_mb 상향 제안 (config.python_max_memory_mb * 1.5, 최대 4GB cap)
T+0      : CircuitBreaker.allow_restart() 확인
T+5s     : spawn_inner() attempt 1
          실패 시 → attempt 2 backoff 5s (고정) → attempt 3 5s → Suspended
```

### 7.3 Windows exit code 정규화

```rust
#[cfg(windows)]
fn normalize_exit_code(raw: Option<i32>) -> Option<i32> {
    match raw {
        Some(-1073741819) /* 0xC0000005 STATUS_ACCESS_VIOLATION */ => Some(139),
        Some(-1073741801) /* 0xC0000017 STATUS_NO_MEMORY */        => Some(137),
        Some(-1073741523) /* 0xC000012D STATUS_COMMITMENT_LIMIT */  => Some(137),
        Some(-1073741523) /* 0xC000012D STATUS_COMMITMENT_LIMIT */  => Some(137),
        Some(-1073741502) /* 0xC0000142 STATUS_DLL_INIT_FAILED */  => Some(127),
        other => other,
    }
}
```

- Job Object 가 종료한 경우 별도 GetExitCodeJobObject 대신 GetProcessTimes + 메모리 피크 기록으로 OOM 판정.

### 7.4 OOM 이후 backoff 정상 진입 여부 (명시)

**결정**: OOM 은 **5s 고정 × 3회** 를 소진하면 Suspended 전환하며, **비정상 종료 경로(1→2→4→8→16s) 로 자동 전환하지 않는다**.

- 근거: LOCK-RT-13 정본 (상세명세 §D-3) 에서 OOM 경로와 비정상 종료 경로는 **배타적 선택지**로 제시되어 있다. 5s 고정 후 비정상 경로로 엎어갈 경우 LOCK-RT-13 의 "OOM: 3회 5s 고정" 불변식이 깨진다.
- 예외: operator 수동 개입(T-07) 또는 circuit breaker HalfOpen 해제 후에는 `RestartCause::OperatorRequested` 로 재진입하여 Immediate 스케줄.
- 본 결정은 spawn_protocol.md §7.4 "제안 1 잠정 매핑" 과 일관된 최소 보수 정책이다.

### 7.5 메모리 한도 상향 제안

- OOM 3회 소진 후 Suspended 시점에 structured log event `python_bridge_memory_limit_proposal` 발행.
- `config.python_max_memory_mb` 값과 `history_max_rss_bytes` 비교 → operator UI 에 "2GB → 3GB 상향 권장" 알림.
- 자동 상향은 **하지 않는다** — 사용자 머신 RAM 상한을 모르기 때문.

---

## §8. Circuit Breaker 의사코드 — 시간복잡도 정리

§5.2.2 의사코드의 복잡도 증명.

### 8.1 amortized 분석

- `allow_restart` 내부 while 루프는 `VecDeque::pop_front` 만 호출한다.
- 각 Instant 는 최대 1회 push_back 후 최대 1회 pop_front 된다.
- N 개 push_back 에 대해 총 pop_front 호출 수는 최대 N.
- 따라서 **N 회 allow_restart 호출 총 비용은 O(N)** → **단일 호출 amortized O(1)**.

### 8.2 worst case

- 단일 호출의 worst case 는 O(max_restarts) (모든 요소가 윈도우 초과 시 한 번에 정리).
- max_restarts = 10 고정이므로 **실질적으로 O(10) = O(1)**.

### 8.3 공간복잡도

- `VecDeque<Instant>` 최대 길이 = max_restarts = 10.
- `Instant` 는 16 B (리눅스) ~ 24 B (Windows). 총 ≤ 240 B.

---

## §9. FailureCodeRegistry 매핑 (LOCK-RT-07)

### 9.1 [CFL-RT-009 RESOLVED-DEFERRED (CC-T14-01)] 상속

spawn_protocol.md §7, healthcheck.md §9 에 이어 본 파일도 상속. 해소 상태: **RESOLVED-DEFERRED** (CONFLICT_LOG v1.2, 2026-04-11) — 4-1 로컬 `rt.py_bridge.*` 네임스페이스 처리 + 6-12 V4 cross-handoff. 요약:

| 내부 레이블 | JSON-RPC code | TauriError variant | 발생 섹션 |
|---|---|---|---|
| `RESTART_TRIGGERED` | (event only) | — | §4 Step 1 |
| `RESTART_BACKOFF_WAIT` | (event only) | — | §4 Step 8.1 |
| `GRACEFUL_SHUTDOWN_OK` | (event only) | — | §4.2 4.4 Ok |
| `GRACEFUL_SHUTDOWN_HARD_KILL` | -32000 | `PythonBridgeError` | §4.2 4.5 |
| `RESTART_EXCEEDED` | -32000 `python_bridge_unhealthy` | `PythonBridgeError` | §5.1 max_attempts |
| `CIRCUIT_BREAK_OPEN` | -32000 | `PythonBridgeError` | §5.2.3 Open 상태 |
| `OOM_RESTART` | -32003 `python_bridge_oom` | `PythonBridgeError` | §7 |
| `PIPE_BROKEN` | -32004 `python_bridge_pipe` | `IoError` | §3 T-05 |
| `SUSPENDED` | -32000 | `PythonBridgeError` | §5.3 |

### 9.2 6-12 V4 통합 후 canonical 매핑 (cross-handoff 대기)

- `RESTART_EXCEEDED` → `PY_BRIDGE_RESTART_EXCEEDED`
- `CIRCUIT_BREAK_OPEN` → `PY_BRIDGE_CIRCUIT_OPEN`
- `OOM_RESTART` → `PY_BRIDGE_OOM_AT_START` (OOM 이 start 직후인 경우) 또는 신규 `PY_BRIDGE_OOM_RUNTIME` 추가 요청

### 9.3 ProcessFailureEscalation 재사용

본 파일은 spawn_protocol.md §9.3 `ProcessFailureEscalation` 구조체를 **그대로 재사용**한다. 중복 정의하지 않는다. `ProcessPhase::Restart` / `ProcessPhase::Shutdown` 값이 본 파일 경로에서 설정된다.

---

## §10. Phase 2 테스트 시나리오 (10건 이상)

### TC-RESTART-01 — 비정상 종료 backoff 순서
- **조건**: Python 프로세스 매 spawn 마다 즉시 exit 1 (mock).
- **기대**: 5 attempt, backoff 1s/2s/4s/8s/16s, 6번째 Suspended.
- **검증**: 각 sleep 간격 ±50ms. 총 경과 ≈ 31s + 5 × spawn 시도 시간.

### TC-RESTART-02 — HC 실패 경로 backoff
- **조건**: TC-HC-04 (HC 3회 실패) 연속 발생.
- **기대**: backoff 2s/4s/8s, 4번째 Suspended.
- **검증**: RestartCause::HealthcheckExhausted 로그.

### TC-RESTART-03 — OOM 5s 고정
- **조건**: 매 spawn 후 10s 내에 exit 137.
- **기대**: 3 attempt, 각 backoff 5.0±0.2s.
- **검증**: BackoffSchedule::OomFixed5s, 4번째 Suspended, memory_limit_proposal 이벤트.

### TC-RESTART-04 — Graceful shutdown 성공 (L3 happy)
- **조건**: 진행 중 RPC 3건, shutdown() 호출.
- **기대**: Step 4.1 shutdown RPC 송출, Step 4.2 5s 내 3건 완료, Step 4.3 SIGTERM, Step 4.4 3초 내 exit 0.
- **검증**: GracefulResult::Graceful, 총 경과 ≤ 10s.

### TC-RESTART-05 — Graceful shutdown fallback SIGKILL
- **조건**: Python 측 SIGTERM 무시.
- **기대**: Step 4.5 SIGKILL, GracefulResult::HardKilled, T-06 트리거 (재시작 1회).
- **검증**: 총 경과 10.5±0.5s.

### TC-RESTART-06 — restart 중 동시 spawn 호출
- **조건**: restart() 진행 중 다른 태스크가 spawn() 호출.
- **기대**: spawn_mutex 로 직렬화, spawn() 은 restart() 완료 후 실행. 이중 child 생성 없음.
- **검증**: FR-5 불변식 유지.

### TC-RESTART-07 — circuit breaker OPEN 전이
- **조건**: 10분 내 11회 restart 시도.
- **기대**: 11번째 `allow_restart` 호출 false, state=Open, opened_at 기록.
- **검증**: 이후 10분간 모든 restart 거부, operator 알림 이벤트.

### TC-RESTART-08 — circuit breaker HalfOpen 복구
- **조건**: TC-RESTART-07 후 10분 + 1s 대기.
- **기대**: state=HalfOpen, 다음 spawn 시도 1회 허용.
- **검증**: 성공 시 Closed, 실패 시 Open 재전이.

### TC-RESTART-09 — OOM 이후 비정상 경로 전환 금지 (§7.4)
- **조건**: OOM 3회 소진.
- **기대**: Suspended, 자동으로 1s/2s/4s 비정상 경로 진입하지 **않음**.
- **검증**: operator 수동 해제 전까지 spawn 미발행.

### TC-RESTART-10 — operator 즉시 재시작 (T-07)
- **조건**: Tauri IPC `vamos:bridge:restart` 호출.
- **기대**: backoff 0s 즉시 spawn, BackoffSchedule::Immediate.
- **검증**: 총 경과 ≤ spawn 시간 + 100ms.

### TC-RESTART-11 — pending drain 완전성 (§4.3 Step 3)
- **조건**: pending map 에 20 건 존재, restart() 진입.
- **기대**: 20건 모두 `-32000 python_bridge_unhealthy` 수신.
- **검증**: 호출자 측 20건 timeout 없음 (즉시 에러 반환).

### TC-RESTART-12 — spawn() 재진입 데드락 방지 (§4.4)
- **조건**: restart() 가 spawn_inner() 를 호출 (내부 lockless 경로).
- **기대**: 데드락 없음, spawn_mutex 는 restart() 시작 시 1회만 잠김.
- **검증**: 정상 완료.

### TC-RESTART-13 — restart 중 stdin write 실패
- **조건**: Step 4.1 shutdown RPC write 시 pipe broken.
- **기대**: 500ms cap 내 실패 감지, Step 4.2 skip, 즉시 Step 4.3 SIGTERM.
- **검증**: Step 4.1 실패가 전체 경로 지연시키지 않음.

### TC-RESTART-14 — FR-8 L0→L1 전파
- **조건**: spawn 3 attempt 실패 (T-04).
- **기대**: RestartCause::SpawnExhausted, 비정상 경로 attempt 4~5 시도 (1→2→4→8→16s 에서 attempt 4,5 만).
- **검증**: LOCK-RT-13 최대 5회 유지.

### TC-RESTART-15 — FR-8 L3→L0 전파 (GracefulShutdownFailed → spawn 재진입)
- **조건**: shutdown fallback SIGKILL 후 operator 아닌 자동 경로.
- **기대**: T-06 GracefulShutdownFailed → backoff 1s → spawn.
- **검증**: circuit breaker 카운트 +1.

---

## §11. 구조화 로그 JSON

### 11.1 restart 이벤트 로그

```json
{
  "timestamp": "2026-04-11T03:05:00.000Z",
  "level": "info",
  "logger": "bridge.python_manager.restart",
  "event": "python_bridge_restart",
  "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "correlation_id": "restart_session_42",
  "context": {
    "cause": {
      "kind": "HealthcheckExhausted",
      "fails": 3
    },
    "schedule": "Hc2_4_8s",
    "max_attempts": 3,
    "current_attempt": 1,
    "backoff_ms": 2000,
    "last_pid": 12345,
    "last_exit_code": null,
    "last_stderr_tail": [],
    "process_state_prev": "Unhealthy",
    "process_state_next": "Restarting",
    "circuit_breaker": {
      "state": "Closed",
      "window_restarts": 3,
      "window_max": 10,
      "window_s": 600
    }
  },
  "recovery": {
    "action": "backoff_then_spawn",
    "retry_count": 1,
    "backoff_ms": 2000,
    "next_state": "Spawning",
    "handoff_to": "spawn_protocol.md §2 Step 1"
  }
}
```

### 11.2 circuit breaker OPEN 이벤트

```json
{
  "timestamp": "2026-04-11T03:30:00.000Z",
  "level": "critical",
  "logger": "bridge.python_manager.circuit_breaker",
  "event": "python_bridge_circuit_open",
  "context": {
    "window_restarts": 11,
    "window_max": 10,
    "window_s": 600,
    "cooldown_s": 600,
    "opened_at": "2026-04-11T03:30:00.000Z"
  },
  "recovery": {
    "action": "suspend_automatic_restart",
    "next_state": "Suspended",
    "operator_required": true,
    "handoff_to": "operator ack via vamos:bridge:unsuspend"
  }
}
```

### 11.3 이벤트 카탈로그

| event | level | 발생 시점 | 필수 context |
|---|---|---|---|
| `python_bridge_restart_triggered` | info | restart() 진입 | cause, schedule |
| `python_bridge_drain_pending` | debug | §4 Step 3 | drained_count |
| `python_bridge_graceful_shutdown_start` | info | §4 Step 4 진입 | |
| `python_bridge_graceful_shutdown_ok` | info | §4.2 Graceful | exit_code |
| `python_bridge_graceful_shutdown_hard_kill` | warn | §4.2 HardKilled | elapsed_ms |
| `python_bridge_restart_backoff_wait` | debug | §4 Step 8.1 | attempt, backoff_ms |
| `python_bridge_restart_ok` | info | spawn 성공 | attempt, elapsed_ms |
| `python_bridge_restart_exceeded` | error | max_attempts 소진 | cause, total_attempts |
| `python_bridge_circuit_open` | critical | §5.2 Open 전이 | window_restarts |
| `python_bridge_circuit_halfopen` | info | cooldown 경과 | |
| `python_bridge_circuit_closed` | info | HalfOpen 성공 | |
| `python_bridge_oom` | error | exit 137 감지 | last_rss_bytes, memory_limit_mb |
| `python_bridge_memory_limit_proposal` | warn | §7.5 | proposed_limit_mb |
| `python_bridge_suspended` | critical | §5.3 Suspended 전이 | reason |
| `python_bridge_unsuspended` | info | operator ack | operator_id |

- **LOCK-RT-15**: Rust `tracing` crate → `logs/rust_bridge.log`.

---

## §12. LOCK 교차 점검표

| LOCK ID | 본 파일 준수 항목 | 섹션 | 재정의? |
|---|---|---|---|
| LOCK-RT-04 | `python_manager.rs::restart()/shutdown()` 인터페이스 + spawn_inner() 경계 | §4, §1 | 없음 |
| LOCK-RT-07 | 48건 정본 내 restart 실패 코드 부재 인지 + 잠정 매핑 (REF-only, 소유 = 6-12) | §9 (CFL-RT-009 RESOLVED-DEFERRED 상속) | 없음 |
| LOCK-RT-11 | shutdown RPC JSON-RPC 프레이밍 | §4.2 | 없음 |
| LOCK-RT-12 | 재시작 후 HC 루프 재기동 시 15s 주기 불변 | §4 Step 9.1, §6.1 L1 | 없음 |
| LOCK-RT-13 | **backoff 1→2→4→8→16s / OOM 5s 고정 / HC 2→4→8s** 정본 수치만 인용 | §2, §3, §4, §7 | **없음 (재정의 절대 금지)** |
| LOCK-RT-14 | TauriError 매핑 (PythonBridgeError, Timeout, IoError) | §9 | 없음 |
| LOCK-RT-15 | Rust tracing → rust_bridge.log, Python stderr → python_engine.log | §11.3 | 없음 |

- **LOCK 변경 필요 여부**: 없음.
- **CFL-RT-009 RESOLVED-DEFERRED (CC-T14-01, FailureCodeRegistry 확장 12건)**: spawn_protocol.md §7.3 에서 최초 등재, 본 파일은 상속. CONFLICT_LOG v1.2 에 CFL-RT-009 RESOLVED-DEFERRED 등재 완료 (2026-04-11). 4-1 로컬 `rt.py_bridge.*` 네임스페이스 즉시 적용 + PY_BRIDGE_* 12건은 6-12 Event-Logging V4 cross-handoff 이관.
- Circuit Breaker 10분/10회 값은 LOCK 이 아닌 config override 가능 값.

---

## §13. 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|---|---|---|---|
| v0.1 | 2026-04-11 | 초기 작성 (T1-4 step 1). §1~§12 신규. LOCK-RT-13 정본 backoff 전수 준수 (비정상 1→2→4→8→16s 5회, OOM 5s 3회, HC 2→4→8s 3회). RestartCause enum / BackoffSchedule DEFINED-HERE. §4 재시작 10-Step 절차 (drain → graceful 5s → SIGTERM/SIGKILL → backoff → spawn_inner 재진입). §5 Circuit Breaker 3-state (Closed/Open/HalfOpen) + sliding window O(1) amortized. §6 FR-8 타임아웃 캐스케이드 4 계층 정본 (L0 Spawn / L1 HC / L2 RPC / L3 Graceful). §7 OOM 5s 고정 후 비정상 경로 전환 금지 명시. §8 circuit breaker 복잡도 증명. Phase 2 테스트 시나리오 15건. CC-T14-01 (FailureCodeRegistry 확장 12건) 상속. T1-3 rpc_protocol.md §6.1 L0~L3 / §7.7 restart()/shutdown() 선정의와 1:1 정합. | T1-4 Subagent |
| v0.2 | 2026-04-11 | T1-4 step 2 재검증. §12 LOCK 교차 점검표의 "CFL-RT-004 (FailureCodeRegistry 확장 12건 제안)" 표기를 "CC-T14-01 (신규 CFL 번호는 step 7 에서 할당, `CFL-RT-006` 이후 예상 — CFL-RT-004/005 는 T0-5 점유)" 로 정정. LOCK-RT-12/13 정본 수치 재정의 없음 재확인. T1-3 rpc_protocol.md §6.1 L0~L3 / §7.7 restart()/shutdown() 선정의와 1:1 정합 확인. §2~§11 본문 L3 내용 무변경. | T1-4 Subagent |
| v0.3 | 2026-04-11 | 4-1 Deep Reverify — §1/§9.1/§12 의 `[CONFLICT_CANDIDATE CC-T14-01]` 마커를 `[CFL-RT-009 RESOLVED-DEFERRED (CC-T14-01)]` 정규 참조로 정정 (CONFLICT_LOG v1.2 반영). §9.2 헤딩을 "6-12 V4 통합 후 canonical 매핑" 으로 갱신. §12 LOCK-RT-07 행에 "REF-only (소유 = 6-12)" 명시. §12 CFL 단락을 RESOLVED-DEFERRED 설명으로 갱신. | Deep Reverify |

<!-- END OF DOCUMENT -->

---

# §V2. Prometheus 모니터링 메트릭 — T2-4 (restart_policy)

> **Phase 2 T2-4 산출물** (plan §7 T2-4 L1039~L1074 + §B.4 L1327~L1338 정본 verbatim)
> **작성일**: 2026-04-24
> **대상 V1**: restart_policy.md §1~§13 불변 (baseline SHA `2e6043b657358c6c`, 39309 bytes, 767 lines)
> **LOCK 근거**: LOCK-RT-13 (Backoff, DEFINED-HERE §D-3) 정본 · LOCK-RT-12 (HC, REF) · LOCK-RT-15 (stderr 분리)

## §V2.1 교차 참조 블록

| 대상 | 경로 | 관계 |
|-----|-----|------|
| **plan 정본** | RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md §B.4 L1327~L1338 + §7 T2-4 L1039~L1074 | Prometheus 메트릭 정본 |
| **FR-8 타임아웃 캐스케이드** | plan §11 FR-8 (Spawn 5s×3 / 메시지 120s / HC 15s) | 본 §V2.3 연동 정본 |
| **LOCK-RT-13 DEFINED-HERE** | RUST_TAURI_INFRASTRUCTURE_상세명세.md §D-3 L360~L365 | backoff 정본 |
| **peer V2 (T2-4 EXTEND)** | spawn_protocol.md §V2 + healthcheck.md §V2 | restart 원인 경로 |
| **peer V2 (T2-1 NEW)** | 04_build-signing/code_signing.md §4.4 업데이트 후 재시작 | update-driven restart |
| **V1 §1~§12** | restart_policy.md §4 재시작 10-Step + §5 Circuit Breaker 3-state + §6 FR-8 4 계층 | 본 §V2 source of truth |

## §V2.2 대상 메트릭 1종 (restart_policy 담당)

| # | 메트릭 이름 | 타입 | 라벨 | 단위 | 설명 |
|---|-------------|------|-----|------|-----|
| 1 | `python_bridge_restart_total` | Counter | `cause`, `phase` | count | Python 프로세스 재시작 횟수 (cause: abnormal_exit / oom_kill / healthcheck_fail / user_manual / update_applied; phase: 0=initial / 1=first_retry / 2=second / 3=third / 4=fourth / 5=circuit_open) |

### Prometheus client Rust
```rust
use prometheus::{CounterVec, register_counter_vec};
use once_cell::sync::Lazy;

pub static RESTART_TOTAL: Lazy<CounterVec> = Lazy::new(|| register_counter_vec!(
    "python_bridge_restart_total",
    "Python bridge restart count",
    &["cause", "phase"]
).expect("register"));

// Usage example
pub fn record_restart(cause: RestartCause, phase: u8) {
    RESTART_TOTAL.with_label_values(&[cause.as_str(), &phase.to_string()]).inc();
}
```

## §V2.3 LOCK-RT-13 Backoff 알림 규칙 (DEFINED-HERE §D-3)

| 조건 | 정책 | PromQL |
|------|-----|--------|
| 비정상 종료 (exit != 0) 1회 | 1s backoff | `increase(python_bridge_restart_total{cause="abnormal_exit",phase="1"}[30s]) >= 1` |
| 비정상 종료 2회 | 2s | phase=2 |
| 비정상 종료 3회 | 4s | phase=3 |
| 비정상 종료 4회 | 8s | phase=4 |
| 비정상 종료 5회 | 16s | phase=5 |
| 비정상 종료 6회 | Circuit Open 30s | phase=6 |
| OOM (137) 1~3회 | 5s 고정 | `increase(python_bridge_restart_total{cause="oom_kill"}[5m]) >= 3` → `critical` |
| HC 실패 1회 | 2s | `{cause="healthcheck_fail",phase="1"}` |
| HC 실패 2회 | 4s | phase=2 |
| HC 실패 3회 | 8s | phase=3 → Circuit Open |
| 1 min 내 2회 이상 restart | Critical 알림 | `increase(python_bridge_restart_total[1m]) >= 2` |
| 5 min 내 5회 이상 restart | Pager | `increase(python_bridge_restart_total[5m]) >= 5` |

### 백오프 스케줄 상수 (V1 §4.3 정본 참조)
```rust
const BACKOFF_ABNORMAL: [Duration; 5] = [
    Duration::from_secs(1), Duration::from_secs(2), Duration::from_secs(4),
    Duration::from_secs(8), Duration::from_secs(16)
];
const BACKOFF_OOM: Duration = Duration::from_secs(5);
const BACKOFF_HC: [Duration; 3] = [
    Duration::from_secs(2), Duration::from_secs(4), Duration::from_secs(8)
];
```

## §V2.4 FR-8 타임아웃 캐스케이드 상호작용 (plan §11 FR-8)

| 계층 | 타임아웃 | 캐스케이드 | 메트릭 연동 |
|------|----------|-----------|-------------|
| L0 Spawn | 5s × 3 retry | 실패 시 LOCK-RT-13 비정상 경로 → restart_total{cause="abnormal_exit"} | spawn_protocol.md §V2.3 FR-5 |
| L1 Initialize RPC | 30s | 실패 → spawn_retry (L0 재진입, 최대 3회) | duration_seconds{method="initialize"} |
| L2 HC | 15s 주기 / 5s timeout | 3회 실패 → restart_total{cause="healthcheck_fail"} | healthcheck.md §V2.2 |
| L3 Message RPC | process_message 120s / 나머지 30s | Timeout → 단일 RPC 실패 (재시작 무관) | rpc_duration_seconds P99 |
| L4 Graceful shutdown | SIGTERM 5s → SIGKILL | shutdown_timeout → `rt.py_bridge.shutdown_timeout` | restart_total{cause="healthcheck_fail"} + stderr 로그 |

- **Circuit Breaker (V1 §5 정본)**: L0/L2 재시도 한도 초과 → `Open` 30s → `HalfOpen` 1 probe → `Closed/Open` 결정
- **FR-8 계층 타임아웃 합**: Spawn (5×3=15s) + Init (30s) + HC (5s timeout × 3 probe = 15s+15s 간격) + Graceful (5s) = 약 80s 이내 복구 경계

## §V2.5 LOCK 5필드 매핑

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-RT-13 | Restart backoff 정책 | 상세명세 §D-3 L360~L365 (DEFINED-HERE) | 비정상 5회 1→2→4→8→16s / OOM 3회 5s / HC 3회 2→4→8s | ❌ (본 파일 정본 소유) |
| LOCK-RT-12 | Python HC 주기 | 상세명세 §D-2 L352~L356 (DEFINED-HERE) | 15s / 5s / 3회 | ❌ (REF, healthcheck.md §V2 정본) |
| LOCK-RT-15 | stderr 로그 분리 | PHASE_B2 + Part2 V0-STEP-3 | stdout=JSON-RPC / stderr=로그 | ❌ |

## §V2.6 SLA 위반 ↔ Restart 상관 (plan §A.3 ↔ §B.4)

| 카테고리 | 메트릭 영향 | 임계 |
|----------|------------|-----|
| System/Health P99 ≤ 30ms 초과 지속 → HC timeout → restart | `rate(python_bridge_restart_total{cause="healthcheck_fail"}[1h]) > 0.001` (1h 내 3회+) | `warn` |
| Conversation P99 ≤ 200ms 초과 → Python 성능 저하 → 재시작 고려 | `rate(python_bridge_restart_total{cause="abnormal_exit"}[1h]) > 0.002` | `warn` |
| OOM 반복 → Python memory 한도 상향 권고 | `increase(python_bridge_restart_total{cause="oom_kill"}[1h]) >= 3` | `critical` (설정 조정 필요) |

## §V2.7 구조화 로그 3-block

### block-1: LOCK-RT-13 비정상 종료 + backoff 진입
```json
{
  "source": "rust_tauri.process.restart",
  "event": "restart.backoff.scheduled",
  "cause": "abnormal_exit",
  "attempt": 2,
  "backoff_seconds": 2,
  "exit_code": 1,
  "severity": "Warn"
}
```

### block-2: OOM 5s 고정 backoff
```json
{
  "source": "rust_tauri.process.restart",
  "event": "restart.oom.backoff",
  "cause": "oom_kill",
  "attempt": 1,
  "backoff_seconds": 5,
  "exit_code": 137,
  "memory_limit_mb": 2048,
  "severity": "Error"
}
```

### block-3: Circuit Breaker OPEN
```json
{
  "source": "rust_tauri.process.restart",
  "event": "restart.circuit.open",
  "cause": "abnormal_exit",
  "total_attempts": 6,
  "window_seconds": 600,
  "next_probe_in_s": 600,
  "severity": "Critical"
}
```

## §V2.8 Phase 3 테스트 시나리오 (≥ 10건)

1. TS-M-RS-1 — 정상 1회 비정상 종료 → restart_total{cause="abnormal_exit",phase="1"} = 1, backoff 1s
2. TS-M-RS-2 — 연속 5회 비정상 → phase 1→2→3→4→5 (1s/2s/4s/8s/16s) + 6회 시 Circuit Open
3. TS-M-RS-3 — OOM 3회 → restart_total{cause="oom_kill"} = 3, 각 5s backoff, `critical` 알림
4. TS-M-RS-4 — HC 3회 실패 → restart_total{cause="healthcheck_fail",phase="1,2,3"} 2s/4s/8s
5. TS-M-RS-5 — Circuit Open 30s 후 HalfOpen 1 probe → 성공 시 Closed, 실패 시 Open 유지
6. TS-M-RS-6 — User manual stop → restart_total{cause="user_manual"} = 1, backoff 없음
7. TS-M-RS-7 — Update applied (T2-1 code_signing 경로) → restart_total{cause="update_applied"}
8. TS-M-RS-8 — 1 min 내 2회 restart → `critical` Alertmanager 발화
9. TS-M-RS-9 — FR-8 L0 Spawn 5s×3 timeout → abnormal_exit 전환 정확성
10. TS-M-RS-10 — backoff 스케줄 정확도 (1/2/4/8/16 oracle vs 실측 ±100ms)
11. TS-M-RS-11 — restart_total Counter reset (process graceful shutdown → restart) 연속성
12. TS-M-RS-12 — Circuit Open 중 요청 → 즉시 `PythonBridgeError {code=503, message=bridge_unavailable}` 반환
13. TS-M-RS-13 — OOM backoff 중 manual kill → 경로 전환 (oom_kill → user_manual)
14. TS-M-RS-14 — Cross-cause 우선순위 (OOM > abnormal_exit > healthcheck_fail) 충돌 없음
15. TS-M-RS-15 — Prometheus counter monotonic (restart_total 감소 0건)

## §V2.9 자가 체크리스트

- [x] §1 교차 참조 블록 (§V2.1): plan §B.4 + FR-8 + 상세명세 §D-3 + peer 2 V2 + T2-1 code_signing + V1 §4/§5/§6 전수
- [x] §2 공통 자료 구조 참조 (§V2.5): LOCK-RT-13/12/15 3 row 5필드 분리 인용
- [x] §3 구현 상세 (§V2.2 Rust + §V2.3 상수): Prometheus client + BACKOFF_* 상수 배열 정본
- [x] §4 기능별 상세 (§V2.3 alert table 12 row + §V2.4 FR-8 4 계층 + §V2.6 SLA 상관 3 row)
- [x] §N LOCK panel + §N 구조화 로그 3-block (§V2.7)
- [x] §N Phase 3 테스트 시나리오 ≥ 10건 (§V2.8): TS-M-RS-1~15 실체화 (총 15)
- [x] §N 세션 간 cross-check: peer T2-4 spawn + healthcheck + T2-1 code_signing + FR-8 plan §11 전수
- [x] 자가 체크리스트 (§V2.9): §3.1~§3.5 anti-fabrication 가이드 준수

---

<!-- END OF §V2 (T2-4 restart_policy) -->
