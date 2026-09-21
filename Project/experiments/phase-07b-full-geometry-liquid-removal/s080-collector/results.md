# Phase 7b S80 — Results

**Status: 5,000-iteration discovery screen complete; evidence complete, numerical indicators failed.**

The 80% collector removes liquid but does not produce a balanced steady
solution. Mean liquid inventory is lower than in the other completed children,
but it continues increasing, source-inclusive mass closure remains strongly
open, and four active residual equations fail the screening threshold.
Completion is not physical qualification.

The exact run is
[p7b-s080-20260921T130348Z](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/manifest.json).
The [analysis summary](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/summary.json)
retains source hashes, evidence audits and complete fixed-window statistics.
The setup and claim limits remain those in [setup.md](setup.md).

## Observed

The common clean reference and fresh Hybrid initialization match S60's
[verified settings](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/common-reference-comparison.json).
The sole intended scientific change is collector thickness. Build checks
verified 78,608 collector cells, zero mask/zone disagreement, 6,177 uniquely
oriented interface faces and unchanged total mesh counts.

All 5,000 scalar and collector-flux records are finite, unique and complete
on N1–N5000. All seven residual histories are complete; ten identical
chunk-boundary repeats were deduplicated without conflict. The recorder reports
5,000 completed PC writes and no error, with checkpoint flux readbacks checked
by the runner. This is not an independent reread of every remote record or
an independent backup. Initial/prepared, checkpoint and matching final
case/data writes completed; [endpoint verification](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/endpoint-verification.json)
confirms steady N5000 and the final pair. All four final section exports
completed. Server case/data storage remains LOCAL_ONLY.

[F1 — Inventory, removal and collector crossing](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/F1-inventory-removal.png)
shows continuing whole-vessel buildup and strongly varying late removal.
At N5000 liquid inventory is **0.695543 m³ (613.309 kg)**, comprising
0.000801606 m³ (0.706832 kg) in the collector and 0.694741 m³ above it.

| Metric | N4001–4500 mean | N4501–5000 mean |
| --- | ---: | ---: |
| Whole liquid volume, m³ | 0.581998 | 0.646800 |
| Collector liquid volume, m³ | 0.000703443 | 0.00137228 |
| Native applied removal, kg/s | 257.216 | 502.207 |
| Recomputed current-field removal, kg/s | 257.419 | 502.175 |
| Gross liquid delivery to collector, kg/s | 283.154 | 562.700 |
| Gross liquid escape from collector, kg/s | 26.173 | 61.798 |
| Liquid net export at steam outlet / liquid feed | 12.52% | 14.08% |
| Vapour net export at steam outlet / vapour feed | 98.73% | 96.76% |

Final-window liquid volume spans 0.612025–0.695543 m³, with standard
deviation 0.0269167 m³ and fitted slope **+1.76333e−4 m³ per iteration**.
The change between window means is **+10.019%** of the larger mean,
exceeding the 1% convention. Numerical iteration trends are not physical
storage rates. Gross collector crossings are internal flows, not additional
external feeds or capture efficiencies.

[F2 — Conservation and outlet routing](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/F2-closure-routing.png)
uses the sum of individual signed boundary flows, positive into the vessel,
plus the signed native applied source exactly once for liquid/mixture.
Vapour has no direct source. Native applied removal at N equals recomputed
current-field removal at N−1 at stored precision for all 4,999 consecutive
pairs. Current-field named closure reports are not substituted for applied-
source closure. No inventory slope or Fluent Net report is added as a source.

| Applied-source closure, N4501–5000 | Signed mean, kg/s | Mean absolute imbalance / measured feed | ≤1% indicator |
| --- | ---: | ---: | --- |
| Liquid | −401.752 | 343.609% | Fail |
| Vapour | +2.61805 | 3.24458% | Fail |
| Mixture | −399.137 | 201.981% | Fail |

