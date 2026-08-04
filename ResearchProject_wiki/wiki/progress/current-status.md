# Current Status

## Split-Inlet Carrier Mesh Study Preflight (2026-07-29)
- Status: `Planned / blocked at preflight`.
- Authoritative actual case record: `C:\Users\syok443\Documents\Setup07extractor\FFF.1-2.cas.h5` with `FFF.1-2-02541.dat.h5`, archived under `../../../PyAnsys/cases/actual_setup_archives/07-pure-phase-split-actual-area-live-fff-1-2/`.
- Selected branch: setup `07a`, a carrier-only mesh-convergence child of the setup `07` split-inlet model. Setup `08c` remains the one-mixed-inlet replication branch and is not the split-inlet mesh-study baseline.
- Reference condition: `1600 kJ/kg`, liquid `116.92 kg/s`, steam `80.69 kg/s`; setup-07 split velocity is `27.118 m/s`.
- Frozen core physics: steady pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon, gravity on, Energy off. DPM and EWF are excluded from the primary study.
- Preflight conflict: the actual archive contains active DPM, `Coupled`, and first-order schemes, while intended setup `07` specifies carrier-first, `SIMPLE`, and second-order/`QUICK`. A single numerics authority must be qualified and read back before all mesh runs.
- Mesh status: no systematic coarse/medium/fine mesh binaries are present locally. Historical `mesh-trial1` metadata describe only diagnostic exports with inconsistent zone preservation.
- Remote status: the read-only connection check to `10.104.145.85:54904` timed out on `2026-07-29`; active processor count remains unverified (historical intent was 15).
- Study definition: `../../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`.
- Next action: restore the Fluent/VPN path, inspect the authoritative case and processor count, verify outer-liquid/inner-steam geometry, then create or locate the systematic mesh ladder before any long solve.

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
