# Successful Fluent Paths Log

Add working paths/orders here as the agent discovers them in the live Fluent session.

Run-policy note: the client-loop and Python-checkpoint entries retained below are historical
evidence only. They are superseded and must not be used for current long runs. Current runs
must use Fluent-native initialization, iteration, and Calculation Activities / Autosave; see
`../native_run_and_autosave.md`.

## Example format

```text
Fluent: 2024 R2
PyFluent: <version>
Case: <case>
Goal: bind DPM injection surface to steaminlet
Order:
  1. enabled DPM
  2. created default injection
  3. reacquired injection object
  4. set particle_type = inert
  5. reacquired injection object
  6. set injection_type = surface
  7. reacquired injection object
  8. set location/surface = <working format>
Working path or TUI:
  <path or command>
Readback:
  <value>
Notes:
  <notes>
```

Fluent: 2025 R2
PyFluent: 0.39.0 local `.venv`
Case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z.cas.h5`
Goal: materialize and full-path reload-verify the 03A 08b-parity full-geometry steady carrier case without initialization or solving
Order:
  1. connect to the reachable `student` server through Fluent gRPC and verify Fluent 2025 R2 is active;
  2. verify and load `Full-geomV2-231kcells.msh.h5`, then read back the five required boundary zones;
  3. set pressure-based steady operation, gravity, `0 Pa` operating pressure, psep materials, Mixture carrier, RNG k-epsilon, differential viscosity, swirl, and standard wall functions;
  4. assign the automatically exposed phase-1 vapour / phase-2 liquid pair without forcing the inactive phase-count setter;
  5. activate inlet/outlet turbulence specification before reacquiring the boundary objects, then set the split pure-phase velocity inlets and two pressure outlets;
  6. set the target SIMPLE, PRESTO!, second-order/QUICK, under-relaxation, residual, initialization, and DPM-guard controls;
  7. write only the case, reload it by full remote path, and compare the normalized contract.
Working path or TUI:
  Mixture activation automatically exposed `phase-1` and `phase-2`; setting the inactive `number_of_phases` branch is not valid on this Student build. Boundary turbulence specification had to be selected before turbulent intensity/hydraulic-diameter fields became writable. Reloaded solution methods were under `spatial_discretization`.
Readback:
  The case contract matched after full-path reload. A gRPC `remote_file_exists` readback confirmed the case exists and the matching `.dat.h5` does not. Fluent read back `231376` cells, inlet areas `0.0048896664` and `0.51928634 m2`, outlet areas `0.60094806` and `0.20143996 m2`, minimum orthogonal quality `0.200006`, and maximum aspect ratio `82.6482`. No initialization, iteration, or DPM injection was created.
Notes:
  The Student operating-temperature and Mixture phase-interaction branches were inactive, so no value was guessed. Outlet wetted perimeters/hydraulic diameters remain a native preflight item; the provisional Dh values were used only to materialize the case. Do not use this entry as evidence that the setup is run-ready.

Fluent: 2025 R2
PyFluent: 0.39.0 local `.venv`
Case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z.cas.h5`
Goal: run the requested 03A native 1,000-iteration diagnostic checkpoint and verify the paired endpoint over gRPC
Order:
  1. connect to `student` through Fluent gRPC and verify the case-only input exists;
  2. write a run-specific native journal through the Fluent Scheme channel;
  3. submit the journal with `solver.settings.file.read_journal`, leaving Fluent responsible for Hybrid Initialization, `/solve/iterate 1000`, transcript, residual export, and paired case/data write;
  4. reconnect through gRPC, verify the endpoint case/data/transcript/residual/journal files, reload the endpoint, and run read-only flux/residual checks.
Working path or TUI:
  Native journal sequence: `/file/read-case` → `/solve/initialize/hyb-initialization` → `/solve/iterate 1000` → `/file/write-case-data` → residual export → `/file/stop-transcript`. Python did not loop over iterations or perform checkpoint timing.
Readback:
  Exactly `1,000` residual points were recovered. Final residuals were continuity `1.6043e-1`, `vf-phase-2 = 6.5142e-3`, velocity components approximately `1.5–1.7e-4`, `k = 5.2127e-3`, and epsilon `2.2262e-1`. The paired endpoint was visible and reloadable; phase-flux extraction included both pressure outlets and reported a `34.0758 kg/s` (`17.17%`) diagnostic full-domain balance residual.
