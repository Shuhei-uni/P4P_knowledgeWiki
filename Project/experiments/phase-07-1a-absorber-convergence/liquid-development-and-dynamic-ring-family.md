# Phase 7.1A — C7/C8 liquid-development and dynamic-ring family plan

## Status and boundary

**Planning only — no packet below authorizes a Fluent mutation or solve.**

This is the active Phase 7.1A direction. It supersedes the unrun turbulence
and solver-path queue as active work, while retaining those records as history.
`C*` in the human request is interpreted here as `C8`, the dynamic thin-outer
ring family.

Both families use the supplied `purnanto-separator(bottomrings)-237k.msh.h5`
mesh. They retain the lower phase-2-only absorber, no direct phase-1 source,
the existing base inlet targets (`116.92 kg/s` liquid and `80.69 kg/s` vapor),
and steady Mixture/RNG settings unless a future setup explicitly changes one.

Every C7 and C8 setup has a `5,000`-active-iteration horizon. Preserve paired
case/data checkpoints after active `1,000`, `2,000`, `3,000`, `4,000`, and
`5,000`; if a run fails earlier, preserve the last valid paired state and the
failure evidence. Checkpoints are evidence anchors, not convergence claims.

## Baseline inheritance and server assignment

The [Phase 7.1A baseline setup record](baseline-setup-record.md) is the
authoritative settings fingerprint. For both families, first load a known
baseline-equivalent parent, replace only the mesh with the supplied 237k mesh,
then read back and preserve every baseline setting that still has a direct
meaning on that mesh. Do not copy an old prepared boundary case as a proxy for
the baseline.

| Family | Assigned runtime | Build order | Permitted departures from the baseline fingerprint |
| --- | --- | --- | --- |
| C7 | `student` endpoint | baseline-equivalent parent → import 237k mesh → recreate lower absorber region and all-wall bottom topology → apply inlet-ramp law | mesh/topology identifiers; lower-region zone volume and its source density; both inlet commands during the ramp |
| C8 | Server 3 | transfer and reopen the exact selected all-wall C7 paired checkpoint from Server 1 → verify its identity/readback on Server 3 → apply delayed ring change | dynamic thin-outer-ring wall-to-pressure-outlet change after its trigger |

The selected C7 checkpoint must be copied to Server 3 as a paired case/data
artifact with an identity/hash check before mutation. A Server 3 rebuild from
the mesh alone is not an equivalent C8 parent, because it would lose the C7
developed field history.

The prior `thin-outer-po-p1120` prepared pair was built on Server 1 with the
thin outer ring already open. It is evidence of a prior save/reopen audit, but
is **not** the C7 parent and must not be used as the C8 Server 3 parent.

The mesh replacement necessarily changes zone IDs/names, face topology, and
the lower-zone geometric volume. Recreate the lower `y <= 0.10 m` absorber
region from the 237k mesh and recalculate only its *volumetric* phase-2 source
density so that the integrated command remains `-116.92 kg/s`. This is a mesh
unit conversion, not source retuning. Every other applicable model, material,
solver, numerical, boundary, source, DPM, residual, and report setting must
match the baseline readback exactly unless C7/C8 explicitly declares it.

Each server build needs a durable before/after readback that identifies:

1. the exact baseline-equivalent parent;
2. the 237k mesh identity, mesh check, and five bottom-band mapping;
3. unchanged baseline settings and any unavailable mesh-specific fields;
4. the recreated lower-zone volume, source density, and verified integrated
   phase-2 command; and
5. the family-specific changes only.

## Common comparison architecture

```text
Initialized 237k all-wall baseline
        |
        +-- C7: both inlet targets ramp together to base flow
        |       thin outer ring remains wall throughout
        |       choose a reproducible lower-liquid development state
        |
        +-- C8: restart an accepted C7 development state
                keep ring wall until a declared liquid condition
                switch only thin outer ring to pressure outlet
                screen pressure, then activation timing
```

Ramping both inlets by the same fraction preserves their base liquid-to-vapor
mass-flow ratio. It tests field-development history rather than a different
operating mixture ratio.

## C7 — two-phase inlet-development family

### Question

Can a gradual, ratio-preserving increase of both inlet flows establish a more
useful and durable lower-region liquid field than beginning at the full base
flow on the same all-wall 237k mesh?

### Fixed conditions

- all five bottom bands remain stationary no-slip walls for the whole run;
- lower absorber remains phase-2-only with zero direct vapor source.  During
  each reduced-flow C7 ramp its integrated liquid sink uses the same
  multiplier as both inlets, `sink = -116.92 f kg/s`; it therefore never
  exceeds the simultaneous liquid inlet command and reaches `-116.92 kg/s`
  only at base flow;
- both inlet targets use the same instantaneous multiplier `f(active)`:
  `liquid = 116.92 f kg/s`, `vapor = 80.69 f kg/s`;
- after the ramp, both return to their unchanged base targets and are held;
- no patch/reset, further mesh change, pressure-ring opening, source retuning,
  or transient/time-accurate branch.

### Proposed staged screen

