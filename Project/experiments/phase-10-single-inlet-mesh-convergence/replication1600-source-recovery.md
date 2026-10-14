# R1600 — recovered spiral parent audited; exact Case 4 reconstruction

| Item | Current selection / evidence |
| --- | --- |
| Human selection | Full-flow **spiral-inlet Case 4**, 1600 kJ/kg, on M04, 946,967 cells; exact historical settings and DPM injections |
| Historical family | `spiral_enthalpy_sweep_20260725`; parent `baseline_spiral_inlet.cas.h5` |
| Handoff correction | The [provided handoff](replication1600-source-handoff.md) selects baseline/Bangma-target Case 4. The human explicitly selected spiral Case 4 instead. The handoff is retained unchanged; its baseline selection is superseded |
| Carrier loading | Steam 80.69 kg/s; liquid 116.92 kg/s; total 197.61 kg/s |
| Exact injection evidence | Nine complete Case 4 objects; pre-DPM, post-DPM and flow-manifest objects identical; diameter/mass values match the spiral droplet CSV |
| Historical carrier horizon | 1500 verified updates; fresh Hybrid initialization recorded in the execution log |
| Source mesh | Case 4 log: 2,964,593 tetrahedral cells, 572,556 nodes, 15 ranks, Fluent 2024 R2 |
| Historical DPM fates | Escaped 0.01655 kg/s; trapped 113 kg/s; incomplete 3.907 kg/s; retain rounding and incomplete-tracking limits |
| Binary recovery | Matching spiral h1600 parent candidate recovered from Extreme SSD and copied with a full hash; exact July-named parent/Case 4 endpoints remain unlocated |
| Human source recovery | Human attached Extreme SSD on 13 October 2026 NZ and requested use of its organisation map; archived h1600 candidate identity now matches recorded spiral mesh and all nine tested parent-injection properties |
| Human-nominated archive folder | `parallel-andy-studies/enthalpy-dpm-replication/baseline/enthalpy_sweep` inspected on the PC; its Case 4 binary is confirmed baseline, not the selected spiral parent |
| Execution | N1500 carrier complete; carrier settings match recovered parent; exact Case 4 DPM tracked and mass-audited; [results](replication1600-dpm-results.md) |

## Preserved spiral evidence

| Artifact | Coverage |
| --- | --- |
| [Retrieval and hashes](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-reference/retrieval.json) | Nine byte-identical copies: Case 4 manifests, DPM report, injection results, summary, residual history, two parent inspections and sweep log |
| [Exact injection objects](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-reference/exact-injection-readbacks.json) | Direct Case 4 definitions; full precision, not rounded injection names or parent values |
| [Settings coverage](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-reference/settings-coverage.json) | Direct Case 4 inlet/injection evidence, parent boundary/coupling evidence and unresolved settings |
| [Original handoff](replication1600-source-handoff.md) | Baseline family only; not the selected spiral settings authority |
| [Unselected baseline bundle](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/accepted-reference/retrieval.json) | Prior imported evidence retained; its spherical drag, water-liquid-dpm material and 34.221202 m/s speed do not apply to this run |
| [Historical runbook](../../../PyAnsys/docs/historical/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md) | Preserved operational reference; [current wrapper](../../../PyAnsys/docs/PURNANTO_ENTHALPY_DPM_REFERENCE.md) gives current precedence |

## Exact spiral Case 4 injection targets

| Injection | Diameter, μm | Mass flow, kg/s |
| --- | ---: | ---: |
| injection-5-micron | 5.621362 | 0.189995 |
| injection-28-micron | 28.106810 | 0.780441 |
| injection-56-micron | 56.213620 | 0.970436 |
| injection-112-micron | 112.427200 | 1.952564 |
| injection-168-micron | 168.640900 | 1.952564 |
| injection-348-micron | 348.524400 | 23.384000 |
| injection-562-micron | 562.136200 | 29.230000 |
| injection-844-micron | 843.204300 | 29.230000 |
| injection-1631-micron | 1630.195000 | 29.230000 |
| **Total** | | **116.920000** |

| Common injection setting | Direct Case 4 readback |
| --- | --- |
| Type / material | Inert surface injection; `liquid-water` |
| Location | `inlet`; global frame; randomized positions false |
| Velocity | Face-normal, positive magnitude **26.865069 m/s** |
| Size | Uniform diameter per injection |
| Drag | **Stokes-Cunningham**, Cunningham factor 1.0 |
| Dispersion / rotation / rough wall | All false |
| Laws | Law 1 inert-heating; laws 2–10 inactive |

## Source settings and remaining gaps

