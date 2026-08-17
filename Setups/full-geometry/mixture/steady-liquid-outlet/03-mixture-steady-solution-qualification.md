# Setup 03 — Mixture Steady-Solution Qualification

> **Lifecycle:** `draft`  
> **Execution status:** `DO NOT RUN — detail audit still open`  
> **Purpose of this draft:** define the next steady Mixture experiment before execution details such as inlet/outlet turbulence specification, wall treatment, relaxation/Courant controls, and exact equation-control procedure are frozen.

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03` |
| Lifecycle | `draft` |
| Investigation mode | numerical qualification / steady-branch continuation |
| Parent | [02e — Y010 outlet-boundary characterization](02e-mixture-y010-brine-outlet-boundary-characterization.md) |
| Primary outlet family | Pressure Outlet |
| Initial brine pressure | `1.160 MPa gauge` |
| Initial liquid condition | Y010 lower-region liquid patch |
| Primary objective | obtain one genuinely steady full-Mixture solution before returning to transient work |
| Primary decision variables | staged equation activation, pressure-velocity coupling, conservative startup numerics, then brine-pressure continuation |
| Evidence-use label | numerical-method qualification first; physical interpretation only after a steady branch is established |

---

## 1. Why this setup exists

The previous full-geometry Mixture work established that brine-outlet pressure strongly affects phase routing, but it did **not** produce a convincing steady liquid-inventory state.

The key distinction is:

- a case can complete `500` or `1000` iterations without an FPE;
- yet still discharge several times more liquid than enters the separator;
- therefore numerical survivability alone is not a steady-solution criterion.

The transient branch is paused for this experiment. Before asking transient Mixture to resolve liquid accumulation/drainage, this setup attempts to establish at least one genuinely steady Mixture state using a deliberately staged solution procedure.

The experiment asks:

> **Can the existing full-geometry Mixture model be brought to a steady state in which phase fluxes and liquid inventory are no longer systematically drifting, when the cyclone flow field and multiphase equations are introduced progressively rather than solved aggressively from the first iteration?**

If such a state can be obtained, it becomes the numerical anchor for a controlled brine-pressure continuation toward stronger retained-liquid behaviour.

---

## 2. Relationship to 02c and 02e

### 2.1 What is retained from 02e

The first qualification case intentionally preserves the `02e` Y010 Pressure Outlet physical configuration as far as possible:

- same production mesh;
- same water-vapour / water-liquid material pair;
- same Mixture model;
- same RNG `k-epsilon` turbulence family;
- same gravity;
- same split velocity inlets;
- same steam outlet;
- same Y010 lower-region initialization;
- same Pressure Outlet brine boundary family;
- same liquid-dominant brine backflow composition;
- DPM off;
- EWF off.

The intended experiment is therefore **not another broad physical-parameter screen**. The first task is to change the *solution strategy* while holding the physical problem fixed.

### 2.2 Why `1.160 MPa` is the initial anchor

`02e-PO-P1` at:

\[
P_{brine}=1.160\ \mathrm{MPa\ gauge}
\]

completed the requested 500 steady iterations, whereas higher-pressure pressure-outlet pilots encountered numerical failure.

This does **not** make `1.160 MPa` a physically correct operating pressure. The case drained the initialized liquid too aggressively. It is selected only because it is the most conservative known pressure-outlet anchor from which to attempt a genuine steady convergence procedure.

---

## 3. Frozen physical model for the first qualification case

Use the production mesh:

```text
Full-geomV2-231kcells.msh.h5
```

Known production-mesh state:

```text
Total cells = 231,376
Fluid zones = 1 combined fluid cell zone
```

Preserve the following unless the detail audit below explicitly resolves a currently missing field.

| Category | Required state |
|---|---|
| Solver | pressure-based, steady |
| Multiphase | Mixture |
| Turbulence | RNG `k-epsilon` |
| Gravity | `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Energy | preserve current verified production/02e state; **exact state to be frozen before execution** |
| DPM | off |
| EWF | off |
| Liquid inlet | Velocity Inlet, `27.118 m/s` |
| Steam inlet | Velocity Inlet, `27.118 m/s` |
| Inlet reference / initial gauge pressure | `1.140 MPa` |
| Steam outlet | Pressure Outlet, `1.120 MPa gauge` |
| Brine outlet | Pressure Outlet, initially `1.160 MPa gauge` |
| Steam-outlet liquid backflow VF | `0.0` |
| Brine-outlet liquid backflow VF | `1.0` |
| Brine-outlet vapour backflow VF | `0.0` |
| Liquid density | `881.77 kg/m³` |
| Materials | preserve verified water-vapour / water-liquid production pair |

