# Setup 10 — Independent Wall-Film and DPM Interaction Tests

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `10` family plan |
| Lifecycle | `future` |
| Role | independently runnable wall-film / re-entrainment / custom-DPM tests |
| Parent setup | [09c](../past/archived/09c-dpm-ewf-wall-film-reentrainment.md) case definition |
| Fallback parent | Same `09c` source case with two-way DPM disabled, or [09a](../past/reported/09a-dpm-split-inlet-carryover.md) |
| Child plans | `10a`, `10b`, `10c` |
| Evidence-use label | diagnostic until interpretation gates pass |
| Outcome | needs follow-up |
| Linked report | none |

## 1. Why these tests are next

The immediate active work is:

- `08c`: test low/reference/high inlet loading at fixed enthalpy basis;
- `09c`: test whether the current six-injection DPM payload changes the carrier field.

The current `09c` artifact is **not** a wall-film case. It has two-way DPM interaction, six injections, and `29.22 kg/s` represented liquid loading, but no EWF, re-entrainment, or custom wall law.

Because the long runs are time-limited, run `10a`, `10b`, and `10c` tomorrow even if the full evidence gate is not yet closed. If the gate fails, label the runs `diagnostic only`; do not discard them.

## 2. Common parent and controls

All three children should start from the same `09c` case definition wherever possible. Keep these fixed:

- geometry and mesh;
- split inlet boundaries and mass flows;
- outlet boundaries and backflow values;
- `Mixture` model, phases, materials, gravity, and operating pressure;
- `RNG k-epsilon` and Energy-off state;
- six-injection DPM payload, diameters, represented mass flow, and injection surface;
- DPM tracking limits and particle count;
- comparison monitors and report surfaces.

Do not switch from the current six-injection `29.22 kg/s` payload to the broader nine-bin payload during this family. If the payload is changed, create a separate branch.

## 3. Tomorrow's minimum test package

| Test | Parent | Single intentional change | Main question |
|---|---|---|---|
| `08c` low/reference/high | `08b` | inlet mass loading / resulting velocity | does loading change carryover, pressure drop, swirl, or stability? |
| `09c` | `08b`-style split-inlet case | DPM continuous-phase interaction on | does DPM feedback change the carrier field or fate? |
| `10a` | `09c` | EWF and DPM-to-film coupling on | does a wall film form and drain? |
| `10b` | `09c` | controlled DPM wall-return condition | does returning wall-hit liquid increase carryover? |
| `10c` | `09c` | one custom DPM law or material variant | do default wall/material assumptions control the result? |

## 4. Child setup definitions

### `10a` — EWF deposition and drainage only

Parent: `09c`. If coupled `09c` is unstable, use the same case with two-way DPM disabled and record the fallback.

Change only:

- `Models > Eulerian Wall Film`: `Off -> On`;
- assign EWF only to confirmed cyclone barrel, baffle/collector, and liquid-impact wall zones;
- enable EWF `DPM Coupling` / standard impingement so DPM impacts can deposit mass into the film;
- keep DPM `Interaction with Continuous Phase` **Off** for the current stability fallback, so film deposition is tested without DPM source feedback into the bulk flow;
- change steady to transient so film inventory and drainage can be measured.

First-pass child settings:

- `Solve Momentum`: `On`, using `Momentum Equation`;
- `Continuity and Momentum Coupling > Coupled Solution`: `Off` for the first stability baseline;
- `Gravity Force`: `On`;
- `Surface Shear Force`: `On`;
- `Pressure Gradient`: `On` if available in the active Fluent version;
- `Spreading Term`, `Surface Tension`, `Solve Energy`, and `Solve Scalar`: `Off`;
- `Phase Coupling`, `VOF Coupling`, `Treat Sharp Edge`, `Particle Splashing`, `Edge Separation`, and `Particle Stripping`: `Off`;
- wall film condition: zero-height, zero-velocity initial film with no external source term;
- wall `Flow Momentum Coupling`: `Off` for the first `10a` stability baseline; enable only in `11a`;
- first film time scheme: `First Order Implicit`; first film continuity/momentum schemes: `First Order Upwind`;
- do not use a low arbitrary `Maximum Thickness`, because Fluent removes material when that limit is exceeded.

Keep unchanged:

- `Mixture`, `RNG k-epsilon`, Energy off, gravity, mesh, inlet/outlet conditions, DPM payload, and DPM coupling state;
- no custom bounce law, re-entrainment UDF, material change, species, evaporation, or geometry change.

Current execution decision:

- DPM `Interaction with Continuous Phase`: `Off` because the previous `09c` coupled calculation failed;
- EWF `DPM Coupling`: `On`, because this is the separate DPM-to-film deposition mechanism required for `10a`;
- if EWF `DPM Coupling` is also disabled, the run no longer tests DPM deposition/drainage and should be labeled an empty-film solver diagnostic instead.

Find out:

- whether film mass forms;
- film thickness and flow direction by wall zone;
- deposition and drainage rates;
- DPM-to-film transfer;
- steam-outlet liquid phase flux plus escaped DPM mass;
- whether film inventory is bounded or grows indefinitely.

#### `10a-splash` — deposition with particle splashing

This child is the splash-enabled variation. The saved run currently labelled `10a` was read back with this state, so it is treated as a `10a-splash`-type diagnostic. The no-splash `10a` configuration below remains the intended control and still needs a separate clean case.

From a fresh `10a` case, change only:

- Eulerian Wall Film `Particle Splashing`: `Off -> On`;
- on each selected film wall, enable `DPM Wall Splash`;
- leave `Number of Splashed Particles` at the Fluent default for the first run and record the value.

Keep `Edge Separation`, `Particle Stripping`, and `Source Smoothing` off. Do not change the impingement model, roughness parameters, surface tension, or wall momentum coupling in the same child. Fluent documents `DPM Wall Splash` and `Number of Splashed Particles` as the wall-level controls exposed when Particle Splashing is enabled ([official wall-film boundary reference](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_ewf_sec_bound.html)).

Interpret `10a-splash` as a splash-sensitive diagnostic rather than pure deposition/drainage. Report splashed DPM mass/count separately from film mass, escaped mass, trapped mass, and steam-outlet carryover.

### `10b` — DPM wall-return / re-entrainment surrogate only

Parent: `09c`, independently of `10a`. This is a wall-fate screening test, not a full physical film model.

Keep EWF `Off` and keep all current `09c` DPM controls unchanged:

- two-way DPM interaction remains `On`;
- update DPM sources every flow iteration remains `On`;
- DPM iteration interval remains `1`;
- spherical drag, particle rotation, stochastic dispersion, injection surfaces, diameters, and represented mass flow remain unchanged.

Use the following nested child sequence:

#### `10b-0` — wall-fate reference

- duplicate `09c` without changing the wall condition;
- read back the current wall `DPM` boundary type and normal/tangential restitution coefficients;
- retain `steamoutlet = escape`, `bottom/collection = trap`, and ordinary walls as currently defined.

This establishes the exact reference before changing wall behavior.

Execution rule for `10b-1` and `10b-2`:

- make each child by saving a fresh copy of the original `09c` case/data;
- keep the global DPM `Interaction with Continuous Phase` state identical across the children;
- if the original `09c` `On` state cannot run, use `Off` for both children and label both as the stability-fallback variants;
- change only the selected wall DPM boundary condition between the children;
- keep EWF `Off` in both children.

#### `10b-1` — built-in wall-return surrogate

Change only the selected liquid-impact wall zones:

- test `wall-jet` as the first built-in wall-return surrogate if available;
- otherwise use `reflect` with a documented normal/tangential restitution sensitivity;
- do not use `trap` on the selected impact walls;
- leave inlet and outlet fates unchanged.

`wall-jet` is a screening representation of liquid continuing along/away from the wall; it is not proof of a resolved liquid film.

#### `10b-2` — user-defined wall-return law

Only if `10b-1` shows a meaningful sensitivity:

- set the selected wall DPM condition to `user-defined`;
- compile/interpret and hook one `DEFINE_DPM_BC` function;
- define one bounded return rule based on documented impact inputs such as impact angle or normal impact speed;
- define a fallback fate for particles outside the valid range;
- do not also enable EWF, splashing, stripping, custom drag, or material changes.

Do not use `reinject` for the first wall-return test. Fluent's `reinject` condition is intended to reintroduce particles at a domain boundary using a specified injection and requires unsteady particle tracking; it is not the clean internal-wall-film surrogate for this branch.

Compare:

1. `09c` default wall fate;
2. `10b` controlled wall return.

Find out:

- wall impacts, returned particles, escaped particles, trapped particles, and incomplete particles;
- returned liquid mass;
- change in steam-outlet carryover;
- whether wall fate is more influential than two-way coupling.

Label this result `wall-return sensitivity`; it does not prove a physical film exists.

### `10c` — Custom DPM trajectory/material sensitivity only

Parent: `09c`, independently of `10a` and `10b`. Keep EWF and wall-return re-entrainment off.

Run the following as separate subcases, not one combined run:

#### `10c-T` custom trajectory

Change one mechanism only:

