# Phase 10 — Angled slit contract

| Record ownership | Value |
| --- | --- |
| Phase | Phase 10 proposed design; human reassignment, 12 October 2026 |
| Phase navigation | [Both proposed designs](../index.md) |

| Contract | Human direction / current state |
| --- | --- |
| Authority | Shuhei, 12 October 2026: load the OneDrive angled-slit paused pair, use 10 µs, reach 50 ms; no numerical thresholds or qualification requirements |
| Mesh | Supplied angled-slit mesh; 213,232 file cells |
| Goal | Develop the selected angled-slit checkpoint from 23.705 ms to 50.000 ms total film age |
| Procedure | Phase 9 native transfer/startup; [Stage 3 basic EWF development](../../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md) |
| Session | Server 6; existing restarted Fluent 2025 R2; attach only, preserve source and endpoints; leave Fluent open |
| Scope | One geometry; bulk startup, basic EWF development, numerical recovery and endpoint evidence |
| Bulk preparation | Historical source preparation:low-feedhold,ramp,full-feedhold. Do not repeat onresume |
| Frozen development | Retain the selected checkpoint’s frozenbulk settings and existingbasicEWF; no newqualification orprobe required |
| Preservation | Native field interpolation; no bulk reinitialization or film reset after startup |
| Session safety | Preserve valuable endpoints; leave Fluent open |
| Endpoint | 50 ms total film age from the selected23.705ms checkpoint; save/reopen finalpair |
| Timestep revision | Human,12October:10 µs; onefinal5 µs update reachesexactly50ms. No numericalacceptance thresholds |
| Current authority | Resume the OneDrive pausedN30862 pair onServer6 to50ms; preserve Fluent andendpoints |
| Claim limit | Finite film development; no steady-film, mesh-convergence or plant-validation claim |
| Separate work | Phase 9 retains its own scope and records |

| Evidence anchor | Observation / limit |
| --- | --- |
| [Mesh audit](../../../../PyAnsys/output/phase10-proposed-design/20261011/mesh-input-audit.json) | 213,232 cells; native scale and quality pending |
| Prepared-A-N1580 pair | Local case/data hashes match the recorded Stage 3 parent |
| [Phase 9 startup](../../phase-09-mesh-convergence/setup.md) | Transfer and preparation method; later Stage 4 EWF physics is not the requested basic EWF |
| [Film-development findings](../../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md#findings-to-apply-to-another-case) | Frozen-bulk advancement and matched-time checks; past matched-time findings; current10 µs is human-selected without newqualification |

| Decision condition | Permitted action |
| --- | --- |
| Verified paused source and reopened controls | Run selected10 µs continuation to50ms |
| Technical stop | Preserve endpoint, reconcile native state; no timeout replay |
| Numerical diagnostics | Record; no stop thresholds or extraqualification |
| Verified50 ms clock and finalpair | Analyse finite endpoint; retain stationarity and conservation limits |

| Current continuation | Selected value |
| --- | --- |
| Film numerics | Fixed 10 µs for 2629 updates to49.995ms; one final5 µs update to exactly50ms |
| Current state | Complete: N33492 /50.000ms; finalpair saved/reopened and both OneDrivecopies SHA-256 verified; Fluent left open; watcher stopped |
| Numerical decision | No Courant, residual, thickness, ledger or qualification acceptance gates; record diagnostics only |
