#!/usr/bin/env python3
"""Run the prepared Phase-07 Coupled + Global Time Step branch.

This recovery runner intentionally starts from the already verified prepared
two-zone state left live in Fluent after the build stage.  It does not reload,
split, reinitialize, or overwrite the prepared parent; it only verifies the
live topology and solver path, redirects evidence files to a fresh OneDrive
run root, and executes the declared 10,000-iteration discovery horizon.
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

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, density_from_case, fluid_names, read_source_tree  # noqa: E402
from run_p7_e5_cz_absorb import configure_inventory_reports, redirect_all_reports  # noqa: E402
import run_p7_e5_cz_absorb_cold as cold  # noqa: E402
from run_p7_e5_cz_absorb_cold import run_discovery  # noqa: E402
from run_p7_treatment_screen import data_path, save_pair  # noqa: E402


CANDIDATE = "P7-E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO-10K"
FAMILY = "E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO"
REPORT_STEM = "S3-C3-10K"
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
HORIZON = 10_000
CHECKPOINTS = (100, 500, 1000, 2500, 5000, 7500, 10_000)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_paths(run_root: str, start_active: int) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "child_start": str(root / f"{CANDIDATE}-active{start_active:03d}.cas.h5"),
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


def normalize_remote_path(value: str) -> str:
    """Collapse accidental doubled Windows separators from shell quoting."""
    return value.replace("\\\\", "\\")


def source_terms_are_zero(source_tree: dict[str, Any]) -> bool:
    """Accept enabled source objects only when every configured value is zero."""
    for zone in source_tree.values():
        if not isinstance(zone, dict):
            continue
        for branch in zone.values():
            if not isinstance(branch, dict):
                continue
            terms = branch.get("terms", {})
            if not isinstance(terms, dict):
                continue
            for entries in terms.values():
                if not isinstance(entries, list):
                    entries = [entries]
                for entry in entries:
                    if not isinstance(entry, dict) or entry.get("option") != "value":
                        continue
                    try:
                        if abs(float(entry.get("value", 0.0))) > 1.0e-14:
                            return False
                    except (TypeError, ValueError):
                        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="3")
    parser.add_argument("--prepared-case", required=True)
    parser.add_argument("--prepared-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    parser.add_argument("--start-active", type=int, default=10)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite Coupled 10k recovery evidence")

    if args.start_active < 0 or args.start_active > HORIZON:
        raise ValueError(f"invalid --start-active={args.start_active}; horizon={HORIZON}")
    args.prepared_case = normalize_remote_path(args.prepared_case)
    args.prepared_data = normalize_remote_path(args.prepared_data)
    args.run_root = normalize_remote_path(args.run_root)
    cold.HORIZON = HORIZON
    cold.CHECKPOINTS = CHECKPOINTS
    paths = build_paths(args.run_root, args.start_active)
    remote_artifacts = [path for key, path in paths.items() if key != "monitor_root"]
    remote_artifacts += [data_path(path) for path in remote_artifacts]
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery-coupled-global-pseudo-10k-from-prepared-live-state",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP3", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP3', 'unknown')}",
        "reference_setup_id": "P7-E0-REF",
        "prepared_case": args.prepared_case,
        "prepared_data": args.prepared_data,
        "run_root": args.run_root,
        "solver_path_delta": "SIMPLE -> Coupled plus steady Global Time Step",
        "final_absorber_rate_kg_s": 116.92,
        "ramp_iterations": 100,
        "update_interval_active_iterations": 10,
        "start_active_iteration": args.start_active,
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
            raise FileExistsError(f"refusing to overwrite Coupled 10k recovery artifacts: {existing}")
        if not remote_file_exists(solver, args.prepared_case) or not remote_file_exists(solver, args.prepared_data):
            raise FileNotFoundError(f"prepared pair is not visible on server {args.server_id}: {args.prepared_case}; {args.prepared_data}")

        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        zones = fluid_names(solver)
        if set(zones) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"prepared live topology mismatch: {zones}")
        density = density_from_case(solver)
        manifest["prepared_live_readback"] = {
            "fluid_zones": zones,
            "base_invariants": base_invariants(solver),
            "liquid_density_kg_m3": density,
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "prepared live runtime state"),
            "source_tree_before_run": read_source_tree(solver),
            "solver_path": configure_coupled_global_pseudo(solver),
        }
        source_tree = read_source_tree(solver)
        if not source_terms_are_zero(source_tree):
            raise RuntimeError("prepared live state has nonzero source terms before the zero-rate ramp start")

        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        # Keep report filenames below Windows' path-length limit.  Case/data
        # checkpoints retain the full scientific candidate name; monitor
        # files use this short, manifest-recorded stem.
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], REPORT_STEM)
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

        if args.start_active > 0:
            save_pair(solver, paths["child_start"])
            manifest["events"].append(
                {
                    "event": "resume_start_saved",
                    "active_iteration": args.start_active,
                    "case": paths["child_start"],
                    "source_state": "zero-rate state immediately after the prior 10-iteration block",
                }
            )
            write_json(args.manifest, manifest)

        run_discovery(
            solver,
            paths,
            manifest["report_files"],
            capture,
            manifest,
            args.manifest,
            density,
            save_initial=args.start_active == 0,
            start_active=args.start_active,
        )
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
        manifest["final_live_readback"] = {
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
