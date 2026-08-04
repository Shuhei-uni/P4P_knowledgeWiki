#!/usr/bin/env python3
"""Probe DPM material state for the active Fluent session."""

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


def safe(label: str, func) -> dict[str, Any]:
    try:
        return {"label": label, "value": func()}
    except Exception as exc:
        return {"label": label, "error": f"{type(exc).__name__}: {exc}"}


def names(branch: Any) -> list[str]:
    return sorted(str(name) for name in branch.get_object_names())


def main() -> int:
    load_dotenv()
    solver = connect()
    materials = solver.settings.setup.materials
    payload = {
        "fluid_names": safe("fluid_names", lambda: names(materials.fluid)),
        "inert_particle_names": safe("inert_particle_names", lambda: names(materials.inert_particle)),
        "water_liquid_dpm_state": safe(
            "water-liquid-dpm",
            lambda: safe_get_state(materials.inert_particle["water-liquid-dpm"], "water-liquid-dpm"),
        ),
        "injection_materials": {},
    }
    injections = solver.settings.setup.models.discrete_phase.injections
    for name in sorted(injections.get_object_names()):
        state = safe_get_state(injections[name], name)
        payload["injection_materials"][name] = {
            "particle_type": state.get("particle_type"),
            "material": state.get("material"),
            "velocity": state.get("initial_values", {}).get("velocity"),
        }
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
