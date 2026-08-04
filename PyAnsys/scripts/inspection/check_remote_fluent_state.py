#!/usr/bin/env python3
"""Lightweight remote Fluent state check.

This avoids running any solver or DPM commands.  It only reads health, active
calculation state, iteration count, and DPM tracking settings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def json_print(label: str, value: Any) -> None:
    print(f"{label}: {json.dumps(value, indent=2, default=str)}")


def try_value(label: str, func) -> Any:
    try:
        value = func()
        json_print(label, value)
        return value
    except Exception as exc:
        payload = {"error": f"{type(exc).__name__}: {exc}"}
        json_print(label, payload)
        return payload


def main() -> int:
    load_dotenv()
    solver = connect()

    print(f"fluent_version: {solver.get_fluent_version()}")
    try_value("health_status", lambda: str(solver.health_check.status()))
    try_value("health_check", lambda: str(solver.health_check.check_health()))
    try_value("reported_number_of_iterations", lambda: sweep.read_iteration_count(solver))
    print(
        "reported_number_of_iterations_note: this is Fluent's current iteration/run setting; "
        "it is not proof that a disconnected controller completed that many iterations"
    )
    try_value("residual_monitor_history", lambda: sweep.monitor_iteration_snapshot(solver))

    run_calc = solver.settings.solution.run_calculation
    try_value("run_calculation_active_children", lambda: list(run_calc.get_active_child_names()))
    try_value("run_calculation_state", lambda: safe_get_state(run_calc, "run_calculation"))

    dpm = solver.settings.setup.models.discrete_phase
    try_value("dpm_tracking_state", lambda: safe_get_state(dpm.tracking, "dpm.tracking"))
    try_value("dpm_interaction_state", lambda: safe_get_state(dpm.general_settings.interaction, "dpm.interaction"))
    try_value("dpm_general_settings", lambda: safe_get_state(dpm.general_settings, "dpm.general_settings"))

    print("state_check_complete: no solver or DPM commands were run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
