# Phase 7b — Historical Cutoff Mapping

**Observed:** read-only local HDF5 inspection of the exact SSD artifacts below
completed on 2026-09-08. No Fluent session was contacted or changed.

**Inferred:** the historical truncated mesh's `y = -6.441 m` bottom maps to
`y = +0.020 m` in the staged full mesh. Matching inlet edges and the separate
steam-outlet plane establish a vertical offset of approximately `+6.461 m`.
This resolves the vertical collector cap; it does not establish complete
three-dimensional geometry equivalence or a physical pool elevation.

## Exact artifacts

| Role | Artifact | SHA-256 |
| --- | --- | --- |
| Historical truncated reference | [mesh-900k_initialized.cas.h5](</Volumes/Extreme SSD/P4P/experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/andy-07a-mesh-study/split_inlet_mesh_convergence_20260801/mesh_900k/mesh-900k_initialized.cas.h5>) | `2771ef93c30518c5706688814474c3860e2693c2a70ed7893e5c82bcc9361b9c` |
| Staged full geometry | [brine-outlet-620kcells.msh.h5](</Volumes/Extreme SSD/P4P/experiments/phase-07b-full-geometry-liquid-removal/inputs/brine-outlet-620kcells.msh.h5>) | `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394` |

**Observed:** the historical reference stores `5,335,623` cells, `923,066`
nodes and `10,743,466` faces. Its historical `900k` filename is not its cell
count. The staged full mesh stores `620,431` cells, `1,770,229` nodes and
`2,852,567` faces. These hashes identify geometry sources, not a qualified
steady case/data parent.

The historical prepared-07c descendant
[start_from_prepared07c_fresh_hybrid_tau0p020_ramp0.cas.h5](</Volumes/Extreme SSD/P4P/experiments/andy-sinks/split_inlet_mass_balance_sink_control_20260810/mesh-900k_band0p140165_target116p92_v1/start_from_prepared07c_fresh_hybrid_tau0p020_ramp0.cas.h5>)
was also inspected during the initial investigation. **Observed:** it has the
same counts, face-zone names and coordinate-array bytes as the truncated
reference. Both NumPy coordinate-array byte hashes are
`5fcee23dff84ea240eae3abd915241130b10cc4bb11e270d6724057765faadcd`.
This connects the inspected historical geometry to the old sink lane; it does
not establish equality of solver settings or solution fields. The reproducible
two-artifact proof below does not require that descendant.

## Observed vertical landmarks

All coordinates in this table are metres. The full artifact stores `m`; the
historical metric interpretation is supported by the prior geometry records
and matching inlet dimensions and areas.

| Landmark | Historical y | Full-mesh y | Full minus historical |
| --- | ---: | ---: | ---: |
| Liquid-inlet lower edge | `-4.757000000000` | `1.703999996185` | `6.460999996185` |
| Liquid-inlet upper edge | `-4.033000000000` | `2.427999973297` | `6.460999973297` |
| Steam-inlet lower edge | `-4.757000000000` | `1.703999996185` | `6.460999996185` |
| Steam-inlet upper edge | `-4.033000000000` | `2.427999973297` | `6.460999973297` |
| Steam-outlet plane | `-0.200000000000` | `6.261000156403` | `6.461000156403` |

The two inlet strips share edges, so they are redundant consistency checks;
the steam-outlet plane supplies the independent vertical landmark. The inlet
height is approximately `0.724 m` in both meshes. Corresponding polygonal
boundary areas also agree closely:

| Boundary | Historical area [m²] | Full area [m²] | Absolute relative difference |
| --- | ---: | ---: | ---: |
| Liquid inlet | `0.004889896000` | `0.004889679675` | `0.004424%` |
| Steam inlet | `0.519286104000` | `0.519286355645` | `0.0000485%` |
| Steam outlet | `0.602027079223` | `0.601305174066` | `0.119912%` |

**Observed:** the five elevation offsets span `1.8310547034e-7 m`. Their
median is `6.460999996185302 m`. The extractor requires offset spread below
`1e-5 m`, horizontal historical-bottom and steam-outlet planes, and corresponding
boundary-area differences no larger than `0.5%`. These are reproducibility
and landmark-consistency checks, not physical validation tolerances or a
statistical uncertainty estimate.

**Inferred:** adding the median offset to the observed historical bottom
`-6.441 m` yields `+0.019999996185 m`; using the smallest and largest offsets
yields `[+0.019999973297, +0.020000156403] m`. The declared cap is
`+0.020 m`, retaining the historical cutoff's millimetre reporting precision.
The rounding difference must itself pass the `1e-5 m` consistency check.

The separate historical full-mesh initial-pool patch at `y <= 0 m` is therefore
20 mm below this mapped cutoff. Shuhei's later 342k truncated mesh also has
its bottom at approximately `y=0`, as documented in its
[own mesh inspection](../phase-07-simplified-purnanto-liquid-removal/mesh-inspection.md).
Neither zero-plane reference replaces Andy's selected historical cutoff.

## Numerical lower datum and approved height fractions

**Observed:** the minimum y coordinate across all nodes in the exact full mesh
is `-1.4845837354660034 m`. The same minimum occurs on its `wall` boundary.
Use this as the reproducible numerical mesh datum `y_b`; no plant elevation or
exact underlying CAD floor is claimed.

**Inferred from the approved fractions:** with cap `y_c = +0.020 m`, the
available vertical span is `H = y_c - y_b = 1.5045837354660034 m`. Each top is
`y_top = y_b + f H`:

