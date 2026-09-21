# P7-E5-CZ-G025 results

## Answer at a glance

The corrected G025 child is `COMPLETE_VERIFIED` as a 500-iteration
implementation and discovery screen. It rebuilt the child from the exact
E0-500 case/data checkpoint, split the supplied mesh into the approved lower
fluid cell zone, passed save/reopen and source-off smoke gates, activated the
lower-zone phase-2 source, completed all ten controller updates through native
iteration 1,000, saved the final paired case/data files, and produced the full
report/residual package.

The result is not promising as a liquid-inventory intervention at `G=0.25`.
The total liquid inventory still rose almost exactly as in E0: the late
751--1,000 slope was `+0.5046 kg/iteration` versus `+0.4968 kg/iteration` for
the matched E0 window. The final G025 inventory was `365.36 kg`, only
`4.67 kg` below E0 at native iteration 1,000 (`370.03 kg`). The controller
command rose from `2.52` to `28.27 kg/s` without saturation, but the observed
global inventory response did not improve.

The earlier source-integral warning was also resolved. The first post-run
audit used `compute_volume_integral` on Fluent's `phase-2-user-mass-source`
field, whose quantity is already mass flow; that reduction returned a
misleading `-0.002838 kg/s`. A read-only final-case check with Fluent's
`get_sum` reduction returned `-28.272494 kg/s`, matching the analytical
integral of the uniform source to `3.3e-14 kg/s`. The runner has been corrected
for the remaining gains. The original contaminated attempt remains archived
as an invalid implementation attempt and is not used here.

## Evidence status

