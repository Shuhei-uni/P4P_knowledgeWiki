> **Legacy source:** Setups/reports/full-geometry/mixture/transient-liquid-outlet/stage-03/stage-03-initialization-comparison-20260816.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Stage-3 Initialization Comparison — FG-MIX-T01

## Current status

The replacement Stage-3 native queue was submitted from the monitor-ready pairs, but the `INIT-H` branch terminated with a Fluent floating-point exception at transient step `53` before writing its endpoint. `INIT-S` did not begin. The earlier queue had already been canceled at the user's request; neither attempt produced a completed Stage-3 comparison.

The requested horizon for the replacement run was:

- timestep: `2.5e-4 s`
- steps: `1,000`
- nominal physical horizon: `0.25 s`

The replacement journal stopped during `INIT-H` after severe residual growth, full-domain turbulent-viscosity limiting, reversed pressure-outlet flow, AMG divergence, and the floating-point exception. Fluent was returned to an idle state and the open transcript was closed. Neither branch wrote a paired Stage-3 case/data endpoint, so the failed run is excluded from the initialization comparison.

## Replacement-run result

- Start-state reload and readback passed for both monitor-ready branches on the locked mesh: `231,376` cells and `697,078` nodes.
- Both branches read back Mixture, `1.200 MPa` brine pressure, `2.5e-4 s` timestep, zero flow time, and the expected Y010/Y030 registers.
- `INIT-H` entered the native `1,000`-step solve and failed at step `53`; the terminal residual sequence reached continuity `3.1443e+57` at step `53` before Fluent reported AMG divergence and a floating-point exception.
- At step `51`, turbulent-viscosity limiting affected all `231,376` cells; reversed flow was reported at both pressure outlets.
- `INIT-S` was never started.
- No paired endpoint exists for either branch. The partial transcript is retained for diagnosis only.

## Cancellation record

- Native solver interrupt succeeded.
- No Stage-3 endpoint exists for either branch.
- The available `INIT-H` transcript is partial and is not a complete physical-time history.
- No comparison result or stability ranking is inferred from this canceled attempt.
- The original submission journal and manifest remain as audit records.

## Total liquid mass tracking

The canceled attempt did not produce a reliable total-liquid-mass history. The saved Stage-2 start pairs were therefore reloaded without reinitializing, repatching, or advancing the solution, and new monitor-ready copies were written with a direct full-domain phase-2 `volume-mass` report:

```text
report name:        fg_mix_t01_s3_total_liquid_mass
report type:        volume-mass
phase:              phase-2
cell zone:          simple-spiral-separator--brine-outlet-
create report file: true after reload verification
create report plot: true after reload verification
```

Monitor-ready input pairs:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-INIT-H-TPO1-0p25s-massmon-start-20260816T124000Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-INIT-H-TPO1-0p25s-massmon-start-20260816T124000Z.dat.h5

C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-INIT-S-TPO1-0p25s-massmon-start-20260816T124000Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-INIT-S-TPO1-0p25s-massmon-start-20260816T124000Z.dat.h5
```

Both monitor-ready pairs reloaded against the locked `Full-geomV2-231kcells.msh.h5` mesh with `231,376` cells and `697,078` nodes, and the direct mass report survived reload verification. The replacement run loaded that report before stepping, but the `INIT-H` floating-point exception occurred at step `53`; therefore no complete or scientifically usable total-liquid-mass trajectory was produced.

## Handoff

The monitor-ready pairs remain available, but the current Stage-3 attempt is failed rather than complete. Any further run requires a new numerical-stability decision; no automatic retry has been submitted.

Audit artifacts:

- total-mass monitor manifest (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_total_mass_monitor_20260816T124000Z.json`; not migrated)
- canceled submission manifest (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T120500Z.json`; not migrated)
- canceled submission journal (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T120500Z.jou`; not migrated)
- replacement failed-run manifest (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T115435Z.json`; not migrated)
- replacement failed-run journal (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_initialization_comparison_20260816T115435Z.jou`; not migrated)
