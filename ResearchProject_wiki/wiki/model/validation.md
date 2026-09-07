# Validation

## Setup 07n calibrated-pressure 70-step balance gate (failed diagnostic 2026-08-28)

- Lineage/settings gate passed: independent checksum-bound server-2 step 90,
  Fluent 2024 R2/16 ranks, explicit VOF/PISO, fixed 0.05% feeds,
  `dt=1.28e-4 s`, 100 inner iterations, DPM zero/off, EWF off and no sources.
- The one-factor pressure schedule held `1,122,263.621237 Pa` through step 10,
  then `1,122,286.840068 Pa` through completed step 70.
- Numerical/physical hard gates passed: final-two continuity
  `7.90715e-4/7.93757e-4`, Courant `0.00764008`, VOF `[0,1]`, finite
  pressure/velocity, brine-face liquid VF `1.0`, zero cross-phase outlet
  leakage, exact clock and unchanged reported inventory.
- Sustained balance gate failed: steps 61-70 maximum absolute liquid/vapor/
  total imbalance was `0.01155471/0.0000760171/0.011478693 kg/s`, above the
  `0.005 kg/s` liquid/total limit. Step-70 liquid storage-closure residual was
  `0.011343928 kg/s`; the inventory report is too coarse to validate a level.
- Classification: `diagnostic / unresolved calibrated pressure-step 0.05%-feed
  long hold`; `eligible_parent:false`, no resume and no unchanged repeat. This
  fails constant-level validation while retaining evidence for numerically
  stable resolved drainage and an emergent liquid steam seal.

## Setup 07n sustained 0.05%-feed balance gate (failed diagnostic 2026-08-26)

- Common lineage/settings gate passed at each independent start: checksum-bound
  server-2 step 90, Fluent 2024 R2/16 ranks, explicit VOF/PISO, fixed feeds,
  DPM zero/off, EWF off and no sources/sinks.
- Fixed-pressure gate failed after 36 credited steps: continuity
  `7.91749e-4` and Courant `0.00452474` passed, but liquid/total imbalance was
  `-0.050185643/-0.049855477 kg/s`.
- Delayed gain-0.25 controller completed 50 steps but failed the five-step
  sustained balance gate; maximum absolute liquid/total imbalance over steps
  46-50 was `0.019462106/0.019334063 kg/s`.
- Delayed gain-0.05 controller stopped after 47 credited steps because the
  following solve lost its stream. Its steps 43-47 maximum absolute
  liquid/total imbalance was `0.03967104/0.039410044 kg/s`. The unobserved
  next step is not credited.
- Across credited endpoints, VOF stayed `[0,1]`, brine-face liquid VF stayed
  `1.0`, vapor-through-brine and liquid-through-steam stayed zero, inventory
  was unchanged and continuity/Courant remained bounded. These passes do not
  override the failed mass/storage closure gate.
- Classification: diagnostic/unresolved; all endpoints
  `eligible_parent:false`. The accepted ten-step result remains valid only as
  a bounded startup diagnostic, not long-time constant-level validation.

## Setup 07n 0.05%-feed pathline-video provenance gate (accepted post-processing diagnostic 2026-08-25)

- Exact source pair: independent server-2 step 100 / `t=0.00639 s`, hashes
  `d0247380...bd52` / `38447356...e97b`; Fluent 2024 R2 and 16 ranks.
- Source-state readback passed for pressure, 0.05% inlet rates, phase identity,
  clock, DPM zero/off, EWF off and all numerical sources off.
- Accepted release: `liquidinlet` exactly; 827 massless seeds and 12 retained
  pathline-integration frames. Rejected release: requested `steaminlet` read
  back as `wall-fluid` and was excluded.
- Mutation gate passed: zero initialization, physical steps, DPM updates,
  boundary/model changes and case/data writes. The accepted endpoint remained
  resident after export.
- Claim limit: pathlines use the shared frozen VOF carrier velocity. They do not
  validate liquid-particle routing, steam carry-under, carryover or separator
  efficiency and must not be interpreted as physical-time droplet histories.

## Setup 07n resolved low-feed drainage gate (accepted diagnostic 2026-08-25)

- Lineage: independent server-2 clean step-90 pair, cold-loaded per member;
  case/data hashes 763fae...fd22 / 9513a9...ae6b7; Fluent 2024 R2, 16 ranks.
- Accepted member: 0.05% feed at 1,122,263.621237 Pa, dt=128 us, 100 inner
  iterations, ten steps. Liquid/vapor/total nets were -9.93e-8, +8.21e-9 and
  -9.11e-8 kg/s; continuity tail 0.00201686/0.00173276; Courant 0.00248721;
  VOF [0,1]; pressure 1.119999-1.132900 MPa; maximum velocity 0.104494 m/s;
  inventory unchanged; storage closure -8.98e-4/+5.90e-6 kg/s; steam-seal and
  phase-routing gates passed.
- Load envelope: 0.05625% passed ten steps; 0.0625% and 0.075% failed the gross
  continuity gate after step one at 1.05293 and 1.26332. Failed fields are
  terminal.
- Limit: accepted diagnostic only. The pressure is CFD-interpolated, the
  balanced window is short and no full-flow, plant, long-time controller,
  mesh-independence, efficiency, DPM or EWF claim is allowed.

## Setup 07n mesh-selected closed-drain relaxation gate (`diagnostic / unresolved` 2026-08-23)

- `Scope`: qualify a reproducible whole-cell liquid pool and its closed-drain
  transient relaxation. Zero feed and a brine wall mean this is not a separator
  operating point or constant-level outlet model.
- `Mesh-selection gate`: accepted attempt 4 isolated the exact `98,473`-cell
  interval `y=0.0164023303045-0.0165144008650 m` and verified the centered
  threshold `0.0164583655847 m`, liquid volume `4.400159116 m3` and inventory
  `3877.468071 kg`. It proves deterministic CFD selection, not plant level.
- `Lineage/setup gate`: setup-07l step-10 case only as settings carrier; no
  inherited data; fresh Hybrid Initialization, patch, unique time-zero
  case/data, cold reload and complete readback. Require Fluent 2024 R2,
  `n0..n15`, one client, explicit VOF/PISO/PRESTO/Geo-Reconstruct/WFGC, RNG
  k-epsilon, gravity, zero inlets, closed brine, DPM zero/off, EWF false and all
  sources/sinks off.
- `Runtime gate`: one physical step per RPC, 20 inner iterations, external
  factor-two timestep scheduling capped at `2.56e-4 s`, exact clock proof and
  non-overwriting checkpoints. Reject non-finite residuals, missing/excessive
  Courant, VOF outside `[0,1]`, brine-face liquid VF loss, pressure/velocity
  bounds, inventory/storage error, phase-routing error or settings drift.
