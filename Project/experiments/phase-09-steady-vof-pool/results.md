# Results — steady VOF pool feasibility

## Completed N1000–2000 extension: unqualified

**Observation:** the unchanged high-pool case reached N2000. The recovery job passed its exact 236-iteration completion verifier; final case/data, native reports, seven active residual histories, full-cell fields and terminal sections are preserved. Live reconciliation confirmed idle N2000, exited controller/worker and a free server1 lock. The two segments total exactly 1000 additional solves, with no duplicated parent iteration.

![Stitched continuation histories](../../../PyAnsys/output/phase09-preflight/user-extension-n2000/extension-review.png)

The dashed line marks the N1764 connection interruption. Native report and residual coordinates cover N1001–2000 without gaps; overlap values agree. The original N1764 gross-flux callback is missing. An unchanged-state N1764 callback captured by the recovery controller supplies that coordinate for the combined flux description, but does not retroactively restore the original event.

| Evidence, N1001–2000 | Observed | Required |
|---|---:|---:|
| Mean absolute liquid/vapor/mixture imbalance | 401.175 / 3.754 / 235.832% feed | each ≤0.5% |
| Maximum absolute liquid/vapor/mixture imbalance | 552.648 / 5.101 / 324.976% feed | each ≤1% |
| Whole-domain liquid inventory | 3990.817→3369.910 kg (−15.558%) | stationary |
| Whole/lower inventory range | 16.938 / 18.068% mean | ≤1% |
| Whole/lower half-window mean change | −8.281 / −8.878% | magnitude ≤0.25% |
| Final continuity / k / epsilon / volume fraction | 0.35136 / 0.008112 / 0.020294 / 0.006924 | all ≤0.001 |
| Maximum liquid reverse brine inflow / vapor reverse steam inflow | 32.206 / 16.789% respective feed | each <0.1% |

The last 200 iterations lost another 118.949 kg liquid. At N2000, vapor exits the brine outlet at 10.979 kg/s and liquid exits the steam outlet at 8.384 kg/s. Momentum residuals satisfy 0.001 but cannot compensate for the other failures. Full-cell N1000/N2000 comparison gives volume-weighted absolute liquid-fraction change 0.03481 and liquid-volume loss 0.70416 m³. These endpoint changes support ongoing redistribution; connected-interface stationarity and persistence are not established.

**Interpretation:** additional unchanged pseudo-time iteration did not establish conservative stationary drainage. The final liquid imbalance is smaller than at N1000, but still extreme, while inventory continues declining and continuity worsens. Neither physical time nor a physical drainage rate may be inferred from inventory change per steady iteration. A connection interruption is an execution defect, not scientific falsification.

**Conclusion and next decision:** close this bounded extension unqualified; select no further calculation. The original two-start independence test and save/reopen persistence requirements are not met. This does not prove that no steady physical solution exists. A useful next scope decision would be whether to establish the actual downstream pressure/head and drain resistance before selecting another boundary model; their present assumed values remain unvalidated. Do not silently change these, switch to transient, or tune again.

**Spend:** 4102 total solved iterations; 9.202 recorded controller-hours including the interrupted segment, excluding disconnected idle time and separate recovery I/O. Both are below the 12000-iteration/48-hour caps. All endpoints remain ineligible as qualified parents. Phase 7b stays closed and Shuhei's sessions remain untouched.

[Reproducible combined audit](../../../PyAnsys/output/phase09-preflight/user-extension-n2000/extension-review.json) · [recovery job proof](../../../PyAnsys/output/run-handoff/phase09-high-pool-n1764-to-2000-recovery/job_manifest.json)

## Earlier records

**Human-authorized continuation on 30 September 2026:** Andy requested resumption. Continue the preserved h_i=0.30 m, scale-0.1 endpoint from native N1000 to N2000, with unchanged physics and numerical settings. This explicitly extends the prior stopping allowance by one 1000-iteration block, within the original 12000-iteration/48-hour total budget. A four-hour execution guard bounds this block; earlier stop gates remain active. No endpoint is qualified. Phase 9 supervision was subsequently resumed by Andy for this bounded extension and terminal review; see CONTEXT.md and phase-state.yaml. Compare conservation, inventory drift, routing, all active residuals and spatial changes with N1000 before selecting further work. This single-start continuation cannot establish initial-condition independence or physical validity.


**Disposition at the original cutoff: closed unqualified.** See [closure.md](closure.md) and the
[matched two-start comparison](../../../PyAnsys/output/phase09/comparison/two-start-comparison.json).
All runs are stopped and preserved; no endpoint qualifies. The records below
document evidence and decisions leading to that disposition.