- wall-impact state: `DEFINE_DPM_BC`;
- initial injection state: `DEFINE_DPM_INJECTION_INIT`;
- drag/body force: `DEFINE_DPM_DRAG` or `DEFINE_DPM_BODY_FORCE`.

Recommended first comparison:

- default wall interaction;
- lower normal restitution / stronger sticking;
- one bounded impact-angle or Weber/Stokes transition law.

Do not add splash/reinjection until the mass balance is closed.

#### `10c-M` material

Change one material definition only:

- current `water-liquid` baseline;
- brine-like surrogate with documented density, viscosity, and surface tension;
- multicomponent or nonvolatile-solids surrogate only if species/energy physics is intentionally enabled.

With inert DPM and Energy off, changing the material name alone is not a physical test. An active property or transport mechanism must change.

For every UDF/material case, record equations, dimensional inputs, valid ranges, fallback behavior, and active material properties.

## 5. Required outputs for the active plans

### `08c`

For each velocity, report actual inlet phase flows, steam-outlet vapor/liquid fluxes, carryover fraction, removal efficiency, pressure drop, complete mass imbalance, residuals, outlet backflow, and qualitative swirl/recirculation changes.

### `09c`

Report one-way versus two-way carrier-field differences, injected/escaped/trapped/incomplete counts by diameter, represented mass flow per injection, residual/monitor stability, and whether the conclusion changes when source feedback is enabled.

### `10a`

Report film mass and thickness histories, deposition/drainage rates, DPM-to-film transfer, escaped DPM mass, continuous liquid at the steam outlet, film inventory drift, and complete phase balance.

### `10b`

Report wall-impact, returned, escaped, trapped, incomplete, and returned-mass fractions, plus the change relative to `09c`.

### `10c`

Report the exact UDF/material definition, active properties, trajectory/fate changes, and whether the result changes direct escape, wall retention, or film-relevant wall impact.

## 6. Setup 10 gates

### Execution gate — may run tomorrow

Run a child if:

1. the parent `.cas.h5` loads;
2. intended wall zones and injections read back;
3. the changed model setting reads back;
4. the case saves with the change isolated.

This gate is intentionally permissive because the runs are expensive.

### Interpretation gate — required before report-quality claims

Do not promote a setup `10` result beyond `diagnostic only` until:

1. the parent case has stable residuals and physical monitors;
2. complete inlet/outlet phase mass balance is available;
3. DPM incomplete tracks are reported and bracketed;
4. `10a` film inventory is bounded over the averaging window;
5. `10b` returned wall mass is conserved and distinguishable from direct escape;
6. `10c` laws/materials have documented properties and valid ranges.

## 7. Gate for setup 11

| Observation | Decision |
|---|---|
| `10a` film does not form | record EWF as inactive for this operating point; do not force `11a` |
| `10a` film grows without bound | repair timestep, wall coverage, film drainage, or compatibility before combining |
| `10b` wall return materially changes carryover | use that closure in `11a` |
| `10b` effect is negligible | retain default wall fate in `11a` |
| `10c` materially changes trajectory/fate | carry the selected law/material into `11b` |
| `10c` effect is negligible | use default DPM law/material in `11b` |
| any child is unstable | do not combine that feature in setup `11`; retain it as diagnostic evidence |

## 8. Research basis and limitations

- Rizaldy et al. report that higher inlet velocity and liquid loading increase liquid-film entrainment and carryover in geothermal cyclone separators ([local synthesis](../../CFD_wiki/wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md)).
- Mondal and Sharma use DPM for gas-core droplets and EWF for wall liquid, with deposition and entrainment treated as separate coupled processes ([local Fluent setup pattern](../../CFD_wiki/wiki/setups/vertical-tube-annular-flow-fluent-dpm-ewf-2024.md)).
- Fluent provides standard EWF/DPM impingement options and UDF hooks for wall boundary behavior, custom laws, and particle properties ([EWF controls](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_ewf_sec_bound.html); [DPM UDF macros](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_udf/flu_udf_DPMDEFINE.html)).

The annular-flow evidence is air-water in a tube, not geothermal steam-brine in this BOC separator. Reuse the model decomposition and diagnostics, not its correlation constants as geothermal validation.

## 9. Links

- [08c inlet-velocity sensitivity](../active/08c-purnanto-parity-inlet-velocity-sensitivity.md)
- [09c two-way DPM coupling](../past/archived/09c-dpm-ewf-wall-film-reentrainment.md)
- [11 combined wall-film and DPM plan](11-combined-wallfilm-dpm-plan.md)
- [separator efficiency methods](../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)
