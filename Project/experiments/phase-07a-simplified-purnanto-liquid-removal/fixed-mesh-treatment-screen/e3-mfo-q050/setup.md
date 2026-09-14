# P7-E3-MFO-Q050 — prescribed withdrawal at 58.46 kg/s

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E3-MFO`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | Intended phase-specific bottom liquid withdrawal `58.46 kg/s` (`50%` nominal liquid inflow), nominal vapor target zero |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

The same hard phase-specific Fluent capability gate applies as Q025. Preserve
all E0 and E3 invariants; vary only withdrawal command. Require full command/
realization, liquid/vapor routing, inventory, balance, residual, failure,
artifact, and F1–F3 evidence. No total-mixture substitution, physical claim,
or convergence claim is permitted.

