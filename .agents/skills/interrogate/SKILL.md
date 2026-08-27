---
name: interrogate
description: "Adversarially review a proposed experiment, analysis, interpretation, or next action using independent subagents. Use before expensive runs or consequential conclusions to expose hidden assumptions, confounders, unsupported claims, and missing evidence."
---

# Interrogate

Attack the work before reality does.

## What to interrogate

Useful targets include:

- `setup.md` before an expensive run;
- experiment-design rationale;
- analysis plan;
- numerical adequacy conclusion;
- interpretation/results claims;
- proposed next action.

## Independent review

Spawn several fresh subagents or reviewers. Give them the artifact plus the relevant goal/evidence, but do not prime them with the main agent's defense.

Assign either the same review question to all reviewers or complementary lenses such as:

- experiment design/confounding;
- CFD numerics;
- data/statistics;
- physical interpretation;
- implementation/reproducibility.

Avoid fake personas when a simple independent review is enough.

## Questions to ask

Reviewers should look for:

- assumptions presented as facts;
- variables that changed unintentionally;
- missing decisive evidence;
- metrics/plots that do not answer the question;
- numerical inadequacy hidden by solver completion;
- causal claims unsupported by controls;
- alternative explanations;
- cherry-picked windows or endpoints;
- project-goal drift;
- unnecessary complexity;
- cheaper tests that would provide the same information.

## Synthesize, don't obey blindly

The main agent groups criticism into:

- confirmed issue;
- plausible issue requiring evidence;
- disagreement/reviewer preference;
- rejected criticism with reason.

Do not implement every suggestion. Adversarial review can itself overcomplicate a simple experiment.

Require evidence or a clear logical failure before materially changing the plan.

## Severity

Classify confirmed issues:

- **blocker** — run/claim should not proceed;
- **important** — should be fixed or explicitly accepted;
- **minor** — improves clarity/robustness but does not change the decision;
- **non-issue** — rejected after synthesis.

## Output

Return:

- strongest surviving criticisms;
- evidence supporting them;
- exact changes required before proceeding;
- accepted residual risks;
- whether the artifact is ready to proceed.

Keep the final artifact lean. The goal is stronger reasoning, not more ceremony.