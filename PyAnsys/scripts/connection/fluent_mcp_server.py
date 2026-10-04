#!/usr/bin/env python3
"""Launch the P4P-preserving upstream MCP server, not Fluent itself."""
from pathlib import Path
import contextlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pyansys_fluent.connection import build_parser


def main() -> None:
    args = build_parser().parse_args()
    # Import native libraries before the STDIO reader threads start on Windows.
    # Keep startup output off the MCP protocol stream.
    with contextlib.redirect_stdout(sys.stderr):
        import ansys.fluent.core
    from pyansys_fluent.mcp_server import P4PFluentMCP
    P4PFluentMCP(args.server_id).run(transport="stdio")


if __name__ == "__main__":
    main()
