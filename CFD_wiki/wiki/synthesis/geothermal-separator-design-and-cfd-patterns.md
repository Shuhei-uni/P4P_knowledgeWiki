# Synthesis: Geothermal Separator Design and CFD Patterns

## Sources Covered
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
- [rivas-cruz-2015-geothermal-separator-state-of-art-review](../sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md)

## Side-by-Side Pattern Summary
- Geometry/design family:
  - Stable pattern: vertical BOC cyclone remains dominant in practice (`supports`).
- Efficiency framing:
  - Stable pattern: reported high steam quality and separator efficiency targets are consistently near high-purity operation.
- Modeling style:
  - 2013 source gives direct CFD reconstruction detail.
  - 2014/2015 reviews provide design-screening and historical-method context.

## Core Defaults (Safe Starting Point)
1. Start with BOC/spiral-inlet geometry as baseline.
2. Keep inlet velocity in established practical band before pushing aggressive designs.
3. Pair empirical screening with CFD confirmation.

## When to Switch
- Switch to horizontal or alternative designs when pressure-drop, layout, or maintenance constraints dominate.
- Switch from pure empirical sizing to CFD-led refinement when carryover risk or off-design transients are critical.

## Failure Signals
- Steam quality/purity drift despite unchanged nominal setpoints.
- Increased pressure drop or instability during field-output changes.
- Persistent carryover near turbine side despite separator nominal efficiency.

## Validation Checks
1. Field steam quality/purity monitoring against design envelope.
2. CFD vs empirical agreement on pressure/velocity trends.
3. Drainage/scrubbing architecture adequacy in final layout decisions.

## Related Physics Basis
- [separator-flow-physics](../physics-basis/separator-flow-physics.md)
- [separator-geometry-and-swirl-mechanisms](../physics-basis/separator-geometry-and-swirl-mechanisms.md)
- [operating-pressure-enthalpy-and-phase-split](../physics-basis/operating-pressure-enthalpy-and-phase-split.md)
