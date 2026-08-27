---
name: pool-patch-volume
description: "Use when a loaded Ansys Fluent session needs a reusable pool initial-condition workflow: inspect the live mesh, create or reuse an axis-aligned cell register for a liquid pool, patch the selected liquid phase, calculate selected-cell and phase-integrated volume, and optionally estimate or reduce pressure over selected regions. Do not use this for brine-outlet backflow or outlet priming unless that is explicitly requested."
---

# Pool Patch Volume

## Purpose

Use this skill for a pool patch that must work across meshes and case files. The pool is a cell selection, normally an axis-aligned hexahedral register bounded by a user-supplied height or other geometry limits; it is an initial condition, not a claim about the eventual steady liquid level.

The important output is two related measurements:

- `V_geom`: the geometric volume of all cells selected by the pool register.
- `V_liq`: the volume occupied by the requested liquid phase, calculated as the phase volume fraction times cell volume.

Always report both. A successful patch can still produce `V_liq < V_geom` because of initialization details, shared cells, or a non-binary phase field.

## Scope and safety boundaries

- Treat the requested Fluent server ID (for example, `student`) as a routing alias. Inspect the live session before changing it; do not assume that alias identifies a particular case or mesh.
- Parameterize the register name, mesh bounds, pool cutoff, fluid zone, mixture/phase domain, patch variable, and liquid phase. Never reuse bounds from another mesh without reading them from the current session or receiving them explicitly.
- Search existing PyFluent setup code and live cell registers before creating anything. Reuse an existing pool register only after reading back its type, bounds, and membership intent.
- If a register with the chosen name has incompatible bounds, do not silently overwrite it. Choose a new name or rebuild it only when the user has authorized replacing that selection.
- Keep the operation pool-only. Do not call brine-outlet boundary-distance registers, backflow volume-fraction helpers, or outlet-priming routines. Boundary backflow settings and an initial pool patch are different operations.
- Do not alter boundary conditions, run iterations, advance timesteps, or save case/data files unless the user asks for those actions. Fluent may need initialization to make the patch legal; initialize only as required and record that it occurred.
- After model, phase, register, or domain creation, reacquire the affected Settings API objects and read them back. Fluent changes the object tree during these operations, so stale handles are unsafe.

## Workflow

### 1. Discover the implementation and live state

Read the repository’s root instructions and the applicable PyAnsys guide. Search for prior pool-register and patch implementations before writing a new one. Existing implementations are useful references, but their mesh bounds and pool height are case-specific.

Connect to the requested Fluent session using the repository’s configured PyFluent environment and connection helper. Record, before mutation:

- Fluent version and connection/server alias.
- Loaded case/mesh identity, if the live API exposes it; otherwise label case identity as unavailable.
- Cell zones and the intended fluid zone.
- Whether VOF or another multiphase model is active.
- Phase names, phase domains, and which phase is the liquid.
- Existing cell-register names and any register that appears to represent the pool.

If the session contains only a mesh and no multiphase model, activate only the model and phase structure needed for the requested pool patch. Follow Fluent’s dependency order: global models, materials, phases, then solution settings. Inspect allowed values and read back each change. Do not import boundary setup merely because an existing combined setup script contains it.

### 2. Define and verify the pool register

Derive the selection from the current mesh. For a height-based pool, use the current mesh extents in the unconstrained directions and a user-supplied cutoff in the vertical direction. Check that the cutoff lies within the mesh and that the box intersects the intended fluid zone rather than a solid, outlet-only region, or unrelated pipe volume.

The canonical register state is equivalent to:

```python
{
    "type": "option hexahedron",
    "min_point": [xmin, ymin, zmin],
    "max_point": [xmax, y_cut, zmax],
    "inside": True,
}
```

Use the live Fluent Settings API, reacquire the register, set the state, and read it back. A typical pattern is:

```python
registers = solver.settings.solution.cell_registers
registers.create(name=register_name)
register = solver.settings.solution.cell_registers[register_name]
register.set_state({...})
state = register.get_state()
# Compare state['min_point'], state['max_point'], and state['inside'] explicitly.
```

Adapt the exact accessors to the installed PyFluent version. Do not infer selected-cell count from the box dimensions; obtain the marked-cell count from Fluent or a validated cell query.

### 3. Initialize and patch only the liquid phase

If Fluent requires initialized fields, use the appropriate initialization command (for example, hybrid initialization) and wait for its completion. Do not iterate or advance time as part of this skill.

Patch the liquid phase using the canonical operation:

```python
solver.settings.solution.initialization.patch.calculate_patch(
    domain=liquid_phase_domain,       # often "phase-2", but inspect first
    registers=[register_name],
    variable=patch_variable,          # often "mp"
    value=1.0,
)
```

The patch variable is commonly Fluent’s phase-volume-fraction alias `mp`; verify the phase mapping instead of assuming that phase 2 is liquid. Confirm that Fluent accepted the command and capture its marked-cell count. Do not treat a successful command as proof that every selected cell now has a liquid fraction of exactly one.

### 4. Calculate the volume from the selected cells

Query the selected register through Fluent’s volume-integral/report API where the installed release supports register locations. The geometric query should be equivalent to:

```python
V_geom = solver.settings.results.report.volume_integrals.get_volume(
    cell_zones=[register_name],
    locations={"geometry": [register_name]},
    cell_function="cell-volume",
    current_domain="mixture",
)
```

Validate the result: the returned report must identify the requested register and return a finite, positive value. Some PyFluent/Fluent releases reject cell registers as report locations; others accept this call. If unsupported or ambiguous, do not silently substitute the full fluid-zone volume. Use a supported cell-zone/field reduction, a release-compatible expression, or an offline cell-volume query and label the fallback method.

