# DPM + Eulerian Wall Film Wall-Film Re-Entrainment Setup Report

## 1. Purpose

Define setup `09c` as the wall-film-aware child branch of setup `07`.

This branch is for the case where setup `07` or `09a`/`09b` suggests:

```text
bulk separation may already look acceptable,
but remaining error or uncertainty may come from wall deposition,
film persistence, and re-entrainment into the steam core.
```

The target model family is:

```text
DPM + Eulerian Wall Film
```

## 2. Why This Is Better Than VOF For The Next Run

This branch is better than the retired VOF `09` idea if the missing mechanism is wall-film behavior, because:

1. `VOF` mainly helps when one large continuous interface is the central unresolved feature;
2. the annular-flow papers in this repo escalate instead to explicit droplet-plus-film separation, not to `VOF`;
3. this branch can distinguish:
   - droplets in the gas core,
   - liquid attached to walls as film,
   - exchange between them.

Main paper support:

- [mondal-sharma-2024-air-water-annular-flow-cfd](../CFD_wiki/wiki/sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
- [skoog-2020-annular-flow-three-field-cfd-thesis](../CFD_wiki/wiki/sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- [droplets-carryover-and-re-entrainment](../CFD_wiki/wiki/physics-basis/droplets-carryover-and-re-entrainment.md)
- [annular-flow-three-field-cfd-patterns](../CFD_wiki/wiki/synthesis/annular-flow-three-field-cfd-patterns.md)

## 3. Parent Setup Authority

Use setup `07` as the geometry and inlet-package authority:

- same spiral-inlet separator body;
- same split pure liquid / pure steam inlet concept;
- same `27.118 m/s` actual-area mass-preserving split;
- same separator operating-condition base unless a dedicated sensitivity overrides it.

This branch changes the liquid-path representation, not the high-level case identity.

## 4. Model Stack

| Panel | Setting | Value |
|---|---|---|
| General | Solver | `Pressure-Based` |
| General | Time | `Transient` |
| Continuous-field multiphase | use the branch-specific carrier representation required by the Fluent EWF workflow and record it explicitly |
| Models > Viscous | Turbulence | start from the branch-specific choice most compatible with available compute and stability; if accuracy pressure remains high, this branch can later inherit `RSM` logic |
| Models > Discrete Phase | DPM | `On` |
| Models > Wall Film | Eulerian Wall Film | `On` on relevant collection walls |

Interpretation:

- this is the most complex child in the `09` family;
- only use it when wall-film fate is the real open question.

## 5. Boundary and Mechanism Intent

This branch must distinguish three liquid pathways:

1. liquid entering as the outer-wall-side inlet stream;
2. droplets moving in the steam-dominant core;
3. liquid that reaches walls and forms a film.

The point of the branch is to avoid the hidden assumption:

```text
every wall hit = permanent separation
```

## 6. DPM and Film Interaction Intent

At minimum, the branch should be able to say:

- how much liquid stays in the wall film,
- how much is deposited from droplets to film,
- how much re-enters the core or reaches the steam outlet.

Use DPM for:

- droplet tracking in the gas/steam-dominant region.

Use EWF for:

- wall film accumulation and transport on the relevant separator walls.

## 7. When 09c Is Worth Running

Run `09c` when one or more of these is true:

1. `09a` or `09b` says wall hits dominate the liquid fate;
2. treating wall hits as `trap` feels too optimistic;
3. bulk phase-flux efficiency looks good but fine carryover still seems physically unresolved;
4. the question has shifted from droplet size to re-entrainment risk.

## 8. Why 09c Is Harder Than 09a and 09b

This branch is harder because:

1. it introduces more closures than plain `DPM`;
2. annular-flow papers support the model family, but not direct geothermal separator calibration;
3. it usually needs transient interpretation and monitoring of film inventory over time.

So this is not the first child to run unless the wall-film mechanism is already the dominant unresolved issue.

## 9. Outputs To Record

Record at least:

1. droplet escaped/trapped/incomplete counts,
2. film mass inventory over time,
3. deposition and entrainment or film-source trends where available,
4. steam-outlet liquid contribution from all active liquid pathways,
5. whether film mass reaches a quasi-steady range before interpreting results.

## 10. Success Criterion

`09c` is worthwhile only if it changes the interpretation that simpler branches would give.

Examples:

1. a branch that looked efficient under wall-trap DPM no longer looks so clean once film return is allowed;
2. a large fraction of "separated" liquid is actually only temporarily wall-held;
3. steam-line contamination is shown to depend on film re-entrainment rather than only inlet droplet size.
