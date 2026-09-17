---
name: supervise-fluent-run
description: "Supervise an approved long Fluent hypothesis run after HYPOTHESIS_RUN_READY passes, using the MCP execution route. On Codex, verify terminal evidence and wake the exact originating thread; otherwise remain attached."
---

# Supervise Fluent Run

Own long-run supervision, not solver discovery or scientific interpretation.
Discovery remains attached and does not use this detached path merely to avoid
waiting. Follow [MCP integration](../fluent-live-inspection/mcp-integration.md).

## Require readiness

Read `CONTEXT.md`, `phase-state.yaml`, the approved setup and `run-paths.yaml`.
Require `DISCOVERY_EVIDENCE`, `HYPOTHESIS_DEFINITION` and
`HYPOTHESIS_RUN_READY` all `PASS`, with no material unresolved recovery block.
Require the authorized candidate ID, exact parent/prepared pair, run/endpoint
identity and ownership, initialization intent, paths, evidence streams, final
pair, verifier and durability plan. Confirm the recorded implementation proof
includes paired save/reopen, invariant readbacks, smoke and instrumentation.

For ordinary steady full-geometry qualification require at least 10,000
iterations, unless the setup declares scoped Auto Loop qualification (normally
2,000) with a correspondingly bounded claim or an equivalent non-iteration
basis. Preserve any required continuation/restart qualification. A mode label
alone grants no permission to launch.

## Keep the existing supervisor

On Codex use `PyAnsys/scripts/orchestration/run_and_handoff.py`, backed by
`PyAnsys/src/pyansys_fluent/run_handoff.py`. Read the current job schema in
`PyAnsys/queues/run-and-handoff.example.yaml`; preserve its actual field names.
Supply argv lists rather than shell strings, an explicit cwd, run-specific logs
and manifest, required-file checks, a deterministic verifier and both terminal
wake triggers. Keep the job input derived from canonical `run-paths.yaml`.

For generated Fluent execution, `runner.command` uses the existing
`PyAnsys/scripts/orchestration/execute_fluent_code.py` with `--server-id`,
`--code-file` and a fresh `--output-json` from the path contract. A coherent
MCP client worker is also appropriate when multiple calls/readbacks are needed.
Keep the approved solve and final-save sequence in that worker lifetime.
Use a direct domain worker only for a named, reviewed capability gap under the
shared contract; it is not the default because an old runner exists.

The snippet uses upstream's `solver` binding. The worker validates and executes
through MCP; neither the supervisor nor a skill may bypass sandbox rejection.
MCP does not provide a durable job scheduler, final-save verifier or AI wakeup.

## Verify completion independently

`EXECUTED`, a zero exit code, elapsed time, a receipt filename or a status summary
is not completion proof. The verifier must parse the execution outcome and prove:

- the intended run reached the approved native iteration/physical-time horizon;
- the final matching case/data pair exists, is non-trivial and has the right identity;
- required histories, reports and checkpoints exist at the declared paths;
- required continuation endpoints and canonical path reconciliation are present.

Use reviewed filesystem/evidence helpers when the worker cannot inspect the
remote filesystem directly. Required-file presence alone cannot establish the
saved state or horizon. Empty/partial receipts and missing required streams block.

## Runtime handoff

On Codex, capture `CODEX_THREAD_ID` at launch; an explicit session ID is only an
override. Require both terminal wake triggers and a working verifier before a
detached job starts. Never use `--last` for autonomous handoff.

```text
RUNNING → approved MCP worker → VERIFYING
→ persist COMPLETE | BLOCKED
→ resume exact originating thread as the final handoff action
```

The wake prompt must direct the thread to read the terminal manifest and
`phase-state.yaml`, reconcile identity/horizon, verify `HYPOTHESIS_EXECUTION`,
produce the planned analysis/figures, verify `HYPOTHESIS_EVIDENCE`, and continue
the same loop. A failed AI handoff after verified completion is recorded
separately; it does not justify rerunning CFD.

On Cursor or a runtime without self-resume, stay attached for the approved
horizon and retain the same terminal proof. Do not require `CODEX_THREAD_ID`
or run `codex exec resume` there. Missing exact-thread support prevents this
Codex detached route, not an explicitly available attached route.

## Supervision and failure

Refuse duplicate launch while a prior job manifest is unresolved. Inspect whether
the prior run is active, complete, blocked or uncertain before any forced rerun.
A lost MCP response or execution error can follow partial mutation or a continuing
solve. Status calls may wait behind a solve; use file-backed progress where
available. Preserve `BLOCKED` and reconcile before replay, not a competing client.

Poor residuals, balances or disappointing physics are evidence, not early-stop
permission while Fluent can reach the approved horizon. Follow a different
stop rule only when the experiment contract explicitly defines it. FPE, fatal
error, failed initialization/save/verifier or unreconciled identity are blockers.
Preserve evidence and wake the exact Codex thread on `BLOCKED` too.

The worker must not redesign numerics, reinitialize or automatically restart from
a checkpoint. The scientific loop chooses an authorized recovery. Fluent stays
running through client cleanup; process restart is not recovery authority.
Promote only important final/selected recovery pairs under the OneDrive plan.

## Handoff record

Keep the existing operational manifest: job/phase/setup/run, mode/horizon,
endpoint, command/cwd/log/return code, worker PID, timestamps, final observed
progress, pair/history checks, verifier outcome and runtime-specific wake status.
It does not replace `run-paths.yaml` or `phase-state.yaml`. `COMPLETE` verifies
execution only; hypothesis evidence and phase closure still require their gates.
