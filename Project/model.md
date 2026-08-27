# Model

This page records stable project assumptions and model boundaries. It is not a Fluent settings dump. Exact setup values belong to the linked setup reports and their machine-readable evidence. If this model is later split into `Project/model/current-model.md`, that page must remain a compact, stable assumptions record rather than becoming a copied Fluent transcript or run dump.

## Stable current assumptions

- **Separator context:** the research concerns a vertical BOC separator, with the current inlet-regime question attached to the spiral-inlet branch. Geometry identity must come from an explicit mesh/case record; a setup number or inlet naming alone is not sufficient (`Inferred`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)).
- **Reference carrier stack:** the audited Purnanto reference uses a steady pressure-based two-phase `Mixture` model, RNG `k-epsilon`, SIMPLE, PRESTO!, second-order momentum/turbulence, QUICK, gravity, operating pressure `0 Pa`, a mass-flow inlet, and pressure outlet(s) (`Observed`, [baseline CFD definition](../ResearchProject_wiki/wiki/model/baseline-cfd.md); live audit [reference](../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)).
- **Reference phase loading:** the live setup audit records approximately `80.69 kg/s` vapour and `116.92 kg/s` liquid, inlet pressure `1,140,000 Pa`, outlet pressure `1,120,000 Pa`, turbulence intensity `2.11%`, and hydraulic diameter `0.724 m` (`Observed`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)). These values are a parity reference, not a claim that every later branch uses the same boundary representation.
- **First deliberate inlet deviation:** the project comparison path uses a split pure-phase inlet concept—liquid on the outer/wall side and steam on the inner/core side—while holding the remaining comparison context fixed as far as the experiment permits (`Assumed`, `Medium Risk`, [inlet-regimes record](../ResearchProject_wiki/wiki/model/inlet-regimes.md)). The exact `27.118 m/s` equal-velocity split and narrow liquid strip are project-derived design inputs, not reported Purnanto values.
- **Simplified-reference boundary:** the Purnanto-derived simplified geometry has no modelled lower liquid-discharge path. Whole-domain liquid or mixture imbalance is therefore not a universal numerical acceptance criterion for that reference branch; liquid/steam outlet behaviour, residual stability, and mesh evidence must be interpreted against the declared geometry and experiment scope (`Inferred`, [baseline CFD definition](../ResearchProject_wiki/wiki/model/baseline-cfd.md)). A full-geometry physical brine-outlet branch is a separate controlled model form and must not be conflated with this simplified-reference rule.

## Current model roles

- **Geometry and mesh:** the 03A full-geometry branch uses the explicitly identified `Full-geomV2-231kcells.msh.h5` mesh with `231,376` cells (`Observed`, [03A setup record](../Setups/full-geometry/mixture/steady-liquid-outlet/03a-08b-parity-full-geometry-baseline.md)). Mesh identity and quality remain setup/report evidence, not assumptions inferred from a setup number.
- **Phases and materials:** the carrier represents primary water vapour and secondary liquid water in a steady Mixture model; energy/phase change is off in the current reference stack. Exact temperature- and pressure-dependent material values belong to the setup authority and live-case readback (`Observed`, [baseline CFD definition](../ResearchProject_wiki/wiki/model/baseline-cfd.md)).
- **Outlet role:** the simplified Purnanto reference has a steam pressure outlet without a modelled lower liquid path; the 03A full-geometry branch deliberately adds a physical brine pressure outlet. Results from those two boundaries cannot be pooled into one balance rule (`Inferred`, [03A setup](../Setups/full-geometry/mixture/steady-liquid-outlet/03a-08b-parity-full-geometry-baseline.md)).
- **DPM role:** DPM is reserved for entrained fine mist, provisionally `5–100 µm`; a separate `100–150 µm` coarse-tail sensitivity may be justified. The size distribution is literature-informed/engineering-assumed rather than a measured geothermal PSD (`Assumed`, [fine-mist decision record](../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md)).
- **Liquid accounting:** in a 5% DPM screening point, the provisional split is `5.846 kg/s` DPM plus `111.074 kg/s` Eulerian liquid. The same liquid mass must not be imposed through both representations (`Assumed`, [fine-mist decision record](../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md); [Skoog guardrails](../ResearchProject_wiki/wiki/model/skoog-application-guardrails.md)).
- **EWF role:** a future three-field branch may separate vapour core, wall film, and dispersed droplets, but Skoog supplies architecture/bookkeeping precedent rather than geothermal default values. Establish the carrier first, allocate liquid explicitly, enable one film mechanism at a time, and keep global DPM source feedback off for the first EWF stability control (`Inferred`, [Skoog guardrails](../ResearchProject_wiki/wiki/model/skoog-application-guardrails.md)).

## Model-development order

1. close setup parity and obtain a stable carrier-field reference;
2. change one inlet representation at a time;
3. verify mesh, residual, phase-flux, pressure, and outlet-carryover evidence;
4. add DPM or higher-realism physics only after the carrier branch earns it;
5. compare against external or analytical anchors before using report-facing validation language.

This ordering is the project-level summary of the [run-efficiency roadmap](../ResearchProject_wiki/wiki/project/roadmap.md), not a replacement for an experiment's exact setup contract.

## Important limits

The model is not considered physically validated because it runs, reaches a high iteration count, or produces a plausible contour. DPM carryover remains a bounded diagnostic when incomplete trajectories or unverified injection assumptions dominate the evidence (`Inferred`, [project validation record](../ResearchProject_wiki/wiki/model/validation.md)).
