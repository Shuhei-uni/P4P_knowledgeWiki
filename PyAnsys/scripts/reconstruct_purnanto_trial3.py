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
    r"\Major Files\trial4.msh"
)
DEFAULT_OUTPUT_CASE = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial4-purnanto-recon-500.cas.h5"
)
DEFAULT_OUTPUT_DATA = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial4-purnanto-recon-500.dat.h5"
)
DEFAULT_LOG_FILE = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial4-purnanto-recon-500-log.txt"
)
MANUAL_VAPOR_NAME = "water-vapor-manual"
MANUAL_LIQUID_NAME = "water-liquid-manual"
MANUAL_VAPOR_DENSITY = 5.7974339
MANUAL_VAPOR_VISCOSITY = 1.52062e-05
MANUAL_LIQUID_DENSITY = 881.21088
MANUAL_LIQUID_VISCOSITY = 0.000145544


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a practical one-inlet Purnanto-style setup on trial4.msh."
    )
    parser.add_argument("--mesh", default=DEFAULT_MESH, help="Local mesh file to load.")
    parser.add_argument(
        "--output-case",
        default=DEFAULT_OUTPUT_CASE,
        help="Local case path to write after setup. Use empty string to skip write.",
    )
    parser.add_argument(
        "--output-data",
        default=DEFAULT_OUTPUT_DATA,
        help="Local data path to write after setup. Use empty string to skip write.",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help="Optional diagnostic log path. Use empty string to skip write.",
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
        default=500,
        help="Controlled diagnostic iteration count after hybrid initialization. Default: 500.",
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=50,
        help="Chunk size between diagnostic reports. Default: 50.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=250,
        help="Checkpoint interval for intermediate case/data writes. Default: 250.",
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


def try_settings_call(label: str, func, *, critical: bool = False) -> bool:
    try:
        func()
        print(f"{label}: OK")
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}")
        if critical:
            raise RuntimeError(f"{label} failed") from exc
        return False


def append_log_line(log_file: str, text: str) -> None:
    if not log_file.strip():
        return
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def set_operating_conditions(solver) -> None:
    print_header("Operating Conditions")

    def via_settings():
        op = solver.settings.setup.general.operating_conditions
        op.operating_pressure = 0
        op.gravity.enable = True
        op.gravity.components = [0.0, -9.81, 0.0]

    if try_settings_call("operating_conditions_settings_api", via_settings):
        try:
            print(f"operating_conditions_state: {solver.settings.setup.general.operating_conditions.get_state()}")
        except Exception as exc:
            print(f"operating_conditions_state: FAILED -> {exc}")
        return

    def scheme_fallback():
        solver.scheme.eval("(rpsetvar 'operating-pressure 0)")
        solver.scheme.eval("(rpsetvar 'gravity? #t)")
        solver.scheme.eval("(rpsetvar 'gravity-x 0.0)")
        solver.scheme.eval("(rpsetvar 'gravity-y -9.81)")
        solver.scheme.eval("(rpsetvar 'gravity-z 0.0)")

    if try_settings_call("operating_conditions_scheme_fallback", scheme_fallback, critical=True):
        try:
            print(f"operating_conditions_state: {solver.settings.setup.general.operating_conditions.get_state()}")
        except Exception as exc:
            print(f"operating_conditions_state: FAILED -> {exc}")
            raise RuntimeError("operating conditions verification failed") from exc


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

    vapor_ok = ensure_manual_fluid(
        MANUAL_VAPOR_NAME,
        MANUAL_VAPOR_DENSITY,
        MANUAL_VAPOR_VISCOSITY,
    )
    liquid_ok = ensure_manual_fluid(
        MANUAL_LIQUID_NAME,
        MANUAL_LIQUID_DENSITY,
        MANUAL_LIQUID_VISCOSITY,
    )
    if not vapor_ok or not liquid_ok:
        raise RuntimeError("phase material creation failed")

    try_settings_call(
        "assign_phase-1_material",
        lambda: setattr(phases["phase-1"], "material", MANUAL_VAPOR_NAME),
        critical=True,
    )
    try_settings_call(
        "assign_phase-2_material",
        lambda: setattr(phases["phase-2"], "material", MANUAL_LIQUID_NAME),
        critical=True,
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
            critical=True,
        )
    else:
        raise RuntimeError("inlet boundary not detected")

    if outlet_name:
        # Usually already correct, but keep this explicit.
        try_settings_call(
            "ensure_outlet_pressure_outlet",
            lambda: bc.set_zone_type(zone_list=[outlet_name], new_type="pressure-outlet"),
            critical=True,
        )
    else:
        raise RuntimeError("outlet boundary not detected")


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
        try_settings_call("set_mass_flow_inlet_state", lambda: inlet_obj.set_state(inlet_state), critical=True)
    else:
        raise RuntimeError("inlet boundary not detected")

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
        try_settings_call("set_pressure_outlet_state", lambda: outlet_obj.set_state(outlet_state), critical=True)
    else:
        raise RuntimeError("outlet boundary not detected")


