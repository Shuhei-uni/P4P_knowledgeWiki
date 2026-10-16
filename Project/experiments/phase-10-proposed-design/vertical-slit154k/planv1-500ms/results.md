# vertical-slit154k — Plan v1 results

| Check | Current evidence |
| --- | --- |
| Parent | N44661 / 150 ms; Mac OneDrive case/data hashes rechecked |
| Current state | Evidence access lost during bulk-scale adjustment. Last printed N45960 / approximately 150.0139 ms, without a new error in received output. Native control and transcript now unavailable; command outcome unconfirmed. Last verified pair N44691 / 150.0012 ms retained |
| Target | N187130 / 500 ms with the reviewed recovery schedule |
| Prior endpoint | Original 150 ms pair retained; no reinitialization of inherited fields |
| Machine owner | [Case receipts](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/vertical-slit154k/) |

| Build and startup | Verified evidence |
| --- | --- |
| Source | N44661 / 150 ms; both case/data hashes match selected OneDrive parent |
| Field preservation | Upper-film mass, height and XYZ velocity retained exactly after geometry-based face ordering; bulk liquid/vapour inventories retained before solve |
| New lower wall | wall:004 allocated at zero film, with direct mass/XYZ drain; no reinitialization of inherited bulk or upper-film data |
| Settings | Full verified Plan v1 parameter template; sequential original implicit EWF; 0.045 mm roughness; bulk active for initial adjustment |
| Prepared pair | Saved/reopened locally and shared to unique OneDrive prepared150ms-planv1 folder; source150ms pair unchanged |
| Smoke | 10 native updates at 0.1 µs; paired endpoint N44671 / 150.001 ms verified |
| First failed command | Original command stopped with FPE at N45047 / 150.0386 ms; failed pair saved and hashed |
| Current evidence access | [Bounded reconciliation](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/bulk-scale-evidence-loss-reconciliation.json); no settings or solve replay from this timeout |
| Bulk-scale retry | Scale factor 0.1 during bulk-active adjustment; same Plan v1 physics and 0.01 µs film step. Smoke N44691 / 150.0012 ms verified after paired reopen. [Startup receipt](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/bulk-scale-startup-verification.json) |
| Second failure | [Transcript and control reconciliation](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/second-failure-reconciliation.json); film-step reduction alone did not sustain bulk-active adjustment |
| Recovery startup | [Verified 0.01 µs smoke and host continuation](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/recovery-startup-verification.json) |
| Native proof | [Startup verification](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/startup-verification.json) |
| Recovery | Restore verified N44671 pair; remaining 1490 bulk updates at 0.01 µs, then frozen 1016 updates at 0.1 µs and main 2.5 µs growth. Physics and bulk-active adjustment count retained. This is recovery below the plan’s lowest prescribed step |
| Failure evidence | [Native reconciliation](../../../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/failure-reconciliation.json) |
| Drain proof | Pending the scheduled frozen 1016-update transition; positive direct-removal and held-bulk checks precede main growth |
| Angle queue | Same Server 5 worker loads angle only after verified/shared vertical 500 ms endpoint |
