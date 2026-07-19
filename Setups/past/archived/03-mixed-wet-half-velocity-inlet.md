# Mixed Wet-Half Velocity-Inlet Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `03` |
| Lifecycle | `archived` |
| Role | mixed wet-half diagnostic parent |
| Parent setup | [02](02-split-two-zone-velocity-inlet-brine-outlet.md) |
| Evidence-use label | non-converged flux diagnostic; no efficiency/DPM report |
| Outcome | superseded |
| Linked report | none |

## 1. Objective

Create a split-inlet `Mixture`, `Steady` setup where both inlet halves use the same velocity, but only the wall-side half carries liquid.

Target inlet concept:

- inner/core half: steam only
- outer/wall-side half: steam + water mixture

This avoids the unrealistic pure-water / pure-steam velocity mismatch from the earlier split-inlet setup.

## 2. Source case being matched

This setup targets the Purnanto 2013 spiral-inlet baseline at:

| Item | Value |
|---|---:|
| Two-phase enthalpy | `1600 kJ/kg` |
| Total mass flow | `197.61 kg/s` |
| Liquid mass flow | `116.92 kg/s` |
| Steam mass flow | `80.69 kg/s` |
| Reported spiral-inlet velocity | `26.81 m/s` |
| Separation pressure | `11.2 bara` |
| Liquid density | `881.77 kg/m3` |
| Steam density | `5.73 kg/m3` |

Source file:

- `CFD_wiki/raw/informit.366967552564856.pdf`

## 3. Volume-fraction calculation

Fluent volume fraction is not mass fraction.

```text
Q_l = m_l / rho_l = 116.92 / 881.77 = 0.13260 m3/s
Q_g = m_g / rho_g = 80.69 / 5.73 = 14.08202 m3/s
Q_total = 14.21462 m3/s
```

Bulk liquid volume fraction:

```text
alpha_l_bulk = Q_l / Q_total
alpha_l_bulk = 0.13260 / 14.21462
alpha_l_bulk = 0.009328
```

For an equal two-half inlet where the steam-only half has no liquid:

```text
alpha_l_wet_half = 2 * alpha_l_bulk
alpha_l_wet_half = 0.018656
alpha_g_wet_half = 0.981344
```

Recommended inlet values:

| Boundary | Velocity | Liquid volume fraction | Steam volume fraction |
|---|---:|---:|---:|
| `inlet_steam_inner` | `26.81 m/s` | `0.0` | `1.0` |
| `inlet_wet_outer` | `26.81 m/s` | `0.018656` | `0.981344` |

## 4. Inferred area and mass-flow check

The paper velocity and phase volumetric flow imply:

```text
A_total = Q_total / V = 14.21462 / 26.81 = 0.53020 m2
A_half = 0.26510 m2
```

Using `V = 26.81 m/s` and `A_half = 0.26510 m2`:

```text
m_l_wet = 0.018656 * 881.77 * 26.81 * 0.26510 = 116.92 kg/s
m_g_wet = 0.981344 * 5.73 * 26.81 * 0.26510 = 39.97 kg/s
m_g_dry = 1.0 * 5.73 * 26.81 * 0.26510 = 40.72 kg/s
m_g_total = 80.69 kg/s
m_total = 197.61 kg/s
```

This only preserves the paper mass flow if:

- total inlet area is close to `0.53020 m2`
- the two inlet halves are equal area
- both velocity inlets use `26.81 m/s`
- the wet half uses liquid volume fraction `0.018656`

If actual wet-half area differs:

```text
alpha_l_wet = 0.13260 / (26.81 * A_wet)
```

## 5. Fluent settings

| Panel | Setting | Value |
|---|---|---:|
| General | Solver | `Pressure-Based` |
| General | Time | `Steady` |
| Models > Multiphase | Model | `Mixture` |
| Models > Multiphase | Primary phase | `steam` / `gas` / `vapor` |
| Models > Multiphase | Secondary phase | `liquid water` |
| Models > Energy | Energy | `Off` |
| Models > Viscous | Turbulence | `RNG k-epsilon` |
| Operating Conditions | Gravity | `On` |
| Operating Conditions | Operating pressure | baseline convention, usually `0 Pa` |

Material properties:

| Material | Property | Value |
|---|---|---:|
| Liquid water | Density | `881.77 kg/m3` |
| Liquid water | Viscosity | `145.96e-6 kg/m-s` |
| Steam/vapor | Density | `5.73 kg/m3` |
| Steam/vapor | Viscosity | `15.188e-6 kg/m-s` |
| Phase interaction | Surface tension | `0.0411 N/m` |

Boundary conditions:

| Boundary | Type | Main inputs |
|---|---|---|
| `inlet_steam_inner` | `Velocity Inlet` | `26.81 m/s`, normal to boundary, liquid VF `0.0` |
| `inlet_wet_outer` | `Velocity Inlet` | `26.81 m/s`, normal to boundary, liquid VF `0.018656` |
| steam outlet | `Pressure Outlet` | baseline pressure, explicit steam-dominant backflow |
| brine outlet | `Pressure Outlet` | pressure to be checked, explicit liquid-dominant backflow |

Solution methods:

| Setting | Value |
|---|---:|
| Pressure-velocity coupling | `SIMPLE` |
| Gradient | `Green-Gauss Node Based` |
| Pressure | `PRESTO!` |
| Momentum | `Second Order Upwind` |
| Turbulent kinetic energy | `Second Order Upwind` |
| Turbulent dissipation rate | `Second Order Upwind` |
| Volume fraction | `QUICK` if available, otherwise closest higher-order option |
| Initialization | `Hybrid Initialization` |
| Water pool patch | not used in first run |

## 6. FFF-2 Result and Interpretation

Run identity:

| Item | Value |
|---|---|
| Run ID | `FFF-2` (`Assumed` from user naming; no separate Fluent run ID found yet) |
| Iteration count | `1020` steady iterations |
| Case file | `FFF-2-2.cas.h5` |
| Additional case/setup file | `FFF-2-Setup-Output.cas.h5` |
| Data file | `FFF-2-2-01024.dat.h5` |
| Residual status | still moving noticeably; not converged |
| Inlet velocity check | liquid inlet and steam inlet area-weighted average velocity magnitude both `26.81 m/s` |

Reported Fluent mass-flow fluxes after `1020` iterations:

```text
Liquid phase:
liquid inlet   =  109.8065259020202 kg/s
liquid outlet  = -161.0144320500405 kg/s
steam inlet    =   -0.0 kg/s
steam outlet   =   -0.00959419105001484 kg/s
net            =  -51.2175 kg/s

Steam phase:
liquid inlet   =   37.53446178758816 kg/s
liquid outlet  =  -19.41428612506385 kg/s
steam inlet    =   37.82770891200012 kg/s
steam outlet   =  -55.55540052237878 kg/s
net            =    0.3924841 kg/s
```

Interpretation of sign convention:

- positive = entering domain
- negative = leaving domain

Phase balance:

```text
Liquid in  = 109.8065259020202 kg/s
Liquid out = 161.0144320500405 + 0.00959419105001484 = 161.0240262410905 kg/s
Liquid net = 109.8065259020202 - 161.0240262410905 = -51.2175003390703 kg/s

Steam in  = 37.53446178758816 + 37.82770891200012 = 75.36217069958828 kg/s
Steam out = 19.41428612506385 + 55.55540052237878 = 74.96968664744263 kg/s
Steam net = 75.36217069958828 - 74.96968664744263 = 0.39248405214565 kg/s
```

The steam phase is approximately balanced. The liquid phase is not balanced: the outlets remove about `51.22 kg/s` more liquid than enters through the inlet during this report state.

The brine outlet, labelled here as `liquid outlet`, is removing:

```text
liquid out through brine outlet = 161.0144320500405 kg/s
steam out through brine outlet  = 19.41428612506385 kg/s
```

The brine outlet is now removing a large amount of liquid, unlike the earlier low-drainage result. However, the liquid phase balance is not yet physically acceptable because liquid outflow exceeds liquid inflow even though no water-pool patch was used.

Likely causes:

- no initialized water pool in the lower separator
- residuals are still moving, so this may be an intermediate non-converged state
- Fluent may still be draining or redistributing liquid from the initialized/hybrid field rather than reaching a steady operating balance
- brine outlet pressure may be over-driving liquid discharge after more iterations
- outlet backflow phase fractions may need correction
- steady Mixture model may not form a realistic liquid inventory from a dry initial condition before residuals stabilize
- lower geometry and outlet placement may still need liquid already present before the solution develops

Recommended next variant:

- do not treat the `1020`-iteration fluxes as final validation data
- first continue or inspect monitor history to see whether liquid net imbalance is trending toward zero or moving farther away
- keep the matching `FFF-2-2-01024.dat.h5` data file linked with the `FFF-2-2.cas.h5` case file when reopening the run
- confirm outlet backflow phase fractions before changing geometry or physics
- if the same setup is continued, collect flux reports at multiple iteration counts to see whether brine outlet liquid flow is stabilizing

## 7. Current conclusion

The inlet settings are producing a reasonable total inlet phase scale:

```text
liquid inlet = 109.8065259020202 kg/s
steam inlet total = 37.53446178758816 + 37.82770891200012 = 75.36217069958828 kg/s
```

These are close enough to the target paper values to make the run diagnostically useful. The outlet behavior has changed from under-draining liquid to over-removing liquid, so the run should be treated as non-converged diagnostic evidence rather than validation evidence.
