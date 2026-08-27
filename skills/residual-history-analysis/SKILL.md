---
name: residual-history-analysis
description: Extract, stitch, and plot Fluent residual histories using native iteration coordinates across staged, restarted, or batched runs.
---

# Residual history analysis

Use this skill when residual history is part of the numerical evidence.

## Rules

- Use Fluent/native iteration as the x-axis when available; never replace it
  with sample index.
- Do not blindly concatenate restarted or batched segments.
- Remove only verified duplicate iterations.
- Preserve real gaps, failure tails, stage boundaries, and the actual horizon;
  do not interpolate unknown iterations.
- State stitching limits and distinguish a complete history from a partial one.

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

## Known working code

Prefer reusable code, then a generic script, then a campaign pattern; live
Fluent evidence wins over prose/API memory.

- `PyAnsys/scripts/inspection/export_residuals.py` for direct residual export.
- `PyAnsys/scripts/report/build_03a_stage3_stitched_scaled_residuals.py` for
  proven staged/batched parsing and merge concepts.

The Stage-3 script is campaign-specific. Reuse its parser/merge/plot concepts,
not its 03A names, paths, or branch assumptions. Extract reusable behaviour
only when current experiments need it.
