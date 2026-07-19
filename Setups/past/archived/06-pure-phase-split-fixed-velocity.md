# Pure-Phase Fixed-Velocity Split-Inlet Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `06` |
| Lifecycle | `archived` |
| Role | alternate pure-phase split setup |
| Parent setup | [04](../reported/04-mixed-wet-half-actual-area.md) |
| Evidence-use label | setup definition only |
| Outcome | retained alternate |
| Linked report | none |

## 1. Purpose

Define a new spiral-inlet setup where the inlet is split into:

- one pure-liquid side;
- one pure-steam side;
- both sides use Purnanto's reported spiral-inlet velocity, `26.81 m/s`.

This is separate from the earlier actual-area correction that recalculated velocity to force exact Purnanto mass flow through the current measured inlet area.

Geometry naming note:

- this split-inlet branch still uses the `purnanto` geometry label;
- the geometry label is separate from the inlet boundary-condition style, so a two-zone split inlet does not by itself make the geometry `purnantov2`.

## 2. Setup Identity

| Item | Value |
|---|---:|
| Geometry | `purnanto` spiral-inlet BOC separator |
| Inlet representation | pure liquid / pure steam split inlet |
| Boundary type | two `Velocity Inlet` zones |
| Liquid-side phase state | liquid VF `1.0`, steam VF `0.0` |
| Steam-side phase state | liquid VF `0.0`, steam VF `1.0` |
| Velocity magnitude | `26.81 m/s` |
| Current inlet width | `0.724 m` |
| Current inlet height | `0.724 m` |
| Current inlet area | `0.524176 m2` |
| Purnanto `1600 kJ/kg` liquid target | `116.92 kg/s` |
| Purnanto `1600 kJ/kg` steam target | `80.69 kg/s` |
| Purnanto `1600 kJ/kg` total target | `197.61 kg/s` |

Evidence labels:

- `Reported`: Purnanto baseline values already extracted in the project setup notes.
- `Calculated`: area ratio, split location, and resulting mass flows calculated from reported values.
- `Assumed`: rectangular inlet face of `0.724 m x 0.724 m`, split along the `x` direction while preserving full `0.724 m` height.

## 3. Key Finding

With the current inlet area fixed at `0.724 m x 0.724 m` and the velocity fixed at `26.81 m/s`, exact Purnanto phase mass flow cannot be matched at the same time.

Reason:

```text
Purnanto required volumetric flow = 14.2146214 m3/s
Area needed at 26.81 m/s        = 14.2146214 / 26.81
Area needed                     = 0.5301985 m2

Current area = 0.724 * 0.724
Current area = 0.524176 m2
```

The current inlet area is about `1.14 %` smaller than the area implied by `26.81 m/s` and the exact Purnanto phase mass flows.

Therefore the fixed-velocity setup should preserve the **phase ratio and velocity**, while accepting a slightly lower total mass flow.

## 4. Phase Volumetric Flow Basis

Inputs:

```text
m_dot_liquid_target = 116.92 kg/s
m_dot_steam_target  = 80.69 kg/s
rho_liquid          = 881.77 kg/m3
rho_steam           = 5.73 kg/m3
V_reported          = 26.81 m/s
```

Volumetric flows:

```text
Q_liquid = 116.92 / 881.77 = 0.1325969 m3/s
Q_steam  = 80.69 / 5.73    = 14.0820244 m3/s
Q_total  = 14.2146214 m3/s
```

Area fractions:

```text
f_liquid = Q_liquid / Q_total = 0.0093282
f_steam  = Q_steam  / Q_total = 0.9906718
```

So the inlet area ratio is:

```text
liquid : steam = 0.0093282 : 0.9906718
liquid : steam = 1 : 106.20
```

## 5. Recommended Current-Geometry Split

Use this when the actual inlet remains `0.724 m x 0.724 m`.

Total area:

```text
A_total = 0.724 * 0.724 = 0.524176 m2
```

Split areas:

```text
A_liquid = 0.524176 * 0.0093282 = 0.0048896 m2
A_steam  = 0.524176 * 0.9906718 = 0.5192864 m2
```

If splitting along `x` while keeping full height `0.724 m`:

```text
x_liquid_width = 0.0048896 / 0.724 = 0.0067536 m
x_steam_width  = 0.5192864 / 0.724 = 0.7172464 m
```

Place the split line:

```text
0.006754 m from the liquid-side edge
```

or equivalently:

