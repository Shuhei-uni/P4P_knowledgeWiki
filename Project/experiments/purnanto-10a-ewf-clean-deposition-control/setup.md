> **Retired source:** Setups/past/archived/10a-ewf-deposition.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Setup 10a — Eulerian Wall Film Deposition and Drainage

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `10a` |
| Lifecycle | `archived` |
| Role | intended no-splash EWF deposition/drainage control; recorded artifact is splash-enabled |
| Parent setup | [09c](../purnanto-09c-two-way-dpm-coupling/setup.md) |
| Evidence-use label | archived setup-only control; the preliminary splash-enabled result belongs to `10a-splash` |
| Outcome | needs follow-up |
| Linked report | none — the splash-enabled saved artifact is filed under `10a-splash` |
| Related child | [10a-splash](../purnanto-10a-splash-ewf-preliminary/setup.md) |
| Family plan | [Setup 10 family plan](../purnanto-10-wallfilm-dpm-sensitivity/setup.md) |

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

`10a` remains the intended no-splash branch, but it is not yet an executed no-splash reference. The available case/data checkpoint is documented in the [preliminary 10a report](../purnanto-10a-splash-ewf-preliminary/results.md) and has `wall` as an EWF wall, `bottom` without EWF, and splash enabled. Use that result as a splash-sensitive diagnostic, not as the clean control. Create a fresh case with both global and wall-level splash disabled before making a no-splash comparison.
