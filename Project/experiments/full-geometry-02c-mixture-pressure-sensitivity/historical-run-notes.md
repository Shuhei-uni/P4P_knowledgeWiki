> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run 02c-STUDENT-I20-I60-SMOKE-2026-08-16
- Run ID: `02c-STUDENT-I20-I60-SMOKE-2026-08-16`
- Date: 2026-08-16
- Objective: verify that the revised first three coarse I-series pressure cases can be independently built, Hybrid Initialized, and executed through a native Fluent 50-iteration journal.
- Geometry and mesh: Student-only mesh-derived surrogate; reload reported `661,558` cells and `1,648,866` nodes. It is not certified identical to the production 02c/server-2 mesh.
- Physics model: steady Mixture with RNG k-epsilon after each endpoint reload; the source is a saved Student 02c-C-like pre-initialization surrogate, not frozen 02c-B.
- Boundary and initial conditions: only brine gauge pressure varied: I20 `1.160 MPa`, I40 `1.180 MPa`, I60 `1.200 MPa`; steam outlet read back at `1.120 MPa` for all endpoints.
- Iteration budget and verification: three independent native `50`-iteration blocks. Every paired `.cas.h5`/`.dat.h5` endpoint was visible, reopened, and showed 50 residual-history points ending at iteration 50.
- Outcome: `Execution-integrity smoke passed; not converged / not comparable`.
- Diagnostics: reverse flow at pressure outlets and turbulent-viscosity limiting were observed; no physical pressure-ranking or convergence conclusion is permitted.
- Next action: retain this as a Student automation proof only. Rebuild the production I-series from a verified server-2 frozen parent when that parent is available.

### Run 02c-I20-I160-PREPARATION-2026-08-16
- Run ID: `02c-I20-I160-PREPARATION-2026-08-16`
- Date: 2026-08-16
- Objective: Prepare a separate, broader 02c brine-outlet pressure screen at `1.160 / 1.180 / 1.200 / 1.220 / 1.240 / 1.260 / 1.280 / 1.300 MPa`, while preserving all verified 02c parent settings and leaving the native queue unstarted.
- Geometry: intended inherited split-velocity-inlet separator with the physical tangential brine pipe; no mesh or zone change was attempted.
- Mesh: intended frozen-parent mesh; not loaded because the required parent was unavailable from the accessible idle Fluent session.
- Physics model: intended inherited steady pressure-based Mixture / RNG k-epsilon configuration with gravity on and Energy/DPM/EWF state preserved; no live model change occurred.
- Solver settings: the local journal is configured only for a later native sequence of independent parent-derived cases: Hybrid Initialization, `500` steady iterations, explicit paired endpoint write, then advance. The journal was not submitted.
- Boundary and initial conditions: intended sole delta is brine-outlet mixture-phase gauge pressure; steam outlet remains `1.120 MPa`, both velocity inlets remain `27.118 m/s` with `1.140 MPa` reference/initial gauge pressure, and no liquid patch is permitted.
- Iteration or timestep budget: planned only: `8 × 500` steady iterations; completed flow iterations `0`.
- Convergence indicators: N/A — no I case was loaded, initialized, or solved.
- Outcome: `Blocked before case-only build`; the builder refused to mutate because the frozen parent was not visible to the accessible idle session.
- Hypothesized cause if not converged: not applicable; this is a remote parent/session availability issue, not a numerical outcome.
- Next action: use an idle Fluent session that can see the documented frozen parent, build/reload-verify each I child, then await explicit authorization before submitting the journal.

