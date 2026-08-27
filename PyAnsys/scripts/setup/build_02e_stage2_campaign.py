#!/usr/bin/env python3
"""Build the four independent Setup 02e Stage-2 children.

The saved Y010 parent remains the initialization source.  This builder loads
that parent separately for each child, recreates the common Stage-2 monitor
package (including total-domain liquid volume), applies only the requested
brine-outlet change, verifies the readback, and writes paired case/data
artifacts.  It does not initialize, iterate, or own a solver run loop.
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
    remote_file_exists,
    require_remote_files,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
import build_02e_y010_campaign as stage1  # noqa: E402


DEFAULT_REMOTE_DIR = stage1.DEFAULT_REMOTE_DIR
STAGE2_PREFIX = "02e_stage2_y010"
STAGE2_CASES = (
    ("02e-PO-S2-A", "PO", "po-p1175", 1_175_000.0, "1.175 MPa"),
    ("02e-PO-S2-B", "PO", "po-p1190", 1_190_000.0, "1.190 MPa"),
    ("02e-OV-S2-A", "OV", "ov-k3", 3.0, "K=3"),
    ("02e-OV-S2-B", "OV", "ov-k7", 7.0, "K=7"),
)


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def resolve_fluid_zone(solver: Any) -> str:
    state = safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones")
    fluid = state.get("fluid", {}) if isinstance(state, Mapping) else {}
    names = [str(name) for name in fluid if str(name) != "settings"]
    if len(names) != 1:
        raise RuntimeError(f"Expected one fluid cell zone for total-domain monitor; found {names}")
    return names[0]


def set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        pass


def configure_stage2_monitors(solver: Any, zones: Mapping[str, str], fluid_zone: str) -> dict[str, Any]:
    """Create uniquely named Stage-2 histories on the loaded parent."""
    root = solver.settings.solution.report_definitions
    flux = root.flux
    volume = root.volume
    surfaces = {
        "liquid_inlet": zones["liquid_inlet"],
        "steam_inlet": zones["steam_inlet"],
        "brine_outlet": zones["brine_outlet"],
        "steam_outlet": zones["steam_outlet"],
    }
    definitions: list[dict[str, Any]] = []
    for phase in ("phase-1", "phase-2"):
        for role, surface in surfaces.items():
            name = f"{STAGE2_PREFIX}_flux_{phase.replace('-', '')}_{role}"
            report = stage1._replace_named_report(flux, name)
            report.report_type = "flux-massflow"
            report.boundaries = [surface]
            set_optional(report, "per_selection", False)
            set_optional(report, "average_over", 1)
            set_optional(report, "retain_instantaneous_values", True)
            report.phase = phase
            set_optional(report, "create_report_file", True)
            set_optional(report, "create_report_plot", True)
            definitions.append({"name": name, "kind": "flux", "phase": phase, "surface": surface, "state": report.get_state()})

    for suffix, register, report_type, field, phase in (
        ("inventory_y010_liquid_mass", stage1.Y010_REGISTER, "volume-mass", None, "phase-2"),
        ("inventory_y030_liquid_mass", stage1.Y030_REGISTER, "volume-mass", None, "phase-2"),
        ("inventory_total_liquid_volume", fluid_zone, "volume-integral", "phase-2-vof", "mixture"),
    ):
        name = f"{STAGE2_PREFIX}_{suffix}"
        report = stage1._replace_named_report(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = [register]
        if field is not None:
            report.field = field
        set_optional(report, "per_selection", False)
        set_optional(report, "average_over", 1)
        set_optional(report, "retain_instantaneous_values", True)
        report.phase = phase
        set_optional(report, "create_report_file", True)
        set_optional(report, "create_report_plot", True)
        definitions.append({"name": name, "kind": "volume", "report_type": report_type, "field": field, "cell_zone": register, "phase": phase, "state": report.get_state()})
    return {"prefix": STAGE2_PREFIX, "fluid_zone": fluid_zone, "count": len(definitions), "definitions": definitions}


def build_child(solver: Any, parent_case: str, remote_dir: str, stamp: str, item: tuple[str, str, str, float, str]) -> dict[str, Any]:
    case_id, family, suffix, control, display_control = item
    filename = f"{case_id}-{suffix}-y010-pre-run-{stamp}.cas.h5"
    output = str(PureWindowsPath(remote_dir) / filename)
    data_output = output[:-7] + ".dat.h5"
    stage1.ensure_absent(solver, [output, data_output])
    solver.settings.file.read_case_data(file_name=parent_case)
    zones = stage1.resolve_zones(solver)
    fluid_zone = resolve_fluid_zone(solver)
    monitors = configure_stage2_monitors(solver, zones, fluid_zone)
    if family == "PO":
        stage1.set_pressure_outlet(solver, zones["brine_outlet"], control)
    elif family == "OV":
        stage1.set_outlet_vent(solver, zones["brine_outlet"], control)
    else:
        raise ValueError(family)
    solver.settings.file.write_case(file_name=output)
    solver.settings.file.write_data(file_name=data_output)
    require_remote_files(
        solver,
        (output, data_output),
        "Paired Stage-2 child not visible after write",
    )
    return {
        "case_id": case_id,
        "family": family,
        "control": display_control,
        "control_si": control,
        "pre_run_case": output,
        "pre_run_data": data_output,
        "fluid_zone": fluid_zone,
        "monitor_prefix": STAGE2_PREFIX,
        "monitor_count": monitors["count"],
        "fluent_version": solver.get_fluent_version(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--snapshot-json", required=True)
    args = parser.parse_args()

    solver = connect(server_id=args.server_id)
    if not remote_file_exists(solver, args.parent_case):
        raise FileNotFoundError(f"Y010 parent case is not visible on {args.server_id}: {args.parent_case}")
    records = [build_child(solver, args.parent_case, args.remote_dir, args.stamp, item) for item in STAGE2_CASES]
    payload = {
        "mode": "stage2",
        "parent_case": args.parent_case,
        "children": records,
        "native_iterations_per_case": 500,
        "stage2_cases": [{"case_id": item[0], "family": item[1], "control": item[4]} for item in STAGE2_CASES],
        "fluent_version": solver.get_fluent_version(),
    }
    output = Path(args.snapshot_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
