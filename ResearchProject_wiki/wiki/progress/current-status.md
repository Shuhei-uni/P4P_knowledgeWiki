# Current Status

## Setup 07n calibrated-pressure long hold (`diagnostic / unresolved`; 2026-08-28 NZST)

- The independent 0.05%-feed 70-step branch completed from the checksum-bound
  server-2 clean step-90 pair. It held the original pressure through step 10,
  then applied one evidence-calibrated `+23.218830875 Pa` change while keeping
  `dt=1.28e-4 s`, 100 inner iterations and all model/source settings fixed.
- Numerical and routing behavior stayed clean: final-two continuity
  `7.90715e-4/7.93757e-4`, Courant `0.00764008`, brine-face liquid VF `1.0`,
  zero vapor through brine, zero liquid through steam, finite fields and no
  DPM/EWF/source drift. Reported inventory remained `3877.468071 kg`.
- Sustained mass balance failed. Step-70 liquid/vapor/total imbalance was
  `-0.01155471/+0.0000760171/-0.011478693 kg/s`; these are also the final-ten
  maximum absolute values and exceed the `0.005 kg/s` liquid/total limit.
- The branch is completed evidence only: `eligible_parent:false`, no resume,
  no unchanged repeat and no level-control or plant-pressure claim. A
  non-overwriting disposition corrects stale nested `zero-feed/accepted`
  summary wording without altering the original manifests.
- No local writer remains. With less than one full run window before the
  scheduled cutoff, no new physical calculation was started. Next work should
  use a fresh clean-step-90 load and test one additional held pressure action
  after the short balance window; all other factors stay fixed.

## Setup 07n sustained drainage status (`diagnostic / unresolved`; 2026-08-27 NZST)

- No local Fluent writer/controller is active. A bounded unauthenticated check
  found the configured server-2 TCP port reachable; Fluent health and ranks
  have not been re-authenticated since the stopped controller.
- The earlier 0.05%-feed pass is valid only for its ten-step / `1.28 ms`
  window. An independent fixed-pressure hold reached 36 credited steps with
  continuity `7.91749e-4`, Courant `0.00452474`, full liquid brine coverage and
  zero cross-phase leakage, but liquid drainage rose to `0.10864564 kg/s`
  against `0.05846 kg/s` feed. Liquid/total imbalance was
  `-0.050185643/-0.049855477 kg/s`, so the long hold failed.
- A delayed gain-0.25 pressure controller completed 50 steps with low residuals
  and intact sealing, but crossed the balance point and overshot. Its final
  liquid/total imbalance was `+0.019462106/+0.019334063 kg/s`; the required
  five-step balance window failed.
- A one-factor gain-0.05 controller reached 47 credited steps before the next
  solve lost its gRPC stream. Its last credited liquid/total imbalance was
  `-0.038632126/-0.038377965 kg/s`; continuity `7.72592e-4`, Courant
  `0.00542563`, inventory and steam-seal gates still passed. The interrupted
  step is uncredited.
- All three sustained/controller endpoints are `eligible_parent:false` and
  prohibited from resume. The clean server-2 step-90 pair remains the only
  authorized origin for another independent diagnostic.
- Interpretation: the resolved pool can seal steam and drain liquid, while
  residual convergence remains much easier than sustained mass balance. The
  current per-step proportional pressure controller is reacting to a delayed
  hydraulic response. The next controller should update only after a settling
  window or use a separately qualified filtered/PI level signal; it must not
  be represented as a plant pressure or validated level controller.

## Setup 07n resolved low-feed drainage (accepted diagnostic; 2026-08-25 NZST)

- Server 2 cold-loaded the checksum-bound clean step-90 parent for every
  comparison; Fluent 2024 R2, 16 ranks, parent hashes, settings, clock, DPM
  zero/off, EWF off and source-off gates passed. Nothing was merged into the
  unavailable server-1 lineage.
- At common feed 0.05%, pressure 1,122,263.621237 Pa, dt=128 us and 100 inner
  iterations, ten steps gave liquid 0.0584600 in / 0.0584601 out kg/s, vapor
  0.0403450 in / 0.0403450 out kg/s and total net -9.11e-8 kg/s. Continuity
  tail was 0.00201686/0.00173276, Courant 0.00248721, reported inventory was
  unchanged and the fully liquid brine face blocked all vapor.
- This is accepted diagnostic evidence, not a plant-valid pressure or eligible
  production parent. The balanced window is only 1.28 ms.
- A post-processing-only six-second H.264 pathway video was exported from the
  hash-verified step-100 endpoint. It uses 12 exact `liquidinlet`-origin
  massless carrier-pathline frames (827 seeds), not DPM particles or physical
  time. The optional `steaminlet` scene was rejected after Fluent read it back
  as `wall-fluid`. No CFD step, initialization, DPM update or case/data write
  occurred. Artifact and manifest:
  `../../../PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07n_s2_p1122264_0p05feed_step100_carrier_pathline_video_attempt3_20260825/`.
- A fixed-pressure load screen passed 0.05625% through ten steps but failed
  0.0625% and 0.075% after one step at continuity 1.05293 and 1.26332. Those
  fields are terminal. Fluent exposed no writable bulk VOF mass-flow-outlet
  rate, so no phasic outlet routing was prescribed.
- Next: design a gradual pressure-feedback/ramp study from independent cold
  loads and obtain downstream head/resistance and operating-level data. Mesh
  convergence, efficiency, DPM and EWF remain blocked. A bounded next
  diagnostic is the same 0.05625% feed at interpolated pressure
  1,122,261.011 Pa, again from the original clean step-90 parent.

## Setup 07n mesh-selected closed-drain relaxation (`diagnostic / unresolved`; no writer active 2026-08-24 NZST)

- An accepted zero-step threshold scan now defines a reproducible whole-cell
  pool even though Fluent 2024 R2 still does not expose the adjacent-cell
  vertices. The invariant `98,473`-cell selection interval is
  `y=0.0164023303045-0.0165144008650 m`; its centered threshold is
  `0.0164583655847 m`. This is an accepted **mesh-selection diagnostic**, not a
  measured plant water level.
- The fresh mesh-selected startup used setup-07l step-10 **case only**, no
  inherited data, Hybrid Initialization, and a new time-zero patch/save/reload.
  The liquid volume/inventory is `4.400159116 m3` / `3877.468071 kg`. DPM has
  zero injections and is off; EWF is false; sources/sinks are off; both feeds
  are zero and the brine face is a wall.
- The guarded timestep ladder and eight same-`dt` stages completed through
  step 940 / `t=0.22271 s`. Completed stages passed every residual, Courant,
  VOF, pressure, velocity, inventory, storage, steam-seal, clock, DPM, EWF,
  source and settings gate. Liquid inventory stayed exactly `3877.468071 kg`,
  brine-face liquid VF stayed `1.0`, and liquid steam-outlet flow stayed zero.
- The original stage-5 attempt is preserved as
  `stopped_postsolve_monitoring`: 27 steps are fully monitored and the next
  solved step is uncredited. It was not resumed. A new non-overwriting
  attempt cold-loaded the verified step-540 parent and completed to step 640.
- Step 940 ended with continuity `3.67467e-4`, Courant `0.0125058`,
  domain-average velocity `0.00357883 m/s`, vorticity `0.0331321 1/s` and
  maximum velocity `0.144127 m/s`. The last-20 regressions were `-1.540%`,
  `-0.637%` and `-0.912%` for those three physical monitors. The pool is
  bounded and nearly quiescent, but the average-velocity drift still exceeds
  the strict `1%` stationarity target.
- A fair matched window cold-loaded the same checksum-bound step-940 parent:
  20 steps at `dt=2.56e-4 s`, 40 at `1.28e-4 s` and 80 at `6.4e-5 s`, all to
  `t=0.22783 s`. Every branch passed its hard gates and endpoint pressure,
  inventories, VOF and steam seal matched. Half-to-quarter endpoint changes
  were `-1.427%` average velocity, `-1.404%` vorticity and `-7.491%` maximum
  velocity. The discrepancy grew rather than contracted, so time-step
  independence **failed**. Continuity improved to `1.99940e-4` and Courant
  halved as expected.
