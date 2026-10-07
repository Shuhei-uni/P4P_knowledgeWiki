# Server 4 — current preparation evidence

| Question | Evidence-backed status |
| --- | --- |
| Is Server 4 reachable? | Yes: TCP connection reached the configured Fluent endpoint |
| Can this chat inspect the solver? | Yes: credentials corrected; native inspection proved empty idle Fluent 2025 R2 |
| Was a case loaded or solve launched? | Yes: verified 2.6M child; smoke accepted; low-feed hold completed at verified N3580; ramp continuation launched |
| Is the first accepted batch verified? | Yes: N1580→N1600; paired reopen verified; all 34 report histories cover N1581–N1600 |
| Were input hash, native cells and child settings verified on Server 4? | Verified: mesh SHA-256 matches input audit; native child has 2,596,657 cells; dry-film N1580 pair passes fields, settings, methods, bulk contract and native clock reopen checks |
| Is Server 3 affected? | No connection or control was submitted |
| Is the implementation ready for review? | Separate runner and watcher are running; native source, mesh transfer, child and first smoke batch checks pass |
| Supervision | Separate watcher checks controller receipts and live transcript every 30 seconds; bounded health every 5 minutes; actionable events wake this chat |

| Evidence | Location |
| --- | --- |
| Authentication block | [Machine receipt](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/connection-block.json) |
| Initial attach failure | [Inspection log](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/initial-inspection.log) |
| Watcher status | [Live supervision](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/continuous-supervision.json) |

| Required input | Next action |
| --- | --- |
| Credentials corrected; no current human input needed | Continue the ramp from N3580 to N5580, then 1000-update full-feed holds |
| Claim limit | No simulation result or preparation maturity claim is supported yet |

| Prepared child proof | Value |
| --- | --- |
| Mesh SHA-256 | `5dbcfa1e0375ce654ae985cbbdb02a86308e837be2cb2eecedaaf14260f30714` |
| Native outlet height | 6.261000633 m; already metre scale in Fluent; no additional scale operation |
| Prepared parent coordinate | N1580; zero native film elapsed time |
| Report count | 34; smoke history coverage PASS |
| Reopen treatment | Initial face-flux diagnostics changed; other required readback passed; second paired save/reopen reproduced required readback |
| Machine receipt | [Prepared child](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/2_6M-prepared-audited.json) |

| First accepted batch | Verified value |
| --- | --- |
| Native coordinate | N1580→N1600; exact terminal iteration proved |
| Film evidence | 20 finite consecutive rows; fixed 1e-7 s step; end time 2e-6 s |
| Peak film Courant | 8.970086e-7 |
| Paired checkpoint | Local case/data saved, hashed and reopen verified; fields/setup/methods/bulk/film-clock checks PASS |
| Instrumentation | All 34 histories cover N1581–N1600 |
| Startup warning | Pressure-outlet reversed-flow warnings retained; no fatal numerical error in the smoke transcript |
| DPM | Scheduled natural DPM step within the smoke solve; no separate tracking command |
| Low-feed hold | N1600→N3580 completed and recovered after laptop RPC timeout |
| Preparation completion | Pending ramp and full-feed stability windows |
| Machine receipt | [First accepted batch](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/first-accepted-batch.json) |

| Low-feed hold recovery | Verified outcome |
| --- | --- |
| Controller failure | Laptop gRPC keepalive watchdog timeout after pause/resume; original error retained in campaign history |
| Native endpoint | N3580, idle; all 2000 low-feed updates complete; no repeat solve required |
| Film evidence | 1980 complete finite rows in recovered hold transcript; consecutive fixed 1e-7 s steps; terminal film time 0.200 ms |
| Report coverage | All 34 histories cover N1581–N3580 with finite values |
| Pair proof | Preserved N3580 case/data hashes match; fields/setup/methods/bulk settings/clock pass reopen |
| Recovery evidence | [Verified recovery](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/low-hold-recovery-1791405772079458000/recovery-terminal.json) |
| Continuation | Server 4 controller relaunched from N3580; approved 10-update ramp spacing; watcher active |
