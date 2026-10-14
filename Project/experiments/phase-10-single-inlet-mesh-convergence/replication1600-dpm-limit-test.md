# R1600 — M04 particle-tracking limit test

| Current result | Verified observation / limit |
| --- | --- |
| Execution | 100000-step test complete; one fresh DPM update; same 11079 parcels; zero new carrier updates |
| Incomplete mass | 19.74 → 19.71 kg/s; reduction 0.030 kg/s, or 0.152% of original incomplete mass |
| Escaped mass | 0.01775 → 0.03812 kg/s; +114.76%; entirely from the 5.621362 μm injection |
| Trapped mass | 97.16 → 97.17 kg/s |
| Remaining incomplete feed share | 16.85768% at 100000 steps |
| Elapsed trajectory time | Remaining incomplete group: mean 9.592 → 101.9 s; maximum 30.37 → 306.1 s |
| Tracking cost | 24.121 → 238.758 s; update only, excludes preparation/save/report/retrieval |
| Accounting / endpoint | Nine reports and aggregate mass-accounted within printed precision; paired hashes and strict reopen verified; controller exited; Fluent idle at N1500 |
| Observation | The eight larger injections have the same reported fate masses; extra steps mainly change the smallest injection |
| Bounded interpretation | Persistent internal trajectories are consistent with recirculation or near-cell/wall retention. Elapsed time increases substantially, so the test does not show a general failure to advance physical time. Spatial positions/paths are still needed to identify the mechanism |
| Carryover limit | Escaped mass changes substantially with the cap; the earlier close historical escape value was not tracking-limit independent |
| Next useful evidence | Locate incomplete paths and distinguish recirculation from tracking/interpolation problems before changing other controls; a further cap increase can address fine-particle carryover sensitivity but is not demonstrated to resolve bulk incomplete mass |
| Further runs | No automatic 1000000-step or physics change issued |

![M04 tracking-limit sensitivity](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/case4-dpm-comparison.png)

*The same frozen N1500 carrier field and nine releases were retracked from the preserved pre-tracking pair. Only the maximum tracking steps changed. Fractions use Final mass flow divided by 116.92 kg/s injected mass.*

| Item | Selected contract |
| --- | --- |
| Human authority | Increase the tracking limit to see where incomplete M04 particles end up |
| Question | Does a tenfold larger integration budget resolve the 19.74 kg/s incomplete mass? |
| Parent result | [Original Case 4 DPM result](replication1600-dpm-results.md); its 10000-step pair and reports remain preserved |
| Carrier field | Same M04 N1500 field; all 16 carrier reports and settings must remain unchanged |
| Controlled delta | Maximum particle tracking steps 10000 → **100000** |
| Invariants | Step-length factor 5; accuracy tolerance 1e-5; maximum refinements 20; all forces, drag, material, nine injections, boundary fates and one-way interaction |
| Release protocol | Reload verified pre-tracking N1500 pair; retrack the same nine surface injections from their original release points; no inherited positions or statistics |
| Execution | One fresh native DPM update; zero initialization or carrier updates; save/reopen paired preparation and tracked endpoints |
| Evidence | Aggregate and nine per-injection Final mass reports, parcel counts, transcript, settings readback, paired hashes and unchanged carrier reports |
| Comparison | Incomplete mass reduction; corresponding escaped/trapped mass increases; identical tracked-parcel total; full terminal mass accounting |
| Decision rule | Large incomplete reduction identifies tracking-budget sensitivity. Persistent incomplete mass requires spatial/path evidence before a cause is assigned; no silent step-size or physics changes |
| Further tracking | No automatic unbounded increases; assess this result before selecting a larger cap |
| Run budget | One additional DPM update counted separately; campaign carrier spend remains 24369–25059 of 35000 |
| Claim limit | Numerical tracking sensitivity on a preserved field; original historical-settings replication remains the 10000-step result |

| Mechanism / evidence | Status |
| --- | --- |
| Meaning of incomplete | A particle reaches maximum integration steps before a terminal boundary fate; [Fluent 2025 R2 tracking guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_use_oview.html) |
| Equal steps across meshes | Do not imply equal trajectory duration; local mesh length/velocity and accuracy refinement affect integration time steps |
| More M04 incomplete mass | Cause not yet identified; different flow paths, recirculation and local integration steps are possible mechanisms |
| Existing duration evidence | Original incomplete trajectories span 1.151–30.37 s at the same 10000-step cap; duration already varies between trajectories |
| Adaptive integration | Accuracy Control is on; step-length factor sets the initial estimate, then time steps adapt to tolerance 1e-5. A fixed step cap is not a fixed physical-duration cap |
| Duration diagnostic | Compare incomplete-trajectory minimum/maximum/mean elapsed time. A tenfold step increase with little physical-time increase is consistent with very small adaptive steps; continued physical-time growth with persistent incompleteness is consistent with long internal paths. Neither observation localizes the cause by itself |
| Particle sampling | M04 1231 parcels per injection; historical 10932 per injection; compare represented mass, not count fractions |

| Native execution | Evidence |
| --- | --- |
| [Deployment](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-launch.json) | Detached controller deployed and launched with verified source readback and native runtime |
| Native folder | `C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-M04-9717fb9b/DPM-limit100000-3c196aeb` |
| Historical tracking-control limit | Recovered h1600 parent stores 10000 steps; original July endpoint/global-control export remains unlocated. Its actual cap is not independently certified, so the original incomplete-mass difference cannot be attributed solely to the mesh |

| Final artifacts | Verified evidence |
| --- | --- |
| [Summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/summary.json) | Mass/accounting comparisons, equal parcel counts and incomplete elapsed times |
| [Per-injection CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/injection-fates.csv) | Exact feed/diameter and current fate masses |
| [Native manifest](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/raw/manifest.json) | Single leaf delta, prepared/particulate pairs, unchanged carrier reports and completed update |
| [Retrieval](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/retrieval.json) | Fourteen byte-identical files, hashes and idle/exited proof |
| [Verified terminal receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-limit100000-evidence/verified-terminal.json) | Native verification saved/read back; two campaign DPM updates total |
| Post-test case SHA-256 | `92eb2d6bffba1c0027d0cbdec709fe54763b755cc532ca10874e15fc5f7396d7` |
| Post-test data SHA-256 | `a9bc52655a9250c7fa6aae5b1b3f89d85decb93d7a427463f8929f6a699511c5` |