The first fresh pool has passed initialization and save/reopen verification.
No separator solution is qualified. The corrected zero-feed diagnostic completed
50 iterations after the first attempt stopped at N2 with an initialization
defect. The first full-feed smoke completed 50 iterations with verified evidence,
but remains unconverged. The N50–1050 continuation completed and is unqualified; Fluent is idle.

The verified initial pool contains 103,778 liquid cells and 4,096.769804 kg
of liquid. Velocity is zero. Modified pressure spans 1,120,000–1,133,581.830 Pa.
Liquid fraction and pressure arrays survived case/data reopening exactly; all
scientific settings matched. Fluent rewrote the report filename to a relative
path, so the runner explicitly rebinds each unique absolute report destination
and verifies native writes. Initialization metadata showed iteration 1 before
save and 0 after reopen, with zero solve commands issued; neither counter was
changed by the client.

The native patch initially applied reconstructed-interface/volumetric smoothing.
The selected binary initial patch now disables those controls, matching the
same cell-centroid predicate used for its pressure field. Monitoring-expression
and register-name errors were repaired before solving. These were setup errors,
not failed scientific tests.

- [Verified build and initial metrics](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/manifest.json)
- [Preservation of the previously loaded Andy endpoint](../../../PyAnsys/output/phase09-preflight/mesh-build-receipt.json)
- [Scientific question and gates](setup.md)

Phase 7b remains closed; E8 remains incomplete, and no old endpoint was used as
a qualified solution parent. Shuhei's sessions have not been used.

## Initial diagnostic and repair

[First diagnostic](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/h0p1-20260929T062514Z-rest-n00000-20260929T063759Z/run.json):
maximum speed 13.991 m/s at N1 and 74,041.201 m/s at N2; automatic stop verified,
endpoint pair and both native histories preserved. The largest velocities were
in vapor cells at the thin inlet region, not the pool drain. Liquid inventory
changed −0.03368%; this small change does not rescue the failed speed gate.

Observed setup defect: zero inlet velocities were set after full-feed
initialization, but the pre-solve native inlet fluxes still held
116.921232/80.689902 kg/s. Reported inlet fluxes became zero during the run.
The startup therefore was not a clean zero-feed equilibrium test. This does
not prove the stale flux caused the spike, but requires correction before a
scientific inference. The next diagnostic freshly initializes after setting
zero feeds and requires all initial inlet/net fluxes to be zero before solving.
Both completed iterations count against the phase budget. No numerical treatment
has yet been changed, and the smaller-pseudo-time option remains unused.

The corrected zero-feed diagnostic has verified initially zero phase inlet and
net fluxes. It remains a numerical diagnostic. Fluent 2025 R2 UG §27.8.1.7
warns that Global Time Step steady multiphase lacks guaranteed conservation
without separate phase inflow/outflow boundaries. Its rest thresholds therefore
cannot establish or reject full-feed steady feasibility. This documentation
restriction was recognized during the corrected bounded run; the full-feed
acceptance criteria have not been relaxed. The rest endpoint will not become
a qualified parent, nor be used in place of the independent fresh full-feed start.

## Corrected rest diagnostic

[Corrected run](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/h0p1-20260929T062514Z-rest-n00000-20260929T064221Z/run.json)
completed N1–50; paired endpoint, native reports/residual transcript, per-iteration
phase and native-mixture face-flux sums and full-cell endpoints were verified.
Initial native fluxes were zero. Liquid inventory increased from 4096.769804 to
4191.950569 kg (+2.32331%). Final maximum speed was 1.73085 m/s, with liquid net
inward flow 42.26103 kg/s. It did not meet the diagnostic quiescence flags. Native
mixture and phase flux sums agreed to 8.53e-14 kg/s; that accounting agreement does
not establish conservation or steady state.

Version-matched review found no pressure-convention error. Fluent applies
modified pressure to its pressure field and pressure boundary inputs; operating
density is the lightest phase, and the density-difference hydrostatic profile is
consistent. The customization manual identifies `SV_P` as cell-pressure storage.
Inferring the same modified-pressure convention for `SV_P` is supported by those
statements. Public SVAR writing does not explicitly document all auxiliary
face/gradient updates, so exact cell readback is not proof of every initialization
side effect. There is no positive evidence that such an API fault occurred.
Sources: [pressure inputs](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html),
[VOF body forces](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html),
[cell pressure storage](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_sec_using_udfs_parallel.html).

Decision: retain the pressure formula and proceed from the original verified
full-feed N0 pair, not the rest endpoint. No smaller-pseudo-time contrast has
been spent. Completed phase iterations: 52. The full-feed acceptance gates remain
unchanged.

## First full-feed smoke: N0–50

