#!/usr/bin/env python3
"""Run isolated Python/Rust JCS adapters against the committed bounded corpus.

This runner emits technical comparison evidence only. It does not perform Merkle
proof checks, negative protocol tests, conformance adjudication, or release gating.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUEST_SCHEMA = "AURA-STAGE-C-ADAPTER-REQUEST/0.1"
RESPONSE_SCHEMA = "AURA-STAGE-C-ADAPTER-RESPONSE/0.1"
MANIFEST_SCHEMA = "AURA-STAGE-C-JCS-MULTIVECTOR-MANIFEST/0.1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def repo_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe repository-relative path: {value!r}")
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path escapes repository root: {value!r}")
    return resolved


def run_logged(command: list[str], root: Path, env: dict[str, str], log_path: Path, timeout: int = 240) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        log = (
            f"COMMAND: {json.dumps(command, ensure_ascii=False)}\n"
            f"EXIT_CODE: {completed.returncode}\n"
            "--- STDOUT ---\n"
            f"{completed.stdout}\n"
            "--- STDERR ---\n"
            f"{completed.stderr}\n"
        )
        log_path.write_text(log, encoding="utf-8")
        return completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        log_path.write_text(
            f"COMMAND: {json.dumps(command, ensure_ascii=False)}\nTIMEOUT_SECONDS: {timeout}\n"
            f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}\n",
            encoding="utf-8",
        )
        return 124


def validate_response(
    root: Path,
    response_path: Path,
    output_path: Path,
    vector: dict[str, Any],
    expected_run_id: str,
    expected_source_commit: str,
    expected_language: str,
) -> dict[str, Any]:
    response = json.loads(response_path.read_bytes())
    if response.get("schema") != RESPONSE_SCHEMA:
        raise ValueError(f"wrong response schema: {response.get('schema')!r}")
    if response.get("run_id") != expected_run_id or response.get("operation") != "jcs.canonicalize":
        raise ValueError("response run_id/operation does not bind to request")
    if response.get("execution_status") != "COMPLETED" or response.get("authority") != "NONE":
        raise ValueError("response status/authority is not the expected non-authoritative state")
    adapter = response.get("adapter", {})
    if adapter.get("source_commit") != expected_source_commit:
        raise ValueError("response source_commit does not match pinned source revision")
    if adapter.get("language") != expected_language:
        raise ValueError("response language does not match adapter")
    if response.get("input", {}).get("fixture_id") != vector["fixture_id"]:
        raise ValueError("response fixture_id does not match manifest")
    input_bytes = repo_path(root, vector["input_path"]).read_bytes()
    actual = output_path.read_bytes()
    if response.get("input", {}).get("sha256") != sha256_hex(input_bytes):
        raise ValueError("response input SHA-256 does not bind to committed fixture")
    if response.get("output", {}).get("sha256") != sha256_hex(actual):
        raise ValueError("response output SHA-256 does not bind to output octets")
    if response.get("output", {}).get("octet_length") != len(actual):
        raise ValueError("response output length does not bind to output octets")
    return response


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("fixtures/corpus/JCS-MULTIVECTOR-MANIFEST-v0.1-DRAFT.json"),
    )
    parser.add_argument("--rust-manifest", type=Path, required=True)
    parser.add_argument("--python-source-commit", required=True)
    parser.add_argument("--rust-source-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--output-root", type=Path, default=Path("artifacts/stage-c/multivector")
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    try:
        manifest_path = repo_path(root, args.manifest.as_posix())
        if not SHA_RE.fullmatch(args.python_source_commit):
            raise ValueError("python-source-commit must be a 40-character lowercase Git SHA")
        if not SHA_RE.fullmatch(args.rust_source_commit):
            raise ValueError("rust-source-commit must be a 40-character lowercase Git SHA")
        if not args.run_id:
            raise ValueError("run-id must not be empty")
        manifest = json.loads(manifest_path.read_bytes())
        if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("status") != "DRAFT_NON_NORMATIVE":
            raise ValueError("manifest schema/status not accepted")
        if manifest.get("normative_effect") != "NONE" or manifest.get("release_effect") != "NONE":
            raise ValueError("manifest claims a prohibited normative/release effect")
        vectors = manifest.get("vectors")
        if not isinstance(vectors, list) or len(vectors) != 6:
            raise ValueError("expected six vectors including CANONICAL-003 baseline")
        ids = [v.get("fixture_id") for v in vectors]
        if len(set(ids)) != len(ids) or "CANONICAL-003" not in ids:
            raise ValueError("fixture IDs must be unique and include the frozen baseline")
    except Exception as exc:
        print(f"MANIFEST_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    output_root = (root / args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "manifest.snapshot.json").write_bytes(manifest_path.read_bytes())
    env = os.environ.copy()
    env["AURA_SPECIFICATION_ROOT"] = str(root)
    vector_results: list[dict[str, Any]] = []

    for vector in vectors:
        fixture_id = vector["fixture_id"]
        case_dir = output_root / fixture_id
        case_dir.mkdir(parents=True, exist_ok=True)
        result: dict[str, Any] = {
            "fixture_id": fixture_id,
            "input_path": vector["input_path"],
            "expected_path": vector["expected_path"],
            "expected_sha256": vector["expected_sha256"],
            "expected_octet_length": vector["expected_octet_length"],
            "passed": False,
            "checks": [],
            "errors": [],
        }
        try:
            input_path = repo_path(root, vector["input_path"])
            expected_path = repo_path(root, vector["expected_path"])
            input_bytes = input_path.read_bytes()
            expected_bytes = expected_path.read_bytes()
            if sha256_hex(input_bytes) != vector["input_sha256"]:
                raise ValueError("committed input SHA-256 does not match manifest")
            if sha256_hex(expected_bytes) != vector["expected_sha256"]:
                raise ValueError("committed oracle SHA-256 does not match manifest")
            if len(expected_bytes) != vector["expected_octet_length"] or expected_bytes.endswith(b"\n"):
                raise ValueError("committed oracle length/final-LF invariant failed")
            fixture = json.loads(input_bytes)
            if fixture.get("fixture_id") != fixture_id or "protocol_object" not in fixture:
                raise ValueError("fixture root identity/protocol_object mismatch")

            common = {
                "schema": REQUEST_SCHEMA,
                "run_id": args.run_id,
                "operation": "jcs.canonicalize",
                "fixture_id": fixture_id,
                "input_path": vector["input_path"],
                "json_pointer": "/protocol_object",
            }
            py_request = dict(common, source_commit=args.python_source_commit)
            rs_request = dict(common, source_commit=args.rust_source_commit)
            py_dir = case_dir / "python"
            rs_dir = case_dir / "rust"
            py_request_path = py_dir / "request.json"
            py_response_path = py_dir / "response.json"
            py_output_path = py_dir / "canonical.bin"
            rs_request_path = rs_dir / "request.json"
            rs_response_path = rs_dir / "response.json"
            rs_output_path = rs_dir / "canonical.bin"
            write_json(py_request_path, py_request)
            write_json(rs_request_path, rs_request)

            py_command = [
                sys.executable,
                str(root / "scripts/stage_c/python_jcs_probe.py"),
                "--request", str(py_request_path),
                "--response", str(py_response_path),
                "--output-octets", str(py_output_path),
                "--repo-root", str(root),
            ]
            py_code = run_logged(py_command, root, env, py_dir / "execution.log")
            if py_code != 0:
                raise ValueError(f"Python adapter exited with code {py_code}; see execution.log")

            rust_command = [
                "cargo", "run", "--locked", "--manifest-path", str(args.rust_manifest.resolve()),
                "--example", "stage_c_jcs_probe", "--",
                "--request", str(rs_request_path),
                "--response", str(rs_response_path),
                "--output-octets", str(rs_output_path),
                "--repo-root", str(root),
            ]
            rs_code = run_logged(rust_command, root, env, rs_dir / "execution.log")
            if rs_code != 0:
                raise ValueError(f"Rust adapter exited with code {rs_code}; see execution.log")

            py_response = validate_response(
                root, py_response_path, py_output_path, vector, args.run_id,
                args.python_source_commit, "Python",
            )
            rs_response = validate_response(
                root, rs_response_path, rs_output_path, vector, args.run_id,
                args.rust_source_commit, "Rust",
            )
            py_bytes = py_output_path.read_bytes()
            rs_bytes = rs_output_path.read_bytes()
            py_hash = sha256_hex(py_bytes)
            rs_hash = sha256_hex(rs_bytes)
            checks = {
                "python_matches_expected_bytes": py_bytes == expected_bytes,
                "rust_matches_expected_bytes": rs_bytes == expected_bytes,
                "python_rust_byte_identical": py_bytes == rs_bytes,
                "both_hashes_match_oracle": py_hash == rs_hash == vector["expected_sha256"],
                "both_lengths_match_oracle": len(py_bytes) == len(rs_bytes) == vector["expected_octet_length"],
                "python_response_provenance_valid": py_response["adapter"]["source_commit"] == args.python_source_commit,
                "rust_response_provenance_valid": rs_response["adapter"]["source_commit"] == args.rust_source_commit,
            }
            result["checks"] = checks
            result["python_output_sha256"] = py_hash
            result["rust_output_sha256"] = rs_hash
            result["output_octet_length"] = len(py_bytes)
            result["python_engine"] = py_response["adapter"].get("engine_distribution")
            result["python_engine_version"] = py_response["adapter"].get("engine_version")
            result["rust_engine"] = rs_response["adapter"].get("engine_distribution")
            result["rust_engine_version"] = rs_response["adapter"].get("engine_version")
            result["passed"] = all(checks.values())
            if not result["passed"]:
                result["errors"].append("One or more byte-level/provenance assertions failed.")
        except Exception as exc:
            result["errors"].append(f"{type(exc).__name__}: {exc}")

        write_json(case_dir / "vector-result.json", result)
        vector_results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{fixture_id}: {status}")

    all_passed = all(item["passed"] for item in vector_results) and len(vector_results) == 6
    summary = {
        "schema": "AURA-STAGE-C-JCS-MULTIVECTOR-EXECUTION-REPORT/0.1",
        "run_id": args.run_id,
        "manifest_schema": manifest["schema"],
        "vector_count": len(vector_results),
        "all_engineering_assertions_passed": all_passed,
        "engineering_result": "PASS" if all_passed else "FAIL",
        "python_source_commit": args.python_source_commit,
        "rust_adapter_source_commit": args.rust_source_commit,
        "vectors": vector_results,
        "scope": "bounded six-vector isolated adapter comparison; not full RFC 8785 or production RI-PY coverage",
        "normative_effect": "NONE",
        "governance_effect": "NONE",
        "release_effect": "NONE",
        "next_required_work": [
            "review multi-vector execution artifact and source pins",
            "then separately test Merkle leaf/node domain rules and proof shapes",
            "then execute protocol-specific negative tests",
            "resolve outstanding cargo-audit/cargo-deny findings; do not waive them",
        ],
    }
    write_json(output_root / "comparison.json", summary)
    (output_root / "summary.txt").write_text(
        f"Engineering result: {summary['engineering_result']}\n"
        f"Vectors: {len(vector_results)}\n"
        f"Python source: {args.python_source_commit}\n"
        f"Rust adapter source: {args.rust_source_commit}\n"
        "Normative effect: NONE\nGovernance effect: NONE\nRelease effect: NONE\n",
        encoding="utf-8",
    )
    print(f"Summary: {output_root / 'comparison.json'}")
    print("Normative effect: NONE; governance effect: NONE; release effect: NONE")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
