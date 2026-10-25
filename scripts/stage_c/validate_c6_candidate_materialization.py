#!/usr/bin/env python3
"""Validate isolated C6 Candidate Lab materialization without executing parsers."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

BASELINE_SHA256 = "c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d"
INVENTORY_BLOB_OID = "06a4e8827fb589e3a549944c71718291d1345f16"
PILOT_IDS = [f"C6-X-{number:03d}" for number in range(13, 21)]
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")
MAX_SAMPLE_BYTES = 2_000_000


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    doc = json.loads(raw.decode("utf-8", errors="strict"))
    if not isinstance(doc, dict):
        raise ValueError(f"expected JSON object: {path}")
    return doc, raw


def safe_path(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe path: {relative!r}")
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"path escapes Candidate Lab root: {relative!r}")
    return resolved


def verify(root: Path) -> dict[str, Any]:
    root = root.resolve()
    lock, _ = read_json(root / "source-lock.json")
    index, index_raw = read_json(root / "materialization-index.json")
    inventory, inventory_raw = read_json(root / "inventory-snapshot.json")
    baseline_raw = (root / "baseline-manifest.raw").read_bytes()

    if lock.get("status") != "PASS_TECHNICAL_SOURCE_LOCK":
        raise ValueError("Source Lock did not pass")
    if lock.get("baseline", {}).get("content_sha256") != BASELINE_SHA256:
        raise ValueError("Source Lock baseline digest mismatch")
    if sha256(baseline_raw) != BASELINE_SHA256:
        raise ValueError("raw pinned baseline bytes differ from Source Lock")
    if lock.get("candidate_inventory", {}).get("git_blob_oid") != INVENTORY_BLOB_OID:
        raise ValueError("Source Lock inventory blob OID mismatch")
    if sha256(inventory_raw) != lock.get("candidate_inventory", {}).get("content_sha256"):
        raise ValueError("inventory snapshot digest mismatch")
    if index.get("source_inventory", {}).get("content_sha256") != sha256(inventory_raw):
        raise ValueError("materialization index inventory digest mismatch")
    if index.get("source_inventory", {}).get("git_blob_oid") != INVENTORY_BLOB_OID:
        raise ValueError("materialization index inventory blob OID mismatch")
    if index.get("schema") != "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1":
        raise ValueError("unexpected materialization index schema")
    if index.get("status") != "EXPLORATORY_NON_NORMATIVE":
        raise ValueError("candidate materialization must remain exploratory")
    for field in EFFECT_FIELDS:
        if index.get(field) != "NONE":
            raise ValueError(f"materialization index {field} must be NONE")
    if index.get("source_baseline", {}).get("manifest_content_sha256") != BASELINE_SHA256:
        raise ValueError("materialization index is not bound to the pinned manifest")
    if inventory.get("status") != "DRAFT_NON_NORMATIVE":
        raise ValueError("inventory snapshot must remain DRAFT_NON_NORMATIVE")
    for field in EFFECT_FIELDS:
        if inventory.get(field) != "NONE":
            raise ValueError(f"inventory snapshot {field} must remain NONE")

    active_ids = [
        case["id"] for case in inventory.get("cases", [])
        if isinstance(case, dict) and case.get("included_in_candidate_pool") is True
    ]
    entries = index.get("candidates")
    if not isinstance(entries, list) or len(entries) != 47:
        raise ValueError("materialization index must contain exactly 47 candidate entries")
    if [entry.get("id") for entry in entries] != active_ids:
        raise ValueError("materialized ID order/set differs from the active inventory")
    if len(set(active_ids)) != 47:
        raise ValueError("active inventory candidate IDs are not unique")
    if index.get("candidate_count") != 47:
        raise ValueError("candidate_count must be 47")

    declared_binary_paths: set[str] = set()
    for entry in entries:
        case_id = entry.get("id")
        if entry.get("contract_binding_status") != "UNRESOLVED":
            raise ValueError(f"{case_id}: contract binding must remain UNRESOLVED")
        if entry.get("expected_outcome_policy") != "CONTRACT_DECISION_REQUIRED":
            raise ValueError(f"{case_id}: expected outcome must remain unresolved")
        if entry.get("observation_only") is not True:
            raise ValueError(f"{case_id}: observation_only must be true")
        if entry.get("governance_effect") != "NONE":
            raise ValueError(f"{case_id}: governance effect must be NONE")
        if "expected_result" in entry or "expected_code" in entry:
            raise ValueError(f"{case_id}: normative expected outcome field found")

        path = safe_path(root, str(entry.get("input_file", "")))
        if not path.is_file():
            raise ValueError(f"{case_id}: materialized primary file missing")
        raw = path.read_bytes()
        if len(raw) != entry.get("input_bytes") or len(raw) > MAX_SAMPLE_BYTES:
            raise ValueError(f"{case_id}: primary byte length differs or exceeds limit")
        if sha256(raw) != entry.get("input_sha256"):
            raise ValueError(f"{case_id}: primary SHA-256 mismatch")

        if entry.get("materialization_kind") == "BYTES":
            declared_binary_paths.add(str(entry["input_file"]))
        elif entry.get("materialization_kind") not in {"MULTI_SAMPLE_SET", "GENERATOR_CONFIGURATION"}:
            raise ValueError(f"{case_id}: unknown materialization kind")
        for sub in entry.get("supplementary_inputs", []):
            sub_path = safe_path(root, str(sub.get("input_file", "")))
            if not sub_path.is_file():
                raise ValueError(f"{sub.get('id')}: supplementary file missing")
            sub_raw = sub_path.read_bytes()
            if len(sub_raw) != sub.get("input_bytes") or len(sub_raw) > MAX_SAMPLE_BYTES:
                raise ValueError(f"{sub.get('id')}: supplementary byte length mismatch/limit")
            if sha256(sub_raw) != sub.get("input_sha256"):
                raise ValueError(f"{sub.get('id')}: supplementary SHA-256 mismatch")
            if sub.get("observation_only") is not True:
                raise ValueError(f"{sub.get('id')}: supplementary sample must be observation-only")
            declared_binary_paths.add(str(sub["input_file"]))

    actual_binary_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "inputs").rglob("*.bin")
        if path.is_file()
    }
    if actual_binary_paths != declared_binary_paths:
        missing = sorted(declared_binary_paths - actual_binary_paths)
        extra = sorted(actual_binary_paths - declared_binary_paths)
        raise ValueError(f"binary input inventory mismatch; missing={missing}, extra={extra}")
    if index.get("materialized_input_artifact_count") != len(actual_binary_paths):
        raise ValueError("materialized_input_artifact_count mismatch")

    if index.get("pilot_group", {}).get("candidate_ids") != PILOT_IDS:
        raise ValueError("JSON pilot group must be exactly C6-X-013 through C6-X-020")
    if not all(any(entry.get("id") == candidate_id and entry.get("materialization_kind") == "BYTES" for entry in entries) for candidate_id in PILOT_IDS):
        raise ValueError("one or more JSON pilot inputs are not standalone raw-byte candidates")

    fuzz, _ = read_json(root / "fuzz-seeds.json")
    fuzz_entry = next(entry for entry in entries if entry.get("id") == "C6-X-050")
    if fuzz.get("schema") != "AURA-C6-BOUNDED-FUZZ-SEED-SET/0.1":
        raise ValueError("missing bounded fuzz seed schema")
    if fuzz.get("seed_count") != 8 or len(fuzz.get("seeds", [])) != 8:
        raise ValueError("fuzz seed count must be exactly eight")
    if fuzz.get("max_seed_count") != 8 or fuzz.get("max_sample_bytes") != MAX_SAMPLE_BYTES:
        raise ValueError("fuzz resource limits changed")
    for field in EFFECT_FIELDS:
        if fuzz.get(field) != "NONE":
            raise ValueError(f"fuzz seed manifest {field} must be NONE")
    if [sample.get("id") for sample in fuzz["seeds"]] != [f"C6-X-050-S{number:03d}" for number in range(1, 9)]:
        raise ValueError("fuzz sample IDs are not deterministic/contiguous")
    if len(fuzz_entry.get("supplementary_inputs", [])) != 8:
        raise ValueError("C6-X-050 must reference eight individual seed samples")

    summary = {
        "schema": "AURA-C6-CANDIDATE-MATERIALIZATION-VALIDATION/0.1",
        "status": "PASS_STRUCTURAL_AND_BYTE_INTEGRITY",
        "candidate_count": 47,
        "binary_input_count": len(actual_binary_paths),
        "json_pilot_count": len(PILOT_IDS),
        "fuzz_seed_count": 8,
        "materialization_index_sha256": sha256(index_raw),
        "baseline_manifest_sha256": BASELINE_SHA256,
        "contract_resolution": "UNRESOLVED",
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    (root / "materialization-validation.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("C6_CANDIDATE_MATERIALIZATION_VALIDATION=PASS")
    print(f"CANDIDATE_COUNT={len(entries)}")
    print(f"BINARY_INPUT_COUNT={len(actual_binary_paths)}")
    print(f"JSON_PILOT_COUNT={len(PILOT_IDS)}")
    print("FUZZ_SEEDS=8")
    print("PARSER_EXECUTION=NOT_PERFORMED")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    verify(args.root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(f"C6_CANDIDATE_MATERIALIZATION_VALIDATION=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
