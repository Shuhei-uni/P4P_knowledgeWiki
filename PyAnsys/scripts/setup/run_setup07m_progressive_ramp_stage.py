#!/usr/bin/env python3
"""Run a gated later setup-07m ramp stage from the preceding accepted checkpoint."""

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
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402


STAGES = {
    "mid": {
        "source_output": "progressive_micro_ramp_dt1e-7_inner100",
        "source_key": "0.01",
        "fractions": (0.02, 0.05, 0.10),
        "output_name": "progressive_mid_ramp_2to10pct_dt1e-7_inner100",
    },
    "high": {
        "source_output": "progressive_mid_ramp_2to10pct_dt1e-7_inner100",
        "source_key": "0.1",
        "fractions": (0.15, 0.20, 0.25, 0.40, 0.60, 0.80, 1.00),
        "output_name": "progressive_high_ramp_15to100pct_dt1e-7_inner100",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=tuple(STAGES))
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    config = STAGES[args.stage]

    source_path = campaign07m.LOCAL_ROOT / config["source_output"] / "ramp_manifest.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("status") != "completed":
        raise RuntimeError(f"preceding ramp stage is not completed: {source_path}")
    checkpoint = source.get("checkpoints", {}).get(config["source_key"])
    if not checkpoint:
        raise RuntimeError(
            f"preceding ramp checkpoint {config['source_key']} is missing: {source_path}"
        )
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
        fractions=config["fractions"],
        steps_per_fraction=10,
        full_flow_extra_hold_steps=0,
        output_name=config["output_name"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
