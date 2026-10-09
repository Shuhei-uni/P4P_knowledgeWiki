# Phase 9 — Mesh convergence preparation

| Contract | Current human direction |
| --- | --- |
| Authority | Shuhei, 7 October 2026; start Phase 9 with the five supplied meshes |
| Question | How sensitive is the separator response to mesh resolution under one controlled setup? |
| Pre-run audit | Compare all active and nested settings with saved 08b; retain traced deliberate changes; ask Shuhei about untraced differences before changing or retaining them |
| Current authorized work | Prepare and run all five meshes through the Stage 4 startup method to a full-feed hold |
| Endpoint boundary | Bulk equations remain active; save paired full-feed endpoints |
| Deferred work | Bulk freeze, EWF-only continuation, final EWF settings and final mesh-convergence qualification |
| EWF planning decision | Shuhei, 9 October 2026: [EWF Plan v1](ewf-plan-v1.md); compare at 200 ms total film age, accept continued growth and treat film mass as an output; stability first, speed second |
| EWF plan authority | Record the plan only; no new solve or settings change authorized by this writing request; numerical candidates require qualification |
| Session control | Human instruction: never exit Fluent; human controls restarts. No agent exit/termination commands. Further model-switch compatibility probes are excluded from this preparation route. Server 3 restarted; preserved Mixture pair restored. |
| Fleet | This chat owns Server 3 for 60k, 342k, 680k and 997k. A separate human-created chat owns Server 4 for 2.6M only. See the machine server-assignment record. |
| Continuous supervision | Human instruction, 7 October: monitor controller and Server 3 without waiting for manual idle reports. Read local evidence every 30 s; finite health check every 5 min. Trigger the originating chat for a stopped controller, 3 min without transcript/log progress, or preparation completion. A timeout alone does not prove a failed or idle solver. |
| Notifications | Quiet during normal progress; notify on a meaningful change, completion, failure, or required human input. Mechanical recovery stays within the existing envelope and never exits or restarts Fluent. |
| Current human control | Human resumed the 997k ramp after laptop pause. Saved N3620 pair reopened and verified before a fresh controller launch; completed N3610→N3620 segment not repeated. Server 3 remains allocated through 997k; supervision active; no Fluent exit/restart. |
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
