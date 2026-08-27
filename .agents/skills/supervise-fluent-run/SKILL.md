---
name: supervise-fluent-run
description: "Supervise a long Fluent calculation launched from a Python runner. Use inside implement-experiment after the case has been verified and smoke-tested, when an agent should stay with the terminal, observe execution efficiently, classify real run failures, verify final data, and hand back clean execution facts without redesigning or interpreting the experiment."
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

- experiment/setup identity;
- server alias;
- exact remote case path;
- exact remote run/output directory;
- Python runner path and arguments;
- initialization intent;
- requested iteration/time horizon;
- expected final data path;
- checkpoint/autosave paths when configured;
- terminal/transcript/log paths when available.

Use the server profile under `PyAnsys/server-profiles/` when one exists. A server profile describes remote directory layout only; it does not establish which scientific case is loaded.

Do not guess a remote output root. If neither the setup nor a verified server profile establishes the path, return the missing execution information before launching.

## Default to Python-supervised execution

Launch the approved run through Python/PyFluent and keep the agent attached to the runner terminal for the intended horizon.

Prefer one clear run command for the planned horizon rather than fine-grained agent-controlled iteration loops. Python may own the synchronous run call and final save; the supervising agent owns observation, failure classification, and handoff.

Do not switch to TUI iteration, a Fluent journal, GUI submission, or another execution mechanism because it seems more convenient. Those are human-approved exceptions. If the Python/PyFluent path cannot execute the approved setup, report the blocker and request approval before using TUI or a journal.

## Stay token-efficient

Most of the supervisor's lifetime should require no reasoning.

Do not narrate normal iteration-by-iteration progress. Wake up on meaningful events such as:

- initialization returns or fails;
- the calculation begins;
- a checkpoint/final file is observed;
- the runner emits an exception or Fluent fatal error;
- the runner or Fluent process terminates unexpectedly;
- connection state becomes uncertain;
- the calculation command returns;
- the requested horizon is reached.

When the terminal is simply advancing normally, wait and continue observing.

Use read-only monitoring helpers when useful, but do not make continuous secondary polling a requirement for the solve to proceed.

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
- case/data state becomes uncertain enough that repeating work could duplicate or overwrite unknown progress.

## Reconcile uncertainty; never blindly repeat work

Treat observer/gRPC loss separately from Fluent numerical failure.

If connection or runner state becomes uncertain:

1. determine whether the same Fluent process still exists;
2. establish the newest independently observed iteration/progress state;
3. identify the latest verified case/data or autosave artifact;
4. do not issue another run command while completion of the previous command is uncertain;
5. resume observation only after the actual state is reconciled.

A local status file or server alias is not sufficient evidence of simulation progress or case identity.

## On a blocker, preserve and hand back

Do not redesign the experiment from inside this skill.

When a real execution blocker occurs:

- stop issuing new mutating commands;
- preserve the last verified checkpoint/data state;
- capture the relevant terminal error, Fluent message, and runner exception;
- record the last independently observed iteration/progress;
- classify whether the failure is initialization, solver/numerical execution, Python/PyFluent execution, transport/state uncertainty, or file/output failure;
- hand the execution facts back to `implement-experiment` and `scientific-phase-loop` for the rethink.

Do not automatically lower relaxation factors, change timestep, alter initialization, change models, or rerun from a checkpoint. Those are scientific or implementation decisions owned upstream.

## Completion requires verified data

Do not claim success because the Python command returned or enough wall time elapsed.

For an iteration-based run, verify at minimum:

- the requested target;
- the final independently observed iteration count;
- the expected final `.dat.h5` exists and belongs to the intended run;
- the matching case/restart identity is known;
- required logs/histories/checkpoints are locatable;
- any execution anomaly is recorded.

If the target was not reached, return `BLOCKED`, not `COMPLETE`.

## Handoff

Return a compact execution handoff only:

```text
STATUS: COMPLETE | BLOCKED
experiment: ...
server: ...
runner: ...
requested horizon: ...
final observed progress: ...
case: ...
final data: ...
latest verified recovery artifact: ...
log/transcript: ...
execution failure/anomaly: ...
```

Do not perform CFD interpretation here. Successful completion hands the data to numerical analysis. A blocked run hands the execution evidence back to the scientific loop.