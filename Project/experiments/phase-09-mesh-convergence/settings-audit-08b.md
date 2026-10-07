# Phase 9 — Native settings comparison with 08b

| Audit status | Evidence / decision |
| --- | --- |
| Scope | Comparison of the preserved 342k child and saved 08b case, completed before Phase 9 solves |
| Actual reference | `P4P-Fluent-Artifacts/08b/TwoPhaseInletV2(Purnanto).cas.h5`; stored beside Phase8 |
| Reference identification | Native server file hash in [reference identity](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/reference-identity.json) |
| Native version | Fluent 2025 R2; 08b read into the same owned Server 3 |
| Read-only reference | Reference case loaded for inspection; no reference save, initialization or solve |
| Build preserved | The 342,609-cell child pair at N1580 was saved/reopened before reference inspection |
| Human bulk decision | Restore four untraced bulk-model differences to 08b; keep traced later changes |
| Human DPM decision | Keep current tracking controls; no separate DPM tracking pass |
| Retained controls | Human chose to keep current smoothing and reporting reference values |
| Approved exception | Human approved stored `none` for Mixture after native Simonin restoration failed to persist. Keep Mixture and proceed. |
| Execution state | Server 3 restarted and preserved Mixture pair restored. Common source and 342k save/reopen checks passed. Full native contract includes the human-approved exception. |

| Critical finding | 08b native state | Phase 9 before correction | Disposition |
| --- | --- | --- | --- |
| Bulk surface-tension force | `interaction.sfc-modeling? = true` | false | Human selected restoration |
| Bulk surface-tension coefficient | Constant `0.04041000083088875 N/m` | none | Restore the saved value, not a literature-rounded value |
| Bulk surface-tension formulation | `sfc-model-type = 0` | 0 | Match; retain same formulation |
| Wall and jump adhesion | Both off | Both off | Match |
| Stored pair turbulence interaction | `simonin-et-al` | none | Human approved `none` as an inactive legacy exception after native restoration failed to persist. No further model-switch probes. |
| Turbulence compressibility flag | `turb-compress-mod? = true` | false | Human selected restoration |
| Drag-modification flag | `mp/modify-drag? = true` | false | Human selected restoration; pair modification itself remains none |
| Drag law | Schiller–Naumann | Schiller–Naumann | Match |
| Slip law | Manninen et al. | Manninen et al. | Match |
| Interphase virtual mass / lift / wall lubrication / turbulent dispersion | Off / none | Off / none | Match; DPM virtual mass is a separate setting |
| Secondary-phase diameter | Saved single-precision approximately `10 µm` | `10 µm` | Match within serialization precision |
| Secondary phase | Non-granular liquid | Non-granular liquid | Match |
| Bulk tension smoothing passes | 1 | 2 | Human chose to keep current value |
| EWF surface-tension force and coefficient | Separate wall-film mechanism | Provisional selected Stage 4 settings | Retain traced EWF settings; bulk and film values are separate |

| Core setting | Comparison result | Owner / evidence |
| --- | --- | --- |
| Solver family / time / velocity | Both pressure-based, steady, absolute | Native setup captures |
| Multiphase / phase materials | Same Mixture pair and material assignments | Native setup and domain captures |
| Active fluid density and viscosity | Same saved phase material properties | Full materials-tree comparison |
| Gravity | Both `[0, -9.81, 0] m/s²` | Native setup captures |
| Operating pressure | Both 0 Pa | Native setup captures |
| Operating-density method | Both minimum-phase-averaged | Native setup captures; stored constant fields are not the active method |
| Turbulence | Both RNG k–epsilon, differential viscosity and swirl options on, standard wall functions | Native setup captures |
| Bulk discretization | Both node-based Green–Gauss; PRESTO pressure; second-order momentum/epsilon; first-order k; QUICK phase fraction | Actual 08b capture; do not replace first-order k based on older 00a records |
| Inlet role / directions / turbulence | Match; split mass-flow inlets retained | Native boundary-tree comparison |
| Current inlet mass flows | 25% of 08b full feed | Intended Stage 4 startup; full feed is 116.92 kg/s liquid and 80.69 kg/s vapor |
| Steam-outlet pressure / phase backflow | Match | Native boundary-tree comparison |
| Outlet hydraulic diameter | 0.876 m in 08b; 0.875936 m in Phase 9 | [Phase 7A geometry correction](../phase-07a-simplified-purnanto-liquid-removal/e0-08b-corrected-reference/setup.md) |
| Pressure–velocity coupling | SIMPLE → Coupled | [Phase 7.1A controlled solver change](../phase-07-1a-absorber-convergence/v2-coupled-global-pseudo-time-inlet-ramp/deffered.md) |
| Pseudo-time | Off → Global Time Step | Same recorded solver package; numerical time, not physical time |
| Scalar AMG / smoother | Gauss–Seidel / interval 2 / one post-sweep / flexible cycles → ILU / interval 8 / three post-sweeps / F cycles | Native no-solve probe reproduces these changes when Global Time Step is enabled |
| Bulk relaxation / pseudo scale | Selected recovery controls, including scale 0.01 | [Stage 4 realism recovery](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/setup.md) |
| Roughness | Smooth 08b → 0.045 mm, Cs 0.5, bottom smooth | Same Stage 4 selected wall treatment |
| Collector | Added lower contact sink, phase-velocity momentum removal, 10 µs source time | [Stage 3 startup intent](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/setup.md) |
| Film / EWF mechanisms | Added wall film and selected Stage 4 mechanisms | Stage 4 provisional selection; not final EWF qualification |
| Bulk equations | All four active | Required Phase 9 endpoint boundary |

