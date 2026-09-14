# P7-E4-ADAPT-G100 — adaptive prescribed withdrawal, G=1.00

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E4-ADAPT`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Controlled delta | Proven E3 bottom actuator controlled by shared law with `G=1.00` |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Use `command=clamp(1.00 × 116.92 kg/s × e,0,146.15 kg/s)` with the same
proven E0 normalization, 50-iteration update interval, actuator, bounds, and
all E0/E4 invariants.

Require every controller/phase/inventory/balance/residual/artifact history and
F1–F4. Invalid normalization/capability blocks; high-gain cycling, saturation,
vapor-dominated removal, or failure rejects the setting. No plant or
convergence claim is permitted.

