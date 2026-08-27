> **Legacy source:** Setups/full-geometry/mixture/transient-liquid-outlet/stage-06-six-case-screen.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# FG-MIX-T01 Stage 6 — Six-Case Aggressive Retention Screen

## Intent

| Field | Value |
|---|---|
| Stage ID | `FG-MIX-T01-S6` |
| Investigation mode | exploratory sensitivity screen |
| Primary question | With initialization and transient numerics qualified and held fixed, do the most promising steady-state liquid-retaining outlet regimes become bounded, interpretable unsteady Mixture solutions? |
| Interpretation owner | user-led |
| Parent | immutable common `t = 0` parent selected in Stage 3 |
| Method | exact Stage-4 method lock, subject to Stage-5 compatibility outcome |

## Scientific framing

This is the first production transient outlet comparison. It is **not** a reproduction of the steady screen and it is not a search for the case that simply survives the longest.

The evidence should distinguish:

- bounded liquid storage;
- bounded oscillatory filling/draining;
- continuing liquid washout;
- sustained outlet reversal;
- vapour corruption;
- per-timestep convergence breakdown;
- other numerical failure.

The six cases were selected because the steady campaign showed useful liquid-retention behavior before failure or showed a distinct mass-flow response worth revisiting transiently.

## Case matrix

| Case | Outlet family | Transient control | Reason retained from steady evidence |
|---|---|---:|---|
| `T-PO-1` | Pressure Outlet | `1.200 MPa gauge` | retained more Y010/Y030 liquid than the stable lower-pressure case before steady failure |
| `T-PO-2` | Pressure Outlet | `1.240 MPa gauge` | most aggressive PO retention point from Stage 1 |
| `T-OV-1` | Outlet Vent | `K = 10` | materially better retention than the low-resistance vent before late steady failure |
| `T-OV-2` | Outlet Vent | `K = 100` | aggressive vent-retention case; Y030 stayed much closer to the initial inventory before failure |
| `T-MF-1` | Mass-Flow Outlet | `58.4235 kg/s liquid` | very strong early apparent retention; tests whether rapid steady failure was steady-solver dependent |
| `T-MF-2` | Mass-Flow Outlet | `233.694 kg/s liquid` | survived much longer than the other MF pilots and had comparatively sensible liquid drainage before vapour corruption |

Do not include Exhaust Fan in this first transient production screen.

## Controlled comparison rule

Every child starts independently from the **same immutable common `t = 0` parent**.

For each child:

```text
load common transient t=0 parent
→ set only the intended brine-outlet formulation/control
→ verify outlet-specific backflow / discharge settings
→ do not initialize
→ do not repatch Y010
→ confirm flow time = 0 s
→ apply/verify locked common transient method
→ run
```

Do not seed one production case from another case's endpoint.

## Frozen context

Keep common across all viable cases:

- exact production mesh;
- Mixture multiphase model;
- same materials/phases;
- same liquid and steam inlet conditions;
- steam outlet `1.120 MPa` gauge;
- gravity `[0, -9.81, 0] m/s²`;
- RNG `k-epsilon`;
- DPM off;
- EWF off;
- selected initialization basis;
- Y010 `t = 0` inventory;
- selected fixed timestep;
- pressure-velocity coupling;
- Mixture VF formulation;
- temporal discretization and any common startup rule;
- maximum iterations per timestep;
- monitor/report definitions and checkpoint cadence.

If Stage 5 showed that one outlet family cannot use the common method, follow the user-approved disposition recorded there rather than hiding a family-specific numerical change inside this comparison.

## Physical-time plan

### Production horizon 1

Run each viable case to:

```text
0.50 s
```

unless it encounters a hard numerical failure first.

### Extension

Cases that remain promising or clearly unsettled at `0.50 s` may be extended toward:

```text
1.00 s or beyond
```

The extension decision should come from the physical-time histories, not from a steady-style iteration target.

## Required evidence package

Record every timestep where practical:

### Liquid inventory

- `V_l,Y010(t)`;
- `V_l,Y030(t)`;
- `V_l,total(t)`;
- liquid mass inventory if available.

### Phase-separated outlet behavior

- liquid mass flux at brine outlet;
- vapour mass flux at brine outlet;
- liquid mass flux at steam outlet;
- vapour mass flux at steam outlet;
- inlet phase fluxes needed for closure.

### Local hydraulic response

- brine-pipe-entry pressure;
- reverse-flow behavior where available;
- outlet normal velocity / total mass flow where useful.

### Numerical behavior

- residual histories within timesteps;
- iterations required per timestep;
- warnings / divergence / FPE events;
- last valid physical time for failed cases.

## Transient storage + flux closure

Do not reuse the steady balance logic directly. For the present no-phase-change liquid balance:

```text
dM_l/dt = m_dot_l,in - m_dot_l,brine - m_dot_l,steam
```

Compute a storage/flux residual from the finite-difference inventory change and net liquid flux over matching time intervals.

An instantaneous inlet/outlet mismatch can be physically correct when the separator is accumulating or losing stored liquid.

## Checkpoints

Preserve full case/data states at useful common physical-time landmarks where the case remains valid, for example:

```text
0.00 s
0.05 s
0.10 s
0.25 s
0.50 s
```

Preserve the last valid state and transcript/log evidence for any case that fails between checkpoints.

## Interpretation contract

There is no automatic physical success threshold for this exploratory screen.

The results report should show time histories and observable behavior first. The user decides whether a case is promising enough to extend, whether a particular outlet family should be retained, or whether the evidence instead points toward a different multiphase formulation or outlet model.

Do not rank failed cases by their last-valid inventory as though they shared an equivalent endpoint.

Do not interpret “no FPE by 0.50 s” as proof of physical correctness.

## Result categories that may be useful

Use only when supported by the histories:

- bounded approach toward a quasi-steady inventory;
- bounded oscillation / cyclic filling-draining;
- monotonic liquid washout;
- sustained lower-vessel accumulation;
- sustained outlet reversal;
- vapour short-circuit through brine outlet;
- liquid carryover through steam outlet;
- timestep/per-step convergence failure;
- vapour-field corruption or other numerical breakdown.

## Successor decision

After this screen, the next modelling step remains intentionally open. Depending on the evidence, the user may choose to:

- refine one or more outlet controls;
- extend physical time;
- investigate a reduced-order level-control boundary;
- change Mixture formulation/settings;
- compare against the full-geometry transient VOF branch;
- or stop the Mixture outlet branch if the model cannot support interpretable retained-liquid behavior.