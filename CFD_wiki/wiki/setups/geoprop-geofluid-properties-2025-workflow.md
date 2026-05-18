# Setup: GeoProp Geofluid Property Workflow (2025)

## Purpose
Compute geofluid phase behavior and thermophysical properties for geothermal design inputs before CFD/process optimization.

## Source
- Primary: [merbecks-2025-geoprop-geofluid-property-framework](../sources/merbecks-2025-geoprop-geofluid-property-framework.md)

## Step-by-Step Build Order
1. Define geofluid composition from sampling data (water, salts, NCGs).
2. Select equilibrium partition and property models in GeoProp.
3. Evaluate property envelopes across expected pressure/temperature range.
4. Export density/enthalpy/phase-quality behavior for downstream design models.
5. Run sensitivity for composition and model-choice uncertainty.

## Key Inputs
- Composition vectors and operating P-T envelope are primary controls.
- Model-selection choices (EOS/activity model/database) are critical.

## Missing Info
- Not a CFD flow setup; no mesh or discretization.
- Exact results depend on code/database version pairing.

## Assumptions
- Start from validated benchmark model sets and then tune to site data (`Assumed`, `Medium Risk`).

## Sensitivity Plan
1. Salinity sweep.
2. NCG fraction sweep.
3. EOS/activity model swap.

## Common Failure Modes
- Using pure-water approximation outside safe range.
- Mixing inconsistent thermodynamic databases.
- Ignoring model uncertainty propagation to plant sizing.

## Quick Diagnostics
- Plot T-Q and phase-fraction curves for each composition scenario.
- Compare density/enthalpy against available lab data.
- Quantify design-input spread passed to CFD/ORC models.
