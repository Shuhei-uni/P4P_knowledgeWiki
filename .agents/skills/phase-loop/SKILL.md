---
name: phase-loop
description: "Execute a declared CFD setup queue faithfully through verified run, analysis, and lifecycle gates. Recover blockers autonomously; do not silently replace the phase question."
---

# Phase Loop

Execute the defined setups. Think hard about their evidence, figures, and
diagnostics, but do not turn that thinking into a new scientific case.

Read [autonomous recovery](../references/autonomous-recovery.md) whenever a
gate, setup, run, evidence stream, or Fluent configuration blocks progress.

## Enter only with a defined queue

Start after the planner's **❗❗❗ Phase Loop - launch decision** or from a direct
human invocation. Read the phase `CONTEXT.md`, `phase-state.yaml`, each queued
`setup.md`, and [the loop autonomy check-in](../references/loop-autonomy.md).

The queue must name, in order, every setup path and its lifecycle role
(`discovery` or `hypothesis-test`). Persist that queue in `phase-state.yaml`.
For each item retain the context/setup ID, parent identity, required horizon,
evidence contract, and gate linkage. A setup not in that queue is not work for
this loop.

Before compute, run the autonomy check-in. If the human selects Auto Loop at
queue completion, collect and persist the Auto Loop profile now. The same
Fluent authority applies to that continuous goal, so the later handoff is not
blocked by another question.

## Authority boundary

Phase Loop may:

- execute queued setups through `implement-experiment`;
- inspect and preserve exact parents, configure planned outputs, analyse
  required figures/histories, and evaluate lifecycle gates;
- use the Fluent-session authority recorded at entry; and
- make a technical implementation workaround only when it demonstrably
  preserves the setup's scientific purpose, controlled delta, invariants,
  evidence contract, and horizon.

Phase Loop follows the declared queue first. When a queued setup is blocked, it
may autonomously add the leanest recovery child or related diagnostic family
that preserves the phase question and records its provenance, rationale,
controlled delta, evidence contract, and claim limit. Use
`design-experiment` / `create-setup` for that recovery work; do not fabricate
an unrelated case or silently alter a durable parent.

## Make every setup earn completion

For each queued setup, in order:

1. Call `verify-phase-transition` for the prerequisite transition.
2. Use `fluent-fleet-orchestration` and `implement-experiment` to build and
   prove the exact queued case.
3. Keep discovery attached through terminal evidence. For qualification use
   `supervise-fluent-run` only after `HYPOTHESIS_RUN_READY == PASS`.
4. Produce the setup's planned numerical and scientific analysis, including
   its core figures. Use `interpret-experiment` to write/update the plot-led
   `results.md`: it must answer the experiment question, embed and explain the
   selected figures, preserve limitations, and keep raw artifact paths compact.
5. Call the execution and evidence gates that apply to the setup's lifecycle
   role. A `BLOCK` invokes autonomous recovery, not a human handoff. Persist
   the evidence, recovery decision, and queue item status.

Use only these queue states:

- `COMPLETE_VERIFIED` — the requested horizon was actually reached, required
  final artifacts/histories exist, terminal verification passed, and the
  relevant execution/evidence gates passed. Its `results.md` is a curated,
  plot-led scientific record rather than a pointer list.
- `BLOCKED_VERIFIED` — a real, evidenced execution or evidence blocker exists.
- `BLOCKED_AUTONOMOUS` — recovery was evidenced and recorded; continue other
  useful lanes while a further recovery child is prepared or awaits resources.
- `ATTEMPTED_UNVERIFIED` — launch, a tool return, or partial output exists but
  terminal proof is absent.
- `NOT_RUN` — work has not started.

Only `COMPLETE_VERIFIED` or a durably recorded `BLOCKED_VERIFIED` after its
recovery path is exhausted satisfies queue disposition. A submitted job,
process exit, worker wakeup, or interesting partial plot is never completion.
A run whose report, required figures, or evidence explanation is incomplete
remains blocked from this state even when its solver execution completed; repair
or reconstruct the evidence autonomously.

## Finish the queue deliberately

After every required item is `COMPLETE_VERIFIED` or `BLOCKED_VERIFIED`, follow the completion route
recorded at entry. Run `check-phase-closure` before a human-return route when
the completed queue is intended to close the phase; an Auto Loop route instead
continues the verified phase inside its already-recorded exploration envelope:

- **Return route** — persist the evidence-backed state; do not pause the
  active autonomous goal for a human reply.
- **Auto Loop** — enter `auto-loop` in the same goal with the persisted Auto
  Loop profile and Fluent authority. Do not ask the profile questions again.

If a required item is `ATTEMPTED_UNVERIFIED` or `NOT_RUN`, start/continue its
autonomous recovery family. Continue independent queue items and do not enter
Auto Loop until the original/recovery route has produced verified evidence or a
durable `BLOCKED_VERIFIED` record, or the loop timebox ends.

## Completion condition

The goal is complete only after the declared queue/recovery routes reach their
recorded completion route or the loop timebox expires with durable autonomous
block records. Do not end merely because a runner was launched or because one
setup produced a result.
