# P7-E5-CZ-G100-CONT2500 results

## Status and claim boundary

`COMPLETE_VERIFIED` for the declared attached discovery continuation, with
one explicit final-runtime-readback limitation recorded below. The exact
verified G100 active-500 case/data pair from
`P7-E5-CZ-G100-student-20260910T045745Z` was continued for `2,000` additional
controller-active iterations, reaching active `2,500` and approximately native
iteration `3,000`.

These are bounded numerical observations for active iterations `501--2,500`
under the unchanged G100 model. They are not qualification evidence and do not
establish physical outlet fidelity, plant drainage, mesh independence, steady
convergence, or removal of all upper liquid. The phase-level discovery gate
therefore remains human-controlled and no automatic follow-on was launched.

## Decision-gate recommendation

`RETURN_TO_HUMAN — unchanged bottom-only cell-zone mechanism weakened.`

The continuation does not meet the useful-continuation signal. Total liquid
inventory continues to drift upward, the lower-zone inventory depletes and then
rebounds rather than approaching a bounded late trend, and bottom phase-2
liquid outflow remains exactly zero. The source command reaches its predeclared
cap while the mixture boundary closure remains open. Vapor bottom outflow is
also zero, which is acceptable only in the narrow phase-routing sense; it does
not compensate for the missing liquid removal path.

The next mechanism discussion should return to the human for the already
specified distinct bottom collector/outlet or localized phase-gated direction.
No new branch, zone enlargement, outlet change, source-law change, UDF,
patch/reset, qualification run, or Auto Loop follow-on is authorized by this
record.

## Observed

### Parent, topology, and frozen setup

- The parent identity readback used the exact case/data pair recorded in the
  setup contract: `P7-E5-CZ-G100-student-20260910T045745Z`, active `500`,
  approximately native `1,000`.
- The final readback retained exactly the two fluid zones
  `p7-e5-lower-y010` and `separator-purnanto`; global mesh counts remained
  `342,609` cells, `1,647,633` faces, and `1,046,255` nodes.
- The lower-zone geometric volume remained
  `0.3083026098250161 m^3`, with the frozen `0 <= y <= 0.10 m` interpretation.
  The region remained a multiphase fluid zone; it was not treated as a
  liquid-only region.
- The final source readback retained phase-1 mass source disabled, lower-zone
  phase-2 mass source enabled, separator sources disabled, and lower-zone
  mixture x/y/z momentum sources enabled. The gain remained `G=1.00`, the
  controller update cadence remained every `50` active iterations, and the
  command bound remained `146.15 kg/s`.
- A paired recovery state was saved before takeover, a paired active-500
  continuation-start state was saved after parent/setup readback, and paired
  checkpoints were saved at active `750`, `1,000`, `1,250`, `1,500`, `1,750`,
  `2,000`, `2,250`, and `2,500`.

### Histories and controller/source evidence

- The continuation report histories contain `2,001` points each, covering
  native iterations `1,000--3,000`; combined with the parent and de-duplicated
  at the handoff, the liquid and residual histories cover native
  `501--3,000` (`2,501` points).
- The continuation contains `40` controller readbacks at active
  `550--2,500`, i.e. every `50` active iterations after the active-500
  parent. The combined parent-plus-continuation audit contains `50` controller
  updates.
- The controller reference values were `M* = 149.424869 kg` and
  `DeltaMref = 223.250694 kg`. The command increased to the cap and remained
  at `146.15 kg/s`; `38` of the `50` combined controller updates were
  saturated.
- The integrated phase-2 user-source audit matched the analytical negative
  command with maximum absolute `get_sum + command` error
  `1.99e-13 kg/s`. The direct phase-1 source was disabled in every audited
  event and in the final source tree.
- The final applied lower-zone phase-2 source density was
  `-474.0472358730619 kg/(m^3 s)`. The source value is a uniform lower-zone
  source readback; it is not a measured bottom liquid outflow.

### Inventory and routing

- Over continuation active `501--2,500` (native `1,001--3,000`), total liquid
  mass rose from `333.0459 kg` to `2,650.5645 kg`, with fitted slope
  `+1.23978 kg/native iteration`.
- Over the final active `2,001--2,500` window (native `2,501--3,000`), total
  liquid mass rose from `2,144.6682 kg` to `2,650.5645 kg`, with fitted slope
  `+0.74294 kg/native iteration`. The slope decreased relative to the full
  continuation window but remained positive.
- Total liquid volume over the continuation rose from `0.37794 m^3` to
  `3.00787 m^3`; the final-window fitted slope remained positive at
  `+0.00084309 m^3/native iteration`.
- The lower-zone phase-2 liquid mass over controller samples in active
  `501--2,500` ranged from `0.0571 kg` to `59.8333 kg`, beginning at
  `13.3382 kg` and ending at `59.8333 kg`, with fitted slope
  `+0.01271 kg/native iteration`.
- In the final active `2,001--2,500` controller window, lower-zone phase-2
  mass ranged from `16.4804 kg` to `59.8333 kg`, ending at `59.8333 kg`, with
  fitted slope `+0.03493 kg/native iteration`. The corresponding final
  phase-2 volume was `0.0678990 m^3`, about `22%` of the lower-zone geometric
  volume.
- Bottom phase-2 liquid outflow was exactly `0 kg/s` across the parent,
  continuation, and final windows. Bottom phase-1 vapor outflow was also
  exactly `0 kg/s` across all three windows.

### Balances, residuals, and warnings

