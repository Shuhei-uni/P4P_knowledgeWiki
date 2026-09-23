# E2.6 — combined EWF numerical controls and coupled solution

## Question

When applied together, do 10 film sub-iterations, maximum Courant `0.05`, a
fixed film timestep of `10e-6 s` (`1e-5 s`), and EWF Coupled Solution ON change
the cap-hit and failure progression seen in E2.1, E2.4, and E2.5?

This is a combined-control screen selected directly by the user. It does not
isolate each control's individual effect. The fixed-step mode disables adaptive
stepping; therefore the Courant value is set/read back at `0.05` as requested
but is inactive for time-step selection during this run.

## Parent and applied controls

Build a new case independently from the verified native-5586 parent in the
[baseline handoff](../../baseline-control-handoff.md). Retain E2.1's phase
accretion recipe, `0.3 m` exploratory maximum film thickness, the `1e-4 s`
initial-step value, and zero roughness. Apply these requested controls together:

- EWF film sub-iterations: `5 -> 10`;
- EWF maximum Courant: `0.25 -> 0.05`;
- adaptive film stepping: ON -> OFF, with fixed EWF Time-Step
  `timestep-max = 1e-5 s`;
- EWF Coupled Solution: OFF -> ON.

Require exact readback of the film material, phase-accretion mode, wall scope,
zero roughness, DPM erosion/accretion OFF, all four requested settings, and
unchanged native iteration `5586` before and after save/reopen.

## Run and evidence

Use the established steady continuation horizon of up to 3000 native
iterations (target 8586), with paired checkpoints every 250 iterations.
Create Fluent-native EWF report definitions for maximum/area-average film
thickness, total film mass, maximum film Courant, and the phase-accretion
quantities. Attach Report Files at every native iteration. Retain Fluent's
native flow residual history and EWF `h/u/v` residual message output each film
sub-iteration. Preserve the transcript, any final reports, and last valid
checkpoint on numerical failure. Compare cap-hit/FPE coordinates and
pre-divergence histories with E2.1, E2.4, and E2.5.

## Decision and claim limits

A later cap-hit or FPE is only a longer numerical response for this combined
setting. Because several controls change together and fixed stepping makes
Courant inactive, this run cannot attribute an outcome to any one control.
The `0.3 m` cap is an exploratory numerical limit; cap-hit and post-cap
divergence values do not establish physically credible thickness, stable film
transport, drainage, or reduced carryover.


## Observed result — 2026-09-23

The saved/reopened child read back all selected settings. Fluent ran from
native 5586, reached the `0.3 m` maximum-thickness cap at native 5760, and
raised an FPE at native 5765; the last complete Report File point is 5764.
All 26 configured native Report Files were recovered at every iteration. The
fixed film timestep remained `1e-5 s`; EWF sub-iteration messages show the
configured maximum of 10 was used in the unstable tail. Maximum film Courant
first exceeded `0.05` at 5673 and grew to infinity before the failure. This
Courant number was stored as requested but was inactive because adaptive
stepping was OFF.

By the cap-hit coordinate, maximum film thickness was `0.300000012 m`, while
area-weighted thickness was `0.000658 m`; by the last report point it was
`0.1825 m`. Film mass rose from `0.00232 kg` at 5587 to `30.96 kg` at 5760,
then to `8593.59 kg` at 5764. Those post-cap values are numerical runaway, not
credible film accumulation. EWF `h/u/v` residuals grew to approximately
`1e175`, `1e175`, and `1e172`; Fluent also reported AMG divergence in `k` and
`epsilon` before the FPE.

The combined setting delayed the cap by 110 native iterations and the FPE by
112 relative to E2.1. It hit the cap and failed 23 iterations later than E2.4,
but 258/257 iterations earlier than E2.5. Because this test combines several
controls, these differences do not identify which setting caused the changed
timing. See the [E2.6 result](../results.md#e26--combined-ewf-controls--2026-09-23),
[native report histories](../../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/e26-native-report-histories_20260923_190209.json),
[summary](../../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/e26-summary.json),
[native solve transcript](../../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/transcript-native-solve.txt),
and [monitoring figure](../figures/E2.6-combined-film-monitoring.png).
