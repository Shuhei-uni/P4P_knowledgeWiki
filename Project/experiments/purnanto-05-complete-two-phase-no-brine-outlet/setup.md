> **Legacy source:** Setups/past/archived/05-complete-two-phase-actual-area-no-brine-outlet.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Complete Two-Phase Actual-Area No-Brine-Outlet Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `05` |
| Lifecycle | `archived` |
| Role | planned full-inlet diagnostic branch |
| Parent setup | [04](../purnanto-04-mixed-wet-half-actual-area/setup.md) |
| Evidence-use label | planned setup definition only |
| Outcome | parked |
| Linked report | none |

## 1. Purpose

Define the next spiral-inlet simulation branch:

- complete two-phase inlet over the full inlet face
- one mixed steam-water `Velocity Inlet`
- no active brine outlet
- planned steady run budget: `5000` iterations

This report starts from the actual-area calculation in:

- [04-mixed-wet-half-actual-area.md](../purnanto-04-mixed-wet-half-actual-area/setup.md)

Geometry naming note:

- this no-brine-outlet branch still uses the `purnanto` geometry label;
- the geometry label is separate from the inlet boundary-condition style, so a uniform two-phase inlet does not make the geometry `purnantov2`.

## 2. Setup Identity

| Item | Value |
|---|---:|
| Geometry | `purnanto` spiral-inlet BOC separator |
| Inlet representation | complete mixed two-phase inlet |
| Boundary type | single full-area `Velocity Inlet` |
| Brine outlet | not active / no brine outlet |
| Planned iteration budget | `5000` steady iterations |
| Multiphase model | `Mixture` |
| Turbulence model | `RNG k-epsilon` |
| Energy | `Off` |
| Liquid density | `881.77 kg/m3` |
| Steam density | `5.73 kg/m3` |
| Actual inlet-half area from parent report | `0.26209 m2` |
| Actual full inlet area used here | `0.52418 m2` |
| Purnanto `1600 kJ/kg` target total flow | `197.61 kg/s` |
| Corrected velocity for actual full inlet area | `27.12 m/s` |

Evidence labels:

- `Reported`: baseline Purnanto operating values reused through the parent setup report.
- `User-reported`: actual inlet-half area measured from the current geometry.
- `Calculated`: velocity-inlet phase fractions and mass-flow checks derived from reported/user-reported values.
- `Assumed`: this report assumes the new case uses one full inlet boundary carrying both phases uniformly, not two split inlet zones.

## 3. Routing and Evidence Note

The CFD lookup layer was checked before creating this report.

Relevant lookup evidence:

- `CFD_wiki/paper_lookup/geothermal/separator-design-sizing-and-mrs.md` points to Zarrouk and Purnanto 2014, Section 6, as the main CFD separator modelling overview and to Section 5.4 for inlet nozzle effects.
- Existing project reports already use the Purnanto 2013 spiral-inlet baseline values: `1600 kJ/kg`, total mass flow `197.61 kg/s`, liquid mass flow `116.92 kg/s`, steam mass flow `80.69 kg/s`, velocity `26.81 m/s`, liquid density `881.77 kg/m3`, and steam density `5.73 kg/m3`.

Uncertainty:

- The exact active Fluent boundary-zone name is not known from the report file alone. Replace `inlet_complete_two_phase` below with the actual boundary name in Fluent.
- Because the brine outlet is not active, this run should not be used to claim final separator liquid-removal efficiency. It is mainly an inlet/mixing and steam-outlet carryover diagnostic.

## 4. Velocity-Inlet Conditions to Enter

Recommended first-run setting: preserve the Purnanto `1600 kJ/kg` target mass flow and use the bulk full-inlet phase volume fractions.

| Fluent field | Value |
|---|---:|
| Boundary name | `inlet_complete_two_phase` or actual full inlet name |
| Boundary type | `Velocity Inlet` |
| Velocity specification | `Normal to Boundary` |
| Velocity magnitude | `27.12 m/s` |
| Liquid water volume fraction | `0.009328` |
| Steam/vapor volume fraction | `0.990672` |
| Turbulence specification | keep same style as parent setup |
| Temperature / energy inputs | not used if Energy remains `Off` |

If Fluent asks only for the secondary-phase volume fraction and liquid water is the secondary phase:

```text
secondary phase volume fraction = 0.009328
```

If Fluent asks for primary phase fraction separately:

```text
steam/vapor phase fraction = 0.990672
```

Important:

- `liquid volume fraction = 1.0` and `steam volume fraction = 0.0` would define a pure-liquid inlet, not a complete steam-water two-phase inlet.
- For a complete mixed two-phase inlet that carries both Purnanto phases, the phase volume fractions must come from the liquid and steam volumetric flow rates.

## 5. Calculation Basis

Baseline phase mass-flow targets from the parent setup:

```text
m_dot_liquid = 116.92 kg/s
m_dot_steam  = 80.69 kg/s
rho_liquid   = 881.77 kg/m3
rho_steam    = 5.73 kg/m3
```

Convert mass flow to volumetric flow:

```text
Q_liquid = 116.92 / 881.77 = 0.13260 m3/s
Q_steam  = 80.69 / 5.73    = 14.08202 m3/s
Q_total  = 14.21462 m3/s
```

Bulk phase volume fractions for one complete two-phase inlet:

```text
alpha_liquid = Q_liquid / Q_total
alpha_liquid = 0.13260 / 14.21462
alpha_liquid = 0.009328

alpha_steam = 1 - alpha_liquid
alpha_steam = 0.990672
```

