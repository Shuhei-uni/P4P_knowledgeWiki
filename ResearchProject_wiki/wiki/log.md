# Work Log

## [2026-08-14] run-correction | Retract nominal 2,000-step claim and launch enforced-step rerun

- files created/updated: `../../PyAnsys/scripts/setup/run_02d_vof_stability_screen.py`, `../../PyAnsys/scripts/setup/submit_02d_vof_enforced_step_screen.py`, `../../PyAnsys/queues/02d-vof-enforced-step-screen-20260814T026000Z.jou`, `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- purpose: audit the claimed 2,000-step coarse VOF stability screen and prevent residual-convergence termination from invalidating the requested rerun.
- what changed: transcript audit proved the nominal outputs stopped at IC0 `69`, IC1 `69`, and IC2 Y030 `67` steps, each with Fluent's `solution is converged` message. The claimed completion is retracted. New restart sources were saved and reload-verified after every data read with `1.0e-5 s`, `2,000` steps, maximum `20` inner iterations, all residual convergence checks disabled, no physical convergence reports, and retained residual history `40,000`. A new Fluent-native queue is running; its first transcript passed step 54 below the former threshold without stopping.
- assumptions introduced or retired: filenames are no longer used as iteration proof. Completion now requires transcript and flow-time evidence (`0.0200 s` per case). The run remains a conservative numerical smoke test only.
- next immediate action: inspect the native transcripts at the 1,000- and 2,000-step boundaries and record any genuine solver failure or verified terminal flow time.

## [2026-08-14] run-update | Complete coarse VOF IC0/IC1/IC2 numerical-stability screen

- files created/updated: `../../PyAnsys/scripts/setup/run_02d_vof_stability_screen.py`, `../../PyAnsys/queues/02d-vof-stability-screen-20260814T023000Z.jou`, `../../PyAnsys/queues/02d-vof-stability-screen-20260814T024000Z.jou`, `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- purpose: screen the user-selected coarse VOF IC0, IC1, and IC2 Y030 fields for a floating-point failure before any fine-mesh execution.
- what changed: IC0 completed natively at `1.0e-5 s` through 1,000 and 2,000 iterations. The first IC1/IC2 journal applied the step before loading data, and the data reads restored `1.0 s`; those outputs were retained but excluded. A corrected journal loaded data first, set `1.0e-5 s` afterward, and completed IC1 and IC2 Y030 to the same paired 1,000/2,000 checkpoints. No corrected job ended with a floating-point exception.
- assumptions introduced or retired: `1.0e-5 s` is a conservative numerical smoke-test setting only, not a Courant-qualified production timestep. No physical monitor, liquid inventory, stationarity, convergence, or separator-performance conclusion was introduced.
- next immediate action: establish mesh/Courant timestep evidence and the physical-monitor package before any result-bearing transient run.

## [2026-08-14] model-update | Prepare fine-mesh VOF IC1/IC2 patch family and dormant queue

- files created/updated: `../../PyAnsys/scripts/setup/prepare_02d_fine_patch_cases_and_queue.py`, `../../PyAnsys/queues/02d-fine-vof-ic0-ic1-ic2-queue-20260814T000000Z.jou`, `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- purpose: move the tested coarse-mesh IC1/IC2 patch definitions onto the fine VOF mesh and prepare the requested seven-case Fluent-native 500/1000-iteration queue without starting it.
- what changed: wrote paired fine-mesh IC1 and independent IC2 Y000/Y015/Y030/Y045/Y060 patch inputs, then wrote a dormant journal with IC0, IC1, and all five pool heights. IC0 initializes in the journal; patched fields reload their saved data without resetting the patches. Every job has explicit paired save commands after 500 and 1,000 iterations.
- assumptions introduced or retired: retained the user-approved five-cell pipe spill and the global-coordinate pool-height matrix. No production timestep, monitor definition, initialized-liquid volume/mass record, calculation, or numerical result was introduced.
- next immediate action: review/define transient timestep and physical monitor package, then explicitly authorize journal execution.

## [2026-08-14] model-update | Rebuild coarse VOF patch platform and hold IC1 selection

- files created/updated: `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: recreate the no-liquid-patch Stage-1 VOF configuration on the loaded coarse mesh and attempt the IC1 brine-pipe patch only where Fluent supplied an unambiguous cell-volume selection.
- what changed: Fluent wrote/reloaded `VOF-IC0-P1120-coarse-patch-platform-preinit-20260814T000000Z.cas.h5`, with the readback-verified explicit/sharp VOF contract. The mesh has `275,448` cells, one combined fluid cell zone, and minimum orthogonal quality `0.250006`. The live test session was Hybrid Initialized (10 internal initialization passes). At the user's direction, `vof_ic1_brine_outlet_5cells` was created from `brine-outlet` with cell-distance `5` and `1,499` marked cells, then patched as phase-2 `mp = 1.0` and saved as a paired case/data checkpoint. The global-coordinate IC2 register `vof_ic2_pool_below_y_0p30m` (`39,127` cells below `y = +0.30 m`) was inspected, approved, patched as phase-2 `mp = 1.0`, and saved as a separate paired checkpoint. The Y000 sibling was independently rebuilt from the IC1 checkpoint, patched below `y = +0.00 m` (`33,200` cells), and saved. A `+0.00/+0.15/+0.30/+0.45/+0.60 m` plane-based initial-pool sensitivity matrix is now defined. No flow timestep or solve was made.
- assumptions introduced or retired: no geometric assumption was introduced. The requested IC1 target remains the full pipe fluid volume only; a boundary face does not prove or provide that volume.
- next immediate action: build the planned `+0.15`, `+0.45`, and `+0.60 m` IC2 initialization siblings only when needed, recording each marked volume and initialized liquid mass before any transient run.

## [2026-08-14] model-update | Build setup 02d VOF-IC0 no-patch case from brine-outlet mesh

