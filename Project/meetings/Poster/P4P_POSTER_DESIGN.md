# P4P research poster — Design definition v1

**Direction:** Geothermal flow, presented as an engineering exhibit.

**Status:** Working design baseline. Palette, colour roles, type family and visual rules are fixed for this version. Final poster dimensions, orientation, institutional requirements and selected results remain unresolved. Physical sizes below assume an A0 poster; the landscape arrangement is provisional.

This is a poster-specific adaptation of Google's DESIGN.md and Stitch design-system approach, not a Google palette or a claim of compliance with Google's web-oriented schema. It defines the design; it is not the poster.

## Overview

Imagine a large explanatory panel in an engineering museum: a precise separator cutaway, a few readable comparisons, and short statements explaining what each modelling decision taught us. The drawing and evidence carry the visual interest. The page itself stays quiet.

The narrative is: **existing model → improve mass conservation → investigate necessary physics → test design choices**. Treat this as a research sequence, not a claim that every later model is better. Attribute Purnanto's contribution where the starting model is introduced. Distinguish published assumptions from problems encountered in our own implementation.

Optimisation is not yet completed. Give it a small, explicitly planned-work section, not a fabricated results panel. Model development should receive the most space.

The presentation should feel precise and approachable, not like a software dashboard, a dark blueprint or a promotional energy brochure.

## Colours

Exact values below are the working sRGB palette. Descriptive names explain their character; roles determine where they may be used. Values were selected for this poster, not copied from Google or generated with Material Theme Builder.

### Page palette

| Token | Name | Hex | Use |
|---|---|---|---|
| `canvas` | Paper white | `#FFFFFF` | Page and plot backgrounds; dominant surface. |
| `ink` | Deep engineering navy | `#17324D` | Title, headings, body text, essential geometry and key-message emphasis. |
| `text-secondary` | Steel grey | `#52616B` | Supporting captions, references, metadata and secondary labels. |
| `surface` | Mineral mist | `#F3F6F7` | Occasional neutral callout, including planned work. Not a fill for every section. |
| `rule` | Pale steel | `#CBD5DB` | Non-essential dividers and light gridlines. Never essential text or a sole scientific boundary. |

### Physical-phase palette

| Token | Name | Hex | Use |
|---|---|---|---|
| `liquid` | Liquid teal | `#007F86` | Liquid/brine arrows, labels and phase-series strokes. |
| `liquid-surface` | Liquid mist | `#E5F3F2` | Liquid-region illustration fill or a specifically liquid-related annotation. |
| `steam` | Steam copper | `#AF541F` | Steam/vapour arrows, labels and phase-series strokes. |
| `steam-surface` | Steam haze | `#FBEDE4` | Steam-region illustration fill or a specifically steam-related annotation. |

Navy provides hierarchy; teal and copper identify the two phases. These are not temperature colours. Label the phase names explicitly. Do not give background, methods, results and future work separate colours. Do not use teal as a generic success colour or copper as a warning/planned-work colour.

The light phase fills are schematic, not quantitative volume-fraction contours. Quantitative fields need a separate, labelled colour scale. A scalar field may use colours outside this categorical palette when required to encode its values; it must not be recoloured merely to match the page.

**Approved text pairings:** navy or steel grey on white/mineral mist; navy on either pale phase fill; teal or copper for short phase labels on white. Do not use teal text on liquid mist or copper text on steam haze. Keep paragraphs navy even when they discuss a particular phase.

Calculated sRGB contrast ratios against white are approximately 13.13:1 for navy, 6.40:1 for steel grey, 4.79:1 for teal and 5.11:1 for copper. These use the WCAG relative-luminance formula. We adopt 4.5:1 as a conservative digital text check, not as certification of print legibility. Proof the final colours on the intended paper and output process.

Teal and copper have similar luminance. They are not a sufficient grayscale distinction: use direct labels plus marker shapes or line styles, and navy outlines between touching schematic regions. Colour must not be the only means of identifying data.

## Typography

Use **Arial Regular and Arial Bold** throughout. Use a proper mathematical font only within equations where needed. Do not add a decorative display font or narrow lettering to make content fit.

| Role | Working size at A0 | Treatment |
|---|---:|---|
| Title | 96 pt | Bold navy; preferably one or two short lines. |
| Section heading | 60 pt | Bold navy; sentence case. |
| Subheading / key takeaway | 48 pt | Bold navy. |
| Body / figure captions / axes / legends | 36 pt | Regular; bold only for a short emphasis. |
| Authors / contact / references | 36 pt | Regular; supporting information may use steel grey. |

Left-align text. Start body line spacing at 1.15. Use short paragraphs and sentence-case headings. Reduce content before reducing type. Check figure text at its final placed size, not just in the graph-export window. Main narrative target: roughly 350–400 words, including essential captions, within the supplied 300–500-word guidance.

