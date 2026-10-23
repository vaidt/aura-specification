//! Strict BC-02.1 wire consumer, experimental C6 surface only.
//!
//! This parser validates receipt JSON transport. It is not a protocol verdict.
//! Raw artifact octets are opaque and may contain non-UTF-8 bytes.
use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

const SCHEMA_ID: &str = "BC-02.1-COMMON-RECEIPT";
const TOP: &[&str] = &["schema_id", "schema_version", "fixture", "handoff", "received", "receiver", "adapter", "environment"];

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WireReceipt {
    pub value: Value,
    pub raw_octets: Vec<u8>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WireError(pub &'static str);

fn expected_fields(parent: &str) -> &'static [&'static str] {
    match parent {
        "fixture" => &["fixture_id", "fixture_artifact_identity"],
        "handoff" => &["status", "method"],
        "received" => &["octet_length", "raw_octets", "recomputed_sha256"],
        "receiver" => &["receiver_id", "implementation_id", "language", "implementation_version", "source_commit"],
        "adapter" => &["adapter_id", "adapter_version"],
        "environment" => &["environment_id", "platform", "runtime"],
        _ => &[],
    }
}

fn forbidden_key(key: &str) -> bool {
    matches!(key.to_ascii_lowercase().as_str(),
        "conformance_result" | "conformance" | "acceptance_state" |
        "expected_acceptance" | "digest_output_state" | "expected_digest_output" |
        "result" | "verdict" | "outcome" | "pass" | "fail")
}

fn scan_authority(v: &Value) -> Result<(), WireError> {
    match v {
        Value::Object(map) => {
            for (key, child) in map {
                if forbidden_key(key) { return Err(WireError("forbidden-authority-key")); }
                scan_authority(child)?;
            }
        }
        Value::Array(items) => for item in items { scan_authority(item)?; },
        _ => {}
    }
    Ok(())
}

fn exact_keys(map: &Map<String, Value>, expected: &[&str]) -> bool {
    let actual: BTreeSet<&str> = map.keys().map(String::as_str).collect();
    let wanted: BTreeSet<&str> = expected.iter().copied().collect();
    actual == wanted
}

fn required_string<'a>(map: &'a Map<String, Value>, key: &str) -> Result<&'a str, WireError> {
    match map.get(key).and_then(Value::as_str) {
        Some(s) if !s.is_empty() => Ok(s),
        _ => Err(WireError("required-nonempty-string")),
    }
}

/// Strict duplicate-aware parser: serde_json::Value alone uses last-key-wins,
/// so first scan raw JSON tokens through a visitor-backed typed map at every
/// nesting level before Value parsing.
pub fn parse_receipt_json(input: &[u8]) -> Result<WireReceipt, WireError> {
    let text = std::str::from_utf8(input).map_err(|_| WireError("invalid-utf8"))?;
    // Recursive duplicate-key detection precedes Value parsing.
    check_duplicate_keys(text)?;
    let value: Value = serde_json::from_str(text).map_err(|_| WireError("malformed-json"))?;
    scan_authority(&value)?;
    let root = value.as_object().ok_or(WireError("top-level-object-required"))?;
    if !exact_keys(root, TOP) { return Err(WireError("top-level-field-set")); }
    if required_string(root, "schema_id")? != SCHEMA_ID ||
       root.get("schema_version").and_then(Value::as_u64) != Some(1) {
        return Err(WireError("schema-identity-or-version"));
    }
    for parent in ["fixture", "handoff", "received", "receiver", "adapter", "environment"] {
        let child = root.get(parent).and_then(Value::as_object).ok_or(WireError("nested-object-required"))?;
        if !exact_keys(child, expected_fields(parent)) { return Err(WireError("nested-field-set")); }
        for key in expected_fields(parent) { required_string(child, key).or_else(|e| {
            // octet_length is the only numeric field.
            if parent == "received" && *key == "octet_length" { Ok("") } else { Err(e) }
        })?; }
    }
    let handoff = root["handoff"]["status"].as_str().ok_or(WireError("status-type"))?;
    if !matches!(handoff, "TRANSFERRED" | "NOT_TRANSFERRED" | "ERROR") {
        return Err(WireError("handoff-status-domain"));
    }
    let received = root["received"].as_object().ok_or(WireError("received-object"))?;
    let length = received["octet_length"].as_u64().ok_or(WireError("octet-length-integer"))?;
    let encoded = received["raw_octets"].as_str().ok_or(WireError("raw-octets-base64-string"))?;
    let raw = B64.decode(encoded).map_err(|_| WireError("invalid-base64"))?;
    if B64.encode(&raw) != encoded { return Err(WireError("noncanonical-base64")); }
    if length != raw.len() as u64 { return Err(WireError("octet-length-mismatch")); }
    let recorded = received["recomputed_sha256"].as_str().ok_or(WireError("digest-string"))?;
    if recorded.len() != 64 || !recorded.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)) {
        return Err(WireError("digest-format"));
    }
    let actual = Sha256::digest(&raw).iter().map(|b| format!("{b:02x}")).collect::<String>();
    if actual != recorded { return Err(WireError("digest-mismatch")); }
    Ok(WireReceipt { value, raw_octets: raw })
}

