# Setup 03 — 08b-Parity Full-Geometry Steady Mixture With Brine Outlet

> **Lifecycle:** `draft — baseline definition substantially specified`  
> **Execution status:** `DO NOT RUN until 08b-parity readback and full-geometry boundary preflight pass`  
> **Primary objective:** reproduce the trusted `08b` / audited-Purnanto continuous-phase setup on the current full geometry, then add only the physical brine outlet required by that geometry.  
> **Baseline rule:** `08b carrier setup + full geometry + brine pressure outlet`; **do not use FG-MIX-T01-S1-C1375 as the setup parent.**

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03` |
| Setup authority | `08b-purnanto-parity-split-inlet-rebuild` |
| Underlying carrier authority | `00a-purnanto-setup-5000-live-audit` / audited Purnanto case-data |
| Historical full-geometry evidence | `02c`, `02e`, `FG-MIX-T01-S1-C1375` — evidence only, **not setup authority** |
| Geometry | current full separator geometry with explicit brine outlet |
| Inlet representation | pure-liquid outer split + pure-steam inner split |
| Time model | steady |
| Initialization | Hybrid Initialization only |
| Liquid patch | **none** |
| DPM injections | none active for the carrier baseline |
| EWF | off / not part of this carrier baseline |
| Steam outlet | Pressure Outlet, `1.120 MPa gauge` |
| Brine outlet | new Pressure Outlet on the full geometry; baseline `1.120 MPa gauge` |
| Primary question | can the `08b`-parity carrier setup remain numerically steady after restoring the full lower vessel and opening a physical brine outlet? |

---

## 1. Setup intent

This setup is **not** a cleaned-up version of `FG-MIX-T01-S1-C1375`.

The intended model is much simpler conceptually:

```text
trusted 08b/Purnanto continuous-phase setup
+ current full geometry
+ physical brine pressure outlet
= Setup 03 baseline
```

`FG-MIX-T01-S1-C1375`, `02c`, and `02e` remain useful because they showed that brine-outlet pressure strongly changes phase routing and numerical behaviour. They must not dictate the baseline turbulence model options, material values, under-relaxation factors, discretization, initialization, or other carrier settings.

The purpose of Setup 03 is to answer one controlled question before any new tuning:

> **If the carrier-flow setup that was deliberately rebuilt for Purnanto parity in 08b is transferred to the full separator geometry and given a real brine outlet, can that model reach a useful steady state without liquid patching or numerical rescue methods?**

If the answer is no, later child setups may change one item at a time. The baseline itself should remain interpretable.

---

## 2. Authority and inheritance rules

### 2.1 Primary authority — Setup 08b

Setup `08b` exists specifically as the project parity-reset branch. Its rule is to preserve the **observed Purnanto Fluent carrier setup** and change only the inlet representation required by the project.

For Setup 03, inherit from `08b` / `00a`:

- pressure-based steady solver;
- Mixture multiphase model and phase mapping;
- RNG `k-epsilon` turbulence configuration;
- operating conditions;
- material properties;
- solver numerics;
- under-relaxation factors;
- residual monitor settings;
- steam pressure-outlet treatment;
- Hybrid Initialization;
- smooth-wall treatment;
- no active DPM injections during carrier convergence.

### 2.2 Deliberate changes allowed in Setup 03

The baseline deliberately changes only what the full geometry requires:

1. replace the simplified/Purnanto lower-domain treatment with the current full geometry;
2. retain the project split inlet on the full geometry;
3. retain the existing steam outlet on the full geometry;
4. introduce the physical brine-outlet boundary as a second Pressure Outlet;
5. add diagnostics needed to judge the new brine-outlet behaviour.

Everything else should match `08b` as closely as the current Fluent version and full mesh allow.

### 2.3 C1375 rule

Do **not** copy a value from `FG-MIX-T01-S1-C1375` merely because it already exists in that case.

A C1375 value may be reused only if:

- it independently matches the 08b / audited-Purnanto authority; or
- it is a full-geometry-only field for which 08b has no equivalent and the value is explicitly justified in this document.

---

## 3. Geometry context

The full geometry retains the Spiral-Inlet BOC design lineage described by Purnanto, Zarrouk & Cater.

Reference Spiral-Inlet dimensions from Table 3 are:

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

The reference paper intentionally did **not** solve the water discharge through the bottom brine pipe; its lower liquid level was assumed constant just above that outlet. Setup 03 removes that simplification by retaining the project's actual lower fluid region and physical brine pipe/outlet.

Therefore the brine outlet is the major new physical boundary relative to the Purnanto/08b carrier problem.

### 3.1 Full-geometry execution mesh

Use the current production full-geometry mesh:

```text
Full-geomV2-231kcells.msh.h5
```

Known project count:

```text
cells = 231,376
```

Before execution, extract directly from the mesh and record:

- actual liquid split-inlet area;
- actual steam split-inlet area;
- total inlet area;
- steam-outlet area / hydraulic diameter;
- brine-outlet area / hydraulic diameter;
- zone names and types;
- minimum orthogonal quality;
- maximum skewness / aspect ratio where available.

Table-3 dimensions are context; measured production-mesh values are execution authority.

---

## 4. Split inlet — retain 08b project representation

The split inlet is an idealized pre-separated representation of the single rectangular spiral inlet:

- outer-wall side = pure liquid;
- inner/core side = pure steam;
- both sub-faces belong to the same spiral inlet cross-section;
- both use the common project velocity `27.118 m/s`.

Reference split geometry:

```text
full inlet           = 0.724 m × 0.724 m
A_total              = 0.524176 m²
A_liquid             = 0.0048896 m²
A_steam              = 0.5192864 m²
liquid-side width    = 0.0067536 m
steam-side width     = 0.7172464 m
```

Using the Purnanto reference phase flows, this gives approximately:

```text
liquid = 116.92 kg/s
steam  = 80.69 kg/s
total  = 197.61 kg/s
```

This is an intentional project deviation from Purnanto's mixed/mist inlet. It is kept because it is the defining continuous-phase inlet hypothesis of `08b`.

### 4.1 Liquid inlet

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
| Hydraulic diameter | `0.01338 m` expected from 08b split; recompute from actual mesh split area/perimeter and verify |

### 4.2 Steam inlet

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
| Hydraulic diameter | `0.72061 m` expected from 08b split; recompute from actual mesh split area/perimeter and verify |

**Do not reproduce the historical `0.72061` viscosity-ratio mis-assignment.** In the intended split-inlet geometry this number is a hydraulic diameter in metres.

---

## 5. Continuous-phase physics — use audited Purnanto/08b authority

### 5.1 General

| Setting | Required state |
|---|---|
| Solver | Pressure-Based |
| Time | Steady |
| Velocity formulation | Absolute |
| Energy | Off |
| Gravity | enabled |
| Gravity vector | `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Operating density method | `mixture-averaged` |
| Operating temperature | `298.15 K` where the current Fluent branch exposes it |
| Pseudo-time | Off |

