#!/usr/bin/env python3
"""Read-only status report for the setup-07g brine-outlet qualification."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07g_pressure_equal_psep_v1"
)
MANIFEST = RUN_DIR / "qualification_manifest.json"
PID_FILE = RUN_DIR / "controller.pid"


def value(data: dict[str, Any], key: str) -> str:
    item = data.get(key)
    if isinstance(item, float):
        return f"{item:.7g}"
    return str(item if item is not None else "n/a")


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    print(f"Setup 07g status - {datetime.now().astimezone().isoformat(timespec='seconds')}")
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        try:
            os.kill(pid, 0)
            process = "active"
        except OSError:
            process = "not active"
        print(f"Controller: {process} (PID {pid})")
    else:
        print("Controller: no PID file")

    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        print(
            f"Run: {manifest.get('status')} | {manifest.get('classification')} | "
            f"{manifest.get('iterations_completed', 0)}/{manifest.get('target_iterations', 3000)}"
        )
        blocks = manifest.get("iteration_blocks") or []
        if blocks:
            metrics = blocks[-1].get("physical_metrics") or {}
            print(f"Latest physical block: {metrics.get('iteration')}")
            print(
                "  outlet mixture flow steam/brine: "
                f"{value(metrics, 'mixture_steamoutlet_kgs')} / "
                f"{value(metrics, 'mixture_brineoutlet_kgs')} kg/s"
            )
            print(
                "  outlet vapor steam / liquid brine: "
                f"{value(metrics, 'vapor_steamoutlet_kgs')} / "
                f"{value(metrics, 'liquid_brineoutlet_kgs')} kg/s"
            )
            print(
                "  imbalance mixture/vapor/liquid: "
                f"{value(metrics, 'mixture_imbalance_percent')}% / "
                f"{value(metrics, 'vapor_imbalance_percent')}% / "
                f"{value(metrics, 'liquid_imbalance_percent')}%"
            )
            print(
                "  pressure drop steam/brine: "
                f"{value(metrics, 'pressure_drop_to_steamoutlet_pa')} / "
                f"{value(metrics, 'pressure_drop_to_brineoutlet_pa')} Pa"
            )
            print(
                "  steam quality / brine liquid fraction: "
                f"{value(metrics, 'steamoutlet_quality_percent')}% / "
                f"{value(metrics, 'brineoutlet_liquid_fraction_percent')}%"
            )
        if manifest.get("error"):
            print(f"Error: {manifest['error']}")
    else:
        print("Run manifest: not written yet")

    try:
        solver = connect(server_id="1", tcp_timeout_seconds=8.0)
        print(f"Fluent: {solver.get_fluent_version()} | {solver.health_check.status()}")
    except Exception as exc:
        print(f"Fluent: unreachable ({type(exc).__name__}: {exc})")
    print("Read-only check: no Fluent settings or calculations were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
