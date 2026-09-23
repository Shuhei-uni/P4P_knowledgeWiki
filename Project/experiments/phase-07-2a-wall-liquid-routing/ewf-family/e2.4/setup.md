# E2.4 — lower adaptive film Courant number

## Question and controlled delta

Does lowering the adaptive EWF maximum Courant number from `0.25` to `0.05`
change the onset or progression of the E2.1 film-thickness growth and numerical
failure?

Build independently from the verified native-5586 parent in the [baseline
handoff](../../baseline-control-handoff.md), using the E2.1 phase-accretion
recipe and `0.3 m` exploratory thickness limit. Change only Fluent's EWF
`courant-number` to `0.05`; retain adaptive film stepping, its `1e-4 s` initial
step, five film sub-iterations, and all remaining E2.1 settings.

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

The prepared case saved and reopened with adaptive stepping ON, maximum
Courant `0.05`, initial film step `1e-4 s`, five film sub-iterations, and the
`0.3 m` cap. Film message output was ON with residual reporting interval one.
Native film and Family E report files were configured at frequency one.

The native solve reached iteration `5742` before floating-point exception;
the last complete report sample is `5741`. Maximum thickness first reached
`0.3 m` at `5737`, 87 iterations later than E2.1's `5650`. E2.1 failed at
`5653`; E2.4 delayed the failure by 89 iterations but did not avoid it. The
EWF `h/u/v` sub-iteration residuals reached roughly `1e272`–`1e279` in the
captured failure tail, alongside runaway flow residuals and Courant values.
The cap-hit-and-beyond values are numerical-failure evidence, not credible
film predictions.

The [recovered every-iteration native report histories](../../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/e24-native-report-histories_20260923_182121.json),
[summary](../../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/e24-summary.json),
and [Fluent failure transcript](../../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/transcript-failure-tail.txt)
retain the evidence. This Courant change delayed the cap/FPE sequence in this
run; it did not make the thickening film numerically stable.
