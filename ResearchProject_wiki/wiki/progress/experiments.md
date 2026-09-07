# Experiment Log

### Run SPLIT-07N-SERVER2-0P05-CALIBRATED-PRESSURE-S70-2026-08-28

- Run ID/date: `b620_07n_s2_0p05_pstep23p219_after10_s70_a1_20260828`,
  2026-08-28 NZST.
- Objective: test whether the accepted short 0.05%-feed balance persists over
  70 steps after one pressure change calibrated from matched open-loop
  response evidence.
- Geometry/mesh: resolved-brine full separator, `620,431` cells; independent
  checksum-bound server-2 clean step-90 parent. No diagnostic endpoint was
  used as a parent.
- Physics/numerics: transient explicit VOF, PISO, PRESTO,
  Geo-Reconstruct/WFGC, RNG k-epsilon, gravity, `dt=1.28e-4 s`, 100 inner
  iterations, DPM zero/off, EWF off and all sources/sinks off.
- Boundaries: liquid/vapor feed `0.05846/0.040345 kg/s`; brine pressure
  `1,122,263.621237 Pa` through step 10 and `1,122,286.840068 Pa` thereafter.
  The pressure is CFD-derived, not plant data.
- Budget/evidence: 70/70 steps completed; checkpoints at 0, 1, 5, 10, 11,
  20, 30, 36, 45, 55 and 70; physical and residual histories plus manifests
  and a non-overwriting final disposition were retained.
- Convergence/monitors: final-two continuity
  `7.90715e-4/7.93757e-4`, final Courant `0.00764008`, maximum velocity
  `0.214241 m/s`, VOF `[0,1]`, brine liquid VF `1.0`, unchanged reported
  inventory and zero cross-phase outlet leakage.
- Mass balance: final liquid/vapor/total imbalance
  `-0.01155471/+0.0000760171/-0.011478693 kg/s`. Final-ten maximum absolute
  liquid/vapor/total imbalance was
  `0.01155471/0.0000760171/0.011478693 kg/s`; the `0.005 kg/s` sustained gate
  failed.
- Outcome: `Partially Converged / Diagnostic Unresolved`. Residual and steam-
  seal gates passed, but hydraulic balance drifted after the short balance
  window. Endpoint is ineligible, non-resumable and not constant-level proof.
- Next action: from clean step 90, change only one further held pressure action
  after the established short balance window. Do not repeat unchanged or
  begin mesh convergence/full flow.

### Run SPLIT-07N-SERVER2-0P05-SUSTAINED-CONTROL-2026-08-26

- Run ID/date: fixed-pressure long hold plus delayed adaptive-pressure gain
  sensitivities, 2026-08-26 NZST.
- Objective: determine whether the accepted ten-step 0.05%-feed state sustains
  low phase/total imbalance and whether bounded brine-pressure feedback can
  correct long-time drainage without losing the liquid steam seal.
- Geometry/mesh: resolved-brine full separator, `620,431` cells, independent
  checksum-bound server-2 clean step-90 parent for every branch; no endpoint
  was reused as a parent.
- Physics/numerics: transient explicit VOF, PISO, PRESTO,
  Geo-Reconstruct/WFGC, RNG k-epsilon, gravity, `dt=1.28e-4 s`, 100 inner
  iterations, DPM zero/off, EWF off and all sources/sinks off.
- Boundaries/initial state: liquid/vapor feed `0.05846/0.040345 kg/s`; initial
  diagnostic brine pressure `1,122,263.621237 Pa`; submerged brine face. The
  pressure is CFD-derived, not plant data.
- Fixed-pressure outcome: stopped after 36 credited steps when liquid/total
  imbalance reached `-0.050185643/-0.049855477 kg/s`. Continuity
  `7.91749e-4`, Courant `0.00452474`, VOF, pressure, velocity, inventory and
  phase-routing gates remained bounded.
- Gain-0.25 outcome: completed 50 steps; final liquid/total imbalance
  `+0.019462106/+0.019334063 kg/s`, continuity `7.73340e-4`, Courant
  `0.00567281`. It crossed balance but overshot; the final-five balance gate
  failed.
- Gain-0.05 outcome: stopped after 47 credited steps when the following Fluent
  solve lost its stream. Last liquid/total imbalance
  `-0.038632126/-0.038377965 kg/s`, continuity `7.72592e-4`, Courant
  `0.00542563`; steam seal and phase routing remained intact.
- Outcome: `Partially Converged / Diagnostic Unresolved`. Residual and seal
  behavior are good, but sustained mass balance is not. All endpoints are
  ineligible/non-resumable.
- Hypothesized cause: pressure-to-drainage response lag makes a per-step
  proportional update either overshoot (gain 0.25) or correct too slowly
  (gain 0.05); downstream resistance and real operating-level data are still
  missing.
- Next action: cold-load clean step 90 and test one lag-aware controller change
  only (settle-and-update or filtered/PI level feedback), with the same physics
  and gates. Do not resume these fields or start mesh convergence.

### Post-processing SETUP-07N-SERVER2-0P05-CARRIER-PATHLINE-VIDEO-2026-08-25

- Source: accepted server-2 0.05%-feed step-100 pair, flow time `0.00639 s`,
  case/data hashes `d0247380...bd52` / `38447356...e97b`.
- Controls: post-processing only; Fluent 2024 R2 and 16 ranks; checksum,
  pressure, inlet, phase, clock, DPM-zero/off, EWF-off and source-off readbacks;
  zero initialization, iteration, DPM update and case/data write.
- Accepted graphic: 12 progressive integration views from the exact
  `liquidinlet` surface, 827 massless carrier seeds, velocity-coloured through
  the frozen endpoint field. Output is 1600 x 900 H.264, 12 fps, 72 frames and
  6.0 s; SHA-256 `3a028c07...6537`.
- Rejected graphic: Fluent changed the optional `steaminlet` release to
  `wall-fluid` after two readbacks, so no steam-origin scene was included.
- Interpretation: accepted diagnostic post-processing visualization only. The
  reveal clock is not CFD physical time and the traces are not droplets, DPM
  parcels, phase-specific trajectories, carryover or efficiency evidence.
- Evidence:
  `../../../PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07n_s2_p1122264_0p05feed_step100_carrier_pathline_video_attempt3_20260825/video_manifest.json`.

### Run SPLIT-07N-C-SERVER2-LOW-FEED-DRAINAGE-2026-08-25

- Parent/model: independent checksum-bound server-2 step 90; Fluent 2024 R2,
  16 ranks, explicit VOF/PISO, dt=128 us, 100 inner iterations, DPM zero/off,
  EWF off and no sources/sinks. Every member cold-loaded the same pair.
- Accepted balanced member: common inlet fraction 0.0005, brine pressure
  1,122,263.621237 Pa, ten steps. Liquid in/out 0.0584600/0.0584601 kg/s,
  vapor in/out 0.0403450/0.0403450 kg/s, total net -9.11e-8 kg/s, continuity
  tail 0.00201686/0.00173276, Courant 0.00248721, unchanged inventory and zero
  vapor-brine/liquid-steam leakage. Classification: accepted diagnostic;
  eligible_parent:false because the pressure is CFD-derived.
- Load bracket: 0.05625% completed ten steps with liquid net +0.00195577 kg/s
  and final continuity 0.00190599; 0.0625% and 0.075% stopped after step one
  at continuity 1.05293 and 1.26332. Failed fields are terminal.
- Outlet inspection: Fluent 24.2 exposed phasic but no writable bulk mixture
  mass-flow-outlet rate; forced phase routing was not used.
- Outcome: resolved drainage and mass closure are demonstrated only at very
  low feed. Full flow, plant-valid pressure, long-time/controller robustness
  and mesh independence remain unproved.

### Post-processing SETUP07-MEETING-VISUALS-2026-08-10

- Activity ID: `SETUP07-MEETING-VISUALS-2026-08-10`; post-processing only, no new CFD iterations.
- Objective: create meeting-ready numerical figures, matched Fluent contours and verified carrier pathlines that explain why setup 07a/07b/07c remain diagnostic and why a resolved brine outlet is recommended.
- Source states: setup-07a 900k iterations 4000 and 6000 for matched liquid-VF/pressure fields; setup-07c full-strength R1 = 2000 for sink-mask and pathline evidence.
- Graphics controls: common `x=-1.5 m` plane, cell values, fixed liquid-VF and absolute-pressure scales, common camera and 1920 x 1440 hardcopies. Pathlines use the Mixture-model carrier domain and `liquidinlet` release; DPM remained off.
- Key evidence: closed-bottom liquid inventory `104.05 -> 171.03 kg` (`+64.4%`) and pressure drop `31.03 -> 34.05 kPa` (`+9.7%`) from iterations 4000 to 6000; setup-07c endpoint sink `22.49 kg/s`, only `19.2%` of the `116.92 kg/s` liquid inlet.
- Outcome: `Diagnostic evidence package completed`. It supports the formulation decision but does not upgrade any CFD run to accepted, converged or validated status.
- Safety/readback: no initialization, iteration, DPM injection update or case/data write; live Fluent restored to the setup-07c saved ramp-reset final and DPM read back off.
- Outputs: `../../../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md`, `09_tuesday_decision_summary.png`, processed figures `00-09`, raw accepted Fluent images, CSV and JSON manifests.
- Next action: use the package for the 2026-08-11 meeting, then qualify a resolved brine outlet on one medium mesh before restarting mesh convergence, DPM or EWF.

## Run Template
- Run ID:
- Date:
- Objective:
- Geometry:
- Mesh:
- Physics model:
- Solver settings:
- Boundary and initial conditions:
- Iteration budget:
- Convergence monitors:
- Outcome:
- Hypothesized cause (if non-converged):
- Next action:

## Runs

### Run SPLIT-07N-A-MESHSELECTED-RELAXATION-DT-SENSITIVITY-2026-08-23

- Run ID: `SPLIT-07N-A-MESHSELECTED-RELAXATION-DT-SENSITIVITY-2026-08-23`.
- Objective: extend the zero-feed, closed-brine, mesh-selected VOF pool over a
  meaningful physical interval, determine whether its physical monitors become
  stationary, and perform a matched `dt/2` check before any outlet opening.
- Fixed configuration: 620,431 cells / 16 ranks, explicit VOF, PISO, PRESTO,
  Geo-Reconstruct, WFGC, RNG `k-epsilon`, Energy off, zero inlet rates, brine
  wall, steam pressure outlet, DPM zero/off, EWF off and no sources/sinks.
- Lineage: the whole-cell pool contains `98,473` cells and
  `3877.468071 kg` liquid. Same-`dt` stages 3-8 extended the accepted lineage
  from step 340 to step 940 / `0.22271 s` at `dt=2.56e-4 s`.
- Interrupted evidence: stage-5 attempt 1 has 27 fully monitored steps through
  cumulative step 567; step 568 solved but post-solve monitoring was
  interrupted. Its manifest is `stopped_postsolve_monitoring`, its checkpoints
  remain ineligible, and it was not resumed. Stage-5 attempt 2 cold-loaded the
  verified step-540 pair and completed a new 100-step block.
- Step-940 result: continuity `3.67467e-4`, Courant `0.0125058`, average
  velocity `0.00357883 m/s`, vorticity `0.0331321 1/s`, maximum velocity
  `0.144127 m/s`, pressure `1.1199994-1.1329449 MPa`, exact inventory,
  brine-face liquid VF `1.0` and zero liquid steam-outlet flow. Last-20
  regressions were `-1.540%`, `-0.637%`, `-0.912%` and `+0.021%` for average
  velocity, vorticity, maximum velocity and Courant.
- Matched physical-time comparison: three branches cold-loaded the same
  step-940 pair and advanced `0.00512 s`. They used 20 x `2.56e-4 s`, 40 x
  `1.28e-4 s` and 80 x `6.4e-5 s`. All ended at `t=0.22783 s` and passed every
  hard gate.
- Matched endpoint differences, half step relative to base: average velocity
  `-0.906%`, vorticity `-0.941%`, maximum velocity `-7.332%`, brine-wall
  pressure `-2.7 Pa`, inventory/VOF/steam-seal `0`, and continuity `-35.62%`.
  Across 20 matched samples the mean absolute differences were `0.506%`,
  `0.526%` and `5.173%` for average velocity, vorticity and maximum velocity.
- Quarter-step discriminator: relative to the half-step endpoint, average
  velocity changed `-1.427%`, vorticity `-1.404%` and maximum velocity
  `-7.491%`. Across 40 matched samples, mean absolute differences were
  `0.817%`, `0.810%` and `5.935%`; maxima were `1.427%`, `1.404%` and `7.491%`.
  The endpoint case/data hashes are `32450dc8...f064` / `8535e5ab...0526`.
- Inner-iteration discriminator: a fourth branch repeated the 20-step baseline
  at fixed `dt=2.56e-4 s` with 100 rather than 20 inner iterations. It passed
  every hard gate and ended at the same step 960 / `t=0.22783 s`. Endpoint
  average velocity, vorticity and maximum velocity changed only
  `-0.00000853%`, `+0.00000607%` and `+0.00000703%`; maximum matched-sample
  differences were all below `0.000009%`. Continuity improved `99.70%` to
  `1.14616e-6`. Endpoint case/data hashes are `30eb872c...1434` /
  `e3bc04de...4778`.
- Velocity-maximum localization: zero-iteration attempt 4 fetched aligned
  native solution-variable arrays for every cell. All three matched endpoints
  have their maximum at cell index `382511`, centroid
  `(0.809789, 0.0420206, 0.651966) m`, with liquid VF
  `0.134811-0.134831`. Base/half and half/quarter top-20 velocity sets overlap
  by 18 and 16 cells, with 14 common to all three. The region is interfacial
  and repeatable, not a migrating single-cell artifact. Its turbulent
  viscosity is only `0.20-0.24%` of the domain maximum, excluding the known
  limiter cell as the cause. Attempts 1-2 remain preserved zero-step API-path
  diagnostics; neither changed or saved a field.
- Matched `dt/8` discriminator: 160 x `3.2e-5 s` cold-loaded the same step-940
  parent and ended at `t=0.22783 s`. All hard gates passed. Quarter-to-eighth
  endpoint changes were `-2.150%` average velocity, `-1.936%` vorticity and
  `-7.283%` maximum velocity. Across 80 matched samples, mean absolute
  differences were `1.284%`, `1.217%` and `6.092%`. Endpoint case/data hashes
  are `b9a7e269...67f79` / `4d8ba586...17c4f`.
- Warning: the turbulent-viscosity limiter remained confined to one of
  `620,431` cells and did not cause a hard-gate failure, but may relate to the
  local-extremum sensitivity.
- Outcome: `Diagnostic / unresolved`. Pressure, inventory, interface and steam
  seal remain bounded, but a second timestep halving did not contract either
  the bulk or maximum-velocity discrepancies. Do not claim time-step
  independence or open/control the brine outlet from any matched endpoint.
- Next action: explicit-VOF timestep halving is stopped. Run a zero-step
  implicit-VOF formulation/readback probe from the checksum-bound step-940
  parent; do not iterate until the supported discretization and complete
  settings contract are proved. No writer remains active.

### Run SPLIT-07L-HYDROSTATIC-REST-2026-08-21

- Run ID: `SPLIT-07L-HYDROSTATIC-REST-2026-08-21`; machine label
  `brine620k_07l_hydrostatic_rest_v1`.
- Objective: determine whether the resolved mesh and patched pool are unstable
  by themselves, or whether the 07j/07k failures require the open/forced brine
  boundary and incompatible startup pressure field.
- Controlled origin: accepted 07j time-zero lineage only; no failed physical
  step was loaded. Six inherited DPM injections were deleted, unsteady tracking
  and interaction were disabled, both inlet phase flows were set to zero,
  `brineoutlet` was temporarily made a wall, operating density was set to vapor
  density and the pressure reference was moved to `(0,1,0) m` in the gas.
- Fixed physics: 620,431-cell/16-rank mesh, transient explicit VOF, vapor
  primary/liquid secondary, RNG k-epsilon, gravity, Energy off, PISO, PRESTO,
  Geo-Reconstruct, WFGC and the same `y<=0 m` pool.
- Execution: fresh Hybrid Initialization and pool patch; separate t0 case/data;
  ten single-RPC `1e-6 s` steps with 20 inner iterations and separate case/data
  at every step. All five focused local tests passed before Fluent execution.
