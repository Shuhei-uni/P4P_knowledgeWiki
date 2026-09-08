# P7-E5-PSINK-G025 — adaptive liquid-only sink, G=0.25

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E5-PSINK`; human-selected phase-selective H2 variant, approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Region | Frozen `separator-purnanto` fluid cells with centroids `0≤y≤0.10 m` |
| Controlled delta | Liquid-only mass/momentum sink using shared adaptive law with `G=0.25`; no vapor sink |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Require positive E0 `ΔMref`. Command
`clamp(0.25 × 116.92 kg/s × e,0,146.15 kg/s)` every 50 iterations. Distribute
realized removal by local continuous-liquid mass and remove associated liquid
momentum consistently.

Before solve, prove fixed cell IDs/count/volume, activation liquid mass,
integrated mass/momentum source readback, and zero direct vapor source. Record
every command, realized source, saturation, inventory, phase balances,
residuals, artifacts, and F1–F4. Any unaccounted source/region drift blocks;
instability or ineffective/saturated response rejects. This deliberately
artificial sink supports no physical outlet or convergence claim.

