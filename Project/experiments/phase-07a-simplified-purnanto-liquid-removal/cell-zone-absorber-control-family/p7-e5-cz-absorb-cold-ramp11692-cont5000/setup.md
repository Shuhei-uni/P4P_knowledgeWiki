# P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000 setup

## Status and authority

| Field | Contract |
| --- | --- |
| Status | `EXECUTED_BLOCKED` — valid through active 1,960; solver divergence in the block ending at 1,970 |
| Phase | Phase 07 simplified Purnanto liquid-removal mechanisms |
| Lifecycle | discovery extension / continuation |
| Candidate | `E5-CZ-ABSORB-COLD-CONT5000` |
| Setup ID | `P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000` |
| Origin | Explicit human request in this chat on 2026-09-11 |
| Authority | Human-approved continuation of the verified active-1000 child |
| Parent | `P7-E5-CZ-ABSORB-COLD-RAMP11692` active-1000 case/data pair |
| Gate | G3 cold-start absorber time-horizon extension |

## Question

Does the exact cold-start absorber case remain numerically executable and show
any materially different inventory or phase-routing behaviour when the same
state is continued from active 1,000 to total active 5,000 iterations?

This continuation is intended to resolve the time-horizon uncertainty in the
first 1,000-iteration discovery screen. It does not change the underlying
scientific question: liquid may disappear only through the lower cell-zone
phase-2 absorber, representing the externally controlled brine-pool surface.
The bottom remains a wall; no conventional outlet is introduced.

## Exact parent and controlled delta

Load the durable final pair from the completed cold-start run:

```text
Case: C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.cas.h5
Data: C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.dat.h5
```

The parent must be read back before iteration. Prove that it retains the two
fluid zones, the `p7-e5-lower-y010` lower zone, the source tree, the bottom wall,
and the same mixture, material, boundary, turbulence, gravity, energy, species,
and DPM-isolation settings. The parent source tree must show the lower-zone
phase-2 mass source and matched mixture momentum source active, with parent-zone
sources and direct phase-1 mass source off.

The only controlled delta is time: perform 4,000 additional iterations, taking
the existing case from total active iteration 1,000 to total active iteration
5,000. Do not ramp, retune, or add feedback to the absorber. Hold the existing
integrated phase-2 removal command at `116.92 kg/s` and retain the source
normalization and lower-zone phase-2 velocity basis already proven in the
parent.

## Frozen invariants

- no outlet or bottom-boundary change;
- no patch/reset, second initialization, remesh, resplit, porous model, UDF, or
  source-region substitution;
- same lower zone `p7-e5-lower-y010`, with the same 3,794-cell split topology;
- same phase-2-only mass sink and matched mixture x/y/z momentum source;
- same source sign, units, integrated command, materials, models, boundaries,
  numerical methods, and relaxation settings;
- direct phase-1 mass source remains off and parent-zone sources remain off; and
- the original active-1000 evidence package remains immutable and is not
  overwritten by continuation files.

## Run intent and evidence

- Mode: attached Fluent discovery continuation.
- Parent active iteration: 1,000.
- Additional iterations: 4,000.
- Total target: active 5,000.
- Smoke: first 50 continuation iterations, corresponding to total active 1,050.
- Checkpoints: total active 1,050, 1,100, 1,250, 1,500, 2,000, 3,000,
  4,000, and 5,000, with paired case/data files.
- Source audit: verify the integrated phase-2 source at each 10-iteration
  update; it must remain `−116.92 kg/s` within numerical precision.
- Histories: create new continuation report files so the parent histories are
  not overwritten. Preserve the native solver coordinate as reported by
  Fluent, and merge parent points 1–1,000 with continuation points for analysis
  only when the coordinate is unambiguous.
- Required histories: the same 18 histories and residual curves as the parent.
  The missing vapor-inventory history from the parent remains a declared
  limitation; this continuation does not silently repair it.
- Warnings: retain reversed-flow, turbulent-viscosity, clipping, divergence,
  and floating-point diagnostics.
- Finalization: save the total-active-5000 pair, reopen it, and read back the
  topology, source tree, invariants, and final runtime state.

The 5,000-iteration total horizon remains an extended discovery result. It is
not a fully converged or physically qualified separator prediction, and a
completed horizon must not be interpreted as evidence of a steady branch.

## Decision gate

Compare active 1,000–5,000 with the existing active 700–1,000 late window.
Record whether total liquid inventory remains positively drifting, whether any
phase-2 liquid reaches the lower zone, whether the absorber source remains
realized, and whether numerical warnings or residuals worsen into a solver
failure. Do not promote this continuation to qualification automatically.
