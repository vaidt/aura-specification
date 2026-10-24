"""C6 native negative tests against the exact pinned RI-PY receiver API.

These tests exercise typed receipt construction/validation. They do not claim
that RI-PY has a strict JSON receipt consumer; the manifest records that gap.
"""
from __future__ import annotations

import base64
import dataclasses
import json
import os
import sys
import unittest
from pathlib import Path

CORE_ROOT = Path(os.environ["AURA_RI_PY_ROOT"]).resolve()
sys.path.insert(0, str(CORE_ROOT))

from conformance.boundary.ri_py_receiver import (  # noqa: E402
    AdapterIdentity,
    BoundaryReceiver,
    EnvironmentIdentity,
    FixtureIdentity,
    ReceiptConstructionError,
    ReceiverIdentity,
    validate_receipt,
    serialize_receipt,
)

SYNTHETIC_OCTETS = b"C6-SYNTHETIC\x00\xfe\xff"
FIXTURE = FixtureIdentity("FIX-C6-SYNTHETIC", "FIX-C6-SYNTHETIC.bin")


def build_receiver():
    return BoundaryReceiver(
        receiver=ReceiverIdentity(
            receiver_id="RI-PY",
            implementation_id="aura-ri-py",
            implementation_version="1.0.0",
            source_commit="1111111111111111111111111111111111111111",
        ),
        adapter=AdapterIdentity("BC-02.2-RI-PY-BOUNDARY-ADAPTER", "1.0.0"),
        environment=EnvironmentIdentity("c6-preflight", "linux-x86_64", "python-test-runtime"),
    )


def build_receipt(octets=SYNTHETIC_OCTETS):
    return build_receiver().receive(
        fixture=FIXTURE,
        method="synthetic-in-memory-octet-transfer",
        octets=octets,
    )


def result(receipt, assertion_id):
    entry = next((x for x in validate_receipt(receipt) if x.assertion_id == assertion_id), None)
    if entry is None:
        raise RuntimeError(f"missing validator assertion {assertion_id}")
    return entry.passed


class C6RIPyNativeNegativeTests(unittest.TestCase):
    def test_positive_control_preserves_non_utf8_raw_octets(self):
        receipt = build_receipt()
        self.assertEqual(receipt.received.raw_octets, SYNTHETIC_OCTETS)
        self.assertEqual(receipt.received.octet_length, len(SYNTHETIC_OCTETS))
        self.assertTrue(result(receipt, "R-VAL-005"))
        self.assertTrue(result(receipt, "R-VAL-010"))

    def test_invalid_status_values_are_rejected(self):
        receiver = build_receiver()
        for value in ("TRANSFERRED", "PASS", "FAIL", "CONFORMANT", "NON_CONFORMANT", None, 1):
            with self.subTest(value=value):
                with self.assertRaises(ReceiptConstructionError):
                    receiver.receive(
                        fixture=FIXTURE, method="synthetic",
                        octets=SYNTHETIC_OCTETS, status=value
                    )

    def test_missing_fixture_and_empty_method_are_rejected(self):
        receiver = build_receiver()
        with self.assertRaises(ReceiptConstructionError):
            receiver.receive(fixture=None, method="synthetic", octets=SYNTHETIC_OCTETS)
        with self.assertRaises(ReceiptConstructionError):
            receiver.receive(fixture=FIXTURE, method="", octets=SYNTHETIC_OCTETS)

    def test_text_hex_and_base64_are_not_raw_octet_inputs(self):
        receiver = build_receiver()
        for value in (
            SYNTHETIC_OCTETS.decode("latin1"),
            SYNTHETIC_OCTETS.hex(),
            base64.b64encode(SYNTHETIC_OCTETS).decode("ascii"),
        ):
            with self.subTest(value_kind=type(value).__name__):
                with self.assertRaises(ReceiptConstructionError):
                    receiver.receive(fixture=FIXTURE, method="synthetic", octets=value)

    def test_length_and_digest_tampering_fail_their_named_assertions(self):
        receipt = build_receipt()
        bad_length = dataclasses.replace(
            receipt,
            received=dataclasses.replace(
                receipt.received, octet_length=len(SYNTHETIC_OCTETS) + 1
            ),
        )
        self.assertFalse(result(bad_length, "R-VAL-004"))

        bad_digest = dataclasses.replace(
            receipt,
            received=dataclasses.replace(receipt.received, recomputed_sha256="0" * 64),
        )
        self.assertFalse(result(bad_digest, "R-VAL-005"))

    def test_wrong_schema_identity_or_version_fails_closed(self):
        receipt = build_receipt()
        self.assertFalse(result(dataclasses.replace(receipt, schema_id="WRONG"), "R-VAL-001"))
        self.assertFalse(result(dataclasses.replace(receipt, schema_version=2), "R-VAL-001"))

    def test_empty_fixture_identity_fails_validation(self):
        receipt = build_receiver().receive(
            fixture=FixtureIdentity("", ""),
            method="synthetic",
            octets=SYNTHETIC_OCTETS,
        )
        self.assertFalse(result(receipt, "R-VAL-002"))

    def test_incomplete_receiver_adapter_environment_provenance_fails(self):
        receipt = build_receipt()
        bad_receiver = dataclasses.replace(receipt.receiver, source_commit="")
        self.assertFalse(result(dataclasses.replace(receipt, receiver=bad_receiver), "R-VAL-007"))

        bad_adapter = dataclasses.replace(receipt.adapter, adapter_version="")
        self.assertFalse(result(dataclasses.replace(receipt, adapter=bad_adapter), "R-VAL-008"))

        bad_environment = dataclasses.replace(receipt.environment, runtime="")
        self.assertFalse(result(dataclasses.replace(receipt, environment=bad_environment), "R-VAL-009"))

    def test_serialized_receipt_preserves_base64_and_excludes_conformance_authority(self):
        value = json.loads(serialize_receipt(build_receipt()).decode("utf-8"))
        self.assertFalse(
            {"conformance_result", "verdict", "acceptance_state", "digest_output_state"}
            & set(value)
        )
        self.assertEqual(
            value["received"]["raw_octets"],
            base64.b64encode(SYNTHETIC_OCTETS).decode("ascii"),
        )


if __name__ == "__main__":
    unittest.main()
