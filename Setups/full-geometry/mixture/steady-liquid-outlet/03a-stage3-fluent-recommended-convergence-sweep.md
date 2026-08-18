# 03A Stage 3 — Fluent-Recommended Convergence Sweep

> **Status:** active plan — scientific design substantially resolved; execution implementation still requires smoke-test verification  
> **Setup family:** `03A` full-geometry steady Mixture baseline  
> **Purpose:** perform a broad, long-duration numerical convergence sweep based directly on Ansys Fluent guidance for difficult Mixture/cyclone and strongly swirling flows before narrowing onto any one turbulence-model or solver-rescue strategy.  
> **Physical case:** unchanged from 03A — same geometry, materials, phase definitions, split inlet, outlet pressures, gravity, and no liquid patch.  
> **Parent authority:** a verified 03A pre-initialization case with the frozen Stage-3 fingerprint defined below. Branches must not begin from an already-developed Stage-1/Stage-2 solution field unless a later setup explicitly defines that as a separate experiment.  
> **Execution model:** three independent Fluent sessions may execute Stage-3 branches in parallel. Session/server assignment is operational execution metadata only and must not define case identity, scientific lineage, filenames, or report structure.  
> **Execution specification:** [`03a-stage3-shared-parent-and-seed-spec.yaml`](./03a-stage3-shared-parent-and-seed-spec.yaml) is the machine-readable authority for shared P0 construction, reusable schedule seeds, branch derivation, OneDrive/local-run handling, and server-independent execution metadata.

---

## 1. Why Stage 3 exists

Stage 1 showed that the canonical 08b-parity full-geometry case can survive `1,000` steady iterations, but it did not approach a sufficiently settled state. The endpoint still had high continuity error and strongly intermittent turbulence residuals, especially `epsilon`.

Stage 2 then tested four shorter numerical interventions (`N1`, `N3`, `N4`, `N5`). These runs were useful as screening experiments, but they were deliberately short relative to the convergence timescale now considered necessary.

The strongest Stage-2 clue came from `N5`:

```text
Stage-1 parent
→ standard k-epsilon bootstrap
→ restore RNG k-epsilon
```

During the standard-`k-epsilon` bootstrap, the residual envelope became much more bounded and the diagnostic mass imbalance improved substantially. The available Stage-2 report gives, over the final 100 iterations of the standard bootstrap:

```text
continuity median ≈ 7.82e-2
k median          ≈ 2.28e-3
epsilon median    ≈ 5.01e-3
epsilon P95       ≈ 1.34e-2
mass imbalance    ≈ 5.24%
```

compared with the Stage-1 reference:

```text
continuity median ≈ 1.58e-1
k median          ≈ 3.29e-3
epsilon median    ≈ 3.22e-2
epsilon P95       ≈ 9.39e-1
mass imbalance    ≈ 17.17%
```

However, the improvement did not remain bounded when the authoritative RNG `k-epsilon` model was restored. Stage 3 therefore does **not** assume that standard `k-epsilon` is the answer. Instead, it first performs the wider solution-strategy sweep recommended by Fluent itself.

The working principle is:

> Before changing the physical model or committing to a different turbulence model, test whether the difficult cyclone/Mixture field can be made substantially more numerically useful by applying Fluent's own staged-solution recommendations over a long enough history to distinguish short-term improvement from genuine settling.

Stage 3 is deliberately broader than Stage 2. It is not trying to find the quickest rescue. It is trying to map which parts of Fluent's recommended continuation strategy actually help this specific full-geometry separator.

A second important principle is that the carrier field is not judged by turbulence residuals alone. For this project, the central physical quantities are the **total flow split, phase flow split, full-domain balance, and pressure behaviour around the brine outlet**. A numerically quieter `k`/`epsilon` field is useful only if the corresponding pressure/flow field is also becoming developed and interpretable.

The staged branches therefore use an evidence-driven transition rule, but that rule is intentionally **non-terminal**. If a preconditioning stage does not satisfy the preferred gate, the branch is still allowed to progress after a sufficiently long attempt. This is important because the project objective is to complete at least one full end-to-end realization of every planned Fluent-guided strategy rather than abandoning branches before the final operating condition is ever tested.

---

## 2. Fluent guidance being tested

Stage 3 is built primarily from two official Ansys Fluent guidance sources for Fluent 2025 R2, with one additional turbulence-convergence recommendation retained as an explicitly later follow-up.

### 2.1 Mixture-model solution strategy — highest-priority/direct cyclone guidance

Fluent's multiphase solution guidance states that, for some Mixture-model cases **including cyclone separation**, an initial solution can be obtained more easily by temporarily disabling the:

- `Volume Fraction` equation;
- `Slip Velocity` equation;

then computing the initial flow field, restoring those equations once a converged flow field has been obtained, and continuing the full Mixture solution.

The same guidance recommends beginning a Mixture calculation with a **slip-velocity under-relaxation factor of `0.2` or lower** and only increasing it if convergence is good.

This is the most directly applicable Fluent recommendation in Stage 3 because Fluent explicitly names cyclone separation.

Official source:

- Ansys Fluent 2025 R2 User's Guide — *Solution Strategies for Multiphase Modeling*, §27.8.2.2 Mixture Model:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html>

### 2.2 Strong swirl / rotating-flow solution strategy — strong 3D continuation guidance

Fluent's swirl/rotation guidance recommends, for difficult pressure-based segregated calculations:

- using `PRESTO!` for steep rotational/swirl pressure gradients;
- lowering velocity under-relaxation when necessary, with approximately `0.3–0.5` given as a useful range in difficult rotating/swirl guidance;
- beginning from a lower rotational or inlet-swirl intensity and gradually increasing toward the final operating condition.

The guide gives approximately `10%` of the final operating condition as a possible initial level and suggests increasing the rotational/swirl speed progressively, for example by roughly doubling between stages.

For the current fixed 3D spiral inlet, reducing the inlet velocity is not a pure swirl-only control: it changes phase mass flow, Reynolds number, inertial loading and centrifugal forcing together. Stage 3 therefore treats the inlet-velocity ramp as a **numerical continuation/homotopy strategy adapted from Fluent's gradual-swirl recommendation**, not as a literal reproduction of an axisymmetric or moving-reference-frame procedure.

Official sources:

- Ansys Fluent 2025 R2 User's Guide — *Swirling and Rotating Flows* / related solution guidance;  
- Ansys Fluent 2025 R2 User's Guide — *Flow in Single Moving Reference Frames*, gradual rotational-speed strategy:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_th_sec_srf_fjk.html>

