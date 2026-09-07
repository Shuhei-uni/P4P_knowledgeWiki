# Synthesis: Two-Phase Geofluid Property Modeling to Binary Plant Design

## Sources Covered
- [merbecks-2025-geoprop-geofluid-property-framework](../sources/merbecks-2025-geoprop-geofluid-property-framework.md)
- [montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid](../sources/montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid.md)

## Side-by-Side Pattern Summary
- 2025 source contributes upstream model fidelity:
  - Better phase/property representation for non-pure-water geofluids.
- 2026 source contributes downstream process value:
  - Plant-level gains depend on accurate two-phase resource characterization.

## Core Defaults (Safe Starting Point)
1. Build property-aware geofluid model first (composition-sensitive).
2. Pass validated property envelopes into binary cycle/process optimization.
3. Compare against flash baselines under matched resource assumptions.

## When to Switch
- Switch from simplified property assumptions to full reactive/property coupling when salinity/NCG effects are large.
- Switch to site-specific re-optimization when CAPEX assumptions or ambient conditions differ.

## Failure Signals
- Design heat-balance mismatch when moving from simplified to detailed properties.
- Cycle performance that is highly unstable under small composition shifts.

## Validation Checks
1. Property model benchmark vs available field/lab data.
2. Sensitivity of net power and exchanger sizing to composition.
3. Economic rerun with local cost and financing assumptions.
