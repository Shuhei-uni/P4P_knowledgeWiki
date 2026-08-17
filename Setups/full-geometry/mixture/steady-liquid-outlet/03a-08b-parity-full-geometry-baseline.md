# Setup 03A — 08b-Parity Full-Geometry Steady Mixture Baseline

> **Lifecycle:** `draft — baseline definition substantially specified`  
> **Execution status:** `DO NOT RUN until 08b-parity readback and full-geometry boundary preflight pass`  
> **Primary objective:** reproduce the trusted `08b` / audited-Purnanto continuous-phase setup on the current full geometry, then add only the physical brine outlet required by that geometry.  
> **Baseline rule:** `08b carrier setup + full geometry + brine pressure outlet at 1.120 MPa`; do **not** use `FG-MIX-T01-S1-C1375` as the setup parent.  
> **Child setup:** [`03B`](03b-brine-pressure-continuation.md) continues this same steady field while changing only brine-outlet pressure.

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03A` |
| Setup authority | `08b-purnanto-parity-split-inlet-rebuild` |
| Underlying carrier authority | `00a-purnanto-setup-5000-live-audit` / audited Purnanto case-data |
| Historical full-geometry evidence | `02c`, `02e`, `FG-MIX-T01-S1-C1375` — evidence only, not setup authority |
| Geometry | current full separator geometry with explicit brine outlet |
| Inlet representation | pure-liquid outer split + pure-steam inner split |
| Time model | steady |
| Initialization | Hybrid Initialization only |
| Liquid patch | **none** |
| DPM injections | none active for carrier convergence |
| EWF | off / not part of this carrier baseline |
| Steam outlet | Pressure Outlet, `1.120 MPa gauge` |
| Brine outlet | Pressure Outlet, baseline `1.120 MPa gauge` |
| Primary question | can the `08b`-parity carrier setup remain numerically useful after restoring the full lower vessel and opening a physical brine outlet? |

---

## 1. Setup intent and lineage

This is **not** a cleaned-up version of `FG-MIX-T01-S1-C1375`.

The intended model is:

```text
trusted 08b/Purnanto continuous-phase setup
+ current full geometry
+ physical brine pressure outlet
= 03A baseline
```

`02c`, `02e`, and `C1375` remain useful because they proved that brine-outlet pressure strongly affects liquid drainage, vapour short-circuiting, reverse flow, and solver stability. They must not define the baseline carrier physics, turbulence settings, material values, numerical methods, initialization, or relaxation factors.

03A deliberately answers the simplest first question:

> What happens when the trusted 08b-style steady carrier setup is transferred to the full separator and the previously omitted lower brine discharge is opened at the same pressure as the steam outlet?

Brine-pressure tuning belongs to 03B and begins only from the saved 03A field.

---

## 2. Geometry context

The full geometry retains the Purnanto Spiral-Inlet BOC design lineage but includes the lower vessel and physical brine pipe that were excluded from the simplified Purnanto carrier calculation.

Reference Spiral-Inlet values from Table 3:

| Parameter | Reference value |
|---|---:|
| Vessel diameter `D` | `2.134 m` |
| Spiral inlet dimension `De` | `0.724 m` |
| Brine outlet diameter `Db` | `0.508 m` |
| `alpha` | `0.200 m` |
| `beta` | `2.320 m` |
| `Z` | `4.195 m` |
| `LT` | `4.929 m` |
| `LB` | `3.579 m` |
| Spiral inlet area `Ao` | `0.5242 m²` |

Execution mesh:

```text
Full-geomV2-231kcells.msh.h5
cells ≈ 231,376
```

Before running, extract from the actual mesh and record:

- liquid split-inlet area and wetted perimeter;
- steam split-inlet area and wetted perimeter;
- total inlet area;
- steam-outlet area / hydraulic diameter;
- brine-outlet area / hydraulic diameter;
- exact zone names and zone types;
- minimum orthogonal quality;
- maximum skewness / aspect ratio where available.

Table-3 dimensions provide physical context. The production mesh is execution authority.

---

## 3. Split inlet — retain the 08b project representation

The inlet is the project's intentionally idealized pure-phase split of the original rectangular spiral inlet:

- outer-wall strip = pure liquid;
- inner/core region = pure steam;
- both are sub-faces of the same spiral inlet cross-section;
- both use the common inlet velocity `27.118 m/s`.

Reference split:

```text
full inlet           = 0.724 m × 0.724 m
A_total              = 0.524176 m²
A_liquid             = 0.0048896 m²
A_steam              = 0.5192864 m²
liquid-side width    = 0.0067536 m
steam-side width     = 0.7172464 m
```

Reference phase-flow targets are approximately:

```text
liquid = 116.92 kg/s
steam  = 80.69 kg/s
total  = 197.61 kg/s
```

### Liquid inlet

| Fluent field | Required value |
|---|---:|
| Boundary type | Velocity Inlet |
| Phase state | pure liquid; secondary liquid VF `1.0` |
| Velocity specification | Magnitude, Normal to Boundary |
| Velocity | `27.118 m/s` |
| Reference frame | Absolute |
| Initial / supersonic gauge pressure | `1,140,000 Pa` |
| Turbulence specification | Intensity and Hydraulic Diameter |
| Turbulence intensity | `2.11 %` |
| Hydraulic diameter | `0.01338 m` expected from 08b split; verify from actual mesh |

### Steam inlet

| Fluent field | Required value |
|---|---:|
| Boundary type | Velocity Inlet |
| Phase state | pure vapour; secondary liquid VF `0.0` |
| Velocity specification | Magnitude, Normal to Boundary |
| Velocity | `27.118 m/s` |
| Reference frame | Absolute |
| Initial / supersonic gauge pressure | `1,140,000 Pa` |
| Turbulence specification | Intensity and Hydraulic Diameter |
| Turbulence intensity | `2.11 %` |
| Hydraulic diameter | `0.72061 m` expected from 08b split; verify from actual mesh |

`0.72061` is a hydraulic diameter in metres. Do not reproduce the historical viscosity-ratio mis-assignment.

---

## 4. Continuous-phase physics — 08b / audited-Purnanto authority

### General

| Setting | Required state |
|---|---|
| Solver | Pressure-Based |
| Time | Steady |
| Velocity formulation | Absolute |
| Energy | Off |
| Gravity | `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Operating density method | `mixture-averaged` |
| Operating temperature | `298.15 K` where exposed |
| Pseudo-time | Off |

