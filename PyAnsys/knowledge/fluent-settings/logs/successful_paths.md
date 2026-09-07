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

## 2026-08-25 | Post-processing-only VOF carrier-pathline video

Evidence: `Observed` in Fluent 2024 R2 and checksum-bound setup-07n attempt-3
graphics manifest.

```text
Case: accepted independent server-2 0.05%-feed step-100 pair
Goal: export carrier-flow pathway frames with DPM remaining zero/off
Order:
  1. acquire the setup-07n server-2 advisory lock
  2. connect one client and verify SERVING, 2024 R2 and ranks n0..n15
  3. hash and cold-load the case/data pair; reacquire all settings branches
  4. verify clock, pressure, inlet rates, phases, DPM, EWF and sources
  5. create/reacquire results.graphics.mesh and results.graphics.pathline
  6. set velocity_domain=all-phases, field=velocity-magnitude
  7. set release_from_surfaces=[liquidinlet] and read it back exactly
  8. set step/skip/coarsen, options, style and color map; read back
  9. display the mesh, add the pathline, set the fixed camera
  10. save PNG through results.graphics.picture.save_picture
  11. copy and hash the PNG; encode retained frames locally with H.264
Working settings path:
  solver.settings.results.graphics.pathline[object_name]
Working hardcopy path:
  solver.settings.results.graphics.picture.save_picture(file_name=...)
Observed seeds:
  827 from liquidinlet
Version-specific caveats:
  pathline.range.option allowed auto-range and clip-to-range; auto-range-off
  was rejected. A requested steaminlet release read back as wall-fluid and was
  rejected. Do not use graphics.particle_track when DPM is off.
Interpretation:
  frozen-field massless carrier pathlines; not droplets, parcels, phase-specific
  histories, carryover or efficiency evidence.
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

## 2026-08-19 | Parse Fluent node IDs, not the connectivity core denominator

Evidence: `Observed` in the setup-07i attempt-8 and restarted-session Fluent
parallel connectivity reports; `Implemented / live verified` in the
pre-mutation Settings-API gate.

```text
Failure mode:
  connectivity rows                  = n0 through n15
  Core column example                = 16/20
  incorrect interpretation           = 20 Fluent processes
  correct interpretation             = 16 solver processes on 20 hardware cores
Impact:
  setup-07i attempt 8 was initially misclassified as process-count invalid;
  its valid 16-process numerical failure was temporarily obscured
Safe order:
  1. connect/authenticate to the intended Fluent server
  2. call settings.parallel.show_connectivity(compute_node=0)
  3. parse unique node IDs and require the contiguous roster n0..n15
  4. record the Core denominators separately as hardware-core counts
  5. only after the gate passes may remote directories, mesh/case, settings or
     initialization be changed
  6. fail closed if the roster is unavailable, non-contiguous or mismatched
Observed result:
  setup-07i attempt 8 used 16 processes, continuity reached 6.9888e14 at
  transcript iteration 20, and the GUI recorded Node-4 SIGSEGV/server shutdown
  at iteration 21; zero complete blocks were credited and the state is not resumable
```

Fluent 2024 R2 did not expose `(parallel/number-of-compute-nodes)` in the live
Scheme environment. The Settings API connectivity path above is live-verified,
and the exact-16, mismatch and denominator-regression paths have unit coverage.

## 2026-08-07 | Fluent 2024 R2 compiled cell-zone source UDF

Evidence: `Observed` in setup-07b preparation manifests, compile transcripts,
source readbacks and cold-reload verification.

```text
Goal: remove phase-2 liquid in bottom-adjacent cells while retaining bottom as a wall
Fluent: 2024 R2, 16 partitions
Order:
  1. load the clean original mesh and verify its hash, zones and quality
  2. transfer the authoritative case-only/settings definition; do not load data
  3. verify complete settings fingerprint and fresh Hybrid Initialize
  4. allocate user_defined_memory(5)
  5. compile/load the content-hashed source with Fluent's built-in Clang
  6. require the positive five-UDM reservation message and named UDM readback
  7. set the liquid mass and mixture momentum source term lists atomically
  8. reacquire and read back the complete liquid, vapor and mixture source containers
  9. set/read RP controls, save at ramp zero, cold reload and repeat verification
