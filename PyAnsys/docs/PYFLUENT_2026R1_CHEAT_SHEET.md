# PyFluent 2026 R1 Practical Cheat Sheet — Purnanto Separator Automation

**Project target:** local Ansys Fluent 2026 R1 Student install, PyFluent automation for `trial4.msh` using a one-inlet Purnanto-style geothermal separator case.

**Status legend used below**

- **[confirmed in my current script]**: path/pattern appears in `reconstruct_purnanto_trial3.py`.
- **[official-docs pattern]**: shown in current official PyFluent docs/API/examples/cheat sheet.
- **[needs local verification]**: likely useful, but confirm in a live Fluent 2026 R1 session using `.child_names`, `.get_state()`, `.allowed_values()`, or a small dry run.
- **[fallback only]**: use when the settings API is missing/inactive or a version-specific setting refuses the expected state shape.

---

## 0. Imports and baseline constants

```python
# [confirmed in my current script] Core import for Solver/Meshing sessions.
import ansys.fluent.core as pyfluent

# [confirmed in my current script] Use pathlib so Windows paths are explicit and safe.
from pathlib import Path
```

```python
# [confirmed in my current script] Raw Windows string path pattern.
MESH = Path(
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial4.msh"
)

# [confirmed in my current script] Prefer explicit .cas.h5 / .dat.h5 outputs.
OUT_CASE = MESH.with_name("trial4-purnanto-recon-500.cas.h5")
OUT_DATA = MESH.with_name("trial4-purnanto-recon-500.dat.h5")
LOG_FILE = MESH.with_name("trial4-purnanto-recon-500-log.txt")
```

---

## 1. Launching and connecting

### Local solver launch

```python
# [confirmed in my current script] Launch local Fluent solver, 3D double precision, local parallel.
solver = pyfluent.Solver.from_install(
    precision="double",
    processor_count=2,
    dimension=3,
)
print(solver.get_fluent_version())  # [confirmed in my current script] Verify launched Fluent version.
```

```python
# [official-docs pattern] Alternative generic launcher; newer docs also support enums.
solver = pyfluent.launch_fluent(
    mode="solver",
    precision="double",
    dimension=3,
    processor_count=2,
)
```

### Meshing launch

```python
# [official-docs pattern] Launch Fluent in meshing mode from local install.
meshing = pyfluent.Meshing.from_install()
```

```python
# [official-docs pattern] Generic meshing launch.
meshing = pyfluent.launch_fluent(mode=pyfluent.FluentMode.MESHING)
```

### Connect to existing Fluent session

```python
# [official-docs pattern] Connect using a server-info file created by Fluent gRPC server.
solver = pyfluent.connect_to_fluent(server_info_file_name="server.txt")
```

**Start the gRPC server in an already-open Fluent session**  
**[official-docs pattern]**

- Launch Fluent with `-sifile=<server_info_file_name>`, or
- In Fluent solution mode TUI: `server/start-server`, or
- GUI: `File -> Applications -> Server -> Start...`

### Student/local session conflict notes

- **[needs local verification]** Close Fluent, Workbench, and leftover Fluent background processes before `from_install()` if local launch hangs or picks up a stale server/session.
- **[needs local verification]** Student edition limits may show up as mesh/cell/node limits, licensing denials, or blocked launches. Treat launch failure as critical.
- **[needs local verification]** If Workbench/Fluent is already open, local PyFluent launch may fail or attach to an unexpected runtime depending on install/session state.

### Safe close

```python
# [confirmed in my current script] Always close in finally so Fluent does not stay alive.
try:
    ...
finally:
    if solver is not None:
        solver.exit()
```

---

## 2. File operations

### Read mesh / case / case-data

```python
# [confirmed in my current script] Read mesh-only file.
solver.settings.file.read_mesh(file_name=str(MESH))
```

```python
# [official-docs pattern] Read case file.
solver.settings.file.read_case(file_name=str(Path("case.cas.h5")))
```

```python
# [official-docs pattern] Read paired case/data from .cas.h5 basename.
solver.settings.file.read_case_data(file_name=str(Path("case.cas.h5")))
```

```python
# [official-docs pattern] Generic file read API; useful when specific command shape changes.
solver.settings.file.read(file_type="case", file_name=str(Path("case.cas.h5")))
solver.settings.file.read(file_type="case-data", file_name=str(Path("case.cas.h5")))
```

### Write case / data / case-data

```python
# [confirmed in my current script] Write case only.
solver.settings.file.write_case(file_name=str(OUT_CASE))
```

```python
# [confirmed in my current script] Write data only.
solver.settings.file.write_data(file_name=str(OUT_DATA))
```

```python
# [official-docs pattern] Write case + data together using .cas.h5 basename.
solver.settings.file.write_case_data(file_name=str(OUT_CASE))
```

```python
# [official-docs pattern] Generic write command; useful for case-data checkpoints.
solver.settings.file.write(file_type="case-data", file_name=str(OUT_CASE))
```

### Checkpoint pattern

