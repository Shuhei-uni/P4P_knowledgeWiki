# Phase 7.1A — 60k Virtual Liquid Outlet (parent evidence)

## Status

**Parent-phase record.** The human created [Phase 7.2A](../phase-07-2a-wall-liquid-routing/index.md)
on 2026-09-22 and promoted the completed R0 Coupled / Global-Time-Step
continuation as its starting baseline. This Phase 7.1A record remains the owner
of the v2 build and control evidence; active wall-mechanism work is now
recorded in Phase 7.2A.

The original human-selected direction on 2026-09-22 restarted Phase 7.1A from
a new baseline on the supplied 60k-cell mesh. The v1 lower-inventory controller
is no longer the active mechanism. V2 treats the lower phase-2 source as a
virtual liquid outlet whose commanded throughput follows the liquid inlet and
whose local removal is weighted by the liquid actually present.

The [v2 setup](baseline-v2-virtual-liquid-outlet/deffered.md) has been built,
save/reopen verified, one-iteration smoke tested, and reloaded on `student`.
See the [build result](baseline-v2-virtual-liquid-outlet/results.md) for the
artifact hashes and exact readback. The first v2 liquid-development run is now
complete as the [inlet-loading ramp result](v2-inlet-loading-ramp/results.md):
the absorber realizes its command after lower-zone liquid develops, but the
finite trajectory remains nonstationary with growing total liquid inventory
and persistent outlet reverse flow.

At the time of the solver-control handoff, the immediate work was the
human-selected [Family N numerical improvement screen](solver-improvement-family/index.md).
It kept the v2 prepared pair and
the common loading rule as the base, then tests the smallest solver delta first:
steady Coupled pressure–velocity treatment with Coupled-compatible Global Time
Step pseudo-time, automatic initially. The roughness and EWF design records
were subsequently superseded as active execution authority by Phase 7.2A;
they now derive from the completed terminal R0 control endpoint rather than
the prepared v2 pair.

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

The [v2 inlet-loading ramp](v2-inlet-loading-ramp/deffered.md) started both inlets
at `0.25` of the prior recorded base targets and ramped them to
`116.92 kg/s` liquid and `80.69 kg/s` steam over `2,000` iterations. The
native applied phase-2 source matches the named removal and follows the
inlet-derived command in the late trajectory. The lower zone remains a small
liquid reservoir while total liquid mass reaches `183.595 kg`; residuals do not
qualify as converged and the pressure outlet retains roughly 250 reversed-flow
faces late in the run. See the [result record](v2-inlet-loading-ramp/results.md)
and [summary figure](../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/v2-inlet-loading-summary.png).

## Historical solver-improvement direction

Family N was the immediate discovery queue at the time of the solver-control
handoff. N1 is a combined solver package,
not a pseudo-time-only test. The live Fluent controls must be read back before
mutation, and pseudo-time must remain numerical rather than physical. N2/N3 are
not pre-filled with guessed tuning values: their deltas will be selected only
from N1 evidence.

The existing mechanism-family split remains recorded below as a separate
follow-on route.

## Superseded mechanism-family design

The former follow-on planning direction was the human-selected split between [Family R
— wall roughness](roughness-family/index.md) on Server 1 and [Family E —
Eulerian Wall Film](ewf-family/index.md) on Server 3. Both derive from the
verified v2 prepared pair and used the same explicit first-2,000-iteration
`0.25 -> 1.00` inlet ramp. That design is retained as provenance. The active
wall-mechanism contract is now in [Phase 7.2A](../phase-07-2a-wall-liquid-routing/index.md),
whose children start from the terminal R0 control and do not replay that ramp.

The two streams are independent and may run in parallel after each server
passes its own parent hash/reopen/readback gate. No old 237k thin-outer-ring,
C7, C8, turbulence, or v1 absorber artifact is an eligible parent for these
families.

## Historical next experiment

The historical selected next action was to prepare N1 from the exact v2 parent and pass its
hash/reopen/readback and smoke gates. The run must preserve the native
command/applied-source distinction, source-inclusive phase balances, solver
warnings, reverse flow, and the first 2,000 iterations on the declared ramp.
Do not promote this loading history to a steady or physical-performance claim.
The current active experiment is Phase 7.2A.
