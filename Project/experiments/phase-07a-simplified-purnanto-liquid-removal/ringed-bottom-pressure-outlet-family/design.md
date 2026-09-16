# E6 — Localized bottom radial-band pressure-outlet family

## Status and authority

- **Candidate:** `E6-RING-PO`
- **Origin:** direct human request on 2026-09-15
- **Lifecycle role:** discovery / numerical mechanism diagnostic
- **Status:** `DESIGN_AUTHORIZED_NOT_RUN`
- **Phase:** Phase 07A simplified Purnanto liquid-removal mechanisms
- **Hard boundary:** this family is not part of the Phase 7.1A absorber-only
  convergence route. It is a separately recorded Phase 07A branch.
- **Claim limit:** a result may initially be described only as a localized
  pressure-boundary phase-routing or drainage diagnostic. It is not evidence
  of a liquid-selective real brine outlet, plant bottom pressure, level
  control, or physical separator performance.

The human request explicitly reopens a localized part of the deferred bottom-
opening idea. It does not reopen arbitrary bottom holes, a lower-geometry
change, or a conventional full-bottom outlet as the preferred brine-pool
representation. The no-outlet absorber remains the working Phase 7.1A route;
E6 is a contrastive “hacky” boundary-topology experiment.

## Scientific question

> Does exposing only a narrow outer radial band of the existing planar bottom
> as a pressure outlet, while retaining the inner bands as walls, change the
> full-bottom pressure outlet’s vapor shortcut and numerical instability while
> still permitting liquid reaching the lower region to leave?

This is deliberately narrower than “does the ring let only liquid escape?”
Fluent’s pressure-outlet boundary is phase-permissive. The outward phase split
is produced by the local solution; backflow phase fractions apply only when the
flow reverses. The first interpretation therefore concerns outlet placement,
pressure response, phase routing, and numerical survivability. A claim of
liquid-selective drainage would require a liquid-filled outlet and a negligible
vapor flux demonstrated by phase-resolved evidence.

## Collision and novelty

| Existing direction | Collision class | What E6 changes |
| --- | --- | --- |
| E1-PO full-bottom pressure outlet | `PARTIAL REPEAT` with a new topology delta | E1 exposes all 432 bottom faces; E6 exposes only selected radial bands and retains the remainder as walls. |
| H1 bottom holes/openings | `REOPENED SUB-DIRECTION` | The human has now explicitly authorized one localized outer-band opening, not arbitrary holes or a new lower geometry. |
| E5-CZ / E5-CZ-ABSORB | `NEW MECHANISM CONTRAST` | E5 removes phase-2 mass volumetrically in a lower cell zone; E6 removes whatever phase the open boundary carries. |
| Phase 05/06 pressure/resistance outlet work | `PARTIAL REPEAT` | Those records constrain interpretation but do not use this supplied mesh and this radial wall/open topology. |

The nonredundant comparison is spatial: hold the pressure value and all
solver/physics settings fixed while comparing the retained-wall outer-ring
topology with the matched E0 wall reference and the existing full-bottom E1
anchor. The family must not be presented as another pressure sweep alone.

## Parent and invariants

Each child must be built from the exact verified E0 initialized parent used by
the fixed-mesh treatment screen, on the supplied mesh:

`Separator-purnanto342k.msh.h5`

Observed local mesh identity:

- SHA-256: `59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801`
- cells: `342,609`
- nodes: `1,077,053` stored mesh nodes in the HDF5 artifact
- faces: `1,647,633`
- original `bottom` boundary faces: `432`
- original `bottom` area: `3.164981439 m²`

The controlled change is the bottom-face partition plus the selected ring’s
boundary type and pressure. Preserve the following unless a setup explicitly
records a required Fluent dependency:

- supplied coordinates and volume mesh;
- cell, face, node, extent, volume-statistic, and mesh-check invariants;
- Mixture/RNG physics and materials from the verified E0 parent;
- inlet definitions and corrected `0.875936 m` steam-outlet hydraulic scale;
- initialization basis, numerics, report definitions, residual monitors, and
  evidence horizon;
- all unselected bottom bands as walls;
- pressure-outlet backflow state set before the requested pressure, with the
  pressure set last and read back before save and after reopen.

The separation operation must be performed on a disposable child or a
preserved copy. It must not overwrite the E0 parent or any durable E1/E5
artifact.

## Existing-bottom radial-band catalogue

The supplied bottom is planar and approximately square-annular rather than a
clean circular disk. A read-only HDF5 survey found an area-weighted radial
centre at approximately `(x,z) = (0.000036, -0.000011) m`, face-centroid
radii from `0.377616` to `1.044660 m`, and no face centroids inside the central
opening. The following are therefore **radial bands / pseudo-rings**, not exact
CAD annuli.

The target intervals below are defined from bottom-face centroid radius
`r = sqrt((x-xc)^2 + (z-zc)^2)`. They are a predeclared selection catalogue,
not a substitute for post-split Fluent readback. Fluent’s mark-based face
separation may classify a boundary face using adjacent-cell marks, so the
actual face count, area, centroid range, adjacency, and displayed topology are
authoritative.

| Band | Target radial interval (m) | Read-only face survey | Read-only area survey (m²) | Initial role |
| --- | ---: | ---: | ---: | --- |
| `R01-inner` | `0.3776 ≤ r < 0.60` | 86 faces | 0.703555 | wall |
| `R02` | `0.60 ≤ r < 0.75` | 86 faces | 0.725761 | wall |
| `R03` | `0.75 ≤ r < 0.90` | 102 faces | 0.799562 | wall |
| `R04` | `0.90 ≤ r < 0.99` | 91 faces | 0.660073 | wall |
| `R05-outer` | `r ≥ 0.99` | 67 faces | 0.276031 | first pressure-outlet candidate |
| **Total** | — | **432 faces** | **3.164981** | — |