```python
# [confirmed in my current script] Write paired checkpoint files during long diagnostic runs.
def checkpoint_write(solver, output_case: str, output_data: str, iteration_count: int) -> None:
    case_path = Path(output_case)
    data_path = Path(output_data)
    checkpoint_case = case_path.with_name(f"{case_path.stem}-iter{iteration_count}{case_path.suffix}")
    checkpoint_data = data_path.with_name(f"{data_path.stem}-iter{iteration_count}{data_path.suffix}")
    solver.settings.file.write_case(file_name=str(checkpoint_case))
    solver.settings.file.write_data(file_name=str(checkpoint_data))
```

**Recommended project pattern**

```text
trial4-purnanto-recon-500.cas.h5
trial4-purnanto-recon-500.dat.h5
trial4-purnanto-recon-500-log.txt
trial4-purnanto-recon-500.cas-iter250.h5  # adjust naming if pathlib suffix handling is awkward
trial4-purnanto-recon-500.dat-iter250.h5
```

**Windows path rules**

```python
# [confirmed in my current script] Use raw strings for source paths.
mesh = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\...\trial4.msh")

# [confirmed in my current script] Convert Path to str at PyFluent boundary.
solver.settings.file.read_mesh(file_name=str(mesh))
```

---

## 3. Live API discovery/debugging

### Core object inspection

```python
# [confirmed in my current script] Get whole state dict for a branch.
state = solver.settings.setup.boundary_conditions.get_state()
```

```python
# [confirmed in my current script] Set a nested state in one call.
solver.settings.setup.materials.fluid["water-vapor-manual"].set_state({
    "density": {"option": "value", "value": 5.7974339},
    "viscosity": {"option": "value", "value": 1.52062e-05},
})
```

```python
# [confirmed in my current script] Print child names before choosing a path.
print(solver.settings.solution.methods.child_names)
print(solver.settings.solution.methods.p_v_coupling.child_names)
print(solver.settings.solution.methods.spatial_discretization.child_names)
```

```python
# [confirmed in my current script] List named objects such as materials/zones/discretization entries.
print(solver.settings.setup.materials.fluid.get_object_names())
print(solver.settings.solution.methods.spatial_discretization.discretization_scheme.get_object_names())
```

```python
# [confirmed in my current script] Check whether a report/settings branch is active.
if solver.settings.results.report.fluxes.is_active():
    ...
```

```python
# [official-docs pattern] Ask allowed values before setting a string enum.
print(solver.settings.setup.models.viscous.model.allowed_values())
print(solver.settings.solution.methods.p_v_coupling.flow_scheme.allowed_values())
```

### Tree dump helper

```python
# [needs local verification] Practical local introspection helper.
def dump_branch(obj, name="obj", depth=1):
    print(f"\n{name}")
    for attr in ("child_names", "command_names"):
        try:
            print(f"{attr}: {getattr(obj, attr)}")
        except Exception as e:
            print(f"{attr}: <not available> {e}")
    try:
        print("object_names:", obj.get_object_names())
    except Exception:
        pass
    try:
        print("state:", obj.get_state())
    except Exception as e:
        print("state: <not available>", e)
```

### Distinguishing common API failures

- **Missing path:** Python `AttributeError`, `KeyError`, or object accessor error before Fluent executes. Use `child_names`, `dir(...)`, or `get_object_names()`.
- **Inactive setting:** `.is_active()` is false, or Fluent accepts the parent but rejects/ignores subkeys. Enable the relevant model/phase/BC first, then re-check `.get_state()`.
- **Wrong value shape:** Fluent errors on `set_state`. Compare current `.get_state()` shape and mirror it. In this project, many numerical values use `{"option": "value", "value": number}`, but `operating_pressure` is scalar `0`.

---

## 4. Mesh and zone inspection

### Boundary state inspection

```python
# [confirmed in my current script] Get boundary tree after mesh load.
boundary_state = solver.settings.setup.boundary_conditions.get_state()
```

```python
# [confirmed in my current script] Summarise zones by boundary type.
def summarize_boundaries(boundary_state):
    for boundary_type, zones in boundary_state.items():
        if isinstance(zones, dict):
            names = [str(n) for n in zones.keys() if str(n) != "settings"]
            if names:
                print(boundary_type, sorted(names))
```

### Detect inlet/outlet/wall names

```python
# [confirmed in my current script] Prefer named zone, otherwise first zone of matching type.
def detect_zone_name(boundary_state, boundary_type, preferred):
    section = boundary_state.get(boundary_type, {})
    if not isinstance(section, dict):
        return None
    if preferred in section:
        return preferred
    names = [str(n) for n in section.keys() if str(n) != "settings"]
    return names[0] if names else None

inlet_name = detect_zone_name(boundary_state, "velocity_inlet", "inlet")
if inlet_name is None:
    inlet_name = detect_zone_name(boundary_state, "mass_flow_inlet", "inlet")

outlet_name = detect_zone_name(boundary_state, "pressure_outlet", "outlet")
```

### Convert zone types