| Requirement | Status | Evidence |
| --- | --- | --- |
| Exact parent | PASS | E0 iteration-500 case/data pair from the shared P7-E0-REF checkpoint; parent settings and liquid density read back |
| Cell-zone split | PASS | `3,794` marked cells moved into `p7-e5-lower-y010`; `338,815` cells remained in `separator-purnanto` |
| Mesh invariants | PASS | `342,609` cells, `1,647,633` faces, `1,046,255` solver nodes, extents, volume/face statistics, and mesh check preserved |
| Generated topology | PASS | New lower fluid zone and adjacent generated face zones were present after save/reopen |
| Source binding | PASS | Lower-zone phase-2 mass and mixture x/y/z momentum sources enabled; parent and lower phase-1 sources disabled |
| Source normalization | PASS | Corrected lower-zone geometric volume `0.308302610 m3`; final phase-2 source `-91.703713 kg/m3/s`; analytical integrated source `-28.272494 kg/s` |
| Source-integral audit | PASS with corrected reduction | `get_sum(phase-2-user-mass-source) = -28.272494 kg/s`; see source audit (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G025-student-20260910T031110Z-source-audit.json` |
| Save/reopen | PASS | Split source-off parent and prepared source-off child reopened with both fluid zones present |
| Smoke horizon | PASS | Source-off smoke completed from native 500 to 550 before source activation |
| Requested horizon | PASS | Ten controller blocks completed, active 1--500 / native 501--1,000 |
| Final paired case/data | PASS | `P7-E5-CZ-G025-active500.cas.h5` and `.dat.h5` saved and reopened |
| Report histories | PASS | Fourteen report files recovered; flux histories have 501 points including native 500, mass/volume histories have 500 active points |
| Residual history | PASS | Seven native residual series with 500 active points |
| Planned figures | PASS with interpretation limits | F1--F4 generated; F2/F3 remain boundary-routing views and do not replace a fully source-inclusive balance because the Fluent report package does not expose mixture momentum source integrals directly |

## Controller and source readback

| Active update | Liquid mass [kg] | Normalized error [-] | Requested source [kg/s] | Lower phase-2 volume [m3] |
| ---: | ---: | ---: | ---: | ---: |
| 50 | 168.709 | 0.0864 | 2.525 | 0.02738 |
| 100 | 185.797 | 0.1629 | 4.762 | 0.02723 |
| 150 | 206.397 | 0.2552 | 7.459 | 0.02952 |
| 200 | 225.331 | 0.3400 | 9.938 | 0.02850 |
| 250 | 245.475 | 0.4302 | 12.576 | 0.03269 |
| 300 | 262.891 | 0.5082 | 14.856 | 0.02895 |
| 350 | 289.491 | 0.6274 | 18.339 | 0.03629 |
| 400 | 316.154 | 0.7468 | 21.830 | 0.02856 |
| 450 | 341.511 | 0.8604 | 25.150 | 0.02978 |
| 500 | 365.362 | 0.9672 | 28.272 | 0.03315 |

The lower-zone geometric volume remained fixed at `0.308302610 m3`; the
phase-2 volume fraction varied between approximately `0.02723` and
`0.03629 m3` at the controller updates. At the final update the source tree
read back as:

- phase-2 mass source: `-91.703713 kg/m3/s`;
- mixture x-momentum source: `-71.292213 N/m3`;
- mixture y-momentum source: `-4.796744 N/m3`;
- mixture z-momentum source: `+40.771574 N/m3`.

## Numerical observations

The planned report-facing figures are:

1. [F1 — liquid inventory versus E0](figures/P7-E5-CZ-G025-student-20260910T031110Z/F1-liquid-inventory-vs-E0.png), the direct answer figure. The G025 and E0 curves remain close through the matched 501--1,000 interval; the intervention does not create a visible downward inventory response.
2. [F2 — phase routing and closure](figures/P7-E5-CZ-G025-student-20260910T031110Z/F2-phase-routing-and-closure.png), showing the phase-resolved boundary routing. Late-window phase-2 boundary liquid outflow averaged `0.256 kg/s`, while liquid inflow remained `116.92 kg/s`.
3. [F3 — numerical adequacy](figures/P7-E5-CZ-G025-student-20260910T031110Z/F3-numerical-adequacy.png), showing finite residual histories alongside the boundary-based mixture-imbalance diagnostic. The late-window imbalance ratio was approximately `0.587`, so the run is not a converged conservation result.
4. [F4 — adaptive controller](figures/P7-E5-CZ-G025-student-20260910T031110Z/F4-adaptive-controller.png), a responsive controller figure added for this E5-CZ family. It shows the liquid mass moving away from `M*=149.425 kg` and the command increasing monotonically without reaching the `146.15 kg/s` clamp.

The matched inventory slopes were:

| Window | G025 [kg/iteration] | E0 [kg/iteration] | Observation |
| --- | ---: | ---: | --- |
| 501--1,000 | `+0.4307` | `+0.4270` | essentially the same positive drift |
| 751--1,000 | `+0.5046` | `+0.4968` | G025 is slightly worse, not better |

The residuals stayed finite, but the late-window means were approximately
`8.39e-2` for continuity, `2.06e-4` for x-velocity, `2.13e-4` for y-velocity,
`2.07e-4` for z-velocity, `1.65e-3` for `k`, `2.78e-3` for epsilon, and
`8.80e-3` for phase-2 volume fraction. These support “completed finite screen,”
not “numerically converged steady solution.”

## Interpretation and claim boundary

The cell-zone architecture is technically viable: it can preserve the global
mesh topology counts while giving Fluent a genuine lower fluid zone that can
be addressed by native phase and mixture source branches. That answers the
implementation question positively.

The G025 result does not support the scientific intervention yet. The
controller requested progressively larger lower-zone removal, but global
liquid inventory continued to rise at essentially the E0 rate, phase-2
boundary liquid outflow remained small, and the boundary-only mixture closure
remained open. This is evidence against promoting `G=0.25` from this finite
screen, not evidence that every gain or every cell-zone source law is
impossible. The remaining gains are needed for the declared contrast, subject
to the same corrected source audit.

This is not a qualification result, not a validated plant-drainage result,
and not a conclusion about mesh independence or physical outlet fidelity. It
also does not justify patching or resetting the field; that route remains
excluded unless explicitly requested by the human.

## Next action

Run G050 and G100 from the exact E0-500 parent using the corrected
`get_sum`-based source audit, then compare all three gains with the same F1--F3
windows. The current evidence suggests the family is unlikely to yield a
useful inventory response, but that ranking must wait until the three-gain
comparison is complete. No numerical tuning, patch/reset, or unapproved
geometry change is introduced by this next step.

Durable implementation artifacts:

- [corrected E5-CZ runner](../../../../../PyAnsys/scripts/setup/run_p7_e5_cz.py)
- G025 manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G025-student-20260910T031110Z-manifest.json`
- G025 report histories (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G025-student-20260910T031110Z-reports.json`
- G025 residual history (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G025-student-20260910T031110Z-residuals.json`
- G025 numerical summary (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G025-student-20260910T031110Z-analysis/summary.json`
