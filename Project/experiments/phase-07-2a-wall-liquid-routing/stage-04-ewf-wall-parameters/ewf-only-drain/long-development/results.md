# Stage 4 — Long native EWF development

| Status / question | Current evidence |
| --- | --- |
| Run status | **RUNNING — native report histories advanced from N49898 to N50152 during the check** |
| Status check | 2026-10-07T20:57:46.432613+13:00; 8,669 / 200,000 updates complete (4.33%); last native block guard passed at +8,000 |
| Recorded peak thickness / Courant | 0.002700960 m / 0.1424277 through N50152; both complete histories consecutive; no threshold reached |
| Inspection limitation | Detailed main-interface requests timed out; direct Cortex status and report-file scan confirmed further progress; checkpoint list / full transcript not inspected |
| Parent | Verified drain-ON N41483 / 0.3881843386354626 s |
| Planned horizon | +200,000 updates at 15 microseconds; +3.000 s film time; target N241483 |
| Physical setup | Full selected upper-film mechanisms ON; direct drain ON; Flow Momentum Coupling OFF; bulk frozen |
| Stationary film | Pending long-run analysis; previous 15 ms screen still grew at 77.723 kg/s in its last half |
| Thickness limit | Any native sample ≥0.3 m marks UNREALISTIC; native block guard preserves the rejected pair and stops further blocks |
| Laptop connection | Not required; native journal, guards, checkpoint writes and final save belong to Fluent |
| Completion evidence | Pending native final pair, actual film clock, all report histories and numerical/film-ledger checks |
| Interpretation limit | Film stationarity under held bulk forcing; assumed collector capacity; no fully coupled separator claim |

| Evidence / next action | Record |
| --- | --- |
| Exact design / decision tests | [Setup](setup.md) |
| Latest status evidence | [Native inspection](../../../../../../PyAnsys/output/phase72a-stage4-ewf-long-native/20261007/inspection/latest-status.json) |
| Native job owner | [Manifest](../../../../../../PyAnsys/output/phase72a-stage4-ewf-long-native/20261007/run-manifest.json) |
| Source proof / short production test | [Completed direct-drain result](../results.md) |
| Required analysis | Inventory/throughput/ledger figures over the full horizon and final three 0.25 s windows |
