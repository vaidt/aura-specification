use ri_rs_receiver::{
    receive, serialize_receipt_json, strict_wire::parse_receipt_json, validate_schema,
};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::{env, fs, path::PathBuf};

#[derive(Debug, Deserialize)]
struct Corpus {
    schema: String,
    contract: String,
    raw_octets_hex: String,
    valid_receipt_json: String,
    mutations: Vec<Mutation>,
}
#[derive(Debug, Deserialize)]
struct Mutation {
    id: String,
    kind: String,
    find: Option<String>,
    replace: Option<String>,
    wire: Option<String>,
    wire_hex: Option<String>,
    expected: String,
}
fn corpus() -> Corpus {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../../fixtures/corpus/STAGE-C-C6-BC02.1-WIRE-MUTATIONS-v0.1.json");
    let bytes = fs::read(&path).expect("shared C6 corpus must be available");
    println!("C6_SHARED_CORPUS_SHA256={}", encode_hex(&Sha256::digest(&bytes)));
    let corpus: Corpus = serde_json::from_slice(&bytes).expect("shared C6 corpus must parse");
    assert_eq!(corpus.schema, "AURA-STAGE-C6-BC02.1-WIRE-MUTATION-CORPUS/0.1");
    assert_eq!(corpus.contract, "BC-02.1-COMMON-RECEIPT");
    corpus
}
fn decode_hex(s: &str) -> Vec<u8> {
    assert_eq!(s.len() % 2, 0, "hex must contain whole octets");
    s.as_bytes().chunks_exact(2).map(|pair| {
        let hi = (pair[0] as char).to_digit(16).expect("hex digit") as u8;
        let lo = (pair[1] as char).to_digit(16).expect("hex digit") as u8;
        (hi << 4) | lo
    }).collect()
}
fn encode_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
fn apply_mutation(base: &str, case: &Mutation) -> Vec<u8> {
    match case.kind.as_str() {
        "replace" => {
            let find = case.find.as_ref().expect("replace case must define find");
            let replace = case.replace.as_ref().expect("replace case must define replacement");
            assert_eq!(base.matches(find).count(), 1, "{}: replacement target must occur once", case.id);
            base.replacen(find, replace, 1).into_bytes()
        }
        "literal" => case.wire.as_ref().expect("literal case must define wire").as_bytes().to_vec(),
        "hex" => decode_hex(case.wire_hex.as_ref().expect("hex case must define wire_hex")),
        other => panic!("{}: unsupported mutation kind {other}", case.id),
    }
}

#[test]
fn accepts_receipt_generated_by_native_receiver_flow_with_pinned_provenance() {
    let source_commit = env::var("AURA_SOURCE_COMMIT")
        .expect("workflow must provide the tested source commit as AURA_SOURCE_COMMIT");
    assert_eq!(source_commit.len(), 40, "source_commit must be a full Git SHA");
    assert!(source_commit.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)),
        "source_commit must be lowercase hexadecimal");
    println!("C6_RI_RS_SOURCE_COMMIT={source_commit}");

    let corpus = corpus();
    let raw_octets = decode_hex(&corpus.raw_octets_hex);
    let receipt = receive(
        "FIX-C6-RECEIVER-FLOW".into(),
        "issued-fixture:FIX-C6-RECEIVER-FLOW".into(),
        "local-octet-transfer".into(),
        raw_octets.clone(),
        "RI-RS-C6".into(),
        "AURA-RI-RS".into(),
        "1.0.0".into(),
        source_commit.clone(),
        "BC02.3-RS-ADAPTER".into(),
        "1.0.0".into(),
        "C6-CI-LINUX".into(),
        "ubuntu-latest".into(),
        "rustc-1.86".into(),
    );
    validate_schema(&receipt).expect("native receiver must produce a valid schema receipt");
    let wire = serialize_receipt_json(&receipt).expect("native receipt must serialize to BC-02.1 JSON");
    let parsed = parse_receipt_json(&wire).expect("strict consumer must accept native receiver output");

    assert_eq!(parsed.raw_octets, raw_octets);
    assert_eq!(parsed.value["receiver"]["source_commit"].as_str(), Some(source_commit.as_str()));
    assert_eq!(parsed.value["receiver"]["receiver_id"].as_str(), Some("RI-RS-C6"));
    assert_eq!(parsed.value["receiver"]["implementation_id"].as_str(), Some("AURA-RI-RS"));
    assert_ne!(parsed.value["receiver"]["receiver_id"], parsed.value["receiver"]["implementation_id"]);
    assert_eq!(parsed.value["adapter"]["adapter_id"].as_str(), Some("BC02.3-RS-ADAPTER"));
    assert_eq!(parsed.value["environment"]["environment_id"].as_str(), Some("C6-CI-LINUX"));
    assert_eq!(parsed.value["received"]["raw_octets"].as_str(), Some("QzYA/v8="));
    assert_eq!(parsed.value["received"]["recomputed_sha256"].as_str(),
        Some(encode_hex(&Sha256::digest(&raw_octets)).as_str()));
}

#[test]
fn accepts_shared_valid_receipt_and_preserves_raw_octets() {
    let corpus = corpus();
    let parsed = parse_receipt_json(corpus.valid_receipt_json.as_bytes()).expect("shared valid receipt");
    assert_eq!(encode_hex(&parsed.raw_octets), corpus.raw_octets_hex);
}

#[test]
fn rejects_every_mutation_in_the_shared_corpus() {
    let corpus = corpus();
    assert_eq!(corpus.mutations.len(), 18);
    for case in &corpus.mutations {
        assert_eq!(case.expected, "REJECT", "{}: unexpected positive disposition", case.id);
        let candidate = apply_mutation(&corpus.valid_receipt_json, case);
        assert!(parse_receipt_json(&candidate).is_err(), "{}: malformed receipt was accepted", case.id);
    }
}
