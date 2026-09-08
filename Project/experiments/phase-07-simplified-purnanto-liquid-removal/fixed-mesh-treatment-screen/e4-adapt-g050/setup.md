# P7-E4-ADAPT-G050 — adaptive prescribed withdrawal, G=0.50

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E4-ADAPT`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Controlled delta | Proven E3 bottom actuator controlled by shared law with `G=0.50` |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Use the exact E4 law and invariants in the shared design, with only gain changed:
`command=clamp(0.50 × 116.92 kg/s × e,0,146.15 kg/s)`. Require positive E0
normalization and proven phase-specific actuator capability.

Record every command/response, saturation, bottom liquid/vapor flow, inventory,
balances, residuals, artifacts, and F1–F4. Invalid prerequisites block;
vapor-dominated response, cycling, ineffective saturation, or numerical failure
rejects. No plant or convergence claim is permitted.

