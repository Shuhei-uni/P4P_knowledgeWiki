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
- Current run evidence now includes a live HDF5 audit of the Purnanto case/data pair, so the main parity gap has shifted away from BC and numerics capture and toward geometry confirmation, residual history, and DPM readiness.

## Current Audited Purnanto Reference
- Use [purnanto-live-setup-reference](../technical/purnanto-live-setup-reference.md) first when you need the audited live Fluent setup rather than the paper narrative.
- The audited case confirms the baseline stack: pressure-based steady `Mixture`, RNG `k-epsilon`, SIMPLE, PRESTO!, second-order momentum/turbulence, QUICK, gravity on, operating pressure `0 Pa`, mass-flow inlet, pressure outlet, and `5000` saved iterations.
- The remaining unknowns are now mostly the ones the case file does not settle directly: exact geometry variant, residual history, mass balance by phase, and DPM injection state.

## Purnanto Geometry Scope Boundary

The current Purnanto-derived geometry is a simplified separator representation without a modelled brine/liquid discharge outlet. Retained liquid is therefore not expected to leave through a closed lower-liquid path in the present model.

Whole-domain liquid or mixture mass imbalance is consequently not a numerical acceptance criterion for this project phase and must not be described as an active simulation blocker. Current performance interpretation is based on liquid and vapour escaping through `steamoutlet`, residual and monitor stability, sufficient iteration development, and mesh convergence.

Resolving retained liquid would require revised geometry, a liquid-outlet definition, boundary conditions, initialization, and a corresponding validation framework. That work is out of scope until the simplified Purnanto model is matched and the higher-priority numerical work is complete.

DPM `Incomplete` trajectories may remain in raw Fluent outputs for traceability, but they are not a project blocker or report acceptance gate. Report-facing DPM interpretation is limited to observed escape through `steamoutlet`; incomplete particles are neither relabelled as trapped nor required to be eliminated in this phase.

## Mesh Quality and Resolution Note
- `Reported`: the baseline separator paper used unstructured tetrahedral meshes and states that node counts in the order of millions were preferable for the vessel scale, with average 5 cm elements and local 1 cm face refinement near high-gradient boundaries (`purnanto-zarrouk-cater-2013`, p.6).
- `Observed`: the live HDF5 audit now confirms a `2,964,593`-cell tetra mesh with `572,556` nodes, `6,063,406` faces, minimum orthogonal quality `0.277635`, and maximum aspect ratio `12.8899`.
- `Inferred`: the current approximately 1.8M-node project mesh is now consistent with the source paper's "order of millions" scale, so the main mesh concern has shifted from global density to local quality and quality distribution.
- `Inferred`: the reported minimum orthogonal quality of 6.73e-2 should be treated as a mesh-audit trigger, not as automatic proof that the case is unusable.
- `Inferred`: since the worst cells are at inlet/outlet regions, prioritize local face/edge sizing and geometry cleanup there; use inflation mainly on physical walls and suppress or soften it locally if layers collapse near sharp inlet/outlet transitions.
- `Inferred`: before using the mesh for report-quality conclusions, locate the worst cells and run a mesh-independence check on pressure drop, outlet steam behavior/carryover proxy, and vortex-core trends. Whole-domain liquid imbalance remains informational under the Purnanto scope boundary.
- Reusable CFD synthesis: `../../../CFD_wiki/wiki/synthesis/mesh-quality-and-resolution-patterns.md`
- Inflation concept: `../../../CFD_wiki/wiki/concepts/mesh-inflation-boundary-layer.md`

## Multiphase Accuracy Guidance
- `Reported`: the 2013 separator paper says both `Mixture` and `Eulerian` are suitable when dispersed-phase volume fraction is above 10%, says `Mixture` is cheaper but less accurate than `Eulerian`, and still selects `Mixture` as the most appropriate model for this separator because the Stokes number is much less than 1 (`purnanto-zarrouk-cater-2013`, p.3).
- `Observed`: the live HDF5 audit uses the `Mixture` model with two phases, matching the paper baseline stack.
- `Inferred`: for this project, `Eulerian` should be treated as a second-stage sensitivity study, not as the first correction to a non-validated baseline.
- `Inferred`: likely higher-value accuracy upgrades before a model swap are:
  1. lock a clean converged `Mixture` baseline,
  2. refine mesh in swirl-critical regions,
  3. improve inlet phase/velocity realism,
  4. then compare `Mixture` versus `Eulerian` on the same stabilized case.

## Next Action
Complete this page before launching the next major iteration batch, and keep the first comparison matrix limited to one change at a time.
