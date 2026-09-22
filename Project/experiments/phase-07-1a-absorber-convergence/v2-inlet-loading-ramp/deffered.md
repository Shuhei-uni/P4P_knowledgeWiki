# Phase 7.1A — v2 inlet-loading ramp

> **Status — SELECTED COMMON BASELINE RULE (2026-09-22):** The earlier
> Server-3 approach was paused, but this v2 ramp is now re-adopted as the
> explicit first-2,000-iteration loading rule for the baseline and both new
> mechanism families. The completed result remains finite-horizon discovery
> evidence only.

## Question

Can the new 60k-mesh v2 virtual liquid outlet be exercised through the same
gradual inlet-development history used in the prior inlet-loading experiment,
while recording steam-outlet routing, applied phase-2 absorption, and total
liquid inventory?

This is the common v2 loading contract. It is a partial repeat of the prior
25%-start, 2,000-iteration inlet ramp, with the verified v2 60k mesh and
feed-forward virtual-outlet absorber. Every new roughness or EWF child must
apply this same loading history before its family-specific comparison is
interpreted.

## Parent and controlled schedule

- Parent: the exact prepared/reopened pair in
  `baseline-v2-virtual-liquid-outlet/run-paths.yaml`.
- Runtime: Fluent 2025 R2 on server `student`.
- Initialization: use the prepared v2 field as-is; do not patch or reset the
  liquid field.
- Start multiplier: `0.25` at active iteration `0`.
- Ramp: linear from `0.25` to `1.00` over `2,000` steady iterations.
- Inlet ratio: fixed at the prior experiment's recorded base targets,
  `116.92 kg/s` liquid and `80.69 kg/s` steam, so the instantaneous commands
  are `116.92 f` and `80.69 f`.
- Absorber: leave the v2 `P71V2Sink` source law authoritative. Its command is
  derived from the instantaneous liquid-inlet throughput; no uniform-source
  replacement or manual source retuning is allowed.
- Frozen boundaries: `steamoutlet` remains the only pressure outlet and all
  bottom boundaries remain walls. Phase 1 receives no direct source.

## Horizon and checkpoints

Run `2,000` native steady solver iterations in `10`-iteration control blocks.
Preserve paired case/data checkpoints at active `0`, `500`, `1,000`, `1,500`,
and `2,000`. Working checkpoints remain on the Fluent host's local disk; the
terminal pair is copied to the recorded OneDrive final root.

## Required evidence

The child-local native report package must record, on Fluent's native iteration
coordinate:

1. mixture, vapor, and liquid mass flux at `steamoutlet`;
2. liquid and steam inlet mass fluxes;
3. `P71V2Command`, named-expression removal, and native applied phase-2 source
   integral in the virtual-outlet zone;
4. lower-zone liquid availability and lower-zone liquid inventory; and
5. total liquid mass and liquid volume over both fluid zones.

Residual history, solver transcript, event readbacks, and final paired artifact
hashes are supporting evidence. Raw histories must remain available for later
plot-led analysis.

## Decision use and claim limit

Use the run to determine whether the new absorber receives liquid during the
loading path and how steam-outlet routing and total liquid inventory respond.
The run does not by itself establish steady convergence, bounded inventory,
physical absorber validity, or plant drainage performance. The absorber's
commanded rate and realized applied source must be kept distinct; a liquid-
starved lower zone is a diagnostic result, not a zero-demand confirmation.
