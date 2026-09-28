# Phase 8 F1 — mixed one-inlet carrier and one-way DPM

## Question and lineage

On the Phase 8 60k geometry, how do carrier routing and post-development droplet fates vary with inlet speed when both phases enter through one mixed physical opening? This is a new Purnanto-style comparison, not numerical reproduction of the old mesh or paper results. Historical anchors: [audited reference](../../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/setup.md) and [one-inlet recreation](../../phase-02-parity-reset-and-pre-v2-qualification/purnantov2-08-one-inlet-massflow-recreation/setup.md).

## Parent and controlled design

### Phase 8 source-case constraint (2026-09-26)

The requested source is `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5`, alongside `Separator-purnanto-60k.msh.h5` in the same folder on `student`. The source case is a full-mesh 08b artifact, approximately 243 MB. The live `student` Fluent 2025 R2 session is Student Edition and rejected this case with its 1,048,576-cell limit; it then rejected the 60k mesh until Fluent is restarted. Therefore the source case has **not** been loaded, its settings have **not** been imported, and no F1 base case has been saved. Do not label a reconstruction as a direct case import.

The user subsequently selected a Phase 7.2A 60k case as the new parent. The actual parent is Family E `E0`'s `P72A-E0-prepared.cas.h5` from `20260922T115500Z` on `student` (SHA-256 `1c5b1a5f5e68fcc6ff7248b50f6df83e788363faf7492315da42960fbce3e9f5`). Fluent read back `60,964` cells and two fluid zones; the lower zone remains as an inert mesh partition after every source is disabled. The historical six-bin injections were removed, both inlet faces now carry the same mixed phase feed, and a new Hybrid initialization replaced the Phase 7.2A field. See [F1 build results](results.md) for the child identity and readback. F2–F4 must use this same mesh partition unless a separately named mesh study deliberately changes it.

Build from the verified Phase 7.2A E0 `60,964`-cell case on the 60k geometry with a fresh, documented initialization for each speed; do not inherit its absorber-developed flow field. The E0 case already contains the lower cell-zone partition, retained without active sources. Treat existing `liquidinlet` and `steaminlet` faces as one combined physical inlet by assigning the same mixed-phase state and direction to both. For a mass-flow inlet, distribute each phase's **total** target over the two face zones in proportion to verified face area; do not apply the full target to each face. Confirm summed realized phase flows. A single merged inlet zone is acceptable only if it preserves the identical physical faces and is documented as a mesh-zone operation.

| Quantity | F1 rule |
| --- | --- |
| Nominal speeds | `20.11`, `23.46`, `26.81`, `29.48`, `32.14 m/s` |
| Feed basis | Same 1600 kJ/kg phase proportion and material state across speeds; mass commands computed from verified inlet area and densities |
| Lower boundary | Closed wall; phase-2 absorber off; no resolved brine outlet |
| Carrier | Steady Mixture with the documented common RNG k-epsilon/material/gravity/outlet/numerical stack; EWF off, roughness zero |
| DPM | Inject only after the carrier development gate; diagnostic one-way tracking with interaction with continuous phase off; use the seven-bin 09cV3 PSD, common wall fates, and tracking controls as F2 |

All five cases use the [common report contract](../report-contract.md). Freeze the carrier settings and DPM protocol across speeds except for the imposed flow. The chosen PSD is the project-designed [09cV3 seven-bin fine-mist distribution](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/setup.md#3-controlled-change-seven-injection-fine-mist-psd), an assumed engineering prior rather than a measured inlet distribution. F1/F2 tracking is **diagnostic**: retain the full Eulerian liquid feed, disable DPM feedback, and do not add nominal parcel mass to the physical inlet mass balance. Fluent may require nonzero injection parcel weights for mass-weighted fate reporting; label those weights as diagnostic, not additional physical feed. Set their common scale before execution and preserve it at every speed.

Use the same `steaminlet` face as the DPM release surface in F1 and F2, even though both F1 inlet faces carry the mixed continuous-phase condition. This keeps the physical release footprint fixed across the topology comparison; verify that the face is accessible for injection in both setups.

## Run sequence and evidence

1. Verify mesh hash, face areas/zones, boundary readback, and Fluent mesh check. Save a source-free initialized pair and setup manifest for each speed.
2. Install and smoke the common phase-flux, inventory, source-inclusive boundary-balance, pressure-drop, residual, and event reports before solving. Run the carrier in large declared blocks with Fluent-local checkpoints, recording the full native trajectory.
3. Declare the carrier assessment window from report histories. A closed bottom can retain liquid during iteration; document inventory slope per native iteration and boundary balance separately. A long run or low residual alone does not establish a stationary separator state.
4. Save the developed carrier pair and then activate the common one-way DPM injection. Record injected, escaped, trapped, and incomplete parcel counts and diagnostic weights by size and boundary. DPM tracking must not alter the saved carrier; any further carrier iterations are a separately labelled continuation.
5. Preserve settings/readback, commands, transcript, report files, checkpoint hashes, failure coordinate if any, and a machine manifest in `PyAnsys/`; link them from results.

Core figures: **F1-A** inlet speed/feed versus phase-resolved `steamoutlet` routing and pressure drop; **F1-B** carrier liquid inventory versus iteration, source-inclusive boundary balance, and numerical health; **F1-C** DPM fate versus speed, showing incomplete fraction beside escape fraction. Compare matching carrier windows and DPM settings against F2 at each speed.

## Decision and claim limit

F1 establishes a documented mixed-inlet reference if each speed has verified feed, reports, and DPM accounting. An outlet dryness or escaped-parcel fraction is a conditional diagnostic while liquid accumulates or tracks remain incomplete. F1/F2 inlet-topology attribution requires the same total feed, DPM representation, numerics, and lower boundary.
