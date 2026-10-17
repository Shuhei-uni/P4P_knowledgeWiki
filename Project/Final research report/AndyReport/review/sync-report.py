#!/usr/bin/env python3
"""Synchronise the existing report export without touching the approved opening.

Run with --write after editing the six numbered draft files. Run with --check
to check that the generated files agree with them. With neither flag, show a
read-only preview of the files and editorial word counts. Compilation and PDF
layout review remain separate steps; stored page counts are not recalculated.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "draft"
LATEX = ROOT / "review/latex"
PROTECTED = (
    DRAFT / "01-introduction-and-literature-review.md",
    LATEX / "sections/01-introduction.tex",
    LATEX / "sections/02-literature-review.tex",
)
DEFAULT_PANDOC = "/tmp/p4p-report-move/deps/pypandoc/files/pandoc"
WORDS = re.compile(r"\b[\w]+(?:[-’'][\w]+)*\b")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(node):
    """Visible AST text, omitting equations, image alternatives and raw markup."""
    if isinstance(node, list):
        return " ".join(filter(None, (plain(item) for item in node)))
    if not isinstance(node, dict):
        return ""
    kind, value = node.get("t"), node.get("c", [])
    if kind in {"Math", "Image", "RawBlock", "RawInline"}:
        return ""
    if kind == "Str":
        return value
    if kind == "Code":
        return value[1]
    if kind == "Link":
        return plain(value[1])
    if kind == "Header":
        return plain(value[2])
    return plain(value)


def section_blocks(blocks):
    sections, title, selected = {}, None, []
    for block in blocks:
        if block["t"] == "Header" and block["c"][0] == 2:
            if title is not None:
                sections[title] = selected
            title, selected = plain(block), [block]
        elif title is not None:
            selected.append(block)
    if title is not None:
        sections[title] = selected
    return sections


class Exporter:
    def __init__(self, pandoc):
        self.pandoc = pandoc
        self.api_version = None
        self.cache = {}
        self.warnings = []
        self.captions = {"Table": [], "Figure": []}
        self.glossary_table = 0

    def parse(self, text):
        result = subprocess.run(
            [self.pandoc, "--from=markdown-implicit_figures", "--to=json"],
            input=text, text=True, check=True, capture_output=True,
        )
        document = json.loads(result.stdout)
        self.api_version = document["pandoc-api-version"]
        return document["blocks"]

    def latex(self, blocks):
        payload = json.dumps({"pandoc-api-version": self.api_version,
                              "meta": {}, "blocks": blocks}, ensure_ascii=False)
        if payload not in self.cache:
            result = subprocess.run(
                [self.pandoc, "--from=json", "--to=latex", "--wrap=none",
                 "--top-level-division=section", "--pdf-engine=xelatex"],
                input=payload, text=True, check=True, capture_output=True,
            )
            self.cache[payload] = result.stdout.replace("\\tightlist\n", "").strip()
        return self.cache[payload]

    def caption(self, block, kind):
        if block["t"] not in {"Para", "Plain"}:
            return None
        text = plain(block)
        match = re.match(rf"^{kind}\s+([A-Z]?\.?\d+(?:\.\d+)?)\.\s+(.+)$", text)
        if not match:
            return None
        number, caption = match.groups()
        # Captions in the canonical draft are one italic paragraph. Reparse the
        # content so mathematical notation and links survive prefix removal.
        inlines = block["c"]
        if len(inlines) == 1 and inlines[0]["t"] == "Emph":
            inlines = inlines[0]["c"]
        copied = copy.deepcopy(inlines)
        remaining = len(f"{kind} {number}. ")
        while copied and remaining:
            item = copied[0]
            if item["t"] == "Str":
                if len(item["c"]) <= remaining:
                    remaining -= len(item["c"])
                    copied.pop(0)
                else:
                    item["c"] = item["c"][remaining:]
                    remaining = 0
            elif item["t"] in {"Space", "SoftBreak", "LineBreak"}:
                remaining -= 1
                copied.pop(0)
            else:
                raise ValueError(f"Unsupported caption prefix: {text}")
        return number, copied

    @staticmethod
    def relocate(target):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            return target
        source = (DRAFT / unquote(parts.path)).resolve()
        relative = os.path.relpath(source, LATEX)
        return urlunsplit(("", "", relative, parts.query, parts.fragment))

    def prepare(self, value, front=False):
        if isinstance(value, list):
            return [self.prepare(item, front) for item in value
                    if not (isinstance(item, dict) and item.get("t") in {"RawBlock", "RawInline"}
                            and item.get("c", [""])[0] == "html")]
        if not isinstance(value, dict):
            return value
        node = copy.deepcopy(value)
        kind = node.get("t")
        if kind in {"Image", "Link"}:
            node["c"][2][0] = self.relocate(node["c"][2][0])
        if kind == "Header":
            title = plain(node)
            title = re.sub(r"^(?:\d+(?:\.\d+)*\.\s+|Appendix\s+[A-Z]\.\s+)", "", title)
            header = self.parse(title)[0]["c"]
            node["c"] = [max(1, node["c"][0] - 1), ["", [], []], header]
            if front:
                # Keep the symbol definitions together after the expanded glossary.
                prefix = "\\clearpage\n" if title == "Symbols" else ""
                return {"t": "RawBlock", "c": ["latex", prefix + "\\subsection*{" + self.latex([{"t": "Plain", "c": header}]) + "}"]}
        if "c" in node:
            node["c"] = self.prepare(node["c"], front)
        return node

    def table(self, block, caption, front=False):
        attr, native_caption, colspec, head, bodies, foot = block["c"]
        count = len(colspec)
        widths = {2: [.29, .71], 3: [.29, .34, .37],
                  4: [.40, .20, .20, .20], 5: [.28, .18, .18, .18, .18]}
        ratios = widths.get(count, [1 / count] * count)
        specification = "@{}" + "".join(
            rf">{{\raggedright\arraybackslash}}p{{{width:.8f}\dimexpr\linewidth-{2 * (count - 1)}\tabcolsep\relax}}"
            for width in ratios) + "@{}"

        def row_text(row):
            cells = []
            for cell in row[1]:
                if cell[2:4] != [1, 1]:
                    raise ValueError("Merged table cells need an explicit export layout")
                text = self.latex(cell[4]).replace("\n\n", "\\par ")
                cells.append(text)
            return " & ".join(cells) + r" \\"

        lines = []
        if front:
            self.glossary_table += 1
            lines += [r"\addtocounter{table}{-1}",
                      rf"\renewcommand{{\theHtable}}{{glossary-{self.glossary_table}}}"]
        lines.append(r"\begin{longtable}{" + specification + "}")
        if caption:
            number, inline = caption
            text = self.latex([{"t": "Plain", "c": inline}])
            lines.append(r"\caption{" + text + r"}\label{tab:table-" + number + r"}\\")
            self.captions["Table"].append(number)
        elif not front:
            self.warnings.append("Uncaptioned table in the report body or appendices")
        headings = [row_text(row) for row in head[1]]
        if headings and any(plain(row[1]) for row in head[1]):
            lines += [r"\toprule", *headings, r"\midrule", r"\endfirsthead",
                      r"\toprule", *headings, r"\midrule", r"\endhead"]
        for body in bodies:
            lines += [row_text(row) for row in body[2] + body[3]]
        lines += [row_text(row) for row in foot[1]]
        lines += [r"\bottomrule", r"\end{longtable}"]
        if caption and caption[0] == "4":
            # Keep the short R0 mass budget together beside its explanation.
            rows = [row_text(row) for body in bodies for row in body[2] + body[3]]
            lines = [r"\noindent\begin{minipage}{\linewidth}",
                     r"\captionof{table}{" + text + r"}\label{tab:table-4}",
                     r"\begin{tabular}{" + specification + "}",
                     r"\toprule", *headings, r"\midrule", *rows,
                     r"\bottomrule", r"\end{tabular}", r"\end{minipage}"]
        if front:
            lines.append(r"\renewcommand{\theHtable}{\arabic{table}}")
        return {"t": "RawBlock", "c": ["latex", "\n".join(lines)]}

    def figure(self, image, caption):
        if not caption:
            raise ValueError("Every exported figure needs a following '*Figure N. ...*' caption")
        number, inline = caption
        path = image["c"][2][0]
        absolute = (LATEX / path).resolve()
        if not absolute.exists():
            raise FileNotFoundError(f"Figure asset missing: {absolute}")
        text = self.latex([{"t": "Plain", "c": inline}])
        self.captions["Figure"].append(number)
        result = "\n".join([
            r"\begin{figure}[!htbp]", r"\centering",
            r"\includegraphics[width=\linewidth,height=.46\textheight,keepaspectratio]{\detokenize{" + path + "}}",
            r"\caption{" + text + "}", r"\label{fig:figure-" + number + "}",
            r"\end{figure}",
        ])
        return {"t": "RawBlock", "c": ["latex", result]}

    def render(self, blocks, front=False, drop_heading=False):
        blocks = copy.deepcopy(blocks[1:] if drop_heading else blocks)
        blocks = self.prepare(blocks, front)
        rendered, index = [], 0
        while index < len(blocks):
            block = blocks[index]
            following = blocks[index + 1] if index + 1 < len(blocks) else {"t": "Null"}
            image = (block["c"][0] if block["t"] == "Para" and len(block["c"]) == 1
                     and block["c"][0]["t"] == "Image" else None)
            if block["t"] == "Table":
                caption = self.caption(following, "Table")
                rendered.append(self.table(block, caption, front))
                index += bool(caption)
            elif image:
                caption = self.caption(following, "Figure")
                rendered.append(self.figure(image, caption))
                index += bool(caption)
            else:
                rendered.append(block)
            index += 1
        return self.latex(rendered) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="save the synchronised export")
    mode.add_argument("--check", action="store_true", help="fail if generated files differ")
    parser.add_argument("--pandoc", default=os.environ.get("PANDOC") or shutil.which("pandoc") or DEFAULT_PANDOC)
    args = parser.parse_args()
    protected_before = {str(path.relative_to(ROOT)): digest(path) for path in PROTECTED}
    files = sorted(DRAFT.glob("0[0-5]-*.md"))
    if len(files) != 6:
        raise ValueError("Expected exactly six numbered draft files (00 through 05)")
    exporter = Exporter(args.pandoc)
    texts = {path.name: path.read_text() for path in files}
    parsed = {name: exporter.parse(text) for name, text in texts.items()}
    sections = {name: section_blocks(blocks) for name, blocks in parsed.items()}
    output = {DRAFT / "draft-v1.md": "\n\n".join(text.rstrip() for text in texts.values()) + "\n"}

    def add(filename, blocks, **options):
        output[LATEX / "sections" / filename] = exporter.render(blocks, **options)

    front = sections[files[0].name]
    add("00-abstract.tex", front["Abstract"], front=True, drop_heading=True)
    add("00-declaration.tex", front["Declaration"], front=True, drop_heading=True)
    glossary = next(value for key, value in front.items() if key.startswith("Glossary"))
    add("00-glossary.tex", glossary, front=True, drop_heading=True)
    chapter_outputs = {
        "3": "03-model-and-methods.tex", "4": "04-verification-and-validation.tex",
        "5": "05-results.tex", "6": "06-discussion.tex", "7": "07-conclusions.tex",
    }
    found = set()
    for path in files[2:5]:
        for title, blocks in sections[path.name].items():
            number = title.split(".", 1)[0]
            if number not in chapter_outputs:
                raise ValueError(f"Unexpected body section: {title}")
            add(chapter_outputs[number], blocks)
            found.add(number)
    if found != set(chapter_outputs):
        raise ValueError(f"Missing chapters: {set(chapter_outputs) - found}")
    end = sections[files[5].name]
    add("08-references.tex", end["References"], drop_heading=True)
    appendix = [block for title, blocks in end.items() if title.startswith("Appendix ") for block in blocks]
    add("09-appendices.tex", appendix)

    body_tables = [int(n) for n in exporter.captions["Table"] if n.isdigit()]
    body_figures = [int(n) for n in exporter.captions["Figure"] if n.isdigit()]
    if body_tables != list(range(1, len(body_tables) + 1)):
        raise ValueError(f"Body table numbers are not consecutive: {body_tables}")
    if body_figures != list(range(5, 5 + len(body_figures))):
        raise ValueError(f"New figures must follow protected Figures 1–4: {body_figures}")

    count_path = ROOT / "review/word-count.json"
    counts = json.loads(count_path.read_text()) if count_path.exists() else {}
    counts["section_file_counts"] = {
        path.name: len(WORDS.findall(plain(parsed[path.name]))) for path in files[1:5]
    }
    counts["body_including_headings_captions_tables"] = sum(counts["section_file_counts"].values())
    intro = next(blocks for title, blocks in sections[files[1].name].items() if title.startswith("1."))
    intro_no_heading = intro[1:]
    counts["introduction_with_caption"] = len(WORDS.findall(plain(intro_no_heading)))
    intro_prose = [b for b in intro_no_heading if not exporter.caption(b, "Figure")]
    counts["introduction_prose"] = len(WORDS.findall(plain(intro_prose)))
    counts["method"] = ("Pandoc Markdown AST; word tokens in text, headings, captions and tables using Unicode word groups "
                        "with internal hyphens/apostrophes. Excludes image alt text, URLs, equations, raw HTML, front matter, "
                        "references and appendices. Approximate editorial count.")
    counts["count_note"] = ("Image alternative text is excluded explicitly, including implicit-figure captions; "
                            "earlier approximate counts are not directly comparable. Protected opening text is unchanged. "
                            "Page counts require compilation and visual review; synchronisation retains the previous recorded page counts.")
    output[count_path] = json.dumps(counts, indent=2, ensure_ascii=False) + "\n"
    different = [str(path.relative_to(ROOT)) for path, text in output.items()
                 if not path.exists() or path.read_text() != text]
    if args.write:
        for path, text in output.items():
            if not path.exists() or path.read_text() != text:
                path.write_text(text)
    protected_after = {str(path.relative_to(ROOT)): digest(path) for path in PROTECTED}
    if protected_after != protected_before:
        raise RuntimeError("Protected introduction or literature-review file changed")
    print(json.dumps({"mode": "write" if args.write else "check" if args.check else "preview",
                      "different_files": different, "body_words": counts["body_including_headings_captions_tables"],
                      "captions": exporter.captions, "warnings": exporter.warnings,
                      "protected_sha256": protected_after}, indent=2))
    if args.check and different:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
