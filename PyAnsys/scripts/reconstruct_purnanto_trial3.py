#!/usr/bin/env python3
"""Temporary PyFluent reconstruction of a Purnanto-style one-inlet setup.

This script aims for a practical near-baseline recreation on the user's local
mesh, not a claim of exact paper parity.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path
import traceback

import ansys.fluent.core as pyfluent


DEFAULT_MESH = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial3.msh"
)
DEFAULT_OUTPUT_CASE = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial3-purnanto-recon.cas.h5"
)
MANUAL_VAPOR_NAME = "water-vapor-manual"
MANUAL_LIQUID_NAME = "water-liquid-manual"
MANUAL_VAPOR_DENSITY = 5.7974339
MANUAL_VAPOR_VISCOSITY = 1.52062e-05
MANUAL_LIQUID_DENSITY = 881.21088
MANUAL_LIQUID_VISCOSITY = 0.000145544


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a practical one-inlet Purnanto-style setup on trial3.msh."
    )
    parser.add_argument("--mesh", default=DEFAULT_MESH, help="Local mesh file to load.")
    parser.add_argument(
        "--output-case",
        default=DEFAULT_OUTPUT_CASE,
        help="Local case path to write after setup. Use empty string to skip write.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=2,
        help="Requested Fluent processor count. Default: 2.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Short smoke-test iteration count after hybrid initialization. Default: 10.",
    )
    return parser


def print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def summarize_boundaries(boundary_state: Mapping) -> None:
    print_header("Boundary Summary")
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, Mapping):
            continue
        names = [str(name) for name in zones.keys() if str(name) != "settings"]
        if names:
            print(f"{boundary_type}: {', '.join(sorted(names))}")


def detect_zone_name(boundary_state: Mapping, boundary_type: str, preferred: str) -> str | None:
    section = boundary_state.get(boundary_type, {})
    if not isinstance(section, Mapping):
        return None
    if preferred in section:
        return preferred
    names = [str(name) for name in section.keys() if str(name) != "settings"]
    return names[0] if names else None


def try_settings_call(label: str, func) -> bool:
    try:
        func()
        print(f"{label}: OK")
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}")
        return False


def set_operating_conditions(solver) -> None:
    print_header("Operating Conditions")

    def via_settings():
        op = solver.settings.setup.general.operating_conditions
        op.operating_pressure = {"option": "value", "value": 0}
        op.gravity.enable = True
        op.gravity.components = [0.0, -9.81, 0.0]

    if try_settings_call("operating_conditions_settings_api", via_settings):
        return

    # Fallback: at minimum force gravity enabled. Pressure is already often 0 on clean loads.
    try_settings_call("gravity_scheme_fallback", lambda: solver.scheme.eval("(rpsetvar 'gravity? #t)"))


def set_multiphase_and_turbulence(solver) -> None:
    print_header("Models")
    models = solver.settings.setup.models

    try_settings_call("set_multiphase_mixture", lambda: setattr(models.multiphase, "model", "mixture"))
    try_settings_call("set_viscous_model", lambda: setattr(models.viscous, "model", "k-epsilon"))
    try_settings_call("set_k_epsilon_rng", lambda: setattr(models.viscous, "k_epsilon_model", "rng"))

    # Keep energy off per the requested temporary reconstruction.
    try_settings_call("set_energy_off", lambda: setattr(models.energy, "enabled", False))

    # These match the live audited baseline more closely if the API accepts them.
    try_settings_call(
        "set_rng_diff_viscosity",
        lambda: setattr(models.viscous.k_epsilon, "differential_viscosity_model", True),
    )
    try_settings_call(
        "set_rng_swirl_option",
        lambda: setattr(models.viscous.k_epsilon, "swirl_dominated_flow", True),
    )


def try_set_phase_materials(solver) -> None:
    print_header("Phase Materials")
    fluid_materials = solver.settings.setup.materials.fluid
    phases = solver.settings.setup.models.multiphase.phases

    def ensure_manual_fluid(name: str, density: float, viscosity: float) -> bool:
        try:
            if name not in fluid_materials.get_object_names():
                fluid_materials.create(name=name)
            fluid_materials[name].set_state(
                {
                    "name": name,
                    "chemical_formula": "",
                    "density": {"option": "value", "value": density},
                    "viscosity": {"option": "value", "value": viscosity},
                }
            )
            state = fluid_materials[name].get_state()
            print(
                f"{name}: density={state['density']['value']} "
                f"viscosity={state['viscosity']['value']}"
            )
            return True
        except Exception as exc:
            print(f"{name}: FAILED -> {exc}")
            return False

    ensure_manual_fluid(
        MANUAL_VAPOR_NAME,
        MANUAL_VAPOR_DENSITY,
        MANUAL_VAPOR_VISCOSITY,
    )
    ensure_manual_fluid(
        MANUAL_LIQUID_NAME,
        MANUAL_LIQUID_DENSITY,
        MANUAL_LIQUID_VISCOSITY,
    )

    try_settings_call(
        "assign_phase-1_material",
        lambda: setattr(phases["phase-1"], "material", MANUAL_VAPOR_NAME),
    )
    try_settings_call(
        "assign_phase-2_material",
        lambda: setattr(phases["phase-2"], "material", MANUAL_LIQUID_NAME),
    )

    # Approximate live-audit droplet size assumption if accessible.
    try_settings_call("phase-2 constant_dia", lambda: setattr(phases["phase-2"], "constant_dia", 1e-5))


def convert_boundary_types(solver, inlet_name: str | None, outlet_name: str | None) -> None:
    print_header("Boundary Type Conversion")
    bc = solver.settings.setup.boundary_conditions

    if inlet_name:
        try_settings_call(
            "convert_inlet_to_mass_flow_inlet",
            lambda: bc.set_zone_type(zone_list=[inlet_name], new_type="mass-flow-inlet"),
        )
    else:
        print("convert_inlet_to_mass_flow_inlet: SKIPPED -> no inlet boundary found")

    if outlet_name:
        # Usually already correct, but keep this explicit.
        try_settings_call(
            "ensure_outlet_pressure_outlet",
            lambda: bc.set_zone_type(zone_list=[outlet_name], new_type="pressure-outlet"),
        )
    else:
        print("ensure_outlet_pressure_outlet: SKIPPED -> no outlet boundary found")


def configure_inlet_and_outlet(solver, inlet_name: str | None, outlet_name: str | None) -> None:
    print_header("Boundary Conditions")
    bc = solver.settings.setup.boundary_conditions

    if inlet_name:
        inlet_obj = bc.mass_flow_inlet[inlet_name]
        inlet_state = {
            "phase": {
                "mixture": {
                    "momentum": {
                        "direction_specification": "Normal to Boundary",
                        "reference_frame": "Absolute",
                        "supersonic_gauge_pressure": {"option": "value", "value": 1_140_000},
                    },
                    "turbulence": {
                        "turbulence_specification": "Intensity and Hydraulic Diameter",
                        "turbulent_intensity": 0.0211,
                        "hydraulic_diameter": 0.724,
                    },
                },
                "phase-1": {
                    "momentum": {
                        "mass_flow_specification": "Mass Flow Rate",
                        "mass_flow_rate": {"option": "value", "value": 80.69},
                    }
                },
                "phase-2": {
                    "momentum": {
                        "mass_flow_specification": "Mass Flow Rate",
                        "mass_flow_rate": {"option": "value", "value": 116.92},
                    }
                },
            }
        }
        try_settings_call("set_mass_flow_inlet_state", lambda: inlet_obj.set_state(inlet_state))
    else:
        print("set_mass_flow_inlet_state: SKIPPED -> no inlet boundary found")

    if outlet_name:
        outlet_obj = bc.pressure_outlet[outlet_name]
        outlet_state = {
            "momentum": {
                "gauge_pressure": {"option": "value", "value": 1_120_000},
                "backflow_dir_spec_method": "Normal to Boundary",
                "backflow_pressure_spec": "Total Pressure",
                "backflow_reference_frame": "Absolute",
            },
            "turbulence": {
                "turbulence_specification": "Intensity and Hydraulic Diameter",
                "backflow_turbulent_intensity": 0.021525,
                "backflow_hydraulic_diameter": 0.724,
            },
            "phase": {
                "phase-2": {
                    "multiphase": {
                        "backflow_volume_fraction": {"option": "value", "value": 0.0}
                    }
                }
            },
        }
        try_settings_call("set_pressure_outlet_state", lambda: outlet_obj.set_state(outlet_state))
    else:
        print("set_pressure_outlet_state: SKIPPED -> no outlet boundary found")


def set_solution_methods(solver) -> None:
    print_header("Solution Methods")
    methods = solver.settings.solution.methods

    try_settings_call("set_coupling_simple", lambda: setattr(methods, "p_v_coupling", "simple"))
    try_settings_call("set_gradient_node_based", lambda: setattr(methods, "gradient_scheme", "green-gauss-node-based"))
    try_settings_call("set_pressure_presto", lambda: setattr(methods, "pressure", "presto"))
    try_settings_call("set_momentum_second_order", lambda: setattr(methods, "momentum", "second-order-upwind"))
    try_settings_call("set_volume_fraction_quick", lambda: setattr(methods, "volume_fraction", "quick"))
    try_settings_call("set_k_second_order", lambda: setattr(methods, "k", "second-order-upwind"))
    try_settings_call("set_epsilon_second_order", lambda: setattr(methods, "epsilon", "second-order-upwind"))


def run_hybrid_init_and_smoke_iterations(solver, iterations: int) -> None:
    print_header("Initialization And Smoke Test")
    try_settings_call("hybrid_initialize", lambda: solver.tui.solve.initialize.hyb_initialization())
    if iterations <= 0:
        print("iterate: SKIPPED")
        return
    try_settings_call("iterate", lambda: solver.tui.solve.iterate(iterations))


def write_case_if_requested(solver, output_case: str) -> None:
    if not output_case.strip():
        print("write_case: SKIPPED")
        return

    output_path = Path(output_case)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try_settings_call("write_case", lambda: solver.settings.file.write_case(file_name=str(output_path)))


def main() -> int:
    args = build_parser().parse_args()
    mesh_path = Path(args.mesh)
    if not mesh_path.exists():
        print(f"MESH_MISSING: {mesh_path}")
        return 2

    solver = None
    try:
        solver = pyfluent.Solver.from_install(
            precision="double",
            processor_count=args.processor_count,
            dimension=3,
        )
        print(f"LAUNCH_OK: {solver.get_fluent_version()}")

        solver.settings.file.read_mesh(file_name=str(mesh_path))
        print(f"MESH_LOAD_OK: {mesh_path}")

        boundary_state = solver.settings.setup.boundary_conditions.get_state()
        summarize_boundaries(boundary_state)

        inlet_name = detect_zone_name(boundary_state, "velocity_inlet", "inlet")
        if inlet_name is None:
            inlet_name = detect_zone_name(boundary_state, "mass_flow_inlet", "inlet")
        outlet_name = detect_zone_name(boundary_state, "pressure_outlet", "outlet")

        print_header("Detected Zones")
        print(f"inlet_name: {inlet_name}")
        print(f"outlet_name: {outlet_name}")

        convert_boundary_types(solver, inlet_name, outlet_name)
        set_multiphase_and_turbulence(solver)
        try_set_phase_materials(solver)
        set_operating_conditions(solver)
        configure_inlet_and_outlet(solver, inlet_name, outlet_name)
        set_solution_methods(solver)
        run_hybrid_init_and_smoke_iterations(solver, args.iterations)

        print_header("Configuration Snapshot")
        print(solver.tui.file.show_configuration())

        write_case_if_requested(solver, args.output_case)
        print("\nRECONSTRUCTION_SCRIPT_FINISHED")
        return 0
    except Exception as exc:
        print(f"RECONSTRUCTION_SCRIPT_FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1
    finally:
        if solver is not None:
            try:
                solver.exit()
                print("EXIT_OK")
            except Exception as exc:
                print(f"EXIT_FAILED: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
