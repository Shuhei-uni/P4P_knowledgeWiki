#!/usr/bin/env python3
"""Run repeatable PyFluent mesh trials under a cell-count cap."""

from __future__ import annotations

import argparse
from pathlib import Path
import traceback

from mesh_trial_harness_lib import (
    DEFAULT_BAD_QUALITY_THRESHOLD,
    DEFAULT_CELL_CAP,
    DEFAULT_TRIAL_PRESET,
    TrialReport,
    assess_trial,
    blocked_trial_report,
    build_baseline_trial_report,
    collect_mesh_metrics_from_meshing,
    collect_zone_inventory_from_meshing,
    compare_zone_inventories,
    default_geometry_trials,
    empty_zone_inventory,
    json_write,
    launch_meshing_session,
    latest_transcript_after,
    read_artifact_in_meshing,
    resolve_input_artifact,
    run_geometry_trial,
    run_mesh_salvage_trial,
    serialize_report,
)
import ansys.fluent.core as pyfluent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a local PyFluent mesh trial harness on case, mesh, or geometry inputs."
    )
    parser.add_argument(
        "--input-artifact",
        required=True,
        help="Path to the primary artifact file or a directory containing candidate artifacts.",
    )
    parser.add_argument(
        "--artifact-type",
        choices=("auto", "case", "mesh", "geometry", "workflow"),
        default="auto",
        help="Artifact type hint. Default: auto.",
    )
    parser.add_argument(
        "--geometry-file",
        default="",
        help="Optional geometry path for watertight remesh trials.",
    )
    parser.add_argument(
        "--workflow-file",
        default="",
        help="Optional workflow file path. V1 records this but does not drive trial steps from it yet.",
    )
    parser.add_argument(
        "--output-dir",
        default="output/mesh_trials",
        help="Directory for reports, transcripts, and trial outputs.",
    )
    parser.add_argument(
        "--cell-cap",
        type=int,
        default=DEFAULT_CELL_CAP,
        help=f"Maximum allowed cell count. Default: {DEFAULT_CELL_CAP}.",
    )
    parser.add_argument(
        "--bad-quality-threshold",
        type=float,
        default=DEFAULT_BAD_QUALITY_THRESHOLD,
        help=(
            "Orthogonal-quality threshold used to define bad cells. "
            f"Default: {DEFAULT_BAD_QUALITY_THRESHOLD}."
        ),
    )
    parser.add_argument(
        "--zone-preservation",
        choices=("exact",),
        default="exact",
        help="Zone preservation mode. V1 supports exact only.",
    )
    parser.add_argument(
        "--trial-preset",
        default=DEFAULT_TRIAL_PRESET,
        help=f"Trial preset name. Default: {DEFAULT_TRIAL_PRESET}.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=1,
        help="Requested Fluent processor count. Default: 1.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=(2, 3),
        default=3,
        help="Fluent dimension. Default: 3.",
    )
    parser.add_argument(
        "--skip-mesh-salvage",
        action="store_true",
        help="Skip the mesh-only salvage trial even when no geometry is supplied.",
    )
    return parser


def baseline_metrics_for_artifact(
    artifact_path: Path,
    artifact_type: str,
    output_dir: Path,
    *,
    processor_count: int,
    dimension: int,
    bad_quality_threshold: float,
) -> tuple[object, object]:
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
                trial_name="baseline-reopen",
            )
        except Exception as exc:
            inventory = empty_zone_inventory()
            metrics.notes.append(
                f"Zone inventory unavailable in meshing mode: {type(exc).__name__}: {exc}"
            )
        return inventory, metrics
    finally:
        session.exit()


