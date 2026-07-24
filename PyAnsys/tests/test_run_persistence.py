from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyansys_fluent.run_persistence import (
    RunPersistence,
    prune_checkpoint_history,
)


class RunPersistenceRetentionTests(unittest.TestCase):
    def test_default_policy_keeps_two_numbered_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output_case = root / "case.cas.h5"
            output_data = root / "case.dat.h5"
            for iteration in (100, 200, 300):
                (root / f"case-iter{iteration}.cas.h5").write_bytes(b"case")
                (root / f"case-iter{iteration}.dat.h5").write_bytes(b"data")

            persistence = RunPersistence(str(output_case), str(output_data))
            self.assertFalse(persistence.keep_history)
            prune_checkpoint_history(str(output_case), str(output_data))

            self.assertFalse((root / "case-iter100.cas.h5").exists())
            self.assertFalse((root / "case-iter100.dat.h5").exists())
            self.assertTrue((root / "case-iter200.cas.h5").exists())
            self.assertTrue((root / "case-iter200.dat.h5").exists())
            self.assertTrue((root / "case-iter300.cas.h5").exists())
            self.assertTrue((root / "case-iter300.dat.h5").exists())

            prune_checkpoint_history(
                str(output_case), str(output_data), keep_pairs=1
            )
            self.assertFalse((root / "case-iter200.cas.h5").exists())
            self.assertTrue((root / "case-iter300.cas.h5").exists())


if __name__ == "__main__":
    unittest.main()
