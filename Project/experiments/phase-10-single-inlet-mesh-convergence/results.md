# Phase 10 — Results

| Question | Current answer |
| --- | --- |
| Is the mesh family prepared? | Yes; seven meshes delivered and verified |
| Are all quality metrics better than the old meshes? | No; gains and regressions depend on the metric and level |
| Has a solver comparison been run? | M01–M06 failed; M07 human-skipped at N718 with paired endpoint recorded. Baseline series unqualified; BF01 also failed at N3567 |
| Why do the levels diverge? | [Failure diagnosis](divergence-diagnosis-20261011.md): all four accumulate liquid and fail phase balance before velocity/residual overflow; gravity treatment is a specific numerical suspect, not a proven unique cause |
| Is mesh independence established? | No |
| Was the previous study logged? | Yes; [Phase 2 seven-level reference](historical-reference.md) |
| Does poly reproduce tet outputs faster? | Not tested; historical reference needs qualification and timing evidence |

## Saved-field comparison after the failed series

| Evidence | Bounded result |
| --- | --- |
| [Pre-divergence field comparison](predivergence-mesh-sensitivity.md) | N1000 M01–M06 and N2000 M02–M06; spatial vector differences persist and iteration changes are comparable or larger |
| [Replication next-scope proposal](replication-next-scope.md) | One accepted carrier point, targeted refinement and paper/cost comparison; no new solve selected |
| Solver impact | Zero new updates; exact ON N3005 state restored and idle |

## Mesh-metric record and family identity

