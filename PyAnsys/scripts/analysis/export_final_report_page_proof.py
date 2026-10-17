#!/usr/bin/env python3
"""Render a review proof with one reserved page for final-model mesh sensitivity.

This is a layout check, not the submission document. Scientific text and image
pixels come from the current Markdown and source assets. Only presentation is
transformed: redundant Part headings and automatic alt-text captions are removed,
table widths are assigned, and the mesh-comparison allowance is made explicit.
Requires pandoc, tectonic, pdfinfo and pdftotext on PATH; no Fluent session.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess


REPO = Path(__file__).resolve().parents[3]
REPORT = REPO / "Project/Final research report/Shuhei Report"
SOURCES = [
    REPORT / "draft/01-introduction-and-literature-review.md",
    REPORT / "draft/02-03-model-development-methods-and-results.md",
    REPORT / "draft/04-discussion-conclusions-and-future-work.md",
]

# Widths in centimetres. Wide multipanel fields stay at the full 16 cm text width.
IMAGE_WIDTHS = {
    "report-liquid-destinations-overview.png": 16.0,
    "rizaldy-2016-figure-5-operation.png": 7.0,
    "zarrouk-purnanto-2015-figure-12-breakdown.png": 10.0,
    "pointon-2009-figure-5-inlets.png": 10.0,
    "pointon-2009-figure-7-velocity.png": 10.0,
    "rizaldy-2016-figure-9-entrainment.png": 10.0,
    "model-domain-overview.png": 13.0,
    "results-described-early-development.png": 12.0,
    "results-described-startup.png": 16.0,
    "results-film-development-reference500ms.png": 16.0,
    "results-described-roughness.png": 14.0,
    "results-described-film-outlet.png": 14.0,
    "bulk-comparison-described-film-treatment.png": 14.0,
    "results-direct-film-drain.png": 14.0,
}
TABLE_WIDTHS = {
    "Study / context": [0.26, 0.22, 0.23, 0.29],
    "Phase": [0.27, 0.31, 0.42],
    "Boundary": [0.22, 0.28, 0.25, 0.25],
    "Comparison": [0.25, 0.27, 0.29, 0.19],
    "Quantity|Mixed feed": [0.56, 0.21, 0.23],
    "Cells": [0.19, 0.37, 0.44],
    "Measure": [0.43, 0.20, 0.20, 0.17],
    "Film time (ms)": [0.17, 0.16, 0.16, 0.16, 0.16, 0.19],
    "Quantity|Drain OFF": [0.56, 0.22, 0.22],
    "Fluid cells": [0.14, 0.16, 0.17, 0.16, 0.20, 0.17],
    "Research question": [0.22, 0.42, 0.36],
}

HEADER = r"""\usepackage{setspace}
\usepackage{graphicx}
\usepackage{booktabs,array}
\setstretch{1.15}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt plus 1pt}
\usepackage{titlesec}
\titleformat{\section}{\large\bfseries}{}{0pt}{}
\titleformat{\subsection}{\normalsize\bfseries}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{0.25\baselineskip}{0.2\baselineskip}
\titlespacing*{\subsection}{0pt}{0pt}{0pt}
\titlespacing*{\subsubsection}{0pt}{0pt}{0pt}
\usepackage{caption}
\captionsetup{font=small,labelfont=bf,width=0.95\linewidth,justification=centering,skip=3pt}
\usepackage{enumitem}
\setlist{nosep,topsep=2pt}
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{6pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.1}
\renewcommand{\floatpagefraction}{0.75}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{5}
\newcommand{\proofslot}[2]{\par\noindent\fbox{\parbox[c][#1][c]{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{\centering #2}}\par}
\newcommand{\proofpage}{\noindent\textbf{Mesh-sensitivity results: one-page allowance}\par\medskip}
"""


def run(args: list[str], *, data: str | None = None, cwd: Path | None = None) -> str:
    completed = subprocess.run(args, input=data, text=True, capture_output=True, cwd=cwd, check=True)
    return completed.stdout


def raw(value: str) -> dict:
    return {"t": "RawBlock", "c": ["latex", value]}


def plain(value: object) -> str:
    if isinstance(value, list):
        return "".join(plain(item) for item in value)
    if not isinstance(value, dict):
        return ""
    if value.get("t") == "Str":
        return value["c"]
    if value.get("t") in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if value.get("t") in ("Code", "Math"):
        return value["c"][1]
    if value.get("t") in ("Link", "Image"):
        return plain(value["c"][1])
    return plain(value.get("c", []))


def latex_blocks(blocks: list[dict], api_version: list[int]) -> str:
    doc = {"pandoc-api-version": api_version, "meta": {}, "blocks": blocks}
    return run(["pandoc", "-f", "json", "-t", "latex"], data=json.dumps(doc)).strip()


def caption_inlines(block: dict) -> list[dict]:
    inlines = block["c"]
    if len(inlines) == 1 and inlines[0]["t"] == "Emph":
        return inlines[0]["c"]
    return inlines


def walk_images(value: object) -> list[dict]:
    found = []
    if isinstance(value, dict):
        if value.get("t") == "Image":
            found.append(value)
        else:
            found.extend(walk_images(value.get("c", [])))
    elif isinstance(value, list):
        for item in value:
            found.extend(walk_images(item))
    return found


def image_tex(image: dict, source: Path) -> tuple[str, Path]:
    path = (source.parent / image["c"][2][0]).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    width = IMAGE_WIDTHS.get(path.name, 16.0)
    return rf"\includegraphics[width={width:g}cm]{{\detokenize{{{path}}}}}", path


def table_tex(block: dict, number: int, api_version: list[int]) -> str:
    """Use an unsplit tabular: these short tables do not need longtable breaks."""
    headers = [plain(cell[4]).strip() for cell in block["c"][3][1][0][1]]
    key = headers[0] if headers[0] != "Quantity" else "|".join(headers[:2])
    widths = TABLE_WIDTHS[key]
    if len(widths) != len(block["c"][2]):
        raise ValueError(f"Table {number}: column count changed; revise its layout")
    padding_cm = 2 * (len(widths) - 1) * 4 / 72.27 * 2.54 / len(widths)
    specs = []
    for spec, fraction in zip(block["c"][2], widths):
        align = "\\raggedleft" if spec[0]["t"] == "AlignRight" else "\\raggedright"
        specs.append(r">{" + align + r"\arraybackslash}p{" + f"{16 * fraction - padding_cm:.5f}cm" + "}")
    rows = []
    head = block["c"][3][1]
    bodies = block["c"][4]
    for row in head:
        cells = [latex_blocks(cell[4], api_version) for cell in row[1]]
        rows.append(" & ".join(r"\textbf{" + cell + "}" for cell in cells) + r" \\")
    rows.append(r"\midrule")
    for body in bodies:
        for row in body[3]:
            cells = [latex_blocks(cell[4], api_version) for cell in row[1]]
            rows.append(" & ".join(cells) + r" \\")
    return (r"{\setlength{\tabcolsep}{4pt}\begin{tabular}{@{}" + "".join(specs) + r"@{}}"
            + "\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}}")


def mesh_comparison_page(blocks: list[dict]) -> list[dict]:
    """Keep the concise pending comparison and one figure slot on one page."""
    reserved = [raw("\\clearpage\n\\proofpage")]
    figure_slots = 0
    for block in blocks:
        if block["t"] == "RawBlock" and block["c"][0] == "html":
            continue
        reserved.append(block)
        if block["t"] == "BlockQuote" and plain(block).startswith("Figure 18 reserved"):
            reserved.append(raw(r"\proofslot{9.0cm}{Figure 18: final-model mesh sensitivity.\\Matched liquid fields with a compact storage/removal comparison.\\Results pending.}"))
            figure_slots += 1
    if figure_slots != 1:
        raise ValueError("Expected one pending Figure 18 in the mesh-comparison section")
    reserved.append(raw(r"\vfill\noindent\textit{Review layout only. Replace this allowance with the verified mesh comparison and its finding.}"))
    reserved.append(raw(r"\clearpage"))
    return reserved


def transform(blocks: list[dict], source: Path, api_version: list[int], images: list[Path]) -> list[dict]:
    converted = []
    index = 0
    table_number = 0
    while index < len(blocks):
        block = copy.deepcopy(blocks[index])
        if block["t"] == "RawBlock" and block["c"][0] == "html":
            index += 1
            continue
        if block["t"] == "Header":
            text = plain(block["c"][2])
            if text.startswith("Part "):
                index += 1
                continue
            block["c"][0] = max(1, block["c"][0] - 1)
            if text.startswith("4.13."):
                tail = copy.deepcopy(blocks[index:])
                for item in tail:
                    if item["t"] == "Header":
                        item["c"][0] = max(1, item["c"][0] - 1)
                converted.extend(mesh_comparison_page(tail))
                break
        # The two published Pointon panels constitute one numbered Figure 4.
        if block["t"] == "Para" and plain(block).startswith("(a) Inlet configurations."):
            panel_a, panel_b = walk_images(blocks[index + 1])[0], walk_images(blocks[index + 3])[0]
            tex_a, path_a = image_tex(panel_a, source)
            tex_b, path_b = image_tex(panel_b, source)
            images.extend([path_a, path_b])
            label_a = latex_blocks([blocks[index]], api_version)
            label_b = latex_blocks([blocks[index + 2]], api_version)
            caption = latex_blocks([{"t": "Plain", "c": caption_inlines(blocks[index + 4])}], api_version)
            converted.append(raw("\\begin{figure}[htbp]\n\\centering\n"
                                 + label_a + "\n\\par\n" + tex_a + "\n\\par\n"
                                 + label_b + "\n\\par\n" + tex_b
                                 + "\n\\caption*{" + caption + "}\n\\end{figure}"))
            index += 5
            continue
        if block["t"] == "Figure":
            items = walk_images(block)
            if len(items) != 1:
                raise ValueError("Expected one image in a numbered source figure")
            graphic, path = image_tex(items[0], source)
            images.append(path)
            following = blocks[index + 1]
            if following["t"] != "Para" or not plain(following).startswith("Figure "):
                raise ValueError(f"Missing explicit caption after {path.name}")
            caption = latex_blocks([{"t": "Plain", "c": caption_inlines(following)}], api_version)
            converted.append(raw("\\begin{figure}[htbp]\n\\centering\n" + graphic
                                 + "\n\\caption*{" + caption + "}\n\\end{figure}"))
            index += 2
            continue
        if block["t"] == "Para" and re.match(r"Table (\d+)\.", plain(block)):
            match = re.match(r"Table (\d+)\.", plain(block))
            table_number = int(match.group(1))
            caption = latex_blocks([{"t": "Plain", "c": caption_inlines(block)}], api_version)
            following = blocks[index + 1]
            if following["t"] != "Table":
                raise ValueError(f"Missing table after caption {table_number}")
            converted.append(raw("\\begin{table}[htbp]\n\\centering\n\\caption*{" + caption
                                 + "}\n" + table_tex(following, table_number, api_version)
                                 + "\n\\end{table}"))
            index += 2
            continue
        if block["t"] == "Table":
            block = transform_table(block, table_number)
        converted.append(block)
        index += 1
    return converted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPORT / "review")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source_inputs = []
    images: list[Path] = []
    combined = []
    api_version = None
    for source in SOURCES:
        content = source.read_text()
        source_inputs.append(f"<!-- Source: {source.relative_to(REPO)} -->\n{content}")
        doc = json.loads(run(["pandoc", "-f", "markdown", "-t", "json"], data=content))
        api_version = doc["pandoc-api-version"]
        combined.extend(transform(doc["blocks"], source, api_version, images))
    ast = {"pandoc-api-version": api_version, "meta": {}, "blocks": combined}
    figure_numbers = sorted(int(match) for block in combined if block["t"] == "RawBlock"
                            for match in re.findall(r"\\caption\*\{Figure (\d+)\.", block["c"][1]))
    if figure_numbers != list(range(1, 18)):
        raise RuntimeError(f"Expected every current main Figure 1–17 once; found {figure_numbers}")
    (out / "body-input.md").write_text("\n\n".join(source_inputs))
    (out / "body-proof-ast.json").write_text(json.dumps(ast, indent=2))
    (out / "layout-header.tex").write_text(HEADER)
    tex = out / "body-page-proof.tex"
    run(["pandoc", str(out / "body-proof-ast.json"), "-f", "json", "-t", "latex", "-s",
         "--pdf-engine=tectonic", "-V", "documentclass=article", "-V", "fontsize=12pt",
         "-V", "mainfont=Times New Roman", "-V", "papersize=a4",
         "-V", "geometry=top=20mm,bottom=20mm,left=25mm,right=25mm",
         "-H", str(out / "layout-header.tex"), "-o", str(tex)])
    # Keep the compiler log for inspection of overflow or unavailable glyphs.
    completed = subprocess.run(["tectonic", "--keep-logs", "--keep-intermediates", str(tex)],
                               text=True, capture_output=True, cwd=out)
    (out / "render.log").write_text(completed.stdout + completed.stderr)
    completed.check_returncode()
    pdf = out / "body-page-proof.pdf"
    info = run(["pdfinfo", str(pdf)])
    pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    run(["pdftotext", "-layout", str(pdf), str(out / "body-page-proof.txt")])
    page_texts = (out / "body-page-proof.txt").read_text().split("\f")
    page_map = []
    for number, content in enumerate(page_texts, 1):
        if not content.strip():
            continue
        titles = [line.strip() for line in content.splitlines()
                  if re.match(r"\s*[1-6]\.\s+(Introduction|Literature review|Model and methods|Results|Discussion|Conclusions)", line)
                  or "Mesh-sensitivity results:" in line]
        page_map.append({"page": number, "titles": titles})
    manifest = {
        "purpose": "Review proof of Introduction through Conclusions; not a submission PDF",
        "pages": pages,
        "limit_pages": 30,
        "within_limit": pages <= 30,
        "mesh_comparison_reserved_pages": [item["page"] for item in page_map
                                           if any("Mesh-sensitivity results:" in title for title in item["titles"])],
        "font": "Times New Roman",
        "body_font_pt": 12,
        "body_line_stretch": 1.15,
        "main_figure_numbers": figure_numbers,
        "image_assets": len(images),
        "caption_font_pt": 11,
        "geometry_mm": {"top": 20, "bottom": 20, "left": 25, "right": 25},
        "paragraph_gap_pt": 4,
        "subsection_extra_gap_pt": {"before": 0, "after": 0},
        "template_difference": "Compact 4 pt paragraph gaps and heading gaps; body font, body line spacing and page margins retained",
        "scientific_text_cuts": [],
        "layout_changes": ["Remove redundant Part headings", "Use the explicit numbered captions rather than image alt text",
                           "Group the two published Figure 4 panels vertically at 10 cm width", "Assign table column widths",
                           "Allow numbered figures to float while retaining their source order", "Reserve one page for the final mesh comparison"],
        "image_widths_cm": IMAGE_WIDTHS,
        "table_column_fractions": TABLE_WIDTHS,
        "source_hashes": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCES},
        "image_hashes": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in images},
        "page_map": page_map,
        "reproduce": "PyAnsys/.venv/bin/python PyAnsys/scripts/analysis/export_final_report_page_proof.py",
    }
    mesh_pages = ", ".join(str(page) for page in manifest["mesh_comparison_reserved_pages"])
    if len(manifest["mesh_comparison_reserved_pages"]) != 1:
        raise RuntimeError("The rendered proof must contain exactly one mesh-comparison reserved page")
    reserved_page = manifest["mesh_comparison_reserved_pages"][0]
    if "5. Discussion" not in page_texts[reserved_page]:
        raise RuntimeError("The mesh-comparison allowance spilled beyond its single reserved page")
    log = (out / "body-page-proof.log").read_text()
    warnings = [line.strip() for line in log.splitlines()
                if "Overfull" in line or "Missing character:" in line]
    manifest["layout_warnings"] = warnings
    (out / "page-proof-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (out / "README.md").write_text(
        "# Main-body page proof\n\n"
        f"[body-page-proof.pdf](body-page-proof.pdf) contains **{pages} pages**, counted from "
        "Introduction through Conclusions. Front matter, references and appendices are excluded. "
        f"One page is reserved for the final mesh comparison: **{mesh_pages}**. "
        + ("This proof meets the 30-page body limit.\n\n" if pages <= 30
           else f"This proof exceeds the 30-page body limit by **{pages - 30} pages**.\n\n")
        + "The proof uses A4, 12 pt Times New Roman body text, 1.15 body line spacing, "
        "20 mm top/bottom margins and 25 mm side margins. Captions use the template's small "
        "type (approximately 11 pt). Paragraph gaps are 4 pt, with compact heading gaps. "
        "Those gaps differ from the supplied template; the body type, line spacing and margins are retained.\n\n"
        "All current main-body text and scientific images are included. The recipe removes "
        "redundant Part headings and uses each explicit numbered caption once. It places the two "
        "published Figure 4 panels vertically at 10 cm width and assigns table widths. Figure pixels and "
        "scientific data are unchanged. Short tables stay together rather than splitting across pages.\n\n"
        "This is a **review proof**, not the submission PDF. The mesh-comparison slot contains no invented "
        "results. Replacing them with final evidence can change pagination. In-text references "
        "to excluded appendices remain in the body for the review.\n\n"
        "Reproduce from the repository root:\n\n"
        "```sh\nPyAnsys/.venv/bin/python PyAnsys/scripts/analysis/export_final_report_page_proof.py\n```\n\n"
        "The script needs `pandoc`, `tectonic`, `pdfinfo` and `pdftotext` on PATH and the "
        "installed Times New Roman fonts. [page-proof-manifest.json](page-proof-manifest.json) "
        "records source/image hashes, display sizes, page count and reserved-page numbers. "
        "[body-input.md](body-input.md) preserves the rendered source snapshot; the JSON AST, "
        "LaTeX input and render logs preserve the layout recipe.\n"
    )
    if warnings:
        raise RuntimeError("Inspect the proof: " + "; ".join(warnings))
    print(json.dumps({"pdf": str(pdf), "pages": pages,
                      "mesh_comparison_reserved_pages": manifest["mesh_comparison_reserved_pages"], "within_limit": pages <= 30}, indent=2))


if __name__ == "__main__":
    main()
