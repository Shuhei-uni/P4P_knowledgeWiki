# Setup 02e — Mixture Y010 Brine-Outlet Boundary Characterization

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Legacy setup ID | `02e` |
| Lifecycle | `active` |
| Investigation mode | exploratory / outlet-family sensitivity |
| Parent | [02c — unprimed pressure sensitivity](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md) |
| Production mesh | `Full-geomV2-231kcells.msh.h5` |
| Fixed initialization | Y010 lower-region liquid patch after Hybrid Initialization |
| Detailed frozen source | [02e compatibility snapshot](../../../compatibility-snapshots/02e-mixture-y010-brine-outlet-boundary-characterization.md) |
| Stage-1 evidence | [Stage-1 results](../../../reports/full-geometry/mixture/steady-liquid-outlet/02e/stage1-results-20260816.md) |
| Stage-2 evidence | [Stage-2 results](../../../reports/full-geometry/mixture/steady-liquid-outlet/02e/stage2-results-20260816.md) |

## Intent

Characterize how built-in Fluent brine-outlet formulations affect drainage, vapour leakage, lower-vessel liquid inventory, and brine-pipe pressure when every case starts from the same initialized Y010 liquid inventory.

The controlled comparison preserves the production mesh, steady Mixture model, RNG `k-epsilon`, gravity, split velocity inlets, steam outlet, materials, spatial numerics, and common Y010 parent. Outlet formulation and its primary control parameter are the intended experimental changes.

## Campaign structure

- **Stage 1:** coarse three-point pilots for Pressure Outlet, Outlet Vent, Mass-Flow Outlet, and Exhaust Fan.
- **Stage 2:** targeted refinement of the Pressure Outlet and Outlet Vent families selected from the Stage-1 evidence.
- **Successor:** the full-geometry [Mixture transient liquid-outlet campaign](../transient-liquid-outlet/index.md), which re-tests the most informative retention regimes using a qualified transient method.

The detailed source snapshot remains the authority for the exact Y010 register, initial inventory, case matrix, monitor definitions, Fluent build/readback requirements, run budget, and historical execution notes.

## Interpretation contract

This is coarse experimental characterization. The steady evidence does not establish convergence, physical correctness, an optimum outlet formulation, or an operating point. Numerical evidence is kept in the mirrored report tree; interpretation remains user-led.
