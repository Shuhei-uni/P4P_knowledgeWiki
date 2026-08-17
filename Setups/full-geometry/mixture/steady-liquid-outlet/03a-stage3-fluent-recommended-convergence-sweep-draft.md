# 03A Stage 3 — Fluent-Recommended Convergence Sweep (Draft)

> **Status:** draft — scientific design substantially resolved; execution implementation still requires smoke-test verification  
> **Setup family:** `03A` full-geometry steady Mixture baseline  
> **Purpose:** perform a broad, long-duration numerical convergence sweep based directly on Ansys Fluent guidance for difficult Mixture/cyclone and strongly swirling flows before narrowing onto any one turbulence-model or solver-rescue strategy.  
> **Physical case:** unchanged from 03A — same geometry, materials, phase definitions, split inlet, outlet pressures, gravity, and no liquid patch.  
> **Parent authority:** a verified 03A pre-initialization case with the frozen Stage-3 fingerprint defined below. Branches must not begin from an already-developed Stage-1/Stage-2 solution field unless a later setup explicitly defines that as a separate experiment.

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

> Before changing the physical model or committing to a different turbulence model, test whether a difficult cyclone/Mixture field becomes substantially more stable when Fluent's own staged-solution recommendations are applied over a sufficiently long, evidence-driven iteration history.

The important Stage-3 change from the earlier screening work is that staged branches are **not advanced according to a fixed iteration count**. The field must demonstrate improving or stabilising `k` and `epsilon` behaviour before additional equations or inlet loading are introduced.

---

## 2. Fluent guidance being tested

Stage 3 is built from two official Ansys Fluent guidance sources for Fluent 2025 R2.

### 2.1 Mixture-model solution strategy

Fluent's multiphase solution guidance states that, for some Mixture-model cases **including cyclone separation**, an initial solution can be obtained more easily by temporarily disabling the:

- `Volume Fraction` equation;
- `Slip Velocity` equation;

then converging the remaining flow field, restoring those equations, and continuing the full Mixture solution.

The same guidance recommends beginning a Mixture calculation with a **slip-velocity under-relaxation factor of `0.2` or lower** and only increasing it if convergence is good.

Official source:

- Ansys Fluent 2025 R2 User's Guide — *Solution Strategies for Multiphase Modeling*, §27.8.2.2 Mixture Model:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html>

### 2.2 Strong swirl / rotating-flow solution strategy

Fluent's swirl/rotation guidance recommends, for difficult pressure-based segregated calculations:

- using `PRESTO!` for steep rotational/swirl pressure gradients;
- lowering velocity under-relaxation when necessary, with approximately `0.3–0.5` given as a useful range in difficult rotating/swirl guidance;
- beginning from a lower rotational or inlet-swirl intensity and gradually increasing toward the final operating condition.

The guide gives approximately `10%` of the final operating condition as a possible initial level and suggests increasing the rotational/swirl speed progressively, for example by roughly doubling between stages.

Official sources:

- Ansys Fluent 2025 R2 User's Guide — *Swirling and Rotating Flows* / related solution guidance:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug.html>
- Ansys Fluent 2025 R2 User's Guide — *Flow in Single Moving Reference Frames*, gradual rotational-speed strategy:  
  <https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_th_sec_srf_fjk.html>

### 2.3 Important scope distinction

The detailed equation-by-equation procedure in the Fluent swirl chapter that separately establishes swirl momentum, freezes selected equations, and then restores all equations is written for **axisymmetric swirl**. The present separator is fully 3D, so that exact 2D procedure is **not** copied into this Stage-3 matrix as though it were directly prescribed for the current geometry.

The Stage-3 sweep uses only recommendations that can be defensibly adapted to the present 3D case:

1. Mixture equation staging;
2. gradual flow/inertial loading as a numerical continuation strategy;
3. conservative momentum under-relaxation;
4. retention of `PRESTO!` and low slip under-relaxation.

The production mesh is intentionally **not** an experimental variable or qualification question in Stage 3. Mesh refinement/mesh sensitivity remains outside this numerical-strategy sweep.

---

## 3. Experimental question

