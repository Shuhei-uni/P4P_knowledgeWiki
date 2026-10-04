"""Rebuild the poster's vector figures from reported values and native histories.

Run from any directory with:
  uv run --with matplotlib python Project/meetings/poster-assets/build_poster_figures.py
No Fluent session is accessed and no source evidence is modified.
"""

from pathlib import Path
import base64
import hashlib
import json
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INK, GREY, RULE, SURFACE, LIQUID = "#17324D", "#52616B", "#CBD5DB", "#F3F6F7", "#007F86"
plt.rcParams.update({
    "font.family": "Arial", "font.size": 30, "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.edgecolor": GREY, "axes.linewidth": 1.5,
    "svg.fonttype": "none", "svg.hashsalt": "p4p-poster-v1",
    "figure.facecolor": "white", "axes.facecolor": "white",
})
# Verify the intended typeface instead of silently choosing a different font.
font_manager.findfont("Arial", fallback_to_default=False)

def finish(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=8, width=1.5, pad=14)
    ax.set_axisbelow(True)

def save_vector(fig, name):
    # At the A1 placement width, 30-point export labels read at about 20 pt.
    # Verify all visible text is within the export, including axis labels.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for label in fig.findobj(Text):
        if not label.get_visible() or not label.get_text():
            continue
        box = label.get_window_extent(renderer)
        assert (box.x0 >= bounds.x0 - 1 and box.y0 >= bounds.y0 - 1
                and box.x1 <= bounds.x1 + 1 and box.y1 <= bounds.y1 + 1), (
                    name, "Clipped figure label", label.get_text(), box.bounds)
    fig.savefig(OUT / name, metadata={"Date": None})

reported_source = ROOT / "Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/results.md"
reported = reported_source.read_text()
for number in ["57.682", "2.408", "1.393", "0.0336", "0.2649", "0.0149"]:
    assert number in reported, f"Poster value missing from owning record: {number}"
fig, ax = plt.subplots(figsize=(18, 3.7))
fig.subplots_adjust(left=.21, right=.93, bottom=.42, top=.95)
ax.barh([1, 0], [57.682, 2.408], height=.48,
        color=[SURFACE, INK], edgecolor=[GREY, INK], linewidth=3)
ax.patches[0].set_linestyle((0, (5, 4)))
ax.set_yticks([1, 0], ["SIMPLE\npackage", "Recovery\npackage"])
ax.set_xticks([0, 20, 40, 60])
ax.set_xlim(0, 74)
ax.set_ylim(-.6, 1.6)
ax.grid(axis="x", color=RULE, linewidth=1)
ax.set_xlabel("Absolute boundary imbalance (kg/s)", labelpad=16)
for y, value in [(1, 57.682), (0, 2.408)]:
    ax.text(value + 1.8, y, f"{value:.3f}", va="center", fontweight="bold")
finish(ax)
save_vector(fig, "boundary-imbalance.svg")
plt.close(fig)

history_path = ROOT / "PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json"
data = json.loads(history_path.read_text())
mass = data["v2-total-liquid-mass"]
xs, ys = mass["iterations"], mass["values"]
assert len(xs) == len(ys) and len(set(xs)) == len(xs)
assert xs == sorted(xs) and xs[0] == 3580 and xs[-1] == 5586
assert all(b - a == 1 for a, b in zip(xs, xs[1:]))

def window(lo, hi):
    points = [(x, y) for x, y in zip(xs, ys) if lo <= x <= hi]
    xw, yw = zip(*points)
    xm, ym = statistics.mean(xw), statistics.mean(yw)
    slope = sum((x-xm)*(y-ym) for x, y in points) / sum((x-xm)**2 for x in xw)
    return {"iterations": [lo, hi], "points": len(points),
            "start_kg": yw[0], "end_kg": yw[-1],
            "change_kg": yw[-1]-yw[0], "ols_slope_kg_per_iteration": slope}

