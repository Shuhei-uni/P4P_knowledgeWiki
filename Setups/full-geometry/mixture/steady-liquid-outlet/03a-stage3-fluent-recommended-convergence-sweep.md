# 03A Stage 3 — Fluent-Recommended Convergence Sweep

> **Status:** active plan — scientific design resolved; P0/monitor smoke-test and live command verification remain before production  
> **Setup family:** `03A` full-geometry steady Mixture baseline  
> **Purpose:** perform a broad, long-duration numerical convergence sweep based on Ansys Fluent guidance for difficult Mixture/cyclone and strongly swirling flows before narrowing onto any one turbulence-model or solver-rescue strategy.  
> **Physical case:** unchanged from 03A — same geometry, materials, phase definitions, split inlet, outlet pressures, gravity, and no liquid patch.  
> **Parent authority:** one verified 03A pre-initialization parent with the frozen Stage-3 fingerprint defined below. Branches must not begin from an already-developed Stage-1/Stage-2 solution field.  
> **Execution model:** three independent Fluent sessions may execute Stage-3 branches in parallel. Session/server assignment is operational metadata only and must not define case identity, scientific lineage, filenames, or report structure.  
> **Execution specification:** [`03a-stage3-shared-parent-and-seed-spec.yaml`](./03a-stage3-shared-parent-and-seed-spec.yaml) is the machine-readable authority for P0 construction, local schedule-seed derivation, branch creation, storage, gate version, and adaptive execution.

---

## 1. Why Stage 3 exists

Stage 1 showed that the canonical 08b-parity full-geometry case can survive `1,000` steady iterations, but it did not approach a sufficiently settled state. Continuity remained high and the turbulence residuals, especially `epsilon`, remained strongly intermittent.

Stage 2 tested four shorter numerical interventions (`N1`, `N3`, `N4`, `N5`). The strongest clue came from `N5`:

```text
Stage-1 parent
→ standard k-epsilon bootstrap
→ restore RNG k-epsilon
```

During the standard-`k-epsilon` bootstrap the residual envelope became much more bounded and the diagnostic mass imbalance improved substantially. The available Stage-2 report gives approximately:

```text
standard-k-epsilon bootstrap final 100:
continuity median ≈ 7.82e-2
k median          ≈ 2.28e-3
epsilon median    ≈ 5.01e-3
epsilon P95       ≈ 1.34e-2
mass imbalance    ≈ 5.24%

Stage-1 reference:
continuity median ≈ 1.58e-1
k median          ≈ 3.29e-3
epsilon median    ≈ 3.22e-2
epsilon P95       ≈ 9.39e-1
mass imbalance    ≈ 17.17%
```

The improvement did not remain bounded after RNG was restored. Stage 3 therefore does **not** assume standard `k-epsilon` is the answer. It first performs the wider Fluent-recommended startup/continuation sweep while keeping RNG as the authoritative turbulence model.

The working principle is:

> Before changing the physical model or committing to a different turbulence model, test whether the difficult cyclone/Mixture field can be made substantially more numerically useful by applying Fluent's own staged-solution recommendations over a long enough history to distinguish short-term improvement from genuine settling.

A second principle is that the carrier field is not judged by turbulence residuals alone. For this project the central physical quantities are total flow split, phase flow split, full-domain balance, liquid inventory, and pressure behaviour around the brine outlet.

The staged transition rule is intentionally non-terminal. If a preconditioning stage does not satisfy the preferred gate, it may still progress after a sufficiently long attempt so that every numerically viable strategy reaches the final physical operating condition.

---

## 2. Fluent guidance being tested

### 2.1 Mixture-model solution strategy — primary/direct cyclone guidance

Fluent's multiphase solution guidance states that for some Mixture-model cases, explicitly including cyclone separation, an initial solution can be obtained more easily by temporarily disabling:

- `Volume Fraction`;
- `Slip Velocity`;

