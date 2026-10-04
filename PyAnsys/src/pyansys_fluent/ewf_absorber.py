"""Inventory-weighted bulk/EWF removal at the Phase 7.2A lower collector.

The existing inlet-throughput command is shared by both liquid inventories.
This is a numerical collector, not evaporation or droplet stripping.
"""
from __future__ import annotations

import math

LOWER_ZONE = "p71a-v2-virtual-outlet"
LOWER_FILM_WALL = "wall:004"
BULK_NORMALIZATION = "max(P71V2AvailableVolume,1e-6[m^3])"
BULK_SINK = "-P71V3BulkCommand*P71V2Alpha/P71V2NormalizationVolume"


def expression_definitions(density: float, film_dt: float, max_step_fraction: float = 0.1, film_steps_per_update: int = 1) -> dict[str, str]:
    if not (math.isfinite(density) and density > 0 and math.isfinite(film_dt) and film_dt > 0):
        raise ValueError("Finite positive liquid density and film timestep are required")
    if not 0 < max_step_fraction < 1:
        raise ValueError("Depletion fraction must lie strictly between zero and one")
    if film_steps_per_update < 1:
        raise ValueError("At least one film step per profile update is required")
    wall = f'["{LOWER_FILM_WALL}"]'
    return {
        "P71V3FilmDensity": f"{density:.17g}[kg/m^3]",
        "P71V3FilmTimeStep": f"{film_dt:.17g}[s]",
        "P71V3FilmStepsPerUpdate": str(int(film_steps_per_update)),
        "P71V3FilmUpdateSpan": "P71V3FilmTimeStep*P71V3FilmStepsPerUpdate",
        "P71V3MaxStepFraction": f"{max_step_fraction:.17g}",
        "P71V3FilmHeight": "max(FilmThickness,0[m])",
        "P71V3FilmVolume": f"AreaInt(P71V3FilmHeight,{wall})",
        "P71V3AvailableVolume": "P71V2AvailableVolume+P71V3FilmVolume",
        "P71V3NormalizationVolume": "max(P71V3AvailableVolume,1e-6[m^3])",
        "P71V3FilmRate": "min(P71V2Command/(P71V3FilmDensity*P71V3NormalizationVolume),P71V3MaxStepFraction/P71V3FilmUpdateSpan)",
        "P71V3FilmSink": "-P71V3FilmRate*P71V3FilmDensity*P71V3FilmHeight",
        "P71V3FilmSinkX": "P71V3FilmSink*FilmVelocity.x",
        "P71V3FilmSinkY": "P71V3FilmSink*FilmVelocity.y",
        "P71V3FilmSinkZ": "P71V3FilmSink*FilmVelocity.z",
        "P71V3FilmRemoval": f"-AreaInt(P71V3FilmSink,{wall})",
        "P71V3BulkCommand": "max(P71V2Command-P71V3FilmRemoval,0[kg/s])",
        "P71V3BulkRemoval": f'-VolumeInt(P71V2Sink,["{LOWER_ZONE}"])',
        "P71V3TotalRemoval": "P71V3BulkRemoval+P71V3FilmRemoval",
        "P71V3CommandError": "P71V3TotalRemoval-P71V2Command",
        "P71V3FilmInventory": "P71V3FilmDensity*P71V3FilmVolume",
    }


def define_expressions(solver, definitions: dict[str, str]) -> None:
    expressions = solver.settings.setup.named_expressions
    for name, definition in definitions.items():
        if name not in expressions.get_object_names():
            expressions.create(name=name)
        expressions[name].definition = definition
        if expressions[name].definition() != definition:
            raise RuntimeError(f"Expression readback failed: {name}")


def configure(solver, *, max_step_fraction: float = 0.1) -> dict:
    parameters = dict(solver.rp_vars("wall-film/model-parameters"))
    if parameters["ewf-adaptive?"]:
        raise RuntimeError("This collector requires a verified fixed film timestep")
    material = parameters["film-material"].strip('"')
    phase_material = solver.settings.setup.models.multiphase.phases["phase-2"].material()
    if material != phase_material:
        raise RuntimeError("Film and bulk liquid densities must use the same material")
    density = solver.settings.setup.materials.fluid[material].density.get_state()
    if density.get("option") != "value":
        raise RuntimeError("The shared volume weighting requires constant liquid density")
    # Profiles are refreshed per bulk iteration; conservatively protect all
    # inherited film steps even if the expressions refresh within that span.
    solver.settings.solution.run_calculation.profile_update_interval = 1
    steps_per_update = int(parameters["film-per-flow-iters"])
    definitions = expression_definitions(float(density["value"]), float(parameters["timestep-max"]), max_step_fraction, steps_per_update)
    define_expressions(solver, definitions)
    volume = float(solver.settings.setup.named_expressions["P71V3FilmVolume"].get_value())
    if not math.isfinite(volume) or volume < 0:
        raise RuntimeError("New film storage must evaluate before binding the sink")
    define_expressions(solver, {"P71V2NormalizationVolume": BULK_NORMALIZATION, "P71V2Sink": BULK_SINK})
    wall = solver.settings.setup.boundary_conditions.wall[LOWER_FILM_WALL].phase["mixture"].wall_film
    if not wall.eulerian_film_wall():
        raise RuntimeError("Lower film wall must be prepared before attaching the collector")
    wall.film_condition_type = "film-wall-initial"
    wall.enable_flow_momentum_coupling = False
    wall.enable_film_source_terms = True
    wall.film_mass_source.set_state({"option": "value", "value": "P71V3FilmSink"})
    wall.momentum_source.set_state([
        {"option": "value", "value": f"P71V3FilmSink{axis}"} for axis in "XYZ"
    ])
    solver.settings.solution.run_calculation.profile_update_interval = 1
    return {"density": density, "material": material, "definitions": definitions, "film_wall": wall.get_state()}


