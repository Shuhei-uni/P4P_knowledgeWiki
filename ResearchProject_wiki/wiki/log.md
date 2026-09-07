# Work Log

## [2026-08-27] progress-update | Reclassify setup-07n sustained 0.05%-feed drainage

- files updated: `../../Setup report/07n-resolved-brine-outlet-model-solver-screening.md`,
  `../../Setup report/order-dictionary.md`, `wiki/progress/current-status.md`,
  `wiki/progress/experiments.md`, `wiki/progress/blockers.md`,
  `wiki/model/validation.md`, `wiki/log.md`, and `../../CFD_wiki/wiki/log.md`.
- what changed: the ten-step 0.05%-feed pass was challenged with a fixed
  long hold and two delayed proportional pressure-control sensitivities. The
  fixed branch over-drained, gain 0.25 crossed and overshot balance, and gain
  0.05 remained imbalanced before a step-48 stream loss.
- current status: no controller/writer is active; credited fields retained low
  residuals, low Courant and an intact steam seal, but no sustained mass-balance
  window passed. All endpoints remain ineligible and non-resumable.
- blocker: pressure-to-drainage response lag plus missing plant downstream
  head/resistance and operating-level data.
- next action: from the checksum-bound clean server-2 step-90 pair, test one
  lag-aware control treatment while preserving all current physics and gates.

## [2026-08-25] post-processing | Export accepted 0.05%-feed carrier-pathline video

- Cold-loaded the hash-verified server-2 step-100 0.05%-feed endpoint and
  re-proved Fluent 2024 R2, 16 ranks, clock, pressure, inlet rates, phases,
  DPM zero/off, EWF off and source-off state without advancing the solution.
- Exported 12 Fluent PNGs from 827 massless `liquidinlet` carrier seeds and
  assembled a six-second 1600 x 900 H.264 MP4. The accepted source remained
  resident; no initialization, iteration, DPM update or case/data write ran.
- Rejected the optional steam-origin scene because Fluent read the requested
  `steaminlet` release back as `wall-fluid`. Preserved two earlier zero-frame
  graphics attempts and completed under non-overwriting attempt 3.
- Interpretation remains qualitative: frozen-field carrier pathlines are not
  DPM particles, phase-specific liquid trajectories or physical-time playback.
- Evidence:
  `../../../PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07n_s2_p1122264_0p05feed_step100_carrier_pathline_video_attempt3_20260825/`.

## [2026-08-25] model-update | Establish resolved low-feed drainage and load limit

- Every server-2 member cold-loaded the checksum-bound clean step-90 pair;
  Fluent 2024 R2, 16 ranks, settings, clock, DPM, EWF and source gates passed.
- A live VOF mass-flow-outlet inspection found no writable bulk mixture rate,
  only phasic rates; setup 07n-b was withheld rather than prescribing routing.
- The accepted 0.05%-feed pressure-outlet member at 1,122,263.621237 Pa
  completed ten steps with total net -9.11e-8 kg/s, continuity 0.00173276,
  Courant 0.00248721, unchanged reported inventory, full liquid brine coverage
  and zero cross-phase leakage.
- A one-factor load screen passed 0.05625% but stopped 0.0625% and 0.075%
  after their first step at continuity 1.05293 and 1.26332. Terminal fields
  are prohibited from resume or parent use.
- Classification: accepted diagnostic at very low feed; no plant pressure,
  full-flow, long-time control, mesh independence, efficiency, DPM or EWF
  claim. The server-1 lineage was not touched.
- Next action: use the accepted diagnostic to design a gradual, separately
  gated pressure-feedback/ramp study after downstream head/resistance and
  operating-level review.

## [2026-08-19] model-update | Correct setup-07i process count and close the failed steady WFGC branch

- what changed since last update: corrected the attempt-8 runtime interpretation. Fluent's connectivity roster contains `n0..n15`, proving 16 solver processes; the `16/20` Core entry denotes core index 16 on 20 hardware cores, not 20 processes. The supplied GUI photograph independently shows `16-processes`.
- execution evidence: setup 07i therefore had a valid controlled preparation from the clean 620,431-cell mesh, with authoritative settings, WFGC `enable=true, mode=fast`, fresh Hybrid Initialization, the `y<=0 m` pool and DPM/EWF/sink off. The transcript records continuity `3.2024` at raw iteration 16 and `6.9888e14` at raw iteration 20. The GUI records iteration 21, Node-4 SIGSEGV, connection reset and Fluent server shutdown.
- classification: `Diagnostic / catastrophic numerical failure`. Zero complete blocks were credited; no post-divergence checkpoint was written; the initialized checkpoint is not resumable and the identical steady case will not be rerun.
- orchestration correction: replaced the unavailable Fluent-2024-R2 Scheme count query with Settings-API `parallel.show_connectivity(compute_node=0)` capture and node-ID parsing. The gate requires contiguous IDs `n0..n15`, records hardware-core denominators separately and runs before mutation. All 29 local tests pass.
- live status: after VPN/server recovery, the 2026-08-19 read-only probe verified Fluent 2024 R2 `Status.SERVING`, 16 solver processes on 20 hardware cores, no case loaded and no active setup-07i controller.
- evidence preservation: added `PROCESS_COUNT_AND_FAILURE_CORRECTION_20260819.md` and `attempt8_gui_sigsegv_iteration21.png`; retained the originally misnamed `invalid_live20_processes` archive files unchanged as audit history.
- next action: implement setup 07j transient VOF/liquid-inventory qualification with a defensible brine-outlet boundary. DPM, EWF, mesh convergence and separator-performance claims remain blocked.

## [2026-08-18] progress-update | Evening setup-07i retry still cannot reach Fluent gRPC

- what changed since last update: added live compute-node reporting to the read-only status probe and retried the current endpoint at `18:12 NZST`.
- current status: TCP again timed out before Fluent authentication, so neither health nor the claimed 16-process runtime count could be verified. No controller started and credited iterations remain zero.
- blocker: unchanged; the Windows host is reachable, but the Fluent gRPC listener/port is not externally reachable.
- next action: confirm locally that the Fluent port is listening, then correct server mode or the Windows inbound firewall rule before another controller launch.

## [2026-08-18] progress-update | Isolate setup-07i connection failure to Fluent listener or port firewall

- what changed since last update: verified end-to-end VPN/host reachability. The Windows PC answered ICMP and TCP port `3389` accepted a connection, but the stated Fluent gRPC port timed out before authentication.
- current status: the host is online and reachable; setup 07i remains stopped at zero credited iterations because the Fluent listener is not externally reachable. The current password has not been accepted or rejected because no TCP session reaches gRPC.
- blocker: Fluent is either open as a normal 16-process GUI/solver without its gRPC server listener active, bound only locally, or the Windows firewall is dropping inbound TCP to the stated port.
- next action: on the Windows PC, start/restart Fluent 2024 R2 in server mode with 16 solver processes and the current server-info/port, then permit that exact TCP port through Windows Defender Firewall. Retry the read-only health/live-count probe before launching any controller.

## [2026-08-18] progress-update | Retry cannot reach claimed 16-process Fluent session

- what changed since last update: retried the recorded setup-07i endpoint with both the normal and a 15-second TCP bound, then checked only the two other Fluent ports previously supplied for the same PC. All three timed out before authentication; the VPN interface and internal route remain active.
- current status: the user reports that a 16-process Fluent session is running, but no currently recorded endpoint reaches it. No controller was started and the formal run remains at zero credited iterations.
- blocker: the live session is either listening on a new gRPC port/address, server mode is not accepting remote TCP, or the Windows firewall/path is blocking it. Its runtime process count cannot be verified until TCP connectivity succeeds.
- next action: obtain the active Fluent server console's current IP, gRPC port and password (or its current server-info file), update `.env`, then run the read-only live-count gate before launching the clean controller.

## [2026-08-18] progress-update | Setup-07i remains stopped and Fluent remains unreachable

- what changed since last update: no new preparation, credited iteration, checkpoint or controller appeared; the attempt-8 invalid manifests remain unchanged at zero credited iterations.
- current status: setup 07i remains `Diagnostic / unresolved`; no controller is active and the read-only endpoint probe at `14:18 NZST` timed out before Fluent health.
- blocker: Fluent 2024 R2 must be relaunched in server mode with exactly 16 solver processes and current connection details before the formal WFGC comparison can restart.
- next action: after endpoint recovery, allow the strict live process-count gate to pass and restart only from the clean original brine-outlet mesh; do not resume attempt 8.

## [2026-08-18] model-update | Stop invalid 20-process setup-07i attempt and add live runtime gate

- files updated: setup-07i preparation/qualification/supervisor manifests and preserved attempt-8 copies; `prepare_setup07h_brine_pool.py`; the shared setup-07h/07i status checker; setup-07i tests; setup report/order dictionary; project current status, experiments, blockers and validation.
- purpose: implement the queued WFGC sensitivity without allowing a hidden solver-process change to contaminate the one-factor comparison.
- execution evidence: attempt 8 completed clean mesh/settings import, WFGC `enable=true, mode=fast`, fresh Hybrid Initialization, the `y<=0 m` pool patch and a separate initialized case/data write with DPM/EWF/sink off. Fluent's startup roster then proved 20 live compute nodes rather than the required 16.
- stop and preservation: the controller was stopped with zero credited iterations. Twenty raw startup rows are retained only as invalid diagnostic evidence; continuity reached `6.9888e14` at raw iteration 20. No divergent checkpoint was saved, and the initialized attempt-8 checkpoint is explicitly not resumable for the formal comparison.
- orchestration correction: a fail-closed Scheme readback of the live compute-node count now runs immediately after authentication and before any remote-directory, mesh, settings or initialization mutation. It must return exactly 16. The status command now reports an unreachable endpoint without a traceback, and the stale attempt-8 PID file was archived under an explicit invalid-attempt name. All 29 local tests pass.
- assumptions introduced or retired: retired the assumption that preflight `mesh_metrics.partitions=16` proves the live Fluent process count. No physics assumption changed.
- blocker: no setup-07i controller is active and the recorded endpoint timed out in the post-stop read-only check.
- next immediate action: relaunch Fluent 2024 R2 with exactly 16 solver processes, update current connection details if they change, and restart setup 07i from the clean original mesh. A valid repeat failure routes to setup 07j transient VOF.

## [2026-08-16] model-update | Implement and queue setup 07i WFGC-only sensitivity

- purpose: isolate Fluent's recommended polyhedral-mesh Warped-Face Gradient Correction as the only changed factor from setup 07h before committing to a transient formulation.
- implementation: added clean preparation/readback, cold-reload verification, 25/250 startup checkpoints, a gross-drainage stop, status/supervisor wrappers and regression tests. All 26 local tests pass.
- fixed controls: clean resolved-outlet mesh, authoritative carrier settings, `y<=0 m` liquid pool, equal `1.12 MPa` outlets, fresh Hybrid Initialization and DPM/EWF/sink off.
- execution evidence: repeated preserved attempts blocked during `connect_to_fluent`, before mesh loading or Fluent mutation. Attempts three through seven reached their bounded 600-second connection timeouts. From 02:16 through 07:46 NZST, twelve consecutive heartbeat checks found the predecessor PID absent but the raw TCP preflight timed out, so no eighth controller was launched. A direct authenticated-channel probe had also timed out before health.
- overnight closure: no active controller, preparation manifest, qualification manifest or CFD result exists. All attempts remain pre-mutation evidence. The next action is to restart Fluent in server mode, confirm current credentials and then launch the prepared clean 07i workflow once.
- network diagnosis: the Mac VPN route is active through `ppp0` and traceroute reaches internal `172.18.*` hops, but the target `10.104.145.85` does not answer ICMP, Fluent `51387`, RDP `3389`, SMB `445` or WinRM `5985/5986`. The saved port and password match the latest user-supplied values. This isolates the present blocker to the Windows host/path or stopped server, not the local credentials or 07i scripts; no available remote-management channel can restart it.
- orchestration correction: the 07i supervisor now avoids a throwaway PyFluent readiness connection immediately before preparation, emits unbuffered stage logs and bounds a silent preparation RPC to 600 seconds.
- supervision: an active heartbeat checks every 30 minutes through 08:00 NZST, never duplicates a controller, and may retry only this proven pre-mutation connection failure after endpoint recovery.
- next action: obtain the first verified WFGC readback and guarded iteration-250 result. If gross drainage or instability remains, define setup 07j transient VOF with a defensible brine boundary rather than tuning pressure to closure.

## [2026-08-16] qualification | Stop setup 07h initialized-pool branch after divergence

- preparation: clean 620,431-cell resolved-outlet mesh, authoritative carrier settings, Hybrid Initialization and a read-back `y<=0 m` cell register; phase-2 patch changed domain-average liquid VF `0 -> 0.15826588`. DPM, EWF and source terms remained off.
- early evidence: iteration 25 established the intended directions and a `97.32%` liquid brine discharge, but the state was still strongly imbalanced.
- terminal verified evidence: at iteration 250 brine liquid discharge was `-3304.7817 kg/s`, mixture imbalance `1602.99%` and liquid imbalance `2726.53%`.
- failure: the next 250-iteration request produced only 43 residual advances. Transcript row 292 showed catastrophic continuity/turbulence growth followed by AMG pressure/k/VOF divergence and a floating-point exception; the block is not credited.
- numerical-method finding: Fluent's settings-import warning recommended Warped-Face Gradient Correction for the polyhedral mesh, while post-stop live readback returned `enable=False`. This is recorded as a plausible contributor requiring a clean one-factor sensitivity, not as a proven root cause.
- preservation: initialized, iteration-25 and iteration-250 pairs remain separate. The post-FPE live state is additionally saved as `post_fpe_residual_row292_unverified`; it is diagnostic only.
- decision: setup 07h is unresolved and closed. Before the transient branch, one clean non-overwriting sensitivity may change only Warped-Face Gradient Correction to enabled/read back. The failed steady field is never resumed and arbitrary pressure tuning remains prohibited.

## [2026-08-12] recovery | Preserve interrupted 07f case 2 and restart unfinished cases

- completed evidence: the doubled-band `tau=0.020 s` case reached `3,000` cumulative / `2,000` full-strength iterations. It ended with sink `53.133696 kg/s`, pressure drop `26.7892 kPa`, domain liquid inventory `64.64961 kg`, corrected liquid imbalance `54.5553%` and zero passing stability windows, so it is diagnostic/unresolved.
- interruption: the first doubled-band `tau=0.005 s` attempt recorded `2,375/1,375` cumulative/full-strength iterations before its manifest/log stopped advancing. Fluent 2024 R2 remained healthy and DPM was off.
- preservation and decision: saved the newer live field separately as explicitly unverified evidence. Since exact completion beyond the saved R1=1000 checkpoint cannot be proved, the partial field is not reused.
- orchestration correction: a sandboxed `kill -0` check returned permission denial and was initially interpreted as process absence, briefly allowing two duplicate `v4` preflight controllers while the original stalled tree still existed. An escalated process audit exposed all three trees; they were terminated before new production iteration. The interleaved `v4` preflight failed the carrier-fingerprint guard and its failure checkpoints/manifests are retained.
- restart: case 1 remains complete and is skipped; only cases 2 and 3 restart clean under one audited `v5_single_controller` tree with the same 25-iteration RPC blocks, guards, physics and monitoring contract.
- v5 correction: the single controller completed clean parity/mask preflight and saved a ramp-zero checkpoint. A separate health probe did not return while Fluent was busy and was incorrectly treated as evidence of service loss; v5 was stopped before its first production iteration, so no solution history was lost.
- v6 terminal preflight: one audited controller connected and restored the clean parent, but Fluent emitted no captured text for mesh size/check/quality report calls. The mandatory parser failed safely before initialization or iteration. No controller remains active; cases 2 and 3 are paused until Fluent is restarted or its report/readback stream is repaired.
- follow-up readback: a later read-only probe confirmed Fluent health `Status.SERVING`, but mesh-size/check/quality calls still returned empty captured output. The queue remains stopped because health connectivity alone is insufficient evidence for a safe production restart.

## [2026-08-11] recovery | Restart setup-07f with bounded Fluent RPC blocks

- trigger: the first optimized doubled-band case recorded `2,500` cumulative / `1,500` full-strength iterations, then a 250-iteration Fluent gRPC request ended with `recvmsg: Operation timed out`.
- diagnosis: Fluent 2024 R2 remained healthy and DPM remained off; the event was a controller transport timeout rather than numerical divergence. The recorded endpoint had sink `44.199736 kg/s`, pressure drop `25.1905 kPa`, continuity about `0.20` and zero passing stability windows.
- preservation: the newer partial in-memory state was saved under an explicitly unverified, non-overwriting recovery filename; the prior clean/ramp/R1 checkpoints and all `v1`/`v2` evidence remain unchanged.
- correction: the runner now bounds ramp and full-strength Fluent calls to 25 iterations. The complete three-case matrix restarted from the clean prepared origin under `v3_rpc25` labels, so no partial failed-state field is reused.
- current action: supervise the clean retry and retain the same physical monitors, safety guards and diagnostic-only interpretation.

## [2026-08-11] model-update | Launch setup-07f sink thickness and rate matrix

- files created or updated: `../../Setup report/07f-split-inlet-sink-thickness-rate-matrix.md`, `../../Setup report/order-dictionary.md`, setup-07f controller changes and queue under `../../PyAnsys/`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, and `wiki/log.md`.
- purpose: run the user-requested bounded extension of the local sink diagnostic while brine-outlet geometry remains unavailable, separating doubled-band and faster-coefficient effects.
- assumptions introduced or retired: introduced setup `07f` as diagnostic sensitivity only; retained the resolved brine outlet as the physical next branch and retained the rule that steady iteration is not physical time.
- launch evidence: the first `(0.2803305072 m, 0.020 s)` case passed Fluent 2024 R2/16-partition, 900k mesh/settings, source-hook, RP-control and fresh-initialization readback. Its complete mask contains `184,145` cells and `0.88704756 m3`; a separate ramp-zero case/data pair is saved and the guarded ramp is active.
- scheduling correction: stopped and preserved the initial startup after 79 iterations when the inherited Adjust hook was shown to rebuild the fixed whole-domain mask every iteration (`8-11 min/iteration`). A live static-mask/on-demand smoke check completed in `6.17 s`, retained every RP control and DPM-off state, and the formal queue restarted clean under new non-overwriting `v2_staticmask` labels.
- next immediate action: supervise all queued cases, preserve terminal checkpoints and compare sink, balance, pressure, inventory, velocity/vorticity and residual histories before assigning accepted/diagnostic/unresolved labels.

