# Full Geometry — Mixture Steady Liquid-Outlet Setup Campaign

This is the canonical setup-side home for the full-geometry steady Mixture investigation of the physical brine outlet and lower-vessel liquid behaviour.

## Canonical setup definitions

- [`02c` — unprimed brine-outlet pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- [`02e` — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md)
- [`03` — unpatched steady Mixture baseline qualification](03-mixture-steady-solution-qualification.md) — **draft / do not run until final readback-preflight is complete**

Their original detailed records are retained as [compatibility snapshots](../../../compatibility-snapshots/index.md) so no execution history is lost during the structural migration.

## Results

Numerical evidence remains separate from setup definitions:

- [Steady liquid-outlet report index](../../../reports/full-geometry/mixture/steady-liquid-outlet/index.md)

## Scientific role

`02c` provides the unprimed pressure-outlet sensitivity evidence. `02e` adds a common Y010 liquid initialization and compares outlet formulations/resistance. `03` deliberately removes the artificial liquid-pool initialization again and asks a simpler baseline question: **can the explicitly specified full-geometry split-inlet Mixture model reach a genuine steady state from Hybrid Initialization with no liquid patching?**

`03` uses the Purnanto Spiral-Inlet design as geometric/physical lineage, while the computational inlet is the project's split pure-phase representation: one pure-liquid and one pure-vapour sub-face of the same rectangular spiral inlet. The baseline uses the full Mixture equations from iteration 1, SIMPLE/PRESTO!/second-order/QUICK numerics, explicit RNG `k-epsilon` and boundary turbulence settings, and phase-flux/inventory monitoring.

The earlier steady studies do not establish that a particular outlet pressure is physically correct. `03` is also not a validation study; its first milestone is the existence of a stationary unpatched steady branch with interpretable phase routing and flux balance. More intrusive numerical stabilization, pressure continuation, liquid patching, or model-form changes are separate fallback experiments rather than part of the baseline.

## Transient branch

The [Mixture transient liquid-outlet characterization](../transient-liquid-outlet/index.md) remains part of the campaign history, but further transient development is paused while `03` tests whether a genuinely steady Mixture solution can first be obtained.
