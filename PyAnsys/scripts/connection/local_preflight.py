#!/usr/bin/env python3
"""Local preflight check.

Run this now on your laptop. It does NOT require Fluent.
It checks Python version and imports the packages you want Codex to use.
"""

from __future__ import annotations

import importlib
import platform
import sys


PACKAGES = [
    ("ansys.fluent.core", "PyFluent / ansys-fluent-core"),
    ("ansys.fluent.visualization", "PyFluent-Visualization"),
    ("pyvista", "PyVista"),
    ("matplotlib", "Matplotlib"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("dotenv", "python-dotenv"),
    ("yaml", "PyYAML"),
]


OPTIONAL_PACKAGES = [
    ("ansys.meshing.prime", "PyPrimeMesh / ansys-meshing-prime"),
    ("ansys.dpf.core", "PyDPF-Core"),
]


def import_check(module_name: str, label: str) -> bool:
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "installed")
        print(f"[OK] {label}: {version}")
        return True
    except Exception as exc:
        print(f"[MISSING/ERROR] {label}: {exc}")
        return False


def main() -> int:
    print("=== Local PyAnsys / PyFluent preflight ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print()

    ok = True
    for module_name, label in PACKAGES:
        ok = import_check(module_name, label) and ok

    print("\nOptional packages:")
    for module_name, label in OPTIONAL_PACKAGES:
        import_check(module_name, label)

    print("\nNotes:")
    print("- This preflight does not connect to Fluent.")
    print("- Connection can only be tested once the Fluent PC has started the gRPC server.")
    print("- If required packages are missing, run: python -m pip install -r requirements-minimal.txt")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