### Run 02c-C-ITER500-2026-08-12
- Run ID: `02c-C-ITER500-2026-08-12`
- Date: 2026-08-12
- Objective: Screen the unprimed Mixture-model tangential brine outlet at `1.125 MPa` while holding the steam outlet at `1.120 MPa`.
- Geometry: split velocity-inlet separator geometry with named `brine-outlet` and `steam-outlet` pressure-outlet faces; full tangential brine-pipe geometry retained.
- Controls: frozen Case B pre-initialization parent explicitly loaded; only brine-outlet pressure changed to `1.125 MPa`; liquid backflow volume fraction `1.0`; Hybrid Initialization without liquid patch.
- Solver settings: native Fluent TUI `solve/initialize/hyb-initialization`, followed by `solve/iterate 500`.
- Artifact: verified paired checkpoint `02c-C-brine-p1125kpa-unprimed-iter500-20260812T055550Z.cas.h5/.dat.h5`.
- Post-processing: direct retained-session carrier/residual extraction, audit, and complete six-injection DPM sweep completed. EWF was inactive/no film wall; carrier coupling was off; all inherited DPM releases were on `steam-outlet` and do not represent brine-drainage evidence.
- Outcome: `Partially Converged / early screening only`.
- Carrier result: liquid inlet `116.847094 kg/s`; liquid brine outlet `136.604543 kg/s`; liquid steam outlet `8.928871e-6 kg/s`; vapour inlet `81.639506 kg/s`; vapour brine outlet `26.743944 kg/s`; vapour steam outlet `54.827687 kg/s` (outlets expressed as positive outward magnitudes).
- Derived screen: liquid closure error `16.91%`; apparent liquid brine recovery `116.91%` (not physically valid due to the open liquid balance); vapour wrong-outlet fraction `32.76%`; vapour phase closure error `0.083%`.
- Convergence caution: final continuity `1.194315e-1` after a `1.120839e-1` minimum; velocity residuals finished at `5.868121e-5`, `5.996074e-5`, and `6.325916e-5` in x/y/z. No pressure-ranking conclusion is recorded.
- Next action: define common physical/stability monitors and continue or rerun A/B/C to the same stable window before comparing pressure points. See [02c results](results.md).

### Run 02c-A-ITER649-2026-08-12
- Run ID: `02c-A-ITER649-2026-08-12`
- Date: 2026-08-12
- Objective: Screen the unprimed Mixture-model tangential brine outlet at the lower `1.115 MPa` brine pressure while holding the steam outlet at `1.120 MPa`.
- Geometry: split velocity-inlet separator geometry with named `brine-outlet` and `steam-outlet` pressure-outlet faces; full tangential brine-pipe geometry retained.
- Controls: Case B pre-initialization parent explicitly loaded; both inlets retained as velocity inlets at `27.118 m/s`; inlet gauge pressure `1.140 MPa`; liquid-inlet phase-2 volume fraction `1`; steam-inlet phase-2 volume fraction `0`; no liquid patch after Hybrid Initialization.
- Execution: native solve passed the requested 500-iteration milestone. A recovery continuation overlapped the active native solve and was allowed to finish, producing a 649-iteration endpoint rather than interrupting the solver.
- Artifact: verified paired checkpoint `02c-A-brine-p1115kpa-unprimed-iter649-20260812T051900Z.cas.h5/.dat.h5` in the remote brine-outlet results directory.
- Post-processing: explicit reload of the verified pair produced carrier flux/residual artifacts, a model audit, and a complete six-injection DPM bundle. EWF was inactive/no film wall; DPM coupling was off. All inherited DPM releases were on `steam-outlet`, so their fates are not brine-drainage evidence.
- Outcome: `Partially Converged / early screening only`.
- Carrier result: liquid inlet `116.847094 kg/s`; liquid brine outlet `45.799051 kg/s`; liquid steam outlet `2.008474e-5 kg/s`; vapour inlet `81.639506 kg/s`; vapour brine outlet `49.294436 kg/s`; vapour steam outlet `32.793685 kg/s` (outlets expressed as positive outward magnitudes).
- Derived screen: liquid closure error `60.80%`; liquid brine-recovery `39.20%`; vapour wrong-outlet fraction `60.38%`; vapour phase closure error `0.55%`.
- Convergence caution: final continuity `1.265345e-1` after a minimum `7.966281e-2`; velocity residuals finished at `4.771068e-5`, `6.136807e-5`, and `5.589449e-5` in x/y/z. Persistent steam-outlet reverse flow and occasional turbulent-viscosity limiting were seen during execution. No pressure-ranking conclusion is recorded.
- Next action: build and analyse Case C from the same frozen parent with a common convergence/stopping gate before comparing the pressure points. See [02c results](results.md).

