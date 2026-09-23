# Family R stronger-roughness extension: R4 and R5

Human decision on 2026-09-23: test two rougher surfaces after R1–R3 returned
toward the smooth-control response at the strongest tested setting. This is a
partial repeat of the same wall-roughness mechanism with a new controlled
range, not a continuation from R3.

## Scientific test

Question: does increasing the intended outer-wall sand-grain roughness beyond
`5e-4 m` reduce the magnitude of phase-2 liquid flux through `steamoutlet`
relative to the matched R0 control? R4 uses `k_s=1e-3 m`; R5 uses
`k_s=2e-3 m`; both use `C_s=0.5` and EWF off.

Use the exact 5586 case/data pair and hashes in
[baseline-control-handoff.md](../baseline-control-handoff.md) as the fresh
parent for each child. Preserve the mesh, 60k v2 virtual-outlet geometry,
steady Coupled/Global-Time-Step scaffold, full-loading inlets, phase-2
absorber, steam pressure outlet, bottom walls, materials, and all other
settings. Apply roughness only to `separator-purnanto:1`,
`separator-purnanto:1:001`, `wall`, and `wall:004`. No initialization, patch,
inlet ramp, or solver adjustment.

Run exactly one native Fluent `/solve/iterate 3000` command per case from
5586 to 8586. Keep report files at frequency 1, paired server-local autosaves
every 250 iterations, and local and durable final case/data pairs. Save and
reopen each prepared child before compute, then verify each final pair after
the solve.

## Predeclared evidence and decision

1. R4/R5/R0 phase-2 `steamoutlet` mass flux (kg/s, Fluent signs retained)
   over offsets 0–3000, with raw traces and tail-500 mean, spread, and slope.
   Reduced magnitude in either roughness child is the primary positive signal.
2. Total and lower-zone liquid mass (kg) over the same window, with tail-500
   slopes and raw oscillation, to distinguish outlet change from inventory
   redistribution or continuing storage.
3. Absorber command, applied removal, command error, phase-resolved inlet and
   outlet fluxes, and source-inclusive closure, using native report histories.
   A carryover change with worsened source accounting is qualified accordingly.
4. Full residual traces, reverse-flow and viscosity-limit event counts, and
   fatal/AMG/FPE/nonfinite checks. Final hashes and paired checkpoint inventory
   prove execution durability.

The no-slip wall-surface liquid velocity report from R0–R3 is retained for
protocol consistency but cannot establish wall-adjacent transport. No claim of
plant-scale drainage, physical wall-scale validity, or absolute mass closure
follows from a favorable outlet response alone. Reassess Family R after both
cases; do not infer an additional run from this extension.
