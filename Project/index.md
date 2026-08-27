# Project

This is the default entry point for the project's current scientific truth. It is intentionally short: detailed setup lineage remains in `Setups/`, reusable methods remain in `CFD_wiki/`, executable work and machine evidence remain in `PyAnsys/`, and chronological work history remains in Git and the retained compatibility records.

## What are we trying to answer now?

Can a controlled, sufficiently iterated reference case for the vertical BOC separator be established before comparing more realistic two-phase inlet regimes or making report-facing performance claims?

The immediate technical question is whether the extraction-first 08b-parity/full-geometry branch can separate setup-fidelity uncertainty from the intended inlet change while producing interpretable residual, phase-flux, pressure, and liquid-carryover evidence.

## Active/latest experiment

The current execution lane is the canonical full-geometry Mixture `03A` Stage-4 promising-state development campaign:

- [Stage-4 setup contract](../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage4-promising-state-development.md)
- [Stage-4 execution evidence](../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-native-queue-execution-2026-08-23.md)
- [steady Mixture campaign index](../Setups/full-geometry/mixture/steady-liquid-outlet/index.md)

The 03A record remains in the setup/report programme for now. This initial Project layer does not migrate it or create a second copy of its evidence.

## What did the latest experiment show?

Stage 4 produced completed diagnostic continuation evidence for S4-01 and S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and prepared-only evidence for S4-04. The available records do not yet establish physical convergence, a report-ready baseline, or eligibility for a new parent branch.

The broader evidence boundary is unchanged: the documented longer runs are diagnostic, and low-iteration or incomplete runs are setup/debug history. Separator efficiency, liquid carryover, pressure drop, and inlet-regime improvement must not be presented as validated performance until the numerical and comparison gates in [V&V limits](vnv.md) are met.

## What remains unresolved?

- whether any 03A state has stable residuals, phase routing, pressure behaviour, and liquid-inventory behaviour over the required continuation window;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a validation claim;
- whether later DPM evidence is complete enough to support more than a bounded carryover diagnostic.

## What happens next?

Review the active setup/report evidence, promote only a state that passes its readback and physical-history checks, then record the next selected experiment with the [setup/results contract](experiments/README.md). Keep each new experiment to a concise delta from a verified parent and make its evidence and interpretation explicit.

## Relevant files

- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [current setup/report programme](../Setups/full-geometry/mixture/steady-liquid-outlet/index.md)
- [current project roadmap](../ResearchProject_wiki/wiki/project/roadmap.md)
