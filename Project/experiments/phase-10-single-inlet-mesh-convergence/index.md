# Phase 10 — Single-inlet mesh convergence

| Item | Current state |
| --- | --- |
| Owner | Andy |
| Question | Can poly-hexcore reproduce the tet-reference outputs under the same Purnanto setup with less solver time? |
| Status | Human-paused. M01–M06 failed; M07 user-skipped at N718 with paired endpoint retained. BF01 prepared, not deployed, zero ON updates |
| Mesh family | Seven delivered levels, from 357,145 to 5,479,605 cells |
| Solver results | Native exceptions: M01 N1756, M02 N4488, M03 N2769, M04 N3911, M05 N4180, M06 N4175. M06 N4000 pair retained. [Restored-access evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/vpn-restored-20261012/M06-failure-check.json) |
| Next work | Wait for human resume; reconcile session/controller and run selected M04 [BF01](setup.md#selected-follow-up--bf01-implicit-body-force-test) |

| Record | Purpose |
| --- | --- |
| [Context](CONTEXT.md) | Scientific scope, current authority and decision conditions |
| [Setup](setup.md) | Mesh register and common-setting requirements |
| [Results](results.md) | Mesh-preparation evidence and future convergence results |
| [Divergence diagnosis](divergence-diagnosis-20261011.md) | Shared liquid accumulation, full failure transcripts, numerical suspects and next controlled check |
| [State](phase-state.yaml) | Compact preparation and execution status |
| [Paths](run-paths.yaml) | Mesh delivery, native audits and reserved run-output location |
| [Mesh-quality CSV](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv) | Verified metrics for all seven new single-inlet meshes |
| [Family JSON](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json) | Exact mesh identities, counts, geometry differences and quality evidence |
| [Mesh-family audit](../../technical/single-inlet-mesh-family-20261008.md) | Quality, geometry, naming and copy verification |
| [Old/new comparison](../../technical/old-new-mesh-quality-20261008.md) | Original-mesh audits and the limits of the quality comparison |
| [Historical study reference](historical-reference.md) | Earlier seven-level tet-lineage study, endpoints and missing quality/timing evidence |

| Related phase | Relationship |
| --- | --- |
| [Shuhei's Phase 9](../phase-09-mesh-convergence/index.md) | Existing study of five original meshes; separate mesh family and execution authority |
| [Referenced planning chat](thread://019ff5ec-f35b-7d32-80b7-4d0b1430c61d?hostId=local) | Human-provided pointer for other-mesh data; contents not yet verified |