Notes:
  The run completed without a floating-point exception but is not converged or qualified: reverse flow persisted on `334` outlet faces and turbulent-viscosity limiting occurred. Do not continue to 03B from this endpoint. All Student interaction for this run used Fluent gRPC; no SSH was used.

Fluent: 2025 R2
PyFluent: 0.39.0 local `.venv`
Case: `C:\Users\syok443\P4P simulation\VOF-IC0-P1120-preinit-20260814T000000Z.cas.h5`
Goal: build and reload-verify a no-patch explicit-VOF case from `brine-outlet-620kcells.msh.h5`
Order:
  1. load the mesh by the current-working-directory-relative name after Fluent confirms it exists;
  2. set pressure-based `unsteady-1st-order` (not the invalid literal `transient`), gravity, and `0 Pa` operating pressure;
  3. create constant `water-vapor` / `water-liquid` materials, then set `models.multiphase.model = "vof"`;
  4. assign phase-1 / phase-2 materials with the documented phase-domain TUI commands;
  5. set the VOF boundary phase fractions/backflow fractions only after VOF phases exist;
  6. set `pressure = presto!` and `mp = geo-reconstruct`, write only a case, reload it, and audit the contract.
Working path or TUI:
  `setup.general.solver.time = "unsteady-1st-order"`
  `setup.models.multiphase.model = "vof"`
  `setup.models.multiphase.vof_parameters` readback gives `vof_formulation = explicit`, `interface_type = sharp`, and `vof_courant_number = 0.25`.
  Phase material TUI: `/define/phases/set-domain-properties/phase-domains/phase-1/material yes water-vapor` then the equivalent phase-2 `water-liquid` command.
Readback:
  Fluent found the mesh under `C:\Users\syok443\P4P simulation`; it has `620431` cells and named `liquid-inlet`, `steam-inlet`, `brine-outlet`, and `steam-outlet` zones. The reloaded child preserved explicit/sharp VOF, Geo-Reconstruct, PRESTO!, RNG k-epsilon, the equal `1120000 Pa` outlet pressures, and the specified phase fractions.
Notes:
  Explicit VOF with the Fluent 2025 R2 unsteady first-order setting exposes a default `1 s` transient-control value. It is not a valid production timestep and must remain unset pending mesh/Courant assessment. This build did not initialize, patch, iterate, write data, or enable DPM interaction/EWF.

Fluent: 2026 R1 Student
PyFluent: 0.39.0
Case: purnanto-extended.msh -> setup09a student smoke
Goal: launch local Student Fluent from Python and apply setup07/setup09a value-setting path
Order:
  1. start fluent.exe manually with `-g -sifile=...`
  2. keep the Fluent child process stdin open from Python
  3. connect with `connect_to_fluent(server_info_file_name=...)`
  4. read mesh
  5. set general + mixture + turbulence carrier settings
  6. initialize and iterate carrier field
  7. create inert particle material
  8. create DPM injections and set particle/material/location/size/mass-flow values
  9. write final case/data
Working path or TUI:
  Local manual launch is more reliable than `launch_fluent()` / `Solver.from_install()` for this Student-edition SSH-driven path because Fluent otherwise halts on stdin EOF after starting the server.
Readback:
  `check_connection.py --server-id 2` reached `Health check: Status.SERVING`
  `setup09a_dpm_split_inlet_carryover.py --apply --server-id 2` completed with created injections:
  `dpm-5um`, `dpm-10um`, `dpm-14.2um`, `dpm-41um`
Notes:
  After setting `models.multiphase.model = "mixture"`, this build already exposed two phases, so forcing `number_of_phases = 2` caused `ASSQ: invalid argument [2]: improper list`.

Fluent: 2024 R2
PyFluent: local `.venv` on repo laptop
Case: `PureTwoPhaseV2(PurnantoV2)-setup09a-100iter.cas.h5`
Goal: rebuild setup 07 carrier field on server `3` and bind 09a DPM surface injections to `steaminlet`
Order:
  1. connect with `check_connection.py --server-id 3`
  2. verify remote mesh path
  3. read mesh
  4. set `models.multiphase.models = "mixture"`
  5. skip explicit phase-count setter because readback already reports `number_of_phases = 2`
  6. assign phase materials and run `100` carrier iterations
  7. create inert-particle material `water-droplet`
  8. create default DPM injections and set particle/material/type fields
  9. isolate `initial_values.location.injection_surfaces` in a probe injection
Working path or TUI:
  On this build, the carrier-field multiphase path is `setup.models.multiphase.models`, not `setup.models.multiphase.model`.
