#!/usr/bin/env python3
"""Probe-first setup script for carrier multiphase + DPM activation.

This is intentionally smaller than setup09a:
- load the target mesh
- apply the carrier multiphase base state
- enable and configure global DPM tracking
- capture live multiphase/DPM trees against the archived 07 seed

The goal is to validate nested Fluent paths before any injection-specific work.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import ansys.fluent.core as pyfluent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.setup_carrier import apply_carrier_general, apply_carrier_models  # noqa: E402
from pyansys_fluent.setup_dpm import apply_dpm_model_settings  # noqa: E402
from pyansys_fluent.setup_io import load_target_mesh, write_case_data_pair  # noqa: E402
from pyansys_fluent.setup_common import load_json, print_header  # noqa: E402
from pyansys_fluent.settings_tree_mapper import capture_settings_tree, compare_tree_shapes  # noqa: E402


DEFAULT_FLUENT_EXE = (
    r"C:\Program Files\ANSYS Inc\ANSYS Student\v261\fluent\ntbin\win64\fluent.exe"
)
DEFAULT_MESH = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended.msh"
)
DEFAULT_SEED_JSON = (
    PROJECT_ROOT
    / "cases"
    / "actual_setup_archives"
    / "07-pure-phase-split-actual-area-live-fff-1-2"
    / "models_tree_detailed.json"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "setup09b_multiphase_dpm_probe"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch Student Fluent and probe multiphase + DPM setup paths.")
    parser.add_argument("--fluent-exe", default=DEFAULT_FLUENT_EXE, help="Path to fluent.exe on the Student PC.")
    parser.add_argument("--mesh", default=DEFAULT_MESH, help="Remote mesh file visible to the Student PC.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for server-info, logs, and JSON outputs.")
    parser.add_argument("--seed-json", default=str(DEFAULT_SEED_JSON), help="Seed archive JSON used for tree comparison.")
    parser.add_argument("--output-case", default="", help="Optional case file to write after the probe.")
    parser.add_argument("--output-data", default="", help="Optional data file to write after the probe.")
    parser.add_argument("--processor-count", type=int, default=2, help="Processor count for the local Fluent launch.")
    parser.add_argument("--start-timeout", type=int, default=120, help="Seconds to wait for the server-info file.")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum recursion depth for tree capture.")
    parser.add_argument("--dpm-max-steps", type=int, default=5000, help="Global DPM max tracking steps.")
    parser.add_argument("--turbulent-dispersion-tries", type=int, default=2, help="DPM turbulent dispersion tries.")
    parser.add_argument("--snapshot-json", default="", help="Optional explicit JSON output path.")
    return parser


def print_kv(key: str, value) -> None:
    print(f"{key}: {value}")


def start_fluent(
    fluent_exe: Path,
    output_dir: Path,
    processor_count: int,
) -> tuple[subprocess.Popen[str], Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    server_info = output_dir / "server_info_setup09b.txt"
    stdout_log = output_dir / "fluent_stdout.log"
    stderr_log = output_dir / "fluent_stderr.log"

    if server_info.exists():
        server_info.unlink()

    args = [
        str(fluent_exe),
        "3ddp",
        f"-t{processor_count}",
        "-g",
        f"-sifile={server_info}",
    ]
    print_kv("launch_command", args)
    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=stdout_log.open("w", encoding="utf-8", errors="replace"),
        stderr=stderr_log.open("w", encoding="utf-8", errors="replace"),
        cwd=str(output_dir),
        text=True,
    )
    print_kv("launch_pid", process.pid)
    return process, server_info, stdout_log, stderr_log


def wait_for_server_info(process: subprocess.Popen[str], server_info: Path, timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_info.exists() and server_info.stat().st_size > 0:
            print_kv("server_info_ready", server_info)
            print(server_info.read_text(encoding="utf-8", errors="replace"))
            return
        if process.poll() is not None:
            raise RuntimeError(f"Fluent exited early with code {process.returncode}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for server-info file: {server_info}")


def resolve_seed_branch(seed_tree: dict[str, object], branch_name: str):
    children = seed_tree.get("children")
    if isinstance(children, dict) and branch_name in children:
        return children[branch_name]
    return None


def capture_branch_summary(branch, label: str, seed_branch, max_depth: int) -> dict[str, object]:
    live_tree = capture_settings_tree(
        branch,
        label,
        max_depth=max_depth,
        include_state=True,
        seed_tree=seed_branch,
    )
    comparison = compare_tree_shapes(live_tree, seed_branch, label) if seed_branch is not None else {
        "missing_children": [],
        "extra_children": [],
        "missing_objects": [],
        "extra_objects": [],
    }
    return {
        "live_tree": live_tree,
        "comparison": comparison,
    }


def main() -> int:
    args = build_parser().parse_args()
    fluent_exe = Path(args.fluent_exe)
    mesh_path = Path(args.mesh)
    output_dir = Path(args.output_dir).resolve()
    seed_path = Path(args.seed_json).expanduser().resolve()
    output_json = Path(args.snapshot_json).expanduser().resolve() if args.snapshot_json else output_dir / "setup09b_multiphase_dpm_probe.json"

    if not fluent_exe.exists():
        print_kv("fluent_exe_missing", fluent_exe)
        return 2
    if not mesh_path.exists():
        print_kv("mesh_missing", mesh_path)
        return 3
    if not seed_path.exists():
        print_kv("seed_json_missing", seed_path)
        return 4

    process = None
    solver = None
    server_info = None
    stdout_log = None
    stderr_log = None

    try:
        process, server_info, stdout_log, stderr_log = start_fluent(
            fluent_exe=fluent_exe,
            output_dir=output_dir,
            processor_count=args.processor_count,
        )
        wait_for_server_info(process, server_info, args.start_timeout)

        solver = pyfluent.connect_to_fluent(
            server_info_file_name=str(server_info),
            cleanup_on_exit=False,
            start_transcript=True,
            allow_remote_host=False,
        )
        print_kv("connect_to_fluent", "OK")
        print_kv("fluent_version", solver.get_fluent_version())

        load_target_mesh(solver, str(mesh_path))
        print_kv("mesh_load", "OK")

        carrier_ok = apply_carrier_general(solver)
        print_kv("carrier_general", carrier_ok)
        carrier_models_ok = apply_carrier_models(solver)
        print_kv("carrier_models", carrier_models_ok)
        dpm_ok = apply_dpm_model_settings(
            solver,
            dpm_max_steps=args.dpm_max_steps,
            one_way_coupling=True,
        )
        print_kv("dpm_model_settings", dpm_ok)

        seed_tree = load_json(seed_path)
        multiphase_seed = resolve_seed_branch(seed_tree, "multiphase")
        dpm_seed = resolve_seed_branch(seed_tree, "discrete_phase")

        multiphase_branch = solver.settings.setup.models.multiphase
        dpm_branch = solver.settings.setup.models.discrete_phase

        multiphase_summary = capture_branch_summary(multiphase_branch, "setup.models.multiphase", multiphase_seed, args.max_depth)
        dpm_summary = capture_branch_summary(dpm_branch, "setup.models.discrete_phase", dpm_seed, args.max_depth)

        payload = {
            "fluent_version": solver.get_fluent_version(),
            "mesh": str(mesh_path),
            "carrier_general_ok": carrier_ok,
            "carrier_models_ok": carrier_models_ok,
            "dpm_model_settings_ok": dpm_ok,
            "multiphase_state": multiphase_branch.get_state(),
            "dpm_state": dpm_branch.get_state(),
            "multiphase_summary": multiphase_summary,
            "dpm_summary": dpm_summary,
        }

        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
        print_kv("snapshot_json", output_json)
        print(json.dumps(
            {
                "multiphase_comparison": multiphase_summary["comparison"],
                "dpm_comparison": dpm_summary["comparison"],
            },
            indent=2,
            default=str,
        ))

        if args.output_case and args.output_data:
            write_case_data_pair(solver, args.output_case, args.output_data, "setup09b_probe")
            print_kv("case_data_write", "OK")
        elif args.output_case or args.output_data:
            raise RuntimeError("--output-case and --output-data must be provided together")

        return 0
    except Exception as exc:
        print_kv("probe_failed", f"{type(exc).__name__}: {exc}")
        if process is not None:
            print_kv("process_alive", process.poll() is None)
            print_kv("process_returncode", process.poll())
        if stdout_log is not None:
            print("stdout_log_tail:")
            lines = stdout_log.read_text(encoding="utf-8", errors="replace").splitlines() if stdout_log.exists() else []
            print("\n".join(lines[-40:]) if lines else "<empty>")
        if stderr_log is not None:
            print("stderr_log_tail:")
            lines = stderr_log.read_text(encoding="utf-8", errors="replace").splitlines() if stderr_log.exists() else []
            print("\n".join(lines[-40:]) if lines else "<empty>")
        return 1
    finally:
        if solver is not None:
            try:
                solver.exit()
                print_kv("solver_exit", "OK")
            except Exception as exc:
                print_kv("solver_exit_failed", exc)
        elif process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=20)
                print_kv("process_terminate", "OK")
            except Exception as exc:
                print_kv("process_terminate_failed", exc)


if __name__ == "__main__":
    raise SystemExit(main())
