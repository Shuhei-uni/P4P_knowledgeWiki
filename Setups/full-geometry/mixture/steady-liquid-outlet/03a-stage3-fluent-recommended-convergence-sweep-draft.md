# 03A Stage 3 — Fluent-Recommended Convergence Sweep (Draft)

> **Status:** draft — planning document, not yet frozen for execution  
> **Setup family:** `03A` full-geometry steady Mixture baseline  
> **Purpose:** perform a broad, long-duration numerical convergence sweep based directly on Ansys Fluent guidance for difficult Mixture/cyclone and strongly swirling flows before narrowing onto any one turbulence-model or solver-rescue strategy.  
> **Physical case:** unchanged from 03A — same geometry, materials, phase definitions, split inlet, outlet pressures, gravity, and no liquid patch.  
> **Parent authority:** the verified 03A pre-initialization case, not an already-developed Stage-1/Stage-2 solution field, unless a branch definition below explicitly says otherwise.

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

> Before changing the physical model or committing to a different turbulence model, test whether a difficult cyclone/Mixture field becomes substantially more stable when Fluent's own staged-solution recommendations are applied over a sufficiently long iteration window.

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
- ensuring sufficient mesh resolution of pressure and swirl-velocity gradients;
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

The Stage-3 sweep uses only the recommendations that can be defensibly adapted to the present 3D case:

1. Mixture equation staging;
2. gradual inlet/swirl loading;
3. conservative momentum under-relaxation;
4. retention of `PRESTO!` and low slip under-relaxation.

---

## 3. Experimental question

> **Which combination of Fluent-recommended Mixture staging, gradual swirl loading, and momentum damping most effectively reduces the long-window residual oscillation and full-domain imbalance of the 03A full-geometry steady field without changing the physical boundary condition?**

A secondary question is:

> **After several thousand full-operating-condition iterations, do the `k` and `epsilon` residuals continue to diverge/expand, become bounded but oscillatory, or approach a progressively smaller stationary envelope?**

This is more important than the value of a single final residual point.

---

## 4. Physical case held fixed

All Stage-3 branches preserve the 03A physical case:

```text
Time model           = Steady
Multiphase           = Mixture
Primary phase        = water vapour
Secondary phase      = liquid water
Turbulence authority = RNG k-epsilon
Gravity              = [0, -9.81, 0] m/s²
Energy               = Off
Liquid patch         = None
DPM                   = Off
EWF                   = Off
Steam outlet         = Pressure Outlet, 1.120 MPa gauge
Brine outlet         = Pressure Outlet, 1.120 MPa gauge
Final inlet velocity = 27.118 m/s on both split-inlet faces
```

The material properties, split-inlet areas/compositions, wall treatment and all remaining physical settings remain those of the verified 03A/08b-parity setup.

Stage 3 is **not** a brine-pressure experiment and does not qualify or modify 03B.

---

## 5. Common numerical settings

Unless a branch definition explicitly changes a listed experimental factor, retain the canonical 03A stack:

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
| Volume-fraction URF | `0.4` |
| `k` URF | `0.8` |
| `epsilon` URF | `0.8` |
| Slip / drift URF | `0.1` |
| Pseudo-time | Off |

The existing slip/drift URF of `0.1` already satisfies Fluent's recommendation to begin at `0.2` or lower, so slip URF is **not** a Stage-3 factorial variable.

`PRESTO!` is also retained in every branch because Fluent specifically recommends it for strong rotational/swirl pressure gradients. It is therefore treated as a fixed best-practice setting rather than another matrix factor.

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

### Factor S — inlet/swirl loading

Two levels:

**S0 — Full-speed startup**

```text
27.118 m/s from the first iteration
```

**S1 — progressive inlet-speed ramp**

Use the project implementation of Fluent's approximate `10%` start / progressive-increase recommendation:

| Ramp level | Velocity on each split inlet |
|---:|---:|
| 10% | `2.7118 m/s` |
| 20% | `5.4236 m/s` |
| 40% | `10.8472 m/s` |
| 80% | `21.6944 m/s` |
| 100% | `27.1180 m/s` |

