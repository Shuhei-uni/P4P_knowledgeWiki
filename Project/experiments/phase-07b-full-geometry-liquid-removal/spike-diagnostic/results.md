# E3 / G3 — diagnostic replication of S40-T020

**The repeat reproduces the original numerical trajectory and localises four
sampled speed excursions to a small region near the inlet-top elevation,
well above the collector. It does not produce a credible steady solution or
identify a unique cause.** E3 reached its absolute N5000 cap. G3 is complete: histories, all 27 diagnostic snapshots and eight native
Fluent spatial views are verified. No case is qualified.

The original is `p7b-s40-t020-resume-20260921T231240Z`. The repeat began as
`p7b-s40-t020-diag-20260922T071533Z` and finished through the recorded
`p7b-s40-t020-diag-resume-20260922T122811Z` continuation. Both used the original
clean N0/Hybrid lineage, S40, tau=0.02 s and unchanged scientific/numerical
settings. Added instrumentation is the declared delta in [setup](setup.md).

## Replication and numerical adequacy

The [independent equality audit](../../../../PyAnsys/output/phase07b-g3/replication-equality-audit.json)
finds exact equality at stored precision in every common scalar, exact-face
flux and seven-equation residual value over N1–5000. All 12 corresponding
initial/final horizontal/axial section arrays also match exactly. Separate
report destinations, fresh initialization/readback receipts, timestamped
callbacks and the additional diagnostic columns establish separate acquisition.
The recovery at N4284 introduces no observed difference in these recorded
signals. This is one deterministic repeat, not a statistical independence
study or proof of reproducibility under other configurations.

![Raw residuals and speed; the two traces coincide](../../../../PyAnsys/output/phase07b-g3/G3-residual-speed-comparison.png)

*Raw curves coincide at recorded precision; no smoothing is used. Green hollow
markers identify the four sampled speed triggers. The N2700 observation and
N4284 controller-recovery boundary are marked. The largest late epsilon spike
is 32.2 at N4767, coincident with maximum speed 2477.05 m/s; these are numerical
excursions, not accepted physical flow predictions.*

Both runs return the same predeclared screening indicators:

| Indicator | Measured | Required | Result |
| --- | ---: | ---: | --- |
| Mean absolute liquid closure, N4501–5000 | 354.843% of liquid feed | ≤1% | Fail |
| Mean absolute vapor closure | 3.329% of vapor feed | ≤1% | Fail |
| Mean absolute mixture closure | 208.591% of total feed | ≤1% | Fail |
| Liquid-inventory mean change, N4001–4500 vs N4501–5000 | 18.370% | ≤1% | Fail |
| Maximum continuity residual, N4501–5000 | 1.2497 | ≤0.001 throughout | Fail |
| Maximum k / epsilon / liquid-fraction residual | 0.16321 / 32.2 / 0.014231 | Each ≤0.001 | Fail |
| Maximum x / y / z velocity residual | 0.00034812 / 0.00035745 / 0.00034763 | Each ≤0.001 | Pass |

![Inventory, applied source and source-inclusive balances](../../../../PyAnsys/output/phase07b-g3/G3-inventory-source-closure.png)

*Liquid inventory keeps growing while applied removal greatly exceeds liquid
feed over much of the late history. Source-inclusive conservation fails;
iteration-to-iteration inventory change is not physical kg/s storage and cannot
repair that imbalance. Native applied source is counted once. Its N value
matches the current-expression removal at N−1 exactly over all 4999 pairs.*

Final liquid volume is 1.043139 m³. Late-window means rise from 0.728696 to
0.892680 m³. Endpoint liquid carryover is 15.83% of liquid feed and vapor
recovery is 97.53%, but neither is a qualified separation-performance result
because the numerical adequacy and stationarity conditions fail.

## Where the sampled excursions occur

| Trigger N | Maximum speed (m/s) | Maximum-speed cell (x, y, z), m | Local liquid fraction | Epsilon equation residual | N+1 / N+5 maximum speed (m/s) |
| --- | ---: | --- | ---: | ---: | ---: |
| 3786 | 661.864 | (0.393428, 2.427477, −0.999545) | 0.007783 | 0.170190 | 209.279 / 548.477 |
| 4124 | 632.191 | (0.274731, 2.424225, −1.032506) | 0.008927 | 0.458910 | 171.426 / 81.244 |
| 4328 | 819.048 | (0.085612, 2.427283, −1.074072) | 0.005742 | 0.193050 | 216.161 / 241.023 |
| 4763 | 585.996 | (0.393428, 2.427477, −0.999545) | 0.100865 | 2.215900 | 175.462 / 759.716 |

These trigger maxima are all in the main fluid zone, roughly 3.307–3.310 m
above the collector upper boundary y=−0.882750 m. Their elevations lie
0.52–3.77 mm below the inlet upper edge y=2.428000 m recorded in the
[geometry proof](../geometry-proof.md). This establishes proximity in elevation;
it does not by itself prove coincidence with an inlet face or a bad mesh cell.
The first and fourth triggers share the same maximum-speed cell. Other maxima
shift, including to the steam-outlet region at N4129. Local liquid fraction is
not consistently near zero across all events or followups.

