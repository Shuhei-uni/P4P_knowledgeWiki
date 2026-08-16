# Experiment Log

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

### Run VOF-IC0-IC1-IC2-Y030-COARSE-STABILITY-2026-08-14
- Run ID: `VOF-IC0-IC1-IC2-Y030-COARSE-STABILITY-2026-08-14`
- Date: 2026-08-14
- Objective: Screen the three user-selected initialized VOF fields for immediate floating-point failure under a deliberately conservative common timestep.
- Geometry: existing coarse separator mesh; IC0 is unpatched, IC1 retains the approved five-cell `brine-outlet` distance-register pipe patch, and IC2 retains the approved full-width `y <= +0.30 m` pool plus IC1 patch.
- Mesh: `275,448` mixed cells and `815,716` nodes; one fluid zone; previously observed minimum orthogonal quality `0.250006` and maximum aspect ratio `65.1632`. No new local size survey.
- Physics model: explicit/sharp VOF with vapour primary and liquid secondary, RNG k-epsilon, gravity `[0, -9.81, 0] m/s²`; Energy, DPM, and EWF off.
- Solver settings: Fluent-native queue. IC0 was Hybrid Initialized in the journal; IC1/IC2 loaded their paired initialized fields. Fixed `1.0e-5 s` was set after every case/data load, with two native 1,000-iteration blocks and explicit paired case/data writes after each block.
- Boundary and initial conditions: unchanged VOF baseline: both inlets `27.118 m/s`, both pressure outlets `1.120 MPa` gauge, and the approved patch fields above.
- Iteration or timestep budget: requested `2,000` transient steps per case in two nominal `1,000`-step blocks; actual early-stop terminal counts were IC0 `69`, IC1 `69`, and IC2 Y030 `67`.
- Convergence indicators: each transcript stated `solution is converged` once residual continuity crossed the enabled `1e-3` criterion. Reverse-flow notices persisted at pressure outlets; required physical phase-flow, inventory, and pressure monitors were not defined.
- Outcome: `Invalid as a 2,000-step screen / early convergence stop`; its nominal filenames are not iteration-count evidence.
- Hypothesized cause if not converged: residual convergence checking was left enabled after the data reads. The earlier `1.0 s` IC1/IC2 queue outputs are separately excluded because those data reads also reset the intended timestep.
- Next action: the fresh convergence-disabled 2,000-step native screen is running from readback-verified restart sources; verify each final transcript reaches flow time `0.0200 s` before any interpretation.

### Run VOF-IC1-IC2-FINE-QUEUE-PREP-2026-08-14
- Run ID: `VOF-IC1-IC2-FINE-QUEUE-PREP-2026-08-14`
- Date: 2026-08-14
- Objective: Create the fine-mesh brine-pipe and plane-pool initialization artifacts, plus a dormant Fluent-native sequential 500/1000-iteration queue; do not start calculations.
- Geometry: fine mesh with one fluid zone and domain extents `x = [-2.068679, 1.066749] m`, `y = [-1.484584, 6.994597] m`, `z = [-1.461048, 1.066830] m`. IC1 uses five cell-distance layers from `brine-outlet`; IC2 uses full-width global-coordinate pool planes at `y_cut = 0.00/0.15/0.30/0.45/0.60 m`.
- Mesh: `620,431` cells, `1,770,229` nodes; no mesh modification.
- Physics model: inherited explicit/sharp VOF, vapour primary/liquid secondary, RNG k-epsilon, gravity `[0, -9.81, 0] m/s²`, Energy/DPM/EWF off.
- Solver settings: IC1 and each IC2 field was Hybrid Initialized then patched and saved as paired case/data input. The dormant journal will use two native `500`-iteration blocks per job with explicit paired saves after each block; it has not been submitted to Fluent.
- Boundary and initial conditions: inherited IC0 BC contract. IC1 phase-2 `mp = 1.0` uses the approved five-cell brine-outlet register. Every IC2 case loads the IC1 field and adds phase-2 `mp = 1.0` below its independent global `y_cut` plane.
- Iteration or timestep budget: planned only: seven jobs × `1,000` iterations, with checkpoints at `500` and `1,000`; completed flow iterations `0`.
- Convergence indicators: N/A — all inputs and journal are prepared but unstarted.
- Outcome: `Queue prepared / not started`.
- Hypothesized cause if not converged: not applicable. The main readiness risk remains unqualified transient timestep and unconfigured monitor/averaging package.
- Next action: define/review timestep and monitor evidence, then obtain explicit authorization before reading the remote journal.

