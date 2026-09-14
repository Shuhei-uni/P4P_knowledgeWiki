# P7-E1-PO-P1160 — bottom pressure outlet at 1.160 MPa

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E1-PO`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate | [`G1`](../../CONTEXT.md); setup creation independently passed in [`phase-state.yaml`](../../phase-state.yaml) |
| Shared design | [`../design.md`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | Change only `bottom` from wall to pressure outlet at `1.160 MPa` gauge |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Use the same liquid-dominant backflow and outlet turbulence state as every E1
child. Preserve all E0 invariants and differ from P1120/P1200 only by bottom
gauge pressure.

Require the shared evidence package plus pressure readback, bottom phase flux,
normalized vapor loss, liquid inventory, balances, and native residuals. Use
F1–F3. Missing setup/history evidence is invalid; vapor-dominated improvement,
backflow-driven artifacts, worse buildup, or failure rejects this setting. No
physical drainage or convergence claim is permitted.

