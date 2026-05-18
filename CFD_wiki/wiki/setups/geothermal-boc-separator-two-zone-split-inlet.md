# Setup: Geothermal BOC Separator Two-Zone Split Inlet

## Purpose
Reusable adaptation of the geothermal BOC separator baseline for cases where the inlet should be spatially segregated instead of uniformly mixed.

Target pattern:

- outer-wall side of inlet: liquid water
- inner/core side of inlet: steam

## Primary Reuse Base
- Baseline setup page: [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md)

## Relation To Existing Knowledge
- `extends` [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md) by changing only the inlet representation while keeping the main solver stack unchanged.

## Reported vs Inferred vs Assumed
- `Reported`: separator baseline solver/model choices and inlet total phase-flow values taken from the 2013 source through the baseline setup page.
- `Inferred`: the easiest robust Fluent implementation is to split the inlet boundary into two named zones.
- `Assumed`: first adaptation uses a sharp half-half inlet split with pure liquid on the wall side and pure steam on the inner side.

## When To Use This
- When the baseline uniform or mist-like inlet is too idealized for the project objective.
- When you want one controlled A/B change before attempting more complex inlet profiles or a UDF.
- When the physical intuition is that phase segregation already exists before flow enters the separator.

## Core Implementation Rule
Do the inlet split in geometry/meshing first, not only in Fluent initialization.

Why this matters:

- A patched field is not the same as a persistent inlet boundary condition.
- Two named inlet zones are easier to audit, reproduce, and compare.

## Step-Wise Adaptation
1. Duplicate the converged or closest-available baseline case.
2. Split the inlet face into two separate faces:
   - `inlet_liquid_outer`
   - `inlet_steam_inner`
3. Remesh with the same global strategy as baseline.
4. Import the mesh and verify both inlet zones appear in Fluent.
5. Keep the same solver family, gravity, mixture model, turbulence model, materials, outlet, walls, and numerical schemes as baseline.
6. Set both new boundaries as `Mass-Flow Inlet`.
7. Assign pure-phase state by boundary:
   - `inlet_liquid_outer`: liquid fraction `1.0`
   - `inlet_steam_inner`: liquid fraction `0.0`
   - If your Fluent version uses different field labels, keep the physical target the same rather than forcing identical UI wording.
8. Preserve baseline phase mass-flow totals for the first test:
   - liquid-side inlet mass flow: `116.92 kg/s`
   - steam-side inlet mass flow: `80.69 kg/s`
9. Initialize with `Hybrid Initialization`.
10. Compare against the original baseline using the same monitors and post-processing planes.

## Reused Baseline Settings
- Solver: `Pressure-Based` (`Reported`) ([purnanto-2013], p.6)
- Time: steady (`Reported`) ([purnanto-2013], p.5)
- Gravity: on, downward in `y` (`Reported`) ([purnanto-2013], p.5)
- Multiphase model: `Mixture` (`Reported`) ([purnanto-2013], p.3)
- Turbulence: RNG `k-epsilon` (`Reported`) ([purnanto-2013], p.1-3)
- Energy: off / isothermal (`Reported`) ([purnanto-2013], p.5)
- Inlet BC family: `Mass-Flow Inlet` (`Reported`) ([purnanto-2013], p.6)
- Outlet BC family: `Pressure Outlet` (`Reported`) ([purnanto-2013], p.6)
- Initialization: `Hybrid Initialization` (`Reported`) ([purnanto-2013], p.6)
- Schemes: `SIMPLE`, `PRESTO`, second-order upwind, `QUICK` (`Reported`) ([purnanto-2013], p.6)

## Assumptions
- Sharp half-half inlet split is used as the first realism upgrade (`Assumed`, `Medium Risk`).
- Same total phase mass-flow rates are preserved while only the spatial distribution changes (`Assumed`, `Medium Risk`).
- Boundary split should be interpreted by physical meaning (`outer wall` vs `inner/core`) rather than camera direction (`left` vs `right`) (`Assumed`, `Low Risk`).

## Missing Info
- Exact inlet-face orientation for each geometry family is not universal.
- The source paper does not report a segregated inlet profile, so this adaptation is not source-reported.
- Inlet-face area is not captured in this page, so the resulting phase velocities must be checked case by case.

## Sensitivity Plan
1. Run one sharp half-half split case first with all other settings frozen.
2. Check whether steam-side velocity becomes unrealistically high due to low gas density.
3. If convergence or physics look poor, test one refinement at a time:
   - local inlet mesh refinement,
   - short upstream duct partition,
   - softer phase-fraction profile instead of pure-phase split.

## Common Failure Modes
- Geometry sketch line does not create two real boundary faces.
- Boundary names are based on viewing direction and get reversed later.
- Pure half-half split creates a numerically harsh inlet jump.
- Users change numerics at the same time as inlet structure, making comparison unclear.

## Quick Diagnostics
- Confirm both inlet boundaries appear in Fluent.
- Plot volume fraction on the inlet plane and immediately downstream.
- Compare pressure drop and outlet phase split against the uniform-inlet baseline.
- Check whether mass imbalance or outlet backflow becomes worse after the inlet split.

## Cross-Linkage
- Reuses baseline values from [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md).
- Project-facing summary should live in `ResearchProject_wiki` rather than be duplicated here.