- Outcome: `Accepted bounded isolation diagnostic`. Final continuity
  `3.4698e-6`, domain velocity `4.8978e-7 m/s`, unchanged liquid inventory
  `3774.370486 kg`, maximum Global Courant `1.0095e-8`, zero unintended closed
  flux and no DPM/FPE/SIGSEGV evidence.
- Hydrostatic result: brine-wall pressure exceeded steam-outlet pressure by
  `2090.4 Pa`, within `4.86%` of the `2197.24 Pa` centroid estimate
  `rho_l g h`. Equal outlet pressure is therefore not a neutral lower boundary.
- Evidence-use label: valid for isolating bounded rest behavior and startup
  diagnosis; invalid for separator performance, outlet mass balance, mesh
  independence, DPM/EWF or plant validation.
- Next action: controlled zero-inlet brine pressure-outlet opening from the
  relaxed DPM-deleted lineage, using a physically supported downstream value
  or explicitly diagnostic bracket around the observed face pressure.

### Run SPLIT-07K-TRANSIENT-VOF-MASSFLOW-BRINE-2026-08-21

- Run ID: `SPLIT-07K-TRANSIENT-VOF-MASSFLOW-BRINE-2026-08-21`; machine label `brine620k_07k_transient_vof_massflow_brine_v1`.
- Objective: determine whether the resolved brine geometry and transient VOF field remain bounded when the known `116.92 kg/s` liquid feed has a strictly outward prescribed discharge route.
- Controlled origin: accepted clean 07j time-zero state, followed by brine boundary conversion, fresh Hybrid Initialization and the same `y<=0 m` pool patch.
- Only intended change from 07j: `brineoutlet` pressure outlet -> mass-flow outlet with phase-2 liquid `116.92 kg/s` and phase-1 vapor `0 kg/s`. Steam outlet remains `1.12 MPa` pressure outlet.
- Fixed controls: 620,431-cell mesh, 16 ranks, explicit VOF/Sharp/Geo-Reconstruct, WFGC, RNG k-epsilon, gravity, Energy off, `1e-4 s`, 20 inner iterations, EWF/sink off. Forensic correction: DPM interaction was off, but six inherited injections tracked `6,456` one-way parcels.
- Preparation: accepted with complete readback and separate non-overwriting time-zero case/data.
- Startup evidence: brine remained exactly `-116.92 kg/s`; steam mixture flow was `0`, `-80.3237`, `-83.5122 kg/s`; liquid VF remained near `0.158245`. However, by step 3 pressure and velocity had exploded to nonphysical magnitudes (`-4.1102e13 Pa` steam-outlet pressure, `5.2599e6 m/s` steam-outlet velocity and `7.2714e4 m/s` domain velocity).
- Terminal execution: the next one-step RPC produced no output and the guarded client stopped after its two-hour idle limit with code `124`. Step 4 is uncredited; only time-zero and step-1 case/data checkpoints exist. No controller remains.
- Outcome: `Diagnostic / terminal numerical failure`; do not resume. Prescribing the integrated liquid discharge did not cure the startup instability and does not validate the downstream plant boundary.

### Run SPLIT-07J-TRANSIENT-VOF-EQUAL-PRESSURE-2026-08-21

- Run ID: `SPLIT-07J-TRANSIENT-VOF-EQUAL-PRESSURE-2026-08-21`; machine label `brine620k_07j_transient_vof_equal_psep_v1`.
- Objective: test the source-free resolved outlet in physical time using the initial equal-`1.12 MPa` pressure bracket.
- Preparation: accepted from the clean mesh with 16 ranks, explicit VOF, Geo-Reconstruct, WFGC, fresh Hybrid Initialization, geometry-inferred pool and EWF/sink off. Forensic correction: DPM interaction was off, but six inherited injections tracked `6,456` one-way parcels.
- Terminal evidence: at step 2 (`0.0002 s`) brine liquid discharge was `-4692.8688 kg/s`, about 40.1 liquid feeds. Storage-aware liquid closure was `0.4601%`, so the gross drainage is model behavior rather than a flux-report inconsistency.
- Outcome: `Diagnostic / failed gross-drainage gate`; do not resume. Accepted time-zero and step-1 pairs are preserved.
- Next action: controlled setup 07k prescribed-flow boundary sensitivity; do not tune pressure without downstream evidence.

### Run SPLIT-07I-RESOLVED-BRINE-WFGC-2026-08-16

- Run ID: `SPLIT-07I-RESOLVED-BRINE-WFGC-2026-08-16`; machine label `brine620k_07i_pool_y0_equal_psep_wfgc_v1`.
- Objective: determine whether Fluent's recommended Warped-Face Gradient Correction materially changes the setup-07h failure while holding every physical input and initialization control fixed.
- Exact one-factor change: after authoritative settings import and before initialization, apply `/solve/set/warped-face-gradient-correction/enable yes yes`; require settings readback and cold-reload readback `enable=True`.
- Fixed origin: clean `brine-outlet-620kcells.msh.h5`, 620,431 cells/16 partitions, fresh Hybrid Initialization, phase-2 pool below `y=0 m`, steady Mixture/RNG k-epsilon/gravity/Energy-off, phase feeds `116.92/80.69 kg/s`, both outlets `1.12 MPa`, DPM/EWF/sink off.
- Early stop: preserve initialized/25/250 pairs; at iteration 250 reject brine liquid discharge above three feeds, mixture imbalance above 100% or liquid imbalance above 200%.
- Implementation verification: scripts compile and all 29 local unit/regression tests pass. The preparation now fails closed unless Fluent's parallel connectivity roster contains exactly node IDs `n0..n15` before any remote mutation.
- Attempt-8 preparation: Fluent loaded the clean 620,431-cell mesh, imported the authoritative settings, read WFGC back as `enable=true, mode=fast`, kept DPM/EWF/sink off, performed fresh Hybrid Initialization, patched the `y<=0 m` pool and saved a separate initialized case/data pair.
- Process-count correction: the roster actually lists nodes `n0..n15`, proving 16 solver processes. The `Core` denominator in entries such as `16/20` is the machine's 20 hardware cores, not the Fluent process count. The title bar independently states `16-processes`. Attempt-8 preparation is therefore valid controlled evidence.
- Qualification outcome: `0` complete blocks credited. The transcript contains 20 startup rows and continuity grew from `3.2024` at raw iteration 16 to `6.9888e14` at raw iteration 20. The GUI then records iteration 21, Node-4 SIGSEGV, connection reset and Fluent server shutdown. No divergent checkpoint was written and resumption is prohibited.
- Connection outcome: after the user restarted Fluent, a read-only check verified Fluent 2024 R2, `Status.SERVING`, and 16 solver processes on 20 hardware cores. No setup-07i controller remains active and no case is loaded.
- Outcome: `Diagnostic / catastrophic numerical failure`; this is a valid 16-process WFGC result showing that WFGC alone did not stabilize startup.
- Hypothesized cause: the explosive residuals remain consistent with the unresolved steady equal-pressure liquid-inventory/boundary formulation seen in setup 07h; the evidence does not isolate a lower-level SIGSEGV cause beyond the preceding numerical divergence.
- Next action: do not rerun the identical steady field. Move to setup 07j transient VOF with explicit liquid inventory and a defensible brine boundary.
- Classification: `Diagnostic / failed`; no convergence, boundary-validity or separator-performance conclusion.
- Setup report: `../../../Setup report/07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md`.

### Run SPLIT-07H-RESOLVED-BRINE-POOL-2026-08-15

- Run ID: `SPLIT-07H-RESOLVED-BRINE-POOL-2026-08-15`; machine label `brine620k_07h_pool_y0_equal_psep_v1`.
- Objective: determine whether the new physical brine outlet establishes correct liquid drainage when the lower vessel is initialized with a geometry-informed liquid reservoir.
- Geometry/mesh: unchanged clean `brine-outlet-620kcells.msh.h5`; SHA-256 `0d75a86e...9394`; 620,431 cells, 16 partitions, dedicated `0.19936247 m2` brine pressure face and no legacy bottom wall.
- Controlled difference from 07g: after fresh Hybrid Initialization, phase-2 liquid VF is patched to 1 below `y=0 m` and 0 above. The level follows the approximately `-0.254 m` brine-face centroid and `0.252 m` equivalent radius; it is inferred from geometry, not measured plant level.
- Physics/boundaries: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off, liquid/steam feed `116.92/80.69 kg/s`, steam/brine pressure outlets both `1.12 MPa`, minimum-phase-averaged operating density, DPM/EWF/sink off.
- Preparation: accepted from the clean mesh after a read-back hexahedral cell register patched phase-2 `mp=1` below `y=0 m`. Domain-average liquid VF changed `0 -> 0.15826588`; initialized validation errors were empty and a separate case/data pair was saved. Two failed pre-iteration automation attempts are retained separately.
- Iteration 25: intended directions passed; steam outlet `-80.376986 kg/s` vapor, brine outlet `-25.299896 kg/s` liquid and `-0.69597467 kg/s` vapor. The early state remained imbalanced and is diagnostic only.
- Terminal verified block: iteration 250 produced nonphysical brine liquid discharge `-3304.7817 kg/s`, mixture imbalance `1602.99%` and liquid imbalance `2726.53%`. The next block produced only 43 residual advances, ending at transcript row 292 with AMG pressure/k/VOF divergence and a floating-point exception; it is not credited.
- Preservation: initialized, iteration-25 and iteration-250 case/data pairs exist. The later failed state was originally saved as `interrupt_iter250` and is also preserved correctly as `post_fpe_residual_row292_unverified`; neither failed-state pair is accepted evidence.
- Classification: `Stopped diagnostic / unresolved at verified iteration 250`.
- Setup report: `../../../Setup report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md`.
- Status command: `../../../PyAnsys/scripts/connection/check_setup07h_status.py`.
- Decision: the steady initialized-pool branch failed numerically and physically. Move the same source-free geometry to a transient qualification with explicit physical-time inventory; brine pressure is not tuned without a defensible downstream value.

### Run SPLIT-07G-RESOLVED-BRINE-OUTLET-2026-08-13

