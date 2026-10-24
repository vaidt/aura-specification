"""Execute the shared, materialized C6 wire input bytes against pinned RI-PY."""
from __future__ import annotations
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

CORE_ROOT = Path(os.environ["AURA_RI_PY_ROOT"]).resolve()
CORPUS_DIR = Path(os.environ["AURA_C6_WIRE_CORPUS_DIR"]).resolve()
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

        for case in cases:
            with self.subTest(case_id=case["id"]):
                raw = (CORPUS_DIR / case["input_file"]).read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                self.assertEqual(digest, case["input_sha256"])
                self.assertEqual(len(raw), case["input_bytes"])
                if case["expected_result"] == "ACCEPT":
                    try:
                        receipt = parse_receipt_json(raw)
                    except ReceiptParseError as exc:
                        self.fail(f"{case['id']}: expected acceptance, got {exc.code}: {exc}")
                    self.assertEqual(receipt.schema_id, "BC-02.1-COMMON-RECEIPT")
                else:
                    with self.assertRaises(ReceiptParseError) as context:
                        parse_receipt_json(raw)
                    self.assertEqual(context.exception.code, case["expected_code"])
                expected_code_text = "null" if case["expected_code"] is None else case["expected_code"]
                print(f"C6_SHARED_WIRE_CASE id={case['id']} input_sha256={digest} result={case['expected_result']} code={expected_code_text}")
