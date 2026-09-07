#!/usr/bin/env python3
"""Measure liquid inventory in saved 900k iteration checkpoints.

This is a post-processing-only diagnostic.  It loads existing case/data pairs,
verifies the mesh and phase identity, evaluates the volume integral of the
secondary-phase volume fraction, and leaves Fluent at the 6000-iteration
checkpoint.  It never initializes, iterates, patches, updates DPM, or writes a
case/data file.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import parse_named_report_rows  # noqa: E402

import resume_split_inlet_mesh_convergence as resume  # noqa: E402
import run_split_inlet_mesh_convergence as study  # noqa: E402


MESH_NAME = "mesh-900k"
EXPECTED_CELLS = 5_335_623
LIQUID_FIELD = "phase-2-vof"
LOCAL_DIR = study.LOCAL_ROOT / "mesh_900k" / "checkpoint_liquid_inventory"
REMOTE_DIR = study.remote_join(study.REMOTE_STUDY_ROOT, "mesh_900k")


def checkpoint_pair(iteration: int) -> tuple[str, str]:
    if iteration == 4000:
        label = "iter4000_iteration_diagnostic1"
    else:
        label = f"iter{iteration}_iteration_diagnostic3"
    return (
        study.remote_join(REMOTE_DIR, f"{MESH_NAME}_{label}.cas.h5"),
        study.remote_join(REMOTE_DIR, f"{MESH_NAME}_{label}.dat.h5"),
    )


CHECKPOINTS = {iteration: checkpoint_pair(iteration) for iteration in (4000, 5000, 5500, 6000)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    return parser


def available_scalar_fields(solver: Any) -> set[str]:
    try:
        return set(solver.fields.field_data.scalar_fields.allowed_values())
    except Exception:
        # Fluent 2024 R2 is exposed through the older field-data protocol.
        return set(solver.fields.field_info.get_scalar_fields_info())


def volume_report(solver: Any, label: str, command_name: str, field: str) -> float:
    reports = solver.settings.results.report.volume_integrals
    command = getattr(reports, command_name)
    text = study.report_file_text(
        solver,
        REMOTE_DIR,
        label,
        lambda path: command(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = parse_named_report_rows(text, ["fluid"])
    if "fluid" not in rows:
        raise RuntimeError(f"Could not parse {command_name} report for {field}")
    return float(rows["fluid"])


def inspect_checkpoint(solver: Any, iteration: int, case_file: str, data_file: str) -> dict[str, Any]:
    print(f"Loading checkpoint {iteration}: {case_file}", flush=True)
    resume.read_case_data(solver, case_file, data_file)

    # All handles are reacquired after the case/data load.
    zones = study.current_zone_mapping(solver, allow_rename=False)
    mesh_metrics, _ = study.collect_mesh_reports(solver)
    if int(mesh_metrics["cells"]) != EXPECTED_CELLS:
        raise RuntimeError(
            f"Checkpoint {iteration} mesh mismatch: expected {EXPECTED_CELLS}, "
            f"got {mesh_metrics['cells']}"
        )
    fluid_role = zones.get("cell_roles", {}).get("fluid", {})
    if fluid_role.get("name") != "fluid" or fluid_role.get("category") != "fluid":
        raise RuntimeError(f"Checkpoint {iteration} has unexpected fluid-zone mapping: {zones}")

    phase_identity = study.verify_initialized_phase_identity(solver, REMOTE_DIR)
    if phase_identity["phase_materials"].get("phase-2") != "water-liquid-at-psep":
        raise RuntimeError(
            f"Checkpoint {iteration} phase-2 is not verified as liquid: {phase_identity}"
        )
    liquid_density = float(phase_identity["phase_densities_kg_m3"]["phase-2"])

    scalar_fields = available_scalar_fields(solver)
    if LIQUID_FIELD not in scalar_fields:
        raise RuntimeError(
            f"Checkpoint {iteration} does not expose {LIQUID_FIELD}; "
            "requires live field-name inspection"
        )

    liquid_volume = volume_report(
        solver, f"iter{iteration}_liquid_volume", "volume_integral", LIQUID_FIELD
    )
    liquid_volume_fraction = volume_report(
        solver, f"iter{iteration}_liquid_vf_average", "volume_average", LIQUID_FIELD
    )
    liquid_vf_min = volume_report(
        solver, f"iter{iteration}_liquid_vf_min", "minimum", LIQUID_FIELD
    )
    liquid_vf_max = volume_report(
        solver, f"iter{iteration}_liquid_vf_max", "maximum", LIQUID_FIELD
    )
    domain_volume = float(mesh_metrics["domain_volume_m3"])
    if not (0.0 <= liquid_volume <= domain_volume):
        raise RuntimeError(
            f"Checkpoint {iteration} liquid volume is outside [0, domain volume]: "
            f"{liquid_volume} vs {domain_volume}"
        )
    if not math.isclose(
        liquid_volume / domain_volume,
        liquid_volume_fraction,
        rel_tol=2e-4,
        abs_tol=1e-8,
    ):
        raise RuntimeError(
            f"Checkpoint {iteration} liquid-volume cross-check failed: "
            f"integral/volume={liquid_volume / domain_volume}, "
            f"reported average={liquid_volume_fraction}"
        )

    physical = study.collect_physical_metrics(solver, REMOTE_DIR, iteration)
    return {
        "iteration": iteration,
        "case_file": case_file,
        "data_file": data_file,
        "cells": int(mesh_metrics["cells"]),
        "domain_volume_m3": domain_volume,
        "liquid_density_kg_m3": liquid_density,
        "liquid_volume_m3": liquid_volume,
        "liquid_inventory_kg": liquid_volume * liquid_density,
        "domain_liquid_volume_fraction": liquid_volume_fraction,
        "liquid_volume_fraction_min": liquid_vf_min,
        "liquid_volume_fraction_max": liquid_vf_max,
        "pressure_drop_pa": physical["pressure_drop_pa"],
        "liquid_steamoutlet_kgs": physical["liquid_steamoutlet_kgs"],
        "vapor_steamoutlet_kgs": physical["vapor_steamoutlet_kgs"],
        "domain_volume_avg_velocity_ms": physical["domain_volume_avg_velocity_ms"],
        "domain_volume_avg_vorticity_s-1": physical["domain_volume_avg_vorticity_s-1"],
        "phase_identity": phase_identity,
        "dpm_active": bool(solver.scheme.eval("(sg-dpm?)")),
    }


def main() -> int:
    args = build_parser().parse_args()
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id=args.server_id)
    rows: list[dict[str, Any]] = []
    failure: BaseException | None = None
    try:
        for iteration, pair in CHECKPOINTS.items():
            rows.append(inspect_checkpoint(solver, iteration, *pair))
            study.write_json(LOCAL_DIR / "liquid_inventory_checkpoints.json", rows)
            study.write_csv(LOCAL_DIR / "liquid_inventory_checkpoints.csv", rows)
    except BaseException as exc:
        failure = exc
    finally:
        # The last normal load is 6000.  If an earlier load failed, explicitly
        # restore the verified 6000 checkpoint before returning control.
        if not rows or int(rows[-1].get("iteration", -1)) != 6000:
            final_case, final_data = CHECKPOINTS[6000]
            print("Restoring the verified 6000-iteration checkpoint", flush=True)
            resume.read_case_data(solver, final_case, final_data)
        print("Fluent left at the 6000-iteration checkpoint; no calculation was run.", flush=True)

    if failure is not None:
        raise failure

    summary = {
        "study_id": study.STUDY_ID,
        "mesh_name": MESH_NAME,
        "classification": "diagnostic",
        "operation": "checkpoint post-processing only",
        "liquid_field": LIQUID_FIELD,
        "iterations": [row["iteration"] for row in rows],
        "dpm": "off; no injection update or tracking performed",
        "fluent_final_state": "mesh-900k iteration 6000 checkpoint loaded",
        "rows": rows,
    }
    study.write_json(LOCAL_DIR / "liquid_inventory_summary.json", summary)
    print(json.dumps(summary, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