### 3.1 Fields that are intentionally not yet frozen in this draft

The following must be audited against the actual Fluent case/setup lineage before this document becomes executable:

- turbulence specification method and values at **both velocity inlets**;
- turbulence backflow specification and values at **steam and brine pressure outlets**;
- phase-specific inlet volume fractions / phase assignment details;
- wall roughness and turbulence wall treatment;
- exact material viscosity and vapour density treatment;
- Mixture slip / drag-law settings;
- volume-fraction formulation details;
- exact spatial discretization schemes;
- exact pressure-velocity coupling settings;
- relaxation factors and/or Coupled Courant number;
- gradient scheme;
- initialization settings beyond the Y010 patch;
- residual normalization and convergence-criteria state;
- exact Fluent controls used to disable/enable Volume Fraction and Slip Velocity equations.

Until these are resolved, this setup remains `DO NOT RUN`.

---

## 4. Y010 initialization

Use the same approved Y010 definition as 02e.

### 4.1 Initialization sequence

```text
load/rebuild frozen production Mixture state
→ Hybrid Initialize
→ create approved Y010 register
→ patch phase-2 water-liquid volume fraction = 1.0
→ verify integrated Y010 liquid inventory
→ save pre-solve case/data checkpoint
```

Approved Y010 region:

```text
x = [-2.067034, 1.066098] m
y = [-1.484584, 0.100000] m
z = [-1.469893, 2.000000] m
inside = True
```

Coordinate interpretation:

> `y = 0` is the level at which the brine pipe is exactly submerged. Y010 extends the initialized lower liquid region to `y = +0.10 m`.

Observed 02e production-mesh reference:

```text
Selected cells = 33,315
Geometric selected-cell volume = 4.829410214 m³
Actual post-patch liquid inventory = 4.790652590 m³
Initial liquid mass = 4224.253734 kg
```

Reference value:

\[
V_{l,Y010,0}=4.790652590\ \mathrm{m^3}.
\]

The setup must verify the actual post-patch inventory before solving. If the value differs materially from the reference, stop and investigate rather than silently continuing.

---

## 5. Definition of success

This setup is explicitly different from the previous fixed-iteration screens.

A case is **not** considered steady merely because it reaches a requested iteration count.

The primary steady-state evidence is:

### 5.1 Liquid phase flux balance

Using outward-positive outlet conventions:

\[
L=\dot m_{l,in}-\dot m_{l,brine}-\dot m_{l,steam}.
\]

Qualification target:

\[
\boxed{|L|/\dot m_{l,in}<5\%}
\]

for the initial numerical qualification, with a preferred later target below `2%`.

### 5.2 Vapour phase flux balance

Using the corresponding vapour inlet and outlet fluxes, target an imbalance below `5%` for qualification.

### 5.3 Liquid inventory stationarity

Monitor:

\[
V_{l,Y010},\qquad V_{l,Y030},\qquad V_{l,total}.
\]

Over the final accepted convergence window, total and lower-region liquid inventories must no longer show a systematic filling or draining trend.

Initial practical target:

- less than approximately `1–2%` change over the final `200` iterations;
- no monotonic inventory trend that is large compared with short-period numerical variation.

### 5.4 Flux stationarity

Over the same final convergence window, phase fluxes at each inlet/outlet should be approximately stationary.

Initial practical target:

- less than approximately `1–2%` change in the relevant final-window mean/trend;
- no large systematic drift.

### 5.5 Numerical survivability

The run must contain no:

- floating-point exception;
- unrecoverable AMG divergence;
- solver termination;
- equivalent numerical breakdown.

### 5.6 Residual role

Residuals remain required diagnostics, but there is no single residual threshold that can override obviously non-steady phase fluxes or inventory.

A candidate cannot qualify if the residuals show sustained growth or severe oscillatory breakdown even when the flux window happens to appear temporarily balanced.

### 5.7 Physical quality is a separate decision

Wrong-outlet vapour, liquid carryover and retained-liquid amount remain important, but they are **not used to reject the first mathematical steady anchor solely because the separation behaviour is poor**.

