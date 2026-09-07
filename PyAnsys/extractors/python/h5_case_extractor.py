#!/usr/bin/env python3
"""Offline inspector for Fluent case/data files.

Supports:
- modern HDF5 `.cas.h5` / `.dat.h5`
- legacy text `.cas` files with Scheme-like settings blocks

The goal is conservative extraction: inventory what is present, surface likely
setup-critical lines, and keep enough structure for later Fluent-side checks.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import h5py
import numpy as np


HDF5_SIGNATURE = b"\x89HDF\r\n\x1a\n"
MAX_STRING_PREVIEW = 40
MAX_DATASET_PREVIEW_ITEMS = 12
TEXT_PREVIEW_LIMIT = 500

KEYWORD_PATTERNS = (
    "case-config",
    "materials",
    "domains",
    "boundary",
    "pressure-reference",
    "operating-pressure",
    "gravity",
    "hyb-init",
    "solver",
    "pressure",
    "velocity",
    "mass-flow",
    "dpm",
    "model",
    "turb",
    "inlet",
    "outlet",
    "wall",
    "initial",
    "reference-",
)


def decode_bytes(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def normalize_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return decode_bytes(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def safe_attr_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        if value.dtype.kind in {"S", "O", "U"}:
            return [normalize_scalar(item) for item in value.tolist()]
        return value.tolist()
    return normalize_scalar(value)


def looks_textual(dataset: h5py.Dataset) -> bool:
    return dataset.dtype.kind in {"S", "O", "U"}


def preview_dataset(dataset: h5py.Dataset) -> Any:
    if dataset.size == 0:
        return []

    if dataset.size > MAX_DATASET_PREVIEW_ITEMS:
        data = dataset[tuple(slice(0, 1) for _ in dataset.shape)] if dataset.shape else dataset[()]
    else:
        data = dataset[()]

    if isinstance(data, np.ndarray):
        flat = data.flatten().tolist()
        return [normalize_scalar(item) for item in flat[:MAX_DATASET_PREVIEW_ITEMS]]
    return normalize_scalar(data)


def extract_candidate_text(dataset: h5py.Dataset) -> str | None:
    if not looks_textual(dataset):
        return None
    if dataset.size == 0 or dataset.size > MAX_STRING_PREVIEW:
        return None

    raw = dataset[()]
    if isinstance(raw, bytes):
        text = decode_bytes(raw)
    elif isinstance(raw, np.ndarray):
        items = [normalize_scalar(item) for item in raw.flatten().tolist()]
        text = "\n".join(str(item) for item in items[:MAX_STRING_PREVIEW])
    else:
        text = str(normalize_scalar(raw))

    text = text.strip()
    if not text:
        return None
    if len(text) > TEXT_PREVIEW_LIMIT:
        text = text[:TEXT_PREVIEW_LIMIT] + "\n...[truncated]"
    return text


def inspect_hdf5(input_path: Path) -> dict[str, Any]:
    tree_lines: list[str] = []
    datasets: list[dict[str, Any]] = []
    candidate_strings: list[dict[str, str]] = []

    with h5py.File(input_path, "r") as handle:
        def visitor(name: str, obj: h5py.Group | h5py.Dataset) -> None:
            if isinstance(obj, h5py.Group):
                tree_lines.append(f"[GROUP]   /{name}")
                attrs = {key: safe_attr_value(value) for key, value in obj.attrs.items()}
                if attrs:
                    tree_lines.append(f"          attrs={json.dumps(attrs, ensure_ascii=False)}")
                return

            if isinstance(obj, h5py.Dataset):
                tree_lines.append(
                    f"[DATASET] /{name} shape={obj.shape} dtype={obj.dtype}"
                )
                attrs = {key: safe_attr_value(value) for key, value in obj.attrs.items()}
                if attrs:
                    tree_lines.append(f"          attrs={json.dumps(attrs, ensure_ascii=False)}")

                preview = preview_dataset(obj)
                entry = {
                    "path": f"/{name}",
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "attrs": attrs,
                    "preview": preview,
                }
                datasets.append(entry)

                candidate = extract_candidate_text(obj)
                if candidate:
                    candidate_strings.append({"path": f"/{name}", "text": candidate})
                    tree_lines.append("          candidate_text=yes")

        handle.visititems(visitor)

        return {
            "format": "hdf5",
            "input_file": str(input_path),
            "root_keys": sorted(list(handle.keys())),
            "dataset_count": len(datasets),
            "candidate_string_count": len(candidate_strings),
            "datasets": datasets,
            "tree_lines": tree_lines,
            "candidate_strings": candidate_strings,
            "notes": [],
        }


def token_from_line(line: str) -> str | None:
    match = re.match(r"^\(([^\s()]+)", line)
    if not match:
        return None
    token = match.group(1)
    if token and token[0].isdigit():
        return None
    return token


def is_candidate_token(token: str) -> bool:
    return (
        "/" in token
        or token.endswith("?")
        or token.startswith("case-")
        or token.startswith("dpm/")
        or token.startswith("pressure/")
        or token.startswith("gravity")
        or token.startswith("materials")
        or token.startswith("domains")
        or token.startswith("boundary")
        or token.startswith("hyb-init")
        or token.startswith("operating-pressure")
        or token.startswith("reference-")
        or token.startswith("solver/")
        or token.startswith("velocity")
        or token.startswith("mass-flow")
        or token.startswith("model")
        or token.startswith("turb")
        or token.startswith("inlet")
        or token.startswith("outlet")
        or token.startswith("wall")
    )


def inspect_legacy_text(input_path: Path) -> dict[str, Any]:
    raw = input_path.read_bytes()
    notes: list[str] = []
    if b"\x00" in raw:
        raw = raw.split(b"\x00", 1)[0]
        notes.append("Binary trailer detected; truncated at first null byte.")

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    tree_lines: list[str] = []
    candidate_strings: list[dict[str, str]] = []
    settings_entries: list[dict[str, Any]] = []
    unique_tokens: set[str] = set()

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line.startswith("("):
            continue

        token = token_from_line(line)
        if token:
            unique_tokens.add(token)

        if token and is_candidate_token(token):
            excerpt = line if len(line) <= TEXT_PREVIEW_LIMIT else line[:TEXT_PREVIEW_LIMIT] + "...[truncated]"
            settings_entries.append(
                {
                    "line": line_no,
                    "token": token,
                    "text": excerpt,
                }
            )
            tree_lines.append(f"{line_no}: {token} {excerpt[:TEXT_PREVIEW_LIMIT]}")

            if any(keyword in token for keyword in KEYWORD_PATTERNS) or any(
                keyword in line for keyword in KEYWORD_PATTERNS
            ):
                candidate_strings.append({"path": f"line:{line_no}:{token}", "text": excerpt})

        elif any(keyword in line for keyword in KEYWORD_PATTERNS):
            excerpt = line if len(line) <= TEXT_PREVIEW_LIMIT else line[:TEXT_PREVIEW_LIMIT] + "...[truncated]"
            candidate_strings.append({"path": f"line:{line_no}", "text": excerpt})
            tree_lines.append(f"{line_no}: {excerpt[:TEXT_PREVIEW_LIMIT]}")

    summary = {
        "format": "legacy_text",
        "input_file": str(input_path),
        "line_count": len(lines),
        "binary_trailer_truncated": bool(notes),
        "settings_entry_count": len(settings_entries),
        "candidate_string_count": len(candidate_strings),
        "unique_token_count": len(unique_tokens),
        "settings_entries": settings_entries,
        "candidate_strings": candidate_strings,
        "tree_lines": tree_lines,
        "notes": notes,
    }
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a Fluent case/data file without Fluent."
    )
    parser.add_argument("input_file", help="Path to a Fluent .cas, .cas.h5, or .dat/.dat.h5 file.")
    parser.add_argument(
        "--output-dir",
        help="Directory for output artifacts. Default: PyAnsys/output/<input_stem>_extract",
    )
    return parser


def detect_format(input_path: Path) -> str:
    with input_path.open("rb") as handle:
        signature = handle.read(8)
    if signature == HDF5_SIGNATURE:
        return "hdf5"
    return "legacy_text"


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    default_output_dir = (
        Path(__file__).resolve().parent.parent / "output" / f"{input_path.name}_extract"
    )
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_format = detect_format(input_path)
    if file_format == "hdf5":
        summary = inspect_hdf5(input_path)
    else:
        summary = inspect_legacy_text(input_path)

    (output_dir / "tree.txt").write_text(
        "\n".join(summary.get("tree_lines", [])) + ("\n" if summary.get("tree_lines") else ""),
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    candidate_text = []
    for item in summary.get("candidate_strings", []):
        candidate_text.append(f"## {item['path']}\n{item['text']}\n")
    (output_dir / "candidate_strings.txt").write_text(
        "\n".join(candidate_text),
        encoding="utf-8",
    )

    print(f"[OK] Format: {summary['format']}")
    print(f"[OK] Input: {input_path}")
    print(f"[OK] Output directory: {output_dir}")
    if summary["format"] == "hdf5":
        print(f"[OK] Datasets inventoried: {summary['dataset_count']}")
    else:
        print(f"[OK] Settings entries captured: {summary['settings_entry_count']}")
        print(f"[OK] Unique token count: {summary['unique_token_count']}")
    print(f"[OK] Candidate text blocks: {summary['candidate_string_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