### 2.3 Scope distinction for the 3D separator

The detailed equation-by-equation procedure in the Fluent swirl chapter that separately establishes swirl momentum, freezes selected equations, and then restores all equations is written for **axisymmetric swirl**. The present separator is fully 3D, so that exact 2D procedure is **not** copied into this Stage-3 matrix as though it were directly prescribed for the current geometry.

The Stage-3 sweep uses only recommendations that can be defensibly applied or adapted to the present 3D case:

1. Mixture equation staging;
2. gradual flow/inertial loading as a numerical continuation strategy;
3. conservative momentum under-relaxation;
4. retention of `PRESTO!` and low slip under-relaxation.

The emphasis is intentionally not equal across those factors:

```text
M — Mixture equation staging
    strongest/direct cyclone recommendation

S — progressive inlet/inertial loading
    strong 3D continuation strategy adapted from Fluent swirl guidance

U — momentum under-relaxation
    secondary Fluent-guided stabilization sensitivity
```

The 12-case factorial is retained because the project currently wants a broad sweep, but interpretation should respect that hierarchy.

### 2.4 Standard k-epsilon → RNG k-epsilon is a separate Fluent-supported follow-up

Fluent's turbulence convergence guidance also states that, when using RNG `k-epsilon`, convergence may improve if a solution is first obtained with standard `k-epsilon` and then used as the starting point for RNG. Fluent notes that RNG introduces additional nonlinearities.

That recommendation is directly relevant to the promising Stage-2 `N5` observation. It strengthens the case for revisiting N5 later, but it does **not** become another factor in F01–F12. Stage 3 first asks whether the authoritative RNG/Mixture setup can be made useful through the cyclone/swirl startup strategies without changing turbulence-model form.

Official source:

- Ansys Fluent 2025 R2 User's Guide — *Solution Strategies for Turbulent Flow Simulations*, §16.19.3 Convergence:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_turb_solution.html>

---

## 3. Experimental question

Primary question:

> **Which combination of Fluent-recommended Mixture staging, gradual inlet/inertial loading, and momentum damping most effectively produces a developed, numerically useful full-geometry steady field without changing the physical boundary condition?**

For this project, a developed field means more than low residuals. The main evidence is split into two equally important classes:

1. **solver behaviour** — especially `k`, `epsilon`, continuity and momentum residual envelopes;
2. **project-core flow behaviour** — total inlet/outlet flow, phase routing once active, full-domain mass balance, and pressure behaviour at the brine-pipe entry.

A secondary question is:

> **After several thousand full-operating-condition iterations, do the `k` and `epsilon` residuals continue to diverge/expand, become bounded but oscillatory, or approach a progressively smaller stationary envelope while the pressure/flow histories also become stationary?**

This is more important than the value of a single final residual point.

---

## 4. Physical case held fixed

All Stage-3 branches preserve the 03A physical case:

```text
Fluent               = 2025 R2
Dimension             = 3D
Precision             = Double
Solver                = Pressure-Based
Time model            = Steady
Multiphase            = Mixture
Primary phase         = water vapour
Secondary phase       = liquid water
Turbulence authority  = RNG k-epsilon
Gravity               = [0, -9.81, 0] m/s²
Energy                = Off
Liquid patch          = None
DPM                   = Off
EWF                   = Off
Steam outlet          = Pressure Outlet, 1.120 MPa gauge
Brine outlet          = Pressure Outlet, 1.120 MPa gauge
Final inlet velocity  = 27.118 m/s on both split-inlet faces
```

The material properties, split-inlet geometry/compositions, wall treatment, boundary types and all remaining physical settings remain those of the verified 03A/08b-parity setup unless explicitly frozen below.

Stage 3 is **not** a brine-pressure experiment and does not qualify or modify 03B.

---

## 5. Frozen Stage-3 model and numerical fingerprint

The Stage-3 implementation should use a **parent + controlled delta** workflow rather than rebuilding every unchanged Fluent setting for every branch.

A branch may start from the canonical verified 03A pre-initialization parent or from an equivalent verified pre-initialization parent copy, provided that the frozen fingerprint below matches. Unchanged boundary conditions, materials and model settings should normally be left untouched in the parent and positively read back rather than rewritten unnecessarily.

Every branch summary must record the exact parent filename/artifact identifier used.

### 5.1 Mixture interaction settings

Freeze the current authoritative 03A interaction setup as:

| Mixture interaction item | Stage-3 state |
|---|---|
| Secondary-phase diameter | Constant `1.0e-5 m` |
| Slip-velocity model | `Manninen-et-al` |
| Drag coefficient | `Schiller-Naumann` |
| Drag modification | None |
| Surface-tension modelling | Continuum Surface Force |
| Surface-tension coefficient | Constant `0.04041 N/m` |
| Wall adhesion | Off |

Other Mixture interaction fields not explicitly listed above remain at their current Fluent/default parent state and must not be changed between branches. The preflight fingerprint should record their actual readback where exposed rather than relying on branch scripts to recreate defaults.

### 5.2 Turbulence and wall treatment

Freeze:

```text
RNG k-epsilon
Standard Wall Functions
Differential Viscosity Model = On
Swirl Dominated Flow         = On
```

All other expert turbulence controls and solution limits remain inherited from the verified parent and are recorded in the preflight readback.

### 5.3 Body-force treatment

The current 03A authority contains:

```text
Gravity / physical body force   = present
Body-force URF                  = 1.0
Implicit Body Force formulation = OFF
```

**Implicit Body Force remains OFF for F01–F12.**

It may be a useful later numerical test, but enabling it throughout Stage 3 would add another uncontrolled solver factor to a campaign that is specifically intended to isolate the Fluent cyclone/swirl startup recommendations.

### 5.4 Initialization

All branches use:

```text
Hybrid Initialization
Fluent default Hybrid Initialization settings
no localised turbulence initialization override
no liquid patch
```

Hybrid Initialization is performed exactly once per branch after branch-specific startup settings have been applied and read back.

Do **not** reinitialize at Mixture-equation transitions or inlet-loading transitions.

A future localised-turbulence-initialization study, if desired, is a separate companion experiment and is not part of F01–F12.

### 5.5 Common solution-method settings

Unless a branch definition explicitly changes a listed factor, retain:

| Numerical item | Stage-3 common setting |
|---|---|
| Pressure-velocity coupling | `SIMPLE` |
| Gradient | `Green-Gauss Node Based` |
| Pressure | `PRESTO!` |
| Momentum | `Second Order Upwind` |
| Volume fraction | `QUICK` |
| Turbulent kinetic energy | `Second Order Upwind` |
| Turbulent dissipation rate | `Second Order Upwind` |
| Pressure URF | `0.3` |
| Density URF | `1.0` |
| Body-force URF | `1.0` |
| Volume-fraction URF | `0.4` |
| `k` URF | `0.8` |
| `epsilon` URF | `0.8` |
| Slip / drift URF | `0.1` |
| Turbulent-viscosity URF | `1.0` |
| Pseudo-time | Off |
| Rhie-Chow high-order-term relaxation | Disabled |
| Operating pressure | `0 Pa` |
| Operating-density method | `mixture-averaged` |
| Implicit Body Force | Off |

Any exposed solution limits or expert controls not listed numerically above remain at the verified parent state and must be included in the branch preflight readback.

The existing slip/drift URF of `0.1` already satisfies Fluent's recommendation to begin at `0.2` or lower, so slip URF is **not** a Stage-3 factorial variable.

`PRESTO!` is retained in every branch because Fluent recommends it for steep rotational/swirl pressure gradients. It is therefore treated as a fixed best-practice setting rather than another matrix factor.

---

## 6. Experimental factors

### Factor M — Mixture-equation startup

Two levels:

**M0 — Full Mixture immediately**

```text
Volume Fraction = active
Slip Velocity   = active
```

from the first post-initialization iteration.

**M1 — Carrier-first Mixture staging**

```text
Volume Fraction = temporarily inactive
Slip Velocity   = temporarily inactive
```

Solve the remaining steady carrier-flow/turbulence field first. Then reactivate both equations **without reinitialization** and continue the full Mixture calculation.

This is the highest-priority Stage-3 factor because Fluent explicitly associates this method with difficult Mixture cases such as cyclone separation.

The M1 transition must not be judged from `k` and `epsilon` alone. Fluent's wording is to obtain a converged initial **flow field**. For this project, M1 therefore places heavy weight on the total-flow and pressure monitors as well as the carrier residuals before the preferred transition gate is considered satisfied.

### Factor S — progressive inlet/inertial loading

Two levels:

**S0 — Full-speed startup**

```text
27.118 m/s from the first iteration
```

**S1 — progressive inlet/inertial-loading ramp**

Use the project implementation of Fluent's approximate `10%` start / progressive-increase guidance:

| Ramp level | Velocity on each split inlet |
|---:|---:|
| 10% | `2.7118 m/s` |
| 20% | `5.4236 m/s` |
| 40% | `10.8472 m/s` |
| 80% | `21.6944 m/s` |
| 100% | `27.1180 m/s` |

The exact intermediate percentages are a **project adaptation**, not values prescribed verbatim by Fluent.

For this 3D spiral inlet, reducing inlet velocity is not a pure independent swirl control. It simultaneously changes both phase mass flows, Reynolds/inertial loading and centrifugal forcing. S1 is therefore interpreted as a **numerical continuation/homotopy strategy adapted from Fluent's gradual-swirl recommendation**.

Both split inlet faces must always use the same percentage of their authoritative final velocity so the intended phase-flow ratio and inlet geometry remain unchanged.

At every ramp level:

- preserve each inlet's turbulence intensity;
- preserve each inlet's hydraulic diameter;
- modify only the inlet velocity magnitude as the ramp variable;
- do not reinitialize after changing the velocity.

Only the final `100%` stage represents the intended physical operating condition. Lower-speed stages are numerical preconditioning states.

### Factor U — momentum under-relaxation

Three levels:

```text
U0 = 0.7   canonical 03A value
U1 = 0.5   moderate damping
U2 = 0.3   strong damping
```

The `0.3–0.5` levels are adapted from Fluent guidance for difficult strongly swirling/rotating flows. Because the current calculation is fully 3D, they are applied as the available global momentum URF rather than as separate axial/radial/swirl-specific values.

U is retained as a broad stabilization sensitivity, but it is interpreted as secondary to M and S.

For the initial Stage-3 matrix, the selected momentum URF remains active throughout the entire branch, including its final 100% operating-condition phase. Therefore U1/U2 are **alternative branch numerical controls**, not merely temporary startup values.

If the best Stage-3 branch uses `U1` or `U2`, it must later undergo a **return-to-authority continuation** with momentum URF restored to `0.7` before that field can become the canonical 03A parent for 03B. This return is a post-Stage-3 qualification test and is not another factor in F01–F12.

---

## 7. Full Stage-3 experiment matrix

The full matrix is:

```text
2 Mixture-startup levels
× 2 inlet/inertial-loading levels
× 3 momentum-URF levels
= 12 branches
```

| Case | Mixture startup | Inlet/inertial startup | Momentum URF | Primary comparison role |
|---|---|---|---:|---|
| `F01` | Full immediately | 100% immediately | `0.7` | long-run canonical control |
| `F02` | Carrier-first staged | 100% immediately | `0.7` | isolate direct Fluent Mixture staging |
| `F03` | Full immediately | 100% immediately | `0.5` | isolate moderate momentum damping |
| `F04` | Carrier-first staged | 100% immediately | `0.5` | Mixture staging + moderate damping |
| `F05` | Full immediately | 100% immediately | `0.3` | isolate strong momentum damping |
| `F06` | Carrier-first staged | 100% immediately | `0.3` | Mixture staging + strong damping |
| `F07` | Full immediately | 10→20→40→80→100% | `0.7` | isolate progressive inlet/inertial loading |
| `F08` | Carrier-first staged | 10→20→40→80→100% | `0.7` | combine the two principal Fluent-guided staging strategies |
| `F09` | Full immediately | 10→20→40→80→100% | `0.5` | loading ramp + moderate damping |
| `F10` | Carrier-first staged | 10→20→40→80→100% | `0.5` | combined recommendations with moderate damping |
| `F11` | Full immediately | 10→20→40→80→100% | `0.3` | loading ramp + strong damping |
| `F12` | Carrier-first staged | 10→20→40→80→100% | `0.3` | most conservative combined strategy |

No Stage-2 result is used to remove branches from this matrix. In particular, the promising standard-`k-epsilon` behaviour in N5 is retained as an important clue only.

---

## 8. Parent, inheritance and initialization rule

The Stage-3 matrix is intended to test **startup strategy**, so branches must not begin from the Stage-1 iteration-1000 field or from an N1/N3/N4/N5 developed solution.

Preferred parent model:

```text
verified 03A full-geometry pre-initialization case
with the frozen Stage-3 fingerprint already present
```