### Run VOF-IC2-Y000-PATCH-PLATFORM-2026-08-14
- Run ID: `VOF-IC2-Y000-PATCH-PLATFORM-2026-08-14`
- Date: 2026-08-14
- Objective: Add the `y = 0` global-coordinate lower-pool initialization as the lowest bracket in the IC2 sensitivity family.
- Geometry: one combined fluid zone. `vof_ic2_pool_below_y_0p00m` is an inside-hexahedron over the full horizontal mesh extent and from `y = -1.484584 m` to `y = +0.000000 m`.
- Mesh: `275,448` mixed cells; `815,716` nodes after case write/read. The register marks `33,200` cells; minimum orthogonal quality `0.250006`; maximum aspect ratio `65.1632`.
- Physics model: inherited explicit/sharp VOF; primary `water-vapor`, secondary `water-liquid`; RNG k-epsilon; gravity `[0, -9.81, 0] m/s²`; operating pressure `0 Pa`; energy/DPM/EWF off.
- Solver settings: read the saved IC1 pipe-patch case/data, created the Y000 register, patched phase-2 `mp = 1.0`, and saved a separate case/data endpoint. No timestep, coupling/URF change, or flow iteration.
- Boundary and initial conditions: unchanged VOF baseline plus retained IC1 pipe patch; IC2 liquid field set to `mp = 1.0` for `y <= 0`.
- Iteration or timestep budget: `0` flow timesteps/iterations.
- Convergence indicators: N/A — initialization/patch artifact.
- Outcome: `Case/data patch-platform checkpoint saved`; not a physical transient result.
- Hypothesized cause if not converged: not applicable. This is the lower global-coordinate bracket for the initial-pool sensitivity.
- Next action: build the planned Y015, Y045, and Y060 siblings from the same IC1 pipe-patch parent, record each selected volume/mass, and run only after the 02d qualification gates are closed.

### Run VOF-IC2-Y030-PATCH-PLATFORM-2026-08-14
- Run ID: `VOF-IC2-Y030-PATCH-PLATFORM-2026-08-14`
- Date: 2026-08-14
- Objective: Create and persist a global-coordinate lower-liquid-pool initialization after visual approval of its shape in the coarse VOF patch platform.
- Geometry: one combined fluid zone. The pool register `vof_ic2_pool_below_y_0p30m` is an inside-hexahedron extending over the full mesh horizontal extents and from `y = -1.484584 m` to the approved horizontal plane `y = +0.300000 m`.
- Mesh: `275,448` mixed cells; `815,716` nodes after case write/read; the region register marks `39,127` cells. Minimum orthogonal quality `0.250006`; maximum aspect ratio `65.1632`.
- Physics model: inherited explicit/sharp VOF; primary `water-vapor`, secondary `water-liquid`; RNG k-epsilon; gravity `[0, -9.81, 0] m/s²`; operating pressure `0 Pa`; energy/DPM/EWF off.
- Solver settings: Hybrid Initialization followed by the existing IC1 pipe patch and IC2 phase-2 liquid patch. No production timestep, coupling/URF change, or flow iteration.
- Boundary and initial conditions: unchanged VOF baseline; inlets `27.118 m/s` and `1.140 MPa` initial gauge pressure; both pressure outlets `1.120 MPa` gauge. IC2 adds phase-2 `mp = 1.0` in the approved `y <= +0.30 m` register.
- Iteration or timestep budget: `0` flow timesteps/iterations; paired case/data checkpoint only.
- Convergence indicators: N/A — initialization/patch artifact.
- Outcome: `Case/data patch-platform checkpoint saved`; not a physical transient result.
- Hypothesized cause if not converged: not applicable. Initial liquid level is a deliberate sensitivity parameter, not an inferred steady state.
- Next action: prepare `y_cut = +0.15`, `+0.45`, and `+0.60 m` siblings with identical controls, report their marked volumes and initialized liquid masses, then run only after the 02d timestep and monitoring gates are closed.

