# Phase 9 — Mesh convergence preparation

| Contract | Current human direction |
| --- | --- |
| Authority | Shuhei, 7 October 2026; start Phase 9 with the five supplied meshes |
| Question | How sensitive is the separator response to mesh resolution under one controlled setup? |
| Pre-run audit | Compare all active and nested settings with saved 08b; retain traced deliberate changes; ask Shuhei about untraced differences before changing or retaining them |
| Current authorized work | EWF development complete at the human-selected frozen 195 ms endpoint. Preserve the pre-EWF-run and final 195 ms pairs; no further solve or supplementary recovery selected. |
| Endpoint boundary | All meshes: final EWF endpoint 195 ms total film age with bulk frozen. Preserve paired case/data immediately before the EWF schedule and at this final endpoint. |
| Deferred work | Final mesh-convergence qualification; other meshes remain under their owning chats |
| EWF planning decision | Human, 9 October 2026: 342k is the Server 3 focus; simplify [EWF Plan v1](ewf-plan-v1.md) to settings and iteration counts. Nominal endpoint 200 ms total film age; continued growth accepted. |
| EWF plan authority | Human authorizes reloading the preserved 342k parent, applying agreed settings on Server 5, and running the settings/count schedule once ready. Film/bulk surface tension 0.04041 N/m; lower-film mass/momentum drain ON, capture time 1.5 ms. |
| Session control | Human instruction: never exit Fluent; human controls restarts. No agent exit/termination commands. Further model-switch compatibility probes are excluded from this preparation route. Server 3 restarted; preserved Mixture pair restored. |
| Fleet | This chat now owns Server 5 for 342k EWF setup and execution. Human revoked this chat's Server 3 authority on 9 October 2026. Do not connect to or control Server 3. Separate Server 4 chat retains 2.6M ownership. |
| Server 1 authority | Shuhei, 9 October 2026: full Server 1 authority; apply EWF Plan v1 and run the selected 679,970-cell mesh only. [Owned lane](server1-680k/CONTEXT.md) |
| Server 1 endpoint plan | Preserve the current 1 µs section through N77580 / 92.5 ms. Next: 10,000 updates at 2.5 µs to 117.5 ms, then retain 5 µs to N104080 / 200 ms. Bulk frozen through 195 ms; all bulk equations active for 195–200 ms. Deliver the remaining sections automatically. [Exact setup](server1-680k/setup.md) |
| Server 1 evidence | N18580 / 33.5 ms pair saved and hashed; Courant stop at peak 0.218784. N21580 / 36.5 ms saved and reopened; resumed at 1 µs for 3,000 updates with a 0.8 Courant ceiling; prior Courant and film subiteration warnings remain. [Current execution evidence](server1-680k/results.md) |
| Selected 997k final checkpoint | Human, 9 October 2026: use N8080 / 0.650 ms as the final initial bulk-development state. OneDrive pair replaced and hashes verified; N9103 retained in the archive. No new solve. |
| Continuous supervision | Human instruction, 7 October: monitor controller and Server 3 without waiting for manual idle reports. Read local evidence every 30 s; finite health check every 5 min. Trigger the originating chat for a stopped controller, 3 min without transcript/log progress, or preparation completion. A timeout alone does not prove a failed or idle solver. |
| Notifications | Quiet during normal progress; notify on a meaningful change, completion, failure, or required human input. Mechanical recovery stays within the existing envelope and never exits or restarts Fluent. |
| Current human control | Human selected saved N111460 / 195 ms frozen-bulk pair as final EWF state, plus prepared pre-run N8580 / 0.700 ms pair. Both source pairs already saved and hash-verified; selected pair manifest records exact paths and provenance. Mac controller and watcher stopped to prevent further continuation/recovery. Already accepted 1 µs bulk-active journal is left running and may save a supplementary result; it is not the selected final state. No Fluent command sent for this selection. |
| Selected-pair shared archive | Pre-EWF N8580 / 0.700 ms and frozen final N111460 / 195 ms pairs exported to university OneDrive `P4P-Fluent-Artifacts/Phase9/Server5/342k/selected-ewf-pre-and-195ms-20261015`; all four hashes verified on Server 5 and independently on the Mac. No case loading, solve, exit or restart during export. |
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