Working result:
  liquid mass: cwl_liquid_mass_sink on phase-2 fluid
  vapor mass: disabled
  mixture momentum: cwl_x/y/z_momentum_sink
  UDMs: mask, mass source, x/y/z momentum source
  library: lib07b_cwl_bdfa31b0ec_r4_clean1
Readback:
  no validation errors after cold reload; ramp=0; DPM off
Notes:
  Fluent 2024 R2 ListObject children can become stale after list resize. Atomic
  list assignment plus object reacquisition was reliable. A successful UDF
  load without the reservation transcript was not sufficient and produced a
  deliberately rejected case in an earlier attempt.
```

## 2026-08-11 | Runtime resize of verified bottom-local sink band

Evidence: `Observed` in setup-07f first-case preflight and saved start manifest.

```text
Goal: reuse the verified setup-07c compiled source while changing only the
      bottom-local band height and fixed tau from a clean origin
Fluent: 2024 R2, 16 partitions
Order:
  1. restore setup-07c's verified source-hooked clean prepared case/data
  2. reacquire and validate complete settings/source hooks and DPM-off state
  3. set RP user/cwl07c/tau-s and user/cwl07c/layer-thickness-m
  4. set/read RP ramp=0 and read every RP control back
  5. fresh Hybrid Initialize
  6. execute cwl07c_rebuild_sink_mask on demand
  7. validate UDF console count/volume/centroid range against the UDM volume integral
  8. save a new run-local ramp-zero case/data pair before iteration
Observed first case:
  thickness requested/read back: 0.28033050723644937 m
  tau requested/read back: 0.02 s
  mask: 184145 cells; UDF volume 0.887048 m3; field integral 0.88704756 m3
  DPM: off
Notes:
  Runtime RP mutation avoids recompiling or double-reserving UDMs in a
  persistent session. Setter success alone is insufficient; require RP,
  console-mask and field-integral readback before solving.
  The inherited Adjust hook rebuilt this fixed mask every iteration and cost
  about 8-11 min/iteration on the 5.3M-cell case. Clearing only the Adjust
  hook after the accepted on-demand build, then executing the on-demand
  builder whenever thickness/tau/ramp changes, retained RP and DPM readback
  and reduced a live smoke iteration to 6.17 s. Formal runs must restart from
  clean origin and preserve this scheduling change in the manifest.
```

## 2026-08-22 | Fresh explicit-VOF pool patch and guarded dt extension

Evidence: `Observed` in setup-07n-a lower-face-proxy pilot attempt 4 and its
first `dt=2e-6 s` extension on Fluent 2024 R2 / PyFluent 0.39.

```text
Safe fresh-pool order:
  1. acquire one stable study-wide flock and audit exact local processes
  2. perform raw TCP preflight, then connect one owner with cleanup_on_exit=False
  3. require no other connected client, Fluent 2024 R2 and roster n0..n15
  4. hash and read the settings-carrier CASE only; never read its DAT
  5. reacquire/read back VOF, PISO/PRESTO/Geo-Reconstruct/WFGC, BCs,
     zero DPM injections/off, all sources off and EWF RP state #f
  6. Hybrid Initialize, recreate the exact cell register, patch phase-2 mp=1
  7. prove marked-cell count, VOF/inventory/extrema/brine-face coverage and t=0
  8. save/hash a unique t0 CASE+DAT, cold reload it and repeat every gate
  9. advance exactly one physical step per RPC and persist clock observation
     before post-solve report collection
 10. save/hash separate checkpoints and never overwrite failed attempts
Observed:
  98473 cells; liquid inventory 3877.468071 kg; ten dt=1e-6 s plus ten
  dt=2e-6 s steps; all gates passed through cumulative t=30 us
