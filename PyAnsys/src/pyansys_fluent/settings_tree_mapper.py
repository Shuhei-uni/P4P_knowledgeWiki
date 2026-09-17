"""Retired generic mapper; retained entry point for explicit historical replay only.

New discovery belongs to pyfluent-mcp. There is no automatic direct-PyFluent
fallback when MCP is unavailable. The original implementation remains verbatim
under PyAnsys/legacy/ to preserve historical setup provenance.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import warnings


def _legacy():
    if os.environ.get("P4P_ALLOW_LEGACY_TREE_MAPPER") != "1":
        raise RuntimeError("P4P's generic tree mapper is retired. Use fluent-live-inspection and MCP describe_path. Historical replay requires explicit review and P4P_ALLOW_LEGACY_TREE_MAPPER=1.")
    warnings.warn("Historical tree mapper may activate parents. Use only a reviewed replay in an owned session, never as MCP fallback.", RuntimeWarning, stacklevel=3)
    path = Path(__file__).resolve().parents[2] / "legacy" / "settings_tree_mapper.py"
    spec = importlib.util.spec_from_file_location("p4p_legacy_tree_mapper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Historical tree mapper is unavailable.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture_settings_tree(*args, **kwargs):
    return _legacy().capture_settings_tree(*args, **kwargs)


def compare_tree_shapes(*args, **kwargs):
    return _legacy().compare_tree_shapes(*args, **kwargs)
