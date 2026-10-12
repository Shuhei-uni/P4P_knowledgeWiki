# Vertical slit — Phase 9 settings and run

| Current evidence | Verified state / limit |
| --- | --- |
| Selected parent | Human-selected OneDrive N5080;154063cells;3.5ms film age; both source hashes match archived Phase7.2A Stage3 endpoint |
| Initial preservation | Previous Server6N45606 preserved as hashed localpair; Phase9child saved/reopened atN5080/3.5ms with originalbulk and upperfilm facets retained |
| Functional drain test | Matched seeded-film OFF/ON frozen-bulk test passed; directremoval3.99389454e-6kg versus matchedfilm loss3.99416087e-6kg, error0.0066684%; productionparent restored |
| Selected recovery checkpoint | Explicit N80580 / 42.35 ms; historical Courant peak 4.292395 remains recorded as an exceedance. Adoption does not make that historical block pass |
| Rejected selected step — earlier policy | Earlier 1 µs qualification from N60580 exceeded Courant 0.8 (peak 1.294363). Stronger-parent 1 µs test from N50580 stayed below 0.8 (peak 0.1086999) but failed the former inner gate. Inner-only rejection is superseded by the human revision; both saved pairs remain preserved |
| Current recovery | Human12October: from42.35ms. Preserve the interrupted 1 µs partial endpoint, reopen saved N80580 /42.35ms and continue at2.5 µs to100ms. Numerical diagnostics only; no automatic rollback. After laptop return, native idle confirmed at N71313. Partial pair saved, hashed and reopened at18.083ms; selected N80580/42.35ms pair hashes and reopened native clock verified. Host controller running from N80580/42.35ms. Native transcript prefix confirms13 film updates at2.5 µs,42.3525–42.3825ms; prefix Courant0.05881872–0.05879154. First10000-update target N90580/67.35ms;100ms completion remains pending |
| Scientific horizon |100ms totalfilm age; final95–100ms bulkactive; then angle213232cellcase after endpoint verification/preservation |
| Numerical evidence throughN9580 | Initialfourstages4500updates all met1e-5; peakCourant0.0003484,0.0001899,0.0066032,0.0356443 |
| Later accepted growth |0.1 µs qualification1000/1000 inner stops; five10000-update blocks reach16.35ms. Innerpass rates99.85%,95.08%,91.87%,100%,96.51%; growth acceptance did not enforce99%qualification gate |
| Production ledger | Corrected recoveryqualification4.84659% andfirstgrowth4.45531% errors remain diagnostic; rejected1 µsblock net ledger17.77577%. Independentfunctionaldrainproof does not establishproductionmassclosure |
| Supervision | Read-only desktopwatcher queues completion/failure. No solve replay from timeouts; Fluentpreserved; currentstate belongs tohostmanifest/nativeevidence |
| Claim limit | Changed geometry/mesh; no mesh-independence, steady-film or physical-validation claim;100ms and angle completion remain pending |


| Control | Verified child |
| --- | --- |
| Bulk physics and solver | Mixture / RNG / Coupled; feed 116.92 kg/s liquid and 80.69 kg/s vapor retained |
| Bulk correction | Surface-tension stored coefficient 0.04041000083088875 N/m; compressibility and drag-modification flags ON; nested contract matches after reopen |
| Roughness | 0.045 mm; Cs 0.5; physical `bottom` remains smooth |
| Film solve | Sequential; first-order implicit; 100 maximum subiterations; stop value 1e-5 |
| Film forces | Full momentum; gravity, gas shear, wall viscosity, advection, pressure, spreading and surface tension ON |
| Film surface tension | 0.04041 N/m; smoothing level 2, factor 0.5 |
| Particle mechanisms | Collection, splash, stripping and edge separation ON |
| Film wall scope | Original upper `wall` and lower collector `wall:004`; Flow Momentum Coupling OFF |
| Direct drain | Lower film mass and XYZ momentum sources; 1.5 ms capture time; 1% source-depletion limiter |
| Initial cadence | Fixed 0.1 µs; one film update per native iteration; profile interval 1; particles every 200 iterations |

