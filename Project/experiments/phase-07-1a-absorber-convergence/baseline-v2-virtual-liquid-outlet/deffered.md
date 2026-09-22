# Phase 7.1A baseline v2 — 60k virtual liquid outlet

> **Status — VERIFIED PREPARED PARENT (2026-09-22):** Retained as the v2
> baseline build/provenance record. The prepared pair is the active parent for
> the common ramp and the new Server-1/Server-3 mechanism families. It is not
> itself a performance result; see the sibling `results.md` for the verified
> build evidence.

## Question

Can Phase 7.1A be restarted from a clean 60k-cell baseline whose lower
liquid-removal mechanism behaves as a throughput-controlled virtual outlet,
rather than as the v1 lower-inventory controller?

This is a prepared-baseline build, not a scientific performance screen.

## Exact source and controlled delta

- Runtime: `student`, Fluent 2025 R2.
- Setup recipe: the non-iterating live Phase 7.1A v1 state captured immediately
  before this build; a paired recovery copy is written before replacement.
- Target mesh:
  `OneDrive-TheUniversityofAuckland/2026 Sem 2/700/Purnanto-new/Separator-purnanto-60k.msh.h5`
  (resolved on `student` to the full path recorded in `run-paths.yaml`).
- Mesh delta: replace the current prepared thin-outer mesh with the named 60k
  mesh and rebuild the v1 physics/numerics on its named boundaries.
- Absorber delta: retain the existing Phase-7 lower spatial selection
  (`y <= 0.10 m`) as a separate cell zone, but replace the uniform
  inventory-driven source with an inlet-throughput feed-forward source.

All other reproducible v1 model, material, boundary, steady-solver, turbulence,
solution-method, and control settings are invariants. The bottom remains a
wall; no physical liquid outlet is introduced. Initialization is fresh Hybrid
Initialization with 10 passes and no patched pool.

## Virtual-outlet law

At every profile update,

\[
Q_{\rm cmd}=|\dot m_{l,\,in}|,
\]

and the phase-2 mass source in the lower zone is

\[
S_l(\mathbf{x})=-Q_{\rm cmd}
\frac{\alpha_l(\mathbf{x})}
{\max\left(\int_{V_a}\alpha_l\,dV,10^{-6}\ {\rm m^3}\right)}.
\]

Thus vapor receives no direct mass source, liquid-free cells receive no direct
liquid sink, and the integrated removal follows the liquid-inlet throughput
when at least the normalization-floor volume is present. The `10^-6 m3` floor
is a divide-by-zero safeguard, not an inventory target or pool controller.

The lower-zone mixture momentum sources use `S_l u_l` with native phase-2
velocity components. Shared turbulence removal uses `S_l k` and
`S_l epsilon`. Profile update interval is one solver iteration.

## Build and evidence contract

1. Capture the live v1 setup recipe and save a recovery case/data pair.
2. Load the exact 60k mesh and reapply the v1 setup in dependency order.
3. Split and rename the lower virtual-outlet cell zone without changing total
   fluid-cell count.
4. Configure/read back every named expression and source hook.
5. Save the freshly hybrid-initialized prepared pair, reopen it, and repeat the
   critical audit. Record Fluent's inherited global iteration marker rather
   than treating it as initialization provenance.
6. Run exactly one smoke iteration, save a separate active-001 pair, then
   reload the canonical active-000 pair.

Required proof is the mesh identity/count, boundary roles, steady Mixture/RNG
state, source scopes, exact expression definitions, positive inlet-derived
command, save/reopen hashes, one-iteration smoke completion, and terminal
reload of the canonical prepared pair. No convergence, balance,
capture-efficiency, or physical
outlet claim is permitted from this build.

## Next experiment

The v2 baseline's first `2,000` iterations must use the common inlet-loading
ramp recorded in
`../v2-inlet-loading-ramp/deffered.md`: start both inlets at `0.25` of their
base targets, increase linearly to `116.92 kg/s` liquid and `80.69 kg/s`
steam over `2,000` native steady iterations, and update every `10` iterations.
This ramp is part of the baseline contract; a constant-flow startup is not an
equivalent baseline. The prepared pair remains the clean parent and is not
itself mutated by the schedule.

The first v2 discovery run must predeclare and record commanded removal,
native applied phase-2 source, liquid-inlet throughput, total liquid inventory,
lower-zone available liquid, phase-1 source audit, boundary phase fluxes,
source-inclusive closure, and residuals. The primary comparison is commanded
versus applied removal; lower-zone inventory is a starvation diagnostic.
