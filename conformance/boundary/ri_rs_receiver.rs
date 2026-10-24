//! BC-02.3 — RI-RS Receiver v1
//!
//! Construction-only receiver for the common BC-02.1 receipt schema.
//! This module MUST NOT execute conformance, B-VAL-014, or §4.5.

use sha2::{Digest, Sha256};
use serde::{Deserialize, Serialize};

pub const SCHEMA_ID: &str = "BC-02.1-COMMON-RECEIPT";
pub const SCHEMA_VERSION: u32 = 1;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct BoundaryReceipt {
    pub schema_id: String,
    pub schema_version: u32,
    pub fixture: Fixture,
    pub handoff: Handoff,
    pub received: Received,
    pub receiver: Receiver,
    pub adapter: Adapter,
    pub environment: Environment,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Fixture {
    pub fixture_id: String,
    pub fixture_artifact_identity: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Handoff {
    pub status: HandoffStatus,
    pub method: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum HandoffStatus {
    TRANSFERRED,
    NOT_TRANSFERRED,
    ERROR,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Received {
    pub octet_length: usize,
    /// Logical octets actually received by RI-RS.
    /// JSON transport encoding, where used, is handled outside this field.
    pub raw_octets: Vec<u8>,
    pub recomputed_sha256: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Receiver {
    pub receiver_id: String,
    pub implementation_id: String,
    pub language: String,
    pub implementation_version: String,
    pub source_commit: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Adapter {
    pub adapter_id: String,
    pub adapter_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Environment {
    pub environment_id: String,
    pub platform: String,
    pub runtime: String,
}

/// Construct a receipt from octets actually supplied to the receiver.
/// No expected digest, parsed object, reconstructed JSON, or textual encoding
/// is used as digest input.
pub fn receive(
    fixture_id: String,
    fixture_artifact_identity: String,
    method: String,
    raw_octets: Vec<u8>,
    receiver_id: String,
    implementation_id: String,
    implementation_version: String,
    source_commit: String,
    adapter_id: String,
    adapter_version: String,
    environment_id: String,
    platform: String,
    runtime: String,
) -> BoundaryReceipt {
    let digest = Sha256::digest(&raw_octets);
    let recomputed_sha256 = digest.iter().map(|b| format!("{b:02x}")).collect();
    let octet_length = raw_octets.len();

    BoundaryReceipt {
        schema_id: SCHEMA_ID.to_owned(),
        schema_version: SCHEMA_VERSION,
        fixture: Fixture { fixture_id, fixture_artifact_identity },
        handoff: Handoff { status: HandoffStatus::TRANSFERRED, method },
        received: Received { octet_length, raw_octets, recomputed_sha256 },
        receiver: Receiver {
            receiver_id,
            implementation_id,
            language: "Rust".to_owned(),
            implementation_version,
            source_commit,
        },
        adapter: Adapter { adapter_id, adapter_version },
        environment: Environment { environment_id, platform, runtime },
    }
}

/// Schema-level validation only. This is NOT a conformance result.
pub fn validate_schema(receipt: &BoundaryReceipt) -> Result<(), &'static str> {
    if receipt.schema_id != SCHEMA_ID || receipt.schema_version != SCHEMA_VERSION {
        return Err("R-VAL-001: schema identity/version invalid");
    }
    if receipt.fixture.fixture_id.is_empty() || receipt.fixture.fixture_artifact_identity.is_empty() {
        return Err("R-VAL-002: fixture identity incomplete");
    }
    if receipt.handoff.method.is_empty() {
        return Err("R-VAL-003: handoff method missing");
    }
    if receipt.received.octet_length != receipt.received.raw_octets.len() {
        return Err("R-VAL-004: received length mismatch");
    }
    let digest = Sha256::digest(&receipt.received.raw_octets);
    let expected: String = digest.iter().map(|b| format!("{b:02x}")).collect();
    if expected != receipt.received.recomputed_sha256 {
        return Err("R-VAL-005: receiver-derived hash mismatch");
    }
    if receipt.receiver.receiver_id.is_empty()
        || receipt.receiver.implementation_id.is_empty()
        || receipt.receiver.source_commit.is_empty()
    {
        return Err("R-VAL-006/007: receiver provenance incomplete");
    }
    if receipt.adapter.adapter_id.is_empty() || receipt.adapter.adapter_version.is_empty() {
        return Err("R-VAL-008: adapter identity incomplete");
    }
    if receipt.environment.environment_id.is_empty()
        || receipt.environment.platform.is_empty()
        || receipt.environment.runtime.is_empty()
    {
        return Err("R-VAL-009: environment identity incomplete");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn receipt() -> BoundaryReceipt {
        receive(
            "FIX-DIGEST-P01".into(), "ISSUED-P01-ARTIFACT".into(), "local-octet-transfer".into(),
            vec![0x00, 0x01, 0xFE, 0xFF], "ri-rs-01".into(), "aura-ri-rs".into(),
            "1.0.0".into(), "construction-test".into(), "bc02.3-rs-adapter".into(),
            "1.0.0".into(), "test-env".into(), "test-platform".into(), "rust-test-runtime".into(),
        )
    }

    #[test] fn r_val_001_schema_identity() { let r = receipt(); assert_eq!(r.schema_id, SCHEMA_ID); assert_eq!(r.schema_version, 1); }
    #[test] fn r_val_002_fixture_identity() { let r = receipt(); assert!(!r.fixture.fixture_id.is_empty() && !r.fixture.fixture_artifact_identity.is_empty()); }
    #[test] fn r_val_003_closed_handoff_domain() { assert!(matches!(receipt().handoff.status, HandoffStatus::TRANSFERRED | HandoffStatus::NOT_TRANSFERRED | HandoffStatus::ERROR)); }
    #[test] fn r_val_004_length_explicit() { let r = receipt(); assert_eq!(r.received.octet_length, 4); }
    #[test] fn r_val_005_hash_from_raw_octets() { assert!(validate_schema(&receipt()).is_ok()); }
    #[test] fn r_val_006_receiver_provenance() { assert!(!receipt().receiver.receiver_id.is_empty()); }
    #[test] fn r_val_007_implementation_provenance() { assert!(!receipt().receiver.implementation_id.is_empty() && !receipt().receiver.source_commit.is_empty()); }
    #[test] fn r_val_008_adapter_identity() { assert!(!receipt().adapter.adapter_id.is_empty()); }
    #[test] fn r_val_009_environment_identity() { assert!(!receipt().environment.environment_id.is_empty()); }
    #[test] fn r_val_010_raw_material_not_reconstructed() { let r = receipt(); assert_eq!(r.received.raw_octets, vec![0x00, 0x01, 0xFE, 0xFF]); }
    #[test] fn r_val_011_deterministic_serialization() { let r = receipt(); let a = serde_json::to_vec(&r).unwrap(); let b = serde_json::to_vec(&r).unwrap(); assert_eq!(a, b); }
    #[test] fn r_val_012_no_conformance_authority_field() { let r = serde_json::to_value(receipt()).unwrap(); let object = r.as_object().unwrap(); assert!(!object.contains_key("conformance_result")); assert!(!object.contains_key("pass")); assert!(!object.contains_key("fail")); }
}


// Strict BC-02.1 receipt wire consumer. This boundary is intentionally
// separate from raw artifact intake and from direct Serde DTO decoding.
use base64::{engine::general_purpose::STANDARD as BC021_B64, Engine as _};
use serde::de::{self, MapAccess, Visitor};
use std::collections::BTreeMap;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReceiptParseError {
    pub code: &'static str,
    pub detail: String,
}

impl ReceiptParseError {
    fn new(code: &'static str, detail: impl Into<String>) -> Self {
        Self { code, detail: detail.into() }
    }
}

impl fmt::Display for ReceiptParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.code, self.detail)
    }
}
impl std::error::Error for ReceiptParseError {}

// Preserve object-member occurrences so duplicate keys cannot be erased by
// serde_json::Value's map representation before validation.
#[derive(Debug, Clone, PartialEq)]
enum StrictJsonValue {
    Null,
    Bool(bool),
    Number(serde_json::Number),
    String(String),
    Array(Vec<StrictJsonValue>),
    Object(BTreeMap<String, StrictJsonValue>),
}

impl<'de> Deserialize<'de> for StrictJsonValue {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where D: serde::Deserializer<'de> {
        struct StrictValueVisitor;
        impl<'de> Visitor<'de> for StrictValueVisitor {
            type Value = StrictJsonValue;

            fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                formatter.write_str("a JSON value with duplicate object keys rejected")
            }
            fn visit_unit<E>(self) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::Null)
            }
            fn visit_none<E>(self) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::Null)
            }
            fn visit_bool<E>(self, value: bool) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::Bool(value))
            }
            fn visit_i64<E>(self, value: i64) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::Number(value.into()))
            }
            fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::Number(value.into()))
            }
            fn visit_f64<E>(self, value: f64) -> Result<Self::Value, E> where E: de::Error {
                serde_json::Number::from_f64(value)
                    .map(StrictJsonValue::Number)
                    .ok_or_else(|| E::custom("TYPE_MISMATCH: non-finite number"))
            }
            fn visit_str<E>(self, value: &str) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::String(value.to_owned()))
            }
            fn visit_string<E>(self, value: String) -> Result<Self::Value, E> where E: de::Error {
                Ok(StrictJsonValue::String(value))
            }
            fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
            where A: serde::de::SeqAccess<'de> {
                let mut values = Vec::new();
                while let Some(value) = seq.next_element::<StrictJsonValue>()? {
                    values.push(value);
                }
                Ok(StrictJsonValue::Array(values))
            }
            fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
            where A: MapAccess<'de> {
                let mut values = BTreeMap::new();
                while let Some((key, value)) = map.next_entry::<String, StrictJsonValue>()? {
                    if values.contains_key(&key) {
                        return Err(de::Error::custom(format!("DUPLICATE_KEY: duplicate member {key:?}")));
                    }
                    values.insert(key, value);
                }
                Ok(StrictJsonValue::Object(values))
            }
        }
        deserializer.deserialize_any(StrictValueVisitor)
    }
}

