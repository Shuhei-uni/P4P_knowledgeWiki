> **Retired source:** Setups/full-geometry/mixture/transient-liquid-outlet/stage-03-initialization-comparison.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# FG-MIX-T01 Stage 3 — No-patch transient control and timestep decision

## Intent

| Field | Value |
|---|---|
| Stage ID | `FG-MIX-T01-S3` |
| Investigation mode | diagnostic / numerical sensitivity |
| Primary question | Can the current transient Mixture formulation run from the developed steady parent when the Y010 patch is removed, and if not, does reducing only the timestep materially delay or remove the failure? |
| Interpretation owner | user-led |
| Parent | [Stages 1–2 — Steady Parent and Transient Start States](../stages-01-02-setup.md) |
| Recovery basis | [Stage-3 failed initialization sweep report](results-initialization-comparison.md) |
| Brine/steam comparison pressure | `1.120 MPa` gauge for both pressure outlets |

## Why this stage exists

The previous Stage-3 sweep did not produce a usable initialization comparison:
the Y010-patched `INIT-H` branch failed with a floating-point exception at
transient step `53`, after residual growth, full-domain turbulent-viscosity
limiting, reversed flow at both pressure outlets, and AMG divergence. The
`INIT-S` branch was not started, so no initialization ranking can be inferred
from that attempt. See the [failed-run report](results-initialization-comparison.md)
for the retained transcript and audit artifacts.

The next experiment is deliberately narrower. Use the developed steady parent
and remove only the Y010 liquid patch from the transient startup. Keep the
current transient formulation, turbulence model, spatial discretization, PISO
settings, mesh, inlets, and `20`-iteration timestep budget unchanged. Set both
the steam and brine pressure outlets to the common `1.120 MPa` gauge condition.

This is no longer an immediate `INIT-S` versus `INIT-H` comparison. It is a
no-patch control followed, only if needed, by one-variable timestep sensitivity.
There is no initial liquid pool in these controls, so do not spend the first
diagnostic pass on a Y010/Y030 inventory comparison.

## Current failed-sweep record

The failed sweep remains part of the evidence trail and must not be rewritten
as a completed comparison:

| Item | Reported state |
|---|---|
| Starting branch | `INIT-H` entered the solve; `INIT-S` did not start |
| Brine outlet in failed sweep | Pressure Outlet, `1.200 MPa` gauge |
| Y010 patch | applied once before the failed transient run |
| Timestep | `2.5e-4 s` |
| Failure point | transient step `53`, physical time `0.01325 s` |
| Failure signature | severe residual growth, all-cell turbulent-viscosity limiting, reverse flow at both outlets, AMG divergence, floating-point exception |
| Comparison result | none; no paired Stage-3 endpoint exists |

The recovery controls below use the baseline `1.120 MPa` gauge pressure at both
pressure outlets as specified for the next test. Do not resume from the failed
partial state and do not use the failed branch as a new parent.

## Sequential case matrix

Run these cases sequentially. Start with `NP-DT1` only. Prepare or run the next
case only when the decision rule below authorizes it. Each timestep trial must
be loaded independently from the same steady parent; do not seed a finer trial
from a coarser-trial endpoint.

| Test | Initial field | Y010 patch | Brine pressure | Timestep | Purpose |
|---|---|---|---:|---:|---|
| `NP-DT1` | steady parent | none | `1.120 MPa` gauge | `2.5e-4 s` | exact current-method control without the patch |
| `NP-DT2` | steady parent | none | `1.120 MPa` gauge | `1.25e-4 s` | run only if `NP-DT1` fails or shows useful improvement is needed |
| `NP-DT3` | steady parent | none | `1.120 MPa` gauge | `6.25e-5 s` | run only if `NP-DT1`/`NP-DT2` still fail or the finer bracket is scientifically useful |

The nominal initial horizon is `0.05 s`: `200` timesteps for `NP-DT1`, `400`
for `NP-DT2`, and `800` for `NP-DT3` if activated. A run that remains clean
through this window is sufficient to establish the immediate diagnostic result;
do not automatically extend every case to `0.10 s` or execute the complete
three-case matrix.

## Frozen controls

Keep the failed Stage-3 transient formulation unchanged wherever it is not
the explicit timestep variable in the table above:

- pressure-based transient solver;
- bounded second-order transient discretization;
- current PISO settings, including the existing neighbor-correction choice;
- implicit Mixture volume-fraction formulation;
- current turbulence model and spatial discretization;
- `20` maximum iterations per timestep;
- same `Full-geomV2-231kcells.msh.h5` mesh;
- same velocity inlets and inlet phase conditions;
- steam Pressure Outlet at `1.120 MPa` gauge;
- brine Pressure Outlet at `1.120 MPa` gauge;
- DPM and EWF disabled;
- no Hybrid Initialization after loading the steady data;
- no Y010 patch or any other patch.

Do not change first-order/second-order treatment, PISO controls, relaxation
factors, iteration limits, turbulence, mesh, outlet family, or inlet settings
as part of `NP-DT1`. If `NP-DT2` or `NP-DT3` is authorized, change only the
timestep from the preceding control and retain every other setting.

## Required startup sequence

For each authorized test:

```text
load steady parent case+data
→ switch to transient
→ retain/set P_brine = 1.120 MPa gauge
→ verify P_steam = 1.120 MPa gauge
→ verify current transient formulation and test timestep
→ do not initialize
→ do not patch
→ set/confirm flow time = 0 s
→ save the no-patch start state if required by the execution workflow
→ run the authorized physical-time window
```

The no-patch start state must remain traceable to the exact steady-parent
case/data pair. If any unintended initialization, patch, boundary change, or
numerical-control change occurs, stop and record the case as setup-invalid
rather than comparing it with the control.

## Required evidence

The primary evidence package for each run is:

- native residual histories;
- iterations required within each timestep, including repeated reaches of the
  `20`-iteration cap;
- liquid and vapour mass fluxes at the brine outlet;
- liquid and vapour mass fluxes at the steam outlet;
- brine-pipe-entry pressure;
- reverse-flow events at either pressure outlet;
- turbulent-viscosity-limit warnings and affected-cell counts when reported;
- AMG divergence, floating-point, and other numerical warning events;
- exact transient step and physical time at which residual growth or
  divergence begins;
- final solver state and paired case/data path, or the last valid checkpoint
  when the run fails.

Y010/Y030 inventory histories are not required as primary decision outputs for
these no-patch tests because no initial pool is imposed. They may be retained
if already present in the monitor package, but their absence must not trigger
additional inventory-analysis work before the no-patch control is decided.

Compare runs at equal physical time, not equal iteration count. For a failed
run, retain the last valid evidence and record the failure time rather than
describing the case as converged or complete.

## Decision tree

```text
No patch, dt = 2.5e-4 s  (`NP-DT1`)
        │
        ├── survives a clean 0.05 s window
        │      ↓
        │   transient conversion itself is viable at the existing timestep
        │      ↓
        │   next experiment: restore Y010 and use dt = 1.25e-4 s
        │   to investigate patch/timestep interaction
        │
        └── fails or shows a clearly useful marginal improvement
               ↓
         No patch, dt = 1.25e-4 s  (`NP-DT2`)
               │
               ├── improves substantially or survives
               │      ↓
               │   temporal resolution is implicated; record the comparison
               │
               └── still fails similarly
                       ↓
                 No patch, dt = 6.25e-5 s  (`NP-DT3`)
```

Use “survives” to mean that the run reaches the planned `0.05 s` window
without the failure signature described above and without an unresolved
runaway in residuals or physical monitors. This is a diagnostic gate, not a
formal convergence or validation criterion.

## Interpretation and follow-on

Interpretation remains user-led. The immediate conclusions permitted by this
stage are limited to:

1. whether transient conversion from the steady parent is viable without the
   Y010 patch at `2.5e-4 s`;
2. whether halving the timestep materially changes the no-patch failure
   timing or stability; and
3. whether a further halving is justified by the observed evidence.

If `NP-DT1` survives, do not launch `NP-DT2`/`NP-DT3` automatically. The next
useful experiment is the Y010 patch restored with `dt = 1.25e-4 s`, while
holding the two `1.120 MPa` outlet pressures and every other control fixed.

If the no-patch controls fail, use the recorded residual, warning, flux,
pressure, reverse-flow, viscosity-limit, and exact-failure-time evidence to
decide whether timestep resolution is the dominant issue. Do not change
first-order schemes, PISO controls, relaxation factors, or other numerical
variables in this stage.

## Handoff

Do not automatically proceed to the six-case outlet screen. After the
authorized no-patch result is recorded, update the common transient-parent
decision and authorize the next patch/timestep experiment or a revised Stage 4
qualification plan. Any final common `t = 0` parent must still be created from
the exact accepted steady parent, with its initialization, patch state, outlet
pressures, timestep, and paired case/data artifacts explicitly recorded.
