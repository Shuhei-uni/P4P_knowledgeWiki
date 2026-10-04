# Phase 8 F1 — mixed one-inlet carrier and one-way DPM

## Current family identity

| Item | Current family identity |
| --- | --- |
| — | F1 owns only the mixed-inlet Coupled / Global Time Step / first-order-k series |
| SIMPLE series | is now [F0](../f0-simple/setup.md) |
| — | Older SIMPLE setup details below preserve build lineage and do not select SIMPLE for F1 |

## Current execution purpose

| Item | Current execution purpose |
| --- | --- |
| The [2026-09-30 phase clarification](../CONTEXT.md#question-and-goal) governs this setup | reproduce this stage in the simulation history using verified settings and a declared bounded horizon |
|  | Balance, inventory, continuity, and track-completeness thresholds below belong to earlier numerical assessment plans; they are diagnostics and claim limits, not current DPM-activation, family-progression, or completion gates |
|  | Do not continue or change solver controls solely to cross those thresholds |
|  | Preserve prior outcomes and label numerical adaptations separately |
|  | The phase remains paused |

## Question and lineage

| Item | Question and lineage |
| --- | --- |
| — | On the Phase 8 60k geometry, how do carrier routing and post-development droplet fates vary with inlet speed when both phases enter through one mixed physical opening? |
| This | is a new Purnanto-style comparison, not numerical reproduction of the old mesh or paper results |
| — | Historical anchors: [audited reference](../../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/setup.md) and [one-inlet recreation](../../phase-02-parity-reset-and-pre-v2-qualification/purnantov2-08-one-inlet-massflow-recreation/setup.md) |

## Parent and controlled design

### Phase 8 source-case constraint (2026-09-26)

| Item | Phase 8 source-case constraint (2026-09-26) |
| --- | --- |
| requested source | is `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5`, alongside `Separator-purnanto-60k.msh.h5` in the same folder on `student` |
| source case | is a full-mesh 08b artifact, approximately 243 MB |
| live `student` Fluent 2025 R2 session | is Student Edition and rejected this case with its 1,048,576-cell limit; it then rejected the 60k mesh until Fluent is restarted |
| — | Therefore the source case has not been loaded, its settings have not been imported, and no F1 base case has been saved |
|  | Do not label a reconstruction as a direct case import |

<details>
<summary>Supporting detail — Phase 8 source-case constraint (2026-09-26)</summary>

| Item | Phase 8 source-case constraint (2026-09-26) |
| --- | --- |
| — | The user subsequently selected a Phase 7.2A 60k case as the new parent |
| actual parent | is Family E `E0`'s `P72A-E0-prepared.cas.h5` from `20260922T115500Z` on `student` (SHA-256 `1c5b1a5f5e68fcc6ff7248b50f6df83e788363faf7492315da42960fbce3e9f5`) |
| — | Fluent read back `60,964` cells and two fluid zones; the lower zone remains as an inert mesh partition after every source is disabled |
| historical six-bin injections | were removed, both inlet faces now carry the same mixed phase feed, and a new Hybrid initialization replaced the Phase 7.2A field |
| — | See [F1 build results](results.md) for the child identity and readback |
|  | F2–F4 must use this same mesh partition unless a separately named mesh study deliberately changes it |
|  | Build from the verified Phase 7.2A E0 `60,964`-cell case on the 60k geometry with a fresh, documented initialization for each speed; do not inherit its absorber-developed flow field |
| E0 case already contains the lower cell-zone partition, | retained without active sources |
| — | Treat existing `liquidinlet` and `steaminlet` faces as one combined physical inlet by assigning the same mixed-phase state and direction to both |
|  | For a mass-flow inlet, distribute each phase's total target over the two face zones in proportion to verified face area; do not apply the full target to each face |
|  | Confirm summed realized phase flows |
| A single merged inlet zone | is acceptable only if it preserves the identical physical faces and is documented as a mesh-zone operation |

</details>

| Quantity | F1 rule |
| --- | --- |
| Nominal speeds | `20.11`, `23.46`, `26.81`, `29.48`, `32.14 m/s` |
| Feed basis | Same 1600 kJ/kg phase proportion and material state across speeds; mass commands computed from verified inlet area and densities |
| Lower boundary | Closed wall; phase-2 absorber off; no resolved brine outlet |
| Carrier | Steady Mixture with the documented common RNG k-epsilon/material/gravity/outlet/numerical stack; EWF off, roughness zero |
| DPM | Inject after the declared bounded carrier-development run and saved-state verification; diagnostic one-way tracking with interaction with continuous phase off; use the seven-bin 09cV3 PSD, common wall fates, and tracking controls as F2 |

| Phase 8 source-case constraint (2026-09-26) |
| --- |
| With the verified combined face area and fixed phase densities, scale both reference mass commands by `speed / 26.81` |
| The selected design targets are: |

| Nominal speed (m/s) | Vapor feed (kg/s) | Liquid feed (kg/s) |
| ---: | ---: | ---: |
| 20.11 | 60.53471824 | 87.71494927 |
| 23.46 | 70.61882098 | 102.32683788 |
| 26.81 | 80.70292372 | 116.93872650 |
| 29.48 | 88.74010411 | 128.58461981 |
| 32.14 | 96.74718271 | 140.18689555 |

| Item | Phase 8 source-case constraint (2026-09-26) |
| --- | --- |
| — | For F1, partition each phase target between both faces by verified area; for F2, put the entire liquid target on `liquidinlet` and vapor target on `steaminlet` |
|  | Read back the phase commands and nominal versus zone-specific superficial speeds at every point |
|  | All five cases use the [common report contract](../report-contract.md) |
|  | Freeze the carrier settings and DPM protocol across speeds except for the imposed flow |
| chosen PSD | is the project-designed [09cV3 seven-bin fine-mist distribution](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/setup.md#3-controlled-change-seven-injection-fine-mist-psd), an assumed engineering prior rather than a measured inlet distribution |
| F1/F2 tracking | is diagnostic: retain the full Eulerian liquid feed, disable DPM feedback, and do not add nominal parcel mass to the physical inlet mass balance |
| Fluent may | require nonzero injection parcel weights for mass-weighted fate reporting; label those weights as diagnostic, not additional physical feed |
| — | Set their common scale before execution and preserve it at every speed |

### Selected Purnanto-parity child (2026-09-29)

| Item | Selected Purnanto-parity child (2026-09-29) |
| --- | --- |
| selected F1 26.81 m/s start pair | is `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\PurnantoParity\F1\F1-purnanto-parity-26p81.cas.h5` and its matching `.dat.h5`, built from the retained initialized F1 base |
| — | Live Fluent 2025 R2 readback after save/reopen verified SIMPLE, segregated pseudo-time off, second-order `k`, a common `0.724 m` inlet turbulence hydraulic diameter on both faces, `2.11%` inlet turbulence intensity, and `0.724 m` / `2.1525%` outlet backflow turbulence inputs |
|  | The `26.81 m/s` design feed, 60,964-cell mesh, mixture/RNG physics, zero roughness, closed bottom, inactive absorber, and no DPM injections remain |
|  | See the machine receipt under `PyAnsys/output/phase8_purnanto_parity_pilots_20260928T110152Z.json` and its builder |
| original 2026-09-26 pair | remains a separate Coupled/Global-Time-Step baseline |

<details>
<summary>Supporting detail — Selected Purnanto-parity child (2026-09-29)</summary>

| Item | Selected Purnanto-parity child (2026-09-29) |
| --- | --- |
| two physical inlet faces | remain separate mesh zones, so this child is a Purnanto-style approximation on the Phase 8 geometry |
| — | Assigning `0.724 m` to each face deliberately reproduces the historical single-inlet turbulence input; it is not a measurement of the thin strip's own hydraulic diameter |
| Fluent's [2025 R2 User's Guide, Figure 8.38](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html) | shows the mass-flow-inlet panel and describes the phase/boundary inputs used here |
| `0.0411 N/m` reference surface-tension value | remains inactive in this Mixture carrier |
| — | After the SIMPLE parity pilot failed its carrier gate, a separately named matched numerical-recovery child was built at `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\NumericalRecovery\F1\F1-26p81-coupled-gts.cas.h5` with its paired `.dat.h5` |
|  | The [build receipt](../../../../PyAnsys/output/phase8_numerical_recovery_f1_20260928T131400Z.json) verifies the same Coupled/Global Time Step/first-order-`k` methods, corrected inlet/outlet turbulence inputs, mixed feeds, fresh Hybrid initialization, and save/reopen identity |
|  | Direct readback comparison with the F2 recovery receipt confirmed equal numerical methods and turbulence settings |
| This branch | is a recovery comparison, not a recreation of Purnanto's SIMPLE result |
| — | Report the same last-500 numerical diagnostics as [F2](../f2-split-inlet/setup.md); threshold failure does not prevent labelled diagnostic DPM from a usable saved state |
| matched F1/F2 discovery pilot | uses the 26.81 m/s children for 2,000 native steady iterations: report cadence 10, an initial 50-iteration instrumentation smoke, a local checkpoint at 1,000, and final paired case/data at 2,000 |
| — | Compare the full trajectories and last 500 iterations |
|  | Continue to a predeclared deeper horizon if inventory or boundary balance is still evolving; the pilot alone cannot establish a stationary separator |

</details>

### Bounded all-speed SIMPLE carrier sweep (2026-10-01)

| Item | Bounded all-speed SIMPLE carrier sweep (2026-10-01) |
| --- | --- |
| authorized F1 SIMPLE sweep | uses a fresh Hybrid initialization from the verified F1 Purnanto-parity child at each nominal speed, then runs exactly `10,000` active steady iterations per speed in one `50`-iteration instrumentation smoke followed by `1,000`-iteration batches |
| — | Save Fluent-local checkpoints every `1,000` iterations and the final case/data pair at N10,000; compare the full trajectory and the predeclared N9,500–10,000 window |
|  | This horizon matches the completed F1/F2 Coupled comparison endpoints and retains the prior SIMPLE N2,000 pilots as early-history evidence |
| N10,000 | is a bounded storyline horizon, not a convergence or balance target |
| — | Do not extend or change methods based on diagnostic thresholds |

<details>
<summary>Supporting detail — Bounded all-speed SIMPLE carrier sweep (2026-10-01)</summary>

| Item | Bounded all-speed SIMPLE carrier sweep (2026-10-01) |
| --- | --- |
| earlier 23.46 m/s SIMPLE start manifest (`F1-23p46-20260928T194516Z`) | records a saved start pair and was interrupted before any carrier iteration because it belonged to the then-selected Coupled sweep |
| Its run ID | is therefore retained as excluded-before-solve evidence; this all-speed SIMPLE sweep is a distinct attempt from the same verified 26.81 m/s source pair with a fresh initialization |
| — | The audited original `00a` record reports one mixed `mass-flow-inlet.inlet` (vapor `80.69`, liquid `116.92 kg/s`) and pressure-based steady Mixture/RNG flow with SIMPLE, node-based Green–Gauss gradients, PRESTO!, second-order momentum/`k`/epsilon and QUICK volume fraction. `08b` deliberately changed the inlet topology to two split `mass-flow-inlet` boundaries (`liquidinlet` and `steaminlet`) while targeting those same total phase feeds |
| its reported carrier field | was at N5,000 and its report showed a large open mixture imbalance |
| 08b rebuild record also | retains replay differences in operating density/temperature, initialization patch and continuity threshold |
| — | Its mesh has 7,601,261 cells |
|  | F1 instead applies the mixed-phase feed to both inlet faces of the 60,964-cell Phase 8 mesh |
| F1 SIMPLE package reproduces the | recorded 00a numerical-method family (with segregated pseudo-time off and second-order `k`, node-based gradients and the verified Phase 8 turbulence inputs); Coupled/Global Time Step F1 runs are a separately labelled numerical-recovery package |
| — | A shared SIMPLE label alone does not establish 08b parity |
|  | Interpret differences as combined mesh, inlet representation, feed, initialization, and numerical-package effects where those dimensions differ; this is not a mesh-identical or topology-identical replay of 08b |
|  | Use the same `steaminlet` face as the DPM release surface in F1 and F2, even though both F1 inlet faces carry the mixed continuous-phase condition |
|  | This keeps the physical release footprint fixed across the topology comparison; verify that the face is accessible for injection in both setups |
|  | For the seven-bin one-way diagnostic, set the sum of Fluent injection parcel weights to 5% of the actual 26.81 m/s liquid feed (`5.846936325 kg/s` at this reference point), distributed by the recorded 09cV3 bin shares; scale with liquid feed at the other four speeds |
|  | This matches the F3 5% point's nominal droplet representation while keeping the entire liquid feed in the F1/F2 Eulerian inlets |
|  | The parcel weights have no carrier feedback or additional physical inlet status |
|  | Save and reopen the injection state, and verify the same release location, velocity rule, tracking controls, and wall fates in F1/F2 before comparing fates |
| reference-speed injection builder starts with the | recorded 09cV2/09cV3 axial `x` release velocity of `27.118 m/s`, a requested 100 release streams per bin, spherical drag, no stochastic dispersion or rotation, 50,000 maximum tracking steps, and step-length factor 5 |
| — | Fluent's surface-injection tracking may realize a different number of trajectories; record the actual count |
| These | are inherited diagnostic controls, not a claim that the current steam-face carrier speed is exactly `27.118 m/s`; its command-derived superficial speed is about `26.807 m/s` |
| — | At other nominal speeds, scale the axial release velocity by `speed/26.81` as a declared flow-loading rule; use the same rule in F1/F2/F3/F4 and verify it after save/reopen |
|  | Hold the remaining injection controls identical across F1/F2 and record their live readback |

</details>

### Completed SIMPLE reconstruction evidence (2026-10-01)

| Item | Completed SIMPLE reconstruction evidence (2026-10-01) |
| --- | --- |
| — | The five-speed F1 SIMPLE reconstruction and its fixed-5% one-way DPM diagnostics are complete |
|  | Each carrier starts from the same verified two-face source pair with fresh Hybrid initialization, SIMPLE, segregated pseudo-time off, second-order `k`, and N10,000 horizon; diagnostic assessments use N9,500–10,000 |
|  | The solver package differs from the selected Coupled/Global Time Step, first-order-`k` sweep, so the matched results isolate neither SIMPLE alone nor any single discretization change |
| Numerical thresholds | remain claim limits, not progression gates |

| Speed (m/s) | Carrier manifest | Window assessment | Diagnostic DPM receipt |
| ---: | --- | --- | --- |
| 20.11 | [manifest](../../../../PyAnsys/output/phase8-carrier/F1-20p11-20260930T110412Z/manifest.json) | [assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f1-simple-n10000/assessment.json) | [build](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-20p11-20260930T150944Z/build.json) |
| 23.46 | [manifest](../../../../PyAnsys/output/phase8-carrier/F1-23p46-20260930T115334Z/manifest.json) | [assessment](../../../../PyAnsys/output/phase8-analysis/23p46-f1-simple-n10000/assessment.json) | [build](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-23p46-20260930T151549Z/build.json) |
| 26.81 | [manifest](../../../../PyAnsys/output/phase8-carrier/F1-26p81-20260930T124257Z/manifest.json) | [assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f1-simple-n10000/assessment.json) | [build](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-26p81-20260930T152153Z/build.json) |
| 29.48 | [manifest](../../../../PyAnsys/output/phase8-carrier/F1-29p48-20260930T133143Z/manifest.json) | [assessment](../../../../PyAnsys/output/phase8-analysis/29p48-f1-simple-n10000/assessment.json) | [build](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-29p48-20260930T152728Z/build.json) |
| 32.14 | [manifest](../../../../PyAnsys/output/phase8-carrier/F1-32p14-20260930T142022Z/manifest.json) | [assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f1-simple-n10000/assessment.json) | [build](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-32p14-20260930T153305Z/build.json) |

| Item | Completed SIMPLE reconstruction evidence (2026-10-01) |
| --- | --- |
| comparison summary and weighted-fate summary | are in [machine analysis](../../../../PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/summary.json) and [diagnostic DPM analysis](../../../../PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/f1-simple-diagnostic-dpm-fates.json) |
| — | All five carriers completed without fatal solver events, but all five fail the mixture-gap, continuity, and inventory-slope diagnostics |
|  | Keep their pressure, outlet-ratio, and particle-fate values conditional on these numerically poor carrier states |
| historical 08b anchor | remains a split-inlet run on 7,601,261 cells; the SIMPLE numerical-method lineage to audited 00a does not make this F1 topology/mesh-identical parity |

## Run sequence and evidence

| Item | Run sequence and evidence |
| --- | --- |
| — | Verify mesh hash, face areas/zones, boundary readback, and Fluent mesh check |
|  | Save a source-free initialized pair and setup manifest for each speed |
|  | Install and smoke the common phase-flux, inventory, source-inclusive boundary-balance, pressure-drop, residual, and event reports before solving |
|  | Run the carrier in large declared blocks with Fluent-local checkpoints, recording the full native trajectory |
|  | Declare the carrier assessment window from report histories |

<details>
<summary>Supporting detail — Run sequence and evidence</summary>

| Item | Run sequence and evidence |
| --- | --- |
| — | A closed bottom can retain liquid during iteration; document inventory slope per native iteration and boundary balance separately |
|  | A long run or low residual alone does not establish a stationary separator state |
|  | Save the developed carrier pair and then activate the common one-way DPM injection |
|  | Record injected, escaped, trapped, and incomplete parcel counts and diagnostic weights by size and boundary |
|  | DPM tracking must not alter the saved carrier; any further carrier iterations are a separately labelled continuation |
|  | Preserve settings/readback, commands, transcript, report files, checkpoint hashes, failure coordinate if any, and a machine manifest in `PyAnsys/`; link them from results |
| Core figures | F1-A inlet speed/feed versus phase-resolved `steamoutlet` routing and pressure drop; F1-B carrier liquid inventory versus iteration, source-inclusive boundary balance, and numerical health; F1-C DPM fate versus speed, showing incomplete fraction beside escape fraction |
|  | Compare matching carrier windows and DPM settings against F2 at each speed |

</details>

## Decision and claim limit

| Item | Decision and claim limit |
| --- | --- |
| — | F1 establishes a documented mixed-inlet reference if each speed has verified feed, reports, and DPM accounting |
| An outlet dryness or escaped-parcel fraction | is a conditional diagnostic while liquid accumulates or tracks remain incomplete |
| F1/F2 inlet-topology attribution | requires the same total feed, DPM representation, numerics, and lower boundary |
