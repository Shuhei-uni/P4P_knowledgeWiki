# Python-Supervised Fluent Run and Recovery Policy

> The filename is retained for stable repository links. The current default is a
> detached Python/PyFluent run worker with a terminal manifest and event-driven
> Codex handoff.

## Key rule

For experiments inside `scientific-phase-loop`, run Fluent through the approved
Python/PyFluent runner, but do **not** keep an AI agent alive for the full solve.

```text
verified case
→ detached run-and-handoff worker
→ approved calculation horizon
→ final save
→ deterministic completion verification
→ COMPLETE | BLOCKED manifest
→ resume exact Codex session
```

The worker owns the long wait. The scientific agent owns the decisions before
launch and after the completion/failure event.

TUI-driven iteration, Fluent journal/batch submission, and GUI-owned execution
are not automatic fallbacks. They require explicit human approval for that
specific run.

## Why detached supervision is the default

A three-hour solve does not need three hours of AI context. The important
execution boundary is whether the deterministic runner can faithfully reach the
approved horizon, save the required state, and prove that the declared outputs
exist.

The detached worker therefore remains alive while the Python/PyFluent runner is
blocking, captures its logs, verifies terminal outputs, persists a machine-
readable manifest, and then launches a fresh Codex continuation using the exact
recorded session ID.

This separates concerns cleanly:

```text
agent: choose and approve experiment
worker: execute and verify
agent: analyse or diagnose after terminal event
```

Poor residuals, poor balances, oscillation, or unexpected physics are normally
evidence to analyse after the planned run, not reasons for the worker to alter
the experiment mid-run.

## Runner contract

Use a Python runner whose intended sequence is explicit:

```text
connect
→ verify endpoint and case identity
→ load/confirm approved case
→ configure approved remote output/checkpoint paths
→ initialize if required
→ run the planned horizon
→ write final case/data as required
→ return success only after its own deterministic execution steps complete
```

Prefer one clear PyFluent solve call for the planned horizon, or another coarse
bounded structure required by the approved experiment. Do not build one-
iteration polling loops merely to emulate an awake agent.

Do not hide TUI commands inside a Python script and call that a Python/PyFluent
run. If the required operation is only available through TUI or a Fluent
journal, stop and obtain explicit human approval before using it.

## Run-and-handoff contract

The generic launcher is:

```text
PyAnsys/scripts/orchestration/run_and_handoff.py
```

The reusable implementation is:

```text
PyAnsys/src/pyansys_fluent/run_handoff.py
```

The YAML job contract defines:

- a unique job ID;
- the exact runner argv and working directory;
- runner/worker log paths;
- the terminal manifest path;
- required locally visible final files and/or a deterministic verifier command;
- the exact Codex session/thread ID;
- whether `COMPLETE`, `BLOCKED`, or both should trigger the handoff.

Use `PyAnsys/queues/run-and-handoff.example.yaml` as the template.

The job spec is a derived execution input. It does not replace the experiment's
canonical `Project/.../run-paths.yaml`.

## Launch and lifecycle

Normal launch:

