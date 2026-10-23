//! C6 contract-negative preflight against the current RI-RS typed receipt surface.
//!
//! This file distinguishes native typed-object validation from the missing
//! strict BC-02.1 JSON consumer. Tests reproducing the missing behavior are
//! labelled KNOWN_GAP and do not imply that C6 has passed.

use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use ri_rs_receiver::{receive, validate_schema, BoundaryReceipt, HandoffStatus};
use serde_json::{json, Value};

fn receipt() -> BoundaryReceipt {
    receive(
        "FIX-C6-SYNTHETIC".into(),
        "FIX-C6-SYNTHETIC.bin".into(),
        "synthetic-in-memory-octet-transfer".into(),
        vec![0x43, 0x36, 0x00, 0xfe, 0xff],
        "RI-RS".into(),
        "aura-ri-rs".into(),
        "1.0.0".into(),
        "1111111111111111111111111111111111111111".into(),
        "BC-02.3-RS-P01-HANDOFF-ADAPTER".into(),
        "1.0.0".into(),
        "c6-preflight".into(),
        "linux-x86_64".into(),
        "rust-test-runtime".into(),
    )
}

fn error_starts(receipt: &BoundaryReceipt, prefix: &str) -> bool {
    validate_schema(receipt)
        .err()
        .is_some_and(|error| error.starts_with(prefix))
}

#[test]
fn rejects_wrong_schema_identity_and_version() {
    let mut r = receipt();
    r.schema_id = "BC-02.1-OTHER".into();
    assert!(error_starts(&r, "R-VAL-001"));

    let mut r = receipt();
    r.schema_version = 2;
    assert!(error_starts(&r, "R-VAL-001"));
}

#[test]
fn rejects_missing_fixture_identity_and_empty_method() {
    let mut r = receipt();
    r.fixture.fixture_id.clear();
    assert!(error_starts(&r, "R-VAL-002"));

    let mut r = receipt();
    r.fixture.fixture_artifact_identity.clear();
    assert!(error_starts(&r, "R-VAL-002"));

    let mut r = receipt();
    r.handoff.method.clear();
    assert!(error_starts(&r, "R-VAL-003"));
}

#[test]
fn rejects_length_and_receiver_derived_digest_mismatch() {
    let mut r = receipt();
    r.received.octet_length += 1;
    assert!(error_starts(&r, "R-VAL-004"));

    let mut r = receipt();
    r.received.recomputed_sha256 = "0".repeat(64);
    assert!(error_starts(&r, "R-VAL-005"));
}

#[test]
fn rejects_incomplete_receiver_adapter_and_environment_provenance() {
    let mut r = receipt();
    r.receiver.receiver_id.clear();
    assert!(error_starts(&r, "R-VAL-006/007"));

    let mut r = receipt();
    r.receiver.implementation_id.clear();
    assert!(error_starts(&r, "R-VAL-006/007"));

    let mut r = receipt();
    r.receiver.source_commit.clear();
    assert!(error_starts(&r, "R-VAL-006/007"));

    let mut r = receipt();
    r.adapter.adapter_id.clear();
    assert!(error_starts(&r, "R-VAL-008"));

    let mut r = receipt();
    r.adapter.adapter_version.clear();
    assert!(error_starts(&r, "R-VAL-008"));

    let mut r = receipt();
    r.environment.environment_id.clear();
    assert!(error_starts(&r, "R-VAL-009"));

    let mut r = receipt();
    r.environment.platform.clear();
    assert!(error_starts(&r, "R-VAL-009"));

    let mut r = receipt();
    r.environment.runtime.clear();
    assert!(error_starts(&r, "R-VAL-009"));
}

#[test]
fn invalid_handoff_status_is_rejected_by_the_closed_enum_parser() {
    for value in ["PASS", "FAIL", "CONFORMANT", "NON_CONFORMANT", "UNKNOWN"] {
        let encoded = serde_json::to_string(value).expect("string JSON");
        assert!(
            serde_json::from_str::<HandoffStatus>(&encoded).is_err(),
            "prohibited or unknown handoff status was accepted: {value}"
        );
    }
    assert!(serde_json::from_str::<HandoffStatus>("null").is_err());
    assert!(serde_json::from_str::<HandoffStatus>("1").is_err());
}

#[test]
fn missing_required_struct_field_and_null_field_are_rejected_by_serde() {
    let mut value = serde_json::to_value(receipt()).expect("receipt JSON value");
    value.as_object_mut().expect("top-level object").remove("environment");
    assert!(serde_json::from_value::<BoundaryReceipt>(value).is_err());

    let mut value = serde_json::to_value(receipt()).expect("receipt JSON value");
    value["fixture"] = Value::Null;
    assert!(serde_json::from_value::<BoundaryReceipt>(value).is_err());
}

#[test]
fn known_gap_serde_ignores_an_extra_authority_bearing_field() {
    let mut value = serde_json::to_value(receipt()).expect("receipt JSON value");
    value.as_object_mut()
        .expect("top-level object")
        .insert("conformance_result".into(), json!("PASS"));
    let parsed = serde_json::from_value::<BoundaryReceipt>(value);

    // Record the observed limitation rather than allowing preparation CI to
    // infer that this typed DTO is already a strict wire schema.
    assert!(parsed.is_ok(), "baseline behavior changed: review the strict field gate");
    println!("C6_KNOWN_GAP: RI-RS derived DTO ignored conformance_result");
}

#[test]
fn known_gap_serde_ignores_unknown_nested_field() {
    let mut value = serde_json::to_value(receipt()).expect("receipt JSON value");
    value["received"]["unrecognized_contract_extension"] = json!("unexpected");
    let parsed = serde_json::from_value::<BoundaryReceipt>(value);
    assert!(parsed.is_ok(), "baseline behavior changed: review the strict field gate");
    println!("C6_KNOWN_GAP: RI-RS derived DTO ignored nested unknown field");
}

#[test]
fn known_gap_base64_wire_string_is_not_consumed_by_native_vec_u8_dto() {
    let mut value = serde_json::to_value(receipt()).expect("receipt JSON value");
    let wire_bytes = [0x43, 0x36, 0x00, 0xfe, 0xff];
    value["received"]["raw_octets"] = Value::String(B64.encode(wire_bytes));
    assert!(value["received"]["raw_octets"].is_string());

    // BC-02.1 specifies Base64 string transport, while the native DTO's Vec<u8>
    // expects an array under generic Serde. A dedicated reciprocal parser is
    // required before C6 can pass.
    assert!(serde_json::from_value::<BoundaryReceipt>(value).is_err());
    println!("C6_KNOWN_GAP: no reciprocal BC-02.1 Base64 receipt consumer in RI-RS DTO");
}

#[test]
fn raw_artifact_octets_are_not_required_to_be_utf8() {
    let r = receipt();
    assert_eq!(r.received.raw_octets, vec![0x43, 0x36, 0x00, 0xfe, 0xff]);
    assert!(validate_schema(&r).is_ok());
}
