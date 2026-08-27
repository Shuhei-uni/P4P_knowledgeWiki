from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.results_evidence import (
    BEGIN_MARKER,
    END_MARKER,
    render_results_evidence,
    update_results_evidence,
)


def _render(path: Path, run_label: str = "demo") -> str:
    return render_results_evidence(
        results_path=path,
        run_label=run_label,
        load_summary={"mode": "already-loaded-session"},
        case_identity={
            "status": "unavailable",
            "warnings": ["Case/data identity was not exposed by the active session."],
        },
        fluent_version="25.2.0",
        records=[
            {
                "name": "residual",
                "status": "complete",
                "scope": "monitor set residual",
                "coordinate": "Fluent monitor iteration",
                "horizon": "iterations 100 → 200",
                "measurements": [
                    "20 monitor point(s)",
                    "last continuity=1e-4 scaled residual",
                ],
                "artifacts": [path.parents[3] / "PyAnsys" / "output" / "demo.json"],
                "notes": ["The native iteration coordinate was retained."],
                "numerical_state": "No convergence verdict was assigned.",
                "missing": [],
                "observations": ["The monitor returned 20 points."],
            },
            {
                "name": "flux",
                "status": "partial",
                "scope": "zones inlet and outlet; domains phase-1, phase-2",
                "coordinate": "single live snapshot; Fluent iteration/time unavailable",
                "horizon": "single live snapshot",
                "measurements": ["signed Fluent fluxes: phase-1/inlet=-1.25 kg/s"],
                "artifacts": [],
                "notes": ["Signed source values remain in the JSON artifact."],
                "numerical_state": "No time-window stability assessment was possible.",
                "missing": ["No iteration/time coordinate was available."],
                "observations": ["The captured scope was a single snapshot."],
            },
        ],
    )


class ResultsEvidenceTests(unittest.TestCase):
    def test_render_keeps_coordinates_units_signs_and_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Project" / "experiments" / "demo" / "results.md"
            markdown = _render(path)

        self.assertIn("### Run identity / horizon", markdown)
        self.assertIn("iterations 100 → 200", markdown)
        self.assertIn("1e-4 scaled residual", markdown)
        self.assertIn("-1.25 kg/s", markdown)
        self.assertIn("`complete`", markdown)
        self.assertIn("`partial`", markdown)
        self.assertIn("does not choose a preferred case or model", markdown)
        self.assertIn(
            "`historical machine artifact path: ../../../PyAnsys/output/demo.json (not migrated)`",
            markdown,
        )
        self.assertNotIn("[demo.json](", markdown)

    def test_render_reports_explicit_load_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Project" / "experiments" / "demo" / "results.md"
            markdown = render_results_evidence(
                results_path=path,
                run_label="explicit-load",
                load_summary={
                    "load_mode": "explicit-read_case-then-read_data",
                },
                case_identity={
                    "status": "verified",
                    "basis": "explicit case/data load performed by this workflow",
                },
                fluent_version="25.2.0",
                records=[],
            )

        self.assertIn(
            "Case/data action: `explicit-read_case-then-read_data`",
            markdown,
        )

    def test_update_appends_without_touching_human_interpretation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Project" / "experiments" / "demo" / "results.md"
            human_text = (
                "# Results\n\n"
                "## Findings / interpretation\n\n"
                "Human-owned interpretation stays here.\n"
            )
            path.parent.mkdir(parents=True)
            path.write_text(human_text, encoding="utf-8")

            update_results_evidence(path, _render(path))
            updated = path.read_text(encoding="utf-8")

        self.assertTrue(updated.startswith(human_text))
        self.assertIn(BEGIN_MARKER, updated)
        self.assertIn(END_MARKER, updated)
        self.assertIn("Human-owned interpretation stays here.", updated)

    def test_update_replaces_only_its_own_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Project" / "experiments" / "demo" / "results.md"
            prefix = "# Results\n\n"
            suffix = "\n\n## Findings / interpretation\n\nKeep this text.\n"
            path.parent.mkdir(parents=True)
            path.write_text(prefix + _render(path, "first") + suffix, encoding="utf-8")

            update_results_evidence(path, _render(path, "second"))
            updated = path.read_text(encoding="utf-8")

        self.assertTrue(updated.startswith(prefix))
        self.assertTrue(updated.endswith(suffix))
        self.assertEqual(updated.count(BEGIN_MARKER), 1)
        self.assertEqual(updated.count(END_MARKER), 1)
        self.assertNotIn("`first`", updated)
        self.assertIn("`second`", updated)
        self.assertIn("Keep this text.", updated)

    def test_update_rejects_orphan_end_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.md"
            path.write_text(END_MARKER + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "end marker without a begin marker"):
                update_results_evidence(path, _render(path))


if __name__ == "__main__":
    unittest.main()