```python
# [confirmed in my current script] Convert existing inlet zone to mass-flow inlet.
solver.settings.setup.boundary_conditions.set_zone_type(
    zone_list=[inlet_name],
    new_type="mass-flow-inlet",
)
```

```python
# [confirmed in my current script] Ensure outlet is pressure outlet.
solver.settings.setup.boundary_conditions.set_zone_type(
    zone_list=[outlet_name],
    new_type="pressure-outlet",
)
```

### List zones if available

```python
# [official-docs pattern] Cell zone names.
fluid_zones = solver.settings.setup.cell_zone_conditions.fluid.get_object_names()
solid_zones = solver.settings.setup.cell_zone_conditions.solid.get_object_names()
```

```python
# [needs local verification] Surface/field zone information from solution variable API.
zones_info = solver.fields.solution_variable_info.get_zones_info()
```

### Common boundary-condition object paths

```python
# [confirmed in my current script] Boundary root.
bc = solver.settings.setup.boundary_conditions

# [confirmed in my current script] Mass-flow inlet object.
inlet_obj = bc.mass_flow_inlet[inlet_name]

# [confirmed in my current script] Pressure outlet object.
outlet_obj = bc.pressure_outlet[outlet_name]

# [official-docs pattern] Wall boundary object.
wall_obj = bc.wall["wall-name"]
```

---

## 5. General setup

### Operating pressure and gravity

```python
# [confirmed in my current script] 2026 R1 path verified in this project.
op = solver.settings.setup.general.operating_conditions

# [confirmed in my current script] Important: scalar 0, not {"option": "..."}.
op.operating_pressure = 0

# [confirmed in my current script] Enable gravity and set vector.
op.gravity.enable = True
op.gravity.components = [0.0, -9.81, 0.0]

# [confirmed in my current script] Verify after applying.
print(op.get_state())
```

### Reference pressure location

```python
# [needs local verification] Inspect first; exact active path depends on model/case.
op = solver.settings.setup.general.operating_conditions
print(op.child_names)
print(op.get_state())
# Then set the matching reference pressure location key only if visible/active.
```

### Operating density

```python
# [official-docs pattern, needs local verification in this case] Operating density branch exists under operating_conditions.
op.operating_density.enable = True      # enables specified operating density
op.operating_density.method = "..."     # check allowed_values() first
op.operating_density.value = 0.0        # set only if needed by buoyancy/multiphase setup
```

### Scheme fallback for operating conditions

```python
# [confirmed in my current script, fallback only] Use only if settings API fails.
solver.scheme.eval("(rpsetvar 'operating-pressure 0)")
solver.scheme.eval("(rpsetvar 'gravity? #t)")
solver.scheme.eval("(rpsetvar 'gravity-x 0.0)")
solver.scheme.eval("(rpsetvar 'gravity-y -9.81)")
solver.scheme.eval("(rpsetvar 'gravity-z 0.0)")
```

---

## 6. Models

### Energy

```python
# [confirmed in my current script] Keep energy off for current temporary reconstruction.
solver.settings.setup.models.energy.enabled = False
```

```python
# [official-docs pattern] Energy on.
solver.settings.setup.models.energy.enabled = True
```

### Viscous model and RNG k-epsilon

```python
# [confirmed in my current script] Enable k-epsilon.
models = solver.settings.setup.models
models.viscous.model = "k-epsilon"

# [confirmed in my current script] Select RNG variant.
models.viscous.k_epsilon_model = "rng"
```

```python
# [confirmed in my current script, needs local verification] Optional RNG suboptions.
models.viscous.k_epsilon.differential_viscosity_model = True
models.viscous.k_epsilon.swirl_dominated_flow = True
```

### Mixture multiphase and phases

```python
# [confirmed in my current script] Enable Mixture multiphase.
models.multiphase.model = "mixture"
```

```python
# [confirmed in my current script] Phase material path used in this project.
phases = solver.settings.setup.models.multiphase.phases
phases["phase-1"].material = "water-vapor-manual"
phases["phase-2"].material = "water-liquid-manual"
```

```python
# [confirmed in my current script, needs local verification] Droplet/diameter assumption if active.
phases["phase-2"].constant_dia = 1e-5
```

### Numerics reset warning after model changes

- **[needs local verification]** Fluent may reset spatial discretization, pressure-velocity coupling, and/or available discretization keys after enabling/changing multiphase, viscous model, or energy. In project scripts, set models first, then materials/phases, then BCs, then solution methods last. Reprint `methods.get_state()` after model changes.

---

## 7. Materials

### Material database access

```python
# [official-docs pattern] Copy water-liquid from Fluent database when available.
solver.settings.setup.materials.database.copy_by_name(type="fluid", name="water-liquid")
```

```python
# [needs local verification] Mesh-only loads may expose only "air"; inspect first.
print(solver.settings.setup.materials.fluid.get_object_names())
```

### Manual material creation

```python
# [confirmed in my current script] Create named manual fluid if missing.
fluid_materials = solver.settings.setup.materials.fluid
if "water-vapor-manual" not in fluid_materials.get_object_names():
    fluid_materials.create(name="water-vapor-manual")
```

