#!/usr/bin/env python3
"""Read the live resolved-brine-outlet geometry and carrier state without mutation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07g_brine_outlet_qualification as qualify  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


REMOTE_ROOT = (
    r"C:\Users\qtra338\Documents\Mesh study"
    r"\split_inlet_resolved_brine_outlet_20260813"
)
LOCAL_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "live_geometry_state_inspection.json"
)
SURFACES = [
    "liquidinlet",
    "steaminlet",
    "steamoutlet",
    "brineoutlet",
    "wall-fluid",
    "inlet-outer-wall",
]


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    solver = connect(server_id="1")
    payload: dict[str, object] = {
        "fluent_version": str(solver.get_fluent_version()),
        "fluent_health": str(solver.health_check.status()),
        "iteration_label": sweep.read_iteration_count(solver),
        "surface_areas_m2": mesh_study.surface_areas(solver, REMOTE_ROOT, SURFACES),
        "surface_centroids_m": {},
        "operating_conditions": safe_get_state(
            solver.settings.setup.general.operating_conditions,
            "setup.general.operating_conditions",
        ),
        "boundary_conditions": safe_get_state(
            solver.settings.setup.boundary_conditions,
            "setup.boundary_conditions",
        ),
        "dpm": "read-only inspection; no injection update or tracking",
    }
    centroids = payload["surface_centroids_m"]
    assert isinstance(centroids, dict)
    for field, key in (
        ("x-coordinate", "x_m"),
        ("y-coordinate", "y_m"),
        ("z-coordinate", "z_m"),
    ):
        centroids[key] = mesh_study.surface_scalar(
            solver,
            REMOTE_ROOT,
            f"live_surface_centroid_{key}",
            SURFACES,
            field,
        )
    payload["physical_metrics"] = qualify.physical_metrics(
        solver, int(payload["iteration_label"])
    )
    LOCAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUTPUT.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(json.dumps(payload, indent=2, default=str))
    print("Read-only inspection: no settings, initialization, or iterations changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
