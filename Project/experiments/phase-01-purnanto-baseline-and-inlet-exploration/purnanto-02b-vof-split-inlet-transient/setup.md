> **Retired source:** Setups/past/archived/02b-vof-split-inlet-transient.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# VOF Split-Inlet Setup Report (Fluent 2024 R1)

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02b` |
| Lifecycle | `archived` |
| Role | VOF transient side experiment |
| Parent setup | [Phase 1 historical inlet index](../index.md) |
| Evidence-use label | invalid qualitative run; no numerical efficiency/DPM report |
| Outcome | rejected |
| Linked report | none |

This report mirrors the structure of [00-baseline-spiral-boc-reference.md](../purnanto-00-reference-spiral-boc/setup.md), but captures your current run configuration:

- Fluent `2024 R1`
- `VOF` (instead of Mixture)
- Two-zone split inlet (`water` half + `steam` half)
- `Transient`
- No patching step for now

## A. Geometry, mesh, and modelling scope

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Geometry | Separator design | **Spiral-inlet BOC design** | Geometry | Kept from tangential baseline |
| Mesh | Mesh type | **Unstructured tetrahedral** | Meshing | Kept from baseline unless you changed mesh |
| Inlet topology | Inlet zone layout | **Two separate inlet boundaries** | Geometry/Meshing | `inlet_water` and `inlet_steam` (or equivalent names) |
| Scope | Inlet realism change | **Main controlled change** | Modelling decision | This run focuses on inlet/interface behavior |

## B. Fluent launch

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Launch | Dimension | **3D** | Fluent launcher | Same as baseline |
| Launch | Precision | **Double Precision** | Fluent launcher | Recommended |

## C. General solver settings

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| General | Solver | **Pressure-Based** | General | Confirmed |
| General | Time | **Transient** | General | Changed from steady baseline |

## D. Operating conditions

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Operating Conditions | Gravity | **On** | Operating Conditions | Keep baseline convention |
| Operating Conditions | Gravity vector | **(0, -9.81, 0) m/s²** | Operating Conditions | Assuming Fluent `y` is vertical |
| Operating Conditions | Operating pressure | **0 Pa** | Operating Conditions | Keep same gauge/absolute convention as baseline |

## E. Models

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Models | Multiphase model | **VOF** | Models > Multiphase | Changed from Mixture |
| Models | VOF phases | **2 phases** | Models > Multiphase | Primary: steam, Secondary: water |
| Models | VOF formulation | **Implicit (assumed current)** | Models > Multiphase | Use explicit only if needed for interface options |
| Models | Turbulence model | **RNG k-epsilon** | Models > Viscous | Kept from baseline |
| Models | Energy equation | **Off** | Models > Energy | Same isothermal assumption as baseline |

## F. Materials and phase pairing

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Materials | Primary phase | **Steam/Vapor** | Phases/Materials | Confirm mapping in VOF panel |
| Materials | Secondary phase | **Liquid water** | Phases/Materials | Confirm mapping in VOF panel |
| Materials | Property set | **Baseline property set** | Materials | Keep same constants unless intentionally changed |

## G. Cell zone conditions

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Cell Zone Conditions | Fluid zone | **Single shared fluid zone** | Cell Zone Conditions | VOF resolves interface inside one zone |
| Cell Zone Conditions | Separate phase bodies | **No** | Geometry concept | Not required for VOF |

## H. Boundary conditions

### H1. Inlet boundaries

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Boundary Conditions | Inlet type | **Mass-Flow Inlet** (both zones) | Boundary Conditions | Confirmed |
| Inlet water side | Zone | **inlet_water** (name may differ) | Boundary Conditions | Water-side half of split face |
| Inlet water side | Water volume fraction | **1.0** | inlet_water | Pure water inlet |
| Inlet water side | Flow direction | **Normal to boundary** | inlet_water | Prevent accidental tangential injection |
| Inlet steam side | Zone | **inlet_steam** (name may differ) | Boundary Conditions | Steam-side half of split face |
| Inlet steam side | Water volume fraction | **0.0** | inlet_steam | Pure steam inlet |
| Inlet steam side | Flow direction | **Normal to boundary** | inlet_steam | Prevent accidental tangential injection |

### H2. Outlet boundary

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Boundary Conditions | Outlet type | **Pressure Outlet** | Boundary Conditions | Kept from baseline |
| Outlet | Gauge pressure | **Baseline outlet pressure** | outlet | Keep same value used in your baseline case |
| Outlet | Backflow phase fractions | **Set explicitly** | outlet | Avoid inconsistent default backflow behavior |

### H3. Walls

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Boundary Conditions | All physical walls | **Wall** | Boundary Conditions | Same as baseline |
| Walls | Roughness | **0** | wall | Smooth-wall baseline assumption |

## I. Numerical methods

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Solution Methods | Pressure-velocity coupling | **PISO** | Solution Methods | Recommended for transient VOF |
| Solution Methods | Pressure discretization | **PRESTO!** | Solution Methods | Recommended for swirl/curvature |
| Solution Methods | Volume fraction discretization | **Second Order Upwind** | Solution Methods | Your current choice (Geo-Reconstruct/Compressive unavailable) |
| Solution Methods | Momentum discretization | **Second Order Upwind** | Solution Methods | Use first-order temporarily only if unstable |
| Solution Methods | Turbulence discretization | **Second Order Upwind** | Solution Methods | Keep consistent with your current run strategy |

## J. Initialization and run controls

| Section | Item | Set this to | Where | Status / notes |
|---|---|---:|---|---|
| Initialization | Method | **Hybrid Initialization** | Solution Initialization | Confirmed |
| Initialization | Patch step | **Skipped intentionally** | Patch panel | Current decision: run without selective patch |
| Run Calculation | Time stepping | **Transient with conservative timestep** | Run Calculation | Keep interface Courant low at startup |
| Run Calculation | Iterations per timestep | **20-50 (starting range)** | Run Calculation | Increase only if needed for convergence each step |

## K. Current assumptions and known gaps

| Item | Status |
|---|---|
| Selective inlet-near patching | **Not applied** (intentional for this run) |
| Geo-Reconstruct/Compressive scheme | **Unavailable in this UI path/version combination** |
| Exact reason scheme unavailable | **Unconfirmed** (likely formulation-dependent) |
| Outlet backflow phase-fraction values | **Must be checked manually** |
| Timestep value and Courant target used in this exact run | **Not yet documented here** |

## L. Super short tracker table

| Done | Setting | Value |
|---|---|---|
| ☑ | Solver | Pressure-Based |
| ☑ | Time | Transient |
| ☑ | Multiphase | VOF |
| ☑ | Primary phase | Steam |
| ☑ | Secondary phase | Water |
| ☑ | Inlet layout | Split into two zones |
| ☑ | Inlet type | Mass-Flow Inlet (both) |
| ☑ | Water-side VOF | 1.0 |
| ☑ | Steam-side VOF | 0.0 |
| ☑ | Pressure-velocity coupling | PISO |
| ☑ | Pressure scheme | PRESTO! |
| ☑ | Volume fraction scheme | Second Order Upwind |
| ☑ | Initialization | Hybrid |
| ☑ | Patch | Skipped for this run |

## M. Immediate next checks after this run

1. Plot water volume fraction on inlet plane and 1-3 inlet diameters downstream.
2. Check vectors near inlet for artificial lateral scatter.
3. Check outlet backflow warnings and phase composition.
4. If interface smears too fast, test:
   - smaller timestep first,
   - then (if needed) Explicit VOF formulation to see whether additional interface schemes appear.

## N. Run outcome and decision (2026-05-05)

- Outcome: this VOF run produced a **very weird / non-physical result** and is considered invalid for current use.
- Interpretation: observed behavior is not acceptable for expected separator physics.
- Decision: stop this VOF branch for now and return to the **Mixture** setup as the next run path.
- Action for next report revision: document the Mixture retry settings and compare directly against this failed VOF attempt.
