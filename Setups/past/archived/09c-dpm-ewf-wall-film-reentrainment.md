# Two-Way DPM Coupling Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09c` |
| Lifecycle | `archived` |
| Role | two-way DPM coupling branch |
| Parent setup | [09b](../reported/09b-rsm-dpm-split-inlet-accuracy.md) |
| Evidence-use label | preliminary two-way-coupling diagnostic; not converged |
| Outcome | needs follow-up |
| Linked report | [09c post-simulation analysis](../../reports/09c/results.md) |

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

Current implementation note:

- `Implemented 2026-07-07`: because `09a` and `09b` are still being gathered manually, the first concrete `09c` case file is derived directly from the accepted `08b`-style split-inlet case file requested by the user:
  `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5`
- this is acceptable as a setup-definition branch as long as the inherited basis is stated clearly and no extra physics is mixed in silently.

## 3. Implemented Case Definition

| Item | Value |
|---|---|
| Setup order | `09c` |
| Branch role | case-only two-way DPM coupling derivative |
| Build date | `2026-07-07` |
| Fluent host | `server 3` only |
| Fluent version | `Ansys Fluent 2024 R2` |
| Source case | `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5` |
| Output case | `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-09c-two-way-dpm-coupled.cas.h5` |
| Initialization / run state | not initialized, not iterated, no `.dat.h5` written |
| Inherited inlet topology | split `Mass-Flow Inlet` pair: `liquidinlet` + `steaminlet` |
| Inherited outlet topology | `pressure_outlet.steamoutlet` |
| Inherited wall DPM fates | `wall = reflect`, `bottom = trap`, inlets/outlet = `escape` |
| Inherited injection payload | 6 active `surface` injections on `steaminlet`, total represented liquid loading `29.22 kg/s` |

## 4. What Was Actually Changed In The Built 09c Case

Only the global DPM continuous-phase feedback controls were changed from the source case.

Readback-confirmed `09c` changes on server `3`:

| Panel | Setting | Source case | `09c` case |
|---|---|---:|---:|
| `Models > Discrete Phase > Interaction` | `Interaction with Continuous Phase` | `Off` | `On` |
| `Models > Discrete Phase > Interaction` | `Update DPM Sources Every Flow Iteration` | `Off` | `On` |
| `Models > Discrete Phase > Interaction` | `DPM Iteration Interval` | `10` after enabling branch default | `1` |

Nothing else was intentionally changed in this first `09c` build:

- no inlet mass-flow changes;
- no stochastic dispersion change;
- no turbulence-model change;
- no wall-film model activation;
- no re-entrainment or stripping model activation;
- no injection-surface rebinding;
- no post-setup initialization or iterations.

Observed source-case note:

- the actual `TwoPhaseInletV2(Purnanto).cas.h5` file used for this build does **not** carry the full 9-size / `116.91 kg/s` payload described in the broader `08b` branch note;
- on server `3`, the loaded source case read back 6 active injections:
  `5`, `28`, `56`, `112`, `168`, and `348` micron;
- the represented total injected loading in that exact source case is `29.22 kg/s`;
- treat this as the authoritative inherited DPM payload for the built `09c` case unless the source case is replaced later.

## 5. Dynamic Setting Rule

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

For the currently built case file, that change budget was respected.

## 6. Model Stack

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

Implemented readback note:

- in the current case file, the `DPM` model was already active and all inherited injections remained present after the interaction toggle was changed;
- the interaction branch read back successfully as:
  `enabled = true`, `update_sources_every_iteration = true`, `iteration_interval = 1`.

## 7. What Changes In This Branch

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

For the present case definition, the inherited droplet basis is:

- same 6-size injected loading already carried by the exact source case used to build `09c`;
- all injections remain `surface` injections on `steaminlet`;
- total represented injected liquid mass flow reads back as `29.22 kg/s`.

## 8. Outputs To Record

Record at minimum:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. coupled vs one-way carrier-field difference
6. coupled vs one-way carryover interpretation difference
7. any new monitor needed to judge coupling stability

## 9. Success Signal

`09c` is successful if it clearly shows one of these:

1. two-way coupling does not materially change the conclusion, so one-way DPM remains adequate for this project stage;
2. two-way coupling does materially change the carrier field or carryover result, so later DPM-based claims must account for coupling.

## 10. Failure Signal

`09c` should not be treated as successful if:

1. droplet loading was not physically justified;
2. the coupling run becomes unstable before a meaningful comparison is possible;
3. the branch accidentally mixes in other major changes;
4. the real next uncertainty turns out to be wall-film persistence rather than coupling.

If the unresolved issue after `09c` is wall persistence or liquid return from walls, move that work into the future `10` family rather than extending `09c`.
