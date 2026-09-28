# Stage 2 E2.7+R3 — phase-accretion EWF with R3 roughness

## Scientific test

Starting from the E2.7 continuation at native 13586, test whether the R3
outer-wall roughness setting changes phase-2 `steamoutlet` response, film
behaviour, or total bulk liquid inventory over 3,000 additional iterations.
Compare with the common parent and the E2.7+R4/R5 children under the
[Stage 2 comparison contract](../index.md).

## Parent and controlled delta

Load the **durable final** `P72A-E2.7-CONT5000-final-N13586.cas.h5` and
matching `.dat.h5` from the local OneDrive `Phase72A/FamilyE/E2.7-continuation-5000/20260923T102912Z`
folder. Verify the pair hashes, native coordinate, and E2.7 EWF readback
listed in the Stage 2 contract. Apply `k_s=5e-4 m`, `C_s=0.5` only on
`separator-purnanto:1`, `separator-purnanto:1:001`, `wall`, and `wall:004`.
All other settings remain those of the loaded pair. Save/reopen the prepared
child and read back roughness and EWF settings before solving.

## Run and measurements

Run one native `/solve/iterate 3000`; target native 16586 without
reinitialization. Retain per-iteration native reports and plot signed phase-2
`steamoutlet` flux, EWF total film mass, maximum thickness, average film
speed, wetted area, and total bulk liquid inventory. Establish and validate
the wetted-area measurement before the solve as specified in the Stage 2
contract. Preserve absorber/closure, residual, event, and paired-checkpoint
evidence for interpretation. Use server-local intermediate checkpoints and
shareable start/final case/data pairs only in OneDrive.

## Interpretation limit

A lower outlet magnitude must be interpreted with film and inventory trends,
closure, and solver health. Completion alone does not establish a stationary
film or physical drainage.
