# Render and critique

Use this when building or reviewing an actual composition. This protocol is a
proposed evaluation workflow, not eye-tracking evidence or a guarantee of taste.
The distinction between visual critique and technical audit is informed by
[S4](sources.md#s4); rendered inspection is also supported by
[S2](sources.md#s2).

## Establish a baseline

Save or identify the current editable version and its preview. Record only the
viewing conditions needed to reproduce the judgement: output dimensions, viewport
or print scale, loaded assets, and relevant interaction state. Wait for fonts and
images to load before judging. A broken asset is a rendering defect, not a style.

For a critique-only request, inspect and recommend; do not edit without authority.
For a concept-only request, label wireframes as proposals rather than tested work.

## Read back before rationalising

Inspect the render first. A separate visual reviewer, when available, should see
the artifact and audience/task but not the proposed attention ranking or designer's
rationale. Ask for observations, then reveal the plan for comparison. With only
one agent, make an observation-first pass and acknowledge that it is self-review.

Use this prompt:

> Describe what the image makes prominent. Name the first three things you notice,
> what appears in front of what, the groups you perceive, and the region hardest to
> read. Identify the visible cues and locations. Then suggest the smallest change
> that would improve the main task. Do not infer quality from the source code.

The response is a model's visual judgement, not a measured human gaze sequence.

## Inspect at three scales

| View | Inspect | Required outcome |
|---|---|---|
| Thumbnail / distant | Large masses, anchor, silhouette, competing bright or busy regions. | The intended entry point is apparent; support does not accidentally dominate. |
| Whole artifact | Grouping, reading path, negative space, cropping, overlap, title-to-body relationship. | The structure is understandable without the design explanation. |
| Close reading | Captions, axes, legends, callout targets, transparency, clipping, small type and rules. | Meaning remains intact and essential details are readable. |

Use grayscale or a lightly blurred copy to diagnose masses when useful. These
views cannot replace the full-colour and full-detail checks. For print, inspect
at the intended placed size; a screenshot cannot establish paper/ink quality.

For web layouts, also inspect supported viewport sizes and active states using
browser/computer-use tools where available. Check keyboard navigation, focus,
links, overflow, and reduced-motion behaviour when relevant. A visual screenshot
alone does not establish accessibility or working interactions.

## Repair one relationship

Use a short record:

```text
Observed: the bright panel at upper right is more prominent than the main subject.
Target: subject first; panel readable on second inspection.
Change: reduce panel/background contrast; keep the plot and its labels unchanged.
Preserve: subject scale, approved colours, data, title, and other groups.
Verify: compare the whole view and the panel crop with the baseline.
Outcome: improved / unchanged / regressed / not verified, with a visible reason.
```

Choose the most important mismatch. Try a local reduction of competition, crop
adjustment, spacing change, or stronger boundary before adding global effects.
Re-render the whole composition as well as the edited area. Keep the repair only
if the intended relation improves without a new readability or integrity problem.
If several repairs fail, revisit the arrangement rather than accumulating patches.

## Finish with evidence, not a beauty score

Record a compact pass/fail/unverified table for hierarchy, grouping, legibility,
content integrity, editability, and the relevant medium-specific checks. Cite the
preview, screenshot, or inspected state for each conclusion. Mark human-dependent
print proofing separately. Do not invent numerical aesthetic scores.

Structural checks may find missing assets, broken links, clipping, or invalid
metadata. They cannot prove that something looks good. Without visual access,
provide the best editable draft or plan, identify the missing inspection, and
avoid claiming visual verification.

Keep critique records alongside the current artifact only when useful for the
next revision. Update the accepted design definition, not a growing duplicate diary.