```text
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

The launcher starts a detached worker and returns immediately.

The worker lifecycle is:

```text
RUNNING
→ execute approved runner
→ VERIFYING
→ required-file checks / deterministic verifier
→ COMPLETE or BLOCKED
→ write terminal manifest
→ codex exec resume <SESSION_ID> <handoff prompt>
```

The terminal manifest is written before the Codex process is launched. This
means run completion is still recoverable even if the AI handoff itself fails.

Never use `codex exec resume --last` for autonomous multi-server work. Several
Fluent jobs may finish in any order, so each job must carry the exact session ID
that owns its scientific loop.

## Completion proof

A Python command returning zero is not enough.

Each run-and-handoff job must declare at least one terminal proof:

1. **required files** visible to the worker, checked for existence and minimum
   size; and/or
2. a **deterministic verifier command** that returns zero only when the declared
   remote final state is verified.

The verifier is the preferred path when the worker cannot directly see Fluent's
remote filesystem. Reuse existing read-only PyFluent/remote-file helpers rather
than inventing filename assumptions.

For an iteration-based run, the complete execution evidence should ultimately
cover:

- requested iteration target;
- final independently observed iteration count where available;
- expected final `.dat.h5` existence;
- matching case/restart identity;
- required logs/histories/checkpoints;
- execution anomalies;
- canonical path reconciliation in the Project packet.

If the runner exits nonzero, a required file is absent/undersized, or the
verifier fails, the job is `BLOCKED` rather than `COMPLETE`.

## Duplicate-run protection

The launcher refuses to start when a prior job manifest already exists.

This is deliberate. A fresh agent must not repeat expensive work just because
its conversational context was lost.

Before using `--force`, reconcile whether the previous job:

- is still active;
- completed;
- blocked;
- left ambiguous Fluent state;
- already produced reusable final/recovery artifacts.

Only then may a forced rerun be justified.

## Remote paths and server knowledge

Use explicit remote paths from the experiment setup and canonical
`run-paths.yaml`. Otherwise use verified non-secret filesystem knowledge from
`PyAnsys/server-profiles/`.

A server alias is routing only. It does not identify the loaded case, current
iteration, or correct experiment directory.

Do not guess output roots or silently reuse a previous campaign directory. Keep
active run data on the Fluent machine's intended storage and use run-specific
names that cannot be confused with an earlier simulation.

## Autosave and recovery

Detached supervision does not remove the value of Fluent-side autosave. When
the experiment is long enough to justify recovery checkpoints, configure
Fluent's autosave controls through the approved Python/PyFluent path before the
main solve.

Useful habits:

- use a run-specific remote autosave root;
- keep enough recent checkpoints to recover from a failure;
- know which case file matches the data checkpoints;
- verify configured remote paths before starting;
- do not treat a local ledger or filename pattern as proof that a remote
  checkpoint exists.

Routine autosaves may remain local for immediate same-server recovery. Promote
selected expensive recovery pairs and scientifically important final case+data
pairs through the OneDrive durability policy when required.

## Distinguish failure types

### Normal scientific behaviour — continue

Do not stop a fixed-horizon run merely because:

- residuals are poor, noisy, oscillatory, or slowly converging;
- balances are poor;
- physical monitors are unexpected;
- the result appears scientifically unpromising.

If Fluent can continue and the experiment contract does not define another
stop rule, let the approved horizon finish.

### Execution blocker — preserve and hand off

Treat these as blockers when they prevent faithful completion:

- initialization failure;
- floating-point/fatal Fluent error;
- Fluent process crash/exit;
- Python/PyFluent runner exception before completion;
- run state that cannot be reconciled safely;
- required final data cannot be written or verified;
- deterministic final-state verification fails;
- output identity is uncertain enough that another run could duplicate or
  overwrite unknown progress.

The worker should preserve the available execution evidence, write `BLOCKED`,
and still invoke the configured Codex handoff. The resumed scientific loop then
decides whether to recover, repair, redesign, or return to the human.

Do not automatically lower relaxation factors, change timestep, change models,
or restart from a checkpoint inside the worker.

## Connection loss and uncertain progress

A lost gRPC connection is not automatically a Fluent numerical failure.

If the approved runner or verifier encounters uncertain state, establish as much
as possible about:

1. whether the same Fluent process still exists;
2. newest independently observed progress;
3. latest verified paired checkpoint/data state;
4. actual output paths versus the Project path map.

Do not silently repeat a solve command whose completion is unknown. Return a
`BLOCKED` execution handoff when safe reconciliation cannot be completed.

`scripts/inspection/monitor_native_run.py` remains available as a read-only
reconnecting evidence helper. It is not a second mutating controller and is no
longer a reason to keep the AI agent awake.

## Codex handoff

The current Codex CLI supports non-interactive session resume with:

```text
codex exec resume <SESSION_ID> <PROMPT>
```

The run worker launches that command only after writing the terminal manifest.
The resumed prompt points the agent to the manifest and the canonical Project
experiment packet.

The run status and AI handoff status remain separate. For example:

```text
status: COMPLETE
handoff.status: FAILED
```

means the simulation completed and was verified, but Codex could not be
launched. The scientific result must not be rerun merely because the hook failed.

## Human-approved alternative execution

TUI, Fluent journals, native queues, or GUI execution may still be useful in
special circumstances, but they are outside the autonomous-loop default.

Before using one, obtain explicit human approval for the specific run and
record why Python/PyFluent execution was not suitable.

Legacy Stage-3/Stage-4 native queue scripts and journals remain historical
implementation evidence. Their existence does not authorize new autonomous-loop
runs to use the same mechanism without approval.
