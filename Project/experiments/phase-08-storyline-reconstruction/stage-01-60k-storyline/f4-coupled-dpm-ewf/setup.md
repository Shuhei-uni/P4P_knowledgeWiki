# Phase 8 F4 — coupled DPM plus Eulerian Wall Film

## Authorized matched Server 1 batch

| Item | Authorized matched Server 1 batch |
| --- | --- |
| — | The [3 October direction](../CONTEXT.md#status) selects five matching F3/F4 speed/loading points, the unchanged Coupled/Global Time Step package, unaveraged DPM sources, source interval 100, held sources, source relaxation 0.5 and 50,000 tracking steps |
|  | Preserve the developed N10,000 carrier basis and run to N16,000 with 6,000 mechanism-active iterations; summaries use N15,500–16,000 |
|  | Only EWF differs between matched F3/F4 points |
|  | The [batch specification](../../../../../PyAnsys/output/phase8-server1-matched-20261003/batch-spec.json) owns exact immutable parents |
| This scoped batch | is complete and verified; the phase is paused at N16000 |

## Current execution purpose

| Item | Current execution purpose |
| --- | --- |
| The [2026-09-30 phase clarification](../CONTEXT.md#question-and-goal) governs this setup | reproduce this stage in the simulation history using verified settings and a declared bounded horizon |
|  | Balance, inventory, continuity, and track-completeness thresholds below belong to earlier numerical assessment plans; they are diagnostics and claim limits, not current DPM-activation, family-progression, or completion gates |
|  | Do not continue or change solver controls solely to cross those thresholds |
|  | Preserve prior outcomes and label numerical adaptations separately |
|  | The phase remains paused |

## Question and contrast

| Item | Question and contrast |
| --- | --- |
| — | At matched speed and inlet-DPM fraction, does adding EWF to [F3](../f3-coupled-dpm/setup.md) change film formation, droplet fate, phase routing, or liquid storage without an unaccounted transfer? |
| This | is a new-mesh mechanism test; historical [Phase 4 EWF](../../../phase-04-ewf-wall-film-mechanisms/interpretation.md) and current [Phase 7.2A EWF](../../../phase-07-2a-wall-liquid-routing/ewf-family/results.md) constrain interpretation but are not quantitative baselines |

## Matrix, parent, and controlled delta

| Item | Matrix, parent, and controlled delta |
| --- | --- |
| Repeat F3's five speeds × five injected-DPM fractions | 25 intended cases |
|  | For each point, start independently from the same-speed F2 DPM-off developed carrier pair used by its F3 counterpart |
|  | Apply the same F3 liquid/DPM allocation and two-way DPM settings; enable EWF as the additional model package |
|  | Keep mesh, inlet areas, feed, closed bottom, no absorber, smooth-wall roughness, materials, the project-designed 09cV3 seven-bin PSD, injection footprint, and DPM controls matched to F3 |
| Human-selected mechanism intent | bulk phase accretion, DPM droplet deposition, splash, particle stripping, DPM interaction with the continuous phase ON, and film momentum transport |

<details>
<summary>Supporting detail — Matrix, parent, and controlled delta</summary>

| Item | Matrix, parent, and controlled delta |
| --- | --- |
| Human-selected mechanism intent | Apply EWF only to the boundary zone named `wall`; keep `bottom` and all other walls out of EWF |
|  | Set Boundary Conditions → `wall` → EWF → Flow Momentum Coupling OFF and verify `enable_flow_momentum_coupling = false` before and after save/reopen |
|  | The film still solves its own transport/momentum |
|  | Fluent's separate EWF Coupled Solution is a numerical solver option, not the wall coupling checkbox; inherit its eventual setting from finalized Phase 7.2A and record it explicitly |
| — | For DPM deposition and splash to reach the Eulerian film, enable EWF DPM Coupling/Collection, enable splashing in the EWF model, and read back the film wall's DPM Interaction controls |
|  | Keep `bottom` as DPM trap and outside EWF |
| main wall | retains its inherited DPM `reflect` setting; [Fluent 2025 R2's EWF limitation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_limits.html) explicitly removes the DPM `wall-film` boundary option while EWF is active, because that option belongs to the incompatible Lagrangian Wall Film model |
| — | The [EWF wall guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html) places impingement and splash controls under the EWF wall-film tab instead |
| first provisional build's rejected `wall-film` attempt | is retained in its machine receipt; no case/data child was saved |
| — | If particle stripping automatically creates a separate injection, record and account for it apart from the seven inlet bins |
| Finalization dependency | F4 is intended to compare directly with the *finalized* Phase 7.2A EWF treatment, which does not yet exist |
|  | Treat the mechanism list above as design intent, not a final Fluent switch manifest |
|  | Once Phase 7.2A is finalized, extract its EWF model settings, wall settings, film numerical controls, and supported transfer reports; reconcile them with the F4 intent and record every deliberate difference, including F4's missing absorber and its coupled DPM injections |
|  | Do not launch F4 until this comparison basis is confirmed in its setup revision |
| Exploratory pilot basis under the 2026-09-29 continuation instruction | while Phase 7.2A remains unfinished, a separately named provisional 26.81 m/s, 5% F4 pilot may use the last directly recorded E2.7 control package as a technical starting point |
|  | It holds the F3 100-iteration DPM source cadence and E2.7's fixed film step `1e-5 s`, 10 maximum film sub-iterations, `0.3 m` exploratory cap, EWF Coupled Solution ON, phase accretion ON, and wall Flow Momentum Coupling OFF |
|  | It additionally enables EWF DPM collection, splash, and stripping, while retaining the main-wall DPM `reflect` setting that is available with EWF |
|  | This pilot tests whether the intended package can be built and monitored; it is not the finalized F3/F4 comparison or evidence that E2.7 film transport was qualified |
|  | The 25-case F4 matrix still needs a verified final 7.2A basis or a separately declared reinterpretation |
| Surface-tension value to settle at finalization | F4's EWF film momentum model has a *separate* wall-film surface-tension coefficient and a separate Surface Tension momentum term |
|  | The current Phase 7.2A E2.7 build readback showed the term off (`surface-tension? = false`) and a stored `0.07194 N/m` value; the stored number is not evidence of an active force |
|  | Purnanto's separator-condition reference is `0.0411 N/m` |
|  | Record whether the finalized 7.2A film uses surface tension and, if so, its chosen coefficient and source, then explicitly set and read back the F4 value |
|  | Do not confuse this film parameter with a bulk interfacial surface-tension force, which is unavailable in the present Fluent 2025 R2 Mixture carrier setup |
| Provisional live build readback | the [saved/reopened 5% child](../../../../../PyAnsys/output/phase8-ewf/F4-26p81-5pct-E27-provisional-20260928T163502Z/build.json) has the E2.7 film step and momentum package, phase accretion, EWF DPM collection, global splashing and stripping on. `wall` alone is a film wall, with Flow Momentum Coupling off, Stanton–Rutland impingement, DPM Wall Splash on and four splashed particles; `bottom` remains outside EWF and DPM trap |
|  | The main wall retains DPM `reflect` under the EWF compatibility rule |
|  | Fluent chose the existing `09cv3-finemist-89um` injection as a stripping/separation template because several injections qualified; no eighth named injection appeared in readback |
|  | This selection and any stripped/splashed parcel mass require separate accounting before interpreting F4 particle fate |
|  | The earlier [global-only splash child](../../../../../PyAnsys/output/phase8-ewf/F4-26p81-5pct-E27-provisional-20260928T163224Z/build.json) lacked the wall-level splash switch and is excluded from the intended pilot |
| — | Verify every EWF model and wall setting after build and save/reopen; log when Fluent changes another setting as a dependency |
|  | Keep separate report streams for bulk-to-film accretion, droplet-to-film deposition, splash return, stripped film-to-DPM transfer, film inventory/transport, and any film/bulk feedback |

</details>

## Run sequence and evidence

| Item | Run sequence and evidence |
| --- | --- |
| — | At each point, verify F3 parity and EWF wall/model settings, install [common reports](../report-contract.md) plus film mass, thickness, velocity, accretion, transfer, and outlet-flow histories, save/reopen and smoke, then run a matched native-offset continuation |
|  | Store Fluent-local checkpoints, report files, event/transcript evidence, and machine manifest |
| A cap hit, numerical failure, or missing transfer report | is recorded at its first coordinate, not interpreted as film drainage or improved separation |
| Core figures | F4-A matched F3/F4 phase-2 `steamoutlet` flow and DPM fate at each speed/fraction; F4-B film mass/thickness and transfer/flow trajectories, including storage; F4-C whole-system liquid accounting and numerical health with the F3 counterpart |
|  | Add a fixed-plane wall-adjacent film/velocity view only when a spatial routing mechanism is claimed |

## Decision and claim limit

| Item | Decision and claim limit |
| --- | --- |
| An apparent reduction in bulk liquid carryover | is useful only if film/DPM transfer, inventory, and outlet accounting explain where the liquid went |
| — | F4 adds a combined EWF mechanism package; the matched F3/F4 contrast measures that package's effect, not separate causal effects of accretion, deposition, splash, or stripping |
|  | Matching a finalized 7.2A EWF switch list will support setup comparison, but its absorber and DPM differences must remain visible |
|  | No film mass endpoint alone proves drainage, no short survival proves numerical adequacy, and no result establishes a physical plant separation efficiency |
