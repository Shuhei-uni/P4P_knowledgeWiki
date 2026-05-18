# Objective And Scope

## Project Objective
- Improve an existing CFD model of a vertical BOC separator.
- Replace idealised inlet representation with more realistic two-phase inlet regimes.
- Quantify effects on internal flow behaviour, separation efficiency, and pressure drop.

Source: `raw/Shuhei Report.docx` (`shuhei-report-2026`).

## Current Phase
- Literature overview is complete at rough level.
- Active phase is baseline reconstruction of past CFD models.
- Immediate target is convergence of the recreated two-phase case before inlet-regime refinement.

## Scope In
- Separator vessel modelling (especially vertical BOC and Bangma-legacy geometry recreation context).
- Inlet-region modelling choices and flow-regime representation.
- CFD setup, convergence, sensitivity, and validation planning.

## Scope Out
- Full downstream steam network modelling.
- Plant-wide operations beyond separator-relevant conditions.
- Non-separator hardware redesign not tied to research objectives.

## Scope Governance Rule
Deep technical settings belong in `wiki/technical/` and `wiki/model/` only.
This page must stay as project intent and boundary control.
