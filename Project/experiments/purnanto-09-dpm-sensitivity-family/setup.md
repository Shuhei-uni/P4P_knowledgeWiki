> **Retired source:** Setups/past/archived/09-multiphase-separator-sensitivity-family.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Multiphase Separator Sensitivity Family

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09` |
| Lifecycle | `archived` |
| Role | sensitivity-family parent |
| Parent setup | [08b](../purnanto-08b-parity-split-inlet/setup.md) |
| Evidence-use label | family definition; child reports carry numerical evidence |
| Outcome | retained family definition |
| Linked report | none |

## 1. Purpose

Define setup family `09` as the first controlled physics-escalation layer after setup `08b`.

This family exists only after setup `08b` has become an accepted baseline candidate under the project roadmap:

- [08b-purnanto-parity-split-inlet-rebuild.md](../purnanto-08b-parity-split-inlet/setup.md)
- [Project state and next decision](../../index.md)

This parent report is **not** a run definition by itself.

It exists to organize three smaller child branches that each retire one uncertainty at a time:

- [09a-dpm-split-inlet-carryover.md](../purnanto-09a-dpm-deterministic-carryover/setup.md)
- [09b-rsm-dpm-split-inlet-accuracy.md](../purnanto-09b-dpm-stochastic-dispersion/setup.md)
- [09c two-way DPM coupling](../purnanto-09c-two-way-dpm-coupling/setup.md)

Sequence note:

- the `09b` and `09c` filenames are legacy sequence holders;
- their branch roles are redefined below to match the current roadmap;
- later wall-film and re-entrainment work should move into a future `10` family rather than being forced back into `09`.

## 2. Family Interpretation

Treat this `09` parent as:

```text
post-08b controlled DPM sensitivity family
```

Do not run `09` directly.
Run only `09a`, `09b`, or `09c`.

## 3. Gate Before Using Family 09

Do not activate any `09` child unless setup `08b` has already passed the current project gate for:

1. baseline acceptance;
2. minimum monitor stability;
3. mesh verification at the needed claim level;
4. enough baseline DPM evidence to justify physics escalation.

If setup `08b` is still only `diagnostic`, stop and repair `08b` first.

Current working status:

- `User-reported`: setup `08b` has been done and setup `08c` is now running;
- `User-reported`: PyFluent automation for the full DPM injection calculation path is proving difficult;
- `User-specified`: proceed with manual Fluent DPM runs for `09a` and `09b`, then paste or report the fate-count results so brief output sections can be added to the corresponding setup reports.

Interpretation:

- manual execution is acceptable for family `09` if the continuous field, DPM model settings, injection values, boundary fates, tracking controls, and fate-count outputs are recorded explicitly;
- automation status should not block `09a` / `09b` unless manual readback cannot verify the applied settings.

## 4. Dynamic Inheritance Rule

All `09` child branches inherit from the **latest accepted simpler branch**, not blindly from the original setup `08b` text.

This means:

- geometry, mesh, numerics, and DPM controls must be updated to the latest accepted findings;
- if a prior branch changes a production mesh, accepted timestep, accepted wall fate, accepted DPM step limit, or accepted particle count, the next branch should inherit that updated setting unless the new branch is explicitly testing that setting;
- setup `08b` remains the branch origin, but it is not the frozen authority for every later setting.

Practical rule:

```text
inherit the last accepted branch state,
change only the one new uncertainty being tested,
and record every inherited setting that was updated dynamically.
```

## 5. Shared Scope

Unless a child branch explicitly changes the scope, all `09` branches remain focused on:

- steam-side liquid carryover;
- droplet-fate interpretation;
- whether added DPM realism changes the project conclusion.

Still out of scope here:

- brine-outlet reconstruction;
- lower-water initialization;
- wall-film and re-entrainment as active model layers inside family `09`.

## 6. Child Branch Logic

### `09a` One-Way DPM Tracking Cleanup

Use [09a-dpm-split-inlet-carryover.md](../purnanto-09a-dpm-deterministic-carryover/setup.md) when the main question is:

```text
can one-way DPM on the accepted carrier field produce bounded,
interpretable escaped/trapped/incomplete trends?
```

Main purpose:

- reduce or bound incomplete tracks;
- clean up DPM tracking controls before stronger DPM claims are made.

### `09b` One-Way DPM Stochastic / Turbulence Sensitivity

Use [09b-rsm-dpm-split-inlet-accuracy.md](../purnanto-09b-dpm-stochastic-dispersion/setup.md) when the main question is:

```text
does one-way DPM carryover change materially when turbulence-driven
particle dispersion is enabled or bounded?
```

Main purpose:

- compare deterministic and stochastic particle-transport interpretations;
- keep the same accepted carrier field while changing only particle-dispersion treatment.

### `09c` Two-Way DPM Coupling

Use the [09c two-way DPM coupling setup](../purnanto-09c-two-way-dpm-coupling/setup.md) when the main question is:

```text
does physically meaningful droplet loading feed back strongly enough
into the carrier flow that one-way DPM is no longer sufficient?
```

Main purpose:

- turn on continuous-phase source feedback only after one-way DPM is stable;
- test coupling as its own uncertainty, without wall film in the same branch.

## 7. Recommendation Order

Recommended order of execution:

1. `09a` first.
2. `09b` second if one-way DPM is stable enough to compare dispersion treatment.
3. `09c` third only after one-way DPM settings and droplet loading are defensible.

Do not skip straight to `09c` unless the project already has a strong reason to believe one-way DPM is insufficient.

Manual-output rule:

- record `09a` deterministic DPM results before changing turbulent dispersion;
- record `09b` stochastic results in the same table structure as `09a` so differences are attributable to dispersion treatment rather than post-processing format;
- keep raw Fluent screenshots, text reports, or copied console/table values outside this parent report and summarize only the branch-level output in the child setup report.

## 8. What Is Deferred Beyond Family 09

Create a later `10` family for:

1. wall-fate sensitivity before film;
2. Eulerian wall film;
3. re-entrainment or film stripping;
4. any transient wall-film interpretation that needs its own acceptance gate.
