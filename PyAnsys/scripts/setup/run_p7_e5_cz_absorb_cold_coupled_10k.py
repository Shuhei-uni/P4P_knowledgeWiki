#!/usr/bin/env python3
"""Build and run the Phase-07 absorber with Coupled + Global Time Step.

The case is rebuilt from the exact E0 case/data pair visible in the server-3
OneDrive tree.  The only solver-path delta from the original control is
pressure-based Coupled plus the Coupled-compatible steady Global Time Step
formulation.  The absorber remains the lower-zone phase-2 mass sink with
matched mixture momentum source and the same 100-iteration ramp to 116.92 kg/s.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, density_from_case, disable_sources, fluid_names, read_source_tree, split_lower_zone  # noqa: E402
from run_p7_e5_cz_absorb import configure_inventory_reports, redirect_all_reports  # noqa: E402
import run_p7_e5_cz_absorb_cold as cold  # noqa: E402
from run_p7_e5_cz_absorb_cold import run_discovery  # noqa: E402
from run_p7_treatment_screen import data_path, parse_residuals, save_pair  # noqa: E402


CANDIDATE = "P7-E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO-10K"
FAMILY = "E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO"
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
HORIZON = 10_000
CHECKPOINTS = (100, 500, 1000, 2500, 5000, 7500, 10_000)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_paths(run_root: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "pre_split_recovery": str(root / f"{CANDIDATE}-pre-split-recovery.cas.h5"),
        "split_source_off": str(root / f"{CANDIDATE}-split-source-off.cas.h5"),
        "prepared": str(root / f"{CANDIDATE}-prepared.cas.h5"),
        "child_start": str(root / f"{CANDIDATE}-active000.cas.h5"),
        "smoke": str(root / f"{CANDIDATE}-active050.cas.h5"),
        "checkpoint100": str(root / f"{CANDIDATE}-active100.cas.h5"),
        "checkpoint500": str(root / f"{CANDIDATE}-active500.cas.h5"),
        "checkpoint1000": str(root / f"{CANDIDATE}-active1000.cas.h5"),
        "checkpoint2500": str(root / f"{CANDIDATE}-active2500.cas.h5"),
        "checkpoint5000": str(root / f"{CANDIDATE}-active5000.cas.h5"),
        "checkpoint7500": str(root / f"{CANDIDATE}-active7500.cas.h5"),
        "final": str(root / f"{CANDIDATE}-active10000.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def configure_coupled_global_pseudo(solver: Any) -> dict[str, Any]:
    methods = solver.settings.solution.methods
    methods.p_v_coupling.flow_scheme.set_state("Coupled")
    methods.pseudo_time_method.formulation.coupled_solver.set_state("global-time-step")
    coupling = safe_get_state(methods.p_v_coupling, "Coupled readback")
    formulation = safe_get_state(methods.pseudo_time_method.formulation, "Global Time Step readback")
    if not isinstance(coupling, dict) or coupling.get("flow_scheme") != "Coupled":
        raise RuntimeError(f"Coupled readback mismatch: {coupling}")
    if not isinstance(formulation, dict) or formulation.get("coupled_solver") != "global-time-step":
        raise RuntimeError(f"Global Time Step readback mismatch: {formulation}")
    return {"pressure_velocity_coupling": coupling, "pseudo_time_formulation": formulation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="3")
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite Coupled 10k evidence")

    # The shared cold runner owns the absorber schedule and discovery loop.
    # Override only its declared horizon/checkpoints for this explicitly
    # requested long branch; no physical/source constants are changed.
    cold.HORIZON = HORIZON
    cold.CHECKPOINTS = CHECKPOINTS
    paths = build_paths(args.run_root)
    remote_artifacts = [path for key, path in paths.items() if key != "monitor_root"]
    remote_artifacts += [data_path(path) for path in remote_artifacts]
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery-coupled-global-pseudo-10k",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP3", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP3', 'unknown')}",
        "reference_setup_id": "P7-E0-REF",
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "solver_path_delta": "SIMPLE -> Coupled plus steady Global Time Step",
        "final_absorber_rate_kg_s": 116.92,
        "ramp_iterations": 100,
        "update_interval_active_iterations": 10,
        "requested_active_iterations": HORIZON,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        existing = [path for path in remote_artifacts if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite Coupled 10k artifacts: {existing}")
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"exact E0 pair is not visible on server {args.server_id}: {args.parent_case}; {args.parent_data}")

        remote_chdir(solver, str(PureWindowsPath(args.parent_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()
        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        if fluid_names(solver) != [PARENT_ZONE]:
            raise RuntimeError(f"exact E0 topology mismatch: {fluid_names(solver)}")
        density = density_from_case(solver)
        manifest["initialized_parent_readback"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "liquid_density_kg_m3": density,
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "initialized runtime state"),
        }

        split = split_lower_zone(solver, capture)
        manifest["mesh_split"] = split
        disable_sources(solver)
        manifest["split_source_off_readback"] = read_source_tree(solver)
        solver.settings.file.write_case(file_name=paths["pre_split_recovery"])
        solver.settings.file.write_data(file_name=data_path(paths["pre_split_recovery"]))
        solver.settings.file.write_case(file_name=paths["split_source_off"])
        solver.settings.file.write_data(file_name=data_path(paths["split_source_off"]))
        manifest["events"].append({"event": "split_source_off_saved", "case": paths["split_source_off"]})

        manifest["solver_path_readback_before_save"] = configure_coupled_global_pseudo(solver)
        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        manifest["residual_configuration"] = configure_residual_history(solver, HORIZON + 200)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=1000)
        manifest["source_contract"] = {
            "parent_zone": PARENT_ZONE,
            "lower_zone": LOWER_ZONE,
            "phase2_mass_only": True,
            "direct_phase1_mass_source": "off",
            "mixture_momentum_components": ["x", "y", "z"],
            "patch_reset_route": "excluded",
            "outlet_change": "excluded",
        }
        write_json(args.manifest, manifest)

        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("Coupled 10k prepared pair was not saved")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        if set(fluid_names(solver)) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"prepared Coupled topology mismatch: {fluid_names(solver)}")
        manifest["prepared_reopen"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
            "solver_path": configure_coupled_global_pseudo(solver),
        }
        report_paths = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE + "-REOPEN")
        manifest["report_files_after_reopen"] = report_paths
        write_json(args.manifest, manifest)

        run_discovery(solver, paths, report_paths, capture, manifest, args.manifest, density, save_initial=True, start_active=0)
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
        solver.settings.file.read_case(file_name=paths["final"])
        solver.settings.file.read_data(file_name=data_path(paths["final"]))
        manifest["final_readback"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
            "solver_path": configure_coupled_global_pseudo(solver),
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "final runtime state"),
        }
        manifest["status"] = "COMPLETE"
        write_json(args.manifest, manifest)
        capture.close()
        print(json.dumps(manifest, indent=2, default=str))
        return 0
    except Exception as exc:
        if capture is not None:
            capture.close()
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        write_json(args.manifest, manifest)
        print(json.dumps(manifest, indent=2, default=str), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