### Run VOF-IC1-PATCH-PLATFORM-2026-08-14
- Run ID: `VOF-IC1-PATCH-PLATFORM-2026-08-14`
- Date: 2026-08-14
- Objective: Recreate the verified no-liquid-patch VOF configuration on the coarse patch-test mesh, create a reproducible brine-pipe patch register, and begin a distinct lower-pool selection trial.
- Geometry: named split inlets and two pressure outlets; the mesh has one combined fluid cell zone, `simple-spiral-separator--brine-outlet-`. User-approved IC1 register `vof_ic1_brine_outlet_5cells` is seeded from the `brine-outlet` face zone at five-cell distance. The distinct unpatched IC2 candidate is a global-coordinate inside-hexahedron register, `vof_ic2_pool_below_y_0p30m`, spanning all horizontal mesh extents and below `y = +0.30 m`.
- Mesh: `275,448` mixed cells; `815,716` nodes after case write/read; minimum orthogonal quality `0.250006`; maximum aspect ratio `65.1632`. Local VOF-relevant sizes and visual lower-pipe connectivity remain unmeasured.
- Physics model: pressure-based `unsteady-1st-order`, explicit/sharp VOF; primary `water-vapor`, secondary `water-liquid`; RNG k-epsilon; gravity `[0, -9.81, 0] m/s²`; operating pressure `0 Pa`; energy/DPM/EWF off.
- Solver settings: PRESTO! pressure and Geo-Reconstruct volume-fraction schemes. Hybrid Initialization completed using Fluent's `10` internal initialization passes. No production timestep, coupling change, URF change, or flow iteration was made.
- Boundary and initial conditions: both inlets `27.118 m/s` with `1.140 MPa` initial gauge pressure; liquid fraction `1.0` at `liquid-inlet` and `0.0` at `steam-inlet`; both pressure outlets `1.120 MPa` gauge; liquid backflow fraction `1.0` at brine and `0.0` at steam.
- Iteration or timestep budget: `0` flow timesteps/iterations. Hybrid Initialization was followed by the user-approved IC1 patch and a paired case/data checkpoint; no solve.
- Convergence indicators: N/A — case-only configuration and register audit.
- Outcome: `IC1 patch-platform checkpoint saved`; IC1 phase-2 `mp = 1.0` was patched in the approved five-cell register (`1,499` cells) and saved to a paired case/data endpoint. The approved `y = +0.30 m` IC2 pool has its own separate paired checkpoint.
- Hypothesized cause if not converged: not applicable. The IC1 pipe selection deliberately includes a small user-approved vessel spill.
- Next action: maintain the distinct IC2 height-sensitivity matrix and do not run it until the 02d timestep, monitor, and stationarity gates are closed.

### Run VOF-IC0-P1120-BUILD-2026-08-14
- Run ID: `VOF-IC0-P1120-BUILD-2026-08-14`
- Date: 2026-08-14
- Objective: Create and reload-verify the Stage-1, no-liquid-patch transient VOF case from the supplied tangential-brine-outlet mesh; do not perform a transient solve.
- Geometry: mesh-based reconstruction using named `liquid-inlet`, `steam-inlet`, `brine-outlet`, and `steam-outlet` zones. The mesh contains one fluid cell zone labelled `simple-spiral-separator--brine-outlet-`; lower-pipe connectivity remains to be visually confirmed before execution.
- Mesh: `C:\Users\syok443\P4P simulation\brine-outlet-620kcells.msh.h5`; `620,431` mixed cells, `1,770,229` nodes, 7 face zones. No quality or local-cell-size survey was performed.
- Physics model: pressure-based explicit VOF; phase 1/primary `water-vapor` (`5.73 kg/m³`), phase 2/secondary `water-liquid` (`881.77 kg/m³`); sharp interface; RNG k-epsilon; gravity `[0, -9.81, 0] m/s²`; Energy off; surface tension unconfigured because no confirmed project/reference value was available; no phase change, DPM injection, EWF, or contact-angle assumption.
- Solver settings: Fluent `unsteady-1st-order` transient formulation (the compatible explicit-VOF choice), pressure interpolation `PRESTO!`, volume-fraction discretization `Geo-Reconstruct`; pressure–velocity coupling read back as `SIMPLE` and is retained as a setting to review before any execution.
- Boundary and initial conditions: both velocity inlets `27.118 m/s` with `1.140 MPa` initial gauge pressure; liquid volume fraction `1.0` at `liquid-inlet` and `0.0` at `steam-inlet`; steam and brine pressure outlets each `1.120 MPa` gauge; liquid backflow fractions respectively `0.0` and `1.0`; operating pressure `0 Pa`.
- Iteration or timestep budget: `0`; no timestep is approved. Fluent's default `1 s` transient-control value is not a production recommendation.
- Convergence monitors: not configured in this case-only build; the required physical-time monitor package and statistical averaging window remain pending.
- Outcome: `Case-only build verified / mesh-based reconstruction only`.
- Hypothesized cause if not converged: not applicable. The main pre-run risk is insufficient local interface resolution or an unjustified timestep, followed by unverified lower-pipe connectivity and unresolved surface-tension evidence.
- Next action: assess local VOF-relevant cell size/quality and define `VOF-DT1` and `VOF-DT2`; visually verify the brine-pipe/lower-vessel connection and configure the required transient monitor package before authorizing Hybrid Initialization of `VOF-IC0-P1120`.

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
- Next action: define common physical/stability monitors and continue or rerun A/B/C to the same stable window before comparing pressure points. See [02c results](../../../Setups/reports/02c/results.md).

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
- Next action: build and analyse Case C from the same frozen parent with a common convergence/stopping gate before comparing the pressure points. See [02c results](../../../Setups/reports/02c/results.md).

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
- Next action: build Case A from the frozen pre-initialization parent at `1.115 MPa` brine pressure and run the same 500-iteration screen before making a pressure-ranking decision. See [02c results](../../../Setups/reports/02c/results.md).

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
- Evidence: [02c comparison report](../../../Setups/reports/02c/results.md), [D flux](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-flux-check.json), [E flux](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-flux-check.json), [F flux](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-flux-check.json), [G flux](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-flux-check.json), and the corresponding residual/audit/DPM links in the report.
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
- Next action: independently Hybrid Initialize each child without a liquid patch; use native autosave and collect outlet phase flows plus continuous-liquid inventory across the common screen. See [02c future runs](../../../Setups/reports/02c/future-runs.md).

