# Phase 07 figure manifest

Status: native Fluent meeting figures, 14 September 2026.

Every image listed here was exported by Fluent from a saved case/data
checkpoint. No HTML, schematic, local drawing, image compositing, or other
non-Fluent figure-generation step is part of these deliverables. The local
copy is only the retrieved native Fluent export.

| Figure | Source/checkpoint | Fluent surface and visual policy | Evidence status |
|---|---|---|---|
| `P07A-native-lower-ZX-Y005-active1900-contour-only-normal-2400x1800.png` | Phase 07A absorber durable pair, active `1900`, `student` | **Contour-only** `ZX` plane at `Y = 0.05 m`; phase-2 VOF fixed at `0–1`; no vector object; orthographic camera normal to `ZX`; `2400 × 1800`; zoom `1.15` after `auto_scale` | Native Fluent lower-zone phase-distribution view; no convergence claim |
| `P071A-native-RNG-active500-XY-Z0-vector-colour-normal-2400x1800.png` | Phase 07.1A RNG pair, active `500`, `student` | **Vector-only** `XY` plane at `Z = 0`; complete in-plane field with `skip=0`; fixed-length arrows, scale `0.05`, coloured by mixture velocity magnitude on shared `0–225 m/s`; orthographic camera normal to `XY`; `2400 × 1800`; zoom `0.95` after `auto_scale` | Native Fluent finite-state vector comparison view |
| `P071A-native-standard-active500-XY-Z0-vector-colour-normal-2400x1800.png` | Phase 07.1A standard `k–epsilon` pair, active `500`, `student` | Same vector-only `XY @ Z=0` plane, all vectors (`skip=0`), fixed-length arrows with scale `0.05`, mixture velocity-magnitude colour range `0–225 m/s`, orthographic camera normal to `XY`, `2400 × 1800`, zoom `0.95` | Native Fluent finite-state vector comparison view |
| `P071A-native-realizable-active500-XY-Z0-vector-colour-normal-2400x1800.png` | Phase 07.1A realizable `k–epsilon` pair, active `500`, `student` | Same vector-only `XY @ Z=0` plane, all vectors (`skip=0`), fixed-length arrows with scale `0.05`, mixture velocity-magnitude colour range `0–225 m/s`, orthographic camera normal to `XY`, `2400 × 1800`, zoom `0.95` | Native Fluent finite-state vector comparison view |

## Exact source identities

- Phase 07A absorber pair: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberColdContinuation\20260910T211158Z\P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000\checkpoint-1900-1-01900.cas.h5` plus the paired `.dat.h5`.
- Phase 07.1A RNG pair: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T0-RNG-REFERENCE\20260911T092613Z\P71A-T0-RNG-REFERENCE-active500.cas.h5` plus the paired `.dat.h5`.
- Phase 07.1A standard `k–epsilon` pair: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T1-STANDARD-KEPSILON\20260911T094339Z\P71A-T1-STANDARD-KEPSILON-active500.cas.h5` plus the paired `.dat.h5`.
- Phase 07.1A realizable `k–epsilon` pair: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T1-REALIZABLE-KEPSILON\20260911T100157Z\P71A-T1-REALIZABLE-KEPSILON-active500.cas.h5` plus the paired `.dat.h5`.

The absorber-plane contour was exported with `global_range=False` and
`auto_range=False`, using the explicit bounded phase-2 VOF range `0–1`. The
Three closure exports are vector-only and therefore have no scalar contour
object. They use the same no-subsampling vector policy (`skip=0`), fixed arrow
scale, Fluent velocity-magnitude colour map, and explicit shared linear range
`0–225 m/s` with `global_range=False` and `auto_range=False`. Each camera was
set perpendicular to its plane with an explicit position, target, up-vector,
and orthographic projection, then tightened iteratively in Fluent after
`auto_scale`. No pixels were subsequently edited outside Fluent.

Camera readback/provenance for the current exports:

- Phase 07A `ZX @ Y=0.05 m`: position `[0, 10, 0.05]`, target
  `[0, 0.05, 0]`, up-vector `[0, 0, 1]`, orthographic, zoom `1.15`.
- Phase 07.1A `XY @ Z=0`: position `[0, 3, 10]`, target `[0, 3, 0]`,
  up-vector `[0, 1, 0]`, orthographic, zoom `0.95`.
