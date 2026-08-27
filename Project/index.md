# Project

This is the default entry point for the project's current scientific truth. It is intentionally short: detailed setup lineage remains in `Setups/`, reusable methods remain in `CFD_wiki/`, executable work and machine evidence remain in `PyAnsys/`, and the retained written historical corpus is grouped below without replacing its legacy sources.

## What are we trying to answer now?

Can a controlled, sufficiently iterated reference case for the vertical BOC separator be established before comparing more realistic two-phase inlet regimes or making report-facing performance claims?

The immediate technical question is whether the extraction-first 08b-parity/full-geometry branch can separate setup-fidelity uncertainty from the intended inlet change while producing interpretable residual, phase-flux, pressure, and liquid-carryover evidence.

## Active/latest experiment

The current execution lane is the canonical full-geometry Mixture `03A` Stage-4 promising-state development campaign. Its Project tracer is now the shortest route through the two-stage record:

- [03A tracer index](experiments/03a/index.md)
- [03A-Q01 setup — S4-01 50-iteration qualification](experiments/03a/q01-s4-01-50-iteration-qualification/setup.md)
- [03A-Q01 results — S4-01 50-iteration qualification](experiments/03a/q01-s4-01-50-iteration-qualification/results.md)
- [Stage-4 setup contract](experiments/03a/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/03a/stage-04/results.md)
- [Stage-3 results](experiments/03a/stage-03/results.md)
- [steady Mixture campaign index](../Setups/full-geometry/mixture/steady-liquid-outlet/index.md)

The original 03A setup/report records remain frozen source and provenance records. The tracer does not duplicate their full evidence; it carries only the decision-relevant setup delta, findings, limitations, and handoff.

## What did the latest experiment show?

Stage 4 produced completed diagnostic continuation evidence for S4-01 and S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and prepared-only evidence for S4-04. The selected [03A-Q01 S4-01 qualification](experiments/03a/q01-s4-01-50-iteration-qualification/results.md) then completed exactly 50 native steady iterations from the verified `33,000` parent endpoint, reaching native coordinate `33,050` with a paired endpoint, hashes, scientific readback, residual/transcript evidence, and all 30 configured physical histories. The short window still contains residual excursions and movement in mass imbalance, liquid inventory, and routing; no paired native autosave checkpoint was recovered. The available records do not yet establish physical convergence, a report-ready baseline, or eligibility for a new parent branch.

The broader evidence boundary is unchanged: the documented longer runs are diagnostic, and low-iteration or incomplete runs are setup/debug history. Separator efficiency, liquid carryover, pressure drop, and inlet-regime improvement must not be presented as validated performance until the numerical and comparison gates in [V&V limits](vnv.md) are met.

## Historical written memory

The Project layer now exposes the substantive written experiment record that
was previously scattered across setup, report, observation, meeting, and
technical-note locations. The copies preserve legacy IDs, wording, evidence
status, and uncertainty labels; the original records remain available as
frozen sources, while raw Fluent and machine-generated artifacts stay with
their existing owners.

- [historical experiment corpus](experiments/README.md)
- [cross-experiment observations](observations/index.md)
- [mesh, DPM, and wall-film meeting record](technical/mesh-conversion-dpm-mass-sensitivity-meeting-report.md)
- [spiral-inlet geometry record](technical/purnanto-spiral-inlet-geometry.md)
- [Skoog application guardrails](technical/skoog-application-guardrails.md)
- [mesh-trial technical audit](technical/mesh-trial1-mesh-audit.md)

## What remains unresolved?

- whether any 03A state has stable residuals, phase routing, pressure behaviour, and liquid-inventory behaviour over the required continuation window;
- whether the Q01 short-window residual and physical-history movement can be qualified over a longer explicitly selected continuation, with complete checkpoint evidence;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a validation claim;
- whether later DPM evidence is complete enough to support more than a bounded carryover diagnostic.

## What happens next?

Review the Q01 packet together with the 03A tracer's remaining readback and physical-history gaps. Promote only a state that passes those checks, then record the next explicitly selected experiment with the [setup/results contract](experiments/README.md). Keep each new experiment to a concise delta from a verified parent and make its evidence and interpretation explicit.

## Relevant files

- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [current setup/report programme](../Setups/full-geometry/mixture/steady-liquid-outlet/index.md)
- [current project roadmap](../ResearchProject_wiki/wiki/project/roadmap.md)
