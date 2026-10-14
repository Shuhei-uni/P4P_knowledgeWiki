# Single-inlet mesh family — 8 October 2026

Seven meshes were rebuilt from the preserved `Separator-purnanto-single-733k.msh.h5` workflow and its supplied single-inlet CAD. The CAD file is unchanged. Every mesh has one `inlet`, the same boundary names/types, positive cell volumes, and zero free or multiply connected boundary faces after save/reopen. No CFD solve was run.

| Delivery | Location |
| --- | --- |
| Final meshes, recipes and CAD | `CAD PurnantoV2\single-inlet-refinement-20261008` beside the user's source files on the Fluent PC/OneDrive |
| Local working meshes | `C:\Users\syok443\P4P-mesh-audit-20261008\single-family` |
| Evidence | [Family summary](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json), [copy hashes](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-copy-manifest.json), [delivery receipt](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/delivery.json) |

## Selected family

Counts were allowed to change. Fixed curvature capture imposes a coarse surface-mesh floor. The selected levels use actual counts to avoid nearly duplicate meshes. Each name uses the rounded count and the original single-inlet naming convention.

| Level | Mesh | Cells | Min OQ before improvement | Min OQ saved | Max skewness saved | Mean OQ saved |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `Separator-purnanto-single-357k.msh.h5` | 357,145 | 0.1230 | 0.2401 | 0.7599 | 0.9484 |
| 2 | `Separator-purnanto-single-488k.msh.h5` | 487,746 | 0.1220 | 0.2349 | 0.7651 | 0.9530 |
| 3 | `Separator-purnanto-single-682k.msh.h5` | 681,844 | 0.1303 | 0.2048 | 0.7952 | 0.9543 |
| 4 | `Separator-purnanto-single-947k.msh.h5` | 946,967 | 0.1008 | 0.2240 | 0.7760 | 0.9584 |
| 5 | `Separator-purnanto-single-1430k.msh.h5` | 1,430,497 | 0.2140 | 0.2195 | 0.7805 | 0.9617 |
| 6 | `Separator-purnanto-single-2210k.msh.h5` | 2,209,748 | 0.1164 | 0.2152 | 0.7848 | 0.9661 |
| 7 | `Separator-purnanto-single-5480k.msh.h5` | 5,479,605 | 0.1282 | 0.2033 | 0.7967 | 0.9871 |

![Achieved refinement and quality](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-quality.png)

Actual adjacent cell-count ratios range from 1.366 to 2.480. The final level has a larger step (2.480 in count; 1.354 in effective h). Poly-hexcore uses discrete octree refinement levels, so counts need not vary smoothly with the size setting. [Ansys 2025 R2 volume-meshing guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/tgd_user_workflow_guided_tasks_vol_mesh_gen.html).

Minimum orthogonal quality improved in 7 of 7 recorded before/after comparisons. Achieved minima range from **0.203 to 0.240**. The improvement target was 0.3; a target setting is not an achieved-quality claim.

The 1,430,497-cell level was recovered after a user-requested pause. The matching live volume was preserved, full quality arguments were restored and read back, and the native quality command was invoked with iteration limit 26. The recorded recovery comparison is 0.2140 before versus 0.2195 saved. The original pre-improvement value during volume generation was not captured for this level.

| Level | Effective h = (V/N)^(1/3), m | Cell ratio to previous | Max Fluent aspect ratio | Max size change | Cells with size change >= 300 | Cells with OQ below 0.3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.03992 | — | 110.34 | 222.75 | 0 | 96 (0.027%) |
| 2 | 0.03600 | 1.366 | 107.47 | 230.47 | 0 | 138 (0.028%) |
| 3 | 0.03221 | 1.398 | 115.28 | 881.63 | 2 | 210 (0.031%) |
| 4 | 0.02887 | 1.389 | 103.49 | 209.08 | 0 | 245 (0.026%) |
| 5 | 0.02516 | 1.511 | 113.56 | 203.00 | 0 | 308 (0.022%) |
| 6 | 0.02177 | 1.545 | 125.83 | 231.95 | 0 | 390 (0.018%) |
| 7 | 0.01608 | 2.480 | 121.05 | 136.09 | 0 | 445 (0.008%) |

Aspect ratio and size change do not improve uniformly. The mesh retains thin wall-layer cells. The 682k anchor has two cells with size change at least 300, including a maximum of 881.63; additional diagnostic improvement did not reduce this maximum. The table reports those tradeoffs; improved minimum OQ and skewness do not mean every quality metric is better than every old mesh.

