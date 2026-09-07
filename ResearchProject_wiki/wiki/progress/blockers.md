# Blockers

## BLK-015 | Resolved brine outlet requires qualified liquid-pool dynamics

- 2026-08-28 update: a calibrated single pressure step produced an excellent
  short balance window but did not hold it through 70 steps. The run completed
  with final liquid/total imbalance `-0.01155471/-0.011478693 kg/s`; the
  final-ten gate failed even though continuity, Courant, VOF, pressure,
  velocity, liquid seal and phase routing all passed. This separates the
  blocker cleanly: it is sustained hydraulic/control closure, not solver
  divergence or steam-seal loss.
- The calibrated endpoint is ineligible and must not be resumed or repeated
  unchanged. The next one-factor test should add only one later held pressure
  action from a fresh clean-step-90 load. A genuine level controller remains
  blocked by insufficient inventory/interface-height precision and missing
  plant level/downstream resistance data.

- 2026-08-27 update: the ten-step 0.05%-feed balance did not persist. The
  fixed-pressure hold reached about `0.050 kg/s` excess liquid drainage;
  gain-0.25 feedback overshot to about `+0.0195 kg/s` liquid imbalance; and
  gain-0.05 feedback was still near `-0.0386 kg/s` when its next RPC lost the
  stream after 47 credited steps. Residuals, Courant, VOF and steam sealing
  stayed bounded in all credited states, so the active blocker is sustained
  hydraulic/control closure rather than immediate numerical divergence.
- The current controller endpoints are all ineligible and non-resumable. The
  next run must cold-load clean server-2 step 90 and change only the treatment
  of response lag. Current server-2 TCP reachability is confirmed, but Fluent
  health/ranks have not been re-authenticated after the stream failure.

- 2026-08-25 update: an independent pressure-outlet diagnostic at 0.05% feed
  completed ten steps with phase and total net imbalance below 1e-7 kg/s,
  continuity 0.00173276, Courant 0.00248721, a fully liquid brine face and
  zero cross-phase leakage. This proves resolved drainage is numerically
  possible at very low feed. 0.05625% also passed; 0.0625% and 0.075% failed
  after one step and are terminal.
- Remaining blocker: scale and physical closure. The accepted
  1,122,263.621237 Pa pressure is CFD-interpolated, not plant-measured; the
  balanced window is only 1.28 ms. Full-flow ramping, controller stability,
  downstream resistance and operating level remain required before mesh
  convergence, efficiency, DPM or EWF.
- Fluent 24.2 exposes no writable bulk VOF mass-flow-outlet rate, only phasic
  rates. Prescribing them would preselect routing, so 07n-b remains unresolved.

- Status: Active but narrowed; setup 07n now has an exact whole-cell pool, a
  bounded closed-drain trajectory through step 940 / `0.22271 s`, matched
  explicit timestep/inner-iteration studies, explicit-versus-implicit VOF
  comparisons and an explicit PISO-versus-plain-Coupled comparison. Every
  completed solver branch is bounded, but formulation/timestep differences do
  not contract; the operating level, open-brine boundary and constant-level
  response remain unqualified.
- First observed: 2026-08-13 dry-start setup 07g; successor defined 2026-08-15.
- Symptom: at verified iteration 500 setup 07g discharged net mixture through both outlets, but the brine outlet discharged `42.680678 kg/s` vapor and admitted `5.512239 kg/s` liquid. The subsequent incomplete block was not credited and the later live field diverged.
- Controlled response: do not reuse a failed field. Use clean resolved-outlet
  lineage, delete inherited DPM injections, establish a bounded liquid pool and
  qualify outlet opening before ramping any inlet flow.
- Execution evidence: setup 07h preparation passed and the initial pool established the intended outlet phase directions at iteration 25. By iteration 250, brine liquid outflow was nonphysical (`-3304.7817 kg/s`) and mixture imbalance was `1602.99%`; the next incomplete block ended in AMG divergence and a floating-point exception at residual row 292.
- Numerical-method evidence: Fluent recommended Warped-Face Gradient Correction for this polyhedral mesh after importing settings; the stopped live case reads back `enable=False`. This is a controlled numerical sensitivity candidate, not proof that the boundary formulation is valid.
- Physical uncertainty: the real steady water level and downstream brine pressure are not supplied. The initial level is a geometry-derived inference; equal pressure inputs are a controlled first bracket, not plant validation.
- Impact: mesh convergence, separator efficiency, DPM and EWF remain blocked until one source-free resolved-outlet carrier case has correct phase direction, phase/mixture closure and stable monitors.
- Next action: explicit-VOF halving and closed-pool solver swapping are stopped.
  Implicit readback, temporal/interface sensitivities and plain Coupled have
  now been adjudicated; PISO is retained because Coupled reproduces the field
  within `0.000063%` at `3.234x` the summed solve-step wall time. Setup 07n may
  next run only a separately gated outlet pressure-response sign probe and
  idealized constant-level diagnostic. Obtain or explicitly define a
  defensible downstream brine pressure, resistance or level condition before
  any plant claim; do not treat a manual pressure choice as plant data.
