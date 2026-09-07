#!/usr/bin/env python3
"""Run the promoted setup-07m inlet ramp after the opening extension passes."""

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
import run_setup07m_opening_extension as extension07m  # noqa: E402
import run_setup07m_pressure_opening_campaign as campaign07m  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    extension_campaign = json.loads(
        (extension07m.LOCAL_ROOT / "extension_campaign_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if extension_campaign.get("status") != "completed":
        raise RuntimeError("setup-07m opening extension has not completed")
    if not extension_campaign.get("ramp_eligible"):
        raise RuntimeError("setup-07m opening extension did not pass promotion gates")
    center_manifest = json.loads(
        (extension07m.LOCAL_ROOT / "center" / "extension_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    checkpoint = center_manifest.get("checkpoints", {}).get("10")
    if not checkpoint:
        raise RuntimeError("accepted centre-pressure step-10 checkpoint is missing")
    preparation = json.loads(
        (prepare07l.local_root_for_server(args.server_id) / "preparation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    domain_volume = float(preparation["mesh_metrics"]["domain_volume_m3"])

    solver = connect(server_id=args.server_id, start_transcript=True)
    runtime = require_live_compute_node_count(solver, prepare07l.EXPECTED_COMPUTE_NODES)
    solver.transcript.stop()
    campaign07m.write_json(
        campaign07m.LOCAL_ROOT / "inlet_ramp" / "promotion_readback.json",
        {
            "source": "accepted setup-07m centre-pressure opening-extension step 10",
            "source_checkpoint": checkpoint,
            "opening_extension_assessment": extension_campaign,
            "live_parallel_runtime": runtime,
        },
    )
    campaign07m.run_ramp(
        solver,
        checkpoint,
        campaign07m.BRINE_FACE_REST_PRESSURE_PA,
        domain_volume,
        1.0e-6,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
