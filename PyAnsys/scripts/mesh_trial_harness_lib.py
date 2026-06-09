#!/usr/bin/env python3
"""Helpers for the local PyFluent mesh trial harness."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import re
import time
from typing import Any

try:
    import ansys.fluent.core as pyfluent
except ModuleNotFoundError:  # pragma: no cover - exercised only on machines without PyFluent
    pyfluent = None


MESH_SUFFIXES = (
    ".msh",
    ".msh.h5",
    ".mesh",
    ".mesh.h5",
    ".meshdat",
)
CASE_SUFFIXES = (".cas", ".cas.h5")
GEOMETRY_SUFFIXES = (
    ".step",
    ".stp",
    ".iges",
    ".igs",
    ".scdoc",
    ".scdocx",
    ".x_t",
    ".x_b",
    ".sat",
)
WORKFLOW_SUFFIXES = (".wft",)
DEFAULT_BAD_QUALITY_THRESHOLD = 0.15
DEFAULT_CELL_CAP = 1_000_000
DEFAULT_TRIAL_PRESET = "first-milestone"


@dataclass
class ZoneInventory:
    boundary_by_type: dict[str, list[str]]
    boundary_flat: list[str]
    cell_zone_names: list[str]


@dataclass
class ZonePreservation:
    mode: str
    preserved: bool
    missing_boundaries: list[str]
    added_boundaries: list[str]
    wrong_boundary_type: dict[str, dict[str, str]]
    missing_cell_zones: list[str]
    added_cell_zones: list[str]


@dataclass
class MeshMetrics:
    node_count: int | None = None
    face_count: int | None = None
    cell_count: int | None = None
    min_orthogonal_quality: float | None = None
    max_equivolume_skewness: float | None = None
    bad_cell_count: int | None = None
    bad_cell_fraction: float | None = None
    bad_cells_by_threshold: dict[str, int] = field(default_factory=dict)
    bad_cell_fraction_by_threshold: dict[str, float] = field(default_factory=dict)
    max_aspect_ratio: float | None = None
    min_expansion_ratio: float | None = None
    transcript_path: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class TrialDelta:
    cell_count: int | None = None
    min_orthogonal_quality: float | None = None
    max_equivolume_skewness: float | None = None
    bad_cell_fraction: float | None = None


@dataclass
class TrialAssessment:
    improved_metrics: list[str]
    under_cell_cap: bool
    zone_preservation_ok: bool
    success: bool


@dataclass
class RequiredZoneContract:
    boundary_zones: list[str]
    boundary_zone_types: dict[str, str]
    cell_zones: list[str]
    source_path: str | None = None


@dataclass
class RequiredZoneCheck:
    all_present: bool
    missing_boundary_zones: list[str]
    wrong_boundary_type: dict[str, dict[str, str]]
    missing_cell_zones: list[str]


@dataclass
class QualityGateResult:
    acceptable_metrics: list[str]
    improved_metrics: list[str]
    failed_metrics: list[str]
    acceptable: bool


@dataclass
class TrialReport:
    name: str
    mode: str
    status: str
    input_artifact: str
    input_artifact_type: str
    output_case: str | None
    output_mesh: str | None
    zone_inventory: ZoneInventory | None
    zone_preservation: ZonePreservation | None
    metrics: MeshMetrics | None
    delta_vs_baseline: TrialDelta | None
    assessment: TrialAssessment | None
    notes: list[str]


def empty_zone_inventory() -> ZoneInventory:
    return ZoneInventory(boundary_by_type={}, boundary_flat=[], cell_zone_names=[])


def empty_required_zone_contract() -> RequiredZoneContract:
    return RequiredZoneContract(
        boundary_zones=[],
        boundary_zone_types={},
        cell_zones=[],
        source_path=None,
    )


def detect_artifact_type(path: Path) -> str:
    name = path.name.lower()
    if any(name.endswith(suffix) for suffix in CASE_SUFFIXES):
        return "case"
    if any(name.endswith(suffix) for suffix in MESH_SUFFIXES):
        return "mesh"
    if any(name.endswith(suffix) for suffix in GEOMETRY_SUFFIXES):
        return "geometry"
    if any(name.endswith(suffix) for suffix in WORKFLOW_SUFFIXES):
        return "workflow"
    return "unknown"


def artifact_priority(kind: str) -> int:
    order = {
        "case": 0,
        "mesh": 1,
        "geometry": 2,
        "workflow": 3,
        "unknown": 99,
    }
    return order.get(kind, 99)


def resolve_input_artifact(path_text: str, artifact_hint: str = "auto") -> tuple[Path, str]:
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input artifact does not exist: {path}")

    if path.is_file():
        kind = detect_artifact_type(path) if artifact_hint == "auto" else artifact_hint
        return path, kind

    candidates = [candidate for candidate in path.rglob("*") if candidate.is_file()]
    if artifact_hint != "auto":
        candidates = [candidate for candidate in candidates if detect_artifact_type(candidate) == artifact_hint]

    typed_candidates = [
        (candidate, detect_artifact_type(candidate))
        for candidate in candidates
        if detect_artifact_type(candidate) != "unknown"
    ]
    if not typed_candidates:
        raise FileNotFoundError(f"No supported artifacts found under: {path}")

    typed_candidates.sort(
        key=lambda item: (
            artifact_priority(item[1]),
            -item[0].stat().st_mtime,
            str(item[0]).lower(),
        )
    )
    return typed_candidates[0]


def latest_transcript_after(directory: Path, previous: set[str]) -> Path | None:
    candidates = sorted(
        directory.glob("fluent-*.trn"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        if str(candidate) not in previous:
            return candidate
    return candidates[0] if candidates else None


def json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_required_zones_text(text: str) -> RequiredZoneContract:
    boundary_zones: list[str] = []
    boundary_zone_types: dict[str, str] = {}
    cell_zones: list[str] = []
    current_section: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lowered = line.lower()
        if lowered in {"[boundary]", "[boundaries]", "boundary:", "boundaries:"}:
            current_section = "boundary"
            continue
        if lowered in {"[cell]", "[cells]", "[cell_zones]", "cell:", "cells:", "cell_zones:"}:
            current_section = "cell"
            continue

        if ":" in line:
            prefix, value = line.split(":", 1)
            prefix = prefix.strip().lower()
            value = value.strip()
            if not value:
                continue
            if prefix in {"boundary", "boundaries"}:
                name, zone_type = parse_required_boundary_value(value)
                boundary_zones.append(name)
                if zone_type is not None:
                    boundary_zone_types[name] = zone_type
                continue
            if prefix in {"cell", "cells", "cell_zone", "cell_zones"}:
                cell_zones.append(value)
                continue

        if current_section == "boundary":
            name, zone_type = parse_required_boundary_value(line)
            boundary_zones.append(name)
            if zone_type is not None:
                boundary_zone_types[name] = zone_type
        elif current_section == "cell":
            cell_zones.append(line)
        else:
            raise ValueError(
                "Required zones file must declare sections or prefixes. "
                f"Could not route line: {line!r}"
            )

    return RequiredZoneContract(
        boundary_zones=sorted(dict.fromkeys(boundary_zones)),
        boundary_zone_types=boundary_zone_types,
        cell_zones=sorted(dict.fromkeys(cell_zones)),
        source_path=None,
    )


def parse_required_boundary_value(value: str) -> tuple[str, str | None]:
    if "|" not in value:
        return value.strip(), None
    name, zone_type = value.split("|", 1)
    return name.strip(), zone_type.strip()


def load_required_zone_contract(path: Path) -> RequiredZoneContract:
    contract = parse_required_zones_text(path.read_text(encoding="utf-8"))
    contract.source_path = str(path)
    return contract


def validate_required_zones(
    inventory: ZoneInventory,
    contract: RequiredZoneContract,
) -> RequiredZoneCheck:
    boundary_names = set(inventory.boundary_flat)
    cell_names = set(inventory.cell_zone_names)
    missing_boundary = sorted(name for name in contract.boundary_zones if name not in boundary_names)
    missing_cell = sorted(name for name in contract.cell_zones if name not in cell_names)
    actual_boundary_type_by_name = {
        name: boundary_type
        for boundary_type, names in inventory.boundary_by_type.items()
        for name in names
    }
    wrong_boundary_type: dict[str, dict[str, str]] = {}
    for name, expected_type in contract.boundary_zone_types.items():
        actual_type = actual_boundary_type_by_name.get(name)
        if actual_type is None or actual_type == expected_type:
            continue
        wrong_boundary_type[name] = {"expected": expected_type, "actual": actual_type}
    return RequiredZoneCheck(
        all_present=not missing_boundary and not missing_cell and not wrong_boundary_type,
        missing_boundary_zones=missing_boundary,
        wrong_boundary_type=wrong_boundary_type,
        missing_cell_zones=missing_cell,
    )


def write_required_zones_template(path: Path, inventory: ZoneInventory) -> None:
    lines = [
        "# Required boundary and cell zones template",
        "# Replace this baseline-observed list with the exact required contract if needed.",
        "",
        "[boundary]",
    ]
    for boundary_type, names in sorted(inventory.boundary_by_type.items()):
        for name in names:
            lines.append(f"{name} | {boundary_type}")
    lines.extend(["", "[cell]"])
    lines.extend(inventory.cell_zone_names)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inventory_from_boundary_state(boundary_state: Mapping[str, Any]) -> dict[str, list[str]]:
    inventory: dict[str, list[str]] = {}
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, Mapping):
            continue
        names = sorted(str(name) for name in zones.keys() if str(name) != "settings")
        if names:
            inventory[str(boundary_type)] = names
    return inventory


def inventory_from_cell_zone_state(cell_zone_state: Mapping[str, Any]) -> list[str]:
    names: set[str] = set()
    for zone_type, zones in cell_zone_state.items():
        if not isinstance(zones, Mapping):
            continue
        for name in zones.keys():
            name_text = str(name)
            if name_text == "settings":
                continue
            names.add(name_text)
    return sorted(names)


def collect_zone_inventory_from_solver(session) -> ZoneInventory:
    boundary_state = session.settings.setup.boundary_conditions.get_state()
    cell_zone_state = session.settings.setup.cell_zone_conditions.get_state()
    boundary_by_type = inventory_from_boundary_state(boundary_state)
    boundary_flat = sorted({name for names in boundary_by_type.values() for name in names})
    cell_zone_names = inventory_from_cell_zone_state(cell_zone_state)
    return ZoneInventory(
        boundary_by_type=boundary_by_type,
        boundary_flat=boundary_flat,
        cell_zone_names=cell_zone_names,
    )


def compare_zone_inventories(
    baseline: ZoneInventory,
    current: ZoneInventory,
    mode: str,
) -> ZonePreservation:
    baseline_boundaries = set(baseline.boundary_flat)
    current_boundaries = set(current.boundary_flat)
    baseline_cells = set(baseline.cell_zone_names)
    current_cells = set(current.cell_zone_names)

    missing_boundaries = sorted(baseline_boundaries - current_boundaries)
    added_boundaries = sorted(current_boundaries - baseline_boundaries)
    missing_cell_zones = sorted(baseline_cells - current_cells)
    added_cell_zones = sorted(current_cells - baseline_cells)
    baseline_boundary_type_by_name = {
        name: boundary_type
        for boundary_type, names in baseline.boundary_by_type.items()
        for name in names
    }
    current_boundary_type_by_name = {
        name: boundary_type
        for boundary_type, names in current.boundary_by_type.items()
        for name in names
    }
    wrong_boundary_type: dict[str, dict[str, str]] = {}
    for name, expected_type in baseline_boundary_type_by_name.items():
        current_type = current_boundary_type_by_name.get(name)
        if current_type is None or current_type == expected_type:
            continue
        wrong_boundary_type[name] = {"expected": expected_type, "actual": current_type}
    preserved = not any(
        (
            missing_boundaries,
            added_boundaries,
            wrong_boundary_type,
            missing_cell_zones,
            added_cell_zones,
        )
    )
    return ZonePreservation(
        mode=mode,
        preserved=preserved,
        missing_boundaries=missing_boundaries,
        added_boundaries=added_boundaries,
        wrong_boundary_type=wrong_boundary_type,
        missing_cell_zones=missing_cell_zones,
        added_cell_zones=added_cell_zones,
    )


def extract_latest_float(pattern: str, text: str) -> float | None:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if not matches:
        return None
    return float(matches[-1])


def extract_latest_int(pattern: str, text: str) -> int | None:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if not matches:
        return None
    return int(matches[-1])


def parse_check_quality_from_text(text: str) -> dict[str, float | None]:
    return {
        "min_orthogonal_quality": extract_latest_float(
            r"Minimum Orthogonal Quality =\s+([0-9eE+\-.]+)", text
        ),
        "max_equivolume_skewness": extract_latest_float(
            r"Maximum Equivolume Skewness =\s+([0-9eE+\-.]+)", text
        ),
        "max_aspect_ratio": extract_latest_float(
            r"Maximum Aspect Ratio =\s+([0-9eE+\-.]+)", text
        ),
        "min_expansion_ratio": extract_latest_float(
            r"Minimum Expansion Ratio =\s+([0-9eE+\-.]+)", text
        ),
    }


def parse_distribution_low_count(payload: Sequence[Any]) -> int | None:
    if len(payload) < 2:
        return None
    first_bin = payload[1]
    if isinstance(first_bin, Sequence) and not isinstance(first_bin, (str, bytes)) and first_bin:
        first_value = first_bin[0]
        if isinstance(first_value, (int, float)):
            return int(first_value)
    return None


def collect_transcript_metrics(transcript_path: Path | None) -> dict[str, float | None]:
    if transcript_path is None or not transcript_path.exists():
        return {
            "min_orthogonal_quality": None,
            "max_equivolume_skewness": None,
            "max_aspect_ratio": None,
            "min_expansion_ratio": None,
        }
    text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    return parse_check_quality_from_text(text)


def collect_transcript_cell_count(transcript_path: Path | None) -> int | None:
    if transcript_path is None or not transcript_path.exists():
        return None
    text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    return extract_latest_int(r"cells:\s+(\d+)", text)


def collect_transcript_entity_count(transcript_path: Path | None, entity: str) -> int | None:
    if transcript_path is None or not transcript_path.exists():
        return None
    text = transcript_path.read_text(encoding="utf-8", errors="ignore")
    return extract_latest_int(rf"{re.escape(entity)}:\s+(\d+)", text)


def parse_zone_inventory_from_mesh_statistics(path: Path) -> ZoneInventory:
    boundary_by_type: dict[str, list[str]] = {}
    boundary_flat: set[str] = set()
    cell_zone_names: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    in_zone_table = False
    for line in text.splitlines():
        if line.strip() == "Zone Information:":
            in_zone_table = True
            continue
        if not in_zone_table:
            continue
        if line.strip().startswith("Entity Count:"):
            break
        match = re.match(r"^\s*(\d+)\s+(.*?)\s{2,}(.*?)\s+(\d+)\s*$", line)
        if not match:
            continue
        _zone_id, name, zone_type, _count = match.groups()
        name = name.strip()
        zone_type = zone_type.strip()
        if zone_type in {"fluid"}:
            cell_zone_names.append(name)
            continue
        if zone_type in {"interior", "node", "boundary-node"}:
            continue
        boundary_by_type.setdefault(zone_type, []).append(name)
        boundary_flat.add(name)

    normalized = {key: sorted(values) for key, values in boundary_by_type.items()}
    return ZoneInventory(
        boundary_by_type=normalized,
        boundary_flat=sorted(boundary_flat),
        cell_zone_names=sorted(cell_zone_names),
    )


def collect_zone_inventory_from_meshing(
    session,
    *,
    output_dir: Path,
    trial_name: str,
) -> ZoneInventory:
    statistics_path = output_dir / f"{trial_name}-mesh-statistics.txt"
    session.tui.report.mesh_statistics('"' + str(statistics_path) + '"')
    return parse_zone_inventory_from_mesh_statistics(statistics_path)


def collect_mesh_metrics_from_meshing(
    session,
    *,
    transcript_path: Path | None,
    bad_quality_threshold: float,
) -> MeshMetrics:
    notes: list[str] = []
    transcript_metrics = collect_transcript_metrics(transcript_path)
    transcript_cell_count = collect_transcript_cell_count(transcript_path)
    transcript_node_count = collect_transcript_entity_count(transcript_path, "nodes")
    transcript_face_count = collect_transcript_entity_count(transcript_path, "faces")
    try:
        zone_ids_raw = session.meshing_utilities.get_cell_zones(filter="*")
        zone_ids = list(zone_ids_raw) if zone_ids_raw is not None else []
    except Exception as exc:
        zone_ids = []
        notes.append(
            f"Could not query cell zones from meshing utilities: {type(exc).__name__}: {exc}"
        )

    total_cells = 0
    minimum_orthogonal: float | None = None
    bad_cell_count = 0
    thresholds = [0.15, 0.10, 0.05]
    bad_cells_by_threshold = {f"{threshold:.2f}": 0 for threshold in thresholds}

    for zone_id in zone_ids:
        quality_limits = session.meshing_utilities.get_cell_quality_limits(
            cell_zone_id_list=[zone_id],
            measure="Orthogonal Quality",
        )
        if isinstance(quality_limits, Sequence) and len(quality_limits) >= 2:
            total_cells += int(quality_limits[0])
            zone_min = float(quality_limits[1])
            minimum_orthogonal = (
                zone_min
                if minimum_orthogonal is None
                else min(minimum_orthogonal, zone_min)
            )
        else:
            notes.append(f"Unexpected quality-limits payload for zone {zone_id}: {quality_limits!r}")

        for threshold in thresholds:
            distribution = session.meshing_utilities.get_cell_mesh_distribution(
                cell_zone_id_list=[zone_id],
                measure="Orthogonal Quality",
                partitions=2,
                range=[0.0, threshold],
            )
            low_count = (
                parse_distribution_low_count(distribution)
                if isinstance(distribution, Sequence)
                else None
            )
            if low_count is None:
                notes.append(
                    f"Could not parse bad-cell distribution for zone {zone_id} at threshold {threshold:.2f}: {distribution!r}"
                )
            else:
                bad_cells_by_threshold[f"{threshold:.2f}"] += low_count

    if zone_ids:
        session.tui.mesh.check_quality_level(1)
        session.tui.mesh.check_quality()
        transcript_metrics = collect_transcript_metrics(transcript_path)
    else:
        notes.append("No cell zones found in meshing session; using transcript-only fallback where available.")

    if minimum_orthogonal is None:
        minimum_orthogonal = transcript_metrics["min_orthogonal_quality"]

    bad_cell_fraction = None
    bad_cell_fraction_by_threshold: dict[str, float] = {}
    if total_cells > 0:
        for threshold_key, count in bad_cells_by_threshold.items():
            bad_cell_fraction_by_threshold[threshold_key] = count / total_cells
        bad_cell_count = bad_cells_by_threshold[f"{bad_quality_threshold:.2f}"] if f"{bad_quality_threshold:.2f}" in bad_cells_by_threshold else 0
        bad_cell_fraction = bad_cell_fraction_by_threshold.get(f"{bad_quality_threshold:.2f}")

    return MeshMetrics(
        node_count=transcript_node_count,
        face_count=transcript_face_count,
        cell_count=total_cells or transcript_cell_count,
        min_orthogonal_quality=minimum_orthogonal,
        max_equivolume_skewness=transcript_metrics["max_equivolume_skewness"],
        bad_cell_count=bad_cell_count,
        bad_cell_fraction=bad_cell_fraction,
        bad_cells_by_threshold=bad_cells_by_threshold,
        bad_cell_fraction_by_threshold=bad_cell_fraction_by_threshold,
        max_aspect_ratio=transcript_metrics["max_aspect_ratio"],
        min_expansion_ratio=transcript_metrics["min_expansion_ratio"],
        transcript_path=str(transcript_path) if transcript_path else None,
        notes=notes,
    )


def compare_metrics(baseline: MeshMetrics, current: MeshMetrics) -> tuple[TrialDelta, list[str]]:
    delta = TrialDelta()
    improved: list[str] = []

    if baseline.cell_count is not None and current.cell_count is not None:
        delta.cell_count = current.cell_count - baseline.cell_count

    if (
        baseline.min_orthogonal_quality is not None
        and current.min_orthogonal_quality is not None
    ):
        delta.min_orthogonal_quality = (
            current.min_orthogonal_quality - baseline.min_orthogonal_quality
        )
        if current.min_orthogonal_quality > baseline.min_orthogonal_quality:
            improved.append("min_orthogonal_quality")

    if (
        baseline.max_equivolume_skewness is not None
        and current.max_equivolume_skewness is not None
    ):
        delta.max_equivolume_skewness = (
            current.max_equivolume_skewness - baseline.max_equivolume_skewness
        )
        if current.max_equivolume_skewness < baseline.max_equivolume_skewness:
            improved.append("max_equivolume_skewness")

    if baseline.bad_cell_fraction is not None and current.bad_cell_fraction is not None:
        delta.bad_cell_fraction = current.bad_cell_fraction - baseline.bad_cell_fraction
        if current.bad_cell_fraction < baseline.bad_cell_fraction:
            improved.append("bad_cell_fraction")

    return delta, improved


def evaluate_quality_gates(
    *,
    baseline: MeshMetrics,
    current: MeshMetrics,
    min_orthogonal_floor: float = 0.03,
    max_equivolume_skewness_cap: float = 0.97,
    max_bad_cell_fraction_caps: Mapping[str, float] | None = None,
    relative_tolerance: float = 0.0,
) -> QualityGateResult:
    acceptable: list[str] = []
    improved: list[str] = []
    failed: list[str] = []
    if max_bad_cell_fraction_caps is None:
        max_bad_cell_fraction_caps = {"0.15": 0.001, "0.10": 0.0005, "0.05": 0.0001}

    if current.min_orthogonal_quality is not None:
        baseline_limit = (
            baseline.min_orthogonal_quality - relative_tolerance
            if baseline.min_orthogonal_quality is not None
            else None
        )
        threshold = max(
            value for value in [min_orthogonal_floor, baseline_limit] if value is not None
        )
        if current.min_orthogonal_quality >= threshold:
            acceptable.append("min_orthogonal_quality")
        else:
            failed.append("min_orthogonal_quality")
        if (
            baseline.min_orthogonal_quality is not None
            and current.min_orthogonal_quality > baseline.min_orthogonal_quality
        ):
            improved.append("min_orthogonal_quality")

    if current.max_equivolume_skewness is not None:
        baseline_limit = (
            baseline.max_equivolume_skewness + relative_tolerance
            if baseline.max_equivolume_skewness is not None
            else None
        )
        threshold = min(
            value for value in [max_equivolume_skewness_cap, baseline_limit] if value is not None
        )
        if current.max_equivolume_skewness <= threshold:
            acceptable.append("max_equivolume_skewness")
        else:
            failed.append("max_equivolume_skewness")
        if (
            baseline.max_equivolume_skewness is not None
            and current.max_equivolume_skewness < baseline.max_equivolume_skewness
        ):
            improved.append("max_equivolume_skewness")

    for threshold_key, cap in max_bad_cell_fraction_caps.items():
        current_fraction = current.bad_cell_fraction_by_threshold.get(threshold_key)
        baseline_fraction = baseline.bad_cell_fraction_by_threshold.get(threshold_key)
        metric_name = f"bad_cell_fraction_{threshold_key}"
        if current_fraction is None:
            continue
        baseline_limit = (
            baseline_fraction + relative_tolerance
            if baseline_fraction is not None
            else None
        )
        threshold = min(
            value for value in [cap, baseline_limit] if value is not None
        )
        if current_fraction <= threshold:
            acceptable.append(metric_name)
        else:
            failed.append(metric_name)
        if baseline_fraction is not None and current_fraction < baseline_fraction:
            improved.append(metric_name)

    return QualityGateResult(
        acceptable_metrics=acceptable,
        improved_metrics=sorted(set(improved)),
        failed_metrics=failed,
        acceptable=not failed,
    )


def assess_trial(
    *,
    baseline: MeshMetrics,
    current: MeshMetrics,
    zone_preservation: ZonePreservation | None,
    cell_cap: int,
) -> tuple[TrialDelta, TrialAssessment]:
    delta, improved = compare_metrics(baseline, current)
    under_cell_cap = current.cell_count is not None and current.cell_count <= cell_cap
    zone_ok = zone_preservation.preserved if zone_preservation is not None else False
    success = under_cell_cap and zone_ok and len(improved) >= 2
    return delta, TrialAssessment(
        improved_metrics=improved,
        under_cell_cap=under_cell_cap,
        zone_preservation_ok=zone_ok,
        success=success,
    )


def read_artifact_in_solver(session, artifact_path: Path, artifact_type: str) -> None:
    if artifact_type == "case":
        session.settings.file.read_case(file_name=str(artifact_path))
        return
    if artifact_type == "mesh":
        session.settings.file.read_mesh(file_name=str(artifact_path))
        return
    raise RuntimeError(f"Unsupported solver artifact type: {artifact_type}")


def read_artifact_in_meshing(session, artifact_path: Path, artifact_type: str) -> None:
    quoted_path = '"' + str(artifact_path) + '"'
    if artifact_type == "case":
        session.tui.file.read_case(quoted_path)
        return
    if artifact_type == "mesh":
        session.tui.file.read_mesh(quoted_path)
        return
    raise RuntimeError(f"Unsupported meshing artifact type: {artifact_type}")


def write_trial_outputs(
    session,
    case_path: Path | None,
    mesh_path: Path | None,
    *,
    notes: list[str] | None = None,
) -> tuple[str | None, str | None]:
    notes = notes if notes is not None else []
    case_value = None
    mesh_value = None
    if case_path is not None:
        try:
            session.tui.file.write_case('"' + str(case_path) + '"')
            case_value = str(case_path)
        except Exception as exc:
            notes.append(f"Case write failed: {type(exc).__name__}: {exc}")
    if mesh_path is not None:
        try:
            session.tui.file.write_mesh('"' + str(mesh_path) + '"')
            mesh_value = str(mesh_path)
        except Exception as exc:
            notes.append(f"Mesh write failed: {type(exc).__name__}: {exc}")
    return case_value, mesh_value


def blocked_trial_report(
    *,
    name: str,
    mode: str,
    input_artifact: Path,
    input_artifact_type: str,
    notes: list[str],
) -> TrialReport:
    return TrialReport(
        name=name,
        mode=mode,
        status="blocked",
        input_artifact=str(input_artifact),
        input_artifact_type=input_artifact_type,
        output_case=None,
        output_mesh=None,
        zone_inventory=None,
        zone_preservation=None,
        metrics=None,
        delta_vs_baseline=None,
        assessment=None,
        notes=notes,
    )


def serialize_report(report: TrialReport) -> dict[str, Any]:
    return asdict(report)


def default_geometry_trials() -> list[dict[str, Any]]:
    return [
        {
            "name": "watertight-coarse-poly",
            "surface_max_size": 120.0,
            "volume_fill": "poly",
            "hex_max_cell_length": None,
        },
        {
            "name": "watertight-tighter-poly",
            "surface_max_size": 80.0,
            "volume_fill": "poly",
            "hex_max_cell_length": None,
        },
        {
            "name": "watertight-poly-hexcore",
            "surface_max_size": 80.0,
            "volume_fill": "poly-hexcore",
            "hex_max_cell_length": 120.0,
        },
    ]


def launch_meshing_session(
    *,
    output_dir: Path,
    processor_count: int,
    dimension: int,
    start_transcript: bool,
    retries: int = 2,
):
    if pyfluent is None:
        raise ModuleNotFoundError(
            "ansys.fluent.core is required for meshing-session launches. "
            "Install PyFluent or run this command inside the prepared PyAnsys environment."
        )
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return pyfluent.Meshing.from_install(
                precision="double",
                processor_count=processor_count,
                dimension=dimension,
                start_transcript=start_transcript,
                cwd=output_dir,
            )
        except Exception as exc:
            last_error = exc
            if attempt >= retries:
                raise
            time.sleep(3)
    if last_error is not None:
        raise last_error
    raise RuntimeError("Failed to launch meshing session.")


def audit_artifact_in_meshing(
    *,
    artifact_path: Path,
    artifact_type: str,
    output_dir: Path,
    processor_count: int,
    dimension: int,
    bad_quality_threshold: float,
    trial_name: str,
) -> tuple[ZoneInventory, MeshMetrics]:
    existing_transcripts = {str(path) for path in output_dir.glob("fluent-*.trn")}
    session = launch_meshing_session(
        output_dir=output_dir,
        processor_count=processor_count,
        dimension=dimension,
        start_transcript=True,
    )
    try:
        transcript_path = latest_transcript_after(output_dir, existing_transcripts)
        read_artifact_in_meshing(session, artifact_path, artifact_type)
        metrics = collect_mesh_metrics_from_meshing(
            session,
            transcript_path=transcript_path,
            bad_quality_threshold=bad_quality_threshold,
        )
        try:
            inventory = collect_zone_inventory_from_meshing(
                session,
                output_dir=output_dir,
                trial_name=trial_name,
            )
        except Exception as exc:
            inventory = empty_zone_inventory()
            metrics.notes.append(
                f"Zone inventory unavailable in meshing mode: {type(exc).__name__}: {exc}"
            )
        return inventory, metrics
    finally:
        session.exit()


def run_geometry_trial(
    *,
    geometry_path: Path,
    output_dir: Path,
    trial_name: str,
    surface_max_size: float,
    volume_fill: str,
    hex_max_cell_length: float | None,
    processor_count: int,
    dimension: int,
    bad_quality_threshold: float,
) -> tuple[ZoneInventory, MeshMetrics, Path | None, Path | None]:
    existing_transcripts = {str(path) for path in output_dir.glob("fluent-*.trn")}
    session = launch_meshing_session(
        output_dir=output_dir,
        processor_count=processor_count,
        dimension=dimension,
        start_transcript=True,
    )
    try:
        transcript_path = latest_transcript_after(output_dir, existing_transcripts)
        watertight = session.watertight()
        import_geometry = watertight.import_geometry
        import_geometry.file_name.set_state(str(geometry_path))
        import_geometry.length_unit.set_state("mm")
        import_geometry()

        create_surface_mesh = watertight.create_surface_mesh
        create_surface_mesh.cfd_surface_mesh_controls.max_size = surface_max_size
        create_surface_mesh()

        describe_geometry = watertight.describe_geometry
        describe_geometry.update_child_tasks(setup_type_changed=False)
        describe_geometry.setup_type = "fluid"
        describe_geometry.update_child_tasks(setup_type_changed=True)
        describe_geometry()
        watertight.update_regions()

        create_volume_mesh = watertight.create_volume_mesh_wtm
        create_volume_mesh.volume_fill.set_state(volume_fill)
        if volume_fill == "poly-hexcore" and hex_max_cell_length is not None:
            create_volume_mesh.volume_fill_controls.hex_max_cell_length.set_state(
                hex_max_cell_length
            )
        create_volume_mesh()

        metrics = collect_mesh_metrics_from_meshing(
            session,
            transcript_path=transcript_path,
            bad_quality_threshold=bad_quality_threshold,
        )
        inventory = collect_zone_inventory_from_meshing(
            session,
            output_dir=output_dir,
            trial_name=trial_name,
        )

        output_case = output_dir / f"{trial_name}.cas.h5"
        output_mesh = output_dir / f"{trial_name}.msh"
        output_case_value, output_mesh_value = write_trial_outputs(
            session,
            output_case,
            output_mesh,
            notes=metrics.notes,
        )
        return (
            inventory,
            metrics,
            Path(output_case_value) if output_case_value else None,
            Path(output_mesh_value) if output_mesh_value else None,
        )
    finally:
        session.exit()


def run_mesh_salvage_trial(
    *,
    artifact_path: Path,
    artifact_type: str,
    output_dir: Path,
    trial_name: str,
    processor_count: int,
    dimension: int,
    bad_quality_threshold: float,
) -> tuple[ZoneInventory, MeshMetrics, Path | None, Path | None]:
    existing_transcripts = {str(path) for path in output_dir.glob("fluent-*.trn")}
    session = launch_meshing_session(
        output_dir=output_dir,
        processor_count=processor_count,
        dimension=dimension,
        start_transcript=True,
    )
    try:
        transcript_path = latest_transcript_after(output_dir, existing_transcripts)
        read_artifact_in_meshing(session, artifact_path, artifact_type)
        session.tui.mesh.clear_mesh()
        session.tui.mesh.auto_mesh()

        metrics = collect_mesh_metrics_from_meshing(
            session,
            transcript_path=transcript_path,
            bad_quality_threshold=bad_quality_threshold,
        )
        metrics.notes.append(
            "Mesh-only salvage used clear_mesh() plus auto_mesh() with Fluent defaults."
        )
        inventory = collect_zone_inventory_from_meshing(
            session,
            output_dir=output_dir,
            trial_name=trial_name,
        )

        output_case = output_dir / f"{trial_name}.cas.h5"
        output_mesh = output_dir / f"{trial_name}.msh"
        output_case_value, output_mesh_value = write_trial_outputs(
            session,
            output_case,
            output_mesh,
            notes=metrics.notes,
        )
        return (
            inventory,
            metrics,
            Path(output_case_value) if output_case_value else None,
            Path(output_mesh_value) if output_mesh_value else None,
        )
    finally:
        session.exit()


def build_baseline_trial_report(
    *,
    artifact_path: Path,
    artifact_type: str,
    zone_inventory: ZoneInventory,
    metrics: MeshMetrics,
) -> TrialReport:
    return TrialReport(
        name="baseline-reopen",
        mode="artifact-reopen",
        status="completed",
        input_artifact=str(artifact_path),
        input_artifact_type=artifact_type,
        output_case=None,
        output_mesh=None,
        zone_inventory=zone_inventory,
        zone_preservation=ZonePreservation(
            mode="exact",
            preserved=True,
            missing_boundaries=[],
            added_boundaries=[],
            wrong_boundary_type={},
            missing_cell_zones=[],
            added_cell_zones=[],
        ),
        metrics=metrics,
        delta_vs_baseline=TrialDelta(
            cell_count=0,
            min_orthogonal_quality=0.0,
            max_equivolume_skewness=0.0,
            bad_cell_fraction=0.0,
        ),
        assessment=TrialAssessment(
            improved_metrics=[],
            under_cell_cap=metrics.cell_count is not None and metrics.cell_count <= DEFAULT_CELL_CAP,
            zone_preservation_ok=True,
            success=False,
        ),
        notes=["Baseline reopen only. No mesh changes applied."],
    )
