# Setup 03A — 08b-Parity Full-Geometry Steady Mixture Baseline

> **Lifecycle:** `active — Stage 1 executed; Stage 2 numerical-stabilization screen planned`  
> **Execution status:** `Stage 1 completed to 1,000 steady iterations; not qualified for 03B`  
> **Primary objective:** reproduce the trusted `08b` / audited-Purnanto continuous-phase setup on the current full geometry, then determine whether that full-geometry steady field can be made numerically useful without changing the physical boundary condition.  
> **Baseline rule:** `08b carrier setup + full geometry + brine pressure outlet at 1.120 MPa`; do **not** use `FG-MIX-T01-S1-C1375` as the setup parent.  
> **Child setup:** [`03B`](03b-brine-pressure-continuation.md) continues only from a qualified 03A field while changing brine-outlet pressure.

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03A` |
| Current stage | `Stage 2 — steady numerical stabilization` |
| Setup authority | `08b-purnanto-parity-split-inlet-rebuild` |
| Underlying carrier authority | `00a-purnanto-setup-5000-live-audit` / audited Purnanto case-data |
| Historical full-geometry evidence | `02c`, `02e`, `FG-MIX-T01-S1-C1375` — evidence only, not setup authority |
| Geometry | current full separator geometry with explicit brine outlet |
| Inlet representation | pure-liquid outer split + pure-steam inner split |
| Time model | steady |
| Initialization | Hybrid Initialization in Stage 1 only; **no reinitialization in Stage 2** |
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

Stage 1 preserves the audited 08b numerical stack exactly. Stage 2 is a controlled numerical-stabilization screen prompted by the Stage-1 residual behaviour. Brine-pressure tuning still belongs to 03B and begins only from a numerically useful 03A field.

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

## 9. Stage 1 — canonical baseline construction and run

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

Do not use Y010/Y030 patching, equation staging, Coupled, first-order rescue, pseudo-time, altered URFs, or C1375 solution controls in Stage 1.

Before iteration 1, produce a machine-readable comparison:

```text
08b / audited-Purnanto authority
03A requested value
03A Fluent readback
```

Any unexplained mismatch is a preflight failure.

### 9.1 Stage-1 execution outcome — 1,000-iteration checkpoint

The reconstructed 03A case was run from Hybrid Initialization for exactly `1,000` native steady iterations with the canonical numerical stack unchanged.

The run completed without an FPE or AMG failure, but the endpoint is **not a converged or qualified steady solution**.

Final scaled residuals at iteration 1,000:

| Equation | Final residual |
|---|---:|
| Continuity | `1.6043e-01` |
| X velocity | `1.4715e-04` |
| Y velocity | `1.6833e-04` |
| Z velocity | `1.7100e-04` |
| `k` | `5.2127e-03` |
| `epsilon` | `2.2262e-01` |
| Liquid volume fraction | `6.5142e-03` |

The plotted histories show that `k` and particularly `epsilon` remain strongly oscillatory rather than approaching a clean residual plateau. Continuity also remains high. Reverse flow was reported at the pressure outlets, including `334` faces at the steam outlet, and turbulent-viscosity limiting occurred during the run.

The corrected full-domain endpoint flux diagnostic, including **both** pressure outlets, reported:

```text
Total inlet magnitude       = 198.4863 kg/s
Total outlet magnitude      = 164.4105 kg/s
Full-domain flux residual   = 34.0758 kg/s
Relative diagnostic residual = 17.17 %
```

The same endpoint gave provisional outlet-partition diagnostics:

```text
steam-outlet dryness estimate = 0.99678
liquid recovery estimate      = 0.99878
```

These phase-routing values are encouraging directionally but must **not** be treated as qualified separator performance while the full-domain steady imbalance remains approximately `17.17 %` and the turbulence residuals are strongly unsettled.

Stage 1 therefore establishes:

> The 08b-parity full-geometry case can survive 1,000 steady iterations without catastrophic solver failure, but the canonical steady numerical stack has not produced a sufficiently settled field for 03B continuation.

---

## 10. Monitoring

Record throughout all 03A stages:

- liquid inlet mass flux;
- vapour inlet mass flux;
- liquid → brine outlet;
- liquid → steam outlet;
- vapour → steam outlet;
- vapour → brine outlet;
- total outlet fluxes;
- full-domain flux residual and relative residual;
- total liquid inventory in the domain;
- Y010 and Y030 liquid inventory as diagnostics only — **no patching**;
- steam- and brine-outlet reverse-flow sign / area where available;
- brine-pipe-entry static and total pressure;
- residual histories;
- turbulent-viscosity limiting count / region.

For Stage 2, retain comparable residual and physical-monitor histories from each branch. A final residual value alone is insufficient: the amplitude/envelope of the `k` and `epsilon` oscillations over the branch must also be compared with the Stage-1 parent.

---

## 11. Stage 2 — steady numerical-stabilization screen

### 11.1 Purpose

Stage 2 asks:

> Can the Stage-1 full-geometry field be brought toward a numerically useful steady state by changing only the steady solution strategy, while keeping the physical case and both outlet pressures fixed?

This is **not** a brine-pressure experiment. Keep:

```text
P_steam = 1.120 MPa gauge
P_brine = 1.120 MPa gauge
```

and preserve the geometry, materials, Mixture physics, phase definitions, inlet conditions, outlet boundary types/compositions, gravity and all other physical settings.

Stage 2 deliberately tests four stabilization approaches:

- `N1` — reduced turbulence under-relaxation;
- `N3` — first-order turbulence transport;
- `N4` — first-order momentum + turbulence startup;
- `N5` — standard-`k-epsilon` turbulence bootstrap followed by return to RNG `k-epsilon`.

`N2` is **not** part of this first Stage-2 screen.

### 11.2 Common parent and branch rule

Save the Stage-1 iteration-1,000 case/data pair as an immutable parent.

Every Stage-2 branch must start independently from this exact parent:

```text
03A Stage-1 iter1000
        ├── N1
        ├── N3
        ├── N4
        └── N5
