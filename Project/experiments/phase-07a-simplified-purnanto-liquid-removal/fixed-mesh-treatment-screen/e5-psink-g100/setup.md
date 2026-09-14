# P7-E5-PSINK-G100 — adaptive liquid-only sink, G=1.00

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E5-PSINK`; human-selected phase-selective H2 variant, approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Region | Frozen `separator-purnanto` fluid cells with centroids `0≤y≤0.10 m` |
| Controlled delta | Liquid-only mass/momentum sink using shared law with `G=1.00`; no vapor sink |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Use the identical E5 region/source and command
`clamp(1.00 × 116.92 kg/s × e,0,146.15 kg/s)`. Vary only gain.

Require exact fixed-region and integrated source proof, zero vapor source, every
controller update, realized mass/momentum removal, saturation, inventory,
phase balances, residuals, artifacts, and F1–F4. Unaccounted sources block;
high-gain cycling, saturation without benefit, or failure rejects. No physical
outlet or convergence claim is permitted.

