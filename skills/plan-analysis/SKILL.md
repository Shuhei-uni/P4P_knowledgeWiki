---
name: plan-analysis
description: "Translate an experiment question into the minimum evidence, plots, metrics, numerical checks, and comparisons required to answer it. Use before or immediately after a run so analysis follows the objective rather than whatever data is easiest to plot."
---

# Plan Analysis

Decide what evidence is needed before running extraction scripts.

## Core question

Start with:

> What observation would answer this experiment's primary question?

Read the target `setup.md`, relevant comparison setup/results, and the observed run status.

## Build the evidence chain

For each experiment define:

```text
question
-> decisive quantities
-> required histories/fields
-> analysis method
-> plot/table
-> comparison
-> claim the evidence could support
```

Every proposed plot must have a reason to exist.

## Analysis plan

Specify:

- **primary metric(s)** — directly answer the question;
- **supporting metric(s)** — explain or validate the primary result;
- **numerical-quality checks** — determine whether the result is usable;
- **comparison basis** — parent, branch, baseline, literature, mesh/timestep level, or time window;
- **required plots/tables** — each tied to a question;
- **required raw sources** — monitor history, report file, field data, final state, transcript, etc.;
- **derived quantities** — equations, sign convention, normalization, units;
- **decision logic** — what patterns would materially change interpretation.

Do not invent hard acceptance thresholds unless they were pre-agreed or the user asks for a proposed threshold.

## Think before the run when possible

Some evidence cannot be reconstructed later. Identify any required:

- report definitions;
- monitor histories;
- transient time series;
- phase-specific fluxes;
- DPM/EWF histories;
- checkpoint cadence;
- saved surfaces/fields.

If these must be configured before solving, feed them back into `setup.md` / `implement-experiment` before the long run begins.

## Choose specialists

Use:

- `cfd-numerical-analysis` for convergence, conservation, stationarity, mesh/timestep/iteration adequacy, solver failures, and CFD-specific trustworthiness;
- `numerical-data-analysis` for histories, windowing, integration, derivatives, normalization, frequency/change-point analysis, and cross-case numerical comparison;
- `statistical-analysis` when repeated/transient/stochastic/sweep data genuinely supports statistical inference or descriptive uncertainty;
- existing deterministic PyAnsys scripts for extraction and plotting.

A specialist is invoked because the question requires it, not because the skill exists.

## Minimum useful analysis

Prefer the smallest evidence pack that can answer the question. Add diagnostic analyses only when they help distinguish explanations or establish trustworthiness.

Avoid:

- plotting every report definition;
- final-value-only conclusions for unsteady histories;
- residual-only conclusions when physical monitors are the question;
- cross-case plots with incomparable iteration/time axes;
- derived metrics whose source quantities are unavailable or ambiguous.

## Missing evidence

Classify missing evidence explicitly:

- recoverable from current artifacts;
- requires additional read-only extraction;
- requires more iterations/time;
- requires rerun with new monitor/instrumentation;
- cannot be recovered.

Do not substitute an easier metric and pretend it answers the original question.

## Output

Produce a concise analysis contract containing:

1. experiment question;
2. required analyses in priority order;
3. exact evidence/source for each;
4. intended plot/table and x-axis/time basis;
5. numerical-quality checks;
6. comparison/derived metric definitions;
7. evidence gaps or rerun requirements;
8. which specialist skills/tools should execute each part.

Hand this contract to the extraction/analysis workers and later to `interpret-experiment`.