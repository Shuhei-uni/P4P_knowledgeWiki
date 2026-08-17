# Full Geometry — Mixture Steady Liquid-Outlet Setup Campaign

This is the canonical setup-side home for the full-geometry steady Mixture investigation of the physical brine outlet and retained lower-vessel liquid.

## Canonical setup definitions

- [`02c` — unprimed brine-outlet pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- [`02e` — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md)
- [`03` — 08b-parity full-geometry steady Mixture with brine outlet](03-mixture-steady-solution-qualification.md) — **draft / parity preflight required before run**

Their original detailed records are retained as [compatibility snapshots](../../../compatibility-snapshots/index.md) so no execution history is lost during the structural migration.

## Results

Numerical evidence remains separate from setup definitions:

- [Steady liquid-outlet report index](../../../reports/full-geometry/mixture/steady-liquid-outlet/index.md)

## Scientific role

`02c` and `02e` are retained as historical evidence showing that the physical brine outlet and its pressure strongly affect liquid retention, phase routing, and numerical behaviour. They are **not** the setup authority for `03`.

`03` resets the full-geometry steady investigation onto the trusted `08b` / audited-Purnanto carrier lineage. Its intended baseline is:

```text
08b Purnanto-parity steady carrier setup
+ current full separator geometry
+ physical brine pressure outlet
```

The baseline therefore keeps the `08b` split pure-phase inlet and audited Purnanto solver/model/numerics stack, uses Hybrid Initialization with no liquid patch, and treats the new brine outlet as the principal physical difference from the simplified Purnanto carrier problem.

`FG-MIX-T01-S1-C1375` and the previous pressure-screen descendants remain useful evidence but do not define `03` turbulence, materials, numerics, relaxation factors, initialization, or Mixture settings.

The first goal is to determine whether the `08b`-parity carrier solution can remain steady after the full lower vessel and brine discharge are restored. Only after that baseline is understood should brine backpressure, outlet resistance, liquid retention, or transient stabilization be varied.

## Transient branch

The [Mixture transient liquid-outlet characterization](../transient-liquid-outlet/index.md) remains part of the campaign history, but further transient development is paused while `03` establishes the full-geometry steady carrier baseline.
