# Vertical slit — angled-settings results

| Check | Current evidence |
| --- | --- |
| Parent | N31000 / 13.392 ms inspected natively; source case/data hashes recorded |
| Angled reference | Idle N33492 / 50.000 ms; model parameters and wall conditions read from the live case; host job COMPLETE |
| Preservation | Loaded angled endpoint saved and hashed before vertical parent load; earlier vertical endpoint retained |
| Controlled change | Basic angled EWF model, wall scope, roughness and drainage; fixed 10 µs |
| Build/run status | Child saved/reopened; full native EWF parameter and wall checks match. Complete: N34661 / 50.000 ms; native readback, paired reopen and both Mac OneDrive hashes verified |
| Limit | Earlier film history differs; equal native iteration does not give equal film age |
| Evidence | [Machine receipts](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/) |

| Run control | Evidence |
| --- | --- |
| Host dispatch | [Launch receipt](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/host-launch.json); reviewed runner hash verified and host import passed |
| Persistence | [Prepared child](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/prepared.json); exact wall-role checks passed after reopen |
| Supervision | Read-only watcher; no routine notifications; native controller runs on Server 6 |

| Native execution proof | Verified observation |
| --- | --- |
| Changed-mode smoke | 10 updates; direct native film outflow increment 0.000347035 kg; bulk liquid/vapour inventories and liquid volume unchanged |
| Growth startup | [Native transcript prefix](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/native-startup.json): 102 rows, 13.502–14.512 ms at 10 µs; Courant 0.1609733–0.1670331 diagnostic |
| Latest verified saved endpoint | N34661 / 50.000 ms; exact clock verified natively after final reopen |
| Target | N34661 / 50.000 ms; complete |

| Completion | Verified evidence |
| --- | --- |
| Native endpoint | N34661 / 50.000 ms; 3661 new updates from N31000 |
| Main step | 3660 updates at 10 µs, including 10 smoke updates |
| Final step | One 8 µs update for the exact 50 ms clock |
| Persistent setup | Full angled basic-EWF parameter match, except endpoint step; wall-role checks passed; bulk equations frozen |
| Diagnostic peak Courant | 0.5509019; no numerical stop threshold applied |
| Endpoint sharing | Final case/data saved and reopened on Server 6; Mac OneDrive copies match host SHA-256 values |
| Connection event | Read-only access returned; existing host run completed; zero replay or solver mutation in reconciliation |
| Evidence | [Native completion and file hashes](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/completion-reconciliation.json) |
| Session | Fluent left open and idle; watcher completed; no updates beyond 50 ms |

| 150 ms continuation — 13 October 2026 | Current evidence |
| --- | --- |
| Authority | Human selected another 100 ms from the verified 50 ms endpoint |
| Reconciliation | Prior host controller/job complete; native N34661 / 50 ms idle; no other Server 6 lane controller |
| Plan | 10,000 fixed 10 µs updates to N44661 / 150 ms; no numerical thresholds |
| Status | Preparation completed; 10 µs step saved/reopened and matched. Complete: N44661 / 150.000 ms; 10,000 fixed 10 µs updates; native clock, paired reopen and Mac OneDrive hashes verified |
| Evidence | [Continuation receipts](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/) |

| Continuation access state | Evidence / consequence |
| --- | --- |
| Network | Fluent, RDP and SMB TCP respond; native bounded readbacks time out. TCP reachability does not prove solver health |
| Last verified endpoint | N34661 / 50.000 ms; paired reopen and OneDrive hashes previously verified |
| Host dispatch | Verified once after preparation; native fixed 10 µs startup verified; no replay from timeout |
| Preparation | Existing preparation completed; 50 ms pair preserved, 10 µs activation saved/reopened and verified |
| Continuation queue | Completed successfully: one reviewed host dispatch; read-only watcher PID92271 active |
| Machine receipt | [Pending control state](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/pending-control-state.json) |

| Host dispatch reconciliation | Verified observation / limit |
| --- | --- |
| Prepared child | N34661 / 50 ms; fixed 10 µs, EWF wall/model and frozen-bulk state verified after paired reopen |
| Controller | Host runner identity matched; import passed; dispatch once; last retrieved host job/run status RUNNING |
| Native startup | Read-only access returned; 540 native film rows at fixed 10 µs, 50.010–55.400 ms. Prefix proves startup, not latest clock or completion. No replay or setting command sent |
| Evidence | [Dispatch reconciliation](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/dispatch-reconciliation.json) |

| Read-only recovery and native startup | Verified evidence |
| --- | --- |
| Controller/job | RUNNING; active native command targets N44661 / 150 ms |
| Transcript | [Startup receipt](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/native-startup.json): 540 prefix film rows, 50.010–55.400 ms; all observed steps 10 µs |
| Latest verified paired endpoint | N34661 / 50.000 ms; later transcript rows are observations, not saved endpoint proof |
| Recovery | Read-only access returned; original command retained; zero solve replay or settings changes |

| 150 ms endpoint — 13 October 2026 | Verified evidence |
| --- | --- |
| Native endpoint | N44661 / 150.000 ms after final paired reopen |
| New updates | 10,000 at fixed 10 µs from N34661 / 50 ms; all 10,000 native film rows recovered |
| Persistent settings | Same basic EWF parameters and wall-role conditions; numerical film drain disabled; bulk equations frozen |
| Peak Courant | 0.731242; diagnostic only, no numerical threshold applied |
| Final sharing | Unique OneDrive final-150ms-N44661 pair; both Mac files match Server 6 SHA-256 values |
| Earlier pair | Original 50 ms OneDrive pair still present; both hashes rechecked |
| Connection gaps | Existing host command completed; no solve replay, rollback, or physics change |
| Session | Fluent left open and idle; watcher stopped on completion; no updates beyond 150 ms |
| Evidence | [Native completion and file hashes](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/completion-reconciliation.json) |
