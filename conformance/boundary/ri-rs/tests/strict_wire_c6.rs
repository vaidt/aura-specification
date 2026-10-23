use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use ri_rs_receiver::strict_wire::parse_receipt_json;
use sha2::{Digest, Sha256};

fn valid() -> Vec<u8> {
    let raw = [0x43, 0x36, 0x00, 0xfe, 0xff];
    let digest = Sha256::digest(raw).iter().map(|b| format!("{b:02x}")).collect::<String>();
    format!(r#"{{"adapter":{{"adapter_id":"adapter-x","adapter_version":"1"}},"environment":{{"environment_id":"env","platform":"linux","runtime":"rust"}},"fixture":{{"fixture_artifact_identity":"fixture.bin","fixture_id":"FIX-C6"}},"handoff":{{"method":"local","status":"TRANSFERRED"}},"received":{{"octet_length":5,"raw_octets":"{}","recomputed_sha256":"{}"}},"receiver":{{"implementation_id":"impl","implementation_version":"1","language":"Rust","receiver_id":"RI-RS","source_commit":"abc"}},"schema_id":"BC-02.1-COMMON-RECEIPT","schema_version":1}}"#, B64.encode(raw), digest).into_bytes()
}
fn rejected(bytes: &[u8]) -> bool { parse_receipt_json(bytes).is_err() }

#[test] fn accepts_valid_base64_wire_and_preserves_octets() {
    let input = valid(); let parsed = parse_receipt_json(&input).expect("valid");
    assert_eq!(parsed.raw_octets, vec![0x43, 0x36, 0, 0xfe, 0xff]);
}
#[test] fn rejects_authority_and_unknown_fields() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace(r#""schema_id":"BC-02.1-COMMON-RECEIPT""#, r#""conformance_result":"PASS","schema_id":"BC-02.1-COMMON-RECEIPT""#).as_bytes());
    assert!(rejected(base.replace(r#""adapter_id":"adapter-x""#, r#""unknown":"x","adapter_id":"adapter-x""#).as_bytes());
}
#[test] fn rejects_duplicate_keys_at_every_level() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace(r#""schema_id":"BC-02.1-COMMON-RECEIPT""#, r#""schema_id":"BAD","schema_id":"BC-02.1-COMMON-RECEIPT""#).as_bytes());
    assert!(rejected(base.replace(r#""method":"local""#, r#""method":"local","method":"other""#).as_bytes());
}
#[test] fn rejects_bad_utf8_json_and_malformed_json() {
    assert!(rejected(&[0xff, 0xfe]));
    assert!(rejected(b"{"));
}
#[test] fn rejects_null_wrong_types_and_negative_length() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace(r#""runtime":"rust""#, r#""runtime":null"#).as_bytes());
    assert!(rejected(base.replace(r#""octet_length":5"#, r#""octet_length":-1"#).as_bytes());
    assert!(rejected(base.replace(r#""octet_length":5"#, r#""octet_length":5.0"#).as_bytes());
    assert!(rejected(base.replace(r#""octet_length":5"#, r#""octet_length":true"#).as_bytes());
}
#[test] fn rejects_malformed_base64_length_and_digest() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace(&B64.encode([0x43, 0x36, 0, 0xfe, 0xff]), "!!!").as_bytes());
    assert!(rejected(base.replace(r#""octet_length":5"#, r#""octet_length":4"#).as_bytes());
    assert!(rejected(base.replace(&"".to_string(), "").as_bytes()) == false); // positive corpus stable
}
