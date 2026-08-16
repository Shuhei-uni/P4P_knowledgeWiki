# Mixture Transient Liquid-Outlet Setup

## Intent contract

| Field | Value |
|---|---|
| Programme | Full geometry |
| Physics family | Mixture |
| Campaign | transient liquid-outlet characterization |
| Suggested machine ID | `FG-MIX-T01` |
| Investigation mode | exploratory / sensitivity with a numerical-qualification pre-stage |
| Interpretation owner | user-led |
| Geometry basis | same verified full-geometry production mesh used by the current Y010 Mixture work |
| Steady predecessor | [`02e` Y010 outlet characterization](../../../active/02e-mixture-y010-brine-outlet-boundary-characterization.md) |
| Key predecessor evidence | [`02e` Stage-1 results](../../../reports/02e/stage1-results-20260816.md) |

## Primary question

Test whether outlet regimes that retained useful lower-vessel liquid during the steady Mixture screen become bounded, interpretable unsteady solutions when the transient method is qualified and then held fixed across the comparison.

This campaign deliberately separates two questions:

1. **Numerical qualification:** what transient timestep/startup procedure is sufficiently stable and insensitive for this screening purpose?
2. **Outlet comparison:** with that method locked, how do the selected Pressure Outlet, Outlet Vent, and Mass-Flow Outlet cases evolve in physical time?

Do not change both the transient method and the outlet formulation case-by-case unless a deviation is explicitly recorded.

## Production screen matrix

| Case | Outlet family | Transient control | Reason retained from steady evidence |
|---|---|---:|---|
| `T-PO-1` | Pressure Outlet | `1.200 MPa gauge` | retained more Y010/Y030 liquid than the stable lower-pressure case before steady failure |
| `T-PO-2` | Pressure Outlet | `1.240 MPa gauge` | aggressive pressure-retention point and strongest PO test of a retained-liquid regime |
| `T-OV-1` | Outlet Vent | `K = 10` | materially better liquid retention than the low-resistance vent before late steady failure |
| `T-OV-2` | Outlet Vent | `K = 100` | aggressive vent-retention case; Y030 remained much closer to the initial inventory before failure |
| `T-MF-1` | Mass-Flow Outlet | `58.4235 kg/s liquid` | strong early apparent retention; tests whether rapid steady failure was solver-form dependent |
| `T-MF-2` | Mass-Flow Outlet | `233.694 kg/s liquid` | longer-lived MF case with comparatively sensible drainage immediately before vapor corruption |

Do not include EF in this first transient screen. The selected PO, OV, and MF cases each have a concrete evidence-based reason to be revisited transiently.

## Common t = 0 state

Every case must begin from one clean common transient parent.

1. Load/rebuild the verified common Mixture setup on the production mesh.
2. Switch to transient and apply the qualified transient numerical settings.
3. Hybrid initialize.
4. Patch the approved Y010 lower-region cells to liquid **once, after initialization**.
5. Set/confirm flow time `t = 0 s`.
6. Save the common initialized case/data parent.
7. Clone each outlet case from that exact parent.
8. Change only the intended brine-outlet formulation/control.
9. Do **not** initialize again and do **not** repatch during the run.

Do not use a partly failed/corrupted steady result as the transient initial field for one child while another child starts clean.

## Frozen physical/model context

Keep the following common unless a numerical-qualification result explicitly requires a shared change:

- Mixture multiphase model;
- same production mesh and geometry;
- same inlet conditions as the current `02e` production basis;
- steam outlet `1.120 MPa gauge`;
- gravity and RNG `k-epsilon` turbulence;
- DPM off;
- EWF off;
- same liquid-dominant brine backflow composition used by the steady Y010 study;
- same spatial discretization schemes as the predecessor where compatible with the transient formulation.

## Transient numerical qualification

Qualify the method on `T-PO-1` before launching the six-case production screen.

### Pressure-velocity and temporal method

Target:

- pressure-velocity coupling: `PISO` with neighbor correction;
- Mixture volume-fraction formulation: implicit;
- temporal discretization: bounded second-order implicit from the start where stable.

If startup proves clearly unstable, a short identical first-order startup may be tested, but it must be applied to every production case for exactly the same physical-time interval and recorded as part of the method.

### Timestep bracket

Initial qualification bracket:

| Trial | Timestep |
|---|---:|
| `DT-A` | `5.0e-4 s` |
| `DT-B` | `2.5e-4 s` |
| `DT-C` | `1.25e-4 s` only if A/B materially disagree |

Use fixed timestep during the first production screen. Do not let each outlet family choose a different adaptive history.

Compare at minimum:

- `V_l,Y010(t)`;
- `V_l,Y030(t)`;
- total liquid inventory;
- phase-separated brine/steam outlet fluxes;
- brine-pipe-entry pressure;
- per-timestep convergence behavior.

Choose the largest timestep that gives sufficiently similar screening trajectories to the finer qualified case for the quantities above. This is a screening qualification, not a formal temporal-convergence claim unless a stronger verification protocol is explicitly added.

### Iterations per timestep

Use a maximum of roughly `15–20` iterations per timestep for the qualification. A healthy run should normally settle each step without repeatedly exhausting that maximum. If essentially every step hits the cap, reduce timestep before simply increasing the iteration cap.

## Physical-time stages

After qualification:

1. **All-case health preflight:** run each of the six cases for approximately `0.05–0.10 s` with the exact locked method.
2. **First screening horizon:** run viable cases to `0.5 s` physical time.
3. **Extension:** extend promising or clearly unsettled cases toward `1.0 s` or beyond when the inventory/flux histories show the first horizon is insufficient.

Do not replace physical duration with a steady-style rule such as “500 iterations.”

## Required evidence package

Record every timestep unless storage constraints require a justified coarser history frequency:

- liquid volume in Y010;
- liquid volume in Y030;
- total continuous-liquid volume/inventory;
- liquid and vapor mass flux at the brine outlet;
- liquid and vapor mass flux at the steam outlet;
- brine-pipe-entry pressure;
- residual histories within each timestep.

Preserve full case/data checkpoints at useful physical-time landmarks (for example around `0`, `0.05`, `0.10`, `0.25`, and `0.50 s`) rather than saving a complete field every timestep.

## Transient liquid balance

Do not interpret instantaneous inlet/outlet mismatch with the steady-state balance rule. For liquid without interphase mass transfer, check storage plus flux closure:

```text
dM_l/dt = m_dot_l,in - m_dot_l,brine - m_dot_l,steam
```

A useful diagnostic residual is the difference between the finite-difference inventory change and the net liquid flux over the same timestep. If phase change is enabled in a later campaign, include the corresponding source term.

## Interpretation contract

No hard physical success threshold is imposed for this exploratory screen.

The result report should show the time histories and classify observable behavior without deciding the preferred outlet automatically. Useful descriptive categories include:

- bounded approach toward a quasi-steady inventory;
- bounded oscillation/filling-draining cycle;
- monotonic washout;
- sustained outlet reversal;
- timestep/convergence breakdown;
- vapor-field corruption or other numerical failure.

The user will decide how these observations affect the next modelling branch.
