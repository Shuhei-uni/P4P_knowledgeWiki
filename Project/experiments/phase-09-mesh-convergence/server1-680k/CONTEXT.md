# Phase 9 — Server 1 / 680k EWF continuation

| Contract | Selected scope |
| --- | --- |
| Authority | Shuhei, 9 October 2026: full Server 1 authority; apply EWF Plan v1 and run the 680k mesh only |
| Scientific basis | [EWF Plan v1](../ewf-plan-v1.md), adapted from the 342k pilot to the selected 680k parent |
| Mesh | 679,970 cells; no other mesh selected in this lane |
| Parent | Selected initial bulk-development case/data at N9080; case SHA-256 `3ed60ccb6d501be2c9a84ac22f82c32ad7b754015e78aa77e94c1c9e28c3138e`; data SHA-256 `1dc3014784e581ca8a54d60cd176b48cbc77df9dfdbdc4b70cfc597216ea1c1f` |
| Inherited film age | 0.750 ms; preserve saved bulk and main-wall film fields |
| Target | Finish the current 1 µs section at N77580 / 92.5 ms; next 10,000 updates at 2.5 µs, then retain 5 µs. A verified frozen-bulk endpoint at N103080 / 195 ms is sufficient. Bulk reactivation to N104080 / 200 ms is an optional bonus sensitivity stage. |
| Session | Server 1 only; preserve any valuable loaded endpoint before replacement; leave Fluent open |
| Other lanes | Server 3, Server 4 and Server 5 records retain their own scope and state |
| Settings and run | [Setup](setup.md) |
| Evidence and status | [Results](results.md) |
| Claim limit | Completion at 195 ms does not establish steady film, mesh independence, whole-separator closure or physical validation. Failure of the optional bulk-active bonus does not invalidate a healthy frozen-bulk endpoint. |

| Continuation instruction | Effect |
| --- | --- |
| Human: “just keep running”, 9 October 2026 | Continue the 680k schedule with the film-ledger gap recorded as a diagnostic. The gap is not evidence of closure. Keep native time, checkpoint, finite-field, Courant, and fatal-error checks. |

| Human: “no just continue from N18580”, 10 October 2026 | Continue from preserved N18580 / 33.5 ms. Retain the completed block’s Courant warning; keep the 0.1 ceiling for future blocks. The proposed N13580 rollback is superseded. |
| Human: “no do 1us for 3000 iterations”, 10 October 2026 | One 1 µs, 3,000-update command from N18580 to N21580 / 36.5 ms. Preserve the interrupted 2.5 µs partial state separately, restore N18580, keep bulk frozen, and stop the controller after saved/reopened endpoint verification. |
| Human: resume; use plan Courant limit or 0.8 if absent, 11 October 2026 | Plan had no Courant ceiling. Select 0.8 for Server 1 / 680k; restart the read-only watcher and apply the reviewed controller change at a saved, idle endpoint. Retain historical warning records. |
| Human: verify automatic next command without influencing current run, 11 October 2026 | Separate server-local queue waits for verified N24580 / 39.5 ms completion, then sends one 3,000-update command at 1 µs to N27580 / 42.5 ms. Keep the active section and controller unchanged; Codex wake-up is not required. |
| Human: complete EWF Plan v1 and keep running until 200 ms, 11 October 2026 | Continue from verified N27580 / 42.5 ms at1 µs; send all remaining sections automatically. Freeze bulk through195 ms; reactivate all bulk equations for195–200 ms. Retain0.8 Courant guard and diagnostic-only ledger policy; preserve final paired save/reopen evidence. |
| Human: remove all limit checks; run to final film time unless error, 12 October 2026 | Supersedes the Courant and film-ledger acceptance gates. Continue to 200 ms at 1 µs. Record numerical diagnostics; retain solver/command, finite-value, native-time, configuration and artifact error checks. The active native command is preserved; a server-local transition resumes automatically if the old controller stops on a retired gate. |
| Human: next run at 2.5 µs, then step up to 5 µs | Preserve the current native command. At its saved N77580 / 92.5 ms boundary, replace only the Python command owner and send 10,000 updates at 2.5 µs. Retain 5 µs afterward, the 20 µs DPM cadence, the final 195–200 ms bulk reactivation, and diagnostic-only numerical limits. Final target becomes N104080 / 200 ms. |
