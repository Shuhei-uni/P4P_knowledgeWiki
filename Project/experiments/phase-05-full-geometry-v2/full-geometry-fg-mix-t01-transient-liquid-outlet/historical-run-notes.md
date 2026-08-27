> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run FG-MIX-T01-S1-CANDIDATES-2026-08-16

- Run ID: `FG-MIX-T01-S1-CANDIDATES-2026-08-16`
- Date: 2026-08-16.
- Objective: Run the user-requested quick Stage-1 pressure-candidate screen between 02c Cases G and H, then identify a provisional parent for the next transient-stage construction.
- Geometry variant: Full-geometry Mixture transient-liquid-outlet campaign; exact production mesh identity preserved.
- Mesh: `Full-geomV2-231kcells.msh.h5`; Fluent reload readback `231,376` mixed cells and `697,078` nodes. No remeshing, adaptation, or mesh substitution.
- Physics model assumptions: pressure-based steady Mixture; phase-1 water vapour and phase-2 water liquid; RNG `k-epsilon`; gravity `[0, -9.81, 0] m/s²`; Energy off; unpatched/unprimed initial state; DPM/EWF not enabled by the candidate builder.
- Solver settings: Fluent-native Hybrid Initialization followed by one native `solve/iterate 1000` command per independent case; common 02c solution controls; no Python iteration loop.
- Boundary/initial condition values: split velocity inlets `27.118 m/s`; inlet initial gauge pressure `1.140 MPa`; steam outlet pressure outlet `1.120 MPa`; brine backflow liquid volume fraction `1.0`; steam-outlet backflow liquid volume fraction `0.0`; only brine-outlet gauge pressure varied.
- Candidate matrix: `1.1360 MPa` (`C136`), `1.1375 MPa` (`C1375`), and `1.1390 MPa` (`C139`).
- Iteration budget: `1,000` steady iterations per candidate; all three paired case/data endpoints were written and remote-file verified.
- Convergence indicators: endpoint residual extraction retained `400` points over reported iterations `4–1,000`. Final continuity was `2.4976e-1` (`C136`), `2.2536e-1` (`C1375`), and `1.7239e-1` (`C139`). Reverse-flow warnings and turbulent-viscosity limiting persisted in all three runs.
- Outcome: `Partially Converged` as an execution screen only; numerically non-converged/open for scientific interpretation. Provisional candidate parent: `C1375` at `1.1375 MPa`, selected for the balance of retained residual smoothness and phase-routing behaviour, not for a final pressure claim.
- Hypothesized limitation: the simplified/open liquid-routing field remains inventory-draining, with liquid-brine outflow above liquid inlet at all recorded endpoints; missing total-inventory and lower-vessel pressure monitors prevent a stronger stability claim.
- Evidence: Stage-1 candidate report (retired source, details retained in this Project packet), build snapshot (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage1_candidates_20260816T102830Z.json`; not migrated), and the three linked residual/flux artifacts in that report.
- Next action: before Stage 2, explicitly reload the `C1375` paired endpoint, verify mesh/model/boundary/case-data identity, then construct the controlled transient startup branches without adding a Y010 patch to the steady endpoint.

### Run FG-MIX-T01-S2-START-STATES-2026-08-16
- Run ID: `FG-MIX-T01-S2-START-STATES-2026-08-16`
- Date: 2026-08-16.
- Objective: Construct the two matched Stage-2 transient startup states for the user-selected `C1375` candidate before the Stage-3 initialization comparison.
- Geometry and mesh: exact full-geometry mesh `Full-geomV2-231kcells.msh.h5`; reload readback `231,376` cells and `697,078` nodes. No remeshing, adaptation, scaling, or mesh substitution.
- Physics/model contract: C1375 Mixture/RNG `k-epsilon` field, water-vapour/water-liquid pair, gravity, operating pressure, split velocity inlets, steam outlet, DPM interaction off, and EWF off preserved. T-PO-1 brine pressure set to `1.200 MPa` gauge in both branches.
- Branches: `INIT-S` loaded the developed C1375 field; `INIT-H` loaded the same source case/data and used Fluent Hybrid Initialization. Both created the same Y010 register and applied one phase-2 liquid `mp = 1.0` patch.
- Transient controls: Fluent `unsteady-2nd-order-bounded`; PISO with one neighbor-correction iteration; fixed `2.5e-4 s` timestep; maximum `20` iterations per timestep; flow time `0 s`; zero transient timesteps run.
- Readback: both paired case/data artifacts were written and independently reloaded. Y010 selected `33,315` cells; post-patch liquid volume was `4.793078931 m³` (`INIT-S`) and `4.790652590 m³` (`INIT-H`).
- Outcome: `Case construction complete; user-accepted scope limitation`. The two post-patch Y010 volumes differ by approximately `0.05065%`; the user accepted this physical difference for comparison. Several optional volume-report history toggles were read-only in the Fluent 2025 R2 Settings API. Direct total-liquid-mass monitoring was prepared separately before any replacement Stage-3 run.
- Evidence: Stage-2 startup-state report (retired source, details retained in this Project packet), build manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage2_start_states_20260816.json`; not migrated), and the four remote paired artifacts named in the report.
- Next action: use the monitor-ready copies for the equal-physical-time INIT-S versus INIT-H comparison when explicitly authorized; preserve the accepted Y010 difference as a scope limitation.