```python
# [confirmed in my current script] Set constant density and viscosity with project state shape.
fluid_materials["water-vapor-manual"].set_state({
    "name": "water-vapor-manual",
    "chemical_formula": "",
    "density": {"option": "value", "value": 5.7974339},
    "viscosity": {"option": "value", "value": 1.52062e-05},
})
```

```python
# [confirmed in my current script] Manual liquid material.
if "water-liquid-manual" not in fluid_materials.get_object_names():
    fluid_materials.create(name="water-liquid-manual")

fluid_materials["water-liquid-manual"].set_state({
    "name": "water-liquid-manual",
    "chemical_formula": "",
    "density": {"option": "value", "value": 881.21088},
    "viscosity": {"option": "value", "value": 0.000145544},
})
```

```python
# [confirmed in my current script] Verify material values after setting.
print(fluid_materials["water-vapor-manual"].get_state())
print(fluid_materials["water-liquid-manual"].get_state())
```

### Assign materials to phases

```python
# [confirmed in my current script] Assign vapor/liquid materials to mixture phases.
phases = solver.settings.setup.models.multiphase.phases
phases["phase-1"].material = "water-vapor-manual"
phases["phase-2"].material = "water-liquid-manual"
```

---

## 8. Boundary conditions

### Mass-flow inlet

```python
# [confirmed in my current script] Access converted mass-flow inlet.
bc = solver.settings.setup.boundary_conditions
inlet_obj = bc.mass_flow_inlet[inlet_name]
```

```python
# [confirmed in my current script] One-inlet Purnanto-style phase-specific mass flow.
inlet_obj.set_state({
    "phase": {
        "mixture": {
            "momentum": {
                "direction_specification": "Normal to Boundary",
                "reference_frame": "Absolute",
                "supersonic_gauge_pressure": {"option": "value", "value": 1_140_000},
            },
            "turbulence": {
                "turbulence_specification": "Intensity and Hydraulic Diameter",
                "turbulent_intensity": 0.0211,
                "hydraulic_diameter": 0.724,
            },
        },
        "phase-1": {
            "momentum": {
                "mass_flow_specification": "Mass Flow Rate",
                "mass_flow_rate": {"option": "value", "value": 80.69},
            }
        },
        "phase-2": {
            "momentum": {
                "mass_flow_specification": "Mass Flow Rate",
                "mass_flow_rate": {"option": "value", "value": 116.92},
            }
        },
    }
})
```

```python
# [confirmed in my current script] Verify inlet state.
print(inlet_obj.get_state())
```

### Pressure outlet

```python
# [confirmed in my current script] Access pressure outlet.
outlet_obj = bc.pressure_outlet[outlet_name]
```

```python
# [confirmed in my current script] Pressure outlet with gauge pressure and backflow settings.
outlet_obj.set_state({
    "momentum": {
        "gauge_pressure": {"option": "value", "value": 1_120_000},
        "backflow_dir_spec_method": "Normal to Boundary",
        "backflow_pressure_spec": "Total Pressure",
        "backflow_reference_frame": "Absolute",
    },
    "turbulence": {
        "turbulence_specification": "Intensity and Hydraulic Diameter",
        "backflow_turbulent_intensity": 0.021525,
        "backflow_hydraulic_diameter": 0.724,
    },
    "phase": {
        "phase-2": {
            "multiphase": {
                "backflow_volume_fraction": {"option": "value", "value": 0.0}
            }
        }
    },
})
```

```python
# [confirmed in my current script] Verify outlet state.
print(outlet_obj.get_state())
```

### Handling inactive pressure-outlet subsettings

```python
# [needs local verification] Check actual active children before forcing turbulence/backflow keys.
print(outlet_obj.child_names)
print(outlet_obj.get_state())
```

- **[confirmed in my current script / project gotcha]** Treat pressure gauge value as critical.
- **[needs local verification]** Treat inactive outlet turbulence/backflow subsettings as warnings if `gauge_pressure` was applied and the solver proceeds.
- **[official-docs pattern]** Backflow values matter only when backflow occurs, but set reasonable values for stability.

---

## 9. Solution methods

### Confirmed 2026 R1 project paths

```python
# [confirmed in my current script] Main branches.
methods = solver.settings.solution.methods
spatial = methods.spatial_discretization
disc = spatial.discretization_scheme
```

```python
# [confirmed in my current script] Debug available method tree before setting.
print(methods.child_names)
print(methods.get_state())
print(methods.p_v_coupling.child_names)
print(spatial.child_names)
print(disc.get_object_names())
```

### Pressure-velocity coupling

```python
# [confirmed in my current script] SIMPLE.
solver.settings.solution.methods.p_v_coupling.flow_scheme = "SIMPLE"
```

```python
# [official-docs pattern] Check legal choices first.
print(solver.settings.solution.methods.p_v_coupling.flow_scheme.allowed_values())
```

### Gradient and discretization stack

```python
# [confirmed in my current script] Green-Gauss Node Based.
solver.settings.solution.methods.spatial_discretization.gradient_scheme = "green-gauss-node-based"
```