| Fraction f | Top y [m] |
| --- | ---: |
| 20% | `-1.1836669883728028` |
| 40% | `-0.8827502412796020` |
| 60% | `-0.5818334941864014` |
| 80% | `-0.2809167470932006` |
| 100% | `+0.0200000000000000` |

These are vertical height fractions, not fluid-volume fractions. The common
lower datum and cap do not alone define the source's horizontal coverage or
active cell selection; those belong to the selected design/setup contract.

**Missing Info:** actual Fluent cell-centroid selection, selected cell counts,
zone volumes and live coordinate readback. The staged mesh has no stored cell
centroid/volume datasets under `meshes/1/cells`. This inspection does not
substitute reconstructed approximate centroids for later solver-side evidence.

## Extraction and reproduction

The read-only
[inspector](../../../PyAnsys/scripts/inspection/inspect_phase07b_geometry.py)
reuses coordinate, zone-topology, polygon-area and hashing helpers from
[inspect_fluent_mesh_h5.py](../../../PyAnsys/scripts/inspection/inspect_fluent_mesh_h5.py).
It verifies both whole-file hashes before deriving the mapping. Input paths
are parameters so verified copies can be used after transfer. Existing output
files are not overwritten; inconsistent landmarks exit with an error before a
passing evidence file is written.

**Observed source structure:** historical coordinates are in
`/meshes/1/nodes/coords/4` (node IDs `1–923066`). Full coordinates are in
`/meshes/1/nodes/coords/1`, `/2` and `/3` (node IDs `1–1228`,
`1229–1636902` and `1636903–1770229`). Both use
`/meshes/1/faces/zoneTopology/{name,id,minId,maxId,zoneType}`.

| Mesh / boundary | Zone ID | Inclusive face IDs | Face-connectivity section |
| --- | ---: | --- | --- |
| Historical liquid inlet | 50062 | `10735500–10735571` | `/meshes/1/faces/nodes/1` |
| Historical steam inlet | 50063 | `10735572–10736999` | same shared section |
| Historical bottom | 50059 | `10737000–10742437` | same shared section |
| Historical steam outlet | 50065 | `10742438–10743466` | same shared section |
| Full wall | 42 | `2809759–2849467` | `/meshes/1/faces/nodes/3` |
| Full steam outlet | 40 | `2849791–2850664` | `/meshes/1/faces/nodes/5` |
| Full liquid inlet | 39 | `2850665–2851491` | `/meshes/1/faces/nodes/6` |
| Full steam inlet | 38 | `2851492–2852567` | `/meshes/1/faces/nodes/7` |

Each connectivity section contains `nnodes` and flat `nodes` datasets. The
inspector cumulatively sums `nnodes` and intersects each zone's face-ID range
with each section's range before slicing flat node IDs. This explicitly handles
the historical case's shared connectivity section. It records the exact slices
in JSON, then computes boundary bounds from referenced nodes and polygon areas
using Newell's area-vector formula.

From the repository root, the actual SSD reproduction command was:

```bash
PYTHONDONTWRITEBYTECODE=1 PyAnsys/.venv/bin/python \
  PyAnsys/scripts/inspection/inspect_phase07b_geometry.py \
  --old-mesh '/Volumes/Extreme SSD/P4P/experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/andy-07a-mesh-study/split_inlet_mesh_convergence_20260801/mesh_900k/mesh-900k_initialized.cas.h5' \
  --full-mesh '/Volumes/Extreme SSD/P4P/experiments/phase-07b-full-geometry-liquid-removal/inputs/brine-outlet-620kcells.msh.h5' \
  --output PyAnsys/output/phase07b_preparation/geometry-proof-20260908.json
```

Omit `--output` to reproduce to stdout without creating another file. The
[generated JSON](../../../PyAnsys/output/phase07b_preparation/geometry-proof-20260908.json)
is an ignored machine-evidence extract. This Project record retains the
source identities, material observations, inference and claim limits when that
local extract or the SSD is unavailable.

**Observed validation:** the actual SSD pair passed the extractor. Focused
rejection checks also passed: a substituted input failed its hash check, a
1 mm inconsistent steam-outlet elevation failed the offset check, and a
non-horizontal historical bottom failed its plane check.

## Live Fluent mask check

**Observed, 2026-09-08:** the copied PC mesh loaded through Fluent 2025 R2.
A source-free on-demand UDF compiled with the built-in compiler and inspected
owned fluid cells across 16 partitions. It found 620,431 cells, total fluid
volume `27.063085694804826 m3`, and no invalid-volume cells in its check.

| Mask | Owned cells | Geometric volume [m3] |
| --- | ---: | ---: |
| S20 | 21,516 | 0.5612436425388415 |
| S40 | 41,258 | 1.4681621275156953 |
| S60 | 59,465 | 2.462894989702537 |
| S80 | 78,608 | 3.3772762231439044 |
| S100 | 98,519 | 4.40172924390485 |

The probe used `centroid_y <= top`; the observed lowest centroid,
`-1.4803939300597493 m`, lies above the common lower bound. Thus this probe
and the design's two-sided predicate select the same cells on this mesh.
All five regions are nonempty and nested. These are geometric volumes,
not liquid inventories or proof of a working source.

The [probe source](../../../PyAnsys/scripts/inspection/phase07b_collector_probe.c)
has SHA-256 `843f22b34210935461a841a0310cd4b05a968796e36b73e88a91889b879e6aa7`.
Its API upload passed exact text readback before compilation. The live
[extracted records](../../../PyAnsys/output/phase07b_preparation/live-collector-geometry.json)
retain each check. No initialization or solution iteration was requested;
phase field storage was unallocated. Source-mask equivalence after source
installation, phase-velocity access, and mask-boundary flux integration
remain separate implementation checks.