[Run receipt](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/h0p1-20260929T062514Z-flow-n00000-20260929T065443Z/run.json),
[analysis](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/h0p1-20260929T062514Z-flow-n00000-20260929T065443Z/analysis.json),
[balance/inventory/residual figure](../../../PyAnsys/output/phase09/h0p1-20260929T062514Z/h0p1-20260929T062514Z-flow-n00000-20260929T065443Z/balance-inventory-residual.png).

**Verified:** all 50 requested iterations completed without a stop condition.
The native case/data pair, complete seven-equation residual history, report
history, per-iteration signed and gross phase/native-mixture face fluxes,
full-cell endpoints and x=0/z=0 section fields are preserved. Independent
cell liquid inventory agrees with the native volume report. Native mixture
and summed phase fluxes agree to 3.13e-13 kg/s; this is bookkeeping consistency,
not conservation.

Liquid inventory decreased 4096.769804→4033.502098 kg (−1.54433%). Liquid above
y=0.5 m increased to 50.47237 kg. Final absolute phase/native-mixture imbalance
was 152.657% liquid, 1.193% vapor and 89.836% mixture, normalized by feed.
Final residuals: continuity 0.47027, k 0.024408, epsilon 0.044102, volume
fraction 0.0039339; momentum residuals were below 1e-3. Maximum speed was
43.7264 m/s. Gross reverse inflow occurred at both outlets; it is retained
separately and cannot qualify as drainage. The transcript warning scan found
reverse-flow reports, without divergence or limit messages.

**Interpretation:** no stationary solution or acceptance window exists. The
liquid excess outflow peaked near N22 and decreased toward N50, while fields
remained finite and phase fractions bounded. Fifty startup iterations cannot
settle whether the pool approaches balance. No physical storage rate or time
is inferred from the iteration history.

**Decision:** continue the exact N50 state to N1050 with unchanged model,
boundaries and pseudo-time scale. This is the first longer test of approach
to balance, not automatic qualification. Audit the endpoint before any further
batch. The second independent initial level and save/reopen persistence remain
outstanding. Total completed iterations before continuation: 102 (2 + 50 rest,
50 full feed); smaller-pseudo-time allowance remains unused.

The [N50–1050 job](../../../PyAnsys/output/run-handoff/phase09-h01-n0050-to-1050/job_manifest.json)
was launched through the repository run-control wrapper. Live callback evidence
confirmed N52, exact continuation-parent metric agreement, and no capture or
stop errors at that check. The job preserves/audits its terminal artifacts and
then invokes the completion handoff to the originating thread on completion or
block. This is a one-shot completion hook, not a restarted Phase 7b automation.
A later human pause takes precedence over the handoff prompt.

## N1050 status and reconciliation

The continuation completed 1000 solves and saved its paired endpoint, native
histories and spatial fields. A live status check confirmed idle Fluent at
N1050 and both endpoint files present. Liquid inventory fell 4033.502098→
2479.237405 kg (−38.5339%); final liquid imbalance was 268.448% of feed,
vapor 3.8388%, native mixture 157.266%. Final continuity residual was 0.93937.
Over N51–1050 mean absolute liquid imbalance was 362.350%; inventory half-mean
change was −25.3204%. Routing and convergence gates also failed. No steady
solution is qualified. This is evidence of severe drift in the tested setup,
not proof that every steady VOF pool model is impossible. Further unchanged
compute is not justified without reviewing the failed mechanism.

The runner retained an initial-state callback at N50 plus N51–1050, then
incorrectly counted 1001 samples as 1001 solves. Its terminal assertion failed
after the endpoint had already been preserved. This counting error is repaired:
solved iterations equal native end minus native start; all raw samples remain.
The original receipt is retained beside the reconciled receipt. Total phase
compute is 1102 solved iterations including rest diagnostics and the smoke.

The completion hook launched a CLI process but it failed with a thread-store
active-writer conflict; it did not resume analysis automatically. The original
job manifest records that failed attempt. No subsequent solver batch launched.
The earlier Project RUNNING label was stale and has been corrected.

## Diagnosis and selected next test

Offline full-cell reductions show the drain-height band −0.51<y<0 m changing
from volume-weighted liquid fraction 0.975 at N50 to 0.176 at N1050. The region
below y=−0.51 m changed from 1.000 to 0.844. These are regional occupancy
measures, not a connected-interface or flat-level determination. Vapor leaving
brine grew to 19.810 kg/s (24.55% of vapor feed); liquid leaving steam grew to
17.954 kg/s. Lower-region depletion accompanies increased upper inventory.
The final 200 iterations still lost about 278 kg total liquid; the drift was
not a completed startup adjustment.

