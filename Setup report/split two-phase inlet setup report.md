# Two-Zone Split Two-Phase Inlet Setup Report

## 1. Objective

Convert the current baseline inlet setup into a more realistic two-zone inlet where:

- the **outer-wall half** of the inlet carries **liquid water**,
- the **inner half** of the inlet carries **steam**.

The aim is to keep the Fluent setup as close as possible to [tangential input setup report.md](tangential%20input%20setup%20report.md), which you have clarified is the **spiral-inlet** baseline report, while changing only what is required to represent a segregated two-phase inlet.

## 2. Direct answer to your main question

Yes, the cleanest and most robust way to do this is to change the **geometry/meshing stage first**, then apply the new boundary conditions in Fluent.

You do **not** need:

- a separate fluid domain for steam and water,
- a full solver rebuild,
- a new turbulence or multiphase model just for this inlet change.

You **do** need:

- the inlet face split into **two separate boundary zones**,
- those two zones imported into Fluent as two named inlet boundaries,
- phase assignment made separately on each inlet zone.

## 3. What should stay the same from the current baseline

Unless you decide otherwise, keep these the same as the current baseline spiral-inlet report:

- Solver: `Pressure-Based`
- Time: `Steady`
- Gravity: on
- Operating pressure: `0 Pa`
- Multiphase model: `Mixture`
- Primary phase: steam/gas
- Secondary phase: liquid water
- Turbulence: `RNG k-epsilon`
- Energy equation: off
- Material properties: same densities, viscosities, and surface tension
- Outlet type and pressure
- Wall treatment
- Solution methods: `SIMPLE`, `PRESTO!`, `Second Order Upwind`, `QUICK`
- Initialization: `Hybrid Initialization`

## 4. What changes

Only three parts need to change:

1. **Geometry/mesh boundary definition**
   - Split one inlet face into two halves.
2. **Boundary-condition definition**
   - Replace one inlet BC with two inlet BCs.
3. **Run interpretation**
   - Check whether the split inlet causes unrealistic velocity imbalance or convergence issues.

## 5. Geometry clarification

Geometry type is now confirmed as:

- **spiral inlet**

The remaining important ambiguity is not the geometry type anymore, but the exact meaning of:

- `left side`
- `right side`
- `inner side`
- `outer wall side`

on the actual spiral-inlet face and the viewing direction.

This report assumes the spiral inlet still has **one identifiable inlet face that can be split into a wall-adjacent half and a separator-core-adjacent half**.

## 6. Recommended implementation route

### Preferred route

Split the inlet face in CAD/geometry, remesh, then assign:

- `inlet_liquid_outer`
- `inlet_steam_inner`

as two separate `Mass-Flow Inlet` boundaries in Fluent.

### Why this route is preferred

- It is the most stable and transparent setup.
- It is easy to document and repeat.
- It keeps the rest of the solver setup nearly unchanged.
- It avoids UDF/profile complexity for a first realistic-inlet test.

### Routes not recommended for the first attempt

- **Do not rely only on patching after initialization.**
  - Patching changes the initial field, not the inlet boundary itself.
- **Do not keep one inlet face and try to fake the split only with post-processing.**
  - The solver will still apply a uniform boundary condition.
- **Do not jump to a UDF first unless the simple face split proves inadequate.**
  - A UDF is only worth it if you later need a smooth spatial phase-fraction profile instead of a sharp half-half split.

## 7. Step-by-step setup workflow

### Step 1. Duplicate the current baseline case

Before editing anything, create a separate case version for the split-inlet test.

Suggested case label:

- `baseline_split_inlet_v1`

This keeps the original baseline intact for A/B comparison.

### Step 2. Define the split direction clearly

Before touching the geometry, define which half is which.

For this setup, use:

- **outer half** = half of the inlet face closer to the separator outer wall
- **inner half** = half of the inlet face closer to the separator core / inner radius side

Do not use only `left` and `right` in the final CAD names, because they depend on view orientation.

Use names like:

- `inlet_liquid_outer`
- `inlet_steam_inner`

### Step 3. Split the inlet face in geometry

In SpaceClaim or DesignModeler:

1. Open the geometry used by the current baseline.
2. Locate the inlet face that currently becomes the single inlet boundary in Fluent.
3. Create a split line through the face so the face is divided into **two equal-area halves**.
4. Make sure the split creates **two separate faces**, not just a sketch line.
5. Name the two faces immediately:
   - `inlet_liquid_outer`
   - `inlet_steam_inner`

