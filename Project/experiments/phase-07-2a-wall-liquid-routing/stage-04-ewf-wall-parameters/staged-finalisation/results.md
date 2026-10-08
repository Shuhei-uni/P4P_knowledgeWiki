# Staged 60k EWF development — execution record

| Item | Verified status |
| --- | --- |
| Human authority | Run the staged method from the original N8000 pair on the 60k mesh; laptop remains active |
| Setup | [Method and execution order](setup.md) |
| Exact parent | Original `auto-8000-1-08000.cas.h5` / `.dat.h5`; case SHA-256 `41463d40f1fecf329cada833d5396e630db603cec3ef453d771122d9b5f900f6`; data SHA-256 `09653f35ce7ec2f79bab3204680245caac110d5e7a5cc4c6c46ef3e4776830a4` |
| Mesh identity | Case HDF5 cell-zone ranges end at 60,964; original file hashes match the preserved server parent |
| Previous continuation | N17000 / film clock 0.009641999999999292 s preserved; final pair hashed and data reopened; previous N13000 and N48483 remain retained |
| Offline review | 13 regression tests passed; native command order, active-journal exclusion, source timing, clocks, bulk gates and all-sample guards checked |
| Current execution | N9020 verified and preserved. Second block stopped near passive N9195 before its N10020 target; runner/watcher stopped. Finite raw idle query returned false, normal Settings returned an internal improper-list error, bounded Scheme reads timed out. Exact GUI error requested; live fields have not been reloaded or reset. [Recovery receipt](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/session-access-recovery.json) owns this interruption |
| Native storage | `C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\staged-N8000-20261008`; paired endpoints/autosaves and transcripts on Server 1 local disk |
| Supervision | Detached laptop runner plus read-only watcher; native journals perform fixed solve blocks |
| Claim limit | Startup proves command delivery and evidence collection, not bulk stability or film accuracy. The production ladder has not started. Sequential ladder cannot isolate timestep error; missing inner residuals and event accounting remain explicit limits. Lower-region inventories are recorded; separate lower-region drift and checkpoint spatial-field comparison are not automated and limit stable-field qualification |

| Startup / supervision proof | Evidence and limit |
| --- | --- |
| Accepted startup updates | N8000 → N8020; 20 updates at 0.1 µs; +2 µs film time |
| Native film clock | 0.0006419999999999314 → 0.0006439999999999303 s |
| Peak film Courant | 0.0001704077 |
| Preserved endpoint | N8020 case/data hashed; native terminal receipt and report histories captured |
| Command completion | SDK transcript stream remained empty. The runner now waits for native `Exec(wait=True)`, then checks the disk terminal receipt, pair, counts and clock; passive v0 Monitor stream records live progress |
| Recovery | Resume from verified N8020 without reloading N8000 or repeating the completed startup updates |
| Watcher launch | Start after the runner publishes its current PID. Read local files/PID only; no Fluent queries or control |

| First bulk-baseline block | N8020 → N9020 |
| --- | --- |
| Accepted updates / film age | 1,000 at inherited 0.1 µs; +0.1 ms; terminal clock 0.0007439999999998785 s |
| Native completion | Blocking execution returned; terminal receipt verified; paired endpoint saved and both hashes verified |
| Residual coverage | 1,000 complete rows |
| Peak film Courant | 0.000169401; no operating guard failure |
| Bulk liquid inventory | 48.921207 → 49.980217 kg; +2.16% across this block |
| Actual phase-2 outlet | 0.497230 → 0.508820 kg/s outward |
| Applied collector | 23.926915 → 56.671551 kg/s; still changing |
| Transition decision | Continue bulk active. One block cannot pass the three-window gate; inventory/collector changes do not support freeze |
| Exact evidence | [Verified block receipt](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/blocks/002-A_BULK_BASELINE-N8020-N9020/block.json) |

| Owning machine evidence | Record |
| --- | --- |
| Job specification | [job.json](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/job.json) |
| Code review | [code-review.json](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/code-review.json) |
| Runner state | [run-manifest.json](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/run-manifest.json) |
| Watcher state | [watcher-status.json](../../../../../PyAnsys/output/phase72a-stage4-staged/20261008/watcher-status.json) |
