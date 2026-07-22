# Setup 10a-splash — Eulerian Wall Film With Particle Splashing

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `10a-splash` |
| Lifecycle | `future` |
| Role | EWF deposition/drainage diagnostic with particle splashing |
| Parent setup | [09c](09c-dpm-ewf-wall-film-reentrainment.md) |
| Fallback parent interpretation | `09c` case with DPM interaction with the continuous phase disabled after the coupled calculation failed |
| Evidence-use label | initialized diagnostic; results pending |
| Outcome | needs follow-up |
| Linked family plan | [Setup 10 family plan](../future/10-wall-film-reentrainment-and-dpm-interaction-plan.md) |

## 1. Purpose

Test whether the injected liquid DPM payload deposits on designated separator walls, forms/drains an Eulerian wall film, and produces secondary splashed DPM parcels under the current separator conditions.

This is a splash-sensitive diagnostic. It is not yet a validated wall-film or re-entrainment model, and it is not the same as the original no-splash `10a` baseline.

## 2. Parent-to-child change record

The following table is the controlling comparison between the active `09c` definition and this initialized child.

| Area | `09c` parent | `10a-splash` child | Change meaning |
|---|---|---|---|
| Eulerian Wall Film | `Off` | `On` | adds wall-film equations |
| Designated film walls | none | selected physical liquid-impact wall zones; exact Fluent zone names must be retained with the case | defines where EWF is solved |
| DPM Interaction with Continuous Phase | `On` | `Off` | stability fallback; removes DPM source feedback into the bulk flow |
| EWF DPM Coupling | not applicable | `On` | permits DPM impacts to transfer liquid mass into the EWF film |
| Film material | not applicable | `water-liquid-at-psep` | matches the liquid-water surrogate used for the project branch |
| Solve Momentum | not applicable | `On`, `Momentum Equation` | solves film velocity and drainage |
| Continuity/momentum coupled solution | not applicable | `Off` | first-pass film stability choice |
| Wall Flow Momentum Coupling | not applicable | `Off` | gas drives film one-way; film does not feed momentum back to the bulk gas |
| Gravity Force | not applicable | `On` | allows gravity-driven drainage |
| Surface Shear Force | not applicable | `On` | allows carrier-flow shear to drive the film |
| Pressure Gradient | not applicable | `On` if available/read back | retains separator pressure-gradient effect |
| Maximum Thickness | not applicable | `0.005 m` | Fluent safety cap; monitor for material removal at the limit |
| Particle Splashing | not applicable | `On` | allows impact-generated secondary DPM parcels |
| DPM Wall Splash | not applicable | `On` on selected film walls | activates wall-level splash treatment |
| Number of Splashed Particles | not applicable | `4` | Fluent default parcel count; record with results |
| Impingement model | not applicable | `stanton-rutland` | first-pass EWF splash model |
| Source Smoothing | not applicable | `Off` | avoids changing source distribution in the first splash comparison |
| Edge Separation | not applicable | `Off` | reserves film-edge separation for later re-entrainment work |
| Particle Stripping | not applicable | `Off` | avoids an uncalibrated shear-stripping closure |
| Initial film state | not applicable | zero height and zero velocity | no pre-existing film or external film source |

## 3. Settings intentionally retained from `09c`

Unless the Fluent readback shows otherwise, retain:

- geometry and mesh;
- split inlet boundaries and mass-flow definitions;
- outlet boundaries and backflow values;
- `Mixture` multiphase model and phase definitions;
- `RNG k-epsilon` turbulence model;
- Energy `Off`;
- gravity and operating pressure;
- six active surface injections on `steaminlet`;
- the six-injection represented loading of `29.22 kg/s`;
- injection diameters, particle material, drag, tracking limits, particle count, and injection velocities;
- ordinary DPM wall fates outside the designated EWF walls.

The `09c` parent reference had `wall = reflect`, `bottom = trap`, and inlet/outlet escape fates. Any change to those fates must be recorded as a separate child change.

## 4. Initialization and run status

| Item | Status |
|---|---|
| EWF model enabled | `User-reported: yes` |
| Film wall designation | `User-reported: completed; exact zone names pending readback` |
| Hybrid initialization | `User-reported: completed after correcting the no-film-wall warning` |
| Dedicated EWF initialization | confirm/read back before the production run |
| Flow iterations after initialization | not yet run |
| Transient film solution | planned for the production diagnostic |
| Case/data result files | not yet available |

## 5. Required readback before running

1. Record the exact wall zones marked `Eulerian Film Wall`.
2. Confirm each selected wall uses `Initial Condition` with zero film height and velocity.
3. Confirm `EWF DPM Coupling = On`.
4. Confirm `DPM Interaction with Continuous Phase = Off`.
5. Confirm `Particle Splashing = On`, `DPM Wall Splash = On`, `Number of Splashed Particles = 4`, and `stanton-rutland`.
6. Confirm `Flow Momentum Coupling = Off` on every selected film wall.
7. Confirm film-wall edges do not create unintended film outlets.
8. Save a case checkpoint before the first production iterations.

## 6. Required result record

Report separately:

- film mass and film thickness by wall zone;
- film velocity and drainage direction;
- DPM mass transferred into the film;
- splashed DPM parcel count and represented mass;
- escaped, trapped, incomplete, and splashed DPM fates;
- steam-outlet liquid phase flux;
- `Film Outflow Mass`, `Film DPM Mass Source`, `Film Stripped Mass`, and `Film Separated Mass`;
- maximum film thickness and any material removal caused by the `0.005 m` cap;
- residual and mass-balance behavior.

## 7. Interpretation gate

Promote this beyond diagnostic status only if:

- the film-wall zones and coupling settings are read back from the saved case;
- the DPM-to-film and splash mass balance closes sufficiently for the run;
- film inventory is bounded or its growth has a defensible physical interpretation;
- splashed mass is distinguishable from direct DPM escape and film outflow;
- the result is compared against the no-splash `10a` reference or a clearly stated baseline.
