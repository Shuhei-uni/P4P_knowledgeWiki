# DPM Tracking Cleanup Setup Report

## 1. Purpose

Define setup `09a` as the first controlled DPM branch after the accepted setup `08b` baseline.

This branch answers:

```text
can one-way DPM on the accepted carrier field produce
bounded escaped / trapped / incomplete trends?
```

This is the first `09` branch because it makes the smallest physics jump:

- keep the accepted carrier field;
- keep one-way DPM;
- change only the DPM tracking controls needed to reduce or bound incomplete tracks.

## 2. Parent Authority

Parent branch rule:

- inherit from the latest accepted simpler branch;
- at first use, that parent will normally be setup `08b`;
- after later reruns, this branch must inherit any accepted updates to mesh, residual gate, pressure reporting, accepted droplet set, or accepted DPM defaults.

Do **not** blindly reuse every original setup `08b` setting if later verification work has already replaced it.

## 3. Dynamic Setting Rule

Settings in `09a` must be changed dynamically to fit findings from the current accepted setup state.

Examples:

- if setup `08b` mesh verification selects a new production mesh, `09a` must use that mesh;
- if setup `08b` acceptance work changes the accepted pressure-outlet treatment, `09a` inherits that;
- if an earlier DPM check shows a certain step-length factor or particle count is unusable, `09a` should not keep it as a default just because it appeared in an older branch.

Only one uncertainty should be tested intentionally in this branch:

```text
DPM tracking completeness and robustness
```

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | inherit accepted parent |
| General | Time | inherit accepted parent |
| Models > Multiphase | Model | inherit accepted parent |
| Models > Viscous | Turbulence | inherit accepted parent |
| Models > Energy | Energy | inherit accepted parent |
| Models > Discrete Phase | DPM | `On` after accepted carrier-field state exists |

Interpretation:

- keep one-way DPM only;
- do not turn on continuous-phase source feedback here;
- do not add wall film here;
- do not change turbulence model here unless the accepted parent already changed it before this branch begins.

## 5. Core Inputs To Inherit

Unless the accepted parent has changed them, inherit:

- geometry;
- split-inlet definition;
- material values;
- outlet role;
- gravity direction;
- accepted production mesh;
- accepted continuous-phase numerics.

## 6. Primary DPM Controls To Test

Test only the DPM robustness controls needed to interpret droplet fate:

1. maximum tracking steps;
2. step-length factor;
3. particle count per injection;
4. justified droplet-size set.

Keep these fixed unless this branch is explicitly testing them:

- injection location;
- particle density;
- outlet escape definition;
- wall-fate interpretation.

## 7. Minimum Droplet Set

Use the latest accepted droplet set from the parent evidence.

If no narrower set has yet been accepted, start with:

- `5 um`
- `10 um`
- `40-41 um`

Add other sizes only if they answer a specific question.

## 8. Outputs To Record

For each tested size, record:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. tracking settings used
6. whether the result is strong enough for carryover interpretation

## 9. Success Signal

`09a` is successful if:

- incomplete fractions reduce materially, or
- incomplete fractions remain but are bounded well enough that DPM can still be used as a controlled diagnostic.

## 10. Failure Signal

`09a` is not enough if:

1. incomplete tracks remain too large to interpret;
2. the droplet-fate result changes too much with reasonable tracking-control adjustments;
3. deterministic one-way DPM still leaves turbulence-driven dispersion as the dominant unresolved question;
4. physically meaningful droplet loading seems likely to affect the carrier flow itself.

If that happens:

- move to `09b` for stochastic / turbulence sensitivity;
- move to `09c` only after one-way DPM settings are stable enough to justify coupling.