- A matched 100-inner branch at the baseline `dt=2.56e-4 s` changed average
  velocity, vorticity and maximum velocity by less than `0.000009%` across all
  20 samples, while endpoint continuity improved `99.70%` to `1.14616e-6`.
  This accepted numerical diagnostic rules out insufficient inner iterations
  as the cause of the timestep discrepancy.
- Accepted post-processing localization places all three maxima on cell index
  `382511`, centroid `(0.809789, 0.0420206, 0.651966) m`, with liquid VF
  `0.134811-0.134831`. The top-20 regions strongly overlap, so this is a small
  persistent interfacial region, not a migrating or isolated cell. Its
  turbulent viscosity is only `0.20-0.24%` of the domain maximum, ruling out
  the known one-cell limiter as the cause.
- The matched `dt/8` branch completed 160 x `3.2e-5 s` from the same step-940
  parent and ended at `t=0.22783 s`. Every hard gate passed, but
  quarter-to-eighth endpoint differences were `2.150%` average velocity,
  `1.936%` vorticity and `7.283%` maximum velocity; 80-sample means were
  `1.284%`, `1.217%` and `6.092%`. The differences did not contract, so
  explicit-VOF timestep halving is stopped.
- Zero-step implicit-VOF attempts 8 and 9 passed exact cold-restore and
  settings readback. Fluent 2024 R2 supports implicit VOF/PISO here, changes
  Geo-Reconstruct to Compressive, exposes Compressive and Modified-HRIC, and
  reports `cell-convective-courant-number`. Attempts 1-7 remain preserved
  zero-step path diagnostics; no stopped probe field was resumed.
- Three matched implicit/PISO windows completed from the exact step-940
  parent. First-order Compressive differed from explicit by `0.873%` average
  velocity, `1.168%` vorticity and `12.669%` maximum velocity. Second-order
  Compressive reduced those to `0.359%`, `0.635%` and `6.993%`; second-order
  Modified-HRIC reduced them marginally to `0.301%`, `0.552%` and `6.831%`.
  Every hard gate passed, but formulation independence did not.
- A matched explicit-VOF/plain-Coupled branch also completed. Fluent read back
  `flow_scheme=Coupled`, `coupled_form=false`, Geo-Reconstruct and the full
  unchanged safety contract. Its physical field matched PISO within
  `0.000063%`, while summed step wall time was `3.234x` larger. PISO is
  retained as the efficient closed-pool baseline; pressure-velocity coupling
  is not the source of the unresolved field sensitivity.
- Current decision: `diagnostic / unresolved`. No matched endpoint is
  promoted to outlet opening, level control or mesh convergence. The solver
  screen is complete enough to stop closed-pool solver swapping: retain PISO,
  retain the explicit step-940 pair as the common diagnostic parent, and move
  next to a separately gated constant-level outlet/control strategy. Plant
  level/head, pipe/valve resistance, formulation independence, mesh
  convergence, DPM and EWF remain unresolved. No local Fluent
  writer/controller is active after the completed screen.
- Open-drain launch status: the new zero-feed centre/`+/-195.156 Pa`
  pressure-response probe is implemented from the exact step-940 parent.
  Attempt 1 passed parent hash/settings/version/rank gates but lost its gRPC
  stream during a redundant read-only phase-flux report; attempt 2 then failed
  raw TCP before authentication. Both credited zero boundary changes and zero
  physical steps and have non-overwriting no-resume disposition records. The
  Windows host answers ICMP, but the Fluent server-1 port is unreachable.
  Attempt 3 is prepared and remains unstarted; no controller is authorized.
- Server-endpoint correction and independent result: the occupied partner
  Stage-4 endpoint is Fluent 2025 R2, but the separately configured server 2
  was available as Fluent 2024 R2 with exactly 16 ranks and no client. Because
  it lacked the authoritative server-1 step-940 pair, it was not used as a
  continuation. A clean case-only reconstruction instead reproduced the
  `98,473`-cell closed pool and ran an independent factor-two timestep ladder.
  The last clean comparison was `dt=2.56e-4 s` at step 90 / `t=0.00511 s`
  (final continuity `7.94905e-4`, stage maximum `0.450821`, Courant
  `0.00104941`). The `dt=5.12e-4 s` stage completed to step 100 but failed its
  residual envelope: every step spiked above `1`, with maximum `2.56074`, and
  is a non-resumable terminal diagnostic. No `1.024e-3 s` child was started.
  Inventory and steam seal remained exact, but zero feed and a brine wall mean
  no operating drainage or through-flow mass balance was tested. The
  authoritative server-1 parent and open-drain blocker are unchanged.
- Still-pool figures: a checksum-bound, post-processing-only server-2 export
  produced 12 full-resolution Fluent contours and five report-ready composites
  for time zero, the first `10 us` endpoint and last clean `5.11 ms` endpoint.
  Liquid VF shows the pool fully covering the brine-leg entrance with no
  visible loss; pressure develops the expected lower-pool head and velocity is
  localized near the interface/pipe entrance. This is independent setup-07n
  evidence, not the accepted historical setup-07l step-10 field. The exporter
  ran zero iterations and left no controller/writer active.
- First server-2 drainage launch: a matched closed-wall control from the exact
  clean step-90 pair fully monitored four additional steps. Continuity stayed
  `8.10e-4-8.77e-4`, Courant `0.00110-0.00128`, maximum velocity
  `0.0252-0.0279 m/s`, inventory `3877.468071 kg` and brine-face liquid VF
  `1.0`. Step 95 solved but stalled in optional scratch-report deletion
  verification, so it is observed-but-uncredited and the attempt is
  non-resumable. A fresh pressure-bracket attempt then passed 3/3 raw-TCP
  probes but stalled before authentication on Fluent's Scheme version query.
  It changed no boundary, loaded no parent and advanced zero steps. Thus there
  is still no drainage result; server 2's TCP listener is reachable but its
  Fluent gRPC/Scheme service is currently unresponsive. Full feed and level
  control remain withheld. A subsequent guarded read-only retry again passed
  server-2 TCP but timed out on the version call after 90 s; server 1 remained
  unreachable on raw TCP. No local writer remained.
- Setup report: `../../../Setup report/07n-resolved-brine-outlet-model-solver-screening.md`.

## Setup 07l hydrostatic-rest isolation (completed accepted diagnostic 2026-08-21 NZST)

- Connection diagnosis: setup 07i diverged before Node-4 `SIGSEGV` and Fluent
  server shutdown; setup 07k was already catastrophically nonphysical before
  its step-4 RPC hung. The lost gRPC connections were consequences of solver
  failure or separate network reachability, not the non-TLS warning.
- Forensic correction: 07j/07k still contained six inherited DPM injections
  and tracked `6,456` one-way parcels despite interaction being off. Hybrid
  Initialization also reported constant-pressure startup before the dense
  `y<=0 m` liquid pool was patched.
- Setup 07l cold-loaded only the accepted 07j time-zero lineage, deleted every
  injection, disabled DPM unsteady tracking and interaction, set both inlets to
  zero, changed the brine face temporarily to a wall, specified vapor operating
  density and moved the pressure reference into the gas region. Complete
  readback passed on Fluent 2024 R2 with 16 ranks.
- Ten `1e-6 s` steps completed with 20 inner iterations and separate t0/step
  1-10 case/data checkpoints. At step 10, continuity was `3.4698e-6`, domain
  velocity `4.8978e-7 m/s`, liquid inventory remained `3774.370486 kg`, net
  steam flow was `1.17e-12 kg/s`, maximum Global Courant was `1.0095e-8`, and
  no DPM/FPE/SIGSEGV/gate failure occurred.
- The lower brine wall stabilized `2090.4 Pa` above the steam pressure outlet,
  versus `2197.24 Pa` from `rho_l g h` at the measured `0.25417245 m` centroid
  depth. This supports hydrostatic head as the main reason equal `1.12 MPa`
  outlet pressure over-drained 07j.
- Decision: the mesh and pool are bounded at rest. Do not resume 07j/07k.
  Reopen the brine boundary only from this clean, DPM-deleted, relaxed lineage,
  first with zero inlets and a pressure bracket around the observed lower-face
  pressure, then ramp the inlets if the outlet-opening gate passes. This remains
  diagnostic until downstream pressure/resistance/level evidence is supplied.
