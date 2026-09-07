from __future__ import annotations

import unittest
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    missing_remote_files,
    require_live_compute_node_count,
    require_remote_files,
)


class FakeScheme:
    def __init__(self, existing: set[str]) -> None:
        self.existing = existing

    def eval(self, expression: str) -> bool:
        return any(path in expression for path in self.existing)


class RemoteArtifactTests(unittest.TestCase):
    def test_missing_remote_files_preserves_order(self) -> None:
        solver = SimpleNamespace(scheme=FakeScheme({"ready.cas.h5"}))

        self.assertEqual(
            missing_remote_files(solver, ["ready.cas.h5", "missing.dat.h5", "other.out"]),
            ["missing.dat.h5", "other.out"],
        )

    def test_require_remote_files_reports_all_missing_paths(self) -> None:
        solver = SimpleNamespace(scheme=FakeScheme({"ready.cas.h5"}))

        with self.assertRaisesRegex(
            FileNotFoundError,
            r"Stage-2 pair: missing remote artifact\(s\): missing\.dat\.h5, other\.out",
        ):
            require_remote_files(
                solver,
                ("ready.cas.h5", "missing.dat.h5", "other.out"),
                "Stage-2 pair",
            )


class ComputeNodeCountTests(unittest.TestCase):
    def test_matching_count_returns_observed_roster(self) -> None:
        roster = {"compute_node_count": 2, "compute_node_ids": [0, 1]}
        solver = object()
        with patch(
            "pyansys_fluent.common.capture_parallel_connectivity_roster",
            return_value=roster,
        ) as capture:
            self.assertIs(require_live_compute_node_count(solver, 2), roster)
        capture.assert_called_once_with(solver)

    def test_mismatching_count_fails_with_actual_and_expected(self) -> None:
        with patch(
            "pyansys_fluent.common.capture_parallel_connectivity_roster",
            return_value={"compute_node_count": 2},
        ):
            with self.assertRaisesRegex(RuntimeError, "must be 4.*actual=2"):
                require_live_compute_node_count(object(), 4)

    def test_unavailable_roster_is_not_treated_as_a_matching_count(self) -> None:
        with patch(
            "pyansys_fluent.common.capture_parallel_connectivity_roster",
            side_effect=RuntimeError("no compute-node rows"),
        ):
            with self.assertRaisesRegex(RuntimeError, "no compute-node rows"):
                require_live_compute_node_count(object(), 2)


if __name__ == "__main__":
    unittest.main()
