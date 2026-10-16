# Server 5 — Plan v1 slit continuations to 500 ms

| Contract — 15 October 2026 | Selected value |
| --- | --- |
| Authority | Human: Server 5 only from now; continue vertical and angled slit from their current points to 500 ms; match Phase 9 EWF Plan v1 |
| Execution order | Vertical first; angle only after verified vertical 500 ms pair is saved, reopened and shared |
| Plan owner | [Current Phase 9 EWF Plan v1](../phase-09-mesh-convergence/ewf-plan-v1.md) |
| New horizon | 500 ms total film age; this human-selected horizon supersedes the plan's 195 ms pilot endpoint for these two designs only |
| Retained parents | Vertical N44661 / 150 ms; angled N43492 / 150 ms; original OneDrive pairs remain unchanged |
| Server scope | Connect, query and control Server 5 only; no Server 6 access |
| Bulk and feed | Retain Mixture/RNG/Coupled and liquid/vapour feed 116.92/80.69 kg/s; retain existing bulk collector hooks |
| Roughness | 0.045 mm, coefficient 0.5; physical bottom smooth |
| EWF | Full momentum, gravity, gas shear, wall viscosity, advection, pressure, spreading and surface tension on; phase accretion on |
| Surface tension | Bulk and EWF 0.04041 N/m |
| Numerics | Sequential film mass/momentum; original first-order implicit; first-order spatial schemes; 100 inner iterations, tolerance 1e-5; smoothing level 2, factor 0.5 |
| Release/collection | DPM collection, splash, stripping and edge separation on; flow momentum feedback off |
| Lower film domain | Allocate mapped wall:004 at zero height, then restore original upper-film and bulk data; preserve inherited 150 ms clock |
| Direct drain | Lower film mass and matching XYZ momentum removal; 1.5 ms capture time; 1% source limiter; profile refresh every update |
| Step selection | Initial fixed 0.1 µs; current Plan v1 Server 5 override selects 2.5 µs later, with particle cadence 8 and matching drain refresh; adaptive off |
| Numerical limits | Disabled as in current Plan v1; actual solver errors and evidence/control failures require in-scope recovery |
| Preservation | Save loaded Server 5 endpoint before replacement; preserve prepared pre-run and final case/data pairs; retain all source 150 ms and earlier pairs |
| Storage | Local Server 5 transcripts/autosaves; unique OneDrive prepared/final selected pairs |
| Claim limit | First 150 ms used earlier basic EWF. New settings apply to the additional 350 ms; initial history and mesh differ. Film age alone does not establish steady film or physical validation |
| Machine evidence | [Campaign receipts](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/) |

| Stage for each case | Bulk | Step | New native updates | Film age after stage |
| --- | --- | --- | ---: | ---: |
| Prepared settings and paired reopen | Active | 0.1 µs | 0 | 150.000 ms |
| New-settings smoke | Active | 0.1 µs | 10 | 150.001 ms |
| Remaining bulk adjustment | Active | 0.1 µs | 1490 | 150.150 ms |
| Frozen transition / direct-drain proof | Frozen | 0.1 µs | 1000 | 150.250 ms |
| First 2.5 µs stage | Frozen | 2.5 µs | 1000 | 152.750 ms |
| Main growth, Plan v1 10,000-update commands | Frozen | 2.5 µs | 138900 | 500.000 ms |
| Total | — | — | 142400 | 500.000 ms |

| Case | Parent | Nominal final | Per-case records |
| --- | --- | --- | --- |
| Vertical slit, 154063 cells | N44661 / 150 ms | N187130 / 500 ms after recovery | [Setup](vertical-slit154k/planv1-500ms/setup.md), [state](vertical-slit154k/planv1-500ms/phase-state.yaml) |
| Angled slit, 213232 cells | N43492 / 150 ms | N185892 / 500 ms | [Setup](angled-slit213k/planv1-500ms/setup.md), [state](angled-slit213k/planv1-500ms/phase-state.yaml) |

| Current execution | Evidence |
| --- | --- |
| Vertical | Evidence access lost during bulk-scale adjustment; last printed N45960 / approximately 150.0139 ms without a new received error. Current command outcome unconfirmed. Last verified pair N44691 / 150.0012 ms retained |
| Angle | Queued in the same Server 5 worker; no angle load before verified/shared vertical 500 ms pair |
| Runtime | Isolated Server 5 dependencies and exact code import verified; runs independently of laptop |
| Supervision | Read-only Server 5 file snapshots and passive transcript; completion/failure/action notifications only |
| Bulk-scale startup | [Verified smoke](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/bulk-scale-startup-verification.json) |
| Second failure | [Control reconciliation](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/second-failure-reconciliation.json); restore native access before further recovery |
| Recovery evidence | [Verified recovery startup](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/recovery-startup-verification.json) |
| Evidence | [Startup and handoff](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/startup-verification.json) |

| Vertical numerical recovery — 16 October 2026 | Selected value |
| --- | --- |
| Reason | Film divergence followed by bulk k/epsilon FPE at the lowest prescribed 0.1 µs level |
| Restore | Last verified saved/reopened N44671 / 150.001 ms pair; failed N45047 pair retained |
| Remaining bulk adjustment | 10-update recovery smoke plus 1480 updates at 0.01 µs; DPM cadence 2000; matching drain refresh |
| Frozen transition | 1016 updates at 0.1 µs, including clock alignment to the main 2.5 µs grid |
| Main stage | 1000-step 2.5 µs stage, then 138953 updates at 2.5 µs; target N187130 / 500 ms |
| Settings | Same Plan v1 physics, original implicit and sequential EWF; smaller numerical step is recorded as recovery below the prescribed ladder |
| Evidence | [Native failure reconciliation](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/failure-reconciliation.json) |

| Bulk numerical recovery — 16 October 2026 | Selected value |
| --- | --- |
| Current native state | Control access returned; idle at failed N44857 / 150.00286 ms; failed pair saved/hashed; old host job BLOCKED |
| Restore | Verified N44681 / 150.0011 ms pair; original 150 ms source unchanged |
| Controlled numerical change | Bulk global pseudo-time scale factor 1.0 → 0.1 for remaining bulk adjustment; film stays fixed at 0.01 µs. Coupled method, active equations and Plan v1 model physics unchanged |
| Restore controls | Return bulk scale to 1.0 when freezing bulk; save/reopen. Then film 0.1 µs transition and 2.5 µs main growth |
| Counts | 10-update new smoke + 1470 bulk updates; frozen 1016 at 0.1 µs, 1000 at 2.5 µs, then 138953 at 2.5 µs; N187130 / 500 ms |
| Evidence | [Native reconciliation](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/native-control-return-reconciliation.json), [code review](../../../PyAnsys/output/phase10-proposed-design/20261015/server5-planv1-to500ms/bulk-scale-code-review.json) |