Readback:
  After carrier setup, `models.multiphase.get_state()` returned `{'models': 'mixture', 'number_of_phases': 2}`.
  `location` after `injection_type = surface` exposed active children `injection_surfaces`, `randomized_positions_enabled`, and `number_of_streams`.
  A fresh mesh-start replay with `--carrier-iterations 1` saved:
  `C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files\PureTwoPhaseV2(PurnantoV2)-setup09a-subagents.cas.h5`
  `C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files\PureTwoPhaseV2(PurnantoV2)-setup09a-subagents.dat.h5`
  In that saved case, all four injections existed, but each read back as:
  `{'injection_surfaces': False, 'randomized_positions_enabled': False}`.
Notes:
  `injection_surfaces` failed through all tested settings paths on server `3`:
  - `StringList.set_state("steaminlet")`
  - `SettingsBase.set_state(["steaminlet"])`
  - `location.set_state({"injection_surfaces": ...})`
  - direct Scheme `api-set-var` attempts with string lists, symbol lists, and alists
  - TUI `/define/models/dpm/injections/injection-properties/set/pick-injections-to-set dpm-5um` entered an interactive loop and spammed the injection list, so it is not safe as a naive batch fallback
  The script now logs explicit `*_location_readback: FAILED -> {'injection_surfaces': False, ...}` lines, which makes the false-positive partial-success condition visible during live runs.
  Failure signature stayed in the DPM surface-location category:
  - `wta(1st) to string->symbol`
  - `wta(1st) to symbol->string`
  - `ASSQ: invalid argument [2]: improper list`
  Current diagnosis: likely `PyFluent wrapper limitation` or `path/version issue` specific to the 2024 R2 DPM surface selector on this server build. Keep using the carrier-field rebuild path above, but isolate the injection-surface bind as a dedicated fallback problem rather than rerunning the full setup.

Update 2026-06-12:
  `scripts/setup/simple_dpm_test.py --server-id 3 --snapshot-json output/simple_dpm_test_summary.json` reproduced the same surface-selector failure on Fluent 2024 R2 without crashing. The live branch reported `initial_values.location.injection_surfaces` active with allowed values `['bottom', 'wall', 'liquidinlet', 'steaminlet', 'steamoutlet']`, but all Settings API write strategies still failed with `wta(1st) to string->symbol` or `value`; the helper now classifies this non-strict path as `PyFluent wrapper limitation`, marks DPM injection setup unsuccessful, and still writes the case for inspection.

Fluent: 2026 R1 Student
PyFluent: `.venv` on Windows SSH target
Case: `purnanto-extended.msh`
Goal: probe carrier multiphase + global DPM activation before any injection setup
Order:
  1. start local Student Fluent with `fluent.exe 3ddp -t2 -g -sifile=<server_info>`
  2. connect with `connect_to_fluent(server_info_file_name=...)`
  3. load mesh `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended.msh`
  4. apply carrier general settings
  5. apply carrier multiphase model settings
  6. enable DPM and apply global DPM tracking settings
  7. capture `setup.models.multiphase` and `setup.models.discrete_phase` against the archived 07 seed JSON
Working path or TUI:
  Student PC repo root: `C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys`
Readback:
  `carrier_general: True`
  `carrier_models: True`
  `dpm_model_settings: True`
  `multiphase_state` stayed active with `models = mixture` and `number_of_phases = 2`
  `discrete_phase` stayed active, with DPM globals applied successfully
Notes:
  The archived `07` seed exposes many inactive multiphase and DPM branches that this Student build does not activate. That mismatch is useful: it tells us which paths are build-sensitive before we attempt any injection-level writes.

Fluent: 2026 R1 Student
PyFluent: `.venv` on Windows SSH target
Case: `purnanto-extended.msh`
Goal: adaptive recursive exploration of a live Fluent settings branch
Order:
  1. start local Student Fluent with `fluent.exe 3ddp -t2 -g -sifile=<server_info>`
  2. connect with `connect_to_fluent(server_info_file_name=...)`
  3. load mesh `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended.msh`
  4. explore `setup.models.energy` with adaptive parent activation enabled
  5. record the activation attempt and the refreshed state
Working path or TUI:
  Generic explorer: `scripts/inspection/explore_settings_space.py`
Readback:
  `enabled=True` was applied to the energy branch during adaptive capture
  `activation_state` was present in the JSON capture
