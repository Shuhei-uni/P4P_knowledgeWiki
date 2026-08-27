> **Legacy source:** Setups/compatibility-snapshots/02e-mixture-y010-brine-outlet-boundary-characterization.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Setup 02e — Mixture Y010 Brine-Outlet Boundary Characterization

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02e` |
| Lifecycle | `active` |
| Role | coarse Mixture-model characterization of built-in Fluent brine-outlet formulations with fixed Y010 liquid initialization, followed by a targeted four-case refinement |
| Parent setup | [02c — Mixture brine-outlet pressure sensitivity, unprimed](../full-geometry-02c-mixture-pressure-sensitivity/setup.md) |
| Execution parent | dedicated `02e-Y010` initialized parent rebuilt from `Full-geomV2-231kcells.msh.h5` |
| Controlled changes | brine-outlet formulation and that formulation's primary control parameter only |
| Fixed initialization | all fluid cells selected by the approved production-mesh Y010 region satisfying `y <= +0.10 m` patched as liquid |
| Stage 1 | 12 requested pilot cases: 3 per outlet family; complete |
| Stage 2 | fixed four-case targeted follow-up: 2 Pressure Outlet + 2 Outlet Vent cases |
| Maximum planned runs | `16` = 12 Stage-1 pilots + 4 targeted Stage-2 cases |
| Evidence-use label | experimental / coarse screening only; no convergence, validation, optimum, or physical-correctness claim |
| Linked Stage-1 report | [stage1-results-20260816.md](stage-01/results.md) |

---

## 1. Objective

Characterize how different built-in Fluent outlet formulations affect brine drainage, vapour leakage, lower-vessel liquid inventory, and local brine-pipe pressure in the existing steady Mixture-model separator when every case starts from the same initialized lower liquid inventory.

The experiment fixes the Y010 initialization so that intended differences between children are limited to the brine-outlet formulation and its primary control parameter.

The principal Stage-1 question was:

> How does each Fluent outlet formulation respond over a coarse control-parameter range when applied to the same separator, same Y010 initial liquid inventory, same steam outlet, same inlet conditions, and same numerical model?

Stage 1 is now complete. The original automatic adaptive Stage-2 plan has been retired because no outlet family produced three complete 500-iteration pilot histories. Instead, Stage 1 is used as a coarse screening result and Stage 2 is a **user-selected four-case targeted refinement** of the two families that produced the most useful evidence: Pressure Outlet (`PO`) and Outlet Vent (`OV`).

The revised campaign structure is:

```text
same production mesh
        ↓
same steady Mixture model
        ↓
same saved Y010 initialized parent
        ↓
Stage 1: 3 pilot points / outlet family
        ↓
record survivability + liquid inventory + phase flux behaviour
        ↓
user interpretation of Stage-1 evidence
        ↓
retain PO and OV for targeted refinement
        ↓
Stage 2: 2 PO cases + 2 OV cases
        ↓
compare against Stage-1 anchors and numerical-failure boundaries
        ↓
