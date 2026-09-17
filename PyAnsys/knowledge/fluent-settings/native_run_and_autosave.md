# MCP-Supervised Fluent Run and Recovery Policy

The filename remains for stable links. Use the
[MCP integration contract](../../../.agents/skills/fluent-live-inspection/mcp-integration.md)
for live calls, preserving sessions, generated code and retained-worker exceptions.
It replaces generic script-first execution, not the scientific lifecycle.

## Execution ownership

`implement-experiment` and `fluent-case-build-and-run` own identity, approved
setup, readback, paired save/reopen, paths, smoke and evidence-stream readiness.
`supervise-fluent-run` owns long-run waiting, terminal proof and handoff. Read
those skills rather than maintaining a second lifecycle here.

Discovery stays attached through the declared short solve and immediate evidence
review. Use a clear MCP solve call or approved coarse structure; one-iteration
keepalive loops add no scientific proof. A timeout does not end the solve.

For a Codex hypothesis after `HYPOTHESIS_RUN_READY == PASS`, use
`PyAnsys/scripts/orchestration/run_and_handoff.py` and the existing job schema
in `PyAnsys/queues/run-and-handoff.example.yaml`. The runner uses the MCP client
or `execute_fluent_code.py`, with the planned solve/save sequence and fresh
execution receipt. Preserve the exact `CODEX_THREAD_ID`, both `COMPLETE` and
`BLOCKED` triggers, and final exact-thread resume; never use `--last`.

On Cursor or a runtime without self-resume remain attached. Missing Codex thread
metadata is expected there, not permission to omit deterministic completion proof.

## Autosave and filesystem

Before the main solve, discover/configure Fluent autosave and required Report
File destinations via MCP. Use actual run-specific paths from the experiment's
canonical `run-paths.yaml`. Preserve scientific definitions while correcting
inherited relative destinations. Loading a case does not prove a cwd change.
Reviewed host helpers check/create directories and files where MCP lacks remote
filesystem capabilities. Prove writability and required streams during smoke.

Know which case matches each data checkpoint. Do not infer a paired recovery
state from a filename pattern, status string or local ledger. Preserve enough
local checkpoints for the approved recovery purpose, not every iteration.
Promote important final/selected expensive recovery pairs to the approved
OneDrive destination, verify the copied pair and record identity/hash/progress/
origin. Keep `LOCAL_ONLY` debt explicit when replication is incomplete.

## Completion and uncertainty

The MCP worker's `EXECUTED` receipt is not the supervisor's `COMPLETE`. The
completion verifier must inspect actual run identity, native progress, final
paired state and all required histories/checkpoints. Receipt/file presence or a
zero return code alone is insufficient. Use a reviewed remote evidence helper
when files are not visible to the worker; record the capability gap.

Persist terminal `COMPLETE` or `BLOCKED` before AI handoff. Keep handoff status
separate: verified CFD completion with a failed wakeup must not rerun CFD.
The operational manifest never replaces phase-state or the Project path map.

Refuse duplicate launch while an older job is unresolved. Lost responses may
follow completed or still-running commands. Reconcile live state and file-backed
progress before any retry, reconnect or forced rerun. Status calls can wait behind
a solve; never add a competing writer to get around that wait.

`scripts/inspection/monitor_native_run.py` is retained only as a reviewed read-only
progress/evidence helper when its complete stream is needed. It is not another
mutating controller. Record the missing capability and inspect cleanup before use.

## Recovery boundaries

Attempt the approved horizon unless an explicit experiment stop condition or real
execution failure prevents it. Poor residuals, balance, oscillation or disappointing
physics are evidence, not permission to alter numerics or shorten the experiment.
Initialization failure, FPE/fatal error, incomplete required save/history, failed
verifier or unreconciled run state remains a block with observed progress recorded.

The worker does not change models/URFs/timestep, reinitialize or automatically
restart from a checkpoint. The active scientific loop applies authorized recovery,
retains evidence and continues another valid lane when necessary. Preserve every
Fluent process; reconnecting a client is not restarting the solver.

TUI, Fluent journals/native queues and GUI-owned execution are not automatic
fallbacks. TUI/journal use requires explicit approval for that run plus manual-
grounded recoverable-child verification. Historical native scripts are evidence,
not new-run authority. Never disguise TUI inside Python or bypass MCP's sandbox.
