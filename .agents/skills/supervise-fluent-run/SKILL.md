---
name: supervise-fluent-run
description: "Launch and supervise an approved long Fluent calculation without keeping an AI agent alive for the full solve. Use after the case has been verified and smoke-tested to create a detached deterministic run job, verify terminal outputs, write a machine-readable COMPLETE/BLOCKED manifest, and resume the exact Codex session when the run finishes or blocks."
---

# Supervise Fluent Run

The long solve should outlive the agent turn that launched it.

Default architecture:

```text
verified case + execution contract
→ detached Python/PyFluent worker
→ Fluent advances for the approved horizon
→ deterministic completion verification
→ terminal job manifest: COMPLETE | BLOCKED
→ resume exact Codex session
→ analyse or diagnose
```

Do **not** keep the scientific agent awake for hours merely to watch Fluent iterate.
The worker owns waiting; the agent owns decisions before and after the run.

The implementation entrypoint is:

```text
PyAnsys/scripts/orchestration/run_and_handoff.py
```

and the reusable implementation is:

```text
PyAnsys/src/pyansys_fluent/run_handoff.py
```

See `PyAnsys/queues/run-and-handoff.example.yaml` for the job contract shape.

## Receive an execution contract

Before launch, know:

- experiment/setup identity and run ID;
- canonical runtime `server.ref`, separate server ID and IP;
- exact parent/child case identity;
- canonical experiment `run-paths.yaml`;
- exact Python/PyFluent runner command and working directory;
- initialization intent and approved iteration/time horizon;
- expected final case/data paths;
- checkpoint/autosave paths when configured;
- required monitor/report/log outputs;
- any deterministic remote verifier needed when output files are not visible to the worker locally;
- OneDrive durability target when applicable;
- the **explicit Codex session/thread ID** that should receive the completion event.

Do not identify the machine by a short server alias alone. Do not guess output roots.
Do not use `codex exec resume --last` for autonomous handoff when several jobs may
finish independently.

## Build the run-and-handoff job

Create a derived YAML job specification for the execution worker. It is an
operational input, not a second scientific path authority; canonical scientific
paths remain in the Project experiment packet.

The job must define:

```yaml
job:
  id: ...
  manifest: ...

runner:
  command: [...]
  cwd: ...
  log: ...

completion:
  required_files: [...]
  # and/or verifier_command: [...]

codex:
  enabled: true
  session_id: <explicit session id>
  trigger_on: [COMPLETE, BLOCKED]
```

Use argv lists, not shell command strings. Do not hide TUI or journal fallbacks
inside the worker.

A zero process exit code is never enough by itself. The job must declare at
least one completion proof:

- locally visible required files with minimum-size checks; and/or
- a deterministic verifier command that returns zero only after the declared
  remote final state has been verified.

## Launch detached

Normal launch:

```text
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

The launcher starts a detached worker and returns immediately. The current Codex
turn is therefore free to end while Fluent continues.

The worker then:

1. writes `RUNNING` to the job manifest;
2. executes the approved Python/PyFluent runner synchronously;
3. captures runner output to the declared log;
4. enters `VERIFYING` after the runner returns;
5. checks all required files and/or runs the deterministic verifier;
6. writes terminal `COMPLETE` or `BLOCKED` **before** invoking the AI handoff;
7. launches `codex exec resume <SESSION_ID> <prompt>` for the exact recorded
   session when the terminal status matches `codex.trigger_on`.

The terminal manifest is the execution handoff source of truth. The Codex
handoff is secondary: a completed simulation remains `COMPLETE` even if the
Codex executable itself cannot be launched; the manifest records that handoff
failure separately.

## Duplicate-run safeguard

The launcher refuses to start when the job manifest already exists.

Do not bypass this casually. First reconcile whether the previous job is still
running, completed, blocked, or left uncertain state. Only then may an explicit
`--force` rerun be justified.

This prevents a newly awakened agent from blindly repeating a 20k-iteration job
because it lost conversational context.

## Distinguish evidence from execution failure

The following are normally scientific evidence, not stop conditions:

- poor, noisy, oscillatory, or slowly decaying residuals;
- poor balances or unexpected physical monitors;
- scientifically unpromising behaviour;
- unexpected flow fields or trends.

Unless the experiment contract defines another deterministic stop rule, the
runner should attempt the approved fixed horizon while Fluent can continue.

A real execution blocker includes:

- initialization failure;
- Fluent floating-point/fatal error;
- Fluent or Python runner crash;
- the calculation stopping before the approved horizon;
- required final files missing or undersized;
- a deterministic final-state verifier failing;
- output/case identity uncertainty severe enough that completion cannot be
  proven safely.

A blocked worker should preserve the available execution evidence and still
trigger the Codex handoff so the scientific loop can diagnose the failure.

## Recovery and durability

Routine autosaves may remain local for same-server recovery. Preserve selected
expensive checkpoints and important final case+data pairs according to the
canonical `run-paths.yaml` and OneDrive durability policy.

The detached wrapper does not itself redesign recovery policy or Fluent
numerics. The experiment runner/verifier may use existing deterministic helpers
to check or promote artifacts when the approved execution plan requires it.

Do not automatically rerun from a checkpoint after a numerical or setup failure.
Wake the scientific agent with the blocker evidence and let the upstream loop
decide.

## Completion manifest

The terminal JSON should make the execution state recoverable without the old
agent context. At minimum it records:

```text
job_id
status: COMPLETE | BLOCKED
worker pid
runner command/cwd/log/return code
start/finish timestamps
required-file checks
verifier command/result/log when used
Codex handoff enabled/status/pid/log
```

The resumed agent must also read the canonical Project experiment packet and
`run-paths.yaml`; the generated worker manifest does not replace them.

## Handoff behaviour

On `COMPLETE`:

```text
read terminal manifest
→ verify experiment identity/path authority
→ run required post-processing
→ interpret evidence
→ update Project result state
→ choose the next scientific action
```

On `BLOCKED`:

```text
read terminal manifest + runner/verifier logs
→ classify the execution failure
→ preserve/reconcile latest verified state
→ decide recovery, repair, redesign, or human boundary
```

Do not perform CFD interpretation inside the detached worker. The worker is an
execution boundary and hook; the resumed scientific agent does the reasoning.
