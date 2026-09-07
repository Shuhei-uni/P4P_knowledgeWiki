# DPM Split-Inlet Carryover Setup Report

## 1. Purpose

Define setup `09a` as the first literature-backed extension of setup `07`.

This branch keeps the stable continuous-field setup from [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md) and adds `DPM` to answer the next most direct question:

```text
which droplet sizes escape through the steam outlet under the current split-inlet flow field?
```

## 2. Why This Is Better Than VOF For The Next Run

This branch is better than the retired VOF `09` idea because:

1. the geothermal separator papers in this repo already use droplet tracking logic, not `VOF`, for separator-efficiency interpretation;
2. your unresolved quantity is carryover by droplet fate, not just sharp-interface shape;
3. `DPM` can answer the droplet-size question directly, while `VOF` cannot do that efficiently;
4. this is the smallest paper-backed change from a setup you already know can run.

Main paper support:

- [purnanto-2013-cfd-geothermal-separator](../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
- [pointon-2009-geothermal-separator-sizing-cfd-validation](../CFD_wiki/wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
- [fluent-separator-efficiency-methods](../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)

## 3. Parent Setup Authority

Use setup `07` as the continuous-field authority:

- keep the geometry;
- keep the actual-area pure liquid / pure steam split;
- keep the `27.118 m/s` equal-velocity inlet package;
- keep the same material properties and outlet roles;
- keep the same scope that judges steam-side carryover rather than full brine-drain closure.

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | `Pressure-Based` |
| General | Time | `Steady` |
| Models > Multiphase | Model | `Mixture` |
| Models > Viscous | Turbulence | `RNG k-epsilon` |
| Models > Energy | Energy | `Off` |
| Models > Discrete Phase | DPM | `On` after continuous-field convergence |

Interpretation:

- this is deliberately not an `RSM` branch;
- it is deliberately not a wall-film branch;
- it is the minimum carryover-focused child of setup `07`.

## 5. Inlet and Continuous-Field Boundary Conditions

Keep the setup `07` split-inlet package:

| Boundary | Type | Velocity | Liquid VF | Steam VF |
|---|---|---:|---:|---:|
| `inlet_liquid_outer` | `Velocity Inlet` | `27.118 m/s` | `1.0` | `0.0` |
| `inlet_steam_inner` | `Velocity Inlet` | `27.118 m/s` | `0.0` | `1.0` |

Use the same outlet, wall, gravity, operating-pressure convention, and continuous-phase numerics as setup `07` unless a run-specific stabilization note is recorded separately.

## 6. DPM Definition

### 6.1 Injection Philosophy

Use post-convergence droplet tracking to measure carryover sensitivity by size.

Recommended first sweep:

| Diameter | Reason |
|---:|---|
| `5 um` | fine-droplet lower marker already useful in the project |
| `10 um` | Purnanto reported baseline |
| `14.2 um` | Harwell-inferred median marker |
| `40-41 um` | larger upper-envelope marker |

If time is limited, start with:

```text
5 um, 10 um, 40-41 um
```

### 6.2 DPM Boundary Fate

| Boundary role | DPM fate |
|---|---|
| steam outlet | `escape` |
| intended liquid collection region / bottom collection logic | `trap` where that interpretation is physically intended |
| ordinary walls | do not silently set all walls to `trap`; use the branch-specific wall interpretation and document it |

Interpretation rule:

- if a wall hit is being counted as permanent separation, say that explicitly;
- do not hide wall-fate physics inside an unexamined default.

## 7. Outputs To Record

For each droplet size, record:

1. `injected`
2. `escaped`
3. `trapped`
4. `incomplete`
5. scoped carryover efficiency based on the branch interpretation

Use the reporting logic already documented in:

- [fluent-separator-efficiency-methods](../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)

## 8. Why 09a May Be Enough

`09a` may already answer the immediate project question if:

- bulk setup `07` flow looks physically plausible;
- the main unknown is just how droplet escape varies with size;
- wall-film re-entrainment is still only a suspicion, not a demonstrated blocker.

## 9. Failure Signal

`09a` is not enough if:

1. droplet fate depends too strongly on arbitrary wall-trap assumptions;
2. swirl-field credibility itself is still doubtful;
3. incomplete tracks remain too large to interpret cleanly;
4. the likely missing mechanism is no longer droplet size, but wall-film return to the core.

If that happens:

- move to `09b` if the flow-field accuracy is the main concern;
- move to `09c` if wall-film and re-entrainment are the main concern.