Notes:
  This proves the new explorer can flip a known parent toggle and rescan the branch. It does not magically invent unsupported build-specific children, but it can widen the visible tree when the parent activation is enough to expose more settings.
  Seed-guided retries against the archived `energy.two_temperature` branch on Fluent 2026 R1 Student still did not activate the nested child. The live capture reported the branch as present but `cycle_detected`, which means the generic recursive walker can see the name but still needs a build-specific activation rule before it can recurse into that subtree.

Fluent: 2024 R2
PyFluent: `.venv` on repo laptop
Case: `enthalpy1680.cas` -> `TwoPhaseInlet(PurnantoExtended).msh`
Goal: export setup settings from an existing case and import them onto a different mesh
Order:
  1. connect with `check_connection.py --server-id 2`
  2. read `C:\Users\syok443\Documents\Purnanto\enthalpy1680.cas`
  3. write settings with `solver.tui.file.write_settings(<settings-file>)`
  4. read `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInlet(PurnantoExtended).msh`
  5. read settings with `solver.tui.file.read_settings(<settings-file>)`
  6. write case-only checkpoint for GUI review
Working path or TUI:
  `scripts/setup/probe_settings_transfer.py --server-id 2 --yes --write-output-case --summary-json output/settings_transfer_probe_summary.json`
Readback:
  Settings export created `C:\Users\syok443\Documents\Purnanto\enthalpy1680-settings-transfer-20260616-093310.set`.
  Settings import changed the target mesh setup to Mixture/RNG k-epsilon.
  Output case written to `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInlet(PurnantoExtended)-settings-transfer-20260616-093310.cas.h5`.
Notes:
  The command is useful for accelerating setup reuse but does not solve topology/name mismatch. Fluent applied matching zones (`fluid`, `interior-fluid`, `bottom`) and skipped missing original zones (`inlet`, `outlet`, `wall-fluid`). New target zones (`liquidinlet`, `steaminlet`, `steamoutlet`, `wall`) received default settings and must be inspected or patched afterward.

Fluent: 2024 R2
PyFluent: `.venv` on repo laptop
Case: `C:\Users\syok443\Documents\Purnanto\enthalpy1680.cas.h5`
Status: historical path, superseded by Fluent-native run/autosave
Goal: load a case-only `.cas.h5` and produce a data file for a one-off diagnostic
Order:
  1. connect with `check_connection.py --server-id 2`
  2. verify remote case path exists
  3. read case with `solver.settings.file.read_case(file_name=...)`
  4. hybrid-initialize and run a one-off diagnostic from the connected client
  5. write data and verify the output
Working path or TUI:
  Retired `save_data_after_iterations.py` client workflow; do not use.
Readback:
  Test command completed for `iterations = 1` and wrote:
  `C:\Users\syok443\Documents\Purnanto\enthalpy1680_1.dat.h5`
Notes:
  This was a one-off historical diagnostic. It is retained to explain the old artifact, not as
  a reusable run procedure. Current workflows configure native autosave and disconnect safely.

Fluent: 2024 R2
PyFluent: `.venv` on repo laptop
Case: `C:\Users\syok443\Documents\Purnanto\enthalpy1680.cas.h5`
Status: historical path, superseded by Fluent-native run/autosave
Goal: run the lightweight case-to-data diagnostic with TUI commands only on server `4`
Order:
  1. connect with `check_connection.py --server-id 4`
  2. verify remote case path exists
  3. run `/file/read-case "<case>"`
  4. run `/solve/initialize/hyb-initialization`
  5. run the short diagnostic from the connected client
  6. run `/file/write-data "<output>"`
  7. verify the output `.dat.h5` is visible to Fluent
Working path or TUI:
  Retired `save_data_after_iterations.py` client workflow; do not use.
Readback:
  Test command completed for `iterations = 2` and wrote:
  `C:\Users\syok443\Documents\Purnanto\enthalpy1680_2.dat.h5`
Notes:
  This was a one-off historical diagnostic. Native Fluent run/autosave is the current recovery
  path; do not recreate the old Python chunking wrapper.