fn bc021_reject_forbidden_values(value: &StrictJsonValue, where_: &str) -> Result<(), ReceiptParseError> {
    match value {
        StrictJsonValue::String(text) if ["PASS", "FAIL", "CONFORMANT", "NON_CONFORMANT"]
            .iter().any(|forbidden| text.to_uppercase() == *forbidden) => {
                Err(ReceiptParseError::new("INVALID_VALUE", format!("{where_} contains a prohibited result-authority value")))
            }
        StrictJsonValue::Object(map) => {
            for (key, child) in map {
                bc021_reject_forbidden_values(child, &format!("{where_}.{key}"))?;
            }
            Ok(())
        }
        StrictJsonValue::Array(values) => {
            for (index, child) in values.iter().enumerate() {
                bc021_reject_forbidden_values(child, &format!("{where_}[{index}]"))?;
            }
            Ok(())
        }
        _ => Ok(()),
    }
}

fn bc021_take_object(
    value: StrictJsonValue,
    required: &[&str],
    where_: &str,
) -> Result<BTreeMap<String, StrictJsonValue>, ReceiptParseError> {
    let mut map = match value {
        StrictJsonValue::Object(map) => map,
        StrictJsonValue::Null => return Err(ReceiptParseError::new("NULL_NOT_ALLOWED", format!("{where_} must not be null"))),
        _ => return Err(ReceiptParseError::new("INVALID_SHAPE", format!("{where_} must be an object"))),
    };
    if let Some(key) = map.keys().find(|key| !required.contains(&key.as_str())) {
        return Err(ReceiptParseError::new("UNKNOWN_FIELD", format!("{where_} has unknown field {key:?}")));
    }
    if let Some(key) = required.iter().find(|key| !map.contains_key(**key)) {
        return Err(ReceiptParseError::new("MISSING_FIELD", format!("{where_} lacks field {key:?}")));
    }
    Ok(std::mem::take(&mut map))
}