> **Which combination of Fluent-recommended Mixture staging, gradual inlet/inertial loading, and momentum damping most effectively reduces the long-window residual oscillation and full-domain imbalance of the 03A full-geometry steady field without changing the physical boundary condition?**

A secondary question is:

> **After several thousand full-operating-condition iterations, do the `k` and `epsilon` residuals continue to diverge/expand, become bounded but oscillatory, or approach a progressively smaller stationary envelope?**

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

Fluent guidance makes Implicit Body Force a relevant possible later numerical test for multiphase calculations with body forces, but enabling it throughout Stage 3 would change the canonical 03A baseline. If Stage 3 does not produce a useful branch, Implicit Body Force can be tested later as a small companion experiment from the best Stage-3 strategy rather than being added to the 12-case factorial.

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

`PRESTO!` is retained in every branch because Fluent recommends it for strong rotational/swirl pressure gradients. It is therefore treated as a fixed best-practice setting rather than another matrix factor.

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

This is the recommendation Fluent explicitly associates with difficult Mixture cases such as cyclone separation.

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

For this 3D spiral inlet, reducing inlet velocity is not a pure independent swirl control. It simultaneously changes both phase mass flows, Reynolds/inertial loading and centrifugal forcing. S1 is therefore interpreted as a **numerical continuation/homotopy strategy adapted from Fluent's gradual-swirl recommendation**, not as a claim that Fluent directly prescribed this exact 3D inlet-velocity sequence.

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
| `F02` | Carrier-first staged | 100% immediately | `0.7` | isolate Fluent Mixture staging |
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

No Stage-2 result is used to remove branches from this matrix. In particular, the promising standard-`k-epsilon` behaviour in N5 is retained as context only.

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
10. execute the evidence-gated branch schedule below;
11. never reinitialize between stages of the same branch;
12. save a paired case/data checkpoint at every stage transition.

This avoids unnecessary reconstruction of settings already carried correctly by the parent while still preventing hidden differences between branches.

---

## 9. Evidence-driven stage-transition rule

### 9.1 Core rule

Intermediate staged branches do **not** advance because they have reached a fixed iteration count.

The active field must demonstrate improving or stabilising turbulence behaviour over the **most recent 750 iterations** before additional Mixture equations or inlet loading are introduced.

The gate is based primarily on the direct Fluent scaled residual histories of:

```text
k
epsilon
```

Both residuals must independently pass the gate. `epsilon` therefore has effective veto power: a branch cannot advance because `k` looks good while `epsilon` is still becoming more intermittent or unstable.

The first gate evaluation cannot occur before at least `750` iterations have been accumulated in the current stage.

After the first 750 iterations, evaluate the rolling gate every `250` additional iterations using the latest 750-iteration window.

### 9.2 Quantifying decreasing level and reduced jumping

For each of `k` and `epsilon`, analyse the most recent 750 iterations in `log10(residual)` space.

Split that window into:

```text
first comparison block = first 250 iterations
middle block           = middle 250 iterations
final comparison block = final 250 iterations
```

For each residual calculate at minimum:

```text
median
P05
P95
maximum
log-envelope width = log10(P95 / P05)
```

A residual passes the transition gate when **at least one** of the following is true:

1. **decreasing residual level** — the final-250 median is at least approximately `10%` lower than the first-250 median; or
2. **reduced jumping/variability** — the final-250 log-envelope width is at least approximately `15%` smaller than the first-250 log-envelope width.

In addition, a pass is rejected if the same residual shows material simultaneous deterioration, defined for this campaign as either:

```text
final-250 median > first-250 median by more than 20%
OR
final-250 P95    > first-250 P95 by more than 20%
```

These percentages are **project transition criteria**, not Fluent convergence criteria. Their role is to make the staged continuation decision reproducible rather than subjective.

### 9.3 Gate decision

The stage can advance only when:

```text
k gate       = PASS
AND
epsilon gate = PASS
AND
no safety veto is active
```

If either turbulence residual fails, the stage continues at the same equation/loading state.

### 9.4 Safety veto

Continuity, phase fluxes, liquid inventory and warnings are **not** the normal transition metric, because Stage 3 deliberately focuses the stage-loading decision on the problematic turbulence equations.

