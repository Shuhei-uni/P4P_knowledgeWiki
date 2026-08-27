> **Retired source:** Setups/reports/purnanto-reference/07/technical-extraction.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Technical Setup Report: Setup 07 Live Export

## 1. Purpose

This companion report records the actual Fluent export for setup 07.

- archive: [PyAnsys/cases/actual_setup_archives/07-pure-phase-split-actual-area-live-fff-1-2/settings_snapshot.json](../../../PyAnsys/cases/actual_setup_archives/07-pure-phase-split-actual-area-live-fff-1-2/settings_snapshot.json)
- narrative companion: [07-pure-phase-split-actual-area.md](setup.md)
- drift note: [PyAnsys intended-vs-actual.md](../../../PyAnsys/cases/actual_setup_archives/07-pure-phase-split-actual-area-live-fff-1-2/intended-vs-actual.md)

Use this file when you need the machine-extracted setup state, not just the intended branch definition.

Rule for this branch:

- if the live export and the narrative report disagree, treat the live export as the replay authority and record the narrative value as the intended branch description.

## 2. Setup Identity

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Bundle label | `07-pure-phase-split-actual-area-live-fff-1-2` | setup 07 | `match in role` | Live export from the loaded Setup07extractor case/data |
| Fluent version | `Ansys Fluent 2024 R2` | not always stated explicitly | `additional detail` | From archive metadata |
| Solver family | pressure-based, steady | pressure-based, steady | `match` |  |
| Multiphase model | `mixture`, 2 phases | `Mixture` | `match` |  |
| Geometry role | split inlet on the purnanto geometry line | `purnanto` geometry | `match in role` | The snapshot does not serialize CAD dimensions |
| Boundary topology | `liquidinlet`, `steaminlet`, `steamoutlet`, `wall-fluid`, `bottom` | same roles | `match` |  |
| DPM state | active, 9 injections | treated as later evaluation logic in the narrative report | `important drift` | The live export already contains DPM content |

## 3. Geometry And Mesh

The settings snapshot does not serialize geometry or mesh cell counts, but the setup report defines the actual split geometry used for the inlet branch.

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| CAD / mesh dimensions | not serialized here | `0.724 m x 0.724 m` inlet face, split into liquid and steam zones | `not-serialized` | Keep the split geometry in the narrative report |
| Full inlet area | not serialized here | `0.524176 m2` | `narrative geometry context` |  |
| Liquid-side area | not serialized here | `0.0048896 m2` | `narrative geometry context` |  |
| Steam-side area | not serialized here | `0.5192864 m2` | `narrative geometry context` |  |
| Liquid-side width | not serialized here | `0.006754 m` | `narrative geometry context` |  |
| Steam-side width | not serialized here | `0.717246 m` | `narrative geometry context` |  |

The archive confirms the boundary names and roles, but not the CAD split dimensions themselves.

## 4. Fluent Setup

### 4.1 General

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Gravity | on, `0, -9.81, 0` | same | `match` |  |
| Operating pressure | `0 Pa` | same | `match` |  |
| Operating density method | `mixture-averaged` | not emphasized | `additional detail` |  |
| Operating temperature | `288.16 K` | not emphasized | `additional detail` |  |

### 4.2 Models

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Energy | off | off | `match` |  |
| Viscous model | RNG `k-epsilon` | RNG `k-epsilon` | `match` |  |
| Near-wall treatment | standard wall function | implied by the report chain | `match` |  |
| Differential viscosity | on | not emphasized | `additional detail` |  |
| Swirl-dominated flow | on | not emphasized | `additional detail` |  |
| Species model | off | off | `match` |  |
| Species mapping | `water-liquid`, `water-vapor` | pure liquid / pure steam setup intent | `match in role` | Fluent stores the exact phase-material map differently from the narrative wording |

### 4.3 Materials

| Material | Extracted value | Narrative report value | Status | Notes |
|---|---|---|---|---|
| Liquid density | `881.77 kg/m3` | `881.77 kg/m3` | `match` |  |
| Vapor density | `5.73 kg/m3` | `5.73 kg/m3` | `match` |  |
| Liquid viscosity | `145.96 × 10^-6 kg/m·s` | `145.96 × 10^-6 kg/m·s` | `match` |  |
| Vapor viscosity | `15.188 × 10^-6 kg/m·s` | `15.188 × 10^-6 kg/m·s` | `match` |  |

## 5. Boundary Conditions

### 5.1 Inlets

Both inlet zones use the same normal-velocity magnitude, but the turbulence field differs between the two zones in the live export.

| Boundary | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| `liquidinlet` type | `velocity_inlet` | `Velocity Inlet` | `match` |  |
| `liquidinlet` velocity | `27.118 m/s`, normal to boundary | `27.118 m/s` | `match` |  |
| `liquidinlet` volume fraction | liquid `1`, vapor `0` | same | `match` |  |
| `liquidinlet` turbulence | intensity + hydraulic diameter, `0.01338 m` | same | `match` |  |
| `steaminlet` type | `velocity_inlet` | `Velocity Inlet` | `match` |  |
| `steaminlet` velocity | `27.118 m/s`, normal to boundary | `27.118 m/s` | `match` |  |
| `steaminlet` volume fraction | liquid `0`, vapor `1` | same | `match` |  |
| `steaminlet` turbulence | intensity + viscosity ratio, `0.7206100000000001` | report text expects hydraulic diameter-like handling | `human-error-candidate` | The live export does not use the same turbulence field as the narrative description |
| Mixture pressure reference on both inlets | `1140000 Pa` | same | `match` |  |

