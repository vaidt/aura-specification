use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use ri_rs_receiver::strict_wire::parse_receipt_json;
use sha2::{Digest, Sha256};

fn valid() -> Vec<u8> {
    let raw = [0x43, 0x36, 0x00, 0xfe, 0xff];
    let digest = Sha256::digest(raw).iter().map(|b| format!("{b:02x}")).collect::<String>();
    format!(r#"{{"adapter":{{"adapter_id":"adapter-x","adapter_version":"1"}},"environment":{{"environment_id":"env","platform":"linux","runtime":"rust"}},"fixture":{{"fixture_artifact_identity":"fixture.bin","fixture_id":"FIX-C6"}},"handoff":{{"method":"local","status":"TRANSFERRED"}},"received":{{"octet_length":5,"raw_octets":"{}","recomputed_sha256":"{}"}},"receiver":{{"implementation_id":"impl","implementation_version":"1","language":"Rust","receiver_id":"RI-RS","source_commit":"abc"}},"schema_id":"BC-02.1-COMMON-RECEIPT","schema_version":1}}"#, B64.encode(raw), digest).into_bytes()
}
fn rejected(bytes: &[u8]) -> bool { parse_receipt_json(bytes).is_err() }

#[test]
fn accepts_valid_base64_wire_and_preserves_octets() {
    let parsed = parse_receipt_json(&valid()).expect("valid receipt");
    assert_eq!(parsed.raw_octets, vec![0x43, 0x36, 0, 0xfe, 0xff]);
}
#[test]
fn rejects_authority_unknown_and_duplicate_fields() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace("\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"", "\"conformance_result\":\"PASS\",\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"").as_bytes());
    assert!(rejected(base.replace("\"adapter_id\":\"adapter-x\"", "\"unknown\":\"x\",\"adapter_id\":\"adapter-x\"").as_bytes());
    assert!(rejected(base.replace("\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"", "\"schema_id\":\"BAD\",\"schema_id\":\"BC-02.1-COMMON-RECEIPT\"").as_bytes());
    assert!(rejected(base.replace("\"method\":\"local\"", "\"method\":\"local\",\"method\":\"other\"").as_bytes());
}
#[test]
fn rejects_bad_utf8_json_null_types_and_negative_lengths() {
    assert!(rejected(&[0xff, 0xfe]));
    assert!(rejected(b"{"));
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace("\"runtime\":\"rust\"", "\"runtime\":null").as_bytes());
    assert!(rejected(base.replace("\"octet_length\":5", "\"octet_length\":-1").as_bytes());
    assert!(rejected(base.replace("\"octet_length\":5", "\"octet_length\":5.0").as_bytes());
    assert!(rejected(base.replace("\"octet_length\":5", "\"octet_length\":true").as_bytes());
}
#[test]
fn rejects_bad_base64_length_and_digest() {
    let base = String::from_utf8(valid()).unwrap();
    assert!(rejected(base.replace(&B64.encode([0x43, 0x36, 0, 0xfe, 0xff]), "!!!").as_bytes());
    assert!(rejected(base.replace("\"octet_length\":5", "\"octet_length\":4").as_bytes());
    let digest = Sha256::digest([0x43, 0x36, 0, 0xfe, 0xff]).iter().map(|b| format!("{b:02x}")).collect::<String>();
    assert!(rejected(base.replace(&digest, &"0".repeat(64)).as_bytes());
}
