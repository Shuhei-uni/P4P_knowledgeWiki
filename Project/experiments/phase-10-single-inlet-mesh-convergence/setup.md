# Phase 10 — Study setup

| Item | Status |
| --- | --- |
| Runnable contract | Human-authorized provisional M04 carrier-first stage for full-flow spiral Case 4, N1500 cap; recovered source audited; exact Case 4 DPM setup saved/reopened. Baseline and BF01 failures remain preserved |
| Human-selected comparison | Same Purnanto 2013 setup; tet versus poly-hexcore output agreement and computational cost |
| Historical reference | [Seven-level study](historical-reference.md); existing endpoints are diagnostic, not a qualified steady reference |
| Mesh parent | Preserved `Separator-purnanto-single-733k.msh.h5`, 733,979 cells |
| CAD parent | `separator-purnanto(single-homo).agdb`; unchanged hash in the [mesh-family audit](../../technical/single-inlet-mesh-family-20261008.md) |
| Mesh delivery and run locations | [Path register](run-paths.yaml) |

## Selected reference and run envelope

| Item | Selection | Evidence or limit |
| --- | --- | --- |
| Human direction | Use an old Purnanto setup; no further source-file recovery required | 8 October 2026 |
| Scientific reference | [00a saved-case audit](../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/setup.md) | Recorded original single-inlet model, properties, BCs and numerics |
| Native source | Recovered `4800-iterations-300412-1.cas.h5`; SHA-256 `5c6fb39a5148a5f39b601d46ed6fa048a0769aed80a9859f18863dee7f02de4b` | Loaded in Fluent 2025 R2; 2,964,593 tet cells, 572,556 nodes, one inlet; original file unchanged |
| Common carrier parent | `purnanto-original-carrier-common.cas.h5`; SHA-256 `99d7c34410c76bcba6d2add51753986ec288ede9de78a90508acbc076c4806de` | [Build proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/original-carrier-common-build-20261009.json); carrier settings unchanged before/after save/reopen |
| Allowed parent changes | Rename `wall-fluid` to `wall`, `outlet` to `steamoutlet`; remove unused `injection-0` at 1e-20 kg/s with carrier feedback off | Boundary roles and carrier values unchanged; native original precision retained |
| Models | Steady pressure-based Mixture; vapor primary/liquid secondary; RNG k-epsilon; standard wall functions; energy off | 00a audit |
| RNG options | Differential viscosity and swirl-dominated flow enabled | 00a audit |
| Properties | Vapor rho 5.7974339 kg/m3, mu 1.52062e-5 Pa s; liquid rho 881.21088 kg/m3, mu 1.45544e-4 Pa s | Preserve saved material precision; phase properties unchanged |
| Operating conditions | Gravity (0,-9.81,0) m/s2; operating pressure 0 Pa; mixture-averaged operating density | 00a audit |
| Inlet | One mass-flow inlet; vapor 80.69 kg/s; liquid 116.92 kg/s; pressure 1.14 MPa; intensity 2.11%; diameter 0.724 m | Both phases through the same boundary |
| Outlet | Pressure 1.12 MPa; liquid backflow VF 0; intensity 2.1525%; diameter 0.724 m | Preserve supplied name `steamoutlet` |
| Walls | Stationary no-slip; roughness height 0; roughness constant 0.5; sealed bottom | Preserve supplied mesh boundary names; copy verified common wall state to new wall scopes |
| Numerics | SIMPLE; Green-Gauss node gradients; PRESTO; second-order momentum/k/epsilon; QUICK volume fraction; pseudo time off | 00a audit; differs from later 08b first-order k |
| Implicit body force, baseline | Off | Both fields are false in the [recovered original readback](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/original-case-setup-52660.json); Purnanto 2013 does not report this switch |
| Relaxation | Pressure 0.3; momentum 0.7; volume fraction 0.4000000059604645; k/epsilon 0.8; drift 0.1; other recorded factors 1 | Common-reference readback required |
| DPM/EWF | No active injections or carrier feedback; no EWF | Carrier mesh study; unused particle-material group may disappear |
| Initialisation | Independent fresh Hybrid start on each mesh | No inherited archived fields |
| Horizon | 5000 new iterations per level; 35000 total maximum | Five 1000-iteration blocks; first five updates are the instrumentation smoke and count in the horizon |
| Checkpoints | Paired N0 and smoke N5; N1000, N2000, N3000, N4000, N5000 | Fluent local disk; N3000 retained for historical comparison |
| Historical horizon | Seven formal levels at nominal N3000; 900k extended to N6000 | Separate 00a/08b baseline records at N5000 |
| Settings proof | Strict common-reference readback before solve and after save/reopen on each mesh | Models, materials, operating conditions, fluid/wall/inlet/outlet state, methods, controls and residual criteria |
| Solver mesh proof | Same cell and face counts; exact active coordinate set and all face polygons | Fluent may omit unused input vertices; report file nodes and solver vertices separately |
| Processor/version control | Same current Fluent 2025 R2 endpoint and processor allocation throughout | Historical study used 2024 R2; no direct speedup claim from unmatched old timing |
| Required reports | Every 10 iterations: phase/mixture fluxes, phase masses, inlet/outlet static pressure and speed, mean/max domain speed, mean vorticity | Preserve native residual transcripts and full histories |
| Qualification window | Final 500 updates; pressure drift <=0.5%; velocity/vorticity drift <=1%; phase/mixture flux error <=1% of phase inlet; inventory change <=1% | Absolute near-zero liquid routing values; residual criteria continuity 1e-4, other active equations 1e-3 |
| Execution stop | Native failure, non-finite report, changed settings, failed artifact/report proof or incomplete block | Preserve last verified pair; recover within the same scientific settings |
| Scientific stop | N5000 per mesh | Failure of qualification does not become mesh independence or a speedup result |
| Figures after execution | Pressure versus actual h; scalar drift and phase/mixture closure table; velocity/vorticity versus h; solver seconds versus output sensitivity | Spatial flow views required before spatial interpretation |

