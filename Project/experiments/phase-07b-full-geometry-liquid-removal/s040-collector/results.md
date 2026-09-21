# Phase 7b S40 — Results

**Status: 5,000-iteration discovery screen complete; numerical indicators failed.**

The 40% collector produces substantial liquid removal, but whole-domain mass
closure remains open and liquid inventory continues changing. Its smaller
late mean inventory and imbalance than S20 do not establish a balanced steady
solution or qualify S40 as the better collector.

The exact run is `p7b-s040-20260921T013001Z`; the
[execution manifest](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/manifest.json)
records the same clean N0 parent and fresh Hybrid initialization, 41,258
collector cells, zero mask/zone disagreement and 5,884 uniquely oriented
interface faces. Matching final case/data and all four final section exports
completed. The [analysis summary](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/summary.json)
contains source hashes, coverage audits and complete window statistics.
Scientific conditions remain in [setup.md](setup.md).

## Observed

Native scalar and collector-flux histories each contain 5,000 finite, unique
rows covering N1–N5000. All seven residual equations have complete coverage;
ten identical chunk-boundary repeats were deduplicated with no conflict.
Applied removal at N equals recomputed current-field removal at N−1 for
all 4,999 consecutive pairs at stored precision. The recorder reports 5,000
completed remote writes and no recorder error; checkpoint readbacks were
verified by the runner. This is not an independent reread of every remote
file or a verified separate backup. Case/data storage remains LOCAL_ONLY.

[F1 — Inventory, removal and collector crossing](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/F1-inventory-removal.png)
shows growth in whole-vessel liquid inventory with strongly varying removal.
At N5000, total water is **0.802170 m³ (707.330 kg)**, of which
0.00173128 m³ (1.52659 kg) is in the collector and 0.800439 m³ is above it.

| Metric | N4001–4500 mean | N4501–5000 mean |
| --- | ---: | ---: |
| Whole liquid volume, m³ | 0.699798 | 0.785728 |
| Collector liquid volume, m³ | 0.00128225 | 0.00106709 |
| Native applied removal, kg/s | 469.437 | 390.040 |
| Recomputed current-field removal, kg/s | 469.230 | 390.492 |
| Gross liquid delivery to collector, kg/s | 509.873 | 424.642 |
| Gross liquid escape from collector, kg/s | 41.933 | 35.211 |
| Liquid net export at steam outlet / liquid feed | 13.50% | 19.01% |
| Vapour net export at steam outlet / vapour feed | 97.00% | 97.62% |

The final-window liquid volume ranges from 0.754466 to 0.802340 m³,
with standard deviation 0.0123160 m³ and fitted slope
**+7.99570e−5 m³ per iteration**. The change between window means is
**+10.936%** of the larger mean, exceeding the 1% convention. Steady
iterations are numerical coordinates, so this slope is not a physical
storage rate. Internal gross crossings are not additional external feeds.

[F2 — Conservation and outlet routing](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/F2-closure-routing.png)
uses individual signed boundary flows, positive into the vessel, plus the
signed native applied mass source once for liquid/mixture. Vapour has no
direct source. Raw named closure reports based on current-field removal are
not substituted for this applied-source accounting; no inventory slope or
Fluent Net report is added as another source.

| Applied-source closure, N4501–5000 | Signed mean, kg/s | Mean absolute imbalance / measured feed | ≤1% indicator |
| --- | ---: | ---: | --- |
| Liquid | −295.347 | 252.603% | Fail |
| Vapour | +1.92006 | 2.37955% | Fail |
| Mixture | −293.427 | 148.487% | Fail |

The mean applied removal, 390.040 kg/s, exceeds the liquid feed of
116.921 kg/s while the source-inclusive balance remains far from closure.
This is a numerical imbalance, not demonstrated physical capture efficiency.

The [residual figure](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/residuals.png)
shows final-window maxima of 0.9928 for continuity, 0.024509 for k,
0.59738 for epsilon and 0.012886 for liquid fraction. These four fail
1e−3 throughout-window screening; only the three momentum equations pass.
The final transcript still reports viscosity-ratio limiting at 1e5 in
7,030 cells and reversed outlet flow on 287 faces.

Final-window mean pressure drops are 31.931 kPa at the liquid inlet and
32.142 kPa at the steam inlet. The domain maximum-mixture-speed report has
a final-window mean of 91.601 m/s but a **614.192 m/s maximum**, falling to
115.345 m/s at N5000. This excursion is retained as a numerical-credibility
limitation; an endpoint image alone would conceal it.

## Spatial evidence and comparison

[F3 — Final above-cap fields](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/F3-final-above-cap-fields.png),
[velocity components](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/F3-final-velocity-components.png)
and [initial fields](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/F3-initial-above-cap-fields.png)
render native facet values without interpolation on y=0.5, 1.5, 3 and 5 m.
All are above the common maximum collector top y=0.020 m. Initial/final
geometry matches exactly; the four nonempty section areas are
3.16472–3.16505 m². The 1.5 m and 5 m sections each include one facet
with zero projected area; it contributes zero to area-weighted means and
its stored values are retained. [Run-local field metadata](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/field-metadata.json)
identifies unqualified pressure/velocity fields as mixture and prefixed
fields as phase-2; exact API field names remain on the panels.

Liquid-rich outer-wall bands remain visible at all heights. The endpoint
area-weighted liquid fractions are 0.02530, 0.02854, 0.06619 and 0.02566
in ascending-height order. The 3 m value is greater than S20's 0.04123,
even though S40's whole-vessel inventory is smaller; the endpoint spatial
response is not a uniform reduction with increased collector thickness.
Both cases remain unconverged, limiting physical interpretation.

S40's section speed peaks at 76.028 m/s, exceeding the previous S20
50 m/s colour range. **Both S20 and S40 panels were regenerated** with
common speed limits 0–80 m/s, component limits −80–80 m/s and liquid
fraction 0–1; no values were clipped. These are section endpoint limits,
not the domain/history maximum above. The
[shared scales](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/shared-section-scales.json)
and [section evidence summary](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/section-summary.json)
preserve the rendering and source checks. Widen and regenerate all cases if
later cases exceed these limits.

| N4501–5000 comparison | S20 | S40 |
| --- | ---: | ---: |
| Mean whole liquid volume, m³ | 0.957893 | 0.785728 |
| Mean applied removal, kg/s | 486.174 | 390.040 |
| Liquid mean absolute closure / feed | 336.821% | 252.603% |
| Mixture mean absolute closure / feed | 197.999% | 148.487% |
| Total-volume slope, m³/iteration | −6.73387e−5 | +7.99570e−5 |
| Liquid carryover / feed | 21.01% | 19.01% |

**Inferred:** increasing the collector from 20% to 40% changes the finite
trajectory, reducing these particular mean inventory and imbalance metrics.
It does not resolve the central steady-state failure: source-inclusive
closure, inventory stationarity and all-equation residual requirements remain
unsatisfied, and S40 retains late velocity excursions. This two-case comparison
does not isolate the source coefficient or collector coverage as the sole cause.

**G1 update:** all five terminal dispositions and the [comparison](../results.md)
are now available. No required S40 evidence stream is missing. No extra S40 iterations, source-strength tuning or
qualification is justified by these observations. The recorded settings and
5,000-iteration cap remain unchanged.
