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


fn wire_receipt() -> Vec<u8> {
    let mut value = serde_json::to_value(receipt()).expect("typed receipt value");
    let bytes = [0x43, 0x36, 0x00, 0xfe, 0xff];
    value["received"]["raw_octets"] = Value::String(B64.encode(bytes));
    serde_json::to_vec(&value).expect("BC-02.1 wire JSON")
}

fn assert_parse_code(raw: &[u8], code: &str) {
    let error = ri_rs_receiver::parse_receipt_json(raw).expect_err("invalid envelope must be rejected");
    assert_eq!(error.code, code, "unexpected error: {error}");
}

#[test]
fn strict_wire_consumer_accepts_base64_and_preserves_raw_octets() {
    let parsed = ri_rs_receiver::parse_receipt_json(&wire_receipt()).expect("valid BC-02.1 envelope");
    assert_eq!(parsed.received.raw_octets, vec![0x43, 0x36, 0x00, 0xfe, 0xff]);
    assert_eq!(parsed.received.octet_length, 5);
    assert_eq!(parsed.handoff.status, HandoffStatus::TRANSFERRED);
    assert!(validate_schema(&parsed).is_ok());
}

#[test]
fn strict_wire_consumer_rejects_invalid_utf8_and_json() {
    assert_parse_code(&[b'{', 0xff, b'}'], "INVALID_UTF8");
    assert_parse_code(b"{\"schema_id\":", "INVALID_JSON");
}

#[test]
fn strict_wire_consumer_rejects_duplicate_keys_before_interpretation() {
    let raw = String::from_utf8(wire_receipt()).expect("valid generated JSON");
    let duplicated = raw.replacen(
        "\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"",
        "\"schema_id\":\"BC-02.1-COMMON-RECEIPT\",\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"",
        1,
    );
    assert_parse_code(duplicated.as_bytes(), "DUPLICATE_KEY");

    let duplicated_nested = raw.replacen(
        "\"status\":\"TRANSFERRED\"",
        "\"status\":\"TRANSFERRED\",\"status\":\"TRANSFERRED\"",
        1,
    );
    assert_parse_code(duplicated_nested.as_bytes(), "DUPLICATE_KEY");
}

#[test]
fn strict_wire_consumer_rejects_unknown_authority_and_nested_fields() {
    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value.as_object_mut().unwrap().insert("conformance_result".into(), json!("PASS"));
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "UNKNOWN_FIELD");

    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["received"]["unexpected"] = json!("extra");
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "UNKNOWN_FIELD");
}

#[test]
fn strict_wire_consumer_rejects_missing_null_and_bad_field_types() {
    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value.as_object_mut().unwrap().remove("receiver");
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "MISSING_FIELD");

    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["adapter"]["adapter_id"] = Value::Null;
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "NULL_NOT_ALLOWED");

    for bad in [json!(true), json!(1.5), json!(-1)] {
        let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
        value["received"]["octet_length"] = bad;
        let expected = if value["received"]["octet_length"] == json!(-1) { "INVALID_VALUE" } else { "TYPE_MISMATCH" };
        assert_parse_code(&serde_json::to_vec(&value).unwrap(), expected);
    }

    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["handoff"]["status"] = json!("PASS");
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "INVALID_VALUE");
}

#[test]
fn strict_wire_consumer_rejects_bad_base64_length_and_digest() {
    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["received"]["raw_octets"] = json!("a@@=");
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "INVALID_BASE64");

    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["received"]["octet_length"] = json!(6);
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "LENGTH_MISMATCH");

    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["received"]["recomputed_sha256"] = json!("0".repeat(64));
    assert_parse_code(&serde_json::to_vec(&value).unwrap(), "DIGEST_MISMATCH");
}

#[test]
fn strict_wire_parser_does_not_confuse_artifact_octets_with_json_utf8() {
    // The JSON envelope itself is UTF-8, while raw_octets contains non-UTF-8.
    let parsed = ri_rs_receiver::parse_receipt_json(&wire_receipt()).unwrap();
    assert_eq!(parsed.received.raw_octets, vec![0x43, 0x36, 0x00, 0xfe, 0xff]);
}


#[test]
fn strict_wire_consumer_accepts_empty_raw_octets() {
    let mut value: Value = serde_json::from_slice(&wire_receipt()).unwrap();
    value["received"]["raw_octets"] = json!("");
    value["received"]["octet_length"] = json!(0);
    value["received"]["recomputed_sha256"] = json!("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    let parsed = ri_rs_receiver::parse_receipt_json(&serde_json::to_vec(&value).unwrap()).unwrap();
    assert!(parsed.received.raw_octets.is_empty());
    assert_eq!(parsed.received.octet_length, 0);
}