- Setup report: `../../../Setup report/07l-split-inlet-hydrostatic-rest-isolation.md`.

## Setup 07j/07k transient resolved-outlet diagnostics (terminal diagnostics 2026-08-21 NZST)

- Setup 07j preparation passed from the clean 620,431-cell mesh with transient explicit VOF, Geo-Reconstruct, WFGC, fresh Hybrid Initialization, a `y<=0 m` liquid pool and exactly 16 compute ranks. EWF and sink/source terms were off. Forensic correction: DPM interaction was off but six inherited one-way injections still tracked `6,456` parcels.
- The equal-`1.12 MPa` pressure bracket failed safely at step 2 (`t=0.0002 s`): brine liquid discharge was `-4692.8688 kg/s`. Inventory change (`-4576.4867 kg/s`) and liquid boundary flux (`-4575.9488 kg/s`) closed to `0.4601%` of feed, proving gross model drainage rather than a report error. The field is not resumed.
- Setup 07k is the predefined controlled fallback. Only the brine boundary changes to a phase-specific mass-flow outlet (`116.92 kg/s` liquid outward, zero vapor); every model, mesh, initialization and numerical control remains fixed.
- 07k preparation passed and saved separate time-zero case/data. The brine command remained exactly `-116.92 kg/s`, but step 3 developed grossly nonphysical fields: inlet pressure `3.7445e9 Pa`, steam-outlet pressure `-4.1102e13 Pa`, steam-outlet velocity `5.2599e6 m/s` and domain velocity `7.2714e4 m/s`.
- The step-4 RPC then hit its guarded two-hour idle timeout and is uncredited. No controller remains and 07k must not be resumed. Correct prescribed outlet mass flow did not cure the transient startup instability.
- Results remain diagnostic; mesh convergence, DPM, EWF and performance claims remain blocked. A physically defensible downstream pressure/resistance or level-control condition is required before another production branch.
- Setup reports: `../../../Setup report/07j-split-inlet-resolved-brine-outlet-transient-vof.md` and `../../../Setup report/07k-split-inlet-transient-vof-massflow-brine-outlet.md`.

## Setup 07i WFGC-only resolved-outlet sensitivity (failed diagnostic; corrected 2026-08-19 NZST)

- Decision: run one clean, non-overwriting sensitivity of setup 07h with only Warped-Face Gradient Correction changed from disabled to enabled/fast and verified before initialization.
- Controls: original 620,431-cell brine-outlet mesh, authoritative settings, `y<=0 m` liquid pool, equal `1.12 MPa` outlet pressures, fresh Hybrid Initialization and all carrier physics unchanged. DPM, EWF and sink remain off.
- Safety gates: save initialized/25/250 checkpoints separately; at iteration 250 stop if brine liquid outflow exceeds three liquid feeds, mixture imbalance exceeds 100% or liquid imbalance exceeds 200%. Never resume the failed 07h field.
- Implementation: dedicated preparation, qualification, status and single-controller supervisor scripts are compiled; all 29 local regression tests pass. The fail-closed runtime gate now parses Fluent's parallel connectivity node IDs rather than misreading the hardware-core denominator.
- Process-count correction: the attempt-8 roster contains `n0..n15`, and the title bar states `16-processes`. Values such as `16/20` mean core index 16 on a 20-hardware-core machine. Attempt 8 therefore used the required 16 solver processes; its clean mesh/settings/WFGC/Hybrid/pool preparation is valid controlled evidence.
- Attempt-8 qualification: catastrophic numerical failure during the first 25-iteration block. Continuity grew from `3.2024` at transcript iteration 16 to `6.9888e14` at iteration 20; the supplied GUI photograph records iteration 21, Node-4 SIGSEGV, connection reset and server shutdown. Zero complete blocks were credited and no divergent checkpoint was saved.
- Current connection/controller state: the restarted endpoint was verified at `2026-08-19 13:27 NZST` as Fluent 2024 R2, `Status.SERVING`, with 16 solver processes (`n0..n15`) on 20 hardware cores. No case is loaded and no setup-07i controller is active.
- Decision: setup 07i is terminal `Diagnostic / catastrophic numerical failure`. Do not resume its initialized state or repeat the identical steady WFGC case; WFGC did not cure the formulation.
- Next physical branch: implement setup 07j transient VOF/liquid-inventory qualification with a defensible downstream brine pressure, prescribed outward flow or resistance condition. DPM, EWF, mesh convergence and performance claims remain blocked.
- Setup report: `../../../Setup report/07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md`.

## Setup 07h Resolved Brine Outlet with Initial Liquid Pool (stopped diagnostic 2026-08-16 NZST)

- Decision: retain the physical brine-outlet geometry and remove the empirical sink. Repeat the source-free case from the clean mesh with an explicit lower liquid reservoir initialized below `y=0 m`.
- Rationale: setup 07g's dry Hybrid start reached a verified iteration-500 state with both net outlet flows outward, but the brine face discharged `42.680678 kg/s` vapor while admitting `5.512239 kg/s` liquid. This is the wrong phase route and the later live field diverged.
- Fixed setup: steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off, `116.92/80.69 kg/s` phase feeds, equal `1.12 MPa` pressure inputs at steam/brine outlets, minimum-phase-averaged operating density, and DPM/EWF/sink off.
- Geometry evidence: brine face centroid `y=-0.25417245 m` and equivalent radius about `0.252 m` place the pipe crown near `y=0 m`; this supports the initial-pool patch but is not measured water-level validation.
- Preparation result: accepted from the clean mesh. The `y<=0 m` cell-register patch changed domain-average liquid VF from `0` to `0.15826588`; setup readback passed and separate initialized case/data were saved. DPM/EWF/sink remained off.
- Early routing: iteration 25 sent vapor outward through the steam outlet and liquid outward through the brine outlet; brine discharge was `97.32%` liquid. This is diagnostic phase-route evidence only.
- Terminal result: the verified iteration-250 state was already nonphysical (`-3304.7817 kg/s` brine liquid, `1602.99%` mixture imbalance). The next block reached residual row 292, then AMG pressure/k/VOF divergence and a floating-point exception. It is uncredited; the post-FPE state is saved under an explicit unverified label.
- Numerical-method finding: Fluent recommended Warped-Face Gradient Correction for the polyhedral mesh after settings import, but live readback shows `enable=False`. This may have reduced robustness/gradient accuracy, although it does not explain away the physical boundary uncertainty or prove causation.
- Classification: `Diagnostic / unresolved`; no controller is continuing this branch and no convergence, efficiency or mesh-independence claim is permitted.
- Next action: before changing formulation, permit one clean controlled numerical sensitivity with Warped-Face Gradient Correction enabled/read back and every other 07h input unchanged. If it still develops nonphysical drainage or instability, move to transient physical-time inventory with a defensible downstream brine pressure/level condition. Do not resume the failed steady field or tune pressure merely to force closure.
- Setup report: `../../../Setup report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md`.

## Setup 07g Resolved Brine-Outlet Qualification (stopped diagnostic 2026-08-13 NZST)