- Current infrastructure blocker: the 07n-c response-sign runner is ready, but
  attempt 1 lost its stream during a read-only parent report and attempt 2
  failed raw TCP before authentication. Both credited zero physical steps and
  are prohibited from resume. The server-1 Windows host answers ICMP while its
  configured Fluent port times out; restart Fluent 2024 R2 in server mode with
  16 ranks and refresh connection details if the port changes before attempt 3.
- Configured-server-2 evidence: the earlier audit had conflated it with the
  partner's occupied Fluent 2025 R2 endpoint. The configured endpoint was
  Fluent 2024 R2, 16 ranks and unowned, so a separate clean case-only
  reconstruction was permitted without touching the prohibited steady
  Mixture field. It reproduced the closed pool and remained clean through
  `dt=2.56e-4 s`; `dt=5.12e-4 s` then failed the within-step continuity
  envelope at a maximum of `2.56074` and is terminal. This improves numerical
  reproducibility evidence but does not remove BLK-015: both inlets were zero,
  the brine face was a wall, and the authoritative server-1 step-940 pair was
  absent. Outlet response, drainage, level regulation and operating mass
  closure therefore remain untested.
- Setup-07i execution evidence: attempt 8 completed mesh/settings/WFGC/pool preparation on exactly 16 solver processes. The roster lists `n0..n15`; `/20` is the hardware-core denominator, not process count. Continuity reached `6.9888e14` at transcript iteration 20 and the GUI recorded Node-4 SIGSEGV/server shutdown at iteration 21. Zero complete blocks were credited and no divergent checkpoint was written. The restarted server is healthy and again verified at 16 processes, but the identical failed steady case will not be retried.
- Setup-07j execution evidence: clean transient VOF preparation passed, but at `t=0.0002 s` the equal-pressure brine outlet discharged `4692.8688 kg/s` liquid. Inventory/boundary accounting closes to `0.4601%` of feed, so this is genuine model drainage. The pressure-bracket field is stopped and prohibited from resume.
- Setup-07k evidence: the prescribed brine route held exactly, but step 3 reached `-4.1102e13 Pa` steam-outlet pressure, `5.2599e6 m/s` steam-outlet velocity and `7.2714e4 m/s` domain velocity. The step-4 RPC timed out uncredited after two hours. No controller remains and the field is prohibited from resume.
- Setup-07l evidence: all six inherited DPM injections were deleted, both
  inlets were zeroed and the brine face was temporarily closed. Ten guarded
  `1e-6 s` steps completed with final continuity `3.4698e-6`, domain velocity
  `4.8978e-7 m/s`, unchanged inventory and no DPM/server failure. The lower
  wall stabilized `2090.4 Pa` above the steam outlet, close to the
  `2197.24 Pa` hydrostatic centroid estimate.
- Setup-07n evidence: a zero-step scan isolated the invariant `98,473`-cell
  interval and centered threshold, closing the reproducible whole-cell
  selection issue but not validating a plant level. The fresh mesh-selected
  chain completed 940 guarded steps to `0.22271 s` with no hard-gate failure,
  unchanged `3877.468071 kg` inventory, brine liquid VF `1.0`, storage closure
  at numerical round-off and zero liquid at the steam outlet. The final-20
  average-velocity/vorticity/maximum-velocity regressions were `-1.540%`,
  `-0.637%` and `-0.912%`.
- Setup-07n matched-`dt` evidence: 20 base steps at `2.56e-4 s` and 40 half
  steps at `1.28e-4 s` cold-loaded the same step-940 parent and ended at the
  same `t=0.22783 s`. Average velocity and vorticity differed `0.906%` and
  `0.941%`, pressure/inventory/VOF/steam seal matched, but maximum velocity
  differed `7.332%`. Time-step independence is therefore unresolved. A
  turbulent-viscosity limiter remained confined to one cell without a hard
  failure and is a candidate explanation for the local sensitivity.
