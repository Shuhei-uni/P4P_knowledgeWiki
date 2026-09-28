# Phase 8 F3 — split inlet with two-way DPM fraction screen

## Question and contrast

At fixed nominal inlet speed and total vapor/liquid feed, how does two-way DPM coupling and allocation of inlet liquid to droplets change carrier behaviour and droplet carryover? Contrast with the matching [F2](../f2-split-inlet/setup.md) one-way point, and separately compare DPM fractions within F3. Historical anchors: [09c two-way coupling](../../phase-03-dpm-carryover-and-coupling/purnanto-09c-two-way-dpm-coupling/setup.md) and [09cV2 allocation](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV2-dpm-partition-control/setup.md).

## Matrix and parent

Use all five Phase 8 speeds (`20.11`, `23.46`, `26.81`, `29.48`, `32.14 m/s`) crossed with injected-DPM fractions (`2.5%`, `5%`, `7.5%`, `10%`, `20%`): **25 intended cases**. Start each child independently from its same-speed verified F2 DPM-off carrier pair; do not serially carry fields from one fraction to another. Keep the physical inlet areas, phase-feed proportion, total liquid feed, outlet and closed bottom, mesh, materials, turbulence, solver settings, zero roughness, and EWF-off state fixed. Activate interaction with continuous phase and verify DPM source-update settings/readback before solving.

For each case, set `m_DPM = f_DPM × total liquid feed` and `m_Eulerian_liquid = (1 − f_DPM) × total liquid feed`; retain vapor feed. Use the project-designed [09cV3 seven-bin fine-mist PSD](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/setup.md#3-controlled-change-seven-injection-fine-mist-psd) at fixed relative weights; preserve injection direction/footprint, wall fates, and tracking controls across fractions. The nominal speed label refers to the pre-allocation total feed/volumetric basis; the Eulerian liquid-strip speed will fall as `f_DPM` rises and must be reported separately. DPM feedback can exchange mass/momentum/energy with the carrier; report applied source terms and avoid counting transfers twice in whole-system closure.

## Run sequence and evidence

Build each child from its F2 checkpoint, apply the allocation and coupling delta, verify phase inlet mass and DPM represented mass, install the [common reports](../report-contract.md) plus DPM source/fate histories, then save/reopen and smoke before the declared coupled continuation. Use declared blocks and Fluent-local checkpoints; preserve failure coordinates, report completeness, and checkpoint identity. Analyse only matching native offsets from activation, not the inherited F2 warm-up.

Core figures: **F3-A** DPM escaped/trapped/incomplete mass fraction against injected fraction at each speed; **F3-B** phase-resolved outlet routing, liquid inventory/storage, and whole-system source-inclusive closure against fraction; **F3-C** F2 diagnostic versus F3 allocated-coupled 5% comparison, explicitly labelled as a combined allocation-and-coupling change. Show raw trajectories behind window summaries.

## Decision and claim limit

The fraction sweep identifies sensitivity to an assumed inlet droplet allocation. It does not identify the real geothermal mist fraction or prove separator efficiency. F2 retains full Eulerian feed with diagnostic one-way tracking, while F3 reallocates liquid and couples DPM; the F2/F3 difference is a **combined package effect**, not an isolated coupling effect. A 5% one-way allocated bridge at each speed is an optional add-on if later evidence makes coupling attribution important. Record incomplete trajectories as unresolved rather than trapped.
