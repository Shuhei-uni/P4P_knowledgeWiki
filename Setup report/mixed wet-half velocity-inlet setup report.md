# Mixed Wet-Half Velocity-Inlet Setup Report

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

## 6. Flux report result and interpretation (2026-05-06)

Reported Fluent mass-flow fluxes:

```text
Liquid phase:
liquid inlet   =  109.8 kg/s
liquid outlet  =   -5.66 kg/s
steam inlet    =    0.0 kg/s
steam outlet   =   -2.5622 kg/s

Steam phase:
liquid inlet   =   37.53 kg/s
liquid outlet  =  -13.84 kg/s
steam inlet    =   37.83 kg/s
steam outlet   =  -62.36 kg/s
```

Interpretation of sign convention:

- positive = entering domain
- negative = leaving domain

Phase balance:

```text
Liquid in  = 109.8 kg/s
Liquid out = 5.66 + 2.5622 = 8.22 kg/s
Liquid imbalance / retained liquid = 101.58 kg/s

Steam in  = 37.53 + 37.83 = 75.36 kg/s
Steam out = 13.84 + 62.36 = 76.20 kg/s
Steam imbalance = -0.84 kg/s
```

The steam phase is approximately balanced. The liquid phase is not balanced: most of the injected liquid is staying inside the separator rather than leaving through the brine outlet.

The brine outlet, labelled here as `liquid outlet`, is removing:

```text
liquid out through brine outlet = 5.66 kg/s
steam out through brine outlet  = 13.84 kg/s
```

So the brine outlet is currently behaving more like a mixed/gas outlet than a liquid drain. This supports the interpretation that the brine outlet setup is not yet functioning physically.

Likely causes:

- no initialized water pool in the lower separator
- brine outlet pressure is not driving liquid discharge strongly enough
- outlet backflow phase fractions may need correction
- steady Mixture model may not form a realistic liquid inventory from a dry initial condition
- lower geometry and outlet placement may need liquid already present before the solution develops

Recommended next variant:

- keep the same wet-half velocity inlet
- initialize/patch a liquid water pool in the lower separator
- set brine outlet backflow liquid volume fraction near `1.0`
- set steam outlet backflow liquid volume fraction near `0.0`
- check whether liquid outlet flow rises toward the required order of `100 kg/s`

## 7. Current conclusion

The inlet settings are producing a reasonable total inlet phase scale:

```text
liquid inlet = 109.8 kg/s
steam inlet total = 37.53 + 37.83 = 75.36 kg/s
```

These are close enough to the target paper values to make the run diagnostically useful, but the outlet behavior is not yet valid because the brine outlet is removing far too little liquid.