- `Observed through step 940`: `t=0.22271 s`, continuity `3.67467e-4`, Courant
  `0.0125058`, average velocity `0.00357883 m/s`, vorticity `0.0331321 1/s`,
  maximum velocity `0.144127 m/s`, pressure `1.1199994-1.1329449 MPa`,
  inventory unchanged, brine liquid VF `1.0`, zero liquid at the steam outlet
  and no hard-gate failure.
- `Stationarity gate`: not fully passed. Over the final 20 steps, regression
  drift was `-1.540%` for average velocity, `-0.637%` for vorticity, `-0.912%`
  for maximum velocity and `+0.021%` for Courant. The pool is bounded and
  nearly quiescent, but average-velocity drift remains above the strict `1%`
  target; final-50 drift is larger.
- `Matched dt/2 and dt/4 gate`: failed. All three branches loaded the same
  step-940 pair and advanced `0.00512 s`. Half-to-quarter endpoint differences
  were `1.427%` for average velocity, `1.404%` for vorticity and `7.491%` for
  maximum velocity; their 40-sample means were `0.817%`, `0.810%` and `5.935%`.
  Pressure/inventory/VOF/steam seal matched, continuity improved and Courant
  halved, but the solution differences did not contract.
- `Inner-iteration gate`: passed as an accepted diagnostic. At fixed
  `dt=2.56e-4 s`, increasing the cap from 20 to 100 changed average velocity,
  vorticity and maximum velocity by less than `0.000009%` across 20 matched
  samples. Continuity improved `99.70%` to `1.14616e-6`, proving that the
  timestep discrepancy is not caused by incomplete inner convergence.
- `Localization gate`: passed as an accepted post-processing diagnostic. The
  base, half and quarter maxima share cell index `382511`, centroid
  `(0.809789, 0.0420206, 0.651966) m`, and interfacial liquid VF
  `0.134811-0.134831`. Fourteen of the top-20 cells are common to all three
  endpoints. The maximum-cell turbulent viscosity is only `0.20-0.24%` of the
  domain maximum, excluding the one-cell limiter as the source. The accepted
  attempt performed zero iterations, initializations and case/data writes.
- `Matched dt/8 gate`: failed for timestep independence. The 160-step branch
  passed every hard gate and reached the same `t=0.22783 s`, but
  quarter-to-eighth endpoint differences remained `2.150%` average velocity,
  `1.936%` vorticity and `7.283%` maximum velocity. Matched-sample means were
  `1.284%`, `1.217%` and `6.092%`. Further explicit halving is stopped.
- `Implicit readback gate`: passed as an accepted zero-step diagnostic in
  attempts 8/9. Fluent 2024 R2 read back implicit VOF/PISO, the
  `(mp/scheme-type 0)` marker, automatic Compressive selection, allowed
  Compressive/Modified-HRIC schemes, `cell-convective-courant-number`, and an
  exact cold restore of the explicit parent. Attempts 1-7 remain preserved
  zero-step path diagnostics.
- `VOF formulation gate`: failed for formulation independence. First-order
  implicit/PISO/Compressive passed every hard gate but differed from explicit
  by `0.873%` average velocity, `1.168%` vorticity and `12.669%` maximum
  velocity. Second-order Compressive reduced these to
  `0.359/0.635/6.993%`; second-order Modified-HRIC reached
  `0.301/0.552/6.831%`. The residual gate passed in all branches, proving that
  residual level alone cannot select the formulation.
- `Implicit interface-scheme gate`: passed as a bounded sensitivity.
  Modified-HRIC and second-order Compressive differ by only
  `0.057/0.083/0.152%` in average velocity/vorticity/maximum velocity and both
  retain every physical gate. Modified-HRIC is marginally closer to explicit,
  but neither implicit endpoint is promoted.
- `Pressure-velocity coupling gate`: passed for this matched closed-pool
  window. Explicit/plain Coupled read back `coupled_form=false`, retained
  Geo-Reconstruct and reproduced PISO within `0.000063%` for every reported
  velocity measure. It improved endpoint continuity `37.22%` but required
  `3.234x` the summed solve-step wall time. PISO is retained as the efficient
  baseline; Coupled-with-Volume-Fractions was not used.
- `Current decision`: the step-940 explicit/PISO pair remains the common
  diagnostic parent. No implicit or Coupled endpoint is promoted. Stop
  closed-pool solver swapping and require a separately gated outlet
  pressure-response sign probe before any idealized constant-level controller
  or boundary experiment.
- `Open-drain execution state`: the response-sign probe is implemented with
  independent centre/low/high cold loads and full zero-feed steam-seal,
  storage, residual, clock, DPM/EWF/source and settings gates. Attempts 1 and 2
  credited zero physical steps; server-1 Fluent became unreachable before an
  open boundary was advanced. Therefore the pressure-response and controller
  gates remain untested, not failed.
- `Independent configured-server-2 gate`: Fluent 2024 R2/16-rank/no-client
  preflight passed and a fresh case-only reconstruction reproduced the exact
  `98,473`-cell pool without loading the prohibited server-2 steady Mixture
  field. Factor-two stages through `dt=2.56e-4 s` passed the bounded startup
  gate; that last clean endpoint had final continuity `7.94905e-4`, maximum
  stage continuity `0.450821` and Global Courant `0.00104941`. The next
  `dt=5.12e-4 s` stage failed its residual-envelope gate despite tail recovery:
  all ten steps spiked above continuity `1`, the maximum was `2.56074`, and
  the first end-step value was `0.0104354`. It is a terminal, non-resumable,
  ineligible diagnostic. Exact liquid inventory, zero steam-outlet liquid and
  brine-face liquid VF `1.0` validate only closed-pool conservation/steam seal;
  zero inlet flow plus a wall means drainage and operating mass balance remain
  untested. This independent chain cannot replace or merge into step 940.
- `Server-2 matched-background gate`: incomplete. Four cold-loaded same-`dt`,
  same-inner closed-wall steps passed every residual and physical gate with
  continuity below `8.78e-4`, Courant below `0.00128`, exact liquid inventory
  and brine-face liquid VF `1.0`. Step 95 physically advanced but stalled in
  scratch-report cleanup verification before monitoring credit. The attempt is
  non-resumable and does not complete the intended ten-step control window.
- `Server-2 open-drain gate`: untested. The first independent pressure-bracket
  attempt stopped before authentication on Fluent's Scheme version query.
  It obtained no client/version/rank readback, loaded no parent, converted no
  boundary and advanced zero physical steps. Raw TCP alone is not a passing
  Fluent-health gate. A new attempt must cold-load the original clean step-90
  pair; neither stopped field is eligible.