## [2026-08-09] progress-update | Close setup-07c thickened-sink sensitivity as unresolved

- files created/updated: `../../Setup report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md`, `../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`, `../../Setup report/order-dictionary.md`, setup-07b and setup-07c qualification result reports, setup-07c `analysis_correction.json`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, and `wiki/log.md`.
- purpose: complete the clean-900k 16-layer-equivalent bottom-local sink sensitivity, preserve recovery/checkpoint evidence, assess iteration stability and close the branch with a defensible evidence label.
- execution: Fluent 2024 R2 on 16 partitions completed a 1,000-iteration guarded ramp and 2,000 full-strength iterations with DPM off. A startup-guard false stop at R1 = 250 was recovered from separately saved case/data without overwriting any evidence.
- result: zero acceptance windows passed. Endpoint sink was `22.4882 kg/s` against `116.92 kg/s` liquid inlet, inventory `71.7785 kg`, pressure drop `27.1372 kPa` and continuity `0.191551`; final-500 pressure, sink, inventory, outlet-velocity and domain-velocity drift all failed.
- sensitivity conclusion: thickening from one cell to `0.1401652536 m` increased sink removal roughly `13-16x` at matched full-strength counts but still removed only `19.23%` of liquid inflow and did not stabilize the carrier field.
- accounting correction: identified that the raw controller `liquid_source_augmented_*` field double-counts the phase-2 cell-zone sink. Corrected source-inclusive liquid imbalance is `80.7661%` for 07c and `91.1909%` for 07b; raw manifests remain unchanged and no classification or acceptance-window decision changes. Mixture source-augmented values remain valid.
- current status: setup `07c` is `Completed diagnostic / physical qualification failed`; no mesh-independence, separator-efficiency, validation, DPM or EWF claim is permitted.
- next immediate action: add and qualify a resolved brine outlet on one medium mesh when geometry editing is available.

## [2026-08-08] progress-update | Close setup-07b tau=0.1 qualification as unresolved
- files created/updated: `../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`, `../../Setup report/order-dictionary.md`, `../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/mesh-900k_tau0p100_qualification_v1/QUALIFICATION_RESULT.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, and `wiki/log.md`.
- purpose: reconcile the supervised clean-origin qualification through its 6,000-iteration full-strength limit, preserve final checkpoints and assign a defensible evidence classification.
- result: zero acceptance windows passed. Final sink was `8.06194 kg/s` against `116.92 kg/s` liquid inlet, domain liquid inventory reached `191.836 kg`, corrected source-inclusive liquid imbalance remained `91.1909%`, pressure drop was `34.8475 kPa`, and continuity was `0.279243`.
- recovery: a controller disconnect during R1 `2750-3000` was handled with separate live-state checkpointing and iteration reconciliation; the formal R1 `6000` case/data and a second ramp-reset-zero final pair were both verified without overwriting earlier files.
- assumptions introduced or retired: retired the active-running state and rejected `tau=0.1 s`/one-cell sink as a physically qualified constant-level model. Retained the UDF implementation itself as accepted technical evidence and retained any future tau/layer work as diagnostic sensitivity only.
- current status: `Completed diagnostic / unresolved at maximum iteration budget`; DPM remained off and no mesh-independence, efficiency or validation claim is permitted.
- next immediate action: create and qualify a resolved brine-outlet branch on one medium mesh before any new mesh ladder, DPM or EWF work.

## [2026-08-07] experiment-start | Launch clean 900k setup-07b tau=0.1 qualification
- files created/updated: setup-07b qualification controller and status checker under `../../PyAnsys/scripts/`, live preflight and run evidence under `../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/`, setup report, experiments, current status and log.
- start evidence: reloaded the accepted clean-original, fresh-Hybrid 900k checkpoint; full carrier/source readback passed; DPM was off; no setup-07a accumulated solution data was loaded; a separate run-local ramp-zero case/data pair was saved.
- execution contract: ramp over 500 iterations, then run `R=1` in 250-iteration blocks with 2,500 minimum/6,000 maximum and monitor-based early stopping only after two passing 500-iteration windows.
- status: `Diagnostic qualification in progress`. The protected source checkpoint remains unchanged.
- next action: inspect ramp-stage source/inventory/balance response, then the full-strength stability windows before assigning a physical result label.

## [2026-08-07] model-update | Implement setup 07b constant-water-level liquid sink
- files created/updated: `../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`, `../../Setup report/order-dictionary.md`, setup-07b PyFluent/UDF source, tests and machine evidence under `../../PyAnsys/`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/gaps/open-questions.md`, `wiki/index.md`, and `wiki/log.md`.
- reason: setup 07a demonstrated monotonic liquid accumulation with a closed-bottom steady model; the user chose to test Purnanto's assumed constant water level by removing liquid reaching the wall that represents that level.
- implementation result: Fluent 2024 R2 compiled and cold-reloaded a parallel-safe UDF with five UDMs, phase-2 liquid mass sink, mixture momentum sinks and no vapor/DPM source. One diagnostic iteration produced `-0.47973263 kg/s`, matching the implemented inventory/ramp/tau law.
- assumptions introduced/retired: introduced setup 07b as an unresolved-reservoir abstraction; did not claim it is a physical brine outlet. Retired use of the setup-07a 6000-iteration accumulated-liquid field as a valid production start state.
- production-start correction: the actual 07b qualification must originate from clean `mesh-900k.msh`, authoritative settings readback and fresh Hybrid Initialization. The old field was used only for code execution proof.
- clean-origin result: preparation v3 loaded original `mesh-900k.msh` (SHA-256 `353bf13c...afef`), matched the normalized authoritative setup fingerprint, fresh Hybrid Initialized, loaded no saved solution data, ran zero production iterations, and passed cold-reload hook/UDM/ramp-zero checks.
- current status: UDF implementation and the clean-origin initialized start state are accepted; steady solution, tau/ramp selection, mass closure, geometry-level water-plane evidence, separator performance and mesh convergence remain unresolved. DPM remains off.
- next immediate action: qualify source strength and steady liquid closure from the accepted clean-origin checkpoint before any mesh ladder, DPM or EWF work.

## [2026-07-29] workflow-update | Consolidate Purnanto automation and mesh-study handoff
- files created/updated: `../../PyAnsys/docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md`, `../../PyAnsys/README.md`, `wiki/index.md`, `wiki/technical/purnanto-enthalpy-dpm-replication.md`, `wiki/progress/current-status.md`, and `wiki/log.md`.
- purpose: replace conversation-dependent operational context with one durable runbook covering connection setup, fixed case inputs, baseline and spiral execution, monitoring, recovery, output acceptance, completed results, known evidence gaps, and the starting protocol for a new mesh-convergence task.
- assumptions introduced/retired: selected Case 4 (`1600 kJ/kg`) as the recommended first representative mesh-study condition unless the research question requires another case; explicitly separated fixed-budget replication execution from carrier convergence and formal mesh-independence evidence.
- current status: the completed sweeps remain provisional; the next workstream is a one-geometry mesh audit and coarse/medium/fine carrier-flow study before repeating DPM comparisons.
- next immediate action: open a new task using the prompt embedded in the consolidated runbook, resolve mesh identity and quality first, then define the mesh ladder and convergence metrics before launching long runs.

## [2026-07-29] lint | Audit Purnanto sweep automation and evidence
- files created/updated: `../../Setup report/08b-purnanto-baseline-enthalpy-dpm-sweep.md`, `../../Setup report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md`, `../../PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py`, `../../PyAnsys/scripts/setup/continue_purnanto_current_case.py`, `../../PyAnsys/tests/test_purnanto_enthalpy_sweep.py`, PyAnsys Fluent knowledge indices/orders/logs, `wiki/technical/purnanto-enthalpy-dpm-replication.md`, `wiki/technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/index.md`, and `wiki/log.md`.
- purpose: apply the repository instruction contracts retroactively, reconcile the completed six-case baseline and six-case spiral sweeps, and prevent silent acceptance of incorrect phase mapping or stale/misparsed DPM reports.
- assumptions introduced/retired: future runs require material-backed phase identity and one-way DPM readback; DPM mass is accepted from the explicitly labelled `Final` report column; particle-count weighting is disabled by default; post-DPM injection verification is read-only before saving. Retired the claims that the campaign was still at Cases 1-3 and that 1500 iterations demonstrated convergence.
- evidence qualification: all 12 cases have injection-level exports with passing fate-mass reconciliation. All spiral cases and baseline Cases 2-6 have standalone 1-1500 residual CSVs; baseline Case 1 has block-level completion evidence but no mirrored residual CSV. Historical manifests do not capture every inherited DPM control.
- current status: both sweeps are complete but scientifically provisional because final continuity residuals remain high and exact setup/geometry parity is incomplete.
- next immediate action: continue representative cases using residual and outlet-flow stability criteria, then localize incomplete DPM endpoints before deciding whether a complete rerun is justified.

## [2026-07-22] progress-update | Document Purnanto enthalpy and DPM replication campaign
- files created/updated: `wiki/technical/purnanto-enthalpy-dpm-replication.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/index.md`, `wiki/log.md`
- purpose: create a mid-year technical-report evidence brief for the six-condition Purnanto replication, structured around research motivation, literature basis, methodology, interim findings, limitations, defensible conclusions, and remaining work; retain operational and recovery details in a reproducibility appendix.
- assumptions introduced/retired: documented the inferred steam-quality convention using paper-table steam flow plus escaped DPM liquid; documented the droplet-input chain from digitized Purnanto Figure 5 data through the fixed nine-bin distribution and Harwell generator; retained uncertainty around exact geometry parity and nine-bin injection allocation; explicitly rejected iteration-count completion as convergence proof.
- current status: Cases 1-3 have complete 1500-iteration and DPM outputs with provisional qualities `99.775%`, `99.672%`, and `99.7304%`; Case 3's DPM recovery passed all nine injection mass-balance checks; Case 4 is active after fresh-case setup and verified injection readback; Cases 5-6 remain queued.
- interim paper comparison: against the nearest digitized Purnanto red simulation points, Cases 1-3 are lower by `0.2169`, `0.1031`, and `0.0817` percentage points; Case 1 is the main mismatch, while Cases 2-3 reproduce the increasing quality trend from `1440` to `1520 kJ/kg`.
- interpretation correction: Purnanto also reported substantial incomplete DPM trajectories, so the current incomplete fractions are not unique to the project implementation; quantitative parity remains unresolved because the paper does not provide enough case-level fate mass and tracking detail.
- blockers: high continuity residuals, large incomplete DPM fractions, and dependence on continuous Mac/VPN connectivity.
- next immediate action: finish Cases 3-6, add steam quality to the combined summary, compare all six points with the digitized Purnanto graph, and audit convergence plus incomplete-particle locations.

## [2026-06-09] model-update | Anchor Purnanto pages to extracted HDF5 setup
- files created/updated: `wiki/technical/purnanto-live-setup-reference.md`, `wiki/technical/sources/purnanto-etal-2013.md`, `wiki/model/baseline-cfd.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/index.md`, `wiki/log.md`
- reason: user asked to clean up the knowledge base so older Purnanto setup assumptions are replaced by the extracted Fluent HDF5 case/data pair and the setup is easier to reference later.
- notable result: the live audited setup is now captured as a friendly reference page and the Purnanto baseline pages now point to observed HDF5 case values instead of leaving the same solver and inlet settings implicit.
- assumptions introduced/removed: removed several paper-only setup guesses from the project-facing reference path by replacing them with observed HDF5 values; retained the paper source as the provenance record for what was originally reported.
- next action: if a run-specific setup report needs the same cleanup, sync `00a-purnanto-setup-5000-live-audit.md` to the local extracted file pair and then use the new reference page as the default citation target.

## [2026-06-08] model-update | Create setup 08a steam-outlet extension trial
- files created/updated: `../../Setup report/08a-steam-outlet-extension-student-trial.md`, `../../Setup report/order-dictionary.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/index.md`, `wiki/log.md`
- reason: user plans to redo the geometry from setup `07` using the same Purnanto spiral-inlet separator and split two-phase inlet, but with an extended steam outlet path for a student-edition diagnostic trial.
- what changed since last update: setup `08a` is now recorded as a child of `07`; it keeps the setup `07` inlet/solver package and changes only the steam outlet geometry so the pressure-outlet boundary is downstream of the outlet-pipe entrance.
- current status: setup `08a` is planned, not yet run. The working hypothesis is that direct pressure-outlet placement at the outlet-pipe entrance may contribute to backflow reversal and unstable steam-outlet mass-flux reports.
- blockers: mesh quality, student-edition cell limit, residual/monitor stability, and outlet flux stability are all still pending.
- next action: build the outlet-extension geometry, verify boundary zones and inlet fluxes, then save geometry, mesh, residual, flux, and outlet-vector evidence before comparing against setup `07`.

## [2026-06-09] model-update | Record 500-iteration one-inlet diagnostic and residual plot
- files created/updated: `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`, `../../../PyAnsys/docs/LOCAL_ONE_INLET_SMOKE_TEST.md`
- reason: user asked to make sure the longer `500`-iteration local diagnostic and the rough residual plot were recorded and the findings updated.
- assumptions introduced/removed: added the explicit one-steam-outlet interpretation rule that mixture imbalance should not be treated as a failure for this branch without a liquid drain or transient accumulation model; retained the caution that the run is still diagnostic only and not convergence/validation evidence.
- current status: the one-inlet `trial4` path now has a completed `500`-iteration controlled diagnostic with vapor recovery near `1`, liquid carryover effectively `0`, checkpoint outputs, and a rough scaled-residual artifact.
- next action: keep this run as the current longer local baseline, then clean up pressure-outlet setting inactivity and direct residual export behavior if possible.

## [2026-06-09] model-update | Harden local PyFluent one-inlet parity record and docs
- files created/updated: `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`, `../../../PyAnsys/docs/LOCAL_ONE_INLET_SMOKE_TEST.md`, `../../../PyAnsys/docs/TROUBLESHOOTING.md`
- reason: user asked to update the project smoke-test report and local docs after the hardened `trial4` parity pass.
- assumptions introduced/removed: removed the earlier assumption that operating-pressure control and numerics-path discovery were still unresolved in the active local script; retained only the smaller uncertainty around pressure-outlet setting inactivity and cleaner balance reporting.
- current status: the local one-inlet PyFluent path is now documented as a hardened `trial4` parity workflow with clean operating-pressure control, confirmed 2026 R1 numerics paths, mass-flow sanity output, and both case/data writes.
- next action: test whether pressure-outlet setting order can be cleaned up, then improve the raw flux report into a more structured balance summary.

