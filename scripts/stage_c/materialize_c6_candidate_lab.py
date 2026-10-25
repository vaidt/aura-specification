#!/usr/bin/env python3
"""Deterministically materialize C6 candidate bytes as isolated, non-normative observations.

This script never sets expected parser outcomes. It consumes the pinned 27-case
manifest's source seed but writes all candidate outputs into a separate lab directory.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BASELINE_COMMIT = "6b4f3dcc46841bb17fafa3e1b1cc8ea9c0397330"
BASELINE_PATH = "fixtures/corpus/STAGE-C-C6-STRICT-WIRE-MUTATION-CORPUS-v0.1-DRAFT.json"
BASELINE_SHA256 = "c975cb0a3b02670b63ebb0e2809a2e0cb7c8247c2f0dc1a9829466f4806ea49d"
INVENTORY_COMMIT = "3a8e7ac3e26faa92fe383d090fe366b72ff438ff"
INVENTORY_PATH = "fixtures/corpus/STAGE-C-C6-EXTENDED-CANDIDATE-INVENTORY-v0.1-DRAFT.json"
INVENTORY_BLOB_OID = "06a4e8827fb589e3a549944c71718291d1345f16"
EXPECTED_INVENTORY_SCHEMA = "AURA-BC021-C6-EXTENDED-CANDIDATE-INVENTORY/0.1"
EXPECTED_BASELINE_SCHEMA = "AURA-BC021-STRICT-WIRE-MUTATION-CORPUS/0.1"
EXPECTED_EXCLUDED = {"C6-X-004", "C6-X-009", "C6-X-041"}
EFFECT_FIELDS = ("authority", "governance_effect", "authorization_effect", "release_effect")
PILOT_IDS = [f"C6-X-{number:03d}" for number in range(13, 21)]
FUZZ_SEED_LIMIT = 8
MAX_SAMPLE_BYTES = 2_000_000


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def write_new(root: Path, relative: str, raw: bytes) -> dict[str, Any]:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
    if len(raw) > MAX_SAMPLE_BYTES:
        raise ValueError(f"materialized sample exceeds hard byte limit: {relative}")
    return {
        "input_file": relative,
        "input_bytes": len(raw),
        "input_sha256": sha256(raw),
    }


def set_path(document: dict[str, Any], path: list[str], value: Any) -> None:
    if not path:
        raise ValueError("empty mutation path")
    current: Any = document
    for key in path[:-1]:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"missing mutation parent: {path!r}")
        current = current[key]
    if not isinstance(current, dict) or path[-1] not in current:
        raise ValueError(f"missing mutation target: {path!r}")
    current[path[-1]] = value


def delete_path(document: dict[str, Any], path: list[str]) -> None:
    if not path:
        raise ValueError("empty mutation path")
    current: Any = document
    for key in path[:-1]:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"missing mutation parent: {path!r}")
        current = current[key]
    if not isinstance(current, dict) or path[-1] not in current:
        raise ValueError(f"missing mutation target: {path!r}")
    del current[path[-1]]


def raw_replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    count = raw.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact byte-token match, got {count}")
    return raw.replace(old, new, 1)


def prepare_seed(manifest_raw: bytes) -> tuple[dict[str, Any], bytes, bytes]:
    manifest = json.loads(manifest_raw.decode("utf-8", errors="strict"))
    if manifest.get("schema") != EXPECTED_BASELINE_SCHEMA:
        raise ValueError("baseline manifest schema mismatch")
    if manifest.get("status") != "DRAFT_NON_NORMATIVE" or manifest.get("stage") != "C6_PREPARATION":
        raise ValueError("baseline manifest must stay DRAFT_NON_NORMATIVE")
    for field in EFFECT_FIELDS:
        if manifest.get(field) != "NONE":
            raise ValueError(f"baseline {field} must remain NONE")
    if len(manifest.get("mutations", [])) != 27:
        raise ValueError("baseline manifest must contain 27 cases")
    seed = copy.deepcopy(manifest["source_seed"]["receipt"])
    octets = bytes.fromhex(manifest["source_seed"]["raw_octets_hex"])
    seed["received"]["octet_length"] = len(octets)
    seed["received"]["raw_octets"] = base64.b64encode(octets).decode("ascii")
    seed["received"]["recomputed_sha256"] = sha256(octets)
    base_raw = canonical_json_bytes(seed)
    return seed, base_raw, octets


def raw_octets_variant(seed: dict[str, Any], octets: bytes, *, refresh_digest: bool = True) -> bytes:
    value = copy.deepcopy(seed)
    value["received"]["octet_length"] = len(octets)
    value["received"]["raw_octets"] = base64.b64encode(octets).decode("ascii")
    if refresh_digest:
        value["received"]["recomputed_sha256"] = sha256(octets)
    return canonical_json_bytes(value)


def nested_depth_candidate(seed: dict[str, Any], depth: int) -> bytes:
    value = copy.deepcopy(seed)
    nested: Any = None
    for _ in range(depth):
        nested = [nested]
    value["candidate_depth"] = nested
    return canonical_json_bytes(value)


def duplicate_key_variant(base_raw: bytes, target: str) -> bytes:
    if target == "schema_id":
        old = b'"schema_id":"BC-02.1-COMMON-RECEIPT"'
        new = old + b',"schema\\u005fid":"BC-02.1-COMMON-RECEIPT"'
        return raw_replace_once(base_raw, old, new, "C6-X-018")
    if target == "handoff.status":
        old = b'"status":"TRANSFERRED"'
        new = old + b',"st\\u0061tus":"TRANSFERRED"'
        return raw_replace_once(base_raw, old, new, "C6-X-019")
    raise ValueError(f"unsupported duplicate-key target: {target}")


def materialize_candidate(case: dict[str, Any], seed: dict[str, Any], base_raw: bytes, octets: bytes) -> tuple[str, bytes, dict[str, Any], list[dict[str, Any]]]:
    case_id = case["id"]
    name = case.get("candidate")
    value = copy.deepcopy(seed)
    supplemental: list[dict[str, Any]] = []
    profile: dict[str, Any] = {"selection": "deterministic exploratory input; no expected outcome assigned"}

    if case_id in {"C6-X-001", "C6-X-002", "C6-X-003", "C6-X-005", "C6-X-006"}:
        target = {
            "C6-X-001": ["fixture"],
            "C6-X-002": ["handoff"],
            "C6-X-003": ["received"],
            "C6-X-005": ["adapter"],
            "C6-X-006": ["environment"],
        }[case_id]
        delete_path(value, target)
        profile["mutation"] = {"operation": "delete_object", "path": target}
        return "BYTES", canonical_json_bytes(value), profile, supplemental

    if case_id in {"C6-X-007", "C6-X-008", "C6-X-010", "C6-X-011", "C6-X-012"}:
        target = {
            "C6-X-007": ["fixture"],
            "C6-X-008": ["handoff"],
            "C6-X-010": ["receiver"],
            "C6-X-011": ["adapter"],
            "C6-X-012": ["environment"],
        }[case_id]
        current: Any = value
        for key in target:
            current = current[key]
        current["candidate_extension"] = "candidate"
        profile["mutation"] = {"operation": "insert_unknown_key", "path": target, "key": "candidate_extension", "value": "candidate"}
        return "BYTES", canonical_json_bytes(value), profile, supplemental

    if case_id == "C6-X-013":
        return "BYTES", b"null", {"raw_input": "JSON null scalar; observation only"}, supplemental
    if case_id == "C6-X-014":
        return "BYTES", b"[]", {"raw_input": "top-level empty JSON array; observation only"}, supplemental
    if case_id == "C6-X-015":
        return "BYTES", b"\\xef\\xbb\\xbf" + base_raw, {"raw_prefix_hex": "efbbbf", "raw_input": "UTF-8 BOM prepended to baseline receipt bytes"}, supplemental
    if case_id == "C6-X-016":
        return "BYTES", base_raw + b"x", {"raw_suffix_hex": "78", "raw_input": "baseline receipt bytes followed by ASCII x"}, supplemental
    if case_id == "C6-X-017":
        return "BYTES", base_raw + base_raw, {"raw_input": "two exact baseline receipt byte sequences concatenated"}, supplemental
    if case_id == "C6-X-018":
        return "BYTES", duplicate_key_variant(base_raw, "schema_id"), {"duplicate_key_profile": "escaped-equivalent top-level schema_id key"}, supplemental
    if case_id == "C6-X-019":
        return "BYTES", duplicate_key_variant(base_raw, "handoff.status"), {"duplicate_key_profile": "escaped-equivalent nested handoff.status key"}, supplemental
    if case_id == "C6-X-020":
        raw = raw_replace_once(base_raw, b'"schema_version":1', b'"schema_version":NaN', "C6-X-020")
        return "BYTES", raw, {"numeric_lexeme": "NaN", "field": "schema_version", "note": "non-standard JSON numeric token; no expected result asserted"}, supplemental

    if case_id == "C6-X-021":
        value["received"]["raw_octets"] = "-_+/"
        profile["parameterization"] = "mixed URL-safe and standard Base64 alphabet characters"
    elif case_id == "C6-X-022":
        value["received"]["raw_octets"] = "QzYA /v8="
        profile["parameterization"] = "one ASCII space embedded in the Base64 transport text"
    elif case_id == "C6-X-023":
        value["received"]["raw_octets"] = "QzYA/v8==="
        profile["parameterization"] = "excess Base64 padding"
    elif case_id == "C6-X-024":
        value["received"]["raw_octets"] = "QzYA/v9="
        profile["parameterization"] = "non-zero unused Base64 pad bits"
    elif case_id == "C6-X-025":
        value["received"]["raw_octets"] = "éQ=="
        profile["parameterization"] = "non-ASCII character in Base64 transport text"
    elif case_id == "C6-X-026":
        value["received"]["raw_octets"] = "QzYA\\n/v8="
        profile["parameterization"] = "line feed embedded in Base64 transport text"
    elif case_id == "C6-X-027":
        profile["parameterization"] = "positive canonical Base64 round-trip for the pinned source octets"
    elif case_id == "C6-X-028":
        return "BYTES", raw_octets_variant(seed, bytes(range(256))), {"parameterization": "decoded raw octets 0x00 through 0xff; length and digest recomputed"}, supplemental
    elif case_id == "C6-X-029":
        value["received"]["octet_length"] = None
        profile["parameterization"] = "JSON null for octet_length"
    elif case_id == "C6-X-030":
        value["received"]["octet_length"] = "5"
        profile["parameterization"] = "JSON string for octet_length"
    elif case_id == "C6-X-031":
        raw = raw_replace_once(base_raw, b'"schema_version":1', b'"schema_version":1e0', "C6-X-031")
        return "BYTES", raw, {"numeric_lexeme": "1e0", "field": "schema_version"}, supplemental
    elif case_id == "C6-X-032":
        raw = raw_replace_once(base_raw, b'"schema_version":1', b'"schema_version":-0', "C6-X-032")
        return "BYTES", raw, {"numeric_lexeme": "-0", "field": "schema_version"}, supplemental
    elif case_id == "C6-X-033":
        large = b"A" * 65_536
        return "BYTES", raw_octets_variant(seed, large), {"parameterization": "65,536 decoded raw octets; exploratory size probe, not a declared contract limit"}, supplemental
    elif case_id == "C6-X-034":
        raw = raw_replace_once(base_raw, b'"octet_length":5', b'"octet_length":18446744073709551616', "C6-X-034")
        return "BYTES", raw, {"numeric_lexeme": "18446744073709551616", "field": "received.octet_length"}, supplemental
    elif case_id == "C6-X-035":
        raw = raw_replace_once(base_raw, b'"octet_length":5', b'"octet_length":-9223372036854775809', "C6-X-035")
        return "BYTES", raw, {"numeric_lexeme": "-9223372036854775809", "field": "received.octet_length"}, supplemental
    elif case_id == "C6-X-036":
        value["received"]["recomputed_sha256"] = value["received"]["recomputed_sha256"].upper()
        profile["parameterization"] = "uppercase hexadecimal SHA-256 text"
    elif case_id == "C6-X-037":
        value["received"]["recomputed_sha256"] = "g" * 64
        profile["parameterization"] = "64 non-hexadecimal characters"
    elif case_id == "C6-X-038":
        values = [("C6-X-038-S001", "a" * 63), ("C6-X-038-S002", "a" * 65)]
        for sub_id, digest_text in values:
            sub_value = copy.deepcopy(seed)
            sub_value["received"]["recomputed_sha256"] = digest_text
            raw = canonical_json_bytes(sub_value)
            metric = write_new(output_root, f"inputs/subcases/{sub_id}.bin", raw)
            supplemental.append({"id": sub_id, **metric, "observation_only": True})
        config = {
            "schema": "AURA-C6-CANDIDATE-SET-CONFIG/0.1",
            "candidate_id": case_id,
            "materialization_type": "MULTI_SAMPLE_SET",
            "samples": [item["id"] for item in supplemental],
            "parameterization": "digest text of 63 and 65 lowercase hexadecimal characters",
            "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
            "authority": "NONE", "governance_effect": "NONE", "authorization_effect": "NONE", "release_effect": "NONE",
        }
        raw_config = (json.dumps(config, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        return "MULTI_SAMPLE_SET", raw_config, {"parameterization": "digest-length boundary pair; two separate byte samples"}, supplemental
    elif case_id == "C6-X-039":
        text_digest = sha256(value["received"]["raw_octets"].encode("ascii"))
        value["received"]["recomputed_sha256"] = text_digest
        profile["parameterization"] = "SHA-256 over the Base64 text bytes instead of decoded raw octets"
    elif case_id == "C6-X-040":
        changed = bytearray(octets)
        changed[0] ^= 0x01
        value["received"]["raw_octets"] = base64.b64encode(bytes(changed)).decode("ascii")
        value["received"]["octet_length"] = len(changed)
        profile["parameterization"] = "flip first decoded octet and re-encode Base64 while retaining the original digest"
    elif case_id == "C6-X-042":
        value["fixture"]["fixture_id"] = ""
        profile["parameterization"] = "blank fixture identifier"
    elif case_id == "C6-X-043":
        value["environment"]["environment_id"] = ""
        profile["parameterization"] = "blank environment identifier"
    elif case_id == "C6-X-044":
        value["adapter"]["adapter_id"] = value["receiver"]["receiver_id"]
        profile["parameterization"] = "adapter_id aliases receiver_id"
    elif case_id == "C6-X-045":
        value["receiver"]["source_commit"] = "not-a-full-commit-sha"
        profile["parameterization"] = "malformed source commit token"
    elif case_id == "C6-X-046":
        value["environment"]["runtime"] = "CONFORMANT"
        profile["parameterization"] = "prohibited result-authority value in an identity/metadata field"
    elif case_id == "C6-X-047":
        value["schema_version"] = None
        del_path(value, ["receiver"])
        profile["parameterization"] = "composite defect: missing receiver object and null schema_version; no precedence expectation asserted"
    elif case_id == "C6-X-048":
        large = bytes(range(256)) * 4096
        return "BYTES", raw_octets_variant(seed, large), {"parameterization": "1,048,576 decoded raw octets; bounded exploratory size probe, not a declared contract limit"}, supplemental
    elif case_id == "C6-X-049":
        return "BYTES", nested_depth_candidate(seed, 256), {"parameterization": "256 nested arrays in an additional unknown top-level field; exploratory depth probe, not a declared contract limit"}, supplemental
    elif case_id == "C6-X-050":
        seeds = build_fuzz_seeds(seed, base_raw, octets)
        for seed_id, raw_seed, note in seeds:
            metric = write_new(output_root, f"inputs/fuzz/{seed_id}.bin", raw_seed)
            supplemental.append({"id": seed_id, **metric, "profile": note, "observation_only": True})
        fuzz_doc = {
            "schema": "AURA-C6-BOUNDED-FUZZ-SEED-SET/0.1",
            "status": "EXPLORATORY_NON_NORMATIVE",
            "generator": "deterministic fixed mutation set; no random source",
            "seed_count": len(supplemental),
            "max_seed_count": FUZZ_SEED_LIMIT,
            "max_sample_bytes": MAX_SAMPLE_BYTES,
            "seeds": supplemental,
            "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
            "authority": "NONE", "governance_effect": "NONE", "authorization_effect": "NONE", "release_effect": "NONE",
        }
        fuzz_raw = (json.dumps(fuzz_doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        write_new(output_root, "fuzz-seeds.json", fuzz_raw)
        config = {
            "schema": "AURA-C6-CANDIDATE-SET-CONFIG/0.1",
            "candidate_id": case_id,
            "materialization_type": "GENERATOR_CONFIGURATION",
            "seed_manifest": "fuzz-seeds.json",
            "seed_count": len(supplemental),
            "max_seed_count": FUZZ_SEED_LIMIT,
            "max_sample_bytes": MAX_SAMPLE_BYTES,
            "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
            "authority": "NONE", "governance_effect": "NONE", "authorization_effect": "NONE", "release_effect": "NONE",
        }
        raw_config = (json.dumps(config, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        return "GENERATOR_CONFIGURATION", raw_config, {"parameterization": "eight fixed bounded seeds; fuzz samples are separate sub-identifiers and are not one parser case"}, supplemental
    else:
        raise ValueError(f"{case_id}: no explicit deterministic materialization rule for {name!r}")

    raw = canonical_json_bytes(value)
    return "BYTES", raw, profile, supplemental


def del_path(value: dict[str, Any], path: list[str]) -> None:
    delete_path(value, path)


def build_fuzz_seeds(seed: dict[str, Any], base_raw: bytes, octets: bytes) -> list[tuple[str, bytes, str]]:
    invalid_utf8 = base_raw + b"\\xff"
    truncated = base_raw[:-1]
    changed = bytearray(octets)
    changed[0] ^= 0x01
    stale_digest = copy.deepcopy(seed)
    stale_digest["received"]["raw_octets"] = base64.b64encode(bytes(changed)).decode("ascii")
    stale_digest["received"]["octet_length"] = len(changed)
    depth = nested_depth_candidate(seed, 256)
    return [
        ("C6-X-050-S001", base_raw + b"x", "trailing ASCII byte"),
        ("C6-X-050-S002", b"\\xef\\xbb\\xbf" + base_raw, "UTF-8 BOM prefix"),
        ("C6-X-050-S003", truncated, "single-byte truncation"),
        ("C6-X-050-S004", invalid_utf8, "invalid UTF-8 trailing octet"),
        ("C6-X-050-S005", raw_replace_once(base_raw, b'"schema_id":"BC-02.1-COMMON-RECEIPT"', b'"schema_id":"BC-02.1-COMMON-RECEIPT","schema_id":"BC-02.1-COMMON-RECEIPT"', "fuzz S005"), "duplicate top-level key"),
        ("C6-X-050-S006", duplicate_key_variant(base_raw, "schema_id"), "escaped-equivalent duplicate key"),
        ("C6-X-050-S007", canonical_json_bytes(stale_digest), "single-octet source mutation with stale digest"),
        ("C6-X-050-S008", depth, "bounded nested-array depth probe"),
    ]


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"refusing to overwrite a non-empty run directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    baseline_raw = args.baseline_manifest.read_bytes()
    if sha256(baseline_raw) != BASELINE_SHA256:
        raise ValueError("baseline manifest content SHA-256 does not match L0 Source Lock")
    inventory_raw = args.inventory.read_bytes()
    inventory = json.loads(inventory_raw.decode("utf-8", errors="strict"))
    if inventory.get("schema") != EXPECTED_INVENTORY_SCHEMA or inventory.get("status") != "DRAFT_NON_NORMATIVE":
        raise ValueError("candidate inventory schema/status mismatch")
    if inventory.get("source_baseline", {}).get("commit") != BASELINE_COMMIT:
        raise ValueError("candidate inventory does not cite the pinned baseline commit")
    if inventory.get("source_baseline", {}).get("manifest_git_blob_oid") != "d9b4a1f488185a44f7edb233ef8ff180981f0e84":
        raise ValueError("candidate inventory baseline blob OID mismatch")
    for field in EFFECT_FIELDS:
        if inventory.get(field) != "NONE":
            raise ValueError(f"candidate inventory {field} must be NONE")
    cases = inventory.get("cases")
    if not isinstance(cases, list) or len(cases) != 50:
        raise ValueError("candidate inventory must have 50 entries")
    ids = [case.get("id") for case in cases]
    if ids != [f"C6-X-{number:03d}" for number in range(1, 51)]:
        raise ValueError("candidate IDs are not the expected unique contiguous sequence")
    active = [case for case in cases if case.get("included_in_candidate_pool") is True]
    excluded = {case.get("id") for case in cases if case.get("included_in_candidate_pool") is False}
    if len(active) != 47 or excluded != EXPECTED_EXCLUDED:
        raise ValueError("active pool/exclusion accounting is not exactly 47/3")
    if any(case.get("contract_binding_status") != "UNRESOLVED" or case.get("expected_outcome_policy") != "CONTRACT_DECISION_REQUIRED" for case in active):
        raise ValueError("candidate contract binding/expected outcome policy must remain unresolved")

    seed, base_raw, octets = prepare_seed(baseline_raw)
    # This directory is different from the pinned baseline manifest, index, and outputs.
    input_root = out / "inputs"
    input_root.mkdir()
    config_root = out / "candidate-configs"
    config_root.mkdir()
    index_cases: list[dict[str, Any]] = []
    for case in active:
        kind, raw, profile, supplemental = materialize_candidate(case, seed, base_raw, octets)
        candidate_id = case["id"]
        relative = f"inputs/{candidate_id}.bin" if kind == "BYTES" else f"candidate-configs/{candidate_id}.json"
        if kind == "BYTES":
            metric = write_new(out, relative, raw)
        else:
            # Multi-sample/generator candidates are represented by a config, not a fake parser expectation.
            config_path = out / relative
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with config_path.open("xb") as stream:
                stream.write(raw)
            metric = {"input_file": relative, "input_bytes": len(raw), "input_sha256": sha256(raw)}
        index_cases.append({
            "id": candidate_id,
            "candidate": case.get("candidate"),
            "dimension": case.get("dimension"),
            "materialization_kind": kind,
            **metric,
            "supplementary_inputs": supplemental,
            "materialization_profile": profile,
            "contract_binding_status": "UNRESOLVED",
            "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
            "observation_only": True,
            "governance_effect": "NONE",
        })

    expected_active_ids = [case["id"] for case in active]
    if [case["id"] for case in index_cases] != expected_active_ids:
        raise ValueError("materialized candidate order/count differs from active inventory")
    pilot = [case["id"] for case in index_cases if case["id"] in PILOT_IDS]
    if pilot != PILOT_IDS:
        raise ValueError("JSON pilot cases missing from materialized inventory")

    inventory_sha = sha256(inventory_raw)
    index = {
        "schema": "AURA-BC021-C6-CANDIDATE-MATERIALIZATION/0.1",
        "status": "EXPLORATORY_NON_NORMATIVE",
        "source_baseline": {
            "repository": "vaidt/aura-specification",
            "commit": BASELINE_COMMIT,
            "manifest_path": BASELINE_PATH,
            "manifest_git_blob_oid": "d9b4a1f488185a44f7edb233ef8ff180981f0e84",
            "manifest_content_sha256": BASELINE_SHA256,
        },
        "source_inventory": {
            "commit": INVENTORY_COMMIT,
            "path": INVENTORY_PATH,
            "git_blob_oid": INVENTORY_BLOB_OID,
            "content_sha256": inventory_sha,
            "source_entry_count": 50,
            "active_candidate_count": 47,
            "excluded_candidate_ids": sorted(EXPECTED_EXCLUDED),
        },
        "candidate_count": 47,
        "materialized_input_artifact_count": len(list((out / "inputs").rglob("*.bin"))),
        "pilot_group": {"name": "JSON syntax and transport", "candidate_ids": PILOT_IDS},
        "candidates": index_cases,
        "expected_outcome_policy": "CONTRACT_DECISION_REQUIRED",
        "authority": "NONE",
        "governance_effect": "NONE",
        "authorization_effect": "NONE",
        "release_effect": "NONE",
    }
    index_raw = (json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    write_new(out, "materialization-index.json", index_raw)
    print("C6_CANDIDATE_MATERIALIZATION=PASS")
    print(f"ACTIVE_CANDIDATES={len(index_cases)}")
    print(f"PHYSICAL_INPUT_SAMPLES={index['materialized_input_artifact_count']}")
    print(f"JSON_PILOT_CASES={len(PILOT_IDS)}")
    print(f"MATERIALIZATION_INDEX_SHA256={sha256(index_raw)}")
    print("PARSER_EXECUTION=NOT_PERFORMED")
    print("AUTHORITY=NONE")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    materialize(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as exc:
        print(f"C6_CANDIDATE_MATERIALIZATION=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