## Layout

Use a development-led layout with a large, accurate separator drawing and central evidence. Do not force the four research stages into four equal columns.

For a provisional landscape layout, divide body width after gutters approximately as follows:

| Region | Share | Contents |
|---|---:|---|
| Left | 25% | Background, research question, Purnanto starting point and separator schematic. |
| Centre | 45% | Compact staged method, mass-conservation evidence and selected physical-model comparisons. |
| Right | 30% | Interpretation, limitations, conclusions and a smaller planned design-exploration section. |

Title, authors and a one-sentence research purpose sit above the body on white. References, acknowledgements and contact information sit below. No large dark masthead by default. Keep logos secondary and preserve their supplied official treatment.

Working A0 spacing: 30 mm outer margins, 20 mm column gutters, and a 5 mm spacing unit. Use 5 mm between a figure and its caption, 10 mm between a heading and its content, and 20–30 mm between separate content groups. Values may be reflowed after the required format is confirmed; do not simply shrink the poster to fit another size.

Put each interpretation beside or below its evidence. Reserve around 10–15% of body area for planned optimisation at the current stage. Give each major group visible breathing room. Leave evidence selection and the exact title open until results are chosen.

## Elevation & Depth

Flat page graphics. No drop shadows, glows, decorative gradients or background textures. A scientific 3D rendering may retain useful depth cues; this is different from adding fake depth to panels.

## Shapes

Use square-cornered panels and simple thin rules. Most sections have no enclosing box. Use a neutral tinted panel only when it helps separate an important takeaway or planned work. Curves should come from the separator geometry, real flow paths or measured plots, not ornamental waves.

## Components

**Separator schematic.** Use the actual research geometry and correct inlet/outlet positions. Navy defines vessel geometry; teal and copper show labelled phase pathways. Label conceptual/expected behaviour as schematic rather than presenting it as a simulation result.

**Result figure.** Give each figure one question, a short heading, readable units and a one-sentence interpretation. Use white plot backgrounds, navy/grey axes and limited gridlines. Working A0 strokes: 3 pt for data and 1.5 pt for axes; adjust only after full-size inspection.

**Comparisons.** Preserve phase colours across cases. Distinguish cases with line styles, markers, direct case labels or separate matched panels. For phase-neutral metrics such as total mass imbalance, compare a steel-grey dashed baseline with a navy solid current case and label both. These styles identify cases, not whether they passed a validation test. Use matching views and scales where the comparison requires them; explain any necessary differences.

**Main takeaway.** One short, prominent navy statement on white or mineral mist. No generic trophy, lightbulb, target or check-mark decoration. The statement must describe evidence, not imply that adding complexity proves accuracy.

**Planned work.** A smaller neutral outlined panel explicitly labelled “Planned design exploration”. Use questions or candidate sketches, not invented output plots. Distinguish proposed changes to the separator from changes to its CFD representation. Replace this component with evidence only when tests have actually been completed.

## Do's and Don'ts

**Do** keep colours attached to their defined roles, group figures with explanations, use accurate geometry and real data, and make the model-development evidence the centre of attention.

**Do not** add a colour for every research stage, make continuity look like curve smoothing, present model complexity as validation, show invented optimisation results, or hide unreadable material in a tiny footer.

Before final production, confirm size/orientation and mandatory template/branding; check all text at final size; inspect grayscale/colour-vision alternatives; proof the colours and scan any real QR code. Final research claims, results and figure assets require their own evidence review.

### Source basis

The values and poster-specific decisions above are original design choices. The sources inform the method and checks, not scientific results or the chosen hex values.

Google Labs, DESIGN.md: exact design values paired with explanatory prose. `https://github.com/google-labs-code/design.md`

Google Labs, DESIGN.md Philosophy: use a concrete visual reference and explain intent. `https://github.com/google-labs-code/design.md/blob/main/PHILOSOPHY.md`

Google Labs, Stitch design-md skill: describe atmosphere, colour names/values/roles, typography, components and layout. `https://github.com/google-labs-code/stitch-skills/blob/main/plugins/stitch-utilities/skills/design-md/SKILL.md`

Android Developers, Material Design 3 in Compose: pair foreground and background roles deliberately. `https://developer.android.com/develop/ui/compose/designsystems/material3`

Nilushika Thambugala, supplied *How to make an effective poster presentation*, `Speech_Nilushika2023.pdf`: concise content (p. 7), layout (p. 10), light background (p. 11), restrained palette (pp. 12–13), whitespace (p. 14), figure labelling (p. 17), A0 type guidance (p. 19). The user's pasted guidance sets 90 pt title, 60 pt headings and 36 pt text starting minima; the proposed scale meets those values.

W3C, WCAG 2.2 Understanding 1.4.3 and 1.4.1: digital contrast and non-colour identification checks. `https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html` and `https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html`
