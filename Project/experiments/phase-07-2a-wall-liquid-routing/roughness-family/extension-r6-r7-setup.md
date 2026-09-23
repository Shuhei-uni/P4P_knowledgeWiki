# Family R doubled-roughness extension: R6 and R7

Human request on 2026-09-23: add two setups by doubling roughness from the
latest R5 setting. R6 uses `k_s=4e-3 m`; R7 uses `k_s=8e-3 m`; both retain
`C_s=0.5`. These are fresh siblings from the exact native-5586 parent in
[baseline-control-handoff.md](../baseline-control-handoff.md), not continuations
from R5.

The question is whether further roughness changes the matched phase-2
`steamoutlet` response, and whether any reduction persists without further
liquid-inventory depletion or solver-health deterioration. R5's 20.58% lower
outlet magnitude accompanied a roughly 162 kg loss of domain liquid, so an
outlet reduction alone is not a positive separation result.

Freeze EWF off, mesh and materials, full-loading inlets, v2 absorber, bottom
walls, steam pressure outlet, steady Coupled/Global-Time-Step solver, and all
other parent settings. Apply roughness only to `separator-purnanto:1`,
`separator-purnanto:1:001`, `wall`, and `wall:004`. Require wall-value readback,
prepared save/reopen, and unchanged-model audit before compute. If Fluent
rejects either value or the wall treatment is not cleanly represented, record
a capability block; do not substitute another physics or numerical change.

Use one native `/solve/iterate 3000` command per child, offsets 0–3000 from
parent iteration 5586, with native-frequency-1 reports, paired server-local
autosaves every 250 iterations, and paired local/durable finals. The decisive
evidence is (1) raw and tail-500 phase-2 outlet flux against R0–R5, (2) total
and lower-zone liquid inventory with whole-run and tail change, (3) vapor
outlet, absorber/source tracking and available closure ledger, and (4) full
residual/event histories. Preserve the no-slip wall velocity report for
protocol consistency but do not interpret it as wall-adjacent transport.

This is a response screen, not a physical roughness validation or deep
qualification. Large inventory depletion, non-closing source accounting, or
oscillatory/poor numerical behavior keeps a favorable outlet number
unqualified. No further roughness case is implied by this pair.