| Item | Status |
| --- | --- |
| Human clarification, 8 October 2026 | One Purnanto mesh was supplied; the intended seven levels are finer/coarser versions made for the convergence study |
| Current request | Record the seven meshes' quality metrics where available; defer missing data until later |
| Available seven-entry record | [Quality CSV](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv) and [family JSON](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json); values agree |
| Verified identity of available entries | 357k, 488k, 682k, 947k, 1430k, 2210k and 5480k; generated from the 733k workflow |
| Original-style family metrics | Historical seven-level cell counts, minimum OQ and maximum aspect ratio recovered; skewness/size change remain pending; do not substitute the seven CAD PurnantoV2 source files |
| Node counts | All seven current file node counts recovered; exact historical node count available for 900k only; see [register](setup.md#mesh-register) and [comparison](historical-reference.md#recorded-mesh-ladder) |
| Historical study located | `split_inlet_mesh_convergence_20260801`; seven historical labels and actual counts in [reference](historical-reference.md); original case files and numeric quality/timing data still need recovery |
| Previous old/new comparison | Valid file-specific statistics; the earlier assignment of those source files as the intended old paper-style family is unverified |

| Available mesh | Actual cells | Min OQ | Mean OQ | Max skewness | Max Fluent aspect ratio | Max size change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 357k | 357,145 | 0.2401 | 0.9484 | 0.7599 | 110.34 | 222.75 |
| 488k | 487,746 | 0.2349 | 0.9530 | 0.7651 | 107.47 | 230.47 |
| 682k | 681,844 | 0.2048 | 0.9543 | 0.7952 | 115.28 | 881.63 |
| 947k | 946,967 | 0.2240 | 0.9584 | 0.7760 | 103.49 | 209.08 |
| 1430k | 1,430,497 | 0.2195 | 0.9617 | 0.7805 | 113.56 | 203.00 |
| 2210k | 2,209,748 | 0.2152 | 0.9661 | 0.7848 | 125.83 | 231.95 |
| 5480k | 5,479,605 | 0.2033 | 0.9871 | 0.7967 | 121.05 | 136.09 |

## Mesh-preparation evidence

| Observation | Evidence | Limit |
| --- | --- | --- |
| One inlet and unchanged supplied CAD across seven levels | [Family audit](technical/single-inlet-mesh-family-20261008.md) | Simplified parent domain; exact paper-CAD parity not established |
| Positive cell volumes; zero free/multi boundary faces | [Native summary](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json) | Topology checks do not prove solution accuracy |
| Min OQ 0.203–0.240; max skewness below 0.80 | [Quality CSV](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv) | OQ target 0.3 unmet |
| M03 size-change maximum 881.63, with two cells >=300 | [Anchor audit](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-loaded-anchor.json) | Local positions and solution impact untested |
| Original and seven new meshes have zero centres in the checked central-pipe core | [Pipe audit](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-check.json) | Check restricted to the recorded core region |
| Shared mesh/CAD copies match working hashes | [Copy manifest](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-copy-manifest.json) | File identity only |

![Prepared mesh-family quality](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-quality.png)

Source: saved/reopened Fluent 2025 R2 audits; the grey series is each new mesh before its recorded quality pass. The M05 comparison uses its recorded recovery pass.

## Solver convergence evidence

| Current diagnostic, 11 October 2026 NZ | Result |
| --- | --- |
| [Divergence diagnosis](divergence-diagnosis-20261011.md) | Complete available M01–M04 residual transcripts and phase histories copied read-only; numerical overflow verified |
| Shared liquid balance | Last diagnostic samples have 43–70% liquid flux deficit; no liquid drain or other removal exists in this setup |
| Current baseline | M01–M06 failed; M07 user-skipped at N718; paired endpoints retained. Baseline writer exited and endpoint hashes verified before BF01 |
| M05 diagnosis snapshot | Copied transcript reaches N1643; plotted report sample N1630 has 85.71% liquid flux deficit; figures remain the preserved diagnosis snapshot |
| BF01 follow-up | ON N3000 restart failed at N3567 with k AMG divergence/FPE; 567 new updates, last verified ON N3005 pair. Writer exited and Fluent idle. [Evidence and comparison](bf01-results.md); [cause/restart audit](bf01-diagnosis.md) |
| Scientific limit | Common setup/numerical instability is the leading explanation; first unstable cell and a controlled contrast remain missing |

![Shared liquid accumulation](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/liquid-balance.png)

Native ten-iteration samples before the descriptive overflow cutoff; M05 is partial. Full source, formulas, failure sequence and residual comparison are in the linked diagnosis.

| Evidence | Verified result | Limit or next action |
| --- | --- | --- |
| Common reference | Recovered original single-inlet tet case loaded; carrier settings retained in a separate saved/reopened common case; original source hash unchanged | [Original carrier build](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/original-carrier-common-build-20261009.json); boundary aliases and unused dummy injection are the declared changes |
| Earlier launch attempts | Exited before build; no solver updates | [Port 64452 recovery](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/recovery-64452.json) |
| First M01 transfer on port 64452 | Scientific settings match the common case | First preparation stopped before any solve because Hybrid reported `Iteration=1` |
| Fresh-start coordinate | Same initialized pair reads `Iteration=0` after save/reopen; settings still match | [Diagnostic](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/iteration-start-diagnostic.json); zero solved updates |
| Failed preparation preserved | Entire folder and diagnostic case/data pair retained | [Recovery mapping](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/M01-counter-recovery.json) |
| Corrected pilot launcher | Detached Windows process creation returned success | [Current launch](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/current-launch.json); corrected pilot result is unconfirmed |
| Latest stall | GUI reported frozen; last visible line `Transcript closed`; API health timed out | Local inspection stack stopped in the external Windows status command; numerical failure is not established |
| Receipt retrieval | Cancelled only the waiting local client; removed external shell/CIM calls from passive inspection | [Stall record](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/pilot-stall-64452.json); reconcile existing receipts once Fluent responds |
| Latest startup attempt | User console reports MPI shared-memory allocation failure before mesh loading | [Startup error](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/mpi-startup-error-20261008.json); Windows memory/process state and exact cause are unverified |
| Current connection | Native receipts pass on port 60569; RUNNING controller 2572 and M05 live iterations verified | [Recovery proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/saved-resume-verification-20261010.json); password remains in memory |
| Account file recovery | All seven meshes are readable; hashes and HDF5 counts match; all seven historical N3000 case/data filenames located | [Runtime and input proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/account-runtime-proof-20261009.json); historical pairs have not been loaded or verified in Fluent |
| Current-account execution | Human resumed on 9 October; isolated runtime verified; original carrier case is the parent; full series launched on port 52660 | Older inaccessible pilot remains unconfirmed |
| Solver vertex count | M01 solver case has 959,963 active vertices; input file has 981,016 including 21,053 unused vertices; 357,145 cells and 1,620,019 faces unchanged | [Exact coordinate/face proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/M01-unused-vertex-proof-20261009.json); geometry unchanged; failed zero-update preparation preserved before retry |
| Preserved checkpoints | M01 N1000, M02 N4000, M03 N2000 and M04 N3000 retained; M05 original N5 pair hash-verified, then resumed to a saved/reopened N10 pair with exact common settings | [Recovery proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/saved-resume-verification-20261010.json); saved finite fields do not establish convergence |
| Numerical failures | Native exceptions at M01 N1756, M02 N4488, M03 N2769, M04 N3911, M05 N4180 and M06 N4175; last full pairs retained | [M06 manifest and transcript review](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/vpn-restored-20261012/M06-failure-check.json); all six remain unqualified |
| M03 failed partial pair | Old controller saved N2769 despite a native floating-point exception and finite sampled reports | Retained as failed evidence; use N2000 as the last verified full checkpoint; repaired controller now detects native exceptions before saving a new pair |
| Remaining continuation | None selected: BF01 terminal numerical failure; no unchanged numerical retry | Consequential interpretation awaits designated Astra review |
| M04 preparation interruption | Earlier GUI Cancel interrupted replacement-case writing before any solve updates. User requested restart; interrupted folder archived after verifying no old worker and preserved checkpoint hashes | [Recovery proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/M04-interrupted-recovery-7d9b7eed.json); incomplete original replacement file retained as failure evidence |
| Monitor connection | Port 60569 authenticated; native receipts and transcript stream retrieved. Bounded reader now checks live health/stream if a Scheme receipt times out during a long solve | [Latest check](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/latest-monitor-check.json); printed progress remains separate from saved checkpoints |
| Budget | Baseline spend 22302–22992 plus BF01 567 gives 22869–23559. BF01 unused allowance 433; no further solve selected | 35000 campaign cap retained; retries do not reset budgets |
| Convergence-study limit | M01–M06 numerically failed; M07 is a skipped N718 partial run | No seven-level comparison, mesh independence or tet/poly speedup claim |
| Batch preflight recovery | Waiting local client cancelled; API recovered; compact receipt and bounded reader passed live verification | [Recovery](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/batch-preflight-stall-20261009.json); native checkpoints and Fluent preserved |
| Qualification / refinement outputs / wall resolution / timing | Not available | No endpoint qualification, independence, GCI or tet/poly speedup claim |
| Codex monitor | New human-created `Phase 10` heartbeat verified ACTIVE at 30-minute intervals, attached to this chat; prompt matches exactly and there is one matching saved Phase 10 task | [Readback](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/monitor-active-readback-20261009.json); configuration verified, first scheduled execution not observed in this check; actual chat model unverified |

## R1600 provisional carrier stage

| Item | Verified result | Limit |
| --- | --- | --- |
| [Carrier results](replication1600-carrier-results.md) | N1500 completed; all four pairs rehashed/reopened; controller exited and Fluent idle | Carrier unqualified; DPM has not been tracked |
| Final window | Liquid inventory +90.895%; mean absolute liquid/mixture flux errors 91.120/53.562%; N1500 continuity 0.23252 | No convergence, mesh independence or exact-replication claim |
| Source gap | Exact nine spiral injection definitions preserved; original material/global controls unresolved | DPM and other enthalpies await source settings |
| Budget | 1500 new updates; campaign spend 24369–25059 of 35000 | All retries count; no budget reset |

| R1600 DPM observation | Evidence / limit |
| --- | --- |
| One-way Case 4 tracking complete | Nine exact injections on M04 N1500; zero new carrier updates; all particle mass accounted within printed precision |
| Final fate mass flows | Escape 0.01775 kg/s; bottom trap 97.16 kg/s; incomplete 19.74 kg/s |
| [Comparison and receipts](replication1600-dpm-results.md) | Historical escape 0.01655 kg/s; incomplete 3.907 kg/s; carrier remains unqualified and no validation/improvement claim follows |

| R1600 maximum-step sensitivity | Verified observation |
| --- | --- |
| 100000-step update | Same N1500 carrier and 11079 parcels; zero new carrier updates; one extra DPM update |
| Incomplete mass | 19.74 → 19.71 kg/s; only 0.152% reduction of unresolved mass |
| Escaped mass | 0.01775 → 0.03812 kg/s; smallest injection only; observed escape depends on tracking cap |
| [Elapsed time / limits](replication1600-dpm-limit-test.md) | Remaining incomplete mean time 9.592 → 101.9 s; persistent internal paths; exact location/cause remains unverified |

## Selected full-flow enthalpy repeats

| Item | Current selection |
| --- | --- |
| Human direction, 13 October 2026 NZ | Run M04 at 1440, 1520, 1680 and 1760 kJ/kg; incomplete particles assumed separated in efficiency |
| Execution contract | [Enthalpy sweep](replication-enthalpy-sweep.md): fresh N1500 carrier and nine source injections per case, 100000 tracking steps |
| State | All five selected enthalpies complete at N1500 plus DPM; native pairs, settings, reports and histories verified. Final writer exited and Fluent idle. [Results](replication-enthalpy-results.md) |

| Selected enthalpy result | Current evidence |
| --- | --- |
| M04 1440, 1520 and 1680 | Completed N1500 and DPM. [Partial efficiency comparison](replication-enthalpy-results.md);1680 single-fate report parsing repaired without a repeated solve/track |
| M04 1760 | Remaining case; replacement controller deployment in progress after original controller absence and pair verification |
