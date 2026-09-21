---
name: cfd-numerical-analysis
description: "Analyse CFD run evidence and produce the smallest figure/table set needed to judge numerical behaviour and the experiment question."
---

# CFD Numerical Analysis

Start from the experiment question and its pre-run evidence contract.

Produce the decisive evidence first. Use supporting branches only when relevant:

- [histories](references/histories.md) — residuals, Fluent report histories,
  stitching, trend summaries;
- [model-specific evidence](references/model-specific.md) — DPM, EWF, phase
  routing, balances, inventory;
- [figures](references/figures.md) — when creating or exporting a native Fluent
  contour, vector scene, plane, or spatial comparison; source identity,
  post-processing, export, visual QA, and provenance.
- [interpretation](references/interpretation.md) — when translating planned
  evidence into a hypothesis judgement, bounded claim, and `results.md` story.

## Analysis order

1. Build the planned core figures/tables.
2. Check numerical adequacy needed to trust their message.
3. Quantify the physical metric(s) that answer the experiment question.
4. Add only diagnostics that help explain uncertainty or a surprising result.
5. Return bounded observations and limitations to `phase-loop`.

Prefer a few high-information plots over overview dashboards.

Keep raw signals visible when smoothing or summarising them. Do not infer
physics from residual shape alone, and do not treat solver completion as
numerical credibility.

If required evidence is missing, identify the narrowest repair, reconstruction,
or rerun needed. Missing evidence is a workflow problem to recover, not a reason
to ask for human review.

The analysis output must identify the exact run/artifacts it used and keep
observation separate from interpretation.
