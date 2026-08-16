# FG-MIX-T01 Stage 3 — NP-DT1 No-patch transient control

## Execution status

`NP-DT1` failed with a Fluent floating-point exception before the requested
`200` transient-step / `0.05 s` window completed. No paired transient endpoint
was written. `NP-DT2` was not launched automatically.

This report records the executed no-patch control defined in the [Stage-3
setup plan](../../../../full-geometry/mixture/transient-liquid-outlet/stage-03-initialization-comparison.md).

## Actual run definition

| Item | Actual state |
|---|---|
| Run ID | `FG-MIX-T01-S3-NP-DT1-2026-08-17` |
| Initial field | verified unpatched steady `FG-MIX-T01-S1-C1375` parent |
| Mesh | `Full-geomV2-231kcells.msh.h5`; `231,376` cells; `697,078` nodes |
| Multiphase model | Mixture; implicit volume-fraction treatment |
| Turbulence | inherited RNG `k-epsilon` |
| Transient formulation | bounded second-order implicit |
| Coupling | inherited current PISO settings with one neighbor-correction iteration |
| Brine pressure outlet | `1.120 MPa` gauge |
| Steam pressure outlet | `1.120 MPa` gauge |
| Y010 patch | none |
| Hybrid Initialization after parent load | none |
| Timestep | `2.5e-4 s` |
| Requested native transient steps | `200` |
| Maximum iterations per timestep | `20` |
| Nominal physical horizon | `0.05 s` |

The steady-parent source pair was:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T104203Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T104203Z.dat.h5
```

A fresh no-patch transient start pair was written and reload-verified before
the native journal was submitted:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-NP-DT1-0p05s-20260816T132226Z-start.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-NP-DT1-0p05s-20260816T132226Z-start.dat.h5
```

## Numerical outcome

The native journal loaded the fresh start pair, set the requested timestep,
enabled residual printing and transcript capture, and entered
`/solve/iterate 200`. Fluent then exhibited the following sequence:

- residuals initially rose from continuity `2.2536e-1` at the loaded-field
  residual row to `9.7418e-1`, `1.3713e+0`, `2.0616e+0`, and `3.2758e+0`;
- continuity then reached `7.6823e+0`, `2.2440e+2`, `8.4960e+6`,
  `6.6879e+16`, and `3.2426e+51`;
- turbulent-viscosity limiting increased from localized cells to all
  `231,376` cells;
- reversed flow was reported at both pressure outlets, including pressure
  outlet zones `30` and `28`;
- AMG divergence was reported for pressure correction, `k`, `epsilon`, and
  `vof-1`;
- Fluent terminated with a host/node floating-point exception and interrupted
  journal processing.

The final displayed residual row before the exception was global residual
label `1028`. Fluent’s read-only monitor exposed the loaded field’s global
residual coordinate rather than a trustworthy transient-step coordinate, and
the journal did not write a completed endpoint. Therefore the exact completed
transient step and physical time at divergence are **not independently
recoverable from this run** and are not inferred here.

The native transcript exists remotely, but the endpoint and residual-export
files do not:

```text
Transcript:
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S3-NP-DT1-0p05s-20260816T132226Z.trn

Endpoint pair: absent
Residual export: absent
```

No Y010/Y030 inventory analysis was performed. The no-patch control did not
impose an initial liquid pool, and the primary diagnostic outputs were the
native residuals, solver warnings, reverse-flow reports, and viscosity-limit
evidence.

## Interpretation status

`NP-DT1` does not support the statement that transient conversion is viable at
`2.5e-4 s` under the unchanged formulation. It demonstrates that the
unpatched steady-parent start still fails under the tested `1.120 MPa`/`1.120
MPa` outlet condition, but this run alone does not distinguish whether the
dominant cause is timestep resolution, the inherited parent field, outlet
physics, or another coupled numerical mechanism.

Interpretation status: pending user direction.

No automatic `NP-DT2` submission was made. The next authorized numerical
variable, if selected, is `dt = 1.25e-4 s` with the same steady parent,
outlets, models, PISO settings, discretization, and no-patch condition.

## Evidence artifacts

- [NP-DT1 runner](../../../../PyAnsys/scripts/setup/run_fg_mix_t01_stage3_no_patch_dt1.py)
- [NP-DT1 native journal](../../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step.jou)
- [NP-DT1 result manifest](../../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step_20260817.json)
- [Stage-3 setup plan](../../../../full-geometry/mixture/transient-liquid-outlet/stage-03-initialization-comparison.md)
