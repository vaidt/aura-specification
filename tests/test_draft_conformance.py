from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fix001 = load_module("check_fix001_evidence", ROOT / "scripts" / "check-fix001-evidence.py")
runner = load_module("run_draft_conformance", ROOT / "scripts" / "run-draft-conformance.py")


class Fix001GateTests(unittest.TestCase):
    def test_run_fix001_gate_happy_path_returns_all_conf_results(self) -> None:
        results = fix001.run_fix001_gate()
        self.assertEqual(set(results), set(fix001.FIX001_CONF_MESSAGES))

    def test_run_fix001_gate_detects_fixture_mismatch(self) -> None:
        fixture = fix001.load_json(fix001.FIXTURE_PATH)
        fixture["expected_output"]["decision"] = "DENY"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad-fix001.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            with mock.patch.object(fix001, "FIXTURE_PATH", path):
                with self.assertRaises(AssertionError):
                    fix001.run_fix001_gate()


class DraftRunnerTests(unittest.TestCase):
    def test_build_report_summary_counts(self) -> None:
        report = runner.build_report()
        self.assertEqual(len(report["results"]), 15)
        self.assertEqual(report["summary"]["PASS"], 7)
        self.assertEqual(report["summary"]["OPEN"], 2)
        self.assertEqual(report["summary"]["BLOCKED"], 4)
        self.assertEqual(report["summary"]["READY"], 2)

    def test_build_report_conf008_failure_result(self) -> None:
        fake_fix001_results = [
            runner.make_result(conf_id, "PASS", "ok") for conf_id in runner.FIX001_CONF_IDS
        ]

        with mock.patch.object(runner, "run_fix001_results", return_value=fake_fix001_results):
            with mock.patch.object(
                runner, "run_conf008_result", side_effect=RuntimeError("boom")
            ):
                report = runner.build_report()

        conf008 = next(result for result in report["results"] if result["id"] == "CONF-008")
        self.assertEqual(conf008["status"], "FAIL")
        self.assertIn("boom", conf008["note"])
        self.assertEqual(report["summary"]["FAIL"], 1)

    def test_run_fix001_results_failure_is_reported_as_failures(self) -> None:
        failing_gate = mock.Mock()
        failing_gate.run_fix001_gate.side_effect = RuntimeError("fix001 boom")

        with mock.patch.object(runner, "load_fix001_gate_module", return_value=failing_gate):
            results = runner.run_fix001_results()

        self.assertEqual({result["status"] for result in results}, {"FAIL"})
        self.assertEqual({result["id"] for result in results}, set(runner.FIX001_CONF_IDS))
        self.assertTrue(all("fix001 boom" in result["note"] for result in results))


if __name__ == "__main__":
    unittest.main()
