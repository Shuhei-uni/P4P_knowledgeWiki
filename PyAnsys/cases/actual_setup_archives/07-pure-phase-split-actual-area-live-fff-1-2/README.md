# Actual Fluent Setup Archive: 07 Pure Phase Split Actual Area Live FFF 1-2

## Purpose

This folder stores the machine-exported Fluent state for the live case/data pair loaded from:

- `C:\Users\syok443\Documents\Setup07extractor\FFF.1-2.cas.h5`
- `C:\Users\syok443\Documents\Setup07extractor\FFF.1-2-02541.dat.h5`

This is an `actual live setup` archive, not an interpretation of the intended setup.

Use this folder when you need:

- what Fluent actually contained at export time;
- a lower-human-error source for rebuild automation;
- a conflict check against the inherited setup-report chain.

Related report-facing branch:

- [07-pure-phase-split-actual-area.md](../../../../Setups/past/reported/07-pure-phase-split-actual-area.md)

Related difference report:

- [intended-vs-actual.md](./intended-vs-actual.md)

## Archive Contents

- [metadata.json](./metadata.json): source paths, export time, archive label
- [settings_snapshot.json](./settings_snapshot.json): broad PyFluent-reachable setup and solution state
- [scheme_snapshot.json](./scheme_snapshot.json): Scheme-side runtime values
- [models_tree_detailed.json](./models_tree_detailed.json): deep enumeration of `setup.models`, including inactive-but-available children
- [notes.txt](./notes.txt): exporter access gaps and inactive-branch warnings

## Key Live Findings

### Boundary Identity

- Velocity inlets: `liquidinlet`, `steaminlet`
- Pressure outlet: `steamoutlet`
- Walls: `wall-fluid`, `bottom`
- Interior: `interior-fluid`

### Active Core Physics

- Solver family: pressure-based, steady
- Multiphase model: `mixture`
- Number of phases: `2`
- Energy: `off`
- Viscous model: `k-epsilon`
- `k-epsilon` variant: `rng`
- RNG options: differential viscosity `on`, swirl-dominated flow `on`
- Near-wall treatment: `standard-wall-fn`

### Active Numerics In The Live Case

- Pressure-velocity coupling: `Coupled`
- Pressure discretization: `PRESTO!`
- Momentum discretization: `first-order-upwind`
- Turbulent kinetic energy discretization: `first-order-upwind`
- Turbulent dissipation rate discretization: `first-order-upwind`
- Mixture / multiphase discretization entry: `first-order-upwind`

### Model-Tree Findings That Matter

- The live `multiphase` tree exposes these children in this Fluent build:
  - `models`
  - `vaporization_pressure`
  - `non_condensable_gas`
  - `liquid_surface_tension`
  - `bubble_number_density`
  - `number_of_phases`
  - `number_of_eulerian_discrete_phases`
- In this exported live case, `liquid_surface_tension` exists in the tree but is currently inactive/unset.
- The live `discrete_phase` tree is active and nontrivial. It includes tracking, numerics, and multiple injections. This means the exported case is not just a bare continuous-flow branch.

## Interpretation Rule

Treat this folder as the best record of what the loaded Fluent case actually contained.

Do not assume it is identical to the intended inherited setup from:

1. `00-baseline-spiral-boc-reference.md`
2. `03-mixed-wet-half-velocity-inlet.md`
3. `04-mixed-wet-half-actual-area.md`
4. `07-pure-phase-split-actual-area.md`

That intended-vs-actual reconciliation is tracked separately in [intended-vs-actual.md](./intended-vs-actual.md).
