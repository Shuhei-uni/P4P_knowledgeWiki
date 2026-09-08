# P7-E2-OV-K007 — bottom outlet vent at K=7

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E2-OV`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | `bottom` becomes outlet vent at `1.120 MPa` gauge, constant `K=7`, function of normal velocity |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Preserve the same E2 formulation and all E0 invariants; only `K` differs. This
is the approved upper initial resistance below prior `K=10` failure context.
Require complete common/E2 histories, last-valid failure evidence, and F1–F3.
Do not treat a failed endpoint as comparable to a completed case or claim
physical drainage/convergence.

