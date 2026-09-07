#!/usr/bin/env python3
"""Read-only preflight for setup 07b's constant-water-level liquid sink."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.constant_water_level_sink import (  # noqa: E402
    find_phase_for_material,
    parse_zone_table,
)

import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_constant_water_level_sink_20260807"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / STUDY_ID / "preflight_readback.json"
REMOTE_SCRATCH = (
    r"C:\Users\qtra338\Documents\Mesh study\split_inlet_mesh_convergence_20260801\mesh_900k"
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--output", default=str(DEFAULT_OUTPUT))
    result.add_argument("--remote-scratch", default=REMOTE_SCRATCH)
    return result


def capture_zone_table(solver: Any) -> tuple[str, dict[str, dict[str, Any]]]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = solver.tui.mesh.modify_zones.list_zones()
        if result is not None:
            print(result)
    text = buffer.getvalue()
    return text, parse_zone_table(text)


def phase_materials(solver: Any) -> dict[str, str]:
    state = solver.settings.setup.models.species.get_state()
    materials = state.get("model", {}).get("phase_material", {})
    if not isinstance(materials, dict):
        raise RuntimeError("path/version issue: phase-material mapping is unavailable")
    return {str(name): str(material) for name, material in materials.items()}


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    solver = connect(server_id=args.server_id)

    zone_text, zones = capture_zone_table(solver)
    required = {
        "bottom": "wall",
        "wall-fluid": "wall",
        "liquidinlet": "mass-flow-inlet",
        "steaminlet": "mass-flow-inlet",
        "steamoutlet": "pressure-outlet",
        "fluid": "fluid",
    }
    errors = [
        f"zone {name!r} expected type {kind!r}; actual={zones.get(name)}"
        for name, kind in required.items()
        if zones.get(name, {}).get("type") != kind
    ]

    materials = phase_materials(solver)
    liquid_phase = find_phase_for_material(materials, "water-liquid-at-psep")
    phase_names = sorted(materials)
    liquid_phase_index = phase_names.index(liquid_phase)

    mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
    settings = mesh_study.capture_settings(solver, args.remote_scratch)
    settings.update(mesh_study.verify_initialized_phase_identity(solver, args.remote_scratch))
    errors.extend(mesh_study.validate_settings(settings, mesh_metrics, require_phase_identity=True))

    # Fluent omits the redundant ``Net`` row for a one-surface area report;
    # scope the report to both wall zones and retain the named bottom row.
    bottom_area = mesh_study.surface_areas(
        solver, args.remote_scratch, ["bottom", "wall-fluid"]
    )["bottom"]
    bottom_centroid = {
        axis: mesh_study.surface_scalar(
            solver,
            args.remote_scratch,
            f"bottom_{axis}_centroid",
            ["bottom"],
            f"{axis}-coordinate",
        )["bottom"]
        for axis in ("x", "y", "z")
    }

    payload = {
        "study_id": STUDY_ID,
        "classification": "accepted" if not errors else "unresolved",
        "fluent_health": str(solver.health_check.status()),
        "fluent_version": str(solver.get_fluent_version()),
        "zone_table": zones,
        "zone_table_transcript": zone_text,
        "bottom_zone_id": zones.get("bottom", {}).get("id"),
        "bottom_type": zones.get("bottom", {}).get("type"),
        "bottom_area_m2": bottom_area,
        "bottom_centroid_m": bottom_centroid,
        "phase_materials": materials,
        "liquid_phase": liquid_phase,
        "liquid_phase_index_zero_based": liquid_phase_index,
        "mesh_metrics": mesh_metrics,
        "mesh_quality_transcript": quality_text,
        "settings_readback": settings,
        "validation_errors": errors,
        "case_mutated": False,
        "iterations_run": 0,
        "unresolved_geometry_evidence": (
            "The repository/user identifies bottom as the constant-water-level cutoff, "
            "but a source-CAD dimension or archived geometry image still needs to be linked."
        ),
    }
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"\nRead-only preflight written to: {output}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
