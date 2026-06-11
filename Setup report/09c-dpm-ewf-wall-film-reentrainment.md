# Two-Way DPM Coupling Setup Report

Legacy filename note:

- this file keeps the `09c-dpm-ewf-wall-film-reentrainment.md` filename for sequence continuity;
- its current branch role is **not** the old wall-film / re-entrainment jump;
- it is now the smaller two-way DPM coupling branch.

## 1. Purpose

Define setup `09c` as the third `09` branch after `09a` and `09b`.

This branch answers:

```text
does physically meaningful droplet loading feed back strongly enough
into the carrier flow that one-way DPM is no longer sufficient?
```

This is the first branch in family `09` that allows DPM to influence the continuous phase.

## 2. Parent Authority

Parent branch rule:

- inherit from the latest accepted simpler branch;
- for `09c`, that parent should normally be the accepted `09b` state, or `09a` if `09b` was judged unnecessary.

That means `09c` should inherit the accepted:

- mesh;
- carrier-field model;
- DPM droplet set;
- step limits;
- particle count;
- wall-fate interpretation;
- stochastic setting decision.

## 3. Dynamic Setting Rule

Settings in `09c` must be changed dynamically to fit the latest accepted findings from `08b` and the current simpler branches.

Only one intentional uncertainty should be changed here:

```text
continuous-phase feedback from droplet loading
```

Do not mix this branch with:

- turbulence-model upgrade;
- Eulerian wall film;
- re-entrainment modeling;
- unrelated outlet or geometry changes.

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | inherit accepted parent |
| General | Time | inherit accepted parent unless coupling stability requires a documented change |
| Models > Multiphase | Model | inherit accepted parent |
| Models > Viscous | Turbulence | inherit accepted parent |
| Models > Energy | Energy | inherit accepted parent |
| Models > Discrete Phase | DPM | `On` with continuous-phase interaction enabled |

Interpretation:

- this branch is still a DPM branch, not a wall-film branch;
- use coupling only after one-way DPM is already stable enough to compare against;
- any time-mode change must be justified as a coupling-stability requirement, not added casually.

## 5. What Changes In This Branch

Change only the DPM coupling state and the minimum supporting settings required to make that comparison meaningful.

The key requirement is:

```text
use a physically meaningful droplet mass loading
```

Do not use arbitrary tiny injection flow rates and then claim coupled realism.

Required branch-specific inputs:

1. droplet mass loading basis;
2. droplet-size set used for the coupled comparison;
3. coupling-related iteration or timestep plan if needed.

## 6. Outputs To Record

Record at minimum:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. coupled vs one-way carrier-field difference
6. coupled vs one-way carryover interpretation difference
7. any new monitor needed to judge coupling stability

## 7. Success Signal

`09c` is successful if it clearly shows one of these:

1. two-way coupling does not materially change the conclusion, so one-way DPM remains adequate for this project stage;
2. two-way coupling does materially change the carrier field or carryover result, so later DPM-based claims must account for coupling.

## 8. Failure Signal

`09c` should not be treated as successful if:

1. droplet loading was not physically justified;
2. the coupling run becomes unstable before a meaningful comparison is possible;
3. the branch accidentally mixes in other major changes;
4. the real next uncertainty turns out to be wall-film persistence rather than coupling.

If the unresolved issue after `09c` is wall persistence or liquid return from walls, move that work into the future `10` family rather than extending `09c`.