| Evidence owner | Record |
| --- | --- |
| Runnable scientific intent | [Setup](setup.md) |
| Verified child | [Settings receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/slit154k-ewf-settings-current.json) |
| Preserved previous endpoint | [Preservation receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/preserved-before-load.json) |
| Exact loaded parent | [Parent receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/parent-loaded.json) |
| Code and command review | [Review receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/code-review.json) |
| Functional drain proof | [Probe receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/matched-drain-probe.json) |
| 100 ms transition | [Host deployment](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/target100-transition-deployed.json); [campaign order](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/campaign-request.json) |
| Lower-step recovery | [Deployment receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/resume-launch.json) |
| Network reconciliation | [Recovery receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/network-reconciliation.json) |
| Native production startup | [Startup observation](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/native-startup-observation.json) |
| Live supervision | [Current state](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/continuous-supervision.json) |
| Host controller | [Launch receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/host-launch.json) |
| Historical startup | [Phase 7.2A slit result](../../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/slit154k/results.md) |

| Artifact limit | Effect |
| --- | --- |
| Later N5290 pair | Unavailable on Server 6 and in the checked OneDrive inventory; not used |
| Field activation | The bulk `domains` readback updates after save/reopen; direct before-save audit was insufficient |
| Drain test scope | Artificial lower film seed tests native removal on this mesh; it does not establish production delivery to the collector |
| Detached retrieval | Windows-host controller active; desktop watcher reads every 30 s and queues completion or recovery events to this chat; notifications require the desktop and network to remain available |

| Recovery evidence | Observation / limit |
| --- | --- |
| 2.5 µs qualification | N9580 → N10580; 11.25 → 13.75 ms; all 1000 clocks observed; peak film Courant 0.04158824; inner-stop criterion passed 948/1000, below required 990; not accepted for continuation |
| Preserved failed pair | [Hash and transcript receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/failed-2p5us-proof.json) |
| Selected recovery | Healthy N9580 / 11.25 ms reopened after hash verification; reduce only timestep/cadence to 0.1 µs; preserve all other selected controls |
| Host dispatch | [Lowest-step launch receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/lowest-step-launch.json); [reconciled schedule](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/target100-lowest-step-plan.json) |
| Remaining work | 876500 updates from accepted N20580 / 12.35 ms to 100 ms; final 50000 updates cover 95–100 ms with bulk active; completion and angle transition remain pending |

| Report-source repair | Verified observation / limit |
| --- | --- |
| Numerical qualification | 0.1 µs qualification: 1000/1000 inner stops, peak Courant 0.000790655. First growth block: 9985/10000 inner stops, peak Courant 0.001499491; N20580 / 12.35 ms saved |
| Failure classification | Implementation: controller used original report filenames; Fluent changed filenames after checkpoint data reload |
| Correct source | Actual native files contain every coordinate N9581–N20580; [report-source receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/actual-report-sources.json) links preserved source copies |
| Corrected drainage ledger | Recovery qualification error 4.84659%; first growth error 4.45531%. Earlier qualification ledger used the stale failed-attempt file and is superseded by [corrected proof](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/recovery-0p1us-proof-reconciled-drain-proof.json). Production ledger remains unresolved; independent matched functional drain proof remains PASS |
| Recovery | Hash verified and reopened N20580. Lookup now follows live active per-iteration report definitions; resumes at the next block, same step/settings/horizon, without repeating completed updates |
| Deployment | [Repair launch](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/history-repair-launch.json); [resume plan](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/target100-history-repair-plan.json) |

| Human control revision | Selected intent / current gate |
| --- | --- |
| Authority11 October2026 | Fixed film step1 µs; film Courant operating ceiling0.8 |
| Native command preservation | Exact owned Python controller held; current native N60580→N70580 command and paired save remain active; no replay or Fluent termination |
| Safe boundary transition | [Reviewed Windows-host deployment](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/human-1us-transition-deployed.json) waits for native idle, reconciles clocks/transcript/live histories, hashes and reopens saved endpoint, then dispatches the revised controller |
| Control activation | First1 µs stage changes particle cadence to20iterations and drain refresh to1 µs; saves/reopens and reads back controls before1000-update qualification; inner100max/1e-5 unchanged |
| Expected counts | At expected N70580 /17.35ms boundary:77650 frozen updates to95ms and5000 bulk-active updates to100ms; expected finalN153230. Boundary and revised timestep activation remain pending |

