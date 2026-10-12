# Server 4 — final initial bulk development

| Selection | Evidence and interpretation |
| --- | --- |
| Human endpoint decision | Use the current N8580 state as final initial bulk development despite remaining unsteady behaviour. No further solve. |
| Mesh | 2_6M; 2,596,657 cells; verified mesh SHA-256 `5dbcfa1e0375ce654ae985cbbdb02a86308e837be2cb2eecedaaf14260f30714` |
| Starting state | Original dry-film A parent at N1580; native Replace Mesh with preserved bulk fields |
| Low-feed development | 2000 updates at 25% feed, through N3580; one accepted 20-update smoke check |
| Ramp | 2000 updates through N5580, with 10-update inlet-change spacing |
| Full-feed development | 3000 updates through N8580; liquid 116.92 kg/s and vapour 80.69 kg/s |
| Original acceptance | The 4000-update minimum was not reached. This endpoint is a user-selected initial bulk state; the earlier preparation acceptance must not be claimed. |
| Bulk equations | Drift, flow, ke and mp remain active; approved 08b contract and provisional Stage 4 EWF retained |
| Final batch | N7580–N8580: 1000 complete finite film-clock rows, fixed 1e-7 s step, no fatal numerical error identified |
| Report histories | All 34 histories cover N1581–N8580 with finite values |
| Final film clock | 0.700 ms; accepted model time, not bulk physical maturity |
| Preservation | Local pair hashed and reopened: fields, setup, methods, bulk settings and film clock pass. OneDrive case/data copy hashes match; cloud upload not independently verified. |
| Solver control | Server 4 idle; laptop controller retired; watcher stopped; Fluent preserved |
| Claim limit | No steady-state, steady-film, final mesh-convergence, mass-closure or physical-validation claim |

| Evidence | Location |
| --- | --- |
| Final preservation receipt | [Machine receipt](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/final-initial-bulk.json) |
| Run history and accepted checkpoints | [Mesh run receipt](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/2_6M-run.json) |
| Startup proof | [Prepared child](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/2_6M-prepared-audited.json) |
| First smoke proof | [First accepted batch](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/first-accepted-batch.json) |

| Final preservation | Verified value |
| --- | --- |
| OneDrive folder on Server 4 | `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase9\Server4\2_6M\final-initial-bulk-N8580-1791516489726781000` |
| Peak final-batch film Courant | 0.0002645622 |
| Final window pressure-drop range / absolute mean | 2.9976% |
| Final window bulk-mass range / mean | 7.5471% |
| Final window outlet-liquid range / full liquid feed | 0.001770% |

| EWF settings child | Verified result |
| --- | --- |
| Settings application | Applied and paired save/reopen verified; no solve submitted |
| Drain | `wall:004` EWF enabled; direct mass source and XYZ momentum sources enabled with capture time 1.5 ms |
| Film preservation | Main-wall mass, thickness and XYZ film velocity facets preserved exactly; N8580 and 0.700 ms clock unchanged |
| State | All bulk equations active; 0.1 µs fixed step; no functional drain-removal claim from this settings-only operation |
| Evidence | [Settings receipt](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/ewf-settings-current.json) |

| Current EWF development | Verified result |
| --- | --- |
| Bulk-active adjustment | 2500 updates completed through N11080 / 0.950 ms; paired reopen verified |
| Frozen transition | 1000 updates completed through N12080 / 1.050 ms; all four bulk groups frozen; fixed 0.1 µs; peak Courant 0.00138383 |
| Controller recovery | Removed invalid requirement for bulk residual rows during frozen solves. Native N12080 and all 1000 film-clock rows verified; pair saved/hashed/reopened; no repeat solve |
| Current command | N12080→N13080, 1000 frozen updates at fixed 2.5 µs; first accepted film age 1.0525 ms, Courant 0.03484939 |
| Evidence | [Recovery and resumed solve](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/frozen-stage-recovery-current.json) |
