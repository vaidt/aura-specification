#!/usr/bin/env python3
"""Verify byte-identical RI-PY/RI-RS C6 wire-corpus results; never promotes the C6 gate."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), raw


def fail(message: str) -> None:
    raise SystemExit(f"C6 parity verifier: FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True,
                        help="The 27-case strict wire mutation manifest.")
    parser.add_argument("--source-pins", type=Path, required=True,
                        help="The C6 preparation inventory containing exact source blob pins.")
    parser.add_argument("--corpus-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest, manifest_raw = read_json(args.manifest)
    pins_doc, _ = read_json(args.source_pins)
    index, index_raw = read_json(args.corpus_dir / "index.json")
    py, py_raw = read_json(args.results_dir / "ri-py-results.json")
    rs, rs_raw = read_json(args.results_dir / "ri-rs-results.json")

    problems: list[str] = []
    if manifest.get("schema") != "AURA-BC021-STRICT-WIRE-MUTATION-CORPUS/0.1":
        problems.append("unexpected wire corpus manifest schema")
    if manifest.get("status") != "DRAFT_NON_NORMATIVE" or manifest.get("stage") != "C6_PREPARATION":
        problems.append("wire corpus manifest is not explicitly draft C6 preparation")
    for field in ("authority", "governance_effect", "authorization_effect", "release_effect"):
        if manifest.get(field) != "NONE":
            problems.append(f"manifest {field} is not NONE")
    if index.get("schema") != "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1":
        problems.append("unexpected materialized index schema")
    if index.get("status") != "MATERIALIZED_FOR_TESTING_ONLY":
        problems.append("materialized index is not marked testing-only")
    if index.get("source_manifest_sha256") != sha256(manifest_raw):
        problems.append("index manifest SHA-256 differs from exact source manifest")
    if index.get("authority") != "NONE" or index.get("governance_effect") != "NONE":
        problems.append("materialized index carries non-NONE authority/governance effects")

    source_pins = pins_doc.get("source_pins", {})
    expected_source = {
        "RI-PY commit": (py.get("source_commit"), source_pins.get("ri_py_commit")),
        "RI-PY receiver blob": (py.get("source_blob_sha256"), source_pins.get("ri_py_receiver_blob")),
        "RI-PY test blob": (py.get("test_blob_sha256"), source_pins.get("ri_py_strict_consumer_test_blob")),
        "RI-RS receiver blob": (rs.get("source_blob_sha256"), source_pins.get("ri_rs_specification_receiver_blob")),
        "RI-RS test blob": (rs.get("test_blob_sha256"), source_pins.get("ri_rs_preflight_test_blob")),
    }
    for name, (actual, expected) in expected_source.items():
        if not expected or actual != expected:
            problems.append(f"{name} pin mismatch: report={actual!r} manifest={expected!r}")

    reports = (("RI-PY", py), ("RI-RS", rs))
    for name, report in reports:
        if report.get("schema") != "AURA-BC021-WIRE-CONSUMER-RESULTS/0.1":
            problems.append(f"{name} result schema mismatch")
        if report.get("status") != "PASS":
            problems.append(f"{name} result status is not PASS")
        if report.get("authority") != "NONE" or report.get("governance_effect") != "NONE":
            problems.append(f"{name} result carries non-NONE authority/governance effects")
        if report.get("index_sha256") != sha256(index_raw):
            problems.append(f"{name} did not consume the exact same index.json")

    cases = index.get("cases")
    if not isinstance(cases, list) or len(cases) != index.get("case_count"):
        problems.append("materialized index case count is inconsistent")
        cases = []
    if len(cases) != len(manifest.get("mutations", [])):
        problems.append("materialized corpus case count differs from manifest mutation count")

    materialized_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or case_id in materialized_by_id:
            problems.append(f"missing or duplicate materialized case id: {case_id!r}")
            continue
        materialized_by_id[case_id] = case
        input_path = args.corpus_dir / case.get("input_file", "")
        if not input_path.is_file():
            problems.append(f"{case_id}: materialized input file missing")
            continue
        raw = input_path.read_bytes()
        if len(raw) != case.get("input_bytes"):
            problems.append(f"{case_id}: input byte length mismatch")
        if sha256(raw) != case.get("input_sha256"):
            problems.append(f"{case_id}: input SHA-256 mismatch")

    result_maps: dict[str, dict[str, dict[str, Any]]] = {}
    for name, report in reports:
        rows = report.get("cases")
        if not isinstance(rows, list) or len(rows) != report.get("case_count"):
            problems.append(f"{name}: result case count is inconsistent")
            rows = []
        result_map: dict[str, dict[str, Any]] = {}
        for row in rows:
            case_id = row.get("id")
            if not isinstance(case_id, str) or case_id in result_map:
                problems.append(f"{name}: missing or duplicate result id {case_id!r}")
                continue
            result_map[case_id] = row
        if set(result_map) != set(materialized_by_id):
            problems.append(f"{name}: result case identifiers differ from materialized input identifiers")
        for case_id, base in materialized_by_id.items():
            row = result_map.get(case_id)
            if row is None:
                continue
            for field in ("input_sha256", "input_bytes", "expected_result", "expected_code"):
                if row.get(field) != base.get(field):
                    problems.append(f"{name} {case_id}: result {field} differs from materialized index")
            if row.get("actual_result") != row.get("expected_result"):
                problems.append(f"{name} {case_id}: actual result differs from expected result")
            if row.get("actual_code") != row.get("expected_code"):
                problems.append(f"{name} {case_id}: actual error code differs from expected code")
            if name == "RI-RS" and row.get("matched") is not True:
                problems.append(f"{name} {case_id}: Rust marked case as not matched")
        result_maps[name] = result_map

    py_map = result_maps.get("RI-PY", {})
    rs_map = result_maps.get("RI-RS", {})
    parity_rows = []
    for case_id in sorted(materialized_by_id):
        py_row, rs_row = py_map.get(case_id), rs_map.get(case_id)
        matched = bool(py_row and rs_row)
        if py_row and rs_row:
            for field in ("input_sha256", "input_bytes", "actual_result", "actual_code"):
                if py_row.get(field) != rs_row.get(field):
                    problems.append(f"{case_id}: RI-PY/RI-RS mismatch in {field}")
                    matched = False
            base = materialized_by_id[case_id]
            if py_row.get("input_sha256") != base.get("input_sha256") or rs_row.get("input_sha256") != base.get("input_sha256"):
                matched = False
        parity_rows.append({
            "id": case_id,
            "input_sha256": materialized_by_id[case_id].get("input_sha256"),
            "ri_py_result": py_row.get("actual_result") if py_row else None,
            "ri_py_code": py_row.get("actual_code") if py_row else None,
            "ri_rs_result": rs_row.get("actual_result") if rs_row else None,
            "ri_rs_code": rs_row.get("actual_code") if rs_row else None,
            "matched": matched,
        })

    status = "BOUNDED_PARITY_PASS" if not problems and all(row["matched"] for row in parity_rows) else "MISMATCH"
    report = {
        "schema": "AURA-BC021-WIRE-CONSUMER-PARITY-REPORT/0.1",
        "status": status,
        "scope": "The 27-case draft BC-02.1 receipt JSON mutation corpus only; not full protocol conformance.",
        "case_count": len(parity_rows),
        "accepted_case_count": sum(1 for row in parity_rows if row["ri_py_result"] == "ACCEPT"),
        "rejected_case_count": sum(1 for row in parity_rows if row["ri_py_result"] == "REJECT"),
        "matched_case_count": sum(1 for row in parity_rows if row["matched"]),
        "mismatch_count": sum(1 for row in parity_rows if not row["matched"]),
        "problems": problems,
        "source_pins": {name: expected for name, (_, expected) in expected_source.items()},
        "hashes": {
            "mutation_manifest_sha256": sha256(manifest_raw),
            "materialized_index_sha256": sha256(index_raw),
            "ri_py_results_sha256": sha256(py_raw),
            "ri_rs_results_sha256": sha256(rs_raw),
        },
        "cases": parity_rows,
        "bounded_parity_claim": "PASS" if status == "BOUNDED_PARITY_PASS" else "NOT_ESTABLISHED",
        "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    out = args.results_dir / "parity-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"bounded_wire_parity_status={status}")
    print(f"case_count={report['case_count']}")
    print(f"accepted_case_count={report['accepted_case_count']}")
    print(f"rejected_case_count={report['rejected_case_count']}")
    print(f"matched_case_count={report['matched_case_count']}")
    print(f"mismatch_count={report['mismatch_count']}")
    print(f"parity_report_sha256={sha256(out.read_bytes())}")
    print("c6_gate_status=BLOCKED_PENDING_EVIDENCE_REVIEW")
    print("authority=NONE")
    if problems:
        for problem in problems:
            print(f"PARITY_PROBLEM: {problem}")
    if status != "BOUNDED_PARITY_PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
