---
name: report-writing
description: "Produce concise evidence-grounded technical reports from Project records, with a small figure-led narrative and clear claim limits."
---

# Report Writing

Treat the report as a communication layer over `Project/`, not a second
experiment log.

When the requested output is an experiment record, follow the
[experiment presentation contract](../../../Project/experiments/README.md#presentation):
tables and figures with short figure interpretations. The report structure below
applies to separately requested technical reports.

For requests centred on academic argument, which findings to emphasise, report
flow, or language, use [STEM Research Writing](../stem-research-writing/SKILL.md).
When this workflow owns report production, consult specific references from
that skill as needed, including its
[questions and suggestions](../stem-research-writing/references/questions-and-suggestions.md)
when author choices remain open.

If the user already gave scope, audience, and output format, proceed. Ask only
for a materially missing choice that would change the report.

## Build the evidence spine

Read the relevant supplied rubric and report guidance before substantive
drafting. Reuse unchanged guidance already read; confirm each section's purpose
before placing methods, observations or interpretation in it.

Start at `Project/index.md`, then read only the selected phases/campaigns and
their current `CONTEXT.md`, `setup.md`, `results.md`, and relevant figure
artifacts.

Use [evidence assembly](references/evidence-assembly.md) when reconciling
several experiments, tracing claims to sources, or choosing the smallest figure
set that can carry the report's argument.

For each section answer:

1. what we wanted to learn;
2. what changed and why;
3. what the decisive evidence shows;
4. what conclusion is justified;
5. what remains unresolved / comes next.

Use Git history only when the current records do not explain an important
decision.

## Figures

Prefer a few figures that carry the argument. Use `cfd-numerical-analysis`
when a new CFD figure or comparison is needed.

Each report-facing figure needs:

- source run/artifact;
- the question it answers;
- a concise observation;
- a caption that does not overclaim.

If a required figure is missing, use a labelled placeholder or request the
narrowest evidence repair. Do not invent a figure.

## Draft

In `P4P_knowledgeWiki` documents, use document-relative paths for internal links and images so they work in Obsidian.

Write around the evidence rather than chronology. Omit failed attempts unless
they changed the scientific direction or explain an important limitation.

Keep observation, interpretation, and claim limits clear. A completed solver run
is not automatically a validated scientific result.

When HTML/final visual presentation is requested, read `REPORT-DESIGN.md` for
layout-specific guidance.

## Completion

The report is complete when the requested scope has a coherent evidence-backed
story, every material claim can be traced to Project evidence, figures are
readable/provenanced, and important limitations are explicit.

Do not add an approval checkpoint unless the user asks to review an outline or
draft before completion.