### 5.2 Outlet

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Boundary type | `pressure_outlet.steamoutlet` | `Pressure Outlet` | `match` |  |
| Gauge pressure | `1120000 Pa` | same | `match` |  |
| Backflow spec | `Total Pressure` | not emphasized | `additional detail` |  |
| Backflow turbulence | intensity + hydraulic diameter, `0.724` | not emphasized | `additional detail` |  |
| Backflow phase-2 VF | `0` | not emphasized | `additional detail` |  |

### 5.3 Walls

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| `bottom` | stationary wall, no slip, roughness height `0` | wall | `match` |  |
| `wall-fluid` | stationary wall, no slip, roughness height `0` | wall | `match` |  |
| Roughness constant | `0.5` | not emphasized | `additional detail` |  |

## 6. Solution, Initialization, And Run Control

### 6.1 Numerics

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Pressure-velocity coupling | `Coupled` | `SIMPLE` | `human-error-candidate` | This is the biggest solver-control drift in the archive |
| Pressure discretization | `presto!` | `PRESTO!` | `match` |  |
| Momentum discretization | `first-order-upwind` | `Second Order Upwind` | `human-error-candidate` |  |
| `k` discretization | `first-order-upwind` | `Second Order Upwind` | `human-error-candidate` |  |
| `epsilon` discretization | `first-order-upwind` | `Second Order Upwind` | `human-error-candidate` |  |
| Multiphase discretization | `first-order-upwind` | `QUICK` | `human-error-candidate` |  |
| Gradient scheme | `least-square-cell-based` | `Green-Gauss Node Based` | `human-error-candidate` |  |
| Unstructured VOF PRESTO variant | on | not emphasized | `additional detail` |  |

### 6.2 Controls

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Flow Courant number | `200` | not emphasized | `additional detail` |  |
| Explicit pressure URF | `0.5` | not emphasized | `additional detail` |  |
| Explicit momentum URF | `0.5` | not emphasized | `additional detail` |  |
| Under-relaxation, multiphase | `0.5` | not emphasized | `additional detail` |  |
| Under-relaxation, momentum | `0.7` | not emphasized | `additional detail` |  |
| Under-relaxation, density | `1` | not emphasized | `additional detail` |  |
| Residual continuity criterion | `1e-3` | not emphasized | `additional detail` |  |
| Residual phase-fraction criterion | `1e-3` | not emphasized | `additional detail` |  |

### 6.3 Initialization And Run

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Initialization | hybrid | hybrid initialization | `match` |  |
| Hybrid init iteration count | `10` | not highlighted | `additional detail` |  |
| Patch reconstructed interface | `true` | not highlighted in the narrative report | `important detail` |  |
| Run calculation iterations | `2000` | not highlighted | `additional detail` |  |

## 7. DPM State

The live export already contains an active discrete-phase branch.

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Injection count | `9` | treated as later evaluation logic | `important drift` |  |
| Injection materials | `anthracite` x2, `water-droplet` x7 | not detailed in the narrative report | `important drift` |  |
| Injection surface | `steaminlet` | steam-side inlet only | `match in role` |  |
| Particle drag | spherical | not emphasized | `additional detail` |  |
| Turbulent dispersion | mixed per injection | not emphasized | `additional detail` |  |
| Particle rotation | mixed per injection | not emphasized | `additional detail` |  |
| DPM report definitions | injection report definition exists | not discussed | `additional detail` |  |

## 8. Drift Log

| Topic | Reported | Extracted | Drift type | Action |
|---|---|---|---|---|
| Pressure-velocity coupling | `SIMPLE` | `Coupled` | `human-error-candidate` | Record as a solver drift in future rebuilds |
| Spatial discretization | second-order family / `QUICK` | first-order upwind family | `human-error-candidate` | Keep the live export as the replay authority |
| Gradient scheme | Green-Gauss Node Based | least-square-cell-based | `human-error-candidate` |  |
| Steam inlet turbulence field | hydraulic-diameter style | intensity + viscosity ratio | `human-error-candidate` | This is already called out in the archive comparison note |
| DPM presence | framed as later-stage logic | active with 9 injections | `human-error-candidate` / `context drift` | The live case had already grown into a richer setup |
| Patch reconstructed interface | not highlighted | `true` | `important detail` | This affects reproducibility |

## 9. Working Conclusion

- The live setup 07 archive matches the intended branch role for geometry, phase split, and boundary topology.
- The most important differences are solver coupling, discretization order, and the turbulence field on the steam inlet.
- The archive also contains an active DPM layer, so this is not a pure continuous-field-only snapshot.
- For future replay work, use this technical companion as the machine authority and keep the narrative report as the intended branch description.
