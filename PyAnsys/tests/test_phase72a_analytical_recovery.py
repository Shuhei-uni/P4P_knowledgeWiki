"""Offline safety checks for recovery after Server 1 closed during retrieval."""

import hashlib
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/setup"))
import run_phase72a_stage4_analytical as runner


class AnalyticalRecoveryTests(unittest.TestCase):
    def test_terminal_capture_closes_only_its_own_report_writers(self):
        state = {"own": {"file_name": "C:/film/mass.out", "active": True, "report_defs": ["mass"]},
                 "other": {"file_name": "C:/other/mass.out", "active": True, "report_defs": ["other"]}}
        files = Mock()
        files.get_state.side_effect = [state, {**state, "own": {**state["own"], "active": False}}]
        solver = SimpleNamespace(settings=SimpleNamespace(solution=SimpleNamespace(
            monitor=SimpleNamespace(report_files=files))))
        closed = runner.close_terminal_report_files(solver, {"mass": r"C:\film\mass.out"})
        self.assertEqual(closed, ["own"])
        files.set_state.assert_called_once_with({"own": {"active": False}})

    def test_native_case_relative_report_paths_keep_writer_identity(self):
        state = {"own": {"file_name": "film//mass.out", "active": True, "report_defs": ["mass"]}}
        files = Mock()
        files.get_state.side_effect = [state, {"own": {**state["own"], "active": False}}]
        solver = SimpleNamespace(settings=SimpleNamespace(solution=SimpleNamespace(
            monitor=SimpleNamespace(report_files=files))))
        self.assertEqual(runner.close_terminal_report_files(solver, {"mass": "C:/film/mass.out"}), ["own"])

    def test_oversized_hash_command_is_rejected_before_any_rpc(self):
        solver = Mock()
        with patch.object(runner, "remote_file_exists") as remote:
            with self.assertRaisesRegex(ValueError, "too long"):
                runner.checked_remote_sha256(solver, "C:/" + "a" * 2000, "C:/scratch.txt")
            remote.assert_not_called()
        solver.scheme.eval.assert_not_called()

    def test_one_file_checksum_has_no_bulk_script(self):
        solver = Mock()
        solver.scheme.eval.return_value = 0
        with patch.object(runner, "remote_file_exists", side_effect=[True, False]), \
                patch.object(runner, "read_text", return_value="a" * 64):
            result = runner.checked_remote_sha256(solver, "C:/film.out", "C:/scratch.txt")
            self.assertEqual(result, "a" * 64)
        expression = solver.scheme.eval.call_args[0][0]
        codes = re.search(r"'\((.*?)\)\)\)\)$", expression).group(1)
        command = "".join(chr(int(code)) for code in codes.split())
        self.assertEqual(command, 'cmd /c certutil -hashfile "C:/film.out" SHA256 > "C:/scratch.txt" 2>&1')
        self.assertNotIn("powershell", command.lower())

    def test_literal_windows_paths_survive_native_command_encoding(self):
        solver = Mock()
        solver.scheme.eval.return_value = 0
        path = r"C:\film\native-status.scm"
        scratch = r"C:\film\scratch\text-hash.txt"
        with patch.object(runner, "remote_file_exists", side_effect=[True, False]), \
                patch.object(runner, "read_text", return_value="a" * 64):
            runner.checked_remote_sha256(solver, path, scratch)
        expression = solver.scheme.eval.call_args[0][0]
        codes = re.search(r"'\((.*?)\)\)\)\)$", expression).group(1)
        command = "".join(chr(int(code)) for code in codes.split())
        self.assertIn(path, command)
        self.assertIn(scratch, command)
        self.assertNotIn("\n", command)
        self.assertNotIn("\t", command)

    def test_cmd_expansions_and_quotes_are_rejected_before_rpc(self):
        solver = Mock()
        with patch.object(runner, "remote_file_exists") as remote:
            for path in ['C:/a"b', "C:/%TEMP%/a", "C:/a!b", "C:/a\nb", "C:/a&b"]:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    runner.checked_remote_sha256(solver, path, "C:/scratch.txt")
            remote.assert_not_called()

    def test_unresolved_submission_prevents_another_solve_before_attach(self):
        for status in ["SUBMITTED_NATIVE", "SUBMITTING_NATIVE", "RECOVERY_REQUIRED"]:
            with self.subTest(status=status), patch.object(runner, "load", return_value={"status": status}), \
                    patch.object(runner, "attach") as attach:
                with self.assertRaises(AssertionError):
                    runner.submit("analytical10", 1000)
                attach.assert_not_called()

    def test_terminal_native_status_resolves_existing_pair(self):
        record = {"work": "C:/film/run", "start": 41483, "target": 41503, "count": 20}
        status = '((status . "HORIZON_REACHED_PENDING_VERIFICATION") (completed-updates . 20))'
        successful, pair = runner.terminal_pair(record, status)
        self.assertTrue(successful)
        self.assertEqual(pair["native_iteration"], 41503)
        self.assertTrue(pair["case"].endswith("final-N41503.cas.h5"))
        for invalid in ['((status . "RUNNING") (completed-updates . 20))',
                        '((status . "HORIZON_REACHED_PENDING_VERIFICATION") (completed-updates . 19))', ""]:
            with self.subTest(status=invalid), self.assertRaises(RuntimeError):
                runner.terminal_pair(record, invalid)

    def test_missing_data_does_not_replace_loaded_case(self):
        files = SimpleNamespace(read_case=Mock(), read_data=Mock())
        solver = SimpleNamespace(settings=SimpleNamespace(file=files))
        pair = {"case": "C:/film.cas.h5", "data": "C:/film.dat.h5", "native_iteration": 41503}
        with patch.object(runner, "remote_file_exists", side_effect=[True, False]):
            with self.assertRaises(FileNotFoundError):
                runner.reopen_recovery_pair(solver, pair)
        files.read_case.assert_not_called()
        files.read_data.assert_not_called()

    def test_interrupted_block_uses_matching_report_counts_not_requested_count(self):
        record = {"work": "C:/film/run", "start": 41503, "target": 43483, "count": 1980}
        status = ('((status . "EVIDENCE_OR_SOLVER_STOP") (completed-updates . 1980) '
                  '(thickness-history 41503 42924 1422 0.002 #t) '
                  '(courant-history 41503 42924 1422 0.03 #t))')
        successful, pair = runner.terminal_pair(record, status)
        self.assertFalse(successful)
        self.assertEqual(pair["native_iteration"], 42924)
        for invalid in [status.replace('42924 1422 0.03', '42925 1423 0.03'),
                        status.replace('1422 0.002', '1421 0.002'),
                        status.replace('0.002 #t', '0.002 #f')]:
            with self.subTest(status=invalid), self.assertRaises(RuntimeError):
                runner.terminal_pair(record, invalid)

    def test_future_native_journal_counts_reports_and_checks_requested_endpoint(self):
        from pathlib import PureWindowsPath
        code = runner.build_native_code(PureWindowsPath('C:/film/run'), 42924, 559, 1e-5)
        self.assertNotIn('(set! p72l-completed (+ p72l-completed steps))', code)
        self.assertIn('(expected-target (+ p72l-start p72l-completed steps))', code)
        self.assertIn('(min (list-ref p72l-h 1) (list-ref p72l-c 1))', code)
        self.assertIn('(p72l-classify p72l-h p72l-c expected-target)', code)
        self.assertIn('final-N43483', code)

    def test_recovery_loads_pair_and_checks_coordinate_without_iteration(self):
        calls = []
        files = SimpleNamespace(read_case=lambda **kw: calls.append(("case", kw["file_name"])),
                                read_data=lambda **kw: calls.append(("data", kw["file_name"])))
        solver = SimpleNamespace(settings=SimpleNamespace(file=files))
        pair = {"case": "C:/film.cas.h5", "data": "C:/film.dat.h5", "native_iteration": 41503}
        with patch.object(runner, "remote_file_exists", return_value=True), \
                patch.object(runner, "native_iteration", return_value=41503):
            runner.reopen_recovery_pair(solver, pair)
        self.assertEqual(calls, [("case", pair["case"]), ("data", pair["data"])])

    def test_native_line_endings_are_recovered_against_source_hash(self):
        source = b"iteration value\r\n41503 0.5\r\n"
        digest = hashlib.sha256(source).hexdigest()
        with tempfile.TemporaryDirectory() as folder, patch.object(runner, "read_text", return_value=source.decode().replace("\r\n", "\n")):
            target = Path(folder) / "courant.out"
            receipt = runner.store_verified_text(Mock(), "C:/courant.out", target, digest)
            self.assertEqual(target.read_bytes(), source)
            self.assertEqual(receipt["bytes"], len(source))

    def test_mismatched_transfer_does_not_create_or_overwrite_raw_evidence(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(runner, "read_text", return_value="altered"):
            target = Path(folder) / "courant.out"
            with self.assertRaisesRegex(RuntimeError, "bytes/hash"):
                runner.store_verified_text(Mock(), "C:/courant.out", target, "a" * 64)
            self.assertFalse(target.exists())
            target.write_bytes(b"retained raw evidence")
            with self.assertRaisesRegex(RuntimeError, "Immutable"):
                runner.store_verified_text(Mock(), "C:/courant.out", target, "a" * 64)
            self.assertEqual(target.read_bytes(), b"retained raw evidence")


if __name__ == "__main__":
    unittest.main()
