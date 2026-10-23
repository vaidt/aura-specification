"""Tests for the independent Stage C C5 RFC 6962 Merkle oracle."""
import unittest
from pathlib import Path
from merkle_c5_reference import audit_path, build_report, leaf_hash, load_corpus, merkle_tree_hash, node_hash, sha256, verify_audit_path

ROOT=Path(__file__).resolve().parents[2]
CORPUS_PATH=ROOT/"fixtures/corpus/STAGE-C-MERKLE-C5-v0.1-DRAFT.json"

class StageCMerkleC5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=load_corpus(CORPUS_PATH)
        cls.payloads=[x.encode("utf-8") for x in cls.corpus["leaf_payloads_utf8"]]
        cls.leaves=[leaf_hash(x) for x in cls.payloads]

    def test_fixed_leaf_and_root_vectors(self):
        self.assertEqual([x.hex() for x in self.leaves],self.corpus["expected_leaf_hashes_sha256"])
        self.assertEqual(len(self.corpus["expected_roots"]),len(self.leaves)+1)
        for case in self.corpus["expected_roots"]:
            self.assertEqual(merkle_tree_hash(self.leaves[:case["tree_size"]]).hex(),case["expected_root_sha256"],f"tree_size={case['tree_size']}")

    def test_leaf_and_node_domains_are_distinct(self):
        case=self.corpus["domain_separation_case"]
        left_raw=case["left_payload_utf8"].encode(); right_raw=case["right_payload_utf8"].encode()
        left=leaf_hash(left_raw); right=leaf_hash(right_raw); expected_node=node_hash(left,right)
        self.assertEqual(left.hex(),case["expected_left_leaf_sha256"])
        self.assertEqual(right.hex(),case["expected_right_leaf_sha256"])
        self.assertEqual(expected_node.hex(),case["expected_node_sha256"])
        self.assertEqual(sha256(left_raw).hex(),case["expected_raw_left_payload_sha256"])
        self.assertEqual(sha256(left+right).hex(),case["expected_undomain_separated_node_sha256"])
        self.assertNotEqual(left,sha256(left_raw)); self.assertNotEqual(expected_node,sha256(left+right))

    def test_every_leaf_index_has_a_valid_path(self):
        for case in self.corpus["expected_roots"]:
            size=case["tree_size"]; leaves=self.leaves[:size]; root=merkle_tree_hash(leaves)
            self.assertEqual(root.hex(),case["expected_root_sha256"])
            for i,leaf in enumerate(leaves):
                self.assertTrue(verify_audit_path(leaf,i,size,audit_path(i,leaves),root),f"size={size} index={i}")

    def test_primitive_tampering_controls_fail_closed(self):
        for case in self.corpus["expected_roots"]:
            size=case["tree_size"]; leaves=self.leaves[:size]
            if not leaves: continue
            root=merkle_tree_hash(leaves)
            for i,leaf in enumerate(leaves):
                proof=audit_path(i,leaves)
                self.assertFalse(verify_audit_path(leaf_hash(b"AURA-C5-TAMPERED"),i,size,proof,root))
                self.assertFalse(verify_audit_path(leaf,size,size,proof,root))
                self.assertFalse(verify_audit_path(leaf,i,size,proof,bytes(32)))
                if proof:
                    self.assertFalse(verify_audit_path(leaf,i,size,proof[:-1],root))
                    self.assertFalse(verify_audit_path(leaf,i,size,proof+[bytes(32)],root))
                    bad=list(proof); bad[0]=bytes([bad[0][0]^1])+bad[0][1:]
                    self.assertFalse(verify_audit_path(leaf,i,size,bad,root))

    def test_report_is_technical_only_and_contains_expected_proofs(self):
        report=build_report(self.corpus,CORPUS_PATH,"0"*40,"local-test")
        self.assertEqual(report["schema"],"AURA-STAGE-C-MERKLE-C5-ORACLE-REPORT/0.1")
        self.assertEqual(report["authority"],"NONE"); self.assertEqual(report["governance_effect"],"NONE")
        self.assertEqual(report["release_effect"],"NONE"); self.assertEqual(report["roots_checked"],18)
        self.assertEqual(report["valid_proofs_constructed_and_verified"],sum(range(18)))
        self.assertEqual(len(report["trees"]),18)

if __name__=="__main__": unittest.main()