```python
# [confirmed in my current script] Project discretization stack.
solver.settings.solution.methods.spatial_discretization.discretization_scheme.set_state({
    "pressure": "presto!",
    "mom": "second-order-upwind",
    "mp": "quick",
    "k": "second-order-upwind",
    "epsilon": "second-order-upwind",
})
```

```python
# [official-docs pattern] Individual setting style.
disc = solver.settings.solution.methods.spatial_discretization.discretization_scheme
disc["pressure"] = "presto!"
```

**Use after all model changes.** Available keys can change with multiphase/turbulence/energy activation.

---

## 10. Initialization and running

### Hybrid initialization

```python
# [confirmed in my current script, fallback only TUI path] Reliable in this project.
solver.tui.solve.initialize.hyb_initialization()
```

```python
# [official-docs pattern] Settings API hybrid initialize.
solver.settings.solution.initialization.hybrid_initialize()
```

### Standard initialization

```python
# [official-docs pattern] Standard initialization.
init = solver.settings.solution.initialization
init.reference_frame = "absolute"
init.initialization_type = "standard"
init.standard_initialize()
```

### Run iterations

```python
# [confirmed in my current script, fallback only TUI path] Run n iterations.
solver.tui.solve.iterate(100)
```

```python
# [official-docs pattern] Settings API iteration.
solver.settings.solution.run_calculation.iterate(iter_count=100)
```

### Chunked diagnostic run with compact reporting

```python
# [confirmed in my current script] Run in chunks and print only compact summaries between chunks.
completed = 0
while completed < 500:
    step = min(50, 500 - completed)
    solver.tui.solve.iterate(step)
    completed += step
    report_flux_sanity(solver, inlet_name, outlet_name, iteration_count=completed, log_file=str(LOG_FILE))
    if completed % 250 == 0:
        checkpoint_write(solver, str(OUT_CASE), str(OUT_DATA), completed)
```

### Avoid flooding Codex/agent context with Fluent logs

```bash
# [needs local verification] Run from terminal and redirect logs to file.
python reconstruct_purnanto_trial3.py > trial4-purnanto-run.out 2>&1
```

```python
# [confirmed in my current script] Write compact custom summaries to a separate log file.
append_log_line(str(LOG_FILE), "iteration=50 | vapor_recovery_ratio=... | liquid_carryover_ratio=...")
```

**Agent rule:** do not paste full Fluent iteration logs into Codex. Paste final compact summary, residual trend comments, and the first/last ~30 lines only if there is a failure.

---

## 11. Reports and post-processing

### Flux/mass-flow report API

```python
# [confirmed in my current script] Access flux report object.
fluxes = solver.settings.results.report.fluxes
```

```python
# [confirmed in my current script] Check active before calling.
if fluxes.is_active():
    result = fluxes.get_mass_flow(domain="mixture", zones=[inlet_name, outlet_name])
```

```python
# [confirmed in my current script] Phase-specific fluxes.
mixture = fluxes.get_mass_flow(domain="mixture", zones=[inlet_name, outlet_name])
vapor = fluxes.get_mass_flow(domain="phase-1", zones=[inlet_name, outlet_name])
liquid = fluxes.get_mass_flow(domain="phase-2", zones=[inlet_name, outlet_name])
```

### Separator branch interpreted checks

```python
# [confirmed in my current script] Vapor recovery for one steam outlet.
vapor_recovery = abs(vapor[outlet_name]) / vapor[inlet_name]
```

```python
# [confirmed in my current script] Liquid carryover to steam outlet.
liquid_carryover = abs(liquid[outlet_name]) / liquid[inlet_name]
```

```python
# [confirmed in my current script] Do not fail one-outlet branch only because mixture net is non-zero.
mixture_net = mixture.get("Net", float("nan"))
```

**Project interpretation**

- **Vapor recovery:** `abs(vapor outlet) / vapor inlet`
- **Liquid carryover:** `abs(liquid outlet) / liquid inlet`
- **Do not treat total mixture imbalance as a failure** in the one-outlet separator branch, because liquid is intentionally not leaving through the steam outlet.

### Residuals

```python
# [official-docs pattern] Residual monitor branch; useful for settings/criteria.
residuals = solver.settings.solution.monitor.residual
print(residuals.get_state())
```

```python
# [official-docs pattern] Example residual criteria.
residuals.equations["continuity"].absolute_criteria = 1e-4
residuals.equations["continuity"].monitor = True
```

### Custom report definitions

```python
# [official-docs pattern] Create a volume report definition.
rep = solver.settings.solution.report_definitions.volume.create("volume-avg-vmag")
rep.report_type = "volume-average"
rep.field = "velocity-magnitude"
rep.cell_zones = solver.settings.setup.cell_zone_conditions.fluid.get_object_names()
```

```python
# [official-docs pattern] Attach report definition to plot/file monitor.
rplot = solver.settings.solution.monitor.report_plots.create("volume-avg-vmag-rplot")
rplot.report_defs = "volume-avg-vmag"

rfile = solver.settings.solution.monitor.report_files.create("volume-avg-vmag-rfile")
rfile.report_defs = "volume-avg-vmag"
```

