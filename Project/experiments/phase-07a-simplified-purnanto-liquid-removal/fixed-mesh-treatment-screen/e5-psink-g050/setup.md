# P7-E5-PSINK-G050 — adaptive liquid-only sink, G=0.50

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E5-PSINK`; human-selected phase-selective H2 variant, approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Region | Frozen `separator-purnanto` fluid cells with centroids `0≤y≤0.10 m` |
| Controlled delta | Liquid-only mass/momentum sink using shared law with `G=0.50`; no vapor sink |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Use the identical E5 region, source formulation, normalization, update interval,
and bounds; only gain changes. Command
`clamp(0.50 × 116.92 kg/s × e,0,146.15 kg/s)`.

Require exact region/source proof and all command, realized source, saturation,
inventory, phase balance, residual, artifact, and F1–F4 evidence. Unaccounted
mass/momentum or vapor source blocks; unstable/ineffective response rejects.
No physical outlet or convergence claim is permitted.