fig, ax = plt.subplots(figsize=(18, 4.2))
fig.subplots_adjust(left=.14, right=.95, bottom=.34, top=.84)
ax.axvspan(4586, 5586, color=SURFACE, zorder=0)
ax.plot(xs, ys, color=LIQUID, linewidth=3)
ax.axvline(4586, color=GREY, linewidth=1.5, linestyle=(0, (6, 5)))
ax.set_xlim(3500, 5700)
ax.set_ylim(170, 315)
ax.set_yticks([200, 250, 300])
ax.set_xticks([3500, 4000, 4500, 5000, 5500])
ax.grid(axis="y", color=RULE, linewidth=1)
ax.set_xlabel("Native steady iteration", labelpad=16)
ax.text(0, 1.14, "Liquid mass (kg)", transform=ax.transAxes)
ax.text(.64, 1.14, "Control window", transform=ax.transAxes, color=GREY)
finish(ax)
save_vector(fig, "liquid-inventory.svg")
plt.close(fig)

native_path = ROOT / "Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-liquid.png"
encoded = base64.b64encode(native_path.read_bytes()).decode("ascii")
# Presentation-only viewports retain original field pixels and the original
# colour strip. Large vector labels replace the small native export labels.
native_image = f'<image width="1800" height="2400" href="data:image/png;base64,{encoded}"/>'
section_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1650" viewBox="0 0 900 1650" role="img" aria-labelledby="title desc">
<title id="title">Native separator liquid-volume-fraction section</title>
<desc id="desc">F2 Coupled at 26.81 m/s and N10000, z=0. Native field pixels and colour strip are unchanged. Liquid volume fraction ranges from zero to one.</desc>
<rect width="900" height="1650" fill="white"/>
<g font-family="Arial" font-size="80" fill="{INK}">
<text x="20" y="110">Liquid</text><text x="20" y="205">volume</text><text x="20" y="300">fraction</text>
<text x="125" y="820">1.0</text><text x="125" y="1110">0.5</text><text x="125" y="1400">0.0</text>
</g>
<svg x="50" y="790" width="46" height="580" viewBox="53 803 65 851" preserveAspectRatio="none">{native_image}</svg>
<svg x="300" y="20" width="560" height="1590" viewBox="560 70 690 2240">{native_image}</svg>
</svg>'''
(OUT / "separator-section.svg").write_text(section_svg)

droplet_source = ROOT / "Project/experiments/phase-08-storyline-reconstruction/f3-coupled-dpm/results.md"
droplet_report = droplet_source.read_text()
for number in ["1.88", "19.13", "78.98", "5.846936325"]:
    assert number in droplet_report, f"Droplet value missing from owning record: {number}"
# Widths preserve the reported rounded percentages, without silently normalising
# the 99.99% sum. Direct labels identify outcomes independently of colour.
droplet_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="160" viewBox="0 0 1000 160" role="img" aria-labelledby="title desc">
<title id="title">Represented droplet-feed fates at the 5% reference pilot</title>
<desc id="desc">F3 at 26.81 m/s and N11000: escaped 1.88%, trapped 19.13%, incomplete 78.98%. Percentages are injection-weighted and rounded; incomplete trajectories remain unresolved.</desc>
<defs><pattern id="escape-hatch" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M-3 3L3-3M0 12L12 0M9 15L15 9" stroke="{GREY}" stroke-width="3"/></pattern></defs>
<rect width="1000" height="160" fill="white"/>
<rect x="5" y="18" width="18.048" height="45" fill="url(#escape-hatch)" stroke="{INK}" stroke-width="2"/>
<rect x="23.048" y="18" width="183.648" height="45" fill="{INK}"/>
<rect x="206.696" y="18" width="758.208" height="45" fill="{SURFACE}" stroke="{GREY}" stroke-width="2"/>
<g font-family="Arial" font-size="29" fill="{INK}">
<text x="5" y="107" font-weight="bold">1.88%</text><text x="5" y="147">Escaped</text>
<text x="250" y="107" font-weight="bold">19.13%</text><text x="250" y="147">Trapped</text>
<text x="555" y="107" font-weight="bold">78.98%</text><text x="555" y="147">Incomplete</text>
</g></svg>'''
(OUT / "droplet-fates.svg").write_text(droplet_svg)

