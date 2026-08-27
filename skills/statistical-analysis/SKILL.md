---
name: statistical-analysis
description: "Add lightweight statistical summaries to noisy CFD histories when they make trends easier to see. Use for moving averages, rough trend fits, percentile envelopes, variability bands, and similar visual aids; do not manufacture certainty from solver data."
---

# Statistical Analysis

Use statistics to make noisy simulation behaviour easier to see, not to create stronger claims than the data support.

This skill is usually a helper for `cfd-numerical-analysis`.

## Keep the raw signal visible

Start from the original iteration/time history. Any fitted or smoothed quantity is a visual aid layered on top of the raw evidence.

Never present a moving average, fitted line, percentile band, or variance estimate as though it were the solver output itself.

## Prefer simple descriptive tools

Use the simplest method that improves interpretation. Useful examples include moving or windowed averages, median trends, rough fitted trend lines, percentile envelopes such as a 95th-percentile line or band, rolling spread, variance or standard-deviation bands, and simple slope estimates over a declared window.

The goal is often to expose a broad tendency in data that are too jumpy to judge by eye.

## Do not overstate the result

A trend line does not prove convergence. A narrow band does not prove numerical accuracy. Thousands of solver iterations are not automatically thousands of independent statistical samples.

Avoid formal hypothesis testing, p-values, elaborate uncertainty claims, or complex models unless the experiment genuinely requires them and the data structure supports them.

## Make transformations explicit

State what transformation was applied, the window or fitting range, and why it helps. If the apparent trend changes materially with a reasonable alternative window, show or report that sensitivity rather than hiding it.

## Output

Return the statistical overlay or summary together with the raw plot, a short description of the method, and a bounded statement of what visual tendency it helps reveal.

Leave the scientific conclusion to `interpret-experiment`.