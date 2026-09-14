---
name: create-figure
description: "Create geometry-aware, report-ready scientific figures from saved CFD case/data checkpoints. Use when a contour, vector scene, plane, spatial comparison, or other Fluent postprocessing figure must answer a defined scientific question."
---

# Create Figure

Create a figure that answers a scientific question, not a generic screenshot of
the current Fluent session. This skill is independent of `report-writing` and
can be used for experiment records, analysis handoffs, reviews, or meeting
reports.

The normal route is:

```text
figure brief → geometry/source confirmation → plane/field design
→ Fluent postprocessing → export → visual QA → provenance handoff
```

Do not run a solver or change a scientific setup as part of figure creation.
Loading an explicit saved case/data pair and creating temporary postprocessing
objects is a postprocessing action; preserve the source case/data pair and
save only derived figure artifacts.

## Native Fluent output boundary

Every deliverable figure produced by this skill must be a native Fluent
graphics export from the verified case/data checkpoint. Use Fluent contours,
vectors, scenes, views, annotations, and `picture.save_picture` (or the
version-matched equivalent) to create the image.

Do not create or repair a figure with HTML, CSS, SVG, Matplotlib, PIL,
ImageMagick, a notebook, ImageGen, or another local drawing/compositing
pipeline. Do not replace a missing Fluent contour with a schematic, field-data
card, or hand-drawn geometry diagram. Local tools may inspect an exported image
for QA, but must not alter its scientific pixels or create a substitute
figure.

This skill does not render HTML or author the meeting document; document
layout belongs to `report-writing`. If a comparison needs multiple panels,
make the panels in Fluent when the version supports it, or export separate
native Fluent images with the same camera and visual settings. Do not assemble
them into a new image outside Fluent.

## 1. Establish the figure brief

First determine what the viewer must learn from the figure. If the context is
not already explicit, ask a few focused questions rather than guessing. Ask
only the missing questions, normally no more than three at a time:

1. **Story:** What conclusion or comparison should the figure support? Is the
   primary quantity phase distribution, pressure, velocity routing, turbulence
   behaviour, an outlet response, or something else?
2. **Geometry:** Which geometry is being shown, and which geometry-information
   record defines its coordinates, zones, cutoffs, inlets, outlets, or special
   regions? If the user has not created that record yet, use the already-known
   project geometry only where it is genuinely established and label any
   remaining coordinate or face-location assumption.
3. **Source:** Which exact case/data pair and checkpoint should be loaded? If
   several cases are relevant, which ones should be compared and at what
   matched checkpoint or valid finite state?

Also resolve any material presentation choice that remains open: one figure or
a multi-panel comparison, full geometry or a lower-region zoom, central cut or
inlet/outlet view, scalar only or scalar plus vectors, and the intended report
size. If the user already supplied these choices, summarize them instead of
re-asking.

Before mutating a Fluent session, state the proposed brief in one compact
block:

```text
Question:
Source case/data and checkpoint(s):
Geometry and coordinate units:
Surface(s)/plane(s):
Primary field and supporting field(s):
Comparison basis:
Camera and visual scale:
Expected message and claim limit:
```

Get confirmation when a material choice is still ambiguous. If the brief is
already explicit and approved in the user request or calling workflow,
proceed without an unnecessary second approval turn.

## 2. Prove geometry and source identity

Read the relevant `Project/index.md`, phase `CONTEXT.md`, and the specific
experiment `setup.md`/`results.md` or report brief needed for the figure. Read
the user-provided geometry-information file when it exists. Do not preload old
chronology or unrelated knowledge trees.

Resolve the exact case/data pair from the recorded experiment paths. A Fluent
`server_id` selects a connection endpoint; it is not case provenance. Verify
both files on the host, verify that the data filename pairs with the case where
the format requires it, and record the checkpoint's status: initialized,
finite discovery state, last valid state, divergent endpoint, or qualified
state. Prefer the declared matched state for comparisons and label a
post-failure snapshot as diagnostic.

If the experiment includes any patching operation—such as patching a phase,
volume fraction, species field, temperature, pressure, or selected cell
register—treat the patched state as required visual evidence. Identify and
preserve the nearest saved case/data pair immediately after patching, then
show it alongside the later/final or diagnostic checkpoint when the figure is
used to explain the experiment. Do not use only the final iteration checkpoint
for a patched experiment: that can hide the initial condition that caused the
observed response. Label the two states explicitly as `post-patch` and
`evolved/final` (or `post-patch` and `last valid`), record their iteration/time
and patch/register provenance, and use the same plane, camera, field, range,
colour map, and vector scale when they are compared visually. If no paired
post-patch case/data state was saved, report that evidence gap instead of
silently substituting the final checkpoint.

If the pair or geometry cannot be proven, stop and report the missing identity
or ask the user to choose between the exact recorded candidates. Do not select
a case merely because it happens to be loaded on a server.