- Run ID: `SPLIT-07G-RESOLVED-BRINE-OUTLET-2026-08-13`; machine label `brine620k_07g_pressure_equal_psep_v1`.
- Objective: qualify a physical brine-discharge route on one mesh before restarting mesh convergence, DPM or EWF.
- Geometry: new full separator mesh with dedicated brine pipe and `brineoutlet` pressure face; the closed-bottom `bottom` wall is absent.
- Mesh: `brine-outlet-620kcells.msh.h5`, SHA-256 `0d75a86e...9394`; 620,431 cells, 16 partitions, `27.06309 m3`, `h=0.03520151 m`, minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258`, no negative-volume error. Brine-outlet area is `0.19936247 m2`.
- Physics/model: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off, DPM/EWF off and no sink UDF.
- Boundary conditions: liquid/steam mass flow `116.92/80.69 kg/s`; steam outlet `1.12 MPa`; first brine pressure bracket also `1.12 MPa` with liquid-only backflow specification.
- Preparation: accepted. Raw hyphenated face names and the single fluid-zone name were explicitly normalized before settings import. Complete pre/post-initialization readback passed with fingerprint `223fd8d3...b30`; separate iteration-zero case/data saved.
- Execution: 3,000-iteration target with guarded 25/225 startup and 250-iteration blocks; checkpoints at 250/500/1000/2000/3000. Full residuals, both-outlet phase/mixture fluxes, pressure drops, outlet/domain velocity, vorticity and liquid inventory are recorded.
- Recovery: the first 25 iterations completed according to Fluent's residual transcript, but the PyFluent monitor stream returned zero points. The verified live state was saved separately at iteration 25; first-attempt evidence was preserved and a single controller resumed with transcript-based iteration proof.
- Second recovery: the resumed block reached and preserved iteration 250. Its metric pass rejected `phase-2-volume-fraction`; Fluent's allowed-values list requires `phase-2-vof`. The corrected/tested controller resumed from the verified iteration-250 pair and now records block completion before optional metric collection.
- Interim iteration 500: net steam/brine mixture flow is outward at `-38.76477/-37.179327 kg/s`, but brine phase routing is not yet physical: vapor `-42.680678 kg/s` out and liquid `+5.512239 kg/s` in. Mixture/liquid imbalance are `61.5687%/104.7145%`. Treat as early diagnostic only; the 500 checkpoint is preserved and execution continues.
- Terminal outcome: `Diagnostic / unresolved at verified iteration 500`. The next requested block produced only 62 of 250 residual rows and was not credited. The later live field reached overflow-scale values, so it is excluded; the iteration-500 case/data pair remains the terminal verified evidence. No boundary acceptance, mesh-independence or separator-efficiency claim is permitted.
- Setup report: `../../../Setup report/07g-split-inlet-resolved-brine-outlet-qualification.md`.
- Output root: `../../../PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/`.
- Status command: `../../../PyAnsys/scripts/connection/check_setup07g_status.py`.

### Run SPLIT-07F-SINK-THICKNESS-RATE-MATRIX-2026-08-11

- Run ID: `SPLIT-07F-SINK-THICKNESS-RATE-MATRIX-2026-08-11`; study ID `split_inlet_sink_thickness_rate_matrix_20260811`; launched 2026-08-11 NZST.
- Objective: test whether the local-supply limit demonstrated by setups 07d/07e moves with a taller active band, then isolate the additional effect of a faster fixed liquid-sink coefficient.
- Geometry: unchanged setup-07 spiral/split-inlet separator; `bottom` remains stationary wall zone `50059`; no brine pipe or outlet face is added.
- Mesh: clean-origin `mesh-900k.msh`; 5,335,623 tetrahedral cells, 923,066 nodes, `22.65842 m3`, characteristic size `0.01619378 m`, minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, 16 partitions and no negative-volume mesh-check error.
- Physics model: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off; phase-2 mass and carried mixture-momentum sources only; DPM/EWF off.
- Solver settings: authoritative setup-07 settings/fingerprint, SIMPLE/PRESTO and inherited discretization/URFs; every case restores the verified source-hooked clean preparation, changes only runtime thickness/tau, reads them back and performs fresh Hybrid Initialization.
- Boundary and initial conditions: liquid/vapor inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, bottom no-slip wall; no saved accumulated solution data loaded.
- Matrix: `(0.2803305072 m, tau=0.020 s)`, `(0.2803305072 m, tau=0.005 s)` and `(0.4204957609 m, tau=0.005 s)`. This permits thickness comparison at fixed rate and rate comparison at fixed doubled thickness.
- First-case preflight: readback matched requested `0.28033050723644937 m` and `0.02 s`; complete band contains `184,145` cells and `0.88704756 m3` from approximately `y=-6.43746` to `-6.16067 m`; separate fresh-Hybrid ramp-zero case/data saved.
- Scheduling correction: the first `v1` startup was interrupted after 79
  startup iterations when its inherited Adjust hook was observed rebuilding
  the fixed full-domain mask every iteration at roughly `8-11 min/iteration`.
  The attempt remains preserved and is not a result case. Clearing only that
  hook and executing the mask builder when thickness/tau/ramp changes produced
  a `6.17 s` live smoke iteration with all RP controls unchanged and DPM off.
  The `v2_staticmask` first case then recorded `2,500` cumulative / `1,500`
  full-strength iterations before a 250-iteration gRPC request timed out.
  Fluent stayed healthy; the separately preserved endpoint had sink
  `44.199736 kg/s`, pressure drop `25.1905 kPa`, continuity about `0.20` and no
  accepted stability window. This is diagnostic interruption evidence, not a
  terminal physical result.
- Recovery: the complete formal matrix restarted from the clean origin under
  non-overwriting `v3_rpc25` labels. Ramp and full-strength requests are now
  bounded to 25 iterations; no partial `v2` field is reused.
- Interim result/recovery: case 1 completed `3,000/2,000` cumulative/full-
  strength iterations with sink `53.133696 kg/s`, pressure `26.7892 kPa`,
  inventory `64.64961 kg`, liquid imbalance `54.5553%` and zero accepted
  windows. Case 2 recorded `2,375/1,375` before its controller stopped
  advancing while Fluent stayed healthy. Its current field was preserved with
  an unverified label. A sandboxed liveness probe then misread permission
  denial as process absence, permitting overlapping `v4` preflights; an
  escalated process audit detected and terminated all duplicate/stalled trees.
  No `v4` production iteration ran, and the fingerprint mismatch was correctly
  rejected. Cases 2 and 3 now restart clean as `v5_single_controller`; the
  completed case 1 is retained and skipped.
- Current execution state: `Paused after v6 preflight failure`. V5 passed full
  clean parity/mask preflight and saved its ramp-zero checkpoint, but was
  stopped before production when a busy Fluent health probe was misinterpreted
  as unavailability. V6 connected and restored the parent, then Fluent returned
  empty captured text for mesh size/check/quality reports. Mandatory parsing
  failed before initialization or iteration. No controller remains active; a
  clean/repaired Fluent session is required.
- Iteration budget: per case, guarded 1,000-iteration ramp plus 1,000 minimum and 2,000 maximum full-strength iterations in 25-iteration RPC blocks; two consecutive passing 500-iteration windows required for early stop.
- Convergence monitors: integrated sink, corrected phase-2 and source-inclusive mixture balance, domain/band liquid inventory, pressure drop, steam-outlet phase flows, outlet/domain velocity, vorticity and all scaled residual histories.
- Safety/preservation: stop for sink above `175 kg/s`, abrupt post-startup pressure change, non-finite fields, DPM activation or controller failure; queue stops rather than starting a new case from uncertain state; start/ramp/R1/final case-data, transcript, CSVs and manifests use new paths.
- Outcome: `Running diagnostic matrix`. No acceptance or validation conclusion is assigned before terminal histories are assessed.
- Hypothesized cause if non-converged: even a larger band may remain limited by where the steady Mixture field transports liquid, while a faster local coefficient can deplete the band without defining the missing outlet pressure-flow relation.
- Evidence-use label: diagnostic parameter sensitivity only; not a physical drain, efficiency, mesh-independence, free-surface or physical-time result.
- Setup report: `../../../Setup report/07f-split-inlet-sink-thickness-rate-matrix.md`.
- Output root: `../../../PyAnsys/output/split_inlet_sink_thickness_rate_matrix_20260811/`.
- Next action: supervise the queue, preserve each terminal checkpoint and compare the two-factor response before deciding whether any case deserves more iterations.

### Run SPLIT-07E-ADAPTIVE-MASS-BALANCE-SINK-2026-08-10

- Run ID: `SPLIT-07E-ADAPTIVE-MASS-BALANCE-SINK-2026-08-10`; machine label `mesh-900k_band0p140165_target116p92_v1`; launched 2026-08-10 NZST.
- Objective: separate the missing-liquid-closure problem from the remaining pressure, velocity and residual stability problem by commanding the existing qualified local sink toward the full `116.92 kg/s` liquid inlet.
- Controlled origin: verified source-hooked setup-07c prepared 900k checkpoint, exact fingerprint `c5294907...`, fresh Hybrid Initialization, same `92,058`-cell/`0.44378932 m3` band and DPM off.
- Feedback law: every 100 iterations, `tau_next = clamp(M_liquid,band/116.92, 0.002, 0.2) s`; the existing source law remains `S=-rho_l alpha_l R/tau`.
- Preserved physics/boundaries: steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off, SIMPLE/PRESTO, inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, bottom wall.
- Iteration contract: guarded 1,000-iteration ramp plus 1,000 minimum and 2,000 maximum full-strength iterations; feedback/monitor blocks of 100; separate start, ramp, R1 = 1,000, R1 = 2,000 and final ramp-zero checkpoints.
- Execution result: completed the guarded 1,000-iteration ramp and full 2,000
  full-strength budget (`3,000` cumulative iterations). The stop reason was
  `maximum iteration budget reached`; zero acceptance windows passed.
- Terminal endpoint: at bounded `tau=0.002 s`, the sink removed
  `50.954294 kg/s` (`43.6%` of command), leaving `56.419329%` corrected liquid
  imbalance and `33.1674%` source-inclusive mixture imbalance. Pressure
  drop/domain inventory were `26.7252 kPa`/`65.007547 kg`; the active band
  held only `0.101909 kg`, below the `0.23384 kg` needed to meet the command at
  the minimum tau.
- Terminal convergence evidence: continuity/liquid-VF residuals ended at
  `0.254617`/`7.53207e-4` and increased `3.634%`/`8.463%` over iterations
  2901-3000. Final-500 pressure, sink and domain-inventory drift were
  `5.8506%`, `26.1894%` and `13.3524%`; outlet/domain velocity drift were
  `3.3033%`/`6.9068%`. Vapor flow and vorticity alone passed their drift gates.
- Preservation and safety: start, ramp-complete, R1=1000, R1=2000 and final
  ramp-reset-zero case/data pairs are separately verified; DPM interaction was
  off and no injection update or tracking ran.
- Dry-band lineage: exact saved iterations 100, 200, 350, 500, 750 and 1000 match setup
  07d with `0.000000%` difference for every controlled comparison field.
- Outcome: `Completed Diagnostic / Unresolved`. The adaptive source remained
  limited by liquid inventory inside its arbitrary local band and did not
  establish mass closure, stable pressure/inventory or acceptable continuity.
- Evidence-use label: diagnostic numerical mass-balance control only. It is not a physical drain boundary and cannot validate outlet hydraulics, efficiency, mesh convergence, a free surface or physical-time accumulation.
- Setup report: `../../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`.
- Output root: `../../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/`.
- Status command: `../../../PyAnsys/scripts/connection/check_setup07e_mass_balance_control_status.py`.
- Result report: `../../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/QUALIFICATION_RESULT.md`.

### Run SPLIT-07D-CAPACITY-MATCHED-SINK-2026-08-10

- Run ID: `SPLIT-07D-CAPACITY-MATCHED-SINK-2026-08-10`; machine label `mesh-900k_band0p140165_tau0p020_v1`; launched 2026-08-10 NZST.
- Objective: determine whether the setup-07c failure was mainly insufficient local sink capacity by increasing source strength fivefold while changing no other carrier or geometry input.
- Rationale: setup 07c ended with `2.24882 kg` liquid in the band; `2.24882/116.92 = 0.01923 s`, so `tau=0.02 s` approximately capacity-matches the endpoint band inventory to the liquid feed.
- Controlled origin: clean original `mesh-900k.msh`, authoritative settings/fingerprint, fresh Hybrid Initialization and no saved accumulated solution data.
- Only intended change: `tau 0.1 -> 0.02 s`; retain the complete `0.1401652536 m` band, physics, boundaries, solver controls, ramp, acceptance gates and DPM-off state.
- Iteration contract: guarded 1,000-iteration ramp plus up to 2,000 full-strength iterations in 250-iteration blocks; separate start, smoke, ramp, 1,000-, 2,000- and final case/data.
- Safety: stop on source overshoot, non-finite primary fields, abrupt pressure change or two accepted stability windows; do not overwrite setup 07a/07b/07c evidence.
- Execution result: completed the guarded 1,000-iteration ramp and full 2,000-iteration R1 budget with separate non-overwriting checkpoints; final ramp reset to zero and DPM read back off.
- Endpoint: sink `46.9874 kg/s` (`40.19%` of liquid feed), corrected liquid imbalance `59.8122%`, source-inclusive mixture imbalance `35.1679%`, inventory `66.6560 kg`, pressure drop `26.8901 kPa`, vapor outlet `81.1272 kg/s` out, continuity `0.229682` and liquid-VF residual `7.3419e-4`.
- Final-500 stability: pressure `6.618%`, sink `23.044%`, inventory `14.120%`, outlet velocity `3.161%` and domain velocity `6.901%` failed; vapor outlet `0.140%` and vorticity `0.797%` passed. Zero acceptance windows passed.
- Outcome: `Completed Diagnostic / Unresolved`. A 5x coefficient produced only a 2.09x endpoint sink because the active-band inventory fell from `2.24882` to `0.93975 kg`; stronger local removal improved but did not close or stabilize the field.
- Evidence-use label: diagnostic sink-capacity sensitivity only. It cannot validate the surrogate, efficiency, mesh convergence, a free surface or physical-time accumulation.
- Setup report: `../../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`.
- Output root: `../../../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/`.
- Result report: `../../../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/QUALIFICATION_RESULT.md`.
- Status command: `../../../PyAnsys/scripts/connection/check_setup07d_strong_sink_status.py`.

### Run SPLIT-07C-THICK-SINK-QUALIFICATION-2026-08-08

- Run ID: `SPLIT-07C-THICK-SINK-QUALIFICATION-2026-08-08`; machine label `mesh-900k_band0p140165_tau0p100_v1`; completed 2026-08-09 NZST.
- Objective: determine whether increasing the setup-07b bottom-local liquid-sink mask from one cell to a fixed 16-layer-equivalent band can establish a steady constant-water-level carrier solution without changing geometry or adding a brine outlet.
- Geometry: setup-07 spiral/split-inlet separator; `bottom` retained as stationary no-slip wall zone `50059`; `steamoutlet` remained the only pressure outlet.
- Mesh: clean original `mesh-900k.msh`, SHA-256 `353bf13c...afef`; 5,335,623 cells, 923,066 nodes, `22.65842 m3`, `h=0.01619378 m`, minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, no negative volumes, 16 partitions.
- Physics model: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off; phase-2 liquid mass and mixture carried-momentum sinks only; DPM off.
- Solver settings: authoritative `mesh_study_settings.set`, fingerprint `424a9bf0...c5`, SIMPLE/PRESTO and inherited discretization/URFs, fresh Hybrid Initialization; no saved accumulated solution data.
- Boundary and initial conditions: phase-2 liquid inlet `116.92 kg/s`, phase-1 vapor inlet `80.69 kg/s`, steam outlet `1.12 MPa` gauge; clean initialized field.
- Sink sensitivity: fixed `0.1401652536 m` band above the full planar bottom, 92,058 cells and `0.44378932 m3`, nominally 16 setup-07b one-cell layers; unchanged `tau=0.1 s`.
- Iteration budget: guarded 1,000-iteration ramp (`R=0.025/0.05/0.10/0.25/0.50/0.75`) then up to 2,000 full-strength iterations in 250-iteration blocks; two consecutive passing final-500 windows required for early acceptance.
- Convergence monitors: pressure drop, integrated sink, domain liquid inventory, vapor/liquid outlet flow, phase/mixture balance, outlet/domain velocity, vorticity and all scaled residual histories.
- Execution/recovery: the first controller false-stopped at R1 = 250 because a startup-change guard compared the first full-strength sample with the preceding ramp sample. The state was saved separately, counts reconciled and a recovery controller resumed to R1 = 2000 without overwriting evidence.
- Endpoint: sink `-22.4882 kg/s`; domain liquid inventory `71.7785 kg`; steam-outlet liquid/vapor `-0.000102861/-81.2960 kg/s`; corrected source-inclusive liquid imbalance `80.7661%`; source-inclusive mixture imbalance `47.4802%`; pressure drop `27.1372 kPa`; outlet/domain velocity `45.6588/30.7530 m/s`; vorticity `82.4945 s^-1`; continuity `0.191551`; liquid-VF residual `6.9815e-4`.
- Final-500 stability: pressure `8.53%`, sink `29.99%`, liquid inventory `16.93%`, outlet velocity `4.24%` and domain velocity `6.78%` failed; vapor outlet `0.0362%` and vorticity `0.860%` passed. The residual-level gate failed due to continuity.
- Outcome: `Completed Diagnostic / Unresolved at maximum iteration budget`. Zero acceptance windows passed. Thickening increased sink by about `13-16x` versus setup 07b at equal R1 counts but still removed only `19.23%` of liquid inflow and did not stabilize inventory or pressure.
- Accounting note: raw `liquid_source_augmented_*` values double-count the phase-2 sink. The corrected 07c liquid imbalance is `80.7661%`; setup 07b is corrected from `84.2956%` to `91.1909%`. Mixture source-augmented values remain valid. No acceptance decision changes.
- Saved outputs: separate ramp, false-stop, resume-start, R1 = 1000, R1 = 2000 and final ramp-reset-zero case/data; remote transcripts; local manifest, correction JSON, physical/mass-balance/residual CSVs and mesh-quality report.
- Hypothesized cause: the local inventory-proportional sink responds only to liquid occupying the selected band and does not prescribe the missing brine-outlet hydraulics or fixed global liquid inventory.
- Next action: retain 07c as diagnostic sensitivity only; qualify a resolved brine outlet on one medium mesh before any new mesh ladder, DPM or EWF run.
- Output root: `../../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/`.
- Result report: `../../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/QUALIFICATION_RESULT.md`.

### Run SPLIT-07B-TAU010-QUALIFICATION-2026-08-07
- Run ID: `SPLIT-07B-TAU010-QUALIFICATION-2026-08-07` / machine label `mesh-900k_tau0p100_qualification_v1`; completed 2026-08-08 NZST.
- Objective: determine whether the constant-level sink can produce an iteration-independent, source-balanced steady carrier solution at `tau=0.1 s` before testing tau sensitivity.
- Start state: accepted clean original 900k reconstruction with fresh Hybrid Initialization and ramp zero; setup-07a accumulated data explicitly not loaded.
- Controls: `R=0.05` for 100, `0.10` for 100, `0.25` for 150, `0.50` for 150, then `R=1` in 250-iteration blocks; 2,500 minimum and 6,000 maximum full-strength iterations.
- Acceptance: two consecutive passing final-500 windows; source-inclusive liquid/mixture imbalance `<=0.5%`; pressure, sink, liquid-inventory and vapor-outlet drift `<=0.5%`; velocity/vorticity drift `<=1%`; non-growing residuals with final values `<=1e-3`.
- Outputs: separate start, ramp-complete, full-strength 1,000-iteration and final/failure case/data; transcript; residual, physical-monitor and mass-balance CSVs; continuously updated JSON manifest.
- Geometry: setup-07 spiral/split-inlet domain; `bottom` remained wall zone `50059`; the sink mask covered the complete one-cell-thick bottom-adjacent layer (`5,438` cells, `0.027726243 m3`).
- Mesh: clean original 900k mesh; `5,335,623` tetrahedral cells, `923,066` nodes, `22.65842 m3` domain volume, minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, 16 partitions.
- Physics model: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off; phase-2 liquid mass sink and carried mixture-momentum sinks only; DPM off.
- Solver settings: inherited setup-07a SIMPLE/PRESTO and discretization/URFs; fresh Hybrid Initialization; full-strength calculation issued and evaluated in 250-iteration blocks.
- Boundary and initial conditions: liquid/vapor inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`; clean initialized field with no saved setup-07a solution loaded.
- Iteration result: completed `500` ramp iterations plus the full `6,000`-iteration `R=1` limit (`6,500` total solver iterations). A controller disconnect in the R1 `2750-3000` block was recovered from a separately saved live field and reconciled; no existing checkpoint was overwritten.
- Endpoint: pressure drop `34.8475 kPa`; sink `-8.06194 kg/s`; domain liquid inventory `191.836 kg`; steam-outlet liquid/vapor `-2.23770/-81.3862 kg/s`; corrected source-inclusive liquid imbalance `91.1909%`; outlet/domain velocity `48.8051/34.6175 m/s`; domain vorticity `86.2906 s^-1`; continuity `0.279243`; liquid-volume-fraction residual `1.8933e-3`.
- Final-500 stability: pressure `2.60%`, sink `17.89%`, liquid inventory `10.07%`, domain velocity `1.76%` and vorticity `1.42%` all failed their limits. Vapor outlet `0.0357%` and outlet velocity `0.269%` passed. The residual-level gate failed and the `k` residual trend was growing.
- Outcome: `Completed Diagnostic / Unresolved at maximum iteration budget`. Zero acceptance windows passed. The sink remained far below the liquid inlet and inventory continued increasing, so `tau=0.1 s` and the one-cell formulation are not physically qualified.
- Saved evidence: verified non-overwriting R1 checkpoints at 1,000, 2,000, 3,000, 4,000, 5,000 and 6,000. The formal endpoint is `r1_iter6000_cumulative6500.cas.h5/.dat.h5`; the separately saved ramp-reset-zero final is `max_r1_6000_unresolved_ramp_reset0.cas.h5/.dat.h5`.
- Hypothesized cause: the local inventory-proportional one-cell sink does not impose the required brine discharge; liquid reaching the sink layer is removed, but most inlet liquid remains in or redistributes through the domain.
- Next action: define and qualify a resolved brine-outlet geometry on one medium mesh. Any additional tau/layer test is diagnostic sensitivity only; do not resume mesh convergence, DPM or EWF from this unresolved field.
- Output root: `../../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/mesh-900k_tau0p100_qualification_v1/`.
- Result report: `../../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/mesh-900k_tau0p100_qualification_v1/QUALIFICATION_RESULT.md`.

