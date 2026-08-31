---
name: fluent-case-build-and-run
description: "Build and prove a Fluent child case from an explicit parent under the active phase execution contract. Use for dependency-ordered mutation, output-path resolution, strict readback/save-reopen verification, smoke testing, and mode-aware handoff."
---

# Fluent Case Build and Run

Treat Fluent as a dependency-ordered GUI state machine, not a stable Python object tree.

This skill implements a case that has already earned scientific permission. It may not waive phase lifecycle gates.

## Establish identity, authority, and scope

- Treat connection/server ID as transport routing, never case identity.
- Require exact parent case/data paths and artifact identity.
- Receive canonical `run-paths.yaml` and server placement from `fluent-fleet-orchestration` / `implement-experiment`.
- Read phase lifecycle state before mutation; do not implement under an unresolved `HUMAN_REQUIRED` lock.
- Define the intended mutable leaves and invariants before mutation.
- Derive run-specific output/recovery paths.

When the active `/goal` has an exclusive fleet lease, the assigned Fluent session is disposable working state after required recovery is preserved. It is valid to stop an inherited solve, reload/restart Fluent, or replace the loaded case according to the execution plan without additional human approval.

Do not use that authority to overwrite verified durable parents or lose a scientifically valuable unpreserved endpoint when a paired recovery save can be made cheaply.

## Inspect before mutating

Inspect the loaded parent and record the settings that must be preserved. For multiphase/DPM work this normally includes model family, phase materials, phase-specific boundaries, turbulence/energy state, injections, wall fates, and other relevant topology.

Use the active live tree as authority.

Whenever a dependency-sensitive object changes:

```text
enable/create parent
→ reacquire objects
→ inspect active children/options
→ set one dependent child
→ read back
→ continue
```

Do not guess a missing path. Use `fluent-live-inspection`; escalate semantic/prerequisite/automation uncertainty to `fluent-manual-researcher`.

## Resolve all file outputs before solving

Fluent may retain relative filenames whose destination depends on the session working directory.

Before smoke/main solve:

1. inspect important report/monitor/autosave/export/transcript destinations;
2. compare them with canonical `run-paths.yaml`;
3. replace ambiguous/relative inherited paths with explicit run-specific paths where supported;
4. where a relative filename is required, deliberately set/verify Fluent working directory and record the resolved absolute path;
5. preserve scientific monitor/report definitions while changing only file destinations;
6. create required directories and prove writability;
7. read back important configured destinations;
8. reconcile the canonical `run-paths.yaml`.

Never assume loading a case changes Fluent's working directory.

## Build and prove the child

1. Preserve required recovery state before first destructive mutation.
2. Make requested changes in dependency order.
3. Reacquire affected objects after topology/model/type changes.
4. Strictly audit every intended delta and declared invariant.
5. Write paired prepared case/data to declared full paths.
6. Confirm the files exist.
7. Reload by full path.
8. Reacquire objects and repeat the strict audit.
9. Record explicit parent/child paths, Fluent version, delta, readback, and output path map.

A successful setter call is not proof. Save/reopen readback is proof.

## Smoke and instrumentation gate

Run the setup's short smoke test, normally around 50 iterations for iteration-based cases.

Before any planned discovery or long hypothesis solve, require:

- initialization success when initialization is part of the setup;
- iteration/physical-time advancement;
- required file-backed histories appearing at declared paths;
- required residual/equation capture working when the evidence contract needs it;
- no setup/readback drift after smoke;
- no unresolved path ambiguity.

If a required evidence stream cannot be captured durably, do not launch a qualification run and hope to recover it later.

## Mode-aware handoff

### Discovery

Discovery remains synchronous and attached.

```text
verified child + smoke
→ synchronous Python/PyFluent discovery run
→ scientific goal remains active
→ terminal execution evidence
→ immediate analysis
```

Do not detach discovery merely to avoid waiting. An RPC/tool timeout is not a terminal state; reconcile manifest/live iteration and keep waiting while the approved run advances.

### Hypothesis-test

A long hypothesis run may launch only after `verify-phase-transition` records `HYPOTHESIS_RUN_READY == PASS`.

For ordinary steady iteration-based full-geometry qualification, reject a planned horizon below 10,000 iterations unless the setup records an explicit human-approved exception or scientifically equivalent non-iteration basis.

On Codex, hand the run to `supervise-fluent-run`; do not background-launch the raw runner. On runtimes without self-resume, remain attached for the approved horizon.

The hypothesis execution path must not change the scientific experiment after readiness verification.

## Stop conditions

Stop before mutation or launch when any of these remains unresolved:

- lifecycle permission missing;
- `HUMAN_REQUIRED` lock active;
- parent identity uncertain;
- path/output identity ambiguous;
- parent audit conflicts with branch assumptions;
- required setting cannot be read back;
- save/reopen audit fails;
- required instrumentation does not write during smoke;
- initialization fails when required;
- planned qualification horizon violates the hypothesis contract;
- no deterministic completion proof exists for a detached hypothesis run;
- Codex hypothesis self-wake cannot target the exact originating thread.

## Reporting

Return execution proof, not scientific interpretation:

- lifecycle mode/prerequisite gates;
- parent and child identity;
- recovery state preserved when takeover occurred;
- run path map and working directory;
- strict pre-save and post-reopen audits;
- smoke/instrumentation result;
- requested horizon;
- exact Python runner and output paths;
- hypothesis handoff job/terminal manifest where applicable;
- final observed progress;
- final/recovery/report/log locations;
- blockers or implementation limitations.
