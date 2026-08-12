# PyFluent 2026 R1 Options Atlas for Fluent Setup Automation

**Purpose:** companion file to `PYFLUENT_2026R1_CHEAT_SHEET.md`.

This file is intentionally more exhaustive than the first cheat sheet. It is an **option atlas** for agents/scripts that need to explore most of Fluent's available setup knobs, especially under:

- `solver.settings.setup.models`
- `solver.settings.setup.boundary_conditions`
- `solver.settings.setup.materials`
- `solver.settings.solution.methods`
- `solver.settings.solution.controls`
- `solver.settings.solution.monitor`
- `solver.settings.results.report`

It is still **not a guaranteed full Fluent manual**. Fluent's Python settings tree is generated from the live Fluent build and is conditional on solver mode, dimensionality, mesh, active models, phase names, materials, and boundary types. Treat this document as a practical enumeration plus scripts to dump the exact active tree locally.

## Status tag legend

| Tag | Meaning |
|---|---|
| `[confirmed in current script]` | This exact pattern appears in `reconstruct_purnanto_trial3.py`. |
| `[official-docs pattern]` | The object path or pattern is directly shown in official PyFluent docs/API/examples. |
| `[needs local verification]` | Likely valid Fluent setting area, but exact path/value names must be checked with `.child_names`, `.get_state()`, `.allowed_values()`, or `.is_active()` in Fluent 2026 R1. |
| `[fallback only]` | Use when settings API is missing/inactive or an agent needs a robust escape hatch. |

---

## 0. First principle: enumerate from the live session

Do not assume all settings are present before activating models. Many subtrees only become active after enabling energy, multiphase, species, DPM, radiation, etc.

### 0.1 Minimal local introspection helpers

```python
# [official-docs pattern] Universal PyFluent settings-object methods.
# Purpose: safely inspect available settings, active state, allowed values, and object names.
from pprint import pprint


def safe(label, fn, default=None):
    try:
        return fn()
    except Exception as exc:
        return f"<FAILED {label}: {type(exc).__name__}: {exc}>" if default is None else default


def show_obj(label, obj, *, state=True, children=True, commands=True, objects=True, allowed=True):
    print(f"\n=== {label} ===")
    if children:
        print("child_names:")
        pprint(safe("child_names", lambda: obj.child_names))
    if commands:
        print("command_names:")
        pprint(safe("command_names", lambda: obj.command_names))
    if objects:
        print("get_object_names:")
        pprint(safe("get_object_names", lambda: obj.get_object_names()))
    print("is_active:")
    pprint(safe("is_active", lambda: obj.is_active()))
    if allowed:
        print("allowed_values:")
        pprint(safe("allowed_values", lambda: obj.allowed_values()))
    if state:
        print("get_state:")
        pprint(safe("get_state", lambda: obj.get_state()))


models = solver.settings.setup.models
bc = solver.settings.setup.boundary_conditions
show_obj("setup.models", models)
show_obj("setup.boundary_conditions", bc)
```

### 0.2 Recursive tree walker for local API maps

```python
# [needs local verification]
# Purpose: create a compact local map of the available settings tree.
# Run after loading mesh, after enabling models, and after converting zones.

from pprint import pprint

SKIP_NAMES = {"parent", "flproxy", "_parent"}


def summarize_setting(obj, label, depth=0, max_depth=3, seen=None):
    if seen is None:
        seen = set()
    indent = "  " * depth
    key = id(obj)
    if key in seen:
        print(f"{indent}- {label}: <seen>")
        return
    seen.add(key)

    active = safe("is_active", lambda: obj.is_active())
    allowed = safe("allowed_values", lambda: obj.allowed_values())
    state = safe("get_state", lambda: obj.get_state())
    objects = safe("get_object_names", lambda: obj.get_object_names())
    children = safe("child_names", lambda: obj.child_names, default=[])
    commands = safe("command_names", lambda: obj.command_names, default=[])

    print(f"{indent}- {label}")
    print(f"{indent}  active: {active}")
    if allowed and not str(allowed).startswith("<FAILED"):
        print(f"{indent}  allowed_values: {allowed}")
    if objects and not str(objects).startswith("<FAILED"):
        print(f"{indent}  object_names: {objects}")
    if commands and not str(commands).startswith("<FAILED"):
        print(f"{indent}  command_names: {commands}")
    if depth >= max_depth:
        return

    if isinstance(children, list):
        for child in children:
            if child in SKIP_NAMES:
                continue
            child_obj = safe(f"getattr {child}", lambda c=child: getattr(obj, c))
            if isinstance(child_obj, str) and child_obj.startswith("<FAILED"):
                print(f"{indent}  - {child}: {child_obj}")
            else:
                summarize_setting(child_obj, f"{label}.{child}", depth + 1, max_depth, seen)


summarize_setting(solver.settings.setup.models, "models", max_depth=4)
summarize_setting(solver.settings.setup.boundary_conditions, "boundary_conditions", max_depth=4)
summarize_setting(solver.settings.solution.methods, "solution.methods", max_depth=4)
```

### 0.3 Snapshot active state before and after model activation

```python
# [needs local verification]
# Purpose: prove which settings appeared/reset after model changes.

before = solver.settings.setup.models.get_state()

solver.settings.setup.models.energy.enabled = False
solver.settings.setup.models.multiphase.model = "mixture"  # your project path uses .model
solver.settings.setup.models.viscous.model = "k-epsilon"
solver.settings.setup.models.viscous.k_epsilon_model = "rng"

after = solver.settings.setup.models.get_state()
print("MODELS BEFORE:")
pprint(before)
print("MODELS AFTER:")
pprint(after)
```

---

# 1. `setup.models` top-level atlas

Official PyFluent API docs list these top-level `setup.models` children for the 2026 docs generation:

```python
models = solver.settings.setup.models
```

| Path | What it controls | Status |
|---|---|---|
| `models.multiphase` | Multiphase model selection/options | `[official-docs pattern]`, project uses this |
| `models.energy` | Energy transport model | `[official-docs pattern]`, project uses this |
| `models.viscous` | Viscous/turbulence model | `[official-docs pattern]`, project uses this |
| `models.acoustics` | Acoustics model | `[official-docs pattern]`, `[needs local verification]` |
| `models.radiation` | Radiative heat transfer | `[official-docs pattern]`, `[needs local verification]` |
| `models.species` | Species transport/reactions | `[official-docs pattern]`, `[needs local verification]` |
| `models.discrete_phase` | DPM | `[official-docs pattern]`, `[needs local verification]` |
| `models.virtual_blade_model` | VBM | `[official-docs pattern]`, `[needs local verification]` |
| `models.optics` | Optics model | `[official-docs pattern]`, `[needs local verification]` |
| `models.structure` | FSI/structural modelling | `[official-docs pattern]`, `[needs local verification]` |
| `models.ablation` | Ablation | `[official-docs pattern]`, `[needs local verification]` |
| `models.dsmc` | DSMC | `[official-docs pattern]`, `[needs local verification]` |
| `models.echemistry` | Electrochemistry/potential model | `[official-docs pattern]`, `[needs local verification]` |
| `models.battery` | Battery model | `[official-docs pattern]`, `[needs local verification]` |
| `models.system_coupling` | System Coupling | `[official-docs pattern]`, `[needs local verification]` |
| `models.sofc` | SOFC | `[official-docs pattern]`, `[needs local verification]` |
| `models.pemfc` | PEMFC | `[official-docs pattern]`, `[needs local verification]` |

Useful enumeration:

```python
# [official-docs pattern]
print(models.child_names)       # list model branches
pprint(models.get_state())      # full active state, if supported
```

---

# 2. Energy model options

```python
energy = solver.settings.setup.models.energy
```

| Path | Pattern | Note | Status |
|---|---|---|---|
| `energy.enabled` | `energy.enabled = True` / `False` | Enables/disables energy equation. | `[official-docs pattern]`, `[confirmed in current script]` uses `False` |
| `energy.viscous_dissipation` | `energy.viscous_dissipation = True` | Compressible/energy-on option. | `[official-docs pattern]`, `[needs local verification]` |
| `energy.pressure_work` | `energy.pressure_work = True` | Compressible/energy-on option. | `[official-docs pattern]`, `[needs local verification]` |
| `energy.kinetic_energy` | `energy.kinetic_energy = True` | Include kinetic energy in energy equation. | `[official-docs pattern]`, `[needs local verification]` |
| `energy.inlet_diffusion` | `energy.inlet_diffusion = True` | Include inlet diffusion in energy equation. | `[official-docs pattern]`, `[needs local verification]` |
| `energy.two_temperature` | inspect with `.child_names` | Two-temperature model object. | `[official-docs pattern]`, `[needs local verification]` |

```python
# [official-docs pattern]
show_obj("energy", energy)

# [confirmed in current script]
solver.settings.setup.models.energy.enabled = False  # no energy equation for current temporary separator reconstruction
```

---

# 3. Viscous / turbulence model atlas

```python
viscous = solver.settings.setup.models.viscous
```

## 3.1 Main viscous model selection

```python
# [official-docs pattern]
print(viscous.model.get_state())
print(viscous.model.allowed_values())

# [confirmed in current script]
viscous.model = "k-epsilon"
```

Common `viscous.model.allowed_values()` shown in official docs include:

```python
[
    "inviscid",
    "laminar",
    "k-epsilon",
    "k-omega",
    "mixing-length",
    "spalart-allmaras",
    "k-kl-w",
    "transition-sst",
    "reynolds-stress",
    "scale-adaptive-simulation",
    "detached-eddy-simulation",
    "large-eddy-simulation",
]
```

Use `allowed_values()` locally; availability can change with solver configuration.

## 3.2 Official viscous child branches

Official API docs list these `viscous` children:

| Path | What it controls | Status |
|---|---|---|
| `viscous.model` | Viscous model selector | `[official-docs pattern]` |
| `viscous.spalart_allmaras_production` | SA strain/vorticity production | `[official-docs pattern]` |
| `viscous.k_epsilon_model` | k-epsilon family selector | `[official-docs pattern]`, `[confirmed in current script]` |
| `viscous.k_omega_model` | k-omega family selector | `[official-docs pattern]` |
| `viscous.k_omega` | k-omega model options | `[official-docs pattern]` |
| `viscous.geko` | GEKO options | `[official-docs pattern]` |
| `viscous.k_epsilon` | k-epsilon options | `[official-docs pattern]`, project uses it |
| `viscous.reynolds_stress` | RSM options | `[official-docs pattern]` |
| `viscous.subgrid_scale_model` | LES subgrid model | `[official-docs pattern]` |
| `viscous.les_model_options` | LES options | `[official-docs pattern]` |
| `viscous.reynolds_stress_options` | RSM options | `[official-docs pattern]` |
| `viscous.near_wall_treatment` | Near-wall treatment | `[official-docs pattern]` |
| `viscous.rans` | RANS options | `[official-docs pattern]` |
| `viscous.des` | DES options | `[official-docs pattern]` |
| `viscous.transition_module` | Transition model enable/disable | `[official-docs pattern]` |
| `viscous.hybrid_rans_les` | Hybrid RANS-LES enable/disable | `[official-docs pattern]` |
| `viscous.sbes` | SBES options | `[official-docs pattern]` |
| `viscous.user_defined_transition` | User-defined transition correlations | `[official-docs pattern]` |
| `viscous.options` | General viscous-model options | `[official-docs pattern]` |
| `viscous.multiphase_turbulence` | Multiphase turbulence options | `[official-docs pattern]` |
| `viscous.turbulence_expert` | Expert turbulence options | `[official-docs pattern]` |
| `viscous.transition` | Transition options | `[official-docs pattern]` |
| `viscous.transition_sst` | Transition SST options | `[official-docs pattern]` |
| `viscous.user_defined_functions` | UDF hooks for turbulent viscosity / Prandtl / Schmidt | `[official-docs pattern]` |
| `viscous.sa_enhanced_wall_treatment` | SA enhanced wall treatment | `[official-docs pattern]` |
| `viscous.sa_damping` | SA low-Re form | `[official-docs pattern]` |

