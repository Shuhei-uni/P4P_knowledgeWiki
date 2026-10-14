# Phase Context — Phase 10 Single-inlet mesh convergence

## Status

| Item | Current direction |
| --- | --- |
| Owner | Andy |
| Authority | Human, 8 October 2026: same Purnanto 2013 setup; verify that poly reproduces the earlier tet results with less computational cost |
| Current work | Selected tet1600 benchmark complete; [cost/output results](replication1600-tet-results.md). No further solve selected |
| Preparation | Meshes, recipes, CAD, quality table and plot delivered with copy verification |
| Execution | TetN1500 and DPM verified; controller8676 exited; owned Fluent idle. All five M04 cases remain complete. BF01 and M01–M06 remain failed; M07 skipped |
| Access / ownership | At the terminal verification, tet controller8676 had exited and owned Fluent was idle; no active writer was verified. See the [terminal proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/verified-terminal.json) |
| Next evidence recommendation | Keep the single current tet1600 benchmark and check direct fluid volumes/source geometry before further solves. The observed2.0513 carrier-time ratio applies only to this fixed-N1500 case; [coverage and recommendation](replication1600-tet-results.md#comparison-coverage-and-report-claims) |
| Follow-up authority | No additional solve selected. The earlier implicit-body-force test is closed and unqualified; more enthalpy repeats remain a recommendation, not a run selection |
| Schedule | Pause monitor manually if still enabled because automation_update is unavailable; actual schedule state/pause remains unverified |
| Other studies | Existing phase records and session authority remain with their owners |

## Evidence anchors

| Source | Observation | Limit |
| --- | --- | --- |
| [Mesh-family audit](../../technical/single-inlet-mesh-family-20261008.md) | Seven levels; one inlet; same supplied CAD and boundary names/types; positive volumes; zero free/multi boundary faces | Mesh checks do not establish solver convergence or physical accuracy |
| [Human-supplied quality CSV](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv) and [family JSON](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-summary.json) | Direct file inspection: all seven names, counts and shared quality values agree | These files describe the new single-inlet family, not old-mesh solver results |
| [Delivery receipt](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/delivery.json) | Seven mesh copies and CAD hash-verified; workflows delivered | File delivery is complete; study solves are not |
| [Pipe-core audit](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/selected-central-pipe-check.json) | Original and seven new meshes have zero cell centres in the checked pipe core below the outlet | Check covers the stated core region, not full paper-CAD parity |
| [Old/new quality comparison](../../technical/old-new-mesh-quality-20261008.md) | File-specific quality comparisons; six audited source files use split inlets | Human disputes their identification as the intended old paper-style family; lineage unverified |
| [Metric register](results.md#mesh-metric-record-and-family-identity) | Current seven-entry metrics and node counts recorded; historical cell counts, minimum OQ and maximum aspect ratio recovered | One supplied Purnanto mesh plus user-generated refinement levels; remaining historical metrics pending |
| [Human-supplied chat reference](thread://019ff5ec-f35b-7d32-80b7-4d0b1430c61d?hostId=local) | Human identified this chat as a source for other-mesh data | Chat contents not verified; `read_thread` unavailable in this session |
| [Existing Phase 9 results](../phase-09-mesh-convergence/results.md) | Repository record points to histories and endpoints for the original five-mesh study | Linked `PyAnsys/output/phase9-mesh-convergence/20261007` folder is absent from this checkout; verify native data before reuse |
| [Final anchor audit](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/final-loaded-anchor.json) | 682k mesh has two cells with size change >=300; maximum 881.63 | Locations and effect on the solution remain untested |
| [Historical tet-lineage study](historical-reference.md) | Earlier seven-level study is logged in Phase 2; 1.69–13.37M actual cells; pressure/velocity remained iteration-dependent | Exact nodes recovered for 900k only; skewness, size change and timing pending; tet evidence is from the historical parent |
| Human explanation | Both studies target the same Purnanto 2013 setup; Shuhei switched to poly for speed | Same setup is the intended invariant; performance gain remains a hypothesis to measure |

## Human clarification — replication purpose

| Item | Current direction |
| --- | --- |
| End goal | Repeat Purnanto 2013 on the new mesh and assess output agreement plus measurable improvement |
| Immediate work | Saved OFF fields at N1000 and N2000 compared; [result](predivergence-mesh-sensitivity.md); zero new solver updates |
| Further body-force diagnosis | Not selected following the human change of direction |
| Historical residual expectation | Human, 13 October 2026 NZ: continuity nonconvergence is expected. Exact-protocol replication remains the goal; continuity alone is not a stop or rejection gate |
| Selected next run | Provisional M04 carrier complete at N1500; [results](replication1600-carrier-results.md); exact Case 4 DPM complete; [particle results](replication1600-dpm-results.md); conditional enthalpies require review |
| Next-scope advice | [Replication proposal](replication-next-scope.md); M04 replication selected, awaiting exact historical settings parity |
| Claim boundary | Pre-divergence agreement is diagnostic mesh sensitivity; paper agreement alone does not prove improved physical accuracy |

## Phase contract

| Item | Requirement |
| --- | --- |
| Question | Can the poly-hexcore family reproduce tet-reference outputs within selected tolerances, using less wall-clock time under the same Purnanto setup? |
| Reason | Verify the proposed speed benefit while preserving the outputs of interest |
| In scope | Qualify local mesh issues; verify setup parity; compare refinement trends and tet/poly outputs; measure solver cost |
| Controlled change | Baseline: mesh type and resolution; follow-up BF01: implicit body force off to on on fixed M04, after the baseline queue |
| Geometry invariant | Supplied single-inlet 733k CAD, sealed bottom and recorded outlet geometry; no added brine outlet |
| Solver invariants | Baseline uses recovered original settings throughout; BF01 changes only implicit body-force treatment under the [selected follow-up contract](setup.md#selected-follow-up--bf01-implicit-body-force-test) |
| Setup parity | Check geometry and inlet loading; historical split-inlet and current single-inlet representations are a documented difference to resolve |
| Runtime invariant | Same hardware, Fluent version, precision, processor allocation and reporting policy for direct timing comparisons |
| Initial-state control | Use one documented initialisation/transfer policy; distinguish startup drift from refinement effects |
| Evidence standard | Mesh/readback proof; active residuals; boundary/source conservation; inventories and histories; spatial flow evidence; output comparisons |
| Performance standard | Solver wall-clock time, seconds per iteration, iterations to the selected qualified window and memory; report mesh/setup/I/O time separately |
| Comparison basis | Time to comparable output accuracy and numerical maturity; equal cell or iteration counts alone do not establish equivalence |
| Claim limit | Mesh sensitivity for this simplified domain and selected model; no automatic Purnanto 2013 physical validation |
| Quality limit | Minimum OQ 0.203–0.240; target 0.3 unmet; wall-layer stair-stepping reported at one location |
| Refinement limit | Last count step is larger; use actual ratios, not an assumed constant refinement ratio |
| Compute boundary | Execution resumed; recovered original carrier reference selected; 5000 iterations per mesh, including smoke updates |

## Candidate experiment families

| Family | Controlled delta | Fixed context | Required evidence | Status |
| --- | --- | --- | --- | --- |
| Local mesh qualification | Inspect cells at quality extremes, especially the 682k size-change pair | Delivered mesh identity | Location, wall-layer/transition context and repair decision | Next preparation item |
| Single-inlet refinement series | Seven recorded mesh levels | Recovered original carrier case; fixed N5000 horizon | Convergence and conservation checks; selected scalar/spatial outputs versus refinement | M07 user-skipped at N718; M01–M06 numerically failed |
| BF01 body-force diagnostic | Implicit body force on | Preserved M04 N3000 fields; 1000 additional updates; all other settings fixed | Residual/speed comparison; conservation and inventory; strict save/reopen proof | Failed at N3567; terminal evidence verified; no further solve selected |
| Tet/poly comparison | Mesh type and independently documented refinement | Same audited Purnanto setup and operating point | Output differences within selected tolerances; time to comparable qualified results | Human-selected question; references/timing to qualify |

## Decision conditions

| Condition | Action | Claim boundary |
| --- | --- | --- |
| Common setup and compute envelope selected | Record exact case identity, readback and budget before execution | Current human execution request; other phases remain closed |
| Local mesh issue affects a critical region | Inspect or repair; record a new mesh identity and repeat relevant checks | Do not silently substitute a repaired artifact |
| A run remains numerically unqualified | Recover within the selected envelope or report incomplete evidence | Do not interpret unconverged differences as mesh error |
| Qualified outputs approach a stable refinement trend | Assess sensitivity against the selected output tolerances | Independence applies only to the measured outputs and tested range |
| Poly matches qualified tet outputs at lower elapsed cost | Report measured speedup and output differences | Scoped to the hardware, setup and accuracy criteria tested |
| Historical tet endpoints remain unqualified | Recover comparable evidence or use a declared common-state diagnostic | Do not claim accuracy equivalence from the old N3000 endpoints alone |
| Trend is non-monotonic or dominated by startup/film time | Report the ambiguity and separate those effects | Do not force an extrapolated order or uncertainty estimate |

## Selected full-flow enthalpy repeats

| Item | Current selection |
| --- | --- |
| Human direction, 13 October 2026 NZ | Run M04 at 1440, 1520, 1680 and 1760 kJ/kg; incomplete particles assumed separated in efficiency |
| Execution contract | [Enthalpy sweep](replication-enthalpy-sweep.md): fresh N1500 carrier and nine source injections per case, 100000 tracking steps |
| State | All five selected enthalpies complete at N1500 plus DPM; native pairs, settings, reports and histories verified. Final writer exited and Fluent idle. [Results](replication-enthalpy-results.md) |
