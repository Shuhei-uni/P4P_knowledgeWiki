from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mesh_trial_harness_lib import (  # noqa: E402
    MeshMetrics,
    RequiredZoneContract,
    ZoneInventory,
    assess_trial,
    collect_transcript_cell_count,
    compare_zone_inventories,
    detect_artifact_type,
    evaluate_quality_gates,
    parse_required_zones_text,
    parse_check_quality_from_text,
    parse_distribution_low_count,
    resolve_input_artifact,
    validate_required_zones,
    write_trial_outputs,
)


class MeshTrialHarnessTests(unittest.TestCase):
    def test_detect_artifact_type(self):
        self.assertEqual(detect_artifact_type(Path("case.cas.h5")), "case")
        self.assertEqual(detect_artifact_type(Path("mesh.meshdat")), "mesh")
        self.assertEqual(detect_artifact_type(Path("geom.step")), "geometry")
        self.assertEqual(detect_artifact_type(Path("workflow.wft")), "workflow")
        self.assertEqual(detect_artifact_type(Path("unknown.txt")), "unknown")

    def test_parse_check_quality_from_text(self):
        text = """
Mesh Quality:

Minimum Orthogonal Quality =  1.40600e-01
Maximum Equivolume Skewness =  8.59400e-01
Maximum Aspect Ratio =  2.26015e+01
Minimum Expansion Ratio =  2.47627e-01
"""
        parsed = parse_check_quality_from_text(text)
        self.assertAlmostEqual(parsed["min_orthogonal_quality"], 0.1406)
        self.assertAlmostEqual(parsed["max_equivolume_skewness"], 0.8594)
        self.assertAlmostEqual(parsed["max_aspect_ratio"], 22.6015)
        self.assertAlmostEqual(parsed["min_expansion_ratio"], 0.247627)

    def test_parse_distribution_low_count(self):
        payload = [2, [3, 0], [97, 0]]
        self.assertEqual(parse_distribution_low_count(payload), 3)

    def test_collect_transcript_cell_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "fluent.trn"
            transcript.write_text("cells: 1444509\n", encoding="utf-8")
            self.assertEqual(collect_transcript_cell_count(transcript), 1444509)

    def test_compare_zone_inventories(self):
        baseline = ZoneInventory(
            boundary_by_type={"wall": ["wall"], "pressure_outlet": ["outlet"]},
            boundary_flat=["outlet", "wall"],
            cell_zone_names=["fluid"],
        )
        current = ZoneInventory(
            boundary_by_type={"wall": ["wall"], "pressure_outlet": ["outlet"]},
            boundary_flat=["outlet", "wall"],
            cell_zone_names=["fluid"],
        )
        result = compare_zone_inventories(baseline, current, "exact")
        self.assertTrue(result.preserved)

    def test_assess_trial(self):
        baseline = MeshMetrics(
            cell_count=120,
            min_orthogonal_quality=0.10,
            max_equivolume_skewness=0.90,
            bad_cell_fraction=0.10,
        )
        current = MeshMetrics(
            cell_count=90,
            min_orthogonal_quality=0.20,
            max_equivolume_skewness=0.80,
            bad_cell_fraction=0.05,
        )
        zones = compare_zone_inventories(
            ZoneInventory({}, [], []),
            ZoneInventory({}, [], []),
            "exact",
        )
        delta, assessment = assess_trial(
            baseline=baseline,
            current=current,
            zone_preservation=zones,
            cell_cap=100,
        )
        self.assertEqual(sorted(assessment.improved_metrics), [
            "bad_cell_fraction",
            "max_equivolume_skewness",
            "min_orthogonal_quality",
        ])
        self.assertTrue(assessment.under_cell_cap)
        self.assertTrue(assessment.success)
        self.assertEqual(delta.cell_count, -30)

    def test_resolve_input_artifact_prefers_case_over_mesh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mesh = root / "trial.msh"
            case = root / "trial.cas.h5"
            mesh.write_text("", encoding="utf-8")
            case.write_text("", encoding="utf-8")
            chosen_path, chosen_type = resolve_input_artifact(str(root), "auto")
            self.assertEqual(chosen_path, case.resolve())
            self.assertEqual(chosen_type, "case")

    def test_write_trial_outputs_returns_none_when_write_fails(self):
        class FileApi:
            def write_case(self, _path):
                raise RuntimeError("case blocked")

            def write_mesh(self, _path):
                raise RuntimeError("mesh blocked")

        class TuiApi:
            file = FileApi()

        class SessionApi:
            tui = TuiApi()

        notes: list[str] = []
        case_value, mesh_value = write_trial_outputs(
            SessionApi(),
            Path("trial.cas.h5"),
            Path("trial.msh"),
            notes=notes,
        )
        self.assertIsNone(case_value)
        self.assertIsNone(mesh_value)
        self.assertEqual(len(notes), 2)
        self.assertIn("Case write failed", notes[0])
        self.assertIn("Mesh write failed", notes[1])

    def test_parse_required_zones_text(self):
        contract = parse_required_zones_text(
            """
            # example
            [boundary]
            inlet | velocity-inlet
            boundary: outlet | pressure-outlet

            [cell]
            fluid
            cell: porous-region
            """
        )
        self.assertEqual(contract.boundary_zones, ["inlet", "outlet"])
        self.assertEqual(
            contract.boundary_zone_types,
            {"inlet": "velocity-inlet", "outlet": "pressure-outlet"},
        )
        self.assertEqual(contract.cell_zones, ["fluid", "porous-region"])

    def test_validate_required_zones(self):
        inventory = ZoneInventory(
            boundary_by_type={"wall": ["wall"], "pressure_outlet": ["outlet"]},
            boundary_flat=["outlet", "wall"],
            cell_zone_names=["fluid"],
        )
        contract = RequiredZoneContract(
            boundary_zones=["outlet", "wall"],
            boundary_zone_types={"outlet": "pressure_outlet", "wall": "wall"},
            cell_zones=["fluid"],
            source_path=None,
        )
        result = validate_required_zones(inventory, contract)
        self.assertTrue(result.all_present)
        self.assertEqual(result.missing_boundary_zones, [])
        self.assertEqual(result.wrong_boundary_type, {})
        self.assertEqual(result.missing_cell_zones, [])

    def test_evaluate_quality_gates(self):
        baseline = MeshMetrics(
            cell_count=1444509,
            min_orthogonal_quality=0.031677,
            max_equivolume_skewness=0.968323,
            bad_cell_fraction=7.6e-06,
            bad_cell_fraction_by_threshold={"0.15": 7.6e-06, "0.10": 2.0e-06, "0.05": 1.0e-06},
        )
        current = MeshMetrics(
            cell_count=980000,
            min_orthogonal_quality=0.035,
            max_equivolume_skewness=0.95,
            bad_cell_fraction=3.0e-06,
            bad_cell_fraction_by_threshold={"0.15": 3.0e-06, "0.10": 1.0e-06, "0.05": 0.0},
        )
        result = evaluate_quality_gates(baseline=baseline, current=current)
        self.assertTrue(result.acceptable)
        self.assertIn("min_orthogonal_quality", result.improved_metrics)
        self.assertIn("max_equivolume_skewness", result.improved_metrics)
        self.assertIn("bad_cell_fraction_0.15", result.improved_metrics)


if __name__ == "__main__":
    unittest.main()