def save_trial(output_dir: Path, report: TrialReport) -> None:
    json_write(output_dir / f"{report.name}.json", serialize_report(report))


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        artifact_path, artifact_type = resolve_input_artifact(
            args.input_artifact,
            args.artifact_type,
        )
        if artifact_type == "unknown":
            raise RuntimeError(f"Unsupported artifact type for: {artifact_path}")

        geometry_path = Path(args.geometry_file).expanduser().resolve() if args.geometry_file.strip() else None
        if geometry_path is not None and not geometry_path.exists():
            raise FileNotFoundError(f"Geometry file does not exist: {geometry_path}")

        workflow_path = Path(args.workflow_file).expanduser().resolve() if args.workflow_file.strip() else None
        if workflow_path is not None and not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file does not exist: {workflow_path}")

        baseline_inventory, baseline_metrics = baseline_metrics_for_artifact(
            artifact_path,
            artifact_type,
            output_dir,
            processor_count=args.processor_count,
            dimension=args.dimension,
            bad_quality_threshold=args.bad_quality_threshold,
        )
        baseline_report = build_baseline_trial_report(
            artifact_path=artifact_path,
            artifact_type=artifact_type,
            zone_inventory=baseline_inventory,
            metrics=baseline_metrics,
        )
        save_trial(output_dir, baseline_report)

        reports: list[TrialReport] = [baseline_report]

        if geometry_path is not None:
            for trial in default_geometry_trials():
                trial_name = trial["name"]
                try:
                    current_inventory, metrics, output_case, output_mesh = run_geometry_trial(
                        geometry_path=geometry_path,
                        output_dir=output_dir,
                        trial_name=trial_name,
                        surface_max_size=trial["surface_max_size"],
                        volume_fill=trial["volume_fill"],
                        hex_max_cell_length=trial["hex_max_cell_length"],
                        processor_count=args.processor_count,
                        dimension=args.dimension,
                        bad_quality_threshold=args.bad_quality_threshold,
                    )
                    zone_preservation = compare_zone_inventories(
                        baseline_inventory,
                        current_inventory,
                        args.zone_preservation,
                    )
                    delta, assessment = assess_trial(
                        baseline=baseline_metrics,
                        current=metrics,
                        zone_preservation=zone_preservation,
                        cell_cap=args.cell_cap,
                    )
                    report = TrialReport(
                        name=trial_name,
                        mode="geometry-remesh",
                        status="completed",
                        input_artifact=str(geometry_path),
                        input_artifact_type="geometry",
                        output_case=str(output_case) if output_case else None,
                        output_mesh=str(output_mesh) if output_mesh else None,
                        zone_inventory=current_inventory,
                        zone_preservation=zone_preservation,
                        metrics=metrics,
                        delta_vs_baseline=delta,
                        assessment=assessment,
                        notes=[],
                    )
                except Exception as exc:
                    report = blocked_trial_report(
                        name=trial_name,
                        mode="geometry-remesh",
                        input_artifact=geometry_path,
                        input_artifact_type="geometry",
                        notes=[f"Geometry trial failed: {type(exc).__name__}: {exc}"],
                    )
                reports.append(report)
                save_trial(output_dir, report)
        else:
            reports.append(
                blocked_trial_report(
                    name="watertight-coarse-poly",
                    mode="geometry-remesh",
                    input_artifact=artifact_path,
                    input_artifact_type=artifact_type,
                    notes=["Geometry trial blocked because no geometry file was supplied."],
                )
            )
            reports.append(
                blocked_trial_report(
                    name="watertight-tighter-poly",
                    mode="geometry-remesh",
                    input_artifact=artifact_path,
                    input_artifact_type=artifact_type,
                    notes=["Geometry trial blocked because no geometry file was supplied."],
                )
            )
            reports.append(
                blocked_trial_report(
                    name="watertight-poly-hexcore",
                    mode="geometry-remesh",
                    input_artifact=artifact_path,
                    input_artifact_type=artifact_type,
                    notes=["Geometry trial blocked because no geometry file was supplied."],
                )
            )
            for report in reports[1:4]:
                save_trial(output_dir, report)

        if artifact_type in {"case", "mesh"} and not args.skip_mesh_salvage:
            try:
                current_inventory, metrics, output_case, output_mesh = run_mesh_salvage_trial(
                    artifact_path=artifact_path,
                    artifact_type=artifact_type,
                    output_dir=output_dir,
                    trial_name="mesh-salvage-auto",
                    processor_count=args.processor_count,
                    dimension=args.dimension,
                    bad_quality_threshold=args.bad_quality_threshold,
                )
                zone_preservation = compare_zone_inventories(
                    baseline_inventory,
                    current_inventory,
                    args.zone_preservation,
                )
                delta, assessment = assess_trial(
                    baseline=baseline_metrics,
                    current=metrics,
                    zone_preservation=zone_preservation,
                    cell_cap=args.cell_cap,
                )
                salvage_report = TrialReport(
                    name="mesh-salvage-auto",
                    mode="mesh-salvage",
                    status="completed",
                    input_artifact=str(artifact_path),
                    input_artifact_type=artifact_type,
                    output_case=str(output_case) if output_case else None,
                    output_mesh=str(output_mesh) if output_mesh else None,
                    zone_inventory=current_inventory,
                    zone_preservation=zone_preservation,
                    metrics=metrics,
                    delta_vs_baseline=delta,
                    assessment=assessment,
                    notes=[],
                )
            except Exception as exc:
                salvage_report = blocked_trial_report(
                    name="mesh-salvage-auto",
                    mode="mesh-salvage",
                    input_artifact=artifact_path,
                    input_artifact_type=artifact_type,
                    notes=[f"Mesh salvage failed: {type(exc).__name__}: {exc}"],
                )
            reports.append(salvage_report)
            save_trial(output_dir, salvage_report)

        if workflow_path is not None:
            workflow_report = blocked_trial_report(
                name="workflow-reload",
                mode="workflow-reload",
                input_artifact=workflow_path,
                input_artifact_type="workflow",
                notes=[
                    "Workflow file was supplied and recorded.",
                    "V1 does not yet drive trial execution from a saved .wft workflow.",
                ],
            )
            reports.append(workflow_report)
            save_trial(output_dir, workflow_report)

        summary = {
            "input_artifact": str(artifact_path),
            "input_artifact_type": artifact_type,
            "geometry_file": str(geometry_path) if geometry_path else None,
            "workflow_file": str(workflow_path) if workflow_path else None,
            "trial_preset": args.trial_preset,
            "cell_cap": args.cell_cap,
            "bad_quality_threshold": args.bad_quality_threshold,
            "zone_preservation": args.zone_preservation,
            "baseline_report": f"{baseline_report.name}.json",
            "trial_reports": [f"{report.name}.json" for report in reports],
        }
        json_write(output_dir / "summary.json", summary)
        print(f"HARNESS_OK: {output_dir}")
        return 0
    except Exception as exc:
        print(f"HARNESS_FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