### Run FG-MIX-T01-S3-INIT-CANCELLED-2026-08-16
- Run ID: `FG-MIX-T01-S3-INIT-CANCELLED-2026-08-16`
- Date: 2026-08-16.
- Objective: begin the equal-physical-time `INIT-S` versus `INIT-H` comparison for the user-selected C1375 parent using `1,000` transient steps at `2.5e-4 s` (`0.25 s` nominal horizon), then retain a per-step total-liquid-mass history.
- Geometry and mesh: exact `Full-geomV2-231kcells.msh.h5`; the prepared start states reloaded as `231,376` cells and `697,078` nodes. No mesh change was made.
- Execution: the first native queue was submitted with Fluent owning the transient solve. The user then requested cancellation; the native interrupt succeeded during `INIT-H` before `INIT-S` began, the transcript was closed, and Fluent was left idle.
- Endpoint status: neither branch wrote a paired Stage-3 case/data endpoint. The partial attempt is excluded from physical comparison and provides no complete liquid-mass history.
- Monitoring recovery: the saved Stage-2 pairs were reloaded without reinitialization, repatching, or advancing. Fresh monitor-ready copies now contain direct full-domain phase-2 `volume-mass` report `fg_mix_t01_s3_total_liquid_mass`, with report-file output true after reload verification.
- Outcome: `Canceled / no comparison result; monitor-ready restart inputs prepared`.
- Evidence: Stage-3 cancellation and mass-monitor report (retired source, details retained in this Project packet), canceled submission manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T120500Z.json`; not migrated), and monitor-preparation manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_total_mass_monitor_20260816T124000Z.json`; not migrated).
- Next action: wait for explicit restart direction; if restarted, use the monitor-ready pairs and preserve the `1,000`-step / `0.25 s` budget.

### Run FG-MIX-T01-S3-INIT-FAILED-FPE-2026-08-16
- Run ID: `FG-MIX-T01-S3-INIT-FAILED-FPE-2026-08-16`
- Date: 2026-08-16.
- Objective: run the monitor-ready INIT-H versus INIT-S comparison for `1,000` transient steps at `2.5e-4 s`, while recording total phase-2 liquid mass through the direct `volume-mass` report.
- Start-state verification: both branches reloaded with the exact `Full-geomV2-231kcells.msh.h5` mesh (`231,376` cells; `697,078` nodes), Mixture model, `1.200 MPa` brine pressure, zero flow time, and the expected Y010/Y030 registers.
- Execution: the native journal entered `INIT-H` and ran Fluent-owned transient steps. `INIT-S` was not reached.
- Failure: `INIT-H` failed at transient step `53` after continuity reached `3.1443e+57`; Fluent reported turbulent-viscosity limiting in all `231,376` cells, reversed flow at both pressure outlets, AMG divergence across the solved variables, and a floating-point exception.
- Endpoint and mass-history status: no paired endpoint was written for either branch. The direct liquid-mass report was loaded, but the failed partial attempt does not provide a complete or scientifically usable mass trajectory.
- Outcome: `Failed / floating-point exception; no Stage-3 comparison result`.
- Evidence: Stage-3 initialization comparison report (retired source, details retained in this Project packet), failed-run manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T115435Z.json`; not migrated), failed-run journal (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T115435Z.jou`; not migrated), and the partial remote INIT-H transcript recorded in the manifest.
- Next action: hold automatic retries. A new user decision is required on timestep/initialization/outlet stabilization before another native run.

### Run FG-MIX-T01-S3-NP-DT1-2026-08-17
- Run ID: `FG-MIX-T01-S3-NP-DT1-2026-08-17`
- Date: 2026-08-17.
- Objective: test whether the current bounded-second-order transient Mixture formulation can start from the developed unpatched steady parent with no Y010 liquid patch at the common `1.120 MPa`/`1.120 MPa` pressure-outlet condition.
- Geometry variant: Full-geometry Mixture transient-liquid-outlet campaign using the exact `Full-geomV2-231kcells.msh.h5` mesh.
- Mesh stats: `231,376` cells and `697,078` nodes; no remeshing, adaptation, scaling, or mesh substitution.
- Physics model assumptions: pressure-based Mixture; implicit volume-fraction treatment; inherited RNG `k-epsilon`; unchanged inlets, outlet families, materials, gravity, DPM/EWF state, and spatial discretization; no Y010/Y030 inventory patch.
- Solver settings: bounded second-order transient; current PISO settings with one neighbor-correction iteration; fixed `2.5e-4 s` timestep; maximum `20` iterations per timestep; Fluent-native `/solve/iterate 200` command.
- Boundary/initial conditions: steady C1375 parent loaded as the initial field; both steam and brine pressure outlets at `1.120 MPa` gauge; no Hybrid Initialization after load; no patch; flow time reset to `0 s`.
- Iteration or timestep budget: requested `200` transient steps, nominal `0.05 s`; the run terminated before completion and wrote no endpoint pair.
- Convergence indicators: continuity grew from `2.2536e-1` through `2.2440e+2`, `8.4960e+6`, `6.6879e+16`, and `3.2426e+51`; turbulent-viscosity limiting reached all `231,376` cells; reverse flow occurred at both pressure outlets; AMG divergence was reported for pressure correction, `k`, `epsilon`, and `vof-1`; terminal floating-point exception.
- Outcome: `Failed / floating-point exception; no-patch transient control did not survive`.
- Hypothesized cause if not converged: timestep resolution, the inherited unpatched parent field, outlet-driven phase redistribution, or another coupled numerical mechanism remains unresolved. The exact transient-step/physical-time failure coordinate is not claimed because the live monitor retained a global residual label rather than a reliable transient-step coordinate.
- Evidence: NP-DT1 report (retired source, details retained in this Project packet), result manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step_20260817.json`; not migrated), native journal (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step.jou`; not migrated), and the remote transcript named in the report.
- Next action: do not launch the six-case screen or alter multiple numerical controls. Decide whether to authorize NP-DT2 at `1.25e-4 s` with every other control frozen.
