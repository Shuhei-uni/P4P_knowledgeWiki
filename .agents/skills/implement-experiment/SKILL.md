---
name: implement-experiment
description: "Execute an approved setup faithfully in Fluent after the relevant phase transition gate has passed: stage the exact parent, prove paths and instrumentation, build/read back/save-reopen/smoke-test the case, then run discovery attached or hand a verified long hypothesis case to the self-waking supervisor."
---

# Implement Experiment

Get the approved setup done as written on the assigned Fluent server.

The scientific decisions have already been made. This skill owns faithful implementation/execution, not experiment design or phase closure.

## Require lifecycle permission before mutation

Read the phase-root `phase-state.yaml` before implementing a phase-loop experiment.

For **discovery** require:

```text
PHASE_CONTRACT == PASS
DISCOVERY_DESIGN == PASS
```

For **hypothesis-test** require:

```text
DISCOVERY_EVIDENCE == PASS
HYPOTHESIS_DEFINITION == PASS
```

Do not treat a mode label in `setup.md` as permission to skip lifecycle state.

`HYPOTHESIS_RUN_READY` is granted only **after** this skill has produced the implementation/readback/save-reopen/smoke/instrumentation proof and `verify-phase-transition` accepts it. Do not launch the long hypothesis solve before that gate is `PASS`.

If `phase-state.yaml` contains an unresolved `HUMAN_REQUIRED` lock, stop. Implementation may not bypass it by substituting an assumed target or different physical boundary.

## Receive the execution plan

Before mutating Fluent, require the placement/path contract from `fluent-fleet-orchestration`.

Know at minimum:

- setup ID and run ID;
- selected `server.ref`, server ID, and IP;
- exact parent artifact ID and verified case/data source;
- canonical sibling `run-paths.yaml`;
- exact remote parent/run/output paths;
- Fluent working directory;
- final case/data paths;
- checkpoint/autosave locations;
- required report/monitor/history outputs;
- runner/log/manifest paths;
- OneDrive durability intent when applicable;
- whether the active phase has exclusive Fluent fleet/session authority.

Do not substitute a convenient similarly named parent.

## Respect active-session authority

When `fluent-fleet-orchestration` has granted the active scientific goal an exclusive fleet lease, the assigned Fluent session is a working resource for this phase.

The execution plan may require stopping an inherited calculation, preserving a quick recovery pair, restarting/reloading Fluent, or replacing the loaded case. Follow that plan without asking the human again.

Do not silently destroy a valuable unpreserved endpoint when a recovery pair can be saved cheaply. Do not overwrite verified durable Project/OneDrive parents.

## Preserve the scientific setup

Treat `setup.md` as the scientific contract. Build the declared delta from the verified parent and preserve stated invariants.

Have essentially no scientific freedom here. Do not add models, alter the hypothesis, change the planned horizon, redefine evidence, or “improve” numerics because another choice seems better.

If Fluent/PyFluent requires a scientifically equivalent implementation change, make only that implementation adaptation and prove the final state. If equivalence cannot be established, return a blocker.

Use `fluent-live-inspection` first for uncertain live paths/state and escalate to `fluent-manual-researcher` when meaning/prerequisites/activation cannot be resolved safely.

## Stage and prove the parent

When the exact parent is not local, stage the complete paired case/data through the execution plan, normally using the verified OneDrive artifact layer.

Prove identity with manifest/hash when available; otherwise use the strongest direct provenance/readback evidence. Matching filenames are not proof.

## Establish and verify the run filesystem

Before any solve:

1. create declared run/report/log/checkpoint/staging directories;
2. verify destinations are writable and do not unintentionally overwrite another run;
3. inspect inherited file-backed reports/monitors/autosaves/exports/transcripts;
4. resolve every important destination against canonical `run-paths.yaml`;
5. rewrite only file destinations where needed, preserving scientific definitions;
6. deliberately establish the Fluent working directory when relative filenames are unavoidable;
7. read back important destinations;
8. reconcile/update the same canonical `run-paths.yaml`.

A bare filename is not an adequate scientific artifact path unless its containing directory has been deliberately fixed and recorded.

## Prove the case before any planned run

Do not spend compute on a case that exists only in memory.

Before the discovery run or long hypothesis launch:

1. read back every intended critical setup state and declared invariant;
2. save the prepared paired case/data to declared paths;
3. reopen the saved pair from those exact paths;
4. reacquire affected Settings objects;
5. repeat the critical audit;
6. run the planned smoke test, normally about 50 iterations for iteration-based work;
7. prove that required file-backed instrumentation actually writes to the declared destinations during smoke.

Initialization is required only when the setup says so.