def set_solution_methods(solver) -> None:
    print_header("Solution Methods")
    methods = solver.settings.solution.methods
    spatial = methods.spatial_discretization
    disc = spatial.discretization_scheme

    print("methods_children:", methods.child_names)
    print("methods_state_before:", methods.get_state())
    print("p_v_coupling_children:", methods.p_v_coupling.child_names)
    print("spatial_discretization_children:", spatial.child_names)
    print("discretization_scheme_objects:", disc.get_object_names())

    try_settings_call("set_coupling_simple", lambda: setattr(methods.p_v_coupling, "flow_scheme", "SIMPLE"))
    try_settings_call(
        "set_gradient_node_based",
        lambda: setattr(spatial, "gradient_scheme", "green-gauss-node-based"),
    )
    try_settings_call(
        "set_discretization_stack",
        lambda: disc.set_state(
            {
                "pressure": "presto!",
                "mom": "second-order-upwind",
                "mp": "quick",
                "k": "second-order-upwind",
                "epsilon": "second-order-upwind",
            }
        ),
    )
    print("methods_state_after:", methods.get_state())


def report_flux_sanity(
    solver,
    inlet_name: str | None,
    outlet_name: str | None,
    *,
    iteration_count: int | None = None,
    log_file: str = "",
) -> dict[str, dict[str, float]] | None:
    title = "Flux Sanity Checks" if iteration_count is None else f"Flux Sanity Checks @ {iteration_count} Iterations"
    print_header(title)
    if inlet_name is None or outlet_name is None:
        print("flux_sanity: SKIPPED -> inlet or outlet boundary missing")
        return None

    fluxes = solver.settings.results.report.fluxes
    if not fluxes.is_active():
        print("flux_sanity: SKIPPED -> report.fluxes not active")
        return None

    zones = [inlet_name, outlet_name]
    results: dict[str, dict[str, float]] = {}
    for domain in ("mixture", "phase-1", "phase-2"):
        try:
            result = fluxes.get_mass_flow(domain=domain, zones=zones)
            print(f"{domain}_mass_flow: {result}")
            results[domain] = {key: float(value) for key, value in result.items()}
        except Exception as exc:
            print(f"{domain}_mass_flow: FAILED -> {exc}")
            return None

    phase1_inlet = results["phase-1"].get(inlet_name, 0.0)
    phase1_outlet = results["phase-1"].get(outlet_name, 0.0)
    phase2_inlet = results["phase-2"].get(inlet_name, 0.0)
    phase2_outlet = results["phase-2"].get(outlet_name, 0.0)
    vapor_recovery_ratio = abs(phase1_outlet) / phase1_inlet if phase1_inlet else float("nan")
    liquid_carryover_ratio = abs(phase2_outlet) / phase2_inlet if phase2_inlet else float("nan")
    interpreted = {
        "iteration": float(iteration_count) if iteration_count is not None else float("nan"),
        "mixture_net": results["mixture"].get("Net", float("nan")),
        "phase1_inlet": phase1_inlet,
        "phase1_outlet": phase1_outlet,
        "phase2_inlet": phase2_inlet,
        "phase2_outlet": phase2_outlet,
        "vapor_recovery_ratio": vapor_recovery_ratio,
        "liquid_carryover_ratio": liquid_carryover_ratio,
    }
    interpreted_line = (
        f"iteration={iteration_count if iteration_count is not None else 'final'} | "
        f"mixture_net={interpreted['mixture_net']:.6f} | "
        f"phase1_in={phase1_inlet:.6f} | phase1_out={phase1_outlet:.6f} | "
        f"phase2_in={phase2_inlet:.6f} | phase2_out={phase2_outlet:.6e} | "
        f"vapor_recovery_ratio={vapor_recovery_ratio:.6f} | "
        f"liquid_carryover_ratio={liquid_carryover_ratio:.6e}"
    )
    print("interpreted_summary:", interpreted_line)
    append_log_line(log_file, interpreted_line)
    return results


