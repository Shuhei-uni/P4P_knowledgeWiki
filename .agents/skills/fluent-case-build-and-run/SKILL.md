---
name: fluent-case-build-and-run
description: "Build a new Ansys Fluent child case from an explicitly named parent and prepare it for a controlled Python-supervised calculation. Use when cloning or modifying a case, especially DPM or multiphase variants, when case identity, recovery copies, readback verification, initialization, and run handoff matter."
---

# Fluent Case Build and Run

Use this workflow for a case-derived Fluent setup and its handoff to execution. Treat Fluent as a dependency-ordered GUI state machine, not a stable Python object tree.

## Establish identity and scope

- Treat a connection/server ID as routing only, never as a case identity.
- Require an explicit remote parent-case path. Confirm its existence, load that exact case, and discard all old settings handles.
- Define the child change narrowly: list what changes and what must remain unchanged. Identify the exact mutable state leaves and their expected post-change values before making a mutation.
- Derive unique child-output and recovery paths. Refuse to overwrite a parent, recovery artifact, or existing child unless the user explicitly requests reuse.
- Use an explicit experiment path or verified `PyAnsys/server-profiles/` filesystem knowledge. Never infer a run directory from `server_id`.

## Inspect before mutating

Before a non-trivial mutation, inspect the loaded parent and record the settings that must be preserved. For DPM and multiphase work, this normally includes inlet topology, phase-specific boundary settings, model family, phase materials, turbulence/energy state, DPM controls, wall zones, particle fates, and named injection properties.

Use the active live tree as authority. If a required path, value, or object identity differs from the proposed recipe, stop and adapt the implementation; do not force a topology-specific script onto a different case.

Use this setting pattern whenever a dependency-sensitive object changes:

```text
enable or create parent -> reacquire -> inspect active children/options
-> set one dependency-sensitive child -> read back -> continue
```

Reacquire settings objects after loading a case, enabling a model, creating an object, changing particle type, or changing injection type.

## Build the child case

1. Before the first mutation, preserve the recovery state required by the experiment. If a recoverable field state matters, write and confirm a paired `.cas.h5`/`.dat.h5`; do not replace it with a case-only save.
2. Make the requested changes in dependency order. For a replacement population, create and fully read back each new object before removing an inherited one.
3. Run a strict pre-save audit. Require every intended change and every declared invariant to match the experiment contract.
4. When a broad state object contains both immutable state and an intentional delta, compare it with a scoped diff: remove or replace only the declared mutable leaves on both sides, then require all remaining state to match. Audit each mutable leaf separately.
5. Write the child `.cas.h5`, confirm that the remote file exists, reload it by full path, and repeat the strict audit.
6. Record the explicit parent and child paths, intended delta, readback, Fluent version, and uncertainty labels. Do not use the server ID as report-facing case identity.

Do not silently combine setup redesign with execution. Once the case is proven, hand the approved run to `implement-experiment` / `supervise-fluent-run`.

## Initialize and run through Python by default

For autonomous experiments inside `scientific-phase-loop`, use a Python/PyFluent runner supervised by an agent.

1. Load the verified child case when it is not already the known active case.
2. Configure the approved output/checkpoint paths on the Fluent machine.
3. Start the initialization required by the setup.
4. Wait for initialization to return successfully before starting the main calculation. If initialization fails, blocks irrecoverably, or leaves state uncertain, do not start the run.
5. Start the requested calculation through the Python/PyFluent runner.
6. Hand the long-lived terminal observation to `supervise-fluent-run`.

A busy or blocked Fluent call during an active synchronous calculation is not by itself evidence of failure. The supervising agent should primarily watch the runner terminal and use read-only inspection only when useful.

TUI-driven iteration, Fluent journal/batch submission, and GUI-owned runs require explicit human approval for that specific run. A PyFluent path failure is not permission to switch execution mechanisms automatically.

## Stop conditions and reporting

Stop before mutation or run launch when any of these occurs:

- parent/output identity cannot be established;
- the parent audit does not match the intended branch assumptions;
- a dependency-sensitive setting cannot be read back;
- an output/recovery file would be overwritten without permission;
- initialization does not complete successfully;
- the Python/PyFluent run path cannot execute the approved experiment faithfully.

At handoff, state separately:

- whether the child case was built and reload-verified;
- whether initialization completed;
- the Python runner and remote output paths;
- whether execution was completed or blocked;
- the final independently observed progress;
- the location of recovery, child, final data, and verification artifacts;
- any implementation or execution limitation that must be reconsidered upstream.

Scientific interpretation belongs downstream.