### Run 02c-B-ITER500-2026-08-12
- Run ID: `02c-B-ITER500-2026-08-12`
- Date: 2026-08-12
- Objective: Screen the unprimed Mixture-model tangential brine outlet at the matching `1.120 MPa` brine/steam pressure-outlet condition.
- Geometry: split velocity-inlet separator geometry with named `brine-outlet` and `steam-outlet` pressure-outlet faces; full tangential brine-pipe geometry retained.
- Mesh: `1,770,229` nodes and `620,431` mixed cells, as read while the saved checkpoint was reloaded.
- Physics model: steady pressure-based Mixture model; RNG k-epsilon; gravity on; Energy off; EWF inactive. Six inherited DPM injections were active with coupling off.
- Solver settings: Hybrid Initialization without phase patch; 500 steady iterations.
- Boundary and initial conditions: both split velocity inlets at `27.118 m/s` and `1.140 MPa` initial gauge pressure; liquid-inlet liquid volume fraction `1.0`; steam-inlet liquid volume fraction `0.0`; steam and brine outlets each `1.120 MPa`; brine liquid backflow fraction `1.0`, steam liquid backflow fraction `0.0`.
- Iteration budget: completed `500`.
- Convergence monitors: continuity `1.239373e-1`; x/y/z velocity residuals `2.575407e-5 / 2.688511e-5 / 2.499069e-5`; k `1.167529e-3`; epsilon `5.747842e-3`; liquid volume fraction `1.795970e-3`.
- Outcome: `Partially Converged / early screening only`.
- Flux result: liquid inlet `116.847094 kg/s`; liquid brine outlet `6.921014 kg/s`; liquid steam outlet `7.779685e-7 kg/s`; vapour inlet `81.639506 kg/s`; vapour brine outlet `42.547417 kg/s`; vapour steam outlet `39.823439 kg/s` (outlets expressed as positive outward magnitudes).
- Hypothesized cause (if non-converged): the unprimed field has not established a stable liquid-drainage/vapour-core split by iteration 500; brine pressure sensitivity remains an unresolved test, not a diagnosed mechanism.
- Next action: build Case A from the frozen pre-initialization parent at `1.115 MPa` brine pressure and run the same 500-iteration screen before making a pressure-ranking decision. See [02c results](results.md).

### Run 02c-POSITIVE-BACKPRESSURE-NATIVE-QUEUE-2026-08-14
- Run ID: `02c-POSITIVE-BACKPRESSURE-NATIVE-QUEUE-2026-08-14`
- Date: 2026-08-14
- Objective: Execute the prepared D/E/F/G positive-brine-backpressure cases unattended through one already-running Fluent instance, with an independent parent-derived field for each point.
- Geometry: inherited 02c split velocity-inlet separator and physical tangential brine-pipe geometry; each queue member loads its own case-only child.
- Mesh: inherited frozen-parent `620,431` mixed cells and `1,770,229` nodes; no mesh change is authorized in the queue.
- Physics model: inherited steady pressure-based Mixture / RNG k-epsilon model, gravity on, Energy off; no model setting changes between queue points.
- Solver settings: Fluent-native journal applies Hybrid Initialization then `500` steady iterations per case. Python neither loops iteration calls nor owns checkpoint timing.
- Boundary and initial conditions: brine pressure is already frozen in each child: D `1.1225 MPa`, E `1.1275 MPa`, F `1.1300 MPa`, G `1.1350 MPa`; steam outlet remains `1.120 MPa`. No liquid patch is applied.
- Iteration or timestep budget: `4 × 500` steady iterations, sequentially.
- Convergence indicators: completion unverified at this record time. The journal started Case D's load, but two bounded read-only reconnect attempts could reach TCP without completing a busy Fluent gRPC handoff.
- Outcome: `Launched / completion unverified`.
- Hypothesized cause if not converged: not applicable until per-case endpoint evidence is retrieved. Existing case children do not yet supply the required continuous-liquid-inventory history.
- Next action: wait for Fluent to return control; verify each expected remote `.cas.h5` / `.dat.h5` endpoint, then post-process each case independently and update this record with actual residual/phase-flux evidence.

### Run 02c-POSITIVE-BACKPRESSURE-POSTPROCESS-2026-08-16

