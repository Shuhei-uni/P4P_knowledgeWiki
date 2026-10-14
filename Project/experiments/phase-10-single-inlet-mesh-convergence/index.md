# Phase 10 — Single-inlet mesh convergence

| Item | Current state |
| --- | --- |
| Owner | Andy |
| Question | Can poly-hexcore reproduce the tet-reference outputs under the same Purnanto setup with less solver time? |
| Status | Tet1600 completedN1500 plus DPM; pairs, settings, histories and reports verified; writer exited and Fluent idle. All five M04 cases remain complete; old mesh failures preserved; carrier results unqualified |
| Mesh family | Seven delivered levels, from 357,145 to 5,479,605 cells |
| Solver results | Native exceptions: M01 N1756, M02 N4488, M03 N2769, M04 N3911, M05 N4180, M06 N4175. M06 N4000 pair retained. [Restored-access evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/vpn-restored-20261012/M06-failure-check.json) |
| Next evidence recommendation | Keep the single current tet1600 benchmark; check direct fluid volumes/source geometry before more solves. [Comparison scope and follow-up](replication1600-tet-results.md#comparison-coverage-and-report-claims); no further solve selected; schedule pause unverified |

| Record | Purpose |
| --- | --- |
| [Context](CONTEXT.md) | Scientific scope, current authority and decision conditions |
| [Setup](setup.md) | Mesh register and common-setting requirements |
| [Results](results.md) | Mesh-preparation evidence and future convergence results |
| [Divergence diagnosis](divergence-diagnosis-20261011.md) | Shared liquid accumulation, full failure transcripts, numerical suspects and next controlled check |
| [Pre-divergence mesh sensitivity](predivergence-mesh-sensitivity.md) | Eleven native field snapshots, mesh/iteration comparisons and attempted solver cost; no convergence claim |
| [Selected R1600 source recovery](replication1600-source-recovery.md) | Historical spiral parent and exact nine-injection definitions; recovered-source limits |
| [M04 enthalpy results](replication-enthalpy-results.md) | All five current M04 cases complete; historical tet efficiencies and M04 runtimes |
| [Current tet1600 benchmark results](replication1600-tet-results.md) | Verified fixed-N1500 cost and particle comparison; single-case coverage, geometry limit and follow-up recommendation |
| [Replication next-scope proposal](replication-next-scope.md) | Human end goal, paper targets, cost/accuracy claims and proposed small study; no new solve |
| [BF01 cause audit](bf01-diagnosis.md) | Matched histories, zero-update restart/face-field proof and proposed next control |
| [State](phase-state.yaml) | Compact preparation and execution status |
| [Paths](run-paths.yaml) | Mesh delivery, native audits and reserved run-output location |
| [Mesh-quality CSV](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv) | Verified metrics for all seven new single-inlet meshes |
| [Family JSON](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json) | Exact mesh identities, counts, geometry differences and quality evidence |
| [Mesh-family audit](technical/single-inlet-mesh-family-20261008.md) | Quality, geometry, naming and copy verification |
| [Old/new comparison](technical/old-new-mesh-quality-20261008.md) | Original-mesh audits and the limits of the quality comparison |
| [Historical study reference](historical-reference.md) | Earlier seven-level tet-lineage study, endpoints and missing quality/timing evidence |

| Related phase | Relationship |
| --- | --- |
| [Shuhei's Phase 9](../phase-09-mesh-convergence/index.md) | Existing study of five original meshes; separate mesh family and execution authority |
| [Referenced planning chat](thread://019ff5ec-f35b-7d32-80b7-4d0b1430c61d?hostId=local) | Human-provided pointer for other-mesh data; contents not yet verified |

| [R1600 carrier results](replication1600-carrier-results.md) | N1500 complete; paired/hash/settings/histories verified; liquid inventory and closure fail; source settings pending |

| [R1600 settings audit](replication1600-settings-audit.md) | Recovered carrier match, exact Case 4 DPM preparation, saved/reopened pair and source limits |

| [R1600 DPM results](replication1600-dpm-results.md) | One fresh update; all nine mass-accounted reports; M04/historical comparison and incomplete-trajectory limits |

| [R1600 tracking-limit sensitivity](replication1600-dpm-limit-test.md) | 10000 → 100000 steps; incomplete mass 19.74 → 19.71 kg/s; escaped mass 0.01775 → 0.03812 kg/s; frozen N1500 field |

## Selected full-flow enthalpy repeats

| Item | Current selection |
| --- | --- |
| Human direction, 13 October 2026 NZ | Run M04 at 1440, 1520, 1680 and 1760 kJ/kg; incomplete particles assumed separated in efficiency |
| Execution contract | [Enthalpy sweep](replication-enthalpy-sweep.md): fresh N1500 carrier and nine source injections per case, 100000 tracking steps |
| State | All five selected enthalpies complete at N1500 plus DPM; native pairs, settings, reports and histories verified. Final writer exited and Fluent idle. [Results](replication-enthalpy-results.md) |

| Current comparison | Record |
| --- | --- |
| All five M04 enthalpies complete | [Enthalpy results](replication-enthalpy-results.md) |
| Fresh tet repeat at1600 only | [Current benchmark and claim limits](replication1600-tet-results.md) |

## Supporting records

| Record | Location |
| --- | --- |
| single inlet mesh family 20261008 | [single-inlet-mesh-family-20261008.md](technical/single-inlet-mesh-family-20261008.md) |
| old new mesh quality 20261008 | [old-new-mesh-quality-20261008.md](technical/old-new-mesh-quality-20261008.md) |
