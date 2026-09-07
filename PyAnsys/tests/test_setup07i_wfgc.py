from __future__ import annotations

import sys
import unittest
from pathlib import Path


SETUP = Path(__file__).resolve().parents[1] / "scripts" / "setup"
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SETUP))
sys.path.insert(0, str(SRC))

from run_setup07h_brine_pool_qualification import gross_physical_gate  # noqa: E402
from pyansys_fluent.common import (  # noqa: E402
    parse_parallel_connectivity_roster,
    require_live_compute_node_count,
)


class _Solver:
    def __init__(self, report):
        class _ShowConnectivity:
            def __call__(_self, compute_node):
                print(report)

        class _Parallel:
            show_connectivity = _ShowConnectivity()

        class _Settings:
            parallel = _Parallel()

        self.settings = _Settings()


def _connectivity_report(node_count: int, hardware_cores: int = 20) -> str:
    return "\n".join(
        f"n{node_id}{'*' if node_id == 0 else ''}   EN439159  "
        f"{node_id + 1}/{hardware_cores}  Windows-x64  {1000 + node_id}  CPU"
        for node_id in reversed(range(node_count))
    )


class LiveComputeNodeGateTests(unittest.TestCase):
    def test_exact_sixteen_compute_nodes_passes(self):
        roster = require_live_compute_node_count(
            _Solver(_connectivity_report(16)), 16
        )
        self.assertEqual(roster["compute_node_count"], 16)
        self.assertEqual(roster["hardware_core_counts"], [20])

    def test_twenty_compute_nodes_fails(self):
        with self.assertRaisesRegex(RuntimeError, "must be 16.*actual=20"):
            require_live_compute_node_count(_Solver(_connectivity_report(20)), 16)

    def test_core_denominator_is_not_misread_as_process_count(self):
        roster = parse_parallel_connectivity_roster(_connectivity_report(16, 20))
        self.assertEqual(roster["compute_node_count"], 16)
        self.assertEqual(roster["compute_node_ids"], list(range(16)))
        self.assertEqual(roster["hardware_core_counts"], [20])


class GrossPhysicalGateTests(unittest.TestCase):
    def test_bounded_outlet_state_passes(self):
        passed, failures = gross_physical_gate(
            {
                "liquid_liquidinlet_kgs": 116.92,
                "liquid_brineoutlet_kgs": -120.0,
                "mixture_imbalance_percent": 2.0,
                "liquid_imbalance_percent": 3.0,
            }
        )
        self.assertTrue(passed)
        self.assertEqual(failures, [])

    def test_setup07h_divergent_state_fails(self):
        passed, failures = gross_physical_gate(
            {
                "liquid_liquidinlet_kgs": 116.92,
                "liquid_brineoutlet_kgs": -3304.7817,
                "mixture_imbalance_percent": 1602.9928,
                "liquid_imbalance_percent": 2726.5324,
            }
        )
        self.assertFalse(passed)
        self.assertEqual(len(failures), 3)


if __name__ == "__main__":
    unittest.main()
