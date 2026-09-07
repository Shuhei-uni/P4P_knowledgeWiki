# Split-Inlet Resolved Brine Outlet with Initial Liquid Pool

## Purpose and status

Setup `07h` is the controlled successor to the failed dry-start setup `07g`.
It tests whether the resolved brine pipe can establish the intended phase route
when the lower separator is initialized with liquid. The branch changes only
the initial phase distribution; it does not add a numerical sink or alter the
carrier physics, boundaries or solver controls.

- Study ID: `split_inlet_resolved_brine_outlet_20260813`
- Run label: `brine620k_07h_pool_y0_equal_psep_v1`
- Status: `Stopped after numerical divergence; terminal verified block iteration 250`.
- Classification: `Diagnostic / unresolved`.
- Parent: [07g-split-inlet-resolved-brine-outlet-qualification.md](07g-split-inlet-resolved-brine-outlet-qualification.md).
- DPM/EWF: off.
- Numerical sink: absent; no source UDF is loaded, compiled or hooked.

## Execution result (2026-08-16 NZST)

Preparation passed from the clean original mesh after the lower pool was
defined with a hexahedral Fluent cell register spanning `y <= 0 m`. Patching
the secondary-phase `mp` variable to `1.0` changed the domain-average liquid
volume fraction from `0.0` to `0.15826588`; all initialized setup validation
errors were empty and a separate initialized case/data pair was saved. Two
earlier preparation attempts stopped before iteration and are retained as
diagnostic automation evidence.

At iteration 25, both outlet mixture fluxes were outward. The steam outlet was
effectively vapor-only (`-80.376986 kg/s`), while the brine outlet discharged
`-25.299896 kg/s` liquid and only `-0.69597467 kg/s` vapor. This demonstrated
the intended initial phase route, but liquid recovery was only `21.64%` and
the early mixture imbalance was `46.17%`.

The iteration-250 block is the terminal verified block. Brine liquid outflow
then reached the nonphysical value `-3304.7817 kg/s`; mixture and liquid
imbalances were `1602.99%` and `2726.53%`, respectively. During the next
requested block, continuity, turbulence and pressure-correction residuals
grew catastrophically. Fluent printed its last residual row at 292, reported
AMG divergence and ended with a floating-point exception. Only 43 of the 250
requested residual advances were observed, so that block is not credited.

The existing `interrupt_iter250` pair contains this later failed live state;
its filename reflects the last credited block, not a physically valid
iteration-250 solution. The same state is therefore also preserved under the
explicit diagnostic label `post_fpe_residual_row292_unverified`. It must not
be used for quantitative flow conclusions.

Fluent also issued its mesh-specific recommendation to enable Warped-Face
Gradient Correction immediately after the legacy settings import. A later
live settings readback returned `{'enable': False}`. Because this is a 3D
polyhedral mesh, the disabled correction is a credible numerical-stability
and gradient-accuracy risk. It is not proven to be the sole cause of failure:
the nonphysical brine flux and unresolved downstream pressure/level condition
remain independent concerns. Any steady retry must start clean, change only
this method switch, read it back as enabled before initialization and use a
new non-overwriting branch; the failed live field must not be resumed.

## Evidence-based modelling decision

The resolved brine face has area `0.19936247 m2` and centroid
`y=-0.25417245 m`. Treating the face as approximately circular gives an
equivalent radius of about `0.252 m`, placing its crown near `y=0 m`. Setup
`07h` therefore initializes phase-2 liquid in cells satisfying:

```text
IF(Position.y <= 0 [m], 1, 0)
```

This is a geometry-derived initial-condition inference, not a measured plant
water level. It is deliberately lower and less aggressive than filling an
arbitrary large fraction of the vessel.

The steam and brine pressure-outlet inputs both remain `1.12 MPa`. With gravity
enabled Fluent interprets pressure boundary inputs using its modified-pressure
formulation, so no separate `rho*g*h` term is added to the lower outlet input.
The unresolved real downstream brine pressure remains an external input for a
later sensitivity or validation case.

## Authoritative inputs

- Clean mesh:
  `C:\Users\qtra338\Documents\Mesh study\Meshes\brine-outlet-620kcells.msh.h5`
