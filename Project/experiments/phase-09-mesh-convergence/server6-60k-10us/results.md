# Server 6 — 60k fixed 10 µs run

| Evidence | Result |
| --- | --- |
| Outcome | Numerical failure; 200 ms target not reached |
| Native failure | Floating-point exception after k and epsilon AMG divergence; live native iteration N8128 |
| Printed film endpoint | 1.130 ms; native 10 µs step; film Courant reached infinity |
| Verified healthy checkpoint | N8081 / 0.660 ms smoke pair; restored and idle |
| Bulk mode | All four bulk equation groups active throughout; human confirmed |
| Parent identity | Selected N8080 pair; both copied hashes match recorded source |
| Changes | Maximum EWF timestep only; physics inherited |
| Preserved evidence | Failed N8128 case/data, native transcript, failed controller manifest, verified smoke pair |
| Clock discrepancy | Failed RP solution-state still reported 0.660 ms; transcript reached 1.130 ms. Failed clock is not accepted progress |
| Interpretation | One successful update did not establish sustained stability at 10 µs |
| Cause limit | Film and bulk divergence observed; causal mechanism not isolated |
| Next action | No unchanged retry; further continuation needs a revised timestep or setup |
| Recovery proof | [Recovery receipt](../../../../PyAnsys/output/phase9-server6-60k-10us/20261013/recovery-receipt.json) |
| Failure evidence | [Native transcript](../../../../PyAnsys/output/phase9-server6-60k-10us/20261013/failed-native-transcript.trn); [analysis](../../../../PyAnsys/output/phase9-server6-60k-10us/20261013/failure-analysis.json) |