- Status: `Stopped at verified iteration 500; diagnostic/unresolved`.
- New geometry: `brine-outlet-620kcells.msh.h5` contains a dedicated `0.19936247 m2` brine pressure face and no legacy `bottom` wall. The mesh has 620,431 cells on 16 partitions, minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258` and no negative-volume error.
- Clean lineage: original mesh plus authoritative `mesh_study_settings.set`, explicit zone-name normalization, fresh Hybrid Initialization and no saved sink/accumulated solution field.
- Verified setup: steady Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off, SIMPLE/PRESTO, phase feeds `116.92/80.69 kg/s`, DPM/EWF off and no source UDF.
- First brine BC: pressure outlet at `1.12 MPa`, equal to the steam-outlet reference pressure, with liquid-only backflow specification. This is a diagnostic first pressure bracket, not a known downstream brine-system pressure.
- Readback: zero pre-initialization or initialized validation errors; full fingerprint `223fd8d3...b30`; separate iteration-zero case/data saved.
- Controller recovery: Fluent's transcript proves the first 25 iterations, while the PyFluent monitor stream returned no points. The iteration-25 case/data was saved separately and the active single controller now accepts either monitor-stream or Fluent-transcript residual-row proof for each complete block.
- Iteration-250 recovery: transcript rows proved the 25-to-250 block and a correctly labelled checkpoint was saved. Post-processing rejected the non-Fluent alias `phase-2-volume-fraction`; the allowed field `phase-2-vof` is now used and execution has resumed from 250 with manifest-before-metrics recovery ordering.
- Iteration-500 diagnostic: both outlets discharge net mixture (`steam -38.76477`, `brine -37.179327 kg/s`), but the brine phase split is wrong: vapor leaves at `42.680678 kg/s` while liquid enters at `5.512239 kg/s`. Mixture/liquid imbalance are `61.5687%/104.7145%`. The next requested block produced only 62 residual rows and was not credited; the later overflow-scale live field is excluded. The iteration-500 pair is the terminal verified checkpoint.
- Acceptance: complete mixture/vapor/liquid balance no greater than 0.5%, correct integrated discharge direction at both outlets, final-window dominant-flow/pressure drift no greater than 0.5%, velocity/vorticity/inventory drift no greater than 1%, and bounded residuals.
- Scope: one-mesh carrier boundary qualification only. Mesh convergence, DPM, EWF and separator performance remain closed until this gate passes.
- Setup report: `../../../Setup report/07g-split-inlet-resolved-brine-outlet-qualification.md`.
- Status: `../../../PyAnsys/scripts/connection/check_setup07g_status.py`.

## Setup 07f Sink Thickness/Rate Matrix (running 2026-08-11 NZST)

- Status: `Paused — Fluent report/readback stream degraded`; the first case is
  complete, while clean cases 2 and 3 remain pending. No setup-07f controller
  is active.
- Purpose: determine whether the local-supply limit observed in setups 07d/07e
  moves when the liquid-only source has access to a taller bottom-local band,
  and then measure the additional effect of a faster fixed coefficient.
- Queue: `(0.2803305 m, tau=0.020 s)`, `(0.2803305 m, tau=0.005 s)` and
  `(0.4204958 m, tau=0.005 s)`, executed sequentially with a hard stop after
  any uncertain case-level failure.
- First preflight: Fluent 2024 R2, 16 partitions, 5,335,623 cells; exact
  runtime readback `thickness=0.28033050723644937 m`, `tau=0.02 s`, `R=0`;
  mask `184,145` cells and `0.88704756 m3`; separate fresh-Hybrid ramp-zero
  case/data saved before iteration.
- Scheduling correction: the superseded `v1` attempt exposed an inherited
  per-iteration full-mesh mask rebuild costing roughly `8-11 min/iteration`.
  It was stopped after 79 startup iterations and is not reused. A live smoke
  check of the equivalent fixed-mask/on-demand schedule completed in about
  `6.17 s/iteration` with unchanged RP controls and DPM off; the formal queue
  restarted under non-overwriting `v2_staticmask` labels.
- Connection recovery: the first `v2_staticmask` case recorded `2,500`
  cumulative / `1,500` full-strength iterations before the next 250-iteration
  gRPC request timed out. Fluent remained healthy, so this is a transport
  failure rather than solver divergence. The endpoint had sink
  `44.199736 kg/s`, pressure drop `25.1905 kPa`, continuity about `0.20` and
  zero passing stability windows. The newer partial live state is preserved
  separately with an unverified label. The clean-origin queue restarted under
  non-overwriting `v3_rpc25` labels with all ramp/full-strength calls limited
  to 25 iterations; no partial `v2` solution is reused.
- Current execution: doubled-band `tau=0.020 s` completed `3,000` cumulative /
  `2,000` full-strength iterations with sink `53.133696 kg/s`, pressure drop
  `26.7892 kPa`, inventory `64.64961 kg`, corrected liquid imbalance
  `54.5553%` and zero passing stability windows. The next `tau=0.005 s`
  attempt recorded `2,375/1,375` iterations before its manifest/log stalled
  while Fluent stayed healthy. Its live field is preserved as unverified
  evidence. A sandbox permission error was initially misread as process
  absence, briefly creating duplicate preflight controllers. An escalated
  process audit found and terminated every duplicate/stalled tree before new
  production iterations; the `v4` fingerprint guard rejected the interleaved
  preflight. Cases 2 and 3 now restart clean with one audited controller under
  `v5_single_controller` labels, and case 1 is not rerun.
- Current blocker: v5 actually passed full parity/mask preflight and saved a
  clean ramp-zero checkpoint; it was stopped before production after a busy
  Fluent session was incorrectly interpreted as an unavailable health service.
  The final single-controller v6 retry connected and restored the clean parent,
  but Fluent returned no captured text for mandatory mesh size/check/quality
  reports. The parser stopped the run before initialization or iteration. All
  controller trees are audited absent. Restart or repair Fluent before retrying
  cases 2 and 3; do not bypass the report/readback gate.
- Latest read-only recheck: Fluent health reports `Status.SERVING`, but an
  independent mesh-size/check/quality capture still returns no text and fails
  the parser. Connectivity has recovered; the report/readback stream has not.
- Unchanged controls: steady pressure-based Mixture, vapor primary/liquid
  secondary, RNG k-epsilon, gravity on, Energy off, SIMPLE/PRESTO, inlets
  `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, bottom wall and DPM/EWF off.
- Iteration contract per case: guarded 1,000-iteration ramp plus 1,000 minimum
  and 2,000 maximum full-strength iterations; 25-iteration RPC blocks, stability
  windows and source/pressure/DPM safety guards; all checkpoints saved under
  new non-overwriting names.
- Evidence limit: diagnostic parameter sensitivity only. Even if a numerical
  window passes, the source does not define brine-outlet hydraulics and cannot
  validate separator performance, a free surface or physical-time behavior.
- Setup report: `../../../Setup report/07f-split-inlet-sink-thickness-rate-matrix.md`.
- Output: `../../../PyAnsys/output/split_inlet_sink_thickness_rate_matrix_20260811/`.

## Setup 07e Adaptive Mass-Balance Sink Control (completed 2026-08-11 NZST)