def checkpoint_write(solver, output_case: str, output_data: str, iteration_count: int) -> None:
    if not output_case.strip() or not output_data.strip():
        return
    case_path = Path(output_case)
    data_path = Path(output_data)
    checkpoint_case = case_path.with_name(f"{case_path.stem}-iter{iteration_count}{case_path.suffix}")
    checkpoint_data = data_path.with_name(f"{data_path.stem}-iter{iteration_count}{data_path.suffix}")
    try_settings_call(
        f"write_checkpoint_case_{iteration_count}",
        lambda: solver.settings.file.write_case(file_name=str(checkpoint_case)),
    )
    try_settings_call(
        f"write_checkpoint_data_{iteration_count}",
        lambda: solver.settings.file.write_data(file_name=str(checkpoint_data)),
    )


def run_hybrid_init_and_diagnostic_iterations(
    solver,
    iterations: int,
    report_interval: int,
    checkpoint_interval: int,
    inlet_name: str | None,
    outlet_name: str | None,
    output_case: str,
    output_data: str,
    log_file: str,
) -> dict[str, dict[str, float]] | None:
    print_header("Initialization And Diagnostic Run")
    try_settings_call(
        "hybrid_initialize",
        lambda: solver.tui.solve.initialize.hyb_initialization(),
        critical=True,
    )
    if iterations <= 0:
        print("iterate: SKIPPED")
        return report_flux_sanity(solver, inlet_name, outlet_name, iteration_count=0, log_file=log_file)

    completed = 0
    latest_report: dict[str, dict[str, float]] | None = None
    chunk_size = max(1, report_interval)
    checkpoint_step = max(0, checkpoint_interval)
    while completed < iterations:
        step = min(chunk_size, iterations - completed)
        try_settings_call(
            f"iterate_chunk_{completed + step}",
            lambda step=step: solver.tui.solve.iterate(step),
            critical=True,
        )
        completed += step
        latest_report = report_flux_sanity(
            solver,
            inlet_name,
            outlet_name,
            iteration_count=completed,
            log_file=log_file,
        )
        if checkpoint_step > 0 and completed < iterations and completed % checkpoint_step == 0:
            checkpoint_write(solver, output_case, output_data, completed)
    return latest_report


def write_outputs_if_requested(solver, output_case: str, output_data: str) -> None:
    if output_case.strip():
        output_case_path = Path(output_case)
        output_case_path.parent.mkdir(parents=True, exist_ok=True)
        try_settings_call(
            "write_case",
            lambda: solver.settings.file.write_case(file_name=str(output_case_path)),
            critical=True,
        )
    else:
        raise RuntimeError("write_case path missing")

    if output_data.strip():
        output_data_path = Path(output_data)
        output_data_path.parent.mkdir(parents=True, exist_ok=True)
        try_settings_call(
            "write_data",
            lambda: solver.settings.file.write_data(file_name=str(output_data_path)),
            critical=True,
        )
    else:
        raise RuntimeError("write_data path missing")


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
        if inlet_name is None:
            raise RuntimeError("inlet boundary not detected")
        if outlet_name is None:
            raise RuntimeError("outlet boundary not detected")

        if args.log_file.strip():
            log_path = Path(args.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("", encoding="utf-8")

        print_header("Detected Zones")
        print(f"inlet_name: {inlet_name}")
        print(f"outlet_name: {outlet_name}")
        append_log_line(args.log_file, f"mesh={mesh_path}")
        append_log_line(args.log_file, f"inlet_name={inlet_name}")
        append_log_line(args.log_file, f"outlet_name={outlet_name}")

        convert_boundary_types(solver, inlet_name, outlet_name)
        set_multiphase_and_turbulence(solver)
        try_set_phase_materials(solver)
        set_operating_conditions(solver)
        configure_inlet_and_outlet(solver, inlet_name, outlet_name)
        set_solution_methods(solver)
        final_flux_report = run_hybrid_init_and_diagnostic_iterations(
            solver,
            args.iterations,
            args.report_interval,
            args.checkpoint_interval,
            inlet_name,
            outlet_name,
            args.output_case,
            args.output_data,
            args.log_file,
        )

        print_header("Configuration Snapshot")
        print(solver.tui.file.show_configuration())

        write_outputs_if_requested(solver, args.output_case, args.output_data)
        if final_flux_report is not None:
            append_log_line(args.log_file, f"final_output_case={args.output_case}")
            append_log_line(args.log_file, f"final_output_data={args.output_data}")
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
