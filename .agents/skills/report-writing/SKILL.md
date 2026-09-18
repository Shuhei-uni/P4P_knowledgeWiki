---
name: report-writing
description: "Produce concise evidence-grounded technical reports from Project records, with a small figure-led narrative and clear claim limits."
---

# Report Writing

Treat the report as a communication layer over `Project/`, not a second
experiment log.

If the user already gave scope, audience, and output format, proceed. Ask only
for a materially missing choice that would change the report.

## Build the evidence spine

Start at `Project/index.md`, then read only the selected phases/campaigns and
their current `CONTEXT.md`, `setup.md`, `results.md`, and relevant figure
artifacts.

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
