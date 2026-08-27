> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md  
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Raw and machine-generated artifacts remain at their legacy paths.

# Historical run notes

> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

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
