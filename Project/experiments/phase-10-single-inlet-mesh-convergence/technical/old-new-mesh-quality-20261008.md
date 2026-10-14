# Old versus new mesh quality — 8 October 2026

**Identity correction:** the human disputes the assignment of the seven audited source files as the intended old Purnanto-style refinement family. The numeric measurements below remain tied to their exact files; the old/new family labels are not verified lineage. The original study used one supplied mesh, with refinement levels made for the convergence study. See the [Phase 10 metric register](../results.md#mesh-metric-record-and-family-identity).

Native Fluent 2025 R2 receipts exist for all seven original files. The new family is not uniformly better on every metric. Six original meshes use split `liquidinlet`/`steaminlet` boundaries; only the original 733k uses the same single-inlet layout as the new family. Counts also differ. These are mesh-statistic comparisons, not matched CFD results.

| Family | File | Actual cells | Inlet | Min OQ | Mean OQ | Max skewness | Mean skewness | Max aspect ratio | Max size change |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| old | `Separator-purnanto-60k.msh.h5` | 60,964 | split | 0.1005 | 0.9108 | 0.8995 | 0.0769 | 44.01 | 169.97 |
| old | `Separator-purnanto-64k(wall-named).msh.h5` | 63,938 | split | 0.3000 | 0.9012 | 0.7000 | 0.0882 | 63.82 | 150.71 |
| old | `Separator-purnanto-342k.msh.h5` | 342,609 | split | 0.2024 | 0.9199 | 0.7976 | 0.0606 | 68.73 | 213.88 |
| old | `Separator-purnanto-680k.msh.h5` | 679,970 | split | 0.2192 | 0.9213 | 0.7808 | 0.0642 | 73.26 | 233.77 |
| old | `Separator-purnanto-single-733k.msh.h5` | 733,979 | single | 0.1841 | 0.9657 | 0.8159 | 0.0319 | 103.15 | 219.56 |
| old | `Separator-purnanto-997k.msh.h5` | 997,604 | split | 0.1828 | 0.9603 | 0.8172 | 0.0350 | 126.42 | 189.76 |
| old | `Separator-purnanto-2_6M.msh.h5` | 2,596,657 | split | 0.1306 | 0.9410 | 0.8694 | 0.0489 | 139.46 | 232.57 |
| new | `Separator-purnanto-single-357k.msh.h5` | 357,145 | single | 0.2401 | 0.9484 | 0.7599 | 0.0434 | 110.34 | 222.75 |
| new | `Separator-purnanto-single-488k.msh.h5` | 487,746 | single | 0.2349 | 0.9530 | 0.7651 | 0.0400 | 107.47 | 230.47 |
| new | `Separator-purnanto-single-682k.msh.h5` | 681,844 | single | 0.2048 | 0.9543 | 0.7952 | 0.0382 | 115.28 | 881.63 |
| new | `Separator-purnanto-single-947k.msh.h5` | 946,967 | single | 0.2240 | 0.9584 | 0.7760 | 0.0340 | 103.49 | 209.08 |
| new | `Separator-purnanto-single-1430k.msh.h5` | 1,430,497 | single | 0.2195 | 0.9617 | 0.7805 | 0.0306 | 113.56 | 203.00 |
| new | `Separator-purnanto-single-2210k.msh.h5` | 2,209,748 | single | 0.2152 | 0.9661 | 0.7848 | 0.0265 | 125.83 | 231.95 |
| new | `Separator-purnanto-single-5480k.msh.h5` | 5,479,605 | single | 0.2033 | 0.9871 | 0.7967 | 0.0125 | 121.05 | 136.09 |

![Old and new mesh metrics](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/old-new-quality-comparison.png)

Near 680k cells, the new mesh improves mean OQ but worsens minimum OQ, maximum skewness, aspect ratio and size change versus the old split-inlet 680k file. Versus the single-inlet 733k parent, the new 682k improves minimum OQ and maximum skewness, but worsens mean OQ, mean skewness, maximum aspect ratio and maximum size change.

The earlier seven-of-seven improvement statement refers to each new mesh before and after its recorded improvement pass. It does not mean seven-of-seven improvement over the old meshes. All old and new receipts record zero free/multiply connected boundary faces and positive minimum cell volume. Dimensionless quality metrics are compared here; original files contain mixed raw coordinate scales, so dimensional volume metrics are excluded.

Evidence: [source manifest](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/source-manifest.json), [comparison CSV with exact audit paths](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/old-new-quality-comparison.csv), [new-family summary](../../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json).
