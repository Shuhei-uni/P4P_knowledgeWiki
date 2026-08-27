# Python-Supervised Fluent Run and Recovery Policy

> The filename is retained for stable repository links. The current default is no longer a detached/native-run workflow.

## Key rule

For experiments inside `scientific-phase-loop`, run Fluent through Python/PyFluent and keep an agent supervising the runner terminal for the planned horizon.

```text
verified case
-> Python/PyFluent runner
-> initialization if required
-> approved calculation horizon
-> final save/verification
-> execution handoff
```

The agent is expected to remain active for the run, but mostly read-only while Fluent is advancing. The agent watches for meaningful execution events rather than repeatedly reasoning about every iteration.

TUI-driven iteration, Fluent journal/batch submission, and GUI-owned execution are not automatic fallbacks. They require explicit human approval for that specific run.

## Why Python supervision is the default

The autonomous scientific loop benefits from having an execution agent present when the calculation begins, fails, completes, or leaves its state uncertain. Initialization failures, floating-point errors, PyFluent exceptions, lost connections, failed final writes, and Fluent process crashes should be detected at the execution boundary rather than discovered much later.

The supervising agent does not interpret the science. Poor residuals, poor balances, oscillation, or unexpected physics are normally evidence to analyse after the planned run, not reasons to alter the experiment while it is executing.

## Runner contract

Use a Python runner whose intended sequence is explicit:

```text
connect
-> verify endpoint and case identity
-> load/confirm approved case
-> configure approved remote output/checkpoint paths
-> initialize if required
-> run the planned horizon
-> write final data
-> verify final data
```

Prefer a single clear PyFluent solve call for the planned horizon, or another coarse bounded structure required by the approved experiment. Do not build one-iteration polling loops simply to keep the agent awake.

Do not hide TUI commands inside a Python script and call that a Python/PyFluent run. If the required operation is only available through TUI or a Fluent journal, stop and obtain explicit human approval before using it.

## Remote paths and server knowledge

Use explicit remote paths from the experiment setup when supplied. Otherwise use verified non-secret filesystem knowledge from `PyAnsys/server-profiles/`.

A server alias is routing only. It does not identify the loaded case, current iteration, or correct experiment directory.

Do not guess output roots or silently reuse a previous campaign directory. Keep active run data on the Fluent machine's intended storage and use run-specific names that cannot be confused with an earlier simulation.

## Autosave and recovery

Python supervision does not remove the value of Fluent-side autosave. When the experiment is long enough to justify recovery checkpoints, configure Fluent's autosave controls through the approved Python/PyFluent path before the main solve.

Useful habits:

- use a run-specific remote autosave root;
- keep enough recent checkpoints to recover from a failure;
- know which case file matches the data checkpoints;
- verify the configured remote paths before starting;
- do not treat a local ledger or filename pattern as proof that a remote checkpoint exists.

The final data save may be performed by the Python runner after the calculation call returns. For long runs, autosave provides recovery evidence if the runner, connection, or Fluent process fails before that final save.

## Agent supervision

Use `supervise-fluent-run` for the long-lived execution period.

Most of the time the correct action is simply to wait. Do not narrate every residual row or repeatedly inspect the solver without a reason.

Wake on meaningful events such as:

- initialization success/failure;
- calculation launch;
- checkpoint observation;
- Python exception;
- Fluent fatal/floating-point error;
- unexpected Fluent/runner termination;
- connection uncertainty;
- calculation return;
- final data write/verification.

The runner terminal is the primary execution surface. `scripts/inspection/monitor_native_run.py` may still be used as a separate read-only helper when it adds useful state evidence, despite its legacy name. It must never become a second mutating controller.

## Distinguish failure types

### Normal scientific behaviour — continue

Do not stop a run merely because:

- residuals are poor, noisy, oscillatory, or slowly converging;
- balances are poor;
- physical monitors are unexpected;
- the result appears scientifically unpromising;
- a secondary read-only request cannot respond while the main calculation is busy.

If Fluent can continue and the experiment contract does not define another stop rule, let the approved horizon finish.

### Execution blocker — preserve and return

Treat these as execution blockers when they prevent faithful continuation:

- initialization failure;
- floating-point/fatal Fluent error;
- Fluent process crash/exit;
- Python/PyFluent runner exception before completion;
- run state that cannot be reconciled safely;
- required final data cannot be written or verified;
- recovery/output state is uncertain enough that another run command could duplicate or overwrite unknown progress.

Capture the error, preserve the newest verified state, record the final observed progress, and return the blocker to `implement-experiment` / `scientific-phase-loop`. Do not redesign numerics inside the run supervisor.

## Connection loss and uncertain progress

A lost gRPC connection is not automatically a Fluent numerical failure.

When state becomes uncertain:

1. establish whether the same Fluent process still exists;
2. determine the newest independently observed progress;
3. inspect the latest verified remote checkpoint/data state;
4. do not silently repeat a solve command whose completion is unknown;
5. resume or restart only after the actual state has been reconciled and the upstream execution decision is clear.

If reconciliation requires changing the experiment, return control upstream rather than improvising inside the supervisor.

## Completion proof

A Python command returning is not enough.

For an iteration-based run, verify at minimum:

- requested iteration target;
- final independently observed iteration count;
- expected final `.dat.h5` exists;
- matching case/restart identity is known;
- required logs/histories/checkpoints can be located;
- execution anomalies are recorded.

If the target was not reached, report the run as blocked/incomplete.

## Human-approved alternative execution

TUI, Fluent journals, native queues, or GUI execution may still be useful in special circumstances, but they are outside the autonomous-loop default.

Before using one, obtain explicit human approval for the specific run and record why Python/PyFluent supervision was not suitable.

Legacy Stage-3/Stage-4 native queue scripts and journals remain historical implementation evidence. Their existence does not authorize new autonomous-loop runs to use the same mechanism without approval.
