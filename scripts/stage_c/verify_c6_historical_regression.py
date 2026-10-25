#!/usr/bin/env python3
"""Fail-closed L6 verifier for exact reproduction of the historical 27-case C6 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED = {
    "baseline_commit": "6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330",
    "ri_py_commit": "fe3be05794d3f254d98af1464e598e5b9be2e369",
    "ri_rs_commit": "feab2d9c369cd5f8cbabe10d713d278b0b09da8b",
    "harness_commit": "38821305ddb93eca96d9eb86e53d5c2db5d91295",
    "index_sha256": "445d5808cb76a24b916a91e91636d4ce10ac3b0239f9eb2f474264783bc41181",
    "ri_py_report_sha256": "cfdbd0fbbc1442bba0b7a70a5bf7c76fc5ecd9cb2dabe27ffe4379053196a6a4",
    "ri_rs_report_sha256": "b289367fc2e19f0666d202d35eb257d795ff18c589d7d0323c202e6a4636e25b",
    "manifest_sha256": "c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d",
}
HISTORICAL_ARTIFACTS = [
    {"name": "integrated-c6-x86_64", "artifact_id": 12593090186, "sha256": "ffbf20cb99341bcd6c7cd33c08077ccaef0be10874e912116580b7499c6d9a4b"},
    {"name": "integrated-c6-aarch64", "artifact_id": 12592151568, "sha256": "77ab20466221e078ff6bcef2f6f9a0795f4b2cfdd5f3e0843d6f1fe5702feba3"},
    {"name": "integrated-c6-cross-implementation-summary", "artifact_id": 12592616150, "sha256": "ad78a4eccaa7e4c467a4a65e483e426e1042fd5411ce9de036ad75a82b9307f4"},
]
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.STDOUT).decode().strip()


def read_bytes(path: Path, label: str, errors: list[str]) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError as exc:
        errors.append(f"{label}_missing_or_unreadable:{type(exc).__name__}")
        return None


def verify(args: argparse.Namespace) -> dict[str, Any]:
    corpus_dir = args.corpus_dir.resolve()
    core_root, guard_root = args.core_root.resolve(), args.guard_root.resolve()
    source_root, harness_root = args.source_root.resolve(), args.harness_root.resolve()
    errors: list[str] = []
    commits: dict[str, str | None] = {}
    for label, root, expected in [
        ("baseline", source_root, EXPECTED["baseline_commit"]),
        ("ri_py", core_root, EXPECTED["ri_py_commit"]),
        ("ri_rs", guard_root, EXPECTED["ri_rs_commit"]),
        ("harness", harness_root, EXPECTED["harness_commit"]),
    ]:
        try:
            actual = git(root, "rev-parse", "HEAD")
        except (OSError, subprocess.CalledProcessError) as exc:
            actual = None
            errors.append(f"{label}_commit_unavailable:{type(exc).__name__}")
        commits[label] = actual
        if actual != expected:
            errors.append(f"{label}_commit_mismatch:expected={expected}:actual={actual}")

    manifest_path = source_root / "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"
    materializer_path = source_root / "scripts/stage_c/materialize_c6_wire_corpus.py"
    manifest_raw = read_bytes(manifest_path, "baseline_manifest", errors)
    if manifest_raw is not None and sha256(manifest_raw) != EXPECTED["manifest_sha256"]:
        errors.append("baseline_manifest_content_sha256_mismatch")

    blobs: dict[str, str | None] = {}
    for label, root, path in [
        ("ri_py_receiver", core_root, "conformance/boundary/ri_py_receiver.py"),
        ("ri_rs_parser", guard_root, "conformance/strict_wire.rs"),
        ("baseline_manifest", source_root, "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"),
        ("baseline_materializer", source_root, "scripts/stage_c/materialize_c6_wire_corpus.py"),
        ("harness_runner", harness_root, "scripts/stage_c/run_ri_py_c6_consumer.py"),
        ("harness_verifier", harness_root, "scripts/stage_c/verify_integrated_c6.py"),
    ]:
        try:
            blobs[label] = git(root, "rev-parse", f"HEAD:{path}")
        except (OSError, subprocess.CalledProcessError):
            blobs[label] = None
            errors.append(f"{label}_blob_oid_unavailable")
    if blobs.get("baseline_manifest") != "d9b4a1f488185a44f7edb233ef8ff180981f0e84":
        errors.append("baseline_manifest_git_blob_oid_mismatch")

    index_raw = read_bytes(corpus_dir / "index.json", "materialized_index", errors)
    py_raw = read_bytes(corpus_dir / "results/ri-py-results.json", "ri_py_report", errors)
    rs_raw = read_bytes(corpus_dir / "results/ri-rs-results.json", "ri_rs_report", errors)
    digests = {
        "index_sha256": sha256(index_raw) if index_raw is not None else None,
        "ri_py_report_sha256": sha256(py_raw) if py_raw is not None else None,
        "ri_rs_report_sha256": sha256(rs_raw) if rs_raw is not None else None,
    }
    for field, actual in digests.items():
        if actual != EXPECTED[field]:
            errors.append(f"{field}_historical_byte_match_failed:expected={EXPECTED[field]}:actual={actual}")

    for raw, label in [(index_raw, "index"), (py_raw, "ri_py_report"), (rs_raw, "ri_rs_report")]:
        if raw is None:
            continue
        try:
            doc = json.loads(raw.decode("utf-8", errors="strict"))
            if not isinstance(doc, dict):
                errors.append(f"{label}_not_json_object")
                continue
            if label == "index":
                if doc.get("case_count") != 27 or doc.get("schema") != "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1":
                    errors.append("baseline_index_schema_or_count_mismatch")
            else:
                if doc.get("case_count") != 27 or doc.get("status") != "PASS" or doc.get("mismatches") != []:
                    errors.append(f"{label}_not_complete_27_of_27_PASS")
            for field in EFFECT_FIELDS:
                if doc.get(field) != "NONE":
                    errors.append(f"{label}_{field}_must_be_NONE")
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"{label}_invalid_json")

    report: dict[str, Any] = {
        "schema": "AURA-C6-HISTORICAL-BASELINE-REGRESSION/0.1",
        "status": "PASS" if not errors else "FAIL",
        "mode": "TECHNICAL_REGRESSION_ONLY",
        "historical_reference_run_id": 40176350679,
        "historical_reference_url": "https://github.com/vaidt/aura-specification/actions/runs/40176350679",
        "expected_source_commits": {
            "baseline": EXPECTED["baseline_commit"],
            "ri_py": EXPECTED["ri_py_commit"],
            "ri_rs": EXPECTED["ri_rs_commit"],
            "harness": EXPECTED["harness_commit"],
        },
        "actual_source_commits": commits,
        "source_git_blob_oids": blobs,
        "actual_report_sha256": digests,
        "expected_historical_report_sha256": {
            "index_sha256": EXPECTED["index_sha256"],
            "ri_py_report_sha256": EXPECTED["ri_py_report_sha256"],
            "ri_rs_report_sha256": EXPECTED["ri_rs_report_sha256"],
        },
        "historical_artifact_archive_references": HISTORICAL_ARTIFACTS,
        "archive_digest_note": "Archive digests identify the historical GitHub artifacts. This gate compares the reproducibly generated index and RI-PY/RI-RS report bytes against the recorded SHA-256 values; it does not recreate GitHub's archive container.",
        "case_count_required": 27,
        "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
        "errors": errors,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"C6_BASELINE_REGRESSION={report['status']}")
    print(f"BASELINE_INDEX_SHA256={digests['index_sha256']}")
    print(f"RI_PY_REPORT_SHA256={digests['ri_py_report_sha256']}")
    print(f"RI_RS_REPORT_SHA256={digests['ri_rs_report_sha256']}")
    print(f"BASELINE_REGRESSION_ERRORS={json.dumps(errors, sort_keys=True)}")
    print("C6_GATE_STATUS=BLOCKED_PENDING_EVIDENCE_REVIEW")
    print("AUTHORITY=NONE")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", type=Path, required=True)
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--guard-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--harness-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"C6_BASELINE_REGRESSION=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
