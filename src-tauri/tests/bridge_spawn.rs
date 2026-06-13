//! Python 브릿지 스폰 통합 테스트 — V0-STEP-3 Stage Gate #4/#5/#6.
//!
//! 실제 Python 서버를 스폰하므로 vamos_core를 import 가능한 인터프리터가 필요하다.
//! `VAMOS_PYTHON`(poetry venv python)이 설정된 경우에만 실행되고, 미설정 시 SKIP한다
//! (CI/개발 환경에서 거짓 실패 방지). 실행 드라이버: `poetry run python scripts/ipc_spawn_check.py`.

use std::path::Path;

use serde_json::json;
use vamos_app_lib::bridge::{PythonBridge, SpawnConfig};

fn backend_dir() -> String {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("backend")
        .to_string_lossy()
        .into_owned()
}

#[test]
fn python_spawn_health_dispatch_restart() {
    if std::env::var("VAMOS_PYTHON").is_err() {
        eprintln!("SKIP: VAMOS_PYTHON 미설정 (poetry run python scripts/ipc_spawn_check.py 로 실행)");
        return;
    }

    let config = SpawnConfig::from_env(&backend_dir());

    // #4 스폰 + ready 센티넬 수신 + stdin/stdout 파이프 연결
    let mut bridge = PythonBridge::spawn(config).expect("Python 스폰 + ready 실패");

    // #5 헬스체크 ping → pong
    assert!(bridge.health_check(), "health_check(system.ping→pong) 실패");

    // 정상 디스패치(13 메서드 중 1) — stdin/stdout 파이프 왕복
    let res = bridge
        .call("llm.generate", json!({"trace_id": "t-rs", "prompt": "x"}))
        .expect("llm.generate 디스패치 실패");
    assert_eq!(res["trace_id"], "t-rs");
    assert_eq!(res["v0_stub"], true);

    // #6 비정상 종료 후 자동 재시작 — shutdown으로 프로세스 강제 종료 후 call → 자동 복구
    bridge.shutdown();
    let res2 = bridge
        .call("system.ping", json!({}))
        .expect("재시작 후 호출 실패");
    assert_eq!(res2, "pong");
    assert!(bridge.restart_count() >= 1, "자동 재시작 카운트 증가 확인");
}
