#!/usr/bin/env python3
"""Deployment and readback helpers for setup 07c's thick liquid-sink band."""

from __future__ import annotations

import argparse
import base64
import hashlib
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402


LOCAL_UDF = PROJECT_ROOT / "udf" / "constant_water_level_thick_sink.c"
REQUIRED_UDM = 5
DEPLOY_REVISION = 2
RP_NAMES = (
    "user/cwl07c/bottom-zone-id",
    "user/cwl07c/liquid-phase-index",
    "user/cwl07c/tau-s",
    "user/cwl07c/ramp",
    "user/cwl07c/alpha-min",
    "user/cwl07c/bottom-y-m",
    "user/cwl07c/layer-thickness-m",
)
UDF_FUNCTIONS = {
    "adjust": "cwl07c_update_sink_mask",
    "on-demand": "cwl07c_rebuild_sink_mask",
    "mass": "cwl07c_liquid_mass_sink",
    "x-momentum": "cwl07c_x_momentum_sink",
    "y-momentum": "cwl07c_y_momentum_sink",
    "z-momentum": "cwl07c_z_momentum_sink",
}


def deploy_source(solver: Any, remote_root: str) -> dict[str, str]:
    source_bytes = LOCAL_UDF.read_bytes()
    sha = hashlib.sha256(source_bytes).hexdigest()
    source_name = f"constant_water_level_thick_sink_{sha[:12]}.c"
    remote_source = setup07b.remote_join(remote_root, source_name)
    encoded_path = remote_source + ".b64"
    encoded = base64.b64encode(source_bytes).decode("ascii")
    if not sweep.remote_text_write_best_effort(solver, encoded_path, encoded):
        raise RuntimeError(f"requires TUI fallback: could not deploy {encoded_path}")
    powershell = (
        'powershell -NoProfile -Command "'
        f"$b=[Convert]::FromBase64String((Get-Content -Raw '{encoded_path}'));"
        f"[IO.File]::WriteAllBytes('{remote_source}',$b)\""
    )
    solver.scheme.eval(f'(system "{sweep.quote_scheme_string(powershell)}")')
    sweep.remote_delete_best_effort(solver, encoded_path)
    if not remote_file_exists(solver, remote_source):
        raise RuntimeError(f"deployed UDF source is not visible: {remote_source}")
    remote_sha = mesh_study.remote_file_sha256(
        solver,
        remote_source,
        setup07b.remote_join(remote_root, f"_{source_name}_sha256.txt"),
    )
    if remote_sha != sha:
        raise RuntimeError(f"UDF SHA mismatch: local={sha}; remote={remote_sha}")
    return {
        "local_source": str(LOCAL_UDF),
        "source_sha256": sha,
        "remote_source": remote_source,
        "remote_source_name": source_name,
        "remote_source_sha256": remote_sha,
        "library_name": f"lib07c_cwl_{sha[:10]}_r{DEPLOY_REVISION}",
    }


def compile_and_load(
    solver: Any, deployment: Mapping[str, str], remote_root: str
) -> str:
    remote_chdir(solver, remote_root)
    library = deployment["library_name"]
    source_name = deployment["remote_source_name"]
    chunks: list[str] = []
    compile_command = (
        f'/define/user-defined/compiled-functions compile "{library}" '
        f'yes "{source_name}" "" ""'
    )
    load_command = f'/define/user-defined/compiled-functions load "{library}"'

    def menu_call(command: str):
        escaped = command.replace('"', '\\"')
        return solver.scheme.exec((f'(ti-menu-load-string "{escaped}")',))

    for label, call in (
        ("built_in_compiler", lambda: solver.tui.define.user_defined.use_built_in_compiler("yes")),
        ("compile", lambda: menu_call(compile_command)),
        ("load", lambda: menu_call(load_command)),
    ):
        _, output = setup07b.capture_console(call)
        chunks.append(f"\n--- {label} ---\n{output}")
        if re.search(r"(?:^|\n)\s*(?:error:|.*fatal error:|scons:\s*\*\*\*)", output, re.I):
            raise RuntimeError(f"UDF {label} failed\n{output}")
        if label == "load" and not re.search(
            rf"CWL07C:\s+reserved\s+{REQUIRED_UDM}\s+UDMs\s+at\s+offset\s+\d+",
            output,
            re.I,
        ):
            raise RuntimeError(
                "load transcript did not prove CWL07C UDM reservation\n" + output
            )
    return "".join(chunks) + f"\n--- exact compile command ---\n{compile_command}\n"


