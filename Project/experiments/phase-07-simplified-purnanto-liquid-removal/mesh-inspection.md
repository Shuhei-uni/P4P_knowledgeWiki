# Phase 07 — Supplied Mesh Structural Inspection

## Status

**Observed, local read-only HDF5 inspection completed on 2026-09-08.** The
supplied Fluent mesh was inspected without loading or modifying a Fluent
session. The inspection establishes artifact identity, stored mesh counts,
zone topology, coordinate bounds, boundary areas, and connectivity checks. It
does not establish solver-side mesh quality or flow-behaviour parity with setup
`08b`.

## Artifact identity

| Item | Observed value |
| --- | --- |
| File | `Separator-purnanto342k.msh.h5` |
| Local OneDrive path | `/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Separator-purnanto342k.msh.h5` |
| Size | `40,685,983 bytes` |
| Modified | `2026-09-08T11:26:11+12:00` |
| SHA-256 | `59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801` |
| Stored origin | `ANSYS FLUENT MESHING 2025 R2` |
| Stored version | `25.2` |
| Units | `m` |

The generated machine-readable inspection is
[`PyAnsys/output/phase07_mesh_inspection/Separator-purnanto342k-inspection-20260908.json`](../../../PyAnsys/output/phase07_mesh_inspection/Separator-purnanto342k-inspection-20260908.json).
The reusable read-only extractor is
[`PyAnsys/scripts/inspection/inspect_fluent_mesh_h5.py`](../../../PyAnsys/scripts/inspection/inspect_fluent_mesh_h5.py).

## Stored mesh structure

| Quantity | Observed value |
| --- | ---: |
| Dimensions | `3` |
| Cells | `342,609` |
| Nodes | `1,077,053` |
| Faces | `1,647,633` |
| Boundary faces | `30,892` |
| Interior faces | `1,616,741` |
| Cell zones | `1` — `separator-purnanto` |
| Type-4 cells | `87,978` (`25.68%`) |
| Type-7 cells | `254,631` (`74.32%`) |

The Fluent cell-type codes and stored meshing state identify type 4 as
hexahedral and type 7 as polyhedral, consistent with a poly-hexcore mesh.

Global coordinate bounds are:

| Axis | Minimum [m] | Maximum [m] | Span [m] |
| --- | ---: | ---: | ---: |
| `x` | `-2.067034` | `1.066950` | `3.133984` |
| `y` | approximately `0` | `6.993944` | `6.993944` |
| `z` | `-1.469893` | `1.066889` | `2.536782` |

## Boundary zones

| Zone | Stored type | Faces | Area [m²] | Main geometric observation |
| --- | --- | ---: | ---: | --- |
| `separator-purnanto:1` | wall | `1,563` | `12.925623` | spans `y≈0–5.761 m`; approximately `0.719 m` across in `x/z` |
| `bottom` | wall | `432` | `3.164981` | planar at `y≈0`; spans about `2.1305 m × 2.1310 m` in `x/z` |
| `wall` | wall | `11,479` | `54.198880` | main external/internal wall collection |
| `liquidinlet` | velocity inlet | `998` | `0.004889925` | planar at `x=-2.067034 m`; `0.724 m` high and `0.006754 m` wide |
| `steaminlet` | velocity inlet | `1,017` | `0.519286085` | planar at `x=-2.067034 m`; `0.724 m` high and `0.717246 m` wide |
| `steamoutlet` | pressure outlet | `15,403` | `0.602608` | near `y=6.261 m`; spans about `0.876 m` in `x/z` |

Every external-zone face has one non-zero adjacent cell and one zero exterior
neighbour in the stored connectivity. The vector sum of all oriented external
face areas closes to approximately `1.9×10⁻¹⁶` of total boundary area, which is
a strong structural consistency check on the extracted face connectivity.

## Comparison with the recorded 08b/Purnanto definition

### Inlet geometry

**Observed agreement.** The new inlet split closely reproduces the recorded
setup-07/08b design:

| Quantity | Recorded target [m²] | New mesh [m²] | Relative difference |
| --- | ---: | ---: | ---: |
| Liquid inlet | `0.0048896` | `0.004889925` | `+0.00665%` |
| Steam inlet | `0.5192864` | `0.519286085` | `-0.000061%` |
| Combined inlet | `0.5241760` | `0.524176010` | approximately zero |

The narrow liquid strip is therefore consistent with the documented 08b/07
equal-velocity, density-weighted area split; it is not evidence of an
accidental missing inlet surface.

### Mesh resolution and topology

**Observed difference against reported metadata.** The setup-08b record gives
`7,601,261` cells and `1,309,312` nodes for its inherited mesh. The supplied
mesh has `342,609` cells and `1,077,053` nodes. This is approximately `22.2×`
fewer cells and `17.7%` fewer nodes, with a stored poly-hexcore cell mixture.
The different element topology means cell count alone is not a resolution
metric, but the new mesh is not the same discrete mesh as recorded for 08b.

### Bottom cutoff

**Human-reported intent, structurally supported.** The new `bottom` zone is a
distinct planar wall at `y≈0`. Its area is `3.164981 m²`. This establishes a
clean zone that can later receive an approved outlet treatment without a CAD
change. The local structural inspection cannot prove that `y=0` corresponds
to the physical plant pool elevation; that mapping remains human-reported.

### Corrected steam-outlet diameter

**Observed and human-confirmed.** The new mesh's `steamoutlet` area is
`0.602608 m²`, giving an area-equivalent circular diameter of `0.875936 m`
(`≈0.876 m`). The human confirmed on 2026-09-08 that this outlet geometry is
intended and that the former Project value of `0.724 m` was incorrect. The
active Purnanto geometry record has therefore been corrected to `0.876 m`.

The separate `0.724 m` dimension remains the square-inlet side length. It must
not be reused as the steam-outlet turbulence/backflow hydraulic diameter for
the Phase-07 setup. Historical cases that actually stored `0.724 m` retain
that value as executed evidence, but E0 must apply and verify the corrected
outlet scale.

## Live Fluent fleet observation

**Observed on 2026-09-08.** Servers 1 and 3 were reachable through gRPC and
quiescent over a three-second activity window in Fluent 2025 R2. Both retained
Phase-06 full-geometry states: server 1 held a Mixture/RNG case and server 3 an
Eulerian/RNG case. Servers 2, 4, and the student endpoint did not answer the
bounded TCP probe. No live session was overwritten and no solver command was
issued.

## What “behave identically to 08b” can mean

**Human expectation.** The supplied geometry should reproduce the relevant
setup-08b behaviour after applying the intentional bottom cutoff and the
corrected steam-outlet scale.

**Current evidence limit.** Structural inspection supports inlet-area parity,
but the bottom cutoff, different discrete mesh, and corrected outlet
turbulence/backflow length scale prevent treating the case as bit-for-bit
identical. Setup reconciliation and behavioural parity must be checked
separately:

1. **Setup parity:** reconcile and read back 08b materials, phases, models,
   inlet conditions, steam outlet, numerics, initialization, and reports on the
   new mesh, with the steam-outlet hydraulic diameter corrected to
   `0.875936 m` (`≈0.876 m`).
2. **Reference behaviour:** with `bottom` retained as a wall, run a matched E0
   reference and compare inlet realization, steam routing, liquid-inventory
   buildup, phase/mixture balance, and residual behaviour against the strongest
   available 08b evidence.

Even a close E0 comparison would support a bounded numerical-parity statement,
not exact identity between two different meshes.

## Remaining live-inspection requirements

- resolve and verify the server-side OneDrive path to the exact mesh;
- locate and prove the 08b case/setup artifact, or return to the human for it;
- obtain authority to preserve/replace one current Fluent session;
- load the mesh and run Fluent's authoritative mesh check;
- extract solver-side minimum orthogonal quality, maximum skewness/aspect
  ratio where available, cell-volume range, zone areas, and topology readback;
- reconcile Fluent readback against the local HDF5 inspection; and
- read back and save/reopen-prove the corrected steam-outlet
  turbulence/backflow hydraulic diameter before using E0 as a reference.