- Setup-07n quarter-step evidence: 80 steps at `6.4e-5 s` loaded the identical
  step-940 parent and ended at the same `t=0.22783 s`. Relative to the half
  step, endpoint average velocity, vorticity and maximum velocity changed
  `-1.427%`, `-1.404%` and `-7.491%`; matched-sample mean differences were
  `0.817%`, `0.810%` and `5.935%`. Continuity improved and Courant halved, but
  the field discrepancies did not contract. This rules out promotion and a
  blind additional timestep halving.
- Setup-07n inner-iteration evidence: the fixed-`dt` 100-inner branch reproduced
  the 20-inner baseline to better than `0.000009%` for average velocity,
  vorticity and maximum velocity across all matched samples. Continuity fell
  `99.70%` to `1.14616e-6` without changing the field. This accepted diagnostic
  rules out insufficient inner convergence as the timestep-discrepancy cause.
- Setup-07n localization evidence: base, half and quarter maxima share cell
  index `382511` and centroid `(0.809789, 0.0420206, 0.651966) m`. Liquid VF is
  `0.134811-0.134831`; the top-20 sets strongly overlap. The sensitive region
  is therefore a persistent interface feature. Its turbulent viscosity is
  only `0.20-0.24%` of the domain maximum, so the known limiter cell is not the
  maximum. The accepted localization used zero iterations/initializations and
  zero case/data writes.
- Setup-07n `dt/8` evidence: 160 guarded steps at `3.2e-5 s` passed every hard
  gate and reached the matched `0.22783 s` endpoint, but quarter-to-eighth
  endpoint differences remained `2.150%`, `1.936%` and `7.283%` for average
  velocity, vorticity and maximum velocity. The sequence is not asymptotic and
  further explicit timestep halving is withheld.
- Setup-07n implicit evidence: accepted zero-step attempts 8/9 proved the
  Fluent 2024 R2 implicit-VOF/PISO contract. Matched first-order Compressive,
  second-order Compressive and second-order Modified-HRIC branches all passed
  hard gates. Second-order Modified-HRIC is the closest implicit result, but
  its maximum velocity remains `6.831%` above explicit; formulation
  independence therefore fails.
- Setup-07n coupling evidence: the accepted explicit/plain-Coupled branch
  read back `coupled_form=false` and reproduced PISO bulk/local velocity to
  within `0.000063%` while costing `3.234x` as much summed solve-step wall
  time. Coupling sensitivity is cleared for this matched closed-pool window;
  PISO remains the efficient diagnostic baseline.
- Next controlled response: do not rerun 07j/07k, open any matched endpoint or
  resume any implicit/Coupled endpoint. The next bounded physical work is an
  outlet pressure-response sign test followed, only if the sign and hard gates
  pass, by an idealized constant-level diagnostic. Production remains blocked
  pending downstream pressure/resistance/operating-level evidence.
- 2026-08-25 server-2 execution state: the independent step-90 parent remains
  intact, but the matched control stalled in a non-physical scratch-report
  cleanup verification after four fully monitored passing steps. The first
  pressure attempt then stopped before authentication because Fluent did not
  return its Scheme version string, despite 3/3 raw-TCP probes. No outlet was
  opened and no physical pressure-response step exists. This adds an active
  Fluent-service-health blocker; it does not change the downstream
  pressure/resistance/level blocker or justify full feed.

## Setup 07g unresolved inputs and execution risks (2026-08-13)

- The physical downstream brine-system pressure or liquid-level datum has not
  been supplied. Setup 07l shows that equal `1.12 MPa` at the elevated steam
  outlet and submerged brine face is not neutral: the closed lower face carries
  about `2.09 kPa` hydrostatic head. Any new pressure value is diagnostic until
  downstream evidence is supplied.
- PyFluent's live monitor stream returned zero residual points despite Fluent's transcript proving 25 completed iterations. The controller now requires transcript residual-row proof as a fallback and preserves each completed checkpoint.
- The HDF5 mesh passes Fluent's basic volume/quality check, but its maximum aspect ratio is `66.0258` and its minimum face area is `4.434417e-11 m2`; local outlet/pipe fields must be inspected before performance claims.
- No mesh-independence sequence exists for the resolved-outlet geometry. Even an accepted setup-07g carrier result qualifies only this mesh and boundary formulation.
- DPM and EWF remain blocked until phase/mixture closure and iteration independence pass on the carrier field.

