# P7-E3-MFO-Q14615 — conditional fourth prescribed withdrawal at 146.15 kg/s

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | discovery short screen |
| Candidate/origin | E3-MFO conditional fourth branch; Phase Loop activation from CONTEXT.md on 2026-09-09 |
| Authority/gate | Human-approved bounded fourth rule recorded in CONTEXT.md; G1 recovery |
| Parent | Exact save/reopen-proven P7-E0-REF initialized iteration-0 case/data pair |
| Controlled delta | phase-specific bottom mass-flow-outlet command: phase-1=0, phase-2=146.15 kg/s |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

## Selection rationale and limits

Q025, Q050, and Q100 completed with phase-specific readback. Q100 has near-zero
mean mixture imbalance and near-zero vapor loss but retains a positive inventory
slope, so the approved upper-edge branch is unresolved. The 146.15 kg/s value
is the context cap, not a plant setpoint.

Preserve all E0/E3 invariants and the live phase-specific capability proof.
Require F1 inventory versus E0, F2 phase routing/closure, and F3 numerical
adequacy. Prescribed-rate closure remains a diagnostic boundary-condition
identity; no physical drainage, plant, or convergence claim is permitted.

