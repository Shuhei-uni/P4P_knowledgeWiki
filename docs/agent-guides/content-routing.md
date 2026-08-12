# Content routing and cross-system workflow

Route content before writing it.

1. Generic CFD methods, literature, or setup knowledge belong in `CFD_wiki/`.
2. Geothermal-separator project decisions and execution records belong in `ResearchProject_wiki/`.
3. A concrete simulation setup, active case definition, report branch, naming decision, or lineage change belongs in `Setups/`.
4. Executable automation, PyFluent path discovery, machine-readable validation targets, and claim-gate scripts belong in `PyAnsys/` first; add any needed human-readable summary to the relevant wiki.
5. When reusable CFD knowledge also has project impact, write the technical extraction in `CFD_wiki/` and a linked project-impact summary in `ResearchProject_wiki/`.
6. When work creates or changes a concrete setup branch, retain technical and project context in the relevant wiki and record the setup instance in `Setups/`.

## Cross-system work

For work spanning systems:

1. Read `CFD_wiki/wiki/index.md` and `ResearchProject_wiki/wiki/index.md` first. Read `Setups/order-dictionary.md` when lineage or naming is involved. For automation, also read `PyAnsys/AGENTS.md` and the relevant `PyAnsys/knowledge/` paths.
2. Update the primary owner selected above.
3. Add short cross-references to secondary systems when useful; do not duplicate the full content.
4. Update index or log files required by each local guide.
5. Update `Setups/order-dictionary.md` when setup ordering, branch identity, or naming changes.
6. When automation behavior or target manifests change, keep the corresponding human-readable claim logic aligned with `ResearchProject_wiki/wiki/vnv/`.
