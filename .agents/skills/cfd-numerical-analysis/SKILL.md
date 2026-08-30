---
name: cfd-numerical-analysis
description: "Turn CFD histories and question-specific numerical outputs into a small set of high-impact plots, supporting tables, and bounded numerical evidence. Use after a run to execute the experiment's planned core figures first, then assess residuals, mass balance, physical monitors, and other supporting simulation behaviour before physical interpretation."
---

# CFD Numerical Analysis

Understand how the simulation behaved over the run before trying to explain why.

The default evidence is not one final number and not a generic overview dashboard. Prefer the **few figures that were deliberately planned to answer the experiment question**, supported by numerical diagnostics where needed.

## Start from the experiment question and core figure plan

Read the setup, evidence plan, and **Core figure plan** that were designed before the run.

Execute the planned core figures first. They are the primary numerical evidence path because they were chosen before the result was known.

For each planned figure, verify:

- the sub-question it is meant to answer;
- the exact x-axis, y-axis/field, units, sign convention, phase/zone/surface scope;
- the intended series/cases and comparison basis;
- the declared full-run or selected comparison window;
- any reduction or derived metric;
- the source monitor/report/file/field and whether the evidence is complete.

If the planned data exists, do not replace the figure with an easier generic overview. If the required evidence is missing, mark that figure `partial`, `unavailable`, or `requires rerun` rather than silently substituting a vaguely related metric.

## Keep the scientific figure set small

Aim to return a compact figure set that makes the numerical story obvious.

As a default:

- discovery: usually `1-3` core screening figures;
- hypothesis test: usually `2-5` core figures;
- supporting diagnostic plots are separate and should not crowd out the core set.

A useful ordering is usually:

1. **direct-answer figure** — the quantity most directly tied to the experiment question;
2. **mechanism/comparison figure** — the secondary behavior that helps explain or distinguish the competing possibilities;
3. **numerical-adequacy figure** — only the residual/balance/stability evidence needed to judge whether the first two can be trusted;
4. optional additional core figures only when they add a distinct scientific message.

Do not create five plots when two communicate the result better.

## Plot one message at a time

Plots should usually place iteration or physical time on the x-axis for quantities that evolve during the solve.

A final snapshot can be useful as a summary, but it should not replace the history when the quantity is noisy, drifting, oscillatory, or still changing. One endpoint can hide behaviour that completely changes the interpretation.

Prefer one scientific message per figure. Do not dump every active monitor into the same figure simply because the data exists.

Avoid dual y-axes unless there is a strong scientific reason. Separate figures are usually easier to interpret.

For spatial evidence, use contours/profiles only when they answer the planned spatial question. Generic velocity, pressure, turbulence, or phase contours are supporting visuals, not automatically useful results.

Preserve raw structure. Do not silently remove divergent tails, smooth away oscillations, interpolate missing sections, or choose a convenient window simply because it looks cleaner.

If a moving average, fitted trend, final-window mean/range, or other reduction is useful, keep the raw data available and state the transformation and window explicitly.

## Treat overview diagnostics as supporting evidence

At minimum, inspect the numerical basics when available: scaled residual histories, mass balance/imbalance, and relevant physical monitors.

These checks are important, but they do **not** automatically belong in the main core figure set. A residual dashboard, all-monitor overview, or bulk diagnostic collage should be treated as supporting evidence unless numerical convergence or solver behaviour is itself the experiment question.

It is acceptable to generate an overview artifact for debugging or completeness. Do not present it as the main result when more discriminating planned figures exist.

## Describe before diagnosing

Focus first on observations that the data clearly support: whether a quantity falls, rises, drifts, oscillates, plateaus, changes regime, or remains broadly bounded.

Tie each important observation to the figure that shows it. Prefer a few figure-linked observations over a catalogue of every available metric.

Be cautious about sophisticated convergence diagnoses. Noisy CFD histories can be difficult to interpret reliably, and an apparent pattern does not by itself establish its cause.

Do not jump from an oscillating residual to a physics conclusion or from solver completion to numerical credibility. Describe the observed behaviour and keep stronger explanations as hypotheses unless additional evidence supports them.

## Compare cases carefully

For linked experiments, compare like with like: same metric definitions, zones, units, sign conventions, and meaningful iteration/time bases.

Show individual branch histories when a broad overlay would hide important behaviour. Do not create unreadable all-case spaghetti plots.

Use a targeted overlay only when the direct comparison between a small number of cases is itself the message. A compact endpoint/final-window comparison can support the histories after the history has established that the statistic is meaningful.

The campaign should tell a numerical story, not collapse everything into one endpoint ranking.

## Use lightweight statistical help when useful

When raw histories are too noisy to see a broad tendency, call `statistical-analysis` for simple visual aids such as moving averages, rough fitted trends, percentile envelopes, or variability bands.

Keep the raw data visible and treat these transforms as aids to seeing the data, not as replacement evidence.

## Add responsive figures only when the result earns them

Unexpected data may reveal a question that the pre-run figure plan could not anticipate.

When a new plot would materially clarify an anomaly, mechanism, regime change, or failure, add it as a clearly labelled **responsive figure**. State why it was added after seeing the data.

Do not silently replace the original core figures with post-hoc plots that make the result look cleaner or more convincing. Preserve the planned figure set for auditability.

## Output

Return:

1. the planned core figures, with completeness status;
2. any clearly labelled responsive figure that materially improves understanding;
3. only the supporting diagnostic plots needed to assess numerical adequacy;
4. concise tables for exact values or final-window statistics where useful;
5. exact source data, units, sign conventions, windows, and transformations;
6. a short set of neutral observations linked to the figures.

Make clear what the figures genuinely show, what remains uncertain, and what numerical limitations matter for `interpret-experiment`.

Physical meaning belongs downstream.