Fluent: 2024 R2
PyFluent: local `.venv` on repo laptop
Case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5`
Goal: derive setup `09c` as a case-only two-way DPM coupling branch on server `3`
Order:
  1. connect with `check_connection.py --server-id 3`
  2. read the source case with `solver.settings.file.read_case(file_name=...)`
  3. inspect `setup.models.discrete_phase.general_settings.interaction`
  4. set `interaction.enabled = true`
  5. set `interaction.update_sources_every_iteration = true`
  6. set `interaction.iteration_interval = 1`
  7. read back the interaction state
  8. write only `.cas.h5`
Working path or TUI:
  On Fluent 2024 R2 server `3`, the writable branch is:
  `setup.models.discrete_phase.general_settings.interaction`
Readback:
  Before mutation: `{'enabled': false}`
  After mutation: `{'enabled': true, 'iteration_interval': 1, 'update_sources_every_iteration': true}`
  The inherited case already carried 6 active `surface` injections on `steaminlet` with `29.22 kg/s` represented total injected loading.
Notes:
  This path did not require rebuilding injections or changing boundary DPM fates. It is a clean derivative of the accepted split-inlet case with only the two-way coupling controls changed.

Fluent: 2024 R2
PyFluent: local `.venv` on repo laptop
Case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5`
Goal: create setup `08c` case-only inlet-velocity sensitivity endpoints from the accepted `08b` split mass-flow inlet case
Order:
  1. connect with `setup08c_purnanto_velocity_sensitivity_cases.py --server-id 2`
  2. read the source `08b` case with `solver.settings.file.read_case(file_name=...)`
  3. inspect `setup.boundary_conditions.mass_flow_inlet` object names and require `liquidinlet` plus `steaminlet`
  4. read the two inlet states before mutation
  5. set `liquidinlet` `phase-2` mass-flow rate and zero `phase-1` where exposed
  6. set `steaminlet` `phase-1` mass-flow rate and zero `phase-2` where exposed
  7. read back the phase-specific mass-flow values
  8. write only `.cas.h5`
  9. reload the original source case before applying the next endpoint
Working path or TUI:
  `scripts/setup/setup08c_purnanto_velocity_sensitivity_cases.py --server-id 2`
Readback:
  `08c-v20p00`: `liquidinlet` `phase-2 = 86.18 kg/s`, `steaminlet` `phase-1 = 60.21 kg/s`, opposite phases `0.0 kg/s`
  `08c-v32p14`: `liquidinlet` `phase-2 = 138.48 kg/s`, `steaminlet` `phase-1 = 96.76 kg/s`, opposite phases `0.0 kg/s`
  Output cases:
  `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-08c-v20p00.cas.h5`
  `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-08c-v32p14.cas.h5`
Notes:
  This path deliberately avoids initialization, iteration, and data writes. The local summary JSON is `PyAnsys/output/setup08c_velocity_sensitivity_cases_summary.json`.