The exact intermediate percentages are a **project adaptation**, not values prescribed verbatim by Fluent. They implement the guidance to begin around 10% and progressively increase, approximately doubling where practical.

Both split inlet faces must always use the same percentage of their authoritative final velocity so the intended phase-flow ratio and inlet geometry remain unchanged.

### Factor U — momentum under-relaxation

Three levels:

```text
U0 = 0.7   canonical 03A value
U1 = 0.5   moderate damping
U2 = 0.3   strong damping
```

The `0.3–0.5` levels are adapted from Fluent guidance for difficult strongly swirling/rotating flows. Because the current calculation is fully 3D, they are applied as the available global momentum URF rather than as separate axial/radial/swirl-specific values.

---

## 7. Full Stage-3 experiment matrix

The full matrix is:

```text
2 Mixture-startup levels
× 2 inlet/swirl-startup levels
× 3 momentum-URF levels
= 12 branches
```

| Case | Mixture startup | Inlet/swirl startup | Momentum URF | Primary comparison role |
|---|---|---|---:|---|
| `F01` | Full immediately | 100% immediately | `0.7` | long-run canonical control |
| `F02` | Carrier-first staged | 100% immediately | `0.7` | isolate Fluent Mixture staging |
| `F03` | Full immediately | 100% immediately | `0.5` | isolate moderate momentum damping |
| `F04` | Carrier-first staged | 100% immediately | `0.5` | Mixture staging + moderate damping |
| `F05` | Full immediately | 100% immediately | `0.3` | isolate strong momentum damping |
| `F06` | Carrier-first staged | 100% immediately | `0.3` | Mixture staging + strong damping |
| `F07` | Full immediately | 10→20→40→80→100% | `0.7` | isolate progressive swirl loading |
| `F08` | Carrier-first staged | 10→20→40→80→100% | `0.7` | combine the two main Fluent staging recommendations |
| `F09` | Full immediately | 10→20→40→80→100% | `0.5` | swirl ramp + moderate damping |
| `F10` | Carrier-first staged | 10→20→40→80→100% | `0.5` | combined recommendations with moderate damping |
| `F11` | Full immediately | 10→20→40→80→100% | `0.3` | swirl ramp + strong damping |
| `F12` | Carrier-first staged | 10→20→40→80→100% | `0.3` | most conservative combined strategy |

No Stage-2 result is used to remove branches from this matrix. In particular, the promising standard-`k-epsilon` behaviour in N5 is retained as context only.

---

## 8. Parent and initialization rule

The Stage-3 matrix is intended to test **startup strategy**, so branches should not begin from the Stage-1 iteration-1000 field or from an N1/N3/N4/N5 developed solution.

Preferred common parent:

```text
verified 03A full-geometry case
with complete physical/numerical setup
before Hybrid Initialization
```

For each branch:

1. load the same immutable verified pre-initialization 03A case;
2. apply branch-specific momentum URF;
3. apply the branch-specific initial inlet velocity;
4. apply M0 or M1 equation state;
5. positively read back all changed settings;
6. Hybrid Initialize once;
7. execute the branch schedule below;
8. never reinitialize between stages of the same branch;
9. save a paired case/data checkpoint at every stage transition.

This avoids contaminating the experiment with a field already developed under full-speed/full-Mixture conditions.

---

## 9. Long-duration iteration schedules

The previous Stage-2 `300–700`-iteration extensions were useful for screening but are too short to decide whether a difficult cyclone residual envelope is truly settling.

For Stage 3, **every branch must accumulate at least `5,000` iterations at the final physical operating condition**.

Low-speed or carrier-only preconditioning iterations do **not** count toward the final 5,000-iteration qualification window.

### Schedule A — M0 + S0

Applies to `F01`, `F03`, `F05`.

```text
Hybrid Initialize
→ full Mixture active
→ inlet = 27.118 m/s
→ run 5,000 steady iterations
```

Nominal total per branch:

```text
5,000 iterations
```

### Schedule B — M1 + S0