### 5.2 Mixture model

| Setting | Required state |
|---|---|
| Multiphase | Mixture |
| Number of phases | `2` |
| Phase 1 / primary | `water-vapor-at-psep` equivalent |
| Phase 2 / secondary | `water-liquid-at-psep` equivalent |
| Energy / phase change | off / none |

For lower-level Mixture interaction settings such as secondary-phase diameter, slip relation, drag/interfacial options, and surface-tension state, **the 08b/audited-Purnanto case is the authority**. They must be extracted and replayed rather than copied from C1375 or reconstructed from Fluent defaults.

Execution rule:

> if the current exporter cannot positively read back a required 08b Mixture interaction field, stop the preflight and extract it before solving.

### 5.3 Material properties — use audited live values

The parity branch should use the values observed in the audited Purnanto Fluent case rather than silently reverting to rounded paper values:

| Material | Density | Dynamic viscosity |
|---|---:|---:|
| vapour | `5.7974339 kg/m³` | `1.52062e-05 kg/(m·s)` |
| liquid | `881.21088 kg/m³` | `1.45544e-04 kg/(m·s)` |

The rounded paper values (`5.73`, `881.77`, etc.) remain useful literature context, but the audited Fluent values are the 08b parity authority.

---

## 6. Turbulence — retain the audited Purnanto configuration

Use:

```text
RNG k-epsilon
Standard Wall Functions
```

The audited Purnanto/08b carrier state includes:

| RNG option | Required state |
|---|---|
| Differential Viscosity Model | **On** |
| Swirl Dominated Flow | **On** |
| Standard Wall Functions | **On** |
| Curvature correction | retain 08b/audited state |
| Other expert turbulence options | retain 08b/audited state; verify by readback |

This is intentionally different from the earlier C1375-derived draft that proposed a basic/default RNG configuration. Setup 03 should reproduce 08b, not simplify the turbulence model merely because the current full-geometry case happened to use different defaults.

### 6.1 Walls

All physical walls:

```text
stationary
no slip
roughness height = 0 m
roughness constant = 0.5 where Fluent exposes the field
```

This preserves the audited smooth-wall Purnanto treatment.

---

## 7. Steam outlet — retain 08b / audited Purnanto treatment

| Fluent field | Required value |
|---|---:|
| Boundary type | Pressure Outlet |
| Gauge pressure | `1,120,000 Pa` |
| Backflow direction | Normal to Boundary |
| Backflow pressure specification | Total Pressure |
| Backflow turbulence specification | Intensity and Hydraulic Diameter |
| Backflow turbulence intensity | `2.1525 %` |
| Backflow hydraulic diameter | `0.724 m` reference; verify against actual full-geometry outlet |
| Secondary liquid backflow VF | `0.0` |

This outlet is not a new experiment variable. It is retained from the trusted carrier baseline.

---

## 8. Brine outlet — the primary new boundary

The full geometry adds a brine discharge that 08b/Purnanto did not actively solve.

### 8.1 Baseline type

Use:

```text
Pressure Outlet
```

The first baseline should avoid importing the C1375 backpressure tuning into the carrier definition.

Therefore start with:

```text
P_brine = 1,120,000 Pa gauge
```

This makes both outlets use the same reference pressure and isolates the effect of **opening the additional physical outlet**.

This is a baseline modelling choice, not a claim that `1.120 MPa` is the final physically correct brine-line pressure. If the resulting steady field over-drains or backflows strongly, brine pressure becomes a controlled child sensitivity after the 08b-parity baseline has been documented.

### 8.2 Brine backflow composition and direction

| Fluent field | Required value |
|---|---:|
| Backflow direction | Normal to Boundary |
| Backflow pressure specification | Total Pressure |
| Secondary liquid backflow VF | `1.0` |
| Vapour backflow VF | `0.0` implied |
| Turbulence specification | Intensity and Hydraulic Diameter |

### 8.3 Brine-outlet turbulence

Use the same internal-flow turbulence-intensity methodology that reproduces the audited steam-outlet value rather than copying C1375 defaults.

Reference Table-3 brine diameter:

```text
Db = 0.508 m
```

Using the design liquid flow near `116.92 kg/s` with the audited liquid properties gives an expected mean pipe velocity of approximately:

```text
U_brine ≈ 0.655 m/s
Re_brine ≈ 2.01e6
```

Using the standard project internal-flow intensity estimate:

```text
I = 0.16 Re^(-1/8)
```

gives approximately:

```text
I_brine_backflow ≈ 2.61 %
```

Therefore the provisional brine backflow turbulence is:

| Field | Baseline value |
|---|---:|
| Intensity | `~2.61 %` |
| Hydraulic diameter | `0.508 m` expected |

Before execution, recompute both from the **actual full-geometry brine-outlet area/perimeter**. If the production mesh does not match `Db = 0.508 m`, the actual mesh geometry wins.

---

## 9. Numerical method — copy the audited Purnanto/08b carrier stack

Do not use C1375 numerics as the authority.

### 9.1 Solution methods

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

### 9.2 Under-relaxation factors

Use the values observed in the audited Purnanto setup:

| Variable | URF |
|---|---:|
| Pressure | `0.3` |
| Momentum | `0.7` |
| Density | `1.0` |
| Body force | `1.0` |
| Slip / drift | `0.1` |
| Volume fraction | `0.4000000059604645` (`0.4`) |
| `k` | `0.8` |
| `epsilon` | `0.8` |
| Turbulent viscosity | `1.0` |

The volume-fraction URF is specifically `0.4`, not the `0.5` used by the later C1375/02e lineage.

### 9.3 Residual monitor criteria

Retain the audited monitor configuration:

| Equation | Absolute criterion |
|---|---:|
| Continuity | `1e-4` |
| x/y/z velocity | `1e-3` |
| Volume fraction | `1e-3` |
| `k` | `1e-3` |
| `epsilon` | `1e-3` |

Residuals are diagnostics. Phase fluxes remain essential for deciding whether the new two-outlet full-geometry state is sensible.

---

## 10. Initialization and run sequence

The baseline run is intentionally plain:

```text
load full-geometry mesh
→ apply 08b/audited-Purnanto carrier settings
→ configure split pure-phase inlet
→ configure retained steam outlet
→ configure new brine outlet
→ read back and compare every shared setting against 08b authority
→ Hybrid Initialize
→ NO liquid patch
→ solve steady
```

Do not:

- patch Y010/Y030;
- disable Volume Fraction or Slip Velocity equations;
- switch to Coupled;
- switch to first-order startup;
- enable pseudo-time;
- alter URFs;
- inherit C1375 solution controls;
- tune brine pressure during the baseline run.

If the baseline fails, save the failure evidence and define a separate child setup for the next numerical change.

---

## 11. Required preflight parity check

Before iteration 1, produce a machine-readable comparison with three columns:

```text
08b / audited-Purnanto authority
Setup-03 requested value
Setup-03 Fluent readback
```

The following must match or have an explicitly documented full-geometry reason for differing:

- solver/time model;
- operating conditions;
- phase mapping;
- material properties;
- RNG turbulence options;
- wall treatment;
- Mixture interaction settings;
- split inlet velocity, composition, turbulence;
- steam outlet pressure, backflow direction, turbulence and liquid VF;
- discretization schemes;
- URFs;
- residual criteria;
- pseudo-time state.

The brine outlet is the expected new branch and is checked against Section 8 rather than against 08b.

Any unexplained mismatch is a **preflight failure**, not a warning to ignore.

---

## 12. What to monitor during the steady solve

Primary diagnostic package:

| Quantity | Purpose |
|---|---|
| liquid inlet mass flux | confirm imposed liquid loading |
| vapour inlet mass flux | confirm imposed steam loading |
| liquid → brine outlet | main desired liquid route |
| liquid → steam outlet | liquid carryover indicator |
| vapour → steam outlet | main desired vapour route |
| vapour → brine outlet | wrong-outlet vapour indicator |
| total outlet fluxes | rapid routing sanity check |
| total liquid inventory in domain | identify continuing filling/draining |
| brine-outlet reverse-flow area / sign | diagnose pressure-outlet behaviour |
| brine-pipe-entry static/total pressure | inform later brine-pressure modelling |
| residuals | numerical diagnostic |
| turbulent-viscosity limiting count/region | compare against the known Purnanto warning state |

A first checkpoint may be taken at `500` iterations, but the case is not called steady merely because it reaches that count.

---

## 13. Baseline interpretation

### If it converges cleanly

Setup 03 becomes the full-geometry steady carrier anchor. Only after that should brine pressure, outlet resistance, retained-liquid behaviour, or transient operation be varied.

### If it runs but drains liquid rapidly

That is still useful evidence. It means the 08b carrier model itself is numerically viable on the full geometry but the new brine boundary does not represent the downstream hydraulic resistance needed to retain liquid.

The next experiment should then change **brine-outlet hydraulics**, not the entire solver setup.

### If it fails numerically

Do not immediately conclude that Mixture or transient physics is required. First identify whether failure originates from:

- full-geometry mesh/local quality;
- the newly opened brine pressure outlet;
- reverse flow;
- a parity mismatch relative to 08b;
- the full lower-vessel flow that the simplified Purnanto model excluded.

Any stabilization change belongs in a separately named child setup so the baseline remains intact.

---

## 14. What this setup deliberately does not claim

Setup 03 does not yet establish:

- correct real-plant brine-line pressure;
- correct retained liquid level;
- final separator efficiency;
- realistic inlet droplet distribution;
- DPM carryover efficiency;
- transient stability;
- validation against plant measurements.

Its role is narrower:

> **take the trusted 08b/Purnanto steady carrier setup, place it on the full separator with a real brine outlet, and determine what changes solely because the previously omitted lower liquid discharge is now part of the CFD domain.**
