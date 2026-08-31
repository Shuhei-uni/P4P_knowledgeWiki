---
name: interpret-experiment
description: "Turn simulation evidence into a bounded scientific interpretation after the required analysis exists. Preserve the pre-run evidence contract, separate observation from interpretation, and never treat a completed run as permission to waive missing qualification evidence or close the phase."
---

# Interpret Experiment

Interpret what the simulation showed, not what you expected it to show.

Reasoning proposes. Simulation tests. Data constrains the conclusion.

Literature, prior experience, and physical intuition may help explain a result. They do not substitute for the result itself.

## Respect lifecycle state and the pre-run evidence contract

Read the experiment setup, results/evidence, and phase-root `phase-state.yaml`.

For discovery, interpretation helps decide whether discovery has earned a specific hypothesis. It does not promote discovery evidence into a final phase claim.

For hypothesis qualification, terminal execution `COMPLETE` is only execution evidence. Before the phase can rely on the interpretation, the required analysis must be produced and `verify-phase-transition` must later judge `HYPOTHESIS_EVIDENCE`.

Do not silently change the required evidence after seeing the result.

If the setup declared scaled residual histories, phase balances, restart/continuation evidence, a qualification window, or another metric as **required**, and it is missing, record that as a gate-critical evidence gap. Do not replace it with prose or a convenient surrogate unless the experiment is explicitly redesigned upstream.

## Start from the evidence

Read:

- experiment question and hypothesis;
- verified discovery basis for hypothesis work;
- controlled changes and invariants;
- working assumptions and claim limits;
- intended strong statement form for hypothesis work;
- required versus supporting evidence;
- core figure plan;
- measured/derived data;
- numerical-quality assessment;
- comparison cases and declared analysis windows.

The preplanned core figures are the primary visual evidence path because they were designed before the result was known. Check whether each was produced from the intended source, axes, scope, window, and comparison basis.

Do not accept a generic overview dashboard as a substitute for planned discriminating figures.

If a planned figure can still be produced from existing data, produce/request it before making the main interpretation. If the required history was never captured, preserve the gap explicitly.

## Read figures for their intended message

For each core figure ask:

- What does the plotted quantity directly show over the declared window/domain?
- What reference/comparison makes that observation meaningful?
- Does the figure distinguish the competing explanations it was designed to test?
- Is any smoothing/reduction/normalization/sign conversion hiding raw behaviour?
- Does the figure require supporting numerical-quality evidence before its scientific message is trustworthy?

Prefer a few strong figure-linked observations over a catalogue of every available variable.

Supporting residual dashboards, diagnostics, or extra contours may help explain anomalies but should not replace the declared core argument.

## Keep four levels separate

### Hypothesis

What was proposed before the evidence was seen.

### Observation

What recorded simulation data directly shows. Trace important observations to a number, history, field, planned core figure, comparison, or solver event.

### Interpretation

What those observations may mean, including connections to theory/literature and plausible alternative explanations.

### Conclusion

What this **experiment** actually allows us to say.

Do not collapse these levels.

The experiment conclusion is not automatically the phase conclusion.

## Judge the hypothesis from its predeclared criteria

For hypothesis qualification, explicitly classify the result against the pre-run contract:

- evidence supporting the hypothesis;
- evidence weakening/rejecting it;
- evidence supporting the competing explanation;
- unresolved ambiguity;
- numerical credibility of the relevant claim;
- whether the intended strong statement form can actually be populated from the evidence.

If the qualification run completed but required evidence is missing, the proper classification may be:

```text
execution complete
hypothesis evidence incomplete
```

Do not force `supported` or `rejected` when the evidence contract cannot be satisfied.

## Revisit working assumptions without inventing facts

Use:

- `accepted-for-now`;
- `questioned`;
- `materially-challenged`.

Only elevate an assumption when evidence gives a concrete reason.

A missing plant fact or human-owned target remains missing. Do not convert it into a scientific conclusion because a numerical surrogate produced a trend.

## Anchor claims to behaviour

For every important claim answer:

- What simulation behaviour supports this?
- Which figure/value/artifact records it?
- What comparison makes it meaningful?
- Is the numerical evidence sufficient for this exact claim?
- What else could explain it?
- Does a challenged assumption weaken it?

Avoid labels such as `better`, `stable`, `converged`, `physical`, or `controlled` without explicit criteria and evidence.

For steady/stationary/reference claims, use the declared qualification window and any required continuation/restart evidence. Do not infer stationarity from a favourable short tail.

## Respect experiment limits

Do not claim causality unless the comparison isolates the change sufficiently.

Do not turn solver failure into physics unless the experiment establishes that connection.

Do not treat reaching the requested horizon as proof of numerical/physical credibility.

Do not extend a CFD-formulation result directly to the real separator without validation evidence.

Directional, conditional, numerical, exploratory, or negative conclusions are all acceptable when that is what the data supports.

## Use outside knowledge as context

Use `cfd-wiki`, literature, Fluent documentation, or specialist reasoning to explain/challenge observed mechanisms.

Keep the boundary visible:

```text
project simulation evidence -> what happened here
outside knowledge            -> why it may make sense / what else may explain it
```

For consequential interpretation, use `interrogate` or independent review to look for unsupported leaps and alternative explanations.

## Treat unexpected results as useful

Contradicting the hypothesis is not experiment failure.

Unexpected trends, plateaus, oscillations, reversals, solver pathologies, or small effects may materially reshape the investigation.

If an unexpected result requires a responsive figure, add it clearly as **responsive evidence** while retaining the planned core figures.

## Write the scientific record

`results.md` should state:

- what was actually run and verified;
- requested and actual horizon;
- whether planned core figures were produced completely/partially/not at all;
- required-evidence completeness;
- key direct observations;
- numerical-quality result/limits;
- hypothesis classification when applicable;
- bounded interpretation;
- alternative explanations;
- experiment conclusion;
- assumptions whose state changed;
- what remains unresolved.

For hypothesis work, explicitly record whether the result appears ready to be sent to `verify-phase-transition` for `HYPOTHESIS_EVIDENCE` or which missing evidence prevents that.

Do not mark the phase concluded here.

## Handoff

Return to `scientific-phase-loop`:

- what the experiment established;
- which planned figures/evidence carry that statement;
- required evidence that is missing, if any;
- what it did not establish;
- hypothesis classification when applicable;
- what changed in current understanding;
- assumption-state changes;
- remaining uncertainty;
- whether the next required lifecycle action is `DISCOVERY_EVIDENCE`, `HYPOTHESIS_EVIDENCE`, further discovery/qualification work, or a human lock.
