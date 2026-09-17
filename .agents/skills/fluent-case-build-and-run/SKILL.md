---
name: fluent-case-build-and-run
description: Build and prove an approved Fluent child through MCP, with dependency-ordered changes, exact paths, strict readback/save-reopen verification and smoke/instrumentation gates.
---

# Fluent case build and run

Implement a case that has already earned scientific permission. Use
[MCP integration](../fluent-live-inspection/mcp-integration.md) for all generic
Fluent operations and retained-worker exceptions. This skill owns setup proof,
not experiment selection or phase closure.

## Establish authority, identity and scope

Receive the approved setup, lifecycle permission and canonical `run-paths.yaml`
from `implement-experiment` / `fluent-fleet-orchestration`. Require exact parent
artifact and case/data paths, run ID, `server.ref`, declared mutable leaves,
invariants, output destinations and recovery plan. Block unresolved material
recovery or identity/path ambiguity before mutation.

An exclusive goal lease permits planned loaded-state replacement, after preserving
valuable unreplicated state. It does not permit closing/relaunching Fluent or
overwriting durable parents. Use an owned, still-running session and one writer.

## Ground before mutation

Use `fluent-live-inspection`: discover candidate APIs, then inspect actual active
state with MCP descriptors, named-object tools and `get_state`. For multiphase/DPM,
include phase/material/boundary identity, turbulence/energy, injections, wall fates
and relevant topology. `summarize_setup` alone is not an invariant audit.

For each dependency-sensitive change:

```text
inspect parent → validate_code → run_code for approved parent change
→ reacquire → describe active child/options → validate and execute child
→ independent critical readback → continue only on a match
```

Reacquire after loads, model/type/phase changes and object creation. Semantic or
prerequisite uncertainty goes to `fluent-manual-researcher`; missing paths never
justify guessing, recursive probing or silently enabling unrelated models.

## Resolve outputs before solving

Inspect inherited reports, monitors, autosaves, exports and transcripts through
MCP. Match their destinations to `run-paths.yaml`. Change only output paths,
preserving scientific definitions. For required relative filenames deliberately
establish and verify Fluent's working directory; loading a case does not establish
it. Create and prove writable directories with the approved host/file support,
not a guessed local path or code pasted around the MCP sandbox.

Read back important destinations and reconcile the same canonical path file after
smoke and final execution. Block unresolved output locations before compute.

## Build and prove the child

1. Preserve any required paired recovery state.
2. Apply only the approved delta through validated MCP execution.
3. Independently read back every critical delta and invariant.
4. Write the prepared case/data pair to declared full paths; verify both files.
5. Reopen that pair in an owned, still-running session and reacquire objects.
6. Repeat the critical audit against expected values, not merely the previous snapshot.
7. Record parent/child identity, Fluent version, changes, readbacks and paths.

Use captured-path comparison as supporting evidence only. Neither a successful
setter, an `EXECUTED` receipt nor `WITHIN_DECLARED_DIFF_SCOPE` proves the setup.
Required missing, inactive, failed or truncated state blocks the audit.

## Smoke and instrumentation

Initialize only when the setup requires it. Run its smoke test, normally about
50 iterations for iteration-based cases, through the approved MCP worker.
Require actual iteration/physical-time advancement, no setup/readback drift,
required file-backed histories at declared paths, required residual/equation
capture, and no unresolved output ambiguity.

A missing decisive stream returns `BLOCK` for autonomous repair, equivalent
instrumentation or upstream claim redesign. Do not launch and hope to reconstruct
uncaptured histories later. Smoke and main-run budgets remain distinct and recorded.

## Mode-aware handoff

Discovery remains attached: verified child and smoke → MCP worker for the fixed
short horizon → terminal proof → immediate evidence analysis. A tool timeout is
not a terminal state. Reconcile progress; do not replay or open a competing writer.

Hypothesis execution requires `HYPOTHESIS_RUN_READY == PASS`. Preserve the default
10,000+ steady full-geometry qualification horizon, the explicitly scoped Auto Loop
2,000-iteration exception with bounded claim, or an approved equivalent basis.
On Codex use `supervise-fluent-run`; on runtimes without self-resume stay attached.
Do not redesign the experiment after readiness. Poor numerical/physical behaviour
is evidence, not a stop condition while the approved run can continue.

## Recovery and handoff

Return execution facts and explicit blockers: lifecycle permission, exact parent
and child, recovery pair, path map, pre-save/post-reopen audits, smoke/streams,
requested and observed horizon, MCP worker/receipt, final/checkpoint/history/log
locations, durability and supervisor/wakeup status where applicable.

Blocked permission, identity, critical readback, save/reopen, initialization,
instrumentation, qualification depth or completion/wakeup proof prevents launch.
Use [autonomous recovery](../references/autonomous-recovery.md); exhausting a lane
means a durable `BLOCKED_AUTONOMOUS`, not a fabricated pass. Technical recovery
must preserve the scientific contract and session policy.
