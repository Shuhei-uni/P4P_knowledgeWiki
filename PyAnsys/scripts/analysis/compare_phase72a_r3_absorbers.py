"""Matched native-history comparison of R3/E2.7 old and new collectors."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OLD_ROOT = ROOT / "output/phase72a-stage2-cap1m/R3-recovery2-20261003"


def stats(record):
    x, y = np.array(record["iterations"]), np.array(record["values"], dtype=float)
    valid = np.isfinite(y)
    tx, ty = x[valid][-500:], y[valid][-500:]
    return {"points": len(x), "first": float(y[0]), "final": float(y[-1]),
            "minimum": float(y[valid].min()), "maximum": float(y[valid].max()),
            "nonfinite_points": int((~valid).sum()), "tail500_mean": float(ty.mean()),
            "tail500_std": float(ty.std()), "tail500_slope_per_iteration": float(np.polyfit(tx-tx[0], ty, 1)[0])}


def cap_stats(record):
    hits = [n for n, h in zip(record["iterations"], record["values"])
            if h >= 1.0 - 1e-10]
    return {"first_native_iteration_at_1m": hits[0] if hits else None,
            "points_at_1m": len(hits), "total_points": record["points"]}


def continuity(path):
    samples = {}
    for line in path.read_text(errors="replace").splitlines():
        match = re.match(r"^\s*(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", line)
        if match and 13586 <= int(match[1]) <= 16586:
            samples[int(match[1])] = float(match[2])
    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--figure-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.run_root/"run-manifest.json").read_text())
    if manifest["status"] != "COMPLETE" or manifest["native_terminal_iteration"] != 16586:
        raise RuntimeError("The comparison requires verified 3000-iteration completion")
    old = json.loads((OLD_ROOT/"report-histories.json").read_text())
    new = json.loads((args.run_root/"report-histories.json").read_text())
    for records in (old, new):
        for item in records.values():
            if item["iterations"] != list(range(13586, 16587)) or len(item["values"]) != 3001:
                raise RuntimeError("History requires 3001 unique consecutive native coordinates N13586–16586")
    args.figure_root.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .2})
    oldc, newc = "#808080", "#005f99"

    def draw(ax, records, key, label, color, scale=1, style="-"):
        item = records[key]
        ax.plot(item["iterations"], np.array(item["values"])*scale, style, color=color, lw=.8, alpha=.85, label=label)

    fig, axes = plt.subplots(3, 2, figsize=(13, 10), sharex=True, layout="constrained")
    specifications = [
        ("p72a-e2.7-ewf-thickness-max", "Upper film maximum thickness (mm)", 1000),
        ("p72a-e2.7-ewf-film-mass-total", "Film inventory (kg)", 1),
        ("p72a-e2.7-ewf-velocity-mag-awavg", "Upper mean film speed (m/s)", 1),
        ("v2-total-liquid-mass", "Bulk liquid inventory (kg)", 1),
        ("v2-flux-phase2-steamoutlet", "Liquid outflow through steamoutlet (kg/s)", -1),
    ]
    for ax, (key, title, scale) in zip(axes.flat, specifications):
        draw(ax, old, key, "Old absorber", oldc, scale)
        draw(ax, new, key, "New absorber: upper film" if "film-mass" in key else "New absorber", newc, scale)
        ax.set_title(title)
    draw(axes[0,0], new, "p72a-collector-combined-thickness-max", "New: upper + lower maximum", "#d47a00", 1000, "--")
    draw(axes[0,1], new, "p72a-collector-combined-film-mass-total", "New: upper + lower inventory", "#d47a00", 1, "--")
    axes[1,0].set_yscale("symlog", linthresh=1)
    ax = axes[2,1]
    draw(ax, old, "v2-absorber-removal", "Old evaluated bulk removal", oldc)
    draw(ax, new, "p72a-collector-bulk-removal", "New evaluated bulk removal", newc)
    draw(ax, new, "p72a-collector-film-removal", "New evaluated film removal", "#00835b")
    draw(ax, new, "p72a-collector-total-removal", "New evaluated combined removal", "#d47a00", 1, "--")
    ax.axhline(116.92, color="black", ls=":", lw=.8, label="Single 116.92 kg/s command")
    ax.set_title("Evaluated collector rates (kg/s)")
    for ax in axes.flat:
        ax.legend(fontsize=7, loc="best")
    for ax in axes[-1]:
        ax.set_xlabel("Native Fluent iteration")
    fig.suptitle("R3 + E2.7: old versus shared bulk/EWF absorber — same 1 m cap, N13586–16586", fontsize=13)
    primary = args.figure_root / "R3-E27-old-new-absorber-histories.png"
    fig.savefig(primary, dpi=180)
    plt.close(fig)

    old_t = OLD_ROOT/"transcript-stream.txt"
    if not old_t.exists():
        old_t = OLD_ROOT/"transcript-native-solve.txt"
    original_t = OLD_ROOT.parent / "R3-20261002T122100Z/transcript-stream.txt"
    old_segments = [continuity(original_t), continuity(old_t)]
    old_res = {}
    for segment in old_segments:
        if set(segment) & set(old_res):
            raise RuntimeError("Overlapping old continuity segments require explicit reconciliation")
        old_res.update(segment)
    new_t = args.run_root/"transcript-repaired-solve.txt"
    new_res = continuity(new_t)
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, layout="constrained")
    for index, segment in enumerate(old_segments):
        axes[0].semilogy(list(segment), list(segment.values()), color=oldc, lw=.6,
                        alpha=.85, label="Old absorber" if index == 0 else None)
    axes[0].semilogy(list(new_res), list(new_res.values()), color=newc, lw=.6,
                    alpha=.85, label="New absorber")
    old_missing = sorted(set(range(13586, 16587)) - set(old_res))
    axes[0].set_title("Scaled continuity residual; old transcript gap N14360–14585 retained")
    draw(axes[1], old, "v2-applied-absorber", "Old native applied bulk sink", oldc, -1)
    draw(axes[1], new, "v2-applied-absorber", "New native applied bulk sink", newc, -1)
    draw(axes[1], new, "p72a-collector-film-removal", "New evaluated film sink", "#00835b")
    axes[1].set_title("Native applied bulk sink and evaluated film sink (kg/s); different reporting bases")
    axes[1].set_xlabel("Native Fluent iteration")
    for ax in axes:
        ax.legend()
    secondary = args.figure_root/"R3-E27-old-new-absorber-continuity-sources.png"
    fig.savefig(secondary, dpi=180)
    plt.close(fig)
    keys = [item[0] for item in specifications] + ["v2-applied-absorber", "v2-absorber-removal"]
    summary = {"native_window": [13586,16586], "new_manifest": str(args.run_root/"run-manifest.json"),
        "old_histories": str(OLD_ROOT/"report-histories.json"), "new_histories": str(args.run_root/"report-histories.json"),
        "old": {k:stats(old[k]) for k in keys}, "new": {k:stats(new[k]) for k in keys},
        "new_collector": {k:stats(v) for k,v in new.items() if k.startswith("p72a-collector-")},
        "upper_film_cap": {"old": cap_stats(old["p72a-e2.7-ewf-thickness-max"]),
                           "new": cap_stats(new["p72a-e2.7-ewf-thickness-max"])},
        "continuity_points": {"old":len(old_res), "new":len(new_res)},
        "continuity_stats": {label: stats({"iterations":sorted(values),
                                            "values":[values[n] for n in sorted(values)]})
                             for label,values in [("old",old_res),("new",new_res)]},
        "old_continuity_segments": [{"file":str(path), "points":len(segment),
                                      "first":min(segment), "last":max(segment)}
                                     for path,segment in zip([original_t, old_t],old_segments)],
        "old_continuity_missing_iterations": old_missing,
        "plots": [str(primary),str(secondary)],
        "claim_limits": ["Matched E2.7 parent, R3 roughness and 1 m cap; the new collector also enables lower-wall EWF storage and its sources", "Local execution repartitioned the eighteen-partition input onto four compute nodes; cross-machine numerical trajectories need not match", "Expression collector rates are evaluated rules; native applied bulk source is reported separately", "Clipping, extreme film velocity and unresolved full EWF-inclusive storage/transfer closure prohibit physical efficiency claims"]}
    (args.run_root/"comparison-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"plots":summary["plots"], "old_film_mass_kg":summary["old"]["p72a-e2.7-ewf-film-mass-total"]["final"],
        "new_combined_film_mass_kg":summary["new_collector"]["p72a-collector-combined-film-mass-total"]["final"]},indent=2))


if __name__ == "__main__":
    main()
