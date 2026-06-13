//! serde 데이터 모델 (A20 — Pydantic 정본에서 자동 생성).
//!
//! `generated.rs`는 `scripts/generate_types.py`가 생성한다(직접 수정 금지 — A20/DEC-006).
//! 본 mod.rs는 손-작성 안정 진입점이다.

mod generated;

pub use generated::{roundtrip_validate, MODEL_NAMES};
// 개별 구조체도 재노출(커맨드/브릿지 계층에서 사용).
pub use generated::*;
