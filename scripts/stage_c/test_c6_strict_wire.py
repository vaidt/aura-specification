from __future__ import annotations
import base64, hashlib, json, sys
from pathlib import Path
import unittest

SPEC_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SPEC_ROOT))
from conformance.boundary.strict_wire import parse_receipt_json, ReceiptWireError

RAW = b"C6\x00\xfe\xff"
def good():
    return {"schema_id":"BC-02.1-COMMON-RECEIPT","schema_version":1,
      "fixture":{"fixture_id":"FIX-C6","fixture_artifact_identity":"fixture.bin"},
      "handoff":{"status":"TRANSFERRED","method":"local"},
      "received":{"octet_length":len(RAW),"raw_octets":base64.b64encode(RAW).decode(),
        "recomputed_sha256":hashlib.sha256(RAW).hexdigest()},
      "receiver":{"receiver_id":"RI-PY","implementation_id":"impl","language":"Python",
        "implementation_version":"1","source_commit":"abc"},
      "adapter":{"adapter_id":"adapter","adapter_version":"1"},
      "environment":{"environment_id":"env","platform":"linux","runtime":"python"}}
def wire(value): return json.dumps(value,separators=(",",":"),ensure_ascii=False).encode()

class StrictWireTests(unittest.TestCase):
    def test_accepts_valid_receipt_and_preserves_non_utf8_raw_octets(self):
        parsed=parse_receipt_json(wire(good()))
        self.assertEqual(parsed.raw_octets, RAW)
    def test_rejects_unknown_and_authority_keys(self):
        for key in ("conformance_result","verdict","unknown"):
            v=good(); v[key]="PASS" if key!="unknown" else "x"
            with self.subTest(key=key), self.assertRaises(ReceiptWireError): parse_receipt_json(wire(v))
        v=good(); v["received"]["extension"]="x"
        with self.assertRaises(ReceiptWireError): parse_receipt_json(wire(v))
    def test_rejects_duplicate_keys_at_top_and_nested(self):
        base=wire(good()).decode()
        for mutant in (base.replace('"schema_id":"BC-02.1-COMMON-RECEIPT"', '"schema_id":"BAD","schema_id":"BC-02.1-COMMON-RECEIPT"'),
                       base.replace('"method":"local"', '"method":"local","method":"other"')):
            with self.assertRaises(ReceiptWireError): parse_receipt_json(mutant.encode())
    def test_rejects_invalid_utf8_and_bad_json(self):
        for data in (b"\xff", b"{"):
            with self.assertRaises(ReceiptWireError): parse_receipt_json(data)
    def test_rejects_null_missing_field_and_wrong_types(self):
        for mut in (lambda v:v.update({"x":None}),
                    lambda v:v["fixture"].pop("fixture_id"),
                    lambda v:v["received"].update({"octet_length":True}),
                    lambda v:v["received"].update({"octet_length":-1}),
                    lambda v:v["received"].update({"octet_length":2.0}),
                    lambda v:v["receiver"].update({"language":None})):
            v=good(); mut(v)
            with self.assertRaises(ReceiptWireError): parse_receipt_json(wire(v))
    def test_rejects_status_base64_length_and_digest_mutations(self):
        mutations=[
          lambda v:v["handoff"].update({"status":"PASS"}),
          lambda v:v["received"].update({"raw_octets":"%%%"}),
          lambda v:v["received"].update({"octet_length":2}),
          lambda v:v["received"].update({"recomputed_sha256":"0"*64}),
        ]
        for mut in mutations:
            v=good(); mut(v)
            with self.assertRaises(ReceiptWireError): parse_receipt_json(wire(v))
    def test_rejects_noncanonical_base64(self):
        v=good(); v["received"]["raw_octets"]=base64.b64encode(RAW).decode().rstrip("=")
        with self.assertRaises(ReceiptWireError): parse_receipt_json(wire(v))

if __name__ == "__main__": unittest.main(verbosity=2)