---

## 12. TUI and Scheme fallbacks

### When to prefer settings API

Use settings API when:

- path is active and stable in `.child_names` / `.get_state()`;
- command has a clean object state shape;
- you need readable scripts future agents can inspect.

```python
# [confirmed in my current script] Settings API is preferred for model/material/BC/numerics setup.
solver.settings.setup.models.multiphase.model = "mixture"
```

### When TUI is safer

Use TUI when:

- a Fluent workflow command is easier in TUI;
- initialization/iterate commands are stable and already proven;
- Python journaling shows a TUI path but not a settings path.

```python
# [confirmed in my current script, fallback only] Hybrid initialize through TUI.
solver.tui.solve.initialize.hyb_initialization()
```

```python
# [confirmed in my current script, fallback only] Iterate through TUI.
solver.tui.solve.iterate(500)
```

```python
# [confirmed in my current script, fallback only] Dump Fluent configuration.
solver.tui.file.show_configuration()
```

### Scheme fallback

Use Scheme only when both settings API and TUI are awkward or broken for a small, known Fluent rpvar.

```python
# [confirmed in my current script, fallback only] Operating condition fallback.
solver.scheme.eval("(rpsetvar 'operating-pressure 0)")
```

```python
# [official-docs pattern, fallback only] Evaluate Scheme expression and return Python value/string where possible.
value = solver.scheme.eval("(+ 1 2)")
```

**Warnings**

- **[fallback only]** Scheme strings are version-sensitive and easy to mistype.
- **[fallback only]** Prefer verifying with `get_state()` after Scheme changes.
- **[official-docs pattern]** In current PyFluent, use `session.scheme.eval(...)`; older `scheme_eval` naming is deprecated.

---

## 13. Error handling patterns

### `try_settings_call(...)` helper

```python
# [confirmed in my current script] Optional settings can warn; critical settings can raise.
def try_settings_call(label: str, func, *, critical: bool = False) -> bool:
    try:
        func()
        print(f"{label}: OK")
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}")
        if critical:
            raise RuntimeError(f"{label} failed") from exc
        return False
```

### Critical failures for this project

Treat these as **critical** and stop:

```text
[confirmed in my current script/project-specific]
- mesh missing
- Fluent launch failure
- inlet/outlet not detected
- phase material creation/assignment failure
- operating pressure/gravity failure
- inlet mass-flow state failure
- outlet pressure state failure
- initialization failure
- final write_case/write_data failure
```

### Non-blocking warnings

Treat these as **warnings**:

```text
[confirmed in my current script/project-specific]
- optional RNG subsettings not accepted
- phase-2 constant_dia not available
- flux report inactive during very early setup
- inactive outlet turbulence/backflow subsettings if outlet gauge pressure is correctly applied
- mixture total imbalance in one-outlet branch
```

### Recommended wrapper usage

```python
# [confirmed in my current script] Critical.
try_settings_call(
    "set_mass_flow_inlet_state",
    lambda: inlet_obj.set_state(inlet_state),
    critical=True,
)
```

```python
# [confirmed in my current script] Optional.
try_settings_call(
    "phase-2 constant_dia",
    lambda: setattr(phases["phase-2"], "constant_dia", 1e-5),
)
```

---

## 14. Project-specific command cookbook

This is the compact workflow for the current geothermal separator case.