def configure_rp_parameters(
    solver: Any,
    *,
    bottom_zone_id: int,
    liquid_phase_index: int,
    tau_s: float,
    ramp: float,
    alpha_min: float,
    bottom_y_m: float,
    layer_thickness_m: float,
) -> dict[str, Any]:
    values = {
        "user/cwl07c/bottom-zone-id": (bottom_zone_id, "integer"),
        "user/cwl07c/liquid-phase-index": (liquid_phase_index, "integer"),
        "user/cwl07c/tau-s": (tau_s, "real"),
        "user/cwl07c/ramp": (ramp, "real"),
        "user/cwl07c/alpha-min": (alpha_min, "real"),
        "user/cwl07c/bottom-y-m": (bottom_y_m, "real"),
        "user/cwl07c/layer-thickness-m": (layer_thickness_m, "real"),
    }
    if layer_thickness_m <= 0.0:
        raise ValueError("layer thickness must be positive")
    for name, (value, kind) in values.items():
        setup07b.define_or_set_rp_var(solver, name, value, kind)
    return rp_readback(solver)


def rp_readback(solver: Any) -> dict[str, Any]:
    return {name: solver.scheme.eval(f"(rpgetvar '{name})") for name in RP_NAMES}


def hook_adjust(solver: Any, library: str) -> dict[str, str]:
    function = f"{UDF_FUNCTIONS['adjust']}::{library}"
    command = f'/define/user-defined/function-hooks/adjust "{function}" ""'
    expression = f'(ti-menu-load-string "{command.replace(chr(34), chr(92) + chr(34))}")'
    _, output = setup07b.capture_console(lambda: solver.scheme.exec((expression,)))
    if any(token in output.lower() for token in ("unknown", "error:")):
        raise RuntimeError(f"Adjust hook failed\n{output}")
    return {"function": function, "command": command, "transcript": output}


def clear_adjust_hook(solver: Any) -> dict[str, str]:
    """Clear Adjust hooks after a fixed geometric mask has been built on demand."""
    command = '/define/user-defined/function-hooks/adjust ""'
    expression = f'(ti-menu-load-string "{command.replace(chr(34), chr(92) + chr(34))}")'
    _, output = setup07b.capture_console(lambda: solver.scheme.exec((expression,)))
    if any(token in output.lower() for token in ("unknown", "error:")):
        raise RuntimeError(f"Adjust-hook clear failed\n{output}")
    return {"command": command, "transcript": output}


def execute_mask_builder(solver: Any, library: str) -> str:
    function = f"{UDF_FUNCTIONS['on-demand']}::{library}"
    command = f'/define/user-defined/execute-on-demand "{function}"'
    expression = f'(ti-menu-load-string "{command.replace(chr(34), chr(92) + chr(34))}")'
    _, output = setup07b.capture_console(lambda: solver.scheme.exec((expression,)))
    if "CWL07C:" not in output or "marked-cells=" not in output:
        raise RuntimeError(f"on-demand mask build lacked positive readback\n{output}")
    return output