| Growth6 failure /1 µs recovery | Evidence and decision |
| --- | --- |
| Native completion | N60580→N70580 at0.1 µs;10000 clocks finite; film16.35→17.35ms; saved case/data hashes verified |
| Numerical failure | Peak film Courant0.8694275 at16.6957ms exceeds revised0.8 ceiling;7364/10000 inner stops passed. Endpoint Courant fell to0.016464; this does not erase the transient peak |
| Preservation | [Failed block receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/failed-0p1us-growth6.json) and complete native transcript retained;1 µs transition stopped before control changes |
| Selected recovery | Restore last acceptedN60580 /16.35ms, test human-selected1 µs in separate1000-update qualification after save/reopen/readback. Exclude failed10000updates; no timeout replay |
| Revised nominal endpoint | 83650 further1 µs updates from16.35ms;78650 frozen to95ms,5000 active to100ms; nominalN144230. Acceptance and100ms completion remain pending |

|1 µs execution evidence | Observation / scope |
| --- | --- |
| Host controller | [Recovery launch](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/human-1us-recovery-launch.json); running qualification N60580→N61580 |
| Native advancement | [Transcript-prefix observation](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/human-1us-native-startup.json):39 accepted clocks16.351–16.389ms, each1 µs; first/last prefix Courant0.102007/0.111718 |
| Claim limit | Confirms revised timestep startup after control save/reopen; does not establish latest live clock, completed qualification or100ms endpoint |

|1 µs qualification failure /lower recovery | Observation / decision |
| --- | --- |
| Completed trial |1000updates N60580→N61580,16.35→17.35ms; selected1 µs and0.8ceiling |
| Rejection | PeakCourant1.294363;786/1000 inner stops passed. Both criteria fail;1000updates excluded from acceptedfilm age |
| Preservation | [Failed qualification record](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/failed-1us-qualification.json); localpaired endpoint hashes and complete transcript retained |
| Lower-level recovery | Restore lastacceptedN60580 /16.35ms;0.1 µs with0.8ceiling and existing100max/1e-5inner controls;1000updates to16.45ms then3000-update qualification to16.75ms, covering prior transientfailure window |
| Continuation gate | Both blocks require≥99%inner stop passes and Courant≤0.8 before long growth; requested1 µs has not qualified.100ms and angle transition remain incomplete |

| Lower-step startup evidence | Verified scope |
| --- | --- |
| Native0.1 µs recovery | [Prefix receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/recovery-from1us-0p1-native-startup.json):51clocks16.3501–16.3551ms,0.1 µs each; prefixCourant0.010196–0.010222 |
| Qualification state | Running first1000-update check; prefixestablishesstartup only, notlatestliveclock orqualifiedendpoint |

| Lowerqualification failure /strongerparent recovery | Verifiedevidence /controlleddelta |
| --- | --- |
| Loweststeprejection |0.1 µs qualificationN60580→N61580,16.35→16.45ms;peakCourant0.01114965;752/1000innerpasses. All248rejectedupdates reached100subiterations; lowCourantdoesnotestablishinnerconvergence |
| Failedpair/trace |[Reconciliation](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/lowest-step-inner-failure-reconciliation.json); fulltranscript andpairhashes retained |
| Untrackedprogress |NativeN66580 observedwhilehostcontrollerterminalat61580; subsequentstableclock16.95ms. Hostautosaves62000–66000 exist, noownedPythoncontroller found. [Liveendpointpreserved](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/untracked-native-state-preserved.json); extra5000nativeincrements excludedfromqualifiedlineage |
| Strongerparent |N50580 /15.35ms,precedingblock10000/10000innerpasses,peakCourant0.001617383. Excludesformerlyacceptedbutunderqualifiedgrowth5 fromrebuiltpath; earlierunderqualifiedblocks remainhistorical limitation |
| Controlledretry |Changeonlystartingpairtoearlierstrictparent andapplyhuman1 µs step; keep100max/1e-5/Courant0.8 andphysics. Two1000-updategates to16.35 and17.35ms precedelonggrowth; nominalfinalN135230;95–100msbulkactive |

