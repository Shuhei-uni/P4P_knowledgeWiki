# Setup 02e — Mixture Y010 Brine-Outlet Boundary Characterization

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02e` |
| Lifecycle | `active` |
| Role | coarse adaptive Mixture-model characterization of built-in Fluent brine-outlet formulations with fixed Y010 liquid initialization |
| Parent setup | [02c — Mixture brine-outlet pressure sensitivity, unprimed](02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md) |
| Execution parent | dedicated `02e-Y010` initialized parent rebuilt from `Full-geomV2-231kcells.msh.h5` |
| Controlled changes | brine-outlet formulation and that formulation's primary control parameter only |
| Fixed initialization | all fluid cells selected by the approved production-mesh Y010 region satisfying `y <= +0.10 m` patched as liquid |
| Stage 1 | three 500-iteration pilot cases per runnable outlet family |
| Stage 2 | up to four automatically generated cases per family, selected from the three-point liquid-balance response |
| Maximum planned runs | `28` = 12 Stage-1 pilots + up to 16 adaptive Stage-2 children |
| Evidence-use label | experimental / coarse screening only; no convergence, validation, optimum, or physical-correctness claim |
| Linked report | create after Stage 1 and update after Stage 2 |

---

## 1. Objective

Characterize how different built-in Fluent outlet formulations affect brine drainage, vapour leakage, lower-vessel liquid inventory, and local brine-pipe pressure in the existing steady Mixture-model separator when every case starts from the same initialized lower liquid inventory.

The experiment deliberately fixes the Y010 initialization so that the intended differences between children are limited to the brine-outlet formulation and its primary control parameter.

The principal question is:

> How does each Fluent outlet formulation respond over a coarse control-parameter range when applied to the same separator, same Y010 initial liquid inventory, same steam outlet, same inlet conditions, and same numerical model?

This setup does **not** attempt to select the physically correct outlet boundary in advance.

The campaign structure is:

```text
same production mesh
        ↓
same steady Mixture model
        ↓
same saved Y010 initialized parent
        ↓
3 pilot points / outlet family
        ↓
measure final-100-iteration phase flux behaviour
        ↓
classify the three-point liquid-balance response
        ↓
refine a crossing / extend a supported trend / densify a non-monotonic range
        ↓
up to 4 Stage-2 children / family
        ↓
plots + observations for user interpretation
```

The campaign is intentionally coarse and aggressive. Detailed refinement belongs to a later setup.

---

## 2. Lineage and scope

`02e` is an active child of `02c`.

`02c` established the unprimed Mixture brine-outlet pressure branch and produced the pressure-direction context that motivated testing positive brine backpressure. `02e` changes the scientific question: instead of screening only a pressure outlet with no initialized retained liquid, it fixes a common lower liquid inventory and characterizes several built-in outlet formulations.

The transient VOF branch remains separate under `02d`. Do not enable or inherit VOF behaviour in `02e`.

Y010 is an **initial-condition control**, not a claim that the true operating liquid level is `y = +0.10 m`.

---

## 3. Production mesh and frozen physical model

Use:

```text
Full-geomV2-231kcells.msh.h5
```

Observed production-mesh preflight:

```text
Total cells = 231,376
Fluid zones = 1 combined fluid cell zone
```

Preserve the following for every case.

| Category | Required state |
|---|---|
| Solver | pressure-based, steady |
| Multiphase | Mixture |
| Turbulence | RNG k-epsilon |
| Gravity | `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Energy | preserve current `02c` / production state |
| DPM | off |
| EWF | off |
| Liquid inlet | Velocity Inlet, `27.118 m/s` |
| Steam inlet | Velocity Inlet, `27.118 m/s` |
| Inlet reference / initial gauge pressure | `1.140 MPa` |
| Steam outlet | Pressure Outlet, `1.120 MPa` gauge |
| Steam-outlet liquid backflow VF | `0.0` |
| Numerical methods | preserve verified parent state |
| Materials | preserve current water-vapour / water-liquid pair |
| Liquid density | `881.77 kg/m³` |

Do not modify turbulence, discretization, relaxation factors, material properties, inlet conditions, or steam-outlet conditions between cases.

---

## 4. Dedicated Y010 execution parent

Before building any outlet-family child, create one reusable initialized Y010 parent from the exact production mesh.

### 4.1 Initialization sequence

Use:

```text
load/rebuild frozen Mixture production state
→ Hybrid Initialize
→ create approved Y010 register
→ patch phase-2 water-liquid volume fraction = 1.0
→ verify integrated inventory
→ save paired case/data execution parent
```

Approved Y010 region definition:

```text
x = [-2.067034, 1.066098] m
y = [-1.484584, 0.100000] m
z = [-1.469893, 2.000000] m
inside = True
```

Definition:

> Every fluid cell selected by the approved production-mesh bounding region satisfying `y <= +0.10 m`.

This intentionally includes lower-vessel cells and any brine-pipe fluid cells lying below the cutoff. It is not a semantic pipe-only or vessel-only region.

### 4.2 Frozen Y010 inventory

Observed preflight:

```text
Selected cells = 33,315
Geometric selected-cell volume = 4.829410214 m³
Actual post-patch liquid inventory = 4.790652590 m³
Initial liquid mass = 4224.253734 kg
```

The official initialization reference is therefore:

\[
\boxed{V_{l,0}=4.790652590\ \mathrm{m^3}}
\]

rather than the geometric register volume.

Every Stage-1 and Stage-2 case must begin from this same saved initialized parent.

Do not:

- initialize and patch each child independently with a slightly different procedure;
- seed one outlet case from another solved outlet case; or
- seed a Stage-2 case from a Stage-1 endpoint.

---

## 5. Outlet formulations in scope

Run four outlet families when the exact Fluent version/case state exposes them and their build/readback gate passes.

### 5.1 Pressure Outlet — `PO`

Primary parameter:

\[
P_{brine}
\]

### 5.2 Outlet Vent — `OV`

Use a constant flow-dependent loss coefficient with discharge pressure held fixed.

Preferred state:

```text
loss_coefficient.option = constant
function_of = normal-velocity
```

Primary parameter:

\[
K
\]

### 5.3 Mass-Flow Outlet — `MF`

Prescribed phase mass-flow outlet.

Primary parameter:

\[
\dot m_{l,target}
\]

The phase-1 vapour target remains:

\[
\dot m_{v,target}=0
\]

### 5.4 Exhaust Fan — `EF`

Diagnostic pressure-jump formulation.

Primary parameter:

\[
\Delta P_{fan}
\]

`EF` is included for behavioural characterization only. Do not interpret it as a physically preferred brine-pipe model.

### 5.5 Outflow exclusion

`Outflow` is excluded from the production matrix because it does not provide the downstream-pressure/resistance control needed for this experiment and can conflict with the frozen pressure-outlet architecture.

Record:

```text
capability = available if confirmed live
campaign status = excluded
reason = unsuitable control structure / incompatible frozen outlet architecture
```

Do not change the steam-outlet architecture solely to accommodate Outflow.

---

## 6. Fixed run budget

Every Stage-1 and Stage-2 child receives:

\[
\boxed{500\ \text{steady iterations}}
\]

This is a coarse behaviour screen, **not** a convergence qualification.

Ensure Fluent does not automatically terminate a case early merely because residual convergence criteria are satisfied. Comparable cases should attempt the full 500-iteration budget.

If a case encounters a hard numerical failure before iteration 500:

1. save the last valid state if possible;
2. preserve transcript/log evidence;
3. mark the case `RUN-FAILED`;
4. do not tune relaxation factors or solver schemes to rescue that one case; and
5. continue independent families where possible.

---

## 7. Common monitor package

Create the monitor package before running children and reuse exactly the same definitions throughout the campaign.

### 7.1 Phase mass flows

Record phase mass flow for:

**Liquid**

- liquid inlet;
- brine outlet;
- steam outlet.

**Vapour**

- steam inlet;
- brine outlet;
- steam outlet.

Store both:

- Fluent-native signed value; and
- outward-positive converted value.

Define outward-positive:

\[
\dot m_{l,b}
\]

as liquid flow through the brine outlet and:

\[
\dot m_{v,b}
\]

as vapour flow through the brine outlet.

### 7.2 Y010 liquid inventory

Monitor:

\[
V_{l,Y010}=\int_{Y010}\alpha_l\,dV
\]

This measures how much liquid remains inside the originally initialized Y010 region.

### 7.3 Larger lower-region inventory

Create a monitoring-only region:

\[
y\le+0.30\ \mathrm{m}
\]

named:

```text
lower-monitor-y030
```

Monitor:

\[
V_{l,Y030}=\int_{y\le0.30}\alpha_l\,dV
\]

