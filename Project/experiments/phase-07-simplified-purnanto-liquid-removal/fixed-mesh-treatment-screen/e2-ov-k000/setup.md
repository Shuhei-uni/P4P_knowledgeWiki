# P7-E2-OV-K000 — bottom outlet vent at K=0

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E2-OV`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate/design | [`G1`](../../CONTEXT.md); [`shared design`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | `bottom` becomes outlet vent at `1.120 MPa` gauge discharge pressure, constant `K=0`, function of normal velocity |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Use the approved liquid-dominant backflow basis and preserve all E0 invariants.
This is the zero-added-resistance E2 anchor and should be compared explicitly
with E1 P1120 without assuming equivalence.

Require common evidence plus loss/discharge-pressure readback, normal velocity,
pressure drop, bottom phase flux, vapor loss, inventory, balances, residuals,
and F1–F3. Unaccounted formulation drift, vapor-dominated drainage, reversal,
or numerical failure invalidates/rejects only as defined by G1. No physical or
steady claim is permitted.

