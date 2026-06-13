//! VAMOS desktop shell — bin entry.
//!
//! STEP 3(P4-2): serde 모델 컴파일 게이트(A20 왕복의 Rust 구간).
//! STEP 5에서 Tauri 셸 + Python 스폰으로 확장된다.

fn main() {
    // serde 모델이 링크되는지 확인 (컴파일 게이트). Tauri 배선은 STEP 5.
    let n = vamos_app_lib::models::MODEL_NAMES.len();
    println!("VAMOS app shell — serde models linked: {n} (Tauri wiring: STEP 5)");
}
