from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_C = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "fixtures" / "corpus" / "JCS-MULTIVECTOR-MANIFEST-v0.1-DRAFT.json"
sys.path.insert(0, str(STAGE_C))

import python_jcs_probe as probe  # noqa: E402


class JcsMultiVectorCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_bytes())
        cls.vectors = cls.manifest["vectors"]

    def _repo_path(self, value: str) -> Path:
        candidate = Path(value)
        self.assertFalse(candidate.is_absolute(), f"absolute corpus path prohibited: {value}")
        self.assertNotIn("..", candidate.parts, f"parent traversal prohibited: {value}")
        resolved = (ROOT / candidate).resolve()
        self.assertTrue(resolved == ROOT or ROOT in resolved.parents, f"path escapes root: {value}")
        return resolved

    def test_manifest_is_explicitly_non_normative_and_has_unique_ids(self) -> None:
        self.assertEqual(self.manifest["schema"], "AURA-STAGE-C-JCS-MULTIVECTOR-MANIFEST/0.1")
        self.assertEqual(self.manifest["status"], "DRAFT_NON_NORMATIVE")
        self.assertEqual(self.manifest["normative_effect"], "NONE")
        self.assertEqual(self.manifest["governance_effect"], "NONE")
        self.assertEqual(self.manifest["release_effect"], "NONE")
        ids = [item["fixture_id"] for item in self.vectors]
        self.assertEqual(len(ids), 6, "expected five added vectors plus frozen CANONICAL-003 baseline")
        self.assertEqual(len(ids), len(set(ids)), "fixture IDs must be unique")
        self.assertIn("CANONICAL-003", ids)

    def test_committed_inputs_and_expected_octets_match_manifest(self) -> None:
        for vector in self.vectors:
            with self.subTest(fixture_id=vector["fixture_id"]):
                input_path = self._repo_path(vector["input_path"])
                expected_path = self._repo_path(vector["expected_path"])
                input_bytes = input_path.read_bytes()
                expected_bytes = expected_path.read_bytes()
                self.assertEqual(hashlib.sha256(input_bytes).hexdigest(), vector["input_sha256"])
                self.assertEqual(hashlib.sha256(expected_bytes).hexdigest(), vector["expected_sha256"])
                self.assertEqual(len(expected_bytes), vector["expected_octet_length"])
                self.assertFalse(expected_bytes.endswith(b"\n"), "oracle bytes must not include a trailing LF")
                parsed = probe.parse_json_bytes(input_bytes)
                self.assertEqual(parsed.get("fixture_id"), vector["fixture_id"])
                self.assertIn("protocol_object", parsed)

    def test_python_jcs_engine_matches_every_frozen_oracle(self) -> None:
        for vector in self.vectors:
            with self.subTest(fixture_id=vector["fixture_id"]):
                input_path = self._repo_path(vector["input_path"])
                expected_path = self._repo_path(vector["expected_path"])
                actual = probe.canonicalize_protocol_object(
                    input_path.read_bytes(), vector["fixture_id"]
                )
                expected = expected_path.read_bytes()
                self.assertEqual(actual, expected)
                self.assertEqual(len(actual), vector["expected_octet_length"])
                self.assertEqual(hashlib.sha256(actual).hexdigest(), vector["expected_sha256"])


if __name__ == "__main__":
    unittest.main()
