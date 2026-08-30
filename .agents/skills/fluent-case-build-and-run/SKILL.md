---
name: fluent-case-build-and-run
description: "Build a new Ansys Fluent child case from an explicitly named parent and prepare it for a controlled Python-supervised calculation. Use when cloning or modifying a case, especially DPM or multiphase variants, when case identity, explicit output paths, recovery copies, readback verification, initialization, and run handoff matter."
---

# Fluent Case Build and Run

Use this workflow for a case-derived Fluent setup and its handoff to execution. Treat Fluent as a dependency-ordered GUI state machine, not a stable Python object tree.

## Establish identity and scope

- Treat a connection/server ID as routing only, never as a case identity.
- Require an explicit remote parent-case path. Confirm its existence, load that exact case, and discard all old settings handles.
- Define the child change narrowly: list what changes and what must remain unchanged. Identify the exact mutable state leaves and their expected post-change values before making a mutation.
- Derive unique child-output and recovery paths. Refuse to overwrite a parent, recovery artifact, or existing child unless the user explicitly requests reuse.
- Use an explicit experiment path or verified `PyAnsys/server-profiles/` filesystem knowledge. Never infer a run directory from `server_id`.
- Receive the authoritative run path map from `fluent-fleet-orchestration` / `implement-experiment`; do not invent a second set of output locations inside the case-building script.

## Inspect before mutating

Before a non-trivial mutation, inspect the loaded parent and record the settings that must be preserved. For DPM and multiphase work, this normally includes inlet topology, phase-specific boundary settings, model family, phase materials, turbulence/energy state, DPM controls, wall zones, particle fates, and named injection properties.

Use the active live tree as authority. If a required path, value, or object identity differs from the proposed recipe, stop and adapt the implementation; do not force a topology-specific script onto a different case.

Use this setting pattern whenever a dependency-sensitive object changes:

```text
enable or create parent -> reacquire -> inspect active children/options
-> set one dependency-sensitive child -> read back -> continue
```

Reacquire settings objects after loading a case, enabling a model, creating an object, changing particle type, or changing injection type.

## Resolve Fluent file outputs before solving

Fluent can retain relative filenames inside a case, especially for report/monitor files such as `.out`, autosaves, exports, transcripts, or other file-backed definitions. These may resolve against the directory where the active Fluent session was launched rather than the directory containing the loaded case.

Before the smoke test or long run:

1. inspect file-backed outputs that matter to the experiment;
2. compare each destination with the run path map;
3. replace relative, inherited, blank, or ambiguous destinations with explicit run-specific paths when the API supports this;
4. if Fluent requires a relative filename, deliberately establish and verify the intended working directory and record the resulting absolute path;
5. preserve the scientific report/monitor definition while changing only its file destination;
6. read back important destinations when possible;
7. ensure required output directories exist and are writable;
8. update the authoritative Project `run-paths.yaml` with the resolved destinations.

Never rely on an unexamined Fluent current working directory. Never assume loading `C:\\somewhere\\parent.cas.h5` means a relative `monitor.out` will be written to `C:\\somewhere`.

A bare filename is acceptable only when its containing directory has been deliberately fixed and the full resolved destination is recorded.

## Build the child case

1. Before the first mutation, preserve the recovery state required by the experiment. If a recoverable field state matters, write and confirm a paired `.cas.h5`/`.dat.h5`; do not replace it with a case-only save.
2. Make the requested changes in dependency order. For a replacement population, create and fully read back each new object before removing an inherited one.
3. Run a strict pre-save audit. Require every intended change and every declared invariant to match the experiment contract.
4. When a broad state object contains both immutable state and an intentional delta, compare it with a scoped diff: remove or replace only the declared mutable leaves on both sides, then require all remaining state to match. Audit each mutable leaf separately.
5. Write the child `.cas.h5` to its declared full path, confirm that the remote file exists, reload it by full path, and repeat the strict audit.
6. Record the explicit parent and child paths, intended delta, readback, Fluent version, output path map, and uncertainty labels. Do not use the server ID as report-facing case identity.

Do not silently combine setup redesign with execution. Once the case is proven, hand the approved run to `implement-experiment` / `supervise-fluent-run` as appropriate for its mode.

## Initialize and run through Python by mode

For autonomous experiments inside `scientific-phase-loop`, use the approved Python/PyFluent runner and preserve the experiment mode chosen upstream.

1. Load the verified child case when it is not already the known active case.
2. Reconfirm the declared working directory and all required output/checkpoint/report paths on the Fluent machine.
3. Start the initialization required by the setup.
4. Wait for initialization to return successfully before committing the planned run. If initialization fails, blocks irrecoverably, or leaves state uncertain, do not launch it.
5. Run the agreed smoke test, including the exact setup readback/save-reopen proof and the short execution check required by the experiment.
6. Define the exact Python/PyFluent run command and the required completion evidence.

For **discovery mode**, keep the scientific agent attached through the short run and throughout the active discovery campaign. Do not hand discovery work to the detached sleep/wake path merely to avoid waiting. Return each result immediately so the same active thread can inspect it, revise the working hypothesis, and choose the next discovery experiment.

For **hypothesis-test mode**, create the run through `supervise-fluent-run`. On Codex, that is the self-waking run-and-handoff job; do not background-launch the raw hypothesis runner directly. On Cursor, keep the agent attached through the approved horizon.

On Codex, the hypothesis launcher should resolve the originating thread automatically from `CODEX_THREAD_ID`. An explicit `codex.session_id` is only an override. The background Python path must persist `COMPLETE` or `BLOCKED` evidence and then resume that exact thread as its mandatory final action.

Do not start a Codex background hypothesis run if the originating thread cannot be resolved, the wakeup hook is disabled, or either terminal state would fail to wake the scientific loop. On Cursor, missing `CODEX_THREAD_ID` is expected; do not block the run for that reason and do not call `codex exec resume`.

A busy or blocked Fluent call during an active synchronous calculation is not by itself evidence of failure. Let the approved horizon continue while Fluent can solve and classify the result from the returned execution evidence.

TUI-driven iteration, Fluent journal/batch submission, and GUI-owned runs require explicit human approval for that specific run. A PyFluent path failure is not permission to switch execution mechanisms automatically.

## Stop conditions and reporting

Stop before mutation or run launch when any of these occurs:

- parent/output identity cannot be established;
- an important artifact or file-backed output destination remains implicit or ambiguous;
- the parent audit does not match the intended branch assumptions;
- a dependency-sensitive setting cannot be read back;
- an output/recovery file would be overwritten without permission;
- initialization does not complete successfully;
- the Python/PyFluent run path cannot execute the approved experiment faithfully;
- no deterministic terminal completion proof can be defined for a background hypothesis run;
- the originating Codex thread cannot be resolved for a Codex background hypothesis run.

At handoff, state separately:

- whether the child case was built and reload-verified;
- whether the run path map was established and where it is stored;
- the deliberately established Fluent working directory;
- whether initialization and smoke testing completed;
- the Python runner and remote output paths;
- the execution mode;
- for hypothesis runs, the detached job spec and terminal manifest when used, originating Codex thread and Codex handoff status on Codex, or attached-session completion on Cursor;
- whether execution was completed or blocked;
- the final independently observed progress;
- the declared and actual locations of recovery, child, final data, `.out`/report files, transcript/log, and verification artifacts;
- any path anomaly, implementation limitation, or execution limitation that must be reconsidered upstream.

Scientific interpretation belongs downstream.
