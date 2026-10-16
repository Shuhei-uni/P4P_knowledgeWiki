# Server 6 — 60k fixed 5 µs run

| Item | Verified result |
| --- | --- |
| Outcome | Numerical failure; 200 ms not reached |
| Failed endpoint | N8148 / 0.995 ms film time |
| Failure | Epsilon AMG divergence followed by floating-point exception |
| Film diagnostic | Last printed Courant 5.658762 × 10¹³⁷ |
| Restored state | Verified N8082 / 0.665 ms 5 µs smoke pair; idle |
| Preserved evidence | Failed N8148 pair, native transcript, original controller error, smoke pair |
| Bulk and settings | All bulk equations active; other parameters retained |
| 10 µs trial | Failed at N8128; last printed film time 1.130 ms |
| Interpretation | Both fixed-step trials failed with active bulk; smaller step did not sustain the requested run |
| Cause limit | Film and bulk divergence observed; causal mechanism not isolated |
| Next action | No unchanged solve retry or unselected setting change |
| Recovery | [Receipt](../../../../PyAnsys/output/phase9-server6-60k-5us/20261013/recovery-receipt.json) |
| Failure evidence | [Native transcript](../../../../PyAnsys/output/phase9-server6-60k-5us/20261013/failed-native-transcript.trn); [analysis](../../../../PyAnsys/output/phase9-server6-60k-5us/20261013/failure-analysis.json) |