The outer candidate is the outermost resolved face row. Its nominal radial
selection width is roughly `0.055 m` from the maximum observed radius, but the
mesh has a centroid-radius gap between approximately `0.990` and `1.041 m`.
Therefore “thin” means the outermost available mesh row, not a continuous
0.055 m geometric annulus. If that row is too coarse or jagged, the next
action is a human-approved CAD/Fluent-Meshing partition and remesh, not an
unrecorded change to the selection threshold.

## First spatial pattern and pressure screen

The first pattern is fixed before execution:

```text
R01-inner wall
R02        wall
R03        wall
R04        wall
R05-outer  pressure-outlet
```

The initial pressure points reuse the human-approved E1 gauge-pressure set so
that pressure response can be compared directly with the full-bottom family:

| Child | Open band | Gauge pressure | Discovery horizon | Status |
| --- | --- | ---: | ---: | --- |
| `P7-E6-RING-OUTER-PO-P1120` | `R05-outer` | `1.120 MPa` | 500 iterations | setup prepared; not run |
| `P7-E6-RING-OUTER-PO-P1160` | `R05-outer` | `1.160 MPa` | 500 iterations | setup prepared; not run |
| `P7-E6-RING-OUTER-PO-P1200` | `R05-outer` | `1.200 MPa` | 500 iterations | setup prepared; not run |

These are boundary gauge pressures, not identified physical bottom pressures.
P1160 and P1200 are not assumed safe because the matched full-bottom cases
already failed their smoke horizons. Each child must pass the same 50-iteration
smoke gate before its 500-iteration result can be compared. A valid member may
continue only after all three initial children are classified and a separate
continuation decision is recorded.

## Mesh-preparation gate

Before any child solve, prepare a reusable ringed mesh/case on a disposable
child. The preferred route is to create named radial subfaces in the geometry
or Fluent Meshing stage. If the existing mesh must be reused, test Fluent’s
documented `Domain → Zones → Separate → Faces... → Mark` workflow with nested
cylindrical/region registers on a disposable copy. That operation redistributes
existing faces; it does not create exact circular edges, new nodes, or a true
annular geometric boundary.

The capability test must prove, before pressure conversion:

1. five real boundary face zones exist for `R01`–`R05`;
2. face counts and areas sum to the original `bottom` zone within the recorded
   mesh-readback tolerance;
3. each band remains planar at the bottom and is adjacent to the expected
   fluid region;
4. the remaining-wall and candidate-ring zones retain the intended names and
   topology after save/reopen;
5. mesh counts, extents, volume statistics, and mesh-check status are
   unchanged if the operation is only face-zone reclassification; and
6. one disposable test ring can be converted to `pressure-outlet`, read back,
   saved, reopened, and read back again while all other bands remain walls.

If Fluent’s mark-based classification cannot produce stable named bands, this
family is blocked at mesh capability. Do not approximate the ring by a cell
source, porous resistance, or a surface used only for postprocessing; those
would be different candidates.

## Evidence contract

Every child must record, per ring and for the steam outlet:

- total mass flow, liquid mass flow, vapor mass flow, and net direction;
- reverse-flow incidence and backflow phase fractions;
- pressure and velocity near the open-ring/wall junctions;
- total and lower-region liquid inventory;
- phase-resolved inlet/outlet balance including inventory change;
- residual histories, continuity/imbalance measures, and solver warnings;
- turbulence or turbulent-viscosity limiting relevant to the localized outlet;
- final paired case/data state when the declared horizon is reached.

Core interpretation tests are:

1. Does the outer ring reduce liquid buildup relative to matched E0?
2. Is any ring removal predominantly liquid, or is it vapor/mixed-phase loss?
3. Does the retained wall create a lower-region accumulation or recirculation
   artifact?
4. Does localization improve numerical survivability relative to E1, or merely
   suppress all discharge?
5. Do the observed responses persist across the declared discovery window?

A smaller total inventory alone is not a success signal. A vapor-dominated
ring repeats the main interpretive weakness of E1. A stable ring with nearly
zero flux may be useful as a negative localization result, but it is not a
successful liquid-removal mechanism.

## Adversarial review and decision

The independent review classified the design as viable for a new discovery
packet with the following important constraints:

- pressure-outlet phase selectivity is an unproven and materially challenged
  assumption;
- the existing 432-face bottom may only support a jagged pseudo-ring;
- local wall-to-outlet junctions are mesh-sensitive;
- downstream pressure, hydraulic resistance, liquid level, and a resolved
  liquid seal are missing physical facts;
- the initial claim must remain a computational phase-routing diagnostic;
- the first run must prove the face-zone capability and phase-resolved flux
  instrumentation before any drainage interpretation.

No blocker remains for design authorization because the human explicitly
requested this contrastive branch. The mesh capability test is a hard
implementation gate, not permission to assume that the desired rings already
exist.

## References

- [Phase 07A context](../CONTEXT.md)
- [Supplied mesh inspection](../mesh-inspection.md)
- [Full-bottom E1 design](../fixed-mesh-treatment-screen/design.md)
- [E1 P1120 results](../fixed-mesh-treatment-screen/e1-po-p1120/results.md)
- [E1 P1160 results](../fixed-mesh-treatment-screen/e1-po-p1160/results.md)
- [E1 P1200 results](../fixed-mesh-treatment-screen/e1-po-p1200/results.md)
- [E5-CZ absorber design](../cell-zone-treatment-family/design.md)
- [Reusable Fluent separator guidance](../../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md)
- [Reusable separator-method synthesis](../../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)
- [Official Fluent zone-separation documentation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridModify.html)
- [Official Fluent region-register documentation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_cell_register.html)
