# P7-E2-OV-K010 results

## Answer at a glance

Observed: the conditional fourth branch was selected exactly under CONTEXT.md:
K=7 completed, remained the upper tested setting, and left the response
unresolved. The current truncated mesh child read back outlet-vent K=10 before
save and after reopen.

Observed: the child diverged during the 50-iteration smoke horizon. The
transcript shows rapidly increasing continuity, k, and epsilon residuals,
AMG divergence, and host/node floating-point exceptions at approximately
native iteration 24. The runner did not accept the smoke event, checkpoint, or
final artifact.

Evidence status: corrected K=10 setup/readback proven; required screen
histories and core figures incomplete. Queue state: BLOCKED_VERIFIED.

## Core visual evidence

No F1--F3 treatment figures are claimed. The run did not complete the required
smoke horizon or produce 500-point histories. The prior full-geometry K=10
failure is collision context only; this current-mesh transcript is the
independent Phase-07 evidence.

## Numerical adequacy and interpretation

- Observed: exact parent/readback/save-reopen preparation passed, including
  K=10.
- Observed: only partial residual rows were captured before Fluent became
  unresponsive; the required 50-point smoke and 500-point screen are absent.
- Inferred: K=10 is numerically unstable on the current truncated mesh under
  the inherited no-tuning numerical contract.
- Competing explanation: the shared inherited RNG/multiphase field may be
  destabilized by the high-resistance boundary; the branch does not identify
  whether the cause is physical or numerical.
- Claim boundary: no inventory, closure, vapor-loss, physical drainage, or
  qualification claim.

## Decision and checklist

| Phase Loop item | Status | Evidence |
| --- | --- | --- |
| Conditional branch authority and parent | PASS | CONTEXT.md and run-paths |
| K=10 setup/readback and save/reopen | PASS | manifest |
| Smoke horizon | BLOCKED | divergence/FPE before accepted smoke |
| Checkpoint/final/history package | NOT RUN | runner stopped before accepted smoke |
| Planned analysis and core figures | NOT APPLICABLE | no valid completed screen |

Queue state: BLOCKED_VERIFIED. Do not activate an additional E2 branch; the
one named fourth point has now probed the upper boundary and failed.

## Run and artifact details

- Manifest: PyAnsys/output/phase07_treatment_screen/P7-E2-OV-K010-server1-20260909T004500Z-manifest.json
- Transcript: PyAnsys/output/phase07_treatment_screen/P7-E2-OV-K010-server1-20260909T004500Z-residuals-transcript.txt
- Residual record: PyAnsys/output/phase07_treatment_screen/P7-E2-OV-K010-server1-20260909T004500Z-residuals.json
- Conditional setup: setup.md

