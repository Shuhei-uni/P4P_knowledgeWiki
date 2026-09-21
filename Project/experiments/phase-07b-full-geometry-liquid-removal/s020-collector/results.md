# Phase 7b S20 — Results

**Status: 5,000-iteration discovery screen complete; numerical indicators failed.**

S20 removes liquid once it reaches the collector, but this finite screen does
not establish a balanced steady solution. The full-domain applied-source mass
balance remains strongly open, liquid inventory changes between the prescribed
late windows, and continuity, k, epsilon and liquid-fraction residuals exceed
the declared threshold. No case promotion, physical capture efficiency or
qualification follows from completion.

The exact run is `p7b-s020-20260920T221831Z`; its
[execution manifest](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/manifest.json)
records the prepared, 50-iteration, 500-interval and matching final case/data
pairs. The [analysis summary](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/summary.json)
contains source hashes, coverage checks and complete fixed-window statistics.
Scientific conditions and claim limits remain in [setup.md](setup.md).

## Observed

All 5,000 native scalar-history rows and collector-flux rows are present,
finite and unique. All seven residual histories cover iterations 1–5,000;
ten repeated chunk-boundary rows are identical and are deduplicated without
conflict. The recorder reports 5,000 completed PC writes, with checkpoint
readback checks performed by the runner. A completed write record does not
mean every remote file has been independently reread. Matching final case/data
writes and four final section exports completed. Server case/data storage
remains LOCAL_ONLY; an independent backup is not established by this analysis.

[F1 — Inventory, removal and collector crossing](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/F1-inventory-removal.png)
shows continuing whole-vessel buildup over most of the run, followed by a
smaller declining trend in the final 500 iterations. At N5000 the liquid
inventory is **0.935870 m³ (825.222 kg)**, comprising 0.000926483 m³
(0.816945 kg) in the collector and 0.934944 m³ above it.

| Metric | N4001–4500 mean | N4501–5000 mean |
| --- | ---: | ---: |
| Whole liquid volume, m³ | 0.808277 | 0.957893 |
| Collector liquid volume, m³ | 0.00138338 | 0.00132738 |
| Native applied removal, kg/s | 505.696 | 486.174 |
| Recomputed current-field removal, kg/s | 506.237 | 485.744 |
| Gross liquid delivery to collector, kg/s | 604.267 | 569.657 |
| Gross liquid escape from collector, kg/s | 97.720 | 85.932 |
| Liquid net export at steam outlet / liquid feed | 18.45% | 21.01% |
| Vapour net export at steam outlet / vapour feed | 96.67% | 96.85% |

The final-window whole-liquid volume spans 0.930328–0.976029 m³,
with standard deviation 0.0138673 m³ and fitted slope
−6.73387e−5 m³ per iteration. Its window-mean change is **+15.619%**
using the larger of the two window means, exceeding the 1% screening
indicator. This compares steady numerical iterations; it is not a physical
storage rate. Mean applied removal is 486.174 kg/s against a fixed liquid
feed of 116.921 kg/s. Gross delivery and escape are internal crossings, not
independent external feeds or capture efficiencies.

[F2 — Conservation and outlet routing](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/F2-closure-routing.png)
uses the sum of individual signed boundary flows (positive into the vessel)
plus the **signed native applied source exactly once** for liquid and mixture;
vapour has no direct source. The named current-field closure reports in the
raw file use recomputed removal and are not substituted for applied-source
closure in this analysis. For every available consecutive pair N2–N5000,
native applied removal at N equals recomputed removal at N−1 at the stored
precision (4,999 pairs, maximum absolute difference zero).

| Applied-source closure, N4501–5000 | Signed mean, kg/s | Mean absolute imbalance / measured feed | ≤1% indicator |
| --- | ---: | ---: | --- |
| Liquid | −393.816 | 336.821% | Fail |
| Vapour | +2.54453 | 3.15347% | Fail |
| Mixture | −391.268 | 197.999% | Fail |

The source is neither counted twice nor corrected with an inventory slope.
The large negative liquid/mixture closures persist using the native applied
source. Apparent sink activity is therefore not evidence of conservative,
steady removal.

The [all-equation residual figure](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/residuals.png)
also fails the required conjunction. Final-window maxima are continuity
0.85602, k 0.0096821, epsilon 0.18167 and liquid fraction 0.0093179;
all exceed 1e−3. The three momentum residuals remain below 1e−3 throughout
that window. The transcript still reports turbulent-viscosity limiting
(9,558 cells at the final iteration) and reversed flow at the steam pressure
outlet (277 faces at the final iteration). Low momentum residuals alone do
not establish steady convergence.

Final-window mean liquid-inlet and steam-inlet pressure drops are 32.382 and
32.593 kPa, respectively; the explicitly mixture-context maximum-speed report
averages 80.705 m/s. Their full ranges and slopes are retained in the summary.

## Spatial evidence and interpretation

[F3 — Final above-cap fields](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/F3-final-above-cap-fields.png)
and the [velocity-component panels](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/F3-final-velocity-components.png)
render native extracted facet values on y=0.5, 1.5, 3 and 5 m, without
interpolation or smoothing. The matching
[initial fields](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/F3-initial-above-cap-fields.png)
use identical geometry and scales. All planes are above the maximum possible
collector top, y=0.020 m. Initial/final vertex and connectivity arrays match
exactly; section areas are 3.16472–3.16505 m². One zero projected-area facet
on each of the 1.5 m and 5 m planes contributes zero to area-weighted means;
all stored values are retained. Geometry checks and field hashes are in the
[section summary](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/section-summary.json).

The final liquid-fraction maps show liquid-rich outer-wall bands at all four
heights, with local maxima 0.960–0.980. Section area-weighted liquid fractions
are 0.03049, 0.04373, 0.04123 and 0.03392 in ascending-height order. These are
unconverged endpoint snapshots. The velocity panels retain exact API field
names. A later read-only [field-metadata query](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/field-metadata.json)
during S40 in the same Fluent session/model explicitly identifies unqualified
pressure/velocity fields as `mixture` and the `phase-2-*` fields as `phase-2`.
This corroborates the mixture/liquid field identities used for S20; it is not
a second extraction from S20. The scalar maximum-mixture-speed report also
has explicit phase context.

Use common liquid-fraction limits 0–1, speed limits 0–80 m/s and signed
component limits −80–80 m/s for the current panels. The
[scale file](../../../../PyAnsys/output/p7b-s020-20260920T221831Z/analysis/section-scales.json)
is reusable for later cases. If any case exceeds these ranges, widen them and
regenerate every comparison panel; do not clip a later case. No collector-
thickness effect can yet be inferred from one completed child.

**Inferred:** liquid reaches S20 and the sink remains active at a substantial
rate, but the observed source-inclusive mass imbalance, changing inventory,
residuals and limiting prevent a credible balanced-steady claim. Neither
insufficient collector thickness nor the finite source coefficient is isolated
as the sole cause by this case.

**G1 update:** all five terminal dispositions and the [comparison](../results.md)
are now available. No required S20 evidence stream is missing.
No extra S20 iterations, coefficient adjustment or physical qualification is
authorized by these results. Return all five observations at G1.

Earlier N0 expression/API failures and the separate 50-iteration source proof
remain [technical diagnostics](../diagnostics.md). They are not part of this
completed 5,000-iteration scientific history.
