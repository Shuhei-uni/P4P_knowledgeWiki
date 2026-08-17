# Setup 03 — Unpatched Steady Mixture Baseline Qualification

> **Lifecycle:** `draft — substantially specified`  
> **Execution status:** `DO NOT RUN until final readback/preflight is complete`  
> **Primary objective:** obtain a reproducible steady full-geometry Mixture solution from Hybrid Initialization with **no liquid patching** and no staged equation activation.  
> **Interpretation:** numerical/physical baseline qualification; not yet a separator-efficiency validation.

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03` |
| Parent evidence | `02c` unpatched pressure-sensitivity + `02e` boundary-characterization results |
| Geometric reference lineage | Purnanto, Zarrouk & Cater (2013), Spiral-Inlet Design, Table 3 / Figure 8 |
| Inlet representation | split rectangular spiral inlet face with two pure-phase velocity-inlet zones |
| Initialization | Hybrid Initialization only; **no Y010/Y030/other phase patch** |
| Brine boundary family | Pressure Outlet |
| Baseline brine pressure | `1.1375 MPa gauge` |
| Steam outlet pressure | `1.120 MPa gauge` |
| Inlet reference / initial gauge pressure | `1.140 MPa` |
| Baseline inlet speed | `27.118 m/s` on both split inlet zones |
| Primary decision question | can the explicitly specified full Mixture model settle to a steady solution without an artificial initial liquid pool? |
| DPM | off |
| EWF | off |

---

## 1. Purpose and change from the previous draft

The purpose of Setup 03 is now deliberately simple:

> **Build the best explicitly specified steady Mixture representation of the current full-geometry separator, initialize it normally, do not patch liquid anywhere, and determine whether a genuine steady solution exists.**

The earlier draft proposed using a Y010 liquid patch followed by staged activation of Volume Fraction and Slip Velocity equations. That is no longer the baseline experiment.

For this setup:

- no Y010 patch is applied;
- no liquid level is prescribed inside the vessel;
- no Mixture equation is temporarily disabled;
- no first-order startup stage is used in the baseline;
- no Coupled pressure-velocity method is introduced in the baseline;
- the solver starts with the complete intended Mixture model active;
- the numerical method follows the simple Purnanto-style steady formulation as closely as practical on the current full geometry.

If this baseline fails, more intrusive numerical stabilization methods can be tested later as controlled fallback experiments. They are not part of the baseline definition.

---

## 2. Geometry context

### 2.1 Spiral-Inlet reference design

The current full-geometry separator is geometrically descended from the **Spiral-Inlet Design** described by Purnanto, Zarrouk & Cater (2013). Table 3 gives the following reference dimensions:

| Parameter | Spiral-Inlet reference |
|---|---:|
| Vessel diameter `D` | `2.134 m` |
| Inlet dimension `De` | `0.724 m` |
| Steam-tube diameter `Db` | `0.508 m` |
| `alpha` | `0.200 m` |
| `beta` | `2.320 m` |
| `Z` | `4.195 m` |
| `LT` | `4.929 m` |
| `LB` | `3.579 m` |
| Two-phase inlet area `Ao` | `0.5242 m²` |

The paper describes a rectangular 90-degree spiral inlet intended to provide a smooth transition from approximately linear inlet motion into vessel rotation. The spiral geometry is therefore important to the development of the cyclone velocity field.

These values are **design-lineage context**, not permission to silently overwrite the current production CAD/mesh. The production mesh remains the execution geometry. Before execution, the agent must report the actual mesh face areas and key geometric dimensions that can be measured directly and identify any material differences from the reference design.

### 2.2 Split-inlet representation used in this project

Unlike the Purnanto paper's mist-form two-phase inlet, the present carrier-flow model uses a **split inlet face** consisting of two independent pure-phase velocity-inlet zones:

- `liquidinlet`: pure water-liquid;
- `steaminlet`: pure water-vapour.

Both inlet zones use the same normal velocity:

\[
U_{in}=27.118\ \mathrm{m/s}.
\]

Using the Purnanto 1600-kJ/kg reference phase flow rates and the selected constant densities,

\[
\dot m_l=116.92\ \mathrm{kg/s},\qquad
\dot m_v=80.69\ \mathrm{kg/s},
\]

implies the required split areas

\[
A_l=\frac{116.92}{881.77\times27.118}\approx0.004890\ \mathrm{m^2},
\]

\[
A_v=\frac{80.69}{5.73\times27.118}\approx0.519287\ \mathrm{m^2}.
\]

Therefore

\[
A_l+A_v\approx0.524177\ \mathrm{m^2},
\]

which is effectively the `0.5242 m²` Spiral-Inlet area reported in Table 3.

This is an important modelling statement: the split is not intended to represent two separate upstream pipes. It is an **idealized phase segregation across the single spiral inlet cross-section** while preserving the reference total area, phase mass flows, and common inlet velocity.

### 2.3 Consequence of the idealized split

The split inlet deliberately removes upstream phase mixing from this baseline. It therefore represents a more perfectly pre-separated inlet than a real geothermal two-phase feed.

Expected consequence:

- carrier-phase separation may be cleaner than in reality;
- later separator-efficiency predictions should therefore not be interpreted as final real-plant efficiency;
- future DPM work will reintroduce dispersed droplets/mist into the steam-side inlet when the continuous solution is sufficiently trustworthy.

Setup 03 is concerned with obtaining and understanding the steady continuous-phase solution first.

---

## 3. Fluid properties and thermodynamic assumptions

Use the Purnanto 1600-kJ/kg, `11.2 bara` reference properties unless a later project-level thermodynamic revision explicitly supersedes them.

| Property | Water vapour | Water liquid |
|---|---:|---:|
| Density | `5.73 kg/m³` | `881.77 kg/m³` |
| Dynamic viscosity | `15.188e-6 Pa·s` | `145.96e-6 Pa·s` |

Required assumptions:

- incompressible phase properties;
- constant density;
- constant viscosity;
- isothermal separation;
- Energy equation **off**;
- no flashing / evaporation / condensation;
- gravity `[0, -9.81, 0] m/s²`;
- operating pressure `0 Pa`;
- all entered pressure values are therefore gauge values relative to zero operating pressure and numerically correspond to the absolute-pressure level used by the project convention.

The Purnanto paper lists a surface tension of `0.0411 N/m` as a fluid property, but **surface-tension force modelling is intentionally disabled in Setup 03**.

---

## 4. Solver and multiphase model

### 4.1 General solver

| Setting | Required state |
|---|---|
| Solver type | Pressure-Based |
| Time | Steady |
| Velocity formulation | Absolute |
| Gravity | enabled, `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Energy | off |

