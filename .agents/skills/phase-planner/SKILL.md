---
name: phase-planner
description: "Run a human-invoked scientific catch-up and phase-planning session. Use before starting a phase, after an autonomous phase loop stops, or when the human wants to reconstruct where the project stands and decide the next phase-level direction without designing individual simulations yet."
---

# Phase Planner

Before deciding what the project should do next, reconstruct what the evidence actually says about where the science stands.

This is a human-invoked planning skill. It does not run the autonomous scientific loop and it does not design the experiment sequence for that loop.

## Reconstruct the current position

Start from durable repository evidence, not from the most recent chat message or setup number.

Recover:

- the phase question or goal that was being pursued;
- the experiments and analyses that materially changed understanding;
- the strongest simulation evidence;
- important failures, contradictions, or superseded interpretations;
- what is currently supported;
- what remains uncertain, weakly supported, contradicted, or untested;
- numerical or modelling limitations that bound the current conclusions.

Use `show-me-your-work` when substantial autonomous work needs to be reconstructed. Treat that reconstruction as evidence for planning, not as the plan itself.

## Think at phase level

Do not jump straight to individual Fluent settings or setup files.

Ask:

- What question can we answer now that we could not answer before?
- What important uncertainty still prevents a strong phase-level statement?
- Is the current phase still the right question to pursue?
- Has the evidence exposed a more important modelling assumption or scientific direction?
- Would more work in the current phase materially improve the project, or are we ready to move on?

A phase may continue, narrow, broaden, be reframed, or end.

## Develop a small number of directions

If further work is justified, identify a small number of scientifically meaningful phase-level directions.

Judge them by what they would accomplish for the project, not by how easy they are to turn into simulations.

For each direction explain:

- the phase-level question it would pursue;
- why that question matters now;
- which current uncertainty it addresses;
- what kind of evidence would make the direction successful;
- major trade-offs, assumptions, or human decisions involved.

Use `arena` or `interrogate` when the phase direction is consequential or genuinely contested. Do not create alternatives merely to fill a list.

Recommend the strongest direction when the evidence supports one, while keeping the judgement open for human discussion.

## Discuss before handing off

The purpose of this skill is a scientific planning conversation with the human.

Do not automatically launch simulations, invoke `scientific-phase-loop`, or turn the recommended direction into a fixed experiment campaign.

Resolve with the human, as needed:

- the next phase goal or question;
- important modelling or scientific boundaries;
- compute or resource limits;
- decisions the human wants to retain;
- what would count as a useful phase-level conclusion;
- when the autonomous loop should return control.

## Handoff to the autonomous loop

Once the phase direction is agreed, produce a concise phase handoff for `scientific-phase-loop` containing:

- phase goal/question;
- current evidence that matters;
- important unresolved uncertainty;
- human constraints and boundaries;
- definition of a useful phase conclusion;
- explicit human-return conditions.

The handoff defines the destination and boundaries, not the route.

`scientific-phase-loop` remains responsible for reasoning within the phase: forming and revising hypotheses, designing high-information experiments, running simulations, analysing evidence, interpreting results, and choosing what to test next.

## Output

Keep the catch-up compact enough to discuss:

1. **Current phase question**
2. **Where we are now**
3. **Strongest evidence and important contradictions**
4. **What remains unresolved**
5. **Whether the current phase should continue, change, or end**
6. **Candidate phase-level directions, if needed**
7. **Recommended direction and trade-offs**
8. **Questions or boundaries to agree with the human**
9. **Phase handoff**, only after direction is agreed

Do not turn this into a project-management roadmap. The aim is to decide what scientific question deserves the next autonomous effort.