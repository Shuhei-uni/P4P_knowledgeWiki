# Stage-2 Startup-State Construction — FG-MIX-T01

## Status

The two Stage-2 case/data pairs were created and independently reloaded on
Fluent 2025 R2. They are case-construction artifacts only: no transient
timestep, steady iteration, or transient solve was run.

The source for both branches was the user-selected Stage-1 candidate
`FG-MIX-T01-S1-C1375` at `1.1375 MPa` brine-outlet pressure. The exact mesh was
preserved throughout:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\Full-geomV2-231kcells.msh.h5
```

Fluent readback on the saved artifacts confirmed `231,376` mixed cells and
`697,078` nodes. No remeshing, adaptation, scaling, or mesh substitution was
performed.

## Case matrix

| Branch | Pre-patch flow field | Brine outlet | Initialization sequence | Status |
|---|---|---:|---|---|
| `FG-MIX-T01-S2-INIT-S` | Developed C1375 case/data field | Pressure Outlet, `1.200 MPa` gauge | load C1375 → transient controls → T-PO-1 → create Y010 → patch liquid VF once | paired endpoint reloaded |
| `FG-MIX-T01-S2-INIT-H` | Fluent Hybrid Initialization field | Pressure Outlet, `1.200 MPa` gauge | load C1375 case/data → transient controls → T-PO-1 → Hybrid Initialize → create Y010 → patch liquid VF once | paired endpoint reloaded |

The remote paired artifacts are:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S2-INIT-S-TPO1-p1200kpa-y010-start-20260816T112833Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S2-INIT-S-TPO1-p1200kpa-y010-start-20260816T112833Z.dat.h5

C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S2-INIT-H-TPO1-p1200kpa-y010-start-20260816T112833Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S2-INIT-H-TPO1-p1200kpa-y010-start-20260816T112833Z.dat.h5
```

## Common transient setup readback

Both branches read back the same provisional Stage-3 method:

- pressure-based transient solver using Fluent’s `unsteady-2nd-order-bounded` setting;
- PISO pressure–velocity coupling with neighbor correction enabled and one neighbor-correction iteration;
- inherited verified spatial schemes, including PRESTO! pressure, second-order-upwind momentum/turbulence, and QUICK Mixture volume-fraction discretization;
- fixed timestep `2.5e-4 s`;
- maximum `20` iterations per timestep;
- initial flow time `0 s` and zero completed transient timesteps;
- DPM interaction off and EWF off;
- same split velocity inlets, steam outlet, materials, Mixture/RNG `k-epsilon` model, gravity, and operating pressure as C1375.

The Mixture model readback exposes the implicit volume-fraction treatment under
the active multiphase model; no separate VOF formulation control was activated.

## Y010 readback

The identical register definition was created on both branches:

```text
x = [-2.067034, 1.066098] m
y = [-1.484584, 0.100000] m
z = [-1.469893, 2.000000] m
inside = True
selected cells = 33,315
```

The applied patch was phase-2 water-liquid volume fraction `1.0`, once at flow
time `0 s`. The resulting readbacks were:

| Branch | Geometric Y010 volume | Post-patch liquid volume | Post-patch liquid mass |
|---|---:|---:|---:|
| `INIT-S` | `4.829410214 m³` | `4.793078931 m³` | `4,226.393209 kg` |
| `INIT-H` | `4.829410214 m³` | `4.790652590 m³` | `4,224.253734 kg` |

The `INIT-S` and `INIT-H` values differ by `0.002426341 m³`, or approximately
`0.05065%` relative to `INIT-H`. The user accepted this small physical
difference for the initialization comparison. It remains a documented scope
limitation rather than an assertion that the branches are exactly equivalent;
the same register and one-patch command were used, but the two pre-patch
initialization histories are not identical.

## Monitor package and API limitation

Each case contains `19` Stage-2 report definitions under the
`fg_mix_t01_s2` prefix, covering mixture/phase-separated inlet and outlet fluxes,
Y010/Y030 inventories, and total continuous-liquid volume.

During creation, Fluent 2025 R2 reported several optional report-definition
fields as read-only through the Settings API. In particular, the file-output
and instantaneous-history toggles for the geometric/Y010/Y030 volume-integral
definitions did not accept writes, although the definitions themselves were
saved. This is a tooling/readback limitation, not evidence that histories were
collected. Inspect or repair those definitions before Stage 3 runs.

## Artifact manifest

- [Stage-2 build manifest](../../../../../PyAnsys/output/fg_mix_t01_stage2_start_states_20260816.json)
- [Stage-2 builder](../../../../../PyAnsys/scripts/setup/build_fg_mix_t01_stage2_start_states.py)
- [Stage-1 candidate report](stage-01-candidate-screen-20260816.md)
- [Stage-1/2 setup definition](../../../../full-geometry/mixture/transient-liquid-outlet/stage-01-02-steady-parent-and-transient-start.md)

## Handoff

The cases are ready as construction artifacts. The user accepted the Y010
post-patch difference as physically meaningful, and fresh monitor-ready copies
were subsequently prepared with a direct full-domain phase-2 liquid-mass
report. The first Stage-3 comparison queue was canceled before either branch
wrote an endpoint; no replacement comparison run has been submitted.

The user subsequently accepted the small physical INIT-S/INIT-H difference. A
direct full-domain phase-2 liquid-mass report was then added to fresh
monitor-ready copies of both saved pairs without reinitializing, repatching, or
advancing either solution. See the [Stage-3 cancellation and mass-monitor
record](stage-03-initialization-comparison-20260816.md).
