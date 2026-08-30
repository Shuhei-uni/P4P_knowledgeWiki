# PyAnsys / PyFluent remote Fluent kit

PyAnsys owns executable Fluent implementation, live inspection, Python-supervised execution, and machine-readable evidence checks. Project-specific scientific truth remains in `../Project/`; reusable CFD and literature knowledge remains in `../CFD_wiki/`.

The operating rule is simple: Fluent is a dependency-ordered state machine, and autonomous-loop execution follows experiment mode. Discovery runs stay agent-attached through their short screening horizons so the same scientific thread can inspect evidence and choose the next probe immediately. Hypothesis-test runs use the detached self-waking worker, which verifies the terminal state and then resumes the exact originating Codex thread. TUI-driven iteration, Fluent journal submission, and GUI-owned execution require explicit human approval for that run.

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
    -> execute according to experiment mode

DISCOVERY:
    attached short run
    -> immediate evidence review
    -> next discovery probe in same active thread

HYPOTHESIS TEST:
    capture CODEX_THREAD_ID
    -> detached run-and-handoff worker
    -> Fluent completes or blocks
    -> verify final outputs and write terminal manifest
    -> mandatory resume of exact originating Codex thread
    -> numerical analysis / Project interpretation
```

Use `supervise-fluent-run` for long hypothesis-test execution. Discovery runs should not use that detached path merely to avoid waiting.

## Connection and run tools

- `scripts/connection/check_connection.py` — endpoint health check.
- `scripts/connection/local_preflight.py` — local runtime and endpoint preflight.
- `scripts/inspection/inspect_fluent_session.py` — non-mutating live tree inspection.
- `scripts/inspection/monitor_native_run.py` — reconnecting read-only monitor that can supplement execution evidence without becoming a mutating controller.
- `scripts/setup/` — case-specific Python setup/run orchestration. Prefer a proven runner when one matches the approved experiment; otherwise keep new runners thin and explicit.
- `scripts/orchestration/run_and_handoff.py` — detached hypothesis worker launcher. It captures the originating Codex thread, runs the approved runner, verifies declared completion evidence, writes a terminal manifest, and mandatorily attempts to wake the thread on `COMPLETE` or `BLOCKED`.
- `queues/run-and-handoff.example.yaml` — example hypothesis-test job contract.
- `scripts/setup/generate_native_run_journal.py` and other journal/native-queue tools — retained for historical or human-approved exception use; not autonomous-loop defaults.
- `scripts/inspection/post_simulation_analysis.py` — selected read-only residual, flux, and results-evidence checks.

The remaining setup and inspection scripts are kept when they support a current Project experiment, a focused skill, a reusable source module, or unique evidence recovery. Campaign-specific scripts are not a general API.

## Hypothesis handoff contract

Normal launch is:

```bash
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

The launcher resolves the originating thread from `CODEX_THREAD_ID` when the job is started from Codex, then starts the detached worker. An explicit `codex.session_id` is only an override.

A hypothesis job must declare at least one completion proof: locally visible required files and/or a deterministic verifier command. A zero runner exit code by itself cannot produce `COMPLETE`.

The worker's mandatory terminal Python tail uses:

```text
codex exec resume <ORIGINATING_THREAD_ID> <PROMPT>
```

on both `COMPLETE` and `BLOCKED`. Do not use `--last` for autonomous multi-server work because jobs can finish in a different order from launch order.

The generated job manifest is execution evidence only. Canonical scientific paths and server placement remain in the experiment's `Project/.../run-paths.yaml`.

## Source layout

- `src/pyansys_fluent/` — reusable connection, setup, extraction, monitoring, evidence, and run-handoff logic.
- `scripts/connection/` — connection and local-environment checks.
- `scripts/inspection/` — non-mutating discovery, snapshots, monitors, and post-processing.
- `scripts/setup/` — thin experiment-specific setup and Python/PyFluent runner orchestration.
- `scripts/orchestration/` — background hypothesis execution and event-driven Codex handoff.
- `server-profiles/` — non-secret per-server remote directory knowledge.
- `knowledge/fluent-settings/native_run_and_autosave.md` — current execution, autosave, recovery, verification, and handoff policy.
- `cases/actual_setup_archives/` — small unique live-case exports retained for exact setup reconciliation; Project records own their interpretation.
- `output/` — generated extracts and diagnostics, never the scientific authority.

## Local runtime

From this directory, use `.venv/bin/python` when the repository runtime exists. On Windows use the equivalent `.venv\\Scripts\\python.exe`. The optional bootstrap script can create a local environment:

```bash
python3 scripts/connection/bootstrap_local_env.py
```

Do not commit `.env`, `.venv/`, cache files, remote case/data files, or generated output. Do not edit any `raw/` directory.
