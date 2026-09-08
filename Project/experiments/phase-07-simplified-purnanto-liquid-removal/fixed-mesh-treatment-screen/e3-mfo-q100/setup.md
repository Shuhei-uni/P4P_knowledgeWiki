# P7-E3-MFO-Q100 — prescribed withdrawal at 116.92 kg/s

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E3-MFO`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | Intended phase-specific bottom liquid withdrawal `116.92 kg/s` (`100%` nominal liquid inflow), nominal vapor target zero |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

The same hard phase-specific capability gate applies. This setting nominally
matches liquid inflow but does not predetermine realized phase routing or
inventory behavior. Preserve all E0/E3 invariants; require command/realization,
phase split, vapor loss, inventory, balance, residual, failure, artifact, and
F1–F3 evidence. A forced rate is not evidence of closure. No physical or
convergence claim is permitted.

