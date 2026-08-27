---
name: interpret-experiment
description: "Turn simulation evidence into a bounded scientific interpretation. Use after the required analysis exists and numerical adequacy has been assessed, to separate hypothesis from observation, interpretation, and conclusion, and to state only what the simulation evidence actually supports."
---

# Interpret Experiment

Interpret what the simulation showed, not what you expected it to show.

Reasoning proposes. Simulation tests. Data constrains the conclusion.

Literature, prior experience, and physical intuition may help explain a result. They do not substitute for the result itself.

## Start from the evidence

Read the experiment question, the controlled changes, the analysis plan, the measured and derived data, the plots, the comparison cases, and the numerical-quality assessment.

If decisive evidence is missing, say what cannot be concluded. If the simulation is numerically inadequate, interpret the numerical behavior that was actually observed without turning it into a physics claim.

A simulation run is not automatically scientific evidence for the intended mechanism. Its value depends on whether the setup represented the intended experiment, whether the required behavior was observed, and whether the numerical solution is credible enough for the claim being made.

## Keep four levels separate

### Hypothesis

What was expected before the evidence was seen.

A hypothesis can come from theory, Fluent guidance, literature, previous simulations, engineering intuition, or a competing explanation. It is not a result.

### Observation

What the simulation data directly shows.

Observations should be traceable to a number, history, field, plot, comparison, solver event, or other recorded evidence.

### Interpretation

What those observations may mean.

Interpretation can connect multiple observations and use scientific reasoning, but it must remain distinguishable from what was measured directly.

### Conclusion

What the experiment actually allows us to say about its question.

The conclusion should be no stronger than the evidence, controls, and numerical quality permit.

Do not collapse these four levels into one narrative.

## Anchor claims to behavior

For every important claim, be able to answer:

- What simulation behavior supports this?
- Where is that behavior recorded?
- What comparison makes the claim meaningful?
- Is the simulation numerically trustworthy enough for this claim?
- What else could plausibly explain the same observation?

Prefer specific evidence over labels such as `better`, `stable`, `improved`, or `physical` unless those terms are tied to explicit behavior or metrics.

The most useful interpretation often comes from histories and behavior over the run, not only the final checkpoint.

## Respect the limits of the experiment

Do not claim causality unless the comparison isolates the relevant change well enough to justify it.

Do not turn a solver failure into a physics conclusion unless the experiment specifically establishes that connection.

Do not treat a numerically completed run as a valid physical result merely because Fluent reached the requested iteration count or timestep count.

Do not interpret beyond the model being tested. A credible result can support a conclusion about the chosen CFD formulation without proving that the real separator behaves identically.

If the evidence only supports a directional, conditional, numerical, or exploratory conclusion, say exactly that.

## Use outside knowledge as context, not replacement evidence

Use `cfd-wiki`, literature, Fluent documentation, or specialist reasoning when they help explain an observed mechanism or challenge an interpretation.

Keep the boundary visible:

```text
simulation evidence -> what happened in this experiment
outside knowledge    -> why that behavior might make sense
```

Unless prior evidence is genuinely equivalent to the present setup and question, do not use it to claim what this simulation must have done.

When a consequential interpretation depends heavily on a proposed mechanism, use independent reviewers or `interrogate` to look for alternative explanations and unsupported leaps.

## Treat unexpected results as valuable evidence

A result that contradicts the hypothesis is not a failed experiment if it teaches us something important.

A numerical failure, unexpected trend, non-monotonic response, plateau, oscillation, reversal, or apparently insignificant change may all reshape the investigation.

Ask what the evidence changed in our understanding, not whether it matched the prediction.

## Write the scientific record

`results.md` should preserve the evidence before the story.

Make clear:

- what was actually run;
- what data and plots were examined;
- what was directly observed;
- the numerical-quality limitations;
- the bounded interpretation;
- alternative explanations where they matter;
- the conclusion the experiment supports;
- what remains unresolved.

Significant claims should be traceable to the evidence that carries them.

Preserve historical observations and results. Do not silently rewrite old evidence to fit the current interpretation.

## Handoff

Return the experiment to the scientific phase with a concise account of:

- what the simulation established;
- what it did not establish;
- what changed in the current understanding;
- what uncertainty remains.

The next step should emerge from that updated understanding rather than from loyalty to the original hypothesis or experiment plan.