A readback mismatch, missing required output, or save/reopen mismatch is a blocker. Do not proceed because the GUI/API call appeared to succeed.

## Instrumentation is a hard pre-run requirement

Compare the actual case against the experiment's evidence contract before the main solve.

Every history/monitor/report that cannot be reconstructed later and is required for a gate or core figure must already exist and must write during smoke.

This includes required residual/equation histories when numerical credibility is part of the hypothesis claim.

Do not knowingly launch a qualification run with “we will see if we can recover the residuals later.” If the required evidence channel cannot be made durable, return the setup for redesign or an explicit pre-run change to the claim/evidence contract.

## Discovery execution — remain attached

Once implementation proof passes and discovery execution is authorized, run the fixed short horizon synchronously through Python/PyFluent.

The scientific goal must remain attached until terminal execution evidence returns.

Do not:

- launch the detached hypothesis worker;
- end/pause the goal because Fluent is still calculating;
- require a human message to resume;
- interpret an RPC/tool timeout as run completion/failure without reconciling the live manifest/session.

If the call times out while Fluent is still advancing, inspect the operational manifest/live iteration state and continue waiting/polling in the same goal.

After terminal discovery execution:

- verify requested horizon reached;
- verify final paired case/data;
- verify required histories;
- return execution facts to the scientific loop;
- let `verify-phase-transition` decide `DISCOVERY_EXECUTION`.

This skill does not itself mark discovery evidence as scientifically sufficient.

## Hypothesis qualification — prove readiness before launch

For hypothesis-test mode, first verify that the setup is genuinely qualification-scale.

For ordinary steady iteration-based full-geometry work, reject a planned horizon below 10,000 iterations unless the setup records an explicit human-approved exception or scientifically equivalent non-iteration qualification basis.

Verify any planned continuation/restart qualification for steady/stationary claims.

Then return the implementation evidence needed for `verify-phase-transition` to judge `HYPOTHESIS_RUN_READY`, including:

- exact parent/setup identity;
- readback audit;
- save/reopen audit;
- smoke result;
- required instrumentation proof;
- selected horizon and qualification basis;
- exact final/checkpoint/report paths;
- runtime-specific wake/completion contract.

Do **not** launch the long solve until `HYPOTHESIS_RUN_READY == PASS` appears in `phase-state.yaml`.

## Run the approved hypothesis horizon

After readiness passes, call `supervise-fluent-run`.

On **Codex**, launch only through the self-waking run-and-handoff entrypoint. Do not background-launch the raw runner.

The Codex job must capture the exact originating `CODEX_THREAD_ID`, trigger on both `COMPLETE` and `BLOCKED`, and have deterministic completion verification. Never use `--last` for multi-job autonomous work.

On **Cursor/runtime without session resume**, keep the agent attached through the full approved horizon instead.

Do not stop early because residuals, balances, routing, or physical monitors look poor while Fluent can still execute the approved experiment. Those behaviours are scientific evidence.

## Completion is execution proof, not scientific proof

Do not claim completion because a command was submitted, a process exited zero, or enough wall time passed.

For an iteration-based run require independent evidence that the intended final saved data belongs to the intended run and reached the requested iteration count.

Also reconcile all required outputs against `run-paths.yaml`.

If the run stops before target, report final observed progress and failure truthfully.

For a hypothesis run, terminal execution `COMPLETE` means only that execution completed and the declared completion verifier passed. It does **not** mean the hypothesis or phase passed. The resumed scientific loop must next run `HYPOTHESIS_EXECUTION` and `HYPOTHESIS_EVIDENCE` verification.

## Preserve important artifacts beyond the server

For scientifically important final states, likely future parents, or deliberately selected expensive recovery checkpoints, preserve complete paired case/data and promote them to the approved OneDrive location when practical.

Do not upload every autosave. Preserve only final/selected recovery states whose loss would materially cost future work.

Record artifact ID, source setup/run, progress, filenames, origin `server.ref`, hashes when feasible, and durability status in the canonical `run-paths.yaml`.

If promotion fails, preserve the local pair and record `LOCAL_ONLY` rather than pretending durability.

## Handoff

Return execution facts only:

- lifecycle mode and prerequisite gate status;
- parent staging/identity proof;
- canonical `run-paths.yaml`;
- working/output path proof;
- setup readback proof;
- save/reopen proof;
- instrumentation proof;
- smoke result;
- requested horizon and actual terminal progress;
- runtime/server/runner;
- final case/data and required history locations;
- Codex handoff status for detached hypothesis work or attached-session completion otherwise;
- durability status;
- implementation/path/execution deviations or blockers.

Scientific interpretation belongs downstream.