def enable_and_hook_sources(
    solver: Any, *, liquid_phase: str, library: str
) -> dict[str, Any]:
    cell_zone = solver.settings.setup.cell_zone_conditions.fluid["fluid"]
    liquid_sources = cell_zone.phase[liquid_phase].sources
    liquid_sources.enable.set_state(True)
    liquid_sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
        liquid_phase
    ].sources
    liquid_terms = [str(name) for name in liquid_sources.terms.get_object_names()]
    mass_name = setup07b.choose_name(
        liquid_terms, ("mass", "continuity"), "liquid mass source term"
    )
    result: dict[str, Any] = {
        "liquid_phase": liquid_phase,
        "liquid_mass_term": mass_name,
        "liquid_mass_hook": setup07b.hook_source_entry(
            lambda: solver.settings.setup.cell_zone_conditions.fluid["fluid"]
            .phase[liquid_phase]
            .sources.terms[mass_name],
            UDF_FUNCTIONS["mass"],
            library,
        ),
    }
    mixture_sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
        "mixture"
    ].sources
    mixture_sources.enable.set_state(True)
    mixture_sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
        "mixture"
    ].sources
    mixture_terms = [str(name) for name in mixture_sources.terms.get_object_names()]
    aliases = {
        "x-momentum": ("x-momentum", "x momentum", "x-velocity"),
        "y-momentum": ("y-momentum", "y momentum", "y-velocity"),
        "z-momentum": ("z-momentum", "z momentum", "z-velocity"),
    }
    result["mixture_term_candidates"] = mixture_terms
    for role, role_aliases in aliases.items():
        term_name = setup07b.choose_name(mixture_terms, role_aliases, role)
        result[role] = {
            "term": term_name,
            **setup07b.hook_source_entry(
                lambda term_name=term_name: solver.settings.setup.cell_zone_conditions.fluid[
                    "fluid"
                ].phase["mixture"].sources.terms[term_name],
                UDF_FUNCTIONS[role],
                library,
            ),
        }
    result["complete_source_readback"] = safe_get_state(
        solver.settings.setup.cell_zone_conditions.fluid["fluid"],
        "setup07c_fluid_cell_zone",
    )
    return result


def source_readback(solver: Any) -> dict[str, Any]:
    cell_zone = solver.settings.setup.cell_zone_conditions.fluid["fluid"]
    return {
        "liquid_sources": cell_zone.phase["phase-2"].sources.get_state(),
        "vapor_sources": cell_zone.phase["phase-1"].sources.get_state(),
        "mixture_sources": cell_zone.phase["mixture"].sources.get_state(),
    }


def validate_source_readback(
    readback: Mapping[str, Any], *, library: str
) -> list[str]:
    errors: list[str] = []
    liquid = readback["liquid_sources"]
    vapor = readback["vapor_sources"]
    mixture = readback["mixture_sources"]
    expected = {
        "mass": f"{UDF_FUNCTIONS['mass']}::{library}",
        "x-momentum": f"{UDF_FUNCTIONS['x-momentum']}::{library}",
        "y-momentum": f"{UDF_FUNCTIONS['y-momentum']}::{library}",
        "z-momentum": f"{UDF_FUNCTIONS['z-momentum']}::{library}",
    }
    if not liquid.get("enable"):
        errors.append("liquid phase sources are disabled")
    if vapor.get("enable"):
        errors.append("vapor phase sources must remain disabled")
    if not mixture.get("enable"):
        errors.append("mixture momentum sources are disabled")
    for group, state, names in (
        ("liquid", liquid, ("mass",)),
        ("mixture", mixture, ("x-momentum", "y-momentum", "z-momentum")),
    ):
        terms = state.get("terms", {})
        for name in names:
            entries = terms.get(name, [])
            expected_entry = [{"option": "udf", "udf": expected[name]}]
            if entries != expected_entry:
                errors.append(
                    f"{group} {name} hook mismatch: expected={expected_entry}; actual={entries}"
                )
    return errors


def set_rp_real(solver: Any, name: str, value: float) -> float:
    setup07b.define_or_set_rp_var(solver, name, value, "real")
    actual = float(solver.scheme.eval(f"(rpgetvar '{name})"))
    if not math.isclose(actual, value, rel_tol=0.0, abs_tol=1.0e-12):
        raise RuntimeError(f"RP readback mismatch for {name}: {actual} != {value}")
    return actual


def find_named_udf(allowed: Iterable[str], base_name: str, library: str) -> str:
    values = [str(value) for value in allowed]
    matches = [
        value
        for value in values
        if base_name.lower() in value.lower() and library.lower() in value.lower()
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one UDF for {base_name}; candidates={values}"
        )
    return matches[0]
