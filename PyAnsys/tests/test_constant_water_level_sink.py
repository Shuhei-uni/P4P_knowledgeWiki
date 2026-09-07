from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from pyansys_fluent.constant_water_level_sink import (
    adaptive_tau_from_inventory,
    bottom_inventory_from_sink,
    find_phase_for_material,
    integrated_sink_kg_s,
    liquid_mass_source,
    momentum_source,
    parse_zone_table,
    source_augmented_imbalance_percent,
    validate_sink_parameters,
)


class ConstantWaterLevelSinkTests(unittest.TestCase):
    def test_liquid_mass_source_sign_units_and_mask(self) -> None:
        self.assertAlmostEqual(liquid_mass_source(881.2, 0.25, 0.1, 1.0), -2203.0)
        self.assertEqual(liquid_mass_source(881.2, 0.25, 0.1, 0.0), 0.0)
        self.assertEqual(
            liquid_mass_source(
                881.2, 0.25, 0.1, 1.0, adjacent_to_bottom=False
            ),
            0.0,
        )
        self.assertAlmostEqual(liquid_mass_source(881.2, 1.5, 0.1, 1.0), -8812.0)

    def test_momentum_and_volume_integration(self) -> None:
        source = liquid_mass_source(800.0, 0.5, 2.0, 1.0)
        self.assertAlmostEqual(momentum_source(source, 3.0), -600.0)
        self.assertAlmostEqual(
            integrated_sink_kg_s([source, source], [0.2, 0.3]), -100.0
        )
        with self.assertRaises(ValueError):
            integrated_sink_kg_s([1.0], [1.0, 2.0])

    def test_source_augmented_balance_and_inventory(self) -> None:
        self.assertAlmostEqual(
            source_augmented_imbalance_percent(116.92, -116.92, 116.92), 0.0
        )
        self.assertAlmostEqual(
            source_augmented_imbalance_percent(116.92, -115.0, 116.92),
            1.6421484776,
        )
        self.assertAlmostEqual(bottom_inventory_from_sink(-5.0, 0.1, 0.05), 10.0)
        with self.assertRaises(ValueError):
            source_augmented_imbalance_percent(1.0, -1.0, 0.0)
        with self.assertRaises(ValueError):
            bottom_inventory_from_sink(-1.0, 0.1, 0.0)

    def test_adaptive_tau_feedback_is_bounded_and_dimensionally_consistent(self) -> None:
        self.assertAlmostEqual(
            adaptive_tau_from_inventory(2.3384, 116.92, 0.002, 0.2),
            0.02,
        )
        self.assertEqual(
            adaptive_tau_from_inventory(0.0, 116.92, 0.002, 0.2),
            0.2,
        )
        self.assertEqual(
            adaptive_tau_from_inventory(0.01, 116.92, 0.002, 0.2),
            0.002,
        )
        self.assertEqual(
            adaptive_tau_from_inventory(100.0, 116.92, 0.002, 0.2),
            0.2,
        )
        for invalid in (
            (1.0, 0.0, 0.002, 0.2),
            (1.0, 116.92, 0.0, 0.2),
            (1.0, 116.92, 0.2, 0.1),
            (math.nan, 116.92, 0.002, 0.2),
        ):
            with self.assertRaises(ValueError):
                adaptive_tau_from_inventory(*invalid)

    def test_zone_table_and_phase_resolution(self) -> None:
        table = """
          id  name                       type                material              kind
        ----  -------------------------  ------------------  --------------------  ----
        40050  fluid                      fluid               air                   cell
        50059  bottom                     wall                air                   face
        50065  steamoutlet                pressure-outlet                           face
        """
        parsed = parse_zone_table(table)
        self.assertEqual(parsed["bottom"], {"id": 50059, "type": "wall"})
        self.assertEqual(
            find_phase_for_material(
                {
                    "phase-1": "water-vapor-at-psep",
                    "phase-2": "water-liquid-at-psep",
                },
                "water-liquid-at-psep",
            ),
            "phase-2",
        )

    def test_parameter_validation(self) -> None:
        self.assertFalse(
            validate_sink_parameters(
                bottom_zone_id=50059,
                liquid_phase_index=1,
                tau_s=0.1,
                ramp=0.0,
                alpha_min=1.0e-12,
            )
        )
        errors = validate_sink_parameters(
            bottom_zone_id=-1,
            liquid_phase_index=-1,
            tau_s=math.nan,
            ramp=1.5,
            alpha_min=-0.1,
        )
        self.assertEqual(len(errors), 5)



if __name__ == "__main__":
    unittest.main()