| Setting | Evidence / required check |
| --- | --- |
| Case 4 inlet | Normal to boundary; absolute frame; pressure field 1,140,000 Pa; turbulence intensity 0.02109999952837825; hydraulic diameter 0.724 m; DPM escape |
| Parent coupling | Shared spiral-parent inspection records interaction false: one-way DPM. Case 1 label identifies inspection context; the inlet readback is full flow. This is not a full carrier/global-settings export |
| Parent top outlet | `outlet`: pressure outlet, 1,120,000 Pa; DPM escape; liquid backflow fraction 0 |
| Parent bottom | `bottom`: stationary no-slip wall; DPM trap |
| Parent vessel wall | `wall-fluid`: stationary no-slip wall; DPM reflect; normal/tangential restitution 0.3 / 0.8 |
| Direct Case 4 boundary parity | Fates corroborate outlet escape / bottom trap. Full Case 4 boundary-state readback remains unavailable; verify inherited settings and geometric mapping to M04 |
| Full carrier settings | Archived h1600 candidate and complete stored RP variables available; live carrier, numerics and geometric boundary-role checks match M04; [audit](replication1600-settings-audit.md) |
| Global DPM settings | Recovered candidate stores maximum 10000 tracking steps and step-length factor 5; full controls exported live; recorded parent boundaries/injections/coupling match after explicit API-name translations |
| Particle material properties | Recovered h1600 candidate has `liquid-water`, density 881.2109 kg/m³, and full stored material properties; no guessed density required |
| Related recovered original | Original Phase 10 export has the same cell count, but lists `arsenic-hydride` and `injection-0`, unlike the spiral parent. It is not a certified exact DPM source |
| Archived baseline Case 4 binary | Offline read and paired hashes verified: 5,578,299 cells; steam_outlet/fluid_outlet; nine injection-0..8 objects; water-liquid-dpm at 881.77 kg/m³; 34.221202 m/s; spherical drag. Stored tracking limit 100000 steps and factor 5; these are not certified spiral settings |
| Archived baseline manifest | Native adjacent manifest is invalid JSON at line 93, column 37; original bytes retained. Binary settings and result CSVs establish baseline identity independently |
| Archive inspection evidence | [Summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/archive-case4-inspection/summary.json); source case not loaded into Fluent; M04 N1500 unchanged; zero solver updates |
| Required action | Case 4 tracking complete with zero carrier updates; review particle results before conditional enthalpies; exact July binary provenance remains a limit |

| Selected continuation after source parity | Contract |
| --- | --- |
| Scope | One full-flow M04 spiral Case 4 repeat; no sweep or further body-force contrast |
| Delta | Mesh only, with explicit geometric boundary-role mapping |
| Horizon | 1500 verified carrier updates, including smoke and retries within the selected cap; fresh historical Hybrid start |
| DPM | Exact spiral Case 4 injection objects; fresh post-carrier update/report with all particle fates |
| Budget | Prior upper bound 23559; plus selected 1500 gives 25059 within the 35000 campaign cap |
| Claims | Historical execution and fate accounting do not establish carrier convergence, mesh independence or validated separator performance |

## Authorized carrier-first staging

| Item | Contract |
| --- | --- |
| Human direction | Start available replication work now; human will look for the spiral files tomorrow |
| Available first stage | Fresh M04 OFF carrier under recovered Purnanto settings; Case 4 phase loading, inlet pressure and turbulence match direct spiral records |
| Horizon | 1500 new updates including one smoke; fixed blocks of 1000 and 499; save/reopen checkpoints |
| DPM | No injections instantiated or particles tracked in this stage. Exact definitions preserved for later verified setup |
| Limit | Recovered parent controls audited; exact Case 4 overrides saved/reopened. Exact July binary/full export unlocated; reconstruction and version limits retained |

| Carrier startup proof | Status |
| --- | --- |
| [Native verification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-start-verification.json) | One controller; fresh N0 and smoke N1 pairs verified; long block dispatched |
| [Code review](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-code-review.json) | Native source hashes, smoke/block budget, DPM exclusion and retrieval limitation |

## SSD spiral-parent recovery

| Item | Verified evidence / remaining limit |
| --- | --- |
| Organisation file | `/Volumes/Extreme SSD/P4P/_organization/original-to-new-manifest.json`; selected entry and recorded sampled fingerprint match |
| Recovered file | `experiments/parallel-andy-studies/enthalpy-dpm-replication/workbench-predecessors/Punanto_injections/h1600_files/dp0/FFF/Fluent/4800-iterations-300412-1.cas.h5` under SSD P4P root |
| Mesh and boundary names | 2,964,593 cells; 572,556 nodes; inlet, outlet, bottom, wall-fluid and interior-fluid |
| Parent-injection checks | All nine match recorded parent material, diameter, total flow, speed, face-normal flag, drag, Cunningham factor and dispersion switch |
| Parent command setting | 2161 matches saved parent inspection; this setting is not an actual solved-horizon proof |
| Material / global controls | liquid-water at 881.2109 kg/m³; 10000 maximum steps; step-length factor 5; other stored settings exported |
| [Recovery receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-recovered-parent/recovery.json) | Exact source/copy paths, full SHA-256, organisation fingerprint, data candidates and audit frontier |
| Data candidates | Same folder has `...-00000.dat.h5` and `...-02003.dat.h5`; pairing/field state not yet audited; fresh carrier already preserved at M04 N1500 |
| Search extent | 43502 readable volume files, including P4P organisation map and 374 HDF5 cases checked; no July-basename hit. Spotlight/Trashes inaccessible; one P4P case has no settings dataset |
| Alternate recovered variant | Windows Recycle Bin contains a spiral-named case with different material/injection values; not substituted |
| Current decision | Source loaded and audited; all recorded parent settings match and M04 carrier groups match. Exact July binary/full export remains unlocated; no carrier updates during audit |
