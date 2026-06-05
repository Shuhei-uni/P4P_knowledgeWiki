#!/usr/bin/env python3
"""Parse a Fluent server_info.txt file.

Usage:
    python scripts/parse_server_info.py ./server_info.txt
"""

from __future__ import annotations

import sys
from pathlib import Path


def parse_server_info(path: Path) -> tuple[str, int, str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]

    if len(lines) < 2:
        raise ValueError("Expected at least two non-empty lines: '<ip>:<port>' and '<password>'.")

    host_port = lines[0]
    password = lines[1]

    if ":" not in host_port:
        raise ValueError(f"First line should look like '<ip>:<port>', got: {host_port!r}")

    host, port_text = host_port.rsplit(":", 1)
    return host.strip(), int(port_text), password.strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/parse_server_info.py ./server_info.txt")
        return 2

    path = Path(sys.argv[1]).expanduser()
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    host, port, password = parse_server_info(path)

    print("Parsed Fluent server-info file:")
    print(f"FLUENT_IP={host}")
    print(f"FLUENT_PORT={port}")
    print(f"FLUENT_PASSWORD={password}")

    if host in {"127.0.0.1", "localhost"}:
        print("\nWARNING:")
        print("The host is localhost/127.0.0.1. From your laptop, this points to your laptop, not the Fluent PC.")
        print("Use the Fluent PC's real IPv4 address from ipconfig instead.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
