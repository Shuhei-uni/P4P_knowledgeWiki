> **Retired source:** Setups/past/reported/09a-dpm-split-inlet-carryover.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# DPM Tracking Cleanup Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09a` |
| Lifecycle | `reported` |
| Role | deterministic one-way DPM carryover baseline |
| Parent setup | [08b](../../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) |
| Evidence-use label | DPM trajectory diagnostic; inherited parent evidence |
| Outcome | needs follow-up |
| Linked report | [09a results](results.md) |

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
- at first use, that parent will normally be the completed setup `08b` carrier field;
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
DPM unresolved-fate interpretation and robustness
```

Current execution note:

- `User-reported`: setup `08b` has been done and setup `08c` is running;
- `User-specified`: run `09a` manually in Fluent because automating the full DPM injection/fate-count workflow through PyFluent is currently too difficult;
- `Assumed`: use the solved `08b` continuous field and already staged DPM setup as the starting state unless a newer accepted `08c` carrier field is explicitly promoted later.

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

Because setup `09a` is now being used to continue the same one-way DPM tracking question already sampled in setup `08b`, inherit the recovered setup `08b` injection bins first rather than inventing a new `5/10/40 um` set.

Recovered setup `08b` DPM inventory:

| Injection name | Diameter | Represented mass flow | Share of recovered DPM mass |
|---|---:|---:|---:|
| `injection-5-micron` | `5.63 um` | `0.19 kg/s` | `0.16%` |
| `injection-28-micron` | `28.14 um` | `0.78 kg/s` | `0.67%` |
| `injection-56-micron` | `56.27 um` | `0.97 kg/s` | `0.83%` |
| `injection-112-micron` | `112.54 um` | `1.95 kg/s` | `1.67%` |
| `injection-168-micron` | `168.81 um` | `1.95 kg/s` | `1.67%` |
| `injection-348-micron` | `348.88 um` | `23.38 kg/s` | `20.00%` |
| `injection-562-micron` | `562.70 um` | `29.23 kg/s` | `25.00%` |
| `injection-844-micron` | `844.06 um` | `29.23 kg/s` | `25.00%` |
| `injection-1631-micron` | `1631.84 um` | `29.23 kg/s` | `25.00%` |

First manual / diagnostic pass:

- `5.63 um` if using the extracted setup `08b` first injection bin, or `5 um` as the rounded manual label
- `28.14 um`
- `56.27 um`
- `112.54 um`
- `168.81 um`
- `348.88 um`

Then add the larger recovered bins, `562.70 um`, `844.06 um`, and `1631.84 um`, if the active six-bin pass becomes interpretable or if coarse-bin escape must be ruled out explicitly.

Separate manual sensitivity labels such as `10 um` may still be useful, but they should be logged as added project diagnostic points, not as part of the recovered setup `08b` injection inventory.

## 8. Outputs To Record

For each tested size, record:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. tracking settings used
6. whether the result is strong enough for carryover interpretation

## 8.1 Manual Fluent Procedure For 09a

Starting point:

- open the solved setup `08b` carrier case/data;
- confirm setup `08c` is not being mixed into this branch unless it has been deliberately selected as the new accepted parent;
- confirm DPM is enabled and one-way only;
- confirm the injection setup matches the setup `08b` DPM basis before running any tracks.

Click-by-click procedure:

1. Save a copy of the solved parent case/data with a `09a` run label.
2. Go to `Models > Discrete Phase` and confirm:
   - DPM is `On`;
   - interaction with continuous phase is `Off` for one-way tracking;
   - stochastic turbulent dispersion is `Off`;
   - wall film is `Off`.
3. Go to `Boundary Conditions` and confirm DPM fates:
   - steam outlet = `escape`;
   - intended bottom/liquid collection boundary = `trap`;
   - ordinary separator walls = the inherited parent wall fate, or `reflect` if this branch is testing carryover without counting every wall hit as permanent separation.
4. Go to `Discrete Phase > Injections` and create or verify one surface injection per droplet diameter.
5. For each injection, record:
   - injection name;
   - surface used;
   - diameter;
   - particle material and density;
   - represented mass flow;
   - number of streams or particles;
   - velocity treatment, especially whether carrier-flow/fixed components are used.
6. Track the deterministic injection.
7. Open the particle summary / DPM report and copy the counts for `injected`, `escaped`, `trapped`, and `incomplete`.
8. If incomplete counts are large, do not automatically treat that as an error. For this Purnanto-style branch, first record incomplete as an unresolved long-residence / likely wall-associated fate category. Only change tracking controls if the goal is to bound how much of that unresolved category could later escape.
9. Save the final `09a` case/data and preserve the output values for the brief report table below.

Minimum inherited run set:

| Diameter | Reason | Required for first manual report |
|---:|---|---|
| `5.63 um` | recovered setup `08b` finest active bin | yes |
| `28.14 um` | recovered setup `08b` active bin | yes |
| `56.27 um` | recovered setup `08b` active bin | yes |
| `112.54 um` | recovered setup `08b` active bin | yes |
| `168.81 um` | recovered setup `08b` active bin | yes |
| `348.88 um` | recovered setup `08b` active bin | yes |

Optional after the first pass:

- add the remaining recovered setup `08b` bins: `562.70 um`, `844.06 um`, and `1631.84 um`;
- add `10 um` or `14.2 um` only as separate project diagnostic points if they answer a specific comparison question.

## 8.2 Inherited Setup 08b DPM Results

The setup `08b` report already contains the same one-way DPM tracking problem that setup `09a` is intended to clean up. Import the relevant result here as the starting `09a` evidence rather than treating `09a` as a blank new DPM setup.

Parent evidence:

- source report: [08b-purnanto-parity-split-inlet-rebuild.md](../../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md)
- carrier field: saved `5000`-iteration split-inlet field from setup `08b`
- DPM model: one-way, deterministic, stochastic tracking off, random eddy off
- tracking controls inherited from `08b`: `max_num_steps = 10000`, `step-length-factor = 5`
- active sampled injections: six recovered bins from `5.63 um` through `348.88 um`
- omitted recovered bins in that pass: `562.70 um`, `844.06 um`, `1631.84 um`

Observed one-injection-at-a-time `dpm-sample` result from setup `08b`:

| Diameter | Injected | Escaped | Trapped | Incomplete | Tracking controls | Interpretation |
|---:|---:|---:|---:|---:|---|---|
| `5.63 um` | `2170` | `8` | `0` | `2162` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | only active bin with reported completed steam-line escape in the sampled setup `08b` pass |
| `28.14 um` | `2170` | `0` | `0` | `2170` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | all sampled tracks reported incomplete |
| `56.27 um` | `2170` | `0` | `0` | `2170` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | all sampled tracks reported incomplete |
| `112.54 um` | `2170` | `0` | `0` | `2170` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | all sampled tracks reported incomplete |
| `168.81 um` | `2170` | `0` | `0` | `2170` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | all sampled tracks reported incomplete |
| `348.88 um` | `2170` | `0` | `0` | `2170` | deterministic; `max_num_steps = 10000`; `step-length-factor = 5` | all sampled tracks reported incomplete |

Aggregate over the six inherited setup `08b` sample passes:

| Quantity | Value |
|---|---:|
| Total tracked | `13020` |
| Total escaped | `8` |
| Total trapped | `0` |
| Total incomplete | `13012` |

Report these derived values once counts are known:

- `escape fraction = escaped / injected`
- `deterministic collection estimate = 1 - escaped / injected`
- `incomplete fraction = incomplete / injected`
- if incomplete is not small, report an optimistic/pessimistic bracket instead of one efficiency value.

Inherited setup `08b` deterministic interpretation:

- rounded `5 um` / extracted `5.63 um` bin: escaped fraction `8 / 2170 = 0.37%`; incomplete fraction `2162 / 2170 = 99.63%`;
- six-bin aggregate: escaped fraction `8 / 13020 = 0.061%`; incomplete fraction `13012 / 13020 = 99.94%`;
- because almost all particles are incomplete, these values should be interpreted with a Purnanto-style unresolved-fate assumption rather than forced to completion. The working assumption is that many incomplete particles are long-residence particles near walls or recirculating paths that may eventually settle to the bottom or later escape by entrainment; report them as an unresolved bracket, not as a tracking failure by itself.

## 8.3 Additional Manual Diagnostic Points

The following result was reported separately as a manual deterministic sample. It is useful for the setup `09a` cleanup story, but it is not part of the recovered setup `08b` injection inventory above unless the matching injection is explicitly created as a project diagnostic point.

| Diameter | Injected | Escaped | Trapped | Incomplete | Tracking controls | Interpretation |
|---:|---:|---:|---:|---:|---|---|
| `10 um` | `2170` | `1` | `TBD` | `2169` | deterministic sample trajectory run; exact tracking controls not yet recorded | preliminary only; incomplete fraction `99.95%`, so not interpretable as efficiency |

## 8.4 Findings So Far

Setup `09a` establishes the deterministic one-way DPM baseline inherited from setup `08b`.

Main findings:

- deterministic tracking produces very little completed steam-outlet escape in the sampled bins;
- the only recovered setup `08b` active bin with completed escape is `5.63 um`, with `8 / 2170` escaped;
- recovered bins from `28.14 um` through `348.88 um` produced no completed escape or trap in the sampled deterministic pass;
- the aggregate six-bin deterministic pass is dominated by incomplete / unresolved fate: `13012 / 13020`;
- the separate `10 um` diagnostic point also remains almost entirely unresolved: `2169 / 2170` incomplete.

Interpretation:

- incomplete particles should be carried as unresolved long-residence / likely wall-associated particles, consistent with the Purnanto-style assumption;
- setup `09a` does not prove high carryover or high collection by itself;
- setup `09a` provides the deterministic reference needed to judge whether stochastic dispersion in setup `09b` changes completed escape counts.

Recommended next checks from `09a`:

1. Keep the deterministic `09a` table as the baseline; do not spend time trying to eliminate incomplete particles unless a supervisor specifically asks for a tracking-completion sensitivity.
2. Use setup `09b` to test whether turbulent dispersion changes the escaped fraction for the same carrier field and same wall-fate assumptions.
3. If a report needs a Purnanto-style optimistic efficiency estimate, state the assumption explicitly: incomplete particles are treated as separated / non-escaped unless later entrainment evidence proves otherwise.
4. If a conservative carryover bound is needed, report escaped count separately and keep incomplete as unresolved rather than folding it into one efficiency number.

## 9. Success Signal

`09a` is successful if:

- escaped, trapped, and incomplete fractions are recorded consistently by droplet bin;
- incomplete particles are explicitly treated as unresolved long-residence / likely wall-associated fate rather than silently counted as either separated or escaped;
- the escaped fraction can still be compared across deterministic and stochastic settings as a controlled diagnostic.

## 10. Failure Signal

`09a` is not enough if:

1. incomplete particles are mixed silently into trapped or escaped totals without a stated assumption;
2. the droplet-fate result changes too much with reasonable stochastic or wall-fate settings to support a bounded trend;
3. deterministic one-way DPM still leaves turbulence-driven dispersion as the dominant unresolved question;
4. physically meaningful droplet loading seems likely to affect the carrier flow itself.

If that happens:

- move to `09b` for stochastic / turbulence sensitivity;
- move to `09c` only after one-way DPM settings are stable enough to justify coupling.