- Run ID: `02c-POSITIVE-BACKPRESSURE-POSTPROCESS-2026-08-16`
- Date: 2026-08-16
- Objective: Explicitly reload and compare the verified D/E/F/G 500-iteration positive-brine-backpressure endpoints using the common carrier-flux, residual, EWF/DPM-audit, and six-injection DPM transcript workflow.
- Geometry: inherited 02c split velocity-inlet separator with the physical tangential brine-pipe geometry; no mesh or zone changes between cases.
- Mesh: `1,770,229` nodes and `620,431` mixed cells, confirmed during endpoint reloads.
- Physics model assumptions: steady pressure-based Mixture carrier; RNG k-epsilon; gravity on; Energy off; EWF disabled; six inherited inert DPM surface injections with carrier coupling off; no UDF body-force or scalar-update match.
- Solver settings: endpoints were produced by the prior Fluent-native queue after Hybrid Initialization and 500 steady iterations per independent pre-initialization child. This post-processing pass made no carrier iterations or setup mutations.
- Boundary/initial conditions: steam outlet fixed at `1.120 MPa`; brine outlet D/E/F/G at `1.1225 / 1.1275 / 1.1300 / 1.1350 MPa`; split velocity inlets and backflow states inherited unchanged; no liquid patch.
- Iteration or timestep budget: D/E/F/G each `500` steady iterations; six DPM injections tracked per endpoint in diameter-ascending order.
- Convergence indicators: final continuity D/E/F/G = `1.021e-1 / 8.959e-2 / 1.117e-1 / 8.243e-2`; minima = `9.563e-2 / 8.934e-2 / 1.116e-1 / 8.241e-2`. None meets the configured `1e-4` residual criterion, and no common stable physical-monitor window or liquid-inventory history exists.
- Outcome: `Partially Converged / directional early screening only`. Vapour brine-outlet flow decreases D→G from `38.127` to `9.211 kg/s` (`46.70%` to `11.28%` of vapour inlet), while vapour steam-outlet flow increases from `44.084` to `71.647 kg/s` (`54.00%` to `87.76%`). D liquid brine flow is `25.966 kg/s`; E/F/G liquid brine outflows are `258.323 / 440.922 / 228.106 kg/s`, all above the `116.847 kg/s` liquid inlet.
- Hypothesized cause if not converged: the positive backpressure shifts vapour routing as expected, but the unprimed liquid field remains inventory-dominated/open. E–G liquid outflow excess may reflect transient drainage of initial liquid inventory; without `M_l(N)` it cannot be classified as a hydraulic drainage restriction or sustained recovery.
- Evidence: [02c comparison report](results.md), D flux (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-flux-check.json`; not migrated), E flux (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-flux-check.json`; not migrated), F flux (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-flux-check.json`; not migrated), G flux (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-flux-check.json`; not migrated), and the corresponding residual/audit/DPM links in the report.
- Next action: add total continuous-liquid inventory, lower-vessel/pipe-entry pressure diagnostics, and common visual evidence; then continue only D-adjacent or otherwise bracket-selected points from the frozen parent under a common stability gate. Preserve E–G as unresolved diagnostic evidence.

### Run 02c-POSITIVE-BACKPRESSURE-BUILD-2026-08-12
- Run ID: `02c-POSITIVE-BACKPRESSURE-BUILD-2026-08-12`
- Date: 2026-08-12
- Objective: Prepare independent positive-brine-backpressure children to bracket the promising Case C vapour-routing direction without changing the unprimed 02c carrier setup.
- Geometry: the frozen split velocity-inlet separator with the physical lower tangential brine pipe; `liquid-inlet`, `steam-inlet`, `brine-outlet`, and `steam-outlet` were retained.
- Mesh: inherited frozen parent mesh, `1,770,229` nodes and `620,431` mixed cells; no mesh operation was performed.
- Physics model: inherited steady pressure-based Mixture / RNG k-epsilon carrier model with gravity on and Energy off; no model activation or material change was made.
- Solver settings: case-only preparation; no initialization, data load, iteration, or checkpoint data write was issued. Fluent-native autosave and run controls remain required for the later screens.
- Boundary and initial conditions: steam outlet remains `1,120,000 Pa` gauge. Only brine-outlet mixture-phase gauge pressure was changed, independently from the frozen parent, to D `1,122,500 Pa`, E `1,127,500 Pa`, F `1,130,000 Pa`, and G `1,135,000 Pa`; the live Fluent 2025 R2 pressure path was inspected and each value read back before saving.
- Iteration or timestep budget: `0` completed flow iterations in this preparation entry; each child is assigned a future Fluent-native `500`-iteration directional screen.
- Convergence indicators: not applicable to case-only artifacts.
- Outcome: `Case-only build verified / directional-screen preparation`.
- Hypothesized cause if not converged: not applicable. The target uncertainty is physical interpretation of liquid inventory after Hybrid Initialization, especially whether Case C-style high liquid brine flow settles or depletes inventory.
- Next action: independently Hybrid Initialize each child without a liquid patch; use native autosave and collect outlet phase flows plus continuous-liquid inventory across the common screen. See [02c future runs](future-runs.md).

