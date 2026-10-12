# Server 6 — vertical slit / 154k

| Contract | Current scope |
| --- | --- |
| Authority | Shuhei, 10 October 2026: own Server 6; use the accessible OneDrive N5080 vertical slit checkpoint; change necessary settings to match Phase 9 and run; 11 October revision: stop at 100 ms, then run angle slit with the same procedure |
| Checkpoint condition | Report back if the checkpoint pair is not on OneDrive |
| Geometry and mesh | Vertical slit; 154,063 cells; historical Phase 7.2A Stage 3 branch |
| Latest recorded checkpoint | N5290; 7.75 ms film age; saved and reopened on Server 3 local disk |
| Available shared checkpoint | N5080; 3.5 ms film age; both OneDrive files match archived SHA-256 hashes |
| Current status | Human, 12 October: pause this case and keep the saved 50.9 ms / N84000 pair. Stop automatic continuation and angle transition; preserve all endpoints and Fluent |
| Selected run parent | Human selected available N5080 on OneDrive; 3.5 ms film age; later N5290 deferred |
| Run basis | [EWF Plan v1](../ewf-plan-v1.md); adapt counts to the selected parent's film clock |
| Audit requirement | Read back selected parent settings; map the lower film collector; verify direct drainage with frozen bulk; save/reopen the prepared child |
| Session safety | Server 6 only; preserve valuable loaded endpoint before replacement; leave Fluent open |
| Claim limit | Geometry differs from the mesh-convergence family; this run cannot isolate mesh sensitivity |
| Revised horizon | Retain 50.9 ms; the previous 100 ms target and final bulk-active stage are cancelled. Angle case is on hold |
| Evidence | [Results](results.md) |
| Selected setup | [Phase 9 settings and run counts](setup.md) |


| Retained endpoint revision — human, 12 October 2026 | Selected value |
| --- | --- |
| Authority | Pause; no longer run this pair; keep near 50 ms. Human selects the saved 50.9 ms pair |
| Selected endpoint | Saved N84000 / 50.9 ms autosave from the fixed 2.5 µs branch |
| Preservation | Interrupted later endpoint N90695 / 67.6375 ms and all earlier pairs retained before replacement |
| Execution | No further solve. Hash and reopen selected pair; copy selected pair to OneDrive; leave Fluent open and idle |
| Supervision | Watcher stopped; no automatic recovery or angle launch |
| Evidence | [Retained endpoint receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/retained-50p9ms.json) |
| Claim limit | Retention does not establish convergence, numerical acceptance, steady film or physical validation |