- files created/updated: `../../PyAnsys/scripts/setup/build_02d_vof_ic0_from_mesh.py`, `../../PyAnsys/output/02d_vof_ic0_mesh_inspection.json`, `../../PyAnsys/output/02d_vof_ic0_vof_probe.json`, `../../PyAnsys/output/02d_vof_ic0_build_verification.json`, `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `wiki/progress/experiments.md`, `wiki/progress/current-status.md`, `../../PyAnsys/knowledge/fluent-settings/logs/successful_paths.md`, `wiki/log.md`
- purpose: create the requested no-liquid-patch Stage-1 VOF case as a case-only artifact from the supplied `brine-outlet-620kcells.msh.h5` mesh and verify it by explicit reload.
- what changed: Fluent found the mesh at `C:\Users\syok443\P4P simulation\brine-outlet-620kcells.msh.h5`, read its required split-inlet/two-pressure-outlet zone topology, and wrote/reloaded `VOF-IC0-P1120-preinit-20260814T000000Z.cas.h5`. Readback confirmed explicit/sharp VOF, Geo-Reconstruct, PRESTO!, RNG k-epsilon, controlled pressures/velocities/volume fractions, and no active DPM interaction or injection.
- assumptions introduced or retired: this is explicitly a mesh-based reconstruction rather than a verified `02c` parent clone. Gravity direction follows the prior project coordinate convention; surface tension/contact angle, local VOF mesh size/quality, pipe-connectivity visualization, monitors, and a Courant-justified timestep remain unresolved. No initialization, phase patch, solve, data write, or production claim was introduced.
- next immediate action: inspect local cell sizes and quality in all interface-sensitive regions, define `VOF-DT1`/`VOF-DT2` plus monitor surfaces, and visually verify the lower tangential-pipe connection before authorizing a Hybrid Initialization.

## [2026-08-14] model-update | Define setup 02d transient VOF brine-outlet model-form sensitivity

- files created/updated: `../../Setups/future/02d-transient-vof-brine-outlet-model-form-sensitivity.md`, `../../Setups/future/index.md`, `../../Setups/order-dictionary.md`, `wiki/index.md`, `wiki/log.md`
- purpose: preserve the user-specified Stage-1 transient explicit-VOF comparison as a distinct future setup branch from the active steady Mixture `02c` brine-outlet sensitivity.
- what changed: defined the inherited operating basis, explicit VOF controls, `VOF-IC0/IC1/IC2-P1120` initialization study, Courant-based timestep and `DT1`/`DT2` sensitivity gates, required transient monitors/diagnostics, staged DPM/EWF plan, and the later `1.115/1.120/1.125 MPa` VOF pressure sweep.
- assumptions introduced or retired: parent artifact identity, VOF-relevant mesh size, surface-tension/contact-angle evidence, and IC1/IC2 patch geometry remain explicit missing information; no Fluent setting, patch, mesh change, case artifact, or numerical result was created.
- next immediate action: read back a verified `02c`-comparable parent in Fluent, inspect local mesh sizes and available regions, then request the user's manual patch selection only if IC1 or IC2 is to be built.

## [2026-08-14] run-update | Launch setup 02c native positive-backpressure queue

- files created/updated: `../../PyAnsys/src/pyansys_fluent/positive_backpressure_queue.py`, `../../PyAnsys/scripts/setup/generate_02c_positive_backpressure_queue.py`, `../../PyAnsys/queues/02c-positive-backpressure-screen.yaml`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- purpose: launch the prepared D/E/F/G 02c positive-backpressure cases serially through the one existing Fluent session, so each case is saved before the next independent child begins.
- what changed: Fluent accepted the native quoted journal and began loading Case D. The first autosave-menu configuration attempt failed safely before Case D was loaded because the live 2025 R2 command is interactive/prompt-sensitive; the final launched journal instead performs the known explicit paired case/data save after each completed 500-iteration screen.
- current status: launched / completion unverified. TCP remains reachable but bounded read-only gRPC reconnection attempts did not complete while Fluent was busy; no additional solver action was issued.
- next immediate action: verify remote endpoint pairs after Fluent returns control, then conduct the same carrier/residual analysis for D/E/F/G.

## [2026-08-12] setup-update | Prepare setup 02c positive-backpressure screen

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/future-runs.md`, `../../PyAnsys/scripts/setup/build_02c_positive_backpressure_cases.py`, `../../PyAnsys/queues/02c-positive-backpressure-screen.yaml`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: extend the unprimed 02c brine-outlet pressure screen above the fixed steam-outlet pressure after the A/B/C early results showed a strong vapour-routing direction.
- what changed: prepared independent case-only children D (`1.1225 MPa`), E (`1.1275 MPa`), F (`1.1300 MPa`), and G (`1.1350 MPa`) from the same frozen pre-initialization parent. The live Fluent 2025 R2 brine-pressure path was inspected and each requested pressure read back before its remote case-only save.
- assumptions introduced/removed: no new physical model assumption. The positive-backpressure behaviour remains an `Inferred` screening hypothesis; Case C's initial-inventory ambiguity remains unresolved.
- next action: run each prepared child in Fluent with native autosave and a common liquid-inventory/phase-flux monitor package, then classify drainage as settling, inventory depletion, restricted, or indeterminate.

## [2026-08-12] analysis-update | Analyse setup 02c Case C higher-pressure screen

- purpose: analyse the user-confirmed retained Case C `iter500` Fluent session without changing model physics.
- what changed: carrier flux/residual extraction, EWF/DPM audit, and all six inherited DPM particle-track summaries completed. EWF was inactive; DPM coupling was off and the inherited release surfaces were `steam-outlet`.
- measured result: liquid brine outflow was `136.604543 kg/s` from a `116.847094 kg/s` liquid inlet; vapour brine and steam outflows were `26.743944` and `54.827687 kg/s` from `81.639506 kg/s` inlet. Final continuity was `1.194315e-1`.
- derived interpretation: Case C has the lowest observed vapour wrong-outlet fraction of the three early screens, but its liquid phase is unclosed. No pressure ranking is justified.
- current status: all A/B/C early checkpoints now have carrier, residual, audit, and DPM evidence bundles.
- next immediate action: introduce common stability/liquid-inventory monitoring and continue or rerun all three cases to a shared stable window before pressure selection.

## [2026-08-12] run-update | Execute setup 02c Case C higher-pressure TUI screen

- purpose: execute the higher-brine-pressure (`1.125 MPa`) point from the frozen parent using Fluent-native TUI initialization and iteration commands.
- what changed: the parent was explicitly loaded, only brine-outlet pressure was changed, the Case C pre-initialization child was saved, and Fluent completed Hybrid Initialization plus `solve/iterate 500`. The paired endpoint checkpoint was written and verified.
- current status: Case C is ready for explicit-reload carrier/residual/audit/DPM analysis; no numerical separation or pressure-ranking statement has been made.
- next immediate action: post-process the verified Case C `iter500` pair using the same workflow as Cases A and B.

## [2026-08-12] run-update | Execute setup 02c Case A lower-pressure unprimed screen

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: execute the lower-brine-pressure (`1.115 MPa`) point of the unprimed 02c sensitivity matrix from the frozen Case B pre-initialization parent.
- what changed since the previous update: Case A was built with only brine-outlet gauge pressure changed, Hybrid Initialized without a liquid patch, and allowed to pass the requested 500-iteration milestone. A recovery continuation overlapped the still-advancing native solve; it was allowed to complete rather than interrupted, and the resulting paired 649-iteration case/data checkpoint was verified on the remote store.
- assumptions introduced or retired: none. The Case A result is explicitly a preliminary screening state; no claim is made that 649 iterations produce convergence, and no pressure ranking is inferred.
- current status: Case A exists as a verified final pair pending explicit reload and analysis. The separately written file with an `iter500` suffix is an approximately 351-iteration intermediate state and is excluded from analysis.
- blockers: residual plateau, steam-outlet reverse flow, and turbulence limiting remain visible in live monitoring. Carrier/phase-flux, DPM, and residual artifact extraction are still required before comparison with Case B.
- next immediate action: run the Case A analysis suite against the verified `iter649` pair, then assess whether Case C is warranted under the same controlled protocol.

## [2026-08-12] analysis-update | Analyse setup 02c Case A lower-pressure unprimed screen

- files created/updated: `../../Setups/reports/02c/results.md`, `../../Setups/reports/02c/future-runs.md`, `../../Setups/reports/index.md`, `../../PyAnsys/output/post_simulation_analysis/02c-A-brine-p1115kpa-unprimed-iter649-*`, `../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-*`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: analyse the explicitly identified 649-iteration Case A case/data checkpoint without changing its physics.
- what changed since the previous update: carrier flux and residual extraction, EWF/DPM audit, and all six inherited DPM particle-track summaries completed. EWF was inactive; the complete DPM bundle was retained but its injection surfaces were `steam-outlet`.
- measured result: liquid brine outflow was `45.799051 kg/s` from `116.847094 kg/s` inlet and vapour brine outflow was `49.294436 kg/s` from `81.639506 kg/s` inlet. Final continuity was `1.265345e-1` after a `7.966281e-2` minimum.
- derived interpretation: Case A's early screen has higher observed liquid brine recovery than Case B but also a higher vapour wrong-outlet fraction. These are not pressure-selection results because neither checkpoint is converged or sampled at a common stable window.
- current status: Case A and Case B now have complete checkpoint-linked analysis bundles; Case C remains unbuilt/unanalysed.
- blockers: persistent non-convergence, open liquid closure, and inherited steam-outlet DPM release surfaces prevent any separator-performance or pressure-ranking claim.
- next immediate action: build Case C using the same frozen parent and a controlled common stopping/convergence rule, then compare all three points as screening evidence only unless convergence is achieved.

