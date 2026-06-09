#!/usr/bin/env python3
"""Semi-automated mesh improvement workflow for Workbench `.meshdat` inputs."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from mesh_trial_harness_lib import (
    DEFAULT_BAD_QUALITY_THRESHOLD,
    MeshMetrics,
    RequiredZoneContract,
    ZoneInventory,
    audit_artifact_in_meshing,
    compare_metrics,
    compare_zone_inventories,
    detect_artifact_type,
    evaluate_quality_gates,
    json_write,
    load_required_zone_contract,
    validate_required_zones,
    write_required_zones_template,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a semi-automated mesh improvement workflow around a Workbench "
            ".meshdat plus a baseline Fluent mesh."
        )
    )
    parser.add_argument("--meshdat", required=True, help="Workbench `.meshdat` file.")
    parser.add_argument(
        "--baseline-mesh",
        required=True,
        help="Baseline Fluent `.msh` or `.msh.h5` exported from the same setup.",
    )
    parser.add_argument(
        "--required-zones",
        default="",
        help="Optional text file listing required boundary and cell zones.",
    )
    parser.add_argument(
        "--output-dir",
        default="output/mesh_improvement_workflow",
        help="Directory for JSON and Markdown workflow artifacts.",
    )
    parser.add_argument(
        "--cell-target",
        type=int,
        default=None,
        help="Optional diagnostic cell target. Not used as a primary pass/fail rule.",
    )
    parser.add_argument(
        "--bad-quality-threshold",
        type=float,
        default=DEFAULT_BAD_QUALITY_THRESHOLD,
        help="Orthogonal quality threshold used to count bad cells.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=1,
        help="Requested Fluent processor count for reopen audits.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=(2, 3),
        default=3,
        help="Fluent dimension for reopen audits.",
    )
    parser.add_argument(
        "--trial-mesh",
        action="append",
        default=[],
        help="Exported trial mesh in the form `trial-name=path-to-msh-or-msh.h5`.",
    )
    parser.add_argument(
        "--write-observed-zones-template",
        action="store_true",
        help="Write a baseline-observed required-zones template when no contract is supplied.",
    )
    return parser


def default_conservative_trials() -> list[dict[str, object]]:
    return [
        {
            "name": "trial-01-coarser-global-size",
            "intent": "Reduce unnecessary density without making cell count the primary target.",
            "change_type": "global-size",
            "operator_changes": [
                "Increase the global element size or relevance center by about 10 to 15 percent.",
                "Do not touch named selections, body suppression, or topology cleanup settings.",
                "Keep all method assignments identical to the baseline mesh branch.",
            ],
        },
        {
            "name": "trial-02-local-inlet-spiral-refine",
            "intent": "Recover quality near the inlet and spiral while still allowing a coarser global field.",
            "change_type": "local-refinement",
            "operator_changes": [
                "Start from Trial 01 settings.",
                "Apply inlet-region local sizing consistently to both `liquid-inlet` and `steam-inlet` unless deliberately testing something else later.",
                "Add only local face or body sizing near the inlet split edge and spiral region at about 10 to 15 percent finer than the surrounding field.",
                "Do not create new scoping selections; reuse only existing selectable entities.",
            ],
        },
        {
            "name": "trial-03-adjust-growth-rate",
            "intent": "Reduce abrupt size jumps without materially changing the geometry definition.",
            "change_type": "growth-rate",
            "operator_changes": [
                "Start from Trial 02 settings.",
                "Make the growth rate slightly smoother, for example one conservative notch lower than the baseline.",
                "Leave proximity and curvature capture logic unchanged unless they were already active in the baseline branch.",
            ],
        },
        {
            "name": "trial-04-smoother-transition",
            "intent": "Improve transition quality around refined zones while staying conservative on total-cell growth.",
            "change_type": "transition",
            "operator_changes": [
                "Start from Trial 03 settings.",
                "Prefer slower or smoother transition behavior if that control is available in the active meshing method.",
                "Do not switch mesh method families unless the baseline branch already uses multiple compatible methods.",
            ],
        },
        {
            "name": "trial-05-mild-inflation-if-stable",
            "intent": "Try a mild wall treatment only after earlier trials reopen cleanly.",
            "change_type": "inflation",
            "operator_changes": [
                "Apply only if Trials 01 to 04 generate and export successfully.",
                "Use a mild inflation setup such as a small number of layers and gentle growth.",
                "Abort this trial if inflation introduces collapses, negative volume warnings, or worse reopen behavior.",
            ],
        },
    ]


def parse_trial_mesh_entry(entry: str) -> tuple[str, Path]:
    if "=" not in entry:
        raise ValueError(
            f"Trial mesh must be supplied as `trial-name=path`, got: {entry!r}"
        )
    name, path_text = entry.split("=", 1)
    name = name.strip()
    path = Path(path_text.strip()).expanduser().resolve()
    if not name:
        raise ValueError(f"Trial mesh name is empty in entry: {entry!r}")
    if not path.exists():
        raise FileNotFoundError(f"Trial mesh does not exist: {path}")
    kind = detect_artifact_type(path)
    if kind != "mesh":
        raise ValueError(f"Trial artifact must be a mesh file, got {kind}: {path}")
    return name, path


def metrics_to_summary(metrics: MeshMetrics) -> dict[str, object]:
    return {
        "node_count": metrics.node_count,
        "face_count": metrics.face_count,
        "cell_count": metrics.cell_count,
        "min_orthogonal_quality": metrics.min_orthogonal_quality,
        "max_equivolume_skewness": metrics.max_equivolume_skewness,
        "bad_cell_fraction": metrics.bad_cell_fraction,
        "bad_cells_by_threshold": metrics.bad_cells_by_threshold,
        "bad_cell_fraction_by_threshold": metrics.bad_cell_fraction_by_threshold,
        "max_aspect_ratio": metrics.max_aspect_ratio,
        "min_expansion_ratio": metrics.min_expansion_ratio,
        "notes": metrics.notes,
    }


def inventory_to_summary(inventory: ZoneInventory) -> dict[str, object]:
    return {
        "boundary_zones": inventory.boundary_flat,
        "boundary_zone_types": inventory.boundary_by_type,
        "cell_zones": inventory.cell_zone_names,
    }


def split_inlet_contract() -> RequiredZoneContract:
    return RequiredZoneContract(
        boundary_zones=[
            "bottom",
            "liquid-inlet",
            "outlet",
            "steam-inlet",
            "wall",
            "wall-smooth_spiral_separator",
        ],
        boundary_zone_types={
            "liquid-inlet": "velocity-inlet",
            "steam-inlet": "velocity-inlet",
            "outlet": "pressure-outlet",
            "bottom": "wall",
            "wall": "wall",
            "wall-smooth_spiral_separator": "wall",
        },
        cell_zones=["smooth_spiral_separator"],
        source_path=None,
    )


def default_manual_review() -> dict[str, str]:
    return {
        "inlet_split_edge": "pending manual review",
        "spiral_wall_and_vessel_blend": "pending manual review",
        "outlet_region": "pending manual review",
        "bottom_region": "pending manual review",
        "overall_suitability_for_fluent": "pending manual review",
    }


def write_markdown_report(
    *,
    path: Path,
    meshdat_path: Path,
    baseline_path: Path,
    required_zone_path: str | None,
    cell_target: int | None,
    required_contract: RequiredZoneContract,
    baseline_inventory: ZoneInventory,
    baseline_metrics: MeshMetrics,
    baseline_required_check: dict[str, object],
    meshdat_inventory: ZoneInventory,
    meshdat_metrics: MeshMetrics,
    planned_trials: list[dict[str, object]],
    trial_results: list[dict[str, object]],
) -> None:
    lines = [
        "# Semi-Automated Mesh Improvement Workflow",
        "",
        "## Inputs",
        f"- `.meshdat`: `{meshdat_path}`",
        f"- Baseline mesh: `{baseline_path}`",
        f"- Required zones file: `{required_zone_path or 'not supplied'}`",
        f"- Cell target: `{cell_target if cell_target is not None else 'diagnostic only / not enforced'}`",
        "",
        "## Required zone contract",
    ]
    for name in required_contract.boundary_zones:
        expected_type = required_contract.boundary_zone_types.get(name, "unspecified")
        lines.append(f"- Boundary: `{name}` | expected Fluent type `{expected_type}`")
    for name in required_contract.cell_zones:
        lines.append(f"- Cell zone: `{name}`")
    lines.extend([
        "",
        "## Baseline audit",
        f"- Baseline boundary zones: `{', '.join(baseline_inventory.boundary_flat) or 'none detected'}`",
        f"- Baseline cell zones: `{', '.join(baseline_inventory.cell_zone_names) or 'none detected'}`",
        f"- Baseline nodes: `{baseline_metrics.node_count}`",
        f"- Baseline faces: `{baseline_metrics.face_count}`",
        f"- Baseline cells: `{baseline_metrics.cell_count}`",
        f"- Baseline min orthogonal quality: `{baseline_metrics.min_orthogonal_quality}`",
        f"- Baseline max equivolume skewness: `{baseline_metrics.max_equivolume_skewness}`",
        f"- Baseline bad-cell fraction <= 0.15: `{baseline_metrics.bad_cell_fraction_by_threshold.get('0.15')}`",
        f"- Baseline bad-cell fraction <= 0.10: `{baseline_metrics.bad_cell_fraction_by_threshold.get('0.10')}`",
        f"- Baseline bad-cell fraction <= 0.05: `{baseline_metrics.bad_cell_fraction_by_threshold.get('0.05')}`",
        f"- Baseline required-zone contract satisfied: `{baseline_required_check['all_present']}`",
        f"- Baseline missing required boundaries: `{baseline_required_check['missing_boundary_zones']}`",
        f"- Baseline wrong boundary types: `{baseline_required_check['wrong_boundary_type']}`",
        f"- Baseline missing required cell zones: `{baseline_required_check['missing_cell_zones']}`",
        "- Zone preservation note: boundary-zone differences are warnings only for this workflow stage.",
        "",
        "## `.meshdat` diagnostic reopen",
        f"- `.meshdat` boundary zones: `{', '.join(meshdat_inventory.boundary_flat) or 'not available from meshing reopen'}`",
        f"- `.meshdat` cell zones: `{', '.join(meshdat_inventory.cell_zone_names) or 'not available from meshing reopen'}`",
        f"- `.meshdat` nodes: `{meshdat_metrics.node_count}`",
        f"- `.meshdat` faces: `{meshdat_metrics.face_count}`",
        f"- `.meshdat` cells: `{meshdat_metrics.cell_count}`",
        "",
        "## Conservative trial plan",
    ])
    for trial in planned_trials:
        lines.append(f"### {trial['name']}")
        lines.append(f"- Intent: {trial['intent']}")
        for change in trial["operator_changes"]:
            lines.append(f"- {change}")
        lines.append("")

    lines.extend(
        [
            "## Trial validation results",
            "",
        ]
    )
    if not trial_results:
        lines.append("- No exported trial meshes were supplied yet. Use the planned trials above, export each `.msh.h5`, then rerun this command with `--trial-mesh` entries.")
    else:
        for result in trial_results:
            lines.append(f"### {result['name']}")
            lines.append(f"- Reopened in Fluent: `{result['reopened_in_fluent']}`")
            lines.append(f"- Required zones preserved: `{result['required_zones_ok']}`")
            lines.append(f"- Zone preservation warning only: `{result['zone_preservation_warning']}`")
            lines.append(f"- Missing required boundaries: `{result['required_zone_check']['missing_boundary_zones']}`")
            lines.append(f"- Wrong boundary types: `{result['required_zone_check']['wrong_boundary_type']}`")
            lines.append(f"- Missing required cell zones: `{result['required_zone_check']['missing_cell_zones']}`")
            lines.append(f"- Exact baseline zone preservation: `{result['zone_preservation_ok']}`")
            lines.append(f"- Node / face / cell counts: `{result['metrics']['node_count']}` / `{result['metrics']['face_count']}` / `{result['metrics']['cell_count']}`")
            lines.append(f"- Diagnostic cell target check: `{result['under_cell_target']}`")
            lines.append(f"- Quality gate acceptable: `{result['quality_gate']['acceptable']}`")
            lines.append(f"- Improved metrics: `{', '.join(result['quality_gate']['improved_metrics']) or 'none'}`")
            lines.append(f"- Bad-cell fraction <= 0.15: `{result['metrics']['bad_cell_fraction_by_threshold'].get('0.15')}`")
            lines.append(f"- Bad-cell fraction <= 0.10: `{result['metrics']['bad_cell_fraction_by_threshold'].get('0.10')}`")
            lines.append(f"- Bad-cell fraction <= 0.05: `{result['metrics']['bad_cell_fraction_by_threshold'].get('0.05')}`")
            lines.append(f"- Local manual review: `{result['manual_review']}`")
            lines.append(f"- Successful trial: `{result['success']}`")
            if result["notes"]:
                for note in result["notes"]:
                    lines.append(f"- Note: {note}")
            lines.append("")

    lines.extend(
        [
            "## Comparison table",
            "",
            "| Mesh | Reopen | Zones ok | Min orth | Max equiv skew | Bad<=0.15 | Bad<=0.10 | Bad<=0.05 | Nodes | Faces | Cells | Overall local review |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            f"| baseline | yes | {str(baseline_required_check['all_present']).lower()} (warning only) | {baseline_metrics.min_orthogonal_quality} | {baseline_metrics.max_equivolume_skewness} | {baseline_metrics.bad_cell_fraction_by_threshold.get('0.15')} | {baseline_metrics.bad_cell_fraction_by_threshold.get('0.10')} | {baseline_metrics.bad_cell_fraction_by_threshold.get('0.05')} | {baseline_metrics.node_count} | {baseline_metrics.face_count} | {baseline_metrics.cell_count} | baseline reference |",
        ]
    )
    for result in trial_results:
        lines.append(
            f"| {result['name']} | {str(result['reopened_in_fluent']).lower()} | {str(result['required_zones_ok'] and result['zone_preservation_ok']).lower()} | {result['metrics']['min_orthogonal_quality']} | {result['metrics']['max_equivolume_skewness']} | {result['metrics']['bad_cell_fraction_by_threshold'].get('0.15')} | {result['metrics']['bad_cell_fraction_by_threshold'].get('0.10')} | {result['metrics']['bad_cell_fraction_by_threshold'].get('0.05')} | {result['metrics']['node_count']} | {result['metrics']['face_count']} | {result['metrics']['cell_count']} | {result['manual_review']['overall_suitability_for_fluent']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    meshdat_path = Path(args.meshdat).expanduser().resolve()
    baseline_path = Path(args.baseline_mesh).expanduser().resolve()
    if not meshdat_path.exists():
        raise FileNotFoundError(f"`.meshdat` input does not exist: {meshdat_path}")
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline mesh does not exist: {baseline_path}")

    if detect_artifact_type(meshdat_path) != "mesh" or meshdat_path.suffix.lower() != ".meshdat":
        raise ValueError(f"Expected a `.meshdat` file, got: {meshdat_path}")
    if detect_artifact_type(baseline_path) != "mesh":
        raise ValueError(f"Expected a Fluent mesh file, got: {baseline_path}")

    required_zone_path = Path(args.required_zones).expanduser().resolve() if args.required_zones.strip() else None
    if required_zone_path is not None and not required_zone_path.exists():
        raise FileNotFoundError(f"Required zones file does not exist: {required_zone_path}")

    baseline_inventory, baseline_metrics = audit_artifact_in_meshing(
        artifact_path=baseline_path,
        artifact_type="mesh",
        output_dir=output_dir,
        processor_count=args.processor_count,
        dimension=args.dimension,
        bad_quality_threshold=args.bad_quality_threshold,
        trial_name="baseline-audit",
    )
    meshdat_inventory, meshdat_metrics = audit_artifact_in_meshing(
        artifact_path=meshdat_path,
        artifact_type="mesh",
        output_dir=output_dir,
        processor_count=args.processor_count,
        dimension=args.dimension,
        bad_quality_threshold=args.bad_quality_threshold,
        trial_name="meshdat-audit",
    )

    if required_zone_path is not None:
        required_contract = load_required_zone_contract(required_zone_path)
    else:
        required_contract = split_inlet_contract()

    if required_zone_path is None and args.write_observed_zones_template:
        write_required_zones_template(output_dir / "required-zones-template.txt", baseline_inventory)

    baseline_required = validate_required_zones(baseline_inventory, required_contract)
    meshdat_required = validate_required_zones(meshdat_inventory, required_contract)
    planned_trials = default_conservative_trials()

    trial_results: list[dict[str, object]] = []
    for entry in args.trial_mesh:
        name, path = parse_trial_mesh_entry(entry)
        notes: list[str] = []
        inventory, metrics = audit_artifact_in_meshing(
            artifact_path=path,
            artifact_type="mesh",
            output_dir=output_dir,
            processor_count=args.processor_count,
            dimension=args.dimension,
            bad_quality_threshold=args.bad_quality_threshold,
            trial_name=name,
        )
        zone_preservation = compare_zone_inventories(baseline_inventory, inventory, "exact")
        required_check = validate_required_zones(inventory, required_contract)
        delta, improved_metrics = compare_metrics(baseline_metrics, metrics)
        quality_gate = evaluate_quality_gates(baseline=baseline_metrics, current=metrics)
        under_cell_target = (
            metrics.cell_count is not None and metrics.cell_count <= args.cell_target
            if args.cell_target is not None
            else None
        )
        if metrics.notes:
            notes.extend(metrics.notes)
        notes.append(
            "Zone preservation differences are treated as warnings only in this workflow stage."
        )
        if required_zone_path is None:
            notes.append("No external required-zones file was supplied; the built-in split-inlet contract was used.")

        success = quality_gate.acceptable
        trial_results.append(
            {
                "name": name,
                "path": str(path),
                "reopened_in_fluent": True,
                "required_zones_ok": required_check.all_present,
                "zone_preservation_warning": not zone_preservation.preserved,
                "required_zone_check": asdict(required_check),
                "zone_preservation_ok": zone_preservation.preserved,
                "zone_preservation": asdict(zone_preservation),
                "under_cell_target": under_cell_target,
                "quality_gate": asdict(quality_gate),
                "delta_vs_baseline": asdict(delta),
                "compare_metrics_improved": improved_metrics,
                "metrics": metrics_to_summary(metrics),
                "inventory": inventory_to_summary(inventory),
                "manual_review": default_manual_review(),
                "success": success,
                "notes": notes,
            }
        )

    payload = {
        "inputs": {
            "meshdat": str(meshdat_path),
            "baseline_mesh": str(baseline_path),
            "required_zones": str(required_zone_path) if required_zone_path else None,
            "cell_target": args.cell_target,
            "bad_quality_threshold": args.bad_quality_threshold,
        },
        "baseline_audit": {
            "inventory": inventory_to_summary(baseline_inventory),
            "metrics": metrics_to_summary(baseline_metrics),
            "required_zone_check": asdict(baseline_required),
        },
        "meshdat_audit": {
            "inventory": inventory_to_summary(meshdat_inventory),
            "metrics": metrics_to_summary(meshdat_metrics),
            "required_zone_check": asdict(meshdat_required),
        },
        "required_zone_contract": asdict(required_contract),
        "planned_trials": planned_trials,
        "trial_results": trial_results,
    }
    json_write(output_dir / "workflow-report.json", payload)
    write_markdown_report(
        path=output_dir / "workflow-report.md",
        meshdat_path=meshdat_path,
        baseline_path=baseline_path,
        required_zone_path=str(required_zone_path) if required_zone_path else None,
        cell_target=args.cell_target,
        required_contract=required_contract,
        baseline_inventory=baseline_inventory,
        baseline_metrics=baseline_metrics,
        baseline_required_check=asdict(baseline_required),
        meshdat_inventory=meshdat_inventory,
        meshdat_metrics=meshdat_metrics,
        planned_trials=planned_trials,
        trial_results=trial_results,
    )
    print(f"WORKFLOW_OK: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