```python
# [confirmed in my current script] Project-specific PyFluent cookbook.

from pathlib import Path
import ansys.fluent.core as pyfluent

MESH = Path(
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe"
    r"\Major Files\trial4.msh"
)
OUT_CASE = MESH.with_name("trial4-purnanto-recon-500.cas.h5")
OUT_DATA = MESH.with_name("trial4-purnanto-recon-500.dat.h5")
LOG_FILE = MESH.with_name("trial4-purnanto-recon-500-log.txt")

MANUAL_VAPOR_NAME = "water-vapor-manual"
MANUAL_LIQUID_NAME = "water-liquid-manual"

def detect_zone_name(boundary_state, boundary_type, preferred):
    section = boundary_state.get(boundary_type, {})
    if not isinstance(section, dict):
        return None
    if preferred in section:
        return preferred
    names = [str(name) for name in section.keys() if str(name) != "settings"]
    return names[0] if names else None

def try_settings_call(label, func, *, critical=False):
    try:
        func()
        print(f"{label}: OK")
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}")
        if critical:
            raise RuntimeError(f"{label} failed") from exc
        return False

def report_flux_sanity(solver, inlet_name, outlet_name):
    fluxes = solver.settings.results.report.fluxes
    if not fluxes.is_active():
        print("flux reports inactive")
        return

    zones = [inlet_name, outlet_name]
    mixture = fluxes.get_mass_flow(domain="mixture", zones=zones)
    vapor = fluxes.get_mass_flow(domain="phase-1", zones=zones)
    liquid = fluxes.get_mass_flow(domain="phase-2", zones=zones)

    vapor_recovery = abs(vapor[outlet_name]) / vapor[inlet_name]
    liquid_carryover = abs(liquid[outlet_name]) / liquid[inlet_name]

    print(f"mixture_mass_flow={mixture}")
    print(f"vapor_mass_flow={vapor}")
    print(f"liquid_mass_flow={liquid}")
    print(f"vapor_recovery={vapor_recovery:.6f}")
    print(f"liquid_carryover={liquid_carryover:.6e}")

solver = None
try:
    # 1) Launch Fluent.
    solver = pyfluent.Solver.from_install(
        precision="double",
        processor_count=2,
        dimension=3,
    )
    print("LAUNCH_OK:", solver.get_fluent_version())

    # 2) Load trial4.msh.
    if not MESH.exists():
        raise FileNotFoundError(f"MESH_MISSING: {MESH}")
    solver.settings.file.read_mesh(file_name=str(MESH))
    print("MESH_LOAD_OK:", MESH)

    # 3) Detect zones.
    boundary_state = solver.settings.setup.boundary_conditions.get_state()
    inlet_name = detect_zone_name(boundary_state, "velocity_inlet", "inlet")
    if inlet_name is None:
        inlet_name = detect_zone_name(boundary_state, "mass_flow_inlet", "inlet")
    outlet_name = detect_zone_name(boundary_state, "pressure_outlet", "outlet")
    if inlet_name is None:
        raise RuntimeError("inlet boundary not detected")
    if outlet_name is None:
        raise RuntimeError("outlet boundary not detected")
    print("inlet_name:", inlet_name)
    print("outlet_name:", outlet_name)

    # 4) Convert inlet/outlet types.
    bc = solver.settings.setup.boundary_conditions
    bc.set_zone_type(zone_list=[inlet_name], new_type="mass-flow-inlet")
    bc.set_zone_type(zone_list=[outlet_name], new_type="pressure-outlet")

    # 5) Set Mixture + RNG k-epsilon.
    models = solver.settings.setup.models
    models.multiphase.model = "mixture"
    models.viscous.model = "k-epsilon"
    models.viscous.k_epsilon_model = "rng"
    models.energy.enabled = False
    try_settings_call("rng_differential_viscosity", lambda: setattr(models.viscous.k_epsilon, "differential_viscosity_model", True))
    try_settings_call("rng_swirl_dominated_flow", lambda: setattr(models.viscous.k_epsilon, "swirl_dominated_flow", True))

    # 6) Create vapor/liquid materials.
    fluid_materials = solver.settings.setup.materials.fluid
    if MANUAL_VAPOR_NAME not in fluid_materials.get_object_names():
        fluid_materials.create(name=MANUAL_VAPOR_NAME)
    fluid_materials[MANUAL_VAPOR_NAME].set_state({
        "name": MANUAL_VAPOR_NAME,
        "chemical_formula": "",
        "density": {"option": "value", "value": 5.7974339},
        "viscosity": {"option": "value", "value": 1.52062e-05},
    })

    if MANUAL_LIQUID_NAME not in fluid_materials.get_object_names():
        fluid_materials.create(name=MANUAL_LIQUID_NAME)
    fluid_materials[MANUAL_LIQUID_NAME].set_state({
        "name": MANUAL_LIQUID_NAME,
        "chemical_formula": "",
        "density": {"option": "value", "value": 881.21088},
        "viscosity": {"option": "value", "value": 0.000145544},
    })

    # 7) Assign materials to phases.
    phases = models.multiphase.phases
    phases["phase-1"].material = MANUAL_VAPOR_NAME
    phases["phase-2"].material = MANUAL_LIQUID_NAME
    try_settings_call("phase-2 constant_dia", lambda: setattr(phases["phase-2"], "constant_dia", 1e-5))

    # 8) Set operating pressure and gravity.
    op = solver.settings.setup.general.operating_conditions
    op.operating_pressure = 0
    op.gravity.enable = True
    op.gravity.components = [0.0, -9.81, 0.0]

    # 9) Set inlet vapor/liquid mass flow.
    inlet_obj = bc.mass_flow_inlet[inlet_name]
    inlet_obj.set_state({
        "phase": {
            "mixture": {
                "momentum": {
                    "direction_specification": "Normal to Boundary",
                    "reference_frame": "Absolute",
                    "supersonic_gauge_pressure": {"option": "value", "value": 1_140_000},
                },
                "turbulence": {
                    "turbulence_specification": "Intensity and Hydraulic Diameter",
                    "turbulent_intensity": 0.0211,
                    "hydraulic_diameter": 0.724,
                },
            },
            "phase-1": {
                "momentum": {
                    "mass_flow_specification": "Mass Flow Rate",
                    "mass_flow_rate": {"option": "value", "value": 80.69},
                }
            },
            "phase-2": {
                "momentum": {
                    "mass_flow_specification": "Mass Flow Rate",
                    "mass_flow_rate": {"option": "value", "value": 116.92},
                }
            },
        }
    })

    # 10) Set pressure outlet.
    outlet_obj = bc.pressure_outlet[outlet_name]
    outlet_obj.set_state({
        "momentum": {
            "gauge_pressure": {"option": "value", "value": 1_120_000},
            "backflow_dir_spec_method": "Normal to Boundary",
            "backflow_pressure_spec": "Total Pressure",
            "backflow_reference_frame": "Absolute",
        },
        "turbulence": {
            "turbulence_specification": "Intensity and Hydraulic Diameter",
            "backflow_turbulent_intensity": 0.021525,
            "backflow_hydraulic_diameter": 0.724,
        },
        "phase": {
            "phase-2": {
                "multiphase": {
                    "backflow_volume_fraction": {"option": "value", "value": 0.0}
                }
            }
        },
    })

    # 11) Set solution methods.
    methods = solver.settings.solution.methods
    spatial = methods.spatial_discretization
    disc = spatial.discretization_scheme
    print("methods_state_before:", methods.get_state())
    methods.p_v_coupling.flow_scheme = "SIMPLE"
    spatial.gradient_scheme = "green-gauss-node-based"
    disc.set_state({
        "pressure": "presto!",
        "mom": "second-order-upwind",
        "mp": "quick",
        "k": "second-order-upwind",
        "epsilon": "second-order-upwind",
    })
    print("methods_state_after:", methods.get_state())

    # 12) Hybrid initialize.
    solver.tui.solve.initialize.hyb_initialization()

    # 13) Run 500 iterations in chunks.
    completed = 0
    while completed < 500:
        step = min(50, 500 - completed)
        solver.tui.solve.iterate(step)
        completed += step
        print(f"\n--- after {completed} iterations ---")
        report_flux_sanity(solver, inlet_name, outlet_name)
        if completed == 250:
            solver.settings.file.write_case(file_name=str(OUT_CASE.with_name("trial4-purnanto-recon-iter250.cas.h5")))
            solver.settings.file.write_data(file_name=str(OUT_DATA.with_name("trial4-purnanto-recon-iter250.dat.h5")))

    # 14) Save final .cas.h5 and .dat.h5.
    solver.settings.file.write_case(file_name=str(OUT_CASE))
    solver.settings.file.write_data(file_name=str(OUT_DATA))
    print("SAVE_OK:", OUT_CASE, OUT_DATA)

finally:
    if solver is not None:
        solver.exit()
        print("EXIT_OK")
```

