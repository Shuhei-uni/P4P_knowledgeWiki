# 03A Stage 4 — setup

## Question

Can a promising Stage-3 state sustain bounded residuals, low and stable mass imbalance, bounded liquid inventory, and sensible phase routing over a common long continuation?

Stage 4 tests whether more iteration, turbulence-model form, or loading path is the main remaining limitation. It is diagnostic/model-development work, not a convergence or validation declaration.

## Parent states and controlled deltas

S4-01 through S4-05 each cold-load an exact Stage-3 case/data parent independently. S4-06 is intentionally different: it is a dependent continuation from a successfully verified, developed S4-05 40% state and must not be treated as an independent Stage-3-parent branch.

| Branch | Exact parent | Controlled delta | Budget |
|---|---|---|---:|
| S4-01 | F05 100% endpoint at cumulative 3,000 | none; long continuation | `+30,000` |
| S4-02 | F06 100% endpoint at cumulative 6,000 | none; long continuation | `+30,000` |
| S4-03 | F11 100% endpoint at cumulative 15,000 | none; long continuation | `+30,000` |
| S4-04 | F11 100% endpoint at cumulative 15,000 | RNG → standard `k-epsilon` only | `+30,000` |
| S4-05 | exact F09 40% endpoint | hold 40% unchanged | `+30,000` |
| S4-06 | developed S4-05 40% state | 50 → 60 → 70 → 80 → 90 → 100% loading | `30,000 total` |

S4-05 and S4-06 are gated until the exact F09 40% parent is accessible and checksum/readback verified. S4-06 cannot start from the short Stage-3 40% checkpoint.

## Frozen comparison context

- Fluent 2025 R2, 3D double precision, steady pressure-based Mixture model;
- exact Stage-3 parent case/data identity read back before preparation;
- all inherited physical and numerical settings held fixed for S4-01/02/03;
- S4-04 changes only the turbulence-model form to standard `k-epsilon`;
- no reinitialization between parent load and the continuation;
- Fluent native journals own iteration, autosave, residual, monitor, transcript, and endpoint evidence.

The common `+30,000` budget is measured from each branch's own parent, not from a shared absolute iteration. This makes continuation length comparable without making absolute cumulative iteration another factor.

## Evidence package

Each branch must record, wherever Fluent permits, the same cumulative histories:

- all scaled residuals;
- total, liquid-phase, and vapour-phase inlet/outlet fluxes;
- total, Y010, and Y030 liquid inventory;
- total mass imbalance and phase-balance inputs;
- brine-entry static/total pressure and outlet-flow reversal indicators.

Interpret full history and consistent windows (`0–5k`, `5–10k`, `10–20k`, and especially `20–30k`). Report mean/median, P95 or spread, slope, and useful extrema. No endpoint alone establishes stationarity.

## Execution boundary

The setup defines intent and required evidence only. Live execution status belongs in [Stage-4 results](results.md). A branch is not parent-eligible until paired-file completeness, checksum/readback, and physical-history analysis are complete.

## Source

[Original Stage-4 setup authority](../../../../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage4-promising-state-development.md)
