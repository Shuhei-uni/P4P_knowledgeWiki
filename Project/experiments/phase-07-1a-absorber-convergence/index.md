# Phase 7.1A — 60k Virtual Liquid Outlet

## Status

**Human-selected direction on 2026-09-22.** Phase 7.1A has been restarted from
a new baseline on the supplied 60k-cell mesh. The v1 lower-inventory controller
is no longer the active mechanism. V2 treats the lower phase-2 source as a
virtual liquid outlet whose commanded throughput follows the liquid inlet and
whose local removal is weighted by the liquid actually present.

The [v2 setup](baseline-v2-virtual-liquid-outlet/setup.md) has been built,
save/reopen verified, one-iteration smoke tested, and reloaded on `student`.
See the [build result](baseline-v2-virtual-liquid-outlet/results.md) for the
artifact hashes and exact readback. The first v2 liquid-development run is now
complete as the [inlet-loading ramp result](v2-inlet-loading-ramp/results.md):
the absorber realizes its command after lower-zone liquid develops, but the
finite trajectory remains nonstationary with growing total liquid inventory
and persistent outlet reverse flow.

Earlier turbulence, solver-path, inlet-ramp, and dynamic-ring material is
historical v1 evidence. Any earlier language describing C7 or C8 as active is
superseded.

## Phase question

> Can the 60k-mesh phase-2 virtual liquid outlet realize the commanded liquid
> inlet throughput while preserving credible phase routing, source-inclusive
> mass closure, bounded inventory behaviour, and useful steady convergence?

## Active mechanism

\[
Q_{\rm cmd}=|\dot m_{l,in}|,
\qquad
S_l(\mathbf{x})=-Q_{\rm cmd}
\frac{\alpha_l(\mathbf{x})}
{\max(\int_{V_a}\alpha_l\,dV,10^{-6}\ {\rm m^3})}.
\]

The source acts directly on phase 2 only. Matching liquid momentum and shared
`k`/`epsilon` removal are attached. Phase 1 has no direct mass source. The
lower-zone liquid volume is an availability/starvation diagnostic, not the
controller input and not the success metric.

## Scope and evidence boundary

- **In scope:** steady v2 liquid development, commanded-versus-applied removal,
  source-inclusive phase and mixture balances, lower-zone starvation, whole-
  separator liquid inventory, phase routing, residual behaviour, and numerical
  recovery inside the v2 envelope.
- **Fixed baseline:** the verified 60k mesh and prepared pair, bottom wall,
  phase-2-only direct mass removal, fresh Hybrid Initialization without a
  patched pool, and the recorded Mixture/RNG physics and numerics.
- **Required primary evidence:** command, native applied phase-2 source, liquid
  inlet throughput, lower-zone available liquid, total liquid inventory,
  phase-resolved boundary fluxes, zero phase-1 source, source-inclusive closure,
  and residual histories on native iteration coordinates.
- **Out of scope:** claiming that the source predicts physical brine-pipe
  hydraulics, validating a real pool level, or inferring plant performance.
- **Claim limit:** the baseline build result proves save/reopen and smoke
  integrity. The inlet-loading result adds finite-horizon throughput and
  inventory evidence, but does not establish steady convergence, bounded
  inventory, physical absorber validity, or plant drainage performance.

## Completed discovery

The [v2 inlet-loading ramp](v2-inlet-loading-ramp/setup.md) started both inlets
at `0.25` of the prior recorded base targets and ramped them to
`116.92 kg/s` liquid and `80.69 kg/s` steam over `2,000` iterations. The
native applied phase-2 source matches the named removal and follows the
inlet-derived command in the late trajectory. The lower zone remains a small
liquid reservoir while total liquid mass reaches `183.595 kg`; residuals do not
qualify as converged and the pressure outlet retains roughly 250 reversed-flow
faces late in the run. See the [result record](v2-inlet-loading-ramp/results.md)
and [summary figure](../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/v2-inlet-loading-summary.png).

## Next experiment

Use the finite-horizon evidence to select the next controlled v2 branch. Any
continuation should preserve the native command/applied-source distinction,
track source-inclusive phase balances, and predeclare a late-window inventory
and reverse-flow decision rule; do not promote this ramp to a steady or
physical-performance claim.
