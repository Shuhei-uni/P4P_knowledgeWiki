# Full Geometry — Mixture Steady Liquid-Outlet Setup Campaign

This is the canonical setup-side home for the full-geometry steady Mixture investigation of the physical brine outlet and retained lower-vessel liquid.

## Canonical setup definitions

- [`02c` — unprimed brine-outlet pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- [`02e` — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md)

Their original detailed records are retained as [compatibility snapshots](../../../compatibility-snapshots/index.md) so no execution history is lost during the structural migration.

## Results

Numerical evidence remains separate from setup definitions:

- [Steady liquid-outlet report index](../../../reports/full-geometry/mixture/steady-liquid-outlet/index.md)

## Scientific role

`02c` provides the unprimed pressure-outlet control. `02e` adds a common Y010 liquid initialization and compares outlet formulations/resistance. Together they generated the screening evidence that motivated the transient successor.

These steady studies do not establish that a particular outlet formulation is physically correct.

## Successor

The direct successor is [Mixture transient liquid-outlet characterization](../transient-liquid-outlet/index.md), not a new global numbered setup.