## 3.3 k-epsilon / RNG project pattern

```python
# [confirmed in current script]
models = solver.settings.setup.models
models.viscous.model = "k-epsilon"        # activate k-epsilon family
models.viscous.k_epsilon_model = "rng"    # select RNG k-epsilon variant
```

```python
# [confirmed in current script]
# Purpose: optional RNG options if active in your local 2026 R1 session.
models.viscous.k_epsilon.differential_viscosity_model = True
models.viscous.k_epsilon.swirl_dominated_flow = True
```

Local verification commands:

```python
# [needs local verification]
show_obj("viscous", models.viscous)
show_obj("viscous.k_epsilon_model", models.viscous.k_epsilon_model)
show_obj("viscous.k_epsilon", models.viscous.k_epsilon)
show_obj("viscous.near_wall_treatment", models.viscous.near_wall_treatment)
show_obj("viscous.multiphase_turbulence", models.viscous.multiphase_turbulence)
```

Likely k-epsilon-related settings to inspect:

| Setting family | Why inspect it | Status |
|---|---|---|
| `k_epsilon_model` | standard/RNG/realizable-like variant selector | `[confirmed in current script]` for `rng`; allowed values need local check |
| `k_epsilon.differential_viscosity_model` | RNG differential viscosity option | `[confirmed in current script]` |
| `k_epsilon.swirl_dominated_flow` | RNG swirl correction option | `[confirmed in current script]` |
| `near_wall_treatment` | standard/enhanced/scalable/etc wall treatment | `[needs local verification]` |
| `multiphase_turbulence` | mixture/phase turbulence behaviour | `[needs local verification]` |
| `turbulence_expert` | expert constants/options | `[needs local verification]` |

---

# 4. Multiphase model atlas

```python
mp = solver.settings.setup.models.multiphase
```

## 4.1 Multiphase model selection

Your current script uses:

```python
# [confirmed in current script]
solver.settings.setup.models.multiphase.model = "mixture"
```

Official cavitation example uses the mixture model but shows a plural property name in that example:

```python
# [official-docs pattern]
solver_session.settings.setup.models.multiphase.models = "mixture"
```

**Practical rule:** in your 2026 R1 script, keep using `.model` because it works locally. When generalising, test both via `try_settings_call`:

```python
# [needs local verification]
def set_multiphase_model(solver, value="mixture"):
    mp = solver.settings.setup.models.multiphase
    try:
        mp.model = value
        return "model"
    except Exception:
        mp.models = value
        return "models"
```

## 4.2 Multiphase option families to inspect

After setting `mixture`, run:

```python
# [needs local verification]
mp = solver.settings.setup.models.multiphase
show_obj("multiphase", mp)
show_obj("multiphase.phases", mp.phases)
print("phase names:", mp.phases.get_object_names())

for ph in mp.phases.get_object_names():
    show_obj(f"multiphase.phases[{ph}]", mp.phases[ph], state=True)
```

Likely multiphase branches/settings to inspect in a geothermal separator:

| Setting family | Why it matters | Status |
|---|---|---|
| `mp.model` or `mp.models` | mixture/VOF/Eulerian/etc selector | `[confirmed in current script]` for `.model="mixture"`; plural path in official example |
| `mp.phases` | named phase objects | `[confirmed in current script]` |
| `mp.phases["phase-1"].material` | assign vapor material | `[confirmed in current script]` |
| `mp.phases["phase-2"].material` | assign liquid material | `[confirmed in current script]` |
| `mp.phases["phase-2"].constant_dia` | constant droplet/particle diameter | `[confirmed in current script]`, optional |
| phase names | `phase-1`/`phase-2` default names or renamed names | `[needs local verification]` |
| slip/drift/interphase velocity | critical for Mixture model | `[needs local verification]` |
| drag law | affects separation/carryover | `[needs local verification]` |
| lift force | possible secondary force | `[needs local verification]` |
| virtual mass force | possible secondary force | `[needs local verification]` |
| turbulent dispersion | affects phase spread | `[needs local verification]` |
| wall lubrication | multiphase wall effect | `[needs local verification]` |
| surface tension | if interface effects are important | `[needs local verification]` |
| mass transfer | evaporation/condensation/cavitation | `[needs local verification]` |
| population balance | droplet distribution instead of constant diameter | `[needs local verification]` |

## 4.3 TUI fallback for mixture parameters

The official cavitation example uses a TUI fallback after enabling mixture:

```python
# [official-docs pattern] / [fallback only]
solver.tui.define.models.multiphase.mixture_parameters("no", "implicit")
```

Use TUI here when the settings API does not expose a stable path for mixture expert options.

---

# 5. Other model branches worth enumerating

These are less central to your current one-inlet separator branch, but agents should know where to inspect them.

## 5.1 Species

```python
# [needs local verification]
species = solver.settings.setup.models.species
show_obj("species", species)
```

Inspect if you need steam/noncondensable gases, mass fractions, reactions, or mixture materials.

Likely areas:

| Area | Use |
|---|---|
| species transport enable | gas/vapor species mixing |
| volumetric reactions | combustion/chemistry, probably not current separator |
| mixture material species list | required for species transport |
| boundary species mass fractions | per inlet/outlet/species |

## 5.2 Discrete Phase Model / DPM

```python
# [needs local verification]
dpm = solver.settings.setup.models.discrete_phase
show_obj("discrete_phase", dpm, state=True)
```

Inspect if adding droplets after a converged continuous-phase solution.

Likely areas:

| Area | Use |
|---|---|
| enable/disable DPM | one-way/two-way particles |
| injections | droplet source definitions |
| tracking | particle step length, max refinements, integration |
| interaction with continuous phase | source coupling |
| turbulent dispersion/random walk | particle spread |
| wall interaction | reflect/trap/escape/splash |

## 5.3 Radiation

```python
# [needs local verification]
radiation = solver.settings.setup.models.radiation
show_obj("radiation", radiation)
```

Mostly not relevant unless temperature/heat transfer is enabled.

## 5.4 Acoustics, optics, ablation, battery, SOFC/PEMFC, DSMC, system coupling

```python
# [needs local verification]
for name in ["acoustics", "optics", "ablation", "battery", "sofc", "pemfc", "dsmc", "system_coupling"]:
    show_obj(f"models.{name}", getattr(models, name), state=False)
```

Usually irrelevant to the geothermal separator branch. Keep them off unless intentionally modelling those physics.

---

# 6. Boundary conditions top-level atlas

```python
bc = solver.settings.setup.boundary_conditions
```

Official docs list the following boundary-condition type containers:

| Boundary type path | Practical use | Status |
|---|---|---|
| `bc.axis` | Axis boundary | `[official-docs pattern]` |
| `bc.degassing` | Degassing boundary | `[official-docs pattern]` |
| `bc.exhaust_fan` | Exhaust fan | `[official-docs pattern]` |
| `bc.fan` | Fan | `[official-docs pattern]` |
| `bc.geometry` | Geometry boundary object | `[official-docs pattern]` |
| `bc.inlet_vent` | Inlet vent | `[official-docs pattern]` |
| `bc.intake_fan` | Intake fan | `[official-docs pattern]` |
| `bc.interface` | Interface | `[official-docs pattern]` |
| `bc.interior` | Interior zone | `[official-docs pattern]` |
| `bc.mass_flow_inlet` | Prescribed mass flow inlet | `[official-docs pattern]`, `[confirmed in current script]` |
| `bc.mass_flow_outlet` | Mass flow outlet | `[official-docs pattern]` |
| `bc.network` | Network boundary | `[official-docs pattern]` |
| `bc.network_end` | Network end | `[official-docs pattern]` |
| `bc.outflow` | Outflow outlet | `[official-docs pattern]` |
| `bc.outlet_vent` | Outlet vent | `[official-docs pattern]` |
| `bc.overset` | Overset boundary | `[official-docs pattern]` |
| `bc.periodic` | Periodic boundary | `[official-docs pattern]` |
| `bc.porous_jump` | Porous jump | `[official-docs pattern]` |
| `bc.pressure_far_field` | Compressible far-field | `[official-docs pattern]` |
| `bc.pressure_inlet` | Total/gauge pressure inlet | `[official-docs pattern]` |
| `bc.pressure_outlet` | Gauge pressure outlet/backflow | `[official-docs pattern]`, `[confirmed in current script]` |
| `bc.radiator` | Radiator boundary | `[official-docs pattern]` |
| `bc.rans_les_interface` | RANS/LES interface | `[official-docs pattern]` |
| `bc.recirculation_inlet` | Recirculation inlet | `[official-docs pattern]` |
| `bc.recirculation_outlet` | Recirculation outlet | `[official-docs pattern]` |
| `bc.shadow` | Shadow wall/interface zone | `[official-docs pattern]` |
| `bc.symmetry` | Symmetry plane | `[official-docs pattern]` |
| `bc.velocity_inlet` | Velocity inlet | `[official-docs pattern]` |
| `bc.wall` | Wall/no-slip/shell/thermal/wall-film | `[official-docs pattern]` |
| `bc.non_reflecting_bc` | Non-reflecting BC object | `[official-docs pattern]` |
| `bc.perforated_wall` | Perforated wall model | `[official-docs pattern]` |
| `bc.settings` | BC settings child | `[official-docs pattern]` |

Useful commands:

```python
# [official-docs pattern]
print(bc.child_names)      # available BC type containers
pprint(bc.get_state())     # full boundary state

# [official-docs pattern]
bc.set_zone_type(zone_list=["inlet"], new_type="mass-flow-inlet")
bc.copy(from_="inlet_1", to="inlet_2")
```

Project conversion:

```python
# [confirmed in current script]
bc.set_zone_type(zone_list=[inlet_name], new_type="mass-flow-inlet")
bc.set_zone_type(zone_list=[outlet_name], new_type="pressure-outlet")
```

---

# 7. Boundary object child sections

For common boundaries such as `mass_flow_inlet`, `pressure_outlet`, and `velocity_inlet`, official child objects include:

| Child path under a named boundary | What it controls | Status |
|---|---|---|
| `.name` | Name of boundary object | `[official-docs pattern]` |
| `.volume` | Associated volume object | `[official-docs pattern]` |
| `.locations` | Location names | `[official-docs pattern]` |
| `.momentum` | Momentum variables/settings | `[official-docs pattern]` |
| `.turbulence` | Turbulence variables/settings | `[official-docs pattern]` |
| `.thermal` | Temperature/thermal settings | `[official-docs pattern]` |
| `.radiation` | Boundary radiation settings | `[official-docs pattern]` |
| `.species` | Boundary species settings | `[official-docs pattern]` |
| `.discrete_phase` | Boundary DPM behaviour | `[official-docs pattern]` |
| `.multiphase` | Boundary multiphase variables | `[official-docs pattern]` |
| `.potential` | Potential/electrochemistry variables | `[official-docs pattern]` |
| `.structure` | FSI/structural variables | `[official-docs pattern]` |
| `.uds` | User-defined scalar boundary values | `[official-docs pattern]` |
| `.icing` | Icing variables | `[official-docs pattern]` |
| `.geometry` | Geometry model variables | `[official-docs pattern]` |
| `.phase` | Domain/phase-specific boundary settings | `[official-docs pattern]`, `[confirmed in current script]` |

