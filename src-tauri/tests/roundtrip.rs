//! A20 왕복 테스트 (Rust 구간) — DEC-005 §5 / DEC-006.
//!
//! `tests/roundtrip_instances.json`(= scripts/roundtrip_test.py가 Pydantic 정본에서 생성한
//! 25 모델 인스턴스)을 serde 구조체로 역직렬화→재직렬화→재역직렬화하여 동일성을 확인한다.
//! deny_unknown_fields(= Pydantic extra='forbid')로 미지 필드를 거부하는지도 검증한다.

use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use vamos_app_lib::models::{roundtrip_validate, MODEL_NAMES};

#[test]
fn serde_roundtrip_all_models() {
    let dir = env!("CARGO_MANIFEST_DIR");
    let path = Path::new(dir).join("tests").join("roundtrip_instances.json");
    let raw = fs::read_to_string(&path)
        .unwrap_or_else(|e| panic!("fixture 읽기 실패 {path:?}: {e}"));
    let instances: BTreeMap<String, serde_json::Value> =
        serde_json::from_str(&raw).expect("fixture JSON 파싱 실패");

    // 25 모델 전수 존재 (분모 LOCK)
    assert_eq!(
        instances.len(),
        MODEL_NAMES.len(),
        "인스턴스 {} vs 모델 {}",
        instances.len(),
        MODEL_NAMES.len()
    );

    for (name, inst) in &instances {
        let json = serde_json::to_string(inst).unwrap();
        roundtrip_validate(name, &json).unwrap_or_else(|e| panic!("{name} 왕복 실패: {e}"));
    }
}

#[test]
fn deny_unknown_fields_rejects_extra_all_models() {
    // extra='forbid' 등가 — 25 모델 **전건**에 미지 필드 주입 → 거부 확인(1/25 → 25/25 격상).
    let dir = env!("CARGO_MANIFEST_DIR");
    let path = Path::new(dir).join("tests").join("roundtrip_instances.json");
    let raw = fs::read_to_string(&path).expect("fixture 읽기 실패");
    let instances: BTreeMap<String, serde_json::Value> =
        serde_json::from_str(&raw).expect("fixture 파싱 실패");
    assert_eq!(instances.len(), MODEL_NAMES.len());
    for (name, inst) in &instances {
        let mut obj = inst.as_object().cloned().expect("object 인스턴스");
        obj.insert("__unknown_xyz__".to_string(), serde_json::json!(1));
        let bad = serde_json::to_string(&serde_json::Value::Object(obj)).unwrap();
        assert!(
            roundtrip_validate(name, &bad).is_err(),
            "{name}: deny_unknown_fields가 미지 필드를 거부해야 함"
        );
    }
}
