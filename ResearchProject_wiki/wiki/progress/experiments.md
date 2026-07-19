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
