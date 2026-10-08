"""Check the one-change contract and event-to-update association offline."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/setup"), str(ROOT / "scripts/analysis")]
from run_phase72a_stage4_dpm_cadence import cadence_parameters
from analyze_phase72a_stage4_dpm_cadence import event_positions


class CadenceTests(unittest.TestCase):
    def test_only_tracking_interval_changes(self):
        parent = {"iters-per-dpm-step": 20, "secondary-phase-mode": 1, "mom-equation?": True, "timestep-max": 1e-5}
        child = cadence_parameters(parent)
        self.assertEqual({key for key in parent if child[key] != parent[key]}, {"iters-per-dpm-step"})
        self.assertEqual(parent["iters-per-dpm-step"], 20)
        with self.assertRaises(RuntimeError):
            cadence_parameters({**parent, "iters-per-dpm-step": 40})


    def test_event_precedes_corresponding_film_update(self):
        line = "Film time = 1.0e-1 with timestep = 1.0e-5, (max_cfl: 0.1)\n"
        self.assertEqual(event_positions(line + "DPM Iteration ....\n" + line + line + "DPM Iteration ....\n" + line), [2, 4])
        with self.assertRaises(ValueError):
            event_positions(line + "DPM Iteration ....\n")
        with self.assertRaises(ValueError):
            event_positions("DPM Iteration ....\nDPM Iteration ....\n" + line)


if __name__ == "__main__":
    unittest.main()
