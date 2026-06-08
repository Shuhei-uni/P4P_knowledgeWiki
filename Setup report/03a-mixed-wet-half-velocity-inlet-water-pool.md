# Mixed Wet-Half Velocity-Inlet With Initialized Water Pool Setup Report

## 1. Parent setup

This is a child setup of:

- [03-mixed-wet-half-velocity-inlet.md](03-mixed-wet-half-velocity-inlet.md)

Keep all parent setup values the same unless explicitly changed in this report.

Parent setup summary:

| Item | Value |
|---|---:|
| Solver | `Pressure-Based` |
| Time | `Steady` |
| Multiphase | `Mixture` |
| Primary phase | `steam` / `gas` / `vapor` |
| Secondary phase | `liquid water` |
| Turbulence | `RNG k-epsilon` |
| Energy | `Off` |
| Steam-only inlet velocity | `26.81 m/s` |
| Wet-half inlet velocity | `26.81 m/s` |
| Steam-only inlet liquid VF | `0.0` |
| Wet-half inlet liquid VF | `0.018656` |

## 2. Reason for this child test

The parent run gave a useful inlet result, but the brine outlet did not remove enough liquid.

Parent flux interpretation:

```text
Liquid in  = 109.8 kg/s
Liquid out = 5.66 + 2.5622 = 8.22 kg/s
Liquid retained / imbalance = 101.58 kg/s
```

The brine outlet removed only:

```text
liquid through brine outlet = 5.66 kg/s
steam through brine outlet  = 13.84 kg/s
```

This suggests the lower separator region did not have a physically established liquid inventory at startup.

## 3. Controlled changes in this child setup

Only change these items:

1. Initialize a lower water pool inside the separator.
2. Set outlet backflow phase fractions explicitly.

Do not change:

- inlet velocity
- inlet volume fractions
- turbulence model
- multiphase model
- material properties
- pressure-velocity coupling
- discretization schemes

## 4. Water-pool initialization target

The original paper assumed a constant water level just above the brine outlet pipe, while excluding the brine discharge region from its CFD model.

This full-geometry project model includes the brine outlet, so the first practical approximation is:

- initialize the lower separator region below the intended water level as liquid water
- initialize the region above that level as mostly steam/mixture from hybrid initialization

Target patch:

| Region | Liquid water volume fraction |
|---|---:|
| Lower water pool | `1.0` |
| Rest of domain | leave from Hybrid Initialization |

If the patch workflow requires patching the whole domain first, use:

1. Hybrid initialize.
2. Patch lower water-pool register to liquid VF `1.0`.
3. Do not patch the inlet boundary values; keep the inlet BCs from the parent setup.

## 5. Fluent 2024 R1 patch workflow

Use a cell register to mark the lower water-pool volume.

Suggested workflow:

1. Go to `Adapt > Region`.
2. Set `Shape = Box`.
3. Use coordinate bounds that cover the lower separator volume below the intended water level.
4. Click `Mark` to create a cell register.
5. Go to `Solution Initialization`.
6. Run `Hybrid Initialization`.
7. Go to `Patch`.
8. Choose variable: liquid water volume fraction / secondary phase volume fraction.
9. Select the lower water-pool cell register.
10. Set value: `1.0`.
11. Click `Patch`.
12. Verify with a contour of liquid volume fraction on a center plane.

Do not use boundary-face selection for this. The water pool must be patched into cells.

## 6. Outlet backflow settings

Set outlet backflow phase fractions deliberately.

| Boundary | Type | Backflow liquid VF | Backflow steam VF | Reason |
|---|---|---:|---:|---|
| steam outlet | `Pressure Outlet` | `0.0` | `1.0` | steam outlet should not inject liquid during local backflow |
| brine outlet | `Pressure Outlet` | `1.0` | `0.0` | brine outlet should not inject steam during local backflow |

These values affect only backflow conditions, but they matter if the pressure outlet locally reverses.

## 7. Boundary conditions retained from parent

| Boundary | Type | Main inputs |
|---|---|---|
| `inlet_steam_inner` | `Velocity Inlet` | `26.81 m/s`, normal to boundary, liquid VF `0.0` |
| `inlet_wet_outer` | `Velocity Inlet` | `26.81 m/s`, normal to boundary, liquid VF `0.018656` |
| steam outlet | `Pressure Outlet` | same pressure as parent, backflow liquid VF `0.0` |
| brine outlet | `Pressure Outlet` | same pressure as parent unless separately tested, backflow liquid VF `1.0` |

## 8. What to check after running

Check the same flux report as before:

```text
Liquid phase:
liquid inlet
liquid outlet
steam inlet
steam outlet

Steam phase:
liquid inlet
liquid outlet
steam inlet
steam outlet
```

Primary success signal:

- brine outlet liquid outflow should increase substantially from the parent value of `5.66 kg/s`

Secondary checks:

- steam through brine outlet should reduce from the parent value of `13.84 kg/s`
- liquid through steam outlet should remain low
- global liquid imbalance should reduce
- lower vessel should show a stable liquid region rather than immediate gas-dominated drain behavior

## 9. Interpretation rules

If liquid outlet flow increases strongly:

- water-pool initialization was necessary for the full-geometry brine outlet branch
- proceed to tune brine outlet pressure and water-level height

If liquid outlet flow remains low:

- brine outlet pressure/geometry is likely the dominant issue
- next test should vary brine outlet pressure or use an outflow/mass-flow outlet sensitivity case

If the water pool collapses or drains instantly:

- steady Mixture may not be adequate for establishing the liquid inventory
- next test should be transient with the same initial water pool

## 10. Execution checklist

| Done | Item | Target |
|---|---|---|
| [ ] | Keep parent inlet setup | unchanged |
| [ ] | Keep parent model stack | `Mixture`, `Steady` |
| [ ] | Hybrid initialize | complete |
| [ ] | Create lower water-pool cell register | below intended water level |
| [ ] | Patch liquid VF in water-pool register | `1.0` |
| [ ] | Steam outlet backflow liquid VF | `0.0` |
| [ ] | Brine outlet backflow liquid VF | `1.0` |
| [ ] | Run short test | completed |
| [ ] | Compare liquid outlet flow | target: much greater than `5.66 kg/s` |

## 11. Run result after 3500 iterations (2026-05-07)

### Visual result summary

After approximately `3500` steady iterations, the result looks more physically promising than the earlier low-iteration attempt.

Observed behavior:

- most of the initialized water has been swirled around inside the separator vessel
- much of that initialized water has left through the bottom/brine side of the separator
- liquid volume fraction remains higher near the bottom, but liquid is now spread more widely throughout the vessel
- static pressure is relatively uniformly distributed
- static pressure is highest near the vessel wall and lowest near the center, which is consistent with rotating separator flow
- at lower iteration counts the mixture did not circulate around the vessel as expected
- after `3500` iterations the flow now spins around the vessel in a more plausible circular pattern

This is a useful improvement over the parent run because the flow field now develops the intended separator swirl.

### Convergence status

The scaled residuals are still changing at `3500` iterations, so the solution should not be treated as fully converged.

However, the residuals have not changed strongly over the last approximately `1000` iterations. This makes the result acceptable for reporting rough qualitative behavior, but not for accurate final quantitative measures such as exact outlet liquid carryover, separator efficiency, or final mass split.

Interpretation level:

- qualitative flow pattern: usable as a rough first interpretation
- flux magnitudes: useful as warning indicators only
- final performance metrics: not yet reliable

### Flux report

Reported Fluent mass-flow fluxes:

```text
Liquid phase:
liquid inlet   =   109.8065 kg/s
liquid outlet  = -1413.05 kg/s
steam inlet    =     0.0 kg/s
steam outlet   = -1044.35 kg/s

Steam phase:
liquid inlet   =    37.6345 kg/s
liquid outlet  =   -14.455 kg/s
steam inlet    =    37.8277 kg/s
steam outlet   =   -45.54 kg/s
```

Using Fluent's usual sign convention:

- positive = entering the domain
- negative = leaving the domain

Phase totals:

```text
Liquid in  = 109.8065 kg/s
Liquid out = 1413.05 + 1044.35 = 2457.40 kg/s
Liquid net = 109.8065 - 2457.40 = -2347.59 kg/s

Steam in  = 37.6345 + 37.8277 = 75.4622 kg/s
Steam out = 14.455 + 45.54 = 59.995 kg/s
Steam net = 75.4622 - 59.995 = 15.4672 kg/s
```

### Interpretation

The qualitative flow behavior is encouraging, but the flux report is not yet physically acceptable.

The liquid outflow is far larger than the liquid inflow:

```text
liquid outlet total = 2457.40 kg/s
liquid inlet total  = 109.8065 kg/s
```

This means the initialized water pool is being drained from the domain, not just balancing the continuing inlet feed. The result should be interpreted as a transient-like depletion of the patched water inventory inside a steady solve, even though the solver mode is steady.

The brine outlet is now active, but the steam outlet is also removing a very large amount of liquid:

```text
liquid through brine outlet = 1413.05 kg/s
liquid through steam outlet = 1044.35 kg/s
```

The steam-outlet liquid flow is not acceptable for a separator target. This supports the user's visual interpretation: much of the initialized lower water was swirled upward/outward and some of it escaped through the steam outlet.

### Current diagnosis

This setup is a better starting point than the no-water-pool parent run because it produces separator-like swirl and a more plausible pressure pattern. However, it does not yet represent a stable operating separator.

Main concerns:

- the initialized water pool is being depleted rather than settling into a stable inventory
- liquid carryover through the steam outlet is extremely high
- the steady solver is being used to settle a strongly initialization-dependent liquid inventory
- steam outlet geometry may be trapping mixture or causing excess turbulence near the steam intake

### Steam outlet geometry concern

The steam outlet geometry is now a likely error source.

The current steam outlet geometry differs from the Bangma-style geometry, and the exact geometry was not specified clearly in the past paper. The current model uses a guessed steam outlet geometry.

Observed concern:

- the guessed steam outlet appears to create significant turbulence near the steam outlet intake
- this turbulence may trap mixture above the intake region
- trapped mixture near the outlet could increase liquid carryover into the steam outlet

This should be treated as a geometry sensitivity issue, not only a multiphase-model issue.

### Recommended next checks

Before changing many settings, collect more evidence from this run:

1. contour of liquid volume fraction near the steam outlet intake
2. velocity vectors around the steam outlet intake
3. streamline or pathline view showing whether liquid is being pulled into the steam outlet
4. flux report at several iteration counts to see whether liquid outflow is decreasing as the initialized pool drains
5. residual and mass-imbalance history around the final iteration

Possible next setup branches:

- run transient with the same initialized water pool to treat water inventory depletion properly
- revise the steam outlet intake geometry and compare liquid carryover
- test a shorter/lower initialized water pool height
- tune brine outlet pressure after the steam-outlet geometry behavior is understood