### Mixture model

| Setting | Required state |
|---|---|
| Multiphase | Mixture |
| Phases | `2` |
| Primary phase | water vapour / `water-vapor-at-psep` equivalent |
| Secondary phase | liquid water / `water-liquid-at-psep` equivalent |
| Energy / phase change | off / none |

Mixture interaction details must be positively read back from the 08b/audited-Purnanto authority rather than inherited from C1375 or accepted as unexplained defaults. This includes secondary-phase diameter, slip relation, drag/interfacial options, and surface-tension state.

### Material properties

Use the audited Fluent values:

| Material | Density | Dynamic viscosity |
|---|---:|---:|
| vapour | `5.7974339 kg/m³` | `1.52062e-05 kg/(m·s)` |
| liquid | `881.21088 kg/m³` | `1.45544e-04 kg/(m·s)` |

---

## 5. Turbulence and walls

Use the audited Purnanto/08b configuration:

```text
RNG k-epsilon
Standard Wall Functions
Differential Viscosity Model = On
Swirl Dominated Flow = On
```

Any other expert turbulence field should be read back from 08b and matched explicitly.

All physical walls:

```text
stationary
no slip
roughness height = 0 m
roughness constant = 0.5 where exposed
```

---

## 6. Steam outlet — retained 08b boundary

| Fluent field | Required value |
|---|---:|
| Boundary type | Pressure Outlet |
| Gauge pressure | `1,120,000 Pa` |
| Backflow direction | Normal to Boundary |
| Backflow pressure specification | Total Pressure |
| Backflow turbulence specification | Intensity and Hydraulic Diameter |
| Backflow turbulence intensity | `2.1525 %` |
| Backflow hydraulic diameter | `0.724 m` reference; verify against actual outlet |
| Secondary liquid backflow VF | `0.0` |

The steam outlet is not an experimental variable in 03A or 03B.

---

## 7. Brine outlet — new full-geometry boundary

Use a Pressure Outlet.

For 03A:

```text
P_brine = 1,120,000 Pa gauge
```

