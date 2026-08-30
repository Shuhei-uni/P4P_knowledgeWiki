# Python-Supervised Fluent Run and Recovery Policy

> The filename is retained for stable repository links. Execution now has two
> deliberate modes: attached discovery runs and detached self-waking hypothesis
> tests.

## Key rule

For experiments inside `scientific-phase-loop`, run Fluent through the approved
Python/PyFluent path and preserve the scientific experiment mode.

```text
DISCOVERY
verified case
→ short Python/PyFluent run (~500-1000 iterations)
→ scientific agent stays attached and mostly waits
→ inspect evidence immediately
→ choose the next discovery experiment in the same active thread

HYPOTHESIS TEST
verified case
→ capture originating CODEX_THREAD_ID
→ detached run-and-handoff worker
→ approved calculation horizon
→ final save + deterministic verification
→ COMPLETE | BLOCKED manifest
→ mandatory resume of exact originating Codex thread
```

TUI-driven iteration, Fluent journal/batch submission, and GUI-owned execution
are not automatic fallbacks. They require explicit human approval for that
specific run.

## Why the modes differ

Discovery is intentionally fast and iterative. A 500-1,000 iteration screen is
short enough that ending the agent turn, sleeping, and later recreating context
adds unnecessary latency. During an active discovery campaign, the scientific
agent should stay alive through each short run so it can immediately inspect the
result, revise the working hypothesis, and launch the next useful probe.

Hypothesis tests are different. A long focused run should not consume hours of
AI context merely because Fluent is calculating. The background worker should
own the long wait, terminal evidence, and wakeup event, then return control to
the exact scientific thread that launched it.

This gives the intended split:

```text
discovery: agent → run → evidence → next probe
hypothesis: agent → background worker → wake same agent thread
```

Poor residuals, poor balances, oscillation, or unexpected physics are normally
evidence to analyse after the planned horizon, not reasons to silently alter the
experiment mid-run.

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
→ return success only after its deterministic execution steps complete
```

Prefer one clear PyFluent solve call for the planned horizon, or another coarse
bounded structure required by the approved experiment. Do not build one-
iteration polling loops merely to keep an agent awake.

Do not hide TUI commands inside a Python script and call that a Python/PyFluent
run. If the required operation is only available through TUI or a Fluent
journal, stop and obtain explicit human approval before using it.

## Discovery execution

Discovery mode does not use the detached handoff path as its normal execution
mechanism.

For each short discovery run:

1. keep the current scientific agent attached to the runner/terminal;
2. issue the approved short run as a clear Python/PyFluent calculation;
3. mostly wait while Fluent advances rather than narrating every iteration;
4. when the run returns, inspect the agreed screening evidence immediately;
5. revise the working hypothesis and decide whether another discovery run is
   justified;
6. if so, continue within the same active scientific thread.

This attached behaviour applies throughout the discovery campaign, not only to
the first case.

If a genuine execution blocker occurs, diagnose it immediately in the active
thread. Do not convert a discovery run to background mode simply because it is
convenient.

## Hypothesis run-and-handoff contract

The generic background launcher is:

```text
PyAnsys/scripts/orchestration/run_and_handoff.py
```

The reusable implementation is:

```text
PyAnsys/src/pyansys_fluent/run_handoff.py
```

The YAML job contract defines:

- a unique job ID;
- `job.mode: hypothesis-test`;
- the exact runner argv and working directory;
- runner/worker log paths;
- the terminal manifest path;
- required locally visible final files and/or a deterministic verifier command;
- `COMPLETE` and `BLOCKED` wakeup triggers;
- an optional explicit Codex session override.

Use `PyAnsys/queues/run-and-handoff.example.yaml` as the template.

The originating thread normally does **not** need to be copied manually into the
YAML. When the job is launched from Codex, the Python loader captures
`CODEX_THREAD_ID` from the process environment. `codex.session_id` is an
explicit override only when needed.

A hypothesis job is invalid if:

- the wakeup hook is disabled;
- the originating thread cannot be resolved;
- either `COMPLETE` or `BLOCKED` is missing from the trigger set;
- no deterministic completion proof is defined.

The job spec is a derived execution input. It does not replace the experiment's
canonical `Project/.../run-paths.yaml`.

## Hypothesis launch and lifecycle

Normal launch:

```text
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

The launcher resolves the originating Codex thread and starts a detached worker.
The current scientific turn may then end because the worker now owns the wakeup
obligation.

The worker lifecycle is:

```text
RUNNING
→ execute approved runner
→ VERIFYING
→ required-file checks / deterministic verifier
→ COMPLETE or BLOCKED
→ write terminal manifest
→ codex exec resume <ORIGINATING_THREAD_ID> <handoff prompt>
```

The final Codex resume is a **mandatory Python tail** for hypothesis mode. It is
not optional cleanup. The worker must attempt the wakeup after both `COMPLETE`
and `BLOCKED`, so progress does not depend on the human noticing that the
simulation probably finished and sending another prompt.

The terminal manifest is written before the Codex process is launched. This
means run completion is still recoverable even if the AI handoff itself fails.

Never use `codex exec resume --last` for autonomous multi-server work. Several
Fluent jobs may finish in any order, so each worker must resume its exact
originating thread.

## Completion proof

A Python command returning zero is not enough.

Each background hypothesis job must declare at least one terminal proof:

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
verifier fails, the hypothesis job is `BLOCKED` rather than `COMPLETE`, and the
same originating thread must still be woken.

## Duplicate-run protection

The background hypothesis launcher refuses to start when a prior job manifest
already exists.

This is deliberate. A fresh or resumed agent must not repeat expensive work just
because conversational context was lost.

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

Mode choice does not remove the value of Fluent-side autosave. When the
experiment is long enough to justify recovery checkpoints, configure Fluent's
autosave controls through the approved Python/PyFluent path before the main
solve.

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

### Execution blocker — preserve and continue the workflow

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

In discovery mode, the still-active scientific agent handles the blocker
immediately.

In hypothesis mode, the worker should preserve the available execution evidence,
write `BLOCKED`, and still invoke the mandatory Codex handoff. The resumed
scientific loop then decides whether to recover, repair, redesign, or return to
the human.

Do not automatically lower relaxation factors, change timestep, change models,
or restart from a checkpoint inside the execution worker.

## Connection loss and uncertain progress

A lost gRPC connection is not automatically a Fluent numerical failure.

If the approved runner or verifier encounters uncertain state, establish as much
as possible about:

1. whether the same Fluent process still exists;
2. newest independently observed progress;
3. latest verified paired checkpoint/data state;
4. actual output paths versus the Project path map.

Do not silently repeat a solve command whose completion is unknown. In
hypothesis mode, persist `BLOCKED` and wake the originating thread when safe
reconciliation cannot be completed.

`scripts/inspection/monitor_native_run.py` remains available as a read-only
reconnecting evidence helper. It is not a second mutating controller.

## Codex handoff status

The current Codex CLI supports non-interactive session resume with:

```text
codex exec resume <SESSION_ID> <PROMPT>
```

The hypothesis worker launches that command only after writing the terminal
manifest. The resumed prompt points the agent to the manifest and the canonical
Project experiment packet.

The CFD run status and AI handoff status remain separate. For example:

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
