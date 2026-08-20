# Codex Remote Fluent Workflow Reference

This project uses PyFluent from the laptop to control Fluent running on a licensed workstation.

```text
Codex + Python on laptop
        |
        | gRPC
        v
Ansys Fluent on workstation
```

## Connection

Use `connect_to_fluent`, not `launch_fluent`, when Fluent is running remotely.

```python
import ansys.fluent.core as pyfluent

solver = pyfluent.connect_to_fluent(
    ip=ip,
    port=port,
    password=password,
    allow_remote_host=True,
    cleanup_on_exit=False,
    start_transcript=True,
)
```

or connect with a `server_info.txt` file.

Paths passed to Fluent are normally interpreted on the Fluent computer. Keep `.env` and `server_info.txt` out of git.

## Basic sequence

```bash
.venv/bin/python scripts/connection/local_preflight.py
.venv/bin/python scripts/connection/check_connection.py
.venv/bin/python scripts/inspection/inspect_fluent_session.py
```

Build project-specific mutation code only after the connection and live state are understood.

## Setup versus run

The default setup deliverable is a verified `.cas.h5`.

After setup creation, make a separate run plan and choose one of three modes:

1. **Simple TUI** — one prepared case and one uninterrupted run.
2. **Fluent journal** — multiple independent cases or a predetermined sequence.
3. **Agent-owned Python** — staged/adaptive runs where intermediate evidence determines the next action.

Use Fluent-native autosave/checkpoints whenever losing progress would be costly, regardless of mode.

For Python-supervised runs, provide the exact launch command and a supervisor/resume guide rather than expecting another agent to infer the state machine from source code.

Detailed policy: `knowledge/fluent-settings/native_run_and_autosave.md`.

## Useful tools

- `scripts/connection/check_connection.py` — connection health/preflight
- `scripts/inspection/inspect_fluent_session.py` — non-mutating live inspection
- `scripts/inspection/monitor_native_run.py` — optional read-only monitoring
- `knowledge/fluent-settings/` — live-tree/dependency/run guidance
- `src/pyansys_fluent/` — reusable Fluent automation helpers

## Storage

Treat `PyAnsys/output/` as temporary/generated evidence. Keep only artifacts that still support checks, analysis, reports, plots, reproducibility or active debugging. Remove stale snapshots, duplicate exports and other regenerable bulk after handoff.