Actual full inlet area:

```text
A_half = 0.26209 m2
A_full = 2 * A_half
A_full = 0.52418 m2
```

Using the actual full inlet area, calculate the velocity required to preserve Purnanto's total volumetric flow:

```text
V_exact = Q_total / A_full
V_exact = 14.21462 / 0.52418
V_exact = 27.12 m/s
```

Using `V = 27.12 m/s` over the actual full inlet area:

```text
m_dot_liquid = alpha_liquid * rho_liquid * V * A_full = 116.92 kg/s
m_dot_steam  = alpha_steam * rho_steam * V * A_full  = 80.69 kg/s
m_dot_total  = 197.61 kg/s
```

This matches the Purnanto `1600 kJ/kg` mass-flow target while using the measured actual full inlet area.

## 6. Velocity-Preserving Alternative

If the priority is to keep the source-reported velocity `26.81 m/s` exactly, use the same volume fractions but accept a slightly lower mass flow because the measured actual inlet area is smaller than the area implied by the paper:

```text
V_reported = 26.81 m/s
```

Velocity-preserving inlet option:

| Fluent field | Value |
|---|---:|
| Velocity magnitude | `26.81 m/s` |
| Liquid water volume fraction | `0.009328` |
| Steam/vapor volume fraction | `0.990672` |
| Resulting liquid mass flow | `115.59 kg/s` |
| Resulting steam mass flow | `79.77 kg/s` |
| Resulting total mass flow | `195.37 kg/s` |

Recommendation for the first run:

- use `27.12 m/s` for the Purnanto `1600 kJ/kg` mass-flow setup;
- use `26.81 m/s` only if exact reported velocity matching matters more than exact mass-flow matching.

## 7. Boundary Conditions

### Complete Two-Phase Inlet

Use one full inlet boundary:

```text
type = Velocity Inlet
velocity magnitude = 27.12 m/s
direction = normal to boundary
liquid water volume fraction = 0.009328
steam/vapor volume fraction = 0.990672
```

### Steam Outlet

Keep the existing steam outlet as a pressure outlet unless the active case requires otherwise:

```text
type = Pressure Outlet
gauge pressure = same convention as parent case
backflow liquid volume fraction = 0.0
backflow steam/vapor volume fraction = 1.0
```

### Brine Outlet

For this branch:

```text
brine outlet = not active
```

Practical Fluent interpretation depends on the geometry:

- if the mesh has no brine outlet face, no action is needed;
- if the face exists but should be closed, set it to `Wall`;
- do not leave it as an unintended `Pressure Outlet`.

## 8. Solver and Numerics to Keep

Keep the parent stack unless the case fails immediately:

| Panel | Setting | Value |
|---|---|---:|
| General | Solver | `Pressure-Based` |
| General | Time | `Steady` |
| Models > Multiphase | Model | `Mixture` |
| Models > Energy | Energy | `Off` |
| Models > Viscous | Turbulence | `RNG k-epsilon` |
| Operating Conditions | Gravity | `On` |
| Solution Methods | Pressure-velocity coupling | `SIMPLE` |
| Solution Methods | Pressure | `PRESTO!` |
| Solution Methods | Momentum | `Second Order Upwind` |
| Solution Methods | Turbulence equations | `Second Order Upwind` |
| Solution Methods | Volume fraction | `QUICK` if available |
| Initialization | Method | `Hybrid Initialization` |
| Run Calculation | Iterations | `5000` |

## 9. Monitors and What to Save

Track these during the `5000`-iteration run:

1. scaled residuals for continuity, momentum, turbulence, and volume fraction;
2. total mass imbalance;
3. steam outlet steam mass flow;
4. steam outlet liquid mass flow;
5. inlet phase mass-flow reports;
6. liquid volume fraction near the spiral inlet and steam outlet intake;
7. velocity vectors around the inlet and central vortex region.

Save at minimum:

```text
case file before run
case/data at 1000 iterations
case/data at 3000 iterations
case/data at 5000 iterations
residual plot
flux report at 5000 iterations
liquid-volume-fraction contour
velocity-vector plot
```

## 10. Interpretation Rules

Use this run for:

- checking whether a uniform complete two-phase inlet is more stable than the mixed wet-half split;
- comparing inlet swirl development against the split-inlet cases;
- estimating steam-outlet carryover risk when no brine outlet drains liquid.

Do not use this run for:

- final liquid separation efficiency;
- final brine removal performance;
- direct comparison against full-geometry cases with an active brine outlet.

Evidence-use label at setup stage:

```text
Setup calculation only
```

Upgrade the evidence-use label only after residuals, mass balance, and outlet phase fluxes are checked at `5000` iterations.

## 11. Execution Checklist

| Done | Item | Target |
|---|---|---|
| [ ] | Confirm one full inlet boundary | not split into dry/wet halves |
| [ ] | Set inlet type | `Velocity Inlet` |
| [ ] | Set inlet velocity | `27.12 m/s` first-run recommendation |
| [ ] | Set liquid water volume fraction | `0.009328` |
| [ ] | Set steam/vapor volume fraction | `0.990672` |
| [ ] | Confirm brine outlet is inactive | absent or set to `Wall` |
| [ ] | Confirm steam outlet backflow fractions | liquid `0.0`, steam `1.0` |
| [ ] | Hybrid initialize | complete |
| [ ] | Set iteration budget | `5000` |
| [ ] | Save case/data checkpoints | `1000`, `3000`, `5000` iterations |
