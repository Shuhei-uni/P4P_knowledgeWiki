# Phase 7b S100 — Results

**Disposition: numerical failure at attempted N4183; 4,182 completed iterations verified. No N5000 endpoint or qualification.**

S100 extended the collector to the historical y=0.020 m cap under the unchanged
[setup](setup.md). The build verified 98,519 collector cells, zero mask/zone
mismatch and 6,286 uniquely oriented interface faces, with the same 620,431-cell
mesh. The [reference comparison](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/common-reference-comparison.json)
confirms the same reference setup and fresh Hybrid initialization as S80.
The approved steady physics, source coefficient and numerics were unchanged.

The [failure transcript](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/solve.trn)
records epsilon AMG divergence followed by host/node floating-point exceptions.
Recovery preserved the diverged N4183 diagnostic pair, recovered the native
scalar history, and reopened the saved N4000 checkpoint for field extraction
without issuing iterations. The [reconciliation](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/failure-recovery/reconciliation.json),
[terminal disposition](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/terminal-disposition.json)
and [recovery-section receipt](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/recovery-sections.json)
distinguish these states; the original execution manifest is retained unchanged.
Exact case/data paths and their permitted uses are in [run-paths.yaml](run-paths.yaml).

## Observed: evidence coverage and failure

The [analysis summary](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/summary.json)
verifies all N1–4182 scalar, collector-flux and active-equation residual records,
with no missing indices, conflicting duplicates or nonfinite samples. Residual
output contains nine identical chunk-boundary duplicates, retained in the
transcript and deduplicated for analysis. The recorder manifest reports 4,182
completed PC writes and no recording error. The [last-record PC readback](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/failure-recovery/last-flux-readback.json)
exactly matches the local N4182 flux record; this sampled readback is not an
independent reread of every remote file. The attempted N4183 did not produce
a completed row; this is a numerical failure, not a missing completed sample.
Finite arithmetic in a stored row does not establish physical validity.

The prescribed N4001–4500 window has only 182 samples and N4501–5000 has none.
No full late-window means, inventory-shift indicator or final-window screening
judgment is substituted with an earlier window. Full histories retain the
runaway values; symlog axes keep their signs and magnitude visible.

- [F1: complete inventory, removal and mask-flux histories](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/F1-inventory-removal.png).
- [F2: complete source-inclusive closure and routing histories](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/F2-closure-routing.png).
- [All active residual histories](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/residuals.png).
- [N1–4000 recovery prefix](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/recovery-prefix-N04000.png), separately labelled and unconverged.

The terminal trajectory shows deterioration before the fatal solver message:

| Iteration | Continuity residual | Epsilon residual | Maximum mixture speed (m/s) |
| --- | ---: | ---: | ---: |
| 4000, saved recovery checkpoint | 0.39042 | 0.010141 | 81.8019 |
| 4147 | 0.73561 | 0.03792 | 238.455 |
| 4148 | 0.93554 | 203.71 | 3,886.81 |
| 4165 | 3.5506 | 479.77 | 81,631.8 |
| 4178 | 734.61 | 13,576 | 7.07665e6 |
| 4182, last completed numerical row | 9.9752e32 | 4.9975e41 | 3.71513e36 |

At N4148 the minimum reported fluid pressure fell to −3.82051e6 Pa; by
N4182 gross collector delivery reached 9.63998e47 kg/s. These are numerical
runaway signals. The bounded-looking liquid inventory and removal traces do
not rescue the failed pressure/velocity solution. N4182 is the last completed
numerical record, not a valid scientific endpoint.

## Observed: N4000 recovery checkpoint

The table describes the saved, unconverged N4000 state, not a successful
terminal result or a matched N5000 comparison with the other cases.