- Status: `Completed diagnostic / unresolved at maximum iteration budget`; zero acceptance windows passed.
- Purpose: determine whether explicitly commanding the missing `116.92 kg/s` liquid discharge can close the balance and whether pressure, velocity, inventory and residual histories then stabilize.
- Feedback law: every 100 iterations, set `tau_next = clamp(M_liquid,band/116.92, 0.002, 0.2) s` while retaining the qualified liquid-only source law and the complete `0.1401652536 m` band.
- Preserved controls: verified prepared 900k checkpoint and fingerprint, fresh Hybrid Initialization, Mixture/RNG k-epsilon carrier physics, gravity on, Energy off, SIMPLE/PRESTO, phase feeds `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, bottom wall and DPM/EWF off.
- Execution: guarded 1,000-iteration ramp followed by 1,000 minimum and 2,000 maximum full-strength iterations, 100-iteration feedback blocks and separate non-overwriting checkpoints.
- Terminal endpoint: the controller completed `3,000` cumulative / `2,000`
  full-strength iterations. At bounded `tau=0.002 s`, the achieved sink was
  `50.954294 kg/s` (`43.6%` of command), leaving `56.419329%` corrected liquid
  imbalance. Pressure drop/domain inventory were `26.7252 kPa`/`65.007547 kg`.
  The band held only `0.101909 kg` against `0.23384 kg` required to meet the
  command at minimum tau, so the controller remained locally capacity limited.
- Convergence result: continuity/liquid-VF residuals ended at
  `0.254617`/`7.53207e-4` and increased `3.634%`/`8.463%` over the final
  100 iterations. Final-500 pressure/sink/inventory drift was
  `5.8506/26.1894/13.3524%`; outlet/domain velocity drift was
  `3.3033/6.9068%`. Vapor flow and vorticity alone passed their drift limits.
- Preservation and live-state safety: start, ramp-complete, R1=1000, R1=2000
  and final case/data pairs are verified separately. The final sink ramp is
  zero, DPM interaction is off, and no DPM injection update or tracking ran.
- Lineage audit: setup 07e and accepted setup 07d match with `0.000000%`
  difference in all controlled pressure/inventory/outlet-flow/velocity fields
  at exact saved iterations 100, 200, 350, 500, 750 and 1000 while the band is dry.
- Interpretation rule: this is an empirical global feedback controller operating through a local volumetric source. Even exact numerical closure would not supply physical brine-outlet hydraulics or validate separator performance.
- Decision: freeze further local band/tau tuning. Add a resolved brine outlet
  and qualify one medium mesh before restarting the mesh ladder, DPM or EWF.
- Setup report: `../../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`.
- Output: `../../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/`.

## Setup 07d Capacity-Matched Thick-Sink Diagnostic (completed 2026-08-10 NZST)

- Status: `Completed diagnostic / unresolved at maximum iteration budget`; zero acceptance windows passed.
- Controlled change: same clean prepared 900k state, band, physics, boundaries, initialization, numerics and DPM-off state as 07c; only `tau` changed from `0.1` to `0.02 s`.
- Execution: 1,000 guarded ramp plus 2,000 full-strength iterations; start, ramp, R1 = 1,000, R1 = 2,000 and final case/data preserved separately; final ramp reset to zero.
- Endpoint: sink `46.9874 kg/s` (`40.19%` of liquid feed), corrected liquid imbalance `59.8122%`, mixture source-inclusive imbalance `35.1679%`, domain inventory `66.6560 kg`, band inventory `0.93975 kg`, pressure drop `26.8901 kPa`, continuity `0.229682`.
- Final-500 drift: pressure `6.618%`, sink `23.044%`, inventory `14.120%`, outlet/domain velocity `3.161/6.901%`; vapor outlet and vorticity alone were stable.
- Interpretation: a 5x coefficient produced only a 2.09x endpoint sink because liquid available inside the band fell. Stronger local removal improves closure but does not establish a fixed, conserved steady state or replace outlet hydraulics.
- Setup report: `../../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`.
- Output: `../../../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/`.

## Tuesday Meeting Evidence Package (ready 2026-08-10 NZST)

- Status: `Ready / diagnostic evidence only`.
- A meeting brief, one-page decision summary, matched liquid-VF and pressure contours, sink-mask image, verified carrier pathlines, physical-monitor plots, residual plots and machine-readable provenance are available under `../../../PyAnsys/output/setup07_meeting_visuals_20260811/`.
- The strongest matched evidence is setup-07a 900k iteration 4000 versus 6000: liquid inventory rises `64.4%` and pressure drop rises `9.7%` while the liquid-rich wall region and pressure field visibly change.
- The setup-07c thick sink removes `22.49 kg/s`, only `19.2%` of the liquid inlet, and leaves `94.43 kg/s` unclosed in the source-inclusive steady balance. Continuity and primary physical monitors remain outside acceptance limits.
- Setup 07d increases the source coefficient fivefold but removes only `46.99 kg/s` (`40.2%` of the liquid feed), with `59.81%` liquid imbalance and failed pressure/inventory/sink stability. Terminal setup 07e improves removal only to `50.954294 kg/s` (`43.6%`) and still fails closure, physical-monitor and continuity gates. Figures `10-27` now include fixed/adaptive histories, residuals, outlet recirculation, capacity limits, matched spatial comparisons, preliminary outlet sizing and the recommended rebuild sequence.
- Geometry-planning figures `24-25` use the authoritative liquid feed and Fluent-read density to provide a continuity-only outlet-area envelope and an official-guidance boundary-condition sequence. They recommend a pressure outlet when downstream static pressure is defensible, retaining a `116.92 kg/s` mass-flow outlet only as a strictly outward diagnostic bracket; neither artifact is a final outlet design. Figure `26` separately shows why the active adaptive source remains capacity-limited at its minimum tau: the band must contain `0.23384 kg` to remove the full liquid feed under the implemented source law.
- Interpretation: the graphics strengthen the existing formulation diagnosis; they do not establish physical-time accumulation, mesh convergence, separator efficiency, a free surface or validation.
- Graphics were exported without new iterations or model mutation. The session
  was restored to the setup-07e ramp-reset final and DPM read back off. Core
  liquid-volume-fraction, pressure and liquid-inlet carrier-pathline images are
  accepted; optional sink-mask and steam-inlet pathline exports are explicitly
  unavailable/not accepted after saved-state reload and are not fabricated.
- Meeting recommendation: implement and qualify a resolved brine outlet on the medium 900k mesh before any new mesh ladder, DPM or EWF work.
- Primary handoff: `../../../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md` and the dynamic opener `../../../PyAnsys/output/setup07_meeting_visuals_20260811/27_tuesday_brine_outlet_action_summary.png`; figure 13 remains the preceding fixed-sink evidence summary.

## Setup 07c Thickened-Sink Qualification (completed 2026-08-09 NZST)

- Status: `Completed diagnostic / unresolved at maximum full-strength budget`; zero acceptance windows passed.
- Branch: setup `07c`, a controlled layer-thickness sensitivity child of setup `07b` for the spiral/split-inlet carrier model.
- Controlled origin: clean original `mesh-900k.msh` (5,335,623 cells), authoritative `mesh_study_settings.set`, normalized fingerprint `424a9bf0...c5`, fresh Hybrid Initialization, Fluent 2024 R2 with 16 partitions, and no saved accumulated solution data.
- Unchanged carrier stack: steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, Energy off, gravity `(0,-9.81,0)`, SIMPLE/PRESTO, liquid/vapor inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`, `bottom` retained as wall and DPM off.
- Only sensitivity change: replace the setup-07b one-cell sink mask with a fixed `0.1401652536 m` bottom-local band, nominally 16 one-cell layers. The mask covered 92,058 cells and `0.44378932 m3` across the full bottom-local band; `tau=0.1 s` and the liquid-only/carried-momentum source law were unchanged.
- Execution: completed a guarded 1,000-iteration ramp plus 2,000 full-strength iterations in 250-iteration blocks. A startup-guard false stop at R1 = 250 was recovered from a separately saved pair; no evidence was overwritten. Formal R1 = 1000 and 2000 checkpoints and a separate final ramp-reset-zero pair were verified.
- Endpoint: sink `22.4882 kg/s`, domain liquid inventory `71.7785 kg`, pressure drop `27.1372 kPa`, steam-outlet vapor/liquid `81.2960/0.000102861 kg/s` out, corrected source-inclusive liquid imbalance `80.7661%`, source-inclusive mixture imbalance `47.4802%`, continuity `0.191551`, DPM off.
- Final-500 result: pressure drift `8.53%`, sink `29.99%`, inventory `16.93%`, outlet velocity `4.24%` and domain velocity `6.78%` failed. Vapor outlet (`0.0362%`) and vorticity (`0.860%`) passed their drift limits, but continuity failed the residual-level gate.
- Interpretation: thickening increased sink magnitude by about `13-16x` versus setup 07b at equal R1 counts, yet removed only `19.23%` of liquid inflow at the endpoint. Inventory and pressure remained iteration-dependent, so the local sink does not enforce Purnanto's constant water level.
- Accounting correction: setup-07b/07c raw `liquid_source_augmented_*` fields double-count the phase-2 sink because Fluent's phase-2 Net already includes that cell-zone source. Use `liquid_imbalance_percent` (`80.7661%` for 07c; `91.1909%` for 07b). Mixture source-augmented fields remain usable. No run classification changes.
- Evidence label: `Accepted diagnostic layer-thickness sensitivity`; not accepted for steady carrier performance, validation, mesh independence, GCI, DPM or EWF.
- Next action: when geometry editing is available, implement and qualify a resolved brine outlet on one medium mesh before restarting mesh convergence or particle/wall-film work.
- Setup report: `../../../Setup report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md`.
- Result report: `../../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/QUALIFICATION_RESULT.md`.

