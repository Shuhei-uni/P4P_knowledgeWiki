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
- `Calculated`: if both zones use the same inlet velocity and pure phases, the split area must be based on phase volumetric flow, not a 50/50 face split.
- `Assumed`: first adaptation uses a sharp phase boundary with pure liquid on the wall side and pure steam on the inner side.

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
9. If using velocity inlets with the same velocity on both pure-phase zones, split the inlet by the calculated area rule below rather than a 50/50 split.
10. Initialize with `Hybrid Initialization`.
11. Compare against the original baseline using the same monitors and post-processing planes.

## Equal-Velocity Pure-Phase Area Rule
Use this when the inlet must be one side pure liquid and one side pure steam, while both inlet zones keep the same normal velocity and the Purnanto `1600 kJ/kg` phase mass flows are preserved.

Formula:

```text
Q_liquid = m_dot_liquid / rho_liquid
Q_steam  = m_dot_steam / rho_steam
V        = (Q_liquid + Q_steam) / A_total
A_liquid = Q_liquid / V
A_steam  = Q_steam / V
```

For a rectangular inlet `0.724 m x 0.724 m`:

```text
A_total = 0.724 * 0.724 = 0.524176 m2

m_dot_liquid = 116.92 kg/s
m_dot_steam  = 80.69 kg/s
rho_liquid   = 881.77 kg/m3
rho_steam    = 5.73 kg/m3

Q_liquid = 0.1325969 m3/s
Q_steam  = 14.0820244 m3/s
V        = 27.1180 m/s

A_liquid = 0.0048896 m2 = 0.9328 % of inlet area
A_steam  = 0.5192864 m2 = 99.0672 % of inlet area
```

If the split is made along the `x` direction and the full inlet height is `0.724 m`:

```text
liquid-side width = A_liquid / 0.724 = 0.006754 m
steam-side width  = A_steam  / 0.724 = 0.717246 m
```

So the split line should be `0.00675 m` from the liquid-side edge, or equivalently `0.71725 m` from the steam-side edge. This is a highly asymmetric split because the steam volumetric flow dominates at the reported density.

### Fixed Reported-Velocity Variant

If the priority is to preserve the reported spiral-inlet velocity `26.81 m/s` rather than force exact mass flow through the current `0.724 m x 0.724 m` inlet, keep the same area fractions and split location:

```text
A_liquid = 0.0048896 m2
A_steam  = 0.5192864 m2
split line = 0.006754 m from the liquid-side edge
```

Expected inlet mass flow at `26.81 m/s`:

```text
liquid = 115.59 kg/s
steam  = 79.77 kg/s
total  = 195.37 kg/s
```

This is `1.14 %` below the Purnanto `1600 kJ/kg` total mass-flow target because exact mass flow at `26.81 m/s` would require `0.5301985 m2`, slightly larger than the current `0.524176 m2` inlet area.

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
- Sharp pure-phase split is used as the first realism upgrade (`Assumed`, `Medium Risk`).
- Same total phase mass-flow rates are preserved while only the spatial distribution changes (`Assumed`, `Medium Risk`).
- Equal velocity is applied to both pure-phase inlet zones for this area-ratio rule (`Assumed`, `Medium Risk`).
- Boundary split should be interpreted by physical meaning (`outer wall` vs `inner/core`) rather than camera direction (`left` vs `right`) (`Assumed`, `Low Risk`).

## Missing Info
- Exact inlet-face orientation for each geometry family is not universal.
- The source paper does not report a segregated inlet profile, so this adaptation is not source-reported.
- Exact inlet-face orientation and which `x` edge corresponds to outer-wall liquid must be confirmed in the active CAD/mesh.

## Sensitivity Plan
1. Run one sharp pure-phase split case first with all other settings frozen.
2. Check whether the very narrow liquid strip is mesh-resolved and remains numerically stable.
3. If convergence or physics look poor, test one refinement at a time:
   - local inlet mesh refinement,
   - short upstream duct partition,
   - softer phase-fraction profile instead of pure-phase split.

## Common Failure Modes
- Geometry sketch line does not create two real boundary faces.
- Boundary names are based on viewing direction and get reversed later.
- Pure-phase split creates a numerically harsh inlet jump.
- Users change numerics at the same time as inlet structure, making comparison unclear.

## Quick Diagnostics
- Confirm both inlet boundaries appear in Fluent.
- Plot volume fraction on the inlet plane and immediately downstream.
- Compare pressure drop and outlet phase split against the uniform-inlet baseline.
- Check whether mass imbalance or outlet backflow becomes worse after the inlet split.

## Cross-Linkage
- Reuses baseline values from [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md).
- Extended by [geothermal-boc-separator-pure-phase-split-velocity-inlet](geothermal-boc-separator-pure-phase-split-velocity-inlet.md) for the fully specified pure-liquid/pure-steam velocity-inlet branch.
- Project-facing summary should live in Project/ rather than be duplicated
  here.
- Project pure-phase record: [purnanto-07 setup](../../../Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-07-pure-phase-actual-area/setup.md).