For `wall`, official docs additionally list:

| Wall-only-ish child | Use | Status |
|---|---|---|
| `.wall_film` | Wall film settings | `[official-docs pattern]` |
| `.ablation` | Ablation boundary variables | `[official-docs pattern]` |

Named boundary object methods include:

```python
# [official-docs pattern]
bc.mass_flow_inlet["inlet"].display()
bc.mass_flow_inlet["inlet"].set_type("velocity-inlet")   # verify syntax locally
bc.mass_flow_inlet["inlet"].set_location(...)             # needs local args check
bc.mass_flow_inlet["inlet"].split(...)                    # needs local args check
```

---

# 8. Mass-flow inlet option atlas

```python
mfi = solver.settings.setup.boundary_conditions.mass_flow_inlet[inlet_name]
```

## 8.1 Project state pattern

```python
# [confirmed in current script]
# Purpose: one-inlet two-phase separator inlet; mixture direction/turbulence plus per-phase mass flow.

mfi.set_state({
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

## 8.2 Things to enumerate on mass-flow inlet

```python
# [needs local verification]
show_obj("mfi", mfi)
show_obj("mfi.momentum", mfi.momentum)
show_obj("mfi.turbulence", mfi.turbulence)
show_obj("mfi.phase", mfi.phase)

for ph in safe("phase object names", lambda: mfi.phase.get_object_names(), default=[]):
    show_obj(f"mfi.phase[{ph}]", mfi.phase[ph])
```

Common inlet subsettings to look for:

| Area | Typical setting keys/ideas | Status |
|---|---|---|
| momentum | mass flow rate, mass flux, direction method, normal-to-boundary, components, reference frame, supersonic/initial gauge pressure | `[confirmed in current script]` for several keys; enumerate locally |
| turbulence | intensity + hydraulic diameter, intensity + viscosity ratio, k/epsilon, k/omega, length scale | `[official-docs pattern]`, `[confirmed in current script]` uses intensity + hydraulic diameter |
| thermal | temperature, total temperature | `[needs local verification]` |
| multiphase | volume fraction / phase conditions | `[needs local verification]` |
| species | mass fractions if species transport is on | `[needs local verification]` |
| DPM | escape/trap/reflect/injection-related behaviour | `[needs local verification]` |

## 8.3 Turbulence specification allowed values

Official boundary-condition guide shows this pattern:

```python
# [official-docs pattern]
inlet_turbulence = pyfluent.VelocityInlet(settings_source=solver_session, name="cold-inlet").turbulence
print(inlet_turbulence.turbulence_specification.allowed_values())
# ['K and Omega', 'Intensity and Length Scale', 'Intensity and Viscosity Ratio', 'Intensity and Hydraulic Diameter']
```

For your inlet, test the actual mass-flow inlet path:

```python
# [needs local verification]
print(mfi.phase["mixture"].turbulence.turbulence_specification.allowed_values())
# or, depending on active tree:
print(mfi.turbulence.turbulence_specification.allowed_values())
```

---

# 9. Pressure outlet option atlas

```python
po = solver.settings.setup.boundary_conditions.pressure_outlet[outlet_name]
```

## 9.1 Project state pattern

```python
# [confirmed in current script]
# Purpose: steam outlet with gauge pressure, backflow turbulence, and zero backflow liquid volume fraction.