## Setup 07b Constant-Water-Level Sink Qualification (completed 2026-08-08 NZST)
- Status: `Implementation accepted; tau=0.1 s physical qualification completed diagnostic / unresolved at maximum iteration budget`.
- Branch: setup `07b`, a liquid-discharge diagnostic child of setup `07` created in response to the closed-bottom accumulation demonstrated by setup `07a`.
- Method: keep `bottom` as a no-slip wall and remove only phase-2 liquid from the directly adjacent cell layer with `S_l = -rho_l alpha_l R/tau`; remove the carried mixture momentum; apply no vapor, energy or DPM source.
- Fluent implementation: compiled UDF `lib07b_cwl_bdfa31b0ec_r4_clean1` in the clean prepared case, five UDMs, liquid mass hook on phase 2, x/y/z momentum hooks on mixture, global Adjust mask, and complete hook/readback persistence after cold reload.
- Smoke evidence: on the 5,335,623-cell 900k mesh, one diagnostic iteration at `R=0.05`, `tau=0.1 s` marked 5,438 cells, integrated a `0.027726243 m3` layer, measured `0.959465 kg` liquid and produced `-0.47973263 kg/s`, consistent with the implemented equation. Ramp was reset to zero and a separate case/data pair was saved.
- Unchanged carrier stack: steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, Energy off, gravity `(0,-9.81,0)`, `116.92/80.69 kg/s` liquid/vapor inlet, `1.12 MPa` steam outlet, 16 processes, DPM off.
- Production-start preparation: accepted. The workflow loaded clean original `C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh` (SHA-256 `353bf13c...afef`), applied the authoritative case-only/settings definition, matched normalized fingerprint `424a9bf0...c5`, hooked at ramp zero and performed fresh Hybrid Initialization. No saved solution data was loaded and zero qualification iterations ran.
- Evidence-use rule: accepted for UDF compilation, persistence, phase scoping, source sign/integration and safe checkpointing only. Not accepted for a steady solution, sink-time-scale selection, separator efficiency, validation or mesh convergence.
- Qualification result: completed `500` ramp iterations plus `6,000` full-strength iterations on the clean 900k field. Zero acceptance windows passed. At R1 `6000`, the sink was `8.06194 kg/s`, domain liquid inventory `191.836 kg`, corrected source-inclusive liquid imbalance `91.1909%`, pressure drop `34.8475 kPa`, and continuity residual `0.279243`.
- Final-window result: pressure drift `2.60%`, sink drift `17.89%`, liquid-inventory drift `10.07%`, domain-velocity drift `1.76%` and vorticity drift `1.42%`; residual-level and residual-trend gates also failed. Stable vapor throughput did not establish a steady carrier solution.
- Interpretation: the one-cell local inventory-proportional sink executes correctly but removes far less than the `116.92 kg/s` liquid inlet. The domain continues filling/redistributing, so the abstraction is not qualified as a constant-level steady model.
- Current Fluent state: the completed R1 `6000` field is loaded with the UDF ramp reset to zero; no calculation is running and DPM remains off.
- Prepared case/data: `C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\clean_900k_preparation\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.cas.h5/.dat.h5`.
- Completed run: `mesh-900k_tau0p100_qualification_v1`; verified separate R1 checkpoints at 1,000 through 6,000 and a second final ramp-reset-zero pair. A controller disconnect was recovered from a separately saved live checkpoint and reconciled without overwriting evidence.
- Evidence label: `Completed diagnostic / unresolved`. DPM was off throughout. No separator-efficiency, validation, mesh-independence, GCI, DPM or EWF claim is allowed.
- Setup report: `../../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`.
- Machine summary: `../../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/implementation_summary.json`.
- Qualification report: `../../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/mesh-900k_tau0p100_qualification_v1/QUALIFICATION_RESULT.md`.
- Next action: create a new steady branch with a resolved brine outlet and qualify it on one medium mesh before any mesh ladder, DPM or EWF work. Further tau/layer tests, if run, are diagnostic sensitivity only.

## Split-Inlet Carrier Mesh Study Diagnostic Closure (2026-08-05)
- Status: `Completed diagnostic — iteration independence and mesh independence unresolved`.
- Selected branch: setup `07a`, carrier-only child of the setup `07` spiral/split-inlet model. Setup `08c` is not the baseline for this study.
- Execution authority: `partial_solution_diagnostic_20260801.cas.h5` plus `mesh_study_settings.set`, with complete Fluent readback and accepted settings fingerprint. The historical `FFF.1-2` archive remains lineage evidence only.
- Reference condition: approximately `1600 kJ/kg`, liquid `116.92 kg/s`, vapor `80.69 kg/s`, and outlet gauge pressure `1.12 MPa`.
- Frozen physics: Fluent 2024 R2, 16 processes, steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off, SIMPLE/PRESTO!, DPM off.
- Geometry: `liquidinlet` and `steaminlet` are distinct split-inlet regions; `steamoutlet` is the only pressure outlet; `bottom` and `wall-fluid` are verified walls.
- Mesh completion: all seven meshes completed 3000 formal iterations and preserved initialized, 1000-, 2000- and 3000-iteration case/data pairs. Actual cells range from `1,688,678` to `13,370,267`.
- Formal result: vapor outlet flow is stable near `81.45 kg/s`, but every mesh fails pressure and/or velocity iteration-stability criteria. Fine-grid mesh changes cannot be separated from within-run drift.
- 900k diagnostic: a separately saved extension reached 6000 iterations. Final-500 pressure drift remained `4.61%`; outlet/domain velocity and vorticity also remained above limits.
- Direct inventory evidence: domain liquid inventory increased from `104.05 kg` at iteration 4000 to `171.03 kg` at 6000 (`+64.37%`), while pressure drop increased from `31.03` to `34.05 kPa`.
- Interpretation: the closed-bottom steady calculation is undergoing liquid filling/redistribution rather than approaching a fixed-inventory steady state. The accepted geometry limitation does not create a steady storage term.
- Evidence-use rule: all mesh endpoints and the 900k extension are `Diagnostic`; carrier quality/liquid carryover are trend-only; no GCI, mesh-independence, separator-efficiency or validation claim is permitted.
- Fluent state: the verified 900k iteration-6000 case/data pair is loaded; no further calculation is running and DPM remains off.
- Study definition: `../../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`.
- Final diagnostic report: `../../../PyAnsys/output/split_inlet_mesh_convergence_20260801/STUDY_DIAGNOSTIC_CLOSURE_20260805.md`.
- Next action: freeze setup 07a. If steady performance is required, define a new branch with a physically credible liquid discharge and qualify one medium mesh before repeating a mesh ladder. Use a closed-bottom transient branch only for an explicitly finite-time filling question.

## July 2026 Purnanto Replication Campaign
- Date: 2026-07-29.
- Objective: replicate six Purnanto enthalpy conditions for the available baseline/Bangma-target model and the spiral-inlet model, using 1500 evidenced carrier-flow iterations and nine-bin Harwell DPM tracking.
- Completed baseline branch: all six setup `08b` cases contain injection-level DPM exports and passing fate-mass audits. Provisional qualities are `99.7746%`, `99.6718%`, `99.7304%`, `99.7753%`, `99.8144%`, and `99.8507%`.
- Completed spiral branch: all six setup `08c` cases contain residual histories from iteration `1` to `1500`, full pre/post injection readbacks, and passing fate-mass audits. Provisional qualities are `99.9679%`, `99.9678%`, `99.9668%`, `99.9795%`, `99.9786%`, and `99.9724%`.
- Evidence qualification: Cases 2-6 of setup `08b` preserve standalone 1500-point residual CSVs. Case 1 preserves block-by-block advancement to 1500 in its manifest but lacks a mirrored standalone residual CSV.
- Scientific blockers: fixed iteration completion is not convergence proof; baseline incomplete DPM mass remains large; the exact geometry lineage, inherited DPM tracking controls, one-way interaction state for historical baseline results, and steam-quality convention remain unresolved.
- Automation correction: future sweeps now verify phase materials and one-way DPM before mutation, fail on DPM update/report failure, parse Fluent's `Final` DPM mass-flow column, and disable particle-count mass fallback by default.
- Operational blocker: remote PyFluent control still depends on an awake Mac and continuous VPN/Wi-Fi connectivity.
- Handoff: the full operator workflow, recovery contract, result snapshot, and mesh-convergence starting protocol are consolidated in `../../../PyAnsys/docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md`.
- Technical records: `../technical/purnanto-enthalpy-dpm-replication.md` and `../technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md`.
- Setup records: `../../../Setup report/08b-purnanto-baseline-enthalpy-dpm-sweep.md` and `../../../Setup report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md`.

