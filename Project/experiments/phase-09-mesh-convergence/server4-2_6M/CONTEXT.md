# Phase 9 — Server 4, 2.6M preparation

| Contract | Selection |
| --- | --- |
| Authority | User instruction, 7 October 2026: this chat owns Server 4 and only 2_6M |
| Other server | Server 3 belongs to the original chat; no connection, query or control |
| Solver safety | Never exit, terminate or restart Fluent; inspect before acting; observe active solve/save |
| Parent | Verified original low-feed A, N1580, dry film; native Replace Mesh; no bulk initialization |
| Mesh | Separator-purnanto-2_6M.msh.h5; 2,596,657 cells; exact shared input audit hash required |
| Physics | Common provisional Stage 4 and approved 08b contract; all drift/flow/ke/mp equations active |
| Endpoint | User-selected N8580 as the final initial bulk development state; preserve paired case/data on OneDrive. Initial bulk-development endpoint remains preserved; subsequent EWF schedule authorised. |
| Storage | Running pairs, autosaves and native transcripts on Server 4 Windows local disk |
| Supervision | Laptop controller retired and watcher stopped after native handover; Fluent idle at N8580. Final local pair reopen verified; OneDrive pair hashes match. |
| Claim limit | Initial bulk development only. User accepts the current unsteady state. Original 4000-update full-feed minimum was not reached; no steady state, final mesh convergence, closure or physical validation claim. |

| Owning reference | Record |
| --- | --- |
| Common scientific settings | [Phase 9 setup](../setup.md) |
| Approved bulk exceptions | [08b audit](../settings-audit-08b.md) |
| Machine handoff | [Server 4 handoff](../../../../PyAnsys/output/phase9-mesh-convergence/20261007/server4-chat-handoff.md) |
| Local runnable intent | [Setup](setup.md) |
| Current evidence | [Results](results.md) |

| Current EWF child | State |
| --- | --- |
| Authority | User requests simplified settings/counts plan, applies settings, then authorises the run. EWF schedule through 200 ms is active. |
| Settings | Sequential first-order implicit film; flow momentum coupling OFF; curvature smoothing ON, level 2/factor 0.5; film surface tension 0.04041000083088875 N/m |
| Direct drain | Lower collector EWF wall enabled; 1.5 ms capture time; mass and XYZ momentum sinks enabled; refresh every update |
| Preserved state | N8580 / 0.700 ms; original main-film facet mass/thickness/XYZ velocity fields preserved exactly |
| Current equations and step | All bulk equations active; fixed 0.1 µs; DPM interval 200 updates = 20 µs |
| Settings receipt | [Readback and reopened pair](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/ewf-settings-current.json) |

| Automatic stage handover | Current arrangement |
| --- | --- |
| Current controller | Recovery of completed frozen transition at N12080; corrected continuation retains the Server 4 schedule below |
| Waiting successor | Separate controller waits for the current process to exit and its N11080 pair to be reopen verified; no Fluent connection while waiting |
| Remaining schedule | Frozen transition reached N12080 / 1.050 ms; 77,580 frozen updates at 2.5 µs remain; restore bulk for 2000 updates to 200 ms / N91660 |
| Duplicate prevention | Successor reservation lock plus exclusive controller lock, live idle/native-coordinate checks and explicit pause check |
| Recovery instruction | Read [successor state](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/ewf-successor.json) before any wake-driven continuation; an armed or running successor owns the next commands |
| Dependency | Both controllers and watcher run on the Mac; keep laptop awake and network available |

| Server 4 schedule authority | Selection |
| --- | --- |
| Scope | This chat owns Server 4 / 2_6M only. The shared EWF plan now describes a separate Server 5 pilot; its 5 µs/count changes do not override this chat's approved 2.5 µs schedule. |
| Completed stages | Bulk-active adjustment through N11080; frozen 0.1 µs transition through N12080 |
| Recovery | Frozen stages omit bulk residual rows. Prove terminal native iteration and complete film-clock rows instead; never repeat the completed transition. |
| Remaining stage boundaries | N13080 / 3.550 ms after first 2.5 µs block; N89660 / 195 ms before bulk restoration; N91660 / 200 ms with all bulk equations active |

| Server 4 limit update | Value |
| --- | --- |
| Film Courant setting and accepted maximum | 0.8, user direction 11 October 2026; apply while idle and verify persistence before continuation |
