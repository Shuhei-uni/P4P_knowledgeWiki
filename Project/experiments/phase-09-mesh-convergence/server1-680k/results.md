# Server 1 / 680k — execution evidence

| Observation | Evidence / limit |
| --- | --- |
| Initial Server 1 inspection | Fluent 2025 R2 reachable; no mesh loaded |
| Parent transfer | Both selected N9080 file hashes verified after server-local copy |
| Parent load | N9080 readback; approved bulk settings and full feed checked against the archived 680k checkpoint |
| Lower-film allocation | New lower-wall storage allocated; saved production data restored; original upper-film mass, thickness and XYZ velocity facets preserved exactly |
| Saved-child verification | N9080 and 0.750 ms preserved after save/reopen; important settings/readback and original main-wall film facets match; all bulk equations active. [Machine receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/680k-ewf-settings-current.json) |
| Initial schedule validation | Original 5 µs schedule totalled 42,800 updates to N51880. Resumed bounded command adds 3,000 updates at 1 µs from N21580 to N24580 / 39.5 ms; exact time/count arithmetic, one-command journal, DPM cadence and Python compilation passed. [Current command review](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/resume-N21580-courant0p8-review.json) |
| Controller runtime | Isolated Server 1 Python 3.12.10 environment; explicit interpreter with `-E`; required modules and exact deployed runner import verified |
| Connection recovery | Prior pre-solve controller preserved and archived; N9080 / idle verified; only owned Python controller processes stopped. Verified v252 service route used; Fluent process retained |
| Run status | **COMPLETE_VERIFIED: N104080 / 200 ms.** Both native controller and server-side supervisor report verified completion. Final 1,000 updates at 5 µs advanced from 195 to 200 ms with all bulk equations active. [Completion evidence](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/status-latest.json) |
| Controller guard | Numerical acceptance limits were disabled by human instruction. Preserve all numerical warnings. Final bulk-active window peak film Courant **4.918978**; reopened endpoint Courant **0.5113200**. Completion is an execution result, not a convergence qualification. |
| Execution location | Controller and checkpoint/transcript writes run on Server 1; laptop not required for the native schedule |
| Next decision | No further native commands queued. Preserve the completed endpoint and leave Fluent open. Numerical/physical interpretation remains separate from execution completion. |
| Verification boundary | Exact 200 ms / N104080 endpoint saved, hashed and reopened; reopened film clock 0.2000000000001696 s, retained 5 µs step, and all bulk equations active. Final reopen record references the same paired endpoint as the completed manifest. |
| Evidence retrieval limit | Final pair copied into the Server 1 computer's OneDrive folder; both local-copy SHA-256 values match the selected server-local pair. Independent cloud upload is not verified. Final manifest and supervisor records retrieved through Fluent Scheme; transcript watcher is reconnecting. |
| Scientific limit | No steady-film, whole-system mass closure, mesh-independence or separator-performance claim |

| Saved comparison pair | Film age | Native coordinate | Bulk equations | Provenance |
| --- | ---: | ---: | --- | --- |
| Freeze onset | 0.900 ms | N10580 | All off | Reconstructed from the exact original 0.900 ms pair by switching only the bulk equation flags off; no iterations. Field reports unchanged; saved pair reopened. |
| End of frozen interval | 195 ms | N103080 | All off | Original endpoint before bulk reactivation; selected copy is byte-identical to the recorded pair and was reopened. |
| Completed run | 200 ms | N104080 | All active | Current 200 ms state restored after export; fields, setup, methods and film controls match the pre-export state. |

Both selected comparison pairs are beside the final pair in the Server 1 OneDrive folder. Case and data SHA-256 values match their server-local sources. Exact paths and verification: [selected checkpoint record](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/selected-pairs-export-latest.json).

| Completed stage | New updates | Native endpoint | Total film age | Peak film Courant |
| --- | ---: | ---: | ---: | ---: |
| Bulk adjustment | 1,500 | N10580 | 0.900 ms | 0.000835510 |
| Frozen transition | 1,000 | N11580 | 1.000 ms | 0.001042868 |
| First faster step | 1,000 | N12580 | 3.500 ms | 0.04320952 |
| Second faster step; save recovered | 1,000 | N13580 | 8.500 ms | 0.05557127 |

