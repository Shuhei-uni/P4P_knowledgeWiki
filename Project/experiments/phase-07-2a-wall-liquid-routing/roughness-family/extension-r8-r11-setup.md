# Family R roughness-constant sensitivity: R8–R11

Human-selected extension on 2026-09-23. Test the roughness constant at two
levels on the existing R3 and R5 roughness heights:

| Case | `k_s` (m) | `C_s` | Status |
| --- | ---: | ---: | --- |
| R8 | `5e-4` (R3 height) | `0.75` | complete |
| R9 | `5e-4` (R3 height) | `1.0` | complete |
| R10 | `2e-3` (R5 height) | `0.75` | complete |
| R11 | `2e-3` (R5 height) | `1.0` | complete |

All four are fresh siblings from the exact native-5586 parent identified in
[baseline-control-handoff.md](../baseline-control-handoff.md), not continuations
from R3 or R5. The only physical delta from that parent is outer-wall roughness
height and roughness constant on `separator-purnanto:1`,
`separator-purnanto:1:001`, `wall`, and `wall:004`.

Freeze EWF off, mesh/materials, full-loading inlets, v2 absorber, bottom walls,
steam pressure outlet, and steady Coupled / Global-Time-Step numerics. Require
wall-setting readback, unchanged-model audit, report-definition setup, and
prepared save/reopen before compute. For each case issue one native TUI
`/solve/iterate 3000` command. Record native-frequency-1 histories, paired
server-local autosaves every 250 iterations, local and durable final pairs,
phase-resolved steamoutlet flux, total/lower liquid inventory, absorber and
source tracking, available closure, residuals, and solver events.

This is a roughness-constant sensitivity screen. Compare each result with its
matched-height `C_s=0.5` R3 or R5 result. Outlet reduction alone is not a
separation improvement; interpret it alongside inventory change, closure,
vapor routing, and numerical health. No physical roughness validation or
steady-convergence claim follows from this 3000-iteration screen.
