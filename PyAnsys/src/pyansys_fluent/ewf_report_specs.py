#!/usr/bin/env python3
"""Semantic report specification registry for EWF diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ReportSpec:
    key: str
    suffix: str
    report_type_candidates: tuple[str, ...]
    report_type_tokens: tuple[tuple[str, ...], ...]
    field_candidates: tuple[str, ...]
    field_tokens: tuple[tuple[str, ...], ...]
    expected_dimension: str
    optional_mechanism: str | None = None


REPORT_SPECS: tuple[ReportSpec, ...] = (
    ReportSpec("film_courant_max", "courant-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-courant-number", "Film Courant Number"), (("film", "courant"),), "dimensionless"),
    ReportSpec("film_mass_total", "film-mass-total", ("surface-sum", "sum"), (("sum",),), ("film-mass", "Film Mass"), (("film", "mass"),), "kg"),
    ReportSpec("film_thickness_max", "thickness-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-thickness", "Film Thickness"), (("film", "thickness"),), "m"),
    ReportSpec("film_thickness_area_average", "thickness-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-thickness", "Film Thickness"), (("film", "thickness"),), "m"),
    ReportSpec("film_dpm_mass_source_total", "dpm-mass-source-total", ("surface-sum", "sum"), (("sum",),), ("film-dpm-mass-source", "Film DPM Mass Source"), (("film", "dpm", "mass", "source"),), "kg/s"),
    ReportSpec("film_outflow_mass_total", "outflow-mass-total", ("surface-sum", "sum"), (("sum",),), ("film-outflow-mass", "Film Outflow Mass"), (("film", "outflow", "mass"),), "kg"),
    ReportSpec("film_velocity_area_average", "velocity-mag-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-velocity-magnitude", "Film Velocity Magnitude"), (("film", "velocity", "magnitude"),), "m/s"),
    ReportSpec("film_velocity_max", "velocity-mag-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-velocity-magnitude", "Film Velocity Magnitude"), (("film", "velocity", "magnitude"),), "m/s"),
    ReportSpec("film_x_velocity_area_average", "x-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-x-velocity", "Film X Velocity", "Film X-Velocity"), (("film", "x", "velocity"),), "m/s"),
    ReportSpec("film_y_velocity_area_average", "y-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-y-velocity", "Film Y Velocity", "Film Y-Velocity"), (("film", "y", "velocity"),), "m/s"),
    ReportSpec("film_z_velocity_area_average", "z-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-z-velocity", "Film Z Velocity", "Film Z-Velocity"), (("film", "z", "velocity"),), "m/s"),
    ReportSpec("film_stripped_mass_total", "stripped-mass-total", ("surface-sum", "sum"), (("sum",),), ("film-stripped-mass", "Film Stripped Mass"), (("film", "stripped", "mass"),), "kg", optional_mechanism="particle_stripping"),
    ReportSpec("film_separated_mass_total", "separated-mass-total", ("surface-sum", "sum"), (("sum",),), ("film-separated-mass", "Film Separated Mass"), (("film", "separated", "mass"),), "kg", optional_mechanism="edge_separation"),
)


def report_specs_as_dicts() -> list[dict[str, Any]]:
    return [asdict(spec) for spec in REPORT_SPECS]
