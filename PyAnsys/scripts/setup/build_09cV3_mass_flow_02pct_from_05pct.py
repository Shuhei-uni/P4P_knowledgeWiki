#!/usr/bin/env python3
"""Create the server-1 2% tracked-liquid allocation child from verified 09cV3.

This is deliberately a case-only builder.  Fluent-native initialization and
iteration are started separately after the saved child has been reloaded and
audited.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from pyansys_fluent.common import remote_file_exists, write_json_snapshot  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402

REMOTE_DIR = r"C:\Users\syok443\P4P simulation"
PARENT = str(PureWindowsPath(REMOTE_DIR) / "09cV3-fDPM-05pct-finemist-5to100um.cas.h5")
CHILD = str(PureWindowsPath(REMOTE_DIR) / "09cV3-fDPM-02pct-finemist-5to100um.cas.h5")
RECOVERY = str(PureWindowsPath(REMOTE_DIR) / "09cV3-fDPM-05pct-prebuild-02pct-20260807.cas.h5")
SUMMARY = PROJECT_ROOT / "output" / "09cV3_mass_flow_02pct_from_05pct_20260807.json"
LIQUID_TOTAL = 116.920
EULERIAN_TARGET = 114.581600
DPM_TARGET = 2.338400
BIN_FLOWS = {
    "09cv3-finemist-07um": 0.1636512,
    "09cv3-finemist-14um": 0.4660596,
    "09cv3-finemist-24um": 0.5069640,
    "09cv3-finemist-35um": 0.4370004,
    "09cv3-finemist-49um": 0.5317048,
    "09cv3-finemist-69um": 0.1874424,
    "09cv3-finemist-89um": 0.0455776,
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def state(obj: Any) -> Mapping[str, Any]:
    value = obj.get_state()
    need(isinstance(value, Mapping), f"Expected mapping state, got {type(value).__name__}")
    return value


def get(payload: Mapping[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        need(isinstance(current, Mapping) and key in current, f"Missing state path: {'.'.join(keys)}")
        current = current[key]
    return current


def close(actual: Any, expected: float, label: str, tolerance: float = 1.0e-10) -> float:
    value = float(actual)
    need(abs(value - expected) <= tolerance, f"{label}: {value} != {expected}")
    return value


def audit(solver: Any, *, parent: bool) -> dict[str, Any]:
    setup = solver.settings.setup
    bc = setup.boundary_conditions
    need(set(bc.mass_flow_inlet.get_object_names()) == {"liquidinlet", "steaminlet"}, "Mass-flow inlet topology mismatch")
    need(not bc.velocity_inlet.get_object_names(), "Velocity-inlet topology unexpectedly active")
    models = state(setup.models)
    need(get(models, "multiphase", "model") == "mixture", "Multiphase model mismatch")
    need(get(models, "viscous", "model") == "k-epsilon" and get(models, "viscous", "k_epsilon_model") == "rng", "Turbulence model mismatch")
    need(get(models, "energy", "enabled") is False, "Energy unexpectedly enabled")
    interaction = state(setup.models.discrete_phase.general_settings.interaction)
    need(get(interaction, "enabled") is True and get(interaction, "update_sources_every_iteration") is True and int(get(interaction, "iteration_interval")) == 1, "DPM interaction controls mismatch")
    liquid = state(bc.mass_flow_inlet["liquidinlet"])
    steam = state(bc.mass_flow_inlet["steaminlet"])
    expected_liquid = 111.074 if parent else EULERIAN_TARGET
    liquid_value = close(get(liquid, "phase", "phase-2", "momentum", "mass_flow_rate", "value"), expected_liquid, "Eulerian liquid")
    vapor = close(get(steam, "phase", "phase-1", "momentum", "mass_flow_rate", "value"), 80.690, "Vapor flow")
    injections = state(setup.models.discrete_phase.injections)
    mapped = {str(name).casefold(): (str(name), item) for name, item in injections.items()}
    need(set(mapped) == set(BIN_FLOWS), f"Fine-mist injection identity mismatch: {sorted(mapped)}")
    flows: dict[str, float] = {}
    for key, expected in BIN_FLOWS.items():
        actual_name, item = mapped[key]
        if parent:
            expected = expected / 0.4
        need(item.get("particle_type") == "inert", f"{actual_name} particle type changed")
        need(item.get("material") == "water-liquid-at-psep-dpm", f"{actual_name} material changed")
        need(get(item, "injection_type", "option") == "surface", f"{actual_name} injection type changed")
        need(get(item, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"{actual_name} surface changed")
        flows[actual_name] = close(get(item, "initial_values", "mass_flow_rate", "total_flow_rate"), expected, f"{actual_name} flow")
    total = close(sum(flows.values()), 5.846 if parent else DPM_TARGET, "DPM total")
    need(abs(liquid_value + total - LIQUID_TOTAL) <= 1e-10, "Liquid accounting does not close")
    return {"eulerian_liquid_kg_s": liquid_value, "vapor_kg_s": vapor, "dpm_flows_kg_s": flows, "dpm_total_kg_s": total, "input_liquid_closed": True, "dpm_interaction": interaction}


def main() -> int:
    solver = connect(server_id="1")
    summary: dict[str, Any] = {"setup_id": "09cV3-02pct", "parent_case": PARENT, "child_case": CHILD, "recovery_case": RECOVERY, "case_identity_status": "explicit parent load + strict signature audit", "dpm_fraction_basis": "2% tracked-liquid allocation", "uncertainty": "Assumed, medium-risk engineering sensitivity; diagnostic only", "fluent_version": solver.get_fluent_version()}
    need(remote_file_exists(solver, PARENT), f"Parent missing: {PARENT}")
    need(not remote_file_exists(solver, CHILD), f"Refusing to overwrite child: {CHILD}")
    need(not remote_file_exists(solver, RECOVERY), f"Refusing to overwrite recovery case: {RECOVERY}")
    try:
        load_case_only(solver, PARENT, label="Load explicit 5% 09cV3 parent")
        summary["parent_audit"] = audit(solver, parent=True)
        write_case_only(solver, RECOVERY, "Write 5% prebuild recovery case")
        need(remote_file_exists(solver, RECOVERY), "Recovery case was not written")
        leaf = solver.settings.setup.boundary_conditions.mass_flow_inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate
        leaf.set_state({"option": "value", "value": EULERIAN_TARGET})
        close(get(state(leaf), "value"), EULERIAN_TARGET, "Eulerian liquid leaf readback")
        for key, value in BIN_FLOWS.items():
            branch = solver.settings.setup.models.discrete_phase.injections
            actual = next(name for name in branch.get_object_names() if str(name).casefold() == key)
            branch[actual].initial_values.mass_flow_rate.total_flow_rate.set_state(value)
            branch = solver.settings.setup.models.discrete_phase.injections
            actual = next(name for name in branch.get_object_names() if str(name).casefold() == key)
            close(get(state(branch[actual]), "initial_values", "mass_flow_rate", "total_flow_rate"), value, f"{actual} leaf readback")
        summary["pre_save_audit"] = audit(solver, parent=False)
        write_case_only(solver, CHILD, "Write 2% 09cV3 child")
        need(remote_file_exists(solver, CHILD), "Child case was not written")
        load_case_only(solver, CHILD, label="Reload explicit 2% 09cV3 child")
        summary["post_save_audit"] = audit(solver, parent=False)
        summary["status"] = "complete"
    except Exception as exc:
        summary["status"] = "failed"
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        write_json_snapshot(str(SUMMARY), summary)
        raise
    write_json_snapshot(str(SUMMARY), summary)
    print(f"child_case: {CHILD}")
    print(f"recovery_case: {RECOVERY}")
    print(f"summary_json: {SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
