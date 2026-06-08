# Source: Comparative CFD Modelling of Pressure Differential Flow Meters for Two-Phase Geothermal Flow (2020)

## Source Metadata
- Source ID: `mubarok-2020`
- File: `raw/1-s2.0-S0375650519304328-main.pdf`
- Authors: Mohamad Husni Mubarok, John E. Cater, Sadiq J. Zarrouk
- Venue: Geothermics 86 (2020) 101801
- Primary tool: ANSYS Fluent 18.2

## One-Page Summary
This paper builds and validates 3D CFD models for six pressure-differential geothermal two-phase flow meters (concentric/top-eccentric/bottom-eccentric/segmental orifice, nozzle, Venturi), then compares pressure loss, flow structure, and thermodynamic losses ([mubarok-2020], p.1-2, p.14-15).

Field-test data from four Indonesian geothermal wells are used for validation. The validated models report pressure-drop, mass-flow, and enthalpy prediction errors mostly within ±5% for the concentric orifice baseline ([mubarok-2020], p.3-4, p.8-9, p.14).

## A) Study Scope
- Objective: compare flow-meter geometries for two-phase geothermal metering quality and pressure-loss behavior ([mubarok-2020], p.1-2).
- Domain: 3D pipeline + meter geometries, about 6 m domain length (longer for Venturi) ([mubarok-2020], p.4-5).
- Outputs: net pressure drop, velocity, TKE, temperature, enthalpy, entropy, and estimated mass-flow performance ([mubarok-2020], p.1, p.9-15).

## B) Physics and Models
- Flow assumptions: two-phase water/steam mixture with steady and transient runs for benchmarking ([mubarok-2020], p.6, Table 2).
- Governing equations: continuity, RANS momentum, mixture multiphase formulation, SST turbulence transport, and energy equation ([mubarok-2020], p.5-7).
- Turbulence model: SST k-omega ([mubarok-2020], p.6, p.14).
- Multiphase model: mixture model with phase-1 steam/vapor and phase-2 liquid/brine ([mubarok-2020], p.5-6, Table 2).
- Particle model: not used (Eulerian mixture instead of DPM).

## C) Material and Operating Conditions
- Gravity: -9.81 m/s^2 on y-axis ([mubarok-2020], Table 2).
- Field-calibrated operating inputs include mass flow, dryness, enthalpy, pressure, and temperature ranges from multiple wells ([mubarok-2020], Table 3, Table 4).
- Design beta ratio for validated concentric orifice: 0.7 ([mubarok-2020], p.4).

## D) Boundary and Initial Conditions
- Initialization: Standard Initialization ([mubarok-2020], Table 2).
- Inlet/outlet: pressure-differential meter context with upstream/downstream pressure monitoring and measured inputs from field tests ([mubarok-2020], p.3-4, p.8-9).
- Flange tap locations: 25.4 mm upstream and downstream of plate ([mubarok-2020], p.4, p.9).
- Full primitive-variable initialization values: `Missing` (not fully tabulated).

## E) Mesh and Numerics
- Mesh: unstructured with curvature-based refinement; transition ratio 0.272, growth 1.2, max 5 wall-near layers, min edge 3.2 mm ([mubarok-2020], p.7).
- Mesh study: Richardson extrapolation with six densities; mesh-6 selected (<1% extrapolated error targets) ([mubarok-2020], p.7-8).
- Solver type: pressure-based ([mubarok-2020], Table 2).
- Simulation type: steady + transient benchmark ([mubarok-2020], Table 2, p.9).
- Discretization: momentum second-order upwind, volume fraction/energy/TKE/omega first-order upwind ([mubarok-2020], Table 2).
- Maximum Courant number: 20 ([mubarok-2020], Table 2).

## F) Validation and Results
- Concentric orifice validation against field data shows <±5% relative error for key outputs ([mubarok-2020], p.8-9, p.14).
- Venturi and nozzle give lowest pressure losses; segmental orifice outperforms concentric among orifice variants for pressure loss ([mubarok-2020], p.10-11, p.14-15).
- Thermodynamic-loss analysis indicates lowest entropy generation in Venturi and higher losses in concentric designs ([mubarok-2020], p.13-15).

## G) Reproducibility Risk
### Missing Parameter List
- Under-relaxation factors are not reported for this specific model setup.
- Exact residual stopping thresholds are not fully listed.
- Full transient time-step schedule outside benchmark statement is incomplete.

### Assumptions Used in This Wiki
- Assume standard Fluent residual targets for unreported equations (`Assumed`, `Medium Risk`).
- Assume reported mesh-6 settings are transferable across all six meter geometries (`Inferred`, `Medium Risk`).

### Confidence Rating
`Medium-High` for relative geometry ranking; `Medium` for absolute replication without full solver-control details.

### Minimal Sensitivity Tests
1. Repeat with second-order schemes for all transported variables.
2. URF sweep for pressure/momentum/energy.
3. Time-step sensitivity for transient benchmark case.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [purnanto-2013-cfd-geothermal-separator](purnanto-2013-cfd-geothermal-separator.md)
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
- Relations:
  - `extends`: extends geothermal two-phase CFD from separators to in-line meter components.
  - `reuses`: reuses geothermal two-phase CFD framing and ANSYS Fluent ecosystem.
- Reuse recommendation:
  - Copy this workflow when meter pressure-loss and metering uncertainty are core targets.
  - Adapt rather than copy if the project target is separation efficiency inside large vessels.