Mean applied removal is 502.207 kg/s against the liquid feed of
116.921 kg/s, with a final-window maximum of 823.499 kg/s. Large removal
with this open global balance does not demonstrate conservative steady capture.

The [all-equation residual figure](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/residuals.png)
shows final-window maxima of continuity 0.7624, k 0.033402, epsilon
4.6067 and liquid fraction 0.013636. These four fail the 1e−3
throughout-window requirement; the three momentum equations pass. The final
transcript still reports reversed outlet flow on 266 faces and viscosity-
ratio limiting at 1e5 in 4,205 cells.

Mean final-window inlet pressure drops are 33.324 kPa for liquid and
33.536 kPa for steam. The domain maximum-mixture-speed report averages
88.114 m/s but reaches **561.432 m/s**, compared with 83.427 m/s at
N5000. This excursion remains a numerical-credibility limitation even though
the endpoint is less extreme.

## Spatial evidence and bounded comparison

[F3 — Final above-cap fields](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/F3-final-above-cap-fields.png),
[velocity components](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/F3-final-velocity-components.png)
and [initial fields](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/F3-initial-above-cap-fields.png)
render native facet values without interpolation on y=0.5, 1.5, 3 and 5 m.
The nonempty planes are above the maximum collector top y=0.020 m;
initial/final geometry matches exactly, with areas 3.16472–3.16505 m².
The 1.5 m and 5 m planes each contain one zero projected-area facet, which
contributes zero to area-weighted means while stored values remain preserved.
[Fresh N5000 metadata](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/field-metadata.json)
identifies unqualified velocity fields as mixture and prefixed fields as
phase-2. The [section summary](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/section-summary.json)
retains geometry checks and source/metadata hashes.

The existing common scales remain valid: liquid fraction 0–1, speed
0–80 m/s, and components −80–80 m/s. S80's highest extracted endpoint
section speed is 63.020 m/s; no widening or clipping was needed. This is
distinct from the domain/history maximum above. Visible zero-speed patches
in the phase-2 panels correspond to zero or extremely small liquid fraction:
all 41 zero-speed facets across the four planes have alpha ≤9.902e−9,
as recorded in the [zero-phase-velocity audit](../../../../PyAnsys/output/p7b-s080-20260921T130348Z/analysis/zero-phase-velocity-audit.json).
They are preserved field values, not evidence of stagnant liquid in a
substantially occupied liquid region.

Liquid-rich outer-wall bands persist. Area-weighted final liquid fractions
are 0.01756, 0.01940, 0.04266 and 0.03384 in ascending-height order. The
3 m value exceeds S60's 0.02816 despite lower whole-vessel inventory.
These unconverged snapshots do not show a uniform improvement in upper
separation with collector thickness.

| N4501–5000 comparison | S20 | S40 | S60 | S80 |
| --- | ---: | ---: | ---: | ---: |
| Mean whole liquid volume, m³ | 0.957893 | 0.785728 | 0.705993 | 0.646800 |
| Mean applied removal, kg/s | 486.174 | 390.040 | 686.730 | 502.207 |
| Liquid mean absolute closure / feed | 336.821% | 252.603% | 502.533% | 343.609% |
| Mixture mean absolute closure / feed | 197.999% | 148.487% | 295.402% | 201.981% |
| Volume-window mean change / larger mean | 15.619% | 10.936% | 14.596% | 10.019% |

**Inferred:** S80 reduces this finite-horizon mean inventory but does not
satisfy the conjunction of closure, stationarity and all-equation residual
indicators. Its lower imbalance than S60 does not extend to a monotonic
thickness trend across all completed cases. Collector coverage alone has not
established steady conservative removal under the fixed treatment.

**G1 update:** S100 has a numerical-failure disposition and the complete
[five-case comparison](../results.md) is available. No required
S80 evidence stream is missing. These results do not authorize extra S80
iterations, source-strength changes or physical qualification.
