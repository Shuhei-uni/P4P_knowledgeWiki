---
name: explore-experiment-space
description: "Design a small, fast simulation matrix to explore several plausible directions when the important mechanism or experiment direction is still unclear. Use inside scientific-phase-loop discovery mode before spending heavily on a focused hypothesis test."
---

# Explore Experiment Space

When the important direction is unclear, breadth can be more valuable than depth.

Use this skill to create a bounded discovery campaign that quickly exposes which ideas, mechanisms, parameter regions, or modelling choices deserve deeper investigation.

Discovery runs are screening evidence. Their job is to reveal direction, not to manufacture strong conclusions from short simulations.

## Start from the unresolved landscape

Before creating cases, inspect the relevant literature, previous simulation results, current model behaviour, and competing explanations.

Ask:

- What important uncertainty is still broad rather than sharply testable?
- Which plausible directions remain difficult to rank from existing evidence?
- What small set of contrasting simulations could make that landscape clearer?
- What would make a direction look promising, weak, or unexpectedly interesting?

Do not create a matrix merely because many parameters exist. Every case should help distinguish a meaningful possibility.

## Build a small discovery matrix

Create at most six simulation cases.

Prefer a compact matrix containing a useful reference plus deliberately different directions. Cases may test alternative mechanisms, settings, formulations, operating conditions, or combinations when an interaction is itself worth screening.

Keep the matrix interpretable. Change as little as practical within each comparison and preserve common conditions where possible.

Use a table such as:

| Case | Main change | Why it is included | Planned iterations | Evidence to compare |
|---|---|---|---:|---|
| D1 | Reference | Comparison anchor | 500-1000 | ... |
| D2 | ... | Tests direction A | 500-1000 | ... |

A ballpark of roughly 500 to 1,000 iterations per case is appropriate when that is enough to expose useful early behaviour. This is a planning default, not a universal numerical criterion. Use a different short budget when the model, solver behaviour, or phase constraints justify it.

The point is to obtain comparable early behaviour across several directions without paying the cost of fully developing every case.

## Design comparable screening evidence

Plan the evidence before running the matrix.

Prefer iteration or time histories over endpoint snapshots. Capture the residuals, balances, physical monitors, fluxes, inventories, contours, or other quantities needed to compare how each case behaves.

Use the same definitions, plotting conventions, comparison windows, and run budget across cases whenever scientifically appropriate.

Short runs can be noisy or still evolving. Preserve that behaviour rather than hiding it behind a single final value.

## Interpret as discovery evidence

After the matrix is run, compare the cases primarily to decide where deeper investigation is worth the compute.

The useful outputs are statements such as:

- this direction is consistently more promising than the alternatives;
- this option appears weak enough to deprioritise;
- these two mechanisms remain difficult to distinguish;
- this case produced unexpected behaviour that creates a new hypothesis;
- the matrix did not separate the candidates, so a different experiment design is needed.

Do not normally use a 500-1,000-iteration discovery case by itself to claim settled model behaviour, convergence, or a strong quantitative conclusion.

Discovery evidence can eliminate poor directions, expose trends, generate hypotheses, and identify the most valuable focused test. It does not need to finish the scientific argument.

## Return to the loop

Return:

1. the discovery question;
2. the case matrix, with no more than six cases;
3. the evidence that should be comparable across the matrix;
4. the short-run budget and why it is sufficient for screening;
5. after execution, which directions appear promising, weak, unresolved, or surprising;
6. the hypothesis or focused question that now deserves deeper testing, if one emerged.

Hand promising focused questions back to `scientific-phase-loop` / `design-experiment` for hypothesis-test mode.

If the matrix does not reduce the uncertainty enough to justify a focused test, redesign the discovery question rather than automatically extending every case into a long simulation.