## Active Blockers

### BLK-014 | Local sink thickness and fixed strength do not enforce a constant level

- Status: Active / diagnostic sensitivity failed physical qualification.
- First observed: 2026-08-09 NZST.
- Related run(s): `SPLIT-07B-TAU010-QUALIFICATION-2026-08-07`, `SPLIT-07C-THICK-SINK-QUALIFICATION-2026-08-08`, `SPLIT-07D-CAPACITY-MATCHED-SINK-2026-08-10` and diagnostic control `SPLIT-07E-ADAPTIVE-MASS-BALANCE-SINK-2026-08-10`.
- Active bounded follow-up: setup `07f` is running three clean-origin diagnostic cases that double/triple the band height and increase the fixed source coefficient. This tests the local-supply hypothesis only; it does not retire the blocker or replace the resolved-brine-outlet action.
- Controlled evidence: setup 07c retained the clean 900k mesh, authoritative carrier settings, fresh Hybrid Initialization, boundaries, `tau=0.1 s`, wall geometry and DPM-off state; only the bottom-local source mask increased to `0.1401652536 m`, 92,058 cells and `0.44378932 m3`.
- Qualification evidence: after 1,000 ramp and 2,000 full-strength iterations, zero windows passed. Endpoint sink was `22.4882 kg/s` against `116.92 kg/s` liquid inlet; inventory was `71.7785 kg`; corrected source-inclusive liquid imbalance `80.7661%`; pressure `27.1372 kPa`; continuity `0.191551`.
- Stability symptom: final-500 pressure, sink, inventory, outlet velocity and domain velocity drift were `8.53%`, `29.99%`, `16.93%`, `4.24%` and `6.78%`, respectively.
- Sensitivity result: the 16-layer-equivalent band produced about `13-16x` the setup-07b sink at equal R1 counts, proving the mask thickness matters numerically, but it still removed only `19.23%` of liquid inflow and did not arrest filling/redistribution.
- Fixed-strength result: setup 07d changed only `tau 0.1 -> 0.02 s`. After 1,000 ramp and 2,000 full-strength iterations, the sink reached `46.9874 kg/s` (`40.19%` of feed), corrected liquid imbalance remained `59.8122%`, pressure/inventory/sink final-500 drift remained `6.618/14.120/23.044%`, continuity was `0.229682`, and zero windows passed. A 5x coefficient yielded only 2.09x removal because active-band inventory fell to `0.93975 kg`.
- Adaptive-control result: setup 07e completed 1,000 ramp plus 2,000
  full-strength iterations with zero passing windows. At the minimum
  `tau=0.002 s`, it removed `50.954294 kg/s` (`43.6%` of feed), left
  `56.419329%` corrected liquid imbalance, and ended at `26.7252 kPa` pressure
  drop, `65.007547 kg` domain inventory and `0.254617` continuity. Final-500
  pressure/sink/inventory drift remained `5.8506/26.1894/13.3524%`.
- Capacity evidence: setup 07e held only `0.101909 kg` liquid in the active
  band, versus `0.23384 kg` required to meet the inlet command at the minimum
  tau. The adaptive source therefore remained limited by local liquid access;
  it did not supply or validate brine-outlet hydraulics.
- Accounting correction: raw setup-07b/07c `liquid_source_augmented_*` fields double-count the phase-2 source. Correct liquid imbalance is `80.7661%` for 07c and `91.1909%` for 07b. This makes neither branch acceptable and changes no stability-window decision.
- Impact: setups 07b/07c/07d/07e are completed diagnostic branches, not
  physically qualified constant-water-level models. Further thickness/tau
  tuning cannot validate missing brine hydraulics. Mesh convergence,
  efficiency, DPM and EWF remain blocked.
- Next action: when geometry editing is possible, add a resolved brine outlet and qualify one medium mesh for source-free phase/mixture closure, stable liquid inventory and iteration independence. Use the continuity-only area envelope and official-guidance boundary-condition sequence in `PyAnsys/output/setup07_meeting_visuals_20260811/`: prefer a pressure outlet when downstream static pressure is defensible, and retain a `116.92 kg/s` mass-flow outlet only as a strictly outward diagnostic bracket.

