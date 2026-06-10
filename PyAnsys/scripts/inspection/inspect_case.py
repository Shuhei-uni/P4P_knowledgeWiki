#!/usr/bin/env python3
"""Read-only inspection of the currently loaded Fluent case."""

from __future__ import annotations

from collections.abc import Mapping
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def keys_of(value) -> list[str]:
    if isinstance(value, Mapping):
        return sorted(str(key) for key in value.keys())
    return []


def compact_boundary_summary(boundary_state: Mapping) -> None:
    print("\n--- Boundary zones ---")
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, Mapping):
            continue
        names = [name for name in zones.keys() if name not in {"settings"}]
        if names:
            print(f"{boundary_type}: {', '.join(sorted(names))}")


def compact_material_summary(materials_state: Mapping) -> None:
    print("\n--- Materials ---")
    for material_type, materials in materials_state.items():
        if isinstance(materials, Mapping):
            names = keys_of(materials)
            if names:
                print(f"{material_type}: {', '.join(names)}")


def compact_model_summary(models_state: Mapping) -> None:
    print("\n--- Models ---")
    multiphase = models_state.get("multiphase", {})
    viscous = models_state.get("viscous", {})
    energy = models_state.get("energy", {})
    dpm = models_state.get("discrete_phase", {})
    species = models_state.get("species", {})

    print(f"multiphase: {multiphase}")
    print(f"viscous: {viscous}")
    print(f"energy: {energy}")
    print(f"species: {species}")
    print(f"discrete_phase keys: {', '.join(keys_of(dpm))}")


def compact_solution_summary(solution_state: Mapping) -> None:
    print("\n--- Solution setup ---")
    methods = solution_state.get("methods", {})
    controls = solution_state.get("controls", {})
    report_defs = solution_state.get("report_definitions", {})
    monitor = solution_state.get("monitor", {})

    print(f"methods: {methods}")
    print(f"controls keys: {', '.join(keys_of(controls))}")
    print(f"report definition categories: {', '.join(keys_of(report_defs))}")

    residual = monitor.get("residual", {}) if isinstance(monitor, Mapping) else {}
    equations = residual.get("equations", {}) if isinstance(residual, Mapping) else {}
    if equations:
        print(f"residual equations: {', '.join(keys_of(equations))}")


def try_scheme(solver, label: str, expression: str) -> None:
    try:
        value = solver.scheme.eval(expression)
        print(f"{label}: {value}")
    except Exception as exc:
        print(f"{label}: unavailable ({exc})")


def main() -> int:
    solver = connect()
    print("\nConnected. Inspecting loaded case without modifying it...")
    print(f"Fluent version: {solver.get_fluent_version()}")

    print("\n--- Runtime values ---")
    try_scheme(solver, "flow-time", "(rpgetvar 'flow-time)")
    try_scheme(solver, "time-step", "(rpgetvar 'time-step)")
    try_scheme(solver, "physical-time-step", "(rpgetvar 'physical-time-step)")

    boundary_state = solver.settings.setup.boundary_conditions.get_state()
    models_state = solver.settings.setup.models.get_state()
    materials_state = solver.settings.setup.materials.get_state()
    cell_zone_state = solver.settings.setup.cell_zone_conditions.get_state()
    solution_state = solver.settings.solution.get_state()

    compact_boundary_summary(boundary_state)
    compact_model_summary(models_state)
    compact_material_summary(materials_state)

    print("\n--- Cell zones ---")
    for zone_type, zones in cell_zone_state.items():
        if isinstance(zones, Mapping):
            print(f"{zone_type}: {', '.join(keys_of(zones))}")

    compact_solution_summary(solution_state)

    print("\nInspection finished. No iterations were run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