### 4.2 Mixture model

| Setting | Required state |
|---|---|
| Multiphase model | Mixture |
| Number of phases | `2` |
| Primary phase | water-vapour |
| Secondary phase | water-liquid |
| Secondary-phase diameter | **constant `1.0e-5 m`** |
| Slip velocity | enabled |
| Slip formulation | **Manninen et al.** |
| Flow-regime modelling | off |
| Surface-tension force modelling | off |
| Surface-tension coefficient | not used / unset |
| Mass transfer | none |

The `1e-5 m` secondary-phase diameter is not an arbitrary Fluent default in this setup. It is explicitly adopted because the Purnanto reference study defines the dispersed liquid phase with a uniform average diameter of `10^-5 m` for the Mixture carrier-flow model.

This value should be revisited in a later model-form sensitivity if the Mixture model is used to make quantitative claims about phase slip or bulk-liquid behaviour. It is nevertheless the most defensible current baseline value because it has direct literature lineage.

---

## 5. Turbulence model

Use:

```text
RNG k-epsilon
Near-wall treatment = Standard Wall Functions
```

The Purnanto study selected RNG `k-epsilon` as a computationally economical first model for the highly turbulent swirling separator flow.

### 5.1 RNG options

Use the **basic/default RNG configuration**, explicitly avoiding additional low-Re or strongly-swirl tuning for the baseline:

| RNG option | Required state |
|---|---|
| Differential Viscosity Model | **off** |
| Swirl Dominated Flow option | **off** |
| Default RNG swirl modification | retained automatically |
| Default mild/moderate swirl constant | Fluent default (`0.07`) |
| Curvature correction | off |
| Kato-Launder production | off |
| Production limiter | off unless Fluent requires its model default; read back and record |
| Turbulence damping | off |

