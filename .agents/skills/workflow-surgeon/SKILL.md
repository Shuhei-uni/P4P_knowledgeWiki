---
name: workflow-surgeon
description: "Repair concrete P4P agent-workflow friction by deleting, consolidating, or rewriting the smallest responsible instruction surface. Use when the human asks to simplify/refine the workflow or repeated agent behaviour shows a real workflow defect."
---

# Workflow Surgeon

Read `writing-for-agents` first. Treat agent instructions as executable
interfaces, not documentation to preserve for its own sake.

## Diagnose the failure

State:

- expected behaviour;
- observed behaviour;
- the smallest instruction surface that could have caused it;
- whether the problem is wording, invocation, duplication, ownership, or a
  missing/incorrect completion criterion.

Read only that path plus directly competing instructions.

## Prefer subtraction

Use this order:

1. delete stale/no-op/duplicated instruction;
2. sharpen a pointer or completion criterion;
3. move branch-only detail behind a reference;
4. merge overlapping skills into one owning workflow;
5. add a new skill only for a genuinely distinct invocation boundary.

A separate `SKILL.md` is expensive because its description becomes another
always-loaded trigger. Do not create one for an internal step.

## Human-gate test

Treat "stop and ask the human" as a design smell unless the human actually owns
the missing decision.

Before keeping a human gate, ask:

- Can the fact be inspected, researched, or tested?
- Can the failure be repaired or bounded inside the current phase?
- Is the choice already covered by the recorded scope/authority?
- Would the human be deciding scientific direction/preferences, or merely
  approving routine execution?

Keep human input for scope/goal changes, genuinely human preferences/judgement,
and unauthorized irreversible external actions. Recover ordinary technical
blockers autonomously.

## Preserve useful invariants

Do not weaken:

- evidence provenance;
- exact parent/setup identity;
- pre-run evidence contracts for consequential claims;
- separation of implementation failure from scientific falsification;
- bounded phase scope;
- deterministic proof of completed runs.

Everything else is eligible for simplification when it improves behaviour.

## Verify the surgery

After editing:

- search active instructions for contradictory or stale skill references;
- confirm each remaining skill has a distinct invocation reason;
- confirm branch detail lives under the owning workflow;
- check that the change reduces context/process load rather than moving it;
- run the smallest static or workflow check available.

Return only the observed friction, root cause, files changed, and the behavioural
difference.
