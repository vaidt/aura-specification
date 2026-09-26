#!/usr/bin/env python3
"""Controlled draft verifier for FIX-001 evidence-pack checks.

This script executes the current repository-local draft verification path for:
- CONF-004 Evidence Integrity
- CONF-005 Traceability
- CONF-010 Cryptographic Verification

It validates the FIX-001 working fixture, recomputes the bound digest values, and
executes one negative mutation control to prove that Evidence tampering is detected.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, RefResolver
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing dependency: jsonschema. Install with `python -m pip install jsonschema`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures" / "core" / "FIX-001_BASIC_EVALUATION.json"
SCHEMA_DIR = ROOT / "fixtures" / "schemas"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        raise TypeError("Floating-point values are not supported in the FIX-001 draft path")
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key in sorted(value):
            items.append(
                json.dumps(key, ensure_ascii=False, separators=(",", ":"))
                + ":"
                + canonical_json(value[key])
            )
        return "{" + ",".join(items) + "}"
    raise TypeError(f"Unsupported JSON value type: {type(value)!r}")


def canonical_sha256(obj: object) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def validate_schema(schema_name: str, instance: object) -> None:
    schema = load_json(SCHEMA_DIR / schema_name)
    resolver = RefResolver(base_uri=(SCHEMA_DIR.resolve().as_uri() + "/"), referrer=schema)
    Draft202012Validator(schema, resolver=resolver).validate(instance)


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def verify_pack_hashes(fixture: dict) -> None:
    request = fixture["input_data"]
    result = fixture["expected_output"]
    pack = fixture["expected_evidence"]
    evidence_object = pack["evidence_object"]
    policy_reference = pack["policy_reference"]
    attestation = pack["attestation"]

    assert_equal(
        request["input_hash"],
        canonical_sha256(request["request_fields"]),
        "input_hash",
    )
    assert_equal(
        result["output_hash"],
        canonical_sha256(
            {"decision": result["decision"], "result_fields": result["result_fields"]}
        ),
        "output_hash",
    )
    assert_equal(
        request["integrity_hash"],
        canonical_sha256({k: v for k, v in request.items() if k != "integrity_hash"}),
        "request.integrity_hash",
    )
    assert_equal(
        policy_reference["integrity_hash"],
        canonical_sha256(
            {k: v for k, v in policy_reference.items() if k != "integrity_hash"}
        ),
        "policy_reference.integrity_hash",
    )
    assert_equal(
        result["integrity_hash"],
        canonical_sha256({k: v for k, v in result.items() if k != "integrity_hash"}),
        "evaluation_result.integrity_hash",
    )

    attestation_content = {
        "attestation_type": attestation["attestation_type"],
        "attested_execution_id": attestation["attested_execution_id"],
        "evidence_reference": attestation["evidence_reference"],
    }
    assert_equal(
        attestation["attestation_hash"],
        canonical_sha256(attestation_content),
        "attestation_hash",
    )
    assert_equal(
        attestation["integrity_hash"],
        canonical_sha256({k: v for k, v in attestation.items() if k != "integrity_hash"}),
        "attestation.integrity_hash",
    )
    assert_equal(
        evidence_object["evidence_hash"],
        canonical_sha256(
            {k: v for k, v in evidence_object.items() if k != "evidence_hash"}
        ),
        "evidence_hash",
    )
    assert_equal(
        pack["integrity_metadata"]["request_integrity_hash"],
        request["integrity_hash"],
        "integrity_metadata.request_integrity_hash",
    )
    assert_equal(
        pack["integrity_metadata"]["result_integrity_hash"],
        result["integrity_hash"],
        "integrity_metadata.result_integrity_hash",
    )
    assert_equal(
        pack["integrity_metadata"]["policy_integrity_hash"],
        policy_reference["integrity_hash"],
        "integrity_metadata.policy_integrity_hash",
    )
    assert_equal(
        pack["integrity_metadata"]["attestation_integrity_hash"],
        attestation["integrity_hash"],
        "integrity_metadata.attestation_integrity_hash",
    )
    assert_equal(
        pack["pack_hash"],
        canonical_sha256({k: v for k, v in pack.items() if k != "pack_hash"}),
        "pack_hash",
    )


def verify_traceability(fixture: dict) -> None:
    request = fixture["input_data"]
    result = fixture["expected_output"]
    pack = fixture["expected_evidence"]
    evidence_object = pack["evidence_object"]
    policy_reference = pack["policy_reference"]
    attestation = pack["attestation"]

    assert_equal(result, pack["evaluation_result"], "pack.evaluation_result")
    assert_equal(result["policy_reference"], policy_reference, "policy_reference embedding")
    assert_equal(evidence_object["execution_id"], result["execution_id"], "execution_id linkage")
    assert_equal(
        attestation["attested_execution_id"],
        result["execution_id"],
        "attested_execution_id linkage",
    )
    assert_equal(
        evidence_object["policy_reference"],
        policy_reference["object_id"],
        "evidence_object.policy_reference linkage",
    )
    assert_equal(
        evidence_object["attestation_reference"],
        attestation["object_id"],
        "attestation_reference linkage",
    )
    assert_equal(
        attestation["evidence_reference"],
        pack["pack_id"],
        "attestation.evidence_reference linkage",
    )
    if not set(evidence_object["requirement_references"]).issubset(
        set(pack["requirement_references"])
    ):
        raise AssertionError("pack.requirement_references must include evidence_object references")
    assert_equal(
        evidence_object["input_hash"],
        request["input_hash"],
        "evidence_object.input_hash linkage",
    )
    assert_equal(
        evidence_object["output_hash"],
        result["output_hash"],
        "evidence_object.output_hash linkage",
    )


def verify_mutation_detection(fixture: dict) -> None:
    mutated = copy.deepcopy(fixture)
    mutated["expected_evidence"]["evidence_object"]["output_hash"] = (
        "f" + mutated["expected_evidence"]["evidence_object"]["output_hash"][1:]
    )
    try:
        verify_pack_hashes(mutated)
    except AssertionError:
        return
    raise AssertionError("Mutation control did not detect Evidence tampering")


def main() -> int:
    fixture = load_json(FIXTURE_PATH)

    validate_schema("evaluation-request.schema.json", fixture["input_data"])
    validate_schema("evaluation-result.schema.json", fixture["expected_output"])
    validate_schema("evidence-pack.schema.json", fixture["expected_evidence"])

    verify_pack_hashes(fixture)
    verify_traceability(fixture)
    verify_mutation_detection(fixture)

    print("CONF-004 PASS — evidence mutation is detected by digest verification")
    print("CONF-005 PASS — execution, policy, attestation, and requirement links are coherent")
    print("CONF-010 PASS — input, output, evidence, and pack digests recompute correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