Interpretation: the solution is losing the liquid seal at the drain. Developed
internal pressure and the assumed reservoir boundary may drive excessive
drainage, but numerical nonconvergence remains an alternative explanation.
Pressure-convention checks previously found no implementation error; the
external reservoir remains an assumption, not a plant-calibrated boundary.

Select the one predeclared numerical contrast, automatic scale 0.3→0.1, from
the preserved fresh N0 state. This keeps the experiment scientifically fixed
while testing sensitivity to the steady solver's pseudo-time step. Reduced
inventory drift alone cannot pass; same-iteration comparisons have unequal
numerical progress. See the added prospective contract in setup.md. No drain
pressure tuning, transient calculation or extra numerical sweep is selected.

The [scale-0.1 fresh child](../../../PyAnsys/output/phase09/h0p1-scale01-20260929T110727Z/manifest.json)
passed live settings comparison and save/reopen. Pressure and phase arrays match
the original fresh N0 exactly; velocities are zero and inventory is
4096.769804 kg. The only numerical delta is scale 0.3→0.1; verbosity is set to 1
to record actual automatic pseudo-step sizes. No physical boundary changed.
The [staged recovery job](../../../PyAnsys/output/run-handoff/phase09-scale01-recovery-screen/job_manifest.json)
executes N0–50, verifies its complete bounded artifacts and absence of a safety
or capture stop, then conditionally runs N50–1000. It uses utility mode with
CLI wakeup disabled; the existing overnight heartbeat owns the next scientific
review. The runner enforces the 07:30 execution deadline. This spends the one
allowed smaller-pseudo-time contrast; no further scale sweep is available.

## Recovery smoke and continuation status

The scale-0.1 smoke completed all 50 iterations, with paired endpoint, native
histories and spatial exports verified by the staged controller. Liquid
inventory changed −0.31350%; final liquid imbalance was 179.090% of feed,
vapor 2.26147% and mixture 105.039%. The smaller inventory change does not
establish improvement: numerical evolution is slower and closure still fails.
The planned N50–1000 continuation is active. At the 11:31 UTC heartbeat,
Fluent was independently verified iterating at N127, the owned controller was
alive and its server1 lock held. No stop/capture error was present. Continue
the predeclared bounded screen; do not alter settings mid-run. The acceptance
assessment must combine smoke N1–50 with continuation N51–1000, excluding a
repeated N50 callback if present. No qualification is claimed.

## Recovery N1000 result and final initial-level comparison

The staged scale-0.1 h_i=0.10 m screen completed N1000. Its controller exited,
the lock was free, and live Fluent was idle with both endpoint files present.
All recorded field, native history and spatial-export checks passed. The
N1–1000 history was stitched without the repeated N50 callback.

From fresh N0, liquid inventory fell 4096.769804→3619.562722 kg (−11.6484%).
Final liquid/vapor/native-mixture imbalances were 334.434%/3.14037%/196.594%
of feed. Continuity was 0.16942; k, epsilon and volume-fraction residuals also
failed. Mean liquid excess discharge increased from 196.66 kg/s in N1–500 to
423.89 kg/s in N501–1000; the final 200 iterations lost another 125.36 kg.
Vapor leaving brine reached 7.6541 kg/s. Drain-band liquid occupancy was 0.75285.
Neither lower residuals nor reduced inventory loss establishes convergence.

Decision: stop this low-level trajectory; no blind extension. Run the remaining
predeclared fresh h_i=0.30 m contrast at the same scale 0.1 for at most 1000
iterations. This tests whether initial submergence changes the failure while
holding the downstream condition fixed. It also exhausts the conservatively
counted 2000-iteration recovery allowance. Qualification remains absent, and no
claim of physical impossibility follows from either unconverged endpoint.

The fresh h_i=0.30 m build passed save/reopen. Initial liquid mass is
4652.236261 kg in 116720 liquid cells; velocities are zero and the pressure
patch matches the same height predicate. Its entire saved settings snapshot
matches the h_i=0.10 m scale-0.1 child, excluding only the report destination.
The higher-level screen uses the same 50 + verified 950 staged controller and
07:30 deadline; its job is `phase09-high-pool-scale01-screen`.

## Connection interruption and equivalent continuation

The N1000–2000 controller lost its connection after callback N1763. Live reconciliation found idle N1764, an exited controller and a free lock. The N1764 case/data pair, full-cell fields, terminal reports and native histories were recovered without reinitialization. The original error manifest is preserved alongside the run. The missing N1764 callback is an explicit gross-flux evidence gap; this is not a completed 1000-iteration block. Liquid inventory declined from 3990.817 to 3506.255 kg by N1764; no qualification is implied. Resume only the remaining 236 iterations with exact terminal-metric parent matching, unchanged settings and the existing deadline.