def readback(solver) -> dict:
    expressions = solver.settings.setup.named_expressions
    names = ["P71V3FilmVolume", "P71V3AvailableVolume", "P71V3FilmRate", "P71V3BulkCommand", "P71V3BulkRemoval", "P71V3FilmRemoval", "P71V3TotalRemoval", "P71V3CommandError", "P71V3FilmInventory", "P71V2Command"]
    values = {name: float(expressions[name].get_value()) for name in names}
    if not all(math.isfinite(value) for value in values.values()):
        raise RuntimeError(f"Nonfinite collector readback: {values}")
    if min(values["P71V3BulkRemoval"], values["P71V3FilmRemoval"]) < -1e-9:
        raise RuntimeError("Collector became a positive mass source")
    if values["P71V3TotalRemoval"] > values["P71V2Command"] * (1 + 1e-8) + 1e-8:
        raise RuntimeError("Combined removal exceeds the single throughput command")
    parameters = dict(solver.rp_vars("wall-film/model-parameters"))
    interval = int(solver.settings.solution.run_calculation.profile_update_interval())
    span = float(parameters["timestep-max"]) * int(parameters["film-per-flow-iters"]) * interval
    fraction = float(expressions["P71V3MaxStepFraction"].get_value())
    if values["P71V3FilmRate"] * span > fraction * (1 + 1e-8):
        raise RuntimeError("Film depletion bound is invalid for the live update cadence")
    wall = solver.settings.setup.boundary_conditions.wall[LOWER_FILM_WALL].phase["mixture"].wall_film.get_state()
    if wall.get("film_mass_source", {}).get("value") != "P71V3FilmSink" or not wall.get("enable_film_source_terms"):
        raise RuntimeError("Film absorber mass hook was not retained")
    if expressions["P71V2NormalizationVolume"].definition() != BULK_NORMALIZATION or expressions["P71V2Sink"].definition() != BULK_SINK:
        raise RuntimeError("Bulk collector does not retain its floor and remaining shared command")
    expected_momentum = [f"P71V3FilmSink{axis}" for axis in "XYZ"]
    if [item.get("value") for item in wall.get("momentum_source", [])] != expected_momentum:
        raise RuntimeError("Film momentum removal hooks were not retained")
    return {"values": values, "lower_film_wall": wall, "bulk_normalization": expressions["P71V2NormalizationVolume"].definition()}


def ensure_reports(solver, monitor_root: str) -> dict:
    """Persist separate actual removal and lower-film inventory histories."""
    from pathlib import PureWindowsPath
    from pyansys_fluent.ewf_reports import ensure_surface_report
    from pyansys_fluent.ewf_report_specs import REPORT_SPECS

    report_root = solver.settings.solution.report_definitions
    expression_reports = report_root.single_valued_expression
    names = []
    for suffix, expression in {
        "bulk-removal": "P71V3BulkRemoval", "film-removal": "P71V3FilmRemoval",
        "total-removal": "P71V3TotalRemoval", "command": "P71V2Command",
        "command-error": "P71V3CommandError", "lower-inventory": "P71V3FilmInventory",
    }.items():
        name = f"p72a-collector-{suffix}"
        if name not in expression_reports.get_object_names():
            expression_reports.create(name=name)
        expression_reports[name].definition = expression
        expression_reports[name].average_over = 1
        names.append(name)
    lower = []
    for spec in REPORT_SPECS:
        if spec.key in {"film_mass_total", "film_thickness_max", "film_velocity_max", "film_outflow_mass_total", "film_courant_max"}:
            result = ensure_surface_report(solver, spec, prefix="p72a-collector-lower", surfaces=[LOWER_FILM_WALL],
                object_policy="replace", create_history_file=False, frequency=1)
            lower.append(result)
            names.append(result["name"])
    files = solver.settings.solution.monitor.report_files
    for name in names:
        if name not in files.get_object_names():
            files.create(name=name)
        files[name].set_state({"report_defs": [name], "file_name": str(PureWindowsPath(monitor_root) / f"{name}.out"),
                               "frequency": 1, "active": True})
    computed = report_root.compute(report_defs=names)
    return {"names": names, "lower_reports": lower, "native_compute": computed,
            "files": {name: files[name].get_state() for name in names}}
