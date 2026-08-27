# Scope

## Current objective

Improve an existing CFD model of a vertical BOC separator, replace an idealised two-phase inlet representation with more realistic inlet-regime options, and quantify effects on internal flow behaviour, separation efficiency, and pressure drop.

Source: `ResearchProject_wiki/raw/Shuhei Report.docx` (`shuhei-report-2026`, `Reported`).

## Current research boundary

The near-term project question is narrower than the full objective: first establish one physically stable and sufficiently iterated reference case, then introduce one controlled inlet-regime change at a time. Current work is evidence triage and controlled reconstruction of the spiral-inlet two-phase case (`Inferred`, [current roadmap](../ResearchProject_wiki/wiki/project/roadmap.md)).

Early or incomplete Fluent runs are retained for setup history and failure diagnosis. They are not report-quality evidence for separator efficiency, liquid carryover, pressure drop, or inlet-regime improvement unless the relevant numerical, physical, and comparison gates are satisfied (`Inferred`, [current evidence boundary](../ResearchProject_wiki/wiki/project/objective-and-scope.md)).

## In scope

- vertical separator vessel modelling, including the spiral-inlet and Bangma-legacy geometry-recreation context;
- inlet-region and flow-regime representation;
- CFD setup verification, convergence, sensitivity, and validation planning;
- selected experiments that rebuild the evidence base from controlled, sufficiently iterated simulations;
- project-specific interpretation of evidence and allowed claims.

## Out of scope

- full downstream steam-network modelling;
- plant-wide operations beyond separator-relevant conditions;
- non-separator hardware redesign that is not tied to the research objective;
- reusable CFD methods, raw Fluent transcripts/settings dumps, and executable automation, which belong to [CFD_wiki](../CFD_wiki/) and [PyAnsys](../PyAnsys/) respectively.

## Ownership rule

`Project/` is the compact authority for current project-specific scientific truth: the question being pursued, stable assumptions, selected experiments, evidence interpretation, and claim boundaries. It does not replace the source corpus or absorb detailed setup lineage. Link to those systems and carry only the minimum context needed for a fresh agent to make the next safe decision.
