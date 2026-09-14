# Phase 05 figure package

These four PNGs are unchanged native Fluent exports prepared for the Phase 05
meeting narrative. They are a diagnostic spatial companion to the existing
quantitative plots; they are not evidence that the full-geometry branch was
qualified or converged.

## Figure set

| Figure | Question it answers | Fluent display |
|---|---|---|
| [F09 phase-2 distribution](P05-F09-XY-Z0-phase2-vof-contour.png) | Where is phase 2 concentrated in the full separator? | Contour only; `phase-2-vof`; `X–Y` plane at `Z=0` |
| [F12 phase-2 distribution](P05-F12-XY-Z0-phase2-vof-contour.png) | Does the later diagnostic state show the same spatial distribution? | Contour only; `phase-2-vof`; `X–Y` plane at `Z=0` |
| [F09 velocity field](P05-F09-XY-Z0-velocity-vectors.png) | What flow direction and speed structure accompanies the F09 distribution? | Vector only; velocity vectors coloured by velocity magnitude; `X–Y` plane at `Z=0` |
| [F12 velocity field](P05-F12-XY-Z0-velocity-vectors.png) | What flow direction and speed structure accompanies the F12 distribution? | Vector only; velocity vectors coloured by velocity magnitude; `X–Y` plane at `Z=0` |
| [F09 steam-outlet routing](P05-F09-steamoutlet-velocity-vectors.png) | What does the local flow look like at the actual steam outlet face? | Vector only; `steamoutlet` boundary face; local velocity range `0–160 m/s` |
| [F12 steam-outlet routing](P05-F12-steamoutlet-velocity-vectors.png) | Does the local outlet pattern persist in the later diagnostic state? | Vector only; `steamoutlet` boundary face; local velocity range `0–160 m/s` |

## Reproducibility and visual settings

- **Source F09:** exact paired Stage 3 case/data state `03a-stage3-f09-final-iter015000`.
  The artifact record identifies this as a hash-verified completed diagnostic
  state from source run F09; it is not treated as a qualified baseline.
- **Source F12:** exact paired Stage 3 case/data state `f12-final-iter018000`.
  The artifact record preserves a reported cumulative-iteration identity
  discrepancy, so this is also labelled diagnostic rather than used as exact
  iteration proof.
- **Surface:** an explicit native Fluent `xy-plane` at `Z=0`; the displayed
  plane bounds were consistent between F09 and F12.
- **Contour range:** fixed physical phase-2 volume-fraction range `0–1` for
  both states. Observed displayed-surface ranges were F09 `0–0.975214` and
  F12 `0–0.789167`.
- **Vector colour range:** fixed common range `0–60 m/s` for both states.
  Observed displayed-surface velocity-magnitude ranges were F09
  `0.660–55.899 m/s` and F12 `0.172–50.798 m/s`.
- **Vector sampling:** all vectors shown (`skip=0`), in-plane, fixed arrow
  length, Fluent velocity colour map enabled, native arrow scale `0.18`.
- **Local outlet range:** the `steamoutlet` boundary face was checked
  separately because its observed maxima were approximately `148.4 m/s` for
  F09 and `146.9 m/s` for F12; the two outlet figures therefore use a shared
  `0–160 m/s` range and a smaller native arrow scale `0.01`.
- **Camera:** orthographic, perpendicular to the `X–Y` plane; position
  `[0, 2.75, 15]`, target `[0, 2.75, 0]`, up vector `[0, 1, 0]`, native zoom
  factor `1.35`.
- **Local outlet camera:** orthographic, normal to the outlet face; position
  `[0, 16.261, 0]`, target `[0, 6.261, 0]`, up vector `[0, 0, 1]`, native zoom
  factor `0.8`.
- **Boundary-face geometry:** the local outlet figures use the actual named
  Fluent `steamoutlet` face at `Y≈6.261 m`, not an assumed internal `X–Z`
  plane. The named `steaminlet` face was also inspected but excluded from the
  meeting set because its velocity magnitude is uniformly prescribed at
  `27.118 m/s` in both states; it adds little diagnostic information.
- **Export:** native Fluent PNG at `2400×1800`, colour mode, independent
  contour-only or vector-only scene. No HTML, SVG, raster editing,
  compositing, or post-export pixel manipulation was used.

## Claim boundary

The figures support the bounded statement that the tested full-geometry
states exhibit wall/outer-region phase-2 accumulation together with a complex
recirculating velocity structure. They do not, by themselves, establish a
stable outlet route, mass closure, convergence, or physical impossibility of
the separator.

The F09/F12 artifact records do not identify a patching operation for these
states; consequently this package does not claim to show a post-patch versus
evolved comparison. If a patched Phase 05 state is later selected for the
report, it must be paired with its post-patch checkpoint and its evolved or
last-valid checkpoint before the figure set is finalised.
