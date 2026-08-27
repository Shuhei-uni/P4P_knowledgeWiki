---
name: swarm
description: "Use parallel read-only subagents for broad literature, documentation, and research discovery, then synthesize the evidence into a compact scientific picture. Use when one research question can be split into several independent searches."
---

# Swarm

Use Swarm primarily to widen research coverage without filling the main context with every source read.

It is especially useful for literature review, Fluent/documentation research, prior published modelling approaches, known numerical issues, physical mechanisms, and other broad evidence discovery that can be investigated independently.

## Split by useful research question

Give each worker a narrow, non-overlapping question or search angle. Different workers might investigate different mechanisms, modelling approaches, solver guidance, or bodies of literature relevant to the same uncertainty.

Keep workers read-only. They gather evidence; they do not decide the scientific direction or mutate the experiment.

## Ask for distilled evidence

Each worker should return the important finding, the supporting source or repository path, important limitations or disagreement, and why the evidence matters to the question being investigated.

Do not return full source dumps when a concise evidence summary and pointer will do.

## Synthesize centrally

The main agent combines the findings, resolves obvious duplication, preserves meaningful contradictions, and decides what the literature actually changes about the current hypothesis or experiment design.

Literature can justify hypotheses and help choose informative simulations. Unless it is genuinely equivalent evidence, it does not substitute for running the project simulation and observing its data.

Use another specialist when the work is no longer broad research discovery.