## Prior Snapshot (2026-06-10)
- Date: 2026-06-10
- Phase: direct Purnanto-recreation reset plus retained setup `07` archive context
- Focus: rebuild the paper-style Purnanto setup on the current project path using one mixed steam-water inlet rather than the later split-inlet branches.
- Current issue: setup `07` has promising apparent steam-line carryover; bottom truncation/no brine outlet/no water pool is now accepted as out of scope for this project branch.
- Current mesh scale: professional setup `07` run reported at approximately `1.3M` nodes and `7.6M` cells; older project mesh scale was approximately `1.8M` nodes.
- Current controlled setup change: new setup `08` returns to the one-inlet Purnanto mass-flow package; older split-inlet and velocity-inlet branches remain comparison context only.
- Latest diagnostic result: `PLS-PRO-2026-06-03-A` reports very low apparent liquid carryover at the steam outlet (`0.03663388722044243 kg/s`, `0.03135 %` of liquid inlet if interpreted as carryover magnitude). Treat this as a scoped steam-carryover diagnostic, not a full brine-drainage balance.
- New baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05` loaded `purnanto-setup.cas.h5` and `purnanto-setup-5000.dat.h5`; the live case matches the core Purnanto baseline solver stack and records a `2,964,593`-cell tetra mesh with minimum orthogonal quality `0.277635`.
- New direct-rebuild branch: setup `08` now records the paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package so the project can return to the closest Purnanto recreation before judging split-inlet alternatives.
- Retained alternate branch: setup `08a` preserves the planned student-edition outlet-extension trial as a comparison path from setup `07`, not as the current primary rebuild target.
- New PyFluent result: the local `trial3.msh` one-inlet reconstruction now launches, creates manual water vapor/liquid materials, hybrid-initializes, and completes a `10`-iteration smoke test through the script in `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`.
- New hardened PyFluent result: the same one-inlet reconstruction path now runs on `trial4.msh` with clean `Operating Pressure = 0 Pa`, confirmed 2026 R1 numerics paths, mass-flow sanity reporting, and both case/data writes.
- New longer PyFluent result: a controlled `500`-iteration `trial4` diagnostic run has now completed on the one-steam-outlet branch with chunked reporting, checkpointing, vapor recovery approximately `1.0092`, liquid carryover approximately `3.97e-25`, and a rough residual-history plot recovered from the Fluent transcript.
- Active setup branch: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md` is now the selected direct baseline-rebuild branch; `../../../Setup report/07-pure-phase-split-actual-area.md` is retained as a comparison-only split-inlet branch.
- Secondary comparison branch: `../../../Setup report/08a-steam-outlet-extension-student-trial.md` remains available for the downstream steam-outlet boundary-placement diagnostic if that question is revived.
- Archive guard: do not archive chats that were active on or after `2026-05-25`; older chats can be archived only after their durable outcomes are confirmed in the wiki and setup-report files.

## What Is Done
- Rough literature overview completed.
- Baseline geometry provided and run attempts started.
- Initial non-convergence signal observed.
- Baseline steady two-phase setup defined in Fluent (pressure-based, RNG k-epsilon, Mixture model, gravity, isothermal assumption).
- A first project-specific inlet-regime change has now been defined conceptually: split inlet with wall-side liquid and inner-side steam.
- Geometry context has been clarified: this split-inlet plan is for the **spiral-inlet** baseline case.
- Mesh density increased from earlier approximately 300k-node run to approximately 1.8M nodes.
- Team split clarified: partner is working on validation/parameter-sweep comparison against analytical data, while Shuhei's immediate lane is now setup `07` steam-carryover/DPM post-processing.
- Current attempted setup history includes two-phase inlet design, brine outlet representation, and a downstream water-pool child case, but setup `07` now explicitly treats bottom liquid handling as out of scope.
- Current usable simulation evidence is limited to documented above-threshold or professional-license diagnostics: `FFF-2` at approximately `1020` iterations, `MWH-WP-2026-05-07-A` at approximately `3500` iterations, and `PLS-PRO-2026-06-03-A` as the newest professional setup `07` flux diagnostic.
- Parent no-water-pool run `FFF-2`, Phase 0 outlet audit, and `FFF-2-OP0` remain historical troubleshooting evidence for older brine-outlet branches.
- A report-facing calculation scaffold now records the actual inlet-half area `2.6209e5 mm2 = 0.26209 m2`, giving total liquid inlet `115.59 kg/s`, total steam inlet `79.77 kg/s`, and total inlet flow `195.36 kg/s` for the mixed wet-half velocity-inlet setup.
- A new complete two-phase no-brine-outlet setup report now converts the same actual-area basis into one full-inlet velocity condition: `26.81 m/s`, liquid volume fraction `0.009328`, steam volume fraction `0.990672`, full inlet area `0.52418 m2`, calculated liquid inlet `115.59 kg/s`, steam inlet `79.77 kg/s`, and total inlet `195.37 kg/s`.
- The pure-liquid/pure-steam equal-velocity split has now been recalculated using Purnanto's `1600 kJ/kg` target phase flows and the current `0.724 m x 0.724 m` inlet: common velocity `27.118 m/s`, liquid strip area `0.0048896 m2`, steam area `0.5192864 m2`, and split line `0.006754 m` from the liquid-side edge if split along `x`.
- A separate fixed-velocity pure-phase split report now keeps Purnanto's reported spiral-inlet velocity `26.81 m/s`; with the current `0.724 m x 0.724 m` inlet and the same `0.006754 m` liquid-side split, the expected inlet mass flows are liquid `115.59 kg/s`, steam `79.77 kg/s`, and total `195.37 kg/s`.
- Active decision: for the next pure liquid / pure steam split-inlet case, use the current-area exact-mass velocity `27.118 m/s`, not the fixed reported-velocity `26.81 m/s` alternate.
- New active setup report created for the pure liquid / pure steam actual-area velocity-inlet case with turbulence intensity `2.10999999 %`, liquid hydraulic diameter `0.01338 m`, and steam hydraulic diameter `0.72061 m`.
- Two rough student-edition pure-phase split diagnostics are now documented against that same inlet sizing. Setup 2 reduced steam-line liquid carryover from `10.67 kg/s` to `7.73 kg/s`, improving implied carryover-based efficiency from `90.87 %` to `93.39 %` and steam-outlet dryness from `88.39 %` to `91.33 %`, but both remain non-converged low-mesh diagnostics only.
- Professional-license setup `07` flux diagnostic is now documented: mesh approximately `1.3M` nodes and `7.6M` cells; liquid inlet `116.8523 kg/s`; steam inlet `81.6395 kg/s`; steam outlet steam `86.2934 kg/s`; steam outlet liquid `0.03663 kg/s`.
- New literature anchors are now linked into the project layer: Pointon et al. 2009 adds a geothermal HP-separator CFD scale/pressure-drop/scrolled-entry check, and Chen et al. 2025 adds an experiment-backed `RSM-DPM` separator-method benchmark for any later turbulence-model sensitivity decision.
- Newest documented run: `PLS-PRO-2026-06-03-A`, based on `Setup report/07-pure-phase-split-actual-area.md`.
- Newest baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05`, recorded in `../../../Setup report/00a-purnanto-setup-5000-live-audit.md`.
- New direct-rebuild report: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`.
- Retained comparison report: `../../../Setup report/08a-steam-outlet-extension-student-trial.md`.
- New local automation note: `../technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`.
- New local reusable doc: `../../../PyAnsys/docs/findings/LOCAL_ONE_INLET_SMOKE_TEST.md`.
- New residual artifact set: `trial4-purnanto-recon-500-residuals.png` and `trial4-purnanto-recon-500-residuals.csv` now exist beside the `500`-iteration case/data outputs.
- Older water-pool run `MWH-WP-2026-05-07-A` showed more plausible swirl after 3500 steady iterations but is retained only as historical troubleshooting evidence.
- New split-inlet mesh workflow result: the updated `mesh-trial1.msh` now reopens with two separate velocity-inlet zones, but the exported baseline still fails the strict required-zone contract because Fluent currently shows `liquidinlet`, `steaminlet`, and no separate `wall-smooth_spiral_separator` boundary in the reopen audit.
- New active mesh workflow artifacts: `../../../PyAnsys/input/required-zones-mesh-trial1.txt` plus `../../../PyAnsys/output/meshdat-semi-automated/workflow-report.md`.

