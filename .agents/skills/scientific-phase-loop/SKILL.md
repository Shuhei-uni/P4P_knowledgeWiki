---
name: scientific-phase-loop
description: "Navigate a scientific phase from a human-defined phase goal toward a defensible conclusion. Use when the phase direction and boundaries are agreed but the route is not known in advance, and the agent should autonomously learn from evidence, design and run high-information simulations, interpret results, revise hypotheses, and keep testing until the phase is answered or a genuine human boundary is reached."
---

# Scientific Phase Loop

You are navigating a scientific phase toward a conclusion.

Keep the phase question in view, but do not assume the route to it is known in advance. The purpose of the loop is not to execute a predetermined sequence of simulations. It is to reduce meaningful uncertainty about the phase question until the evidence supports a useful conclusion.

## Enter with a phase handoff

Start from the agreed phase goal or question and any boundaries supplied by the human or `phase-planner`.

The handoff may include:

- the phase goal or question;
- current evidence that matters;
- important unresolved uncertainty;
- human constraints or compute/resource boundaries;
- what would count as a useful phase-level conclusion;
- conditions that should return control to the human.

Treat this as the destination and boundaries, not the route. Do not turn the phase handoff into a fixed experiment checklist.

Within those boundaries, you own the scientific reasoning needed to move the phase forward.

## Simulation evidence is the anchor

Reasoning, literature, prior experience, and specialist opinions are useful for forming hypotheses and deciding what to test. Unless genuinely equivalent evidence already exists, they do not tell you what this simulation will do.

Treat untested expectations as hypotheses.

When the uncertainty concerns the behaviour of the current CFD model, the strongest way to resolve it is normally to run the relevant simulation properly and inspect the resulting data.

The governing posture is:

```text
reasoning proposes
simulation tests
data constrains the conclusion
```

Simulation output is not automatically truth. Its scientific weight depends on whether the case was implemented as intended, run for an adequate duration or convergence window, and shown to be numerically credible for the claim being made. Use the appropriate specialist skills to establish that before making strong conclusions.

## Orient to the phase

Begin by forming a clear picture of where the investigation stands.

Understand the phase goal, the current model and assumptions, the experiments already attempted, the evidence they produced, what appears established, what has failed, and what remains unresolved.

Previous work is evidence, not a prescribed trajectory. Do not simply continue from the last setup because it is the most recent. Reconsider the problem from the phase question itself.

Ask:

- Where are we now?
- What is genuinely supported by simulation evidence?
- What is still only a hypothesis or interpretation?
- What uncertainty matters most to the phase goal?
- What observation would materially change our understanding?

The repository is the durable scientific memory. Use it to understand the investigation, not to constrain the investigation to paths already tried.

## Navigate uncertainty

Treat the unresolved parts of the phase as a landscape of uncertainty.

There may be several plausible lines of investigation. Some may involve conservative numerical changes. Others may challenge an equation, formulation, physical assumption, initialization strategy, interpretation, or even the way the question has been framed. A useful branch may also be additional analysis of an existing run, literature research, or a deliberately simple diagnostic case.

Do not force the phase into a fixed experiment matrix before the evidence justifies one.

Sketch the branches that are visible now. Leave the rest in the fog. As evidence arrives, new branches may become visible, old branches may collapse, and the most useful direction may change completely.

## Make simulations earn their cost

Simulation time is expensive. Do not brute-force the phase merely because automation makes it possible.

Prefer a small number of high-information runs over a large number of weakly motivated cases. A simulation earns its cost when its possible outcomes would materially change the current understanding, distinguish between plausible explanations, establish a useful bound, or reveal behaviour needed to decide the next move.

Before committing compute, ask what the run can teach that the current evidence cannot.

Whenever possible, design a run so that both success and failure are informative. Capture enough behaviour, history, and comparison data that the run can answer more than a narrow endpoint question without contaminating the experiment with unnecessary changes.

Do not confuse a large sweep with a strong investigation. Coverage matters only when the cases are chosen to resolve uncertainty.

## Learn, then look again

Each meaningful piece of work should change the picture of the phase.

After new evidence arrives, do not blindly continue the old plan. Reconsider the landscape:

```text
What did the simulation or analysis actually show?
        ↓
What changed in our understanding?
        ↓
What remains uncertain?
        ↓
What would be most informative next?
```

Sometimes the answer is another experiment. Sometimes it is more analysis of the same run, a numerical sensitivity, a literature check, a repair to the setup, a challenge to the current model, or no further work at all.

The loop should remain responsive to evidence rather than loyal to its original plan.

When another experiment is justified, form or revise the hypothesis, design the smallest high-information experiment or campaign that can test it, run it, analyse the resulting evidence, interpret it, and update the phase understanding before choosing again.

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

## Know when to return control

The output of this loop is not a collection of simulations. It is a defensible phase-level conclusion and the evidence that supports it.

Return control when one of three things is true:

1. the phase question is sufficiently answered to the level justified by the evidence;
2. useful progress now requires a genuine human phase-level judgement outside the agreed boundaries;
3. the human explicitly or manually stops the loop.

A phase can finish because the desired behaviour has been demonstrated, because a route has been shown not to work, because the remaining uncertainty is no longer important to the phase goal, or because the evidence reveals that a different assumption or phase must come next.

Do not plan the next phase on your own at this boundary. Produce a concise phase-state handoff that `phase-planner` and the human can use to decide what comes next.

A good ending should make clear:

- what the phase set out to understand;
- what the simulations and analyses actually established;
- what remains hypothesis rather than evidence;
- what numerical or modelling limitations bound the conclusion;
- why the loop stopped or returned control.

Do not manufacture certainty. A well-supported negative or conditional conclusion is a successful phase conclusion.

## Preserve the scientific thread

Long-running research should survive the death of any individual agent context.

Use the repository to preserve the scientific thread through setup definitions, results, observations, figures, and the current phase understanding. A fresh agent should be able to recover where the phase stands and continue reasoning without needing the previous chat transcript.

Keep that durable state concise enough to be useful. The repository is the memory of the investigation, not a transcript of the agent's thought process.
