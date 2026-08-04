# Successful Fluent Paths Log

Add working paths/orders here as the agent discovers them in the live Fluent session.

## Example format

```text
Fluent: 2024 R2
PyFluent: <version>
Case: <case>
Goal: bind DPM injection surface to steaminlet
Order:
  1. enabled DPM
  2. created default injection
  3. reacquired injection object
  4. set particle_type = inert
  5. reacquired injection object
  6. set injection_type = surface
  7. reacquired injection object
  8. set location/surface = <working format>
Working path or TUI:
  <path or command>
Readback:
  <value>
Notes:
  <notes>
```

## 2026-07-21 to 2026-07-25 | Purnanto enthalpy DPM sweeps

Evidence: `Observed` in Fluent 2024 R2 controller logs, case manifests, and DPM reports.

PyFluent controller package: the current environment is `0.39.0`; the exact
package version was not separately written into each run manifest.

### Purnanto baseline / Bangma-target branch

```text
Case: C:\Users\qtra338\Documents\baseline.cas.h5
Inlet: inlet
Outlets observed in DPM report: steam_outlet (escaped), fluid_outlet (trapped)
Injection names: injection-0 through injection-8
Particle material: water-liquid-dpm
Order:
  1. loaded the baseline case fresh
  2. reacquired the mass-flow inlet and DPM injection branch
  3. set particle_type = inert
  4. reacquired injection
  5. set material = water-liquid-dpm
  6. reacquired injection
  7. set injection_type.option = surface
  8. reacquired injection
  9. set initial_values.location.injection_surfaces = [inlet]
  10. set initial_values.mass_flow_rate.total_flow_rate
  11. set initial_values.velocity.use_face_normal_direction = true
  12. reacquired injection
  13. set initial_values.velocity.magnitude = abs(z_velocity_ms)
  14. set uniform particle diameter
  15. read back and validate every field
Readback:
  Nine injection readbacks were verified in controller logs for every case.
  Cases 4-6 also preserve full pre- and post-DPM injection states in manifests.
```

### Spiral-inlet branch

```text
Case: C:\Users\qtra338\Documents\baseline_spiral_inlet.cas.h5
Inlet: inlet
Outlets observed in DPM report: outlet (escaped), bottom (trapped)
Injection names: injection-5-micron, injection-28-micron,
  injection-56-micron, injection-112-micron, injection-168-micron,
  injection-348-micron, injection-562-micron, injection-844-micron,
  injection-1631-micron
Particle material: liquid-water
Order and setting paths: same as the baseline branch above.
Readback:
  All nine pre- and post-DPM injection states are present in every final manifest.
```

### DPM reporting

```text
Order:
  1. enable per-injection zone summaries
  2. run /solve/dpm-update
  3. run aggregate DPM summary
  4. write one extended-summary scratch file per injection
  5. parse escaped, trapped, and incomplete Final mass flow
  6. reconcile fate mass against injected mass
Observed report columns:
  Mass Flow (kg/s): Initial, Final, Change
Result:
  Initial and Final were equal for these inert, isothermal runs.
  All 12 case-level DPM mass-balance audits passed the 0.2% tolerance.
```

Known evidence limits:

- Case 1 of the baseline sweep has block-by-block monitor evidence through
  iteration 1500 but no mirrored standalone residual-history CSV.
- Cases 1-3 of the baseline sweep predate full pre/post injection-state storage
  in the final manifest; their controller logs still record nine successful
  injection readback validations.
- Face-normal velocity is stored as a positive magnitude. The CSV negative
  `z_velocity_ms` is provenance for the earlier Cartesian definition, not the
  value entered when face-normal mode is active.
- These observations do not prove carrier-flow convergence.