Then calculate actual phase volume with a phase-volume-fraction field. In current Fluent releases the field may be exposed as `phase-2-vof` even though the patch variable is `mp`; inspect available field names rather than assuming the spelling:

```python
V_liq = solver.settings.results.report.volume_integrals.compute_volume_integral(
    locations={"geometry": [register_name]},
    cell_function="phase-2-vof",
    current_domain="mixture",
)
```

Use the installed API’s exact parameter names if they differ. Where useful, also calculate the complementary vapor-phase integral, then check:

```text
V_liq + V_vapor ≈ V_geom
fill_fraction = V_liq / V_geom
```

Use the selected-cell count separately. Report `V_geom` as the mesh volume represented by the patch region and `V_liq` as the initialized liquid inventory. Do not report `V_geom` as “water volume” unless the phase readback supports that conclusion.

### 5. Optional pressure information

Treat pressure as supplementary case information, not an automatic recommendation. The same register is a useful spatial filter for pressure, but the strength of any interpretation depends on the user’s intent and the state of the case.

For a rough hydrostatic estimate in a mostly static liquid:

```text
p(y) ≈ p_ref + rho * g * (y_ref - y)
```

Record the density, gravity direction, elevation reference, and whether the result is gauge or absolute pressure. Use the actual material density and operating pressure from the live case; never assume water density or a zero-pressure reference. This estimate is useful for exploratory screening or an order-of-magnitude check, but it does not include inlet losses, acceleration, turbulence, swirl, or vapor dynamics.

For a Fluent field reduction, use the same register or additional sub-registers for regions of interest. Typical quantities are volume-weighted average static pressure, minimum, maximum, and pressure distribution. In the Settings API, the pattern is equivalent to:

```python
p_avg = solver.settings.results.report.volume_integrals.get_volume_average(
    cell_zones=[register_name],
    locations={"geometry": [register_name]},
    cell_function="pressure",       # inspect whether this is gauge/static pressure
    current_domain="mixture",
)
```

Inspect available field names before querying. `pressure` commonly represents static gauge pressure, while absolute pressure may be exposed separately. Do not mix the two in comparisons. If a register contains both liquid and vapor, its pressure average is a mixture-region average; for liquid-only pressure, use a phase-fraction-conditioned selection, a liquid-only register, or a clearly liquid subregion. For walls, inlets, and outlets, use face/surface reductions and pressure force rather than a cell-volume average.

Choose the interpretation according to intent and case state:

- Exploratory geometry or design screening: provide the hydrostatic estimate and register-based pressure statistics as low-strength, clearly labelled approximate information.
- Freshly initialized or patched case with no physical iterations: use pressure only as an initialization diagnostic. Do not make an operational or design recommendation from it.
- Converged steady case or a documented transient snapshot: pressure reductions can support a stronger case-specific comparison, provided the relevant monitors, residuals, timestep, and boundary conditions are recorded.
- Safety, equipment rating, or other high-consequence decision: treat this workflow as evidence gathering only. Require validated physics, mesh/time-step checks, convergence or uncertainty evidence, and domain expertise before recommending an action.

If the user asks for a recommendation, first identify which of these intents applies and state the confidence level. Keep pressure as additional information when the user only requested pool volume; do not let an optional pressure estimate silently change the requested workflow.

### 6. Verify and hand off

Before handing off, read back and record:

- Register name, type, bounds, `inside` flag, and selected-cell count.
- Liquid phase name/domain and patch variable/value.
- Geometric register volume, phase-integrated liquid volume, optional complementary phase volume, and fill fraction.
- Optional pressure results: pressure type/reference, hydrostatic estimate, region, average/minimum/maximum, and case state used for the reduction.
- Whether initialization ran, whether any iterations/timesteps ran, and whether any boundary condition changed.
- Whether a brine-outlet register or outlet-priming operation was intentionally absent.
- Case/data save paths only if files were explicitly saved; otherwise state that the live session was left unsaved.
- Uncertainties, especially unavailable case identity, register-query fallback, or a mismatch between geometric and phase-integrated volumes.

A concise result should look like:

```text
Pool register: <name>
Selection: x=[...,...], y<=<cutoff> m, z=[...,...]
Cells marked: <count>
Geometric selected-cell volume: <V_geom> m^3
Liquid phase volume after patch: <V_liq> m^3
Liquid fill fraction of selection: <V_liq/V_geom>
Initialization: <method or not required>
Iterations/timesteps: none
Outlet priming: not performed
```

## Failure handling

- Bare mesh with no VOF: activate the minimum required multiphase model and reacquire Settings objects; do not run the combined boundary-setup helper.
- Register creation succeeds but later calls fail: reacquire `solution.cell_registers`, the register, and the results-report object after each tree mutation.
- Volume result is missing, zero, or looks like the whole domain: mark the measurement unverified and use a supported fallback rather than guessing.
- `V_liq` differs materially from `V_geom`: report both values, check phase mapping and initialization state, and investigate cell membership; never hide the discrepancy by replacing one with the other.
- The requested pool intersects an unintended zone: stop before patching and ask for corrected bounds or an explicit fluid-zone restriction.

## Repository references

- Existing loaded-mesh pool implementation: `PyAnsys/scripts/setup/build_02d_vof_ic0_ic1_ic2_from_loaded_mesh.py`
- Existing pool-height case preparation: `PyAnsys/scripts/setup/prepare_02d_fine_patch_cases_and_queue.py`
- Local Fluent guidance: `docs/agent-guides/fluent-guidance.md`
- PyFluent `calculate_patch` reference: https://fluent.docs.pyansys.com/version/stable/api/solver/_autosummary/settings/calculate_patch.html
- PyFluent volume-integral reference: https://fluent.docs.pyansys.com/version/dev/api/solver/_autosummary/settings/volume_integral.html
