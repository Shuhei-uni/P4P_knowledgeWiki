---
name: report-writing
description: "Plan and produce concise, evidence-grounded technical reports. Use when choosing report scope, agreeing a narrative, selecting project evidence, drafting sections, placing figures, or rendering a report for review. Read REPORT-DESIGN.md for HTML, figure, table, and visual-layout decisions."
---

# Report Writing

Own the report as a visual argument: each section should make it easy for the
reader to follow what we wanted to learn, what we changed to learn it, what the
evidence shows, what conclusion is justified, and what question comes next.

The report is a communication layer over the project records. It is not a
second experiment log and it must not become a catalogue of every run.

## Start with scope, then earn the draft

The first interaction is a scope gate. Before reading the whole project or
writing prose, ask a concise question such as:

> Which phases, campaigns, or time window should this report cover, and who is
> the audience?

If the user already supplied the scope, restate it briefly and ask only for a
materially missing item such as the audience, meeting date, or output format.
Do not make the user answer a long intake questionnaire when the scope is
already clear.

Once scope is known, give a short rough flow for approval. The flow should
name the order of the phases or sections, the one question each section will
answer, the small set of figures that will carry the argument, and the final
current position/next-step section. Ask whether that flow matches before
starting the full evidence pass.

Wait for approval. If the user changes the flow, revise the flow rather than
drafting the report around an unapproved structure. The scope gate is complete
only when the report boundary, audience/purpose, rough spine, and approval are
explicit.

## Build a compact evidence spine

After the flow is approved:

1. Start from [`Project/index.md`](../../../Project/index.md). For each selected
   phase, read its phase-root `CONTEXT.md` first, then only the latest relevant
   `setup.md`, `results.md`, figure index, or parent record needed to answer the
   report question. Use `show-me-your-work` when a long campaign needs a
   concise evidence reconstruction.
2. Build a private evidence spine with one row per report section:
   `question → experiments included → observed result → justified conclusion
   → claim limit → next decision → figure(s)`. Keep exact paths and evidence
   status in the working notes so the report does not rely on memory.
3. Select the smallest useful evidence set. Prefer one direct-answer figure
   and, only when it adds a distinct message, one mechanism or numerical-
   adequacy figure per phase. Existing quantitative plots come first. Do not
   add a plot merely because it exists.
4. Separate `Reported`, `Observed`, `Inferred`, `Assumed`, and `Missing Info`
   where the distinction matters. A completed run is not automatically a
   converged or qualified result; preserve the source record's lifecycle and
   claim boundary.

The evidence spine is complete when every planned section has a source-backed
answer, a bounded conclusion, a next step, and either an existing figure, an
approved figure brief, or an explicit placeholder explaining what is missing.

## Use the phase story consistently

For each phase or campaign, write a compact version of this sequence:

1. **What we wanted to test** — the decision or uncertainty that mattered.
2. **What we tested and why** — the few experiments or comparison branches
   that directly addressed it; omit chronology that does not change the
   interpretation.
3. **What we observed** — neutral, figure-linked behaviour such as rise,
   drift, oscillation, saturation, redistribution, or failure.
4. **What follows** — the strongest conclusion supported by the evidence and
   the sentence that limits overclaiming.
5. **What we are doing next** — the next question or one-change-at-a-time
   decision, not an unapproved experiment matrix.

Open with a one-minute project story when the report spans several phases.
Close with the current position, unresolved evidence gaps, and next steps. A
useful meeting report lets the author point to a figure and say: “we saw this;
therefore we tried that; this happened; now we are testing the next question.”

## Figures are arguments, not decoration

For every selected figure, write a report-ready title, a one-sentence caption,
the exact source and scope, and the point the presenter should be able to say
while pointing at it. Keep the point-to-say faithful to what the figure can
actually show. A spatial contour can show distribution; it cannot by itself
prove phase-resolved mass transfer or a stable solution.

Use the independent [`create-figure`](../create-figure/SKILL.md) skill when a
new Fluent contour, vector scene, plane, or geometry-aware spatial comparison
is needed. Give it the approved scientific message and exact case/checkpoint
choices; it owns the Fluent postprocessing workflow. Do not duplicate its
plane-setting or export procedure here.

When a required figure is not yet available, insert a useful placeholder rather
than inventing an image. A good placeholder states:

- the figure ID and the question it must answer;
- the exact case/checkpoint or comparison still to be selected;
- the plane, field, or plot family expected;
- the evidence status (`planned`, `partial`, `unavailable`, or `requires
  rerun`); and
- the point the presenter should be able to make once it exists.

## Assemble the deliverable

Create meeting or report artifacts under the relevant `Project/meetings/` or
project-local report directory. Keep the Markdown source readable and link
figures with project-relative paths. Do not edit `raw/` files or put current
scientific truth in a second report log.

When the user requests HTML or final visual presentation, read
[`REPORT-DESIGN.md`](REPORT-DESIGN.md) before assembling it. Render the HTML
beside the Markdown source, preserve local image links or embed them when that
is appropriate, and inspect the rendered output at normal reading size. Check
hierarchy, figure legibility, caption proximity, whitespace, table density,
broken links, and whether the page feels like a technical report rather than a
dashboard.

Use the report's visual language to make distinctions that matter—comparison
series, thresholds, failures, or selected states. Keep decorative colour,
heavy cards, tiny text, and redundant plots out of the main flow.

## Completion criteria

The report-writing task is complete only when:

- the scope and rough flow were approved, unless the user explicitly asked for
  a draft without an approval gate;
- each section has a source-backed question, observation, conclusion, claim
  limit, and next step;
- each included figure has a readable title/caption, exact provenance, and a
  clear point-to-say;
- missing figures are honest placeholders rather than implied evidence;
- existing plots and internal links resolve from the report location; and
- the requested output has been rendered and visually reviewed, with the
  final Markdown/HTML paths handed back to the user.
