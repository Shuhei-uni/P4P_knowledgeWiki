# Full Geometry — Mixture Steady Liquid-Outlet Reports

Corresponding setup campaign: [Mixture steady liquid-outlet setups](../../../../full-geometry/mixture/steady-liquid-outlet/index.md).

## Existing compatibility reports

These reports predate the geometry-first report hierarchy, so their source files remain in the numbered report folders to preserve existing links:

### 02c — unprimed pressure sensitivity

- [Early diagnostics](../../../02c/results.md)
- [Future-run notes retained in the old report folder](../../../02c/future-runs.md)

### 02e — Y010 outlet-boundary characterization

- [Stage-1 results](../../../02e/stage1-results-20260816.md)
- [Stage-1 execution record](../../../02e/stage1-execution-20260816.md)
- [275k retry notes](../../../02e/mesh-275k-retry-20260816.md)
- [275k retry results](../../../02e/stage1-results-275k-retry-20260816.md)

## Filing rule from now on

Any new steady full-geometry result report belongs directly in this folder with a descriptive filename. Do not create another numbered report directory for it.

## 03A Stage 2 — numerical-stabilisation screen

The branch-level records are written independently so that each case retains its own evidence and can be reviewed without waiting for the remaining branches:

- [N1 — reduced turbulence under-relaxation](03a-08b-stage2-N1-results.md)
- [N3 — first-order turbulence transport](03a-08b-stage2-N3-results.md)
- [N4 — first-order momentum and turbulence startup](03a-08b-stage2-N4-results.md)
- [N5 — standard-`k-epsilon` bootstrap and RNG return](03a-08b-stage2-N5-results.md)
- [Compact Stage-2 screening report](03a-08b-stage2-screening-report.md)

The consolidated report is currently provisional until the pending N4 endpoint readback and N5 +700 endpoint evidence are reconciled.