| Execution from earlier qualified parent | Evidence / limit |
| --- | --- |
| Native 1 µs startup | [Prefix receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/strict-parent-1us-native-startup.json): 113 clocks from 15.351 to 15.463 ms at 1 µs; first/last prefix Courant 0.014375/0.014355 |
| Qualification state | First 1000-update check is running. This confirms startup after control save/reopen; it does not establish a completed qualification or latest live clock |

| Stronger-parent 1 µs result | Evidence / decision |
| --- | --- |
| Native and controller state | Terminal controller BLOCKED; native idle N51580 / 16.35 ms agrees with transcript and saved pair |
| Numerical gate | 954/1000 inner stops passed; required 990. All 46 rejections hit 100 inner iterations. Peak Courant 0.1086999 ≤0.8 does not establish inner convergence |
| Preservation | [Failed pair hashes, live state and inner rows](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/strict-parent-failed-1us-reconciliation.json); complete native transcript retained |
| Controlled recovery | Restore N50580 / 15.35 ms; test recorded 0.1 µs level from this earlier parent, not the failed N60580 route. Keep physics, 100 max inner iterations, 1e-5 stop and 0.8 ceiling |
| Next gates | 1000 updates to 15.45 ms, then 13000 to 16.75 ms; both require ≥99% inner passes. The second spans the earlier failure/spike interval |
| Review | [Code and command review](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/strict-parent-0p1-code-review.json) |

| Recovery startup | Observed native evidence / limit |
| --- | --- |
| 0.1 µs step | [Native prefix](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/strict-parent-0p1-native-startup.json): 37 film rows, 15.3501–15.3537 ms, fixed 1e-7 s; prefix Courant 0.001437381–0.001437828 |
| Controller | RUNNING, strict-parent-0p1-proof, target N51580; parent N50580 / 15.35 ms verified/reopened; controls saved/reopened before solve |
| Limit | Startup confirmed; qualification and 100 ms completion remain pending. Prefix is not the latest live clock |

| Human numerical acceptance revision | Decision / limit |
| --- | --- |
| Accepted rule | Courant ≤0.8 only. Earlier inner-stop rejections remain recorded evidence, but the inner pass fraction is no longer a continuation gate |
| Solver controls | 100 max inner iterations / 1e-5 retained. Residuals and film ledgers remain diagnostic, with no convergence or closure claim implied by acceptance |
| Implementation | Hold only owned Python runner; preserve the in-flight 13000-update native journal to N64580 / 16.75 ms. Reconcile its saved pair, transcript and Courant before fixed 1 µs continuation; no solve replay |
| Review | [Reviewed policy and transition](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/courant-only-code-review.json) |

| Human N70580 / 2.5 µs revision | Evidence / decision |
| --- | --- |
| Authority | Continue from N70580 with 2.5 µs; reach 100 ms wall-film time |
| Selected saved pair | [Original N70580 receipt and hashes](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/failed-0p1us-growth6.json) |
| Superseded run | Owned waiting controller cancelled; native old command cleanly interrupted. Native clock settled after interruption; first save retained, then stable partial pair saved/reopened before replacement |
| Continuation | 33060 new updates: 31060 frozen to 95 ms, then 2000 bulk active to 100 ms. No inner or ledger acceptance gate |
| Review | [Exact control and continuation review](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n70580-2p5us-code-review.json) |

| N70580 continuation startup | Verified evidence / limit |
| --- | --- |
| Selected parent | N70580 / 17.35 ms pair hashes verified, native coordinates and bulk contract read back after reopen |
| Controls and startup | [Native prefix](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n70580-2p5us-native-startup.json): 26 film rows at fixed 2.5 µs, 17.3525–17.4150 ms; first/last prefix Courant 0.4098856 / 0.3513399. Control activation saved/reopened before solve |
| Active controller | RUNNING; first 10000-update command targets N80580 / 42.35 ms. Scheduled final N103640 / 100 ms remains pending |
| Preservation | [Old partial N56958 / 15.9878 ms saved/reopened](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n70580-partial-preservation.json); native journal interruption not replayed |
| Claim limit | Prefix proves startup, not latest live clock or completed endpoint. Parent historical Courant exceedance remains recorded; inner/ledger acceptance gates removed |

