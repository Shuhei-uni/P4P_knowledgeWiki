#!/usr/bin/env python3
"""Save the paused live setup-07b field without iterating or changing settings."""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402

import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import run_setup07b_sink_qualification as qualify  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    manifest_path = qualify.LOCAL_DIR / "qualification_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cumulative = int(manifest["cumulative_iterations_completed"])
    r1_completed = int(manifest["r1_iterations_completed"])

    solver = connect(server_id="1")
    mesh_metrics, _ = mesh_study.collect_mesh_reports(solver)
    errors: list[str] = []
    if int(mesh_metrics.get("cells", -1)) != qualify.EXPECTED_CELLS:
        errors.append(f"mesh mismatch: {mesh_metrics}")

    settings = mesh_study.capture_settings(solver, qualify.REMOTE_DIR)
    settings.update(
        mesh_study.verify_initialized_phase_identity(solver, qualify.REMOTE_DIR)
    )
    errors.extend(
        mesh_study.validate_settings(settings, mesh_metrics, require_phase_identity=True)
    )
    sources = verify07b.source_readback(solver)
    errors.extend(
        verify07b.validate_source_readback(sources, library=qualify.EXPECTED_LIBRARY)
    )
    parameters = verify07b.rp_readback(solver)
    if not math.isclose(
        float(parameters["user/cwl07b/tau-s"]),
        float(manifest["tau_s"]),
        abs_tol=1.0e-12,
    ):
        errors.append(f"tau mismatch: {parameters}")
    if not math.isclose(
        float(parameters["user/cwl07b/ramp"]), 1.0, abs_tol=1.0e-12
    ):
        errors.append(f"ramp mismatch: {parameters}")
    if bool(solver.scheme.eval("(sg-dpm?)")):
        errors.append("DPM model unexpectedly active")
    if errors:
        raise RuntimeError("live recovery preflight failed: " + "; ".join(errors))

    label = f"recovery_live_cumulative{cumulative}_r1_{r1_completed}_r1p0"
    pair = setup07b.save_pair(solver, qualify.REMOTE_DIR, label)
    manifest.setdefault("checkpoints", {})[
        f"live_recovery_{cumulative}"
    ] = pair
    manifest.update(
        {
            "status": "paused",
            "classification": "diagnostic qualification paused; recoverable",
            "controller_state": "paused after controller disconnect",
            "pause_reason": (
                "The calculation controller disconnected after the recorded "
                "iteration-1000 block; Fluent remained healthy and idle."
            ),
            "ramp_live_at_pause": 1.0,
            "last_update_epoch": time.time(),
        }
    )
    # Update only the manifest. The recorded monitor CSVs remain untouched.
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "paused", "checkpoint": pair}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
