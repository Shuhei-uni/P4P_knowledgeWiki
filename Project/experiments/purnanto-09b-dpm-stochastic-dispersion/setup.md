> **Retired source:** Setups/past/reported/09b-rsm-dpm-split-inlet-accuracy.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# DPM Stochastic / Turbulence Sensitivity Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09b` |
| Lifecycle | `reported` |
| Role | stochastic DPM and turbulence sensitivity |
| Parent setup | [09a](../purnanto-09a-dpm-deterministic-carryover/setup.md) |
| Evidence-use label | stochastic DPM trajectory diagnostic |
| Outcome | needs follow-up |
| Linked report | [09b results](results.md) |

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
- for `09b`, that parent should normally be the accepted manual `09a` deterministic DPM state, not raw setup `08b`.

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

Current execution note:

- `User-specified`: run `09b` manually after the `09a` deterministic fate-count report is available;
- `User-specified`: do not wait for PyFluent automation if manual Fluent readback can verify the DPM settings and output counts;
- `Assumed`: the carrier field remains the same solved parent field used for `09a`; if setup `08c` becomes the accepted parent before `09b`, record that parent switch explicitly before comparing outputs.

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

## 7.1 Manual Fluent Procedure For 09b

Starting point:

- use the saved `09a` manual case/data after deterministic DPM setup has been verified;
- do not change geometry, mesh, continuous-field solution, inlet mass flows, outlet pressure, droplet diameters, injection surfaces, represented mass flow, wall fates, step limits, or particle count unless the `09a` report proved one of those settings was unusable.

Click-by-click procedure:

1. Save a new copy of the accepted `09a` case/data with a `09b` run label.
2. Go to `Models > Discrete Phase` and keep DPM one-way.
3. Enable turbulent dispersion / stochastic tracking for the DPM comparison case.
4. Use the same maximum tracking steps and step-length factor accepted in `09a`.
5. Go to `Discrete Phase > Injections` and verify each injection still has the same:
   - diameter;
   - surface;
   - material and density;
   - represented mass flow;
   - number of streams or particles.
6. For each selected diameter, track the stochastic case and record `injected`, `escaped`, `trapped`, and `incomplete`.
7. Repeat stochastic tracking if Fluent's random-walk result varies noticeably between tries; record the number of tries or repeats used.
8. Compare against the matching `09a` deterministic row, not against a different parent case.
9. Save the final `09b` case/data and preserve the output values for the brief report table below.

Minimum comparison set:

| Diameter | Comparison | Required for first manual report |
|---:|---|---|
| `5 um` | deterministic `09a` vs stochastic `09b` | yes |
| `10 um` | deterministic `09a` vs stochastic `09b` | yes |
| `40-41 um` | deterministic `09a` vs stochastic `09b` | optional unless larger droplets showed sensitivity in `09a` |

Recommended first stochastic settings:

| Test label | Stochastic tracking | Number of tries | Random eddy lifetime | Purpose |
|---|---|---:|---|---|
| `09b-DRW10-eddy-life-off` | on / DRW | `10` | off | first bounded comparison against deterministic `09a` |
| `09b-DRW10-eddy-life-on` | on / DRW | `10` | on | second comparison to test whether eddy lifetime treatment changes fate counts |

Interpretation rule:

- run the `random eddy lifetime off` case first;
- then turn `random eddy lifetime on` without changing any injection, wall fate, particle count, step limit, or carrier-field setting;
- treat incomplete particles as an unresolved long-residence / likely wall-associated fate category inherited from the Purnanto-style DPM interpretation;
- compare stochastic settings mainly by escaped count/fraction and by how the unresolved category changes, without forcing incomplete particles to be either separated or escaped.

## 7.2 Brief Output Report Template

Fill this after the manual run.

| Diameter | Dispersion setting | Injected | Escaped | Trapped | Incomplete | Difference vs 09a | Interpretation |
|---:|---|---:|---:|---:|---:|---|---|
| `5 um` / nearest recovered bin `5.63 um` | `DRW stochastic, 10 tries, random eddy lifetime assumed off` | `21700` | `2722` | `15` | `18963` | escape fraction much higher than deterministic `09a`; incomplete still dominant | diagnostic only; stochastic dispersion materially changes completed escape count, but incomplete fraction remains too high for efficiency interpretation |
| `10 um` project diagnostic point | `DRW stochastic, 10 tries, random eddy lifetime assumed off` | `21700` | `3370` | `106` | `18224` | escape fraction higher than both deterministic `10 um` and stochastic `5 um` | unexpected ordering; treat as stochastic/tracking sensitivity, not proof that `10 um` physically carries over more |
| `5 um` / nearest recovered bin `5.63 um` | `DRW stochastic, 10 tries, random eddy lifetime on` | `21700` | `2312` | `19` | `19369` | escaped count lower than eddy-lifetime-off case; counts close exactly | random eddy lifetime changes results but keeps incomplete as the dominant unresolved-fate category |
| `10 um` project diagnostic point | `DRW stochastic, 10 tries, random eddy lifetime on` | `21700` | `2943` | `85` | `18672` | escaped count lower than eddy-lifetime-off case; counts close exactly | random eddy lifetime changes results but keeps `10 um` escaped fraction above `5 um`; still interpret with unresolved-fate bracket |
| `28.14 um` recovered bin | `DRW stochastic, 10 tries, random eddy lifetime off` | `21700` | `0` | `6` | `21694` | no completed escape; tiny completed trap count | supports transition from completed fine-droplet escape to unresolved/coarser-bin residence |
| `28.14 um` recovered bin | `DRW stochastic, 10 tries, random eddy lifetime on` | `21700` | `0` | `9` | `21691` | no completed escape; tiny completed trap count | random eddy lifetime does not create steam-outlet escape for this recovered bin |
| `40 um` / coarse diagnostic point | `DRW stochastic, 10 tries, random eddy lifetime off` | `21700` | `0` | `0` | `21700` | no completed fate under the same stochastic try count | all sampled tracks remain unresolved/incomplete; no completed carryover observed |
| `40 um` / coarse diagnostic point | `DRW stochastic, 10 tries, random eddy lifetime on` | `21700` | `0` | `0` | `21700` | no completed fate under the same stochastic try count | all sampled tracks remain unresolved/incomplete; random eddy lifetime did not create completed escape/trap fate |

