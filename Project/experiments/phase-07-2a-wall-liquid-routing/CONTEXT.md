# Phase Context — Phase 7.2A Wall-Liquid Routing and Steam-Outflow Carryover

## Stage 4 — EWF settings and wall parameters

| Item | Current contract |
| --- | --- |
| Human direction — 7 October 2026 | Record the commercial-steel result as Stage 4; use the Stage 3 startup method for the next Stage 4 cases |
| Stage 3 position | Human is satisfied with Stage 3 as the method/reference stage; preserve its evidence and existing claim limits |
| Stage 4 goal | Assess changed EWF settings and wall parameters using the same low-feed activation and inlet-ramp pattern |
| Startup sequence | Low inlet loading → Coupled + EWF activation → low-feed hold → inlet ramp → short full-feed hold → freeze bulk equations → EWF-only development |
| Method references | [Early-EWF startup](stage-03-shortened-reconstruction/early-ewf-startup/setup.md); [film-development](stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md) |
| Configurable scope | EWF settings and wall parameters may differ substantially from Stage 3; record selected values and controlled changes per case |
| EWF-only direction — 7 October 2026 | After the short full-loading hold, retain bulk/film fields and film clock; freeze bulk equation advancement and advance EWF alone |
| Frozen-flow interpretation | Bulk inventory/outlet flux are held-field diagnostics; continuity has no new solved rows; film inventory and accretion/drainage continue to evolve |
| Film claim boundary | A steady film under frozen bulk forcing does not establish a stationary fully coupled separator |
| User-nominated reference | [Solve EWF Transiently](chatgpt-conversation://6ac5733b-48a4-83ec-9e11-23e6902b1d24); conversation not retrieved in this session; exact settings not imported |
| Other model basis | Retain Stage 3 geometry/mesh and model basis unless the human changes the scope |
| Selected continuation | Human-selected current N29815 commercial-steel parent; all settings in [selected setup](stage-04-ewf-wall-parameters/realism-continuation/setup.md); 2000 bulk-and-film iterations, then +50 ms EWF-only, target 15 microseconds |
| Completed first Stage 4 evidence | Commercial steel 0.045 mm continuation; N25815 → N29815; 4000 updates; 4 ms added film time |
| Completed retry — 7 October 2026 | Human selected Flow Momentum Coupling OFF; other selected settings ON; exact N29815 restart; 4000 bulk updates verified to N33815; +50 ms EWF-only verified to N37149; film still filling; [retry result](stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md) |
| Selected-mechanism continuation status | All initial target flags read back and reopened; feedback-ON probes FPE at N29827 and N29829; control recovered; feedback-OFF requested horizon complete; [results](stage-04-ewf-wall-parameters/realism-continuation/results.md) |
| Continuation result | Outlet-flux magnitude falls 19.72%; bulk mass rises 1.20%; EWF mass rises 1.42% |
| Final-500 film rates / continuity | Accretion 92.329 kg/s; drainage 68.247 kg/s; storage 24.087 kg/s; continuity mean 1.846e-3 |
| Required diagnostics | Bulk liquid inventory; phase-2 steamoutlet boundary flux; EWF liquid inventory; film accretion/drainage rates; continuity |
| Evidence standard | Native histories with actual iteration/film time, report/source definitions, accepted-step and film-ledger checks, explicit parent and paired restart proof |
| Claim limits | Existing result combines lower roughness, restored bulk equations and changed film step; film remains filling; no isolated roughness-benefit claim |
| Compute / session boundary | Current human instruction authorizes Server 1 continuation from loaded N29815; no initialization; preserve local parent and other active stages' sessions |
| Owning records | [Stage 4 index](stage-04-ewf-wall-parameters/index.md); [startup design](stage-04-ewf-wall-parameters/setup.md); [results](stage-04-ewf-wall-parameters/results.md) |

## Local re-entrainment speed sensitivity — 6 October 2026

| Item | Current contract |
| --- | --- |
| Human direction | Three local cases at 20.11, 26.81 and 32.14 m/s; same Stage 3 startup and film-development method |
| Current authority | Human stopped the campaign on 6 October 2026; current 26.81 m/s endpoint saved at N6080 / 4.000 ms EWF time; Fluent closed and monitoring paused; no continuation authorized |
| Selected features | Particle Splashing, Edge Separation and Particle Stripping on; Source Smoothing retains inherited off |
| Horizon | Each case reaches approximately 250 ms actual EWF time from dry activation |
| Invariants | 60,964-cell mesh; R3/contact absorber; materials; film wall scope; other physical settings |
| Local authority | `direct-fluent-use`, HOME-DESKTOP-SH, Fluent 2025 R2 Student, four ranks; no remote-server changes |
| Settings proof | Official v252 guide and Figures 30.1 / 30.9; explicit TUI responses, native readback and save/reopen |
| Claim limit | Bounded speed sensitivity; frozen bulk development remains labelled; steady film is not a stop gate |
| Exact contract | [Setup](stage-03-shortened-reconstruction/early-ewf-startup/reentrainment-speed-sensitivity/setup.md) |

## Vertical-slit film development on Server 3 — 6 October 2026

| Item | Current contract |
| --- | --- |
| Human direction | Develop the wall film as far as numerical evidence supports; continuously supervise the run |
| Authority | Overwrite Server 3; supersedes the historical N10000 case found idle on 6 October |
| Preserved previous endpoint | Historical N10000 case/data saved and hashed on local FluentRuns disk before replacement |
| Selected parent | Verified 154k vertical-slit N5080 startup pair, 3.5 ms film clock; no bulk or film initialization |
| Fixed science | Parent mesh, full inlet loading, R3 roughness, corrected contact absorber, phase accretion, wall scope and DPM |
| Initial result | Full-bulk 1 µs ×100 probe passes: 100% inner-film residual tolerance, CFL 0.002945, film ledger error 0.000012% |
| Next numerical contrast | Original implicit solver, 0.5 µs ×1000 versus 5 µs ×100 at identical frozen N5080 bulk fields |
| Qualification | Actual native film time, complete inner residuals, film accounting, facet mass/thickness/velocity, paired local saves and reopen |
| Full-model requirement | Restore all original bulk equations before any steady-film claim |
| Contract owner | [Vertical-slit film-development setup](stage-03-shortened-reconstruction/early-ewf-startup/slit154k/film-development/setup.md) |
| Machine state | [Continuation manifest](../../../PyAnsys/output/phase72a-stage3-slit154k-film-development-server3/20261006/run-manifest.json) |
| Other server | Server 1 remains separate; its film-development results are method evidence, not this mesh's qualification |

## Supplied vertical-slit mesh repeat on Server 3 — 5 October 2026

| Item | Current contract |
| --- | --- |
| Human direction | Repeat the completed Stage 3 early-EWF startup on `Separator-vertical-slit-154k.msh.h5`; use Fluent native settings transfer |
| Session authority | Full ownership and replacement of Server 3 explicitly granted; supersedes its Stage 2 continuation placement |
| Reference | Exact prepared A case/data at N1580 from completed Server 1 early-EWF startup |
| Selected delta | Supplied 154,063-cell vertical-slit geometry and mesh; required collector partition and boundary correspondence |
| Settings | Native Replace Mesh; separate native injection transfer; readback and paired save/reopen before solve |
| Startup | Same 500-update low-feed hold, 2,000-update ramp and 1,000-update target hold; fixed 1 µs film step |
| Previous endpoint | Server 3 N46806 preserved locally before replacement |
| Status owner | [Supplied-mesh setup](stage-03-shortened-reconstruction/early-ewf-startup/slit154k/setup.md) and [results](stage-03-shortened-reconstruction/early-ewf-startup/slit154k/results.md) |
| Machine state | [Run manifest](../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/run-manifest.json) |
| Comparison limit | Geometry and mesh change together; mapped A fields differ from exact historical A arrays; no mesh-convergence claim |
| Server 1 | Its separate film-development lane remains under its own authority |

## Stage 2 continuation on Server 3 — 5 October 2026

| Item | Current contract |
| --- | --- |
| Human direction | Continue verified N45606; increase adaptive EWF stepping to seek accretion–drainage convergence |
| Authority | Full ownership of Server 3 for this continuation; supersedes its Stage 3 placement |
| Parent / model | Developed Stage 2 R3 + E2.7 with corrected contact absorber; exact N45606 fields |
| Preservation | Save/reopen Stage 3 N8000 before replacement |
| First numerical delta | Courant target 0.15; accepted 6.415943 µs; incomplete inner-film convergence |
| Selected numerical recovery | Larger-step probes preserved at N45906; restart exact original N45606 with target 0.06 and 30 allowed film subiterations |
| Confirmed human target | Steady film: retained film mass may be nonzero; inventory growth should approach zero |
| Evidence | Actual accepted steps, film clock, all EWF inner residuals, inventories, accretion/drainage and film ledger |
| Run plan | 100-update probe; 1,000-update batches; bounded 0.2 s corrected-restart film horizon |
| Recovery | Preserve unstable endpoints; repair numerics within this authority |
| Contract | [Server 3 aggressive continuation](stage-02-combined-ewf-roughness/aggressive-server3/setup.md) |
| Other lane | Stage 3 Server 1 startup remains separate |
| R5 | Cancelled |

## Stage 3 early Coupled/EWF startup — 5 October 2026

| Item | Current contract |
| --- | --- |
| Human question | Reduce the inlet-loading spike by enabling Coupled and EWF at historical A, then holding low feed for 500 updates |
| Selected model | R3 roughness and corrected contact absorber from A |
| Placement / authority | Server 1; full ownership explicitly granted for this Stage 3 run |
| Exact parent | Hash-verified historical A case/data at N1580; retain original bulk fields |
| Startup | 500 updates at 25% feed; original 2000-update ramp; 1000-update full-feed persistence hold |
| Film | Dry start at A; fixed 1 µs throughout; current E2.7 coupling and wall scope |
| Preserved previous work | Save current Server 1 N45606 before replacement; Server 3 branch remains separate |
| Comparison | Ramp progress and equal inlet loading; raw carrier excursions, bulk + film storage, carryover and inner-film convergence |
| Status | Startup N5080 complete and reopened; 31 reports and all 3500 new residual/film records verified; live Server 1 now belongs to film development |
| Startup result | Ramp continuity peak 70.15% lower; combined inventory peak 70.43% lower; carryover peak 75.78% lower |
| Numerical limit | Activation spike remains; 15 final inner-film failures at N5025–N5076; film remains developing |
| Result | [Early EWF results](stage-03-shortened-reconstruction/early-ewf-startup/results.md) |
| Further compute | Human selected accelerated, numerically adequate film development; [continuation contract](stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md) |
| Film-development status | Human instruction on 6 October 2026: keep Server 1 running; reference, lowest and highest Phase 8 nominal inlet speeds to 500 ms film time; continuous monitoring. Reference resumes N25815; low/high repeat the same prepared-A startup with scaled feeds, then develop film under their own frozen bulk fields. Student-server transfer is superseded; preserved OneDrive pair remains available. [Campaign setup](stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/setup.md), [results](stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md). |
| Exact contract | [Early EWF setup](stage-03-shortened-reconstruction/early-ewf-startup/setup.md) |
| Machine evidence | [Run manifest](../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/run-manifest.json) |
| Claim limit | Combined finite startup recipe; no isolated timing, steady-film or whole-separator qualification |

## Stage 3 reconstruction authority — 5 October 2026

| Item | Current contract |
| --- | --- |
| Human goal | Test a shorter startup that reproduces the current model; prepare for later mesh convergence |
| Authority | Full ownership of Server 3 for Stage 3 |
| Relation to Stage 2 | Separate reconstruction lane; Server 1 adaptive-film continuation remains separate |
| Scientific scope | Existing approximately 60k mesh and exact current physical model |
| Reference selected for verification | Corrected R3/contact N33586; independent local four-rank developed endpoint |
| Reference limit | Film remains developing; no stationary-film or full-separator qualification |
| Startup | Coupled and R3 from start; 1500 updates at 25% feed, ten 100-update loading steps, 500 updates at target with film equations off |
| Target feed | Verified reference mass flows: liquid 116.92 kg/s; vapor 80.69 kg/s |
| Low feed assumption | 25% of each target, from the parent startup precedent |
| Film screen | Initialize EWF after 3000 bulk updates; fixed 1 µs and adaptive arms from the same dry-film parent |
| Adaptive candidate | Initial 1 µs; Courant target 0.1; increase 1.2; decrease 2.0 |
| Comparison | Actual elapsed film time; predeclared scalar tolerances plus accounting and spatial evidence |
| Checkpoints | Paired local saves every 1000 updates; final saved endpoint reopen |
| Deliverable | Tested reconstruction recipe, measured cost and claim limits |
| Later mesh family | Conditional on existing-mesh reproduction evidence; preserve physical collector extent and wall treatment |
| Exact run contract | [Stage 3 setup](stage-03-shortened-reconstruction/setup.md) |
| Evidence/status | [Stage 3 results](stage-03-shortened-reconstruction/results.md) |
| Stage 3 screen outcome | N6000 screen complete; carrier snapshot screen passes; developed-film reproduction fails |
| Authorized continuation | N6000–N8000 complete; accepted step 3.713 µs; film time 10.416 ms; ledger error 0.000907%; Server 3 saved/reopened and idle |
| Current interpretation | Carrier snapshot close; film inventory 14.09% of developed reference; continuity 0.089159; no further solve selected |

## Current authority and adaptive test — 5 October 2026

| Item | Current contract |
| --- | --- |
| Goal | Reach steady film; test adaptive EWF steps to advance film time faster |
| Authority | Full ownership of Server 1; supersedes earlier Server 1 restrictions |
| Selected model | Stage 2 R3 + E2.7 with corrected contact absorber |
| Parent | Independent local four-rank N33586 endpoint; retain its lineage |
| Shared source files | Case, data and contact-library archive downloaded on this Mac; all hashes match source manifest |
| Server 1 | Full connection helper attached to fresh Fluent 2025 R2 session; N33586 loaded |
| Destination files | Case/data/library hashes verified on Server 1; copied to local FluentRuns disk |
| Execution | Recovered and analysed N45606; controller stopped after gRPC timeout; requested 50 ms horizon incomplete |
| Next action | Preserve N45606 as reference; Server 1 now owns the Stage 3 early-EWF startup test |
| Controlled delta | Adaptive EWF stepping; keep roughness, absorber, DPM and bulk controls fixed |
| Adaptive controls | Initial step 1 µs; increase factor 1.2; decrease factor 2; Courant target 0.05 |
| Maximum-step limit | No separate native upper bound verified; do not call timestep-max an adaptive ceiling |
| Current evidence | 12,020 updates; accepted step 1.728 µs; peak CFL 0.026604; film ledger error 0.004799% |
| Film stationarity | Not reached; last 1,000-update storage 8.2017 kg/s; drainage deficit 9.9767% |
| Film clock | Native endpoint 0.120769016 s; total corrected-restart added time 0.040769016 s |
| Continuation | Large TUI batches; local checkpoints; staged cumulative film horizons 0.05, 0.1 and 0.2 s when stable |
| Required time evidence | Actual accepted film steps and their sum; never iteration count times upper bound |
| Steady-film evidence | Sustained near-zero inventory growth and accretion–drainage agreement, with film ledger closure |
| Diagnostic cap | Retain 1 m; no cap-based steady-state claim |
| R5 | Cancelled |
| Initial access receipt | [Preflight](../../../PyAnsys/output/phase72a-adaptive-preflight/20261004T225805Z/preflight.json) |
| Current run evidence | [Adaptive manifest](../../../PyAnsys/output/phase72a-adaptive-server1/20261005/run-manifest.json) |
| Completion and return to this chat | [50 ms stage job](../../../PyAnsys/output/phase72a-adaptive-server1/20261005/stage-50ms-job-manifest.json) |

## Previous fixed-step continuation



| Current local continuation | Verified setting or state |
| --- | --- |
| Human-selected execution | `direct-fluent-use`, HOME-DESKTOP-SH, Fluent 2025 R2 Student, 4 ranks |
| Available parent | Hash-verified local N17586 case/data pair |
| Missing checkpoint | Server 1 N23586 pair was not synced; remote access is blocked |
| Recovery | Replay 6,000 updates locally to N23586 |
| Requested extension | Then submit `/solve/iterate 10000`, targeting N33586 |
| Total horizon | 20,000 updates from original E2.7 N13586 |
| Film timestep | Fixed 1e-6 s; scientific settings unchanged |
| Verification | Parent fields and all seven state groups matched; prepared pair reopened exactly |
| Execution proof | Native solve progressed beyond N17586; N17670 recorded during startup check |
| Checkpoints | Native paired autosaves every 1,000 updates on local disk |
| Follow-up | One check in four hours; no continuous status queries |
| Lineage limit | Independent 4-rank replay; does not reuse Server 1's unavailable 18-rank N23586 fields |
| Server 1 | Left untouched during the local run; prior queued command remains unverified |
| Machine evidence | [Local run manifest](../../../PyAnsys/output/phase72a-contact-absorber-local-20000/20261004T081120Z/run-manifest.json) |

**Previous Server 1 continuation:** Submit one `/solve/iterate 10000` command
on Server 1 from N23586, retain the 1 microsecond film step and all scientific
settings, and leave the session running without constant monitoring. Target
N33586, for 20,000 restart updates. The asynchronous command was acknowledged
at 08:52 UTC on 3 October, but stalled service reads leave actual solve start
unconfirmed. A single check is scheduled for 12:54 UTC; reconcile native state
before any further submission and preserve the endpoint if complete.

**Continuation result:** All 6,000 added updates completed at N23586,
giving 10,000 updates at 1 microsecond. Film maximum is 0.291141 mm and
inventory is 6.013528 kg; continued accumulation means no stationary film
within this horizon. The full film ledger closes within 0.016725%.
Six remote paired checkpoints are saved and hashed. Final native case/data
reads returned and printed film reports match, but full settings verification
and shared transfer are blocked by an unresponsive Server 1 service.
No further updates were run and the solver was not terminated. See the
[longer-film evidence](stage-02-combined-ewf-roughness/results.md#contact-absorber-10000-updates-at-1-microsecond).

**Latest human continuation — 2026-10-03:** Server 1 is now explicitly
authorized for another 6,000 updates of the corrected R3/contact arm at a
fixed 1e-6 s film timestep. Continue the verified thin-film N17586 pair to
N23586, for 10,000 updates from original E2.7 N13586 and 0.01 s added film
time. Change no scientific controls; preserve Server 1's existing endpoint
before replacement and leave its session open afterward. Record every
iteration and paired checkpoints every 1,000 updates. Judge film thickness,
inventory, accretion and drainage trends across consecutive 1,000-update
windows; check film mass closure and residuals. Thickness alone cannot prove
steady film. Earlier Server 1 restrictions are superseded for this run;
R5 remains cancelled. The 10 microsecond failed arm remains separate evidence.

| Item | Status |
| --- | --- |
| Latest human timestep match — 2026-10-03 | repeat the original-E2.7 |
| — | N13586 restart with fixed EWF timestep 1e-5 s, matching E2.7, for |
|  | 4,000 iterations to N17586 |
|  | Change only the film step relative to the |
|  | corrected contact restart; keep bulk tau=1e-5 s, fraction relaxation=0.1, |

<details>
<summary>Supporting detail — Status</summary>

| Item | Status |
| --- | --- |
| — | R3 roughness and all new absorber settings |
|  | Preserve an early N13686 |
|  | checkpoint, then every 1,000 iterations; retain numerical failure evidence |
|  | without reducing the requested timestep |
|  | Evidence: |
|  | `PyAnsys/output/phase72a-contact-absorber-e27-timestep/20261003T050619Z/run-manifest.json` |
| Completed N13586–17586; all 4,000 native film steps | were 1e-5 s |
| — | The film |
|  | CFL first exceeded one at N13773 and thickness reached the 1 m diagnostic |
|  | cap at N13776 |
| Final reported film inventory | is 6305.274 kg; film-side |
| — | closure fails by 1.648e6% |
|  | The saved endpoint reopened exactly and all |
| owned sessions | are closed |
| This arm | is scientifically rejected |
| — | The |
|  | earlier thin-film result depends on timestep and cannot be attributed |
|  | solely to absorber changes |
|  | See the |
|  | [timestep-matched result](stage-02-combined-ewf-roughness/results.md#contact-absorber-with-e27-timestep) |
| Latest human restart — 2026-10-03 | run R3 + the corrected contact absorber |
| — | for 4,000 iterations starting directly from the original E2.7 endpoint |
|  | N13586, before the historical roughness branch reached its 0.3 m film cap |
| Original maximum film thickness | is 0.30979 mm |
| — | Target N17586; retain the |
|  | selected tau=10 microseconds, film step=1 microsecond and volume-fraction |
|  | relaxation=0.1 |
|  | Restore original E2.7 solution fields, preserving the new |
|  | absorber/R3 settings; do not use N14686 or N18686 solution fields |
|  | `PyAnsys/output/phase72a-contact-absorber-e27-restart/20261003T032636Z/run-manifest.json` |
|  | Completed N13586–17586 with exact original bulk/film array verification, |
|  | prepared-parent reopen, four local checkpoints and exact final reopen |
|  | Maximum film thickness decreased to 0.298108 mm; collector inventory is |
|  | 0.609 g and maximum liquid fraction 0.02605% |
|  | Film-side closure error is |
| 0.007668%, while steady bulk convergence/joint closure | remain unqualified |
| All three owned local sessions | are closed |
| — | [original E2.7 restart result](stage-02-combined-ewf-roughness/results.md#contact-absorber-restart-from-original-e27) |
| Human continuation — 2026-10-03 | continue the verified corrected R3 + |
| — | E2.7 contact-absorber endpoint N14686 for 4,000 additional iterations to |
|  | N18686, with no model/control change |
|  | Use local direct Fluent, with paired |
|  | checkpoints every 1,000 iterations |
|  | `PyAnsys/output/phase72a-contact-absorber-continuation/20261003T001729Z/run-manifest.json` |
|  | Completed all 4,000 iterations and exact fresh-session endpoint readback; |
| both owned local sessions | are closed |
| Final collector inventory | is 0.658 g, |
| — | maximum liquid fraction 0.02284%, and maximum film thickness 0.29443 mm |
|  | (previously 0.30806 mm) |
|  | Film inventory increased by 0.07132 kg; film-side |
| ledger error | is 0.007632% |
| — | Bulk removal and residuals still fluctuate, so |
| steady convergence and whole-separator closure | remain unqualified |
| — | [continuation result](stage-02-combined-ewf-roughness/results.md#contact-absorber-4000-iteration-continuation) |
| Active human absorber change — 2026-10-03 | replace the shared-throughput |
| — | collector with independent capture of bulk liquid, EWF and liquid DPM on |
|  | entry to the existing lower y<=0.10 m cell-centre-selected region |
|  | [contact-capture setup](stage-02-combined-ewf-roughness/ewf-absorber/setup.md#active-contact-capture-trial) |
|  | owns the conservative implementation and stability screen |
|  | Use the preserved |
|  | thin E2.7 N13586 parent, local `direct-fluent-use`, no Server 1 and no R5 |
|  | Bulk finite-time depletion must be identified as an approximation; native |
|  | film-edge outflow and DPM escape must have independent removal accounting |
| prior completed shared-budget comparison below | remains historical |
| — | The corrected local contact prototype has now completed N13686–14686 and |
| exact saved-endpoint readback; its owned session | is closed |
| — | Collector max |
| liquid fraction | is 0.02265%, film max thickness 0.30806 mm and film-side |
| — | closure error 0.007505% |
|  | DPM contact and non-entry controls passed |
|  | Bulk |
|  | source variation, inventory drift and residual plateaus leave steady and |
|  | whole-separator qualification unresolved |
|  | [bounded trial result](stage-02-combined-ewf-roughness/results.md#all-liquid-contact-absorber-trial) |
| Latest execution override — 2026-10-03 | the human selected local |
| — | `direct-fluent-use` for R3 + E2.7 with the new shared bulk/EWF absorber, |
|  | 3,000 iterations from N13586 to N16586 |
|  | Do not work on Server 1 |
|  | This |
|  | supersedes the earlier fleet/no-direct-use instruction for current work |
|  | Retain the recent old-absorber R3 test's 1 m cap, roughness and E2.7 controls |
| for the matched comparison; the 0.3 m result | is secondary evidence |
| Fluent execution from now | uses this local workflow until the human changes it |
| requested run | is now complete to N16586 with verified final files and the |
| — | owned local session closed |
|  | The [matched result](stage-02-combined-ewf-roughness/results.md#r3-new-absorber-direct-comparison) |
|  | shows 3.84% lower late combined film inventory but 3.69 times higher liquid |
| carryover; the film | remains metre-cap-censored and numerically unphysical |
| Human absorber extension — 2026-10-03 | extend the lower numerical absorber |
| — | to remove EWF liquid as well as bulk phase-2 liquid |
|  | The [shared collector |
|  | setup](stage-02-combined-ewf-roughness/ewf-absorber/setup.md) owns the new |
|  | controlled change and combined mass budget |
|  | The completed R3/R4 1 m cap tests |
|  | remain preserved comparison evidence; do not use their unphysical endpoints |
|  | as the implementation parent |
| No R5 run | is authorized |
| Native source operation | was verified in a paired isolated check; earlier R3/R4 |
| — | collector preparation passed save/reopen and roughness/source readback on |
|  | Server 1 |
| Those fleet preparation receipts | are historical, not current live |
| — | status |
|  | [extension result](stage-02-combined-ewf-roughness/results.md#ewf-absorber-extension--3-october-2026) |
|  | distinguishes that implementation proof from the completed local R3 screen |
|  | and its unresolved physical accumulation/transport interpretation |
| Human mechanism preference — 2026-10-03 | prefer measured film drainage |
| — | and release back into the flow so that liquid can both enter and leave EWF |
| A hard thickness limit | is a last resort, not the intended removal mechanism |
| 1 m tests | remain diagnostic comparisons |
| — | The next mechanism design must |
|  | audit native film-edge outflow and distinguish shear stripping from edge |
|  | separation, with explicit source/destination mass and momentum accounting |
|  | Do not interpret release driven by the current unphysical film velocities as |
|  | validated physical entrainment |
| Human follow-up — 2026-10-03 | before the newly authorized Stage 2 |
| — | inlet-speed / one-way-DPM / two-way-DPM sensitivity sequence, repeat R3 and R4 |
|  | Stage 2 roughness children with the maximum film-thickness limit raised only |
|  | from 0.3 m to 1.0 m |
| Servers 1 and 3 | are owned for this work; do not invoke |
| — | `direct-fluent-use` |
|  | The [Stage 2 follow-up contract](stage-02-combined-ewf-roughness/index.md#selected-follow-up--3-october-2026) |
|  | owns the matched cap test and deferred speed/DPM sequence |
|  | The original |
| cap-limited outcomes | remain immutable comparison evidence |
| Stage 2 screen complete — 2026-09-27. | The first stage screened roughness and EWF |
| primarily as separate mechanisms; E3 | was an earlier basic-EWF-plus-R3 interaction |
| — | with no measured film |
| Stage 2 combined the | retained E2.7 phase-accretion EWF |
| — | state with the previously tested R3, R4, and R5 roughness settings |
|  | Each child |
|  | started independently from the E2.7 continuation final pair at native 13586 |
|  | and completed 3,000 steady iterations |
|  | All three reached the exploratory |
|  | `0.3 m` film-thickness cap and had extreme film mass/speed responses; none |
|  | reduced phase-2 `steamoutlet` outflow magnitude against the E2.7 parent |
|  | See |
|  | the [Stage 2 result](stage-02-combined-ewf-roughness/results.md) and child |
|  | setups |
|  | The older R0-based first-stage |
| contract below | is retained as evidence of how the component settings arose |
| Human-selected phase direction — 2026-09-22. | Phase 7.2A starts from the |
| — | completed Phase 7.1A R0 Coupled / Global-Time-Step control continuation |
|  | That |
| run is a strong numerical starting baseline | it completed its continuation, |
| tracked the absorber command to machine precision, | retained low late scaled |
| — | residuals, and did not encounter AMG failure, floating-point exception, |
|  | nonfinite residuals, or a fatal solver event |
|  | It also leaves the central |
| mechanism question unresolved | liquid carryover through `steamoutlet` remains |
| — | large, while reverse flow and turbulent-viscosity limiting persist |
|  | The first 7.2A screen therefore compares two separate wall-routing |
|  | mechanisms—wall roughness and Eulerian Wall Film (EWF)—from the same developed |
|  | full-loading state |
| mechanisms | are not combined in the first screen, so a |
| — | change in steam-outlet liquid carryover can be attributed to one wall treatment |
|  | at a time |

</details>

## Evidence anchors

### Observed simulation evidence

| Item | Observed simulation evidence |
| --- | --- |
| — | The [declared R0 control window](../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-window.md) |
|  | identifies the terminal second continuation as the comparison control |
|  | Its |
|  | checkpoint ledger ends at expected native coordinate `5580`, while the final |
|  | report/transcript state reaches native coordinate `5586` |

<details>
<summary>Supporting detail — Observed simulation evidence</summary>

| Item | Observed simulation evidence |
| --- | --- |
| — | Phase 7.2A uses |
|  | that final `5586` state as its parent; the `4580–5580` interval remains the |
|  | historical R0 comparison window |
|  | The [R0 control result](../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md) |
|  | records the terminal second-continuation state and its limitations |
|  | The authoritative [run4 completion receipt](../../../PyAnsys/output/phase71a_r0_control_run4/authoritative-completion-receipt.json) |
|  | reports a verified final pair, `1000` reverse-flow messages, `1000` |
|  | turbulent-viscosity-limit messages, and no AMG/FPE/nonfinite messages |
| At the terminal report point, total liquid mass | was `295.8536 kg`, liquid |
| volume | was `0.3357353 m^3`, and lower-zone liquid mass was `0.0021686 kg` |
| absorber command and applied removal | were both `116.9200 kg/s`, with |
| — | command error `4.26e-14 kg/s` |
| terminal phase-resolved outlet reports | were approximately |
| — | `-80.2509 kg/s` for phase 1 and `-24.3344 kg/s` for phase 2 at |
|  | `steamoutlet`, for a mixture flux of `-104.5823 kg/s` |
|  | The phase-2 value is |
|  | the primary liquid-carryover baseline for 7.2A; its sign convention must be |
|  | stated in each child record |
|  | Terminal continuity and phase-2 volume-fraction residuals were |
|  | `2.7841e-3` and `5.4762e-4`, respectively |
| These | are useful numerical-health |
| — | observations, not a steady-state qualification |

</details>

### Inference and remaining uncertainty

| Item | Inference and remaining uncertainty |
| --- | --- |
| Inference | the control is numerically durable enough to support a |
| — | mechanism screen, but its lower liquid inventory and outlet routing are still |
|  | evolving |
|  | A wall treatment should be judged by matched-window routing and |
|  | balance evidence, not by a single lower residual or a lower total inventory |

<details>
<summary>Supporting detail — Inference and remaining uncertainty</summary>

| Item | Inference and remaining uncertainty |
| --- | --- |
| Open question | can wall momentum exchange or explicit film attachment |
| — | reduce phase-2 liquid reaching `steamoutlet` and/or move that liquid toward |
|  | the lower region without damaging vapor routing, source accounting, or |
|  | numerical health? |
| Assumption to verify at preflight | the final pair can be loaded and |
| — | reopened on each assigned live Fluent endpoint, and the wall/EWF control |
| needed for a family delta | is exposed cleanly in Fluent 2025 R2 |
| — | A capability |
| gap | is recorded as such; it is not to be emulated by changing another model |

</details>

## Phase contract

### Question

| Question |
| --- |
| Starting from the verified smooth-wall R0 terminal control state, can wall |
| roughness or EWF reduce liquid carryover through `steamoutlet` by changing |
| wall-adjacent liquid transport, while preserving absorber command tracking, |
| low source-inclusive mass imbalance, bounded or improving liquid inventory |
| behaviour, and credible vapor routing? |

### In scope

| Item | In scope |
| --- | --- |
| — | A matched steady continuation from the verified R0 terminal pair |
| Family R | roughness with EWF off and the rest of the model frozen |
| Family E | EWF with zero roughness and the rest of the model frozen |
| — | Native iteration histories, paired checkpoints, wall/mechanism readback, |
|  | phase-resolved fluxes, source-inclusive closure, liquid inventory, and |

<details>
<summary>Supporting detail — In scope</summary>

| Item | In scope |
| --- | --- |
| — | residual/event evidence |
|  | A first discovery window of up to `1,000` additional native steady |
|  | iterations per child, with checkpoints at `0`, `250`, `500`, `750`, and |
|  | `1,000` |
| exact child horizon | remains bounded by the live preflight and |
| must be reported explicitly; extending it | is a new execution decision |
| — | Parallel execution on independent server-local Fluent sessions when the |
|  | endpoint and parent gates pass |

</details>

### Frozen invariants

| Item | Frozen invariants |
| --- | --- |
| — | Unless the family record explicitly names the single wall-treatment delta, |
|  | preserve: |
|  | the 60k-mesh v2 virtual-outlet geometry and `p71a-v2-virtual-outlet` zone; |
|  | steady pressure-based Mixture/RNG k-epsilon physics; |
|  | the phase-2-only throughput-controlled absorber, matching liquid momentum |

<details>
<summary>Supporting detail — Frozen invariants</summary>

| Item | Frozen invariants |
| --- | --- |
| — | removal, and shared `k`/`epsilon` removal; |
|  | no direct phase-1 mass source and no direct vapor sink; |
|  | full-loading liquid and steam inlet targets (`116.92` and `80.69 kg/s`); |
|  | `steamoutlet` as the pressure outlet and all bottom boundaries as walls; |
|  | materials, gravity, discretization, solution controls, and steady |
|  | formulation from the verified control endpoint; |
|  | no physical transient formulation, mesh change, outlet change, absorber |
|  | change, inlet ramp, whole-domain reinitialization, or patched liquid pool |
| run4 endpoint | is already a developed full-loading state |
| — | The old v2 |
| `0.25 -> 1.00` first-2,000-iteration loading rule | remains historical context |
| for Phase 7.1A and | is not replayed in 7.2A children |

</details>

### Out of scope and claim limits

| Item | Out of scope and claim limits |
| --- | --- |
| — | No roughness-plus-EWF interaction in the initial single-mechanism E0–E2/R0–R3 |
|  | screen |
|  | The human-selected E3 follow-on combines E1 basic EWF with the |
|  | already tested R3 wall roughness (`k_s=5e-4 m`, `C_s=0.5`), from the same |
|  | verified parent; phase accretion stays off in E3 |

<details>
<summary>Supporting detail — Out of scope and claim limits</summary>

| Item | Out of scope and claim limits |
| --- | --- |
| — | No claim that lower carryover proves physical wall-scale validity, plant |
|  | separation efficiency, or hardware drainage performance |
|  | No claim of steady convergence solely from the control's low residuals or a |
|  | child completing its iteration budget |
|  | No inference of film drainage from a global liquid-inventory decrease unless |
| film mass and transfer/flow evidence | are also available |
| — | No promotion of a family solely because it reduces total liquid mass; the |
|  | result must also show an interpretable change in phase-resolved routing and |
|  | preserved mass/source accounting |

</details>

## Candidate experiment families

| Family | Controlled delta | Screening question | Positive signal | Reject / defer signal |
| --- | --- | --- | --- | --- |
| R — roughness | Wall roughness only; EWF off; `C_s=0.5` when active | Does increased wall shear change near-wall liquid direction and reduce phase-2 carryover? | Monotonic or otherwise interpretable change in outer-wall liquid velocity, lower-region delivery, and lower `steamoutlet` liquid flux with preserved closure | Wall scope/readback is not clean, another setting changes, or the response is unresolvable against numerical deterioration |
| E — Eulerian Wall Film | EWF only; roughness `k_s=0` | Does explicit wall-film formation and drainage capture liquid that remains in the bulk near-wall path? | Film mass/transfer evidence shows bulk-to-film capture and downward film flow, accompanied by reduced bulk liquid carryover and preserved vapor audit | Film variables/transfer cannot be exposed, film behaviour is unaccounted for, or apparent benefit is only a global inventory change |

| Item | Candidate experiment families |
| --- | --- |
| initial queue | is `R0/E0` smooth no-EWF control reference, then R1–R3 and |
| — | E1–E2 |
| R4 | remains an evidence-gated roughness extension |
| — | By direct human |
| reframe on 2026-09-23, E3 is a selected interaction follow-on | E1 basic EWF |

<details>
<summary>Supporting detail — Candidate experiment families</summary>

| Item | Candidate experiment families |
| --- | --- |
| — | plus R3 roughness, with no phase accretion or additional film-physics option |
| Its clean two-factor contrast | is E0/E1/R3/E3, judged by the same matched-window |
| — | carryover, film, closure, inventory, and solver-health evidence |
|  | The human also selected E2.1 on 2026-09-23 after reviewing the EWF result: |
|  | repeat E2's phase-accretion setup from the same verified 5586 parent, changing |
|  | only the Fluent maximum film-thickness limit from `0.01 m` to `0.3 m` |
|  | Treat |
|  | this as an exploratory numerical-limit sensitivity, not a physical film |
|  | thickness target |
|  | Record maximum and area-weighted film thickness and film |
|  | mass every native iteration, with the EWF transfer, outlet, closure, and |
|  | solver-health evidence already required for Family E |
|  | Its setup and claim |
| limits | are in [E2.1 setup](ewf-family/e2.1/setup.md) |
| After E2.4 and E2.5 | were each tested individually, the user selected a |
| combined E2.6 | 10 film sub-iterations, maximum Courant `0.05`, fixed film |
| — | timestep `10e-6 s` (`1e-5 s`), and EWF Coupled Solution ON, retaining the |
|  | `0.3 m` exploratory cap |
|  | E2.6 starts independently from the same native-5586 |
|  | parent |
| Since fixed film stepping | is selected, the Courant value is retained |
| for requested readback but | is inactive in time-step selection |
| — | The [E2.6 |
| setup](ewf-family/e2.6/setup.md) | records the combined-control interpretation |
| — | limit and every-iteration monitoring contract |
|  | E2.6 reached the `0.3 m` cap |
|  | at native 5760 and an FPE at 5765; all 26 native Report Files were recovered |
|  | through 5764 |
|  | The combined controls delayed failure relative to E2.1 and E2.4 |
|  | but not E2.5, without isolating any individual control effect |
|  | [E2.6 result](ewf-family/results.md#e26--combined-ewf-controls--2026-09-23) |
|  | The user next selected E2.7 to repeat the E2.6 controls from the same parent |
|  | while disabling only film-wall Flow Momentum Coupling |
|  | Phase Accretion and |
| Fluent's separate EWF Coupled Solution option | remain on |
| — | E2.7 completed native |
| 5586–8586 without cap or FPE; maximum thickness | was `0.000331 m`, and film |
| — | mass reached `3.111 kg` |
| This | is a run-specific numerical improvement over |
| — | E2.6's cap/FPE sequence, not evidence of convergence or physical carryover |
|  | benefit |
| Liquid inventory and absorber tracking | were still moving/off-command |
| — | See the [E2.7 setup and result](ewf-family/e2.7/setup.md) and |
|  | [Family E results](ewf-family/results.md#e27--flow-momentum-coupling-off--2026-09-23) |

</details>

## Decision conditions

| Item | Decision conditions |
| --- | --- |
| screen | is useful only if each child passes parent identity, wall/EWF |
| — | readback, paired save/reopen, and instrumentation gates |
|  | For a usable |
|  | mechanism conclusion, compare the same native windows against the R0 baseline |
|  | using: |

<details>
<summary>Supporting detail — Decision conditions</summary>

| Item | Decision conditions |
| --- | --- |
| — | phase-2 liquid flux through `steamoutlet` and its window mean/slope; |
|  | phase-1 steam flux through `steamoutlet` and mixture outlet flux; |
|  | total liquid inventory and lower-region liquid inventory/availability; |
|  | absorber command, native applied phase-2 removal, and command error; |
|  | source-inclusive phase and mixture closure, including storage when the |
| field | is moving; |
| — | residuals, reverse-flow activity, viscosity limiting, AMG/FPE/nonfinite |
|  | events, and checkpoint survival; and |
|  | family-specific wall trajectory evidence, or EWF film mass and transfer |
|  | evidence where applicable |
|  | A branch can be selected for a longer follow-up when it gives a repeatable, |
|  | mechanistically supported reduction in liquid carryover without an |
|  | unaccounted source/outlet path and without unacceptable numerical degradation |
| If both families fail that test, the result | is still a useful negative screen: |
| the missing mechanism | is not established as a roughness/EWF effect inside this |
| — | model |
|  | Neither outcome authorizes Phase 08 or a plant-performance claim |

</details>
