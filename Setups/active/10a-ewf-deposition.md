# Setup 10a — Eulerian Wall Film Deposition and Drainage

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `10a` |
| Lifecycle | `active` |
| Role | intended no-splash EWF deposition/drainage control; recorded artifact is splash-enabled |
| Parent setup | [09c](09c-dpm-ewf-wall-film-reentrainment.md) |
| Evidence-use label | active diagnostic; preliminary result available, but not a clean no-splash control |
| Outcome | needs follow-up |
| Related child | [10a-splash](10a-splash-ewf-deposition.md) |
| Family plan | [Setup 10 family plan](../future/10-wall-film-reentrainment-and-dpm-interaction-plan.md) |

## 1. Purpose

Keep `10a` as the intended clean EWF deposition/drainage control. The saved case currently labelled `10a` was read back with particle splashing enabled, so its preliminary result is treated as a `10a-splash`-type diagnostic until a corrected no-splash case is created.

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
| Particle Splashing | not applicable | `Off` intended; `On` in the recorded `10a` artifact |
| DPM Wall Splash | not applicable | `Off` intended; `On`, with `4` splashed particles, in the recorded artifact |
| Impingement model | not applicable | `stanton-rutland` in the recorded artifact |
| Edge Separation / Particle Stripping | not applicable | `Off` / `Off` |
| Maximum Thickness | not applicable | `0.005 m` initial cap |
| Initial film | not applicable | zero height and zero velocity |

All geometry, mesh, carrier model, inlet/outlet package, six-injection payload, particle material, and tracking controls remain inherited from `09c`.

## 3. Current status

`10a` remains the intended no-splash branch, but it is not yet an executed no-splash reference. The available case/data checkpoint is documented in the [preliminary 10a report](../reports/10a/results.md) and has `wall` as an EWF wall, `bottom` without EWF, and splash enabled. Use that result as a splash-sensitive diagnostic, not as the clean control. Create a fresh case with both global and wall-level splash disabled before making a no-splash comparison.