Y030 is **not patched** in this setup. It is a monitoring region only, intended to distinguish liquid leaving the lower vessel from liquid moving slightly above the original Y010 cutoff.

### 7.4 Total liquid inventory

Monitor:

\[
V_{l,total}=\int_V\alpha_l\,dV
\]

### 7.5 Brine-pipe-entry pressure

Preferred diagnostic location:

```text
brine-pipe-entry-section
```

an internal cross-sectional surface slightly inside the brine pipe from the lower-vessel/pipe junction.

If created reproducibly, record:

- area-weighted average static pressure;
- minimum static pressure;
- maximum static pressure.

A nearby cell region may also be used for volume-averaged static pressure.

**This is not a campaign gate.** If the surface cannot be created robustly through gRPC/PyFluent without guessing geometry, record the monitor as unavailable and continue the experiment. Do not invent the section location.

### 7.6 Outlet behaviour

Where available, record:

- area-averaged normal velocity at the brine outlet;
- mixture density at the brine outlet;
- reverse-flow area fraction;
- total brine mass flow.

For Outlet Vent, retain the quantities needed to interpret the resistance response.

### 7.7 Residuals

Store all residual histories and plot them for each case.

Do not use a terminal residual threshold as a Stage-2 gate and do not replace residual histories with a large terminal-number table.

---

## 8. Stage 1 — three-point pilot characterization

A single baseline cannot establish the response direction of an outlet control. Therefore every runnable family receives three independent pilot points from the same saved Y010 parent.

The middle point is the nominal reference; it is not automatically preferred.

### 8.1 Pressure Outlet pilots

Keep the steam outlet fixed at `1.120 MPa` gauge.

| Case | Brine pressure |
|---|---:|
| `02e-PO-P1` | `1.160 MPa` gauge |
| `02e-PO-P2` | `1.200 MPa` gauge |
| `02e-PO-P3` | `1.240 MPa` gauge |

### 8.2 Outlet Vent pilots

Keep:

\[
P_{discharge}=1.200\ \mathrm{MPa\ gauge}
\]

and vary only constant `K`.

| Case | `K` |
|---|---:|
| `02e-OV-P1` | `0` |
| `02e-OV-P2` | `10` |
| `02e-OV-P3` | `100` |

### 8.3 Mass-Flow Outlet pilots

Define:

\[
\dot m_{l,ref}=116.847\ \mathrm{kg/s}
\]

and keep:

\[
\dot m_{v,target}=0
\]

for every `MF` case.

| Case | Liquid target |
|---|---:|
| `02e-MF-P1` | `0.5 × ref = 58.4235 kg/s` |
| `02e-MF-P2` | `1.0 × ref = 116.847 kg/s` |
| `02e-MF-P3` | `2.0 × ref = 233.694 kg/s` |

### 8.4 Exhaust Fan pilots

Keep discharge pressure at `1.200 MPa` gauge and use Stage 1 to establish Fluent's effective pressure-jump response direction.

| Case | Pressure jump |
|---|---:|
| `02e-EF-P1` | `-50 kPa` |
| `02e-EF-P2` | `0 kPa` |
| `02e-EF-P3` | `+50 kPa` |

The pressure-jump signs are Fluent-native inputs. Do not attach a physical interpretation to the sign before observing the response.

---

## 9. Stage-2 data-quality gate

Stage 2 is allowed only when the family has a complete and usable three-point pilot set.

For a family to enter automatic Stage 2:

1. all three requested Stage-1 control values must pass build/readback;
2. all three cases must provide usable monitor histories through their last valid iteration;
3. final-100-iteration phase-flux averages must exist for all three cases;
4. branching values must be finite; and
5. the outward-positive sign convention must be applied consistently.

There is **no** residual threshold, liquid-level threshold, vapour-leakage threshold, or automatic physical-success gate.

If one or more pilot cases are unusable, record:

```text
STAGE2_NOT_GENERATED
reason = incomplete three-point pilot set
```

Do not infer a full response direction from only one or two points.

---

## 10. Branching quantities

Use arithmetic means over iterations `401–500` for a complete run. If a run fails before 500, it is not eligible for the normal three-point Stage-2 gate.

Define the outward-positive liquid balance:

\[
\boxed{
L=\bar{\dot m}_{l,in}-\bar{\dot m}_{l,brine}-\bar{\dot m}_{l,steam}
}
\]

Interpretation for **branch navigation only**:

- `L > 0`: measured liquid outlets remove less liquid than enters; fluxes imply liquid accumulation.
- `L < 0`: measured liquid outlets remove more liquid than enters; fluxes imply liquid depletion.
- `L = 0`: measured liquid inlet and outlets balance at the stored numerical precision.

The previous total-brine quantity

\[
B=\bar{\dot m}_{l,b}+\bar{\dot m}_{v,b}
\]

must **not** be used to select Stage 2. Liquid outflow and vapour flow are physically different behaviours and can cancel in `B`.

Also calculate, for reporting only:

\[
R_{v,b}=\frac{\bar{\dot m}_{v,brine}}{\bar{\dot m}_{v,in}}
\]

and:

\[
R_{l,s}=\frac{\bar{\dot m}_{l,steam}}{\bar{\dot m}_{l,in}}
\]

These describe vapour leakage to the brine outlet and liquid carryover to the steam outlet. They are **not** Stage-2 branch criteria.

Do not compare raw vapour kg/s directly with raw liquid kg/s to classify a case.

---

## 11. Generic automatic Stage-2 rule

For each family, sort the Stage-1 controls as:

\[
x_1<x_2<x_3
\]

with corresponding liquid balances:

\[
L_1,L_2,L_3.
\]

Use the stored full-precision values. Do not invent an arbitrary numerical tolerance solely to force a branch.

### 11.1 Exactly one adjacent sign crossing

If exactly one adjacent pair satisfies:

\[
L_iL_{i+1}<0,
\]

then the pilot sweep has bracketed a liquid-balance sign change.

Do **not** extrapolate.

Generate four equally spaced interior control values in that interval:

\[
x_j=x_{low}+\frac{j}{5}(x_{high}-x_{low}),\qquad j=1,2,3,4.
\]

A sign crossing is an information-rich region; it is **not** automatically an optimum or physically correct operating point.

### 11.2 Two sign crossings or non-monotonic response

If both pilot intervals contain sign changes, or the response reverses direction such that extrapolation is not justified, classify the family as `NON_MONOTONIC`.

Do not extrapolate.

Generate two points inside each pilot interval at one-third and two-thirds of the gap:

\[
x_{1a}=x_1+\frac13(x_2-x_1),\quad
x_{1b}=x_1+\frac23(x_2-x_1)
\]

\[
x_{2a}=x_2+\frac13(x_3-x_2),\quad
x_{2b}=x_2+\frac23(x_3-x_2).
\]

This creates four Stage-2 cases that densify the observed range rather than guessing beyond it.

### 11.3 No crossing — supported endpoint trend

If there is no sign crossing, compare:

\[
|L_1|,|L_2|,|L_3|.
\]

- If `|L3|` is the unique minimum and the high-side response is moving toward zero, use the family's predefined **high-side extension bank**.
- If `|L1|` is the unique minimum and the low-side response is moving toward zero, use the family's predefined **low-side extension bank**, where that direction is physically/definitionally available.
- If `|L2|` is the minimum, the sequence reverses trend, or the evidence otherwise does not support endpoint extrapolation, classify as `NON_MONOTONIC` and use Section 11.2.

If values tie at stored precision, prefer densification rather than extrapolation.

### 11.4 Exact zero at a pilot

If a pilot has `L = 0` exactly at stored precision, do not declare success.

- If the zero is the middle pilot, use Section 11.2 to densify both adjacent intervals.
- If the zero is an endpoint, generate four interior points in the adjacent pilot interval using the one-fifth spacing rule from Section 11.1.

The purpose is to characterize sensitivity around the observed zero rather than rank the case.

---

## 12. Family-specific Stage-2 extension banks

The generic rules above decide **whether to refine, densify, extend high, or extend low**. Only an endpoint-supported extrapolation uses the following preset banks.

### 12.1 Pressure Outlet

Stage-1 controls:

```text
1.160, 1.200, 1.240 MPa
```

High-side extension:

```text
1.280 MPa
1.320 MPa
1.360 MPa
1.400 MPa
```

Low-side extension:

```text
1.120 MPa
1.130 MPa
1.140 MPa
1.150 MPa
```

Do not automatically go below the frozen `1.120 MPa` steam-outlet pressure in this campaign.

Important sign logic:

> If the observed pressure trend shows that increasing `P_brine` moves `L` toward zero, Stage 2 explores **higher** backpressure. In particular, `L < 0` means the measured liquid outlets are removing more liquid than enters; that is not a reason to reduce brine pressure automatically.

