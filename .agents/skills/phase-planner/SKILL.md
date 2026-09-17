---
name: phase-planner
description: "Catch up on current P4P evidence and define or revise the next scientific phase with the human. Human-only."
disable-model-invocation: true
---

# Phase Planner

Plan the scientific **envelope**, not every solver action.

Start at `Project/index.md`, then read the active phase `CONTEXT.md` and only the
latest evidence needed to understand the frontier. Use
[planning reference](references/planning.md) when the direction is unsettled.

## Conversation

Work like a technical teammate:

- reconstruct what is known and what is still uncertain;
- research factual unknowns instead of asking the human to remember them;
- ask the human only for scientific judgement, priorities, or scope choices that
  cannot be inferred from evidence;
- offer a recommendation when the evidence supports one;
- keep implementation detail out of the conversation unless it changes the
  scientific choice.

Do not require the human to approve every experiment. The useful human boundary
is the phase question and its autonomy envelope.

## Record the phase contract

Keep the active phase `CONTEXT.md` compact and current. It should make these
things obvious:

- question / goal;
- why it matters now;
- strongest current evidence;
- important unknowns or assumptions;
- in-scope and out-of-scope changes;
- candidate mechanisms or experiment families worth testing;
- what evidence would be enough for a useful conclusion;
- compute/time boundary and any explicit Fluent authority.

Use `phase-state.yaml` only for machine state and short attempt/status records,
not as a second scientific narrative.

## Handoff

When the human says to execute, hand the recorded phase contract to
`phase-loop`.

The handoff should not contain a long command script. The phase contract is the
authority; `phase-loop` owns bounded experiment selection, recovery, execution,
analysis, and continuation inside that envelope.

Return to planning only when the phase question/scope itself needs to change or
the human explicitly asks to reframe it.
