# 997k — EWF execution evidence

| Observation | Evidence / limit |
| --- | --- |
| Status | 997k partial endpoint preserved at N10642; Server 6 reassigned by the human to native poster graphics; timestep repair remains incomplete |
| Mesh | Selected 997,604-cell N8080 case/data; copied parent hashes match |
| Prepared child | [Saved/reopened settings receipt](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/997k-ewf-settings-current.json) |
| Retained fields | Original bulk report fields and upper film facets preserved; inherited film age 0.650 ms |
| First accepted film update | 0.6501 ms total age; 0.1 µs step; maximum Courant 0.0003793612 |
| First inner film solve | Seven subiterations; h/u/v residuals 4.058620e-11 / 1.226099e-6 / 1.504258e-6 |
| Startup proof | [Transcript observation](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/startup-observation.json); native transcript contains `/solve/iterate 1500` |
| Latest completed-stage checkpoint | N10580 / 0.900 ms; all bulk equations frozen; case/data SHA256 verified by host controller |
| Preserved partial endpoint | N10642 / 0.906200 ms; local case/data hashes verified and native reports checked after reopening. [Receipt](../../../../PyAnsys/output/poster-N45606-native/20261010/previous-endpoint.json) |
| Completed stages | 1,500 bulk-active updates and 1,000 frozen updates; peak Courant 0.000874006 and 0.001407046 |
| Frozen bulk | Report fields unchanged through the transition |
| Applied drain proof | [Matched OFF/ON probe](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/matched-drain-probe.json): 100 updates per arm at 0.1 µs; identical starting pair; upper-film endpoint reports identical; production N10580 / 0.900 ms restored |
| Matched drain ledger | OFF-minus-ON inventory change 2.58933575e-10 kg; integrated removal 2.59035021e-10 kg; 0.039163% difference |
| Production drain report | Integrated named removal 2.024787e-9 kg; a positive rate alone does not establish applied removal |
| Production ledger gap | 32.5426% using current net-secondary/DPM accounting; attribution unresolved, no mass-closure claim |
| Stop evidence | [Host run manifest](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/host-run-manifest.json) and [drain check](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/host-frozen-transition-drain-proof.json) |
| Supervision at reassignment | No owning host controller or local Server 6 watcher active; preflight recorded in the preservation receipt |
| Staged target | [Schedule](setup.md): N50900 / 200 ms; 42,820 new updates |
| Execution location | [Host launch receipt](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261009/host-launch.json); Windows-host controller; laptop not required for execution |
| Recovery storage | Paired local autosaves every 1,000 updates; paired checkpoints and transcript at each stage |
| Continuation attempt | New report files resolved the restart prompt. The native stage accepted at least 19 updates, but at 0.1 µs instead of requested 2.5 µs. These are recorded diagnostic updates; the faster-step stage is not accepted. |
| Native control repair | Apply the version-252 EWF `solution-options` callback after setting parameters. Working code and an own-case save/reopen smoke are staged; active host code unchanged. |
| Current access | Idle Fluent reached and N10642 saved/reopened before loading N45606. No Fluent exit or process termination; [native poster preparation](../../../../PyAnsys/output/poster-N45606-native/20261010/prepared.json) |
| Continuation limit | Native callback repair and the later 200 ms stages remain incomplete; current server assignment is poster graphics |
| Claim limit | Verified progression to 0.900 ms; no completed 200 ms endpoint, production mass closure or steady-film claim |
