# E2.7 — phase accretion with flow momentum coupling off

## Question

With the E2.6 settings held fixed, does disabling Flow Momentum Coupling on
the film wall change the cap-hit or numerical-failure progression while EWF
phase accretion remains enabled?

Fluent defines Flow Momentum Coupling as two-way exchange between the film and
bulk flow; clearing it leaves one-way coupling, where the gas flow affects the
film but film flow does not feed back on the bulk flow ([Fluent 2025 R2
Boundary Conditions task page](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_boundary_conditions_task_page.html)).
The separate EWF Coupled Solution option remains ON; it controls the numerical
solution of film continuity and momentum equations. Phase Accretion remains
enabled (`secondary-phase-mode = 1`) so secondary-phase liquid can still
transfer into the film.

## Parent and controlled delta

Build independently from the same verified native-5586 parent as E2.6. Retain
the phase-accretion setup, zero roughness, `0.3 m` exploratory thickness cap,
10 maximum film sub-iterations, Courant `0.05`, adaptive stepping OFF, fixed
film timestep `1e-5 s`, and EWF Coupled Solution ON. Change only the film wall's
`enable_flow_momentum_coupling` setting from ON to OFF. Require readback before
and after save/reopen that this wall setting is OFF, the bottom is not a film
wall, phase accretion remains enabled, and all E2.6 controls persist.

## Run and evidence

Use the same steady continuation horizon of up to 3,000 native iterations
(target 8586) and paired local checkpoints every 250 iterations. Retain Fluent
native Report Definitions and Report Files at every iteration for film
thickness, total film mass, maximum film Courant, phase-accretion quantities,
and existing flow/closure monitors. Retain native flow residual history and
EWF `h/u/v` residual messages at every film sub-iteration. Compare directly
with E2.6, with the wall Flow Momentum Coupling toggle as the sole intended
case difference.

## Decision and claim limits

Report cap and FPE coordinates, pre-divergence film histories, and solver
events. Because the fixed timestep disables adaptive selection, Courant `0.05`
is retained for readback but does not limit the timestep. A later failure is
only a longer numerical response. A cap hit and post-cap values cannot
establish credible film thickness, film mass, stable transport, drainage, or
reduced outlet carryover. Any difference from E2.6 is attributable only to the
boundary Flow Momentum Coupling change within this numerical setup; it does not
qualify the physical model.


## Observed result — 2026-09-23

The build receipt confirms Flow Momentum Coupling OFF, Phase Accretion ON, and
EWF Coupled Solution ON after save/reopen. The 3,000-iteration continuation
completed from native 5586 through 8586. All 26 Fluent-native Report Files
were recovered with per-iteration data (3,001 points each); the run raised no
FPE, AMG, nonfinite, or fatal event. Reverse flow and turbulent-viscosity
limiting remained present.

Maximum film thickness peaked at `0.0003310 m` and terminal area-weighted
thickness was `0.00006607 m`; reported film mass peaked at `3.111 kg`. In
native 7590–8580, maximum thickness ranged `0.000297–0.000328 m`, while film
mass rose from `2.149` to `3.106 kg`. This is a small film response compared
with the exploratory `0.3 m` cap, but the rise means the window is not shown
to be stationary. Over the same window, phase-2 `steamoutlet` signed flux
averaged `-1.7361 kg/s` (outflow), liquid inventory averaged `63.03 kg`, and
absorber removal averaged `98.23 kg/s` versus its `116.92 kg/s` command. These
results do not establish converged film transport, closure, stable carryover,
or a physical carryover benefit. Courant `0.05` remained a stored setting,
not a timestep limiter, because adaptive stepping was OFF.

The E2.6/E2.7 comparison at native 5760 is shown in
[results](../results.md#e27--flow-momentum-coupling-off--2026-09-23) and
[figure](../figures/E2.6-E2.7-flow-momentum-coupling-comparison.png). Machine
evidence: [build receipt](../../../../../PyAnsys/output/phase72a_ewf_student_e27_build_20260923T071523Z/probe-receipt.json),
[native reports](../../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/report-histories.json),
[summary](../../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/e27-summary.json),
and [run manifest](../../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/run-manifest.json).
