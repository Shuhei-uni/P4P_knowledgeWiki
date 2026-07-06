from __future__ import annotations

import unittest

from pyansys_fluent.postprocess_live import (
    calculate_carrier_metrics,
    compile_postprocess_result,
    infer_phase_domain_map,
    parse_dpm_sample_output,
    render_markdown_report,
)


class PostprocessLiveTests(unittest.TestCase):
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
        self.assertIn("small relative", metrics["mass_imbalance_note"])

    def test_compile_and_render_report(self) -> None:
        result = compile_postprocess_result(
            server_id="2",
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
                    "selected_boundaries": ["steamoutlet"],
                    "selected_planes": [],
                    "aggregate_counts": {
                        "tracked": 6510,
                        "escaped": 8,
                        "trapped": 0,
                        "incomplete": 6502,
                    },
                    "samples": [
                        {
                            "name": "injection-5-micron",
                            "counts": {
                                "tracked": 2170,
                                "escaped": 8,
                                "trapped": 0,
                                "incomplete": 2162,
                            }
                        }
                    ],
                    "warnings": [],
                },
            },
        )

        markdown = render_markdown_report(result)

        self.assertEqual(result["claim_class_ceiling"], "Numerically verified")
        self.assertIn("562 um, 844 um, 1631 um", "\n".join(result["limitations"]))
        self.assertIn("## Carrier Flux Metrics", markdown)
        self.assertIn("## Per-Injection DPM Sample", markdown)
        self.assertIn("injection-5-micron: tracked `2170`, escaped `8`, trapped `0`, incomplete `2162`", markdown)
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


if __name__ == "__main__":
    unittest.main()
