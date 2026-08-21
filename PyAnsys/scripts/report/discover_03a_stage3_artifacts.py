#!/usr/bin/env python3
"""Discover local 03A Stage-3 Fluent artifacts without using them as evidence.

The server-2 native queue has a specific run stamp and branch sequence.  This
read-only inventory searches operator-supplied roots for Fluent case/data and
Report File artifacts, records their metadata, and classifies whether their
lineage can be attributed to that queue.  It deliberately does not copy,
open, modify, or promote any artifact into a branch history.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = (
    PROJECT_ROOT
    / ".."
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
).resolve()
DEFAULT_SEARCH_ROOT = Path(
    "/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/2026 Sem 2/700"
)
DEFAULT_OUTPUT_JSON = (
    REPORT_ROOT
    / "evidence"
    / "03a-stage3-native-queue"
    / "03a-stage3-local-artifact-discovery.json"
)
DEFAULT_OUTPUT_CSV = (
    REPORT_ROOT
    / "evidence"
    / "03a-stage3-native-queue"
    / "03a-stage3-local-artifact-discovery.csv"
)
TARGET_RUN_STAMP = "20260820T013223Z"
STAGE3_NAME_RE = re.compile(r"03a[-_]?stage3", re.IGNORECASE)
BRANCH_RE = re.compile(r"(?<![A-Za-z0-9])F(?:0[1-9]|1[0-2])(?![A-Za-z0-9])", re.IGNORECASE)
RUN_STAMP_RE = re.compile(r"20\d{6}T\d{6}Z")
NUMBER_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d*)?(?:[Ee][+-]?\d+)?)\s+"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)"
)

ARTIFACT_SUFFIXES = (".cas.h5", ".dat.h5", ".cas", ".dat", ".out")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--search-root",
        action="append",
        type=Path,
        help="Root to search recursively. Repeat for multiple roots.",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--target-run-stamp", default=TARGET_RUN_STAMP)
    return parser


def artifact_type(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    for suffix in ARTIFACT_SUFFIXES:
        if name.endswith(suffix):
            if suffix in {".cas", ".cas.h5"}:
                return "case", suffix
            if suffix in {".dat", ".dat.h5"}:
                return "data", suffix
            return "report_file", suffix
    return "other", ""


def canonical_name(path: Path, suffix: str) -> str:
    name = path.name
    stem = name[: -len(suffix)] if suffix else name
    return re.sub(r"_\d+_1$", "", stem)


def iso_mtime(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        return None


def parse_report_file(path: Path) -> dict[str, Any]:
    """Read only numeric-row metadata from a Fluent text Report File."""
    result: dict[str, Any] = {
        "point_count": 0,
        "first_iteration": None,
        "last_iteration": None,
        "first_value": None,
        "last_value": None,
        "parse_error": None,
    }
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = NUMBER_RE.match(line)
                if not match:
                    continue
                iteration = int(float(match.group(1)))
                value = float(match.group(2))
                if result["point_count"] == 0:
                    result["first_iteration"] = iteration
                    result["first_value"] = value
                result["point_count"] += 1
                result["last_iteration"] = iteration
                result["last_value"] = value
    except (OSError, UnicodeError, ValueError) as error:
        result["parse_error"] = f"{type(error).__name__}: {error}"
    return result


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def discover_file(path: Path, roots: list[Path], target_run_stamp: str) -> dict[str, Any]:
    kind, suffix = artifact_type(path)
    path_text = path.as_posix()
    filename_stage3 = bool(STAGE3_NAME_RE.search(path_text))
    branch_match = BRANCH_RE.search(path_text)
    branch_token = branch_match.group(0).upper() if branch_match else None
    run_stamp_match = target_run_stamp in path_text
    known_run_stamps = sorted(set(RUN_STAMP_RE.findall(path_text)))
    if run_stamp_match and branch_token:
        classification = "server2_fixed_queue_candidate_requires_positive_case_data_proof"
        do_not_use = True
    elif filename_stage3:
        classification = "found_local_but_unmapped_to_server2_fixed_queue"
        do_not_use = True
    else:
        classification = "found_local_outside_server2_stage3_filename_scope"
        do_not_use = True

    record: dict[str, Any] = {
        "kind": kind,
        "path": str(path.resolve()),
        "filename": path.name,
        "canonical_name": canonical_name(path, suffix),
        "suffix": suffix,
        "size_bytes": None,
        "mtime_utc": iso_mtime(path),
        "matches_03a_stage3_name": filename_stage3,
        "branch_token": branch_token,
        "target_run_stamp": target_run_stamp,
        "target_run_stamp_match": run_stamp_match,
        "other_run_stamps_in_path": known_run_stamps,
        "classification": classification,
        "do_not_use_as_server2_branch_history": do_not_use,
        "search_root": None,
        "relative_to_search_root": None,
    }
    try:
        record["size_bytes"] = path.stat().st_size
    except OSError as error:
        record["parse_error"] = f"{type(error).__name__}: {error}"

    for root in roots:
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        record["search_root"] = str(root.resolve())
        record["relative_to_search_root"] = relative_to_root(path, root)
        break

    if kind == "report_file":
        record.update(parse_report_file(path))
    else:
        record.update(
            {
                "point_count": None,
                "first_iteration": None,
                "last_iteration": None,
                "first_value": None,
                "last_value": None,
                "parse_error": record.get("parse_error"),
            }
        )
    return record


def discover(roots: list[Path], target_run_stamp: str) -> dict[str, Any]:
    files: list[Path] = []
    missing_roots: list[str] = []
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            missing_roots.append(str(root))
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and artifact_type(path)[0] != "other"
        )
    files = sorted(set(files), key=lambda path: path.as_posix().lower())
    records = [discover_file(path, roots, target_run_stamp) for path in files]
    report_files = [record for record in records if record["kind"] == "report_file"]
    stage3_reports = [record for record in report_files if record["matches_03a_stage3_name"]]
    canonical_groups: dict[str, list[dict[str, Any]]] = {}
    for record in stage3_reports:
        canonical_groups.setdefault(record["canonical_name"], []).append(record)

    point_counts = [record["point_count"] for record in stage3_reports if record["point_count"] is not None]
    mtimes = [record["mtime_utc"] for record in stage3_reports if record["mtime_utc"]]
    case_data = [record for record in records if record["kind"] in {"case", "data"}]
    target_matches = [record for record in records if record["target_run_stamp_match"]]
    branch_matches = [record for record in records if record["branch_token"]]
    if stage3_reports or case_data:
        artifact_status = "found_unmapped_local_artifacts"
    else:
        artifact_status = "no_matching_local_artifacts_found"

    observations = {
        "stage3_report_file_count": len(stage3_reports),
        "stage3_report_canonical_name_count": len(canonical_groups),
        "stage3_report_copy_count_by_canonical_name": {
            name: len(items) for name, items in sorted(canonical_groups.items())
        },
        "stage3_report_point_count_min": min(point_counts) if point_counts else None,
        "stage3_report_point_count_max": max(point_counts) if point_counts else None,
        "stage3_report_mtime_utc_min": min(mtimes) if mtimes else None,
        "stage3_report_mtime_utc_max": max(mtimes) if mtimes else None,
        "case_file_count": sum(record["kind"] == "case" for record in case_data),
        "data_file_count": sum(record["kind"] == "data" for record in case_data),
        "target_run_stamp_match_count": len(target_matches),
        "branch_token_match_count": len(branch_matches),
    }
    return {
        "kind": "03a_stage3_local_artifact_discovery",
        "search_roots": [str(root.expanduser().resolve()) for root in roots],
        "missing_search_roots": missing_roots,
        "target_run_stamp": target_run_stamp,
        "artifact_status": artifact_status,
        "server2_fixed_queue_history_usable": False,
        "lineage_conclusion": (
            "Local Fluent artifacts were found, but the Stage-3-named report files have no "
            "server-2 fixed-queue run stamp or branch token. Their copies are short 25-point "
            "files and the case/data names identify P0/preinit/smoke artifacts. They are "
            "preserved as discovery evidence only and must not be used as F02/F04/F05/F06/F11 "
            "late-window histories."
        ),
        "observations": observations,
        "files": records,
    }


CSV_COLUMNS = [
    "kind",
    "path",
    "filename",
    "canonical_name",
    "suffix",
    "size_bytes",
    "mtime_utc",
    "matches_03a_stage3_name",
    "branch_token",
    "target_run_stamp",
    "target_run_stamp_match",
    "other_run_stamps_in_path",
    "classification",
    "do_not_use_as_server2_branch_history",
    "search_root",
    "relative_to_search_root",
    "point_count",
    "first_iteration",
    "last_iteration",
    "first_value",
    "last_value",
    "parse_error",
]


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for record in records:
            row = dict(record)
            if isinstance(row.get("other_run_stamps_in_path"), list):
                row["other_run_stamps_in_path"] = ";".join(row["other_run_stamps_in_path"])
            writer.writerow({column: row.get(column) for column in CSV_COLUMNS})


def main() -> int:
    args = build_parser().parse_args()
    roots = args.search_root or [DEFAULT_SEARCH_ROOT]
    payload = discover(roots, args.target_run_stamp)
    output_json = args.output_json.expanduser().resolve()
    output_csv = args.output_csv.expanduser().resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(output_csv, payload["files"])
    print(
        json.dumps(
            {
                "output_json": str(output_json),
                "output_csv": str(output_csv),
                "artifact_status": payload["artifact_status"],
                "observations": payload["observations"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
