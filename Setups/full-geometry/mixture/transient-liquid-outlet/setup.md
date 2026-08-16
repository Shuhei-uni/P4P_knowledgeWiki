# Mixture Transient Liquid-Outlet Setup

## Intent contract

| Field | Value |
|---|---|
| Programme | Full geometry |
| Physics family | Mixture |
| Campaign | transient liquid-outlet characterization |
| Suggested machine ID | `FG-MIX-T01` |
| Investigation mode | exploratory / sensitivity with staged numerical-method qualification |
| Interpretation owner | user-led |
| Geometry basis | exact verified full-geometry production mesh used by the current Y010 Mixture work; repeat the parent-build stage for any new mesh |
| Steady predecessor | [`02e` Y010 outlet characterization](../../../active/02e-mixture-y010-brine-outlet-boundary-characterization.md) |
| Key predecessor evidence | [`02e` Stage-1 results](../../../reports/02e/stage1-results-20260816.md) |
| Report home | [mirrored transient report folder](../../../reports/full-geometry/mixture/transient-liquid-outlet/index.md) |

## Campaign question

Can the promising liquid-retaining outlet regimes identified during the steady Mixture work become bounded, interpretable **unsteady** solutions once the transient startup method and numerical controls have first been qualified?

This campaign does **not** jump directly from steady to the six transient outlet cases. The transition to transient is treated as an experiment in its own right so initialization effects, timestep effects, and outlet-family compatibility can be separated before the production screen.

The production question is therefore reached through six dependent stages:

```text
Stage 1  Build one healthy unpatched steady Mixture parent for the exact mesh
   ↓
Stage 2  Construct matched transient start states from steady-parent and Hybrid paths
   ↓
Stage 3  Compare steady-parent versus Hybrid transient initialization
   ↓
Stage 4  Qualify and lock the common transient numerical method / timestep
   ↓
Stage 5  Short common-method preflight across PO / OV / MF outlet families
   ↓
Stage 6  Run the six-case aggressive-retention screen
```

No downstream stage should be treated as independent of the handoff decision from the stage above it.

## Stage documents

The six stages are defined in five detailed setup records because Stages 1 and 2 form one parent-construction workflow:

1. [Stages 1–2 — Steady Parent and Transient Start States](stage-01-02-steady-parent-and-transient-start.md)
2. [Stage 3 — Initialization Comparison](stage-03-initialization-comparison.md)
3. [Stage 4 — Transient Numerical Qualification](stage-04-transient-numerical-qualification.md)
4. [Stage 5 — Outlet-Family Compatibility Preflight](stage-05-outlet-family-preflight.md)
5. [Stage 6 — Six-Case Aggressive Retention Screen](stage-06-six-case-screen.md)

This master file defines the campaign-level lineage and frozen context. Exact run logic belongs in the stage records above.

---

## Parent architecture

### Steady parent

For every exact production mesh used by this campaign, create one immutable, **unpatched**, healthy steady Mixture parent.

Its purpose is to provide a developed pressure, velocity, turbulence and phase field for transient initialization. It is not one of the six transient scientific cases and it is not required to use the same brine-outlet pressure as every later child.

The current baseline parent build uses a Pressure Outlet at `1.120 MPa gauge` on the brine outlet. Later transient children may replace that outlet type/value before timestep 1.

Conceptually:

```text
exact mesh + frozen common physics
→ Hybrid Initialize
→ NO Y010 patch
→ steady solve to accepted developed field
→ save immutable steady case/data parent
```

A different mesh requires a different steady parent. Do not use a parent from a nominally similar mesh without verifying exact mesh identity.

### Initialization comparison branches

The initialization comparison uses `T-PO-1` as the common test definition:

```text
Pressure Outlet
P_brine = 1.200 MPa gauge
```

Both comparison branches receive the **same Y010 liquid patch once at t = 0**.

- `INIT-S`: start from the accepted steady parent field, switch to transient, set `T-PO-1`, then patch Y010.
- `INIT-H`: use Fluent Hybrid Initialization on the same transient case definition, then patch the same Y010 region.

The comparison is therefore **developed-flow initialization versus Hybrid Initialization**, not patched versus unpatched.

### Final transient t = 0 parent

Stage 3 does not pre-assume which initialization method wins. After the comparison, the user selects the common initialization basis.

Create a fresh immutable `t = 0` parent from that selected method using the common baseline physical/model state, Y010 patch, and flow time `0 s`. Do not use a partially evolved `T-PO-1` comparison endpoint as the parent.

All later timestep trials, preflights, and production cases must independently reload this common `t = 0` parent. They may change the intended brine-outlet type/control **before timestep 1**, but must not reinitialize or repatch.

---

## Frozen physical/model context

Unless a qualification stage deliberately revises one item for **all** later cases, keep the following common:

- exact full-geometry production mesh and topology;
- pressure-based solver;
- Mixture multiphase model;
- same water-vapour / water-liquid materials and phase definitions;
- same liquid and steam inlet conditions as the production Y010 basis;
- inlet velocity `27.118 m/s` on both split inlets;
- inlet reference / initial gauge pressure `1.140 MPa`;
- steam outlet `1.120 MPa gauge`;
- gravity `[0, -9.81, 0] m/s²`;
- RNG `k-epsilon` turbulence;
- operating pressure `0 Pa`;
- DPM off;
- EWF off;
- liquid-dominant brine backflow composition where the outlet formulation exposes it;
- common spatial discretization inherited from the verified predecessor where compatible.

Do not tune turbulence, relaxation, discretization, material properties, inlet conditions, or steam-outlet conditions separately for an individual production outlet case and still treat the six cases as one controlled comparison.

