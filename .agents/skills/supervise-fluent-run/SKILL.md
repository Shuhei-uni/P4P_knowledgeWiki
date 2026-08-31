---
name: supervise-fluent-run
description: "Launch and supervise an approved long hypothesis-qualification Fluent calculation only after HYPOTHESIS_RUN_READY passes. On Codex, use a detached worker that deterministically verifies completion and resumes the exact originating scientific goal; on runtimes without session resume, stay attached."
---

# Supervise Fluent Run

This skill is only for long **hypothesis qualification** runs.

Discovery stays attached and must never use this detached path merely to avoid waiting.

## Hard launch preconditions

Before launch, read the phase-root `phase-state.yaml` and require:

```text
DISCOVERY_EVIDENCE == PASS
HYPOTHESIS_DEFINITION == PASS
HYPOTHESIS_RUN_READY == PASS
no unresolved HUMAN_REQUIRED lock
```

Also require the approved setup/run contract to contain:

- experiment/setup/run identity;
- exact runtime `server.ref` and parent/child identity;
- canonical `run-paths.yaml`;
- exact Python/PyFluent runner and working directory;
- initialization intent;
- approved qualification horizon/window;
- required final case/data;
- required report/monitor/residual/checkpoint outputs;
- deterministic terminal completion proof;
- OneDrive durability intent when applicable.

Do not launch a run merely because `mode: hypothesis-test` appears in YAML.

For ordinary steady iteration-based full-geometry qualification, reject a horizon below **10,000 iterations** unless the setup records an explicit human-approved exception or a scientifically equivalent non-iteration qualification basis.

When the hypothesis claim depends on stationarity/steady/bounded behaviour, require the approved continuation/restart qualification component when the setup says it is necessary.

## Runtime architecture

### Codex

```text
verified hypothesis case
→ exact CODEX_THREAD_ID
→ run_and_handoff.py
→ detached Python/PyFluent worker
→ full approved horizon
→ deterministic terminal verification
→ COMPLETE | BLOCKED manifest
→ resume exact originating scientific goal thread
→ read phase-state.yaml
→ verify HYPOTHESIS_EXECUTION
→ analyse/verify HYPOTHESIS_EVIDENCE
```

Do not keep the Codex scientific agent awake for hours just to watch a long qualification solve. The worker waits; the scientific goal owns decisions before and after.

### Cursor / runtime without session resume

```text
verified hypothesis case
→ keep scientific agent attached
→ Python/PyFluent run full horizon
→ deterministic terminal verification
→ continue analysis in same session
```

Do not call `codex exec resume` outside Codex.

## Build the run-and-handoff job

On Codex, use:

```text
PyAnsys/scripts/orchestration/run_and_handoff.py
```

with reusable implementation:

```text
PyAnsys/src/pyansys_fluent/run_handoff.py
```

The derived job spec must define at least:

```yaml
job:
  id: ...
  mode: hypothesis-test
  manifest: ...

runner:
  command: [...]
  cwd: ...
  log: ...

completion:
  required_files: [...]
  verifier_command: [...]  # when needed

codex:
  trigger_on: [COMPLETE, BLOCKED]
```

Use argv lists, not shell strings.

A zero runner exit code is never sufficient completion proof.

## Codex self-wake is mandatory

Every Codex detached hypothesis job must capture the exact originating thread.

Prefer `CODEX_THREAD_ID`; an explicit `codex.session_id` is only an override.

Do not launch if:

- no exact originating thread can be resolved;
- wakeup is disabled;
- either `COMPLETE` or `BLOCKED` is absent from triggers;
- deterministic completion proof is absent.

Never use `codex exec resume --last` for autonomous multi-job work.

The worker's terminal sequence must be:

1. persist `RUNNING`;
2. run the approved Python/PyFluent runner synchronously;
3. capture logs/return code;
4. enter `VERIFYING`;
5. verify required files and/or run the deterministic verifier;
6. persist terminal `COMPLETE` or `BLOCKED` **before** AI handoff;
7. as the final action, launch `codex exec resume <EXACT_THREAD_ID> <prompt>`.

The wake prompt must tell the resumed thread to:

```text
read the terminal manifest
read the phase-root phase-state.yaml
verify experiment identity and approved horizon
run verify-phase-transition for HYPOTHESIS_EXECUTION
produce required post-processing/core figures
run verify-phase-transition for HYPOTHESIS_EVIDENCE
continue the same scientific-phase-loop automatically
```

Do not wake with a vague “simulation finished” prompt that leaves the next lifecycle step optional.

A completed simulation remains `COMPLETE` if the handoff executable itself fails after terminal evidence was safely persisted. Record handoff failure separately and do not rerun CFD merely because the wake hook failed.

## Completion verifier must prove the approved qualification actually happened

The terminal completion proof should verify as much as can be checked deterministically before waking the scientist:

- final case/data exist and are non-trivial;
- saved data belongs to the intended run;
- requested iteration/time horizon was reached;
- required monitor/report/history files exist at declared paths;
- required checkpoint/continuation endpoint exists when part of the contract;
- output identity/path map is consistent with `run-paths.yaml`.

If the required residual/history file is known to be mandatory and absent, terminal verification should not report a clean scientific-ready completion. Record the deficiency so the resumed evidence gate can return `BLOCK` rather than discovering silently missing data later.

## Duplicate-run safeguard

Refuse to launch when the same job manifest already exists until previous state is reconciled.

Determine whether the prior job is still running, complete, blocked, or uncertain before any forced rerun. This prevents self-wake/context loss from duplicating expensive work.

## Scientific behaviour is not an execution stop rule

While Fluent can continue, these are normally evidence rather than execution blockers:

- poor/noisy/oscillatory residuals;
- poor balances;
- unexpected routing or inventory behaviour;
- scientifically unpromising trends.

Attempt the full approved horizon unless the experiment contract contains another deterministic stop condition.

Real execution blockers include initialization failure, FPE/fatal error, process crash, failure to reach approved horizon, missing required final files, failed deterministic verifier, or severe run identity uncertainty.

On Codex, a blocked worker must still persist the blocker and wake the exact scientific thread.

## Recovery and durability

Routine autosaves may remain server-local. Preserve selected expensive checkpoints and important final paired case/data according to canonical `run-paths.yaml` and the OneDrive durability plan.

Do not automatically redesign or restart from a checkpoint inside the worker. Wake the scientific loop with the evidence and let it decide.

## Terminal manifest

Record at minimum:

```text
job_id
phase_id
setup_id/run_id
mode: hypothesis-test
approved qualification horizon
originating Codex thread ID when applicable
status: COMPLETE | BLOCKED
worker pid
runner command/cwd/log/return code
start/finish timestamps
final observed progress
required-file checks
verifier command/result/log
Codex handoff required/enabled/status/pid/log when applicable
runtime: Codex | Cursor | other
```

The generated worker manifest is operational evidence. It does not replace the Project experiment packet or `phase-state.yaml`.

## Handoff meaning

`COMPLETE` means the approved execution and deterministic terminal checks completed.

It does **not** mean:

- the hypothesis is supported;
- the required scientific evidence is complete;
- numerical credibility is established;
- the phase may conclude.

Those require the resumed scientific loop to pass `HYPOTHESIS_EXECUTION`, then `HYPOTHESIS_EVIDENCE`, then eventually `PHASE_CLOSURE`.
