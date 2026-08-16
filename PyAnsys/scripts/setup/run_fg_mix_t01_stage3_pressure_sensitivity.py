#!/usr/bin/env python3
"""Prepare and submit a shortened FG-MIX-T01 pressure-sensitivity sweep.

Each pressure case is built from an explicitly named Stage-3 monitor-ready
case/data pair. The only setup delta is the brine pressure-outlet gauge
pressure. Python prepares and verifies the pressure siblings, then submits one
Fluent-native journal. Fluent owns all 200 transient timesteps and endpoint
writes; Python does not loop over solver iterations.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    quote_scheme_string,
    remote_file_exists,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data, write_case_data_pair  # noqa: E402


REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
EXPECTED_MESH = "Full-geomV2-231kcells.msh.h5"
TIME_STEP_S = 2.5e-4
MAX_ITER_PER_TIMESTEP = 20
TRANSIENT_STEPS = 200
PRESSURES_MPA = (1.120, 1.130, 1.140, 1.150, 1.160, 1.170, 1.180, 1.190, 1.200)
RESIDUAL_HISTORY_SIZE = 1_200


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def pressure_tag(pressure_mpa: float) -> str:
    return f"p{int(round(pressure_mpa * 1000)):04d}kpa"


def render_journal(children: list[dict[str, Any]]) -> str:
    lines = [
        "; FG-MIX-T01 Stage-3 shortened pressure sensitivity",
        "; Fluent owns 200 transient timesteps per pressure case.",
        "; Same timestep: 2.5e-4 s; same maximum iterations per timestep: 20.",
        "; Cases are pressure-only siblings of the verified Stage-2 start state.",
        "/file/confirm-overwrite? no",
    ]
    for child in children:
        branch = child["branch"]
        pressure_mpa = child["pressure_mpa"]
        lines.extend(
            [
                f"; BEGIN {branch} {pressure_mpa:.3f} MPa gauge",
                f'/file/read-case "{posix(child["prepared_case"])}"',
                f'/file/read-data "{posix(child["prepared_data"])}"',
                f"/solve/set/transient-controls/time-step-size {TIME_STEP_S}",
                f"/solve/monitors/residual/n-save {RESIDUAL_HISTORY_SIZE}",
                "/solve/monitors/residual/print? yes",
                f'/file/start-transcript "{posix(child["transcript"])}"',
                f"/solve/iterate {TRANSIENT_STEPS}",
                f'/file/write-case-data "{posix(child["endpoint_case"])}"',
                f'/plot/residuals-set/plot-to-file "{posix(child["residual_file"])}"',
                "/plot/residuals",
                "/plot/residuals-set/end-plot-to-file",
                "/file/stop-transcript",
                f"; END {branch} {pressure_mpa:.3f} MPa gauge",
            ]
        )
    lines.extend(["; Pressure sensitivity journal submitted; Fluent remains open.", ""])
    return "\n".join(lines)


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)'
        for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote pressure-sensitivity journal was not created: {remote_journal}")


def verify_start_state(solver: Any, *, branch: str, pressure_mpa: float) -> dict[str, Any]:
    solver_state = safe_get_state(solver.settings.setup.general.solver, "solver")
    transient = safe_get_state(
        solver.settings.solution.run_calculation.transient_controls,
        "transient_controls",
    )
    models = safe_get_state(solver.settings.setup.models.multiphase, "multiphase")
    boundary = safe_get_state(
        solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"],
        "brine_outlet",
    )
    pressure = nested(boundary, "phase", "mixture", "momentum", "gauge_pressure", "value")
    registers = solver.settings.solution.cell_registers.get_object_names()
    expected_pa = pressure_mpa * 1_000_000.0
    if solver_state.get("time") != "unsteady-2nd-order-bounded":
        raise RuntimeError(f"{branch} is not bounded second-order transient: {solver_state}")
    if abs(float(transient.get("time_step_size")) - TIME_STEP_S) > 1.0e-15:
        raise RuntimeError(f"{branch} timestep mismatch: {transient}")
    if transient.get("flow_time") != 0:
        raise RuntimeError(f"{branch} does not start at flow time 0: {transient}")
    if int(transient.get("max_iter_per_time_step")) != MAX_ITER_PER_TIMESTEP:
        raise RuntimeError(f"{branch} per-timestep iteration limit mismatch: {transient}")
    if abs(float(pressure) - expected_pa) > 0.5:
        raise RuntimeError(
            f"{branch} brine pressure mismatch: read {pressure!r} Pa, expected {expected_pa:.1f} Pa"
        )
    if models.get("model") != "mixture":
        raise RuntimeError(f"{branch} multiphase model mismatch: {models}")
    required_registers = {"codex_y010_pool_below_y_0p10m", "codex_y030_monitor_below_y_0p30m"}
    if not required_registers.issubset(set(registers)):
        raise RuntimeError(f"{branch} required registers are missing: {registers}")
    return {
        "solver": solver_state,
        "transient_controls": transient,
        "multiphase_model": models.get("model"),
        "brine_pressure_pa": pressure,
        "registers": sorted(str(name) for name in registers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--stage3-manifest", required=True, type=Path)
    parser.add_argument("--branch", choices=("INIT-S", "INIT-H"), default="INIT-S")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Prepare and reload-verify pressure siblings without submitting the native journal",
    )
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC stamp for prepared cases, endpoints, transcripts, and journal",
    )
    parser.add_argument("--local-journal", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    args = parser.parse_args()

    stage3 = json.loads(args.stage3_manifest.expanduser().resolve().read_text(encoding="utf-8"))
    if PureWindowsPath(stage3["mesh"]).name != EXPECTED_MESH:
        raise ValueError(f"Stage-3 manifest is not locked to {EXPECTED_MESH}: {stage3['mesh']}")
    sources = [child for child in stage3.get("children", []) if child["branch"] == args.branch]
    if len(sources) != 1:
        raise ValueError(f"Expected exactly one source child for {args.branch}; found {len(sources)}")
    source = sources[0]

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")

    source_case = source["case_file"]
    source_data = source["data_file"]
    for path in (source_case, source_data):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Missing immutable Stage-3 source pair member: {path}")

    children: list[dict[str, Any]] = []
    prepared_readbacks: dict[str, Any] = {}
    for pressure_mpa in PRESSURES_MPA:
        tag = pressure_tag(pressure_mpa)
        stem = f"FG-MIX-T01-S3-{args.branch}-TPO1-{tag}-200step-{args.run_stamp}"
        prepared_case = str(PureWindowsPath(REMOTE_DIR) / f"{stem}-start.cas.h5")
        prepared_data = str(PureWindowsPath(REMOTE_DIR) / f"{stem}-start.dat.h5")
        endpoint_case = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.cas.h5")
        endpoint_data = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.dat.h5")
        transcript = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.trn")
        residual_file = str(PureWindowsPath(REMOTE_DIR) / f"{stem}-residuals.out")
        for path in (
            prepared_case,
            prepared_data,
            endpoint_case,
            endpoint_data,
            transcript,
            residual_file,
        ):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"Refusing to overwrite pressure-sensitivity artifact: {path}")

        load_resume_case_data(solver, source_case, source_data)
        # The source pair is the recovery point. The pressure is the only
        # intentional delta, and is read back before the sibling is written.
        outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"]
        outlet.phase["mixture"].momentum.gauge_pressure.value = pressure_mpa * 1_000_000.0
        readback = verify_start_state(solver, branch=args.branch, pressure_mpa=pressure_mpa)
        write_case_data_pair(
            solver,
            prepared_case,
            prepared_data,
            f"prepare_{args.branch}_{tag}",
        )

        load_resume_case_data(solver, prepared_case, prepared_data)
        prepared_readbacks[f"{args.branch}:{pressure_mpa:.3f}MPa"] = verify_start_state(
            solver,
            branch=args.branch,
            pressure_mpa=pressure_mpa,
        )
        children.append(
            {
                "branch": args.branch,
                "pressure_mpa": pressure_mpa,
                "pressure_pa": pressure_mpa * 1_000_000.0,
                "source_case": source_case,
                "source_data": source_data,
                "prepared_case": prepared_case,
                "prepared_data": prepared_data,
                "endpoint_case": endpoint_case,
                "endpoint_data": endpoint_data,
                "transcript": transcript,
                "residual_file": residual_file,
                "prepare_readback": readback,
            }
        )

    remote_journal = str(
        PureWindowsPath(REMOTE_DIR)
        / f"FG-MIX-T01-S3-{args.branch}-pressure-sensitivity-200step-{args.run_stamp}.jou"
    )
    if remote_file_exists(solver, remote_journal):
        raise FileExistsError(f"Refusing to overwrite pressure-sensitivity journal: {remote_journal}")
    journal = render_journal(children)
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    if not args.prepare_only:
        write_remote_journal(solver, remote_journal, journal)

    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S3",
        "purpose": "shortened brine-outlet pressure sensitivity",
        "branch": args.branch,
        "mesh": stage3["mesh"],
        "mesh_readback": stage3.get("mesh_readback", {}),
        "pressure_grid_mpa": list(PRESSURES_MPA),
        "time_step_s": TIME_STEP_S,
        "native_transient_steps": TRANSIENT_STEPS,
        "physical_horizon_s": TIME_STEP_S * TRANSIENT_STEPS,
        "max_iter_per_time_step": MAX_ITER_PER_TIMESTEP,
        "source_stage3_manifest": str(args.stage3_manifest.expanduser().resolve()),
        "source_case": source_case,
        "source_data": source_data,
        "prepared_readbacks": prepared_readbacks,
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "children": children,
        "status": "PREPARED_ONLY" if args.prepare_only else "SUBMITTED_NATIVE_RUN",
        "fluent_version": fluent_version,
    }
    manifest_path = args.manifest_json.expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    if args.prepare_only:
        print("pressure_sensitivity_prepared_only: true", flush=True)
    else:
        solver.settings.file.read_journal(file_name_list=[remote_journal])
        print(f"native_journal_submitted: {remote_journal}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