po.set_state({
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

## 9.2 Official multiphase pressure outlet phase pattern

```python
# [official-docs pattern]
outlet = solver_session.settings.setup.boundary_conditions.pressure_outlet["outlet"].phase
outlet["mixture"] = {
    "momentum": {"gauge_pressure": {"value": 95000}},
    "turbulence": {
        "turbulent_specification": "Intensity and Viscosity Ratio",
        "turbulent_intensity": 0.04,
        "turbulent_viscosity_ratio": 10,
    },
}
outlet["vapor"] = {
    "multiphase": {"volume_fraction": {"value": 0}}
}
```

## 9.3 Things to enumerate on pressure outlet

```python
# [needs local verification]
show_obj("pressure_outlet", po)
show_obj("pressure_outlet.momentum", po.momentum)
show_obj("pressure_outlet.turbulence", po.turbulence)
show_obj("pressure_outlet.phase", po.phase)
show_obj("pressure_outlet.multiphase", po.multiphase)
```

Common outlet subsettings:

| Area | Typical setting keys/ideas | Status |
|---|---|---|
| momentum | gauge pressure, backflow pressure type, direction method, radial equilibrium, target mass flow options | `[confirmed in current script]` for gauge/backflow keys; enumerate locally |
| turbulence | backflow intensity/hydraulic diameter, viscosity ratio, k/epsilon/omega values | `[confirmed in current script]`, `[official-docs pattern]` |
| multiphase | phase backflow volume fraction / volume fraction | `[confirmed in current script]` for phase-2 backflow volume fraction; official example uses phase volume fraction |
| thermal | backflow temperature | `[needs local verification]` |
| species | backflow mass fractions | `[needs local verification]` |
| DPM | particle escape/trap/reinject behaviour | `[needs local verification]` |

**Project gotcha:** pressure-outlet subsettings can appear inactive even if the top-level `set_state()` returns OK. Always verify:

```python
# [needs local verification]
pprint(po.get_state())
print("gauge pressure active:", po.momentum.gauge_pressure.is_active())
print("turbulence active:", po.turbulence.is_active())
```

---

# 10. Velocity inlet, pressure inlet, wall, and outlet variants

These are not your current final inlet/outlet types, but useful for agent experiments.

## 10.1 Velocity inlet

```python
# [official-docs pattern]
vi = solver.settings.setup.boundary_conditions.velocity_inlet["inlet"]
show_obj("velocity_inlet", vi)
show_obj("velocity_inlet.momentum", vi.momentum)
show_obj("velocity_inlet.turbulence", vi.turbulence)
```

Common areas:

| Area | Settings to inspect | Status |
|---|---|---|
| momentum | velocity magnitude, components, direction method, frame, swirl/angular velocity | `[needs local verification]` |
| turbulence | intensity/hydraulic diameter, viscosity ratio, k-epsilon/k-omega values | `[official-docs pattern]` |
| thermal | temperature | `[official-docs pattern]` |
| multiphase/species | phase volume fractions, species mass fractions | `[needs local verification]` |

## 10.2 Pressure inlet

Official cavitation example uses pressure inlet phase dictionaries:

```python
# [official-docs pattern]
pi = solver.settings.setup.boundary_conditions.pressure_inlet["inlet_1"].phase
pi["mixture"] = {
    "momentum": {
        "gauge_total_pressure": {"value": 500000},
        "supersonic_or_initial_gauge_pressure": {"value": 449000},
        "direction_specification_method": "Normal to Boundary",
    },
    "turbulence": {
        "turbulent_specification": "Intensity and Viscosity Ratio",
        "turbulent_intensity": 0.05,
        "turbulent_viscosity_ratio": 10,
    },
}
pi["vapor"] = {"multiphase": {"volume_fraction": {"value": 0}}}
```

## 10.3 Wall

```python
# [official-docs pattern]
wall = solver.settings.setup.boundary_conditions.wall["wall"]
show_obj("wall", wall)
show_obj("wall.momentum", wall.momentum)
show_obj("wall.thermal", wall.thermal)
show_obj("wall.multiphase", wall.multiphase)
```

Common wall areas:

| Area | What to inspect | Status |
|---|---|---|
| momentum | no-slip/slip, roughness, moving wall, shear | `[needs local verification]` |
| thermal | adiabatic, heat flux, temperature, convection, shell conduction | `[needs local verification]` |
| roughness | roughness height/constant | `[needs local verification]` |
| wall film | wall film if model enabled | `[official-docs pattern]` |
| multiphase | wetting/contact angle/wall adhesion-ish settings if active | `[needs local verification]` |
| DPM | trap/reflect/escape | `[needs local verification]` |

---

# 11. Materials and phase material assignment atlas

```python
materials = solver.settings.setup.materials
fluid_materials = materials.fluid
```

## 11.1 Manual material creation

```python
# [confirmed in current script]
name = "water-vapor-manual"
if name not in fluid_materials.get_object_names():
    fluid_materials.create(name=name)

fluid_materials[name].set_state({
    "name": name,
    "chemical_formula": "",
    "density": {"option": "value", "value": 5.7974339},
    "viscosity": {"option": "value", "value": 1.52062e-05},
})
```

Official example sometimes uses `"option": "constant"` instead of `"value"` for material property options:

```python
# [official-docs pattern] / [needs local verification for your local 2026 R1 shape]
solver.settings.setup.materials.fluid["water"] = {
    "density": {"option": "constant", "value": 1000},
    "viscosity": {"option": "constant", "value": 0.001},
}
```

## 11.2 Copy from database

```python
# [official-docs pattern]
solver.settings.setup.materials.database.copy_by_name(type="fluid", name="water-vapor")
```

## 11.3 Assign material to phases

```python
# [confirmed in current script]
phases = solver.settings.setup.models.multiphase.phases
phases["phase-1"].material = "water-vapor-manual"
phases["phase-2"].material = "water-liquid-manual"
```

Verification:

```python
# [needs local verification]
for ph in phases.get_object_names():
    print(ph, phases[ph].get_state())
```

---

# 12. Solution methods and numerics atlas

Your project script uses the `solution.methods` tree with `p_v_coupling`, `spatial_discretization`, and nested `discretization_scheme`.

```python
methods = solver.settings.solution.methods
spatial = methods.spatial_discretization
scheme = spatial.discretization_scheme
```

## 12.1 Project numerics pattern

```python
# [confirmed in current script]
methods.p_v_coupling.flow_scheme = "SIMPLE"
spatial.gradient_scheme = "green-gauss-node-based"
scheme.set_state({
    "pressure": "presto!",
    "mom": "second-order-upwind",
    "mp": "quick",
    "k": "second-order-upwind",
    "epsilon": "second-order-upwind",
})
```

## 12.2 Official cavitation example pattern

```python
# [official-docs pattern]
methods = solver_session.settings.solution.methods
methods.discretization_scheme = {
    "k": "first-order-upwind",
    "mom": "quick",
    "mp": "quick",
    "omega": "first-order-upwind",
    "pressure": "presto!",
}
methods.p_v_coupling.flow_scheme = "Coupled"
methods.pseudo_time_method.formulation.coupled_solver = "global-time-step"
methods.high_order_term_relaxation.enable = True
```

## 12.3 What to enumerate

```python
# [needs local verification]
show_obj("solution.methods", methods)
show_obj("methods.p_v_coupling", methods.p_v_coupling)
show_obj("methods.spatial_discretization", methods.spatial_discretization)
show_obj("methods.spatial_discretization.discretization_scheme", methods.spatial_discretization.discretization_scheme)
show_obj("methods.pseudo_time_method", methods.pseudo_time_method)
show_obj("methods.high_order_term_relaxation", methods.high_order_term_relaxation)
```

Important because model activation can reset schemes. Apply numerics **after** activating models, materials, and BCs.

---

# 13. Solution controls, relaxation, monitors

```python
controls = solver.settings.solution.controls
monitors = solver.settings.solution.monitor
```

## 13.1 Controls to inspect

```python
# [needs local verification]
show_obj("solution.controls", controls)
show_obj("solution.controls.pseudo_time_explicit_relaxation_factor", controls.pseudo_time_explicit_relaxation_factor)
```

Official cavitation example sets volume-fraction pseudo-time explicit relaxation factor:

```python
# [official-docs pattern]
solver.settings.solution.controls.pseudo_time_explicit_relaxation_factor.global_dt_pseudo_relax["mp"] = 0.3
```

Likely controls to inspect:

| Area | Why |
|---|---|
| under-relaxation factors | steady segregated stability |
| pseudo-time relaxation | coupled/pseudo-transient runs |
| Courant number / time scale | transient/pseudo-transient stability |
| equation controls | may appear/disappear with models |

## 13.2 Residual monitors

```python
# [official-docs pattern]
resid_eqns = solver.settings.solution.monitor.residual.equations
print(resid_eqns.get_object_names())
resid_eqns["continuity"].absolute_criteria = 1e-5
```

In multiphase, look for equations such as `vf-vapor`, `vf-phase-1`, `vf-phase-2`, etc. Names are local-case dependent.

```python
# [needs local verification]
for eq in resid_eqns.get_object_names():
    print(eq, resid_eqns[eq].get_state())
```

---

# 14. Initialization, running, and checkpointing

## 14.1 Case-only setup boundary

PyFluent may configure the models, boundary conditions, solution methods, monitors, and
native autosave settings, then write a case-only artifact. It must stop before initialization
and long-run iteration. This keeps the solver independent of the Python client's lifetime.

## 14.2 Fluent-native initialization and run

Start the solve from Fluent's GUI, Fluent console, or a Fluent-native journal. For example:

```text
/solve/initialize/hyb-initialization
/solve/iterate 5000
```

Set the Calculation Activities / Autosave interval in Fluent before the run (for example,
every 500 steady iterations), use a remote root name, and retain at least two recent paired
case/data checkpoints. Reconnect with a fresh client only to inspect progress or recover from
the newest complete native checkpoint.

## 14.3 Prohibited client-side run pattern

Do not wrap Fluent iteration commands in a Python `for`/`while` loop, and do not use Python to
decide when to write checkpoints or the final data file. The old examples in earlier versions
of this atlas are historical patterns and are not approved for current runs.

---

# 15. Reports and diagnostics atlas

```python
fluxes = solver.settings.results.report.fluxes
```

## 15.1 Project flux pattern

```python
# [confirmed in current script]
if fluxes.is_active():
    zones = [inlet_name, outlet_name]
    mixture = fluxes.get_mass_flow(domain="mixture", zones=zones)
    vapor = fluxes.get_mass_flow(domain="phase-1", zones=zones)
    liquid = fluxes.get_mass_flow(domain="phase-2", zones=zones)
```

Project-specific checks:

```python
# [confirmed in current script]
vapor_recovery = abs(vapor[outlet_name]) / vapor[inlet_name]
liquid_carryover = abs(liquid[outlet_name]) / liquid[inlet_name]
```

Do **not** fail just because total mixture mass imbalance is large in the one-outlet branch; liquid is intentionally not leaving the steam outlet.

## 15.2 More report areas to enumerate

```python
# [needs local verification]
reports = solver.settings.results.report
show_obj("results.report", reports)
show_obj("results.report.fluxes", reports.fluxes)
show_obj("results.report.surface_integrals", reports.surface_integrals)
show_obj("results.report.volume_integrals", reports.volume_integrals)
```

Useful report types to look for:

| Report | Use |
|---|---|
| fluxes mass flow | inlet/outlet balance, phase recovery |
| area-weighted average | pressure, velocity, volume fraction at outlet |
| mass-weighted average | phase/mixture outlet values |
| surface integrals | forces, flow rate, area |
| volume integrals | inventory of phase volume in separator |
| report definitions | create persistent monitors/files |

---

# 16. Full local option dump workflow for your separator case

Run this on your local machine with Fluent 2026 R1 after loading `trial4.msh`. It creates a text map that an agent can reference.

```python
# [needs local verification]
# Save as: dump_pyfluent_options_trial4.py

from pathlib import Path
from pprint import pformat
import ansys.fluent.core as pyfluent

MESH = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4.msh")
OUT = MESH.with_name("trial4_pyfluent_2026R1_live_options_dump.txt")

solver = pyfluent.Solver.from_install(precision="double", processor_count=2, dimension=3)


def safe(label, fn, default=None):
    try:
        return fn()
    except Exception as exc:
        return f"<FAILED {label}: {type(exc).__name__}: {exc}>" if default is None else default


def block(label, obj):
    lines = [f"\n=== {label} ==="]
    for name, fn in [
        ("is_active", lambda: obj.is_active()),
        ("child_names", lambda: obj.child_names),
        ("command_names", lambda: obj.command_names),
        ("get_object_names", lambda: obj.get_object_names()),
        ("allowed_values", lambda: obj.allowed_values()),
        ("get_state", lambda: obj.get_state()),
    ]:
        lines.append(f"-- {name} --")
        lines.append(pformat(safe(name, fn)))
    return "\n".join(lines)

try:
    solver.settings.file.read_mesh(file_name=str(MESH))

    sections = []
    sections.append(block("setup.models", solver.settings.setup.models))
    sections.append(block("setup.models.energy", solver.settings.setup.models.energy))
    sections.append(block("setup.models.viscous", solver.settings.setup.models.viscous))
    sections.append(block("setup.models.multiphase", solver.settings.setup.models.multiphase))
    sections.append(block("setup.boundary_conditions", solver.settings.setup.boundary_conditions))

    bc = solver.settings.setup.boundary_conditions
    bc_state = safe("bc get_state", lambda: bc.get_state(), default={})
    sections.append("\n=== boundary_conditions state ===\n" + pformat(bc_state))

    # Optional: convert to your intended types first, then inspect again.
    # bc.set_zone_type(zone_list=["inlet"], new_type="mass-flow-inlet")
    # bc.set_zone_type(zone_list=["outlet"], new_type="pressure-outlet")

    for bctype in ["velocity_inlet", "mass_flow_inlet", "pressure_inlet", "pressure_outlet", "wall"]:
        container = safe(bctype, lambda n=bctype: getattr(bc, n))
        if isinstance(container, str):
            sections.append(f"\n=== {bctype} ===\n{container}")
            continue
        sections.append(block(f"bc.{bctype}", container))
        names = safe(f"{bctype}.get_object_names", lambda c=container: c.get_object_names(), default=[])
        for nm in names:
            obj = container[nm]
            sections.append(block(f"bc.{bctype}[{nm}]", obj))
            for child in ["momentum", "turbulence", "thermal", "multiphase", "phase", "species", "discrete_phase"]:
                child_obj = safe(child, lambda o=obj, c=child: getattr(o, c))
                if not isinstance(child_obj, str):
                    sections.append(block(f"bc.{bctype}[{nm}].{child}", child_obj))

    # Activate project-relevant models and dump again.
    try:
        solver.settings.setup.models.multiphase.model = "mixture"
    except Exception:
        solver.settings.setup.models.multiphase.models = "mixture"
    solver.settings.setup.models.viscous.model = "k-epsilon"
    solver.settings.setup.models.viscous.k_epsilon_model = "rng"
    solver.settings.setup.models.energy.enabled = False

    sections.append("\n\n######## AFTER PROJECT MODEL ACTIVATION ########")
    sections.append(block("models.after", solver.settings.setup.models))
    sections.append(block("viscous.after", solver.settings.setup.models.viscous))
    sections.append(block("multiphase.after", solver.settings.setup.models.multiphase))
    sections.append(block("multiphase.phases.after", solver.settings.setup.models.multiphase.phases))

    OUT.write_text("\n".join(sections), encoding="utf-8")
    print(f"WROTE {OUT}")
finally:
    solver.exit()
```

---

# 17. Error-handling recommendations for broad option scripts

```python
# [confirmed in current script style]
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
```

Critical for your project:

- mesh missing
- Fluent launch failure
- inlet/outlet not detected
- boundary type conversion failure
- multiphase model activation failure
- phase material assignment failure
- operating pressure/gravity failure
- inlet mass flow failure
- outlet gauge pressure failure
- initialization failure
- final case/data write failure

Non-blocking warnings:

- inactive outlet turbulence/backflow subsettings if gauge pressure is correctly applied
- optional RNG swirl/differential-viscosity settings unavailable
- optional phase diameter unavailable
- total mixture imbalance in one-outlet branch
- missing DPM/species/radiation trees when those models are off

---

# 18. Known gotchas from this project

1. Close Fluent/Workbench before launching local PyFluent if local Student sessions conflict.
2. Mesh-only loads may expose only default material state until models/materials are created.
3. Model activation can reset numerical schemes. Apply solution methods after model setup.
4. In your confirmed 2026 R1 path, operating pressure is scalar: `op.operating_pressure = 0`, not a dictionary.
5. Pressure-outlet subsettings may appear inactive even if `set_state()` returns OK. Verify the final `get_state()` and inspect key leaves with `.is_active()`.
6. Avoid streaming full Fluent iteration logs into Codex/agent context. Write logs to file and print compact summaries.
7. The exact multiphase selector may differ between `.model` and `.models`; your current script uses `.model`, while one official example uses `.models`.
8. `phase-1` / `phase-2` names may change if phases are renamed. Prefer `mp.phases.get_object_names()` before assigning materials or BC phase states.
9. Boundary state dictionary shape is model-dependent. After converting zone types and enabling multiphase, re-query `bc.get_state()` before applying a large nested `set_state()`.
10. For one-outlet separator branch, judge success using vapor recovery and liquid carryover, not total mixture net flow alone.

---

# 19. Official references used

- PyFluent session/settings object interface: `get_state()`, `set_state()`, `is_active()`, `allowed_values()`, `min()`, `max()`.
  - https://fluent.docs.pyansys.com/version/stable/user_guide/session/session.html
- PyFluent settings object / `flobject` API.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/flobject.html
- PyFluent `setup.models` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/models.html
- PyFluent `models.energy` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/energy.html
- PyFluent `models.viscous` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/viscous.html
- PyFluent `setup.boundary_conditions` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/boundary_conditions.html
- PyFluent boundary conditions user guide.
  - https://fluent.docs.pyansys.com/version/stable/user_guide/solver_settings/set_up/boundary_conditions.html
- PyFluent `mass_flow_inlet` / `mass_flow_inlet_child` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/mass_flow_inlet.html
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/mass_flow_inlet_child.html
- PyFluent `pressure_outlet` / `pressure_outlet_child` API reference.
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/pressure_outlet.html
  - https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/pressure_outlet_child.html
- PyFluent cavitation example using mixture, pressure inlet/outlet phase dictionaries, operating pressure, methods, residuals, initialization, and run APIs.
  - https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/modeling_cavitation.html
- Ansys Developer blog on PyFluent Settings APIs and objects.
  - https://developer.ansys.com/blog/all-you-need-know-about-pyfluents-settings-apis-and-objects