```

Do **not** run these as a sequential `N1 → N3 → N4 → N5` rescue chain. Otherwise the effect of each method cannot be separated.

For every branch:

- load the same Stage-1 case/data endpoint;
- do **not** Hybrid Initialize;
- do **not** patch liquid;
- apply only the branch-specific numerical change;
- positively read back the changed setting;
- run an initial `300` additional steady iterations unless the case fails earlier;
- inspect the histories at approximately `100`-iteration intervals;
- if clearly improving at iteration 300, the branch may be extended toward `500` additional iterations before qualification testing;
- save branch-specific case/data, residual, flux, inventory and warning artifacts.

### 11.3 N1 — turbulence under-relaxation damping

Change only:

```text
k URF:       0.8 → 0.5
epsilon URF: 0.8 → 0.5
```

Keep the remaining Stage-1 numerical method unchanged, including:

```text
Pressure URF = 0.3
Momentum URF = 0.7
Volume-fraction URF = 0.4
SIMPLE
PRESTO!
Momentum = Second Order Upwind
Volume fraction = QUICK
k = Second Order Upwind
epsilon = Second Order Upwind
RNG k-epsilon
```

Primary question:

> Is the Stage-1 turbulence instability mainly an over-aggressive turbulence-equation update that can be damped without altering the discretization or turbulence model?

### 11.4 N3 — first-order turbulence transport

Return to the immutable Stage-1 parent and change only:

```text
k discretization:       Second Order Upwind → First Order Upwind
epsilon discretization: Second Order Upwind → First Order Upwind
```

Retain the original Stage-1 URFs, including:

```text
k URF = 0.8
epsilon URF = 0.8
```

Keep momentum `Second Order Upwind`, volume fraction `QUICK`, pressure `PRESTO!`, and the remaining Stage-1 settings unchanged.

Primary question:

> Can added numerical diffusion in the turbulence transport equations suppress the large `k`/`epsilon` oscillation while leaving momentum and phase-fraction discretization at the canonical 08b settings?

The first-order result is a stabilization field, not a final high-order CFD solution.

### 11.5 N4 — first-order momentum + turbulence startup

Return to the immutable Stage-1 parent and change:

```text
Momentum: Second Order Upwind → First Order Upwind
k:        Second Order Upwind → First Order Upwind
epsilon:  Second Order Upwind → First Order Upwind
```

Keep:

```text
Pressure = PRESTO!
Volume fraction = QUICK
Stage-1 URFs unchanged
RNG k-epsilon unchanged
```

Primary question:

> Does a broader first-order startup create a sufficiently smooth developed flow/turbulence field that can later sustain the canonical second-order discretization?

Again, a first-order endpoint is not itself the final scientific solution.

### 11.6 N5 — standard-k-epsilon bootstrap then return to RNG

Return to the immutable Stage-1 parent.

Temporarily replace the RNG `k-epsilon` turbulence model with **standard `k-epsilon`**, retaining Standard Wall Functions and all compatible physical/numerical settings. RNG-specific options that do not exist in the standard model must not be invented or silently approximated; record the exact model-state differences in the readback.

Use the standard-`k-epsilon` phase only as a numerical bootstrap:

```text
Stage-1 parent
→ standard k-epsilon
→ continue steady until the turbulence field becomes clearly more bounded
   or until 500 additional iterations show no useful improvement
