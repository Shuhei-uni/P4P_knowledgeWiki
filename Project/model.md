# Model

This page records stable project assumptions and model boundaries. It is not a Fluent settings dump. Exact setup values belong to the linked setup reports and their machine-readable evidence.

## Stable current assumptions

- **Separator context:** the research concerns a vertical BOC separator, with the current inlet-regime question attached to the spiral-inlet branch. Geometry identity must come from an explicit mesh/case record; a setup number or inlet naming alone is not sufficient (`Inferred`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)).
- **Reference carrier stack:** the audited Purnanto reference uses a steady pressure-based two-phase `Mixture` model, RNG `k-epsilon`, SIMPLE, PRESTO!, second-order momentum/turbulence, QUICK, gravity, operating pressure `0 Pa`, a mass-flow inlet, and pressure outlet(s) (`Observed`, [baseline CFD definition](../ResearchProject_wiki/wiki/model/baseline-cfd.md); live audit [reference](../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)).
- **Reference phase loading:** the live setup audit records approximately `80.69 kg/s` vapour and `116.92 kg/s` liquid, inlet pressure `1,140,000 Pa`, outlet pressure `1,120,000 Pa`, turbulence intensity `2.11%`, and hydraulic diameter `0.724 m` (`Observed`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)). These values are a parity reference, not a claim that every later branch uses the same boundary representation.
- **First deliberate inlet deviation:** the project comparison path uses a split pure-phase inlet concept—liquid on the outer/wall side and steam on the inner/core side—while holding the remaining comparison context fixed as far as the experiment permits (`Assumed`, `Medium Risk`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)). The exact `27.118 m/s` equal-velocity split and narrow liquid strip are project-derived design inputs, not reported Purnanto values.
- **Simplified-reference boundary:** the Purnanto-derived simplified geometry has no modelled lower liquid-discharge path. Whole-domain liquid or mixture imbalance is therefore not a universal numerical acceptance criterion for that reference branch; liquid/steam outlet behaviour, residual stability, and mesh evidence must be interpreted against the declared geometry and experiment scope (`Inferred`, [baseline CFD definition](../ResearchProject_wiki/wiki/model/baseline-cfd.md)). A full-geometry physical brine-outlet branch is a separate controlled model form and must not be conflated with this simplified-reference rule.

## Model-development order

1. close setup parity and obtain a stable carrier-field reference;
2. change one inlet representation at a time;
3. verify mesh, residual, phase-flux, pressure, and outlet-carryover evidence;
4. add DPM or higher-realism physics only after the carrier branch earns it;
5. compare against external or analytical anchors before using report-facing validation language.

This ordering is the project-level summary of the [run-efficiency roadmap](../ResearchProject_wiki/wiki/project/roadmap.md), not a replacement for an experiment's exact setup contract.

## Important limits

The model is not considered physically validated because it runs, reaches a high iteration count, or produces a plausible contour. DPM carryover remains a bounded diagnostic when incomplete trajectories or unverified injection assumptions dominate the evidence (`Inferred`, [project validation record](../ResearchProject_wiki/wiki/model/validation.md)).