## Mesh register

| Level | File | Actual cells | File nodes | Effective h = (V/N)^(1/3), m | Preparation |
| --- | --- | ---: | ---: | ---: | --- |
| M01 | `Separator-purnanto-single-357k.msh.h5` | 357,145 | 981,016 | 0.03992 | Saved/reopened and copy-verified |
| M02 | `Separator-purnanto-single-488k.msh.h5` | 487,746 | 1,267,334 | 0.03600 | Saved/reopened and copy-verified |
| M03 | `Separator-purnanto-single-682k.msh.h5` | 681,844 | 1,812,424 | 0.03221 | Saved/reopened and copy-verified; size-change locations need review |
| M04 | `Separator-purnanto-single-947k.msh.h5` | 946,967 | 2,440,489 | 0.02887 | Saved/reopened and copy-verified |
| M05 | `Separator-purnanto-single-1430k.msh.h5` | 1,430,497 | 3,644,493 | 0.02516 | Saved/reopened and copy-verified |
| M06 | `Separator-purnanto-single-2210k.msh.h5` | 2,209,748 | 5,560,709 | 0.02177 | Saved/reopened and copy-verified |
| M07 | `Separator-purnanto-single-5480k.msh.h5` | 5,479,605 | 10,041,979 | 0.01608 | Saved/reopened and copy-verified |

Source: [read-only saved-file header counts](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/family-node-counts.json); global node counts agree with coordinate-array row counts. File nodes are geometric vertices, not solver processes.

## Fixed mesh controls

| Item | Recorded control |
| --- | --- |
| Geometry | One inlet; same CAD and boundary names/types |
| Surface sizing | Curvature and proximity; curvature normal angle 6 degrees; linear sizes scaled by level |
| Volume mesh | Poly-hexcore; maximum cell length scaled by level |
| Wall layers | 12 requested; growth 1.15; same wall scopes; local stair-stepping warning retained |
| Quality improvement | OQ target 0.3; feature ignoring disabled; iteration limit 25 except recovered M05 at 26 |
| Actual geometry differences | Recorded volume/area differences in the [audit](../../technical/single-inlet-mesh-family-20261008.md); preserve them in interpretation |

## Comparison outputs

| Output | Definition | Evidence |
| --- | --- | --- |
| Pressure drop | Inlet minus steam-outlet area-averaged static pressure | History and refinement plot |
| Steam-outlet liquid routing | Phase-liquid steam-outlet mass flow; report absolute values near zero | History and refinement plot |
| Conservation | Signed phase/mixture inlet plus outlet fluxes; no active DPM/EWF/source removal | Closure and inventory-window table |
| Flow structure | Common planes, locations and velocity/pressure measures | Comparable spatial views |
| Numerical adequacy | Active residuals, inventory drift and endpoint stability | Qualification table per mesh |
| Solver cost | Elapsed solver time and iterations to the qualified comparison window; seconds/iteration; peak memory | Cost versus output agreement; measured tet/poly speedup where both runs qualify |