### Run 09cV3-RUN-STUDENT-2026-08-04
- Run ID: `09cV3-RUN-STUDENT-2026-08-04`
- Date: 2026-08-04
- Objective: Hybrid-initialize the verified Student `09cV3` fine-mist child, run the first `50` iterations, save a paired checkpoint, explicitly resume from that pair, and continue toward `100` until the user requested a stop.
- Geometry: inherited Student `09cV2` velocity-inlet adaptation geometry with split `liquidinlet` / `steaminlet` topology; original case-only child remains `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`.
- Mesh: `177,564` nodes and `992,771` tetrahedral cells; unchanged throughout the run.
- Physics model: steady Mixture multiphase model; RNG `k-epsilon`; energy off; two-way DPM interaction on; DPM source update every flow iteration; DPM interval `1`; EWF not activated.
- Solver settings: hybrid initialization once; Settings-API iteration calls in chunks of `10`; paired case/data save at the first checkpoint; explicit case/data resume without reinitialization for the second stage.
- Boundary and initial conditions: `liquidinlet` water-liquid velocity `25.7621 m/s`; `steaminlet` water-vapor velocity `27.118 m/s`; seven active fine-mist surface injections on `steaminlet`; total DPM flow `5.846000 kg/s`; inherited input accounting `111.074000 + 5.846000 = 116.920000 kg/s`.
- Iteration budget: first stage completed at `50`; second stage was requested as `50` additional iterations, but the user stopped during the `51–60` chunk after the transcript reached `51–59`; exact in-memory progress at interruption is not claimed; no iteration-100 checkpoint was written.
- Convergence monitors: at iteration 50, continuity `6.4197e-1`; x/y/z velocity `7.1907e-4 / 6.6254e-4 / 6.6994e-4`; `k = 7.5132e-3`; epsilon `1.5149e-2`; water-liquid-VF residual `1.2477e-2`; reversed flow on `35` pressure-outlet faces; turbulent-viscosity ratio limited to `1.0e5` in `26` cells.
- DPM monitor at iteration 50: `21,581` tracked, `20,928` escaped, `650` trapped, and `3` incomplete. These are iteration monitor counts, not a completed per-injection fate result.
- Outcome: `Partially completed / User stopped / Diagnostic only`.
- Hypothesized cause (if non-converged): no causal diagnosis is promoted; the iteration-50 state still has high continuity residual and outlet reverse flow, while the inherited live mass-flow closure remains unverified for the velocity-inlet adaptation.
- Evidence-use label: valid as a run/checkpoint lineage record; not valid as converged carrier evidence, separator-performance evidence, or a per-injection DPM-fate result.
- Next action: leave the live session at the verified iteration-50 checkpoint; resume from that paired case/data only if explicitly requested.

