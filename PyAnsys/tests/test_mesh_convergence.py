from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from pyansys_fluent.mesh_convergence import (  # noqa: E402
    generalized_richardson,
    monitor_stability,
    parse_mesh_check,
    parse_mesh_quality,
    parse_mesh_size,
    parse_named_report_rows,
    resolve_zone_roles,
)


class ZoneMappingTests(unittest.TestCase):
    def test_normalized_unique_aliases_resolve(self):
        available = {
            "liquid-inlet": "mass_flow_inlet",
            "steam_inlet": "mass_flow_inlet",
            "steamoutlet": "pressure_outlet",
        }
        result = resolve_zone_roles(
            available,
            {
                "liquidinlet": ("liquid-inlet",),
                "steaminlet": ("steam_inlet",),
                "steamoutlet": (),
            },
        )
        self.assertEqual(result["liquidinlet"]["name"], "liquid-inlet")

    def test_missing_role_fails(self):
        with self.assertRaisesRegex(RuntimeError, "missing required zone role"):
            resolve_zone_roles({"steaminlet": "mass_flow_inlet"}, {"liquidinlet": ()})

    def test_ambiguous_role_fails(self):
        with self.assertRaisesRegex(RuntimeError, "ambiguous zone role"):
            resolve_zone_roles(
                {"liquid-inlet": "a", "liquid_inlet": "b"},
                {"liquidinlet": ("liquid-inlet", "liquid_inlet")},
            )


class FluentTextParsingTests(unittest.TestCase):
    def test_mesh_reports_parse(self):
        size = """Level Cells Faces Nodes Partitions\n0 3609102 7273531 627514 16\n"""
        check = """minimum volume (m3): 3.49e-09\nmaximum volume (m3): 1.98e-05\n total volume (m3): 2.265799e+01\nminimum face area (m2): 2.9e-06\nmaximum face area (m2): 1.7e-03\n"""
        quality = """Minimum Orthogonal Quality = 1.91653e-01\nMaximum Aspect Ratio = 1.84352e+01\n"""
        self.assertEqual(parse_mesh_size(size)["cells"], 3_609_102)
        self.assertAlmostEqual(parse_mesh_check(check)["domain_volume_m3"], 22.65799)
        self.assertAlmostEqual(parse_mesh_quality(quality)["minimum_orthogonal_quality"], 0.191653)

    def test_named_report_rows_preserve_sign(self):
        text = " liquidinlet 116.92\n steamoutlet -0.22993056\n"
        parsed = parse_named_report_rows(text, ["liquidinlet", "steamoutlet"])
        self.assertEqual(parsed["liquidinlet"], 116.92)
        self.assertLess(parsed["steamoutlet"], 0)


class StabilityAndGciTests(unittest.TestCase):
    def test_final_window_stability(self):
        rows = [
            {"iteration": 2500, "pressure_drop_pa": 100.0},
            {"iteration": 2750, "pressure_drop_pa": 100.2},
            {"iteration": 3000, "pressure_drop_pa": 100.1},
        ]
        result = monitor_stability(rows, ["pressure_drop_pa"])
        self.assertLess(result["pressure_drop_pa"]["drift_percent"], 0.5)

    def test_generalized_unequal_ratio_recovers_order(self):
        exact = 10.0
        order = 2.0
        h3, h2, h1 = 0.15, 0.10, 0.07
        result = generalized_richardson(
            (h3, exact + h3**order),
            (h2, exact + h2**order),
            (h1, exact + h1**order),
        )
        self.assertEqual(result["status"], "gci_computed")
        self.assertAlmostEqual(result["observed_order"], order, places=6)
        self.assertAlmostEqual(result["richardson_extrapolated"], exact, places=8)

    def test_oscillatory_sequence_is_percentage_only(self):
        result = generalized_richardson((0.15, 10.0), (0.10, 11.0), (0.07, 10.5))
        self.assertEqual(result["status"], "percentage_change_only")
        self.assertFalse(result["monotonic"])
        self.assertTrue(math.isfinite(result["pct_medium_fine"]))


if __name__ == "__main__":
    unittest.main()
