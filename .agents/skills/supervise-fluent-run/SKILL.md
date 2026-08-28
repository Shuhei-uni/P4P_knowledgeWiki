---
name: supervise-fluent-run
description: "Supervise a long Fluent calculation launched from a Python runner. Use inside implement-experiment after the case has been verified and smoke-tested, when an agent should stay with the terminal, observe execution efficiently, classify real run failures, verify declared output paths and final data, preserve selected important recovery states, and hand back clean execution facts without redesigning or interpreting the experiment."
---

# Supervise Fluent Run

Watch the approved simulation until it either produces verified final data or reaches a real execution blocker.

The default autonomous-loop execution path is a Python runner supervised by an agent. TUI-driven runs and Fluent journal submission require explicit human approval for that run.

The governing posture is:

```text
observe continuously
intervene rarely
never confuse bad scientific behaviour with an execution failure
```

## Receive an execution contract

Before launch, know:

- experiment/setup identity and run ID;
- the canonical runtime `server.ref` plus separate server ID and IP;
- exact remote case path;
- exact remote run/output directory;
- the canonical `run-paths.yaml` beside `setup.md` and `results.md` in the Project experiment packet;
- the deliberately established Fluent working directory;
- Python runner path and arguments;
- initialization intent;
- requested iteration/time horizon;
- expected final case/data paths;
- checkpoint/autosave paths when configured;
- every required file-backed report/monitor output path, including `.out` files;
- which, if any, selected checkpoint states should be promoted for durable recovery;
- expected OneDrive durability target for the final state when configured;
- terminal/transcript/log paths when available.

Use the server profile under `PyAnsys/server-profiles/` when one exists. A server profile describes remote directory layout only; it does not establish which scientific case is loaded or where a relative Fluent output will actually be written.

Do not identify the machine by a short alias such as `server-2` alone when collaborators may have duplicate numbering. Use the fleet-resolved reference such as `server-2@192.168.1.42`.

Do not guess a remote output root. Do not accept a bare output filename unless its working directory and resulting absolute destination are recorded. If neither the execution plan nor the experiment-local `run-paths.yaml` establishes important destinations, return the missing execution information before launching.

A remote copy of the path configuration may exist temporarily if the runner needs it, but it is derived. Do not let a server-local manifest become a competing source of truth.

## Default to Python-supervised execution

Launch the approved run through Python/PyFluent and keep the agent attached to the runner terminal for the intended horizon.

Prefer one clear run command for the planned horizon rather than fine-grained agent-controlled iteration loops. Python may own the synchronous run call and final save; the supervising agent owns observation, failure classification, path/output reconciliation, recovery-artifact verification, and handoff.

Do not switch to TUI iteration, a Fluent journal, GUI submission, or another execution mechanism because it seems more convenient. Those are human-approved exceptions. If the Python/PyFluent path cannot execute the approved setup, report the blocker and request approval before using TUI or a journal.

## Stay token-efficient

Most of the supervisor's lifetime should require no reasoning.

Do not narrate normal iteration-by-iteration progress. Wake up on meaningful events such as:

- initialization returns or fails;
- the calculation begins;
- a declared report/monitor output or selected recovery checkpoint appears;
- an expected output fails to appear where the path map says it should;
- the runner emits an exception or Fluent fatal error;
- the runner or Fluent process terminates unexpectedly;
- connection state becomes uncertain;
- the calculation command returns;
- the requested horizon is reached.

When the terminal is simply advancing normally, wait and continue observing.

Use read-only monitoring helpers when useful, but do not make continuous secondary polling a requirement for the solve to proceed.

## Keep output locations reconciled

The Project experiment `run-paths.yaml` is part of the execution contract.

During supervision, treat these as path anomalies worth reconciling:

- a required `.out`, transcript, checkpoint, case/data save, or log is missing from its declared destination when it should exist;
- Fluent creates an important file in the session launch directory or another unexpected location;
- an existing relative path resolves somewhere other than the intended run root;
- a file from another run would be overwritten;
- the runner and Fluent disagree about the expected final path.

Do not redirect scientific outputs ad hoc during an active run unless doing so is a safe execution-only correction. Prefer to preserve the current state, record the actual observed location, and return a blocker when changing paths mid-run could create uncertainty.

An unexpected file found elsewhere must be documented with its actual path in the same canonical `run-paths.yaml`. Never silently pretend it was written to the planned location.

## Distinguish evidence from execution failure

The following are normally scientific evidence, not reasons for the supervisor to stop the run:

- poor, noisy, oscillatory, or slowly decaying residuals;
- poor balances or unexpected physical monitors;
- behaviour that appears scientifically unpromising;
- an unexpected flow field or trend;
- a temporarily unavailable read-only snapshot while the main calculation is busy.

