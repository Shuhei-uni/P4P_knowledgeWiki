---
name: supervise-fluent-run
description: "Launch and supervise an approved long hypothesis-test Fluent calculation. Use after a hypothesis-test case has been verified and smoke-tested. In Codex, create a detached job that writes a COMPLETE/BLOCKED manifest and resumes the originating Codex thread. In Cursor or any runtime without session-resume, keep the agent attached through the approved horizon unless a detached manifest-only job is explicitly required."
---

# Supervise Fluent Run

This skill is for long **hypothesis-test** runs. Discovery-mode runs stay agent-attached and do not use this detached path.

The long hypothesis solve should outlive the agent turn that launched it **when the runtime can wake that turn later**.

Codex default architecture:

```text
verified case + execution contract
→ capture originating CODEX_THREAD_ID
→ detached Python/PyFluent worker
→ Fluent advances for the approved horizon
→ deterministic completion verification
→ terminal job manifest: COMPLETE | BLOCKED
→ mandatory resume of exact originating Codex thread
→ analyse or diagnose
```

Cursor and other agents with no session-resume hook:

```text
verified case + execution contract
→ keep the scientific agent attached
→ Python/PyFluent run for the approved horizon
→ deterministic completion verification
→ analyse or diagnose in the same session
```

Do **not** keep a Codex scientific agent awake for hours merely to watch a hypothesis-test run iterate. The worker owns waiting; the agent owns decisions before and after the run.

In Cursor, attached waiting is the default hypothesis path. Do not call `codex exec resume`. Launch `run_and_handoff.py` only when the human explicitly wants a detached `COMPLETE`/`BLOCKED` job; missing `CODEX_THREAD_ID` is expected and is not a launch blocker.

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
- OneDrive durability target when applicable.

On Codex, the originating thread/session ID is mandatory for detached hypothesis mode. Prefer automatic capture from `CODEX_THREAD_ID` inherited from the Codex process that launches the job. An explicit `codex.session_id` is only an override when necessary.

On Cursor, do not require `CODEX_THREAD_ID`. Prefer staying attached. If a detached job is explicitly requested, write the terminal manifest and return without a Codex resume.

Do not identify the machine by a short server alias alone. Do not guess output roots. Never use `codex exec resume --last` for autonomous Codex handoff when several jobs may finish independently. Never invoke `codex exec resume` from Cursor.

## Build the run-and-handoff job

Create a derived YAML job specification for the execution worker. It is an operational input, not a second scientific path authority; canonical scientific paths remain in the Project experiment packet.

The job must define:

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
  # and/or verifier_command: [...]

codex:
  trigger_on: [COMPLETE, BLOCKED]
