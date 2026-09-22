# Phase 4 — Interpretation

## Why this phase existed

Phase 4 introduced Eulerian Wall Film (EWF) because the separator should develop liquid on the outer wall, while the earlier carrier/DPM work did not show a convincing resolved wall-liquid structure.

At the time, one working hypothesis was that wall-film behaviour needed to be represented explicitly in Fluent rather than expecting the Mixture/DPM setup to produce all relevant wall physics by itself.

## Main hypothesis

Explicit EWF physics can capture deposition and transport of liquid on the wall, and submodels such as splash, edge separation, and stripping may change how liquid returns to the bulk flow or DPM population.

## What was run

| Run | Main mechanism |
| --- | --- |
| 010V2 | clean EWF deposition baseline |
| 010V2a | splash |
| 010V2b | edge separation |
| 010V2c | particle stripping |
| 010V2d | combined film mechanisms |
| 010V2d-2 | global DPM interaction with EWF |
| 10a | earlier splash-enabled preliminary branch |

## Representative evidence

The phase did produce measurable film behaviour rather than only a configuration change.

Examples retained in the repo include:

- 010V2a: 12 explicitly reported splash events, four each for the 56.27, 112.54, and 168.81 µm injections;
- 010V2d: film mass 5.66845e-2 kg, maximum film thickness 1.2496e-4 m, area-weighted thickness 9.60e-7 m, and non-zero wall-film velocity components;
- 010V2d-2: area-weighted film thickness 4.60e-6 m.

The records also preserve important limitations: some stripping/transfer quantities could not be read back reliably, interval film histories were incomplete, and the combined continuation developed numerical-quality concerns.

## Interpretation

The useful result of Phase 4 was that EWF could create a finite, inspectable film and expose wall-specific mechanisms that were absent from the earlier bulk+DPM interpretation.

It did not establish that enabling EWF improved separator efficiency. The carrier was still not mass closed, and the film evidence was often based on single checkpoints rather than complete transfer histories.

A later retrospective hypothesis is that the earlier tetrahedral mesh and near-wall resolution were also limiting the wall-film representation. That is plausible and important for current work, but it was not isolated in Phase 4 and should not be written as a proven cause.

## Why this led to Phase 5

By this point the project had added increasingly detailed inlet, DPM, and wall physics, but the continuous liquid still had no credible way to leave the simplified domain. The resulting mass imbalance became more important than adding another local mechanism.

The next step was therefore to introduce the full lower separator geometry and a brine outlet.

## Evidence gaps / TODO

- TODO: recover one representative EWF contour, ideally film thickness or film velocity, for the final report.
- TODO: perform a future mesh/near-wall sensitivity before attributing the early weak film behaviour to tetrahedral meshing.
- TODO: avoid using final film mass alone as evidence of drainage; matched transfer/outflow histories are needed.
