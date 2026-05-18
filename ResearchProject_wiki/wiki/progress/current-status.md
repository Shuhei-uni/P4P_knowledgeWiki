# Current Status

## Snapshot
- Date: 2026-05-06
- Phase: Baseline CFD model recreation moving toward inlet-regime refinement
- Focus: define the first realistic split-inlet case while preserving baseline solver parity
- Current issue: mesh density has been increased to literature-scale order, but mesh quality remains a concern before report-quality conclusions.
- Current mesh scale: approximately 1.8M nodes (user-reported)

## What Is Done
- Rough literature overview completed.
- Baseline geometry provided and run attempts started.
- Initial non-convergence signal observed.
- Baseline steady two-phase setup defined in Fluent (pressure-based, RNG k-epsilon, Mixture model, gravity, isothermal assumption).
- A first project-specific inlet-regime change has now been defined conceptually: split inlet with wall-side liquid and inner-side steam.
- Geometry context has been clarified: this split-inlet plan is for the **spiral-inlet** baseline case.
- Mesh density increased from earlier approximately 300k-node run to approximately 1.8M nodes.

## What Is In Progress
- Convergence debugging for recreated baseline case.
- Verification of flow settings and numerical configuration.
- Review of whether mesh quality, worst-cell location, and mesh-independence evidence are sufficient for stable solution progression.
- Building a result-interpretation workflow to connect contour outputs to separator performance decisions.
- Preparing the first geometry/mesh-level inlet modification so it changes only boundary representation, not the full solver stack.

## Immediate Next Actions
1. Map which inlet half is outer-wall side versus inner/core side on the spiral-inlet face.
2. Locate the worst-quality cells and confirm whether they sit in inlet, swirl, wall, steam-outlet, or brine-outlet critical regions.
3. Split the inlet face into two named boundary zones and remesh without degrading the main mesh quality.
4. Run the first A/B comparison using the same solver/model settings with only the inlet structure changed.
5. Evaluate the same KPI set for both cases: pressure drop, steam outlet behavior, liquid carryover trend, inlet-region phase distribution, and convergence stability.
