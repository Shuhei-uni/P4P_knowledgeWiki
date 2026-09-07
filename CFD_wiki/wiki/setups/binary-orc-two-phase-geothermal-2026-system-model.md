# Setup: Two-Phase Geothermal Binary ORC Process Model (2026)

## Purpose
Rebuild the system-level two-phase geothermal binary-plant model from `montesdeoca-2026` for process and economic screening.

## Source
- Primary: [montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid](../sources/montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid.md)

## Step-by-Step Build Order
1. Define geothermal wellhead pressure/enthalpy and two-phase split assumptions.
2. Build separator + dual-evaporator + preheater + recuperative ORC flowsheet.
3. Select working fluid (n-pentane/isopentane/n-butane) and set cycle limits.
4. Sweep TIT, wellhead pressure, pinch point and dry-cooler approach.
5. Optimize for net power and compare CAPEX/SPO against flash references.

## Key Inputs
- Reported strong case: TIT 175 C, wellhead pressure 13 bar, dry-cooler approach 16 K, n-pentane (`Reported`) ([montesdeoca-2026], Abstract).

## Missing Info
- Not a CFD setup; no mesh/numerics stack for flow field reconstruction.
- Some cost factors and productivity assumptions are context-specific.

## Assumptions
- Treat this as thermodynamic process model, coupled later to reservoir/flow assurance work (`Assumed`, `Low Risk`).

## Sensitivity Plan
1. Fluid selection sensitivity.
2. Ambient and dry-cooler approach sensitivity.
3. Reservoir productivity uncertainty sensitivity.

## Common Failure Modes
- Overestimated performance when geofluid properties are simplified.
- Economic ranking reversal under local cost and financing inputs.
- Off-design degradation at high ambient temperatures.

## Quick Diagnostics
- Verify mass/energy closure in each heat exchanger.
- Compare SPO and CAPEX deltas against baseline flash cases.
- Check reinjection temperature constraints against field limits.
