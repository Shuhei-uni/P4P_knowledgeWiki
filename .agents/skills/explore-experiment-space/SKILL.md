---
name: explore-experiment-space
description: "Organize human-approved CONTEXT.md candidate experiments into a small, contrastive discovery screen. Use inside an active phase only after candidates and a decision gate are approved; do not originate or promote new candidates."
---

# Explore Experiment Space

Turn an approved candidate pool into the smallest contrastive discovery screen
that can answer its declared decision gate. The phase `CONTEXT.md` owns
candidate origin, approval, and the allowed next paths; this skill owns a clear
comparison plan.

## Require an approved context campaign

Read the phase-root `CONTEXT.md`. Require every proposed screen to have a
candidate ID, origin, `approved` status, controlled delta, invariants, required
evidence, and a shared decision gate. Return to `phase-grill` when a missing
candidate or gate would need a new human decision.

Check each approved candidate against prior Project work. Classify its delta as
`NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`. A redundant candidate
does not license a substitute candidate; return it to the human.

## Build the screen

Use the fewest approved cases that genuinely distinguish the gate's stated
alternatives. Preserve a reference where the gate needs one, change as little
as practical within each comparison, and state why each approved case is
necessary. Do not add cases for arbitrary breadth or idle compute capacity.

For each screen record:

| Field | Required content |
| --- | --- |
| Context candidate ID | Human-approved candidate being screened |
| Parent/reference | Exact comparison anchor |
| Delta and invariants | What changes and what remains fixed |
| Short horizon | Enough to answer the screen question, not a qualification claim |
| Evidence | Histories, balances, fields, or comparisons required by the gate |
| Rejection signal | Artifact or outcome that rules the candidate out |

## Design evidence before compute

Define the small core figure set and instrumentation that the declared gate
needs. Prefer histories and comparable metrics over endpoint snapshots. State
units, sign conventions, phase/zone/surface scope, comparison window, and data
source. Preserve noise, drift, or instability rather than smoothing away the
screen's signal.

Discovery evidence may screen candidates and trigger a named conditional path;
it may not establish the long-run claim by itself.

## Output

Return the approved context candidate IDs, screening table, declared gate,
required evidence/core figures, and each case's short horizon. After execution,
classify only the gate-authorized next action. When evidence suggests an
unlisted direction, return `HUMAN_REQUIRED` rather than proposing another case.
