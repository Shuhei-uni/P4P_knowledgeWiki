# Phase 10 — Vertical slit contract

| Current authority — 15 October 2026 | Selected scope |
| --- | --- |
| Server | Server 5 only; previous Server 6 ownership is historical |
| New continuation | [Plan v1 from 150 to 500 ms](planv1-500ms/setup.md) |
| Source | Preserve the completed 150 ms basic-EWF pair and all earlier endpoints |

| Record ownership | Value |
| --- | --- |
| Phase | Phase 10 proposed design; human reassignment, 12 October 2026 |
| Phase navigation | [Both proposed designs](../index.md) |
| Preserved earlier endpoint | Enhanced-EWF N84000 / 50.9 ms retained |
| New selected continuation | [Basic angled-EWF settings at 10 µs](basic-ewf-10us/setup.md), completed from N31000 / 13.392 ms to N34661 / 50.000 ms |
| Historical method | Phase 9 continuation settings; earlier schedules below are superseded |

| Contract | Current scope |
| --- | --- |
| Authority | Shuhei, 10 October 2026: own Server 6; use the accessible OneDrive N5080 vertical slit checkpoint; change necessary settings to match Phase 9 and run; 11 October revision: stop at 100 ms, then run angle slit with the same procedure |
| Checkpoint condition | Report back if the checkpoint pair is not on OneDrive |
| Geometry and mesh | Vertical slit; 154,063 cells; historical Phase 7.2A Stage 3 branch |
| Historical later startup checkpoint | N5290; 7.75 ms film age; saved and reopened on Server 3 local disk |
| Available shared checkpoint | N5080; 3.5 ms film age; both OneDrive files match archived SHA-256 hashes |
| Current status | Human, 12 October: pause this case and keep the saved 50.9 ms / N84000 pair. Stop this continuation and its automatic transition; preserve all endpoints and Fluent |
| Selected run parent | Human selected available N5080 on OneDrive; 3.5 ms film age; later N5290 deferred |
| Run basis | [EWF Plan v1](../../phase-09-mesh-convergence/ewf-plan-v1.md); adapt counts to the selected parent's film clock |
| Audit requirement | Read back selected parent settings; map the lower film collector; verify direct drainage with frozen bulk; save/reopen the prepared child |
| Session safety | Server 6 only; preserve valuable loaded endpoint before replacement; leave Fluent open |
| Claim limit | Geometry differs from the mesh-convergence family; this run cannot isolate mesh sensitivity |
| Revised horizon | Retain 50.9 ms; the previous 100 ms target and final bulk-active stage are cancelled. The angle case later completed separately; see [angle contract](../angled-slit213k/CONTEXT.md) |
| Evidence | [Results](results.md) |
| Selected setup | [Inherited Phase 9 settings and retained endpoint](setup.md) |


| Retained endpoint revision — human, 12 October 2026 | Selected value |
| --- | --- |
| Authority | Pause; no longer run this pair; keep near 50 ms. Human selects the saved 50.9 ms pair |
| Selected endpoint | Saved N84000 / 50.9 ms autosave from the fixed 2.5 µs branch |
| Preservation | Interrupted later endpoint N90695 / 67.6375 ms and all earlier pairs retained before replacement |
| Execution | No further solve. Hash and reopen selected pair; copy selected pair to OneDrive; leave Fluent open and idle |
| Supervision | Watcher stopped; no automatic recovery or angle launch |
| Evidence | [Retained endpoint receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/retained-50p9ms.json) |
| Claim limit | Retention does not establish convergence, numerical acceptance, steady film or physical validation |

| Latest continuation endpoint | Verified value |
| --- | --- |
| Basic EWF latest pair | N44661 / 150.000 ms; 10,000 additional fixed 10 µs updates |
| Retained common-age reference | N34661 / 50.000 ms remains saved on OneDrive |
| Run status | Complete; Fluent open and idle; watcher stopped; no further run selected |
