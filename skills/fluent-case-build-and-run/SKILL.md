---
name: fluent-case-build-and-run
description: "Use when deriving a Fluent child case from an explicit parent and then planning or starting its run. Covers parent/child identity, recovery, readback verification, and choosing simple TUI, journal batch, or agent-owned Python execution."
---

# Fluent Case Build and Run

Treat this as three steps: **build the child case -> choose the run mode -> execute the run**.

## Build the child case

1. Require an explicit parent-case path. `server_id` is routing only, never case identity.
2. Load the exact parent and reacquire all Fluent settings objects.
3. Define the intended delta and the important inherited settings that must remain unchanged.
4. If the loaded field state matters, save a separate recovery `.cas.h5` + `.dat.h5` pair before mutation.
5. Apply changes in dependency order:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

6. Audit the intended changes and invariants.
7. Write the child `.cas.h5`, reload it, and verify the audit again.

Do not overwrite the parent or an existing child unless explicitly requested.

## Choose the run mode

Use the simplest execution method that matches the scientific workflow.

### Simple TUI

Use for one prepared case with no mid-run decisions. Configure required autosave/checkpoints, initialize as requested, then send one Fluent/TUI solve command.

### Fluent journal

Use for multiple independent cases or a fixed sequence where no intermediate result changes the next action. A robust journal should use explicit full paths, unique output names, deterministic load/initialize/run/save operations, transcripts, and recovery/autosave where useful.

### Agent-owned Python

Use when the experiment is staged or adaptive: ramping, checkpoint gates, mid-run setting changes, conditional continuation, or similar logic.

At each decision point:

```text
run block -> inspect -> checkpoint/record -> decide -> change state if required -> continue
```

After a connection/transport failure, reconcile the actual Fluent stage and iteration before issuing another solve command. Never silently repeat an uncertain block.

For this mode, hand off:

- the exact launch command;
- what the supervising agent should monitor;
- checkpoint/log locations;
- stage and stop criteria;
- safe resume/recovery steps.

## Reporting

At handoff, state separately:

- parent and verified child paths;
- intended delta and readback status;
- chosen run mode and why;
- whether initialization completed;
- whether the run was submitted, actively supervised, or independently observed as complete;
- recovery/autosave locations;
- unresolved assumptions that affect interpretation.

## Examples

**Pressure sweep:** build sibling cases first, then submit a single journal that loads, initializes, runs, and saves each sibling. No agent needs to wait between cases.

**Staged solver ramp:** build one parent case, then use a Python supervisor that runs to each checkpoint, inspects residual/flux gates, applies the prescribed next state, and resumes from explicit checkpoints if interrupted.
