---
name: fluent-case-build-and-run
description: "Deprecated compatibility workflow for retained Fluent case-build/run guidance; use fluent-implementation for new selected experiments."
---

> **Transitional compatibility skill.** Do not route new implementation work here. Use `fluent-implementation` and its focused specialist skills; retain this file only for explicit compatibility reference until the #19 cleanup stage.

# Fluent Case Build and Run

Use this workflow for a case-derived Fluent setup and its subsequent run. Treat Fluent as a dependency-ordered GUI state machine, not a stable Python object tree.

## Establish identity and scope

- Treat a connection/server ID as routing only, never as a case identity.
- Require an explicit remote parent-case path. Confirm its existence, load that exact case, and discard all old settings handles.
- Define the child change narrowly: list what changes and the carrier, materials, boundaries, mesh, global model controls, and injection properties that must stay unchanged. Identify the exact mutable state leaves and their expected post-change values before making a mutation.
- Derive unique child-output and recovery-pair paths. Refuse to overwrite a parent, recovery artifact, or existing child unless the user explicitly requests reuse.
- Obtain an observed or explicitly supplied current iteration label for the recovery pair; never infer it from the server ID. Use it in both remote filenames, for example `name-5000.cas.h5` and `name-5000.dat.h5`.

## Inspect before mutating

Before a non-trivial mutation, inspect the loaded parent and record the settings that must be preserved. For DPM and multiphase work, this normally includes:

- inlet topology and phase-specific boundary settings;
- model family, phase materials, turbulence/energy state, and global DPM controls;
- materials, wall zones, and particle fates;
- named injections, particle type/material, injection type/location, mass flow, size, velocity, parcel/tracking, and physical-model state.

Use the active live tree as authority. If a required path, value, or object identity differs from the proposed recipe, stop and adapt the recipe; do not force a topology-specific script onto a different case.

Use this setting pattern whenever a dependency-sensitive object changes:

```text
enable or create parent -> reacquire -> inspect active children/options
-> set one dependency-sensitive child -> read back -> continue
```

Reacquire settings objects after loading a case, enabling a model, creating an object, changing particle type, or changing injection type.

## Build the child case

1. Before the first mutation, write and confirm a separate **paired** recovery checkpoint: `.cas.h5` and `.dat.h5`. Preserve the loaded field state as well as the setup; do not replace this with a case-only save when the task requires a recoverable data state. Require both remote files to exist before continuing.
2. Make the requested changes in dependency order. For a replacement population, create and fully read back each new object before removing an inherited one.
3. Run a strict pre-save audit. Require every intended change and every declared invariant to match the parent audit.

When a broad state object contains both immutable state and an intentional delta (for example, DPM injection flow leaves inside the DPM model state), compare it with a **scoped diff**: remove or replace only the declared mutable leaves on both sides, then require all remaining state to match. Audit each mutable leaf separately. Do not use a whole-object equality assertion that will reject the requested change merely because it appears inside the object.
4. Write the child `.cas.h5`, confirm that the remote file exists, reload it by full path, and repeat the strict audit.
5. Record a machine-readable summary with the explicit parent and child paths, intended delta, readback, Fluent version, and uncertainty labels. Do not include a server ID in report-facing identity fields.

Do not initialize, iterate, or write data from the child-case builder unless the user explicitly asks for the run as well.

## Initialize and start a run

Keep setup construction separate from run ownership. Fluent—not a laptop-side Python loop—must own a long calculation and its autosaves.

1. Load the verified child case when it is not already the known active case.
2. Configure Fluent-native autosave/checkpointing when the user asks for a resilient or long run. Use remote paths and Fluent-native retention; do not make a Python loop the checkpoint owner.
3. Start hybrid or the explicitly requested initialization.
4. **Wait for initialization to return successfully before starting the run.** Before the initialization call, and while it is expected to be idle, the server must answer normally. A server that becomes busy, blocks, disconnects, or fails to return before initialization completes is a fatal pre-run condition: stop, preserve the recovery case, and report it. Do not call `iterate`.
5. Only after initialization has returned, start the requested Fluent-native calculation or Fluent-native journal.
6. Once the calculation command has started, an occupied/busy Fluent server is expected. Do not send another mutating command, reload a case, or assume that a blocked parallel gRPC call means the run failed.

For a requested direct run with no additional checks, perform only the requested initialization and run launch. Do not silently add model, boundary, convergence, or DPM safety gates after the user has explicitly declined them.

## Observe without interfering

Use a separate read-only reconnecting monitor after a native run starts. It may inspect health, monitor histories, and explicitly supplied checkpoint-pair existence, but it must never initialize, iterate, save, reload, interrupt, or exit Fluent.

If a read-only request blocks while Fluent is actively solving, report that no live snapshot is available rather than inferring an iteration count. Prefer Fluent console output, a configured remote transcript, or a later monitor snapshot once the solver responds.

## Stop conditions and reporting

Stop before mutation or run launch when any of these occurs:

- parent/output identity cannot be established;
- the parent audit does not match the intended branch assumptions;
- a dependency-sensitive setting cannot be read back;
- an output/recovery file would be overwritten without permission, or either member of the required recovery case/data pair is missing;
- initialization does not return and leave Fluent responsive before the run begins.

At handoff, state separately:

- whether the child case was built and reload-verified;
- whether initialization completed;
- whether the run was merely launched or its completed iteration count was independently observed;
- the location of recovery, child, data/autosave, and local verification artifacts;
- assumptions or unresolved physics limitations that affect result interpretation.
