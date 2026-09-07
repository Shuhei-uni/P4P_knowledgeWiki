import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from prepare_setup07l_hydrostatic_rest import (  # noqa: E402
    configured_zero_inlet_state,
    run_label_for_server,
)
from run_setup07l_hydrostatic_rest import (  # noqa: E402
    dpm_tracking_evidence,
    parse_global_courant,
    rest_gate,
)


def good_row():
    row = {
        "domain_volume_avg_liquid_volume_fraction": 0.1,
        "inlet_area_weighted_pressure_pa": 1.12e6,
        "steamoutlet_area_weighted_pressure_pa": 1.12e6,
        "brine_wall_area_weighted_pressure_pa": 1.122e6,
        "domain_volume_avg_velocity_ms": 0.01,
        "steamoutlet_area_weighted_velocity_ms": 0.01,
        "brine_wall_area_weighted_velocity_ms": 0.0,
        "mixture_steamoutlet_kgs": 0.01,
        "liquid_inventory_kg": 10.0,
    }
    for domain in ("mixture", "vapor", "liquid"):
        for zone in ("liquidinlet", "steaminlet", "brineoutlet"):
            row[f"{domain}_{zone}_kgs"] = 0.0
    return row


class Setup07lHydrostaticRestTests(unittest.TestCase):
    def test_zero_inlet_state_is_phase_specific_and_non_mutating(self):
        source = {
            "phase": {
                "mixture": {"momentum": {}},
                "phase-1": {"momentum": {"mass_flow_rate": {"value": 80.69}}},
                "phase-2": {"momentum": {"mass_flow_rate": {"value": 116.92}}},
            }
        }
        result = configured_zero_inlet_state(source)
        self.assertEqual(
            result["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"],
            0.0,
        )
        self.assertEqual(
            result["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"],
            0.0,
        )
        self.assertEqual(
            source["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"],
            80.69,
        )

    def test_server_namespace_is_isolated(self):
        self.assertEqual(
            run_label_for_server("2"),
            "brine620k_07l_hydrostatic_rest_v1_server2",
        )

    def test_transcript_parsers_capture_courant_and_particles(self):
        text = (
            "Global Courant Number [Explicit VOF Criteria] : 0.231\n"
            "Injecting 6456 particle parcels\n"
            "Advancing DPM injections\n"
            "number tracked = 6456\n"
        )
        self.assertEqual(parse_global_courant(text), [0.231])
        self.assertEqual(len(dpm_tracking_evidence(text)), 3)

    def test_rest_gate_accepts_bounded_closed_state(self):
        self.assertEqual(rest_gate(good_row(), None), [])

    def test_rest_gate_rejects_wall_flux_and_pressure_blowup(self):
        row = good_row()
        row["liquid_brineoutlet_kgs"] = -1.0
        row["brine_wall_area_weighted_pressure_pa"] = -1.0e11
        failures = rest_gate(row, None)
        self.assertTrue(any("closed-boundary flux" in item for item in failures))
        self.assertTrue(any("gross pressure response" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
