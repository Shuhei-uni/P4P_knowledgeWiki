# Successful Fluent Paths Log

Add working paths/orders here as the agent discovers them in the live Fluent session.

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
  Local manual launch is more reliable than `launch_fluent()` / `Solver.from_install()` for this Student-edition path because Fluent otherwise halts on stdin EOF after starting the server.
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
PyFluent: `.venv` on Windows Student target
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
PyFluent: `.venv` on Windows Student target
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
Goal: load a case-only `.cas.h5`, initialize, run `X` iterations, and save only `name_X.dat.h5`
Order:
  1. connect with `check_connection.py --server-id 2`
  2. verify remote case path exists
  3. read case with `solver.settings.file.read_case(file_name=...)`
  4. hybrid-initialize through `solution.initialization.hybrid_initialize()`
  5. run iterations through `solution.run_calculation.iterate(iter_count=...)`
  6. fall back to `solver.tui.solve.iterate(...)` only if the Settings API iterate call fails
  7. write data with `solver.settings.file.write_data(file_name=...)`
  8. verify the written `.dat.h5` is visible to Fluent
Working path or TUI:
  `scripts/setup/save_data_after_iterations.py '<case>.cas.h5' <iterations> --server-id 2`
Readback:
  Test command completed for `iterations = 1` and wrote:
  `C:\Users\syok443\Documents\Purnanto\enthalpy1680_1.dat.h5`
Notes:
  The script intentionally hybrid-initializes after loading the `.cas.h5` because a case-only file does not provide field data for data-file output. It avoids the repo's checkpoint persistence helpers so remote Windows output paths do not create local `C:\...run-state.json` artifacts on the laptop.

Fluent: 2024 R2
PyFluent: `.venv` on repo laptop
Case: `C:\Users\syok443\Documents\Purnanto\enthalpy1680.cas.h5`
Goal: run the lightweight case-to-data script with TUI commands only on server `4`
Order:
  1. connect with `check_connection.py --server-id 4`
  2. verify remote case path exists
  3. run `/file/read-case "<case>"`
  4. run `/solve/initialize/hyb-initialization`
  5. run `/solve/iterate <step>` in chunked calls
  6. run `/file/write-data "<output>"`
  7. verify the output `.dat.h5` is visible to Fluent
Working path or TUI:
  `scripts/setup/save_data_after_iterations.py '<case>.cas.h5' <iterations> --server-id 4 --report-interval 1`
Readback:
  Test command completed for `iterations = 2` and wrote:
  `C:\Users\syok443\Documents\Purnanto\enthalpy1680_2.dat.h5`
Notes:
  The script now uses literal TUI strings through `ti-menu-load-string`, so the solver work is driven by `/file/*` and `/solve/*` commands rather than the Settings API wrappers.

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
