# P7-E3-MFO-Q025 — prescribed withdrawal at 29.23 kg/s

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E3-MFO`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | `bottom` becomes intended phase-specific prescribed liquid withdrawal at `29.23 kg/s` (`25%` nominal liquid inflow), nominal vapor target zero |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Before build, live Fluent capability inspection must prove the intended phase-
specific command, readback, and phase-resolved realized flux. A total-mixture-
only substitute is forbidden. Preserve all E0 invariants and differ from other
E3 children only by command.

Require requested-versus-read-back command, realized bottom liquid/vapor flow,
vapor loss, inventory, balances, residuals, failure evidence, artifacts, and
F1–F3. Capability failure blocks the family; vapor-dominated removal,
instability, or uninterpretable conservation rejects the setting. No physical
or convergence claim is allowed.