## [2026-06-09] model-update | Record PyFluent trial3 smoke-test troubleshooting report
- files created/updated: `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- reason: user asked for a durable markdown report of the PyFluent setup troubles, workarounds, successful steps, and next improvement points so the next automation pass starts from current evidence.
- assumptions introduced/removed: introduced a narrow active automation blocker around the operating-pressure API path and the 2026 R1 numerics-setting object paths; removed the broader fear that local PyFluent setup might not work at all on the current mesh branch.
- current status: the one-inlet `trial3.msh` reconstruction is now documented as a runnable local smoke-test workflow with manual water-property definition, hybrid initialization, and `10` completed steady iterations.
- next action: fix operating-pressure control, map the correct solution-method API paths, and add automatic phase mass-flow reporting before attempting longer controlled runs.

## [2026-06-09] model-update | Reset direct recreation target to one-inlet Purnanto branch
- files created/updated: `../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`, `../../Setup report/order-dictionary.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/index.md`, `wiki/log.md`
- reason: user asked to recreate the Purnanto setup itself, meaning one inlet carrying both steam and water together rather than continuing the later split-inlet branches.
- assumptions introduced/removed: removed the implied assumption that the split-inlet lineage was still the best direct recreation target; introduced setup `08` as a reset-to-baseline branch that reuses the live Purnanto audit and the reusable CFD baseline.
- current status: the active rebuild target is now the one-inlet mixed steam-water `Mass-Flow Inlet` package from setup `08`; split-inlet branches remain comparison-only context.
- next action: build the Fluent case for setup `08` and verify one-inlet phase mass flows plus baseline model parity before reviving split-inlet comparisons.

## [2026-06-05] query | Audit live Purnanto Fluent setup
- files created/updated: `../../Setup report/00a-purnanto-setup-5000-live-audit.md`, `../../Setup report/order-dictionary.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/index.md`, `wiki/log.md`
- reason: user asked for an extensive setup check of the Purnanto Fluent case/data pair in `Fluent Standalone Test 1\purnanto case`.
- notable result: live Fluent 2024 R2 audit loaded `purnanto-setup.cas.h5` and `purnanto-setup-5000.dat.h5`; setup matches the core Purnanto baseline stack and reports `2,964,593` tetra cells, minimum orthogonal quality `0.277635`, and `5000` saved iterations.
- assumptions introduced/removed: introduced the `00a` setup-report branch as a live baseline audit child of `00`; retained uncertainty around exact geometry variant, residual values, mass-balance state, and turbulent-viscosity-limited cell locations.
- next action: run phase flux reports and localize the `34,302` cells where turbulent viscosity hit the `1e5` ratio cap before using the result as quantitative baseline evidence.

## [2026-06-04] ingest | Add Chen 2025 and Pointon 2009 validation anchors
- files created/updated: `wiki/literature/matrix.md`, `wiki/model/validation.md`, `wiki/progress/current-status.md`, `wiki/index.md`, `wiki/log.md`
- reason: two new raw CFD papers were processed in `CFD_wiki`, and the project wiki needed only the linked impact summary: Chen 2025 as the strongest current experiment-backed separator-method anchor and Pointon 2009 as a geothermal HP-separator validation/scale anchor.
- assumptions introduced/removed: introduced a cross-wiki method rule that Chen 2025 supports a later `RSM-DPM` sensitivity decision but does not provide direct geothermal operating targets; clarified that Pointon 2009 is trend/context support rather than a fully specified reproduction target.
- current status: the project now has stronger external validation framing without duplicating the full CFD extraction into the research wiki.
- next action: keep the current setup `07` baseline path unchanged, and only consider an `RSM-DPM` sensitivity case after residual stability and phase-flux/DPM evidence are clean.

## [2026-06-04] model-update | Update setup 07 DPM results for water-density droplets
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user changed the DPM particle density to `881.77 kg/m3` to match water droplets and supplied a replacement main sweep plus updated `5 um` sensitivity checks.
- assumptions introduced/removed: retired the anthracite-based DPM count table as the main interpretation for setup `07`; kept the incomplete-as-trapped project rule and inferred `0` escape for the reported `4.1e-5 m, 200, 72, 128` row because that is the only count-closing parse.
- current status: the updated water-density runs now give scoped DPM removal efficiencies of `63.0 %` at `5 um`, `88.5 %` at `1 um`, `93.0 %` at `10 um`, and `100 %` at `41 um` and `100 um`.
- next action: treat the water-density deterministic `5 um` case as the primary fine-droplet reference and optionally rerun `10 um` with `100,000` max steps as a robustness check.

## [2026-06-03] model-update | Add `5 um` DRW and rotation sensitivity checks
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user supplied extra `5 um` sensitivity results for Discrete Random Walk and particle rotation.
- assumptions introduced/removed: no new branch assumption; recorded DRW and rotation as sensitivity checks rather than new baseline settings.
- current status: at `5 um`, DRW lowers scoped efficiency from `77.2 %` to `73.8 %` and rotation lowers it to `75.7 %`, so neither materially changes the branch-level conclusion.
- next action: keep the deterministic `5 um` result as the primary fine-droplet reference unless later sensitivities show a larger spread.

## [2026-06-03] model-update | Adopt incomplete-as-trapped interpretation for setup 07 DPM
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user decided that incomplete DPM particles should be treated as trapped for setup `07` because they are interpreted as wall-stuck rather than escaped.
- assumptions introduced/removed: replaced the pessimistic-bracketing interpretation with a user-specified scoped efficiency rule `1 - escaped/injected`; zero-escape sizes are now treated as `100 %` efficient for this branch.
- current status: scoped DPM removal efficiencies are now `76.5 %` at `5 um`, `88.5 %` at `1 um`, and `100 %` at `10 um`, `41 um`, and `100 um`, with anthracite still noted as a surrogate-material limitation.
- next action: record residual/monitor stability, then optionally rerun `10 um` with `100,000` max steps as a robustness check.

## [2026-06-03] model-update | Record first setup 07 DPM sweep
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user supplied the first DPM tracked/escaped/trapped/incomplete counts for setup `07`.
- assumptions introduced/removed: kept the counts exactly as reported, including the `1e-6 m` (`1 um`) case; introduced explicit optimistic/pessimistic efficiency bracketing because incomplete counts are too high for a single-value claim.
- current status: the first DPM sweep shows plausible lower escape for larger droplets, but incomplete fractions from `47.5 %` to `67.0 %` make the result diagnostic only.
- next action: increase DPM max steps to `100,000` and rerun at least the `10 um` case before treating DPM as stronger efficiency evidence.

## [2026-06-03] model-update | Audit and sync setup 07 DPM settings
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user asked for a critical assessment of current Fluent DPM boundary, tracking, injection, and physical-model settings before running efficiency tests.
- assumptions introduced/removed: synced the report to the user's applied settings: step factor `2`, flow rate `1e-6 kg/s`, particle rotation off, and stochastic tracking off. Anthracite remains the only unresolved surrogate-material limitation.
- current status: setup `07` now has a report-ready DPM settings audit that matches the currently applied Fluent settings.
- next action: run `5 um`, `10 um`, and `40-41 um` DPM injections with escaped/trapped/incomplete counts, then note the anthracite material limitation in the results.

## [2026-06-03] model-update | Scope setup 07 away from bottom liquid handling
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- reason: user clarified that the cut-off bottom without a brine outlet or water pool is acceptable for setup `07` and should not remain a project concern.
- assumptions introduced/removed: introduced `User-specified` scope assumption that setup `07` is judged on steam-line liquid carryover and DPM droplet fate, not brine-outlet drainage or lower water-pool modelling.
- current status: missing brine/liquid outlet flux is no longer a blocker for the scoped setup `07` efficiency baseline; residual/monitor stability and DPM fate counts remain needed.
- next action: run the `5 um`, `10 um`, and `40-41 um` DPM checks on the saved setup `07` field.

## [2026-06-03] progress-update | Record professional setup 07 flux diagnostic
- files created/updated: `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `../../Setup report/order-dictionary.md`, `../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md`, `../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md`, `../../CFD_wiki/wiki/log.md`
- reason: user completed the pure liquid / pure steam actual-area setup using the professional license and wants only baseline efficiency checks before deeper wall-film work.
- what changed since last update: professional run `PLS-PRO-2026-06-03-A` is now logged with `1.3M` nodes, `7.6M` cells, low apparent steam-line liquid carryover, and a short DPM plan.
- current status: setup `07` looks promising for steam-line carryover, but the full mass balance is not closed because the brine/liquid outlet was not included in the reported flux surfaces.
- blockers: missing all-boundary flux report, missing residual/monitor stability evidence, and no DPM escaped/trapped/incomplete counts yet.
- next action: export all-boundary phase fluxes, then run `5 um`, `10 um`, and `40-41 um` DPM injections before exploring transient wall film.

## [2026-06-01] model-update | Add rough pure-phase split flux calculations from meeting report
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user asked for report-ready inlet-sizing calculations and flux-based efficiency values for two rough pure-phase split setups documented in `Meeting Report 2.docx`.
- what changed since last update: added copyable inlet area-sizing equations to the pure-phase actual-area setup report, recorded flux-based carryover efficiency and steam-outlet dryness for both rough student-edition setups, and synced the comparison signal into the project experiment log and current-status page.
- current status: the rough report now has a repo-backed calculation source for the `1600 kJ/kg` inlet split, and the two rough diagnostics currently suggest Setup 2 reduced steam-line liquid carryover relative to Setup 1.
- blockers: the rough comparison is not a clean one-factor test because Setup 2 changed both upstream geometry and inlet boundary type; both runs also remain low-mesh/non-converged diagnostics only.
- next action: if the Setup 2 direction looks worth keeping, rerun it as a controlled comparison with the same inlet boundary type as Setup 1 before using the trend in any stronger claim.

## [2026-06-01] workflow-update | Add lightweight subagent operating model
- files created/updated: `../../AGENTS.md`, `../../subagents/README.md`, `../../subagents/cfd-subagent.md`, `../../subagents/research-subagent.md`, `../../subagents/setup-subagent.md`, `wiki/log.md`
- reason: user wants subagents implemented, but is intentionally skipping worktrees for now.
- what changed since last update: added a root-level subagent operating model with main-agent authority, lane boundaries, deployment rules, quality gates, and reusable prompt briefs for CFD, research, and setup subagents.
- current status: the repository now has an explicit lightweight subagent workflow that can be applied without extra branch or worktree overhead.
- blockers: this is a process implementation only; future tasks still depend on the main agent enforcing routing and deduplication discipline.
- next action: use the new subagent briefs on larger multi-step tasks and refine them only if repeated coordination failures appear.

## [2026-06-01] workflow-update | Start chat-cleanup handoff consolidation
- files created/updated: `wiki/progress/current-status.md`, `../../Setup report/order-dictionary.md`, `wiki/log.md`
- reason: user wants the folder and chat workflow cleaned up, with crucial information preserved in repo files before older chats are archived.
- what changed since last update: synced the live project status snapshot to the later May setup/log decisions, added an explicit no-archive guard for chats active on or after `2026-05-25`, and added last-known-state labels to the setup lineage dictionary so branch status is clearer without reopening old chats.
- current status: the repo now holds a clearer archive-safe handoff for project state and setup-branch status; recent chats within the last week remain intentionally unarchived.
- blockers: chat cleanup still depends on checking individual older threads against the durable files because the repository does not contain a direct chat inventory.
- next action: review older-than-`2026-05-25` chats one by one, confirm each thread's outcome is captured in the correct wiki/setup files, then archive only the threads that add no unrecovered information.

## [2026-05-29] model-update | Extend root repository contract to include setup-report system
- files created/updated: `../../AGENTS.md`, `wiki/log.md`
- reason: user requested that the repository-level operating contract explicitly recognize `Setup report/` alongside `CFD_wiki` and `ResearchProject_wiki`.
- what changed since last update: added `Setup report/` as a third knowledge system at the root level, defined its role, added routing/orchestration rules, and documented filename/order-dictionary discipline.
- current status: the root contract now distinguishes reusable CFD knowledge, project-trace knowledge, and ordered setup-branch records as separate responsibilities.
- blockers: none.
- next action: follow the new root routing rule so future setup-branch work updates `Setup report/` deliberately instead of being treated as ad hoc project notes.

## [2026-05-29] model-update | Rename setup reports into strict sequence
- files created/updated: `../../Setup report/00-baseline-spiral-boc-reference.md`, `../../Setup report/01-split-two-zone-massflow-inlet.md`, `../../Setup report/02-split-two-zone-velocity-inlet-brine-outlet.md`, `../../Setup report/02b-vof-split-inlet-transient.md`, `../../Setup report/03-mixed-wet-half-velocity-inlet.md`, `../../Setup report/03a-mixed-wet-half-velocity-inlet-water-pool.md`, `../../Setup report/04-mixed-wet-half-actual-area.md`, `../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`, `../../Setup report/06-pure-phase-split-fixed-velocity.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `../../Setup report/order-dictionary.md`, `wiki/index.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`, `../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
- reason: user approved the strict setup-report ordering and requested the actual filename cleanup.
- what changed since last update: renamed the setup reports to stable ordered filenames and updated internal report links plus project/wiki references to the new names.
- current status: `Setup report/` now follows a fixed sequence with branch suffixes, and the order dictionary remains the source-of-truth mapping page.
- blockers: none for the rename itself; sequence meaning is still based on the reconstructed lineage already documented in the dictionary.
- next action: use the numbered filenames consistently for future setup reports, adding new branch suffixes instead of renaming old files again.

## [2026-05-29] model-update | Add setup-report order dictionary and stable rename map
- files created/updated: `../../Setup report/order-dictionary.md`, `wiki/index.md`, `wiki/log.md`
- reason: user wants `Setup report/` cleaned into a strict sequence so the setup lineage is easier to follow and future report renaming can stay stable without using words like `current`.
- what changed since last update: reconstructed the likely setup-report order from project logs, experiment pages, and internal report references; added a filename mapping with fixed order numbers and branch suffixes.
- current status: `Setup report/order-dictionary.md` now defines the proposed sequence `00 -> 01 -> 02 -> 03 -> 04 -> 07` with side branches `02b`, `03a`, `05`, and `06`; no files have been renamed yet.
- blockers: the order is still partly reconstructed from logs and memory, especially around the relative timing of `02`, `02b`, and `03`.
- next action: confirm the proposed sequence from memory, then rename the setup reports and update internal links using the dictionary as the source of truth.

## [2026-05-28] model-update | Create pure liquid/steam actual-area velocity-inlet report
- files created/updated: `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user requested a new setup report using the pure liquid / pure steam inlet design from `wiki/model/inlet-regimes.md`, inheriting all other settings from the mixed wet-half actual-area report.
- current status: active report uses velocity `27.118 m/s`, liquid width `0.006754 m`, steam width `0.717246 m`, turbulence intensity `2.10999999 %`, liquid hydraulic diameter `0.01338 m`, and steam hydraulic diameter `0.72061 m`.
- blockers: confirm the liquid side maps to the outer-wall side and verify mesh resolution across the `6.754 mm` liquid strip.
- next action: build the two named inlet faces and verify inlet fluxes match liquid `116.92 kg/s`, steam `80.69 kg/s`, total `197.61 kg/s` after initialization.

## [2026-05-28] decision | Select current-area exact-mass pure-phase velocity
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user decided to use the velocity calculated from the current inlet area rather than preserving the reported `26.81 m/s` velocity.
- current status: active pure liquid / pure steam split-inlet setup uses `27.118 m/s`, liquid-side area `0.0048896 m2`, steam-side area `0.5192864 m2`, and split line `0.006754 m` from the liquid-side edge.
- blockers: physical side mapping and mesh resolution of the `6.754 mm` liquid strip still need checking before running.
- next action: build the two named inlet faces, set both velocity inlets to `27.118 m/s`, and verify inlet fluxes match liquid `116.92 kg/s`, steam `80.69 kg/s`, total `197.61 kg/s`.

## [2026-05-28] model-update | Create fixed-velocity pure-phase split report
- files created/updated: `../../Setup report/06-pure-phase-split-fixed-velocity.md`, `wiki/index.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user corrected that the Purnanto `1600 kJ/kg` spiral-inlet velocity should stay at `26.81 m/s` and requested a completely new setup report.
- what changed since last update: the pure-phase split now has a fixed-velocity report separate from the exact-mass `27.118 m/s` calculation.
- current status: for the current `0.724 m x 0.724 m` inlet, the split line remains `0.006754 m` from the liquid-side edge because the phase volumetric ratio is unchanged; expected inlet flow at `26.81 m/s` is liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`.
- blockers: exact Purnanto mass flow at `26.81 m/s` would require `0.5301985 m2` total inlet area, larger than the current `0.524176 m2`; the `6.754 mm` liquid strip also needs mesh-resolution verification.
- next action: build the two named inlet faces, assign both velocity inlets at `26.81 m/s`, and verify inlet flux reports before running long iterations.

## [2026-05-28] model-update | Calculate pure liquid/steam split-inlet area
- files created/updated: `../../Setup report/04-mixed-wet-half-actual-area.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`, `../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`, `../../CFD_wiki/wiki/log.md`
- reason: user requested a corrected area ratio / `x` split for a pure-liquid plus pure-steam inlet while preserving Purnanto's `1600 kJ/kg` mass flows and correct inlet velocity.
- what changed since last update: the previous 50/50 split assumption is superseded for the pure-phase equal-velocity setup.
- current status: using `0.724 m x 0.724 m`, liquid `116.92 kg/s`, steam `80.69 kg/s`, liquid density `881.77 kg/m3`, and steam density `5.73 kg/m3`, the common velocity is `27.118 m/s`; liquid area is `0.0048896 m2`; steam area is `0.5192864 m2`; split line is `0.006754 m` from the liquid-side edge if split along `x`.
- blockers: exact outer-wall liquid side must be mapped on the real inlet orientation, and the `6.754 mm` liquid strip must be mesh-resolved.
- next action: create named inlet faces using the calculated split and verify Fluent phase mass-flow reports before interpreting separator performance.

## [2026-05-27] model-update | Define complete two-phase no-brine-outlet run
- files created/updated: `../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- purpose: create the report and project trace for the next spiral-inlet setup using one complete mixed two-phase velocity inlet, no active brine outlet, and a `5000`-iteration run budget.
- assumptions introduced/removed: introduced the assumption that "complete two phase inlet" means one full inlet boundary with uniform bulk liquid volume fraction `0.009328`; retained uncertainty around the actual Fluent boundary-zone name and whether the no-brine-outlet geometry has the face absent or closed as a wall.
- next immediate action: set the full inlet as `Velocity Inlet` at `26.81 m/s` with liquid volume fraction `0.009328`, confirm the brine outlet is inactive, then run/save checkpoints at `1000`, `3000`, and `5000` iterations.

## [2026-05-27] model-update | Start mixed wet-half actual-area report
- files created/updated: `../../../Setup report/04-mixed-wet-half-actual-area.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user provided the actual split-inlet area and asked to start a report with inlet mass flow, then later add mass flux, separator efficiency, and visual findings.
- assumptions introduced/removed: introduced `MWH-ACTUAL-AREA-2026-05-27` as an assumed report label and interpreted `2.6209e5 mm2` as the area of each split inlet half; no separator-efficiency claim added yet.
- current status: actual-area inlet calculation gives total liquid inlet `115.59 kg/s`, total steam inlet `79.77 kg/s`, and total inlet flow `195.36 kg/s` at `26.81 m/s`.
- next immediate action: add outlet fluxes, mass flux discussion, efficiency calculation, and contour/vector findings after post-processing values are available.

## [2026-05-21] model-update | Log preliminary FFF-2-OP0 flux result
- files created/updated: `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user ran just above 100 iterations of the pressure-reference parity parent case and reported residual/flux behavior.
- assumptions introduced/removed: introduced an `Inferred` interpretation that pressure-reference parity may improve residual smoothness but has not solved physical liquid drainage; retained `FFF-2-OP0` as diagnostic-only.
- current status: residuals are smoother and flattening, steam flux is close to balanced, but liquid flux is not physically balanced because liquid inlet is approximately `109.8065 kg/s` and liquid outlet flux is effectively zero.
- next action: inspect liquid volume fraction movement near the brine outlet and extend only as a short trend test if liquid drainage is developing; otherwise proceed to a brine outlet control case.

## [2026-05-21] project-update | Add post-triage two-phase modelling upgrade gate
- files created/updated: `wiki/project/roadmap.md`, `wiki/log.md`
- reason: user wanted the newer CFD-wiki comparison of two-phase modelling approaches added to the roadmap after the current Phase 0 triage has progressed.
- assumptions introduced/removed: introduced a gated recommendation to keep Purnanto 2013 as the separator geometry baseline, borrow Mubarok 2020 for modern geothermal Fluent workflow/validation discipline if needed, keep DPM as a post-convergence carryover check, and reserve EWF+DPM three-field annular modelling for future work.
- next immediate action: continue Phase 0/R1-R4 parent-case triage before making physics-model changes.

