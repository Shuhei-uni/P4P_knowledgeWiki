# Baseline CFD Definition

## Purpose
Freeze an explicit baseline case definition for reproducible convergence debugging.

## Case ID
- `baseline-bangma-recreation-v1` (working draft)

## Mandatory Fields To Fill Before Next Run
- Geometry source and exact dimensions.
- Mesh stats and quality metrics.
- Solver type and pressure-velocity coupling.
- Multiphase and turbulence model settings.
- BC and IC values.
- Initialization method.
- Convergence criteria and monitors.

## Current State
- Active but incomplete.
- Current run evidence points to missing parity capture of all settings.

## Mesh Quality and Resolution Note
- `Reported`: the baseline separator paper used unstructured tetrahedral meshes and states that node counts in the order of millions were preferable for the vessel scale, with average 5 cm elements and local 1 cm face refinement near high-gradient boundaries (`purnanto-zarrouk-cater-2013`, p.6).
- `Inferred`: the current approximately 1.8M-node project mesh is now consistent with the source paper's "order of millions" scale, so the main mesh concern has shifted from global density to local quality and quality distribution.
- `Inferred`: the reported minimum orthogonal quality of 6.73e-2 should be treated as a mesh-audit trigger, not as automatic proof that the case is unusable.
- `Inferred`: since the worst cells are at inlet/outlet regions, prioritize local face/edge sizing and geometry cleanup there; use inflation mainly on physical walls and suppress or soften it locally if layers collapse near sharp inlet/outlet transitions.
- `Inferred`: before using the mesh for report-quality conclusions, locate the worst cells and run a mesh-independence check on pressure drop, outlet steam behavior/carryover proxy, mass imbalance, and vortex-core trends.
- Reusable CFD synthesis: `../../../CFD_wiki/wiki/synthesis/mesh-quality-and-resolution-patterns.md`
- Inflation concept: `../../../CFD_wiki/wiki/concepts/mesh-inflation-boundary-layer.md`

## Multiphase Accuracy Guidance
- `Reported`: the 2013 separator paper says both `Mixture` and `Eulerian` are suitable when dispersed-phase volume fraction is above 10%, says `Mixture` is cheaper but less accurate than `Eulerian`, and still selects `Mixture` as the most appropriate model for this separator because the Stokes number is much less than 1 (`purnanto-zarrouk-cater-2013`, p.3).
- `Inferred`: for this project, `Eulerian` should be treated as a second-stage sensitivity study, not as the first correction to a non-validated baseline.
- `Inferred`: likely higher-value accuracy upgrades before a model swap are:
  1. lock a clean converged `Mixture` baseline,
  2. refine mesh in swirl-critical regions,
  3. improve inlet phase/velocity realism,
  4. then compare `Mixture` versus `Eulerian` on the same stabilized case.

## Next Action
Complete this page before launching the next major iteration batch, and keep the first comparison matrix limited to one change at a time.
