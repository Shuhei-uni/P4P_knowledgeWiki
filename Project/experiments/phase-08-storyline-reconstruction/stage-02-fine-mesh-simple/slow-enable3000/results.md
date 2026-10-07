# Stage 2 — long low-feed hold: Cortex shutdown

| Evidence | Observation |
| --- | --- |
| Outcome | Shutdown before absorber activation at N1000 |
| Last printed solve row | N350; exact shutdown iteration unavailable |
| Native error | eof inside list; Cortex received a fatal signal; critical code section error |
| Autosaves | Paired N100, N200 and N300 |
| Recovery | N300 hashes recorded and pair reopened at native N300; zero diagnostic solves |
| Report histories | All 17 active carrier reports recovered; absorber-source report inactive during OFF hold |
| Scientific limit | Delayed absorber activation was not reached; this run does not test its effect |
| Failure interpretation | Cortex/session error observed; numerical divergence and root cause not established |
| Next trial | [200 OFF, 500 low ON, stepped ramp, 1,000 full](../step-enable2200/setup.md) |

[Recovery receipt](../../../../../PyAnsys/output/phase8-stage2/20261007/slow-enable3000/second-shutdown-recovery.json) records the saved pair and hashes. Native log and report histories remain in PyAnsys.
