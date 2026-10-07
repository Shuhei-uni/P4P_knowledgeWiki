"""Bounded local evidence reads; no Fluent, network, watcher, or controller calls."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time


def read_json(path, *, max_bytes=64 * 1024 * 1024):
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise ValueError("JSON exceeds the read limit; select a smaller owning receipt")
    return json.loads(path.read_text())


def json_pointer(value, pointer):
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValueError("Use an RFC 6901 JSON pointer beginning with /")
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                raise ValueError("JSON array pointers require a nonnegative index")
            value = value[int(part)]
        else:
            value = value[part]
    return value


def markdown_section(path, heading):
    """Read one exact heading and its children, with source line numbers."""
    lines = Path(path).read_text().splitlines()
    headings, fence = [], None
    for i, line in enumerate(lines):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None and (m := re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)):
            headings.append((i, len(m[1]), m[2]))
    matches = [(i, level) for i, level, title in headings
               if lines[i].strip() == heading.strip() or title == heading.strip()]
    if len(matches) != 1:
        raise ValueError("Heading must identify exactly one section")
    begin, level = matches[0]
    end = len(lines)
    for i, next_level, _ in headings:
        if i > begin and next_level <= level:
            end = i
            break
    return {"path": str(path), "start_line": begin + 1, "end_line": end,
            "text": "\n".join(lines[begin:end])}


def tail_file(path, *, max_bytes=16384):
    if max_bytes <= 0:
        raise ValueError("Tail size must be positive")
    path = Path(path)
    with path.open("rb") as stream:
        size = path.stat().st_size
        start = max(0, size - max_bytes)
        stream.seek(start)
        text = stream.read(max_bytes).decode(errors="replace")
    if start:
        text = text.partition("\n")[2]
    return text, max(0, time.time() - path.stat().st_mtime)


def campaign_status(output_root, *, expected_controller=None):
    """Read one campaign snapshot; saved evidence is not a live Fluent readback."""
    root = Path(output_root)
    warnings = []

    def read(name):
        try:
            value = read_json(root / name)
            if not isinstance(value, dict):
                raise ValueError("Receipt must be an object")
            return value
        except (OSError, ValueError) as exc:
            warnings.append({"file": name, "error_type": type(exc).__name__})
            return {}

    receipt = read("desktop-controller.json")
    campaign = read("campaign-manifest.json")
    mesh = campaign.get("active_mesh")
    child = read(f"{mesh}-run.json") if isinstance(mesh, str) and re.fullmatch(r"[\w.-]+", mesh) else {}
    live, age = "", None
    try:
        if receipt.get("live_transcript"):
            live, age = tail_file(receipt["live_transcript"])
    except OSError as exc:
        warnings.append({"file": "live_transcript", "error_type": type(exc).__name__})
    rows = re.findall(r"^\s*(\d+)\s+[\d.+eE-]+\s+[\d.+eE-]+", live, re.M)
    running = None
    pid = receipt.get("pid")
    if type(pid) is int and pid > 0 and expected_controller:
        try:
            process = subprocess.run(["ps", "-p", str(pid), "-o", "state=,command="],
                                     capture_output=True, text=True, timeout=3, check=False)
            line = process.stdout.strip()
            running = bool(line) and not line.startswith("Z") and expected_controller in line
        except (OSError, subprocess.TimeoutExpired) as exc:
            warnings.append({"file": "controller_process", "error_type": type(exc).__name__})
    pair = child.get("latest_pair", {})
    screens = child.get("hold_screens", [])
    return {"observed_utc": datetime.now(timezone.utc).isoformat(),
            "evidence_scope": "local receipts and bounded transcript tail; no Fluent query",
            "server_id": receipt.get("server_id"), "controller_pid": pid,
            "controller_alive": running, "campaign_status": campaign.get("status"),
            "active_mesh": mesh, "child_status": child.get("status"),
            "verified_native_end": child.get("verified_native_end"),
            "last_streamed_iteration": int(rows[-1]) if rows else None,
            "transcript_age_seconds": age, "active_target": child.get("active_target"),
            "latest_pair_iteration": pair.get("native_iteration") if isinstance(pair, dict) else None,
            "latest_hold_screen": screens[-1] if screens else None,
            "requires_desktop_running": receipt.get("requires_desktop_running"),
            "warnings": warnings}
