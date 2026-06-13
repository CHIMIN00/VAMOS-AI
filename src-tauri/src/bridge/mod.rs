//! Python AI/ML 프로세스 브릿지 (IPC JSON-RPC over stdin/stdout) — V0-STEP-3.

pub mod python_manager;

pub use python_manager::{PythonBridge, SpawnConfig};
