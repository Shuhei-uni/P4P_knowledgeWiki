# Phase 1 — Interpretation

## Why this phase existed

Phase 1 was exploratory model development. At this point the project had limited understanding of both Fluent and the separator, so the main objective was to move away from a homogeneous inlet representation and build a workable two-phase inlet for the simplified Purnanto separator.

The physical idea was that the real spiral inlet already promotes liquid toward the outer wall, and the separator continues that centrifugal separation. A two-phase inlet was therefore treated as a more useful starting point than a single homogeneous mixture.

This interpretation is partly retrospective. Several early inlet variants also came from setup mistakes and trial-and-error while learning Fluent, so the phase should not be rewritten as a perfectly planned sensitivity campaign.

## Main hypothesis

A two-phase inlet should better reproduce the incoming steam-water structure and give a more useful separator flow field than the earlier homogeneous representation.

A secondary exploratory question was whether initializing a lower liquid pool could reproduce the retained brine seen in a real separator.

## What was run

| Run / family | Main change | What it was trying to learn | High-level outcome |
| --- | --- | --- | --- |
| 00 / 00a | reference setup and live audit | establish the Purnanto/reference lineage | setup authority, not a final result |
| 02b | transient VOF split inlet | test a sharper two-phase representation | rejected qualitative diagnostic |
| 03 | mixed wet-half velocity inlet | introduce an explicit wet outer inlet region | useful inlet experiment, non-converged |
| 03a | same inlet plus initialized lower water pool | test whether a brine-like retained inventory could be established | pool redistributed/drained; flow became more plausible only after long development |
| 04 | measured actual inlet area | improve inlet representation and inspect DPM/flux response | low-confidence flux/DPM diagnostic |
| 07 | pure-phase actual-area variant | another inlet representation check | non-converged diagnostic |

## Representative evidence

The 03a setup records why the pool test was attempted: the parent had about 109.8 kg/s liquid entering but only about 8.22 kg/s of reported liquid leaving through the named outlets, leaving a very large apparent liquid imbalance. The lower pool was patched to liquid volume fraction 1.0 as a diagnostic.

After roughly 3500 iterations, the 03a notes describe a much more developed swirling field than at low iteration count, but the residuals were still moving and the phase fluxes were physically inconsistent. This is useful evidence that the early cases needed much longer development than the first short tests suggested, but it is not a valid operating point.

Setup 04 reported 115.52 kg/s liquid inlet and only 2.50 kg/s liquid outlet, with a large retained-liquid problem. Its DPM tracks also remained dominated by incomplete trajectories.

## Interpretation

The main useful outcome of Phase 1 was not a validated separator prediction. It was the establishment of the two-phase inlet direction and the first recognition that initial liquid distribution alone does not solve the global liquid-balance problem.

At the time, rapid loss or redistribution of a patched pool was interpreted mainly as a consequence of a very turbulent separator field. Later work in Phases 5 and 6 suggests that this explanation was incomplete: the lower liquid state is also strongly controlled by how the brine outlet and downstream hydraulics are represented.

The early pool experiment is therefore best read as: patching liquid can create an initial condition, but it does not define the operating state.

## Why this led to Phase 2

The next requirement was a cleaner, reproducible baseline that kept the Purnanto geometry/model lineage but used the selected two-phase inlet. This became the 08b parity direction.

## Evidence gaps / TODO

- TODO: recover one or two original Phase-1 contour/streamline images that visually show the transition from poorly developed flow to the later 03a swirling field.
- TODO: document the exact inlet-representation mistake(s) that produced some of the early variants, if useful for the final report.
- TODO: do not claim that tetrahedral meshing caused the pool/wall-film behaviour in this phase; that is a later retrospective hypothesis and is not directly proven by Phase-1 evidence.
