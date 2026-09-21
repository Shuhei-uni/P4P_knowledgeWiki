"""Offline Phase 7b evidence and figures; completion is not qualification.

Usage: python analyze_phase07b_screen.py RUN_DIRECTORY [--output DIRECTORY]
Native flux signs are positive into the vessel. Applied source is signed:
liquid/mixture closure = boundary sum + native applied source, exactly once.
No inventory trend per steady iteration is interpreted as physical storage.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "p7b-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HORIZON = 5000
WINDOWS = ((4001, 4500), (4501, 5000))


def fingerprint(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def canonical(name: str) -> str:
    name = name.lower().removeprefix("proof-")
    return re.sub(r"[^a-z0-9]", "", name)


def table(rows: list[tuple[int, list[float]]], names: list[str]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    unique: dict[int, list[float]] = {}
    duplicates, conflicts = [], []
    for iteration, values in rows:
        if iteration in unique:
            duplicates.append(iteration)
            if not np.array_equal(unique[iteration], values, equal_nan=True):
                conflicts.append(iteration)
            continue
        unique[iteration] = values
    indices = sorted(unique)
    matrix = np.asarray([unique[i] for i in indices], dtype=float).reshape(len(indices), len(names))
    data = {name: matrix[:, j] for j, name in enumerate(names)}
    data["iteration"] = np.asarray(indices, dtype=int)
    return data, {
        "rows": len(rows), "unique_rows": len(indices),
        "duplicate_indices": duplicates, "conflicting_indices": sorted(set(conflicts)),
        "nonfinite_columns": [n for n in names if not np.isfinite(data[n]).all()],
        "first_iteration": indices[0] if indices else None,
        "last_iteration": indices[-1] if indices else None,
    }


def parse_history(path: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    header = None
    rows, rejected = [], []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith('("Iteration"'):
            current = re.findall(r'"([^"]+)"', line)
            if header is not None and current != header:
                raise ValueError(f"History header changed at {path}:{number}")
            header = current
            continue
        if header is None or not re.match(r"^\s*\d+\s", line):
            continue
        try:
            values = [float(v.replace("D", "e").replace("d", "e")) for v in line.split()]
            if len(values) != len(header) or not values[0].is_integer():
                raise ValueError("row width/index mismatch")
            rows.append((int(values[0]), values[1:]))
        except ValueError:
            rejected.append(number)
    if not header:
        raise ValueError(f"No native report header in {path}")
    names = [canonical(n) for n in header[1:]]
    if len(set(names)) != len(names):
        raise ValueError("Ambiguous canonical report column names")
    data, audit = table(rows, names)
    audit.update(source=fingerprint(path), native_header=header, rejected_lines=rejected)
    return data, audit


def parse_residuals(path: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    names = None
    rows, malformed = [], []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        words = line.split()
        if words and words[0] == "iter" and "continuity" in words:
            current = words[1:words.index("time/iter")] if "time/iter" in words else words[1:]
            if names is not None and names != current:
                raise ValueError(f"Residual equation set changed at {path}:{number}")
            names = current
            continue
        if not names or len(words) < len(names) + 1 or not words[0].isdigit():
            continue
        # Exclude numeric tables printed elsewhere in a transcript.
        if not any(":" in token for token in words[1 + len(names):]):
            continue
        try:
            rows.append((int(words[0]), [float(v) for v in words[1:1 + len(names)]]))
        except ValueError:
            malformed.append(number)
    data, audit = table(rows, names or [])
    audit.update(source=fingerprint(path), rejected_lines=malformed,
                 nonpositive_columns=[n for n in (names or []) if np.any(data[n] <= 0)])
    return data, audit


def parse_flux(path: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    names = ["delivery_kg_s", "escape_kg_s", "net_outward_kg_s"]
    rows, rejected = [], []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        try:
            row = json.loads(line)
            index = row["iteration"]
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("Noninteger flux index")
            rows.append((index, [float(row[n]) for n in names]))
        except (ValueError, KeyError, TypeError):
            rejected.append(number)
    data, audit = table(rows, names)
    audit.update(source=fingerprint(path), rejected_lines=rejected,
                 remote_persistence="Local rows alone do not prove remote writes; inspect run flux_monitor manifest.")
    return data, audit


def coverage(audit: dict[str, Any], data: dict[str, np.ndarray], end: int) -> None:
    actual = set(int(i) for i in data.get("iteration", []) if i > 0)
    missing = sorted(set(range(1, end + 1)) - actual)
    audit.update(expected_start=1, expected_end=end, missing_indices=missing,
                 complete_to_expected_end=end > 0 and not audit.get("missing") and not missing and not audit.get("conflicting_indices")
                 and not audit.get("nonfinite_columns") and not audit.get("rejected_lines"))


def derive(data: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], dict[str, str]]:
    derived, units = {}, {}
    def put(name: str, values: np.ndarray, unit: str) -> None:
        derived[name] = values
        units[name] = unit
    for suffix, label in [("watervolume", "whole_water_volume"), ("collectorvolume", "collector_water_volume"), ("abovevolume", "above_water_volume")]:
        if "p7b" + suffix in data:
            put(label, data["p7b" + suffix], "m^3")
    for suffix, label in [("watermass", "whole_water_mass"), ("collectormass", "collector_water_mass")]:
        if "p7b" + suffix in data:
            put(label, data["p7b" + suffix], "kg")
    if "whole_water_mass" in derived and "collector_water_mass" in derived:
        put("above_water_mass", derived["whole_water_mass"] - derived["collector_water_mass"], "kg")
    if "p7bremoval" in data:
        put("current_expression_removal", data["p7bremoval"], "kg/s")
    for key, label in [("p7bpressureliquid", "liquid_inlet_pressure"),
                       ("p7bpressuresteam", "steam_inlet_pressure"),
                       ("p7bpressureoutlet", "outlet_pressure"),
                       ("p7bdropliquid", "liquid_inlet_pressure_drop"),
                       ("p7bdropsteam", "steam_inlet_pressure_drop"),
                       ("p7bminimumpressure", "minimum_fluid_pressure"),
                       ("p7bmaximumpressure", "maximum_fluid_pressure")]:
        if key in data:
            put(label, data[key], "Pa")
    if "p7bmaximumspeed" in data:
        put("maximum_mixture_speed", data["p7bmaximumspeed"], "m/s")
    if "p7bappliedsource" in data:
        put("native_applied_removal", -data["p7bappliedsource"], "kg/s")
    for phase in ["liquid", "vapor", "mixture"]:
        fields = ["p7b" + phase + suffix for suffix in ["liquidinlet", "steaminlet", "outlet", "brinewall"]]
        if all(f in data for f in fields):
            boundary = sum(data[f] for f in fields)
            feed = data[fields[0]] + data[fields[1]]
            put(phase + "_net_boundary_inflow", boundary, "kg/s")
            put(phase + "_measured_feed", feed, "kg/s")
            if phase == "vapor" or "p7bappliedsource" in data:
                balance = boundary if phase == "vapor" else boundary + data["p7bappliedsource"]
                put(phase + "_closure_applied", balance, "kg/s")
                ratio = np.divide(100 * balance, feed, out=np.full_like(balance, np.nan), where=feed > 0)
                put(phase + "_closure_percent_feed", ratio, "%")
            if phase in ("liquid", "vapor"):
                ratio = np.divide(-data[fields[2]], feed, out=np.full_like(feed, np.nan), where=feed > 0)
                put("liquid_carryover_fraction" if phase == "liquid" else "steam_recovery_fraction", ratio, "1")
    if "p7bliquidoutlet" in data and "p7bvaporoutlet" in data:
        liquid, vapor = -data["p7bliquidoutlet"], -data["p7bvaporoutlet"]
        put("outlet_vapor_mass_fraction", np.divide(vapor, vapor + liquid, out=np.full_like(vapor, np.nan), where=(vapor + liquid) > 0), "1")
    return derived, units


def stats(x: np.ndarray, y: np.ndarray, unit: str) -> dict[str, Any]:
    valid = np.isfinite(y)
    if not valid.all() or not len(y):
        return {"valid": False, "samples": len(y), "finite_samples": int(valid.sum()), "unit": unit}
    return {"valid": True, "samples": len(y), "unit": unit, "mean": float(y.mean()),
            "minimum": float(y.min()), "maximum": float(y.max()), "standard_deviation": float(y.std()),
            "slope_per_iteration": float(np.polyfit(x - x.mean(), y, 1)[0]) if len(y) > 1 else None,
            "slope_unit": unit + "/iteration", "mean_absolute": float(np.abs(y).mean())}


def fixed_windows(x: np.ndarray, metrics: dict[str, np.ndarray], units: dict[str, str]) -> dict[str, Any]:
    windows = {}
    for lo, hi in WINDOWS:
        mask = (x >= lo) & (x <= hi)
        complete = np.array_equal(x[mask], np.arange(lo, hi + 1))
        windows[f"{lo}-{hi}"] = {"complete": complete, "observed_samples": int(mask.sum()),
            "metrics": {k: stats(x[mask], v[mask], units[k]) for k, v in metrics.items()} if complete else {}}
    comparisons = {}
    if all(w["complete"] for w in windows.values()):
        first, second = [w["metrics"] for w in windows.values()]
        for name in metrics:
            if first[name]["valid"] and second[name]["valid"]:
                a, b = first[name]["mean"], second[name]["mean"]
                item = {"mean_change": b - a, "unit": units[name]}
                if units[name] == "m^3":
                    item["mean_change_percent_with_1e-6_m3_floor"] = 100 * (b - a) / max(abs(a), 1e-6)
                comparisons[name] = item
    return {"windows": windows, "second_minus_first": comparisons}


def draw(ax: Any, x: np.ndarray, metrics: dict[str, np.ndarray], names: list[tuple[str, str]], ylabel: str) -> None:
    found = False
    for key, label in names:
        if key in metrics:
            ax.plot(x, metrics[key], label=label, linewidth=1)
            found = True
    if found:
        ax.legend(fontsize=8)
    else:
        ax.text(.5, .5, "Required evidence unavailable", ha="center", transform=ax.transAxes)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=.2)


def analyze(run: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = run / "manifest.json"
    if not manifest_path.exists():
        manifest_path = run / "result.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    candidates = list(run.glob("history-*.out")) + ([run / "history.out"] if (run / "history.out").exists() else [])
    parsed, rejected_files = [], []
    for path in candidates:
        try:
            data, audit = parse_history(path)
            parsed.append((data, audit))
        except ValueError as exc:
            rejected_files.append({"path": str(path), "error": str(exc)})
    if not parsed:
        raise ValueError(f"No readable native report history in {run}; {rejected_files}")
    data, history_audit = max(parsed, key=lambda pair: (pair[1]["last_iteration"] or -1, pair[1]["unique_rows"]))
    x = data["iteration"]
    last = int(x[-1]) if len(x) else 0
    claimed = manifest.get("completed_iterations", manifest.get("actual_iteration", manifest.get("final_iteration", 0)))
    end = max(last, int(claimed or 0))
    coverage(history_audit, data, end)
    flux_path = run / "collector-flux.jsonl"
    flux, flux_audit = parse_flux(flux_path) if flux_path.exists() else ({"iteration": np.array([], dtype=int)}, {"missing": True})
    residual_path = run / "solve.trn"
    residuals, residual_audit = parse_residuals(residual_path) if residual_path.exists() else ({"iteration": np.array([], dtype=int)}, {"missing": True})
    coverage(flux_audit, flux, end)
    coverage(residual_audit, residuals, end)
    metrics, units = derive(data)
    label = str(manifest.get("run_id", run.name))
    qualifier = "5,000-iteration evidence" if last == HORIZON else f"PARTIAL: through iteration {last}"
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), constrained_layout=True, sharex=True)
    draw(axes[0], x, metrics, [(n, l) for n, l in [("whole_water_volume", "Whole vessel"), ("collector_water_volume", "Collector"), ("above_water_volume", "Above collector")]], "Liquid volume (m³)")
    draw(axes[1], x, metrics, [("native_applied_removal", "Native applied removal"), ("current_expression_removal", "Current expression S(αₙ)")], "Liquid removal (kg/s)")
    if "native_applied_removal" not in metrics:
        axes[1].text(.02, .92, "Native applied source missing", transform=axes[1].transAxes, fontsize=9)
    draw(axes[2], flux["iteration"], flux, [("delivery_kg_s", "Gross delivery to collector"), ("escape_kg_s", "Gross escape from collector")], "Liquid mask flux (kg/s)")
    axes[2].set_xlabel("Steady iteration (not physical time)")
    fig.suptitle(f"F1 — Inventory and collection\n{label} · {qualifier}")
    fig.savefig(output / "F1-inventory-removal.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True, sharex=True)
    draw(axes[0], x, metrics, [(p + "_closure_percent_feed", p.title()) for p in ["liquid", "vapor", "mixture"]], "Applied-source closure (% feed)")
    axes[0].axhline(0, color="black", lw=.7)
    if "native_applied_removal" not in metrics:
        axes[0].text(.02, .92, "Liquid/mixture closure unavailable: native applied source missing", transform=axes[0].transAxes, fontsize=9)
    draw(axes[1], x, metrics, [("liquid_carryover_fraction", "Liquid carryover / liquid feed"), ("steam_recovery_fraction", "Steam recovery / vapor feed"), ("outlet_vapor_mass_fraction", "Outlet vapor mass fraction")], "Signed net-flow ratio")
    axes[1].set_xlabel("Steady iteration")
    fig.suptitle(f"F2 — Conservation and outlet routing\n{label} · {qualifier}")
    fig.savefig(output / "F2-closure-routing.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    draw(ax, residuals["iteration"], residuals, [(n, n) for n in residuals if n != "iteration"], "Native scaled residual")
    ax.set_yscale("log"); ax.set_xlabel("Steady iteration")
    ax.set_title(f"All active residual histories\n{label} · {qualifier}")
    fig.savefig(output / "residuals.png", dpi=160); plt.close(fig)
    residual_metrics = {n: a for n, a in residuals.items() if n != "iteration"}
    required = ["whole_water_volume", "collector_water_volume", "above_water_volume", "native_applied_removal", "current_expression_removal", "liquid_closure_applied", "vapor_closure_applied", "mixture_closure_applied"]
    summary = {
        "schema_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run.resolve()), "run_id": label,
        "manifest_source": fingerprint(manifest_path) if manifest_path.exists() else None,
        "manifest_status": manifest.get("status"), "scientific_screen": manifest.get("scientific_screen", manifest_path.name == "manifest.json"),
        "planned_scientific_horizon": HORIZON,
        "requested_iterations": manifest.get("requested_iterations", manifest.get("requested_diagnostic_iterations")),
        "claimed_completed_or_actual_iteration": claimed, "observed_report_last_iteration": last,
        "horizon_observed": last == HORIZON and history_audit["complete_to_expected_end"],
        "analysis_status": ("HORIZON_OBSERVED_EVIDENCE_REVIEW_REQUIRED" if last == HORIZON and history_audit["complete_to_expected_end"]
                            else "INCOMPLETE_EVIDENCE_NO_HORIZON_CLAIM" if last >= HORIZON
                            else "PARTIAL_NO_LATE_WINDOW_JUDGMENT"),
        "history": history_audit, "other_history_candidates": [a["source"] for _, a in parsed if a is not history_audit],
        "rejected_history_files": rejected_files, "collector_flux": flux_audit,
        "run_flux_monitor": manifest.get("flux_monitor"), "residuals": residual_audit,
        "latest_residuals": {n: float(a[-1]) if len(a) and np.isfinite(a[-1]) else None for n, a in residual_metrics.items()},
        "missing_required_derived_metrics": [name for name in required if name not in metrics],
        "latest_metrics": {n: {"value": float(y[-1]) if len(y) and np.isfinite(y[-1]) else None, "unit": units[n]} for n, y in metrics.items()},
        "fixed_late_windows": fixed_windows(x, metrics, units),
        "collector_flux_fixed_late_windows": fixed_windows(flux["iteration"], {n: a for n, a in flux.items() if n != "iteration"}, {n: "kg/s" for n in flux if n != "iteration"}),
        "residual_fixed_late_windows": fixed_windows(residuals["iteration"], residual_metrics, {n: "1" for n in residual_metrics}),
        "definitions": {
            "applied_closure": "B + signed native applied mass source for liquid/mixture; B for vapor. Source counted once.",
            "B": "Sum of signed phase/mixture flux at both inlets, steam outlet and brine wall; positive into vessel.",
            "current_expression_removal": "-integral S(alpha_N) dV; distinct from native source used during the iteration.",
            "ratios": "Signed net outlet export divided by measured phase feed; not clipped to [0,1].",
            "steady_trends": "Slopes are per iteration, never physical kg/s storage or a second source.",
        },
        "limitations": ["Horizon completion does not establish convergence or physical steady state.",
                        "F3 requires native saved case/data spatial extraction; no spatial figure was synthesized.",
                        "Conflicting duplicate samples retain the first observed row and invalidate completeness.",
                        "No numerical qualification claim is made by this script."],
        "figures": [{"path": str((output / name).resolve()), "source": label} for name in ["F1-inventory-removal.png", "F2-closure-routing.png", "residuals.png"]],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(args.run_directory, args.output or args.run_directory / "analysis")
    print(json.dumps({"run_id": result["run_id"], "status": result["analysis_status"],
                      "last_iteration": result["observed_report_last_iteration"],
                      "missing_metrics": result["missing_required_derived_metrics"]}, indent=2))
