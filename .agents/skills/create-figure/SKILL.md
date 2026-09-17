---
name: create-figure
description: "Create geometry-aware, report-ready native Fluent figures from saved CFD checkpoints using MCP-grounded graphics operations, matched visual settings and explicit provenance."
---

# Create Figure

Create a figure that answers a scientific question, not a generic screenshot.
Follow [MCP integration](../fluent-live-inspection/mcp-integration.md). Report
layout belongs to `report-writing`; this skill owns native Fluent graphics.

## Native-output boundary

Deliver native Fluent contours, vectors, scenes and picture exports from the
verified case/data checkpoint. Local tools may inspect an export for QA but must
not alter its scientific pixels or substitute HTML/SVG/Matplotlib/PIL/ImageGen
or another drawing/compositing pipeline. For comparisons export separate native
images with matched settings, or use a supported native Fluent scene.

Loading a different pair and creating graphics objects changes workspace state.
Use an owned, non-conflicting session, preserving valuable state before replacing
it. Never solve, initialize, patch, alter physical/numerical setup or save over
the source pair merely to produce a figure.

## 1. Establish a figure brief

Read only the relevant Project index, phase context, experiment setup/results
and geometry-information record. Resolve the scientific question, audience/size,
exact checkpoint(s), geometry/coordinates/units, surface/plane, fields, comparison
basis, camera/range and claim limit. Ask only for materially missing choices;
proceed when the brief is already explicit and approved.

Verify both case and data, checkpoint progress/status and provenance. A server
alias or a convenient loaded case is not identity. Label initialized, finite
screen, last-valid, divergent diagnostic and qualified states distinctly.

For a patched experiment, preserve/show the nearest saved post-patch pair alongside
its evolved/final or last-valid state when explaining the response. Match plane,
camera, fields, ranges, colors and vector scale; label both progress states. If
post-patch evidence is absent, record the gap rather than substituting a final.

## 2. Discover and load through MCP

Use `session_status` and the assigned process's argument-free `connect` only when
needed. Ground load/surface/graphics/export paths using `find_api`, `get_help`,
`describe_path`, named-object/template tools and `get_state`. Discover available
fields with `list_fields`; use `mesh_quality` for mesh diagnostics, not a custom
crawler. Geometry measurements still need actual scoped queries, not tool names.

Validate/run the approved pair load, reacquire objects, and verify identity and
field/domain mapping. Semantic/prerequisite uncertainty goes to
`fluent-manual-researcher`. Existing postprocessing code supplies domain ideas,
not a direct-PyFluent default. Retained field-data/file-transfer helpers require a
named capability gap and review under the shared contract.

## 3. Design surfaces and fields around the question

Use verified coordinates, not assumed centerlines. Typical center cuts are XY
at known Z or YZ at known X; horizontal cuts require a verified elevation. An
actual inlet/outlet boundary is preferable when that boundary is the question.
Record method, origin/coordinate, normal/orientation and units. Expose conflicts
between supplied geometry and mesh evidence before exporting.

Use the verified liquid-phase fraction for liquid location; pressure/velocity
for routing; turbulence fields only for the corresponding numerical question.
Mixture density is not automatically a liquid level. A source contour shows a
prescription, not delivered liquid; pair it with quantitative evidence when needed.

Each image is **contour-only** or **vector-only** unless an explicitly combined
scene is requested. Contours contain no vector object. Vector-only images show
the complete field (`skip=0` or the discovered equivalent), with recorded fixed
arrow scale and in-plane/3D policy. For small arrows, use a declared vector-scalar
color map, an unset color override and a readable color bar. Fixed-length arrows
are useful when direction is the message; do not imply magnitude through them.

## 4. Configure, read back and export

Create only the required named temporary surfaces/graphics objects through
validated MCP snippets. Reacquire after loads/creation. Clear only the named
objects/display needed; avoid broad collection clears or stale prior-case graphics.

For each exact surface and checkpoint, discover actual field minimum/maximum
using the grounded graphics computation/readback. A reviewed field-data query
may fill an explicit capability gap. Keep per-case observations separate from
display limits. A field list is not a range measurement.

For matched figures use common explicit scalar limits, color map, threshold,
linear/log policy, camera, plane and vector scale. Disable global/automatic range
for final comparative exports and read back limits. Known physical bounds can
set a shared range (for example verified phase fraction on 0–1); otherwise use
a justified outward-rounded union. Do not silently clip outliers. A deliberately
auto-ranged single non-comparative scene may be used only with its actual limits
and rationale recorded; it is not a comparable panel by default.

Set camera position, target and up-vector for a square-on plane; use orthographic
projection when appropriate. After auto-scale, zoom/tighten the view so the
scientific region fills the frame without clipping. Inspect an exported candidate,
adjust in Fluent and re-export until orientation, framing and labels are clear.
Preserve these settings across compared states.

Set native picture resolution explicitly, disable window-resolution inheritance,
and normally export at least 2,000 pixels on the long edge (preferably about
2,400 × 1,800 for reports). Resolution does not fix poor framing. Keep units,
legends, axes and short meaningful graphics names readable; use light mesh/zone
outlines only when they clarify location.

Display/save through grounded `validate_code` → `run_code` operations. Use
`screenshot` only when it captures the intended native view at the required
quality and provenance; an arbitrary workspace screenshot is not the deliverable.
Verify the actual file format and output path; file transfer remains a reviewed
host operation when needed. No local recomposition or pixel repair.

## 5. Visual and evidence QA

Store report-facing images in the relevant experiment/stage `figures/` folder.
A meeting report may use a copy while retaining original source identity. Never
write into `raw/`. A finished figure requires:

- exact pair/checkpoint and geometry/phase/surface provenance;
- required post-patch/evolved comparison or an explicit missing-evidence note;
- valid remote/local image files written by Fluent;
- intended fields, units, observed/display ranges and vector sampling/scale;
- matched comparison settings and no stale graphics;
- readable, unclipped subject, labels, legends, arrows and color bars at report size;
- a caption that states the observation and what it cannot establish.

Return paths, core/responsive/supporting/partial status, checkpoint and geometry,
field/surface/range/camera/export settings, observed message and claim limit.
Keep partial outputs labelled. Return path/version, dependency, capability or
missing-choice blockers without substituting another case, field or checkpoint.
