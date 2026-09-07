#!/usr/bin/env python3
"""Hold the bounded setup-07m 1% inlet checkpoint without increasing flow."""

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


SOURCE_OUTPUT = "progressive_micro_ramp_dt1e-7_inner100"
SOURCE_KEY = "0.01"
OUTPUT_NAME = "progressive_hold_1pct_dt1e-7_inner100_steps20"
FRACTION = 0.01
DT_S = 1.0e-7
STEPS = 20
MAX_INNER = 100


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    source_path = campaign07m.LOCAL_ROOT / SOURCE_OUTPUT / "ramp_manifest.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    checkpoint = source.get("checkpoints", {}).get(SOURCE_KEY)
    if not checkpoint:
        raise RuntimeError(f"bounded 1% checkpoint is missing: {source_path}")
    source_blocks = source.get("blocks", [])
    if not source_blocks or float(source_blocks[-1].get("fraction", -1.0)) != FRACTION:
        raise RuntimeError("source manifest does not end at the expected 1% fraction")
    failures = source_blocks[-1].get("gate_failures", [])
    if not failures or any("continuity residual exceeds" not in item for item in failures):
        raise RuntimeError(f"1% source has a non-continuity gate failure: {failures}")

    preparation = json.loads(
        (prepare07l.local_root_for_server(args.server_id) / "preparation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])

    campaign07m.MAX_ITERATIONS_PER_TIME_STEP = MAX_INNER
    solver = connect(server_id=args.server_id, start_transcript=True)
    require_live_compute_node_count(solver, prepare07l.EXPECTED_COMPUTE_NODES)
    solver.transcript.stop()
    campaign07m.run_ramp(
        solver,
        checkpoint,
        campaign07m.BRINE_FACE_REST_PRESSURE_PA,
        domain_volume,
        DT_S,
        fractions=(FRACTION,),
        steps_per_fraction=STEPS,
        full_flow_extra_hold_steps=0,
        output_name=OUTPUT_NAME,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
