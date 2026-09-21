# Phase 7b S60 — Results

**Status: 5,000 global iterations complete; evidence complete, numerical indicators failed.**

The 60% collector removes liquid but does not establish a balanced steady
solution. Its smaller whole-vessel inventory than S20/S40 coexists with larger
late source-inclusive imbalance, a sharp late increase in removal, changing
inventory and unconverged residuals. No physical capture efficiency or case
qualification follows.

The completed continuation is
[p7b-s060-resume-20260921T113238Z](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/manifest.json),
with original N1–N2495 evidence retained in
[p7b-s060-20260921T043132Z](../../../../PyAnsys/output/p7b-s060-20260921T043132Z/manifest.json).
The [analysis summary](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/summary.json)
contains exact source hashes, full histories and both prescribed late-window
statistics. Scientific conditions remain those in [setup.md](setup.md).

## Observed

Build checks verified 59,465 collector cells, zero mask/zone disagreement and
6,121 uniquely oriented interface faces. The original child used the common
clean N0 parent and fresh Hybrid initialization. A human-directed pause at
N2495 preserved a matching pair. After live-state reconciliation, the run
continued **without reload or reinitialization** for 2,505 more iterations,
ending at global N5000 rather than adding a fresh 5,000-iteration run.

The [continuation audit](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/continuation-audit.json)
verifies that the original 2,495 flux rows are the exact byte prefix of the
combined history; scalar and residual prefixes retain identical values, and
initial section NPZ files are byte-identical to the originals. Flux capture
`bc23dc2e1a0b40d987211c2d63ede2ba` covers N1–N2495 and capture
`4be74084a60743ac8fe71867012a5f34` covers N2496–N5000. The manifest records
2,495 inherited and 2,505 resumed completed remote writes. All six resumed
checkpoint flux readbacks, including N5000, match local records; this is
not an independent reread of every remote file.

All 5,000 scalar and collector-flux rows are present, finite and unique. All
seven residual histories cover N1–N5000; eleven identical pause/chunk-boundary
repeats are deduplicated without conflict. Matching final case/data and four
final section exports completed. The separate
[endpoint verification](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/endpoint-verification.json)
confirms steady N5000 and the final pair. Storage remains LOCAL_ONLY; this
analysis does not establish an independent backup.

[F1 — Inventory, removal and collector crossing](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/F1-inventory-removal.png)
shows liquid buildup and a strong late excursion in removal. At N5000 total
water is **0.725713 m³ (639.912 kg)**: 0.00134446 m³ (1.18551 kg)
in the collector and 0.724369 m³ above it.

| Metric | N4001–4500 mean | N4501–5000 mean |
| --- | ---: | ---: |
| Whole liquid volume, m³ | 0.602948 | 0.705993 |
| Collector liquid volume, m³ | 0.000978980 | 0.00187808 |
| Native applied removal, kg/s | 358.656 | 686.730 |
| Recomputed current-field removal, kg/s | 358.250 | 687.268 |
| Gross liquid delivery to collector, kg/s | 396.389 | 772.290 |
| Gross liquid escape from collector, kg/s | 40.259 | 84.059 |
| Liquid net export at steam outlet / liquid feed | 13.35% | 15.19% |
| Vapour net export at steam outlet / vapour feed | 97.94% | 95.26% |

Final-window liquid volume spans 0.597952–0.792541 m³, with standard
deviation 0.0681603 m³ and fitted slope **+3.71567e−4 m³ per iteration**.
The change between window means is **+14.596%** of the larger mean,
exceeding the 1% convention. The curve rises sharply and then declines near
the endpoint; the full window must not be replaced by that terminal decline.
These are steady numerical iterations, not physical time or a storage rate.
Internal gross crossings are not additional external feeds.

[F2 — Conservation and outlet routing](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/F2-closure-routing.png)
uses individual signed boundary flows, positive into the vessel, plus the
signed native applied source once for liquid/mixture; vapour has no direct
source. Applied removal at N matches recomputed removal at N−1 exactly at
stored precision for all 4,999 consecutive pairs, including the resume
boundary. Current-field named closure reports are not substituted for this
accounting. No inventory slope or Fluent Net report is added as another source.