Important distinction: disabling **Swirl Dominated Flow** does not remove RNG's normal swirl response. Fluent applies the RNG swirl modification by default in 3-D flows; the extra option is used to change the model for strongly swirl-dominated flow. Setup 03 does not add that extra tuning.

### 5.2 Wall treatment

All stationary solid walls:

- no slip;
- Standard Wall Functions;
- roughness height `0 m`;
- smooth-wall assumption;
- if Fluent exposes a roughness constant despite zero roughness height, retain/read back its default but it has no physical effect while the roughness height is zero.

---

## 6. Turbulence boundary specification

Use **Intensity and Viscosity Ratio** at every flow boundary so the setup is consistent and explicit.

The `08b`/split-inlet archive is useful for the turbulence **intensity** values, but it contains a known historical boundary-setting mismatch: `0.72061` appears in a live case as a viscosity ratio even though the reconstruction audit identifies it as the intended hydraulic diameter in metres. **Do not use `0.72061` as a turbulent viscosity ratio.**

### 6.1 Baseline turbulence values

| Boundary | Specification | Intensity | Viscosity ratio | Basis |
|---|---|---:|---:|---|
| `liquidinlet` | Intensity + Viscosity Ratio | `2.11%` | `10` | retain 08b inlet intensity; moderate explicit internal-flow viscosity-ratio assumption |
| `steaminlet` | Intensity + Viscosity Ratio | `2.11%` | `10` | retain 08b inlet intensity; replace known 08b field mismatch with explicit value |
| `steamoutlet` backflow | Intensity + Viscosity Ratio | `2.1525%` | `10` | retain 08b steam-outlet backflow intensity; explicit moderate ratio |
| `brineoutlet` backflow | Intensity + Viscosity Ratio | `2.11%` | `10` | liquid-dominant reverse-flow assumption, aligned with liquid-inlet intensity |

The viscosity ratio `10` is a documented modelling assumption, not claimed measured data. It is selected because the project has no measured turbulence length scale or dissipation rate at these boundaries, the split inlet is itself an idealization rather than a developed upstream pipe, and a single moderate explicit value is preferable to inheriting inconsistent Fluent defaults.

If later experimental/upstream-pipe information becomes available, turbulence boundary values should be recalculated rather than tuned for convergence.

---

## 7. Boundary conditions

### 7.1 Liquid inlet — `liquidinlet`

| Field | Value |
|---|---|
| Type | Velocity Inlet |
| Velocity specification | Magnitude, Normal to Boundary |
| Reference frame | Absolute |
| Velocity magnitude | `27.118 m/s` |
| Initial gauge pressure | `1.140 MPa` |
| Liquid volume fraction | `1.0` |
| Vapour volume fraction | `0.0` |
| Turbulence | Intensity and Viscosity Ratio |
| Turbulent intensity | `2.11%` |
| Turbulent viscosity ratio | `10` |

Expected reference mass flow from the intended split area:

\[
\dot m_l\approx116.92\ \mathrm{kg/s}.
\]

The actual mesh-area-based mass flow must be reported before the run; do not silently force the reference mass flow if the actual split area differs.

### 7.2 Steam inlet — `steaminlet`

| Field | Value |
|---|---|
| Type | Velocity Inlet |
| Velocity specification | Magnitude, Normal to Boundary |
| Reference frame | Absolute |
| Velocity magnitude | `27.118 m/s` |
| Initial gauge pressure | `1.140 MPa` |
| Liquid volume fraction | `0.0` |
| Vapour volume fraction | `1.0` |
| Turbulence | Intensity and Viscosity Ratio |
| Turbulent intensity | `2.11%` |
| Turbulent viscosity ratio | `10` |

Expected reference mass flow:

\[
\dot m_v\approx80.69\ \mathrm{kg/s}.
\]

### 7.3 Steam outlet — `steamoutlet`

| Field | Value |
|---|---|
| Type | Pressure Outlet |
| Gauge pressure | `1.120 MPa` |
| Backflow direction | **Normal to Boundary** |
| Backflow pressure specification | **Total Pressure** |
| Backflow liquid volume fraction | `0.0` |
| Backflow vapour volume fraction | `1.0` |
| Backflow turbulence | Intensity and Viscosity Ratio |
| Backflow turbulent intensity | `2.1525%` |
| Backflow turbulent viscosity ratio | `10` |