| DPM / diagnostics | Difference and trace | Disposition |
| --- | --- | --- |
| Diagnostic injections | Six bins retained; each `1e-20 kg/s`; 08b uses substantive diagnostic mass | [Stage 3 reconstruction](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/results.md); no second carrier feed |
| Particle material | Stage 4 water-liquid-at-psep-pcle matches parent film density/viscosity and film tension | Retain [Stage 4 prerequisite](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/setup.md) |
| DPM pressure / virtual-mass force | Both enabled; virtual-mass factor 0.5 | Match |
| DPM carrier interaction | Off | Match; film collection/coupling options are separate |
| Tracking budget | 10,000 → 50,000 | Contact-absorber tracking proof implementation; retain |
| Step-length factor | 5 → 20 | Disposable contact fixture leaves factor 20 after its sweep; no explicit production selection found; human chose to keep current controls |
| Subtet validity / quad-face centroid | Off → on | No explicit change record found; human chose to keep current controls |
| Bottom/collector particle treatment | Trap → collector/lower escape | [Contact-absorber route](../phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/ewf-absorber/setup.md) |
| Residual automatic convergence stop | Enabled in 08b; disabled in later run package | Native requested-horizon execution; retain monitoring and exact update-count proof |
| Report definitions / files / UDF diagnostics | Added source-inclusive flux, inventories, film and collector reports; paths relocated to local disk | Intended later instrumentation; preserve full definitions and native histories |
| Reporting reference values | 08b values differ from inherited default density, velocity, temperature, pressure and enthalpy | Human chose to keep current values; these are distinct from active fluid properties and imposed BCs |

| Inactive / serialization differences | Why they are not current model changes |
| --- | --- |
| Cavitation pressure and related stored values | Cavitation and mass transfer are off in both; do not enable an inactive model to force a stored-value match |
| Granular packing / friction / stored granular viscosity | Secondary liquid is non-granular; active material viscosity matches |
| Single-precision versus double-precision constants | Compare physical values within their saved precision; preserve exact coefficients where explicitly selected |
| Disabled energy/species/radiation/population/boiling settings | Their stored defaults are retained in the full machine diff; they do not establish active added physics |
| Operating constant density/temperature fields | The active density method matches; constant values are dormant; energy is off |
| Plot styling / file paths / extra reports / zone suffixes | Infrastructure or mesh topology; compare physical zone roles and complete report definitions |

| Audit method / limitation | Evidence |
| --- | --- |
| Verified restoration route | Version-252 surface-tension TUI plus two RP flags; common source and 342k paired save/reopen proof in [native correction probe](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-bulk-native-probe-readback.json) |
| Rejected archive workaround | Changing only the stored Simonin entry did not survive native resave; removed from the production runner |
| Settings tree alone is insufficient | Both trees reported inactive `phase_interaction`; native `domains` showed the surface-tension and interaction differences |
| Native domain inspection | [08b domains](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/08b-domains.json), [Phase 9 domains](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/phase9-domains.json) |
| Full native setup/solution snapshots | [08b](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/08b-native.json), [Phase 9 before correction](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/phase9-before.json) |
| Full leaf comparison | [1376 raw leaf differences](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-settings-differences.json); count includes added reports, inactive parameters and topology |
| Domain comparison | [16 raw domain differences](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-domain-differences.json) |
| Matched 08b case/data check | [Native full-pair read and resave](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-full-pair-normalization-probe.json); reference unchanged, no solve; Simonin still retained |
| 08b native roundtrip | [Case-only native copy](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-native-roundtrip-probe.json); original file unchanged, no solve; its stored Simonin choice persists |
| Global Time Step probe | [Native probe](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/08b-settings-audit/08b-coupled-global-default-probe.json); no solve and no reference-file write |
| Human decisions | [Decision receipt](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-settings-human-decisions.json) |
| Final audit proof | [Approved native contract and paired verification](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-settings-audit-approved.json) |
| Claim limit | Settings parity and intentional differences; no solver convergence, steady film, final mesh convergence or physical validation claim |

| Session recovery | Evidence / limit |
| --- | --- |
| Failed probe | [Preserved probe receipt](../../../PyAnsys/output/phase9-mesh-convergence/20261007/08b-eulerian-setter-capability-probe.json); no solve; switch to Eulerian caused loss of solver connection |
| Valuable fields | Original source, original 342k pair and corrected 342k native pairs remain on server-local disk |
| Exit commands | No exit/termination command sent; connection helper uses `cleanup_on_exit=False` |
| Human control | Never exit Fluent; Server 3 restarted; preserved Mixture pair restored |