## [2026-05-21] model-update | Record FFF-2 pressure-reference parity control
- files created/updated: `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user prepared a controlled `FFF-2` derivative after confirming the informit/Purnanto paper used zero relative atmospheric pressure so gauge and absolute pressures are equivalent.
- assumptions introduced/removed: introduced an `Assumed` temporary run label `FFF-2-OP0`; retained the interpretation that this is a parent convergence-control test, not a water-pool or geometry change.
- current status: next parent diagnostic keeps all `FFF-2` settings unchanged except `Operating Pressure = 0 Pa`, with inlet pressure `1140000 Pa` and both pressure outlets `1120000 Pa`.
- next action: run a short diagnostic and compare residual trend, phase mass-flow reports, and net liquid imbalance against original `FFF-2`.

## [2026-05-21] model-update | Prioritize parent convergence issue
- files created/updated: `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/log.md`
- reason: user clarified that the more important issue is convergence/mass-balance failure in `FFF-2` even without initialized water.
- assumptions introduced/removed: promoted `FFF-2` parent convergence recovery to the first blocker; downgraded water-pool depletion to a downstream child-case problem that should be revisited only after the parent case is understood.
- current status: roadmap now starts from `FFF-2` residual/monitor/flux triage, not from the water-pool initialized child case.
- next action: load the `FFF-2` case/data pair, extract residual and phase mass-balance history, then run one controlled parent convergence fix.

## [2026-05-21] model-update | Reset future scope around usable simulation evidence
- files created/updated: `wiki/project/objective-and-scope.md`, `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/gaps/open-questions.md`, `wiki/log.md`
- reason: user realised only two documented simulations exceed `1000` iterations, so lower-iteration data should not drive future project scope or report-facing performance claims.
- assumptions introduced/removed: introduced an `Inferred` evidence boundary that `FFF-2` and `MWH-WP-2026-05-07-A` are the only active diagnostic simulation evidence; downgraded lower-iteration outputs to setup/debug history only.
- current status: future scope now centers on rebuilding a stable reference case before inlet-regime comparison, with both above-threshold runs still classified as diagnostic rather than validation evidence.
- next action: extract post-processing evidence from `MWH-WP-2026-05-07-A`, then run a controlled reference-case path with documented monitor stability and phase mass balance.

## [2026-05-21] project-update | Add spiral-inlet run validation template
- files created/updated: `../template/spiral-inlet-run-validation-template.md`, `wiki/index.md`, `wiki/log.md`
- reason: user asked for a fill-in Markdown template for values and figures to make for each simulation/setup.
- assumptions introduced/removed: template assumes the active geometry is spiral inlet and keeps wider BOC/Lazalde-Crabtree values only as sanity-check fields where comparable.
- current status: a reusable run card template now captures setup, validation targets, sanity calculations, convergence, required figures, and report claim strength.
- next action: copy the template for each new Fluent run and fill it immediately after post-processing.

## [2026-05-21] query | Record Fluent case-data post-processing step
- files created/updated: `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user has available `.cas.h5` and `.dat.h5` files and wants to inspect fluxes, plots, and contours before deciding the next model action.
- assumptions introduced/removed: introduced an `Inferred` workflow that the large `.dat.h5` file should be loaded with the matching setup/mesh `.cas.h5` before using Fluent post-processing.
- current status: next diagnostic work can start from loading the available case/data pair and extracting flux, phase-contour, vector, and pathline evidence.
- next action: load the case/data pair in Fluent and export the evidence listed in `wiki/progress/current-status.md`.

## [2026-05-20] project-update | Narrow roadmap validation to spiral inlet
- files created/updated: `wiki/project/roadmap.md`, `wiki/model/validation.md`, `wiki/log.md`
- reason: user clarified that the active focus is the spiral-inlet geometry, not Bangma, except where older evidence also applies to spiral-inlet or general BOC behavior.
- assumptions introduced/removed: removed Bangma as a direct benchmark target; retained Lazalde-Crabtree and wider BOC evidence only as empirical comparison or sanity-check context where transferable.
- current status: validation gates now prioritize spiral-inlet CFD behavior and treat other geometries as method/context.
- next action: build the validation target table specifically for the active spiral-inlet case.

## [2026-05-20] project-update | Incorporate validation sanity checks into roadmap
- files created/updated: `wiki/project/roadmap.md`, `wiki/model/validation.md`, `wiki/log.md`
- reason: user asked to incorporate past validation methods, analytical checks, and sanity checks into the roadmap.
- assumptions introduced/removed: introduced Lazalde-Crabtree/Bangma efficiency and pressure-drop checks, Purnanto-style outlet steam quality/DPM carryover validation, and Mubarok-style field/mesh validation reporting as roadmap gates.
- current status: roadmap now requires inlet-velocity, carryover/efficiency, pressure-drop, and mesh/output-stability checks before accepting production results.
- next action: build the project-specific validation target table and calculate quick sanity values for the current `MWH-WP-2026-05-07-A` result.

## [2026-05-20] project-update | Add validation gates to roadmap
- files created/updated: `wiki/project/roadmap.md`, `wiki/model/validation.md`, `wiki/log.md`
- reason: user noted that without analytical or real-world comparison targets, there is no way to know whether Fluent results are on the right track.
- assumptions introduced/removed: introduced a validation hierarchy from real-world/test data to analytical/design estimates, literature CFD trends, and internal A/B comparisons; downgraded internal comparison alone to sensitivity evidence rather than validation.
- current status: long production runs now require a target table or explicit `trend-only` label before results are used for design claims.
- next action: collect partner analytical/parameter-sweep outputs for pressure drop, steam outlet quality/carryover, brine outlet liquid flow, and efficiency before accepting R4/R5 results.

## [2026-05-20] project-update | Create run-efficiency roadmap
- files created/updated: `wiki/project/roadmap.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user needs a roadmap from the current state because ANSYS setup and each solve take significant time.
- assumptions introduced/removed: introduced an operating rule that every Fluent run must answer one primary decision question with a planned comparison and stop condition; retained uncertainty around whether the current failure is water-pool depletion, steam outlet intake behavior, brine outlet pressure, inlet allocation, mesh quality, or numerics.
- current status: roadmap now starts from `MWH-WP-2026-05-07-A` and prioritizes pre-run triage, cheap control runs, then only later inlet-regime comparison and sensitivity evidence.
- next action: complete Phase 0 evidence extraction before launching the next long run.

## [2026-05-20] progress-update | Summarize current project state
- files created/updated: `wiki/progress/current-status.md`, `wiki/log.md`
- reason: user asked for an update on the current state of the project.
- what changed since last update: no newer documented simulation has superseded `MWH-WP-2026-05-07-A`; the project remains in split-inlet/brine-outlet troubleshooting.
- current status: partner validation/parameter-sweep comparison remains separate, while Shuhei's active lane is diagnosing the mixed wet-half velocity-inlet case with lower water-pool initialization.
- blockers: current result is not quantitatively usable because liquid outflow greatly exceeds liquid inflow and steam-outlet liquid carryover is very high; likely causes remain water-pool depletion in a steady solve, steam outlet intake behavior, brine outlet pressure behavior, initialization history, inlet phase allocation, mesh quality, or numerics.
- next action: extract local evidence near the steam outlet intake and compare flux history at multiple iteration counts before choosing transient setup, steam-outlet geometry sensitivity, water-pool height sensitivity, or brine outlet pressure tuning.

## [2026-05-18] query | Ingest newest water-pool initialized inlet result
- files created/updated: `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/progress/experiments.md`, `wiki/model/inlet-regimes.md`, `wiki/log.md`
- reason: user pointed to the newest setup report, `Setup report/03a-mixed-wet-half-velocity-inlet-water-pool.md`, as the latest attempted case.
- notable result: the 3500-iteration steady run developed more plausible swirl and activated brine outlet liquid removal, but liquid outflow greatly exceeded liquid inflow and steam outlet liquid carryover was very high.
- assumptions introduced/removed: introduced working diagnosis that the run is draining an initialized liquid inventory inside a steady solve; added steam outlet intake geometry as an active sensitivity source.
- next action: inspect liquid volume fraction, velocity vectors, streamlines/pathlines, and iteration-history fluxes near the steam outlet before choosing between transient test, steam outlet geometry revision, water-pool height sensitivity, or brine outlet pressure tuning.

## [2026-05-18] progress-update | Reframe Shuhei's lane around split-inlet troubleshooting
- files created/updated: `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/model/inlet-regimes.md`, `wiki/log.md`
- reason: user reported that partner is handling validation/parameter sweep comparison while Shuhei is stuck on the two-phase inlet design with brine outlet and bottom-water initialization.
- what changed since last update: active focus shifted from general baseline/inlet planning to diagnosing the current problematic split-inlet/brine-outlet case.
- current status: partner validation work should remain separate; Shuhei's immediate task is to classify the current result failure mode before making further design changes.
- blockers: current result problem is unclassified; likely candidates include initialization artifact, brine outlet boundary behavior, inlet phase allocation/orientation, mesh quality, or numerics.
- next action: save the current result as a diagnostic reference, then run a one-change control comparing bottom-water initialization with a simpler initialization while keeping inlet/outlet setup fixed.

## [2026-04-22] progress-update | Initialise progress-tracking structure
- files created/updated: `AGENTS.md`, `wiki/index.md`, `wiki/log.md`, `wiki/project/objective-and-scope.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/technical/sources/purnanto-etal-2013.md`, `wiki/literature/matrix.md`, `wiki/model/baseline-cfd.md`, `wiki/model/inlet-regimes.md`, `wiki/model/validation.md`, `wiki/gaps/open-questions.md`
- reason: enforce separation of project scope vs technical CFD detail and start explicit progress tracking.
- assumptions introduced/removed: introduced assumption that current active technical baseline is the Bangma-based two-phase recreation run.
- next action: execute convergence debugging runs and log each run using the experiment schema.

## [2026-05-29] model-update | Link project inlet-regime notes to consolidated pure-phase CFD setup
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/log.md`
- purpose: add a project-facing pointer to the reusable CFD settings sheet so the detailed Fluent stack stays in `CFD_wiki` instead of being duplicated in the research wiki.
- assumptions introduced/removed: no new modelling assumption; this change only adds cross-wiki traceability to the consolidated pure-phase split-inlet setup.

## [2026-04-22] progress-update | Shift focus to result interpretation and KPI-driven iteration
- files created/updated: `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/gaps/open-questions.md`, `wiki/log.md`
- reason: user reported progress in model setup but uncertainty in interpreting CFD outputs and selecting next model-improvement actions.
- assumptions introduced/removed: introduced assumption that a fixed KPI and post-processing template is required before further A/B changes can be judged reliably.
- current status: baseline setup exists; interpretation framework is now the immediate blocker alongside convergence stability.
- blockers: unclear decision metrics for pressure/phase/flow outputs; no fixed mapping from visualization to parameter-change decisions.
- next action: define run-level KPI set and evaluate each run against the same contour/probe/outlet metrics before choosing the next setting change.

## [2026-04-30] query | Clarify Mixture vs Eulerian upgrade path for tangential-inlet report
- files created/updated: `../Setup report/00-baseline-spiral-boc-reference.md`, `wiki/model/baseline-cfd.md`, `wiki/log.md`
- purpose: document that the source paper selected `Mixture` for the baseline separator case while acknowledging `Eulerian` may be more accurate, then add a project-specific accuracy-upgrade sequence.
- assumptions introduced/removed: introduced project recommendation that `Eulerian` should be tested only after baseline parity, local mesh refinement, and improved inlet realism are established.
- next immediate action: run a controlled baseline `Mixture` case, then perform one-at-a-time sensitivity tests for mesh and inlet realism before any `Eulerian` comparison.

## [2026-04-30] model-update | Define two-zone split-inlet as next realism upgrade
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/index.md`, `wiki/log.md`
- purpose: record the next inlet-regime test as a geometry/mesh-level split of the inlet into wall-side liquid and inner-side steam while preserving the baseline solver stack for A/B comparison.
- assumptions introduced/removed: introduced first-pass assumption that the inlet can be split into equal-area outer and inner halves with pure-phase assignment; flagged geometry naming inconsistency and inlet-orientation definition as active blockers.
- current status: split-inlet implementation route is defined, but orientation confirmation is still required before the case build.
- blockers: inconsistent tangential/spiral naming and ambiguous `left/right` wording for actual inlet-face orientation.
- next action: confirm active geometry and side mapping, then split the inlet face, remesh, and run the first controlled comparison.

## [2026-04-30] model-update | Confirm spiral-inlet geometry for split-inlet plan
- files created/updated: `../Setup report/01-split-two-zone-massflow-inlet.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: remove the tangential-versus-spiral ambiguity from the split-inlet planning notes after user clarification that the active geometry is the spiral inlet.
- assumptions introduced/removed: removed the geometry-type ambiguity; retained only the remaining orientation ambiguity for outer-wall versus inner-side inlet mapping.
- current status: geometry type is now fixed as spiral inlet; the remaining setup question is exact side mapping on the inlet face.
- blockers: inlet-face side mapping is still unresolved.
- next action: identify the outer-wall half and inner/core half on the actual spiral-inlet face, then split the boundary accordingly.

## [2026-05-06] query | Record mesh-quality implication from CFD synthesis
- files created/updated: `wiki/model/baseline-cfd.md`, `wiki/gaps/open-questions.md`, `wiki/index.md`, `wiki/log.md`
- purpose: add a project-facing note that the current minimum orthogonal quality of 6.73e-2 requires mesh auditing and independence checks before report-quality conclusions.
- assumptions introduced/removed: introduced an `Inferred` project interpretation that the quality value is a warning trigger rather than automatic case rejection.
- next immediate action: locate worst cells, classify whether they are in critical inlet/swirl/outlet regions, then run a controlled mesh refinement comparison.

## [2026-05-06] model-update | Update active mesh scale to 1.8M nodes
- files created/updated: `wiki/progress/current-status.md`, `wiki/model/baseline-cfd.md`, `wiki/gaps/open-questions.md`, `wiki/technical/sources/purnanto-etal-2013.md`, `wiki/log.md`
- purpose: replace the outdated approximately 300k-node active-mesh interpretation with the user-reported approximately 1.8M-node mesh.
- assumptions introduced/removed: retired the assumption that global mesh density is the primary deficiency; retained local mesh quality and worst-cell location as active risks.
- next immediate action: inspect worst-quality cell locations and repair/refine critical regions before using the mesh for report-quality conclusions.

## [2026-05-06] query | Add inflation note to mesh-quality decision
- files created/updated: `wiki/model/baseline-cfd.md`, `wiki/log.md`
- purpose: record that inlet/outlet worst-cell quality should be treated as a local sizing/geometry/inflation interaction rather than a global node-count issue.
- assumptions introduced/removed: introduced an `Inferred` caution that inflation layers can worsen quality if they collapse near sharp inlet/outlet transitions.
- next immediate action: inspect whether worst cells are ordinary tetra/sliver cells or collapsed inflation layers before choosing the next mesh repair.

## [2026-05-28] query | Clarify velocity-inlet hydraulic diameter for square inlet
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/log.md`
- purpose: record the project-specific Fluent velocity-inlet turbulence inputs for the current `0.724 m x 0.724 m` inlet and distinguish the physical square inlet from artificial split inlet zones.
- assumptions introduced/removed: introduced the first-run recommendation to use `Dh = 0.724 m` for the square inlet, including both split zones if they are only phase-allocation subdivisions of the same physical duct.
- next immediate action: set the velocity-inlet turbulence method to `Intensity and Hydraulic Diameter`, retain `2.109999 %` if reproducing the baseline, and use `0.724 m` hydraulic diameter unless deliberately running a split-zone turbulence sensitivity test.

## [2026-05-28] query | Add phase-specific split-inlet turbulence sensitivity
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/log.md`
- purpose: calculate zone-specific hydraulic diameters for the pure-liquid and pure-steam split velocity inlets and capture risks before applying them in Fluent.
- assumptions introduced/removed: introduced a candidate sensitivity setup with liquid-zone `Dh = 0.01338 m` and steam-zone `Dh = 0.72061 m`; retained the warning that this is a turbulence-length-scale change in addition to the phase split.
- next immediate action: if testing this, save a matching comparison case with `Dh = 0.724 m` on both zones, then compare inlet `k`, dissipation, turbulent viscosity ratio, residual behavior, and near-inlet phase/velocity fields.
## [2026-06-09] query | Add no-brine-outlet spiral geometry record
- files created/updated: `wiki/technical/v2-purnanto-spiral-inlet-geometry.md`, `wiki/index.md`, `wiki/log.md`
- purpose: preserve the current no-brine-outlet spiral-inlet dimension record as a short project-technical page covering Purnanto-derived vessel dimensions plus the user's reconstructed dish-head and scroll-curvature calculations.
- assumptions introduced/removed: introduced an explicit project-only reconstruction note that the recorded dish-head crown/knuckle radii and three-arc scroll-wall centres are assumed geometry-rebuild aids, not fully reported paper dimensions.
- next immediate action: use this page as the geometry reference when rebuilding or checking the no-brine-outlet spiral-inlet CAD and keep any later curve changes traceable here.
## [2026-06-09] query | Correct v2 spiral inlet inner-wall note
- files created/updated: `wiki/technical/v2-purnanto-spiral-inlet-geometry.md`, `wiki/log.md`
- purpose: correct the geometry record so the inner wall is described as straight and perpendicular to the inlet face, rather than as a tangent line plus curved vessel-following transition.
- assumptions introduced/removed: removed the earlier inner-wall tangent-point construction from the `v2` record and replaced it with the user's stated simpler straight-wall assumption.
- next immediate action: use the corrected `v2` page as the geometry reference and only add inner-wall curvature later if the actual CAD branch changes.

