from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "setup"
sys.path.insert(0, str(SCRIPT_DIR))

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


REPORT_TEXT = """
===== dpm_extended_summary_injection-0_file_contents =====

 Fate                        Zone   Zone Number                  Elapsed Time (s)
                             Name     Id               Min        Max        Avg    Std Dev
 ----------- -------------------- ------ ------ ---------- ---------- ---------- ----------
 Incomplete                                   2  1.000e+00  2.000e+00  1.500e+00  5.000e-01
 Escaped             steam_outlet      7     10  1.000e+00  2.000e+00  1.500e+00  5.000e-01
 Trapped             fluid_outlet      8      8  1.000e+00  2.000e+00  1.500e+00  5.000e-01

                                               (*)- Mass Transfer Summary -(*)

 Fate                        Zone   Zone      Mass Flow (kg/s)
                             Name     Id    Initial      Final     Change
 ----------- -------------------- ------ ---------- ---------- ----------
 Incomplete                               2.000e-01  2.500e-01  5.000e-02
 Escaped             steam_outlet      7  1.000e-01  1.500e-01  5.000e-02
 Trapped             fluid_outlet      8  6.500e-01  6.000e-01 -5.000e-02
 -----------                             ---------- ---------- ----------
 Net                                      9.500e-01  1.000e+00  5.000e-02
"""


COUNT_ONLY_REPORT = """
===== dpm_extended_summary_injection-0_file_contents =====

 Fate                        Zone   Zone Number                  Elapsed Time (s)
                             Name     Id               Min        Max        Avg    Std Dev
 ----------- -------------------- ------ ------ ---------- ---------- ---------- ----------
 Incomplete                                   2  1.000e+00  2.000e+00  1.500e+00  5.000e-01
 Escaped             steam_outlet      7     10  1.000e+00  2.000e+00  1.500e+00  5.000e-01
 Trapped             fluid_outlet      8      8  1.000e+00  2.000e+00  1.500e+00  5.000e-01
"""

UNLABELED_MASS_REPORT = """
===== dpm_extended_summary_injection-0_file_contents =====

 Fate                        Zone   Zone      Mass Flow (kg/s)
 ----------- -------------------- ------ ---------- ---------- ----------
 Escaped             steam_outlet      7  1.000e-01  1.500e-01  5.000e-02
"""


class FakeSetting:
    def __init__(self, state):
        self.state = state

    def get_state(self):
        return self.state


class FakePhase:
    def __init__(self, material: str):
        self.material = FakeSetting(material)


class FakePhases:
    def __init__(self, materials: dict[str, str]):
        self.items = {name: FakePhase(material) for name, material in materials.items()}

    def get_object_names(self):
        return list(self.items)

    def __getitem__(self, name: str):
        return self.items[name]


def fake_solver(*, gas: str, liquid: str, interaction_enabled: bool):
    phases = FakePhases({"phase-1": gas, "phase-2": liquid})
    interaction = FakeSetting({"enabled": interaction_enabled})
    return SimpleNamespace(
        settings=SimpleNamespace(
            setup=SimpleNamespace(
                models=SimpleNamespace(
                    multiphase=SimpleNamespace(phases=phases),
                    discrete_phase=SimpleNamespace(
                        general_settings=SimpleNamespace(interaction=interaction)
                    ),
                )
            )
        )
    )


