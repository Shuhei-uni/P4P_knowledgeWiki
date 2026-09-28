# Phase 8 F4 — coupled DPM plus Eulerian Wall Film

## Question and contrast

At matched speed and inlet-DPM fraction, does adding EWF to [F3](../f3-coupled-dpm/setup.md) change film formation, droplet fate, phase routing, or liquid storage without an unaccounted transfer? This is a new-mesh mechanism test; historical [Phase 4 EWF](../../phase-04-ewf-wall-film-mechanisms/interpretation.md) and current [Phase 7.2A EWF](../../phase-07-2a-wall-liquid-routing/ewf-family/results.md) constrain interpretation but are not quantitative baselines.

## Matrix, parent, and controlled delta

Repeat F3's five speeds × five injected-DPM fractions: **25 intended cases**. For each point, start independently from the same-speed F2 DPM-off developed carrier pair used by its F3 counterpart. Apply the same F3 liquid/DPM allocation and two-way DPM settings; enable EWF as the additional model package. Keep mesh, inlet areas, feed, closed bottom, no absorber, smooth-wall roughness, materials, the project-designed 09cV3 seven-bin PSD, injection footprint, and DPM controls matched to F3.

**Human-selected mechanism intent:** bulk phase accretion, DPM droplet deposition, splash, particle stripping, DPM interaction with the continuous phase ON, and film momentum transport. Apply EWF only to the boundary zone named `wall`; keep `bottom` and all other walls out of EWF. Set Boundary Conditions → `wall` → EWF → **Flow Momentum Coupling OFF** and verify `enable_flow_momentum_coupling = false` before and after save/reopen. The film still solves its own transport/momentum. Fluent's separate EWF Coupled Solution is a numerical solver option, not the wall coupling checkbox; inherit its eventual setting from finalized Phase 7.2A and record it explicitly.

**Finalization dependency:** F4 is intended to compare directly with the *finalized* Phase 7.2A EWF treatment, which does not yet exist. Treat the mechanism list above as design intent, not a final Fluent switch manifest. Once Phase 7.2A is finalized, extract its EWF model settings, wall settings, film numerical controls, and supported transfer reports; reconcile them with the F4 intent and record every deliberate difference, including F4's missing absorber and its coupled DPM injections. Do not launch F4 until this comparison basis is confirmed in its setup revision.

**Surface-tension value to settle at finalization:** F4's EWF film momentum model has a *separate* wall-film surface-tension coefficient and a separate Surface Tension momentum term. The current Phase 7.2A E2.7 build readback showed the term off (`surface-tension? = false`) and a stored `0.07194 N/m` value; the stored number is not evidence of an active force. Purnanto's separator-condition reference is `0.0411 N/m`. Record whether the finalized 7.2A film uses surface tension and, if so, its chosen coefficient and source, then explicitly set and read back the F4 value. Do not confuse this film parameter with a bulk interfacial surface-tension force, which is unavailable in the present Fluent 2025 R2 Mixture carrier setup.

Verify every EWF model and wall setting after build and save/reopen; log when Fluent changes another setting as a dependency. Keep separate report streams for bulk-to-film accretion, droplet-to-film deposition, splash return, stripped film-to-DPM transfer, film inventory/transport, and any film/bulk feedback.

## Run sequence and evidence

At each point, verify F3 parity and EWF wall/model settings, install [common reports](../report-contract.md) plus film mass, thickness, velocity, accretion, transfer, and outlet-flow histories, save/reopen and smoke, then run a matched native-offset continuation. Store Fluent-local checkpoints, report files, event/transcript evidence, and machine manifest. A cap hit, numerical failure, or missing transfer report is recorded at its first coordinate, not interpreted as film drainage or improved separation.

Core figures: **F4-A** matched F3/F4 phase-2 `steamoutlet` flow and DPM fate at each speed/fraction; **F4-B** film mass/thickness and transfer/flow trajectories, including storage; **F4-C** whole-system liquid accounting and numerical health with the F3 counterpart. Add a fixed-plane wall-adjacent film/velocity view only when a spatial routing mechanism is claimed.

## Decision and claim limit

An apparent reduction in bulk liquid carryover is useful only if film/DPM transfer, inventory, and outlet accounting explain where the liquid went. F4 adds a **combined EWF mechanism package**; the matched F3/F4 contrast measures that package's effect, not separate causal effects of accretion, deposition, splash, or stripping. Matching a finalized 7.2A EWF switch list will support setup comparison, but its absorber and DPM differences must remain visible. No film mass endpoint alone proves drainage, no short survival proves numerical adequacy, and no result establishes a physical plant separation efficiency.