---

## Y010 initial-condition control

The six-case transient screen retains the Y010 lower liquid inventory as a controlled initial condition.

Use the approved production-mesh region:

```text
x = [-2.067034, 1.066098] m
y = [-1.484584, 0.100000] m
z = [-1.469893, 2.000000] m
inside = True
```

Historical 231k-mesh reference from `02e`:

```text
Selected cells = 33,315
Geometric selected-cell volume = 4.829410214 m³
Post-patch liquid inventory = 4.790652590 m³
Initial liquid mass = 4224.253734 kg
```

These historical values are references only. Every newly created comparison/start parent must read back its actual selected cells and liquid inventory.

Patch Y010 **once after the selected initialization method and before timestep 1**. Never patch during the transient solution.

---

## Production six-case matrix

The final screen remains:

| Case | Outlet family | Transient control | Reason retained from steady evidence |
|---|---|---:|---|
| `T-PO-1` | Pressure Outlet | `1.200 MPa gauge` | retained more Y010/Y030 liquid than the stable lower-pressure case before steady failure |
| `T-PO-2` | Pressure Outlet | `1.240 MPa gauge` | most aggressive PO liquid-retention point from the steady screen |
| `T-OV-1` | Outlet Vent | `K = 10` | materially better liquid retention than the low-resistance vent before late steady failure |
| `T-OV-2` | Outlet Vent | `K = 100` | aggressive OV retention case; Y030 remained much closer to the initial inventory before failure |
| `T-MF-1` | Mass-Flow Outlet | `58.4235 kg/s liquid` | strong early apparent retention; tests whether rapid steady failure was solver-form dependent |
| `T-MF-2` | Mass-Flow Outlet | `233.694 kg/s liquid` | longer-lived MF case with comparatively sensible drainage before vapour corruption |

Exhaust Fan is excluded from this first transient production screen.

The six cases are not launched until Stages 1–5 have established the parent, initialization rule, transient method, and outlet-family compatibility decision.

---

## Numerical-method principle

Stage 4 owns the exact transient qualification. The current method to test is:

- `PISO` with neighbor correction;
- implicit Mixture volume-fraction formulation;
- bounded second-order implicit temporal discretization where stable;
- fixed timestep during this campaign;
- approximately `15–20` maximum iterations per timestep.

Initial timestep bracket:

| Trial | Timestep |
|---|---:|
| `DT-A` | `5.0e-4 s` |
| `DT-B` | `2.5e-4 s` |
| `DT-C` | `1.25e-4 s` only if A/B materially disagree or remain numerically questionable |

The selected method is a **screening qualification**, not automatically a formal temporal-convergence proof. Once selected, it becomes the common method lock for Stages 5 and 6.

Do not let each outlet family independently choose its own timestep or transient scheme inside the six-case comparison.

---

## Physical-time logic

Transient runs are compared in physical time, not by a steady-style iteration count.

Current campaign horizons are:

| Stage | Initial physical-time horizon |
|---|---:|
| Initialization comparison | `0.05 s`, extend both branches toward `0.10 s` if needed |
| Timestep qualification | `0.05 s`, extend active trials toward `0.10 s` if needed |
| Outlet-family preflight | `0.05 s`, optionally `0.10 s` identically |
| Six-case production screen | `0.50 s` |
| Production extension | toward `1.00 s` or beyond only when histories justify it |

A case reaching a particular iteration count is not itself evidence that enough physical time has elapsed.

---

## Common evidence package

Instrument before the transient solve so the required histories exist from timestep 1.

At minimum record:

- liquid volume in Y010;
- liquid volume in Y030;
- total continuous-liquid volume/inventory;
- liquid and vapour mass flux at the brine outlet;
- liquid and vapour mass flux at the steam outlet;
- inlet phase fluxes needed for closure;
- brine-pipe-entry pressure;
- residual histories and iterations used within each timestep;
- reverse-flow / warning / divergence events.

Preserve full case/data checkpoints at useful common physical-time landmarks rather than saving the entire field every timestep.

---

## Transient liquid balance

Do not apply the steady instantaneous inlet/outlet balance rule directly to transient results.

For the present no-phase-change liquid balance:

```text
dM_l/dt = m_dot_l,in - m_dot_l,brine - m_dot_l,steam
```

Compare the finite-difference liquid-inventory change with the net liquid flux over matching physical-time intervals. Instantaneous inlet/outlet mismatch can be physically correct when liquid is accumulating or draining from the separator.

---

## Interpretation contract

No hard physical success threshold is imposed for this exploratory campaign.

Each stage report should present measured histories, numerical behavior, limitations, and neutral observations before any decision is made. The user remains the interpretation owner and chooses the handoff to the next stage.

Useful behavior descriptions for the final production screen may include, only when supported by the evidence:

- bounded approach toward a quasi-steady inventory;
- bounded filling/draining oscillation;
- monotonic washout;
- sustained lower-vessel accumulation;
- sustained outlet reversal;
- vapour short-circuit through the brine outlet;
- liquid carryover through the steam outlet;
- timestep/per-step convergence breakdown;
- vapour-field corruption or other numerical failure.

`No FPE` is not by itself a physical success criterion.

---

## Report filing rule

This folder contains setup definitions and stage plans only.

All completed-run evidence belongs under:

```text
Setups/reports/full-geometry/mixture/transient-liquid-outlet/
```

Use the mirrored [report index](../../../reports/full-geometry/mixture/transient-liquid-outlet/index.md) for the stage-report sequence. Do not create completed-run `results.md` files beside these setup records.