phase1in, phase2in, phase1out, phase2out, nativeout, source = [
    data[key] for key in ["v2-flux-phase1-steaminlet", "v2-flux-phase2-liquidinlet",
                         "v2-flux-phase1-steamoutlet", "v2-flux-phase2-steamoutlet",
                         "v2-flux-mixture-steamoutlet", "v2-applied-absorber"]]
assert all(s["iterations"] == xs for s in [phase1in, phase2in, phase1out, phase2out, nativeout, source])
liquid_error = phase2in["values"][-1] + phase2out["values"][-1] + source["values"][-1]
mixture_error = phase1in["values"][-1] + phase2in["values"][-1] + nativeout["values"][-1] + source["values"][-1]

manifest = {
    "status": "Draft poster communication layer; no simulation or raw evidence edits",
    "comparison": {
        "source": str(reported_source.relative_to(ROOT)),
        "basis": "Phase 8 F2, 26.81 m/s, 60,964 cells, split feed, closed bottom, no absorber/EWF, independently initialized branches, N5000 endpoints",
        "values": {"simple_boundary_error_kg_s": 57.682, "recovery_boundary_error_kg_s": 2.408,
                   "simple_last500_inventory_slope_kg_per_iteration": 1.393,
                   "recovery_last500_inventory_slope_kg_per_iteration": .0336,
                   "simple_terminal_continuity": .2649, "recovery_terminal_continuity": .0149},
        "limits": "Reported values from Project; linked Phase 8 native analysis bundles absent from checkout. Multiple numerical settings change together."
    },
    "inventory": {
        "source": str(history_path.relative_to(ROOT)),
        "sha256": hashlib.sha256(history_path.read_bytes()).hexdigest(),
        "series": "v2-total-liquid-mass", "rendering": "All 2,007 raw samples, no smoothing or interpolation",
        "basis": "Phase 7.1A R0, full loading, smooth wall, absorber on, EWF off; separate configuration from Phase 8",
        "windows": [window(3580, 4586), window(4586, 5586), window(5086, 5586)],
        "terminal_liquid_error_kg_s": liquid_error,
        "terminal_native_mixture_error_kg_s": mixture_error,
        "terminal_liquid_error_pct_feed": 100 * abs(liquid_error) / phase2in["values"][-1],
        "terminal_native_mixture_error_pct_feed": 100 * abs(mixture_error) / (phase1in["values"][-1] + phase2in["values"][-1]),
        "limits": "Inventory stationarity does not establish source-inclusive closure; kg/iteration is not physical kg/s. Native restart coordinates retained."
    },
    "droplet_fates": {
        "source": str(droplet_source.relative_to(ROOT)),
        "basis": "Phase 8 F3, 26.81 m/s, 5% liquid allocated to coupled DPM, N11000; seven-bin assumed fine mist, 50,000-step tracking cap",
        "escaped_pct": 1.88, "trapped_pct": 19.13, "incomplete_pct": 78.98,
        "represented_feed_kg_s": 5.846936325,
        "limits": "Reported injection-weighted fates, not trajectory-count fractions or separator efficiency. Rounded total is 99.99%; bars not renormalised."
    },
    "spatial_view": {
        "source": "Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-liquid.png",
        "basis": "Native Fluent 2025 R2 export, F2 Coupled, 26.81 m/s, N10000, z=0, phase-2 volume fraction 0–1",
        "rendering": "Original field and colour-strip pixels embedded in clipped SVG viewports, with larger vector labels. No recolouring or field alteration; offset inlet outside section.",
        "sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
        "native_pixel_viewports": {"field": [560, 70, 690, 2240], "colour_strip": [53, 803, 65, 851]}
    }
}
(OUT / "figure-provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"generated": ["boundary-imbalance.svg", "liquid-inventory.svg", "separator-section.svg", "droplet-fates.svg", "figure-provenance.json"],
                  "inventory_windows": manifest["inventory"]["windows"],
                  "liquid_error_pct": manifest["inventory"]["terminal_liquid_error_pct_feed"]}, indent=2))
