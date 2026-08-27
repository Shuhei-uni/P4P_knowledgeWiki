> **Retired source:** Setups/reports/purnanto-reference/00/technical-extraction.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Technical Setup Report: Baseline Purnanto 1680J Live Extract

## 1. Purpose

This companion report records the actual Fluent export for the baseline Purnanto 1680J case:

- archive: PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1680-live-extract/live/settings_root_tree.json (historical machine artifact path: `../../../PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1680-live-extract/live/settings_root_tree.json`; not migrated)
- narrative companion: [00-baseline-spiral-boc-reference.md](setup.md)

Use this file when you need the machine-extracted replay state, not the paper-style narrative reconstruction.

Rule for this branch:

- if this report and the narrative report disagree, treat the extracted Fluent state as the replay authority and record the narrative value as the intended interpretation.

## 2. Setup Identity

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Bundle label | `purnanto-enthalpy1680-live-extract` | baseline spiral BOC reference | `match in role` | This is the exact live extract for the 1680J case |
| Fluent version | `Ansys Fluent 2024 R2` | not stated in the narrative report | `additional detail` | From the archive manifest |
| Solver family | pressure-based, steady | pressure-based, steady | `match` |  |
| Multiphase model | `mixture`, 2 phases | `Mixture` | `match` |  |
| Geometry role | spiral-inlet BOC separator setup | spiral-inlet BOC reference | `match in role` | Physical CAD dimensions are not serialized in this settings tree |
| Boundary topology | `mass_flow_inlet.inlet`, `pressure_outlet.outlet`, `wall.bottom`, `wall.wall-fluid` | generic inlet / outlet / walls | `match in role` | The archive stores the actual zone names |
| DPM state | discrete-phase tree present, no active injections | not discussed in the narrative report | `additional detail` | Important for replay completeness |

## 3. Geometry And Mesh

The settings tree does not serialize the full CAD geometry dimensions or the actual mesh cell count. It does, however, expose the mesh-control state and the topology needed for replay.

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Geometry dimensions | not serialized here | paper-style baseline dimensions are described in the narrative report | `not-serialized` | Keep the design geometry in the narrative report; do not infer it from the settings tree |
| Mesh adaptation method | `puma` | not discussed in the narrative report | `additional detail` | `maximum_refinement_level = 2` |
| Mesh quality guard | `minimum_cell_quality = 0.01` | not discussed | `additional detail` |  |
| Minimum edge length | `0` | not discussed | `additional detail` |  |
| Wall distance method | `geometric` | not discussed | `additional detail` |  |
| Polyhedra options | preserve boundary layer `decide-at-runtime` | not discussed | `additional detail` |  |
| Periodic shadow zones | shown | not discussed | `additional detail` |  |

Reference values carried by the archive:

| Field | Extracted value |
|---|---:|
| Area | `1` |
| Density | `0.5541999936103821` |
| Enthalpy | `1600000` |
| Length | `1` |
| Pressure | `1080000` |
| Temperature | `500` |
| Y+ | `300` |
| Velocity | `32.13999938964844` |
| Viscosity | `1.789400084817316e-05` |
| Reference zone | `fluid` |

## 4. Fluent Setup

### 4.1 General

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Gravity | on, `0, -9.81, 0` | on, `0, -9.81, 0` | `match` |  |
| Operating pressure | `0 Pa` | `0 Pa` | `match` |  |
| Operating density method | `mixture-averaged` | not emphasized in the narrative report | `additional detail` |  |
| Operating temperature | `298.15 K` | not emphasized in the narrative report | `additional detail` |  |

### 4.2 Models

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Energy | off | off | `match` |  |
| Viscous model | RNG `k-epsilon` | RNG `k-epsilon` | `match` |  |
| Near-wall treatment | standard wall function | standard wall function | `match` |  |
| Differential viscosity | on | not emphasized | `additional detail` |  |
| Swirl-dominated flow | on | not emphasized | `additional detail` |  |
| Species model | off | off | `match` |  |
| Species mapping | `water-vapor-at-psep`, `water-liquid-at-psep` | same physical intent, rounded values in the narrative report | `rounded` | The archive stores the exact material names used in Fluent |

### 4.3 Materials

| Material | Extracted value | Narrative report value | Status | Notes |
|---|---|---|---|---|
| Water liquid density | `881.2108764648438 kg/m3` | `881.77 kg/m3` | `rounded` | Slight numerical mismatch, likely source or rounding drift |
| Water vapour density | `5.797433853149414 kg/m3` | `5.73 kg/m3` | `rounded` |  |
| Water liquid viscosity | `0.0001455440069548786 kg/m·s` | `145.96 × 10^-6 kg/m·s` | `rounded` |  |
| Water vapour viscosity | `0.00001520620025985409 kg/m·s` | `15.188 × 10^-6 kg/m·s` | `rounded` |  |

## 5. Boundary Conditions

### 5.1 Inlet

