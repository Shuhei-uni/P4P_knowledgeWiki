# R1600 — M04 spiral Case 4 DPM results

| Item | Verified result |
| --- | --- |
| Execution | One fresh one-way DPM update; all nine exact Case 4 injections |
| Carrier | M04, 946,967 cells, N1500; zero new carrier updates or initialization |
| Settings | [Recovered-parent audit and exact Case 4 setup](replication1600-settings-audit.md); unchanged after tracking and checkpoint reopen |
| Particle material / controls | liquid-water, 881.2109 kg/m³; Stokes-Cunningham; maximum 10000 steps; step-length factor 5; historical force/integration controls preserved |
| Tracking elapsed time | 24.121 s for the update only; excludes connection, saving, reporting and retrieval |
| Particle accounting | All nine per-injection and aggregate Final-column mass totals verified within printed precision |
| Endpoint | Post-tracking case/data pair saved, rehashed and reopened; native controller exited; Fluent idle with tracked M04 N1500 loaded |
| Carrier invariants | All 16 carrier reports unchanged; settings unchanged; iteration remains N1500 |
| Scientific status | Execution and particle accounting verified; carrier remains numerically unqualified; no mesh-independence, validation or improvement claim |

![Case 4 escaped mass flow and fate fractions](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/case4-dpm-comparison.png)

*Both calculations use the historical N1500 carrier horizon and 116.92 kg/s particle feed. Fractions use reported Final mass flow, not particle-count fractions. Historical values retain Fluent's printed rounding; the very small escaped fraction is shown separately.*

| Fate | Historical spiral, kg/s | M04, kg/s | Historical feed share | M04 feed share |
| --- | ---: | ---: | ---: | ---: |
| Escaped | 0.01655 | 0.01775 | 0.01415% | 0.01518% |
| Trapped at bottom | 113.0 | 97.16 | 96.64728% | 83.09956% |
| Incomplete | 3.907 | 19.74 | 3.34160% | 16.88334% |

| Accounting / numerical observation | Evidence and limit |
| --- | --- |
| M04 tracked parcels | 11079: 6596 trapped, 4368 incomplete, 115 escaped; zero reported aborted parcels |
| Spatial sampling | 1231 parcels per injection on M04; historical total 98388, or 10932 per injection; mesh-linked particle sampling differs |
| M04 rounded mass sum | 116.91775 kg/s versus 116.92 kg/s injected; error −0.00225 kg/s within ±0.010005 kg/s combined printed roundoff |
| Mass versus counts | 39.43% of parcel count is incomplete; 16.88% of injected particle mass is incomplete; counts do not substitute for mass |
| Escaped mass difference | M04 minus historical +0.00120 kg/s, or +7.25% of the reported historical value; arithmetic comparison, not an accuracy judgement |
| Incomplete trajectories | 19.74 kg/s remains unresolved under the preserved tracking limit; do not assign it to escape or trap |
| Carrier adequacy | [Carrier result](replication1600-carrier-results.md): inventory and flux observations remain unqualified; one-way DPM does not repair them |
| Source / version limit | Matching recovered h1600 parent plus direct July Case 4 overrides; exact July binary/full export unlocated; historical Fluent 2024 R2 versus current 2025 R2 |
| Interpretation owner | Consequential scientific interpretation and usefulness of conditional enthalpy follow-ups remain with the designated Astra planner |
| Next selection | Review this Case 4 evidence before selecting additional enthalpies; no further tracking or carrier updates are required to complete this run |
| Schedule block | `automation_update` unavailable in this chat; pause not performed or verified. Manual action: pause `phase-10` in Codex Automations when monitoring is no longer needed |

| Artifact | Evidence |
| --- | --- |
| [Summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/summary.json) | Aggregate and all nine injection fates, mass-roundoff audits and limits |
| [Per-injection CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/injection-fates.csv) | Exact feed/diameter and reported fate masses |
| [Byte-identical retrieval](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/retrieval.json) | Fourteen native files, hashes, exited controller, idle solver and paired hashes; original incorrectly named local copies retained unchanged |
| [Native controller manifest](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/raw/manifest.json) | Dispatch/completion counts, readbacks, paired endpoint, reports and transcript identity |
| [Verified terminal receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/DPM-evidence/verified-terminal.json) | Native verification saved and read back after accounting audit |
| Native pair | `C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-M04-9717fb9b/DPM-run-08b272ca/tracked-M04-N1500.{cas,dat}.h5` |
| Case SHA-256 | `ff9859f4cacdbdfe9b2294127912651fcaa88a743c5b7d11e4f361df08c33c09` |
| Data SHA-256 | `5706139f0285396f24b14153d418901cf61ab2a71ac652a39b9918ef60f06782` |