### Run 09cV3-BUILD-2026-08-04
- Run ID: `09cV3-BUILD-2026-08-04`
- Date: 2026-08-04
- Objective: Build and strictly verify the case-only `09cV3` fine-mist PSD child from the read-back-verified Student `09cV2` velocity-inlet adaptation, changing only the active DPM injection population.
- Geometry: inherited Student `09cV2` velocity-inlet adaptation geometry and split `liquidinlet` / `steaminlet` topology; the child case is `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`.
- Mesh: `177,564` nodes and `992,771` tetrahedral cells, read back while loading the explicit parent and child case; no mesh change was made.
- Physics model: steady Mixture multiphase model; RNG `k-epsilon`; energy off; DPM interaction on; DPM source update every flow iteration; DPM interval `1`; EWF not activated in the inherited branch.
- Solver settings: inherited carrier and DPM tracking settings; no initialization, no solution iteration, no data read, and case-only writes only.
- Boundary and initial conditions: `liquidinlet` water-liquid velocity `25.7621 m/s`; `steaminlet` water-vapor velocity `27.118 m/s`; seven active `Surface` injections on `steaminlet`; flow inputs `0.409128`, `1.165149`, `1.267410`, `1.092501`, `1.329262`, `0.468606`, and `0.113944 kg/s`; read-back total `5.846000 kg/s`; setup-level accounting `111.074000 + 5.846000 = 116.920000 kg/s`.
- Iteration budget: `0` flow iterations; the planned `20–50`-iteration smoke test was not run in this build.
- Convergence monitors: not applicable to a case-only build; strict reload read back inlet velocities, model controls, material identities, seven injection payloads, wall fates, and the input accounting closure.
- Outcome: `Case-only build verified / diagnostic only`.
- Hypothesized cause (if non-converged): not applicable; the inherited velocity-inlet adaptation still lacks an independent live mass-flow report for the `111.074000 kg/s` Eulerian-liquid reference, and no converged carrier result is claimed.
- Evidence-use label: valid as a setup and lineage record; not valid as a separator-performance, convergence, or DPM-fate result. The seven-bin PSD is an `Assumed`, medium-risk engineering prior rather than measured inlet data.
- Next action: if the user authorizes execution, run the documented short smoke test from the saved child, preserving the case-only checkpoint and recording residuals, phase fluxes, DPM source terms, and per-injection fates.

### Run EWF-010V2A-POST-2026-07-22
- Run ID: `EWF-010V2A-POST-2026-07-22`
- Date: 2026-07-22
- Objective: Read-only post-simulation assessment of `010V2a`, the isolated Eulerian wall-film particle-splash branch.
- Geometry: active Purnanto-style separator branch with `liquidinlet`, `steaminlet`, `steamoutlet`, `bottom`, and `wall`; no lower liquid drain/brine outlet appears in the extracted flux report.
- Mesh: not captured by this post-processing pass.
- Physics model: two-phase Mixture carrier; RNG `k-epsilon`; global DPM interaction with the continuous phase `Off`; EWF splash is the intended isolated branch change, but the standard collector did not capture live EWF readback.
- Solver settings: DPM unsteady tracking `Off`; maximum particle steps `10000`; detailed EWF film numerics not captured.
- Boundary/initial condition values: phase flux extraction gives liquid inlet `111.074 kg/s`, vapour inlet `80.690 kg/s`, and vapour steam outlet `81.4218 kg/s`.
- Iteration budget: residual history through iteration `1963`.
- Convergence indicators: velocity residuals are low, but continuity finishes at `2.290e-3`; final-100 `k` spans `1.115e-2`–`3.889e-1` and epsilon spans `1.323e-2`–`5.526e-1`. The derived lower-liquid/whole-domain imbalance is `110.3422 kg/s` (`57.54 %` of inlet).
- Outcome: `Partially Converged / Diagnostic Only`.
- DPM result: the retried Particle Tracks Summary completed for all six live injections. Displayed escaped/trapped/incomplete counts are respectively `2162/0/7`, `2158/2/4`, `2007/5/4`, `1510/20/3`, `1008/33/3`, and `435/54/0` from `5.63` through `348.88 um`. The compact summary does not close to the tracked count for every injection; the unclassified differences are `1`, `6`, `158`, `641`, `1130`, and `1681`, so they remain unresolved rather than being assigned a physical fate. No splash-mass count is available.
- Assumptions: retained liquid is allowed for this no-brine-outlet EWF diagnostic; it is not a closed separator balance. Incomplete DPM tracks are retained as an unresolved long-residence population that may later escape by entrainment, not counted as completed escape or collection.
- Next action: monitor EWF film CFL, film mass/inventory, thickness, DPM-film source, film outflow, splashed represented mass, and a DPM report that identifies the unclassified fate category before comparing with `010V2`.

