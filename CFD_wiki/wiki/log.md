# CFD Wiki Log

## [2026-04-21] ingest | Purnanto 2013 geothermal separator baseline
- Files created/updated:
  - `wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/entities/geometry-vertical-boc-cyclone-separator.md`
  - `wiki/entities/turbulence-rng-k-epsilon.md`
  - `wiki/entities/solver-pressure-based-simple-presto.md`
  - `wiki/entities/multiphase-dpm-particle-tracking.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: first source ingest to establish reproducible geothermal separator CFD baseline and numerical-parameter capture workflow.
- Notable assumptions introduced or removed:
  - Introduced inferred two-stage continuous+particle workflow due mixed wording around mixture model vs DPM usage.
  - Introduced medium-risk fallback assumptions for unreported convergence controls.

## [2026-04-21] query | Clarify meaning of "two-phase flow" in separator paper
- Files created/updated:
  - `wiki/concepts/two-phase-flow-regime-vs-cfd-representation.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: distinguish physical geothermal flow regimes from the simplified CFD two-phase representation used in the 2013 separator study.
- Notable assumptions introduced or removed:
  - Introduced one general terminology note listing common regime names as `Assumed` (non-source-specific context).
