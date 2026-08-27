# Phase 1 — Purnanto baseline and inlet exploration

## Scientific purpose

Reconstruct the early Purnanto/reference context and test inlet and initial
phase representations before the parity reset.

## Retained experiments

- [purnanto-00-reference-spiral-boc](purnanto-00-reference-spiral-boc/setup.md) — reference setup and lineage authority.
- [purnanto-00a-live-setup-audit](purnanto-00a-live-setup-audit/setup.md) — audited 5,000-iteration baseline data; reference/diagnostic.
- [purnanto-02b-vof-split-inlet-transient](purnanto-02b-vof-split-inlet-transient/setup.md) — executed, rejected qualitative VOF diagnostic.
- [purnanto-03-mixed-wet-half-velocity-inlet](purnanto-03-mixed-wet-half-velocity-inlet/setup.md) — executed, non-converged diagnostic.
- [purnanto-03a-mixed-wet-half-water-pool](purnanto-03a-mixed-wet-half-water-pool/setup.md) — executed, rejected water-pool diagnostic.
- [purnanto-04-mixed-wet-half-actual-area](purnanto-04-mixed-wet-half-actual-area/results.md) — reported low-confidence flux/DPM diagnostic.
- [purnanto-07-pure-phase-actual-area](purnanto-07-pure-phase-actual-area/results.md) — reported non-converged pure-phase/DPM diagnostic.

## Phase outcome

The retained records establish that the early inlet and initialization
variants produced useful diagnostics but did not establish a stable,
report-ready separator baseline. The rejected VOF branch and unstable liquid
inventory observations remain evidence for the later parity reset.

## Remaining uncertainty

The exact provenance and native solve count of some historical reference
checkpoints are incomplete, and the early simplified geometry does not close
the same liquid balance as the later full-geometry branch.
