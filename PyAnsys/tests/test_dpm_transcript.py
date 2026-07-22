from __future__ import annotations

import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.dpm_transcript import (  # noqa: E402
    SessionTranscriptCapture,
    track_one_injection_streamed,
)


DPM_SAMPLE = """DPM Iteration ....
number tracked = 2174, escaped = 2007, trapped = 5, incomplete = 4
Eulerian wall film particles:
absorbed = 159, splashed = 4

 Fate                        Zone   Zone Number                  Elapsed Time (s)
                             Name     Id               Min        Max        Avg    Std Dev
 ----------- -------------------- ------ ------ ---------- ---------- ---------- ----------
 Incomplete                                   4  1.906e-01  1.071e+01  2.820e+00  4.554e+00 injection-56 2092 injection-56 1037
 Absorbed                                   158  3.891e-03  3.228e+00  1.696e-01  3.293e-01 injection-56 1562 injection-56 1882
 Trapped                   bottom  50059      5  2.419e+00  5.943e+00  4.251e+00  1.443e+00 injection-56 2065 injection-56 1863
 Escaped              steamoutlet  50065   2007  8.084e-01  1.661e+01  1.481e+00  8.957e-01 injection-56 467 injection-56 1270

 (*)- Mass Transfer Summary -(*)
 Fate                        Zone   Zone      Mass Flow (kg/s)
                             Name     Id    Initial      Final     Change
 ----------- -------------------- ------ ---------- ---------- ----------
 Incomplete                               3.577e-04  3.577e-04  0.000e+00
 Absorbed                                 1.413e-02  1.413e-02  0.000e+00
 Trapped                   bottom  50059  4.472e-04  4.472e-04  0.000e+00
 Escaped              steamoutlet  50065  1.792e-01  1.792e-01  0.000e+00
 -----------                             ---------- ---------- ----------
 Net                                      1.941e-01  1.941e-01  0.000e+00
"""


class FakeTranscript:
    def __init__(self) -> None:
        self.is_streaming = True
        self.callbacks: dict[str, object] = {}
        self.next_id = 0

    def register_callback(self, callback, **_kwargs):
        callback_id = str(self.next_id)
        self.next_id += 1
        self.callbacks[callback_id] = callback
        return callback_id

    def unregister_callback(self, callback_id):
        self.callbacks.pop(callback_id, None)

    def start(self):
        self.is_streaming = True

    def stop(self):
        self.is_streaming = False

    def emit(self, text: str) -> None:
        for callback in list(self.callbacks.values()):
            callback(text)


class FakeSolver:
    def __init__(self) -> None:
        self.transcript = FakeTranscript()


class TranscriptCaptureTests(unittest.TestCase):
    def test_waits_for_complete_summary_and_writes_raw_file(self) -> None:
        solver = FakeSolver()

        def submit(_solver, _command):
            def emit() -> None:
                for line in DPM_SAMPLE.splitlines(keepends=True):
                    solver.transcript.emit(line)
                    time.sleep(0.001)

            threading.Thread(target=emit, daemon=True).start()
            return None

        item = {"index": 2, "name": "injection-56", "diameter_um": 56.0}
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / "raw.txt"
            with SessionTranscriptCapture(solver) as collector:
                with patch(
                    "pyansys_fluent.dpm_transcript.execute_tui",
                    side_effect=submit,
                ):
                    result = track_one_injection_streamed(
                        solver,
                        item,
                        collector,
                        timeout_seconds=2.0,
                        quiet_seconds=0.02,
                        raw_output_path=raw_path,
                    )

            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["completion"]["confirmed"])
            self.assertEqual(result["parsed"]["counts"]["tracked"], 2174)
            self.assertEqual(result["parsed"]["ewf_events"]["splashed"], 4)
            self.assertAlmostEqual(result["closure"]["injected_kg_s"], 0.1941)
            self.assertIn("Mass Transfer Summary", raw_path.read_text(encoding="utf-8"))

    def test_timeout_blocks_next_submission(self) -> None:
        solver = FakeSolver()
        item = {"index": 0, "name": "injection-timeout", "diameter_um": 5.0}
        with SessionTranscriptCapture(solver) as collector:
            with patch(
                "pyansys_fluent.dpm_transcript.execute_tui",
                return_value=None,
            ):
                result = track_one_injection_streamed(
                    solver,
                    item,
                    collector,
                    timeout_seconds=0.05,
                    quiet_seconds=0.01,
                )
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["completion"]["confirmed"])
        self.assertFalse(result["completion"]["safe_to_submit_next"])


if __name__ == "__main__":
    unittest.main()
