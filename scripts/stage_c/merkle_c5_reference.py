#!/usr/bin/env python3
"""Independent RFC 6962 Merkle reference model for Stage C C5 (non-normative)."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def leaf_hash(data: bytes) -> bytes:
    return sha256(b"\x00" + data)

def node_hash(left: bytes, right: bytes) -> bytes:
    if len(left) != 32 or len(right) != 32:
        raise ValueError("node children must be 32-byte digests")
    return sha256(b"\x01" + left + right)

def largest_power_of_two_lt(n: int) -> int:
    if n < 2:
        raise ValueError("tree size must be >= 2")
    return 1 << ((n - 1).bit_length() - 1)

def merkle_tree_hash(leaves: list[bytes]) -> bytes:
    if not leaves: return sha256(b"")
    if len(leaves) == 1: return leaves[0]
    k = largest_power_of_two_lt(len(leaves))
    return node_hash(merkle_tree_hash(leaves[:k]), merkle_tree_hash(leaves[k:]))

def audit_path(index: int, leaves: list[bytes]) -> list[bytes]:
    n = len(leaves)
    if not 0 <= index < n: raise ValueError("leaf index out of range")
    if n == 1: return []
    k = largest_power_of_two_lt(n)
    if index < k:
        return audit_path(index, leaves[:k]) + [merkle_tree_hash(leaves[k:])]
    return audit_path(index - k, leaves[k:]) + [merkle_tree_hash(leaves[:k])]

def verify_audit_path(leaf: bytes, index: int, tree_size: int, proof: list[bytes], expected_root: bytes) -> bool:
    if tree_size < 1 or not 0 <= index < tree_size or len(leaf) != 32 or len(expected_root) != 32:
        return False
    position = 0
    def walk(i: int, n: int, current: bytes) -> bytes | None:
        nonlocal position
        if n == 1: return current
        k = largest_power_of_two_lt(n)
        if i < k:
            child = walk(i, k, current)
            if child is None or position >= len(proof): return None
            sibling = proof[position]; position += 1
            return node_hash(child, sibling)
        child = walk(i-k, n-k, current)
        if child is None or position >= len(proof): return None
        sibling = proof[position]; position += 1
        return node_hash(sibling, child)
    rebuilt = walk(index, tree_size, leaf)
    return position == len(proof) and rebuilt == expected_root

def load_corpus(path: Path) -> dict[str, Any]:
    corpus = json.loads(path.read_text(encoding="utf-8"))
    if corpus.get("schema") != "AURA-STAGE-C-MERKLE-C5-CORPUS/0.1":
        raise ValueError("unexpected C5 corpus schema")
    if corpus.get("status") != "DRAFT_NON_NORMATIVE":
        raise ValueError("C5 corpus must remain non-normative")
    return corpus

def build_report(corpus: dict[str, Any], corpus_path: Path, source_commit: str, run_id: str) -> dict[str, Any]:
    payloads = [x.encode("utf-8") for x in corpus["leaf_payloads_utf8"]]
    leaves = [leaf_hash(x) for x in payloads]
    if [x.hex() for x in leaves] != corpus["expected_leaf_hashes_sha256"]:
        raise ValueError("fixed leaf digest mismatch")
    if len(corpus["expected_roots"]) != len(leaves)+1:
        raise ValueError("expected roots must cover sizes 0..N")
    trees=[]; proof_count=0; rejected_controls=0
    for case in corpus["expected_roots"]:
        size=int(case["tree_size"])
        if not 0 <= size <= len(leaves): raise ValueError(f"invalid tree size {size}")
        subset=leaves[:size]; root=merkle_tree_hash(subset)
        if root.hex()!=case["expected_root_sha256"]: raise ValueError(f"fixed root mismatch: size={size}")
        proofs=[]
        for index, leaf in enumerate(subset):
            proof=audit_path(index, subset)
            if not verify_audit_path(leaf,index,size,proof,root): raise ValueError(f"reference proof invalid: size={size} index={index}")
            controls=[]
            candidates=[
                ("tampered_leaf", leaf_hash(b"AURA-C5-TAMPERED"), index, proof, root),
                ("tampered_root", leaf, index, proof, bytes(32)),
                ("out_of_range_index", leaf, size, proof, root)
            ]
            if proof:
                candidates += [
                    ("truncated_proof", leaf,index,proof[:-1],root),
                    ("extra_proof_element",leaf,index,proof+[bytes(32)],root),
                    ("tampered_sibling",leaf,index,[bytes([proof[0][0]^1])+proof[0][1:]]+proof[1:],root)
                ]
            for label,c_leaf,c_index,c_proof,c_root in candidates:
                if verify_audit_path(c_leaf,c_index,size,c_proof,c_root):
                    raise ValueError(f"{label} unexpectedly verified: size={size} index={index}")
                controls.append(label); rejected_controls+=1
            proofs.append({"leaf_index":index,"sibling_hashes_sha256":[x.hex() for x in proof],"valid_proof":True,"rejected_controls":controls})
            proof_count+=1
        trees.append({"tree_size":size,"expected_root_sha256":root.hex(),"proofs":proofs})
    d=corpus["domain_separation_case"]
    left_raw=d["left_payload_utf8"].encode(); right_raw=d["right_payload_utf8"].encode()
    left=leaf_hash(left_raw); right=leaf_hash(right_raw); node=node_hash(left,right)
    if left.hex()!=d["expected_left_leaf_sha256"] or right.hex()!=d["expected_right_leaf_sha256"] or node.hex()!=d["expected_node_sha256"]:
        raise ValueError("fixed domain-separated hash vector mismatch")
    if sha256(left_raw).hex()!=d["expected_raw_left_payload_sha256"] or sha256(left+right).hex()!=d["expected_undomain_separated_node_sha256"]:
        raise ValueError("unprefixed contrast vector mismatch")
    return {
      "schema":"AURA-STAGE-C-MERKLE-C5-ORACLE-REPORT/0.1",
      "status":"TECHNICAL_ORACLE_ONLY","authority":"NONE","protocol_conformance":"NOT_ASSESSED",
      "governance_effect":"NONE","release_effect":"NONE","run_id":run_id,"source_commit":source_commit,
      "corpus_path":str(corpus_path),"corpus_sha256":hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
      "algorithm_profile":corpus["profile"],"tree_sizes_checked":[x["tree_size"] for x in trees],
      "roots_checked":len(trees),"leaf_hashes_checked":len(leaves),
      "valid_proofs_constructed_and_verified":proof_count,"rejected_primitive_tamper_controls":rejected_controls,
      "domain_separation_case":{"left_leaf_sha256":left.hex(),"right_leaf_sha256":right.hex(),"node_sha256":node.hex()},
      "trees":trees
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--corpus",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--source-commit",required=True); p.add_argument("--run-id",required=True); a=p.parse_args()
    corpus=load_corpus(a.corpus); report=build_report(corpus,a.corpus,a.source_commit,a.run_id)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    for key in ("corpus_sha256","roots_checked","leaf_hashes_checked","valid_proofs_constructed_and_verified","rejected_primitive_tamper_controls"): print(f"{key}={report[key]}")
    print("oracle_status=TECHNICAL_ORACLE_ONLY"); print("authority=NONE"); return 0

if __name__=="__main__": raise SystemExit(main())