First create an all-wall 237k base-flow reference (`C7-R0`). It separates the
mesh/topology effect from the inlet-history effect. Then use the same linear
ramp length and base-flow hold for three initial multipliers:

| Packet | Initial multiplier | Ramp | Interpretation purpose |
| --- | ---: | --- | --- |
| C7-R0 | `1.00` | none; base flow from start | all-wall 237k reference |
| C7-R25 | `0.25` | linear to `1.00` | strong gentle-start contrast |
| C7-R50 | `0.50` | linear to `1.00` | intermediate contrast |
| C7-R75 | `0.75` | linear to `1.00` | mild gentle-start contrast |

All three ramped cases use a deliberately slow, common **2,000-active-
iteration linear ramp** followed by a **3,000-active-iteration base-flow
hold**. This reaches the phase's existing 4,000-iteration maturity marker
without mistaking it for a convergence criterion, and retains a full 3,000
iterations at the unchanged base condition for comparison. `C7-R0` also runs
for the full 5,000 iterations at its base flow from the start.

### C7 evidence and selection gate

For every case record commanded and realized inlet fluxes, lower/adjacent/total
liquid inventory, lower-zone phase-2 volume fraction, absorber command and
realized removal, residuals, continuity/imbalance, steam-outlet routing, and
limiter/reverse-flow warnings through both ramp and hold.

Select a C7 parent for C8 only if it has a documented lower-liquid development
interval at base flow and preserves interpretable balances. The selected state
need not be converged or physically validated. A case that merely accumulates
liquid globally without increasing lower-region inventory is not a successful
C7 development state.

## C8 — dynamic thin-outer-ring family

### Question

Starting from a selected C7 state, can delayed conversion of only the thin
outer bottom ring from wall to pressure outlet increase liquid routing through
that ring without predominantly venting vapor or making the phase/source
balance uninterpretable?

### Fixed conditions

- same 237k mesh and C7 parent; all inner/thick bottom bands remain walls;
- ring remains a wall until its declared trigger; only the named thin outer
  band may change to pressure outlet;
- inlet flows remain at base targets after the C7 ramp; absorber schedule is
  frozen and recorded before the switch;
- the ring remains phase-permissive: a zero liquid backflow fraction is a
  backflow condition, not liquid-only outward routing.

### Stage 1 — establish a pressure response at one mature trigger

Use a single, predeclared *established-liquid* trigger from the selected C7
history. It should require both a lower-zone liquid measure above a chosen
threshold and persistence for a declared observation window, rather than a
bare iteration count. The actual threshold must be chosen from C7 evidence
before a setup is made.

At that one trigger, screen the pressure ladder sequentially rather than as a
full activation-by-pressure matrix. Each C8 child receives 5,000 active
iterations from its prepared C7 restart and the same 1,000-iteration paired
checkpoint cadence:

| Packet | Ring gauge pressure | Purpose |
| --- | ---: | --- |
| C8-P0 | `1.120 MPa` | equal to steam-outlet gauge pressure; opening-only reference |
| C8-P10 | `1.110 MPa` | mild additional pressure drive |
| C8-P30 | `1.090 MPa` | moderate additional pressure drive |
| C8-P60 | `1.060 MPa` | strong artificial drive / stop-boundary probe |

Run in this order and stop the ladder if a case produces sustained
vapor-dominated ring outflow, unacceptable imbalance, destructive reverse
flow, or solver failure. These values are a deliberately coarse numerical
screen around the current `1.120 MPa` outlet reference; they are not a model
of plant drainage hardware.

### Stage 2 — activation timing only after a useful pressure is found

Choose the least aggressive Stage-1 pressure that shows a favorable liquid-to-
vapor ring-routing signal and acceptable accounting. Then compare activation
rules at that fixed pressure:

| Packet | Trigger family | Purpose |
| --- | --- | --- |
| C8-AE | early/onset lower-liquid threshold | tests whether earlier opening captures emerging liquid or vents vapor |
| C8-AM | established-liquid threshold | Stage-1 reference |
| C8-AL | delayed/persistent lower-liquid threshold | tests whether waiting for a stronger developed field improves selectivity |

The thresholds must be based on the same lower-zone metric and persistence
window. Do not test all pressure and activation combinations unless Stage 1 and
2 identify a clear reason: that matrix would obscure the main routing result.

### C8 evidence and decision gate

Record the ring wall/open state, exact switch iteration, ring gauge pressure,
ring mixture/vapor/liquid mass fluxes, phase fractions and reverse flow,
steam-outlet fluxes, lower/adjacent/total liquid inventories, absorber command
and realized removal, residuals, imbalance, and warnings.

Classify each case as one of:

- **useful artificial routing:** liquid ring flux increases relative to vapor
  loss and balances remain interpretable;
- **vapor venting:** ring flow is predominantly vapor or worsens outlet/routing
  behavior;
- **no routing response:** opening changes little in lower liquid or ring flux;
- **numerically unusable:** instability, non-finite field, or unacceptable
  imbalance prevents interpretation.

No outcome validates physical separator drainage. A useful result only selects
the next numerical routing condition for this model.
