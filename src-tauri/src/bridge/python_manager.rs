//! Python 프로세스 수명주기 관리 (V0-STEP-3 / PHASE3-DEC-006).
//!
//! 규칙(PART2 L975~982):
//!   - stdin/stdout 파이프만(TCP/HTTP 아님). 한 줄 = 한 JSON-RPC 메시지.
//!   - stderr는 별도 스레드로 읽어 로그(stdout JSON-RPC와 혼선 금지 — M-5).
//!   - 시작 시 Python이 stdout 첫 줄로 ready 센티넬 출력 → Rust 감지.
//!   - 비정상 종료 시 자동 재시작(최대 `ipc_max_restart`=3).
//!   - 요청 타임아웃 `ipc_timeout_s`=30s.
//!
//! 스폰 경로/인터프리터는 **하드코딩 금지** — `SpawnConfig`(env/config 경유)로 주입한다.

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc::{self, Receiver, RecvTimeoutError};
use std::thread;
use std::time::Duration;

use serde_json::{json, Value};

/// Python 서버 스폰 설정 (config/env 경유 — 하드코딩 금지).
#[derive(Debug, Clone)]
pub struct SpawnConfig {
    /// Python 인터프리터 경로(예: poetry venv python). 기본 "python".
    pub python_exe: String,
    /// 실행 모듈(`python -m <module>`).
    pub module: String,
    /// 작업 디렉터리(vamos_core import 가능한 위치 = backend/).
    pub cwd: String,
    /// PYTHONPATH로 추가할 경로(비면 미설정). cwd로 import 안 될 때 보강.
    pub pythonpath: Option<String>,
    /// 요청 타임아웃(초) — config [core].ipc_timeout_s.
    pub timeout_s: u64,
    /// 최대 자동 재시작 — config [core].ipc_max_restart.
    pub max_restart: u32,
}

impl SpawnConfig {
    /// V0 기본값 + 환경변수 오버라이드(VAMOS_PYTHON / VAMOS_BACKEND_DIR / VAMOS_PYTHONPATH).
    pub fn from_env(default_cwd: &str) -> Self {
        let python_exe = std::env::var("VAMOS_PYTHON").unwrap_or_else(|_| "python".to_string());
        let cwd = std::env::var("VAMOS_BACKEND_DIR").unwrap_or_else(|_| default_cwd.to_string());
        let pythonpath = std::env::var("VAMOS_PYTHONPATH").ok();
        SpawnConfig {
            python_exe,
            module: "vamos_core.rpc.server".to_string(),
            cwd,
            pythonpath,
            timeout_s: 30,
            max_restart: 3,
        }
    }
}

/// 살아있는 Python 서버 프로세스 + 파이프.
pub struct PythonBridge {
    config: SpawnConfig,
    child: Child,
    stdin: ChildStdin,
    /// stdout 리더 스레드 → 라인 채널.
    rx: Receiver<String>,
    restart_count: u32,
    next_id: u64,
}

impl PythonBridge {
    /// 프로세스를 스폰하고 ready 센티넬을 수신할 때까지 대기.
    pub fn spawn(config: SpawnConfig) -> Result<Self, String> {
        let (child, stdin, rx) = Self::launch(&config)?;
        let mut bridge = PythonBridge {
            config,
            child,
            stdin,
            rx,
            restart_count: 0,
            next_id: 1,
        };
        bridge.await_ready()?;
        Ok(bridge)
    }