- `Not permitted`: outlet/controller qualification, plant-valid pressure or
  level, model/solver promotion, mesh independence/GCI, separator efficiency,
  DPM carryover or EWF performance.

## Setup 07l hydrostatic-rest isolation gate (accepted diagnostic 2026-08-21)

- `Scope`: closed-pool numerical/initialization isolation only. Inlets are zero,
  the brine face is a wall and the steam pressure outlet remains the pressure
  anchor. This is not a separator operating point.
- `Lineage gate`: accepted 07j time-zero only; delete all six inherited DPM
  injections, disable unsteady tracking and interaction, prove zero objects,
  use 16 ranks, specified vapor operating density and a gas-region pressure
  reference before initialization.
- `Execution gate`: one `1e-6 s` step per RPC, 20 inner iterations, exact clock
  proof and separate checkpoint after each step. Reject non-finite fields,
  VOF outside `[0,1]`, closed-boundary flow above `1e-6 kg/s`, liquid inventory
  change above `0.01 kg/step`, pressure above `1e7 Pa`, domain velocity above
  `20 m/s`, steam velocity above `50 m/s`, any parcel tracking or server error.
- `Observed`: all ten steps passed. Final continuity `3.4698e-6`, velocity
  residuals `1.36e-7/2.08e-7/1.28e-7`, domain velocity `4.8978e-7 m/s`, liquid
  VF `0.15826588`, liquid inventory `3774.370486 kg` and maximum Global Courant
  `1.0095e-8`. No gate, DPM, FPE or SIGSEGV failure occurred.
- `Physical check`: final brine-wall pressure head was `2090.4 Pa`, within
  `4.86%` of `rho_l g h = 2197.24 Pa` using the brine-face centroid depth.
- `Decision`: accepted as bounded isolation evidence. It rules out inherent
  rest instability but does not accept an open brine boundary, operating mass
  balance, time-step independence, mesh independence or performance.

## Setup 07j/07k transient boundary gates (2026-08-21)

- `07j decision`: failed gross-drainage gate at step 2. Brine liquid flow `-4692.8688 kg/s` exceeded the five-feed limit; storage-aware liquid closure was nevertheless `0.4601%`, confirming model drainage. Do not resume or use for performance.
- `07k scope`: controlled prescribed-flow sensitivity only. The brine outlet commands `116.92 kg/s` phase-2 liquid and zero phase-1 vapor; all other 07j controls and the fresh initial pool are fixed.
- `Runtime gate`: exactly 16 compute ranks, one physical step per RPC, exact time-step/flow-time proof, per-step finite/bounded field checks and non-overwriting checkpoints.
- `Terminal evidence`: prescribed brine flow held exactly, but step 3 produced `-4.1102e13 Pa` steam-outlet pressure, `5.2599e6 m/s` steam-outlet velocity and `7.2714e4 m/s` domain velocity. The step-4 RPC timed out and is uncredited. Setup 07k fails the bounded-field gate and must not be resumed.
- `Forensic correction`: both branches retained six DPM injections and tracked
  `6,456` one-way parcels despite interaction being off; both also patched the
  dense pool after Hybrid Initialization reported constant-pressure startup.
  These facts invalidate the earlier strict carrier-only label. One-way DPM is
  not considered the pressure-failure driver, but future carrier gates require
  zero injection objects and no parcel-tracking transcript text.
- `Acceptance still required`: bounded progression through a useful physical window, storage-aware closure trending to <=5% for startup and <=1% for formal acceptance, stable monitors, correct phase routes and a matched `dt/2` sensitivity. A defensible downstream pressure/flow/resistance condition is still required for plant validation.
- `Decision`: both 07j and 07k are terminal diagnostic failures. Correct integrated outlet flow alone is insufficient; obtain/define a defensible coupled downstream boundary and revise guarded startup before any new production run.
- `Not permitted`: mesh independence, GCI, DPM/EWF performance, separator efficiency or plant validation.

## Setup 07i WFGC-only numerical sensitivity gate (failed diagnostic; corrected 2026-08-19)

- `Scope`: one-factor numerical robustness sensitivity of failed setup 07h; not boundary validation, mesh independence or plant validation.
- `Only permitted difference`: WFGC enabled in fast mode and read back before initialization and after cold reload. Geometry, pool, models, materials, boundaries, numerics, convergence rules and DPM/EWF/sink-off state remain fixed.
- `Gross early gate`: from iteration 250 onward require brine liquid outflow no greater than three times feed, mixture imbalance no greater than 100% and liquid imbalance no greater than 200%; otherwise stop and classify unresolved.
- `Final gate`: retain setup 07h's phase-route, <=0.5% phase/mixture balance, <=0.5% primary drift, <=1% secondary drift and bounded-residual requirements.
- `Runtime comparability gate`: the live Fluent runtime must report exactly node IDs `n0..n15` immediately after authentication and before any directory, mesh, settings or initialization mutation. Stored mesh partition metadata is not accepted as proof; the connectivity table's `/20` hardware-core denominator is recorded separately and never interpreted as a process count.
- `Current evidence`: all 29 local tests pass. Attempt 8 read WFGC back `enable=true, mode=fast`, preserved a separate initialized checkpoint with DPM/EWF/sink off, and used exactly 16 solver processes. Continuity rose to `6.9888e14` at transcript iteration 20; the GUI then recorded iteration 21, Node-4 SIGSEGV, connection reset and server shutdown. Zero complete blocks were credited and no divergent checkpoint was written.
- `Current infrastructure state`: no controller is active. The restarted endpoint is healthy and independently verified as Fluent 2024 R2 with 16 solver processes on 20 hardware cores; no case is loaded.
- `Decision rule`: setup 07i is terminal failed diagnostic evidence. Do not repeat or resume the identical steady field; route to transient setup 07j. This does not validate downstream brine pressure or separator performance.

## Setup 07h initial-liquid-pool carrier gate (failed diagnostic 2026-08-16)

