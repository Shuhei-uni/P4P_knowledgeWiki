#!/usr/bin/env python3
"""Check active Markdown links without treating history or code as note links."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!\!)\[[^\]\n]*\]\(([^)\n]+)\)")
INLINE_CODE = re.compile(r"`+[^`\n]+`+")
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PATH_LITERAL_SUFFIXES = {".json", ".jou", ".py", ".sh", ".toml", ".yaml", ".yml"}

# These are provenance/debug surfaces, not active navigation authorities.
EXCLUDED_PREFIXES = (
    ".obsidian",
    "PyAnsys/cases",
    "PyAnsys/output",
    "PyAnsys/queues",
    "ResearchProject_wiki/observations",
    "ResearchProject_wiki/wiki/log.md",
    "Setups/archived",
    "Setups/compatibility-snapshots",
    "Setups/past",
    "Setups/reports/purnanto-reference",
)

# Existing files in these paths are compatibility/reference surfaces. A missing
# target under one of them is historical provenance, not an active-link failure.
COMPATIBILITY_PREFIXES = (
    "Setups/active",
    "Setups/archived",
    "Setups/compatibility-snapshots",
    "Setups/future",
    "Setups/past",
    "Setups/reports/purnanto-reference",
)
DIRECT_NUMBERED_REPORT = re.compile(
    r"(?:^|/)Setups/reports/(?:\d{2}|\d+[A-Za-z][^/]*)(?:/|$)"
)

HISTORICAL_PREFIXES = (
    ".obsidian",
    "PyAnsys/cases",
    "PyAnsys/output",
    "PyAnsys/queues",
    "ResearchProject_wiki/observations",
    "ResearchProject_wiki/wiki/log.md",
)


@dataclass(frozen=True)
class LinkResult:
    source: Path
    line: int
    target: str
    status: str
    resolved: Path | None


def repo_relative(path: Path) -> str:
    """Return a stable repository-relative path for display and matching."""

    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def under_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    normalized = path.lstrip("./")
    return any(
        normalized == prefix
        or normalized.startswith(f"{prefix}/")
        or f"/{prefix}/" in f"/{normalized}"
        for prefix in prefixes
    )


def excluded(path: Path) -> bool:
    return under_prefix(repo_relative(path), EXCLUDED_PREFIXES)


def markdown_files() -> list[Path]:
    """Yield active Markdown files from the small, maintained scan surface."""

    roots = (
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "Project",
        ROOT / "docs",
        ROOT / "ResearchProject_wiki" / "wiki",
        ROOT / "Setups",
        ROOT / "PyAnsys" / "docs",
        ROOT / "skills",
    )
    files: set[Path] = set()
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".md":
            candidates = (root,)
        elif root.is_dir():
            candidates = root.rglob("*.md")
        else:
            candidates = ()
        for path in candidates:
            resolved = path.resolve()
            if not excluded(resolved):
                files.add(resolved)
    return sorted(files)


def parse_destination(raw: str) -> str:
    """Parse the destination part of one ordinary Markdown link."""

    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        value = value.split(None, 1)[0]
    return unquote(value)


def target_path(source: Path, target: str) -> Path:
    if target.startswith("/"):
        return Path(target).resolve()
    return (source.parent / target).resolve()


def historical_path(path: str) -> bool:
    return under_prefix(path, HISTORICAL_PREFIXES) or under_prefix(path, COMPATIBILITY_PREFIXES)


def compatibility_path(path: str) -> bool:
    return under_prefix(path, COMPATIBILITY_PREFIXES) or bool(
        DIRECT_NUMBERED_REPORT.search(path)
    )


def redirect_note(path: Path) -> bool:
    """Recognise a deliberately retained redirect without parsing its links."""

    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:4000].lower()
    except OSError:
        return False
    return any(
        marker in head
        for marker in ("compatibility redirect", "redirect only", "legacy for new work")
    )


def classify(source: Path, target: str) -> LinkResult:
    raw_path = target.split("#", 1)[0].split("?", 1)[0]
    if not raw_path:
        return LinkResult(source, 0, target, "INTERNAL_ANCHOR", None)
    if URI_SCHEME.match(raw_path):
        return LinkResult(source, 0, target, "EXTERNAL_URL", None)

    candidate = target_path(source, raw_path)
    candidates = [candidate]
    if not candidate.exists() and candidate.suffix == "":
        candidates.append(candidate.with_suffix(".md"))
    resolved = next((item for item in candidates if item.exists()), None)
    resolved_rel = repo_relative(resolved) if resolved else repo_relative(candidate)
    compatibility_target = compatibility_path(resolved_rel)
    historical_target = historical_path(resolved_rel) or compatibility_target
    literal_target = Path(raw_path).suffix.lower() in PATH_LITERAL_SUFFIXES

    if resolved is None:
        if compatibility_target:
            status = "MISSING_COMPATIBILITY_REFERENCE"
        elif historical_target:
            status = "HISTORICAL_ARTIFACT_REFERENCE"
        elif literal_target:
            status = "MISSING_ACTIVE_PATH_LITERAL"
        else:
            status = "MISSING_ACTIVE_NOTE_LINK"
        return LinkResult(source, 0, target, status, None)

    if historical_target:
        status = (
            "EXISTS_COMPATIBILITY_REDIRECT"
            if compatibility_target or redirect_note(resolved)
            else "HISTORICAL_ARTIFACT_REFERENCE"
        )
    elif literal_target:
        status = "PATH_LITERAL_PROVENANCE"
    elif redirect_note(resolved):
        status = "EXISTS_COMPATIBILITY_REDIRECT"
    elif repo_relative(resolved).startswith("/"):
        status = "OUTSIDE_VAULT"
    else:
        status = "EXISTS_CANONICAL"
    return LinkResult(source, 0, target, status, resolved)


def active_markdown_lines(lines: list[str]) -> list[str]:
    """Remove fenced and inline code so examples are not treated as links."""

    in_fence = False
    active: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            active.append("")
        elif in_fence:
            active.append("")
        else:
            active.append(INLINE_CODE.sub("", line))
    return active


def scan() -> list[LinkResult]:
    results: list[LinkResult] = []
    for source in markdown_files():
        try:
            lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print(f"could not read {repo_relative(source)}: {exc}", file=sys.stderr)
            continue
        for line_number, line in enumerate(active_markdown_lines(lines), start=1):
            for match in MARKDOWN_LINK.finditer(line):
                target = parse_destination(match.group(1))
                result = classify(source, target)
                results.append(
                    LinkResult(
                        source=result.source,
                        line=line_number,
                        target=result.target,
                        status=result.status,
                        resolved=result.resolved,
                    )
                )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve active Markdown link destinations relative to their source note. "
            "Python/YAML/JSON literals are reported separately when linked."
        )
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="show canonical links and external URLs as well as warnings",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="return 1 when an active link or path literal is missing",
    )
    args = parser.parse_args()

    results = scan()
    quiet_statuses = {"EXISTS_CANONICAL", "EXTERNAL_URL", "INTERNAL_ANCHOR"}
    for result in results:
        if not args.all and result.status in quiet_statuses:
            continue
        destination = repo_relative(result.resolved) if result.resolved else "missing"
        print(
            f"{repo_relative(result.source)}:{result.line}: "
            f"{result.status}: {result.target} -> {destination}"
        )

    counts = Counter(result.status for result in results)
    print(f"Scanned {len(markdown_files())} active Markdown files and {len(results)} links.")
    for status in sorted(counts):
        print(f"{status}: {counts[status]}")

    if args.fail_on_missing and any(
        result.status in {"MISSING_ACTIVE_NOTE_LINK", "MISSING_ACTIVE_PATH_LITERAL"}
        for result in results
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