### 12.2 Outlet Vent

Stage-1 controls:

```text
K = 0, 10, 100
```

High-side extension:

```text
K = 250
K = 500
K = 1000
K = 2000
```

There is no negative-resistance low-side extension.

If `K = 0` is the supported lower-bound endpoint closest to `L = 0` and increasing `K` moves the response away from zero, do not invent negative `K` and do not spend four runs increasing resistance anyway. Record:

```text
STAGE2_NOT_GENERATED
reason = useful direction lies below physical K lower bound
```

The Stage-2 count is therefore **up to** four cases per family rather than an unconditional four.

### 12.3 Mass-Flow Outlet

Use multiplier `r` relative to:

\[
\dot m_{l,ref}=116.847\ \mathrm{kg/s}.
\]

Stage-1 controls:

```text
r = 0.5, 1.0, 2.0
```

High-side extension:

```text
r = 2.5
r = 3.0
r = 4.0
r = 5.0
```

Low-side extension:

```text
r = 0.1
r = 0.2
r = 0.3
r = 0.4
```

The vapour target remains `0 kg/s` for every Mass-Flow Outlet child.

### 12.4 Exhaust Fan

Stage-1 controls:

```text
-50 kPa, 0 kPa, +50 kPa
```

Positive-side extension:

```text
+100 kPa
+150 kPa
+200 kPa
+250 kPa
```

Negative-side extension:

```text
-100 kPa
-150 kPa
-200 kPa
-250 kPa
```

The three pilots establish the response direction. Do not assume in advance that positive or negative jump is the physically restrictive direction.

---

## 13. Inventory slopes are supporting evidence, not branch gates

For each case, estimate the final-100-iteration trend of:

\[
V_{l,Y010},\qquad V_{l,Y030},\qquad V_{l,total}.
\]

These trends should be used as a consistency check on the flux story.

For example:

```text
L > 0
+
lower-region liquid inventory increasing
```

is mutually consistent with liquid accumulation, while:

```text
L < 0
+
lower-region liquid inventory falling
```

is consistent with liquid depletion.

Do **not** create another branching tree from inventory slope. Flux chooses the Stage-2 control values; inventory shows what those fluxes did to the initialized liquid.

If flux and inventory trends strongly disagree, flag the case for user interpretation rather than automatically changing the branching rule.

---

## 14. Automatic Stage-2 execution

After all available Stage-1 pilots finish:

```text
read Stage-1 monitor histories
→ calculate final-100-iteration averages
→ apply the Stage-2 data-quality gate
→ calculate L1, L2, L3
→ classify each valid family:
      CROSSING
      HIGH_EXTENSION
      LOW_EXTENSION
      NON_MONOTONIC
      NO_USEFUL_EXTENSION
→ generate up to 4 Stage-2 controls from Sections 11–12
→ write generated matrix and classification to manifest
→ build every child independently from frozen Y010 parent
→ run each child for 500 iterations
→ save endpoint case/data and monitor histories
```

No user approval is required between valid Stage 1 and Stage 2.

The agent must record **why** each branch fired.

Example:

```text
Outlet family: PO
Stage-1 controls: 1.160, 1.200, 1.240 MPa
L1 = ...
L2 = ...
L3 = ...
Classification = CROSSING between P2 and P3
Generated controls = four interior one-fifth points
```

Do not invent values outside the rules in this setup.

---

## 15. Build and readback procedure

For every child:

1. reload the exact saved Y010 execution parent;
2. verify Mixture, RNG k-epsilon, gravity, inlet types/velocities, steam pressure, materials, DPM off, EWF off, and preserved numerical methods;
3. convert only `brineoutlet` / `brine-outlet` to the intended outlet type using the verified live zone name;
4. apply only the case-specific primary parameter;
5. apply/read back a liquid-dominant brine backflow state where that boundary formulation exposes a relevant phase backflow control;
6. verify no unintended inlet, steam-outlet, model, material, or numerical changes;
7. save a uniquely named pre-run child;
8. run 500 iterations;
9. save paired endpoint case/data;
10. export monitor histories; and
11. reload the unchanged Y010 parent before building the next child.

Never seed one Stage-2 child from another solution.

If a requested outlet formulation is unavailable or cannot pass readback in the exact Fluent version/state, mark that family `BUILD-UNAVAILABLE` and continue other independent families. Do not improvise a different boundary formulation under the same case ID.

