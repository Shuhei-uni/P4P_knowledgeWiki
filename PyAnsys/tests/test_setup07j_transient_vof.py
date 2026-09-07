import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from prepare_setup07j_transient_vof import (  # noqa: E402
    RUN_LABEL,
    local_root_for_server,
    run_label_for_server,
)
from run_setup07j_transient_vof_qualification import (  # noqa: E402
    gross_gate,
    latest_checkpoint_step,
    next_block,
    phase_inventory,
    storage_closure,
)
from supervise_setup07j_transient_vof import (  # noqa: E402
    connection_failure,
    has_numeric_checkpoint,
    numerical_failure_evidence,
    safely_resumable_connection_failure,
    safely_resumable_guard_timeout,
    time_step_proof_failure,
    zero_flow_ratio_gate_failure,
)
class Setup07jServerSelectionTests(unittest.TestCase):
    def test_server_one_preserves_existing_namespace(self):
        self.assertEqual(run_label_for_server("1"), RUN_LABEL)
        self.assertEqual(local_root_for_server("1").name, RUN_LABEL)

    def test_second_server_gets_isolated_namespace(self):
        expected = f"{RUN_LABEL}_server2"
        self.assertEqual(run_label_for_server("2"), expected)
        self.assertEqual(local_root_for_server("2").name, expected)

    def test_invalid_server_is_rejected(self):
        with self.assertRaises(ValueError):
            run_label_for_server("4")


class Setup07jInventoryTests(unittest.TestCase):
    def test_phase_inventory_closes_domain_volume(self):
        result = phase_inventory(0.25, 2.0)
        self.assertAlmostEqual(result["liquid_inventory_kg"], 0.5 * 881.2108764648438)
        self.assertAlmostEqual(result["vapor_inventory_kg"], 1.5 * 5.797433853149414)

    def test_storage_closure_is_zero_for_consistent_liquid_gain(self):
        previous = {
            "flow_time_s": 0.0,
            "liquid_inventory_kg": 10.0,
            "vapor_inventory_kg": 5.0,
            "liquid_net_boundary_flux_kg_s": 2.0,
            "vapor_net_boundary_flux_kg_s": -1.0,
        }
        current = {
            "flow_time_s": 2.0,
            "liquid_inventory_kg": 14.0,
            "vapor_inventory_kg": 3.0,
            "liquid_net_boundary_flux_kg_s": 2.0,
            "vapor_net_boundary_flux_kg_s": -1.0,
        }
        result = storage_closure(previous, current)
        self.assertAlmostEqual(result["liquid_storage_closure_residual_kg_s"], 0.0)
        self.assertAlmostEqual(result["vapor_storage_closure_residual_kg_s"], 0.0)


class Setup07jGuardTests(unittest.TestCase):
    def base_metrics(self):
        return {
            "domain_volume_avg_liquid_volume_fraction": 0.2,
            "liquid_brineoutlet_kgs": -100.0,
            "liquid_steamoutlet_kgs": -1.0,
            "vapor_brineoutlet_kgs": -1.0,
            "vapor_steamoutlet_kgs": -79.0,
        }

    def test_bounded_state_passes(self):
        self.assertEqual(gross_gate(self.base_metrics()), [])

    def test_undefined_composition_is_allowed_only_at_zero_outlet_flow(self):
        metrics = self.base_metrics()
        metrics.update(
            {
                "mixture_steamoutlet_kgs": 0.0,
                "mixture_brineoutlet_kgs": 0.0,
                "steamoutlet_quality_percent": math.nan,
                "brineoutlet_liquid_fraction_percent": math.nan,
            }
        )
        self.assertEqual(gross_gate(metrics), [])
        metrics["mixture_steamoutlet_kgs"] = -1.0
        self.assertIn(
            "non-finite steamoutlet_quality_percent=nan", gross_gate(metrics)
        )

    def test_nonfinite_and_gross_drainage_fail(self):
        metrics = self.base_metrics()
        metrics["liquid_brineoutlet_kgs"] = -1000.0
        metrics["extra"] = math.inf
        failures = gross_gate(metrics)
        self.assertEqual(len(failures), 2)

    def test_finite_but_explosive_pressure_and_velocity_fail(self):
        metrics = self.base_metrics()
        metrics.update(
            {
                "inlet_mass_weighted_pressure_pa": 3.7e9,
                "steamoutlet_mass_weighted_pressure_pa": -4.1e13,
                "domain_volume_avg_velocity_ms": 7.2e4,
            }
        )
        failures = gross_gate(metrics)
        self.assertTrue(any("gross pressure field" in item for item in failures))
        self.assertTrue(any("gross velocity field" in item for item in failures))

    def test_block_schedule_has_guarded_first_endpoints(self):
        self.assertEqual(next_block(0, 1000), 1)
        self.assertEqual(next_block(1, 1000), 1)
        self.assertEqual(next_block(10, 1000), 1)
        self.assertEqual(next_block(50, 1000), 1)
        self.assertEqual(next_block(100, 1000), 1)
        self.assertEqual(next_block(999, 1000), 1)


