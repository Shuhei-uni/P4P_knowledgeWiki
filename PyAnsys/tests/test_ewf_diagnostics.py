from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.dpm_reports import (  # noqa: E402
    dpm_flow_closure,
    parse_particle_track_summary,
)
from pyansys_fluent.ewf_diagnostics import (  # noqa: E402
    parse_film_flux_output,
    parse_report_compute_output,
)


DPM_SAMPLE = r"""
DPM Iteration ....
number tracked = 2170, escaped = 435, trapped = 54
Eulerian wall film particles:
absorbed = 1681

 Fate                        Zone   Zone Number                  Elapsed Time (s)
                             Name     Id               Min        Max        Avg    Std Dev
 ----------- -------------------- ------ ------ ---------- ---------- ---------- ----------
 Absorbed                                  1681  5.722e-03  6.070e+00  2.505e-01  5.351e-01 injection-348 963 injection-348 818
 Trapped                   bottom  50059     54  1.375e+00  5.235e+00  2.501e+00  9.350e-01 injection-348 2128 injection-348 100
 Escaped              steamoutlet  50065    435  9.509e-01  5.240e+00  1.806e+00  6.975e-01 injection-348 2133 injection-348 68

 (*)- Mass Transfer Summary -(*)
 Fate                        Zone   Zone      Mass Flow (kg/s)
                             Name     Id    Initial      Final     Change
 ----------- -------------------- ------ ---------- ---------- ----------
 Absorbed                                 3.624e+00  3.624e+00  0.000e+00
 Trapped                   bottom  50059  1.164e-01  1.164e-01  0.000e+00
 Escaped              steamoutlet  50065  9.377e-01  9.377e-01  0.000e+00
 -----------                             ---------- ---------- ----------
 Net                                      4.678e+00  4.678e+00  0.000e+00
"""


class DpmParserTests(unittest.TestCase):
    def test_parse_summary_and_mass_rows(self) -> None:
        parsed = parse_particle_track_summary(DPM_SAMPLE)
        self.assertEqual(parsed["counts"]["tracked"], 2170)
        self.assertEqual(parsed["counts"]["escaped"], 435)
        self.assertEqual(parsed["counts"]["trapped"], 54)
        self.assertEqual(parsed["ewf_events"]["absorbed"], 1681)
        self.assertEqual(len(parsed["fate_rows"]), 3)
        self.assertEqual(len(parsed["mass_transfer_rows"]), 4)

    def test_dpm_closure(self) -> None:
        closure = dpm_flow_closure(parse_particle_track_summary(DPM_SAMPLE))
        self.assertEqual(closure["status"], "computed")
        self.assertAlmostEqual(closure["injected_kg_s"], 4.678)
        self.assertAlmostEqual(closure["terminal_sum_kg_s"], 4.6781)
        self.assertAlmostEqual(closure["residual_kg_s"], -0.0001, places=7)


class EwfParserTests(unittest.TestCase):
    def test_report_compute_output(self) -> None:
        raw = """
 Report Name                Value Unit
 -------------------  ------------------- -----
 ewfdiag-film-mass-total          0.074310961 [kg]
"""
        parsed = parse_report_compute_output(raw, "ewfdiag-film-mass-total")
        self.assertAlmostEqual(parsed["value"], 0.074310961)
        self.assertEqual(parsed["unit"], "kg")

    def test_film_flux_output(self) -> None:
        raw = """
                         mixture
             Film Mass Flow Rate               [kg/s]
-------------------------------- --------------------
                     liquidinlet                   -0
                      steaminlet                   -0
                     steamoutlet       -6.5910833e-06
                ---------------- --------------------
                             Net       -6.5910833e-06
"""
        parsed = parse_film_flux_output(raw)
        self.assertAlmostEqual(parsed["by_zone_kg_s"]["steamoutlet"], -6.5910833e-06)
        self.assertAlmostEqual(parsed["net_kg_s"], -6.5910833e-06)


if __name__ == "__main__":
    unittest.main()
