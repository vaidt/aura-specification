#!/usr/bin/env python3
"""Repo-native draft conformance runner for the current specification workspace."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIX001_FIXTURE_PATH = ROOT / "fixtures" / "core" / "FIX-001_BASIC_EVALUATION.json"
FIX001_GATE_PATH = ROOT / "scripts" / "check-fix001-evidence.py"
COMPAT_FIXTURE_PATH = ROOT / "fixtures" / "compatibility" / "FIX-COMPAT-001_VERSION_MATRIX.json"
COMPAT_MATRIX_PATH = (
    ROOT / "ck003" / "decisions" / "DQ-003" / "CURRENT_VERSION_COMPATIBILITY_MATRIX.json"
)

CONF_TITLES = {
    "CONF-001": "Deterministic Evaluation",
    "CONF-002": "Replay Verification",
    "CONF-003": "Canonical Serialization",
    "CONF-004": "Evidence Integrity",
    "CONF-005": "Traceability",
    "CONF-006": "Platform Independence",
    "CONF-007": "Fail Closed",
    "CONF-008": "Version Compatibility",
    "CONF-009": "Conformance Completeness",
    "CONF-010": "Cryptographic Verification",
    "CONF-011": "Zero Float Runtime",
    "CONF-012": "Auditability",
    "CONF-013": "Policy Determinism",
    "CONF-014": "Reference Compatibility",
    "CONF-015": "Canonical Identity",
}
FIX001_CONF_IDS = ["CONF-001", "CONF-002", "CONF-004", "CONF-005", "CONF-006", "CONF-010"]
NON_EXECUTED_RESULTS = [
    (
        "CONF-003",
        "OPEN",
        "DQ-006 still needs discriminating cross-language execution evidence for canonical serialization.",
    ),
    (
        "CONF-007",
        "BLOCKED",
        "No FIX-ERROR fixture is bound yet for the fail-closed path.",
    ),
    (
        "CONF-009",
        "OPEN",
        "Structural mapping exists, but full invariant-to-execution evidence is not yet complete.",
    ),
    (
        "CONF-011",
        "READY",
        "FIX-INV-007 exists; the remaining step is controlled execution evidence.",
    ),
    (
        "CONF-012",
        "BLOCKED",
        "DQ-004 event vocabulary is still empty, so strict auditability cannot yet PASS.",
    ),
    (
        "CONF-013",
        "READY",
        "FIX-INV-013 is concrete; controlled execution evidence is still outstanding.",
    ),
    (
        "CONF-014",
        "BLOCKED",
        "The normative APS-500 corpus is not yet frozen.",
    ),
    (
        "CONF-015",
        "BLOCKED",
        "Canonical identity semantics remain draft-bound and are not yet fully closed for objective execution.",
    ),
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def make_result(conf_id: str, status: str, note: str) -> dict:
    return {
        "id": conf_id,
        "title": CONF_TITLES[conf_id],
        "status": status,
        "note": note,
    }


def load_fix001_gate_module():
    spec = importlib.util.spec_from_file_location("check_fix001_evidence", FIX001_GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load FIX-001 gate from {FIX001_GATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_fix001_results() -> list[dict]:
    module = load_fix001_gate_module()
    try:
        messages = module.run_fix001_gate()
        missing = [conf_id for conf_id in FIX001_CONF_IDS if conf_id not in messages]
        if missing:
            raise AssertionError(
                f"FIX-001 draft gate did not return results for: {', '.join(missing)}"
            )
        return [make_result(conf_id, "PASS", messages[conf_id]) for conf_id in FIX001_CONF_IDS]
    except Exception as exc:  # pragma: no cover - top-level reporting path
        note = f"FIX-001 draft gate failed: {exc}"
        return [make_result(conf_id, "FAIL", note) for conf_id in FIX001_CONF_IDS]


def extract_fix001_versions(fixture: dict) -> dict:
    request = fixture["input_data"]
    result = fixture["expected_output"]
    pack = fixture["expected_evidence"]
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_version": fixture["fixture_version"],
        "protocol_version": fixture["protocol_version"],
        "input_schema": request["input_schema"],
        "evidence_profile": pack["evidence_profile"],
        "object_schema_versions": {
            "EvaluationRequest": request["schema_version"],
            "EvaluationResult": result["schema_version"],
            "PolicyReference": result["policy_reference"]["schema_version"],
            "Attestation": pack["attestation"]["schema_version"],
            "EvidencePack": pack["schema_version"],
        },
    }


def evaluate_compatibility_case(matrix: dict, artifact_versions: dict) -> tuple[bool, str]:
    matching_rule = None
    for rule in matrix["rules"]:
        if rule["protocol_version"] == artifact_versions["protocol_version"]:
            matching_rule = rule
            break
    if matching_rule is None:
        return False, f"protocol_version {artifact_versions['protocol_version']} is not in the matrix"

    fixture_versions = matching_rule["allowed_fixture_bindings"].get(
        artifact_versions["fixture_id"], []
    )
    if artifact_versions["fixture_version"] not in fixture_versions:
        return (
            False,
            f"{artifact_versions['fixture_id']}@{artifact_versions['fixture_version']} is not approved for protocol_version {artifact_versions['protocol_version']}",
        )

    if artifact_versions["input_schema"] not in matching_rule["allowed_input_schemas"]:
        return (
            False,
            f"input_schema {artifact_versions['input_schema']} is not approved for protocol_version {artifact_versions['protocol_version']}",
        )

    if artifact_versions["evidence_profile"] not in matching_rule["allowed_evidence_profiles"]:
        return (
            False,
            f"evidence_profile {artifact_versions['evidence_profile']} is not approved for protocol_version {artifact_versions['protocol_version']}",
        )

    for object_type, version in artifact_versions["object_schema_versions"].items():
        allowed = matching_rule["allowed_object_schema_versions"].get(object_type, [])
        if version not in allowed:
            return (
                False,
                f"{object_type} schema_version {version} is not approved for protocol_version {artifact_versions['protocol_version']}",
            )

    return True, "version combination is explicitly permitted by the matrix"


def run_conf008_result() -> dict:
    matrix = load_json(COMPAT_MATRIX_PATH)
    fixture = load_json(COMPAT_FIXTURE_PATH)
    fix001 = load_json(FIX001_FIXTURE_PATH)

    if fixture["compatibility_matrix_id"] != matrix["matrix_id"]:
        raise AssertionError("FIX-COMPAT-001 must bind the active DQ-003 compatibility matrix")

    if fixture["source_fixture"] != "fixtures/core/FIX-001_BASIC_EVALUATION.json":
        raise AssertionError("FIX-COMPAT-001 must point at FIX-001 as its source fixture")

    observed_fix001_versions = extract_fix001_versions(fix001)
    case_notes = []

    for case in fixture["cases"]:
        artifact_versions = case["artifact_versions"]
        if case["case_id"] == "CURRENT_DRAFT_FIX001":
            if artifact_versions != observed_fix001_versions:
                raise AssertionError(
                    "FIX-COMPAT-001 current-draft case no longer matches the live FIX-001 version envelope"
                )
        allowed, reason = evaluate_compatibility_case(matrix, artifact_versions)
        expected_pass = case["expected"] == "PASS"
        if allowed != expected_pass:
            raise AssertionError(
                f"{case['case_id']} expected {case['expected']} but observed {'PASS' if allowed else 'FAIL'} ({reason})"
            )
        case_notes.append(f"{case['case_id']}={case['expected']}")

    return make_result(
        "CONF-008",
        "PASS",
        f"{matrix['matrix_id']} accepts the current FIX-001 version envelope and rejects unapproved matrix combinations ({', '.join(case_notes)})",
    )


def build_report() -> dict:
    results = run_fix001_results()
    results.append(run_conf008_result())
    results.extend(make_result(*entry) for entry in NON_EXECUTED_RESULTS)
    results.sort(key=lambda item: item["id"])

    summary = {"PASS": 0, "FAIL": 0, "ERROR": 0, "OPEN": 0, "BLOCKED": 0, "READY": 0}
    for result in results:
        summary[result["status"]] = summary.get(result["status"], 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runner": "scripts/run-draft-conformance.py",
        "results": results,
        "summary": summary,
    }


def emit_report(report: dict, json_out: Path | None) -> None:
    for result in report["results"]:
        print(f"{result['id']} {result['status']} — {result['note']}")
    print(
        "SUMMARY "
        + ", ".join(
            f"{key}={value}" for key, value in report["summary"].items() if value
        )
    )

    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote JSON report to {json_out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, help="Optional path for JSON output")
    args = parser.parse_args(argv)

    try:
        report = build_report()
    except Exception as exc:  # pragma: no cover - top-level reporting path
        print(f"draft conformance runner failed: {exc}", file=sys.stderr)
        return 1

    emit_report(report, args.json_out)
    return 1 if report["summary"].get("FAIL", 0) or report["summary"].get("ERROR", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
