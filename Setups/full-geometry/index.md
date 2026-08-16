# Full-Geometry Setup Programme

This is the canonical **setup-definition tree** for the current production separator geometry (`Full-geomV2` and verified descendants).

Numerical result reports do **not** live in this tree. The mirrored report tree is [Setups/reports/full-geometry](../reports/full-geometry/index.md).

## Current programme map

```text
Full-geometry setups
├── Mixture
│   ├── steady liquid-outlet characterization
│   └── transient liquid-outlet characterization   ← next major campaign
└── VOF
    └── transient liquid-outlet model-form branch
```

- [Mixture setup campaigns](mixture/index.md)
- [VOF setup campaigns](vof/index.md)
- [Full-geometry result reports](../reports/full-geometry/index.md)

## Authoring rule

New setup work is organized as:

```text
geometry → physics family → scientific campaign → setup/stage plans
```

The matching numerical evidence is organized separately as:

```text
reports → geometry → physics family → scientific campaign → result reports
```

A campaign may use a stable machine/reference ID such as `FG-MIX-T01`, but the descriptive campaign path is the primary human-facing identity.

## What belongs here

Keep here:

- `index.md` campaign navigation;
- `setup.md` experiment/build contract;
- stage plans;
- initialization plans;
- numerical-qualification plans;
- planned case matrices and monitor requirements.

Do not keep here:

- result reports;
- execution-result summaries;
- post-analysis evidence packets;
- interpretation reports based on completed simulations.

Those belong in the mirrored [full-geometry reports tree](../reports/full-geometry/index.md).

## Relationship to the numbered corpus

The current steady Mixture work was originally recorded as numbered Setup `02c` and `02e`. Those source setup files and their old numbered report folders remain at their historical paths for link stability, but their scientific ownership is now the full-geometry programme.

The older numbered corpus remains accessible through [Purnanto/reference programme](../purnanto-reference/index.md). A legacy setup can be a methodological predecessor without being a geometry parent. Do not claim case/mesh inheritance unless the artifact lineage is explicitly verified.

## Geometry identity gate

Before adding a campaign here, record the exact geometry/mesh evidence. A name containing “full geometry” is not sufficient. At minimum capture one of:

- exact mesh filename and readback;
- exact parent `.cas.h5` with verified mesh identity;
- explicit geometry revision/provenance record.
