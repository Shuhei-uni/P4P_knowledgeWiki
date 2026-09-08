# Phase 7b — Full-Geometry Steady Liquid Removal

## Status

**Human-selected direction, revised on 2026-09-08.** Retain the full geometry,
including its lower brine region, and investigate a function-based liquid-only
removal zone. The model must stay steady state. The human explicitly selected
an ideal collector with no requirement to maintain a standing pool.

This is Andy's Phase 7b, separate from
[Shuhei's Phase 7](../phase-07-simplified-purnanto-liquid-removal/index.md),
which retains the simplified, truncated Purnanto direction. The current
planning authority for Phase 7b is
[`CONTEXT.md`](CONTEXT.md). Exact zone, source law, parent, outlet treatment,
screening horizon and acceptance gate remain to be defined; no run is selected.

## Phase question

> Can a function-based ideal liquid collector in a defined lower region of the
> full separator geometry remove separated water and support a balanced,
> numerically stable steady-state solution while preserving useful separation
> behaviour above the collector?

## Evidence and first uncertainty

The [historical closed-bottom sink studies](../parallel-andy-studies/closed-bottom-liquid-sinks.md)
removed liquid but did not establish a stable, balanced carrier solution.
Available liquid in the small removal band limited one stronger-sink case.
These results make liquid transport into the proposed zone an explicit
uncertainty, alongside the removal rate and its effects on the surrounding flow.

The [resolved-outlet studies](../parallel-andy-studies/resolved-brine-outlet.md)
include the transient VOF work that did not sustain balance even at very low
feed. The separate [Phase-06 steady pressure-feedback test](../phase-06-full-geometry-with-brine-pool/stage-06-long-horizon-surrogate-hypothesis/results.md)
also failed to establish its controlled numerical pool state. These are distinct
meshes and model lineages; their settings and endpoints cannot be interchanged.

## Scope and evidence boundary

The collector represents numerical liquid removal. It does not need to predict
a pool surface or physical brine-outlet response. Useful evidence must include
liquid delivery to the collector, integrated removal, phase and total balance,
inventory, steam loss/carryover, pressure/velocity behaviour, and residuals.
Sink accounting must avoid the historical error of counting the source twice.

Success would qualify a computational collection mechanism within its tested
conditions. Physical pool behaviour, drainage hardware and separator-efficiency
validation remain outside this phase's initial claim.

## Next planning step

Define the collector's location and extent and identify the exact full-geometry
reference. Then frame the smallest informative screen of the human's selected
mechanism, with explicit invariants and a decision gate in `CONTEXT.md`.
