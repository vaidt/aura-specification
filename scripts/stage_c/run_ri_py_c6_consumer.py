#!/usr/bin/env python3
"""Execute RI-PY against the pinned shared Stage C6 BC-02.1 wire corpus.

This is a bounded, non-normative evidence runner. It does not produce a protocol
conformance decision or authorize implementation/release/governance changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_INDEX_SCHEMA = "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1"
EXPECTED_RESULTS_SCHEMA = "AURA-BC021-WIRE-CONSUMER-RESULTS/0.1"
EXPECTED_RECEIPT_SCHEMA = "BC-02.1-COMMON-RECEIPT"
EXPECTED_CASE_COUNT = 27


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_text(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def git_blob(root: Path, relative_path: str) -> str:
    return git_text(root, "rev-parse", f"HEAD:{relative_path}")


def write_json(path: Path, payload: dict[str, Any]) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def safe_input_path(corpus_dir: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe corpus input path: {relative!r}")
    resolved_root = corpus_dir.resolve()
    resolved = (corpus_dir / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"corpus input escapes corpus directory: {relative!r}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", required=True, type=Path)
    parser.add_argument("--corpus-dir", required=True, type=Path)
    parser.add_argument("--corpus-source-root", required=True, type=Path)
    parser.add_argument("--architecture", required=True, choices=("x86_64", "aarch64"))
    parser.add_argument("--expected-core-commit", required=True)
    parser.add_argument("--expected-corpus-commit", required=True)
    args = parser.parse_args()

    core_root = args.core_root.resolve()
    corpus_dir = args.corpus_dir.resolve()
    corpus_source_root = args.corpus_source_root.resolve()
    index_path = corpus_dir / "index.json"
    results_dir = corpus_dir / "results"
    results_path = results_dir / "ri-py-results.json"
    evidence_path = corpus_dir / "ri-py-implementation-evidence.json"

    errors: list[str] = []

    actual_core_commit = git_text(core_root, "rev-parse", "HEAD")
    actual_corpus_commit = git_text(corpus_source_root, "rev-parse", "HEAD")
    if actual_core_commit != args.expected_core_commit:
        errors.append(f"core_source_commit_mismatch:{actual_core_commit}")
    if actual_corpus_commit != args.expected_corpus_commit:
        errors.append(f"corpus_source_commit_mismatch:{actual_corpus_commit}")

    receiver_path = "conformance/boundary/ri_py_receiver.py"
    test_path = "conformance/boundary/test_ri_py_receipt_json_consumer.py"
    manifest_path = "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"
    materializer_path = "scripts/stage_c/materialize_c6_wire_corpus.py"

    receiver_raw = (core_root / receiver_path).read_bytes()
    test_raw = (core_root / test_path).read_bytes()
    manifest_raw = (corpus_source_root / manifest_path).read_bytes()
    materializer_raw = (corpus_source_root / materializer_path).read_bytes()

    source_identity = {
        "repository": "vaidt/aura-poc-a-core-v3.3",
        "source_commit": actual_core_commit,
        "receiver_path": receiver_path,
        "receiver_git_blob_oid": git_blob(core_root, receiver_path),
        "receiver_content_sha256": sha256(receiver_raw),
        "test_path": test_path,
        "test_git_blob_oid": git_blob(core_root, test_path),
        "test_content_sha256": sha256(test_raw),
    }
    corpus_identity = {
        "repository": "vaidt/aura-specification",
        "source_commit": actual_corpus_commit,
        "manifest_path": manifest_path,
        "manifest_git_blob_oid": git_blob(corpus_source_root, manifest_path),
        "manifest_content_sha256": sha256(manifest_raw),
        "materializer_path": materializer_path,
        "materializer_git_blob_oid": git_blob(corpus_source_root, materializer_path),
        "materializer_content_sha256": sha256(materializer_raw),
    }

    if not index_path.is_file():
        raise SystemExit(f"missing materialized C6 index: {index_path}")
    index_raw = index_path.read_bytes()
    index_sha = sha256(index_raw)
    index = json.loads(index_raw.decode("utf-8", errors="strict"))

    if index.get("schema") != EXPECTED_INDEX_SCHEMA:
        errors.append("unexpected_materialized_index_schema")
    if index.get("status") != "MATERIALIZED_FOR_TESTING_ONLY":
        errors.append("unexpected_materialization_status")
    for field in ("authority", "governance_effect", "authorization_effect", "release_effect"):
        if index.get(field) != "NONE":
            errors.append(f"index_{field}_must_be_NONE")

    cases = index.get("cases")
    if not isinstance(cases, list):
        raise SystemExit("C6 index does not contain a cases array")
    if index.get("case_count") != len(cases):
        errors.append("index_declared_case_count_mismatch")
    if len(cases) != EXPECTED_CASE_COUNT:
        errors.append(f"expected_{EXPECTED_CASE_COUNT}_cases_got_{len(cases)}")
    case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(case_ids) != len(cases) or len(set(case_ids)) != len(case_ids):
        errors.append("index_case_ids_missing_or_duplicated")

    # Import the candidate Core parser only after binding its exact checkout.
    sys.path.insert(0, str(core_root))
    from conformance.boundary.ri_py_receiver import ReceiptParseError, parse_receipt_json  # noqa: E402

    rows: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict):
            errors.append("index_case_is_not_object")
            continue

        case_id = case.get("id")
        try:
            raw = safe_input_path(corpus_dir, str(case["input_file"])).read_bytes()
        except Exception as exc:
            errors.append(f"{case_id}:input_read_error:{type(exc).__name__}")
            rows.append({
                "id": case_id,
                "input_sha256": None,
                "input_bytes": None,
                "expected_result": case.get("expected_result"),
                "expected_code": case.get("expected_code"),
                "actual_result": "ERROR",
                "actual_code": f"INPUT_{type(exc).__name__}",
                "matched": False,
            })
            continue

        input_sha = sha256(raw)
        if len(raw) != case.get("input_bytes"):
            errors.append(f"{case_id}:input_byte_length_mismatch")
        if input_sha != case.get("input_sha256"):
            errors.append(f"{case_id}:input_sha256_mismatch")

        try:
            receipt = parse_receipt_json(raw)
            actual_result = "ACCEPT"
            actual_code = None
            if getattr(receipt, "schema_id", None) != EXPECTED_RECEIPT_SCHEMA:
                errors.append(f"{case_id}:parsed_schema_id_mismatch")
            received = getattr(receipt, "received", None)
            if received is None:
                errors.append(f"{case_id}:parsed_receipt_missing_received_material")
            else:
                octets = received.raw_octets
                if received.octet_length != len(octets):
                    errors.append(f"{case_id}:parsed_octet_length_mismatch")
                if received.recomputed_sha256 != sha256(octets):
                    errors.append(f"{case_id}:parsed_raw_octet_digest_mismatch")
        except ReceiptParseError as exc:
            actual_result = "REJECT"
            actual_code = str(exc.code)
        except Exception as exc:  # unexpected exceptions are execution errors, never REJECT
            actual_result = "ERROR"
            actual_code = type(exc).__name__
            errors.append(f"{case_id}:unexpected_parser_exception:{type(exc).__name__}")

        expected_result = case.get("expected_result")
        expected_code = case.get("expected_code")
        matched = actual_result == expected_result and actual_code == expected_code
        if not matched:
            errors.append(
                f"{case_id}:expected=({expected_result},{expected_code})"
                f":actual=({actual_result},{actual_code})"
            )
        rows.append({
            "id": case_id,
            "input_sha256": input_sha,
            "input_bytes": len(raw),
            "expected_result": expected_result,
            "expected_code": expected_code,
            "actual_result": actual_result,
            "actual_code": actual_code,
            "matched": matched,
        })
        print(
            f"C6_RI_PY_CASE id={case_id} input_sha256={input_sha} "
            f"result={actual_result} code={actual_code if actual_code is not None else 'null'} "
            f"matched={str(matched).lower()}"
        )

    result_status = "PASS" if not errors else "MISMATCH"
    report: dict[str, Any] = {
        "schema": EXPECTED_RESULTS_SCHEMA,
        "implementation": "RI-PY-AURA-CORE",
        "source_commit": actual_core_commit,
        "source_blob_git_oid": source_identity["receiver_git_blob_oid"],
        "test_blob_git_oid": source_identity["test_git_blob_oid"],
        "index_sha256": index_sha,
        "case_count": len(rows),
        "cases": rows,
        "mismatches": errors,
        "status": result_status,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    report_raw = write_json(results_path, report)

    evidence = {
        "schema": "AURA-C6-IMPLEMENTATION-EVIDENCE/0.5",
        "component": "RI-PY-AURA-CORE-STRICT-BC021-CONSUMER",
        "repository": "vaidt/aura-poc-a-core-v3.3",
        "tested_source_commit": actual_core_commit,
        "source_git_blob_oid": source_identity["receiver_git_blob_oid"],
        "source_content_sha256": source_identity["receiver_content_sha256"],
        "test_git_blob_oid": source_identity["test_git_blob_oid"],
        "test_content_sha256": source_identity["test_content_sha256"],
        "corpus_source_commit": actual_corpus_commit,
        "manifest_git_blob_oid": corpus_identity["manifest_git_blob_oid"],
        "manifest_content_sha256": corpus_identity["manifest_content_sha256"],
        "materializer_git_blob_oid": corpus_identity["materializer_git_blob_oid"],
        "materializer_content_sha256": corpus_identity["materializer_content_sha256"],
        "architecture": args.architecture,
        "runtime": platform.python_version(),
        "machine": platform.machine(),
        "shared_index_sha256": index_sha,
        "consumer_report_sha256": sha256(report_raw),
        "consumer_report_bytes": len(report_raw),
        "case_count": len(rows),
        "consumer_report_status": result_status,
        "preservation_status": "PASS" if not errors else "FAIL",
        "preservation_errors": errors,
        "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    write_json(evidence_path, evidence)

    print(f"RI_PY_SOURCE_COMMIT={actual_core_commit}")
    print(f"C6_INDEX_SHA256={index_sha}")
    print(f"RI_PY_CASE_COUNT={len(rows)}")
    print(f"RI_PY_MATCHED_COUNT={sum(row.get('matched') is True for row in rows)}")
    print(f"RI_PY_STATUS={result_status}")
    print(f"RI_PY_ERRORS={json.dumps(errors, sort_keys=True)}")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