---

## Known gotchas from this project

- **[confirmed/project-specific]** Close Fluent/Workbench before local PyFluent launch to avoid local session conflicts.
- **[confirmed/project-specific]** Mesh-only loads may only expose `air` as a material, so manual vapor/liquid material creation is more reliable than assuming the database copy is available.
- **[confirmed/project-specific]** Model activation can reset numerics. Set solution methods after changing multiphase/turbulence/energy.
- **[confirmed in my current script]** `solver.settings.setup.general.operating_conditions.operating_pressure = 0` expects scalar `0`, not `{"option": "value", "value": 0}` in the confirmed 2026 R1 path.
- **[confirmed/project-specific]** Pressure-outlet subsettings may appear inactive even if `.set_state(...)` returns OK; verify `outlet_obj.get_state()` and treat inactive backflow/turbulence as warning if gauge pressure is correct.
- **[confirmed/project-specific]** Avoid streaming huge iteration logs into Codex/agent context. Write logs to a file and print compact summaries only.
- **[confirmed/project-specific]** Do not fail the one-outlet branch on total mixture imbalance alone; the liquid phase is intentionally not expected to leave through the steam outlet.

---

## Official/source references used

1. PyFluent documentation home / compatibility  
   https://fluent.docs.pyansys.com/

2. Launching and connecting to Fluent  
   https://fluent.docs.pyansys.com/version/stable/user_guide/session/launching_ansys_fluent.html

3. Using PyFluent sessions  
   https://fluent.docs.pyansys.com/version/stable/user_guide/session/session.html

4. PyFluent official cheat sheet PDF  
   https://fluent.docs.pyansys.com/version/stable/_static/cheat_sheet.pdf

5. PyFluent settings/flobject API  
   https://fluent.docs.pyansys.com/version/stable/api/solver/flobject.html  
   https://fluent.docs.pyansys.com/version/stable/api/services/settings.html

6. File settings API  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/file.html  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/read_mesh.html  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/read_case.html  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/read_case_data.html  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/write_case_data.html

7. Boundary conditions API  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/boundary_conditions.html

8. General operating conditions API  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/gravity.html  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/operating_density.html

9. Viscous model API  
   https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/viscous.html

10. Official PyFluent examples for material, BC, methods, reports, initialization, run, and save patterns  
    https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/species_transport.html  
    https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/mixing_tank_workflow.html  
    https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/modeling_ablation.html

11. TUI and Scheme fallback docs  
    https://fluent.docs.pyansys.com/version/stable/user_guide/legacy/tui.html  
    https://fluent.docs.pyansys.com/version/stable/api/services/scheme_eval.html

12. Ansys Developer settings API blog  
    https://developer.ansys.com/blog/all-you-need-know-about-pyfluents-settings-apis-and-objects
