#!/usr/bin/env python3
"""Build matched setup-07c/07e spatial composites from verified Fluent exports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
FLUENT = OUTPUT / "fluent"
SETUP07C = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)
SETUP07E = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)

NAVY = "#14324A"
GREY = "#5C6770"
RED = "#B42318"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def endpoint_07c() -> dict[str, float]:
    with (SETUP07C / "physical_monitor_history.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    full_strength = [row for row in rows if float(row["r1_iteration"]) > 0]
    row = max(full_strength, key=lambda item: float(item["r1_iteration"]))
    numeric: dict[str, float] = {}
    for key, value in row.items():
        if value in ("", None):
            continue
        try:
            numeric[key] = float(value)
        except ValueError:
            # History rows also contain labels such as ``ramp_1.00_resume``.
            # The spatial captions only consume numeric monitor fields.
            continue
    return numeric


def endpoint_07e() -> dict[str, Any]:
    path = SETUP07E / "QUALIFICATION_RESULT.json"
    if not path.exists():
        raise RuntimeError("Setup-07e terminal analysis is not available")
    result = load_json(path)
    if not result.get("final"):
        raise RuntimeError("Setup-07e analysis is not terminal")
    return result["endpoint"]


def verify_graphics_manifest() -> dict[str, Any]:
    path = FLUENT / "fluent_graphics_manifest.json"
    manifest = load_json(path)
    state = manifest.get("states", {}).get("sink07e")
    if not state:
        raise RuntimeError("Verified sink07e Fluent graphics state is missing")
    dpm_state = state.get("dpm_interaction", {}).get("state", {})
    if bool(dpm_state.get("enabled")):
        raise RuntimeError("DPM was enabled in the sink07e graphics state")
    restore = manifest.get("restore", {})
    if not restore.get("ok"):
        raise RuntimeError("Setup-07e ramp-zero restore was not verified")
    restore_key = restore.get("state", {}).get("key")
    if restore_key != "sink07e_ramp_reset_final":
        raise RuntimeError(f"Unexpected restored state: {restore_key!r}")
    return manifest


def load_crop(name: str) -> Image.Image:
    path = FLUENT / name
    if not path.exists():
        raise FileNotFoundError(path)
    image = Image.open(path).convert("RGB")
    if image.size != (1920, 1440):
        raise RuntimeError(f"Unexpected image size for {path}: {image.size}")
    return image.crop((0, 245, 1210, 1110))


def save(figure: plt.Figure, stem: str) -> dict[str, str]:
    paths: dict[str, str] = {}
    for suffix in ("png", "svg"):
        path = OUTPUT / f"{stem}.{suffix}"
        figure.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
        paths[suffix] = str(path)
    plt.close(figure)
    return paths


def pair(
    left: Image.Image,
    right: Image.Image,
    *,
    title: str,
    subtitle: str,
    left_title: str,
    right_title: str,
    footer: str,
    stem: str,
) -> dict[str, str]:
    figure, axes = plt.subplots(1, 2, figsize=(15.0, 7.6), constrained_layout=True)
    figure.suptitle(title, fontsize=22, color=NAVY, fontweight="bold")
    figure.text(0.5, 0.925, subtitle, ha="center", va="top", fontsize=12, color=GREY)
    for axis, image, heading in zip(
        axes, (left, right), (left_title, right_title), strict=True
    ):
        axis.imshow(image)
        axis.set_title(heading, fontsize=15, color=NAVY, fontweight="bold", pad=10)
        axis.axis("off")
    figure.text(0.5, 0.012, footer, ha="center", va="bottom", fontsize=11, color=GREY)
    return save(figure, stem)


def update_manifest(
    artifacts: dict[str, dict[str, str]], graphics: dict[str, Any]
) -> None:
    path = OUTPUT / "visual_manifest.json"
    manifest = load_json(path)
    manifest.setdefault("artifacts", {}).update(artifacts)
    manifest.setdefault("source_files", [])
    for source in (
        SETUP07C / "physical_monitor_history.csv",
        SETUP07E / "QUALIFICATION_RESULT.json",
        FLUENT / "fluent_graphics_manifest.json",
    ):
        if str(source) not in manifest["source_files"]:
            manifest["source_files"].append(str(source))
    accepted = manifest.setdefault("accepted_fluent_exports", [])
    graphics_state = graphics["states"]["sink07e"].get("graphics", {})
    for record in graphics_state.values():
        if not record.get("ok"):
            continue
        picture = record.get("picture") or {}
        local_png = picture.get("local_png")
        if not local_png or not Path(local_png).exists():
            continue
        if local_png not in accepted:
            accepted.append(local_png)
    manifest.setdefault("graphics_provenance", {}).update(
        {
            "setup07e_state": graphics["states"]["sink07e"]["title"],
            "setup07e_final_live_state": (
                "setup-07e saved ramp-reset final restored; DPM read back off"
            ),
        }
    )
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    graphics = verify_graphics_manifest()
    c = endpoint_07c()
    e = endpoint_07e()
    artifacts = {
        "setup07c_setup07e_liquid_field_comparison": pair(
            load_crop("sink07c_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png"),
            load_crop("sink07e_phase2_liquid_volume_fraction_zoom0p05_xm1p5.png"),
            title="Fixed and adaptive local sinks produce different unresolved liquid fields",
            subtitle=(
                "Same 900k mesh, x = -1.5 m section, cell values, and liquid volume-fraction range 0-0.05"
            ),
            left_title=(
                f"07c fixed tau=0.10 s | sink {c['sink_magnitude_kgs']:.2f} kg/s | "
                f"inventory {c['domain_liquid_inventory_kg']:.2f} kg"
            ),
            right_title=(
                f"07e adaptive tau={e['tau_s']:.3f} s | sink {e['sink_magnitude_kgs']:.2f} kg/s | "
                f"inventory {e['domain_liquid_inventory_kg']:.2f} kg"
            ),
            footer=(
                "Matched full-strength endpoints. The clipped scale reveals low-volume liquid structure; both states are diagnostic/unresolved and do not represent outlet hydraulics."
            ),
            stem="22_setup07c_setup07e_liquid_field_comparison",
        ),
        "setup07c_setup07e_pressure_field_comparison": pair(
            load_crop("sink07c_static_pressure_xm1p5.png"),
            load_crop("sink07e_static_pressure_xm1p5.png"),
            title="Pressure field remains dependent on the numerical sink strategy",
            subtitle=(
                "Same 900k mesh, x = -1.5 m section, cell values, and absolute static-pressure range 1.10-1.20 MPa"
            ),
            left_title=f"07c fixed tau=0.10 s | pressure drop {c['pressure_drop_pa'] / 1000.0:.2f} kPa",
            right_title=f"07e adaptive control | pressure drop {e['pressure_drop_kpa']:.2f} kPa",
            footer=(
                "A source-law-dependent pressure field is diagnostic evidence that the local sink is not a physical brine-outlet boundary; no mesh-independence claim follows."
            ),
            stem="23_setup07c_setup07e_pressure_field_comparison",
        ),
    }
    update_manifest(artifacts, graphics)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