This is deliberately equal to the steam-outlet pressure. It is not claimed to be the final physical brine-line backpressure; it simply isolates the effect of opening the additional physical outlet before pressure continuation begins.

Backflow settings:

| Fluent field | Required value |
|---|---:|
| Backflow direction | Normal to Boundary |
| Backflow pressure specification | Total Pressure |
| Secondary liquid backflow VF | `1.0` |
| Vapour backflow VF | `0.0` implied |
| Turbulence specification | Intensity and Hydraulic Diameter |

For the reference `Db = 0.508 m`, the provisional brine backflow turbulence estimate is approximately:

```text
I_brine ≈ 2.61 %
Dh_brine ≈ 0.508 m
```

Recalculate from the actual full-geometry brine-outlet area/perimeter before execution. The mesh value wins if it differs from Table 3.

---

## 8. Numerical method — audited Purnanto/08b stack

### Solution methods

| Numerical item | Required value |
|---|---|
| Pressure-velocity coupling | `SIMPLE` |
| Gradient | `Green-Gauss Node Based` |
| Pressure | `PRESTO!` |
| Momentum | `Second Order Upwind` |
| Volume fraction | `QUICK` |
| Turbulent kinetic energy | `Second Order Upwind` |
| Turbulent dissipation rate | `Second Order Upwind` |
| Pseudo-time | Off |
| Rhie-Chow high-order-term relaxation | disabled |

### Under-relaxation factors

| Variable | URF |
|---|---:|
| Pressure | `0.3` |
| Momentum | `0.7` |
| Density | `1.0` |
| Body force | `1.0` |
| Slip / drift | `0.1` |
| Volume fraction | `0.4` |
| `k` | `0.8` |
| `epsilon` | `0.8` |
| Turbulent viscosity | `1.0` |

### Residual monitor criteria

| Equation | Absolute criterion |
|---|---:|
| Continuity | `1e-4` |
| x/y/z velocity | `1e-3` |
| Volume fraction | `1e-3` |
| `k` | `1e-3` |
| `epsilon` | `1e-3` |

Residuals are diagnostics, not the sole steady-state criterion.

---

## 9. Initialization and baseline run

Run sequence:

```text
load full-geometry mesh
→ apply 08b/audited-Purnanto carrier settings
→ configure pure-phase split inlet
→ configure retained steam outlet
→ configure brine outlet at 1.120 MPa
→ read back all settings and compare with authority
→ Hybrid Initialize
→ NO liquid patch
→ solve steady
```

Do not use Y010/Y030 patching, equation staging, Coupled, first-order rescue, pseudo-time, altered URFs, or C1375 solution controls in the 03A baseline.

Before iteration 1, produce a machine-readable comparison:

```text
08b / audited-Purnanto authority
03A requested value
03A Fluent readback
```

Any unexplained mismatch is a preflight failure.

---

## 10. Monitoring

Record throughout the solve:

- liquid inlet mass flux;
- vapour inlet mass flux;
- liquid → brine outlet;
- liquid → steam outlet;
- vapour → steam outlet;
- vapour → brine outlet;
- total outlet fluxes;
- total liquid inventory in the domain;
- Y010 and Y030 liquid inventory as diagnostics only — **no patching**;
- brine-outlet reverse-flow sign / area where available;
- brine-pipe-entry static and total pressure;
- residual histories;
- turbulent-viscosity limiting count / region.

A `500`-iteration checkpoint is useful, but iteration count alone does not qualify the case as steady.

---

## 11. 03A outcome and handoff to 03B

03A is successful as a parent when the solution is numerically stable enough to provide a meaningful developed field for continuation. Ideally the phase fluxes and liquid inventory have reached a plateau; if they are still changing strongly, do not disguise that by immediately changing pressure.

If 03A is stable but drains liquid too rapidly, that is exactly the condition 03B is intended to investigate.

If 03A fails catastrophically before a useful developed field exists, do **not** start 03B. Diagnose the baseline first.

When ready, save an immutable 03A case/data checkpoint and begin [`03B — brine-pressure continuation`](03b-brine-pressure-continuation.md) from that exact field without reinitialization.

03A does not establish final brine pressure, retained liquid level, separator efficiency, DPM performance, transient stability, or plant validation.