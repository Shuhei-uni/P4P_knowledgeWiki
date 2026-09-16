# E6 mesh catalogue capability setup

## Status and authority

- **Setup ID:** `P7-E6-RING-MESH-CATALOGUE`
- **Candidate:** `E6-RING-PO`
- **Role:** disposable mesh/case capability test; no scientific solve
- **Status:** `NOT_PLACED`
- **Authority:** direct human request on 2026-09-15, recorded in the E6 design
- **Parent:** exact Phase 07A E0 parent and supplied `Separator-purnanto342k.msh.h5`

## Objective

Determine whether the existing planar `bottom` wall can be split into five
stable, named radial-band face zones that survive save/reopen. The test must
prove the reusable ring catalogue before any pressure outlet or iteration is
introduced.

## Target catalogue

Use the area-weighted bottom centre `(x,z) ≈ (0.000036,-0.000011) m` and the
face-centroid radial target intervals:

| Name | Target interval | Source-survey faces | Source-survey area |
| --- | ---: | ---: | ---: |
| `p7-bottom-ring-r01-inner` | `0.3776 ≤ r < 0.60 m` | 86 | `0.703555 m²` |
| `p7-bottom-ring-r02` | `0.60 ≤ r < 0.75 m` | 86 | `0.725761 m²` |
| `p7-bottom-ring-r03` | `0.75 ≤ r < 0.90 m` | 102 | `0.799562 m²` |
| `p7-bottom-ring-r04` | `0.90 ≤ r < 0.99 m` | 91 | `0.660073 m²` |
| `p7-bottom-ring-r05-outer` | `r ≥ 0.99 m` | 67 | `0.276031 m²` |

These are classification targets, not exact geometry. The actual Fluent zone
readback is authoritative because a mark-based split can use adjacent-cell
ownership and the source bottom is a coarse square-annular mesh.

## Preferred implementation order

1. Load the exact parent/mesh into a disposable child and inspect the original
   `bottom` wall, face count, area, adjacency, and hanging-node status.
2. Prefer real named subfaces from CAD/Fluent Meshing if available without
   changing the supplied volume mesh. If not, test the documented Fluent
   `Domain → Zones → Separate → Faces... → Mark` workflow with nested region
   registers.
3. Split only the disposable `bottom` face zone. Do not convert a boundary
   type yet.
4. Rename and read back the five radial bands; inspect the displayed faces and
   their plane/adjacency.
5. Verify the bands’ counts and areas sum to the original `bottom` totals and
   verify global mesh invariants.
6. Save a new case/data pair, reopen it, and repeat the readback.
7. On a second disposable copy only, convert `p7-bottom-ring-r05-outer` to
   `pressure-outlet`, leave R01–R04 as walls, set a test pressure, and verify
   type/backflow/pressure readback before and after reopen.

## Hard pass criteria

- five real boundary zones exist after the split;
- all five are on the intended planar bottom and adjacent to the fluid;
- zone counts and areas sum to the original bottom within recorded tolerance;
- cell/face/node counts, extents, volume statistics, and mesh-check status are
  unchanged by face-zone reclassification;
- the ring names and zone types survive save/reopen;
- selected R05 alone can be converted to pressure outlet in the disposable
  test, with all other bands remaining walls;
- no durable E0/E1/E5 parent is overwritten.

## Blockers

Block the E6 family if Fluent cannot make stable named face zones, if mark
selection produces an unacceptable or non-reproducible topology, if hanging
nodes prevent separation, or if save/reopen changes the ring assignment. A
postprocessing surface, porous resistance, cell source, or guessed TUI prompt
is not an acceptable substitute for a proven boundary face-zone split.
