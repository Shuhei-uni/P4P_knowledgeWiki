# DPM Stochastic / Turbulence Sensitivity Setup Report

Legacy filename note:

- this file keeps the `09b-rsm-dpm-split-inlet-accuracy.md` filename for sequence continuity;
- its current branch role is **not** the old `RSM-DPM` jump;
- it is now the smaller one-way DPM stochastic / turbulence sensitivity branch.

## 1. Purpose

Define setup `09b` as the second `09` branch after `09a`.

This branch answers:

```text
does one-way DPM carryover interpretation change materially
when turbulence-driven particle dispersion is enabled or bounded?
```

This branch exists because deterministic one-way DPM may be too clean or too optimistic for fine droplets, but that uncertainty should be tested before changing the whole carrier-flow model.

## 2. Parent Authority

Parent branch rule:

- inherit from the latest accepted simpler branch;
- for `09b`, that parent should normally be the accepted `09a` state, not raw setup `08b`.

That means `09b` should inherit the accepted:

- mesh;
- carrier-field state;
- droplet set;
- DPM step limits;
- particle count;
- wall-fate interpretation.

## 3. Dynamic Setting Rule

Settings in `09b` must be changed dynamically to fit the latest accepted findings from `08b` and `09a`.

Only one intentional uncertainty should be changed here:

```text
particle-dispersion treatment inside one-way DPM
```

Do not silently re-open other uncertainties in the same branch.

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | inherit accepted parent |
| General | Time | inherit accepted parent |
| Models > Multiphase | Model | inherit accepted parent |
| Models > Viscous | Turbulence | inherit accepted parent carrier model |
| Models > Energy | Energy | inherit accepted parent |
| Models > Discrete Phase | DPM | `On` |

Interpretation:

- keep one-way DPM;
- keep the accepted carrier-flow model unchanged;
- do not upgrade to `RSM` in this branch unless `RSM` was already accepted earlier as part of the parent state;
- do not add wall film here;
- do not add coupling here.

## 5. What Changes In This Branch

Change only the DPM particle-dispersion treatment needed for sensitivity testing.

Typical comparisons:

1. deterministic vs `DRW`;
2. one accepted stochastic configuration vs another bounded alternative if needed.

Keep fixed unless directly justified:

- droplet sizes;
- injection location;
- particle density;
- step limit;
- step-length factor;
- particle count;
- wall-fate interpretation.

## 6. Recommended Comparison Set

Use the smallest set that answers the question.

Recommended start:

- `5 um` deterministic vs `5 um` stochastic;
- `10 um` deterministic vs `10 um` stochastic.

Add `40-41 um` only if you need to show whether larger droplets are insensitive to the same change.

## 7. Outputs To Record

For each compared case, record:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. particle-dispersion setting
6. carryover interpretation difference relative to deterministic one-way DPM

## 8. Success Signal

`09b` is successful if it shows one of these clearly:

1. stochastic dispersion does not materially change the branch conclusion, so deterministic one-way DPM is adequate;
2. stochastic dispersion does change the conclusion enough that the uncertainty must be carried forward explicitly.

## 9. Failure Signal

`09b` is not enough if:

1. the result is still dominated by uncertain droplet loading rather than dispersion treatment;
2. one-way DPM still appears structurally insufficient because particles should feed back into the carrier flow;
3. wall behavior, not dispersion, now looks like the dominant unresolved mechanism.

If that happens:

- move to `09c` if coupling is the next real uncertainty;
- defer wall-film and re-entrainment questions to the later `10` family.
