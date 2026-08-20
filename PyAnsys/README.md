# PyAnsys / PyFluent Remote Fluent Kit

`PyAnsys/` is the executable layer for controlling a remote Fluent session through PyFluent/gRPC/TUI.

The key model is simple: Fluent is a dependency-ordered live state machine, not a flat Python API.

## Workflow split

Keep three responsibilities separate:

1. **setup building** — create/modify and verify the `.cas.h5`;
2. **run planning** — choose simple TUI, Fluent journal, or agent-owned Python;
3. **run execution** — run, recover, monitor, and hand off evidence.

See [`AGENTS.md`](./AGENTS.md) for the operating rules and [`knowledge/fluent-settings/native_run_and_autosave.md`](./knowledge/fluent-settings/native_run_and_autosave.md) for run-mode/recovery guidance.

## Environment

Recommended local target:

```text
CPython 3.12
PyAnsys/.venv
PyFluent core + visualization
connect_to_fluent workflow
```

Architecture:

```text
Laptop: Codex + Python + PyFluent
        |
        | gRPC
        v
Fluent PC: Ansys Fluent + gRPC server
```

Bootstrap locally with:

```bash
python3 scripts/connection/bootstrap_local_env.py
```

When Fluent is available:

```bash
.venv/bin/python scripts/connection/check_connection.py
.venv/bin/python scripts/inspection/inspect_fluent_session.py
```

## Setup mutation pattern

Read the relevant material under `knowledge/fluent-settings/`, then use:

```text
connect
-> verify inputs
-> load mesh/case
-> enable/create parent
-> reacquire
-> inspect active children/options
-> set
-> read back
-> classify/fallback if needed
-> write verified .cas.h5
```

Do not infer case identity from the connection/server alias.

## Run planning

Choose the simplest mode that fits the experiment:

- **Simple TUI** — one prepared case, no mid-run decision.
- **Fluent journal** — multiple independent cases or a predetermined sequence.
- **Agent-owned Python** — staged/adaptive runs where intermediate evidence changes what happens next.

For complex Python-supervised runs, provide the exact command plus supervisor, checkpoint and resume instructions.

## Useful layout

- `scripts/connection/` — bootstrap and connection checks
- `scripts/inspection/` — live/read-only discovery and analysis
- `scripts/setup/` — case-specific setup/run orchestration
- `src/pyansys_fluent/` — reusable helpers
- `knowledge/fluent-settings/` — dependency/path/run knowledge
- `extractors/` — reusable case/data extraction
- `output/` — temporary/generated evidence, not an archive

Keep `output/` small. Retain only artifacts that still support checks, analysis, result reports, plots, reproducibility or active debugging; remove stale/redundant generated bulk when it is no longer needed.

## Remote-path note

Paths passed to Fluent are normally interpreted on the Fluent computer. Keep connection secrets such as `.env` and `server_info.txt` out of git.
