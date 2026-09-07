#!/usr/bin/env python3
"""Inspect live Fluent paths needed for the setup-07l hydrostatic-rest test.

This probe is deliberately read-only.  It records DPM injection/model state,
operating-density controls, boundary object names, and transient/VOF controls
before the setup-07l preparation script changes anything.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

import sys

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


LOCAL_ROOT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07l_hydrostatic_rest_v1"
)


def attempt(func: Callable[[], Any]) -> Any:
    try:
        return func()
    except Exception as exc:  # inspection must preserve partial evidence
        return {"error": f"{type(exc).__name__}: {exc}"}


def active_children(obj: Any) -> Any:
    return attempt(lambda: list(obj.get_active_child_names()))


def allowed(setting: Any) -> Any:
    return attempt(lambda: [str(value) for value in setting.allowed_values()])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    solver = connect(server_id=args.server_id, start_transcript=True)

    models = solver.settings.setup.models
    dpm = models.discrete_phase
    injections = dpm.injections
    operating = solver.settings.setup.general.operating_conditions
    density = operating.operating_density
    boundaries = solver.settings.setup.boundary_conditions
    transient = solver.settings.solution.run_calculation.transient_controls
    methods = solver.settings.solution.methods

    payload = {
        "classification": "read-only setup-07l capability inspection",
        "server_id": args.server_id,
        "captured_epoch": time.time(),
        "fluent_version": str(solver.get_fluent_version()),
        "health": str(solver.health_check.status()),
        "dpm": {
            "state": safe_get_state(dpm, "setup.models.discrete_phase"),
            "active_children": active_children(dpm),
            "injection_names": attempt(lambda: list(injections.get_object_names())),
            "injections_state": safe_get_state(injections, "dpm.injections"),
            "interaction": safe_get_state(
                dpm.general_settings.interaction, "dpm.general_settings.interaction"
            ),
            "unsteady_tracking": safe_get_state(
                dpm.general_settings.unsteady_tracking,
                "dpm.general_settings.unsteady_tracking",
            ),
        },
        "operating_conditions": {
            "state": safe_get_state(operating, "operating_conditions"),
            "density_state": safe_get_state(density, "operating_density"),
            "density_active_children": active_children(density),
            "density_method_allowed_values": allowed(density.method),
            "reference_pressure_location": attempt(
                lambda: operating.reference_pressure_location.get_state()
            ),
        },
        "boundary_conditions": {
            "active_children": active_children(boundaries),
            "mass_flow_inlet_names": attempt(
                lambda: list(boundaries.mass_flow_inlet.get_object_names())
            ),
            "mass_flow_outlet_names": attempt(
                lambda: list(boundaries.mass_flow_outlet.get_object_names())
            ),
            "pressure_outlet_names": attempt(
                lambda: list(boundaries.pressure_outlet.get_object_names())
            ),
            "wall_names": attempt(lambda: list(boundaries.wall.get_object_names())),
        },
        "transient_controls": safe_get_state(transient, "transient_controls"),
        "solution_methods": safe_get_state(methods, "solution.methods"),
        "note": "No setting, initialization, particle update, or iteration was run.",
    }

    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    output = LOCAL_ROOT / "capability_inspection.json"
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"Saved read-only capability inspection: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