Applies to `F02`, `F04`, `F06`.

```text
Hybrid Initialize
→ Volume Fraction OFF
→ Slip Velocity OFF
→ inlet = 27.118 m/s
→ carrier-only stage: 2,000 iterations
→ save checkpoint
→ Volume Fraction ON
→ Slip Velocity ON
→ no reinitialization
→ full Mixture: 5,000 iterations
```

Nominal total per branch:

```text
7,000 iterations
```

The fixed `2,000` carrier-only budget is a practical Stage-3 starting rule. If the carrier field is still clearly evolving at iteration 2,000, preserve the evidence and allow extension before reactivating the Mixture equations rather than forcing the transition solely because the iteration counter was reached.

### Schedule C — M0 + S1

Applies to `F07`, `F09`, `F11`.

```text
Hybrid Initialize at 10%
→ 1,000 iterations at 10%
→ 1,000 iterations at 20%
→ 1,000 iterations at 40%
→ 1,000 iterations at 80%
→ 5,000 iterations at 100%
```

Nominal total per branch:

```text
9,000 iterations
```

The full Mixture equations remain active throughout.

### Schedule D — M1 + S1

Applies to `F08`, `F10`, `F12`.

Project synthesis of the two Fluent recommendations:

```text
Hybrid Initialize at 10%
→ Volume Fraction OFF + Slip Velocity OFF
→ 1,000 carrier-only iterations at 10%
→ save checkpoint
→ Volume Fraction ON + Slip Velocity ON
→ 1,000 full-Mixture iterations at 10%
→ 1,000 at 20%
→ 1,000 at 40%
→ 1,000 at 80%
→ 5,000 at 100%
```

Nominal total per branch:

```text
10,000 iterations
```

This exact combined ordering is a **project experimental synthesis** of the two Fluent guides. Fluent recommends both strategies independently but does not prescribe this exact 3D combined schedule.

---

## 10. Extension rule beyond 5,000 full-condition iterations

`5,000` final-condition iterations are a minimum observation window, not an automatic stopping definition for convergence.

At the 5,000-final-condition checkpoint:

- if residual/physical-monitor envelopes are clearly expanding or the case has become physically corrupted, classify the branch accordingly and do not extend solely to accumulate iterations;
- if the solution is bounded but clearly unchanged over a long window, retain it as a bounded/oscillatory outcome;
- if the residual and physical-monitor envelopes are still meaningfully decreasing, extend the full-condition phase toward `10,000` iterations;
- if convergence appears achieved before 5,000, still preserve the planned long history unless a later review explicitly shortens the branch.

No branch is considered better merely because it produces one unusually low endpoint residual.

---

## 11. Required monitoring

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

The Stage-2 reporting gap where temporal liquid-inventory monitor arrays were empty must not be repeated in Stage 3. Monitor persistence must be verified during preflight before any long sweep is submitted.

---

## 12. Analysis windows

For each branch, preserve stage boundaries and evaluate at least:

- each preconditioning/ramp stage endpoint;
- first `100` iterations after every major equation/inlet-speed transition;
- final `1,000` iterations of the 100% operating-condition phase;
- final `2,000` iterations where available;
- full final-condition history.

For `k`, `epsilon`, continuity and volume fraction, report at minimum:

```text
median
P05
P95
maximum
log-envelope amplitude
trend/slope of rolling median
trend/slope of rolling P95
```

The analysis should distinguish:

```text
converging envelope
bounded stationary oscillation
slow drift
intermittent spikes
expanding/diverging envelope
numerical failure
```

---

## 13. Primary comparison logic

The 12-case matrix allows direct estimates of:

### Mixture staging effect

Compare pairs such as:

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

### Progressive swirl-loading effect

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

The campaign should explicitly determine whether the recommendations act independently or whether, for example, Mixture staging is only useful when combined with gradual swirl loading and/or lower momentum URF.

---

## 14. Stage-3 success criteria

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

## 15. Relationship to N1/N3/N4/N5

Stage 3 does not discard Stage 2.

Stage-2 evidence currently suggests:

- `N1` reduced turbulence URFs did not improve the long available continuation;
- `N3` first-order turbulence transport changed the solution and did not clearly settle the turbulence field;
- `N4` broader first-order startup did not provide convincing available endpoint behaviour;
- `N5` standard `k-epsilon` bootstrap gave the clearest short-window numerical improvement, but the improvement did not survive the available return to RNG.

These results are important but should not narrow the next experiment prematurely because:

1. the Stage-2 interventions were not the complete Fluent-recommended cyclone/swirl startup sweep;
2. the Stage-2 continuation windows were shorter than the Stage-3 convergence horizon;
3. N5 changes the turbulence model, while Stage 3 first asks whether the canonical model can be made numerically useful through startup strategy alone.

After Stage 3, the N5 observation should be revisited explicitly.

If none of the Fluent-guided Stage-3 branches produces a sufficiently settled RNG field, the next targeted campaign can compare longer turbulence-model bootstraps or alternative turbulence closures from the best Stage-3 startup strategy rather than from the original unstable baseline.

---

## 16. Out-of-scope changes for this sweep

Do not add the following as extra factors during the initial Stage-3 matrix:

- brine-outlet pressure;
- steam-outlet pressure;
- liquid patching;
- transient formulation;
- standard `k-epsilon` as a final model;
- RSM;
- first-order momentum/turbulence discretization;
- altered `k` or `epsilon` URFs;
- Coupled solver;
- pseudo-time;
- mesh refinement;
- DPM;
- EWF.

Those remain possible later experiments, but adding them now would prevent a clean interpretation of the Fluent-recommended staging sweep.

---

## 17. Execution artifact requirements

Every branch should produce a self-contained artifact set containing at least:

```text
case/data checkpoint before initialization
case/data checkpoint at each stage transition
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

---

## 18. Draft execution order

The full matrix is intended to be run, but a practical submission order is:

```text
F01  canonical long control
F02  Mixture staging only
F07  swirl ramp only
F08  both principal Fluent recommendations
F03/F04/F09/F10  moderate momentum damping variants
F05/F06/F11/F12  strongest damping variants
```

This ordering is for early visibility only. It does **not** authorize stopping the matrix after a promising early branch unless a later decision explicitly changes the campaign objective.

The current intention is to run the complete 12-case sweep.

---

## 19. Decision after Stage 3

Once the full sweep is available, classify the outcome into one of the following directions:

### A — one or more RNG branches become clearly usable

Use the best Fluent-guided startup strategy as the new numerical parent for subsequent 03A qualification and eventual 03B pressure continuation.

### B — RNG remains bounded but persistently oscillatory while physical monitors are stationary

Assess whether the steady-RANS solution should be interpreted statistically/boundedly rather than demanding monotonic residual collapse, and determine whether a transient/RANS comparison is required.

### C — no RNG branch becomes numerically useful, but the N5 standard bootstrap remains markedly better

Launch a dedicated turbulence-model campaign from the best Stage-3 startup strategy, including longer standard-`k-epsilon` behaviour and controlled transitions to the intended higher-swirl turbulence closure.

### D — all branches remain unstable or physically inconsistent

Reassess mesh resolution, outlet/backflow behaviour, turbulence-model suitability, and the assumption that a steady solution exists before spending further iterations on solver-only tuning.

---

## 20. Draft status / items to edit before execution

This document intentionally remains a draft. Before execution, confirm:

- exact Fluent/PyFluent commands for toggling `Volume Fraction` and `Slip Velocity` independently in the active 2025 R2 Mixture case;
- whether the current gRPC execution layer can modify both split-inlet velocities safely between continuation stages without reinitialization;
- branch checkpoint naming convention;
- monitor persistence/reload behaviour for liquid inventory and phase fluxes;
- whether `2,000` carrier-only iterations should remain fixed or become an evidence-based transition gate;
- whether the 10→20→40→80→100% ramp should remain the canonical project implementation after an initial smoke test;
- final long-run extension rule and compute budget.

No scientific conclusion should be attached to Stage 3 until the full-condition histories have been analysed.
