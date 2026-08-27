> **Retired source:** ResearchProject_wiki/wiki/technical/v2-purnanto-spiral-inlet-geometry.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# V2 Purnanto Spiral Inlet Geometry

## Purpose

Record the working geometry dimensions, naming, and reconstruction assumptions for the current `purnantov2` no-brine-outlet spiral-inlet branch.

This page is a compact project-specific geometry note. It keeps the main Purnanto-derived dimensions together with the later reconstruction calculations used for:

- the spiral-inlet scroll curvature; and
- the top vessel head / dish head approximation.

It also records the project naming rule now used for the two related geometry variants:

- `purnanto`
- `purnantov2`

It is not a CAD procedure and it does not replace the reusable source extraction in `CFD_wiki`.

Primary linked context:

- `../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
- [CFD Wiki baseline setup](../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [Phase 1 inlet-exploration index](../experiments/phase-01-purnanto-baseline-and-inlet-exploration/index.md)

## Scope

- Geometry branch: `purnantov2` no-brine-outlet spiral-inlet separator
- Main use: preserve the dimensions, naming, simple construction logic, and calculation trail behind the current reconstruction
- Out of scope: CAD click-paths, meshing steps, Fluent settings, or claims that every reconstructed curve is explicitly reported in the paper

## Geometry Naming Rule

From this point in the project, use:

- `purnanto`
  - the geometry intended to match the original Purnanto spiral-inlet separator more directly;
  - steam-outlet boundary condition placed at the entrance of the steam outlet in the original paper-style interpretation.
- `purnantov2`
  - the later project geometry recorded on this page;
  - steam-outlet pipe meshed farther downward so the outlet boundary condition is placed downstream near the bottom of the separator rather than at the immediate steam-outlet entrance;
  - local inlet spiral and vessel dish-head reconstruction adjusted to make the project geometry more robust than the earlier spline-style version.

Interpretation note:

- `purnanto` is the closer paper-parity geometry label.
- `purnantov2` is the later cleaned and extended project geometry label.
- current project branch mapping:
  - setups `04`, `05`, `06`, and `07` use `purnanto` geometry;
  - setup `08` and later geometry branches use `purnantov2` unless a setup report explicitly overrides that mapping.
- inlet boundary-condition style is tracked separately from geometry naming.

## High-Level Difference Between `purnanto` and `purnantov2`

The current project distinction is:

1. steam outlet boundary placement
   - `purnanto`: outlet boundary at the steam-outlet entrance;
   - `purnantov2`: outlet boundary placed downstream after a longer meshed outlet passage.
2. steam outlet meshing extent
   - `purnanto`: no extra downstream outlet-pipe passage beyond the direct boundary placement interpretation;
   - `purnantov2`: outlet pipe meshed down toward the bottom of the separator before the boundary.
3. local reconstruction detail
   - `purnanto`: earlier direct paper-style geometry label;
   - `purnantov2`: spiral inlet and dish-head region adjusted into a more robust project geometry.

`Assumed`: both names are project geometry labels. They should not be treated as proof that the exact original Purnanto CAD definition is fully known.

## Evidence Labels

- `Reported`: directly taken from the Purnanto paper or the existing baseline extraction
- `Calculated`: derived from reported dimensions using explicit formulas
- `Assumed`: reconstruction choice used because the paper does not fully define the exact local curve or CAD profile
- `Inferred`: interpretation of why the reconstruction choice is reasonable for this project branch

## Baseline Geometry Values Carried Into This Record

These are the main dimensions already reused elsewhere in the project.

| Item | Value | Label | Note |
|---|---:|---|---|
| Separator type | spiral-inlet vertical BOC separator | `Reported` | Purnanto comparison geometry |
| Main vessel diameter `D` | `2.134 m` | `Reported` | `2134 mm` |
| Steam outlet diameter `D_e` | `0.724 m` | `Reported` | also used as the current square-inlet side length in project setup notes |
| Brine outlet diameter `D_b` | `0.508 m` | `Reported` | paper baseline value even though this branch is "no brine outlet" |
| `alpha` | `0.200 m` | `Reported` | Table-3-style baseline dimension |
| `beta` | `2.320 m` | `Reported` | Table-3-style baseline dimension |
| Vessel height `Z` | `4.195 m` | `Reported` | |
| Total height `L_T` | `4.929 m` | `Reported` | |
| Lower-body height `L_B` | `3.579 m` | `Reported` | |
| Inlet / outlet area `A_o` | `0.5242 m2` | `Reported` | matches `0.724 m x 0.724 m` within rounding |

Source trail:

- `CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
- [CFD Wiki baseline setup](../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [Project Purnanto reference](../experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00-reference-spiral-boc/setup.md)

## Rectangular Inlet Face Used In The Current Reconstruction

For the current project branch, the inlet is being treated as a square face:

| Item | Value | Label |
|---|---:|---|
| Inlet width | `724 mm` | `Calculated` |
| Inlet height / extrusion depth | `724 mm` | `Calculated` |
| Inlet area | `0.724 x 0.724 = 0.524176 m2` | `Calculated` |

`Inferred`: this is consistent with the project's existing no-brine-outlet and split-inlet notes, where the current active inlet face has been treated as `0.724 m x 0.724 m`.

## Top Head / Dish Head Reconstruction

### Why this section is separate

`Reported`: the baseline CFD wiki currently notes that the paper treated heads as `2:1 ellipses`.

`Assumed`: the current project reconstruction below keeps the paper-scale diameter and head height, but records a practical CAD-style dish-head approximation using crown and knuckle radii. This should be treated as a project reconstruction choice, not as a claim that the paper explicitly published these exact crown/knuckle values.

### Working inputs

| Item | Value | Label |
|---|---:|---|
| Vessel diameter `D` | `2134 mm` | `Reported` |
| Total dish height `H` | `534 mm` | `Calculated` |

Half diameter:

```text
R_vessel = D / 2 = 2134 / 2 = 1067 mm
```

### Reconstruction formulas used

The reconstruction prompt used the following dish-head relations:

```text
H = D/4 + SF
CR = 0.948 D
KR = 0.173 D
```

where:

- `SF` = straight flange
- `CR` = crown radius
- `KR` = knuckle radius

### Calculated dish-head values

### Straight flange

```text
SF = H - D/4
SF = 534 - 2134/4
SF = 534 - 533.5
SF = 0.5 mm
```

| Item | Value | Label | Note |
|---|---:|---|---|
| Straight flange `SF` | `0.5 mm` | `Calculated` | effectively `0 mm` for this reconstruction |

### Crown radius

```text
CR = 0.948 x 2134
CR = 2023.03 mm
```

| Item | Value | Label |
|---|---:|---|
| Crown radius `CR` | `2023 mm` | `Calculated` |

### Knuckle radius

```text
KR = 0.173 x 2134
KR = 369.18 mm
```

| Item | Value | Label |
|---|---:|---|
| Knuckle radius `KR` | `369.2 mm` | `Calculated` |

### Dish-head interpretation

- `Calculated`: the chosen head height of `534 mm` gives a straight flange of only `0.5 mm`.
- `Inferred`: for practical reconstruction, this is effectively a no-straight-flange head.
- `Assumed`: if a later fabrication-style model needs a real weld flange, the total head height should be increased rather than silently changing the crown/knuckle geometry.

## Spiral-Inlet Scroll Reconstruction

### Why this section exists

`Reported`: the paper identifies the geometry as a rectangular `90 deg` spiral inlet and describes smoother entry behavior than the tangential alternatives.

`Missing`: the paper does not provide a full scroll-wall equation or a complete CAD-ready centre-point list for the spiral wall.

`Assumed`: the current project reconstruction therefore uses a simple tangent-continuous `3`-arc approximation for the outer wall, while the inner wall is kept straight and perpendicular to the inlet face with no added curvature.

`User-specified`: this cleaned reconstruction is now part of the `purnantov2` geometry identity rather than an unnamed local variation.

### Coordinate system and main assumptions

Top-view construction plane:

```text
(x, z)
```

with vessel centre:

```text
O = (0, 0)
```

and vessel radius:

```text
R = 1067 mm
```

Working inlet-face points:

```text
A = (-1067, 737)
B = (-1067, 1461)
```

So the inlet width is:

```text
1461 - 737 = 724 mm
```

Additional working assumptions:

- `Assumed`: flow enters in the `+x` direction
- `Assumed`: the outer wall starts at `B = (-1067, 1461)`
- `Assumed`: the outer wall merges into the vessel at `M = (1067, 0)`
- `Assumed`: the outer scroll turn is approximated by three tangent arcs, each rotating the heading by `30 deg`, for a total `90 deg` turn
- `Assumed`: the final outer-wall arc radius is set to `1200 mm` so the wall stays outside the vessel before merging

### Outer wall: three tangent arcs

| Arc | Centre `(x, z)` mm | Radius mm | Start point | End point | Centre-angle range |
|---|---:|---:|---|---|---|
| Arc 1 | `(-1067, -1577.67)` | `3038.67` | `B = (-1067, 1461)` | `J1 = (452.34, 1053.90)` | `90 deg -> 60 deg` |
| Arc 2 | `(-167.70, -20.03)` | `1240.07` | `J1 = (452.34, 1053.90)` | `J2 = (906.23, 600.00)` | `60 deg -> 30 deg` |
| Arc 3 | `(-133.00, 0)` | `1200.00` | `J2 = (906.23, 600.00)` | `M = (1067, 0)` | `30 deg -> 0 deg` |

Heading transition preserved by construction:

```text
0 deg -> -30 deg -> -60 deg -> -90 deg
```

`Inferred`: this gives a smoother inlet turn than a single hard corner while staying simple enough to document and rebuild.

### Inner wall reconstruction

The inner wall is not given a scroll curve in this reconstruction.

- `Assumed`: keep the inner wall straight.
- `Assumed`: keep it perpendicular to the inlet face.
- `Assumed`: do not add a tangent arc, spline, or vessel-following curvature on the inner wall.

Practical interpretation:

- the outer wall provides the scroll-like turning shape;
- the inner wall remains a straight construction edge for this `v2` geometry record.

### Practical interpretation

- `Assumed`: this is a geometry-rebuild aid, not a proof of the paper's exact original scroll profile.
- `Inferred`: the approximation is still consistent with the paper's qualitative claim that the spiral inlet creates a smoother transition into rotation than the tangential alternatives.
- `Assumed`: if later CFD sensitivity shows strong dependence on the inner-wall treatment or local curvature near merge point `M`, this page should be revised with the updated curve definition rather than editing the values silently.
- `User-specified`: compared with the `purnanto` geometry label, `purnantov2` keeps the same broad separator concept but uses a more deliberate local reconstruction for the inlet spiral and dish-head region.

## Compact Construction Summary

### Vessel and top head

- Vessel centre: `O = (0, 0)`
- Vessel radius: `1067 mm`
- Dish height: `534 mm`
- Straight flange: `0.5 mm` effectively `0 mm`
- Crown radius: `2023 mm`
- Knuckle radius: `369.2 mm`

### Spiral inlet

- Inlet face endpoints: `A = (-1067, 737)`, `B = (-1067, 1461)`
- Merge point: `M = (1067, 0)`
- Inner wall: straight and perpendicular to inlet face, with no added curvature
- Outer arc radii: `3038.67 mm`, `1240.07 mm`, `1200.00 mm`

## Open Uncertainties

- The paper does not provide the exact scroll-wall equation or a definitive CAD construction for the spiral wall.
- The paper-scale vessel dimensions are traceable, but the local no-brine-outlet geometry may still differ from the original published branch in details not captured by Table 3 alone.
- The dish-head reconstruction recorded here is a project approximation and may not match the exact head family implied in the source paper.

## Reuse Note

Use this page when the project needs:

- one place to look up the current `purnantov2` no-brine-outlet spiral-inlet dimensions;
- the naming rule for `purnanto` versus `purnantov2`;
- the centre points and radii behind the current scroll reconstruction; or
- the logic behind the current top-head approximation.

Use the setup reports for run-specific boundary-condition packages and use `CFD_wiki` for reusable source extraction.