## [2026-08-12] progress-update | Analyse setup 02c Case B unprimed brine-outlet pressure screen

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/results.md`, `../../Setups/reports/02c/future-runs.md`, `../../PyAnsys/output/post_simulation_analysis/02c-B-brine-p1120kpa-unprimed-iter500-*`, `../../PyAnsys/output/ewf_dpm_diagnostics/02c-B-iter500-*`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: run and analyse the first `02c` three-pressure-matrix screening point without liquid initialization, then preserve the evidence and reserve the remaining matrix points without manufacturing results.
- what changed since the previous update: Case B at `1.120 MPa` brine pressure was hybrid-initialized, reached a saved 500-iteration checkpoint, and was explicitly reloaded for carrier flux/residual analysis and the full inherited DPM sweep. Carrier fluxes show low liquid brine recovery (`6.921014 kg/s` of `116.847094 kg/s` liquid inlet) and substantial vapour flow to the brine outlet (`42.547417 kg/s` of `81.639506 kg/s` vapour inlet). All six active DPM injection sweeps completed; EWF was inactive.
- assumptions introduced or retired: no pressure-performance ranking was introduced. The result is retained as an early unprimed diagnostic because continuity remains `1.239373e-1`, phase closure is open, and the required liquid-inventory/pressure-history and visual diagnostics were not yet instrumented.
- current status: Case B evidence is complete and linked to setup `02c`; Cases A (`1.115 MPa`) and C (`1.125 MPa`) remain not built/not run placeholders.
- blockers: the Case B field is not converged and its two-outlet mass split is unsuitable for a design claim; whether a brine-pressure change improves this remains untested.
- next immediate action: build Case A from the frozen pre-initialization parent and repeat the same 500-iteration protocol before comparing pressure points.

## [2026-08-04] model-update | Stop 09cV3 run at saved iteration-50 checkpoint

- files created/updated: `../../PyAnsys/scripts/setup/run_09cV3_student_50_then_100.py`, `../../PyAnsys/output/09cV3_student_50_then_100_run_20260804.json`, `../../PyAnsys/output/09cV3_student_50_then_100_run_state_20260804.json`, `../../Setups/active/09cV3-fine-mist-5pct-psd-rerun.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `../../PyAnsys/knowledge/fluent-settings/logs/successful_paths.md`, `wiki/log.md`
- purpose: execute the user-requested 50-iteration run, save a resumable checkpoint, begin the resumed continuation, and stop cleanly when the user changed the instruction.
- what changed since the previous update: hybrid-initialized and completed the first 50 iterations; wrote and verified paired iteration-50 case/data files; explicitly loaded that pair and began the resumed stage. The user stopped the run during the chunk covering iterations 51–60 after the transcript reached 51–59. The live session was restored from the saved iteration-50 pair.
- assumptions introduced or retired: no convergence or performance claim was introduced. Iteration-50 residuals and DPM counts are retained as diagnostic monitor output only; the exact in-memory state at the interrupted second-stage chunk is not treated as a saved checkpoint.
- current status: iteration-50 case/data checkpoint is complete and verified; iteration-100 case/data checkpoint does not exist; the original case-only 09cV3 child is untouched; the live session is restored to iteration 50.
- blockers: no new construction blocker; the run remains numerically diagnostic with high continuity residual and outlet reverse-flow warnings, and the inherited velocity-inlet mass-flow closure remains unverified.
- next immediate action: do not resume unless explicitly requested; if resumed later, start from the saved iteration-50 case/data pair.

## [2026-08-04] model-update | Build 09cV3 fine-mist child case

- files created/updated: `../../Setups/active/09cV3-fine-mist-5pct-psd-rerun.md`, `../../PyAnsys/scripts/setup/build_09cV3_student_finemist_from_09cV2.py`, `../../PyAnsys/output/09cV3_student_finemist_verification_20260804.json`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `../../PyAnsys/knowledge/fluent-settings/logs/successful_paths.md`, `wiki/log.md`
- purpose: build the direct `09cV2` child case with the documented seven-bin `5–100 µm` fine-mist PSD while retaining the parent 5% DPM allocation and all non-PSD settings.
- what changed since the previous update: loaded the explicit Student `09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5`, wrote a recovery copy, replaced the six legacy active injections with seven `09cV3` fine-mist injections on `steaminlet`, saved `09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`, and reloaded it by full path for strict verification. Fluent 2025 R2 serialized the requested injection identities as lowercase `09cv3-finemist-*` names; all seven are active and sum to `5.846000 kg/s`.
- assumptions introduced or retired: retained the parent velocity-inlet adaptation caveat; `111.074000 kg/s` remains an input allocation reference without an independent live mass-flow report. Retained the seven-bin PSD as an `Assumed`, medium-risk engineering prior; no run-facing result or convergence claim was introduced.
- current status: `09cV3` case-only build is complete and reload-verified; the live Student session is left on the saved child; no flow iterations, data read, or `.dat.h5` write occurred.
- blockers: no new blocker from setup construction; the inherited mass-flow closure remains unverified at the live flux-report level, and DPM/phase behavior has not been smoke-tested.
- next immediate action: if execution is authorized, run a bounded `20–50`-iteration smoke test from the saved child and capture residual, phase-flux, DPM-source, and per-injection fate diagnostics before any interpretation.

## [2026-08-04] model-update | Define 09cV3 fine-mist 5% DPM rerun

