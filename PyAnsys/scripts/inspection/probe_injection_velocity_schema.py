#!/usr/bin/env python3
"""Probe the DPM injection velocity settings object without mutating Fluent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


def safe_call(label: str, func) -> dict[str, Any]:
    try:
        return {"label": label, "value": func()}
    except Exception as exc:
        return {"label": label, "error": f"{type(exc).__name__}: {exc}"}


def public_attrs(obj: Any) -> list[str]:
    return sorted(name for name in dir(obj) if not name.startswith("_"))


def main() -> int:
    load_dotenv()
    solver = connect()
    branch = solver.settings.setup.models.discrete_phase.injections
    injection = branch["injection-0"]
    velocity = injection.initial_values.velocity

    payload = {
        "injection_state": safe_get_state(injection, "injection-0"),
        "velocity_state": safe_get_state(velocity, "injection-0.velocity"),
        "velocity_public_attrs": public_attrs(velocity),
        "velocity_active_child_names": safe_call(
            "get_active_child_names", lambda: list(velocity.get_active_child_names())
        ),
        "velocity_active_command_names": safe_call(
            "get_active_command_names", lambda: list(velocity.get_active_command_names())
        ),
        "velocity_attrs": safe_call("get_attrs", lambda: velocity.get_attrs()),
        "velocity_state_with_units": safe_call(
            "state_with_units", lambda: velocity.state_with_units()
        ),
        "velocity_attr_use_face_normal": safe_call(
            "use_face_normal_direction", lambda: velocity.use_face_normal_direction()
        ),
        "velocity_attr_magnitude": safe_call("magnitude", lambda: velocity.magnitude()),
        "velocity_attr_swirl_fraction": safe_call(
            "swirl_fraction", lambda: velocity.swirl_fraction()
        ),
        "velocity_attr_x": safe_call("x_velocity", lambda: velocity.x_velocity()),
        "velocity_attr_y": safe_call("y_velocity", lambda: velocity.y_velocity()),
        "velocity_attr_z": safe_call("z_velocity", lambda: velocity.z_velocity()),
        "velocity_attr_x2": safe_call("x_velocity_2", lambda: velocity.x_velocity_2()),
        "velocity_attr_y2": safe_call("y_velocity_2", lambda: velocity.y_velocity_2()),
        "velocity_attr_z2": safe_call("z_velocity_2", lambda: velocity.z_velocity_2()),
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
