---
name: cfd-numerical-analysis
description: "Turn CFD histories and question-specific numerical outputs into plots, tables, and bounded numerical evidence. Use after a run to understand residuals, mass balance, physical monitors, and other simulation behaviour over iteration/time before physical interpretation."
---

# CFD Numerical Analysis

Understand how the simulation behaved over the run before trying to explain why.

The default evidence is not one final number. Prefer iteration- or time-based histories that show how important quantities evolved.

## Start from the experiment question

Read the setup and the evidence plan that was designed with it. Focus on the numerical behaviour that matters for that hypothesis.

At minimum, inspect the basics when available: scaled residual histories, mass balance or imbalance, and important physical monitors. Add question-specific quantities only when they help answer the experiment.

## Show the history

Plots should usually place iteration or physical time on the x-axis.

A final snapshot can be useful as a summary, but it should not replace the history when the quantity is noisy, drifting, oscillatory, or still changing. One endpoint can hide behaviour that completely changes the interpretation.

Preserve raw structure. Do not silently remove divergent tails, smooth away oscillations, interpolate missing sections, or choose a convenient window simply because it looks cleaner.

Use concise tables alongside plots when exact values or cross-case comparisons are useful.

## Describe before diagnosing

Focus first on observations that the data clearly support: whether a quantity falls, rises, drifts, oscillates, plateaus, changes regime, or remains broadly bounded.

Be cautious about sophisticated convergence diagnoses. Noisy CFD histories can be difficult to interpret reliably, and an apparent pattern does not by itself establish its cause.

Do not jump from an oscillating residual to a physics conclusion or from solver completion to numerical credibility. Describe the observed behaviour and keep stronger explanations as hypotheses unless additional evidence supports them.

## Compare cases carefully

For linked experiments, compare like with like: same metric definitions, zones, units, sign conventions, and meaningful iteration/time bases.

Show the individual histories when overlaying cases would hide important behaviour. The campaign should tell a numerical story, not collapse everything into one endpoint ranking.

## Use lightweight statistical help when useful

When raw histories are too noisy to see a broad tendency, call `statistical-analysis` for simple visual aids such as moving averages, rough fitted trends, percentile envelopes, or variability bands.

Keep the raw data visible and treat these transforms as aids to seeing the data, not as replacement evidence.

## Visualise the simulation

Use contours and other field visualisations planned by the experiment when they help reveal the behaviour being tested. Numerical histories and spatial visualisations should complement each other when both are relevant.

## Output

Return the important plots, supporting tables, exact source data and transformations, and a concise set of neutral numerical observations.

Make clear what the histories genuinely show, what remains uncertain, and what numerical limitations matter for `interpret-experiment`.

Physical meaning belongs downstream.