---

## 16. Artifact naming

Recommended Stage-1 patterns:

```text
02e-PO-P1-y010-p1160
02e-PO-P2-y010-p1200
02e-PO-P3-y010-p1240

02e-OV-P1-y010-p1200-k0
02e-OV-P2-y010-p1200-k10
02e-OV-P3-y010-p1200-k100

02e-MF-P1-y010-liquid58p4235-vapour0
02e-MF-P2-y010-liquid116p847-vapour0
02e-MF-P3-y010-liquid233p694-vapour0

02e-EF-P1-y010-p1200-jumpm50kpa
02e-EF-P2-y010-p1200-jump0
02e-EF-P3-y010-p1200-jumpp50kpa
```

Stage-2 patterns:

```text
02e-PO-S2-1-...
02e-OV-S2-1-...
02e-MF-S2-1-...
02e-EF-S2-1-...
```

Every artifact name must include the actual generated control value.

---

## 17. Required visual outputs

For every run create consistent plots of:

1. Y010 liquid inventory vs iteration;
2. Y030 lower-region liquid inventory vs iteration;
3. total liquid inventory vs iteration;
4. liquid brine-outlet mass flow vs iteration;
5. vapour brine-outlet mass flow vs iteration;
6. steam-outlet phase flows vs iteration;
7. pipe-entry average pressure vs iteration, when available; and
8. residual histories vs iteration.

Also save consistent iteration-500 field images where the case reaches iteration 500:

- lower-vessel liquid volume fraction;
- brine-pipe liquid volume fraction;
- lower-vessel static pressure;
- brine-pipe velocity; and
- one full-vessel liquid-volume-fraction view.

Do not replace plots with endpoint number dumps.

---

## 18. Reporting

After Stage 1, create an intermediate pilot summary used by the Stage-2 generator.

After Stage 2, create/update the comparison report.

Minimum final comparison fields:

| Case | Outlet family | Control value | `L` | Mean liquid → brine | Vapour → brine / vapour inlet | Liquid → steam / liquid inlet | Y010 trend | Y030 trend | Total-liquid trend | Pipe-entry pressure behaviour | Reverse flow observed? |
|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|

Use final-100-iteration means for the mass-flow quantities.

For each outlet family, also report:

- the three Stage-1 pilot values;
- `L1`, `L2`, `L3`;
- the Stage-2 classification;
- the four generated Stage-2 values, or the reason Stage 2 was not generated.

Do not rank cases automatically.

Do not label a case:

- correct;
- optimal;
- realistic;
- validated;
- converged; or
- best.

Report what happened and leave physical selection to the user.

---

## 19. Interpretation rule

This is an **experimental characterization campaign**.

There are deliberately:

- no numerical success thresholds;
- no required terminal residual values;
- no automatic "pool maintained" criterion;
- no automatic final outlet-family selection; and
- no assumption that `L = 0` is sufficient evidence of a physically correct separator state.

The agent may describe observations such as:

```text
liquid inventory increased
liquid inventory decreased
vapour brine leakage increased
liquid carryover to steam outlet increased
reverse flow appeared
pressure oscillated
liquid outlet flux exceeded liquid inlet flux
```

but should leave physical interpretation and next-stage selection to the user.

Residuals are contextual numerical evidence, not the primary adaptive variable.

---

## 20. What this setup is allowed to conclude

`02e` may establish:

- how each tested Fluent outlet formulation responds under a common initialized Mixture state;
- whether pressure, resistance, prescribed liquid mass flow, or pressure jump produces a strong directional response;
- whether the liquid-balance response contains a sign crossing within the tested range;
- whether the response is monotonic enough to justify coarse extrapolation;
- which parameter ranges produce substantially different flux/inventory behaviour;
- which outlet families are numerically unavailable or unusable in the frozen Fluent architecture; and
- where a later detailed sensitivity should concentrate.

It may **not** establish:

- the real geothermal brine-system downstream pressure;
- the correct hydraulic loss coefficient;
- the true separator operating liquid level;
- validation of the Mixture model;
- a converged production separator operating point; or
- the physically preferred outlet family without subsequent user interpretation and later validation work.

The central design rule of this setup is therefore:

> **Three pilot points establish the response. Flux-based liquid balance chooses where to probe next. Vapour leakage and liquid inventory explain the consequence. The user decides what the behaviour means physically.**
