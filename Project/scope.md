# Scope

## Current objective

Improve an existing CFD model of a vertical BOC separator, replace an
idealised two-phase inlet representation with more realistic inlet-regime
options, and quantify effects on internal flow behaviour, separation
efficiency, and pressure drop.

Source: ResearchProject_wiki/raw/Shuhei Report.docx
(shuhei-report-2026, Reported).

## Current research boundary

The near-term question is narrower than the full objective: first establish one
physically stable and sufficiently iterated reference case, then introduce one
controlled inlet-regime change at a time. Current work is evidence triage and
controlled reconstruction of the spiral-inlet two-phase case
(Inferred, [current Project state](index.md)).

Early or incomplete Fluent runs remain setup history and failure diagnosis.
They are not report-quality evidence for separator efficiency, liquid
carryover, pressure drop, or inlet-regime improvement unless the numerical,
physical, and comparison gates in [V&V limits](vnv.md) are satisfied
(Inferred).

Lower-water initialization and bottom-pool studies remain parked. A physical
brine outlet may be part of a declared full-geometry model-form experiment,
but brine-outlet pressure tuning is not a project-wide default lane.
Whole-vessel liquid closure is not a universal acceptance metric for the
simplified Purnanto geometry; every experiment must state its own geometry and
balance boundary (Inferred).

## In scope

- vertical separator vessel modelling, including the spiral-inlet and
  Bangma-legacy geometry-recreation context;
- inlet-region and flow-regime representation;
- CFD setup verification, convergence, sensitivity, and validation planning;
- selected experiments that rebuild the evidence base from controlled,
  sufficiently iterated simulations;
- project-specific interpretation of evidence and allowed claims.

## Out of scope

- full downstream steam-network modelling;
- plant-wide operations beyond separator-relevant conditions;
- non-separator hardware redesign that is not tied to the research objective;
- reusable CFD methods, raw Fluent transcripts/settings dumps, and executable
  automation, which belong to [CFD_wiki](../CFD_wiki) and
  [PyAnsys](../PyAnsys) respectively.

## Ownership rule

Project/ is the compact authority for current project-specific scientific
truth: the question being pursued, stable assumptions, selected experiments,
evidence interpretation, and claim boundaries. Reusable methods belong in
CFD_wiki/, and executable implementation or machine evidence belongs in
PyAnsys/. The two tracked files under ResearchProject_wiki/raw/ are source
inputs only.

## Evidence labels

- Reported: stated by a cited source or retained project record;
- Observed: measured or read back from a case, run, or artifact;
- Inferred: project interpretation grounded in the available evidence;
- Assumed: an explicit project choice that still needs sensitivity or
  confirmation;
- Missing Info: required evidence that is not currently available.