Version-specific report rules:
  - volume_integrals minimum/maximum works with cell_zones=['fluid']; omit
    volumes=[] because Fluent 2024 R2 otherwise reaches unbound pm/volumes
  - surface_integrals has no minimum/maximum child; brine-face VF extrema were
    read from the field-data service and its area average reported separately
  - EWF-off proof used (rpgetvar 'sg-wallfilm?) => #f plus empty model params
Evidence limitation:
  a boundary-face-height proxy and 30 us startup do not validate a physical
  pool level or dynamic relaxation
```

## 2026-08-22 | Exact whole-cell threshold plateau and checksum-bound same-dt holds

Evidence: `Observed` in setup-07n Stage-0 plateau attempt 4 and the
mesh-selected closed-drain startup/extension manifests on Fluent 2024 R2 /
PyFluent 0.39.

```text
Goal 1: determine a register threshold that reproducibly selects one whole-cell pool
Working observation order:
  1. cold-read the checksum-bound carrier CASE only and prove rank/settings gates
  2. Hybrid Initialize once
  3. create a unique hexahedral inside/max-point/min-point cell register
  4. patch phase-2 mp=1 through solution.initialization.patch.calculate_patch
  5. obtain the marked count from the post-patch transcript, not register creation
  6. patch the same register back to mp=0 before the next threshold query
  7. delete/recreate and reacquire each temporary register
  8. bisection-bracket both count transitions, then verify the centered threshold
Observed:
  invariant 98473-cell interval:
    [0.01640233030449599, 0.01651440086495131] m
  centered threshold: 0.01645836558472365 m
  liquid volume/inventory: 4.400159116224599 m3 / 3877.4680713930516 kg
Failure signatures:
  - register creation emits no marked-cell count in this 24.2 path
  - redirecting the live stream before the post-load rank proof can hide n0..n15
  - the direct volume-cell mesh RPC remains UNIMPLEMENTED

Goal 2: continue an expensive transient without inheriting an in-memory field
Working order:
  1. require absent exact local PID/controller and acquire the study-wide flock
  2. raw TCP preflight, authenticate one owner, then prove exclusive client/version/ranks
  3. remotely rehash the exact parent CASE and DAT before cold load
  4. read case and data, reacquire all branches, prove settings and exact clock
  5. set/read transient_controls.time_step_size and max_iter_per_time_step
  6. run one physical step per RPC; record clock before expensive post-step reports
  7. gate end continuity, Global Courant, VOF extrema, pressure/velocity,
     brine coverage, phase inventory/storage and DPM/EWF/source state
  8. save/hash unique step-1, step-5 and endpoint pairs
Observed:
  factor-two dt ladder 1e-6 -> 2.56e-4 s, followed by same-dt holds;
  all hard gates passed through cumulative step 240 / 0.04351 s
Interpretation:
  numerical residual passage does not prove physical stationarity; the
  velocity/vorticity window must flatten and a matched dt/2 window is required
```

## 2026-08-25 | VOF pressure-outlet drainage and mass-flow-outlet capability

Evidence: live Fluent 2024 R2 / PyFluent 0.39 setup-07n server-2 diagnostics.

```text
VOF mass-flow-outlet object:
  mixture mass_flow_specification exists
  mixture mass_flow_rate does not exist
  phase-1 and phase-2 mass_flow_rate children are writable
Interpretation:
  no single bulk rate is exposed; setting phasic rates prescribes routing.

Working pressure-outlet order:
  cold-load one checksum-bound liquid-sealed parent per member; set/read only
  brine pressure and common inlet fraction; advance one step per RPC; gate
  continuity, Global Courant, phase fluxes, brine-face VF, extrema,
  inventory/storage, clock, DPM, EWF and sources; save/hash unique checkpoints.
Observed:
  at 0.05% feed and 1122263.621237 Pa, liquid/vapor nets were -9.93e-8 and
  +8.21e-9 kg/s after ten steps; brine-face VF stayed 1.0 and leakage was zero.
Limit:
  pressure is CFD-interpolated, not plant-valid; 0.0625% feed failed the
  first-step continuity envelope although Courant and fields stayed bounded.
```
