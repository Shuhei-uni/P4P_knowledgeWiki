# Phase 07 fixed-mesh treatment-screen setup series

## Status

**Server-neutral setup compilation complete; dependency-gated child execution
and plot-led evidence audit complete for every attempted packet.** The human
approved five treatment families with three initial settings each. E0, E1
P1120, E2, E3, and E4 have complete execution/analysis packets; corrected E1
P1160/P1200 are verified smoke-horizon numerical blocks; E5 reached its live
region/source capability probe for all three gains and was blocked before
solving. The shared scientific and evidence contract is [`design.md`](design.md).

## Phase Loop audit — 2026-09-10

The authoritative per-setup queue is recorded in the phase
[`phase-state.yaml`](../phase-state.yaml). A completed packet below means its
declared execution, histories, analysis, and core figures are verified; it does
not mean that the physical mechanism passed the scientific screen.

| Setup | Terminal execution / capability | Final artifacts and histories | Analysis/core figures | Phase Loop state |
| --- | --- | --- | --- | --- |
| `P7-E0-REF` | [x] 2,000 iterations and final reopen | [x] checkpoints, 14 reports, 7 residual histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E1-PO-P1120` | [x] 500 iterations | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E1-PO-P1160` | [x] corrected readback; [ ] smoke blocked | [ ] required 500-point histories | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E1-PO-P1200` | [x] corrected readback; [ ] smoke blocked | [ ] required 500-point histories | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E2-OV-K000` | [x] 500 iterations | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E2-OV-K003` | [x] 500 iterations | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E2-OV-K007` | [x] 500 iterations | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E3-MFO-Q025` | [x] 500 iterations and phase readback | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E3-MFO-Q050` | [x] 500 iterations and phase readback | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E3-MFO-Q100` | [x] 500 iterations and phase readback | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E4-ADAPT-G025` | [x] 500 active iterations, 10 updates | [x] final pair and adaptive histories | [x] F1–F4 analysis | `COMPLETE_VERIFIED` |
| `P7-E4-ADAPT-G050` | [x] 500 active iterations, 10 updates | [x] final pair and adaptive histories | [x] F1–F4 analysis | `COMPLETE_VERIFIED` |
| `P7-E4-ADAPT-G100` | [x] 500 active iterations, 10 updates | [x] final pair and adaptive histories | [x] F1–F4 analysis | `COMPLETE_VERIFIED` |
| `P7-E5-PSINK-G025` | [x] register probe; [ ] solve blocked | [ ] not applicable | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E5-PSINK-G050` | [x] register probe; [ ] solve blocked | [ ] not applicable | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E5-PSINK-G100` | [x] register probe; [ ] solve blocked | [ ] not applicable | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E2-OV-K010` | [x] K=10 readback; [ ] smoke blocked | [ ] required histories | [ ] not applicable | `BLOCKED_VERIFIED` |
| `P7-E3-MFO-Q14615` | [x] 500 iterations and phase readback | [x] smoke/checkpoint/final and histories | [x] F1–F3 analysis | `COMPLETE_VERIFIED` |
| `P7-E4-ADAPT-G150` | [x] 500 active iterations, 10 updates | [x] final pair and adaptive histories | [x] F1–F4 analysis | `COMPLETE_VERIFIED` |

The complete packets are execution-and-analysis complete, but several
scientific screens remain negative or inconclusive: positive inventory drift,
large vapor loss for E1/E2, imposed phase-routing caveats for Q146.15, and
final-command saturation with positive inventory drift for G1.50. E1
P1160/P1200 are blocked by corrected Fluent smoke failures, and E5 is blocked
earlier by the missing region-specific liquid-only source binding.

| Family | Initial setup packets |
| --- | --- |
| E1 pressure outlet | [`P1120`](e1-po-p1120/setup.md), [`P1160`](e1-po-p1160/setup.md), [`P1200`](e1-po-p1200/setup.md) |
| E2 outlet vent | [`K000`](e2-ov-k000/setup.md), [`K003`](e2-ov-k003/setup.md), [`K007`](e2-ov-k007/setup.md) |
| E3 prescribed withdrawal | [`Q025`](e3-mfo-q025/setup.md), [`Q050`](e3-mfo-q050/setup.md), [`Q100`](e3-mfo-q100/setup.md) |
| E4 adaptive withdrawal | [`G025`](e4-adapt-g025/setup.md), [`G050`](e4-adapt-g050/setup.md), [`G100`](e4-adapt-g100/setup.md) |
| E5 phase-selective sink | [`G025`](e5-psink-g025/setup.md), [`G050`](e5-psink-g050/setup.md), [`G100`](e5-psink-g100/setup.md) |

The three rows after E5 are the only conditionally activated fourth packets:
E2 K=10, E3 Q=146.15 kg/s, and E4 G=1.50. They were selected under the named
CONTEXT.md triggers and remain discovery screens, not continuations or
qualification runs. E2 is blocked during smoke; Q146.15 and G1.50 are now
complete analyzed screens on student. E1 and E5 fourth branches were not
activated because their trigger conditions remain unmet or blocked.
