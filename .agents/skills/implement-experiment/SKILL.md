---
name: implement-experiment
description: Execute an approved setup through MCP after lifecycle permission; stage the exact parent, prove the child and instrumentation, then run discovery attached or hand qualification to the self-waking supervisor.
---

# Implement experiment

Get the approved setup done as written. Use
[MCP integration](../fluent-live-inspection/mcp-integration.md) for generic
Fluent operations; retain P4P's scientific and execution proof. This skill
implements, not designs, the experiment.

## Require permission before mutation

Read `CONTEXT.md` and `phase-state.yaml`. Match the setup's candidate ID, purpose,
delta, invariants, evidence contract and gate linkage to human approval for Phase
Loop or `origin: auto-loop` / `origin: autonomous-recovery` within its envelope.
Block unresolved provenance or material recovery before touching the case.

Discovery requires `PHASE_CONTRACT == PASS` and `DISCOVERY_DESIGN == PASS`.
Hypothesis preparation requires `DISCOVERY_EVIDENCE == PASS` and
`HYPOTHESIS_DEFINITION == PASS`. The long solve additionally requires
`HYPOTHESIS_RUN_READY == PASS`, granted only after implementation proof below.
A mode label or MCP tool's availability grants no lifecycle permission.

## Receive placement and path authority

Require `fluent-fleet-orchestration`'s plan: artifact/setup/run IDs, exact parent
pair, `server.ref`/ID/IP, canonical sibling `run-paths.yaml`, Fluent working
directory, staging/run roots, prepared/final/checkpoint paths, required histories,
logs/receipts/manifests, durability intent and granted session authority.

Stage a missing parent through verified local/OneDrive copies. Confirm paired
identity using hashes/manifests where available and strongest independent readback
otherwise. Matching filenames or server aliases are not proof.

Under an exclusive lease, follow approved takeover while preserving valuable
unreplicated state and the Fluent process. Do not overwrite durable parents or
start a second writer. Host filesystem/transfer operations remain P4P support,
not a reason to bypass MCP for generic setup work.

## Preserve scientific intent

Treat `setup.md` as the contract. No additional model, different horizon, new
hypothesis, changed evidence or opportunistic numerical tuning belongs here.
Make a necessary implementation adaptation only when its scientific equivalence
is demonstrated; otherwise return a blocker to the calling loop.

Use `fluent-live-inspection` for live paths/state and `fluent-manual-researcher`
for semantics/prerequisites. Build using `fluent-case-build-and-run`: discovered
MCP paths → `validate_code` → `run_code` → independent readback. Existing domain
workers are allowed only for the documented capability gap under the shared policy.

## Prove filesystem, child and streams

Before the planned solve:

1. Create and prove writable declared run/report/log/checkpoint directories.
2. Inspect inherited output definitions, resolve relative/ambiguous destinations,
   preserve their scientific definitions, and verify the actual working directory.
3. Reconcile the same canonical `run-paths.yaml`; invent no competing manifest.
4. Read back every intended critical change and invariant.
5. Save the prepared paired case/data, verify both files, reopen the exact pair
   in the preserved owned session, reacquire, and repeat the audit.
6. Initialize only if required; execute the planned smoke test, normally about
   50 iterations, and prove progress plus required durable evidence streams.

Required histories/equation residuals that cannot be reconstructed later must
write during smoke. Missing evidence, drift or readback/save-reopen mismatch
returns `BLOCK` for repair or upstream redesign, never retrospective waiver.

## Discovery: stay attached

After preparation passes, run the fixed discovery budget synchronously through
an MCP worker. Keep the scientific goal attached through terminal evidence and
immediate analysis; do not use detached hypothesis handoff to avoid waiting.

A timeout or lost response means uncertain execution. Reconcile manifests,
file-backed progress and safe live queries, then continue waiting if the approved
solve is advancing. Never replay a possibly applied command.

Verify the actual requested horizon, final pair and required histories. Return
execution facts to `verify-phase-transition` for `DISCOVERY_EXECUTION`; this
skill does not grant scientific evidence sufficiency.

## Hypothesis: earn readiness, then supervise

Check the approved qualification basis: ordinary steady full-geometry work needs
10,000+ iterations, unless an explicitly scoped Auto Loop horizon (normally
2,000) limits the claim accordingly, or a scientifically equivalent non-iteration
basis is specified. Carry required continuation/restart evidence for stationary
or bounded claims.

Supply identity, pre/post-save readbacks, smoke/streams, horizon, paths and
completion/wakeup proof to `verify-phase-transition`. Launch only after
`HYPOTHESIS_RUN_READY == PASS` is recorded.

Use `supervise-fluent-run` with the MCP worker. Codex launches through
`run_and_handoff.py`, captures exact `CODEX_THREAD_ID`, verifies terminal evidence
and wakes that thread on both `COMPLETE` and `BLOCKED`; never use `--last` or
background-launch the raw runner. Other runtimes remain attached.

Attempt the full approved horizon while Fluent can continue. Poor residuals,
balances or routing are evidence, not authority to change the experiment.

## Verify completion and durability

An `EXECUTED` MCP receipt, command submission, zero exit code or elapsed time is
not completion. Prove the final saved state belongs to this run, reached the
requested iteration/time horizon, and has the required files at declared paths.
An interrupted/empty receipt or missing required stream blocks completion.

Terminal execution `COMPLETE` does not pass the hypothesis or phase. The resumed
loop must verify `HYPOTHESIS_EXECUTION` and then `HYPOTHESIS_EVIDENCE`.

Promote important finals, likely parents and selected costly recovery pairs to
approved OneDrive storage. Record artifact ID, source setup/run, progress,
filenames, origin `server.ref`, hashes where feasible and durability in
`run-paths.yaml`. Do not upload every autosave. Failed promotion leaves an intact
local pair and explicit `LOCAL_ONLY` debt, not a claim of replication.

## Handoff

Return lifecycle prerequisites; parent/staging proof; canonical paths and working
directory; delta/invariant readbacks; paired save/reopen; smoke/stream checks;
requested versus observed horizon; server, worker and MCP receipt; final/history
and recovery locations; terminal verifier/wakeup status; durability; and all
implementation deviations or blockers. Scientific interpretation follows downstream.
