---
name: pyansys-workflow
description: "Use when working with PyAnsys executable automation for Fluent/PyFluent: connection checks, inspection scripts, setup/run scripts, machine-readable validation, dependency-ordered Fluent settings, or PyAnsys knowledge updates."
---

# PyAnsys Workflow

## Core Rule

Use `PyAnsys/` as the executable automation layer for Fluent setup, inspection, execution, data extraction, and machine-readable verification. Treat Fluent as a dependency-ordered GUI state machine, not a stable static Python object tree.

Keep setup construction and run supervision conceptually separate:

- setup/build code creates or modifies the approved Fluent case and proves its state;
- run code connects to the intended case and performs the approved initialization/run/save sequence;
- discovery runs stay agent-attached through the short run and immediate evidence review;
- hypothesis-test runs use `supervise-fluent-run`: Codex detaches and wakes the originating Codex thread; Cursor stays attached through the approved horizon.

For autonomous experiments inside `scientific-phase-loop`, Python/PyFluent execution is the default. TUI-driven iteration, Fluent journal submission, and GUI-owned execution require explicit human approval for that run.

Do not merge unrelated setup mutation, scientific decision-making, and long-run supervision into one opaque script. A case-specific Python runner is fine when it is the clearest faithful implementation of the approved experiment.

Connection routing is not case provenance: `server_id` only selects the Fluent endpoint. After connecting, inspect what is loaded. Use observed case/data identity when available; otherwise mark it unavailable and never infer a case or setup from the server ID or a previous session. Do not persist `server_id` in report-facing identity fields.

Use verified remote directory knowledge from `PyAnsys/server-profiles/` when available. An explicit path in the experiment setup takes precedence. Never invent a remote output root from the server alias.

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

Do not use the detached sleep/wake worker merely to avoid waiting. Do not end the scientific thread between ordinary discovery runs. The point is fast experimental iteration while context is still live.

Do not create one-iteration polling loops merely to keep the agent awake. Prefer one clear solve call for the approved short horizon and wait on that call or its terminal.

### Hypothesis test

For a background Codex hypothesis-test run, use the canonical `supervise-fluent-run` / `scripts/orchestration/run_and_handoff.py` path. For a Cursor hypothesis-test run, keep the agent attached and wait on the approved Python/PyFluent solve; do not require Codex wakeup.

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

The originating thread is captured automatically from `CODEX_THREAD_ID` when the job is launched from Codex; an explicit `codex.session_id` is only an override. Never use `--last` when multiple servers or jobs may finish independently.

A Codex hypothesis-test job is invalid if the wakeup hook is disabled, the originating thread cannot be resolved, or either `COMPLETE` or `BLOCKED` is excluded from the wakeup triggers.

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
