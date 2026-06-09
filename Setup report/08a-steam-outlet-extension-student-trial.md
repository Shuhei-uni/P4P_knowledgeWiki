# Steam Outlet Extension Student-Edition Trial Setup Report

## 1. Purpose

Define a trial geometry branch from:

- [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)

This setup keeps the same Purnanto spiral-inlet separator geometry and the same pure liquid / pure steam split-inlet setup from `07`, except for a targeted steam-outlet geometry change:

- extend the central steam outlet pipe so the `steam_outlet` pressure-outlet boundary is placed farther downstream, near the bottom end of the extended outlet path;
- require flow that enters the central outlet pipe to travel along the outlet extension before reaching the boundary condition;
- test whether moving the pressure-outlet boundary away from the immediate outlet-pipe entrance reduces backflow reversal and unstable mass-flux reports.

This is a student-edition trial branch. Treat it as diagnostic until mesh quality, convergence, and flux stability are recorded.

## 2. Setup Identity

| Item | Value |
|---|---|
| Setup order | `08a` |
| Parent setup | `07-pure-phase-split-actual-area.md` |
| Geometry family | Purnanto rectangular 90-degree spiral-inlet BOC separator |
| Main retained feature | same separator body and same spiral inlet as Purnanto baseline |
| Inlet representation | same pure liquid / pure steam split inlet as setup `07` |
| New geometry change | extended central steam outlet pipe / outlet path |
| Outlet-boundary intent | place `steam_outlet` boundary downstream of the outlet-pipe entrance, not directly at the top intake opening |
| Licence / mesh context | student-edition trial |
| Evidence state | planned diagnostic geometry branch |

Evidence labels:

- `User-specified`: same setup as Purnanto's spiral inlet, with a split two-phase inlet.
- `User-specified`: actual separator geometry remains the same except earlier test setups with extended inlet pipe.
- `User-specified`: current trial extends the steam outlet so the pressure-outlet boundary is not located at the immediate entrance of the outlet pipe.
- `Inferred`: this branch tests outlet-boundary placement sensitivity, not a new separator design claim.
- `Assumed`: all setup `07` solver, inlet, material, and DPM settings remain unchanged unless this report explicitly says otherwise.

## 3. What Changes From Setup `07`

Change only the steam outlet geometry and boundary placement:

1. Keep the separator vessel, spiral inlet, and two-zone split inlet from setup `07`.
2. Add or extend the central steam outlet pipe so the pressure-outlet boundary face is farther downstream from the point where flow first enters the outlet pipe.
3. Place the named `steam_outlet` pressure-outlet boundary at the end of the extended outlet path.
4. Keep the opening from the separator core into the central outlet pipe as internal flow passage geometry, not as the external boundary-condition face.

Do not change the inlet split, phase velocities, phase volume fractions, turbulence model, mixture model, material properties, gravity, discretization schemes, or DPM interpretation rules in the same trial. If another setting must change because of student-edition limits, record it as a limitation before using the result for comparison.

## 4. Retained Inlet Boundary Package

Use the same inlet package as setup `07`:

| Field | Liquid inlet | Steam inlet |
|---|---:|---:|
| Boundary name | `inlet_liquid_outer` | `inlet_steam_inner` |
| Boundary type | `Velocity Inlet` | `Velocity Inlet` |
| Velocity magnitude | `27.118 m/s` | `27.118 m/s` |
| Liquid water volume fraction | `1.0` | `0.0` |
| Steam/vapor volume fraction | `0.0` | `1.0` |
| Turbulence intensity | `2.10999999 %` | `2.10999999 %` |
| Hydraulic diameter | `0.01338 m` | `0.72061 m` |

Expected inlet mass-flow targets remain:

```text
liquid inlet ~= 116.92 kg/s
steam inlet  ~= 80.69 kg/s
total inlet  ~= 197.61 kg/s
```

## 5. Retained Solver and Model Settings

Inherit setup `07` unless explicitly changed by Fluent during the student-edition rebuild:

| Setting | Value |
|---|---|
| Solver | `Pressure-Based` |
| Time | `Steady` |
| Multiphase model | `Mixture` |
| Primary phase | steam/vapor |
| Secondary phase | liquid water |
| Turbulence model | `RNG k-epsilon` |
| Energy | `Off` |
| Pressure-velocity coupling | `SIMPLE` |
| Pressure scheme | `PRESTO!` |
| Momentum scheme | `Second Order Upwind` |
| Turbulence schemes | `Second Order Upwind` |
| Volume fraction scheme | same as setup `07`, `QUICK` if available |
| Initialization | `Hybrid Initialization` |

## 6. Outlet-Extension Trial Rationale

Observed problem:

