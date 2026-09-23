# E2.1 — Phase-accretion maximum-thickness sensitivity

## Question

Does increasing Fluent EWF's maximum film thickness limit from `0.01 m` to
`0.3 m` allow the accreting EWF calculation to continue past E2's rapid
thickness-limit event, and how do film thickness and accretion evolve while
it does?

This is a numerical-limit sensitivity selected after E2 reached the `0.01 m`
limit and diverged. The `0.3 m` value is an exploratory solver limit, not a
claim that a 0.3 m wall film is physically credible.

## Parent and controlled delta

- Authoritative parent: verified Phase 7.1A R0 terminal case/data pair at
  native iteration `5586`; use the exact hashes and paths in
  [baseline handoff](../../baseline-control-handoff.md).
- Build an independent EWF child from that parent with the E2 phase-accretion
  recipe: water-liquid-at-psep film material, EWF active on `wall`, phase
  accretion enabled, zero wall roughness, initial film time step `1e-4 s`,
  five film sub-iterations, and the existing film momentum settings.
- Single controlled delta from E2: `thickness-limit = 0.3 m` (E2 used
  `0.01 m`). Preserve all other model, boundary, mesh, operating, absorber,
  and solver settings.
- Do not resume from the failed E2 or time-step-recovery solve. Neither has a
  valid post-failure checkpoint.

## Run and monitoring

- Fluent 2025 R2, steady continuation, up to `3000` native iterations from
  native `5586` (target `8586`).
- Native report definitions and file-backed reports on film wall `wall` at
  every native iteration:
  maximum and area-weighted film thickness, total film mass, phase-2 film
  mass/collection, film outflow, film velocity, and maximum film Courant.
- Continue the Family E phase reports for outlet phase fluxes, liquid
  inventory, absorber command/removal, closure, and solver residual/event
  evidence at their existing cadence.
- Paired Fluent-local checkpoints at offsets `0`, `250`, `500`, `750`, and
  each subsequent `250` through `3000`; preserve the first failure iteration,
  last report sample, and last valid checkpoint if Fluent fails.
- Required review: plot maximum and area-weighted film thickness and film mass
  against native iteration, retaining raw samples; align the thickness-limit
  value and solver-event markers. Also inspect phase-2 `steamoutlet` flux,
  phase-2 collection, film outflow, closure, and residual/event histories.

## Decision and limits

- If the run passes the former E2 failure region, use its complete monitored
  history to identify whether the thickness cap was the immediate trigger and
  whether accretion remains numerically controlled. This alone does not
  establish physical plausibility, drainage, or reduced carryover.
- If it again diverges, preserve the last valid checkpoint and film history;
  distinguish a new thickness-limit event from an earlier instability.
- A completed 3000-iteration continuation is a discovery result only, not a
  steady-state or physical validation claim.

## Executed result — 2026-09-23

The prepared/reopened child passed its `0.3 m` thickness-limit readback at
native 5586. The 3000-iteration continuation stopped at native 5653 with
AMG divergence and a floating-point exception, before the first scheduled
250-iteration checkpoint. The maximum film thickness reached `0.3 m` at
5650. Native Report Files were set to one sample per iteration; all 26 active
files were recovered with 67 samples apiece, covering native 5586–5652.
The recovered histories and event summary are preserved in the [native
report histories](../../../../../PyAnsys/output/phase72a_ewf_student_e21_run_20260923T052000Z/E2.1/e21-native-report-histories_20260923_173131.json)
and [summary](../../../../../PyAnsys/output/phase72a_ewf_student_e21_run_20260923T052000Z/E2.1/e21-summary.json);
the visual review is in [E2.1 iteration monitoring](../figures/E2.1-native-iteration-monitoring.png).

This result does not establish whether phase accretion would remain stable
above the cap. The terminal film mass, average thickness, and Courant values
are contaminated by divergence. No checkpoint beyond the prepared parent
exists.