plots + observations for user interpretation
```

This remains a coarse experimental characterization. Stage 2 is not an optimisation and does not assert that either retained outlet family is physically correct.

---

## 2. Lineage and scope

`02e` is an active child of `02c`.

`02c` established the unprimed Mixture brine-outlet pressure branch and produced the pressure-direction context that motivated testing positive brine backpressure. `02e` changes the scientific question: instead of screening only a pressure outlet with no initialized retained liquid, it fixes a common lower liquid inventory and characterizes several built-in outlet formulations.

The transient VOF branch remains separate under `02d`. Do not enable or inherit VOF behaviour in `02e`.

Y010 is an **initial-condition control**, not a claim that the true operating liquid level is `y = +0.10 m`.

Stage 2 remains within the same steady Mixture-model branch and does not change turbulence, discretization, material properties, inlet conditions, or steam-outlet conditions.

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

Do not modify turbulence, discretization, relaxation factors, material properties, inlet conditions, steam-outlet conditions, or mesh between Stage-2 cases.

---

## 4. Dedicated Y010 execution parent

Every Stage-1 and Stage-2 child must start from the same saved initialized Y010 parent.

### 4.1 Initialization sequence

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

The official initialization reference is:

\[
\boxed{V_{l,0}=4.790652590\ \mathrm{m^3}}
\]

Do not:

- initialize and patch each child independently with a different procedure;
- seed one outlet case from another solved outlet case; or
- seed a Stage-2 case from a Stage-1 endpoint.

---

## 5. Outlet formulations

### 5.1 Pressure Outlet — `PO`

Primary parameter:

\[
P_{brine}
\]

This family remains active for Stage 2.

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

This family remains active for Stage 2.

### 5.3 Mass-Flow Outlet — `MF`

Stage-1 diagnostic family only. All three Stage-1 pilots terminated before 500 iterations. Do not generate Stage-2 MF cases in this setup.

### 5.4 Exhaust Fan — `EF`

Stage-1 diagnostic family only. `EF` was included for behavioural characterization and is not treated as a physically preferred brine-pipe model. Do not generate Stage-2 EF cases in this setup.

### 5.5 Outflow exclusion

`Outflow` remains excluded because it does not provide the downstream-pressure/resistance control required by this experiment and can conflict with the frozen pressure-outlet architecture.

---

## 6. Fixed run budget

Every child receives:

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
5. continue the remaining independent cases.

---

## 7. Common monitor package

Use the same monitor definitions for all Stage-2 cases.

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

Store both Fluent-native signed values and outward-positive converted values.

### 7.2 Y010 liquid inventory

\[
V_{l,Y010}=\int_{Y010}\alpha_l\,dV
\]

### 7.3 Y030 lower-region inventory

Create/retain the monitoring-only region:

\[
y\le+0.30\ \mathrm{m}
\]

and monitor:

\[
V_{l,Y030}=\int_{y\le0.30}\alpha_l\,dV.
\]

Y030 is not patched.

### 7.4 Total-domain liquid inventory — required for Stage 2

Stage 1 did not preserve this history. Stage 2 must add and retain:

\[
\boxed{V_{l,total}=\int_V\alpha_l\,dV}
\]

This is required so lower-region depletion can be distinguished from redistribution elsewhere in the computational domain.

### 7.5 Brine-pipe-entry pressure

Preferred diagnostic location:

```text
brine-pipe-entry-section
```

When reproducibly available, record area-weighted average, minimum, and maximum static pressure. A nearby cell region may also be used for volume-averaged static pressure.

This remains a diagnostic rather than a run gate.

### 7.6 Outlet behaviour

Where available, record:

- area-averaged normal velocity at the brine outlet;
- mixture density at the brine outlet;
- reverse-flow area fraction; and
- total brine mass flow.

### 7.7 Residuals

Store and plot residual histories. Do not impose a terminal residual threshold as a Stage-2 pass/fail criterion.

---

## 8. Stage 1 — completed pilot characterization

Stage 1 requested three independent pilot points for each of four outlet families from the same saved Y010 parent.

### 8.1 Pressure Outlet pilots

| Case | Brine pressure | Stage-1 outcome |
|---|---:|---|
| `02e-PO-P1` | `1.160 MPa` gauge | completed 500 |
| `02e-PO-P2` | `1.200 MPa` gauge | FPE at 335 |
| `02e-PO-P3` | `1.240 MPa` gauge | FPE at 226 |

### 8.2 Outlet Vent pilots

Keep discharge pressure at `1.200 MPa` gauge.

| Case | `K` | Stage-1 outcome |
|---|---:|---|
| `02e-OV-P1` | `0` | completed 500 |
| `02e-OV-P2` | `10` | FPE at 448 |
| `02e-OV-P3` | `100` | FPE at 457 |

### 8.3 Mass-Flow Outlet pilots

| Case | Liquid target | Stage-1 outcome |
|---|---:|---|
| `02e-MF-P1` | `58.4235 kg/s` | FPE at 33 |
| `02e-MF-P2` | `116.847 kg/s` | FPE at 9 |
| `02e-MF-P3` | `233.694 kg/s` | FPE at 254 |

### 8.4 Exhaust Fan pilots

Keep discharge pressure at `1.200 MPa` gauge.

| Case | Pressure jump | Stage-1 outcome |
|---|---:|---|
| `02e-EF-P1` | `-50 kPa` | FPE at 254 |
| `02e-EF-P2` | `0 kPa` | completed 500 |
| `02e-EF-P3` | `+50 kPa` | completed 500 |

The detailed Stage-1 evidence and limitations are retained in the linked results report.

---

## 9. Stage-1 interpretation used to select Stage 2

The original automatic Stage-2 gate required three complete finite pilot histories per family. No family satisfied that rule, so no automatic Stage-2 controls were generated.

The user has instead chosen a **manual targeted refinement** based on the coarse Stage-1 observations.

The selection is intentionally limited to `PO` and `OV` because:

- `PO-P1` completed 500 iterations and provides a stable lower-pressure anchor;
- the higher PO cases failed, creating a useful transition interval between the stable `1.160 MPa` anchor and the first failed `1.200 MPa` point;
- `OV-P1` completed 500 iterations and provides a stable zero-added-resistance anchor;
- `OV-P2` failed relatively late at `K=10`, creating a useful transition interval between `K=0` and `K=10`;
- all three `MF` cases failed and therefore do not justify further Stage-2 allocation here; and
- `EF` remains diagnostic, and the completed `+50 kPa` case did not provide enough benefit to justify prioritising this family over PO/OV.

The completed finite cases also showed strongly negative liquid balance and declining lower-region liquid inventory. This indicates that the current stable anchor cases are still highly permissive with respect to the initialized liquid inventory. The Stage-2 question is therefore not “which case is already correct?” but:

> Can moderate additional backpressure or outlet resistance reduce excessive liquid drainage while retaining numerical survivability and without causing unacceptable vapour leakage or liquid carryover?

Comparisons involving failed Stage-1 cases must respect their different stopping iterations. Their last-valid inventories are contextual evidence only, not equivalent endpoints.

---

## 10. Stage 2 — fixed four-case targeted refinement

There is **no automatic branching algorithm** in the revised Stage 2.

Run exactly the following four cases from the unchanged saved Y010 parent.

### 10.1 Pressure Outlet follow-up

Keep the steam outlet fixed at `1.120 MPa` gauge.

| Case | Brine pressure | Purpose |
|---|---:|---|
| `02e-PO-S2-A` | `1.175 MPa` gauge | moderate step above the stable `1.160 MPa` anchor |
| `02e-PO-S2-B` | `1.190 MPa` gauge | probe nearer the `1.200 MPa` Stage-1 failure boundary |

These cases test whether increased backpressure reduces brine liquid drainage and improves lower-region liquid retention before the numerical instability observed at `1.200 MPa` is reached.

### 10.2 Outlet Vent follow-up

Keep:

\[
P_{discharge}=1.200\ \mathrm{MPa\ gauge}
\]

and vary only constant `K`.

| Case | `K` | Purpose |
|---|---:|---|
| `02e-OV-S2-A` | `3` | modest added resistance above the stable `K=0` anchor |
| `02e-OV-S2-B` | `7` | stronger resistance while remaining below the `K=10` Stage-1 failure point |

These cases test whether added resistance reduces excessive brine liquid drainage and improves liquid retention without reproducing the late numerical failure observed at `K=10`.

### 10.3 No Stage-2 MF or EF cases

Do not create additional `MF` or `EF` children under this setup unless the user explicitly revises the experiment again.

---

## 11. Stage-2 analysis quantities

For complete runs, use arithmetic means over iterations `401–500` for phase-flow reporting. For failed runs, preserve last-valid histories but do not treat them as equivalent complete endpoints.

Define the outward-positive liquid balance:

\[
\boxed{
L=\bar{\dot m}_{l,in}-\bar{\dot m}_{l,brine}-\bar{\dot m}_{l,steam}
}
\]

Use `L` as a descriptive mass-balance quantity, not an automatic branching gate.

Also calculate:

\[
R_{v,b}=\frac{\bar{\dot m}_{v,brine}}{\bar{\dot m}_{v,in}}
\]

and:

\[
R_{l,s}=\frac{\bar{\dot m}_{l,steam}}{\bar{\dot m}_{l,in}}.
\]

The primary Stage-2 comparison is the joint behaviour of:

- liquid flow to the brine outlet;
- vapour leakage to the brine outlet;
- liquid carryover to the steam outlet;
- Y010 inventory history;
- Y030 inventory history;
- total-domain liquid inventory history;
- brine-pipe-entry pressure where available;
- reverse flow where available; and
- numerical survivability over 500 iterations.

No automatic physical-success threshold is defined. The user interprets the result.

---

## 12. Comparison anchors

Use the following Stage-1 cases as the primary anchors for Stage-2 plots and tables:

```text
PO anchor: 02e-PO-P1, 1.160 MPa, completed 500
OV anchor: 02e-OV-P1, K=0, completed 500
```

Use the following only as numerical transition/failure context:

```text
PO failure boundary context: 02e-PO-P2, 1.200 MPa, FPE at 335
OV failure boundary context: 02e-OV-P2, K=10, FPE at 448
```

Do not compare a failed-case endpoint directly with iteration 500 as though the calculation lengths were equivalent.

---

## 13. Build and readback procedure

For every Stage-2 child:

1. reload the exact saved Y010 execution parent;
2. verify Mixture, RNG k-epsilon, gravity, inlet types/velocities, steam pressure, materials, DPM off, EWF off, and preserved numerical methods;
3. convert only `brineoutlet` / `brine-outlet` to the intended outlet type using the verified live zone name;
4. apply only the case-specific control value;
5. apply/read back a liquid-dominant brine backflow state where that boundary formulation exposes a relevant phase backflow control;
6. verify the Y010, Y030, **total-domain liquid**, phase-flux, residual, and available pressure/outlet monitors are active before solving;
7. verify no unintended inlet, steam-outlet, model, material, or numerical changes;
8. save a uniquely named pre-run child;
9. run 500 iterations;
10. save paired endpoint case/data and monitor histories; and
11. reload the unchanged Y010 parent before building the next child.

Never seed one Stage-2 child from another solution.

---

## 14. Artifact naming

Stage-1 names remain unchanged.

Recommended Stage-2 patterns:

```text
02e-PO-S2-A-y010-p1175
02e-PO-S2-B-y010-p1190
02e-OV-S2-A-y010-p1200-k3
02e-OV-S2-B-y010-p1200-k7
```

Every artifact name must include the actual control value.

---

## 15. Required visual outputs

For every Stage-2 run create consistent plots of:

1. Y010 liquid inventory vs iteration;
2. Y030 lower-region liquid inventory vs iteration;
3. total liquid inventory vs iteration;
4. liquid brine-outlet mass flow vs iteration;
5. vapour brine-outlet mass flow vs iteration;
6. steam-outlet phase flows vs iteration;
7. pipe-entry average pressure vs iteration, when available; and
8. residual histories vs iteration.

Where a case reaches iteration 500, also save consistent field images for lower-vessel liquid volume fraction, brine-pipe liquid volume fraction, lower-vessel static pressure, brine-pipe velocity, and one full-vessel liquid-volume-fraction view.

---

## 16. Reporting and interpretation

Update the existing Stage-1 report after Stage 2 rather than replacing the Stage-1 historical record.

The Stage-2 comparison should show the four new cases alongside their Stage-1 family anchors and clearly distinguish complete from failed calculations.

Do not rank cases automatically and do not label a case:

- correct;
- optimal;
- realistic;
- validated;
- converged; or
- best.

The report may describe observations such as:

```text
liquid drainage decreased
lower-region liquid was retained for longer
vapour brine leakage increased/decreased
liquid carryover to steam outlet increased/decreased
reverse flow appeared
pressure oscillated
case remained numerically finite for 500 iterations
case failed before 500 iterations
```

but physical interpretation and the next experiment remain user decisions.

---

## 17. What this setup is allowed to conclude

`02e` may establish:

- how the tested Fluent outlet formulations respond under a common initialized Mixture state;
- which Stage-1 families were numerically usable enough to justify targeted follow-up;
- whether moderate PO backpressure between `1.160` and `1.200 MPa` changes liquid drainage/retention before the observed failure boundary;
- whether moderate OV resistance between `K=0` and `K=10` changes liquid drainage/retention before the observed failure boundary;
- whether the four Stage-2 controls provide a more useful numerical operating region for later refinement; and
- where a later detailed sensitivity should concentrate.

It may **not** establish:

- the real geothermal brine-system downstream pressure;
- the correct hydraulic loss coefficient;
- the true separator operating liquid level;
- validation of the Mixture model;
- a converged production separator operating point; or
- the physically preferred outlet family without subsequent user interpretation and later validation work.

The revised design rule is:

> **Stage 1 screens outlet families and reveals useful numerical transition regions. Stage 2 deliberately probes two points inside the stable-to-failure intervals for PO and OV. Liquid inventory and phase routing explain the consequence; the user decides what the behaviour means physically.**
