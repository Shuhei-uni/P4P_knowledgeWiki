---
name: pyansys-workflow
description: "Use when working with PyAnsys executable automation for Fluent/PyFluent: connection checks, inspection scripts, setup/run scripts, machine-readable validation, dependency-ordered Fluent settings, or PyAnsys knowledge updates."
---

# PyAnsys Workflow

## Core Rule

Use `PyAnsys/` as the executable automation layer for Fluent setup, inspection, detached execution, data extraction, and machine-readable verification. Treat Fluent as a dependency-ordered GUI state machine, not a stable static Python object tree.

Keep setup construction and run supervision conceptually separate:

- setup/build code creates or modifies the approved Fluent case and proves its state;
- run code connects to the intended case and performs the approved initialization/run/save sequence;
- `supervise-fluent-run` launches that long runner through the detached run-and-handoff worker, which verifies terminal evidence and resumes the exact Codex session afterward.

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
- `scripts/orchestration/`: generic detached run execution and event-driven handoff;
- `server-profiles/`: non-secret per-server filesystem layout;
- `knowledge/fluent-settings/`: durable Fluent/PyFluent execution and settings knowledge;
- `output/`: generated extracts only; do not treat as authoritative scientific knowledge.

Setup scripts should remain thin: parse inputs, connect, verify remote files, load case/mesh, inspect state, apply the approved changes, read back critical values, and write the required case artifact.

## Python-supervised run contract

For a long run inside the scientific loop, use a Python runner that makes the intended PyFluent calls and launch it through `supervise-fluent-run` / `scripts/orchestration/run_and_handoff.py`.

The runner should make the execution sequence explicit:

```text
connect -> establish case identity -> initialize if required
-> run the approved horizon -> write final data -> verify output
```

Prefer a single clear solve call for the planned horizon or another coarse bounded structure required by the experiment. Do not create one-iteration polling loops merely to keep an agent awake.

The current AI turn does not need to remain alive while Fluent advances. The detached worker captures the runner log, writes `RUNNING`/`VERIFYING`/terminal state to a job manifest, checks required files and/or a deterministic verifier, and records `COMPLETE` or `BLOCKED` before invoking the Codex continuation hook.

For autonomous continuation, store an explicit Codex session/thread ID in the job contract and use `codex exec resume <SESSION_ID> ...`. Never use `--last` when multiple servers or jobs may finish independently.

A zero runner exit code is not sufficient completion proof. Declare required final files and/or a deterministic verifier command. Poor residuals or unexpected physics are not execution failures while Fluent can continue.

If Python/PyFluent cannot perform the approved run faithfully, stop and return the blocker. Do not silently fall back to TUI, a Fluent journal, or GUI execution.

## Cross-System Sync

After PyAnsys work:

- put current experiment evidence and findings in the matching `Project/` record;
- put reusable CFD method knowledge in `CFD_wiki/`;
- put durable implementation/discovery details in `PyAnsys/knowledge/`;
- update a server profile only with directly observed or user-supplied filesystem facts.

Do not create a second project log inside PyAnsys.
