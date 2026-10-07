#!/usr/bin/env python3
"""Read narrow evidence or probe an explicit local/host Python; never attach to Fluent."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent.execution_contract import probe_runtime, verify_drain_probe
from pyansys_fluent.workflow_evidence import campaign_status, json_pointer, markdown_section, read_json, tail_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-chars", type=int, default=6000)
    sub = parser.add_subparsers(dest="command", required=True)
    js = sub.add_parser("json")
    js.add_argument("file")
    js.add_argument("--pointer", action="append", required=True)
    md = sub.add_parser("section")
    md.add_argument("file")
    md.add_argument("--heading", required=True)
    tail = sub.add_parser("tail")
    tail.add_argument("file")
    tail.add_argument("--bytes", type=int, default=16384)
    status = sub.add_parser("status")
    status.add_argument("output_root")
    status.add_argument("--controller-name")
    runtime = sub.add_parser("runtime")
    runtime.add_argument("--python", required=True)
    runtime.add_argument("--module", action="append", default=[])
    runtime.add_argument("--extra-path", action="append", default=[])
    runtime.add_argument("--timeout", type=float, default=5)
    drain = sub.add_parser("drain-proof")
    drain.add_argument("file")
    drain.add_argument("--setup-identity", required=True)
    drain.add_argument("--frozen-bulk", action="store_true")
    args = parser.parse_args()
    if args.max_chars < 200:
        parser.error("--max-chars must be at least 200")
    try:
        if args.command == "json":
            value = read_json(args.file)
            result = {p: json_pointer(value, p) for p in args.pointer}
        elif args.command == "section":
            result = markdown_section(args.file, args.heading)
        elif args.command == "tail":
            text, age = tail_file(args.file, max_bytes=args.bytes)
            result = {"text": text, "age_seconds": age}
        elif args.command == "status":
            result = campaign_status(args.output_root, expected_controller=args.controller_name)
        elif args.command == "runtime":
            result = probe_runtime(args.python, args.module, extra_paths=args.extra_path, timeout=args.timeout)
        else:
            result = verify_drain_probe(read_json(args.file), setup_identity=args.setup_identity,
                                        frozen_bulk=args.frozen_bulk)
        rendered = json.dumps(result, indent=2, allow_nan=False)
        if len(rendered) > args.max_chars:
            print(json.dumps({"status": "OUTPUT_LIMIT", "characters": len(rendered),
                              "action": "Select narrower pointers or a smaller section; no partial JSON returned"}))
            return 2
        print(rendered)
        return 1 if result.get("status") in {"UNAVAILABLE", "UNVERIFIED"} else 0
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print(json.dumps({"status": "READ_FAILED", "error_type": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
