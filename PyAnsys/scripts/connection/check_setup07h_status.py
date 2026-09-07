#!/usr/bin/env python3
"""Report setup-07h preparation/controller status and Fluent health read-only."""

from __future__ import annotations

import json
import signal
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import capture_parallel_connectivity_roster  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


RUN_ROOT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07h_pool_y0_equal_psep_v1"
)
SETUP_LABEL = "07h"


def load_json(name: str) -> dict:
    path = RUN_ROOT / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def connect_with_deadline(seconds: int = 15):
    """Bound the PyFluent handshake as well as the preliminary TCP check."""

    def deadline_handler(_signum, _frame):
        raise TimeoutError(
            f"Fluent accepted TCP but did not complete the gRPC handshake in {seconds}s"
        )

    previous = signal.signal(signal.SIGALRM, deadline_handler)
    signal.alarm(seconds)
    try:
        return connect(server_id="1", tcp_timeout_seconds=3.0)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    prep = load_json("preparation_manifest.json")
    run = load_json("qualification_manifest.json")
    print(
        f"Setup {SETUP_LABEL} status - "
        f"{datetime.now().astimezone().isoformat(timespec='seconds')}"
    )
    print(f"Preparation: {prep.get('status', 'not started')}")
    print(
        f"Qualification: {run.get('status', 'not started')} | "
        f"{run.get('classification', 'not classified')} | "
        f"{run.get('iterations_completed', 0)}/{run.get('target_iterations_if_qualified', 3000)}"
    )
    blocks = run.get("iteration_blocks", [])
    if blocks:
        m = blocks[-1].get("physical_metrics", {})
        print(f"Latest block: {blocks[-1].get('end_iteration')}")
        print(
            "  steam/brine mixture: "
            f"{m.get('mixture_steamoutlet_kgs')} / {m.get('mixture_brineoutlet_kgs')} kg/s"
        )
        print(
            "  brine liquid/vapor: "
            f"{m.get('liquid_brineoutlet_kgs')} / {m.get('vapor_brineoutlet_kgs')} kg/s"
        )
        print(
            "  imbalance mix/vapor/liquid: "
            f"{m.get('mixture_imbalance_percent')} / {m.get('vapor_imbalance_percent')} / "
            f"{m.get('liquid_imbalance_percent')} %"
        )
        print(f"  routing: {blocks[-1].get('routing')}")
    if run.get("error"):
        print(f"Error: {run['error']}")
    try:
        solver = connect_with_deadline()
    except Exception as exc:
        print(f"Fluent: unreachable ({type(exc).__name__}: {exc})")
        print("Read-only check: no settings or calculations changed.")
        return 2
    print(f"Fluent: {solver.get_fluent_version()} | {solver.health_check.status()}")
    try:
        roster = capture_parallel_connectivity_roster(solver)
        print(
            "Live compute nodes/hardware cores: "
            f"{roster['compute_node_count']} / {roster['hardware_core_counts']}"
        )
    except Exception as exc:
        print(f"Live compute-node readback unavailable: {type(exc).__name__}: {exc}")
    try:
        warped_face = (
            solver.settings.solution.methods.warped_face_gradient_correction
        ).get_state()
        print(f"Warped-face gradient correction: {warped_face}")
    except Exception as exc:
        print(f"Warped-face gradient correction readback unavailable: {type(exc).__name__}: {exc}")
    print("Read-only check: no settings or calculations changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
