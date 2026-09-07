#!/usr/bin/env python3
"""Build report-ready composites from the preserved setup-07n Fluent PNGs."""

from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_LABEL = "brine620k_07n_a_server2_independent_stillpool_figures_attempt1_20260825"
SOURCE = PROJECT_ROOT / "output" / "split_inlet_resolved_brine_outlet_20260813" / RUN_LABEL
OUTPUT = SOURCE / "composites_attempt3"
MANIFEST = OUTPUT / "composite_manifest.json"

CROP = (0, 250, 1150, 1000)
PANEL_WIDTH = 760
PANEL_HEIGHT = 555
HEADER_HEIGHT = 78
FOOTER_HEIGHT = 112
GAP = 20
BACKGROUND = "white"
TEXT = (25, 32, 42)
MUTED = (74, 85, 104)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE_FONT = font(30, bold=True)
PANEL_FONT = font(24, bold=True)
FOOTER_FONT = font(19)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def panel(filename: str, label: str) -> Image.Image:
    source = SOURCE / filename
    with Image.open(source) as raw:
        cropped = raw.convert("RGB").crop(CROP)
    cropped.thumbnail((PANEL_WIDTH, PANEL_HEIGHT), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (PANEL_WIDTH, PANEL_HEIGHT + 44), BACKGROUND)
    x = (PANEL_WIDTH - cropped.width) // 2
    canvas.paste(cropped, (x, 44))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 7), label, font=PANEL_FONT, fill=TEXT)
    return canvas


def make_composite(
    output_name: str,
    title: str,
    panels: list[tuple[str, str]],
    footer: str,
) -> dict[str, object]:
    output_path = OUTPUT / output_name
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite composite: {output_path}")
    rendered = [panel(filename, label) for filename, label in panels]
    width = len(rendered) * PANEL_WIDTH + (len(rendered) - 1) * GAP
    height = HEADER_HEIGHT + max(image.height for image in rendered) + FOOTER_HEIGHT
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 19), title, font=TITLE_FONT, fill=TEXT)
    y = HEADER_HEIGHT
    x = 0
    for image in rendered:
        canvas.paste(image, (x, y))
        x += PANEL_WIDTH + GAP
    draw.line((0, height - FOOTER_HEIGHT, width, height - FOOTER_HEIGHT), fill=(210, 215, 222), width=2)
    wrapped_footer = "\n".join(textwrap.wrap(footer, width=120))
    draw.multiline_text(
        (18, height - FOOTER_HEIGHT + 14),
        wrapped_footer,
        font=FOOTER_FONT,
        fill=MUTED,
        spacing=4,
    )
    canvas.save(output_path, format="PNG", optimize=True)
    return {
        "path": str(output_path),
        "sha256": sha256(output_path),
        "dimensions": list(canvas.size),
        "source_files": [filename for filename, _ in panels],
        "title": title,
        "footer": footer,
    }


def main() -> int:
    OUTPUT.mkdir(parents=False, exist_ok=False)
    common = (
        "Independent server-2 setup-07n reconstruction; zero inlet flow and closed brine wall. "
        "Cell-centred values. Not accepted setup-07l or an operating separator result."
    )
    records = [
        make_composite(
            "figure01_liquid_pool_t0_vs_10us.png",
            "First still-pool startup: liquid volume fraction",
            [
                ("t0_brine_axis_x0p714343_phase_2_vof_range0to1.png", "Patched pool: t = 0"),
                (
                    "startup_step10_10us_brine_axis_x0p714343_phase_2_vof_range0to1.png",
                    "After 10 × 1 µs steps: t = 10 µs",
                ),
            ],
            common + " The red region is liquid (alpha_l=1); blue is vapour (alpha_l=0).",
        ),
        make_composite(
            "figure02_modified_pressure_t0_vs_10us.png",
            "First still-pool startup: Fluent pressure field",
            [
                ("t0_brine_axis_x0p714343_pressure_range1120to1133kpa.png", "Patched pool: t = 0"),
                (
                    "startup_step10_10us_brine_axis_x0p714343_pressure_range1120to1133kpa.png",
                    "After 10 × 1 µs steps: t = 10 µs",
                ),
            ],
            common + " Fixed 1.120-1.133 MPa scale; this CFD pressure is not a validated plant boundary.",
        ),
        make_composite(
            "figure03_velocity_t0_vs_10us.png",
            "First still-pool startup: velocity magnitude",
            [
                (
                    "t0_brine_axis_x0p714343_velocity_magnitude_range0to7em5ms.png",
                    "Patched pool: t = 0",
                ),
                (
                    "startup_step10_10us_brine_axis_x0p714343_velocity_magnitude_range0to7em5ms.png",
                    "After 10 × 1 µs steps: t = 10 µs",
                ),
            ],
            common + " Fixed 0-7e-5 m/s scale; motion is gravity-driven startup adjustment.",
        ),
        make_composite(
            "figure04_liquid_pool_t0_10us_5p11ms.png",
            "Independent closed-pool reconstruction: liquid seal persistence",
            [
                ("t0_brine_axis_x0p714343_phase_2_vof_range0to1.png", "t = 0"),
                (
                    "startup_step10_10us_brine_axis_x0p714343_phase_2_vof_range0to1.png",
                    "t = 10 µs",
                ),
                (
                    "lastclean_step90_5p11ms_brine_axis_x0p714343_phase_2_vof_range0to1.png",
                    "Last clean state: t = 5.11 ms",
                ),
            ],
            common + " The liquid-covered brine-leg entrance persists, but drainage was not enabled.",
        ),
        make_composite(
            "figure05_last_clean_pressure_and_velocity.png",
            "Last clean independent state at t = 5.11 ms",
            [
                (
                    "lastclean_step90_5p11ms_brine_axis_x0p714343_pressure_range1120to1133kpa.png",
                    "Fluent pressure: 1.120-1.133 MPa",
                ),
                (
                    "lastclean_step90_5p11ms_brine_axis_x0p714343_velocity_magnitude_range0to0p025ms.png",
                    "Velocity magnitude: 0-0.025 m/s",
                ),
            ],
            common + " This is about 0.119 local gravity times and is not a fully relaxed endpoint.",
        ),
    ]
    payload = {
        "schema_version": 1,
        "classification": "diagnostic post-processing only",
        "source_run_label": RUN_LABEL,
        "crop_box_raw_pixels": list(CROP),
        "raw_images_preserved": True,
        "supersedes_composites_directories": ["composites", "composites_attempt2"],
        "excluded_raw_view": {
            "plane": "vessel_axis_xm1p5",
            "reason": (
                "The x=-1.5 m section does not intersect the selected pool in "
                "this geometry and is retained only as raw evidence, not used "
                "for interpretation."
            ),
        },
        "composites": records,
    }
    with MANIFEST.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")
    print(MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