However, they can veto progression if the field is clearly becoming corrupted.

A transition is blocked by any of the following:

- Fluent FPE or unrecoverable AMG divergence;
- clearly expanding continuity over repeated windows;
- full-domain mass imbalance becoming explosively worse rather than merely unsettled;
- unbounded/nonphysical liquid-inventory behaviour inconsistent with the flux histories;
- reverse flow or turbulent-viscosity limiting spreading in a manner consistent with numerical breakdown;
- corrupted/non-finite phase flux or monitor values.

### 9.5 Stalled stage

There is no fixed scientific iteration ceiling for an intermediate stage.

If a stage repeatedly fails the gate, continue evaluating it in rolling windows. If **three consecutive gate evaluations** show no meaningful improvement in either residual, or show progressive deterioration, classify the stage as:

```text
STAGE_STALLED
```

A `STAGE_STALLED` branch must not automatically advance to the next equation/loading state. It can be stopped and retained as evidence rather than spending iterations indefinitely.

---

## 10. Evidence-gated branch schedules

Every branch must accumulate at least `5,000` iterations at the final physical operating condition.

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
→ minimum 750 iterations
→ evaluate rolling k/epsilon gate every 250 iterations
→ PASS: save checkpoint
→ Volume Fraction ON
→ Slip Velocity ON
→ no reinitialization
→ final 100% full-Mixture phase
→ minimum 5,000 iterations
→ continue according to final-stage rule
```

The former fixed `2,000` carrier-only transition has been removed. The field determines when the Mixture equations are restored.

### Schedule C — M0 + S1

Applies to `F07`, `F09`, `F11`.

```text
Hybrid Initialize at 10%
→ full Mixture at 10%
→ pass 750-window k/epsilon gate
→ checkpoint
→ 20%
→ pass gate
→ checkpoint
→ 40%
→ pass gate
→ checkpoint
→ 80%
→ pass gate
→ checkpoint
→ 100%
→ minimum 5,000 final-condition iterations
→ continue according to final-stage rule
```

The full Mixture equations remain active throughout.

There is no predetermined `1,000`-iteration duration for a ramp level. Each level remains active until the evidence gate passes or the stage is classified `STAGE_STALLED`/failed.

### Schedule D — M1 + S1

Applies to `F08`, `F10`, `F12`.

Project synthesis of the two Fluent recommendations:

```text
Hybrid Initialize at 10%
→ Volume Fraction OFF + Slip Velocity OFF
→ carrier-only at 10%
→ pass 750-window k/epsilon gate
→ checkpoint
→ Volume Fraction ON + Slip Velocity ON
→ no reinitialization
→ full Mixture at 10%
→ pass gate
→ checkpoint
→ 20%
→ pass gate
→ checkpoint
→ 40%
→ pass gate
→ checkpoint
→ 80%
→ pass gate
→ checkpoint
→ 100%
→ minimum 5,000 final-condition iterations
→ continue according to final-stage rule
```

This exact combined ordering is a **project experimental synthesis** of the two Fluent guides. Fluent recommends both strategies independently but does not prescribe this exact 3D combined schedule.

---

## 11. Final 100% operating-condition rule

`5,000` final-condition iterations are a **minimum observation window**, not an automatic stopping definition.

The final stage is different from an intermediate stage because there is no next loading/equation state to unlock.

At and beyond 5,000 final-condition iterations:

1. evaluate the same rolling 750-iteration `k`/`epsilon` metrics every 250 iterations;
2. if either residual is still showing meaningful improvement in level or variability, **continue the calculation beyond 5,000**;
3. do not stop merely because iteration 5,000 has been reached;
4. if the residuals become bounded and no longer materially improve over three consecutive evaluations, classify the final field according to its stationary behaviour rather than forcing more iterations indefinitely;
5. if the residual envelope is progressively expanding or a safety veto occurs, terminate/classify the branch accordingly.

A branch can therefore finish at 5,000, 6,500, 8,000, 10,000+ final-condition iterations depending on what the actual turbulence histories show.

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
NUMERICAL_FAILURE
```

