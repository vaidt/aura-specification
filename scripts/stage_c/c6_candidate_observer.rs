//! Observation-only RI-RS runner for the isolated C6 JSON candidate pilot.
//! No expected outcomes or normative conformance verdicts are assigned.
use aura_guard::strict_wire::parse_receipt_json;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::error::Error;
use std::fs;
use std::path::{Component, Path, PathBuf};
use std::process::Command;

const EXPECTED_RI_RS_COMMIT: &str = "feab2d9c369cd5f8cbabe10d713d278b0b09da8b";
const PILOT_IDS: [&str; 8] = [
    "C6-X-013", "C6-X-014", "C6-X-015", "C6-X-016",
    "C6-X-017", "C6-X-018", "C6-X-019", "C6-X-020",
];

fn sha256_hex(raw: &[u8]) -> String {
    let digest = Sha256::digest(raw);
    let mut output = String::with_capacity(64);
    for byte in digest {
        output.push_str(&format!("{byte:02x}"));
    }
    output
}

fn git(root: &Path, args: &[&str]) -> Result<String, Box<dyn Error>> {
    let output = Command::new("git").arg("-C").arg(root).args(args).output()?;
    if !output.status.success() {
        return Err(format!("git command failed: {}", String::from_utf8_lossy(&output.stderr)).into());
    }
    Ok(String::from_utf8(output.stdout)?.trim().to_owned())
}

fn argument(args: &[String], name: &str) -> Result<PathBuf, Box<dyn Error>> {
    let position = args.iter().position(|value| value == name)
        .ok_or_else(|| format!("missing required argument {name}"))?;
    let value = args.get(position + 1).ok_or_else(|| format!("missing value for {name}"))?;
    Ok(PathBuf::from(value))
}

fn safe_path(root: &Path, relative: &str) -> Result<PathBuf, Box<dyn Error>> {
    let rel = Path::new(relative);
    if rel.is_absolute() || rel.components().any(|component| matches!(component, Component::ParentDir)) {
        return Err(format!("unsafe candidate input path: {relative}").into());
    }
    let root = root.canonicalize()?;
    let resolved = root.join(rel).canonicalize()?;
    if !resolved.starts_with(&root) {
        return Err(format!("candidate input path escapes laboratory directory: {relative}").into());
    }
    Ok(resolved)
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let index_path = argument(&args, "--index")?;
    let lab_root = argument(&args, "--lab-root")?;
    let guard_root = argument(&args, "--guard-root")?;
    let output_path = argument(&args, "--output")?;

    let actual_commit = git(&guard_root, &["rev-parse", "HEAD"])?;
    if actual_commit != EXPECTED_RI_RS_COMMIT {
        return Err(format!("RI-RS source commit mismatch: expected {EXPECTED_RI_RS_COMMIT}, got {actual_commit}").into());
    }
    let source_path = "conformance/strict_wire.rs";
    let source_blob = git(&guard_root, &["rev-parse", &format!("HEAD:{source_path}")])?;
    let source_raw = fs::read(guard_root.join(source_path))?;
    let lib_blob = git(&guard_root, &["rev-parse", "HEAD:src/lib.rs"])?;
    let cargo_blob = git(&guard_root, &["rev-parse", "HEAD:Cargo.toml"])?;

    let index_raw = fs::read(&index_path)?;
    let index: Value = serde_json::from_slice(&index_raw)?;
    if index["schema"] != "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1"
        || index["status"] != "EXPLORATORY_NON_NORMATIVE"
        || index["authority"] != "NONE"
        || index["governance_effect"] != "NONE"
        || index["authorization_effect"] != "NONE"
        || index["release_effect"] != "NONE"
    {
        return Err("candidate materialization index schema/status/effect boundary invalid".into());
    }
    let entries = index["candidates"].as_array().ok_or("candidate index lacks candidates array")?;
    let mut rows = Vec::new();
    for id in PILOT_IDS {
        let entry = entries.iter().find(|value| value["id"] == id)
            .ok_or_else(|| format!("missing pilot candidate {id}"))?;
        if entry["materialization_kind"] != "BYTES"
            || entry["contract_binding_status"] != "UNRESOLVED"
            || entry["expected_outcome_policy"] != "CONTRACT_DECISION_REQUIRED"
            || entry.get("expected_result").is_some()
            || entry.get("expected_code").is_some()
        {
            return Err(format!("{id}: candidate is not observation-only").into());
        }
        let relative = entry["input_file"].as_str().ok_or("candidate input_file missing")?;
        let path = safe_path(&lab_root, relative)?;
        let raw = fs::read(path)?;
        let actual_sha = sha256_hex(&raw);
        if entry["input_bytes"].as_u64() != Some(raw.len() as u64)
            || entry["input_sha256"].as_str() != Some(actual_sha.as_str())
        {
            return Err(format!("{id}: input bytes/digest differs from materialization index").into());
        }

        let (observed_result, observed_code) = match parse_receipt_json(&raw) {
            Ok(_receipt) => ("ACCEPT", None),
            Err(error) => ("REJECT", Some(error.code.to_owned())),
        };
        println!("RI_RS_C6_CANDIDATE id={id} result={observed_result} code={}", observed_code.as_deref().unwrap_or("null"));
        rows.push(json!({
            "id": id,
            "input_file": relative,
            "input_bytes": raw.len(),
            "input_sha256": actual_sha,
            "observed_result": observed_result,
            "observed_code": observed_code,
            "exception_type": Value::Null,
        }));
    }

    let report = json!({
        "schema": "AURA-C6-CANDIDATE-OBSERVATION/0.1",
        "status": "OBSERVATION_COMPLETE",
        "mode": "OBSERVATION_ONLY",
        "implementation": "RI-RS-AURA-GUARD",
        "source_commit": actual_commit,
        "source_path": source_path,
        "source_git_blob_oid": source_blob,
        "source_content_sha256": sha256_hex(&source_raw),
        "lib_git_blob_oid": lib_blob,
        "cargo_toml_git_blob_oid": cargo_blob,
        "materialization_index_sha256": sha256_hex(&index_raw),
        "case_count": rows.len(),
        "cases": rows,
        "contract_binding_status": "UNRESOLVED",
        "expected_outcomes_assigned": false,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    });
    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(
        output_path,
        format!("{}\n", serde_json::to_string_pretty(&report)?),
    )?;
    println!("RI_RS_OBSERVATION_COUNT={}", PILOT_IDS.len());
    println!("EXPECTED_OUTCOMES_ASSIGNED=NO");
    println!("AUTHORITY=NONE");
    Ok(())
}