| Applied-source closure, N4501–5000 | Signed mean, kg/s | Mean absolute imbalance / measured feed | ≤1% indicator |
| --- | ---: | ---: | --- |
| Liquid | −587.567 | 502.533% | Fail |
| Vapour | +3.82207 | 4.73674% | Fail |
| Mixture | −583.748 | 295.402% | Fail |

Mean applied removal is 686.730 kg/s against the liquid feed of
116.921 kg/s, with a final-window maximum of 1,429.409 kg/s. Large sink
activity therefore coexists with strongly open global closure; it does not
show conservative steady capture.

The [all-equation residual figure](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/residuals.png)
shows final-window maxima of continuity 1.5055, k 0.038564, epsilon
0.75303 and liquid fraction 0.018371. These four fail the 1e−3
throughout-window indicator; the three momentum equations pass. The final
transcript still reports reversed outlet flow on 287 faces and turbulent-
viscosity-ratio limiting at 1e5 in 10 cells.

Final-window mean inlet pressure drops are 36.754 kPa for liquid and
36.965 kPa for steam. The domain maximum-mixture-speed report averages
100.462 m/s but reaches **934.429 m/s**, returning to 72.922 m/s at
N5000. The late excursion is a numerical-credibility limitation that the
final snapshot alone would conceal.

## Spatial evidence and comparison

[F3 — Final above-cap fields](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/F3-final-above-cap-fields.png),
[velocity components](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/F3-final-velocity-components.png)
and [initial fields](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/F3-initial-above-cap-fields.png)
use native facet values without interpolation on y=0.5, 1.5, 3 and 5 m.
The four nonempty planes are above the maximum collector top y=0.020 m;
initial/final geometry matches exactly. Section areas are 3.16472–3.16505 m².
One zero projected-area facet on each of the 1.5 m and 5 m planes contributes
zero to area-weighted means while its stored values are retained.
[Fresh N5000 field metadata](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/field-metadata.json)
identifies unqualified velocity fields as mixture and prefixed fields as
phase-2; the figure labels retain the exact API names.

All panels retain the common S20/S40 scales: liquid fraction 0–1, speed
0–80 m/s and components −80–80 m/s. No widening or clipping was needed;
S60's highest extracted section speed is 55.270 m/s. This endpoint section
value is distinct from the domain/history excursion above. Source hashes,
geometry checks and metadata are in the
[section summary](../../../../PyAnsys/output/p7b-s060-resume-20260921T113238Z/analysis/section-summary.json).

Liquid-rich outer-wall bands remain visible. Area-weighted final section
liquid fractions are 0.02031, 0.01872, 0.02816 and 0.04926 in ascending
height order. The 5 m value is greater than S40's 0.02566, despite smaller
whole-vessel inventory. This is an unconverged endpoint observation, not a
uniform improvement in upper separation with collector thickness.

| N4501–5000 comparison | S20 | S40 | S60 |
| --- | ---: | ---: | ---: |
| Mean whole liquid volume, m³ | 0.957893 | 0.785728 | 0.705993 |
| Mean applied removal, kg/s | 486.174 | 390.040 | 686.730 |
| Liquid mean absolute closure / feed | 336.821% | 252.603% | 502.533% |
| Mixture mean absolute closure / feed | 197.999% | 148.487% | 295.402% |
| Volume-window mean change / larger mean | 15.619% | 10.936% | 14.596% |

**Inferred:** increasing coverage changes the finite numerical trajectory but
has not resolved the steady-state problem. S60's lower mean inventory does
not offset its larger late imbalance and removal/velocity excursions. None
of the three completed children satisfies the conjunction of closure,
inventory stationarity and all-equation residual indicators. Their differences
do not isolate collector thickness or source coefficient as the sole cause.

**G1 update:** all five terminal dispositions and the [comparison](../results.md)
are now available. No required S60 evidence stream is missing. No additional S60
iterations, coefficient tuning or qualification is authorized by these results.
