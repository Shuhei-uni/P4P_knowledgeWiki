#!/usr/bin/env python3
"""Extract particle injection settings and tracking summaries from Enthalpy_1600 source files.

The source directory contains plain-text injection definitions and per-injection
`.sum` summaries. This script normalizes those files into a case archive under
`PyAnsys/cases/actual_setup_archives/` so the extracted settings are available
without reopening Fluent.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "data" / "Enthalpy_1600"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "cases" / "actual_setup_archives" / "purnanto-enthalpy1600-particle-extract"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract Enthalpy_1600 particle settings into a case archive.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR), help="Source directory containing injection files and .sum summaries.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Archive directory to write the extracted case bundle.")
    return parser


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def tokenize_sexpr(text: str) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append({"t": ch})
            i += 1
            continue
        if ch == '"':
            j = i + 1
            value = ""
            while j < len(text):
                cur = text[j]
                if cur == "\\":
                    value += text[j + 1] if j + 1 < len(text) else ""
                    j += 2
                    continue
                if cur == '"':
                    break
                value += cur
                j += 1
            tokens.append({"t": "str", "v": value})
            i = j + 1
            continue
        j = i
        value = ""
        while j < len(text) and not text[j].isspace() and text[j] not in "()":
            value += text[j]
            j += 1
        tokens.append({"t": "atom", "v": value})
        i = j
    return tokens


def parse_sexpr(text: str) -> Any:
    tokens = tokenize_sexpr(text)
    idx = 0

    def atom(token: dict[str, str]) -> Any:
        if token["t"] == "str":
            return token["v"]
        value = token["v"]
        if value == "#t":
            return True
        if value == "#f":
            return False
        if value == ".":
            return "."
        if value and value[0] in "-+" and value[1:].replace(".", "", 1).isdigit():
            try:
                return int(value)
            except ValueError:
                return float(value)
        if value.replace(".", "", 1).replace("e+", "", 1).replace("e-", "", 1).isdigit():
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        return value

    def expression() -> Any:
        nonlocal idx
        token = tokens[idx]
        idx += 1
        if token["t"] == "(":
            return parse_list()
        if token["t"] == ")":
            raise ValueError("unexpected )")
        return atom(token)

    def parse_list() -> Any:
        nonlocal idx
        items: list[Any] = []
        while idx < len(tokens):
            token = tokens[idx]
            if token["t"] == ")":
                idx += 1
                return items
            if token["t"] == "atom" and token["v"] == "." and len(items) == 1:
                idx += 1
                rhs = expression()
                if tokens[idx]["t"] != ")":
                    raise ValueError("expected ) after dotted pair")
                idx += 1
                return {"__pair__": [items[0], rhs]}
            items.append(expression())
        raise ValueError("unclosed list")

    return expression()


def to_scalar(value: Any) -> Any:
    if isinstance(value, list):
        return [to_scalar(item) for item in value]
    if isinstance(value, dict) and "__pair__" in value:
        return {"__pair__": [to_scalar(value["__pair__"][0]), to_scalar(value["__pair__"][1])]}
    return value


def scalar_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(scalar_text(item) for item in value)
    if isinstance(value, dict) and "__pair__" in value:
        left, _right = value["__pair__"]
        return scalar_text(left)
    return str(value)


def is_kv_item(node: Any) -> bool:
    if isinstance(node, dict) and "__pair__" in node:
        return True
    if isinstance(node, list) and node:
        return len(node) in (1, 2)
    return False


def convert_value(node: Any) -> Any:
    if isinstance(node, dict) and "__pair__" in node:
        key = scalar_text(node["__pair__"][0])
        return {key: convert_value(node["__pair__"][1])}
    if isinstance(node, list):
        if not node:
            return []
        if all(is_kv_item(item) for item in node):
            return list_to_object(node)
        return [convert_value(item) for item in node]
    return node


def pair_to_item(node: Any) -> tuple[str, Any]:
    if isinstance(node, dict) and "__pair__" in node:
        key = scalar_text(node["__pair__"][0])
        return key, convert_value(node["__pair__"][1])
    if isinstance(node, list):
        if not node:
            return "", []
        if len(node) == 1 and isinstance(node[0], dict) and "__pair__" in node[0]:
            return pair_to_item(node[0])
        key = scalar_text(node[0])
        if len(node) == 1:
            return key, True
        if len(node) == 2:
            return key, convert_value(node[1])
        rest = node[1:]
        if all(is_kv_item(item) for item in rest):
            return key, list_to_object(rest)
        return key, [convert_value(item) for item in rest]
    return str(node), True


def list_to_object(items: list[Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items:
        key, value = pair_to_item(item)
        if not key:
            continue
        result[key] = value
    return result


def parse_injection_file(path: Path) -> dict[str, Any]:
    ast = parse_sexpr(path.read_text(encoding="utf-8"))
    if not isinstance(ast, list) or not ast:
        raise ValueError(f"Unexpected injection file shape: {path}")

    outer = ast[0] if len(ast) == 1 and isinstance(ast[0], list) else ast
    if not isinstance(outer, list) or len(outer) != 2:
        raise ValueError(f"Unexpected top-level structure in {path}")

    injection_name = scalar_text(outer[0])
    body = outer[1]
    if not isinstance(body, list):
        raise ValueError(f"Unexpected injection body in {path}")

    settings = list_to_object(body)
    if "laws" in settings and isinstance(settings["laws"], list):
        settings["laws"] = list_to_object(settings["laws"])

    return {
        "injection_name": injection_name,
        "settings": settings,
        "source_file": str(path),
    }


def parse_sum_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line.rstrip("\r") for line in text.splitlines() if line.strip()]
    records: list[dict[str, Any]] = []
    mass_records: list[dict[str, Any]] = []
    mode: str | None = None

    fate_re = re.compile(
        r"^(?P<fate>.+?\bZone\s+\d+)\s+"
        r"(?P<number>\d+)\s+"
        r"(?P<elapsed_min>[-+0-9.eE]+)\s+"
        r"(?P<elapsed_max>[-+0-9.eE]+)\s+"
        r"(?P<elapsed_avg>[-+0-9.eE]+)\s+"
        r"(?P<elapsed_std>[-+0-9.eE]+)\s+"
        r"(?P<inj_min>.+?)\s+"
        r"(?P<inj_min_index>\d+)\s+"
        r"(?P<inj_max>.+?)\s+"
        r"(?P<inj_max_index>\d+)\s*$"
    )
    mass_re = re.compile(
        r"^(?P<fate>.+?\bZone\s+\d+)\s+"
        r"(?P<initial>[-+0-9.eE]+)\s+"
        r"(?P<final>[-+0-9.eE]+)\s+"
        r"(?P<change>[-+0-9.eE]+)\s*$"
    )

    for line in lines:
        if line.startswith("----") or line.startswith("Elapsed") or line.startswith("Mass Flow"):
            continue
        if "Fate" in line and "Number" in line and "Elapsed Time" in line:
            mode = "fate"
            continue
        if "Mass Transfer Summary" in line:
            mode = "mass"
            continue
        if mode is None:
            continue
        if mode == "fate":
            match = fate_re.match(line)
            if not match:
                continue
            groups = match.groupdict()
            records.append(
                {
                    "fate": groups["fate"].strip(),
                    "number": int(groups["number"]),
                    "elapsed_time": {
                        "min": float(groups["elapsed_min"]),
                        "max": float(groups["elapsed_max"]),
                        "avg": float(groups["elapsed_avg"]),
                        "std_dev": float(groups["elapsed_std"]),
                    },
                    "injection_index": {
                        "min": f"{groups['inj_min']} {groups['inj_min_index']}",
                        "max": f"{groups['inj_max']} {groups['inj_max_index']}",
                    },
                }
            )
        elif mode == "mass":
            match = mass_re.match(line)
            if not match:
                continue
            groups = match.groupdict()
            mass_records.append(
                {
                    "fate": groups["fate"].strip(),
                    "mass_flow": {
                        "initial": float(groups["initial"]),
                        "final": float(groups["final"]),
                        "change": float(groups["change"]),
                    },
                }
            )

    return {
        "source_file": str(path),
        "fate_rows": records,
        "mass_transfer_rows": mass_records,
    }


def extract_diameter_um(settings: dict[str, Any]) -> float | None:
    diameter = settings.get("diameter")
    if isinstance(diameter, (int, float)):
        return float(diameter) * 1e6
    return None


def render_readme(metadata: dict[str, Any], injections: list[dict[str, Any]]) -> str:
    lines = [
        f"# Enthalpy 1600 Particle Extract",
        "",
        "## Metadata",
        "",
        f"- Extracted at (UTC): `{metadata['extracted_at_utc']}`",
        f"- Source directory: `{metadata['source_dir']}`",
        f"- Archive directory: `{metadata['archive_dir']}`",
        "",
        "## Contents",
        "",
        f"- Injection files parsed: `{metadata['injection_file_count']}`",
        f"- Summary files parsed: `{metadata['summary_file_count']}`",
        f"- Ignored non-settings file: `Injection_Files/cortexerror.log`",
        "",
        "## Injections",
        "",
    ]

    for item in injections:
        settings = item["settings"]
        lines.append(f"- `{item['injection_name']}`")
        lines.append(
            f"  - type: `{settings.get('type', '(missing)')}`; injection type: `{settings.get('injection-type', '(missing)')}`; material: `{settings.get('material', '(missing)')}`"
        )
        diameter_um = item.get("diameter_um")
        if diameter_um is not None:
            lines.append(f"  - diameter: `{diameter_um:g} um`")
        lines.append(
            f"  - boundary: `{settings.get('boundary', '(missing)')}`; surfaces: `{settings.get('surfaces', '(missing)')}`; flow rate: `{settings.get('total-flow-rate', settings.get('flow-rate', '(missing)'))}`"
        )

    lines.extend(["", "## Notes", "", "- Particle settings were extracted directly from the source text files.", "- `*.sum` files contain fate and mass-transfer summaries for each tracked particle size.", ""])
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    injection_dir = source_dir / "Injection_Files"

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if not injection_dir.exists():
        raise FileNotFoundError(f"Injection_Files directory does not exist: {injection_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    injection_files = sorted(
        path for path in injection_dir.iterdir()
        if path.is_file() and path.name != "cortexerror.log" and not path.name.startswith(".")
    )
    summary_files = sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix == ".sum")

    injections: list[dict[str, Any]] = []
    for path in injection_files:
        parsed = parse_injection_file(path)
        parsed["diameter_um"] = extract_diameter_um(parsed["settings"])
        injections.append(parsed)

    summaries: list[dict[str, Any]] = []
    for path in summary_files:
        summaries.append(parse_sum_file(path))

    injections.sort(key=lambda item: item["injection_name"])
    summaries.sort(key=lambda item: Path(item["source_file"]).name)

    metadata = {
        "extracted_at_utc": now_utc(),
        "source_dir": str(source_dir),
        "archive_dir": str(output_dir),
        "injection_file_count": len(injection_files),
        "summary_file_count": len(summary_files),
    }

    manifest = {
        "bundle_name": output_dir.name,
        "metadata": metadata,
        "source": {
            "injection_files": [str(path) for path in injection_files],
            "summary_files": [str(path) for path in summary_files],
        },
        "generated_files": [
            "README.md",
            "manifest.json",
            "injections.json",
            "summaries.json",
        ],
    }

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output_dir / "injections.json").write_text(json.dumps(injections, indent=2) + "\n", encoding="utf-8")
    (output_dir / "summaries.json").write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")
    (output_dir / "README.md").write_text(render_readme(metadata, injections), encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