// A syntax-aware recursive scanner that preserves duplicate object member names.
// It intentionally validates JSON string/escape boundaries before Value decoding.
fn check_duplicate_keys(input: &str) -> Result<(), WireError> {
    struct Scanner<'a> { s: &'a [u8], i: usize }
    impl<'a> Scanner<'a> {
        fn ws(&mut self) { while self.i < self.s.len() && self.s[self.i].is_ascii_whitespace() { self.i += 1; } }
        fn string(&mut self) -> Result<String, WireError> {
            let start = self.i;
            if self.s.get(self.i) != Some(&b'"') { return Err(WireError("malformed-json")); }
            self.i += 1;
            while self.i < self.s.len() {
                match self.s[self.i] {
                    b'\\' => { self.i += 2; if self.i > self.s.len() { return Err(WireError("malformed-json")); } }
                    b'"' => { self.i += 1; let raw = std::str::from_utf8(&self.s[start..self.i]).map_err(|_| WireError("invalid-utf8"))?;
                        let decoded: String = serde_json::from_str(raw).map_err(|_| WireError("malformed-json"))?; return Ok(decoded); }
                    0..=31 => return Err(WireError("malformed-json")),
                    _ => self.i += 1,
                }
            }
            Err(WireError("malformed-json"))
        }
        fn value(&mut self) -> Result<(), WireError> {
            self.ws();
            match self.s.get(self.i) {
                Some(b'{') => self.object(),
                Some(b'[') => self.array(),
                Some(b'"') => { self.string()?; Ok(()) }
                Some(_) => { while self.i < self.s.len() && !b",]} \r\n\t".contains(&self.s[self.i]) { self.i += 1; } if self.i == 0 { Err(WireError("malformed-json")) } else { Ok(()) } },
                None => Err(WireError("malformed-json")),
            }
        }
        fn object(&mut self) -> Result<(), WireError> {
            self.i += 1; self.ws(); let mut keys = BTreeSet::new();
            if self.s.get(self.i) == Some(&b'}') { self.i += 1; return Ok(()); }
            loop {
                self.ws(); let key = self.string()?;
                if !keys.insert(key) { return Err(WireError("duplicate-key")); }
                self.ws(); if self.s.get(self.i) != Some(&b':') { return Err(WireError("malformed-json")); }
                self.i += 1; self.value()?; self.ws();
                match self.s.get(self.i) {
                    Some(b',') => self.i += 1,
                    Some(b'}') => { self.i += 1; return Ok(()); }
                    _ => return Err(WireError("malformed-json")),
                }
            }
        }
        fn array(&mut self) -> Result<(), WireError> {
            self.i += 1; self.ws(); if self.s.get(self.i) == Some(&b']') { self.i += 1; return Ok(()); }
            loop { self.value()?; self.ws(); match self.s.get(self.i) { Some(b',') => self.i += 1, Some(b']') => { self.i += 1; return Ok(()); }, _ => return Err(WireError("malformed-json")) } }
        }
    }
    let mut scan = Scanner { s: input.as_bytes(), i: 0 };
    scan.value()?; scan.ws();
    if scan.i != scan.s.len() { return Err(WireError("malformed-json")); }
    Ok(())
}