- Across the 50 controller sample points, phase-2 boundary net flux had mean
  `108.761 kg/s` and ranged from `69.039` to `116.914 kg/s`. Phase-2 boundary
  net plus user source had mean `-17.272 kg/s` and ranged from `-77.111` to
  `106.814 kg/s`.
- Phase-1 boundary net flux had mean `0.0733 kg/s` and ranged from
  `-0.7328` to `+0.9331 kg/s`; no direct phase-1 user source was enabled.
- Mixture boundary net flux had mean `108.832 kg/s`. The normalized mixture
  boundary imbalance, using the recorded `197.61 kg/s` scale, had mean
  `0.5507`, minimum `0.3496`, maximum `0.5891`, and final value `0.5890`.
- In the final native `2,501--3,000` window, the continuity residual had mean
  `0.7149`, maximum `1.1258`, and final value `0.7464`. The final means for
  x-, y-, and z-velocity residuals were `5.65e-4`, `6.03e-4`, and `5.95e-4`;
  `k`, `epsilon`, and phase-2 volume-fraction residual means were `8.33e-3`,
  `3.19e-2`, and `7.80e-3`, respectively.
- The transcript records recurring reversed-flow messages at pressure outlet
  `30` and turbulent-viscosity limiting to the ratio `1e5` in thousands to
  tens of thousands of cells. No floating-point exception or AMG-divergence
  termination occurred in this continuation.

## Inferred

- The positive total-inventory trend is persistent over the declared
  active `501--2,500` continuation window. Its late slope is smaller than the
  full continuation slope but does not approach zero or become negative.
- The lower-zone liquid response is not bounded in the observed late window:
  it falls close to zero for part of the continuation, then rebounds strongly
  and finishes at its largest audited value. This is evidence of non-monotonic
  redistribution under the unchanged model, not evidence of a stable lower
  collector state.
- The unchanged lower-zone source does not produce a measurable bottom
  phase-2 liquid transport path in this run. The zero bottom phase-2 flux,
  rising total inventory, and capped command jointly weaken the original
  bottom-only cell-zone mechanism for this question.
- The zero bottom vapor flux and zero direct phase-1 source show no observed
  bottom vapor loss in these histories, but the open mixture balance and
  residual/warning behaviour prevent a stronger closure or convergence claim.
- The continuation therefore supports a mechanism-level return to the human,
  not promotion: consider only the distinct bottom collector/outlet or
  localized phase-gated direction already named by the decision gate.

## Assumed

- The active coordinate is continued from the verified parent active `500`;
  the reported native coordinate is the recorded approximately one-to-one
  continuation coordinate, with the parent/continuation report handoff
  de-duplicated at native `1,000`.
- The report histories and residual histories are treated as the primary
  horizon evidence because they reach the requested native `3,000` endpoint
  and retain the complete continuation samples.
- The parent package remains the authoritative source for the unchanged G100
  setup values before active `501`; parent observations are shown only as the
  continuation anchor and are not reinterpreted as new continuation evidence.

## Missing Info and limitations

- The final manifest's post-reopen runtime snapshot reports
  `current_iteration: 1556`, which is inconsistent with the final report and
  residual extents to native `3,000` and with the terminal pair-exists and
  pair-reopened checks. This stale runtime-counter field is preserved as an
  explicit limitation; the run is not used for qualification.
- The final paired artifacts are present at the remote Fluent run root and the
  manifest, reports, residuals, transcript, and analysis summary are written
  locally. No separate OneDrive promotion was performed in this handoff, so
  the durable placement claim is limited to those verified remote/local paths.
- No distinct physical bottom collector/outlet or localized phase-gated source
  was tested here; either would be a separate human-approved direction.
- This continuation does not resolve the broader phase-level discovery or
  qualification gates. No physical-time drainage, plant-scale performance,
  mesh-independence, or outlet-fidelity claim is made.

## Core figures

The four required figures were generated from the parent-plus-continuation
histories with the stated units and sign convention. The bottom-outflow plots
negate Fluent's raw boundary flux so positive values would denote outflow;
both bottom phase curves remain at zero.

- F1 — total liquid inventory (recorded path; file not in this checkout): `figures/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z/F1-total-liquid-inventory.png`
- F2 — lower zone and bottom routing (recorded path; file not in this checkout): `figures/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z/F2-lower-zone-and-bottom-routing.png`
- F3 — adaptive controller and source audit (recorded path; file not in this checkout): `figures/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z/F3-controller-and-source-audit.png`
- F4 — balances and residuals (recorded path; file not in this checkout): `figures/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z/F4-balances-and-residuals.png`

## Durable evidence

- [Continuation setup](setup.md)
- [Resolved run paths](run-paths.yaml)
- Continuation manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone_cont2500/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z-manifest.json`
- Continuation reports (local generated artifact): `PyAnsys/output/phase07_cell_zone_cont2500/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z-reports.json`
- Continuation residual history (local generated artifact): `PyAnsys/output/phase07_cell_zone_cont2500/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z-residuals.json`
- Solver transcript and warnings (local generated artifact): `PyAnsys/output/phase07_cell_zone_cont2500/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z-residuals-transcript.txt`
- F1-F4 analysis summary (local generated artifact): `PyAnsys/output/phase07_cell_zone_cont2500/P7-E5-CZ-G100-CONT2500-student-20260910T070332Z-analysis/summary.json`
- Continuation runner (historical path; file not retained): `PyAnsys/scripts/setup/run_p7_e5_cz_cont2500.py`
- Analysis script (historical path; file not retained): `PyAnsys/scripts/analysis/analyze_p7_e5_cz_cont2500.py`
- [Exact G100 parent results](../p7-e5-cz-g100/results.md)
