#!/usr/bin/env python3
"""Run the Purnanto paper enthalpy sweep and export DPM injection results.

The script is intentionally explicit about the paper cases.  It reads the
Harwell injection bins from the local CSV, but it uses the steam/liquid phase
mass-flow table from the Purnanto paper for the boundary condition values.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import math
import re
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    quote_scheme_string,
    remote_chdir,
    remote_file_exists,
    safe_get_state,
    try_action,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402
from pyansys_fluent.setup_common import print_header, require_remote_input  # noqa: E402


DEFAULT_BASE_CASE = r"C:\Users\qtra338\Documents\baseline.cas.h5"
DEFAULT_REMOTE_OUTPUT_DIR = r"C:\Users\qtra338\Documents\enthalpy_sweep"
DEFAULT_HARWELL_CSV = REPO_ROOT / "Code" / "harwell_results.csv"
DEFAULT_LOCAL_OUTPUT_DIR = PROJECT_ROOT / "output" / "enthalpy_sweep"
DEFAULT_ITERATIONS = 1500
DEFAULT_REPORT_INTERVAL = 100
DEFAULT_CHECKPOINT_INTERVAL = 500
DEFAULT_DPM_VELOCITY_MODE = "face-normal"
DEFAULT_GAS_PHASE_MATERIAL = "water-vapor-at-psep"
DEFAULT_LIQUID_PHASE_MATERIAL = "water-liquid-at-psep"
DPM_MASS_FLOW_BASIS = "Final"
REMOTE_REPORT_SCRATCH_SUFFIX = "_scratch.txt"

INLET_NAME = "inlet"
OUTLET_NAME = "steam_outlet"
PARTICLE_MATERIAL = "water-liquid-dpm"
INJECTION_SURFACE = "inlet"
INJECTION_COUNT = 9
INJECTION_NAMES: tuple[str, ...] = tuple(f"injection-{index}" for index in range(INJECTION_COUNT))


@dataclass(frozen=True)
class PaperCase:
    case_number: int
    csv_case: str
    condition: str
    liquid_mass_flow_kgs: float
    gas_mass_flow_kgs: float

    @property
    def slug(self) -> str:
        return slugify(self.condition)


@dataclass(frozen=True)
class InjectionBin:
    injection_number: int
    injection_name: str
    x_xmed: float
    diameter_mm: float
    diameter_m: float
    mass_flow_kgs: float
    z_velocity_ms: float


PAPER_CASES: tuple[PaperCase, ...] = (
    PaperCase(1, "Case 1", "1600 -25%", 87.69, 60.52),
    PaperCase(2, "Case 2", "1440", 132.76, 64.85),
    PaperCase(3, "Case 3", "1520", 124.84, 72.77),
    PaperCase(4, "Case 4", "1600", 116.92, 80.69),
    PaperCase(5, "Case 5", "1680", 109.00, 88.61),
    PaperCase(6, "Case 6", "1760", 101.09, 96.52),
)


class RunInterrupted(Exception):
    def __init__(self, completed_iterations: int):
        super().__init__(f"Run interrupted after approximately {completed_iterations} iterations")
        self.completed_iterations = completed_iterations


def slugify(text: str) -> str:
    slug = text.strip().lower().replace("%", "pct")
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def remote_join(directory: str, filename: str) -> str:
    return str(PureWindowsPath(directory) / filename)


def ti_menu(solver: Any, command: str) -> Any:
    return solver.scheme.exec((f'(ti-menu-load-string "{command}")',))


def case_prefix(case: PaperCase) -> str:
    return f"case_{case.case_number}_{case.slug}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the six paper-table Purnanto enthalpy conditions with Harwell DPM bins."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Validate and print the sweep plan only.")
    mode.add_argument("--apply", action="store_true", help="Connect to Fluent and execute the sweep.")
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--base-case", default=DEFAULT_BASE_CASE, help="Remote Fluent base case path.")
    parser.add_argument(
        "--harwell-csv",
        default=str(DEFAULT_HARWELL_CSV),
        help="Local Harwell injection CSV path.",
    )
    parser.add_argument(
        "--remote-output-dir",
        default=DEFAULT_REMOTE_OUTPUT_DIR,
        help="Remote Windows output folder visible to Fluent.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(DEFAULT_LOCAL_OUTPUT_DIR),
        help="Local folder for parsed CSV/manifests and captured reports.",
    )
    parser.add_argument("--inlet-name", default=INLET_NAME, help="Mass-flow inlet zone name.")
    parser.add_argument("--outlet-name", default=OUTLET_NAME, help="Pressure-outlet zone name.")
    parser.add_argument(
        "--particle-material",
        default=PARTICLE_MATERIAL,
        help="Existing Fluent inert-particle material assigned to all injections.",
    )
    parser.add_argument(
        "--gas-phase-material",
        default=DEFAULT_GAS_PHASE_MATERIAL,
        help="Required material readback for phase-1 before applying gas mass flow.",
    )
    parser.add_argument(
        "--liquid-phase-material",
        default=DEFAULT_LIQUID_PHASE_MATERIAL,
        help="Required material readback for phase-2 before applying liquid mass flow.",
    )
    parser.add_argument(
        "--allow-coupled-dpm",
        action="store_true",
        help=(
            "Allow inherited DPM interaction with the continuous phase. By default the "
            "replication requires one-way DPM so injections cannot affect the 1500-iteration carrier solve."
        ),
    )
    parser.add_argument(
        "--injection-surface",
        default=INJECTION_SURFACE,
        help="Surface used by all DPM injections.",
    )
    parser.add_argument(
        "--injection-names",
        default=",".join(INJECTION_NAMES),
        help="Nine comma-separated existing injection names, ordered from CSV bin 1 to bin 9.",
    )
    parser.add_argument(
        "--seed-results-csv",
        action="append",
        default=[],
        help="Optional prior per-injection CSV rows to include in combined sweep outputs.",
    )
    parser.add_argument(
        "--seed-case-summary-csv",
        action="append",
        default=[],
        help="Optional prior case-summary CSV rows to include in combined sweep outputs.",
    )
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Flow iterations per case.")
    parser.add_argument(
        "--iteration-mode",
        choices=("chunked", "single"),
        default="chunked",
        help=(
            "How to submit Fluent iterations. 'chunked' runs repeated blocks of --report-interval "
            "iterations so Python can checkpoint between blocks. 'single' submits one Fluent "
            "iterate command per case, preserving a cleaner GUI residual history."
        ),
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=DEFAULT_REPORT_INTERVAL,
        help="Iteration chunk size in chunked mode, and Fluent reporting interval in single mode.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=DEFAULT_CHECKPOINT_INTERVAL,
        help="Remote autosave interval. Use 0 to disable.",
    )
    parser.add_argument(
        "--residual-history-points",
        type=int,
        default=2000,
        help="Best-effort residual monitor n-save/n-display value applied before iteration. Use 0 to skip.",
    )
    parser.add_argument(
        "--case-filter",
        action="append",
        default=[],
        help=(
            "Restrict cases. Accepts case number, e.g. 4, condition, e.g. 1600, "
            "or slug, e.g. 1600_minus25pct. Can be repeated."
        ),
    )
    parser.add_argument(
        "--initialize",
        choices=("auto", "hybrid", "none"),
        default="hybrid",
        help="Initialization after reading the base case. Default: hybrid.",
    )
    parser.add_argument(
        "--allow-early-convergence",
        action="store_true",
        help="Allow Fluent residual convergence checks to stop before the requested iteration count.",
    )
    parser.add_argument(
        "--dpm-velocity-mode",
        choices=("face-normal", "components"),
        default=DEFAULT_DPM_VELOCITY_MODE,
        help=(
            "How to apply Harwell injection velocity. Default face-normal uses Fluent's "
            "face-normal direction option and the CSV speed magnitude. Components uses "
            "x=0, y=0, z=z_velocity_ms from the CSV."
        ),
    )
    parser.add_argument(
        "--no-dpm-report",
        action="store_true",
        help="Skip DPM reports/results parsing. Useful for a one-iteration smoke test.",
    )
    parser.add_argument(
        "--allow-missing-escaped",
        action="store_true",
        help="Do not fail if escaped_kgs cannot be parsed from the DPM reports.",
    )
    parser.add_argument(
        "--allow-count-based-escaped-fallback",
        action="store_true",
        help=(
            "Permit escaped mass to be estimated from particle counts when no DPM mass-flow "
            "table is available. This is disabled by default because trajectory counts need "
            "not be proportional to mass."
        ),
    )
    return parser


def selected_cases(filters: Sequence[str]) -> list[PaperCase]:
    if not filters:
        return list(PAPER_CASES)

    wanted = {value.strip().lower() for value in filters if value.strip()}
    selected: list[PaperCase] = []
    for case in PAPER_CASES:
        candidates = {
            str(case.case_number).lower(),
            case.csv_case.lower(),
            case.condition.lower(),
            case.slug.lower(),
        }
        if wanted & candidates:
            selected.append(case)

    missing = wanted - {
        candidate
        for case in PAPER_CASES
        for candidate in {
            str(case.case_number).lower(),
            case.csv_case.lower(),
            case.condition.lower(),
            case.slug.lower(),
        }
    }
    if missing:
        raise ValueError(f"Unknown --case-filter value(s): {', '.join(sorted(missing))}")
    return selected


def parse_float(row: Mapping[str, str], key: str) -> float:
    return float(row[key].strip())


def read_harwell_bins(csv_path: Path) -> dict[tuple[str, str], list[InjectionBin]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Harwell CSV not found: {csv_path}")

    groups: dict[tuple[str, str], list[InjectionBin]] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "case",
            "enthalpy_kJkg",
            "inj",
            "x_xmed",
            "diameter_mm",
            "diameter_m",
            "mass_flow_kgs",
            "z_velocity_ms",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Harwell CSV is missing required column(s): {', '.join(sorted(missing))}")

        for row in reader:
            case_name = row["case"].strip()
            condition = row["enthalpy_kJkg"].strip()
            injection_number = int(row["inj"])
            groups.setdefault((case_name, condition), []).append(
                InjectionBin(
                    injection_number=injection_number,
                    injection_name=INJECTION_NAMES[injection_number - 1],
                    x_xmed=parse_float(row, "x_xmed"),
                    diameter_mm=parse_float(row, "diameter_mm"),
                    diameter_m=parse_float(row, "diameter_m"),
                    mass_flow_kgs=parse_float(row, "mass_flow_kgs"),
                    z_velocity_ms=parse_float(row, "z_velocity_ms"),
                )
            )

    for key, bins in groups.items():
        bins.sort(key=lambda item: item.injection_number)
    return groups


def validate_case_bins(case: PaperCase, bins: Sequence[InjectionBin]) -> None:
    if len(bins) != INJECTION_COUNT:
        raise ValueError(f"{case.csv_case} / {case.condition} has {len(bins)} bins, expected {INJECTION_COUNT}")

    numbers = [item.injection_number for item in bins]
    if numbers != list(range(1, INJECTION_COUNT + 1)):
        raise ValueError(f"{case.csv_case} / {case.condition} injection numbers are {numbers}, expected 1..9")

    total = sum(item.mass_flow_kgs for item in bins)
    if abs(total - case.liquid_mass_flow_kgs) > 0.03:
        raise ValueError(
            f"{case.csv_case} / {case.condition} DPM mass total {total:.6f} kg/s "
            f"does not match paper liquid flow {case.liquid_mass_flow_kgs:.6f} kg/s"
        )


def build_sweep_plan(cases: Sequence[PaperCase], groups: Mapping[tuple[str, str], list[InjectionBin]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for case in cases:
        key = (case.csv_case, case.condition)
        if key not in groups:
            raise ValueError(f"Harwell CSV does not contain required group: {case.csv_case} / {case.condition}")
        bins = groups[key]
        validate_case_bins(case, bins)
        plan.append(
            {
                "case": case,
                "bins": bins,
                "dpm_total_mass_flow_kgs": sum(item.mass_flow_kgs for item in bins),
            }
        )
    return plan


def print_dry_run(plan: Sequence[Mapping[str, Any]]) -> None:
    print_header("Dry Run Sweep Plan")
    print("case\tcondition\tliquid_kgs\tgas_kgs\tbins\tdpm_total_kgs\tz_velocity_ms\tnormal_speed_ms")
    for item in plan:
        case: PaperCase = item["case"]
        bins: Sequence[InjectionBin] = item["bins"]
        print(
            f"{case.csv_case}\t{case.condition}\t{case.liquid_mass_flow_kgs:.6g}\t"
            f"{case.gas_mass_flow_kgs:.6g}\t{len(bins)}\t"
            f"{item['dpm_total_mass_flow_kgs']:.6f}\t{bins[0].z_velocity_ms:.6g}\t"
            f"{abs(bins[0].z_velocity_ms):.6g}"
        )


def ensure_local_output_dir(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def remote_text_write_best_effort(solver: Any, path_text: str, text: str) -> bool:
    """Write a small text file on the Fluent host through Scheme."""
    try:
        quoted_path = quote_scheme_string(path_text)
        quoted_text = quote_scheme_string(text)
        remote_delete_best_effort(solver, path_text)
        expression = (
            f'(let ((p (open-output-file "{quoted_path}"))) '
            f'(display "{quoted_text}" p) '
            "(close-output-port p))"
        )
        solver.scheme.eval(expression)
        return True
    except Exception as exc:
        print(f"remote_text_write: FAILED for {path_text} -> {exc}")
        return False


def remote_delete_best_effort(solver: Any, path_text: str) -> bool:
    try:
        if not remote_file_exists(solver, path_text):
            return True
        delete_cmd = f'cmd /c if exist "{path_text}" del /f /q "{path_text}" >nul 2>nul'
        solver.scheme.eval(f'(system "{quote_scheme_string(delete_cmd)}")')
        return not remote_file_exists(solver, path_text)
    except Exception as exc:
        print(f"remote_delete: FAILED for {path_text} -> {exc}")
        return False


def remote_text_read_best_effort(solver: Any, path_text: str) -> str:
    """Read a small text file from the Fluent host through Scheme."""
    try:
        if not remote_file_exists(solver, path_text):
            return ""
        quoted_path = quote_scheme_string(path_text)
        expression = (
            f'(let ((p (open-input-file "{quoted_path}"))) '
            "(let loop ((chars '())) "
            "(let ((c (read-char p))) "
            "(if (eof-object? c) "
            "(begin (close-input-port p) (list->string (reverse chars))) "
            "(loop (cons c chars))))))"
        )
        value = solver.scheme.eval(expression)
        return "" if value is None else str(value)
    except Exception as exc:
        print(f"remote_text_read: FAILED for {path_text} -> {exc}")
        return ""


def ensure_remote_directory_best_effort(solver: Any, path_text: str) -> bool:
    if remote_file_exists(solver, path_text):
        return True

    mkdir_cmd = f'cmd /c mkdir "{path_text}"'
    try:
        solver.scheme.eval(f'(system "{quote_scheme_string(mkdir_cmd)}")')
        if remote_file_exists(solver, path_text):
            print(f"remote_output_dir: created {path_text}")
            return True
    except Exception as exc:
        print(f"remote_output_dir system mkdir failed: {exc}")

    print(f"remote_output_dir: could not create {path_text}; save operations may fail if it does not exist")
    return False


def read_rpvar(solver: Any, name: str) -> Any:
    return solver.scheme.eval(f"(rpgetvar '{name})")


def set_rpvar(solver: Any, name: str, value: Any) -> None:
    if isinstance(value, str):
        encoded = f'"{quote_scheme_string(value)}"'
    elif isinstance(value, bool):
        encoded = "#t" if value else "#f"
    else:
        encoded = str(value)
    solver.scheme.eval(f"(rpsetvar '{name} {encoded})")


def disable_inherited_fluent_autosave(
    solver: Any,
    remote_output_dir: str,
    prefix: str,
) -> dict[str, Any]:
    """Disable Workbench autosave paths; Python writes verified checkpoints instead."""
    frequency_names = (
        "autosave/frequency/data",
        "autosave/frequency/case",
        "mmp/autosave/frequency/data",
        "mmp/autosave/frequency/case",
    )
    filename_names = ("autosave/filename", "mmp/autosave/filename")
    before = {name: read_rpvar(solver, name) for name in (*frequency_names, *filename_names)}
    # Fluent Scheme preserves doubled backslashes in RP string values; forward
    # slashes are accepted by Fluent on Windows and round-trip unambiguously.
    safe_root = remote_join(remote_output_dir, f"{prefix}_internal_autosave_disabled").replace("\\", "/")
    for name in frequency_names:
        set_rpvar(solver, name, 0)
    for name in filename_names:
        set_rpvar(solver, name, safe_root)
    after = {name: read_rpvar(solver, name) for name in (*frequency_names, *filename_names)}
    failed = [name for name in frequency_names if int(after[name]) != 0]
    stale = [name for name in filename_names if str(after[name]) != safe_root]
    if failed or stale:
        raise RuntimeError(f"Could not sanitize Fluent autosave state: frequency={failed}, filename={stale}")
    payload = {"before": before, "after": after, "python_checkpoints_enabled": True}
    print(f"fluent_internal_autosave: VERIFIED disabled -> {json.dumps(payload, default=str)}")
    return payload


def write_local_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_local_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_seed_csv(path_text: str, required_fields: Sequence[str], label: str) -> list[dict[str, str]]:
    if not path_text:
        return []
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(required_fields) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{label} missing columns: {sorted(missing)}")
        rows = [dict(row) for row in reader]
    print(f"{label}: loaded {len(rows)} rows from {path}")
    return rows


def rows_to_csv_text(rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> str:
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return handle.getvalue()


def read_iteration_count(solver: Any) -> int | None:
    try:
        value = solver.scheme.eval("(rpgetvar 'number-of-iterations)")
        return int(value)
    except Exception:
        return None


def load_base_case(solver: Any, base_case: str) -> None:
    print_header("Load Base Case")
    require_remote_input(solver, base_case, "base case")
    remote_chdir(solver, str(PureWindowsPath(base_case).parent))
    if not try_action("read_base_case", lambda: solver.settings.file.read_case(file_name=base_case)):
        raise RuntimeError(f"Could not read base case: {base_case}")
    # A Workbench-origin case can restore a stale working directory while loading.
    remote_chdir(solver, str(PureWindowsPath(base_case).parent))


def maybe_initialize(solver: Any, mode: str) -> None:
    if mode == "none":
        print("initialize: SKIPPED by --initialize none")
        return
    print_header("Hybrid Initialization")
    if try_action("hybrid_initialize_settings_api", lambda: solver.settings.solution.initialization.hybrid_initialize()):
        return
    if try_action("hybrid_initialize_tui", lambda: solver.tui.solve.initialize.hyb_initialization()):
        return
    if try_action("hybrid_initialize_scheme_tui", lambda: ti_menu(solver, "/solve/initialize/hyb-initialization")):
        return
    raise RuntimeError("Failed to hybrid-initialize case")


def scalar_setting_state(setting: Any) -> Any:
    """Return a scalar setting without assuming one PyFluent wrapper shape."""
    try:
        state = setting.get_state()
    except Exception:
        state = setting()
    if isinstance(state, Mapping):
        for key in ("value", "option", "material", "enabled"):
            if key in state and len(state) == 1:
                return state[key]
    return state


def require_case_physics(
    solver: Any,
    *,
    gas_phase_material: str,
    liquid_phase_material: str,
    allow_coupled_dpm: bool,
) -> dict[str, Any]:
    """Verify inherited phase identity and DPM coupling before mutation."""
    print_header("Verify Inherited Physics")
    phases = solver.settings.setup.models.multiphase.phases
    phase_names = sorted(str(name) for name in phases.get_object_names())
    required_names = {"phase-1", "phase-2"}
    missing = sorted(required_names - set(phase_names))
    if missing:
        raise RuntimeError(
            "path/version issue: required multiphase objects are missing: "
            f"{missing}; available={phase_names}"
        )

    phase_materials: dict[str, Any] = {}
    expected_materials = {
        "phase-1": gas_phase_material,
        "phase-2": liquid_phase_material,
    }
    for phase_name, expected in expected_materials.items():
        phase = phases[phase_name]
        actual = scalar_setting_state(phase.material)
        phase_materials[phase_name] = actual
        if str(actual) != expected:
            raise RuntimeError(
                "invalid value/format issue: phase material readback mismatch for "
                f"{phase_name}: expected={expected!r}, actual={actual!r}"
            )

    interaction = solver.settings.setup.models.discrete_phase.general_settings.interaction
    interaction_state = safe_get_state(interaction, "DPM interaction")
    if isinstance(interaction_state, Mapping):
        interaction_enabled = interaction_state.get("enabled")
    else:
        interaction_enabled = interaction_state
    if interaction_enabled is not False and not allow_coupled_dpm:
        raise RuntimeError(
            "invalid value/format issue: the replication requires one-way DPM, but "
            f"interaction.enabled read back as {interaction_enabled!r}. Use "
            "--allow-coupled-dpm only for an explicitly documented sensitivity run."
        )

    readback = {
        "phase_names": phase_names,
        "phase_materials": phase_materials,
        "dpm_interaction": interaction_state,
        "one_way_dpm_required": not allow_coupled_dpm,
    }
    print(json.dumps(readback, indent=2, default=str))
    return readback


def require_current_case_shape(solver: Any) -> None:
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions")
    if not isinstance(boundary_state, Mapping):
        raise RuntimeError("Could not inspect boundary conditions")

    mass_flow_names = set()
    pressure_outlet_names = set()
    for section, target in (("mass_flow_inlet", mass_flow_names), ("pressure_outlet", pressure_outlet_names)):
        values = boundary_state.get(section, {})
        if isinstance(values, Mapping):
            target.update(str(name) for name in values if str(name) != "settings")

    if INLET_NAME not in mass_flow_names:
        raise RuntimeError(f"Expected mass-flow inlet '{INLET_NAME}', found {sorted(mass_flow_names)}")
    if OUTLET_NAME not in pressure_outlet_names:
        raise RuntimeError(f"Expected pressure outlet '{OUTLET_NAME}', found {sorted(pressure_outlet_names)}")

    injection_branch = solver.settings.setup.models.discrete_phase.injections
    try:
        injection_names = set(injection_branch.get_object_names())
    except Exception as exc:
        raise RuntimeError(f"Could not inspect DPM injections: {exc}") from exc

    expected = set(INJECTION_NAMES)
    missing = sorted(expected - injection_names)
    if missing:
        raise RuntimeError(f"Missing expected DPM injections: {missing}")


def set_inlet_phase_mass_flows(solver: Any, case: PaperCase) -> dict[str, Any]:
    print_header("Set Inlet Phase Mass Flows")
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet[INLET_NAME]
    state = inlet.get_state()
    state["phase"]["phase-1"]["momentum"]["mass_flow_rate"] = {
        "option": "value",
        "value": case.gas_mass_flow_kgs,
    }
    state["phase"]["phase-2"]["momentum"]["mass_flow_rate"] = {
        "option": "value",
        "value": case.liquid_mass_flow_kgs,
    }
    if not try_action(f"set_{INLET_NAME}_phase_mass_flows", lambda: inlet.set_state(state)):
        raise RuntimeError("Could not set inlet phase mass flows")
    readback = inlet.get_state()
    print(json.dumps(readback["phase"], indent=2, default=str))
    gas = readback["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"]
    liquid = readback["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"]
    if not math.isclose(float(gas), case.gas_mass_flow_kgs, rel_tol=0.0, abs_tol=1e-8):
        raise RuntimeError(f"Gas mass-flow readback mismatch: expected {case.gas_mass_flow_kgs}, got {gas}")
    if not math.isclose(float(liquid), case.liquid_mass_flow_kgs, rel_tol=0.0, abs_tol=1e-8):
        raise RuntimeError(
            f"Liquid mass-flow readback mismatch: expected {case.liquid_mass_flow_kgs}, got {liquid}"
        )
    return readback


def dpm_velocity_state(item: InjectionBin, mode: str) -> dict[str, Any]:
    if mode == "components":
        return {
            "use_face_normal_direction": False,
            "x_velocity": 0.0,
            "y_velocity": 0.0,
            "z_velocity": item.z_velocity_ms,
        }
    raise ValueError(f"Unsupported DPM velocity mode: {mode}")


def validate_injection_readback(
    item: InjectionBin,
    velocity_mode: str,
    readback: Mapping[str, Any],
) -> None:
    """Validate one injection state without mutating the tracked DPM solution."""
    initial = readback.get("initial_values", {})
    location = initial.get("location", {})
    mass_flow = initial.get("mass_flow_rate", {}).get("total_flow_rate")
    velocity = initial.get("velocity", {})
    particle_size = initial.get("particle_size", {})
    checks = {
        "particle_type": readback.get("particle_type") == "inert",
        "material": readback.get("material") == PARTICLE_MATERIAL,
        "injection_type": readback.get("injection_type", {}).get("option") == "surface",
        "surface": location.get("injection_surfaces") == [INJECTION_SURFACE],
        "mass_flow": mass_flow is not None
        and math.isclose(float(mass_flow), item.mass_flow_kgs, rel_tol=0.0, abs_tol=1e-10),
        "diameter": particle_size.get("diameter") is not None
        and math.isclose(float(particle_size["diameter"]), item.diameter_m, rel_tol=0.0, abs_tol=1e-12),
    }
    if velocity_mode == "face-normal":
        checks["face_normal"] = velocity.get("use_face_normal_direction") is True
        checks["velocity_magnitude"] = velocity.get("magnitude") is not None and math.isclose(
            float(velocity["magnitude"]), abs(item.z_velocity_ms), rel_tol=0.0, abs_tol=1e-8
        )
    else:
        checks["face_normal"] = velocity.get("use_face_normal_direction") is False
        checks["z_velocity"] = velocity.get("z_velocity") is not None and math.isclose(
            float(velocity["z_velocity"]), item.z_velocity_ms, rel_tol=0.0, abs_tol=1e-8
        )
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"{item.injection_name} readback validation failed: {failed}")


def set_single_injection(solver: Any, item: InjectionBin, velocity_mode: str) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    injection = branch[item.injection_name]

    ok = True
    ok &= try_action(
        f"{item.injection_name}_particle_type",
        lambda: setattr(injection, "particle_type", "inert"),
    )
    injection = branch[item.injection_name]
    ok &= try_action(
        f"{item.injection_name}_material",
        lambda: setattr(injection, "material", PARTICLE_MATERIAL),
    )
    injection = branch[item.injection_name]
    ok &= try_action(
        f"{item.injection_name}_injection_type_surface",
        lambda: setattr(injection.injection_type, "option", "surface"),
    )
    injection = branch[item.injection_name]
    ok &= try_action(
        f"{item.injection_name}_location",
        lambda: injection.initial_values.location.set_state(
            {
                "injection_surfaces": [INJECTION_SURFACE],
                "randomized_positions_enabled": False,
            }
        ),
    )
    ok &= try_action(
        f"{item.injection_name}_mass_flow_rate",
        lambda: injection.initial_values.mass_flow_rate.set_state(
            {"total_flow_rate": item.mass_flow_kgs}
        ),
    )
    if velocity_mode == "face-normal":
        ok &= try_action(
            f"{item.injection_name}_use_face_normal_direction",
            lambda: setattr(injection.initial_values.velocity, "use_face_normal_direction", True),
        )
        injection = branch[item.injection_name]
        ok &= try_action(
            f"{item.injection_name}_velocity_magnitude",
            lambda: setattr(injection.initial_values.velocity, "magnitude", abs(item.z_velocity_ms)),
        )
    else:
        ok &= try_action(
            f"{item.injection_name}_velocity",
            lambda: injection.initial_values.velocity.set_state(dpm_velocity_state(item, velocity_mode)),
        )
    ok &= try_action(
        f"{item.injection_name}_particle_size",
        lambda: injection.initial_values.particle_size.set_state(
            {
                "option": "uniform",
                "diameter": item.diameter_m,
            }
        ),
    )
    if not ok:
        raise RuntimeError(f"Could not fully update {item.injection_name}")
    readback = branch[item.injection_name].get_state()
    validate_injection_readback(item, velocity_mode, readback)
    print(f"{item.injection_name}_readback: VERIFIED")
    return readback


def set_dpm_injections(solver: Any, bins: Sequence[InjectionBin], velocity_mode: str) -> dict[str, Any]:
    print_header("Set DPM Injections")
    print(f"DPM velocity mode: {velocity_mode}")
    readbacks: dict[str, Any] = {}
    for item in bins:
        readbacks[item.injection_name] = set_single_injection(solver, item, velocity_mode)
    return readbacks


def read_dpm_injections(
    solver: Any,
    bins: Sequence[InjectionBin],
    velocity_mode: str,
) -> dict[str, Any]:
    """Read and validate injections without changing post-tracking state."""
    print_header("Read DPM Injections")
    branch = solver.settings.setup.models.discrete_phase.injections
    readbacks: dict[str, Any] = {}
    for item in bins:
        readback = branch[item.injection_name].get_state()
        validate_injection_readback(item, velocity_mode, readback)
        readbacks[item.injection_name] = readback
        print(f"{item.injection_name}_readback: VERIFIED")
    return readbacks


def checkpoint_paths(remote_output_dir: str, prefix: str, iteration: int) -> tuple[str, str]:
    return (
        remote_join(remote_output_dir, f"{prefix}_autosave_iter{iteration}.cas.h5"),
        remote_join(remote_output_dir, f"{prefix}_autosave_iter{iteration}.dat.h5"),
    )


def write_case_data_pair(solver: Any, case_file: str, data_file: str, label: str) -> None:
    print_header(label)
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not try_action(f"write_case_{label}", lambda: solver.settings.file.write_case(file_name=case_file)):
        raise RuntimeError(f"Could not write case for {label}")
    if not try_action(f"write_data_{label}", lambda: solver.settings.file.write_data(file_name=data_file)):
        raise RuntimeError(f"Could not write data for {label}")
    missing = [path for path in (case_file, data_file) if not remote_file_exists(solver, path)]
    if missing:
        raise RuntimeError(f"Saved case/data verification failed for {label}: {missing}")
    print(f"saved_pair_{label}: VERIFIED")


def configure_residual_history(solver: Any, points: int) -> None:
    if points <= 0:
        return
    print_header("Configure Residual History")
    try:
        options = solver.settings.solution.monitor.residual.options
    except Exception as exc:
        print(f"residual_history: SKIPPED -> {type(exc).__name__}: {exc}")
        return
    try_action("set_residual_n_save", lambda: setattr(options, "n_save", points))
    try_action("set_residual_n_display", lambda: setattr(options, "n_display", points))
    try_action("enable_residual_print", lambda: setattr(options, "print", True))
    try_action("enable_residual_plot", lambda: setattr(options, "plot", True))


def configure_full_iteration_run(solver: Any, allow_early_convergence: bool) -> dict[str, bool]:
    equations = solver.settings.solution.monitor.residual.equations
    names = list(equations.get_object_names())
    readback: dict[str, bool] = {}
    for name in names:
        equation = equations[name]
        if not allow_early_convergence:
            setattr(equation, "check_convergence", False)
        readback[name] = bool(equation.check_convergence())
    if not allow_early_convergence and any(readback.values()):
        enabled = sorted(name for name, value in readback.items() if value)
        raise RuntimeError(f"Could not disable early convergence checks for: {enabled}")
    print(f"residual_convergence_stop_flags: {json.dumps(readback, sort_keys=True)}")
    return readback


def start_iteration_monitor(solver: Any) -> None:
    monitors = solver.monitors
    if not monitors.is_streaming:
        monitors.start()
    names = list(monitors.get_monitor_set_names())
    if not names:
        raise RuntimeError("Fluent monitor stream has no monitor sets; iteration completion cannot be verified")
    print(f"iteration_monitor_sets: {names}")


def monitor_iteration_snapshot(solver: Any) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for name in solver.monitors.get_monitor_set_names():
        x_values, y_values = solver.monitors.get_monitor_set_data(name)
        numeric_x = [float(value) for value in x_values if math.isfinite(float(value))]
        snapshot[name] = {
            "points": len(numeric_x),
            "first_iteration": min(numeric_x) if numeric_x else None,
            "last_iteration": max(numeric_x) if numeric_x else None,
            "series": sorted(str(series) for series in y_values),
        }
    return snapshot


def monitor_history_rows(solver: Any, monitor_set_name: str = "residual") -> list[dict[str, Any]]:
    names = list(solver.monitors.get_monitor_set_names())
    if monitor_set_name not in names:
        raise RuntimeError(f"Required monitor set '{monitor_set_name}' not found; available={names}")
    x_values, y_values = solver.monitors.get_monitor_set_data(monitor_set_name)
    rows_by_iteration: dict[float, dict[str, Any]] = {}
    for index, x_value in enumerate(x_values):
        iteration = float(x_value)
        row: dict[str, Any] = {"iteration": iteration}
        for series_name, values in y_values.items():
            row[str(series_name)] = float(values[index])
        rows_by_iteration[iteration] = row
    return [rows_by_iteration[iteration] for iteration in sorted(rows_by_iteration)]


def write_monitor_history_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    if not rows:
        raise RuntimeError("Residual monitor history is empty")
    fieldnames = ("iteration",) + tuple(
        sorted({str(key) for row in rows for key in row if str(key) != "iteration"})
    )
    write_local_csv(path, rows, fieldnames)
    return fieldnames


def set_verified_iteration_label(solver: Any, completed: int) -> int:
    solver.scheme.eval(f"(rpsetvar 'number-of-iterations {int(completed)})")
    readback = read_iteration_count(solver)
    if readback != completed:
        raise RuntimeError(f"Could not set verified iteration label: expected {completed}, got {readback}")
    print(f"verified_iteration_label: {readback}")
    return readback


def latest_monitored_iteration(snapshot: Mapping[str, Mapping[str, Any]]) -> float | None:
    values = [
        float(item["last_iteration"])
        for item in snapshot.values()
        if item.get("last_iteration") is not None
    ]
    return max(values) if values else None


def require_monitor_advance(
    solver: Any,
    before: Mapping[str, Mapping[str, Any]],
    requested: int,
    timeout_seconds: float = 20.0,
) -> dict[str, dict[str, Any]]:
    before_iteration = latest_monitored_iteration(before)
    expected = (before_iteration or 0.0) + requested
    deadline = time.monotonic() + timeout_seconds
    after: dict[str, dict[str, Any]] = {}
    while time.monotonic() < deadline:
        after = monitor_iteration_snapshot(solver)
        after_iteration = latest_monitored_iteration(after)
        if after_iteration is not None and after_iteration >= expected:
            return after
        time.sleep(0.5)
    after_iteration = latest_monitored_iteration(after)
    raise RuntimeError(
        "Fluent did not provide evidence for the requested iteration block: "
        f"before={before_iteration}, requested={requested}, expected_at_least={expected}, "
        f"observed={after_iteration}, monitor_snapshot={after}"
    )


def run_single_iteration_command(solver: Any, iterations: int, report_interval: int) -> bool:
    run_calculation = solver.settings.solution.run_calculation
    try_action(
        "set_calculation_reporting_interval",
        lambda: setattr(run_calculation, "reporting_interval", max(1, report_interval)),
    )
    run_calculation.iterate(iter_count=iterations)
    print(f"iterate_{iterations}_single: RPC returned")
    return True


def iterate_case(
    solver: Any,
    iterations: int,
    report_interval: int,
    checkpoint_interval: int,
    remote_output_dir: str,
    prefix: str,
    iteration_mode: str,
    evidence_out: list[dict[str, Any]] | None = None,
) -> int:
    print_header("Run Iterations")
    if iterations <= 0:
        print("iterate: SKIPPED")
        return 0

    remote_chdir(solver, remote_output_dir)
    start_iteration_monitor(solver)
    if iteration_mode == "single":
        if checkpoint_interval > 0:
            print(
                "checkpoint: SKIPPED in single iteration mode; Fluent is kept in one continuous "
                "iterate command for cleaner residual history"
            )
        try:
            before = monitor_iteration_snapshot(solver)
            ok = run_single_iteration_command(solver, iterations, report_interval)
        except KeyboardInterrupt as exc:
            raise RunInterrupted(0) from exc
        if not ok:
            raise RuntimeError(f"Single iteration command failed for {iterations} iterations")
        after = require_monitor_advance(solver, before, iterations)
        if evidence_out is not None:
            evidence_out.append({"requested": iterations, "before": before, "after": after})
        print(f"progress: {iterations}/{iterations}")
        return iterations

    completed = 0
    chunk = max(1, report_interval)
    while completed < iterations:
        step = min(chunk, iterations - completed)
        before = monitor_iteration_snapshot(solver)
        try:
            solver.settings.solution.run_calculation.iterate(iter_count=step)
            print(f"iterate_{completed + step}: RPC returned")
        except KeyboardInterrupt as exc:
            raise RunInterrupted(completed) from exc
        after = require_monitor_advance(solver, before, step)
        if evidence_out is not None:
            evidence_out.append(
                {"block_end": completed + step, "requested": step, "before": before, "after": after}
            )
        completed += step
        print(f"progress: {completed}/{iterations}")
        if checkpoint_interval > 0 and completed < iterations and completed % checkpoint_interval == 0:
            checkpoint_case, checkpoint_data = checkpoint_paths(remote_output_dir, prefix, completed)
            write_case_data_pair(solver, checkpoint_case, checkpoint_data, f"autosave_{completed}")
    return completed


def capture_call(label: str, func: Callable[[], Any], *, required: bool = False) -> str:
    print(f"report_call: {label}")
    buffer = io.StringIO()
    failure: Exception | None = None
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            result = func()
            text_so_far = buffer.getvalue()
            result_text = "" if result is None else str(result)
            if result_text.strip() and result_text.strip() not in text_so_far:
                print(result_text)
        except Exception as exc:
            failure = exc
            category = classify_failure(exc)
            print(f"{label}: FAILED [{category}] -> {type(exc).__name__}: {exc}")
    text = buffer.getvalue()
    print(text[:1000] if text else f"{label}: no captured text")
    if failure is not None and required:
        category = classify_failure(failure)
        raise RuntimeError(f"{label} failed [{category}]: {failure}") from failure
    return f"\n\n===== {label} =====\n{text}"


def enable_per_injection_dpm_summaries(solver: Any) -> str:
    report = solver.settings.results.report.discrete_phase
    parts: list[str] = []
    enable_attempts: tuple[tuple[str, Callable[[], Any]], ...] = (
        (
            "settings_zone_summaries_per_injection_enable",
            lambda: report.zone_summaries_per_injection(summary_state=True),
        ),
        (
            "settings_per_injection_zone_summaries_enable",
            lambda: report.per_injection_zone_summaries(enable=True),
        ),
        (
            "settings_per_injection_zone_summaries_summary_state",
            lambda: report.per_injection_zone_summaries(summary_state=True),
        ),
        (
            "tui_dpm_zone_summaries_per_injection_enable",
            lambda: solver.tui.report.dpm_zone_summaries_per_injection("yes"),
        ),
    )
    enabled = False
    for label, func in enable_attempts:
        text = capture_call(label, func)
        parts.append(text)
        if "FAILED" not in text:
            enabled = True
            break
    if not enabled:
        raise RuntimeError(
            "requires TUI fallback: Fluent rejected every available per-injection zone-summary command"
        )
    parts.append(
        "\n===== settings_zone_summaries_per_injection_reset =====\n"
        "skipped: non-essential reset can block for a long time on remote Fluent sessions\n"
    )
    return "\n".join(parts)


def run_dpm_update(solver: Any) -> str:
    return capture_call(
        "solve_dpm_update",
        lambda: solver.scheme.exec(('(ti-menu-load-string "/solve/dpm-update")',)),
        required=True,
    )


def run_extended_summary(
    solver: Any,
    *,
    label: str,
    write_to_file: bool = False,
    file_name: str | None = None,
    injection_name: str | None = None,
) -> str:
    report = solver.settings.results.report.discrete_phase
    if write_to_file and file_name:
        if not remote_delete_best_effort(solver, file_name):
            raise RuntimeError(
                "requires manual GUI cleanup: could not remove the prior DPM scratch report "
                f"before writing {file_name}"
            )

    def call_settings() -> Any:
        kwargs: dict[str, Any] = {"write_to_file": write_to_file}
        if file_name:
            kwargs["file_name"] = file_name
        if injection_name:
            kwargs["pick_injection"] = True
            kwargs["injection"] = injection_name
        else:
            kwargs["pick_injection"] = False
        return report.extended_summary(**kwargs)

    text = capture_call(label, call_settings)
    if "FAILED" in text:
        tui_args: list[Any] = ["yes" if write_to_file else "no"]
        if write_to_file and file_name:
            tui_args.append(file_name)
        tui_args.append("no")
        tui_args.append("yes" if injection_name else "no")
        if injection_name:
            tui_args.append(injection_name)
        text += capture_call(f"tui_{label}", lambda: solver.tui.report.dpm_extended_summary(*tui_args))

    if write_to_file and file_name:
        file_text = remote_text_read_best_effort(solver, file_name)
        if not file_text:
            raise RuntimeError(
                "requires TUI fallback: per-injection DPM report did not produce a readable "
                f"scratch file for {injection_name or label}"
            )
        text += f"\n\n===== {label}_file_contents =====\n{file_text}"
    return text


def run_dpm_reports(solver: Any, remote_output_dir: str, prefix: str, bins: Sequence[InjectionBin]) -> str:
    print_header("Run DPM Reports")
    parts: list[str] = []
    parts.append(enable_per_injection_dpm_summaries(solver))
    parts.append(run_dpm_update(solver))

    report = solver.settings.results.report.discrete_phase
    parts.append(capture_call("settings_dpm_summary", lambda: report.summary()))
    parts.append(capture_call("tui_dpm_summary", lambda: solver.tui.report.dpm_summary()))
    parts.append(capture_call("tui_particle_summary", lambda: solver.tui.report.particle_summary()))
    parts.append(run_extended_summary(solver, label="settings_dpm_extended_summary"))

    for item in bins:
        scratch_name = f"{prefix}_{item.injection_name}_extended{REMOTE_REPORT_SCRATCH_SUFFIX}"
        scratch_path = remote_join(remote_output_dir, scratch_name)
        parts.append(
            run_extended_summary(
                solver,
                label=f"dpm_extended_summary_{item.injection_name}",
                write_to_file=True,
                file_name=scratch_path,
                injection_name=item.injection_name,
            )
        )
    return "\n".join(parts)


def numeric_or_blank(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"


SECTION_RE = re.compile(r"^===== (?P<label>[^=]+?) =====$", flags=re.MULTILINE)
NUMBER_RE = r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
FATE_TO_PREFIX = {
    "escaped": "escaped",
    "trapped": "trapped",
    "incomplete": "incomplete",
}


def report_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group("label").strip()] = text[start:end]
    return sections


def parse_fate_summary_block(text: str) -> dict[str, float]:
    values: dict[str, float] = {}
    in_mass_table = False
    mass_columns_verified = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "Mass Flow (kg/s)" in stripped:
            in_mass_table = True
            continue
        if in_mass_table and all(label in stripped for label in ("Initial", "Final", "Change")):
            mass_columns_verified = True
            continue
        fate_match = re.match(r"^(Escaped|Trapped|Incomplete)\s+", stripped, flags=re.IGNORECASE)
        if not fate_match:
            continue
        fate = fate_match.group(1).lower()
        prefix = FATE_TO_PREFIX[fate]
        tokens = stripped.split()
        numeric_tokens = [token for token in tokens if re.fullmatch(NUMBER_RE, token)]
        if not in_mass_table:
            if fate == "incomplete" and numeric_tokens:
                values[f"{prefix}_count"] = float(numeric_tokens[0])
            elif len(numeric_tokens) >= 2:
                values[f"{prefix}_count"] = float(numeric_tokens[1])
            continue
        if not mass_columns_verified:
            continue
        if fate == "incomplete" and len(numeric_tokens) >= 3:
            values[f"{prefix}_kgs"] = float(numeric_tokens[-2])
        elif len(numeric_tokens) >= 4:
            values[f"{prefix}_kgs"] = float(numeric_tokens[-2])
    return values


def is_number_token(token: str) -> bool:
    return bool(re.fullmatch(NUMBER_RE, token))


def parse_fate_zone_breakdown(text: str) -> dict[str, list[dict[str, Any]]]:
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    order: list[tuple[str, str, str]] = []
    in_mass_table = False
    mass_columns_verified = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "Mass Flow (kg/s)" in stripped:
            in_mass_table = True
            continue
        if in_mass_table and all(label in stripped for label in ("Initial", "Final", "Change")):
            mass_columns_verified = True
            continue
        fate_match = re.match(r"^(Escaped|Trapped|Incomplete)\s+", stripped, flags=re.IGNORECASE)
        if not fate_match:
            continue

        tokens = stripped.split()
        fate = FATE_TO_PREFIX[fate_match.group(1).lower()]
        zone_name = ""
        zone_id = ""
        value_tokens = tokens[1:]
        if len(tokens) >= 3 and not is_number_token(tokens[1]) and is_number_token(tokens[2]):
            zone_name = tokens[1]
            zone_id = tokens[2]
            value_tokens = tokens[3:]

        key = (fate, zone_name, zone_id)
        if key not in by_key:
            by_key[key] = {
                "fate": fate,
                "zone_name": zone_name,
                "zone_id": zone_id,
            }
            order.append(key)
        entry = by_key[key]
        numeric_values = [float(token) for token in value_tokens if is_number_token(token)]
        if not numeric_values:
            continue
        if in_mass_table and mass_columns_verified:
            entry["mass_flow_kgs"] = numeric_values[1] if len(numeric_values) >= 2 else numeric_values[0]
        elif not in_mass_table:
            entry["count"] = numeric_values[0]

    grouped: dict[str, list[dict[str, Any]]] = {"escaped": [], "trapped": [], "incomplete": []}
    for key in order:
        entry = by_key[key]
        grouped.setdefault(str(entry["fate"]), []).append(entry)
    return grouped


def zone_names(rows: Sequence[Mapping[str, Any]]) -> str:
    names = [str(row.get("zone_name", "")) for row in rows if row.get("zone_name")]
    return ";".join(dict.fromkeys(names))


def zone_ids(rows: Sequence[Mapping[str, Any]]) -> str:
    ids = [str(row.get("zone_id", "")) for row in rows if row.get("zone_id")]
    return ";".join(dict.fromkeys(ids))


def zone_breakdown_json(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return ""
    return json.dumps(list(rows), separators=(",", ":"), default=str)


def injection_report_block(sections: Mapping[str, str], injection_name: str) -> str:
    preferred_labels = (
        f"dpm_extended_summary_{injection_name}_file_contents",
        f"dpm_extended_summary_{injection_name}",
        f"tui_dpm_extended_summary_{injection_name}",
    )
    for label in preferred_labels:
        value = sections.get(label)
        if value and "FAILED" not in value:
            return value

    target = injection_name.lower()
    for label, value in sections.items():
        if target in label.lower() and "extended_summary" in label.lower() and "FAILED" not in value:
            return value
    return ""


def aggregate_report_values(report_text: str) -> dict[str, float]:
    sections = report_sections(report_text)
    merged: dict[str, float] = {}
    for label in ("settings_dpm_extended_summary", "settings_dpm_summary", "tui_dpm_summary"):
        value = sections.get(label)
        if value:
            parsed = parse_fate_summary_block(value)
            if parsed:
                merged.update(parsed)
    if merged:
        return merged
    return parse_fate_summary_block(report_text)


def aggregate_zone_breakdown(report_text: str) -> dict[str, list[dict[str, Any]]]:
    sections = report_sections(report_text)
    merged: dict[str, dict[tuple[str, str], dict[str, Any]]] = {
        "escaped": {},
        "trapped": {},
        "incomplete": {},
    }
    for label in ("settings_dpm_extended_summary", "settings_dpm_summary", "tui_dpm_summary"):
        value = sections.get(label)
        if not value:
            continue
        parsed = parse_fate_zone_breakdown(value)
        for fate, rows in parsed.items():
            for row in rows:
                key = (str(row.get("zone_name", "")), str(row.get("zone_id", "")))
                existing = merged.setdefault(fate, {}).setdefault(
                    key,
                    {
                        "fate": fate,
                        "zone_name": key[0],
                        "zone_id": key[1],
                    },
                )
                existing.update(row)
    if any(merged[fate] for fate in merged):
        return {fate: list(rows.values()) for fate, rows in merged.items()}
    return parse_fate_zone_breakdown(report_text)


def sum_numeric_field(rows: Sequence[Mapping[str, Any]], field: str) -> float | None:
    total = 0.0
    found = False
    for row in rows:
        value = row.get(field)
        if value in (None, ""):
            continue
        total += float(value)
        found = True
    return total if found else None


def parse_dpm_result_rows(
    case: PaperCase,
    bins: Sequence[InjectionBin],
    report_text: str,
    velocity_mode: str,
    *,
    allow_count_fallback: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sections = report_sections(report_text)
    for item in bins:
        block = injection_report_block(sections, item.injection_name)
        parsed = parse_fate_summary_block(block)
        zone_breakdown = parse_fate_zone_breakdown(block)
        has_fate_data = bool(parsed) or any(zone_breakdown.values())
        notes: list[str] = []
        if block and has_fate_data:
            for fate in ("escaped", "trapped", "incomplete"):
                if f"{fate}_kgs" not in parsed and not zone_breakdown.get(fate):
                    parsed[f"{fate}_kgs"] = 0.0
                    parsed[f"{fate}_count"] = 0.0
                    notes.append(f"{fate}_kgs set to 0; no {fate} fate row in per-injection report")
        escaped_mass = parsed.get("escaped_kgs")
        trapped_mass = parsed.get("trapped_kgs")
        incomplete_mass = parsed.get("incomplete_kgs")
        escaped_count = parsed.get("escaped_count")
        trapped_count = parsed.get("trapped_count")
        incomplete_count = parsed.get("incomplete_count")

        escaped_fraction: float | None = None
        if escaped_mass is not None:
            notes.append(f"mass flows parsed from Fluent DPM {DPM_MASS_FLOW_BASIS} column")
        elif allow_count_fallback and escaped_count is not None:
            total_count = (escaped_count or 0) + (trapped_count or 0) + (incomplete_count or 0)
            if total_count > 0:
                escaped_fraction = escaped_count / total_count
                escaped_mass = item.mass_flow_kgs * escaped_fraction
                notes.append(
                    "escaped_kgs estimated from escaped_count / total_count; "
                    "count weighting is not validated as a mass fraction"
                )
        if escaped_mass is not None and item.mass_flow_kgs:
            escaped_fraction = escaped_mass / item.mass_flow_kgs

        if not block:
            notes.append("no per-injection report block parsed")
        elif escaped_mass is None:
            notes.append("escaped_kgs not parsed")

        rows.append(
            {
                "case": case.csv_case,
                "enthalpy_kJkg": case.condition,
                "injection_name": item.injection_name,
                "injection_number": item.injection_number,
                "diameter_m": numeric_or_blank(item.diameter_m),
                "diameter_mm": numeric_or_blank(item.diameter_mm),
                "injected_mass_flow_kgs": numeric_or_blank(item.mass_flow_kgs),
                "velocity_mode": velocity_mode,
                "normal_speed_ms": numeric_or_blank(abs(item.z_velocity_ms)),
                "z_velocity_ms_source": numeric_or_blank(item.z_velocity_ms),
                "escaped_kgs": numeric_or_blank(escaped_mass),
                "trapped_kgs": numeric_or_blank(trapped_mass),
                "incomplete_kgs": numeric_or_blank(incomplete_mass),
                "escaped_zone_names": zone_names(zone_breakdown.get("escaped", [])),
                "trapped_zone_names": zone_names(zone_breakdown.get("trapped", [])),
                "incomplete_zone_names": zone_names(zone_breakdown.get("incomplete", [])),
                "escaped_zone_ids": zone_ids(zone_breakdown.get("escaped", [])),
                "trapped_zone_ids": zone_ids(zone_breakdown.get("trapped", [])),
                "incomplete_zone_ids": zone_ids(zone_breakdown.get("incomplete", [])),
                "escaped_zone_breakdown": zone_breakdown_json(zone_breakdown.get("escaped", [])),
                "trapped_zone_breakdown": zone_breakdown_json(zone_breakdown.get("trapped", [])),
                "incomplete_zone_breakdown": zone_breakdown_json(zone_breakdown.get("incomplete", [])),
                "escaped_count": numeric_or_blank(escaped_count),
                "trapped_count": numeric_or_blank(trapped_count),
                "incomplete_count": numeric_or_blank(incomplete_count),
                "escaped_fraction": numeric_or_blank(escaped_fraction),
                "notes": "; ".join(notes),
            }
        )
    return rows


def parse_case_summary_row(
    case: PaperCase,
    bins: Sequence[InjectionBin],
    report_text: str,
    completed_iterations: int,
    injection_rows: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    parsed = aggregate_report_values(report_text)
    zone_breakdown = aggregate_zone_breakdown(report_text)
    row = {
        "case": case.csv_case,
        "enthalpy_kJkg": case.condition,
        "iterations_completed": completed_iterations,
        "liquid_mass_flow_kgs": numeric_or_blank(case.liquid_mass_flow_kgs),
        "gas_mass_flow_kgs": numeric_or_blank(case.gas_mass_flow_kgs),
        "dpm_injected_mass_flow_kgs": numeric_or_blank(sum(item.mass_flow_kgs for item in bins)),
        "escaped_kgs": numeric_or_blank(parsed.get("escaped_kgs")),
        "trapped_kgs": numeric_or_blank(parsed.get("trapped_kgs")),
        "incomplete_kgs": numeric_or_blank(parsed.get("incomplete_kgs")),
        "escaped_zone_names": zone_names(zone_breakdown.get("escaped", [])),
        "trapped_zone_names": zone_names(zone_breakdown.get("trapped", [])),
        "incomplete_zone_names": zone_names(zone_breakdown.get("incomplete", [])),
        "escaped_zone_breakdown": zone_breakdown_json(zone_breakdown.get("escaped", [])),
        "trapped_zone_breakdown": zone_breakdown_json(zone_breakdown.get("trapped", [])),
        "incomplete_zone_breakdown": zone_breakdown_json(zone_breakdown.get("incomplete", [])),
        "escaped_count": numeric_or_blank(parsed.get("escaped_count")),
        "trapped_count": numeric_or_blank(parsed.get("trapped_count")),
        "incomplete_count": numeric_or_blank(parsed.get("incomplete_count")),
    }
    for field in (
        "escaped_kgs",
        "trapped_kgs",
        "incomplete_kgs",
        "escaped_count",
        "trapped_count",
        "incomplete_count",
    ):
        if not row[field]:
            row[field] = numeric_or_blank(sum_numeric_field(injection_rows, field))
    return row


RESULT_FIELDS = (
    "case",
    "enthalpy_kJkg",
    "injection_name",
    "injection_number",
    "diameter_m",
    "diameter_mm",
    "injected_mass_flow_kgs",
    "velocity_mode",
    "normal_speed_ms",
    "z_velocity_ms_source",
    "escaped_kgs",
    "trapped_kgs",
    "incomplete_kgs",
    "escaped_zone_names",
    "trapped_zone_names",
    "incomplete_zone_names",
    "escaped_zone_ids",
    "trapped_zone_ids",
    "incomplete_zone_ids",
    "escaped_zone_breakdown",
    "trapped_zone_breakdown",
    "incomplete_zone_breakdown",
    "escaped_count",
    "trapped_count",
    "incomplete_count",
    "escaped_fraction",
    "notes",
)

CASE_SUMMARY_FIELDS = (
    "case",
    "enthalpy_kJkg",
    "iterations_completed",
    "liquid_mass_flow_kgs",
    "gas_mass_flow_kgs",
    "dpm_injected_mass_flow_kgs",
    "escaped_kgs",
    "trapped_kgs",
    "incomplete_kgs",
    "escaped_zone_names",
    "trapped_zone_names",
    "incomplete_zone_names",
    "escaped_zone_breakdown",
    "trapped_zone_breakdown",
    "incomplete_zone_breakdown",
    "escaped_count",
    "trapped_count",
    "incomplete_count",
)


def output_paths(remote_output_dir: str, prefix: str, iterations: int) -> dict[str, str]:
    run_suffix = "1500" if iterations == 1500 else f"{iterations}iter"
    return {
        "flow_case": remote_join(remote_output_dir, f"{prefix}_{run_suffix}_flow.cas.h5"),
        "flow_data": remote_join(remote_output_dir, f"{prefix}_{run_suffix}_flow.dat.h5"),
        "case": remote_join(remote_output_dir, f"{prefix}_{run_suffix}.cas.h5"),
        "data": remote_join(remote_output_dir, f"{prefix}_{run_suffix}.dat.h5"),
        "dpm_report": remote_join(remote_output_dir, f"{prefix}_dpm_report.txt"),
        "injection_results": remote_join(remote_output_dir, f"{prefix}_injection_results.csv"),
        "case_summary": remote_join(remote_output_dir, f"{prefix}_case_summary.csv"),
        "residual_history": remote_join(remote_output_dir, f"{prefix}_{run_suffix}_residual_history.csv"),
        "manifest": remote_join(remote_output_dir, f"{prefix}_manifest.json"),
        "flow_manifest": remote_join(remote_output_dir, f"{prefix}_flow_manifest.json"),
    }


def dpm_mass_balance_audit(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    audit_rows: list[dict[str, Any]] = []
    failed: list[str] = []
    for row in rows:
        name = str(row["injection_name"])
        injected = float(row["injected_mass_flow_kgs"])
        fate_values: list[float] = []
        missing: list[str] = []
        for field in ("escaped_kgs", "trapped_kgs", "incomplete_kgs"):
            value = row.get(field)
            if value in (None, ""):
                missing.append(field)
            else:
                fate_values.append(float(value))
        fate_total = sum(fate_values)
        error = fate_total - injected
        tolerance = max(1e-5, injected * 0.002)
        passed = not missing and abs(error) <= tolerance
        if not passed:
            failed.append(name)
        audit_rows.append(
            {
                "injection_name": name,
                "injected_kgs": injected,
                "fate_total_kgs": fate_total,
                "error_kgs": error,
                "tolerance_kgs": tolerance,
                "missing_fields": missing,
                "passed": passed,
            }
        )
    return {"passed": not failed, "failed_injections": failed, "rows": audit_rows}


def run_one_case(
    solver: Any,
    item: Mapping[str, Any],
    args: argparse.Namespace,
    local_output_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    case: PaperCase = item["case"]
    bins: Sequence[InjectionBin] = item["bins"]
    prefix = case_prefix(case)
    paths = output_paths(args.remote_output_dir, prefix, args.iterations)

    load_base_case(solver, args.base_case)
    autosave_state = disable_inherited_fluent_autosave(solver, args.remote_output_dir, prefix)
    require_current_case_shape(solver)
    physics_readback = require_case_physics(
        solver,
        gas_phase_material=args.gas_phase_material,
        liquid_phase_material=args.liquid_phase_material,
        allow_coupled_dpm=args.allow_coupled_dpm,
    )
    inlet_readback = set_inlet_phase_mass_flows(solver, case)
    injection_readbacks = set_dpm_injections(solver, bins, args.dpm_velocity_mode)
    maybe_initialize(solver, args.initialize)
    configure_residual_history(solver, args.residual_history_points)
    convergence_stop_flags = configure_full_iteration_run(solver, args.allow_early_convergence)

    completed = 0
    iteration_evidence: list[dict[str, Any]] = []
    try:
        completed = iterate_case(
            solver,
            args.iterations,
            args.report_interval,
            args.checkpoint_interval,
            args.remote_output_dir,
            prefix,
            args.iteration_mode,
            evidence_out=iteration_evidence,
        )
    except RunInterrupted:
        interrupt_case = remote_join(args.remote_output_dir, f"{prefix}_interrupt.cas.h5")
        interrupt_data = remote_join(args.remote_output_dir, f"{prefix}_interrupt.dat.h5")
        write_case_data_pair(solver, interrupt_case, interrupt_data, "interrupt")
        raise

    residual_rows = monitor_history_rows(solver)
    residual_iterations = [float(row["iteration"]) for row in residual_rows]
    if not residual_iterations or max(residual_iterations) < completed:
        raise RuntimeError(
            f"Residual history does not contain verified iteration {completed}: "
            f"last={max(residual_iterations) if residual_iterations else None}"
        )
    residual_fieldnames = write_monitor_history_csv(
        local_output_dir / f"{prefix}_{args.iterations}iter_residual_history.csv",
        residual_rows,
    )
    remote_text_write_best_effort(
        solver,
        paths["residual_history"],
        rows_to_csv_text(residual_rows, residual_fieldnames),
    )
    verified_iteration_label = set_verified_iteration_label(solver, completed)
    write_case_data_pair(solver, paths["flow_case"], paths["flow_data"], "verified_flow")
    flow_manifest = {
        "case": case.csv_case,
        "condition": case.condition,
        "iterations_requested": args.iterations,
        "iterations_verified": completed,
        "verification_source": "PyFluent residual monitor x-axis advancement",
        "iteration_evidence": iteration_evidence,
        "verified_iteration_label": verified_iteration_label,
        "residual_history_rows": len(residual_rows),
        "residual_history": paths["residual_history"],
        "flow_case": paths["flow_case"],
        "flow_data": paths["flow_data"],
        "inlet_readback": inlet_readback,
        "physics_readback": physics_readback,
        "injection_readbacks": injection_readbacks,
        "residual_convergence_stop_flags": convergence_stop_flags,
        "fluent_internal_autosave": autosave_state,
    }
    flow_manifest_text = json.dumps(flow_manifest, indent=2, default=str)
    write_local_text(local_output_dir / f"{prefix}_flow_manifest.json", flow_manifest_text)
    remote_text_write_best_effort(solver, paths["flow_manifest"], flow_manifest_text)

    report_text = ""
    result_rows: list[dict[str, Any]]
    if args.no_dpm_report:
        result_rows = parse_dpm_result_rows(
            case,
            bins,
            "",
            args.dpm_velocity_mode,
            allow_count_fallback=args.allow_count_based_escaped_fallback,
        )
    else:
        report_text = run_dpm_reports(solver, args.remote_output_dir, prefix, bins)
        local_report = local_output_dir / f"{prefix}_dpm_report.txt"
        write_local_text(local_report, report_text)
        remote_text_write_best_effort(solver, paths["dpm_report"], report_text)
        result_rows = parse_dpm_result_rows(
            case,
            bins,
            report_text,
            args.dpm_velocity_mode,
            allow_count_fallback=args.allow_count_based_escaped_fallback,
        )
    dpm_mass_balance = dpm_mass_balance_audit(result_rows) if not args.no_dpm_report else None
    case_summary_row = parse_case_summary_row(case, bins, report_text, completed, result_rows)

    if not args.allow_missing_escaped and not args.no_dpm_report:
        missing = [row["injection_name"] for row in result_rows if not row["escaped_kgs"]]
        if missing:
            print(f"escaped_kgs missing for {missing}; raw DPM report will still be saved")

    local_case_csv = local_output_dir / f"{prefix}_injection_results.csv"
    write_local_csv(local_case_csv, result_rows, RESULT_FIELDS)
    remote_text_write_best_effort(solver, paths["injection_results"], rows_to_csv_text(result_rows, RESULT_FIELDS))
    local_case_summary_csv = local_output_dir / f"{prefix}_case_summary.csv"
    write_local_csv(local_case_summary_csv, [case_summary_row], CASE_SUMMARY_FIELDS)
    remote_text_write_best_effort(solver, paths["case_summary"], rows_to_csv_text([case_summary_row], CASE_SUMMARY_FIELDS))

    post_dpm_injection_readbacks = (
        read_dpm_injections(solver, bins, args.dpm_velocity_mode)
        if not args.no_dpm_report
        else injection_readbacks
    )
    write_case_data_pair(solver, paths["case"], paths["data"], "final_post_dpm")

    manifest = {
        "case": case.csv_case,
        "condition": case.condition,
        "base_case": args.base_case,
        "remote_output_paths": paths,
        "iterations_requested": args.iterations,
        "iterations_completed": completed,
        "iterations_verified": completed,
        "iteration_verification_source": "PyFluent residual monitor x-axis advancement",
        "iteration_evidence": iteration_evidence,
        "verified_iteration_label": verified_iteration_label,
        "residual_history_rows": len(residual_rows),
        "iteration_mode": args.iteration_mode,
        "residual_history_points": args.residual_history_points,
        "residual_convergence_stop_flags": convergence_stop_flags,
        "fluent_internal_autosave": autosave_state,
        "liquid_mass_flow_kgs": case.liquid_mass_flow_kgs,
        "gas_mass_flow_kgs": case.gas_mass_flow_kgs,
        "dpm_total_mass_flow_kgs": sum(bin_item.mass_flow_kgs for bin_item in bins),
        "dpm_velocity_mode": args.dpm_velocity_mode,
        "allow_count_based_escaped_fallback": args.allow_count_based_escaped_fallback,
        "dpm_report_mass_flow_basis": DPM_MASS_FLOW_BASIS,
        "dpm_velocity_definition": (
            "Fluent face-normal direction with magnitude=abs(z_velocity_ms)"
            if args.dpm_velocity_mode == "face-normal"
            else "Explicit components x=0, y=0, z=z_velocity_ms"
        ),
        "inlet_readback": inlet_readback,
        "physics_readback": physics_readback,
        "injection_readback_names": sorted(injection_readbacks),
        "injection_readbacks": injection_readbacks,
        "post_dpm_injection_readbacks": post_dpm_injection_readbacks,
        "escaped_kgs_missing_count": sum(1 for row in result_rows if not row["escaped_kgs"]),
        "dpm_mass_balance": dpm_mass_balance,
        "case_summary": case_summary_row,
    }
    manifest_text = json.dumps(manifest, indent=2, default=str)
    write_local_text(local_output_dir / f"{prefix}_manifest.json", manifest_text)
    remote_text_write_best_effort(solver, paths["manifest"], manifest_text)

    if not args.allow_missing_escaped and not args.no_dpm_report:
        missing = [row["injection_name"] for row in result_rows if not row["escaped_kgs"]]
        if missing:
            raise RuntimeError(
                f"escaped_kgs was not parsed for {case.csv_case} / {case.condition}: {missing}. "
                "Case/data and raw DPM reports were saved; rerun with --allow-missing-escaped "
                "only if raw report parsing will be handled manually."
            )
    if dpm_mass_balance is not None and not dpm_mass_balance["passed"]:
        raise RuntimeError(
            "DPM fate mass does not reconcile with injected mass for: "
            f"{dpm_mass_balance['failed_injections']}. Raw reports and case/data were saved."
        )
    return result_rows, case_summary_row


def main() -> int:
    global INLET_NAME, OUTLET_NAME, PARTICLE_MATERIAL, INJECTION_SURFACE, INJECTION_NAMES

    args = build_parser().parse_args()
    load_dotenv()
    INLET_NAME = args.inlet_name.strip()
    OUTLET_NAME = args.outlet_name.strip()
    PARTICLE_MATERIAL = args.particle_material.strip()
    INJECTION_SURFACE = args.injection_surface.strip()
    INJECTION_NAMES = tuple(
        name.strip() for name in args.injection_names.split(",") if name.strip()
    )
    if len(INJECTION_NAMES) != INJECTION_COUNT:
        raise ValueError(
            f"--injection-names must contain exactly {INJECTION_COUNT} names; "
            f"received {len(INJECTION_NAMES)}"
        )
    if len(set(INJECTION_NAMES)) != INJECTION_COUNT:
        raise ValueError("--injection-names entries must be unique")

    csv_path = Path(args.harwell_csv).expanduser().resolve()
    groups = read_harwell_bins(csv_path)
    cases = selected_cases(args.case_filter)
    plan = build_sweep_plan(cases, groups)

    if args.dry_run:
        print_dry_run(plan)
        return 0

    local_output_dir = ensure_local_output_dir(args.local_output_dir)
    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    require_remote_input(solver, args.base_case, "base case")
    if not ensure_remote_directory_best_effort(solver, args.remote_output_dir):
        raise RuntimeError(f"Could not create or verify remote output directory: {args.remote_output_dir}")

    all_rows: list[dict[str, Any]] = []
    for seed_path in args.seed_results_csv:
        all_rows.extend(read_seed_csv(seed_path, RESULT_FIELDS, "seed_results_csv"))
    case_summary_rows: list[dict[str, Any]] = []
    for seed_path in args.seed_case_summary_csv:
        case_summary_rows.extend(
            read_seed_csv(seed_path, CASE_SUMMARY_FIELDS, "seed_case_summary_csv")
        )
    for item in plan:
        case: PaperCase = item["case"]
        print_header(f"Run {case.csv_case} / {case.condition}")
        rows, case_summary_row = run_one_case(solver, item, args, local_output_dir)
        all_rows.extend(rows)
        case_summary_rows.append(case_summary_row)

        # Persist combined outputs after every case so a later disconnect does not lose prior cases.
        local_combined = local_output_dir / "all_enthalpy_injection_results.csv"
        write_local_csv(local_combined, all_rows, RESULT_FIELDS)
        remote_combined = remote_join(args.remote_output_dir, "all_enthalpy_injection_results.csv")
        remote_text_write_best_effort(solver, remote_combined, rows_to_csv_text(all_rows, RESULT_FIELDS))
        local_case_summary = local_output_dir / "all_enthalpy_case_summary.csv"
        write_local_csv(local_case_summary, case_summary_rows, CASE_SUMMARY_FIELDS)
        remote_case_summary = remote_join(args.remote_output_dir, "all_enthalpy_case_summary.csv")
        remote_text_write_best_effort(
            solver,
            remote_case_summary,
            rows_to_csv_text(case_summary_rows, CASE_SUMMARY_FIELDS),
        )

    local_combined = local_output_dir / "all_enthalpy_injection_results.csv"
    write_local_csv(local_combined, all_rows, RESULT_FIELDS)
    remote_combined = remote_join(args.remote_output_dir, "all_enthalpy_injection_results.csv")
    remote_text_write_best_effort(solver, remote_combined, rows_to_csv_text(all_rows, RESULT_FIELDS))
    local_case_summary = local_output_dir / "all_enthalpy_case_summary.csv"
    write_local_csv(local_case_summary, case_summary_rows, CASE_SUMMARY_FIELDS)
    remote_case_summary = remote_join(args.remote_output_dir, "all_enthalpy_case_summary.csv")
    remote_text_write_best_effort(
        solver,
        remote_case_summary,
        rows_to_csv_text(case_summary_rows, CASE_SUMMARY_FIELDS),
    )

    print_header("Sweep Complete")
    print(f"local_combined_results: {local_combined}")
    print(f"remote_combined_results: {remote_combined}")
    print(f"local_case_summary: {local_case_summary}")
    print(f"remote_case_summary: {remote_case_summary}")
    print(f"rows: {len(all_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
