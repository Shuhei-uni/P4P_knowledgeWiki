#!/usr/bin/env python3
"""Build the five-page setup-07 supervisor meeting report.

The report is deliberately short enough for a ten-minute walkthrough. It uses
only figures and terminal metrics already accepted in the setup-07 evidence
package; it does not run Fluent or alter any CFD state.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "output" / "setup07_meeting_visuals_20260811"
OUTPUT = ROOT / "output" / "pdf" / "setup07_condensed_meeting_report_20260811.pdf"

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 32

INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5F6B78")
BLUE = colors.HexColor("#1672B8")
BLUE_DARK = colors.HexColor("#0B4F7F")
BLUE_LIGHT = colors.HexColor("#EAF3FA")
ORANGE = colors.HexColor("#D97700")
ORANGE_LIGHT = colors.HexColor("#FFF1DF")
GREY = colors.HexColor("#D7DDE3")
GREY_LIGHT = colors.HexColor("#F4F6F8")
RED = colors.HexColor("#A94332")
WHITE = colors.white


def set_font(c: canvas.Canvas, size: float, *, bold: bool = False, color=INK) -> None:
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.setFillColor(color)


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    size: float,
    *,
    leading: float | None = None,
    bold: bool = False,
    color=INK,
    max_lines: int | None = None,
) -> float:
    leading = leading or size * 1.25
    font = "Helvetica-Bold" if bold else "Helvetica"
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines is not None:
        lines = lines[:max_lines]
    set_font(c, size, bold=bold, color=color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullets(
    c: canvas.Canvas,
    items: list[str],
    x: float,
    y: float,
    width: float,
    size: float = 9.2,
    leading: float = 12.0,
    color=INK,
) -> float:
    for item in items:
        c.setFillColor(BLUE)
        c.circle(x + 3, y + 3, 1.7, fill=1, stroke=0)
        y = draw_wrapped(c, item, x + 12, y, width - 12, size, leading=leading, color=color)
        y -= 3
    return y


def rounded_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill, stroke=GREY, radius=8) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def draw_image_fit(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(ImageReader(str(path)), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")


def page_header(c: canvas.Canvas, section: str, title: str, subtitle: str | None = None) -> None:
    c.setFillColor(BLUE)
    c.rect(0, PAGE_H - 7, PAGE_W, 7, fill=1, stroke=0)
    set_font(c, 8.5, bold=True, color=BLUE)
    c.drawString(MARGIN, PAGE_H - 27, section.upper())
    set_font(c, 22, bold=True)
    c.drawString(MARGIN, PAGE_H - 55, title)
    if subtitle:
        set_font(c, 9.5, color=MUTED)
        c.drawString(MARGIN, PAGE_H - 72, subtitle)


def page_footer(c: canvas.Canvas, number: int, source: str) -> None:
    c.setStrokeColor(GREY)
    c.line(MARGIN, 27, PAGE_W - MARGIN, 27)
    set_font(c, 7.2, color=MUTED)
    page_label = f"Page {number} | 10-minute meeting report"
    label_width = stringWidth(page_label, "Helvetica", 7.2)
    source_width = PAGE_W - 2 * MARGIN - label_width - 20
    draw_wrapped(c, source, MARGIN, 15, source_width, 7.2, max_lines=1, color=MUTED)
    c.drawRightString(PAGE_W - MARGIN, 15, page_label)


def metric_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, value: str, label: str, accent=BLUE) -> None:
    rounded_box(c, x, y, w, h, GREY_LIGHT, GREY)
    c.setFillColor(accent)
    c.rect(x, y, 4, h, fill=1, stroke=0)
    set_font(c, 16, bold=True, color=accent)
    c.drawString(x + 12, y + h - 23, value)
    draw_wrapped(c, label, x + 12, y + h - 39, w - 20, 7.5, leading=9.0, color=MUTED, max_lines=2)


def build() -> None:
    required = {
        "summary": FIGURES / "27_tuesday_brine_outlet_action_summary.png",
        "closed": FIGURES / "01_closed_bottom_inventory_pressure.png",
        "pathways": FIGURES / "21_setup07_liquid_pathway_accounting.png",
        "residual": FIGURES / "15_setup07e_adaptive_residual_history.png",
        "plan": FIGURES / "25_brine_outlet_boundary_condition_decision.png",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing accepted report figure(s): {missing}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("Setup 07 CFD Diagnostic - Condensed Supervisor Meeting Report")
    c.setAuthor("P4P geothermal separator CFD project")
    c.setSubject("Ten-minute technical decision report for the setup-07 carrier and liquid-outlet diagnostics")

    # Page 1 - decision.
    page_header(
        c,
        "1. Decision - 1 minute",
        "Geothermal Separator CFD: Resolve the Brine Outlet Next",
        "Condensed supervisor report | setup 07a-07e carrier diagnostics | Fluent 2024 R2",
    )
    rounded_box(c, 32, 447, 244, 68, BLUE_LIGHT, BLUE)
    set_font(c, 10.5, bold=True, color=BLUE_DARK)
    c.drawString(46, 493, "RECOMMENDED DECISION")
    draw_wrapped(
        c,
        "Add a resolved brine pipe and qualify one 900k carrier case before repeating mesh convergence, DPM or EWF.",
        46,
        475,
        214,
        10.2,
        leading=13.2,
        bold=True,
    )
    metric_card(c, 32, 372, 116, 60, "7 meshes", "Formal carrier runs completed", BLUE)
    metric_card(c, 160, 372, 116, 60, "+64.4%", "Liquid inventory, iter 4000-6000", BLUE)
    metric_card(c, 32, 300, 116, 60, "43.6%", "Best represented liquid route", ORANGE)
    metric_card(c, 160, 300, 116, 60, "0 windows", "Full convergence gates passed", RED)
    rounded_box(c, 32, 88, 244, 192, GREY_LIGHT, GREY)
    set_font(c, 10.5, bold=True)
    c.drawString(46, 258, "What the evidence says")
    draw_bullets(
        c,
        [
            "The closed-bottom steady field keeps filling and redistributing liquid.",
            "Local volumetric sinks improve removal but do not supply outlet hydraulics.",
            "Residuals and physical monitors do not establish iteration independence.",
            "Current steam quality and carryover remain trend-only, not validated efficiency.",
        ],
        46,
        238,
        214,
        size=8.6,
        leading=10.7,
    )
    draw_image_fit(c, required["summary"], 292, 69, 517, 446)
    page_footer(c, 1, "Evidence: setup-07 qualification manifests, saved Fluent checkpoints and terminal analysis.")
    c.showPage()

    # Page 2 - iteration independence.
    page_header(
        c,
        "2. Baseline limitation - 2 minutes",
        "The Closed-Bottom Carrier Field Never Became Iteration-Independent",
        "Same 900k mesh and physics; DPM off; saved states at iterations 4000-6000",
    )
    draw_image_fit(c, required["closed"], 42, 142, 758, 365)
    rounded_box(c, 42, 45, 758, 83, GREY_LIGHT, GREY)
    set_font(c, 10, bold=True)
    c.drawString(58, 108, "Interpretation")
    draw_bullets(
        c,
        [
            "Liquid inventory increased from 104.05 to 171.03 kg (+64.4%), while pressure drop increased from 31.03 to 34.05 kPa (+9.7%).",
            "Within-run drift is larger than or comparable with mesh-to-mesh changes, so Richardson extrapolation and GCI are not defensible.",
            "Solver iteration is not physical time: this is evidence of a changing steady iterate, not a measured accumulation rate.",
        ],
        58,
        91,
        724,
        size=8.4,
        leading=10.2,
    )
    page_footer(c, 2, "Figure source: setup-07a 900k extension, saved case/data and physical-monitor histories.")
    c.showPage()

    # Page 3 - source strategy comparison.
    page_header(
        c,
        "3. Sink sensitivity - 2 minutes",
        "Every Tested Local Sink Leaves a Large Unclosed Liquid Route",
        "Common liquid feed 116.92 kg/s; same clean 900k carrier lineage for sink cases; DPM off",
    )
    draw_image_fit(c, required["pathways"], 32, 73, 620, 448)
    rounded_box(c, 665, 91, 145, 412, ORANGE_LIGHT, ORANGE)
    set_font(c, 10.2, bold=True, color=ORANGE)
    c.drawString(678, 479, "Endpoint result")
    for y, value, label in [
        (438, "8.8%", "07b one-cell sink"),
        (382, "19.2%", "07c thick sink"),
        (326, "40.2%", "07d strong sink"),
        (270, "43.6%", "07e adaptive sink"),
    ]:
        set_font(c, 17, bold=True, color=ORANGE)
        c.drawString(678, y, value)
        draw_wrapped(c, label, 678, y - 14, 118, 7.9, leading=9.2, color=MUTED)
    c.setStrokeColor(colors.HexColor("#E7B36F"))
    c.line(678, 235, 797, 235)
    draw_wrapped(
        c,
        "The adaptive source reached its minimum tau but removed only 50.954 kg/s. Its band held 0.1019 kg liquid versus 0.2338 kg required for the commanded rate.",
        678,
        214,
        118,
        8.1,
        leading=10.0,
        bold=True,
        color=INK,
    )
    draw_wrapped(
        c,
        "This is a numerical capacity limit, not a drain characteristic.",
        678,
        124,
        118,
        7.8,
        leading=9.5,
        color=MUTED,
    )
    page_footer(c, 3, "Figure source: corrected source-inclusive liquid accounting for setup 07a-07e endpoints.")
    c.showPage()

    # Page 4 - residuals and method scope.
    page_header(
        c,
        "4. Acceptance gate - 2 minutes",
        "The Adaptive Run Still Fails Residual and Physical-Monitor Stability",
        "Setup 07e completed 3000 cumulative / 2000 full-strength iterations; zero accepted windows",
    )
    draw_image_fit(c, required["residual"], 32, 176, 558, 318)
    rounded_box(c, 606, 176, 204, 318, GREY_LIGHT, GREY)
    set_font(c, 10.2, bold=True)
    c.drawString(620, 470, "Terminal setup 07e")
    rows = [
        ("Sink", "50.954 kg/s"),
        ("Liquid imbalance", "56.42%"),
        ("Pressure drop", "26.725 kPa"),
        ("Liquid inventory", "65.008 kg"),
        ("Continuity", "0.254617"),
        ("Liquid VF residual", "7.53e-4"),
    ]
    y = 438
    for label, value in rows:
        set_font(c, 8.2, color=MUTED)
        c.drawString(620, y, label)
        set_font(c, 9.4, bold=True)
        c.drawRightString(795, y, value)
        c.setStrokeColor(GREY)
        c.line(620, y - 7, 795, y - 7)
        y -= 36
    rounded_box(c, 620, 194, 175, 51, ORANGE_LIGHT, ORANGE)
    set_font(c, 8.2, bold=True, color=ORANGE)
    c.drawString(632, 225, "FINAL-500 DRIFT")
    draw_wrapped(c, "Pressure 5.85% | sink 26.19% | inventory 13.35%", 632, 210, 150, 7.6, leading=9.0, color=INK)
    rounded_box(c, 32, 49, 778, 108, BLUE_LIGHT, BLUE)
    set_font(c, 9.6, bold=True, color=BLUE_DARK)
    c.drawString(47, 136, "Controlled model scope")
    draw_wrapped(
        c,
        "Steady pressure-based Mixture model; vapor primary and liquid secondary; RNG k-epsilon; gravity (0, -9.81, 0); Energy off; SIMPLE/PRESTO; liquid/vapor feeds 116.92/80.69 kg/s; steam outlet 1.12 MPa; bottom remains a wall; DPM/EWF off.",
        47,
        119,
        748,
        8.3,
        leading=10.4,
    )
    draw_wrapped(
        c,
        "Acceptance required complete mass closure, stable pressure/inventory/velocity/swirl, and acceptable residual level and trend. Stable vapor throughput alone is insufficient.",
        47,
        81,
        748,
        8.3,
        leading=10.4,
        bold=True,
    )
    page_footer(c, 4, "Figure source: setup-07e complete residual history and terminal qualification result.")
    c.showPage()

    # Page 5 - decision and next questions.
    page_header(
        c,
        "5. Recommended rebuild - 3 minutes",
        "Add a Resolved Brine Pipe and Qualify One Medium Mesh First",
        "The next run should answer outlet hydraulics and steady mass closure - not tune another local sink",
    )
    draw_image_fit(c, required["plan"], 32, 162, 526, 330)
    rounded_box(c, 575, 162, 235, 330, BLUE_LIGHT, BLUE)
    set_font(c, 10.3, bold=True, color=BLUE_DARK)
    c.drawString(590, 466, "Proposed first qualification")
    y = draw_bullets(
        c,
        [
            "Create a resolved brine pipe and named brine-outlet face away from vessel recirculation.",
            "Use a pressure outlet first when downstream static pressure is defensible; let Fluent solve the discharge rate.",
            "Use 116.92 kg/s mass-flow outlet only as a strictly outward diagnostic bracket.",
            "Freshly initialize the 900k mesh and retain the accepted carrier physics and convergence gates.",
            "Repeat the mesh ladder only after two accepted iteration-stability windows.",
        ],
        590,
        440,
        200,
        size=8.5,
        leading=10.7,
    )
    set_font(c, 9.4, bold=True, color=ORANGE)
    c.drawString(590, y - 4, "Do not add DPM or EWF yet.")
    rounded_box(c, 32, 45, 778, 100, GREY_LIGHT, GREY)
    set_font(c, 9.8, bold=True)
    c.drawString(47, 124, "Decisions requested from supervisors")
    draw_bullets(
        c,
        [
            "Confirm the physical drain location, target water level and available downstream brine pressure.",
            "Confirm a preliminary outlet size. Continuity-only envelope: equivalent circular diameter 0.411, 0.291 or 0.237 m at mean liquid velocity 1, 2 or 3 m/s.",
            "Approve pressure-outlet first qualification and the rule that mesh/DPM/EWF work remains blocked until carrier closure and stability pass.",
        ],
        47,
        106,
        748,
        size=8.2,
        leading=10.0,
    )
    page_footer(c, 5, "Plan basis: Fluent 2024 R2 boundary guidance plus project operating conditions; sizing is preliminary only.")
    c.save()


if __name__ == "__main__":
    build()
    print(OUTPUT)
