# Full Geometry — Mixture Steady Liquid-Outlet Setup Campaign

This is the canonical setup-side home for the full-geometry steady Mixture investigation of the physical brine outlet and retained lower-vessel liquid.

## Canonical setup definitions

- [`02c` — unprimed brine-outlet pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- [`02e` — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md)
- [`03` — steady Mixture solution qualification](03-mixture-steady-solution-qualification.md) — **draft / do not run until detail audit is complete**

Their original detailed records are retained as [compatibility snapshots](../../../compatibility-snapshots/index.md) so no execution history is lost during the structural migration.

## Results

Numerical evidence remains separate from setup definitions:

- [Steady liquid-outlet report index](../../../reports/full-geometry/mixture/steady-liquid-outlet/index.md)

## Scientific role

`02c` provides the unprimed pressure-outlet control. `02e` adds a common Y010 liquid initialization and compares outlet formulations/resistance. `03` returns to the steady Mixture branch with a different objective: first establish one genuinely stationary full-Mixture state using staged equation activation and conservative numerics, then follow that converged branch through small brine-pressure continuation steps toward stronger retained-liquid behaviour.

The earlier steady studies do not establish that a particular outlet formulation is physically correct. `03` is also not a validation study; its first milestone is numerical steady-state qualification using phase fluxes and liquid-inventory stationarity rather than fixed iteration count alone.

## Transient branch

The [Mixture transient liquid-outlet characterization](../transient-liquid-outlet/index.md) remains part of the campaign history, but further transient development is paused while `03` tests whether a genuinely steady Mixture anchor can first be obtained.
