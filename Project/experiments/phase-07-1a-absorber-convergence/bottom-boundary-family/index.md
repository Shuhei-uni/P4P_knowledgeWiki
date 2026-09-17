# Phase 7.1A bottom-boundary family

This family is the user-authorized Phase 7.1A contrastive branch for testing
the supplied `purnanto-separator(bottomrings)-237k.msh.h5` mesh. It is separate
from the absorber-only turbulence and solver-path queue because the bottom
boundary topology changes.

The common prepared baseline preserves the Phase 7.1A Mixture/RNG model,
two mass-flow inlets, steam pressure outlet, lower `y <= 0.10 m` phase-2-only
absorber, and steady numerical settings. It replaces the former 342k mesh with
the 237,137-cell thin-outer mesh. The new mesh has one thin outer bottom band
that is a pressure outlet; the remaining bottom bands stay no-slip walls.

## First prepared child

- [Thin-outer pressure outlet at 1.120 MPa gauge](thin-outer-po-p1120/setup.md)

## Scope and claim limit

This is a localized, phase-permissive pressure-boundary diagnostic. It does
not make the outlet liquid-selective. A future run must record ring-resolved
vapor/liquid fluxes, reverse flow, absorber source accounting, inventory, and
residual behaviour before any drainage or separator-performance claim.

The prepared case/data pair has passed the builder's save/reopen audit on
Server 1. No solve is authorized merely by creation of the prepared baseline. The first
child remains a setup/readback artifact until its run horizon and evidence
contract are explicitly selected.
