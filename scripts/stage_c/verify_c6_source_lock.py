#!/usr/bin/env python3
"""Fail-closed L0 Source Lock for the non-normative AURA C6 Candidate Lab."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BASELINE_COMMIT = "6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330"
BASELINE_PATH = "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"
BASELINE_BLOB_OID = "d9b4a1f488185a44f7edb233ef8ff180981f0e84"
BASELINE_CONTENT_SHA256 = "c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d"

INVENTORY_COMMIT = "3a8e7ac3e26faa92fe383d090fe366b72ff438ff"
INVENTORY_PATH = "fixtures/corpus/STAGE-C-C6-EXTENDED-CANDIDATE-INVENTORY-v0.1-DRAFT.json"
INVENTORY_BLOB_OID = "06a4e8827fb589e3a549944c71718291d1345f16"
INVENTORY_SCHEMA = "AURA-BC021-C6-EXTENDED-CANDIDATE-INVENTORY/0.1"

CORE_COMMIT = "fe3be05794d3f254d98af1464e598e5b9be2e369"
RI_RS_COMMIT = "feab2d9c369cd5f8cbabe10d713d278b0b09da8b"
INTEGRATED_HARNESS_COMMIT = "38821305ddb93eca96d9eb86e53d5c2db5d91295"
HISTORICAL_RUN_ID = 40176350679
HISTORICAL_REPORTS = {
    "materialized_index_sha256": "445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181",
    "ri_py_report_sha256": "cfdbd0fbbc1442bba0b7a70a5bf7c76fc5ecd9cb2dabe27ffe4379053196a6a4",
    "ri_rs_report_sha256": "b289367fc2e19f0666d202d35eb257d795ff18c589d7d0323c202e6a4636e25b",
}
HISTORICAL_ARTIFACTS = [
    {
        "name": "integrated-c6-x86_64",
        "artifact_id": 12593090186,
        "sha256": "ffbf20cb99341bcd6c7cd33c08077ccaef0be10874e912116580b7499c6d9a4b",
    },
    {
        "name": "integrated-c6-aarch64",
        "artifact_id": 12592151568,
        "sha256": "77ab20466221e078ff6bcef2f6f9a0795f4b2cfdd5f3e0843d6f1fe5702feba3",
    },
    {
        "name": "integrated-c6-cross-implementation-summary",
        "artifact_id": 12592616150,
        "sha256": "ad78a4eccaa7e4c467a4a65e483e426e1042fd5411ce9de036ad75a82b9307f4",
    },
]
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.STDOUT
    ).decode("utf-8", errors="strict").strip()


def git_blob(root: Path, commit: str, path: str) -> tuple[str, bytes]:
    oid = git(root, "rev-parse", f"{commit}:{path}")
    raw = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", oid])
    return oid, raw


def write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def verify(candidate_root: Path, baseline_root: Path, output_dir: Path) -> dict[str, Any]:
    candidate_root = candidate_root.resolve()
    baseline_root = baseline_root.resolve()
    output_dir = output_dir.resolve()

    baseline_head = git(baseline_root, "rev-parse", "HEAD")
    if baseline_head != BASELINE_COMMIT:
        raise ValueError(f"baseline commit mismatch: expected {BASELINE_COMMIT}, got {baseline_head}")
    baseline_oid, baseline_raw = git_blob(baseline_root, BASELINE_COMMIT, BASELINE_PATH)
    if baseline_oid != BASELINE_BLOB_OID:
        raise ValueError(f"baseline Git blob OID mismatch: {baseline_oid}")
    baseline_sha = sha256(baseline_raw)
    if baseline_sha != BASELINE_CONTENT_SHA256:
        raise ValueError(f"baseline content SHA-256 mismatch: {baseline_sha}")
    baseline_doc = json.loads(baseline_raw.decode("utf-8", errors="strict"))
    if baseline_doc.get("schema") != "AURA-BC021-STRICT-WIRE-MUTATION-CORPUS/0.1":
        raise ValueError("baseline corpus schema mismatch")
    if baseline_doc.get("status") != "DRAFT_NON_NORMATIVE" or baseline_doc.get("stage") != "C6_PREPARATION":
        raise ValueError("baseline must remain a draft C6 preparation artifact")
    for field in EFFECT_FIELDS:
        if baseline_doc.get(field) != "NONE":
            raise ValueError(f"baseline {field} must remain NONE")
    if len(baseline_doc.get("mutations", [])) != 27:
        raise ValueError("baseline manifest must contain exactly 27 cases")

    origin_oid, origin_inventory_raw = git_blob(candidate_root, INVENTORY_COMMIT, INVENTORY_PATH)
    current_head = git(candidate_root, "rev-parse", "HEAD")
    current_oid, current_inventory_blob = git_blob(candidate_root, current_head, INVENTORY_PATH)
    inventory_worktree_raw = (candidate_root / INVENTORY_PATH).read_bytes()
    if origin_oid != INVENTORY_BLOB_OID or current_oid != INVENTORY_BLOB_OID:
        raise ValueError("candidate inventory Git blob differs from the pinned inventory")
    if inventory_worktree_raw != current_inventory_blob or origin_inventory_raw != current_inventory_blob:
        raise ValueError("candidate inventory worktree/blob/source pin mismatch")
    inventory_sha = sha256(current_inventory_blob)
    inventory = json.loads(current_inventory_blob.decode("utf-8", errors="strict"))
    if inventory.get("schema") != INVENTORY_SCHEMA or inventory.get("status") != "DRAFT_NON_NORMATIVE":
        raise ValueError("candidate inventory must remain DRAFT_NON_NORMATIVE")
    if inventory.get("stage") != "C6_PREPARATION":
        raise ValueError("candidate inventory stage mismatch")
    for field in EFFECT_FIELDS:
        if inventory.get(field) != "NONE":
            raise ValueError(f"candidate inventory {field} must remain NONE")
    cases = inventory.get("cases")
    if not isinstance(cases, list) or len(cases) != 50:
        raise ValueError("candidate inventory must contain 50 source entries")
    active_ids = [item.get("id") for item in cases if item.get("included_in_candidate_pool") is True]
    if len(active_ids) != 47 or len(set(active_ids)) != 47:
        raise ValueError("candidate inventory must have exactly 47 unique active entries")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_new(output_dir / "baseline-manifest.raw", baseline_raw)
    write_new(output_dir / "inventory-snapshot.json", current_inventory_blob)
    lock: dict[str, Any] = {
        "schema": "AURA-C6-CANDIDATE-LAB-SOURCE-LOCK/0.1",
        "status": "PASS_TECHNICAL_SOURCE_LOCK",
        "scope": "EXPLORATORY_NON_NORMATIVE_ONLY",
        "baseline": {
            "repository": "vaidt/aura-specification",
            "commit": BASELINE_COMMIT,
            "path": BASELINE_PATH,
            "git_blob_oid": baseline_oid,
            "content_sha256": baseline_sha,
            "content_bytes": len(baseline_raw),
            "case_count": 27,
        },
        "candidate_inventory": {
            "repository": "vaidt/aura-specification",
            "origin_commit": INVENTORY_COMMIT,
            "checkout_commit": current_head,
            "path": INVENTORY_PATH,
            "git_blob_oid": current_oid,
            "content_sha256": inventory_sha,
            "source_entries": 50,
            "active_candidates": 47,
        },
        "parser_source_pins": {
            "ri_py_repository": "vaidt/aura-poc-a-core-v3.3",
            "ri_py_commit": CORE_COMMIT,
            "ri_rs_repository": "vaidt/aura-guard-v1.3",
            "ri_rs_commit": RI_RS_COMMIT,
            "integrated_harness_repository": "vaidt/aura-specification",
            "integrated_harness_commit": INTEGRATED_HARNESS_COMMIT,
        },
        "historical_baseline_run": {
            "run_id": HISTORICAL_RUN_ID,
            "url": "https://github.com/vaidt/aura-specification/actions/runs/40176350679",
            "report_sha256": HISTORICAL_REPORTS,
            "artifact_archive_references": HISTORICAL_ARTIFACTS,
            "archive_digest_note": "These are pinned historical GitHub artifact digests; L6 independently compares the newly generated deterministic index and result-report bytes against the recorded report hashes.",
        },
        "execution_contract": {
            "expected_result_locking": "PROHIBITED_WHILE_CONTRACT_BINDING_UNRESOLVED",
            "candidate_execution": "OBSERVATION_ONLY",
            "baseline_mutation": "PROHIBITED",
            "automatic_governance_effect": "NONE",
        },
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    write_new(output_dir / "source-lock.json", (json.dumps(lock, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print("C6_SOURCE_LOCK=PASS")
    print(f"BASELINE_COMMIT={baseline_head}")
    print(f"BASELINE_BLOB_OID={baseline_oid}")
    print(f"BASELINE_SHA256={baseline_sha}")
    print(f"INVENTORY_BLOB_OID={current_oid}")
    print(f"ACTIVE_CANDIDATES={len(active_ids)}")
    print("AUTHORITY=NONE")
    return lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    verify(args.candidate_root, args.baseline_root, args.output_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"C6_SOURCE_LOCK=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
