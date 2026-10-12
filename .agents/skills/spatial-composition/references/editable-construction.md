# Editable construction

Choose the requested authoring platform first. Use its available native or
programmatic tools; do not move the work to a different platform merely because
image generation is easier. Inspect tool capabilities before promising edits or
exports. A custom control panel is optional when it makes repeated comparison
cheaper, inspired by [S3](sources.md#s3), not a required software project.

## Construct a scene, not a single picture

Give major objects stable names and retain their sources. Group an image with
its caption and related callouts, but allow the background and subject to be
edited independently. A simple layer table in the existing design definition is
enough; introduce a machine-readable scene graph only when the build uses it.

Useful relationships are `behind`, `overlaps`, `inside`, `aligned-with`, and
`label-for`. Also record regions that must remain unobstructed. These relationships
matter more than arbitrary layer numbers. A globally layered composition needs a
consistent draw order; a local interleaving effect may require explicit masks or
split objects rather than contradictory stacking instructions.

Typical adjustable properties are subject position/scale, background crop,
local contrast masks, group spacing, and annotation anchors. Expose only the
controls needed for the current comparison. Keep the accepted layout as a baseline.

## Choose the implementation by medium

| Medium | Editable construction | Verify in the actual output |
|---|---|---|
| Web / HTML poster | Separate elements and semantic groups; layout rules for content, positioned decorative layers only where justified. | Responsive or fixed-page behaviour, asset loading, text overflow, stacking and print rendering. |
| SVG | Named groups, preserved text where practical, linked/embedded assets, explicit masks and clipping. | Font rendering, clipping, asset portability, and export fidelity. |
| Slides / design canvas | Native text and shapes, separate image objects, named groups, and the platform's layer order. | Source-file editability and final-size text/figure readability. |
| 3D subject illustration | Preserve the model/camera when available and export a separate subject asset. | Geometry, camera/crop, transparency and lighting; keep page typography outside the render. |

In CSS, stacking contexts constrain how descendants stack against other groups;
a high child `z-index` does not escape its parent context. Inspect actual parent
contexts before raising values. Properties such as opacity or transforms can
create contexts ([S11](sources.md#s11)). Decorative overlays must not block input
or keyboard focus. Put semantic reading order in the document structure, not
merely in visual coordinates.

## Asset integrity

Classify each placed image as **evidence**, **schematic**, or **atmosphere**.

| Class | Treatment |
|---|---|
| Evidence | Keep the source intact and retain units, scales, legends, case identity and relevant boundaries. Regenerate from the evidence owner when substantive changes are needed. |
| Schematic | Simplify to explain structure; make its illustrative status clear. Check geometry and flow arrows against supplied references. |
| Atmosphere | Use a separately named derivative for crop, masking or tonal treatment. Identify it as decorative rather than a readable quantitative result. |

An image-generation tool may help make a missing schematic or atmospheric asset.
It must not invent quantitative CFD evidence. Keep generated figures separate
from live text and charts. Do not generate the entire poster and present its
pixels as editable layers. A flattened preview is acceptable alongside the
editable source, not instead of it.

Never paint over an inconvenient scientific value, recolour only part of a contour
to imply another result, or crop away a relevant failure. Protect original files
and all `raw/` records. Do not redistribute fonts or third-party reference assets
without permission; use references for analysis rather than copying their artwork.

## Output fidelity

Keep essential text clear of detailed imagery. For digital text, use applicable
contrast requirements ([S12](sources.md#s12)); assess the local composite background,
not just a palette swatch. Digital contrast checks do not certify print legibility.

For a print poster, inspect the export at the requested physical dimensions,
including placed figure labels and image resolution. Check printer-specific bleed,
fonts, colour handling, and other requirements only against the actual brief.
Use the available PDF/export workflow when producing that deliverable. Keep the
editable master even when the final submission format is flattened.