### Run SPLIT-07B-UDF-IMPLEMENTATION-2026-08-07
- Run ID: `SPLIT-07B-UDF-IMPLEMENTATION-2026-08-07`.
- Date: 2026-08-07.
- Objective: implement and prove a constant-water-level liquid-only sink on the setup-07 split-inlet carrier model without adding a physical brine outlet, DPM or EWF.
- Geometry: setup-07 spiral/split-inlet domain; `bottom` retained as wall and interpreted by the project as the assumed water-level cutoff.
- Mesh: implementation/smoke proof on `mesh-900k`, actual `5,335,623` cells, `h=0.01619378 m`, minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, 16 partitions.
- Physics model: unchanged steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off. Added phase-2 liquid mass source and mixture x/y/z carried-momentum sources only.
- Source law: bottom-adjacent cells use `S_l=-rho_l alpha_l R/tau`; mixture momentum uses `S_liquid*u_mixture`. Five UDMs store the mask and source fields.
- Boundary and operating conditions: liquid/vapor inlet `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, `bottom` wall zone ID `50059`; no vapor source, no energy source, DPM interaction off.
- Implementation workflow: protected checkpoint, content-hashed remote source deployment, built-in Clang compile, positive UDM-reservation requirement, atomic Fluent 2024 R2 source-list assignment, complete setting/source readback, separate checkpointing and cold-reload verification.
- Iteration budget: zero iterations for the ramp-zero hook save; one diagnostic iteration for execution proof.
- Smoke result: residual history advanced `6000 -> 6001`; 5,438 cells and `0.027726243 m3` were marked; marked liquid inventory was `0.959465 kg`; source integral was `-0.47973263 kg/s` at `R=0.05`, `tau=0.1 s`; ramp reset to zero.
- Outcome: `Implementation Accepted / Physical Qualification Unresolved`.
- Evidence-use label: valid for code compilation, UDM persistence, hook scoping, source sign/magnitude and checkpoint safety. Not valid for steady carrier convergence, tau selection, mass closure, separator performance, mesh convergence, DPM or EWF.
- Failure history: r1-r3 were safely rolled back; r3 is explicitly nonfunctional because its load transcript showed missing UDM reservation. Smoke v1 is superseded because the wrapper misread a per-command iteration control; smoke v2 is accepted.
- Clean-start rule: the actual qualification run must load `C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh`, apply `mesh_study_settings.set`, verify the setup fingerprint, hook at ramp zero and fresh Hybrid Initialize. It must not load the setup-07a 6000-iteration data as initial solution.
- Clean-start result: `Accepted clean-origin initialized start state`. Preparation v3 verified original mesh SHA-256 `353bf13ca13d4a32a4cd505d991e64b1ea6f306cc3e8add438859b9117a5afef`, normalized full-settings fingerprint `424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5`, fresh Hybrid Initialization, exact cold-reload source hooks, ramp zero, DPM off, no saved solution data loaded and zero production iterations.
- Prepared checkpoint: `C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\clean_900k_preparation\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.cas.h5/.dat.h5`.
- Outputs: `../../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/` and `../../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`.
- Next action: run the prepared clean-original-mesh 900k qualification with gradual ramping, source/inventory monitors and `tau` sensitivity before deciding whether to retain the abstraction or model a resolved brine outlet.

### Run PURNANTO-ENTHALPY-DPM-SWEEP-2026-07
- Run ID: `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`
- Date: 2026-07-21 to 2026-07-24; evidence re-audited 2026-07-29.
- Objective: reproduce the six Purnanto paper-table enthalpy conditions using the current one-inlet Fluent baseline, 1500 carrier-flow iterations per condition, and nine Harwell-derived DPM injections for outlet steam-quality prediction.
- Geometry: `baseline.cas.h5`; a Purnanto baseline / Bangma-target operating reconstruction. Exact paper geometry identity remains unconfirmed.
- Mesh: loaded baseline reports approximately 5.58 million cells, 1.03 million nodes, and 11.36 million faces during case writes (`Observed`). Mesh quality statistics have not yet been added to this run record.
- Physics model: inherited steady pressure-based Mixture carrier field, primary vapor and secondary liquid, RNG k-epsilon, gravity enabled, energy off; DPM after the carrier solve. The historical manifests did not preserve a direct one-way interaction readback.
- Solver settings: fresh base-case load and Hybrid Initialization per paper condition; inherited early convergence stops disabled; iterations issued in verified chunks; residual x-axis used as completion evidence.
- Boundary and initial conditions: one phase-specific mass-flow inlet using the six paper-table steam/liquid splits; pressure outlet inherited from baseline; nine face-normal surface injections on `inlet` using CSV diameters, mass allocation, and speed; DPM material `water-liquid-dpm`.
- Iteration budget: 1500 carrier-flow iterations per case, followed by DPM tracking; checkpoints and separate pre-DPM/post-DPM saves enabled.
- Convergence monitors: Cases 2-6 preserve residual CSVs through iteration 1500, with final continuity residuals approximately `0.342`, `0.343`, `0.223`, `0.193`, and `0.206`. Case 1 has manifest evidence for block-by-block advancement through 1500 but no mirrored standalone residual CSV; its final continuity residual was recorded at approximately `0.283`. Iteration completion is evidenced, residual convergence is not.
- Outcome: `Completed / Scientifically Provisional`. All six flow solves, DPM tracks, case/data saves, 54 injection rows, and per-injection fate-mass checks completed.
- Results: escaped liquid is `0.1367`, `0.213559`, `0.196699`, `0.1817`, `0.1648`, and `0.1443 kg/s`; provisional steam quality is `99.7746%`, `99.6718%`, `99.7304%`, `99.7753%`, `99.8144%`, and `99.8507%` for Cases 1-6.
- Evidence-use label: valid for automation/readback, DPM fate accounting, and provisional comparison. Not valid as converged paper replication because carrier residuals remain high, inherited DPM controls are incompletely preserved, and exact geometry/convention parity is unresolved.
- Hypothesized cause if trends disagree with Purnanto: carrier field not converged, geometry mismatch, inferred nine-bin mass allocation, face-normal injection interpretation, tracking-control sensitivity, or high incomplete-particle fraction.
- Next action: freeze this run as provisional evidence, then run a controlled convergence extension and capture the full inherited DPM state before using the quality values as validation evidence.
- Mid-year technical-report evidence brief: `../technical/purnanto-enthalpy-dpm-replication.md`.

### Run PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07
- Run ID: `PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07`
- Date: 2026-07-25 to 2026-07-28; evidence re-audited 2026-07-29.
- Objective: apply the same six Purnanto enthalpy conditions and nine-bin DPM method to the available spiral-inlet separator baseline.
- Geometry: `baseline_spiral_inlet.cas.h5`; its exact lineage to the documented v2 spiral CAD/mesh remains unconfirmed.
- Mesh: inherited spiral baseline; exact mesh-quality and identity evidence must be captured in a future case audit.
- Physics model: inherited steady pressure-based Mixture carrier field with vapor primary and liquid secondary phases, RNG k-epsilon, gravity enabled, energy off, and one-way DPM confirmed in the inspected baseline.
- Solver settings: fresh baseline load, case-specific phase flows and injections, Hybrid Initialization, 1500 carrier iterations, then DPM update/reporting and post-DPM save.
- Boundary and initial conditions: one mixed mass-flow inlet; Purnanto paper gas/liquid splits; nine positive-magnitude Normal to Face surface injections using `spiral_harwell_results.csv`; inert `liquid-water` particles.
- Iteration budget: 1500 carrier-flow iterations per case followed by DPM tracking.
- Convergence monitors: all six residual CSVs span iterations 1-1500. Final continuity residuals are approximately `0.185`, `0.229`, `0.204`, `0.200`, `0.162`, and `0.145`; completion is verified, convergence is not.
- Outcome: `Completed / Scientifically Provisional`. All six case/data pairs, DPM reports, residual histories, 54 injection rows, and per-injection fate-mass checks completed.
- Results: escaped liquid is `0.01941`, `0.02088`, `0.02416`, `0.01655`, `0.01896`, and `0.02667 kg/s`; provisional steam quality is `99.9679%`, `99.9678%`, `99.9668%`, `99.9795%`, `99.9786%`, and `99.9724%`.
- Evidence-use label: valid for controlled branch comparison and provisional DPM fate accounting. Not a pure geometry sensitivity because inlet area, Harwell diameter, and injection speed also differ.
- Hypothesized cause if trends disagree with Purnanto: non-converged carrier flow, unconfirmed geometry/mesh lineage, changed inlet and droplet scaling, or inherited DPM controls not captured by the historical manifests.
- Next action: preserve the completed branch, capture full DPM/mesh readbacks, and compare only after the baseline convergence and methodology uncertainties are resolved.
- Technical-report evidence brief: `../technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md`.

### Run MESH-TRIAL1-SPLIT-CONTRACT-AUDIT-2026-06-10
- Run ID: `MESH-TRIAL1-SPLIT-CONTRACT-AUDIT-2026-06-10`
- Date: 2026-06-10
- Objective: re-audit the overwritten `mesh-trial1` baseline after adding separate `liquid-inlet` and `steam-inlet` named selections, then check whether the exported Fluent mesh preserves the exact required split-inlet zone contract.
- Geometry: current spiral-inlet separator meshing branch; geometry unchanged.
- Mesh: reopened exported baseline `mesh-trial1.msh` with `255,163` nodes, `2,915,260` faces, and `1,444,529` cells.
- Physics model: not a solve run; mesh reopen and quality audit only.
- Solver settings: not applicable; PyFluent meshing-mode reopen plus mesh-statistics extraction.
- Boundary and initial conditions: not applicable; audit checks only the exported Fluent mesh zone inventory and quality metrics.
- Iteration budget: none.
- Convergence monitors: not applicable.
- Outcome: `Contract Failed / Audit Completed`.
- Key audit result: Fluent reopened the mesh cleanly and detected `bottom`, `liquidinlet`, `outlet`, `steaminlet`, and `wall` as boundary zones plus `smooth_spiral_separator` as the fluid cell zone. The strict required-zone contract failed because the exported mesh did not preserve the exact names `liquid-inlet`, `steam-inlet`, and `wall-smooth_spiral_separator`.
- Mesh quality summary: minimum orthogonal quality approximately `0.03168`; maximum equivolume skewness approximately `0.96832`; bad-cell fraction approximately `2.56e-05` at threshold `0.15`, `3.46e-06` at threshold `0.10`, and `6.92e-07` at threshold `0.05`.
- Evidence-use label: valid for mesh-audit workflow decisions only; not a solver-performance result.
- Hypothesized cause (if non-converged): not applicable. Current blocker is export/name preservation rather than solver convergence.
- Next action: fix the Meshing/export path so the Fluent-exported mesh preserves the exact split-inlet and wall-zone names, then rerun the same baseline audit before scoring conservative Workbench trial meshes.

### Run PURNANTO-H5-AUDIT-2026-06-09
- Run ID: `PURNANTO-H5-AUDIT-2026-06-09`
- Date: 2026-06-09
- Objective: Extract the local Fluent HDF5 case/data pair and turn the saved Purnanto setup into a portable reference rather than a paper-only reconstruction.
- Geometry: Purnanto baseline separator case as saved in `PyAnsys/data/4800-iterations-300412-1.cas.h5`; exact paper inlet variant still requires visual confirmation if geometry identity matters.
- Mesh: `2,964,593` cells, `572,556` nodes, `6,063,406` faces, minimum orthogonal quality `0.277635`, maximum aspect ratio `12.8899`.
- Physics model: steady pressure-based `Mixture`; `phase-1 = water-vapor-at-psep`; `phase-2 = water-liquid-at-psep`; `RNG k-epsilon`; energy off.
- Solver settings: `SIMPLE`, Green-Gauss Node Based gradient, `PRESTO!` pressure, second-order momentum/k/epsilon, `QUICK` volume fraction, gravity `(0, -9.81, 0) m/s2`, operating pressure `0 Pa`, hybrid initialization state present in the case.
- Boundary and initial conditions: mass-flow inlet with vapor `80.69 kg/s`, liquid `116.92 kg/s`, inlet pressure field `1,140,000 Pa`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`; pressure outlet at `1,120,000 Pa`; wall zones stationary no-slip; bottom wall present; DPM injections inactive in the saved case.
- Iteration budget: `5000` saved iterations in the paired data file.
- Convergence monitors: residual criteria continuity `1e-4`; velocity, `k`, `epsilon`, and volume fraction `1e-3`; residual histories themselves still need a separate export if report-level confirmation is required.
- Outcome: `Audited / Extracted`.
- Hypothesized cause (if non-converged): not applicable; this is a setup audit, not a solve failure.
- Next action: use the new live setup reference page to retire paper-only assumptions and keep future Purnanto setup notes anchored to the extracted case.

### Run PYFLUENT-TRIAL4-500-2026-06-09
- Run ID: `PYFLUENT-TRIAL4-500-2026-06-09`
- Date: 2026-06-09
- Objective: extend the current hardened one-inlet PyFluent setup into a controlled `500`-iteration diagnostic on `trial4.msh` without changing the working setup core, so the branch can be checked for longer-run stability and phase-flow behavior.
- Geometry: current project spiral-inlet BOC separator geometry exported as `trial4.msh`, with one inlet, one outlet, walls including `bottom`, and no active liquid drain / sink branch in this diagnostic.
- Mesh: `trial4.msh` loaded successfully; Fluent read approximately `983,001` tetrahedral cells with inlet `inlet`, outlet `outlet`, and wall zones including `bottom` and `wall`.
- Physics model: steady pressure-based `Mixture` model with two phases; phase-1 assigned manual water vapor, phase-2 assigned manual liquid water; `RNG k-epsilon`; energy off; gravity on; one-steam-outlet interpretation retained.
- Solver settings: same hardened baseline stack as the shorter `trial4` run: `Operating Pressure = 0 Pa`, gravity `(0, -9.81, 0)`, `SIMPLE`, Green-Gauss Node Based gradient, `PRESTO!`, second-order momentum / `k` / `epsilon`, and `QUICK` for the multiphase discretization path.
- Boundary and initial conditions: one inlet converted to `Mass-Flow Inlet` with vapor `80.69 kg/s`, liquid `116.92 kg/s`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`, and pressure-related value `1,140,000 Pa`; one `Pressure Outlet` at `1,120,000 Pa`; bottom treated as wall; no active brine outlet branch.
- Iteration budget: hybrid initialization plus `500` steady iterations, executed in chunks of `50` with checkpoint interval `250`.
- Convergence monitors: the script printed raw mixture / phase-1 / phase-2 mass flows plus interpreted vapor-recovery and liquid-carryover summaries every `50` iterations. A rough residual-history plot was later recovered from the Fluent transcript.
- Outcome: `Controlled Diagnostic Completed`.
- Residual trend: residuals dropped substantially from the start of the run; by iteration `500`, continuity was approximately `3.3731e-01`, `x` velocity `3.2375e-04`, `y` velocity `3.3763e-04`, `z` velocity `3.1935e-04`, `k` `2.1085e-03`, `epsilon` `3.8826e-03`, and `vf-phase-2` `2.2265e-03`.
- Final interpreted phase-flow result: phase-1 inlet `80.69 kg/s`, phase-1 outlet `-81.43119629260137 kg/s`, phase-2 inlet `116.92 kg/s`, phase-2 outlet `-4.640062523254778e-23 kg/s`, vapor recovery ratio `1.009186`, and liquid carryover ratio `3.968579e-25`.
- Interpretation rule: because this branch has only a steam outlet, the nonzero total mixture imbalance should not be treated as a failure. The key check is that vapor outlet flow stays close to vapor inlet flow while liquid outlet flow through the steam outlet remains near zero.
- Output files: final case/data were written as `trial4-purnanto-recon-500.cas.h5` and `trial4-purnanto-recon-500.dat.h5`; checkpoint case/data were written at iteration `250`; rough residual artifacts were saved as `trial4-purnanto-recon-500-residuals.png` and `trial4-purnanto-recon-500-residuals.csv`.
- Evidence-use label: valid as a controlled longer one-inlet diagnostic and as a stronger local stability/phase-flow check than the short smoke test; not valid as convergence proof, validation evidence, separator efficiency evidence, or paper parity proof.
- Hypothesized cause (if non-converged): the remaining uncertainty is more about outlet-setting cleanup and residual-export tooling than about basic setup stability on this branch.
- Next action: keep this `500`-iteration run as the current local longer-diagnostic baseline, then clean up pressure-outlet setting inactivity and direct residual export if possible.

### Run PYFLUENT-TRIAL4-HARDENED-2026-06-09
- Run ID: `PYFLUENT-TRIAL4-HARDENED-2026-06-09`
- Date: 2026-06-09
- Objective: harden the local one-inlet PyFluent reconstruction script without changing its working core, using `trial4.msh` to confirm clean operating-pressure control, correct 2026 R1 numerics paths, flux sanity reporting, and case/data output.
- Geometry: current project spiral-inlet BOC separator geometry exported as `trial4.msh`, with one inlet, one outlet, walls including `bottom`, and no active brine-outlet branch in this parity pass.
- Mesh: `trial4.msh` loaded successfully; Fluent read approximately `983,001` tetrahedral cells with inlet `inlet`, outlet `outlet`, and wall zones including `bottom` and `wall`.
- Physics model: steady pressure-based `Mixture` model with two phases; phase-1 assigned manual water vapor, phase-2 assigned manual liquid water; `RNG k-epsilon`; energy off; gravity on.
- Solver settings: `Operating Pressure = 0 Pa` set cleanly through `setup.general.operating_conditions`; `SIMPLE` set through `solution.methods.p_v_coupling.flow_scheme`; gradient set through `solution.methods.spatial_discretization.gradient_scheme`; pressure/momentum/volume-fraction/`k`/`epsilon` schemes set through `solution.methods.spatial_discretization.discretization_scheme`.
- Boundary and initial conditions: one inlet converted to `Mass-Flow Inlet` with vapor `80.69 kg/s`, liquid `116.92 kg/s`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`, and pressure-related value `1,140,000 Pa`; one `Pressure Outlet` at `1,120,000 Pa`; bottom treated as wall; no brine outlet branch active.
- Iteration budget: hybrid initialization plus `10` steady iterations.
- Convergence monitors: at iteration `10`, residuals were approximately continuity `4.43e-01`, `x` velocity `1.17e-03`, `y` velocity `8.98e-04`, `z` velocity `1.06e-03`, `k` `3.77e-02`, `epsilon` `1.61e-01`, and `vf-phase-2` `5.64e-02`.
- Sanity report: mixture mass flow inlet `197.61`, outlet `-81.47756596537904`, net `116.13243403462097 kg/s`; phase-1 inlet `80.69`, outlet `-81.47756596537904`, net `-0.7875659653789882 kg/s`; phase-2 inlet `116.92`, outlet effectively `0`, net `116.92 kg/s`.
- Output files: `trial4-purnanto-recon.cas.h5` and `trial4-purnanto-recon.dat.h5` written successfully.
- Outcome: `Runnable Hardened Parity Pass Completed`.
- Evidence-use label: valid as local PyFluent hardening evidence and as the current best reproducible one-inlet parity workflow; not yet valid as a final baseline convergence or separator-performance run.
- Hypothesized cause (if non-converged): the main remaining ambiguity is pressure-outlet subsetting inactivity, not environment setup, operating-pressure control, or numerics-path discovery.
- Next action: test whether pressure-outlet subsetting order can be cleaned up and convert the raw flux printout into a more structured balance summary.

