# P7-E1-PO-P1160 results

## Answer at a glance

The earlier `20260908T094500Z` artifact is **invalid for P1160**: its
manifest recorded the intended `1,160,000 Pa`, but the final Fluent readback
was `1,120,000 Pa` because the backflow-state helper overwrote the pressure
after the setter. Its recovered histories are byte-identical to P1120 and are
not used as P1160 evidence.

The corrected attempt `P7-E1-PO-P1160-server1-20260909T001000Z` applied the
backflow state first, set `1,160,000 Pa` last, and proved that value both before
save and after reopen. Fluent then diverged during the 50-iteration smoke
horizon and raised floating-point exceptions; only seven native residual rows
were captured before the session became unavailable. The runner correctly
refused to write a completion event or a scientific result.

**Evidence status:** corrected setup/readback proven; solve, required report
histories, and core figures incomplete. **Queue state:** `BLOCKED_VERIFIED`.

## Core visual evidence

No F1–F3 treatment figures are claimed for this packet. The corrected run did
not complete the smoke horizon or produce the required 500-point report
histories. The old figures under the superseded `20260908T094500Z` directory
are deliberately excluded because they represent P1120, not P1160.

## Numerical adequacy and blocker

- `Observed`: corrected pre-save and post-reopen bottom pressure readback was
  `1,160,000 Pa`.
- `Observed`: the smoke transcript shows rapidly growing turbulence/velocity
  residuals, repeated AMG divergence messages, and floating-point exceptions.
- `Observed`: the smoke residual history contains only seven native rows,
  below the required 50; no 250/500 checkpoints or final pair were accepted.
- `Inferred`: the corrected P1160 boundary is numerically unstable from the
  exact initialized parent under the approved no-tuning contract.
- `Claim boundary`: no inventory, balance, vapor-loss, convergence, or
  treatment-ranking claim may be taken from the superseded run.

## Decision and checklist

| Phase Loop item | Status | Evidence |
| --- | --- | --- |
| Corrected boundary mutation and readback | PASS | corrected manifest before/after reopen |
| Smoke horizon | BLOCKED | seven residual rows; Fluent floating-point exception |
| Checkpoint/final pair | NOT RUN | solver fault before accepted smoke completion |
| Reports and residual histories | BLOCKED | required 500-point histories absent |
| Planned analysis and core figures | NOT APPLICABLE | no valid completed screen |

**Decision:** retain the corrected run as a verified numerical failure and do
not activate the conditional E1 fourth point. A pressure value between P1120
and P1200 is not scientifically selected by the failed P1160/P1200 evidence.

## Run and artifact details

- Superseded invalid manifest: `PyAnsys/output/phase07_treatment_screen/P7-E1-PO-P1160-server1-20260908T094500Z-manifest.json`
- Corrected manifest: `PyAnsys/output/phase07_treatment_screen/P7-E1-PO-P1160-server1-20260909T001000Z-manifest.json`
- Corrected transcript: `PyAnsys/output/phase07_treatment_screen/P7-E1-PO-P1160-server1-20260909T001000Z-residuals-transcript.txt`
- Corrected residual record: `PyAnsys/output/phase07_treatment_screen/P7-E1-PO-P1160-server1-20260909T001000Z-residuals.json`
