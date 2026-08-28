# PyAnsys / PyFluent remote Fluent kit

PyAnsys owns executable Fluent implementation, live inspection, Python-supervised execution, and machine-readable evidence checks. Project-specific scientific truth remains in `../Project/`; reusable CFD and literature knowledge remains in `../CFD_wiki/`.

The operating rule is simple: Fluent is a dependency-ordered state machine, and autonomous-loop runs default to an approved Python/PyFluent runner launched through a detached execution worker. The AI agent does not need to remain alive for the full solve; the worker verifies the terminal state and then resumes the exact Codex session. TUI-driven iteration, Fluent journal submission, and GUI-owned execution require explicit human approval for that run.

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
    -> detached run-and-handoff worker
    -> Fluent completes or blocks
    -> verify final outputs and write terminal manifest
    -> resume exact Codex session
    -> numerical analysis / Project interpretation
```

Use `supervise-fluent-run` to prepare and launch the long-lived execution. The worker should let the approved fixed horizon run while Fluent can continue, record `COMPLETE` or `BLOCKED`, and wake the scientific agent only when there is a terminal execution event.

## Connection and run tools

- `scripts/connection/check_connection.py` — endpoint health check.
- `scripts/connection/local_preflight.py` — local runtime and endpoint preflight.
- `scripts/inspection/inspect_fluent_session.py` — non-mutating live tree inspection.
- `scripts/inspection/monitor_native_run.py` — reconnecting read-only monitor that can supplement execution evidence without becoming a mutating controller.
- `scripts/setup/` — case-specific Python setup/run orchestration. Prefer a proven runner when one matches the approved experiment; otherwise keep new runners thin and explicit.
- `scripts/orchestration/run_and_handoff.py` — generic detached worker launcher. It runs the approved runner, verifies declared completion evidence, writes a terminal manifest, and optionally resumes an explicit Codex session.
- `queues/run-and-handoff.example.yaml` — example detached job contract.
- `scripts/setup/generate_native_run_journal.py` and other journal/native-queue tools — retained for historical or human-approved exception use; not autonomous-loop defaults.
- `scripts/inspection/post_simulation_analysis.py` — selected read-only residual, flux, and results-evidence checks.

The remaining setup and inspection scripts are kept when they support a current Project experiment, a focused skill, a reusable source module, or unique evidence recovery. Campaign-specific scripts are not a general API.

## Detached handoff contract

Normal launch is:

```bash
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

The launcher returns after starting a detached worker. The worker then owns the long synchronous runner call.

A job must declare at least one completion proof: locally visible required files and/or a deterministic verifier command. A zero runner exit code by itself cannot produce `COMPLETE`.

For Codex continuation, store an explicit session/thread ID in the job specification. The hook uses:

```text
codex exec resume <SESSION_ID> <PROMPT>
```

Do not use `--last` for autonomous multi-server work because jobs can finish in a different order from launch order.

The generated job manifest is execution evidence only. Canonical scientific paths and server placement remain in the experiment's `Project/.../run-paths.yaml`.

## Source layout

- `src/pyansys_fluent/` — reusable connection, setup, extraction, monitoring, evidence, and run-handoff logic.
- `scripts/connection/` — connection and local-environment checks.
- `scripts/inspection/` — non-mutating discovery, snapshots, monitors, and post-processing.
- `scripts/setup/` — thin experiment-specific setup and Python/PyFluent runner orchestration.
- `scripts/orchestration/` — generic detached execution and event-driven handoff.
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
