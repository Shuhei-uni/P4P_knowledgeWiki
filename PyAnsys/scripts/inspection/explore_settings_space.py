#!/usr/bin/env python3
"""Inspect selected live paths through MCP. Loading/activation flags are retired."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pyansys_fluent.mcp_inspection import main

if __name__ == "__main__":
    raise SystemExit(main())
