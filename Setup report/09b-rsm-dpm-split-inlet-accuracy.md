# RSM-DPM Split-Inlet Accuracy Setup Report

## 1. Purpose

Define setup `09b` as the stronger-accuracy child branch of setup `07`.

This branch keeps the split-inlet phase package but upgrades the continuous-field and carryover workflow to:

```text
RSM + DPM
```

The target question is:

```text
does stronger swirl-resolving turbulence closure materially improve separator accuracy
and therefore droplet carryover prediction?
```

## 2. Why This Is Better Than VOF For The Next Run

This branch is better than the retired VOF `09` idea because:

1. the recent experiment-backed separator paper in this repo uses transient `RSM-DPM`, not `VOF`;
2. your separator is strongly swirling, so turbulence anisotropy is a more defensible concern than sharp-interface transport alone;
3. `DPM` still answers droplet fate directly;
4. this branch can improve both the resolved flow field and the carryover interpretation at the same time.

Main paper support:

- [chen-2025-straight-through-cyclone-water-separator](../CFD_wiki/wiki/sources/chen-2025-straight-through-cyclone-water-separator.md)
- [pointon-2009-geothermal-separator-sizing-cfd-validation](../CFD_wiki/wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
- [separator-flow-physics](../CFD_wiki/wiki/physics-basis/separator-flow-physics.md)

## 3. Parent Setup Authority

Use setup `07` for:

- geometry;
- inlet split;
- phase mass-flow target;
- outlet role;
- project scope and reporting interpretation.

Only the following core changes are intentional:

1. turbulence closure: `RNG k-epsilon` -> `RSM`
2. time mode: steady baseline may be retained first or upgraded to transient if the chosen Fluent workflow requires it for stability and comparison discipline
3. add `DPM` after continuous-field stabilization

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | `Pressure-Based` |
| General | Time | start with the branch-specific continuous-field mode chosen for the available Fluent workflow; if you use transient, record the timestep explicitly |
| Models > Multiphase | Model | `Mixture` |
| Models > Viscous | Turbulence | `RSM` |
| Models > Energy | Energy | `Off` |
| Models > Discrete Phase | DPM | `On` after continuous-field stabilization |

Practical note:

- this branch is about improving the swirling carrier field first, not about jumping directly to wall-film modeling.

## 5. Inlet and Boundary Conditions

Keep the same split-inlet mass package as setup `07`:

| Boundary | Type | Velocity | Liquid VF | Steam VF |
|---|---|---:|---:|---:|
| `inlet_liquid_outer` | `Velocity Inlet` | `27.118 m/s` | `1.0` | `0.0` |
| `inlet_steam_inner` | `Velocity Inlet` | `27.118 m/s` | `0.0` | `1.0` |

Keep:

- the same pressure-outlet role;
- the same gravity direction;
- the same material values;
- the same physical scope unless a separate child diagnostic is created.

## 6. DPM Definition

Use the same first droplet-size sweep logic as `09a` unless a narrower validation comparison is preferred:

| Diameter | Reason |
|---:|---|
| `5 um` | fine-droplet sensitivity |
| `10 um` | Purnanto baseline |
| `14.2 um` | Harwell-inferred median marker |
| `40-41 um` | larger-droplet marker |

DPM boundary interpretation:

| Boundary role | DPM fate |
|---|---|
| steam outlet | `escape` |
| liquid collection region | `trap` where physically intended |
| walls | explicitly document chosen wall behavior |

## 7. Why 09b May Be Better Than 09a

Choose `09b` over `09a` if you suspect the current issue is not just droplet size, but the resolved swirl field itself.

Signals that favor `09b`:

1. separator core pressure or vortex structure still looks suspicious under `RNG k-epsilon`;
2. small droplet escape seems too sensitive to the underlying resolved flow field;
3. you want the strongest recent separator-method anchor available in the repo.

## 8. Main Risk

`09b` costs more and converges harder than `09a`.

It is not the right first run if:

- you only need a quick carryover ranking;
- the current flow field already looks acceptable;
- the real missing mechanism is likely wall-film re-entrainment rather than turbulence anisotropy.

In that case, use `09a` or go directly to `09c`.

## 9. Success Criterion

`09b` is worthwhile only if it improves at least one of these materially over `09a`/`07`:

1. internal swirl/core-pressure plausibility,
2. stability of steam-outlet liquid carryover interpretation,
3. droplet-fate credibility across the tested size range.