The [complete snapshot/event table](../../../../PyAnsys/output/phase07b-g3/comparison.json)
retains co-located pressure, k, epsilon, alpha and coordinates, native report
parity, hashes and scheduling evidence. Every snapshot passed finite-field,
unchanged-iteration and native speed/k/epsilon/inventory checks. Array indices
are local to the stored ordering. Raw `SV_MASS_IMBALANCE` is uncalibrated and
is not used as a scaled residual or physical mass balance.

Capture is bounded: the first speed ≥500 m/s per 250-iteration band, plus N+1
and N+5. **The largest N4767 peak was not captured as a whole-cell snapshot**;
N4763/N4764/N4768 provide nearby evidence. It is therefore inappropriate to
assign the exact N4767 maximum to a cell, although the sampled excursions
recur in the same small region. Event arrays are not reloadable case/data pairs.
See the [native spatial comparison](spatial-comparison.md) for saved-state
context and its timing limits.

## The observation near N2700

The broader increase is reproducible, but N2700 is not a universal sharp onset.
Epsilon's 95th percentile rises from 0.015398 in N2201–2700 to 0.033009 in
N2701–3200; its maximum rises from 0.023848 to 0.122060, and maximum speed
from 236.699 to 443.091 m/s. Neither window reaches the 500 m/s capture trigger.
In N3201–3700 the speed maximum falls back to 93.451 m/s, before larger later
excursions. This is intermittent growth, not a monotonically increasing
instability amplitude.

The scheduled N2600/N2700/N2800 snapshots show their maximum speeds at the
steam-outlet elevation (~6.265 m), at 86.628/85.570/85.607 m/s. These isolated
snapshots do not capture the intervening bursts. Liquid inventory increases
from 0.299561 to 0.303819 to 0.327029 m³ across those snapshots. Neither
coincidence nor an iteration threshold establishes which equation initiated
the disturbance.

## Interpretation and next decision

1. **Local inlet-region flow/phase/turbulence amplification is a leading
   explanation to test.** Four sampled triggers recur close to the inlet-top
   elevation, with large local k/epsilon and speed. Mesh treatment, pressure–
   velocity coupling, phase transport and limiting remain alternatives within
   that explanation; no quality metric or controlled numerical contrast yet
   isolates them.
2. **Indirect coupling to the collector remains plausible.** Applied removal,
   inventory and conservation are badly behaved, and the implemented source
   has a verified one-iteration update lag. Locating the largest sampled speed
   away from the collector weakens a direct sink-zone hotspot explanation but
   does not decouple the global pressure/flow system from the sink.
3. **Fresh full-feed development may contribute.** The pattern occurs during
   continuing liquid accumulation. This run does not compare a developed
   parent, staged loading or another solver coupling treatment.
4. **A recorder-generated spike is weakened by the evidence.** Common histories
   and native initial/final arrays reproduce exactly despite the additional
   field reads and recovered interruption. This does not establish a physical
   instability or prove that every possible instrumentation change is neutral.

The supported next action is the authorized correctness audit of Shuhei's
newly pulled work, followed by a prospectively declared controlled numerical
or source contrast. Compare actual loading/history, residual definitions,
source accounting and geometry before attributing his improvement to Coupled
or Global-Time-Step controls. Do not run another tau-only point or extend this
E3 trajectory merely because it completed; E2 already showed tau alone was
insufficient and E3 reproduces that failure.

## Evidence and execution provenance

All N1–5000 scalar, seven-residual and exact-face flux histories are retained.
N50/every-500 checkpoints and the final pair are preserved; final N5000 serves
as the last 500-iteration checkpoint. Initial/final horizontal and full-height
axial fields are present. All 27 scheduled/event snapshots are verified.
The controller disappeared at N4283 for an unknown local reason; the unchanged
live N4284 state was preserved, orphan callbacks were retired and the recorder
was recovered without reloading or initialization. A native boundary print
recovered N4284's residual row; no interpolation was used. Routine recovery
implementation errors advanced no additional scientific iterations. Detailed
receipts and the sole continuation are in [run paths](run-paths.md).

- [Completion and paired-artifact audit](../../../../PyAnsys/output/p7b-s40-t020-diag-resume-20260922T122811Z/completion-audit.json)
- [Comparison, numerical indicators and all snapshot records](../../../../PyAnsys/output/phase07b-g3/comparison.json)
- [Original raw derived histories](../../../../PyAnsys/output/phase07b-g3/original-history.csv) and [diagnostic raw derived histories](../../../../PyAnsys/output/phase07b-g3/diagnostic-history.csv)
- [Original evidence manifest](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/manifest.json) and [completed diagnostic manifest](../../../../PyAnsys/output/p7b-s40-t020-diag-resume-20260922T122811Z/manifest.json)
