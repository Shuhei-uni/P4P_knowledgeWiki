# Server 6 — angle slit / 213k

| Archive status | Value |
| --- | --- |
| Status | Superseded; this queued Phase 9 plan was not executed |
| Authority | Historical 11 October plan only; no active run authority |
| Current case | [Phase 10 angle contract](../CONTEXT.md); completed 50 ms under basic Stage 3 settings |

| Contract | Selected scope |
| --- | --- |
| Authority | Shuhei, 11 October 2026: finish the vertical slit at 100 ms wall-film time, then start the angle slit with the same procedure |
| Execution order | Start only after the vertical slit 100 ms endpoint is saved/reopened, checked and preserved |
| Server | Server 6; no other server or unrelated lane |
| Shared input | OneDrive `CAD PurnantoV2/Design improvement/Separator-angle-slit-213k.msh.h5`; 213,232 cells |
| Current state | Mesh audited offline; native mesh checks, source transfer and case preparation deferred until vertical completion |
| Target | 100 ms total wall-film time; final 95–100 ms bulk active |
| Procedure | Same Phase 9 settings, field preservation, direct-drain proof and evidence-based 0.1 → 2.5 → 5 µs ladder; reduce step when numerical checks fail |
| Claim limit | Geometry and mesh both change; this does not isolate mesh sensitivity or establish physical validation |
| Setup | [Selected procedure](setup.md) |
| Evidence | [Results and current limits](results.md) |

| Numerical acceptance revision — human, 11 October 2026 | Selected rule |
| --- | --- |
| Authority | Remove any gates other than Courant; this supersedes earlier numerical qualification gates in this record |
| Sole numerical acceptance gate | Film Courant ≤0.8 |
| Selected step | Fixed 1 µs; apply at the next reconciled native command boundary with save/reopen |
| Inner solver | Keep 100 maximum subiterations and 1e-5 stop. Record pass counts and residuals as diagnostics; no minimum pass fraction or inner-convergence gate |
| Film ledger | Record as a diagnostic; no numerical acceptance gate |
| Evidence and completion | Preserve paired checkpoints and Fluent; verify native iteration/film clock, intended settings, final 95–100 ms bulk-active interval and saved/reopened 100 ms endpoint before the next case |
