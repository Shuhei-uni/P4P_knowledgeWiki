# P7-E2-OV-K010 — conditional fourth outlet-vent screen at K=10

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | discovery short screen |
| Candidate/origin | E2-OV conditional fourth branch; Phase Loop activation from CONTEXT.md on 2026-09-09 |
| Authority/gate | Human-approved bounded fourth rule recorded in CONTEXT.md; G1 recovery |
| Parent | Exact save/reopen-proven P7-E0-REF initialized iteration-0 case/data pair |
| Controlled delta | bottom becomes outlet vent at 1.120 MPa gauge, constant normal-velocity loss coefficient K=10 |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

## Selection rationale and limits

K=7 completed its declared screen but left the upper-edge response unresolved:
inventory remains positively drifting, closure is non-small, and vapor loss remains
material. The K=10 branch is therefore the one named E2 fourth rule. A prior
full-geometry K=10 failure is collision context only; this case tests the
current truncated mesh and must not inherit its result.

Preserve every E0/E2 invariant and the same report/residual instrumentation.
Require F1 inventory versus E0, F2 phase routing/closure, and F3 numerical
adequacy. A solver failure is a bounded branch outcome, not a completed
comparison. No physical drainage, convergence, or plant-control claim is
permitted.

