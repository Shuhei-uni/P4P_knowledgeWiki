# PyFluent Trial3 One-Inlet Reconstruction Smoke Test

## Purpose

Record the actual PyFluent setup attempt on the current local `trial3.msh` branch so the next automation pass can start from working evidence rather than repeating avoidable failure modes.

This page is project-specific technical evidence for the current local rebuild path, not a generic Fluent tutorial.

Primary linked setup context:

- `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`
- `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
- `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`

## Scope

- Geometry/mesh: local current-project `trial3.msh`
- Setup intent: practical one-inlet Purnanto-style recreation
- Goal of this pass: prove Python can launch Fluent locally, load the mesh, build a usable setup, hybrid initialize, and advance a short steady run
- Out of scope: exact paper parity, DPM, polished numerics, final validation, final separator-efficiency claims

## Evidence Labels

- `Reported`: taken from setup `08` and the live Purnanto audit
- `Observed`: seen directly during the local PyFluent runs on `2026-06-09`
- `Inferred`: interpretation of why a behavior happened
- `Assumed`: recommended next-step fallback where the exact Fluent API path is still uncertain

## Working Inputs Used

### Mesh and boundary discovery

- `Observed`: mesh file loaded successfully from `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial3.msh`
- `Observed`: detected boundary family after load:
  - one inlet: `inlet`
  - one outlet: `outlet`
  - walls: `bottom`, `wall-part1`

### Intended baseline package

- `Reported`: one mixed steam-water `Mass-Flow Inlet`
- `Reported`: one `Pressure Outlet`
- `Reported`: `Mixture` model, `RNG k-epsilon`, gravity on, energy off
- `Reported`: inlet vapor mass flow `80.69 kg/s`
- `Reported`: inlet liquid mass flow `116.92 kg/s`
- `Reported`: inlet pressure-related value `1,140,000 Pa`
- `Reported`: outlet gauge pressure `1,120,000 Pa`
- `Reported`: operating pressure `0 Pa`
- `Reported`: turbulence intensity about `2.11 %`
- `Reported`: hydraulic diameter `0.724 m`

## What Worked

### 1. Local Fluent launch through PyFluent

- `Observed`: `ansys.fluent.core` launched local Fluent successfully after Fluent and Workbench windows were closed.
- `Inferred`: the local Student setup is usable for direct local PyFluent automation as long as another ANSYS session is not already occupying licensing/resources.

### 2. Mesh-only case load and zone detection

- `Observed`: the script could load `trial3.msh`, inspect boundary-condition state, and detect the key one-inlet / one-outlet / wall zones without needing a prebuilt `.cas.h5`.
- `Inferred`: for early automation testing, a mesh path is enough; a case file is not required to prove basic setup control.

### 3. Boundary conversion and main model activation

- `Observed`: inlet conversion from `velocity_inlet` to `mass_flow_inlet` worked.
- `Observed`: outlet confirmation as `pressure_outlet` worked.
- `Observed`: the script successfully enabled:
  - `Mixture`
  - `RNG k-epsilon`
  - energy off
  - phase-2 droplet diameter fallback

### 4. Manual material creation for water vapor and liquid water

- `Observed`: a fresh mesh-only load exposed only `air` as the default fluid material.
- `Observed`: PyFluent material creation worked through `solver.settings.setup.materials.fluid.create(...)` plus `set_state(...)`.
- `Observed`: the following manual materials were created and assigned successfully:
  - `water-vapor-manual`: density `5.7974339 kg/m3`, viscosity `1.52062e-05 kg/(m s)`
  - `water-liquid-manual`: density `881.21088 kg/m3`, viscosity `0.000145544 kg/(m s)`
- `Inferred`: this is the key workaround that makes a mesh-only PyFluent reconstruction viable even when the saved case materials are unavailable.

### 5. Inlet and outlet state application

- `Observed`: the inlet mass-flow package applied successfully for phase-1 and phase-2.
- `Observed`: the outlet pressure condition applied successfully.
- `Observed`: Fluent accepted the practical one-inlet branch as a runnable case even though some higher-level setting paths remained imperfect.

### 6. Hybrid initialization and short smoke test

- `Observed`: hybrid initialization completed successfully.
- `Observed`: the case then advanced through `10` steady iterations without crashing.
- `Observed`: final residual magnitudes at iteration `10` were approximately:
  - continuity: `4.98e-01`
  - `x` velocity: `1.15e-03`
  - `y` velocity: `9.23e-04`
  - `z` velocity: `1.02e-03`
  - `k`: `3.25e-02`
  - `epsilon`: `1.63e-01`
  - `vf-phase-2`: `5.63e-02`
- `Inferred`: this run is only a smoke test, not convergence evidence, but it proves the setup is solver-runnable and not obviously broken.

## Troubles And Workarounds

### Trouble 1. Fluent/Workbench already open blocked clean local testing

- `Observed`: earlier retries failed until existing Fluent/Workbench windows were closed.
- `Workaround used`: close active ANSYS GUI sessions first, then relaunch the PyFluent script.
- `Why it likely helped`: `Inferred` licensing/session conflicts or already-busy local resources were interfering with fresh local launch.

### Trouble 2. Original mesh/case paths were inconsistent

- `Observed`: earlier candidate files included `.meshdat` and `.mshdb` paths that were not the cleanest direct test target for this script.
- `Workaround used`: switch to the exported `trial3.msh` mesh in the main project directory.
- `Why it helped`: `Inferred` the plain `.msh` path reduced uncertainty around what Fluent could read directly through the tested API.

### Trouble 3. Mesh-only case had no usable water materials

- `Observed`: material lookup initially failed because only `air` existed in the new mesh-loaded session.
- `Workaround used`: manually create fluid materials and assign density and viscosity values directly in PyFluent.
- `Why it helped`: this removed dependence on a pre-existing Fluent material database entry or a prebuilt case file.

### Trouble 4. High-level operating-pressure setter failed

- `Observed`: the script hit `Value is not in range` when trying to set operating pressure and gravity through the high-level settings API.
- `Workaround used`: leave the direct operating-pressure setter unresolved for now and force gravity on through a Scheme fallback.
- `What this means`: gravity is being applied, but the exact operating-pressure setter path still needs a cleaner Fluent-version-specific fix.

### Trouble 5. Several solution-method setters used the wrong API path for this Fluent version

- `Observed`: direct setters for `SIMPLE`, `PRESTO!`, momentum, volume fraction, `k`, and `epsilon` discretization partly failed even though the case still ran.
- `Observed`: at least the gradient-scheme path was recoverable via the newer `spatial_discretization` route.
- `Workaround used`: keep the case runnable first, accept partial numerics-setting failure, and rely on the smoke test to verify the setup is still operational.
- `What this means`: numerics parity is not yet fully scripted even though the model and boundary skeleton now work.

### Trouble 6. Pressure-outlet subsettings were partly inactive at assignment time

- `Observed`: Fluent reported some pressure-outlet momentum/turbulence settings as inactive when the state was applied.
- `Workaround used`: accept the applied state where Fluent allowed it and continue with the smoke test instead of blocking on a perfect outlet-state write.
- `Inferred`: this may be due to setting-order sensitivity, inactive panels for the current model state, or version-specific state-shape differences.

## Current Known Caveats

1. `Observed`: operating pressure `0 Pa` is still not being set through the clean high-level API path in the script.
2. `Observed`: the script does not yet fully reproduce the intended solution-method stack by explicit PyFluent setters.
3. `Observed`: the smoke test proves runnability, not final physical correctness or convergence quality.
4. `Assumed`: local Student licensing and already-open ANSYS sessions may continue to affect repeatability if the environment is not clean before launch.

## Best Current Practical Workflow

1. Close Fluent and Workbench before launching the script.
2. Use `trial3.msh` as the current direct test mesh.
3. Build the case from the one-inlet setup `08` logic.
4. Create manual water vapor and liquid water materials inside PyFluent.
5. Apply the one-inlet mass-flow package and one pressure outlet.
6. Use hybrid initialization.
7. Run a short iteration smoke test before attempting any longer solve or post-processing workflow.

## Improvement Points To Try Next

### Priority 1. Fix operating-pressure scripting cleanly

- Goal: explicitly set `Operating Pressure = 0 Pa` through the correct 2026 R1 API path rather than relying on the current fallback.
- Why first: it is small in scope and removes one of the remaining ambiguity points between the scripted case and the intended baseline.

### Priority 2. Probe the newer solution-method API tree

- Goal: map the exact 2026 R1 object paths for:
  - pressure-velocity coupling
  - pressure discretization
  - momentum discretization
  - volume-fraction discretization
  - `k` and `epsilon` discretization
- Why next: this is the main remaining gap between `runnable setup` and `clean scripted baseline reproduction`.

### Priority 3. Save case and data after a short stable run

- Goal: extend from current `.cas.h5` writing to a paired short-run `.dat.h5` save.
- Why useful: this would give a faster restart point for future scripting and debugging passes.

### Priority 4. Add immediate report extraction after the smoke test

- Goal: automatically print inlet/outlet phase mass-flow checks after initialization or after the first few iterations.
- Why useful: this gives early sanity evidence before spending time on longer runs.

### Priority 5. Optional controlled longer test

- Goal: increase from `10` iterations to a modest controlled run only after the operating-pressure and numerics-path caveats are better understood.
- Why later: longer runs are still worth less than removing the remaining script ambiguity first.

## Recommendation For The Next Setup Pass

Use the current script and report as the new starting point:

- the environment works;
- mesh-only reconstruction works;
- manual water-property definition works;
- hybrid initialization works;
- a short steady smoke test works.

So the next pass should focus narrowly on:

1. clean operating-pressure control,
2. correct 2026 R1 numerics API paths,
3. automatic mass-flow sanity reporting,
4. then only after that, slightly longer controlled runs.

## Linked Artifacts

- Script: `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`
- Mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial3.msh`
- Output case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial3-purnanto-recon.cas.h5`
- Setup branch definition: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`
