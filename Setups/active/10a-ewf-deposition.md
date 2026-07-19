# Setup 10a — Eulerian Wall Film Deposition and Drainage

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `10a` |
| Lifecycle | `active` |
| Role | no-splash EWF deposition/drainage reference branch |
| Parent setup | [09c](09c-dpm-ewf-wall-film-reentrainment.md) |
| Evidence-use label | active diagnostic/control case; results pending |
| Outcome | needs follow-up |
| Related child | [10a-splash](10a-splash-ewf-deposition.md) |
| Family plan | [Setup 10 family plan](../future/10-wall-film-reentrainment-and-dpm-interaction-plan.md) |

## 1. Purpose

Keep `10a` as the clean EWF deposition/drainage control. Its purpose is to separate ordinary DPM-to-film deposition and film motion from the optional splash mechanism used in `10a-splash`.

## 2. Parent-to-child change from `09c`

| Area | `09c` parent | `10a` child |
|---|---|---|
| Eulerian Wall Film | `Off` | `On` |
| Film walls | none | selected physical liquid-impact wall zones |
| DPM Interaction with Continuous Phase | `On` in the original `09c` definition; current fallback may be `Off` after the coupled error | `Off` for the current stability fallback |
| EWF DPM Coupling | not applicable | `On` |
| Film material | not applicable | `water-liquid-at-psep` |
| Solve Momentum | not applicable | `On`, `Momentum Equation` |
| Gravity / Surface Shear / Pressure Gradient | not applicable | `On` / `On` / `On if available` |
| Flow Momentum Coupling | not applicable | `Off` |
| Particle Splashing | not applicable | `Off` |
| Edge Separation / Particle Stripping | not applicable | `Off` / `Off` |
| Maximum Thickness | not applicable | `0.005 m` initial cap |
| Initial film | not applicable | zero height and zero velocity |

All geometry, mesh, carrier model, inlet/outlet package, six-injection payload, particle material, and tracking controls remain inherited from `09c`.

## 3. Current status

`10a` is now an active setup branch and serves as the no-splash reference for the initialized `10a-splash` child. The exact film-wall zone names and saved-case readback must be retained before interpreting results.

