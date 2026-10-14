# M04 full-flow spiral enthalpy replication

| Item | Selected contract |
| --- | --- |
| Authority | Human, 13 October 2026 NZ: run the other enthalpies; assume incomplete particles are trapped, as in the earlier comparison |
| Question | How does the M04 liquid escape fraction compare with the historical spiral tet cases across enthalpy? |
| Mesh | M04, 946967 cells; same saved mesh as the completed 1600 kJ/kg repeat |
| Queue | 1440, 1520, 1680, 1760 kJ/kg; reduced-flow Case 1 excluded |
| Parent | Saved/reopened Case 4 DPM-ready M04 pair; zero prior DPM updates; exact hashes in the [job specification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/job-spec.json) and native configuration |
| Initialization | Reload that parent for every case; apply case-specific source values; fresh Hybrid initialization; no transfer of developed fields between enthalpies |
| Carrier | N1500 per case including one smoke update; then fixed 1000 and final 499 updates; paired N0, N1, N1001, N1500 checkpoints |
| Particle protocol | One fresh post-carrier DPM update with all nine exact historical surface injections for that enthalpy |
| Tracking cap | 100000 steps, matching the latest M04 Case 4 test; recovered archived parent used 10000. The original July sweep cap remains unverified |
| Other invariants | Verified recovered spiral carrier physics/numerics, one-way DPM, material, forces, drag, step factor 5, accuracy tolerance 1e-5, wall fates, global injection frame; no body-force change |
| Efficiency | 100 × (1 − escaped Final mass flow / injected liquid mass flow). Incomplete mass is assumed separated by human direction; retain its measured mass in the output |
| Budget | Prior campaign spend 24369–25059; four cases allocate 6000 new carrier updates. No-retry terminal spend 30369–31059 of 35000. DPM counted separately |
| Failure action | Preserve native error, transcript and last verified pair; stop queue. Reconcile before technical recovery; no blind solve or DPM retry |
| Advancement | Controller advances only after horizon, settings, saved/reopened pair, histories, nine-injection accounting and aggregate checks pass |
| Completion evidence | Native manifests, checkpoints/hashes, exact input identities, residual transcripts, report histories/final-500 summary, DPM fates/timing and efficiency comparison |
| Claim limit | Historical reconstruction and fixed-horizon comparison. Neither the incomplete-particle assumption nor N1500 establishes carrier convergence, mesh independence, validation or superiority |

| Historical case | Enthalpy (kJ/kg) | Steam (kg/s) | Liquid (kg/s) | Face-normal injection speed (m/s) | Injections |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 | 1440 | 64.85 | 132.76 | 21.591272 | 9 |
| 3 | 1520 | 72.77 | 124.84 | 24.228170 | 9 |
| 5 | 1680 | 88.61 | 109.00 | 29.501968 | 9 |
| 6 | 1760 | 96.52 | 101.09 | 32.135537 | 9 |

| Source / verification | Evidence or limit |
| --- | --- |
| Historical case-specific source | [Candidate index](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-candidates/candidate-index.json); original source bytes retained under its immutable `raw/` folder |
| Case-specific parity | All nine pre-DPM, post-DPM and flow-manifest injection readbacks agree; inlet readbacks agree; injection mass sums equal each case's liquid flow |
| Current API translation | Historical `dpm` → `discrete_phase`; inlet `discrete_phase_bc_type` → `bc_type`; serialized injection frames checked as global |
| Reconstructed parent physics | [Settings audit](replication1600-settings-audit.md); [source recovery](replication1600-source-recovery.md) |
| Code review | [Review receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/code-review.json); compiled source identities and affected command path |
| Status | All five enthalpies complete; paired/settings/history/DPM evidence verified; final controller exited; owned Fluent idle |
| Queue supervision | One native writer; [passive probe](../../../PyAnsys/scripts/setup/probe_phase10_native_receipts.py) reads batch/current-case manifests; do not issue OS commands through active Fluent |
| Access limit | Independent Windows process/file access is unavailable if Fluent/VPN is unreachable; native worker can continue while VPN is disconnected |
| Schedule tools | `automation_update` unavailable in this tool session. Schedule prompt/pause readback cannot be changed here; manual update is required if the saved prompt must change. No schedule change claimed |

The previous 1600 kJ/kg carrier and both DPM tests stay preserved. This explicit selection replaces the earlier conditional-follow-up hold. Report the assumed-capture efficiency alongside escaped, trapped and incomplete mass, and preserve carrier adequacy evidence separately.

| Native execution / analysis | Path |
| --- | --- |
| Native batch | `C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication-enthalpy-M04-86f85b3d` |
| Launch and smoke | [Launch receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/sweep-launch.json); [startup verification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/startup-verification.json) |
| Terminal retrieval | `PyAnsys/scripts/inspection/fetch_phase10_replication_enthalpies.py`; run only when the batch is terminal and live endpoint is idle |
| Comparison analysis | `PyAnsys/scripts/analysis/analyze_phase10_replication_enthalpies.py`; produce efficiency CSV and Matplotlib comparison after retrieval |

| External status block | Required action |
| --- | --- |
| Fluent RPC timeout with reachable TCP; no independent Windows process/file route | Human confirms Fluent is still solving or tracking. Keep the existing controller; exact case, iteration and completed outputs remain unverified. No further manual action required now |

| Report recovery | Evidence |
| --- | --- |
| Single-fate Net omission | [Completed results and repair](replication-enthalpy-results.md); zero repeated carrier/DPM updates |
| Remaining contract | Only1760, freshN1500 and one DPM update; prior4500updates and3tracks retained. [Remaining job](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/remaining-job-spec.json) |

| Final-case execution | Current proof |
| --- | --- |
| 1760 controller40060 | N1500 and DPM complete; native artifacts rehashed, strict reopen/settings/report/history proof verified; controller exited |
| Current launch | [Remainder receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication-enthalpy-M04/remainder-launch.json) |
| Completion follow-up | Use fetcher with `--continue-reconciled`, then analyzer; update final Project comparison and request schedule pause only with successful native automation readback |

| Completion | Evidence / action |
| --- | --- |
| Five-case set | [Completed comparison](replication-enthalpy-results.md); no further run selected |
| Schedule |automation_update unavailable; pause Phase10 manually if still enabled. No native pause readback or pause claim |