then computing the initial carrier flow field, restoring those equations without reinitialization, and continuing the full Mixture solution.

The same guidance recommends beginning a Mixture calculation with a slip-velocity URF of `0.2` or lower. The current 03A value is `0.1`, so slip URF is held fixed rather than made another Stage-3 factor.

Official source:

- Ansys Fluent 2025 R2 User's Guide — *Solution Strategies for Multiphase Modeling*, §27.8.2.2 Mixture Model.

### 2.2 Strong-swirl continuation guidance

Fluent's strong swirl/rotating-flow guidance supports:

- `PRESTO!` for steep rotational pressure gradients;
- reduced velocity/momentum relaxation for difficult swirl;
- beginning from weaker rotational/inertial loading and progressively increasing toward the final operating condition.

For the present fixed 3D spiral inlet, reducing inlet velocity changes phase mass flow, Reynolds number, inertial loading and centrifugal forcing together. Stage 3 therefore treats the inlet ramp as a **numerical continuation/homotopy strategy adapted from Fluent's gradual-swirl guidance**, not as a literal pure-swirl control.

### 2.3 3D scope distinction

The detailed equation-by-equation axisymmetric-swirl procedure is not copied literally into this 3D separator. Stage 3 uses only the defensible 3D adaptations:

```text
M — Mixture equation staging
    strongest/direct cyclone recommendation

S — progressive inlet/inertial loading
    3D continuation strategy adapted from Fluent swirl guidance

U — momentum under-relaxation
    secondary Fluent-guided stabilization sensitivity
```

### 2.4 Standard k-epsilon → RNG is a separate later follow-up

Fluent also recommends that difficult RNG convergence may benefit from first obtaining a standard-`k-epsilon` solution and then returning to RNG. That directly supports revisiting Stage-2 `N5`, but it is intentionally excluded from F01–F12 so Stage 3 first tests whether the canonical RNG/Mixture model can be made useful without changing turbulence-model form.

---

## 3. Experimental question

Primary question:

> **Which combination of Fluent-recommended Mixture staging, gradual inlet/inertial loading, and momentum damping most effectively produces a developed, numerically useful full-geometry steady field without changing the physical boundary condition?**

A developed field requires both:

1. **solver behaviour** — especially `k`, `epsilon`, continuity and momentum residual envelopes;
2. **project-core behaviour** — total inlet/outlet flow, phase routing when active, mass balance, liquid inventory, and brine-entry pressure behaviour.

A secondary question is whether, after several thousand full-condition iterations, the residuals and physical monitors:

- continue expanding/diverging;
- become bounded but oscillatory;
- or approach a progressively smaller/stationary envelope.

---

## 4. Physical case held fixed

All F01–F12 branches preserve:

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

Stage 3 is **not** a brine-pressure experiment and does not qualify or modify 03B.

---

## 5. Frozen Stage-3 model and numerical fingerprint

Branches use a **parent + controlled delta** workflow. Unchanged settings are inherited from the verified P0 parent and positively read back rather than repeatedly reconstructed.

### 5.1 Mixture interaction

| Item | Stage-3 state |
|---|---|
| Secondary-phase diameter | Constant `1.0e-5 m` |
| Slip-velocity model | `Manninen-et-al` |
| Drag coefficient | `Schiller-Naumann` |
| Drag modification | None |
| Surface tension | Continuum Surface Force |
| Surface-tension coefficient | `0.04041 N/m` |
| Wall adhesion | Off |

### 5.2 Turbulence

```text
RNG k-epsilon
Standard Wall Functions
Differential Viscosity Model = On
Swirl Dominated Flow         = On
```

### 5.3 Body-force treatment

```text
Gravity / physical body force   = present
Body-force URF                  = 1.0
Implicit Body Force formulation = OFF
```

Implicit Body Force remains OFF throughout F01–F12.

### 5.4 Initialization

Every branch uses:

```text
Hybrid Initialization
Fluent default Hybrid Initialization settings
no localised turbulence initialization override
no liquid patch
```