It is useful to retain more than one verified pre-initialization parent artifact/copy for operational flexibility. A parent alternative is acceptable only if its readback matches the same Stage-3 frozen fingerprint. Parent alternatives are not distinct experimental factors.

For each branch:

1. load one verified immutable pre-initialization 03A parent;
2. record the exact parent artifact identifier;
3. verify the frozen Stage-3 fingerprint;
4. leave unchanged boundary conditions/material/model settings untouched wherever possible;
5. apply the branch-specific momentum URF;
6. apply the branch-specific initial inlet velocity;
7. apply M0 or M1 equation state;
8. positively read back every changed setting and all critical fingerprint fields;
9. Hybrid Initialize once using Fluent's default Hybrid Initialization settings;
10. execute the evidence-gated / forced-progression branch schedule below;
11. never reinitialize between stages of the same branch;
12. save a paired case/data checkpoint at every stage transition.

This avoids unnecessary reconstruction of settings already carried correctly by the parent while still preventing hidden differences between branches.

### 8.1 Shared P0 and reusable schedule seeds for parallel execution

For the three-session production campaign, setup preparation should be centralized before long runs begin. The detailed machine-readable construction and release contract is maintained in [`03a-stage3-shared-parent-and-seed-spec.yaml`](./03a-stage3-shared-parent-and-seed-spec.yaml). Where execution-preparation details are repeated here, they should remain consistent with that YAML.

Create one authoritative monitor-ready, pre-initialization Stage-3 parent:

```text
03A-stage3-P0-monitor-ready-preinit.cas.h5
```

P0 is the common scientific authority. It must remain immutable, uninitialized and solution-free once its frozen Stage-3 fingerprint and monitor definitions have been verified.

To reduce repeated setup work across the three independent Fluent computers, derive only four reusable **pre-initialization schedule seeds** from P0:

```text
SEED-A-M0-S0  full Mixture + 100% inlet
SEED-B-M1-S0  carrier-first + 100% inlet
SEED-C-M0-S1  full Mixture + 10% inlet
SEED-D-M1-S1  carrier-first + 10% inlet
```

These four seeds encode only the M/S startup state. They remain uninitialized and are operational conveniences rather than new scientific parents.

The 12 experiment branches are then produced by copying the appropriate reusable seed and applying only the branch momentum-URF delta:

```text
SEED-A + U0/U1/U2 → F01 / F03 / F05
SEED-B + U0/U1/U2 → F02 / F04 / F06
SEED-C + U0/U1/U2 → F07 / F09 / F11
SEED-D + U0/U1/U2 → F08 / F10 / F12
```

with:

```text
U0 = 0.7
U1 = 0.5
U2 = 0.3
```

A persistent `F##-preinit` case may still be saved after the U delta is applied and read back if operationally useful, but it is not necessary to pre-build twelve elaborate independent seeds. Every branch remains scientifically:

```text
P0
+ documented M/S schedule seed
+ documented U delta
```

The shared OneDrive location is the common artifact exchange so all three independent Fluent computers can access P0 and the same four verified schedule seeds. For production solving, each agent copies the selected seed into that computer's local run directory, applies and verifies the branch U delta, and allows Fluent-native autosave/checkpointing to operate locally. Completed stage/checkpoint artifacts can then be synchronized back to the shared location. Avoid simultaneous Fluent writes from several computers to the same shared file path.

Before releasing P0/seeds for production, use a disposable copy of P0 for a short monitor smoke test. Verify that every required residual, flow, pressure and liquid-inventory history records non-empty temporal data and behaves correctly across save/reload. Never turn the smoke-test solution into P0 or one of the shared seeds.

---

## 9. Evidence-driven stage-transition rule

### 9.1 Intent of the transition gate

The transition gate is a **preferred progression rule**, not a termination rule.

The purpose is to follow Fluent's recommendation to develop the simplified field before introducing more difficult equations/loading. However, Stage 3 is also an experiment. If a simplified stage refuses to satisfy the preferred gate, that itself is useful evidence, but the project still wants to discover what happens when the next part of the Fluent strategy is applied.

Therefore:

```text
preferred behaviour:
    advance when the field demonstrates development/stabilisation

fallback behaviour:
    if no preferred pass is obtained by 3,000 iterations,
    save the evidence and advance anyway unless a hard numerical failure occurred
```

This ensures that every non-crashed branch gets at least one complete path to the final 100% operating condition.

### 9.2 Evaluation windows

The first transition-gate evaluation cannot occur before at least `750` iterations have accumulated in the current stage.

After iteration 750, evaluate every `250` additional iterations using the most recent `750`-iteration window.

Split each 750-iteration window into:

```text
first comparison block = first 250 iterations
middle block           = middle 250 iterations
final comparison block = final 250 iterations
```

The gate contains three evidence groups:

```text
A. turbulence behaviour
B. carrier residual behaviour
C. project-core flow / pressure behaviour
```

M1 in particular is not allowed to claim a preferred `PASS` based only on turbulence residuals.

### 9.3 A — turbulence gate: k and epsilon

For each of `k` and `epsilon`, analyse the most recent 750 iterations in `log10(residual)` space.

Calculate at minimum:

```text
median
P05
P95
maximum
log-envelope width = log10(P95 / P05)
```

A turbulence residual is considered improving/stabilising when **at least one** of the following is true:

1. **decreasing level** — final-250 median is at least approximately `10%` lower than first-250 median; or
2. **reduced jumping/variability** — final-250 log-envelope width is at least approximately `15%` smaller than first-250 log-envelope width.

A preferred pass is rejected if the same residual simultaneously deteriorates materially:

```text
final-250 median > first-250 median by more than 20%
OR
final-250 P95    > first-250 P95 by more than 20%
```

Both `k` and `epsilon` must independently satisfy this gate for a preferred transition. `epsilon` therefore still has effective veto power within the turbulence group.

These percentages are **project transition criteria**, not Fluent convergence criteria. Their purpose is to make the staged decision reproducible.

### 9.4 B — carrier residual gate: continuity and momentum

The simplified field should also look like a developing carrier solution rather than a turbulence-only improvement sitting on top of an unstable pressure/velocity field.

Track:

```text
continuity
x-momentum
y-momentum
z-momentum
```

The preferred carrier-residual gate does not demand that all four reach final convergence thresholds during preconditioning. Instead it asks that they are **bounded and non-expanding**, with no repeated evidence that the pressure/velocity field is becoming progressively less stable.

At minimum, over the same 750-iteration window:

- continuity final-250 median and P95 must not both worsen by more than approximately `20%` relative to the first-250 block;
- each momentum residual must remain finite and bounded rather than entering an expanding envelope;
- a clear downward trend is favourable but is not mandatory if the residuals have already entered a stable bounded band.

