# Phase 07 — Simplified Purnanto Liquid-Removal Mechanisms

## Status

**Selected by the human on 2026-09-08; phase direction only.** No particular
liquid-removal method, experiment setup, parent case, or acceptance threshold
has yet been selected.

The current human-approved planning state is maintained in
[`CONTEXT.md`](CONTEXT.md). It must record an approved candidate and decision
gate before an experiment is designed or executed.

## Phase question

> What practical numerical mechanism can remove separated liquid from the
> bottom of the truncated Purnanto separator model while preserving a useful
> and interpretable representation of the separation behaviour?

## Geometry boundary

Phase 07 returns to the simplified Purnanto geometry rather than continuing
with the full separator geometry. The computational geometry will be cut at
the elevation corresponding to the brine-pool surface in the real separator.
That cut plane becomes the bottom boundary of the simplified model, and the
detailed real-separator geometry below the pool surface is excluded.

**Missing Info.** The exact physical elevation of the real brine-pool surface
and its corresponding coordinate in the Purnanto geometry must be established
before building a runnable case.

## Exploration direction

The phase will use human think-aloud and `phase-grill` to identify candidate
ways of removing liquid through or near the bottom of the simplified separator.
Only candidates recorded as approved in `CONTEXT.md` may be tested. Pragmatic
and deliberately “hacky” methods are permitted because the immediate purpose
is mechanism discovery. No candidate is assumed to be physically faithful
merely because it runs or drains liquid.

For every candidate, the project should record:

- the boundary condition, model feature, source/sink treatment, or other
  numerical intervention used;
- the intended liquid-removal mechanism and why it might work;
- whether it also removes steam or otherwise distorts phase routing;
- its effect on liquid inventory, phase-resolved mass balance, separator flow,
  and numerical behaviour;
- known artefacts, failure modes, tuning parameters, and claim limits; and
- the evidence-based decision to retain, revise, or reject it.

## Initial claim boundary

Phase 07 is a modelling-method development phase. Its first useful result may
be a robust numerical workaround rather than a plant-faithful outlet model.
Until separately supported, a successful method may be described only as a
mechanism for removing liquid from the simplified computational separator. It
must not be presented as validation of the real brine-pool interface, outlet
hardware, drainage rate, or level-control response.

## Predecessor decision

- [Phase 06 conclusion](../phase-06-full-geometry-with-brine-pool/conclusion.md)
