# Stage 2 — absorber from start: failed run

| Evidence | Observation |
| --- | --- |
| Outcome | Fluent process shutdown before N1000; no completed 1,000-iteration block |
| Exact failure iteration | Unavailable after process shutdown |
| Local autosaves | Paired case/data at N100, N200, N300, N400, N500 and N600 |
| Recovered endpoint | N600 pair hashes recorded; native N600 confirmed after save/reopen; zero diagnostic solve updates |
| Run logs | Recovered host run manifest, runner log and immutable native transcript |
| Interpretation | Absorber from the full-feed start did not complete this configuration; no stability benefit or universal OFF-impossibility claim |
| Following trial | Human-confirmed [slow inlet and delayed absorber activation](../slow-enable3000/setup.md) |

[Recovery receipt](../../../../../PyAnsys/output/phase8-stage2/20261007/absorber3000/shutdown-recovery.json) records the N600 pair and hashes. [Setup](setup.md) retains the failed trial definition.
