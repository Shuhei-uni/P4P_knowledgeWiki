# Phase 9 — Mesh convergence preparation

| Contract | Current human direction |
| --- | --- |
| Authority | Shuhei, 7 October 2026; start Phase 9 with the five supplied meshes |
| Question | How sensitive is the separator response to mesh resolution under one controlled setup? |
| Pre-run audit | Compare all active and nested settings with saved 08b; retain traced deliberate changes; ask Shuhei about untraced differences before changing or retaining them |
| Current authorized work | Apply and run the simplified 342k EWF settings/count schedule on Server 5 to 200 ms total film age |
| Endpoint boundary | Bulk active during adjustment; frozen during middle film development; active again from 195 to 200 ms; save paired 200 ms endpoint |
| Deferred work | Final mesh-convergence qualification; other meshes remain under their owning chats |
| EWF planning decision | Human, 9 October 2026: 342k is the Server 3 focus; simplify [EWF Plan v1](ewf-plan-v1.md) to settings and iteration counts. Nominal endpoint 200 ms total film age; continued growth accepted. |
| EWF plan authority | Human authorizes reloading the preserved 342k parent, applying agreed settings on Server 5, and running the settings/count schedule once ready. Film/bulk surface tension 0.04041 N/m; lower-film mass/momentum drain ON, capture time 1.5 ms. |
| Session control | Human instruction: never exit Fluent; human controls restarts. No agent exit/termination commands. Further model-switch compatibility probes are excluded from this preparation route. Server 3 restarted; preserved Mixture pair restored. |
| Fleet | This chat now owns Server 5 for 342k EWF setup and execution. Human revoked this chat's Server 3 authority on 9 October 2026. Do not connect to or control Server 3. Separate Server 4 chat retains 2.6M ownership. |
| Server 1 authority | Shuhei, 9 October 2026: full Server 1 authority; apply EWF Plan v1 and run the selected 679,970-cell mesh only. [Owned lane](server1-680k/CONTEXT.md) |
| Server 1 endpoint plan | Continue verified N27580 /42.5 ms at1 µs to N185080 /200 ms:152,500 frozen-bulk updates to195 ms, then5,000 bulk-active updates. All remaining sections delivered automatically. [Exact setup](server1-680k/setup.md) |
| Server 1 evidence | N18580 / 33.5 ms pair saved and hashed; Courant stop at peak 0.218784. N21580 / 36.5 ms saved and reopened; resumed at 1 µs for 3,000 updates with a 0.8 Courant ceiling; prior Courant and film subiteration warnings remain. [Current execution evidence](server1-680k/results.md) |
| Selected 997k final checkpoint | Human, 9 October 2026: use N8080 / 0.650 ms as the final initial bulk-development state. OneDrive pair replaced and hashes verified; N9103 retained in the archive. No new solve. |
| Continuous supervision | Human instruction, 7 October: monitor controller and Server 3 without waiting for manual idle reports. Read local evidence every 30 s; finite health check every 5 min. Trigger the originating chat for a stopped controller, 3 min without transcript/log progress, or preparation completion. A timeout alone does not prove a failed or idle solver. |
| Notifications | Quiet during normal progress; notify on a meaningful change, completion, failure, or required human input. Mechanical recovery stays within the existing envelope and never exits or restarts Fluent. |
| Current human control | Completed N59080 / 160.950 ms attempt exceeded Courant limit 0.8 with peak 1.497401. Failed attempt preserved. Restored healthy N49080 / 135.950 ms (batch peak 0.050828), activated next lower planned step 0.1 µs through save/reopen. First 1,000-update check running toward N50080 / 136.050 ms; fresh actual step 0.1 µs and Courant 0.00203 verified. Remaining nominal 640,500 updates end at N689580 / 200 ms, final 195–200 ms bulk active. Watcher active; no exit/restart. |
| Monitoring dependency | macOS launch agent restarts the watcher if it exits. Mac and network must remain available; an awake guard runs while the watcher runs. |
| Previous endpoint | Preserve before replacement; never terminate Server 1 or its campaign |
| Input owner | Supplied mesh files in CAD PurnantoV2; keep unchanged |
| Execution owner | PyAnsys scripts and machine evidence |
| Settings basis | Stage 4 selected-mechanism recovery readback; provisional common settings across meshes |
| Startup basis | Verified historical low-feed A fields; native mesh interpolation; no bulk reinitialization |
| Film start | Dry-film A; preserve its zero clock through transfer |
| Adaptive horizon | Mesh-dependent minimum holds; additional 1000-update blocks selected from monitor histories |
| Geometry limitation | Different surface tessellation and wall names; prove physical scope and record geometry discretization differences |
| Claim limit | Prepared full-load states and provisional mesh sensitivity; no final EWF, steady-film, mesh-independence or plant-validation claim |

| Record | Owner |
| --- | --- |
| Runnable intent | [setup](setup.md) |
| Current outcome | [results](results.md) |
| Compact state | [phase-state](phase-state.yaml) |
| Live supervision | [machine watcher state](../../../PyAnsys/output/phase9-mesh-convergence/20261007/continuous-supervision.json) |
| Mesh audit | [machine input audit](../../../PyAnsys/output/phase9-mesh-convergence/20261007/mesh-input-audit.json) |
| Method reference | [Stage 4 startup](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/setup.md) |
