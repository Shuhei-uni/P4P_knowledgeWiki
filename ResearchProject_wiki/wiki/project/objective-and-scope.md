# Objective And Scope

## Project Objective
- Improve an existing CFD model of a vertical BOC separator.
- Replace idealised inlet representation with more realistic two-phase inlet regimes.
- Quantify effects on internal flow behaviour, separation efficiency, and pressure drop.

Source: `raw/Shuhei Report.docx` (`shuhei-report-2026`).

## Current Phase
- Literature overview is complete at rough level.
- Active phase is evidence triage and controlled reconstruction of the spiral-inlet two-phase case.
- Immediate target is to obtain one physically stable, sufficiently iterated reference case before inlet-regime refinement or report-facing design comparison.

## Current Evidence Boundary
- `Inferred`: most early Fluent outputs are not report-quality performance evidence because they were stopped before enough iterations for the flow field and phase balances to become interpretable.
- Only two documented simulations currently exceed `1000` iterations and should remain in the active evidence set:
  - `FFF-2` / mixed wet-half velocity-inlet parent run at approximately `1020` steady iterations.
  - `MWH-WP-2026-05-07-A` / mixed wet-half velocity-inlet with initialized water pool at approximately `3500` steady iterations.
- These two runs are still diagnostic rather than validation evidence: neither provides a converged, physically balanced final separator-performance result.
- Low-iteration cases should be retained as setup/debug history only, not used for quantitative claims about separator efficiency, liquid carryover, pressure drop, or inlet-regime improvement.

## Scope In
- Separator vessel modelling (especially vertical BOC and Bangma-legacy geometry recreation context).
- Inlet-region modelling choices and flow-regime representation.
- CFD setup, convergence, sensitivity, and validation planning.
- Future run planning that rebuilds the evidence base from controlled, sufficiently iterated simulations.

## Scope Out
- Full downstream steam network modelling.
- Plant-wide operations beyond separator-relevant conditions.
- Non-separator hardware redesign not tied to research objectives.

## Scope Governance Rule
Deep technical settings belong in `wiki/technical/` and `wiki/model/` only.
This page must stay as project intent and boundary control.