A bounded oscillatory field may still be useful if the physical histories are stationary enough to support a steady-RANS interpretation.

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

### Physical histories

Record throughout:

- liquid inlet mass flux;
- vapour inlet mass flux;
- liquid → brine outlet;
- liquid → steam outlet;
- vapour → brine outlet;
- vapour → steam outlet;
- total mixture inlet/outlet;
- full-domain mass imbalance and relative imbalance;
- total domain liquid inventory;
- Y010 liquid inventory as a diagnostic only;
- Y030 liquid inventory as a diagnostic only;
- brine-pipe-entry static pressure;
- brine-pipe-entry total pressure.

The Stage-2 reporting gap where temporal liquid-inventory monitor arrays were empty must not be repeated in Stage 3.

Before production submission, run a short monitor smoke test and verify that every required monitor actually records non-empty temporal data and survives save/reload where applicable. A branch with missing required monitor histories fails preflight.

---

## 13. Analysis windows and gate artifacts

For each branch, preserve stage boundaries and evaluate at least:

- every 750-iteration transition-gate window;
- each preconditioning/ramp stage endpoint;
- first `100` iterations after every major equation/inlet-speed transition;
- final `1,000` iterations of the 100% operating-condition phase;
- final `2,000` iterations where available;
- full final-condition history.

For every transition-gate evaluation, store for both `k` and `epsilon`:

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

---

## 14. Primary comparison logic

The 12-case matrix allows direct estimates of:

### Mixture staging effect

Compare:

```text
F01 vs F02
F03 vs F04
F05 vs F06
F07 vs F08
F09 vs F10
F11 vs F12
```

### Momentum damping effect

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

### Progressive inlet/inertial-loading effect

Compare:

```text
F01 vs F07
F02 vs F08
F03 vs F09
F04 vs F10
F05 vs F11
F06 vs F12
```

### Interaction effects

Determine whether the recommendations act independently or whether, for example, Mixture staging is only useful when combined with gradual loading and/or lower momentum URF.

Because staged branches may require different numbers of preconditioning iterations, comparisons must be made primarily over the **100% final-condition histories**, not by comparing the same absolute global iteration number.

---

## 15. Stage-3 success criteria

Stage 3 is not required to produce a perfectly textbook residual curve.

A branch is **numerically promising** if, over the long final-condition window:

- `k` and `epsilon` residual envelopes are substantially smaller and more bounded than the Stage-1 reference;
- continuity does not display an expanding envelope;
- full-domain imbalance trends materially downward or becomes acceptably bounded;
- phase-flux histories approach a stationary mean or bounded repeatable regime;
- liquid inventory does not exhibit an unbounded secular drift inconsistent with the outlet fluxes;
- turbulent-viscosity limiting and reverse-flow behaviour do not progressively spread through the domain;
- there is no FPE/AMG numerical breakdown.

A branch can be useful even if residuals remain oscillatory, provided the oscillation is bounded and the physical monitor histories are stationary enough to justify a steady-RANS interpretation.

A branch is **not** qualified solely because:

- it survives the requested iteration count;
- one residual reaches the nominal criterion once;
- an endpoint flux snapshot looks favourable;
- it has lower residuals while equations or operating conditions are still intentionally simplified.

---

## 16. Relationship to N1/N3/N4/N5

Stage 3 does not discard Stage 2.

Stage-2 evidence currently suggests:

- `N1` reduced turbulence URFs did not improve the long available continuation;
- `N3` first-order turbulence transport changed the solution and did not clearly settle the turbulence field;
- `N4` broader first-order startup did not provide convincing available endpoint behaviour;
- `N5` standard `k-epsilon` bootstrap gave the clearest short-window numerical improvement, but the improvement did not survive the available return to RNG.

These results remain important but do not narrow the next experiment prematurely because:

1. the Stage-2 interventions were not the complete Fluent-recommended cyclone/swirl startup sweep;
2. the Stage-2 continuation windows were shorter than the Stage-3 convergence horizon;
3. N5 changes the turbulence model, while Stage 3 first asks whether the canonical RNG model can be made numerically useful through startup strategy alone.

After Stage 3, the N5 observation should be revisited explicitly.

