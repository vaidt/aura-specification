#!/usr/bin/env python3
"""Validate the non-normative L3 candidate contract-mapping matrix."""
from __future__ import annotations
import json
import sys
from pathlib import Path

MAPPING = Path("docs/completion/AURA_C6_L3_CONTRACT_MAPPING_39_REMAINING_v0.1-DRAFT.json")
INVENTORY = Path("fixtures/corpus/STAGE-C-C6-EXTENDED-CANDIDATE-INVENTORY-v0.1-DRAFT.json")
PILOT = {f"C6-X-{n:03d}" for n in range(13, 21)}
EXCLUDED = {"C6-X-004", "C6-X-009", "C6-X-041"}
EFFECTS = ("authority", "governance_effect", "authorization_effect", "release_effect")

def fail(message: str) -> None:
    raise ValueError(message)

def main() -> int:
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if mapping.get("schema") != "AURA-BC021-C6-L3-CONTRACT-MAPPING/0.1":
        fail("unexpected L3 mapping schema")
    if mapping.get("status") != "DRAFT_CONTRACT_REVIEW_REQUIRED" or mapping.get("normative_effect") != "NONE":
        fail("L3 mapping must remain draft/non-normative")
    if inventory.get("status") != "DRAFT_NON_NORMATIVE":
        fail("source inventory is not draft/non-normative")
    for field in EFFECTS:
        if mapping.get(field) != "NONE":
            fail(f"{field} must be NONE")
    active = [case["id"] for case in inventory["cases"] if case.get("included_in_candidate_pool") is True]
    expected = [case_id for case_id in active if case_id not in PILOT]
    rows = mapping.get("candidates")
    if not isinstance(rows, list) or [row.get("id") for row in rows] != expected or len(rows) != 39:
        fail("mapped IDs/order must equal the 39 active non-pilot candidates")
    if len(set(expected)) != 39 or any(case_id in EXCLUDED or case_id in PILOT for case_id in expected):
        fail("excluded/pilot IDs must not appear in L3 map")
    pins = {item.get("artifact"): item for item in mapping.get("source_pins", [])}
    expected_pins = {
        "C6 candidate inventory": ("3a8e7ac3e26faa92fe383d090fe366b72ff438ff", "06a4e8827fb589e3a549944c71718291d1345f16"),
        "BC-02.1 common receipt schema": ("6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330", "f40f7a2ea246f382d12490a6489159f9e226fd17"),
        "Error taxonomy decision record": ("6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330", "7573f83762b8d02f98f0665542a67722fcf0b616"),
        "APS-200 Canonical Data Model": ("6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330", "198eee23f12e1db7b3417d3b359c4f912142e984"),
        "C6 Contract Negatives": ("6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330", "a440742ebcd7f6b3b6cb396e30dfc8f95362d4f0"),
    }
    if set(pins) != set(expected_pins):
        fail("source pin set incomplete or unexpected")
    for name, (commit, blob) in expected_pins.items():
        if pins[name].get("commit") != commit or pins[name].get("git_blob_oid") != blob:
            fail(f"{name}: source identity mismatch")
    for row in rows:
        cid = row["id"]
        if row.get("contract_binding_status") != "UNRESOLVED":
            fail(f"{cid}: contract binding must remain unresolved")
        if row.get("expected_outcome_policy") != "CONTRACT_DECISION_REQUIRED":
            fail(f"{cid}: outcome policy must remain unresolved")
        if row.get("expected_code") is not None or row.get("expected_result") is not None:
            fail(f"{cid}: expected outcomes cannot be locked by this draft")
        if row.get("execution_authorization") != "NOT_GRANTED":
            fail(f"{cid}: execution authorization must remain NOT_GRANTED")
        if row.get("proposed_diagnostic_family") != "NONE_LOCKED":
            fail(f"{cid}: diagnostic family must not be locked")
        for field in EFFECTS:
            if row.get(field) != "NONE":
                fail(f"{cid}: {field} must be NONE")
        if not all(row.get(field) for field in ("contract_reference", "mapping_disposition", "rule_or_gap")):
            fail(f"{cid}: contract traceability missing")
    summary = mapping.get("summary", {})
    expected_counts = {"active_candidate_count":47,"completed_observation_pilot_count":8,"mapped_remaining_count":39,"exact_expected_codes_locked":0,"unresolved_outcome_count":39}
    for name, value in expected_counts.items():
        if summary.get(name) != value:
            fail(f"summary.{name} must be {value}")
    if summary.get("excluded_tombstones") != sorted(EXCLUDED):
        fail("excluded tombstones mismatch")
    if len(mapping.get("governance_findings", [])) < 3:
        fail("governance-source ambiguity must remain documented")
    print("C6_L3_CONTRACT_MAPPING=PASS_STRUCTURAL")
    print("MAPPED_REMAINING_CANDIDATES=39")
    print("EXPECTED_CODES_LOCKED=0")
    print("OUTCOME_POLICY=CONTRACT_DECISION_REQUIRED")
    print("AUTHORITY=NONE")
    print("NORMATIVE_EFFECT=NONE")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"C6_L3_CONTRACT_MAPPING=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
