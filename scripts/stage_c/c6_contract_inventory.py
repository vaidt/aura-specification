#!/usr/bin/env python3
"""Validate the C6 test inventory and emit PREPARATION_ONLY metadata."""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_CASE_FIELDS = {"id","kind","area","mutation","expected","ri_py","ri_rs","disposition"}
ALLOWED_DISPOSITIONS = {"READY_FOR_NATIVE_TESTS","PARTIAL_NATIVE_BOUNDARY","KNOWN_WIRE_CONSUMER_GAP","NOT_WIRED","IMPLEMENTED_EXPERIMENTAL_PENDING_SHARED_CORPUS"}
REQUIRED_AREAS = {
 "raw-octet-intake","handoff-status","fixture-identity","handoff-method","octet-type",
 "octet-length","digest-integrity","schema-version","provenance","adapter-provenance",
 "environment-provenance","forbidden-authority-field","unknown-field","base64-transport",
 "malformed-base64","strict-json-shape","duplicate-json-keys","utf8-boundary","raw-octet-boundary"
}

def load_and_validate(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    if manifest.get("schema") != "AURA-STAGE-C6-CONTRACT-NEGATIVE-MANIFEST/0.1":
        raise ValueError("unexpected C6 manifest schema")
    if manifest.get("status") != "DRAFT_NON_NORMATIVE":
        raise ValueError("C6 manifest must stay draft/non-normative")
    if manifest.get("stage") != "C6_PREPARATION":
        raise ValueError("manifest must identify preparation, not execution")
    if manifest.get("normative_effect") != "NONE":
        raise ValueError("manifest must have no normative effect")
    if manifest.get("execution_boundary", {}).get("governance_effect") != "NONE":
        raise ValueError("governance effect must remain NONE")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("C6 case list must be a non-empty array")
    ids = [item.get("id") for item in cases]
    if any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("each case must have a non-empty ID")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate C6 case IDs")
    for case in cases:
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            raise ValueError(f"{case.get('id')}: missing fields {sorted(missing)}")
        if case["disposition"] not in ALLOWED_DISPOSITIONS:
            raise ValueError(f"{case['id']}: unknown disposition {case['disposition']!r}")
        if not all(isinstance(case[field], str) and case[field] for field in REQUIRED_CASE_FIELDS):
            raise ValueError(f"{case['id']}: required case fields must be non-empty strings")
    areas = {item["area"] for item in cases}
    if areas != REQUIRED_AREAS:
        raise ValueError(f"coverage mismatch; missing={sorted(REQUIRED_AREAS-areas)} extra={sorted(areas-REQUIRED_AREAS)}")
    counts = Counter(case["disposition"] for case in cases)
    gaps = [case["id"] for case in cases if case["disposition"] in {"KNOWN_WIRE_CONSUMER_GAP","NOT_WIRED"}]
    partial = [case["id"] for case in cases if case["disposition"] == "PARTIAL_NATIVE_BOUNDARY"]
    pending = [case["id"] for case in cases if case["disposition"] == "IMPLEMENTED_EXPERIMENTAL_PENDING_SHARED_CORPUS"]
    return {
        "schema": "AURA-STAGE-C6-PREPARATION-REPORT/0.1",
        "status": "PREPARATION_ONLY",
        "c6_gate_status": "BLOCKED_NOT_EXECUTED",
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "manifest_case_count": len(cases),
        "case_ids": ids,
        "disposition_counts": dict(sorted(counts.items())),
        "known_or_unwired_gap_case_ids": gaps,
        "partial_native_boundary_case_ids": partial,
        "pending_shared_corpus_case_ids": pending,
        "pending_shared_corpus_count": len(pending),
        "required_areas_covered": sorted(areas),
        "native_cross_language_wire_consumer_parity": "NOT_ESTABLISHED",
        "c6_execution": "NOT_CLAIMED",
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE"
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = load_and_validate(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("preparation_status=PREPARATION_ONLY")
    print("c6_gate_status=BLOCKED_NOT_EXECUTED")
    print(f"manifest_sha256={report['manifest_sha256']}")
    print(f"manifest_case_count={report['manifest_case_count']}")
    print(f"known_or_unwired_gap_count={len(report['known_or_unwired_gap_case_ids'])}")
    print(f"pending_shared_corpus_count={report['pending_shared_corpus_count']}")
    print("authority=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
