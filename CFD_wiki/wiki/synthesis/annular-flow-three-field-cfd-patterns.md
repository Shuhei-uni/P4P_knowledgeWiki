# Synthesis: Annular Flow Three-Field CFD Patterns

## Sources Covered
- [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)

## Side-by-Side Pattern Summary
- Shared structure:
  - Both use three-field decomposition (gas core, wall film, droplets) (`supports`).
  - Both rely on DPM + EWF coupling (`reuses`).
- Main difference:
  - 2020 thesis emphasizes implementation/UDF control and onset split sensitivity.
  - 2024 paper emphasizes entrainment-correlation benchmarking and broader operating envelope checks.

## Core Defaults (Safe Starting Point)
1. Use transient SST k-omega + DPM + EWF.
2. Calibrate entrainment closure against reference data before deployment.
3. Check outlet equilibrium (entrainment approximately deposition) before reading final metrics.

## When to Switch
- Switch entrainment closure if EF trends are biased at low/high gas velocities.
- Switch droplet-size assumptions if deposition profile mismatch persists.

## Failure Signals
- Systematic EF underprediction.
- Nonphysical film-thickness trends near outlet.
- Strong mesh/time-step dependence of deposition rate.

## Validation Checks
1. EF error band versus reference experiments.
2. Mass-balance closure across three fields.
3. Stability of results under droplet-size, parcel-rate, and mesh perturbations.