- `Scope`: one-mesh qualification of the source-free brine-outlet boundary formulation; not mesh independence or plant validation.
- `Controlled origin`: clean 620,431-cell resolved-outlet mesh, authoritative setup-07 carrier settings, fresh Hybrid Initialization and no reuse of the divergent setup-07g live field.
- `Only intended difference`: initialize secondary-phase liquid below `y=0 m`, inferred from the brine-face centroid and equivalent radius. The actual plant water level remains missing.
- `Preparation proof required`: mesh hash, 16 partitions, zone inventory, complete settings readback, minimum-phase-averaged operating density, DPM/EWF/source off, named-expression readback, bounded phase-2 VF change and a separate initialized case/data pair.
- `Iteration-1000 routing gate`: outward mixture at both outlets, outward vapor at the steam outlet, outward liquid at the brine outlet, brine vapor no more than `25%` of vapor feed, steam liquid no more than `10%` of liquid feed, and no non-finite/grossly divergent field.
- `Final gate`: mixture, vapor and liquid imbalance each no more than `0.5%`; primary monitor drift no more than `0.5%`; velocity/vorticity/liquid-inventory drift no more than `1%` over iterations 2500-3000; correct phase directions; bounded, non-growing residual histories.
- `Preparation evidence`: accepted. Cell-register patch readback changed domain-average liquid VF `0 -> 0.15826588`; all initialized setup checks passed and the initialized pair was saved separately.
- `Observed routing evidence`: iteration 25 had outward steam vapor and outward brine liquid, with the brine outlet `97.32%` liquid. This supports the initial-condition concept but is not a converged boundary result.
- `Terminal evidence`: iteration 250 had `-3304.7817 kg/s` brine liquid, `1602.99%` mixture imbalance and `2726.53%` liquid imbalance. The next requested block ended at residual row 292 with AMG pressure/k/VOF divergence and a floating-point exception. That block and its failed live state are unverified diagnostic evidence only.
- `Numerical-method caveat`: Fluent recommended Warped-Face Gradient Correction for the polyhedral mesh after settings import; live readback is `enable=False`. A clean one-factor enabled sensitivity is required before attributing the failure entirely to the steady boundary formulation.
- `Gate decision`: failed; setup 07h is diagnostic/unresolved. The steady branch must not be resumed or used for separator metrics.
- `Failure interpretation`: the source-free resolved geometry now requires a transient successor with physical-time inventory accounting and a defensible downstream brine pressure/level condition. It does not justify ad hoc pressure tuning.
- `Not permitted`: mesh independence, GCI, separator efficiency, DPM carryover, EWF behavior or plant validation.

## Setup 07g resolved brine-outlet validation gate (failed diagnostic 2026-08-13)

