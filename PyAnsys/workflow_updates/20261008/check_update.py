"""Validate staged source and base hashes offline. This command never installs."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    bundle = Path(__file__).resolve().parent
    root = bundle.parents[2]
    manifest = json.loads((bundle / "manifest.json").read_text())
    failures = []
    for item in manifest["files"]:
        current = root / item["path"]
        staged = bundle / item["staged_path"]
        if hashlib.sha256(current.read_bytes()).hexdigest() != item["base_sha256"]:
            failures.append({"path": item["path"], "reason": "base changed; regenerate patch"})
        if hashlib.sha256(staged.read_bytes()).hexdigest() != item["staged_sha256"]:
            failures.append({"path": item["path"], "reason": "staged source changed"})
        ast.parse(staged.read_text(), filename=str(staged))
    checked = subprocess.run(["git", "apply", "--check", str(bundle / "changes.patch")],
                             cwd=root, capture_output=True, text=True, timeout=10, check=False)
    if checked.returncode:
        failures.append({"reason": "git apply --check failed"})
    processes = subprocess.run(["ps", "-axo", "pid=,state=,command="],
                               capture_output=True, text=True, timeout=5, check=True)
    protected = []
    for line in processes.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3 or parts[1].startswith("Z"):
            continue
        if any(str(root / item["path"]) in parts[2] for item in manifest["files"]):
            protected.append(int(parts[0]))
    print(json.dumps({"status": "PASS" if not failures else "FAIL", "failures": failures,
                      "runtime_installation": "BLOCKED_ACTIVE_PROCESSES" if protected else "IDLE_RECONCILIATION_REQUIRED",
                      "protected_processes": protected, "installed": False}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
