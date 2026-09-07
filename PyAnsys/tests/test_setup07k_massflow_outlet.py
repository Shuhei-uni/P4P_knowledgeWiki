import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from prepare_setup07k_transient_vof_massflow_outlet import (  # noqa: E402
    configured_mass_flow_outlet_state,
    run_label_for_server,
)


class Setup07kMassFlowOutletTests(unittest.TestCase):
    def test_phase_specific_outlet_command_is_liquid_only(self):
        state = {
            "name": "brineoutlet",
            "phase": {
                "mixture": {"momentum": {}},
                "phase-1": {"momentum": {}},
                "phase-2": {"momentum": {}},
            },
        }
        result = configured_mass_flow_outlet_state(state)
        self.assertEqual(
            result["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"],
            0.0,
        )
        self.assertEqual(
            result["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"],
            116.92,
        )
        self.assertEqual(state["phase"]["phase-2"]["momentum"], {})

    def test_server_namespace_is_isolated(self):
        self.assertEqual(
            run_label_for_server("2"),
            "brine620k_07k_transient_vof_massflow_brine_v1_server2",
        )


if __name__ == "__main__":
    unittest.main()
