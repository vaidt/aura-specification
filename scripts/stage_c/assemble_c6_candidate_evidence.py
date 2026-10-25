#!/usr/bin/env python3
"""Assemble the nine logical evidence components for a C6 Candidate Lab run."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

EFFECTS = {"authority": "NONE", "governance_effect": "NONE", "authorization_effect": "NONE", "release_effect": "NONE"}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def find_all(root: Path, name: str) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob(name) if path.is_file())


def first_file(root: Path, name: str) -> Path | None:
    matches = find_all(root, name)
    return matches[0] if matches else None


def copy_or_placeholder(source: Path | None, target: Path, schema: str, status: str) -> dict[str, Any]:
    if source is not None:
        shutil.copyfile(source, target)
        loaded = load_json(target)
        if loaded is not None:
            return loaded
    target.write_text(json.dumps({
        "schema": schema,
        "status": status,
        "missing_source": source is None,
        **EFFECTS,
    }, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {"schema": schema, "status": status, **EFFECTS}


def assemble(args: argparse.Namespace) -> dict[str, Any]:
    materialization_dir = args.materialization_dir.resolve()
    baseline_dir = args.baseline_dir.resolve()
    pilot_dir = args.pilot_dir.resolve()
    out = args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"refusing to overwrite evidence package directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    source_lock = copy_or_placeholder(
        first_file(materialization_dir, "source-lock.json"), out / "source-lock.json",
        "AURA-C6-CANDIDATE-LAB-SOURCE-LOCK/0.1", "EXECUTION_INCOMPLETE",
    )
    inventory_path = first_file(materialization_dir, "inventory-snapshot.json")
    inventory_doc = copy_or_placeholder(
        inventory_path, out / "inventory-snapshot.json",
        "AURA-BC021-C6-EXTENDED-CANDIDATE-INVENTORY/0.1", "EXECUTION_INCOMPLETE",
    )
    materialization_path = first_file(materialization_dir, "materialization-index.json")
    materialization_doc = copy_or_placeholder(
        materialization_path, out / "materialization-index.json",
        "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1", "EXECUTION_INCOMPLETE",
    )

    py_path = first_file(pilot_dir, "ri-py-json-observations.json")
    py_doc = copy_or_placeholder(
        py_path, out / "ri-py-report.json",
        "AURA-C6-CANDIDATE-OBSERVATION/0.1", "EXECUTION_INCOMPLETE",
    )
    rs_path = first_file(pilot_dir, "ri-rs-json-observations.json")
    rs_doc = copy_or_placeholder(
        rs_path, out / "ri-rs-report.json",
        "AURA-C6-CANDIDATE-OBSERVATION/0.1", "EXECUTION_INCOMPLETE",
    )
    diff_path = first_file(pilot_dir, "differential-report.json")
    diff_doc = copy_or_placeholder(
        diff_path, out / "differential-report.json",
        "AURA-C6-CANDIDATE-DIFFERENTIAL-REPORT/0.1", "EXECUTION_INCOMPLETE",
    )

    baseline_files = find_all(baseline_dir, "baseline-regression-report.json")
    baseline_reports = [(path.parent.name, load_json(path)) for path in baseline_files]
    baseline_reports = [(name, report) for name, report in baseline_reports if report is not None]
    if len(baseline_reports) >= 2 and all(report.get("status") == "PASS" for _, report in baseline_reports):
        baseline_status = "PASS"
    elif any(report.get("status") == "FAIL" for _, report in baseline_reports):
        baseline_status = "FAIL"
    else:
        baseline_status = "EXECUTION_INCOMPLETE"
    baseline_doc = {
        "schema": "AURA-C6-HISTORICAL-BASELINE-REGRESSION-AGGREGATE/0.1",
        "status": baseline_status,
        "expected_architectures": ["x86_64", "aarch64"],
        "reports_found": len(baseline_reports),
        "architectures": {name: report for name, report in baseline_reports},
        "historical_reference_run_id": 40176350679,
        **EFFECTS,
    }
    (out / "baseline-regression-report.json").write_text(json.dumps(baseline_doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Preserve run inputs and all per-architecture reports outside the nine primary
    # evidence documents. This prevents the index from replacing or mutating baseline data.
    support = out / "supporting-evidence"
    support.mkdir()
    if materialization_dir.exists():
        for name in ("baseline-manifest.raw", "materialization-validation.json", "fuzz-seeds.json"):
            source = materialization_dir / name
            if source.is_file():
                shutil.copyfile(source, support / name)
        for name in ("inputs", "candidate-configs"):
            source = materialization_dir / name
            if source.is_dir():
                shutil.copytree(source, support / name)
    for path in baseline_files:
        try:
            arch = path.parent.name
            dest = support / "baseline" / arch
            dest.mkdir(parents=True, exist_ok=True)
            for name in ("baseline-regression-report.json", "source-identities.txt"):
                source = path.parent / name
                if source.is_file():
                    shutil.copyfile(source, dest / name)
            for name in ("index.json", "ri-py-results.json", "ri-rs-results.json"):
                matches = find_all(path.parent, name)
                if matches:
                    shutil.copyfile(matches[0], dest / name)
        except OSError:
            pass

    lab_ready = (
        source_lock.get("status") == "PASS_TECHNICAL_SOURCE_LOCK"
        and inventory_doc.get("status") == "DRAFT_NON_NORMATIVE"
        and materialization_doc.get("status") == "EXPLORATORY_NON_NORMATIVE"
        and len(materialization_doc.get("candidates", [])) == 47
    )
    baseline_ready = baseline_status == "PASS"
    pilot_complete = (
        py_doc.get("status") == "OBSERVATION_COMPLETE"
        and rs_doc.get("status") == "OBSERVATION_COMPLETE"
        and diff_doc.get("status") in {"CONTRACT_UNRESOLVED", "AGREEMENT"}
        and diff_doc.get("mismatch_count") == 0
    )
    if not lab_ready or not baseline_ready or not pilot_complete:
        if diff_doc.get("status") == "MISMATCH":
            overall = "MISMATCH"
        else:
            overall = "EXECUTION_INCOMPLETE"
    else:
        # Expected results remain contract-unresolved by design.
        overall = "CONTRACT_UNRESOLVED"

    disposition_doc = {
        "schema": "AURA-C6-CANDIDATE-LAB-DISPOSITION/0.1",
        "status": overall,
        "run_id": str(args.run_id),
        "run_attempt": str(args.run_attempt),
        "source_lock": "PASS" if lab_ready else "INCOMPLETE",
        "candidate_materialization": "PASS" if materialization_doc.get("candidate_count") == 47 and materialization_doc.get("status") == "EXPLORATORY_NON_NORMATIVE" else "INCOMPLETE",
        "baseline_regression": baseline_status,
        "json_pilot_differential": diff_doc.get("status", "EXECUTION_INCOMPLETE"),
        "expected_outcomes_assigned": False,
        "contract_binding_status": "UNRESOLVED",
        "interpretation": "Technical observations only. Even cross-implementation agreement is not proof of contract correctness, protocol ratification, or release readiness.",
        "frozen_statuses": {
            "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
            "conf_003": "PARTIAL",
            "dq_006": "OPEN",
            "m1_g1": "BLOCKED_NOT_PROVEN",
            "release": "NO_GO",
            "existing_pull_requests": "UNCHANGED",
        },
        **EFFECTS,
    }
    (out / "disposition-report.json").write_text(json.dumps(disposition_doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # The integrity manifest covers every evidence file except itself, avoiding a circular hash.
    integrity_items = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "integrity-manifest.json"):
        raw = path.read_bytes()
        integrity_items.append({
            "path": path.relative_to(out).as_posix(),
            "bytes": len(raw),
            "sha256": sha256(raw),
        })
    integrity_doc = {
        "schema": "AURA-C6-CANDIDATE-LAB-INTEGRITY-MANIFEST/0.1",
        "status": "COMPLETE" if lab_ready and baseline_ready and pilot_complete else "PARTIAL",
        "self_hash_included": False,
        "hash_algorithm": "SHA-256",
        "file_count": len(integrity_items),
        "files": integrity_items,
        "run_id": str(args.run_id),
        "run_attempt": str(args.run_attempt),
        **EFFECTS,
    }
    (out / "integrity-manifest.json").write_text(json.dumps(integrity_doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"C6_CANDIDATE_LAB_PACKAGE_STATUS={overall}")
    print(f"BASELINE_REGRESSION={baseline_status}")
    print(f"JSON_PILOT={diff_doc.get('status', 'EXECUTION_INCOMPLETE')}")
    print(f"PRIMARY_EVIDENCE_DOCUMENTS=9")
    print(f"INTEGRITY_FILE_COUNT={len(integrity_items)}")
    return disposition_doc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--materialization-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--pilot-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    args = parser.parse_args()
    result = assemble(args)
    return 0 if result["status"] == "CONTRACT_UNRESOLVED" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"C6_CANDIDATE_LAB_ASSEMBLY=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