| Metric | N4000 value |
| --- | ---: |
| Whole liquid volume / mass | 0.628836 m³ / 554.489 kg |
| Collector liquid volume / mass | 0.000784156 m³ / 0.691446 kg |
| Above-collector liquid volume | 0.628052 m³ |
| Native applied removal | 286.316 kg/s |
| Recomputed removal from current alpha | 286.956 kg/s |
| Gross liquid delivery / escape | 301.563 / 19.0249 kg/s |
| Liquid closure | −177.451 kg/s; −151.770% of liquid feed |
| Vapour closure | +1.13246 kg/s; +1.40347% of vapour feed |
| Mixture closure | −176.315 kg/s; −89.2230% of total feed |
| Liquid carryover / measured liquid feed | 6.89009% |
| Steam recovery / measured vapour feed | 98.5965% |
| Outlet vapour mass fraction | 0.908051 |
| Liquid-inlet / steam-inlet pressure drop | 29,544.7 / 29,754.9 Pa |
| Minimum / maximum fluid pressure | 1,118,078.6 / 1,159,335.8 Pa |
| Maximum mixture speed | 81.8019 m/s |

Measured liquid/vapour feeds were 116.921/80.6899 kg/s. With boundary flux
positive into the vessel, liquid and mixture closure is the boundary sum plus
the signed native applied mass source, counted once; vapour has no sink.
Applied removal at N exactly matches recomputed removal at N−1 for all
4,181 adjacent stored pairs. The current-alpha integral is a separate diagnostic
and is not the source used to close that iteration. Inventory change per steady
iteration is numerical evolution, never physical storage in kg/s.

N4000 continuity, k, epsilon and liquid-fraction residuals were respectively
0.39042, 0.0036091, 0.010141 and 0.0070321, all above 1e-3. The mass imbalances
and rising inventory already prevent a credible steady-state interpretation
before the extreme terminal runaway. Routing ratios are descriptive numerical
reports from that unconverged state, not validated separation performance.

## Observed: recovery spatial fields

[F3 liquid fraction and speeds](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/F3-checkpoint-04000-above-cap-fields.png)
and [velocity components](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/F3-checkpoint-04000-velocity-components.png)
show only **recovery N4000**. The [section audit](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/analysis/section-summary.json)
verifies finite native facet values on all four nonempty y=0.5, 1.5, 3 and 5 m
planes, exact initial/checkpoint geometry identity, and unchanged shared
colour scales: alpha 0–1, speeds 0–80 m/s and components −80–80 m/s. No values
are clipped. Peak section speed is 54.8757 m/s; the domain maximum can be
larger because these four sections do not cover every cell.

Fresh [run-local field metadata](../../../../PyAnsys/output/p7b-s100-20260921T160825Z/field-metadata.json)
identifies unqualified pressure/velocity fields as mixture fields and the
phase-2-prefixed fields as liquid-phase fields. Facets are rendered without
interpolation or smoothing. One zero-projected-area facet on each of the
1.5 and 5 m sections contributes no area weight. The area-weighted liquid
fractions are 0.0105338, 0.0295399, 0.0318299 and 0.0333836, respectively.
Liquid is concentrated in outer-wall bands, with local alpha maxima near
0.95–0.97; this is an unconverged field pattern. Both initial F3 panels,
recovery F3 panels and all history plots were visually inspected.

## Inferred and missing information

S100 is the fifth scientific case with an explicit numerical-failure disposition
at G1. Its early history and N4000 checkpoint can inform failure diagnosis,
but cannot establish a stable ideal collector or be ranked against the other
cases' N5000 snapshots as equivalent endpoints. No additional exact-N4000
replay is necessary to document this failed attempt, and no numerical tuning
or further solve was used to improve its disposition.

The isolated failure mechanism and repeatability are unknown. The simultaneous
epsilon, pressure and velocity escalation establishes numerical breakdown;
it does not alone distinguish source stiffness, coupling, turbulence feedback
or other numerical causes. There is no N5000 pair or field export and no
complete prescribed late window. The failed N4183 pair is diagnostic evidence
only, not an approved restart parent. These limits remain explicit in the
five-case G1 comparison; altered source strength, numerics or further cases
require a separately framed next experiment.