- `User-specified`: during previous runs, the steam outlet showed repeated backflow reversal and inconsistent mass-flux reporting.
- `User-specified`: the steam outlet boundary was placed at the very entrance of the outlet at the top, with a wider opening.

Working interpretation:

- `Inferred`: placing a pressure-outlet boundary directly at the intake of the central steam outlet pipe may let Fluent apply pressure-outlet/backflow behavior at a highly swirling, locally recirculating internal region.
- `Inferred`: moving the boundary condition downstream gives the core flow a finite outlet passage before it meets the pressure boundary, which may reduce artificial outlet-face reversal and make steam-outlet mass-flux reports less sensitive to local recirculation at the intake.
- `Uncertain`: this is a boundary-placement hypothesis, not proof that the physical separator would perform better. If liquid carryover changes, compare contours and DPM fate before attributing the change to real separation physics.

Lookup context:

- `Reported lookup`: Purnanto, Zarrouk, and Cater 2013 remains the direct CFD reconstruction source for the spiral-inlet BOC separator geometry, pressure-outlet setup, mixture model, and DPM outlet-quality workflow.
- `Reported lookup`: the lookup layer notes that Purnanto's spiral-inlet steam tube includes a design detail around the middle steam tube intended to limit water-film creep into the steam outlet.
- `Inferred`: the lookup supports keeping the Purnanto spiral-inlet body as the baseline geometry context, but it does not prove the proposed outlet extension will reduce backflow in this student-edition branch.

## 7. Geometry-Build Checklist

1. Start from the setup `07` geometry definition.
2. Preserve the Purnanto spiral inlet and main separator vessel dimensions.
3. Preserve the two separate inlet faces:
   - `inlet_liquid_outer`;
   - `inlet_steam_inner`.
4. Extend the central steam outlet pipe/path.
5. Name only the downstream end face of that extension as `steam_outlet`.
6. Confirm the former top/intake opening of the outlet pipe is not accidentally exported as a pressure outlet.
7. Confirm the new extension does not intersect the vessel wall, inlet path, or any bottom cut/wall surface.
8. Confirm mesh resolution in the outlet extension is sufficient to avoid a new artificial pressure-loss or skewness problem.

## 8. Pre-Run Checks

Before running iterations:

1. Confirm Fluent boundary zones:

```text
inlet_liquid_outer = Velocity Inlet
inlet_steam_inner  = Velocity Inlet
steam_outlet       = Pressure Outlet at downstream end of extension
```

2. Confirm the same setup `07` inlet targets:

```text
liquid inlet ~= 116.92 kg/s
steam inlet  ~= 80.69 kg/s
```

3. Confirm pressure-outlet backflow settings match setup `07`.
4. Check mesh statistics and note student-edition limits:

```text
nodes =
cells =
min orthogonal quality =
max skewness =
```

5. Save a pre-run case file after boundary assignment.

## 9. Result Interpretation Rules

Use this branch to test:

- whether downstream placement of the steam pressure-outlet boundary reduces outlet-face backflow reversal;
- whether steam-outlet phase mass-flux reports become more stable;
- whether the outlet extension changes DPM escaped/trapped/incomplete counts compared with setup `07`.

Do not use this branch to claim final separator performance unless:

1. inlet fluxes match setup `07`;
2. the mesh and solver settings are documented;
3. residuals and physical monitors are stable enough for the chosen evidence label;
4. phase fluxes are reported with Fluent sign convention preserved;
5. DPM counts are compared against setup `07` using the same particle settings.

## 10. Evidence to Save

Save at minimum:

```text
CAD/SpaceClaim geometry screenshot showing the outlet extension
boundary-zone screenshot
mesh statistics
case file before run
case/data after initialization
residual plot
inlet phase flux report
steam outlet phase flux report
velocity vectors near the central outlet intake
velocity vectors inside the outlet extension
liquid volume fraction near the outlet intake
DPM escaped/trapped/incomplete counts if particle tracking is repeated
```

Recommended trial label:

```text
PLS-STUDENT-OUTLET-EXT-2026-06-08
```

## 11. Comparison Against Setup `07`

Use setup `07` as the comparison parent:

| Metric | Setup `07` parent | Setup `08a` trial |
|---|---:|---:|
| Liquid inlet mass flow | record from run | pending |
| Steam inlet mass flow | record from run | pending |
| Steam outlet steam mass flow | record from run | pending |
| Steam outlet liquid mass flow | record from run | pending |
| Outlet-face backflow warnings | record from run notes | pending |
| DPM escaped / trapped / incomplete | record same diameter set | pending |

Primary decision question:

```text
Does moving the steam pressure-outlet boundary downstream reduce numerical outlet reversal without changing the split-inlet physics?
```