Fluent: 2024 R2
PyFluent: local `.venv` on repo laptop
Case/data: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\08c different speeds\TwoPhaseInletV2(Purnanto)-08c-v20p00.cas.h5` with `TwoPhaseInletV2(Purnanto)-08c-v20p00-25-03088.dat.h5`
Goal: verify the six reference DPM injections before running legacy Particle Tracks Summary reports
Order:
  1. connect with `run_dpm_particle_tracks.py --server-id 1`
  2. load the explicit case/data pair, or use `--already-loaded` after a large case read
  3. inspect `setup.models.discrete_phase.injections`
  4. read back each injection diameter and require the reference values
  5. configure `/display/set/particle-tracks` with Summary, screen, and display off
  6. invoke the legacy `/display/particle-tracks` command through Scheme
Readback:
  All six names were present and matched: `5.63`, `28.14`, `56.27`, `112.54`, `168.811`, and `348.88` um.
Notes:
  Fluent 2024 R2 accepts `screen` rather than `console` for the report destination. The generated nested PyFluent `particle_tracks` wrapper was classified as `PyFluent wrapper limitation` after an empty probe terminated the parallel Fluent session; do not call that wrapper. The safe runner uses the direct Scheme/TUI command and keeps the command signature isolated for live validation after Server 1 is restarted.

Fluent: 2024 R2
PyFluent: local `.venv` on repo laptop
Case/data: active Server 1 session with `TwoPhaseInletV2(Purnanto)-08c-v20p00.cas.h5` and `TwoPhaseInletV2(Purnanto)-08c-v20p00-25-03088.dat.h5`
Goal: dynamically discover and track every live DPM injection with Particle Tracks Summary
Order:
  1. connect with `run_dpm_particle_tracks.py --server-id 1`
  2. assume the target case/data are already loaded unless `--load-case-data` is explicitly supplied
  3. inspect `setup.models.discrete_phase.injections` and record live index, name, diameter, material, particle type, and surface
  4. configure `/display/set/particle-tracks` with Summary, screen, and display off
  5. invoke `/display/particle-tracks particle-tracks mixture particle-resid-time "<injection-name>" () 0 0` through Scheme/TUI
  6. parse the Summary counts; omitted zero-valued fate rows are recorded as zero
Readback:
  All six live injections were discovered and tracked successfully in diameter order: `injection-5-micron` (2170 tracked, 851 trapped, 1318 incomplete), `injection-28-micron` (2170, 1010 trapped, 1160 incomplete), `injection-56-micron` (2170, 1160 trapped, 1010 incomplete), `injection-112-micron` (2170, 1301 trapped, 869 incomplete), `injection-168-micron` (2170, 1415 trapped, 755 incomplete), and `injection-348-micron` (2170, 1621 trapped, 549 incomplete).
Working path or TUI:
  `scripts/inspection/run_dpm_particle_tracks.py --server-id 1 --order diameter-ascending --keep-going`
Notes:
  Injection names are the stable audit identity. Indices are discovered from the current live session and are only a selection convenience. The runner does not require hardcoded names or diameters, does not mutate the case, and does not write case/data files.

Fluent: 2025 R2
PyFluent: local `.venv` on repo laptop
Case/data: unavailable; only a non-mutating connection health check was performed
Goal: verify the named Windows Student Edition pool endpoint
Order:
  1. configure `STUDENT_IP`, `STUDENT_PORT`, and `STUDENT_PASSWORD` in `.env`
  2. run `scripts/connection/check_connection.py --server-id student`
  3. read `health_check.status()`, `health_check.check_health()`, and the Fluent version
Working path or TUI:
  `scripts/connection/check_connection.py --server-id student`
Readback:
  Both health calls returned `Status.SERVING`; the connected server reported `Ansys Fluent 2025 R2`.
Notes:
  `student` is only a transport-routing alias and does not establish the active case identity. The current Student endpoint uses insecure gRPC, so PyFluent emits its insecure-connection warning; keep its configuration scoped to a trusted network or supply a TLS-capable server configuration.

Fluent: 2025 R2 Student
PyFluent: 0.39.0
Case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5`
Goal: build the documented 5% `09cV2` allocation as a velocity-inlet adaptation from the already-loaded Student case
Order:
  1. connect with `build_09cV2_student_velocity_adaptation.py --server-id student`
  2. read back `velocity_inlet` topology and confirm `mass_flow_inlet` is inactive
  3. write a full-path pre-build recovery case before mutation
  4. scale `liquidinlet` water-liquid velocity from `27.118` to `25.7621 m/s`
  5. copy `water-liquid` to fallback fluid material `water-liquid-at-psep`
  6. create inert-particle material `water-liquid-at-psep-dpm` with the copied density
  7. enable DPM interaction, source update every flow iteration, and interval `1`
  8. set `bottom = trap`, keep `wall-fluid = reflect`, and verify inlet/outlet `escape`
  9. create six surface injections, then set particle type/material/type/location/flow/diameter/velocity/physical models sequentially
  10. remove the two anthracite placeholders and read back the exact six-injection total `5.846 kg/s`
  11. write only the case, reload it by full Windows path, and repeat the strict audit
Working path or TUI:
  Settings paths confirmed on Student 2025 R2:
  `setup.models.discrete_phase.general_settings.interaction`
  `setup.models.discrete_phase.injections.<name>`
  `setup.boundary_conditions.velocity_inlet.liquidinlet.phase.water-liquid.momentum.velocity_magnitude`
Readback:
  liquid velocity `25.7621 m/s`; steam velocity `27.118 m/s`; DPM interaction/source update/interval `True/True/1`; six injections on `steaminlet`; DPM total `5.846 kg/s`; fallback materials present; wall fates `bottom=trap`, `wall-fluid=reflect`, inlets/outlet=`escape`.
Notes:
  This is a diagnostic velocity-inlet derivative, not an exact historical mass-flow-parent recreation. The five-percent fraction is assumed, the exact mass-flow closure was unavailable, and the EWF material pair is a fallback copy. Full Windows paths are required for post-save reloads; bare relative names can fail after Fluent changes its working directory.

