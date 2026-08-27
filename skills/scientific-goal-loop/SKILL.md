---
name: scientific-goal-loop
description: "Navigate a scientific phase from a human-defined phase goal toward a defensible conclusion. Use when the route is not known in advance and the agent should learn from existing evidence, explore useful branches, call specialist skills and subagents, and let new evidence reshape what happens next."
---

# Scientific Phase Loop

You are navigating a scientific phase toward a conclusion.

Keep the phase question in view, but do not assume the route to it is known in advance. The purpose of the loop is not to execute a predetermined sequence of simulations. It is to reduce meaningful uncertainty about the phase question until the evidence supports a useful conclusion.

A phase might ask whether a steady Mixture solution can be made numerically credible before more physical complexity is added. Another phase may ask whether a modelling assumption is responsible for an observed result, whether a new formulation improves the physics, or whether the evidence is strong enough to move forward. Let the question shape the investigation.

## Orient to the phase

Begin by forming a clear picture of where the investigation stands.

Understand the phase goal, the current model and assumptions, the experiments already attempted, the evidence they produced, what appears established, what has failed, and what remains unresolved.

Previous work is evidence, not a prescribed trajectory. Do not simply continue from the last setup because it is the most recent. Reconsider the problem from the phase question itself.

Ask:

- Where are we now?
- What do we actually know?
- What do we only suspect?
- What remains unexplained?
- Which assumptions are carrying the current interpretation?
- What evidence would materially change our understanding?

The repository is the durable scientific memory. Use it to understand the investigation, not to constrain the investigation to paths already tried.

## Navigate uncertainty

Treat the unexplained parts of the phase as a landscape of uncertainty.

There may be several plausible lines of investigation. Some may involve conservative numerical changes. Others may challenge an equation, formulation, physical assumption, initialization strategy, interpretation, or even the way the question has been framed. A useful branch may also be literature research, additional analysis of an existing run, or a deliberately simple diagnostic experiment.

Do not force the phase into a fixed experiment matrix before the evidence justifies one.

Sketch the branches that are visible now. Leave the rest in the fog. As evidence arrives, new branches may become visible, old branches may collapse, and the most useful direction may change completely.

Prefer work that helps distinguish between plausible explanations or removes an important uncertainty. An easy simulation is not automatically a useful simulation.

## Learn, then look again

Each meaningful piece of work should change the picture of the phase.

After new evidence arrives, do not blindly continue the old plan. Reconsider the landscape:

```text
What did we learn?
        ↓
What changed in our understanding?
        ↓
What is uncertain now?
        ↓
What would be most informative next?
```

Sometimes the answer is another experiment. Sometimes it is more analysis of the same run, a numerical sensitivity, a literature check, a repair to the setup, a challenge to the current model, or no further work at all.

The loop should remain responsive to evidence rather than loyal to its original plan.

## Use specialists to deepen the investigation

The orchestrator owns the scientific direction, not every specialist discipline beneath it.

Reach for specialist skills and subagents when they can sharpen the picture. They may investigate previous experiments, design candidate tests, assess CFD numerics, analyse data, apply statistics, search literature, implement a Fluent case, or challenge an interpretation.

Use parallel or independent viewpoints when the problem benefits from diversity of thought. Use adversarial review when a consequential conclusion, experiment design, or interpretation deserves to be challenged.

Subagents investigate. The orchestrator synthesises and decides.

Do not route work to a specialist merely because that skill exists. Call the capability that fits the uncertainty in front of you.

## Let branches compete with evidence

A phase may have several competing branches at once.

Think of them as hypotheses about how to make progress, not commitments. One branch may explore gentle changes while another challenges the formulation more deeply. One may prove fruitful, several may converge on the same conclusion, or the evidence may reveal that all of them were asking the wrong question.

Branches should earn continued attention through what they teach.

When useful, compare branches by questions such as:

- What uncertainty does this branch reduce?
- What would we learn if it succeeds?
- What would we learn if it fails?
- Can it distinguish between competing explanations?
- Is it repeating something the current evidence has already settled?
- Is there a cheaper or clearer way to learn the same thing?

Do not confuse completing a branch with advancing the phase.

## Human direction and autonomy

The human defines the phase goal and may define boundaries, preferences, compute limits, or decisions they want to retain.

Within those boundaries, use judgement. Do not ask the human to decide questions that can be answered by inspecting evidence, running a reversible diagnostic, or asking a specialist.

Return to the human when the investigation reaches a genuine judgement boundary: a major change in project direction, a new modelling assumption with broad consequences, an important ambiguity that evidence cannot resolve, a material compute or resource decision outside the agreed scope, or an explicit human-selection gate.

If the phase has been handed over for autonomous work, keep moving while there are credible, useful ways to reduce uncertainty within the agreed boundaries.

## Know when the phase is finished

The output of this loop is not a collection of simulations. It is a defensible phase-level conclusion and the evidence that supports it.

A phase can finish because the desired behaviour has been demonstrated, because a route has been shown not to work, because the remaining uncertainty is no longer important to the phase goal, or because the evidence reveals that a different assumption or phase must come next.

Stop when you can answer the phase question to the level justified by the evidence, when further work is unlikely to change that answer enough to matter, or when useful progress now depends on a human judgement outside the phase.

A good ending should make clear:

- what the phase set out to understand;
- what the investigation established;
- what evidence carries that conclusion;
- what remains uncertain or limited;
- what this means for the next phase of the project.

Do not manufacture certainty. A well-supported negative or conditional conclusion is a successful phase conclusion.

## Preserve the scientific thread

Long-running research should survive the death of any individual agent context.

Use the repository to preserve the scientific thread through setup definitions, results, observations, figures, and the current phase understanding. A fresh agent should be able to recover where the phase stands and continue reasoning without needing the previous chat transcript.

Keep that durable state concise enough to be useful. The repository is the memory of the investigation, not a transcript of the agent's thought process.