The archive stores a single mass-flow inlet named `inlet`.

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Boundary type | `mass_flow_inlet` | `Mass-Flow Inlet` | `match` |  |
| Mixture pressure reference | `supersonic_gauge_pressure = 1140000 Pa` | `11.4 bar` | `match` |  |
| Mixture turbulence | intensity/hydraulic diameter | mass-flow inlet description | `match in role` | `turbulent_intensity = 0.02109999952837825`, `hydraulic_diameter = 0.724` |
| Phase-1 mass flow | `88.61 kg/s` | `80.69 kg/s` in the narrative baseline summary | `human-error-candidate` | Phase-1 is `water-vapor-at-psep` in the archive |
| Phase-2 mass flow | `109 kg/s` | `116.92 kg/s` in the narrative baseline summary | `human-error-candidate` | Phase-2 is `water-liquid-at-psep` in the archive |
| Total mass flow | `197.61 kg/s` | `197.61 kg/s` | `match` |  |

### 5.2 Outlet

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Boundary type | `pressure_outlet.outlet` | pressure outlet | `match` |  |
| Gauge pressure | `1120000 Pa` | `11.2 bar` | `match` |  |
| Backflow pressure spec | `Total Pressure` | described as mostly gas in the narrative report | `different wording` | The archive stores the actual Fluent choice |
| Backflow phase-2 volume fraction | `0` | not emphasized in the narrative report | `additional detail` |  |

### 5.3 Walls

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Wall type | `wall.bottom`, `wall.wall-fluid` | walls | `match in role` |  |
| Wall motion | stationary wall | stationary wall | `match` |  |
| Shear condition | no slip | no slip | `match` |  |
| Roughness height | `0` | smooth wall assumption | `match` |  |
| Roughness constant | `0.5` | not emphasized | `additional detail` |  |

### 5.4 Other Boundary Infrastructure

| Field | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Non-reflecting BC | present, inactive | not discussed | `additional detail` |  |
| Perforated wall setup method | `None` | not discussed | `additional detail` |  |

## 6. Solution, Initialization, And Run Control

### 6.1 Numerics

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Pressure-velocity coupling | `SIMPLE` | `SIMPLE` | `match` |  |
| Gradient scheme | `green-gauss-node-based` | `Green-Gauss Node Based` | `match` |  |
| Pressure discretization | `presto!` | `PRESTO!` | `match` |  |
| Momentum discretization | `second-order-upwind` | `Second Order Upwind` | `match` |  |
| `k` discretization | `second-order-upwind` | `Second Order Upwind` | `match` |  |
| `epsilon` discretization | `second-order-upwind` | `Second Order Upwind` | `match` |  |
| Multiphase discretization | `quick` | `QUICK` | `match` |  |

### 6.2 Controls

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Under-relaxation, pressure | `0.3` | not highlighted | `additional detail` |  |
| Under-relaxation, momentum | `0.7` | not highlighted | `additional detail` |  |
| Under-relaxation, multiphase | `0.4` | not highlighted | `additional detail` |  |
| Under-relaxation, `k` / `epsilon` | `0.8` / `0.8` | not highlighted | `additional detail` |  |
| Residual continuity criterion | `1e-4` | not highlighted | `additional detail` |  |
| Residual `k`, `epsilon`, phase-fraction, velocity criteria | `1e-3` | not highlighted | `additional detail` |  |

### 6.3 Initialization And Run

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| Initialization | hybrid | hybrid initialization | `match` |  |
| Hybrid init iteration count | `10` | not highlighted | `additional detail` |  |
| Patch reconstructed interface | `false` | not highlighted | `additional detail` |  |
| Run calculation iterations | `3003` | not specified in the narrative report | `additional detail` |  |

## 7. DPM State

The archive includes a discrete-phase model branch even though the narrative report does not treat DPM as part of the baseline setup.

| Topic | Extracted Fluent state | Narrative report | Status | Notes |
|---|---|---|---|---|
| DPM interaction | off | not discussed | `additional detail` |  |
| Pressure force | on | not discussed | `additional detail` |  |
| Virtual mass force | on, factor `0.5` | not discussed | `additional detail` |  |
| Tracking | `max_num_steps = 10000`, `step_length_factor = 5` | not discussed | `additional detail` |  |
| Injections | none active | not discussed | `additional detail` | The archive serializes the DPM tree but no active injections |

## 8. Drift Log

| Topic | Reported | Extracted | Drift type | Action |
|---|---|---|---|---|
| Baseline inlet phase split | `116.92 kg/s liquid` / `80.69 kg/s gas` | `109 kg/s liquid` / `88.61 kg/s vapor` | `human-error-candidate` | Keep the extracted split for replay and call out the mismatch explicitly |
| Material constants | rounded values in the narrative report | exact Fluent-exported values shown above | `rounded` | Use the archive values for replay, but keep the narrative values for context |
| DPM content | not discussed | DPM tree present, no injections active | `not-serialized in narrative` | Mention this in any rebuild plan |
| Geometry dimensions | paper-style design context in the narrative report | not serialized in the settings tree | `not-serialized` | Keep geometry in the narrative report and use the archive for replay state |

## 9. Working Conclusion

- The live 1680J archive matches the main solver, model, and numerics stack from the narrative baseline report.
- The most important mismatch is the inlet phase split.
- The archive also preserves exact material constants, reference values, and a dormant DPM branch that the narrative report does not spell out.
- For future replay work, trust this technical companion for actual Fluent settings and use the narrative report for the wider project story.
