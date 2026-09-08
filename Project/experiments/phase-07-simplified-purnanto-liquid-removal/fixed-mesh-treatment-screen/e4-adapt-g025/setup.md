# P7-E4-ADAPT-G025 — adaptive prescribed withdrawal, G=0.25

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Candidate/origin | `E4-ADAPT`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact valid `P7-E0-REF` iteration-500 case/data checkpoint |
| Controlled delta | Proven E3 bottom actuator controlled by shared normalized inventory law with `G=0.25` |
| Active horizon | 500 controller-active iterations; 50-iteration smoke; checkpoints active 50, 250, 500 |

Require valid positive `ΔMref = M_E0(1000)-M_E0(500)`. Every 50 active
iterations command `clamp(0.25 × 116.92 kg/s × e, 0, 146.15 kg/s)`, where
`e=max(0,(M-M*)/ΔMref)` and `M*=M_E0(500)`. Hold between updates.

E3 phase-specific capability must already be proven. Record every controller
input, requested/clamped command, saturation state, realized bottom liquid and
vapor flow, inventory, balances, residuals, checkpoints, and F1–F4. Invalid
normalization/capability blocks the case; cycling, saturation without benefit,
vapor-dominated removal, or numerical failure rejects it. This numerical
controller has no plant-level or convergence claim.

