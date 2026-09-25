# E2.7 continuation — 5,000 additional iterations on Server 1

## Question

Does the E2.7 numerical response continue over another 5,000 steady iterations
from the native-8586 endpoint, while retaining per-iteration EWF film and flow
reports?

This is a horizon extension of E2.7, not a new controlled-physics contrast.
The EWF and flow settings remain those of E2.7. The requested native TUI solve
is `/solve/iterate 5000`, from native iteration `8586` to expected iteration
`13586`.

## Parent and identity checks

The input is the E2.7 final case/data pair copied into the local OneDrive sync
folder:

- `P72A-E2.7-full-loading-plus3000.cas.h5`
- `P72A-E2.7-full-loading-plus3000.dat.h5`

The synchronized pair hashes differ from the earlier E2.7 run-manifest hashes.
The copies match each other byte-for-byte between the Mac sync folder and
Server 1. Before this extension, Fluent 2025 R2 loaded the copied pair and
reported native iteration `8586`; Phase Accretion ON; maximum film thickness
`0.3 m`; ten film subiterations; fixed film timestep `1e-5 s`; Courant setting
`0.05`; EWF Coupled Solution ON; film-wall Flow Momentum Coupling OFF; and the
bottom is not a film wall. This checksum discrepancy is retained as a
provenance limitation for the extension.

## Run and evidence

Run on Server 1, continuing the loaded E2.7 pair without reinitialization or a
model-setting change. Retain the existing 26 Fluent-native report definitions
as active Fluent Report Files at every native iteration, writing into a fresh
Server 1 local run folder. The reports include maximum and area-weighted film
thickness, film mass, film Courant, phase transfer, phase-resolved outlet
fluxes, liquid inventory, absorber control, and other E2.7 flow monitors.
Retain native flow residual history and EWF residual messages. Configure local
paired autosave checkpoints every 250 iterations. Save start and final
case/data pairs to the run's OneDrive folder.

Issue one literal `/solve/iterate 5000` Fluent TUI command. A detached runner
records its terminal status, report histories, transcript, exact native
coordinate, and paired saves.

## Claim limits

A completed horizon can show whether the monitored quantities continued to
move or encountered numerical failure over this longer interval. It cannot by
itself establish convergence, stationary film behaviour, source-inclusive
closure, drainage, or a physical carryover benefit. No additional model
settings change is being tested.
