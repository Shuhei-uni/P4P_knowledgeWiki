"""Safety and finite-horizon scheduling checks for the E3 recorder."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from pyansys_fluent.phase07b_spike_monitor import Phase07bSpikeMonitor, SpikeSchedule


class SpikeMonitorTests(unittest.TestCase):
    def test_threshold_sampling_keeps_followups_without_retriggering_band(self):
        schedule = SpikeSchedule()
        self.assertFalse(schedule.reasons(2701, 499.9))
        self.assertIn('speed_ge_500_m_s_first_in_250_iteration_band', schedule.reasons(2702, 500))
        self.assertEqual(schedule.reasons(2703, 1000), ['event_followup'])
        self.assertFalse(schedule.reasons(2704, 2000))
        self.assertEqual(schedule.reasons(2707, 20), ['event_followup'])
        self.assertIn('speed_ge_500_m_s_first_in_250_iteration_band', schedule.reasons(2751, 501))

    def test_persistent_extreme_speed_has_bounded_capture_and_no_extension(self):
        schedule = SpikeSchedule()
        captures = [n for n in range(1, 5001) if schedule.reasons(n, 1000)]
        self.assertEqual(len(schedule.used_bins), 20)
        self.assertLessEqual(len(captures), 74)
        self.assertTrue(all(n <= 5000 for n in schedule.followups))
        self.assertTrue({50, 2600, 2700, 2800, 5000}.issubset(captures))

    def test_missed_iteration_latches_evidence_failure_before_reading_fluent(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'diagnostics'
            monitor = Phase07bSpikeMonitor(SimpleNamespace(), ['fluid'], directory)
            with self.assertRaises(AssertionError):
                monitor.capture(None, 2, {})
            self.assertEqual(monitor.last_iteration, 0)
            self.assertEqual(json.loads((directory / 'manifest.json').read_text())['error']['iteration'], 2)
            with self.assertRaises(AssertionError):
                monitor.assert_complete(2)
            monitor.close()


if __name__ == '__main__':
    unittest.main()