class DpmReportParsingTests(unittest.TestCase):
    def setUp(self):
        self.case = sweep.PaperCase(1, "Case 1", "1600 -25%", 1.0, 1.0)
        self.bin = sweep.InjectionBin(1, "injection-0", 1.0, 1.0, 0.001, 1.0, -2.0)

    def test_final_mass_flow_column_is_used(self):
        rows = sweep.parse_dpm_result_rows(
            self.case,
            [self.bin],
            REPORT_TEXT,
            "face-normal",
        )
        self.assertEqual(rows[0]["escaped_kgs"], "0.15")
        self.assertEqual(rows[0]["trapped_kgs"], "0.6")
        self.assertEqual(rows[0]["incomplete_kgs"], "0.25")
        self.assertIn("Final column", rows[0]["notes"])

    def test_count_fallback_is_disabled_by_default(self):
        rows = sweep.parse_dpm_result_rows(
            self.case,
            [self.bin],
            COUNT_ONLY_REPORT,
            "face-normal",
        )
        self.assertEqual(rows[0]["escaped_kgs"], "")

    def test_count_fallback_requires_explicit_opt_in(self):
        rows = sweep.parse_dpm_result_rows(
            self.case,
            [self.bin],
            COUNT_ONLY_REPORT,
            "face-normal",
            allow_count_fallback=True,
        )
        self.assertAlmostEqual(float(rows[0]["escaped_kgs"]), 0.5)
        self.assertIn("not validated", rows[0]["notes"])

    def test_mass_columns_require_explicit_header(self):
        rows = sweep.parse_dpm_result_rows(
            self.case,
            [self.bin],
            UNLABELED_MASS_REPORT,
            "face-normal",
        )
        self.assertEqual(rows[0]["escaped_kgs"], "")

    def test_post_dpm_readback_does_not_require_mutation(self):
        state = {
            "particle_type": "inert",
            "material": sweep.PARTICLE_MATERIAL,
            "injection_type": {"option": "surface"},
            "initial_values": {
                "location": {"injection_surfaces": [sweep.INJECTION_SURFACE]},
                "mass_flow_rate": {"total_flow_rate": self.bin.mass_flow_kgs},
                "velocity": {
                    "use_face_normal_direction": True,
                    "magnitude": abs(self.bin.z_velocity_ms),
                },
                "particle_size": {"diameter": self.bin.diameter_m},
            },
        }
        solver = SimpleNamespace(
            settings=SimpleNamespace(
                setup=SimpleNamespace(
                    models=SimpleNamespace(
                        discrete_phase=SimpleNamespace(
                            injections={self.bin.injection_name: FakeSetting(state)}
                        )
                    )
                )
            )
        )
        result = sweep.read_dpm_injections(solver, [self.bin], "face-normal")
        self.assertEqual(result[self.bin.injection_name], state)


class PhysicsPreflightTests(unittest.TestCase):
    def test_expected_phase_mapping_and_one_way_dpm_pass(self):
        result = sweep.require_case_physics(
            fake_solver(
                gas=sweep.DEFAULT_GAS_PHASE_MATERIAL,
                liquid=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
                interaction_enabled=False,
            ),
            gas_phase_material=sweep.DEFAULT_GAS_PHASE_MATERIAL,
            liquid_phase_material=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
            allow_coupled_dpm=False,
        )
        self.assertEqual(result["phase_materials"]["phase-1"], sweep.DEFAULT_GAS_PHASE_MATERIAL)

    def test_swapped_phase_materials_fail(self):
        with self.assertRaisesRegex(RuntimeError, "phase material readback mismatch"):
            sweep.require_case_physics(
                fake_solver(
                    gas=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
                    liquid=sweep.DEFAULT_GAS_PHASE_MATERIAL,
                    interaction_enabled=False,
                ),
                gas_phase_material=sweep.DEFAULT_GAS_PHASE_MATERIAL,
                liquid_phase_material=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
                allow_coupled_dpm=False,
            )

    def test_coupled_dpm_fails_by_default(self):
        with self.assertRaisesRegex(RuntimeError, "requires one-way DPM"):
            sweep.require_case_physics(
                fake_solver(
                    gas=sweep.DEFAULT_GAS_PHASE_MATERIAL,
                    liquid=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
                    interaction_enabled=True,
                ),
                gas_phase_material=sweep.DEFAULT_GAS_PHASE_MATERIAL,
                liquid_phase_material=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
                allow_coupled_dpm=False,
            )


if __name__ == "__main__":
    unittest.main()
