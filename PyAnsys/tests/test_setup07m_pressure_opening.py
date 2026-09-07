import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from run_setup07m_pressure_opening_campaign import (  # noqa: E402
    BRINE_FACE_REST_PRESSURE_PA,
    DYNAMIC_PRESSURE_PA,
    PRESSURES,
    TIME_STEPS_S,
    case_slug,
    configured_pressure_outlet_state,
    response_pattern_failures,
    scale_inlet_state,
)


class Setup07mPressureOpeningTests(unittest.TestCase):
    def test_pressure_bracket_is_symmetric_and_ordered(self):
        values = dict(PRESSURES)
        self.assertLess(values["low"], values["center"])
        self.assertLess(values["center"], values["high"])
        self.assertAlmostEqual(values["center"], BRINE_FACE_REST_PRESSURE_PA)
        self.assertAlmostEqual(values["center"] - values["low"], DYNAMIC_PRESSURE_PA)
        self.assertAlmostEqual(values["high"] - values["center"], DYNAMIC_PRESSURE_PA)

    def test_matrix_slugs_are_unique(self):
        slugs = {
            case_slug(label, dt_s)
            for label, _pressure in PRESSURES
            for dt_s in TIME_STEPS_S
        }
        self.assertEqual(len(slugs), 9)

    def test_pressure_state_is_non_mutating(self):
        source = {
            "name": "steamoutlet",
            "phase": {
                "mixture": {"momentum": {"gauge_pressure": {"value": 1.12e6}}},
                "phase-2": {
                    "multiphase": {"backflow_volume_fraction": {"value": 0.0}}
                },
            },
        }
        result = configured_pressure_outlet_state(source, 1.122e6)
        self.assertEqual(result["name"], "brineoutlet")
        self.assertEqual(
            result["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"],
            1.122e6,
        )
        self.assertEqual(
            result["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"],
            1.0,
        )
        self.assertEqual(source["name"], "steamoutlet")

    def test_inlet_scaling_is_phase_specific_and_non_mutating(self):
        source = {
            "phase": {
                "phase-1": {"momentum": {"mass_flow_rate": {"value": 0.0}}},
                "phase-2": {"momentum": {"mass_flow_rate": {"value": 0.0}}},
            }
        }
        result = scale_inlet_state(source, vapor_kg_s=8.069, liquid_kg_s=11.692)
        self.assertEqual(
            result["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"],
            8.069,
        )
        self.assertEqual(
            result["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"],
            11.692,
        )
        self.assertEqual(
            source["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"],
            0.0,
        )

    def test_response_gate_accepts_monotonic_sign_pattern(self):
        rows = []
        for dt_s in TIME_STEPS_S:
            rows.extend(
                [
                    {"requested_time_step_s": dt_s, "pressure_label": "low", "liquid_brineoutlet_kgs": -100.0},
                    {"requested_time_step_s": dt_s, "pressure_label": "center", "liquid_brineoutlet_kgs": 0.0},
                    {"requested_time_step_s": dt_s, "pressure_label": "high", "liquid_brineoutlet_kgs": 100.0},
                ]
            )
        self.assertEqual(response_pattern_failures(rows), [])

    def test_response_gate_rejects_nonquiet_center(self):
        rows = []
        for dt_s in TIME_STEPS_S:
            rows.extend(
                [
                    {"requested_time_step_s": dt_s, "pressure_label": "low", "liquid_brineoutlet_kgs": -100.0},
                    {"requested_time_step_s": dt_s, "pressure_label": "center", "liquid_brineoutlet_kgs": 20.0},
                    {"requested_time_step_s": dt_s, "pressure_label": "high", "liquid_brineoutlet_kgs": 100.0},
                ]
            )
        self.assertTrue(any("centre flow is not quiet" in item for item in response_pattern_failures(rows)))


if __name__ == "__main__":
    unittest.main()