- `Observed/preflight accepted`: the new mesh contains a separate brine pressure face (`0.19936247 m2`), two inlets, a separate steam outlet, two wall zones and one fluid zone. Fluent reports 620,431 cells, 16 partitions, minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258` and no negative-volume error.
- `Observed/setup accepted`: zone names were explicitly normalized, the authoritative setup-07 carrier physics was imported, the new brine outlet was configured at `1.12 MPa` with liquid-only backflow, and complete pre/post-Hybrid readback returned zero validation errors. DPM/EWF and cell sources are off.
- `Observed/execution evidence`: Fluent's transcript proves 25 completed iterations; that state is preserved separately. The monitor-stream failure is a controller evidence-path issue, not a solver acceptance result.
- `Observed/iteration 500 diagnostic`: both outlet mixture fluxes are outward, but the brine outlet is vapor-dominant (`-42.680678 kg/s`) and admits liquid (`+5.512239 kg/s`). Mixture and liquid imbalance remain `61.5687%` and `104.7145%`. This fails phase-route and closure gates but is not terminal iteration-independence evidence.
- `Terminal execution evidence`: the next requested 250-iteration block produced only 62 residual rows and was not credited. The later live field diverged to overflow scale. The verified iteration-500 pair is the final usable evidence.
- `Not permitted yet`: mesh independence, Richardson/GCI, DPM carryover, EWF behavior, separator efficiency or plant validation.
- Decision: only an accepted one-mesh carrier result may reopen a resolved-geometry mesh sequence. The physical brine downstream pressure remains an external validation input.

## Setup 07f Sink Thickness/Rate Sensitivity Gate (running 2026-08-11 NZST)

- Evidence status: `Diagnostic sensitivity in progress`; no validation claim.
- Controlled origin: verified setup-07c clean-original prepared 900k state,
  authoritative carrier readback, fresh Hybrid Initialization for every case,
  and no setup-07a accumulated solution data.
- Planned controls: two-factor staircase across `0.2803305-0.4204958 m` band
  height and fixed `tau=0.020-0.005 s`, with all carrier physics, boundaries,
  numerics, acceptance gates and DPM-off state held fixed.
- First-case implementation evidence: requested and read-back band height and
  tau match; the complete mask contains `184,145` cells and `0.88704756 m3`;
  a separate fresh-initialized ramp-zero checkpoint exists.
- Computational-schedule evidence: an interrupted non-result startup exposed
  a redundant per-iteration full-mesh mask rebuild. The `v2_staticmask`
  schedule retains live source evaluation but rebuilds/broadcasts the fixed
  geometric mask only when controls change. A live smoke iteration reduced
  wall time from about `8-11 min` to `6.17 s`, preserved RP readback and kept
  DPM off. Formal cases restart clean; parity still requires their histories.
- Transport-recovery evidence: the first optimized attempt was interrupted by
  a gRPC timeout after `2,500` cumulative / `1,500` recorded full-strength
  iterations, not by a numerical guard. Its partial state is preserved but is
  not accepted or reused. The formal clean-origin `v3_rpc25` retry limits every
  ramp/full-strength call to 25 iterations while retaining the same source,
  controls and acceptance windows.
- Interim classification: the completed doubled-band `tau=0.020 s` case
  reached its full budget but passed zero windows; endpoint sink was
  `53.133696 kg/s` and corrected liquid imbalance remained `54.5553%`.
  The first `tau=0.005 s` attempt stalled after `2,375/1,375` recorded
  iterations while Fluent stayed healthy. It remains interrupted diagnostic
  evidence. A process-liveness permission error briefly allowed overlapping
  preflight controllers; all were terminated before new production, and the
  fingerprint guard rejected the interleaved `v4` state. One audited
  `v5_single_controller` clean retry passed parity/mask preflight and saved a
  ramp-zero pair with no partial-field reuse, then was stopped before
  production after a busy health probe was misdiagnosed. V6 connected and
  restored the clean parent but received empty captured mesh-report text; the
  mandatory parser rejected it before initialization/iteration. Cases 2 and 3
  remain pending and no controller is active.
- Acceptance rule: lower liquid imbalance or larger sink magnitude is
  insufficient. Pressure, liquid inventory, outlet/domain velocity, vorticity,
  mass balance and residual histories must also satisfy two consecutive
  iteration-independent windows.
- Interpretation limit: these empirical sources remain unable to validate
  brine-outlet hydraulics or separator efficiency. The resolved outlet remains
  the physical validation branch.
- Setup report: `../../../Setup report/07f-split-inlet-sink-thickness-rate-matrix.md`.

## Setup-07 Visual Diagnostic Evidence (2026-08-10)

- Classification: `Diagnostic / unresolved`; no validation claim.
- Matched setup-07a contours at 900k iterations 4000 and 6000 use identical `x=-1.5 m` plane, camera, cell sampling and fixed field ranges. They show the liquid-rich wall region expanding while liquid inventory changes `64.4%`, and the pressure field shifting while pressure drop changes `9.7%`.
- Setup-07c sink-mask/pathline graphics verify that the complete thick bottom-local band is active and that the displayed trajectories are Mixture-model carrier pathlines from `liquidinlet`, not DPM particles.
- The setup-07c sink closes only `19.2%` of liquid inflow and primary convergence gates fail. Low steam-outlet liquid flow is therefore trend-only and cannot validate separator efficiency.
- Setup-07d fixed-strength evidence adds a controlled fivefold source-coefficient sensitivity. The endpoint sink increases only `2.09x`, from `22.49` to `46.99 kg/s`, while the active-band liquid inventory falls and continuity/primary physical-monitor gates still fail. Figures `10-12` document this diminishing-return result.
- Steady iteration is not physical time. Inventory change with iteration demonstrates lack of iteration independence; it is not a transient accumulation-rate measurement.
- Evidence package: `../../../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md`; graphics/readback provenance: `../../../PyAnsys/output/setup07_meeting_visuals_20260811/visual_manifest.json` and `../../../PyAnsys/output/setup07_meeting_visuals_20260811/fluent/fluent_graphics_manifest.json`.
- Validation gate remains unchanged: qualify a resolved brine outlet and conserved, fixed-inventory medium-mesh carrier solution before mesh independence or DPM/EWF performance validation.

## Setup 07e Adaptive Mass-Balance Control Gate (failed 2026-08-11 NZST)

- Evidence status: `Completed diagnostic / unresolved`; no validation claim.
- Controlled lineage: verified source-hooked setup-07c 900k preparation, fresh
  Hybrid Initialization, unchanged complete 92,058-cell band, carrier physics,
  boundaries, solver controls and DPM-off state.
- Dry-band repeatability: at exact saved cumulative iterations 100, 200, 350,
  500, 750 and 1000, setup 07e and the accepted setup-07d control have `0.000000%`
  difference in pressure drop, domain liquid inventory, mixture/vapor outlet
  flow, outlet/domain velocity and domain vorticity. Adaptive tau changes
  therefore have no detectable field effect before liquid reaches the band.
- Execution evidence: the run reached `3,000` cumulative / `2,000`
  full-strength iterations and stopped at the maximum budget. Separate start,
  ramp-complete, R1=1000, R1=2000 and final ramp-reset-zero case/data are
  verified; DPM remained off and zero acceptance windows passed.
- Terminal limitation: at the bounded minimum `tau=0.002 s`, the source
  removed `50.954294 kg/s` (`43.6%` of command), leaving `56.419329%`
  corrected liquid imbalance. Pressure drop/domain inventory were
  `26.7252 kPa`/`65.007547 kg`; band inventory was `0.101909 kg`, versus
  `0.23384 kg` required to meet the command under the implemented source law.
- Stability evidence: final-500 pressure, sink and inventory drift were
  `5.8506%`, `26.1894%` and `13.3524%`; outlet/domain velocity drift were
  `3.3033%`/`6.9068%`. Continuity ended at `0.254617` and grew `3.634%` over
  the final 100 iterations; liquid-VF residual ended at `7.53207e-4` and grew
  `8.463%`. Numerical closure, physical-monitor stability, residual level and
  residual-trend gates all failed.
- Decision rule: numerical phase closure is informative only if the complete
  pressure, inventory, velocity/swirl and residual gates also pass. Even a
  passing numerical control would not validate brine-outlet hydraulics or
  separator performance.
- Validation conclusion: further local sink tuning is not a validation path.
  A resolved brine outlet and source-free conserved medium-mesh solution are
  required before mesh independence, efficiency, DPM or EWF can be assessed.
- Setup report: `../../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`.

## Setup 07d Capacity-Matched Sink-Strength Gate (failed 2026-08-10 NZST)

- Evidence status: `Accepted diagnostic fixed-strength sensitivity / physical qualification failed`.
- Controlled comparison: setup 07d retained the verified setup-07c prepared 900k state, full settings fingerprint, fresh Hybrid Initialization, 92,058-cell band, physics, boundaries, solver controls and DPM-off state. Only `tau` changed from `0.1` to `0.02 s`.
- Parity audit: canonical mesh-metric and complete settings-readback hashes are identical; all mask fields match. Six matched pre-sink ramp rows remain within the existing `0.5%` primary and `1%` velocity/vorticity comparison limits. The result is an accepted controlled diagnostic comparison, not a physical validation.
- Execution evidence: guarded 1,000-iteration ramp plus 2,000 full-strength iterations; separate checkpoints and failure-attempt provenance preserved; zero passing acceptance windows.
- Endpoint evidence: sink `46.9874 kg/s`, corrected liquid imbalance `59.8122%`, source-inclusive mixture imbalance `35.1679%`, domain/band inventory `66.6560/0.93975 kg`, pressure drop `26.8901 kPa`, continuity `0.229682` and liquid-VF residual `7.3419e-4`.
- Stability evidence: final-500 pressure `6.618%`, sink `23.044%`, inventory `14.120%`, outlet velocity `3.161%` and domain velocity `6.901%` drift failed. Stable vapor throughput and vorticity alone are insufficient.
- Sensitivity conclusion: a 5x local coefficient gave only a 2.09x endpoint sink and removed `40.19%` of liquid feed. Local liquid availability limits the source response, and the result neither closes nor stabilizes the carrier field.
- Validation claim: none. Setup 07d supports the resolved-brine-outlet decision but cannot validate outlet hydraulics, separator efficiency, mesh independence, a free surface or physical-time accumulation.
- Setup report: `../../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`.

## Setup 07c Thickened-Sink Qualification Gate (failed 2026-08-09 NZST)

- Evidence status: `Accepted diagnostic layer-thickness sensitivity / physical qualification failed`.
- Controlled comparison: setup 07c used the same clean original 900k mesh, full settings fingerprint, fresh Hybrid Initialization, physics, boundaries, `tau=0.1 s`, wall roles, solver controls and DPM-off state as 07b. Only the sink band changed from one-cell adjacency to a fixed `0.1401652536 m`, nominal 16-layer-equivalent volume.
- Mask evidence: 92,058 cells and `0.44378932 m3` across the complete bottom-local band, versus 5,438 cells and `0.027726243 m3` for 07b.
- Execution evidence: guarded 1,000-iteration ramp plus 2,000 full-strength iterations; zero passing acceptance windows; separate recovery and endpoint/final case-data evidence preserved.
- Endpoint evidence: sink `22.4882 kg/s`, inventory `71.7785 kg`, corrected source-inclusive liquid imbalance `80.7661%`, source-inclusive mixture imbalance `47.4802%`, pressure drop `27.1372 kPa`, continuity `0.191551`, and liquid-volume-fraction residual `6.9815e-4`.
- Stability evidence: final-500 pressure `8.53%`, sink `29.99%`, inventory `16.93%`, outlet velocity `4.24%` and domain velocity `6.78%` drift failed; vapor outlet and vorticity drift alone were insufficient.
- Accounting correction: the controller's phase-2 `liquid_source_augmented_*` field double-counts the cell-zone source. Use Fluent's already-source-inclusive phase-2 Net (`80.7661%` imbalance). The same correction changes setup 07b from `84.2956%` to `91.1909%`. No scientific classification changes.
- Validation claim: none. Thickening increased removal by roughly `13-16x` at matched full-strength counts, but the sink still removed only `19.23%` of liquid inflow and did not establish fixed-inventory steady behavior.
- Decision: do not repeat the mesh ladder, add DPM/EWF or tune more bands as a validation exercise. Resolve a brine outlet, qualify one medium mesh and then reopen mesh independence.
- Setup report: `../../../Setup report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md`.
- Result report: `../../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/QUALIFICATION_RESULT.md`.

## Setup 07b Liquid-Sink Qualification Gate (failed 2026-08-08 NZST)
- Implementation evidence: `Accepted` for compile/load, five-UDM reservation, cold-reload persistence, exact phase/mixture hook placement and one-iteration source integration.
- One-iteration evidence: `5,438` bottom-adjacent cells, `0.027726243 m3` layer, `0.959465 kg` liquid and `-0.47973263 kg/s` integrated source for `R=0.05`, `tau=0.1 s`; the source magnitude matches `-M_l R/tau` within output rounding.
- Physical evidence: `Completed diagnostic / unresolved`. The clean 900k `tau=0.1 s` run reached 500 ramp plus 6,000 full-strength iterations with zero passing acceptance windows.
- Mandatory production origin: satisfied by clean-preparation v3. It used original `mesh-900k.msh`, authoritative case-only/settings transfer, complete normalized settings-fingerprint parity and fresh Hybrid Initialization; no saved solution data was loaded and zero production iterations ran. No setup-07a accumulated-liquid data field may seed a restart.
- Endpoint evidence: sink `8.06194 kg/s`, domain liquid inventory `191.836 kg`, corrected source-inclusive liquid imbalance `91.1909%`, pressure drop `34.8475 kPa`, continuity `0.279243`, and liquid-volume-fraction residual `1.8933e-3`.
- Final-window evidence: pressure, sink, inventory, domain velocity and vorticity drift all exceeded their limits; residual-level and `k` trend gates failed. Vapor outlet and outlet velocity stability alone are insufficient.
- Comparison rule: do not promote setup 07b to an accepted comparison against setup 07a and do not repeat the mesh ladder. Any tau/layer comparison is diagnostic sensitivity only.
- Validation claim: none. The one-cell sink is a technically functional unresolved-reservoir abstraction, not a qualified drain model.
- Next validation branch: resolve a physical brine outlet, demonstrate steady phase/mixture closure and iteration independence on one medium mesh, then reconsider mesh independence and DPM/EWF.
- Setup report: `../../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`.

## Split-Inlet Mesh-Convergence Gate (closed 2026-08-05)
- Evidence status: `Completed diagnostic — iteration independence and mesh independence unresolved`; no mesh-independence claim is permitted.
- Execution baseline: setup `07a` used `partial_solution_diagnostic_20260801.cas.h5` plus `mesh_study_settings.set` and accepted full Fluent readback. `FFF.1-2.cas.h5` is lineage evidence; setup `08c` is not this study's baseline.
- Preflight result: accepted for seven meshes. Geometry, phase assignment, zone roles, materials, models, boundaries, numerics, initialization, monitors, 16 processes and DPM-off state were held fixed.
- Formal result: all meshes reached 3000 iterations. Steam-outlet vapor flow is stable, but every mesh fails pressure and/or velocity iteration-stability criteria.
- Extension result: the 900k mesh reached a separately saved iteration-6000 checkpoint; final-500 pressure drift remained `4.61%`, outlet velocity `1.49%`, domain velocity `1.70%` and vorticity `1.83%`.
- Inventory result: liquid inventory increased from `104.05 kg` at iteration 4000 to `171.03 kg` at 6000 (`+64.37%`). This directly violates the no-inventory-drift requirement.
- Interpretation: the closed-bottom steady case is a filling/redistribution diagnostic, not a conserved steady separator state. Carrier quality and liquid carryover remain trend-only.
- Richardson/GCI status: not accepted because iteration/inventory changes dominate or contaminate the grid-to-grid differences.
- Validation status: the study cannot validate separator pressure drop, carryover or efficiency. It is valid evidence of a modelling limitation and of stable imposed vapor throughput.
- Full study contract: `../../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`.
- Diagnostic closure: `../../../PyAnsys/output/split_inlet_mesh_convergence_20260801/STUDY_DIAGNOSTIC_CLOSURE_20260805.md`.

## Current Validation State
- Not ready for final validation; the completed setup-07a campaign demonstrates that the current closed-bottom steady formulation does not produce a stable comparison state.
- `Observed`: seven formal mesh runs and the 900k 6000-iteration extension are diagnostic/non-converged rather than iteration-independent.
- `Observed`: liquid inventory rises monotonically across the audited saved checkpoints.
- `Inferred`: a physically credible liquid discharge is required before steady separator pressure drop, carryover or efficiency can be validated.

## Pre-Validation Requirements
1. Stable converged baseline solution.
2. Repeatability across at least two reruns with same settings.
3. Documented sensitivity on key uncertain assumptions.
4. External or analytical target ranges for pressure drop, outlet steam quality/liquid carryover, and expected separation behavior.

## Initial Validation Targets
- Compare modeled separator behavior trend against published expectations from literature.
- Compare outlet quality behavior patterns against reference correlations where applicable.
- Compare spiral-inlet CFD pressure drop against Lazalde-Crabtree-style analytical pressure-drop estimates only where the required geometry/flow inputs are transferable.
- Convert steam-outlet liquid carryover into an implied separator efficiency and compare against reported geothermal separator design ranges.

## Validation Anchor Hierarchy
Use the strongest available comparison first. If a higher-confidence source is unavailable, explicitly downgrade the claim.

1. `Reported` plant/test data for the same or similar separator.
   - Best use: pressure drop, outlet steam quality, brine outlet flow, inlet mass flow, operating pressure, and separator efficiency.
   - Claim strength if matched: strongest project evidence.
2. `Reported` analytical or design-correlation estimate.
   - Best use: expected separation efficiency range, allowable velocity/swirl behavior, pressure-drop order of magnitude, and outlet quality expectation.
   - Claim strength if matched: acceptable engineering sanity check, but not full validation.
3. `Reported` CFD/literature benchmark trend.
   - Best use: qualitative flow structure, vortex behavior, phase segregation, mesh/numerics plausibility.
   - Claim strength if matched: supports model direction, not absolute accuracy.
4. Internal A/B comparison only.
   - Best use: isolate whether a design change improves or worsens a metric under the same modelling assumptions.
   - Claim strength if matched: useful for sensitivity, not proof of real-world correctness.

## Minimum Gate Before Long Runs
Before launching a multi-hour production run, define:
- the external/analytical quantity it will be compared against,
- the acceptable error band or qualitative expectation,
- the metric to extract from Fluent,
- the decision if the result misses the target.
- the minimum iteration/monitor-stability evidence needed before the run can enter the report-facing result set.

## Simulation Evidence Use Rules
- `Usable for validation/design comparison`: sufficiently iterated, physically balanced, monitor-stable, and checked against external or analytical targets.
- `Usable for diagnostics`: sufficiently developed to show failure modes or qualitative flow behavior, but not converged or not mass-balanced.
- `Setup/debug history only`: low-iteration or incomplete runs that can explain setup evolution but cannot support performance claims.
- Current classification:
  - `FFF-2`: `Usable for diagnostics`.
  - `MWH-WP-2026-05-07-A`: `Usable for diagnostics`.
  - Earlier lower-iteration runs: `Setup/debug history only`.

## Current Sanity-Check Anchors
- `Reported`: spiral-inlet BOC separators sit within the wider vertical BOC evidence base, where properly designed separators commonly target around `99.5-99.99%` efficiency; use this as a high-level carryover sanity band, not proof of model validity.
- `Reported`: effective inlet velocity for BOC design is commonly around `30-40 m/s`, with breakdown warning near `42 m/s`; apply this to the spiral-inlet case as a sanity check only where the inlet definition is comparable.
- `Reported`: Purnanto 2013 compared CFD outlet steam quality against Lazalde-Crabtree empirical estimates and Webre separator trend data; for this project, use the spiral-inlet result as the closest separator-specific validation pattern and other geometries only as context.
- `Reported`: Mubarok 2020 validated geothermal CFD by comparing pressure drop, enthalpy, and mass flow against field data and reporting relative errors; use that as the reporting template if partner/field data become available.
- `Reported`: Pointon et al. 2009 provides a geothermal HP separator CFD anchor at `11.7 barA`, `1875 t/h`, `3.3 m` vessel diameter, and about `19-20 kPa` pressure drop, with scrolled entry slightly outperforming tangential entry (`99.96%` vs `99.93%`) and closely matching a Lazalde-Crabtree-based design prediction (`99.955%`). Use this as geothermal-specific trend support for the current spiral/scrolled-inlet preference and as an order-of-magnitude check for pressure drop and outlet dryness, not as a full one-to-one validation target because the exact geometry and Fluent controls are incomplete.
- `Reported`: Chen et al. 2025 is not geothermal, but it is currently the strongest experiment-backed separator CFD method anchor in the repo. Their transient Fluent `RSM + DPM` model matched dry-case inlet pressure within `0.01-2.13%` and wet-case separation efficiency within `4.1%`, with reported droplet PSD and grid-independence evidence. Use this as support for one later `RSM-DPM` sensitivity case if the cheaper geothermal baseline remains ambiguous after convergence and phase-flux checks; do not use Chen's air-water operating values as direct geothermal targets.

## Useful Calculation Checks
- Separator efficiency from steam-line brine carryover:
  - `eta_s = m_s / (m_s + m_b) * 100`
  - `eta_s = (m_w - m_b) / m_w * 100`
- Lazalde-Crabtree empirical efficiency structure, used only where applicable to the spiral-inlet case:
  - `eta_eff = eta_m * eta_A`
- Pressure drop:
  - `Delta P = (NH * u^2 * rho_v) / 2`
  - `NH = 16 * Ao / De^2`
  - `u = QVS / Ao`
- Phase split from enthalpy:
  - `x = (h - h_f) / h_fg`
  - `m_g = x * m`
  - `m_f = (1 - x) * m`

## DPM Carryover Validation Option
- Use only after a stable continuous/mixture solution exists.
- Inject droplets and classify outcomes as `trapped`, `escaped`, and `incomplete`, following the separator CFD validation pattern in Purnanto 2013.
- Treat DPM as a carryover sanity check rather than final truth if incomplete tracks are high or droplet-size assumptions dominate the result.

## Current Missing Validation Inputs
- `Missing Info`: analytical pressure-drop estimate for the active geometry and flow conditions.
- `Missing Info`: expected steam outlet quality or allowable liquid carryover range.
- `Missing Info`: brine outlet liquid flow expectation.
- `Missing Info`: separator efficiency target or design benchmark for this operating point.
- `Missing Info`: whether partner's validation/parameter-sweep comparison has already produced usable target values.

## Practical Near-Term Validation Plan
1. Fix or classify the `FFF-2` parent convergence and phase mass-balance problem.
2. Ask partner for the analytical/parameter-sweep outputs in a table with input conditions, predicted pressure drop, steam quality/carryover, brine flow, and any efficiency metric.
3. Calculate quick sanity values for the stabilized parent spiral-inlet case: inlet velocity position relative to the applicable `30-40 m/s` BOC band, implied separator efficiency from carryover if interpretable, and pressure-drop estimate if geometry terms are available.
4. Build a validation target table before the next production run.
5. Use the next Fluent run first as a sanity-check run against target ranges, not as a design-optimisation run.
6. Only compare split-inlet vs baseline after the baseline-like case is within a defensible target band or the mismatch is clearly explained.
7. If no analytical or real-world target exists for a metric, label that metric as `trend-only` in the report.

## Claim Rules
- If a run only matches internal expectations, claim: "model trend is internally consistent."
- If a run matches analytical/design-correlation ranges, claim: "model is directionally supported by engineering estimates."
- If a run matches real-world/test data, claim: "model is validated against available operating evidence."
- If a run fails target checks, do not tune multiple parameters at once to force agreement; identify which assumption is most likely responsible and run one control case.
## Setup 07m bounded pressure-opening validation

Setup 07m adds internal numerical/physical consistency evidence, not plant
validation. All pressure members originate from the same accepted 07l step-10
field. A low/centre/high bracket produced monotonic liquid brine flow after ten
`1e-5 s` steps, with an endpoint sign change and a near-zero centre response.
The later 0.1% inlet hold reduced continuity monotonically to `0.00186867`,
kept Global Courant at `3.47e-6`, routed vapor only through the steam outlet and
liquid only through the brine outlet, and preserved finite pressure/velocity.

This supports the claim: **the CFD-derived centre pressure is numerically safe
for bounded startup diagnostics on the present mesh**. It does not support the
claim that the pressure is the real downstream brine pressure or that the
separator is validated at operating flow. External downstream pressure/loss
data and longer operating-flow closure remain required.

## Setup 07n model-form screening requirement

Mesh convergence is withheld until the resolved-brine-outlet carrier passes a
model-form screen. The minimum comparison set is:

1. reconstructed transient VOF/PISO constant-level baseline with
   inner-iteration and `dt/2` checks;
2. one pressure-velocity-coupling sensitivity;
3. one alternative phase formulation prepared from the same mesh and
   hydrostatic initial-condition definition;
4. an RSM sensitivity only after one drainage formulation is stable.

The closed-pool numerical subset of this screen is now complete: explicit
PISO versus plain Coupled is field-equivalent within `0.000063%`, whereas
explicit versus the closest tested implicit/PISO branch retains a `6.831%`
maximum-velocity difference. This clears pressure-velocity coupling for the
closed-pool window but does not satisfy the model-form gate for drainage,
because no accepted constant-level open-outlet baseline exists yet. Transient
Mixture/Eulerian/RSM tests remain downstream of that physical boundary gate.

All comparisons use phase-resolved boundary flux, inventory change and
storage-aware closure over a matched physical-time window. Residual level
alone cannot choose the model because implicit VOF, Mixture and Eulerian
formulations solve different equation sets and have different numerical
diffusion.

The downstream brine boundary must also be screened independently. The current
outlet area implies a reference full-flow velocity of about `0.666 m/s` and a
velocity head of about `195 Pa`, compared with the accepted hydrostatic-rest
head of about `2090.4 Pa`. A pressure-only outlet with omitted pipe/valve loss
therefore remains diagnostic even if it converges. A mesh ladder may begin only
after both model-form and downstream-boundary choices are fixed and read back.

DPM, EWF and numerical sinks remain outside this carrier validation stage.

### Constant-level and steam-seal gates

The lower water pool is an intended operational feature. Qualification must
show all of the following over the same accepted window:

- liquid discharge matches liquid feed after accounting for transient storage;
- liquid inventory remains within the specified drift band around the
  independently calculated setup-07n level setpoint; setup 07l's
  `3774.370486 kg` is only a comparison datum;
- the resolved interface remains in the stated design-level band and above the
  actual mesh-derived brine-pipe crown by a resolved margin;
- vapor carry-under through the brine outlet is negligible and non-growing;
- continuity and phase residuals are bounded and meet their promotion gates;
- the controller/outlet command is not saturated or oscillating.

A good overall mass balance is not sufficient if the pool uncovers the drain
or steam escapes through the brine outlet. Conversely, a fixed pool patch with
no balanced liquid removal is only an initial condition, not a constant-level
operating model.

Backflow liquid volume fraction is not evidence of a steam seal because it is
used only if flow reverses into the domain. For outward flow, outlet phase
composition must be taken from the resolved VOF field. Any imposed total
mass-flow outlet is accepted only if its adjacent cells remain liquid-dominant
and the reported vapor flux is negligible without a phase-selective outlet
constraint.

The setup-07l closed-pool and setup-07m micro-start evidence cannot by
themselves satisfy these gates: their physical windows are too short to prove
separator-scale level relaxation, and their level/pressure values were not
plant inputs. They remain useful forensic numerical evidence only.

### Stage-0 validation evidence from 22 August 2026

The mesh checksum, Fluent version, 16-rank roster and exclusive connected-
client state passed. Polygon integration of the 323 brine faces reproduced the
accepted `0.19936247 m2` area to `4.98e-9` relative difference. The same
surface connectivity located the crown at `y=-0.0015579789 m` and the median
vertical height of the two crown-touching faces at `0.0089871744 m`.

Two independent case-only/fresh-Hybrid patches then passed the exact inventory
calculation path. Their VOF integrals were `4.40015912` and `4.43625099 m3`, or
`3877.46807` and `3909.27263 kg` using the read-back liquid density. Both began
with zero domain-average liquid VOF, retained zero DPM injections and disabled
source containers, and ran zero physical steps.

This validates the geometry and inventory calculations only. Those first
elevations used two/four exact boundary-face heights as a proxy; the supported
PyFluent cell-mesh readback is unavailable in Fluent 2024 R2 and the tested
UTL-volume fallback failed. The later exact whole-cell plateau removed the
selection ambiguity and enabled the closed-pool relaxation described above,
but it did not turn the CFD-selected submergence into a plant operating level.

The planned coupling comparison is also corrected: explicit VOF may compare
PISO with plain Coupled. **Coupled with Volume Fractions** is not supported
with explicit VOF in Fluent 2024 R2 and can be inspected only on a separately
qualified implicit-VOF branch.

### Setup 07n lower-face-proxy startup gate (passed diagnostic; not physical qualification)

- `Lineage`: setup-07l step-10 case only as settings carrier, no data; fresh
  Hybrid Initialization and exact lower Stage-0 patch; server 1, Fluent 2024
  R2, 16 ranks, exclusive client and checksum-bound files.
- `Invariant controls`: zero inlet flow, brine wall, steam pressure outlet,
  explicit VOF/PISO/PRESTO/Geo-Reconstruct/WFGC, RNG k-epsilon, gravity,
  Energy off, DPM zero/off, EWF false and every source/sink disabled.
- `Pilot gate`: ten one-step RPCs at `dt=1e-6 s`, 20 inner iterations. Every
  step passed clock, finite residual, Courant, VOF bound, pressure, velocity,
  closed-boundary flux, brine coverage, phase inventory/storage and full
  settings readback gates. Step-10 continuity was `2.74398e-6`; brine liquid VF
  was `1.0`; inventory was `3877.468071 kg`.
- `First dt extension`: parent case/data hashes reverified; the sole change was
  `dt=2e-6 s`. Ten more guarded steps passed. At cumulative `30 us`, continuity
  was `4.64048e-6`, Courant `4.81584e-8`, pressure
  `1.1199992-1.1329162 MPa`, maximum velocity `1.64972e-4 m/s`, liquid steam
  flow zero and inventory unchanged.
- `Validation decision`: accept only bounded implementation/startup behavior
  for this exact face-proxy field. Reject claims of hydrostatic/dynamic
  relaxation, accepted operating level, open-drain mass balance, controller
  performance or time-step independence. The physical window is `~0.07%` of
  the local gravity time and no matched `dt/2` relaxation window exists.
- `Promotion blocker`: independently recover adjacent volume-cell spacing,
  repeat the pool integral at the resulting mesh-defined level, and run a
  meaningful-time closed-drain relaxation before outlet/model/solver or mesh
  studies.
