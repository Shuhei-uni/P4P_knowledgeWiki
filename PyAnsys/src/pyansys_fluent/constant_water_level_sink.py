#!/usr/bin/env python3
"""Offline source-law and validation helpers for liquid-sink studies.

These numerical helpers do not configure Fluent or establish that a sink model
is suitable for a selected experiment. Historical UDFs remain in Git history.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any


ZONE_ROW = re.compile(
    r"^\s*(?P<id>\d+)\s+(?P<name>\S+)\s+(?P<type>\S+)(?:\s+.*)?$",
    flags=re.MULTILINE,
)


def bounded(value: float, lower: float, upper: float) -> float:
    """Return *value* clipped to a closed interval."""
    return max(lower, min(upper, float(value)))


def liquid_mass_source(
    density_kg_m3: float,
    volume_fraction: float,
    tau_s: float,
    ramp: float,
    *,
    adjacent_to_bottom: bool = True,
    alpha_min: float = 1.0e-12,
) -> float:
    """Evaluate the steady volumetric liquid source used by the C UDF."""
    density = float(density_kg_m3)
    alpha = bounded(float(volume_fraction), 0.0, 1.0)
    tau = float(tau_s)
    gain = bounded(float(ramp), 0.0, 1.0)
    if not adjacent_to_bottom or density < 0.0 or tau <= 0.0 or alpha <= alpha_min:
        return 0.0
    return -density * alpha * gain / tau


def momentum_source(mass_source_kg_m3_s: float, velocity_m_s: float) -> float:
    """Momentum removed with the local mixture velocity, in N/m3."""
    return float(mass_source_kg_m3_s) * float(velocity_m_s)


def integrated_sink_kg_s(
    sources_kg_m3_s: Sequence[float], cell_volumes_m3: Sequence[float]
) -> float:
    """Integrate signed volumetric sources over a collection of cells."""
    if len(sources_kg_m3_s) != len(cell_volumes_m3):
        raise ValueError("source and volume arrays must have equal length")
    if any(float(volume) < 0.0 for volume in cell_volumes_m3):
        raise ValueError("cell volumes must be non-negative")
    return sum(float(source) * float(volume) for source, volume in zip(sources_kg_m3_s, cell_volumes_m3))


def source_augmented_imbalance_percent(
    boundary_net_kg_s: float,
    integrated_source_kg_s: float,
    reference_inlet_kg_s: float,
) -> float:
    """Return steady mass imbalance after including a volumetric source.

    Fluent boundary reports use positive inflow and negative outflow. A sink is
    negative, so the conserved steady balance is ``boundary_net + source = 0``.
    """
    reference = abs(float(reference_inlet_kg_s))
    if reference <= 0.0:
        raise ValueError("reference inlet mass flow must be non-zero")
    return (
        abs(float(boundary_net_kg_s) + float(integrated_source_kg_s))
        / reference
        * 100.0
    )


def bottom_inventory_from_sink(
    integrated_source_kg_s: float, tau_s: float, ramp: float
) -> float:
    """Recover bottom-layer liquid inventory from ``sink=-M*R/tau``."""
    tau = float(tau_s)
    gain = float(ramp)
    if tau <= 0.0 or gain <= 0.0:
        raise ValueError("tau and ramp must be positive")
    return -float(integrated_source_kg_s) * tau / gain


def adaptive_tau_from_inventory(
    liquid_inventory_kg: float,
    target_sink_kg_s: float,
    minimum_tau_s: float,
    maximum_tau_s: float,
) -> float:
    """Return bounded feedback tau for ``sink=-inventory*ramp/tau``.

    When the marked band is empty, the weakest allowed source is selected so
    a fresh vapor-filled initialization is not driven by an arbitrarily small
    time scale before liquid reaches the band.
    """
    inventory = float(liquid_inventory_kg)
    target = float(target_sink_kg_s)
    minimum = float(minimum_tau_s)
    maximum = float(maximum_tau_s)
    if not all(math.isfinite(value) for value in (inventory, target, minimum, maximum)):
        raise ValueError("adaptive tau inputs must be finite")
    if target <= 0.0:
        raise ValueError("target sink must be positive")
    if minimum <= 0.0 or maximum < minimum:
        raise ValueError("adaptive tau bounds are invalid")
    if inventory <= 0.0:
        return maximum
    return bounded(inventory / target, minimum, maximum)


def parse_zone_table(text: str) -> dict[str, dict[str, Any]]:
    """Parse Fluent's ``mesh/modify-zones/list-zones`` table by zone name."""
    result: dict[str, dict[str, Any]] = {}
    for match in ZONE_ROW.finditer(text):
        name = match.group("name")
        result[name] = {
            "id": int(match.group("id")),
            "type": match.group("type"),
        }
    return result


def validate_sink_parameters(
    *, bottom_zone_id: int, liquid_phase_index: int, tau_s: float, ramp: float, alpha_min: float
) -> list[str]:
    """Return validation errors for values passed into the compiled UDF."""
    errors: list[str] = []
    if int(bottom_zone_id) < 0:
        errors.append("bottom zone id must be non-negative")
    if int(liquid_phase_index) < 0:
        errors.append("liquid phase index must be non-negative")
    if not math.isfinite(float(tau_s)) or float(tau_s) <= 0.0:
        errors.append("tau_s must be finite and positive")
    if not math.isfinite(float(ramp)) or not 0.0 <= float(ramp) <= 1.0:
        errors.append("ramp must lie in [0, 1]")
    if not math.isfinite(float(alpha_min)) or not 0.0 <= float(alpha_min) <= 1.0:
        errors.append("alpha_min must lie in [0, 1]")
    return errors


def find_phase_for_material(
    phase_materials: Mapping[str, Any], material_name: str
) -> str:
    """Resolve exactly one phase whose material matches *material_name*."""
    matches = [
        str(phase)
        for phase, material in phase_materials.items()
        if str(material).strip().lower() == material_name.strip().lower()
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one phase for material {material_name!r}; matches={matches}"
        )
    return matches[0]
