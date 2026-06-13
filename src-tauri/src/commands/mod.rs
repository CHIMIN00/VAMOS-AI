//! Tauri IPC 커맨드 5종 (V0-STEP-3 — PART2 L874~879, L939~972).
//!
//! 모든 커맨드는 `#[tauri::command]` + `Result<T, String>` 반환(M-4). 논리 커맨드명 ↔ 함수:
//!   vamos:decision:create → decision_create  → langgraph.decision.create
//!   vamos:workflow:start  → workflow_start   → langgraph.workflow.run
//!   vamos:ui:log_stream   → ui_log_stream    → (Tauri 이벤트)
//!   vamos:ui:config_get   → ui_config_get    → (Rust 직접)
//!   vamos:ui:config_set   → ui_config_set    → (Rust 직접)

use serde_json::Value;
use tauri::{AppHandle, Emitter, State};

use crate::state::AppState;

#[tauri::command]
pub fn decision_create(state: State<'_, AppState>, input: Value) -> Result<Value, String> {
    state.call("langgraph.decision.create", input)
}

#[tauri::command]
pub fn workflow_start(state: State<'_, AppState>, input: Value) -> Result<Value, String> {
    state.call("langgraph.workflow.run", input)
}

#[tauri::command]
pub fn ui_log_stream(app: AppHandle, subscribe: bool) -> Result<Value, String> {
    // V0: 구독 ACK + Tauri 이벤트 1회 발행(스트림 본체는 V1 로그 파이프라인).
    app.emit("vamos://log", serde_json::json!({"v0_stub": true, "subscribe": subscribe}))
        .map_err(|e| format!("이벤트 발행 실패: {e}"))?;
    Ok(serde_json::json!({"subscribed": subscribe, "v0_stub": true}))
}

#[tauri::command]
pub fn ui_config_get(state: State<'_, AppState>, key: String) -> Result<Value, String> {
    state.config_get(&key)
}

#[tauri::command]
pub fn ui_config_set(state: State<'_, AppState>, key: String, value: String) -> Result<Value, String> {
    state.config_set(&key, &value)
}