Hybrid Initialization is performed **exactly once per branch**, after the branch-specific startup state has been applied and verified. Never reinitialize at Mixture-equation or inlet-loading transitions.

### 5.5 Common numerical settings

| Numerical item | Stage-3 setting |
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

Other exposed expert controls remain at the verified P0 state and are included in the fingerprint/readback.

---

## 6. Experimental factors

### Factor M — Mixture-equation startup

**M0 — Full Mixture immediately**

```text
Volume Fraction = active
Slip Velocity   = active
```

**M1 — Carrier-first staging**

```text
Volume Fraction = temporarily inactive
Slip Velocity   = temporarily inactive
```

Solve the carrier/turbulence field first, then reactivate both equations without reinitialization.

### Factor S — progressive inlet/inertial loading

**S0 — full-speed startup**

```text
27.118 m/s from the first iteration
```

**S1 — progressive loading**

| Level | Velocity on each split inlet |
|---:|---:|
| 10% | `2.7118 m/s` |
| 20% | `5.4236 m/s` |
| 40% | `10.8472 m/s` |
| 80% | `21.6944 m/s` |
| 100% | `27.1180 m/s` |

At every ramp transition:

- change only velocity magnitude;
- change both split inlet faces together;
- preserve turbulence intensity;
- preserve hydraulic diameter;
- do not reinitialize.

Only the 100% stage is the intended physical operating condition.

### Factor U — momentum under-relaxation

```text
U0 = 0.7   canonical 03A
U1 = 0.5   moderate damping
U2 = 0.3   strong damping
```

The selected U value remains active throughout the branch. If the best Stage-3 branch uses U1/U2, a later return-to-authority continuation to `0.7` is required before that field can become the canonical 03A parent for 03B.

---

## 7. Full Stage-3 experiment matrix

```text
2 Mixture-startup levels
× 2 inlet-loading levels
× 3 momentum-URF levels
= 12 branches
```

| Case | Mixture startup | Inlet startup | Momentum URF | Role |
|---|---|---|---:|---|
| `F01` | Full immediately | 100% immediately | `0.7` | long-run canonical control |
| `F02` | Carrier-first staged | 100% immediately | `0.7` | isolate direct Mixture staging |
| `F03` | Full immediately | 100% immediately | `0.5` | moderate momentum damping |
| `F04` | Carrier-first staged | 100% immediately | `0.5` | staging + moderate damping |
| `F05` | Full immediately | 100% immediately | `0.3` | strong momentum damping |
| `F06` | Carrier-first staged | 100% immediately | `0.3` | staging + strong damping |
| `F07` | Full immediately | 10→20→40→80→100% | `0.7` | progressive loading only |
| `F08` | Carrier-first staged | 10→20→40→80→100% | `0.7` | both principal staging strategies |
| `F09` | Full immediately | 10→20→40→80→100% | `0.5` | ramp + moderate damping |
| `F10` | Carrier-first staged | 10→20→40→80→100% | `0.5` | combined + moderate damping |
| `F11` | Full immediately | 10→20→40→80→100% | `0.3` | ramp + strong damping |
| `F12` | Carrier-first staged | 10→20→40→80→100% | `0.3` | most conservative combined strategy |

---

## 8. P0, local inheritance and initialization

Stage 3 must not begin from the Stage-1 iteration-1000 field or from N1/N3/N4/N5 developed solutions.

### 8.1 OneDrive P0 only

The shared parent is:

```text
03A-stage3-P0-monitor-ready-preinit.cas.h5
```

User-designated OneDrive parent root:

```text
/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/
2026 Sem 2/700/Full geom/03A-stage3
```

**Only P0 is a shared Stage-3 case artifact.** P0 may have its fingerprint/readback/SHA256 companion files beside it, but no run-specific Fluent artifacts belong in this OneDrive directory.

For each Fluent computer/agent:

```text
OneDrive P0
→ copy P0 to local Fluent-machine storage
→ verify local P0
→ derive the required A/B/C/D startup state locally
→ apply only the branch U delta
→ optional local F##-preinit save/reload verification
→ Hybrid Initialize once
→ run locally
```

All A/B/C/D seed cases, F## preinit cases, checkpoints, autosaves, transcripts, monitor exports, gate reports, and final case/data files remain **local to the Fluent machine**. Do not synchronize them back into the Stage-3 OneDrive parent directory.

The four local schedule states are:

```text
A = M0 + S0 = full Mixture + 100% inlet
B = M1 + S0 = carrier-first + 100% inlet
C = M0 + S1 = full Mixture + 10% inlet
D = M1 + S1 = carrier-first + 10% inlet
```

They are deterministic operational conveniences, not scientific parents and not shared artifacts.

Branch mapping:

```text
A + U0/U1/U2 → F01 / F03 / F05
B + U0/U1/U2 → F02 / F04 / F06
C + U0/U1/U2 → F07 / F09 / F11
D + U0/U1/U2 → F08 / F10 / F12
```

Before production, use a **disposable local copy of P0** for a `20–50` iteration monitor smoke test. Verify every required residual, flow, pressure, phase-routing and liquid-inventory history records non-empty finite data and survives save/reload where applicable. Never promote the smoke-test solution into P0.

---

## 9. Evidence-driven stage-transition rule

### 9.1 Gate intent

The gate is a **preferred progression rule**, not a terminal convergence test.

```text
preferred:
    advance when the current state demonstrates development/stabilisation

fallback:
    if no preferred pass by 3,000 iterations at that state,
    save evidence and advance anyway unless hard numerical failure occurred
```

### 9.2 Frozen production gate — `stage3-gate-v1`

All F01–F12 production branches use the same gate version:

```text
stage3-gate-v1
```

The thresholds below are **exact project thresholds for this campaign**, not Fluent convergence criteria. Once production starts, an agent must not tune them branch-by-branch.

First assessment at a stage:

```text
after 750 iterations
```

Later assessments:

```text
every +250 iterations
using the most recent 750-iteration window
```

Split the window into first/middle/final 250-iteration blocks.

### 9.3 A — turbulence gate: `k` and `epsilon`

For each residual calculate over the most recent 750 iterations:

```text
median
P05
P95
maximum
log-envelope width = log10(P95 / P05)
```

Each of `k` and `epsilon` passes its improvement test when at least one is true:

```text
final-250 median <= 0.90 × first-250 median
OR
final-250 log-envelope width <= 0.85 × first-250 log-envelope width
```

The same residual is vetoed if either deterioration condition is true:

```text
final-250 median > 1.20 × first-250 median
OR
final-250 P95    > 1.20 × first-250 P95
```

Both `k` and `epsilon` must pass independently.

### 9.4 B — carrier residual gate

Track:

```text
continuity
x-momentum
y-momentum
z-momentum
```

All values must remain finite.

Continuity fails the non-expansion check only when **both** are true:

```text
final-250 median > 1.20 × first-250 median
AND
final-250 P95    > 1.20 × first-250 P95
```

Apply the same deterministic non-expansion test to each momentum residual. A downward trend is favourable but is not required when the field is already bounded.

### 9.5 C — project-core flow / pressure gate

Always use:

```text
total mixture inlet flow
total mixture outlet flow
steam-outlet total flow
brine-outlet total flow
full-domain mass imbalance / relative imbalance
brine-pipe-entry static pressure
brine-pipe-entry total pressure
```

When full Mixture is active also inspect:

```text
liquid → brine
liquid → steam
vapour → brine
vapour → steam
total domain liquid inventory
Y010 / Y030 liquid inventory diagnostics
```

During M1 carrier-only intervals, phase-specific outlet fluxes and liquid inventories are not required positive gate variables.

For each required total-flow/pressure signal, the stationarity signal passes when either:

```text
|final-250 median - first-250 median| / representative magnitude <= 0.05
OR
final-250 variability envelope <= 0.85 × first-250 variability envelope
```

The shared gate evaluator must use one fixed definition of representative magnitude and variability for every branch.

Relative mass imbalance passes non-deterioration when:

```text
final-250 relative-imbalance median <= 1.20 × first-250 median
```

Non-finite/corrupted required monitor values veto a preferred pass.

For S1 stages, each loading level is judged for stationarity at its **own** imposed loading; absolute 10/20/40/80% values are not compared against 100% operating targets.

### 9.6 Preferred transition decision

A preferred pass requires:

```text
k gate                  = PASS
epsilon gate            = PASS
carrier residual gate   = PASS
flow / pressure gate    = PASS
hard numerical failure  = NO
```

For full Mixture stages, phase-routing and liquid-inventory evidence is also retained and may veto a pass when it is non-finite/corrupted or classified by the shared evaluator as clearly expanding/unbounded.

### 9.7 Hard numerical failure vs transport failure

Hard numerical failure includes:

- Fluent FPE;
- unrecoverable AMG/solver termination;
- non-finite solution/monitor state that is unusable;
- corruption/loss of all valid checkpoints needed to continue scientifically.

These are **not automatically hard numerical failures** while Fluent remains numerically usable:

- poor convergence;
- bounded oscillation;
- large but finite mass imbalance;
- reverse flow;
- turbulent-viscosity limiting;
- drifting monitors.

A gRPC disconnect, client timeout, agent interruption, or other transport problem is also **not** `NUMERICAL_FAILURE` by itself. After transport loss:

1. reconnect to the same Fluent process first;
2. establish actual branch, stage and completed iteration state;
3. do not silently repeat an iteration block whose completion is uncertain;
4. continue the same F## branch if Fluent remains numerically valid.

### 9.8 STAGE_STALLED and forced progression

Do not label a stage `STAGE_STALLED` before `2,000` iterations at that state.

Continue until either:

1. preferred gate passes; or
2. the stage reaches `3,000` iterations.

At `3,000` without preferred pass and without hard numerical failure:

```text
save checkpoint
record final failed gate statistics
record FORCED_ADVANCE_AT_3000
advance to next prescribed state
```

### 9.9 Explicit adaptive blocking execution exception

Stage 3 requires the agent to make a scientific decision at each gate checkpoint. For F01–F12 only, the user has explicitly approved an exception to the repository's normal detached/native-run preference.

The agent may remain attached and issue **one synchronous blocking Fluent solve command per decision block**:

```text
first intermediate block = 750 iterations
subsequent block          = 250 iterations
```

The solve call returning is intentionally the agent wake-up point. The agent then evaluates `stage3-gate-v1`, records the decision, performs any prescribed transition/checkpoint, and issues the next block.

This does **not** authorize a generic Python iteration runner:

- no Python `for`/`while` loop around solve calls;
- no one-iteration/fine-grained loop;
- every solve call follows an explicit scientific decision point;
- Fluent-native autosave must still be configured locally;
- never silently repeat an uncertain block after a transport failure.

---

## 10. Branch schedules

Every branch must accumulate at least `5,000` iterations at the final 100% physical operating condition unless hard numerical failure prevents it. Preconditioning iterations do not count toward that minimum.

### Schedule A — M0 + S0 — F01/F03/F05

```text
Hybrid Initialize
→ full Mixture active
→ inlet = 27.118 m/s
→ final 100% condition
→ minimum 5,000 iterations
→ apply final-condition rule
```

### Schedule B — M1 + S0 — F02/F04/F06

```text
Hybrid Initialize
→ Volume Fraction OFF
→ Slip Velocity OFF
→ inlet = 27.118 m/s
→ carrier-only stage
→ 750 then +250 gate assessments
→ PASS or forced advance at 3,000
→ checkpoint
→ enable Volume Fraction + Slip Velocity
→ no reinitialization
→ final 100% full Mixture
→ minimum 5,000 iterations
→ apply final-condition rule
```