Fluent: 2025 R2 Student
PyFluent: 0.39.0
Case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`
Goal: build the `09cV3` fine-mist PSD child from the read-back-verified Student `09cV2` velocity-inlet adaptation
Order:
  1. load the parent by its full Windows path and confirm split velocity-inlet topology, six legacy injections, inherited DPM material, wall fates, and `True/True/1` DPM interaction/source-update/interval settings
  2. write a full-path recovery case before mutation
  3. create seven surface injections on `steaminlet`, reacquiring the injection object after each dependency-sensitive setter
  4. inherit velocity, location, particle material, drag, deterministic tracking, rotation, and turbulent-dispersion settings from the parent exemplar while changing only representative diameter, name, and flow
  5. remove the six legacy injections from the copied child branch and require exactly seven remaining active injections with a `5.846000 kg/s` read-back sum
  6. write only the child case, reload it by full Windows path, and repeat the strict audit
Working path or TUI:
  `scripts/setup/build_09cV3_student_finemist_from_09cV2.py --server-id student`
Readback:
  Seven active fine-mist surface injections on `steaminlet`; Fluent 2025 R2 serializes the requested `09cV3` identities as lowercase `09cv3-finemist-*`; flows are `0.409128`, `1.165149`, `1.267410`, `1.092501`, `1.329262`, `0.468606`, and `0.113944 kg/s`, totaling `5.846000 kg/s`.
Notes:
  The output is a case-only diagnostic child; no initialization, flow iterations, data read, or `.dat.h5` write was performed. The parent remains untouched. The child preserves the parent velocity-inlet adaptation caveat: `111.074000 kg/s` is an input allocation reference, not an independently verified live mass-flow report. The provisional seven-bin PSD is an assumed engineering prior, not measured inlet data. Full Windows paths are required for strict post-save reloads.

Fluent: 2025 R2 Student
PyFluent: 0.39.0
Case/data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-iter50.cas.h5` + matching `.dat.h5` checkpoint
Status: historical client-orchestration test, superseded by Fluent-native run/autosave
Goal: test a 09cV3 fine-mist child with paired case/data checkpoints
Order:
  1. load the explicit 09cV3 child and independently audit it against the explicit 09cV2 Student parent lineage
  2. hybrid-initialize and run a short connected-client diagnostic
  3. save a paired case/data checkpoint and verify both remote files
  4. reload the checkpoint and inspect the resumed state
Working path or TUI:
  Retired `run_09cV3_student_50_then_100.py` client worker; do not use.
Readback:
  First stage completed at 50 iterations. At the saved checkpoint, continuity was `6.4197e-1`; x/y/z velocity residuals were `7.1907e-4 / 6.6254e-4 / 6.6994e-4`; `k = 7.5132e-3`; epsilon `1.5149e-2`; water-liquid-VF residual `1.2477e-2`. DPM monitor output showed `21,581` tracked, `20,928` escaped, `650` trapped, and `3` incomplete; reversed flow was reported on 35 pressure-outlet faces.
Notes:
  The user stopped the resumed stage during the 51–60 chunk after the transcript reached 51–59. No iteration-100 case/data pair was written. The live session was explicitly restored from the saved iteration-50 pair. Iteration-50 monitor counts are diagnostic flow-iteration output, not a completed per-injection fate report or convergence claim. This entry is retained as a failure-mode record; current long runs use Fluent-native autosave so a client disconnect does not stop checkpoint ownership.

Fluent: 2025 R2
PyFluent: local `.venv` on repo laptop
Case: `C:\Users\syok443\P4P simulation\09cV3-fDPM-05pct-finemist-5to100um.cas.h5`
Goal: build the `09cV3` fine-mist PSD child from the explicitly named server-1 mass-flow `09cV2` case
Order:
  1. connect with `build_09cV3_mass_flow_from_09cV2.py --server-id 1`
  2. explicitly load `C:\Users\syok443\P4P simulation\09cV2-fDPM-05pct-10678.cas.h5`
  3. read back `mass_flow_inlet` topology, `111.074 kg/s` Eulerian liquid, `80.690 kg/s` vapor, six legacy injections, inherited materials, DPM `True/True/1`, and `bottom=trap` / `wall=reflect`
  4. write the full-path pre-build recovery case before mutation
  5. create seven `steaminlet` surface injections, reacquiring the injection object after each dependency-sensitive setter and inheriting velocity/location/physical-model state from the parent exemplar
  6. remove the six legacy injections from the copied child branch and require exactly seven remaining injections with a `5.846000 kg/s` read-back sum
  7. require unchanged carrier boundaries, materials, phase model, mass-flow topology, wall fates, and liquid-accounting closure
  8. write only the child case, reload it by full Windows path, and repeat the strict audit
Working path or TUI:
  `scripts/setup/build_09cV3_mass_flow_from_09cV2.py --server-id 1`
