# Server 6 — vertical slit / 154k

| Contract | Current scope |
| --- | --- |
| Authority | Shuhei, 10 October 2026: own Server 6; use the accessible OneDrive N5080 vertical slit checkpoint; change necessary settings to match Phase 9 and run; 11 October revision: stop at 100 ms, then run angle slit with the same procedure |
| Checkpoint condition | Report back if the checkpoint pair is not on OneDrive |
| Geometry and mesh | Vertical slit; 154,063 cells; historical Phase 7.2A Stage 3 branch |
| Latest recorded checkpoint | N5290; 7.75 ms film age; saved and reopened on Server 3 local disk |
| Available shared checkpoint | N5080; 3.5 ms film age; both OneDrive files match archived SHA-256 hashes |
| Current status | Human, 12 October: continue from the saved N80580 / 42.35 ms endpoint at fixed 2.5 µs. Preserve the interrupted 1 µs partial pair before replacement. Courant, inner residuals and film ledgers are diagnostics; no automatic numerical stop or rollback. Final 95–100 ms remains bulk active; completion requires the saved/reopened 100 ms endpoint |
| Selected run parent | Human selected available N5080 on OneDrive; 3.5 ms film age; later N5290 deferred |
| Run basis | [EWF Plan v1](../ewf-plan-v1.md); adapt counts to the selected parent's film clock |
| Audit requirement | Read back selected parent settings; map the lower film collector; verify direct drainage with frozen bulk; save/reopen the prepared child |
| Session safety | Server 6 only; preserve valuable loaded endpoint before replacement; leave Fluent open |
| Claim limit | Geometry differs from the mesh-convergence family; this run cannot isolate mesh sensitivity |
| Revised horizon | 100 ms total film time; final 95–100 ms bulk active; then [angle slit](../server6-angle213k/CONTEXT.md) |
| Evidence | [Results](results.md) |
| Selected setup | [Phase 9 settings and run counts](setup.md) |

| Lane control revision | Selected value |
| --- | --- |
| Authority | Human, 12 October 2026: continue from N80580 / 42.35 ms with 2.5 µs; Courant 0.8 is a diagnostic reference |
| Control-change gate | Native command completes, pair preserved/hash verified/reopened; new controls saved/reopened before solve |
| Qualification | None. Record numerical diagnostics; keep running to 100 ms |

| Numerical acceptance revision — human, 11 October 2026 | Selected rule |
| --- | --- |
| Authority | Remove any gates other than Courant; this supersedes earlier numerical qualification gates in this record |
| Sole numerical acceptance gate | None: human 12 October revision supersedes Courant-only acceptance. Record Courant 0.8 as a diagnostic reference |
| Selected step | Fixed 2.5 µs from explicit N80580 / 42.35 ms checkpoint; save/reopen controls before solve |
| Inner solver | Keep 100 maximum subiterations and 1e-5 stop. Record pass counts and residuals as diagnostics; no minimum pass fraction or inner-convergence gate |
| Film ledger | Record as a diagnostic; no numerical acceptance gate |
| Evidence and completion | Preserve paired checkpoints and Fluent; verify native iteration/film clock, intended settings, final 95–100 ms bulk-active interval and saved/reopened 100 ms endpoint before the next case |

| Adopted continuation parent | Provenance / limit |
| --- | --- |
| Explicit human selection | N80580 / 42.35 ms, archived local pair with verified hashes; original OneDrive lineage remains N5080 / 3.5 ms |
| Historical numerical result | Parent block peak Courant 4.292395 exceeded 0.8. Human selected this preserved endpoint for a new 2.5 µs continuation; adoption does not relabel that historical block as passing |

| Continue-to-100 ms revision — human, 12 October 2026 | Selected rule |
| --- | --- |
| Authority | No, keep running to100ms; from42.35. Load N80580 / 42.35 ms and continue at 2.5 µs |
| Numerical diagnostics | Courant, inner residuals and ledger values are recorded; no automatic numerical stop or rollback |
| Completion | Preserve native clock, current settings, all endpoints and Fluent. Final 95–100 ms bulk active; verify paired 100 ms save/reopen |