fn bc021_take(map: &mut BTreeMap<String, StrictJsonValue>, key: &str) -> StrictJsonValue {
    map.remove(key).expect("exact BC-02.1 key set checked before extraction")
}

fn bc021_string(value: StrictJsonValue, where_: &str) -> Result<String, ReceiptParseError> {
    match value {
        StrictJsonValue::Null => Err(ReceiptParseError::new("NULL_NOT_ALLOWED", format!("{where_} must not be null"))),
        StrictJsonValue::String(value) if !value.is_empty() => Ok(value),
        StrictJsonValue::String(_) => Err(ReceiptParseError::new("INVALID_VALUE", format!("{where_} must not be empty"))),
        _ => Err(ReceiptParseError::new("TYPE_MISMATCH", format!("{where_} must be a string"))),
    }
}

fn bc021_string_allow_empty(value: StrictJsonValue, where_: &str) -> Result<String, ReceiptParseError> {
    match value {
        StrictJsonValue::Null => Err(ReceiptParseError::new("NULL_NOT_ALLOWED", format!("{where_} must not be null"))),
        StrictJsonValue::String(value) => Ok(value),
        _ => Err(ReceiptParseError::new("TYPE_MISMATCH", format!("{where_} must be a string"))),
    }
}

fn bc021_usize(value: StrictJsonValue, where_: &str) -> Result<usize, ReceiptParseError> {
    match value {
        StrictJsonValue::Null => Err(ReceiptParseError::new("NULL_NOT_ALLOWED", format!("{where_} must not be null"))),
        StrictJsonValue::Number(number) => {
            if number.as_i64().is_some_and(|n| n < 0) {
                return Err(ReceiptParseError::new("INVALID_VALUE", format!("{where_} must be non-negative")));
            }
            number.as_u64()
                .and_then(|number| usize::try_from(number).ok())
                .ok_or_else(|| ReceiptParseError::new("TYPE_MISMATCH", format!("{where_} must be a non-negative JSON integer fitting usize")))
        },
        _ => Err(ReceiptParseError::new("TYPE_MISMATCH", format!("{where_} must be a non-negative JSON integer"))),
    }
}

