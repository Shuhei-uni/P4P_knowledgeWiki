from __future__ import annotations

import unittest
import sys
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import missing_remote_files, require_remote_files  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
