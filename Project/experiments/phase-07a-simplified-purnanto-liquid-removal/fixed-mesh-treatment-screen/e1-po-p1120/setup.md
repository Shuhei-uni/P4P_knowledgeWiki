# P7-E1-PO-P1120 — bottom pressure outlet at 1.120 MPa

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` short screen |
| Candidate/origin | `E1-PO`; human-inspired H2 variant, human-approved 2026-09-08 |
| Gate | [`G1`](../../CONTEXT.md); setup creation independently passed in [`phase-state.yaml`](../../phase-state.yaml) |
| Shared design | [`../design.md`](../design.md) |
| Parent | Exact save/reopen-proven `P7-E0-REF` initialized iteration-0 case/data pair |
| Controlled delta | Change only `bottom` from wall to pressure outlet at `1.120 MPa` gauge |
| Horizon | 500 iterations including 50-iteration smoke; checkpoints 50, 250, 500 |

Use a liquid-dominant bottom backflow phase state and parent-consistent outlet
turbulence form. Preserve every E0 mesh, model, material, inlet, steam-outlet,
numerical, initialization, DPM-isolation, report, and residual invariant. This
is the pressure-equal passive anchor.

Required evidence is the complete shared package plus immediate/post-reopen
bottom boundary readback, bottom phase fluxes, normalized vapor loss, liquid
inventory, phase/mixture balances, and native residuals. F1–F3 in the shared
design are predeclared core figures. Missing setup proof or histories makes the
case invalid; vapor-dominated drainage, worse buildup, or numerical failure is
a rejection signal. The result cannot establish physical drainage or steady
convergence.

