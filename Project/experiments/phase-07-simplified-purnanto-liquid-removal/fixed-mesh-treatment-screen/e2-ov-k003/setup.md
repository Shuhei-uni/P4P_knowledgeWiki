# P7-E2-OV-K003 — bottom outlet vent at K=3

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E2-OV`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | `bottom` becomes outlet vent at `1.120 MPa` gauge, constant `K=3`, function of normal velocity |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Preserve the same E2 formulation and all E0 invariants; only `K` differs from
K000/K007. Require exact readback, pressure drop/normal velocity, bottom phase
flux, vapor loss, inventory, balance, residual, failure, and artifact evidence
and F1–F3. No physical drainage or convergence claim is permitted.

