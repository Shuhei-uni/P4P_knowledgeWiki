#!/usr/bin/env python3
"""Eulerian Wall Film boundary flux extraction and bookkeeping scaffolding."""

from __future__ import annotations

import contextlib
import io
import re
import time
from collections.abc import Mapping, Sequence
from typing import Any

from pyansys_fluent.ewf_core import normalize_token, safe_float
from pyansys_fluent.ewf_reports import flatten_snapshot_reports
from pyansys_fluent.extraction import safe_json

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
_FLUX_VALUE_RE = re.compile(
    rf"^\s*(?P<zone>[A-Za-z0-9_.-]+)\s+(?P<value>{_NUMBER}|[+-]?0)\s*$"
)


def parse_film_flux_output(raw_output: str) -> dict[str, Any]:
    values: dict[str, float] = {}
    for raw_line in raw_output.splitlines():
        match = _FLUX_VALUE_RE.match(raw_line.rstrip())
        if not match:
            continue
        value = safe_float(match.group("value"))
        if value is not None:
            values[match.group("zone")] = value
    net = next((value for key, value in values.items() if normalize_token(key) == "net"), None)
    return {"by_zone_kg_s": values, "net_kg_s": net}


def extract_film_mass_flow(
    solver: Any,
    *,
    zones: Sequence[str],
    domain: str = "mixture",
    settle_seconds: float = 0.5,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    buffer = io.StringIO()
    returned: Any = None

    try:
        command = solver.settings.results.report.fluxes.film_mass_flow
    except Exception as exc:
        return {
            "status": "unavailable",
            "domain": domain,
            "zones": list(zones),
            "attempts": [{"method": "settings.results.report.fluxes.film_mass_flow", "status": "failed", "error": f"{type(exc).__name__}: {exc}"}],
            "parsed": {"by_zone_kg_s": {}, "net_kg_s": None},
            "raw_output": "",
        }

    variants = (
        ("domain+zones", lambda: command(domain=domain, zones=list(zones))),
        ("domain+locations.physics", lambda: command(domain=domain, locations={"physics": list(zones)})),
    )
    ok = False
    for label, func in variants:
        try:
            with contextlib.redirect_stdout(buffer):
                returned = func()
                time.sleep(settle_seconds)
            attempts.append({"method": label, "status": "ok"})
            ok = True
            break
        except Exception as exc:
            attempts.append({"method": label, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})

    raw_output = buffer.getvalue()
    parsed = parse_film_flux_output(raw_output)
    if isinstance(returned, Mapping):
        returned_values = {
            str(key): safe_float(value)
            for key, value in returned.items()
            if safe_float(value) is not None
        }
        if returned_values and not parsed["by_zone_kg_s"]:
            parsed["by_zone_kg_s"] = returned_values
            parsed["net_kg_s"] = next(
                (value for key, value in returned_values.items() if normalize_token(key) == "net"),
                None,
            )
    return {
        "status": "ok" if ok else "failed",
        "domain": domain,
        "zones": list(zones),
        "attempts": attempts,
        "returned": safe_json(returned),
        "parsed": parsed,
        "raw_output": raw_output,
    }


def build_ewf_bookkeeping_target(
    snapshot: Mapping[str, Any],
    film_flux: Mapping[str, Any],
) -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    for row in flatten_snapshot_reports(snapshot):
        values[str(row["key"])] = {
            "value": row.get("value"),
            "unit": row.get("unit"),
            "status": row.get("status"),
        }
    return {
        "status": "bookkeeping-only",
        "reason": (
            "A single final snapshot cannot close the EWF transient balance. "
            "Film inventory change and source/outflow integrals require histories over a defined interval."
        ),
        "snapshot_terms": values,
        "instantaneous_film_flux": film_flux.get("parsed", {}),
        "required_for_closure": [
            "initial film inventory",
            "final film inventory",
            "time-integrated Film DPM Mass Source",
            "time-integrated film boundary inflow/outflow",
            "time-integrated stripped mass when active",
            "time-integrated separated mass when active",
            "explicit unresolved term",
        ],
    }