    fn launch(config: &SpawnConfig) -> Result<(Child, ChildStdin, Receiver<String>), String> {
        let mut cmd = Command::new(&config.python_exe);
        cmd.arg("-m")
            .arg(&config.module)
            .current_dir(&config.cwd)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        if let Some(pp) = &config.pythonpath {
            cmd.env("PYTHONPATH", pp);
        }
        // cp949 환경 방어: Python I/O를 UTF-8로 강제(서버도 reconfigure 하지만 이중 안전).
        cmd.env("PYTHONIOENCODING", "utf-8");
        cmd.env("PYTHONUTF8", "1");

        let mut child = cmd
            .spawn()
            .map_err(|e| format!("Python 스폰 실패({}): {e}", config.python_exe))?;

        let stdin = child.stdin.take().ok_or("stdin 핸들 획득 실패")?;
        let stdout = child.stdout.take().ok_or("stdout 핸들 획득 실패")?;
        let stderr = child.stderr.take().ok_or("stderr 핸들 획득 실패")?;

        // stdout 리더 스레드 → 채널 (JSON-RPC 라인).
        let (tx, rx) = mpsc::channel::<String>();
        thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                match line {
                    Ok(l) => {
                        if tx.send(l).is_err() {
                            break; // 수신측 drop → 종료
                        }
                    }
                    Err(_) => break,
                }
            }
        });

        // stderr 리더 스레드 → 로그(stdout JSON-RPC와 분리, M-5).
        thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().map_while(Result::ok) {
                eprintln!("[python] {line}");
            }
        });

        Ok((child, stdin, rx))
    }

    fn await_ready(&mut self) -> Result<(), String> {
        let line = self
            .rx
            .recv_timeout(Duration::from_secs(self.config.timeout_s))
            .map_err(|e| format!("ready 센티넬 대기 실패: {e:?}"))?;
        let v: Value = serde_json::from_str(&line)
            .map_err(|e| format!("ready 파싱 실패: {e} (raw={line})"))?;
        if v.get("method").and_then(Value::as_str) == Some("server.ready") {
            Ok(())
        } else {
            Err(format!("ready 센티넬 아님: {line}"))
        }
    }

    /// JSON-RPC 메서드 호출 → result Value 반환(에러는 Err). 실패 시 1회 재시작 후 재시도.
    pub fn call(&mut self, method: &str, params: Value) -> Result<Value, String> {
        match self.call_once(method, params.clone()) {
            Ok(v) => Ok(v),
            Err(e) => {
                // 파이프 단절 추정 → 재시작 후 1회 재시도(restart budget 내).
                if self.try_restart()? {
                    self.call_once(method, params)
                } else {
                    Err(e)
                }
            }
        }
    }

    fn call_once(&mut self, method: &str, params: Value) -> Result<Value, String> {
        let id = self.next_id;
        self.next_id += 1;
        let req = json!({"jsonrpc": "2.0", "method": method, "params": params, "id": id});
        let line = format!("{req}\n");
        self.stdin
            .write_all(line.as_bytes())
            .map_err(|e| format!("요청 쓰기 실패: {e}"))?;
        self.stdin.flush().map_err(|e| format!("flush 실패: {e}"))?;

        let resp_line = self
            .rx
            .recv_timeout(Duration::from_secs(self.config.timeout_s))
            .map_err(|e| match e {
                RecvTimeoutError::Timeout => format!("응답 타임아웃({}s)", self.config.timeout_s),
                RecvTimeoutError::Disconnected => "파이프 단절".to_string(),
            })?;
        let v: Value =
            serde_json::from_str(&resp_line).map_err(|e| format!("응답 파싱 실패: {e}"))?;
        if let Some(err) = v.get("error") {
            return Err(format!("JSON-RPC error: {err}"));
        }
        v.get("result")
            .cloned()
            .ok_or_else(|| format!("result 부재: {resp_line}"))
    }

    /// 헬스체크: system.ping → "pong" 이면 정상.
    pub fn health_check(&mut self) -> bool {
        matches!(self.call_once("system.ping", json!({})), Ok(Value::String(s)) if s == "pong")
    }

    /// 자동 재시작(restart budget 내). 성공 시 true.
    fn try_restart(&mut self) -> Result<bool, String> {
        if self.restart_count >= self.config.max_restart {
            return Ok(false);
        }
        self.restart_count += 1;
        let _ = self.child.kill();
        let _ = self.child.wait();
        let (child, stdin, rx) = Self::launch(&self.config)?;
        self.child = child;
        self.stdin = stdin;
        self.rx = rx;
        self.await_ready()?;
        Ok(true)
    }

    pub fn restart_count(&self) -> u32 {
        self.restart_count
    }

    /// 명시적 종료.
    pub fn shutdown(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

impl Drop for PythonBridge {
    fn drop(&mut self) {
        self.shutdown();
    }
}
