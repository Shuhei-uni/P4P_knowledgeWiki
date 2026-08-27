---
name: statistical-analysis
description: "Apply statistical reasoning to simulation data only when the experiment supports it. Use for transient/repeated/stochastic data, parameter sweeps, regression/response surfaces, uncertainty summaries, effect sizes, and sensitivity ranking; avoid fake inferential certainty from deterministic single-run CFD endpoints."
---

# Statistical Analysis

First decide whether statistics are scientifically appropriate.

## Applicability gate

Statistical analysis is useful when the data contain meaningful sampling or variation, for example:

- transient time windows after startup;
- periodic/unsteady signals;
- repeated stochastic particle or simulation realizations;
- parameter sweeps / DOE;
- regression or response-surface work;
- uncertainty propagation;
- repeated experiments or validation measurements.

Be cautious with:

- one deterministic steady endpoint per case;
- pseudo-replication created by treating highly autocorrelated iterations as independent samples;
- p-values attached to arbitrary solver histories;
- confidence intervals that ignore numerical/model-form error.

If formal statistics are not appropriate, use descriptive numerical analysis instead.

## Define the statistical unit

State what constitutes an observation/sample and why it can be treated as such.

For time series, assess correlation and effective sample size before treating points as independent. For repeated runs, distinguish within-run temporal variation from between-run variation.

## Choose the method from the question

Possible tools include:

- mean/median and spread;
- quantiles;
- confidence/credible intervals when assumptions support them;
- effect sizes and relative changes;
- bootstrap/resampling where appropriate;
- correlation and regression;
- response surfaces;
- ANOVA/factor effects for designed matrices;
- sensitivity ranking;
- uncertainty propagation;
- outlier diagnostics;
- equivalence/practical-difference reasoning when a meaningful tolerance exists.

Do not use a more complex method when a direct effect size and uncertainty band answers the question.

## Time-series safeguards

Before computing time averages:

- identify/remove startup only with evidence;
- choose a physically meaningful averaging window;
- assess autocorrelation or periodicity;
- report the physical duration represented;
- test sensitivity to nearby windows;
- avoid presenting thousands of correlated timesteps as thousands of independent observations.

## Assumptions

State assumptions that materially affect the result, such as:

- independence;
- stationarity;
- distributional form;
- linearity;
- homoscedasticity;
- adequate sample size;
- chosen prior/tolerance if relevant.

If assumptions are weak, use robust/descriptive alternatives and lower the strength of the claim.

## Statistical vs numerical uncertainty

Keep separate:

- temporal/stochastic variability;
- discretization/timestep error;
- iterative convergence error;
- parameter uncertainty;
- model-form uncertainty;
- experimental/reference uncertainty.

A tight statistical interval does not prove the CFD model is accurate.

## Cross-case inference

Before comparing cases, confirm that the experiment design supports the comparison and that numerical adequacy is not the dominant uncertainty.

Report practical effect size alongside any inferential statistic. A statistically detectable difference may be physically irrelevant, and a physically important difference may be unresolved with the available samples.

## Delegate/check

For consequential analysis, use `interrogate` or an independent subagent to check:

- sample definition;
- independence/autocorrelation;
- window selection;
- regression assumptions;
- whether the statistical conclusion exceeds the experiment design.

## Output

Return:

1. why statistical analysis is or is not appropriate;
2. sample/unit definition;
3. method and assumptions;
4. effect estimates and uncertainty;
5. robustness/diagnostic checks;
6. limitations;
7. neutral statements safe to use in `results.md`.

Leave numerical CFD adequacy to `cfd-numerical-analysis` and physical causality to `interpret-experiment`.