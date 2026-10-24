#!/usr/bin/env python3
"""Materialize the shared C6 BC-02.1 receipt JSON mutation corpus once."""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def nested_parent(document: dict[str, Any], path: list[str]) -> dict[str, Any]:
    current: Any = document
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"invalid mutation path: {path!r}")
        current = current[key]
    if not isinstance(current, dict):
        raise ValueError(f"mutation target is not an object: {path!r}")
    return current


def materialize(manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    if manifest.get("schema") != "AURA-BC021-STRICT-WIRE-MUTATION-CORPUS/0.1":
        raise ValueError("unexpected strict wire corpus schema")
    if manifest.get("status") != "DRAFT_NON_NORMATIVE" or manifest.get("stage") != "C6_PREPARATION":
        raise ValueError("wire corpus must remain a draft C6 preparation artifact")
    for field in ("authority", "governance_effect", "authorization_effect", "release_effect"):
        if manifest.get(field) != "NONE":
            raise ValueError(f"{field} must remain NONE")
    seed = copy.deepcopy(manifest["source_seed"]["receipt"])
    octets = bytes.fromhex(manifest["source_seed"]["raw_octets_hex"])
    seed["received"]["octet_length"] = len(octets)
    seed["received"]["raw_octets"] = base64.b64encode(octets).decode("ascii")
    seed["received"]["recomputed_sha256"] = hashlib.sha256(octets).hexdigest()
    base_bytes = canonical_json_bytes(seed)
    base_text = base_bytes.decode("utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    inputs_dir = output_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    seen_ids: set[str] = set()
    for case in manifest.get("mutations", []):
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen_ids:
            raise ValueError(f"missing or duplicate case id: {case_id!r}")
        seen_ids.add(case_id)
        operation = case.get("operation")
        payload: bytes
        if operation == "accept":
            payload = base_bytes
        elif operation == "empty_raw_octets":
            value = copy.deepcopy(seed)
            value["received"]["octet_length"] = 0
            value["received"]["raw_octets"] = ""
            value["received"]["recomputed_sha256"] = hashlib.sha256(b"").hexdigest()
            payload = canonical_json_bytes(value)
        elif operation in {"set", "delete", "insert"}:
            value = copy.deepcopy(seed)
            path = case.get("path", [])
            if not isinstance(path, list) or not all(isinstance(item, str) for item in path):
                raise ValueError(f"{case_id}: mutation path must be a string array")
            if operation == "set":
                parent = nested_parent(value, path[:-1]) if path else None
                if parent is None or path[-1] not in parent:
                    raise ValueError(f"{case_id}: set must target an existing field")
                parent[path[-1]] = case.get("value")
            elif operation == "delete":
                parent = nested_parent(value, path[:-1]) if path else None
                if parent is None or path[-1] not in parent:
                    raise ValueError(f"{case_id}: delete must target an existing field")
                del parent[path[-1]]
            else:
                parent = nested_parent(value, path)
                key = case.get("key")
                if not isinstance(key, str) or key in parent:
                    raise ValueError(f"{case_id}: insert key must be new")
                parent[key] = case.get("value")
            payload = canonical_json_bytes(value)
        elif operation == "duplicate_key":
            needle = case.get("needle")
            replacement = case.get("replacement")
            if not isinstance(needle, str) or base_text.count(needle) != 1 or not isinstance(replacement, str):
                raise ValueError(f"{case_id}: duplicate-key replacement must match exactly once")
            payload = base_text.replace(needle, replacement, 1).encode("utf-8")
        elif operation == "raw_text":
            payload = case["text"].encode("utf-8")
        elif operation == "raw_hex":
            payload = bytes.fromhex(case["hex"])
        else:
            raise ValueError(f"{case_id}: unsupported mutation operation {operation!r}")

        filename = f"{case_id}.bin"
        (inputs_dir / filename).write_bytes(payload)
        expected_code = case.get("expected_code")
        if expected_code is not None and (not isinstance(expected_code, str) or not expected_code):
            raise ValueError(f"{case_id}: expected_code must be null or a non-empty string")
        cases.append({
            "id": case_id,
            "source_case": case.get("source_case"),
            "operation": operation,
            "expected_code": expected_code,
            "expected_result": "ACCEPT" if expected_code is None else "REJECT",
            "input_file": f"inputs/{filename}",
            "input_bytes": len(payload),
            "input_sha256": hashlib.sha256(payload).hexdigest(),
        })

    if not cases or len(seen_ids) != len(manifest["mutations"]):
        raise ValueError("wire mutation corpus must be non-empty and uniquely identified")
    index = {
        "schema": "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1",
        "status": "MATERIALIZED_FOR_TESTING_ONLY",
        "source_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "seed_envelope_sha256": hashlib.sha256(base_bytes).hexdigest(),
        "case_count": len(cases),
        "cases": cases,
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    (output_dir / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("materialization_status=MATERIALIZED_FOR_TESTING_ONLY")
    print(f"case_count={len(cases)}")
    print(f"source_manifest_sha256={index['source_manifest_sha256']}")
    print(f"index_sha256={hashlib.sha256((output_dir / 'index.json').read_bytes()).hexdigest()}")
    print("authority=NONE")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    materialize(args.manifest, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
