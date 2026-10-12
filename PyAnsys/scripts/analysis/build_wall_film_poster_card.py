"""Build the wall-film poster card from saved figures and native histories.

No Fluent connection or solve. Scientific evidence stays in its existing owner.
Run with PyAnsys/.venv/bin/python. PDF crops are rendered with native Poppler.
"""

from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import html
import json
import re
import subprocess
import uuid
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
POSTER = ROOT / "Project/Poster/Geothermal_Separator_CFD_Poster.html"
ASSETS = ROOT / "Project/Poster/poster-assets"
EARLY = ROOT / "PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006"
LATER = ROOT / "PyAnsys/output/phase72a-stage4-ewf-long-native/20261007"
DEVELOPMENT = ROOT / (
    "Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/"
    "early-ewf-startup/film-development"
)
REVIEW = Path("/tmp/p4p-poster-wall-film-review")
TEAL, ORANGE, PURPLE, INK = "#0B5F6B", "#D37B26", "#7861A5", "#10222A"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data_uri(path: Path) -> str:
    mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def window(rows: list[dict], finish: float, seconds: float = 0.01) -> dict:
    start = finish - seconds
    duration = accretion = drainage = storage = 0.0
    for a, b in zip(rows, rows[1:]):
        overlap = max(0, min(finish, b["film_time_s"]) - max(start, a["film_time_s"]))
        if overlap:
            duration += overlap
            accretion += overlap * b["accretion_kg_s"]
            drainage += overlap * b["drainage_kg_s"]
            storage += overlap * (b["film_kg"] - a["film_kg"]) / b["film_dt_s"]
    assert abs(duration - seconds) < 1e-9
    return {"accretion_kg_s": accretion / duration, "drainage_kg_s": drainage / duration,
            "storage_kg_s": storage / duration, "duration_s": duration}


def plots(rows: list[dict], later: dict) -> dict:
    times = np.array([r["film_time_s"] for r in rows])
    masses = np.array([r["film_kg"] for r in rows])
    acc = np.array([r["accretion_kg_s"] for r in rows[1:]])
    drain = np.array([r["drainage_kg_s"] for r in rows[1:]])
    storage = np.diff(masses) / np.array([r["film_dt_s"] for r in rows[1:]])
    assert np.isfinite(storage).all()
    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK,
                        "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                        "axes.spines.top": False, "axes.spines.right": False})
    for compact in (False, True):
        plt.rcParams["font.size"] = 8 if compact else 12
        fig, ax = plt.subplots(figsize=(3.1, 1.13) if compact else (6.15, 2.65))
        for values, color, label in [(acc, TEAL, "Input to film"),
                                     (drain, ORANGE, "Film drainage"),
                                     (storage, PURPLE, "Film accumulation")]:
            ax.plot(times[1:] * 1000, values, color=color, lw=1.2 if compact else 1.8, label=label)
        ax.axvline(265.1843386356894, color="#83989F", lw=0.6, ls=":")
        ax.set_xlim(0, 500)
        ax.set_ylim(-2, 88)
        ax.set_xticks([0, 250, 500] if compact else [0, 100, 200, 300, 400, 500])
        ax.set_yticks([0, 40, 80])
        ax.get_xticklabels()[-1].set_ha("right")
        ax.grid(axis="y", color="#DCE4E3", lw=0.6)
        ax.set_xlabel("Film time (ms)", labelpad=1 if compact else 5)
        ax.set_ylabel("kg/s" if compact else "Mass rate (kg/s)", labelpad=2 if compact else 6)
        ax.tick_params(length=2, pad=2)
        if not compact:
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=3,
                      frameon=False, fontsize=10, handlelength=1.7, columnspacing=1)
        fig.subplots_adjust(left=0.12 if compact else 0.13, bottom=0.30 if compact else 0.24,
                            top=0.94 if compact else 0.86, right=0.98)
        name = "wall-film-rates-compact" if compact else "wall-film-rates-early"
        fig.savefig(ASSETS / f"{name}.png", dpi=250, facecolor="white")
        if not compact:
            fig.savefig(ASSETS / f"{name}.svg", facecolor="white")
        plt.close(fig)

    w = later["pre_guard_last_75ms"]
    duration = w["duration_s"]
    values = [w["changes_kg"]["stripped"] / duration,
              w["direct_drain_mean_kg_s"], w["changes_kg"]["outflow"] / duration,
              w["changes_kg"]["separated"] / duration, w["storage_mean_kg_s"]]
    labels = ["Stripping → flow", "Film absorber → pool", "Native film outflow",
              "Edge separation → flow", "Film accumulation"]
    colors = [ORANGE, TEAL, "#4A8C9A", "#BC956D", PURPLE]
    plt.rcParams["font.size"] = 11
    fig, ax = plt.subplots(figsize=(4.0, 2.65))
    ax.barh(np.arange(5), values, color=colors, height=0.56)
    ax.invert_yaxis()
    ax.set_yticks(np.arange(5), labels)
    ax.set_xlim(0, 120)
    ax.set_xticks([0, 50, 100])
    ax.set_xlabel("Mean rate (kg/s)")
    ax.grid(axis="x", color="#DCE4E3", lw=0.6)
    ax.set_axisbelow(True)
    for i, value in enumerate(values):
        ax.text(value + 2, i, f"{value:.2f}", va="center", fontsize=10)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.52, right=0.98, bottom=0.24, top=0.96)
    fig.savefig(ASSETS / "wall-film-rates-later.png", dpi=250, facecolor="white")
    fig.savefig(ASSETS / "wall-film-rates-later.svg", facecolor="white")
    plt.close(fig)
    return dict(zip(labels, values))


