# Execution status

| Item | Evidence |
| --- | --- |
| Current status | Floating-point exception at native N9295; 1215 iteration-counter increments from N8080; last printed residual row N9294 |
| Submission evidence | [Stream observation](../../../../PyAnsys/output/rsm-server3-60k/20261009/submission-observation.json) |
| Machine receipt | [Run manifest](../../../../PyAnsys/output/rsm-server3-60k/20261009/run-manifest.json) |
| Applied model | Linear Pressure-Strain RSM; wall reflection on; standard wall functions retained |
| Active equations | Drift, Reynolds stresses, flow, k/epsilon and multiphase |
| Requested horizon | 2000 new iterations from N8080 |
| Scientific interpretation | k/epsilon residual escalation precedes large Reynolds-stress and momentum escalation; continuity follows. Root cause remains unresolved. |
| Numerical qualification | Not established by setup or submission |
| RSM pairs | RSM N8080 start and failed N9295 endpoint deleted by human instruction; [reset receipt](../../../../PyAnsys/output/rsm-server3-60k/20261009/reset-receipt.json) owns deletion and restored-state evidence |
| Restored start | Original Phase 9 RNG k-epsilon N8080 parent; Server 3 idle; no new iterations |

| Native iteration | Continuity | Largest momentum residual | k | epsilon | Largest Reynolds-stress residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9283 | 1.57e-3 | 4.61e-5 | 3.53e-3 | 5.63e-3 | 322 |
| 9284 | 1.59e-3 | 4.61e-5 | 4.97e-2 | 1.47e-2 | 322 |
| 9286 | 1.62e-3 | 4.83e-5 | 283 | 6139 | 987 |
| 9287 | 1.64e-3 | 1.95e-3 | 11.5 | 4.64 | 2.65e6 |
| 9288 | 1.26e-2 | 1.55e-2 | 16.6 | 54.0 | 3.66e8 |

| Evidence and limit | Detail |
| --- | --- |
| Source | [Native stream](../../../../PyAnsys/output/rsm-server3-60k/20261009/client-transcript.txt), [extracted onset](../../../../PyAnsys/output/rsm-server3-60k/20261009/failure-onset.json) |
| Film coupling | Film Courant rises from 1.77e-4 at N9284 to 0.101 at N9285; 1.50 at N9287 |
| Terminal solver messages | First explicit AMG divergence messages are k and epsilon, followed by volume-fraction divergence and floating-point exception |
| Residual scales | Compare changes within each residual history; magnitudes across different equations have different scaling |
| Inference limit | Printed iterations resolve the sequence of observed changes, not the initiating cell or within-iteration causal order |