## [2026-06-10] model-update | Record semi-automated `mesh-trial1` mesh-improvement workflow
- files created/updated: `wiki/technical/mesh-trial1-semi-automated-workflow.md`, `wiki/index.md`, `wiki/log.md`
- purpose: capture the project-facing workflow that uses the current `mesh-trial1.meshdat` plus baseline `mesh-trial1.msh` for conservative mesh-control trials with PyFluent reopen and comparison checks.
- assumptions introduced/removed: introduced a provisional `1,000,000`-cell target for the first audit run because the user did not supply a final target; retained the observation that the `.meshdat` reopen is diagnostically weaker than the exported baseline `.msh`.
- next immediate action: confirm the exact required-zone text contract, export conservative Workbench trial meshes, and rerun the workflow with `--trial-mesh` validation inputs.

## [2026-06-10] model-update | Tighten split-inlet mesh workflow contract and rerun baseline audit
- files created/updated: `wiki/technical/mesh-trial1-semi-automated-workflow.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`, `../../../PyAnsys/input/required-zones-mesh-trial1.txt`, `../../../PyAnsys/output/meshdat-semi-automated/workflow-report.md`, `../../../PyAnsys/output/meshdat-semi-automated/workflow-report.json`
- purpose: update the semi-automated split-inlet workflow so exact Fluent-exported zone names and boundary types are enforced, make cell count diagnostic-only, and rerun the overwritten `mesh-trial1` baseline audit with the corrected named selections.
- assumptions introduced/removed: removed the provisional idea that cell target should be a main success rule; introduced the explicit split-inlet required-zone contract with `liquid-inlet` and `steam-inlet` kept separate; retained the observation that `.meshdat` remains a weaker diagnostic source than the exported baseline `.msh`.
- next immediate action: fix the Meshing/export naming so the exported baseline preserves `liquid-inlet`, `steam-inlet`, and `wall-smooth_spiral_separator` exactly, then rerun the baseline audit before accepting any trial meshes.
## [2026-07-29] progress-update | Gate split-inlet carrier mesh-convergence study
- files created or updated: `../../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`, `../../../Setup report/order-dictionary.md`, `../../../PyAnsys/scripts/analysis/analyze_mesh_convergence.py`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/log.md`
- purpose: identify the authoritative actual setup-07 split-inlet case, define a carrier-only systematic mesh study and GCI analysis contract, and record why no long run was launched.
- assumptions introduced or retired: retired `baseline_spiral_inlet.cas.h5` as the split-inlet authority; retained `FFF.1-2.cas.h5` as actual-state authority while explicitly leaving intended-versus-actual numerics unresolved.
- next immediate action: restore remote Fluent access, query processor count, verify inlet orientation/areas and full settings readback, and create or locate the coarse/medium/fine meshes.

## [2026-08-05] progress-update | Close split-inlet mesh study as inventory-drifting diagnostic
- files created or updated: `../../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`, `../../../Setup report/order-dictionary.md`, `../../../PyAnsys/scripts/inspection/inspect_split_inlet_liquid_inventory.py`, `../../../PyAnsys/scripts/analysis/plot_split_inlet_liquid_inventory.py`, `../../../PyAnsys/output/split_inlet_mesh_convergence_20260801/STUDY_DIAGNOSTIC_CLOSURE_20260805.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/log.md`
- purpose: reconcile the completed seven-mesh carrier campaign, the separate 900k 6000-iteration extension and the direct checkpoint liquid-inventory evidence.
- assumptions introduced or retired: retired the planned/preflight-blocked state and the idea that further steady iterations might merely polish convergence; retained the intentional bottom-wall geometry but classified its increasing liquid inventory as incompatible with an accepted steady mesh-convergence claim.
- current status: all seven formal meshes and the 900k extension are complete; Fluent is left at the verified 6000 checkpoint; DPM remains off; overall evidence is `Diagnostic — iteration independence and mesh independence unresolved`.
- blockers: liquid inventory increases `64.37%` between iterations 4000 and 6000 while pressure rises `9.73%`; pressure/velocity stability limits remain failed.
- next immediate action: freeze setup 07a and define a new liquid-discharge branch for steady performance, or a separately scoped transient branch only for finite-time filling/redistribution.

## [2026-08-10] post-processing | Build setup-07 Tuesday meeting evidence package

- files created or updated: `../../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md`, figures `00-09`, `visual_manifest.json`, `fluent/fluent_graphics_manifest.json`, `../../PyAnsys/scripts/analysis/build_setup07_meeting_visuals.py`, `../../PyAnsys/scripts/analysis/build_setup07_meeting_composites.py`, `../../PyAnsys/scripts/inspection/probe_setup07_meeting_graphics.py`, `../../PyAnsys/scripts/inspection/export_setup07_meeting_graphics.py`, `../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`, `../../Setup report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/model/validation.md`, `wiki/log.md`.
- purpose: convert the completed setup-07a/07b/07c diagnostic evidence into matched Fluent contours, verified carrier pathlines, quantitative plots and a supervisor-facing decision narrative for the 2026-08-11 meeting.
- evidence: setup-07a 900k liquid inventory increases `104.05 -> 171.03 kg` and pressure drop `31.03 -> 34.05 kPa` from iterations 4000 to 6000; setup-07c removes `22.49 kg/s`, only `19.2%` of the liquid feed.
- controls: matched `x=-1.5 m` cell-value contours and fixed scales; pathlines released from `liquidinlet` in the Mixture carrier domain; DPM off. A steam-inlet pathline and an incomplete boundary map were excluded after readback mismatch.
- assumptions introduced or retired: no new physics assumption; strengthened the existing formulation diagnosis while explicitly retaining the rule that steady iteration drift is not physical-time accumulation.
- live-state safety: post-processing only, no initialization/iterations/case-data overwrite; Fluent restored to setup-07c saved ramp-reset final with DPM read back off.
- next immediate action: present the diagnostic package, then add and qualify a resolved brine outlet on one medium mesh before restarting mesh convergence, DPM or EWF.

## [2026-08-10] model-update | Launch setup-07d capacity-matched sink diagnostic

- files created or updated: `../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`, `../../Setup report/order-dictionary.md`, `../../PyAnsys/scripts/setup/run_setup07c_thick_sink_qualification.py`, `../../PyAnsys/scripts/connection/check_setup07d_strong_sink_status.py`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/log.md`.
- purpose: use the available compute window before geometry editing to test whether a fivefold stronger setup-07c sink can establish liquid closure and iteration-independent monitors.
- controlled change: `tau=0.02 s` instead of `0.1 s`; selected from the setup-07c endpoint capacity estimate `2.24882 kg / 116.92 kg/s = 0.01923 s`. All geometry, mesh, carrier physics, boundary conditions, initialization, solver controls, sink band and DPM-off state are retained.
- execution: clean original 900k rebuild, guarded 1,000-iteration ramp, up to 2,000 full-strength iterations in 250-iteration blocks, separate checkpoints and non-overwriting output branch.
- initial status: detached controller launched and Fluent health verified serving; preflight began with DPM off.
- evidence-use label: diagnostic sink-capacity sensitivity only; cannot establish separator efficiency, mesh convergence, a physical free surface or physical-time accumulation.
- next immediate action: supervise through guarded ramp/full-strength blocks, analyze closure and drift, then add the result to the Tuesday meeting package without changing the resolved-brine-outlet recommendation unless the evidence justifies a narrower conclusion.

## [2026-08-10] result | Complete setup-07d fixed-strength sink diagnostic

- files created or updated: `../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`, `../../Setup report/order-dictionary.md`, `../../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/model/validation.md`, `wiki/log.md`.
- execution: the accepted third attempt restored the verified source-hooked setup-07c prepared checkpoint, fresh Hybrid Initialized and completed 1,000 guarded-ramp plus 2,000 full-strength iterations. Separate checkpoints and both zero-production-iteration recovery attempts are preserved; final ramp is zero and DPM is off.
- endpoint: sink `46.9874 kg/s` (`40.19%` of liquid feed), corrected liquid imbalance `59.8122%`, source-inclusive mixture imbalance `35.1679%`, domain/band liquid inventory `66.6560/0.93975 kg`, pressure drop `26.8901 kPa`, continuity `0.229682`.
- stability: final-500 pressure, sink, inventory, outlet velocity and domain velocity drift `6.618/23.044/14.120/3.161/6.901%`; zero acceptance windows.
- interpretation: a fivefold coefficient produced only a `2.09x` endpoint sink because liquid in the marked band depleted. Local fixed-strength tuning improves closure but does not establish a conserved, iteration-independent carrier state.
- classification: `Completed diagnostic / unresolved`; no mesh-convergence, outlet-hydraulics, efficiency, free-surface or physical-time claim.

## [2026-08-10] post-processing | Add fixed-strength sensitivity figures to Tuesday package

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07_sink_strength_comparison.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md`, figures `10-12`, `fixed_sink_strength_comparison.csv`, `fixed_sink_strength_endpoints.csv`, `visual_manifest.json`, and project status/validation records.
- evidence: matched setup-07c/07d full-strength histories show improved liquid removal but persistent pressure/inventory drift; the 5x coefficient versus 2.09x achieved sink is visualized alongside declining band liquid inventory and unresolved continuity/VF residual histories.
- safety: post-processing used saved CSV/JSON evidence only; it did not connect to or mutate Fluent.
- meeting use: the figures strengthen the resolved-brine-outlet recommendation and explicitly distinguish steady-solver mass defect from physical transient accumulation.

## [2026-08-10] model-update | Launch setup-07e adaptive mass-balance sink control

- files created or updated: `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `../../Setup report/order-dictionary.md`, `../../PyAnsys/scripts/setup/run_setup07d_from_prepared07c.py`, `../../PyAnsys/scripts/connection/check_setup07e_mass_balance_control_status.py`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/log.md`.
- purpose: use the remaining no-geometry compute window to separate missing liquid closure from pressure/velocity/residual stability by commanding the existing qualified sink toward `116.92 kg/s`.
- control law: every 100 iterations, `tau_next = clamp(M_liquid,band/116.92, 0.002, 0.2) s`; the existing source and complete 92,058-cell band remain unchanged.
- execution: verified prepared 900k source-hooked checkpoint, fresh Hybrid Initialization, guarded 1,000-iteration ramp and up to 2,000 full-strength iterations with separate checkpoints. One controller is active; DPM/EWF remain off.
- evidence-use label: diagnostic empirical global feedback only. Even exact numerical closure would not validate brine-outlet hydraulics or separator performance.
- next immediate action: supervise without launching duplicates, preserve ramp-zero final state, analyze all monitor/residual histories and add any defensible result to the Tuesday package.

## [2026-08-10] code-update | Harden setup-07e adaptive feedback helper

- files created or updated: `../../PyAnsys/src/pyansys_fluent/constant_water_level_sink.py`, `../../PyAnsys/scripts/setup/run_setup07d_from_prepared07c.py`, `../../PyAnsys/tests/test_constant_water_level_sink.py`, `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/log.md`.
- change: factored the bounded `tau=M_liquid,band/target_sink` calculation into a reusable validation helper and made command-line R1 iteration/block limits authoritative in the generic controller.
- verification: eight constant-water-level sink unit tests pass, including dimensional consistency, empty-band behavior, both clamp limits and invalid-input rejection; Python compilation and scoped whitespace checks pass.
- live-run safety: the active controller was already loaded with the equivalent feedback calculation. No Fluent setting, iteration, checkpoint or controller process was changed by this code-only hardening.

## [2026-08-10] validation | Prove setup-07c/07d controlled-comparison parity

- files created or updated: `../../PyAnsys/scripts/analysis/validate_setup07d_controlled_comparison.py`, `../../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/CONTROLLED_COMPARISON_AUDIT.json`, `.md`, `QUALIFICATION_RESULT.md`, `../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`, `wiki/model/validation.md`, `wiki/log.md`.
- exact evidence: canonical mesh-metric hash `e0763587...` and complete Fluent settings-readback hash `bad1be14...` match between 07c and 07d; band thickness, mask/source fields and mask volume also match.
- numerical repeatability: six matched pre-sink ramp rows remain within the established comparison limits: maximum pressure/inventory/outlet-flow difference `0.4474%` and maximum velocity/vorticity difference `0.7602%`.
- result: `PASS — accepted controlled diagnostic comparison`; the intended production change is isolated to `tau 0.1 -> 0.02 s` (5x coefficient).
- interpretation: the audit strengthens causal attribution of the 07d response to sink strength but does not validate the sink surrogate or upgrade the unresolved convergence result.

## [2026-08-10] post-processing | Visualize the inventory-limited sink mechanism

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07_sink_strength_comparison.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/16_inventory_limited_sink_mechanism.png`, `.svg`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `visual_manifest.json`, `wiki/log.md`.
- purpose: make the setup-07c/07d diminishing-return mechanism explicit for the Tuesday meeting while setup-07e continues computing.
- evidence: across eight matched full-strength samples per case, the implemented law is `sink=M_liquid,band/tau`; the five-times-stronger source finishes with only `0.94 kg` in the active band versus `2.25 kg` for setup-07c and therefore reaches `46.99 kg/s`, only `2.09x` the setup-07c endpoint.
- interpretation: the empirical volume sink is supply-limited by liquid entering its local band and is not a resolved brine-outlet flow condition. The figure is a controlled numerical-mechanism diagnostic, not a physical drain-law validation.
- safety: generated from completed setup-07c/07d CSV evidence only; no Fluent state was changed and DPM remains off in the active setup-07e run.

## [2026-08-10] process-control | Add setup-07 overnight evidence gate

- files created or updated: `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_COMPLETION_CHECKLIST.md`, `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/visual_manifest.json`, `wiki/log.md`.
- purpose: prevent the morning handoff from inferring success from controller termination alone by requiring explicit final-state, checkpoint, history, analysis, graphics, documentation and automation-shutdown evidence.
- live-run safety: the checklist and manifest update are local post-processing only; setup-07e continues under its single controller with DPM off.

## [2026-08-10] post-processing | Add setup-07e outlet-recirculation diagnostic

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_reversed_flow_visual.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/17_setup07e_pressure_outlet_reversed_flow.png`, `.svg`, `setup07e_pressure_outlet_reversed_flow.csv`, `setup07e_pressure_outlet_reversed_flow_summary.json`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `OVERNIGHT_COMPLETION_CHECKLIST.md`, `visual_manifest.json`, `wiki/log.md`.
- purpose: preserve the pressure-outlet reversed-flow face count reported in the live transcript and compare it with continuity at the latest common iteration grain.
- interpretation limit: reversed-face count describes changing outlet-recirculation topology; it is not backflow mass rate and cannot independently establish convergence or physical outlet behavior.
- safety: read-only local transcript/CSV post-processing; the single setup-07e controller remains active and DPM is off.

## [2026-08-10] code-update | Add residual evidence to setup-07e status checks

- files created or updated: `../../PyAnsys/scripts/connection/check_setup07e_mass_balance_control_status.py`, `../../PyAnsys/scripts/analysis/analyze_setup07e_control.py`, `wiki/log.md`.
- change: the read-only status command and generated interim/final analysis now report continuity, liquid-volume-fraction, turbulence and velocity residual endpoints plus the last-100-iteration endpoint direction. The status command also reports the latest transcript-observed iteration, controller-log age and live UDF ramp/tau/band-inventory separately from the authoritative saved milestone.
- interpretation: the directional change is explicitly not a convergence claim; residual levels remain subordinate to full-strength physical-monitor and mass-balance gates.
- verification: both scripts compile, the current interim JSON validates and the status command reads the iteration-600 evidence without changing Fluent.

## [2026-08-10] validation | Add setup-07e dry-band lineage audit

- files created or updated: `../../PyAnsys/scripts/analysis/analyze_setup07e_control.py`, `../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/INTERIM_ANALYSIS.json`, `.md`, `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/model/validation.md`, `wiki/log.md`.
- exact evidence: setup 07e and accepted setup 07d match at saved iterations 100, 200, 350, 500 and 750 with `0.000000%` difference in pressure, liquid inventory, mixture/vapor outlet flow, outlet/domain velocity and domain vorticity while both active bands are dry.
- interpretation: this passes a deterministic clean-start lineage check and shows tau changes are inactive without local liquid; it does not validate adaptive feedback, the sink surrogate or outlet hydraulics.
- safety: local CSV/JSON analysis only; the live controller was not changed and DPM remains off.

## [2026-08-10] post-processing | Visualize setup-07e clean-start repeatability

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/18_setup07e_dry_band_lineage_repeatability.png`, `.svg`, `setup07e_dry_band_lineage_comparison.csv`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `OVERNIGHT_COMPLETION_CHECKLIST.md`, `visual_manifest.json`, `wiki/log.md`.
- evidence: pressure drop, domain liquid inventory and outlet velocity overlap exactly between setup 07d and 07e at saved iterations 100, 200, 350, 500 and 750; seven controlled fields have maximum difference `0.000000%` while the bands are dry.
- interpretation: appendix-quality lineage evidence only; no adaptive-feedback, sink-surrogate or physical-outlet validation claim.
- safety: local saved-CSV post-processing only; Fluent was not changed and the setup-07e controller remains active with DPM off.

