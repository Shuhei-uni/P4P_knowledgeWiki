# Content routing and cross-system workflow

Route content before writing it.

1. Generic CFD methods, literature, or setup knowledge belong in `CFD_wiki/`.
2. Current geothermal-separator scientific truth, selected experiments, evidence interpretation, and claim limits belong in `Project/`.
3. Detailed retained progress, technical, source, and existing V&V records remain in `ResearchProject_wiki/` until a deliberate cutover.
4. A concrete simulation setup, case definition, result packet, naming decision, or lineage change belongs in `Setups/`.
5. Executable automation, PyFluent path discovery, machine-readable validation targets, and claim-gate scripts belong in `PyAnsys/` first; add any needed human-readable summary to the relevant project record.
6. When reusable CFD knowledge also has project impact, write the technical extraction in `CFD_wiki/` and a concise linked impact summary in `Project/`.

## Setup routing

For new setup work, route by geometry before lifecycle or number:

- current `Full-geomV2` work → `Setups/full-geometry/<physics>/<campaign>/`;
- historical numbered/reference work → existing compatibility paths, navigated through `Setups/purnanto-reference/index.md`.

Do not create a new full-geometry setup under `Setups/active/` or a new full-geometry report under `Setups/reports/<id>/`.

Do not infer geometry from the setup number/title. Require explicit mesh/case provenance.

## Cross-system work

1. Read `Project/index.md` first, then `CFD_wiki/wiki/index.md` and `ResearchProject_wiki/wiki/index.md` when their owned context is needed.
2. When creating or reorganizing setups, read `Setups/index.md` and the relevant programme index.
3. Read `Setups/order-dictionary.md` only when numbered legacy lineage is involved.
4. For automation, also read `PyAnsys/AGENTS.md` and the relevant `PyAnsys/knowledge/` paths.
5. Update the primary owner and add short cross-references to secondary systems; do not duplicate full content.
6. When automation behavior or target manifests change, keep corresponding human-readable claim logic aligned with `Project/vnv.md` and the detailed records in `ResearchProject_wiki/wiki/vnv/`.