If none of the Fluent-guided Stage-3 branches produces a sufficiently settled RNG field, the next targeted campaign can compare longer turbulence-model bootstraps or alternative turbulence closures from the best Stage-3 startup strategy rather than from the original unstable baseline.

---

## 17. Out-of-scope changes for the F01–F12 sweep

Do not add the following as extra factors during the initial Stage-3 matrix:

- brine-outlet pressure;
- steam-outlet pressure;
- liquid patching;
- transient formulation;
- standard `k-epsilon` as a final model;
- RSM;
- first-order momentum/turbulence discretization;
- altered `k` or `epsilon` URFs;
- altered slip URF;
- Coupled solver;
- pseudo-time;
- Implicit Body Force changes;
- localised-turbulence-initialization changes;
- mesh refinement or mesh-sensitivity study;
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
warning/event log
branch summary JSON/Markdown
```

The branch summary must record the actual number of iterations completed at every stage rather than infer lineage from filenames.

At every successful transition, save:

```text
checkpoint before transition
750-iteration gate statistics
PASS reason for k
PASS reason for epsilon
settings before transition
settings after transition
new stage start iteration
```

This makes later instability traceable to the exact equation/loading change that preceded it.

---

## 19. Draft execution order

The full matrix is intended to be run, but a practical submission order is:

```text
F01  canonical long control
F02  Mixture staging only
F07  inlet/inertial ramp only
F08  both principal Fluent-guided staging recommendations
F03/F04/F09/F10  moderate momentum damping variants
F05/F06/F11/F12  strongest damping variants
```

This ordering is for early visibility only. It does **not** authorize stopping the matrix after a promising early branch unless a later decision explicitly changes the campaign objective.

The current intention is to run the complete 12-case sweep.

---

## 20. Decision after Stage 3

Once the full sweep is available, classify the outcome into one of the following directions.

### A — one or more RNG branches become clearly usable

Use the best Fluent-guided startup strategy as the candidate numerical parent for subsequent 03A qualification and eventual 03B pressure continuation.

If that candidate uses momentum URF `0.5` or `0.3`, first restore:

```text
Momentum URF = 0.7
```

without reinitialization and evaluate the continuation using the same 750-iteration `k`/`epsilon` logic before declaring it a canonical 03A parent.

### B — RNG remains bounded but persistently oscillatory while physical monitors are stationary

Assess whether the steady-RANS solution should be interpreted statistically/boundedly rather than demanding monotonic residual collapse, and determine whether a transient/RANS comparison is required.

### C — no RNG branch becomes numerically useful, but the N5 standard bootstrap remains markedly better

Launch a dedicated turbulence-model campaign from the best Stage-3 startup strategy, including longer standard-`k-epsilon` behaviour and controlled transitions to the intended higher-swirl turbulence closure.

### D — all F01–F12 branches remain numerically unusable

Before repeating the same solver-only tuning, use the best available Stage-3 branch as the basis for targeted follow-up numerical tests that were deliberately excluded from the factorial, especially:

- Implicit Body Force formulation;
- localised turbulence initialization;
- turbulence-model suitability / N5 follow-up;
- whether a steady solution exists for the current model.

Mesh investigation remains outside the present Stage-3 scope and is not an execution gate for this sweep.

---

## 21. Remaining execution-implementation checks

The scientific decisions in this draft are now mostly resolved. Before production execution, verify only the implementation details needed to make the plan reproducible:

- exact Fluent/PyFluent commands for toggling `Volume Fraction` and `Slip Velocity` independently in the active 2025 R2 Mixture case;
- whether the current gRPC execution layer can modify both split-inlet velocities safely between continuation stages without reinitialization;
- that inlet turbulence intensity/hydraulic-diameter values remain unchanged when velocity is ramped;
- branch/checkpoint naming convention;
- persistence and reload behaviour for residual, liquid-inventory and phase-flux histories;
- calculation of the automated 750-iteration `k`/`epsilon` gate metrics;
- checkpoint/save behaviour before every transition;
- ability to distinguish `STAGE_STALLED` from numerical failure in the branch summary.

No scientific conclusion should be attached to Stage 3 until the full-condition histories have been analysed.