## [2026-08-10] reporting | Add reproducible setup-07 overnight handoff

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07_overnight_handoff.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_HANDOFF.md`, `OVERNIGHT_COMPLETION_CHECKLIST.md`, `MEETING_BRIEF.md`, `visual_manifest.json`, `wiki/log.md`.
- purpose: build the supervisor/partner handoff directly from setup-07d and setup-07e manifests plus setup-07e analysis JSON, keeping endpoint numbers, residuals, checkpoints, safety state and interpretation limits synchronized.
- current state: the generated handoff is explicitly interim while setup 07e runs and will be regenerated from terminal JSON after completion.
- safety: local reporting only; no Fluent state or controller process was changed.

## [2026-08-10] run-update | Complete setup-07e guarded ramp and enter adaptive control

- files created or updated: `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/model/validation.md`, `../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/qualification_manifest.json`, `INTERIM_ANALYSIS.json`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_HANDOFF.md`, figures `14`, `15`, `17`, `18`, and `wiki/log.md`.
- milestone: the clean 900k controller completed its guarded 1,000-iteration ramp. At iteration 1000, pressure drop/domain liquid inventory were `15.2466 kPa`/`22.5761 kg`, continuity/liquid-VF residual were `0.405080`/`6.60996e-4`, and the active band remained effectively dry (`1.30160e-12 kg`).
- lineage: setup 07e and accepted setup 07d now match exactly at six common dry-band saved iterations (100, 200, 350, 500, 750 and 1000), with `0.000000%` maximum difference across all seven controlled comparison fields.
- transition: the bounded feedback selected `tau=0.002 s`; the separate ramp-complete case/data write returned before Fluent entered the first `R=1` feedback block. Feedback tracking remains unresolved until the marked band wets.
- safety: the single controller remains active; bottom is still a wall and DPM/EWF remain off. The result is diagnostic numerical-control evidence only, not physical outlet or separator-performance validation.

## [2026-08-10] post-processing | Add setup-07e band-wetting and sink-onset figure

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/19_setup07e_band_wetting_and_sink_response.png`, `.svg`, `setup07e_band_wetting_response.csv`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `visual_manifest.json`, and `wiki/log.md`.
- purpose: make the many-orders-of-magnitude clean-start transport delay visible and separate local band wetting from the adaptive source response, which is hidden on the linear control-history scale.
- first full-strength evidence: at cumulative iteration 1100/R1=100, saved band inventory was `1.19261e-9 kg` and achieved sink `5.96307e-7 kg/s` at bounded `tau=0.002 s`; pressure drop/continuity were `15.8438 kPa`/`0.369865`.
- presentation rule: log-scale plotting floors (`1e-15 kg`, `1e-12 kg/s`) are disclosed. The figure is a numerical wetting/control diagnostic and does not represent physical brine-outlet flow.
- safety: local CSV/JSON plotting only; the single Fluent controller was not changed and DPM/EWF remain off.

## [2026-08-10] run-update | Record first material setup-07e feedback response

- files created or updated: `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/model/validation.md`, `../../PyAnsys/output/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/INTERIM_ANALYSIS.json`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_HANDOFF.md`, figures `14`, `15`, `17`, `19`, and `wiki/log.md`.
- milestone: at cumulative iteration `1300`/`R=1` iteration `300`, band liquid inventory was `0.00243195 kg` and bounded `tau=0.002 s` produced `1.21598 kg/s`, only `1.040%` of the `116.92 kg/s` command; corrected liquid imbalance remained `98.960%`.
- field state: pressure drop/domain liquid inventory continued upward to `18.0216 kPa`/`30.6899 kg`. Continuity decreased to `0.288247` but remained far above its gate; no stable acceptance window passed.
- interpretation: the adaptive source is now measurably active after the expected clean-start transport delay, but the evidence does not yet show numerical mass closure or field stabilization.
- safety: the single controller remains active, the ramp-complete pair is preserved, no guard has triggered, and DPM/EWF remain off.

## [2026-08-10] code-update | Report live setup-07e source capacity in status checks

- files created or updated: `../../PyAnsys/scripts/connection/check_setup07e_mass_balance_control_status.py`, `wiki/log.md`.
- change: the read-only status command now calculates the transcript-observed implied source `abs(Mband) x ramp / tau` and reports both kg/s and percentage of the `116.92 kg/s` target beside live UDF ramp/tau/band inventory.
- purpose: make rapid source growth visible between saved 100-iteration feedback points while keeping saved CSV/manifest rows authoritative for formal assessment.
- verification and safety: the script compiles and read back the live iteration-1335 source as `1.68610 kg/s` (`1.44209%` of target); it does not connect to or change Fluent.

## [2026-08-10] run-update | Record setup-07e source plateau and residual reversal

- files created or updated: `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/model/validation.md`, setup-07e interim analysis/handoff/figures, and `wiki/log.md`.
- milestone: at cumulative iteration `1600`/`R=1` iteration `600`, bounded `tau=0.002 s` produced `7.87548 kg/s` (`6.736%` of command) and corrected liquid imbalance remained `93.264%`.
- stability evidence: pressure drop/domain liquid inventory continued upward to `22.5860 kPa`/`38.6312 kg`. Continuity ended `0.240295` and changed `+0.272%` over iterations 1501-1600; the phase-2 residual worsened `5.076%` to `5.33466e-4`.
- interpretation: the adaptive source is active but is approaching a low local-inventory-limited response while primary physical monitors remain iteration-dependent; no acceptance window has passed.
- safety: no sink, pressure or finite-field guard triggered; the single controller continues and DPM/EWF remain off.

## [2026-08-10] post-processing | Compare all three setup-07 thick-band sink strategies

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/20_setup07_sink_strategy_comparison.png`, `.svg`, `setup07_sink_strategy_comparison.csv`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `visual_manifest.json`, and `wiki/log.md`.
- purpose: compare setup 07c fixed `tau=0.10 s`, setup 07d fixed `tau=0.02 s`, and setup 07e adaptive tau on the same full-strength iteration axis using sink, corrected liquid imbalance, pressure drop and domain liquid inventory.
- visual result: stronger source laws increase numerical removal, but the early pressure/inventory histories are nearly coincident and all three strategies remain far from the `116.92 kg/s` liquid-feed closure.
- grain and limit: each controller's native saved block spacing is retained; this is a numerical-source strategy comparison and does not validate physical outlet hydraulics.
- safety: local CSV plotting only; the active setup-07e controller was not changed and DPM/EWF remain off.

## [2026-08-10] post-processing | Add five-case liquid-pathway accounting

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/21_setup07_liquid_pathway_accounting.png`, `.svg`, `setup07_liquid_pathway_accounting.csv`, `CHART_MAP.md`, `MEETING_BRIEF.md`, `visual_manifest.json`, and `wiki/log.md`.
- purpose: place setup 07a-07e endpoints on one common `116.92 kg/s` liquid-feed budget, separating steam-outlet liquid, numerical sink removal and the source-inclusive unclosed steady rate.
- current evidence: the strongest completed fixed source (setup 07d) routes `40.2%` of the liquid feed; the setup-07e adaptive row is explicitly labelled `running` and regenerates from each saved feedback point.
- interpretation limit: the unclosed rate is not a physical transient accumulation rate, and no endpoint is accepted as physical brine-outlet or separator-performance evidence.
- safety: read-only saved-CSV post-processing; the single setup-07e controller remains active and DPM/EWF are off.

## [2026-08-10] code-update | Prepare setup-07e terminal Fluent graphics export

- files created or updated: `../../PyAnsys/scripts/inspection/export_setup07_meeting_graphics.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_COMPLETION_CHECKLIST.md`, and `wiki/log.md`.
- change: the existing post-processing-only graphics exporter can now discover the latest preserved setup-07e `R=1` checkpoint and its separate ramp-zero final directly from the qualification manifest. It can export matched liquid-volume-fraction, pressure, sink-mask, boundary and carrier-pathline pictures, then restore the ramp-zero setup-07e state.
- guard: setup-07e export is unavailable until both the preserved full-strength and final checkpoints exist; no initialization, iteration, DPM update or case/data write is issued by the exporter.
- verification: the exporter compiles and its command-line contract reads back correctly. The live controller was not touched and DPM/EWF remain off.

## [2026-08-10] correction | Remove double-counted sink from setup-07c/07d history visual

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07_sink_strength_comparison.py`, `../../PyAnsys/scripts/analysis/build_setup07e_control_visuals.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/10_fixed_sink_strength_history.png`, `.svg`, `fixed_sink_strength_comparison.csv`, `setup07e_band_wetting_response.csv`, `visual_manifest.json`, and `wiki/log.md`.
- issue: the appendix history builder subtracted `sink_magnitude_kgs` from `liquid_net_kgs`, even though Fluent's phase-2 Net already includes the cell-zone source. This affected the plotted/exported unclosed-rate history only; the setup reports, meeting-brief endpoint values and five-case pathway budget use the correct source-inclusive phase Net.
- correction: `unclosed_liquid_rate_kgs = liquid_net_kgs`. Correct endpoints are `94.4317 kg/s` for setup 07c and `69.9324 kg/s` for setup 07d. The setup-07e wetting CSV now exports the corrected `liquid_imbalance_percent` field rather than the explicitly double-added diagnostic column.
- safety: local saved-CSV post-processing only; Fluent and the active setup-07e controller were not changed, and DPM/EWF remain off.

## [2026-08-10] run-update | Preserve setup-07e R1=1000 checkpoint and fail first acceptance window

- files created or updated: `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/model/validation.md`, setup-07e manifest/analysis/histories, meeting figures `14`, `15`, `17-21`, `OVERNIGHT_HANDOFF.md`, and `wiki/log.md`.
- checkpoint: separate `r1_iter1000_cumulative2000.cas.h5` and `.dat.h5` writes returned and were verified without overwriting the start or ramp-complete evidence.
- endpoint: bounded `tau=0.002 s` produced `20.19472 kg/s` (`17.272%` of command); corrected liquid and source-inclusive mixture imbalance were `82.7277%`/`48.6231%`; pressure drop/domain inventory were `23.3447 kPa`/`47.6467 kg`; continuity/liquid-VF residual were `0.187581`/`5.13866e-4`.
- acceptance: the first complete 500-iteration window failed pressure/sink/inventory drift (`7.339/97.927/27.521%`), outlet/domain velocity and vorticity drift, balance and the absolute continuity gate. Zero acceptance windows passed; the single controller continues toward the 2000 full-strength cap.
- safety: DPM/EWF remain off, the bottom remains a wall, and no duplicate controller or new mesh/physics sensitivity was launched.

## [2026-08-10] code-update | Prepare matched setup-07c/07e terminal spatial figures

- files created or updated: `../../PyAnsys/scripts/analysis/build_setup07e_spatial_comparison.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_COMPLETION_CHECKLIST.md`, the `continue-setup07-overnight` automation prompt, and `wiki/log.md`.
- purpose: after setup 07e completes, build matched fixed-versus-adaptive liquid-VF and absolute-pressure composites from the preserved full-strength states using identical 900k plane, cell sampling, camera and fixed ranges.
- guards: the builder requires terminal setup-07e analysis, a verified `sink07e` graphics manifest state, DPM off and successful restoration of the separate setup-07e ramp-zero final. It fails before producing figures if those conditions are absent.
- verification: the script compiles and its pre-terminal failure path was exercised; it correctly refused to run because terminal setup-07e graphics do not yet exist. No Fluent state was changed.

## [2026-08-10] code-update | Add machine-readable setup-07 overnight completion audit

- files created or updated: `../../PyAnsys/scripts/analysis/audit_setup07_overnight_completion.py`, `../../PyAnsys/output/setup07_meeting_visuals_20260811/OVERNIGHT_COMPLETION_AUDIT.json`, `.md`, `OVERNIGHT_COMPLETION_CHECKLIST.md`, `visual_manifest.json`, `../../PyAnsys/scripts/analysis/build_setup07_overnight_handoff.py`, and `wiki/log.md`.
- scope: verify terminal controller/classification, ramp-zero and DPM-off state, all non-overwriting checkpoint records and write markers, non-empty histories, terminal analysis, figures 14-23, Fluent post-processing provenance/safe restore and required documentation.
- current pre-terminal result: `pending` with `0` failures, `2` passes and `11` pending checks. Pending terminal evidence is not treated as success.
- completion rule: rerun after terminal post-processing and require overall `passed` with no pending/failed checks before closing the overnight goal.

## [2026-08-11] run-complete | Close setup-07e adaptive mass-balance control

- files created or updated: setup-07e qualification manifest and histories,
  `QUALIFICATION_RESULT.json/.md`, separate terminal case/data checkpoints,
  `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`,
  setup ordering, project experiments/current status/blockers/validation and
  `wiki/log.md`.
- execution: completed the guarded 1,000-iteration ramp and the full 2,000
  full-strength budget (`3,000` cumulative iterations). Stop reason was
  `maximum iteration budget reached`; zero acceptance windows passed.
- endpoint: the bounded `tau=0.002 s` source removed `50.954294 kg/s`
  (`43.6%` of the `116.92 kg/s` liquid feed). Corrected liquid imbalance was
  `56.419329%`, pressure drop/domain liquid inventory were
  `26.7252 kPa`/`65.007547 kg`, and the active band held `0.101909 kg` versus
  `0.23384 kg` required for full command tracking at minimum tau.
- convergence: continuity/liquid-VF residual ended at
  `0.254617`/`7.53207e-4` and both grew over the final 100 iterations.
  Final-500 pressure/sink/inventory drift was
  `5.8506/26.1894/13.3524%`; outlet/domain velocity drift was
  `3.3033/6.9068%`.
- safety: separate start, ramp-complete, R1=1000, R1=2000 and final
  ramp-reset-zero case/data pairs were preserved; final ramp was zero, DPM
  interaction was off and no injection update or tracking ran.
- classification: `Completed diagnostic / unresolved`. Further local sink
  tuning is frozen; the next physical branch is a resolved brine outlet on one
  medium mesh.

## [2026-08-11] post-processing | Complete terminal meeting graphics and spatial comparison

- files created or updated: terminal figures `14`, `15`, `17`, `19-23`,
  `26-27`, linked CSV/JSON evidence, `MEETING_BRIEF.md`, `CHART_MAP.md`,
  `OVERNIGHT_HANDOFF.md`, `visual_manifest.json` and
  `fluent/fluent_graphics_manifest.json` under
  `../../PyAnsys/output/setup07_meeting_visuals_20260811/`.
- accepted Fluent graphics: setup-07e liquid-volume-fraction and absolute-
  pressure contours plus liquid-inlet Mixture-carrier pathlines. Matched
  setup-07c/setup-07e liquid and pressure composites were generated with the
  same plane, field ranges and camera.
- limitations: the optional UDF sink-mask field was unavailable after saved-
  state reload and the requested steam-inlet pathline release did not read
  back to that surface. Neither optional view was fabricated or used for a
  claim.
- safety: post-processing loaded saved case/data only, ran zero solver
  iterations, performed no DPM update and restored the setup-07e ramp-zero
  final with DPM off.
- meeting decision: open with figure `27`; use the terminal data to support a
  resolved brine pipe, pressure outlet first when downstream pressure is
  defensible, and a rate-forced outlet only as a diagnostic bracket.

## [2026-08-11] report | Create condensed ten-minute supervisor handout

- files created or updated:
  `../../PyAnsys/output/pdf/setup07_condensed_meeting_report_20260811.pdf`,
  its editable `.md` source and chart map,
  `../../PyAnsys/scripts/analysis/build_setup07_condensed_meeting_report.py`,
  the setup-07 meeting brief artifact inventory and `wiki/log.md`.
- format: five A4 landscape pages paced for a ten-minute walkthrough: decision
  (1 minute), baseline limitation (2), sink sensitivity (2), acceptance gate
  (2) and recommended rebuild (3).
- evidence: only accepted terminal setup-07 metrics and figures `01`, `15`,
  `21`, `25` and `27` are used. The report preserves the classifications that
  all sink cases are diagnostic/unresolved and that no mesh independence,
  separator efficiency or free-surface claim is supported.
- verification: all five pages were rendered and visually inspected; PDF
  metadata, page count, selectable text, key values and per-page footers were
  checked. No Fluent state or CFD output was changed.

## [2026-08-11] report | Create Google Docs-style setup-07 supervisor report

- files created or updated:
  `../../PyAnsys/output/docx/setup07_supervisor_report_google_docs_style_20260811.docx`,
  `../../PyAnsys/scripts/analysis/build_setup07_google_docs_report.py`, the
  meeting-brief artifact inventory and `wiki/log.md`.
- format: nine-page US Letter portrait report using the native Google Docs
  visual system (Arial, black hierarchy, simple title block, prose sections,
  quiet tables and conventional numbered captions).
- content: includes the implemented liquid source
  `S_l=-rho_l alpha_l R/tau`, its integrated band-capacity equation, momentum
  removal and the bounded setup-07e feedback law. It reuses six accepted
  figures: baseline drift, closed-bottom Fluent liquid contours, liquid-route
  accounting, sink-mask/carrier pathlines, setup-07e residuals and preliminary
  brine-outlet sizing.
- verification: the sanitized DOCX rendered to nine clean pages; all rendered
  pages were inspected, the final render was pixel-identical after the
  accessibility-only table-header patch, and title, heading, section, image and
  accessibility audits passed with no findings. No Fluent state or CFD output
  was changed.

## [2026-08-13] model-update | Launch setup-07g resolved brine-outlet qualification

- files created or updated: `../../Setup report/07g-split-inlet-resolved-brine-outlet-qualification.md`, setup ordering, project experiments/current status/blockers/validation, `../../PyAnsys/scripts/inspection/inspect_brine_outlet_mesh.py`, `inspect_remote_windows_environment.py`, `search_remote_documents.py`, `inspect_tui_zone_capabilities.py`, `../../PyAnsys/scripts/setup/prepare_setup07g_brine_outlet.py`, `run_setup07g_brine_outlet_qualification.py`, `../../PyAnsys/scripts/connection/check_setup07g_status.py`, setup-07g output manifests/transcripts/checkpoints and `wiki/log.md`.
- mesh evidence: located `brine-outlet-620kcells.msh.h5` in the server `Meshes` folder; SHA-256 `0d75a86e...9394`, 620,431 cells, 16 partitions, `27.06309 m3`, minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258`, no negative-volume error and dedicated `0.19936247 m2` brine pressure face.
- controlled setup: clean mesh, explicit zone normalization, authoritative carrier settings, fresh Hybrid Initialization, feeds `116.92/80.69 kg/s`, steam/brine pressure outlets at `1.12 MPa`, DPM/EWF/sink off. Complete readback passed with fingerprint `223fd8d3...b30`.
- execution: separate iteration-zero pair saved. Fluent transcript proved the first 25 iterations, but the PyFluent monitor stream was empty; the verified iteration-25 pair and failed controller evidence were preserved separately. A single resumed controller now proves blocks from either monitor points or Fluent residual rows and targets 3,000 iterations with non-overwriting checkpoints.
- recovery correction: the transcript-proven 25-to-250 block was saved as a verified iteration-250 pair. Post-processing rejected `phase-2-volume-fraction`; Fluent exposed `phase-2-vof` as the allowed field. The controller now uses that field, writes completed-block proof before metrics and has resumed singly from iteration 250.
- first physical result: at iteration 500 both outlets discharged net mixture (`steam -38.76477`, `brine -37.179327 kg/s`), but the brine outlet carried vapor outward at `42.680678 kg/s` while liquid entered at `5.512239 kg/s`; mixture/liquid imbalance remained `61.5687/104.7145%`. The result is diagnostic/unresolved and the non-overwriting 500 checkpoint was preserved before continuation.
- classification: active diagnostic. No mesh-independence, efficiency, DPM or EWF claim.

