# PyFluent One-Inlet Reconstruction Smoke Test

## Purpose

Record the actual PyFluent setup attempts on the current local one-inlet reconstruction path so the next automation pass can start from working evidence rather than repeating avoidable failure modes.

This page is project-specific technical evidence for the local rebuild path, not a generic Fluent tutorial.

Primary linked setup context:

- `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`
- `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
- `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`
- `../../../PyAnsys/docs/LOCAL_ONE_INLET_SMOKE_TEST.md`

## Scope

- Setup intent: practical one-inlet Purnanto-style recreation
- Goal of these passes: prove Python can launch Fluent locally, load the mesh, build a usable setup, hybrid initialize, advance a short steady run, and then harden the script toward cleaner setup parity
- Out of scope: exact paper parity, DPM, polished convergence, final validation, final separator-efficiency claims

## Evidence Labels

- `Reported`: taken from setup `08` and the live Purnanto audit
- `Observed`: seen directly during the local PyFluent runs on `2026-06-09`
- `Inferred`: interpretation of why a behavior happened
- `Assumed`: recommended next-step fallback where the exact Fluent API path is still uncertain

## Run Sequence Summary

### Pass A. Initial runnable smoke test on `trial3.msh`

- `Observed`: local Fluent launch worked after Fluent and Workbench windows were closed
- `Observed`: `trial3.msh` loaded, boundaries were detected, manual water materials were created, the inlet/outlet package was applied, hybrid initialization succeeded, and a `10`-iteration run completed
- `Observed`: this pass proved the basic workflow was runnable
- `Observed`: key remaining gaps after this pass were:
  - operating pressure was not being set cleanly through the high-level API
  - numerics setters were using the wrong 2026 R1 object paths
  - no automated flux sanity report existed yet
  - only `.cas.h5` was being written

### Pass B. Hardened parity pass on `trial4.msh`

- `Observed`: the same workflow was repeated on `trial4.msh`
- `Observed`: the script now explicitly sets `Operating Pressure = 0 Pa`
- `Observed`: the script now prints the available 2026 R1 solution-method tree before applying numerics
- `Observed`: the intended numerics now apply through the correct 2026 R1 path
- `Observed`: the script now prints mixture and phase mass-flow sanity checks after the short smoke test
- `Observed`: the script now writes both `.cas.h5` and `.dat.h5`

### Pass C. Controlled 500-iteration diagnostic extension on `trial4.msh`

- `Observed`: the current hardened script was extended without replacing the working setup core
- `Observed`: the same one-inlet `trial4.msh` branch was run for `500` steady iterations in chunks of `50`
- `Observed`: checkpoint case/data files were written at iteration `250`
- `Observed`: the script now prints interpreted chunk summaries including:
  - cumulative iteration count
  - raw mixture / phase-1 / phase-2 mass-flow output
  - vapor recovery ratio
  - liquid carryover ratio
- `Observed`: a rough scaled-residual plot was recovered from the Fluent transcript and saved as a PNG plus CSV

## Working Inputs Used

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

### Meshes used in the local tests

- `Observed`: first runnable pass used `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial3.msh`
- `Observed`: hardened parity pass used `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4.msh`

## What Worked

### 1. Local Fluent launch through PyFluent

- `Observed`: `ansys.fluent.core` launched local Fluent successfully after Fluent and Workbench windows were closed
- `Inferred`: the local Student setup is usable for direct local PyFluent automation as long as another ANSYS session is not already occupying licensing/resources

### 2. Mesh-only case load and zone detection

- `Observed`: the script could load `.msh` files directly, inspect boundary-condition state, and detect the key one-inlet / one-outlet / wall zones without needing a prebuilt `.cas.h5`
- `Observed`: `trial4.msh` boundary summary was effectively:
  - inlet: `inlet`
  - outlet: `outlet`
  - walls: `bottom`, `wall`
- `Inferred`: for early automation testing, a mesh path is enough; a case file is not required to prove basic setup control

### 3. Boundary conversion and main model activation

- `Observed`: inlet conversion from `velocity_inlet` to `mass_flow_inlet` worked
- `Observed`: outlet confirmation as `pressure_outlet` worked
- `Observed`: the script successfully enabled:
  - `Mixture`
  - `RNG k-epsilon`
  - energy off
  - phase-2 droplet diameter fallback

### 4. Manual material creation for water vapor and liquid water

- `Observed`: a fresh mesh-only load exposed only `air` as the default fluid material
- `Observed`: PyFluent material creation worked through `solver.settings.setup.materials.fluid.create(...)` plus `set_state(...)`
- `Observed`: the following manual materials were created and assigned successfully:
  - `water-vapor-manual`: density `5.7974339 kg/m3`, viscosity `1.52062e-05 kg/(m s)`
  - `water-liquid-manual`: density `881.21088 kg/m3`, viscosity `0.000145544 kg/(m s)`
- `Inferred`: this is the key workaround that makes a mesh-only PyFluent reconstruction viable even when the saved case materials are unavailable

### 5. Clean operating-pressure control in the hardened pass

- `Observed`: in the hardened `trial4` pass, `Operating Pressure = 0 Pa` set cleanly through:
  - `solver.settings.setup.general.operating_conditions.operating_pressure = 0`
  - `solver.settings.setup.general.operating_conditions.gravity.enable = True`
  - `solver.settings.setup.general.operating_conditions.gravity.components = [0.0, -9.81, 0.0]`
- `Observed`: the resulting state confirmed operating pressure `0` and gravity components `[0.0, -9.81, 0.0]`
- `Inferred`: the earlier error was caused by using the wrong value shape for this 2026 R1 settings path, not by a missing capability

### 6. Correct 2026 R1 numerics path in the hardened pass

- `Observed`: the 2026 R1 numerics tree is:
  - `solution.methods.p_v_coupling.flow_scheme`
  - `solution.methods.spatial_discretization.gradient_scheme`
  - `solution.methods.spatial_discretization.discretization_scheme`
- `Observed`: the intended numerics were applied successfully as:
  - `flow_scheme = SIMPLE`
  - `gradient_scheme = green-gauss-node-based`
  - `discretization_scheme.pressure = presto!`
  - `discretization_scheme.mom = second-order-upwind`
  - `discretization_scheme.mp = quick`
  - `discretization_scheme.k = second-order-upwind`
  - `discretization_scheme.epsilon = second-order-upwind`
- `Observed`: the script now prints the methods tree and before/after state so later debugging can compare what Fluent is actually exposing

### 7. Hybrid initialization and short smoke test

- `Observed`: hybrid initialization completed successfully in both local passes
- `Observed`: the hardened `trial4` case advanced through `10` steady iterations without crashing
- `Observed`: the `trial4` final residual magnitudes at iteration `10` were approximately:
  - continuity: `4.43e-01`
  - `x` velocity: `1.17e-03`
  - `y` velocity: `8.98e-04`
  - `z` velocity: `1.06e-03`
  - `k`: `3.77e-02`
  - `epsilon`: `1.61e-01`
  - `vf-phase-2`: `5.64e-02`
- `Inferred`: this remains a smoke test, not convergence evidence, but it proves the setup is solver-runnable and the hardened parity controls are not obviously broken

### 8. Mass-flow sanity reporting in the hardened pass

- `Observed`: after the `trial4` smoke test, the script printed:
  - mixture mass flow: inlet `197.61`, outlet `-81.47756596537904`, net `116.13243403462097 kg/s`
  - phase-1 mass flow: inlet `80.69`, outlet `-81.47756596537904`, net `-0.7875659653789882 kg/s`
  - phase-2 mass flow: inlet `116.92`, outlet effectively `0`, net `116.92 kg/s`
- `Inferred`: these are early sanity outputs only, but they are useful for immediately checking whether the scripted boundary package is being imposed in the expected direction and magnitude

### 9. Case and data output in the hardened pass

- `Observed`: the hardened run wrote both:
  - `trial4-purnanto-recon.cas.h5`
  - `trial4-purnanto-recon.dat.h5`
- `Inferred`: this gives a better restart and inspection point for the next pass than a case-only write

### 10. Longer controlled one-steam-outlet diagnostic behavior

- `Observed`: the `500`-iteration run completed successfully on the one-steam-outlet branch
- `Observed`: final residual magnitudes at iteration `500` were approximately:
  - continuity: `3.3731e-01`
  - `x` velocity: `3.2375e-04`
  - `y` velocity: `3.3763e-04`
  - `z` velocity: `3.1935e-04`
  - `k`: `2.1085e-03`
  - `epsilon`: `3.8826e-03`
  - `vf-phase-2`: `2.2265e-03`
- `Observed`: final interpreted phase-flow check at iteration `500` was:
  - phase-1 inlet `80.69 kg/s`
  - phase-1 outlet `-81.43119629260137 kg/s`
  - phase-2 inlet `116.92 kg/s`
  - phase-2 outlet `-4.640062523254778e-23 kg/s`
  - vapor recovery ratio `1.009186`
  - liquid carryover ratio `3.968579e-25`
- `Inferred`: under the intended one-steam-outlet interpretation, this is a good practical sign because vapor outlet flow stayed close to vapor inlet flow and liquid outlet flow through the steam outlet remained effectively zero
- `Inferred`: the nonzero total mixture imbalance should not be treated as a failure for this branch because no liquid drain / sink / transient accumulation model is present

### 11. Residual-history artifact recovery

- `Observed`: Fluent's residual monitor object existed in the saved case/data state
- `Observed`: the direct residual write command produced an empty output file on this run
- `Observed`: the full Fluent transcript still contained the per-iteration scaled residual table
- `Observed`: a rough residual-history plot and extracted CSV were therefore generated from the transcript:
  - `trial4-purnanto-recon-500-residuals.png`
  - `trial4-purnanto-recon-500-residuals.csv`
- `Inferred`: this is still based on Fluent's own residual history, just pulled from the transcript rather than the empty residual-export file

## Troubles And Workarounds

### Trouble 1. Fluent/Workbench already open blocked clean local testing

- `Observed`: earlier retries failed until existing Fluent/Workbench windows were closed
- `Workaround used`: close active ANSYS GUI sessions first, then relaunch the PyFluent script
- `Why it likely helped`: `Inferred` licensing/session conflicts or already-busy local resources were interfering with fresh local launch

### Trouble 2. Earlier candidate mesh paths added avoidable uncertainty

- `Observed`: `.meshdat` and `.mshdb` attempts were less straightforward than the direct exported `.msh` route
- `Workaround used`: switch to plain exported mesh files and keep the current hardened pass on `trial4.msh`
- `Why it helped`: `Inferred` the plain `.msh` path reduced uncertainty around what Fluent could read directly through the tested API

### Trouble 3. Mesh-only case had no usable water materials

- `Observed`: material lookup initially failed because only `air` existed in the new mesh-loaded session
- `Workaround used`: manually create fluid materials and assign density and viscosity values directly in PyFluent
- `Why it helped`: this removed dependence on a pre-existing Fluent material database entry or a prebuilt case file

### Trouble 4. Earlier operating-pressure call used the wrong value form

- `Observed`: the earlier script used a dictionary-style value for `operating_pressure`, which triggered a range error in the local smoke-test path
- `Workaround used`: set `operating_pressure` as a scalar integer `0` instead
- `Why it helped`: `Inferred` this matches the actual 2026 R1 settings object expectation

### Trouble 5. Earlier numerics setters targeted the wrong API layer

- `Observed`: direct setters for `pressure`, `momentum`, `volume_fraction`, `k`, and `epsilon` failed when treated as top-level `methods` attributes
- `Workaround used`: probe the live methods tree first, then set them through `spatial_discretization.discretization_scheme`
- `Why it helped`: this matches the current Fluent 2026 R1 object layout

### Trouble 6. Report API availability depends on model/run activation

- `Observed`: flux-report calls were inactive in earlier probes before the relevant model/run state was active
- `Workaround used`: run the short initialization/iteration path first, then call `results.report.fluxes.get_mass_flow(...)`
- `Why it helped`: `Inferred` the report object becomes usable once the case is in the right active state

### Trouble 7. Pressure-outlet subsettings were partly inactive at assignment time

- `Observed`: Fluent still reported some pressure-outlet momentum/turbulence settings as inactive when the state was applied
- `Workaround used`: accept the applied state where Fluent allowed it and continue with the short parity run
- `Inferred`: this may be due to setting-order sensitivity, inactive panels for the current model state, or version-specific state-shape differences

### Trouble 8. First 500-iteration attempt failed because the settings path already worked

- `Observed`: the first diagnostic extension failed early because `set_operating_conditions()` fell through into the older Scheme fallback even after the high-level settings path had succeeded
- `Workaround used`: restore the immediate return after successful high-level operating-condition assignment
- `Why it helped`: `Inferred` the failure was a script-control bug, not a Fluent modelling failure

### Trouble 9. Built-in residual write produced an empty file

- `Observed`: `solution.monitor.residual.write(...)` created an empty output file for this case
- `Workaround used`: recover the per-iteration residual history from the Fluent transcript instead
- `Why it helped`: the transcript contained the full scaled-residual table even though the residual export file did not

## Current Known Caveats

1. `Observed`: the main operating-pressure and numerics-path issues are now resolved in the script
2. `Observed`: pressure-outlet momentum/turbulence subsettings still show partial inactivity at assignment time
3. `Observed`: the built-in residual write path was not reliable on this run, so transcript recovery was needed for the rough residual plot
4. `Observed`: the mass-flow sanity output is useful for setup checking, but it is not yet a full report-quality balance workflow
5. `Observed`: the `500`-iteration run should still be treated as a controlled diagnostic only, not as convergence, validation, separator efficiency, or paper parity evidence
6. `Assumed`: local Student licensing and already-open ANSYS sessions may continue to affect repeatability if the environment is not clean before launch

## Best Current Practical Workflow

1. Close Fluent and Workbench before launching the script
2. Use `trial4.msh` as the current hardened local parity mesh
3. Build the case from the one-inlet setup `08` logic
4. Create manual water vapor and liquid water materials inside PyFluent
5. Apply the one-inlet mass-flow package and one pressure outlet
6. Explicitly set `Operating Pressure = 0 Pa` and gravity through the high-level operating-conditions object
7. Print the 2026 R1 solution-method tree before applying numerics
8. Apply the numerics stack through `spatial_discretization.discretization_scheme`
9. Use hybrid initialization
10. Use short smoke tests for setup hardening, then controlled chunked runs for longer diagnostics
11. Print mixture and phase mass-flow sanity checks plus interpreted vapor-recovery and liquid-carryover summaries
12. Save both case and data, with checkpointing only at deliberate intervals

## Improvement Points To Try Next

### Priority 1. Clarify pressure-outlet setting inactivity

- Goal: find out whether the inactive pressure-outlet momentum/turbulence subsettings are harmless state-shape noise or whether a slightly different setting order is needed
- Why first: this is the main remaining setup-write ambiguity in the hardened script

### Priority 2. Add a cleaner balance report

- Goal: expand from raw mass-flow sanity numbers into a short structured balance printout with simple interpreted checks
- Why next: the current output is useful, but still fairly raw

### Priority 3. Save a compact restart or checkpoint workflow

- Goal: decide whether the script should save only the final `.cas.h5` and `.dat.h5` pair or also write an earlier checkpoint for debugging
- Why useful: this can make repeated short parity tests faster to inspect

### Priority 4. Investigate why Fluent residual write was empty

- Goal: determine whether a different residual export command or monitor option is needed so future runs can export residual history directly
- Why useful: this would avoid depending on transcript parsing for quick residual plots

### Priority 5. Only then consider slightly longer controlled runs

- Goal: extend the smoke test only after the remaining pressure-outlet ambiguity is understood
- Why later: the current objective is reproducible setup parity, not convergence

## Recommendation For The Next Setup Pass

Use the current hardened script and `trial4` outputs as the new local baseline:

- the environment works
- mesh-only reconstruction works
- manual water-property definition works
- operating pressure and gravity now set cleanly
- the 2026 R1 numerics path is now identified and applied correctly
- hybrid initialization works
- a short steady smoke test works
- mixture and phase mass-flow sanity output now exists
- both case and data files are now written
- a controlled `500`-iteration one-steam-outlet diagnostic run has completed
- vapor recovery stayed close to one while liquid carryover stayed effectively zero
- a rough scaled-residual plot is now available from the run transcript

So the next pass should focus narrowly on:

1. pressure-outlet setting-order cleanup,
2. slightly cleaner balance reporting,
3. direct residual export cleanup if possible,
4. then only after that, modest controlled extensions of the current diagnostic path.

## Linked Artifacts

- Script: `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`
- First runnable mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial3.msh`
- Hardened parity mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4.msh`
- Hardened output case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.cas.h5`
- Hardened output data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.dat.h5`
- 500-iteration diagnostic case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.cas.h5`
- 500-iteration diagnostic data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.dat.h5`
- 500-iteration diagnostic log: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500-log.txt`
- Residual plot: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500-residuals.png`
- Residual CSV: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500-residuals.csv`
- Setup branch definition: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`