### 7.4 Brine outlet — `brineoutlet`

Baseline:

\[
\boxed{P_{brine}=1.1375\ \mathrm{MPa\ gauge}}
\]

This pressure is selected from the earlier unpatched `02c` evidence because it produced the most promising phase-routing tendency in the unprimed pressure sweep. It is **not** claimed to be the physically correct downstream brine-system pressure.

| Field | Value |
|---|---|
| Type | Pressure Outlet |
| Gauge pressure | `1.1375 MPa` baseline |
| Backflow direction | **Normal to Boundary** |
| Backflow pressure specification | **Total Pressure** |
| Backflow liquid volume fraction | `1.0` |
| Backflow vapour volume fraction | `0.0` |
| Backflow turbulence | Intensity and Viscosity Ratio |
| Backflow turbulent intensity | `2.11%` |
| Backflow turbulent viscosity ratio | `10` |

The brine pressure remains a model parameter that may require later continuation once a steady baseline exists.

---

## 8. Numerical methods

Use a simple Purnanto-style steady formulation rather than introducing stabilization changes in the first run.

| Setting | Baseline |
|---|---|
| Pressure-velocity coupling | **SIMPLE** |
| Gradient | **Green-Gauss Node Based** |
| Pressure | **PRESTO!** |
| Momentum | **Second-Order Upwind** |
| Turbulent kinetic energy `k` | **Second-Order Upwind** |
| Turbulent dissipation `epsilon` | **Second-Order Upwind** |
| Volume fraction | **QUICK** |

The rationale is straightforward:

- SIMPLE is the method used in the reference study;
- PRESTO! is appropriate for strong rotation/swirl and is also used in the reference study;
- the reference study used second-order momentum/turbulence and QUICK for volume fraction;
- therefore the baseline does not need a special first-order rescue stage unless the direct solve proves numerically impossible.

### 8.1 Under-relaxation factors

Set explicitly rather than relying on version-dependent inheritance:

| Quantity | URF |
|---|---:|
| Pressure | `0.3` |
| Momentum | `0.7` |
| `k` | `0.8` |
| `epsilon` | `0.8` |
| Volume fraction / multiphase | `0.5` |
| Drift / slip | `0.1` |
| Density | `1.0` |
| Body force | `1.0` |
| Turbulent viscosity | `1.0` |

These are numerical controls, not physical calibration parameters. They are frozen for reproducibility during the first baseline attempt.

---

## 9. Initialization — explicitly no patch

The complete initialization sequence is:

```text
load production mesh
→ build/read back the complete Setup 03 specification
→ Hybrid Initialize
→ DO NOT patch liquid volume fraction
→ DO NOT create a Y010/Y030 initialization region
→ DO NOT seed a water pool
→ save the post-Hybrid pre-solve case/data checkpoint
→ begin the full steady Mixture solve
```

Y010 and Y030 may still be created later as **monitoring regions only** if useful, but they must not modify the phase field.

The initial field is whatever Fluent's Hybrid Initialization produces from the explicitly defined boundaries and model. The pre-solve phase inventory must be measured and recorded so that later changes can be interpreted.

---

## 10. Monitoring package

Residuals are necessary but are not the primary physical diagnostic.

### 10.1 Phase-specific fluxes — highest-priority diagnostic

Record every iteration where practical:

**Liquid**

- liquid through `liquidinlet`;
- liquid through `steaminlet`;
- liquid through `brineoutlet`;
- liquid through `steamoutlet`.

**Vapour**

- vapour through `liquidinlet`;
- vapour through `steaminlet`;
- vapour through `brineoutlet`;
- vapour through `steamoutlet`.

Store Fluent-native signed fluxes and an outward-positive interpretation table.

### 10.2 Overall mass/phase balance

Compute:

\[
B_l=\dot m_{l,in}-\dot m_{l,brine}-\dot m_{l,steam},
\]

\[
B_v=\dot m_{v,in}-\dot m_{v,brine}-\dot m_{v,steam}.
\]

