# Phase 7.2A Stage 2 — E2.7 plus R3/R4/R5 roughness results

![Matched native histories for phase-2 steamoutlet flux, EWF mass, maximum thickness, average speed, wetted area, and bulk liquid inventory](figures/E2.7-R3-R4-R5-native-histories.png)

![Boundary-plus-absorber imbalance and scaled continuity residual](figures/E2.7-R3-R4-R5-balance-continuity.png)

![Outlet-based apparent liquid separation efficiency](figures/E2.7-R3-R4-R5-outlet-based-efficiency.png)

All three independent children used the hash-verified E2.7 continuation final
pair at native `13586`, changed only the intended outer-wall roughness height
(`C_s=0.5`), and reached native `16586` after one `/solve/iterate 3000` Fluent
TUI command each. Every child has 27 Fluent-native report histories with 3,001
points, including the starting coordinate. The [figure statistics](figures/E2.7-R3-R4-R5-summary.json)
and [phase-2 outlet CSV](figures/E2.7-R3-R4-R5-phase2-outlet.csv) accompany
the plot. The [R3](../../../../PyAnsys/output/phase72a_stage2_e27_roughness/R3-20260926T223230Z/run-manifest.json),
[R4](../../../../PyAnsys/output/phase72a_stage2_e27_roughness/R4-20260926T223500Z/run-manifest.json),
and [R5](../../../../PyAnsys/output/phase72a_stage2_e27_roughness/R5-20260926T223501Z/run-manifest.json)
manifests own the machine evidence and final-pair hashes.

| Case | `k_s` (m) | First native iteration at `0.3 m` film-thickness cap | Final phase-2 `steamoutlet` flux (kg/s) | Tail-500 outlet mean (kg/s) | Final film mass (kg) | Final average film speed (m/s) | Final native wetted area (m²) | Final bulk liquid inventory (kg) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E2.7 parent | `0` | not reached by N13586 | `-1.735` | — | `5.842` | `82.41` | `50.338` | `62.989` |
| E2.7+R3 | `5e-4` | `13723` | `-3.632` | `-3.632` | `2900.8` | `287775` | `48.581` | `62.781` |
| E2.7+R4 | `1e-3` | `13685` | `-3.682` | `-3.678` | `2985.2` | `75098` | `49.484` | `61.672` |
| E2.7+R5 | `2e-3` | `13665` | `-2.879` | `-2.884` | `2734.7` | `25088` | `48.389` | `62.545` |

Negative `steamoutlet` phase-2 flux denotes outflow. Relative to the parent
terminal magnitude, the final phase-2 outflow magnitude increased by `109%`
for R3, `112%` for R4, and `66%` for R5. The outlet histories first show a
large transient excursion and then settle near the tail means; none supports
a carryover reduction relative to the E2.7 parent. The three children do not
form a monotonic roughness response: R5 has a smaller late outlet magnitude
than R3/R4, but all three exceed the parent.

The film response is the stronger limit on interpretation. Maximum thickness
hit the configured `0.3 m` exploratory cap within the first `79–137` child
iterations and remained there. Film mass rose from `5.842 kg` to roughly
`2,700–3,000 kg` by N16586, with large fluctuations; area-weighted film speed
showed extreme spikes reaching tens of millions of m/s. These are reported
Fluent quantities, not credible evidence of physical wall drainage or a
stationary film. Bulk liquid inventory also had a large early transient peak
(`91–99 kg` across children) before ending near `62 kg`; endpoint inventory
alone obscures that response.

