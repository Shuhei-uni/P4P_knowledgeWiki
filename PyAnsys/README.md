# PyAnsys / PyFluent remote Fluent kit

PyAnsys owns executable Fluent implementation, live inspection, Python-supervised execution, and machine-readable evidence checks. Project-specific scientific truth remains in `../Project/`; reusable CFD and literature knowledge remains in `../CFD_wiki/`.

The operating rule is simple: Fluent is a dependency-ordered state machine, and autonomous-loop runs default to a Python/PyFluent runner supervised by an agent for the full planned horizon. TUI-driven iteration, Fluent journal submission, and GUI-owned execution require explicit human approval for that run.

## Start here

1. Read the selected Project setup and results packet.
2. Read the applicable focused skill under `../.agents/skills/`.
3. Read [the current run supervision and recovery policy](knowledge/fluent-settings/native_run_and_autosave.md).
4. Use the proven source module or script, then inspect critical live values and identity before changing anything.

## Canonical workflow

```text
selected Project setup/results
    -> focused skill and proven source path
    -> connect and verify explicit remote inputs
    -> load case or mesh
    -> enable/change in dependency order
    -> reacquire, inspect, set, and read back critical values
    -> write and reload-verify the case artifact
    -> short Python/PyFluent smoke test
    -> Python runner supervised by agent
    -> verify final data and execution state
    -> hand off to numerical analysis / Project interpretation
```

Use `supervise-fluent-run` for the long-lived execution period. The agent should mostly wait while Fluent advances, wake on meaningful execution events, and never turn poor residuals or unexpected physics into an unapproved mid-run experiment change.

## Connection and run tools

- `scripts/connection/check_connection.py` — endpoint health check.
- `scripts/connection/local_preflight.py` — local runtime and endpoint preflight.
- `scripts/inspection/inspect_fluent_session.py` — non-mutating live tree inspection.
- `scripts/inspection/monitor_native_run.py` — legacy-named reconnecting read-only monitor that can supplement the supervising agent.
- `scripts/setup/` — case-specific Python setup/run orchestration. Prefer a proven runner when one matches the approved experiment; otherwise keep new runners thin and explicit.
- `scripts/setup/generate_native_run_journal.py` and other journal/native-queue tools — retained for historical or human-approved exception use; not autonomous-loop defaults.
- `scripts/inspection/post_simulation_analysis.py` — selected read-only residual, flux, and results-evidence checks.

The remaining setup and inspection scripts are kept when they support a current Project experiment, a focused skill, a reusable source module, or unique evidence recovery. Campaign-specific scripts are not a general API.

## Source layout

- `src/pyansys_fluent/` — reusable connection, setup, extraction, monitoring, and evidence logic.
- `scripts/connection/` — connection and local-environment checks.
- `scripts/inspection/` — non-mutating discovery, snapshots, monitors, and post-processing.
- `scripts/setup/` — thin setup and Python-supervised run orchestration.
- `server-profiles/` — non-secret per-server remote directory knowledge.
- `knowledge/fluent-settings/native_run_and_autosave.md` — current run supervision, autosave, recovery, and exception policy.
- `cases/actual_setup_archives/` — small unique live-case exports retained for exact setup reconciliation; Project records own their interpretation.
- `output/` — generated extracts and diagnostics, never the scientific authority.

## Local runtime

From this directory, use `.venv/bin/python` when the repository runtime exists. The optional bootstrap script can create a local environment:

```bash
python3 scripts/connection/bootstrap_local_env.py
```

Do not commit `.env`, `.venv/`, cache files, remote case/data files, or generated output. Do not edit any `raw/` directory.
