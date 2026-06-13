//! VAMOS desktop shell — bin entry (Tauri 2.0).
//!
//! 실제 셸 로직은 lib(`vamos_app_lib::run`)에 있다(Tauri 2 표준: lib+bin 분리).

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    vamos_app_lib::run();
}
