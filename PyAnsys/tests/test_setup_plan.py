from __future__ import annotations

import hashlib
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
    execute_pinned_build_script,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plan(*, script_sha: str, parent: Path, output: Path) -> str:
    return f"""---
schema_version: 2
plan_id: 09c-test
parent_case_path: {parent}
parent_case_sha256: {_sha256(parent)}
output_case_path: {output}
build_script_path: scripts/build_09c.py
build_script_sha256: {script_sha}
---

# Test plan
"""


class MarkdownSetupPlanTests(unittest.TestCase):
    def test_plan_round_trip_has_stable_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "08b.cas.h5"
            parent.write_bytes(b"parent-case")
            plan_text = _plan(
                script_sha="a" * 64,
                parent=parent,
                output=root / "09c.cas.h5",
            )
        plan = MarkdownSetupPlan.from_markdown(plan_text)
        self.assertEqual(plan.plan_id, "09c-test")
        self.assertEqual(plan.build_script_path, "scripts/build_09c.py")
        self.assertEqual(plan.digest, MarkdownSetupPlan.from_markdown(plan_text).digest)

    def test_unknown_front_matter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "08b.cas.h5"
            parent.write_bytes(b"parent-case")
            plan = _plan(script_sha="a" * 64, parent=parent, output=root / "09c.cas.h5")
            with self.assertRaises(ContractValidationError):
                MarkdownSetupPlan.from_markdown(
                    plan.replace("build_script_sha256:", "unsafe_command: erase\nbuild_script_sha256:")
                )

    def test_parent_identity_hashes_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = Path(temporary) / "parent.cas.h5"
            case.write_bytes(b"parent-case")
            identity = capture_parent_identity(str(case))
        self.assertEqual(identity["size_bytes"], len(b"parent-case"))
        self.assertEqual(len(identity["sha256"]), 64)

    def test_runner_executes_the_pinned_build_script_not_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scripts = root / "scripts"
            scripts.mkdir()
            parent = root / "08b.cas.h5"
            output = root / "09c.cas.h5"
            parent.write_bytes(b"parent-case")
            script = scripts / "build_09c.py"
            script.write_text(
                "from pathlib import Path\n"
                "import argparse, json\n"
                "p=argparse.ArgumentParser()\n"
                "p.add_argument('--server-id'); p.add_argument('--source-case'); p.add_argument('--output-case'); p.add_argument('--summary-json')\n"
                "a=p.parse_args()\n"
                "Path(a.output_case).write_bytes(Path(a.source_case).read_bytes() + b'-09c')\n"
                "Path(a.summary_json).write_text(json.dumps({'steps': ['literal-tui-step', 'readback']}))\n"
            )
            plan = MarkdownSetupPlan.from_markdown(
                _plan(script_sha=_sha256(script), parent=parent, output=output)
            )
            result = execute_pinned_build_script(plan, project_root=root, server_id="1")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["build_script_evidence"]["steps"], ["literal-tui-step", "readback"])

    def test_build_script_outside_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            parent = root / "08b.cas.h5"
            parent.write_bytes(b"parent-case")
            plan = _plan(script_sha="a" * 64, parent=parent, output=root / "09c.cas.h5")
            with self.assertRaises(ContractValidationError):
                MarkdownSetupPlan.from_markdown(
                    plan.replace("scripts/build_09c.py", "../outside.py")
                )


if __name__ == "__main__":
    unittest.main()
