---
name: interpret-experiment
description: "Convert simulation evidence into bounded scientific interpretation with explicit claim-to-evidence links, alternative explanations, and limitations. Use after the required analysis is available and numerical adequacy has been assessed."
---

# Interpret Experiment

Interpret what the evidence supports, not what the experiment was hoped to show.

## Preconditions

Read:

- `setup.md` question and controlled changes;
- analysis plan;
- measured/derived evidence and plots;
- `cfd-numerical-analysis` status;
- relevant comparison results.

If decisive evidence is missing or numerical status is `insufficient`/`failed`, restrict interpretation accordingly and state the gap.

## Separate four levels

Keep these distinct:

1. **Observation** — directly seen in a plot/number/state.
2. **Interpretation** — what that observation likely means.
3. **Hypothesis/explanation** — plausible mechanism not yet proven.
4. **Conclusion** — answer justified by the experiment and its controls.

Do not write hypotheses as observations.

## Claim-evidence discipline

For every major claim identify:

- supporting figure/table/metric;
- exact comparison;
- numerical-quality status;
- important limitation;
- plausible alternative explanation.

Prefer:

```text
Claim
-> measured evidence
-> comparison
-> limitation
```

Avoid vague statements such as "more stable", "better", or "improved" unless the metric defining them is explicit.

## Causality gate

Before claiming a controlled variable caused an effect, ask:

- Was it the only meaningful change?
- Were cases compared at equivalent states/windows?
- Could initialization, timestep, mesh, solver settings, or run length explain the difference?
- Is the observed response larger than known numerical/temporal variability?

If not, use association/directional language rather than causal language.

## Negative and failed experiments

A failed or inconclusive simulation can still support useful conclusions about:

- numerical viability;
- implementation feasibility;
- invalid assumptions;
- evidence gaps;
- eliminated hypotheses.

Do not turn numerical failure into a physics conclusion unless the experiment specifically establishes that link.

## Alternative explanations

For consequential findings, generate at least the strongest plausible alternative explanation and state what evidence would distinguish it.

Use `interrogate` when the result will materially influence the next project direction.

## Literature/reference use

Use `cfd-wiki` when external knowledge is needed to contextualize a mechanism or modelling expectation. Keep clear which statements come from the simulation and which come from literature/general CFD knowledge.

Do not retroactively redefine the experiment to match literature.

## Write results.md

Structure report-facing interpretation around:

- experiment question;
- what was actually run;
- measured evidence and plots;
- numerical/evidence quality;
- neutral observations;
- bounded interpretation;
- alternative explanations/limitations;
- what remains unresolved.

Preserve historical evidence; do not silently overwrite an earlier interpretation without provenance.

## Handoff

Return a concise set of:

- supported conclusions;
- unsupported/unsafe claims;
- unresolved explanations;
- evidence that would resolve them.

Then invoke `next-action` rather than automatically proposing another setup.