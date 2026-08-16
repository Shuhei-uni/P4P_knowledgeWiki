# Content routing and cross-system workflow

Route content before writing it.

1. Generic CFD methods, literature, or setup knowledge belong in `CFD_wiki/`.
2. Geothermal-separator project decisions and execution records belong in `ResearchProject_wiki/`.
3. A concrete simulation setup, case definition, result packet, naming decision, or lineage change belongs in `Setups/`.
4. Executable automation, PyFluent path discovery, machine-readable validation targets, and claim-gate scripts belong in `PyAnsys/` first; add any needed human-readable summary to the relevant wiki.
5. When reusable CFD knowledge also has project impact, write the technical extraction in `CFD_wiki/` and a linked project-impact summary in `ResearchProject_wiki/`.

## Setup routing

For new setup work, route by geometry before lifecycle or number:

- current `Full-geomV2` work → `Setups/full-geometry/<physics>/<campaign>/`;
- historical numbered/reference work → existing compatibility paths, navigated through `Setups/purnanto-reference/index.md`.

Do not create a new full-geometry setup under `Setups/active/` or a new full-geometry report under `Setups/reports/<id>/`.

Do not infer geometry from the setup number/title. Require explicit mesh/case provenance.

## Cross-system work

1. Read `CFD_wiki/wiki/index.md` and `ResearchProject_wiki/wiki/index.md` first.
2. When creating or reorganizing setups, read `Setups/index.md` and the relevant programme index.
3. Read `Setups/order-dictionary.md` only when numbered legacy lineage is involved.
4. For automation, also read `PyAnsys/AGENTS.md` and the relevant `PyAnsys/knowledge/` paths.
5. Update the primary owner and add short cross-references to secondary systems; do not duplicate full content.
6. When automation behavior or target manifests change, keep corresponding human-readable claim logic aligned with `ResearchProject_wiki/wiki/vnv/`.
