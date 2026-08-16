# FG-MIX-T01 Stage 4 — Transient Numerical Qualification

## Intent

| Field | Value |
|---|---|
| Stage ID | `FG-MIX-T01-S4` |
| Investigation mode | numerical sensitivity / screening qualification |
| Primary question | What common transient method is sufficiently stable and timestep-insensitive to support the later outlet comparison? |
| Interpretation owner | user-led |
| Parent | final common `t = 0` transient parent selected in [Stage 3](stage-03-initialization-comparison.md) |
| Qualification case | `T-PO-1`, Pressure Outlet at `1.200 MPa` gauge |

## Why this stage exists

The six outlet cases should not each discover their own timestep or solver controls. Qualify one common transient method first, lock it, and then apply it unchanged to the later comparison.

This is a **screening qualification**, not a formal temporal-convergence proof unless the user later adds stricter verification criteria.

## Common case construction

For every timestep trial:

```text
reload the same immutable common t=0 parent
→ set brine outlet = Pressure Outlet, 1.200 MPa gauge
→ do not initialize
→ do not repatch
→ apply only the trial timestep / explicitly planned common numerical setting
→ start from flow time 0 s
```

Do not seed a finer-timestep case from the endpoint of a coarser case.

## Target common transient method

Use the following as the method to qualify:

| Control | Target |
|---|---|
| Solver | pressure-based, transient |
| Pressure-velocity coupling | `PISO` with neighbor correction |
| Mixture VF formulation | implicit |
| Temporal discretization | bounded second-order implicit from timestep 1 where stable |
| Spatial discretization | preserve the verified predecessor schemes where compatible |
| Maximum iterations / timestep | approximately `15–20` |
| Timestep control | fixed during this first campaign |

If bounded second-order is clearly unusable during the startup period, a short common first-order startup may be tested. If adopted, it must be applied to **every later production case for the same physical-time interval** and recorded as part of the locked method.

## Timestep matrix

| Trial | Timestep | Role |
|---|---:|---|
| `DT-A` | `5.0e-4 s` | coarser candidate |
| `DT-B` | `2.5e-4 s` | primary finer comparison |
| `DT-C` | `1.25e-4 s` | run only if A/B materially disagree or convergence behavior remains questionable |

The current inlet characteristic scale is approximately:

```text
L = 0.724 m
U = 27.118 m/s
L/U ≈ 0.0267 s
```

The bracket therefore resolves that simple convective scale with roughly tens to hundreds of timesteps rather than choosing an arbitrary transient step.

## Qualification horizon

Initial comparison horizon:

```text
0.05 s
```

Extend all active timestep trials identically toward `0.10 s` if the initial window is dominated by startup adjustment or if the trajectories cannot yet be compared meaningfully.

## Required evidence

Compare at equal physical times:

- `V_l,Y010(t)`;
- `V_l,Y030(t)`;
- `V_l,total(t)`;
- liquid/vapour mass fluxes at both outlets;
- brine-pipe-entry pressure;
- residual histories within every timestep;
- iterations required per timestep;
- reverse-flow events and Fluent numerical warnings;
- transient liquid storage + flux closure.

## Per-timestep convergence diagnostic

Use `15–20` iterations per timestep as a maximum budget, not as a target that must always be exhausted.

A useful healthy pattern is that most timesteps settle without repeatedly hitting the maximum. If essentially every timestep reaches the cap, reduce timestep before simply increasing the cap.

Do not define success only as “Fluent did not crash.”

## Transient liquid balance

For the present no-phase-change campaign, interpret liquid storage with:

```text
dM_l/dt = m_dot_l,in - m_dot_l,brine - m_dot_l,steam
```

Compare the finite-difference inventory change over a timestep with the corresponding net liquid flux. Instantaneous inlet/outlet mismatch is not, by itself, a transient mass-balance failure.

## Selection rule

The user selects the **largest** timestep that is sufficiently similar to the finer qualified trajectory for the quantities that matter to this screening campaign.

Do not impose an invented percentage threshold unless the user later chooses one. The results should present the overlaid histories and the numerical-cost/convergence behavior needed for that decision.

Possible outcomes:

- `DT-A` and `DT-B` are sufficiently similar → lock `DT-A` for the screen;
- `DT-A` differs materially from `DT-B` → run `DT-C` and judge which trajectory is converging;
- all tested timesteps show poor per-step convergence → method is not qualified; revise the common transient method before Stage 5;
- only a short common first-order startup is stable → qualify and document that startup protocol before proceeding.

## Method-lock record

At the end of this stage, record one shared production method containing at minimum:

```text
selected initialization method
selected fixed timestep
pressure-velocity coupling
Mixture VF formulation
temporal scheme
any common startup scheme/time
maximum iterations per timestep
monitor sampling frequency
checkpoint frequency
```

No later outlet case may silently change one of these controls.

## Handoff

Proceed to [Stage 5 — Outlet-Family Compatibility Preflight](stage-05-outlet-family-preflight.md).