```text
0.717246 m from the steam-side edge
```

## 6. Resulting Mass Flow at `26.81 m/s`

Mass-flow check using the current-geometry split:

```text
m_dot_liquid = 881.77 * 26.81 * 0.0048896 = 115.59 kg/s
m_dot_steam  = 5.73   * 26.81 * 0.5192864 = 79.77 kg/s
m_dot_total  = 195.37 kg/s
```

Comparison with Purnanto target:

| Quantity | Purnanto target | Fixed-velocity current-geometry result | Difference |
|---|---:|---:|---:|
| Liquid mass flow | `116.92 kg/s` | `115.59 kg/s` | `-1.33 kg/s` |
| Steam mass flow | `80.69 kg/s` | `79.77 kg/s` | `-0.92 kg/s` |
| Total mass flow | `197.61 kg/s` | `195.37 kg/s` | `-2.24 kg/s` |
| Relative total difference | - | - | `-1.14 %` |

This is the consistent setup if the priority is matching the reported spiral-inlet velocity and using the current `0.724 m x 0.724 m` inlet geometry.

## 7. Exact-Mass Alternative at `26.81 m/s`

Use this only if the geometry can be resized or if the inlet area in the active CAD is later found to be closer to the paper-implied area.

Required total area:

```text
A_required = Q_total / 26.81
A_required = 0.5301985 m2
```

Required phase areas:

```text
A_liquid_required = Q_liquid / 26.81 = 0.0049458 m2
A_steam_required  = Q_steam  / 26.81 = 0.5252527 m2
```

If height stays `0.724 m`, required widths would be:

```text
x_liquid_required = 0.0049458 / 0.724 = 0.006831 m
x_steam_required  = 0.5252527 / 0.724 = 0.725487 m
total required width = 0.732318 m
```

This is wider than the current `0.724 m` inlet, so it is not compatible with the current inlet dimensions unless the geometry is changed.

## 8. Fluent Boundary Conditions

Create two separate inlet faces in geometry/meshing:

| Boundary | Type | Velocity | Liquid VF | Steam VF |
|---|---|---:|---:|---:|
| `inlet_liquid_outer` | `Velocity Inlet` | `26.81 m/s` | `1.0` | `0.0` |
| `inlet_steam_inner` | `Velocity Inlet` | `26.81 m/s` | `0.0` | `1.0` |

Use the current-geometry split unless the inlet area is changed:

```text
liquid-side width = 0.006754 m
steam-side width  = 0.717246 m
```

Mapping rule:

- liquid side should be the outer-wall side of the spiral inlet;
- steam side should be the inner/core side;
- do not rely only on screen-left/screen-right naming.

## 9. Solver Settings to Keep

Keep the baseline setup unchanged so this run tests only inlet distribution:

| Setting | Value |
|---|---:|
| Solver | `Pressure-Based` |
| Time | `Steady` |
| Multiphase model | `Mixture` |
| Primary phase | steam/vapor |
| Secondary phase | liquid water |
| Turbulence model | `RNG k-epsilon` |
| Energy | `Off` |
| Gravity | `On` |
| Pressure-velocity coupling | `SIMPLE` |
| Pressure scheme | `PRESTO!` |
| Momentum/turbulence schemes | `Second Order Upwind` |
| Volume fraction scheme | `QUICK` if available |
| Initialization | `Hybrid Initialization` |

## 10. Checks Before Running

1. Confirm the split creates two real boundary faces, not only a sketch line.
2. Confirm the `6.754 mm` liquid strip has enough mesh resolution across its width.
3. Confirm the liquid strip is on the outer-wall side of the spiral inlet.
4. After initialization, run a flux report on both inlet zones and check:

```text
liquid inlet ~= 115.59 kg/s
steam inlet  ~= 79.77 kg/s
total inlet  ~= 195.37 kg/s
```

5. Do not compare this run directly against an exact `197.61 kg/s` run without noting the `-1.14 %` total mass-flow difference.

## 11. Interpretation

This setup is best described as:

```text
Purnanto-velocity-matched, current-area pure-phase split inlet
```

It matches:

- reported spiral-inlet velocity: `26.81 m/s`;
- phase volumetric ratio from Purnanto `1600 kJ/kg`;
- current measured inlet size: `0.724 m x 0.724 m`.

It does not exactly match:

- Purnanto total mass flow `197.61 kg/s`.

The mass-flow mismatch is small enough for a controlled diagnostic run, but it must be reported.
