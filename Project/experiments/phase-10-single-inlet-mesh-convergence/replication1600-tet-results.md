# Tet1600 benchmark — completed

| Result | Verified evidence |
| --- | --- |
| Execution |1500 new carrier updates, including smoke; one DPM update at100000 steps; no repeated solved updates |
| Current endpoint |Tet trackedN1500 pair preserved; controller8676 absent; owned Fluent idle |
| Verification |37 retrieved files byte-identical;10 native case/data file hashes verified; paired N0/N1/N1001/N1500 and trackedN1500 reopen checks pass |
| Carrier record |Residual coverageN1–1500;16 report histories with final500 evidence; closed transcripts |
| Particle record |Nine injection reports reconcile with aggregate count and represented mass;98388 tracks;0 aborted |
| Classification |Completed fixed-horizon comparison; carrier unqualified |

|1600 kJ/kg comparison |M04 |Tet |
| --- | ---: | ---: |
| Cells |946967 |2964593 |
|1500 carrier updates (min) |42.01 |86.17 |
| Carrier seconds/update |1.6803 |3.4469 |
| DPM at100000-step limit (min) |3.98 |7.06 |
| Combined compute (min) |45.99 |93.23 |
| Assumed-capture efficiency (%) |99.967397 |99.880431 |
| Escaped represented mass (kg/s) |0.03812 |0.1398 |
| Trapped represented mass (kg/s) |97.17 |113.0 |
| Incomplete represented mass (kg/s) |19.71 |3.764 |

*Efficiency =100 × (1 − escaped mass / injected116.92 kg/s), with incomplete mass assumed separated by human direction. Printed fate masses have limited precision. Timing includes only the carrier iterate calls and one DPM update; setup, save/reopen and retrieval are excluded. Tables are the core evidence for this scalar cost/output comparison.*

| Observation / limit | Meaning |
| --- | --- |
| Carrier time ratio |Tet took2.0513 times the M04 carrier compute time in these runs |
| DPM time ratio |Tet took1.7743 times the M04 tracking time |
| Efficiency difference |Current tet estimate is0.08697 percentage points below M04 under the selected capture convention |
| Inferred fluid volume |Tet27.961010 m³ versus M04 22.792997 m³; identical constant-density, all-vapor N0 starts indicate a22.67% difference |
| Geometry limit |Direct mesh-volume and source geometry audit pending; time ratio does not isolate mesh construction from geometry |
| Configuration-stage limit |Tet had uncoupled injections installed before the carrier solve; M04's original1600 carrier preceded installation. Tracking was dispatched only afterN1500 |
| Numerical limit |Tet final500 liquid inventory range20.0948 kg,39.22% of its51.2317 kg mean; fixed-horizon completion does not qualify carrier conservation or stationarity |
| Historical source limit |Reconstructed recovered spiral parent; exact July binary/full settings export unlocated |
| Accuracy claim |Not established by agreement or by the efficiency estimate being higher on either mesh |

| Budget / next action | Current record |
| --- | --- |
| Carrier campaign spend |31869–32559 of35000; remaining2441–3131; this benchmark added1500 |
| DPM campaign spend |7 updates, including this single tet tracking update |
| Further solve |None selected; preserve current tet and prior M04 endpoints |
| Next evidence |Review the fluid-volume/source-geometry difference before attributing the observed cost difference to mesh alone |
| Schedule block |automation_update is unavailable; pause the Phase10 automation manually if still enabled. No native pause or schedule-state claim |

## Comparison coverage and report claims

| Evidence coverage | What it supports |
| --- | --- |
| Current M04 runs | All five enthalpies: 1440, 1520, 1600, 1680 and 1760 kJ/kg; N1500 carrier and nine-injection DPM results |
| Current-PC tet repeat | Only 1600 kJ/kg was rerun on the current PC and Fluent version |
| Other tet enthalpies | Historical July results only; no fresh runtime benchmark at 1440, 1520, 1680 or 1760 kJ/kg |
| Historical versus current tet1600 | Historical efficiency estimate 99.985845%; current repeat 99.880431%. These are separate runs and must not be combined |
| Supported timing statement | At 1600 kJ/kg, M04 completed 1500 flow iterations in 42 minutes, compared with 86 minutes for the tet model on the same PC and Fluent version |
| Required timing limit | This measures cost at a fixed iteration count. It does not measure time to a converged solution or establish a speed advantage across all enthalpies |
| Mesh claim limit | The inferred volume difference and unqualified carrier fields prevent a claim that mesh construction alone caused the time difference, or that M04 is more accurate or better overall |

*Timing scope and exclusions are defined above. The [five-enthalpy comparison](replication-enthalpy-results.md) retains the historical tet values separately from this current repeat.*

## Follow-up recommendation documented 14 October 2026 NZ

| Decision item | Recorded recommendation / authority |
| --- | --- |
| Keep the single benchmark for now | It is enough to report the observed runtime difference for the 1600 kJ/kg case with the stated limits |
| Check geometry before more solves | Confirm direct fluid volumes and source geometry. Additional enthalpy points cannot resolve the geometry difference |
| Value of more enthalpies | Matched repeats could test whether the runtime trend persists across the operating range after the geometry issue is resolved |
| Available carrier budget | 2441–3131 updates remain. One additional N1500 case fits under the upper-bound spend; all four would require 6000 updates and exceed the current cap. Two cannot be guaranteed within the cap |
| Human request | Document the results and this discussion. No additional tet run, mesh change or budget increase has been selected |
| Scientific review | Consequential interpretation remains with the designated Astra planner; these recommendations do not mark either carrier as qualified |

| Evidence | Artifact |
| --- | --- |
| [Terminal proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/verified-terminal.json) |Actual horizon, native pair hashes, idle/exited proof, budget and native publication readback |
| [Independent local verification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/independent-terminal-check.json) |Residual and nine-injection accounting; checkpoint boundary rows1 and1001 are reprinted at the next block start, with1500 new-update rows overall |
| [Comparison CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/cost-output-comparison.csv) |Timings, efficiencies and particle fate masses |
| [Machine summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/comparison-summary.json) |Source hashes, ratios and claim limits |
| [Coverage and follow-up record](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/results-review.json) |Current versus historical tet coverage, budget and documented recommendation; no new run selection |
| [Immutable native evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/H1600/raw/manifest.json) |Settings, checkpoints, histories, residual and DPM transcripts |