## What Is In Progress
- Transitioning from the completed provisional replication sweeps to a single-geometry, representative-case mesh-convergence study.
- Auditing the exact baseline mesh identity before defining coarse, medium, and fine meshes.
- Capturing incomplete-particle locations near the cylinder-to-dome transition.
- Preserving the full DPM interaction, tracking, wall-fate, and face-normal setup in future manifests.
- Keeping older setup `07`, split-inlet, and outlet-extension branches as comparison history rather than active replication work.

## Chat Cleanup Readiness
- Older chats should be treated as archive candidates only after the decision, evidence, blocker state, and next action are visible in repo files.
- Recent chats from `2026-05-25` onward are intentionally excluded from cleanup for now, even if their contents are already logged.
- The main remaining archive-risk before removing reliance on older chats was the stale snapshot date on this page and ambiguous branch state in the setup-order dictionary; this cleanup pass addresses those two gaps.

## Immediate Next Actions
1. Start a new task from the consolidated runbook and choose one geometry for the first mesh study.
2. Resolve the historical `2.96M` versus `5.58M` baseline cell-count discrepancy before defining the mesh ladder.
3. Define carrier residual, phase mass-balance, pressure-drop, outlet-flow, and velocity/swirl convergence metrics for Case 4.
4. Keep the completed 12-case results labelled provisional until carrier convergence and mesh independence are demonstrated.

## Roadmap Link
- Run-efficiency roadmap: `../project/roadmap.md`
# 19 August 2026 — setup 07j transient VOF prepared for guarded execution

The corrected 07i evidence now shows that the failed WFGC case was a valid
16-process controlled run that diverged and terminated with a node-4 SIGSEGV at
raw iteration 21; it was not a 20-process invalidation. Setup 07j is the
source-free successor: clean 620,431-cell resolved-brine mesh, transient
explicit VOF, Sharp/Geo-Reconstruct, PISO, `1e-4 s`, pool below `y=0 m`, equal
1.12 MPa pressure-outlet bracket, and DPM/EWF/sink off.

The restarted Fluent endpoint authenticated and its `n0..n15` roster was
verified. A formal preparation attempt then blocked for more than 11 minutes
inside the generated Settings-API `read_settings` call and was interrupted
before initialization or time advance. The importer now prefers the historical
TUI `file/read-settings` path, and a guarded one-step-to-0.1-s controller with
storage-aware phase closure and non-overwriting checkpoints is implemented and
locally tested. The same Fluent process subsequently left its TCP port open but
Cortex unobtainable/authentication unavailable, so execution requires one clean
Fluent restart before the TUI-based preparation can resume.
## 2026-08-21 — Setup 07m pressure-opening evidence retained; physical lineage reset

- The setup-07l step-10 hydrostatic-rest checkpoint is the bounded numerical
  parent used by the historical 07m campaign; it is not an accepted operating
  level or dynamically relaxed separator state.
- Nine independent zero-feed pressure/time-step openings completed without a
  finite-field, VOF, Courant, DPM, clock or residual hard failure.
- Ten-step extensions proved the required monotonic pressure response:
  low `-0.00724149`, centre `+0.00451280`, high `+0.01626494 kg/s` liquid at
  the brine face (negative is outward).
- A direct 1% start was rejected on continuity, not on Courant or field blow-up.
- A clean 0.1%/`1e-7 s` startup held for ten further steps with 100 inner
  iterations; continuity fell to `0.00186867` and all physical gates passed.
- The progressive 0.2% and 0.5% stages passed their hard gates. The 1% stage
  remained finite and bounded but stopped at final continuity `0.0177001`,
  above the `0.01` promotion limit; all 2%-to-100% stages were withheld.
- A separate 20-step hold at the same 1% flow, `dt=1e-7 s` and 100 inner
  iterations was proposed. Its first controller attempt timed out during
  connection before any physical step was credited; the zero-block `running`
  manifest is stale and no controller is active. This hold is no longer the
  main physical continuation because it would extend the same unvalidated
  level and pressure assumptions.
- An independent server-2 steady Mixture comparison stopped at iteration 150
  after brine liquid drainage reached `-1372.91 kg/s` and mixture imbalance
  `-1247.64 kg/s`. The field is terminal diagnostic evidence and must not be
  resumed.
- DPM remains zero-object/off; EWF and the numerical sink remain absent.
- The `1.12209 MPa` centre remains a CFD-derived modified-pressure diagnostic,
  not a measured or validated downstream brine boundary.
- Handoff: `brine-outlet-modelling-handoff-2026-08-21.md`.

## 2026-08-21 — Resolved-outlet model and solver review

- Setup `07n` now defines a carrier-only model/solver screening family for the
  explicitly resolved pool, brine pipe and outlet.
- Literature correction: Purnanto's Mixture/DPM separator calculation excluded
  the flow into the brine pipe and prescribed a constant water level. The older
  setup-09 statement that VOF was dropped applies to its carryover-only parent,
  not automatically to the new drainage model.
- Current ranking: first audit the exact pipe crown, outlet leg, local vertical
  resolution and characteristic physical time; then reconstruct a fresh VOF
  pool at a stated submergence. Compare ideal matched liquid removal with
  bounded level-feedback outlet-pressure control before Coupled, implicit-VOF,
  turbulence or alternative phase-model sensitivities.
- RNG `k-epsilon` remains the baseline turbulence closure. RSM is a later
  one-factor sensitivity after one outlet formulation passes, consistent with
  Fluent guidance for highly swirling flows and modern experiment-backed
  cyclone work.
- The principal physical uncertainty remains downstream hydraulic closure,
  not solver choice. The `0.19936247 m2` outlet carries the reference liquid
  feed at only about `0.666 m/s`; one velocity head is about `195 Pa`, versus
  the approximately `2090.4 Pa` hydrostatic-rest head. Omitted pipe/valve losses
  can therefore be of first-order importance.
- DPM remains zero-object/off; EWF and numerical sinks remain off. No new solve
  or model mutation was performed for this literature review.
- User clarification accepted: a constant water level is a physically intended
  operating assumption. The lower pool is required to seal the brine outlet
  against steam escape, while the drain/control system removes liquid at the
  long-time inlet rate.
- Setup `07n` therefore prioritizes a fresh hydrostatic pool definition, a new
  paired inlet/outlet-flow ideal-control diagnostic and a bounded
  level-feedback pressure controller. The recorded setup-07l inventory
  `3774.370486 kg` is a comparison datum only; 07n's controller target will be
  recalculated from its independently accepted level.
- The setup-07k terminal failure does not reject this approach because it
  applied the full outlet flow abruptly to a quiescent non-hydrostatic startup.
  The new branch must start from accepted hydrostatic rest and ramp feed and
  drain together at identical fractions.
- Boundary correction: pressure-outlet backflow volume fraction controls only
  reversed inflow. A Fluent mass-flow outlet prescribes total outlet flow and
  extrapolates phase composition from the adjacent solution. Neither boundary
  can impose zero outward steam as a physical seal.
- The `y=0 m` pool lies approximately at the inferred brine-pipe crown. Setup
  `07n` must first test additional resolved submergence above that crown. The
  outlet passes only if VOF itself keeps the outlet leg liquid-filled and vapor
  carry-under becomes negligible without prescribing the outgoing phase.
- Zarrouk and Purnanto's design review identifies a downstream water drum or a
  U-bend loop seal as the real means of level control and steam sealing. If the
  current short outlet leg cannot preserve the seal, 07n stops solver tuning
  and moves to an explicit water-drum/loop-seal geometry sensitivity.
