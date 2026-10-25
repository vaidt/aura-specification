#!/usr/bin/env python3
"""Observe (do not judge) RI-PY behavior on the isolated C6 JSON pilot."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

CORE_COMMIT = "fe3be05794d3f254d98af1464e598e5b9be2e369"
PILOT_IDS = [f"C6-X-{number:03d}" for number in range(13, 21)]
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.STDOUT).decode().strip()


def safe_path(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe candidate input path: {relative!r}")
    base = root.resolve()
    path = (root / candidate).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"candidate input escapes lab directory: {relative!r}")
    return path


def observe(core_root: Path, index_path: Path, lab_root: Path, output_path: Path) -> dict[str, Any]:
    core_root = core_root.resolve()
    lab_root = lab_root.resolve()
    index_raw = index_path.read_bytes()
    index = json.loads(index_raw.decode("utf-8", errors="strict"))
    if index.get("schema") != "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1":
        raise ValueError("unexpected candidate materialization index schema")
    if index.get("status") != "EXPLORATORY_NON_NORMATIVE":
        raise ValueError("candidate index is not marked exploratory")
    for field in EFFECT_FIELDS:
        if index.get(field) != "NONE":
            raise ValueError(f"candidate index {field} must be NONE")
    actual_commit = git(core_root, "rev-parse", "HEAD")
    if actual_commit != CORE_COMMIT:
        raise ValueError(f"RI-PY source commit mismatch: expected {CORE_COMMIT}, got {actual_commit}")
    receiver_path = "conformance/boundary/ri_py_receiver.py"
    receiver_blob = git(core_root, "rev-parse", f"HEAD:{receiver_path}")
    receiver_raw = (core_root / receiver_path).read_bytes()

    entries = index.get("candidates")
    if not isinstance(entries, list):
        raise ValueError("candidate index has no candidate list")
    selected = {entry.get("id"): entry for entry in entries if isinstance(entry, dict)}
    if not all(candidate_id in selected for candidate_id in PILOT_IDS):
        raise ValueError("JSON pilot candidate missing from materialization index")
    for candidate_id in PILOT_IDS:
        entry = selected[candidate_id]
        if entry.get("materialization_kind") != "BYTES" or entry.get("contract_binding_status") != "UNRESOLVED":
            raise ValueError(f"{candidate_id}: pilot must be a standalone unresolved byte sample")
        if "expected_result" in entry or "expected_code" in entry:
            raise ValueError(f"{candidate_id}: expected outcomes must not be supplied")
        for field in EFFECT_FIELDS:
            if field == "authority":
                continue
            if entry.get("governance_effect") != "NONE":
                raise ValueError(f"{candidate_id}: governance effect must remain NONE")

    sys.path.insert(0, str(core_root))
    from conformance.boundary.ri_py_receiver import ReceiptParseError, parse_receipt_json  # noqa: E402

    rows: list[dict[str, Any]] = []
    for candidate_id in PILOT_IDS:
        entry = selected[candidate_id]
        input_path = safe_path(lab_root, str(entry.get("input_file", "")))
        raw = input_path.read_bytes()
        if len(raw) != entry.get("input_bytes") or sha256(raw) != entry.get("input_sha256"):
            raise ValueError(f"{candidate_id}: input bytes do not match materialization index")
        try:
            parse_receipt_json(raw)
            result, code, exception_type = "ACCEPT", None, None
        except ReceiptParseError as exc:
            result, code, exception_type = "REJECT", str(exc.code), None
        except Exception as exc:
            result, code, exception_type = "EXECUTION_ERROR", None, type(exc).__name__
        rows.append({
            "id": candidate_id,
            "input_file": entry["input_file"],
            "input_bytes": len(raw),
            "input_sha256": sha256(raw),
            "observed_result": result,
            "observed_code": code,
            "exception_type": exception_type,
        })
        print(f"RI_PY_C6_CANDIDATE id={candidate_id} result={result} code={code if code is not None else 'null'}")

    report = {
        "schema": "AURA-C6-CANDIDATE-OBSERVATION/0.1",
        "status": "OBSERVATION_COMPLETE",
        "mode": "OBSERVATION_ONLY",
        "implementation": "RI-PY-AURA-CORE",
        "source_commit": actual_commit,
        "source_path": receiver_path,
        "source_git_blob_oid": receiver_blob,
        "source_content_sha256": sha256(receiver_raw),
        "materialization_index_sha256": sha256(index_raw),
        "case_count": len(rows),
        "cases": rows,
        "contract_binding_status": "UNRESOLVED",
        "expected_outcomes_assigned": False,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"RI_PY_OBSERVATION_COUNT={len(rows)}")
    print("EXPECTED_OUTCOMES_ASSIGNED=NO")
    print("AUTHORITY=NONE")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--lab-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    observe(args.core_root, args.index, args.lab_root, args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"RI_PY_C6_CANDIDATE_OBSERVATION=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
