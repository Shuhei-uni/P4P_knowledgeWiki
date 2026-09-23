# E2.2 — phase-accretion sub-iteration recovery

## Question

With the E2.1 `0.3 m` maximum film thickness held fixed, does increasing EWF
film sub-iterations from 5 to 20 prevent the rapid film/Courant growth and
numerical failure observed near native iteration 5650?

This is a numerical recovery comparison. It does not test physical credibility
of a film approaching the configured `0.3 m` cap.

## Parent and controlled delta

- Build independently from the verified Phase 7.1A R0 terminal case/data pair
  at native iteration `5586`, using the parent hashes and paths in the
  [baseline handoff](../../baseline-control-handoff.md).
- Retain E2 phase accretion, `water-liquid-at-psep`, EWF active on `wall`, zero
  roughness, initial film time step `1e-4 s`, and maximum film thickness
  `0.3 m` as in E2.1.
- Change only EWF film sub-iterations from `5` to `20`.
- Preserve the mesh, flow settings, boundaries, materials, solver, source,
  and absorber state. Do not continue from either failed E2.1 or E2 checkpoint.

## Run and evidence

- Fluent 2025 R2; up to 3000 steady native iterations from 5586 (target 8586).
- Use native Report Files at frequency `1` for maximum and area-weighted film
  thickness, total film mass, phase-2 film mass and collection, film outflow,
  film velocity, and maximum film Courant. Keep the Family E reports for
  phase-resolved outlet flux, liquid inventory, absorber command/removal,
  closure, and native solver event/residual evidence.
- Save paired local checkpoints every 250 native iterations. If the run
  blocks, preserve the first failure iteration, all complete report-file
  samples, and the latest valid paired checkpoint.
- First inspect thickness/Courant/mass around 5649–5653. If these stay finite,
  continue assessment across the declared run horizon; do not infer drainage
  or reduced carryover without interpretable transfer, routing, and closure
  evidence.

## Claim limits

A run that passes the former failure region only supports that this numerical
setting delayed or avoided the observed early failure for the tested window.
It does not establish steady state, physical thickness credibility, wall-film
closure, drainage, or improved outlet carryover.