### Run 02c-ABOVE-INLET-COARSE-QUEUE-2026-08-16
- Run ID: `02c-ABOVE-INLET-COARSE-QUEUE-2026-08-16`
- Date: 2026-08-16
- Objective: Run a broad pressure-only screen at `+20` to `+50 kPa` above the nominal `1.140 MPa` inlet reference in `+5 kPa` increments to identify the rough upper-pressure response before finer tuning.
- Geometry: inherited 02c split velocity-inlet separator with physical tangential lower brine pipe; each child was built from the same frozen 02c-B pre-initialization parent.
- Mesh: inherited `1,770,229` nodes and `620,431` mixed cells; no mesh changes.
- Physics model assumptions: steady pressure-based Mixture, RNG k-epsilon, gravity on, Energy off; DPM/EWF and all parent controls preserved.
- Solver settings: Fluent-native journal owns Hybrid Initialization, 500 steady iterations, paired case/data write, and sequential advancement. Python prepared/submitted the journal and does not loop iterations.
- Boundary and initial conditions: steam outlet fixed at `1.120 MPa`; H20/H25/H30/H35/H40/H45/H50 brine outlets at `1.160 / 1.165 / 1.170 / 1.175 / 1.180 / 1.185 / 1.190 MPa`; both inlets remain velocity inlets with nominal `1.140 MPa` reference/initial gauge value.
- Iteration budget: seven independent 500-iteration steady screens, sequential queue.
- Convergence monitors: not yet available for completed endpoints. H20 is active; its early transcript shows reverse flow on both pressure outlets and turbulent-viscosity limiting.
- Outcome: `Running / completion unverified` at record time; no pressure conclusion is drawn from the early H20 iterations.
- Hypothesized cause if not converged: above-inlet brine backpressure may be approaching or exceeding the local hydraulic pressure needed for liquid discharge, causing reverse flow, liquid accumulation, or an unstable mixed field. This remains a hypothesis until endpoint fluxes and liquid-inventory evidence are captured.
- Evidence: [02c future-run queue record](future-runs.md), H20–H50 build manifest (historical machine artifact path: `../../../PyAnsys/output/02c-above-inlet-20-to-50-build-20260816T002025Z.json`; not migrated), and local native journal (historical machine artifact path: `../../../PyAnsys/output/02c-above-inlet-20-to-50-queue-20260816T003500Z.jou`; not migrated).
- Next action: allow Fluent to complete or stop safely if unavailable; verify every paired remote endpoint before post-processing. Interpret the broad sweep only with outlet phase fluxes, reverse-flow diagnostics, residuals, and total liquid-inventory history.

### Run 02c-STUDENT-H1140-2026-08-16
- Run ID: `02c-STUDENT-H1140-2026-08-16`
- Date: 2026-08-16.
- Objective: Execute the user-requested single current 02c-H upper-pressure point at `1.140 MPa` brine-outlet gauge pressure for a native `500`-iteration diagnostic screen after cancelling the former H/I pressure sweeps.
- Geometry variant: Student mesh-derived 02c surrogate from `02c-C-brine-p1125kpa-unprimed-preinit-20260815T231711Z.cas.h5`; not certified as exact server-2/production 02c mesh parity.
- Mesh stats: `661,558` mixed cells, `1,648,866` nodes, `2,841,025` faces, six face zones; reload diagnostic included turbulent-viscosity limiting in approximately `27,030` cells.
- Physics model assumptions: pressure-based steady Mixture; phase-1 water vapour and phase-2 water liquid; RNG k-epsilon; gravity inherited; Energy off; DPM/EWF inactive in the Student endpoint.
- Solver settings: Fluent-native Hybrid Initialization; inherited solver/discretization/control state; one native `/solve/iterate 500` command; no Python iteration loop and no liquid-pool patch.
- Boundary/initial conditions: split velocity inlets at `27.118 m/s` with `1.140 MPa` initial gauge reference; steam outlet pressure outlet `1.120 MPa`; brine outlet pressure outlet `1.140 MPa`; liquid brine backflow volume fraction `1.0`.
- Iteration or timestep budget: `500` steady iterations; exact paired case/data endpoint written after iteration 500.
- Convergence indicators: 500 residual points; final continuity `2.288839e-1`, minimum continuity `1.332997e-1` at iteration 37; final x/y/z velocity residuals `1.079818e-3 / 1.212693e-3 / 1.117975e-3`; persistent reverse flow on both pressure outlets and viscosity limiting.
- Outcome: `Unstable / Indeterminate; completed requested screen but not converged`.
- Hypothesized cause if not converged: the `1.140 MPa` brine pressure is associated with strong reverse liquid flow at the brine boundary in this Student surrogate, while the simplified geometry has no modelled lower-liquid outlet; the resulting field is open and numerically unhealthy. This is a hypothesis, not a validated pressure-limit claim.
- Evidence: 02c H results (retired source; details retained in this Project packet), build manifest (historical machine artifact path: `../../../PyAnsys/output/02c-student-h1140-build-20260816T091723Z.json`; not migrated), flux extraction (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-flux-check.json`; not migrated), residual extraction (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-residual-check.json`; not migrated), and residual plot (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-residual-check.png`; not migrated).
- Next action: retain H as diagnostic evidence only; do not revive the cancelled H20–H50 or I20–I160 sweeps without a new user scope decision and a mesh/lineage decision. Interpretation status remains pending user direction.