The immediate objective is first to prove that a steady branch exists. Physical quality is assessed after that anchor exists.

---

## 6. Proposed staged solution procedure

The central numerical hypothesis is that the full cyclone field should be developed progressively before all Mixture transport equations are solved simultaneously.

### Stage S0 — carrier/cyclone flow-field development

Start from the frozen initialized physical setup but temporarily disable the Mixture equations for:

- Volume Fraction;
- Slip Velocity.

Solve the remaining pressure, momentum and turbulence field using conservative steady numerics.

Purpose:

> establish a stable pressure/velocity/turbulence cyclone field before allowing the multiphase distribution and slip response to evolve.

**S0 exit rule — draft:** do not use a fixed iteration count alone. Continue until pressure, velocity/flux monitors and residual trends are substantially settled. Exact quantitative S0 gate remains to be frozen after the detail audit.

Save:

```text
S0-flow-field.cas.h5
S0-flow-field.dat.h5
```

### Stage S1 — enable Volume Fraction

Enable the Mixture Volume Fraction equation while retaining the conservative startup numerics.

Purpose:

> allow the phase distribution and Y010 inventory to adjust on top of an already-developed cyclone flow field.

Monitor the complete phase-flux and liquid-inventory package during this stage.

Do not yet change brine pressure.

Save the first stable checkpoint as:

```text
S1-volume-fraction.cas.h5
S1-volume-fraction.dat.h5
```

### Stage S2 — enable Slip Velocity

Enable the Mixture Slip Velocity equation so the complete intended Mixture phase-relative-motion model is restored.

Again, keep:

\[
P_{brine}=1.160\ \mathrm{MPa\ gauge}.
\]

Continue with conservative numerics until the complete Mixture field becomes stable or a numerical failure is reached.

Save:

```text
S2-full-mixture-start.cas.h5
S2-full-mixture-start.dat.h5
```

### Stage S3 — full-Mixture steady qualification

With all intended Mixture equations active, continue solving until the steady-state criteria in Section 5 can be assessed over a sufficiently long final window.

The initial analysis window is proposed as the most recent `200` iterations, but the run may need substantially more than `500` iterations.

There is deliberately **no fixed total iteration ceiling** in the scientific definition of success. Execution can still use checkpoint budgets, but the solution should not be labelled steady because a budget expired.

If S3 satisfies the qualification criteria, save:

```text
STEADY-BASE-1p160.cas.h5
STEADY-BASE-1p160.dat.h5
```

This becomes the first steady anchor.

### Stage S4 — higher-order confirmation

After a steady baseline is obtained with conservative startup numerics, change only the intended higher-order spatial discretization settings and re-converge.

Purpose:

> demonstrate that the steady branch is not merely a first-order numerical artefact.

The exact schemes and transition procedure remain to be frozen in the detail audit.

If the higher-order solution satisfies the same steady criteria, save:

```text
STEADY-BASE-HO-1p160.cas.h5
STEADY-BASE-HO-1p160.dat.h5
```

This is the preferred parent for pressure continuation.

---

## 7. Pressure-velocity coupling strategy

The preferred first test is:

```text
Coupled pressure-velocity
+ segregated volume-fraction solution
```

Do **not** initially enable a formulation that directly couples volume fractions into the pressure-velocity block unless later evidence specifically justifies it.

The rationale is to strengthen the steady pressure/velocity coupling while avoiding an unnecessary increase in the aggressiveness of the volume-fraction solve during startup.

### 7.1 Conservative startup controls

The draft intends to use:

- conservative initial Coupled Courant number;
- first-order spatial discretization for the earliest stabilization stages where appropriate;
- no case-specific ad-hoc tuning simply to force an unstable candidate through;
- staged promotion to higher-order schemes only after the field is settled.

**Exact numerical values are intentionally TBD until the actual parent case and Fluent recommendations are audited.**

### 7.2 Pseudo-time

Pseudo-time may be considered as a stabilization aid during development, but it must **not** be allowed to obscure the final phase mass balance.

If pseudo-time is used to approach a solution, the final candidate must be re-solved with the chosen final steady formulation and demonstrate the Section 5 balance/stationarity criteria before qualification.

Pseudo-time is therefore a numerical aid, not part of the physical definition of the final steady state.

---

## 8. Pressure continuation after STEADY-BASE

