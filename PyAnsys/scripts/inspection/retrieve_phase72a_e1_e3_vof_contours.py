"""Retrieve previously exported Fluent PNGs from student via ASCII base64 RPC."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PureWindowsPath
from pyansys_fluent.common import quote_scheme_string, remote_file_exists
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("E0", "E1", "E3"), help="Retrieve one case; default is the original E1/E3 pair")
    args = parser.parse_args()
    cases = (args.case,) if args.case else ("E1", "E3")
    output_dir = (ROOT / "PyAnsys/output/phase72a_e0_native_vof_contour_20260923") if args.case == "E0" else OUT
    manifest_path = output_dir / "export-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "EXPORTED_NATIVE_FLUENT_AWAIT_LOCAL_QA"
    solver = connect("student", start_transcript=False, tcp_timeout_seconds=5)
    for case in cases:
        info = manifest["cases"][case]
        source = info["remote_png"]
        encoded_path = source + ".base64.txt"
        assert remote_file_exists(solver, source)
        if not remote_file_exists(solver, encoded_path):
            powershell = (
                f"[IO.File]::WriteAllText('{encoded_path}',"
                f"[Convert]::ToBase64String([IO.File]::ReadAllBytes('{source}')))"
            )
            encoded_command = base64.b64encode(powershell.encode("utf-16le")).decode("ascii")
            command = f"cmd /c powershell -NoProfile -EncodedCommand {encoded_command}"
            solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
        encoded = read_text(solver, encoded_path)
        payload = base64.b64decode(encoded, validate=True)
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        path = output_dir / PureWindowsPath(source).name
        if path.exists():
            assert path.read_bytes() == payload
        else:
            path.write_bytes(payload)
        info["local_png"] = str(path.relative_to(ROOT))
        info["png_sha256"] = hashlib.sha256(payload).hexdigest()
        info["png_bytes"] = len(payload)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    manifest["status"] = "LOCAL_PNGS_RETRIEVED_AWAIT_VISUAL_QA"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({c: manifest["cases"][c]["local_png"] for c in cases}, indent=2))


if __name__ == "__main__":
    main()
