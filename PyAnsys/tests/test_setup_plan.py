from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.autonomy.common import ContractValidationError  # noqa: E402
from pyansys_fluent.setup_plan import (  # noqa: E402
    MarkdownSetupPlan,
    capture_parent_identity,
)


PLAN = """---
schema_version: 1
plan_id: 09c-test
recipe_id: dpm_two_way_interaction
parent_case_path: /tmp/08b.cas.h5
parent_case_sha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
output_case_path: /tmp/09c.cas.h5
expected_parent_interaction:
  enabled: false
  update_sources_every_iteration: false
  iteration_interval: 1
update_sources_every_iteration: true
iteration_interval: 1
---

# Test plan
"""


class MarkdownSetupPlanTests(unittest.TestCase):
    def test_plan_round_trip_has_stable_digest(self) -> None:
        plan = MarkdownSetupPlan.from_markdown(PLAN)
        self.assertEqual(plan.plan_id, "09c-test")
        self.assertEqual(plan.recipe_id, "dpm_two_way_interaction")
        self.assertEqual(plan.iteration_interval, 1)
        self.assertEqual(plan.digest, MarkdownSetupPlan.from_markdown(PLAN).digest)

    def test_unknown_front_matter_is_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            MarkdownSetupPlan.from_markdown(PLAN.replace("iteration_interval: 1\n---", "iteration_interval: 1\nunsafe_command: erase\n---"))

    def test_parent_identity_hashes_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = Path(temporary) / "parent.cas.h5"
            case.write_bytes(b"parent-case")
            identity = capture_parent_identity(str(case))
        self.assertEqual(identity["size_bytes"], len(b"parent-case"))
        self.assertEqual(len(identity["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