Do not begin this stage unless `STEADY-BASE` has qualified.

The purpose is to follow one converged solution branch gradually toward greater retained-liquid behaviour rather than launching independent large pressure jumps from the original Y010 parent.

### 8.1 Continuation principle

Starting from the converged pressure-outlet state at:

\[
P_{brine}=1.160\ \mathrm{MPa\ gauge},
\]

increase brine pressure in small increments.

Initial proposed sequence:

\[
1.1600
\rightarrow1.1625
\rightarrow1.1650
\rightarrow1.1675
\rightarrow1.1700\ \mathrm{MPa\ gauge}
\]

and continue only while each preceding case produces a usable converged parent.

The `2.5 kPa` increment is a **draft continuation step**, not yet a validated pressure resolution.

### 8.2 Parent rule

Each pressure child must start from the **fully converged immediately preceding pressure state**.

Do not:

- restart every continuation pressure from the original Y010 parent;
- re-Hybrid-Initialize each pressure child;
- re-patch Y010 between continuation points;
- jump directly to the old `1.175`, `1.190`, `1.200 MPa` cases unless the continuation branch reaches them naturally.

This stage deliberately follows a numerical branch rather than conducting an independent pressure sensitivity.

### 8.3 Continuation target

The scientifically interesting region is where:

\[
\dot m_{l,brine}+\dot m_{l,steam}
\approx
\dot m_{l,in}
\]

while the liquid inventory remains bounded and the solution remains numerically steady.

At every continuation point record:

- phase-specific inlet/outlet fluxes;
- Y010, Y030 and total liquid inventory;
- wrong-outlet vapour;
- liquid carryover to steam outlet;
- brine-pipe-entry pressure;
- reverse-flow diagnostics;
- convergence window statistics.

### 8.4 Stop conditions

Stop continuation and preserve the last converged state if any of the following occurs:

- FPE / unrecoverable numerical breakdown;
- no stationary inventory can be obtained despite adequate continuation iterations;
- persistent reverse-flow regime makes the pressure boundary qualitatively different from the preceding converged branch;
- the next pressure step cannot be made to converge without changing additional physical/numerical controls;
- user review determines that the branch has already become physically uninformative.

Do not silently reduce pressure increments, relaxation values or change schemes after a failed child without recording that as a new numerical experiment.

---

## 9. Common monitor and evidence package

The following must exist before S0/S1/S2 execution so that the complete history is recoverable.

### 9.1 Phase-specific mass flows

Record signed Fluent-native and outward-positive values for:

**Liquid**

- liquid inlet;
- brine outlet;
- steam outlet.

**Vapour**

- steam inlet;
- brine outlet;
- steam outlet.

### 9.2 Liquid inventory

Record:

\[
V_{l,Y010}=\int_{Y010}\alpha_l\,dV,
\]

\[
V_{l,Y030}=\int_{Y030}\alpha_l\,dV,
\]

and

\[
\boxed{V_{l,total}=\int_V\alpha_l\,dV}.
\]

Where convenient, also store corresponding liquid masses.

### 9.3 Brine-pipe diagnostics

At a reproducible `brine-pipe-entry-section`, record where available:

- area-weighted static pressure;
- minimum and maximum static pressure;
- area-averaged normal velocity;
- mixture density;
- reverse-flow area fraction.

### 9.4 Outlet diagnostics

Record:

- total brine mass flow;
- total steam-outlet mass flow;
- phase-resolved brine and steam-outlet fluxes;
- reverse-flow warnings/events and their duration.

### 9.5 Residuals

Store all relevant residual histories from the beginning of S0 through final qualification.

Equation activation/deactivation points must be marked in the resulting plots/logs so residual changes are not misinterpreted as one continuous numerical regime.

### 9.6 Solver event log

Record at minimum:

- initialization complete;
- Y010 inventory verification;
- S0 start/end;
- Volume Fraction enabled;
- S1 start/end;
- Slip Velocity enabled;
- S2 start/end;
- numerical-scheme changes;
- pressure continuation changes;
- reversed-flow warnings;
- turbulent-viscosity limiting counts where available;
- AMG warnings/divergence;
- FPE or solver termination.

---

## 10. Optional fallback experiments — not active by default

These are retained only as explicit next diagnostics if the primary staged procedure fails. Do not combine them silently with the baseline.

### 10.1 Solve N-phase Volume Fraction Equations

