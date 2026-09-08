---
name: phase-loop
description: "Execute a declared CFD setup queue faithfully through verified run, analysis, and lifecycle gates. Use after phase-planner has fixed the queue and its completion route; do not invent scientific cases."
---

# Phase Loop

Execute the defined setups. Think hard about their evidence, figures, and
diagnostics, but do not turn that thinking into a new scientific case.

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

Phase Loop does not originate, select, promote, reorder, or broaden cases. A
workaround that cannot prove equivalence is `HUMAN_REQUIRED`, not a replacement
setup. It does not use `design-experiment`, `create-setup`, or an unqueued
candidate to keep servers busy.

## Make every setup earn completion

For each queued setup, in order:

1. Call `verify-phase-transition` for the prerequisite transition.
2. Use `fluent-fleet-orchestration` and `implement-experiment` to build and
   prove the exact queued case.
3. Keep discovery attached through terminal evidence. For qualification use
   `supervise-fluent-run` only after `HYPOTHESIS_RUN_READY == PASS`.
4. Produce the setup's planned numerical and scientific analysis, including
   its core figures. Use `interpret-experiment` to keep observation,
   interpretation, and claim limits separate.
5. Call the execution and evidence gates that apply to the setup's lifecycle
   role. Persist their evidence and the queue item status.

Use only these queue states:

- `COMPLETE_VERIFIED` — the requested horizon was actually reached, required
  final artifacts/histories exist, terminal verification passed, and the
  relevant execution/evidence gates passed.
- `BLOCKED_VERIFIED` — a real, evidenced execution or evidence blocker exists.
- `ATTEMPTED_UNVERIFIED` — launch, a tool return, or partial output exists but
  terminal proof is absent.
- `NOT_RUN` — work has not started.

Only `COMPLETE_VERIFIED` satisfies a required queue item. A submitted job,
process exit, worker wakeup, or interesting partial plot is never completion.

## Finish the queue deliberately

After every required item is `COMPLETE_VERIFIED`, follow the completion route
recorded at entry. Run `check-phase-closure` before a human-return route when
the completed queue is intended to close the phase; an Auto Loop route instead
continues the verified phase inside its already-recorded exploration envelope:

- **Return to human** — report the evidence-backed state and any remaining
  human decision.
- **Auto Loop** — enter `auto-loop` in the same goal with the persisted Auto
  Loop profile and Fluent authority. Do not ask the profile questions again.

If any required item is `BLOCKED_VERIFIED`, `ATTEMPTED_UNVERIFIED`, or
`NOT_RUN`, do not transition into Auto Loop. Persist the exact deficiency and
return to the human.

## Completion condition

The goal is complete only after the declared queue has either reached its
recorded completion route or stopped at a persisted human-owned blocker. Do not
end merely because a runner was launched or because one setup produced a result.
