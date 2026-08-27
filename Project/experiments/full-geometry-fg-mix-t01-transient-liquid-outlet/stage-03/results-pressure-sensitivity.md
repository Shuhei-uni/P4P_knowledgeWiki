> **Legacy source:** Setups/reports/full-geometry/mixture/transient-liquid-outlet/stage-03/stage-03-pressure-sensitivity-20260817.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Stage-3 Pressure Sensitivity — FG-MIX-T01 — 2026-08-17

## Execution status

The shortened pressure-sensitivity sweep was prepared from the verified
Stage-3 `INIT-S` and `INIT-H` monitor-ready start pairs and submitted to
Fluent on the `student` endpoint. The sweep used the current provisional
transient method:

- pressure outlet grid: `1.120` through `1.200 MPa` gauge in `0.010 MPa`
  increments;
- timestep size: `2.5e-4 s`;
- requested native transient steps per pressure: `200`;
- nominal physical horizon per pressure: `0.05 s`;
- maximum iterations per timestep: `20`;
- solver: pressure-based Mixture, bounded second-order transient;
- branches attempted: `INIT-S` and `INIT-H`.

All eighteen pressure siblings (nine per branch) were written as paired
case/data start artifacts and reload-verified before the independent native
journals were submitted. The immutable Stage-3 source case/data pairs were not
overwritten.

## INIT-S run outcome

The native journal began with the `INIT-S` case at `1.120 MPa` gauge. Fluent
remained reachable and reported `Status.SERVING`, but the residuals grew
catastrophically during the first pressure case. The independent-case runner
then closed the failed transcript, reloaded the next prepared start pair, and
continued through every remaining pressure level:

| Brine outlet pressure | Prepared start pair | Native endpoint pair | Transcript | Outcome |
|---:|---|---|---|---|
| `1.120 MPa` gauge | present | absent | present | floating-point failure |
| `1.130 MPa` gauge | present | absent | present | floating-point failure |
| `1.140 MPa` gauge | present | absent | present | floating-point failure |
| `1.150 MPa` gauge | present | absent | present | floating-point failure |
| `1.160 MPa` gauge | present | absent | present | floating-point failure |
| `1.170 MPa` gauge | present | absent | present | floating-point failure |
| `1.180 MPa` gauge | present | absent | present | floating-point failure |
| `1.190 MPa` gauge | present | absent | present | floating-point failure |
| `1.200 MPa` gauge | present | absent | present | floating-point failure |

Every attempted pressure showed reversed flow and expanding
turbulent-viscosity limiting before AMG divergence and a floating-point
exception. The exact completed transient-step count could not be
independently recovered from the available read-only monitor because the live
iteration coordinate retained the loaded field's global iteration label rather
than exposing a transient-step count.

## INIT-H run outcome

After the complete `INIT-S` sweep, the same nine pressure levels were prepared
from the verified `INIT-H` monitor-ready start pair and submitted one at a time.
Each case was started from its own prepared pair. When Fluent raised the
floating-point exception, the transcript was closed and the next independent
prepared pair was submitted without changing the timestep, per-timestep
iteration cap, solver, or multiphase controls.

| Brine outlet pressure | Prepared start pair | Native endpoint pair | Transcript | Outcome |
|---:|---|---|---|---|
| `1.120 MPa` gauge | present | absent | present | floating-point failure |
| `1.130 MPa` gauge | present | absent | present | floating-point failure |
| `1.140 MPa` gauge | present | absent | present | floating-point failure |
| `1.150 MPa` gauge | present | absent | present | floating-point failure |
| `1.160 MPa` gauge | present | absent | present | floating-point failure |
| `1.170 MPa` gauge | present | absent | present | floating-point failure |
| `1.180 MPa` gauge | present | absent | present | floating-point failure |
| `1.190 MPa` gauge | present | absent | present | floating-point failure |
| `1.200 MPa` gauge | present | absent | present | floating-point failure |

The `INIT-H` cases reproduced the same failure signature: reversed flow,
turbulent-viscosity limiting, rapidly growing residuals, AMG divergence, and a
floating-point exception. No pressure in the nine-point grid reached the
requested 200 native transient steps or wrote a paired endpoint. As with
`INIT-S`, the exact transient-step count at failure is not claimed because the
available monitor label does not provide a reliable transient-step count.

The pressure sweep is therefore **complete for both initialization branches as
an attempted screen but failed at every pressure**, and it provides no
numerically acceptable pressure level under the unchanged provisional
controls.

## Artifact evidence

Local preparation and submission records:

- pressure-sensitivity manifest (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_INIT-S_pressure_sensitivity_200step_20260817.json`; not migrated)
- native pressure-sensitivity journal (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_INIT-S_pressure_sensitivity_200step_20260817.jou`; not migrated)
- [pressure-sensitivity preparation/run script](../../../../PyAnsys/scripts/setup/run_fg_mix_t01_stage3_pressure_sensitivity.py)
- INIT-H pressure-sensitivity manifest (historical machine artifact path: `../../../../PyAnsys/output/fg_mix_t01_stage3_INIT-H_pressure_sensitivity_200step_20260817.json`; not migrated)
- [single-pressure native-run script](../../../../PyAnsys/scripts/setup/submit_fg_mix_t01_stage3_pressure_case.py)

Remote start-pair directory:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\
```

All eighteen pressure transcripts exist remotely: nine for `INIT-S` and nine
for `INIT-H`. Their paired transient endpoint and residual exports do not. The
prepared start pairs for all eighteen branch/pressure combinations exist
remotely; no endpoint pair was found for any of them.

## Interpretation status

Interpretation status: pending user direction.

This combined attempt does not justify changing the timestep or selecting a
production outlet pressure. Both initialization branches became unstable
before the pressure grid could be compared. A subsequent stability
intervention must be recorded as a separate numerical-control experiment, with
the pressure and branch held fixed while the changed control is identified
explicitly.