### Step 4. What exactly to split

If your spiral inlet enters through a single identifiable inlet face, the split should be made so that:

- one half touches the **outer wall side**,
- the other half touches the **inner/core side**.

You normally do **not** need to split the whole fluid body into two volumes.

You only need the inlet boundary face split into two boundary zones.

If the inlet includes a short upstream duct section and you want a cleaner geometric transition, you may also partition a short inlet length upstream of the vessel entrance. That is optional, not mandatory for the first test.

### Step 5. Remesh the model

After the inlet face is split:

1. Update the geometry in Meshing.
2. Confirm the two new named selections appear.
3. Keep the same global mesh strategy as the baseline.
4. Keep the same local refinements already used near the inlet and important boundaries.
5. Regenerate the mesh.
6. Check that the mesh remains conformal across the inlet opening and that no unwanted non-manifold or sliver geometry was introduced by the split.

### Step 6. Export/import the mesh into Fluent

When the mesh is loaded into Fluent, confirm that the boundary list now contains:

- `inlet_liquid_outer`
- `inlet_steam_inner`

and that the old single inlet is no longer the only inlet boundary.

### Step 7. Keep the general Fluent model setup unchanged

Keep the same settings as the baseline unless you are forced to change them for stability:

- General
- Operating conditions
- Models
- Materials
- Cell zone conditions
- Outlet
- Walls
- Solution methods
- Initialization method

This is important because the inlet representation is supposed to be the main A/B change.

### Step 8. Set the two inlet boundary conditions

Use `Mass-Flow Inlet` for both inlet zones.

Different Fluent versions may show slightly different inlet fields for the `Mixture` model. The exact field names can vary, but the physical target should stay the same:

- liquid-side boundary = liquid-only feed with the liquid-side mass flow
- steam-side boundary = steam-only feed with the steam-side mass flow

#### 8A. Liquid-side inlet

Boundary:

- `inlet_liquid_outer`

Recommended target state:

- pure liquid water on this half
- no steam on this half

If Fluent asks for phase fraction:

- liquid water fraction = `1.0`
- steam/gas fraction = `0.0`

If Fluent asks for secondary-phase volume fraction and liquid water is the secondary phase:

- secondary phase volume fraction = `1.0`

#### 8B. Steam-side inlet

Boundary:

- `inlet_steam_inner`

Recommended target state:

- pure steam on this half
- no liquid water on this half

If Fluent asks for phase fraction:

- liquid water fraction = `0.0`
- steam/gas fraction = `1.0`

If Fluent asks for secondary-phase volume fraction and liquid water is the secondary phase:

- secondary phase volume fraction = `0.0`

### Step 9. Recommended mass-flow allocation

If your goal is to preserve the same overall inlet mass rates as the baseline case, assign:

- `inlet_liquid_outer` total mass flow = **116.92 kg/s**
- `inlet_steam_inner` total mass flow = **80.69 kg/s**

This preserves the baseline total:

- total inlet mass flow = **197.61 kg/s**

This is the simplest interpretation of the split-inlet idea because it keeps the same total steam and liquid feed rates while changing only the spatial distribution.

## 8. Very important physical warning

This half-half split with pure phases is simple, but it can produce a very strong velocity mismatch because steam density is much lower than liquid density.

If each half has area `A_inlet / 2`, then the phase inlet velocities are approximately:

- `V_liquid = 116.92 / (881.77 * A_half)`
- `V_steam = 80.69 / (5.73 * A_half)`

where:

- `A_half = A_inlet / 2`

So the steam-side superficial velocity may become much larger than the liquid-side velocity.

This is not automatically wrong, but it is a **high-risk assumption** and should be checked carefully.

## 9. Practical interpretation of that warning

This means there are really two levels of “realism”:

### Level 1: simple segregated inlet

- outer half = pure liquid
- inner half = pure steam
- preserve baseline phase mass-flow rates

This is the best first implementation because it is easy to build and easy to compare against the original case.

### Level 2: more physically smoothed inlet

If the pure half-half split proves too abrupt or too unstable, a later refinement could use:

- a non-uniform profile,
- more than two zones,
- a short upstream duct,
- a profile file or UDF.

Do **not** start there unless needed.

## 10. Fluent setup checklist

