> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

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
- Next action: build the Fluent case from `setup.md` and verify the boundary/model stack before reviving any split-inlet comparison logic.
