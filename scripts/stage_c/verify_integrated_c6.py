#!/usr/bin/env python3
"""Fail-closed validation and cross-architecture comparison for integrated C6 evidence.

All outputs are strictly technical and non-constitutive. The evidence package
must preserve authority/governance/release fields as NONE.
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

INDEX_SCHEMA = "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1"
RESULTS_SCHEMA = "AURA-BC021-WIRE-CONSUMER-RESULTS/0.1"
EVIDENCE_SCHEMA = "AURA-C6-IMPLEMENTATION-EVIDENCE/0.5"
DIAGNOSTICS_SCHEMA = "AURA-C6-RI-RS-PRESERVATION-DIAGNOSTICS/0.3"
EXPECTED_CASE_COUNT = 27
ROW_FIELDS = (
    "id",
    "input_sha256",
    "input_bytes",
    "expected_result",
    "expected_code",
    "actual_result",
    "actual_code",
    "matched",
)
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8", errors="strict"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value, raw


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def identity(root: Path, relative: str) -> dict[str, str]:
    raw = (root / relative).read_bytes()
    return {
        "path": relative,
        "git_blob_oid": git(root, "rev-parse", f"HEAD:{relative}"),
        "content_sha256": digest(raw),
    }


def fail(errors: list[str], condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)


def validate_effect_fields(document: dict[str, Any], label: str, errors: list[str]) -> None:
    for field in EFFECT_FIELDS:
        fail(errors, document.get(field) == "NONE", f"{label}_{field}_must_be_NONE")


def validate_report(
    name: str,
    report: dict[str, Any],
    index: dict[str, Any],
    index_sha: str,
    expected_commit: str,
    errors: list[str],
) -> list[dict[str, Any]]:
    fail(errors, report.get("schema") == RESULTS_SCHEMA, f"{name}_unexpected_report_schema")
    fail(errors, report.get("status") == "PASS", f"{name}_report_status_not_PASS")
    fail(errors, report.get("source_commit") == expected_commit, f"{name}_source_commit_mismatch")
    fail(errors, report.get("index_sha256") == index_sha, f"{name}_index_sha256_mismatch")
    fail(errors, report.get("case_count") == EXPECTED_CASE_COUNT, f"{name}_report_case_count_not_27")
    fail(errors, report.get("case_count") == index.get("case_count"), f"{name}_report_index_count_mismatch")
    fail(errors, report.get("mismatches") == [], f"{name}_report_has_mismatches")
    validate_effect_fields(report, name, errors)

    rows = report.get("cases")
    if not isinstance(rows, list):
        errors.append(f"{name}_cases_not_array")
        return []
    fail(errors, len(rows) == EXPECTED_CASE_COUNT, f"{name}_case_rows_not_27")
    index_cases = index.get("cases")
    if not isinstance(index_cases, list):
        errors.append("index_cases_not_array")
        return rows

    expected_ids = [case.get("id") for case in index_cases if isinstance(case, dict)]
    actual_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    fail(errors, len(actual_ids) == len(rows), f"{name}_case_row_not_object")
    fail(errors, actual_ids == expected_ids, f"{name}_case_id_order_or_set_mismatch")

    expected_by_id = {case.get("id"): case for case in index_cases if isinstance(case, dict)}
    for row in rows:
        if not isinstance(row, dict):
            continue
        case_id = row.get("id")
        source_case = expected_by_id.get(case_id)
        if source_case is None:
            errors.append(f"{name}_unknown_case_id:{case_id}")
            continue
        fail(errors, row.get("input_sha256") == source_case.get("input_sha256"),
             f"{name}_{case_id}_input_sha256_mismatch")
        fail(errors, row.get("input_bytes") == source_case.get("input_bytes"),
             f"{name}_{case_id}_input_bytes_mismatch")
        fail(errors, row.get("expected_result") == source_case.get("expected_result"),
             f"{name}_{case_id}_expected_result_mismatch")
        fail(errors, row.get("expected_code") == source_case.get("expected_code"),
             f"{name}_{case_id}_expected_code_mismatch")
        fail(errors, row.get("matched") is True, f"{name}_{case_id}_matched_not_true")
        fail(errors, row.get("actual_result") == row.get("expected_result"),
             f"{name}_{case_id}_actual_result_mismatch")
        fail(errors, row.get("actual_code") == row.get("expected_code"),
             f"{name}_{case_id}_actual_code_mismatch")
    return rows


def validate_per_arch(args: argparse.Namespace) -> int:
    corpus_dir = args.corpus_dir.resolve()
    corpus_source_root = args.corpus_source_root.resolve()
    core_root = args.core_root.resolve()
    guard_root = args.guard_root.resolve()
    harness_root = args.harness_root.resolve()
    evidence_dir = args.guard_evidence_dir.resolve()
    errors: list[str] = []

    actual_core_commit = git(core_root, "rev-parse", "HEAD")
    actual_guard_commit = git(guard_root, "rev-parse", "HEAD")
    actual_corpus_commit = git(corpus_source_root, "rev-parse", "HEAD")
    actual_harness_commit = git(harness_root, "rev-parse", "HEAD")

    fail(errors, actual_core_commit == args.expected_core_commit, "core_checkout_commit_mismatch")
    fail(errors, actual_guard_commit == args.expected_ri_rs_commit, "ri_rs_checkout_commit_mismatch")
    fail(errors, actual_corpus_commit == args.expected_corpus_commit, "corpus_checkout_commit_mismatch")
    fail(errors, actual_harness_commit == args.expected_harness_commit, "harness_checkout_commit_mismatch")

    core_source = identity(core_root, "conformance/boundary/ri_py_receiver.py")
    core_test = identity(core_root, "conformance/boundary/test_ri_py_receipt_json_consumer.py")
    rs_source = identity(guard_root, "conformance/strict_wire.rs")
    rs_lib = identity(guard_root, "src/lib.rs")
    rs_cargo = identity(guard_root, "Cargo.toml")
    rs_test = identity(guard_root, "conformance/strict_wire_c6.rs")
    corpus_manifest_path = "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"
    materializer_path = "scripts/stage_c/materialize_c6_wire_corpus.py"
    workflow_path = ".github/workflows/stage-c-c6-integrated-evidence.yml"
    py_runner_path = "scripts/stage_c/run_ri_py_c6_consumer.py"
    verifier_path = "scripts/stage_c/verify_integrated_c6.py"
    corpus_manifest = identity(corpus_source_root, corpus_manifest_path)
    materializer = identity(corpus_source_root, materializer_path)
    harness_workflow = identity(harness_root, workflow_path)
    harness_runner = identity(harness_root, py_runner_path)
    harness_verifier = identity(harness_root, verifier_path)

    manifest_doc, manifest_raw = read_json(corpus_source_root / corpus_manifest_path)
    validate_effect_fields(manifest_doc, "source_manifest", errors)
    fail(errors, manifest_doc.get("schema") == "AURA-BC021-STRICT-WIRE-MUTATION-CORPUS/0.1",
         "unexpected_source_manifest_schema")
    fail(errors, manifest_doc.get("status") == "DRAFT_NON_NORMATIVE",
         "source_manifest_not_draft_non_normative")
    fail(errors, manifest_doc.get("stage") == "C6_PREPARATION", "source_manifest_stage_mismatch")

    index, index_raw = read_json(corpus_dir / "index.json")
    index_sha = digest(index_raw)
    fail(errors, index.get("schema") == INDEX_SCHEMA, "unexpected_materialized_index_schema")
    fail(errors, index.get("status") == "MATERIALIZED_FOR_TESTING_ONLY",
         "materialized_index_status_mismatch")
    validate_effect_fields(index, "materialized_index", errors)
    fail(errors, index.get("source_manifest_sha256") == digest(manifest_raw),
         "materialized_index_manifest_digest_mismatch")
    fail(errors, index.get("case_count") == EXPECTED_CASE_COUNT, "index_case_count_not_27")

    index_cases = index.get("cases")
    if not isinstance(index_cases, list):
        raise SystemExit("FAIL: index does not contain cases array")
    fail(errors, len(index_cases) == EXPECTED_CASE_COUNT, "index_cases_not_27")
    input_relpaths: list[str] = []
    input_digests: dict[str, str] = {}
    for case in index_cases:
        if not isinstance(case, dict):
            errors.append("index_case_not_object")
            continue
        rel = Path(str(case.get("input_file", "")))
        if rel.is_absolute() or ".." in rel.parts:
            errors.append(f"unsafe_input_path:{rel}")
            continue
        path = (corpus_dir / rel).resolve()
        if not path.is_relative_to(corpus_dir.resolve()) or not path.is_file():
            errors.append(f"missing_or_escaping_input:{rel}")
            continue
        raw = path.read_bytes()
        if len(raw) != case.get("input_bytes"):
            errors.append(f"input_byte_length_mismatch:{case.get('id')}")
        if digest(raw) != case.get("input_sha256"):
            errors.append(f"input_digest_mismatch:{case.get('id')}")
        input_relpaths.append(rel.as_posix())
        input_digests[rel.as_posix()] = digest(raw)
    actual_input_paths = sorted(
        path.relative_to(corpus_dir).as_posix()
        for path in (corpus_dir / "inputs").rglob("*")
        if path.is_file()
    )
    fail(errors, sorted(input_relpaths) == actual_input_paths, "input_file_inventory_mismatch")
    fail(errors, len(set(input_relpaths)) == EXPECTED_CASE_COUNT, "input_paths_missing_or_duplicated")

    ri_py_report, py_report_raw = read_json(corpus_dir / "results/ri-py-results.json")
    ri_rs_report, rs_report_raw = read_json(corpus_dir / "results/ri-rs-results.json")
    py_evidence, py_evidence_raw = read_json(corpus_dir / "ri-py-implementation-evidence.json")
    rs_evidence, rs_evidence_raw = read_json(evidence_dir / "implementation-evidence.json")
    rs_diagnostics, rs_diagnostics_raw = read_json(evidence_dir / "preservation-diagnostics.json")

    py_rows = validate_report(
        "ri_py", ri_py_report, index, index_sha, args.expected_core_commit, errors
    )
    rs_rows = validate_report(
        "ri_rs", ri_rs_report, index, index_sha, args.expected_ri_rs_commit, errors
    )

    validate_effect_fields(py_evidence, "ri_py_evidence", errors)
    validate_effect_fields(rs_evidence, "ri_rs_evidence", errors)
    fail(errors, py_evidence.get("schema") == EVIDENCE_SCHEMA, "ri_py_evidence_schema_mismatch")
    fail(errors, rs_evidence.get("schema") == EVIDENCE_SCHEMA, "ri_rs_evidence_schema_mismatch")
    fail(errors, rs_diagnostics.get("schema") == DIAGNOSTICS_SCHEMA,
         "ri_rs_diagnostics_schema_mismatch")
    fail(errors, py_evidence.get("tested_source_commit") == args.expected_core_commit,
         "ri_py_evidence_source_commit_mismatch")
    fail(errors, rs_evidence.get("tested_source_commit") == args.expected_ri_rs_commit,
         "ri_rs_evidence_source_commit_mismatch")
    fail(errors, py_evidence.get("corpus_source_commit") == args.expected_corpus_commit,
         "ri_py_evidence_corpus_source_commit_mismatch")
    fail(errors, py_evidence.get("architecture") == args.architecture,
         "ri_py_evidence_architecture_mismatch")
    fail(errors, py_evidence.get("shared_index_sha256") == index_sha,
         "ri_py_evidence_index_digest_mismatch")
    fail(errors, py_evidence.get("consumer_report_sha256") == digest(py_report_raw),
         "ri_py_evidence_report_digest_mismatch")
    fail(errors, py_evidence.get("consumer_report_bytes") == len(py_report_raw),
         "ri_py_evidence_report_byte_count_mismatch")
    fail(errors, py_evidence.get("consumer_report_status") == "PASS",
         "ri_py_evidence_report_not_PASS")
    fail(errors, py_evidence.get("preservation_status") == "PASS",
         "ri_py_evidence_preservation_not_PASS")
    fail(errors, py_evidence.get("preservation_errors") == [],
         "ri_py_evidence_has_preservation_errors")
    fail(errors, py_evidence.get("source_git_blob_oid") == core_source["git_blob_oid"],
         "ri_py_source_blob_oid_mismatch")
    fail(errors, py_evidence.get("source_content_sha256") == core_source["content_sha256"],
         "ri_py_source_content_sha256_mismatch")
    fail(errors, py_evidence.get("test_git_blob_oid") == core_test["git_blob_oid"],
         "ri_py_test_blob_oid_mismatch")
    fail(errors, py_evidence.get("test_content_sha256") == core_test["content_sha256"],
         "ri_py_test_content_sha256_mismatch")
    fail(errors, py_evidence.get("manifest_git_blob_oid") == corpus_manifest["git_blob_oid"],
         "ri_py_manifest_blob_oid_mismatch")
    fail(errors, py_evidence.get("manifest_content_sha256") == corpus_manifest["content_sha256"],
         "ri_py_manifest_content_sha256_mismatch")
    fail(errors, py_evidence.get("materializer_git_blob_oid") == materializer["git_blob_oid"],
         "ri_py_materializer_blob_oid_mismatch")
    fail(errors, py_evidence.get("materializer_content_sha256") == materializer["content_sha256"],
         "ri_py_materializer_content_sha256_mismatch")

    fail(errors, rs_evidence.get("component") == "RI-RS-AURA-GUARD-STRICT-BC021-CONSUMER",
         "ri_rs_evidence_component_mismatch")
    fail(errors, rs_evidence.get("repository") == "vaidt/aura-guard-v1.3",
         "ri_rs_evidence_repository_mismatch")
    fail(errors, rs_evidence.get("case_count") == EXPECTED_CASE_COUNT, "ri_rs_evidence_case_count_not_27")
    fail(errors, rs_evidence.get("shared_index_sha256") == index_sha,
         "ri_rs_evidence_index_digest_mismatch")
    fail(errors, rs_evidence.get("consumer_report_sha256") == digest(rs_report_raw),
         "ri_rs_evidence_report_digest_mismatch")
    fail(errors, rs_evidence.get("consumer_report_bytes") == len(rs_report_raw),
         "ri_rs_evidence_report_byte_count_mismatch")
    fail(errors, rs_evidence.get("consumer_report_status") == "PASS",
         "ri_rs_evidence_report_not_PASS")
    fail(errors, rs_evidence.get("preservation_status") == "PASS",
         "ri_rs_evidence_preservation_not_PASS")
    fail(errors, rs_evidence.get("preservation_errors") == [],
         "ri_rs_evidence_has_preservation_errors")
    fail(errors, rs_diagnostics.get("tested_source_commit") == args.expected_ri_rs_commit,
         "ri_rs_diagnostics_source_commit_mismatch")
    fail(errors, rs_diagnostics.get("preservation_status") == "PASS",
         "ri_rs_diagnostics_preservation_not_PASS")
    fail(errors, rs_diagnostics.get("errors") == [], "ri_rs_diagnostics_has_errors")
    fail(errors, rs_diagnostics.get("index_sha256") == index_sha,
         "ri_rs_diagnostics_index_digest_mismatch")
    fail(errors, rs_diagnostics.get("report_sha256") == digest(rs_report_raw),
         "ri_rs_diagnostics_report_digest_mismatch")
    fail(errors, rs_diagnostics.get("report_byte_count") == len(rs_report_raw),
         "ri_rs_diagnostics_report_byte_count_mismatch")
    fail(errors, rs_diagnostics.get("index_byte_count") == len(index_raw),
         "ri_rs_diagnostics_index_byte_count_mismatch")

    expected_rs_identities = {
        "consumer": rs_source,
        "library": rs_lib,
        "cargo_manifest": rs_cargo,
        "consumer_test": rs_test,
    }
    diag_identities = rs_diagnostics.get("source_blob_identity", {})
    for key, expected in expected_rs_identities.items():
        actual = diag_identities.get(key, {})
        fail(errors, actual.get("git_blob_oid") == expected["git_blob_oid"],
             f"ri_rs_{key}_blob_oid_mismatch")
        fail(errors, actual.get("content_sha256") == expected["content_sha256"],
             f"ri_rs_{key}_content_sha256_mismatch")

    fail(errors, rs_evidence.get("consumer_git_blob_oid") == rs_source["git_blob_oid"],
         "ri_rs_consumer_blob_oid_mismatch")
    fail(errors, rs_evidence.get("consumer_content_sha256") == rs_source["content_sha256"],
         "ri_rs_consumer_content_sha256_mismatch")
    fail(errors, rs_evidence.get("lib_git_blob_oid") == rs_lib["git_blob_oid"],
         "ri_rs_lib_blob_oid_mismatch")
    fail(errors, rs_evidence.get("lib_content_sha256") == rs_lib["content_sha256"],
         "ri_rs_lib_content_sha256_mismatch")
    fail(errors, rs_evidence.get("cargo_git_blob_oid") == rs_cargo["git_blob_oid"],
         "ri_rs_cargo_blob_oid_mismatch")
    fail(errors, rs_evidence.get("cargo_content_sha256") == rs_cargo["content_sha256"],
         "ri_rs_cargo_content_sha256_mismatch")
    fail(errors, rs_evidence.get("test_git_blob_oid") == rs_test["git_blob_oid"],
         "ri_rs_test_blob_oid_mismatch")
    fail(errors, rs_evidence.get("test_content_sha256") == rs_test["content_sha256"],
         "ri_rs_test_content_sha256_mismatch")

    negative_fixture_marker = evidence_dir / "negative-fixtures-pass.txt"
    if not negative_fixture_marker.is_file():
        errors.append("missing_ri_rs_negative_fixture_marker")
    else:
        fail(errors, negative_fixture_marker.read_text(encoding="utf-8").strip() == "9",
             "ri_rs_negative_fixture_count_not_9")

    py_by_id = {row.get("id"): row for row in py_rows if isinstance(row, dict)}
    rs_by_id = {row.get("id"): row for row in rs_rows if isinstance(row, dict)}
    fail(errors, set(py_by_id) == set(rs_by_id), "ri_py_ri_rs_case_id_set_mismatch")
    cross_impl_differences = []
    for case_id in sorted(set(py_by_id) | set(rs_by_id)):
        py_row, rs_row = py_by_id.get(case_id), rs_by_id.get(case_id)
        if py_row is None or rs_row is None:
            cross_impl_differences.append({"id": case_id, "difference": "missing_row"})
            continue
        py_contract = {field: py_row.get(field) for field in ROW_FIELDS}
        rs_contract = {field: rs_row.get(field) for field in ROW_FIELDS}
        if py_contract != rs_contract:
            cross_impl_differences.append({
                "id": case_id,
                "ri_py": py_contract,
                "ri_rs": rs_contract,
            })
    fail(errors, cross_impl_differences == [], "ri_py_ri_rs_outcomes_differ")

    harness_identities = {
        "workflow": harness_workflow,
        "ri_py_runner": harness_runner,
        "integrated_verifier": harness_verifier,
    }
    input_file_records = [
        {"path": path, "sha256": input_digests[path]}
        for path in sorted(input_digests)
    ]
    payload = {
        "schema": "AURA-C6-INTEGRATED-EVIDENCE/0.1",
        "result": "PASS" if not errors else "FAIL",
        "tested_sources": {
            "ri_py": {
                "repository": "vaidt/aura-poc-a-core-v3.3",
                "commit": actual_core_commit,
                "receiver_git_blob_oid": core_source["git_blob_oid"],
                "receiver_content_sha256": core_source["content_sha256"],
                "test_git_blob_oid": core_test["git_blob_oid"],
                "test_content_sha256": core_test["content_sha256"],
            },
            "ri_rs": {
                "repository": "vaidt/aura-guard-v1.3",
                "commit": actual_guard_commit,
                "consumer_git_blob_oid": rs_source["git_blob_oid"],
                "consumer_content_sha256": rs_source["content_sha256"],
                "lib_git_blob_oid": rs_lib["git_blob_oid"],
                "lib_content_sha256": rs_lib["content_sha256"],
                "cargo_git_blob_oid": rs_cargo["git_blob_oid"],
                "cargo_content_sha256": rs_cargo["content_sha256"],
                "test_git_blob_oid": rs_test["git_blob_oid"],
                "test_content_sha256": rs_test["content_sha256"],
            },
            "shared_corpus": {
                "repository": "vaidt/aura-specification",
                "commit": actual_corpus_commit,
                "manifest_git_blob_oid": corpus_manifest["git_blob_oid"],
                "manifest_content_sha256": corpus_manifest["content_sha256"],
                "materializer_git_blob_oid": materializer["git_blob_oid"],
                "materializer_content_sha256": materializer["content_sha256"],
                "index_sha256": index_sha,
                "case_count": len(index_cases),
                "input_file_count": len(input_file_records),
                "input_files": input_file_records,
            },
            "integration_harness": {
                "repository": "vaidt/aura-specification",
                "commit": actual_harness_commit,
                "workflow_git_blob_oid": harness_workflow["git_blob_oid"],
                "workflow_content_sha256": harness_workflow["content_sha256"],
                "runner_git_blob_oid": harness_runner["git_blob_oid"],
                "runner_content_sha256": harness_runner["content_sha256"],
                "verifier_git_blob_oid": harness_verifier["git_blob_oid"],
                "verifier_content_sha256": harness_verifier["content_sha256"],
            },
        },
        "architecture": args.architecture,
        "case_count": len(index_cases),
        "ri_py": {
            "status": ri_py_report.get("status"),
            "matched_cases": sum(row.get("matched") is True for row in py_rows if isinstance(row, dict)),
            "report_sha256": digest(py_report_raw),
        },
        "ri_rs": {
            "status": ri_rs_report.get("status"),
            "matched_cases": sum(row.get("matched") is True for row in rs_rows if isinstance(row, dict)),
            "report_sha256": digest(rs_report_raw),
            "negative_preservation_fixtures_rejected": 9,
        },
        "cross_implementation": {
            "status": "PASS" if not cross_impl_differences else "FAIL",
            "matched_cases": EXPECTED_CASE_COUNT - len(cross_impl_differences),
            "differences": cross_impl_differences,
        },
        "artifact_integrity": {
            "index_sha256": index_sha,
            "index_bytes": len(index_raw),
            "ri_py_report_sha256": digest(py_report_raw),
            "ri_py_report_bytes": len(py_report_raw),
            "ri_rs_report_sha256": digest(rs_report_raw),
            "ri_rs_report_bytes": len(rs_report_raw),
            "ri_py_evidence_sha256": digest(py_evidence_raw),
            "ri_rs_evidence_sha256": digest(rs_evidence_raw),
            "ri_rs_diagnostics_sha256": digest(rs_diagnostics_raw),
            "input_file_count": len(input_file_records),
            "all_index_inputs_present_and_hash_verified": len(input_file_records) == EXPECTED_CASE_COUNT,
        },
        "mismatches": errors,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
        "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
        "interpretation": (
            "Bounded technical agreement of RI-PY and RI-RS on this pinned 27-case "
            "BC-02.1 corpus and source set. This artifact does not constitute full CONF-003, "
            "DQ-006 closure, protocol ratification, release authorization, or a general "
            "constant-time proof."
        ),
    }

    output_path = corpus_dir / f"integrated-evidence-{args.architecture}.json"
    output_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(output_path.read_text(encoding="utf-8"))
    return 0 if not errors else 1


def compare_architectures(args: argparse.Namespace) -> int:
    root = args.artifact_root.resolve()
    errors: list[str] = []
    artifacts = {}
    for arch in ("x86_64", "aarch64"):
        artifact_dir = root / f"integrated-c6-{arch}"
        bundle = artifact_dir / "bundle"
        # upload-artifact may strip the provided root directory; accept either
        # representation while still requiring every expected member below.
        if not bundle.is_dir():
            bundle = artifact_dir
        artifacts[arch] = bundle
    for arch, path in artifacts.items():
        fail(errors, path.is_dir(), f"missing_architecture_bundle:{arch}")
    if errors:
        print(json.dumps({"result": "FAIL", "mismatches": errors}, indent=2))
        return 1

    per_arch: dict[str, dict[str, Any]] = {}
    raw_members: dict[str, dict[str, bytes]] = {}
    for arch, bundle in artifacts.items():
        corpus = bundle / "corpus"
        rs_evidence_dir = bundle / "ri-rs-evidence"
        index, index_raw = read_json(corpus / "index.json")
        py_report, py_raw = read_json(corpus / "results/ri-py-results.json")
        rs_report, rs_raw = read_json(corpus / "results/ri-rs-results.json")
        integrated, integrated_raw = read_json(corpus / f"integrated-evidence-{arch}.json")
        py_evidence, py_ev_raw = read_json(corpus / "ri-py-implementation-evidence.json")
        rs_evidence, rs_ev_raw = read_json(rs_evidence_dir / "implementation-evidence.json")
        diagnostics, diag_raw = read_json(rs_evidence_dir / "preservation-diagnostics.json")
        negative_marker = rs_evidence_dir / "negative-fixtures-pass.txt"
        fail(errors, negative_marker.is_file() and negative_marker.read_text(encoding="utf-8").strip() == "9",
             f"{arch}_negative_fixture_marker_missing_or_wrong")
        validate_effect_fields(integrated, f"{arch}_integrated", errors)
        validate_effect_fields(py_evidence, f"{arch}_ri_py_evidence", errors)
        validate_effect_fields(rs_evidence, f"{arch}_ri_rs_evidence", errors)

        fail(errors, integrated.get("schema") == "AURA-C6-INTEGRATED-EVIDENCE/0.1",
             f"{arch}_integrated_schema_mismatch")
        fail(errors, integrated.get("result") == "PASS", f"{arch}_integrated_result_not_PASS")
        fail(errors, integrated.get("case_count") == EXPECTED_CASE_COUNT, f"{arch}_integrated_case_count_not_27")
        fail(errors, integrated.get("c6_gate_status") == "BLOCKED_PENDING_EVIDENCE_REVIEW",
             f"{arch}_c6_gate_not_blocked_pending_review")
        fail(errors, integrated.get("mismatches") == [], f"{arch}_integrated_has_mismatches")
        fail(errors, index.get("schema") == INDEX_SCHEMA, f"{arch}_index_schema_mismatch")
        fail(errors, index.get("case_count") == EXPECTED_CASE_COUNT, f"{arch}_index_case_count_not_27")
        fail(errors, py_report.get("status") == "PASS", f"{arch}_ri_py_report_not_PASS")
        fail(errors, rs_report.get("status") == "PASS", f"{arch}_ri_rs_report_not_PASS")
        fail(errors, py_report.get("case_count") == EXPECTED_CASE_COUNT, f"{arch}_ri_py_count_not_27")
        fail(errors, rs_report.get("case_count") == EXPECTED_CASE_COUNT, f"{arch}_ri_rs_count_not_27")
        fail(errors, diagnostics.get("preservation_status") == "PASS", f"{arch}_rs_preservation_not_PASS")
        fail(errors, diagnostics.get("errors") == [], f"{arch}_rs_diagnostics_have_errors")
        fail(errors, rs_evidence.get("preservation_errors") == [], f"{arch}_rs_evidence_has_errors")
        fail(errors, integrated.get("artifact_integrity", {}).get("index_sha256") == digest(index_raw),
             f"{arch}_integrated_index_digest_mismatch")
        fail(errors, integrated.get("ri_py", {}).get("report_sha256") == digest(py_raw),
             f"{arch}_integrated_ri_py_report_digest_mismatch")
        fail(errors, integrated.get("ri_rs", {}).get("report_sha256") == digest(rs_raw),
             f"{arch}_integrated_ri_rs_report_digest_mismatch")
        fail(errors, py_evidence.get("consumer_report_sha256") == digest(py_raw),
             f"{arch}_ri_py_evidence_digest_mismatch")
        fail(errors, rs_evidence.get("consumer_report_sha256") == digest(rs_raw),
             f"{arch}_ri_rs_evidence_digest_mismatch")
        fail(errors, diagnostics.get("report_sha256") == digest(rs_raw),
             f"{arch}_rs_diagnostics_digest_mismatch")
        fail(errors, py_report.get("index_sha256") == digest(index_raw), f"{arch}_ri_py_index_binding_mismatch")
        fail(errors, rs_report.get("index_sha256") == digest(index_raw), f"{arch}_ri_rs_index_binding_mismatch")

        input_hashes: dict[str, str] = {}
        for case in index.get("cases", []):
            rel = Path(str(case.get("input_file", "")))
            if rel.is_absolute() or ".." in rel.parts:
                errors.append(f"{arch}_unsafe_input_path:{rel}")
                continue
            path = (corpus / rel).resolve()
            if not path.is_relative_to(corpus.resolve()) or not path.is_file():
                errors.append(f"{arch}_missing_input:{rel}")
                continue
            raw = path.read_bytes()
            if len(raw) != case.get("input_bytes") or digest(raw) != case.get("input_sha256"):
                errors.append(f"{arch}_input_integrity_mismatch:{case.get('id')}")
            input_hashes[rel.as_posix()] = digest(raw)
        fail(errors, len(input_hashes) == EXPECTED_CASE_COUNT, f"{arch}_input_file_count_not_27")

        # Require the complete retained bundle, including pinned source materials and harness.
        required_files = [
            corpus / "index.json",
            corpus / "ri-py-implementation-evidence.json",
            corpus / "results/ri-py-results.json",
            corpus / "results/ri-rs-results.json",
            corpus / f"integrated-evidence-{arch}.json",
            rs_evidence_dir / "implementation-evidence.json",
            rs_evidence_dir / "preservation-diagnostics.json",
            rs_evidence_dir / "negative-fixtures-pass.txt",
            bundle / "corpus-source/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json",
            bundle / "corpus-source/materialize_c6_wire_corpus.py",
            bundle / "harness/run_ri_py_c6_consumer.py",
            bundle / "harness/verify_integrated_c6.py",
            bundle / "harness/stage-c-c6-integrated-evidence.yml",
        ]
        required_files.extend(corpus / case["input_file"] for case in index.get("cases", []) if isinstance(case, dict))
        for required in required_files:
            fail(errors, required.is_file(), f"{arch}_artifact_missing:{required.relative_to(bundle)}")

        integrated_sources = integrated.get("tested_sources", {})
        fail(errors, integrated_sources.get("ri_py", {}).get("commit") == py_evidence.get("tested_source_commit"),
             f"{arch}_ri_py_source_binding_mismatch")
        fail(errors, integrated_sources.get("ri_rs", {}).get("commit") == rs_evidence.get("tested_source_commit"),
             f"{arch}_ri_rs_source_binding_mismatch")
        fail(errors, integrated_sources.get("shared_corpus", {}).get("commit") == py_evidence.get("corpus_source_commit"),
             f"{arch}_corpus_source_binding_mismatch")

        per_arch[arch] = {
            "case_count": EXPECTED_CASE_COUNT,
            "ri_py_matched": sum(row.get("matched") is True for row in py_report.get("cases", []) if isinstance(row, dict)),
            "ri_rs_matched": sum(row.get("matched") is True for row in rs_report.get("cases", []) if isinstance(row, dict)),
            "integrated_evidence_sha256": digest(integrated_raw),
            "ri_py_report_sha256": digest(py_raw),
            "ri_rs_report_sha256": digest(rs_raw),
            "index_sha256": digest(index_raw),
            "source_commits": {
                "ri_py": py_evidence.get("tested_source_commit"),
                "ri_rs": rs_evidence.get("tested_source_commit"),
                "corpus": py_evidence.get("corpus_source_commit"),
            },
            "preservation_negative_fixtures_rejected": 9,
        }
        raw_members[arch] = {
            "index": index_raw,
            "ri_py": py_raw,
            "ri_rs": rs_raw,
            "ri_py_evidence": py_ev_raw,
            "ri_rs_evidence": rs_ev_raw,
            "ri_rs_diagnostics": diag_raw,
            **{f"input:{name}": (corpus / name).read_bytes() for name in input_hashes},
        }

    differences = []
    for member in sorted(set(raw_members.get("x86_64", {})) | set(raw_members.get("aarch64", {}))):
        if raw_members.get("x86_64", {}).get(member) != raw_members.get("aarch64", {}).get(member):
            # Evidence files contain an architecture field and may differ by design.
            if member in ("ri_py_evidence", "ri_rs_evidence", "ri_rs_diagnostics"):
                continue
            differences.append(member)
    fail(errors, differences == [], "cross_architecture_byte_differences")
    for implementation in ("ri_py", "ri_rs"):
        fail(
            errors,
            per_arch["x86_64"][f"{implementation}_report_sha256"]
            == per_arch["aarch64"][f"{implementation}_report_sha256"],
            f"{implementation}_report_not_byte_identical_across_architectures",
        )
    fail(errors, per_arch["x86_64"]["index_sha256"] == per_arch["aarch64"]["index_sha256"],
         "index_not_byte_identical_across_architectures")
    for arch in ("x86_64", "aarch64"):
        fail(errors, per_arch[arch]["ri_py_matched"] == EXPECTED_CASE_COUNT,
             f"{arch}_ri_py_not_27_of_27")
        fail(errors, per_arch[arch]["ri_rs_matched"] == EXPECTED_CASE_COUNT,
             f"{arch}_ri_rs_not_27_of_27")
        fail(errors, len(per_arch[arch]["source_commits"]) == 3, f"{arch}_source_commit_binding_incomplete")

    payload = {
        "schema": "AURA-C6-INTEGRATED-CROSS-IMPLEMENTATION/0.1",
        "result": "PASS" if not errors else "FAIL",
        "case_count": EXPECTED_CASE_COUNT,
        "architectures": per_arch,
        "cross_implementation": {
            "ri_py_and_ri_rs_reports_each_match_all_cases": all(
                per_arch[arch]["ri_py_matched"] == EXPECTED_CASE_COUNT
                and per_arch[arch]["ri_rs_matched"] == EXPECTED_CASE_COUNT
                for arch in ("x86_64", "aarch64")
            ),
            "ri_py_report_byte_identical_across_architectures":
                per_arch["x86_64"]["ri_py_report_sha256"] == per_arch["aarch64"]["ri_py_report_sha256"],
            "ri_rs_report_byte_identical_across_architectures":
                per_arch["x86_64"]["ri_rs_report_sha256"] == per_arch["aarch64"]["ri_rs_report_sha256"],
            "index_byte_identical_across_architectures":
                per_arch["x86_64"]["index_sha256"] == per_arch["aarch64"]["index_sha256"],
        },
        "byte_differences": differences,
        "mismatches": errors,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
        "c6_gate_status": "BLOCKED_PENDING_EVIDENCE_REVIEW",
        "interpretation": (
            "This aggregate binds RI-PY and RI-RS to one pinned corpus and exact source identities, "
            "checks per-case agreement, preserves the 27-case evidence on x86_64/aarch64, and validates "
            "artifact completeness. It remains non-normative and does not close CONF-003 or DQ-006."
        ),
    }
    output = Path("integrated-c6-cross-implementation-summary.json")
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(output.read_text(encoding="utf-8"))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    per_arch = sub.add_parser("per-arch")
    per_arch.add_argument("--core-root", type=Path, required=True)
    per_arch.add_argument("--guard-root", type=Path, required=True)
    per_arch.add_argument("--corpus-source-root", type=Path, required=True)
    per_arch.add_argument("--corpus-dir", type=Path, required=True)
    per_arch.add_argument("--guard-evidence-dir", type=Path, required=True)
    per_arch.add_argument("--harness-root", type=Path, required=True)
    per_arch.add_argument("--architecture", choices=("x86_64", "aarch64"), required=True)
    per_arch.add_argument("--expected-core-commit", required=True)
    per_arch.add_argument("--expected-ri-rs-commit", required=True)
    per_arch.add_argument("--expected-corpus-commit", required=True)
    per_arch.add_argument("--expected-harness-commit", required=True)

    cross = sub.add_parser("compare-architectures")
    cross.add_argument("--artifact-root", type=Path, required=True)

    args = parser.parse_args()
    if args.mode == "per-arch":
        return validate_per_arch(args)
    return compare_architectures(args)


if __name__ == "__main__":
    raise SystemExit(main())