For Fluent automation, use the repository's connection and postprocessing
helpers when available. Read the local PyAnsys guide and the native-run
autosave guidance before working with a native Fluent session. Use live
inspection to resolve uncertain object names, allowed values, coordinate
units, field names, or prerequisites; escalate to the official version-matched
Fluent manual when the live tree cannot resolve them. Do not guess a deep
Fluent setting or switch to a TUI/journal merely because the Settings API is
inconvenient.

## 3. Design surfaces around the question

In a 3D Fluent case, create or select explicit surfaces before displaying
contours or vectors. Use the geometry record and live zone readback to choose
the surface; do not treat a convenient plane as a physical inlet or outlet
unless its location is verified.

Common starting patterns are:

- `X–Y` at `Z = 0` and `Y–Z` at `X = 0` for orthogonal centre cuts through a
  vessel;
- `X–Z` at a verified elevation for a horizontal inlet/outlet or internal
  slice;
- a boundary face or zone surface when the question is specifically about
  inlet/outlet flow;
- a lower-region cut plus a zone outline/overlay when the question concerns a
  pool, measurement volume, or absorber region.

Record the plane method, coordinate, normal/orientation, and units. For an
  inlet or outlet, prefer the actual boundary surface when available. If a
  user-supplied elevation and the mesh/zone geometry disagree, expose the
  mismatch before exporting a figure.

Choose fields by the claim they support:

- use phase-2 volume fraction as the primary liquid-location contour when the
  question is where the liquid is;
- use phase-specific density as a secondary view only when the phase identity
  and density contrast are clear;
- use pressure, velocity magnitude, or in-plane velocity vectors for routing
  and local flow behaviour;
- use turbulent viscosity/viscosity ratio, `k`, or `epsilon` only when the
  numerical/model-treatment question calls for it.

Mixture density is not automatically a liquid-level measurement. A source
  contour shows where a source was prescribed; it does not prove that liquid
  reached that region. Connect spatial evidence to phase-resolved flux,
  selected-volume mass, or another quantitative measure when the claim needs
  that connection.

Keep the figure visual grammar unambiguous: each deliverable must be either
**contour-only** or **vector-only** unless the user explicitly asks for a
combined Fluent scene. A contour-only figure must not contain a vector object.
For a vector-only figure, display the complete vector field (`skip=0`, or the
version-matched Fluent equivalent for no subsampling) and record the fixed
arrow scale, colour, and in-plane/3D policy. Do not use a sparse vector overlay
to imply that all vectors are shown, and do not combine a dense vector field
with a scalar contour merely because both objects are available.

When the vectors are visually small, colour them in Fluent by a declared
vector scalar such as velocity magnitude. Keep the arrows fixed-length if
direction is still the primary message, leave the vector colour override
unset so the Fluent colour map is used, and show the colour bar. For matched
comparisons, disable global/automatic range selection and apply one explicit
shared range with units to every case; record the field, limits, colour map,
and whether the scale is linear or logarithmic. A colourless vector field is
not an acceptable default when the arrows cannot be distinguished at report
size.

## 4. Configure a comparable visual

For each figure, set the visual parameters deliberately and read them back:

- use a common plane, camera, scalar range, colour map, and vector scale for
  cases being compared;
- keep units, field names, legends, and thresholds visible and readable;
- use in-plane vectors on a 2D cut and fixed-length arrows when magnitude is
  not the message. In a vector-only figure, show all vectors (`skip=0`) and
  choose the fixed arrow scale carefully so the field remains readable. In a
  contour-only figure, do not add vectors;
- use a light mesh or zone outline only when it provides spatial context;
- bring the separator closer in the Fluent view. For a planar figure, orient
  the camera perpendicular to the plane normal by explicitly setting the
  camera position, target, and up-vector; use orthographic projection when it
  improves geometric readability. After `auto_scale`, apply an explicit zoom
  or tighter view scale so the relevant vessel region occupies most of the
  frame. Do not accept Fluent's oblique default view when a square-on plane
  view is the intended evidence, or a tall, narrow separator floating in a
  large empty canvas when the question concerns a lower zone or local route;
- treat camera selection as iterative. Export a native Fluent candidate,
  inspect its orientation, crop, margins, and label readability, then adjust
  the Fluent camera and re-export until the plane is square-on and the subject
  is close without clipping the scientific region or frame context. Record
  the final camera position, target, up-vector, projection, and post-
  `auto_scale` zoom;
- export at a deliberately high resolution, normally at least `2000` pixels on
  the long edge and preferably around `2400 × 1800` pixels for a report or
  meeting figure. Set the picture resolution explicitly and disable
  window-resolution inheritance; do not inherit an arbitrary interactive-window
  resolution. Higher resolution does not compensate for a poor crop, so make
  the important region large enough before exporting;
- use a short meaningful graphics name so Fluent legends remain legible; hide
  irrelevant UI text while retaining scientific axes, units, and colour bars.

### Resolution and scalar-range continuity

Treat resolution, scalar limits, and vector scaling as part of the scientific
presentation rather than as Fluent defaults:

- Do not enable Fluent's `global range` for report figures. First discover the
  field range on the exact displayed surface for every selected case. In the
  live Fluent API, prefer the version-matched range computation/readback on a
  temporary contour or vector object (for example, set `global_range=False`,
  leave `auto_range=True` only during discovery, run the range `compute`
  command, and read back `minimum`/`maximum`). If that surface-level query is
  unavailable, use the version-matched field-data min/max query and record that
  fallback explicitly. Range discovery is evidence collection; it is not the
  final exported display policy.
- For a physically bounded field or a direct comparison, use an explicit fixed
  range across all comparable panels. For example, phase-2 volume fraction is
  naturally compared on `0–1`; the same colour bar must mean the same thing in
  every case.
- Auto-range is acceptable for a single, non-comparative scene when the field
  has no defensible common bounds, but it is a deliberate choice, not a default.
  If auto-range would make one panel's colour bar jump relative to another,
  either compute a jointly justified comparison range and apply it explicitly,
  or do not present the panels as a direct visual comparison.

Use this range workflow for both filled contours and colour-mapped vectors:

1. Create the exact temporary Fluent plane/surface and graphics object for
   each case/data checkpoint.
2. Discover and record the observed minimum and maximum on that surface for
   the declared field. Keep the case-specific observations separate; never
   overwrite them with a single global value.
3. Choose the display limits from the observations and physical bounds. For a
   matched comparison, take the justified union of the observed ranges and
   round outward to readable limits without clipping relevant values. Use a
   known physical bound directly when it is stronger—for example, phase-2 VOF
   `0–1`.
4. If an outlier would make the field unreadable, do not silently clip it.
   Either retain the outlier in the shared range, investigate it, or create a
   separately labelled diagnostic view with the clipping and claim limit
   stated.
5. Before export, set `global_range=False` and `auto_range=False` on the
   contour or vector range options, apply the chosen numeric limits, and read
   them back. For coloured vectors, keep the vector colour override unset,
   enable the Fluent colour map, and apply the same limits to the velocity (or
   other declared vector-scalar) colour field.
6. Record both the per-case observed ranges and the final displayed range,
   including units, linear/log scale, clipping policy, and whether the range
   was selected from a physical bound, a single-scene observation, or a
   cross-case union.
- Keep the same scalar range, colour map, threshold policy, camera, plane, and
  vector scale for cases whose visual difference is the message. Do not use
  automatic vector scaling for a comparison unless the scale is visibly and
  explicitly shared; fixed-length sparse arrows are preferable when direction
  rather than magnitude is the claim.
- Read back and record the chosen range policy, numeric limits, export
  resolution, and vector scale in the figure handoff. If an auto-range is used,
  record its actual limits and why it was appropriate for that scene.

Clear only the named temporary graphics objects or active display using a
verified API path before each export, then add only the objects required for
that figure. Do not call a broad graphics-collection `clear()` when the wrapper
would enumerate every existing object and hang or mutate unrelated state. This
prevents stale contours or vectors from an earlier case from leaking into the
next image. Reacquire Settings objects after loading a new case/data pair or
creating a surface, inspect allowed values before setting them, and verify the
resulting state.

If several plots answer one question together, keep them as separate native
Fluent exports or create the comparison inside a Fluent scene with a shared
comparison basis. Do not make a dense dashboard out of unrelated fields, and
do not compose a new image outside Fluent. Separate scalar and vector views
when the combination makes both unreadable.

## 5. Export without changing the experiment

Use the version-appropriate PyFluent Settings/API path to display and save the
native Fluent graphics. Do not iterate, initialize, patch, alter
boundary/model/numerical settings, or save over the source case/data pair. If
a needed figure requires a setup mutation or a new run, return that as a
separate scientific action rather than silently doing it here.

Store the primary derived figure with the relevant experiment/stage when it
belongs to one experiment. For a cross-phase meeting report, a copy may live
under the meeting's `figures/` directory, but preserve the source paths and
checkpoint in the report or a figure manifest. Never write under a `raw/`
directory.

## 6. Perform visual and provenance QA

A figure is complete only after both machine and visual checks pass:

- the exact case/data pair and checkpoint are recorded;
- for a patched experiment, both the required post-patch state and the later
  evolved/final or diagnostic state are represented, or the missing post-patch
  evidence is explicitly reported;
- the remote and local output files exist and open as valid images, and the
  image was written by Fluent rather than a local composition step;
- the image uses the intended plane/surface, field, phase, zone, units, and
  scalar/vector ranges;
- compared cases share the declared camera, plane, range, and vector scale;
- the important region is large enough to read at normal report size;
- legends, labels, arrows, colour bars, and annotations are not clipped or
  misleading;
- no stale graphics object from a prior display is present; and
- the caption can state what is observed and what the image cannot prove.

Return a compact figure handoff containing:

```text
Figure path(s):
Figure status: core / responsive / supporting / partial
Source case/data and checkpoint:
Geometry and surface definition:
Field(s), units, ranges, vector sampling/scale:
Observed visual message:
Claim limit or remaining evidence gap:
```

If a step fails, classify the failure as a path/version issue, invalid value,
dependency/order problem, PyFluent limitation, or missing user decision. Keep
the partial artifact labelled and return the narrowest recovery action; do not
silently substitute another case, plane, field, or checkpoint.