def card_bounds(template: str) -> tuple[int, int]:
    marker = template.index('data-card="05"')
    start = template.rfind("<div", 0, marker)
    depth = 0
    for match in re.finditer(r"</?div\b[^>]*>", template[start:]):
        depth += -1 if match.group().startswith("</") else 1
        if depth == 0:
            return start, start + match.end()
    raise ValueError("Unclosed card 05")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    before = POSTER.read_text()
    if not (REVIEW / "before.html").exists():
        (REVIEW / "before.html").write_text(before)
    template_match = re.search(r'<script type="__bundler/template">(.*?)</script>', before, re.S)
    manifest_match = re.search(r'<script type="__bundler/manifest">(.*?)</script>', before, re.S)
    template = json.loads(template_match.group(1))
    manifest = json.loads(manifest_match.group(1))
    start, end = card_bounds(template)
    original_card = template[start:end]
    original_images = re.findall(r'<img\b[^>]*src="([^"]+)"', original_card)[:3]
    assert len(original_images) == 3

    pdf = ROOT / "CFD_wiki/raw/053_Rizaldy_Final.pdf"
    pdf_hash = digest(pdf)
    for name, y, height in [("wall-film-reentrainment-rizaldy-fig9", 260, 570),
                            ("wall-film-reentrainment-rizaldy-fig9b", 570, 260)]:
        subprocess.run(["/opt/homebrew/bin/pdftoppm", "-f", "5", "-l", "5", "-r", "300",
                        "-x", "1288", "-y", str(y), "-W", "920", "-H", str(height),
                        "-png", "-singlefile", str(pdf), str(ASSETS / name)], check=True)
    assert digest(pdf) == pdf_hash

    csv_path = EARLY / "selected-film-history-reference.csv"
    with csv_path.open() as stream:
        rows = [{k: float(v) for k, v in r.items() if k != "source_segment"}
                for r in csv.DictReader(stream)]
    assert all(b["film_time_s"] > a["film_time_s"] for a, b in zip(rows, rows[1:]))
    final = window(rows, 0.5)
    later_path = LATER / "analysis-summary.json"
    later = json.loads(later_path.read_text())
    later_rates = plots(rows, later)

    # Reuse the existing poster's local fonts; all new media is embedded.
    harness = (ROOT / "Project/Poster/Fluent_Agent_Harness_Card.html").read_text()
    font_css = "\n".join(re.findall(r"@font-face\{[^}]+\}", harness))
    def image(name: str, alt: str, cls: str = "") -> str:
        return f'<img class="{cls}" src="{data_uri(ASSETS / name)}" alt="{html.escape(alt)}">'

    development_image = DEVELOPMENT / "figures/wall-film-thickness-development-N25815.png"
    full_sources = '''<details><summary>Evidence and figure sources</summary>
<p>The early figure shows the selected Stage 3 field history. Its 500 ms result continues the same 265 ms parent; stripping, splashing, edge separation and DPM collection were OFF. The later Stage 4 run uses a different developed parent, enabled particle/film transfers and direct lower-film removal. These are distinct model-development runs.</p>
<ul>
<li><a href="../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md">Early film development and spatial evidence</a>.</li>
<li><a href="../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/setup.md">265 → 500 ms continuation lineage</a> and <a href="../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md">500 ms results</a>.</li>
<li><a href="../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv">Early raw selected film history</a>; no smoothing. The dotted line marks the final spatial snapshot at 265.18 ms; the rate history continues to 500 ms.</li>
<li><a href="../../CFD_wiki/raw/053_Rizaldy_Final.pdf#page=5">Rizaldy et al. (2016), Fig. 9, PDF p.5</a>, after Ishii and Grolmes (1975): undercut and roll-wave re-entrainment. Supports stripping rationale, not impact splashing or sharp-edge departure.</li>
<li><a href="https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html">Fluent 2025 R2 theory: particle-wall interaction, film separation, stripping and phase accretion</a>. These submodels approximate transfers; the poster does not claim resolved wave breakup or physical validation.</li>
<li><a href="../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md">Later film-absorber and release-model run</a>. The displayed means use N62647–N67647, +317.46–392.46 ms after this run's parent, a 75 ms window before the first Courant guard crossing. Native cumulative transfer differences are divided by accepted film time; direct drain is integrated from its recorded preceding rate. Splashing has no isolated reported mass rate.</li>
<li><a href="../../PyAnsys/output/phase72a-stage4-ewf-long-native/20261007/analysis-summary.json">Later window evidence</a>; the completed run was numerically rejected, with unresolved source accounting and no inner-residual qualification. Bars are descriptive film transfers, not a closed separator mass balance.</li>
</ul><p><a href="poster-assets/wall-film-card-provenance.json">Figure provenance</a> · <a href="poster-assets/wall-film-behaviour-card.png">PNG export</a></p></details>'''
    page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wall-film behaviour — poster card</title><style>
{font_css}
*{{box-sizing:border-box}}body{{margin:0;background:#EAF0EF;color:{INK};font-family:'IBM Plex Sans',Arial,sans-serif}}main{{width:1100px;margin:0 auto}}.card{{background:white;padding:30px 36px 24px;display:flex;flex-direction:column;gap:17px;min-height:1420px}}header{{display:flex;justify-content:space-between;align-items:center;gap:20px}}h1{{font-family:'Barlow Semi Condensed',Arial,sans-serif;font-size:44px;line-height:1;margin:7px 0 0}}h2{{font-family:'Barlow Semi Condensed',Arial,sans-serif;font-size:27px;line-height:1.1;margin:0 0 8px}}p{{font-size:20px;line-height:1.35;margin:0}}.eyebrow{{font-family:'IBM Plex Mono',monospace;color:{TEAL};font-size:15px;font-weight:600;letter-spacing:.1em}}.badge{{background:#E4F0F1;padding:14px 20px;border-radius:10px;white-space:nowrap;text-align:right;font-family:'IBM Plex Mono',monospace;font-size:25px;color:{TEAL};font-weight:600}}.badge small{{display:block;font-family:'IBM Plex Sans',Arial,sans-serif;font-size:14px;font-weight:400;margin-top:4px}}.section{{border-top:1px solid #CBD7D5;padding-top:15px}}.native{{width:100%;height:390px;object-fit:contain;display:block}}.caption{{font-size:15px;line-height:1.35;color:#4A5D64}}.mechanisms{{display:grid;grid-template-columns:330px 1fr;gap:24px;align-items:center}}.paper{{width:330px;height:205px;object-fit:contain;display:block}}.model{{font-size:19px;line-height:1.35;margin:8px 0}}.model strong{{color:{TEAL}}}.rates{{display:grid;grid-template-columns:610px 1fr;gap:10px;align-items:start}}.rates img{{display:block;width:100%;height:262px;object-fit:contain}}.panel-title{{font-size:19px;font-weight:600;margin-bottom:3px}}.numbers{{font-family:'IBM Plex Mono',monospace;font-size:16px;color:{TEAL};margin:4px 0 7px}}.conclusion{{background:#E4F0F1;padding:15px 18px;border-left:4px solid {TEAL};font-size:21px;line-height:1.3}}.limit{{font-size:15px;color:#4A5D64;line-height:1.35}}details{{padding:22px 36px;background:white;margin:20px 0;font-size:16px;line-height:1.45}}details p{{font-size:16px}}details li{{margin:8px 0}}a{{color:{TEAL}}}@media(max-width:1100px){{main{{width:100%}}.card{{min-height:0}}.rates{{grid-template-columns:1fr}}.mechanisms{{grid-template-columns:1fr}}.paper{{margin:auto}}}}@media print{{body{{background:white}}main{{width:1100px}}details{{display:none}}}}
</style></head><body><main><article class="card" id="wall-film-card">
<header><div><div class="eyebrow">05 · WALL FILM</div><h1>Wall-film behaviour</h1></div><div class="badge">6.69 → 9.54 kg<small>early-run film mass · 265 → 500 ms</small></div></header>
<p>Wall liquid can spread, drain or return to the steam as droplets. Different runs reveal these different parts of its behaviour.</p>
<section class="section"><h2>1 · Film spreads and stores liquid</h2><p>Early runs showed a broader, thicker film over the lower and middle walls. The upper wall remained thinner.</p>
<img class="native" src="{data_uri(development_image)}" alt="Saved wall-film thickness at 5.90, 75.66 and 265.18 ms; native wall facets and shared 0–0.30 mm colour range.">
<p class="caption">Same camera and 0–0.30 mm scale. These early snapshots have release models OFF; the rate history continues to 500 ms.</p></section>
<section class="section"><h2>2 · Added models represent liquid returning to the flow</h2><div class="mechanisms"><figure style="margin:0">{image('wall-film-reentrainment-rizaldy-fig9.png','Undercut and roll-wave re-entrainment sketches from Rizaldy et al. (2016), Figure 9.','paper')}<figcaption class="caption">Steam removes droplets from film waves.<br>Rizaldy et al. (2016), Fig. 9, after Ishii &amp; Grolmes (1975).</figcaption></figure><div>
<p class="model"><strong>Stripping:</strong> steam shear removes film droplets. The literature sketch gives the physical rationale.</p>
<p class="model"><strong>Splashing:</strong> droplet impacts create more droplets. Added as a separate impact model.</p>
<p class="model"><strong>Edge separation:</strong> film leaves wall edges as droplets. Added as a separate edge model.</p>
<p class="caption">Later runs enabled these processes and droplet collection. They add liquid-transfer paths; they do not resolve every breakup event.</p></div></div></section>
<section class="section"><h2>3 · Rates distinguish drainage, release and accumulation</h2><div class="rates"><div><p class="panel-title">Early run · input, drainage and storage</p><p class="numbers">At 500 ms: 81.12 in · 69.60 drained · 11.53 stored kg/s</p>{image('wall-film-rates-early.png','Unsmooth early-run film input, native film drainage and storage rates through 500 ms.')}<p class="caption">Input exceeded drainage; film mass continued to rise.<br>Endpoint numbers are final-10-ms means.</p></div><div><p class="panel-title">Later run · release plus film absorber</p><p class="caption">Mean rates in a 75 ms window before the numerical guard.</p>{image('wall-film-rates-later.png','Later-run mean stripping, direct film absorber, native outflow, edge-separation and storage rates in a 75 ms pre-guard window.')}<p class="caption">Stripping and edge separation transfer liquid to the flow. The film absorber removes mass and momentum to represent entry into the brine pool. No isolated splash rate was recorded.</p></div></div></section>
<p class="conclusion"><strong>What we learnt:</strong> active lower-film removal can coexist with continued upper-film accumulation. Film growth, drainage and droplet release must be assessed together.</p>
<p class="limit">Two different model-development runs; bulk flow was frozen during these film windows. Steady film was not reached. The later run stopped at a numerical guard and retains source-accounting and inner-solve limits; its transfer rates do not establish separator efficiency.</p>
</article>{full_sources}</main></body></html>'''
    page = page.replace("@media(max-width:1100px)", "@media(max-width:1000px)")
    (ROOT / "Project/Poster/Wall_Film_Behaviour_Card.html").write_text(page)

    # Keep the main poster at its existing size; add a compact figure-led version.
    managed_keys = set()
    def bundle(name: str) -> str:
        path = ASSETS / name
        key = str(uuid.uuid5(uuid.NAMESPACE_URL, "p4p-poster-wall-film/" + name))
        managed_keys.add(key)
        manifest[key] = {"mime": "image/png", "compressed": True,
                         "data": base64.b64encode(gzip.compress(path.read_bytes(), mtime=0)).decode()}
        return key

    rate_id = bundle("wall-film-rates-compact.png")
    paper_id = bundle("wall-film-reentrainment-rizaldy-fig9b.png")
    thumbs = "".join(f'<div style="flex:1;min-width:0;text-align:center"><img src="{key}" style="width:100%;height:64px;object-fit:contain;display:block" alt="Early-run wall-film thickness at {time} ms, shared 0–0.30 mm scale"><div style="font-size:12px;line-height:1.15">{time} ms</div></div>' for key, time in zip(original_images, ["5.90", "75.66", "265.18"]))
    new_card = f'''<div style="box-sizing:border-box;background:#FFFFFF;border:1px solid #C4D1CE;border-radius:14px;padding:16px 22px;display:flex;flex-direction:column;gap:6px;min-width:0;min-height:0" data-original-node="132" data-card="05">
<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex:0 0 auto;height:42px"><div><div style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:12px;letter-spacing:.1em;color:#0B5F6B">05 · DEVELOPMENT + LIQUID TRANSFER</div><h2 style="margin:3px 0 0;font-family:'Barlow Semi Condensed',sans-serif;font-size:29px;line-height:1;color:#10222A">Wall-film behaviour</h2></div><div style="background:#E4F0F1;padding:7px 10px;border-radius:8px;text-align:right"><div style="font-family:'IBM Plex Mono',monospace;font-size:21px;font-weight:600;color:#0B5F6B">6.69 → 9.54 kg</div><div style="font-size:11px">film mass · 265 → 500 ms</div></div></div>
<p style="margin:0;font-size:14px;line-height:1.2;color:#4A5D64">Film spreads over the lower and middle walls. Later models add routes for liquid to return to the steam.</p>
<div style="display:flex;gap:14px;flex:1;min-height:0"><div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:3px"><div style="display:flex;gap:4px">{thumbs}</div><div style="font-size:12px;color:#4A5D64">Early run · film input, drainage and accumulation</div><img src="{rate_id}" alt="Early-run raw film mass rates through 500 ms" style="display:block;width:100%;height:100px;object-fit:contain"><div style="font-size:12px;line-height:1.25"><span style="color:#0B5F6B">81.12 in</span> · <span style="color:#D37B26">69.60 drained</span> · <span style="color:#7861A5">11.53 stored kg/s</span></div></div>
<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:4px"><img src="{paper_id}" style="width:100%;height:66px;object-fit:contain" alt="Roll-wave re-entrainment: steam shear lifts droplets from a wall film; Rizaldy et al. 2016 Fig.9b"><div style="font-size:11px;line-height:1.15;color:#4A5D64">Film-wave breakup · Rizaldy et al. (2016), Fig. 9b</div><div style="font-size:13px;line-height:1.23;display:flex;flex-direction:column;gap:4px"><p style="margin:0"><strong>Stripping:</strong> steam shear removes film droplets.</p><p style="margin:0"><strong>Splashing:</strong> impacts create more droplets.</p><p style="margin:0"><strong>Edge separation:</strong> film leaves wall edges.</p><p style="margin:0"><strong>Film absorber:</strong> removes mass and momentum at the lower collector.</p></div><p style="margin:0;font-size:12px;line-height:1.2;color:#4A5D64">Later run: lower-film removal stayed active while upper-film liquid accumulated.</p></div></div>
<p style="margin:0;font-size:11px;line-height:1.25;color:#4A5D64">Different runs; release models OFF in early images/rates. Bulk flow frozen; steady film not reached. Later run has numerical and accounting limits.</p></div>'''
    new_card = new_card.replace('height:100px;object-fit:contain', 'height:72px;object-fit:contain')
    updated_template = template[:start] + new_card + template[end:]
    old_manifest = json.loads(manifest_match.group(1))
    assert all(manifest[k] == v for k, v in old_manifest.items() if k not in managed_keys)
    assert updated_template[:start] == template[:start]
    assert updated_template[start + len(new_card):] == template[end:]
    updated = before[:template_match.start(1)] + json.dumps(updated_template, ensure_ascii=True).replace("</", "<\\/") + before[template_match.end(1):]
    updated_manifest_match = re.search(r'<script type="__bundler/manifest">(.*?)</script>', updated, re.S)
    updated = updated[:updated_manifest_match.start(1)] + json.dumps(manifest, separators=(",", ":")) + updated[updated_manifest_match.end(1):]
    POSTER.write_text(updated)

    provenance = {"early_spatial_figure": {"path": str(development_image.relative_to(ROOT)), "sha256": digest(development_image), "snapshots_ms": [5.904, 75.662, 265.184], "colour_range_mm": [0, 0.30]},
                  "early_rates": {"path": str(csv_path.relative_to(ROOT)), "sha256": digest(csv_path), "transformation": "Raw accepted-time history; storage = per-step native inventory difference / accepted film step; no smoothing", "final_10ms": final},
                  "later_rates": {"path": str(later_path.relative_to(ROOT)), "sha256": digest(later_path), "window": later["pre_guard_last_75ms"], "mean_rates_kg_s": later_rates, "claim_limit": "Descriptive separate run, later rejected; frozen bulk; accounting/inner convergence unresolved; no efficiency claim"},
                  "literature_figure": {"path": str(pdf.relative_to(ROOT)), "sha256": pdf_hash, "pdf_page": 5, "figure": "9 and 9b", "credit": "Rizaldy et al. (2016), after Ishii and Grolmes (1975)", "poppler_dpi": 300, "clip_pixels": {"fig9": [1288, 260, 920, 570], "fig9b": [1288, 570, 920, 260]}, "supports": "Steam shear and wall-film wave breakup; qualitative stripping rationale", "does_not_demonstrate": ["particle-impact splashing", "sharp-edge film separation", "project CFD breakup prediction"]},
                  "build_script": str(Path(__file__).relative_to(ROOT)), "new_solve_calls": 0,
                  "main_poster_change": "Only card 05 template changed; existing manifest entries preserved; two new PNG entries added"}
    (ASSETS / "wall-film-card-provenance.json").write_text(json.dumps(provenance, indent=2))
    print("Built standalone card, compact card 05, rate plots and literature crops. No Fluent calls.")
    print("Final early rates:", final)
    print("Later pre-guard transfer rates:", later_rates)


if __name__ == "__main__":
    main()
