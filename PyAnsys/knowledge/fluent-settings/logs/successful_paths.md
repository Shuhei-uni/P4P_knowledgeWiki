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
Notes:
  `injection_surfaces` failed through all tested settings paths on server `3`:
  - `StringList.set_state("steaminlet")`
  - `SettingsBase.set_state(["steaminlet"])`
  - `location.set_state({"injection_surfaces": ...})`
  - direct Scheme `api-set-var` attempts with string lists, symbol lists, and alists
  Failure signature stayed in the DPM surface-location category:
  - `wta(1st) to string->symbol`
  - `wta(1st) to symbol->string`
  - `ASSQ: invalid argument [2]: improper list`
  Current diagnosis: likely `PyFluent wrapper limitation` or `path/version issue` specific to the 2024 R2 DPM surface selector on this server build. Keep using the carrier-field rebuild path above, but isolate the injection-surface bind as a dedicated fallback problem rather than rerunning the full setup.
