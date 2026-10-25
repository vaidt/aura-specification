#!/usr/bin/env python3
"""Validate the non-normative C6 candidate inventory without executing parsers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

MANIFEST = Path("fixtures/corpus/STAGE-C-C6-EXTENDED-CANDIDATE-INVENTORY-v0.1-DRAFT.json")
EXPECTED_SCHEMA = "AURA-BC021-C6-EXTENDED-CANDIDATE-INVENTORY/0.1"
EXPECTED_DUPLICATES = {
    "C6-X-004": "C6-N-015A",
    "C6-X-009": "C6-N-012A",
}


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_SCHEMA:
        fail("unexpected candidate inventory schema")
    if payload.get("status") != "DRAFT_NON_NORMATIVE":
        fail("candidate inventory must remain DRAFT_NON_NORMATIVE")
    if payload.get("stage") != "C6_PREPARATION":
        fail("unexpected stage")
    for field in ("authority", "governance_effect", "authorization_effect", "release_effect"):
        if payload.get(field) != "NONE":
            fail(f"{field} must remain NONE")

    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 50:
        fail("candidate inventory must contain exactly 50 items")

    expected_ids = [f"C6-X-{n:03d}" for n in range(1, 51)]
    actual_ids = [case.get("id") for case in cases]
    if actual_ids != expected_ids:
        fail("candidate IDs must be unique and contiguous from C6-X-001 through C6-X-050")

    found_duplicates = {}
    for case in cases:
        case_id = case["id"]
        if case.get("contract_binding_status") != "UNRESOLVED":
            fail(f"{case_id}: contract binding must remain unresolved")
        if case.get("expected_outcome_policy") != "CONTRACT_DECISION_REQUIRED":
            fail(f"{case_id}: expected outcome policy must not be locked")
        if case.get("execution_status") != "NOT_RUN":
            fail(f"{case_id}: execution status must remain NOT_RUN")
        if "expected_code" in case or "expected_result" in case:
            fail(f"{case_id}: do not store normative expected_code/expected_result yet")
        if case_id in EXPECTED_DUPLICATES:
            if case.get("deduplication") != "CONFIRMED_EXACT_DUPLICATE":
                fail(f"{case_id}: duplicate disposition changed unexpectedly")
            if case.get("dedupe_reference") != EXPECTED_DUPLICATES[case_id]:
                fail(f"{case_id}: expected duplicate reference missing or wrong")
            if case.get("included_in_candidate_pool") is not False:
                fail(f"{case_id}: exact duplicate must be excluded from active pool")
            found_duplicates[case_id] = case["dedupe_reference"]
        else:
            if case.get("deduplication") != "PENDING_BYTE_LEVEL_DEDUP":
                fail(f"{case_id}: nonduplicate candidates need byte-level deduplication")
            if case.get("included_in_candidate_pool") is not True:
                fail(f"{case_id}: candidate should remain in triage pool")
        if not isinstance(case.get("mutation_recipe"), dict):
            fail(f"{case_id}: mutation_recipe must be an object")

    if found_duplicates != EXPECTED_DUPLICATES:
        fail("confirmed duplicate inventory does not match expected first-pass triage")
    counts = payload.get("counts", {})
    if counts.get("candidate_count") != 50:
        fail("candidate_count must be 50")
    if counts.get("confirmed_exact_duplicates") != 2:
        fail("confirmed_exact_duplicates must be 2")
    if counts.get("remaining_candidates_for_triage") != 48:
        fail("remaining_candidates_for_triage must be 48")
    if counts.get("runnable_cases") != 0:
        fail("runnable_cases must stay 0 until contract binding")

    print("C6_CANDIDATE_INVENTORY=PASS")
    print("CANDIDATE_COUNT=50")
    print("CONFIRMED_EXACT_DUPLICATES=2")
    print("REMAINING_CANDIDATES_FOR_TRIAGE=48")
    print("CONTRACT_BOUND_RUNNABLE_CASES=0")
    print("PARSER_EXECUTION=NOT_PERFORMED")
    print("AUTHORITY=NONE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"C6_CANDIDATE_INVENTORY=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