| Frozen-stage balance observation | Value / interpretation |
| --- | --- |
| Film inventory | 0.008493686 → 0.010349348 kg |
| Integrated secondary + DPM source | 0.0019960725 kg |
| Direct lower-film removal | 2.472526e-9 kg; positive but very small |
| Bulk report preservation | PASS; all four bulk equations frozen |
| Net-secondary accounting gap | 0.000277356 kg / 13.8951%; limit 1% |
| Gross-source alternative | Also fails; changing only separated-mass convention does not explain the discrepancy |
| Failure classification | Source-consistency gate failure after completed solve; cause unresolved; no native fatal event detected in recent output |

| Fixed-step repair | Evidence / result |
| --- | --- |
| Detected error | Changing RP `timestep-max` alone retained the compiled 0.1 µs step. The partial attempt was interrupted and saved; N11580 was restored. |
| Verified route | Retain model controls, then call native EWF `solution-options` with current defaults. This applies the fixed step without initializing film storage. |
| 2.5 µs smoke | Accepted timestep 2.50e-6 s; peak Courant 0.0262168. [Receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/film-step-tui-smoke.json) |
| 5 µs smoke | Accepted timestep 5.00e-6 s; peak Courant 0.0529848. Only intended step/cadence parameters changed. [Receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/film-step-tui-5us-smoke.json) |
| Production origin | Both smoke updates preserved outside the production schedule. Restore the exact N11580 pair before resumed production. |

| Monitor recovery | Evidence / result |
| --- | --- |
| Cause | The preserved monitor files contained rows above restored N11580. Fluent requested a file reset before iteration. The rejected restart did not advance the production coordinate. |
| Correction | Keep prior histories and give every report file a unique resume folder. New ledger windows use those fresh histories. |

| Resumed monitoring | Evidence / limit |
| --- | --- |
| Completed 2.5 µs balance | Net-secondary ledger discrepancy 0.537664%; direct-drain probe checks PASS for this bounded frozen window. Film inventory 0.0569144 kg. This does not qualify whole-system closure or a steady film. |
| Current 5 µs updates | Transcript confirms accepted 5 µs steps. Some updates reach all 100 subiterations with large native h/u/v residuals. Record this numerical warning; no converged-update claim. |
| Laptop observer | Raw read-only transcript subscription avoids the busy attachment handshake. Prior transcript preserved; new stream recorded in the observer receipt. |

| N13580 recovery | Evidence / limit |
| --- | --- |
| Interruption cause | An agent status probe queried an undefined RP variable during the active command. Native transcript contains that error; the solve reached all 1,000 accepted updates, but the journal stopped before its paired save. The faulty probe is removed. |
| Preserved endpoint | N13580 / 8.5 ms saved manually and hashed. All frozen bulk fields checked through native histories or paired-data comparison. No solve was repeated. [Recovery receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/completed-save-recovery.json) |
| Completed-window balance | Film-ledger discrepancy 0.24168021115992505%; bounded drain-probe checks PASS. This does not remove the film subiteration warning or establish whole-system closure. |
| Continuation | Exact completed schedule prefix verified; next growth block is 5,000 updates at 5 µs. [Code and deployment review](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/resume-N13580-code-review.json) |


| N18580 Courant stop and continuation | Evidence / limit |
| --- | --- |
| Completed native work | All 5,000 updates at 5 µs completed once; N18580 / 33.5 ms case/data saved and hashes verified. |
| Stop trigger | Peak film Courant 0.218784 exceeded the retained 0.1 ceiling. Endpoint Courant was about 0.0538; the guard uses the maximum over the whole block. |
| Balance | Bounded film-ledger discrepancy 0.23849555%; drain-probe checks PASS. This was not the stop cause. |
| Human-selected endpoint | “no just continue from N18580”. The started N13580 restore completed, then the exact N18580 pair was reloaded. Readback confirmed N18580 / 33.5 ms, full feed, retained bulk contract, drainage hooks, and all bulk equations frozen. No solve was submitted from N13580. |
| Preserved warning | Retain the Courant exceedance and the 100-subiteration residual warning. The retained film age is 33.5 ms; no completed development is excluded under this instruction. |
| New controlled delta | Human selected 1 µs for 3,000 updates: DPM every 20 iterations and direct-drain refresh span 1 µs. Other model controls retained. |
| Acceptance policy | Peak Courant ≤0.1 was retained for the first 1 µs block. Human raised the subsequent-block ceiling to 0.8 on 11 October 2026. Continuing from N18580 does not turn the earlier block into a numerically qualified result. |

