# Phase 10 — Proposed design

| Contract | Human direction / current state |
| --- | --- |
| Authority | Shuhei, 11 October 2026: run the supplied design with basic EWF to 100 ms; name this Phase 10 proposed design |
| Mesh | Supplied angled-slit mesh; 213,232 file cells |
| Goal | Prepare the proposed design and develop its wall film to 0.100 s total film age |
| Procedure | Phase 9 native transfer/startup; [Stage 3 basic EWF development](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md) |
| Session | Human selected `direct-fluent-use`; pinned local Fluent 2025 R2 Student, four ranks |
| Scope | One geometry; bulk startup, basic EWF development, numerical recovery and endpoint evidence |
| Bulk preparation | Bulk equations active through low-feed hold, ramp and full-feed hold |
| Frozen development | Follow the referenced method; first prove direct film removal, advancing film clock and preserved bulk fields |
| Preservation | Native field interpolation; no bulk reinitialization or film reset after startup |
| Session safety | Preserve valuable endpoints; leave Fluent open |
| Endpoint | 100 ms from dry A; count startup and probes; save/reopen the final pair |
| Timestep revision | Human request: 1 µs for 3,000 iterations, then 2.5 µs to the same 100 ms endpoint; retain evidence guards and preserved fields |
| Current authority | Human paused the run and requested the furthest film-time pair in OneDrive. Preserve and verify that endpoint; do not resume toward 100 ms without new human direction |
| Claim limit | Finite film development; no steady-film, mesh-convergence or plant-validation claim |
| Separate work | Phase 9 retains its own scope and records |

| Evidence anchor | Observation / limit |
| --- | --- |
| [Mesh audit](../../../PyAnsys/output/phase10-proposed-design/20261011/mesh-input-audit.json) | 213,232 cells; native scale and quality pending |
| Prepared-A-N1580 pair | Local case/data hashes match the recorded Stage 3 parent |
| [Phase 9 startup](../phase-09-mesh-convergence/setup.md) | Transfer and preparation method; later Stage 4 EWF physics is not the requested basic EWF |
| [Film-development findings](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md#findings-to-apply-to-another-case) | Frozen-bulk advancement and matched-time checks; timestep limits need qualification on this mesh |

| Decision condition | Permitted action |
| --- | --- |
| Verified child and smoke evidence | Run bulk startup, then film development |
| Numerical failure | Preserve evidence; repair controls and resume verified fields |
| Film removal fails with frozen bulk | Repair the traced direct removal path and repeat the bounded probe |
| Verified 100 ms clock and final pair | Analyse finite endpoint; retain stationarity and conservation limits |