- Mesh SHA-256:
  `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`
- Settings:
  `C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set`
- Fluent: `2024 R2`, 16 partitions.
- Mesh: 620,431 cells, `27.06309 m3`, characteristic size
  `0.03520151 m`, minimum orthogonal quality `0.250003`, maximum aspect ratio
  `66.0258`, no negative-volume error.

## Fixed carrier setup

- steady, pressure-based Mixture model;
- primary phase `water-vapor-at-psep`;
- secondary phase `water-liquid-at-psep`;
- RNG k-epsilon turbulence;
- gravity `(0,-9.81,0) m/s2`;
- Energy off;
- SIMPLE/PRESTO with imported discretization and under-relaxation factors;
- liquid inlet `116.92 kg/s` and steam inlet `80.69 kg/s`;
- steam outlet pressure `1.12 MPa`, steam-dominant backflow;
- brine outlet pressure `1.12 MPa`, phase-2 backflow volume fraction `1.0`;
- operating pressure `0 Pa` and operating-density method
  `minimum-phase-averaged`;
- fresh Hybrid Initialization followed by the liquid-volume-fraction patch;
- no saved setup-07g field, DPM, EWF or source terms.

All setup setters must be read back after import and customization. The
critical settings fingerprint must match the accepted setup-07g preparation;
the initial phase distribution is the intended difference.

## Guarded execution plan

1. Load the clean mesh, normalize the seven canonical zones and import the
   authoritative settings.
2. Configure and read back `brineoutlet`, verify both wall zones and prove that
   no legacy `bottom` wall or cell source exists.
3. Hybrid-initialize, create/read back a hexahedral cell register spanning
   `y<=0 m` and patch phase-2 liquid volume fraction. Require a bounded,
   measurable change in the domain-average liquid fraction.
4. Save a separate initialized case/data pair.
5. Cold-reload that pair and run `25`, `225`, then `250`-iteration blocks.
6. Save separate checkpoints at iterations `25`, `250`, `500`, `1000`, `2000`
   and `3000`.
7. At iteration 1000, continue only if steam and brine mixture flows are both
   outward, steam vapor is outward, brine liquid is outward, brine vapor is no
   more than `25%` of vapor feed and steam liquid is no more than `10%` of
   liquid feed.
8. Stop immediately on non-finite fields or gross divergence.

The 1000-iteration gate is a diagnostic routing gate, not convergence proof.
At 3000 iterations acceptance additionally requires mixture, vapor and liquid
imbalance each no more than `0.5%`; primary monitor drift no more than `0.5%`;
secondary velocity, vorticity and liquid-inventory drift no more than `1%` over
iterations 2500-3000; correct outlet directions; and bounded, non-growing
residual histories.

## Outputs

Local output root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07h_pool_y0_equal_psep_v1/
```

Expected files include `preparation_manifest.json`,
`qualification_manifest.json`, complete settings readbacks, preparation and
qualification transcripts, `residual_history.csv`,
`physical_monitor_history.csv`, `qualification_metrics.json`, and the named
non-overwriting case/data checkpoints listed above. Remote files are written
under:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_resolved_brine_outlet_20260813\
```

Status command:

```bash
cd PyAnsys
.venv/bin/python scripts/connection/check_setup07h_status.py
```

The detached supervisor manifest is
`PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07h_pool_y0_equal_psep_v1/supervisor_manifest.json`.
It retries connection/authentication failures for up to 18 hours and executes
preparation plus qualification once Fluent passes the read-only gate. It does
not blindly repeat a failed preparation or calculation.

## Decision rule

- `Accepted`: use setup `07h` only as the one-mesh carrier/boundary baseline,
  then build a systematic brine-geometry mesh sequence before DPM or EWF.
- `Diagnostic/unresolved`: if correct routing is not established, preserve the
  checkpoints and do not tune outlet pressure without downstream evidence.
- `Transient successor required`: if the steady solution is materially
  dependent on the patched inventory, drains the pool, or remains
  iteration-dependent, repeat this same initialized geometry in a transient
  formulation with liquid inventory and both outlet phase fluxes monitored in
  physical time.
