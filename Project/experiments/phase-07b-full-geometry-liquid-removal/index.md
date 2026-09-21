# Phase 7b — Full-Geometry Steady Liquid Removal

## Status

**Human-selected direction, revised on 2026-09-08.** Retain the full geometry,
including its lower brine region, and investigate a function-based liquid-only
removal zone. The model must stay steady state. The human explicitly selected
an ideal collector with no requirement to maintain a standing pool.

The human approved five cases at `20%, 40%, 60%, 80%, 100%` collector thickness,
each with a maximum of `5,000` steady iterations. DPM and EWF are off; every
case uses the same fresh initialization without a patched standing pool.
The maximum
collector top is the old model cut plane associated with the assumed water-pool
surface, now mapped to `y=+0.020 m` by the [geometry proof](geometry-proof.md).
All five centroid masks were counted through Fluent; the corrected source
implementation and complete recording route have now completed the S20 screen.
The human selected the reference steady Mixture/RNG
physics with Energy off and the full-feed `1600 kJ/kg` condition: liquid
`116.92 kg/s` and vapour `80.69 kg/s`. Retain this mesh's separate liquid and
steam inlet faces, using Shuhei's earlier pure-phase equal-velocity design:
nominally `27.118 m/s` on both faces, with the design's consistent densities
and actual areas checked against the phase-flow targets. Close the physical
brine outlet as a wall; the collector is the intended lower liquid-removal
path. The transient `0.05%` study is historical context, not the
Phase-7b settings parent or development route.

This is Andy's Phase 7b, separate from
[Shuhei's Phase 7](../phase-07a-simplified-purnanto-liquid-removal/index.md),
which retains the simplified, truncated Purnanto direction. The current
planning authority for Phase 7b is
[`CONTEXT.md`](CONTEXT.md). The five-case screen is selected and technical
preparation is authorized. The clean reference, corrected native source syntax,
50-iteration source diagnostic and exact collector-face recorder have passed
bounded checks. All five approved cases now have terminal dispositions:
S20/S40/S60/S80 completed N5000 but failed the numerical indicators; S100
suffered numerical divergence at attempted N4183, with complete records through
N4182 and preserved failed/recovery pairs. The [G1 comparison](results.md)
contains the figures, observations, alternatives and proposed next decision.
No case is qualified. Check-ins stop at G1; no further solve is authorized.

The resolved brine-outlet study's 620,431-cell mesh is staged in the Phase 7b
folder on Extreme SSD with a verified matching SHA-256. Its PC copy is at
`C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal`;
assistant access is through Fluent/PyFluent. API connectivity, directory
write/read access and a source-free compiled diagnostic passed on Fluent
2025 R2. The uninitialized reference preparation case also passed strict
settings checks before save and after same-process reload. The corrected Python-only steady setup has completed S20. See `CONTEXT.md`
for the handoff boundary.

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

## Next decision

Review the [G1 evidence](results.md) and decide whether to authorize a separate
fixed-geometry source-strength diagnostic. The current five-case queue is
exhausted. No source-strength change, numerical tuning, extra iterations or
qualification is automatically authorized.

[Supervisor meeting PDF and figure bundle](meeting-report.md) provide a minimal-text presentation of the G1 evidence.