Wetted area is the Fluent-native surface integral of `film-coverage` over the
active EWF `wall`, recorded every iteration. At the parent N13586 state, this
native method returned `50.338 m²`; the earlier offline threshold
reconstruction in [Family E results](../ewf-family/results.md#e27-continuation--another-5000-iterations-on-server-1--2026-09-23)
gave `50.690 m²`. The `0.352 m²` method difference is unresolved, so this
screen compares the three children using the common native definition and
does not merge the offline endpoint into their history.

R3 and R5 runners retained full local native solve transcripts and recorded no
FPE, AMG, nonfinite, or fatal event. The laptop lost its gRPC/TCP route during
R4 near N16060; Fluent continued to N16586. R4 was reconciled after reconnect
from its live terminal iteration, all 27 complete native report files, and
hash-verified final pairs. Its local transcript ends near the disconnect and
does not cover the full solve, so a no-event claim is unavailable for R4.

Fluent reopened a just-saved prepared start data file at native `13585` despite
reporting `13586` immediately before save. For each actual solve, the runner
loaded the prepared roughness case and then the verified parent N13586 data;
native iteration and E2.7/roughness settings passed readback before compute.
The durable `run-input-N13586` files preserve that exact case-plus-data
combination separately from the original prepared snapshots. All three
`run-input` pairs were subsequently reopened on Server 3 and passed native
`13586`, E2.7, and roughness readback. The final
case/data pairs for all three children are present in the local OneDrive sync
folder and their hashes match the run manifests.

## Balance diagnostic and continuity

The [balance/continuity figure](figures/E2.7-R3-R4-R5-balance-continuity.png)
uses the same native iterations. Its mass-balance trace is the signed sum of
reported phase-1 inlet/outlet fluxes, phase-2 inlet/outlet fluxes, and the
native applied absorber (`kg/s`). The raw traces have recurring positive spikes
up to about `61–68 kg/s`; the 51-iteration rolling medians remain near
`-2` to `-3 kg/s` late in the runs. Over the final 500 iterations, the mean
absolute algebraic imbalance is `7.82 kg/s` (R3), `7.22 kg/s` (R4), and
`5.92 kg/s` (R5). The [plotted-data summary](figures/E2.7-R3-R4-R5-balance-continuity-summary.json)
records each formula, source, and window statistic. This is a
boundary-plus-absorber diagnostic: EWF transfer and storage are not included,
so it is not proof of complete physical mass closure.

The scaled continuity residual drops from its early transient and then
oscillates around a few `10^-3`. Raw transcript rows cover all 3,001 native
coordinates for R3 and R5. R4 has 2,475 continuity rows through N16060;
the plot leaves N16061–16586 blank for R4 because the laptop transcript ended
during the connection loss. The complete R4 mass-balance trace comes from
its native report files. No continuity values were interpolated into the gap.

## Outlet-based apparent separation

For this requested measure, the ratio of phase-2 liquid outflow through
`steamoutlet` to **total mass in** (steam plus liquid inlet) is the carryover
fraction, using a minus sign for Fluent's negative outlet flux. Its complement
is the outlet-based apparent separation measure:

`apparent separation (%) = 100 × [1 + signed phase-2 steamoutlet flux / (phase-1 steam-inlet flux + phase-2 liquid-inlet flux)]`.

The [history plot](figures/E2.7-R3-R4-R5-outlet-based-efficiency.png) uses both
inlet reports and the outlet report at every iteration. Total mass in was
`197.61 kg/s` (`80.69 kg/s` steam plus `116.92 kg/s` liquid). The E2.7 parent
terminal value is `99.12%`; the Stage 2 final values are `98.16%` (R3),
`98.14%` (R4), and `98.54%` (R5). The final-500 means differ by less than `0.01` percentage
point from those final values. The [calculation record](figures/E2.7-R3-R4-R5-outlet-based-efficiency-summary.json)
preserves the formula, signs, and values. This is an outlet-based ratio, not
validated separator efficiency: liquid can accumulate in the bulk or EWF film,
be removed by the virtual absorber, or remain in an unclosed mass balance.

This was a completed numerical screen, not a successful routing treatment.
The cap, extreme film values, and unresolved EWF-inclusive closure preclude a
physical benefit or convergence claim.
