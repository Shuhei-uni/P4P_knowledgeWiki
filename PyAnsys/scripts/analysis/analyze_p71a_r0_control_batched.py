#!/usr/bin/env python3
"""Make compact, evidence-grounded plots and summary for the R0 batched run."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


RESIDUAL_RE = re.compile(
    r"^\s*(\d+)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"\d\d?:\d\d:\d\d",
    re.MULTILINE,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def series(reports: dict[str, Any], name: str) -> tuple[np.ndarray, np.ndarray]:
    item = reports[name]
    return np.asarray(item["iterations"], dtype=float), np.asarray(item["values"], dtype=float)


def parse_residuals(paths: list[Path]) -> dict[str, np.ndarray]:
    names = ["iteration", "continuity", "x-velocity", "y-velocity", "z-velocity", "k", "epsilon", "vf-phase-2"]
    rows: dict[int, tuple[float, ...]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in RESIDUAL_RE.finditer(text):
            row = tuple(float(match.group(i)) for i in range(1, 9))
            rows[int(row[0])] = row
    ordered = [rows[key] for key in sorted(rows)]
    return {name: np.asarray([row[i] for row in ordered], dtype=float) for i, name in enumerate(names)}


def style(ax: plt.Axes, title: str, xlabel: str = "Native Fluent iteration") -> None:
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(True, alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    reports = read_json(run / "report-histories-batched.json")
    transcript_inputs = [path for path in (run / "transcript.txt", run / "transcript-batched-resume.txt") if path.exists()]
    residuals = parse_residuals(transcript_inputs)
    fig_dir = run / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir = run / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    it, total_mass = series(reports, "v2-total-liquid-mass")
    _, total_volume = series(reports, "v2-total-liquid-volume")
    _, lower_mass = series(reports, "v2-lower-liquid-mass")
    _, lower_volume = series(reports, "v2-lower-liquid-volume")
    _, available = series(reports, "v2-lower-available-volume")
    _, command = series(reports, "v2-command")
    _, applied = series(reports, "v2-applied-absorber")
    _, command_error = series(reports, "v2-command-error")
    _, removal = series(reports, "v2-absorber-removal")
    _, mix_out = series(reports, "v2-flux-mixture-steamoutlet")
    _, p1_in = series(reports, "v2-flux-phase1-steaminlet")
    _, p1_out = series(reports, "v2-flux-phase1-steamoutlet")
    _, p2_in = series(reports, "v2-flux-phase2-liquidinlet")
    _, p2_out = series(reports, "v2-flux-phase2-steamoutlet")
    p1_closure = p1_in + p1_out
    p2_closure = p2_in + p2_out + applied
    mixture_closure = p1_closure + p2_closure
    storage_rate = np.gradient(total_mass, it)

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(it, total_mass, label="Total liquid mass [kg]")
    ax2 = ax.twinx()
    ax2.plot(it, total_volume, color="tab:orange", label="Total liquid volume [m³]")
    ax.set_ylabel("Mass [kg]")
    ax2.set_ylabel("Volume [m³]")
    style(ax, "R0 control: total liquid inventory")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc="best")
    save(fig, fig_dir / "01-total-liquid-inventory.png")

    fig, axes = plt.subplots(2, 1, figsize=(8.5, 7.2), sharex=True)
    axes[0].plot(it, total_mass, color="tab:blue", label="Total liquid mass")
    axes[0].set_ylabel("Mass [kg]")
    style(axes[0], "Total liquid inventory")
    axes[0].legend(loc="best")
    top_volume = axes[0].twinx()
    top_volume.plot(it, total_volume, color="tab:orange", label="Total liquid volume")
    top_volume.set_ylabel("Volume [m³]")
    top_volume.spines["top"].set_visible(False)
    axes[1].plot(it, lower_mass, color="tab:green", label="Lower-zone liquid mass")
    axes[1].set_ylabel("Mass [kg]")
    style(axes[1], "Lower-zone liquid inventory")
    lower_volume_axis = axes[1].twinx()
    lower_volume_axis.plot(it, lower_volume, color="tab:red", label="Lower-zone liquid volume")
    lower_volume_axis.set_ylabel("Volume [m³]")
    lower_volume_axis.spines["top"].set_visible(False)
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = lower_volume_axis.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc="best")
    save(fig, fig_dir / "07-liquid-inventory-dedicated.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(it, command, label="Command")
    ax.plot(it, removal, label="Absorber removal (+)")
    ax.plot(it, -applied, "--", label="Applied source magnitude")
    ax.set_ylabel("kg/s")
    style(ax, "R0 control: absorber command and applied source")
    ax.legend(loc="best")
    ax2 = ax.twinx()
    ax2.plot(it, command_error, color="tab:red", alpha=0.75, label="Command error")
    ax2.set_ylabel("Command error [kg/s]")
    ax2.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
    save(fig, fig_dir / "02-command-absorber-error.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(it, lower_mass, label="Lower liquid mass [kg]")
    ax.plot(it, lower_volume, label="Lower liquid volume [m³]")
    ax.plot(it, available, "--", label="Available lower volume [m³]")
    ax.set_ylabel("Reported value")
    style(ax, "R0 control: lower-zone availability and inventory")
    ax.legend(loc="best")
    save(fig, fig_dir / "03-lower-zone-availability.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(it, p1_in, label="Phase 1 inlet")
    ax.plot(it, p1_out, label="Phase 1 steam outlet")
    ax.plot(it, p2_in, label="Phase 2 liquid inlet")
    ax.plot(it, p2_out, label="Phase 2 steam outlet")
    ax.plot(it, mix_out, "k--", label="Mixture steam outlet")
    ax.set_ylabel("Signed mass flux [kg/s]")
    style(ax, "R0 control: phase-resolved fluxes")
    ax.legend(ncol=2, loc="best")
    save(fig, fig_dir / "04-phase-fluxes.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(it, p1_closure, label="Phase 1 boundary closure")
    ax.plot(it, p2_closure, label="Phase 2 + absorber closure")
    ax.plot(it, mixture_closure, label="Mixture boundary + source closure")
    ax.plot(it, storage_rate, "k--", alpha=0.8, label="d(total liquid mass)/d iteration")
    ax.axhline(0.0, color="0.3", linewidth=0.8)
    ax.set_ylabel("kg/s, or kg/iteration for storage")
    style(ax, "R0 control: source-inclusive closure and storage diagnostic")
    ax.legend(ncol=2, loc="best")
    save(fig, fig_dir / "05-source-inclusive-closure.png")

    fig, axes = plt.subplots(2, 1, figsize=(8.5, 7.0), sharex=True)
    for name in ("continuity", "x-velocity", "y-velocity", "z-velocity", "k", "epsilon", "vf-phase-2"):
        axes[0].semilogy(residuals["iteration"], residuals[name], label=name)
    style(axes[0], "R0 control: residual history")
    axes[0].set_ylabel("Residual")
    axes[0].legend(ncol=3, fontsize=8)
    axes[1].plot(residuals["iteration"], residuals["continuity"], label="Continuity")
    axes[1].plot(residuals["iteration"], residuals["vf-phase-2"], label="VOF phase 2")
    axes[1].set_ylabel("Residual")
    axes[1].legend(loc="best")
    style(axes[1], "Linear view of dominant residuals")
    save(fig, fig_dir / "06-residual-health.png")

    checkpoints = []
    for offset in (250, 500, 750, 1000):
        payload = read_json(run / f"checkpoint-plus{offset:04d}-batched-readback.json")
        checkpoints.append({
            "additional_offset": offset,
            "native_expected_coordinate": payload.get("native_expected_coordinate"),
            "native_observed_tail": re.findall(r"\n\s*(\d+)\s+", payload.get("console_tail", ""))[-1:] or [None],
            "total_liquid_mass_kg": payload.get("total_liquid_mass_kg"),
            "total_liquid_volume_m3": payload.get("total_liquid_volume_m3"),
            "lower_liquid_mass_kg": payload.get("lower_liquid_mass_kg"),
            "lower_liquid_volume_m3": payload.get("lower_liquid_volume_m3"),
            "command_kg_s": payload.get("command_kg_s"),
            "command_error_kg_s": payload.get("command_error_kg_s"),
            "event_flags": payload.get("console_event_flags"),
            "checkpoint_pair": payload.get("checkpoint_pair"),
        })

    warnings_text = "".join(path.read_text(errors="ignore") for path in transcript_inputs)
    input_names = ["report-histories-batched.json", "residuals-batched-resume.json"] + [path.name for path in transcript_inputs]
    summary = {
        "run_directory": str(run),
        "inputs": {name: {"path": str(run / name), "sha256": sha256(run / name)} for name in input_names},
        "report_iteration_range": [int(it.min()), int(it.max())],
        "report_point_count": int(len(it)),
        "transcript_iteration_range": [int(residuals["iteration"].min()), int(residuals["iteration"].max())],
        "transcript_residual_point_count": int(len(residuals["iteration"])),
        "terminal_state": {
            "total_liquid_mass_kg": float(total_mass[-1]),
            "total_liquid_volume_m3": float(total_volume[-1]),
            "lower_liquid_mass_kg": float(lower_mass[-1]),
            "lower_liquid_volume_m3": float(lower_volume[-1]),
            "command_kg_s": float(command[-1]),
            "absorber_removal_kg_s": float(removal[-1]),
            "command_error_kg_s": float(command_error[-1]),
            "mixture_steamoutlet_kg_s": float(mix_out[-1]),
        },
        "window_statistics": {
            "continuity_max": float(np.max(residuals["continuity"])),
            "continuity_last": float(residuals["continuity"][-1]),
            "vf_phase2_max": float(np.max(residuals["vf-phase-2"])),
            "vf_phase2_last": float(residuals["vf-phase-2"][-1]),
            "reverse_flow_messages": len(re.findall(r"Reversed flow on", warnings_text)),
            "viscosity_limit_messages": len(re.findall(r"turbulent viscosity limited", warnings_text)),
            "amg_messages": len(re.findall(r"AMG", warnings_text, re.I)),
            "fpe_messages": len(re.findall(r"floating point exception|\bFPE\b", warnings_text, re.I)),
            "nonfinite_messages": len(re.findall(r"non.?finite|\bNaN\b|\bInf\b", warnings_text, re.I)),
        },
        "closures_terminal": {
            "phase1_boundary_kg_s": float(p1_closure[-1]),
            "phase2_boundary_plus_absorber_kg_s": float(p2_closure[-1]),
            "mixture_boundary_plus_source_kg_s": float(mixture_closure[-1]),
            "storage_increment_kg_per_iteration": float(storage_rate[-1]),
        },
        "checkpoint_snapshots": checkpoints,
        "figures": {path.name: {"path": str(path), "sha256": sha256(path)} for path in sorted(fig_dir.glob("*.png"))},
        "interpretation_limits": [
            "The RP current-iteration variable was stale on this Fluent session; transcript iteration rows and checkpoint offsets are the native-coordinate evidence used here.",
            "The source-inclusive closure is a signed algebraic diagnostic; storage is shown as finite difference of reported total liquid mass per native iteration and is not a dimensional physical time rate.",
        ],
    }
    (analysis_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
