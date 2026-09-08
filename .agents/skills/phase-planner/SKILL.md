---
name: phase-planner
description: "Catch up on project evidence, hear the human's phase or experiment thinking, and agree a human-controlled next direction. Human-only; invoke with /phase-planner in Cursor or $phase-planner in Codex."
disable-model-invocation: true
---

# Phase Planner

Treat this like a research catch-up with the human, not a formal planning report.

Read the repo first. Work out what we were trying to learn, what the simulations actually showed, what did not work, and what is still unclear. Use `show-me-your-work` when there is a lot of previous work to reconstruct.

## Catch me up

Answer the useful questions:

- What were we trying to figure out?
- What do the runs actually tell us?
- What surprised us or went against what we expected?
- What do we still not know?
- What limits how strongly we can say anything?

Do not dump every setup or result. Pull out the evidence that changes the current picture.

Simulation data is the main source of truth for what happened in our model. Literature, Fluent guidance, past experience, and reasoning can help explain results or suggest what to try next, but do not turn them into simulation results we have not actually observed.

If the evidence is weak, say so. `We do not know yet` is a valid answer.

## Shape the direction with the human

When the human wants to move from catch-up into choosing, reframing, or
designing work for a phase, invoke `phase-grill` before proposing a phase,
mechanism, or experiment matrix. It first captures the human's own thinking,
then distinguishes unfinished phase framing from experiment framing.

Maintain the current phase-root `CONTEXT.md` through that conversation. It is
the human-approved planning authority for candidates, decision gates, and
conditional qualification paths; it is not a chat log or a replacement for a
selected experiment's `setup.md`.

## What should we do next?

Stay at phase level. Do not jump straight into exact URFs, pressures, timesteps, setup files, or an experiment matrix unless the human asks.

First decide whether the current phase still has useful work left. Do not invent
a new phase just because the last batch of simulations finished. If direction
setting is needed, let `phase-grill` hear the human's thinking before narrowing
the options.

If there are genuinely different ways forward, give a small number of real options. Usually one to three is enough.

For each direction, explain simply:

- what question it would answer;
- why that question matters now;
- what evidence would make the work worthwhile;
- the main cost, risk, or assumption.

Say which direction you would pick and why when the evidence supports a recommendation. The human can change it, merge ideas, reject it, or keep discussing.

Use `arena` or `interrogate` only when the direction is genuinely hard to choose or worth challenging from independent viewpoints.

## Talk like a technical teammate

Use technical terms when they are the clearest words: Mixture, VOF, residuals, mass balance, `k`, `epsilon`, FPE, timestep, under-relaxation factor, and so on.

But prefer plain language around them.

Say `what do we still not know?` instead of `what unresolved uncertainty remains?`.

Say `this run does not support that claim yet` instead of wrapping the point in formal scientific-planning language.

Keep the technical detail. Cut the fluff.

Do not use consultant-speak, fake certainty, or long formal summaries when a short direct explanation works.

## Decide with the human

Do not automatically launch simulations or invoke `scientific-phase-loop`.

Talk through the direction first. Before handing off, agree on the parts that actually matter:

- the phase question or goal;
- what is in scope and what is not;
- important modelling assumptions or boundaries;
- compute or resource limits when they matter;
- what would count as enough evidence for this phase;
- when the loop should come back to the human.

### Define the autonomy envelope explicitly

Experiment origination and selection remain human-controlled. The normal handoff
grants `scientific-phase-loop` authority to execute, verify, and analyse only
the candidates, decision gates, and conditional qualification paths that the
human has approved in the phase `CONTEXT.md`.

When Fluent compute is part of the phase, the normal `/goal` handoff should also grant exclusive active-session authority over the configured Fluent fleet for the duration of the phase goal. Within that authority the loop may stop active calculations, preserve a recovery pair when a valuable unpreserved state could otherwise be lost, reload or restart Fluent, replace the loaded case, reassign servers, terminate abandoned workers, and use available servers only for approved context work.

This authority applies to active working sessions and approved experiment
children. It does **not** authorize creating or promoting a new experiment
idea, silently deleting verified durable Project/OneDrive parent artifacts,
inventing plant facts or validation targets, changing the fixed phase-level
question, or crossing an explicit human boundary.

If the human wants a narrower authority envelope for a particular phase, record the restriction in the handoff.

## Handoff

Once the direction is agreed, give `scientific-phase-loop` a short handoff:

- **Goal** — what this phase is trying to answer.
- **Why now** — why this is the useful question given the evidence so far.
- **What we already know** — only the evidence that matters for this phase.
- **Main unknowns / assumptions** — what is still open or being accepted for now.
- **Boundaries** — what the loop should not casually change.
- **Enough evidence looks like** — what would support a useful phase conclusion.
- **Context authority** — path/revision of `CONTEXT.md`, approved candidate IDs,
  declared decision gates, and conditional qualification paths.
- **Autonomy** — context-gated experiment execution plus the granted Fluent
  fleet/session authority, including any restrictions.
- **Return to the human when** — the decisions or missing facts the loop must not invent or authorize itself.

The handoff sets the destination, authority, approved route, and boundaries.

`scientific-phase-loop` still owns faithful execution, evidence verification,
analysis, and lifecycle discipline. It may follow only the human-approved route
recorded in `CONTEXT.md`; a new candidate, ambiguous gate, or unplanned result
returns to this human planning boundary.