This deliberately keeps the gate less strict than a final convergence test. The objective is to decide whether the carrier field is developed enough to justify the next continuation step.

### 9.5 C — project-core flow / pressure gate

For this project, this group is as important as the residual gate.

The key monitors are:

```text
total mixture inlet flow
total mixture outlet flow
steam-outlet total flow
brine-outlet total flow
full-domain mass imbalance and relative imbalance
brine-pipe-entry static pressure
brine-pipe-entry total pressure
```

When the full Mixture equations are active, also include:

```text
liquid → brine outlet
liquid → steam outlet
vapour → brine outlet
vapour → steam outlet
total domain liquid inventory
Y010 / Y030 liquid inventory diagnostics
```

During an M1 carrier-only interval, phase-specific outlet fluxes and liquid-inventory behaviour are recorded where Fluent exposes them but are **not required positive gate variables**, because Volume Fraction and Slip Velocity are intentionally inactive. The carrier-only preferred gate therefore concentrates on total flow, balance and pressure.

At each fixed equation/loading state, the flow/pressure field is considered developed enough for a preferred transition when the recent histories are becoming stationary or clearly approaching stationarity. The gate should look for:

- outlet-flow medians changing less between the first and final 250-iteration blocks;
- pressure medians at the brine-pipe entry changing less between those blocks;
- shrinking variability/envelope of those signals;
- relative mass imbalance improving or at minimum not entering a progressively expanding regime;
- no non-finite/corrupted monitor values.

For automated screening, use the following initial project rules:

```text
flow/pressure stationarity signal:
    |final-250 median - first-250 median| / representative magnitude <= ~5%
    OR variability/envelope reduces by >= ~15%

mass-balance non-deterioration:
    final-250 relative-imbalance median is not > first-250 median by > ~20%
```

These are **transition heuristics**, not physical acceptance criteria. They may be tuned after the monitor smoke test if they prove too sensitive to normal cyclone oscillation.

For S1 ramp stages, absolute flow and pressure values at 10%, 20%, 40% and 80% are not compared with the final 100% operating targets. Each stage is judged only for stationarity/development at its own imposed loading.

### 9.6 Preferred transition decision

A stage receives a preferred `PASS` when:

```text
k gate                  = PASS
epsilon gate            = PASS
carrier residual gate   = PASS
flow / pressure gate    = PASS
hard numerical failure  = NO
```

For full-Mixture stages, phase-flow and liquid-inventory histories are included in the qualitative supporting evidence and can prevent a preferred pass if they are clearly unbounded/corrupted.

The intent is not to create an impossibly strict mini-convergence test at every ramp point. The intent is to avoid introducing the next difficulty while the current pressure/flow field is obviously still developing violently.

### 9.7 Hard failure versus soft warning

Only a **hard numerical failure** prevents the forced full-sequence experiment from continuing:

- Fluent FPE;
- unrecoverable AMG divergence / solver termination;
- non-finite solution/monitor values that make the state unusable;
- loss of a valid case/data checkpoint from which continuation is possible.

The following are important warnings but are not automatically terminal before the 3,000-iteration forced-progression point:

- expanding continuity that remains finite;
- poor or worsening mass imbalance;
- persistent reverse flow;
- turbulent-viscosity limiting;
- drifting outlet flows;
- drifting brine-entry pressure;
- poor `k`/`epsilon` gate behaviour.

Those warnings are recorded in the branch evidence. The deliberate reason for not terminating immediately is that Stage 3 wants to learn whether the **next continuation step can rescue or reorganise the field**.

### 9.8 STAGE_STALLED and forced progression

A stage must not be labelled stalled before at least `2,000` iterations have been attempted at the current state.

From `2,000` onward, if repeated 750-iteration windows show no meaningful improvement or show deterioration, mark the stage provisionally:

```text
STAGE_STALLED
```

However, `STAGE_STALLED` is a diagnostic label, **not a branch-stop command**.

Continue the same state until either:

1. the preferred transition gate passes; or
2. the stage reaches `3,000` iterations without a preferred pass.

At `3,000` iterations, if there is still no preferred pass but no hard numerical failure has occurred:

```text
save checkpoint
record final failed gate statistics
classify transition = FORCED_ADVANCE_AT_3000
advance to the next planned equation/loading state
```

This is a deliberate experimental choice. It sacrifices some purity of the Fluent "converge first, then advance" recommendation in order to ensure that every viable branch receives a full end-to-end test. The report must therefore distinguish clearly between:

```text
PREFERRED_PASS_ADVANCE
FORCED_ADVANCE_AT_3000
```

A branch that required forced progression is not interpreted as equivalent to one that passed naturally.

---

## 10. Evidence-gated / forced-progression branch schedules

Every branch must accumulate at least `5,000` iterations at the final physical operating condition unless a hard numerical failure prevents it.

Low-speed or carrier-only preconditioning iterations do **not** count toward that final 5,000-iteration minimum.

### Schedule A — M0 + S0

Applies to `F01`, `F03`, `F05`.

```text
Hybrid Initialize
→ full Mixture active
→ inlet = 27.118 m/s
→ final 100% operating-condition phase
→ minimum 5,000 steady iterations
→ continue according to final-stage rule
```

There is no intermediate transition gate because no equations/loading states are staged before the final condition.

### Schedule B — M1 + S0

Applies to `F02`, `F04`, `F06`.

```text
Hybrid Initialize
→ Volume Fraction OFF
→ Slip Velocity OFF
→ inlet = 27.118 m/s
→ carrier-only stage
→ evaluate preferred whole-field gate from iteration 750 onward
→ preferred PASS at any evaluation:
     checkpoint and enable Volume Fraction + Slip Velocity
→ otherwise continue carrier-only through iteration 3,000
→ if still no PASS at 3,000 and no hard failure:
     checkpoint + FORCED_ADVANCE_AT_3000
     enable Volume Fraction + Slip Velocity
→ no reinitialization
→ final 100% full-Mixture phase
→ minimum 5,000 iterations
→ continue according to final-stage rule
```

The carrier-only stage is therefore long enough to test Fluent's intended preconditioning properly, but it cannot prevent the branch from ever reaching the full Mixture operating condition.

### Schedule C — M0 + S1

Applies to `F07`, `F09`, `F11`.

```text
Hybrid Initialize at 10%
→ full Mixture at 10%
→ preferred whole-field gate PASS OR forced advance at 3,000
→ checkpoint
→ 20%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 40%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 80%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 100%
→ minimum 5,000 final-condition iterations
→ continue according to final-stage rule
```