## [2026-08-15] model-update | Define setup-07h initial-pool brine-outlet qualification

- files created or updated: `../../Setup report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md`, setup `07g`, setup ordering, project experiments/current status/blockers/validation, `../../PyAnsys/scripts/inspection/inspect_setup07g_live_geometry_state.py`, `../../PyAnsys/scripts/setup/prepare_setup07h_brine_pool.py`, `run_setup07h_brine_pool_qualification.py`, `supervise_setup07h_brine_pool.py`, `../../PyAnsys/scripts/connection/check_setup07h_status.py` and `wiki/log.md`.
- purpose: replace the failed dry-start interpretation with a controlled source-free test of the physical brine outlet initialized with a lower liquid reservoir.
- terminal 07g evidence: verified iteration 500 had net outward mixture at both outlets, but brine vapor was `-42.680678 kg/s` and brine liquid was `+5.512239 kg/s`; the next block produced only 62/250 residual rows and the later overflow-scale live field is excluded.
- setup-07h control: clean original 620,431-cell mesh, unchanged authoritative carrier physics and equal `1.12 MPa` pressure inputs, fresh Hybrid Initialization, then phase-2 liquid below geometry-inferred `y=0 m`; DPM/EWF/sink remain off.
- verification: all four new scripts compile and all 24 local unit tests pass. The controller has explicit monitor streaming, complete setup readback, non-finite-state gates, a 1000-iteration phase-routing gate and non-overwriting 0/25/250/500/1000/2000/3000 checkpoints.
- assumptions introduced/retired: introduced `y=0 m` only as a geometry-derived initial pool level from the brine face centroid/radius; did not treat it as a measured plant level. Retired use of the divergent 07g live field and manual hydrostatic pressure-offset tuning.
- execution launch: one detached supervisor was started. It retries the bounded read-only gate every 300 seconds for up to 18 hours, then runs preparation and qualification once; it will not blindly repeat an actual preparation or solver failure.
- blocker: the Fluent port accepts TCP but currently returns a PyFluent `InvalidPassword` classification during the application-mode query. No setup-07h calculation controller is active and no live mutation occurred.
- next immediate action: the supervisor will prepare and run setup 07h when Fluent authentication succeeds; if the steady state drains or depends on the patched pool, qualify the same geometry as transient before any new mesh ladder, DPM or EWF work.
## [2026-08-19] model-update | Implement setup-07j guarded transient VOF branch

- corrected setup 07i: the live roster was 16 ranks (`n0..n15`); `/20` was
  hardware cores. The WFGC sensitivity was a valid controlled setup and failed
  numerically with residual explosion and node-4 SIGSEGV at raw iteration 21.
- verified the restarted Fluent 2024 R2 endpoint and release-specific VOF
  controls, including Sharp selector `0`, Geo-Reconstruct, PISO and transient
  controls under `run-calculation/transient-controls`.
- implemented `prepare_setup07j_transient_vof.py` and
  `run_setup07j_transient_vof_qualification.py`: clean resolved-brine mesh,
  explicit VOF, pool below `y=0 m`, DPM/EWF/sink off, exact 16-rank gate,
  one-step smoke, storage-aware phase closure, gross-failure gates and separate
  checkpoints through `0.1 s`.
- the first formal preparation attempt stopped before initialization/time
  advance after the generated Settings-API read-settings RPC blocked for more
  than 11 minutes. The importer now prefers the established TUI read-settings
  path. The live process then became unauthenticatable with Cortex unobtainable
  despite an open TCP port and requires a clean Fluent restart.
- verification: both scripts compile; five setup-07i and five setup-07j focused
  local tests pass. Classification remains `Diagnostic / unresolved`.

## [2026-08-21] model-update | Execute setup 07j and launch controlled setup 07k

- setup 07j: accepted clean transient-VOF preparation on 16 ranks, with
  Geo-Reconstruct, WFGC, fresh Hybrid Initialization, `y<=0 m` liquid pool and
  DPM/EWF/sink off. Separate time-zero and step-1 pairs were saved.
- equal-pressure outcome: the gross-drainage gate stopped step 2 at
  `-4692.8688 kg/s` brine liquid. Inventory change and boundary flux close to
  `0.4601%` of feed, so the result is real model drainage, not a report error.
  The 07j field is terminal diagnostic evidence and is not resumed.
- robustness correction: transient execution now requests exactly one physical
  step per PyFluent RPC and verifies both step and flow-time clocks after every
  call. Nineteen focused 07j/07k tests pass.
- setup 07k: implemented isolated preparation, qualification wrapper and locked
  supervisor. The sole boundary change is a phase-specific brine mass-flow
  outlet (`116.92 kg/s` liquid, zero vapor), followed by fresh initialization
  and the same pool patch. Preparation passed and separate case/data were saved.
- initial 07k result: steps 1-3 passed gross gates; brine command remained exact,
  steam outflow established by step 2 and liquid VF remained bounded. The
  overnight run remains diagnostic and cannot validate the downstream plant
  boundary, mesh independence, efficiency, DPM or EWF.
- terminal correction: step-3 mass-flow routes were finite but the field was
  already numerically nonphysical (`-4.1102e13 Pa` steam-outlet pressure,
  `5.2599e6 m/s` steam-outlet velocity and `7.2714e4 m/s` domain velocity).
  The step-4 writer RPC then hit the existing two-hour guard and exited `124`;
  step 4 is uncredited, no controller remains and setup 07k is prohibited from
  resume. The gross gate now also fails closed on explosive finite pressure and
  velocity values; 21 focused tests pass.

## [2026-08-21] model-update | Diagnose server loss and complete setup 07l hydrostatic-rest isolation

- connection diagnosis: setup 07i numerical divergence preceded a confirmed
  Node-4 SIGSEGV/server shutdown; setup 07k was already catastrophically
  nonphysical before its following RPC hung. Current Fluent 2024 R2 endpoint
  reconnected and completed the new run on 16 ranks.
- forensic corrections: 07j/07k tracked `6,456` one-way parcels from six
  inherited injections even though interaction was off, and Hybrid
  Initialization used constant pressure before the dense liquid pool patch.
- implementation: added setup-07l capability probe, preparation, guarded
  one-step qualification, resume support and five unit tests. Preparation
  deletes every injection, disables DPM tracking/interaction, zeros both
  inlets, temporarily closes the brine face, specifies vapor operating density,
  places the reference in gas and saves a separate time-zero pair.
- execution: ten `1e-6 s` steps completed with 20 inner iterations and separate
  checkpoints 1-10. Final continuity was `3.4698e-6`, domain velocity
  `4.8978e-7 m/s`, liquid inventory unchanged at `3774.370486 kg`, maximum
  Global Courant `1.0095e-8`, and no DPM/FPE/SIGSEGV/gate failure occurred.
- physical finding: the closed lower face stabilized `2090.4 Pa` above the
  steam outlet, within `4.86%` of the `2197.24 Pa` centroid estimate
  `rho_l g h`. Equal outlet pressure is therefore not a neutral submerged
  brine boundary.
- classification: setup 07l is accepted bounded isolation evidence only. It
  does not validate the open outlet or separator performance. Next open the
  brine pressure boundary at zero inlet flow from clean relaxed lineage, then
  ramp inlets only after one-step pressure/Courant/flux gates pass.
## [2026-08-21] model-update | Execute setup 07m zero-feed pressure opening

- added setup-07m campaign, ten-step extension, promoted/micro-ramp and hold
  controllers plus focused tests and non-overwriting output namespaces;
- ran nine independent zero-feed pressure/time-step cases from accepted 07l
  step 10; all stayed bounded, finite and DPM-free;
- extended low/centre/high cases for ten `1e-5 s` steps and proved monotonic
  liquid response with an endpoint sign bracket;
- rejected an abrupt 1% start on continuity, then qualified a 0.1%/`1e-7 s`
  ten-step hold with 100 inner iterations and final continuity `0.00186867`;
- launched a guarded 0.2%/0.5%/1% continuation. The bracket remains diagnostic
  pending real downstream pressure or resistance data.

## [2026-08-21] progress-update | Hand off resolved brine-outlet modelling

- files created or updated: `wiki/progress/brine-outlet-modelling-handoff-2026-08-21.md`, `wiki/progress/brine-outlet-modelling-new-chat-prompt-2026-08-21.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/index.md`, `../../Setup report/order-dictionary.md` and `wiki/log.md`.
- purpose: give a new Codex chat an evidence-backed, non-overwriting continuation path from accepted setup 07l through the stopped setup-07m 1% checkpoint.
- current status: no controller is active; the first 1% hold attempt credited zero steps during a connection timeout, while the independent server-2 steady field is a terminal gross-drainage diagnostic.
- blockers: the 1% continuity gate remains unresolved and downstream brine pressure/head, pipe or valve resistance and operating liquid level remain missing.
- assumptions introduced or retired: no new physical assumption; retired the stale summary that the higher-flow ramp was still active.
- next immediate action: restore and verify server-1 ownership, preserve the stale attempt, and run a non-overwriting 20-step fixed 1% hold at `dt=1e-7 s` with 100 inner iterations.

## [2026-08-21] research-update | Define resolved-outlet model and solver screening

- reviewed the maintained geothermal separator, cyclone RSM-DPM, annular-flow
  DPM/EWF and Fluent multiphase/solver guidance against the new resolved brine
  outlet scope;
- corrected setup `09`: its VOF rejection applies to the older carryover-only,
  truncated-bottom family and is not a decision for the explicit pool/drainage
  lineage;
- added setup `07n`, which ranks explicit/implicit VOF solver sensitivities
  before freshly prepared Mixture and Eulerian/Multi-Fluid-VOF comparisons;
- retained zero DPM injections, DPM off, EWF off and no numerical sinks for all
  carrier-screening work;
- identified outlet resistance as first-order: the full-flow velocity head is
  about `195 Pa`, compared with the `2090.4 Pa` hydrostatic-rest diagnostic;
- no Fluent solve, model change or remote file write was performed during the
  literature review.

## [2026-08-21] scope-correction | Make constant water level the primary carrier target

- accepted the user clarification that the lower water pool is an intended
  constant-level operating feature and the physical steam seal over the brine
  outlet;
- corrected setup `07n`, current status, blockers and validation so the missing
  plant valve curve no longer blocks an idealized constant-level CFD baseline;
- added a paired liquid feed/drain ramp and a bounded inventory-feedback outlet
  controller as the first resolved-outlet physical configurations;
- retained setup-07k as terminal evidence only: its abrupt full-flow command
  from a non-hydrostatic quiescent start is not reused and does not reject a
  hydrostatic, matched-ramp constant-level branch;
- retained DPM zero-object/off, EWF off and no numerical sink for this work.

## [2026-08-21] boundary-correction | Require an emergent liquid steam seal

- corrected the proposed constant-level implementation: pressure-outlet
  backflow fraction affects reversed inflow only, and a Fluent mass-flow outlet
  prescribes total outlet flow rather than creating a liquid-only membrane;
- made outlet phase composition an emergent VOF result and added a fail gate on
  vapor carry-under through the brine outlet;
- noted that the current `y=0 m` pool reaches approximately to the inferred
  pipe crown, so setup `07n` first requires a resolved submergence sensitivity
  above the crown before paired-flow or feedback level control;
- preserved setup-07k as historical terminal evidence without reinterpreting
  its recorded boundary commands or resuming its field.

## [2026-08-21] scope-reset | Rebuild setup 07n from the physical constant-level problem

- downgraded setups 07l and 07m from proposed physical lineage to forensic
  numerical evidence: their bounded microsecond windows do not prove an
  operating level, separator-scale relaxation or a plant-valid brine pressure;
- reviewed the local Purnanto, Pointon, and Zarrouk/Purnanto sources. Purnanto
  excluded brine-pipe flow and prescribed level; Pointon excluded the brine-drum
  piping; the geothermal design review identifies water drums and U-bend loop
  seals as the real level-control and steam-seal mechanisms;
- added analogy-level support from Vani et al.'s gravity-separator CFD method,
  which adjusts liquid-outlet pressure from interface-level feedback when the
  downstream outlet pressure is unknown;
- reset 07n to start with exact crown/local-mesh/time-scale audit and a freshly
  reconstructed VOF pool, then compare ideal matched liquid removal with
  bounded level-feedback pressure control;
- made explicit water-drum or loop-seal geometry the next physical branch if
  the current outlet leg cannot preserve a liquid seal;
- no Fluent connection, iteration or remote file mutation was performed in
  this scope reset.

## [2026-08-22] model-update | Execute setup 07n Stage-0 geometry and inventory audit

- audited exact local processes, stale manifests and both Fluent endpoints;
  no writer/controller was active, both servers were Fluent 2024 R2 on 16
  ranks, and server 2 lacked the authoritative case/data parents;
- preserved the stale setup-07m zero-step 1% hold in a separate non-overwriting
  attempt record while leaving the original `running` manifest unchanged;
- added non-mutating server preflight and Stage-0 geometry scripts with a local
  one-writer lock, checksum/version/rank/client gates and non-overwriting JSON;
- resolved brine area `0.1993624690 m2`, crown `-0.0015579789 m`, invert
  `-0.5067311525 m`, median crown-face height `0.0089871744 m` and inferred
  cylindrical wall extent `1.95976 m`;
- documented the Fluent-2024-R2 `UNIMPLEMENTED` volume-cell RPC and failed UTL
  `pm/volumes` fallback; corrected the first UTL manifest's over-optimistic
  classification through a checksum-bound companion record;
- measured two fresh case-only VOF patch inventories with zero physical steps:
  `3877.46807 kg` at `y=0.0164163698 m` and `3909.27263 kg` at
  `y=0.0343907186 m`; DPM remained zero-object/off and all sources remained off;
- corrected setup 07n's PI pressure sign, separated bulk-mixture 07n-b from the
  old phasic 07k command, and replaced the illegal explicit-VOF
  Coupled-with-Volume-Fractions sensitivity with plain Coupled;
- classification: geometry/inventory `accepted diagnostic`; adjacent
  volume-cell height and Stage-0 completion `diagnostic / unresolved`; no 07n-a
  relaxation, outlet opening or solver/model sensitivity was run;
- live-state disposition: server 1 retains candidate 2 only as an unsaved,
  non-parentable patched diagnostic; the next writer must cold-load the
  accepted settings carrier before any calculation;
- activated a 30-minute read-only task monitor that cannot authenticate or
  start a Fluent writer.

## [2026-08-22] model-update | Run setup 07n lower-face-proxy closed-drain startup

