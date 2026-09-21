# Phase context schema

Use this branch when creating or materially revising an active phase
`CONTEXT.md`. Keep it a current decision record, not a transcript or run diary.

## Minimum structure

Use headings that make the current frontier searchable:

```md
# Phase Context — <phase>

## Status
<current frontier and one-sentence decision>

## Evidence anchors
<observed Project evidence, reusable reported evidence, inferences,
assumptions, and genuinely missing facts>

## Phase contract
<question; in/out-of-scope; invariants; claim limit; useful evidence standard>

## Candidate experiment families
<mechanism, controlled delta, screening question, required evidence,
rejection/selection signal>

## Decision conditions
<evidence required, interpretation condition, allowed next in-scope route,
and what the screen does not establish>
```

Link evidence anchors to their owning Project or CFD-wiki source. Mark direct
simulation observations separately from reported literature, inference, and
assumption. State candidate families as contrasts: each needs a controlled delta,
frozen context, observation that matters, and evidence needed to see it.

## Keep execution detail at the right layer

`CONTEXT.md` carries scientific authority and the comparison logic. A selected
experiment's `setup.md` carries its parent, run plan, instrumentation, and
core-figure contract. `run-paths.yaml` and manifests carry placement and machine
paths. Link across those layers instead of restating mutable paths or a history
of every attempt in the context record.

When a direction is superseded, replace the active wording and rely on Git for
chronology. Keep only retained evidence and an explicit reason where an old
candidate still constrains the current phase.
