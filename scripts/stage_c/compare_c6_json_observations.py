#!/usr/bin/env python3
"""Differentially compare observation-only RI-PY and RI-RS candidate reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PILOT_IDS = [f"C6-X-{number:03d}" for number in range(13, 21)]
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_report(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    report = json.loads(raw.decode("utf-8", errors="strict"))
    if not isinstance(report, dict):
        raise ValueError(f"{label}: expected JSON object report")
    if report.get("schema") != "AURA-C6-CANDIDATE-OBSERVATION/0.1":
        raise ValueError(f"{label}: unexpected observation schema")
    if report.get("status") != "OBSERVATION_COMPLETE" or report.get("mode") != "OBSERVATION_ONLY":
        raise ValueError(f"{label}: observation report is incomplete or not observation-only")
    for field in EFFECT_FIELDS:
        if report.get(field) != "NONE":
            raise ValueError(f"{label}: {field} must be NONE")
    if report.get("expected_outcomes_assigned") is not False:
        raise ValueError(f"{label}: expected outcomes must not be assigned")
    if report.get("contract_binding_status") != "UNRESOLVED":
        raise ValueError(f"{label}: contract binding must remain unresolved")
    return report, raw


def rows_by_id(report: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    rows = report.get("cases")
    if not isinstance(rows, list) or len(rows) != len(PILOT_IDS):
        raise ValueError(f"{label}: report must contain exactly eight pilot cases")
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or ids != PILOT_IDS:
        raise ValueError(f"{label}: pilot case IDs/order mismatch")
    return {row["id"]: row for row in rows}


def compare(index_path: Path, py_path: Path, rs_path: Path, output_path: Path) -> dict[str, Any]:
    index_raw = index_path.read_bytes()
    index = json.loads(index_raw.decode("utf-8", errors="strict"))
    if index.get("schema") != "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1":
        raise ValueError("candidate materialization index schema mismatch")
    if index.get("authority") != "NONE" or index.get("governance_effect") != "NONE":
        raise ValueError("candidate index has a prohibited governance effect")
    py, _ = load_report(py_path, "RI-PY")
    rs, _ = load_report(rs_path, "RI-RS")
    index_sha = sha256(index_raw)
    if py.get("materialization_index_sha256") != index_sha or rs.get("materialization_index_sha256") != index_sha:
        raise ValueError("observation reports do not bind to the exact same materialization index")
    py_rows, rs_rows = rows_by_id(py, "RI-PY"), rows_by_id(rs, "RI-RS")
    discrepancies: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    has_execution_error = False
    for candidate_id in PILOT_IDS:
        left, right = py_rows[candidate_id], rs_rows[candidate_id]
        if left.get("observed_result") == "EXECUTION_ERROR" or right.get("observed_result") == "EXECUTION_ERROR":
            has_execution_error = True
        reasons: list[str] = []
        for field in ("input_sha256", "input_bytes"):
            if left.get(field) != right.get(field):
                reasons.append(f"{field}_mismatch")
        for field in ("observed_result", "observed_code"):
            if left.get(field) != right.get(field):
                reasons.append(f"{field}_mismatch")
        row_status = "AGREEMENT" if not reasons else "MISMATCH"
        record = {
            "id": candidate_id,
            "ri_py": {"result": left.get("observed_result"), "code": left.get("observed_code"), "input_sha256": left.get("input_sha256"), "input_bytes": left.get("input_bytes")},
            "ri_rs": {"result": right.get("observed_result"), "code": right.get("observed_code"), "input_sha256": right.get("input_sha256"), "input_bytes": right.get("input_bytes")},
            "differential_status": row_status,
            "contract_binding_status": "UNRESOLVED",
            "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
            "reasons": reasons,
        }
        results.append(record)
        if reasons:
            discrepancies.append(record)
    if discrepancies:
        status = "MISMATCH"
    elif has_execution_error:
        status = "EXECUTION_INCOMPLETE"
    else:
        status = "CONTRACT_UNRESOLVED"

    report = {
        "schema": "AURA-C6-CANDIDATE-DIFFERENTIAL-REPORT/0.1",
        "status": status,
        "mode": "OBSERVATION_ONLY",
        "materialization_index_sha256": index_sha,
        "ri_py_report_sha256": sha256(py_path.read_bytes()),
        "ri_rs_report_sha256": sha256(rs_path.read_bytes()),
        "pilot_case_count": len(results),
        "agreement_count": sum(row["differential_status"] == "AGREEMENT" for row in results),
        "mismatch_count": len(discrepancies),
        "cases": results,
        "interpretation": "Implementation agreement is an observation only; it does not establish contract correctness or conformance.",
        "contract_binding_status": "UNRESOLVED",
        "expected_outcomes_assigned": False,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"C6_JSON_DIFFERENTIAL_STATUS={status}")
    print(f"C6_JSON_PILOT_CASES={len(results)}")
    print(f"C6_JSON_AGREEMENTS={report['agreement_count']}")
    print(f"C6_JSON_MISMATCHES={report['mismatch_count']}")
    print("AUTHORITY=NONE")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--ri-py", type=Path, required=True)
    parser.add_argument("--ri-rs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.index, args.ri_py, args.ri_rs, args.output)
    if report["status"] in {"MISMATCH", "EXECUTION_INCOMPLETE"}:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"C6_JSON_DIFFERENTIAL=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