- files created/updated: `../../Setups/active/09cV3-fine-mist-5pct-psd-rerun.md`, `../../Setups/active/09cV2-skoog-partition-injection-control.md`, `../../Setups/active/index.md`, `../../Setups/order-dictionary.md`, `wiki/model/fine-mist-dpm-size-and-mass-distribution.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- purpose: create the direct `09cV2` child that recreates the 5% DPM allocation using the seven-bin `5–100 µm` fine-mist injection sizes and mass distribution recorded after the meeting.
- assumptions introduced or retired: the seven-bin PSD and its mass shares remain an `Assumed`, medium-risk engineering prior rather than a measured geothermal inlet PSD; retained the parent `5.846000 kg/s` DPM and `111.074000 kg/s` Eulerian-liquid allocations so the PSD is the only intentional physics-input change.
- next immediate action: copy a read-back-verified `09cV2` 5% checkpoint, deactivate the six legacy injections, create the seven `09cV3` injections, verify the active-flow sum and DPM interaction settings, then run a short diagnostic smoke test.

## [2026-07-30] model-update | Define carrier-field mesh-convergence family

- files created/updated: `../../Setups/future/12-carrier-mesh-convergence-plan.md`, `../../Setups/future/index.md`, `../../Setups/order-dictionary.md`, `wiki/vnv/verification/index.md`, `wiki/progress/current-status.md`, `wiki/index.md`, `wiki/log.md`
- reason: user requested a practical mesh-convergence start from the current approximately `1.3M`-node case, with trial meshes near `500k`, `700k`, and `1.0M` nodes.
- what changed since last update: recorded the observed `1,309,312`-node / `7,601,261`-cell live checkpoint as an additional fine reference; created a planned M0–M3 carrier-only comparison with fixed report definitions, mesh-quality/zone checks, and common solution-acceptance requirements.
- assumptions introduced/removed: treats the `08b`-compatible carrier case as the default parent unless an operator explicitly freezes a different baseline; treats the `~1.12` refinement ratios as practical sensitivity evidence rather than sufficient by themselves for a formal Richardson/GCI uncertainty claim.
- current status: mesh-convergence setup plan is ready; no new mesh has been generated or solved.
- blockers: exact frozen parent case/data, the common report definitions, and per-mesh quality statistics remain to be read back in Fluent.
- next action: export and Fluent-reopen the approximately `500k`-node M0 mesh, verify its zone/quality contract, then solve it to the same monitor gate used for all levels.

## [2026-07-30] model-update | Revise mesh-convergence ladder around the live reference

- files created/updated: `../../Setups/future/12-carrier-mesh-convergence-plan.md`, `../../Setups/future/index.md`, `../../Setups/order-dictionary.md`, `wiki/progress/current-status.md`, `wiki/index.md`, `wiki/log.md`
- reason: user refined the requested mesh ladder to approximately `400k`, `900k`, `1.3M`, and `1.6M` nodes.
- what changed since last update: the observed `1,309,312`-node mesh is now M2 rather than an after-the-fact reference; the planned M0 and M1 meshes are `400k` and `900k`, and M3 is a planned `1.6M`-node fine comparison.
- assumptions introduced/removed: M0-to-M1 has an estimated linear refinement ratio of `1.31`, but M1-to-M2 and M2-to-M3 remain tighter; the study is still a practical mesh-sensitivity test unless the completed output sequence supports a formal uncertainty estimate.
- current status: plan revised; no meshes have been generated or solved for setup `12`.
- blockers: exact frozen parent case/data, the common report definitions, and per-mesh quality statistics remain to be read back in Fluent.
- next action: export and Fluent-reopen the approximately `400k`-node M0 mesh, verify its zone/quality contract, then solve it to the same monitor gate used for all levels.

## [2026-07-27] model-update | Add 010V2b 5,000-iteration observation evidence
- files created/updated: `observations/04-010v2-ewf-mechanism-comparison.md`, `observations/06-010v2-iteration-continuation.md`, `wiki/log.md`
- reason: synchronize all project observations that use the `010V2b` edge-separation branch with its completed 5,000-iteration result.
- what changed: replaced the stale 1,498-iteration branch values with the 5,000-iteration film, DPM-fate, carrier/residual, and separation-event results; linked the fresh 2026-07-27 recapture as corroborating EWF/DPM evidence with no new carrier bundle.
- assumptions introduced/retired: separated events remain a secondary event/parcel count and are not added to terminal mass closure; no edge-separation mass balance, EWF closure, convergence, or separator-performance claim was added.
- next immediate action: repair EWF field aliases and instrument a defined continuation interval with film source, outflow, CFL, and separated-mass histories.

## [2026-07-24] progress-update | Reclassify Purnanto scope limitations
- files created/updated: `wiki/model/baseline-cfd.md`, `wiki/progress/blockers.md`, `wiki/project/roadmap.md`, `../../CFD_wiki/wiki/physics-basis/uncertainties-and-assumption-register.md`, `../../Setups/index.md`, `../../Setups/templates/results-report-template.md`, `../../PyAnsys/src/pyansys_fluent/postprocess_live.py`, `../../PyAnsys/tests/test_postprocess_live.py`, `../../skills/post-simulation-analysis/SKILL.md`, `../../skills/post-simulation-analysis/references/report-structure.md`, `wiki/log.md`
- reason: align project interpretation with the simplified Purnanto geometry and stop treating missing lower-liquid closure or Fluent `Incomplete` DPM trajectories as active blockers.
- what changed since last update: added the governing scope boundary, downgraded BLK-008/BLK-009 to accepted scope limitations, refocused active blocker language on residuals, iteration maturity, monitors, mesh quality/convergence, and made generated reports retain raw diagnostics without using them as gates.
- assumptions introduced/retired: introduced the explicit `purnanto_simplified_no_liquid_outlet` policy; retired whole-domain imbalance and incomplete DPM completion as current acceptance criteria.
- current status: residuals, iteration maturity, mesh convergence, and setup parity remain the active numerical concerns.
- blockers: no new blocker introduced by this interpretation change; automated pytest verification is unavailable in the current environment.
- next immediate action: run the post-processing test suite where pytest is available and review generated report wording for active setup outputs.

## [2026-07-24] model-update | Refresh EWF observations with 5,000-iteration checkpoints
- files created/updated: `observations/04-010v2-ewf-mechanism-comparison.md`, `observations/05-010v2d-global-dpm-interaction.md`, `wiki/log.md`
- reason: synchronize the cross-branch EWF and global-DPM observations with the newly populated 5,000-iteration setup reports.
- what changed: replaced the stale lower-iteration film, DPM-fate, event, and residual values with the latest completed checkpoints; retained `010V2b` as unavailable at 5,000 and `010V2d-2` at its latest completed 4,189 checkpoint.
- assumptions introduced/retired: no mechanism or global-DPM causal claim was strengthened; unmatched checkpoints, open carrier balance, missing EWF histories, and unavailable generated-particle mass remain explicit.
- next immediate action: obtain a completed `010V2b` 5,000 checkpoint and a matched `010V2d`/`010V2d-2` interval before interpreting mechanism or global-interaction effects physically.

## [2026-07-24] synthesis | Deepen 010V2 5,000-iteration continuation analysis
- files created/updated: `observations/06-010v2-iteration-continuation.md`, `wiki/log.md`
- purpose: replace the endpoint-only continuation screen with a checkpoint-comparability audit, normalized coarse-DPM fate shifts, film localisation/transport analysis, residual-tail variability screen, and an evidence-ranked next-run decision.
- assumptions introduced or retired: retained continued net film storage as an inference rather than a closed balance; retired the implicit idea that low final 5,000-iteration film CFL or a lower final turbulence residual alone demonstrates a settled state.
- next immediate action: instrument one verified restart interval with film source/flux/CFL histories and full carrier coverage before any further end-only continuation checkpoint.

## [2026-07-24] model-update | Record 010V2 5,000-iteration continuation observation
- files created/updated: `observations/06-010v2-iteration-continuation.md`, `observations/index.md`, `observations/order-dictionary.md`, `wiki/index.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- purpose: compare the new 5,000-iteration evidence for the splash, edge-separation, stripping, and combined EWF branches against their earlier lower-iteration checkpoints without conflating it with the existing cross-mechanism observation.
- assumptions introduced or retired: retained final-state film and terminal-fate changes as diagnostic trends only; did not infer convergence, EWF closure, mechanism causality, or separator performance from the open carrier scope, missing histories, and unmatched session metadata.
- next immediate action: repair the EWF report aliases and record interval histories plus complete carrier boundary fluxes before continuing one branch from a verified shared checkpoint.

## [2026-07-24] refactor | Reconcile active setup lifecycle
- files created/updated: `../../Setups/active/`, `../../Setups/past/reported/`, `../../Setups/past/archived/`, `../../Setups/order-dictionary.md`, `../../Setups/reports/`, `observations/03-08b-09c-global-dpm-interaction.md`, `wiki/index.md`, `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/log.md`
- purpose: make `08c`, `09cV2`, and the complete `010V2` family the sole active setup set and remove the experimental HTML/MDX presentation copies.
- assumptions introduced or retired: classified the splash-enabled recorded artifact as `10a-splash` evidence rather than a clean no-splash `10a` result; retained future `10` and `11` family plans as future rather than treating them as displaced active setups.
- next immediate action: use `Setups/active/index.md` as the canonical execution list and keep new numerical findings in the linked setup reports.

