# Skill evaluation scenarios

Use when creating or changing this skill. These are behavioural test briefs, not
completed tests or proof that the skill improves model performance. Supply actual
assets/screenshots to test visual judgement. Text-only review tests routing and
reasoning but cannot pass visual acceptance.

For a meaningful comparison, run the same task with and without the skill using
the same assets, model, tools and budget. Compare editable artifacts and previews,
not the confidence or length of their explanations. Blind the reviewer to the
version where practical. Repeat across different briefs before generalising.

## Scenarios

| Scenario and prompt | Expected behaviour | Failure signal |
|---|---|---|
| Busy background: keep this colourful field, but make the separator stand out. | Diagnose local competition; retain background character while testing silhouette separation. | Fades everything, adds effects everywhere, or changes the source data. |
| Foreground labels: keep these labels above the image but visually secondary. | Separate draw order from attention; preserve readable labels and correct targets. | Makes all foreground content the loudest or lowers its contrast until unreadable. |
| Visual-only P4P: redesign the composition; keep all text, figures and results. | Reads the current artifact and newer brief, preserves scientific content, creates editable layers. | Rewrites claims, starts new simulations, or delivers one generated poster image. |
| Three concepts only: compare spatial arrangements of these assets. | Same assets/content; materially different position, crop, grouping or overlap; stop at concepts. | Three palette swaps, new evidence selections, or an unrequested finished poster. |
| Quiet comparison interface: make this dashboard clearer without distracting depth. | Preserves comparisons and scan order; uses only useful grouping/elevation. | Introduces a giant hero, tilted charts, or decorative parallax. |
| Conflicting brief: old spec says flat; current request asks for a layered field background. | Changes that visual axis while preserving unaffected dimensions, data and other constraints. | Treats the old style as immutable or discards every existing requirement. |
| No renderer: improve the provided layout with available text-only tools. | Produces a useful plan or editable draft and marks visual inspection unverified. | Claims that screenshots were inspected or that the hierarchy passed. |

## Inspect the delivered result

Apply [render and critique](../references/render-and-critique.md) at the three
viewing scales. Record each scenario as pass, fail, or unverified, with the artifact
and a concrete observation. Separately check protected content and source integrity,
editable objects, accurate callout targets, and adherence to the requested mode.
A polished appearance cannot compensate for altered evidence or lost editability.

## Structural checks

Check `SKILL.md` frontmatter, the name/description, agent metadata, internal links,
and invocation-map registration. Confirm that references are reached by clear
conditions and project-specific decisions stay with the project. These checks
verify packaging only. Record visual evaluations separately and do not report
unrun scenarios as passes.
