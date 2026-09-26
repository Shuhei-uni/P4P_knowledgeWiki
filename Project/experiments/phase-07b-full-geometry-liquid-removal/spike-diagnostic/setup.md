# Phase 7b E3 — S40-T020 diagnostic replication

## Authority and purpose

On 22 September 2026 Andy returned home, requested a new run, and explicitly
selected “Diagnostic repeat of S40-T020” after being offered the unchanged
tau 0.02 s, fresh-start, 5,000-iteration case with extra spike diagnostics.
This supersedes his earlier temporary no-new-run instruction. This E3 packet
authorizes one case, S40-T020-DIAG, and its analysis. Andy's later
[autonomous-investigation instruction](../convergence-investigation/plan.md)
governs post-G3 work; it does not modify this run.
Phase 7b remains appropriate because the geometry and scientific question
are unchanged. E2/G2 remains a completed historical comparison.

Classification: **REPLICATION with additional instrumentation**. The prior
[T020 result](../lower-sink-rate/results.md) associates its largest late
epsilon residual with a maximum-speed excursion at N4767, but its retained
fields cannot locate that event. A repeat can locate sampled excursions and
test whether the broad numerical behaviour recurs. It cannot prove a unique
cause, identical iteration timing, or physical validity.

## Parent, invariants and horizon

Use the original clean N0 pair
`C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal/case-data/p7b-clean-initial-20260912T080713Z.cas.h5`
and its matching `.dat.h5`, with identical Hybrid options. Verify the original
S40 manifest `p7b-s040-20260921T013001Z`; compare scientific results to
`p7b-s40-t020-resume-20260921T231240Z`. Preserve the currently loaded T100
N5000 endpoint before replacement. Unique checkpoint destinations must refuse
overwrites, including any graphics view names created later.

Retain every scientific/numerical setting from [E2](../lower-sink-rate/setup.md):
S40 mask, tau 0.02 s, original steady Mixture/RNG model and source bindings,
full feed and split velocity inlets, Energy/DPM/EWF off, no liquid patch,
profile update interval 1, same controls and discretization. Added report
definitions, synchronous field reads and local evidence writes are the only
delta. No new source/Jacobian treatment, numerical tuning, coefficient point,
extension or qualification is authorized.

Absolute cap: 5,000 steady iterations, including the N50 instrumentation smoke.
Use the existing single controller and 500-iteration checkpoint chunks after
N50. Poor balances or spike thresholds are not early-stop rules. On uncertain
RPCs reconcile actual progress before retry. Recover numerical failure as an
explicit partial disposition; never terminate Fluent.

## Additional evidence, declared before compute

Retain all E2 scalar, seven-residual, exact-face collector-flux, applied versus
current-expression source and paired checkpoint evidence. Keep initial/final
horizontal and full-height axial fields. Add native maximum k and epsilon
reports every iteration, without changing any equation.

The existing synchronous iteration-ended callback also reads the native
maximum mixture speed. It captures whole-cell fields at N0, N50, every 500,
and N2600/N2700/N2800. For the first speed at or above 500 m/s in each
250-iteration band, capture that iteration and its N+1/N+5 successors (within
the cap). This bounds overhead while sampling growth/relaxation. It is a
speed-triggered sample, not exhaustive capture of every residual spike.
Record every trigger decision so unsampled spikes remain visible.

Store mixture U/V/W, pressure, k, epsilon, liquid volume fraction and raw
mixture/phase-2 `SV_MASS_IMBALANCE`, alongside fixed cell coordinates/volumes.
Raw imbalance storage is not yet calibrated as a physical balance or scaled
equation residual. Preserve its identity; do not substitute it for native
applied-source accounting. Match cell ordering across domains and verify
field-reduced speed, k, epsilon and liquid inventory against native reports.
Check the iteration before and after each snapshot. Retain coordinates and
co-located values at top speed/k/epsilon cells; array indices are local to
the snapshot, not asserted global cell IDs.

Capability proof on the preserved T100 endpoint:
`PyAnsys/output/phase07b-e3-capability-20260922T071037Z/receipt.json`.
Cell-derived speed matches native exactly; liquid volume agrees within
roundoff. This proof issued zero iterations. N0 and N50 repeat-specific
proofs are required before accepting the long-run instrumentation.

## Analysis and G3 decision

Use cfd-numerical-analysis. Minimum deliverable: (1) raw residual/speed/source
histories with sampled events marked, compared to original T020; (2) an event
table of location, timing, local alpha/pressure/k/epsilon and relaxation;
(3) native Fluent spatial views through selected hotspot coordinates, on
common scales, from preserved pairs where available; and (4) original E2
late-window balance, stationarity, residual and source-lag indicators.
Raw cell arrays enable localisation, but are not native spatial screenshots;
do not synthesize a Fluent-looking rendering or claim an unsaved event pair
exists. Native checkpoint views may bracket rather than coincide with events.

Compare hotspot placement inside/outside the collector and near its boundary,
the onset around N2700, and coupling to source/inventory/phase flux. Separate
observations from explanations: recurrence/localisation supports a targeted
next diagnostic, not causality. No recurrence is evidence about variability,
not proof of stability. Return the one-case disposition, missing evidence,
competing explanations and next supported decision. After G3, the later
autonomous-investigation instruction governs further research and case
selection; keep the existing heartbeat active for that work.
