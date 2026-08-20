---
name: fluent-run-orchestration
description: "Use when planning or executing Fluent simulations after the case is built. Selects between direct TUI, Fluent journal batching, and agent-owned Python orchestration, with recovery and supervisor handoff requirements."
---

# Fluent Run Orchestration

Use this skill after the Fluent setup is built and verified.

Choose the **simplest execution mode that gives the experiment the control it actually needs**.

```text
single uninterrupted case
    -> direct TUI

multiple fixed/independent cases
    -> Fluent journal

next action depends on intermediate results
    -> agent-owned Python orchestration
```

## 1. Direct TUI run

Use one direct Fluent/TUI solve command when:

- one prepared case is being run;
- no setting change is required during the calculation;
- no intermediate result changes what happens next.

Before submitting the solve command, configure the required initialization, monitors, autosave/checkpoints, and output path.

Do not build an orchestration framework around a single uninterrupted run.

**Example:** load a verified case, initialize it, configure autosave every 500 iterations, then issue one `solve/iterate 3000` command.

## 2. Fluent journal batch

Use a Fluent journal when several cases or fixed stages can execute without an agent making decisions between them.

Typical uses:

- pressure or parameter sweeps of already-built sibling cases;
- multiple cases that each follow `load -> initialize -> run -> save`;
- a fixed sequence where later actions do not depend on intermediate results.

A robust journal should use:

- explicit full paths;
- deterministic load/initialize/run/save steps;
- unique output names;
- required autosave/recovery points;
- transcript/logging where useful;
- no assumptions about interactive working directories or previous Fluent state.

Prefer one journal over keeping an agent attached merely to submit the next independent case.

**Example:** nine prepared outlet-pressure cases are each loaded, initialized, run for the same iteration count, and saved by one Fluent journal.

## 3. Agent-owned Python orchestration

Use Python when the **next Fluent action depends on evidence produced during the run**.

Typical uses:

- staged solver ramping;
- changing numerical controls after a checkpoint;
- convergence or physics gates;
- conditional continuation or termination;
- adaptive experiments;
- recovery logic that must inspect Fluent state before deciding what happens next.

The script should behave as a recoverable state machine:

```text
run block
-> inspect evidence
-> record/checkpoint state
-> decide
-> mutate if required
-> continue
```

Do not use a blind fine-grained iteration loop when a larger decision block is sufficient.

After connection or transport uncertainty, reconnect to the same Fluent process and establish the actual stage/iteration state before issuing another solve command. Never silently repeat a block whose completion is uncertain.

**Example:** run 750 iterations, inspect residual and flux criteria, either change the solver state or remain at the current state, save the transition checkpoint, then run the next block.

## Recovery and evidence

For every run mode:

1. identify the exact input case;
2. define initialization explicitly;
3. define monitors and required result evidence before solving;
4. define autosave/checkpoint behavior appropriate to the run;
5. use unique run/output names;
6. distinguish Fluent numerical failure from client/gRPC/transport failure;
7. preserve enough evidence to establish what actually ran and how far it progressed.

Do not use `server_id` as case identity.

Keep generated evidence compact. Retain what supports recovery, analysis, plots, or result reporting; remove redundant temporary output when it is no longer needed.

## Python supervisor handoff

Whenever an agent creates an agent-owned Python run, it must also provide an overseeing-agent handoff containing:

- the exact launch command;
- the intended case and run/stage sequence;
- what files, monitors, or logs to watch;
- where checkpoints and authoritative run state live;
- how to identify the current stage;
- stop and completion conditions;
- expected failure states;
- how to reconnect and reconcile uncertain progress;
- how to stop safely;
- how to resume safely without repeating completed work.

The supervising agent should not need to reverse-engineer the run script to operate it.

## Selection rule

If two modes would both work, choose the simpler one:

- TUI before journal for one straightforward case;
- journal before Python for fixed independent batches;
- Python only when decisions or mutations genuinely depend on intermediate run evidence.
