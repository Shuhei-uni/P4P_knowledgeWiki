#!/usr/bin/env python3
"""Create a local PyAnsys-ready virtual environment for remote Fluent work."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
ENV_TEMPLATE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"
MINIMAL_REQUIREMENTS = PROJECT_ROOT / "requirements-minimal.txt"
EXTENDED_REQUIREMENTS = PROJECT_ROOT / "requirements-extended.txt"
PREFERRED_PYTHON = "3.12"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print(f"\n>>> {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, check=True)


def venv_python_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def detect_existing_venv_python() -> Path | None:
    python_path = venv_python_path()
    if not python_path.exists():
        return None

    cmd = [
        str(python_path),
        "-c",
        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
    ]
    completed = subprocess.run(cmd, capture_output=True, check=True, text=True)
    version = completed.stdout.strip()
    if version == PREFERRED_PYTHON:
        return python_path
    return None


def find_python312() -> str | None:
    return shutil.which("python3.12")


def find_uv() -> str | None:
    return shutil.which("uv")


def create_venv(args: argparse.Namespace) -> Path:
    if args.recreate and VENV_DIR.exists():
        print(f"Removing existing virtual environment: {VENV_DIR}", flush=True)
        shutil.rmtree(VENV_DIR)

    existing = detect_existing_venv_python()
    if existing is not None:
        print(
            f"Reusing existing Python {PREFERRED_PYTHON} virtual environment: {existing}",
            flush=True,
        )
        return existing

    python312 = find_python312()
    if python312:
        run([python312, "-m", "venv", str(VENV_DIR)])
        venv_python = venv_python_path()
        run([str(venv_python), "-m", "ensurepip", "--upgrade"])
        return venv_python

    uv = find_uv()
    if uv:
        run([uv, "venv", str(VENV_DIR), "--python", PREFERRED_PYTHON, "--seed"])
        return venv_python_path()

    raise RuntimeError(
        "Could not find python3.12 or uv.\n"
        "Install one of these first:\n"
        "- brew install python@3.12\n"
        "- brew install uv"
    )


def install_requirements(venv_python: Path, args: argparse.Namespace) -> None:
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(venv_python), "-m", "pip", "install", "-r", str(MINIMAL_REQUIREMENTS)])
    if args.extended:
        run([str(venv_python), "-m", "pip", "install", "-r", str(EXTENDED_REQUIREMENTS)])


def ensure_env_file() -> None:
    if ENV_FILE.exists():
        print(f"Keeping existing environment file: {ENV_FILE}", flush=True)
        return
    shutil.copyfile(ENV_TEMPLATE, ENV_FILE)
    print(f"Created {ENV_FILE.name} from {ENV_TEMPLATE.name}", flush=True)


def run_preflight(venv_python: Path) -> None:
    run([str(venv_python), str(PROJECT_ROOT / "scripts" / "local_preflight.py")])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap a local PyAnsys virtual environment for remote Fluent control."
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Also install the extended meshing and DPF dependencies.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and rebuild .venv even if one already exists.",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip the final import check.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    venv_python = create_venv(args)
    install_requirements(venv_python, args)
    ensure_env_file()

    if not args.skip_preflight:
        run_preflight(venv_python)

    activate_cmd = "source .venv/bin/activate" if os.name != "nt" else r".venv\Scripts\Activate.ps1"
    print("\nEnvironment is ready.", flush=True)
    print(f"Activate it with: {activate_cmd}", flush=True)
    print("When you reach the Fluent PC, start the gRPC server and then run:", flush=True)
    print("  .venv/bin/python scripts/check_connection.py", flush=True)
    print("  .venv/bin/python scripts/inspect_fluent_session.py", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
