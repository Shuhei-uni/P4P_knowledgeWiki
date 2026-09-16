# Phase 7.1A — Absorber Convergence and Solver Stability

## Status

**Human-selected planning direction on 2026-09-11.** Phase 7.1A continues
from the mechanism result retained in [Phase 07A](../phase-07a-simplified-purnanto-liquid-removal/index.md): the lower cell-zone, phase-2-only absorber is the preferred liquid-removal path for the simplified Purnanto model. The purpose of this phase is to find out whether the scaled residuals—especially continuity—can converge while that removal behaviour remains useful.

The human has additionally raised a Phase 7.1A-specific long-horizon
hypothesis from the current longer runs: steady-state assessment may not be
meaningful until at least roughly `4,000` solver iterations, and the separator
may plausibly operate near `2,000 kg` of total liquid inventory. These values
are observation-window and operating-point markers, not generic Fluent rules
or sufficient acceptance criteria. Any steady-state claim still requires
bounded late-window inventory and key monitors, credible phase-resolved and
mixture mass closure, acceptable residual behaviour, and explained routing.

This is a new planning phase, not Phase 08. It does not create an executable
setup queue yet. Specific solver changes must be framed as controlled,
human-approved candidates before `setup.md` is created.

## Phase question

> Can the selected bottom-only cell-zone absorber reach credible scaled-residual
> and continuity convergence in the simplified Purnanto model when the other
> numerical and physical treatments are changed one at a time?

## Why now

Phase 07A showed that the absorber is a workable and auditable liquid-removal
mechanism in the model, but the fixed-setting long continuation repeatedly
entered a coupled residual blow-up. The continuation had a nearly closed
integrated mixture balance, yet continuity, turbulence, and volume-fraction
residuals rose while pressure-outlet reverse flow and turbulent-viscosity
limiting became widespread. That separates the next question from the original
mechanism question: the issue is now convergence and numerical stability of
the chosen absorber branch.

## Scope and evidence boundary

- **In scope:** steady-state convergence of the simplified Purnanto absorber
  branch; pressure–velocity coupling; spatial discretization; relaxation or
  pseudo-time treatment; turbulence closure sensitivity; phase-fraction
  treatment; and, only when justified by a declared gate, mesh or absorber
  conditioning sensitivities.
- **Must remain fixed for the primary screen:** the simplified geometry, the
  lower cell-zone absorber concept, phase-2-only direct removal, the bottom
  wall, no conventional bottom outlet, and no patch/reset field treatment.
- **Controlled-change rule:** change one non-absorber treatment at a time so
  residual improvement can be attributed. Do not combine a turbulence-model
  change with a coupling, source, outlet, and mesh change in one child.
- **Out of scope:** physical qualification of the brine-pool interface,
  plant drainage-rate claims, a conventional bottom outlet as a replacement,
  or silently changing the absorber into a different mechanism.
- **Claim limit:** a successful result would establish a numerically
  converged computational absorber branch under the tested settings. It would
  not validate the physical brine pool, the real drainage hardware, or the
  separator's plant performance.

## Next planning step

Choose the first controlled change, its exact parent/reference, short
diagnostic horizon, and evidence gate. Phase 7.1A is not ready for Phase Loop
until that candidate is human-approved and formalized.