Use this as the execution checklist.

| Done | Item | Target |
|---|---|---|
| ☐ | Duplicate baseline case | `baseline_split_inlet_v1` |
| ☐ | Confirm actual geometry type | Spiral inlet |
| ☐ | Identify wall-side half | Outer-wall half |
| ☐ | Identify core-side half | Inner half |
| ☐ | Split inlet face | Two separate faces |
| ☐ | Create names | `inlet_liquid_outer`, `inlet_steam_inner` |
| ☐ | Remesh | Same baseline strategy |
| ☐ | Import into Fluent | Two inlet zones visible |
| ☐ | Keep same solver family | `Pressure-Based`, steady |
| ☐ | Keep same multiphase model | `Mixture` |
| ☐ | Keep same turbulence model | `RNG k-epsilon` |
| ☐ | Keep same materials | baseline properties |
| ☐ | Set liquid inlet type | `Mass-Flow Inlet` |
| ☐ | Set steam inlet type | `Mass-Flow Inlet` |
| ☐ | Set liquid-half phase state | liquid = 1.0 |
| ☐ | Set steam-half phase state | liquid = 0.0 |
| ☐ | Set liquid-half mass flow | `116.92 kg/s` |
| ☐ | Set steam-half mass flow | `80.69 kg/s` |
| ☐ | Keep outlet pressure | same as baseline |
| ☐ | Keep solution methods | same as baseline |
| ☐ | Initialize | `Hybrid Initialization` |
| ☐ | Check residuals and mass balance | mandatory |
| ☐ | Check for unrealistic steam jetting | mandatory |

## 11. Initialization and running guidance

Start with the same initialization strategy:

- `Hybrid Initialization`

Then run a short first test and check:

- residual trend,
- inlet-to-outlet mass balance,
- volume-fraction contour near the inlet,
- whether one phase penetrates unrealistically across the other half immediately,
- whether the steam-side jet is numerically too aggressive.

## 12. What to inspect after the first run

Compare the split-inlet case against the original uniform/tangential baseline using the same plots:

1. Pressure drop across the separator
2. Gas/liquid distribution near the inlet region
3. Swirl development in the upper chamber
4. Steam outlet phase purity trend
5. Liquid carryover tendency
6. Convergence behavior versus the original case

## 13. Common failure modes

### Failure mode 1. The two inlet zones do not appear in Fluent

Cause:

- the inlet was only sketched, not actually split into two faces.

Fix:

- go back to geometry and confirm two separate faces exist and are named.

### Failure mode 2. The case diverges much faster than the baseline

Cause:

- the split inlet creates a sharper and more extreme phase/velocity jump than the uniform inlet.

Fix:

- verify mass-flow values,
- verify phase fractions,
- verify inlet orientation,
- consider a shorter first run with tighter monitoring before changing numerics.

### Failure mode 3. The “liquid side” and “steam side” are reversed

Cause:

- left/right naming based on camera view instead of geometry meaning.

Fix:

- rename zones by physics meaning, not screen direction.

### Failure mode 4. The setup is physically too abrupt

Cause:

- pure-phase half-half split may be too idealized.

Fix:

- keep this as the first A/B test, then move to a graded profile only if results or convergence demand it.

## 14. Recommended decision for the first implementation

For the first split-inlet test, use this exact strategy:

- split the inlet face into **two equal halves**,
- assign the **outer-wall half** to **pure liquid water**,
- assign the **inner half** to **pure steam**,
- preserve the baseline phase mass-flow totals:
  - liquid = `116.92 kg/s`
  - steam = `80.69 kg/s`
- keep all other Fluent settings the same as the baseline report.

This gives the cleanest one-change-at-a-time comparison.

## 15. Questions that still need your confirmation

Please confirm these before the actual case build:

1. When you say `left side` and `inner side`, can you confirm which side is the **outer-wall-adjacent half** on your actual inlet face?
2. Do you want the first test to use:
   - **pure half-half split with preserved phase mass flows**,
   - or a softer split where each half still contains a small amount of the other phase?
3. Does your current CAD already include a short inlet duct section, or is the inlet just a single entry face into the separator?

## 16. Bottom-line recommendation

Start from **geometry/mesh**, not from Fluent alone.

Split the existing inlet into two named inlet boundaries, keep the current solver/model settings, and use the split inlet as the single controlled change for the next A/B comparison against the baseline case.