### BLK-013 | Constant-water-level sink failed physical qualification
- Status: Active / qualification failed at maximum budget.
- First observed: 2026-08-07.
- Related run(s): `SPLIT-07B-UDF-HOOK-2026-08-07`, `SPLIT-07B-UDF-SMOKE-2026-08-07`.
- Resolved implementation scope: the compiled UDF persists after cold reload, reserves five UDMs, attaches liquid mass to phase 2 only, attaches carried x/y/z momentum to mixture, leaves vapor sources and DPM off, and passed a one-iteration source-integral proof.
- Qualification evidence: the clean 900k `tau=0.1 s` run completed 500 ramp plus 6,000 full-strength iterations with zero passing acceptance windows. Endpoint sink magnitude was `8.06194 kg/s` against `116.92 kg/s` liquid inlet; domain liquid inventory reached `191.836 kg`; corrected source-inclusive liquid imbalance remained `91.1909%`; continuity was `0.279243`.
- Stability symptom: over the final 500 full-strength iterations, pressure drift was `2.60%`, sink drift `17.89%`, liquid-inventory drift `10.07%`, domain-velocity drift `1.76%` and vorticity drift `1.42%`. Residual-level and `k` trend gates failed.
- Start-state control: satisfied. Preparation v3 used the clean original `mesh-900k.msh`, matched its SHA-256 and the normalized authoritative settings fingerprint, used fresh Hybrid Initialization, loaded no saved solution data and ran zero production iterations. The 6000-iteration setup-07a field and one-iteration UDF smoke field remain forbidden as production initial data.
- Geometry evidence gap: the project interpretation identifies `bottom` as the constant-water-level plane, but the source-CAD elevation/image is not yet linked into the evidence package.
- Impact: setup 07b cannot support separator efficiency, validation, mesh independence, GCI, DPM or EWF results. The failure also means a tau sweep cannot by itself establish physical credibility for the one-cell abstraction.
- Next action: define a resolved brine-outlet branch and qualify one medium mesh. Retain any later `tau` or sink-layer sensitivity as diagnostic evidence only.

### BLK-011 | Split-inlet mesh study cannot pass preflight
- Status: Resolved / superseded by BLK-012.
- First observed: 2026-07-29.
- Related run(s): `SPLIT-MESH-PREFLIGHT-2026-07-29`.
- Symptom: the configured Fluent endpoint timed out, the active processor count was unknown, no systematic three-mesh binaries were local, and the actual split-inlet archive conflicted with intended setup-07 numerics.
- Current interpretation: remote access, 16-process readback, geometry/zone mapping, settings authority and a seven-mesh ladder were subsequently verified. Preflight passed and all formal runs completed.
- Next action: none for preflight; use BLK-012 for the unresolved physical/iteration-convergence limitation.

### BLK-012 | Closed-bottom steady carrier field has increasing liquid inventory
- Status: Active / study-limiting.
- First observed: 2026-08-05 checkpoint audit; monitor drift was visible earlier in the formal runs.
- Related run(s): `SPLIT-MESH-CARRIER-2026-08-01`, `SPLIT-MESH-900K-EXT-2026-08-05`.
- Symptom: all seven 3000-iteration mesh endpoints fail pressure and/or velocity stability criteria. Extending the 900k mesh to 6000 leaves final-500 pressure drift at `4.61%`, continuity near `0.246`, and secondary-phase residual near `1.75e-3`.
- Direct evidence: liquid inventory measured from the volume integral of `phase-2-vof` rises from `104.05 kg` at iteration 4000 to `171.03 kg` at 6000 (`+64.37%`); pressure drop rises from `31.03` to `34.05 kPa`.
- Current interpretation: with `116.92 kg/s` liquid entering, `bottom` as a wall and no dedicated liquid discharge, the steady calculation is undergoing filling/redistribution rather than approaching a fixed-inventory steady state. Treating liquid imbalance as an accepted geometry limitation does not supply a steady storage term.
- Impact: setup 07a remains diagnostic; mesh independence, GCI, separator efficiency and validated carrier quality cannot be claimed. DPM/EWF must remain blocked.
- Next action: freeze setup 07a. If steady performance is required, define a new branch with a physically credible liquid discharge and qualify one medium mesh before repeating the ladder. Use closed-bottom transient modelling only for an explicitly finite-time filling question.