```

On Codex, `codex.enabled` defaults to true and may not be disabled for `hypothesis-test`. `codex.session_id` may be omitted when the job is launched from Codex because the Python loader captures `CODEX_THREAD_ID` automatically.

On Cursor, do not enable the Codex wakeup hook. If a detached job YAML is still required, set the handoff disabled or omit Codex resume rather than inventing a thread id.

Use argv lists, not shell command strings. Do not hide TUI or journal fallbacks inside the worker.

A zero process exit code is never enough by itself. The job must declare at least one completion proof:

- locally visible required files with minimum-size checks; and/or
- a deterministic verifier command that returns zero only after the declared remote final state has been verified.

### Runtime-specific self-wake

On **Codex**, every background hypothesis-test Python entrypoint must finish through the Codex handoff path. The canonical way is to launch `run_and_handoff.py` as the background Python entrypoint; do **not** background-launch the raw experiment runner directly.

The Codex wakeup is a hard workflow requirement, not optional cleanup. The Python worker must attempt it on both `COMPLETE` and `BLOCKED` so the scientific loop continues without the human having to send a later prompt.

Do not start a Codex background hypothesis run if:

- `CODEX_THREAD_ID` cannot be captured and no explicit session override exists;
- the wakeup hook is disabled;
- either `COMPLETE` or `BLOCKED` is missing from the trigger set;
- no deterministic completion proof is available.

Requiring a human to notice that a Codex simulation probably finished and manually restart the thread is a workflow failure.

On **Cursor**, keep the agent attached through the approved horizon. Missing `CODEX_THREAD_ID` is not a blocker. Do not start `run_and_handoff.py` merely to wait, and do not call `codex exec resume`.

## Launch detached

Normal launch:

```text
python PyAnsys/scripts/orchestration/run_and_handoff.py --job <job.yaml>
```

On Codex, the launcher resolves the originating thread before starting the detached worker. The current Codex turn is then free to end while Fluent continues.

The Codex worker itself contains the mandatory terminal Python tail:

1. writes `RUNNING` to the job manifest;
2. executes the approved Python/PyFluent runner synchronously;
3. captures runner output to the declared log;
4. enters `VERIFYING` after the runner returns;
5. checks all required files and/or runs the deterministic verifier;
6. writes terminal `COMPLETE` or `BLOCKED` **before** invoking the AI handoff;
7. **as the final hypothesis-run action, launches `codex exec resume <THREAD_ID> <prompt>`** for the exact originating thread.

The terminal manifest is the execution handoff source of truth. The Codex handoff is separate: a completed simulation remains `COMPLETE` even if the Codex executable itself cannot be launched; the manifest records that handoff failure separately. Do not rerun completed CFD work merely because the hook failed.

Cursor attached hypothesis runs skip this launcher. If Cursor must leave a detached job, stop after the terminal manifest; do not attempt Codex resume.

## Duplicate-run safeguard

The launcher refuses to start when the job manifest already exists.

Do not bypass this casually. First reconcile whether the previous job is still running, completed, blocked, or left uncertain state. Only then may an explicit `--force` rerun be justified.

This prevents a newly awakened agent from blindly repeating an expensive run because it lost conversational context.

## Distinguish evidence from execution failure

The following are normally scientific evidence, not stop conditions:

- poor, noisy, oscillatory, or slowly decaying residuals;
- poor balances or unexpected physical monitors;
- scientifically unpromising behaviour;
- unexpected flow fields or trends.

Unless the experiment contract defines another deterministic stop rule, the runner should attempt the approved fixed horizon while Fluent can continue.

A real execution blocker includes:

- initialization failure;
- Fluent floating-point/fatal error;
- Fluent or Python runner crash;
- the calculation stopping before the approved horizon;
- required final files missing or undersized;
- a deterministic final-state verifier failing;
- output/case identity uncertainty severe enough that completion cannot be proven safely.

A blocked Codex worker should preserve the available execution evidence and still trigger the Codex handoff so the scientific loop can diagnose the failure immediately. A blocked Cursor attached run should return the same execution evidence in the live session.

## Recovery and durability

Routine autosaves may remain local for same-server recovery. Preserve selected expensive checkpoints and important final case+data pairs according to the canonical `run-paths.yaml` and OneDrive durability policy.

The detached wrapper does not itself redesign recovery policy or Fluent numerics. The experiment runner/verifier may use existing deterministic helpers to check or promote artifacts when the approved execution plan requires it.

Do not automatically rerun from a checkpoint after a numerical or setup failure. Wake the scientific agent with the blocker evidence and let the upstream loop decide.

## Completion manifest

The terminal JSON should make the execution state recoverable without the old agent context. At minimum it records:

```text
job_id
mode: hypothesis-test
originating Codex thread id when launched from Codex
status: COMPLETE | BLOCKED
worker pid
runner command/cwd/log/return code
start/finish timestamps
required-file checks
verifier command/result/log when used
Codex handoff required/enabled/status/pid/log when launched from Codex
runtime: Codex | Cursor | other
```

The resumed agent must also read the canonical Project experiment packet and `run-paths.yaml`; the generated worker manifest does not replace them.

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

Do not perform CFD interpretation inside the detached worker. The worker is an execution boundary and hook; the resumed Codex agent or the still-attached Cursor agent does the reasoning.