| N80580 failure reconciliation | Verified evidence / decision |
| --- | --- |
| Controller failure | Empty certutil hash output interrupted verification after the native solve. This file-output error alone does not justify replay or a step change |
| Native completion | N80580 / 42.35 ms, 10000 finite film-clock rows at fixed 2.5 µs, schedule matches and no fatal transcript lines |
| Independent numerical failure | Full-transcript peak Courant 4.292395 >0.8. End Courant 0.0588193 does not negate the exceedance; step reduction is based on the peak |
| Preservation | [Host transcript and paired hashes](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n80580-host-native-summary.json); full native transcript retained locally and on the host |
| Inner diagnostics | 2240/10000 met 1e-5; this count is recorded only and does not block continuation |
| Hash repair | [Known case/data match](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n80580-hash-repair-proof.json); Server 6-only PowerShell hashing replaces fragile certutil output |
| Recovery | Reopen selected N70580 / 17.35 ms, lower 2.5→1 µs with DPM20 and drain refresh1 µs, save/reopen controls. First10000 fixed updates, no extra qualification gate; final95–100ms bulk active |
| Review | [Code and recovery review](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n70580-1us-recovery-code-review.json) |

| Lower-step recovery startup | Verified evidence / limit |
| --- | --- |
| Native startup | [Observed prefix](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n70580-recovery-1us-native-startup.json): 15 rows at fixed 1 µs, 17.351–17.365 ms; first/last prefix Courant 0.1643737 / 0.1603146 |
| Controller | RUNNING; first10000-update block targets N80580 / 27.35 ms. Control pair saved/reopened and hashed through the repaired lane-only path before solve |
| Horizon | Scheduled 100 ms / N153230, final95–100ms bulk active; completion pending. Prefix confirms startup only |

| Human continue-to-100 ms revision | Decision / limit |
| --- | --- |
| Authority | No, keep running to100ms —12October2026 |
| Numerical checks | Courant/inner/ledger values become diagnostics only; threshold0.8 recorded without automatic stop/rollback. Earlier exceedances remain historical evidence |
| Execution | Hold only owned Python runner; native in-flight1 µs command and saved endpoint continue. Boundary handoff removes numerical gates before subsequent commands |
| Claim limit | Reaching100ms establishes the requested clock horizon; it does not establish numerical convergence, mass closure, steady film or physical validity |
| Review | [Controller and handoff review](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/continue100-code-review.json) |


| Human-selected 42.35 ms continuation | Evidence / limit |
| --- | --- |
| Selected endpoint | N80580 / 42.35 ms; archived case and data hashes in [native pair summary](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/n80580-host-native-summary.json) |
| Native control | Superseded owned boundary waiter cancelled. Native interrupt submitted once; no solve replay. After laptop return, idle confirmed; stable N71313 /18.083ms partial pair saved, hashed and reopened |
| Pending handoff | [Host launch receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/from4235-2p5us-launch.json): source hashes unchanged from review; selected parent reopened and reconciled; host controller dispatched once after verified partial preservation |
| Remaining schedule | 10000 + 10000 + 1060 frozen updates at 2.5 µs to 95 ms; 2000 bulk-active updates to 100 ms / N103640 |
| Limit | Native 2.5 µs startup is confirmed by transcript prefix; 100 ms completion is pending. Courant, inner residuals and ledgers remain diagnostics; no automatic numerical rollback |


| Resumed native execution | Verified observation / scope |
| --- | --- |
| Controller | RUNNING; from4235-2p5us-growth-1; next endpoint N90580 /67.35ms |
| Native startup | [Prefix receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/from4235-2p5us-native-startup.json):13 film rows,42.3525–42.3825ms, fixed2.5 µs; first/last prefix Courant0.05881872/0.05879154 |
| Preserved partial | [Save/hash/reopen receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/from4235-partial-preservation.json): N71313 /18.083ms; prior interrupt reconciled, no duplicate interrupt or solve replay |
| Limit | Prefix proves startup, not latest live clock or a completed block.100ms completion and final95–100ms bulk-active stage remain pending |
