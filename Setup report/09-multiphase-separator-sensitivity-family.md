# Multiphase Separator Sensitivity Family

## 1. Purpose

Replace the retired VOF-only `09` idea with a new setup-family parent that reflects the stronger research direction now established in `CFD_wiki`.

This `09` family is built from:

- [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)
- [08-purnanto-one-inlet-massflow-recreation.md](08-purnanto-one-inlet-massflow-recreation.md)
- the maintained paper extractions in `CFD_wiki`

This parent report is **not** a run definition by itself.

It exists to organize three concrete child branches:

- [09a-dpm-split-inlet-carryover.md](09a-dpm-split-inlet-carryover.md)
- [09b-rsm-dpm-split-inlet-accuracy.md](09b-rsm-dpm-split-inlet-accuracy.md)
- [09c-dpm-ewf-wall-film-reentrainment.md](09c-dpm-ewf-wall-film-reentrainment.md)

## 2. Why VOF Was Dropped

The current maintained paper set does not support `VOF` as the main production model for this separator problem.

Current evidence summary:

- [purnanto-2013-cfd-geothermal-separator](../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md): `Mixture` plus later droplet logic, not `VOF`.
- [pointon-2009-geothermal-separator-sizing-cfd-validation](../CFD_wiki/wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md): `RNG k-epsilon + DPM`, not `VOF`.
- [chen-2025-straight-through-cyclone-water-separator](../CFD_wiki/wiki/sources/chen-2025-straight-through-cyclone-water-separator.md): transient `RSM-DPM`, not `VOF`.
- [mondal-sharma-2024-air-water-annular-flow-cfd](../CFD_wiki/wiki/sources/mondal-sharma-2024-air-water-annular-flow-cfd.md): `DPM + Eulerian Wall Film`, not `VOF`.
- [skoog-2020-annular-flow-three-field-cfd-thesis](../CFD_wiki/wiki/sources/skoog-2020-annular-flow-three-field-cfd-thesis.md): three-field `EWF + DPM`, not `VOF`.

Interpretation:

- `VOF` remains a known model family, but not the best-supported next branch for this project.
- the stronger paper-backed question is not "can one clean interface be resolved?"
- the stronger paper-backed questions are:
  - which droplets escape,
  - whether stronger swirl changes droplet fate enough to justify a higher turbulence closure,
  - whether wall-hit liquid stays removed or re-enters the steam path.

## 3. Shared Inherited Inputs

All `09` child branches inherit the same core setup identity unless the child report explicitly overrides it:

| Item | Value |
|---|---:|
| Geometry family | spiral-inlet BOC separator |
| Split-inlet basis | setup `07` actual-area pure liquid / pure steam split |
| One-inlet baseline context | setup `08` |
| Liquid target mass flow | `116.92 kg/s` |
| Steam target mass flow | `80.69 kg/s` |
| Total target mass flow | `197.61 kg/s` |
| Liquid density | `881.77 kg/m3` |
| Steam density | `5.73 kg/m3` |
| Liquid viscosity | `145.96e-6 kg/m-s` |
| Steam viscosity | `15.188e-6 kg/m-s` |
| Shared split-inlet velocity | `27.118 m/s` |
| Liquid strip width | `0.006754 m` |
| Steam strip width | `0.717246 m` |

Scope note:

- bottom liquid drainage remains out of scope unless a child branch explicitly changes that;
- these branches are still judged mainly by steam-side liquid carryover, internal flow plausibility, and mechanism clarity.

## 4. Child Branch Logic

### `09a` DPM

Use [09a-dpm-split-inlet-carryover.md](09a-dpm-split-inlet-carryover.md) when the main question is:

```text
which droplet sizes escape under the currently resolved separator flow field?
```

Best match:

- quickest literature-backed extension from setup `07`;
- strongest continuity with Purnanto and Pointon;
- lowest extra setup complexity.

### `09b` RSM-DPM

Use [09b-rsm-dpm-split-inlet-accuracy.md](09b-rsm-dpm-split-inlet-accuracy.md) when the main question is:

```text
is the present eddy-viscosity turbulence closure hiding important swirl anisotropy
and therefore biasing separator accuracy?
```

Best match:

- strongest recent separator-method validation anchor from Chen 2025;
- better aligned with strong swirl than `RNG k-epsilon`;
- higher cost than `09a`, but more defensible if flow-field accuracy is the concern.

### `09c` DPM + Eulerian Wall Film

Use [09c-dpm-ewf-wall-film-reentrainment.md](09c-dpm-ewf-wall-film-reentrainment.md) when the main question is:

```text
does wall-hit liquid stay separated, or does wall film and re-entrainment
control the remaining carryover error?
```

Best match:

- best mechanism match if setup `07` already looks good in bulk carryover but still may hide wall-film physics;
- strongest link to the annular-flow literature in the repo;
- highest implementation risk and highest closure dependence.

## 5. Recommendation Order

Recommended order of execution:

1. `09a` first if you want the fastest paper-backed next run.
2. `09b` first instead if you care more about separator accuracy than speed and have enough compute.
3. `09c` only after `09a` or `09b` shows that wall re-entrainment is still the likely missing mechanism.

## 6. Interpretation Rule

Treat this `09` parent as:

```text
multiphase sensitivity family container only
```

Do not run `09` directly.
Run only `09a`, `09b`, or `09c`.