Report these derived values once counts are known:

- `escape fraction = escaped / injected`
- `stochastic collection estimate = 1 - escaped / injected`
- `change in escape fraction vs 09a`
- `change in incomplete fraction vs 09a`
- if stochastic repeats vary, report the range rather than a single number.

Preliminary `DRW10` interpretation:

- `5 um` / nearest recovered `5.63 um`: escaped fraction `2722 / 21700 = 12.54%`; trapped fraction `15 / 21700 = 0.069%`; incomplete fraction `18963 / 21700 = 87.39%`.
- `10 um` project diagnostic point: escaped fraction `3370 / 21700 = 15.53%`; trapped fraction `106 / 21700 = 0.49%`; incomplete fraction `18224 / 21700 = 83.98%`.
- `28.14 um` recovered bin: escaped fraction `0 / 21700 = 0%`; trapped fraction `6 / 21700 = 0.028%`; incomplete fraction `21694 / 21700 = 99.97%`.
- `40 um` coarse diagnostic point: escaped fraction `0 / 21700 = 0%`; trapped fraction `0 / 21700 = 0%`; incomplete fraction `21700 / 21700 = 100%`.
- The stochastic run changes the result strongly compared with deterministic tracking, but the outcome is still dominated by incomplete tracks.
- The larger `10 um` escape fraction is plausible as a numerical / stochastic-transport result because turbulent dispersion, residence time, and inertia can interact non-monotonically in a swirling separator. It should not be interpreted as a physical grade-efficiency trend unless repeated runs and the unresolved-fate bracket support the same ordering.

Preliminary `DRW10` random-eddy-lifetime-on interpretation:

- `5 um` / nearest recovered `5.63 um`: escaped fraction `2312 / 21700 = 10.65%`; trapped fraction `19 / 21700 = 0.088%`; incomplete fraction `19369 / 21700 = 89.26%`.
- `10 um` project diagnostic point: escaped fraction `2943 / 21700 = 13.56%`; trapped fraction `85 / 21700 = 0.39%`; incomplete fraction `18672 / 21700 = 86.05%`.
- `28.14 um` recovered bin: escaped fraction `0 / 21700 = 0%`; trapped fraction `9 / 21700 = 0.041%`; incomplete fraction `21691 / 21700 = 99.96%`.
- `40 um` coarse diagnostic point: escaped fraction `0 / 21700 = 0%`; trapped fraction `0 / 21700 = 0%`; incomplete fraction `21700 / 21700 = 100%`.
- Turning random eddy lifetime on reduced escaped counts for both tested diameters compared with random eddy lifetime off.
- The `10 um` case still escapes more than the `5 um` / `5.63 um` case in the completed fate counts, so carry this as a stochastic sensitivity result rather than dismissing it.
- Incomplete particles are not the target to eliminate in this branch; they represent an unresolved long-residence / likely wall-associated category that should be carried as a bracket around the escaped/trapped result.

## 7.3 Findings So Far

Setup `09b` shows that one-way DPM carryover is sensitive to turbulent dispersion settings.

Main findings:

- DRW stochastic tracking increases completed steam-outlet escape strongly compared with deterministic tracking for the fine/project-diagnostic bins.
- With random eddy lifetime off, completed escape is:
  - `5 um` / nearest recovered `5.63 um`: `12.54%`;
  - `10 um`: `15.53%`;
  - `28.14 um`: `0%`;
  - `40 um`: `0%`.
- With random eddy lifetime on, completed escape is:
  - `5 um` / nearest recovered `5.63 um`: `10.65%`;
  - `10 um`: `13.56%`;
  - `28.14 um`: `0%`;
  - `40 um`: `0%`.
- Turning random eddy lifetime on reduces completed escape for both `5 um` / `5.63 um` and `10 um`.
- The `10 um` diagnostic point escapes more than the `5 um` / `5.63 um` point in both stochastic settings.
- The `28.14 um` recovered bin and `40 um` coarse diagnostic point show no completed steam-outlet escape under either stochastic setting.

Interpretation:

- stochastic dispersion matters and should be carried as a project uncertainty;
- the `10 um > 5 um` completed-escape ordering should be treated as a stochastic sensitivity result, not as a final physical grade-efficiency curve;
- the absence of completed `28.14 um` and `40 um` escape suggests that, under the current sampled settings, completed stochastic carryover is concentrated in the fine `5-10 um` range;
- incomplete particles remain an unresolved long-residence / likely wall-associated fate category, not a numerical target to eliminate.

Recommended next checks:

1. Repeat the `5 um` / `5.63 um` and `10 um` DRW10 cases once more with the same settings to see whether the escaped fractions are repeatable or just random-seed noise.
2. If you need one more size to strengthen the transition claim, run `56.27 um` with DRW10 random eddy lifetime off and on.
3. If `56.27 um` also shows no completed escape, stop the size sweep and report that completed stochastic carryover is concentrated in the fine `5-10 um` range under this sampled setup.
4. For reporting, present escaped fraction separately from unresolved fraction. Do not collapse incomplete particles into escaped or trapped without an explicit Purnanto-style assumption.

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