### Schedule C — M0 + S1 — F07/F09/F11

```text
Hybrid Initialize at 10%
→ full Mixture 10%
→ PASS or forced advance at 3,000
→ checkpoint → 20%
→ PASS or forced advance at 3,000
→ checkpoint → 40%
→ PASS or forced advance at 3,000
→ checkpoint → 80%
→ PASS or forced advance at 3,000
→ checkpoint → 100%
→ minimum 5,000 final-condition iterations
→ apply final-condition rule
```

### Schedule D — M1 + S1 — F08/F10/F12

```text
Hybrid Initialize at 10%
→ Volume Fraction OFF + Slip Velocity OFF
→ carrier-only 10%
→ PASS or forced advance at 3,000
→ checkpoint
→ Volume Fraction ON + Slip Velocity ON
→ no reinitialization
→ full Mixture 10%
→ PASS or forced advance at 3,000
→ checkpoint → 20%
→ PASS or forced advance at 3,000
→ checkpoint → 40%
→ PASS or forced advance at 3,000
→ checkpoint → 80%
→ PASS or forced advance at 3,000
→ checkpoint → 100%
→ minimum 5,000 final-condition iterations
→ apply final-condition rule
```

The exact D ordering is a project synthesis of the two Fluent recommendations; Fluent does not prescribe this exact combined 3D schedule.

---

## 11. Final 100% operating-condition rule

`5,000` iterations are the minimum final-condition observation window, not an automatic convergence declaration.

At and beyond 5,000:

1. evaluate the same rolling `750`-iteration evidence every `250` iterations;
2. if meaningful improvement remains, continue;
3. stop once **three consecutive assessments** show no material improvement according to the frozen final-condition evaluator; or
4. stop at a hard maximum of **10,000 final-condition iterations**.

The `10,000` cap is an observation/resource cap, **not a convergence criterion**. If the field is still materially improving at that point, classify:

```text
IMPROVING_AT_OBSERVATION_CAP
```

and preserve the full evidence for the next decision.

Final numerical-state labels include at least:

```text
CONVERGING
BOUNDED_LOW_VARIABILITY
BOUNDED_OSCILLATORY
SLOW_DRIFT
EXPANDING_OSCILLATION
IMPROVING_AT_OBSERVATION_CAP
STAGE_STALLED
FORCED_ADVANCE_AT_3000
NUMERICAL_FAILURE
```

A bounded oscillatory field may still be useful if pressure/flow/inventory histories are stationary enough to support a steady-RANS interpretation.

---

## 12. Required monitoring

Every branch must capture **continuous temporal histories**, not endpoint snapshots only.

### Solver histories

- continuity scaled residual;
- x/y/z momentum scaled residuals;
- liquid volume-fraction residual when active;
- `k` residual;
- `epsilon` residual;
- turbulent-viscosity limiting warnings/count where available;
- reversed-flow warnings/outlet faces where available.

When Volume Fraction / Slip Velocity are disabled, mark that interval explicitly rather than treating absent residuals as zero.

### Project-core histories

Record throughout:

- liquid inlet mass flux;
- vapour inlet mass flux;
- total mixture inlet mass flux;
- total steam-outlet flow;
- total brine-outlet flow;
- total mixture outlet flow;
- full-domain mass imbalance and relative imbalance;
- brine-entry static pressure;
- brine-entry total pressure.

When full Mixture is active also record:

- liquid → brine;
- liquid → steam;
- vapour → brine;
- vapour → steam;
- total domain liquid inventory;
- Y010 liquid inventory diagnostic;
- Y030 liquid inventory diagnostic.

A branch with missing required temporal histories fails preflight.

---

## 13. Analysis windows and transition evidence

Preserve/evaluate at least:

- every 750-iteration gate window;
- the 2,000-iteration stall-assessment point when reached;
- the 3,000 forced-transition point when reached;
- every preconditioning/ramp endpoint;
- first 100 iterations after major equation/loading transitions;
- final 1,000 iterations of the final condition;
- final 2,000 iterations where available;
- full final-condition history.

Every gate decision must store:

```text
branch + stage
actual iteration range
stage3-gate-v1
k metrics/result
epsilon metrics/result
continuity/momentum metrics/result
flow/pressure metrics/result
mass-balance metrics/result
phase/inventory supporting evidence where applicable
PASS / FAIL and reason
PREFERRED_PASS_ADVANCE or FORCED_ADVANCE_AT_3000
checkpoint identifier
settings before transition
settings after transition
new-stage start iteration
```

---

## 14. Primary comparison logic

### Mixture staging effect

```text
F01 vs F02
F03 vs F04
F05 vs F06
F07 vs F08
F09 vs F10
F11 vs F12
```

### Progressive-loading effect

```text
F01 vs F07
F02 vs F08
F03 vs F09
F04 vs F10
F05 vs F11
F06 vs F12
```

### Momentum damping effect

```text
F01 vs F03 vs F05
F02 vs F04 vs F06
F07 vs F09 vs F11
F08 vs F10 vs F12
```

Comparisons are made primarily over the **100% final-condition histories**, not the same absolute global iteration number. Also compare how often strategies reached later states by preferred passes versus forced advances.

---

## 15. Stage-3 success criteria

A branch is numerically promising when the long final-condition evidence shows that:

- `k` and `epsilon` are substantially smaller/more bounded than Stage 1;
- continuity and momentum are bounded rather than progressively expanding;
- total inlet/outlet histories approach stationary means;
- full-domain imbalance materially improves or becomes bounded;
- brine-entry static/total pressures approach stationary or bounded repeatable regimes;
- phase-routing histories approach stationary/bounded regimes;
- liquid inventory does not show unexplained unbounded secular drift;
- turbulent-viscosity limiting/reverse-flow behaviour does not progressively spread toward numerical breakdown;
- no FPE/unrecoverable AMG numerical failure occurs.

A branch is **not** qualified solely because it survives the iteration count, reaches a low residual once, or produces a favourable endpoint flux snapshot.

---

## 16. Relationship to N1/N3/N4/N5 and Stage 3B

Stage-2 evidence currently suggests:

- `N1` reduced turbulence URFs did not improve the available continuation;
- `N3` first-order turbulence transport did not clearly settle the field;
- `N4` broader first-order startup did not provide convincing endpoint behaviour;
- `N5` standard-`k-epsilon` bootstrap gave the clearest short-window improvement, but that improvement did not survive the available RNG return.

The intended hierarchy remains:

```text
Stage 3A
    F01–F12 cyclone/swirl startup sweep with RNG retained

then, if needed:

Stage 3B
    best Stage-3A startup method
    → longer standard k-epsilon bootstrap
    → controlled return to RNG
    → long final-condition qualification
```

---

## 17. Out-of-scope changes for F01–F12

Do not add these as extra factors:

- brine-outlet pressure;
- steam-outlet pressure;
- liquid patching;
- transient formulation;
- standard `k-epsilon` as final model;
- RSM;
- first-order momentum/turbulence discretization;
- altered `k`/`epsilon` URFs;
- altered slip URF;
- Coupled solver;
- pseudo-time;
- Implicit Body Force;
- localised turbulence initialization;
- DPM;
- EWF.

---

## 18. Execution artifact requirements

Every branch keeps a **local** self-contained artifact set containing at least:

```text
P0 parent identifier / fingerprint
local branch-preinit checkpoint
preflight Stage-3 readback
Fluent multiphase/model summary where available
case/data checkpoint at each stage transition
transition-gate JSON/Markdown at each gate decision
final case/data endpoint
Fluent transcript / execution log
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

Record actual iteration counts rather than inferring them from filenames.

Run-specific artifacts stay on local Fluent-machine storage. The OneDrive Stage-3 directory remains the immutable P0 parent location only.

---

## 19. Three-session execution distribution

The preferred initial queues are:

| Session | Queue | Role |
|---|---|---|
| **Session 1 — user supervised** | `F08 → F10 → F12` | all Schedule-D combined branches |
| **Session 2** | `F01 → F07 → F03 → F09` | control + loading branches |
| **Session 3** | `F02 → F04 → F11 → F06 → F05` | Mixture staging + remaining strong-damping branches |

First parallel launch:

```text
Session 1: F08
Session 2: F01
Session 3: F02
```

### 19.1 Agent ownership

For every queued branch, the agent must:

1. copy the immutable shared P0 to local Fluent-machine storage;
2. establish the correct local A/B/C/D startup state from that local P0 copy;
3. apply only the branch momentum-URF delta;
4. verify Stage-3 fingerprint + M/S state + U value before initialization;
5. optionally save/reload-verify a local F## preinit case;
6. Hybrid Initialize exactly once;
7. configure local Fluent-native autosave;
8. execute the branch using the Stage-3 blocking decision workflow and `stage3-gate-v1`;
9. checkpoint before every equation/loading transition;
10. record preferred/forced/stalled/failure states;
11. complete the final-condition rule unless hard failure prevents it;
12. keep the complete branch artifact set locally;
13. move to the next unstarted branch in the queue.

### 19.2 Queue flexibility

The queues are preferred initial ownership, not permanent case/server binding.

Any **unstarted** branch may be reassigned to another Fluent machine to improve throughput. Moving an unstarted branch changes only operational ownership.

Do not casually move a running branch. Cross-machine recovery is allowed only from a verified complete case/data checkpoint while preserving branch/stage/iteration provenance.

`server_id` remains transport metadata only and never becomes scientific identity.

---

## 20. Decision after Stage 3

### A — one or more RNG branches clearly usable

Use the best Fluent-guided startup strategy as the candidate numerical parent. If it uses U=`0.5` or `0.3`, restore momentum URF to `0.7` without reinitialization and qualify that continuation before it becomes the canonical 03A parent for 03B.

### B — RNG bounded/oscillatory while physical monitors stationary

Assess a bounded/statistical steady-RANS interpretation and whether a transient comparison is required.

### C — RNG still poor but N5 bootstrap remains markedly better

Launch the predeclared Stage-3B standard-`k-epsilon` → RNG campaign from the best Stage-3A startup strategy.

### D — all F01–F12 unusable

Use the full Stage-3 evidence to choose targeted follow-up tests such as Implicit Body Force, local turbulence initialization, turbulence-model suitability, or whether a steady solution exists for the current model.

---

## 21. Remaining implementation checks before production

Before F01–F12 production, verify:

- exact Fluent/PyFluent paths for toggling `Volume Fraction` and `Slip Velocity` in the active 2025 R2 Mixture case;
- both split-inlet velocities can be changed safely between continuation stages without reinitialization;
- inlet turbulence intensity/hydraulic diameter remain unchanged during ramping;
- creation, smoke test, fresh-session reload verification and placement of the immutable P0 in the designated OneDrive Stage-3 parent root;
- local deterministic derivation of A/B/C/D states from a local P0 copy;
- branch/checkpoint naming convention;
- local Fluent-native autosave configuration;
- persistence/reload behaviour of residual, liquid-inventory, phase-flux and brine-entry-pressure histories;
- one deterministic implementation of `stage3-gate-v1` used by all three agents;
- the explicit synchronous 750/+250 blocking workflow wakes the agent reliably after a completed solve block;
- transport recovery reconciles actual completed iteration/stage state before any retry;
- final-condition stop logic enforces the 5,000 minimum, three no-improvement assessments, and 10,000 observation cap;
- no derived seed, branch, checkpoint, transcript or result is written into the OneDrive P0 directory.

No scientific conclusion should be attached to Stage 3 until the full-condition histories have been analysed.