| Superseded 2.5 µs command | Evidence / limit |
| --- | --- |
| Interruption | Ten native updates completed, to N18590 / 33.525 ms, before the human-selected 1 µs command. Only owned Python controllers stopped; native Fluent calculation interrupted without exiting Fluent. |
| Preservation | Partial case/data saved and hashed separately. [Partial endpoint receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/superseded-2p5us-partial.json) |
| Selected origin | Reload exact saved N18580 / 33.5 ms before the 1 µs command; no extra partial development is counted in this command. |


| Completed 1 µs block and 11 October resume | Evidence / limit |
| --- | --- |
| Exact completed command | N18580 → N21580; 3,000 accepted 1 µs updates; film age 33.5 → 36.5 ms; paired checkpoint hashes and reopen checked by the server controller. |
| Peak film Courant | 0.01112552; passes the 0.1 ceiling used by that block. |
| Film ledger | 1.6248274172%; ledger-only warning retained under the human’s diagnostic-only policy. This block does not prove total-film closure. |
| Current policy | Peak Courant ≤0.8 for subsequent blocks; earlier exceedance at N18580 remains in the historical evidence. |
| Resume | Keep bulk frozen, 1 µs step, 1 µs drain refresh and DPM every 20 iterations. Submit one further 3,000-update command to N24580 / 39.5 ms; no repeated earlier solve or older checkpoint load. |
| Watcher | Laptop read-only transcript observer restarted; prior stream preserved. [Observer receipt](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/observer-resume.json) |


| Automatic next-command check | Evidence / result |
| --- | --- |
| Gap found | Current bounded controller stops at N24580; its job has Codex wake-up disabled. No next command was previously queued. |
| Correction | Separate Server 1 queue worker verified alive in WAITING_FOR_PARENT_VERIFIED, PID 69712. Deployed source SHA and exact parent job read back. [Verified deployment](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/next-command-queue-launch.json) |
| Next command | 3,000 updates at 1 µs from saved N24580 / 39.5 ms to N27580 / 42.5 ms, only after parent save/reopen and endpoint verification pass. |
| Isolation | Current solver settings, journal and controller source retained. Queue waiting path only reads server-local files; no Fluent attachment or solve call. |
| Wake-up | No Codex wake-up is needed for this next command. Queue runs on Server 1 and remains independent of the laptop watcher. |
| Checks | Offline gate tests reject failed, foreign and mismatched endpoints; current runner/verifier hashes guarded before child launch; separate queue lock and existing solver-writer lock prevent duplicate command ownership. |


| Latest saved endpoint | Evidence / limit |
| --- | --- |
| Automatic continuation | Queue sent the next 3,000-update command after N24580 passed completion verification. Queued controller returned 0; endpoint verifier passed. |
| Preserved endpoint | N27580 / 42.5 ms; fixed 1 µs; all bulk equations frozen and bulk report fields unchanged. |
| Peak film Courant | 0.01092497, below selected limit 0.8. |
| Film ledger discrepancy | 1.63358%; recorded as an authorized ledger-only warning, not a closure pass. |
| Current control state | Both sections complete; Fluent remains open; no further native command is queued. Laptop transcript observer remains active. |


| Continuation to 200 ms | Evidence / limit |
| --- | --- |
| Authority | Human explicitly selected completion of EWF Plan v1 to 200 ms; the single-next-command boundary is superseded. |
| Preserved origin | N27580 /42.5 ms paired checkpoint; retained 1 µs step, all frozen bulk equations and existing feed/models/drainage controls. |
| Reviewed repair | Clear the previous bounded-run flag and replace its42.5 ms target with200 ms. Do not repeat a step smoke check when the same1 µs step has already passed complete blocks. |
| Exact schedule | 15 commands of10,000 frozen updates, then2,500 frozen updates to195 ms; 5,000 bulk-active updates to200 ms. Final nativeN185080. |
| Automatic delivery | Server-local controller sends the next section after the preceding section passes its endpoint checks. Local paired autosaves and section transcripts remain active. |
| Completion boundary | Target not yet reached. Final paired save/reopen, bulk-active readback, hashes and selected shared pair remain required. |
