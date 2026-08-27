---
name: design-experiment
description: "Design high-information simulation experiments from a research question, prior evidence, and constraints. Use to propose controlled CFD experiments, sensitivities, diagnostic runs, or discriminating comparisons before creating setup.md."
---

# Design Experiment

Design experiments to answer a question, not to generate more cases.

## Start with the decision problem

State:

- the primary scientific question;
- what is currently known;
- the competing explanations or uncertainty;
- what evidence would materially change the conclusion;
- relevant compute/time constraints.

If no plausible result would change the next decision, do not propose the experiment.

## Candidate structure

Each candidate should contain:

- **Question** — one sentence;
- **Hypothesis / competing explanations** — when appropriate;
- **Parent/reference** — the case or evidence being compared;
- **Controlled change** — the variable(s) deliberately changed;
- **Frozen context** — what must remain identical;
- **Required evidence** — metrics, histories, plots, fields, comparisons;
- **Numerical requirements** — enough to make the result interpretable;
- **Possible outcomes** — what each outcome would imply;
- **Cost/risk** — rough compute and implementation risk;
- **Information value** — why this is worth running now.

## Experimental discipline

Prefer the smallest experiment that separates explanations.

Use one-variable-at-a-time when isolating causality is important and interactions are not the main question. Use small factorial/matrix designs when interaction effects are themselves important and the compute budget supports them.

Distinguish clearly between:

- physics experiments;
- numerical-method experiments;
- sensitivity screening;
- verification studies;
- validation studies;
- diagnostic/recovery runs.

Do not mix these labels. A timestep study is not evidence for a physics mechanism unless the numerical dependence is first resolved.

## Control confounding

For each proposed comparison ask:

- Are multiple meaningful variables changing at once?
- Are cases compared at equivalent iteration/physical-time or statistical states?
- Did initialization change as well as the intended variable?
- Did numerical schemes, mesh, or monitor definitions change?
- Would the result distinguish the proposed mechanisms?

If not, redesign the comparison or state the limitation explicitly.

## Plan evidence before running

Call `plan-analysis` conceptually while designing the experiment. If the decisive evidence requires a monitor/history that must exist during the run, put that requirement into the setup before implementation.

Do not depend on a final `.dat.h5` to answer a question that requires a time history.

## Generate alternatives with subagents

For an important or expensive next step, use `arena` or a small `swarm`:

- ask independent subagents for alternative experiment designs;
- require each to identify confounders and expected information gain;
- synthesize rather than voting blindly.

Use `interrogate` on the leading design before execution if a mistaken setup would waste substantial compute.

## Rank candidates

Rank primarily by:

1. ability to answer the current question;
2. ability to discriminate competing explanations;
3. numerical/implementation feasibility;
4. compute cost;
5. reversibility and reuse of results.

Do not rank primarily by novelty or sophistication.

## Output

Return a small set of genuinely different candidates, usually 3–6 when human selection is expected. Recommend one and explain why.

Once selected, convert the chosen design into `setup.md` with:

- question;
- rationale;
- parent/reference;
- controlled changes;
- preserved settings;
- run plan;
- evidence/analysis requirements;
- known limitations.

Do not write results or conclusions into the setup.