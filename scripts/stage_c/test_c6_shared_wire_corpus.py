"""Execute the exact materialized C6 wire corpus against pinned RI-PY."""
from __future__ import annotations
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

CORE_ROOT = Path(os.environ["AURA_RI_PY_ROOT"]).resolve()
CORPUS_DIR = Path(os.environ["AURA_C6_WIRE_CORPUS_DIR"]).resolve()
RESULTS_DIR = Path(os.environ["AURA_C6_WIRE_RESULTS_DIR"]).resolve()
SOURCE_COMMIT = os.environ["AURA_RI_PY_COMMIT"]
SOURCE_BLOB = os.environ["AURA_RI_PY_RECEIVER_BLOB"]
TEST_BLOB = os.environ["AURA_RI_PY_TEST_BLOB"]
sys.path.insert(0, str(CORE_ROOT))

from conformance.boundary.ri_py_receiver import ReceiptParseError, parse_receipt_json  # noqa: E402


class SharedC6WireCorpusTests(unittest.TestCase):
    def test_exact_materialized_inputs_against_ri_py(self):
        index_raw = (CORPUS_DIR / "index.json").read_bytes()
        index = json.loads(index_raw.decode("utf-8"))
        self.assertEqual(index["schema"], "AURA-BC021-MATERIALIZED-WIRE-CORPUS/0.1")
        self.assertEqual(index["status"], "MATERIALIZED_FOR_TESTING_ONLY")
        self.assertEqual(index["authority"], "NONE")
        self.assertEqual(index["governance_effect"], "NONE")
        cases = index["cases"]
        self.assertEqual(len(cases), index["case_count"])
        self.assertGreater(len(cases), 0)

        results = []
        for case in cases:
            with self.subTest(case_id=case["id"]):
                raw = (CORPUS_DIR / case["input_file"]).read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                self.assertEqual(digest, case["input_sha256"])
                self.assertEqual(len(raw), case["input_bytes"])
                expected_result = case["expected_result"]
                expected_code = case["expected_code"]

                actual_result = "REJECT"
                actual_code = None
                try:
                    receipt = parse_receipt_json(raw)
                    actual_result = "ACCEPT"
                    self.assertEqual(receipt.schema_id, "BC-02.1-COMMON-RECEIPT")
                except ReceiptParseError as exc:
                    actual_code = exc.code

                results.append({
                    "id": case["id"],
                    "input_sha256": digest,
                    "input_bytes": len(raw),
                    "expected_result": expected_result,
                    "expected_code": expected_code,
                    "actual_result": actual_result,
                    "actual_code": actual_code,
                })
                self.assertEqual(actual_result, expected_result)
                self.assertEqual(actual_code, expected_code)
                code_text = "null" if actual_code is None else actual_code
                print(f"C6_SHARED_WIRE_CASE id={case['id']} input_sha256={digest} result={actual_result} code={code_text}")

        report = {
            "schema": "AURA-BC021-WIRE-CONSUMER-RESULTS/0.1",
            "status": "PASS" if all(r["actual_result"] == r["expected_result"] and r["actual_code"] == r["expected_code"] for r in results) else "MISMATCH",
            "implementation": "RI-PY",
            "source_commit": SOURCE_COMMIT,
            "source_blob_sha256": SOURCE_BLOB,
            "test_blob_sha256": TEST_BLOB,
            "index_sha256": hashlib.sha256(index_raw).hexdigest(),
            "case_count": len(results),
            "cases": results,
            "authority": "NONE",
            "governance_effect": "NONE",
            "authorization_effect": "NONE",
            "release_effect": "NONE",
        }
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "ri-py-results.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
        )
        self.assertEqual(report["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
