# Model

This page records stable project assumptions and model boundaries. It is not a
Fluent settings dump. Exact setup values belong to the selected experiment
setup and its machine-readable evidence.

## Stable current assumptions

- **Separator context:** the research concerns a vertical BOC separator, with
  the current inlet-regime question attached to the spiral-inlet branch.
  Geometry identity must come from an explicit mesh/case record; a setup number
  or inlet naming alone is not sufficient (Inferred, [inlet-regimes
  interpretation](experiments/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md)).
- **Reference carrier stack:** the audited Purnanto reference uses a steady
  pressure-based two-phase Mixture model, RNG k-epsilon, SIMPLE, PRESTO!,
  second-order momentum/turbulence, QUICK, gravity, operating pressure 0 Pa,
  a mass-flow inlet, and pressure outlet(s) (Observed, [reference
  experiment](experiments/purnanto-00a-live-setup-audit/setup.md); [live
  readback](experiments/purnanto-00a-live-setup-audit/technical-live-setup-reference.md)).
- **Reference phase loading:** the live setup audit records approximately
  80.69 kg/s vapour and 116.92 kg/s liquid, inlet pressure 1,140,000 Pa,
  outlet pressure 1,120,000 Pa, turbulence intensity 2.11%, and hydraulic
  diameter 0.724 m (Observed, [inlet-regimes
  interpretation](experiments/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md)).
  These values are a parity reference, not a claim that every later branch
  uses the same boundary representation.
- **First deliberate inlet deviation:** the project comparison path uses a
  split pure-phase inlet concept—liquid on the outer/wall side and steam on the
  inner/core side—while holding the remaining comparison context fixed as far
  as the experiment permits (Assumed, Medium Risk, [inlet-regimes
  interpretation](experiments/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md)).
  The exact 27.118 m/s equal-velocity split and narrow liquid strip are
  project-derived design inputs, not reported Purnanto values.
- **Simplified-reference boundary:** the Purnanto-derived simplified geometry
  has no modelled lower liquid-discharge path. Whole-domain liquid or mixture
  imbalance is therefore not a universal numerical acceptance criterion for
  that reference branch; outlet behaviour, residual stability, and mesh
  evidence must be interpreted against the declared geometry and experiment
  scope (Inferred). A full-geometry physical brine-outlet branch is a separate
  controlled model form.

## Current model roles

- **Geometry and mesh:** the 03A full-geometry branch uses the explicitly
  identified Full-geomV2-231kcells.msh.h5 mesh with 231,376 cells (Observed,
  [03A setup source](experiments/03a/setup-source.md)). Mesh identity and
  quality remain setup evidence, not assumptions inferred from a setup number.
- **Phases and materials:** the carrier represents primary water vapour and
  secondary liquid water in a steady Mixture model; energy/phase change is off
  in the current reference stack. Exact material values belong to the setup
  authority and live-case readback (Observed, [live setup
  reference](experiments/purnanto-00a-live-setup-audit/technical-live-setup-reference.md)).
- **Outlet role:** the simplified Purnanto reference has a steam pressure
  outlet without a modelled lower liquid path; the 03A full-geometry branch
  deliberately adds a physical brine pressure outlet. Results from those
  boundaries cannot be pooled into one balance rule (Inferred, [03A setup
  source](experiments/03a/setup-source.md)).
- **DPM role:** DPM is reserved for entrained fine mist, provisionally
  5–100 µm; a separate 100–150 µm coarse-tail sensitivity may be justified.
  The distribution is literature-informed/engineering-assumed rather than a
  measured geothermal PSD (Assumed, [fine-mist
  interpretation](experiments/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md)).
- **Liquid accounting:** in a 5% DPM screening point, the provisional split
  is 5.846 kg/s DPM plus 111.074 kg/s Eulerian liquid. The same liquid mass
  must not be imposed through both representations (Assumed, [fine-mist
  interpretation](experiments/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md);
  [Skoog guardrails](technical/skoog-application-guardrails.md)).
- **EWF role:** a future three-field branch may separate vapour core, wall
  film, and dispersed droplets, but Skoog supplies architecture/bookkeeping
  precedent rather than geothermal default values. Establish the carrier
  first, allocate liquid explicitly, enable one film mechanism at a time, and
  keep global DPM source feedback off for the first EWF stability control
  (Inferred, [Skoog guardrails](technical/skoog-application-guardrails.md)).

## Model-development order

1. close setup parity and obtain a stable carrier-field reference;
2. change one inlet representation at a time;
3. verify mesh, residual, phase-flux, pressure, and outlet-carryover evidence;
4. add DPM or higher-realism physics only after the carrier branch earns it;
5. compare against external or analytical anchors before using report-facing
   validation language.

This ordering is the project-level summary of the current run-efficiency
decision, not a replacement for an experiment's exact setup contract.

## Important limits

The model is not considered physically validated because it runs, reaches a
high iteration count, or produces a plausible contour. DPM carryover remains a
bounded diagnostic when incomplete trajectories or unverified injection
assumptions dominate the evidence (Inferred, [V&V limits](vnv.md)).
