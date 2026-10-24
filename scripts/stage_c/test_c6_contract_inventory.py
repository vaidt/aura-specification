"""Inventory tests for C6 preparation; these do not claim protocol execution."""
import json
import tempfile
import unittest
from pathlib import Path
from c6_contract_inventory import load_and_validate

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "fixtures/corpus/STAGE-C-C6-CONTRACT-NEGATIVES-v0.1-DRAFT.json"

class C6InventoryTests(unittest.TestCase):
    def test_full_inventory_is_covered_and_remains_blocked(self):
        report = load_and_validate(MANIFEST)
        self.assertEqual(report["status"], "PREPARATION_ONLY")
        self.assertEqual(report["c6_gate_status"], "BLOCKED_NOT_EXECUTED")
        self.assertEqual(report["manifest_case_count"], 19)
        self.assertEqual(report["native_cross_language_wire_consumer_parity"], "BOUNDED_PARITY_PASS_PENDING_EVIDENCE_REVIEW")
        self.assertEqual(report["pending_shared_corpus_count"], 0)
        self.assertEqual(report["tested_pending_review_count"], 7)
        self.assertEqual(len(report["known_or_unwired_gap_case_ids"]), 0)
        self.assertEqual(report["authority"], "NONE")
        self.assertEqual(report["governance_effect"], "NONE")
        self.assertEqual(report["authorization_effect"], "NONE")
        self.assertEqual(report["release_effect"], "NONE")

    def test_duplicate_case_ids_fail_closed(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["cases"].append(dict(manifest["cases"][0]))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate C6 case IDs"):
                load_and_validate(path)

    def test_unknown_disposition_fails_closed(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["cases"][0]["disposition"] = "PASS"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-disposition.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown disposition"):
                load_and_validate(path)

if __name__ == "__main__":
    unittest.main()