## [2026-07-22] model-update | Strengthen 010V2d global-DPM-plus-EWF comparison
- files created/updated: `observations/05-010v2d-global-dpm-interaction.md`, `wiki/log.md`
- reason: make the combined-EWF global-DPM interaction evidence more transparent without expanding its claim strength.
- what changed: added comparison-integrity, film-localisation, full six-bin terminal-fate, coarse secondary-event, residual-ratio, and causal-evidence-chain comparisons.
- assumptions introduced/removed: retained direct interaction as the intended primary change; did not attribute unmatched snapshot differences or event counts to a closed mass/momentum mechanism.
- current status: the coupled checkpoint has stronger local film/fate/event signals but no validated bulk-throughput change.
- blockers: slight payload and checkpoint mismatch, open carrier balance, and absent DPM-to-carrier/film source histories.
- next action: rerun an exact common-checkpoint pair with identical payload and interval histories.

## [2026-07-22] model-update | Expand 010V2 EWF mechanism comparison
- files created/updated: `observations/04-010v2-ewf-mechanism-comparison.md`, `wiki/log.md`
- reason: compare reported clean, splash, edge-separation, stripping, and combined EWF branch results more completely while retaining their diagnostic limits.
- what changed: added run-comparability, film-morphology, size-resolved absorbed-mass, mechanism-activation, and EWF bookkeeping comparisons; incorporated the stripping branch's completed console fate/film results rather than treating the branch response as absent.
- assumptions introduced/removed: retained snapshots and event signals as diagnostic evidence only; did not infer generated-particle mass or a separate stripping mass where Fluent did not report it.
- current status: size-selective DPM-to-film absorption is consistent across branches; optional mechanisms show activation/event signals but not closed mass effects.
- blockers: open carrier flux scope, unmatched checkpoints, no defined EWF history, and unreconciled generated-particle mass.
- next action: rerun isolated mechanisms from one accepted control checkpoint with corrected EWF-history/report tokens, then combine only mass-bounded mechanisms.

## [2026-07-22] model-update | Convert global-DPM observation to three-way evidence sequence
- files created/updated: `observations/03-08b-09c-global-dpm-interaction.md`, `wiki/log.md`
- reason: compare the branch chain `08b` → `09c` → `09cV2` while preserving the absent original-`09c` particle-fate result as an explicit future evidence slot.
- what changed: replaced the direct endpoint table with three-way DPM accounting, setting, checkpoint, and fate fields; added the `09c` six-injection tracking placeholder; and made completion of that record a next-run gate.
- assumptions introduced/removed: removed the direct `08b`/`09cV2` framing; no `09c` fate values were inferred.
- next action: add the original `09c` DPM Particle Tracks Summary to the placeholder, then distinguish interaction and allocation effects.

## [2026-07-22] model-update | Add exploratory 08b/09cV2 DPM tracking contrast
- files created/updated: `observations/03-08b-09c-global-dpm-interaction.md`, `wiki/log.md`
- reason: retain the useful DPM-fate contrast between the one-way `08b` sample and the later mass-partitioned `09cV2` coupled diagnostic without misrepresenting it as a controlled interaction result.
- what changed: added parcel, fate, and represented-mass-flow comparisons; identified the fine-bin escape and coarse-bin trapping pattern in `09cV2`; and listed the co-changing allocation, material, solver/version, carrier maturity, and tracking-report factors.
- assumptions introduced/removed: retained the comparison as exploratory; did not attribute its fate difference to DPM interaction alone.
- next action: reproduce the fate comparison from a common carrier state with one controlled change at a time.

## [2026-07-22] model-update | Strengthen 08b/09c global-DPM-interaction observation evidence chain
- files created/updated: `observations/03-08b-09c-global-dpm-interaction.md`, `wiki/log.md`
- reason: make the global DPM comparison traceable to its coupling readback, carrier flux artifacts, and DPM mass-accounting boundary.
- what changed: documented the verified interaction controls, the additional `29.22 kg/s` DPM payload (approximately `25%` of the Eulerian liquid inlet), the unmatched flux deltas, missing source/fate evidence, and exclusion of the differently partitioned `09cV2` branch.
- assumptions introduced/removed: removed any implication that the 921-iteration `09c` checkpoint measures a physical two-way-DPM effect or that `09cV2` is a direct comparator; retained global DPM interaction as an isolated diagnostic variable.
- current status: setting isolation is verified; physical coupling impact remains unresolved.
- blockers: unmatched carrier maturity, open flux scope, unpartitioned DPM loading, no integrated DPM-source history, and no matched terminal-fate records.
- next action: run a common-window, mass-accounted one-way/two-way pair with source, flux, residual, and fate outputs.

## [2026-07-22] model-update | Strengthen 08b/08c inlet-loading observation evidence chain
- files created/updated: `observations/01-08b-08c-inlet-loading.md`, `wiki/log.md`
- reason: distinguish the carrier phase-flux loading trend from the separate one-way DPM tracking evidence and preserve the limits of each.
- what changed: added a low/reference/high carrier-flux and DPM-fate comparison, documented the fixed DPM probe basis and non-additivity, linked the raw 08c carrier/DPM artifacts, and set a matched carrier/DPM rerun gate.
- assumptions introduced/removed: retained the directional carrier-flow interpretation; removed any implication that DPM escaped mass can be added to Eulerian steam-outlet liquid flow or that incomplete DPM tracks show collection.
- current status: inlet loading remains a directional carrier-flow observation only; DPM fate versus loading is unresolved.
- blockers: open carrier phase balances, unmatched iteration checkpoints, and incomplete DPM trajectories.
- next action: obtain common accepted carrier states with a closed flux scope, then repeat matched DPM tracking with per-injection zone summaries.

