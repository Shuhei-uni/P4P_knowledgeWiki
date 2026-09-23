# E2.3 — reduced initial film time step

## Question

With the E2.2 `0.3 m` maximum film thickness and 20 film sub-iterations
retained, does reducing the initial EWF film time step from `1e-4 s` to
`1e-6 s` change the rapid thickness/Courant growth and FPE sequence near
native iteration 5650?

This is a numerical recovery probe. It does not make the `0.3 m` film limit a
physically meaningful target.

## Parent and controlled delta

- Build independently from the verified Phase 7.1A R0 terminal case/data pair
  at native iteration `5586`, using the parent hashes and paths in the
  [baseline handoff](../../baseline-control-handoff.md).
- Retain E2 phase accretion, `water-liquid-at-psep`, EWF active on `wall`, zero
  roughness, 20 film sub-iterations, and maximum film thickness `0.3 m` as in
  E2.2.
- Change only initial film time step from `1e-4 s` to `1e-6 s`.
- Preserve all remaining mesh, flow, boundary, material, solver, source, and
  absorber settings. Do not resume from a failed E2-series run.

## Run and evidence

- Fluent 2025 R2; up to 3000 steady native iterations from 5586 (target 8586).
- Configure native Report Files at frequency `1` for maximum and
  area-weighted film thickness, total film mass, phase-2 film mass and
  collection, film outflow, film velocity, and maximum film Courant. Preserve
  Family E outlet, inventory, absorber, closure, and numerical-health reports.
- Save paired local checkpoints every 250 native iterations. If the run
  blocks, preserve its failure iteration, all complete report-file samples,
  and latest valid pair.
- Compare the history with E2.2 on the shared native-iteration coordinates,
  focusing on 5649–5653 first. Do not claim drainage, steady behaviour, or
  reduced carryover from an early numerical recovery alone.

## Claim limits

Passing the previous failure region would only show that the tested numerical
setting delayed or avoided the specific early failure for that interval. It
would not validate the very large film thickness, establish steady state, or
demonstrate film drainage or reduced outlet carryover.

## Executed result — 2026-09-23

The prepared child passed save/reopen at native 5586 with `adapt-init-dt =
1e-6 s`, `sub-iter-nums = 20`, and `thickness-limit = 0.3 m`. The 3000-iteration
continuation stopped at native 5653 with AMG divergence and an FPE before a
scheduled checkpoint. All 26 active native Report Files were configured at
frequency `1` and recovered with 67 samples each for native 5586–5652. See
the [raw report histories](../../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e23-native-report-histories_20260923_180234.json),
[comparison data](../../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e21-e23-aligned-film-history.csv),
[summary](../../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e23-summary.json), and [figure](../figures/E2.1-E2.3-iteration-monitoring.png).

The maximum film thickness reached the `0.3 m` cap at 5647, earlier than the
5650 cap hit in E2.1/E2.2. The lower initial film time step did not prevent or
delay the FPE. There is no post-parent checkpoint. E2.3 and further numerical
recovery runs are stopped as requested.