Readback:
  Seven active fine-mist surface injections on `steaminlet`; flows `0.409128`, `1.165149`, `1.267410`, `1.092501`, `1.329262`, `0.468606`, and `0.113944 kg/s`, totaling `5.846000 kg/s`; mass-flow inlets and wall names remained `liquidinlet`, `steaminlet`, `bottom`, and `wall`.
Notes:
  This is the mass-flow-topology child and must not be conflated with the separate Student velocity-inlet adaptation. The source case was not overwritten. The build is case-only: no initialization, flow iterations, data read, or `.dat.h5` write. The seven-bin PSD remains an assumed engineering prior, not measured inlet data. Fluent 2025 R2 serializes the saved injection names as lowercase `09cv3-finemist-*`; verification is case-insensitive.

Fluent: 2025 R2
PyFluent: local `.venv` on repo laptop
Goal: Fluent-native sequential queue smoke test
Order:
  1. create the complete `.jou` on the Fluent host with one literal Scheme `display` and `newline` call per journal line
  2. start it with `settings.file.read_journal(file_name_list=[<absolute Windows path>])`
  3. for each independent job, read the source case, Hybrid Initialize, call `/solve/iterate <N>`, then `/file/write-case-data <output.cas.h5>`
  4. verify each expected `.cas.h5` and `.dat.h5` endpoint after Fluent completes the relevant job
Working path or TUI:
  `scripts/setup/run_vof_queue_smoke_test.py`
Readback:
  Three independent jobs each completed `75` Fluent iterations and wrote paired endpoints. The first two endpoint pairs appeared before Fluent reloaded and began the next job; all three pairs existed after completion.
Notes:
  In this 2025 R2 wrapper, `file.read_journal` expects `file_name_list`, not `file_name`. A Scheme string containing literal `\\n` writes backslash-n text to the remote journal and does not execute as separate TUI lines; write every record with an explicit Scheme `(newline)` instead. The journal itself, not Python, owns the iteration loop and checkpoint order.

Fluent: 2025 R2
PyFluent: local `.venv` on repo laptop
Goal: transient VOF queued numerical-stability screen with saved initialized fields
Order:
  1. read the explicit source case
  2. if the field is initialized/patched, read its paired data file
  3. set `/solve/set/transient-controls/time-step-size <dt>` **after** the data read
  4. start a transcript, run each native iteration block, and write paired case/data checkpoints
  5. stop the transcript before submitting a replacement journal after any interruption
Working path or TUI:
  `scripts/setup/run_02d_vof_stability_screen.py`
Readback:
  `solver.settings.solution.run_calculation.transient_controls.time_step_size` read back as `1e-05` during the corrected IC1/IC2 screen. IC0, IC1, and IC2 each reached paired 1,000/2,000-iteration endpoints.
Notes:
  Reading a `.dat.h5` restores transient run controls and overwrote a previously set timestep with `1.0`; setting the timestep before the data read is therefore invalid for a saved-field restart. An interrupted journal can leave a native transcript open, causing a later `/file/start-transcript` to fail; close the stale transcript while Fluent is idle, use a new uniquely named journal, and retain—but explicitly exclude—the large-step artifacts from the corrected test conclusion.

Fluent: 2025 R2
PyFluent: 0.39.0 local `.venv`
Case/data: unavailable; active filenames were not exposed by the existing session
Goal: recover configured Report Plot histories when live PyFluent monitor buffers are empty
Order:
  1. inspect `solution.monitor.report_files` without loading case/data or changing the session;
  2. read each configured relative Report File through Fluent Scheme after resolving it against an explicitly supplied remote report directory;
  3. parse the Fluent Lisp-style header and iteration/value pairs;
  4. write local JSON/PNG artifacts and preserve missing-file or parser errors.
Working path or TUI:
  `PyAnsys/scripts/inspection/extract_report_plot_histories.py --report-dir <remote report directory>`
  Relative names such as `.\\03a_stage3_*_rfile_4_1.out` may fail from the current Fluent working directory even when the absolute file exists elsewhere. The read-only `file-exists?` check and Scheme reader work with an explicit path such as `C:\Users\syok443\P4P simulation\brine outlet\<report-file>.out`.
Readback:
  The live session exposed 30 active Report Files. All 30 absolute report files were found in `C:\Users\syok443\P4P simulation\brine outlet`, and each yielded 18,000 iteration/value points through iteration 18,000.
Notes:
  Report File location is independent of case/data location. Do not infer case identity from the report directory or server routing alias. If the report files are absent, the history is unavailable from that checkpoint and must be instrumented before a rerun.