### Run PYFLUENT-TRIAL3-SMOKE-2026-06-09
- Run ID: `PYFLUENT-TRIAL3-SMOKE-2026-06-09`
- Date: 2026-06-09
- Objective: prove the current project can be rebuilt through local PyFluent from `trial3.msh` using the one-inlet Purnanto-style package, then hybrid-initialize and advance a short steady smoke test.
- Geometry: current project spiral-inlet BOC separator geometry exported as `trial3.msh`, with one inlet, one outlet, and wall boundaries including named `bottom`.
- Mesh: `trial3.msh` loaded successfully; Fluent read approximately `983,001` tetrahedral cells, one velocity-inlet zone, one pressure-outlet zone, and wall zones including `bottom` and `wall-part1`.
- Physics model: steady pressure-based `Mixture` model with two phases; phase-1 assigned manual water vapor, phase-2 assigned manual liquid water; `RNG k-epsilon`; energy off; gravity enabled through fallback.
- Solver settings: boundary conversion to one `Mass-Flow Inlet` succeeded; hybrid initialization succeeded; some intended numerics setters were not accepted through the first attempted PyFluent API paths, so this run is a smoke-test reconstruction rather than a full parity proof.
- Boundary and initial conditions: one inlet converted to `Mass-Flow Inlet` with vapor `80.69 kg/s`, liquid `116.92 kg/s`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`, and pressure-related value `1,140,000 Pa`; one `Pressure Outlet` at `1,120,000 Pa`; bottom treated as wall; no brine outlet branch active.
- Material definition: manual materials created in-session because the mesh-only case initially exposed only `air`. Final assigned values were vapor density `5.7974339 kg/m3`, vapor viscosity `1.52062e-05 kg/(m s)`, liquid density `881.21088 kg/m3`, and liquid viscosity `0.000145544 kg/(m s)`.
- Iteration budget: hybrid initialization plus `10` steady iterations.
- Convergence monitors: hybrid initialization completed; at iteration `10`, residuals were approximately continuity `4.98e-01`, `x` velocity `1.15e-03`, `y` velocity `9.23e-04`, `z` velocity `1.02e-03`, `k` `3.25e-02`, `epsilon` `1.63e-01`, and `vf-phase-2` `5.63e-02`.
- Outcome: `Runnable Smoke Test Completed`.
- Evidence-use label: valid as local PyFluent environment/setup evidence and as proof that the reconstructed one-inlet branch can initialize and iterate; not yet valid as a final baseline parity or separator-performance run.
- Hypothesized cause (if non-converged): remaining uncertainty is concentrated in the clean operating-pressure API path and the correct 2026 R1 solution-method setter paths rather than in the basic ability to build and run the case.
- Next action: fix the operating-pressure setter path, map the correct solution-method API tree, and add automatic phase mass-flow reporting before attempting a longer controlled run.

### Run PPMR-2026-06-09
- Run ID: `PPMR-2026-06-09`
- Date: 2026-06-09
- Objective: define the direct current-project rebuild branch for the Purnanto one-inlet mixed steam-water setup rather than continuing from the later split-inlet variants.
- Geometry: current project spiral-inlet BOC separator geometry, to be paired with one inlet boundary carrying both phases together.
- Mesh: use the current project mesh family for the rebuild branch; exact chosen mesh/case filename still to be recorded when the case is built.
- Physics model: steady pressure-based `Mixture` model with primary vapor and secondary liquid, `RNG k-epsilon`, gravity on, energy off.
- Solver settings: retain the live-audited Purnanto baseline stack: `SIMPLE`, Green-Gauss Node Based gradient, `PRESTO!`, second-order momentum / `k` / `epsilon`, `QUICK` volume fraction, and `Hybrid Initialization`.
- Boundary and initial conditions: one `Mass-Flow Inlet` with vapor `80.69 kg/s`, liquid `116.92 kg/s`, gauge/initial pressure field `1,140,000 Pa`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`; one `Pressure Outlet` at `1,120,000 Pa`; no split inlet zones in this branch.
- Iteration budget: not yet run; setup-definition stage only.
- Convergence monitors: when built, first check phase mass-flow reports, residual criteria parity, and gross mass balance before any performance interpretation.
- Outcome: `Setup Defined`.
- Evidence-use label: direct Purnanto-recreation branch definition only.
- Hypothesized cause (if non-converged): not yet applicable; the point of this branch is to remove the split-inlet change and return to the simpler paper-style one-inlet package.
- Next action: build the Fluent case from `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md` and verify the boundary/model stack before reviving any split-inlet comparison logic.