If the full-Mixture state becomes numerically stable but persistent phase mass imbalance remains, test Fluent's option to solve the complete set of phase volume-fraction equations rather than obtaining one phase purely by complement.

This is a separate numerical experiment and must be labelled accordingly.

### 10.2 Alternative pressure-velocity coupling

If Coupled cannot be made stable using a reasonable conservative startup, create a controlled comparison against the verified previous steady pressure-velocity coupling method.

Do not mix multiple coupling-method changes into the pressure continuation.

### 10.3 Smaller continuation pressure step

If a converged continuation parent fails only after a pressure increment, a smaller pressure step may be tested as a branch-following diagnostic.

Record the failed larger step first; do not erase it from the evidence chain.

---

## 11. Decision tree

```text
build frozen 02e-like Y010 + PO 1.160 MPa case
        ↓
S0: develop pressure/velocity/turbulence field
VF + slip equations temporarily disabled
        ↓
S1: enable Volume Fraction
        ↓
S2: enable Slip Velocity
        ↓
S3: full Mixture steady qualification
        │
        ├── fails → diagnose numerical method / parent details
        │          do NOT return directly to transient
        │
        └── passes
             ↓
S4: higher-order re-convergence
             │
             ├── fails → quantify discretization sensitivity
             │
             └── passes
                  ↓
             save STEADY-BASE
                  ↓
       small-step brine-pressure continuation
                  ↓
       search for stationary liquid-inventory branch
```

---

## 12. Interpretation contract

This setup has two distinct phases of interpretation.

### Phase A — numerical qualification

The user is asked to decide whether the evidence is sufficient to call a state genuinely steady based primarily on:

- phase flux balance;
- liquid-inventory stationarity;
- flux stationarity;
- numerical stability;
- residual behaviour.

A mathematically steady but physically poor phase-routing solution may still be retained as a useful numerical anchor.

### Phase B — physical continuation

Only after a steady anchor exists should the user interpret:

- retained-liquid level/inventory;
- brine liquid flow;
- vapour short-circuit to the brine outlet;
- liquid carryover to steam outlet;
- brine-pipe pressure and reverse flow;
- whether the continuation is moving toward a believable separator state.

No automatic statement such as “optimum pressure” or “validated operating condition” is permitted from this setup alone.

---

## 13. Pre-execution detail audit — mandatory

Before this draft can become `active`, the exact Fluent state must be reconstructed and frozen for the details that earlier reports often left implicit.

At minimum answer and record:

1. What turbulence **specification method** is used at each velocity inlet?
2. What exact turbulence values are applied at each inlet?
3. What turbulence **backflow** specification is used at each pressure outlet?
4. What exact outlet backflow turbulence values are applied?
5. What phase volume fractions are imposed at the liquid and steam inlets?
6. Are phase velocities shared or phase-specific at the inlets under the current Mixture setup?
7. What are the exact wall roughness and wall-treatment settings?
8. What are the exact water-liquid viscosity and water-vapour density/viscosity models/values?
9. What Mixture slip/drag model is active?
10. What exact spatial discretization schemes are currently inherited from 02e?
11. What gradient scheme is active?
12. What exact pressure-velocity coupling and controls were used in the previous steady parent?
13. What under-relaxation factors are currently stored?
14. If Coupled is used here, what initial Courant number and coupled controls will be frozen?
15. Is pseudo-time currently enabled anywhere in the parent state?
16. What residual convergence criteria/normalization settings are active?
17. What exact Hybrid Initialization options are active?
18. What is the executable Fluent/PyFluent path for temporarily disabling and re-enabling Volume Fraction and Slip Velocity equations, and can each state be read back reliably?
19. Are all monitor definitions evaluated from the intended phase/domain and signed consistently?
20. What exact checkpoint/save cadence should be used so every equation-activation stage can be reopened and audited?

This file remains a draft until these questions are resolved or explicitly accepted as intentional assumptions.

---

## 14. Immediate next action

Do **not** execute Stage S0 yet.

First audit the existing full-geometry Mixture setup lineage, Fluent boundary definitions, scripts and result records to reconstruct all missing detailed settings. Update this file with explicit values rather than inherited phrases such as “preserve verified parent state” wherever the value can be established.

Only then change:

```text
Lifecycle: draft
Execution status: DO NOT RUN
```

to an active executable setup.