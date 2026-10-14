# M04 spiral enthalpy comparison — completed set

| Enthalpy (kJ/kg) | M04 efficiency (%) | Historical tet efficiency (%) | Difference (percentage points) | Status |
| --- | ---: | ---: | ---: | --- |
| 1440 | 99.972936 | 99.984272 | -0.011336 | Carrier N1500 and DPM complete |
| 1520 | 99.965412 | 99.980647 | -0.015236 | Carrier N1500 and DPM complete |
| 1600 | 99.967397 | 99.985845 | -0.018449 | Carrier N1500 and DPM complete |
| 1680 | 99.967927 | 99.982606 | -0.014679 | Carrier N1500 and DPM complete |
| 1760 | 99.959215 | 99.973618 | -0.014403 | Carrier N1500 and DPM complete |

![Assumed separation and incomplete mass](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/efficiency-comparison.png)

*Efficiency = 100 × (1 − escaped Final mass / injected mass). Incomplete mass is assumed separated by human direction. M04 uses 100000 tracking steps; the original July cap remains unverified.*

| Comparison provenance | Scope |
| --- | --- |
| Tet values in the table above | Historical July results at all five enthalpies; these values are retained as the historical comparison |
| Fresh tet repeat | Only 1600 kJ/kg was rerun on the current PC and Fluent. Its estimate is 99.880431%, separate from the historical 99.985845% |
| Fresh runtime comparison | [Tet1600 benchmark results](replication1600-tet-results.md) contain the current timing and particle-fate comparison. No fresh tet timing exists here for the other four enthalpies |

| Evidence / limit | Verified record |
| --- | --- |
| 1440 and 1520 | Native strict completion, N1500, one DPM update each; paired hashes, histories and raw reports recovered |
| 1680 report repair | Some single-fate injection reports omit Net. Count-fate consistency, feed closure, all nine reports and aggregate reconciliation pass; saved tracked pair reopened; zero new carrier or DPM updates |
| Original 1680 error | Immutable `H1680/raw/manifest.json` retains STOPPED status and original assertion. Separate [verified record](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/H1680/verified-manifest.json) records completed evidence |
| Source retrieval | [Byte-identical collection](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/collection-recovery.json): 96 files, 30 paired-file hashes, old controller absent |
| Derived vorticity | Pre-reopen checkpoint report 117.948107 s^-1; DPM transcript/live result 117.945526 s^-1, a −0.002188% difference. Other 15 reports exactly unchanged. The tracked pair reopen preserves the current 16 reports. No solved update was added |
| Prior sweep spend | 4500 carrier updates and 3 DPM updates. Campaign carrier spend 28869–29559 of35000; last1760 allocation1500 remains withincap |
| Interpretation | Fixed-horizon reconstructed historical comparison. Assumed incomplete capture does not qualify carrier conservation, mesh independence, validation or superiority |
| Next | Selected five-case set complete; no further solve selected. Pause Phase10 schedule manually if it is still enabled; automation_update is unavailable here |

| Final set verification | Evidence |
| --- | --- |
| All five cases | N1500 carrier and one post-carrier DPM update at100000 steps per case; earlier1600 10000-step test separately preserved |
| 1760 endpoint | Case/data paired hashes, strict reopen, exact settings, nine injection reports, terminal count/mass accounting, histories and closed residual/DPM transcripts verified; controller40060 exited and owned Fluent idle |
| Campaign carrier spend |30369–31059 of35000;6000 updates in the four-case sweep,7500 in all five replication carriers; repair added0 |
| DPM spend |Four new sweep updates; six campaign updates including the original1600 10000-step run and100000-step sensitivity; repair added0 |
| [Final comparison CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/efficiency-comparison.csv) |Mass flows, efficiencies and differences in percentage points |
| [Terminal proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/verified-series-terminal.json) |Native series-verification publication and successful readback, case identities, budget and idle/exited proof |
| Schedule block |No automation_update tool in this session. Schedule state and pause cannot be verified. Required manual action: pause Phase10 if it remains enabled. No pause claimed |

## Cell count and measured runtime

| Comparison question | Supported answer | Limit |
| --- | --- | --- |
| Similar efficiency estimate? | Maximum difference is 0.018449 percentage points across the five enthalpies | Uses the human-selected incomplete-as-separated convention; original July tracking cap remains unverified |
| Smaller mesh? | M04 has 946,967 cells versus 2,964,593 tet cells: 68.06% fewer | Cell reduction does not measure runtime or memory reduction |
| Faster than the historical tet run? | No verified speedup can be calculated | Recovered historical logs and case records have no measured solve duration; different workstation, Fluent version and rank count also prevent a controlled mesh comparison |
| More accurate or better overall? | Not established | Close efficiency estimates do not establish carrier qualification, mesh independence or improved accuracy |

| Enthalpy (kJ/kg) | N1500 carrier (min) | DPM at 100000-step limit (min) | Combined compute (min) |
| --- | ---: | ---: | ---: |
| 1440 | 41.94 | 4.17 | 46.11 |
| 1520 | 42.00 | 4.29 | 46.29 |
| 1600 | 42.01 | 3.98 | 45.99 |
| 1680 | 42.19 | 4.63 | 46.82 |
| 1760 | 41.59 | 4.26 | 45.85 |

*Carrier time is the sum of elapsed blocking solve calls, including the smoke update and in-solve monitoring. DPM time covers one update. Preparation, initialization, checkpoint save/reopen, transfer and post-solve report extraction are excluded. The earlier 1600 10000-step DPM run is excluded from this per-case table. Sources and hashes: [runtime audit](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/runtime-audit.json), [runtime CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/runtime-comparison.csv).*

| Bounded statement / next evidence | Scope |
| --- | --- |
| Report wording | M04 reproduces the historical estimated separation efficiency within 0.019 percentage points using 68% fewer cells, under the assumption that incomplete particles are separated |
| Runtime follow-up | Completed [same-PC1600 tet benchmark](replication1600-tet-results.md); geometry and configuration-stage limits retained |

| Completed follow-up | Current result |
| --- | --- |
| Same-PC1600 tet repeat |[Tet benchmark results](replication1600-tet-results.md):N1500 plus DPM complete; carrier86.17 versus42.01 min; DPM7.06 versus3.98 min |
| Comparison limit |Inferred fluid volumes differ27.9610 versus22.7930 m³; timing ratio is a cost observation for these two models and does not isolate mesh construction |