### Run PLS-STUDENT-OUTLET-EXT-2026-06-08
- Run ID: `PLS-STUDENT-OUTLET-EXT-2026-06-08` (`Assumed` setup label until the Fluent case filename is confirmed)
- Date: 2026-06-08
- Objective: Test whether moving the steam pressure-outlet boundary downstream of the central outlet-pipe entrance reduces outlet backflow reversal and stabilizes steam-outlet mass-flux reports.
- Geometry: child of `../../../Setup report/07-pure-phase-split-actual-area.md`; keeps Purnanto's rectangular 90-degree spiral-inlet BOC separator body and setup `07` pure liquid / pure steam split inlet, but extends the central steam outlet pipe/path so `steam_outlet` is placed at the downstream end of the extension.
- Mesh: pending student-edition rebuild; record nodes, cells, minimum orthogonal quality, maximum skewness, and outlet-extension local mesh quality before running.
- Physics model: inherit setup `07` steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off unless the rebuilt Fluent case forces a documented change.
- Solver settings: inherit setup `07` (`SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, setup `07` volume-fraction scheme, hybrid initialization) unless explicitly recorded as changed.
- Boundary and initial conditions: same setup `07` split inlet values: `inlet_liquid_outer` velocity inlet at `27.118 m/s`, liquid VF `1.0`, hydraulic diameter `0.01338 m`; `inlet_steam_inner` velocity inlet at `27.118 m/s`, liquid VF `0.0`, hydraulic diameter `0.72061 m`; `steam_outlet` pressure outlet moved to the end of the extended outlet path.
- Iteration budget: pending; choose after mesh count and student-edition runtime limit are known.
- Convergence monitors: residuals, inlet liquid/steam phase fluxes, steam-outlet phase fluxes, outlet-face backflow warnings, velocity vectors near the central outlet intake, velocity vectors inside the outlet extension, and liquid volume fraction near the outlet intake.
- Outcome: `Planned`.
- Evidence-use label: planned student-edition geometry diagnostic only. This branch can test boundary-placement sensitivity, but it is not final separator-performance evidence unless mesh quality, residual/monitor stability, and flux stability are documented.
- Hypothesized cause (if non-converged): `Inferred` pressure-outlet boundary placement at the immediate outlet-pipe entrance may expose the boundary to local swirling/recirculating flow, causing backflow reversal and unstable outlet mass-flux reporting.
- Next action: build the setup `08a` geometry from `../../../Setup report/08a-steam-outlet-extension-student-trial.md`, confirm the former outlet-pipe entrance is internal flow passage rather than a boundary face, then initialize and verify inlet fluxes before running.

### Run PURNANTO-LIVE-AUDIT-2026-06-05
- Run ID: `PURNANTO-LIVE-AUDIT-2026-06-05`
- Date: 2026-06-05
- Objective: Load and audit the live Fluent 2024 R2 Purnanto setup case/data pair for solver, mesh, boundary, model, and numerics parity against the reconstructed 2013 baseline.
- Geometry: Purnanto baseline separator case from `C:\Users\syok443\Documents\Fluent Standalone Test 1\purnanto case\purnanto-setup.cas.h5`; exact inlet-design variant still requires visual confirmation.
- Mesh: `2,964,593` tetra cells, `572,556` nodes, `6,063,406` faces, minimum orthogonal quality `0.277635`, maximum aspect ratio `12.8899`.
- Physics model: steady pressure-based `Mixture` multiphase model with `2` phases; `phase-1 = water-vapor-at-psep`, `phase-2 = water-liquid-at-psep`; `RNG k-epsilon`; energy off.
- Solver settings: `SIMPLE`, Green-Gauss Node Based gradient, `PRESTO!` pressure, second-order momentum/k/epsilon, `QUICK` volume fraction, operating pressure `0 Pa`, gravity `(0, -9.81, 0) m/s2`.
- Boundary and initial conditions: one mass-flow inlet with vapor `80.69 kg/s`, liquid `116.92 kg/s`, inlet pressure-related value `1,140,000 Pa`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`; one pressure outlet at `1,120,000 Pa`; bottom and vessel wall are stationary no-slip walls.
- Iteration budget: data file is `purnanto-setup-5000.dat.h5`; loaded data reports `number-of-iterations = 5000`.
- Convergence monitors: residual criteria are continuity `1e-4`; velocity, volume fraction, `k`, and `epsilon` `1e-3`; actual residual values were not extracted.
- Outcome: `Audited / Loaded`.
- Key quality flag: data load reported turbulent viscosity limited to viscosity ratio `1e5` in `34,302` cells.
- Evidence-use label: valid as a live setup parity audit and baseline reference; not yet valid as final separator-efficiency evidence or DPM efficiency evidence because active injections are absent and residual/mass-balance histories still need extraction.
- Hypothesized cause (if non-converged): not classified; the main current risk is localized turbulence-viscosity limiting and missing residual/mass-balance evidence rather than case-load failure.
- Next action: run phase mass-flow reports, locate turbulent-viscosity-limited cells, and visually confirm which Purnanto geometry variant this case represents before using it as a quantitative benchmark.

### Run PLS-PRO-2026-06-03-A
- Run ID: `PLS-PRO-2026-06-03-A` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-03
- Objective: Record the professional-license baseline flux result for `../../../Setup report/07-pure-phase-split-actual-area.md` before running quick DPM droplet-size efficiency checks.
- Geometry: spiral-inlet BOC separator with pure liquid / pure steam split inlet using the actual-area setup from `../../../Setup report/07-pure-phase-split-actual-area.md`.
- Mesh: `1.3M` nodes and `7.6M` cells (`User-reported`).
- Physics model: inferred continuation of the steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off unless the saved Fluent case shows otherwise.
- Solver settings: professional-license run; detailed residuals, discretization confirmation, and monitor history not yet captured in this log entry.
- Boundary and initial conditions: same nominal pure-phase split as setup `07`; liquid inlet target approximately `116.92 kg/s`, steam inlet target approximately `80.69 kg/s`.
- Iteration budget: not captured.
- Convergence monitors: phase flux report captured for `liquid inlet`, `steam inlet`, and `steam outlet`; bottom liquid handling is intentionally out of scope for this setup.
- Outcome: `Baseline Flux Diagnostic`.
- Key flux result: liquid phase `116.8522661860914 kg/s` at liquid inlet, `0.03663388722044243 kg/s` at steam outlet; steam phase `81.63946888251938 kg/s` at steam inlet, `-86.29342139251109 kg/s` at steam outlet.
- Calculated metrics: if the steam-outlet liquid value is interpreted as carryover magnitude, liquid carryover fraction is `0.03135 %`, implied liquid-removal efficiency is `99.96865 %`, and steam-outlet dryness is `99.95757 %`.
- Evidence-use label: professional-mesh steam-carryover diagnostic. The tiny steam-line liquid carryover is promising for the scoped project metric, but residual/monitor stability and DPM fate counts are still needed before report-quality efficiency evidence.
- DPM material update: DPM particle density was changed to `881.77 kg/m3` to match the water-droplet density used in setup `07`.
- DPM result set: `5 um` -> escaped `74`, trapped `63`, incomplete `63`; `1 um` -> escaped `23`, trapped `64`, incomplete `113`; `10 um` -> escaped `14`, trapped `53`, incomplete `133`; `41 um` -> escaped `0`, trapped `72`, incomplete `128`; `100 um` -> escaped `0`, trapped `86`, incomplete `114`.
- DPM interpretation: per the current project assumption, treat incomplete as effectively trapped for this branch. That gives scoped DPM removal efficiencies of `63.0 %` at `5 um`, `88.5 %` at `1 um`, `93.0 %` at `10 um`, and `100 %` at `41 um` and `100 um`.
- `5 um` sensitivity checks: deterministic `1000`-track run gave escaped `324`, trapped `325`, incomplete `351` (`67.6 %` scoped efficiency); DRW sensitivity gave escaped `288`, trapped `390`, incomplete `322` (`71.2 %`); rotation sensitivity gave escaped `347`, trapped `360`, incomplete `293` (`65.3 %`).
- `5 um` sensitivity interpretation: DRW and rotation still shift escape by only a few percentage points relative to the deterministic baseline and do not overturn the conclusion that fine droplets are only partially removed in this branch.
- Hypothesized cause (if non-converged): the main residual uncertainty is now whether the high incomplete counts truly correspond to wall-stuck particles and whether the updated water-density droplet surrogate is still sensitive to tracking controls, plus approximately `5.70 %` steam-phase imbalance between steam inlet and steam outlet magnitudes.
- Next action: record residual/monitor stability, then optionally increase DPM max steps to `100,000` and rerun at least the `10 um` case to see whether the `93.0 %` removal result holds with fewer incomplete tracks.

### Run PLS-STUDENT-ROUGH-2026-06-01-A
- Run ID: `PLS-STUDENT-ROUGH-2026-06-01-A` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-01
- Objective: Roughly check flux behavior for the pure liquid / pure steam actual-area split using a student-edition mesh and a `2 m` inlet extension before deciding which geometry direction looks more promising.
- Geometry: spiral-inlet BOC separator with pure liquid / pure steam split inlet sized from `../../../Setup report/07-pure-phase-split-actual-area.md`; both inlet legs appear extended upstream in the rough report.
- Mesh: `178k` nodes, `993k` cells, minimum orthogonal quality `0.194`.
- Physics model: inferred continuation of the steady `Mixture`-model separator setup; exact case file settings not fully captured in the report.
- Solver settings: not fully captured; residuals were reported as not converged enough for strong quantitative claims.
- Boundary and initial conditions: pure-phase split sized from the `1600 kJ/kg` actual-area basis; shared velocity `27.118 m/s`; liquid-side area `0.0048896 m2`; steam-side area `0.5192864 m2`.
- Iteration budget: not captured in the rough report.
- Convergence monitors: scaled residuals and phase flux report.
- Outcome: `Diagnostic Only`.
- Key flux result: steam inlet `80.6899 kg/s`, steam outlet `81.3067 kg/s`, liquid inlet `116.9264 kg/s`, liquid through steam outlet `10.6744 kg/s`.
- Calculated metrics: liquid carryover fraction `9.13 %`; implied carryover-based liquid-removal efficiency `90.87 %`; steam-outlet dryness `88.39 %`.
- Evidence-use label: rough student-edition diagnostic only; not valid for final separator efficiency or final setup ranking.
- Hypothesized cause (if non-converged): mesh cap, unresolved inlet behavior, and incomplete convergence likely distort the outlet split.
- Next action: compare against the modified rough geometry case and keep only the direction-of-change signal unless a higher-quality rerun confirms the trend.

### Run PLS-STUDENT-ROUGH-2026-06-01-B
- Run ID: `PLS-STUDENT-ROUGH-2026-06-01-B` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-01
- Objective: Roughly test whether changing the upstream extension arrangement improves the pure-phase split inlet behavior seen in the first student-edition diagnostic case.
- Geometry: spiral-inlet BOC separator with the same pure liquid / pure steam split sizing from `../../../Setup report/07-pure-phase-split-actual-area.md`; rough report notes that only the steam inlet kept the upstream extension while the liquid inlet was moved closer to the vessel.
- Mesh: `168k` nodes, `937k` cells, minimum orthogonal quality `0.194`.
- Physics model: inferred continuation of the steady `Mixture`-model separator setup; exact case file settings not fully captured in the report.
- Solver settings: rough report notes that the inlet condition was changed from velocity inlet to mass-flow inlet, making this a two-factor comparison rather than a clean one-factor control.
- Boundary and initial conditions: same nominal pure-phase mass split as the prior rough case, but with altered upstream geometry and reported inlet-type change.
- Iteration budget: not captured in the rough report.
- Convergence monitors: scaled residuals and phase flux report.
- Outcome: `Diagnostic Only`.
- Key flux result: steam inlet `80.6900 kg/s`, steam outlet `81.3802 kg/s`, liquid inlet `116.9200 kg/s`, liquid through steam outlet `7.7278 kg/s`.
- Calculated metrics: liquid carryover fraction `6.61 %`; implied carryover-based liquid-removal efficiency `93.39 %`; steam-outlet dryness `91.33 %`.
- Evidence-use label: rough student-edition diagnostic only; useful only as a qualitative comparison against `PLS-STUDENT-ROUGH-2026-06-01-A`.
- Hypothesized cause (if non-converged): the lower carryover trend may reflect the geometry change, the inlet-type change, or both.
- Next action: if this direction is pursued, rerun it as a controlled comparison with the same inlet boundary type as Setup 1 so the geometry effect can be isolated cleanly.

### Run PLS-ACTUAL-AREA-HD-2026-05-28
- Run ID: `PLS-ACTUAL-AREA-HD-2026-05-28` (`Assumed` setup label until Fluent filename is confirmed)
- Date: 2026-05-28
- Objective: Define the active pure liquid / pure steam split-inlet setup using current-area exact-mass velocity and phase-zone hydraulic diameters.
- Geometry: spiral-inlet BOC separator with rectangular `0.724 m x 0.724 m` inlet split into liquid-side width `0.006754 m` and steam-side width `0.717246 m`.
- Mesh: same current project mesh family unless superseded; key pre-run check is resolving the `6.754 mm` liquid strip.
- Physics model: steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherit from `../../../Setup report/04-mixed-wet-half-actual-area.md` unless separately changed.
- Boundary and initial conditions: `inlet_liquid_outer` velocity inlet at `27.118 m/s`, liquid VF `1.0`, turbulence intensity `2.10999999 %`, hydraulic diameter `0.01338 m`; `inlet_steam_inner` velocity inlet at `27.118 m/s`, liquid VF `0.0`, turbulence intensity `2.10999999 %`, hydraulic diameter `0.72061 m`.
- Iteration budget: pending Fluent run plan.
- Convergence monitors: residuals, inlet phase fluxes, outlet phase fluxes, liquid-volume-fraction contours, velocity vectors, and near-inlet turbulence quantities if available.
- Outcome: `Setup Defined`.
- Evidence-use label: setup definition only until Fluent run results are available.
- Hypothesized cause (if non-converged): likely risks are under-resolved liquid strip, sharp pure-phase inlet discontinuity, or turbulence-length-scale sensitivity from the small liquid-side hydraulic diameter.
- Next action: create the two named inlet faces, apply the report settings, initialize, and verify inlet fluxes before running long iterations.

### Run PTS-FV-2026-05-28
- Run ID: `PTS-FV-2026-05-28` (`Assumed` setup-calculation label; not a Fluent solve)
- Date: 2026-05-28
- Objective: Create a pure-liquid/pure-steam split-inlet setup that preserves Purnanto's reported spiral-inlet velocity `26.81 m/s` for the `1600 kJ/kg` case using the current `0.724 m x 0.724 m` inlet.
- Geometry: spiral-inlet BOC separator inlet face, treated as a rectangular `0.724 m x 0.724 m` face split along `x`.
- Mesh: not run; immediate mesh risk is resolving a `6.754 mm` liquid-side strip.
- Physics model: setup calculation for later steady pressure-based `Mixture` model run; primary phase steam/vapor, secondary phase liquid water.
- Solver settings: not run.
- Boundary and initial conditions: `inlet_liquid_outer` velocity inlet at `26.81 m/s`, liquid VF `1.0`; `inlet_steam_inner` velocity inlet at `26.81 m/s`, liquid VF `0.0`; liquid-side width `0.006754 m`; steam-side width `0.717246 m`.
- Iteration budget: not applicable.
- Convergence monitors: not applicable.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: valid for boundary setup. Expected inlet flows are liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`, which is `1.14 %` below Purnanto's `197.61 kg/s` target because the current inlet area is smaller than the area implied by `26.81 m/s`.
- Hypothesized cause (if non-converged): not applicable; main pre-run risks are wrong physical side mapping and under-resolved narrow liquid strip.
- Next action: create the two named inlet faces from `../../../Setup report/06-pure-phase-split-fixed-velocity.md`, then verify Fluent flux reports before interpreting outlet behavior.

### Run PTS-AREA-2026-05-28
- Run ID: `PTS-AREA-2026-05-28` (`Assumed` setup-calculation label; not a Fluent solve)
- Date: 2026-05-28
- Objective: Calculate the inlet split for a pure-liquid/pure-steam two-zone velocity inlet that preserves Purnanto's `1600 kJ/kg` phase mass-flow targets using the current `0.724 m x 0.724 m` inlet area.
- Geometry: spiral-inlet BOC separator inlet face, treated as a rectangular `0.724 m x 0.724 m` area for the split calculation.
- Mesh: not run; immediate mesh risk is whether a `6.754 mm` liquid-side strip can be resolved cleanly.
- Physics model: setup calculation for later steady pressure-based `Mixture` model run; primary phase steam/vapor, secondary phase liquid water.
- Solver settings: not run.
- Boundary and initial conditions: future pure liquid inlet uses liquid VF `1.0`; future pure steam inlet uses liquid VF `0.0`; shared velocity `27.118 m/s`; calculated liquid area `0.0048896 m2`, steam area `0.5192864 m2`, split line `0.006754 m` from the liquid-side edge if split along `x`.
- Iteration budget: not applicable.
- Convergence monitors: not applicable.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: valid for boundary-area setup; not valid as separator performance evidence until a Fluent run is completed.
- Hypothesized cause (if non-converged): not applicable; main pre-run risk is under-resolving the narrow liquid strip or mapping the liquid side to the wrong physical edge.
- Current decision: selected as the active next pure-phase split setup over the fixed-velocity `26.81 m/s` alternate.
- Next action: confirm the outer-wall liquid edge in CAD/meshing, create two named inlet zones with the calculated split, set both inlets to `27.118 m/s`, and verify inlet phase mass-flow reports before judging outlet behavior.

### Run CTP-NBO-2026-05-27
- Run ID: `CTP-NBO-2026-05-27` (`Assumed` setup label until Fluent filename is confirmed)
- Date: 2026-05-27
- Objective: Prepare a complete two-phase full-inlet spiral case with no active brine outlet for a `5000`-iteration diagnostic run.
- Geometry: spiral-inlet BOC separator with one full inlet boundary; brine outlet absent or closed as a wall for this branch.
- Mesh: same current project mesh family unless a new no-brine-outlet mesh export supersedes it; approximately 1.8M nodes from prior user-reported mesh scale remains the working assumption.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from the mixed wet-half actual-area setup where applicable: `SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, higher-order volume-fraction scheme where available, and hybrid initialization.
- Boundary and initial conditions: one full `Velocity Inlet` at `26.81 m/s`, liquid water volume fraction `0.009328`, steam/vapor volume fraction `0.990672`; calculated full-area inlet flow is liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`; steam outlet remains a pressure outlet with steam-dominant backflow; brine outlet inactive.
- Iteration budget: `5000` steady iterations, with recommended saves at `1000`, `3000`, and `5000` iterations.
- Convergence monitors: residuals, global mass imbalance, inlet phase mass flows, steam-outlet steam flow, steam-outlet liquid carryover, liquid-volume-fraction contours, and velocity vectors near the spiral inlet and steam outlet.
- Outcome: `Planned`.
- Evidence-use label: setup calculation only until `5000`-iteration residuals, mass balance, and outlet phase fluxes are checked.
- Hypothesized cause (if non-converged): not yet applicable; main risk is that no active brine outlet may accumulate or carry liquid to the steam outlet, making the run unsuitable for liquid-removal efficiency.
- Next action: create the Fluent case from `../../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`, confirm the brine outlet is not active, and run the planned checkpoint sequence.

### Run MWH-ACTUAL-AREA-2026-05-27
- Run ID: `MWH-ACTUAL-AREA-2026-05-27` (`Assumed` report label until Fluent filename is confirmed)
- Date: 2026-05-27
- Objective: Start a report-facing record for the mixed wet-half velocity-inlet simulation using the actual inlet-half area from the current geometry.
- Geometry: spiral-inlet BOC separator with split inlet; area interpreted as `2.6209e5 mm2 = 0.26209 m2` for each split inlet half.
- Mesh: same current project mesh family; approximately 1.8M nodes from prior user-reported mesh scale unless superseded by a new mesh export.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from mixed wet-half velocity-inlet setup; details pending confirmation from final case file.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; calculated total liquid inlet `115.59 kg/s`, total steam inlet `79.77 kg/s`, and total inlet flow `195.36 kg/s`.
- Iteration budget: pending.
- Convergence monitors: pending.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: inlet boundary-condition documentation only; not yet usable for separator efficiency or final performance claims.
- Hypothesized cause (if non-converged): pending actual solve/post-processing evidence.
- Next action: add mass flux interpretation, outlet phase fluxes, separator efficiency, and key contour/vector findings to `../../../Setup report/04-mixed-wet-half-actual-area.md`.

### Run FFF-2-OP0
- Run ID: `FFF-2-OP0` (`Assumed` temporary label until Fluent filename is confirmed)
- Date: 2026-05-21
- Objective: Test whether `FFF-2` convergence and liquid mass imbalance improve when the pressure reference matches the Purnanto 2013 convention where gauge and absolute pressures are equivalent.
- Geometry: Same as `FFF-2`; full separator model with brine outlet included.
- Mesh: same as `FFF-2`, approximately 1.8M nodes from current project mesh family.
- Physics model: same as `FFF-2`; steady pressure-based `Mixture` multiphase model, primary phase steam/vapor, secondary phase liquid water, `RNG k-epsilon`, energy off.
- Solver settings: same as `FFF-2` except `Operating Pressure = 0 Pa`.
- Boundary and initial conditions: inlet pressure set to `1140000 Pa`; steam outlet pressure outlet set to `1120000 Pa`; brine/liquid outlet pressure outlet set to `1120000 Pa`; all other inlet, outlet, initialization, and model settings retained from `FFF-2`.
- Iteration budget: preliminary diagnostic run just above 100 steady iterations; extend only if phase flux trends become physically plausible.
- Convergence monitors: residuals reported by user as smooth, non-jumpy, and flattening after just above 100 iterations.
- Outcome: `Partially Improved / Stalled`.
- Key flux result: user-reported Fluent flux order is liquid inlet, liquid outlet, steam inlet, steam outlet. Liquid phase fluxes were `109.8065259020202`, `-1.666485038755287e-194`, `-0`, and `-6.176921748322125e-101 kg/s`, so liquid outlet flow was effectively zero while liquid continued entering the domain. Steam phase fluxes were `37.53446178758816`, `-15.11238833163424`, `37.82770891200012`, and `-61.05984355746033 kg/s`, giving an approximate steam net of `-0.81 kg/s` under the reported sign convention.
- Evidence-use label: diagnostic only. Residual behavior improved compared with original `FFF-2`, but the phase fluxes are not physically balanced because liquid is not yet leaving through either outlet.
- Hypothesized cause (if non-converged): pressure-reference parity may improve numerical residual stability, but the current early solution still has liquid inventory accumulation or delayed/blocked brine outlet drainage; brine outlet pressure sensitivity, outlet placement, liquid residence-time development, or initialization history remain possible contributors.
- Next action: inspect liquid volume fraction near the brine outlet and continue only as a short trend test if the liquid front is moving toward drainage; otherwise classify the pressure-reference parity run as residual-improved but liquid-drainage failed and proceed to a brine outlet control.

### Run FFF-2
- Run ID: `FFF-2`
- Date: unknown; documented before `2026-05-07`
- Objective: Test the mixed wet-half velocity-inlet setup where both inlet halves use `26.81 m/s`, with liquid volume fraction assigned only to the wall-side wet half.
- Geometry: Full separator model with brine outlet included; steam outlet geometry remains a guessed implementation and suspected sensitivity source.
- Mesh: approximately 1.8M nodes from current project mesh family; detailed quality distribution still pending.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: `SIMPLE`, `Green-Gauss Node Based`, `PRESTO!`, second-order momentum/turbulence schemes, higher-order volume-fraction scheme where available; hybrid initialization with no water-pool patch.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; pressure outlets for steam and brine outlets with backflow fractions pending final audit.
- Iteration budget: approximately `1020` steady iterations.
- Convergence monitors: residuals still moving noticeably; mass-flow flux report collected at `1020` iterations.
- Outcome: `Stalled`.
- Key flux result: liquid inlet approximately `109.8065 kg/s`; liquid out through brine outlet approximately `161.0144 kg/s`; liquid out through steam outlet approximately `0.0096 kg/s`; liquid net approximately `-51.2175 kg/s`, so the liquid phase was not balanced.
- Evidence-use label: diagnostic only. This run is above the current `1000`-iteration evidence threshold, but it is not converged and should not be used for final separator efficiency, pressure-drop, or design-comparison claims.
- Hypothesized cause (if non-converged): brine outlet over-removal or continued redistribution of the initialized/hybrid liquid field; outlet backflow setup, brine outlet pressure, and steady dry-start behavior remain possible contributors.
- Next action: retain as the parent diagnostic comparison for `MWH-WP-2026-05-07-A`, but rebuild future design comparisons from a stable reference case.

### Run MWH-WP-2026-05-07-A
- Run ID: `MWH-WP-2026-05-07-A`
- Date: 2026-05-07
- Objective: Test whether initializing a lower water pool improves brine outlet liquid removal for the mixed wet-half velocity-inlet setup.
- Geometry: Full separator model with brine outlet included; steam outlet geometry is a guessed implementation and remains a suspected sensitivity source.
- Mesh: approximately 1.8M nodes from current project mesh family; detailed quality distribution still pending.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from parent mixed wet-half velocity-inlet setup; pressure-velocity coupling and discretization unchanged from parent.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; steam outlet pressure outlet with backflow liquid VF `0.0`; brine outlet pressure outlet with backflow liquid VF `1.0`; lower water-pool cell register patched to liquid VF `1.0` after hybrid initialization.
- Iteration budget: 3500 steady iterations.
- Convergence monitors: scaled residuals still changing at final iteration, but weak change over the last approximately 1000 iterations; mass-flow flux report collected.
- Outcome: `Partially Converged`.
- Key flux result: liquid inlet `109.8065 kg/s`; liquid out through brine outlet `1413.05 kg/s`; liquid out through steam outlet `1044.35 kg/s`; liquid net approximately `-2347.59 kg/s`, indicating depletion of initialized liquid inventory rather than stable operating balance.
- Evidence-use label: diagnostic only. This is the strongest current qualitative flow-pattern evidence because it reached `3500` iterations, but it is not valid for final quantitative carryover, separator efficiency, or mass-split claims.
- Hypothesized cause (if non-converged): steady solver is draining the patched water inventory; steam outlet geometry/intake flow may be entraining excessive liquid; brine outlet is active but the total liquid mass split is not physically stable.
- Next action: collect liquid-volume-fraction contours, velocity vectors, streamlines/pathlines near steam outlet intake, flux reports at multiple iteration counts, and residual/mass-imbalance history before choosing between transient water-pool test, steam outlet geometry revision, lower water-pool height test, or brine outlet pressure tuning.

### Run BGM-2026-04-22-A
- Run ID: `BGM-2026-04-22-A`
- Date: 2026-04-22
- Objective: Recreate legacy Bangma-based two-phase baseline and test convergence readiness.
- Geometry: Bangma-based model provided by supervisor/team.
- Mesh: approximately 300k nodes (reported).
- Physics model: two-phase cyclone separator recreation (details pending confirmation).
- Solver settings: ran to 1000 iterations (detailed numerics pending explicit capture).
- Boundary and initial conditions: pending full setting audit.
- Iteration budget: 1000 iterations.
- Convergence monitors: residual trend indicates non-convergence.
- Outcome: `Stalled`.
- Evidence-use label: setup/debug history only. Because this run reached `1000` iterations but did not exceed the current usable-evidence threshold and did not converge, it should not be used for performance interpretation.
- Hypothesized cause (if non-converged): mesh may be under-resolved, flow/BC settings may be incomplete or inconsistent.
- Next action: perform full solver/BC audit against `purnanto-zarrouk-cater-2013` technical notes, then rerun with controlled setting changes.

### Run SPLIT-MESH-PREFLIGHT-2026-07-29
- Run ID: `SPLIT-MESH-PREFLIGHT-2026-07-29`
- Date: 2026-07-29
- Objective: establish the authoritative post-replication spiral/split-inlet baseline and gate a carrier-only coarse/medium/fine mesh-convergence study.
- Geometry: intended spiral BOC with `0.724 m x 0.724 m` inlet, `0.006754 m` outer liquid strip, and `0.717246 m` inner steam region; live orientation remains unverified.
- Mesh: no accepted ladder. Historical split mesh metadata include about `1.4445M` cells and minimum orthogonal quality about `0.03168`, but exports have inconsistent zone preservation and are not systematic refinements.
- Physics model: planned frozen carrier field is steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off; no DPM/EWF.
- Solver settings: unresolved authority conflict between intended setup-07 `SIMPLE`/second-order/`QUICK` and actual archive `Coupled`/first-order.
- Boundary and initial conditions: target `1600 kJ/kg`; liquid `116.92 kg/s`, steam `80.69 kg/s`; two pure-phase velocity inlets at `27.118 m/s`; hybrid initialization intended.
- Iteration budget: none launched; stopping is to be based on residual plus physical-monitor stability rather than a fixed iteration count.
- Convergence indicators: not available. Required outputs and acceptance criteria are defined in setup `07a`.
- Outcome: `Stalled`.
- Evidence-use label: `Diagnostic / preflight only`.
- Hypothesized cause: remote endpoint unavailable; processor count unknown; no systematic mesh ladder; unresolved geometry-orientation and numerics-authority conflicts.
- Next action: reconnect and run read-only live inspection, freeze/read back the carrier setup, then generate and audit the three meshes before long calculations.

### Run SPLIT-MESH-CARRIER-2026-08-01
- Run ID: `SPLIT-MESH-CARRIER-2026-08-01` with extension `SPLIT-MESH-900K-EXT-2026-08-05`.
- Date: 2026-08-01 to 2026-08-05.
- Objective: establish carrier-field iteration and mesh independence for the post-replication spiral/split-inlet separator before DPM or EWF.
- Geometry: setup `07a`; distinct `liquidinlet` outer-wall strip and `steaminlet` inner/core region, `steamoutlet` as the only pressure outlet, and `bottom`/`wall-fluid` as stationary walls.
- Mesh: seven tetrahedral meshes with `1,688,678`, `3,609,102`, `5,335,623`, `9,720,194`, `10,756,635`, `11,959,759` and `13,370,267` cells. Minimum orthogonal quality is approximately `0.192-0.203`; maximum aspect ratio approximately `17.8-20.3`.
- Physics model: steady pressure-based Mixture; vapor primary and liquid secondary; RNG `k-epsilon`; gravity on; Energy off; DPM interaction off.
- Solver settings: SIMPLE, PRESTO!, Green-Gauss node-based gradient, second-order momentum, first-order `k`, second-order epsilon, QUICK volume fraction; imported URFs; hybrid initialization; 16 processes.
- Boundary and initial conditions: liquid `116.92 kg/s`, vapor `80.69 kg/s`, outlet gauge pressure `1.12 MPa`, liquid outlet backflow VF `0`; fresh hybrid initialization for each formal mesh.
- Iteration budget: 3000 formal iterations per mesh in 250-iteration blocks; separate 900k diagnostic continued from verified iteration 4000 to 6000 with 250-iteration case/data checkpoints.
- Convergence indicators: vapor outlet flow stable near `81.45 kg/s`; formal final-500 pressure drift `2.46-9.65%`; 900k extension final-500 pressure/outlet-velocity/domain-velocity/vorticity drift `4.61/1.49/1.70/1.83%`; continuity approximately `0.246` at 6000.
- Checkpoint inventory: phase-2 liquid inventory `104.05 kg` at iteration 4000, `134.33 kg` at 5000, `152.10 kg` at 5500 and `171.03 kg` at 6000. Pressure increases from `31.03` to `34.05 kPa` over the same checkpoints.
- Outcome: `Stalled / Diagnostic`. Preflight and file preservation accepted; iteration independence, mesh independence and GCI unresolved.
- Evidence-use label: vapor throughput may be described as mesh-insensitive under imposed flow; pressure, velocities, vorticity, carryover, carrier quality and efficiency are diagnostic/trend-only.
- Hypothesized cause: confirmed monotonic liquid inventory growth in a steady domain with continuous liquid inflow and no dedicated liquid outlet; the field is filling/redistributing rather than approaching a fixed-inventory steady state.
- Next action: freeze setup 07a. Create a new branch with credible liquid discharge for steady performance, or use a separately defined transient branch only for finite-time filling/redistribution. Do not add DPM/EWF to this unresolved carrier field.
## Run SETUP-07M-PRESSURE-OPENING-2026-08-21

- Run ID: `SETUP-07M-PRESSURE-OPENING-2026-08-21`.
- Objective: open the resolved brine pressure face from the accepted 07l
  hydrostatic-rest checkpoint at zero inlet flow, then introduce feed only
  after pressure-response and numerical gates pass.
- Source: setup-07l step-10 case/data; no failed 07j/07k or uncheckpointed live state.
- Matrix: low/centre/high pressures `1,121,895.244 / 1,122,090.400 /
  1,122,285.556 Pa`, each tested independently at `1e-6`, `3e-6` and `1e-5 s`.
- Matrix outcome: all nine one-step fields bounded, but one step was too short
  to resolve the directional brine flux; inlet ramp withheld.
- Extension outcome: ten `1e-5 s` steps gave liquid brine flows
  `-0.00724149 / +0.00451280 / +0.01626494 kg/s`, proving monotonic response
  and an endpoint sign bracket with very small centre flow.
- Direct ramp outcome: a `1%`, `dt=1e-6`, 20-inner start was finite but rejected
  at continuity `2.15676`.
- Micro-start outcome: at `0.1%`, `dt=1e-7`, 100 inner iterations and a further
  ten-step hold, continuity decreased monotonically to `0.00186867`; final
  brine liquid flow was `-0.0830901 kg/s` and Global Courant `3.46743e-6`.
- Continuation outcome: 0.2% and 0.5% passed their hard gates. The 1% field
  remained finite and bounded but stopped at final continuity `0.0177001`,
  above the `0.01` promotion gate. All higher-flow levels were withheld.
- Historical proposed action: hold the saved 1% checkpoint for 20 more
  `1e-7 s` steps with 100 inner iterations. The first connection attempt
  credited zero steps and is stale; no controller is active. After physical
  review this is retained as an optional numerical sensitivity, not the main
  continuation. Setup 07n instead reconstructs the pool level and outlet
  control from the mesh/physics definition.
- Evidence label: pressure bracket and 0.1% hold accepted as bounded diagnostics;
  production boundary, long-time level control and operating-flow validation unresolved.

## Run SETUP-07N-STAGE0-GEOMETRY-2026-08-22

- Run ID: `SETUP-07N-STAGE0-GEOMETRY-2026-08-22`.
- Objective: derive the resolved brine crown/outlet geometry and candidate pool
  inventories before any new physical solve.
- Parent use: the 620,431-cell mesh is authoritative. The setup-07l step-10
  case was loaded without data only as a verified settings carrier for fresh
  initialization/patch diagnostics; no 07l solution field was inherited.
- Ownership/runtime: server 1, Fluent 2024 R2, PyFluent 0.39.0, exactly 16
  ranks, no other connected client, and one local writer lock. Server 2 lacked
  all authoritative case/data parents and was excluded.
- Geometry result: SHA-256
  `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`;
  brine area `0.1993624690 m2`; crown/invert
  `-0.0015579789/-0.5067311525 m`; opening height `0.5051731736 m`; median
  crown-face height `0.0089871744 m`; inferred cylindrical wall extent
  `1.95976 m`.
- Candidate 1: boundary-face proxy crown plus two heights,
  `y=0.0164163698 m`; `98,473` cells patched; liquid volume
  `4.40015912 m3`; inventory `3877.46807 kg`.
- Candidate 2: boundary-face proxy crown plus four heights,
  `y=0.0343907186 m`; `99,647` cells patched; liquid volume
  `4.43625099 m3`; inventory `3909.27263 kg`.
- Safety state: no data file read, no physical step, no case/data write; DPM
  injection names `[]`, interaction/tracking false, all cell-zone sources
  false, brine outlet wall, EWF not activated and no sink introduced.
- Capability result: PyFluent's volume-cell mesh RPC returned
  `UNIMPLEMENTED`; a temporary UTL volume was not exposed as a field surface,
  and the initialized volume report failed with unbound `pm/volumes`. All
  temporary registers were deleted.
- Classification: geometry and patched inventory are `accepted diagnostic`;
  adjacent volume-cell height and Stage-0 completion are `diagnostic /
  unresolved`.
- Outcome: stopped before 07n-a physical relaxation. No controller remains.
  Candidate 2 remains only as an unsaved, non-parentable in-memory diagnostic;
  the next writer must cold-load the accepted settings carrier.
- Next action: obtain a Fluent-2024-R2-supported local volume-cell-spacing
  readback or independently inspect/export the mesh; only then set the first
  resolved submergence and run a closed-drain relaxation window.

## Run SETUP-07N-A-LOWER-FACEPROXY-STARTUP-2026-08-22

- Run ID: `SETUP-07N-A-LOWER-FACEPROXY-STARTUP-2026-08-22`; authoritative
  label `brine620k_07n_a_closeddrain_lower_faceproxy_pilot_attempt4_20260822`.
- Objective: prove that the lower Stage-0 candidate can be reconstructed and
  marched safely without inheriting a prior data field; this is an
  implementation/startup pilot, not accepted water-level relaxation.
- Parent/setup: checksum-bound setup-07l step-10 **case only**; fresh Hybrid
  Initialization; exact `98,473`-cell patch to `y=0.0164163698 m`; zero feed;
  brine wall; steam pressure outlet; explicit VOF/PISO/PRESTO/Geo-Reconstruct;
  RNG k-epsilon; gravity; Energy off; DPM zero/off; EWF/sources/sinks off.
- Execution: server 1, Fluent 2024 R2, 16 ranks, one owner; ten one-step RPCs at
  `dt=1e-6 s`, 20 inner iterations; hashed t0/step-1/step-5/step-10 pairs plus
  transcript, residual and physical histories.
- Outcome: all steps/gates passed. Final continuity `2.74398e-6`, Courant
  `7.73149e-9`, liquid inventory `3877.468071 kg`, brine-face liquid VF
  `1.0`, pressure range `1.1199992-1.1329161 MPa`, maximum velocity
  `6.63818e-5 m/s`, zero liquid through the steam outlet.
- Attempt correction: attempt 3 physically reached one finite step but failed
  post-solve storage bookkeeping before credit/checkpoint. Its original
  manifest is preserved and a checksum-bound correction makes the field
  ineligible and non-resumable.
- Classification: `Diagnostic / unresolved lower faceproxy bounded startup`.
  Ten microseconds is not relaxation, and the adjacent volume-cell height is
  still unresolved.

## Run SETUP-07N-A-LOWER-FACEPROXY-DT2EM6-2026-08-22

- Run ID: `SETUP-07N-A-LOWER-FACEPROXY-DT2EM6-2026-08-22`; label
  `brine620k_07n_a_closeddrain_lower_faceproxy_dt2em6_extension_attempt1_20260822`.
- Objective: first conservative external dt schedule step after the bounded
  pilot; change only `dt: 1e-6 -> 2e-6 s`.
- Parent: pilot step-10 case/data, remotely rehashed to
  `5a17b988...ef19b` / `29780b16...0a8d` before cold load; clock read back
  step 10 / `10 us`.
- Execution: ten more one-step RPCs, 20 inner iterations, hashed
  additional-step-1/5/10 pairs and the full gate package.
- Outcome: all gates passed at cumulative step 20 / `30 us`. Final continuity
  `4.64048e-6`, Courant `4.81584e-8`, liquid inventory `3877.468071 kg`,
  brine-face liquid VF `1.0`, pressure range `1.1199992-1.1329162 MPa`, maximum
  velocity `1.64972e-4 m/s`, zero liquid steam-outlet flow.
- Classification: `Diagnostic / unresolved lower faceproxy dt2em6 bounded
  startup`. The endpoint may parent only a further same-proxy conservative dt
  diagnostic; it is not a general 07n parent. Stop before more marching because
  `30 us` is only about `0.07%` of the `~0.0428 s` gravity scale and the pool
  height still lacks the adjacent-cell proof.

## Run SETUP-07N-STAGE0-WHOLE-CELL-PLATEAU-2026-08-22

- Run ID: `SETUP-07N-STAGE0-WHOLE-CELL-PLATEAU-2026-08-22`; accepted attempt
  `brine620k_07n_stage0_pool_selection_plateau_attempt4_20260822`.
- Objective: replace the boundary-face target proxy with an exact,
  reproducible whole-volume-cell selection interval before further physical
  marching.
- Geometry/mesh: resolved-brine geometry; `620,431` cells, 16 partitions,
  brine crown `y=-0.0015579789 m`. The threshold scan selected exactly
  `98,473` cells over `y=0.0164023303045-0.0165144008650 m`; centered threshold
  `0.0164583655847 m`; liquid volume `4.400159116 m3`.
- Physics/setup: setup-07l step-10 case only as settings carrier; VOF vapor/
  liquid, RNG k-epsilon, gravity, Energy off, DPM zero/off, EWF/sources/sinks
  off, zero inlets, brine wall and steam pressure outlet.
- Solver/initialization: PISO, PRESTO, Geo-Reconstruct, WFGC; one Hybrid
  Initialization followed by 44 reversible selection queries (88 patch/reset
  operations). No data file was read.
- Boundary/initial conditions: both phase rates at both inlets `0 kg/s`;
  brine closed; centered whole-cell phase-2 patch only.
- Budget: zero physical steps and no case/data output.
- Convergence/monitor evidence: not applicable to a zero-step geometry
  diagnostic. Fluent 2024 R2, exclusive client, `n0..n15`, carrier checksum,
  exact cell count, DPM/EWF/source state and temporary-register cleanup passed.
- Outcome: `Accepted mesh-selection diagnostic`. Attempts 1-3 are preserved
  zero-step `Diagnostic / unresolved` path-observation failures.
- Limitation/cause: this establishes a deterministic CFD cell set, not a
  direct cell-vertex measurement or plant operating level.
- Next action: freshly reconstruct this pool, relax it over meaningful physical
  time and retain the physical-level uncertainty.

## Run SETUP-07N-A-MESHSELECTED-CLOSED-DRAIN-2026-08-22

- Run ID: `SETUP-07N-A-MESHSELECTED-CLOSED-DRAIN-2026-08-22`; lineage begins
  `brine620k_07n_a_closeddrain_meshselected_startup_attempt1_20260822` and
  continues through checksum-bound timestep stages and holds.
- Objective: determine whether the exact whole-cell pool can remain bounded,
  liquid-sealed and storage-consistent through a physically meaningful
  closed-drain relaxation before any outlet/control experiment.
- Geometry/mesh: resolved brine pipe/outlet; `620,431` cells, 16 partitions,
  minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258`;
  `98,473` liquid cells, `4.400159116 m3`, `3877.468071 kg`.
- Physics model: transient explicit VOF, vapor primary/liquid secondary, RNG
  k-epsilon with standard wall functions, gravity, Energy off; DPM zero/off,
  EWF false and all sources/sinks off.
- Solver settings: pressure-based PISO, PRESTO, Geo-Reconstruct, WFGC fast,
  first-order time, 20 inner iterations, maximum explicit-VOF Courant `0.25`,
  one physical step per guarded RPC.
- Boundary/initial conditions: both phase rates at both inlets `0 kg/s`;
  brine outlet is a wall; steam pressure outlet `1,120,000 Pa`; fresh Hybrid
  Initialization and centered whole-cell liquid patch, followed by unique
  time-zero save/cold reload.
- Budget/execution: physical `dt` advanced only by factors of two from `1e-6`
  to `2.56e-4 s`, then held fixed. The completed chain reached 940 cumulative
  steps and `0.22271 s`, with unique t0/stage/hold checkpoints, transcripts,
  residual/physical histories and manifests. A preserved stage-5 attempt has
  27 monitored steps plus one solved/uncredited step and was not resumed; its
  replacement cold-loaded the verified parent and completed independently.
- Convergence indicators: step-940 continuity `3.67467e-4`, Global Courant
  `0.0125058`, average velocity `0.00357883 m/s`, vorticity `0.0331321 1/s`,
  maximum velocity `0.144127 m/s`, pressure `1.1199994-1.1329449 MPa`, liquid
  inventory unchanged, brine-face liquid VF `1.0`, liquid steam-outlet flow
  zero and no hard-gate failure. Final-20 regression drift was
  `-1.540/-0.637/-0.912%` for average velocity/vorticity/maximum velocity.
- Outcome: `Diagnostic / unresolved`. The numerical and physical hard gates
  pass and the pool is nearly quiescent, but the average-velocity stationarity
  target and a localized matched-timestep maximum-velocity gate do not.
- Hypothesized cause: expected gravity-driven adjustment from the freshly
  patched constant-pressure Hybrid field; no numerical or mass-loss failure is
  indicated.
- Matched timestep result: 20 base steps and 40 half-`dt` steps from the same
  step-940 parent ended at `t=0.22783 s`. Average velocity/vorticity agreed
  within `0.906/0.941%`, while maximum velocity differed `7.332%`.
- Current/next action: localization, inner-iteration, `dt/8`, implicit-VOF and
  plain-Coupled sensitivities are now complete below. Outlet opening, level
  control and mesh convergence remain withheld; no writer is active.

## Run SETUP-07N-CLOSED-POOL-SOLVER-SCREEN-2026-08-23

- Run ID: `SETUP-07N-CLOSED-POOL-SOLVER-SCREEN-2026-08-23`.
- Objective: determine whether the unresolved closed-pool field depends on
  VOF formulation, implicit temporal/interface discretization or
  pressure-velocity coupling before any constant-level outlet experiment.
- Common parent: accepted explicit/PISO step 940 at `t=0.22271 s`; case/data
  SHA-256 `03383ac0...6c7c9` / `a5963dfa...0772a`.
- Fixed contract: `620,431` cells; zero feed; closed brine wall; steam pressure
  outlet; RNG k-epsilon; gravity; Energy off; DPM zero/off; EWF and all
  sources/sinks off; `dt=2.56e-4 s`; 20 physical steps; 20 inner iterations;
  no initialization. Every physical branch ended at `t=0.22783 s`.
- Zero-step readback: attempts 1-7 are preserved stopped path diagnostics.
  Attempts 8/9 accepted implicit VOF/PISO, `(mp/scheme-type 0)`, automatic
  Compressive selection, allowed Compressive/Modified-HRIC schemes, exact
  implicit Courant field and exact explicit restore. They ran zero steps.
- Implicit first-order result: Compressive passed every hard gate; endpoint
  continuity `8.51484e-4`, average velocity `0.00354829 m/s`, vorticity
  `0.0333085 1/s`, maximum velocity `0.160205 m/s`. Differences from explicit
  were `0.873/1.168/12.669%`; classification `diagnostic / unresolved`.
- Implicit second-order result: Compressive passed and moved those differences
  to `0.359/0.635/6.993%`; endpoint continuity `7.14202e-4`. It is the better
  implicit temporal choice but remains non-promotable.
- Interface result: second-order Modified-HRIC passed, with endpoint
  continuity `7.00262e-4`. It differed from second-order Compressive by only
  `0.057/0.083/0.152%` and from explicit by `0.301/0.552/6.831%` for average
  velocity/vorticity/maximum velocity. The interface-scheme axis is resolved,
  but formulation independence is not.
- Pressure-velocity result: explicit VOF/plain Coupled passed 20/20 steps with
  `coupled_form=false`, proving Coupled-with-Volume-Fractions was not selected.
  It reproduced the PISO field to within `0.000063%`, reduced endpoint
  continuity to `2.395996e-4`, and required `3.2339x` the summed solve-step wall
  time. PISO is retained for efficient closed-pool work.
- Coupled attempt history: attempt 1 stopped before authentication when the
  local sandbox denied raw TCP. Attempt 2 authenticated and stopped before a
  physical step on an over-strict explicit-VOF residual assertion. Attempt 3
  cold-loaded the parent under a fresh label and completed; neither stopped
  in-memory field was resumed.
- Hard-gate outcome: all completed physical branches retained bounded
  residuals/Courant/VOF/pressure/velocity, stable liquid inventory (maximum
  cross-branch endpoint difference `0.0002385 kg`), zero liquid
  steam-outlet flow, brine-face liquid VF `1.0`, storage/clock closure and full
  DPM/EWF/source/boundary settings. Separate case/data checkpoints exist at
  additional steps 1, 5, 10 and 20.
- Evidence: `implicit_piso_comparison.json`,
  `implicit_temporal_order_comparison.json`,
  `implicit_interface_scheme_comparison.json` and
  `pressure_velocity_coupling_comparison.json` in the matched-window comparison
  directory. The final two SHA-256 values are `e87de881...cae4` and
  `ccec7afc...7248`.
- Outcome: solver sensitivities are `accepted diagnostic`; the carrier remains
  `diagnostic / unresolved`. No implicit or Coupled endpoint is eligible as a
  parent. Solver swapping stops; the next model task is a separately gated
  constant-level brine-outlet/control strategy with explicit downstream
  pressure/head/resistance and operating-level assumptions. Mesh convergence,
  DPM and EWF remain withheld.

## Run SETUP-07N-C-PRESSURE-RESPONSE-SIGN-2026-08-23

- Objective: open the liquid-covered brine face at zero feed from the exact
  explicit/PISO step-940 parent and establish the sign/magnitude of the
  hydraulic response before authorizing level feedback.
- Planned matrix: diagnostic centre `1,122,423.2 Pa` and
  `+/-195.156 Pa`, each independently cold-loaded, ten steps at
  `dt=2.56e-4 s`, 100 inner iterations, checkpoints at steps 0/1/5/10.
- Attempt 1: authenticated, verified Fluent 2024 R2/16 ranks, exact parent
  checksums and the closed settings contract, then stopped on a gRPC timeout
  during a redundant read-only phase-flux report. Zero boundary changes, zero
  physical steps and zero case/data writes were credited. Manifest SHA-256
  `d58d06c9...c26`; no-resume disposition SHA-256 `0c008bd3...8449`.
- Attempt 2: the fresh label stopped before authentication when bounded raw
  TCP timed out. Manifest SHA-256 `d0e5963e...238`; no-resume disposition
  SHA-256 `dd391d0d...854`.
- Infrastructure diagnosis: the Windows host answers ICMP at `8.6-9.0 ms`,
  but Fluent port `57329` times out. No setup-07n writer/controller is active;
  the partner's independent Stage-4 observer was not altered. A separately
  configured server-2 endpoint was distinguished and used only for the clean,
  non-authoritative reconstruction recorded below.
- Current classification: `diagnostic / unresolved; zero physical result`.
  Attempt 3 is statically ready under a unique label and may begin only after
  server-1 raw-TCP reachability returns. No feedback controller or inlet feed
  is authorized before this sign gate passes.

## Run SPLIT-07N-A-SERVER2-INDEPENDENT-DT-LADDER-2026-08-24

- Run ID: `SPLIT-07N-A-SERVER2-INDEPENDENT-DT-LADDER-2026-08-24`.
- Date: 2026-08-24 NZST.
- Objective: use the separately configured server 2 for a bounded independent
  reconstruction and determine the closed-pool startup timestep boundary
  without competing with, resuming or replacing any authoritative or failed
  field.
- Geometry: resolved-brine-outlet separator geometry; brine face closed as a
  wall for isolation.
- Mesh: `620,431` cells, exactly 16 solver ranks; deterministic whole-cell
  liquid pool of `98,473` cells / `4.400159116 m3`.
- Physics model: transient two-phase VOF, vapor primary and liquid secondary,
  RNG `k-epsilon`, gravity on, Energy off; DPM has zero injection objects and
  is off; EWF and every cell source/sink are off.
- Solver settings: pressure based, explicit VOF, PISO, PRESTO,
  Geo-Reconstruct, WFGC fast, first-order transient; ten physical steps per
  level, one step per RPC, 20 inner iterations, factor-two `dt` ladder from
  `1e-6` to `5.12e-4 s`.
- Boundary and initial conditions: fresh case-only settings reconstruction,
  Hybrid Initialization, exact pool patch and time-zero save/reload; liquid
  and vapor inlet mass flows both zero, steam pressure outlet retained and
  brine wall closed. The prohibited server-2 steady Mixture field and every
  stopped setup-07n field were not loaded.
- Iteration budget: 100 physical steps completed to `t=0.01023 s`; no
  `1.024e-3 s` stage was started.
- Convergence monitors: all scaled residuals including within-step envelope;
  Global Courant; pressure, velocity and VOF extrema; mixture and phase fluxes;
  liquid inventory/storage closure; steam seal; brine-face coverage; clock;
  DPM/EWF/source and complete settings readback.
- Outcome: `Partially converged / terminal diagnostic at 512 us`. All stages
  through `dt=2.56e-4 s` remained bounded. The last clean independent endpoint
  at step 90 had final continuity `7.94905e-4`, maximum stage continuity
  `0.450821`, Courant `0.00104941` and maximum velocity `0.0242414 m/s`. At
  `dt=5.12e-4 s`, every step's inner continuity exceeded `1`, the stage maximum
  was `2.56074`, the first end-step value was `0.0104354`, and final continuity
  recovered to `0.00254275`; the whole envelope therefore failed.
- Mass/storage evidence: liquid inventory range was exactly `0 kg`, liquid
  steam-outlet flow was zero, brine-face liquid VF was `1.0` and mixture net
  flow was only round-off-scale vapor flux. Because feed and drainage were
  both zero, this is a closed-pool conservation/steam-seal result, not an
  operating mass-balance qualification.
- Hypothesized cause (if non-converged): with the inner cap fixed at 20, the
  doubled physical step creates a large pressure/continuity correction inside
  each step. The very low final Courant (`0.00457429`) shows that the stop is a
  residual-envelope failure rather than a Courant limit.
- Next action: do not promote or resume the `512 us` field and do not start a
  larger timestep child. Retain `256 us` only as the last clean independent
  comparison. Keep the authoritative server-1 step-940 parent unchanged;
  qualify the open brine outlet and constant-level response only from that
  parent, or after an exact checksum-verified transfer and full readback.

### Post-processing SETUP-07N-SERVER2-STILLPOOL-FIGURES-2026-08-25

- Activity ID: `SETUP-07N-SERVER2-STILLPOOL-FIGURES-2026-08-25`; zero new CFD
  iterations.
- Objective: visually verify pool placement, brine-leg liquid coverage,
  pressure-head development and startup velocity structure in the independent
  server-2 reconstruction.
- Sources: checksum-bound setup-07n independent time zero, step 10 / `10 us`
  and last-clean step 90 / `5.11 ms`; the terminal `512 us` field was not
  loaded.
- Controls: Fluent 2024 R2, 16 ranks, cell-centred contours, fixed field
  ranges, brine-axis `yz` plane at `x=0.7143434057 m`, zero feed, closed brine
  wall, DPM zero/off, EWF/sources off. No initialization, solve, DPM update or
  case/data write.
- Outputs: 12 SHA-bound 1920 x 1440 Fluent PNGs, five labelled comparison
  composites and machine-readable graphics/composite manifests under
  `brine620k_07n_a_server2_independent_stillpool_figures_attempt1_20260825`.
- Outcome: `Accepted post-processing diagnostic`. The pool visibly covers the
  brine-leg entrance and persists, the pressure field develops a gravity head,
  and low velocity remains concentrated near the interface/pipe entrance.
  This does not qualify drainage, level control or operating mass balance.
- Next action: while server 1 remains down, the most useful independent
  numerical continuation is a fresh `dt=2.56e-4 s` hold from clean step 90 to
  about one local gravity time (`t≈0.0435 s`), with the existing hard gates.
  It must remain separate from the authoritative server-1 lineage.

## Run SETUP-07N-SERVER2-DRAINAGE-LAUNCH-2026-08-25

- Run ID: `SETUP-07N-SERVER2-DRAINAGE-LAUNCH-2026-08-25`.
- Date: 2026-08-25 NZST.
- Objective: establish a matched closed-wall background and then run a
  zero-feed outlet-pressure response bracket before any feed or controller.
- Geometry/mesh: resolved brine outlet; `620,431` cells; deterministic
  `98,473`-cell liquid pool; Fluent 2024 R2 on 16 ranks.
- Physics: transient explicit VOF, vapor primary/liquid secondary, RNG
  `k-epsilon`, gravity, Energy off; DPM zero/off, EWF off and all sinks/sources
  off.
- Solver/boundaries: PISO/PRESTO/Geo-Reconstruct/WFGC, first-order time,
  `dt=2.56e-4 s`, 20 inner iterations; zero inlets. The control retained the
  brine wall. Planned pressure members were `1,122,154.344`, `1,122,349.500`
  and `1,122,544.656 Pa`, all CFD-derived modified-pressure diagnostics.
- Budget: ten matched control steps and ten steps per pressure member, one
  step per RPC, checkpoints at additional steps 1/5/10.
- Convergence/physical evidence: control steps 91-94 passed all gates with
  continuity `8.09759e-4-8.77262e-4`, Courant `0.00110266-0.00127507`, maximum
  velocity `0.0252033-0.0279062 m/s`, exact liquid inventory and brine-face VF
  `1.0`. Step 95 solved but its post-step monitor did not complete.
- Outcome: `Stalled / diagnostic unresolved`. The control stopped in optional
  scratch-report deletion verification after four fully monitored steps; a
  non-overwriting disposition prohibits resume. The pressure attempt then
  timed out before authentication on the Fluent Scheme version call despite
  3/3 raw-TCP probes, so it loaded no parent, changed no boundary and completed
  zero steps.
- Hypothesized cause: the TCP listener remains open while Fluent's Scheme/gRPC
  service is not returning calls after the report-cleanup stall. This is a
  service/connection failure, not a numerical or drainage result.
- Next action: wait for or restart a responsive Fluent server mode, use a new
  non-overwriting attempt label and cold-load the original step-90 pair. Do not
  use the interrupted in-memory field. Withhold full feed, 07n-b and feedback
  until the zero-feed pressure sign/steam-seal gate passes.