### BLK-009 | Fixed 1500-iteration completion is not convergence proof
- Status: Active
- First observed: 2026-07-21.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`, `PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: all 12 runs completed 1500 carrier iterations, but final continuity residuals remained approximately `0.193-0.343` for the baseline cases and `0.145-0.229` for the spiral cases. Baseline incomplete DPM mass ranges from `36.06` to `58.01 kg/s`.
- Current interpretation: the steam-quality values are provisional DPM outputs, not converged validation results. The full residual/physical-monitor trend and incomplete-particle locations must be assessed before claiming replication.
- Next action: run a controlled continuation on representative cases with residual and outlet-flow stopping criteria, then decide whether all six cases require extension.

### BLK-010 | Historical sweep manifests do not preserve the complete DPM contract
- Status: Active for evidence qualification; mitigated for future runs by automation preflight.
- First observed: 2026-07-29 compliance audit.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`, `PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: historical manifests do not preserve all tracking controls, wall fates, face-normal geometry orientation, and interaction readbacks. The baseline branch also lacks a standalone residual CSV for Case 1.
- Current interpretation: the accepted reports provide consistent `Final` DPM mass flows and passing injection mass balances, but they cannot prove full setup parity independently. Particle-count weighting is not a defensible substitute for fate mass flow.
- Next action: use the hardened preflight/report path for any rerun, capture full DPM state plus zone normals, and require fresh per-injection reports before accepting outputs.

### BLK-008 | Remote PyFluent sweep is vulnerable to sleep and VPN loss
- Status: Active / mitigated by checkpoints and recovery manifests.
- First observed: 2026-07-21.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: closing the Mac lid or losing VPN/Wi-Fi removes the gRPC stream while Fluent may continue the already-issued iteration block remotely.
- Current interpretation: `caffeinate` prevents idle sleep but cannot override lid sleep. Short chunks, explicit checkpoints, and first-residual recovery verification limit lost work, but continuous connectivity is still required for unattended sequencing.
- Next action: keep the Mac lid open and VPN connected; prefer an on-PC controller or persistent remote host for future long sweeps.

### BLK-007 | Fluent-exported split-inlet mesh does not yet preserve the exact required zone contract
- Status: Active
- First observed: 2026-06-10
- Related run(s): `MESH-TRIAL1-SPLIT-CONTRACT-AUDIT-2026-06-10`
- Symptom: the corrected `mesh-trial1.msh` now reopens with two separate velocity-inlet boundaries, but Fluent currently exposes them as `liquidinlet` and `steaminlet`, and the exported boundary list does not include `wall-smooth_spiral_separator`.
- Current interpretation: this is a mesh-export / naming-preservation blocker for the semi-automated split-inlet workflow, not a geometry-change request. Conservative mesh-control trials should not be accepted until the exported baseline itself satisfies the exact required-zone contract.

### BLK-006 | PyFluent baseline script still has version-specific API gaps
- Status: Active
- First observed: 2026-06-09
- Related run(s): `PYFLUENT-TRIAL3-SMOKE-2026-06-09`
- Symptom: the local one-inlet reconstruction can launch, initialize, and iterate, but the high-level operating-pressure setter still fails and several intended solution-method setters do not match the current Fluent 2026 R1 PyFluent object paths.
- Current interpretation: this is now a narrow automation-parity blocker, not a full environment blocker. The important result is that the case is already runnable; the remaining task is to make the script cleaner and less ambiguous.
- Update after `PYFLUENT-TRIAL4-HARDENED-2026-06-09`: operating-pressure control and numerics-path discovery are now resolved; the remaining issue is smaller and mostly limited to pressure-outlet subsetting inactivity cleanup.
- Update after `PYFLUENT-TRIAL4-500-2026-06-09`: the longer controlled diagnostic run completed, so this is no longer a stability blocker for the one-inlet branch. The remaining issue is mostly tooling/polish: pressure-outlet subsetting inactivity and the empty direct residual-write export.

### BLK-001 | Baseline run not converging
- Status: Downgraded to setup/debug history
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A`
- Symptom: no satisfactory convergence after 1000 iterations.
- Current interpretation: this run is no longer part of the active quantitative evidence base because it did not exceed the current `1000`-iteration evidence threshold and did not converge. Retain it only as a setup-history warning unless the Bangma-based reconstruction becomes necessary again.

### BLK-002 | No interpretation framework for simulation outputs
- Status: Active
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A` and follow-up runs
- Symptom: uncertainty about which outputs indicate separator performance and what model change should follow from results.