For this split-inlet case, cross-phase inlet flux should be essentially zero by construction.

### 10.3 Liquid inventory

Even though there is no patch, monitor:

\[
V_{l,total}=\int_V\alpha_l\,dV.
\]

Also retain Y010/Y030 volume-integral monitors as lower-vessel diagnostics if they can be created without affecting initialization:

\[
V_{l,Y010},\qquad V_{l,Y030}.
\]

These are monitoring regions only.

### 10.4 Outlet diagnostics

At both outlets record where available:

- mixture mass flow;
- phase-specific mass flow;
- area-weighted static pressure;
- area-weighted total pressure;
- area-averaged normal velocity;
- reverse-flow area fraction;
- mixture density.

At the brine pipe entry record:

- area-weighted static pressure;
- minimum/maximum static pressure;
- phase volume fraction;
- normal/axial velocity where meaningful.

### 10.5 Residuals and numerical warnings

Record:

- continuity;
- x/y/z momentum;
- `k`;
- `epsilon`;
- volume fraction / multiphase residuals;
- turbulent-viscosity limiting warnings;
- reverse-flow warnings;
- AMG divergence;
- FPE or equivalent hard failure.

A solver FPE or equivalent unrecoverable error is classified as `RUN-FAILED`.

---

## 11. Baseline run plan

### Case `03-U-P1375`

`U` = unpatched.

```text
Hybrid Initialize
no patch
all Mixture equations active
Pbrine = 1.1375 MPa gauge
Psteam = 1.120 MPa gauge
SIMPLE
Green-Gauss Node Based
PRESTO!
Second-Order Upwind momentum/k/epsilon
QUICK volume fraction
```

### Execution budget

Run in checkpoints rather than assuming a single iteration count defines convergence:

```text
0 → 500 iterations
500 → 1000 if finite/stable
1000 → 2000 if still evolving but improving
2000 → 3000 only if there is credible movement toward a stationary solution
```

At each checkpoint save case/data and evaluate flux trends.

Do not stop automatically simply because Fluent's residual convergence criteria fire. Conversely, do not continue thousands of iterations through clearly divergent or physically runaway behaviour merely to reach a nominal budget.

---

## 12. Qualification criteria

A solution is not accepted merely because it survived the requested iteration count.

### 12.1 Numerical requirement

No:

- FPE;
- unrecoverable AMG divergence;
- NaN/Inf field;
- solver termination;
- persistent explosive residual growth.

### 12.2 Flux stationarity

Over the final `200`-iteration evaluation window:

- inlet and outlet phase fluxes should no longer show a strong monotonic drift;
- moving-window means should be approximately stationary;
- the liquid and vapour balances should be trending toward zero rather than systematically worsening.

Initial numerical qualification target:

\[
\frac{|B_l|}{\dot m_{l,in}}<5\%,\qquad
\frac{|B_v|}{\dot m_{v,in}}<5\%.
\]

A preferred later target is below `2%` once a steady branch exists.

### 12.3 Inventory stationarity

Total-domain liquid inventory must not show persistent filling or draining.

Practical initial target:

- less than approximately `1–2%` systematic change over the final `200` iterations;
- no large monotonic lower-vessel inventory trend.

### 12.4 Routing sanity check

The expected qualitative direction is:

- most liquid leaves through the brine outlet;
- most vapour leaves through the steam outlet;
- wrong-outlet phase fluxes remain finite and interpretable.

Poor separator routing does not automatically invalidate the mathematical existence of a steady state, but it must be reported clearly and prevents the case from being treated as a validated physical separator solution.

---

## 13. What happens if the direct baseline fails

Do **not** immediately perform another large pressure sweep and do **not** immediately patch a pool.

The fallback hierarchy is one change at a time:

1. **Numerical order fallback:** repeat the exact same physical case using first-order momentum/`k`/`epsilon`/volume-fraction startup, then promote back to the baseline schemes if a stable field is obtained.
2. **Pressure-velocity fallback:** test Coupled only after the SIMPLE case has provided clear failure evidence.
3. **Equation-staging fallback:** only then test temporarily disabling/re-enabling Volume Fraction or Slip Velocity.
4. **Pressure continuation:** only after one numerically steady unpatched baseline exists.
5. **Model-form change:** reconsider Mixture assumptions/diameter/VOF only after the controlled numerical fallbacks have been assessed.