fn bc021_version(value: StrictJsonValue) -> Result<u32, ReceiptParseError> {
    match value {
        StrictJsonValue::Null => Err(ReceiptParseError::new("NULL_NOT_ALLOWED", "schema_version must not be null")),
        StrictJsonValue::Number(number) if number.as_u64() == Some(SCHEMA_VERSION as u64) => Ok(SCHEMA_VERSION),
        StrictJsonValue::Number(number) if number.as_u64().is_some() || number.as_i64().is_some() => Err(ReceiptParseError::new("SCHEMA_VERSION_MISMATCH", "unsupported schema_version")),
        _ => Err(ReceiptParseError::new("TYPE_MISMATCH", "schema_version must be a JSON integer")),
    }
}

/// Consume the original UTF-8 JSON envelope with exact-field, duplicate-key,
/// Base64, byte-length, and receiver-derived SHA-256 validation.
///
/// This is receipt transport validation only. It does not parse arbitrary raw
/// artifact bytes as UTF-8 and produces no conformance result.
pub fn parse_receipt_json(raw_json: &[u8]) -> Result<BoundaryReceipt, ReceiptParseError> {
    if std::str::from_utf8(raw_json).is_err() {
        return Err(ReceiptParseError::new("INVALID_UTF8", "receipt envelope is not valid UTF-8"));
    }
    let document: StrictJsonValue = serde_json::from_slice(raw_json).map_err(|error| {
        let message = error.to_string();
        if message.contains("DUPLICATE_KEY") {
            ReceiptParseError::new("DUPLICATE_KEY", message)
        } else {
            ReceiptParseError::new("INVALID_JSON", "receipt envelope is not valid JSON")
        }
    })?;

    if matches!(document, StrictJsonValue::Null) {
        return Err(ReceiptParseError::new("NULL_NOT_ALLOWED", "receipt must not be null"));
    }
    let document_for_value_check = document.clone();

    let mut top = bc021_take_object(document,
        &["schema_id", "schema_version", "fixture", "handoff", "received", "receiver", "adapter", "environment"],
        "receipt")?;
    let schema_id = bc021_string(bc021_take(&mut top, "schema_id"), "schema_id")?;
    if schema_id != SCHEMA_ID {
        return Err(ReceiptParseError::new("SCHEMA_ID_MISMATCH", "unsupported schema_id"));
    }
    let schema_version = bc021_version(bc021_take(&mut top, "schema_version"))?;

    let mut fixture = bc021_take_object(bc021_take(&mut top, "fixture"),
        &["fixture_id", "fixture_artifact_identity"], "fixture")?;
    let fixture = Fixture {
        fixture_id: bc021_string(bc021_take(&mut fixture, "fixture_id"), "fixture.fixture_id")?,
        fixture_artifact_identity: bc021_string(bc021_take(&mut fixture, "fixture_artifact_identity"), "fixture.fixture_artifact_identity")?,
    };

    let mut handoff = bc021_take_object(bc021_take(&mut top, "handoff"),
        &["status", "method"], "handoff")?;
    let status_text = bc021_string(bc021_take(&mut handoff, "status"), "handoff.status")?;
    let status = match status_text.as_str() {
        "TRANSFERRED" => HandoffStatus::TRANSFERRED,
        "NOT_TRANSFERRED" => HandoffStatus::NOT_TRANSFERRED,
        "ERROR" => HandoffStatus::ERROR,
        _ => return Err(ReceiptParseError::new("INVALID_VALUE", "handoff.status outside closed BC-02.1 domain")),
    };
    let handoff = Handoff {
        status,
        method: bc021_string(bc021_take(&mut handoff, "method"), "handoff.method")?,
    };

    let mut received = bc021_take_object(bc021_take(&mut top, "received"),
        &["octet_length", "raw_octets", "recomputed_sha256"], "received")?;
    let octet_length = bc021_usize(bc021_take(&mut received, "octet_length"), "received.octet_length")?;
    let encoded_octets = bc021_string_allow_empty(bc021_take(&mut received, "raw_octets"), "received.raw_octets")?;
    let raw_octets = BC021_B64.decode(encoded_octets.as_bytes())
        .map_err(|_| ReceiptParseError::new("INVALID_BASE64", "received.raw_octets is not strict Base64"))?;
    if BC021_B64.encode(&raw_octets) != encoded_octets {
        return Err(ReceiptParseError::new("INVALID_BASE64", "received.raw_octets is not canonical padded Base64"));
    }
    if octet_length != raw_octets.len() {
        return Err(ReceiptParseError::new("LENGTH_MISMATCH", "octet_length differs from decoded raw_octets length"));
    }
    let recomputed_sha256 = bc021_string(bc021_take(&mut received, "recomputed_sha256"), "received.recomputed_sha256")?;
    if recomputed_sha256.len() != 64 || !recomputed_sha256.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)) {
        return Err(ReceiptParseError::new("INVALID_VALUE", "recomputed_sha256 must be 64 lowercase hexadecimal characters"));
    }
    let digest = Sha256::digest(&raw_octets);
    let actual: String = digest.iter().map(|b| format!("{b:02x}")).collect();
    if actual != recomputed_sha256 {
        return Err(ReceiptParseError::new("DIGEST_MISMATCH", "recomputed_sha256 does not match decoded raw_octets"));
    }
    let received = Received { octet_length, raw_octets, recomputed_sha256 };

    let mut receiver = bc021_take_object(bc021_take(&mut top, "receiver"),
        &["receiver_id", "implementation_id", "language", "implementation_version", "source_commit"], "receiver")?;
    let receiver = Receiver {
        receiver_id: bc021_string(bc021_take(&mut receiver, "receiver_id"), "receiver.receiver_id")?,
        implementation_id: bc021_string(bc021_take(&mut receiver, "implementation_id"), "receiver.implementation_id")?,
        language: bc021_string(bc021_take(&mut receiver, "language"), "receiver.language")?,
        implementation_version: bc021_string(bc021_take(&mut receiver, "implementation_version"), "receiver.implementation_version")?,
        source_commit: bc021_string(bc021_take(&mut receiver, "source_commit"), "receiver.source_commit")?,
    };
    let mut adapter = bc021_take_object(bc021_take(&mut top, "adapter"),
        &["adapter_id", "adapter_version"], "adapter")?;
    let adapter = Adapter {
        adapter_id: bc021_string(bc021_take(&mut adapter, "adapter_id"), "adapter.adapter_id")?,
        adapter_version: bc021_string(bc021_take(&mut adapter, "adapter_version"), "adapter.adapter_version")?,
    };
    let mut environment = bc021_take_object(bc021_take(&mut top, "environment"),
        &["environment_id", "platform", "runtime"], "environment")?;
    let environment = Environment {
        environment_id: bc021_string(bc021_take(&mut environment, "environment_id"), "environment.environment_id")?,
        platform: bc021_string(bc021_take(&mut environment, "platform"), "environment.platform")?,
        runtime: bc021_string(bc021_take(&mut environment, "runtime"), "environment.runtime")?,
    };
    bc021_reject_forbidden_values(&document_for_value_check, "receipt")?;

    let receipt = BoundaryReceipt { schema_id: SCHEMA_ID.to_owned(), schema_version, fixture, handoff, received, receiver, adapter, environment };
    if receipt.receiver.implementation_id == receipt.receiver.receiver_id {
        return Err(ReceiptParseError::new("INVALID_VALUE", "implementation identity must differ from receiver identity"));
    }
    if receipt.adapter.adapter_id == receipt.receiver.receiver_id
        || receipt.adapter.adapter_id == receipt.receiver.implementation_id {
        return Err(ReceiptParseError::new("INVALID_VALUE", "adapter identity must differ from receiver and implementation identities"));
    }
    validate_schema(&receipt).map_err(|error| {
        let code = error.split(':').next().unwrap_or("INVALID_VALUE");
        ReceiptParseError::new("INVALID_VALUE", format!("schema validation failed ({code})"))
    })?;
    Ok(receipt)
}