→ save checkpoint
→ restore the canonical RNG k-epsilon model and its audited 08b options
→ continue without reinitialization
```

After restoring RNG `k-epsilon`, continue for an initial `300` iterations and determine whether the improved behaviour survives the return to the authoritative turbulence model.

Primary question:

> Can a more forgiving turbulence-field bootstrap provide an initial field from which the required RNG `k-epsilon` model can subsequently remain stable?

A solution that is stable only while standard `k-epsilon` remains active does **not** qualify as the canonical 03A result.

### 11.7 Stage-2 comparison criteria

For each branch compare against the Stage-1 iteration-1,000 parent:

1. **`k` and `epsilon` residual envelope** — are the oscillations becoming smaller/bounded rather than continuing to jump over a similar or increasing range?
2. **Continuity residual** — does it move materially below the Stage-1 `1.6043e-01` level?
3. **Liquid-volume-fraction residual** — does it become more bounded and trend downward?
4. **Full-domain flux residual** — does the relative imbalance move materially below `17.17 %`?
5. **Phase flux histories** — do liquid/vapour outlet flows become less erratic and approach plateaus?
6. **Liquid inventory histories** — is the domain filling/draining trend becoming interpretable rather than being masked by numerical instability?
7. **Reverse flow** — does the steam/brine reverse-flow area remain bounded or reduce?
8. **Turbulent-viscosity limiting** — does the limited-cell count/region reduce or at least remain localized and bounded?
9. **Failure state** — any FPE, unrecoverable AMG divergence or equivalent numerical breakdown is recorded explicitly.

The objective is not to select the branch with the smallest single final residual. The preferred stabilization branch is the one that produces the clearest overall movement toward a bounded steady field while preserving sensible phase routing and mass conservation.

### 11.8 Return-to-authority qualification

A successful Stage-2 stabilization branch must not automatically become the 03B parent while altered startup numerics remain active.

For `N1`, `N3`, or `N4`, once a branch is demonstrably more stable:

1. save the stabilized checkpoint;
2. restore the canonical Stage-1 / 08b numerical settings:

```text
Pressure URF = 0.3
Momentum URF = 0.7
k URF = 0.8
epsilon URF = 0.8
Momentum = Second Order Upwind
k = Second Order Upwind
epsilon = Second Order Upwind
Volume fraction = QUICK
RNG k-epsilon
```

3. continue **without reinitialization** for at least approximately `200–300` iterations;
4. determine whether the reduced residual oscillation, improved flux balance and bounded physical monitors survive the return.

For `N5`, this return-to-authority check is already built into the branch: the standard-`k-epsilon` bootstrap must be followed by restoration of RNG `k-epsilon` and its audited options.

Only a field that remains numerically useful after returning to the canonical authority is eligible to become the current `03B` parent under the existing continuation design.

If a branch is stable **only** with permanently altered URFs/discretization/model settings, record that as an important Stage-2 result but do not silently redefine 03B. Either create a separately named child using the altered numerical stack or explicitly revise the continuation setup.

---

## 12. 03A outcome and handoff to 03B

03A is successful as a parent when the solution is numerically stable enough to provide a meaningful developed field for continuation. Ideally the phase fluxes and liquid inventory have reached a plateau; if they are still changing strongly, do not disguise that by immediately changing pressure.

The current Stage-1 iteration-1,000 endpoint is **not yet qualified** because the turbulence residuals are strongly oscillatory, continuity remains high, and the full-domain flux residual is approximately `17.17 %`.

Stage 2 therefore precedes any brine-pressure continuation.

If one Stage-2 route creates a stable developed field and that improvement survives restoration of the canonical 08b/RNG/second-order settings, save an immutable qualified 03A case/data checkpoint and begin [`03B — brine-pressure continuation`](03b-brine-pressure-continuation.md) from that exact field without reinitialization.

If all four Stage-2 routes remain strongly oscillatory or fail when the authoritative settings are restored, do **not** use 03B as a numerical rescue. Record that the canonical full-geometry steady branch has not been established and decide separately whether to investigate outlet recirculation/domain placement, other steady numerics, or return to transient development.

03A does not establish final brine pressure, retained liquid level, separator efficiency, DPM performance, transient stability, or plant validation.