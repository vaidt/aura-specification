from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "stage_c"))

import python_jcs_probe as probe  # noqa: E402

FIXTURE_PATH = ROOT / "fixtures" / "corpus" / "CANONICAL-003_jcs_full_discriminator.json"
EXPECTED_PATH = (
    ROOT / "fixtures" / "corpus" / "CANONICAL-003_jcs_full_discriminator.expected.jcs"
)
EXPECTED_SHA256 = "9fb648c388c4485575d25c1d6171ba691fec51c1b433b11f4d61197bbe2a5509"
EXPECTED_LEAF_SHA256 = "38672ea2bd0ea87b2446efce8d4ba4adeb822e0baaecee4a54b73179198d2b3e"
TEST_SOURCE_COMMIT = "991274eed57d5b3308b0607feeb4d01e6a485974"


class StrictInputTests(unittest.TestCase):
    def test_duplicate_json_member_is_rejected(self) -> None:
        with self.assertRaisesRegex(probe.ProbeInputError, "duplicate JSON member"):
            probe.parse_json_bytes(b'{"k":1,"k":2}')

    def test_nan_and_infinity_are_rejected(self) -> None:
        for raw in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
            with self.subTest(raw=raw):
                with self.assertRaises(probe.ProbeInputError):
                    probe.parse_json_bytes(raw)

    def test_invalid_utf8_is_rejected(self) -> None:
        with self.assertRaises(probe.ProbeInputError):
            probe.parse_json_bytes(b'{"x":"\xff"}')

    def test_pointer_outside_v01_surface_is_rejected(self) -> None:
        request = {
            "schema": probe.SCHEMA_REQUEST,
            "run_id": "unit-test",
            "operation": "jcs.canonicalize",
            "fixture_id": "CANONICAL-003",
            "input_path": "fixtures/corpus/CANONICAL-003_jcs_full_discriminator.json",
            "json_pointer": "/",
            "source_commit": TEST_SOURCE_COMMIT,
        }
        with self.assertRaisesRegex(probe.ProbeInputError, "only JSON Pointer"):
            probe.validate_request(request)


class CanonicalOutputTests(unittest.TestCase):
    def test_python_jcs_engine_matches_discriminator_bytes_exactly(self) -> None:
        actual = probe.canonicalize_protocol_object(
            FIXTURE_PATH.read_bytes(), "CANONICAL-003"
        )
        expected = EXPECTED_PATH.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 577)
        self.assertFalse(actual.endswith(b"\n"))
        self.assertEqual(hashlib.sha256(actual).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(hashlib.sha256(b"\x00" + actual).hexdigest(), EXPECTED_LEAF_SHA256)

    def test_mismatched_fixture_identity_fails_closed(self) -> None:
        with self.assertRaisesRegex(probe.ProbeInputError, "identity mismatch"):
            probe.canonicalize_protocol_object(FIXTURE_PATH.read_bytes(), "WRONG-FIXTURE")

    def test_script_does_not_alias_bc02_receiver(self) -> None:
        source = (ROOT / "scripts" / "stage_c" / "python_jcs_probe.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("from conformance.boundary.ri_py_adapter import", source)
        self.assertNotIn("from conformance.boundary.ri_py_receiver import", source)


class OuterContractTests(unittest.TestCase):
    def test_request_generates_raw_bytes_and_non_authoritative_response(self) -> None:
        request = {
            "schema": probe.SCHEMA_REQUEST,
            "run_id": "unit-test-001",
            "operation": "jcs.canonicalize",
            "fixture_id": "CANONICAL-003",
            "input_path": "fixtures/corpus/CANONICAL-003_jcs_full_discriminator.json",
            "json_pointer": "/protocol_object",
            "source_commit": TEST_SOURCE_COMMIT,
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            request_path = tmp_path / "request.json"
            response_path = tmp_path / "response.json"
            output_path = tmp_path / "canonical.bin"
            request_path.write_bytes(json.dumps(request).encode("utf-8"))

            code = probe.execute_request(
                request_path, response_path, output_path, repo_root=ROOT
            )

            self.assertEqual(code, 0)
            self.assertEqual(output_path.read_bytes(), EXPECTED_PATH.read_bytes())
            response = json.loads(response_path.read_bytes())
            self.assertEqual(response["schema"], probe.SCHEMA_RESPONSE)
            self.assertEqual(response["run_id"], "unit-test-001")
            self.assertEqual(response["execution_status"], "COMPLETED")
            self.assertEqual(response["authority"], "NONE")
            self.assertEqual(response["adapter"]["source_commit"], TEST_SOURCE_COMMIT)
            self.assertEqual(response["adapter"]["engine_distribution"], "rfc8785")
            self.assertEqual(response["adapter"]["engine_version"], "0.1.4")
            self.assertEqual(response["output"]["octet_length"], 577)
            self.assertEqual(response["output"]["sha256"], EXPECTED_SHA256)
            for prohibited in (
                "conformance_result",
                "acceptance_state",
                "protocol_verdict",
                "ratification",
                "release_decision",
            ):
                self.assertNotIn(prohibited, response)


if __name__ == "__main__":
    unittest.main()
