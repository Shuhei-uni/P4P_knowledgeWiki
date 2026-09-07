#!/usr/bin/env python3
"""Deploy, compile and safely hook setup 07b's liquid-sink UDF in Fluent 2024 R2.

The default mode is read-only.  ``--apply`` saves a new pre-hook case/data pair,
uses a content-addressed UDF source/library name, hooks the source terms with the
sink ramp fixed at zero, reads everything back, and saves a separate hooked
case/data pair.  No long calculation and no DPM tracking are performed.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import io
import json
import re
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.constant_water_level_sink import (  # noqa: E402
    find_phase_for_material,
    parse_zone_table,
    validate_sink_parameters,
)
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_constant_water_level_sink_20260807"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_PREFLIGHT_SCRATCH = (
    r"C:\Users\qtra338\Documents\Mesh study\split_inlet_mesh_convergence_20260801\mesh_900k"
)
LOCAL_UDF = PROJECT_ROOT / "udf" / "constant_water_level_sink.c"
EXPECTED_900K_CELLS = 5_335_623
LIQUID_MATERIAL = "water-liquid-at-psep"
UDF_FUNCTIONS = {
    "adjust": "cwl_update_sink_mask",
    "mass": "cwl_liquid_mass_sink",
    "x-momentum": "cwl_x_momentum_sink",
    "y-momentum": "cwl_y_momentum_sink",
    "z-momentum": "cwl_z_momentum_sink",
}
DEPLOY_REVISION = 4
REQUIRED_UDM = 5


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--remote-root", default=REMOTE_ROOT)
    parser.add_argument("--run-label", default="mesh-900k_07b_sink_hook_v1")
    parser.add_argument("--expected-cells", type=int, default=EXPECTED_900K_CELLS)
    parser.add_argument("--tau-s", type=float, default=0.10)
    parser.add_argument("--ramp", type=float, default=0.0)
    parser.add_argument("--alpha-min", type=float, default=1.0e-12)
    parser.add_argument(
        "--reuse-prehook-case",
        default="",
        help="Existing protected pre-hook case to reuse instead of writing another copy.",
    )
    parser.add_argument(
        "--reuse-prehook-data",
        default="",
        help="Existing protected pre-hook data paired with --reuse-prehook-case.",
    )
    parser.add_argument(
        "--smoke-iterations",
        type=int,
        default=0,
        help="Optional tiny diagnostic only; zero keeps the hooked case unadvanced.",
    )
    parser.add_argument("--smoke-ramp", type=float, default=0.05)
    return parser


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def capture_console(call) -> tuple[Any, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = call()
        time.sleep(1.0)
    return result, buffer.getvalue()


def list_zones(solver: Any) -> tuple[str, dict[str, dict[str, Any]]]:
    _, text = capture_console(lambda: solver.tui.mesh.modify_zones.list_zones())
    return text, parse_zone_table(text)


def phase_material_map(solver: Any) -> dict[str, str]:
    state = solver.settings.setup.models.species.get_state()
    materials = state.get("model", {}).get("phase_material", {})
    if not isinstance(materials, Mapping):
        raise RuntimeError("path/version issue: phase material mapping is unavailable")
    return {str(phase): str(material) for phase, material in materials.items()}


def inspect_live_baseline(solver: Any, args: argparse.Namespace) -> dict[str, Any]:
    zone_text, zones = list_zones(solver)
    required_types = {
        "bottom": "wall",
        "wall-fluid": "wall",
        "liquidinlet": "mass-flow-inlet",
        "steaminlet": "mass-flow-inlet",
        "steamoutlet": "pressure-outlet",
        "fluid": "fluid",
    }
    errors = [
        f"zone {name!r} expected type={kind!r}; actual={zones.get(name)}"
        for name, kind in required_types.items()
        if zones.get(name, {}).get("type") != kind
    ]
    materials = phase_material_map(solver)
    liquid_phase = find_phase_for_material(materials, LIQUID_MATERIAL)
    phase_names = sorted(materials)
    liquid_phase_index = phase_names.index(liquid_phase)
    mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
    if int(mesh_metrics.get("cells", -1)) != args.expected_cells:
        errors.append(
            f"expected the 900k qualification mesh with {args.expected_cells} cells; "
            f"actual={mesh_metrics.get('cells')}"
        )
    settings = mesh_study.capture_settings(solver, REMOTE_PREFLIGHT_SCRATCH)
    settings.update(
        mesh_study.verify_initialized_phase_identity(solver, REMOTE_PREFLIGHT_SCRATCH)
    )
    errors.extend(mesh_study.validate_settings(settings, mesh_metrics, require_phase_identity=True))
    parameter_errors = validate_sink_parameters(
        bottom_zone_id=int(zones.get("bottom", {}).get("id", -1)),
        liquid_phase_index=liquid_phase_index,
        tau_s=args.tau_s,
        ramp=args.ramp,
        alpha_min=args.alpha_min,
    )
    errors.extend(parameter_errors)
    return {
        "status": "accepted" if not errors else "unresolved",
        "fluent_version": str(solver.get_fluent_version()),
        "health": str(solver.health_check.status()),
        "zone_table_transcript": zone_text,
        "zones": zones,
        "bottom_zone_id": zones.get("bottom", {}).get("id"),
        "phase_materials": materials,
        "liquid_phase": liquid_phase,
        "liquid_phase_index_zero_based": liquid_phase_index,
        "mesh_metrics": mesh_metrics,
        "mesh_quality_transcript": quality_text,
        "settings_readback": settings,
        "validation_errors": errors,
        "dpm_required_state": "off",
    }


def ensure_remote_root(solver: Any, remote_root: str) -> None:
    if not sweep.ensure_remote_directory_best_effort(solver, remote_root):
        raise RuntimeError(f"requires manual GUI cleanup: cannot create {remote_root}")


def deploy_source(solver: Any, remote_root: str) -> dict[str, str]:
    source_bytes = LOCAL_UDF.read_bytes()
    sha = hashlib.sha256(source_bytes).hexdigest()
    source_name = f"constant_water_level_sink_{sha[:12]}.c"
    remote_source = remote_join(remote_root, source_name)
    encoded_path = remote_source + ".b64"
    encoded = base64.b64encode(source_bytes).decode("ascii")
    if not sweep.remote_text_write_best_effort(solver, encoded_path, encoded):
        raise RuntimeError(f"requires TUI fallback: could not deploy {encoded_path}")
    powershell = (
        "powershell -NoProfile -Command \""
        f"$b=[Convert]::FromBase64String((Get-Content -Raw '{encoded_path}'));"
        f"[IO.File]::WriteAllBytes('{remote_source}',$b)\""
    )
    solver.scheme.eval(f'(system "{sweep.quote_scheme_string(powershell)}")')
    sweep.remote_delete_best_effort(solver, encoded_path)
    if not remote_file_exists(solver, remote_source):
        raise RuntimeError(f"missing file: deployed UDF source is not visible: {remote_source}")
    remote_sha = mesh_study.remote_file_sha256(
        solver,
        remote_source,
        remote_join(remote_root, f"_{source_name}_sha256.txt"),
    )
    if remote_sha != sha:
        raise RuntimeError(
            f"readback mismatch: local UDF sha256={sha} remote sha256={remote_sha}"
        )
    return {
        "local_source": str(LOCAL_UDF),
        "source_sha256": sha,
        "remote_source": remote_source,
        "remote_source_name": source_name,
        "remote_source_sha256": remote_sha,
        "library_name": f"lib07b_cwl_{sha[:10]}_r{DEPLOY_REVISION}",
    }


def compile_and_load(solver: Any, deployment: Mapping[str, str], remote_root: str) -> str:
    remote_chdir(solver, remote_root)
    library = deployment["library_name"]
    source_name = deployment["remote_source_name"]
    chunks: list[str] = []
    for label, call in (
        ("built_in_compiler", lambda: solver.tui.define.user_defined.use_built_in_compiler("yes")),
        (
            "compile",
            lambda: solver.tui.define.user_defined.compiled_functions(
                "compile", library, "yes", source_name, "", ""
            ),
        ),
        ("load", lambda: solver.tui.define.user_defined.compiled_functions("load", library)),
    ):
        _, text = capture_console(call)
        chunks.append(f"\n--- {label} ---\n{text}")
        lowered = text.lower()
        failed = bool(
            re.search(r"(?:^|\n)\s*(?:error:|.*fatal error:|scons:\s*\*\*\*)", text, re.I)
        )
        if failed:
            raise RuntimeError(f"invalid value/format issue: UDF {label} failed\n{text}")
        if label == "load":
            if "cwl07b error" in lowered:
                raise RuntimeError(f"order/dependency issue: UDF autorun failed\n{text}")
            if not re.search(
                rf"CWL07B:\s+reserved\s+{REQUIRED_UDM}\s+UDMs\s+at\s+offset\s+\d+",
                text,
                re.I,
            ):
                raise RuntimeError(
                    "readback mismatch: load transcript did not prove UDM reservation\n"
                    + text
                )
    return "".join(chunks)


def allocate_and_verify_udm(solver: Any) -> dict[str, Any]:
    _, transcript = capture_console(
        lambda: solver.tui.define.user_defined.user_defined_memory(REQUIRED_UDM)
    )
    allowed = [str(name) for name in solver.fields.field_data.scalar_fields.allowed_values()]
    user_memory = [
        name
        for name in allowed
        if re.search(r"(?:user[-_ ]?memory|udm)", name, re.I)
    ]
    if len(user_memory) < REQUIRED_UDM:
        raise RuntimeError(
            f"readback mismatch: expected at least {REQUIRED_UDM} UDM fields; "
            f"found={user_memory}"
        )
    return {
        "requested_locations": REQUIRED_UDM,
        "field_readback": user_memory,
        "transcript": transcript,
    }


def rp_literal(value: Any, kind: str) -> str:
    if kind == "integer":
        return str(int(value))
    return format(float(value), ".17g")


def define_or_set_rp_var(solver: Any, name: str, value: Any, kind: str) -> None:
    literal = rp_literal(value, kind)
    try:
        solver.scheme.eval(f"(rpsetvar '{name} {literal})")
    except Exception:
        solver.scheme.eval(f"(rp-var-define '{name} {literal} '{kind} #f)")
        solver.scheme.eval(f"(rpsetvar '{name} {literal})")
    actual = solver.scheme.eval(f"(rpgetvar '{name})")
    if kind == "integer" and int(actual) != int(value):
        raise RuntimeError(f"readback mismatch for {name}: expected={value} actual={actual}")
    if kind == "real" and abs(float(actual) - float(value)) > 1.0e-14:
        raise RuntimeError(f"readback mismatch for {name}: expected={value} actual={actual}")


def configure_rp_parameters(solver: Any, preflight: Mapping[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    values = {
        "user/cwl07b/bottom-zone-id": (preflight["bottom_zone_id"], "integer"),
        "user/cwl07b/liquid-phase-index": (
            preflight["liquid_phase_index_zero_based"],
            "integer",
        ),
        "user/cwl07b/tau-s": (args.tau_s, "real"),
        "user/cwl07b/ramp": (args.ramp, "real"),
        "user/cwl07b/alpha-min": (args.alpha_min, "real"),
    }
    for name, (value, kind) in values.items():
        define_or_set_rp_var(solver, name, value, kind)
    return {name: solver.scheme.eval(f"(rpgetvar '{name})") for name in values}


def choose_name(candidates: Iterable[str], aliases: Iterable[str], label: str) -> str:
    values = [str(value) for value in candidates]
    normalized = {re.sub(r"[^a-z0-9]+", "", value.lower()): value for value in values}
    matches = {
        normalized[re.sub(r"[^a-z0-9]+", "", alias.lower())]
        for alias in aliases
        if re.sub(r"[^a-z0-9]+", "", alias.lower()) in normalized
    }
    if len(matches) != 1:
        raise RuntimeError(f"path/version issue: cannot resolve {label}; candidates={values}")
    return matches.pop()


def choose_udf(allowed: Iterable[str], base_name: str, library: str) -> str:
    values = [str(value) for value in allowed]
    matches = [
        value
        for value in values
        if base_name.lower() in value.lower() and library.lower() in value.lower()
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"path/version issue: expected one loaded UDF for {base_name}; allowed={values}"
        )
    return matches[0]


def hook_source_entry(term_getter, function_base: str, library: str) -> dict[str, Any]:
    term_list = term_getter()
    term_list.resize(1)
    # Resizing a Fluent ListObject invalidates both it and every child handle.
    term_list = term_getter()
    # In Fluent 2024 R2, an entry whose option is ``none`` is itself inactive;
    # child-by-child option/UDF setters therefore cannot be used.  Atomically
    # assigning the list is the active generated-API path, verified by the
    # protected-copy source activation probe.
    function_name = f"{function_base}::{library}"
    term_list.set_state([{"option": "udf", "udf": function_name}])
    readback = term_getter().get_state()
    if not isinstance(readback, list) or len(readback) != 1:
        raise RuntimeError(f"readback mismatch: source list has unexpected state {readback}")
    if str(readback[0].get("udf")) != function_name or str(
        readback[0].get("option")
    ).lower() != "udf":
        raise RuntimeError(
            f"readback mismatch: expected source UDF {function_name!r}; actual={readback}"
        )
    return {"function": function_name, "readback": readback}


def enable_and_hook_sources(
    solver: Any, preflight: Mapping[str, Any], library: str
) -> dict[str, Any]:
    cell_zone = solver.settings.setup.cell_zone_conditions.fluid["fluid"]
    liquid_phase = str(preflight["liquid_phase"])

    liquid_sources = cell_zone.phase[liquid_phase].sources
    liquid_sources.enable.set_state(True)
    liquid_sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
        liquid_phase
    ].sources
    liquid_terms = [str(name) for name in liquid_sources.terms.get_object_names()]
    mass_name = choose_name(liquid_terms, ("mass", "continuity"), "liquid mass source term")
    mass_hook = hook_source_entry(
        lambda: solver.settings.setup.cell_zone_conditions.fluid["fluid"]
        .phase[liquid_phase]
        .sources.terms[mass_name],
        UDF_FUNCTIONS["mass"],
        library,
    )

    mixture_sources = cell_zone.phase["mixture"].sources
    mixture_sources.enable.set_state(True)
    mixture_sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
        "mixture"
    ].sources
    mixture_terms = [str(name) for name in mixture_sources.terms.get_object_names()]
    result: dict[str, Any] = {
        "liquid_phase": liquid_phase,
        "liquid_mass_term": mass_name,
        "liquid_mass_hook": mass_hook,
        "mixture_term_candidates": mixture_terms,
    }
    aliases = {
        "x-momentum": ("x-momentum", "x momentum", "x-velocity"),
        "y-momentum": ("y-momentum", "y momentum", "y-velocity"),
        "z-momentum": ("z-momentum", "z momentum", "z-velocity"),
    }
    for role, role_aliases in aliases.items():
        term_name = choose_name(mixture_terms, role_aliases, role)
        result[role] = {
            "term": term_name,
            **hook_source_entry(
                lambda term_name=term_name: solver.settings.setup.cell_zone_conditions.fluid[
                    "fluid"
                ].phase["mixture"].sources.terms[term_name],
                UDF_FUNCTIONS[role],
                library,
            ),
        }
    result["complete_source_readback"] = safe_get_state(
        solver.settings.setup.cell_zone_conditions.fluid["fluid"],
        "setup07b_fluid_cell_zone",
    )
    return result


def hook_adjust(solver: Any, library: str) -> dict[str, str]:
    function = f"{UDF_FUNCTIONS['adjust']}::{library}"
    command = f'/define/user-defined/function-hooks/adjust "{function}" ""'
    expression = f'(ti-menu-load-string "{command.replace(chr(34), chr(92) + chr(34))}")'
    _, text = capture_console(lambda: solver.scheme.exec((expression,)))
    if any(token in text.lower() for token in ("unknown", "error:")):
        raise RuntimeError(f"requires TUI fallback: Adjust hook failed\n{text}")
    return {"function": function, "command": command, "transcript": text}


def save_pair(solver: Any, remote_root: str, label: str) -> dict[str, str]:
    case_file = remote_join(remote_root, f"{label}.cas.h5")
    data_file = remote_join(remote_root, f"{label}.dat.h5")
    sweep.write_case_data_pair(solver, case_file, data_file, label)
    return {"case": case_file, "data": data_file}


def restore_pair(solver: Any, pair: Mapping[str, str]) -> None:
    solver.settings.file.read_case(file_name=pair["case"])
    solver.settings.file.read_data(file_name=pair["data"])


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = LOCAL_ROOT / f"{args.run_label}_manifest.json"
    solver = connect(server_id=args.server_id)
    preflight = inspect_live_baseline(solver, args)
    write_json(LOCAL_ROOT / f"{args.run_label}_preflight.json", preflight)
    if preflight["validation_errors"]:
        raise RuntimeError("preflight failed: " + "; ".join(preflight["validation_errors"]))
    if args.preflight_only:
        print(json.dumps(preflight, indent=2, default=str))
        print("setup07b: PREFLIGHT ACCEPTED; no Fluent settings or iterations changed")
        return 0

    manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": args.run_label,
        "status": "running",
        "classification": "diagnostic",
        "started_epoch": time.time(),
        "preflight": preflight,
        "sink_parameters": {
            "tau_s": args.tau_s,
            "ramp": args.ramp,
            "alpha_min": args.alpha_min,
            "smoke_iterations": args.smoke_iterations,
            "smoke_ramp": args.smoke_ramp,
        },
        "dpm": "off; no injection update or tracking permitted",
    }
    write_json(manifest_path, manifest)
    ensure_remote_root(solver, args.remote_root)
    transcript = remote_join(args.remote_root, f"{args.run_label}_transcript.trn")
    prehook_pair: dict[str, str] | None = None
    try:
        solver.settings.file.start_transcript(file_name=transcript)
        if bool(args.reuse_prehook_case) != bool(args.reuse_prehook_data):
            raise ValueError(
                "--reuse-prehook-case and --reuse-prehook-data must be supplied together"
            )
        if args.reuse_prehook_case:
            for path in (args.reuse_prehook_case, args.reuse_prehook_data):
                if not remote_file_exists(solver, path):
                    raise FileNotFoundError(f"reused pre-hook checkpoint is missing: {path}")
            prehook_pair = {
                "case": args.reuse_prehook_case,
                "data": args.reuse_prehook_data,
            }
            manifest["prehook_checkpoint_mode"] = "reused existing protected pair"
            # The live session may contain a failed hook from an earlier attempt.
            # Reload the protected pair before allocating UDM or loading a new library.
            restore_pair(solver, prehook_pair)
        else:
            prehook_pair = save_pair(solver, args.remote_root, f"{args.run_label}_prehook")
            manifest["prehook_checkpoint_mode"] = "new protected pair"
        manifest["prehook_checkpoint"] = prehook_pair
        manifest["udm_allocation"] = allocate_and_verify_udm(solver)
        deployment = deploy_source(solver, args.remote_root)
        manifest["udf_deployment"] = deployment
        manifest["compile_transcript"] = compile_and_load(solver, deployment, args.remote_root)
        manifest["rp_parameter_readback"] = configure_rp_parameters(solver, preflight, args)
        manifest["adjust_hook"] = hook_adjust(solver, deployment["library_name"])
        manifest["source_hooks"] = enable_and_hook_sources(
            solver, preflight, deployment["library_name"]
        )

        posthook_state = inspect_live_baseline(solver, args)
        posthook_errors = posthook_state["validation_errors"]
        if posthook_errors:
            raise RuntimeError("post-hook baseline parity failed: " + "; ".join(posthook_errors))
        manifest["posthook_readback"] = posthook_state
        manifest["hooked_checkpoint"] = save_pair(
            solver, args.remote_root, f"{args.run_label}_hooked_ramp0"
        )

        if args.smoke_iterations:
            if args.smoke_iterations < 0 or args.smoke_iterations > 5:
                raise ValueError("--smoke-iterations must lie between 0 and 5")
            if not 0.0 < args.smoke_ramp <= 0.1:
                raise ValueError("--smoke-ramp must lie in (0, 0.1]")
            define_or_set_rp_var(solver, "user/cwl07b/ramp", args.smoke_ramp, "real")
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=args.smoke_iterations)
            after = sweep.monitor_iteration_snapshot(solver)
            define_or_set_rp_var(solver, "user/cwl07b/ramp", 0.0, "real")
            manifest["smoke_test"] = {
                "iterations": args.smoke_iterations,
                "ramp_during_smoke": args.smoke_ramp,
                "ramp_after_smoke": solver.scheme.eval("(rpgetvar 'user/cwl07b/ramp)"),
                "before": before,
                "after": after,
                "checkpoint": save_pair(
                    solver, args.remote_root, f"{args.run_label}_smoke_ramp_reset0"
                ),
            }

        manifest.update(
            {
                "status": "complete",
                "classification": "diagnostic",
                "completed_epoch": time.time(),
                "transcript": transcript,
                "limitations": [
                    "The UDF is a constant-water-level abstraction, not a resolved brine outlet.",
                    "The sink time scale requires sensitivity testing before report-facing results.",
                    "The bottom water-level plane still needs a linked source-CAD dimension/image.",
                    "No carrier-field acceptance or mesh-convergence claim is made by this hook step.",
                ],
            }
        )
        write_json(manifest_path, manifest)
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(args.remote_root, f"{args.run_label}_manifest.json"),
            json.dumps(manifest, indent=2, default=str),
        )
        print(json.dumps(manifest, indent=2, default=str))
        print("setup07b: UDF HOOK IMPLEMENTATION COMPLETE (diagnostic, ramp=0)")
        return 0
    except Exception as exc:
        manifest.update(
            {
                "status": "failed",
                "classification": "unresolved",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        if prehook_pair is not None:
            try:
                restore_pair(solver, prehook_pair)
                manifest["rollback"] = "pre-hook case/data restored"
            except Exception as rollback_exc:
                manifest["rollback"] = f"FAILED: {type(rollback_exc).__name__}: {rollback_exc}"
        write_json(manifest_path, manifest)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