- files created or updated: `../../Setup report/07n-resolved-brine-outlet-model-solver-screening.md`,
  `../../Setup report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md`,
  `../../Setup report/order-dictionary.md`, setup-07n pilot/extension scripts and
  output evidence, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`,
  `wiki/progress/blockers.md`, `wiki/model/validation.md`, PyAnsys successful-path
  knowledge and `wiki/log.md`;
- purpose: execute and classify the first safely reconstructed closed-drain
  lower-pool startup plus one conservative physical-dt extension, without
  inheriting a prior solution field or promoting an unproved water level;
- preserved three discovery/failure attempts without overwrite. Attempt 3
  physically completed one finite step but failed post-solve monitor-key
  bookkeeping before controller credit; a checksum-bound correction records
  the step and permanently excludes the uncheckpointed field;
- ran authoritative pilot attempt 4 from the setup-07l step-10 **case only**,
  followed by fresh Hybrid initialization and the accepted lower Stage-0 proxy
  patch (`98,473` cells, `3877.468071 kg` liquid). DPM zero/off, EWF false,
  sources/sinks off, brine wall and zero feeds were read back throughout;
- completed ten `dt=1e-6 s` single-step RPCs and saved hashed t0/step-1/5/10
  pairs. Step-10 continuity `2.74398e-6`, Courant `7.73149e-9`, brine-face
  liquid VF `1.0`, unchanged inventory and zero gate failures;
- checksum-verified the step-10 parent and ran a one-factor `dt=2e-6 s`
  extension for ten more steps with hashed additional-step-1/5/10 pairs. At
  cumulative step 20 / `30 us`, continuity `4.64048e-6`, Courant
  `4.81584e-8`, maximum velocity `1.64972e-4 m/s`, unchanged inventory and zero
  gate failures;
- classification: both completed runs are `diagnostic / unresolved bounded
  startup`. The boundary-face proxy is not a promoted water level and `30 us`
  is only `~0.07%` of the local gravity scale. Outlet opening, model/solver
  screens and mesh convergence remain withheld pending adjacent cell-height
  proof and meaningful-time relaxation;
- assumptions introduced or retired: introduced no plant value; retained the
  lower elevation only as a boundary-face-proxy diagnostic and retired the idea
  that passing microsecond startup gates proves hydrostatic/dynamic relaxation;
- controller state: no local Fluent writer remains active after completion;
- next immediate action: independently recover adjacent volume-cell height,
  reconstruct the mesh-defined pool and design a meaningful-time closed-drain
  relaxation before opening the outlet or screening solvers/models.

## [2026-08-23] model-update | Complete setup 07n meaningful-time relaxation and matched dt/2 diagnostic

- files created or updated: `../../Setup report/07n-resolved-brine-outlet-model-solver-screening.md`,
  `../../Setup report/order-dictionary.md`, the guarded mesh-selected dt runner,
  setup-07n output evidence, `wiki/progress/current-status.md`,
  `wiki/progress/experiments.md`, `wiki/progress/blockers.md`,
  `wiki/model/validation.md` and `wiki/log.md`;
- continued the accepted `98,473`-cell / `3877.468071 kg` zero-feed closed-pool
  lineage at `dt=2.56e-4 s` through cumulative step 940 / `0.22271 s`, with
  explicit VOF, PISO/PRESTO/Geo-Reconstruct/WFGC, RNG `k-epsilon`, brine wall,
  DPM zero/off, EWF off and all sources/sinks off;
- all completed stages passed residual, Courant, VOF, pressure, velocity,
  inventory, storage, steam-seal, clock and settings gates. Step 940 ended at
  continuity `3.67467e-4`, Courant `0.0125058`, average velocity
  `0.00357883 m/s`, vorticity `0.0331321 1/s` and maximum velocity
  `0.144127 m/s`, with exact inventory and zero liquid steam-outlet flow;
- preserved stage-5 attempt 1 as `stopped_postsolve_monitoring`: 27 fully
  monitored steps, followed by one solved but uncredited step. Its field was
  not resumed. Stage-5 attempt 2 cold-loaded the verified step-540 pair and
  completed a new non-overwriting 100-step block;
- classified physical stationarity as nearly reached but unresolved: final-20
  regression drift was `-1.540%` average velocity, `-0.637%` vorticity,
  `-0.912%` maximum velocity and `+0.021%` Courant;
- ran a checksum-bound matched physical-time comparison from the same step-940
  parent: 20 x `2.56e-4 s` versus 40 x `1.28e-4 s`, both ending at
  `t=0.22783 s`. Average velocity/vorticity differed `0.906%`/`0.941%`,
  pressure/inventory/VOF/steam seal matched, and half-step continuity was
  `35.62%` lower, but maximum velocity differed `7.332%`;
- classification: `diagnostic / unresolved`. The bulk field is nearly
  time-step independent over the matched window, while the localized velocity
  maximum is not. Neither endpoint is promoted to outlet opening, level
  control, solver/model screening or mesh convergence;
- warning: the turbulent-viscosity limiter remained confined to one of
  `620,431` cells without a hard-gate failure and may be connected to the local
  maximum sensitivity;
- controller state: exact local process audit found no Fluent writer after the
  matched comparison;
- next immediate action: run one bounded, one-factor discriminator for the
  localized maximum from the verified step-940 parent, then adjudicate the
  timestep before opening or controlling the brine outlet.

## [2026-08-23] model-update | Complete setup 07n quarter-step discriminator

- files created or updated: the non-overwriting quarter-step run evidence,
  machine-readable matched-window comparison, setup-07n report, order
  dictionary, current status, experiments, blockers, validation, setup-07m
  correction and repository log;
- cold-loaded the same checksum-bound step-940 parent and advanced 80 x
  `6.4e-5 s`, exactly matching the existing base/half physical window at
  `t=0.22783 s`; all residual, Courant, VOF, pressure, velocity, inventory,
  storage, steam-seal, clock, DPM, EWF, source and settings gates passed;
- the endpoint case/data hashes are `32450dc8...f064` / `8535e5ab...0526`;
  inventory remained `3877.468071 kg`, brine-face liquid VF remained `1.0`
  and liquid steam-outlet flow remained zero;
- half-to-quarter endpoint changes were `-1.427%` average velocity, `-1.404%`
  vorticity and `-7.491%` maximum velocity. Across 40 matched samples their
  mean absolute differences were `0.817%`, `0.810%` and `5.935%`;
- classification: `diagnostic / unresolved`. The timestep discrepancies did
  not contract under a second halving, so no endpoint is promoted and another
  blind timestep halving is not justified;
- controller state: exact local process audit found no Fluent writer after the
  quarter-step run;
- next immediate action: localize the maximum and run a bounded inner-iteration
  sensitivity from the same verified step-940 parent before any outlet opening.

## [2026-08-23] model-update | Clear setup 07n inner-iteration convergence

- ran a non-overwriting 20-step branch from the same checksum-bound step-940
  parent at fixed `dt=2.56e-4 s`, changing only the inner-iteration cap from 20
  to 100;
- Fluent 2024 R2, exclusive-client state, ranks `n0..n15`, parent hashes,
  controls, DPM zero/off, EWF off, sources off and all boundary/model settings
  read back correctly before solving;
- all 20 physical steps and hard gates passed. The endpoint case/data hashes
  are `30eb872c...1434` / `e3bc04de...4778`, with exact inventory, brine-face
  liquid VF `1.0` and zero liquid steam-outlet flow;
- endpoint continuity improved from `3.81644e-4` to `1.14616e-6` (`-99.70%`),
  while average velocity, vorticity and maximum velocity changed less than
  `0.000009%` across every matched sample;
- classification: accepted diagnostic for inner-iteration independence, while
  the overall timestep result remains `diagnostic / unresolved`. Insufficient
  inner iterations do not explain the `dt/2` / `dt/4` field discrepancy;
- controller state: exact post-run process audit found no Fluent writer;
- next immediate action: spatially localize the sensitive maximum from the
  checksum-bound matched endpoints before any further numerical branch.

## [2026-08-23] post-processing | Localize setup 07n timestep-sensitive maximum

- preserved attempts 1 and 2 as zero-iteration stopped diagnostics: Fluent
  2024 R2 rejected the cell-register `pm/volumes` path, then correctly rejected
  the volume zone `fluid` as a surface-field target. Neither attempt
  initialized, iterated or wrote case/data;
- accepted attempt 4 checksum-verified and cold-loaded the base, half and
  quarter endpoints, read every carrier gate, and fetched aligned native
  `SV_CENTROID` / velocity-component arrays for all `620,431` cells;
- all endpoints place the maximum on array index `382511`, centroid
  `(0.809789, 0.0420206, 0.651966) m`, with liquid VF
  `0.134811-0.134831`. Velocity magnitude decreases
  `0.142191 -> 0.131766 -> 0.121895 m/s` as the timestep halves;
- top-20 velocity-cell overlap is 18/20 base-to-half, 16/20 half-to-quarter
  and 14/20 across all three. The result is a persistent small interfacial
  region, not a moving or isolated-cell maximum;
- maximum-cell pressure is effectively unchanged and its turbulent viscosity
  is only `0.20-0.24%` of the domain maximum, excluding the known one-cell
  turbulent-viscosity limiter as the cause;
- classification: accepted post-processing diagnostic. It performed zero
  iterations, zero initializations and zero case/data writes. Exact post-run
  process audit found no Fluent writer;
- next immediate action: run one checksum-bound matched `dt/8` branch from the
  same step-940 parent. If quarter-to-eighth differences do not contract, stop
  halving and consider an implicit-VOF numerical sensitivity.

## [2026-08-23] model-update | Stop explicit-VOF halving after matched dt/8

- cold-loaded the same checksum-bound step-940 parent and advanced 160 x
  `3.2e-5 s`, ending at the common `t=0.22783 s` endpoint;
- all residual, Courant, VOF, pressure, velocity, inventory, storage,
  steam-seal, clock, DPM, EWF, source and settings gates passed. Final
  continuity was `1.47877e-4`, Courant `0.00154527`, inventory remained exact
  and liquid steam-outlet flow remained zero;
- endpoint case/data hashes are `b9a7e269...67f79` / `4d8ba586...17c4f`;
- quarter-to-eighth endpoint differences were `-2.150%` average velocity,
  `-1.936%` vorticity and `-7.283%` maximum velocity. Across 80 matched samples,
  mean absolute differences were `1.284%`, `1.217%` and `6.092%`;
- classification: `diagnostic / unresolved`. The differences did not contract
  into an asymptotic sequence, so further explicit-VOF timestep halving is
  stopped and no endpoint is promoted;
- controller state: exact post-run process audit found no Fluent writer;
- next immediate action: run a zero-step implicit-VOF formulation/readback
  probe from the checksum-bound step-940 parent before any implicit iteration.

## [2026-08-23] model-update | Complete setup 07n closed-pool solver screen

- preserved implicit-VOF readback attempts 1-7 as non-overwriting zero-step
  path diagnostics; accepted attempts 8/9 proved implicit VOF/PISO, the
  `(mp/scheme-type 0)` settings marker, automatic Compressive selection,
  supported Compressive/Modified-HRIC choices, exact cell Courant field and
  exact explicit-parent restore;
- ran three checksum-bound implicit/PISO branches from the common step-940
  parent over the same `0.00512 s` physical window. First-order Compressive,
  second-order Compressive and second-order Modified-HRIC all passed every
  residual, Courant, VOF, pressure, velocity, inventory, storage, phase-routing,
  steam-seal, clock, DPM, EWF, source and settings gate;
- first-order implicit differed from explicit by
  `0.873/1.168/12.669%` for average velocity/vorticity/maximum velocity.
  Second-order Modified-HRIC was closest at `0.301/0.552/6.831%`; formulation
  independence remains unresolved and no implicit endpoint is promoted;
- preserved explicit/plain-Coupled attempts 1 and 2 as zero-step diagnostics:
  attempt 1 was blocked before authentication by the local TCP sandbox;
  attempt 2 read back all actual Coupled settings but stopped on an over-strict
  explicit-VOF residual assertion. Neither in-memory state was resumed;
- fresh Coupled attempt 3 cold-loaded the verified parent, read back
  `flow_scheme=Coupled`, `coupled_form=false`, explicit VOF/Geo-Reconstruct and
  the full invariant contract, then completed 20/20 steps with unique
  checkpoints at additional steps 1/5/10/20;
- the Coupled field matched PISO to within `0.000063%`, reduced endpoint
  continuity `37.22%`, and used `3.234x` the summed solve-step wall time. PISO
  is retained as the efficient closed-pool baseline; pressure-velocity
  coupling is cleared for this matched window;
- wrote accepted machine-readable implicit formulation, temporal-order,
  interface-scheme and pressure-velocity comparison records. All implicit and
  Coupled checkpoints remain ineligible; the explicit step-940 pair remains
  the common diagnostic parent;
- classification: solver sensitivities `accepted diagnostic`; overall model
  `diagnostic / unresolved`. Stop solver swapping and move next to a
  separately gated outlet pressure-response sign probe and idealized
  constant-level strategy after downstream head/resistance/level assumptions
  are explicit. Mesh convergence, DPM and EWF remain withheld;
- controller state: exact post-run process audit found no local Fluent writer.

## 2026-08-23 — Setup 07n-c open-drain launch blocked before physical solve

- implemented a non-overwriting zero-feed centre/`+/-195.156 Pa` brine
  pressure-response runner from the checksum-bound explicit/PISO step-940
  parent, with one member per cold load and steam-seal/storage/residual/clock/
  DPM/EWF/source/settings gates;
- attempt 1 verified Fluent 2024 R2, 16 ranks, exact parent hashes and the
  closed parent settings, then lost gRPC during a redundant read-only parent
  phase-flux report. It changed no boundary, advanced zero steps and wrote no
  case/data; its original manifest and a separate no-resume disposition were
  preserved;
- attempt 2 failed the bounded raw-TCP preflight before authentication and
  likewise credited zero physical steps. A separate no-resume disposition was
  written without altering its original manifest;
- host diagnosis: server 1 answers ICMP, while the configured Fluent port
  times out. Attempt 3 is prepared but unstarted pending a Fluent server-mode
  restart/current port. No level controller or inlet feed was authorized and
  no setup-07n writer remains active. The partner's Stage-4 observer was not
  touched;
- preliminary fallback assessment rejected that occupied Fluent 2025 R2
  partner endpoint. The 2026-08-24 record below corrects the earlier
  conflation with the separately configured Fluent 2024 R2 server 2. The
  authoritative step-940 pair was absent from both, so neither could continue
  or replace the server-1 lineage.

## [2026-08-24] progress-update | independent-server2-closed-pool-dt-boundary

- corrected the endpoint record: the partner's occupied endpoint was Fluent
  2025 R2, while the separately configured server 2 was independently verified
  as Fluent 2024 R2, exactly 16 ranks and unowned before each bounded run;
- created a clean non-authoritative setup-07j/settings -> setup-07l/isolation
  -> setup-07n whole-cell-pool reconstruction. The prohibited server-2 steady
  Mixture field and all stopped/failed fields were never loaded or resumed;
- completed the explicit-VOF/PISO factor-two closed-pool ladder from `1 us` to
  `512 us`. The `256 us` stage is the last clean independent comparison. The
  `512 us` stage completed but failed its within-step continuity envelope at
  `2.56074`; a non-overwriting adjudication prohibits promotion, resume, parent
  use and a larger timestep child;
- liquid inventory, brine-face coverage and steam seal remained exact, but
  zero inlet flow and a brine wall make this conservation result trivial with
  respect to operating through-flow. No drainage, level control or operating
  mass balance was qualified;
- updated `Setup report/07n-resolved-brine-outlet-model-solver-screening.md`,
  `Setup report/order-dictionary.md`, `progress/current-status.md`,
  `progress/experiments.md`, `progress/blockers.md` and `model/validation.md`.
  No `CFD_wiki` method page was changed because this run added project-specific
  evidence rather than a new transferable CFD method or literature result;
- assumptions retired: configured server 2 is not the partner's Fluent 2025 R2
  endpoint and is not intrinsically ineligible. Assumptions retained: the
  reconstructed level is CFD-selected rather than plant-measured, and server 2
  cannot replace the authoritative server-1 lineage without the exact
  checksum-verified parent pair;
- next action: keep the server-1 step-940 pair authoritative and move to the
  separately gated open-drain pressure response/constant-level strategy when
  that parent is reachable or identically transferred and read back.

## [2026-08-25] progress-update | independent-server2-stillpool-contours

- audited the stale server-2 lock PID and exact local processes; no writer or
  controller was active before export;
- connected one post-processing owner, verified Fluent 2024 R2, 16 ranks,
  client ownership, source checksums and complete closed-pool safety readback;
- cold-loaded only the independent setup-07n time-zero, `10 us` and clean
  `5.11 ms` pairs. The terminal `512 us` field and historical failed steady
  Mixture field were not loaded;
- exported 12 matched 1920 x 1440 liquid-VF, Fluent-pressure and velocity
  contours plus five report-ready composites. All image copies and hashes
  passed; zero initialization, iteration, DPM update or case/data write was
  performed;
- visual finding: the selected pool covers the brine-leg entrance and remains
  intact over the displayed window; pressure head develops and low velocity is
  localized near the interface. The `x=-1.5 m` raw slice misses the selected
  pool and is excluded from interpretation;
- classification: `accepted post-processing diagnostic`, while the physical
  model remains `diagnostic / unresolved`. Zero feed and a closed brine wall
  still preclude drainage, constant-level and operating-mass-balance claims;
- no post-run local Fluent writer/controller remained active. Next useful
  independent server-2 work is a guarded `dt=2.56e-4 s` hold from clean step 90
  to approximately one local gravity time, without merging it into the
  authoritative server-1 lineage.

## [2026-08-25] model-update | launch independent server2 drainage response

- added thin, non-overwriting server-2 controllers for a matched closed-wall
  control and a zero-feed centre/`+/-195.156 Pa` pressure bracket from the
  checksum-bound clean step-90 pair;
- fully monitored four control steps: continuity remained
  `8.09759e-4-8.77262e-4`, Courant `0.00110266-0.00127507`, inventory exact and
  brine-face liquid VF `1.0`;
- preserved the fifth solved step as observed-but-uncredited after optional
  scratch-report deletion verification stalled. The attempt is non-resumable;
- preserved the first pressure attempt as a zero-step connection failure. Raw
  TCP passed 3/3, but Fluent did not return its Scheme version string before
  the 120 s bound; no parent load, boundary change or solve occurred;
- updated the setup-07n report, order dictionary, current status, experiments,
  blockers and validation. No CFD-wiki method page changed because no new
  drainage physics result was obtained;
- assumptions retained: the pressure bracket is CFD-derived, not plant-valid;
  server 2 remains independent; full feed and feedback require a passing
  zero-feed pressure-response and steam-seal gate;
- next immediate action: retry once under a new label only after Fluent's
  gRPC/Scheme service is responsive, always from the original step-90 pair.
- readiness close: a second read-only server-2 preflight again timed out at the
  version query despite 3/3 TCP probes, while server 1 failed its first bounded
  TCP probe. No local writer/client remained, so no physical retry was started.

## [2026-08-28] progress-update | classify calibrated-pressure 0.05%-feed long hold

- files updated: setup-07n report/order dictionary, project current status,
  experiments, blockers, validation and log, CFD method synthesis/log, plus a
  non-overwriting machine-readable disposition beside the run evidence;
- completed the independent 70-step branch after one `+23.218830875 Pa`
  brine-pressure action. Fluent 2024 R2/16 ranks, continuity, Courant, fields,
  brine liquid seal, phase routing, DPM/EWF/source and clock gates passed;
- final-ten liquid/total imbalance reached `0.01155471/0.011478693 kg/s`, so
  the sustained `0.005 kg/s` gate failed despite final continuity
  `7.93757e-4`. Classification is diagnostic/unresolved; no endpoint may be
  resumed, promoted or repeated unchanged;
- assumption retired: a pressure calibrated to one short balance window is
  sufficient for persistent balance. Assumptions retained: reported inventory
  precision cannot prove level constancy, and CFD pressure is not plant data;
- next action: fresh-load clean step 90 and add only one later held pressure
  action, with every other factor unchanged. No new physical run was launched
  near the scheduled cutoff.
