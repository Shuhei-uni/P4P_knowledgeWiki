# E2.5 — fixed EWF film time step

## Question and controlled delta

Does a fixed EWF film time step of `1e-6 s` change the onset or progression of
the E2.1 film-thickness growth and numerical failure?

Build independently from the verified native-5586 parent in the [baseline
handoff](../../baseline-control-handoff.md), using the E2.1 phase-accretion
recipe and `0.3 m` exploratory thickness limit. Disable adaptive film time
stepping and set Fluent's fixed EWF `Time-Step` (`timestep-max` in the live
model-parameter readback) to `1e-6 s`. Keep all other E2.1 settings, including
five film sub-iterations, unchanged. Verify the fixed/adaptive flags and step
size in the saved-and-reopened case before solving.

## Run and evidence

Use the existing steady continuation envelope (up to 3000 native iterations,
target 8586), saving paired checkpoints at the configured 250-iteration
interval. Create Fluent-native EWF report definitions for maximum and
area-average film thickness and total film mass, then attach native Report
Files at every iteration. Keep the maximum film Courant and E2 phase-accretion
reports too. Enable Fluent's native residual monitors and save/print their
history each iteration so EWF residuals are visible alongside the film
reports. Compare aligned histories with E2.1 to identify changes in cap-hit and
failure coordinates. Record only the pre-divergence evidence as interpretable.

## Interpretation limit

The `0.3 m` limit is an exploratory numerical ceiling, not a physically
credible target. A changed failure coordinate does not establish stable film
transport or reduced liquid carryover.

## Executed result — 2026-09-23

The saved-and-reopened case confirmed adaptive film stepping OFF and the fixed
EWF `Time-Step` at `1e-6 s`. The `0.3 m` cap, five sub-iterations, and native
EWF residual message output at every film sub-iteration were verified. All 26
native Report Files, including the EWF thickness and mass reports, were
configured at every iteration and recovered from the failed run.

Maximum thickness first reached `0.3 m` at native `6018`; Fluent failed with
FPE at `6022`, with the last complete reports at `6021`. Relative to E2.1's
cap at `5650` and FPE at `5653`, the fixed-step case delayed the cap by 368
iterations and the FPE by 369. It delayed instability further than E2.4 but
did not prevent the cap or FPE. EWF `h/u/v` residuals eventually rose to about
`1e210`–`1e215`, and the maximum Courant report became enormous near failure.
Values after the cap are divergence evidence, not physically meaningful film
thickness or mass.

See the [native every-iteration report histories](../../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/e25-native-report-histories_20260923_183617.json),
[summary](../../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/e25-summary.json),
and [native solve transcript](../../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/transcript-native-solve.txt).
E2.5 is a longer numerical response than E2.1/E2.4 in this observed run, but
it still does not establish stable film transport or reduced carryover.
