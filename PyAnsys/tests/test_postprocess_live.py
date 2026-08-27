from __future__ import annotations

import json
import unittest

from pyansys_fluent.postprocess_live import (
    build_case_identity,
    build_dpm_sample_tui_command,
    calculate_carrier_metrics,
    capture_residual_history,
    compile_postprocess_result,
    determine_claim_class_ceiling,
    infer_phase_domain_map,
    parse_dpm_sample_output,
    render_markdown_report,
    run_dpm_sample_per_injection,
)


class PostprocessLiveTests(unittest.TestCase):
    def test_capture_residual_history_uses_and_stops_monitor_stream(self) -> None:
        class FakeMonitors:
            def __init__(self) -> None:
                self.started = False
                self.stopped = False

            def start(self) -> None:
                self.started = True

            def stop(self) -> None:
                self.stopped = True

            def get_monitor_set_names(self) -> list[str]:
                return ["residual"]

            def get_monitor_set_data(self, _name: str):
                return [10, 11], {"continuity": [1.0e-2, 1.0e-3]}

        class FakeSolver:
            def __init__(self) -> None:
                self.monitors = FakeMonitors()

        solver = FakeSolver()
        payload = capture_residual_history(
            solver,
            monitor_set="residual",
            timeout=0.1,
            interval=0.0,
            settle_seconds=0.0,
        )

        self.assertEqual(payload["point_count"], 2)
        self.assertEqual(payload["curve_count"], 1)
        self.assertEqual(payload["iterations"], [10, 11])
        self.assertTrue(solver.monitors.started)
        self.assertTrue(solver.monitors.stopped)

    def test_case_identity_does_not_fall_back_to_connection_metadata(self) -> None:
        identity = build_case_identity(
            {
                "load_mode": "already-loaded-session",
                "server_id": "3",
                "case_file": r"C:\\wrong-default.cas.h5",
                "data_file": r"C:\\wrong-default.dat.h5",
            }
        )

        self.assertEqual(identity["status"], "unavailable")
        self.assertIsNone(identity["case_file"])
        self.assertIsNone(identity["data_file"])
        self.assertIn("no server-id", identity["warnings"][0])

    def test_explicit_case_data_load_is_verified_identity(self) -> None:
        identity = build_case_identity(
            {
                "load_mode": "paired-read_case_data",
                "case_file": r"C:\\case.cas.h5",
                "data_file": r"C:\\case.dat.h5",
            }
        )

        self.assertEqual(identity["status"], "verified")
        self.assertEqual(identity["case_file"], r"C:\\case.cas.h5")
        self.assertEqual(identity["data_file"], r"C:\\case.dat.h5")

    def test_unavailable_case_identity_caps_claims_at_debug_only(self) -> None:
        result = {
            "source": {"case_identity": {"status": "unavailable"}},
            "carrier_fluxes": {"available": True},
            "carrier_metrics": {"eta_phase": 0.99, "mass_imbalance_ratio": 0.0},
            "dpm_inventory": {"result_fields_available": True},
        }

        self.assertEqual(determine_claim_class_ceiling(result), "Debug only")

    def test_infer_phase_domain_map_from_material_names(self) -> None:
        models_state = {
            "multiphase": {
                "phases": {
                    "phase-1": "water-vapor-at-psep",
                    "phase-2": "water-liquid-at-psep",
                }
            }
        }

        result = infer_phase_domain_map(models_state)

        self.assertEqual(result["vapor_domain"], "phase-1")
        self.assertEqual(result["liquid_domain"], "phase-2")
        self.assertEqual(result["warnings"], [])

    def test_calculate_carrier_metrics(self) -> None:
        carrier_fluxes = {
            "zones": ["liquidinlet", "steaminlet", "steamoutlet"],
            "by_domain": {
                "mixture": {
                    "liquidinlet": -116.92,
                    "steaminlet": -80.69,
                    "steamoutlet": 196.90,
                },
                "phase-1": {
                    "liquidinlet": 0.0,
                    "steaminlet": -80.69,
                    "steamoutlet": 80.0,
                },
                "phase-2": {
                    "liquidinlet": -116.92,
                    "steaminlet": 0.0,
                    "steamoutlet": 10.0,
                },
            },
        }
        zone_roles = {
            "liquid_inlet": "liquidinlet",
            "steam_inlet": "steaminlet",
            "steam_outlet": "steamoutlet",
        }

        metrics = calculate_carrier_metrics(
            carrier_fluxes,
            zone_roles,
            vapor_domain="phase-1",
            liquid_domain="phase-2",
        )

        self.assertAlmostEqual(metrics["m_liq_in"], 116.92)
        self.assertAlmostEqual(metrics["m_vap_in"], 80.69)
        self.assertAlmostEqual(metrics["m_liq_steam_out"], 10.0)
        self.assertAlmostEqual(metrics["m_vap_steam_out"], 80.0)
        self.assertAlmostEqual(metrics["eta_phase"], 1.0 - (10.0 / 116.92))
        self.assertAlmostEqual(metrics["x_out"], 80.0 / 90.0)
        self.assertAlmostEqual(metrics["mass_imbalance_kg_s"], abs((116.92 + 80.69) - 196.90))
        self.assertIn("not an acceptance criterion", metrics["mass_imbalance_note"])

    def test_compile_and_render_report(self) -> None:
        result = compile_postprocess_result(
            run_label="TwoPhaseInletV2(Purnanto)-25-05000",
            load_summary={
                "case_file": r"C:\case.cas.h5",
                "data_file": r"C:\case.dat.h5",
                "load_mode": "paired-read_case_data",
            },
            session_summary={
                "fluent_version": "25.2.0",
                "boundary_summary": {
                    "mass_flow_inlet": ["liquidinlet", "steaminlet"],
                    "pressure_outlet": ["steamoutlet"],
                },
                "warnings": [],
                "phase_domain_map": {
                    "vapor_domain": "phase-1",
                    "liquid_domain": "phase-2",
                    "warnings": [],
                },
                "zone_discovery": {
                    "roles": {
                        "liquid_inlet": "liquidinlet",
                        "steam_inlet": "steaminlet",
                        "steam_outlet": "steamoutlet",
                    },
                    "all_outlets": ["steamoutlet"],
                    "warnings": [],
                },
            },
            carrier_fluxes={"available": True, "by_domain": {}, "zones": []},
            carrier_metrics={
                "m_liq_in": 116.92,
                "m_vap_in": 80.69,
                "m_liq_steam_out": 0.5,
                "m_vap_steam_out": 80.0,
                "eta_phase": 0.9957235716739651,
                "x_out": 0.9937888198757764,
                "mass_imbalance_kg_s": 0.71,
                "mass_imbalance_ratio": 0.0036,
                "mass_imbalance_note": "Mass imbalance is small relative to the reported steam-line liquid carryover.",
            },
            dpm_inventory={
                "enabled": True,
                "warnings": [
                    "No stored DPM fate/result summary fields were found in the loaded session; this pass is inventory-only for DPM."
                ],
                "injection_count": 6,
                "injections": [],
                "result_fields_available": False,
            },
            dpm_metrics={
                "result_available": False,
                "active_diameters_um": [5.63, 28.14, 56.27, 112.54, 168.81, 348.88],
                "represented_mass_flow_total": 29.22,
                "aggregate_scope": "partial-bin diagnostic only",
                "missing_requested_bins_um": [562.0, 844.0, 1631.0],
                "per_injection_sample": {
                    "available": True,
                    "mode": "dpm-sample-per-injection",
                    "prompt_order": "injections-first",
                    "selected_boundaries": ["steaminlet"],
                    "selected_planes": [],
                    "aggregate_counts": {
                        "tracked": 6510,
                        "escaped": 8,
                        "trapped": 0,
                        "incomplete": 6502,
                    },
                    "escaped_fraction": 8 / 6510,
                    "trapped_fraction": 0.0,
                    "incomplete_fraction": 6502 / 6510,
                    "samples": [
                        {
                            "name": "injection-5-micron",
                            "counts": {
                                "tracked": 2170,
                                "escaped": 8,
                                "trapped": 0,
                                "incomplete": 2162,
                            },
                            "escaped_fraction": 8 / 2170,
                            "trapped_fraction": 0.0,
                            "incomplete_fraction": 2162 / 2170,
                        }
                    ],
                    "warnings": [],
                },
            },
        )

        markdown = render_markdown_report(result)

        self.assertEqual(result["claim_class_ceiling"], "Numerically verified")
        self.assertEqual(result["source"]["case_identity"]["status"], "verified")
        self.assertNotIn("server_id", json.dumps(result, default=str))
        self.assertNotIn("Server id", markdown)
        self.assertIn("562 um, 844 um, 1631 um", "\n".join(result["limitations"]))
        self.assertIn("## Carrier Flux Metrics", markdown)
        self.assertIn("## Per-Injection DPM Sample", markdown)
        self.assertIn("Prompt order: `injections-first`", markdown)
        self.assertIn("Selected boundaries: `steaminlet`", markdown)
        self.assertIn("injection-5-micron: tracked `2170`, observed escaped `8`", markdown)
        self.assertIn("raw fate bookkeeping retained in JSON", markdown)
        self.assertIn("Claim class ceiling: `Numerically verified`", markdown)
        self.assertIn("Stored DPM result fields available: `False`", markdown)

    def test_parse_dpm_sample_output(self) -> None:
        payload = parse_dpm_sample_output(
            """
            /report/dpm-sample
            DPM Iteration ....
            number tracked = 2170, escaped = 8, incomplete = 2162
            """
        )

        self.assertEqual(payload["counts"]["tracked"], 2170)
        self.assertEqual(payload["counts"]["escaped"], 8)
        self.assertEqual(payload["counts"]["trapped"], 0)
        self.assertEqual(payload["counts"]["incomplete"], 2162)
        self.assertEqual(
            payload["summary_line"],
            "number tracked = 2170, escaped = 8, incomplete = 2162",
        )

    def test_build_dpm_sample_tui_command_matches_fluent_tui_order(self) -> None:
        command = build_dpm_sample_tui_command(
            injection_name="injection-112-micron",
            boundary_names=["steaminlet"],
            plane_names=[],
            sample_file_name=r"C:\Users\syok443\Documents\sample.dpm",
        )

        self.assertEqual(
            command,
            "/report/dpm-sample\n"
            "(injection-112-micron)\n"
            "(steaminlet)\n"
            "()\n"
            r"C:\Users\syok443\Documents\sample.dpm" "\n",
        )

    def test_run_dpm_sample_per_injection_can_fall_back_to_injection_first(self) -> None:
        class FakeScheme:
            def __init__(self) -> None:
                self.commands: list[str] = []

            def eval(self, command: str) -> bool:
                self.commands.append(command)
                if "(steaminlet)\\n()\\n(injection-5-micron)" in command:
                    print("Invalid report/dpm-sample input")
                else:
                    print("number tracked = 2170, escaped = 8, trapped = 0, incomplete = 2162")
                return True

        class FakeSolver:
            def __init__(self) -> None:
                self.scheme = FakeScheme()

        solver = FakeSolver()

        payload = run_dpm_sample_per_injection(
            solver,
            injection_names=["injection-5-micron"],
            boundary_names=["steaminlet"],
            plane_names=[],
            prompt_order="sample-surfaces-first",
            fallback_prompt_order="injections-first",
        )

        self.assertEqual(payload["aggregate_counts"]["tracked"], 2170)
        self.assertEqual(payload["aggregate_counts"]["escaped"], 8)
        self.assertAlmostEqual(payload["escaped_fraction"], 8 / 2170)
        self.assertEqual(payload["samples"][0]["prompt_order"], "injections-first")
        self.assertEqual(len(solver.scheme.commands), 2)


if __name__ == "__main__":
    unittest.main()