Every fallback becomes its own named child experiment. Do not silently modify the baseline case until it runs.

---

## 14. Required preflight before removing `DO NOT RUN`

The agent must produce a machine-readable and human-readable readback confirming every item below.

### Geometry / zones

- production mesh filename and hash/size if available;
- cell count;
- boundary zone names and types;
- actual `liquidinlet` area;
- actual `steaminlet` area;
- total inlet area and comparison with `0.5242 m²`;
- steam-outlet area;
- brine-outlet area;
- key brine-pipe and inlet characteristic dimensions available from the mesh.

### Physics

- phase names and ordering;
- both material densities and viscosities;
- Mixture model active;
- phase-2 diameter exactly `1e-5 m`;
- Manninen slip formulation active;
- flow-regime modelling off;
- surface-tension force modelling off;
- Energy off;
- gravity and operating pressure exact.

### Turbulence

- RNG `k-epsilon`;
- Standard Wall Functions;
- Differential Viscosity Model off;
- Swirl Dominated Flow option off;
- boundary turbulence specification = Intensity and Viscosity Ratio on all four flow boundaries;
- exact values match Section 6.

### Boundaries

- both inlet velocities = `27.118 m/s` normal to boundary;
- pure-phase inlet volume fractions correct;
- inlet initial gauge pressure = `1.140 MPa`;
- steam outlet = `1.120 MPa`;
- brine outlet = `1.1375 MPa`;
- pressure-outlet backflow direction = Normal to Boundary;
- pressure-outlet backflow pressure specification = Total Pressure;
- steam backflow liquid VF = `0`;
- brine backflow liquid VF = `1`.

### Numerics

- SIMPLE;
- Green-Gauss Node Based;
- PRESTO!;
- second-order momentum/`k`/`epsilon`;
- QUICK volume fraction;
- URFs match Section 8.1;
- all intended Mixture equations active before iteration 1.

### Initialization

- Hybrid Initialization completed;
- no patch command issued;
- no Y010/Y030 initialization operation issued;
- pre-solve total liquid inventory reported;
- pre-solve case/data checkpoint written and reload verified.

If any item differs, stop and report the mismatch instead of silently substituting a Fluent default.

---

## 15. Source and interpretation notes

### Purnanto, Zarrouk & Cater (2013)

The paper provides the reference Spiral-Inlet geometry, 1600-kJ/kg phase properties/flows, RNG `k-epsilon` selection, `10^-5 m` liquid secondary-phase diameter, smooth-wall/isothermal/no-flashing assumptions, and SIMPLE/PRESTO!/second-order/QUICK numerical approach used as the modelling lineage for this setup.

### 08b / split-inlet archive

The archive supports the split pure-phase inlet construction and the approximately `2.11%` inlet turbulence intensity. It must **not** be copied blindly: the archive audit identifies a historical field mismatch in which an intended hydraulic diameter (`0.72061 m`) appeared in a live case as turbulent viscosity ratio `0.72061`.

### Earlier full-geometry runs

`02c` and `02e` are evidence about pressure sensitivity, routing and numerical failure boundaries. They do not define the new initialization. Setup 03 deliberately returns to an unpatched baseline and rebuilds the physical/numerical specification explicitly.

---

## 16. Summary of the experiment

```text
Purnanto Spiral-Inlet geometric/physical lineage
        +
current production full geometry
        +
split pure-liquid / pure-steam inlet face
        +
explicit constant properties
        +
Mixture, 10 µm secondary liquid, Manninen slip
        +
RNG k-epsilon, Standard Wall Functions
        +
explicit turbulence BCs
        +
pressure outlets with explicit backflow composition/direction
        +
SIMPLE + PRESTO! + second-order + QUICK
        +
Hybrid Initialization only
        +
NO LIQUID PATCH
        ↓
03-U-P1375
        ↓
phase flux + inventory + residual diagnostics
        ↓
Does a real steady branch exist?
```

The baseline should remain boring and explicit. If it fails, complexity is introduced only through separately identified fallback cases so that the cause of any improvement or failure remains interpretable.