Unless the experiment contract explicitly says otherwise, let the approved horizon finish when Fluent can continue solving.

A real execution blocker includes events such as:

- initialization cannot complete;
- Fluent reports a floating-point/fatal solver error and cannot continue;
- the Fluent process exits or crashes;
- the Python runner raises an execution error before completion;
- the calculation stops before the requested horizon and cannot be reconciled;
- required final data cannot be written or verified;
- important output locations become ambiguous enough that scientific evidence may be lost or overwritten;
- case/data state becomes uncertain enough that repeating work could duplicate or overwrite unknown progress.

## Reconcile uncertainty; never blindly repeat work

Treat observer/gRPC loss separately from Fluent numerical failure.

If connection or runner state becomes uncertain:

1. determine whether the same Fluent process still exists;
2. establish the newest independently observed iteration/progress state;
3. identify the latest verified paired case/data or autosave artifact;
4. reconcile actual files against the canonical Project experiment path map;
5. update that same `run-paths.yaml` with actual locations or uncertainty;
6. do not issue another run command while completion of the previous command is uncertain;
7. resume observation only after the actual state is reconciled.

A local status file, short server alias, or iteration count is not sufficient evidence of simulation progress or case identity.

## Preserve selected important recovery states

Do not turn high-frequency autosave into high-frequency network synchronization.

Routine autosaves may remain local for immediate same-server recovery. When the execution plan identifies an expensive or strategically important checkpoint worth protecting, preserve a complete matching case+data pair at the declared recovery paths and promote that selected state through the OneDrive durability path defined by `fluent-fleet-orchestration` when practical.

A protected recovery artifact should have one artifact ID and enough provenance to identify its source run, runtime `server.ref`, and iteration/progress. Prefer manifest/hash verification after transfer for important checkpoints. Record its verified local and OneDrive locations in `run-paths.yaml`.

This is specifically intended to reduce dependence on the current server: if the machine later becomes unavailable, a verified shared recovery pair may allow re-placement to another compatible server.

## On a blocker, preserve and hand back

Do not redesign the experiment from inside this skill.

When a real execution blocker occurs:

- stop issuing new mutating commands;
- preserve the last verified paired checkpoint/data state available locally;
- when practical and safe, promote a valuable recovery pair to OneDrive before abandoning the server state;
- capture the relevant terminal error, Fluent message, and runner exception;
- record the last independently observed iteration/progress;
- update the experiment-local `run-paths.yaml` with actual-vs-declared path differences and durability state;
- classify whether the failure is initialization, solver/numerical execution, Python/PyFluent execution, transport/state uncertainty, path/output failure, or file/output failure;
- hand the execution facts back to `implement-experiment` and `scientific-phase-loop` for the rethink.

Do not automatically lower relaxation factors, change timestep, alter initialization, change models, or rerun from a checkpoint. Those are scientific or implementation decisions owned upstream.

## Completion requires verified data and locatable outputs

Do not claim success because the Python command returned or enough wall time elapsed.

For an iteration-based run, verify at minimum:

- the requested target;
- the final independently observed iteration count;
- the expected final `.dat.h5` exists at the declared path and belongs to the intended run;
- the matching final case/restart identity is known at its declared path;
- required logs, histories, report `.out` files, and checkpoints are locatable at their declared paths or have an explicitly reconciled actual location;
- the canonical Project experiment `run-paths.yaml` is updated and available;
- any execution or path anomaly is recorded.

For scientifically important finals, also preserve a complete paired case+data final artifact. When the execution plan calls for durable preservation, promote that pair to OneDrive and verify the shared copy. If promotion cannot be completed, report `LOCAL_ONLY` rather than masking the durability gap.

If the target was not reached, return `BLOCKED`, not `COMPLETE`.

## Handoff

Return a compact execution handoff only:

```text
STATUS: COMPLETE | BLOCKED
experiment: ...
run: ...
server.ref: server-2@192.168.1.42
server.id: server-2
server.ip: 192.168.1.42
runner: ...
requested horizon: ...
final observed progress: ...
run-paths manifest: Project/.../experiment/run-paths.yaml
fluent working directory: ...
local case: ...
local final data: ...
report/monitor outputs: declared -> actual
latest verified recovery artifact: ...
onedrive final/recovery artifact: ...
durability: VERIFIED | LOCAL_ONLY | NOT_REQUIRED
log/transcript: ...
path anomaly: ...
execution failure/anomaly: ...
```

Do not perform CFD interpretation here. Successful completion hands the data to numerical analysis. A blocked run hands the execution evidence back to the scientific loop.