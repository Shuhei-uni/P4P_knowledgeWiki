---
name: pyansys-workflow
description: "Use when working with PyAnsys executable automation for Fluent/PyFluent: connection checks, inspection scripts, setup/run scripts, machine-readable validation, dependency-ordered Fluent settings, or PyAnsys knowledge updates."
---

# PyAnsys Workflow

## Core Rule

Use `PyAnsys/` as the executable automation layer for Fluent setup, inspection, execution, data extraction, and machine-readable verification. Treat Fluent as a dependency-ordered GUI state machine, not a stable static Python object tree.

When this work belongs to an active `scientific-phase-loop`, read the phase-root `phase-state.yaml` and obey its hard lifecycle gates. PyAnsys tooling must not become an escape hatch around `verify-phase-transition`: discovery compute requires the discovery design permission, and a long hypothesis solve may not launch before `HYPOTHESIS_RUN_READY == PASS`.

Keep setup construction and run supervision conceptually separate:

- setup/build code creates or modifies the approved Fluent case and proves its state;
- run code connects to the intended case and performs the approved initialization/run/save sequence;
- discovery runs stay agent-attached through the short run and immediate evidence review;
- hypothesis-test runs use `supervise-fluent-run`: Codex detaches and wakes the originating Codex thread; Cursor stays attached through the approved horizon.

For autonomous experiments inside `scientific-phase-loop`, Python/PyFluent execution is the default. TUI-driven iteration, Fluent journal submission, and GUI-owned execution require explicit human approval for that run.

Do not merge unrelated setup mutation, scientific decision-making, and long-run supervision into one opaque script. A case-specific Python runner is fine when it is the clearest faithful implementation of the approved experiment.

Connection routing is not case provenance: `server_id` only selects the Fluent endpoint. After connecting, inspect what is loaded. Use observed case/data identity when available; otherwise mark it unavailable and never infer a case or setup from the server ID or a previous session. Do not persist `server_id` in report-facing identity fields.

Use verified remote directory knowledge from `PyAnsys/server-profiles/` when available. An explicit path in the experiment setup takes precedence. Never invent a remote output root from the server alias.

When the phase execution plan grants an exclusive fleet lease, a busy inherited Fluent session is not automatically protected working state. Follow `fluent-fleet-orchestration`: preserve a paired recovery state when scientifically valuable, then stop/reload/reassign the active session as the approved goal requires. Never overwrite verified durable parent artifacts merely because the session can be controlled.

## Fluent Settings Rule

Follow this canonical order for non-trivial setting changes:

```text
enable parent -> refresh/reacquire -> inspect children/options -> set child -> read back -> classify failure
```

Mandatory habits:

- Reacquire objects after enabling models, creating objects, changing types, loading a case/data file, changing phase count, or switching boundary/model families.
- Inspect live child names, commands, and allowed values before setting deep paths.
- Treat readback mismatch as failure even when no exception was raised.
- Classify failures as `order/dependency issue`, `path/version issue`, `invalid value/format issue`, `PyFluent wrapper limitation`, `requires human-approved TUI/journal fallback`, or `requires manual GUI cleanup`.

A Settings/API limitation is not permission to switch to TUI. Return the blocker and obtain explicit human approval before using TUI or a Fluent journal.

For semantic/prerequisite uncertainty in a Fluent setting, escalate from live inspection to `fluent-manual-researcher` rather than inventing a path or model state.

## Inspection-First Workflow

Before writing a setup script for a new Fluent branch:

1. Run `scripts/connection/check_connection.py`.
2. Run `scripts/inspection/inspect_fluent_session.py`.
3. Add a targeted non-mutating probe if paths or object names are unclear.
4. Only then edit or create mutation-heavy setup code.

Prefer existing helpers and proven code paths before inventing new campaign-specific machinery.

## Code Placement

Keep file roles strict:

- `src/pyansys_fluent/`: reusable library code;
- `scripts/connection/`: bootstrap and preflight;
- `scripts/inspection/`: non-mutating discovery, monitoring, and probes;
- `scripts/setup/`: thin case-specific build/run orchestration;
- `scripts/orchestration/`: background hypothesis execution and event-driven Codex handoff when launched from Codex;
- `server-profiles/`: non-secret per-server filesystem layout;
- `knowledge/fluent-settings/`: durable Fluent/PyFluent execution and settings knowledge;
- `output/`: generated extracts only; do not treat as authoritative scientific knowledge.

Setup scripts should remain thin: parse inputs, connect, verify remote files, load case/mesh, inspect state, apply the approved changes, read back critical values, and write the required case artifact.

## Mode-specific Python execution

### Discovery

Discovery mode is intentionally interactive at the agent-workflow level even though the Fluent solve itself remains deterministic.

For the short discovery horizon, normally around 500-1,000 iterations:

```text
agent launches Python/PyFluent run
→ agent stays attached and mostly waits
→ run returns
→ agent immediately inspects screening evidence
→ agent revises hypothesis / chooses next discovery probe
```

Do not use the detached sleep/wake worker merely to avoid waiting. Do not end or pause the scientific goal between ordinary discovery runs. The point is fast experimental iteration while context is still live.

A tool/RPC timeout is not permission to leave discovery. Reconcile the operational manifest/live Fluent state and continue waiting while the approved calculation is still advancing.

Do not create one-iteration polling loops merely to keep the agent awake. Prefer one clear solve call for the approved short horizon and wait on that call or its terminal state.

### Hypothesis test

For a background Codex hypothesis-test run, use the canonical `supervise-fluent-run` / `scripts/orchestration/run_and_handoff.py` path. For a Cursor hypothesis-test run, keep the agent attached and wait on the approved Python/PyFluent solve; do not require Codex wakeup.

Before execution, the scientific design/setup layers must already have selected a genuine qualification horizon. For ordinary steady full-geometry work that means the project default minimum of 10,000 iterations unless the approved setup carries the explicit exception/equivalent basis required by the lifecycle.

The experiment runner should make the execution sequence explicit:

```text
connect -> establish case identity -> initialize if required
-> run approved horizon -> write final data -> verify output
```

On Codex, the background Python orchestration must then finish through this mandatory tail:

```text
persist COMPLETE or BLOCKED evidence
→ codex exec resume <ORIGINATING_THREAD_ID> <continuation prompt>
```

The continuation prompt must return to the exact scientific lifecycle: read `phase-state.yaml`, verify `HYPOTHESIS_EXECUTION`, produce the required analysis, verify `HYPOTHESIS_EVIDENCE`, and continue automatically.

The originating thread is captured automatically from `CODEX_THREAD_ID` when the job is launched from Codex; an explicit `codex.session_id` is only an override. Never use `--last` when multiple servers or jobs may finish independently.

A Codex hypothesis-test job is invalid if the wakeup hook is disabled, the originating thread cannot be resolved, either `COMPLETE` or `BLOCKED` is excluded from the wakeup triggers, or deterministic completion proof is absent.

On Cursor, persist the same completion evidence in the live session. Do not call `codex exec resume`. Missing `CODEX_THREAD_ID` is not a blocker.

A zero runner exit code is not sufficient completion proof. Declare required final files and/or a deterministic verifier command. Poor residuals or unexpected physics are not execution failures while Fluent can continue.

If Python/PyFluent cannot perform the approved run faithfully, stop and return the blocker. Do not silently fall back to TUI, a Fluent journal, or GUI execution.

## Cross-System Sync

After PyAnsys work:

- put current experiment evidence and findings in the matching `Project/` record;
- put reusable CFD method knowledge in `CFD_wiki/`;
- put durable implementation/discovery details in `PyAnsys/knowledge/`;
- update a server profile only with directly observed or user-supplied filesystem facts.

Do not create a second project log inside PyAnsys.