| Timing record | Method |
| --- | --- |
| Solver timer | Fluent Parallel → Timer → Usage; capture total solver wall-clock time and seconds per iteration |
| End-to-end time | Record mesh generation, setup, file I/O and solver time separately |
| Reference | [Ansys 2025 R2 performance timer](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_parallel_monitor_optimize.html) |

## Authorized execution and monitoring

| Item | Contract |
| --- | --- |
| User authority | Execute the selected study without further confirmation; ordinary technical recovery stays in scope |
| Assigned endpoint | Port 60569, IP 10.104.145.174; Fluent 2025 R2, 16 ranks verified in the N10 reopen transcript; account-local controller runtime retained |
| Fresh-start coordinate | Hybrid may report `Iteration=1` before any solve; the saved/reopened N0 pair must prove zero |
| Deployment | Detached Windows `Win32_Process.Create`; fifteen-second delay before callback; sixty-second startup connection limit; credentials remain in memory |
| Live inspection | Passive receipt reads only; no Scheme system/PowerShell/CIM query while a controller is active; OS process state requires an independent verified route |
| Relaunch guard | Reconcile previous controller, saved pilot pair and actual solved count; no duplicate controller; smoke proof required before batch |
| Current state | BF01 failed at N3567; ON flags and N3005 hashes verified; controller 24124 exited; owned Fluent idle. No further solve selected |
| Monitor request | Human-created task `Phase 10` was verified ACTIVE every 30 minutes in this chat. Prepared prompt now includes BF01; saved schedule prompt update is unverified because `automation_update` is unavailable. [Prior readback](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/monitor-active-readback-20261009.json) |
| Retrieval limit | Current remote file route uses Fluent Scheme; loss of API access blocks receipt retrieval, not proof that remote files are absent |
| Current access block | Resolved. Human resumed 12 October NZ; authenticated native receipts and live BF01 progress verified |

## Selected follow-up — BF01 implicit body-force test

| Item | Contract |
| --- | --- |
| Status | NUMERICAL_FAILURE_UNQUALIFIED; terminal at N3567 after 567 new updates; ON N3005 retained; no retry selected |
| Human authority | 11 October 2026, NZ: try body force ON after the series. Updated 12 October NZ: skip M07 and test ON using a coarser mesh; selected M04 contract retained |
| Question | Does implicit body-force treatment suppress the recorded M04 overflow when restarted from the same finite N3000 fields? |
| Paper provenance | [Purnanto 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS), p.5 §3.1 and p.6 §3.3: gravity and numerical methods reported; implicit body-force switch not specified |
| Numerical rationale | [Fluent 2025 R2 §27.2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html) recommends this treatment for Mixture with body forces; gravity is already active |
| Contrast class | NEW numerical contrast; existing OFF failure supplies the baseline, but does not test ON |
| Parent | Preserved original M04 `checkpoint-N3000.cas.h5` / `.dat.h5`; 946967 cells, 2385385 solver nodes; finite but unqualified |
| Parent identity | Paths and exact hashes in the [BF01 job specification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-job-spec.json), copied from the original native manifest |
| Single controlled delta | Set `setup.models.multiphase.advanced_formulation.implicit_body_force` to true; capture the expert field readback to resolve any native alias |
| Frozen inputs | Parent fields and iteration coordinate; geometry, boundary types and values, materials, all models, gravity, discretisation, relaxation, residual criteria and processor allocation |
| State proof | Compare complete scientific state before/after toggle and save/reopen; only the selected switch and a proven native alias may change; no reinitialisation |
| Baseline | Existing M04 N3000–N3911 segment; preserve its failed classification and original files |
| Trigger | M05 and M06 numerically failed; M07 user-stopped with preserved N718 pair; original batch terminal evidence reconciled; controller exited and owned Fluent idle; no human pause |
| Launch gate | Hash-check parent; verify mesh/counter/readback; review separate runner; reconcile all spent/lost updates and confirm at least 1000 campaign updates remain |
| Solve | Exactly 1000 additional updates, N3000 to N4000; one five-update instrumentation smoke, then 995 unchanged updates; smoke and all retries count in this cap |
| Checkpoints | Separate paired ON N3000, smoke N3005 and final N4000; hashes, native iteration and state readbacks; preserve the last valid pair after a failure |
| Output ownership | Separate `bodyforce-BF01-<run-id>` native folder and BF01 ledger; original queue/configuration and baseline artifacts remain intact |
| Budget | 35000 campaign cap unchanged; baseline conservative maximum 28919, plus BF01 1000 gives 29919; actual native receipts govern dispatch |
| Evidence | Native residual transcript and ten-update histories; phase/mixture fluxes, liquid/vapor inventory, pressure, speed/vorticity, maximum speed and viscosity-clipping warnings |
| Compare | Same native iteration coordinate against OFF history; raw N3000–N3911 curves and final-500 ON drift/balance table; report absolute flux errors relative to fixed phase feeds |
| Support | Finite continuation past the original N3911 failure supports a stability benefit under this restart condition |
| Competing explanation | Liquid accumulation and poor routing may persist even if overflow is suppressed; check conservation and inventory independently |
| Failure policy | Preserve numerical failure and actual spend; technical recovery may resume only a verified ON pair within the remaining BF01 cap; no automatic changed-input retry |
| Claim limit | Numerical diagnostic only; N4000 survival does not qualify M04, prove mesh independence, or establish tet/poly accuracy or speedup |
| Completion | Verify paired endpoint, settings, histories and spend; analyse the contrast; then pause monitoring after terminal review; no further solve selected |

