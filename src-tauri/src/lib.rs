//! VAMOS app library root.
//!
//! V0 스코프(P4-2): serde 모델(A20) + Python 브릿지(bridge) + Tauri 커맨드(commands).

pub mod bridge;
pub mod commands;
pub mod models;
pub mod state;

use bridge::SpawnConfig;
use state::AppState;

/// Tauri 셸 진입점. Python 스폰 경로는 env(VAMOS_PYTHON/VAMOS_BACKEND_DIR) 경유(하드코딩 금지).
pub fn run() {
    let app_state = AppState::new(SpawnConfig::from_env("backend"));
    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            commands::decision_create,
            commands::workflow_start,
            commands::ui_log_stream,
            commands::ui_config_get,
            commands::ui_config_set,
        ])
        .run(tauri::generate_context!())
        .expect("Tauri 앱 실행 오류");
}