The full Mixture equations remain active throughout.

There is no predetermined short duration for a ramp level. A stage advances as soon as it demonstrates development, but a non-crashed stage is forced forward after 3,000 iterations so the entire homotopy path is tested.

### Schedule D — M1 + S1

Applies to `F08`, `F10`, `F12`.

Project synthesis of the two Fluent recommendations:

```text
Hybrid Initialize at 10%
→ Volume Fraction OFF + Slip Velocity OFF
→ carrier-only at 10%
→ preferred whole-field gate PASS OR forced advance at 3,000
→ checkpoint
→ Volume Fraction ON + Slip Velocity ON
→ no reinitialization
→ full Mixture at 10%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 20%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 40%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 80%
→ preferred gate PASS OR forced advance at 3,000
→ checkpoint
→ 100%
→ minimum 5,000 final-condition iterations
→ continue according to final-stage rule
```

This exact combined ordering is a **project experimental synthesis** of the two Fluent guides. Fluent recommends both strategies independently but does not prescribe this exact 3D combined schedule.

---

## 11. Final 100% operating-condition rule

`5,000` final-condition iterations are a **minimum observation window**, not an automatic stopping definition.

Unlike an intermediate preconditioning stage, the final stage has no next state to unlock. Every branch that reaches 100% without hard numerical failure should therefore be allowed to complete the full 5,000-iteration minimum even if the field looks poor early in that interval.

At and beyond 5,000 final-condition iterations:

1. evaluate the rolling 750-iteration turbulence, carrier-residual and flow/pressure metrics every 250 iterations;
2. if the field is still showing meaningful improvement in residual level, residual variability, flow balance or monitor stationarity, **continue beyond 5,000**;
3. do not stop merely because iteration 5,000 has been reached;
4. if the field becomes bounded and no longer materially improves over repeated windows, classify the final state according to its stationary behaviour rather than forcing iterations indefinitely;
5. if the field is poor but finite, retain the complete 5,000-iteration evidence and classify it accordingly;
6. terminate before 5,000 only for a hard numerical failure.

A branch can therefore finish at 5,000, 6,500, 8,000, 10,000+ final-condition iterations depending on what the actual histories show.

No branch is considered better merely because it produces one unusually low endpoint residual.

### Final numerical-state labels

Use at least:

```text
CONVERGING
BOUNDED_LOW_VARIABILITY
BOUNDED_OSCILLATORY
SLOW_DRIFT
EXPANDING_OSCILLATION
STAGE_STALLED
FORCED_ADVANCE_AT_3000
NUMERICAL_FAILURE
```

A bounded oscillatory field may still be useful if the pressure/flow and inventory histories are stationary enough to support a steady-RANS interpretation.

---

## 12. Required monitoring

Every branch must capture continuous histories, not only endpoint snapshots.

### Solver histories

Record:

- continuity scaled residual;
- x/y/z momentum scaled residuals;
- liquid volume-fraction residual when active;
- `k` residual;
- `epsilon` residual;
- turbulent-viscosity limiting warnings/count/region where available;
- reversed-flow warnings and affected outlet faces where available.

When Volume Fraction / Slip Velocity are disabled, the report must clearly mark the corresponding interval rather than plot it as missing or zero convergence data.

### Project-core flow and pressure histories

These are not secondary diagnostics. They are a core part of the Stage-3 convergence judgement.

Record throughout:

- liquid inlet mass flux;
- vapour inlet mass flux;
- total mixture inlet mass flux;
- total steam-outlet mass flux;
- total brine-outlet mass flux;
- total mixture outlet mass flux;
- full-domain mass imbalance and relative imbalance;
- brine-pipe-entry static pressure;
- brine-pipe-entry total pressure.

When full Mixture equations are active, also record:

- liquid → brine outlet;
- liquid → steam outlet;
- vapour → brine outlet;
- vapour → steam outlet;
- total domain liquid inventory;
- Y010 liquid inventory as a diagnostic only;
- Y030 liquid inventory as a diagnostic only.

The Stage-2 reporting gap where temporal liquid-inventory monitor arrays were empty must not be repeated in Stage 3.

Before production submission, run a short monitor smoke test and verify that every required monitor actually records non-empty temporal data and survives save/reload where applicable. A branch with missing required monitor histories fails preflight.

---

## 13. Analysis windows and transition artifacts

For each branch, preserve stage boundaries and evaluate at least:

- every 750-iteration preferred-gate window;
- iteration 2,000 stall-assessment point where reached;
- iteration 3,000 forced-transition point where reached;
- each preconditioning/ramp stage endpoint;
- first `100` iterations after every major equation/inlet-speed transition;
- final `1,000` iterations of the 100% operating-condition phase;
- final `2,000` iterations where available;
- full final-condition history.

For every transition-gate evaluation, store:

### Turbulence metrics

For both `k` and `epsilon`:

```text
iteration range
median
P05
P95
maximum
log-envelope width
first-250 vs final-250 median change
first-250 vs final-250 envelope-width change
first-250 vs final-250 P95 change
PASS / FAIL
reason
```

### Carrier residual metrics

For continuity and x/y/z momentum:

```text
first-250 median / P95
final-250 median / P95
trend classification
bounded / expanding classification
PASS / FAIL
reason
```

### Flow / pressure metrics

For the applicable total-flow, balance and brine-entry-pressure monitors:

```text
first-250 median
final-250 median
first-250 variability
final-250 variability
relative median change
variability change
stationary / improving / drifting / expanding classification
PASS / FAIL
reason
```

For final-condition reporting, also include trend/slope of rolling median and rolling P95 over longer windows.

The analysis should distinguish:

```text
converging envelope
bounded low-variability state
bounded stationary oscillation
slow drift
intermittent spikes
expanding/diverging envelope
numerical failure
```

Every stage transition must record whether it occurred because of:

```text
PREFERRED_PASS_ADVANCE
or
FORCED_ADVANCE_AT_3000
```

---

## 14. Primary comparison logic

The 12-case matrix allows direct estimates of:

### Mixture staging effect — primary/direct Fluent cyclone comparison

Compare:

```text
F01 vs F02
F03 vs F04
F05 vs F06
F07 vs F08
F09 vs F10
F11 vs F12
```

### Progressive inlet/inertial-loading effect — strong continuation comparison

Compare:

```text
F01 vs F07
F02 vs F08
F03 vs F09
F04 vs F10
F05 vs F11
F06 vs F12
```

### Momentum damping effect — secondary numerical sensitivity