class Setup07jRecoveryTests(unittest.TestCase):
    def test_latest_checkpoint_ignores_time_zero_and_future_steps(self):
        result = {
            "checkpoints": {
                "time_zero": {"case": "t0.cas.h5", "data": "t0.dat.h5"},
                "100": {"case": "100.cas.h5", "data": "100.dat.h5"},
                "500": {"case": "500.cas.h5", "data": "500.dat.h5"},
            }
        }
        self.assertEqual(latest_checkpoint_step(result, 400), 100)
        self.assertEqual(latest_checkpoint_step(result, 1000), 500)

    def test_connection_failures_are_resumable_but_numerical_failures_are_not(self):
        self.assertTrue(connection_failure("_InactiveRpcError: StatusCode.UNAVAILABLE"))
        self.assertTrue(connection_failure("Connection reset by peer"))
        self.assertFalse(connection_failure("Floating point exception in AMG solver"))

    def test_resume_requires_a_numeric_case_data_pair(self):
        self.assertFalse(
            has_numeric_checkpoint(
                {"checkpoints": {"time_zero": {"case": "a", "data": "b"}}}
            )
        )
        self.assertTrue(
            has_numeric_checkpoint(
                {"checkpoints": {"100": {"case": "a", "data": "b"}}}
            )
        )

    def test_numerical_crash_is_not_misclassified_as_safe_network_resume(self):
        qualification = {
            "error": "_InactiveRpcError: StatusCode.UNAVAILABLE after SIGSEGV",
            "checkpoints": {"100": {"case": "a", "data": "b"}},
            "blocks": [],
        }
        self.assertTrue(connection_failure(qualification["error"]))
        self.assertTrue(numerical_failure_evidence(qualification))
        self.assertFalse(safely_resumable_connection_failure(qualification))

    def test_plain_network_loss_with_checkpoint_is_safely_resumable(self):
        qualification = {
            "error": "_InactiveRpcError: StatusCode.UNAVAILABLE connection reset",
            "checkpoints": {"100": {"case": "a", "data": "b"}},
            "blocks": [],
        }
        self.assertTrue(safely_resumable_connection_failure(qualification))

    def test_guard_timeout_resumes_only_running_finite_checkpoint(self):
        qualification = {
            "status": "running",
            "checkpoints": {"1": {"case": "a", "data": "b"}},
            "blocks": [],
        }
        self.assertTrue(safely_resumable_guard_timeout(124, qualification))
        self.assertFalse(safely_resumable_guard_timeout(1, qualification))
        qualification["error"] = "floating point exception"
        self.assertFalse(safely_resumable_guard_timeout(124, qualification))

    def test_known_zero_flow_ratio_gate_can_be_explicitly_resumed(self):
        qualification = {
            "error": (
                "RuntimeError: gross transient startup gate failed: "
                "non-finite steamoutlet_quality_percent=nan; "
                "non-finite brineoutlet_liquid_fraction_percent=nan"
            ),
            "checkpoints": {"1": {"case": "a", "data": "b"}},
        }
        self.assertTrue(zero_flow_ratio_gate_failure(qualification))

    def test_known_multi_step_clock_mismatch_can_be_explicitly_resumed(self):
        qualification = {
            "error": (
                "RuntimeError: time-step proof failed: expected=10, "
                "actual={'flow_time_s': 0.0004, 'time_step': 4}"
            ),
            "checkpoints": {"1": {"case": "a", "data": "b"}},
        }
        self.assertTrue(time_step_proof_failure(qualification))
        qualification["checkpoints"] = {"time_zero": {"case": "a", "data": "b"}}
        self.assertFalse(time_step_proof_failure(qualification))

    def test_no_output_settings_call_cannot_be_treated_as_success(self):
        required_markers = (
            "setting fluid (mixture)",
            "setting liquidinlet (mixture)",
            "setting steaminlet (mixture)",
            "setting steamoutlet (mixture)",
        )
        empty_text = "===== tui_read_settings =====\n"
        self.assertFalse(all(marker in empty_text.lower() for marker in required_markers))


if __name__ == "__main__":
    unittest.main()
