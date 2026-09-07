#!/usr/bin/env python3
"""Progress the accepted 0.1% setup-07m hold through 0.2%, 0.5% and 1%."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import run_setup07m_micro_hold as hold07m  # noqa: E402
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    hold = json.loads((hold07m.LOCAL_ROOT / "hold_manifest.json").read_text(encoding="utf-8"))
    if hold.get("status") != "completed" or not hold.get("strict_0p01_gate_passed"):
        raise RuntimeError("accepted 0.1% fixed-flow hold is unavailable")
    checkpoint = hold.get("checkpoints", {}).get("10")
    if not checkpoint:
        raise RuntimeError("0.1% hold step-10 checkpoint is missing")
    preparation = json.loads(
        (prepare07l.local_root_for_server(args.server_id) / "preparation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])

    campaign07m.MAX_ITERATIONS_PER_TIME_STEP = 100
    solver = connect(server_id=args.server_id, start_transcript=True)
    require_live_compute_node_count(solver, prepare07l.EXPECTED_COMPUTE_NODES)
    solver.transcript.stop()
    campaign07m.run_ramp(
        solver,
        checkpoint,
        campaign07m.BRINE_FACE_REST_PRESSURE_PA,
        domain_volume,
        1.0e-7,
        fractions=(0.002, 0.005, 0.01),
        steps_per_fraction=10,
        full_flow_extra_hold_steps=0,
        output_name="progressive_micro_ramp_dt1e-7_inner100",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