Within a common startup strategy compare:

```text
0.7 vs 0.5 vs 0.3
```

for example:

```text
F01 vs F03 vs F05
F02 vs F04 vs F06
F07 vs F09 vs F11
F08 vs F10 vs F12
```

### Interaction effects

Determine whether the recommendations act independently or whether, for example, Mixture staging is only useful when combined with gradual loading and/or lower momentum URF.

Because staged branches may require different numbers of preconditioning iterations, comparisons must be made primarily over the **100% final-condition histories**, not by comparing the same absolute global iteration number.

Also compare how often each strategy reaches later stages by preferred passes versus forced 3,000-iteration transitions. A method that reaches 100% only through repeated forced advances is qualitatively different from one whose intermediate fields naturally settle.

---

## 15. Stage-3 success criteria

Stage 3 is not required to produce a perfectly textbook residual curve.

A branch is **numerically promising** if, over the long final-condition window:

- `k` and `epsilon` residual envelopes are substantially smaller and more bounded than the Stage-1 reference;
- continuity and momentum residuals are bounded rather than progressively expanding;
- total inlet/outlet flow histories approach stationary means;
- full-domain imbalance trends materially downward or becomes bounded;
- brine-pipe-entry static and total pressure histories approach stationary means or bounded repeatable regimes;
- phase-flux histories, when active, approach stationary means or bounded repeatable regimes;
- liquid inventory does not exhibit an unbounded secular drift inconsistent with the outlet fluxes;
- turbulent-viscosity limiting and reverse-flow behaviour do not progressively spread in a manner consistent with numerical breakdown;
- there is no FPE/AMG numerical breakdown.

A branch can be useful even if residuals remain oscillatory, provided the oscillation is bounded and the physical monitor histories are stationary enough to justify a steady-RANS interpretation.

A branch is **not** qualified solely because:

- it survives the requested iteration count;
- one residual reaches the nominal criterion once;
- an endpoint flux snapshot looks favourable;
- `k`/`epsilon` look quieter while total flow, balance or pressure continues to drift;
- it has lower residuals while equations or operating conditions are still intentionally simplified.

---

## 16. Relationship to N1/N3/N4/N5 and the intended Stage-3B follow-up

Stage 3 does not discard Stage 2.

Stage-2 evidence currently suggests:

- `N1` reduced turbulence URFs did not improve the long available continuation;
- `N3` first-order turbulence transport changed the solution and did not clearly settle the turbulence field;
- `N4` broader first-order startup did not provide convincing available endpoint behaviour;
- `N5` standard `k-epsilon` bootstrap gave the clearest short-window numerical improvement, but the improvement did not survive the available return to RNG.

The N5 observation is now considered especially important because Fluent independently recommends standard `k-epsilon` → RNG `k-epsilon` as a possible RNG convergence strategy.

Nevertheless, F01–F12 remain the immediate campaign because:

1. Mixture equation staging is directly recommended for cyclone separation;
2. the Stage-2 interventions were not the complete Fluent cyclone/swirl startup sweep;
3. Stage-2 continuation windows were shorter than the Stage-3 convergence horizon;
4. Stage 3 first asks whether the canonical RNG model can be made useful without changing turbulence-model form.

The intended hierarchy is therefore:

```text
Stage 3A
    F01–F12 Fluent cyclone/swirl startup sweep with RNG retained

then, if needed:

Stage 3B
    take the best Stage-3A startup strategy
    → longer standard k-epsilon bootstrap
    → controlled return to RNG k-epsilon
    → long final-condition qualification
```

If RNG remains fundamentally troublesome even after that, turbulence-model suitability becomes the next explicit scientific question rather than another ad-hoc numerical tweak.

---

## 17. Out-of-scope changes for the F01–F12 sweep

Do not add the following as extra factors during the initial Stage-3 matrix:

- brine-outlet pressure;
- steam-outlet pressure;
- liquid patching;
- transient formulation;
- standard `k-epsilon` as the final model;
- RSM;
- first-order momentum/turbulence discretization;
- altered `k` or `epsilon` URFs;
- altered slip URF;
- Coupled solver;
- pseudo-time;
- Implicit Body Force changes;
- localised-turbulence-initialization changes;
- DPM;
- EWF.

Those remain possible later experiments, but adding them now would prevent a clean interpretation of the Fluent-recommended staging sweep.

---

## 18. Execution artifact requirements

Every branch should produce a self-contained artifact set containing at least:

```text
parent artifact identifier
case checkpoint before initialization
preflight Stage-3 fingerprint/readback
Fluent multiphase/model summary where available
case/data checkpoint at each stage transition
transition-gate JSON/Markdown at each gate decision
final case/data endpoint
native Fluent journal/transcript
settings readback before first iteration
settings readback at every equation/ramp transition
residual history
phase-flux history
mass-balance history
liquid-inventory history
brine-entry pressure history
warning/event log
branch summary JSON/Markdown
```

The branch summary must record the actual number of iterations completed at every stage rather than infer lineage from filenames.

At every transition, save:

```text
checkpoint before transition
750-iteration gate statistics
turbulence gate result
carrier residual gate result
flow / pressure gate result
transition type: PREFERRED_PASS_ADVANCE or FORCED_ADVANCE_AT_3000
settings before transition
settings after transition
new stage start iteration
```

This makes later instability traceable to the exact equation/loading change that preceded it.

---

## 19. Three-session execution distribution

Stage 3 is intended to use **three independent Fluent sessions in parallel**. The distribution below is an execution plan only; it does not change the scientific meaning or lineage of F01–F12.

The governing rule is:

> **Agents own Fluent sessions; Fluent sessions do not own scientific cases.**

`server_id` / session number is only a connection-routing detail. It may appear in transient operational diagnostics or agent instructions, but it must not be used as the branch identity and should not be embedded in scientific case names, report filenames, setup lineage, result JSON, or interpretation.

### 19.1 Initial agent/session queues

Use the following initial queues:

| Fluent session | Assigned queue | Reason for grouping |
|---|---|---|
| **Session 1 — actively monitored by the user** | `F08 → F10 → F12` | all Schedule-D `M1 + S1` branches; highest number of equation/loading transitions and therefore the most useful branches to supervise interactively |
| **Session 2** | `F01 → F07 → F03 → F09` | starts with the canonical long control, then covers ramp-only and moderate-damping branches |
| **Session 3** | `F02 → F04 → F11 → F06 → F05` | starts with the direct Fluent Mixture-staging branch, then covers complementary staged and strong-damping branches |

This gives the first parallel launch:

```text
Session 1: F08   combined Mixture staging + progressive loading
Session 2: F01   canonical long control
Session 3: F02   direct Fluent Mixture-staging comparison
```

The first batch therefore gives early visibility on the central `F01 ↔ F02` comparison while the user-supervised session exercises the most transition-heavy combined strategy.

### 19.2 Agent ownership rule

Each execution agent owns exactly one Fluent endpoint/session during its assigned work. Apart from the endpoint and queue, the agents should follow the same Stage-3 execution contract.

For every queued branch, the agent must:

1. obtain the correct verified reusable schedule seed (`A/B/C/D`) and apply the documented branch momentum-URF delta, or reproduce the same starting state from verified P0 if the seed is unavailable;
2. establish branch identity from the explicitly loaded artifact and branch definition, never from `server_id`;
3. verify the Stage-3 frozen fingerprint, seed M/S state and branch-specific U value before initialization;
4. copy the selected seed/branch input to a local run directory on that Fluent computer before production solving;
5. Hybrid Initialize exactly once;
6. verify Fluent-native autosave/checkpoint configuration before the long run;
7. execute the branch schedule and evidence gates defined in Sections 9–11;
8. save/checkpoint before every equation/loading transition;
9. record `PREFERRED_PASS_ADVANCE`, `STAGE_STALLED`, `FORCED_ADVANCE_AT_3000`, or hard numerical failure as applicable;
10. complete the minimum 5,000 final-condition iterations unless a hard numerical failure prevents it;
11. return the complete branch artifact set defined in Section 18;
12. then move to the next unstarted branch in that session's queue.

An agent must not reinterpret its queue as a new setup grouping. For example, `F08` remains `F08` regardless of whether it happens to run on Session 1, Session 2, or a replacement endpoint after recovery.

### 19.3 Queue flexibility

The queue above is the preferred starting distribution, not a permanent case/server binding.

Before the full production matrix, it is acceptable to perform a short **non-scientific hardware throughput smoke test** from disposable copies of the same verified seed on all three computers. Those runs must be clearly labelled as execution benchmarks and must not be included as F01–F12 scientific results.

If one machine is materially faster or a session becomes unavailable, any **unstarted** branch may be moved to another session to improve throughput. Moving a branch changes only operational ownership; its parent, branch definition, settings, evidence requirements and scientific identity remain unchanged.

Do not casually move an already-running branch between live sessions. If recovery on another computer is required, resume only from a verified complete case/data checkpoint and preserve the exact branch/stage/iteration provenance.

### 19.4 Parallel-execution reporting boundary

A lightweight operational board may record information such as:

```text
Session 1 — F08 — full Mixture 10% — current stage iteration 1450
Session 2 — F01 — final 100% — current stage iteration 3200
Session 3 — F02 — carrier-only — current stage iteration 2250
```

That board is execution state only.

The scientific branch artifacts and reports should remain organized by:

```text
F##
parent artifact
controlled delta
stage history
case/data checkpoints
monitor evidence
final classification
```

not by the computer or server that happened to run them.

### 19.5 Overall execution priority

The full matrix is still intended to be completed. If early visibility is needed beyond the first three parallel branches, retain the original scientific priority inside the available queues:

```text
highest early-value branches:
F01  canonical long control
F02  direct Fluent Mixture staging only
F07  inlet/inertial ramp only
F08  both principal Fluent-guided staging recommendations

then:
F03/F04/F09/F10  moderate momentum damping variants

then:
F05/F06/F11/F12  strongest damping variants
```

The three-session allocation is intended to reduce wall-clock experiment time without changing that interpretation hierarchy or authorizing early termination of the 12-case sweep.

---

## 20. Decision after Stage 3

Once the full sweep is available, classify the outcome into one of the following directions.

### A — one or more RNG branches become clearly usable

Use the best Fluent-guided startup strategy as the candidate numerical parent for subsequent 03A qualification and eventual 03B pressure continuation.

If that candidate uses momentum URF `0.5` or `0.3`, first restore:

```text
Momentum URF = 0.7
```

without reinitialization and evaluate the continuation using the same long-window residual and flow/pressure evidence before declaring it a canonical 03A parent.

### B — RNG remains bounded but persistently oscillatory while physical monitors are stationary

Assess whether the steady-RANS solution should be interpreted statistically/boundedly rather than demanding monotonic residual collapse, and determine whether a transient/RANS comparison is required.

### C — no RNG branch becomes sufficiently useful, but the N5 standard bootstrap remains markedly better

Launch the predeclared Stage-3B turbulence-bootstrap campaign from the best Stage-3A startup strategy:

```text
best Stage-3A startup method
→ standard k-epsilon bootstrap
→ controlled RNG return
→ long final-condition qualification
```

This directly tests the separate Fluent RNG convergence recommendation rather than treating N5 as an isolated anomaly.

### D — all F01–F12 branches remain numerically unusable

Use the full Stage-3 evidence to choose targeted follow-up numerical tests that were deliberately excluded from the factorial, especially:

- Implicit Body Force formulation;
- localised turbulence initialization;
- turbulence-model suitability / Stage-3B N5 follow-up;
- whether a steady solution exists for the current model.

---

## 21. Remaining execution-implementation checks

The scientific decisions in this plan are now mostly resolved. Before production execution, verify only the implementation details needed to make the plan reproducible:

- exact Fluent/PyFluent commands for toggling `Volume Fraction` and `Slip Velocity` independently in the active 2025 R2 Mixture case;
- whether the current gRPC execution layer can modify both split-inlet velocities safely between continuation stages without reinitialization;
- that inlet turbulence intensity/hydraulic-diameter values remain unchanged when velocity is ramped;
- creation and verification of the shared monitor-ready P0 parent and four reusable `A/B/C/D` pre-initialization schedule seeds, including branch-specific U readback before initialization;
- branch/checkpoint naming convention;
- persistence and reload behaviour for residual, liquid-inventory, phase-flux and brine-entry-pressure histories;
- calculation of the automated 750-iteration turbulence/carrier/flow-pressure gate metrics;
- checkpoint/save behaviour before every transition;
- explicit recording of `PREFERRED_PASS_ADVANCE`, `STAGE_STALLED`, `FORCED_ADVANCE_AT_3000`, and hard numerical failure;
- confirmation that the forced-progression scheduler never skips the final 5,000-iteration operating-condition phase unless Fluent genuinely fails numerically;
- verification that each of the three agents can independently connect to its assigned endpoint, load the same shared seed lineage, and write only to its own local run workspace.

No scientific conclusion should be attached to Stage 3 until the full-condition histories have been analysed.