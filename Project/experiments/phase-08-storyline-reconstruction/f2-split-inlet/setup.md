# Phase 8 F2 — split two-phase carrier and one-way DPM

## Question and contrast

At each Phase 8 speed, what changes when the same total vapor/liquid feed enters through separate pure-phase faces instead of F1's mixed physical opening? The intended controlled delta from [F1](../f1-one-inlet/setup.md) is inlet phase topology. Historical anchor: [08b split-inlet record](../../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md).

## Parent and frozen context

Derive each F2 base from the corresponding verified F1 base on the identical `60,964`-cell Phase 7.2A mesh partition, then initialize a fresh field. Retain total physical inlet area and face geometry. Apply phase-2 Eulerian liquid through outer `liquidinlet` and phase-1 vapor through inner `steaminlet`; verify pure-phase boundary readback and realized flux. Use the same nominal speeds `20.11`, `23.46`, `26.81`, `29.48`, and `32.14 m/s`, same 1600 kJ/kg phase proportion, closed bottom, `steamoutlet`, carrier physics, numerics, zero roughness, and EWF off as F1. The historical split-area ratio is only an initial design; actual 60k face areas and resulting zone velocities must be read back.

Use the same post-development **diagnostic** one-way DPM protocol and project-designed seven-bin 09cV3 PSD as F1. Retain the full Eulerian liquid feed and keep DPM interaction with continuous phase off. Release from the same physical `steaminlet` face in F1 and F2, with identical release footprint, direction rule, diagnostic parcel weights, wall fates, and tracking controls. Do not include diagnostic parcel weights as additional physical inlet liquid. Verify the F1/F2 injection readback after save/reopen.

## Run sequence and evidence

For each speed, verify face-zone and feed readback, create/verify the [common reports](../report-contract.md), initialize afresh, and develop the carrier under the same block/checkpoint and assessment rule as F1. Preserve a developed carrier pair before turning on one-way DPM. Track DPM without carrier feedback and retain complete fate counts/mass by size, boundary, and completion status. Save machine evidence and hashes in `PyAnsys/`.

Core figures: **F2-A** matched F1/F2 phase-resolved outlet flux and pressure drop versus speed; **F2-B** F1/F2 liquid inventory slope per native iteration, source-inclusive boundary balance, and residual/event adequacy; **F2-C** F1/F2 DPM escape/trap/incomplete response versus speed. Include near-inlet phase-fraction/velocity contours on the same geometric plane if the routing difference is used as a spatial claim.

## Decision and claim limit

Attribute a matched difference to inlet topology only after feed, DPM injection footprint/mass, boundary areas, solver settings, and comparison windows pass the parity audit. The closed bottom prevents a steady liquid-removal claim; report accumulation explicitly. F2 is the carrier parent for F3/F4 at each speed, using a verified DPM-off developed checkpoint.