## [2026-07-16] reorganization | Reorganize setup records and numerical reports
- files created/updated: `../../Setups/`, `../../Setups/index.md`, `../../Setups/order-dictionary.md`, `../../Setups/reports/`, `wiki/index.md`, `wiki/project/roadmap.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: reorganize the setup-report system around concrete setup definitions, lifecycle views, and linked numerical result reports so experiment findings are easier to locate.
- what changed since last update: renamed `Setup report/` to `Setups/`; grouped setup definitions into active, future, past/reported, and past/archived folders; created linked reports for setups `04`, `07`, `08b`, `09a`, and `09b`; added setup/report templates and a numerical-evidence rule.
- assumptions introduced/removed: `reported` requires actual flux-efficiency/carryover numerics and/or numerical DPM trajectory/fate counts; lifecycle and evidence-use labels remain separate, so diagnostic or incomplete results can be reported without being treated as validated.
- current status: `08c` and `09c` are active; `04`, `07`, `08b`, `09a`, and `09b` are past reported; remaining existing setup definitions are archived until stronger numerical evidence is recorded.
- next action: update a setup's lifecycle and linked report when new run evidence changes its role, without renumbering the lineage.

## [2026-07-02] model-update | Add setup 08b one-injection DPM sample attribution
- files created/updated: `../../../PyAnsys/src/pyansys_fluent/postprocess_live.py`, `../../../PyAnsys/scripts/inspection/postprocess_live_case.py`, `../../../PyAnsys/tests/test_postprocess_live.py`, `../../../PyAnsys/output/live_postprocess/TwoPhaseInletV2(Purnanto)-25-05000-summary.json`, `../../../PyAnsys/output/live_postprocess/TwoPhaseInletV2(Purnanto)-25-05000-report.md`, `../../Setup report/08b-purnanto-parity-split-inlet-rebuild.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- reason: user asked to repeat the DPM check injection by injection, matching the manual Fluent `Discrete Phase > Sample` workflow, so the active 6-bin `08b` result can be attributed per injection rather than only through the aggregate summary.
- what changed since last update: added reusable live-Fluent per-injection `dpm-sample` support to the `PyAnsys` post-processing toolchain, reran the loaded `08b` case injection by injection against `steamoutlet`, and recorded that the sampled aggregate remains `13012` incomplete / `8` escaped / `0` trapped, with the completed sampled escape confined to `injection-5-micron` in the current pass.
- assumptions introduced/removed: introduced the explicit limitation that the new per-injection counts are still boundary-scoped `dpm-sample` diagnostics rather than full validated fate accounting; removed the earlier gap that the `08b` escaped-row attribution was only inferred indirectly from the aggregate summary text.
- current status: setup `08b` now has both aggregate and one-injection sampled DPM attribution recorded, but the result still remains `Debug only` because incomplete tracks dominate every active sampled bin except for the small completed `5-micron` escape count.
- next action: raise the DPM tracking budget or export stronger per-injection fate summaries before treating the per-bin result as stronger evidence.

## [2026-07-02] model-update | Create setup 08c inlet-velocity sensitivity branch
- files created/updated: `../../Setup report/08c-purnanto-parity-inlet-velocity-sensitivity.md`, `../../Setup report/order-dictionary.md`, `wiki/project/roadmap.md`, `wiki/index.md`, `wiki/log.md`
- reason: user wants the next stage after setup `08b` recorded as setup `08c` after supervisor advice to test how different inlet velocities affect separator efficiency while keeping the inlet enthalpy basis fixed.
- assumptions introduced/removed: introduced the working interpretation that setup `08c` should keep inlet **specific enthalpy** fixed and vary inlet **mass loading / resulting velocity** only; explicitly separated that from any later enthalpy-sensitivity branch so the next test does not mix two major changes at once.
- current status: setup `08c` now exists as the planned child of `08b`, with the first recommended loading ladder recorded and the enthalpy-versus-flow-rate interpretation made explicit.
- next action: calculate the actual split-zone mass-flow targets for the chosen `0.75x`, `1.00x`, `1.25x`, and `1.50x` loading points, then build and run the first `08c` carrier cases before deciding whether DPM or enthalpy sensitivity should follow.

## [2026-07-02] model-update | Refine setup 08c to target 20 m/s and 32.14 m/s endpoints
- files created/updated: `../../Setup report/08c-purnanto-parity-inlet-velocity-sensitivity.md`, `wiki/project/roadmap.md`, `wiki/log.md`
- reason: user clarified that the next sensitivity branch should stay mass-flow-inlet based, but the actual endpoint cases should correspond to prescribed low/high inlet velocities rather than generic loading multipliers.
- assumptions introduced/removed: replaced the provisional `0.75x` to `1.50x` ladder with endpoint velocity cases; kept `32.14 m/s` as the repo-backed upper reference from the live audit and labeled `20.00 m/s` as a user-specified low-end sensitivity point pending source confirmation.
- current status: setup `08c` now records equivalent split-zone mass-flow targets for `20.00 m/s`, the current `08b`-adjacent reference condition, and `32.14 m/s` while keeping the branch as a split `Mass-Flow Inlet` study at fixed enthalpy basis.
- next action: build the `20.00 m/s` and `32.14 m/s` carrier cases using the recorded equivalent mass-flow values, then compare steam-line carryover, pressure drop, and residual stability against the existing `08b` reference case.

## [2026-07-02] model-update | Record setup 08b live post-processing and current DPM summary
- files created/updated: `../../Setup report/08b-purnanto-parity-split-inlet-rebuild.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- reason: user finished the continuous-field `5000`-iteration run for setup `08b`, asked for the actual post-processing workflow on the loaded Fluent case/data, and then asked for the current DPM escaped/trapped/incomplete outcome for the active 6-injection set.
- what changed since last update: recorded the live `08b` phase-flux result (`steamoutlet` liquid `0.082132007 kg/s`, vapor `81.464165 kg/s`), the scoped flux-based steam-line carryover efficiency (`99.93 %`), the large mixture imbalance (`116.063719 kg/s`), and the refreshed aggregate DPM summary (`13012` incomplete, `8` escaped, no trapped row printed) for the active 6-bin subset.
- assumptions introduced/removed: kept the user-specified limitation that bins `562.70 um`, `844.06 um`, and `1631.84 um` remain intentionally omitted from this pass; introduced the explicit rule that the current `08b` DPM result stays `Debug only` because incomplete tracks dominate the updated summary.
- current status: setup `08b` now has a live post-processing record and a current aggregate DPM-screening result, but neither the carrier flux result nor the DPM result is yet strong enough for report-quality validation language.
- next action: increase DPM tracking budget and, if needed, export per-injection zone summaries before trying to interpret the active 6-bin DPM result more strongly.

## [2026-06-11] model-update | Pivot V&V target from setup 07 to extraction-first setup 08b
- files created/updated: `../../Setup report/08b-purnanto-parity-split-inlet-rebuild.md`, `../../Setup report/order-dictionary.md`, `../../Setup report/09-multiphase-separator-sensitivity-family.md`, `../../Setup report/09a-dpm-split-inlet-carryover.md`, `../../Setup report/09b-rsm-dpm-split-inlet-accuracy.md`, `../../Setup report/09c-dpm-ewf-wall-film-reentrainment.md`, `wiki/project/roadmap.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/index.md`, `wiki/log.md`
- reason: user realized setup `07` likely contains human reconstruction drift from the real Purnanto Fluent case and wants the next serious V&V branch to be rebuilt from extracted settings rather than from memory.
- assumptions introduced/removed: removed the working assumption that setup `07` should stay the main V&V parent; introduced setup `08b` as the extraction-first parity-reset branch while keeping setup `08` as the one-inlet automation scaffold and keeping the existing `09` numbering stable instead of renumbering older setup reports again.
- next action: build the robust `PyAnsys` extraction workflow, diff the live audit against setup `07`, then rebuild setup `08b` with only the intended split-inlet change and later steam-side `DPM` injection definition.

## [2026-06-11] model-update | Correct geometry-to-setup mapping for purnanto naming
- files created/updated: `../../Setup report/04-mixed-wet-half-actual-area.md`, `../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`, `../../Setup report/06-pure-phase-split-fixed-velocity.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`, `../../Setup report/order-dictionary.md`, `wiki/model/inlet-regimes.md`, `wiki/technical/v2-purnanto-spiral-inlet-geometry.md`, `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user clarified the actual geometry mapping: setups `04` to `07` are all `purnanto`, setup `08` is `purnantov2`, and geometry naming must stay separate from inlet boundary-condition style.
- assumptions introduced/removed: removed the earlier mistaken assumption that split-inlet or no-brine-outlet branches were automatically `purnantov2`; introduced the corrected rule that inlet BC style does not determine geometry label.
- next action: for future setup reports, state geometry label and inlet BC package as separate fields instead of letting one imply the other.