## Geometry and central pipe

All levels use the same preserved CAD, SHA256 `24777C3009AEA1784C629989A79E722DA17A24FC4BA30058AD73EAC59FE2F5D7`. Surface discretisation changes the polygonal area and volume slightly. Initial unrestricted coarse trials changed outlet area by 2.3%; those trials are excluded. The selected recipe holds curvature capture at 6 degrees.

| Level | Volume, m3 | Volume difference from original 733k | Inlet area difference | Outlet area difference | Maximum wall-area difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 22.723465 | -0.3058% | +0.00000% | +0.0326% | 0.6497% |
| 2 | 22.765741 | -0.1204% | +0.00000% | +0.0309% | 0.2684% |
| 3 | 22.787114 | -0.0266% | -0.00000% | +0.0379% | 0.1599% |
| 4 | 22.792997 | -0.0008% | -0.00000% | +0.1770% | 0.1606% |
| 5 | 22.795174 | +0.0088% | -0.00000% | +0.2777% | 0.2112% |
| 6 | 22.796619 | +0.0151% | -0.00000% | +0.3760% | 0.2603% |
| 7 | 22.796965 | +0.0166% | +0.00000% | +0.4281% | 0.2854% |

Maximum absolute differences from the parent are 0.3058% for volume, 0.4281% for outlet area, and 0.00000% for inlet area. These measurements establish the recorded geometry representation; they do not prove exact parity with the original paper CAD.

The central-pipe check compared the original 733k mesh with the saved 357k and 381k builds. Each has zero cell centres in the pipe core (`r < 0.25 m`, below the outlet plane `y = 6.261 m`). All lower-band cell centres lie outside the central wall. Fluid cells above the outlet plane were already present in the original. No downstream pipe-fluid region was added. [Read-only cell comparison](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/central-pipe-check.json).

![Central-pipe comparison](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/central-pipe-comparison.png)

This preserves the supplied simplified 733k domain. It does not establish full physical-geometry parity with Purnanto 2013, including the lower brine outlet and exact scroll/head profiles. The supplied CAD is the parent for this mesh-convergence family.

## Fixed controls and checks

| Item | Control/evidence |
| --- | --- |
| CAD | Same preserved single-inlet AGDB on every level; no CAD edits |
| Surface controls | Curvature and Proximity; curvature normal angle 6 degrees; minimum/maximum lengths scaled from 0.01/0.05 m |
| Local outlet sizing | Scaled from 0.05 m |
| Volume mesh | Poly-hexcore; maximum cell length scaled from 0.08 m |
| Wall layers | 12 requested layers; growth 1.15; same wall scopes; smooth transition |
| Surface improvement | Source 733k task retained; no defeaturing/step removal |
| Volume improvement | Orthogonal quality target 0.3; iteration limit 25, except recovered level 26; geometric-feature ignoring disabled |
| Saved-mesh checks | Positive volume in every cell; zero free/multi boundary faces; same names/types; native mesh check; saved/reopened counts match |
| File delivery | New destination files; SHA256 equality between local working and shared copies; original source meshes preserved |

Fluent reported local stair-stepping of all requested wall layers at one location during the selected volume builds. Thus, 12 requested layers does not mean 12 layers everywhere. No solved wall y-plus is available. These files are mesh-preparation products; mesh independence and solver convergence still require the planned CFD study.

| Boundary | Type |
| --- | --- |
| `inlet` | velocity-inlet |
| `steamoutlet` | pressure-outlet |
| `bottom` | wall |
| `inlet-wall-1-wall-separator-purnanto` | wall |
| `inlet-wall-2-wall-separator-purnanto` | wall |
| `vessel-wall-wall-separator-purnanto` | wall |
| `wall` | wall |
| `separator-purnanto:1` | wall |

Implementation: [builder](../../../../PyAnsys/scripts/meshing/build_single_inlet_family.py), [selection](../../../../PyAnsys/scripts/meshing/build_remaining_single_levels.py), [summary checks](../../../../PyAnsys/scripts/meshing/summarise_single_family.py). Fluent version: 2025 R2 / 25.2. Curvature-control meaning: [Ansys 2025 R2 surface meshing guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/tgd_user_workflow_guided_surface_mesh_gen.html).

The final read-only HDF5 check covers the original mesh and all seven selected meshes. All eight have zero cell centres inside the checked pipe core below the outlet plane. [Final pipe audit](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-check.json).

![Original and selected anchor](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-comparison.png)
