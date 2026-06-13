//! Tauri 앱 전역 상태 (Python 브릿지 + 설정) — V0-STEP-3.

use std::collections::HashMap;
use std::sync::Mutex;

use serde_json::Value;

use crate::bridge::{PythonBridge, SpawnConfig};

/// LOCK 설정 키(A21 Layer 1 — config frozen). V0 config_set는 이들을 거부.
const LOCKED_CONFIG_KEYS: &[&str] = &[
    "core.single_decision_lock",
    "cost.warn_threshold",
    "cost.block_threshold",
    "confidence.high_threshold",
    "confidence.medium_threshold",
    "confidence.low_threshold",
];

pub struct AppState {
    /// 지연 스폰되는 Python 브릿지(최초 호출 시 기동).
    bridge: Mutex<Option<PythonBridge>>,
    spawn: SpawnConfig,
    /// V0 인메모리 설정(get/set — Rust 직접 처리). V1에서 config_loader 연동.
    config: Mutex<HashMap<String, String>>,
}

impl AppState {
    pub fn new(spawn: SpawnConfig) -> Self {
        let mut seed = HashMap::new();
        seed.insert("core.autonomy_level".to_string(), "L1".to_string());
        seed.insert("core.default_execution_mode".to_string(), "mini".to_string());
        AppState {
            bridge: Mutex::new(None),
            spawn,
            config: Mutex::new(seed),
        }
    }

    /// 브릿지를 통해 JSON-RPC 호출(최초 호출 시 지연 스폰).
    pub fn call(&self, method: &str, params: Value) -> Result<Value, String> {
        let mut guard = self.bridge.lock().map_err(|_| "bridge lock 실패".to_string())?;
        if guard.is_none() {
            *guard = Some(PythonBridge::spawn(self.spawn.clone())?);
        }
        guard
            .as_mut()
            .expect("bridge 보장됨")
            .call(method, params)
    }

    pub fn config_get(&self, key: &str) -> Result<Value, String> {
        let map = self.config.lock().map_err(|_| "config lock 실패".to_string())?;
        Ok(match map.get(key) {
            Some(v) => Value::String(v.clone()),
            None => Value::Null,
        })
    }

    pub fn config_set(&self, key: &str, value: &str) -> Result<Value, String> {
        if LOCKED_CONFIG_KEYS.contains(&key) {
            return Err(format!("LOCK 설정 키는 변경 불가(A21 L1): {key}"));
        }
        let mut map = self.config.lock().map_err(|_| "config lock 실패".to_string())?;
        map.insert(key.to_string(), value.to_string());
        Ok(Value::Bool(true))
    }
}
