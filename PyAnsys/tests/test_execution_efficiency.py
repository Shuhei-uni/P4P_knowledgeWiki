"""Offline regressions from setup/run failures; no controller import or Fluent calls."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent.execution_contract import (compare_state, native_transcript,
    probe_runtime, require_named_objects, require_state_same, should_check_health,
    verify_drain_probe, windows_path)
from pyansys_fluent.workflow_evidence import campaign_status, json_pointer, markdown_section, tail_file

ROOT = Path(__file__).resolve().parents[2]


class Comparison(unittest.TestCase):
    def test_native_rounding_requires_an_explicit_path(self):
        before = {"inlet": 34.999287499999994, "flag": True}
        after = {"inlet": 34.99928749999999, "flag": True}
        self.assertEqual(compare_state(after, before)["status"], "FAIL")
        result = require_state_same(after, before, numeric_paths=[("inlet",)])
        self.assertEqual(len(result["normalization"]), 1)
        self.assertEqual(after["inlet"], 34.99928749999999)

    def test_real_change_flags_and_nonfinite_values_fail(self):
        for a, e, rules in [(True, 1, {}), (False, True, {}), (1.2, 1.0, {"numeric_paths": [()]}),
                             (float("nan"), float("nan"), {"numeric_paths": [()]}),
                             (float("inf"), float("inf"), {})]:
            with self.subTest(actual=a):
                self.assertEqual(compare_state(a, e, **rules)["status"], "FAIL")

    def test_windows_paths_need_explicit_rules_and_verified_working_directory(self):
        a = {"file": r"reports\flow.out", "hook": "CaseSensitive"}
        e = {"file": "C:/Runs/reports/flow.out", "hook": "CaseSensitive"}
        self.assertEqual(compare_state(a, e)["status"], "FAIL")
        result = require_state_same(a, e, path_paths=[("file",)], working_directory=r"C:\Runs")
        self.assertEqual(len(result["normalization"]), 1)
        with self.assertRaises(ValueError): windows_path(r"C:reports\flow.out", working_directory=r"C:\Runs")
        with self.assertRaises(ValueError): windows_path("relative.out")
        self.assertEqual(windows_path(r"C:\Runs\\reports\FLOW.out"), windows_path("c:/runs/reports/flow.out"))

    def test_missing_keys_and_undeclared_changes_fail(self):
        for actual in [{"x": 1}, {"x": 1, "hook": "changed"}]:
            self.assertEqual(compare_state(actual, {"x": 1, "hook": "original"})["status"], "FAIL")


class Transcript(unittest.TestCase):
    def settings(self):
        file = NS(start_transcript=Mock(), stop_transcript=Mock())
        file.start_transcript.is_active.return_value = True
        return file

    def test_two_batches_have_exactly_two_start_stop_pairs(self):
        file = self.settings(); calls = []
        file.start_transcript.side_effect = lambda **kw: calls.append("start")
        file.stop_transcript.side_effect = lambda: calls.append("stop")
        for _ in range(2):
            with native_transcript(file, "server-local.trn"): calls.append("solve")
        self.assertEqual(calls, ["start", "solve", "stop"] * 2)

    def test_cleanup_keeps_original_solver_error(self):
        file = self.settings(); file.stop_transcript.side_effect = RuntimeError("cleanup")
        with self.assertRaisesRegex(ValueError, "original solve"):
            with native_transcript(file, "server-local.trn"): raise ValueError("original solve")

    def test_inactive_start_is_reconciled_once_or_rejects_before_solve(self):
        file = self.settings(); file.start_transcript.is_active.return_value = False
        file.stop_transcript.is_active.return_value = False
        with self.assertRaises(RuntimeError):
            with native_transcript(file, "x"): self.fail("solve should not run")
        file.start_transcript.assert_not_called()
        file.stop_transcript.is_active.return_value = True
        with native_transcript(file, "x"): pass
        self.assertEqual(file.stop_transcript.call_count, 2)


class Preflight(unittest.TestCase):
    def proof(self):
        return {"setup_identity": "case-and-drain-hash", "direct_film_drain": True,
                "native_evidence_verified": True, "evidence_paths": ["accepted-native-proof.json"],
                "film_start_s": 0.1, "film_end_s": 0.10002, "drained_mass_kg": 0.0001,
                "ledger_error_percent": 0.01, "ledger_limit_percent": 0.1,
                "bulk_equations": {k: False for k in ("drift", "flow", "ke", "mp")},
                "bulk_fields_unchanged": True}

    def test_direct_drain_requires_functional_evidence(self):
        result = verify_drain_probe(self.proof(), setup_identity="case-and-drain-hash", frozen_bulk=True)
        self.assertEqual(result["status"], "PASS")
        for key, value in [("direct_film_drain", False), ("film_end_s", 0.1),
                           ("drained_mass_kg", 0), ("bulk_fields_unchanged", False),
                           ("ledger_error_percent", 1), ("native_evidence_verified", False),
                           ("bulk_equations", {"flow": False}), ("drained_mass_kg", float("nan")),
                           ("setup_identity", "another-case")]:
            with self.subTest(key=key):
                p = self.proof(); p[key] = value
                self.assertEqual(verify_drain_probe(p, setup_identity="case-and-drain-hash",
                                                  frozen_bulk=True)["status"], "UNVERIFIED")

    def test_missing_or_duplicate_objects_fail_before_build(self):
        require_named_objects(["a", "b"], ["a"])
        for names in [["a"], ["a", "a", "b"]]:
            with self.assertRaises(RuntimeError): require_named_objects(names, ["a", "b"])

    def test_explicit_interpreter_is_bounded_and_missing_dependency_is_reported(self):
        self.assertEqual(probe_runtime(sys.executable, ["json"])["status"], "PASS")
        self.assertEqual(probe_runtime(sys.executable, ["missing_p4p_test_module"])["status"], "UNAVAILABLE")
        with patch("pyansys_fluent.execution_contract.subprocess.run", side_effect=subprocess.TimeoutExpired("probe", 1)) as run:
            self.assertEqual(probe_runtime("explicit-python", timeout=1)["status"], "UNAVAILABLE")
            self.assertEqual(run.call_args.kwargs["timeout"], 1)

    def test_persistent_event_does_not_trigger_health_every_poll(self):
        event = (1, "CONTROLLER_STOPPED", "342k", 3800)
        self.assertTrue(should_check_health(30, 0, event, None))
        self.assertFalse(should_check_health(60, 30, event, event))
        self.assertTrue(should_check_health(330, 30, event, event))
        self.assertTrue(should_check_health(60, 30, (2, *event[1:]), event))


class Evidence(unittest.TestCase):
    def test_json_pointer_and_one_markdown_section(self):
        self.assertEqual(json_pointer({"a/b": {"~key": [3]}}, "/a~1b/~0key/0"), 3)
        with self.assertRaises(ValueError): json_pointer([3], "/-1")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "setup.md"; p.write_text("# Setup\n## Schedule\n10\n### Ramp\n20\n```md\n## Fake heading\n```\n## Evidence\n30\n")
            result = markdown_section(p, "Schedule")
            self.assertIn("Ramp", result["text"]); self.assertNotIn("Evidence", result["text"])
            self.assertEqual(result["start_line"], 2)
            with self.assertRaises(ValueError): markdown_section(p, "absent")
            with self.assertRaises(ValueError): markdown_section(p, "Fake heading")

    def test_tail_reads_a_bounded_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "native.txt"; p.write_text("unneeded\n" * 10000 + "42 1e-4 2e-4\n")
            text, age = tail_file(p, max_bytes=128)
            self.assertLessEqual(len(text.encode()), 128); self.assertIn("42 1e-4", text)

    def test_status_separates_observed_and_verified_and_never_queries_fluent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); live = p / "live.txt"; live.write_text("4100 1e-4 2e-4\n")
            (p / "desktop-controller.json").write_text(json.dumps({"pid": 123, "server_id": "3", "live_transcript": str(live)}))
            (p / "campaign-manifest.json").write_text(json.dumps({"active_mesh": "342k", "status": "RUNNING"}))
            (p / "342k-run.json").write_text(json.dumps({"verified_native_end": 3800, "active_target": 4800,
                                                        "latest_pair": {"native_iteration": 3800}}))
            with patch("pyansys_fluent.workflow_evidence.subprocess.run") as run:
                result = campaign_status(p)
                run.assert_not_called()
            self.assertEqual(result["last_streamed_iteration"], 4100)
            self.assertEqual(result["verified_native_end"], 3800)
            self.assertEqual(result["active_target"], 4800)

    def test_cli_returns_valid_small_json_when_selection_exceeds_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "large.json"; p.write_text(json.dumps({"large": "x" * 10000}))
            result = subprocess.run([sys.executable, str(ROOT / "PyAnsys/tools/workflow_evidence.py"),
                                     "--max-chars", "300", "json", str(p), "--pointer", "/large"],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "OUTPUT_LIMIT")
            self.assertLess(len(result.stdout), 300)


class StagedIntegration(unittest.TestCase):
    def test_both_staged_runners_use_shared_checks_without_importing_controllers(self):
        for name in ("run_phase9_mesh_startup.py", "run_phase9_server4_2_6M.py"):
            with self.subTest(runner=name):
                path = ROOT / "PyAnsys/workflow_updates/20261008/files/PyAnsys/scripts/setup" / name
                tree = ast.parse(path.read_text())
                functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and
                             n.name in {"require_setup_same", "native_batch_transcript"}]
                namespace = {"native_transcript": native_transcript, "require_state_same": require_state_same}
                exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), namespace)
                flow = {"boundary_conditions": {"mass_flow_inlet": {}}}
                for zone, phase in [("liquidinlet", "phase-2"), ("steaminlet", "phase-1")]:
                    flow["boundary_conditions"]["mass_flow_inlet"][zone] = {"phase": {phase: {"momentum": {"mass_flow_rate": {"value": 34.999287499999994}}}}}
                after = copy.deepcopy(flow)
                after["boundary_conditions"]["mass_flow_inlet"]["steaminlet"]["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"] = 34.99928749999999
                self.assertEqual(namespace["require_setup_same"](after, flow)["status"], "PASS")
                file = NS(start_transcript=Mock(), stop_transcript=Mock())
                file.start_transcript.is_active.return_value = True
                with namespace["native_batch_transcript"](NS(settings=NS(file=file)), "local.trn"): pass
                file.stop_transcript.assert_called_once()

    def test_both_staged_watchers_use_timer_or_new_event_health_checks(self):
        for name in ("watch_phase9_campaign.py", "watch_phase9_server4.py"):
            path = ROOT / "PyAnsys/workflow_updates/20261008/files/PyAnsys/scripts/orchestration" / name
            tree = ast.parse(path.read_text())
            health_ifs = [n for n in ast.walk(tree) if isinstance(n, ast.If) and
                          any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "health"
                              for node in n.body for c in ast.walk(node))]
            self.assertTrue(any(isinstance(n.test, ast.Call) and n.test.func.id == "should_check_health" for n in health_ifs))


if __name__ == "__main__":
    unittest.main()