### BLK-003 | Split-inlet orientation and allocation not yet frozen
- Status: Active
- First observed: 2026-04-30
- Related run(s): next split-inlet A/B case
- Symptom: `left/right` wording is not precise enough to guarantee the correct wall-side vs inner-side phase placement on the spiral-inlet face.

### BLK-004 | Current split-inlet/brine-outlet result has unclassified problems
- Status: Historical / not blocking setup `07`
- First observed: 2026-05-18
- Related run(s): `FFF-2`, `MWH-WP-2026-05-07-A`
- Symptom: the parent `FFF-2` case is already not converged and not liquid-mass-balanced after approximately `1020` iterations without water-pool initialization; the water-pool child case then develops additional liquid inventory depletion and extreme steam-outlet liquid carryover.
- Current interpretation: this remains historical troubleshooting context for older mixed wet-half/brine-outlet cases. For setup `07`, bottom truncation without an active brine outlet or water pool is accepted as out of scope, so this blocker should not delay steam-carryover/DPM efficiency checks.

### BLK-005 | Steam outlet geometry/intake may be entraining liquid
- Status: Historical / not blocking setup `07`
- First observed: 2026-05-18 from review of newest setup report
- Related run(s): `MWH-WP-2026-05-07-A`
- Symptom: guessed steam outlet geometry appears likely to create turbulence or suction near the intake, with reported liquid through steam outlet of `1044.35 kg/s`.
- Current interpretation: retain as a warning from the older water-pool branch only. The professional setup `07` run currently shows low apparent steam-line carryover, so this should not block the baseline DPM sweep.

## Ranked Hypotheses
1. Parent `FFF-2` has an unresolved convergence/mass-balance problem even without initialized water, but this is historical context rather than an active setup `07` blocker.
2. Brine outlet pressure, backflow settings, or outlet type may be over-driving liquid removal in older parent cases; this is not part of the setup `07` acceptance scope.
3. Missing stabilization tuning in numerics may be preventing the mixed wet-half velocity-inlet case from settling.
4. Mesh quality may still be insufficient in the inlet, swirl, steam-outlet, or brine-outlet regions.
5. Inlet phase allocation may be too sharp or incorrectly oriented, creating an artificial steam jet or liquid blockage.
6. Steam outlet geometry/intake behavior may be entraining liquid and causing excessive carryover.
7. The steady solver is depleting the initialized lower water pool in the child case, producing transient-like liquid drainage inside a steady calculation; this is now out of scope for setup `07`.
8. The project still needs residual/monitor stability and DPM fate counts before setup `07` can become report-quality efficiency evidence.
9. The direct PyFluent rebuild path is now proven runnable, significantly hardened, and stable enough for a controlled `500`-iteration diagnostic, but pressure-outlet setting inactivity and residual-export behavior still need cleanup before treating it as a polished baseline automation workflow.

## Recovery Plan
1. For setup `07`, proceed with steam-carryover/DPM efficiency checks without reopening bottom/brine-outlet troubleshooting.
2. Record residual/monitor stability for `PLS-PRO-2026-06-03-A`.
3. Run DPM diameter checks at `5 um`, `10 um`, and `40-41 um`.
4. Keep `FFF-2` and `MWH-WP-2026-05-07-A` as historical troubleshooting references only unless the project scope later returns to brine-drainage or water-pool modelling.
5. For the new one-inlet PyFluent path, keep `trial4` plus the completed `500`-iteration diagnostic as the active local baseline and clean up pressure-outlet setting order plus residual export before extending much further.
## 2026-08-21 — Setup 07m production-boundary blockers

- `Accepted diagnostic`: zero-feed opening is bounded and monotonic around the
  CFD-derived closed-face pressure.
- `Accepted diagnostic`: a 0.1% inlet hold reaches continuity below 0.01.
- `Unresolved`: the actual downstream brine static pressure, level datum and
  pipe/valve/control resistance remain unavailable, so the centre pressure
  cannot be promoted to a plant boundary condition.
- `Unresolved`: a 1% abrupt start with 20 inner iterations failed the continuity
  gate even though the field and Courant remained bounded. The current smaller
  staged ramp must pass before higher flow is attempted.
- `Blocked claim`: do not claim operating-flow balance, level control,
  separator efficiency, mesh independence, DPM carryover or EWF performance
  from setup 07m.

## 2026-08-21 — Model-form and downstream-resistance blocker

- `Resolved scope correction`: the older setup-09 preference for DPM/RSM-DPM
  concerned a separator truncated above the brine drain. It does not remove
  VOF from consideration when the pool and drainage route are explicitly
  resolved.
