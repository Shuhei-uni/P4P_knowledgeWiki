# Setup: Geothermal Two-Phase Flow Meter CFD Benchmark (Fluent, 2020)

## Purpose
Rebuild the validated baseline from `mubarok-2020` to compare pressure-differential meter geometries for two-phase geothermal pipelines.

## Source
- Primary: [mubarok-2020-cfd-geothermal-flow-meters](../sources/mubarok-2020-cfd-geothermal-flow-meters.md)

## Step-by-Step Build Order
1. Build 3D meter geometries (concentric/top-eccentric/bottom-eccentric/segmental/nozzle/venturi).
2. Generate refined unstructured mesh and run mesh sensitivity.
3. Configure pressure-based mixture model with SST k-omega and energy equation.
4. Apply field-derived inlet/outlet operating conditions.
5. Run steady solutions; run transient benchmark for consistency check.
6. Compare pressure drop, mass flow, enthalpy and thermodynamic-loss indicators.

## A) Geometry and Domain
- Total model length around 6 m for most geometries (`Reported`) ([mubarok-2020], p.4-5).
- Venturi domain is longer to include convergent-throat-divergent section (`Reported`) ([mubarok-2020], p.4-5).

## B) Materials and Operating Inputs
- Two-phase mixture: steam + brine/water (`Reported`) ([mubarok-2020], p.5-6).
- Use field-test ranges for mass flow, enthalpy, dryness, and pressure (`Reported`) ([mubarok-2020], Table 3, Table 4).

## C) Physics and Models
- Multiphase model: mixture (`Reported`) ([mubarok-2020], p.5-6).
- Turbulence: SST k-omega (`Reported`) ([mubarok-2020], Table 2).
- Gravity: -9.81 m/s^2 in y (`Reported`) ([mubarok-2020], Table 2).

## D) Boundary and Initial Conditions
- Initialization: Standard Initialization (`Reported`) ([mubarok-2020], Table 2).
- Flange pressure taps at 25.4 mm upstream and downstream (`Reported`) ([mubarok-2020], p.4, p.9).
- Full initialized primitive-field values are not provided (`Missing`).

## E) Mesh and Numerics
- Mesh settings (`Reported`) ([mubarok-2020], p.7):
  - Curvature refinement
  - Transition ratio 0.272
  - Growth rate 1.2
  - Max 5 near-wall layers
  - Min edge length 3.2 mm
- Solver and schemes (`Reported`) ([mubarok-2020], Table 2):
  - Pressure-based
  - Momentum second-order upwind
  - Volume fraction, k, omega, energy first-order upwind
  - Max Courant number 20

## Missing Info
- Under-relaxation factors per equation.
- Residual targets and monitor-based stop rules.
- Complete transient time-step schedule.

## Assumptions
- Use standard Fluent URFs unless calibration data is available (`Assumed`, `Medium Risk`).
- Use same mesh strategy across all six geometries (`Assumed`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. URF sweep.
2. First- vs second-order scheme sensitivity for transported scalars.
3. Mesh refinement around throat/recirculation zones.

## Common Failure Modes
- Non-physical recirculation persistence due to low-order transport.
- Meter ranking flip after mesh or URF changes.
- Unstable downstream entropy trends.

## Quick Diagnostics
- Check mass balance and pressure recovery curves.
- Plot centerline pressure and TKE.
- Verify validated concentric case remains within expected error band.

## Cross-Paper Linkage
- Related separator CFD baseline: [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md) (`extends`).