## [2026-06-11] model-update | Sweep remaining geometry references for purnanto naming
- files created/updated: `../../Setup report/04-mixed-wet-half-actual-area.md`, `../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`, `../../Setup report/06-pure-phase-split-fixed-velocity.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `../../Setup report/08a-steam-outlet-extension-student-trial.md`, `wiki/model/inlet-regimes.md`, `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`, `wiki/progress/experiments.md`, `wiki/log.md`
- reason: user asked for a sweep so remaining project/setup references stop using ambiguous geometry wording where `purnanto` versus `purnantov2` now matters.
- assumptions introduced/removed: introduced the default interpretation that the current split-inlet / no-brine-outlet local geometry line is `purnantov2` unless a setup report explicitly overrides it; kept some local mesh exports marked as likely `purnantov2` rather than claiming certainty where the mesh provenance is still not fully audited.
- next action: if a specific local mesh or case file becomes important for comparison, audit it explicitly and record whether it is `purnanto` or `purnantov2` instead of relying on folder names.

## [2026-06-11] model-update | Define purnanto versus purnantov2 geometry naming
- files created/updated: `wiki/technical/v2-purnanto-spiral-inlet-geometry.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`, `../../Setup report/08a-steam-outlet-extension-student-trial.md`, `../../Setup report/order-dictionary.md`, `wiki/log.md`
- reason: user clarified that the project now has two related BOC separator geometries and wants them referred to consistently as `purnanto` and `purnantov2`.
- assumptions introduced/removed: introduced the project naming rule that `purnanto` means the closer paper-parity geometry with the steam-outlet boundary at the outlet entrance, while `purnantov2` means the later cleaned geometry with a downstream steam-outlet boundary plus local spiral-inlet and dish-head cleanup; did not claim that either label fully proves the unpublished original CAD detail.
- next action: when future setup reports are created, state explicitly whether they use `purnanto` or `purnantov2` instead of relying on informal memory.

## [2026-06-11] model-update | Rewrite setup 09 family into smaller DPM-only stages
- files created/updated: `../../Setup report/09-multiphase-separator-sensitivity-family.md`, `../../Setup report/09a-dpm-split-inlet-carryover.md`, `../../Setup report/09b-rsm-dpm-split-inlet-accuracy.md`, `../../Setup report/09c-dpm-ewf-wall-film-reentrainment.md`, `../../Setup report/order-dictionary.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/log.md`
- reason: user asked to rewrite the `09` setup family after agreeing that the old version made too many testing jumps between settings and no longer matched the project roadmap.
- assumptions introduced/removed: removed the old interpretation that family `09` should jump directly into `RSM-DPM` and `DPM + EWF`; introduced the rule that family `09` is now limited to smaller staged DPM escalation after setup `07`, with settings inherited dynamically from the latest accepted simpler branch rather than copied blindly from the original baseline.
- next action: create the later `10` family only when wall-fate, Eulerian wall film, or re-entrainment becomes the next justified uncertainty after the smaller `09` branches.

## [2026-06-11] model-update | Link setup-report system back to roadmap
- files created/updated: `../../Setup report/order-dictionary.md`, `../../Setup report/07-pure-phase-split-actual-area.md`, `wiki/log.md`
- reason: user asked to make the setup-report system aware that the project roadmap exists, because the roadmap had been forgotten and the active setup branch needed a durable backlink.
- assumptions introduced/removed: introduced the explicit cross-system rule that setup lineage should be read together with the project roadmap; no setup identity or ordering assumptions were changed.
- next action: when new setup branches are created from `07`, check the roadmap first so setup reports stay aligned with the active project path.

## [2026-06-11] workflow-update | Refresh AGENTS guides for current repo structure
- files created/updated: `../../AGENTS.md`, `../AGENTS.md`, `../../PyAnsys/AGENTS.md`, `../../CFD_wiki/AGENTS.md`, `../../CFD_wiki/wiki/log.md`, `wiki/log.md`
- reason: user asked to update the active `AGENTS.md` files so they reflect the current split between reusable CFD knowledge, project V&V sign-off, setup lineage, and executable automation.
- assumptions introduced/removed: clarified that `ResearchProject_wiki/wiki/vnv/` owns human-readable V&V records while `PyAnsys` owns machine-readable target and claim-gate logic; kept `Setup report/` separate as the setup-lineage authority.

## [2026-06-11] workflow-update | Add dedicated project V&V layer and repo tree map
- files created/updated: `AGENTS.md`, `wiki/index.md`, `wiki/model/validation.md`, `wiki/project/roadmap.md`, `wiki/vnv/index.md`, `wiki/vnv/policy.md`, `wiki/vnv/claim-classes.md`, `wiki/vnv/signoff-log.md`, `wiki/vnv/targets/index.md`, `wiki/vnv/verification/index.md`, `wiki/vnv/validation/index.md`, `../../PROJECT_TREE.md`, `wiki/log.md`
- reason: user asked for a cleaner place to store project-owned verification and validation reports without mixing them into setup-lineage records, and also asked for a simple top-level tree of the repository structure after the refactor.
- assumptions introduced/removed: kept `Setup report/` as a separate lineage system rather than moving it into `ResearchProject_wiki`; introduced `wiki/vnv/` as the project-owned layer for target records, verification reports, validation reports, and final human sign-off.
- next action: start the first concrete reports under `wiki/vnv/verification/` and `wiki/vnv/validation/` for setup `07`, then link the matching machine-readable target manifests from `PyAnsys`.

## [2026-06-11] model-update | Reset roadmap around setup 07 baseline path
- files created/updated: `wiki/project/roadmap.md`, `wiki/log.md`
- reason: user asked to replace the old brine-outlet and water-initialization roadmap with a new project sequence built from `07-pure-phase-split-actual-area.md`, while making it explicit that setup `07` is not yet verified or validated.
- assumptions introduced/removed: removed the old assumption that `FFF-2`, brine-outlet recovery, and water-pool initialization remain the main project path; introduced the user-specified scope decision that these are parked future-work branches unless extra time remains after the main setup `07` path is complete.
- next action: use the new roadmap to decide the setup `07` acceptance gate, then run mesh verification only after the baseline branch is numerically acceptable.

## [2026-06-10] model-update | Link project validation page to reusable CFD-side V&V workflow
- files created/updated: `wiki/model/validation.md`, `wiki/index.md`, `wiki/log.md`
- reason: user asked for a more robust verification/validation method grounded in the existing CFD literature pages, so the project validation page now points to the reusable CFD-side workflow instead of trying to duplicate that method locally.
- assumptions introduced/removed: added the rule that the CFD wiki holds the reusable separator V&V method authority, while the research wiki should only track which anchor and acceptance gate are active for the current project branch.

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
## [2026-07-17] model-update | Define future setup 10 wall-film escalation family
- files created/updated: `../../Setups/future/10-wall-film-reentrainment-and-dpm-interaction-plan.md`, `../../Setups/future/index.md`, `../../Setups/order-dictionary.md`, `wiki/project/roadmap.md`, `wiki/log.md`
- reason: user requested a forward plan covering inlet-velocity sensitivity, Eulerian wall film, re-entrainment, custom DPM wall-impact trajectories, and non-water injection materials.
- what changed since last update: recorded that `09c` is currently two-way DPM coupling only; defined a future `10` family that separates EWF deposition/drainage, re-entrainment/impingement, and custom DPM/material sensitivity rather than combining them.
- assumptions introduced/removed: retained fixed-enthalpy inlet loading as the immediate `08c` question; treated air-water EWF literature as a method-pattern source with geothermal transfer uncertainty; required active material-property or species/energy changes before calling a new injection material physically meaningful.
- current status: `08c` remains the immediate carrier-loading experiment, `09c` remains the active DPM-coupling comparison, and setup `10` is future/planned.
- blockers: no initialized/iterated `08c` endpoint results, no completed `09c` two-way comparison, no calibrated geothermal wall-film or re-entrainment closure.
- next action: run the three-point `08c` carrier matrix, select the stable reference point, then finish `09c` before building `10a`.
## [2026-07-17] model-update | Split setup 10 into independent runs and reserve setup 11 for combinations
- files created/updated: `../../Setups/future/10-wall-film-reentrainment-and-dpm-interaction-plan.md`, `../../Setups/future/11-combined-wallfilm-dpm-plan.md`, `../../Setups/future/index.md`, `../../Setups/order-dictionary.md`, `wiki/project/roadmap.md`, `wiki/log.md`
- reason: user needs long-running wall-film and DPM cases ready for execution tomorrow, even if parent interpretation gates are not yet closed.
- what changed since last update: defined `10a` EWF-only deposition/drainage, `10b` DPM wall-return sensitivity without EWF, and `10c` custom trajectory/material sensitivity without EWF or re-entrainment; reserved `11a` for EWF plus selected re-entrainment and `11b` for the full selected combination.
- assumptions introduced/removed: separated execution readiness from report-quality interpretation; diagnostic `10` runs may proceed when the parent case and changed model read back, while combined `11` cases require bounded film inventory and conserved returned mass.
- current status: future setup families `10` and `11` are now concretely defined; active branches remain `08c` and `09c`.
- blockers: `08c` and `09c` results are still pending; EWF wall-zone selection, timestep, and re-entrainment closure still require Fluent-side confirmation.
- next action: prepare the parent `09c` case and launch independent `10a`, `10b`, and `10c` cases with the same loading and injection payload.

## [2026-08-16] model-update | Complete 02c positive-backpressure D–G post-processing

- files created/updated: `../../Setups/reports/02c/results.md`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`, plus the generated D–G carrier/residual and EWF/DPM diagnostic bundles under `../../../PyAnsys/output/`.
- purpose: verify and interpret the queued 02c D/E/F/G endpoints and reformat the results report so pressure points can be compared directly.
- what changed since last update: all four paired remote 500-iteration endpoints were independently reloaded and post-processed. The report now has a sweep definition, primary phase-routing table, numerical-health table, compact D–G evidence blocks, and an artifact index.
- measured direction: from D to G, vapour brine-outlet flow fell `38.127` → `9.211 kg/s` (`46.70%` → `11.28%` of vapour inlet), while vapour steam-outlet flow rose `44.084` → `71.647 kg/s` (`54.00%` → `87.76%`).
- evidence boundary: continuity remained `8.24e-2` to `1.12e-1`; no case is converged. D is a promising bracket-adjacent directional candidate, while E–G have liquid brine outflow above inlet and remain inventory-draining / unresolved. No pressure-selection or separator-efficiency claim is made.
- inherited diagnostics: EWF audit reports disabled/no active film wall; six DPM transcripts completed per case, but all injections originate at `steam-outlet`, so DPM is excluded from primary pressure interpretation.
- next immediate action: instrument total continuous-liquid inventory, lower-vessel/pipe-entry pressure diagnostics, and visual phase/velocity evidence before continuing a common-window pressure screen.

