#!/usr/bin/env python3
"""Public facade for modular Eulerian Wall Film diagnostics."""

from pyansys_fluent.ewf_audit import audit_ewf_dpm_settings
from pyansys_fluent.ewf_flux import (
    build_ewf_bookkeeping_target,
    extract_film_mass_flow,
    parse_film_flux_output,
)
from pyansys_fluent.ewf_report_specs import REPORT_SPECS, ReportSpec, report_specs_as_dicts
from pyansys_fluent.ewf_reports import (
    compute_report_definition,
    create_and_compute_snapshot,
    ensure_surface_report,
    flatten_snapshot_reports,
    parse_report_compute_output,
)

__all__ = [
    "REPORT_SPECS",
    "ReportSpec",
    "audit_ewf_dpm_settings",
    "build_ewf_bookkeeping_target",
    "compute_report_definition",
    "create_and_compute_snapshot",
    "ensure_surface_report",
    "extract_film_mass_flow",
    "flatten_snapshot_reports",
    "parse_film_flux_output",
    "parse_report_compute_output",
    "report_specs_as_dicts",
]