### Run PURNANTO-08B-POSTPROCESS-2026-07-02
- Run ID: `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Date: 2026-07-02
- Objective: post-process the already-run setup `08b` `5000`-iteration case/data on the live Fluent server, record the current phase-flux result, and refresh the active 6-injection DPM summary without rebuilding the case.
- Geometry: `purnanto` split-inlet parity-reset branch from `../../../Setups/past/reported/08b-purnanto-parity-split-inlet-rebuild.md`; two `mass-flow-inlet` zones (`liquidinlet`, `steaminlet`), one `pressure-outlet` zone (`steamoutlet`), walls `bottom` and `wall`.
- Mesh: `1,309,312` nodes and `7,601,261` tetrahedral cells (`Observed` from the live case readback during the manual load and server-side post-processing session).
- Physics model: steady pressure-based `Mixture` with `2` phases; `phase-1 = water-vapor-at-psep`; `phase-2 = water-liquid-at-psep`; `RNG k-epsilon`; energy off; one-way DPM active with `pressure force = on`, `virtual mass = on`, `max_num_steps = 10000`, and `step-length-factor = 5`.
- Solver settings: carrier field already solved to the saved `5000`-iteration state before this post-processing pass; no rebuild, no new carrier iterations, and no new injections were created during this run.
- Boundary and initial conditions: liquid inlet target `116.92 kg/s`; steam inlet target `80.69 kg/s`; steam outlet only for exported phase-flux result; active DPM subset contains `5.63`, `28.14`, `56.27`, `112.54`, `168.81`, and `348.88 um` steam-side surface injections. Larger `562.70`, `844.06`, and `1631.84 um` bins were intentionally omitted from this pass.
- Iteration budget: carrier field already saved at `5000` iterations; one DPM refresh pass run through Fluent `/solve/dpm-update`.
- Convergence monitors: live post-processing extracted phase-flux output and the refreshed aggregate `dpm-summary`; no new residual history was generated because the carrier solve was not rerun.
- Outcome: `Post-processed / DPM Diagnostic Only`.
- Flux result: liquid inlet `116.92 kg/s`; steam inlet `80.69 kg/s`; steam outlet vapor `81.464165 kg/s`; steam outlet liquid `0.082132007 kg/s`.
- Calculated flux metrics: scoped steam-line liquid-removal efficiency `eta_phase = 99.92975367 %`; steam-outlet dryness `x_out = 99.89928175 %`.
- Mass-balance caution: the same live report gives mixture inlet `197.61 kg/s`, mixture outlet `81.546281 kg/s`, and mixture imbalance `116.063719 kg/s`, so the carryover result is still a scoped steam-line diagnostic, not a closed whole-separator efficiency result.
- DPM summary result: aggregate Fluent summary reports `13012` incomplete and `8` escaped particles, with no `trapped` row printed in the refreshed summary output; escaped represented mass flow is `7.005e-04 kg/s`, while incomplete represented mass is `29.22 kg/s`.
- Per-injection sampled result: one-injection-at-a-time `dpm-sample` to `steamoutlet` gives `2170` tracked particles per active injection. `injection-5-micron` reports `8` escaped and `2162` incomplete; `injection-28-micron`, `injection-56-micron`, `injection-112-micron`, `injection-168-micron`, and `injection-348-micron` each report `2170` incomplete and `0` escaped / `0` trapped in this sampled pass.
- DPM interpretation: the current active 6-bin DPM pass is dominated by incomplete tracks, so it should stay `Debug only` and should not yet be promoted to a report-facing removal-efficiency claim. The one-injection-at-a-time sample now supports the narrower statement that the observed completed sampled escape is confined to `injection-5-micron` in this pass, but the result is still not strong enough for full per-bin fate claims because tracking completion remains poor.
- Evidence-use label: valid as a live post-processing record for setup `08b` and as a current DPM-screening result for the active 6-bin subset; not valid as a full validation result or a full 9-bin historical-parity DPM result.
- Hypothesized cause (if non-converged): the dominant issue is DPM tracking completion, not obvious high escaped mass. The unresolved lower liquid inventory and lack of a separate drain/outlet closure also keep the carrier flux result from becoming a stronger whole-separator efficiency claim.
- Next action: increase DPM tracking budget first, then rerun the same active 6-bin subset before interpreting DPM more strongly; if needed, export per-injection zone summaries instead of relying only on the aggregate Fluent `dpm-summary` output.

### Run GEOM-NAMING-PURNANTOV2-2026-06-11
- Run ID: `GEOM-NAMING-PURNANTOV2-2026-06-11`
- Date: 2026-06-11
- Objective: record the project geometry split between the closer paper-parity `purnanto` geometry and the later cleaned `purnantov2` geometry so future setup branches use the names consistently.
- Geometry: `purnanto` = closer original Purnanto-style spiral-inlet separator geometry with the steam-outlet boundary at the outlet entrance; `purnantov2` = later project geometry with the steam outlet meshed downward so the outlet boundary is downstream near the bottom of the separator, plus local spiral-inlet and dish-head cleanup.
- Mesh: not a solve; naming / geometry-definition update only.
- Physics model: not a solve; this entry records setup-lineage geometry identity rather than a Fluent model change.
- Solver settings: not applicable.
- Boundary and initial conditions: key geometry-related BC distinction is that `purnanto` places the steam pressure-outlet boundary at the steam-outlet entrance, while `purnantov2` places the outlet boundary downstream after a longer meshed outlet passage.
- Iteration budget: not applicable.
- Convergence monitors: not applicable.
- Outcome: `Geometry Naming Defined`.
- Evidence-use label: valid as the project naming authority for future setup reports; not a simulation result.
- Hypothesized cause (if non-converged): not applicable.
- Next action: treat setups `04` to `07` as `purnanto` geometry by default, and setup `08` plus later geometry branches as `purnantov2` unless a later setup report explicitly overrides that geometry identity.

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
- Geometry: current project one-inlet geometry exported as `trial4.msh`, likely closer to the `purnantov2` line because it came from the extended-outlet mesh workspace, with one inlet, one outlet, walls including `bottom`, and no active liquid drain / sink branch in this diagnostic.
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
- Geometry: current project one-inlet geometry exported as `trial4.msh`, likely closer to the `purnantov2` line because it came from the extended-outlet mesh workspace, with one inlet, one outlet, walls including `bottom`, and no active brine-outlet branch in this parity pass.
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
- Geometry: current project one-inlet geometry exported as `trial3.msh`, likely closer to the `purnantov2` line because it came from the extended-outlet mesh workspace, with one inlet, one outlet, and wall boundaries including named `bottom`.
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
- Geometry: `purnantov2` one-inlet recreation branch by intent, to be paired with one inlet boundary carrying both phases together; keep geometry naming separate from the one-inlet BC choice.
- Mesh: use the current project mesh family for the rebuild branch; exact chosen mesh/case filename still to be recorded when the case is built.
- Physics model: steady pressure-based `Mixture` model with primary vapor and secondary liquid, `RNG k-epsilon`, gravity on, energy off.
- Solver settings: retain the live-audited Purnanto baseline stack: `SIMPLE`, Green-Gauss Node Based gradient, `PRESTO!`, second-order momentum / `k` / `epsilon`, `QUICK` volume fraction, and `Hybrid Initialization`.
- Boundary and initial conditions: one `Mass-Flow Inlet` with vapor `80.69 kg/s`, liquid `116.92 kg/s`, gauge/initial pressure field `1,140,000 Pa`, turbulence intensity `2.11 %`, hydraulic diameter `0.724 m`; one `Pressure Outlet` at `1,120,000 Pa`; no split inlet zones in this branch.
- Iteration budget: not yet run; setup-definition stage only.
- Convergence monitors: when built, first check phase mass-flow reports, residual criteria parity, and gross mass balance before any performance interpretation.
- Outcome: `Setup Defined`.
- Evidence-use label: direct Purnanto-recreation branch definition only.
- Hypothesized cause (if non-converged): not yet applicable; the point of this branch is to remove the split-inlet change and return to the simpler paper-style one-inlet package.
- Next action: build the Fluent case from `../../../Setups/past/archived/08-purnanto-one-inlet-massflow-recreation.md` and verify the boundary/model stack before reviving any split-inlet comparison logic.

### Run PLS-STUDENT-OUTLET-EXT-2026-06-08
- Run ID: `PLS-STUDENT-OUTLET-EXT-2026-06-08` (`Assumed` setup label until the Fluent case filename is confirmed)
- Date: 2026-06-08
- Objective: Test whether moving the steam pressure-outlet boundary downstream of the central outlet-pipe entrance reduces outlet backflow reversal and stabilizes steam-outlet mass-flux reports.
- Geometry: child of `../../../Setups/past/reported/07-pure-phase-split-actual-area.md`; uses the `purnantov2` geometry branch with setup `07` pure liquid / pure steam split inlet, plus the downstream steam-outlet extension so `steam_outlet` is placed at the end of the longer outlet path.
- Mesh: pending student-edition rebuild; record nodes, cells, minimum orthogonal quality, maximum skewness, and outlet-extension local mesh quality before running.
- Physics model: inherit setup `07` steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off unless the rebuilt Fluent case forces a documented change.
- Solver settings: inherit setup `07` (`SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, setup `07` volume-fraction scheme, hybrid initialization) unless explicitly recorded as changed.
- Boundary and initial conditions: same setup `07` split inlet values: `inlet_liquid_outer` velocity inlet at `27.118 m/s`, liquid VF `1.0`, hydraulic diameter `0.01338 m`; `inlet_steam_inner` velocity inlet at `27.118 m/s`, liquid VF `0.0`, hydraulic diameter `0.72061 m`; `steam_outlet` pressure outlet moved to the end of the extended outlet path.
- Iteration budget: pending; choose after mesh count and student-edition runtime limit are known.
- Convergence monitors: residuals, inlet liquid/steam phase fluxes, steam-outlet phase fluxes, outlet-face backflow warnings, velocity vectors near the central outlet intake, velocity vectors inside the outlet extension, and liquid volume fraction near the outlet intake.
- Outcome: `Planned`.
- Evidence-use label: planned student-edition geometry diagnostic only. This branch can test boundary-placement sensitivity, but it is not final separator-performance evidence unless mesh quality, residual/monitor stability, and flux stability are documented.
- Hypothesized cause (if non-converged): `Inferred` pressure-outlet boundary placement at the immediate outlet-pipe entrance may expose the boundary to local swirling/recirculating flow, causing backflow reversal and unstable outlet mass-flux reporting.
- Next action: build the setup `08a` geometry from `../../../Setups/past/archived/08a-steam-outlet-extension-student-trial.md`, confirm the former outlet-pipe entrance is internal flow passage rather than a boundary face, then initialize and verify inlet fluxes before running.

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
- Objective: Record the professional-license baseline flux result for `../../../Setups/past/reported/07-pure-phase-split-actual-area.md` before running quick DPM droplet-size efficiency checks.
- Geometry: `purnanto` spiral-inlet BOC separator with pure liquid / pure steam split inlet using the actual-area setup from `../../../Setups/past/reported/07-pure-phase-split-actual-area.md`.
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
- Geometry: likely `purnanto` spiral-inlet BOC separator with pure liquid / pure steam split inlet sized from `../../../Setups/past/reported/07-pure-phase-split-actual-area.md`; both inlet legs appear extended upstream in the rough report.
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
- Geometry: spiral-inlet BOC separator with the same pure liquid / pure steam split sizing from `../../../Setups/past/reported/07-pure-phase-split-actual-area.md`; rough report notes that only the steam inlet kept the upstream extension while the liquid inlet was moved closer to the vessel.
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
- Solver settings: inherit from `../../../Setups/past/reported/04-mixed-wet-half-actual-area.md` unless separately changed.
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
- Next action: create the two named inlet faces from `../../../Setups/past/archived/06-pure-phase-split-fixed-velocity.md`, then verify Fluent flux reports before interpreting outlet behavior.

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
- Geometry: `purnanto` spiral-inlet BOC separator with one full inlet boundary; brine outlet absent or closed as a wall for this branch.
- Mesh: same current project mesh family unless a new no-brine-outlet mesh export supersedes it; approximately 1.8M nodes from prior user-reported mesh scale remains the working assumption.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from the mixed wet-half actual-area setup where applicable: `SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, higher-order volume-fraction scheme where available, and hybrid initialization.
- Boundary and initial conditions: one full `Velocity Inlet` at `26.81 m/s`, liquid water volume fraction `0.009328`, steam/vapor volume fraction `0.990672`; calculated full-area inlet flow is liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`; steam outlet remains a pressure outlet with steam-dominant backflow; brine outlet inactive.
- Iteration budget: `5000` steady iterations, with recommended saves at `1000`, `3000`, and `5000` iterations.
- Convergence monitors: residuals, global mass imbalance, inlet phase mass flows, steam-outlet steam flow, steam-outlet liquid carryover, liquid-volume-fraction contours, and velocity vectors near the spiral inlet and steam outlet.
- Outcome: `Planned`.
- Evidence-use label: setup calculation only until `5000`-iteration residuals, mass balance, and outlet phase fluxes are checked.
- Hypothesized cause (if non-converged): not yet applicable; main risk is that no active brine outlet may accumulate or carry liquid to the steam outlet, making the run unsuitable for liquid-removal efficiency.
- Next action: create the Fluent case from `../../../Setups/past/archived/05-complete-two-phase-actual-area-no-brine-outlet.md`, confirm the brine outlet is not active, and run the planned checkpoint sequence.

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
- Next action: add mass flux interpretation, outlet phase fluxes, separator efficiency, and key contour/vector findings to `../../../Setups/past/reported/04-mixed-wet-half-actual-area.md` and its linked results report.

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
- Evidence: [02c future-run queue record](../../../Setups/reports/02c/future-runs.md), [H20–H50 build manifest](../../../PyAnsys/output/02c-above-inlet-20-to-50-build-20260816T002025Z.json), and [local native journal](../../../PyAnsys/output/02c-above-inlet-20-to-50-queue-20260816T003500Z.jou).
- Next action: allow Fluent to complete or stop safely if unavailable; verify every paired remote endpoint before post-processing. Interpret the broad sweep only with outlet phase fluxes, reverse-flow diagnostics, residuals, and total liquid-inventory history.
