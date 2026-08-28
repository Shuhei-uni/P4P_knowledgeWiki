from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.run_handoff import (  # noqa: E402
    CodexHandoff,
    RequiredFile,
    build_codex_command,
    load_spec,
    run_job,
    verify_required_files,
)


class RunHandoffTests(unittest.TestCase):
    def test_required_file_verification_checks_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ready = root / "ready.dat.h5"
            ready.write_bytes(b"abc")
            checks = verify_required_files(
                [RequiredFile(ready, 3), RequiredFile(root / "missing.cas.h5", 1)]
            )
            self.assertTrue(checks[0]["passed"])
            self.assertFalse(checks[1]["passed"])

    def test_codex_handoff_requires_explicit_session(self) -> None:
        handoff = CodexHandoff(
            enabled=True,
            session_id=None,
            executable="codex",
            working_directory=Path("."),
            prompt="continue",
            log_path=Path("codex.log"),
        )
        with self.assertRaisesRegex(ValueError, "session_id is required"):
            handoff.validate()

    def test_codex_resume_command_uses_explicit_session(self) -> None:
        handoff = CodexHandoff(
            enabled=True,
            session_id="1234-session",
            executable="codex",
            working_directory=Path("."),
            prompt="continue",
            log_path=Path("codex.log"),
        )
        command = build_codex_command(handoff, Path("manifest.json"), "COMPLETE")
        self.assertEqual(command[:4], ("codex", "exec", "resume", "1234-session"))
        self.assertIn("manifest.json", command[4])
        self.assertIn("COMPLETE", command[4])

    def test_successful_runner_writes_complete_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "job.yaml"
            spec_path.write_text(
                """
job:
  id: smoke
  manifest: manifest.json
runner:
  command:
    - PYTHON
    - -c
    - "from pathlib import Path; Path('final.dat.h5').write_bytes(b'ok')"
  cwd: .
  log: runner.log
completion:
  required_files:
    - path: final.dat.h5
      min_size_bytes: 2
codex:
  enabled: false
""".replace("PYTHON", sys.executable.replace("\\", "\\\\")),
                encoding="utf-8",
            )
            spec = load_spec(spec_path, repo_root=root)
            manifest = run_job(spec)
            self.assertEqual(manifest["status"], "COMPLETE")
            saved = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "COMPLETE")
            self.assertTrue(saved["verification"]["required_files"][0]["passed"])

    def test_nonzero_runner_is_blocked_even_when_output_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "job.yaml"
            spec_path.write_text(
                """
job:
  id: fail
  manifest: manifest.json
runner:
  command:
    - PYTHON
    - -c
    - "from pathlib import Path; Path('final.dat.h5').write_bytes(b'ok'); raise SystemExit(3)"
  cwd: .
completion:
  required_files:
    - final.dat.h5
codex:
  enabled: false
""".replace("PYTHON", sys.executable.replace("\\", "\\\\")),
                encoding="utf-8",
            )
            spec = load_spec(spec_path, repo_root=root)
            manifest = run_job(spec)
            self.assertEqual(manifest["status"], "BLOCKED")
            self.assertEqual(manifest["runner"]["return_code"], 3)


if __name__ == "__main__":
    unittest.main()