## Selected 1600 kJ/kg follow-up — R1600

| Item | Selection |
| --- | --- |
| Human request | Repeat the full-flow 1600 kJ/kg case with exact historical settings and DPM injections |
| Human clarification, 13 October 2026 NZ | Continuity residual nonconvergence is expected for the historical replication. Do not use continuity alone to stop or reject the N1500 protocol; retain its values and the independent inventory/flux observations |
| Mesh | M04, 946,967 cells; explicitly selected by human |
| Source | Human-selected spiral Case 4, `spiral_enthalpy_sweep_20260725`; [binary/settings recovery](replication1600-source-recovery.md). Baseline selection in the original handoff is superseded |
| Injections | Nine direct spiral Case 4 objects; `liquid-water`; 26.865069 m/s face-normal; Stokes-Cunningham drag; 116.92 kg/s total |
| Settings parity | Recovered parent carrier/global/material controls and geometric boundary-role mapping verified; direct Case 4 injections applied; exact July binary/full-export provenance unverified |
| Carrier-first authority | Human requested starting available replication work now; historical spiral file search deferred until tomorrow |
| Carrier stage | Provisional fresh Hybrid M04 OFF run using recovered Purnanto settings; verified Case 4 inlet conditions; cap 1500 new updates, including one smoke, then blocks of 1000 and 499 |
| DPM stage | Exact nine spiral definitions applied; recovered material and global controls verified; one fresh tracking update complete at N1500; aggregate/nine reports mass-audited; tracked pair saved/reopened |
| Launch status | N1500 carrier complete and source-audited; post-DPM pair saved/reopened and loaded; Fluent idle; particle mass accounting verified; carrier unqualified |

| Conditional enthalpy follow-ups | Contract |
| --- | --- |
| Human monitor authority | After R1600 review and source-setting resolution, useful full-flow M04 cases at 1440, 1520, 1680 and 1760 kJ/kg may proceed |
| Per case | Exact own historical inlet/injection definitions, common verified parent physics/numerics, fresh initialization, 1500-update allocation including retries |
| Limits | No reduced-flow Case 1; no sweep after repeated numerical failure; no DPM with unverified particle properties/global controls |
| Combined no-retry budget | Prior upper bound 23559 plus five 1500 allocations = 31059 of 35000 |

## Selected full-flow enthalpy repeats

| Item | Current selection |
| --- | --- |
| Human direction, 13 October 2026 NZ | Run M04 at 1440, 1520, 1680 and 1760 kJ/kg; incomplete particles assumed separated in efficiency |
| Execution contract | [Enthalpy sweep](replication-enthalpy-sweep.md): fresh N1500 carrier and nine source injections per case, 100000 tracking steps |
| State | All five selected enthalpies complete at N1500 plus DPM; native pairs, settings, reports and histories verified. Final writer exited and Fluent idle. [Results](replication-enthalpy-results.md) |

## Selected matched tet benchmark

| Item | Current selection |
| --- | --- |
| Human direction | Run the tet mesh on the current PC and Fluent for the proposed matched1600 comparison |
| Contract | [Tet benchmark](replication1600-tet-benchmark.md): fresh Hybrid N0;1500 carrier updates including smoke; one DPM update at100000 steps; exact M04 Case4 physics and injections |
| Budget |1500 allocated updates; prior upper bound31059; terminal upper bound32559 of35000 |
| Claim | Fixed-horizon cost/output comparison; no convergence or improved-accuracy claim |
| Completion |TetN1500 plus one DPM update verified; no further solve selected; [benchmark results](replication1600-tet-results.md) |
