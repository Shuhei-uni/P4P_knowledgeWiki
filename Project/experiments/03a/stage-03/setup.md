# 03A Stage 3 — setup

## Question

Which combination of Fluent-recommended Mixture staging, progressive inlet/inertial loading, and momentum damping can produce a developed, numerically useful full-geometry steady field without changing the physical boundary condition?

The field must be judged from both solver behaviour and project-core behaviour: residual envelopes, total/phase flow, mass balance, liquid inventory, and brine-entry pressure.

## Why this experiment was selected

The 03A Stage-1 parent survived `1,000` steady iterations but retained high continuity and intermittent turbulence residuals. Stage 2 showed a short-lived improvement during a standard-`k-epsilon` bootstrap, but that improvement did not persist when RNG was restored. Stage 3 therefore tests a wider, predeclared continuation matrix while retaining RNG `k-epsilon` as the authority before changing physical model form.

## Parent and start state

- Use one verified 03A pre-initialization `P0` case/data parent with the frozen Stage-3 fingerprint.
- Derive every branch independently from that parent; do not start from a developed Stage-1 or Stage-2 field.
- Apply the branch state, positively read it back, then Hybrid Initialize exactly once.
- Do not reinitialize when Mixture equations or inlet loading are restored/advanced.

## Frozen physical context

| Item | Common state |
|---|---|
| Geometry | `Full-geomV2-231kcells.msh.h5` full separator with physical brine outlet |
| Solver | 3D, double precision, pressure-based, steady |
| Carrier model | Mixture; primary vapour, secondary liquid water |
| Turbulence | RNG `k-epsilon`, standard wall functions, swirl-dominated option on |
| Inlets | split pure-liquid/pure-steam faces, final `27.118 m/s` on each |
| Outlets | steam and brine pressure outlets, each `1.120 MPa` gauge |
| Other physics | gravity on; energy, liquid patch, DPM, and EWF off |
| Numerical authority | SIMPLE, PRESTO!, second-order momentum/turbulence, QUICK |

## Controlled factors and matrix

- **Mixture staging (`M`):** `M0` solves full Mixture immediately; `M1` temporarily disables volume fraction and slip velocity, solves the carrier field, then restores both without reinitialization.
- **Progressive loading (`S`):** `S0` starts at 100%; `S1` uses `10% → 20% → 40% → 80% → 100%` of `27.118 m/s`, changing both inlet faces together.
- **Momentum relaxation (`U`):** `U0 = 0.7`, `U1 = 0.5`, or `U2 = 0.3`, held constant within a branch.

| Branches | Mixture start | Inlet start | Momentum URF | Role |
|---|---|---|---:|---|
| F01 / F03 / F05 | M0 | S0 | 0.7 / 0.5 / 0.3 | full-Mixture full-load controls and damping |
| F02 / F04 / F06 | M1 | S0 | 0.7 / 0.5 / 0.3 | isolate carrier-first staging |
| F07 / F09 / F11 | M0 | S1 | 0.7 / 0.5 / 0.3 | progressive loading with full Mixture |
| F08 / F10 / F12 | M1 | S1 | 0.7 / 0.5 / 0.3 | combined staging strategies |

The full 2 × 2 × 3 matrix is the experiment; no extra turbulence-model, outlet-pressure, transient, DPM, EWF, or physics factor is included.

## Run horizon and transition rule

- Evaluate the common `stage3-gate-v1` using the latest `750` iterations every `250` iterations.
- If a preferred gate is not reached by `3,000` iterations at a state, save the evidence and force progression unless a hard numerical failure occurs.
- At 100% load, observe at least `5,000` final-condition iterations; stop only after three consecutive no-improvement assessments or at the `10,000` observation cap. The cap is not a convergence declaration.
- Record actual iteration ranges and preserve gaps, failed transitions, transport failures, and missing histories.

## Evidence required

Capture continuous histories wherever Fluent permits:

- all scaled residuals, with inactive Mixture equations marked as unavailable rather than zero;
- total and phase inlet/outlet flows, signed and relative mass imbalance;
- liquid → brine/steam and vapour → brine/steam routing;
- total, Y010, and Y030 liquid inventory;
- brine-entry static/total pressure and outlet/reverse-flow indicators.

Compare complete histories and common final-condition windows. Endpoint values alone cannot establish stationarity or qualify a parent.

## Source

[Original Stage-3 setup authority](../../../../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)
