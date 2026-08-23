# Full Geometry — Mixture Steady Liquid-Outlet Setup Campaign

This is the canonical setup-side home for the full-geometry steady Mixture investigation of the physical brine outlet and retained lower-vessel liquid.

## Canonical setup definitions

- [`02c` — unprimed brine-outlet pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- [`02e` — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md)
- [`03A` — 08b-parity full-geometry steady Mixture baseline](03a-08b-parity-full-geometry-baseline.md) — **draft / parity preflight required before run**
- [`03A Stage 4` — promising-state development](03a-stage4-promising-state-development.md) — **active long-continuation/model-form comparison**
- [`03B` — same-field brine-pressure continuation](03b-brine-pressure-continuation.md) — **draft / starts only from a usable 03A endpoint**

Their original detailed records are retained as [compatibility snapshots](../../../compatibility-snapshots/index.md) so no execution history is lost during the structural migration.

## Results

Numerical evidence remains separate from setup definitions:

- [Steady liquid-outlet report index](../../../reports/full-geometry/mixture/steady-liquid-outlet/index.md)

## Scientific role

`02c` and `02e` are retained as historical evidence showing that the physical brine outlet and its pressure strongly affect liquid retention, phase routing, and numerical behaviour. They are **not** the setup authority for the `03` family.

### 03A — baseline

`03A` resets the full-geometry steady investigation onto the trusted `08b` / audited-Purnanto carrier lineage:

```text
08b Purnanto-parity steady carrier setup
+ current full separator geometry
+ physical brine pressure outlet at 1.120 MPa
```

The baseline keeps the `08b` split pure-phase inlet and audited Purnanto solver/model/numerics stack, uses Hybrid Initialization with no liquid patch, and treats the new brine outlet as the principal physical difference from the simplified Purnanto carrier problem.

`FG-MIX-T01-S1-C1375` and the previous pressure-screen descendants remain evidence only; they do not define `03A` turbulence, materials, numerics, relaxation factors, initialization, or Mixture settings.

### 03B — continuation

Once `03A` has produced a numerically useful developed field, `03B` changes only brine-outlet pressure **within that same steady solution**:

```text
1.120 MPa parent
→ 1.125 MPa
→ 1.130 MPa
→ 1.135 MPa
→ 1.1375 MPa
→ adaptive refinement as required
```

There is no Hybrid Initialization between these pressure levels. Each pressure begins from the previous developed checkpoint. This is steady numerical continuation, not a physical transient pressure ramp.

The purpose is to follow the steady branch toward a condition where liquid inventory and outlet phase fluxes approach a plateau, rather than repeating the independent pressure-case approach used in `02c` / `02e`.

If a pressure increment fails, restore the last stable checkpoint and reduce the pressure increment before concluding that the branch itself has ended.

## Transient branch

The [Mixture transient liquid-outlet characterization](../transient-liquid-outlet/index.md) remains part of the campaign history, but further transient development is paused while `03A` and `03B` establish whether a defensible full-geometry steady carrier branch can first be obtained.
