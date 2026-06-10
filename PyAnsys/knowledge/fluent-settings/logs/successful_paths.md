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
