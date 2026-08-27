---
name: numerical-data-analysis
description: "Perform question-driven numerical analysis of simulation histories and cross-case data: alignment, normalization, windowing, integration, derivatives, convergence trends, frequency/change-point analysis, and derived metrics. Use after plan-analysis identifies a numerical method needed to answer the experiment."
---

# Numerical Data Analysis

Turn extracted simulation data into quantitative evidence without hiding dynamics or manufacturing certainty.

## Start from the requested metric

Read the analysis plan and identify:

- source data;
- independent axis: iteration, timestep, physical time, mesh size, parameter value, etc.;
- units and sign convention;
- comparison cases;
- required derived quantity;
- intended scientific interpretation.

Do not begin by applying a favorite smoothing or statistics method.

## Common operations

Use as appropriate:

- align histories by true iteration/physical time;
- preserve missing segments and failure tails;
- normalize by physically meaningful reference values;
- compute relative/absolute differences;
- moving-window mean, median, range, standard deviation, or slope;
- numerical derivatives and integrals;
- cumulative quantities;
- nondimensional groups;
- convergence rates/error norms;
- time/iteration-to-threshold when a threshold is predeclared;
- change-point detection;
- autocorrelation/frequency/spectral analysis for persistent oscillations;
- parameter-response and sensitivity trends.

## Preserve raw structure

Never silently:

- interpolate missing solver history;
- delete divergent tails;
- clip data without annotation;
- smooth a signal and present it as raw;
- realign cases using arbitrary index positions when true iteration/time exists;
- mix gauge/absolute pressure or inward/outward flux conventions.

Keep transformed data traceable to the source.

## Window selection

Averages and slopes depend on the chosen window. Select windows using scientific reasoning:

- exclude startup only when there is evidence startup has ended;
- for steady cases, test whether the result changes with nearby end windows;
- for transient cases, use physical-time windows and verify enough cycles/events where relevant;
- expose sensitivity to window choice when it affects the conclusion.

Do not choose a window solely because it gives a cleaner result.

## Derived metrics

For every derived metric state:

- formula;
- source variables;
- units;
- sign convention;
- normalization/reference;
- time/iteration reduction;
- assumptions.

Prefer measured quantities first, derived quantities second.

## Cross-case comparison

Before comparing cases, verify:

- same metric definition;
- same zones/surfaces/phases;
- compatible units;
- comparable numerical/physical state;
- relevant controlled variables really are controlled.

If not, flag the comparison as limited rather than forcing a ranking.

## Plotting principles

Plot for the experiment question.

Prefer:

- iteration/time on the x-axis for convergence or evolution questions;
- separate branch plots when combining cases would obscure dynamics;
- clear stage/checkpoint boundaries;
- measured series with transformed/averaged series distinguishable;
- annotations for failures, missing data, or scheme changes.

Do not create decorative plots or plots whose axes cannot support the intended claim.

## When to use statistics

If uncertainty across repeated/transient/stochastic samples needs formal statistical treatment, hand off to `statistical-analysis`. Descriptive moving-window variation alone does not automatically require inferential statistics.

## Output

Return:

- numerical methods used and why;
- exact source data and transformations;
- plots/tables/derived metrics;
- robustness checks such as window sensitivity;
- limitations introduced by missing or incomparable data;
- neutral quantitative observations suitable for `results.md`.

Leave CFD trustworthiness to `cfd-numerical-analysis` and causal/physical meaning to `interpret-experiment`.