## [2026-08-16] model-update | Launch coarse above-inlet 02c pressure sweep

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/log.md`, `../../../PyAnsys/scripts/setup/build_02c_positive_backpressure_cases.py`, `../../../PyAnsys/scripts/setup/generate_02c_positive_backpressure_queue.py`, `../../../PyAnsys/scripts/setup/run_02c_above_inlet_20_to_50.py`, and `../../../PyAnsys/src/pyansys_fluent/positive_backpressure_queue.py`.
- purpose: test the user-proposed possibility that the brine outlet may require pressure above the nominal inlet reference because of lower-vessel hydrostatic and swirl pressure.
- what changed: added H20–H50 at `1.160`–`1.190 MPa`, representing `+20` to `+50 kPa` above the nominal `1.140 MPa` inlet reference in `+5 kPa` steps; steam outlet remains `1.120 MPa`.
- execution state: all seven case-only children were built/reload-verified from the frozen 02c-B pre-initialization parent. Fluent accepted the native H20 → H25 → H30 → H35 → H40 → H45 → H50 queue; H20 is active and endpoint completion is unverified.
- early diagnostic: H20 immediately shows reverse flow on both pressure outlets and turbulent-viscosity limiting. This is retained as a diagnostic signal; no case is marked failed until the queued endpoint or a defined hard-stop condition is recorded.
- next immediate action: verify paired endpoints after Fluent returns control, then post-process fluxes/residuals/reverse-flow evidence and liquid inventory before drawing any upper-pressure conclusion.

## [2026-08-16] model-update | Prepare blocked 02c I20–I160 coarse extension

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`, `../../../PyAnsys/scripts/setup/build_02c_positive_backpressure_cases.py`, `../../../PyAnsys/scripts/setup/generate_02c_positive_backpressure_queue.py`, and `../../../PyAnsys/output/02c-above-inlet-20-to-130-coarse-queue-20260816T014600Z.jou`.
- purpose: prepare the user-requested broad brine-outlet pressure screen from `1.160` to `1.300 MPa` in `20 kPa` steps above the nominal inlet reference, with an independently parent-derived case-only child per point and a dormant Fluent-native journal.
- what changed since last update: added distinct I20–I160 case identifiers and `coarse130` artifact suffixes, enhanced the builder to compare every audited boundary/model value after child reload except the requested brine pressure, and rendered the eight-case native journal without submitting it.
- assumptions introduced/removed: preserves the frozen 02c-B parent, `1.120 MPa` steam outlet, velocity-inlet contract, unprimed Hybrid Initialization procedure, and `500` native-iteration screen; no pressure-selection, drainage-limit, or convergence claim is introduced.
- current status: no I child was created because the accessible idle Fluent session could not see the required frozen parent; no initialization, iteration, data write, or journal execution occurred.
- blockers: parent availability from an idle Fluent session is required before this identical-settings case-only build can proceed.
- next immediate action: reconnect to an idle Fluent session with the documented frozen parent visible, build/reload-verify all eight I children, and keep the generated journal unsubmitted until separately authorized.

## [2026-08-16] model-update | Verify Student 02c I20/I40/I60 native smoke queue

- files created/updated: `../../Setups/active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md`, `../../Setups/reports/02c/future-runs.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/log.md`, and `../../../PyAnsys/scripts/setup/run_02c_student_i_smoke_test.py`.
- purpose: confirm the first three coarse I-series cases can run independently through Fluent-native initialization/iteration/write sequencing before any later server-2 production work.
- what changed since last update: Student built I20/I40/I60 from the same saved Student Mixture pre-initialization surrogate and ran the submitted journal for 50 iterations per member. All three paired endpoints were visible and explicitly reopened; each retained the requested brine pressure, `1.120 MPa` steam outlet, Mixture/RNG k-epsilon, and 50-point residual history ending at iteration 50.
- evidence boundary: this is Student mesh-derived surrogate evidence only. Reverse-flow and turbulent-viscosity-limit diagnostics occurred; no member is called converged, scientifically comparable to 02c, or suitable for server-2 pressure interpretation.
- next immediate action: do not promote or extend the Student endpoints. Recover the exact frozen parent on server 2, then rebuild the production I matrix independently from that parent.