- `Narrowed model form`: explicit VOF/PISO remains the numerical baseline.
  Plain Coupled has now reproduced its field within `0.000063%`, while matched
  implicit/PISO Compressive and Modified-HRIC branches retained a material
  interfacial maximum-velocity difference (`6.831%` for the closest implicit
  branch). Transient Mixture and Eulerian/Multi-Fluid VOF have not been run on
  an accepted identical constant-level drainage window; they remain future
  physics comparisons, not substitutes for the missing outlet closure.
- `Unresolved hydraulic closure`: the resolved outlet area is
  `0.19936247 m2`. At the reference liquid feed it implies about `0.666 m/s`
  and a velocity head of about `195 Pa`, while the hydrostatic-rest diagnostic
  is about `2090.4 Pa`. Unknown downstream pipe, valve and level-control losses
  may therefore dominate the discharge response.
- `Execution rule`: do not use a solver or turbulence change to compensate for
  an unphysical outlet boundary. Complete the numerical one-factor tests first,
  then qualify a measured pressure/head or resistance formulation before mesh
  convergence.
- `Scope correction`: constant water level itself is not a missing or
  unreasonable assumption. It is the intended operating constraint and steam
  seal. What remains missing for plant validation is the exact level elevation
  and the real valve/pipe response used to maintain it.
- `Available diagnostic closure`: a paired liquid feed/drain ramp can impose
  ideal constant-level control. A more plant-like comparison adjusts
  liquid-outlet pressure from measured level/inventory error with bounded gain,
  anti-windup and slew rate. These are useful CFD baselines before the plant
  valve curve is known only if they are labelled as idealized controls and pass
  steam-seal, storage, time-scale and residual gates.
- `Geometry blocker`: the present short outlet leg may not represent the water
  drum or U-bend loop seal described for operating geothermal separators. If a
  properly submerged 07n VOF pool cannot keep the boundary liquid-filled, an
  explicit seal geometry is required; solver tuning is not an acceptable fix.

## 2026-08-22 — Setup 07n Stage-0 local cell-resolution blocker

- `Superseding mesh-selection evidence`: an accepted threshold scan now proves
  that every threshold in
  `y=0.0164023303045-0.0165144008650 m` selects the same `98,473` whole cells;
  the centered value `0.0164583655847 m` reproduced the expected
  `4.400159116 m3` / `3877.468071 kg` pool. This closes deterministic cell-set
  selection for diagnostic initialization.
- `Remaining scope`: direct adjacent-cell vertex height is still unavailable,
  and neither the centered CFD threshold nor its inventory is a measured plant
  level. The blocker is therefore narrowed from numerical selection to
  physical submergence and operating-level validation.

- `Accepted diagnostic`: exact surface connectivity resolves the brine crown
  at `y=-0.0015579789 m`, the invert at `-0.5067311525 m`, the opening area at
  `0.1993624690 m2` and the median crown-touching boundary-face height at
  `0.0089871744 m`.
- `Accepted diagnostic`: fresh case-only initialization and VOF patching give
  exact mesh-selected liquid inventories of `3877.46807 kg` and
  `3909.27263 kg` for the two/four-face-height numerical brackets.
- `Unresolved`: Fluent 2024 R2 does not implement PyFluent 0.39's full
  volume-cell mesh RPC. A temporary register's `create_volume_surface` state
  read back true but created no field-data surface; the initialized UTL
  `volumes` report failed with unbound `pm/volumes`.
- `Bounded pilot evidence`: the lower proxy was run only under an explicit
  diagnostic label. Ten `1e-6 s` plus ten `2e-6 s` closed-drain steps passed
  every residual/VOF/Courant/pressure/velocity/storage/steam-seal/clock gate,
  but covered only `30 us` versus a local gravity scale of `~0.0428 s`.
- `Impact`: the old face-proxy field is not promoted, but the new centered
  whole-cell field is a reproducible diagnostic parent for closed-drain
  relaxation only. Outlet opening, model/solver screening and mesh convergence
  remain withheld pending stationarity and timestep evidence.
- `Recovery`: finish meaningful-time relaxation and a matched `dt/2` window.
  Independently obtain the plant level or defensible submergence range before
  interpreting the CFD-selected threshold as an operating condition.
- `Unaffected blocker`: actual operating level, downstream head and valve/pipe
  response remain missing for plant validation even after the numerical mesh
  level is resolved.
