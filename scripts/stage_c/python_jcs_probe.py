#!/usr/bin/env python3
"""Stage C isolated Python JCS probe.

This is an experimental JCS execution shim, NOT the BC-02.2 RI-PY receiver,
and NOT a protocol conformance authority. It canonicalizes only the object at
/protocol_object using the pinned rfc8785 package and writes the raw output
bytes separately from its provenance envelope.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

import rfc8785

SCHEMA_REQUEST = "AURA-STAGE-C-ADAPTER-REQUEST/0.1"
SCHEMA_RESPONSE = "AURA-STAGE-C-ADAPTER-RESPONSE/0.1"
ADAPTER_ID = "STAGE-C-PYTHON-JCS-PROBE"
ADAPTER_VERSION = "0.1.0"
EXPECTED_REQUEST_KEYS = {
    "schema",
    "run_id",
    "operation",
    "fixture_id",
    "input_path",
    "json_pointer",
    "source_commit",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ProbeInputError(ValueError):
    """Request or input is invalid. This is not a conformance result."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProbeInputError(f"duplicate JSON member: {key!r}")
        result[key] = value
    return result


def _reject_non_json_constant(token: str) -> None:
    raise ProbeInputError(f"non-JSON numeric constant is prohibited: {token}")


def parse_json_bytes(raw: bytes) -> Any:
    """Decode strict UTF-8 JSON and reject duplicate members and NaN/Infinity."""
    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeInputError(f"input is not strict UTF-8 JSON: {exc}") from exc


def validate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise ProbeInputError("request root must be a JSON object")
    if set(request) != EXPECTED_REQUEST_KEYS:
        missing = sorted(EXPECTED_REQUEST_KEYS - set(request))
        unknown = sorted(set(request) - EXPECTED_REQUEST_KEYS)
        raise ProbeInputError(f"request field mismatch; missing={missing}, unknown={unknown}")
    if request["schema"] != SCHEMA_REQUEST:
        raise ProbeInputError(f"unsupported request schema: {request['schema']!r}")
    if request["operation"] != "jcs.canonicalize":
        raise ProbeInputError(f"unsupported operation: {request['operation']!r}")
    if request["json_pointer"] != "/protocol_object":
        raise ProbeInputError("v0.1 supports only JSON Pointer /protocol_object")
    for field in ("run_id", "fixture_id", "input_path"):
        if not isinstance(request[field], str) or not request[field]:
            raise ProbeInputError(f"{field} must be a non-empty string")
    if not isinstance(request["source_commit"], str) or not SHA_RE.fullmatch(request["source_commit"]):
        raise ProbeInputError("source_commit must be a 40-character lowercase Git SHA")
    return request


def resolve_input_path(repo_root: Path, input_path: str) -> Path:
    candidate = Path(input_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ProbeInputError("input_path must be repository-relative and must not contain '..'")
    root = repo_root.resolve()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ProbeInputError("input_path resolves outside the repository root")
    return resolved


def canonicalize_protocol_object(fixture_bytes: bytes, expected_fixture_id: str) -> bytes:
    fixture = parse_json_bytes(fixture_bytes)
    if not isinstance(fixture, dict):
        raise ProbeInputError("fixture root must be a JSON object")
    actual_fixture_id = fixture.get("fixture_id")
    if actual_fixture_id != expected_fixture_id:
        raise ProbeInputError(
            f"fixture identity mismatch: expected {expected_fixture_id!r}, got {actual_fixture_id!r}"
        )
    if "protocol_object" not in fixture:
        raise ProbeInputError("fixture does not contain JSON Pointer /protocol_object")
    try:
        output = rfc8785.dumps(fixture["protocol_object"])
    except Exception as exc:
        raise ProbeInputError(f"JCS engine rejected protocol_object: {type(exc).__name__}: {exc}") from exc
    if not isinstance(output, bytes):
        raise RuntimeError(f"rfc8785.dumps returned {type(output).__name__}, expected bytes")
    return output


def execute_request(
    request_path: Path,
    response_path: Path,
    output_path: Path,
    repo_root: Path,
) -> int:
    request = validate_request(parse_json_bytes(request_path.read_bytes()))
    input_path = resolve_input_path(repo_root, request["input_path"])
    input_bytes = input_path.read_bytes()
    canonical_bytes = canonicalize_protocol_object(input_bytes, request["fixture_id"])

    # Binary write is deliberate: no BOM, newline, text encoding, or reserialization.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(canonical_bytes)

    response = {
        "schema": SCHEMA_RESPONSE,
        "run_id": request["run_id"],
        "operation": request["operation"],
        "execution_status": "COMPLETED",
        "authority": "NONE",
        "adapter": {
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "language": "Python",
            "source_commit": request["source_commit"],
            "engine_distribution": "rfc8785",
            "engine_version": importlib.metadata.version("rfc8785"),
            "python_runtime": sys.version,
            "platform": platform.platform(),
        },
        "input": {
            "fixture_id": request["fixture_id"],
            "path": request["input_path"],
            "json_pointer": request["json_pointer"],
            "octet_length": len(input_bytes),
            "sha256": sha256_hex(input_bytes),
        },
        "output": {
            "path": str(output_path),
            "octet_length": len(canonical_bytes),
            "sha256": sha256_hex(canonical_bytes),
        },
        "scope_note": (
            "Isolated JCS probe only; no receiver handoff, Merkle decision, "
            "protocol conformance, acceptance, ratification, or release result."
        ),
    }
    response_bytes = (
        json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response_path.write_bytes(response_bytes)
    print(f"execution_status={response['execution_status']}")
    print(f"adapter_id={ADAPTER_ID}")
    print(f"engine=rfc8785 {response['adapter']['engine_version']}")
    print(f"input_sha256={response['input']['sha256']}")
    print(f"output_octet_length={response['output']['octet_length']}")
    print(f"output_sha256={response['output']['sha256']}")
    print("authority=NONE")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--output-octets", required=True, type=Path)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args(argv)
    try:
        return execute_request(args.request, args.response, args.output_octets, args.repo_root)
    except ProbeInputError as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"OUTPUT_OR_INPUT_ERROR: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:  # fail closed; report unexpected engine/adapter failures
        print(f"EXECUTION_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
